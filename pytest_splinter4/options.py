import pytest

from selenium import webdriver


def pytest_addoption(parser):
    """Add selenium options lists to pytest options."""
    parser.addoption(
        "--chrome-arguments",
        action="append",
        default=[],
        help="List of arguments to use for chrome Options.",
    )

    parser.addini(
        'chrome_arguments',
        'Arguments to add to Chrome Options object',
    )


@pytest.fixture(scope='session')
def chrome_options(request):
    """Create a new Webdriver Chrome Options instance.

    Returns:
        chrome.options.Options

    """
    ini_args = request.config.getini('chrome_arguments').split()
    cmdline_args = request.config.getoption('chrome_arguments')
    chrome_arguments = ini_args + cmdline_args

    options = webdriver.chrome.options.Options()

    for argument in chrome_arguments:
        options.add_argument(argument)

    return options
