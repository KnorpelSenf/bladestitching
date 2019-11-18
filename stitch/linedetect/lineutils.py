#!/usr/bin/env python3
# -*- coding: utf8 -*-

import numpy as np


def eq(rho, theta):
    r = str(rho)
    t = str(theta)
    return r + ' = x * sin( ' + t + ' ) + y * cos( ' + t + ' )'


def are_lines_similar(r, s, max_rho=30, max_theta=0.1):
    rho_r, theta_r = r
    rho_s, theta_s = s
    diff_t = abs(theta_r - theta_s)
    similar = abs(rho_r - rho_s) < max_rho and diff_t < max_theta
    similar_inverted = abs(
        rho_r + rho_s) < max_rho and abs(diff_t - np.pi) < max_theta
    return similar or similar_inverted


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

    # coordinates of foot point of l (and r, respectively)
    # (from origin move by rho_l in the direction of theta_l)
    x_l, y_l = (rho_l * np.cos(theta_l), rho_l * np.sin(theta_l))
    x_r, y_r = (rho_r * np.cos(theta_r), rho_r * np.sin(theta_r))

    # move in this direction from foot point of l (and r respectively)
    # to get to the point where the supporting vector of the bisecting
    # line intersects l (and r respectively)
    alpha_l = 0.5 * np.pi + theta_l
    alpha_r = 0.5 * np.pi + theta_r

    # move by this number of pixels from foot point of l (and r respectively)
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
