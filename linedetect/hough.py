#!/usr/bin/env python3
# -*- coding: utf8 -*-

import cv2 as cv
import numpy as np
import os


def hough(imagefile, output):
    img = cv.imread(imagefile)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    edges = cv.Canny(gray, 50, 150, apertureSize=3)
    lines = cv.HoughLines(edges, 2, np.pi/180, 150)
    if lines is not None:
        for line in lines:
            for rho, theta in line:
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a*rho
                y0 = b*rho
                x1 = int(x0 + 1000*(-b))
                y1 = int(y0 + 1000*(a))
                x2 = int(x0 - 1000*(-b))
                y2 = int(y0 - 1000*(a))

                cv.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
    cv.imwrite(output, img)
    print('Applied Hough transform to', imagefile)


def hough_all(imagedir, output):
    for file in os.listdir(imagedir):
        imagefile = os.path.join(imagedir, file)
        outputfile = os.path.join(output, file)
        hough(imagefile, outputfile)


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
            args.output = os.path.join(args.input, os.path.pardir, 'hough')
            os.makedirs(args.output, exist_ok=True)
        else:
            # split ext
            filename, ext = os.path.splitext(args.input)
            args.output = filename + '_hough' + ext

    if is_dir:
        hough_all(args.input, args.output)
    else:
        hough(args.input, args.output)
