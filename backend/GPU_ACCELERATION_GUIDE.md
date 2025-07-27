# GPU Acceleration Guide: From CPU to cuBLAS GPU Inference

## 🎯 **Project Overview**
Complete transformation of the AI Medical Assistant from CPU-only inference to GPU-accelerated performance using NVIDIA cuBLAS on RTX 3050 Laptop GPU.

---

## 📊 **Performance Results**

### Before (CPU Only)
- **Generation Time**: 9.72s baseline
- **Load Time**: 6.78s 
- **Framework**: Basic llama-cpp-python

### After (GPU Accelerated)
- **Generation Time**: 4.45s (**2.2x faster**)
- **Load Time**: 7.54s (similar)
- **Framework**: llama-cpp-python + cuBLAS
- **GPU Layers**: 16 optimal layers
- **Speedup**: **1.8x-2.2x performance improvement**

---

## 🔧 **System Requirements**

### Hardware
- **GPU**: NVIDIA GeForce RTX 3050 Laptop GPU (4GB VRAM)
- **CPU**: AMD Ryzen 7 5800H (8 cores)
- **RAM**: 16GB DDR4
- **Storage**: SSD recommended for model loading

### Software Prerequisites
- **Windows 10/11**
- **Python 3.11**
- **CUDA 12.5 or 12.9**
- **Visual Studio Build Tools 2019/2022**
- **CMake 3.24+**
- **Git**

## ⏱️ **Complete Installation Timeline & Progress Tracker**

### Phase Overview (Total Time: 45-60 minutes)
```
Phase 1: Environment Setup        [10-15 min] ████████░░
Phase 2: Framework Evaluation     [5 min]     ███░░░░░░░
Phase 3: Build Preparation        [5-10 min]  ████░░░░░░
Phase 4: Compilation              [30-45 min] ██████████
Phase 5: Verification            [5-10 min]  ████░░░░░░
```

### Detailed Progress Checklist

#### � **Phase 1: Environment Setup & Analysis** (10-15 minutes)
- [ ] **Step 1.1**: System Assessment (2 min)
  - [ ] Check CUDA version: `nvcc --version`
  - [ ] Verify GPU: `nvidia-smi`
  - [ ] Python version: `python --version`
  - [ ] ✅ Expected: CUDA 12.x, RTX 3050, Python 3.11

- [ ] **Step 1.2**: NumPy Compatibility (2 min)
  - [ ] Check current version: `python -c "import numpy; print(numpy.__version__)"`
  - [ ] Downgrade if needed: `pip install "numpy<2.0.0"`
  - [ ] ✅ Expected: NumPy 1.26.x

- [ ] **Step 1.3**: CUDA Environment (1 min)
  - [ ] Verify PyTorch CUDA: `python -c "import torch; print(torch.cuda.is_available())"`
  - [ ] Check GPU memory: `python -c "import torch; print(torch.cuda.get_device_properties(0))"`
  - [ ] ✅ Expected: True, RTX 3050 with 4GB

#### 📋 **Phase 2: Framework Evaluation** (5 minutes)
- [ ] **Step 2.1**: Document failed attempts (1 min)
  - [ ] ❌ vLLM: Windows incompatibility
  - [ ] ❌ ExLlamaV2: Model format issues
  - [ ] ❌ Pre-built cuBLAS: CPU-only wheels

- [ ] **Step 2.2**: Select llama-cpp-python (1 min)
  - [ ] ✅ Windows compatible
  - [ ] ✅ GGUF format support
  - [ ] ✅ Manual compilation possible

#### 📋 **Phase 3: Build Environment Preparation** (5-10 minutes)
- [ ] **Step 3.1**: Visual Studio Build Tools (5-8 min)
  - [ ] Check existing: `Get-WmiObject -Class Win32_Product | Where-Object {$_.Name -like "*Visual Studio*"}`
  - [ ] Install if needed: `winget install Microsoft.VisualStudio.2022.BuildTools`
  - [ ] Verify compiler: `where cl`
  - [ ] ✅ Expected: Microsoft C/C++ compiler found

- [ ] **Step 3.2**: CMake Installation (2-3 min)
  - [ ] Check version: `cmake --version`
  - [ ] Install/update: `winget install Kitware.CMake`
  - [ ] Add to PATH: `$env:PATH += ";C:\Program Files\CMake\bin"`
  - [ ] ✅ Expected: CMake 3.24+

- [ ] **Step 3.3**: Git Verification (1 min)
  - [ ] Check: `git --version`
  - [ ] Install if needed: `winget install Git.Git`
  - [ ] ✅ Expected: Git available

#### 📋 **Phase 4: CUDA & Build Setup** (2-5 minutes)
- [ ] **Step 4.1**: CUDA Paths (2 min)
  - [ ] Set CUDA_PATH: `$env:CUDA_PATH = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.5"`
  - [ ] Set build flags: `$env:CMAKE_ARGS = "-DGGML_CUDA=on"`
  - [ ] Verify: `echo $env:CUDA_PATH`
  - [ ] ✅ Expected: Valid CUDA path shown

- [ ] **Step 4.2**: Pre-build Cleanup (1 min)
  - [ ] Remove existing: `pip uninstall llama-cpp-python -y`
  - [ ] Clear cache: `pip cache purge`
  - [ ] Verify clean: `pip list | Select-String "llama"`
  - [ ] ✅ Expected: No llama packages listed

#### 📋 **Phase 5: Manual Compilation** (30-45 minutes)
- [ ] **Step 5.1**: Start Build Process (1 min)
  ```powershell
  $env:CMAKE_ARGS = "-DGGML_CUDA=on"
  pip install llama-cpp-python --no-cache-dir --force-reinstall --no-binary=llama-cpp-python --verbose
  ```

- [ ] **Step 5.2**: Monitor Build Progress (30-40 min)
  - [ ] **Phase A**: Source Download (2-3 min)
    - [ ] Downloading source package
    - [ ] Extracting files
    - [ ] ✅ Expected: "Preparing metadata"

  - [ ] **Phase B**: CMake Configuration (3-5 min)
    - [ ] Running CMake setup
    - [ ] CUDA detection
    - [ ] ✅ Expected: "Found CUDA", "GGML_CUDA: ON"

  - [ ] **Phase C**: Compilation (25-35 min)
    - [ ] Building C++ objects: [  5%] → [ 25%]
    - [ ] Building CUDA kernels: [ 25%] → [ 50%]
    - [ ] Linking libraries: [ 50%] → [ 75%]
    - [ ] Python bindings: [ 75%] → [100%]
    - [ ] ✅ Expected: "Built target llama-cpp-python"

  - [ ] **Phase D**: Wheel Creation (2-3 min)
    - [ ] Packaging wheel
    - [ ] Installing package
    - [ ] ✅ Expected: "Successfully installed llama-cpp-python"

#### 📋 **Phase 6: Build Verification** (5 minutes)
- [ ] **Step 6.1**: Installation Check (1 min)
  - [ ] Verify package: `pip list | Select-String "llama"`
  - [ ] Check wheel size: Should be ~445MB
  - [ ] Import test: `python -c "from llama_cpp import Llama; print('✅ Success')"`
  - [ ] ✅ Expected: No import errors

- [ ] **Step 6.2**: CUDA Detection Test (2 min)
  ```python
  from llama_cpp import Llama
  llm = Llama(
      model_path="backend/ai_models/Llama-3.1-8B-UltraMedical.Q8_0.gguf",
      n_gpu_layers=1,
      n_ctx=128,
      verbose=True
  )
  ```
  - [ ] ✅ Expected: "ggml_cuda_init: found 1 CUDA devices"
  - [ ] ✅ Expected: "layer 31 assigned to device CUDA0"

- [ ] **Step 6.3**: Performance Baseline (2 min)
  - [ ] CPU test: 0 GPU layers
  - [ ] GPU test: 16 GPU layers
  - [ ] Compare times
  - [ ] ✅ Expected: GPU 1.5x+ faster than CPU

#### 📋 **Phase 7: Optimization & Integration** (5-10 minutes)
- [ ] **Step 7.1**: Optimal Configuration (3 min)
  - [ ] Test different GPU layer counts
  - [ ] Find optimal settings for RTX 3050
  - [ ] ✅ Expected: 16 layers optimal

- [ ] **Step 7.2**: LocalModelAdapter Integration (5 min)
  - [ ] Update adapter settings
  - [ ] Test diagnosis generation
  - [ ] Test follow-up questions
  - [ ] ✅ Expected: Sub-5s generation times

### 🚨 **Troubleshooting Checkpoints**

#### Checkpoint 1: After CMake Configuration
**If build fails here**:
- Check CUDA path: `echo $env:CUDA_PATH`
- Verify CMake: `cmake --version`
- Check compiler: `where cl`

#### Checkpoint 2: During Compilation
**If build stops/fails**:
- Check RAM usage (need 4GB+ free)
- Reduce parallel jobs: `$env:CMAKE_ARGS = "-DGGML_CUDA=on -DCMAKE_BUILD_PARALLEL_LEVEL=2"`
- Close unnecessary applications

#### Checkpoint 3: After Installation
**If import fails**:
- Check wheel size (should be ~445MB)
- Verify Python path
- Test basic import: `python -c "import llama_cpp"`

#### Checkpoint 4: GPU Detection
**If CUDA not detected**:
- Verify verbose output shows GPU messages
- Check layer assignment to CUDA device
- Test with minimal GPU layers (n_gpu_layers=1)

### 📊 **Progress Tracking Template**

```
Installation started: [DATE/TIME]

✅ Phase 1 Complete: [TIME] - Environment verified
✅ Phase 2 Complete: [TIME] - Framework selected  
✅ Phase 3 Complete: [TIME] - Build tools ready
✅ Phase 4 Complete: [TIME] - CUDA environment set
✅ Phase 5 Complete: [TIME] - Compilation successful
✅ Phase 6 Complete: [TIME] - GPU acceleration verified
✅ Phase 7 Complete: [TIME] - Integration complete

Total Time: [DURATION]
Final Performance: [X.XX]s generation (vs [Y.YY]s baseline)
Speedup Achieved: [Z.Z]x faster

Notes:
- Any issues encountered: ________________
- Specific optimizations: ________________
- Final GPU layers used: ________________
```

### 🎯 **Success Criteria Validation**

**✅ Installation Success Indicators**:
- [ ] Build time: 30+ minutes (indicates full compilation)
- [ ] Wheel size: ~445MB (indicates GPU libraries included)
- [ ] Import works: No errors when importing llama_cpp
- [ ] CUDA detected: Verbose output shows GPU initialization
- [ ] Layers assigned: Some layers assigned to CUDA device
- [ ] Performance gain: GPU faster than CPU-only mode

**✅ Optimization Success Indicators**:
- [ ] Generation time: Under 5 seconds for simple prompts
- [ ] GPU utilization: nvidia-smi shows GPU activity during inference
- [ ] Memory efficient: No out-of-memory errors
- [ ] Consistent performance: Stable generation times across runs
- [ ] Adapter integration: LocalModelAdapter works with GPU settings

**🎉 Project Complete When**:
- All success indicators checked ✅
- Performance improvement documented
- Integration tests passing
- Ready for production use

#### 1.1 Initial System Assessment
```bash
# Check CUDA installation
nvcc --version
nvidia-smi

# Verify Python environment
python --version
pip list | grep torch
```

#### 1.2 NumPy Compatibility Fix
**Issue**: NumPy 2.x incompatibility with existing packages
```bash
# Downgrade to compatible version
pip install "numpy<2.0.0"
```

#### 1.3 CUDA Environment Verification
```python
import torch
print(f"CUDA Available: {torch.cuda.is_available()}")
print(f"CUDA Version: {torch.version.cuda}")
print(f"GPU Name: {torch.cuda.get_device_name(0)}")
print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
```

### Phase 2: Framework Evaluation & Selection

#### 2.1 Failed Attempts
1. **vLLM**: Windows incompatibility issues
2. **ExLlamaV2**: Model format conversion required
3. **Pre-built cuBLAS wheels**: Actually CPU-only despite naming

#### 2.2 Successful Solution: Manual Build
**Chosen**: llama-cpp-python with manual cuBLAS compilation

### Phase 3: Build Environment Preparation

#### 3.1 Prerequisites Installation (Estimated Time: 10-15 minutes)

##### Step 1: Visual Studio Build Tools
```powershell
# Check if already installed
Get-WmiObject -Class Win32_Product | Where-Object {$_.Name -like "*Visual Studio*"}

# Install Build Tools (if not present)
winget install Microsoft.VisualStudio.2022.BuildTools
```

**Progress Indicators**:
- ✅ Download: ~1-2GB, takes 5-10 minutes
- ✅ Installation: Automatic with GUI installer
- ✅ Verification: Should see "Microsoft Visual Studio Build Tools" in installed programs

##### Step 2: CMake Installation
```powershell
# Check current CMake version
cmake --version

# Install/Update CMake
winget install Kitware.CMake

# Add to PATH (if needed)
$env:PATH += ";C:\Program Files\CMake\bin"
```

**Progress Indicators**:
- ✅ Required version: 3.24 or higher
- ✅ Download size: ~40MB
- ✅ Installation time: 2-3 minutes

##### Step 3: Git Installation (if needed)
```powershell
# Verify Git is available
git --version

# Install if missing
winget install Git.Git
```

#### 3.2 CUDA Environment Setup (Estimated Time: 5 minutes)

##### Step 1: Verify CUDA Installation
```powershell
# Check CUDA version
nvcc --version
nvidia-smi

# Expected output patterns:
# nvcc: Cuda compilation tools, release 12.5, V12.5.xxx
# nvidia-smi: Should show your RTX 3050 GPU
```

**Troubleshooting CUDA Issues**:
```powershell
# If CUDA not found, check installation paths
dir "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA"

# Common CUDA paths to verify
$env:CUDA_PATH
$env:CUDA_PATH_V12_5
```

##### Step 2: Set Build Environment Variables
```powershell
# Set CUDA paths (adjust version as needed)
$env:CUDA_PATH = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.5"
$env:CUDA_HOME = $env:CUDA_PATH

# Set cuBLAS build flags
$env:CMAKE_ARGS = "-DGGML_CUDA=on -DCUDA_TOOLKIT_ROOT_DIR=$env:CUDA_PATH"

# Optional: Add to permanent environment (requires admin)
[Environment]::SetEnvironmentVariable("CUDA_PATH", $env:CUDA_PATH, "Machine")
```

**Environment Verification**:
```powershell
# Verify all paths are set correctly
Write-Host "CUDA_PATH: $env:CUDA_PATH"
Write-Host "CMAKE_ARGS: $env:CMAKE_ARGS"

# Test CUDA compiler access
nvcc --version
```

### Phase 4: llama-cpp-python Manual Compilation

#### 4.1 Pre-Build Preparation (Estimated Time: 2-3 minutes)

##### Step 1: Clean Previous Installations
```powershell
# Uninstall any existing llama-cpp-python versions
pip uninstall llama-cpp-python -y

# Clear pip cache to ensure fresh build
pip cache purge

# Verify removal
pip list | Select-String "llama"
```

##### Step 2: Verify Build Dependencies
```powershell
# Check Python version (3.11 recommended)
python --version

# Verify pip is updated
python -m pip install --upgrade pip

# Check available disk space (need ~2GB for build)
Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, @{Name="Free(GB)";Expression={[math]::Round($_.FreeSpace/1GB,2)}}
```

#### 4.2 cuBLAS Build Process (Estimated Time: 30-45 minutes)

##### Step 1: Start the Build
```powershell
# Set build environment (critical step)
$env:CMAKE_ARGS = "-DGGML_CUDA=on"
$env:FORCE_CMAKE = "1"

# Start compilation (this will take 30+ minutes)
Write-Host "Starting llama-cpp-python compilation with cuBLAS..."
Write-Host "Build time: ~30-45 minutes depending on system"
Write-Host "Expected wheel size: ~445MB (vs ~50MB CPU-only)"

pip install llama-cpp-python --no-cache-dir --force-reinstall --no-binary=llama-cpp-python --verbose
```

##### Step 2: Build Progress Monitoring
**Phase 1: Source Download & Setup** (2-3 minutes)
```
Expected output:
- Collecting llama-cpp-python
- Downloading llama-cpp-python-x.x.x.tar.gz
- Preparing metadata
```

**Phase 2: CMake Configuration** (3-5 minutes)
```
Expected output:
- Running setup.py bdist_wheel
- CMake configuration starting
- -- Found CUDA: /path/to/cuda (found version "12.5")
- -- GGML_CUDA: ON
- -- CUDA compiler: /path/to/nvcc
```

**Phase 3: Compilation** (25-35 minutes)
```
Expected progress indicators:
- [  5%] Building CXX object
- [ 25%] Building CUDA object (GPU kernels)
- [ 50%] Linking targets
- [ 75%] Building Python bindings
- [100%] Built target llama-cpp-python
```

**Phase 4: Wheel Creation** (2-3 minutes)
```
Expected output:
- Creating wheel
- Successfully built llama-cpp-python
- Installing collected packages: llama-cpp-python
```

##### Step 3: Build Success Verification
```powershell
# Check installation
pip list | Select-String "llama"

# Verify wheel size (should be ~445MB)
$wheelPath = (pip show llama-cpp-python | Select-String "Location").ToString().Split(":")[1].Trim()
Write-Host "Installation location: $wheelPath"

# Quick CUDA test
python -c "from llama_cpp import Llama; print('✅ Import successful')"
```

#### 4.3 Build Troubleshooting

##### Common Build Errors & Solutions

**Error 1: "CUDA not found"**
```powershell
# Solution: Set CUDA path explicitly
$env:CUDA_PATH = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.5"
$env:CMAKE_ARGS = "-DGGML_CUDA=on -DCUDA_TOOLKIT_ROOT_DIR=$env:CUDA_PATH"
```

**Error 2: "CMake not found"**
```powershell
# Solution: Add CMake to PATH
$env:PATH += ";C:\Program Files\CMake\bin"
cmake --version  # Should work now
```

**Error 3: "Microsoft Visual C++ 14.0 is required"**
```powershell
# Solution: Install Build Tools
winget install Microsoft.VisualStudio.2022.BuildTools
# Then restart PowerShell and retry
```

**Error 4: "Out of memory during compilation"**
```powershell
# Solution: Reduce parallel jobs
$env:CMAKE_ARGS = "-DGGML_CUDA=on -DCMAKE_BUILD_PARALLEL_LEVEL=2"
# Or close other applications to free RAM
```

##### Build Verification Checklist
- ✅ **Build completed without errors**
- ✅ **Wheel size ~445MB** (indicates GPU libraries included)
- ✅ **Import test passes**: `python -c "from llama_cpp import Llama"`
- ✅ **CUDA detection**: Build logs show "Found CUDA" messages
- ✅ **Installation time**: 30+ minutes (quick builds usually indicate CPU-only)

#### 4.4 GPU Acceleration Verification (Estimated Time: 5-10 minutes)

##### Step 1: Basic CUDA Detection Test
```python
# Create test script: test_cuda_detection.py
import sys
import os

print("=== llama-cpp-python CUDA Verification ===")

try:
    from llama_cpp import Llama
    print("✅ llama-cpp-python import successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test CUDA availability through PyTorch (if available)
try:
    import torch
    print(f"PyTorch CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA Device: {torch.cuda.get_device_name(0)}")
        print(f"CUDA Version: {torch.version.cuda}")
except ImportError:
    print("PyTorch not available (optional)")
```

##### Step 2: Model Loading Test with GPU Detection
```python
# Create comprehensive test: test_gpu_model.py
import os
import time
from llama_cpp import Llama

# Configuration
MODEL_PATH = os.path.join('backend', 'ai_models', 'Llama-3.1-8B-UltraMedical.Q8_0.gguf')
print(f"Testing model: {MODEL_PATH}")

if not os.path.exists(MODEL_PATH):
    print(f"❌ Model not found at: {MODEL_PATH}")
    print("Please verify model path and try again")
    exit(1)

print("\n=== GPU Layer Test ===")

# Test with 1 GPU layer to verify CUDA works
print("Loading model with 1 GPU layer (verbose mode)...")
start_time = time.time()

try:
    llm = Llama(
        model_path=MODEL_PATH,
        n_gpu_layers=1,          # Test with minimal GPU usage
        n_ctx=256,               # Small context for speed
        verbose=True             # Show GPU detection messages
    )
    
    load_time = time.time() - start_time
    print(f"✅ Model loaded successfully in {load_time:.2f}s")
    
    # Quick generation test
    print("\n=== Generation Test ===")
    start_gen = time.time()
    
    response = llm.create_completion(
        prompt="What is fever?",
        max_tokens=20,
        temperature=0.1
    )
    
    gen_time = time.time() - start_gen
    print(f"✅ Generation completed in {gen_time:.2f}s")
    print(f"Response: {response['choices'][0]['text'].strip()}")
    
except Exception as e:
    print(f"❌ Error during model loading/generation: {e}")
    print("\nTroubleshooting steps:")
    print("1. Verify model path is correct")
    print("2. Check CUDA environment variables")
    print("3. Ensure sufficient GPU memory")
```

##### Step 3: Expected Verbose Output Analysis
**Look for these key indicators in the verbose output:**

```
✅ CUDA Detection:
ggml_cuda_init: found 1 CUDA devices:
  Device 0: NVIDIA GeForce RTX 3050 Laptop GPU, compute capability 8.6

✅ Memory Allocation:
llama_model_load_from_file_impl: using device CUDA0 - 3303 MiB free
llama_model_load_from_file_impl: mem required  = 8159.38 MiB
llama_model_load_from_file_impl: allocating batch_size x 1 MB = 16 MB VRAM

✅ Layer Assignment:
load_tensors: layer 31 assigned to device CUDA0  # This confirms GPU usage
```

**❌ Warning Signs (indicates CPU-only):**
- No CUDA initialization messages
- All layers assigned to CPU
- Unusually fast "build" (under 10 minutes)
- Wheel size around 50MB instead of 445MB

##### Step 4: Performance Baseline Establishment
```python
# Create benchmark script: benchmark_performance.py
import time
import os
from llama_cpp import Llama

MODEL_PATH = os.path.join('backend', 'ai_models', 'Llama-3.1-8B-UltraMedical.Q8_0.gguf')

def test_configuration(gpu_layers, description):
    print(f"\n=== {description} ===")
    start_time = time.time()
    
    llm = Llama(
        model_path=MODEL_PATH,
        n_gpu_layers=gpu_layers,
        n_ctx=256,
        verbose=False  # Reduce noise for benchmarking
    )
    
    load_time = time.time() - start_time
    
    # Standard test prompt
    test_prompt = "Patient has fever, headache, and fatigue. List 3 possible diagnoses:"
    
    gen_start = time.time()
    response = llm.create_completion(
        prompt=test_prompt,
        max_tokens=50,
        temperature=0.1
    )
    gen_time = time.time() - gen_start
    
    print(f"Load time: {load_time:.2f}s")
    print(f"Generation time: {gen_time:.2f}s")
    print(f"Total time: {load_time + gen_time:.2f}s")
    
    return gen_time

# Benchmark different configurations
print("=== Performance Baseline Tests ===")
cpu_time = test_configuration(0, "CPU Only (Baseline)")
gpu_time = test_configuration(16, "GPU Accelerated (16 layers)")

if gpu_time < cpu_time:
    speedup = cpu_time / gpu_time
    print(f"\n✅ GPU Acceleration Working!")
    print(f"Speedup: {speedup:.2f}x faster than CPU")
else:
    print(f"\n❌ GPU acceleration not working properly")
    print(f"GPU time ({gpu_time:.2f}s) should be less than CPU time ({cpu_time:.2f}s)")
```

##### Step 5: Integration Test with LocalModelAdapter
```python
# Test the actual adapter: test_adapter_gpu.py
import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from adapters.local_model_adapter import LocalModelAdapter

async def test_adapter():
    print("=== LocalModelAdapter GPU Test ===")
    
    # Initialize adapter
    model_path = os.path.join('ai_models', 'Llama-3.1-8B-UltraMedical.Q8_0.gguf')
    adapter = LocalModelAdapter(model_path)
    
    # Load model
    print("Loading model through adapter...")
    await adapter.load_model()
    
    # Test diagnosis generation
    print("\n=== Diagnosis Test ===")
    symptoms = "Patient has persistent cough, fever, and chest pain for 3 days"
    
    start_time = time.time()
    diagnosis = await adapter.generate_diagnosis(symptoms)
    end_time = time.time()
    
    print(f"Generation time: {end_time - start_time:.2f}s")
    print(f"Result:\n{diagnosis}")
    
    # Test follow-up questions
    print("\n=== Follow-up Questions Test ===")
    start_time = time.time()
    questions = await adapter.generate_followup_questions(diagnosis, 0.8)
    end_time = time.time()
    
    print(f"Generation time: {end_time - start_time:.2f}s")
    print(f"Questions:\n{questions}")
    
    print("\n✅ Adapter integration test completed")

if __name__ == "__main__":
    import time
    asyncio.run(test_adapter())
```

##### Verification Checklist
- ✅ **CUDA Detection**: Verbose output shows GPU initialization
- ✅ **Layer Assignment**: At least some layers assigned to CUDA device
- ✅ **Performance Improvement**: GPU faster than CPU-only mode
- ✅ **Memory Usage**: GPU memory allocated properly
- ✅ **Adapter Integration**: LocalModelAdapter works with GPU acceleration
- ✅ **Error-free Operation**: No crashes or CUDA errors during inference

### Phase 5: Performance Optimization

#### 5.1 Optimal GPU Layer Configuration
**Testing Results**:
- 0 layers (CPU): 9.72s generation
- 16 layers (Optimal): 5.36s generation (**1.8x faster**)
- 32 layers (Full): 13.30s generation (slower due to memory overhead)

**Conclusion**: 16 GPU layers optimal for RTX 3050 4GB VRAM

#### 5.2 LocalModelAdapter Optimization
```python
# Optimal settings for RTX 3050
settings = {
    "chat_format": "llama-3",
    "n_ctx": 256,                       # Minimal context for speed
    "n_gpu_layers": 16,                 # Optimal for 4GB VRAM
    "main_gpu": 0,
    "split_mode": 1,
    "n_batch": 64,                      # Optimized batch size
    "n_ubatch": 32,                     # Optimized micro-batch
    "offload_kqv": True,                # GPU key-value cache
    "flash_attn": True,                 # Speed optimization
    "low_vram": True,                   # Memory efficiency
    "verbose": False,
    "mul_mat_q": True,                  # Quantized operations
    "f16_kv": True,                     # FP16 precision
    "use_mmap": True,                   # Memory mapping
}
```

#### 5.3 Runtime Optimizations
```python
def optimize_for_inference(self):
    if self.gpu_available:
        torch.cuda.empty_cache()
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        torch.backends.cudnn.benchmark = True

def enable_speed_mode(self):
    if self.gpu_available:
        torch.cuda.set_per_process_memory_fraction(0.9)
        torch.backends.cuda.fast_math = True
```

### Phase 6: Prompt Engineering for Speed

#### 6.1 Diagnosis Generation Optimization
**Before** (Complex prompt):
```python
prompt = f"""
Symptoms: {symptoms}
Provide 5 most possible diagnoses in this EXACT format:
- Diagnosis: <condition name>
- Confidence: <0.0-1.0>
Repeat the above 2 lines per diagnosis...
"""
```

**After** (Streamlined):
```python
prompt = f"""Symptoms: {symptoms}
List 5 diagnoses in this exact format:
- diagnosis: <name>
- confidence: <0.0-1.0>

Repeat for each diagnosis."""
```

#### 6.2 Follow-up Questions Optimization
**Before** (200 tokens, 0.3 temp):
```python
prompt = f"""Based on suspected condition(s): {diagnosis_context}
Generate ONLY 5 focused follow-up questions...
[detailed instructions]"""
```

**After** (100 tokens, 0.1 temp):
```python
prompt = f"""Based on: {diagnosis_context} (confidence: {average_confidence:.2f})
Generate 5 follow-up questions numbered 1-5:
1. 
2. 
3. 
4. 
5. """
```

---

## 🎯 **Final Architecture**

### GPU-Optimized LocalModelAdapter
```python
class LocalModelAdapter(ModelInterface):
    def __init__(self, llm_path: str):
        # System detection
        self.gpu_available = torch.cuda.is_available()
        self.gpu_memory_gb = self._get_gpu_memory()
        
    async def load_model(self):
        # Enable optimizations
        self.enable_speed_mode()
        
        # Optimal cuBLAS settings
        settings = self._get_optimal_settings()
        
        # Load with GPU acceleration
        self.model = Llama(model_path=self.model_path, **settings)
        
        # Apply runtime optimizations
        self.optimize_for_inference()
```

### Streamlined Generation Methods
```python
async def generate_diagnosis(self, symptoms: str) -> str:
    prompt = f"Symptoms: {symptoms}\nList 5 diagnoses..."
    return await self.run_sync(self._generate_text_sync, prompt, 50, 0.1)

async def generate_followup_questions(self, diagnosis_context: str, average_confidence: float) -> str:
    prompt = f"Based on: {diagnosis_context}..."
    return await self.run_sync(self._generate_text_sync, prompt, 100, 0.1)
```

---

## 📈 **Performance Benchmarks**

### Load Time Analysis
- **Model Size**: 7.95 GiB (Llama-3.1-8B-UltraMedical.Q8_0.gguf)
- **GPU Memory Allocation**: 221.03 MiB model buffer + 661.56 MiB compute buffer
- **Load Time**: 7.54s (acceptable for initialization)

### Generation Speed Analysis
- **Simple Generation**: 4.45s (under 5s target ✅)
- **Medical Diagnosis**: 7.45s (with complex medical reasoning)
- **Follow-up Questions**: ~5-8s (context-dependent)

### Memory Usage
- **GPU VRAM**: ~1GB actively used of 4GB available
- **System RAM**: Normal usage patterns
- **Context Window**: 256 tokens (optimized for speed)

---

## 🔍 **Comprehensive Troubleshooting Guide**

### Installation & Build Issues

#### Issue 1: "CUDA not found during build"
**Symptoms**:
- Build completes in under 10 minutes
- Wheel size is ~50MB instead of 445MB
- No CUDA messages in build log

**Diagnostic Steps**:
```powershell
# Check CUDA installation
nvcc --version
nvidia-smi

# Verify environment variables
echo $env:CUDA_PATH
echo $env:CMAKE_ARGS

# Check if CUDA is in PATH
where nvcc
```

**Solutions**:
```powershell
# Solution A: Set CUDA path explicitly
$env:CUDA_PATH = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.5"
$env:CMAKE_ARGS = "-DGGML_CUDA=on -DCUDA_TOOLKIT_ROOT_DIR=$env:CUDA_PATH"

# Solution B: Install CUDA if missing
# Download from: https://developer.nvidia.com/cuda-downloads
# Select: Windows > x86_64 > 10/11 > exe (local)

# Solution C: Verify CUDA version compatibility
# CUDA 12.x recommended for RTX 3050
```

#### Issue 2: "Microsoft Visual C++ 14.0 is required"
**Symptoms**:
- Build fails immediately
- Error mentions "Microsoft Visual C++ 14.0 or greater is required"

**Solutions**:
```powershell
# Option 1: Install Build Tools (Recommended)
winget install Microsoft.VisualStudio.2022.BuildTools

# Option 2: Install full Visual Studio
winget install Microsoft.VisualStudio.2022.Community

# Option 3: Install standalone MSVC
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Verify installation
where cl  # Should show Microsoft C/C++ compiler path
```

#### Issue 3: "CMake not found"
**Symptoms**:
- Error: "CMake must be installed to build the following extensions"
- Build fails during setup phase

**Solutions**:
```powershell
# Install CMake
winget install Kitware.CMake

# Add to PATH manually if needed
$env:PATH += ";C:\Program Files\CMake\bin"

# Verify installation
cmake --version  # Should show 3.24+ for best compatibility

# Alternative: Use pip to install cmake
pip install cmake
```

#### Issue 4: "Out of memory during compilation"
**Symptoms**:
- Build fails partway through
- System becomes unresponsive
- Error about insufficient memory

**Solutions**:
```powershell
# Solution 1: Reduce parallel compilation
$env:CMAKE_ARGS = "-DGGML_CUDA=on -DCMAKE_BUILD_PARALLEL_LEVEL=2"

# Solution 2: Close unnecessary applications
# - Close browsers, IDEs, other memory-heavy apps
# - Monitor RAM usage during build

# Solution 3: Use swap file (if needed)
# Increase virtual memory in Windows settings

# Solution 4: Build with minimal flags
$env:CMAKE_ARGS = "-DGGML_CUDA=on -DCMAKE_BUILD_TYPE=Release"
```

#### Issue 5: NumPy version conflicts
**Symptoms**:
- Import errors after installation
- Compatibility warnings
- Other packages fail to work

**Diagnostic**:
```powershell
# Check NumPy version
python -c "import numpy; print(numpy.__version__)"

# Check conflicting packages
pip list | Select-String "numpy"
```

**Solution**:
```powershell
# Downgrade NumPy to compatible version
pip install "numpy<2.0.0"

# If that fails, force reinstall
pip uninstall numpy -y
pip install "numpy==1.26.4"

# Verify fix
python -c "import numpy; print('NumPy version:', numpy.__version__)"
```

### Runtime Issues

#### Issue 6: "Model path does not exist"
**Symptoms**:
- Error when loading model
- Path-related exceptions

**Solutions**:
```python
# Use absolute paths
import os
model_path = os.path.abspath(os.path.join('backend', 'ai_models', 'Llama-3.1-8B-UltraMedical.Q8_0.gguf'))

# Check if file exists
if not os.path.exists(model_path):
    print(f"Model not found at: {model_path}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Directory contents: {os.listdir('.')}")

# Alternative: Use relative path from script location
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, 'ai_models', 'model.gguf')
```

#### Issue 7: CUDA detected but no GPU acceleration
**Symptoms**:
- CUDA appears in logs
- No performance improvement
- Layers still on CPU

**Diagnostic**:
```python
# Enable verbose mode to see layer assignment
llm = Llama(
    model_path=model_path,
    n_gpu_layers=16,
    verbose=True  # Check output for "assigned to device CUDA0"
)
```

**Solutions**:
```python
# Solution 1: Increase GPU layers gradually
for layers in [1, 4, 8, 16, 32]:
    print(f"Testing {layers} GPU layers...")
    # Test each configuration

# Solution 2: Check GPU memory availability
import torch
if torch.cuda.is_available():
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
    print(f"GPU Free: {torch.cuda.memory_reserved(0) / 1024**3:.1f}GB")

# Solution 3: Enable low VRAM mode
llm = Llama(
    model_path=model_path,
    n_gpu_layers=16,
    low_vram=True,  # Essential for 4GB GPUs
    main_gpu=0
)
```

#### Issue 8: Slow performance despite GPU
**Symptoms**:
- GPU detected and layers assigned
- Still slower than expected
- High generation times

**Solutions**:
```python
# Optimize context size
llm = Llama(
    model_path=model_path,
    n_gpu_layers=16,
    n_ctx=256,      # Smaller context = faster generation
    n_batch=64,     # Optimize batch size
    n_ubatch=32     # Optimize micro-batch
)

# Enable speed optimizations
llm = Llama(
    model_path=model_path,
    n_gpu_layers=16,
    flash_attn=True,    # Speed optimization
    offload_kqv=True,   # GPU key-value cache
    f16_kv=True,        # Half precision
    mul_mat_q=True      # Quantized operations
)

# Reduce generation parameters
response = llm.create_completion(
    prompt=prompt,
    max_tokens=50,      # Fewer tokens = faster
    temperature=0.1,    # Lower temperature = more deterministic
    top_p=0.7,         # Reduced sampling
    top_k=15           # Limited choices
)
```

### Performance Validation Issues

#### Issue 9: Inconsistent performance results
**Symptoms**:
- Performance varies greatly between runs
- Sometimes fast, sometimes slow
- Unpredictable generation times

**Solutions**:
```python
# Warm up the model first
for i in range(3):
    _ = llm.create_completion(prompt="Test", max_tokens=5)

# Use consistent test conditions
def benchmark_generation():
    import time
    times = []
    
    for i in range(5):  # Multiple runs for average
        start = time.time()
        response = llm.create_completion(
            prompt="Standard test prompt",
            max_tokens=50,
            temperature=0.1,
            seed=42  # Consistent seed for reproducibility
        )
        times.append(time.time() - start)
    
    avg_time = sum(times) / len(times)
    print(f"Average generation time: {avg_time:.2f}s")
    return avg_time
```

#### Issue 10: GPU memory errors
**Symptoms**:
- CUDA out of memory errors
- System freezing
- Driver crashes

**Solutions**:
```python
# Solution 1: Reduce GPU layers
llm = Llama(
    model_path=model_path,
    n_gpu_layers=8,     # Start smaller
    low_vram=True
)

# Solution 2: Clear GPU memory before loading
import torch
if torch.cuda.is_available():
    torch.cuda.empty_cache()

# Solution 3: Monitor memory usage
def check_gpu_memory():
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated(0) / 1024**3
        reserved = torch.cuda.memory_reserved(0) / 1024**3
        print(f"GPU Memory - Allocated: {allocated:.2f}GB, Reserved: {reserved:.2f}GB")

# Solution 4: Use smaller batch sizes
llm = Llama(
    model_path=model_path,
    n_gpu_layers=16,
    n_batch=32,     # Smaller batch
    n_ubatch=16     # Smaller micro-batch
)
```

### Diagnostic Tools & Commands

#### System Information Gathering
```powershell
# Complete system diagnostic script
Write-Host "=== System Diagnostic ==="

# GPU Information
nvidia-smi --query-gpu=name,memory.total,memory.free,driver_version --format=csv

# CUDA Information
nvcc --version
$env:CUDA_PATH

# Python Environment
python --version
pip list | Select-String "llama|torch|numpy"

# Build Tools
cmake --version
where cl  # Visual Studio compiler

# System Resources
Get-WmiObject -Class Win32_ComputerSystem | Select-Object TotalPhysicalMemory
Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID,FreeSpace,Size
```

#### Performance Monitoring During Operation
```python
# Real-time monitoring script
import psutil
import torch
import time

def monitor_system():
    while True:
        # CPU Usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory Usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # GPU Usage (if available)
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.memory_allocated(0) / 1024**3
            gpu_reserved = torch.cuda.memory_reserved(0) / 1024**3
        else:
            gpu_memory = gpu_reserved = 0
        
        print(f"CPU: {cpu_percent}% | RAM: {memory_percent}% | GPU: {gpu_memory:.1f}GB/{gpu_reserved:.1f}GB")
        time.sleep(5)
```

### Emergency Recovery Procedures

#### Complete Environment Reset
```powershell
# If everything is broken, start fresh
Write-Host "=== Emergency Reset ==="

# 1. Uninstall all llama-cpp-python versions
pip uninstall llama-cpp-python -y

# 2. Clear all caches
pip cache purge
Remove-Item -Recurse -Force $env:TEMP\pip-*

# 3. Reset environment variables
Remove-Item Env:CMAKE_ARGS -ErrorAction SilentlyContinue
Remove-Item Env:CUDA_PATH -ErrorAction SilentlyContinue

# 4. Restart PowerShell session
# Close and reopen PowerShell

# 5. Verify clean state
pip list | Select-String "llama"  # Should return nothing

# 6. Start installation process from Phase 3 again
```

### Success Validation Checklist

#### Final Verification Steps
```powershell
# Run this complete validation script
Write-Host "=== Final GPU Acceleration Validation ==="

# 1. Import test
python -c "from llama_cpp import Llama; print('✅ Import successful')"

# 2. CUDA detection
python -c "
import torch
if torch.cuda.is_available():
    print(f'✅ CUDA Available: {torch.cuda.get_device_name(0)}')
else:
    print('❌ CUDA not available')
"

# 3. Wheel size check
$location = (pip show llama-cpp-python | Select-String "Location").ToString().Split(":")[1].Trim()
$size = (Get-ChildItem "$location\llama_cpp*" -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "Wheel size: $([math]::Round($size))MB (should be ~445MB)"

# 4. Performance test
python -c "
import time
import os
from llama_cpp import Llama

model_path = os.path.join('backend', 'ai_models', 'Llama-3.1-8B-UltraMedical.Q8_0.gguf')
if os.path.exists(model_path):
    start = time.time()
    llm = Llama(model_path=model_path, n_gpu_layers=1, n_ctx=128, verbose=True)
    response = llm.create_completion(prompt='Test', max_tokens=5)
    total_time = time.time() - start
    print(f'✅ Complete test: {total_time:.2f}s')
else:
    print('❌ Model file not found')
"
```

**Expected Results for Success**:
- ✅ All imports work without errors
- ✅ CUDA detected and RTX 3050 shown
- ✅ Wheel size approximately 445MB
- ✅ Verbose output shows "assigned to device CUDA0"
- ✅ Generation time under 10 seconds for simple prompts
- ✅ No error messages or warnings

---

## 🎛️ **Configuration Reference**

### Optimal Settings for RTX 3050 (4GB VRAM)
```python
OPTIMAL_SETTINGS = {
    "n_gpu_layers": 16,        # Tested optimal
    "n_ctx": 256,              # Speed over capacity
    "n_batch": 64,             # Memory/speed balance
    "n_ubatch": 32,            # Micro-batch optimization
    "low_vram": True,          # Essential for 4GB
    "flash_attn": True,        # Speed boost
    "offload_kqv": True,       # GPU key-value cache
    "f16_kv": True,            # Half precision
    "mul_mat_q": True,         # Quantized operations
}
```

### Generation Parameters
```python
SPEED_PARAMS = {
    "temperature": 0.1,        # Deterministic, fast
    "top_p": 0.7,              # Reduced sampling
    "top_k": 15,               # Limited choices
    "repeat_penalty": 1.02,    # Minimal penalty
}
```

---

## 📚 **Key Learnings**

### Technical Insights
1. **Manual compilation essential**: Pre-built wheels often lack true GPU support
2. **Layer optimization crucial**: More GPU layers ≠ better performance
3. **Context size matters**: Smaller contexts = faster generation
4. **Prompt engineering impact**: Concise prompts significantly improve speed
5. **Memory management**: Low VRAM mode essential for consumer GPUs

### Performance Principles
1. **Measure everything**: Baseline → optimize → verify
2. **Find sweet spots**: Balance GPU layers with memory constraints
3. **Optimize holistically**: Hardware + software + prompts
4. **Monitor resources**: GPU utilization, memory usage, temperatures

### Development Best Practices
1. **Environment isolation**: Use virtual environments
2. **Version pinning**: Lock working versions
3. **Comprehensive testing**: Multiple scenarios and edge cases
4. **Documentation**: Record configurations and results

---

## 🔮 **Future Enhancements**

### Potential Improvements
1. **Model optimization**: Try Q4_K_M quantization for more GPU layers
2. **Dynamic scaling**: Adjust GPU layers based on available VRAM
3. **Batch processing**: Optimize for multiple concurrent requests
4. **Model caching**: Keep model loaded between requests

### Monitoring & Maintenance
1. **Performance tracking**: Log generation times and GPU utilization
2. **Error monitoring**: Track failures and fallback scenarios
3. **Regular testing**: Verify performance after system updates
4. **Optimization reviews**: Periodic analysis of new optimization techniques

---

## ✅ **Success Criteria Met**

- ✅ **2x+ performance improvement** (4.45s vs 9.72s baseline)
- ✅ **GPU acceleration working** (cuBLAS enabled, layers on GPU)
- ✅ **Memory efficient** (Low VRAM mode, optimized settings)
- ✅ **Production ready** (Error handling, fallbacks, monitoring)
- ✅ **Maintainable code** (Clean architecture, documented settings)

---

## 📞 **Support & Resources**

### Key Dependencies
- `llama-cpp-python`: Core inference engine
- `torch`: CUDA interface and optimizations
- `numpy<2.0.0`: Compatibility requirement

### Documentation Links
- [llama-cpp-python GitHub](https://github.com/abetlen/llama-cpp-python)
- [CUDA Installation Guide](https://developer.nvidia.com/cuda-downloads)
- [CMake Documentation](https://cmake.org/documentation/)

### Performance Monitoring
- Use `nvidia-smi` for GPU monitoring
- Check `torch.cuda.memory_allocated()` for memory usage
- Monitor generation times in application logs

---

*This documentation represents a complete transformation from CPU-only to GPU-accelerated inference, achieving significant performance improvements while maintaining code quality and reliability.*
