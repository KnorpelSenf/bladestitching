#!/bin/bash

BASE=data/processed/dec19/kalkar1/thermal

for threshold in {50..250..10}; do
    for maxvdev in {1..8}; do
        P=$BASE/eval/hough/$threshold/$maxvdev
        mkdir -p $P/hough

        echo "Threshold: $threshold | Max dev: 0.$maxvdev >>> $P"
        ./stitch/hough.py $BASE/data/ -p $P/hough -o $P/hough.csv -s center -t $threshold -d 0.$maxvdev --max-workers $(nproc) > $P/log.txt

    done
done
