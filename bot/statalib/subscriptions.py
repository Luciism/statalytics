import json
import sqlite3
from datetime import datetime

from .functions import get_timestamp, get_config, REL_PATH


def get_all_subscription_data(discord_id: int) -> tuple | None:
    """
    Returns all columns of subscription data for a user
    :param discord_id: the discord id of the respective user
    """
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM subscriptions WHERE discord_id = {discord_id}")
        subscription_data = cursor.fetchone()

    return subscription_data or None


def get_package_data(discord_id: int) -> dict:
    """
    Returns package data dict for a user
    :param discord_id: the discord id of the respective user
    """
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()

        cursor.execute(
            f"SELECT package_data FROM subscriptions WHERE discord_id = {discord_id}")
        package_data = cursor.fetchone()

    if package_data and package_data[0]:
        package_data: dict = json.loads(package_data[0])
        # sort by timestamp purchased
        return dict(sorted(package_data.items(), key=lambda x: -float(x[0])))
    return {}


def is_booster(discord_id: int) -> bool:
    """
    Returns a bool if the user has booster premium or not
    :param discord_id: the discord id of the respective user
    """
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT booster FROM subscriptions WHERE discord_id = {discord_id}")
        booster = cursor.fetchone()

    if booster:
        if booster[0] == 1:
            return True
    return False


def get_subscription(
    discord_id: int=None,
    package_data: dict[str, dict]=None,
    include_booster: bool=True,
    get_expiry: bool=False
) -> str | tuple | None:
    """
    Returns a users subscription data from subscription database\n
    Either `discord_id` or `package_data` must be set\n
    `is_booster` requires `discord_id`

    :param discord_id: the discord id of the respective user
    :param package_data: optionally pass custom package_data
    :param include_booster: whether or not to include booster premium
    :param get_expiry: whether or not to return the package expiry timestamp
    """
    assert (discord_id, package_data).count(None) == 1

    if discord_id and include_booster and is_booster(discord_id):
        return 'pro'

    if package_data is None:
        package_data = get_package_data(discord_id)

    if package_data:
        for data in package_data.values():
            expires = data.get('expires')
            package = data.get('package')

            values = (package, expires) if get_expiry else package

            if expires != -1:
                # check if package is still valid
                now = datetime.utcnow().timestamp()
                if expires > now:
                    return values
            else:
                return values
    return None


def set_package_data(discord_id: int, package_data: dict):
    """
    Sets a user's package data column to specified package data dictionary
    :param discord_id: the discord id of the respective user
    :param package_data: the package data to be set for the user
    """
    subscription_data = get_subscription(
        package_data=package_data, get_expiry=True, include_booster=False)

    if subscription_data:
        package, expires = subscription_data
        current_package = f'{package}:{expires}'
    else:
        current_package = None

    package_data_str = json.dumps(package_data)

    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM subscriptions WHERE discord_id = {discord_id}")
        current_subscription = cursor.fetchone()

        if current_subscription:
            cursor.execute(
                'UPDATE subscriptions '
                'SET current_package = ?, package_data = ? '
                'WHERE discord_id = ?',
                (current_package, package_data_str, discord_id))
        else:
            cursor.execute(
                'INSERT INTO subscriptions '
                '(discord_id, current_package, package_data) '
                'VALUES (?, ?, ?)',
                (discord_id, current_package, package_data_str))


def get_all_of_package(where_clause: str) -> list:
    """
    Selects all row from subscriptions table of a certain package type
    :param package: the package to select
    """
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()

        cursor.execute(
            f"SELECT * FROM subscriptions WHERE {where_clause}")
        subscription_data = cursor.fetchall()

    return subscription_data


def set_current_package(discord_id: int, package: str=None,
                        expiry: int=None) -> None:
    """
    Sets a user's current package column to specified package
    :param discord_id: the discord id of the respective user
    :param package: the current package to set for the user
    :param expiry: the expiry to set with the current package
    if package or expiry is `None`, current_package will get
    set to `None`
    """
    if (package, expiry).count(None) == 0:
        current_package = f'{package}:{expiry}'
    else:
        current_package = None

    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE subscriptions SET current_package = ? WHERE discord_id = ?",
            (current_package, discord_id)
        )


def update_current_package(discord_id: int):
    """
    Updates current_package column to match current
    package determined from package_data json string
    :param discord_id: the discord id of the respective user
    """

    subscription = get_subscription(
        discord_id, include_booster=False, get_expiry=True)
    if subscription:
        package, expiry = subscription
    else:
        package, expiry = None, None
    set_current_package(discord_id, package, expiry)


def add_subscription(discord_id: int, package: str, expires: int) -> None:
    """
    Adds a subscription to a user
    :param discord_id: the discord id of the respective user
    :param package: package the same of the package to give the user
    :param expires: the epoch timestamp that the package will expire 
    """
    package_data = get_package_data(discord_id)

    timestamp_blacklist = [float(key) for key in package_data]
    timestamp = get_timestamp(blacklist=timestamp_blacklist)

    package_data[str(timestamp)] = {'package': package, 'expires': expires}
    package_data_str = json.dumps(package_data)

    current_package = f'{package}:{expires}'

    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM subscriptions WHERE discord_id = ?', (discord_id,))
        current_subscription = cursor.fetchone()

        if current_subscription:
            cursor.execute(
                "UPDATE subscriptions SET current_package = ?, package_data = ? WHERE discord_id = ?",
                (current_package, package_data_str, discord_id))
        else:
            cursor.execute(
                'INSERT INTO subscriptions '
                '(discord_id, current_package, package_data) '
                'VALUES (?, ?, ?)',
                (discord_id, current_package, package_data_str))

    set_current_package(discord_id, package, expires)

    with open('../utils/database/new_subscriptions.json', 'r+') as datafile:
        new_subscriptions = json.load(datafile)
        new_subscriptions[str(discord_id)] = package

        datafile.seek(0)  # Move the file pointer to the beginning
        json.dump(new_subscriptions, datafile, indent=4)
        datafile.truncate()


def remove_subscription(discord_id: int, package: str,
                        max_removals: int=-1):
    """
    Removes certain amount occurences of a subscription from a user
    :param discord_id: the discord_id of the respective user
    :param package: the package to remove from the user
    :param max_removals: the amount of packages in the user's package
    history to remove from the user (`-1` for no limit)
    """
    package_data = get_package_data(discord_id)

    removed = 0
    now = datetime.utcnow().timestamp()
    for key, value in package_data.items():
        if value['package'] == package:
            if max_removals == -1 or removed < max_removals:
                package_data[key]['expires'] = now - 1

                removed += 1
                continue
            break

    set_package_data(discord_id, package_data)
    set_current_package(discord_id, package='idle', expiry=0)


def get_package_permissions(package: str) -> list:
    """
    Returns a list of the configured permissions for a given package
    :param package: the package to get the permissions of
    """
    packages_config: dict[str, dict[str, list]] = get_config('packages')

    package_perms = packages_config.get(package, {}).get('permissions', [])
    return package_perms


class SubscriptionManager:
    def __init__(self, discord_id: int):
        self.discord_id = discord_id


    def get_subscription(self, include_booster=True, get_expiry=False):
        """
        Returns a users subscription data from subscription database\n

        :param include_booster: whether or not to include booster premium
        :param get_expiry: whether or not to return the package expiry timestamp
        """
        return get_subscription(
            discord_id=self.discord_id,
            include_booster=include_booster,
            get_expiry=get_expiry
        )


    def add_subscription(self, package: str, expires: int):
        """
        Adds a subscription to a user
        :param package: package the same of the package to give the user
        :param expires: the epoch timestamp that the package will expire
        """
        add_subscription(self.discord_id, package, expires)


    def remove_subscription(self, package: str, max_removals: int=-1):
        """
        Removes certain amount occurences of a subscription from a user
        :param package: the package to remove from the user
        :param max_removals: the amount of packages in the user's package
        history to remove from the user (`-1` for no limit)
        """
        remove_subscription(self.discord_id, package, max_removals)


    def update_current_package(self):
        """
        Updates current_package column to match current
        package determined from package_data json string
        """
        update_current_package(self.discord_id)


    def set_package_data(self, package_data: dict):
        """
        Sets a user's package data column to specified package data dictionary
        :param package_data: the package data to be set for the user
        """
        set_package_data(self.discord_id, package_data)


    def is_booster(self) -> bool:
        """
        Returns a bool if the user has booster premium or not
        """
        return is_booster(self.discord_id)


    def get_package_data(self) -> dict:
        """
        Returns package data dict for a user
        """
        return get_package_data(self.discord_id)


    def get_all_subscription_data(self) -> tuple | None:
        """
        Returns all columns of subscription data for a user
        """
        return get_all_subscription_data(self.discord_id)
