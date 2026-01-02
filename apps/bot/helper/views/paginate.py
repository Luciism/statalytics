from typing import Self, Callable, Awaitable, final
import discord
from discord.ui import TextInput
from typing_extensions import override

from ._custom import CustomBaseModal, CustomBaseView
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


class SkipLeftBtn(discord.ui.Button["PaginationView"]):
    def __init__(self) -> None:
        super().__init__(
            style=discord.ButtonStyle.gray, emoji=emoji.SKIP_LEFT, custom_id="skip_left_btn"
        )

    @override
    async def callback(self, interaction: discord.Interaction) -> None:
        if self.view is None:
            return

        view = self.view.replicate(page=1)
        _ = await self.view.base_interaction.edit_original_response(view=view)

        await interaction.response.defer()
        await self.view.callback(view.page)


class SkipRightBtn(discord.ui.Button["PaginationView"]):
    def __init__(self) -> None:
        super().__init__(
            style=discord.ButtonStyle.gray, emoji=emoji.SKIP_RIGHT, custom_id="skip_right_btn"
        )

    @override
    async def callback(self, interaction: discord.Interaction) -> None:
        if self.view is None:
            return

        if self.view.total_pages:
            page = self.view.total_pages
        else:
            page = self.view.page + 10

        view = self.view.replicate(page)
        _ = await self.view.base_interaction.edit_original_response(view=view)

        await interaction.response.defer()
        await self.view.callback(view.page)


@final
class GoToPageModal(CustomBaseModal, title='Skip to page #'):
    def __init__(
        self,
        update_page_callable: Callable[[int], Awaitable[None]],
        total_pages: int | None=None,
    ) -> None:
        super().__init__()
        self.update_page = update_page_callable
        self.total_pages: int | None = total_pages

    page_number: TextInput['GoToPageModal'] = TextInput(
        label='Page Number',
        placeholder='1',
        style=discord.TextStyle.short,
        min_length=1
    )

    @override
    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        try:
            page = int(self.page_number.value)
        except ValueError:
            return

        await self.update_page(page)



class GoToBtn(discord.ui.Button["PaginationView"]):
    def __init__(self, page: int, total_pages: int | None) -> None:
        super().__init__(
            label=f"Page {page}/{total_pages}" if total_pages else f"Page {page}",
            style=discord.ButtonStyle.gray,
            # emoji=emoji.HASH,
            custom_id="goto_btn"
        )

    @override
    async def callback(self, interaction: discord.Interaction) -> None:
        if self.view is None:
            return

        async def update_page(page: int) -> None:
            if self.view is None:
                return

            if self.view.total_pages and page > self.view.total_pages:
                page = self.view.total_pages

            view = self.view.replicate(max(page, 1))
            _ = await self.view.base_interaction.edit_original_response(view=view)

            await self.view.callback(view.page)

        await interaction.response.send_modal(GoToPageModal(update_page, self.view.total_pages))


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

        prev_btn = PreviousPageBtn()
        skip_left_btn = SkipLeftBtn()
        if page == 1:
            prev_btn.disabled = True
            skip_left_btn.disabled = True

        next_btn = NextPageBtn()
        skip_right_btn = SkipRightBtn()

        if page == total_pages:
            next_btn.disabled = True
            skip_right_btn.disabled = True

        _ = self.add_item(skip_left_btn)
        _ = self.add_item(prev_btn)
        _ = self.add_item(GoToBtn(page, total_pages))
        _ = self.add_item(next_btn)
        _ = self.add_item(skip_right_btn)

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

