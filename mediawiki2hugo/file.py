from unidecode import unidecode
from os import path


def get_filename_for_image(filename):
    filename = filename.replace(" ", "_")
    return filename


def get_filename_for_title(title):
    filename = title.replace(" - ", "-")
    filename = filename.replace(" ", "-")
    filename = filename.replace("/", "-")
    filename = filename.replace("#", "-")
    filename = unidecode(filename)
    filename = f"{filename}.md"

    return filename


def get_filename(title, output_path):
    filename = get_filename_for_title(title)
    return path.join(output_path, filename)
