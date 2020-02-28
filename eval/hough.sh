#!/bin/bash

BASE=data/processed/dec19/kalkar1/thermal

for strategy in {center,nub}; do
    for threshold in {50..250..10}; do
        for maxvdev in {1..8}; do
            P=$BASE/eval/hough/$strategy/$threshold/$maxvdev
            mkdir -p $P/hough

            echo "Strategy: $strategy | Threshold: $threshold | Max dev: 0.$maxvdev >>> $P"
            ./stitch/hough.py $BASE/data/ -p $P/hough -o $P/hough.csv -s $strategy -t $threshold -d 0.$maxvdev --max-workers $(nproc) > $P/log.txt

        done
    done
done
