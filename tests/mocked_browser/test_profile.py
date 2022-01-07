def test_firefox_profile(pytester):
    """Change firefox preferences.

    When the splinter_firefox_profile_preferences fixture is changed,
    Then the return value is still applied to the Options object.
    """

    pytester.makepyfile("""
        import pytest


        @pytest.fixture(scope="session")
        def splinter_firefox_profile_preferences():
            firefox_profile_preferences = {
                'browser.startup.page': 1,
                'browser.startup.homepage': "https://wikipedia.org",
            }

            return firefox_profile_preferences

        def test_firefox_profile_override(browser, firefox_options):
            assert firefox_options.preferences['browser.startup.page'] == 1
            assert firefox_options.preferences['browser.startup.homepage'] == "https://wikipedia.org"
    """)

    result = pytester.runpytest('-vv')
    assert 0 == result.ret
