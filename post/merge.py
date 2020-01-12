#!/usr/bin/env python3
# -*- coding: utf8 -*-

import cv2 as cv
import pandas as pd
import os


def merge(offsetsfile, imagedir, outputfile):
    df = pd.read_csv(offsetsfile, index_col=0)
    d = df.to_dict(orient='index')

    file_img = min(d.keys())
    img = cv.imread(os.path.join(imagedir, file_img))
    current_x, current_y = 0, 0

    while file_img in d:
        c = d[file_img]
        x = c['x']
        y = c['y']

        file_ref = c['ref']
        path_ref = os.path.join(imagedir, file_ref)
        img_ref = cv.imread(path_ref)

        print(file_img, '->', file_ref, '|', x, y)

        # w, h of current image
        w_img, h_img = img.shape[1], img.shape[0]

        # relative x, relative y, w, h of next image
        x_ref, y_ref = current_x + x, current_y + y
        w_ref, h_ref = img_ref.shape[1], img_ref.shape[0]

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
        img[y_ref:y_ref+h_ref, x_ref:x_ref+w_ref] = img_ref

        current_x, current_y = x_ref, y_ref
        file_img = file_ref

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
