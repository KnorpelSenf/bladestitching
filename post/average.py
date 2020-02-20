#!/usr/bin/env python3
# -*- coding: utf8 -*-

import os
import pandas as pd
import numpy as np


def average(translations, output, window_size=5):
    df = pd.read_csv(translations, index_col=0)
    index = list(df.index.values)
    xs = df['x']
    ys = df['y']
    length = len(index)
    diff = int(window_size / 2)

    res_index = index
    res_ref = df['ref']
    res_xs = []
    res_ys = []

    windows = (range(
        max(i - diff, 0),
        min(i + diff + 1, length)
    ) for i in range(0, length))

    coords = ([
        xs[file] if args.x_only else
        ys[file] if args.y_only else
        (xs[file], ys[file]) for file in window
    ] for window in windows)

    avgs = (np.array(values).mean(0).astype(int)
            for values in coords)

    res_df = {'ref': res_ref}

    if args.x_only:
        res_df['x'] = avgs
        res_df['y'] = ys
    elif args.y_only:
        res_df['x'] = xs
        res_df['y'] = avgs
    else:
        res_x, res_y = zip(*avgs)
        res_df['x'] = res_x
        res_df['y'] = res_y

    res = pd.DataFrame(res_df, index=res_index)
    res.to_csv(output)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('translations', help='Input file')
    parser.add_argument(
        '-o', '--output', help='Output file')
    parser.add_argument('-s', '--window-size', default=5, type=int,
                        help='Size of sliding window used for averaging')
    parser.add_argument('-y', '--y-only', action='store_true',
                        help='Only apply averaging to y column')
    parser.add_argument('-x', '--x-only', action='store_true',
                        help='Only apply averaging to x column')
    args = parser.parse_args()

    if not args.output:
        args.output = os.path.join(
            os.path.dirname(args.translations),
            'translations_averaged.csv'
        )
        print(args.output)

    average(args.translations, args.output, args.window_size)
