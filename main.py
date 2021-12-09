import sys
import argparse
from common import *
from snatcher import NewsSnatcher, ComicSnatcher, SnatchAttemptFailed
from saver import save_as_file


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help = 'snatch wut')

    parserForComic = subparsers.add_parser('comic')
    parserForComic.add_argument('wut_comic', choices = [ 'xkcd', 'ext' ])
    parserForComic.add_argument('--save-as', type = str, default = None, help = 'save comic as')
    parserForComic.add_argument('--download-from', type = str, default = None, help = 'download from this page')

    args = parser.parse_args()
    if len(sys.argv) < 2:
        parser.print_help()
        exit(1)


    if args.wut_comic == 'xkcd':
        santcher = ComicSnatcher()
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

    elif args.wut_comic == 'existential':
        pass


if __name__ == '__main__':
    main()
