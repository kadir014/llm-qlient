"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

import subprocess
from dataclasses import dataclass


@dataclass
class NvidiaDriverInfo:
    """
    Information about installed Nvidia driver.

    Fields are empty strings if information is failed to fetch

    Fields
    ------
    version
        Currently installed version
    smi_version
        NVSMI version
    nvml_version
        NVML version
    cuda_version
        Supported CUDA version
        This can be different from the installed CUDA driver version
    """
    version: str = ""
    smi_version: str = ""
    nvml_version: str = ""
    cuda_version: str = ""


@dataclass
class NvidiaGPUInfo:
    """
    Information about Nvidia GPU.

    Fields are either empty strings or zeroes if informatios is failed to fetch.

    Fields
    ------
    name
        Official product name of the GPU
    brand
        Official brand of the GPU
    arch
        Official architecture name of the GPU
    mem_total
        Total size of frame buffer memory.
    mem_reserved
        Reserved size of frame buffer memory.
    mem_used
        Used size of frame buffer memory.
    mem_free
        Free size of frame buffer memory.
    """
    name: str = ""
    brand: str = ""
    arch: str = ""

    mem_total: int = 0
    mem_reserved: int = 0
    mem_used: int = 0
    mem_free: int = 0

    fan_speed: float = 0.0
    usage: float = 0.0
    mem_usage: float = 0.0

    temperature: str = ""
    
    power_avg: str = ""

    clock_graphics: str = ""
    clock_sm: str = ""
    clock_mem: str = ""

    clock_max_graphics: str = ""
    clock_max_sm: str = ""
    clock_max_mem: str = ""


def parse_datasize(data: str) -> int:
    """
    Parse datasize string and return bytes.

    Returns -1 if fails to parse.
    """
    data = data.lower().strip()

    if not data:
        return 0

    # If no unit, assume bytes
    if data.isdigit():
        return int(data)
    
    elif data.endswith("gib"):
        return int(data.replace("mib", "")) * 1073741824

    elif data.endswith("mib"):
        return int(data.replace("mib", "")) * 1048576
    
    elif data.endswith("kib"):
        return int(data.replace("kib", "")) * 1024
    
    elif data.endswith("b"):
        return int(data.replace("b", ""))
    
    return -1

def parse_percentage(data: str) -> float:
    """
    Parse percentage and return normalized percentage.

    Return -1 if fails to parse.
    """

    if not data:
        return 0.0
    
    # If no unit, assume integer in [0, 100]
    if data.isdigit():
        return float(data) * 0.01
    
    if "%" in data:
        return float(data.replace("%", "")) * 0.01
    
    return -1.0


def get_driver_info() -> NvidiaDriverInfo:
    driver_info = NvidiaDriverInfo()

    p = subprocess.run(
        ("nvidia-smi", "--version"),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE
    )

    if p.returncode != 0:
        # TODO: logging
        return driver_info

    content = p.stdout.decode("utf-8")

    for line in content.strip().split("\n"):
        line = line.strip()

        if line.startswith("NVIDIA-SMI"):
            driver_info.smi_version = line.split(":")[1].strip()

        elif line.startswith("NVML"):
            driver_info.nvml_version = line.split(":")[1].strip()

        elif line.startswith("DRIVER"):
            driver_info.version = line.split(":")[1].strip()
        
        elif line.startswith("CUDA"):
            driver_info.cuda_version = line.split(":")[1].strip()

    return driver_info

def get_gpu_info() -> NvidiaGPUInfo:
    # TODO: use --query-gpu=... arg instead of parsing the big table
    gpu = NvidiaGPUInfo()

    p = subprocess.run(
        ("nvidia-smi", "--query"),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE
    )

    if p.returncode != 0:
        # TODO: logging
        return gpu

    content = p.stdout.decode("utf-8")

    category = ""
    subcategory = ""

    indent = "    "

    for line in content.strip().split("\n"):
        if line.startswith("Attached GPUs"):
            attached_gpus = line.split(":")[1].strip()

        elif line.startswith("GPU"):
            category = "GPU"

        if category == "GPU":
            line_type = "field"
            if line.startswith(indent) and not line[len(indent)].isspace():
                line_type = "subcategory"
                subcategory = ""

            line = line.strip()

            if line.startswith("Product Name"):
                gpu.name = line.split(":")[1].strip()

            elif line.startswith("Product Brand"):
                gpu.brand = line.split(":")[1].strip()
            
            elif line.startswith("Product Architecture"):
                gpu.arch = line.split(":")[1].strip()

            elif line.startswith("Fan Speed"):
                gpu.fan_speed = parse_percentage(line.split(":")[1].strip())

            if line.startswith("FB Memory Usage"):
                subcategory = "Memory"

            elif line.startswith("Utilization"):
                subcategory = "Utilization"

            elif line.startswith("Temperature"):
                subcategory = "Temperature"

            elif line.startswith("GPU Power Readings"):
                subcategory = "Power"

            elif line.startswith("Clocks"):
                subcategory = "Clocks"

            elif line.startswith("Max Clocks"):
                subcategory = "Max Clocks"

            if subcategory == "Memory":
                if line.startswith("Total"):
                    gpu.mem_total = parse_datasize(line.split(":")[1].strip())

                elif line.startswith("Reserved"):
                    gpu.mem_reserved = parse_datasize(line.split(":")[1].strip())

                elif line.startswith("Used"):
                    gpu.mem_used = parse_datasize(line.split(":")[1].strip())

                elif line.startswith("Free"):
                    gpu.mem_free = parse_datasize(line.split(":")[1].strip())

            elif subcategory == "Utilization":
                if line.startswith("GPU"):
                    gpu.usage = parse_percentage(line.split(":")[1].strip())

                elif line.startswith("Memory"):
                    gpu.mem_usage = parse_percentage(line.split(":")[1].strip())

            elif subcategory == "Temperature":
                if line.startswith("GPU Current Temp"):
                    gpu.temperature = line.split(":")[1].strip()

                    # TODO: Shutdown and slowdown target limits

            elif subcategory == "Power":
                if line.startswith("Average Power Draw"):
                    gpu.power_avg = line.split(":")[1].strip()

            elif subcategory == "Clocks":
                if line.startswith("Graphics"):
                    gpu.clock_graphics = line.split(":")[1].strip()

                elif line.startswith("SM"):
                    gpu.clock_sm = line.split(":")[1].strip()

                elif line.startswith("Memory"):
                    gpu.clock_mem = line.split(":")[1].strip()

            elif subcategory == "Max Clocks":
                if line.startswith("Graphics"):
                    gpu.clock_max_graphics = line.split(":")[1].strip()

                elif line.startswith("SM"):
                    gpu.clock_max_sm = line.split(":")[1].strip()

                elif line.startswith("Memory"):
                    gpu.clock_max_mem = line.split(":")[1].strip()

    return gpu


if __name__ == "__main__":
    from pprint import pprint
    pprint(get_driver_info())
    pprint(get_gpu_info())