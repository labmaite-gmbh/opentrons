"""Left Menu Locators."""
from typing import Literal

from rich.console import Console
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from src.driver.base import Base, Element

PagesLike = Literal["devices", "protocols", "labware", "app-settings"]


class LeftMenu:
    """Locators for the left side menu."""

    def __init__(self, driver: WebDriver, console: Console, execution_id: str) -> None:
        """Initialize with driver, console, and unique id for the test."""
        self.base: Base = Base(driver, console, execution_id)

    protocols: Element = Element(
        (By.XPATH, '//a[contains(@href,"#/protocols")]'), "Left menu Protocols"
    )
    labware: Element = Element(
        (By.XPATH, '//a[contains(@href,"#/labware")]'), "Left menu Labware"
    )
    devices: Element = Element(
        (By.XPATH, '//a[contains(@href,"#/devices")]'), "Left menu Devices"
    )
    gear: Element = Element(
        (By.XPATH, '//a[contains(@href,"#/app-settings")]'),
        "Left menu bottom gear to go to App Settings",
    )

    def navigate(self, page_name: PagesLike) -> None:
        """Use url to navigate."""
        base_url = self.base.driver.current_url.split("#")[0]
        self.base.driver.get(f"{base_url}#/{page_name}")
