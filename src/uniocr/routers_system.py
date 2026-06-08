import platform
import psutil
import time
import socket
import subprocess
import re
from fastapi import APIRouter, Depends
from .routers_auth import get_current_user

router = APIRouter(prefix="/api/system", tags=["System"])

def get_cpu_model():
    sys_os = platform.system()
    if sys_os == "Darwin":
        try:
            return subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], text=True).strip()
        except Exception:
            return "Unknown Apple CPU"
    elif sys_os == "Linux":
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        return line.split(":")[1].strip()
        except Exception:
            pass
    return platform.processor() or "Unknown CPU"

def get_gpu_info():
    sys_os = platform.system()
    if sys_os == "Darwin":
        try:
            out = subprocess.check_output(["system_profiler", "SPDisplaysDataType"], text=True)
            match = re.search(r"Chipset Model:\s*(.*)", out)
            cores = re.search(r"Total Number of Cores:\s*(\d+)", out)
            if match:
                name = match.group(1).strip()
                if cores:
                    name += f" ({cores.group(1).strip()} Cores)"
                return name
        except Exception:
            pass
    elif sys_os == "Linux":
        try:
            out = subprocess.check_output(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], text=True)
            return out.strip().split('\n')[0]
        except Exception:
            pass
    return "No Dedicated GPU / Unknown"

@router.get("/info", dependencies=[Depends(get_current_user)])
def get_system_info():
    info = {
        "os": platform.system(),
        "release": platform.release(),
        "arch": platform.machine(),
        "python_version": platform.python_version(),
        "cpu_model": get_cpu_model(),
        "cpu_cores": psutil.cpu_count(logical=True),
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "memory_used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
        "memory_used_percent": psutil.virtual_memory().percent,
        "disk_total_gb": round(psutil.disk_usage('/').total / (1024**3), 2),
        "disk_used_gb": round(psutil.disk_usage('/').used / (1024**3), 2),
        "disk_used_percent": psutil.disk_usage('/').percent,
        "gpu_model": get_gpu_info(),
        "uptime_hours": round((time.time() - psutil.boot_time()) / 3600, 1),
        "network_ip": socket.gethostbyname(socket.gethostname()) if socket.gethostname() else "127.0.0.1",
        "apple_silicon": False,
        "mlx_available": False,
        "paddle_available": False,
    }
    
    # Apple Silicon detection
    if platform.system() == "Darwin" and platform.machine() == "arm64":
        info["apple_silicon"] = True
        
    try:
        import mlx.core
        info["mlx_available"] = True
    except ImportError:
        pass
        
    try:
        import paddle
        info["paddle_available"] = True
    except ImportError:
        pass
        
    return info
