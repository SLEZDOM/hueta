from enum import Enum
from typing import Dict, List

from aiogram.types import InlineKeyboardButton

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import WhenCondition, Scroll
from aiogram_dialog.widgets.kbd import NumberedPager
from aiogram_dialog.widgets.kbd.pager import (
    DEFAULT_CURRENT_PAGE_TEXT,
    DEFAULT_PAGE_TEXT,
    DEFAULT_PAGER_ID,
    PagerData
)
from aiogram_dialog.api.internal import RawKeyboard
from aiogram_dialog.widgets.text import Text


class PaginationMode(Enum):
    NORMAL = "NORMAL"
    CENTERED = "CENTERED"


class PaginationPager(NumberedPager):
    def __init__(
        self,
        scroll: str | Scroll | None,
        mode: PaginationMode = PaginationMode.NORMAL,
        width: int = 0,
        id: str = DEFAULT_PAGER_ID,
        page_text: Text = DEFAULT_PAGE_TEXT,
        current_page_text: Text = DEFAULT_CURRENT_PAGE_TEXT,
        when: WhenCondition | None = None
    ) -> None:
        super().__init__(scroll, id, page_text, current_page_text, when)
        self.mode = mode
        self.width = width

    async def _render_page(
        self,
        pages: int,
        page: int,
        keyboard: List[List[InlineKeyboardButton]],
        mode: PaginationMode = PaginationMode.NORMAL,
    ) -> List[List[InlineKeyboardButton]]:
        if mode is PaginationMode.NORMAL:
            start_index = self.width * (page // self.width)
            end_index = min(pages, start_index + self.width)
        elif mode is PaginationMode.CENTERED:
            half_width = self.width // 2
            start_index = max(0, min(page - half_width, pages - self.width))
            end_index = min(pages, start_index + self.width)
        else:
            raise ValueError(f"Unknown pagination mode: {mode}")

        return keyboard[start_index:end_index]

    async def _render_contents(
        self,
        pages: int,
        page: int,
        data: Dict,
        manager: DialogManager,
    ) -> RawKeyboard:
        buttons = []
        for target_page in range(pages):
            button_data = await self._prepare_page_data(
                data=data, target_page=target_page,
            )
            if target_page == page:
                text_widget = self.current_page_text
            else:
                text_widget = self.page_text
            text = await text_widget.render_text(button_data, manager)
            buttons.append(
                InlineKeyboardButton(
                    text=text,
                    callback_data=self._item_callback_data(target_page),
                )
            )
        return buttons

    async def _render_keyboard(
        self,
        data: PagerData,
        manager: DialogManager,
    ) -> RawKeyboard:
        pages = data["pages"]
        current_page = data["current_page"]

        keyboard = await self._render_contents(
            pages,
            current_page,
            data,
            manager
        )
        page = await self._render_page(
            pages=pages,
            page=current_page,
            keyboard=keyboard,
            mode=self.mode
        )

        return [page]
