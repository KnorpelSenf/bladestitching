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
    xs = reasonable['x']
    ys = reasonable['y']
    M = (np.absolute(np.array(xs)) + np.absolute(np.array(ys))).max()

    print(len(df.index), 'files supplied, only',
          len(files), 'have reasonable values (< 800px L1-translation):')
    print(files)
    print('Reference padding is', M)
    for file in tqdm(files):
        in_path = os.path.join(imagedir, file)
        out_path = os.path.join(output, file)
        ref_path = os.path.join(reference, file)

        img = cv.imread(in_path)

        ref = cv.copyMakeBorder(img, M, M, M, M, 0)
        cv.imwrite(ref_path, ref)

        x = xs[file]
        y = ys[file]

        # print('Next image is', x, 'pixels further right and',
        #       y, 'pixels further down')

        top, bottom = M - y, M + y
        left, right = M - x, M + x

        # print('Padding of this image is therefore top =', top, '| bottom =',
        #       bottom, '| left =', left, '| right =', right)

        out = cv.copyMakeBorder(img, top, bottom, left, right, 0)
        cv.imwrite(out_path, out)


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
