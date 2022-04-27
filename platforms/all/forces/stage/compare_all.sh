for dir in test_*
do
  cd $dir
  echo -e "Comparing $dir:"
   ../compare_npy.py run_libe_forces_history_*.npy
  cd ..
done
