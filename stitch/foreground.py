#!/usr/bin/env python3
# -*- coding: utf8 -*-

import os

import cv2 as cv
import numpy as np
import pandas as pd
from tqdm import tqdm

import lineutils as ut
from lineutils import r, t, x, y


def foreground(hough, inputdir, outputdir, color=(0, 0, 0)):
    df = pd.read_csv(hough, index_col=0)
    lines_per_file = {file: list(zip(group_df['rho'], group_df['theta']))
                      for file, group_df in df.groupby(by='file')}

    for file in tqdm(list(sorted(lines_per_file.keys()))):
        img_path = os.path.join(inputdir, file)
        out_path = os.path.join(outputdir, file)
        lines = [ut.normalize(l) for l in lines_per_file[file]]

        # average rho value used to determine left/right sides of lines
        average_rho = (np.array([r(l) for l in lines])
                       .mean(0)
                       .astype(int))

        img = cv.imread(img_path)
        img_w, img_h = img.shape[1], img.shape[0]

        # used for cutting off left side
        left_side = [(0, img_h), (0, 0)]
        # used for cutting off right side
        right_side = [(img_w, img_h), (img_w, 0)]

        for line in lines:
            rho, theta = line

            cos_theta = np.cos(theta)
            if not cos_theta:  # line is exactly horizontal
                continue  # should not happen, but prevents both /0

            # x axis intersection
            top = (rho / cos_theta, 0)

            rho_bottom, theta_bottom = ut.move_origin(line, y=img_h)
            # line's intersection point with image's bottom border
            bottom = (rho_bottom / np.cos(theta_bottom), img_h)

            # polygon around left/right side of background
            polygon = np.array([top, bottom,
                                *(left_side if rho < average_rho else right_side)], dtype=int)

            cv.fillConvexPoly(img, polygon, color)

        cv.imwrite(out_path, img)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('hough',
                        help='Input file')
    parser.add_argument('input',
                        help='Image directory')
    parser.add_argument('-o', '--output',
                        help='Output file')
    parser.add_argument('-r', '--red', type=int, default=0,
                        help='Replace background with this red value')
    parser.add_argument('-g', '--green', type=int, default=0,
                        help='Replace background with this green value')
    parser.add_argument('-b', '--blue', type=int, default=0,
                        help='Replace background with this blue value')

    args = parser.parse_args()

    if not os.path.isfile(args.hough):
        print('Please provide a CSV file containing Hough files')
        exit(1)

    if not os.path.isdir(args.input):
        print('Please prove a directory containing the image files')
        exit(2)

    if not args.output:
        args.output = os.path.join(args.input, '_foreground')
        os.makedirs(args.output)
    foreground(args.hough, args.input, args.output,
               color=(args.blue, args.green, args.red))
