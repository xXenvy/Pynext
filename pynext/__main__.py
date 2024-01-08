from argparse import ArgumentParser, Namespace

import platform
import sys

import aiohttp
import pynext


VERSION_OUTPUT = """
- Python: v{py.major}.{py.minor}.{py.micro}-{py.releaselevel}
- Pynext: v{mafic}
- Aiohttp: v{aiohttp}
- System info: {uname.system} {uname.release} {uname.version}
""".strip()


def core(_parser: ArgumentParser, args: Namespace) -> None:
    if args.version:
        version = pynext.__version__
        uname = platform.uname()
        print(
            VERSION_OUTPUT.format(
                py=sys.version_info,
                mafic=version,
                aiohttp=aiohttp.__version__,
                uname=uname,
            )
        )


def parse_args() -> tuple[ArgumentParser, Namespace]:
    parser = ArgumentParser(prog="pynext", description="CLI tools for pynext")
    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        help="Shows pynext version and system info.",
    )
    return parser, parser.parse_args()


def main() -> None:
    parser, args = parse_args()
    core(parser, args)


if __name__ == "__main__":
    main()
