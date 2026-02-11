import os

from ..accounts import Account, AccountThemes
from ..common import REL_PATH
from ..errors import ThemeNotFoundError

BG_DIR = f"{REL_PATH}/database/fractyl-custom-backgrounds"
THEME_DIR = f"{REL_PATH}/assets/fractyl-themes"


def load_custom_background(discord_user_id: int, render_name: str) -> bytes | None:
    account = Account(discord_user_id)

    if not account.permissions.has_access("custom_backgrounds"):
        return None

    specific_img = f"{BG_DIR}/{discord_user_id}/{render_name}.png"

    if os.path.exists(specific_img):
        with open(specific_img, "rb") as img_file:
            return img_file.read()

    default_img = f"{BG_DIR}/{discord_user_id}/default.png"

    if os.path.exists(default_img):
        with open(default_img, "rb") as img_file:
            return img_file.read()

    return None


def load_theme_img(theme_id: str) -> bytes:
    theme_fp = f"{THEME_DIR}/{theme_id}.png"

    if not os.path.exists(theme_fp):
        raise ThemeNotFoundError(f"No such theme at '{theme_fp}'")

    with open(theme_fp, "rb") as img_file:
        return img_file.read()


def load_background_for_user(discord_user_id: int, render_name: str) -> bytes | None:
    bg = load_custom_background(discord_user_id, render_name)

    if not bg:
        user_theme = AccountThemes(discord_user_id).get_active_theme()

        try:
            bg = load_theme_img(user_theme.id)
        except ThemeNotFoundError:
            bg = None

    return bg

