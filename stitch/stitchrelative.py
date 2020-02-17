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

    translations = {}

    for current_image, next_image in zip(line_files, line_files[1:]):

        current_image.init_twins(next_image)

        c_lines = current_image.lines
        n_lines = [current_image.twins[line]
                   if line in current_image.twins
                   else None
                   for line in c_lines]

        line_pairs = list(
            filter(
                lambda p: p[1] is not None,
                zip(c_lines,
                    n_lines)
            )
        )

        count = len(line_pairs)
        twins = [(line_pairs[l], line_pairs[r])
                 for l in range(0, count)
                 for r in range(l + 1, count)]

        image_translations = []

        # Naming conventions:
        # Prefix c_ stands for C_urrent set of lines
        # Prefix n_ stands for N_ext set of lines
        # Postfix _l stands for _Left line
        # Postfix _b stands for _Bisection line
        # Postfix _r stands for _Right line
        # x means x coord, y means y coord of foot point
        # rho, theta are simply x, y in polar coords
        for (c_l, n_l), (c_r, n_r) in twins:

            # Compute bisecting lines
            c_b = ut.get_bisecting_line(c_l, c_r)
            n_b = ut.get_bisecting_line(n_l, n_r)

            # We need the original lines later on
            c_b_backup, n_b_backup = c_b, n_b

            # Move this distance to align bisec foot points
            x_diff_b, y_diff_b = x(n_b) - x(c_b), y(n_b) - y(c_b)

            # Use these four variables to track the overall translation for each side
            translate_x_l = x_diff_b
            translate_x_r = x_diff_b
            translate_y_l = y_diff_b
            translate_y_r = y_diff_b

            # Move current lines
            c_l = ut.translate(c_l, x_diff_b, y_diff_b)
            c_b = ut.translate(c_b, x_diff_b, y_diff_b)
            c_r = ut.translate(c_r, x_diff_b, y_diff_b)

            # Foot points should now be "equal" (deviate less than 1 pixel) for the bisecting lines
            bft_x, bft_y = x(n_b), y(n_b)  # = x(c_b), y(c_b)

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
            translate_l = ut.vertical_distance(n_l, c_l)
            translate_r = ut.vertical_distance(n_r, c_r)

            # As we rotated the lines earlier,
            # vertical actually refers to parallel along the bisections,
            # so we need to take them into account
            # (We use the bisection of the bisections as a simplifying assumption)
            vertical_direction = t(ut.get_bisecting_line(c_b_backup,
                                                         n_b_backup)) + np.pi / 2

            print('++ Moving', translate_l, 'left and', translate_r, 'right')
            print('Bisections were', ut.eq(
                c_b_backup), 'and', ut.eq(n_b_backup))
            print('Vertical actually meant', vertical_direction,
                  'by', translate_l, '/', translate_r)
            print(translate_l * np.cos(vertical_direction),
                  translate_r * np.cos(vertical_direction), '|',
                  translate_l * np.sin(vertical_direction),
                  translate_r * np.sin(vertical_direction))

            # Distribute vertical translations among both axes according to bisection of bisections
            # (Note how we swapped sin and cos to account for the pi/2 angle of difference)
            translate_x_l += translate_l * np.cos(vertical_direction)
            translate_x_r += translate_r * np.cos(vertical_direction)
            translate_y_l += translate_l * np.sin(vertical_direction)
            translate_y_r += translate_r * np.sin(vertical_direction)

            # Take the average over both translation for left and right
            translate_x = (translate_x_l + translate_x_r) / 2
            translate_y = (translate_y_l + translate_y_r) / 2

            image_translations.append([translate_x, translate_y])

        if len(image_translations) > 0:
            translation = np.array(image_translations).mean(0).astype(int)
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
        print('Results not written to disk as output file was not specified.')


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
