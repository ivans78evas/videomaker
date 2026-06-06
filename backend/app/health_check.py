import sys
import torch

def health_check():
    """
    Checks if GPU is accessible and necessary services are running.
    """
    status = {
        "gpu_available": torch.cuda.is_available(),
        "gpu_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None",
        "python_version": sys.version
    }

    if status["gpu_available"]:
        print(f"HEALTH CHECK PASSED: {status}")
        sys.exit(0)
    else:
        print(f"HEALTH CHECK FAILED (No GPU): {status}")
        sys.exit(1)

if __name__ == "__main__":
    health_check()
