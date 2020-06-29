
def write2file(fn: str, content: str) -> None:
    with open(fn, 'w') as _f:
        _f.write(content)
