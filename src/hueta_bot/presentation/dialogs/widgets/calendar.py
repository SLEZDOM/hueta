from datetime import date
from typing import (
    Dict,
    TypedDict,
    Sequence,
    Callable,
    Union,
    TypeVar,
    Any,
    Optional
)

from babel.dates import get_day_names, get_month_names
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import (
    Calendar,
    CalendarScope,
)
from aiogram_dialog.widgets.kbd.calendar_kbd import (
    CalendarDaysView,
    DATE_TEXT,
    CalendarMonthView,
    CalendarScopeView,
    CalendarYearsView,
    date_from_raw,
    OnDateSelected,
    CalendarUserConfig,
    CalendarConfig
)
from aiogram_dialog.widgets.text import Format, Text
from aiogram_dialog.widgets.common import ManagedWidget, WhenCondition
from aiogram_dialog.widgets.widget_event import (
    ensure_event_processor, WidgetEventProcessor,
)
from aiogram_dialog.widgets.common.items import (
    get_items_getter,
    ItemsGetterVariant
)


MARK_DATE_TEXT = Format("{date:%d}")
UNMARK_DATE_TEXT = Format("✗")
CHECKED_MARK_DATE_TEXT = Format("[{date:%d}]")
CHECKED_UNMARK_DATE_TEXT = Format("[✗]")


T = TypeVar("T")
TypeFactory = Callable[[str], T]
ItemIdGetter = Callable[[Any], Union[str, int]]
ItemsGetter = Callable[[Dict], Sequence]


class CalendarData(TypedDict):
    current_scope: str
    current_offset: str
    checked: list[str]


class RadioCalendarData(TypedDict):
    current_scope: str
    current_offset: str
    checked: Optional[str] = None


class CheckedDay(Text):
    def __init__(
        self,
        is_date_checked: Callable[["DialogManager", date], bool],
        is_date_in_items: Callable[[Dict, date], bool],
    ):
        super().__init__()
        self._is_date_checked = is_date_checked
        self.is_date_in_items = is_date_in_items

    async def _render_text(self, data, manager: DialogManager) -> str:
        _is_date_checked = self._is_date_checked(manager, data["date"])

        is_date_in_items = self.is_date_in_items(data["data"], data["date"])

        if _is_date_checked and is_date_in_items:
            return await CHECKED_MARK_DATE_TEXT.render_text(data, manager)
        elif _is_date_checked:
            return await CHECKED_UNMARK_DATE_TEXT.render_text(data, manager)
        elif is_date_in_items:
            return await MARK_DATE_TEXT.render_text(data, manager)
        else:
            return await UNMARK_DATE_TEXT.render_text(data, manager)


class MarkedDay(Text):
    def __init__(
        self,
        is_date_in_items: Callable[[Dict, date], bool],
    ):
        super().__init__()
        self.is_date_in_items = is_date_in_items

    async def _render_text(self, data, manager: DialogManager) -> str:
        is_date_in_items = self.is_date_in_items(data["data"], data["date"])

        if is_date_in_items:
            return await MARK_DATE_TEXT.render_text(data, manager)
        else:
            return await UNMARK_DATE_TEXT.render_text(data, manager)


class WeekDay(Text):
    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: date = data["date"]
        locale = manager.event.from_user.language_code
        return get_day_names(
            width="short", context="stand-alone", locale=locale,
        )[selected_date.weekday()].title()


class Month(Text):
    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: date = data["date"]
        locale = manager.event.from_user.language_code
        return get_month_names(
            "wide", context="stand-alone", locale=locale,
        )[selected_date.month].title()


class CustomCalendar(Calendar):
    def __init__(
        self,
        id: str,
        on_click: Union[OnDateSelected, WidgetEventProcessor, None] = None,
        config: Optional[CalendarConfig] = None,
        when: WhenCondition = None,
    ) -> None:
        super().__init__(
            id=id,
            on_click=on_click,
            config=config,
            when=when
        )

    def _init_views(self) -> dict[CalendarScope, CalendarScopeView]:
        return {
            CalendarScope.DAYS: CalendarDaysView(
                self._item_callback_data,
                date_text=DATE_TEXT,
                today_text=DATE_TEXT,
                header_text=Month(),
                weekday_text=WeekDay(),
                next_month_text=Month() + " ⊳",
                prev_month_text="⊲ " + Month(),
            ),
            CalendarScope.MONTHS: CalendarMonthView(
                self._item_callback_data,
                month_text=Month(),
                header_text="~~~~~ " + Format("{date:%Y}") + " ~~~~~",
                this_month_text="[" + Month() + "]",
            ),
            CalendarScope.YEARS: CalendarYearsView(
                self._item_callback_data,
            ),
        }


class MarkedCalendar(CustomCalendar):
    def __init__(
        self,
        id: str,
        item_id_getter: ItemIdGetter,
        items: ItemsGetterVariant,
        on_click: Union[OnDateSelected, WidgetEventProcessor, None] = None,
        when: WhenCondition = None,
    ) -> None:
        super().__init__(id=id, when=when)
        self.item_id_getter = item_id_getter
        self.items_getter = get_items_getter(items)
        self.on_click = ensure_event_processor(on_click)
    
    async def reset_checked(
        self,
        manager: DialogManager,
    ) -> None:
        self.set_widget_data(manager, {"checked": None})

    async def set_checked(
        self,
        item_id: date,
        manager: DialogManager,
    ) -> None:
        item_id_str = str(item_id.isoformat())
        self.set_widget_data(manager, {"checked": item_id_str})
    
    async def _handle_click_date(
        self,
        data: str,
        manager: DialogManager,
    ) -> None:
        item_date = date_from_raw(int(data))
        await self.on_click.process_event(
            manager.event,
            self.managed(manager),
            manager,
            item_date,
        )
    
    def _is_date_in_items(
        self,
        data: Dict,
        item_date: date
    ):
        return item_date in {
            self.item_id_getter(item)
            for item in self.items_getter(data)
        }

    def _init_views(self) -> dict[CalendarScope, CalendarScopeView]:
        return {
            CalendarScope.DAYS: CalendarDaysView(
                self._item_callback_data,
                date_text=MarkedDay(
                    self._is_date_in_items,
                ),
                today_text=MarkedDay(
                    self._is_date_in_items
                ),
                header_text=Month(),
                weekday_text=WeekDay(),
                next_month_text=Month() + " ⊳",
                prev_month_text="⊲ " + Month(),
            ),
            CalendarScope.MONTHS: CalendarMonthView(
                self._item_callback_data,
                month_text=Month(),
                header_text="~~~~~ " + Format("{date:%Y}") + " ~~~~~",
                this_month_text="[" + Month() + "]",
            ),
            CalendarScope.YEARS: CalendarYearsView(
                self._item_callback_data,
            ),
        }


class MultiselectCalendar(CustomCalendar):
    def __init__(
        self,
        id: str,
        item_id_getter: ItemIdGetter,
        items: ItemsGetterVariant,
        on_click: Union[OnDateSelected, WidgetEventProcessor, None] = None,
        when: WhenCondition = None,
    ) -> None:
        super().__init__(id=id, when=when)
        self.item_id_getter = item_id_getter
        self.items_getter = get_items_getter(items)
        self.on_click = ensure_event_processor(on_click)

    def is_checked(
        self,
        item_id: date,
        manager: DialogManager,
    ) -> bool:
        data = self.get_checked(manager)
        return item_id in data

    def get_checked(self, manager: DialogManager) -> list[date]:
        checked = self._get_checked(manager)
        return [date.fromisoformat(str(item)) for item in checked]
    
    def _get_checked(self, manager: DialogManager) -> list[str]:
        calendar_data: CalendarData = self.get_widget_data(manager, {})
        return calendar_data.get("checked", [])
    
    async def reset_checked(
        self,
        manager: DialogManager,
    ) -> None:
        data = self.get_widget_data(manager, {})
        data["checked"] = []

    async def set_checked(
        self,
        item_id: date,
        checked: bool,
        manager: DialogManager,
    ) -> None:
        item_id_str = str(item_id.isoformat())
        data: list = self._get_checked(manager)
        changed = False
        if item_id_str in data:
            if not checked and len(data) > 0:
                data.remove(item_id_str)
                changed = True
        else:
            if checked:
                data.append(item_id_str)
                changed = True
        if changed:
            self.set_widget_data(manager, {"checked": data})
    
    async def _handle_click_date(
        self,
        data: str,
        manager: DialogManager,
    ) -> None:
        date_ = date_from_raw(int(data))
        await self.set_checked(
            date_,
            not self.is_checked(date_, manager),
            manager,
        )
        await self.on_click.process_event(
            manager.event,
            self.managed(manager),
            manager,
            date_,
        )

    def _is_date_checked(
        self,
        manager: DialogManager,
        item_date: date
    ):
        return item_date in self.get_checked(manager)
    
    def _is_date_in_items(
        self,
        data: Dict,
        item_date: date
    ):
        return item_date in {
            self.item_id_getter(item)
            for item in self.items_getter(data)
        }

    def _init_views(self) -> dict[CalendarScope, CalendarScopeView]:
        return {
            CalendarScope.DAYS: CalendarDaysView(
                self._item_callback_data,
                date_text=CheckedDay(
                    self._is_date_checked,
                    self._is_date_in_items,
                ),
                today_text=CheckedDay(
                    self._is_date_checked,
                    self._is_date_in_items,
                ),
                header_text=Month(),
                weekday_text=WeekDay(),
                next_month_text=Month() + " ⊳",
                prev_month_text="⊲ " + Month(),
            ),
            CalendarScope.MONTHS: CalendarMonthView(
                self._item_callback_data,
                month_text=Month(),
                header_text="~~~~~ " + Format("{date:%Y}") + " ~~~~~",
                this_month_text="[" + Month() + "]",
            ),
            CalendarScope.YEARS: CalendarYearsView(
                self._item_callback_data,
            ),
        }

    def managed(self, manager: DialogManager) -> "ManagedMultiselectCalendar":
        return ManagedMultiselectCalendar(self, manager)
    

class ManagedMultiselectCalendar(ManagedWidget[MultiselectCalendar]):
    def is_checked(self, item_id: date) -> bool:
        return self.widget.is_checked(item_id, self.manager)

    def get_checked(self) -> list[date]:
        return self.widget.get_checked(self.manager)

    async def reset_checked(self):
        return await self.widget.reset_checked(
            self.manager,
        )

    async def set_checked(self, item_id: date, checked: bool) -> None:
        return await self.widget.set_checked(
            item_id, checked, self.manager,
        )


class RadioCalendar(CustomCalendar):
    def __init__(
        self,
        id: str,
        item_id_getter: ItemIdGetter,
        items: ItemsGetterVariant,
        on_click: Union[OnDateSelected, WidgetEventProcessor, None] = None,
        when: WhenCondition = None,
        user_config: Optional[CalendarUserConfig] = None,
        config: Optional[CalendarConfig] = None,
    ) -> None:
        super().__init__(id=id, when=when, config=config)
        self.item_id_getter = item_id_getter
        self.items_getter = get_items_getter(items)
        self.on_click = ensure_event_processor(on_click)
        self.user_config = user_config
    
    def is_checked(
        self,
        item_id: date,
        manager: DialogManager,
    ) -> bool:
        data = self.get_checked(manager)
        return item_id == data
    
    def set_offset(
        self,
        new_offset: date,
        manager: DialogManager
    ) -> None:
        data = self.get_widget_data(manager, {})
        data["current_offset"] = new_offset.isoformat()

    def get_checked(self, manager: DialogManager) -> date | None:
        checked = self._get_checked(manager)
        if checked:
            return date.fromisoformat(str(checked))
    
    def _get_checked(self, manager: DialogManager) -> str | None:
        calendar_data: RadioCalendarData = self.get_widget_data(manager, {})
        return calendar_data.get("checked", None)
    
    async def reset_checked(
        self,
        manager: DialogManager,
    ) -> None:
        data = self.get_widget_data(manager, {})
        data["checked"] = None

    async def set_checked(
        self,
        item_id: date,
        manager: DialogManager,
    ) -> None:
        item_id_str = str(item_id.isoformat())
        self.set_widget_data(manager, {"checked": item_id_str})
    
    async def _handle_click_date(
        self,
        data: str,
        manager: DialogManager,
    ) -> None:
        item_date = date_from_raw(int(data))
        await self.set_checked(
            item_date,
            manager,
        )
        await self.on_click.process_event(
            manager.event,
            self.managed(manager),
            manager,
            item_date,
        )

    def _is_date_checked(
        self,
        manager: DialogManager,
        item_date: date
    ):
        return item_date == self.get_checked(manager)
    
    def _is_date_in_items(
        self,
        data: Dict,
        item_date: date
    ):
        return item_date in {
            self.item_id_getter(item)
            for item in self.items_getter(data)
        }

    def _init_views(self) -> dict[CalendarScope, CalendarScopeView]:
        return {
            CalendarScope.DAYS: CalendarDaysView(
                self._item_callback_data,
                date_text=CheckedDay(
                    self._is_date_checked,
                    self._is_date_in_items,
                ),
                today_text=CheckedDay(
                    self._is_date_checked,
                    self._is_date_in_items
                ),
                header_text=Month(),
                weekday_text=WeekDay(),
                next_month_text=Month() + " ⊳",
                prev_month_text="⊲ " + Month(),
            ),
            CalendarScope.MONTHS: CalendarMonthView(
                self._item_callback_data,
                month_text=Month(),
                header_text="~~~~~ " + Format("{date:%Y}") + " ~~~~~",
                this_month_text="[" + Month() + "]",
            ),
            CalendarScope.YEARS: CalendarYearsView(
                self._item_callback_data,
            ),
        }

    def managed(self, manager: DialogManager) -> "ManagedRadioCalendar":
        return ManagedRadioCalendar(self, manager)
    

class ManagedRadioCalendar(ManagedWidget[RadioCalendar]):
    def is_checked(self, item_id: date) -> bool:
        return self.widget.is_checked(item_id, self.manager)

    def get_checked(self) -> date | None:
        return self.widget.get_checked(self.manager)

    async def reset_checked(self):
        return await self.widget.reset_checked(
            self.manager,
        )

    async def set_checked(self, item_id: date, checked: bool) -> None:
        return await self.widget.set_checked(
            item_id, checked, self.manager,
        )