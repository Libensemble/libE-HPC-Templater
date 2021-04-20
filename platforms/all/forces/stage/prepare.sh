#!/bin/sh
for dir in test_*; do
        cp forces_simf.py $dir
        cp cleanup.sh $dir
        cp forces_support.py $dir
        cp build_forces.sh $dir
        cp forces.c $dir
        cd $dir
        chmod +x submit_*
        cd ..
done
