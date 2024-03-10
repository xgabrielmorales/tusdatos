import html
import re


def sanitize_text(text: str) -> str:
    # Replace '&nbsp;' with an empty string.
    text = re.sub(r"&nbsp;", "", text)
    # Replace any HTML tag with an empty string.
    text = re.sub(r"<[^>]*>", "", text)
    # Replace '\n' or '\r\n' with an empty string.
    text = re.sub(r"[\r\n]+", "", text)
    # Replace html character entities
    text = html.unescape(text)

    return text
