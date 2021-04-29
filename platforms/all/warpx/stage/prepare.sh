#!/bin/sh
for dir in test_*; do
        cp warpx_simf.py $dir
        cp read_sim_output.py $dir
        cp write_sim_input.py $dir
        cp warpx_support.py $dir
        cp -r sim $dir
        cd $dir
        chmod +x submit_*
        cd ..
done
