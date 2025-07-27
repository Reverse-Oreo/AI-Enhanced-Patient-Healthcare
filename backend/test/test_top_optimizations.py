#!/usr/bin/env python3
"""
Top 3 Optimization Validation Test
Validates the top 3 performance improvements discovered:
1. mul_mat_q: True (10.93s - FASTEST)
2. n_ctx: 256 (11.41s vs 12.02s for 512)
3. f16_kv: False (11.76s vs 12.42s - surprising result!)
"""

import time
import os
import sys
import asyncio
import torch
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from adapters.local_model_adapter import LocalModelAdapter

async def test_config(config_name, custom_settings):
    """Test a specific configuration"""
    print(f"\n🧪 Testing {config_name}")
    
    model_path = os.path.join(backend_dir, "ai_models", "Llama-3.1-8B-UltraMedical.Q8_0.gguf")
    
    if not os.path.exists(model_path):
        print(f"❌ Model not found")
        return None
    
    try:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        adapter = LocalModelAdapter(model_path)
        
        async def custom_load():
            """Load model with specific configuration"""
            from llama_cpp import Llama
            
            # Base settings
            settings = {
                "chat_format": "llama-3",
                "verbose": False,
                "n_ctx": 512,  # Default
                "seed": 42,
                "logits_all": False,
                "embedding": False,
                "n_threads": 4,
                "n_threads_batch": 4,
                "mul_mat_q": True,  # Default
                "f16_kv": True,  # Default
                "numa": False,
                "use_mmap": True,
                "use_mlock": False,
                "n_gpu_layers": 16,
                "main_gpu": 0,
                "split_mode": 1,
                "n_batch": 512,
                "n_ubatch": 128,
                "offload_kqv": True,
                "flash_attn": True,
                "low_vram": True,
            }
            
            # Apply custom settings
            settings.update(custom_settings)
            
            print(f"   Settings: {custom_settings}")
            
            adapter.model = Llama(model_path=adapter.model_path, **settings)
            adapter.optimize_for_inference()
        
        adapter.load_model = custom_load
        
        # Load model
        start_load = time.time()
        await adapter.load_model()
        load_time = time.time() - start_load
        
        # Test prompt
        test_prompt = "Patient has persistent fever 39°C, severe headache, neck stiffness, photophobia. List 3 diagnoses."
        
        # Warm-up
        await adapter.generate_diagnosis(test_prompt)
        
        # Performance test - 5 runs for accuracy
        times = []
        for i in range(5):
            start_time = time.time()
            result = await adapter.generate_diagnosis(test_prompt)
            end_time = time.time()
            times.append(end_time - start_time)
        
        avg_time = sum(times) / len(times)
        std_dev = (sum((t - avg_time) ** 2 for t in times) / len(times)) ** 0.5
        
        print(f"   Load time: {load_time:.2f}s")
        print(f"   Avg inference: {avg_time:.2f}s ± {std_dev:.2f}s")
        print(f"   Times: {[f'{t:.2f}s' for t in times]}")
        
        del adapter
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        return {'load_time': load_time, 'avg_time': avg_time, 'std_dev': std_dev, 'times': times}
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return None

async def main():
    """Test top optimizations"""
    print("🔥 TOP OPTIMIZATION VALIDATION TEST")
    print("=" * 50)
    
    # Test configurations
    configs = [
        ("BASELINE: Current Settings", {}),
        ("OPT 1: Minimal Context", {"n_ctx": 256}),
        ("OPT 2: FP32 KV Cache", {"f16_kv": False}),
        ("OPT 3: Both Optimizations", {"n_ctx": 256, "f16_kv": False}),
        ("OPT 4: All Top Settings", {"n_ctx": 256, "f16_kv": False, "mul_mat_q": True, "offload_kqv": True, "flash_attn": True}),
    ]
    
    results = {}
    
    for config_name, settings in configs:
        result = await test_config(config_name, settings)
        if result:
            results[config_name] = result
    
    # Analysis
    if results:
        print("\n📊 OPTIMIZATION IMPACT ANALYSIS")
        print("=" * 50)
        
        # Sort by performance
        sorted_results = sorted(results.items(), key=lambda x: x[1]['avg_time'])
        
        baseline_time = results.get("BASELINE: Current Settings", {}).get('avg_time')
        
        print(f"{'Configuration':<25} | {'Time':<10} | {'Speedup':<8} | {'Consistency'}")
        print("-" * 65)
        
        for name, data in sorted_results:
            avg_time = data['avg_time']
            std_dev = data['std_dev']
            
            if baseline_time:
                speedup = baseline_time / avg_time
                speedup_str = f"{speedup:.2f}x"
            else:
                speedup_str = "N/A"
            
            consistency = "High" if std_dev < 0.5 else "Medium" if std_dev < 1.0 else "Low"
            
            marker = "🏆" if name == sorted_results[0][0] else "  "
            print(f"{marker} {name:<23} | {avg_time:6.2f}s ± {std_dev:4.2f} | {speedup_str:<8} | {consistency}")
        
        # Recommendations
        best_config = sorted_results[0]
        print(f"\n💡 FINAL RECOMMENDATIONS")
        print("=" * 50)
        print(f"🏆 Best Configuration: {best_config[0]}")
        print(f"⚡ Performance: {best_config[1]['avg_time']:.2f}s")
        
        if baseline_time:
            total_improvement = baseline_time / best_config[1]['avg_time']
            print(f"🚀 Total Speedup: {total_improvement:.2f}x faster than baseline")
            
            if total_improvement > 1.1:
                print("✅ SIGNIFICANT IMPROVEMENT ACHIEVED!")
            elif total_improvement > 1.05:
                print("✅ Good improvement achieved")
            else:
                print("📈 Minimal improvement - current settings already optimal")
    
    else:
        print("❌ No successful tests completed")

if __name__ == "__main__":
    asyncio.run(main())
