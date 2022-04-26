#!/bin/sh
for dir in test_MPI_balsam2_*; do
        cp forces.c $dir
        cp define_apps.py $dir
        cp forces_simf_balsam.py $dir
        cp build_forces.sh $dir
done
