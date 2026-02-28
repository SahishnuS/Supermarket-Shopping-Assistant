"""
AMD Hardware Detection & DirectML Acceleration Utilities.
Detects AMD GPU hardware and configures ONNX Runtime with DirectML
for GPU-accelerated AI inference on AMD Radeon GPUs.
"""

import subprocess
import platform


def detect_amd_gpu():
    """
    Detect AMD GPU hardware on the system.
    
    Returns:
        dict with keys:
            - found (bool): Whether an AMD GPU was detected
            - name (str): GPU name (e.g. 'AMD Radeon(TM) Graphics')
            - driver (str): Driver info if available
    """
    gpu_info = {"found": False, "name": "Unknown", "driver": "Unknown"}
    
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ["wmic", "path", "win32_VideoController", "get", "name"],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.strip().split("\n"):
                line = line.strip()
                if "AMD" in line or "Radeon" in line:
                    gpu_info["found"] = True
                    gpu_info["name"] = line
                    break
            
            # Get driver version
            result_driver = subprocess.run(
                ["wmic", "path", "win32_VideoController", "get", "DriverVersion"],
                capture_output=True, text=True, timeout=5
            )
            for line in result_driver.stdout.strip().split("\n"):
                line = line.strip()
                if line and line != "DriverVersion":
                    gpu_info["driver"] = line
                    break
        else:
            # Linux: check lspci
            result = subprocess.run(
                ["lspci"], capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.split("\n"):
                if "AMD" in line and ("VGA" in line or "Display" in line):
                    gpu_info["found"] = True
                    gpu_info["name"] = line.split(":")[-1].strip()
                    break
    except Exception:
        pass
    
    return gpu_info


def get_directml_provider():
    """
    Check if ONNX Runtime DirectML execution provider is available
    for AMD GPU acceleration.
    
    Returns:
        dict with keys:
            - available (bool): Whether DirectML provider is ready
            - provider_name (str): The ONNX Runtime provider name
            - all_providers (list): All available ONNX Runtime providers
    """
    info = {
        "available": False,
        "provider_name": "CPUExecutionProvider",
        "all_providers": []
    }
    
    try:
        import onnxruntime as ort
        providers = ort.get_available_providers()
        info["all_providers"] = providers
        
        if "DmlExecutionProvider" in providers:
            info["available"] = True
            info["provider_name"] = "DmlExecutionProvider"
        elif "ROCMExecutionProvider" in providers:
            info["available"] = True
            info["provider_name"] = "ROCMExecutionProvider"
    except ImportError:
        pass
    
    return info


def get_amd_acceleration_status():
    """
    Get a comprehensive AMD acceleration status report.
    
    Returns:
        dict with full AMD hardware and software status
    """
    gpu = detect_amd_gpu()
    directml = get_directml_provider()
    
    # Check PyTorch ROCm
    rocm_available = False
    try:
        import torch
        rocm_available = hasattr(torch.version, 'hip')
    except ImportError:
        pass
    
    return {
        "gpu": gpu,
        "directml": directml,
        "rocm_available": rocm_available,
        "acceleration_active": directml["available"] or rocm_available,
        "summary": _build_summary(gpu, directml, rocm_available)
    }


def _build_summary(gpu, directml, rocm_available):
    """Build a human-readable summary of AMD acceleration status."""
    lines = []
    
    if gpu["found"]:
        lines.append(f"✅ AMD GPU Detected: {gpu['name']}")
        lines.append(f"   Driver: {gpu['driver']}")
    else:
        lines.append("❌ No AMD GPU detected")
    
    if directml["available"]:
        lines.append(f"✅ DirectML Acceleration: Active ({directml['provider_name']})")
    else:
        lines.append("⚠️ DirectML: Not available (using CPU fallback)")
    
    if rocm_available:
        lines.append("✅ PyTorch ROCm: Available")
    
    lines.append(f"   ONNX Providers: {', '.join(directml['all_providers'])}")
    
    return "\n".join(lines)


def get_optimal_onnx_providers():
    """
    Get the optimal ONNX Runtime execution providers list,
    prioritizing AMD GPU acceleration.
    
    Returns:
        list of provider names in priority order
    """
    providers = ["CPUExecutionProvider"]  # Always fallback
    
    try:
        import onnxruntime as ort
        available = ort.get_available_providers()
        
        # Prefer DirectML for AMD GPUs on Windows
        if "DmlExecutionProvider" in available:
            providers.insert(0, "DmlExecutionProvider")
        # ROCm for AMD GPUs on Linux
        elif "ROCMExecutionProvider" in available:
            providers.insert(0, "ROCMExecutionProvider")
        # CUDA as alternative
        elif "CUDAExecutionProvider" in available:
            providers.insert(0, "CUDAExecutionProvider")
    except ImportError:
        pass
    
    return providers


# Quick test when run directly
if __name__ == "__main__":
    status = get_amd_acceleration_status()
    print("\n=== AMD Acceleration Status ===")
    print(status["summary"])
    print(f"\nOptimal ONNX Providers: {get_optimal_onnx_providers()}")
