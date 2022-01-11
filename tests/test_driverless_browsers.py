"""Tests for pytest-splinter django driver availability."""
import unittest.mock as mock

import pytest


@pytest.fixture(autouse=True)
def driverless_browser(request):
    """
    Mock splinter browser specifically for driverless browsers.

    Django and Flask browsers extends the LxmlDriver and doesn't provide a
    driver attribute.
    """

    def mocked_browser(driver_name, *args, **kwargs):
        mocked_browser = mock.Mock()
        del mocked_browser.driver  # force AttributeError
        mocked_browser.driver_name = driver_name
        mocked_browser.is_text_present.return_value = True
        return mocked_browser

    with mock.patch("pytest_splinter4.plugin.splinter.Browser", mocked_browser):
        yield


def test_driverless_splinter_browsers(pytester, browser):
    """Test the driverless splinter browsers."""

    pytester.makepyfile("""
        import pytest


        @pytest.fixture(scope='session')
        def splinter_webdriver():
            return 'django'


        def test_two(browser):
            browser.visit("/")
            assert browser.is_text_present("Ok!") is True
    """)

    result = pytester.runpytest('-v')
    assert result.ret == 0
