#!/bin/bash

BASE=data/processed/dec19/kalkar1/thermal

mkdir $BASE/eval/sift

for count in {0,10,20,50,100,200,500,1000,2000,5000,10000}; do
    mkdir $BASE/eval/sift/$count

    for ct in {1..9}; do
        mkdir $BASE/eval/sift/$count/$ct

        for et in {2..18..2}; do
            P=$BASE/eval/sift/$count/$ct/$et
            mkdir $P $P/sift

            echo "Count: $count | CT: 0.0$ct | ET: $et >>> $P"
            ./unused/sift.py $BASE/data/ -o $P/sift -c $count --contrast-threshold 0.0$ct --edge-threshold $et > $P/log.txt

        done
    done
done
