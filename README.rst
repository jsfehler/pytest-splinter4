pytest-splinter4
================

A `pytest <http://pytest.org>`_ plugin for `splinter <https://splinter.readthedocs.io>`_.

pytest-splinter4 is a fork of `pytest-splinter <https://github.com/pytest-dev/pytest-splinter>`_
with added features and fixes to support newer versions of
``pytest``, ``pytest-xdist``, ``splinter >= 0.17.0``, and ``selenium >= 4.0``.

.. image:: https://img.shields.io/pypi/v/pytest-splinter4.svg
    :alt: PyPI
    :target: https://pypi.python.org/pypi/pytest-splinter4

.. image:: https://img.shields.io/pypi/pyversions/pytest-splinter4.svg
    :alt: PyPI - Python Version
    :target: https://pypi.python.org/pypi/pytest-splinter4

.. image:: https://img.shields.io/github/license/jsfehler/pytest-splinter4.svg
    :alt: GitHub
    :target: https://github.com/jsfehler/pytest-splinter4/blob/master/LICENSE

.. image:: https://github.com/jsfehler/pytest-splinter4/workflows/CI/badge.svg
    :target: https://github.com/jsfehler/pytest-splinter4/actions/workflows/main.yml
    :alt: Build status

.. image:: https://codecov.io/gh/jsfehler/pytest-splinter4/branch/master/graph/badge.svg?token=C1vfu8YgWn
   :target: https://codecov.io/gh/jsfehler/pytest-splinter4

.. image:: https://readthedocs.org/projects/pytest-splinter4/badge/?version=latest
    :target: https://readthedocs.org/projects/pytest-splinter4/?badge=latest
    :alt: Documentation Status


Installation
------------

.. code-block:: bash

    python -m pip install pytest-splinter4


Features
--------

Sensible Defaults
+++++++++++++++++


Driver executable_path argument
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
When using chrome, firefox, or edge, the `executable_path` driver argument has
a default value set to also search for chrome/gecko/edgedriver in the current working directory.


Browser Fixtures
++++++++++++++++

The following fixtures provide instances of ``splinter.Browser()``

* browser
    A new instance of splinter's Browser. Fixture is session scoped, so browser process is started
    once per test session, but the state of the browser will be clean (current page is ``blank``, cookies clean).

* browser_instance_getter
    Function to create an instance of the browser. This fixture is required only if you need to have
    multiple instances of the Browser in a single test at the same time. Example:

    .. code-block:: python

        @pytest.fixture
        def admin_browser(request, browser_instance_getter):
            """Admin browser fixture."""
            # browser_instance_getter function receives parent fixture -- our admin_browser
            return browser_instance_getter(request, admin_browser)

        def test_2_browsers(browser, admin_browser):
            """Test using 2 browsers at the same time."""
            browser.visit('http://google.com')
            admin_browser.visit('http://admin.example.com')

Selenium Fixtures
+++++++++++++++++

The following fixtures provide support for selenium parameters.
They are only used when Selenium based drivers are used.

* splinter_selenium_implicit_wait
    Implicit wait timeout to be passed to Selenium webdriver.
    Fixture gets the value from the command-line option splinter-implicit-wait (see below)

* splinter_selenium_speed
    Speed for Selenium, if not 0 then it will sleep between each selenium command.
    Useful for debugging/demonstration.
    Fixture gets the value from the command-line option splinter-speed (see below)

* splinter_selenium_socket_timeout
    Socket timeout for communication between the webdriver and the browser.
    Fixture gets the value from the command-line option splinter-socket-timeout (see below)

Splinter Fixtures
+++++++++++++++++

The following fixtures provide support for splinter parameters.

* splinter_wait_time
    Explicit wait timeout (for waiting for explicit condition via `wait_for_condition`).
    Default value is from the command-line option splinter-wait-time (see below)

* splinter_webdriver
    Splinter's webdriver name to use. Default value is from the command-line option
    splinter-webdriver (see below).

    To make pytest-splinter always use certain webdriver, override a fixture
    in your `conftest.py` file. Example:

    .. code-block:: python

        import pytest

        @pytest.fixture(scope='session')
        def splinter_webdriver():
            """Override splinter webdriver name."""
            return 'chrome'

* splinter_remote_url
    Webdriver remote url to use. Default value is from the command-line option
    splinter-remote-url (see below).

    This will only be used if the selected webdriver name is 'remote'.

* splinter_remote_name
    Name of the browser to use when running Remote Webdriver.

    This will be used only if the selected webdriver name is 'remote'.

* splinter_file_download_dir
    Directory, to which browser will automatically download the files it
    will experience during browsing. For example when you click on some download link.
    By default it's a temporary directory. Automatic downloading of files is only supported for firefox driver
    at the moment.

* splinter_download_file_types
    Comma-separated list of content types to automatically download.
    By default it's the all known system mime types (via mimetypes standard library).

* splinter_browser_load_condition
    Browser load condition, a python function which should return True.
    If function returns False, it will be run several times, until timeout below reached.

* splinter_browser_load_timeout
    Browser load condition timeout in seconds, after this timeout the exception
    WaitUntilTimeout will be raised.

* splinter_wait_time
    Browser explicit wait timeout in seconds, after this timeout the exception
    WaitUntilTimeout will be raised.

* splinter_driver_kwargs
    Webdriver keyword arguments, a dictionary which is passed to selenium
    webdriver's constructor (after applying firefox preferences)

    .. code-block:: python

        import pytest
        from pathlib import Path

        @pytest.fixture
        def splinter_driver_kwargs():
            """
            Webdriver kwargs for Firefox.
            https://selenium-python.readthedocs.io/api.html#module-selenium.webdriver.firefox.webdriver
            """
            return {"service_log_path": Path("/log/directory/geckodriver.log")}

* splinter_window_size
    Size of the browser window on browser initialization. Tuple in form (<width>, <height>). Default is (1366, 768)

* splinter_logs_dir
    Driver logs directory. Default is 'logs'.

* splinter_screenshot_dir
    Browser screenshot directory. Default is 'logs/{test_function_name}'.

    This fixture gets the value from the command-line option
    `splinter-screenshot-dir` (see below).

* splinter_make_screenshot_on_failure
    Should pytest-splinter take browser screenshots on test failure?
    This fixture gets the value from the command-line option
    `splinter-make-screenshot-on-failure` (see below).

* splinter_screenshot_encoding
    Encoding of the `html` `screenshot` on test failure. UTF-8 by default.

* splinter_browser_class
    Class to use for browser instance.
    Defaults to `pytest_splinter.plugin.Browser`.

* splinter_clean_cookies_urls
    List of additional urls to clean cookies on. By default, during the preparation of the browser for the test,
    pytest-splinter only cleans cookies for the last visited url from previous test, as it's not possible to clean
    all cookies from all domains at once via webdriver protocol, by design. This limitation can be worked around if
    you know the list of urls, the domains for which you need to clean cookies (for example https://facebook.com).
    If so, you can override this fixture and put those urls there, and pytest-splinter will visit each of them and will
    clean the cookies for each domain.

* splinter_headless
    Run Chrome in headless mode. Defaults to false. http://splinter.readthedocs.io/en/latest/drivers/chrome.html#using-headless-option-for-chrome

Firefox Only
~~~~~~~~~~~~

* splinter_firefox_profile_preferences
    Firefox profile preferences, a dictionary which is passed to selenium
    webdriver's profile_preferences

* splinter_firefox_profile_directory
    Firefox profile directory to use as template for firefox profile created by selenium.
    By default, it's an empty directly inside pytest_splinter/profiles/firefox

Command-line options
--------------------

* `--splinter-implicit-wait`
    Selenium webdriver implicit wait. Seconds (default: 5).

* `--splinter-speed`
    selenium webdriver speed (from command to command). Seconds (default: 0).

* `--splinter-socket-timeout`
    Selenium webdriver socket timeout for for communication between the webdriver and the browser.
    Seconds (default: 120).

* `--splinter-webdriver`
    Webdriver name to use. (default: firefox). Options:

    *  firefox
    *  remote
    *  chrome

    For more details refer to the documentation for splinter and selenium.

* `--splinter-remote-url`
    Webdriver remote url to use. (default: None). Will be used only if selected webdriver name is 'remote'.

    For more details refer to the documentation for splinter and selenium.

* `--splinter-remote-name`
    Name of the browser to use when running Remote Webdriver.

* `--splinter-make-screenshot-on-failure`
    pytest-splinter should take browser screenshots on test failure.
    Choices are 'true' or 'false' (default: 'true').

* `--splinter-screenshot-dir`
    pytest-splinter browser screenshot directory. Defaults to the current
    directory.

* `--splinter-headless`
    Override `splinter_headless` fixture. Choices are 'true' or 'false', default: 'true'.
    http://splinter.readthedocs.io/en/latest/drivers/chrome.html#using-headless-option-for-chrome
    https://splinter.readthedocs.io/en/latest/drivers/firefox.html#using-headless-option-for-firefox

Browser fixture
---------------

As mentioned above, the ``browser`` fixture is an instance of splinter's Browser object,
but with some overrides.

*  visit
    Added possibility to wait for condition on each browser visit by having a fixture.

*  wait_for_condition
    Method copying selenium's wait_for_condition, with difference that condition is in python,
    so there you can do whatever you want, and not only execute javascript via browser.evaluate_script.


Automatic screenshots on test failure
-------------------------------------

When a test fails, it's important to know the reason.
This becomes hard when tests are being run on the continuous integration server,
where you cannot debug (using --pdb).
To simplify things, a special behaviour of the browser fixture is available,
which takes a screenshot on test failure and puts it in a folder with the a
naming convention compatible to the
`jenkins plugin <https://wiki.jenkins-ci.org/display/JENKINS/JUnit+Attachments+Plugin>`_.
The html content of the browser page is also stored, this can be useful for debugging the html source.

Creating screenshots is fully compatible with `pytest-xdist plugin
<https://pypi.python.org/pypi/pytest-xdist>`_ and will transfer the screenshots
from the worker nodes through the communication channel automatically.

If a test (using the browser fixture) fails, you should get a screenshot files
in the following path:

::

    <splinter-screenshot-dir>/my.dotted.name.test.package/test_name-browser.png
    <splinter-screenshot-dir>/my.dotted.name.test.package/test_name-browser.html

The `splinter-screenshot-dir` for storing the screenshot is generated by a
fixture and can be provided through a command line argument, as described above
at the configuration options section.

Taking screenshots on test failure is enabled by default. It can be controlled
through the `splinter_make_screenshot_on_failure` fixture, where return `False`
skips it. You can also disable it via a command line argument:

::

    pytest tests/functional --splinter-make-screenshot-on-failure=false

In case taking a screenshot fails, a pytest warning will be issued, which
can be viewed using the `-rw` argument for `pytest`.


Example
-------

.. code-block:: python

    def test_using_a_browser(browser):
        """Test using real browser."""
        url = "http://www.google.com"
        browser.visit(url)

        browser.fill('q', 'splinter - python acceptance testing for web applications')

        # Find and click the 'search' button
        button = browser.find_by_name('btnK')

        # Interact with elements
        button.click()

        assert browser.is_text_present('splinter.cobrateam.info'), "splinter.cobrateam.info wasn't found... We need to"
        ' improve our SEO techniques'


Contact
-------

If you have questions, bug reports, suggestions, etc. please create an issue on
the `GitHub project page <http://github.com/jsfehler/pytest-splinter4>`_.


License
-------

This software is licensed under the `MIT license <http://en.wikipedia.org/wiki/MIT_License>`_

See `License file <https://github.com/jsfehler/pytest-splinter4/blob/master/LICENSE.txt>`_
