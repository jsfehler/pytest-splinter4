"""Browser screenshot tests."""
import unittest.mock as mock
import os

import pytest


def test_browser_screenshot_escaped(pytester):
    """Test making screenshots on test failure with escaped test names.

    Normal test run.
    """
    pytester.inline_runsource(
        """
        import pytest

        @pytest.mark.parametrize('param', ['escaped/param'])
        def test_screenshot(browser, param):
            assert False
    """,
        "-vl",
        "-r w",
    )

    expected_directory = os.path.join(
        pytester.path, "logs", "test_browser_screenshot_escaped",
    )

    assert os.path.isdir(expected_directory)
    assert 2 == len(os.listdir(expected_directory))

    for item in (os.listdir(expected_directory)):
        assert item.startswith('test_screenshot[escaped-param]-browser')


def test_browser_screenshot_normal(pytester, mocked_browser):
    """Test making screenshots on test failure.

    Normal test run.
    """
    pytester.inline_runsource(
        """
        def test_screenshot(browser):
            assert False
    """,
        "-vl",
        "-r w",
    )

    expected_directory = os.path.join(
        pytester.path, "logs", "test_browser_screenshot_normal",
    )

    assert os.path.isdir(expected_directory)
    assert 2 == len(os.listdir(expected_directory))

    for item in (os.listdir(expected_directory)):
        assert item.startswith('test_screenshot-browser')


def test_browser_screenshot_function_scoped_browser(pytester, mocked_browser):
    """Test making screenshots on test failure.

    Normal test run.
    """
    pytester.inline_runsource(
        """
        def test_screenshot(browser):
            assert False
    """,
        "-vls",
        "--splinter-session-scoped-browser=false",
    )

    expected_directory = os.path.join(
        pytester.path, "logs", "test_browser_screenshot_function_scoped_browser",
    )

    assert os.path.isdir(expected_directory)
    assert 2 == len(os.listdir(expected_directory))

    for item in (os.listdir(expected_directory)):
        assert item.startswith('test_screenshot-browser')


@mock.patch("pytest_splinter4.plugin.splinter.Browser")
def test_browser_screenshot_error(mocked_browser, testdir):
    """Test warning with error during taking screenshots on test failure."""
    mocked_browser.return_value.screenshot.side_effect = Exception(
        "Expected Test Failure",
    )
    mocked_browser.return_value.driver_name = "firefox"
    mocked_browser.return_value.html = u"<html>"

    testdir.makepyfile(
        """
        def test_screenshot(browser):
            assert False
    """
    )
    result = testdir.runpytest()
    result.stdout.fnmatch_lines(
        "*Warning: Could not save screenshot: Expected Test Failure",
    )


@pytest.mark.skipif(
    'not config.pluginmanager.getplugin("xdist")',
    reason="pytest-xdist is not installed",
)
def test_browser_screenshot_xdist(pytester):
    """Test making screenshots on test failure in distributed mode (xdist).

    Distributed test run.
    """
    pytester.inline_runsource(
        """
        import unittest.mock as mock

        import splinter

        import pytest

        m = mock.MagicMock()
        m.driver = mock.MagicMock()
        m.return_value.driver_name = "mock"

        splinter.browser._DRIVERS['mock'] = m

        @pytest.fixture
        def splinter_webdriver():
            return "mock"


        def test_screenshot(browser):
            def screenshot(name="", **kwargs):
                path = f"{name}.png"
                with open(path, "w") as f:
                    f.write('dummy')
                return path

            def html_snapshot(name="", **kwargs):
                path = f"{name}.html"
                with open(path, "w") as f:
                    f.write('dummy')
                return path

            browser.screenshot.side_effect = screenshot
            browser.html_snapshot.side_effect = html_snapshot

            assert False
    """,
        "-vl",
        "-n1",
    )

    expected_directory = os.path.join(
        pytester.path, 'logs', 'test_browser_screenshot_xdist',
    )

    assert os.path.isdir(expected_directory)
    assert 2 == len(os.listdir(expected_directory))

    for item in (os.listdir(expected_directory)):
        assert item.startswith('test_screenshot-browser')
