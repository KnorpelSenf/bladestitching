#!/bin/bash

for strategy in {center,nub}; do
    mkdir data/processed/dec19/kalkar1/thermal/eval/$strategy

    for maxvdev in {1..8}; do
        mkdir data/processed/dec19/kalkar1/thermal/eval/$strategy/$maxvdev

        for threshold in {50..250..10}; do
            P=data/processed/dec19/kalkar1/thermal/eval/$strategy/$maxdev/$threshold
            mkdir $P $P/hough

            ./stitch/hough.py data/processed/dec19/kalkar1/thermal/data/ -p $P/paint -o $P/hough.csv -s $strategy -t $threshold -d 0.$maxvdev

        done
    done
done
