# adjustment_blending/ui.py
"""
Professional user interface for adjustment blending system
Comprehensive panels with advanced controls and workflow integration
"""

import bpy
from bpy.types import Panel

class ADJBLEND_PT_main_panel(bpy.types.Panel):
    """Main control panel for professional adjustment blending"""
    bl_label = "Professional Adjustment Blending"
    bl_idname = "ADJBLEND_PT_main_panel"
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Adjustment"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.adjustment_blending
        
        # Header with workflow preset
        header_box = layout.box()
        header_box.label(text="Professional Workflow", icon='MODIFIER')
        
        row = header_box.row()
        row.prop(props, "workflow_preset", text="")
        row.operator("adjblend.cache_management", text="", icon='FILE_REFRESH').operation = 'CLEAR'
        
        # Master controls
        master_box = layout.box()
        master_box.label(text="Master Controls", icon='SETTINGS')
        
        col = master_box.column()
        col.prop(props, "master_influence", text="Master Influence")
        col.prop(props, "energy_preservation", text="Energy Preservation")
        
        row = col.row()
        row.prop(props, "preview_mode", toggle=True, icon='HIDE_OFF' if props.preview_mode else 'HIDE_ON')
        row.prop(props, "auto_update", toggle=True, icon='AUTO')
        
        layout.separator()
        
        # Quick actions
        actions_box = layout.box()
        actions_box.label(text="Quick Actions", icon='PLAY')
        
        col = actions_box.column(align=True)
        
        # Analysis
        analysis_row = col.row(align=True)
        analysis_op = analysis_row.operator("adjblend.analyze_motion_professional", 
                                           text="Analyze", icon='DRIVER')
        analysis_op.analysis_type = 'COMPREHENSIVE'
        analysis_op.target_selection = 'SELECTED_CURVES'
        
        # Sliding fix
        sliding_row = col.row(align=True)
        sliding_op = sliding_row.operator("adjblend.fix_sliding_professional", 
                                         text="Fix Sliding", icon='CONSTRAINT')
        sliding_op.target_mode = 'AUTO_DETECT'
        
        col.separator()
        
        # Layer creation
        create_row = col.row(align=True)
        create_op = create_row.operator("adjblend.create_adjustment_layer_professional", 
                                       text="Create Layer", icon='ADD')
        create_op.layer_type = 'GENERAL'
        create_op.source_type = 'SELECTED_CURVES'
        
        # Apply adjustments
        apply_row = col.row(align=True)
        apply_op = apply_row.operator("adjblend.apply_adjustment_professional", 
                                     text="Apply", icon='CHECKMARK')
        apply_op.apply_mode = 'ALL_LAYERS'

class ADJBLEND_PT_analysis_panel(bpy.types.Panel):
    """Advanced motion analysis panel"""
    bl_label = "Motion Analysis"
    bl_idname = "ADJBLEND_PT_analysis_panel"
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Adjustment"
    bl_parent_id = "ADJBLEND_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.adjustment_blending
        
        # Analysis type selection
        col = layout.column()
        col.label(text="Analysis Type:", icon='VIEWZOOM')
        
        # Comprehensive analysis
        comp_box = col.box()
        comp_row = comp_box.row()
        comp_op = comp_row.operator("adjblend.analyze_motion_professional", 
                                   text="Comprehensive", icon='DRIVER')
        comp_op.analysis_type = 'COMPREHENSIVE'
        comp_op.target_selection = 'SELECTED_CURVES'
        
        # Contact analysis
        contact_box = col.box()
        contact_row = contact_box.row()
        contact_op = contact_row.operator("adjblend.analyze_motion_professional", 
                                         text="Contact Focus", icon='CONSTRAINT')
        contact_op.analysis_type = 'CONTACT_FOCUSED'
        contact_op.target_selection = 'FOOT_BONES'
        
        # Sliding detection
        sliding_box = col.box()
        sliding_row = sliding_box.row()
        sliding_op = sliding_row.operator("adjblend.analyze_motion_professional", 
                                         text="Sliding Detection", icon='ERROR')
        sliding_op.analysis_type = 'SLIDING_DETECTION'
        sliding_op.target_selection = 'FOOT_BONES'
        
        layout.separator()
        
        # Analysis settings
        settings_box = layout.box()
        settings_box.label(text="Analysis Settings", icon='PREFERENCES')
        
        col = settings_box.column()
        col.prop(props, "velocity_threshold", text="Velocity Threshold")
        col.prop(props, "sliding_sensitivity", text="Sliding Sensitivity")
        col.prop(props, "analysis_precision", text="Precision")
        
        col.separator()
        
        # Visualization options
        viz_col = col.column()
        viz_col.label(text="Visualization:")
        viz_col.prop(props, "visualize_energy", text="Energy Patterns")
        viz_col.prop(props, "visualize_contacts", text="Contact Points")
        viz_col.prop(props, "visualize_velocity", text="Velocity Curves")

class ADJBLEND_PT_layers_panel(bpy.types.Panel):
    """Professional layer management panel"""
    bl_label = "Adjustment Layers"
    bl_idname = "ADJBLEND_PT_layers_panel"
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Adjustment"
    bl_parent_id = "ADJBLEND_PT_main_panel"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.adjustment_blending
        
        # Layer creation controls
        create_box = layout.box()
        create_row = create_box.row()
        create_row.label(text="Create Layer:", icon='ADD')
        
        # Layer type buttons
        type_row = create_box.row(align=True)
        
        general_op = type_row.operator("adjblend.create_adjustment_layer_professional", 
                                      text="General", icon='MODIFIER')
        general_op.layer_type = 'GENERAL'
        general_op.layer_name = "General Layer"
        
        contact_op = type_row.operator("adjblend.create_adjustment_layer_professional", 
                                      text="Contact", icon='CONSTRAINT')
        contact_op.layer_type = 'CONTACT_FIX'
        contact_op.layer_name = "Contact Fix"
        
        smooth_op = type_row.operator("adjblend.create_adjustment_layer_professional", 
                                     text="Smooth", icon='SMOOTHCURVE')
        smooth_op.layer_type = 'SMOOTHING'
        smooth_op.layer_name = "Smoothing"
        
        layout.separator()
        
        # Layer stack
        if len(props.layers) > 0:
            # Stack controls
            stack_box = layout.box()
            stack_header = stack_box.row()
            stack_header.label(text=f"Layer Stack ({len(props.layers)})", icon='RENDERLAYERS')
            
            # Solo mode toggle
            solo_row = stack_header.row()
            solo_row.alignment = 'RIGHT'
            solo_op = solo_row.operator("adjblend.layer_management", text="", 
                                       icon='SOLO_ON' if props.solo_mode else 'SOLO_OFF')
            solo_op.operation = 'SOLO'
            
            # Layer list
            for i, layer in enumerate(props.layers):
                layer_box = stack_box.box()
                
                # Layer header
                header_row = layer_box.row()
                
                # Visibility toggle
                vis_icon = 'HIDE_OFF' if layer.is_visible else 'HIDE_ON'
                header_row.prop(layer, "is_visible", text="", icon=vis_icon)
                
                # Layer name and selection
                name_row = header_row.row()
                name_row.prop(layer, "name", text="")
                if props.active_layer_index == i:
                    name_row.active = True
                
                # Layer type icon
                type_icons = {
                    'GENERAL': 'MODIFIER',
                    'CONTACT_FIX': 'CONSTRAINT', 
                    'SMOOTHING': 'SMOOTHCURVE',
                    'ENERGY_PRESERVE': 'FORCE_HARMONIC',
                    'PROCEDURAL': 'SCRIPT'
                }
                type_icon = type_icons.get(layer.layer_type, 'MODIFIER')
                header_row.label(text="", icon=type_icon)
                
                # Active indicator
                if props.active_layer_index == i:
                    header_row.label(text="", icon='LAYER_ACTIVE')
                
                # Layer controls (shown if active)
                if props.active_layer_index == i or not props.solo_mode:
                    controls_col = layer_box.column()
                    
                    # Main properties
                    prop_row = controls_col.row()
                    prop_row.prop(layer, "influence", text="Influence", slider=True)
                    
                    controls_col.prop(layer, "blend_mode", text="Mode")
                    
                    # Advanced properties (if active layer)
                    if props.active_layer_index == i:
                        adv_col = controls_col.column(align=True)
                        adv_col.prop(layer, "energy_threshold", text="Energy Threshold")
                        
                        if layer.layer_type in ['CONTACT_FIX', 'ENERGY_PRESERVE']:
                            adv_col.prop(layer, "preserve_contacts", text="Preserve Contacts")
                            adv_col.prop(layer, "contact_threshold", text="Contact Threshold")
                        
                        # Frame range
                        range_row = adv_col.row(align=True)
                        range_row.prop(layer, "frame_start", text="Start")
                        range_row.prop(layer, "frame_end", text="End")
                        
                        # Layer management buttons
                        mgmt_row = controls_col.row(align=True)
                        
                        # Move up/down
                        up_op = mgmt_row.operator("adjblend.layer_management", text="", icon='TRIA_UP')
                        up_op.operation = 'MOVE_UP'
                        
                        down_op = mgmt_row.operator("adjblend.layer_management", text="", icon='TRIA_DOWN')
                        down_op.operation = 'MOVE_DOWN'
                        
                        mgmt_row.separator()
                        
                        # Duplicate/Delete
                        dup_op = mgmt_row.operator("adjblend.layer_management", text="", icon='DUPLICATE')
                        dup_op.operation = 'DUPLICATE'
                        
                        del_op = mgmt_row.operator("adjblend.layer_management", text="", icon='TRASH')
                        del_op.operation = 'DELETE'
                
                # Click to select layer
                layer_box.operator("wm.context_set_int", text="").data_path = "scene.adjustment_blending.active_layer_index"
                # Note: In a full implementation, this would properly set the index to i
            
            layout.separator()
            
            # Stack operations
            stack_ops_row = layout.row(align=True)
            
            apply_all_op = stack_ops_row.operator("adjblend.apply_adjustment_professional", 
                                                 text="Apply All", icon='CHECKMARK')
            apply_all_op.apply_mode = 'ALL_LAYERS'
            
            clear_op = stack_ops_row.operator("adjblend.layer_management", 
                                             text="Clear All", icon='TRASH')
            clear_op.operation = 'CLEAR_ALL'
        
        else:
            # No layers message
            no_layers_box = layout.box()
            no_layers_box.label(text="No adjustment layers", icon='INFO')
            no_layers_box.label(text="Create a layer to begin")

class ADJBLEND_PT_character_panel(bpy.types.Panel):
    """Character-specific settings and tools"""
    bl_label = "Character Setup"
    bl_idname = "ADJBLEND_PT_character_panel"
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Adjustment"
    bl_parent_id = "ADJBLEND_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.adjustment_blending
        active_obj = context.active_object
        
        # Character info
        char_box = layout.box()
        char_box.label(text="Character Information", icon='ARMATURE_DATA')
        
        if active_obj and active_obj.type == 'ARMATURE':
            info_col = char_box.column()
            info_col.label(text=f"Active: {active_obj.name}")
            
            # Character type and scale
            info_col.prop(props, "character_type", text="Type")
            info_col.prop(props, "character_scale", text="Scale")
            info_col.prop(props, "foot_height_offset", text="Foot Offset")
            
            # Bone detection
            from .core import AnimationDataUtils
            foot_bones = AnimationDataUtils.find_foot_bones(active_obj)
            
            bone_col = info_col.column()
            bone_col.label(text=f"Foot Bones Detected: {len(foot_bones)}")
            
            if foot_bones:
                bone_box = bone_col.box()
                for bone_name in foot_bones[:6]:  # Show first 6
                    bone_box.label(text=f"• {bone_name}")
                if len(foot_bones) > 6:
                    bone_box.label(text=f"... and {len(foot_bones) - 6} more")
            
            # Animation info
            if active_obj.animation_data and active_obj.animation_data.action:
                action = active_obj.animation_data.action
                anim_col = info_col.column()
                anim_col.separator()
                anim_col.label(text=f"Action: {action.name}")
                anim_col.label(text=f"F-curves: {len(action.fcurves)}")
                
                if hasattr(action, 'frame_range'):
                    start, end = action.frame_range
                    anim_col.label(text=f"Range: {start:.0f} - {end:.0f}")
        else:
            char_box.label(text="Select an armature", icon='INFO')
        
        layout.separator()
        
        # Contact detection settings
        contact_box = layout.box()
        contact_box.label(text="Contact Detection", icon='CONSTRAINT')
        
        contact_col = contact_box.column()
        contact_col.prop(props, "contact_detection_mode", text="Mode")
        
        if props.contact_detection_mode == 'AUTO':
            contact_col.prop(props, "contact_threshold", text="Threshold")
        
        # Sliding detection settings
        sliding_box = layout.box()
        sliding_box.label(text="Sliding Detection", icon='ERROR')
        
        sliding_col = sliding_box.column()
        sliding_col.prop(props, "sliding_sensitivity", text="Sensitivity")
        
        # Quick fix button
        if active_obj and active_obj.type == 'ARMATURE':
            fix_row = sliding_col.row()
            fix_op = fix_row.operator("adjblend.fix_sliding_professional", 
                                     text="Auto Fix Sliding", icon='TOOL_SETTINGS')
            fix_op.target_mode = 'AUTO_DETECT'
            fix_op.fix_strength = 0.8

class ADJBLEND_PT_performance_panel(bpy.types.Panel):
    """Performance and optimization settings"""
    bl_label = "Performance"
    bl_idname = "ADJBLEND_PT_performance_panel"
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Adjustment"
    bl_parent_id = "ADJBLEND_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.adjustment_blending
        
        # Caching settings
        cache_box = layout.box()
        cache_box.label(text="Caching", icon='FILE_CACHE')
        
        cache_col = cache_box.column()
        cache_col.prop(props, "use_caching", text="Enable Caching")
        
        if props.use_caching:
            cache_col.prop(props, "cache_size", text="Cache Size")
            
            # Cache management
            cache_row = cache_col.row(align=True)
            
            info_op = cache_row.operator("adjblend.cache_management", 
                                        text="Info", icon='INFO')
            info_op.operation = 'INFO'
            
            clear_op = cache_row.operator("adjblend.cache_management", 
                                         text="Clear", icon='TRASH')
            clear_op.operation = 'CLEAR'
        
        # Processing settings
        proc_box = layout.box()
        proc_box.label(text="Processing", icon='PREFERENCES')
        
        proc_col = proc_box.column()
        proc_col.prop(props, "analysis_precision", text="Precision")
        proc_col.prop(props, "use_multiprocessing", text="Multi-core")
        
        # Debug settings
        debug_box = layout.box()
        debug_box.label(text="Debug", icon='CONSOLE')
        
        debug_col = debug_box.column()
        debug_col.prop(props, "show_debug_info", text="Console Output")

class ADJBLEND_PT_workflow_panel(bpy.types.Panel):
    """Workflow presets and templates"""
    bl_label = "Workflow Presets"
    bl_idname = "ADJBLEND_PT_workflow_panel"
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Adjustment"
    bl_parent_id = "ADJBLEND_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.adjustment_blending
        
        # Preset selection
        preset_box = layout.box()
        preset_box.label(text="Workflow Presets", icon='PRESET')
        
        preset_col = preset_box.column()
        preset_col.prop(props, "workflow_preset", text="")
        
        # Preset descriptions
        preset_descriptions = {
            'MOCAP_CLEANUP': "Optimize for cleaning motion capture data",
            'KEYFRAME_POLISH': "Polish hand-keyed animations",
            'PROCEDURAL_BLEND': "Blend procedural animation layers",
            'CONTACT_FIX': "Focus on ground contact preservation",
            'CUSTOM': "Custom workflow configuration"
        }
        
        desc_text = preset_descriptions.get(props.workflow_preset, "")
        if desc_text:
            preset_col.label(text=desc_text, icon='INFO')
        
        # Quick workflow buttons
        workflow_box = layout.box()
        workflow_box.label(text="Quick Workflows", icon='PLAY')
        
        workflow_col = workflow_box.column(align=True)
        
        # Mocap cleanup workflow
        mocap_row = workflow_col.row()
        mocap_row.label(text="Mocap Cleanup:", icon='RENDER_ANIMATION')
        
        mocap_ops = workflow_col.row(align=True)
        
        # Step 1: Analyze
        analyze_op = mocap_ops.operator("adjblend.analyze_motion_professional", 
                                       text="1. Analyze", icon='VIEWZOOM')
        analyze_op.analysis_type = 'COMPREHENSIVE'
        analyze_op.target_selection = 'FOOT_BONES'
        
        # Step 2: Fix sliding
        fix_op = mocap_ops.operator("adjblend.fix_sliding_professional", 
                                   text="2. Fix", icon='TOOL_SETTINGS')
        fix_op.target_mode = 'AUTO_DETECT'
        
        # Step 3: Create smoothing layer
        smooth_op = mocap_ops.operator("adjblend.create_adjustment_layer_professional", 
                                      text="3. Smooth", icon='SMOOTHCURVE')
        smooth_op.layer_type = 'SMOOTHING'
        smooth_op.layer_name = "Mocap Smooth"
        
        workflow_col.separator()
        
        # Contact fix workflow
        contact_row = workflow_col.row()
        contact_row.label(text="Contact Fix:", icon='CONSTRAINT')
        
        contact_ops = workflow_col.row(align=True)
        
        contact_analyze_op = contact_ops.operator("adjblend.analyze_motion_professional", 
                                                 text="Detect", icon='SEARCH')
        contact_analyze_op.analysis_type = 'CONTACT_FOCUSED'
        
        contact_fix_op = contact_ops.operator("adjblend.fix_sliding_professional", 
                                             text="Apply", icon='CHECKMARK')
        contact_fix_op.target_mode = 'AUTO_DETECT'

class ADJBLEND_PT_help_panel(bpy.types.Panel):
    """Help and documentation panel"""
    bl_label = "Help & Guide"
    bl_idname = "ADJBLEND_PT_help_panel"
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Adjustment"
    bl_parent_id = "ADJBLEND_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        # Quick start guide
        guide_box = layout.box()
        guide_box.label(text="Quick Start Guide", icon='HELP')
        
        steps_col = guide_box.column(align=True)
        steps_col.label(text="1. Select your rigify character")
        steps_col.label(text="2. Choose workflow preset")
        steps_col.label(text="3. Run motion analysis")
        steps_col.label(text="4. Create adjustment layers")
        steps_col.label(text="5. Apply blending")
        
        # Tips
        tips_box = layout.box()
        tips_box.label(text="Professional Tips", icon='LIGHT')
        
        tips_col = tips_box.column(align=True)
        tips_col.label(text="• Use 'Overlay' mode for energy preservation")
        tips_col.label(text="• Lower influence for subtle adjustments")
        tips_col.label(text="• Enable contact preservation for feet")
        tips_col.label(text="• Stack layers for complex adjustments")
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