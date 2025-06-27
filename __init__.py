# adjustment_blending/__init__.py
"""
Professional Adjustment Blending Addon for Blender
Implements industry-standard non-destructive animation editing with energy preservation
Based on techniques pioneered at Ubisoft Montreal by Dan Lowe
"""

bl_info = {
    "name": "Professional Adjustment Blending",
    "author": "Your Name",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "Graph Editor > Sidebar > Adjustment Blending",
    "description": "Professional non-destructive animation editing with energy preservation",
    "category": "Animation",
    "doc_url": "",
    "tracker_url": "",
}

import bpy
from . import core, operators, ui, properties

def register():
    """Register all addon components"""
    try:
        properties.register()
        operators.register()
        ui.register()
        
        # Add property group to scene
        bpy.types.Scene.adjustment_blending = bpy.props.PointerProperty(
            type=properties.AdjustmentBlendingProperties
        )
        
        # Register app handlers for real-time updates
        if core.frame_change_handler not in bpy.app.handlers.frame_change_post:
            bpy.app.handlers.frame_change_post.append(core.frame_change_handler)
        
        print("Professional Adjustment Blending addon registered successfully")
        
    except Exception as e:
        print(f"Error registering Adjustment Blending addon: {e}")

def unregister():
    """Unregister all addon components"""
    try:
        # Remove app handlers
        if core.frame_change_handler in bpy.app.handlers.frame_change_post:
            bpy.app.handlers.frame_change_post.remove(core.frame_change_handler)
        
        ui.unregister()
        operators.unregister()
        properties.unregister()
        
        # Remove property group from scene
        if hasattr(bpy.types.Scene, 'adjustment_blending'):
            del bpy.types.Scene.adjustment_blending
        
        print("Professional Adjustment Blending addon unregistered successfully")
        
    except Exception as e:
        print(f"Error unregistering Adjustment Blending addon: {e}")

if __name__ == "__main__":
    register()