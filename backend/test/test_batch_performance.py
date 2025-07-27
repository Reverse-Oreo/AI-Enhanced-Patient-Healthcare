#!/usr/bin/env python3
"""
Batch Size Performance Test for LLM Inference
Tests different n_batch and n_ubatch configurations for optimal RTX 3050 performance
"""

import time
import os
import sys
import psutil
import torch
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from adapters.local_model_adapter import LocalModelAdapter

def get_gpu_memory_info():
    """Get current GPU memory usage"""
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated(0) / (1024**3)
        reserved = torch.cuda.memory_reserved(0) / (1024**3)
        total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        return allocated, reserved, total
    return 0, 0, 0

def test_batch_config(n_batch, n_ubatch, test_name):
    """Test a specific batch configuration"""
    print(f"\n🧪 Testing {test_name}")
    print(f"   n_batch: {n_batch}")
    print(f"   n_ubatch: {n_ubatch}")
    
    # Model path
    model_path = os.path.join(backend_dir, "ai_models", "Llama-3.1-8B-UltraMedical.Q8_0.gguf")
    
    if not os.path.exists(model_path):
        print(f"❌ Model not found: {model_path}")
        return None
    
    try:
        # Clear GPU memory before test
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        # Get initial memory
        initial_alloc, initial_reserved, total_memory = get_gpu_memory_info()
        
        # Create adapter with custom batch settings
        adapter = LocalModelAdapter(model_path)
        
        # Temporarily modify settings for this test
        async def custom_load():
            """Load model with custom batch settings"""
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
                "n_batch": n_batch,               # Test parameter
                "n_ubatch": n_ubatch,             # Test parameter
                "offload_kqv": True,
                "flash_attn": True,
                "low_vram": True,
            }
            
            adapter.model = Llama(model_path=adapter.model_path, **settings)
            adapter.optimize_for_inference()
            
            logger.info(f"✅ Model loaded with n_batch={n_batch}, n_ubatch={n_ubatch}")
        
        adapter.load_model = custom_load
        
        # Load model
        import asyncio
        asyncio.run(adapter.load_model())
        
        # Get memory after loading
        loaded_alloc, loaded_reserved, _ = get_gpu_memory_info()
        memory_used = loaded_alloc - initial_alloc
        
        print(f"   GPU Memory Used: {memory_used:.2f}GB")
        print(f"   Total GPU Memory: {loaded_alloc:.2f}GB / {total_memory:.2f}GB")
        
        # Test prompts of different lengths
        test_prompts = [
            "Patient has fever and headache. Diagnose.",  # Short
            "Patient presents with persistent fever of 39°C for 3 days, severe headache, muscle aches, fatigue, and mild nausea. No recent travel. List 3 possible diagnoses.",  # Medium
            "A 45-year-old patient presents to the emergency department with a 5-day history of high-grade fever (39-40°C), severe frontal headache that worsens with movement, neck stiffness, photophobia, nausea, vomiting, and generalized muscle aches. The patient reports no recent travel, no sick contacts, and no known allergies. Vital signs show temperature 39.5°C, heart rate 110 bpm, blood pressure 130/85 mmHg, respiratory rate 22/min. Physical examination reveals positive Kernig's and Brudzinski's signs. Please provide a comprehensive differential diagnosis with the 5 most likely conditions."  # Long
        ]
        
        prompt_names = ["Short", "Medium", "Long"]
        
        all_times = []
        
        for i, (prompt, name) in enumerate(zip(test_prompts, prompt_names)):
            # Warm-up run for first prompt only
            if i == 0:
                asyncio.run(adapter.generate_diagnosis(prompt))
            
            # Performance test - 2 runs per prompt
            times = []
            for run in range(2):
                start_time = time.time()
                result = asyncio.run(adapter.generate_diagnosis(prompt))
                end_time = time.time()
                inference_time = end_time - start_time
                times.append(inference_time)
                
            avg_time = sum(times) / len(times)
            all_times.extend(times)
            print(f"   {name} prompt: {avg_time:.2f}s")
        
        overall_avg = sum(all_times) / len(all_times)
        print(f"   Overall Average: {overall_avg:.2f}s")
        
        # Clean up
        del adapter
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        return {
            'avg_time': overall_avg,
            'memory_used': memory_used,
            'times': all_times
        }
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        return None

def main():
    """Run batch size performance comparison"""
    print("🚀 Batch Size Performance Test for LLM Inference")
    print("=" * 60)
    
    # GPU info
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"🎮 GPU: {gpu_name}")
        print(f"💾 Total GPU Memory: {total_memory:.2f}GB")
    else:
        print("❌ No GPU available")
        return
    
    # Test configurations - optimized for RTX 3050 4GB
    test_configs = [
        (32, 16, "Conservative (32/16)"),
        (64, 32, "Current Settings (64/32)"),
        (128, 32, "Higher Batch (128/32)"),
        (128, 64, "Balanced High (128/64)"),
        (256, 64, "Large Batch (256/64)"),
        (256, 128, "Max Batch (256/128)"),
        (512, 128, "Extreme Batch (512/128)"),  # May fail on 4GB GPU
    ]
    
    results = {}
    
    for n_batch, n_ubatch, name in test_configs:
        result = test_batch_config(n_batch, n_ubatch, name)
        if result:
            results[name] = result
        else:
            print(f"   ⚠️ Configuration failed - likely out of memory")
    
    # Results summary
    print("\n📊 BATCH SIZE PERFORMANCE RESULTS")
    print("=" * 60)
    
    if results:
        # Sort by performance (fastest first)
        sorted_results = sorted(results.items(), key=lambda x: x[1]['avg_time'])
        
        print(f"{'Configuration':<20} | {'Avg Time':<8} | {'Memory':<8} | {'Speedup':<8}")
        print("-" * 60)
        
        best_time = sorted_results[0][1]['avg_time']
        
        for name, data in sorted_results:
            avg_time = data['avg_time']
            memory_used = data['memory_used']
            speedup = best_time / avg_time
            print(f"{name:<20} | {avg_time:6.2f}s | {memory_used:5.2f}GB | {speedup:6.2f}x")
        
        print(f"\n🏆 Best Configuration: {sorted_results[0][0]}")
        print(f"⚡ Performance Range: {best_time:.2f}s - {sorted_results[-1][1]['avg_time']:.2f}s")
        print(f"💾 Memory Range: {min(r[1]['memory_used'] for r in sorted_results):.2f}GB - {max(r[1]['memory_used'] for r in sorted_results):.2f}GB")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        best_config = sorted_results[0]
        print(f"✅ Optimal: {best_config[0]} - Best performance")
        
        # Find memory-efficient option
        memory_efficient = min(results.items(), key=lambda x: x[1]['memory_used'])
        if memory_efficient[0] != best_config[0]:
            print(f"💾 Memory Efficient: {memory_efficient[0]} - Uses only {memory_efficient[1]['memory_used']:.2f}GB")
    
    else:
        print("❌ No successful tests completed")

if __name__ == "__main__":
    main()
