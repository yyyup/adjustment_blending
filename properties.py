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