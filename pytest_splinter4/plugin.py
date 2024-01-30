"""Splinter plugin for pytest.

Provides easy interface for the browser from your tests providing the `browser` fixture
which is an object of splinter Browser class.
"""
import codecs
import functools  # pragma: no cover
import logging
import mimetypes  # pragma: no cover
import os.path
import re
import warnings
from http.client import HTTPException

from _pytest import junitxml

import pytest  # pragma: no cover

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import wait

import splinter  # pragma: no cover

from urllib3.exceptions import MaxRetryError

from .executable_path import get_executable_path
from .webdriver_patches import patch_webdriver  # pragma: no cover
from .xdist_plugin import SplinterXdistPlugin

LOGGER = logging.getLogger(__name__)


NAME_RE = re.compile(r"[\W]")


pytest_plugins = [
    'pytest_splinter4.options',
]


def _visit(self, old_visit, url):
    """Override splinter's visit to avoid unnecessary checks and add wait_until instead."""
    old_visit(url)
    self.wait_for_condition(self.visit_condition,
                            timeout=self.visit_condition_timeout)


def _wait_for_condition(
    self, condition=None, timeout=None, poll_frequency=0.5, ignored_exceptions=None,
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


def _screenshot_extraline(screenshot_png_file_name, screenshot_html_file_name):
    return f"""
===========================
pytest-splinter screenshots
===========================
png:  {screenshot_png_file_name}
html: {screenshot_html_file_name}
"""


def Browser(*args, **kwargs):  # NOQA N802
    """Emulate splinter's Browser."""
    visit_condition = kwargs.pop("visit_condition")
    visit_condition_timeout = kwargs.pop("visit_condition_timeout")
    browser = splinter.Browser(*args, retry_count=6, **kwargs)
    browser.wait_for_condition = functools.partial(
        _wait_for_condition, browser)
    if hasattr(browser, "driver"):
        browser.visit_condition = visit_condition
        browser.visit_condition_timeout = visit_condition_timeout
        browser.visit = functools.partial(_visit, browser, browser.visit)
    browser.__splinter_browser__ = True
    return browser


@pytest.fixture(scope="session")  # pragma: no cover
def splinter_close_browser() -> bool:
    """Determine if the browser is closed at the end of a test.

    Returns:
        bool
    """
    return True


@pytest.fixture(scope="session")  # pragma: no cover
def splinter_webdriver(request) -> str:
    """Name of the Webdriver to use.

    Returns:
        str
    """
    return request.config.option.splinter_webdriver


@pytest.fixture(scope="session")  # pragma: no cover
def splinter_remote_url(request) -> str:
    """URL for the Selenium Server used by Remote Webdriver.

    Returns:
        str
    """
    return request.config.option.splinter_remote_url


@pytest.fixture(scope="session")  # pragma: no cover
def splinter_remote_name(request) -> str:
    """Name of the browser used for Remote webdriver.

    Returns:
        str
    """
    return request.config.option.splinter_remote_name


@pytest.fixture(scope="session")  # pragma: no cover
def splinter_selenium_socket_timeout(request) -> int:
    """Set the internal Selenium socket timeout.

    ie: Communication between webdriver and the web browser.

    Returns:
        int: Timeout amount, in seconds.
    """
    return request.config.option.splinter_webdriver_socket_timeout


@pytest.fixture(scope="session")  # pragma: no cover
def splinter_selenium_implicit_wait(request):
    """Return Selenium implicit wait timeout.

    Returns:
        Selenium implicit wait, in seconds.
    """
    return request.config.option.splinter_webdriver_implicit_wait


@pytest.fixture(scope="session")  # pragma: no cover
def splinter_wait_time(request) -> int:
    """Splinter explicit wait timeout.

    Returns:
        int: Splinter wait time, in seconds.
    """
    return request.config.option.splinter_wait_time or 5


@pytest.fixture(scope="session")  # pragma: no cover
def splinter_selenium_speed(request) -> int:
    """Selenium speed, in seconds.

    Returns:
        int
    """
    return request.config.option.splinter_webdriver_speed


@pytest.fixture(scope="session")  # pragma: no cover
def splinter_browser_load_condition():
    """Return the condition that has to be `True` to assume that the page is fully loaded.

    One example is to wait for jQuery, then the condition could be::

        @pytest.fixture
        def splinter_browser_load_condition():

            def condition(browser):
                return browser.evaluate_script('typeof $ === "undefined" || !$.active')

            return condition
    """
    return lambda browser: True


@pytest.fixture(scope="session")  # pragma: no cover
def splinter_browser_load_timeout():
    """Return the timeout in seconds in which the page is expected to be fully loaded."""
    return 10


@pytest.fixture(scope="session")  # pragma: no cover
def splinter_file_download_dir(session_tmpdir):
    """Browser file download directory."""
    return session_tmpdir.ensure("splinter", "download", dir=True).strpath


@pytest.fixture(scope="session")  # pragma: no cover
def splinter_download_file_types():
    """Browser file types to download. Comma-separated."""
    return ",".join(mimetypes.types_map.values())


@pytest.fixture(scope="session")
def splinter_firefox_profile_preferences(splinter_file_download_dir, splinter_download_file_types):
    """Firefox profile preferences."""
    firefox_profile_preferences = {
        "browser.download.folderList": 2,
        "browser.download.manager.showWhenStarting": False,
        "browser.download.dir": splinter_file_download_dir,
        "browser.helperApps.neverAsk.saveToDisk": splinter_download_file_types,
        "browser.helperApps.alwaysAsk.force": False,
        "pdfjs.disabled": True,  # disable internal ff pdf viewer to allow auto pdf download
        "browser.cache.memory.enable": False,
        "browser.sessionhistory.max_total_viewers": 0,
        "network.http.pipelining": True,
        "network.http.pipelining.maxrequests": 8,
        "browser.startup.page": 0,
        "browser.startup.homepage": "about:blank",
        "startup.homepage_welcome_url": "about:blank",
        "startup.homepage_welcome_url.additional": "about:blank",
        "browser.startup.homepage_override.mstone": "ignore",
        "toolkit.telemetry.reportingpolicy.firstRun": False,
        "datareporting.healthreport.service.firstRun": False,
        "browser.cache.disk.smart_size.first_run": False,
        # Firefox hangs when the file is not found
        "media.gmp-gmpopenh264.enabled": False,
    }

    return firefox_profile_preferences


@pytest.fixture(scope="session")
def splinter_firefox_profile_directory():
    """Firefox profile directory."""
    return os.path.join(os.path.dirname(__file__), "profiles", "firefox")


@pytest.fixture(scope="session")
def splinter_driver_kwargs():
    """Keyword arguments for the driver.

    These values will take precedence over the plugin's default arguments
    for the driver.

    Returns:
        dict: A dict of keyword arguments for the driver defined by `splinter_webdriver`
    """
    return {}


@pytest.fixture(scope='session')
def splinter_logs_dir():
    """Name of the directory to place driver log files into."""
    return 'logs'


@pytest.fixture(scope='session')
def _splinter_driver_default_kwargs(splinter_logs_dir, splinter_remote_name):
    """Sane defaults for the various driver arguments."""
    os.makedirs(splinter_logs_dir, exist_ok=True)

    options = {
        'chrome': {},
        'firefox': {},
        'edge': {},
    }

    cwd = os.getcwd()

    driver_kwargs = {
        'chrome': {
            'executable_path': get_executable_path(cwd, 'chromedriver'),
            'service_args': [
                '--verbose',
                f"--log-path={splinter_logs_dir}/chromedriver.log",
            ],
            'options': options['chrome'],
        },
        'firefox': {
            'executable_path': get_executable_path(cwd, 'geckodriver'),
            'service_log_path': f"{splinter_logs_dir}/geckodriver.log",
            'options': options['firefox'],
        },
        'edge': {
            'executable_path': get_executable_path(cwd, 'edgedriver'),
            'options': options['edge'],
        },
        'remote': {},
        'django': {},
        'flask': {},
        'zope.testbrowser': {},
    }

    return driver_kwargs


@pytest.fixture(scope="session")
def splinter_window_size():
    """Browser window size. (width, height)."""
    return (1366, 768)


@pytest.fixture(scope="session")
def splinter_session_scoped_browser(request):
    """Flag to keep single browser per test session."""
    return request.config.option.splinter_session_scoped_browser == "true"


@pytest.fixture(scope="session")
def splinter_make_screenshot_on_failure(request):
    """Flag to make browser screenshot on test failure."""
    return request.config.option.splinter_make_screenshot_on_failure == "true"


@pytest.fixture(scope="session")  # pragma: no cover
def splinter_screenshot_dir(request):
    """Browser screenshot directory."""
    return os.path.abspath(request.config.option.splinter_screenshot_dir)


@pytest.fixture(scope="session")
def splinter_headless(request):
    """Flag to start the browser in headless mode."""
    return request.config.option.splinter_headless


@pytest.fixture(scope="session")  # pragma: no cover
def splinter_screenshot_encoding(request):
    """Browser screenshot html encoding."""
    return "utf-8"


@pytest.fixture(scope="session")
def browser_pool(request, splinter_close_browser):
    """Browser 'pool' to emulate session scope but with possibility to recreate browser."""
    pool = {}

    def fin():
        for browser in pool.values():
            try:
                browser.quit()
            except Exception:  # NOQA
                pass

    if splinter_close_browser:
        request.addfinalizer(fin)

    return pool


@pytest.fixture(scope="session")
def browser_patches():
    """Browser monkey patches."""
    patch_webdriver()


@pytest.fixture(scope="session")
def session_tmpdir(tmpdir_factory):
    """Pytest tmpdir which is session-scoped."""
    return tmpdir_factory.mktemp("pytest-splinter")


@pytest.fixture(scope="session")
def splinter_browser_class(request):
    """Browser class to use for browser instance creation."""
    return Browser


def get_args(
    driver=None,
    remote_url=None,
    headless=False,
    driver_kwargs=None,
):
    """Construct arguments to be passed to webdriver on initialization."""
    kwargs = {}

    # TODO: Splinter needs to support remote headless as an argument
    if headless and driver in ['firefox', 'chrome']:
        kwargs["headless"] = headless

    elif driver == "remote":
        kwargs["desired_capabilities"] = driver_kwargs.get(
            "desired_capabilities", {})

        if remote_url:
            kwargs["command_executor"] = remote_url
        kwargs["keep_alive"] = True

    if driver_kwargs:
        kwargs.update(driver_kwargs)
    return kwargs


@pytest.fixture(scope="session")
def splinter_clean_cookies_urls():
    """List of urls to clean cookies on their domains."""
    return []


def _take_screenshot(
    request,
    browser_instance,
    fixture_name,
    session_tmpdir,
):
    """Capture a screenshot as .png and .html.

    Invoked from session and function browser fixtures.
    """
    screenshot_dir = request.getfixturevalue('splinter_screenshot_dir')

    names = junitxml.mangle_test_address(request.node.nodeid)

    classname = ".".join(names[:-1])

    screenshot_dir = os.path.join(screenshot_dir, classname)

    name_0 = names[-1][:128 - len(fixture_name) - 5]

    screenshot_file_name = f"{name_0}-{fixture_name}".replace(os.path.sep, "-")

    slaveoutput = getattr(request.config, "workeroutput", None)
    if not slaveoutput:
        os.makedirs(screenshot_dir, exist_ok=True)
    else:
        screenshot_dir = session_tmpdir.ensure("screenshots", dir=True).strpath

    screenshot_path = os.path.join(screenshot_dir, screenshot_file_name)

    LOGGER.info(f"Saving screenshot to {screenshot_dir}")

    screenshot_html_path: str = ''
    screenshot_png_path: str = ''

    try:
        screenshot_html_path = browser_instance.html_snapshot(
            name=screenshot_path,
        )
    except Exception as e:  # NOQA
        warnings.warn(pytest.PytestWarning(
            "Could not save html snapshot: {}".format(e)))

    try:
        screenshot_png_path = browser_instance.screenshot(
            name=screenshot_path, unique_file=False,
        )
    except Exception as e:  # NOQA
        warnings.warn(pytest.PytestWarning(
            "Could not save screenshot: {}".format(e)))

    if request.node.splinter_failure.longrepr:
        reprtraceback = request.node.splinter_failure.longrepr.reprtraceback
        reprtraceback.extraline = _screenshot_extraline(
            screenshot_png_path, screenshot_html_path,
        )

    try:
        if slaveoutput is not None:
            encoding = request.getfixturevalue('splinter_screenshot_encoding')

            with codecs.open(
                screenshot_html_path, encoding=encoding,
            ) as html_fd:
                with open(screenshot_png_path, "rb") as fd:
                    slaveoutput.setdefault("screenshots", []).append(
                        {
                            "class_name": classname,
                            "files": [
                                {
                                    "file_name": screenshot_png_path,
                                    "content": fd.read(),
                                },
                                {
                                    "file_name": screenshot_html_path,
                                    "content": html_fd.read(),
                                    "encoding": encoding,
                                },
                            ],
                        },
                    )
    except Exception as e:  # NOQA
        warnings.warn(pytest.PytestWarning(
            "Could not save screenshot: {}".format(e)))


@pytest.yield_fixture(autouse=True)
def _browser_screenshot_session(
    request,
    session_tmpdir,
    splinter_session_scoped_browser,
    splinter_make_screenshot_on_failure,
):
    """Make browser screenshot on test failure."""
    yield

    # Screenshot for function scoped browsers is handled in browser_instance_getter
    if not splinter_session_scoped_browser:
        return

    fixture_values = getattr(request, "_fixture_values", {})

    for name, value in fixture_values.items():
        should_take_screenshot = (
            hasattr(value, "__splinter_browser__")
            and splinter_make_screenshot_on_failure
            and getattr(request.node, "splinter_failure", True)
        )

        if should_take_screenshot:
            _take_screenshot(
                request=request,
                fixture_name=name,
                session_tmpdir=session_tmpdir,
                browser_instance=value,
            )


def _setup_firefox_profile(request, options):
    """Put custom Firefox profile into an options object."""
    splinter_firefox_profile_directory = request.getfixturevalue(
        'splinter_firefox_profile_directory',
    )
    splinter_firefox_profile_preferences = request.getfixturevalue(
        'splinter_firefox_profile_preferences',
    )

    # Create custom profile
    options.set_preference('profile', splinter_firefox_profile_directory)

    # Set profile preferences
    for key, value in splinter_firefox_profile_preferences.items():
        options.set_preference(key, value)


@pytest.fixture(scope="session")
def browser_instance_getter(
    request,
    browser_patches,
    splinter_session_scoped_browser,
    splinter_browser_load_condition,
    splinter_browser_load_timeout,
    splinter_driver_kwargs,
    splinter_remote_name,
    splinter_make_screenshot_on_failure,
    splinter_remote_url,
    splinter_selenium_implicit_wait,
    splinter_wait_time,
    splinter_selenium_socket_timeout,
    splinter_selenium_speed,
    splinter_window_size,
    splinter_browser_class,
    splinter_clean_cookies_urls,
    splinter_headless,
    session_tmpdir,
    browser_pool,
):
    """Splinter browser instance getter.

    To be used for getting of plugin.Browser's instances.

    :return: function(parent). New instance of plugin.Browser class.
    """
    _chrome_options = request.getfixturevalue('chrome_options')
    _firefox_options = request.getfixturevalue('firefox_options')

    _default_kwargs = request.getfixturevalue(
        '_splinter_driver_default_kwargs')

    def get_browser(splinter_webdriver, retry_count=3):

        # Set options objects into kwargs
        if splinter_webdriver == 'chrome':
            _default_kwargs['chrome']['options'] = _chrome_options

        elif splinter_webdriver == 'firefox':
            _default_kwargs['firefox']['options'] = _firefox_options
            _setup_firefox_profile(request, _firefox_options)

        if splinter_remote_name == 'chrome':
            _default_kwargs['remote']['options'] = _chrome_options

        elif splinter_remote_name == 'firefox':
            _default_kwargs['remote']['options'] = _firefox_options
            _setup_firefox_profile(request, _firefox_options)

        kwargs = get_args(
            driver=splinter_webdriver,
            remote_url=splinter_remote_url,
            headless=splinter_headless,
            driver_kwargs={
                **_default_kwargs.get(splinter_webdriver, {}),
                **splinter_driver_kwargs,
            },
        )
        try:
            return splinter_browser_class(
                splinter_webdriver,
                visit_condition=splinter_browser_load_condition,
                visit_condition_timeout=splinter_browser_load_timeout,
                wait_time=splinter_wait_time,
                **kwargs,
            )
        except Exception:  # NOQA
            if retry_count > 1:
                return get_browser(splinter_webdriver, retry_count - 1)
            else:
                raise

    def prepare_browser(request, parent, retry_count=3):
        splinter_webdriver = request.getfixturevalue("splinter_webdriver")
        splinter_session_scoped_browser = request.getfixturevalue(
            "splinter_session_scoped_browser",
        )
        splinter_close_browser = request.getfixturevalue(
            "splinter_close_browser")
        browser_key = id(parent)
        browser = browser_pool.get(browser_key)
        if not splinter_session_scoped_browser:
            browser = get_browser(splinter_webdriver)
            if splinter_close_browser:
                request.addfinalizer(browser.quit)
        elif not browser:
            browser = browser_pool[browser_key] = get_browser(
                splinter_webdriver)

        if request.scope == "function":

            def _take_screenshot_on_failure():
                if splinter_make_screenshot_on_failure and getattr(
                    request.node, "splinter_failure", True,
                ):
                    _take_screenshot(
                        request=request,
                        fixture_name=parent.__name__,
                        session_tmpdir=session_tmpdir,
                        browser_instance=browser,
                    )

            request.addfinalizer(_take_screenshot_on_failure)

        try:
            if splinter_webdriver not in browser.driver_name.lower():
                return _replace_browser(
                    request, browser, retry_count, browser_pool, browser_key, parent,
                )

            if hasattr(browser, "driver"):
                browser.driver.implicitly_wait(splinter_selenium_implicit_wait)
                browser.driver.set_speed(splinter_selenium_speed)
                browser.driver.command_executor.set_timeout(
                    splinter_selenium_socket_timeout,
                )
                browser.driver.command_executor._conn.timeout = (
                    splinter_selenium_socket_timeout
                )
                if splinter_window_size:
                    browser.driver.set_window_size(*splinter_window_size)

            try:
                browser.cookies.delete_all()
            except (IOError, HTTPException, WebDriverException):
                LOGGER.warning("Error cleaning browser cookies", exc_info=True)

            for url in splinter_clean_cookies_urls:
                browser.visit(url)
                browser.cookies.delete_all()

            if hasattr(browser, "driver"):
                browser.visit_condition = splinter_browser_load_condition
                browser.visit_condition_timeout = splinter_browser_load_timeout

                # Let firefox preferences handle this.
                if splinter_webdriver != 'firefox':
                    browser.visit("about:blank")

        except (HTTPException, WebDriverException, MaxRetryError):
            return _replace_browser(
                request, browser, retry_count, browser_pool, browser_key, parent,
            )

        return browser

    def _replace_browser(request, browser, retry_count, browser_pool, browser_key, parent):
        splinter_webdriver = request.getfixturevalue("splinter_webdriver")

        # we lost browser, try to restore the justice
        try:
            browser.quit()
        except Exception:  # NOQA
            pass

        LOGGER.warning("Error preparing the browser", exc_info=True)

        if retry_count < 1:
            raise
        else:
            browser = browser_pool[browser_key] = get_browser(
                splinter_webdriver)
            prepare_browser(request, parent, retry_count - 1)

        return browser

    return prepare_browser


@pytest.fixture
def browser(request, browser_instance_getter):
    """Browser fixture."""
    return browser_instance_getter(request, browser)


@pytest.fixture(scope="session")
def session_browser(request, browser_instance_getter):
    """Session scoped browser fixture."""
    return browser_instance_getter(request, session_browser)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Assign the report to the item for futher usage."""
    outcome = yield
    rep = outcome.get_result()
    if rep.outcome == "failed":
        item.splinter_failure = rep
    else:
        item.splinter_failure = None


def pytest_configure(config):
    """Register pytest-splinter's deferred plugin."""
    if config.pluginmanager.getplugin("xdist"):
        screenshot_dir = os.path.abspath(config.option.splinter_screenshot_dir)
        config.pluginmanager.register(
            SplinterXdistPlugin(screenshot_dir=screenshot_dir),
        )


def pytest_addoption(parser):  # pragma: no cover
    """Pytest hook to add custom command line option(s)."""
    group = parser.getgroup(
        "splinter", "splinter integration for browser testing")
    group.addoption(
        "--splinter-webdriver",
        help="splinter: Name of the webdriver to use.",
        type=str,
        choices=list(splinter.browser._DRIVERS.keys()),
        dest="splinter_webdriver",
        metavar="DRIVER",
        default="firefox",
    )
    group.addoption(
        "--splinter-remote-url",
        help="splinter: URL for Remote Webdriver.",
        metavar="URL",
        dest="splinter_remote_url",
        default=None,
    )
    group.addoption(
        "--splinter-remote-name",
        help="splinter: Name of the browser to use when running Remote Webdriver.",
        metavar="BROWSER_NAME",
        dest="splinter_remote_name",
        default="chrome",
    )
    group.addoption(
        "--splinter-wait-time",
        help="splinter: Explicit wait, in seconds.",
        type=int,
        dest="splinter_wait_time",
        metavar="SECONDS",
        default=None,
    )
    group.addoption(
        "--splinter-implicit-wait",
        help="splinter: selenium implicit wait, in seconds",
        type=int,
        dest="splinter_webdriver_implicit_wait",
        metavar="SECONDS",
        default=5,
    )
    group.addoption(
        "--splinter-speed",
        help="splinter: selenium speed, in seconds",
        type=int,
        dest="splinter_webdriver_speed",
        metavar="SECONDS",
        default=0,
    )
    group.addoption(
        "--splinter-socket-timeout",
        help="splinter: socket timeout, in seconds",
        type=int,
        dest="splinter_webdriver_socket_timeout",
        metavar="SECONDS",
        default=120,
    )
    group.addoption(
        "--splinter-session-scoped-browser",
        help="splinter: Use a single browser instance per test session. Defaults to true.",
        action="store",
        dest="splinter_session_scoped_browser",
        metavar="false|true",
        type=str,
        choices=["false", "true"],
        default="true",
    )
    group.addoption(
        "--splinter-make-screenshot-on-failure",
        help="splinter: Take browser screenshots on test failure. Defaults to true.",
        action="store",
        dest="splinter_make_screenshot_on_failure",
        metavar="false|true",
        type=str,
        choices=["false", "true"],
        default="true",
    )
    group.addoption(
        "--splinter-screenshot-dir",
        help="splinter: Browser screenshot directory. Default is 'logs'.",
        action="store",
        dest="splinter_screenshot_dir",
        metavar="DIR",
        default="logs",
    )
    group.addoption(
        "--splinter-headless",
        help="splinter: Run the browser in headless mode.",
        action="store_true",
        dest="splinter_headless",
    )
