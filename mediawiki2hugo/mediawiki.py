import re
from collections import defaultdict

from .file import get_filename_for_title, get_filename_for_image

IMAGES = set()
PAGES = set()
REDIRECT_F2A = defaultdict(set)
REDIRECT_A2F = dict()


def get_tags(text):
    category_regexp = r"\[\[Category: ?([^\]]*)\]\]"
    tags = re.findall(category_regexp, text)
    text = re.sub(category_regexp, "", text)
    return tags, text


def replace_lists(text):
    text = re.sub(r"(^|\n)\*\*\*", r"\1  *", text)
    text = re.sub(r"(^|\n)\*\*", r"\1 *", text)
    text = re.sub(r"(^|\n)\*", r"\1*", text)

    # make sure there is an empty line before a list
    lines = text.split("\n")
    new_lines = []
    in_block = False
    for idx, line in enumerate(lines):
        matches = re.match(r"^\*", line)
        if not in_block and matches:
            in_block = True
            if not re.match(r"^$", lines[idx - 1]):
                new_lines.append("")
            new_lines.append(line)
        elif in_block and not matches:
            in_block = False
            new_lines.append(line)
        else:
            new_lines.append(line)

    return "\n".join(new_lines)


def replace_description(text):
    text = re.sub(r"(^|\n); ?(.[^:]*):(.*)", r"\1\n\2\n:\3", text)
    return text


def replace_numbering(text):
    text = re.sub(r"(^|\n)# ", r"\1 1. ", text)
    return text


def replace_code(text):
    lines = text.split("\n")
    new_lines = []
    in_block = False
    for line in lines:
        matches = re.match(r"^ (.+)", line)
        if not in_block and matches:
            in_block = True
            new_lines.append("```")
            new_lines.append(matches[1])

        elif in_block and matches:
            new_lines.append(matches[1])

        elif in_block and not matches:
            in_block = False
            new_lines.append("```")
            new_lines.append(line)

        else:
            new_lines.append(line)

    return "\n".join(new_lines)


def replace_images(text):
    # [[File:Connect-IOU-to-QEMU-ASA.jpg|400px]]
    # ![MPLS-Termionology](/MPLS-Termionology.png)
    image_regexp = r"\[\[File:([^\]\|]+)(\|[^\]\|]*)?\]\]"

    matches = re.findall(image_regexp, text)
    if matches:
        for match in matches:
            filename = get_filename_for_image(match[0])
            IMAGES.add(filename)
            # text = re.sub(image_regexp, r"![\1](/\1)", text)
            search = f"[[File:{filename}{match[1]}]]"
            replace = f"![{filename}](/{filename})"
            # print(match, search, replace)
            text = text.replace(search, replace)
    return text


def replace_links(text):
    # complex links
    # [[Internet Protocol#Tunnel Mechanisms|IPv6 Tunnel Types]]
    # [my first post]({{< ref "my-first-post.md" >}})
    ## link_regexp = r"\[\[([^\]\|]+)\|([^\]\|]+)\]\]"
    link_regexp = r"\[\[([^\]\|\#]+)(\#[^\]\|]+)?\|([^\]\|]+)\]\]"
    matches = re.findall(link_regexp, text)
    if matches:
        for match in matches:
            target = match[0]
            if target in REDIRECT_A2F:
                target = REDIRECT_A2F[target]
            PAGES.add(target)
            filename = get_filename_for_title(target)

            if len(match) == 2:
                search = f"[[{match[0]}|{match[1]}]]"
            if len(match) == 3:
                search = f"[[{match[0]}{match[1]}|{match[2]}]]"
            replace = f'[{match[0]}]({{{{< ref "{filename}" >}}}})'
            # print(match, search, replace)
            text = text.replace(search, replace)

    # complex links
    # [[Generic Routing Encapsulation]] (GRE)
    # [my first post]({{< ref "my-first-post.md" >}})
    link_regexp = r"\[\[([^\]]+)\]\] \(([^\)]+)\)"
    matches = re.findall(link_regexp, text)
    if matches:
        for match in matches:
            target = match[0]
            if target in REDIRECT_A2F:
                target = REDIRECT_A2F[target]
            PAGES.add(target)
            filename = get_filename_for_title(target)

            search = f"[[{match[0]}]] ({match[1]})"
            replace = f'[{match[0]}]({{{{< ref "{filename}" >}}}})'
            # print(match, search, replace)
            text = text.replace(search, replace)

    # simple links
    # [[Generic Routing Encapsulation]]
    # [my first post]({{< ref "my-first-post.md" >}})
    link_regexp = r"\[\[([^\]]+)\]\]"
    matches = re.findall(link_regexp, text)
    if matches:
        for match in matches:
            target = match
            if target in REDIRECT_A2F:
                target = REDIRECT_A2F[target]
            PAGES.add(target)
            filename = get_filename_for_title(target)

            search = f"[[{match}]]"
            replace = f'[{match}]({{{{< ref "{filename}" >}}}})'
            # print(match, search, replace)
            text = text.replace(search, replace)

    return text


def replace_headers(text):
    text = re.sub(r"====([^=]*)====", r"####\1", text)
    text = re.sub(r"===([^=]*)===", r"###\1", text)
    text = re.sub(r"==([^=]*)==", r"##\1", text)
    return text


def replace_syntax_highlight(text):
    # <syntaxhighlight lang="Python" line>
    # {{< highlight python "linenos=table,hl_lines=1 3" >}}
    text = re.sub(
        r'<syntaxhighlight lang="(.*)"( line)?>', r"{{< highlight \1>}}", text
    )
    # </syntaxhighlight>
    # {{</ highlight >}}
    text = text.replace("</syntaxhighlight>", "{{< / highlight >}}")

    text = text.replace("{{< highlight >}}", "{{< highlight bash>}}")
    return text


def replace_syntax(text):
    text = replace_code(text)
    text = replace_headers(text)
    text = replace_numbering(text)
    text = replace_description(text)
    text = replace_lists(text)
    text = replace_images(text)
    text = replace_links(text)
    text = replace_syntax_highlight(text)
    return text
