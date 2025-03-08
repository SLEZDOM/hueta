from enum import Enum
from typing import Dict, Optional

from aiogram.types import CallbackQuery
from aiogram.fsm.state import State

from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import Data
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.kbd.state import (
    EventProcessorButton,
)
from aiogram_dialog.widgets.text import Text, Case
from aiogram_dialog.widgets.kbd.button import Button, OnClick


class CheckStateMode(str, Enum):
    STATE_GROUP = State()
    STATE = State()


class TabState(EventProcessorButton):
    def __init__(
        self,
        checked_text: Text,
        unchecked_text: Text,
        id: str,
        state: State,
        default_state: Optional[State] = None,
        check_state_mode: CheckStateMode = CheckStateMode.STATE,
        on_click: Optional[OnClick] = None,
        when: WhenCondition = None,
    ) -> None:
        text = Case(
            {
                True: checked_text,
                False: unchecked_text
            },
            selector=self._is_text_checked,
        )
        super().__init__(
            text=text,
            id=id,
            on_click=on_click,
            when=when,
        )
        self.user_on_click = on_click
        self.state = state
        self.check_state_mode = check_state_mode
        self.default_state = default_state

    def _is_text_checked(
        self,
        data: Dict,
        case: Case,
        manager: DialogManager
    ) -> bool:
        case_state_check = {
            CheckStateMode.STATE: (
                self.state == manager.current_context().state
            ),
            CheckStateMode.STATE_GROUP: (
                self.state.group == manager.current_context().state.group
            )
        }

        return case_state_check[self.check_state_mode]


class TabSwitchTo(TabState):
    async def _on_click(
        self,
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
    ) -> None:
        if self.user_on_click:
            await self.user_on_click(callback, self, manager)
        if self.default_state:
            if self.state == manager.current_context().state:
                return await manager.switch_to(self.default_state)
        await manager.switch_to(self.state)


class TabStart(TabState):
    def __init__(
        self,
        checked_text: Text,
        unchecked_text: Text,
        id: str,
        state: State,
        data: Data = None,
        check_state_mode: CheckStateMode = CheckStateMode.STATE,
        default_state: Optional[State] = None,
        on_click: Optional[OnClick] = None,
        when: WhenCondition = None,
    ) -> None:
        super().__init__(
            checked_text=checked_text,
            unchecked_text=unchecked_text,
            id=id,
            state=state,
            default_state=default_state,
            check_state_mode=check_state_mode,
            on_click=on_click,
            when=when
        )
        self.data = data

    async def _on_click(
        self,
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
    ) -> None:
        if self.user_on_click:
            await self.user_on_click(callback, self, manager)
        if self.default_state:
            if self.state == manager.current_context().state:
                return await manager.start(self.default_state)
        await manager.start(self.state)
