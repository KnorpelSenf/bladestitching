#!/usr/bin/env python3
# -*- coding: utf8 -*-

import cv2 as cv
import os


def rotate(imagefile, output):
    img = cv.imread(imagefile)
    img = cv.rotate(imagefile, rotateCode=cv.ROTATE_90_CLOCKWISE)
    cv.imwrite(output, img)
    print('Rotated', imagefile, 'to', os.path.abspath(output))


def rotate_all(imagedir, output):
    for file in sorted(os.listdir(imagedir)):
        imagefile = os.path.join(imagedir, file)
        outputfile = os.path.join(output, file)
        rotate(imagefile, outputfile)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('input', help='Image file or directory')
    parser.add_argument('-o', '--output', help='Output file or directory')
    args = parser.parse_args()

    is_dir = os.path.isdir(args.input)

    if not args.output:
        if is_dir:
            args.output = os.path.join(args.input, os.path.pardir, 'rotated')
            os.makedirs(args.output, exist_ok=True)
        else:
            # split ext
            filename, ext = os.path.splitext(args.input)
            args.output = filename + '_rotated' + ext

    if is_dir:
        rotate_all(args.input, args.output)
    else:
        rotate(args.input, args.output)
