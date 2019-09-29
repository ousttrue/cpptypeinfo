import pathlib
import cpptypeinfo


def generate(parser: cpptypeinfo.TypeParser, dst: pathlib.Path) -> None:
    print(dst)
