"""

    llm-qlient  -  Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.
    https://github.com/kadir014/llm-qlient

"""

# Easy auto-installation & runner script

import os
import sys
import subprocess


PYTHON = sys.executable
if not PYTHON:
    PYTHON = "python"


def download_llama_cpp_python() -> None:
    # llama-cpp-python supported backends
    # https://github.com/JamePeng/llama-cpp-python?tab=readme-ov-file#supported-backends
    print(
        "\n"
        "Do you want GPU acceleration? (for the llama-cpp-python build)\n"
        "0: None, build for CPU (default)\n"
        "1: Nvidia CUDA\n"
        "2: AMD ROCm"
    )
    gpu_accel = input("(Leave blank for default)").strip().lower()

    if gpu_accel == "1":
        os.environ["CMAKE_ARGS"] = "-DGGML_CUDA=on"
        print("Nvidia CUDA support is chosen")

    elif gpu_accel == "2":
        os.environ["CMAKE_ARGS"] = "-DGGML_HIP=ON -DGPU_TARGETS=gfx1030"
        print("AMD ROCm support is chosen")

    else:
        os.environ["CMAKE_ARGS"] = "-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS"
        print("CPU support is chosen")

    subprocess.run("uv pip install --upgrade \"llama-cpp-python @ git+https://github.com/JamePeng/llama-cpp-python.git\"")


if __name__ == "__main__":
    print("Python version:")
    subprocess.run(f"\"{PYTHON}\" --version", shell=True)
    print()

    subprocess.run(f"\"{PYTHON}\" -m pip install --upgrade uv", shell=True)

    download_llama_cpp_python()

    subprocess.run("uv run main --debug")