#!/usr/bin/env python3
# -*- coding: utf8 -*-

import cv2 as cv
import numpy as np
import os


def scale(imagefile, output, factor, interpolation=cv.INTER_LINEAR):
    img = cv.imread(imagefile)
    img = cv.resize(img, None, fx=factor, fy=factor,
                    interpolation=interpolation)
    cv.imwrite(output, img)
    print('Scaled', 'up' if factor > 1 else
          'down' if factor < 1 else
          'without change', imagefile, 'to',  os.path.abspath(output))


def scale_all(imagedir, output, factor, interpolation=cv.INTER_LINEAR):
    for file in sorted(os.listdir(imagedir)):
        imagefile = os.path.join(imagedir, file)
        outputfile = os.path.join(output, file)
        scale(imagefile, outputfile, factor, interpolation=interpolation)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('input', help='Image file or directory')
    parser.add_argument('factor', type=float, help='Scaling factor')
    parser.add_argument('-o', '--output', help='Output file or directory')
    parser.add_argument('-a', '--area', dest='interpolation', action='store_const',
                        const=cv.INTER_AREA, help='Use area interpolation (cv.INTER_AREA)')
    parser.add_argument('-c', '--cubic', dest='interpolation', action='store_const',
                        const=cv.INTER_CUBIC, help='Use cubic interpolation (cv.INTER_CUBIC)')
    parser.add_argument('-l', '--linear', dest='interpolation', action='store_const',
                        const=cv.INTER_LINEAR, help='Use linear interpolation (cv.INTER_LINEAR)')
    args = parser.parse_args()

    is_dir = os.path.isdir(args.input)

    if not args.output:
        if is_dir:
            args.output = os.path.join(args.input, os.path.pardir, 'scaled')
            os.makedirs(args.output, exist_ok=True)
        else:
            # split ext
            filename, ext = os.path.splitext(args.input)
            args.output = filename + '_scaled' + ext

    if not args.interpolation:
        args.interpolation = cv.INTER_AREA

    if is_dir:
        scale_all(args.input, args.output, args.factor,
                  interpolation=args.interpolation)
    else:
        scale(args.input, args.output, args.factor,
              interpolation=args.interpolation)
