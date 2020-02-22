#!/bin/bash

mkdir data/processed/dec19/kalkar1/thermal/eval/hough

for strategy in {center,nub}; do
    mkdir data/processed/dec19/kalkar1/thermal/eval/hough/$strategy

    for threshold in {50..250..10}; do
        mkdir data/processed/dec19/kalkar1/thermal/eval/hough/$strategy/$threshold

        for maxvdev in {1..8}; do
            P=data/processed/dec19/kalkar1/thermal/eval/hough/$strategy/$threshold/$maxvdev
            mkdir $P $P/hough

            echo "Strategy: $strategy | Threshold: $threshold | Max dev: 0.$maxvdev >>> $P"
            ./stitch/hough.py data/processed/dec19/kalkar1/thermal/data/ -p $P/hough -o $P/hough.csv -s $strategy -t $threshold -d 0.$maxvdev --max-workers $(nproc) > $P/log.txt

        done
    done
done
