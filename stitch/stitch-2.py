#!/usr/bin/env python3
# -*- coding: utf8 -*-

import os

import cv2 as cv
import numpy as np
import pandas as pd
from tqdm import tqdm

import linedetect.hough as ld
import linedetect.lineutils as ut
from linedetect.lineutils import r, t, x, y


def stitch(imagedir, output=None, center=True):
    files = sorted(os.listdir(imagedir))
    file_paths = [os.path.join(imagedir, file) for file in files]
    print('Applying Hough transformations to input images ...')
    lines_per_image = [ld.hough(file_path,
                                nubPredicate=None
                                if center
                                else ld.naiveNubPredicate,
                                center=center,
                                filterPredicate=lambda l: ld.naiveFilter(
                                    l, 0.5),
                                paint=True,
                                output=os.path.join(os.path.dirname(file_path),
                                                    os.pardir,
                                                    'hough',
                                                    os.path.basename(file_path)))
                       for file_path in tqdm(file_paths)]
    line_files = [LineImage(p, l) for p, l in zip(file_paths, lines_per_image)]
    pairs = list(zip(line_files, line_files[1:]))

    translations = {}

    for current_image, next_image in pairs:
        img = cv.imread(current_image.img_path)

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

            # TODO:
            # 1) align bisec lines c and n ---> x translation
            # 2) Rotate l and r accordingly
            # 3) Rotate entire coords to avoid /0 (cf. prev. TODO)
            # 4) calc vertical offset for l and r to match (perhaps counting in rotation?) ---> y translation
            # 5) Rotate everything back to get actual x,y translation

            # Move this distance to align bisec foot points
            x_diff_b, y_diff_b = x(n_b) - x(c_b), y(n_b) - y(c_b)

            # Use these two variables to track the overall translation for each side
            translate_y_l = y_diff_b
            translate_y_r = y_diff_b

            # Move current lines
            c_l = ut.translate(c_l, x_diff_b, y_diff_b)
            c_b = ut.translate(c_b, x_diff_b, y_diff_b)
            c_r = ut.translate(c_r, x_diff_b, y_diff_b)

            # Foot point should now be equal for both bisecting lines
            bft_x, bft_y = x(n_b), y(n_b)

            print('Rotating by', c_b, 'and', n_b,
                  'and moving current foot point by', x_diff_b, 'and', y_diff_b)

            # Rotate current lines and next lines
            # such that the bisection lines are both vertical
            c_l = ut.rotate(c_b, t(c_b), bft_x, bft_y)
            c_b = ut.rotate(c_b, t(c_b), bft_x, bft_y)
            c_r = ut.rotate(c_b, t(c_b), bft_x, bft_y)
            n_l = ut.rotate(n_b, t(n_b), bft_x, bft_y)
            n_b = ut.rotate(n_b, t(n_b), bft_x, bft_y)
            n_r = ut.rotate(n_b, t(n_b), bft_x, bft_y)

            # Compute how far both current lines
            # need to be translated in vertical direction
            # to match both next lines
            translate_y_l += ut.vertical_distance(n_l, c_l)
            translate_y_r += ut.vertical_distance(n_r, c_r)

            # We only translated horizontally in the beginning
            translate_x = x_diff_b
            # Take the average over both translation for left and right
            translate_y = 0.5 * (translate_y_l + translate_y_r)

            image_translations.append([translate_x, translate_y])
            # cv.line(img,
            #         (200, 400),
            #         (200 + translate_x, 400 + translate_y),
            #         (0, 0, 0),
            #         thickness=3)

            # cv.line(img,
            #         (-1, 480 + translate_y),
            #         (10000, 480 + translate_y),
            #         (0, 0, 0),
            #         thickness=1)

        if len(image_translations) > 0:
            translation = np.array(image_translations).mean(0).astype(int)
            key = os.path.basename(current_image.img_path)
            ref = os.path.basename(next_image.img_path)
            translations[key] = (ref, translation)
            print(current_image.img_path, '-->',
                  next_image.img_path, ':: moved by', translation)
        p_dir = os.path.join(imagedir, os.path.pardir,
                             'stitch-c' if center else 'stitch-n')
        os.makedirs(p_dir, exist_ok=True)
        p = os.path.join(p_dir, os.path.basename(current_image.img_path))
        cv.imwrite(p, img)

    if output is not None:
        paths = list(sorted(translations.keys()))
        refs = [translations[p][0] for p in paths]
        xs = [translations[p][1][0] for p in paths]
        ys = [translations[p][1][1] for p in paths]
        df = pd.DataFrame({'ref': refs, 'x': xs, 'y': ys}, index=paths)
        print('#####')
        print(df)
        print('#####')
        df.to_csv(output)


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
                    key=lambda l: l[0] - line[0]
                )
            )
            if(len(neighbors) > 0):
                if(len(neighbors) > 1):
                    print('WARNING: Ignoring other similar line(s)!',
                          [ut.eq(*l) for l in neighbors[1:]])
                self.twins[line] = neighbors[0]
            else:
                print('WARNING: Line cannot be found in next image!',
                      ut.eq(*line))

    def __str__(self):
        return str(self.img_path) + ' has lines ' + str(
            self.lines) + ' which correspond to ' + str(self.twins)

# def draw_line(img, rho, theta, color=(0, 0, 255), width=2):
#     a = np.cos(theta)
#     b = np.sin(theta)
#     x0 = a * rho
#     y0 = b * rho
#     x1 = int(x0 + b * -1000)
#     y1 = int(y0 + a * 1000)
#     x2 = int(x0 - b * -1000)
#     y2 = int(y0 - a * 1000)

#     cv.line(img, (x1, y1), (x2, y2), color, width)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('input', help='Image directory')
    parser.add_argument('strategy', choices=['nub', 'center'],
                        help='Decide whether adjacent lines should be discarded or joined')
    parser.add_argument('-o', '--output', help='Output file')

    args = parser.parse_args()

    stitch(args.input, output=args.output, center=args.strategy == 'center')
