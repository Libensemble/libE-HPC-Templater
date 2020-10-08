for dir in test_*
do
  cd $dir
  bsub submit_*.sh
  cd ../
done
