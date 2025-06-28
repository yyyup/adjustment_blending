# adjustment_blending/core.py
"""
Professional core algorithms for adjustment blending system
Implements industry-standard velocity-aware energy preservation techniques
"""

import bpy
import bmesh
from mathutils import Vector, Quaternion, Euler
import numpy as np
from typing import List, Dict, Tuple, Optional
import time
import threading
from collections import defaultdict

# Global cache for performance optimization
_analysis_cache = {}
_cache_lock = threading.Lock()

def frame_change_handler(scene):
    """Handler for real-time preview updates"""
    try:
        if hasattr(scene, 'adjustment_blending'):
            props = scene.adjustment_blending
            if props.preview_mode and props.auto_update:
                # Trigger real-time update
                AdjustmentBlendingEngine.update_preview(scene.frame_current)
    except Exception as e:
        if props.show_debug_info:
            print(f"Frame change handler error: {e}")

class MotionAnalyzer:
    """Advanced motion analysis for professional adjustment blending"""
    
    @staticmethod
    def calculate_velocity(fcurve, frame, window=2):
        """Calculate velocity at a frame using central difference with error handling"""
        try:
            if frame <= window:
                # Forward difference
                val_curr = fcurve.evaluate(frame)
                val_next = fcurve.evaluate(frame + window)
                return (val_next - val_curr) / window
            elif frame >= (fcurve.range()[1] - window):
                # Backward difference
                val_prev = fcurve.evaluate(frame - window)
                val_curr = fcurve.evaluate(frame)
                return (val_curr - val_prev) / window
            else:
                # Central difference
                val_prev = fcurve.evaluate(frame - window)
                val_next = fcurve.evaluate(frame + window)
                return (val_next - val_prev) / (2 * window)
        except Exception:
            return 0.0
    
    @staticmethod
    def calculate_acceleration(fcurve, frame, window=2):
        """Calculate acceleration for advanced energy analysis"""
        try:
            vel_prev = MotionAnalyzer.calculate_velocity(fcurve, frame - window, window)
            vel_next = MotionAnalyzer.calculate_velocity(fcurve, frame + window, window)
            return (vel_next - vel_prev) / (2 * window)
        except Exception:
            return 0.0
    
    @staticmethod
    def detect_movement_regions(fcurve, velocity_threshold=0.1, min_duration=3):
        """
        Detect regions where significant movement occurs with professional filtering
        Returns list of (start_frame, end_frame, energy_level, motion_type) tuples
        """
        if not fcurve.keyframe_points:
            return []
        
        # Check cache first
        cache_key = f"movement_{id(fcurve)}_{velocity_threshold}_{min_duration}"
        with _cache_lock:
            if cache_key in _analysis_cache:
                return _analysis_cache[cache_key]
        
        frame_start = int(fcurve.range()[0])
        frame_end = int(fcurve.range()[1])
        
        movement_regions = []
        current_region_start = None
        current_max_energy = 0
        current_avg_velocity = 0
        velocity_samples = []
        
        for frame in range(frame_start, frame_end + 1):
            velocity = abs(MotionAnalyzer.calculate_velocity(fcurve, frame))
            acceleration = abs(MotionAnalyzer.calculate_acceleration(fcurve, frame))
            
            # Combined energy metric
            energy = velocity + (acceleration * 0.5)
            
            if energy > velocity_threshold:
                if current_region_start is None:
                    current_region_start = frame
                    velocity_samples = []
                
                current_max_energy = max(current_max_energy, energy)
                velocity_samples.append(velocity)
                current_avg_velocity = sum(velocity_samples) / len(velocity_samples)
            else:
                if current_region_start is not None:
                    region_duration = frame - current_region_start
                    
                    # Only include regions that meet minimum duration
                    if region_duration >= min_duration:
                        # Classify motion type
                        motion_type = MotionAnalyzer._classify_motion_type(
                            current_avg_velocity, current_max_energy, region_duration
                        )
                        
                        movement_regions.append((
                            current_region_start,
                            frame - 1,
                            current_max_energy,
                            motion_type
                        ))
                    
                    current_region_start = None
                    current_max_energy = 0
                    current_avg_velocity = 0
                    velocity_samples = []
        
        # Handle case where movement continues to end
        if current_region_start is not None:
            region_duration = frame_end - current_region_start
            if region_duration >= min_duration:
                motion_type = MotionAnalyzer._classify_motion_type(
                    current_avg_velocity, current_max_energy, region_duration
                )
                movement_regions.append((
                    current_region_start,
                    frame_end,
                    current_max_energy,
                    motion_type
                ))
        
        # Cache result
        with _cache_lock:
            _analysis_cache[cache_key] = movement_regions
        
        return movement_regions
    
    @staticmethod
    def _classify_motion_type(avg_velocity, max_energy, duration):
        """Classify the type of motion for intelligent blending"""
        if max_energy > 2.0:
            return 'FAST'
        elif max_energy > 0.5:
            if duration > 20:
                return 'SUSTAINED'
            else:
                return 'QUICK'
        elif avg_velocity > 0.3:
            return 'SMOOTH'
        else:
            return 'SLOW'
    
    @staticmethod
    def detect_contact_phases(fcurves, ground_threshold=0.05, stability_threshold=0.02):
        """
        Professional contact phase detection for ground contact preservation
        """
        if len(fcurves) < 3:
            return []
        
        # Get Z-axis curve (height)
        z_curve = None
        for fcurve in fcurves:
            if fcurve.data_path.endswith('location') and fcurve.array_index == 2:
                z_curve = fcurve
                break
        
        if not z_curve:
            return []
        
        frame_start = int(z_curve.range()[0])
        frame_end = int(z_curve.range()[1])
        
        # Analyze Z movement to find stable periods
        z_positions = []
        z_velocities = []
        
        for frame in range(frame_start, frame_end + 1):
            z_pos = z_curve.evaluate(frame)
            z_vel = abs(MotionAnalyzer.calculate_velocity(z_curve, frame))
            z_positions.append(z_pos)
            z_velocities.append(z_vel)
        
        # Adaptive ground level detection
        sorted_z = sorted(z_positions)
        ground_level = sorted_z[len(sorted_z) // 4]  # 25th percentile
        adaptive_threshold = ground_level + ground_threshold
        
        # Find contact phases with hysteresis
        contact_phases = []
        in_contact = False
        contact_start = None
        
        for i, frame in enumerate(range(frame_start, frame_end + 1)):
            z_pos = z_positions[i]
            z_vel = z_velocities[i]
            
            # Contact criteria with hysteresis
            is_near_ground = z_pos <= adaptive_threshold
            is_stable = z_vel < stability_threshold
            
            if is_near_ground and is_stable:
                if not in_contact:
                    contact_start = frame
                    in_contact = True
            else:
                if in_contact and (z_vel > stability_threshold * 2 or z_pos > adaptive_threshold * 1.5):
                    # End contact with hysteresis
                    if contact_start is not None:
                        contact_phases.append((contact_start, frame - 1))
                    in_contact = False
        
        # Handle contact phase that continues to end
        if in_contact and contact_start is not None:
            contact_phases.append((contact_start, frame_end))
        
        # Filter out very short contact phases
        min_contact_duration = 3
        filtered_phases = [(start, end) for start, end in contact_phases 
                          if end - start >= min_contact_duration]
        
        return filtered_phases
    
    @staticmethod
    def detect_foot_sliding(foot_fcurves, sensitivity=1.0):
        """
        Advanced foot sliding detection with configurable sensitivity
        """
        if len(foot_fcurves) < 3:
            return []
        
        # Get X, Y, Z curves
        x_curve = y_curve = z_curve = None
        
        for fcurve in foot_fcurves:
            if fcurve.data_path.endswith('location'):
                if fcurve.array_index == 0:  # X
                    x_curve = fcurve
                elif fcurve.array_index == 1:  # Y
                    y_curve = fcurve
                elif fcurve.array_index == 2:  # Z
                    z_curve = fcurve
        
        if not all([x_curve, y_curve, z_curve]):
            return []
        
        # Detect contact phases first
        contact_phases = MotionAnalyzer.detect_contact_phases(foot_fcurves)
        
        sliding_frames = []
        
        for phase_start, phase_end in contact_phases:
            # Analyze horizontal movement during contact
            horizontal_movement = 0
            max_horizontal_velocity = 0
            
            for frame in range(phase_start, phase_end + 1):
                x_vel = abs(MotionAnalyzer.calculate_velocity(x_curve, frame))
                y_vel = abs(MotionAnalyzer.calculate_velocity(y_curve, frame))
                
                frame_h_vel = max(x_vel, y_vel)
                max_horizontal_velocity = max(max_horizontal_velocity, frame_h_vel)
                
                if frame < phase_end:
                    x_delta = abs(x_curve.evaluate(frame + 1) - x_curve.evaluate(frame))
                    y_delta = abs(y_curve.evaluate(frame + 1) - y_curve.evaluate(frame))
                    horizontal_movement += max(x_delta, y_delta)
            
            # Adaptive thresholds based on contact duration and sensitivity
            phase_duration = phase_end - phase_start + 1
            movement_threshold = (0.02 + (phase_duration * 0.005)) / sensitivity
            velocity_threshold = (0.03 + (phase_duration * 0.002)) / sensitivity
            
            # Sliding detection with both criteria
            excessive_movement = horizontal_movement > movement_threshold
            high_velocity = max_horizontal_velocity > velocity_threshold
            
            if excessive_movement or high_velocity:
                sliding_frames.extend(range(phase_start, phase_end + 1))
        
        return sliding_frames
    
    @staticmethod
    def calculate_energy_profile(fcurves, frame_range=None):
        """
        Calculate comprehensive energy profile for a set of F-curves
        Returns energy data for visualization and analysis
        """
        if not fcurves:
            return {}
        
        if frame_range is None:
            start_frame = min(int(fc.range()[0]) for fc in fcurves)
            end_frame = max(int(fc.range()[1]) for fc in fcurves)
        else:
            start_frame, end_frame = frame_range
        
        energy_profile = {
            'frames': [],
            'kinetic_energy': [],
            'potential_energy': [],
            'total_energy': [],
            'velocity_magnitude': [],
            'acceleration_magnitude': []
        }
        
        for frame in range(start_frame, end_frame + 1):
            frame_kinetic = 0
            frame_velocity = 0
            frame_acceleration = 0
            
            for fcurve in fcurves:
                velocity = MotionAnalyzer.calculate_velocity(fcurve, frame)
                acceleration = MotionAnalyzer.calculate_acceleration(fcurve, frame)
                
                frame_kinetic += velocity * velocity
                frame_velocity += abs(velocity)
                frame_acceleration += abs(acceleration)
            
            # Calculate potential energy (height-based for location curves)
            frame_potential = 0
            for fcurve in fcurves:
                if fcurve.data_path.endswith('location') and fcurve.array_index == 2:
                    height = fcurve.evaluate(frame)
                    frame_potential += max(0, height)  # Only positive heights
            
            energy_profile['frames'].append(frame)
            energy_profile['kinetic_energy'].append(frame_kinetic)
            energy_profile['potential_energy'].append(frame_potential)
            energy_profile['total_energy'].append(frame_kinetic + frame_potential)
            energy_profile['velocity_magnitude'].append(frame_velocity)
            energy_profile['acceleration_magnitude'].append(frame_acceleration)
        
        return energy_profile

class AnimationDataUtils:
    """Professional utilities for working with Blender animation data"""
    
    @staticmethod
    def get_selected_fcurves():
        """Get currently selected F-curves in Graph Editor with error handling"""
        fcurves = []
        
        try:
            for area in bpy.context.screen.areas:
                if area.type == 'GRAPH_EDITOR':
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            with bpy.context.temp_override(area=area, region=region):
                                space = area.spaces.active
                                if hasattr(space, 'dopesheet'):
                                    for fcurve in bpy.context.editable_fcurves:
                                        if fcurve.select:
                                            fcurves.append(fcurve)
        except Exception as e:
            print(f"Error getting selected F-curves: {e}")
        
        return fcurves
    
    @staticmethod
    def get_object_fcurves(obj):
        """Get all F-curves for an object with comprehensive coverage"""
        fcurves = []
        
        try:
            if obj and obj.animation_data:
                if obj.animation_data.action:
                    fcurves.extend(obj.animation_data.action.fcurves)
                
                # Include NLA track F-curves if any
                if obj.animation_data.nla_tracks:
                    for track in obj.animation_data.nla_tracks:
                        for strip in track.strips:
                            if strip.action:
                                fcurves.extend(strip.action.fcurves)
        except Exception as e:
            print(f"Error getting object F-curves: {e}")
        
        return fcurves
    
    @staticmethod
    def get_bone_fcurves(armature_obj, bone_name, data_type='location'):
        """Get F-curves for a specific bone with multiple data types"""
        if not armature_obj or not armature_obj.animation_data:
            return []
        
        action = armature_obj.animation_data.action
        if not action:
            return []
        
        fcurves = []
        data_path = f'pose.bones["{bone_name}"].{data_type}'
        
        for fcurve in action.fcurves:
            if fcurve.data_path == data_path:
                fcurves.append(fcurve)
        
        return fcurves
    
    @staticmethod
    def get_all_bone_fcurves(armature_obj, bone_names=None):
        """Get all F-curves for specified bones or all bones"""
        if not armature_obj or not armature_obj.animation_data:
            return {}
        
        action = armature_obj.animation_data.action
        if not action:
            return {}
        
        bone_fcurves = defaultdict(list)
        
        if bone_names is None:
            # Get all bones if none specified
            if armature_obj.type == 'ARMATURE':
                bone_names = [bone.name for bone in armature_obj.pose.bones]
            else:
                return {}
        
        for bone_name in bone_names:
            for data_type in ['location', 'rotation_euler', 'rotation_quaternion', 'scale']:
                fcurves = AnimationDataUtils.get_bone_fcurves(armature_obj, bone_name, data_type)
                if fcurves:
                    bone_fcurves[bone_name].extend(fcurves)
        
        return dict(bone_fcurves)
    
    @staticmethod
    def find_foot_bones(armature_obj):
        """Enhanced foot bone detection for rigify and custom rigs"""
        if not armature_obj or armature_obj.type != 'ARMATURE':
            return []
        
        foot_bones = []
        
        # Primary foot keywords (high priority)
        primary_keywords = ['foot_ik', 'foot.ik']
        
        # Secondary foot keywords
        secondary_keywords = ['foot', 'toe', 'heel']
        
        # Exclusion keywords
        exclude_keywords = ['tweak', 'mch-', 'def-', 'org-', 'vis_']
        
        for bone in armature_obj.pose.bones:
            bone_name_lower = bone.name.lower()
            
            # Skip excluded bones
            if any(exclude in bone_name_lower for exclude in exclude_keywords):
                continue
            
            # Check primary keywords first
            for keyword in primary_keywords:
                if keyword in bone_name_lower:
                    foot_bones.append(bone.name)
                    break
            else:
                # Check secondary keywords
                for keyword in secondary_keywords:
                    if keyword in bone_name_lower and 'ik' in bone_name_lower:
                        foot_bones.append(bone.name)
                        break
        
        return foot_bones
    
    @staticmethod
    def create_adjustment_action(base_action, suffix="_adjustment"):
        """Create a new action for adjustment layers"""
        if not base_action:
            return None
        
        try:
            # Create new action with unique name
            adj_action_name = base_action.name + suffix
            counter = 1
            while adj_action_name in bpy.data.actions:
                adj_action_name = f"{base_action.name}{suffix}_{counter:03d}"
                counter += 1
            
            adj_action = bpy.data.actions.new(name=adj_action_name)
            
            # Copy F-curves structure
            for fcurve in base_action.fcurves:
                new_fcurve = adj_action.fcurves.new(
                    data_path=fcurve.data_path,
                    index=fcurve.array_index
                )
                new_fcurve.color_mode = fcurve.color_mode
                new_fcurve.color = fcurve.color
                new_fcurve.extrapolation = fcurve.extrapolation
            
            return adj_action
            
        except Exception as e:
            print(f"Error creating adjustment action: {e}")
            return None
    
    @staticmethod
    def create_nla_layer(armature_obj, action, layer_name="Adjustment Layer"):
        """Create NLA layer for non-destructive workflow"""
        if not armature_obj or not action:
            return None
        
        try:
            # Ensure animation data exists
            if not armature_obj.animation_data:
                armature_obj.animation_data_create()
            
            # Create new NLA track
            nla_track = armature_obj.animation_data.nla_tracks.new()
            nla_track.name = layer_name
            
            # Create strip in the track
            strip = nla_track.strips.new(
                name=layer_name,
                start=1,
                action=action
            )
            
            # Configure strip for adjustment blending
            strip.blend_type = 'ADD'
            strip.influence = 1.0
            strip.use_auto_blend = True
            
            return nla_track, strip
            
        except Exception as e:
            print(f"Error creating NLA layer: {e}")
            return None

class AdjustmentBlendingEngine:
    """Professional adjustment blending engine with energy preservation"""
    
    @staticmethod
    def apply_velocity_aware_blend(base_fcurve, adjustment_fcurve, influence=1.0, 
                                 energy_preservation=0.8, contact_frames=None):
        """
        Core velocity-aware blending algorithm
        AdjustedPose = BasePose + (AdjustmentLayer × VelocityWeight × EnergyMask)
        """
        if not base_fcurve or not adjustment_fcurve:
            return None
        
        # Get frame range
        frame_start = int(min(base_fcurve.range()[0], adjustment_fcurve.range()[0]))
        frame_end = int(max(base_fcurve.range()[1], adjustment_fcurve.range()[1]))
        
        # Analyze movement patterns
        movement_regions = MotionAnalyzer.detect_movement_regions(base_fcurve)
        
        adjusted_values = {}
        
        for frame in range(frame_start, frame_end + 1):
            base_value = base_fcurve.evaluate(frame)
            adj_value = adjustment_fcurve.evaluate(frame)
            
            # Calculate velocity weight
            velocity_weight = AdjustmentBlendingEngine._calculate_velocity_weight(
                frame, movement_regions, energy_preservation
            )
            
            # Calculate contact mask
            contact_mask = 1.0
            if contact_frames and frame in contact_frames:
                contact_mask = 0.1  # Reduce influence during contact
            
            # Apply the professional blending formula
            adjustment = adj_value - base_value
            final_adjustment = adjustment * velocity_weight * contact_mask * influence
            adjusted_values[frame] = base_value + final_adjustment
        
        return adjusted_values
    
    @staticmethod
    def _calculate_velocity_weight(frame, movement_regions, energy_preservation):
        """Calculate velocity-based weight for energy preservation"""
        for start, end, energy, motion_type in movement_regions:
            if start <= frame <= end:
                # Weight based on energy level and motion type
                base_weight = min(1.0, energy / 2.0)  # Normalize energy
                
                # Adjust based on motion type
                type_multipliers = {
                    'FAST': 1.2,
                    'SUSTAINED': 1.0,
                    'QUICK': 0.9,
                    'SMOOTH': 0.8,
                    'SLOW': 0.6
                }
                
                type_weight = type_multipliers.get(motion_type, 1.0)
                final_weight = base_weight * type_weight * energy_preservation
                
                return min(1.0, max(0.1, final_weight))
        
        # Outside movement regions - minimal weight
        return 0.05
    
    @staticmethod
    def apply_layered_adjustments(base_fcurve, adjustment_layers, global_influence=1.0):
        """
        Apply multiple adjustment layers with proper blending hierarchy
        """
        if not base_fcurve or not adjustment_layers:
            return None
        
        frame_start = int(base_fcurve.range()[0])
        frame_end = int(base_fcurve.range()[1])
        
        final_values = {}
        
        for frame in range(frame_start, frame_end + 1):
            current_value = base_fcurve.evaluate(frame)
            
            # Apply each layer in order
            for layer_data in adjustment_layers:
                if not layer_data.get('active', True) or not layer_data.get('fcurve'):
                    continue
                
                layer_fcurve = layer_data['fcurve']
                blend_mode = layer_data.get('blend_mode', 'OVERLAY')
                influence = layer_data.get('influence', 1.0) * global_influence
                contact_frames = layer_data.get('contact_frames', [])
                energy_preservation = layer_data.get('energy_preservation', 0.8)
                
                # Apply blend based on mode
                if blend_mode == 'OVERLAY':
                    # Energy-preserving blend
                    blend_result = AdjustmentBlendingEngine.apply_velocity_aware_blend(
                        base_fcurve, layer_fcurve, influence, energy_preservation, contact_frames
                    )
                    if blend_result and frame in blend_result:
                        current_value = blend_result[frame]
                
                elif blend_mode == 'ADD':
                    layer_value = layer_fcurve.evaluate(frame)
                    adjustment = (layer_value - base_fcurve.evaluate(frame)) * influence
                    current_value += adjustment
                
                elif blend_mode == 'MULTIPLY':
                    layer_value = layer_fcurve.evaluate(frame)
                    current_value *= (1.0 + (layer_value - 1.0) * influence)
                
                elif blend_mode == 'REPLACE':
                    layer_value = layer_fcurve.evaluate(frame)
                    current_value = AdjustmentBlendingEngine.lerp(
                        current_value, layer_value, influence
                    )
                
                elif blend_mode == 'SUBTRACT':
                    layer_value = layer_fcurve.evaluate(frame)
                    adjustment = (layer_value - base_fcurve.evaluate(frame)) * influence
                    current_value -= adjustment
                
                elif blend_mode == 'SCREEN':
                    layer_value = layer_fcurve.evaluate(frame)
                    current_value = 1.0 - ((1.0 - current_value) * (1.0 - layer_value * influence))
            
            final_values[frame] = current_value
        
        return final_values
    
    @staticmethod
    def fix_foot_sliding_professional(foot_fcurves, sliding_frames, influence=1.0, 
                                    preserve_motion_flow=True):
        """
        Professional foot sliding fix with motion flow preservation
        """
        if not foot_fcurves or not sliding_frames:
            return False
        
        try:
            # Group consecutive sliding frames into contact phases
            contact_phases = AdjustmentBlendingEngine._group_sliding_frames(sliding_frames)
            
            # Get horizontal movement curves
            horizontal_curves = []
            for fcurve in foot_fcurves:
                if (fcurve.data_path.endswith('location') and 
                    fcurve.array_index in [0, 1]):  # X and Y axes
                    horizontal_curves.append(fcurve)
            
            if not horizontal_curves:
                return False
            
            # Apply professional sliding fix
            for phase_start, phase_end in contact_phases:
                AdjustmentBlendingEngine._fix_contact_phase(
                    horizontal_curves, phase_start, phase_end, influence, preserve_motion_flow
                )
            
            # Update all curves
            for fcurve in horizontal_curves:
                fcurve.update()
            
            return True
            
        except Exception as e:
            print(f"Error in professional foot sliding fix: {e}")
            return False
    
    @staticmethod
    def _group_sliding_frames(sliding_frames):
        """Group consecutive sliding frames into contact phases"""
        if not sliding_frames:
            return []
        
        contact_phases = []
        current_start = sliding_frames[0]
        current_end = sliding_frames[0]
        
        for frame in sliding_frames[1:]:
            if frame == current_end + 1:
                current_end = frame
            else:
                contact_phases.append((current_start, current_end))
                current_start = current_end = frame
        
        contact_phases.append((current_start, current_end))
        return contact_phases
    
    @staticmethod
    def _fix_contact_phase(horizontal_curves, phase_start, phase_end, influence, preserve_flow):
        """Fix individual contact phase with flow preservation"""
        phase_duration = phase_end - phase_start + 1
        
        for fcurve in horizontal_curves:
            # Calculate stable position (weighted average of phase)
            positions = [fcurve.evaluate(f) for f in range(phase_start, phase_end + 1)]
            
            if preserve_flow:
                # Use median for robustness
                stable_position = sorted(positions)[len(positions) // 2]
            else:
                # Use average
                stable_position = sum(positions) / len(positions)
            
            # Apply fix with graduated influence
            for frame in range(phase_start, phase_end + 1):
                # Calculate distance from phase center
                phase_center = (phase_start + phase_end) / 2
                distance_from_center = abs(frame - phase_center)
                max_distance = phase_duration / 2
                
                # Graduated influence - stronger in center
                if max_distance > 0:
                    frame_influence = influence * (1.0 - (distance_from_center / max_distance) * 0.5)
                else:
                    frame_influence = influence
                
                # Apply the fix
                AdjustmentBlendingEngine._apply_keyframe_fix(
                    fcurve, frame, stable_position, frame_influence
                )
    
    @staticmethod
    def _apply_keyframe_fix(fcurve, frame, target_value, influence):
        """Apply fix to specific keyframe with influence"""
        current_value = fcurve.evaluate(frame)
        new_value = AdjustmentBlendingEngine.lerp(current_value, target_value, influence)
        
        # Find existing keyframe or insert new one
        keyframe_found = False
        for kf in fcurve.keyframe_points:
            if abs(kf.co[0] - frame) < 0.5:
                kf.co[1] = new_value
                keyframe_found = True
                break
        
        if not keyframe_found:
            fcurve.keyframe_points.insert(frame, new_value)
    
    @staticmethod
    def update_preview(current_frame):
        """Update real-time preview for current frame"""
        try:
            # This would trigger real-time blend calculations
            # Implementation depends on specific preview requirements
            pass
        except Exception as e:
            print(f"Preview update error: {e}")
    
    @staticmethod
    def lerp(a, b, factor):
        """Linear interpolation"""
        return a + (b - a) * factor
    
    @staticmethod
    def smooth_lerp(a, b, factor):
        """Smooth interpolation with easing"""
        # Smooth step function
        smooth_factor = factor * factor * (3.0 - 2.0 * factor)
        return a + (b - a) * smooth_factor

# Utility functions for cache management
def clear_analysis_cache():
    """Clear the analysis cache to free memory"""
    global _analysis_cache
    with _cache_lock:
        _analysis_cache.clear()

def get_cache_info():
    """Get information about current cache usage"""
    with _cache_lock:
        return {
            'entries': len(_analysis_cache),
            'memory_estimate': len(_analysis_cache) * 1024  # Rough estimate
        }