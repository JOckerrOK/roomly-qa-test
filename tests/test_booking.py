import pytest
from playwright.sync_api import Page


@pytest.mark.skip(reason="TODO: implement a successful booking scenario")
def test_successful_booking(page: Page, base_url: str):
    raise NotImplementedError


@pytest.mark.skip(reason="TODO: choose and implement a negative scenario")
def test_invalid_booking(page: Page, base_url: str):
    raise NotImplementedError


@pytest.mark.skip(reason="TODO: reproduce a discovered defect")
def test_discovered_defect(page: Page, base_url: str):
    raise NotImplementedError
