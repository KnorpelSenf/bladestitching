#!/bin/bash

BASE=data/processed/dec19/kalkar1/thermal

# Note that you can use
# for l in $(ls */*/log.txt);do echo $l,$(cat $l|grep "merely 0"|wc -l),$(cat $l|grep "merely 1"|wc -l),$(cat $l|grep "multiple" | wc -l);done
# in order to accumulate the results into a csv file (filename,zero,one,multiple) when the WD is in $BASE/eval/hough

for threshold in {50..250..10}; do
    for maxvdev in {1..8}; do
        P=$BASE/eval/hough/$threshold/$maxvdev
        mkdir -p $P/hough

        echo "Threshold: $threshold | Max dev: 0.$maxvdev >>> $P"
        ./stitch/hough.py $BASE/data/ -p $P/hough -o $P/hough.csv -s center -t $threshold -d 0.$maxvdev --max-workers $(nproc) > $P/log.txt

    done
done
