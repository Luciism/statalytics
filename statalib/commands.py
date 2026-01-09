from dataclasses import dataclass
import json
from typing import Any, Literal, overload

from .common import REL_PATH

class InvalidCommandsFileError(Exception):
    ...

class CommandNotFoundError(Exception):
    ...

try:
    with open(f"{REL_PATH}/commands.json") as cmd_file:
        data: dict[str, Any] = json.load(cmd_file)

        ARG_DEFAULTS: dict[str, dict[str, str]] = data["argument_defaults"]
        COMMANDS: list[dict[str, Any]] = data["commands"]
except (KeyError, json.JSONDecodeError, FileNotFoundError) as e:
    raise InvalidCommandsFileError("commands.json file missing or invalid") from e


@dataclass
class CommandArgument:
    name: str
    description: str | None
    autocomplete: str | None

    def as_dict(self) -> dict[str, str | None]:
        return {
            "name": self.name,
            "description": self.description,
            "autocomplete": self.autocomplete
        }

    @staticmethod
    def build(arg: str | dict[str, str]) -> 'CommandArgument':
        if isinstance(arg, str):
            # Defaults may or may not exist
            defaults = ARG_DEFAULTS.get(arg, {})

            return CommandArgument(
                arg,
                defaults.get("description"),
                defaults.get("autocomplete")
            )


        defaults = ARG_DEFAULTS.get(arg["name"], {})

        return CommandArgument(
            arg["name"],
            arg.get("description", defaults.get("description")),
            arg.get("autocomplete", defaults.get("autocomplete")),
        )


@dataclass
class CommandAllowedInstalls:
    guilds: bool
    users: bool

    def as_dict(self) -> dict[str, bool]:
        return {
            "guilds": self.guilds,
            "users": self.users
        }


@dataclass
class CommandAllowedContexts:
    guilds: bool
    dms: bool
    private_channels: bool

    def as_dict(self) -> dict[str, bool]:
        return {
            "guilds": self.guilds,
            "dms": self.dms,
            "private_channels": self.private_channels
        }

@dataclass
class Command:
    id: str
    name: str
    description: str
    parent: str | None
    cooldown: bool
    arguments: list[CommandArgument]
    installs: CommandAllowedInstalls
    contexts: CommandAllowedContexts
 
    def argument_map(self) -> dict[str, str]:
        return {
            arg.name: arg.description for arg in self.arguments if arg.description
        }

    def format(self) -> str:
        if self.parent:
            return f"/{self.parent} {self.name}"

        return f"/{self.name}"

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "parent": self.parent,
            "cooldown": self.cooldown,
            "installs": self.installs.as_dict(),
            "contexts": self.contexts.as_dict(),
            "arguments": [arg.as_dict() for arg in self.arguments]
        }

    @staticmethod
    @overload
    def build(cmd: dict[str, Any]) -> 'Command':
        ...

    @staticmethod
    @overload
    def build(cmd: dict[str, Any], silent_fail: Literal[False]) -> 'Command':
        ...

    @staticmethod
    @overload
    def build(cmd: dict[str, Any], silent_fail: Literal[True]) -> 'Command | None':
        ...

    @staticmethod
    def build(cmd: dict[str, Any], silent_fail: bool=False) -> 'Command | None':
        try:
            if cmd.get("name") is None:
                cmd["name"] = cmd["id"]

            return Command(
                id=cmd["id"],
                name=cmd["name"],
                description=cmd.get("description", ""),
                parent=cmd.get("parent"),
                cooldown=cmd.get("cooldown", True),
                arguments=[
                    CommandArgument.build(arg)
                    for arg in cmd.get("arguments", [])
                ],
                installs=CommandAllowedInstalls(
                    guilds=cmd.get("installs", {}).get("guilds", True),
                    users=cmd.get("installs", {}).get("users", True),
                ),
                contexts=CommandAllowedContexts(
                    guilds=cmd.get("contexts", {}).get("guilds", True),
                    dms=cmd.get("contexts", {}).get("dms", True),
                    private_channels=cmd.get("contexts", {}).get("private_channels", True),
                )
            )
        except KeyError as exc:
            if silent_fail:
                return
            raise InvalidCommandsFileError from exc


def get_command(command_id: str) -> Command:
    """
    Get the command metadata associated with a given command ID.

    :param command_id: The ID of the command to retrieve metadata for.
    :raises CommandNotFoundError: The command does not exist in `commands.json`.
    :raises InvalidCommandsFileError: There is an issue with the `commands.json` file.
    """
    try:
        cmd = [cmd for cmd in COMMANDS if cmd["id"] == command_id][0]
    except IndexError:
        raise CommandNotFoundError(f"No command with ID '{command_id}'")
    except KeyError as exc:
        raise InvalidCommandsFileError("Invalid command file") from exc

    return Command.build(cmd)

def get_all_commands() -> list[Command]:
    """
    Load all commands into models.

    :raises KeyError: 
    """
    return [ Command.build(cmd) for cmd in COMMANDS ]
