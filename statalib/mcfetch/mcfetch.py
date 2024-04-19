import json
from base64 import b64decode

import requests


class FetchPlayer:
    def __init__(
        self,
        name: str=None,
        uuid: str=None,
        requests_obj=requests
    ):
        """
        Initializes a FetchPlayer object with a name and/or uuid.

        Args:
            name (str, optional): The player's name. Defaults to None.
            uuid (str, optional): The player's uuid. Defaults to None.
            requests_obj (module, optional): The requests module or a compatible
            object to use for making HTTP requests. Defaults to the requests module.

        Raises:
            AssertionError: If both name and uuid are None or if both are not None.
        """
        assert (name, uuid).count(None) == 1
        self._name = name
        self._uuid = uuid

        self._pretty_name = None

        self._skin_url = None
        self._skin_texture = None

        self._player_exists = True
        self._has_loaded_by_uuid = False

        self._requests_obj = requests_obj


    @property
    def name(self) -> str | None:
        """Returns the player's pretty name."""
        if self._pretty_name is None:
            if self._name is None:
                self._load_by_uuid()
            else:
                self._load_by_name()
        return self._pretty_name


    @property
    def uuid(self) -> str | None:
        """Returns the player's uuid."""
        self._load_by_name()
        return self._uuid


    @property
    def skin_url(self) -> str | None:
        """Returns the player's skin url."""
        if self._skin_url is None:
            if self._uuid is None:
                self._load_by_name()
            self._load_by_uuid()
        return self._skin_url


    @property
    def skin_texture(self) -> str | None:
        """Returns the player's skin texture images as bytes."""
        if self._skin_texture is None:
            if self.skin_url is None:
                return None
            self._skin_texture = self._requests_obj.get(self.skin_url).content
        return self._skin_texture


    def _load_by_name(self):
        if self._uuid is None and self._player_exists:
            data: dict = self._requests_obj.get(
                f"https://api.mojang.com/users/profiles/minecraft/{self._name}").json()

            self._uuid = data.get("id")
            self._pretty_name = data.get("name")

            if self._pretty_name is None:
                self._player_exists = False


    def _load_by_uuid(self):
        if (not self._has_loaded_by_uuid) and self._player_exists:
            data: dict = self._requests_obj.get(
                f"https://sessionserver.mojang.com/session/minecraft/profile/{self._uuid}"
            ).json()

            name = data.get("name")

            # Stops future requests
            if name is None:
                self._player_exists = False
                return
            self._pretty_name = name

            # Get skin url from base64 string
            for item in data.get('properties', []):
                if item.get('name') == 'textures':
                    encoded_str = item.get('value', '')
                    textures: dict = json.loads(b64decode(encoded_str) or '{}')

                    self._skin_url = textures.get('textures', {}).get('SKIN', {}).get('url')
                    break


class FetchPlayer2(FetchPlayer):
    def __init__(self, identifier: str, requests_obj=requests):
        """
        Wrapper for the `FetchPlayer` class that allows either a username or uuid to
        be passed as the `identifier` parameter. Whether the identifier is a username
        or uuid will be determined by its length.

        Args:
            identifier (str, optional): The player's username or uuid.
            requests_obj (module | class, optional): The requests module or a compatible
            object to use for making HTTP requests. Defaults to the requests module.
        """
        if len(identifier) > 16:
            super().__init__(uuid=identifier, requests_obj=requests_obj)
        else:
            super().__init__(name=identifier, requests_obj=requests_obj)
