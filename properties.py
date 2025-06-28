# adjustment_blending/properties.py
"""
Professional property definitions for adjustment blending system
"""

import bpy
from bpy.props import (FloatProperty, EnumProperty, BoolProperty, StringProperty, 
                      CollectionProperty, IntProperty, PointerProperty)

class AdjustmentKeyframe(bpy.types.PropertyGroup):
    """Individual keyframe data for adjustment layers"""
    
    frame: IntProperty(
        name="Frame",
        description="Frame number for this keyframe"
    )
    
    value: FloatProperty(
        name="Value", 
        description="Adjustment value at this frame"
    )
    
    velocity_weight: FloatProperty(
        name="Velocity Weight",
        description="Calculated velocity weight for energy preservation",
        default=1.0,
        min=0.0,
        max=1.0
    )
    
    contact_mask: FloatProperty(
        name="Contact Mask",
        description="Contact preservation mask value",
        default=1.0,
        min=0.0,
        max=1.0
    )

class AdjustmentLayer(bpy.types.PropertyGroup):
    """Professional adjustment layer with full feature set"""
    
    name: StringProperty(
        name="Layer Name",
        description="Name of the adjustment layer",
        default="Adjustment Layer"
    )
    
    layer_type: EnumProperty(
        name="Layer Type",
        description="Type of adjustment layer",
        items=[
            ('GENERAL', "General", "General purpose adjustment layer", 'MODIFIER', 0),
            ('CONTACT_FIX', "Contact Fix", "Specialized for fixing ground contacts", 'CONSTRAINT', 1),
            ('SMOOTHING', "Smoothing", "Motion smoothing and cleanup", 'SMOOTHCURVE', 2),
            ('ENERGY_PRESERVE', "Energy Preserve", "Energy preservation layer", 'FORCE_HARMONIC', 3),
            ('PROCEDURAL', "Procedural", "Procedural animation adjustments", 'SCRIPT', 4),
        ],
        default='GENERAL'
    )
    
    influence: FloatProperty(
        name="Influence",
        description="Layer influence on final result",
        default=1.0,
        min=0.0,
        max=2.0,
        subtype='FACTOR'
    )
    
    blend_mode: EnumProperty(
        name="Blend Mode",
        description="How this layer blends with underlying layers",
        items=[
            ('ADD', "Add", "Add adjustment values to base", 'PLUS', 0),
            ('MULTIPLY', "Multiply", "Multiply adjustment with base", 'X', 1),
            ('REPLACE', "Replace", "Replace base with adjustment", 'FILE_REFRESH', 2),
            ('OVERLAY', "Overlay", "Energy-preserving smart blend", 'MOD_WAVE', 3),
            ('SCREEN', "Screen", "Screen blend mode", 'LIGHT', 4),
            ('SUBTRACT', "Subtract", "Subtract adjustment from base", 'REMOVE', 5),
        ],
        default='OVERLAY'
    )
    
    is_active: BoolProperty(
        name="Active",
        description="Whether this layer is active",
        default=True
    )
    
    is_visible: BoolProperty(
        name="Visible",
        description="Whether this layer is visible in preview",
        default=True
    )
    
    is_locked: BoolProperty(
        name="Locked",
        description="Whether this layer is locked from editing",
        default=False
    )
    
    frame_start: IntProperty(
        name="Start Frame",
        description="Start frame for this adjustment layer",
        default=1
    )
    
    frame_end: IntProperty(
        name="End Frame", 
        description="End frame for this adjustment layer",
        default=250
    )
    
    preserve_contacts: BoolProperty(
        name="Preserve Contacts",
        description="Preserve contact points and low-energy regions",
        default=True
    )
    
    energy_threshold: FloatProperty(
        name="Energy Threshold",
        description="Minimum energy level to apply adjustments",
        default=0.1,
        min=0.0,
        max=2.0,
        precision=3
    )
    
    contact_threshold: FloatProperty(
        name="Contact Threshold",
        description="Threshold for detecting ground contacts",
        default=0.05,
        min=0.0,
        max=1.0,
        precision=3
    )
    
    velocity_sensitivity: FloatProperty(
        name="Velocity Sensitivity",
        description="Sensitivity for velocity-based blending",
        default=1.0,
        min=0.1,
        max=3.0,
        subtype='FACTOR'
    )
    
    # Reference to source action/NLA data
    source_action: PointerProperty(
        type=bpy.types.Action,
        name="Source Action",
        description="Source action for this adjustment layer"
    )
    
    target_bones: StringProperty(
        name="Target Bones",
        description="Comma-separated list of target bone names",
        default=""
    )
    
    # Keyframe data collection
    keyframes: CollectionProperty(
        type=AdjustmentKeyframe,
        name="Adjustment Keyframes"
    )

class AdjustmentBlendingProperties(bpy.types.PropertyGroup):
    """Main property group for professional adjustment blending system"""
    
    layers: CollectionProperty(
        type=AdjustmentLayer,
        name="Adjustment Layers"
    )
    
    active_layer_index: IntProperty(
        name="Active Layer Index",
        description="Index of currently active layer",
        default=0
    )
    
    # Global system settings
    master_influence: FloatProperty(
        name="Master Influence",
        description="Global influence multiplier for all layers",
        default=1.0,
        min=0.0,
        max=2.0,
        subtype='FACTOR'
    )
    
    energy_preservation: FloatProperty(
        name="Energy Preservation",
        description="How much to preserve original motion energy",
        default=0.8,
        min=0.0,
        max=1.0,
        subtype='FACTOR'
    )
    
    auto_update: BoolProperty(
        name="Auto Update",
        description="Automatically update blend when keyframes change",
        default=False
    )
    
    preview_mode: BoolProperty(
        name="Preview Mode",
        description="Show real-time preview of adjustments",
        default=False
    )
    
    # Advanced analysis settings
    velocity_threshold: FloatProperty(
        name="Velocity Threshold",
        description="Minimum velocity to detect as movement",
        default=0.1,
        min=0.01,
        max=2.0,
        precision=3
    )
    
    contact_detection_mode: EnumProperty(
        name="Contact Detection",
        description="Method for detecting ground contacts",
        items=[
            ('AUTO', "Automatic", "Automatic contact detection", 'AUTO', 0),
            ('MANUAL', "Manual", "Manual contact point specification", 'HAND', 1),
            ('CONSTRAINT', "Constraint Based", "Use constraints for contact detection", 'CONSTRAINT', 2),
            ('DISABLED', "Disabled", "Disable contact detection", 'CANCEL', 3),
        ],
        default='AUTO'
    )
    
    sliding_sensitivity: FloatProperty(
        name="Sliding Sensitivity",
        description="Sensitivity for detecting foot sliding",
        default=0.5,
        min=0.1,
        max=2.0,
        subtype='FACTOR'
    )
    
    # Performance settings
    use_caching: BoolProperty(
        name="Use Caching",
        description="Cache analysis results for better performance",
        default=True
    )
    
    cache_size: IntProperty(
        name="Cache Size",
        description="Maximum number of frames to cache",
        default=1000,
        min=100,
        max=10000
    )
    
    analysis_precision: EnumProperty(
        name="Analysis Precision",
        description="Precision level for motion analysis",
        items=[
            ('LOW', "Low", "Fast analysis, less accurate", 'TRIA_DOWN', 0),
            ('MEDIUM', "Medium", "Balanced speed and accuracy", 'TRIA_RIGHT', 1), 
            ('HIGH', "High", "Slow analysis, most accurate", 'TRIA_UP', 2),
            ('EXTREME', "Extreme", "Maximum precision for final output", 'TRIA_UP_BAR', 3),
        ],
        default='MEDIUM'
    )
    
    use_multiprocessing: BoolProperty(
        name="Use Multiprocessing",
        description="Use multiple CPU cores for processing",
        default=True
    )
    
    # Debug and visualization
    show_debug_info: BoolProperty(
        name="Show Debug Info",
        description="Show debug information in console",
        default=False
    )
    
    visualize_energy: BoolProperty(
        name="Visualize Energy",
        description="Show energy patterns in Graph Editor",
        default=False
    )
    
    visualize_contacts: BoolProperty(
        name="Visualize Contacts",
        description="Highlight contact points in viewport",
        default=False
    )
    
    visualize_velocity: BoolProperty(
        name="Visualize Velocity", 
        description="Show velocity patterns as overlays",
        default=False
    )
    
    # Character-specific settings
    character_scale: FloatProperty(
        name="Character Scale",
        description="Scale factor for character (affects thresholds)",
        default=1.0,
        min=0.1,
        max=10.0
    )
    
    character_type: EnumProperty(
        name="Character Type",
        description="Type of character for optimization",
        items=[
            ('HUMAN', "Human", "Human character with standard proportions", 'ARMATURE_DATA', 0),
            ('QUADRUPED', "Quadruped", "Four-legged character", 'MESH_MONKEY', 1),
            ('CREATURE', "Creature", "Non-standard creature", 'FORCE_TURBULENCE', 2),
            ('MECHANICAL', "Mechanical", "Mechanical/robotic character", 'MODIFIER', 3),
            ('CUSTOM', "Custom", "Custom character setup", 'SETTINGS', 4),
        ],
        default='HUMAN'
    )
    
    foot_height_offset: FloatProperty(
        name="Foot Height Offset",
        description="Additional offset for foot height detection",
        default=0.0,
        min=-1.0,
        max=1.0,
        precision=3
    )
    
    # Workflow presets
    workflow_preset: EnumProperty(
        name="Workflow Preset",
        description="Preset configurations for different workflows",
        items=[
            ('MOCAP_CLEANUP', "Mocap Cleanup", "Optimized for motion capture cleanup", 'RENDER_ANIMATION', 0),
            ('KEYFRAME_POLISH', "Keyframe Polish", "Polish hand-keyed animation", 'KEYFRAME_HLT', 1),
            ('PROCEDURAL_BLEND', "Procedural Blend", "Blend procedural animations", 'SCRIPT', 2),
            ('CONTACT_FIX', "Contact Fix", "Focus on fixing ground contacts", 'CONSTRAINT', 3),
            ('CUSTOM', "Custom", "Custom workflow settings", 'PREFERENCES', 4),
        ],
        default='MOCAP_CLEANUP'
    )
    
    # Layer management
    solo_mode: BoolProperty(
        name="Solo Mode",
        description="Show only active layer (solo mode)",
        default=False
    )
    
    layer_isolation: BoolProperty(
        name="Layer Isolation",
        description="Isolate selected layers for editing",
        default=False
    )

def register():
    """Register all property classes"""
    bpy.utils.register_class(AdjustmentKeyframe)
    bpy.utils.register_class(AdjustmentLayer)
    bpy.utils.register_class(AdjustmentBlendingProperties)

def unregister():
    """Unregister all property classes"""
    bpy.utils.unregister_class(AdjustmentBlendingProperties)
    bpy.utils.unregister_class(AdjustmentLayer)
    bpy.utils.unregister_class(AdjustmentKeyframe)