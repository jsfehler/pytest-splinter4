def test_firefox_options_ini(testdir):
    testdir.makeini("""
        [pytest]
        firefox_arguments =
            -private-window
            -foreground
    """)

    testdir.makepyfile("""
        def test_one(firefox_options):
            expected = [
                '-private-window', '-foreground',
            ]
            assert firefox_options.arguments == expected

    """)

    result = testdir.runpytest('-v')

    assert result.ret == 0


def test_firefox_options_command_line(testdir):
    testdir.makepyfile("""
        def test_two(firefox_options):
            expected = [
                '-private-window', '-foreground',
            ]
            assert firefox_options.arguments == expected
    """)

    result = testdir.runpytest(
        '-v',
        '--firefox-arguments=-private-window',
        '--firefox-arguments=-foreground',
    )

    assert result
