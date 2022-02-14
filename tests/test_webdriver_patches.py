def test_speed(browser):
    """Test browser's driver set_speed and get_speed."""
    browser.driver.set_speed(2)
    assert browser.driver.get_speed() == 2


def test_get_current_window_info(browser):
    """Test browser's driver get_current_window_info."""
    assert len(browser.driver.get_current_window_info()) == 5


def test_current_window_is_main(browser):
    """Test browser's driver current_window_is_main."""
    assert browser.driver.current_window_is_main()
