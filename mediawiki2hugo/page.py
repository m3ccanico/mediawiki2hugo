import hashlib
import re

from unidecode import unidecode
from xml.etree import ElementTree
from os import path
from jinja2 import Environment, FileSystemLoader
from shutil import copyfile

from .mediawiki import (
    replace_syntax,
    get_tags,
    IMAGES,
    PAGES,
    REDIRECT_F2A,
    REDIRECT_A2F,
)
from .file import get_filename

NAMESPACE = {"mediawiki": "http://www.mediawiki.org/xml/export-0.10/"}
BLACKLIST = ("Main Page",)


def get_template():
    file_loader = FileSystemLoader("mediawiki2hugo")
    env = Environment(loader=file_loader)
    return env.get_template("page.md")


def copy_images(image_source_path, image_destination_path):
    for image in IMAGES:
        md5_digest = hashlib.md5(image.encode()).hexdigest()
        first_folder = md5_digest[0]
        second_folder = md5_digest[0:2]
        image_source_file = path.join(
            image_source_path, first_folder, second_folder, image
        )
        image_destination_file = path.join(image_destination_path, image)
        if path.isfile(image_source_file):
            copyfile(image_source_file, image_destination_file)
        else:
            print(f"MISSING IMAGE: {image_source_file}")
        # print(image, md5_digest, image_source_file, image_destination_file)


def create_missing_pages(md_output_path):
    for page in PAGES:
        page_file = get_filename(page, md_output_path)
        if page not in REDIRECT_A2F and not path.isfile(page_file):
            # print(page_file)
            create_md(page, "placeholder", md_output_path)


def create_md(title, text, md_output_path):
    try:
        # category pages only contain the tag, ignore them
        tags, text = get_tags(text)
        if not text:
            return

        filename = get_filename(title, md_output_path)
        template = get_template()

        print("---", title)
        text = replace_syntax(text)

        output = template.render(
            title=title, text=text, tags=tags, aliases=REDIRECT_F2A[title]
        )

        md = open(filename, "w")
        md.write(output)
        md.close()
    except TypeError:
        print(title, text)


def find_redirects(root):
    for page in root.iterfind("mediawiki:page", NAMESPACE):
        title, text = parse_page(page)

        # ignore empty pages
        if not text:
            continue

        text = text.replace("#REDIRECT", "#redirect")

        if text.startswith("#redirect"):
            matches = re.findall(r"\#redirect \[\[(.*)\]\]", text)
            if matches:
                target = matches[0]
                REDIRECT_F2A[target].add(title)
                REDIRECT_A2F[title] = target


def parse_dump(dump_file, image_path, output_path):
    root = ElementTree.parse(dump_file).getroot()

    find_redirects(root)

    i = 0
    for page in root.iterfind("mediawiki:page", NAMESPACE):
        title, text = parse_page(page)
        if (
            not title.startswith("File:")
            and title not in BLACKLIST
            and text
            and not (text.startswith("#redirect") or text.startswith("#REDIRECT"))
        ):
            # if title in ("AWS - VPC",):
            # print("---", title[0:25], "\n", text[0:50])
            create_md(title, text, output_path)
            i += 1

        # if i > 20:
        #    break


def get_title(page):
    for title in page.iterfind("mediawiki:title", NAMESPACE):
        return title.text


def get_text(page):
    for revision in page.iterfind("mediawiki:revision", NAMESPACE):
        for text in revision.iterfind("mediawiki:text", NAMESPACE):
            return text.text


def parse_page(page):
    title = get_title(page)
    text = get_text(page)
    return title, text
