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

    for i in range(0, length):
        window = range(
            max(i - diff, 0),
            min(i + diff + 1, length)
        )
        coords = [(xs[file], ys[file]) for file in window]
        res_x, res_y = np.array(coords).mean(0).astype(int)
        res_xs.append(res_x)
        res_ys.append(res_y)

    res = pd.DataFrame({
        'ref': res_ref,
        'x': res_xs,
        'y': res_ys
    }, index=res_index)
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
    args = parser.parse_args()

    if not args.output:
        args.output = os.path.join(
            os.path.dirname(args.translations),
            'translations_averaged.csv'
        )
        print(args.output)

    average(args.translations, args.output, args.window_size)
