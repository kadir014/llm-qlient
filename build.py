"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

import os
import subprocess
from pathlib import Path


ROOT = Path.cwd()


def log(msg: str) -> None:
    print(f"\n[BUILDER] {msg}\n")

def run(*cmd: str) -> int:
    if isinstance(cmd, (tuple, list)):
        cmd = " ".join(cmd)
    
    return subprocess.run(cmd, shell=True).returncode


def remove_spec() -> None:
    """
    Remove spec file from previous builds so it doesn't
    conflict with current parameters.
    """

    if os.path.exists(ROOT / "__main__.spec"):
        os.remove(ROOT / "__main__.spec")


def collect_hidden_imports() -> str:
    """
    Unfortunately PyInstaller can't collect dynamic imports.

    So we have to manually add them using the '--hidden-import' parameters.
    """

    hiddens = []

    for _, dirs, _ in os.walk(ROOT / "src" / "llm_qlient" / "ui" / "pages"):
        for dir in dirs:
            if dir in {"__pycache__",}: continue
            hiddens.append(f"--hidden-import llm_qlient.ui.pages.{dir}.view")
            log(f"Collected hidden import: {dir}")

        # Only one level
        break

    return " ".join(hiddens)


def main() -> None:
    remove_spec()

    hiddens = collect_hidden_imports()

    run(
        "pyinstaller",
        "--onedir",
        "src/llm_qlient/__main__.py",
        #"--paths ./.venv/Lib/site-packages",
        "--paths src",
        hiddens,
        "--add-data data;data",
        "--distpath ./pyinstaller_dist",
        "--workpath ./pyinstaller_build",
        "--noconfirm",
        "--clean",
    )


if __name__ == "__main__":
    main()