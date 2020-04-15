for dir in test_MPI_balsam_*; do
        cp forces.c $dir
        cp build_forces.sh $dir
done
