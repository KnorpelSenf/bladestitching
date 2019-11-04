#!/usr/bin/env python3
# -*- coding: utf8 -*-

import cv2 as cv
import numpy as np
import os


def nubBy(predicate, iterable):
    res = []
    for e in iterable:
        if not any(predicate(e, r) for r in res):
            res.append(e)
    return res


def hough(imagefile, output=None, nubPredicate=None, filterPredicate=None, verbose=False, paint=True):
    img = cv.imread(imagefile)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    edges = cv.Canny(gray, 50, 150, apertureSize=3)
    lines = cv.HoughLines(edges, 1, np.pi/180/100, 150)

    res = []
    if lines is not None:
        if filterPredicate is not None:
            lines = filter(filterPredicate, lines)
        if nubPredicate is not None:
            lines = nubBy(nubPredicate, lines)
        for line in lines:
            for rho, theta in line:
                res.append((rho, theta))
                if verbose:
                    print('Line', str(len(res)) + ':',
                          rho, '= x * sin(', theta, ') + y * cos(', theta, ')')
                if output is not None and paint:
                    a = np.cos(theta)
                    b = np.sin(theta)
                    x0 = a*rho
                    y0 = b*rho
                    x1 = int(x0 + 1000*(-b))
                    y1 = int(y0 + 1000*(a))
                    x2 = int(x0 - 1000*(-b))
                    y2 = int(y0 - 1000*(a))

                    cv.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

    if output is not None:
        cv.imwrite(output, img)
    if len(res) < 2:
        print('WARNING: number of lines is merely',
              len(res), 'in image file', imagefile)

    print('Applied Hough transform from', imagefile,
          'to ' + output if output is not None else '')
    return res


def naiveNub(r, s, max_rho=20, max_theta=0.1):
    [[rho_r, theta_r]] = r
    [[rho_s, theta_s]] = s
    diff_t = abs(theta_r - theta_s)
    similar = abs(rho_r - rho_s) < max_rho and diff_t < max_theta
    similar_inverted = abs(
        rho_r + rho_s) < max_rho and abs(diff_t - np.pi) < max_theta
    return similar or similar_inverted


def naiveFilter(line, max_deviation):
    [[_, theta]] = line
    return theta < max_deviation or abs(np.pi - theta) < max_deviation


def hough_all(imagedir, output, nubPredicate=None, filterPredicate=None, verbose=False):
    for file in os.listdir(imagedir):
        imagefile = os.path.join(imagedir, file)
        outputfile = os.path.join(output, file)
        hough(imagefile, outputfile, nubPredicate, filterPredicate, verbose)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('input', help='Image file or directory')
    parser.add_argument('-o', '--output', help='Output file or directory')
    parser.add_argument('--nub', action='store_true',
                        help='Filter out similar lines')
    parser.add_argument('--max-v-deviation', type=float,
                        help='Filter lines by their maximum deviation from the vertical line (good default: 0.5)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print verbose line equations')

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
        hough_all(args.input, args.output,
                  naiveNub if args.nub else None,
                  (lambda l: naiveFilter(l, args.max_v_deviation)
                   ) if args.max_v_deviation is not None else None,
                  args.verbose)
    else:
        hough(args.input, args.output,
              naiveNub if args.nub else None,
              (lambda l: naiveFilter(l, args.max_v_deviation)
               ) if args.max_v_deviation is not None else None,
              args.verbose)
