import requests


class FetchPlayer:
    def __init__(self, name: str=None, uuid: str=None, requests_obj=requests):
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

        self.requests_obj = requests_obj


    @property
    def uuid(self) -> str | None:
        """
        Returns the player's uuid.

        Returns:
            str: The player's uuid.
        """
        self._load_by_name()
        return self._uuid


    @property
    def name(self) -> str | None:
        """
        Returns the player's pretty name.

        Returns:
            str: The player's pretty name.
        """
        if self._pretty_name is None:
            if self._name is None:
                self._load_by_uuid()
            else:
                self._load_by_name()
        return self._pretty_name


    def _load_by_name(self):
        if self._uuid is None:
            data = self.requests_obj.get(
                f"https://api.mojang.com/users/profiles/minecraft/{self._name}",
                headers={'Content-Type':'application/json'}
            ).json()

            self._uuid = data.get("id")
            self._pretty_name = data.get("name")


    def _load_by_uuid(self):
        if self._pretty_name is None:
            data = self.requests_obj.get(
                f"https://sessionserver.mojang.com/session/minecraft/profile/{self._uuid}",
                headers={'Content-Type':'application/json'}
            ).json()

            self._pretty_name = data.get("name")
