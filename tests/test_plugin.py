"""Tests for pytest-splinter plugin."""
import os.path
import time
import socket

import pytest

from splinter.driver import DriverAPI


@pytest.fixture
def simple_page_content():
    """Return simple page content."""
    return """<html xmlns="http://www.w3.org/1999/xhtml"><head></head>
    <body>
        <div id="content">
            <p>
                Some <strong>text</strong>
            </p>
        </div>
        <textarea id="textarea">area text</textarea>
    </body>
</html>"""


@pytest.fixture
def simple_page(httpserver, browser, simple_page_content):
    """Serve simple html page."""
    httpserver.serve_content(
        simple_page_content, code=200, headers={"Content-Type": "text/html"}
    )
    browser.visit(httpserver.url)


def test_browser(browser):
    """Check the browser fixture."""
    assert isinstance(browser, DriverAPI)


def test_session_browser(session_browser):
    """Check the browser fixture."""
    assert isinstance(session_browser, DriverAPI)


@pytest.mark.skip(reason="Unnecessary test")
@pytest.mark.parametrize(
    ("file_extension", "mime_type"),
    (
        ["txt", "text/plain"],
        ["pdf", "application/pdf"],
    ),
)
def test_download_file(
    httpserver,
    browser,
    splinter_file_download_dir,
    file_extension,
    mime_type,
    splinter_webdriver,
):
    """Test file downloading and accessing it afterwise."""
    if splinter_webdriver in ["zope.testbrowser"]:
        pytest.skip("{} doesn't support file downloading".format(splinter_webdriver))
    if splinter_webdriver in ["firefox"]:
        pytest.skip("Bug: https://bugzilla.mozilla.org/show_bug.cgi?id=1366035")
    file_name = "some.{}".format(file_extension)
    httpserver.serve_content(
        "Some text file",
        code=200,
        headers={
            "Content-Disposition": "attachment; filename={}".format(file_name),
            "Content-Type": mime_type,
        },
    )

    time.sleep(5)
    browser.visit(httpserver.url)

    file_path = os.path.join(splinter_file_download_dir, file_name)
    with open(file_path, "r") as f:
        assert f.read() == "Some text file"


@pytest.mark.parametrize("cookie_name", ["name1", "name2"])
@pytest.mark.parametrize("splinter_webdriver", ["firefox"])
def test_clean_cookies(
    httpserver,
    browser,
    cookie_name,
    splinter_webdriver,
    splinter_session_scoped_browser,
):
    """Test that browser has always clean state (no cookies set)."""
    assert not browser.cookies.all()
    httpserver.serve_content(
        """
        <html>
            <body>
                <script>
                    document.cookie = '{name}=value'
                </script>
            </body>
        </html>""".format(
            name=cookie_name
        ),
        code=200,
        headers={"Content-Type": "text/html"},
    )
    browser.visit(httpserver.url)
    assert browser.cookies.all() == {cookie_name: "value"}


@pytest.mark.parametrize("check", [1, 2])
@pytest.mark.parametrize("splinter_webdriver", ["firefox"])
def test_restore_browser(browser, simple_page, check, splinter_webdriver):
    """Test that browser is restored after failure automatically."""
    browser.quit()


@pytest.mark.parametrize("splinter_webdriver", ["firefox", "remote"])
def test_restore_browser_connection(
    browser, httpserver, simple_page, splinter_webdriver
):
    """Test that browser connection is restored after failure automatically."""
    def raises(*args, **kwargs):
        raise socket.error()

    browser.driver.command_executor._conn.request = raises
    browser.reload()
