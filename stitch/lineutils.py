#!/usr/bin/env python3
# -*- coding: utf8 -*-

import numpy as np

# define selector functions for rho and theta
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


# define some functions for pretty-printing lines
# as well as their foot points

def eq(line):
    """
    Turns a line into a nice string representation.
    """
    rho, theta = line
    r = '{:6.2f}'.format(float(rho))
    t = '{:4.4f}'.format(float(theta))
    return r + ' = x * sin(' + t + ') + y * cos(' + t + ')'


def xy(line):
    """
    Turns a line into a nice string representation of its foot point.
    """
    return 'FP({:4d}, {:4d})'.format(x(line), y(line))


# define a couple of helper functions
# to perform various computations on lines

def are_lines_similar(r, s, max_rho=30, max_theta=0.1):
    """
    Returns true if two given normalized lines
    do not deviate too far from each other
    as specified by the parameters,
    and false otherwise.
    """
    rho_r, theta_r = r
    rho_s, theta_s = s
    diff_t = abs(theta_r - theta_s)
    # assumes normalized lines
    similar = abs(rho_r - rho_s) < max_rho and diff_t < max_theta
    similar_inverted = abs(
        rho_r + rho_s) < max_rho and abs(diff_t - np.pi) < max_theta
    return similar or similar_inverted


def is_line_left(line, x, y):
    """
    Returns true if the given line is right of the given point
    in the sense that the line's foot point
    would be in the first or fourth quadrant
    if the given point would be the origin.
    """
    return not is_line_right(line, x, y)


def is_line_right(line, x, y):
    """
    Returns true if the given line is left of the given point
    in the sense that the line's foot point
    would be in the second or third quadrant
    if the given point would be the origin.
    """
    halfpi = np.pi / 2
    return -halfpi <= t(move_origin(line, x, y, norm=True)) < halfpi


def translate(line, x=0, y=0, norm=True):
    """
    Translates a line by the given distance in x and y direction.
    """
    return move_origin(line, -x, -y, norm=norm)


def move_origin(line, x=0, y=0, norm=True):
    """
    Transforms a line's representation by moving the origin as specified.
    """
    rho, theta = line

    # get polar coordinates of point x, y
    dist = np.sqrt(x * x + y * y)
    alpha = np.arctan2(y, x)

    # imagine a line perpendicular to the given line
    # that is also crossing through the given point

    # compute the angle between the normal vector of the given line (theta)
    # and the line from the origin to our given point (alpha)
    # so we can construct a right triangle over our imagined line
    # with the line from the origin to our given point as a hypotenuse
    omega = theta - alpha

    # compute new distance from origin, this is the distance from x, y to line
    # and this very distance is a part of our imagined line
    rho_prime = rho - dist * np.cos(omega)

    line = (rho_prime, theta)
    return normalize(line) if norm else line


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
    theta = (theta_l + theta_r) / 2

    # coordinates of foot point of l (and r, respectively)
    # (from origin move by rho_l in the direction of theta_l)
    x_l, y_l = (rho_l * np.cos(theta_l), rho_l * np.sin(theta_l))
    x_r, y_r = (rho_r * np.cos(theta_r), rho_r * np.sin(theta_r))

    # move in this direction from foot point of l (and r respectively)
    # to get to the point where the supporting vector of the bisecting
    # line intersects l (and r respectively)
    alpha_l = np.pi/2 + theta_l
    alpha_r = np.pi/2 + theta_r

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
    x, y = (xn_l + xn_r) / 2, (yn_l + yn_r) / 2

    # distance from origin
    rho = np.sqrt(x * x + y * y)

    return rho, theta


def vertical_distance(line0, line1):
    """
    Computes the distance `line1` needs to moved vertically
    such that its foot point lies on `line0`. If `line0` is
    a vertical line (its theta value is either `0` or `pi`),
    this distance is either 0 (if `line1`'s foot point is on `line0`)
    or it cannot be defined (if `line1`'s foot point is not on `line0`).
    In both cases, `0` is returned.
    """

    # construct a triangle between the two foot points
    # and the point that has the same x coordinate as line1's foot point
    # but lies on line0

    # we will later apply the law of sines to our triangle
    # where a is the vertical distance
    # and b is the distance between the two foot points
    # (we will call this the main triangle)
    # in order to compute a from the other values
    # (they can easily be determined by looking at line0 and line1)

    # compute the opposite angle of b
    beta = -t(line0)  # (!)
    sinbeta = np.sin(beta)

    if not sinbeta:
        # beta in { 0, pi }, so a is on line0
        # and it is also parallel to line1,
        # therefore line1's foot point is already on line0
        # (or it could never be moved there)
        return 0

    # coordinates of foot points
    x0, y0 = x(line0), y(line0)
    x1, y1 = x(line1), y(line1)

    # L∞ distance between foot points
    dist_x = x0 - x1
    dist_y = y0 - y1

    if not dist_x:
        # x0 == x1 holds true yielding gamma == 0
        return dist_y

    # recall that b is the distance between the two foot points
    b = np.sqrt(dist_x * dist_x + dist_y * dist_y)
    # np.pi/2 + gamma + (-arctan2(dist_y, dist_x)) == pi
    # holds true in the triangle between the a, b and the x axis
    gamma = np.pi/2 + np.arctan2(dist_y, dist_x)
    # alpha + beta + gamma == pi (if this was not obvious)
    alpha = np.pi - beta - gamma
    # law of sines in the main triangle
    return np.sin(alpha) * b / sinbeta


def root(line):
    """
    Assume `cos(t(line)) != 0`. Be `f` the linear function
    that describes `line`.

    This function then solves `f(x) = 0` for `x` and returns `x`.
    In other words, it returns the `x` value of the intersection point
    between the given line and the x-axis.

    Crashes on `cos(t(line)) == 0` (division by zero).
    """
    rho, theta = line
    return rho / np.cos(theta)
