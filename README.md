# Blade Stitching

Source code and more for Steffen Trog's bachelor thesis.

## Installation

Clone the repo, e. g. using SSH, and execute:

```bash
git@git.zs.informatik.uni-kiel.de:stu204766/bladestitching.git
virtualenv venv && venv/bin/activate
pip install -r requirements.txt
```

## Directory structure

| Directory | What's in there       |
|-----------|-----------------------|
| `pre`     | Preprocessing scripts |

## Preprocessing tasks

There's a number of preprocessing steps to perform on the AVI video files.
For all python scripts mentioned in this section you can get detailed usage instructions by supplying `--help`.

### Trimming videos

Assume you want to shave off the start and the end of a video and only keep the interval between seconds 42 and 1729.
Trim the video using `pre/trim.py`.

### Sampling images from videos

Choose your fps rate and supply it to `pre/imgseries.py`. Default is 1/2.
