import os


def get_executable_path(root: str, file_name: str) -> str:
    """Check if a file name is in the current working directory.

    If so, return the full path.
    If not, return the file name.

    Arguments:
        root (str): The assumed location of the file.
        file_path (str): The name of the file.

    Returns:
        str: An assumed valid path for the file.

    Example:
        >>> from automation_utils import get_executable_path
        >>>
        >>> cwd = os.getcwd()
        >>> result = get_executable_path(cwd, 'chromedriver')
    """
    os_correct_file_name = {
        'nt': f'{file_name}.exe',
        'posix': file_name,
    }
    _file_name = os_correct_file_name[os.name]
    full_file_path = os.path.join(root, _file_name)

    if not os.path.isfile(full_file_path):
        full_file_path = _file_name

    return full_file_path
