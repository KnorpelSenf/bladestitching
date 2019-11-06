#!/usr/bin/env python3
# -*- coding: utf8 -*-

import os

import cv2 as cv
import numpy as np

import linedetect.hough as ld


def are_lines_similar(r, s, max_rho=30, max_theta=0.1):
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


def stitch(imagedir):
    files = sorted(os.listdir(imagedir))
    file_paths = [os.path.join(imagedir, file) for file in files]
    lines_per_image = [ld.hough(file_path,
                                None,
                                ld.naiveNub,
                                lambda l: ld.naiveFilter(l, 0.5))
                       for file_path in file_paths]
    line_files = [LineImage(p, l) for p, l in zip(file_paths, lines_per_image)]
    pairs = list(zip(line_files, line_files[1:]))

    for current_image, next_image in pairs:
        img = cv.imread(current_image.img_path)
        current_image.init_twins(next_image)
        lines = current_image.lines

        for line in lines:
            draw_line(img, *line, (0, 0, 255), width=1)

        c = len(lines)
        unique_combinations = [(lines[l], lines[r])
                               for l in range(0, c)
                               for r in range(l + 1, c)]

        for l, r in unique_combinations:
            b = get_bisecting_line(l, r)
            draw_line(img, *b, (0, 0, 255), width=2)

        p = os.path.join(imagedir, os.path.pardir, 'bisect',
                         os.path.basename(current_image.img_path))
        cv.imwrite(p, img)


class LineImage:
    """
    LineImages contain an image path and a list of Hough lines with it.
    Hough lines will automatically be normalized upon instantiation
    as specified by normalize(line).
    """

    def __init__(self, img_path, lines=[]):
        self.img_path = img_path
        self.lines = [normalize(l) for l in lines]
        self.twins = []

    def init_twins(self, image):
        """
        Takes an image and matches self.lines with image.lines to generate
        pairs of closest lines. Result will be stored in self.twins property.
        """
        # TODO: find metric that works more generically, create clusters with two elements each
        print('Finding neighbors for', len(
            self.lines), 'lines in', self.img_path)
        for line in self.lines:
            # print('Finding neighbor for', line, 'in', image.lines)

            # Take lines that are similar and sort them by rho distance
            neighbors = list(
                sorted(
                    filter(
                        lambda l: are_lines_similar(l, line),
                        image.lines
                    ),
                    key=lambda l: l[0] - line[0]
                )
            )
            # print(line, 'has', len(neighbors),
            #       'neighbors, they are:', neighbors)
            if(len(neighbors) > 0):
                if(len(neighbors) > 1):
                    print('WARNING: Ignoring other similar line(s)!',
                          [eq(*l) for l in neighbors[1:]])
                self.twins.append(neighbors[0])
            else:
                print('WARNING: Line cannot be found in next image!',
                      eq(*line))
                self.twins.append(None)

    def __str__(self):
        return str(self.img_path) + ' has lines ' + str(
            self.lines) + ' which correspond to ' + str(self.twins)


def get_bisecting_line(l, r):
    """
    Takes two lines and returns their bisecting line.
    This implementation works well for parallel lines
    as it does not rely on the intersection point of the input lines.
    As a result, it also works well for almost parallel lines. It introduces
    (almost) no errors due to imprecision of floating point operations.
    """
    rho_l, theta_l = l
    rho_r, theta_r = r

    # direction of bisecting line
    theta = 0.5 * (theta_l + theta_r)

    # coordinates of base point of l (and r, respectively)
    # (from origin move by rho_l in the direction of theta_l)
    x_l, y_l = (rho_l * np.cos(theta_l), rho_l * np.sin(theta_l))
    x_r, y_r = (rho_r * np.cos(theta_r), rho_r * np.sin(theta_r))

    # move in this direction from base point of l (and r respectively)
    # to get to the point where the supporting vector of the bisecting
    # line intersects l (and r respectively)
    alpha_l = 0.5 * np.pi + theta_l
    alpha_r = 0.5 * np.pi + theta_r

    # move by this number of pixels from base point of l (and r respectively)
    # to get to the point where the supporting vector of the bisecting
    # line intersects l (and r respectively)
    intersect_l = np.tan(theta - theta_l) * rho_l
    intersect_r = np.tan(theta - theta_r) * rho_r

    # coordinates of the point where the supporting vector of the bisecting
    # line intersects l
    xn_l = x_l + intersect_l * np.cos(alpha_l)
    yn_l = y_l + intersect_l * np.sin(alpha_l)

    # coordinates of the point where the supporting vector of the bisecting
    # line intersects r
    xn_r = x_r + intersect_r * np.cos(alpha_r)
    yn_r = y_r + intersect_r * np.sin(alpha_r)

    # take center between both computed points, this is where the supporting
    # vector of the bisecting line points
    x, y = 0.5 * (xn_l + xn_r), 0.5 * (yn_l + yn_r)

    # distance from origin
    rho = np.sqrt(x * x + y * y)

    return rho, theta


def normalize(line):
    """
    Normalizes a line such that rho is positive and -pi <= theta < pi holds true.
    """
    r, t = line
    if r < 0:
        r, t = -r, np.pi + t
    while t < -np.pi:
        t += 2 * np.pi
    while t >= np.pi:
        t -= 2 * np.pi
    return r, t


def draw_line(img, rho, theta, color=(0, 0, 255), width=2):
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a * rho
    y0 = b * rho
    x1 = int(x0 + b * -1000)
    y1 = int(y0 + a * 1000)
    x2 = int(x0 - b * -1000)
    y2 = int(y0 - a * 1000)

    cv.line(img, (x1, y1), (x2, y2), color, width)


def eq(rho, theta):
    r = str(rho)
    t = str(theta)
    return r + ' = x * sin( ' + t + ' ) + y * cos( ' + t + ' )'


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('input', help='Image directory')

    args = parser.parse_args()

    stitch(args.input)
