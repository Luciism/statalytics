from dataclasses import dataclass
import json
from typing import Any, Literal, overload

from .common import REL_PATH


@dataclass
class CommandArgument:
    name: str
    description: str | None
    autocomplete: str | None

@dataclass
class CommandAllowedInstalls:
    guilds: bool
    users: bool

    @property
    def dict(self) -> dict[str, bool]:
        return {
            "guilds": self.guilds,
            "users": self.users
        }


@dataclass
class CommandAllowedContexts:
    guilds: bool
    dms: bool
    private_channels: bool

    @property
    def dict(self) -> dict[str, bool]:
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
            arg.name: arg.description or "" for arg in self.arguments
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
                    CommandArgument(
                        name=arg["name"],
                        description=arg.get("description"),
                        autocomplete=arg.get("autocomplete")
                    )
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

class InvalidCommandsFileError(Exception):
    ...

class CommandNotFoundError(Exception):
    ...

try:
    with open(f"{REL_PATH}/commands.json") as cmd_file:
        COMMANDS: list[dict[str, Any]] = json.load(cmd_file)["commands"]
except (KeyError, json.JSONDecodeError, FileNotFoundError) as e:
    raise InvalidCommandsFileError("commands.json file missing or invalid") from e


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
