#!/usr/bin/env python3
# -*- coding: utf8 -*-


# ./stitch/templatematch.py \
#      data/processed/oct19/sample/result/hough.csv \
#      data/processed/oct19/sample/result/translations.csv \
#      data/processed/oct19/sample/foreground/ \
#      -t50 -s50 -r50 -o /tmp/bladestitching/temp.txt


import os

import cv2 as cv
import numpy as np
import pandas as pd
from tqdm import tqdm

import lineutils as ut
from lineutils import r, t, x, y

METHODS = {
    cv.TM_SQDIFF: 'SQDIFF',
    cv.TM_SQDIFF_NORMED: 'SQDIFF_NORMED',
    cv.TM_CCORR: 'CCORR',
    cv.TM_CCORR_NORMED: 'CCORR_NORMED',
    cv.TM_CCOEFF: 'CCOEFF',
    cv.TM_CCOEFF_NORMED: 'CCOEFF_NORMED',
}


def tmatch(hough, stitch, inputdir, method, outputfile=None,
           gridpx=10, templatepx=10, radiuspx=10):
    print('+++', 'Using method', method, '(', METHODS[method], ')', '+++')
    dfhough = pd.read_csv(hough, index_col=0)
    lines_per_file = {file: list(zip(group_df['rho'], group_df['theta']))
                      for file, group_df in dfhough.groupby(by='file')}

    dfstitch = pd.read_csv(stitch, index_col=0)
    translations_per_file = dfstitch.to_dict(orient='index')

    line_files = set(lines_per_file.keys())
    translation_files = set(translations_per_file.keys())

    missing = list(sorted(line_files ^ translation_files))
    if missing:
        print('Missing data for:', *missing)

    files = list(sorted(line_files & translation_files))

    t = tqdm(files, unit='files')
    for file_name in t:
        t.set_description(file_name)

        translation = translations_per_file[file_name]
        ref_name = translation['ref']  # next image
        x = translation['x']  # inital guess of x translation
        y = translation['y']  # inital guess of y translation

        lines = lines_per_file[ref_name]

        img = cv.imread(os.path.join(inputdir, file_name), 0)
        ref = cv.imread(os.path.join(inputdir, ref_name), 0)

        img_w, img_h = img.shape[1], img.shape[0]
        ref_w, ref_h = ref.shape[1], ref.shape[0]

        # Bounds in ref from which to sample the grid
        # (overlapping area with img)
        cut_x, cut_y, cut_w, cut_h = (max(0, -x),
                                      max(0, -y),
                                      min(ref_w, img_w - x),
                                      min(ref_h, img_h - y))

        # build grid inside overlapping area (regarding patch size)
        grid = build_grid(cut_w - cut_x - templatepx, cut_h - cut_y - templatepx,
                          gridpx, border=radiuspx)

        # average rho value used to determine left/right sides of lines
        average_rho = (np.array([r(l) for l in lines])
                       .mean(0)
                       .astype(int))
        left_lines = list(filter(lambda line: r(line) < average_rho, lines))
        right_lines = list(filter(lambda line: r(line) >= average_rho, lines))

        # offset between grid corrdinates and center of patch in cut_ref
        half_template_size = int(templatepx / 2)
        x_off = half_template_size - cut_x
        y_off = half_template_size - cut_y

        # only keep a patch if its center is on rotor blade
        grid = [(px, py) for px, py in grid
                if all([ut.is_line_left(l, px + x_off, py + y_off) for l in left_lines])
                and all([ut.is_line_right(l, px + x_off, py + y_off) for l in right_lines])]

        # print('Matching', len(grid), 'templates:', grid)
        for point in grid:
            p_x_ref, p_y_ref = point
            p_x_img, p_y_img = p_x_ref - x, p_y_ref - y

            # only match inside this region around template
            match_region = img[p_y_img - radiuspx:p_y_img + templatepx + radiuspx,
                               p_x_img - radiuspx:p_x_img + templatepx + radiuspx]
            # template to match, taken from grid
            template = ref[p_y_ref:p_y_ref + templatepx,
                           p_x_ref:p_x_ref + templatepx]
            # perform actual template matching
            res = cv.matchTemplate(match_region, template, method)
            # find best match
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
            # compute actual point where patch belongs
            if method in [cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED]:
                min_loc_x, min_loc_y = min_loc
                res_point = (min_loc_x - radiuspx,
                             min_loc_y - radiuspx)
            else:
                max_loc_x, max_loc_y = max_loc
                res_point = (max_loc_x - radiuspx,
                             max_loc_y - radiuspx)
            print(point, '::', res_point)

        # TODO: aggregate points of image
    # TODO: write out csv file


def build_grid(w, h, dist, border=0):
    xs = list(range(border, w - border, dist))
    ys = list(range(border, h - border, dist))
    return [(x, y) for x in xs for y in ys]


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('hough',
                        help='Input file')
    parser.add_argument('stitch',
                        help='Input file')
    parser.add_argument('input',
                        help='Image directory')
    parser.add_argument('-o', '--output',
                        help='Output file')
    parser.add_argument('-m', '--method', type=int, choices=list(sorted(METHODS.keys())),
                        help='Matching method to use')
    parser.add_argument('-s', '--grid-spacing', type=int, default=10,
                        help='Define the space between two sampled templates')
    parser.add_argument('-t', '--template-size', type=int, default=10,
                        help='Define the template size')
    parser.add_argument('-r', '--radius', type=int, default=10,
                        help='Define how far to shift each template starting at the initial value')

    args = parser.parse_args()

    if not os.path.isfile(args.hough):
        print('Please provide a CSV file containing Hough files')
        exit(1)

    if not os.path.isfile(args.stitch):
        print('Please provide a CSV file containing the hough stitching estimates')
        exit(2)

    if not os.path.isdir(args.input):
        print('Please prove a directory containing the image files')
        exit(3)

    if args.method is not None:
        methods = [args.method]
    else:
        methods = METHODS

    for m in methods:
        tmatch(args.hough, args.stitch, args.input, m,
               outputfile=args.output,
               gridpx=args.grid_spacing,
               templatepx=args.template_size,
               radiuspx=args.radius)
