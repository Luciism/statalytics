from typing import Self, Callable, Awaitable
import discord
from typing_extensions import override

from ._custom import CustomBaseView
from .. import emoji


class PreviousPageBtn(discord.ui.Button["PaginationView"]):
    def __init__(self) -> None:
        super().__init__(
            style=discord.ButtonStyle.gray, emoji=emoji.PREV, custom_id="prev_btn"
        )

    @override
    async def callback(self, interaction: discord.Interaction) -> None:
        if self.view is None:
            return

        view = self.view.replicate(self.view.page - 1)
        _ = await self.view.base_interaction.edit_original_response(view=view)

        await interaction.response.defer()
        await self.view.callback(view.page)

class NextPageBtn(discord.ui.Button["PaginationView"]):
    def __init__(self) -> None:
        super().__init__(
            style=discord.ButtonStyle.gray, emoji=emoji.NEXT, custom_id="next_btn"
        )

    @override
    async def callback(self, interaction: discord.Interaction) -> None:
        if self.view is None:
            return

        view = self.view.replicate(self.view.page + 1)
        _ = await self.view.base_interaction.edit_original_response(view=view)

        await interaction.response.defer()
        await self.view.callback(view.page)


class PaginationView(CustomBaseView):
    def __init__(
        self,
        *,
        interaction: discord.Interaction,
        callback: Callable[[int], Awaitable[None]],
        page: int = 1,
        total_pages: int | None,
        timeout: float | None = 180,
    ) -> None:
        super().__init__(timeout=timeout)

        self.page: int = page
        self.total_pages: int | None = total_pages
        self.base_interaction: discord.Interaction = interaction
        self.callback: Callable[[int], Awaitable[None]] = callback 

        btn_label = f"Page {page}/{total_pages}" if total_pages else f"Page {page}"

        page_info_btn: discord.ui.Button[Self] = discord.ui.Button(
            style=discord.ButtonStyle.gray, label=btn_label
        )
        page_info_btn.disabled = True

        prev_btn = PreviousPageBtn()
        if page == 1:
            prev_btn.disabled = True

        next_btn = NextPageBtn()

        if page == total_pages:
            next_btn.disabled = True
        _ = self.add_item(prev_btn)
        _ = self.add_item(page_info_btn)
        _ = self.add_item(next_btn)

    def replicate(self, page: int) -> "PaginationView":
        return PaginationView(
            interaction=self.base_interaction,
            callback=self.callback,
            page=page,
            total_pages=self.total_pages,
            timeout=self.timeout,
        )

    @override
    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True

        _ = await self.base_interaction.edit_original_response(view=self)

