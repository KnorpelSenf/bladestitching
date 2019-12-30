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

        # w, h of current image
        w_img, h_img = img.shape[0], img.shape[1]

        # relative x, relative y, w, h of next image
        x_ref, y_ref = current_x + x, current_y + y
        w_ref, h_ref = ref_img.shape[0], ref_img.shape[1]

        border_right = max(0, x_ref + w_ref - w_img)
        border_bottom = max(0, y_ref + h_ref - h_img)

        if x_ref < 0:
            border_left = -x_ref
            x_ref = 0
        else:
            border_left = 0

        if y_ref < 0:
            border_top = -y_ref
            y_ref = 0
        else:
            border_top = 0

        img = cv.copyMakeBorder(img,
                                border_top, border_bottom, border_left, border_right,
                                0)

        img[x_ref:x_ref+w_ref, y_ref:y_ref+h_ref] = ref_img

        current_x, current_y = x_ref, y_ref
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
