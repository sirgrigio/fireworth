import re

def lowerdashed(value: str) -> str:
    return re.sub(r'\s+', '-', value.lower().replace('&', 'and').replace(':', ' ')) if value else value

def camelcased(value: str) -> str:
    return ' '.join([w.title() if w.islower() else w for w in value.split()]) if value else value
