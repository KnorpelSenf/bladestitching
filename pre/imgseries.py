#!/usr/bin/env python3
# -*- coding: utf8 -*-

import os
import ffmpeg


def imgseries(videofile, output, fps):

    print('Extracting frames from', videofile, 'to directory', output)
    (
        ffmpeg.input(videofile)
        .filter('fps', fps=fps)
        .output(os.path.join(output, 'frame-%06d.jpg'))
        .run()
    )
    print('Done.', output)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('videofile', help='Video file')
    parser.add_argument('-o', '--output', help='Output directory')
    parser.add_argument('--fps', default='1/2',
                        help='Frames extracted per second of video. Use 10 or 1/2 (default) or 0.3 or the like')

    args = parser.parse_args()

    if not args.output:
        # split ext
        filename, _ = os.path.splitext(args.videofile)
        args.output = filename + '_frames'

    os.makedirs(args.output, exist_ok=True)

    print(args)

    imgseries(args.videofile, args.output, args.fps)
