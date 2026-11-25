"""Page Object формы бронирования переговорной."""
import datetime
from dataclasses import dataclass

from playwright.sync_api import Locator, Page


@dataclass(frozen=True)
class Booking:
    """Данные брони. room — значение в списке комнат: small, medium или large."""

    room: str
    date: datetime.date
    start: str
    end: str
    participants: int | str
    name: str
    email: str


class BookingPage:
    SUCCESS_TEXT = "Бронирование создано"
    FORM_ERROR_TEXT = "Проверьте, пожалуйста, заполнение формы."

    def __init__(self, page: Page) -> None:
        self.page = page
        self.room = page.get_by_label("Переговорная")
        self.date = page.get_by_label("Дата")
        self.start_time = page.get_by_label("Начало")
        self.end_time = page.get_by_label("Окончание")
        self.participants = page.get_by_label("Участники")
        self.name = page.get_by_label("Ваше имя")
        self.email = page.get_by_label("Рабочая почта")
        self.submit_button = page.get_by_role("button", name="Забронировать")
        self.status = page.get_by_role("status")
        self.invalid_fields = page.locator(".field.has-error")

    def open(self, url: str) -> "BookingPage":
        self.page.goto(url)
        return self

    def fill(self, booking: Booking) -> None:
        self.room.select_option(booking.room)
        self.date.fill(booking.date.isoformat())
        self.start_time.fill(booking.start)
        self.end_time.fill(booking.end)
        self.participants.fill(str(booking.participants))
        self.name.fill(booking.name)
        self.email.fill(booking.email)

    def submit(self) -> None:
        self.submit_button.click()

    def book(self, booking: Booking) -> None:
        self.fill(booking)
        self.submit()

    def error(self, field: str) -> Locator:
        """Текст ошибки под полем.

        field — имя поля формы: room, date, startTime, endTime, participants, name, email.
        """
        return self.page.locator(f'[data-error-for="{field}"]')
