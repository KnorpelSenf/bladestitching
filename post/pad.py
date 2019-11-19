#!/usr/bin/env python3
# -*- coding: utf8 -*-

import os
import cv2 as cv
import pandas as pd
import numpy as np
from tqdm import tqdm


def pad(imagedir, translations, output, reference):
    df = pd.read_csv(translations, index_col=0)
    reasonable = df[abs(df['x']) < 800]
    reasonable = reasonable[abs(reasonable['y']) < 800]
    files = reasonable.index
    refs = reasonable['ref']
    xs = reasonable['x']
    ys = reasonable['y']

    print(len(df.index), 'files supplied, only',
          len(files), 'have reasonable values (< 800px L1-translation):')
    print(files)

    for file in tqdm(files):
        ref = refs[file]
        x = xs[file]
        y = ys[file]

        in_path_file = os.path.join(imagedir, file)
        in_path_ref = os.path.join(imagedir, ref)

        out_path_file = os.path.join(output, file)
        out_path_ref = os.path.join(reference, ref)

        img = cv.imread(in_path_file)
        ref_img = cv.imread(in_path_ref)

        # print(ref, 'is', x, 'pixels further right and',
        #       y, 'pixels further down than', file)

        top_file, bottom_file = (0, y) if y > 0 else (-y, 0)
        left_file, right_file = (0, x) if x > 0 else (-x, 0)

        top_ref, bottom_ref = (y, 0) if y > 0 else (0, -y)
        left_ref, right_ref = (0, x) if x > 0 else (0, -x)

        out_img = cv.copyMakeBorder(img,
                                    top_file, bottom_file, left_file, right_file,
                                    0)
        out_ref = cv.copyMakeBorder(ref_img,
                                    top_ref, bottom_ref, left_ref, right_ref,
                                    0)
        cv.imwrite(out_path_file, out_img)
        cv.imwrite(out_path_ref, out_ref)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('input', help='Input directory')
    parser.add_argument(
        'translations', help='CSV file containing x,y offsets between images')
    parser.add_argument(
        '-o', '--output', help='Output directory of padded files')
    parser.add_argument('-r', '--reference',
                        help='Output directory of reference images')
    args = parser.parse_args()

    is_dir = os.path.isdir(args.input)

    if not args.output:
        args.output = os.path.join(args.input, os.path.pardir, 'padded')
        os.makedirs(args.output, exist_ok=True)
    if not args.reference:
        args.reference = os.path.join(args.input, os.path.pardir, 'reference')
        os.makedirs(args.reference, exist_ok=True)

    pad(args.input, args.translations, args.output, args.reference)
