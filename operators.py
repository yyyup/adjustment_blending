# adjustment_blending/operators.py
"""
Professional operators for adjustment blending system
Implements complete workflow from analysis to application
"""

import bpy
from bpy.props import FloatProperty, EnumProperty, BoolProperty, StringProperty
from .core import (AdjustmentBlendingEngine, MotionAnalyzer, AnimationDataUtils, 
                   clear_analysis_cache, get_cache_info)
import time

# Global storage for operation data
_operation_data = {}

class ADJBLEND_OT_analyze_motion_professional(bpy.types.Operator):
    """Professional motion analysis with comprehensive reporting"""
    bl_idname = "adjblend.analyze_motion_professional"
    bl_label = "Analyze Motion (Professional)"
    bl_description = "Comprehensive motion analysis with energy profiling"
    bl_options = {'REGISTER'}
    
    analysis_type: EnumProperty(
        name="Analysis Type",
        items=[
            ('BASIC', "Basic", "Basic velocity analysis"),
            ('COMPREHENSIVE', "Comprehensive", "Full energy and motion analysis"),
            ('CONTACT_FOCUSED', "Contact Focused", "Focus on contact detection"),
            ('SLIDING_DETECTION', "Sliding Detection", "Detect sliding issues"),
        ],
        default='COMPREHENSIVE'
    )
    
    target_selection: EnumProperty(
        name="Target",
        items=[
            ('SELECTED_CURVES', "Selected F-Curves", "Analyze selected F-curves"),
            ('ACTIVE_OBJECT', "Active Object", "Analyze entire active object"),
            ('FOOT_BONES', "Foot Bones", "Auto-detect and analyze foot bones"),
        ],
        default='SELECTED_CURVES'
    )
    
    def execute(self, context):
        props = context.scene.adjustment_blending
        
        start_time = time.time()
        
        # Get target F-curves based on selection
        if self.target_selection == 'SELECTED_CURVES':
            fcurves = AnimationDataUtils.get_selected_fcurves()
            if not fcurves:
                self.report({'WARNING'}, "No F-curves selected")
                return {'CANCELLED'}
        
        elif self.target_selection == 'ACTIVE_OBJECT':
            active_obj = context.active_object
            if not active_obj:
                self.report({'WARNING'}, "No active object")
                return {'CANCELLED'}
            fcurves = AnimationDataUtils.get_object_fcurves(active_obj)
        
        elif self.target_selection == 'FOOT_BONES':
            active_obj = context.active_object
            if not active_obj or active_obj.type != 'ARMATURE':
                self.report({'WARNING'}, "Active object must be an armature")
                return {'CANCELLED'}
            
            foot_bones = AnimationDataUtils.find_foot_bones(active_obj)
            if not foot_bones:
                self.report({'WARNING'}, "No foot bones detected")
                return {'CANCELLED'}
            
            fcurves = []
            for bone_name in foot_bones:
                bone_fcurves = AnimationDataUtils.get_bone_fcurves(active_obj, bone_name, 'location')
                fcurves.extend(bone_fcurves)
        
        if not fcurves:
            self.report({'WARNING'}, "No F-curves found for analysis")
            return {'CANCELLED'}
        
        # Perform analysis based on type
        results = self._perform_analysis(fcurves, props)
        
        # Store results for other operators
        _operation_data['last_analysis'] = results
        
        analysis_time = time.time() - start_time
        
        # Report results
        self._report_results(results, analysis_time)
        
        return {'FINISHED'}
    
    def _perform_analysis(self, fcurves, props):
        """Perform the selected type of analysis"""
        results = {
            'fcurves_analyzed': len(fcurves),
            'movement_regions': [],
            'contact_phases': [],
            'sliding_frames': [],
            'energy_profile': {},
            'recommendations': []
        }
        
        print(f"\n{'='*60}")
        print("PROFESSIONAL MOTION ANALYSIS")
        print(f"{'='*60}")
        print(f"Analysis Type: {self.analysis_type}")
        print(f"F-Curves Analyzed: {len(fcurves)}")
        
        if self.analysis_type in ['BASIC', 'COMPREHENSIVE']:
            # Movement region analysis
            total_regions = 0
            for i, fcurve in enumerate(fcurves):
                movement_regions = MotionAnalyzer.detect_movement_regions(
                    fcurve, props.velocity_threshold
                )
                results['movement_regions'].extend(movement_regions)
                total_regions += len(movement_regions)
                
                if props.show_debug_info:
                    self._print_fcurve_analysis(fcurve, movement_regions, i)
            
            print(f"Total Movement Regions: {total_regions}")
        
        if self.analysis_type in ['COMPREHENSIVE', 'CONTACT_FOCUSED']:
            # Contact phase detection
            bone_groups = self._group_fcurves_by_bone(fcurves)
            total_contacts = 0
            
            for bone_name, bone_fcurves in bone_groups.items():
                if len(bone_fcurves) >= 3:  # Need X, Y, Z for contact detection
                    contact_phases = MotionAnalyzer.detect_contact_phases(bone_fcurves)
                    results['contact_phases'].extend(contact_phases)
                    total_contacts += len(contact_phases)
                    
                    if props.show_debug_info:
                        print(f"\nBone: {bone_name}")
                        print(f"  Contact Phases: {len(contact_phases)}")
                        for start, end in contact_phases:
                            print(f"    Frames {start}-{end} (duration: {end-start+1})")
            
            print(f"Total Contact Phases: {total_contacts}")
        
        if self.analysis_type in ['COMPREHENSIVE', 'SLIDING_DETECTION']:
            # Sliding detection
            bone_groups = self._group_fcurves_by_bone(fcurves)
            total_sliding = 0
            
            for bone_name, bone_fcurves in bone_groups.items():
                if len(bone_fcurves) >= 3:
                    sliding_frames = MotionAnalyzer.detect_foot_sliding(
                        bone_fcurves, props.sliding_sensitivity
                    )
                    if sliding_frames:
                        results['sliding_frames'].extend(sliding_frames)
                        total_sliding += len(sliding_frames)
                        
                        if props.show_debug_info:
                            print(f"\nSliding detected in {bone_name}: {len(sliding_frames)} frames")
            
            print(f"Total Sliding Frames: {total_sliding}")
        
        if self.analysis_type == 'COMPREHENSIVE':
            # Energy profile calculation
            if fcurves:
                results['energy_profile'] = MotionAnalyzer.calculate_energy_profile(fcurves)
                print(f"Energy Profile Generated: {len(results['energy_profile']['frames'])} frames")
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results)
        
        return results
    
    def _group_fcurves_by_bone(self, fcurves):
        """Group F-curves by bone for bone-specific analysis"""
        bone_groups = {}
        
        for fcurve in fcurves:
            if 'pose.bones[' in fcurve.data_path:
                # Extract bone name
                start = fcurve.data_path.find('["') + 2
                end = fcurve.data_path.find('"]', start)
                if start > 1 and end > start:
                    bone_name = fcurve.data_path[start:end]
                    if bone_name not in bone_groups:
                        bone_groups[bone_name] = []
                    bone_groups[bone_name].append(fcurve)
        
        return bone_groups
    
    def _print_fcurve_analysis(self, fcurve, movement_regions, index):
        """Print detailed F-curve analysis"""
        print(f"\nF-Curve {index + 1}: {fcurve.data_path}[{fcurve.array_index}]")
        print(f"  Keyframes: {len(fcurve.keyframe_points)}")
        print(f"  Frame Range: {fcurve.range()[0]:.0f} - {fcurve.range()[1]:.0f}")
        
        if movement_regions:
            print(f"  Movement Regions ({len(movement_regions)}):")
            for i, (start, end, energy, motion_type) in enumerate(movement_regions):
                duration = end - start + 1
                print(f"    Region {i+1}: Frames {start}-{end} ({duration} frames)")
                print(f"      Energy: {energy:.3f}, Type: {motion_type}")
        else:
            print("  No significant movement detected")
    
    def _generate_recommendations(self, results):
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Movement-based recommendations
        if results['movement_regions']:
            avg_energy = sum(r[2] for r in results['movement_regions']) / len(results['movement_regions'])
            if avg_energy > 1.5:
                recommendations.append("High energy motion detected - consider smoothing adjustments")
            elif avg_energy < 0.3:
                recommendations.append("Low energy motion - may benefit from amplification")
        
        # Contact-based recommendations
        if results['contact_phases']:
            total_contact_time = sum(end - start + 1 for start, end in results['contact_phases'])
            if total_contact_time > 0:
                recommendations.append(f"Ground contact detected - preserve contact integrity")
        
        # Sliding-based recommendations
        if results['sliding_frames']:
            recommendations.append(f"Foot sliding detected on {len(results['sliding_frames'])} frames - apply sliding fix")
        
        return recommendations
    
    def _report_results(self, results, analysis_time):
        """Report analysis results to user"""
        print(f"\nAnalysis completed in {analysis_time:.2f} seconds")
        
        if results['recommendations']:
            print("\nRECOMMENDations:")
            for i, rec in enumerate(results['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        print(f"{'='*60}\n")
        
        # User-facing report
        summary_parts = []
        if results['movement_regions']:
            summary_parts.append(f"{len(results['movement_regions'])} movement regions")
        if results['contact_phases']:
            summary_parts.append(f"{len(results['contact_phases'])} contact phases")
        if results['sliding_frames']:
            summary_parts.append(f"{len(results['sliding_frames'])} sliding frames")
        
        summary = ", ".join(summary_parts) if summary_parts else "No issues detected"
        self.report({'INFO'}, f"Analysis complete: {summary}")

class ADJBLEND_OT_create_adjustment_layer_professional(bpy.types.Operator):
    """Create professional adjustment layer with full feature set"""
    bl_idname = "adjblend.create_adjustment_layer_professional"
    bl_label = "Create Adjustment Layer"
    bl_description = "Create professional adjustment layer from selected animation"
    bl_options = {'REGISTER', 'UNDO'}
    
    layer_name: StringProperty(
        name="Layer Name",
        description="Name for the new adjustment layer",
        default="Adjustment Layer"
    )
    
    layer_type: EnumProperty(
        name="Layer Type",
        items=[
            ('GENERAL', "General", "General purpose adjustment layer"),
            ('CONTACT_FIX', "Contact Fix", "Specialized for fixing ground contacts"),
            ('SMOOTHING', "Smoothing", "Motion smoothing and cleanup"),
            ('ENERGY_PRESERVE', "Energy Preserve", "Energy preservation layer"),
        ],
        default='GENERAL'
    )
    
    source_type: EnumProperty(
        name="Source",
        items=[
            ('SELECTED_CURVES', "Selected F-Curves", "Use selected F-curves"),
            ('ACTIVE_ACTION', "Active Action", "Use entire active action"),
            ('DUPLICATE_ACTION', "Duplicate Action", "Create from duplicated action"),
        ],
        default='SELECTED_CURVES'
    )
    
    def execute(self, context):
        props = context.scene.adjustment_blending
        active_obj = context.active_object
        
        if not active_obj:
            self.report({'WARNING'}, "No active object")
            return {'CANCELLED'}
        
        # Create new adjustment layer
        new_layer = props.layers.add()
        new_layer.name = self.layer_name
        new_layer.layer_type = self.layer_type
        
        # Configure layer based on type
        self._configure_layer_by_type(new_layer)
        
        # Set up source data
        success = self._setup_layer_source(new_layer, active_obj)
        
        if not success:
            # Remove the layer if setup failed
            props.layers.remove(len(props.layers) - 1)
            self.report({'ERROR'}, "Failed to create adjustment layer")
            return {'CANCELLED'}
        
        # Set as active layer
        props.active_layer_index = len(props.layers) - 1
        
        self.report({'INFO'}, f"Created adjustment layer: {new_layer.name}")
        return {'FINISHED'}
    
    def _configure_layer_by_type(self, layer):
        """Configure layer settings based on type"""
        if layer.layer_type == 'CONTACT_FIX':
            layer.preserve_contacts = True
            layer.energy_threshold = 0.05
            layer.blend_mode = 'OVERLAY'
        
        elif layer.layer_type == 'SMOOTHING':
            layer.blend_mode = 'OVERLAY'
            layer.energy_threshold = 0.1
            layer.velocity_sensitivity = 0.8
        
        elif layer.layer_type == 'ENERGY_PRESERVE':
            layer.blend_mode = 'OVERLAY'
            layer.preserve_contacts = True
            layer.energy_threshold = 0.15
        
        elif layer.layer_type == 'GENERAL':
            layer.blend_mode = 'ADD'
            layer.energy_threshold = 0.1
    
    def _setup_layer_source(self, layer, active_obj):
        """Set up the source data for the adjustment layer"""
        try:
            if self.source_type == 'SELECTED_CURVES':
                selected_curves = AnimationDataUtils.get_selected_fcurves()
                if not selected_curves:
                    return False
                
                # Store curve references (simplified - in full implementation would copy data)
                bone_names = set()
                for fcurve in selected_curves:
                    if 'pose.bones[' in fcurve.data_path:
                        start = fcurve.data_path.find('["') + 2
                        end = fcurve.data_path.find('"]', start)
                        if start > 1 and end > start:
                            bone_names.add(fcurve.data_path[start:end])
                
                layer.target_bones = ",".join(bone_names)
            
            elif self.source_type == 'ACTIVE_ACTION':
                if not active_obj.animation_data or not active_obj.animation_data.action:
                    return False
                layer.source_action = active_obj.animation_data.action
            
            elif self.source_type == 'DUPLICATE_ACTION':
                if not active_obj.animation_data or not active_obj.animation_data.action:
                    return False
                
                base_action = active_obj.animation_data.action
                new_action = AnimationDataUtils.create_adjustment_action(
                    base_action, f"_{layer.name}"
                )
                if new_action:
                    layer.source_action = new_action
                else:
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error setting up layer source: {e}")
            return False

class ADJBLEND_OT_apply_adjustment_professional(bpy.types.Operator):
    """Apply professional adjustment blending to selected layers"""
    bl_idname = "adjblend.apply_adjustment_professional"
    bl_label = "Apply Adjustment Blending"
    bl_description = "Apply professional adjustment blending with energy preservation"
    bl_options = {'REGISTER', 'UNDO'}
    
    apply_mode: EnumProperty(
        name="Apply Mode",
        items=[
            ('ACTIVE_LAYER', "Active Layer", "Apply only active layer"),
            ('ALL_LAYERS', "All Layers", "Apply all active layers"),
            ('PREVIEW', "Preview", "Preview without applying"),
        ],
        default='ACTIVE_LAYER'
    )
    
    bake_result: BoolProperty(
        name="Bake Result",
        description="Bake the result to keyframes",
        default=False
    )
    
    def execute(self, context):
        props = context.scene.adjustment_blending
        active_obj = context.active_object
        
        if not active_obj:
            self.report({'WARNING'}, "No active object")
            return {'CANCELLED'}
        
        if not props.layers:
            self.report({'WARNING'}, "No adjustment layers to apply")
            return {'CANCELLED'}
        
        start_time = time.time()
        
        # Get layers to apply
        if self.apply_mode == 'ACTIVE_LAYER':
            if 0 <= props.active_layer_index < len(props.layers):
                layers_to_apply = [props.layers[props.active_layer_index]]
            else:
                self.report({'WARNING'}, "No active layer selected")
                return {'CANCELLED'}
        else:
            layers_to_apply = [layer for layer in props.layers if layer.is_active]
        
        if not layers_to_apply:
            self.report({'WARNING'}, "No active layers to apply")
            return {'CANCELLED'}
        
        # Apply adjustment blending
        success = self._apply_adjustment_blending(active_obj, layers_to_apply, props)
        
        if success:
            application_time = time.time() - start_time
            self.report({'INFO'}, f"Applied {len(layers_to_apply)} layers in {application_time:.2f}s")
        else:
            self.report({'ERROR'}, "Failed to apply adjustment blending")
            return {'CANCELLED'}
        
        return {'FINISHED'}
    
    def _apply_adjustment_blending(self, active_obj, layers, props):
        """Apply the adjustment blending to the object"""
        try:
            if not active_obj.animation_data or not active_obj.animation_data.action:
                return False
            
            base_action = active_obj.animation_data.action
            applied_count = 0
            
            # Process each target bone
            all_target_bones = set()
            for layer in layers:
                if layer.target_bones:
                    all_target_bones.update(layer.target_bones.split(','))
            
            if not all_target_bones:
                # Fall back to all bones if no specific targets
                if active_obj.type == 'ARMATURE':
                    all_target_bones = {bone.name for bone in active_obj.pose.bones}
            
            for bone_name in all_target_bones:
                bone_name = bone_name.strip()
                if not bone_name:
                    continue
                
                # Get base F-curves for this bone
                base_fcurves = AnimationDataUtils.get_bone_fcurves(
                    active_obj, bone_name, 'location'
                )
                
                if not base_fcurves:
                    continue
                
                # Apply layer stack to each F-curve
                for base_fcurve in base_fcurves:
                    success = self._apply_layers_to_fcurve(
                        base_fcurve, layers, props, bone_name
                    )
                    if success:
                        applied_count += 1
            
            print(f"Applied adjustment blending to {applied_count} F-curves")
            return applied_count > 0
            
        except Exception as e:
            print(f"Error applying adjustment blending: {e}")
            return False
    
    def _apply_layers_to_fcurve(self, base_fcurve, layers, props, bone_name):
        """Apply layer stack to individual F-curve"""
        try:
            # Prepare layer data for the blending engine
            layer_data_list = []
            
            for layer in layers:
                if not layer.is_active or not layer.is_visible:
                    continue
                
                # Check if this layer applies to this bone
                if layer.target_bones and bone_name not in layer.target_bones.split(','):
                    continue
                
                # Get adjustment F-curve (simplified - in full implementation would have actual curves)
                adjustment_fcurve = base_fcurve  # Placeholder
                
                # Detect contact frames if needed
                contact_frames = []
                if layer.preserve_contacts:
                    # Get all curves for this bone for contact detection
                    bone_fcurves = AnimationDataUtils.get_bone_fcurves(
                        bpy.context.active_object, bone_name, 'location'
                    )
                    if len(bone_fcurves) >= 3:
                        contact_phases = MotionAnalyzer.detect_contact_phases(bone_fcurves)
                        for start, end in contact_phases:
                            contact_frames.extend(range(start, end + 1))
                
                layer_data = {
                    'active': True,
                    'fcurve': adjustment_fcurve,
                    'blend_mode': layer.blend_mode,
                    'influence': layer.influence * props.master_influence,
                    'contact_frames': contact_frames,
                    'energy_preservation': props.energy_preservation
                }
                
                layer_data_list.append(layer_data)
            
            if not layer_data_list:
                return False
            
            # Apply the professional blending
            result_values = AdjustmentBlendingEngine.apply_layered_adjustments(
                base_fcurve, layer_data_list, props.master_influence
            )
            
            if result_values and self.bake_result:
                # Bake results to keyframes
                for frame, value in result_values.items():
                    base_fcurve.keyframe_points.insert(frame, value)
                base_fcurve.update()
            
            return True
            
        except Exception as e:
            print(f"Error applying layers to F-curve: {e}")
            return False

class ADJBLEND_OT_fix_sliding_professional(bpy.types.Operator):
    """Professional foot sliding fix with advanced options"""
    bl_idname = "adjblend.fix_sliding_professional"
    bl_label = "Fix Sliding (Professional)"
    bl_description = "Professional foot sliding fix with motion flow preservation"
    bl_options = {'REGISTER', 'UNDO'}
    
    target_mode: EnumProperty(
        name="Target",
        items=[
            ('AUTO_DETECT', "Auto Detect", "Automatically detect and fix foot sliding"),
            ('SELECTED_BONES', "Selected Bones", "Fix sliding on selected bones"),
            ('MANUAL_FRAMES', "Manual Frames", "Fix specific frame ranges"),
        ],
        default='AUTO_DETECT'
    )
    
    fix_strength: FloatProperty(
        name="Fix Strength",
        description="Strength of the sliding fix",
        default=0.8,
        min=0.0,
        max=1.0,
        subtype='FACTOR'
    )
    
    preserve_motion_flow: BoolProperty(
        name="Preserve Motion Flow",
        description="Preserve natural motion flow during fix",
        default=True
    )
    
    sensitivity: FloatProperty(
        name="Detection Sensitivity",
        description="Sensitivity for sliding detection",
        default=1.0,
        min=0.1,
        max=3.0
    )
    
    def execute(self, context):
        props = context.scene.adjustment_blending
        active_obj = context.active_object
        
        if not active_obj or active_obj.type != 'ARMATURE':
            self.report({'WARNING'}, "Active object must be an armature")
            return {'CANCELLED'}
        
        start_time = time.time()
        
        # Get target bones and F-curves
        target_data = self._get_target_data(active_obj)
        
        if not target_data:
            self.report({'WARNING'}, "No valid targets found for sliding fix")
            return {'CANCELLED'}
        
        # Apply sliding fix
        fixed_count = 0
        total_sliding_frames = 0
        
        for bone_name, fcurves in target_data.items():
            sliding_frames = MotionAnalyzer.detect_foot_sliding(fcurves, self.sensitivity)
            
            if sliding_frames:
                success = AdjustmentBlendingEngine.fix_foot_sliding_professional(
                    fcurves, sliding_frames, self.fix_strength, self.preserve_motion_flow
                )
                
                if success:
                    fixed_count += 1
                    total_sliding_frames += len(sliding_frames)
                    
                    if props.show_debug_info:
                        print(f"Fixed sliding in {bone_name}: {len(sliding_frames)} frames")
        
        fix_time = time.time() - start_time
        
        if fixed_count > 0:
            self.report({'INFO'}, 
                       f"Fixed sliding in {fixed_count} bones ({total_sliding_frames} frames) in {fix_time:.2f}s")
        else:
            self.report({'INFO'}, "No sliding detected to fix")
        
        return {'FINISHED'}
    
    def _get_target_data(self, armature_obj):
        """Get target bone data based on mode"""
        target_data = {}
        
        if self.target_mode == 'AUTO_DETECT':
            # Auto-detect foot bones
            foot_bones = AnimationDataUtils.find_foot_bones(armature_obj)
            for bone_name in foot_bones:
                fcurves = AnimationDataUtils.get_bone_fcurves(armature_obj, bone_name, 'location')
                if len(fcurves) >= 3:
                    target_data[bone_name] = fcurves
        
        elif self.target_mode == 'SELECTED_BONES':
            # Use selected F-curves, group by bone
            selected_fcurves = AnimationDataUtils.get_selected_fcurves()
            bone_groups = {}
            
            for fcurve in selected_fcurves:
                if 'pose.bones[' in fcurve.data_path and fcurve.data_path.endswith('location'):
                    start = fcurve.data_path.find('["') + 2
                    end = fcurve.data_path.find('"]', start)
                    if start > 1 and end > start:
                        bone_name = fcurve.data_path[start:end]
                        if bone_name not in bone_groups:
                            bone_groups[bone_name] = []
                        bone_groups[bone_name].append(fcurve)
            
            # Only include bones with complete location data
            for bone_name, fcurves in bone_groups.items():
                if len(fcurves) >= 3:
                    target_data[bone_name] = fcurves
        
        return target_data

class ADJBLEND_OT_layer_management(bpy.types.Operator):
    """Layer management operations"""
    bl_idname = "adjblend.layer_management"
    bl_label = "Layer Management"
    bl_description = "Manage adjustment layers"
    bl_options = {'REGISTER', 'UNDO'}
    
    operation: EnumProperty(
        name="Operation",
        items=[
            ('MOVE_UP', "Move Up", "Move layer up in stack"),
            ('MOVE_DOWN', "Move Down", "Move layer down in stack"),
            ('DUPLICATE', "Duplicate", "Duplicate active layer"),
            ('DELETE', "Delete", "Delete active layer"),
            ('SOLO', "Solo", "Solo active layer"),
            ('CLEAR_ALL', "Clear All", "Clear all layers"),
        ]
    )
    
    def execute(self, context):
        props = context.scene.adjustment_blending
        
        if self.operation == 'MOVE_UP':
            return self._move_layer(props, -1)
        elif self.operation == 'MOVE_DOWN':
            return self._move_layer(props, 1)
        elif self.operation == 'DUPLICATE':
            return self._duplicate_layer(props)
        elif self.operation == 'DELETE':
            return self._delete_layer(props)
        elif self.operation == 'SOLO':
            return self._solo_layer(props)
        elif self.operation == 'CLEAR_ALL':
            return self._clear_all_layers(props)
        
        return {'CANCELLED'}
    
    def _move_layer(self, props, direction):
        """Move layer up or down in stack"""
        if not props.layers or props.active_layer_index < 0:
            return {'CANCELLED'}
        
        current_idx = props.active_layer_index
        new_idx = current_idx + direction
        
        if 0 <= new_idx < len(props.layers):
            props.layers.move(current_idx, new_idx)
            props.active_layer_index = new_idx
            return {'FINISHED'}
        
        return {'CANCELLED'}
    
    def _duplicate_layer(self, props):
        """Duplicate the active layer"""
        if not props.layers or props.active_layer_index < 0:
            return {'CANCELLED'}
        
        source_layer = props.layers[props.active_layer_index]
        new_layer = props.layers.add()
        
        # Copy properties
        for prop_name in source_layer.bl_rna.properties.keys():
            if prop_name not in ['rna_type', 'name']:
                try:
                    setattr(new_layer, prop_name, getattr(source_layer, prop_name))
                except:
                    pass
        
        new_layer.name = f"{source_layer.name} Copy"
        props.active_layer_index = len(props.layers) - 1
        
        return {'FINISHED'}
    
    def _delete_layer(self, props):
        """Delete the active layer"""
        if not props.layers or props.active_layer_index < 0:
            return {'CANCELLED'}
        
        props.layers.remove(props.active_layer_index)
        
        # Adjust active index
        if props.active_layer_index >= len(props.layers):
            props.active_layer_index = max(0, len(props.layers) - 1)
        
        return {'FINISHED'}
    
    def _solo_layer(self, props):
        """Solo the active layer"""
        if not props.layers or props.active_layer_index < 0:
            return {'CANCELLED'}
        
        props.solo_mode = not props.solo_mode
        
        if props.solo_mode:
            # Hide all layers except active
            for i, layer in enumerate(props.layers):
                layer.is_visible = (i == props.active_layer_index)
        else:
            # Show all layers
            for layer in props.layers:
                layer.is_visible = True
        
        return {'FINISHED'}
    
    def _clear_all_layers(self, props):
        """Clear all layers"""
        props.layers.clear()
        props.active_layer_index = 0
        props.solo_mode = False
        return {'FINISHED'}

class ADJBLEND_OT_cache_management(bpy.types.Operator):
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

class ADJBLEND_OT_create_nla_layer(bpy.types.Operator):
    """Create an NLA layer from the active action or adjustment layer"""
    bl_idname = "adjblend.create_nla_layer"
    bl_label = "Create NLA Layer"
    bl_description = "Create non-destructive NLA layer for pipeline integration"
    bl_options = {'REGISTER', 'UNDO'}

    layer_name: StringProperty(
        name="Layer Name",
        description="Name of the new NLA layer",
        default="Adjustment NLA"
    )

    def execute(self, context):
        arm_obj = context.active_object
        if not arm_obj:
            self.report({'WARNING'}, "No active object")
            return {'CANCELLED'}

        props = context.scene.adjustment_blending

        action = None
        if props.layers and 0 <= props.active_layer_index < len(props.layers):
            layer = props.layers[props.active_layer_index]
            if layer.source_action:
                action = layer.source_action

        if not action and arm_obj.animation_data and arm_obj.animation_data.action:
            action = arm_obj.animation_data.action

        if not action:
            self.report({'WARNING'}, "No action found to create NLA layer")
            return {'CANCELLED'}

        result = AnimationDataUtils.create_nla_layer(arm_obj, action, self.layer_name)
        if result:
            self.report({'INFO'}, f"NLA layer '{self.layer_name}' created")
            return {'FINISHED'}

        self.report({'ERROR'}, "Failed to create NLA layer")
        return {'CANCELLED'}

def register():
    """Register all operator classes"""
    bpy.utils.register_class(ADJBLEND_OT_analyze_motion_professional)
    bpy.utils.register_class(ADJBLEND_OT_create_adjustment_layer_professional)
    bpy.utils.register_class(ADJBLEND_OT_apply_adjustment_professional)
    bpy.utils.register_class(ADJBLEND_OT_fix_sliding_professional)
    bpy.utils.register_class(ADJBLEND_OT_layer_management)
    bpy.utils.register_class(ADJBLEND_OT_cache_management)
    bpy.utils.register_class(ADJBLEND_OT_create_nla_layer)

def unregister():
    """Unregister all operator classes"""
    bpy.utils.unregister_class(ADJBLEND_OT_create_nla_layer)
    bpy.utils.unregister_class(ADJBLEND_OT_cache_management)
    bpy.utils.unregister_class(ADJBLEND_OT_layer_management)
    bpy.utils.unregister_class(ADJBLEND_OT_fix_sliding_professional)
    bpy.utils.unregister_class(ADJBLEND_OT_apply_adjustment_professional)
    bpy.utils.unregister_class(ADJBLEND_OT_create_adjustment_layer_professional)
    bpy.utils.unregister_class(ADJBLEND_OT_analyze_motion_professional)
