import asyncio
from adapters.local_model_adapter import LocalModelAdapter
from nodes.llm_diagnosis_node import LLMDiagnosisNode

##Test input 
# A new growth on the skin that might look like a mole, a bump or a scab.
# I have a headache and nausea. I also feel very tired and have a slight fever.

async def simple_diagnosis_test():
    print("🏥 Medical Diagnosis Chatbot Test")
    print("=" * 50)
    
    # Initialize
    print("Loading model...")
    adapter = LocalModelAdapter(llm_path="ai_models/Llama-3.1-8B-UltraMedical.Q8_0.gguf")
    await adapter.load_model()
    print("✅ Model loaded!\n")
    
    diagnosis_node = LLMDiagnosisNode(adapter)
    
    # Predefined test symptoms
    test_symptoms = [
        "I have a headache and nausea. I also feel very tired and have a slight fever.",
        "A new growth on the skin that might look like a mole, a bump or a scab.",
        "I have chest pain and difficulty breathing.",
        "There's a rash on my arm that's been itching for days.",
        "I feel dizzy and have been vomiting since this morning."
    ]
    
    print("🔍 Testing with predefined symptoms:\n")
    
    for i, symptoms in enumerate(test_symptoms, 1):
        print(f"--- Test {i} ---")
        print(f"🗣️ Patient: {symptoms}")
        
        # Create state
        state = {"latest_user_message": symptoms}
        
        # Get diagnosis
        result = await diagnosis_node(state)
        
        # Display results
        image_required = result.get("image_required", False)
        diagnoses = result.get("textual_analysis", [])
        
        print(f"📸 Image Required: {'Yes' if image_required else 'No'}")
        print(f"🏥 Number of Diagnoses: {len(diagnoses)}")
        
        if diagnoses:
            print("📋 Diagnoses:")
            for j, diagnosis in enumerate(diagnoses, 1):
                name = diagnosis.get('text_diagnosis', 'Unknown')
                confidence = diagnosis.get('diagnosis_confidence', 0)
                
                print(f"   {j}. {name}")
                print(f"      📊 Confidence: {confidence}")
        else:
            print("❌ No diagnoses found")
        
        print("\n" + "="*50 + "\n")

async def interactive_diagnosis_test():
    print("🏥 Interactive Medical Diagnosis Chatbot")
    print("=" * 50)
    print("Type your symptoms (or 'quit' to exit)")
    
    # Initialize
    print("\nLoading model...")
    adapter = LocalModelAdapter(llm_path="ai_models/Llama-3.1-8B-UltraMedical.Q8_0.gguf")
    await adapter.load_model()
    print("✅ Model ready!\n")
    
    diagnosis_node = LLMDiagnosisNode(adapter)
    
    while True:
        # Get user input
        user_input = input("🗣️ Describe your symptoms: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye! Take care of your health!")
            break
        
        if not user_input:
            print("❌ Please describe your symptoms.\n")
            continue
        
        try:
            # Process symptoms
            print("🔍 Analyzing symptoms...")
            state = {"latest_user_message": user_input}
            result = await diagnosis_node(state)
            
            # Display results
            image_required = result.get("image_required", False)
            diagnoses = result.get("textual_analysis", [])
            
            print(f"\n📸 Image Required: {'Yes' if image_required else 'No'}")
            if image_required:
                print("📸 Note: Visual examination may be needed for accurate diagnosis.")
            else:
                print(f"🏥 Found {len(diagnoses)} possible diagnoses:\n")
                
                for i, diagnosis in enumerate(diagnoses, 1):
                    name = diagnosis.get('text_diagnosis', 'Unknown')
                    confidence = diagnosis.get('diagnosis_confidence', 0)
                    
                    print(f"   {i}. 🏷️ {name}")
                    print(f"      📊 Confidence: {confidence:.1f}/1.0")
                    print()
                
                if not diagnoses:
                    print("❌ Could not generate diagnoses. Please try describing symptoms differently.")
            
            print("=" * 50 + "\n")
            
        except Exception as e:
            print(f"❌ Error occurred: {e}")
            print("Please try again with different symptoms.\n")

async def quick_test():
    """Quick single test"""
    print("🏥 Quick Diagnosis Test")
    print("=" * 30)
    
    adapter = LocalModelAdapter(llm_path="ai_models/Llama-3.1-8B-UltraMedical.Q8_0.gguf")
    await adapter.load_model()
    diagnosis_node = LLMDiagnosisNode(adapter)
    
    # Test one symptom
    symptoms = "I have a severe headache and feel nauseous"
    print(f"🗣️ Testing: {symptoms}")
    
    state = {"latest_user_message": symptoms}
    result = await diagnosis_node(state)
    
    print(f"📸 Image Required: {result.get('image_required', False)}")
    print(f"🏥 Diagnoses Count: {len(result.get('textual_analysis', []))}")
    
    for diagnosis in result.get('textual_analysis', []):
        print(f"   - {diagnosis.get('text_diagnosis')} (confidence: {diagnosis.get('diagnosis_confidence')})")

def main():
    """Choose test mode"""
    print("Choose test mode:")
    print("1. Predefined symptoms test")
    print("2. Interactive chatbot")
    print("3. Quick test")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        asyncio.run(simple_diagnosis_test())
    elif choice == "2":
        asyncio.run(interactive_diagnosis_test())
    elif choice == "3":
        asyncio.run(quick_test())
    else:
        print("Invalid choice. Running quick test...")
        asyncio.run(quick_test())

if __name__ == "__main__":
    main()