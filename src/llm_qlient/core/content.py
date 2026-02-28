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

import miniprofiler

from llm_qlient import shared
from llm_qlient.core import log
from llm_qlient.core.types import JSONContent
from llm_qlient.core.models import Conversation, UserPersona


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

def load_content(path: Path, template: Path) -> JSONContent:
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

def save_content(path: Path, content: JSONContent) -> None:
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


def t(dt: float) -> str:
    """
    Format delta time for logging.

    TODO: Better name? Also move to another module.

    Parameters
    ----------
    dt
        Elapsed time in seconds
    """

    dt = float(dt)
    unit = "s"

    # Minutes
    if dt >= 3600.0:
        dt /= 3600.0
        unit = "h"

    elif dt >= 60.0:
        dt /= 60.0
        unit = "m"

    else:
        # Milliseconds
        if dt <= 1.0:
            dt *= 1000.0
            unit = "ms"

        # Microseconds
        if dt <= 1.0:
            dt *= 1000.0
            unit = "us"

    return f"<fg.lightcyan>{round(dt, 4)}{unit}</>"


class ContentManager:
    """
    JSON Content manager.
    """

    def __init__(self) -> None:
        self.root = Path.cwd()

        self._prof = miniprofiler.Profiler(1)

    def load_conversations(self) -> None:
        with self._prof.profile("load"):
            convos_json = load_content(
                self.root / "data" / "content" / "conversations.json",
                self.root / "data" / "content" / "conversations.json.template"
            )

            for convo in convos_json:
                shared.convos.append(Conversation.deserialize(convo))

        log.info(f"Loaded <fg.lightcyan>{len(shared.convos)}</> conversations in {t(self._prof['load'].last)}.")

    def save_conversations(self) -> None:
        with self._prof.profile("save"):
            save_content(
                self.root / "data" / "content" / "conversations.json",
                [convo.serialize() for convo in shared.convos]
            )

        log.info(f"Saved <fg.lightcyan>{len(shared.convos)}</> conversations in {t(self._prof['save'].last)}.")

    def load_user_personas(self) -> None:
        with self._prof.profile("load"):
            personas_json = load_content(
                self.root / "data" / "content" / "user_personas.json",
                self.root / "data" / "content" / "user_personas.json.template"
            )

            for persona in personas_json:
                shared.personas.append(UserPersona.deserialize(persona))

        s = f"{round(self._prof['load'].last * 1000.0, 3)}ms"
        log.info(f"Loaded <fg.lightcyan>{len(shared.personas)}</> user personas in {t(self._prof['load'].last)}.")

    def save_user_personas(self) -> None:
        with self._prof.profile("save"):
            save_content(
                self.root / "data" / "content" / "user_personas.json",
                [persona.serialize() for persona in shared.personas]
            )

        log.info(f"Loaded <fg.lightcyan>{len(shared.convos)}</> user personas in {t(self._prof['save'].last)}.")

    def load_all(self) -> None:
        self.load_conversations()
        self.load_user_personas()

    def save_all(self) -> None:
        self.save_conversations()
        self.save_user_personas()