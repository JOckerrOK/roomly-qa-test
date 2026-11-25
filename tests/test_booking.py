"""Форма бронирования: позитивный, негативный сценарий и найденный дефект.

«Сейчас» в браузере зафиксировано, часовой пояс задан явно: результат
не зависит от даты, времени и места запуска.
"""
import re
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest
from playwright.sync_api import Page, expect

from pages.booking_page import Booking, BookingPage

# В Москве нет перехода на летнее время, поэтому достаточно фиксированного смещения.
MSK = timezone(timedelta(hours=3))
NOW = datetime(2030, 6, 14, 12, 0, tzinfo=MSK)

TODAY = NOW.date()
YESTERDAY = TODAY - timedelta(days=1)
FUTURE = TODAY + timedelta(days=3)

VALID = Booking(
    room="medium",
    date=FUTURE,
    start="10:00",
    end="11:00",
    participants=6,
    name="Анна Смирнова",
    email="anna.smirnova@company.ru",
)


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "timezone_id": "Europe/Moscow", "locale": "ru-RU"}


@pytest.fixture
def booking_page(page: Page, base_url: str) -> BookingPage:
    # Время фиксируется до загрузки: скрипт страницы берёт «сегодня» при старте.
    page.clock.set_fixed_time(NOW)
    return BookingPage(page).open(base_url)


def test_successful_booking(booking_page: BookingPage):
    """Будущая дата и корректные данные: сообщение с комнатой, датой, временем и именем."""
    booking_page.book(VALID)

    status = booking_page.status
    expect(status).to_contain_text(BookingPage.SUCCESS_TEXT)
    expect(status).to_contain_text("Средняя")
    # Формат даты в сообщении ТЗ не задаёт: принимаем ISO и ДД.ММ.ГГГГ.
    expect(status).to_contain_text(
        re.compile(f"{FUTURE.isoformat()}|{re.escape(FUTURE.strftime('%d.%m.%Y'))}")
    )
    expect(status).to_contain_text(VALID.start)
    expect(status).to_contain_text(VALID.end)
    expect(status).to_contain_text(VALID.name)
    expect(booking_page.invalid_fields).to_have_count(0)


def test_invalid_booking(booking_page: BookingPage):
    """Вчерашняя дата отклоняется: ошибка у поля «Дата», бронь не создаётся."""
    booking_page.book(replace(VALID, date=YESTERDAY))

    expect(booking_page.error("date")).to_have_text("Дата не может быть в прошлом.")
    expect(booking_page.status).to_have_text(BookingPage.FORM_ERROR_TEXT)


@pytest.mark.xfail(
    strict=True,
    reason="BUG-01: на сегодняшнюю дату можно забронировать уже прошедшее время",
    raises=AssertionError,
)
def test_discovered_defect(booking_page: BookingPage):
    """Сегодня 12:00, слот 09:00–10:00 уже прошёл: бронь должна быть отклонена."""
    booking_page.book(replace(VALID, date=TODAY, start="09:00", end="10:00"))

    expect(booking_page.status).not_to_contain_text(BookingPage.SUCCESS_TEXT)
    expect(booking_page.status).to_have_text(BookingPage.FORM_ERROR_TEXT)
