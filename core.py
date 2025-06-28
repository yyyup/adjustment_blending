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