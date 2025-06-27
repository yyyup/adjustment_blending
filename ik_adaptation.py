# adjustment_blending/ik_adaptation.py
"""
Real-time IK adaptation system for professional adjustment blending
Automatically adapts foot IK constraints when root motion changes
"""

import bpy
import bmesh
from mathutils import Vector, Matrix, Quaternion
from bpy_extras import object_utils
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import time

# Global state management
_adaptive_constraints = {}
_root_motion_data = {}
_contact_states = {}
_constraint_drivers = {}

class AdaptiveConstraintManager:
    """Manages real-time IK constraint adaptation"""
    
    def __init__(self, armature_obj):
        self.armature = armature_obj
        self.constraint_data = {}
        self.contact_detection = ContactDetectionSystem(armature_obj)
        self.space_switcher = ConstraintSpaceSwitcher(armature_obj)
        
    def setup_adaptive_constraints(self, foot_bones=None):
        """Set up adaptive IK constraints for foot bones"""
        if not foot_bones:
            from .core import AnimationDataUtils
            foot_bones = AnimationDataUtils.find_foot_bones(self.armature)
        
        print(f"Setting up adaptive constraints for: {foot_bones}")
        
        for bone_name in foot_bones:
            if 'ik' in bone_name.lower() and 'foot' in bone_name.lower():
                success = self._setup_bone_constraints(bone_name)
                if success:
                    print(f"✓ Adaptive constraints set up for {bone_name}")
                else:
                    print(f"✗ Failed to set up constraints for {bone_name}")
        
        # Register the constraint manager globally
        _adaptive_constraints[self.armature.name] = self
        
        return len(self.constraint_data) > 0
    
    def _setup_bone_constraints(self, bone_name):
        """Set up adaptive constraints for a specific bone"""
        try:
            if bone_name not in self.armature.pose.bones:
                return False
            
            pose_bone = self.armature.pose.bones[bone_name]
            
            # Create world space constraint
            world_constraint = self._create_world_space_constraint(pose_bone)
            
            # Create local space constraint  
            local_constraint = self._create_local_space_constraint(pose_bone)
            
            # Set up constraint driver for automatic switching
            driver_constraint = self._create_constraint_driver(pose_bone, world_constraint, local_constraint)
            
            # Store constraint data
            self.constraint_data[bone_name] = {
                'pose_bone': pose_bone,
                'world_constraint': world_constraint,
                'local_constraint': local_constraint,
                'driver_constraint': driver_constraint,
                'contact_state': False,
                'world_position': pose_bone.matrix.to_translation().copy(),
                'initial_position': pose_bone.matrix.to_translation().copy()
            }
            
            return True
            
        except Exception as e:
            print(f"Error setting up constraints for {bone_name}: {e}")
            return False
    
    def _create_world_space_constraint(self, pose_bone):
        """Create world space positioning constraint"""
        try:
            # Create an empty object as world space target
            target_name = f"{pose_bone.name}_world_target"
            
            # Remove existing target if it exists
            if target_name in bpy.data.objects:
                bpy.data.objects.remove(bpy.data.objects[target_name])
            
            # Create new empty
            target_empty = bpy.data.objects.new(target_name, None)
            target_empty.empty_display_type = 'PLAIN_AXES'
            target_empty.empty_display_size = 0.1
            
            # Add to scene
            bpy.context.collection.objects.link(target_empty)
            
            # Position at current bone location
            target_empty.matrix_world = self.armature.matrix_world @ pose_bone.matrix
            
            # Create copy location constraint
            constraint = pose_bone.constraints.new(type='COPY_LOCATION')
            constraint.name = "Adaptive_World_Position"
            constraint.target = target_empty
            constraint.influence = 0.0  # Start disabled
            
            return {
                'constraint': constraint,
                'target': target_empty
            }
            
        except Exception as e:
            print(f"Error creating world space constraint: {e}")
            return None
    
    def _create_local_space_constraint(self, pose_bone):
        """Create local space constraint for normal IK behavior"""
        try:
            # This maintains the original IK behavior
            # In a full implementation, this would preserve existing IK chains
            
            # For now, we'll use a simple approach
            constraint = pose_bone.constraints.new(type='COPY_LOCATION')
            constraint.name = "Adaptive_Local_Position"
            constraint.target = self.armature
            constraint.subtarget = pose_bone.name  # Self-reference for local space
            constraint.influence = 1.0  # Start enabled
            
            return {
                'constraint': constraint,
                'target': self.armature
            }
            
        except Exception as e:
            print(f"Error creating local space constraint: {e}")
            return None
    
    def _create_constraint_driver(self, pose_bone, world_constraint, local_constraint):
        """Create driver that automatically switches between world/local space"""
        try:
            if not world_constraint or not local_constraint:
                return None
            
            # Create custom property for contact state
            contact_prop_name = f"{pose_bone.name}_contact_state"
            
            if contact_prop_name not in self.armature:
                self.armature[contact_prop_name] = 0.0
            
            # Add driver to world constraint influence
            world_constraint['constraint'].driver_remove('influence')
            driver = world_constraint['constraint'].driver_add('influence').driver
            
            # Set up driver
            driver.type = 'SCRIPTED'
            driver.expression = f"contact * blend_factor"
            
            # Add variables
            contact_var = driver.variables.new()
            contact_var.name = "contact"
            contact_var.type = 'SINGLE_PROP'
            contact_target = contact_var.targets[0]
            contact_target.id = self.armature
            contact_target.data_path = f'["{contact_prop_name}"]'
            
            blend_var = driver.variables.new()
            blend_var.name = "blend_factor"
            blend_var.type = 'SINGLE_PROP'
            blend_target = blend_var.targets[0]
            blend_target.id = self.armature
            blend_target.data_path = '["adaptive_blend_factor"]' if "adaptive_blend_factor" in self.armature else "1.0"
            
            # Add driver to local constraint influence (inverse)
            local_constraint['constraint'].driver_remove('influence')
            local_driver = local_constraint['constraint'].driver_add('influence').driver
            local_driver.type = 'SCRIPTED'
            local_driver.expression = f"1.0 - (contact * blend_factor)"
            
            # Copy variables
            local_contact_var = local_driver.variables.new()
            local_contact_var.name = "contact"
            local_contact_var.type = 'SINGLE_PROP'
            local_contact_target = local_contact_var.targets[0]
            local_contact_target.id = self.armature
            local_contact_target.data_path = f'["{contact_prop_name}"]'
            
            local_blend_var = local_driver.variables.new()
            local_blend_var.name = "blend_factor"
            local_blend_var.type = 'SINGLE_PROP'
            local_blend_target = local_blend_var.targets[0]
            local_blend_target.id = self.armature
            local_blend_target.data_path = '["adaptive_blend_factor"]' if "adaptive_blend_factor" in self.armature else "1.0"
            
            return {
                'contact_property': contact_prop_name,
                'world_driver': driver,
                'local_driver': local_driver
            }
            
        except Exception as e:
            print(f"Error creating constraint driver: {e}")
            return None
    
    def update_constraints(self, frame_current):
        """Update constraint states based on current frame"""
        try:
            for bone_name, constraint_data in self.constraint_data.items():
                # Detect contact state
                is_contact = self.contact_detection.is_foot_in_contact(bone_name, frame_current)
                
                # Update contact state property
                contact_prop = constraint_data.get('driver_constraint', {}).get('contact_property')
                if contact_prop and contact_prop in self.armature:
                    # Smooth transition
                    current_value = self.armature[contact_prop]
                    target_value = 1.0 if is_contact else 0.0
                    blend_speed = 0.3  # Adjust for responsiveness
                    
                    new_value = current_value + (target_value - current_value) * blend_speed
                    self.armature[contact_prop] = new_value
                    
                    # Update world target position if in contact
                    if is_contact and 'world_constraint' in constraint_data:
                        self._update_world_target_position(bone_name, constraint_data)
                
                # Store contact state
                constraint_data['contact_state'] = is_contact
            
        except Exception as e:
            print(f"Error updating constraints: {e}")
    
    def _update_world_target_position(self, bone_name, constraint_data):
        """Update world target position to maintain foot contact"""
        try:
            world_data = constraint_data['world_constraint']
            if not world_data or 'target' not in world_data:
                return
            
            target_empty = world_data['target']
            pose_bone = constraint_data['pose_bone']
            
            # Get current foot position in world space
            current_world_pos = self.armature.matrix_world @ pose_bone.matrix.to_translation()
            
            # Update target position (in a full implementation, this would use ground detection)
            # For now, we'll maintain the current Y position
            target_empty.location = current_world_pos
            
        except Exception as e:
            print(f"Error updating world target position: {e}")
    
    def cleanup_constraints(self):
        """Clean up adaptive constraints"""
        try:
            for bone_name, constraint_data in self.constraint_data.items():
                pose_bone = constraint_data['pose_bone']
                
                # Remove constraints
                constraints_to_remove = []
                for constraint in pose_bone.constraints:
                    if constraint.name.startswith('Adaptive_'):
                        constraints_to_remove.append(constraint)
                
                for constraint in constraints_to_remove:
                    pose_bone.constraints.remove(constraint)
                
                # Remove target empties
                if 'world_constraint' in constraint_data:
                    target = constraint_data['world_constraint'].get('target')
                    if target and target.name in bpy.data.objects:
                        bpy.data.objects.remove(target)
            
            # Clear data
            self.constraint_data.clear()
            
            # Remove from global registry
            if self.armature.name in _adaptive_constraints:
                del _adaptive_constraints[self.armature.name]
            
            print("Adaptive constraints cleaned up")
            
        except Exception as e:
            print(f"Error cleaning up constraints: {e}")

class ContactDetectionSystem:
    """Advanced contact detection for real-time IK adaptation"""
    
    def __init__(self, armature_obj):
        self.armature = armature_obj
        self.contact_cache = {}
        self.ground_level = 0.0
        self.contact_threshold = 0.05
        
    def is_foot_in_contact(self, bone_name, frame):
        """Determine if foot is in contact with ground at current frame"""
        try:
            # Check cache first
            cache_key = f"{bone_name}_{frame}"
            if cache_key in self.contact_cache:
                return self.contact_cache[cache_key]
            
            if bone_name not in self.armature.pose.bones:
                return False
            
            pose_bone = self.armature.pose.bones[bone_name]
            
            # Get bone position in world space
            world_matrix = self.armature.matrix_world @ pose_bone.matrix
            world_position = world_matrix.to_translation()
            
            # Simple ground contact detection (Z-axis)
            is_contact = world_position.z <= (self.ground_level + self.contact_threshold)
            
            # Enhanced detection: check velocity
            if is_contact:
                velocity = self._calculate_bone_velocity(bone_name, frame)
                # Lower velocity threshold for contact
                is_contact = velocity < 0.1
            
            # Cache result
            self.contact_cache[cache_key] = is_contact
            
            return is_contact
            
        except Exception as e:
            print(f"Error in contact detection: {e}")
            return False
    
    def _calculate_bone_velocity(self, bone_name, frame):
        """Calculate bone velocity for enhanced contact detection"""
        try:
            if bone_name not in self.armature.pose.bones:
                return 0.0
            
            pose_bone = self.armature.pose.bones[bone_name]
            
            # Get positions at different frames
            current_pos = (self.armature.matrix_world @ pose_bone.matrix).to_translation()
            
            # For real-time, we can't easily get other frame positions
            # This would need to be enhanced with actual F-curve evaluation
            return 0.05  # Placeholder - assume moderate movement
            
        except Exception:
            return 0.0
    
    def update_ground_level(self, new_ground_level):
        """Update ground level for contact detection"""
        self.ground_level = new_ground_level
        self.contact_cache.clear()  # Clear cache when ground level changes

class ConstraintSpaceSwitcher:
    """Manages constraint space switching for adaptive IK"""
    
    def __init__(self, armature_obj):
        self.armature = armature_obj
        self.space_history = defaultdict(list)
        
    def switch_to_world_space(self, bone_name, blend_factor=1.0):
        """Switch bone constraint to world space"""
        try:
            constraint_manager = _adaptive_constraints.get(self.armature.name)
            if not constraint_manager or bone_name not in constraint_manager.constraint_data:
                return False
            
            constraint_data = constraint_manager.constraint_data[bone_name]
            
            # Update world constraint influence
            if 'world_constraint' in constraint_data:
                world_constraint = constraint_data['world_constraint']['constraint']
                world_constraint.influence = blend_factor
            
            # Update local constraint influence
            if 'local_constraint' in constraint_data:
                local_constraint = constraint_data['local_constraint']['constraint']
                local_constraint.influence = 1.0 - blend_factor
            
            return True
            
        except Exception as e:
            print(f"Error switching to world space: {e}")
            return False
    
    def switch_to_local_space(self, bone_name, blend_factor=1.0):
        """Switch bone constraint to local space"""
        try:
            constraint_manager = _adaptive_constraints.get(self.armature.name)
            if not constraint_manager or bone_name not in constraint_manager.constraint_data:
                return False
            
            constraint_data = constraint_manager.constraint_data[bone_name]
            
            # Update local constraint influence
            if 'local_constraint' in constraint_data:
                local_constraint = constraint_data['local_constraint']['constraint']
                local_constraint.influence = blend_factor
            
            # Update world constraint influence
            if 'world_constraint' in constraint_data:
                world_constraint = constraint_data['world_constraint']['constraint']
                world_constraint.influence = 1.0 - blend_factor
            
            return True
            
        except Exception as e:
            print(f"Error switching to local space: {e}")
            return False

class RootMotionDetector:
    """Detects and responds to root motion changes"""
    
    def __init__(self, armature_obj):
        self.armature = armature_obj
        self.previous_root_position = None
        self.root_bone_name = self._find_root_bone()
        self.motion_threshold = 0.01
        
    def _find_root_bone(self):
        """Find the root bone of the armature"""
        # Common root bone names in rigify
        root_candidates = ['root', 'Root', 'master', 'Master', 'COG', 'pelvis']
        
        for bone_name in root_candidates:
            if bone_name in self.armature.pose.bones:
                return bone_name
        
        # Fallback: use first bone
        if self.armature.pose.bones:
            return self.armature.pose.bones[0].name
        
        return None
    
    def detect_motion(self):
        """Detect if root has moved significantly"""
        if not self.root_bone_name or self.root_bone_name not in self.armature.pose.bones:
            return False, Vector((0, 0, 0))
        
        root_bone = self.armature.pose.bones[self.root_bone_name]
        current_position = (self.armature.matrix_world @ root_bone.matrix).to_translation()
        
        if self.previous_root_position is None:
            self.previous_root_position = current_position.copy()
            return False, Vector((0, 0, 0))
        
        # Calculate motion delta
        motion_delta = current_position - self.previous_root_position
        motion_magnitude = motion_delta.length
        
        has_moved = motion_magnitude > self.motion_threshold
        
        if has_moved:
            self.previous_root_position = current_position.copy()
        
        return has_moved, motion_delta
    
    def reset_motion_tracking(self):
        """Reset motion tracking"""
        self.previous_root_position = None

# Real-time update handlers
def adaptive_ik_frame_handler(scene, depsgraph):
    """Frame change handler for adaptive IK updates"""
    try:
        # Update all active constraint managers
        for armature_name, constraint_manager in _adaptive_constraints.items():
            if armature_name in bpy.data.objects:
                constraint_manager.update_constraints(scene.frame_current)
    
    except Exception as e:
        print(f"Error in adaptive IK frame handler: {e}")

def adaptive_ik_depsgraph_handler(scene, depsgraph):
    """Depsgraph update handler for real-time root motion detection"""
    try:
        # Check for object updates that might indicate root motion
        for update in depsgraph.updates:
            if update.is_updated_transform and hasattr(update.id, 'pose'):
                armature_obj = update.id
                
                # Check if this armature has adaptive constraints
                if armature_obj.name in _adaptive_constraints:
                    constraint_manager = _adaptive_constraints[armature_obj.name]
                    
                    # Update constraints based on current state
                    constraint_manager.update_constraints(scene.frame_current)
    
    except Exception as e:
        print(f"Error in adaptive IK depsgraph handler: {e}")

# Utility functions
def register_adaptive_handlers():
    """Register handlers for real-time updates"""
    if adaptive_ik_frame_handler not in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.append(adaptive_ik_frame_handler)
    
    if adaptive_ik_depsgraph_handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(adaptive_ik_depsgraph_handler)

def unregister_adaptive_handlers():
    """Unregister handlers"""
    if adaptive_ik_frame_handler in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.remove(adaptive_ik_frame_handler)
    
    if adaptive_ik_depsgraph_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(adaptive_ik_depsgraph_handler)

def cleanup_all_adaptive_constraints():
    """Clean up all adaptive constraints"""
    for constraint_manager in list(_adaptive_constraints.values()):
        constraint_manager.cleanup_constraints()
    
    _adaptive_constraints.clear()
    _root_motion_data.clear()
    _contact_states.clear()
    _constraint_drivers.clear()