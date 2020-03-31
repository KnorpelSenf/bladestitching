# Blade Stitching

Source code and more for Steffen Trog's bachelor thesis.
If you were looking for this repo, you know what it's all about.
In case you just stumbled upon it: Performing panoramic image stitching of thermographic video footage in order to compute full-width pictures of rotor blades of wind engines, thus enabling an affordable inspection method.

## About

So far, this repo contains code that performs the following tasks:

1) **Preprocessing.**
This includes the following steps, all of which are achieved by a separate, adequately named script.
All scripts take AVI video files recorded by drones flying along rotor blades of wind engines as input.
    * Trim the videos manually to the relevant parts
    * Sample JPG images from the trimmed video at a given fps rate
    * Crop the resulting images
    * Scale the resulting images
1) **Feature detection.**
These scripts take an image (or a directory full of images) as input.
Note that feature detection has been found to fail on the given data as the number of features on the background outweigh those on the rotor blade by a far margin in number and temporal robustness.
    * Detect and highlight features using Good Features to Track (GFTT)
    * Detect and hightlight features using Scale Invariant Feature Transform (SIFT)
    * Apply template matching to further refine the results of the Hough stitching package.
1) **Hough stitching.**
This package also contains a utility module named `lineutils.py` that provides basic geometric operations to other scripts in the same directory. All other files take again an image or a directory of images as input.
They're supposed to work on the output of the preprocessing scripts.
    * Apply a Hough transformation and store the resulting linear equations (polar coordinates) in a CSV file, ambiguously keyed by file names
    * Use a CSV file of linear equations to compute a basic stitching result, thus outputting a list of pixel-wise translations per file name
    * The same thing with a little optimization that is well justified but deteriorating the results, same script as the regular stitching but used with program argument
    * Iterative stitching (again usable via program argument)
    * “Intelligently” color the background of an image based on Hough lines, outputting an image containing all black but the rotor blade (or any other color, if specified)
1) **Postprocessing.**
A few helper scripts that achieve the following.
    * Average over a Hough stitching result in a sliding window manner
    * Merge multiple image files into a panorama based on a CSV file containing pixel-wise translations per file name
    * Apply padding to image files based on pixel-wise translations so both images can be viewed as if they we're in the same coordinate system
    * Rotate an image (or all images in a directory) by 90 degrees clockwise.
1) **Visualization.**
There's a Vue.js based visualization HTML file providing a minimal UI to interactively explore the quality of stiching results.
Requires padded images to ensure comparability.
Note that the Vue library will be loaded via CDN, so a network connection will be required.

All code will be provided with at least a minimal documentation.
Many scripts will rely heavily on geometric constructions.
Variables are named accordingly.
Often, the constructions will be described along the lines.
Please feel encouraged to grab a pencil and a sheet of paper if you wish to follow along.

## Installation

Clone the repo, e.g. using SSH, and execute:

```bash
git clone git@github.com:KnorpelSenf/bladestitching.git
virtualenv venv && source venv/bin/activate
pip install -r requirements.txt
```

## Directory structure

| Directory   | What's in there                                                                      |
|-------------|--------------------------------------------------------------------------------------|
| `pre`       | Preprocessing scripts                                                                |
| `stitch`    | Hough line based stitching                                                           |
| `post`      | Postprocessing scripts                                                               |
| `unused`    | Feature detection and template matching                                              |
| `visualize` | Visualization                                                                        |
| `eval`      | A few scripts (bash and python) to perform grid searches and aggregate their results |

For all python scripts mentioned in the following sections you can get detailed usage instructions by supplying `--help`.

## Preprocessing tasks

There's a number of preprocessing steps to perform on the AVI video files.

All scripts working on images also work on a directory.
Supply a directory to image processing scripts to apply the same script for all images inside the directory.
Make sure all elements in the directory are image files.
This behavior is useful once the images were sampled from a video.

### Trimming videos

Assume you want to shave off the start and the end of a video and only keep the interval between seconds 42 and 1729.
Trim the video using:

```bash
# Virtual environment if you did not set it already
source venv/bin/activate
# Script to trim video
./pre/trim.py <input> --output <output> --start 42 --end 1729
```

Use `-o`, `-s` and `-e` as abbreviations for `--output`, `--start` and `--end`, respectively.

Any argument (except `input`) can be omitted entirely.
In all cases a default value will be used.

All following scripts behave similarly.

### Sampling images from videos

Choose your fps rate and supply it to `pre/imgseries.py`. Default is 1/2 (used in thesis: 15).

### Cropping images

Crop your images from north, south, east and west using `pre/crop.py`.

### Scaling images

Scale your images by any factor and using any interpolation method using `pre/scale.py`.

## Stitching, postprocessing tasks, visualization, feature detection

Confer the above description to find out about what inputs a scripts relies on and what it yields as a result.
In general, all inputs are mandatory arguments, while a possible output needs to be specified explicitely with the `-o` flag.
Kindly supply `--help` to get a detailed description of the available arguments per script.
Also, don't hesitate to read the arg parsing as it is straightforward.

## Complete pipeline

In the corresponding thesis to this repository, the following steps were shown to work well.
Recall that these results are based on a small dataset and most likely will not generalize seemlessly to further recordings.

```bash
./pre/trim.py <input video> -s <start number of seconds> -e <end number of seconds> -o <output video>
./pre/imseries.py <trimmed input file> --fps <number of fps> -o <output data directory>
./stitch/hough.py <input data directory> -t <Hough transform threshold> -d 0.3 --max-workers <number of threads to use> -o <output csv>
./stitch/stitch.py iterative <Hough input csv> <image height> -o <output csv>
./post/merge.py <stitch input csv> <input data directory> <output panorama>
```
