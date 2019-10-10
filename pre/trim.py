#!/usr/bin/env python3
# -*- coding: utf8 -*-

import os
import ffmpeg


def main(args):

    print('Processing', args.videofile, ', creating file', args.output)
    stream = ffmpeg.input(args.videofile)

    if args.start:
        if args.end:
            print('Shaving off first', args.start,
                  'and last', args.end, 'seconds')
            stream = ffmpeg.trim(stream, start=args.start, end=args.end)
        else:
            print('Shaving off first', args.start, 'seconds')
            stream = ffmpeg.trim(stream, start=args.start)
    else:
        if args.end:
            print('Shaving off last', args.end, 'seconds')
            stream = ffmpeg.trim(stream, end=args.end)
        else:
            print('Converting video file')

    stream = ffmpeg.setpts(stream, 'PTS-STARTPTS')

    stream = ffmpeg.output(stream, args.output, **{'qscale': 0})

    ffmpeg.run(stream)
    print('Done.', args.output)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('videofile',
                        help='Video file to trim')
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('-s', '--start', type=int,
                        help='Start of trimmed video in seconds')
    parser.add_argument('-e', '--end', type=int,
                        help='End of trimmed video in seconds')

    args = parser.parse_args()

    if not args.output:
        # split ext
        filename, file_extension = os.path.splitext(args.videofile)
        args.output = filename + '_trimmed' + file_extension

    print(args)

    main(args)
