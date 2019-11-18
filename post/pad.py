#!/usr/bin/env python3
# -*- coding: utf8 -*-

import os

import cv2 as cv

import pandas as pd


def pad(imagedir, translations, output):
    df = pd.read_csv(translations, index_col=0)
    xs = df['x']
    ys = df['y']
    for file in df.index:
        in_path = os.path.join(imagedir, file)
        out_path = os.path.join(output, file)

        img = cv.imread(in_path)
        x = xs[file]
        y = ys[file]

        top, bottom = (-y, 0) if y < 0 else (0, y)
        left, right = (-x, 0) if x < 0 else (0, x)

        top, bottom, left, right = int(top), int(bottom), int(left), int(right)

        img = cv.copyMakeBorder(img, top, bottom, left, right,  0)

        cv.imwrite(out_path, img)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('input', help='Image file or directory')
    parser.add_argument('translations', help='Scaling factor')
    parser.add_argument('-o', '--output', help='Output file or directory')
    args = parser.parse_args()

    is_dir = os.path.isdir(args.input)

    if not args.output:
        args.output = os.path.join(args.input, os.path.pardir, 'padded')
        os.makedirs(args.output, exist_ok=True)

    pad(args.input, args.translations, args.output)
