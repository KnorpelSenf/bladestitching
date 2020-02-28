#!/bin/bash

BASE=data/processed/dec19/kalkar1/thermal

mkdir $BASE/eval $BASE/eval/gftt

for count in {10,20,50,100,200,500,1000,5000}; do
    mkdir $BASE/eval/gftt/$count

    for quality in {0.005,0.01,0.015,0.02,0.025,0.03,0.035,0.04,0.045,0.05,0.055,0.06,0.065,0.07,0.08,,0.09,0.1,0.2,0.5}; do
        P=$BASE/eval/gftt/$count/$quality
        mkdir $P $P/gftt

        echo "Count: $count | Quality: $quality >>> $P"
        ./unused/gftt.py $BASE/data/ -o $P/gftt -c $count -q $quality -d 5 >$P/log.txt

    done
done
