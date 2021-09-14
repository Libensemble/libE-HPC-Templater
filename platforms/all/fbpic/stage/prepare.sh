#!/bin/sh
for dir in test_*; do
        cp -r libe_opt $dir
        cp *.py $dir
        cd $dir
        chmod +x submit_*
        cd ..
done
