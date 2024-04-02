import json
from typing import Any

from .common import REL_PATH


class _Config:
    def __init__(self) -> None:
        self._config_data: dict = None

    def __call__(self, path: str=None) -> dict | Any:
        config_data = self.data

        if path:
            for key in path.split('.'):
                config_data = config_data[key]

        return config_data

    def _load_config_data(self) -> dict:
        with open(f'{REL_PATH}/config.json', 'r') as datafile:
            config_data: dict = json.load(datafile)

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


config = _Config()  # Globally used instance
