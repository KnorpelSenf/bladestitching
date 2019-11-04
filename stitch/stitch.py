#!/usr/bin/env python3
# -*- coding: utf8 -*-

import os

import cv2 as cv
import numpy as np

import linedetect.hough as ld


def areLinesSimilar(r, s, max_rho=50, max_theta=0.1):
    rho_r, theta_r = r
    rho_s, theta_s = s
    diff_t = abs(theta_r - theta_s)
    similar = abs(rho_r - rho_s) < max_rho and diff_t < max_theta
    similar_inverted = abs(
        rho_r + rho_s) < max_rho and abs(diff_t - np.pi) < max_theta
    # if similar:
    #     print(abs(rho_r - rho_s), '<', max_rho, 'and', diff_t, '<', max_theta)
    # if similar_inverted:
    #     print(abs(rho_r + rho_s), '<', max_rho, 'and',
    #           abs(diff_t - np.pi), '<', max_theta)
    return similar or similar_inverted


def get_closest_lines(current, nex):
    res = []
    for line in current:
        # print('Finding neighbor for', line, 'in', nex)
        neighbors = list(filter(lambda l: areLinesSimilar(l, line), nex))
        # print(line, 'has', len(neighbors), 'neighbors, they are:', neighbors)
        if(len(neighbors) > 0):
            if(len(neighbors) > 1):
                print('WARNING: Ignoring second similar line!')
            res.append((line, neighbors[0]))
    return res


def stitch(imagedir):
    files = sorted(os.listdir(imagedir))
    file_paths = (os.path.join(imagedir, file) for file in files)
    lines_per_image = [ld.hough(file_path,
                                None,
                                ld.naiveNub,
                                lambda l: ld.naiveFilter(l, 0.5))
                       for file_path in file_paths]
    file_pairs = zip(lines_per_image, lines_per_image[1:])

    for (current, nex) in file_pairs:
        pairs = get_closest_lines(current, nex)
        for p in pairs:
            print(p, 'will be aligned')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('input', help='Image directory')

    args = parser.parse_args()

    stitch(args.input)
