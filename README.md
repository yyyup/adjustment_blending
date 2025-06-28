# Professional Adjustment Blending for Blender

A professional-grade Blender addon implementing industry-standard adjustment blending techniques pioneered at Ubisoft Montreal by Dan Lowe. This system provides non-destructive animation editing with energy preservation, contact point maintenance, and real-time IK adaptation.

## 🎯 Project Status

**Current Phase:** Core System Complete + Real-time IK Adaptation (In Progress)

### ✅ Completed Features
- **Core adjustment blending algorithms** with velocity-aware energy preservation
- **Professional motion analysis** with movement region detection and contact phase analysis
- **Multi-layer adjustment system** with proper blend modes (Add, Multiply, Overlay, etc.)
- **Advanced foot sliding detection and fixing** with motion flow preservation
- **Comprehensive UI system** with workflow presets and layer management
- **Performance optimization** with caching and multi-threading support
- **Complete property system** for professional workflow integration

### 🔄 In Development
- **Real-time IK adaptation system** for automatic foot planting during root motion
- **Dynamic constraint space switching** (local/world/custom)
- **Live constraint weight management** based on contact detection
- **Automatic rigify constraint setup** for seamless integration

### 🎯 Next Priorities
1. Complete real-time IK adaptation system
2. Add NLA layer integration for true non-destructive workflow
3. Implement GPU acceleration for real-time preview
4. Add export/import for pipeline integration
5. Create comprehensive documentation and video tutorials

## 📁 Project Structure

```
adjustment_blending/
├── __init__.py              # Main addon registration
├── properties.py            # Complete property system with 50+ professional settings
├── core.py                  # Advanced algorithms: velocity analysis, energy preservation, caching
├── operators.py             # Professional operators: analysis, layer management, sliding fixes
├── ui.py                    # Comprehensive UI with 7 panels and workflow presets
├── ik_adaptation.py         # [IN PROGRESS] Real-time IK adaptation system
└── README.md               # This file
```

## 🚀 Installation

1. Download or clone this repository
2. Copy the `adjustment_blending` folder to your Blender addons directory:
   - Windows: `%APPDATA%/Blender Foundation/Blender/4.4/scripts/addons/`
   - macOS: `~/Library/Application Support/Blender/4.4/scripts/addons/`
   - Linux: `~/.config/blender/4.4/scripts/addons/`
3. Enable the addon in Blender Preferences > Add-ons > Animation
4. Access via Graph Editor > Sidebar > Adjustment tab

## 💡 Core Philosophy

This addon implements the **adjustment blending formula**:
```
AdjustedPose = BasePose + (AdjustmentLayer × VelocityWeight × EnergyMask × ContactMask)
```

### Key Principles:
- **Energy Preservation**: Adjustments only applied where base motion already exists
- **Contact Awareness**: Maintains ground contact integrity during blending
- **Non-destructive Workflow**: Original animation data remains untouched
- **Layer-based System**: Multiple adjustments stack intelligently
- **Real-time Feedback**: Immediate preview of blending results

## 🎬 Professional Workflows

### Mocap Cleanup Workflow
1. Select rigify character with mocap animation
2. Use "Comprehensive Analysis" to detect motion patterns
3. Apply "Auto Fix Sliding" to resolve foot sliding issues
4. Create "Smoothing Layer" for motion refinement
5. Apply all layers with energy preservation

### Contact Fixing Workflow
1. Run "Contact Focus" analysis to detect ground contact phases
2. Use "Fix Sliding (Professional)" with auto-detection
3. Create "Contact Fix" layer for manual refinements
4. Enable contact preservation for foot planting

### Layer Stacking Workflow
1. Create multiple adjustment layers with different types
2. Use various blend modes (Overlay for energy preservation)
3. Adjust influence and energy thresholds per layer
4. Apply entire stack with "Apply All Layers"

## 🔧 Technical Implementation

### Core Algorithms
- **Motion Analysis**: Velocity and acceleration-based movement detection
- **Energy Preservation**: Maintains natural motion characteristics during blending
- **Contact Detection**: Sophisticated ground contact phase identification
- **Sliding Fix**: Professional foot sliding correction with flow preservation
- **Layer Blending**: Multi-layer stack with proper blend mode mathematics

### Performance Features
- **Analysis Caching**: Intelligent caching system for repeated calculations
- **Multi-threading**: Parallel processing for complex character rigs
- **LOD System**: Level-of-detail optimization for performance
- **Real-time Preview**: Interactive feedback during adjustment operations

### Architecture
- **Modular Design**: Clean separation between core algorithms, operators, and UI
- **Professional Properties**: 50+ settings for fine-tuned control
- **Error Handling**: Robust error management and user feedback
- **Extensible Framework**: Easy to add new blend modes and analysis types

## 🎮 Usage Examples

### Basic Sliding Fix
```python
# Auto-detect and fix foot sliding
bpy.ops.adjblend.fix_sliding_professional(
    target_mode='AUTO_DETECT',
    fix_strength=0.8,
    preserve_motion_flow=True
)
```

### Professional Analysis
```python
# Comprehensive motion analysis
bpy.ops.adjblend.analyze_motion_professional(
    analysis_type='COMPREHENSIVE',
    target_selection='FOOT_BONES'
)
```

### Layer Creation
```python
# Create energy-preserving adjustment layer
bpy.ops.adjblend.create_adjustment_layer_professional(
    layer_type='ENERGY_PRESERVE',
    layer_name="Energy Layer",
    source_type='SELECTED_CURVES'
)
```

## 🔬 Research Foundation

This implementation is based on:
- **Dan Lowe's GDC 2016 talk** on mocap automation techniques at Ubisoft Montreal
- **MobuCore repository** algorithms for MotionBuilder integration
- **Professional Maya plugins** like Smart Layer and Shift Animation Tool
- **Academic research** on motion blending and energy preservation

### Key References:
- [YouTube: Dan Lowe - Adjustment Blending](https://www.youtube.com/watch?v=jfg9gh5mvs0&t=2464s)
- [GitHub: MobuCore](https://github.com/Danlowlows/MobuCore)
- Industry papers on motion capture cleanup and procedural animation

## 🛠 Development Roadmap

### Phase 1: Foundation ✅ (Complete)
- Core adjustment blending algorithms
- Basic UI and operator system
- Motion analysis and sliding detection

### Phase 2: Professional Features ✅ (Complete)
- Multi-layer system with blend modes
- Advanced property system
- Performance optimization
- Comprehensive UI with workflow presets

### Phase 3: Real-time Adaptation 🔄 (In Progress)
- **Real-time IK adaptation system**
- Dynamic constraint space switching
- Automatic foot planting during root motion
- Live constraint weight management

### Phase 4: Pipeline Integration (Planned)
- NLA layer integration for non-destructive workflow
- Export/import for studio pipelines
- GPU acceleration for real-time preview
- Advanced visualization tools

### Phase 5: Production Ready (Planned)
- Comprehensive documentation
- Video tutorial series
- Performance benchmarking
- Studio deployment tools

## 🧪 Testing & Validation

### Test Scenarios
1. **Rigify Character**: Standard rigify armature with mocap animation
2. **In-place Walk Cycle**: Walk cycle with root translation on NLA layer
3. **Complex Character Rigs**: Custom rigs with non-standard bone naming
4. **Large Datasets**: 1000+ frame animations with multiple characters
5. **Pipeline Integration**: Integration with studio animation workflows

### Performance Targets
- **Real-time Preview**: 60 FPS during adjustment operations
- **Analysis Speed**: <2 seconds for 500-frame character analysis
- **Memory Usage**: <500MB for complex character with 10 adjustment layers
- **Scalability**: Support for 100+ characters in single scene

## 🤝 Contributing

### Development Setup
1. Clone repository and set up Blender development environment
2. Follow Blender addon development best practices
3. Test with rigify characters and mocap data
4. Submit pull requests with comprehensive testing

### Code Standards
- **Python 3.10+** compatibility for Blender 4.0+
- **Type hints** for all functions and methods
- **Comprehensive error handling** with user-friendly messages
- **Performance optimization** for real-time operations
- **Documentation** for all public APIs

## 📄 License

[Specify your license here - GPL, MIT, or other appropriate license for Blender addons]

## 🎯 Current Development Focus

**Next Session Priorities:**
1. **Complete IK adaptation system** in `ik_adaptation.py`
2. **Implement real-time constraint management** for foot planting
3. **Add root motion detection** with automatic IK updates
4. **Test with rigify characters** and validate foot planting behavior
5. **Integrate with existing layer system** for seamless workflow

**Technical Challenges to Solve:**
- Real-time constraint weight management during root motion
- Automatic space switching between local/world coordinate systems
- Performance optimization for real-time IK updates
- Integration with Blender's constraint system and drivers

**Key Files for Next Development:**
- `ik_adaptation.py`: Core real-time adaptation system
- `operators.py`: Add IK setup and management operators
- `ui.py`: Add IK adaptation controls to existing panels
- `core.py`: Integrate IK adaptation with existing motion analysis

---

*This project aims to bring professional adjustment blending capabilities to the Blender community, democratizing advanced animation techniques pioneered in AAA game studios.*