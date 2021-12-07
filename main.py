import sys
import argparse
from snatcher import NewsSnatcher, ComicSnatcher
from saver import save_as_file


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help = 'snatch wut')

    parserForComic = subparsers.add_parser('comic')
    parserForComic.add_argument('wut comic', choices = [ 'xkcd' ])

    args = parser.parse_args()
    if len(sys.argv) < 2:
        parser.print_help()
        exit(1)


    # santcher = ComicSnatcher()
    # save_as_file(santcher.snatch_xkcd(), "hmm.png")


if __name__ == '__main__':
    main()
