import os
import sys
import argparse
from typing import List
from common import *
from snatcher import NewsSnatcher, ComicSnatcherXkcd, ComicSnatcherExt, ComicSnatcherXkcdResult, SnatchAttemptFailed
from saver import save_as_file


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help = 'snatch wut')

    parserForComic = subparsers.add_parser('comic')
    parserForComic.add_argument('wut_comic', choices = [ 'xkcd', 'ext' ])
    parserForComic.add_argument('--save-as', type = str, default = None, help = 'save comic as')
    parserForComic.add_argument('--save-in', type = str, default = None, help = 'save comic in which folder?')
    parserForComic.add_argument('--download-from', type = str, default = None, help = 'download from this page')

    args = parser.parse_args()
    if len(sys.argv) < 2:
        parser.print_help()
        exit(1)


    if args.wut_comic == 'xkcd':
        santcher = ComicSnatcherXkcd()
        if args.save_as is None:
            args.save_as = f'{args.wut_comic}.png'

        try:
            snatched_bytes: bytes = santcher.snatch_xkcd()            \
                    if args.download_from is None                     \
                    else santcher.snatch_xkcd_from(args.download_from)
        except SnatchAttemptFailed as e:
            panic(f'failed snatch attempt: {e}')

        try:
            save_as_file(snatched_bytes, args.save_as)
        except Expection as e:
            LOG_ERROR("failed to write to file '{args.save_as}'");
            exit(1)

    elif args.wut_comic == 'ext':
        snatcher_ext = ComicSnatcherExt(args.download_from, args.save_in)

        try:
            snatcher_ext.save_as_folder()
        except FileExistsError:
            panic(f'folder already exists: "{args.save_in}"')
        except SnatchAttemptFailed as e:
            panic(f'failed snatch attempt: {e}')
        except Expection as e:
            panic("failed to store comics in '{args.save_in}': {e}")



if __name__ == '__main__':
    main()
