def test_driverless_splinter_browsers(pytester):
    """Test: Use non-selenium driver for splinter_webdriver fixture

    When splinter_webdriver is changed to a non-selenium driver
    Then the browser fixture can be loaded successfully
    """

    pytester.makepyfile("""
        import pytest

        @pytest.fixture(scope='session')
        def splinter_webdriver():
            return 'django'


        def test_non_selenium(browser):
            assert browser.driver_name == 'django'
    """)

    result = pytester.runpytest('-v')
    assert result.ret == 0
