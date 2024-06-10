"""Browser instance getter tests."""
import pytest


@pytest.fixture(scope="session")
def splinter_session_scoped_browser():
    """Override to default to test getter twice."""
    return True


def test_browser_instance_getter(request, browser_instance_getter):
    """Test browser_instance_getter fixture.

    Test that it return a function and if run this function then each time we will get
    different instance of plugin.Browser class.
    """
    assert callable(browser_instance_getter)

    browser1 = browser_instance_getter(request, test_browser_instance_getter)

    def mock_func():
        return 1

    browser2 = browser_instance_getter(request, mock_func)

    assert hasattr(browser1, "visit_condition")
    assert hasattr(browser2, "visit_condition")

    assert browser1 is not browser2
