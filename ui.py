        tips_col.label(text="• Check console for detailed analysis")
        
        # Blend modes reference
        blend_box = layout.box()
        blend_box.label(text="Blend Modes", icon='NODE_COMPOSITING')
        
        blend_col = blend_box.column(align=True)
        blend_col.label(text="Add: Additive adjustments")
        blend_col.label(text="Multiply: Scaling adjustments")
        blend_col.label(text="Replace: Direct replacement")
        blend_col.label(text="Overlay: Energy-preserving blend")
        blend_col.label(text="Subtract: Removal adjustments")
        
        # Troubleshooting
        trouble_box = layout.box()
        trouble_box.label(text="Troubleshooting", icon='ERROR')
        
        trouble_col = trouble_box.column(align=True)
        trouble_col.label(text="No sliding detected:")
        trouble_col.label(text="  • Increase sensitivity")
        trouble_col.label(text="  • Check foot bone selection")
        trouble_col.label(text="Motion too aggressive:")
        trouble_col.label(text="  • Lower influence")
        trouble_col.label(text="  • Increase energy preservation")

def register():
    """Register all UI panel classes"""
    bpy.utils.register_class(ADJBLEND_PT_main_panel)
    bpy.utils.register_class(ADJBLEND_PT_analysis_panel)
    bpy.utils.register_class(ADJBLEND_PT_layers_panel)
    bpy.utils.register_class(ADJBLEND_PT_character_panel)
    bpy.utils.register_class(ADJBLEND_PT_performance_panel)
    bpy.utils.register_class(ADJBLEND_PT_workflow_panel)
    bpy.utils.register_class(ADJBLEND_PT_help_panel)

def unregister():
    """Unregister all UI panel classes"""
    bpy.utils.unregister_class(ADJBLEND_PT_help_panel)
    bpy.utils.unregister_class(ADJBLEND_PT_workflow_panel)
    bpy.utils.unregister_class(ADJBLEND_PT_performance_panel)
    bpy.utils.unregister_class(ADJBLEND_PT_character_panel)
    bpy.utils.unregister_class(ADJBLEND_PT_layers_panel)
    bpy.utils.unregister_class(ADJBLEND_PT_analysis_panel)
    bpy.utils.unregister_class(ADJBLEND_PT_main_panel)