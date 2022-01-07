def test_chrome_options_ini(testdir):
    testdir.makeini("""
        [pytest]
        chrome_arguments =
            --disable-gpu
            --start-maximized
            disable-infobars
    """)

    testdir.makepyfile("""
        def test_one(chrome_options):
            expected = [
                '--disable-gpu', '--start-maximized', 'disable-infobars',
            ]
            assert chrome_options.arguments == expected

    """)

    result = testdir.runpytest('-v')

    assert result.ret == 0


def test_chrome_options_command_line(testdir):
    testdir.makepyfile("""
        def test_two(chrome_options):
            expected = [
                '--disable-gpu', '--start-maximized', 'disable-infobars',
            ]
            assert chrome_options.arguments == expected
    """)

    result = testdir.runpytest(
        '-v',
        '--chrome-arguments=--disable-gpu',
        '--chrome-arguments=--start-maximized',
        '--chrome-arguments=disable-infobars',
    )

    assert result
