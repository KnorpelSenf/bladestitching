#!/usr/bin/env python3
# -*- coding: utf8 -*-

import ffmpeg
import os


def trim(videofile, output, start, end):

    print('Processing', videofile, ', creating file', output)
    stream = ffmpeg.input(videofile)

    if start:
        if end:
            print('Shaving off first', start,
                  'and last', end, 'seconds')
            stream = ffmpeg.trim(stream, start=start, end=end)
        else:
            print('Shaving off first', start, 'seconds')
            stream = ffmpeg.trim(stream, start=start)
    else:
        if end:
            print('Shaving off last', end, 'seconds')
            stream = ffmpeg.trim(stream, end=end)
        else:
            print('Converting video file')

    (
        ffmpeg.setpts(stream, 'PTS-STARTPTS')
        .output(output, **{'qscale': 0})
        .run()
    )
    print('Done.', output)


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

    trim(args.videofile, args.output, args.start, args.end)
