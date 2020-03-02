import numpy as np
import pandas as pd

# Transform [(0,0,a),(0,1,b),(1,0,c),(1,1,d)] to [[a,b],[c,d]]

def transform(filename):
    df = pd.read_csv(filename)
    vals = df.values
    cols = vals.transpose()
    xrange = (min(cols[0]), max(cols[0]))
    yrange = (min(cols[1]), max(cols[1]))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('input', help='Input CSV')

    args = parser.parse_args()

    transform(args.input)
