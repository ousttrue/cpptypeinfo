import argparse
import os
import pathlib
import cpptypeinfo


def get_windowskits() -> pathlib.Path:
    # C:\Program Files (x86)\Windows Kits\10\Include
    program_files = pathlib.Path(os.environ['ProgramFiles(x86)'])
    include = program_files / 'Windows Kits/10/Include'
    dirs = [child for child in include.iterdir()]
    return sorted(dirs)[-1]


def debug(args):
    parser = cpptypeinfo.TypeParser()
    cpptypeinfo.parse_files(parser, pathlib.Path(args.header), debug=True)


def debug_args(subparsers: argparse._SubParsersAction):
    parser = subparsers.add_parser('debug', help='debug print')
    parser.set_defaults(func=debug)
    parser.add_argument('header')


def gen(args):
    parser = cpptypeinfo.TypeParser()
    headers = []
    if args.d3d11:
        dir = get_windowskits()
        headers.append(dir / 'um/d3d11.h')

    cpptypeinfo.parse_files(parser, *headers)

    if args.lang == 'dlang':

    else:
        raise NotImplementedError()


def gen_args(subparsers: argparse._SubParsersAction):
    parser = subparsers.add_parser('gen', help='generate code')
    parser.set_defaults(func=gen)
    parser.add_argument('--d3d11', action='store_true')
    parser.add_argument('--windows', action='store_true')
    parser.add_argument('lang', choices=['csharp', 'dlang'])


def main():
    '''
    cpptypeinfo gen -lib d3d11 -g dlang
    '''
    parser = argparse.ArgumentParser(description='cpptypeinfo')
    subparsers = parser.add_subparsers()

    debug_args(subparsers)
    gen_args(subparsers)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
