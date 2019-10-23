# Blade Stitching

Source code and more for Steffen Trog's bachelor thesis.

## About

So far, this repo contains code that performs the following tasks:

1) Preprocessing. This includes:
    * Take AVI video files recorded by drones flying along rotor blades of wind engines as input,
    * Trim the videos manually to the relevant parts,
    * Sample JPG images from the trimmed video at a given fps rate
    * Crop the resulting images, and
    * Scale the resulting images.
2) Feature detection. This includes:
    * Take an image (or a directory full of images) as input,
    * Detect and highlight features using Good Features to Track (GFTT), or
    * Detect and hightlight features using Scale Invariant Feature Transform (SIFT)
3) Line detection. This includes:
    * Take an image (or a directory full of images) as input, and
    * Detect and filter lines using a Hough transform

All code will be provided with at least a minimal documentation.

## Installation

Clone the repo, e. g. using SSH, and execute:

```bash
git clone git@git.zs.informatik.uni-kiel.de:stu204766/bladestitching.git
virtualenv venv && venv/bin/activate
pip install -r requirements.txt
```

## Directory structure

| Directory       | What's in there           |
|-----------------|---------------------------|
| `pre`           | Preprocessing scripts     |
| `featuredetect` | Feature detection scripts |
| `linedetect`    | Line detection scripts    |

## Preprocessing tasks

There's a number of preprocessing steps to perform on the AVI video files.
For all python scripts mentioned in this section you can get detailed usage instructions by supplying `--help`.

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

Choose your fps rate and supply it to `pre/imgseries.py`. Default is 1/2.

### Cropping images

Crop your images from north, south, east and west using `pre/crop.py`.

### Scaling images

Scale your images by any factor and using any interpolation method using `pre/scale.py`.

## Feature detection tasks

Use `featuredetect/gftt.py` and `featuredetect/sift.py` to find features with Good Features to Track and SIFT, respectively.

## Line detection tasks

Use `linedetect/hough.py` to detect Hough lines.
