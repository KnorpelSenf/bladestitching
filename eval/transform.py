#!/usr/bin/env python3
# -*- coding: utf8 -*-

from tqdm import tqdm
import numpy as np
import pandas as pd

# Transform [(i,j,a),(i,j+1,b),(i+1,j,c),(i+1,j+1,d)] to [[a,b],[c,d]]


def transform(filename, rows_idx, cols_idx, vals_idx, outfile):
    print('Reading data')
    in_df = pd.read_csv(filename)
    print('Transforming')
    raw = in_df.values
    t = raw.transpose()
    rows, cols = t[rows_idx], t[cols_idx]
    row_index, col_index = set(rows), set(cols)
    res = []
    for i in tqdm(row_index):
        row = []
        for j in col_index:
            val = raw[(rows == i) & (cols == j)][0][vals_idx]
            row.append(val)
        res.append(row)
    out_df = pd.DataFrame(res, index=row_index, columns=col_index)
    print('Writing output file')
    out_df.to_csv(outfile)
    print('Done.', outfile)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('input', help='Input CSV')
    parser.add_argument('row', type=int, help='row name')
    parser.add_argument('col', type=int, help='col name')
    parser.add_argument('val', type=int, help='val name')
    parser.add_argument('output', help='Output CSV')

    args = parser.parse_args()

    transform(args.input, args.row, args.col, args.val, args.output)
