from typing import Any, Optional

from aiogram.fsm.state import State
from aiogram.types import CallbackQuery

from aiogram_dialog.api.entities import ShowMode, StartMode, Context
from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.kbd.button import Button, OnClick
from aiogram_dialog.widgets.text import Const, Text
from aiogram_dialog.widgets.kbd.state import EventProcessorButton


CANCEL_TEXT = Const("Cancel")


class Cancel(EventProcessorButton):
    def __init__(
        self,
        state: State,
        text: Text = CANCEL_TEXT,
        id: str = "__cancel__",
        result: Any = None,
        on_click: Optional[OnClick] = None,
        show_mode: Optional[ShowMode] = None,
        mode: StartMode = StartMode.NORMAL,
        when: WhenCondition = None,
    ):
        super().__init__(
            text=text, on_click=self._on_click,
            id=id, when=when,
        )
        self.text = text
        self.result = result
        self.user_on_click = on_click
        self.show_mode = show_mode
        self.state = state
        self.mode = mode

    def is_stack_empty(self, manager: DialogManager) -> bool:
        return len(manager.current_stack().intents) <= 1

    def is_first_state(self, manager: DialogManager) -> bool:
        context: Context = manager.current_context()
        all_states: tuple[State, ...] = context.state.group.__all_states__
        return all_states[0]._state == context.state._state

    async def _on_click(
        self,
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
    ) -> None:
        if self.user_on_click:
            await self.user_on_click(callback, self, manager)

        if self.is_first_state(manager):
            if self.is_stack_empty(manager):
                return await manager.start(
                    state=self.state,
                    mode=self.mode,
                    show_mode=self.show_mode
                )
            return await manager.done(self.result, show_mode=self.show_mode)

        await manager.back()
