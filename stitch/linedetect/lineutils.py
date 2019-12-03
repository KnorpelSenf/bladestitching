#!/usr/bin/env python3
# -*- coding: utf8 -*-

import numpy as np

# Define selector functions for rho and theta
# as well as the coordinates of the foot point


def r(line):
    """
    Selects rho from a given line.
    """
    r, _ = line
    return r


def t(line):
    """
    Selects theta from a given line.
    """
    _, t = line
    return t


def x(line):
    """
    Selects the x coordinate of the foot point from a given line.
    """
    r, t = line
    return r * np.cos(t)


def y(line):
    """
    Selects the y coordinate of the foot point from a given line.
    """
    r, t = line
    return r * np.sin(t)


def eq(rho, theta):
    """
    Turns a line into a nice string representation.
    """
    r = str(rho)
    t = str(theta)
    return r + ' = x * sin( ' + t + ' ) + y * cos( ' + t + ' )'


def are_lines_similar(r, s, max_rho=30, max_theta=0.1):
    """
    Returns true if two given normalized lines
    do not deviate too far from each other
    as specified by the parameters.
    """
    rho_r, theta_r = r
    rho_s, theta_s = s
    diff_t = abs(theta_r - theta_s)
    # assumes normalized lines
    similar = abs(rho_r - rho_s) < max_rho and diff_t < max_theta
    similar_inverted = abs(
        rho_r + rho_s) < max_rho and abs(diff_t - np.pi) < max_theta
    return similar or similar_inverted


def move_origin(line, x, y, normalize=True):
    """
    Transforms a line's representation by moving the origin as specified.
    """
    rho, theta = line
    if y != 0:
        theta_star = np.arctan(x / y)
        alpha = 0.5 * np.pi - theta - theta_star
        cos_alpha = np.cos(alpha)
        if cos_alpha:
            r = rho / cos_alpha
            r_prime = np.sqrt(x * x + y * y) - r
            rho_prime = r_prime * cos_alpha
        else:  # do not divide by zero. rho stays the same iff cos_alpha == 0
            rho_prime = rho
    else:  # y == 0
        r = rho / np.cos(theta)
        r_prime = x - r
        rho_prime = r_prime * np.cos(theta)
    line = (rho_prime, theta)
    return normalize(line) if normalize else line


def rotate(line, theta, x=0, y=0, norm=True):
    """
    Rotates a line around the origin
    or optionally around a given coordinate
    by the specified angle.
    """
    custom_anchor = x != 0 or y != 0
    if custom_anchor:
        line = move_origin(line, x, y, norm=False)
    r, t = line
    t += theta
    line = (r, t)
    if custom_anchor:
        line = move_origin(line, -x, -y, norm=False)
    return normalize(line) if norm else line


def translate(line, x=0, y=0, norm=True):
    """
    Translates a line by the given distance in x and y direction.
    """
    rho, theta = line
    old_x, old_y = (rho * np.cos(theta),
                    rho * np.sin(theta))
    new_x, new_y = old_x + x, old_y + y
    new_rho = np.sqrt(new_x * new_x + new_y * new_y)
    # TODO: calculate fresh theta if old rho was 0
    # (as we never encounter lines crossing the origin in our data,
    # this usually doesn't happen in practice, but still)
    new_theta = np.arccos(new_x / rho)
    line = (new_rho, new_theta)
    return normalize(line) if norm else line


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


def vertical_distance(line0, line1):
    """
    Computes the vertical distance `line1` needs to moved
    such that it's foot point lies on `line0`.
    """
    # coordinates of foot points
    x0, y0 = x(line0), y(line0)
    x1, y1 = x(line1), y(line1)

    # construct a triangle between the two foot points
    # and the point that has the same x coordinate as line1's foot point
    # but lies on line0

    # apply the law of sines to this triangle
    # where a is the vertical distance
    # and b is the distance between the two foot points
    dist_x = x0 - x1
    dist_y = y0 - y1

    if not dist_x:
        # a == b && c == 0 && gamma == 0 holds true
        return dist_y

    beta = t(line0)  # (!)
    sinbeta = np.sin(beta)

    if not sinbeta:
        # beta in { 0, pi }, so a is on both line0 and line1,
        # therefore it is line0 == line1
        return 0

    # b is the distance between the two foot points
    b = np.sqrt(dist_x * dist_x + dist_y * dist_y)
    # it is gamma + arctan(dist_y / dist_x) == 0.5 * pi, so
    gamma = 0.5 * np.pi - np.arctan(dist_y / dist_x)
    # alpha + beta + gamma == pi (if this was not obvious)
    alpha = np.pi - beta - gamma
    # law of sines
    return np.sin(alpha) * b / sinbeta
