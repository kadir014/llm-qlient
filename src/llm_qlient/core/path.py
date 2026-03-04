"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

import os
import sys
from pathlib import Path


def resolve(*children: str) -> Path:
    """ Resolve path in the base directory regardless of freezer. """

    if getattr(sys, "frozen", False):
        base = sys._MEIPASS

    else:
        base = os.getcwd()

    return (Path(base) / Path(*children)).resolve()