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
        "--edge-arguments",
        action="append",
        default=[],
        help="List of arguments to use for Edge Options.",
    )

    parser.addini(
        'edge_arguments',
        'Arguments to add to Edge Options object',
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


def _create_options(request, name: str):
    """Create a new Webdriver Options instance.

    Arguments:
        name (str): Name of the options object to create. One of:
            chrome, edge, firefox

    Returns:
        Options
    """
    ini_args = request.config.getini(f'{name}_arguments').split()
    cmdline_args = request.config.getoption(f'{name}_arguments')
    arguments = ini_args + cmdline_args

    options_objects = {
        'chrome': webdriver.chrome.options.Options,
        'edge': webdriver.edge.options.Options,
        'firefox': webdriver.firefox.options.Options,
    }

    options = options_objects[name]()

    for argument in arguments:
        options.add_argument(argument)

    return options


@pytest.fixture(scope='session')
def selenium_options(request, splinter_webdriver):
    """Get the correct Options object for the current driver.

    Returns:
        Options
    """
    return _create_options(request, splinter_webdriver)


@pytest.fixture(scope='session')
def chrome_options(selenium_options):
    """Get a new Webdriver Chrome Options instance.

    Returns:
        selenium.webdriver.chrome.options.Options
    """
    return selenium_options


@pytest.fixture(scope='session')
def edge_options(selenium_options):
    """Get a new Webdriver Edge Options instance.

    Returns:
        selenium.webdriver.edge.options.Options
    """
    return selenium_options


@pytest.fixture(scope='session')
def firefox_options(selenium_options):
    """Get a new Webdriver Firefox Options instance.

    Returns:
        selenium.webdriver.firefox.options.Options
    """
    return selenium_options
