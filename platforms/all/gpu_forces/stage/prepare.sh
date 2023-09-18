#!/bin/sh
for dir in test_*; do
        cp forces_gpu_simf.py $dir
        cp build_forces.sh $dir
        cp forces.c $dir
        cd $dir
        chmod +x submit_*
        cd ..
done
