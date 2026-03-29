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

from PyQt6.QtGui import QPixmap
import miniprofiler

from llm_qlient import shared
from llm_qlient.core import log, path
from llm_qlient.core.types import JSONContent
from llm_qlient.core.models import Conversation, UserPersona, Character


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


class ContentManager:
    """
    JSON Content manager.
    """

    def __init__(self) -> None:
        self._prof = miniprofiler.Profiler(1)

    def load_conversations(self) -> None:
        with self._prof.profile("load"):
            convos_json = load_content(
                path.resolve("data", "content", "conversations.json"),
                path.resolve("data", "content", "conversations.json.template")
            )

            for convo in convos_json:
                shared.convos.append(Conversation.deserialize(convo))

        log.info(f"Loaded <fg.lightcyan>{len(shared.convos)}</> conversations in {log.t(self._prof['load'].last)}.")

    def save_conversations(self) -> None:
        with self._prof.profile("save"):
            save_content(
                path.resolve("data", "content", "conversations.json"),
                [convo.serialize() for convo in shared.convos]
            )

        log.info(f"Saved <fg.lightcyan>{len(shared.convos)}</> conversations in {log.t(self._prof['save'].last)}.")

    def load_user_personas(self) -> None:
        with self._prof.profile("load"):
            personas_json = load_content(
                path.resolve("data", "content", "user_personas.json"),
                path.resolve("data", "content", "user_personas.json.template")
            )

            for persona in personas_json:
                user_persona = UserPersona.deserialize(persona)

                pixmap = QPixmap(user_persona.avatar_path)

                if pixmap.isNull():
                    pixmap = shared.default_user_pixmap
                    log.warn(f"Avatar for <fg.yellow>{user_persona.ui_name}</> could't load at '<fg.darkgray>{user_persona.avatar_path}</>'")

                    user_persona.avatar_pixmap = pixmap.copy()

                else:
                    user_persona.avatar_pixmap = pixmap

                shared.personas.append(user_persona)

        log.info(f"Loaded <fg.lightcyan>{len(shared.personas)}</> user personas in {log.t(self._prof['load'].last)}.")

    def save_user_personas(self) -> None:
        with self._prof.profile("save"):
            save_content(
                path.resolve("data", "content", "user_personas.json"),
                [persona.serialize() for persona in shared.personas]
            )

        log.info(f"Loaded <fg.lightcyan>{len(shared.convos)}</> user personas in {log.t(self._prof['save'].last)}.")

    def load_characters(self) -> None:
        with self._prof.profile("load"):
            chars_json = load_content(
                path.resolve("data", "content", "characters.json"),
                path.resolve("data", "content", "characters.json.template")
            )

            for char in chars_json:
                character = Character.deserialize(char)

                # TODO: Global pixmap manager to cache pixmaps with same path, transforms, etc
                pixmap = QPixmap(character.avatar_path)

                if pixmap.isNull():
                    pixmap = shared.default_ai_pixmap
                    log.warn(f"Avatar for <fg.yellow>{character.ui_name}</> could't load at '<fg.darkgray>{character.avatar_path}</>'")

                    character.avatar_pixmap = pixmap.copy()

                else:
                    character.avatar_pixmap = pixmap

                shared.characters.append(character)

        log.info(f"Loaded <fg.lightcyan>{len(shared.convos)}</> characters in {log.t(self._prof['load'].last)}.")

    def save_characters(self) -> None:
        with self._prof.profile("save"):
            save_content(
                path.resolve("data", "content", "characters.json"),
                [char.serialize() for char in shared.characters]
            )

        log.info(f"Saved <fg.lightcyan>{len(shared.convos)}</> characters in {log.t(self._prof['save'].last)}.")

    def load_all(self) -> None:
        self.load_user_personas()
        self.load_characters()
        self.load_conversations()

    def save_all(self) -> None:
        self.save_user_personas()
        self.save_characters()
        self.save_conversations()