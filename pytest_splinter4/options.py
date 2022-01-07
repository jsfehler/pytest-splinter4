import pytest

from selenium import webdriver


def pytest_addoption(parser):
    """Add selenium options lists to pytest options."""
    parser.addoption(
        "--chrome-arguments",
        action="append",
        default=[],
        help="List of arguments to use for Chrome Options.",
    )

    parser.addini(
        'chrome_arguments',
        'Arguments to add to Chrome Options object',
    )

    parser.addoption(
        "--firefox-arguments",
        action="append",
        default=[],
        help="List of arguments to use for Firefox Options.",
    )

    parser.addini(
        'firefox_arguments',
        'Arguments to add to Firefox Options object',
    )


@pytest.fixture(scope='session')
def chrome_options(request):
    """Create a new Webdriver Chrome Options instance.

    Returns:
        chrome.options.Options

    """
    ini_args = request.config.getini('chrome_arguments').split()
    cmdline_args = request.config.getoption('chrome_arguments')
    arguments = ini_args + cmdline_args

    options = webdriver.chrome.options.Options()

    for argument in arguments:
        options.add_argument(argument)

    return options


@pytest.fixture(scope='session')
def firefox_options(request):
    """Create a new Webdriver Firefox Options instance.

    Returns:
        firefox.options.Options

    """
    ini_args = request.config.getini('firefox_arguments').split()
    cmdline_args = request.config.getoption('firefox_arguments')
    arguments = ini_args + cmdline_args

    options = webdriver.firefox.options.Options()

    for argument in arguments:
        options.add_argument(argument)

    return options
