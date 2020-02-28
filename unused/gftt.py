#!/usr/bin/env python3
# -*- coding: utf8 -*-

import cv2 as cv
import numpy as np
import os


def gftt(imagefile, output, featurecount=25, minquality=0.01, mindist=10):
    img = cv.imread(imagefile)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    corners = cv.goodFeaturesToTrack(gray, featurecount, minquality, mindist)
    corners = np.int0(corners)
    for i in corners:
        x, y = i.ravel()
        cv.circle(img, (x, y), 3, 255, -1)
    cv.imwrite(output, img)
    print('Applied Good Features to Track from', imagefile, 'to',  os.path.abspath(output),
          'and found', len(corners), 'features')


def gftt_all(imagedir, output, featurecount=25, minquality=0.01, mindist=10):
    for file in sorted(os.listdir(imagedir)):
        imagefile = os.path.join(imagedir, file)
        outputfile = os.path.join(output, file)
        gftt(imagefile, outputfile, featurecount, minquality, mindist)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('input', help='Image file or directory')
    parser.add_argument('-o', '--output', help='Output file or directory')
    parser.add_argument('-c', '--count', type=int,
                        default=25, help='Number of features to detect')
    parser.add_argument('-q', '--quality', type=float,
                        default=0.01, help='Minimal quality level')
    parser.add_argument('-d', '--distance', type=int,
                        default=10, help='Minimal distance between features')
    args = parser.parse_args()

    is_dir = os.path.isdir(args.input)

    if not args.output:
        if is_dir:
            args.output = os.path.join(args.input, os.path.pardir, 'gftt')
            os.makedirs(args.output, exist_ok=True)
        else:
            # split ext
            filename, ext = os.path.splitext(args.input)
            args.output = filename + '_gftt' + ext

    if is_dir:
        gftt_all(args.input, args.output,
                 featurecount=args.count, minquality=args.quality, mindist=args.distance)
    else:
        gftt(args.input, args.output,
             featurecount=args.count, minquality=args.quality, mindist=args.distance)
