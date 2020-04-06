for dir in test_*; do
        cp forces_simf.py $dir
        cd $dir
        chmod +x submit_*
        cd ..
done
