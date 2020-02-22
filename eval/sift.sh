#!/bin/bash

mkdir data/processed/dec19/kalkar1/thermal/eval/sift

for count in {0,10,20,50,100,200,500,1000,2000,5000,10000}; do
    mkdir data/processed/dec19/kalkar1/thermal/eval/sift/$count

    for ct in {1..9}; do
        mkdir data/processed/dec19/kalkar1/thermal/eval/sift/$count/$ct

        for et in {2..18..2}; do
            P=data/processed/dec19/kalkar1/thermal/eval/sift/$count/$ct/$et
            mkdir $P $P/sift

            echo "Count: $count | CT: $ct | ET: $et >>> $P"
            ./unused/sift.py data/processed/dec19/kalkar1/thermal/data/ -o $P/sift -c $count -q $ct -d $et > $P/log.txt

        done
    done
done
