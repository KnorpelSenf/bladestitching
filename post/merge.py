#!/usr/bin/env python3
# -*- coding: utf8 -*-

import cv2 as cv
import pandas as pd
import os


def merge(offsetsfile, imagedir, outputfile):
    df = pd.read_csv(offsetsfile, index_col=0)
    d = df.to_dict(orient='index')

    current = min(d.keys())
    img = cv.imread(os.path.join(imagedir, current))
    current_x, current_y = 0, 0

    while current in d:
        c = d[current]
        x = c['x']
        y = c['y']

        ref = c['ref']
        ref_path = os.path.join(imagedir, ref)
        ref_img = cv.imread(ref_path)

        print(current, '->', ref, '|', x, y)

        w_img, h_img = img.shape[0], img.shape[1]
        w_ref, h_ref = ref_img.shape[0], ref_img.shape[1]

        next_x, next_y = current_x + x, current_y + y

        border_right = max(0, next_x + w_ref - w_img)
        border_bottom = max(0, next_y + h_ref - h_img)

        if next_x < 0:
            border_left = -next_x
            next_x = 0
        else:
            border_left = 0

        if next_y < 0:
            border_top = -next_y
            next_y = 0
        else:
            border_top = 0

        img = cv.copyMakeBorder(img,
                                border_top, border_bottom, border_left, border_right,
                                0)

        img[next_x:w_ref, next_y:h_ref] = ref_img

        current = ref

    cv.imwrite(outputfile, img)
    print('Done.', os.path.abspath(outputfile))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('offsets',
                        help='Input file containing translations')
    parser.add_argument('input',
                        help='Image directory')
    parser.add_argument('output',
                        help='Output file')
    args = parser.parse_args()

    merge(args.offsets, args.input, args.output)
