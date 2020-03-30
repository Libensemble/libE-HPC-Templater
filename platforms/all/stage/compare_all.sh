for dir in test_*
do
  cd $dir
  echo -e "Comparing $dir:"
   ../compare_npy.py run_libe_forces_results_History_*.npy
  cd ..
done
