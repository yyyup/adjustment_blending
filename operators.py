    """Cache management operations"""
    bl_idname = "adjblend.cache_management"
    bl_label = "Cache Management"
    bl_description = "Manage analysis cache"
    bl_options = {'REGISTER'}
    
    operation: EnumProperty(
        name="Operation",
        items=[
            ('CLEAR', "Clear Cache", "Clear analysis cache"),
            ('INFO', "Cache Info", "Show cache information"),
        ]
    )
    
    def execute(self, context):
        if self.operation == 'CLEAR':
            clear_analysis_cache()
            self.report({'INFO'}, "Analysis cache cleared")
        
        elif self.operation == 'INFO':
            cache_info = get_cache_info()
            self.report({'INFO'}, 
                       f"Cache: {cache_info['entries']} entries, ~{cache_info['memory_estimate']}KB")
        
        return {'FINISHED'}

def register():
    """Register all operator classes"""
    bpy.utils.register_class(ADJBLEND_OT_analyze_motion_professional)
    bpy.utils.register_class(ADJBLEND_OT_create_adjustment_layer_professional)
    bpy.utils.register_class(ADJBLEND_OT_apply_adjustment_professional)
    bpy.utils.register_class(ADJBLEND_OT_fix_sliding_professional)
    bpy.utils.register_class(ADJBLEND_OT_layer_management)
    bpy.utils.register_class(ADJBLEND_OT_cache_management)

def unregister():
    """Unregister all operator classes"""
    bpy.utils.unregister_class(ADJBLEND_OT_cache_management)
    bpy.utils.unregister_class(ADJBLEND_OT_layer_management)
    bpy.utils.unregister_class(ADJBLEND_OT_fix_sliding_professional)
    bpy.utils.unregister_class(ADJBLEND_OT_apply_adjustment_professional)
    bpy.utils.unregister_class(ADJBLEND_OT_create_adjustment_layer_professional)
    bpy.utils.unregister_class(ADJBLEND_OT_analyze_motion_professional)