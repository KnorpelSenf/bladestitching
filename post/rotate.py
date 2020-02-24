#!/usr/bin/env python3
# -*- coding: utf8 -*-

import cv2 as cv
import numpy as np
import os


def rotate(imagefile, angle, output):
    img = cv.imread(imagefile)

    img_center = tuple(np.array(img.shape[1::-1]) / 2)
    rot_mat = cv.getRotationMatrix2D(img_center, angle, 1)
    result = cv.warpAffine(
        img, rot_mat, img.shape[1::-1], flags=cv.INTER_LINEAR)

    cv.imwrite(output, result)
    print('Rotated', imagefile, 'by', angle, 'to', os.path.abspath(output))


def rotate_all(imagedir, angle, output):
    for file in sorted(os.listdir(imagedir)):
        imagefile = os.path.join(imagedir, file)
        outputfile = os.path.join(output, file)
        rotate(imagefile, angle, outputfile)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('input', help='Image file or directory')
    parser.add_argument('-o', '--output', help='Output file or directory')
    parser.add_argument('-a', '--angle', type=float, default=-90,
                        help='Rotation angle, positive values mean counter-clockwise')
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
        rotate_all(args.input, args.angle, args.output)
    else:
        rotate(args.input, args.angle, args.output)
