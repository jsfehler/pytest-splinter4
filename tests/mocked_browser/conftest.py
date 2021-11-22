"""Configuration for pytest runner."""
import unittest.mock as mock

import pytest


@pytest.fixture(scope="session")
def splinter_session_scoped_browser():
    """Make it test scoped."""
    return False


@pytest.fixture(autouse=True)
def mocked_browser(browser_pool, request):
    """Mock splinter browser."""
    # to avoid re-using of cached browser from other tests
    for browser in browser_pool.values():
        browser.quit()
    browser_pool.clear()

    def mocked_browser(driver_name, *args, **kwargs):
        mocked_browser = mock.MagicMock()
        mocked_browser.driver = mock.MagicMock()
        mocked_browser.driver.profile = mock.MagicMock()
        mocked_browser.driver_name = driver_name
        mocked_browser.html = u"<html></html>"

        def screenshot(name="", suffix=".png"):
            path = f"{name}{suffix}"
            with open(path, "w") as f:
                f.write('dummy')
            return path

        def html_snapshot(name="", suffix=".html"):
            path = f"{name}{suffix}"
            with open(path, "w") as f:
                f.write('dummy')
            return path

        mocked_browser.screenshot.side_effect = screenshot
        mocked_browser.html_snapshot.side_effect = html_snapshot
        return mocked_browser

    patcher = mock.patch(
        "pytest_splinter4.plugin.splinter.Browser", mocked_browser)
    yield patcher.start()
    patcher.stop()
