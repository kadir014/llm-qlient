"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

import os
import json
from pathlib import Path


def ensure_content(path: Path, template: Path) -> None:
    """
    Ensure content JSON exists with the given template.
    
    Parameters
    ----------
    path
        Path to content JSON
    template
        Path to content JSON template
    """

    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as file:
            with open(template, "r", encoding="utf-8") as tmpl_f:
                file.write(tmpl_f.read())

def load_content(path: Path, template: Path) -> dict | list[dict]:
    """
    Load content JSON. Create it from template if it doesn't exist.
    
    Parameters
    ----------
    path
        Path to content JSON
    template
        Path to content JSON template
    """

    ensure_content(path, template)

    with open(path, "r", encoding="utf-8") as file:
        content = file.read()

    return json.loads(content)

def save_content(path: Path, content: dict | list[dict]) -> None:
    """
    Save content to JSON.

    Parameters
    ----------
    path
        Path to content JSON
    content
        Content to save
    """

    with open(path, "w", encoding="utf-8") as file:
        file.write(json.dumps(content))