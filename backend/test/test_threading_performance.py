#!/usr/bin/env python3
"""
Threading Performance Test for LLM Inference
Tests different thread configurations to find optimal settings
"""

import time
import os
import sys
import psutil
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from adapters.local_model_adapter import LocalModelAdapter

def test_threading_config(n_threads, n_threads_batch, test_name):
    """Test a specific threading configuration"""
    print(f"\n🧪 Testing {test_name}")
    print(f"   n_threads: {n_threads}")
    print(f"   n_threads_batch: {n_threads_batch}")
    
    # Model path
    model_path = os.path.join(backend_dir, "ai_models", "Llama-3.1-8B-UltraMedical.Q8_0.gguf")
    
    if not os.path.exists(model_path):
        print(f"❌ Model not found: {model_path}")
        return None
    
    try:
        # Create adapter with custom threading
        adapter = LocalModelAdapter(model_path)
        
        # Temporarily modify settings for this test
        original_load = adapter.load_model
        
        async def custom_load():
            """Load model with custom threading settings"""
            from llama_cpp import Llama
            import logging
            
            logger = logging.getLogger(__name__)
            
            # Custom settings for this test
            settings = {
                "chat_format": "llama-3",
                "verbose": False,
                "n_ctx": 384,
                "seed": 42,
                "logits_all": False,
                "embedding": False,
                "n_threads": n_threads,
                "n_threads_batch": n_threads_batch,
                "mul_mat_q": True,
                "f16_kv": True,
                "numa": False,
                "use_mmap": True,
                "use_mlock": False,
                "n_gpu_layers": 16,
                "main_gpu": 0,
                "split_mode": 1,
                "n_batch": 64,
                "n_ubatch": 32,
                "offload_kqv": True,
                "flash_attn": True,
                "low_vram": True,
            }
            
            adapter.model = Llama(model_path=adapter.model_path, **settings)
            adapter.optimize_for_inference()
            
            logger.info(f"✅ Model loaded with n_threads={n_threads}, n_threads_batch={n_threads_batch}")
        
        adapter.load_model = custom_load
        
        # Load model
        import asyncio
        asyncio.run(adapter.load_model())
        
        # Test prompt
        test_prompt = "Patient has fever, headache, and muscle aches for 3 days. List 3 possible diagnoses."
        
        # Warm-up run
        asyncio.run(adapter.generate_diagnosis(test_prompt))
        
        # Performance test - 3 runs
        times = []
        for i in range(3):
            start_time = time.time()
            result = asyncio.run(adapter.generate_diagnosis(test_prompt))
            end_time = time.time()
            inference_time = end_time - start_time
            times.append(inference_time)
            print(f"   Run {i+1}: {inference_time:.2f}s")
        
        avg_time = sum(times) / len(times)
        print(f"   Average: {avg_time:.2f}s")
        
        # Clean up
        del adapter
        
        return avg_time
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None

def main():
    """Run threading performance comparison"""
    print("🚀 Threading Performance Test for LLM Inference")
    print("=" * 50)
    
    # System info
    physical_cores = psutil.cpu_count(logical=False)
    logical_cores = psutil.cpu_count(logical=True)
    
    print(f"💻 System Info:")
    print(f"   Physical cores: {physical_cores}")
    print(f"   Logical cores: {logical_cores}")
    
    # Test configurations
    test_configs = [
        (None, None, "Auto-detect (Default)"),
        (1, 1, "Minimal Threading"),
        (4, 4, "Conservative Threading"), 
        (6, 8, "Optimized Threading"),
        (physical_cores, logical_cores, "Max Physical/Logical"),
        (logical_cores, logical_cores, "Max Logical Both"),
    ]
    
    results = {}
    
    for n_threads, n_threads_batch, name in test_configs:
        result = test_threading_config(n_threads, n_threads_batch, name)
        if result:
            results[name] = result
    
    # Results summary
    print("\n📊 THREADING PERFORMANCE RESULTS")
    print("=" * 50)
    
    if results:
        # Sort by performance (fastest first)
        sorted_results = sorted(results.items(), key=lambda x: x[1])
        
        best_time = sorted_results[0][1]
        
        for name, avg_time in sorted_results:
            speedup = best_time / avg_time
            print(f"{name:20} | {avg_time:6.2f}s | {speedup:4.2f}x")
        
        print(f"\n🏆 Best Configuration: {sorted_results[0][0]}")
        print(f"⚡ Performance Improvement: {best_time / sorted_results[-1][1]:.2f}x faster than worst")
    
    else:
        print("❌ No successful tests completed")

if __name__ == "__main__":
    main()
