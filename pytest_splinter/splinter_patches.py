"""Patches for splinter."""
import functools  # pragma: no cover

from splinter import driver

from selenium.webdriver.support import wait


class PatchDriverAPI(driver.DriverAPI):
    """Add extra methods to splinter's Browser."""
    def __init__(self, *args, **kwargs):
        visit_condition = kwargs.pop("visit_condition")
        visit_condition_timeout = kwargs.pop("visit_condition_timeout")
        super().__init__(self, *args, **kwargs)

        if hasattr(self, "driver"):
            self.visit_condition = visit_condition
            self.visit_condition_timeout = visit_condition_timeout
            self.switch_to = self.driver.switch_to

        self.__splinter_browser__ = True

    def visit(self, url):
        """Override splinter's visit to avoid unnecessary checks and add wait_until instead."""
        super().visit(url)
        self.wait_for_condition(self.visit_condition, timeout=self.visit_condition_timeout)

    def wait_for_condition(
        self, condition=None, timeout=None, poll_frequency=0.5, ignored_exceptions=None
    ):
        """Wait for given javascript condition."""
        condition = functools.partial(condition or self.visit_condition, self)

        timeout = timeout or self.wait_time

        return wait.WebDriverWait(
            self.driver,
            timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions,
        ).until(lambda browser: condition())
