#!/usr/bin/env python3
"""
Medical Model Comparison Test
Compares accuracy and performance between Llama3-Med42-8B and Llama-3.1-8B-UltraMedical models
"""

import time
import os
import sys
import asyncio
import json
import torch
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from statistics import mean, stdev

# Add the backend directory to the path
backend_dir = Path(__file__).parent.parent  # Go up one level to reach backend directory
sys.path.insert(0, str(backend_dir))

try:
    from adapters.local_model_adapter import LocalModelAdapter
    from nodes.llm_diagnosis_node import LLMDiagnosisNode
except ImportError as e:
    print(f"⚠️ Could not import modules: {e}")
    print("📁 Current working directory:", os.getcwd())
    print("📁 Backend directory:", backend_dir)
    print("📁 Available files in backend:", list(backend_dir.iterdir()) if backend_dir.exists() else "Directory not found")
    sys.exit(1)

@dataclass
class TestCase:
    """Medical test case with expected diagnosis"""
    symptoms: str
    expected_conditions: List[str]  # Expected possible diagnoses
    severity: str  # "mild", "moderate", "severe"
    category: str  # "infectious", "cardiovascular", "neurological", etc.

@dataclass
class ModelResult:
    """Results for a single model test"""
    model_name: str
    load_time: float
    avg_diagnosis_time: float
    diagnosis_times: List[float]
    accuracy_score: float
    diagnoses: List[Dict]
    memory_usage: float

class MedicalModelComparison:
    def __init__(self):
        self.models = {
            "Llama3-Med42-8B": "ai_models/Llama3-Med42-8B.Q8_0.gguf",
            "Llama-3.1-8B-UltraMedical": "ai_models/Llama-3.1-8B-UltraMedical.Q8_0.gguf"
        }
        
        self.test_cases = [
            TestCase(
                symptoms="Patient presents with severe chest pain radiating to left arm, shortness of breath, sweating, and nausea. Pain started 2 hours ago during physical activity.",
                expected_conditions=["myocardial infarction", "acute coronary syndrome", "unstable angina", "heart attack"],
                severity="severe",
                category="cardiovascular"
            ),
            TestCase(
                symptoms="45-year-old with high fever 39.5°C, severe headache, neck stiffness, photophobia, and positive Kernig's sign. No recent travel history.",
                expected_conditions=["bacterial meningitis", "viral meningitis", "meningitis", "central nervous system infection"],
                severity="severe",
                category="infectious"
            ),
            TestCase(
                symptoms="Patient has persistent dry cough for 3 weeks, weight loss of 5kg, night sweats, and fatigue. No fever currently.",
                expected_conditions=["tuberculosis", "lung cancer", "pneumonia", "bronchitis", "pulmonary infection"],
                severity="moderate",
                category="respiratory"
            ),
            TestCase(
                symptoms="Sudden onset severe headache described as 'worst headache of my life', with nausea, vomiting, and brief loss of consciousness.",
                expected_conditions=["subarachnoid hemorrhage", "intracranial hemorrhage", "stroke", "cerebral aneurysm"],
                severity="severe",
                category="neurological"
            ),
            TestCase(
                symptoms="Patient with polyuria, polydipsia, polyphagia, and unintentional weight loss over 2 months. Random glucose 350 mg/dL.",
                expected_conditions=["diabetes mellitus", "type 1 diabetes", "type 2 diabetes", "diabetic ketoacidosis"],
                severity="moderate",
                category="endocrine"
            ),
            TestCase(
                symptoms="Red, swollen, warm joint in big toe with severe pain that started overnight. Patient has history of alcohol use.",
                expected_conditions=["gout", "gouty arthritis", "uric acid arthropathy", "acute arthritis"],
                severity="mild",
                category="rheumatologic"
            ),
            TestCase(
                symptoms="Crushing substernal chest pain, diaphoresis, dyspnea, and left arm numbness in 65-year-old with diabetes and hypertension.",
                expected_conditions=["myocardial infarction", "heart attack", "acute coronary syndrome", "cardiac event"],
                severity="severe",
                category="cardiovascular"
            ),
            TestCase(
                symptoms="Patient presents with abdominal pain in right lower quadrant, nausea, vomiting, and low-grade fever. Pain migrated from periumbilical area.",
                expected_conditions=["appendicitis", "acute appendicitis", "abdominal inflammation"],
                severity="moderate",
                category="gastrointestinal"
            )
        ]

    def get_gpu_memory_info(self) -> Tuple[float, float, float]:
        """Get current GPU memory usage in GB"""
        if torch.cuda.is_available():
            torch.cuda.synchronize()
            allocated = torch.cuda.memory_allocated(0) / (1024**3)
            reserved = torch.cuda.memory_reserved(0) / (1024**3)
            total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            return allocated, reserved, total
        return 0.0, 0.0, 0.0

    async def load_model_with_optimization(self, model_path: str) -> LocalModelAdapter:
        """Load model with optimized settings"""
        try:
            adapter = LocalModelAdapter(model_path)
            
            # Check if we need to override the load method
            if hasattr(adapter, 'load_model') and callable(getattr(adapter, 'load_model')):
                await adapter.load_model()
            else:
                # Fallback: create a simple load method
                try:
                    from llama_cpp import Llama
                    
                    settings = {
                        "chat_format": "llama-3",
                        "verbose": False,
                        "n_ctx": 512,
                        "seed": 42,
                        "n_threads": 4,
                        "n_gpu_layers": 16 if torch.cuda.is_available() else 0,
                        "use_mmap": True,
                        "use_mlock": False,
                    }
                    
                    adapter.model = Llama(model_path=model_path, **settings)
                except ImportError:
                    print("❌ llama-cpp-python not installed. Please install it: pip install llama-cpp-python")
                    raise
            
            return adapter
        except Exception as e:
            print(f"Error loading model: {e}")
            raise

    def calculate_accuracy_score(self, generated_diagnoses: List[Dict], expected_conditions: List[str]) -> float:
        """Calculate accuracy score based on diagnosis overlap"""
        if not generated_diagnoses:
            return 0.0
        
        # Extract diagnosis text from generated diagnoses
        generated_texts = []
        for diagnosis in generated_diagnoses:
            if isinstance(diagnosis, dict):
                # Try different possible keys for diagnosis text
                text = diagnosis.get('text_diagnosis') or diagnosis.get('diagnosis') or diagnosis.get('condition') or str(diagnosis)
                generated_texts.append(text.lower())
            elif isinstance(diagnosis, str):
                generated_texts.append(diagnosis.lower())
        
        # Check for matches with expected conditions
        matches = 0
        total_expected = len(expected_conditions)
        
        for expected in expected_conditions:
            expected_lower = expected.lower()
            for generated in generated_texts:
                if expected_lower in generated or any(word in generated for word in expected_lower.split()):
                    matches += 1
                    break
        
        return matches / total_expected if total_expected > 0 else 0.0

    async def test_model(self, model_name: str, model_path: str) -> Optional[ModelResult]:
        """Test a single model on all test cases"""
        print(f"\n🧪 Testing {model_name}")
        print("=" * 50)
        
        full_model_path = os.path.join(backend_dir, model_path)
        if not os.path.exists(full_model_path):
            print(f"❌ Model not found: {full_model_path}")
            return None
        
        try:
            # Clear GPU memory
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            initial_alloc, _, total_memory = self.get_gpu_memory_info()
            
            # Load model
            print(f"Loading {model_name}...")
            start_load = time.time()
            adapter = await self.load_model_with_optimization(full_model_path)
            load_time = time.time() - start_load
            
            loaded_alloc, _, _ = self.get_gpu_memory_info()
            memory_usage = loaded_alloc - initial_alloc
            
            print(f"✅ Model loaded in {load_time:.2f}s")
            print(f"💾 Memory usage: {memory_usage:.2f}GB")
            
            try:
                diagnosis_node = LLMDiagnosisNode(adapter)
            except Exception as e:
                print(f"⚠️ Error creating diagnosis node: {e}")
                print("📝 Creating simple test interface...")
                diagnosis_node = None
            
            # Test all cases
            diagnosis_times = []
            accuracy_scores = []
            all_diagnoses = []
            
            for i, test_case in enumerate(self.test_cases, 1):
                print(f"\n--- Test Case {i}/{len(self.test_cases)} ({test_case.category}) ---")
                print(f"Symptoms: {test_case.symptoms[:100]}...")
                
                try:
                    # Actual test
                    start_time = time.time()
                    
                    if diagnosis_node:
                        state = {"latest_user_message": test_case.symptoms}
                        result = await diagnosis_node(state)
                        diagnoses = result.get('textual_analysis', [])
                    else:
                        # Fallback: direct model query
                        prompt = f"Given these symptoms: {test_case.symptoms}\n\nProvide possible medical diagnoses:"
                        response = adapter.model.create_completion(
                            prompt=prompt,
                            max_tokens=200,
                            temperature=0.3,
                            stop=["Human:", "Assistant:"]
                        )
                        diagnoses = [{"text_diagnosis": response['choices'][0]['text'].strip()}]
                    
                    end_time = time.time()
                    diagnosis_time = end_time - start_time
                    diagnosis_times.append(diagnosis_time)
                    all_diagnoses.append(diagnoses)
                    
                    # Calculate accuracy
                    accuracy = self.calculate_accuracy_score(diagnoses, test_case.expected_conditions)
                    accuracy_scores.append(accuracy)
                    
                    print(f"⏱️  Time: {diagnosis_time:.2f}s")
                    print(f"🎯 Accuracy: {accuracy:.2f}")
                    print(f"📊 Diagnoses count: {len(diagnoses)}")
                    
                    if diagnoses:
                        for j, diagnosis in enumerate(diagnoses[:2], 1):  # Show top 2
                            if isinstance(diagnosis, dict):
                                text = diagnosis.get('text_diagnosis', diagnosis.get('diagnosis', 'N/A'))
                                confidence = diagnosis.get('diagnosis_confidence', diagnosis.get('confidence', 'N/A'))
                                print(f"   {j}. {text} (confidence: {confidence})")
                    
                except Exception as e:
                    print(f"❌ Error in test case {i}: {e}")
                    diagnosis_times.append(0.0)
                    accuracy_scores.append(0.0)
                    all_diagnoses.append([])
            
            avg_diagnosis_time = mean(diagnosis_times) if diagnosis_times else 0.0
            avg_accuracy = mean(accuracy_scores) if accuracy_scores else 0.0
            
            print(f"\n📈 {model_name} Summary:")
            print(f"   Load time: {load_time:.2f}s")
            print(f"   Avg diagnosis time: {avg_diagnosis_time:.2f}s")
            print(f"   Overall accuracy: {avg_accuracy:.2f}")
            print(f"   Memory usage: {memory_usage:.2f}GB")
            
            # Cleanup
            del adapter
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            return ModelResult(
                model_name=model_name,
                load_time=load_time,
                avg_diagnosis_time=avg_diagnosis_time,
                diagnosis_times=diagnosis_times,
                accuracy_score=avg_accuracy,
                diagnoses=all_diagnoses,
                memory_usage=memory_usage
            )
            
        except Exception as e:
            print(f"❌ Error testing {model_name}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def print_detailed_comparison(self, results: Dict[str, ModelResult]):
        """Print detailed comparison results"""
        print("\n" + "="*80)
        print("🏆 DETAILED MODEL COMPARISON RESULTS")
        print("="*80)
        
        models = list(results.keys())
        if len(models) != 2:
            print("❌ Need exactly 2 models for comparison")
            return
        
        model1, model2 = models
        result1, result2 = results[model1], results[model2]
        
        # Performance Comparison
        print(f"\n⚡ PERFORMANCE METRICS")
        print(f"{'Metric':<25} | {model1:<20} | {model2:<20} | {'Winner':<15}")
        print("-" * 85)
        
        # Load time
        load_winner = model1 if result1.load_time < result2.load_time else model2
        load_speedup = max(result1.load_time, result2.load_time) / min(result1.load_time, result2.load_time)
        print(f"{'Load Time':<25} | {result1.load_time:<18.2f}s | {result2.load_time:<18.2f}s | {load_winner:<15}")
        
        # Diagnosis time
        diag_winner = model1 if result1.avg_diagnosis_time < result2.avg_diagnosis_time else model2
        diag_speedup = max(result1.avg_diagnosis_time, result2.avg_diagnosis_time) / min(result1.avg_diagnosis_time, result2.avg_diagnosis_time)
        print(f"{'Avg Diagnosis Time':<25} | {result1.avg_diagnosis_time:<18.2f}s | {result2.avg_diagnosis_time:<18.2f}s | {diag_winner:<15}")
        
        # Memory usage
        mem_winner = model1 if result1.memory_usage < result2.memory_usage else model2
        print(f"{'Memory Usage':<25} | {result1.memory_usage:<18.2f}GB | {result2.memory_usage:<18.2f}GB | {mem_winner:<15}")
        
        # Accuracy Comparison
        print(f"\n🎯 ACCURACY METRICS")
        print(f"{'Metric':<25} | {model1:<20} | {model2:<20} | {'Winner':<15}")
        print("-" * 85)
        
        acc_winner = model1 if result1.accuracy_score > result2.accuracy_score else model2
        acc_diff = abs(result1.accuracy_score - result2.accuracy_score)
        print(f"{'Overall Accuracy':<25} | {result1.accuracy_score:<18.2f} | {result2.accuracy_score:<18.2f} | {acc_winner:<15}")
        
        # Category-wise accuracy
        print(f"\n📊 CATEGORY-WISE ACCURACY")
        categories = {}
        for i, test_case in enumerate(self.test_cases):
            cat = test_case.category
            if cat not in categories:
                categories[cat] = []
            
            acc1 = self.calculate_accuracy_score(result1.diagnoses[i], test_case.expected_conditions)
            acc2 = self.calculate_accuracy_score(result2.diagnoses[i], test_case.expected_conditions)
            categories[cat].append((acc1, acc2))
        
        print(f"{'Category':<20} | {model1:<15} | {model2:<15} | {'Winner':<15}")
        print("-" * 70)
        
        for category, scores in categories.items():
            avg1 = mean([s[0] for s in scores])
            avg2 = mean([s[1] for s in scores])
            winner = model1 if avg1 > avg2 else model2
            print(f"{category:<20} | {avg1:<15.2f} | {avg2:<15.2f} | {winner:<15}")
        
        # Overall Recommendations
        print(f"\n💡 RECOMMENDATIONS")
        print("-" * 50)
        
        if result1.accuracy_score > result2.accuracy_score + 0.1:
            print(f"🎯 For Accuracy: {model1} (+{acc_diff:.2f} better)")
        elif result2.accuracy_score > result1.accuracy_score + 0.1:
            print(f"🎯 For Accuracy: {model2} (+{acc_diff:.2f} better)")
        else:
            print(f"🎯 For Accuracy: Similar performance (±{acc_diff:.2f})")
        
        if result1.avg_diagnosis_time < result2.avg_diagnosis_time:
            print(f"⚡ For Speed: {model1} ({diag_speedup:.2f}x faster)")
        else:
            print(f"⚡ For Speed: {model2} ({diag_speedup:.2f}x faster)")
        
        if result1.memory_usage < result2.memory_usage:
            print(f"💾 For Memory: {model1} ({result2.memory_usage - result1.memory_usage:.2f}GB less)")
        else:
            print(f"💾 For Memory: {model2} ({result1.memory_usage - result2.memory_usage:.2f}GB less)")
        
        # Best overall choice
        score1 = result1.accuracy_score * 2 + (1/result1.avg_diagnosis_time) * 0.5 + (1/result1.memory_usage) * 0.3
        score2 = result2.accuracy_score * 2 + (1/result2.avg_diagnosis_time) * 0.5 + (1/result2.memory_usage) * 0.3
        
        overall_winner = model1 if score1 > score2 else model2
        print(f"\n🏆 OVERALL WINNER: {overall_winner}")
        print(f"   (Balanced score considering accuracy, speed, and memory efficiency)")

async def main():
    """Run the medical model comparison"""
    print("🏥 MEDICAL MODEL ACCURACY & PERFORMANCE COMPARISON")
    print("=" * 60)
    
    # Check dependencies
    try:
        import llama_cpp
        print("✅ llama-cpp-python is available")
    except ImportError:
        print("❌ llama-cpp-python not found. Install with: pip install llama-cpp-python")
        return
    
    # GPU info
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"🎮 GPU: {gpu_name}")
        print(f"💾 Total GPU Memory: {total_memory:.2f}GB")
    else:
        print("❌ No GPU available - tests will run on CPU")
    
    comparison = MedicalModelComparison()
    results = {}
    
    # Test each model
    for model_name, model_path in comparison.models.items():
        result = await comparison.test_model(model_name, model_path)
        if result:
            results[model_name] = result
        else:
            print(f"⚠️ Failed to test {model_name}")
    
    # Print comparison if we have results
    if len(results) >= 2:
        comparison.print_detailed_comparison(results)
    elif len(results) == 1:
        print(f"\n⚠️ Only one model tested successfully: {list(results.keys())[0]}")
    else:
        print(f"\n❌ No models tested successfully")
    
    print(f"\n✅ Comparison complete!")

if __name__ == "__main__":
    asyncio.run(main())