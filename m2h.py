import click

from mediawiki2hugo.page import parse_dump, copy_images, create_missing_pages


@click.command()
@click.option("-d", "--dump", "dump_file", required=True, type=click.File())
@click.option(
    "-i",
    "--image",
    "image_source_path",
    required=True,
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
)
@click.option(
    "-o",
    "--md-ouptput",
    "md_output_path",
    required=True,
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
)
@click.option(
    "-a",
    "--image-destination",
    "image_destination_path",
    required=True,
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
)
def main(dump_file, md_output_path, image_source_path, image_destination_path):
    parse_dump(dump_file, image_source_path, md_output_path)
    copy_images(image_source_path, image_destination_path)
    create_missing_pages(md_output_path)


if __name__ == "__main__":
    main(None, None, None, None)
