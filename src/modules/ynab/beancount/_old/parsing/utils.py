import re


def travel_name_to_tag(name: str) -> str:
    prefix, title = name.lower().replace('&', 'and').split(':')
    return prefix + '-' + re.sub(r'\s+', '-', title.strip())
