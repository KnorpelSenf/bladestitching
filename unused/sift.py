#!/usr/bin/env python3
# -*- coding: utf8 -*-

import cv2 as cv
import numpy as np
import os


def sift(imagefile, output,
         featurecount=25, contrastThreshold=0.04, edgeThreshold=10, rich=False):
    img = cv.imread(imagefile)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    sift = cv.xfeatures2d.SIFT_create(
        nfeatures=featurecount, contrastThreshold=contrastThreshold, edgeThreshold=edgeThreshold)
    kp = sift.detect(gray, None)
    img = (cv.drawKeypoints(img, kp, img)
           if not rich
           else cv.drawKeypoints(img, kp, img, flags=cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS))

    cv.imwrite(output, img)
    print('Applied SIFT from', imagefile, 'to',  os.path.abspath(output))


def sift_all(imagedir, output,
             featurecount=25, contrastThreshold=0.04, edgeThreshold=10, rich=False):
    for file in sorted(os.listdir(imagedir)):
        imagefile = os.path.join(imagedir, file)
        outputfile = os.path.join(output, file)
        sift(imagefile, outputfile,
             featurecount=featurecount, contrastThreshold=contrastThreshold, edgeThreshold=edgeThreshold, rich=rich)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('input', help='Image file or directory')
    parser.add_argument('-o', '--output', help='Output file or directory')
    parser.add_argument('-c', '--count', type=int,
                        default=0, help='Number of features to detect')
    parser.add_argument('--contrast-threshold', type=float,
                        default=0.04, help='Contrast threshold')
    parser.add_argument('--edge-threshold', type=float,
                        default=10, help='Edge threshold')
    parser.add_argument('-r', '--rich', action='store_true',
                        help='Draw rich features')
    args = parser.parse_args()

    is_dir = os.path.isdir(args.input)

    if not args.output:
        if is_dir:
            args.output = os.path.join(args.input, os.path.pardir, 'sift')
            os.makedirs(args.output, exist_ok=True)
        else:
            # split ext
            filename, ext = os.path.splitext(args.input)
            args.output = filename + '_sift' + ext

    if is_dir:
        sift_all(args.input, args.output,
                 featurecount=args.count, contrastThreshold=args.contrast_threshold, edgeThreshold=args.edge_threshold, rich=args.rich)
    else:
        sift(args.input, args.output, rich=args.rich)
