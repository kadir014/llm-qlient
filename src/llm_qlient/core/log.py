"""

    llm-qlient - Qt desktop client for interacting with local LLMs

    This file is a part of the llm-qlient
    project and distributed under MIT license.
    https://github.com/kadir014/llm-qlient

"""

from typing import IO

from datetime import datetime
from dataclasses import dataclass
from enum import IntEnum


# ANSI escape codes for terminal graphics modes
_ANSI_STYLES = {
    "fg.black": "\033[30m",
    "fg.darkgray": "\033[90m",
    "fg.lightgray": "\033[37m",
    "fg.white": "\033[97m",
    "fg.red": "\033[31m",
    "fg.orange": "\033[33m",
    "fg.yellow": "\033[93m",
    "fg.green": "\033[32m",
    "fg.blue": "\033[34m",
    "fg.cyan": "\033[36m",
    "fg.purple": "\033[35m",
    "fg.magenta": "\033[95m",
    "fg.lightred": "\033[91m",
    "fg.lightgreen": "\033[92m",
    "fg.lightblue": "\033[94m",
    "fg.lightcyan": "\033[96m",

    "bg.black": "\033[40m",
    "bg.darkgray": "\033[100m",
    "bg.lightgray": "\033[47m",
    "bg.white": "\033[107m",
    "bg.red": "\033[41m",
    "bg.orange": "\033[43m",
    "bg.yellow": "\033[103m",
    "bg.green": "\033[42m",
    "bg.blue": "\033[44m",
    "bg.cyan": "\033[46m",
    "bg.purple": "\033[45m",
    "bg.magenta": "\033[105m",
    "bg.lightred": "\033[101m",
    "bg.lightgreen": "\033[102m",
    "bg.lightblue": "\033[104m",
    "bg.lightcyan": "\033[106m",

    "reset": "\033[0m",
    "bold": "\033[01m",
    "underline": "\033[04m",
    "reverse": "\033[07m",
    "strike": "\033[09m"
}

def _render_color_template(text: str, no_color: bool = False) -> str:
    """
    Apply ANSI escape codes to templated string.

    Parameters
    ----------
    text
        Templated string to render
    no_color
        Whether to remove or render templates
    """

    rendered = text

    for style in _ANSI_STYLES:
        ansi = "" if no_color else _ANSI_STYLES[style]

        if style == "reset":
            style = "/"
        
        rendered = rendered.replace(f"<{style}>", ansi)

    return rendered


class LogLevel(IntEnum):
    """
    Logging severity level.

    Members
    -------
    DEBUG
        Negligible information for developers and diagnostics
    INFO
        Expected events.
    WARNING
        Something unexpected happened, but the app can continue executing
    ERROR
        Something major happened, but the app can continue executing
    FATAL
        Something unrecoverable happened, app needs to terminate
    """

    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    FATAL = 4


@dataclass(frozen=True)
class LogTarget:
    """
    Logging output target.

    Attributes
    ----------
    stream
        Output stream to write to
    min_level
        Minimum severity required to emit a log
    colored
        Whether to use ANSI escape codes or not
    end
        String to append to after logging message
    indent_lines
        Indent multiple lines of log message to same level
    use_unicode
        Use unicode emojis for indicators
    use_indicators
        Use indicator character prefixes for each log 
    """

    stream: IO
    min_level: LogLevel = LogLevel.INFO
    colored: bool = False
    end: str = "\n"
    indent_lines: bool = True
    use_unicode: bool = False
    use_indicators: bool = False


def log(level: LogLevel, message: str) -> None:
    """
    Log a message to all existing target streams.

    Parameters
    ----------
    level
        Severity level
    message
        Log message
    """

    if len(targets) == 0:
        return
    
    ind_emojis = {
        LogLevel.DEBUG: "\u2699\ufe0f",
        LogLevel.INFO: "\u2714\ufe0f",
        LogLevel.WARNING: "\u26a0\ufe0f",
        LogLevel.ERROR: "\u274c\ufe0f",
        LogLevel.FATAL: "\u2620\ufe0f"
    }

    ind_nonemojis = {
        LogLevel.DEBUG: "<bold><fg.lightcyan>+</>",
        LogLevel.INFO: "<bold><fg.lightgreen>i</>",
        LogLevel.WARNING: "<bold><fg.orange>!</>",
        LogLevel.ERROR: "<bold><fg.magenta>X</>",
        LogLevel.FATAL: "<bold><fg.lightred>#</>"
    }

    gap = {
        LogLevel.DEBUG: 2,
        LogLevel.INFO: 3,
        LogLevel.WARNING: 0,
        LogLevel.ERROR: 2,
        LogLevel.FATAL: 2
    }

    level_colors = {
        LogLevel.DEBUG: "<fg.lightcyan>",
        LogLevel.INFO: "<fg.lightgreen>",
        LogLevel.WARNING: "<fg.orange>",
        LogLevel.ERROR: "<fg.magenta>",
        LogLevel.FATAL: "<fg.lightred>"
    }

    now = datetime.today().strftime("%H:%M:%S")

    for target in targets:
        if level < target.min_level:
            continue

        if target.use_indicators:
            if target.use_unicode:
                indicator = ind_emojis[level]
            else:
                indicator = ind_nonemojis[level]
            indicator += " "
        else:
            indicator = "" 

        log_prefix = f"{indicator}{level_colors[level]}[{level.name}]</>{' ' * gap[level]} │ <fg.darkgray>{now}</> │ "
        pure_log_prefix = _render_color_template(log_prefix, no_color=True)
        color_log_prefix = _render_color_template(log_prefix, no_color=False)
        rendered_log_prefix = color_log_prefix if target.colored else pure_log_prefix

        rendered_message = message
        if target.indent_lines:
            indent = len(pure_log_prefix)
            rendered_message = rendered_message.replace("\n", f"\n{' ' * indent}")

        rendered_message = _render_color_template(rendered_message, no_color=not target.colored)
        
        log_message = rendered_log_prefix + rendered_message

        print(
            log_message,
            end=target.end,
            file=target.stream
        )

def debug(message: str) -> None:
    """
    Issue a debug log.

    Parameters
    ----------
    message
        Debug message
    """

    log(LogLevel.DEBUG, message)

def info(message: str) -> None:
    """
    Issue an information log.

    Parameters
    ----------
    message
        Information message
    """

    log(LogLevel.INFO, message)

def warn(message: str) -> None:
    """
    Issue a warning log.

    Parameters
    ----------
    message
        Warning message
    """

    log(LogLevel.WARNING, message)

def error(message: str) -> None:
    """
    Issue an error log.

    Parameters
    ----------
    message
        Error message
    """

    log(LogLevel.ERROR, message)

def fatal(message: str) -> None:
    """
    Issue a fatal log.

    Parameters
    ----------
    message
        Fatal message
    """

    log(LogLevel.FATAL, message)


targets: set[LogTarget] = set()


__all__ = (
    "LogLevel",
    "LogTarget",
    "log",
    "debug",
    "info",
    "warn",
    "error",
    "fatal",
    "targets"
)