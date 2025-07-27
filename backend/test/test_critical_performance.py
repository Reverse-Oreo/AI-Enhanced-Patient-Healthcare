#!/usr/bin/env python3
"""
Critical Performance Settings Test (Remaining Optimizations)
Tests the 6 remaining most impactful settings for LLM inference performance:
1. f16_kv (KV cache precision) - HIGH IMPACT
2. flash_attn (Flash attention) - HIGH IMPACT  
3. offload_kqv (KV cache GPU offloading) - MEDIUM IMPACT
4. mul_mat_q (Quantized matrix multiplication) - MEDIUM IMPACT
5. n_ctx (Context window size) - HIGH IMPACT
6. use_mmap (Memory mapping) - LOW IMPACT

Note: n_gpu_layers, n_threads, n_batch already optimized
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

def get_gpu_memory_info():
    """Get current GPU memory usage"""
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated(0) / (1024**3)
        reserved = torch.cuda.memory_reserved(0) / (1024**3)
        total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        return allocated, reserved, total
    return 0, 0, 0

async def test_performance_setting(setting_name, setting_value, test_description):
    """Test a specific performance setting"""
    print(f"\n🧪 Testing {test_description}")
    print(f"   {setting_name}: {setting_value}")
    
    model_path = os.path.join(backend_dir, "ai_models", "Llama-3.1-8B-UltraMedical.Q8_0.gguf")
    
    if not os.path.exists(model_path):
        print(f"❌ Model not found")
        return None
    
    try:
        # Clear GPU memory before test
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        initial_alloc, initial_reserved, total_memory = get_gpu_memory_info()
        
        # Create adapter
        adapter = LocalModelAdapter(model_path)
        
        async def custom_load():
            """Load model with custom setting"""
            from llama_cpp import Llama
            
            # Base optimized settings
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
                "n_batch": 512,
                "n_ubatch": 128,
                "offload_kqv": True,
                "flash_attn": True,
                "low_vram": True,
            }
            
            # Override the specific setting being tested
            settings[setting_name] = setting_value
            
            adapter.model = Llama(model_path=adapter.model_path, **settings)
            adapter.optimize_for_inference()
        
        adapter.load_model = custom_load
        
        # Load model
        start_load = time.time()
        await adapter.load_model()
        load_time = time.time() - start_load
        
        # Get memory after loading
        loaded_alloc, loaded_reserved, _ = get_gpu_memory_info()
        memory_used = loaded_alloc - initial_alloc
        
        # Test diagnosis generation
        test_prompt = "Patient has persistent fever 39°C, severe headache, neck stiffness, photophobia. List 3 diagnoses."
        
        # Warm-up
        await adapter.generate_diagnosis(test_prompt)
        
        # Performance test - 3 runs
        times = []
        for i in range(3):
            start_time = time.time()
            result = await adapter.generate_diagnosis(test_prompt)
            end_time = time.time()
            times.append(end_time - start_time)
        
        avg_time = sum(times) / len(times)
        
        print(f"   Load time: {load_time:.2f}s")
        print(f"   Avg inference: {avg_time:.2f}s")
        print(f"   GPU Memory: {memory_used:.2f}GB")
        print(f"   Times: {[f'{t:.2f}s' for t in times]}")
        
        # Clean up
        del adapter
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        return {
            'load_time': load_time,
            'avg_time': avg_time,
            'memory_used': memory_used,
            'times': times
        }
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        return None

async def main():
    """Test critical performance settings"""
    print("🚀 CRITICAL PERFORMANCE SETTINGS TEST")
    print("=" * 60)
    
    # GPU info
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"🎮 GPU: {gpu_name}")
        print(f"💾 Total GPU Memory: {total_memory:.2f}GB")
    
    # Test configurations - 6 remaining critical settings (GPU layers already optimized)
    test_configs = [
        # 1. KV Cache Precision (High Impact)
        ("f16_kv", False, "1. FP32 KV Cache (slower, more memory)"),
        ("f16_kv", True, "1. FP16 KV Cache (faster) - CURRENT"),
        
        # 2. Flash Attention (High Impact)
        ("flash_attn", False, "2. Standard Attention"),
        ("flash_attn", True, "2. Flash Attention (faster) - CURRENT"),
        
        # 3. KV Cache GPU Offloading (Medium Impact)
        ("offload_kqv", False, "3. KV Cache on CPU"),
        ("offload_kqv", True, "3. KV Cache on GPU - CURRENT"),
        
        # 4. Quantized Matrix Multiplication (Medium Impact)
        ("mul_mat_q", False, "4. Standard Matrix Mult"),
        ("mul_mat_q", True, "4. Quantized Matrix Mult - CURRENT"),
        
        # 5. Context Window Size (High Impact for speed vs capability)
        ("n_ctx", 256, "5. Minimal Context (256 tokens)"),
        ("n_ctx", 512, "5. Current Context (512 tokens) - CURRENT"),
        ("n_ctx", 1024, "5. Large Context (1024 tokens)"),
        ("n_ctx", 2048, "5. Max Context (2048 tokens)"),
        
        # 6. Memory Mapping (Medium Impact)
        ("use_mmap", False, "6. No Memory Mapping"),
        ("use_mmap", True, "6. Memory Mapping Enabled - CURRENT"),
    ]
    
    results = {}
    baseline_time = None
    
    for setting_name, setting_value, description in test_configs:
        result = await test_performance_setting(setting_name, setting_value, description)
        if result:
            results[description] = result
            
            # Set baseline (current optimal settings)
            if "CURRENT" in description and baseline_time is None:
                baseline_time = result['avg_time']
    
    # Results analysis
    print("\n📊 PERFORMANCE IMPACT ANALYSIS")
    print("=" * 60)
    
    if results:
        # Group by setting type
        setting_groups = {
            "1. KV Cache Precision": [],
            "2. Flash Attention": [],
            "3. KV Cache Offloading": [],
            "4. Matrix Multiplication": [],
            "5. Context Window": [],
            "6. Memory Mapping": []
        }
        
        for description, data in results.items():
            key = description.split(".")[0] + "."
            for group_key in setting_groups.keys():
                if group_key.startswith(key):
                    setting_groups[group_key].append((description, data))
                    break
        
        # Analyze each setting group
        for group_name, group_results in setting_groups.items():
            if group_results:
                print(f"\n{group_name}")
                print("-" * 40)
                
                # Sort by performance (fastest first)
                sorted_results = sorted(group_results, key=lambda x: x[1]['avg_time'])
                
                best_time = sorted_results[0][1]['avg_time']
                
                for description, data in sorted_results:
                    avg_time = data['avg_time']
                    memory_used = data['memory_used']
                    speedup = best_time / avg_time
                    current_marker = "⭐" if "CURRENT" in description else "  "
                    
                    print(f"{current_marker} {avg_time:6.2f}s | {memory_used:5.2f}GB | {speedup:6.2f}x | {description.split('. ')[1]}")
        
        # Overall recommendations
        print(f"\n💡 OPTIMIZATION RECOMMENDATIONS")
        print("=" * 60)
        
        # Find most impactful settings
        all_results = [(desc, data) for desc, data in results.items()]
        fastest = min(all_results, key=lambda x: x[1]['avg_time'])
        slowest = max(all_results, key=lambda x: x[1]['avg_time'])
        
        max_speedup = slowest[1]['avg_time'] / fastest[1]['avg_time']
        
        print(f"🏆 Fastest Configuration: {fastest[0].split('. ')[1]}")
        print(f"   Time: {fastest[1]['avg_time']:.2f}s")
        print(f"   Memory: {fastest[1]['memory_used']:.2f}GB")
        
        print(f"\n🐌 Slowest Configuration: {slowest[0].split('. ')[1]}")
        print(f"   Time: {slowest[1]['avg_time']:.2f}s")
        print(f"   Memory: {slowest[1]['memory_used']:.2f}GB")
        
        print(f"\n⚡ Maximum Performance Difference: {max_speedup:.1f}x")
        
        # Setting-specific recommendations
        print(f"\n🎯 SETTING PRIORITIES (Impact on Performance):")
        print("1. f16_kv: HIGH - 10-20% improvement + 50% memory savings")
        print("2. flash_attn: HIGH - 10-25% improvement in attention computation")
        print("3. n_ctx: HIGH - 2-5x speed difference (smaller = faster)")
        print("4. offload_kqv: MEDIUM - 5-15% improvement for GPU systems")
        print("5. mul_mat_q: MEDIUM - 5-10% improvement with quantization")
        print("6. use_mmap: LOW - 2-5% improvement + memory efficiency")
    
    else:
        print("❌ No successful tests completed")

if __name__ == "__main__":
    asyncio.run(main())
