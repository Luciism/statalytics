"""Application configuration related functionality."""

import json
import os
from typing import Any, Literal

from .common import REL_PATH


def merge_dicts(original_dict: dict, update_dict: dict) -> dict:
    """
    Merges two dictionaries together, updating existing
    keys with nested dictionaries merged recursively.

    :param original_dict: The original dictionary.
    :param update_dict: The dictionary to update the original with.
    :return dict: The merged dictionary.
    """
    result = original_dict.copy()

    for key, value in update_dict.items():
        if (
            key in result
            and isinstance(value, dict)
            and isinstance(result[key], dict)
        ):
            result[key] = merge_dicts(result[key], value)
            continue

        result[key] = value

    return result


class _Config:
    """Config class."""
    SHOULD_UPDATE_SUBSCRIPTION_ROLES = True
    DB_FILE_PATH = f'{REL_PATH}/database/core.db'

    def __init__(self) -> None:
        """Initialize the config class."""
        self._config_data: dict = None

    def __call__(self, path: str=None) -> dict | Any:
        config_data = self.data

        if path:
            for key in path.split('.'):
                config_data = config_data[key]

        return config_data

    def _load_config_data(self) -> dict:
        with open(f'{REL_PATH}/config.json', encoding="utf-8") as datafile:
            config_data: dict = json.load(datafile)

        # Load dev config
        if os.getenv('ENVIRONMENT').lower() == "development":
            with open(f'{REL_PATH}/config.dev.json', encoding="utf-8") as datafile:
                dev_config_data: dict = json.load(datafile)
            config_data = merge_dicts(config_data, dev_config_data)

        self._config_data = config_data
        return config_data

    def refresh(self) -> None:
        """Read the latest config data from the config file"""
        self._load_config_data()

    @property
    def data(self) -> dict:
        """The configuration data for the program"""
        if self._config_data is None:
            self._load_config_data()
        return self._config_data

    @staticmethod
    def loading_message() -> str:
        """Get the currently configured loading message."""
        return config('apps.bot.loading_message')

    @staticmethod
    def embed_color(embed_type: Literal["primary", "warning", "danger"]) -> int:
        """
        Get a base 16 integer for a specfied embed color.

        :param embed_type: The embed color type (primary, warning, or danger).
        """
        return int(config(f'apps.bot.embeds.{embed_type}_color'), base=16)

config = _Config()  # Globally used instance
"Global config instance."
