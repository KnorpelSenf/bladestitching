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
