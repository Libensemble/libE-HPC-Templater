#!/bin/sh
for dir in test_*; do
        cp all_machine_specs.py $dir
        cp warpx_simf.py $dir
        cp read_sim_output.py $dir
        cp write_sim_input.py $dir
        cd $dir
        chmod +x submit_*
        cd ..
done
