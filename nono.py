#!/usr/bin/env python

'''
Usage: nono.py [ <filename> | <line-descriptor>... ]

A <line-descriptor> is a set of numbers separated by commas or spaces.
If an argument not matching that format is found, it's treated as a filename from which the line-descriptors are read, one per line of the file.

Line-descriptors are parsed from the left column to the right column and then from the top row to the bottom row.  Within each line-descriptor, the numbers represent the blocks of filled-in squares from left-to-right or from top-to-bottom.

        11
     11 11
     31311
2 2  ##x##
  3  ..#..
1 3  #x###
1 1  #.#..
2 2  ##x##

This would be represented as:
1,3 1,1 3 1,1,1 1,1,1 2,2 3 1,3 1,1 2,2

The size of the puzzle is determined from the number of line descriptors.
'''

import argparse
import itertools
import nonoboard
import re
import sys

if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument('--stepwise', action='store_true', default=False, help='''Show the results of solving after each step.''')
    ap.add_argument('--rows', nargs='+', help='''The row descriptors starting with the topmost row.  Each descriptor is a comma-separated list of the span lengths for that row or column.''')
    ap.add_argument('--columns', nargs='+', help='''The column descriptors starting with the leftmost column.  Each descriptor is a comma-separated list of the span lengths for that row or column.''')
    ap.add_argument('descriptors', nargs='*', help='''The column and row descriptors.  Must be specified if `--rows` and `--columns` are not.  Descriptors are listed first for the columns, starting with the leftmost column, then for the rows, beginning with the topmost row.  Each descriptor is a comma-separated list of the span lengths for that row or column.''')

    args = ap.parse_args()

    if (
                (args.rows and not args.columns)
                or (not args.rows and args.columns)
            ):
        ap.error('''Both --rows and --columns must be specified if either is.''')

    # until we allow non-square boards...
    if args.rows and len(args.rows) != len(args.columns):
        ap.error('''Both --rows and --columns must have the same number of descriptors.''')

    if args.descriptors and args.rows:
        ap.error('''Cannot specify --rows/--columns and generic descriptors at the same time.''')

    if len(args.descriptors) % 2:
        ap.error('''Must provide an even number of descriptors.''')

    descriptors = (args.columns + args.rows) if args.rows else args.descriptors

    re_sep = re.compile(r'''(?:,| +)''')
    i = 0
    while i < len(descriptors):
        d = re_sep.split(descriptors[i].strip())
        if all(part.isdigit() for part in d):
            descriptors[i] = tuple(int(part) for part in d)
            i += 1
        else:
            descriptors[i:i+1] = [
                        line.strip()
                        for line in open(descriptors[i]).readlines()
                        if line.strip()
                    ]

    size = len(descriptors)//2
    colspecs = descriptors[:size]
    rowspecs = descriptors[size:]
    nono = nonoboard.NonoBoard(size, descriptors[size:], descriptors[:size])

    rowpfx = [
                '/'.join(
                    str(span)
                    for span in spec
                )
                for spec in rowspecs
            ]
    maxpfx = max(len(pfx) for pfx in rowpfx)
    rowpfx = [f'''{pfx:>{maxpfx}}  ''' for pfx in rowpfx]

    colhdr = [
                '/'.join(
                    str(span)
                    for span in spec
                )
                for spec in colspecs
            ]
    maxhdr = max(len(hdr) for hdr in colhdr)
    colhdr = (
                [
                    f'''{"":>{maxpfx}}  {" ".join(hdr)}'''
                    for hdr in zip(*(
                        f'''{hdr:>{maxhdr}}'''
                        for hdr in colhdr
                    ))
                ]
                + ['']
            )

    header_and_board = lambda nono: (
                '\n'.join(
                    itertools.chain(
                        colhdr,
                        (
                            ''.join((row[0], ''.join(f'''{cell}{cell}''' for cell in row[1])))
                            for row in zip(rowpfx, nono.board)
                        )
                    )
                )
            )

    while not nono.is_solved:
        if args.stepwise:
            print(header_and_board(nono))
            ans = None
            while not isinstance(ans, bool):
                if ans is None:
                    print('''\nContinue?''', end=' ', flush=True)
                else:
                    print('''\nPlease answer 'yes' or 'no'.  Continue?''', end=' ', flush=True)
                ans = sys.stdin.readline().strip().lower()
                if ans == 'y' or ans == 'yes':
                    ans = True
                elif ans == 'n' or ans == 'no':
                    ans = False
            if not ans:
                break
        next_board = nono.resolve_once()
        if not next_board:
            break
        nono = next_board

    if nono.is_solved:
        print('\nSolved!')
    else:
        print('\nUnsolvable?!?')

    print(header_and_board(nono))

