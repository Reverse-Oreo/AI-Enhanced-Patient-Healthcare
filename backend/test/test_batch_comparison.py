#!/usr/bin/env python3
"""
Before/After Batch Optimization Comparison Test
Compares old (64/32) vs new (512/128) batch settings
"""

import time
import os
import sys
import asyncio
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from adapters.local_model_adapter import LocalModelAdapter

async def test_batch_settings(n_batch, n_ubatch, config_name):
    """Test specific batch configuration"""
    print(f"\n🧪 Testing {config_name}")
    print(f"   n_batch: {n_batch}, n_ubatch: {n_ubatch}")
    
    model_path = os.path.join(backend_dir, "ai_models", "Llama-3.1-8B-UltraMedical.Q8_0.gguf")
    
    if not os.path.exists(model_path):
        print(f"❌ Model not found")
        return None
    
    try:
        # Create adapter
        adapter = LocalModelAdapter(model_path)
        
        # Temporarily override batch settings
        original_load = adapter.load_model
        
        async def custom_load():
            from llama_cpp import Llama
            import logging
            
            settings = {
                "chat_format": "llama-3",
                "verbose": False,
                "n_ctx": 512,
                "seed": 42,
                "logits_all": False,
                "embedding": False,
                "n_threads": 4,
                "n_threads_batch": 4,
                "mul_mat_q": True,
                "f16_kv": True,
                "numa": False,
                "use_mmap": True,
                "use_mlock": False,
                "n_gpu_layers": 16,
                "main_gpu": 0,
                "split_mode": 1,
                "n_batch": n_batch,
                "n_ubatch": n_ubatch,
                "offload_kqv": True,
                "flash_attn": True,
                "low_vram": True,
            }
            
            adapter.model = Llama(model_path=adapter.model_path, **settings)
            adapter.optimize_for_inference()
        
        adapter.load_model = custom_load
        
        # Load model
        start_load = time.time()
        await adapter.load_model()
        load_time = time.time() - start_load
        
        # Test diagnosis generation
        test_prompt = "Patient has persistent fever 39°C, severe headache, neck stiffness, photophobia. Urgent evaluation needed."
        
        # Warm-up
        await adapter.generate_diagnosis(test_prompt)
        
        # Performance test
        times = []
        for i in range(3):
            start_time = time.time()
            result = await adapter.generate_diagnosis(test_prompt)
            end_time = time.time()
            times.append(end_time - start_time)
        
        avg_time = sum(times) / len(times)
        
        print(f"   Load time: {load_time:.2f}s")
        print(f"   Avg diagnosis: {avg_time:.2f}s")
        print(f"   Times: {[f'{t:.2f}s' for t in times]}")
        
        del adapter
        return {'load_time': load_time, 'avg_time': avg_time, 'times': times}
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return None

async def main():
    """Compare old vs new batch configurations"""
    print("🔄 BATCH OPTIMIZATION COMPARISON")
    print("=" * 50)
    
    # Test configurations
    configs = [
        (64, 32, "OLD: Current Settings (64/32)"),
        (512, 128, "NEW: Optimized Settings (512/128)")
    ]
    
    results = {}
    
    for n_batch, n_ubatch, name in configs:
        result = await test_batch_settings(n_batch, n_ubatch, name)
        if result:
            results[name] = result
    
    # Comparison results
    if len(results) == 2:
        print("\n📊 PERFORMANCE COMPARISON")
        print("=" * 50)
        
        old_key = "OLD: Current Settings (64/32)"
        new_key = "NEW: Optimized Settings (512/128)"
        
        old_data = results[old_key]
        new_data = results[new_key]
        
        load_improvement = old_data['load_time'] / new_data['load_time']
        diagnosis_improvement = old_data['avg_time'] / new_data['avg_time']
        
        print(f"Load Time:")
        print(f"  Old (64/32):  {old_data['load_time']:.2f}s")
        print(f"  New (512/128): {new_data['load_time']:.2f}s")
        print(f"  Improvement: {load_improvement:.2f}x faster")
        
        print(f"\nDiagnosis Time:")
        print(f"  Old (64/32):  {old_data['avg_time']:.2f}s")
        print(f"  New (512/128): {new_data['avg_time']:.2f}s")
        print(f"  Improvement: {diagnosis_improvement:.2f}x faster")
        
        overall_improvement = (old_data['avg_time'] + old_data['load_time']) / (new_data['avg_time'] + new_data['load_time'])
        print(f"\nOverall Performance: {overall_improvement:.2f}x faster")
        
        if diagnosis_improvement > 1.1:
            print(f"\n🎉 SIGNIFICANT IMPROVEMENT!")
            print(f"⚡ Batch optimization provides {diagnosis_improvement:.1f}x speedup")
        elif diagnosis_improvement > 1.05:
            print(f"\n✅ Good improvement: {diagnosis_improvement:.1f}x speedup")
        else:
            print(f"\n📈 Minimal improvement: {diagnosis_improvement:.1f}x speedup")
    
    else:
        print("❌ Could not complete comparison - missing results")

if __name__ == "__main__":
    asyncio.run(main())
