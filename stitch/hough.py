#!/usr/bin/env python3
# -*- coding: utf8 -*-

import os

import cv2 as cv
import numpy as np
import pandas as pd

from tqdm import tqdm

import lineutils as ut
from lineutils import r, t


def nubBy(predicate, iterable):
    res = []
    for e in iterable:
        if not any([predicate(e, r) for r in res]):
            res.append(e)
    return res


def naiveNubPredicate(r, s, max_rho=20, max_theta=0.1):
    rho_r, theta_r = r
    rho_s, theta_s = s
    diff_t = abs(theta_r - theta_s)
    similar = (abs(rho_r - rho_s) < max_rho
               and diff_t < max_theta)
    similar_inverted = (abs(rho_r + rho_s) < max_rho
                        and abs(diff_t - np.pi) < max_theta)
    return similar or similar_inverted


def naiveFilter(line, max_deviation):
    theta = t(line)
    # print(theta < max_deviation or abs(np.pi - theta)
    #       < max_deviation, 'for', ut.eq(line))
    return theta < max_deviation or abs(np.pi - theta) < max_deviation


def findCenters(lines):

    groups = {}  # Check similarity with keys. Values are lists of similar lines

    for line in lines:
        similar_lines = list(filter(
            lambda other: ut.are_lines_similar(line, other),
            groups.keys()
        ))
        count = len(similar_lines)
        if count == 0:
            groups[line] = [line]
        else:
            groups[similar_lines[0]].append(line)
            if count > 1:
                print('Found multiple lines similar to', ut.eq(line), 'of which the first will be used:',
                      *[ut.eq(x) for x in similar_lines])

    return [np.array(group).mean(0) for group in groups.values()]


def hough(imagefile, outputfile=None,
          threshold=100,
          normalize=True,
          filterPredicate=None,
          nubPredicate=None,
          verbose=False):

    # Read image file
    img = cv.imread(imagefile)
    # Turn into grayscale
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # Detect edges using canny edge detection
    edges = cv.Canny(gray, 50, 150, apertureSize=3)
    # Hough transform
    lines = cv.HoughLines(edges, 1, np.pi/180/100, threshold)

    if lines is None:
        print('No lines found in', imagefile, ' :(')
    else:
        # Unpack lists of single elements
        lines = [l for [l] in lines]

        # Normalize
        if normalize:
            lines = [ut.normalize(l) for l in lines]

        # Filter
        if filterPredicate is not None:
            lines = filter(filterPredicate, lines)

        # Center or nub
        if nubPredicate is not None:
            lines = nubBy(nubPredicate, lines)
        else:
            lines = findCenters(lines)

        # Log
        if verbose:
            for line in lines:
                print(ut.eq(line))

        # Paint
        if outputfile is not None:
            for line in lines:
                rho, theta = line
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a * rho
                y0 = b * rho
                x1 = int(x0 + 1000 * (-b))
                y1 = int(y0 + 1000 * (a))
                x2 = int(x0 - 1000 * (-b))
                y2 = int(y0 - 1000 * (a))

                cv.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

            # Write copy of image to separate file for visualization
            cv.imwrite(outputfile, img)

        line_count = len(lines)
        if line_count < 2:
            print('WARNING: number of lines is merely',
                  line_count, 'in image file', imagefile)

    if verbose:
        print('Applied Hough transform on', imagefile,
              'to ' + outputfile if outputfile is not None else '')
    return lines


def hough_all(imagedir, outputfile,
              paint_output=None,
              threshold=100,
              filterPredicate=None,
              nubPredicate=None,
              verbose=False):

    res = []

    for file in tqdm(sorted(os.listdir(imagedir))):
        imagefile = os.path.join(imagedir, file)
        paint_outputfile = None
        if paint_output is not None:
            paint_outputfile = os.path.join(paint_output, file)

        lines = hough(imagefile, outputfile=paint_outputfile,
                      threshold=threshold,
                      filterPredicate=filterPredicate,
                      nubPredicate=nubPredicate,
                      verbose=verbose)

        if lines is not None:
            for line in lines:
                res.append([file, r(line), t(line)])

    df = pd.DataFrame(res, columns=['file', 'rho', 'theta'])
    df.to_csv(outputfile, index=False)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('input',
                        help='Image file or directory')
    parser.add_argument('-p', '--paint',
                        help='Output file or directory to draw lines')
    parser.add_argument('-o', '--output',
                        help='Aggregate translations to output csv if input is directory')
    parser.add_argument('-s', '--strategy', default='center', choices=['center', 'nub'],
                        help='Use center of lines close to each other or filter out similar lines')
    parser.add_argument('-t', '--threshold', type=int, default=100,
                        help='Threshold to use for Hough transformation')
    parser.add_argument('-d', '--max-v-deviation', type=float,
                        help='Filter lines by their maximum deviation from the vertical line (good default: 0.5)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print verbose line equations')

    args = parser.parse_args()

    if os.path.isdir(args.input):
        if not args.output:
            args.output = os.path.join(args.input, 'hough.csv')
        hough_all(args.input, args.output,
                  paint_output=args.paint,
                  threshold=args.threshold,
                  filterPredicate=(
                      lambda l: naiveFilter(l, args.max_v_deviation)
                  ) if args.max_v_deviation is not None else None,
                  nubPredicate=naiveNubPredicate
                  if args.strategy == 'nub' else None,
                  verbose=args.verbose)
    else:
        lines = hough(args.input, outputfile=args.paint,
                      threshold=args.threshold,
                      filterPredicate=(
                          lambda l: naiveFilter(l, args.max_v_deviation)
                      ) if args.max_v_deviation is not None else None,
                      nubPredicate=naiveNubPredicate
                      if args.strategy == 'nub' else None,
                      verbose=args.verbose)
        print('RESULT')
        for line in lines:
            print(ut.eq(line))