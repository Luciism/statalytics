import json
from base64 import b64decode

from aiohttp import ClientSession
from aiohttp_client_cache import CacheBackend, CachedSession


class AsyncFetchPlayer:
    def __init__(
        self,
        name: str=None,
        uuid: str=None,
        cache_backend: CacheBackend=None
    ):
        """
        Initializes a FetchPlayer object with a name and/or uuid.

        Args:
            name (str, optional): The player's name. Defaults to None.
            uuid (str, optional): The player's uuid. Defaults to None.
            cache_backend (class, optional): The backend used for caching
            responses, if `None`, caching won't be used.

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

        self.cache_backend = cache_backend


    @property
    async def name(self) -> str | None:
        """Returns the player's pretty name."""
        if self._pretty_name is None:
            if self._name is None:
                await self._load_by_uuid()
            else:
                await self._load_by_name()
        return self._pretty_name


    @property
    async def uuid(self) -> str | None:
        """Returns the player's uuid."""
        await self._load_by_name()
        return self._uuid


    @property
    async def skin_url(self) -> str | None:
        """Returns the player's skin url."""
        if self._skin_url is None:
            if self._uuid is None:
                await self._load_by_name()
            await self._load_by_uuid()
        return self._skin_url


    @property
    async def skin_texture(self) -> str | None:
        """Returns the player's skin texture image as bytes."""
        if self._skin_texture is None:
            skin_url = await self.skin_url
            if skin_url is None:
                return None
            texture = (await self._make_request(skin_url)).content
            self._skin_texture = await texture.read()

        return self._skin_texture


    async def _make_request(self, url: str):
        if self.cache_backend is None:
            async with ClientSession() as session:
                data = await session.get(url)
        else:
            async with CachedSession(cache=self.cache_backend) as session:
                data = await session.get(url)
        return data


    async def _load_by_name(self):
        if self._uuid is None and self._player_exists:
            data: dict = await (await self._make_request(
                f"https://api.mojang.com/users/profiles/minecraft/{self._name}"
            )).json()

            self._uuid = data.get("id")
            self._pretty_name = data.get("name")

            if self._pretty_name is None:
                self._player_exists = False


    async def _load_by_uuid(self):
        if (not self._has_loaded_by_uuid) and self._player_exists:
            data: dict = await (await self._make_request(
                f"https://sessionserver.mojang.com/session/minecraft/profile/{self._uuid}"
            )).json()

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

            self._has_loaded_by_uuid == True


class AsyncFetchPlayer2(AsyncFetchPlayer):
    def __init__(
        self,
        identifier: str,
        cache_backend: CacheBackend=None
    ):
        """
        Wrapper for the `FetchPlayer` class that allows either a username or uuid to
        be passed as the `identifier` parameter. Whether the identifier is a username
        or uuid will be determined by its length.

        Args:
            identifier (str, optional): The player's username or uuid.
            cache_backend (class, optional): The backend used for caching
            responses, if `None`, caching won't be used.
        """
        if len(identifier) > 16:
            super().__init__(uuid=identifier, cache_backend=cache_backend)
        else:
            super().__init__(name=identifier, cache_backend=cache_backend)
