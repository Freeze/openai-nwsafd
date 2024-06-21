# weather_utils/file_utils.py


def save_to_file(filename, content):
    """Saves the given content to a file."""
    with open(filename, "w") as file:
        file.write(content)


def load_from_file(filename):
    """Loads content from a file."""
    with open(filename, "r") as file:
        return file.read()
