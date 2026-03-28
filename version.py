"""

    llm-qlient • Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.

    Repository: https://github.com/kadir014/llm-qlient
    Issues:     https://github.com/kadir014/llm-qlient/issues

"""

import sys
import re
from pathlib import Path


ROOT = Path.cwd()


def match_and_replace(path: Path, pattern: str, replace: str) -> None:
    content = path.read_text(encoding="utf-8")

    content = re.compile(pattern).sub(replace, content)

    path.write_text(content, encoding="utf-8")


def main() -> None:
    if len(sys.argv) > 1:
        new_version = sys.argv[1]
    else:
        raise ValueError("Version string is needed as an argument.")
    
    PATTERNS = {
        "pyproject.toml": {
            "pattern": r'(version\s*=\s*")[^"]*(")',
            "replace": rf'\g<1>{new_version}\g<2>'
        },
        "src/llm_qlient/shared.py": {
            "pattern": r'(__version__\s*=\s*")[^"]*(")',
            "replace": rf'\g<1>{new_version}\g<2>'
        },
        "README.md": {
            "pattern": r'(version-)(.+)(-[^-"]+)',
            "replace": rf'\g<1>{new_version.replace("-", "--")}\g<3>'
        }
    }

    for path, patterns in PATTERNS.items():
        match_and_replace(ROOT / path, patterns["pattern"], patterns["replace"])


if __name__ == "__main__":
    main()