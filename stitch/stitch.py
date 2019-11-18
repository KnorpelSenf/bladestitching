#!/usr/bin/env python3
# -*- coding: utf8 -*-

import os

import cv2 as cv
import numpy as np
import pandas as pd
from tqdm import tqdm

import linedetect.hough as ld
import linedetect.lineutils as ut


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
                                paint=False)
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

        # for c in c_lines:
        #     draw_line(img, *c, (0, 0, 255), width=1)
        # for n in n_lines:
        #     if n is not None:
        #         draw_line(img, *n, (255, 0, 0), width=1)

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
        # print('Aligning according to', len(twins), 'pairs of matched lines')

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

            c_rho_l, c_theta_l = c_l
            c_rho_b, c_theta_b = ut.get_bisecting_line(c_l, c_r)
            c_rho_r, c_theta_r = c_r

            n_rho_l, n_theta_l = n_l
            n_rho_b, n_theta_b = ut.get_bisecting_line(n_l, n_r)
            n_rho_r, n_theta_r = n_r

            c_x_l, c_y_l = (c_rho_l * np.cos(c_theta_l),
                            c_rho_l * np.sin(c_theta_l))
            c_x_b, c_y_b = (c_rho_b * np.cos(c_theta_b),
                            c_rho_b * np.sin(c_theta_b))
            c_x_r, c_y_r = (c_rho_r * np.cos(c_theta_r),
                            c_rho_r * np.sin(c_theta_r))

            n_x_l, n_y_l = (n_rho_l * np.cos(n_theta_l),
                            n_rho_l * np.sin(n_theta_l))
            n_x_b, n_y_b = (n_rho_b * np.cos(n_theta_b),
                            n_rho_b * np.sin(n_theta_b))
            n_x_r, n_y_r = (n_rho_r * np.cos(n_theta_r),
                            n_rho_r * np.sin(n_theta_r))

            # print(c_theta_l, c_theta_b, c_theta_r)

            translate_x_l = None
            translate_y_l = None

            translate_x_r = None
            translate_y_r = None

            # TODO: rotate everything according to c_b and n_b
            # in order to avoid /0 error here

            # TODO: take average over multiple images?

            if not abs(c_theta_l) < 1e-5:
                x_diff_l = (n_x_l - c_x_l
                            + n_x_b - c_x_b)
                y_diff_l = (n_y_l - c_y_l
                            + n_y_b - c_y_b)

                theta_diff_l = (0.5 * np.pi
                                - c_theta_l
                                - np.arctan(y_diff_l
                                            / x_diff_l))

                bottom_len_l = np.sqrt(x_diff_l * x_diff_l
                                       + y_diff_l * y_diff_l)
                up_len_l = (bottom_len_l
                            * np.sin(theta_diff_l)
                            / np.sin(c_theta_l))

                translate_x_l = x_diff_l
                translate_y_l = y_diff_l + up_len_l
                # print('====L>>>', translate_x_l, translate_y_l)
                # cv.line(img,
                #         (100, 400),
                #         (int(100+translate_x_l), int(400 + translate_y_l)),
                #         (0, 0, 0),
                #         thickness=1)

            if not abs(c_theta_r) < 1e-5:
                x_diff_r = (n_x_r - c_x_r
                            + n_x_b - c_x_b)
                y_diff_r = (n_y_r - c_y_r
                            + n_y_b - c_y_b)

                theta_diff_r = (0.5 * np.pi
                                - c_theta_r
                                - np.arctan(y_diff_r
                                            / x_diff_r))

                bottom_len_r = np.sqrt(x_diff_r * x_diff_r
                                       + y_diff_r * y_diff_r)
                up_len_r = (bottom_len_r
                            * np.sin(theta_diff_r)
                            / np.sin(c_theta_r))

                translate_x_r = x_diff_r
                translate_y_r = y_diff_r + up_len_r
                # print('====R>>>', translate_x_r, translate_y_r)
                # cv.line(img,
                #         (300, 400),
                #         (int(300+translate_x_r), int(400 + translate_y_r)),
                #         (0, 0, 0),
                #         thickness=1)
            else:
                translate_x_r = translate_x_l
                translate_y_r = translate_y_l

            if translate_x_l is None:
                translate_x_l = translate_x_r
                translate_y_l = translate_y_r

            if translate_x_l is not None:
                translate_x = 0.5 * (translate_x_l + translate_x_r)
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
            translations[key] = translation
            print(current_image.img_path, '-->',
                  next_image.img_path, ':: moved by', translation)
        p = os.path.join(imagedir, os.path.pardir, 'stitch-c' if center else 'stitch-n',
                         os.path.basename(current_image.img_path))
        cv.imwrite(p, img)

    if output is not None:
        paths = list(sorted(translations.keys()))
        xs = [translations[p][0] for p in paths]
        ys = [translations[p][1] for p in paths]
        df = pd.DataFrame({'x': xs, 'y': ys}, index=paths)
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
