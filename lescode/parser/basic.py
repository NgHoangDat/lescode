import re
import json


def camel2snake(text: str, **kwargs) -> str:
    text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
    text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text)
    return text.lower()


def snake2camel(text: str, **kwargs) -> str:
    text = text.split("_")
    text = text[0] + "".join(map(str.capitalize, text[1:]))
    return text


def parse_json(**kwargs):
    return json.dumps(
        {snake2camel(k): v for k, v in kwargs.items()}, ensure_ascii=False
    )
