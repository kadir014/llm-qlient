"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

from dataclasses import dataclass

import psutil

from llm_qlient.core.nvidia_info import get_gpu_info


@dataclass(frozen=True)
class UtilizationSummary:
    """
    Utilization values of important system resources.

    Attributes
    ----------
    cpu
        System-wide CPU utilization percentage in range [0, 1]
    gpu
        GPU utilization percentage in range [0, 1]
    ram_used
        Used memory amount in bytes
    ram_total
        Total memory amount in bytes
    ram_percent
        Memory utilization percentage in range [0, 1]
    vram_used
        Used video memory amount in bytes
    vram_total
        Total video memory amount in bytes
    vram_percent
        Video memory utilization percentage in range [0, 1]
    """
    cpu: float
    gpu: float
    ram_used: int
    ram_total: int
    ram_percent: float
    vram_used: int
    vram_total: int
    vram_percent: float

def get_utilization_summary() -> UtilizationSummary:
    cpu = psutil.cpu_percent() * 0.01
    mem = psutil.virtual_memory()
    gpu = get_gpu_info()

    mem_percent = 0 if mem.total == 0 else mem.used / mem.total
    gpu_mem_percent = 0 if gpu.mem_total == 0 else gpu.mem_used / gpu.mem_total

    return UtilizationSummary(
        cpu,
        gpu.usage,
        mem.used,
        mem.total,
        mem_percent,
        gpu.mem_used,
        gpu.mem_total,
        gpu_mem_percent
    )