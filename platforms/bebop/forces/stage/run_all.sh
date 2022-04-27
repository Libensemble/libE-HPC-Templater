for dir in test_*
do
  cd $dir
  sbatch submit_*
  cd ../
done
