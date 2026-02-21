"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

# Easy auto-installation & runner script
#
# For the first run:
#   1. Installs uv
#   2. Setups environment
#   3. Installs llama-cpp-python (JamePeng's fork)
#   4. Runs the app
#
# For the subsequent runs, the installation will not occur unless opted.

import os
import sys
import subprocess
import platform
import argparse


PYTHON = sys.executable
if not PYTHON:
    PYTHON = "python"

args: argparse.Namespace


def normalize(string: str) -> str:
    return string.strip().lower()

def log(msg: str) -> None:
    print(f"\n[RUNNER] {msg}\n")

def run(cmd: str) -> int:
    return subprocess.run(cmd, shell=True).returncode


def install_llama_cpp_python() -> None:
    # llama-cpp-python supported backends for JamePeng's fork
    # https://github.com/JamePeng/llama-cpp-python?tab=readme-ov-file#supported-backends
    print(
        "\n"
        "[RUNNER] Do you want GPU acceleration? (for the llama-cpp-python build)\n"
        "         0: None, build for CPU (default)\n"
        "         1: Nvidia CUDA\n"
        "         2: AMD ROCm"
    )
    gpu_accel = normalize(input("(Leave blank for default)"))

    if gpu_accel in {"1", "one", "cuda", "nvidia"}:
        os.environ["CMAKE_ARGS"] = "-DGGML_CUDA=on"
        log("Nvidia CUDA support is chosen")

    elif gpu_accel in {"2", "two", "rocm", "amd"}:
        os.environ["CMAKE_ARGS"] = "-DGGML_HIP=ON -DGPU_TARGETS=gfx1030"
        log("AMD ROCm support is chosen")

    else:
        os.environ["CMAKE_ARGS"] = "-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS"
        log("CPU support is chosen")

    force_arg = "--force-reinstall" if args.force_reinstall else ""
    dist = "llama-cpp-python @ git+https://github.com/JamePeng/llama-cpp-python.git"
    run(f"uv pip install --upgrade {force_arg} \"{dist}\"")


def is_installed(module: str) -> bool:
    """
    Check if the given module is installed in current uv environment.

    Parameters
    ----------
    module
        Name of the module to check
    """
    out = subprocess.check_output("uv pip list").decode("utf-8")
    return normalize(module) in normalize(out)


def main() -> None:
    """ Installer & runner entry point. """

    log(f"Python: {platform.python_version()} - {platform.python_compiler()}")

    run(f"\"{PYTHON}\" -m pip install --upgrade uv")

    run("uv venv --no-clear")

    if not args.no_install and (not is_installed("llama-cpp-python") or args.force_reinstall):
        log("llama-cpp-python is not found, installing.")
        install_llama_cpp_python()
    else:
        log("llama-cpp-python is found, skipping installing.")

    run("uv run main --debug")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="run.py",
        description="Easy auto installation & runner script"
    )

    parser.add_argument(
        "--force-reinstall",
        help="Force reinstall llama-cpp-python even if it exists.",
        action="store_true"
    )

    parser.add_argument(
        "--no-install",
        help="Don't install llama-cpp-python even if it's not found. "
             "This overwrites any installation related conditions.",
        action="store_true"
    )

    args = parser.parse_args()

    main()