#!/usr/bin/env python3
# -*- coding: utf8 -*-

import os

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def plot(file, xlabel, ylabel, color='Blues', dpi=None, output=None):
    print('Loading data file')
    df = pd.read_csv(file, index_col=0)
    print('Plotting', file)
    sns.set()
    sns.heatmap(cmap=color, data=df)
    plt.xlabel(xlabel=xlabel)
    plt.ylabel(ylabel=ylabel)
    plt.yticks(rotation=0)
    if output is None:
        print('Here you go')
        plt.show()
    else:
        print('Done. Saving to', output)
        plt.savefig(output, dpi=dpi)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('data',
                        help='Input file')
    parser.add_argument('xlabel',
                        help='Label for x axis')
    parser.add_argument('ylabel',
                        help='Label for y axis')
    parser.add_argument('-c', '--color',
                        help='Color map to use, identified by name')
    parser.add_argument('--dpi', type=int, default=300,
                        help='Dpi to use')
    parser.add_argument('-o', '--output',
                        help='Store output')

    args = parser.parse_args()

    if not os.path.isfile(args.data):
        print('Please prove a file')
        exit(1)

    plot(args.data, args.xlabel, args.ylabel,
         color=args.color,
         dpi=args.dpi,
         output=args.output)
