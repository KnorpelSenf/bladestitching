#!/usr/bin/env python3
# -*- coding: utf8 -*-

import cv2 as cv
import numpy as np
import os


def crop(imagefile, output, north=0, east=0, south=0, west=0):
    img = cv.imread(imagefile)
    cropped = img[north:-south-1, west:-east-1]
    cv.imwrite(output, cropped)
    print('Cropped', imagefile, 'to',  os.path.abspath(output))


def crop_all(imagedir, output, north=0, east=0, south=0, west=0):
    for file in sorted(os.listdir(imagedir)):
        imagefile = os.path.join(imagedir, file)
        outputfile = os.path.join(output, file)
        crop(imagefile, outputfile, north, east, south, west)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('input', help='Image file or directory')
    parser.add_argument('-o', '--output', help='Output file or directory')
    parser.add_argument('-n', '--north', type=int,
                        default=0, help='Trim from top')
    parser.add_argument('-s', '--south', type=int,
                        default=0, help='Trim from bottom')
    parser.add_argument('-e', '--east', type=int,
                        default=0, help='Trim from right')
    parser.add_argument('-w', '--west', type=int,
                        default=0, help='Trim from left')
    args = parser.parse_args()

    is_dir = os.path.isdir(args.input)

    if not args.output:
        if is_dir:
            args.output = os.path.join(args.input, os.path.pardir, 'cropped')
            os.makedirs(args.output, exist_ok=True)
        else:
            # split ext
            filename, ext = os.path.splitext(args.input)
            args.output = filename + '_cropped' + ext

    if is_dir:
        crop_all(args.input, args.output,
                 north=args.north, south=args.south, west=args.west, east=args.east)
    else:
        crop(args.input, args.output,
             north=args.north, south=args.south, west=args.west, east=args.east)
