#!/usr/bin/env python3
# -*- coding: utf8 -*-

import os
import ffmpeg


def main(args):

    print('Extracting frames from', args.videofile, 'to directory', args.output)
    stream = ffmpeg.input(args.videofile)
    stream = ffmpeg.filter(stream, 'fps', fps=args.fps)
    stream = ffmpeg.output(stream, os.path.join(args.output, 'frame-%06d.jpg'))
    ffmpeg.run(stream)
    print('Done.', args.output)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('videofile', help='Video file')
    parser.add_argument('-o', '--output', help='Output directory')
    parser.add_argument(
        '--fps', help='Frames extracted per second of video. Use 10 or 1/2 (default) or 0.3 or the like')

    args = parser.parse_args()

    if not args.fps:
        args.fps = '1/2'

    if not args.output:
        # split ext
        filename, _ = os.path.splitext(args.videofile)
        args.output = filename + '_frames'

    os.makedirs(args.output, exist_ok=True)

    print(args)

    main(args)
