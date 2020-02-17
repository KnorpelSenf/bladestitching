#!/usr/bin/env python3
# -*- coding: utf8 -*-

import os

import cv2 as cv
import numpy as np
import pandas as pd
from tqdm import tqdm

import hough as ld
import lineutils as ut
from lineutils import r, t, x, y


def stitch(imagedir, cachefile, output=None):

    print('Reading Hough lines')
    df = pd.read_csv(cachefile)
    lines_per_file = {file: list(zip(group_df['rho'], group_df['theta']))
                      for file, group_df in df.groupby(by='file')}
    line_files = [LineImage(os.path.join(imagedir, p), l)
                  for p, l
                  in sorted(lines_per_file.items(), key=lambda x:x[0])]

    # dict holding final translation values
    translations = {}

    # pairs of images n and n+1
    for current_image, next_image in zip(line_files, line_files[1:]):

        # find out which line in the current image
        # corresponds to which line in the next image

        # we call these pairs twins
        current_image.init_twins(next_image)

        # current lines
        c_lines = current_image.lines
        # next lines
        n_lines = [current_image.twins[line]
                   if line in current_image.twins
                   else None
                   for line in c_lines]

        # filter out entries where no twin was found
        line_pairs = list(
            filter(
                lambda p: p[1] is not None,
                zip(c_lines,
                    n_lines)
            )
        )

        # we need two twins (that is, four lines) for each translation computation,
        # so we generate all possible combinations of twins (pairs of twins)
        count = len(line_pairs)
        twin_combinations = [(line_pairs[l], line_pairs[r])
                             for l in range(0, count)
                             for r in range(l + 1, count)]

        # translation values for each pair of twins
        image_translations = {}

        # Naming conventions:
        # Prefix c_ stands for C_urrent set of lines
        # Prefix n_ stands for N_ext set of lines
        # Postfix _l stands for _Left line
        # Postfix _b stands for _Bisection line
        # Postfix _r stands for _Right line
        # x means x coord, y means y coord of foot point
        # rho, theta are simply x, y in polar coords
        for (c_l, n_l), (c_r, n_r) in twin_combinations:

            # Compute bisecting lines
            c_b = ut.get_bisecting_line(c_l, c_r)
            n_b = ut.get_bisecting_line(n_l, n_r)

            # Move this distance to align bisec foot points
            x_diff_b, y_diff_b = x(n_b) - x(c_b), y(n_b) - y(c_b)

            # Use these two variables to track the overall vertical translation for each side
            translate_y_l = y_diff_b
            translate_y_r = y_diff_b

            # Move current lines
            c_l = ut.translate(c_l, x_diff_b, y_diff_b)
            c_b = ut.translate(c_b, x_diff_b, y_diff_b)
            c_r = ut.translate(c_r, x_diff_b, y_diff_b)

            # Foot points should now be "equal" (deviate less than 1 pixel) for the bisecting lines
            bft_x, bft_y = x(n_b), y(n_b)  # = x(c_b), y(c_b)

            # Note how we never account for the following rotation
            # in the final translation values, see stitchrelative.py
            # for a script that does this (and produces worse results!)

            # Rotate current lines and next lines
            # such that the bisection lines are both vertical
            c_rotate, n_rotate = -t(c_b), -t(n_b)
            c_l = ut.rotate(c_l, c_rotate, bft_x, bft_y)
            c_b = ut.rotate(c_b, c_rotate, bft_x, bft_y)
            c_r = ut.rotate(c_r, c_rotate, bft_x, bft_y)
            n_l = ut.rotate(n_l, n_rotate, bft_x, bft_y)
            n_b = ut.rotate(n_b, n_rotate, bft_x, bft_y)
            n_r = ut.rotate(n_r, n_rotate, bft_x, bft_y)

            # Compute how far both current lines
            # need to be translated in vertical direction
            # to match both next lines
            translate_y_l += ut.vertical_distance(n_l, c_l)
            translate_y_r += ut.vertical_distance(n_r, c_r)

            # The only time we translated horizontally was in the beginning, so we just copy that value
            translate_x = x_diff_b
            # Take the average over both translation for left and right
            translate_y = 0.5 * (translate_y_l + translate_y_r)

            image_translations[((c_l, n_l), (c_r, n_r))] = [
                translate_x, translate_y]

        # Optimize result based on error function
        optimize_line_distances(image_translations)

        if len(image_translations) > 0:
            translation = np.array(
                list(image_translations.values())).mean(0).astype(int)
            key = os.path.basename(current_image.img_path)
            ref = os.path.basename(next_image.img_path)
            translations[key] = (ref, translation)

    paths = list(sorted(translations.keys()))
    refs = [translations[p][0] for p in paths]
    xs = [translations[p][1][0] for p in paths]
    ys = [translations[p][1][1] for p in paths]
    df = pd.DataFrame({'ref': refs, 'x': xs, 'y': ys}, index=paths)
    if output is not None:
        print('Done.', output)
        df.to_csv(output)
    else:
        print('Done. Result:')
        print(df)
        print('Result not written to disk as output file was not specified.')


def optimize_line_distances(image_translations):
    # image 1, image 2
    # lines from 1, lines from 2
    # translation from 1 -> 2
    # translate all lines from 1 by translation to align them to lines from 2
    # compute distance via error function over all
    # create surrounding area around target translation value
    # brute force compute error function over all points in that space
    # find minimum
    # adjust translation value to this

    # AND DON'T FORGET TO DUMP EVERYTING TO STDOUT!!!
    pass


class LineImage:
    """
    LineImages contain an image path and a list of Hough lines with it.
    Hough lines will automatically be normalized upon instantiation
    as specified by linedetect.lineutils.normalize(line).
    """

    def __init__(self, img_path, lines=[]):
        self.img_path = img_path
        self.lines = [ut.normalize(l) for l in lines]
        self.twins = {}

    def init_twins(self, image):
        """
        Takes an image and matches self.lines with image.lines to generate
        pairs of closest lines. Result will be stored in self.twins property.
        """
        # TODO: find metric that works more generically, create clusters with two elements each
        # print('Finding neighbors for', len(
        #     self.lines), 'lines in', self.img_path)
        for line in self.lines:
            # print('Finding neighbor for', line, 'in', image.lines)

            # Take lines that are similar and sort them by rho distance
            neighbors = list(
                sorted(
                    filter(
                        lambda l: ld.ut.are_lines_similar(l, line),
                        image.lines
                    ),
                    # similarity heuristic: compare distances of foot points from origin
                    key=lambda l: abs(r(line) - r(l))
                )
            )
            if(len(neighbors) > 0):
                twin = neighbors[0]
                if(len(neighbors) > 1):
                    print('WARNING: Ignoring other similar line(s) of',
                          ut.eq(line), 'besides', ut.eq(twin) + '!', '(', self.img_path, ')')
                    print([ut.eq(l) for l in neighbors[1:]])
                self.twins[line] = twin
            else:
                print('WARNING: Line cannot be found in next image!',
                      ut.eq(line), '(', self.img_path, ')')

    def __str__(self):
        return (str(self.img_path)
                + ' has lines ' + str(self.lines)
                + ' which correspond to ' + str(self.twins))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('hough',
                        help='File containing precomputed hough lines')
    parser.add_argument('input',
                        help='Image directory')
    parser.add_argument('-o', '--output',
                        help='Output file')

    args = parser.parse_args()

    stitch(args.input, args.hough,
           output=args.output)
