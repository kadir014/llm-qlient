"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

from typing import Any

from pathlib import Path


PathLike = str | bytes | Path

JSONContent = dict | list[dict]

SettingsDict = dict[str, Any]