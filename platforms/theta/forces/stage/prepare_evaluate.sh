#!/bin/sh
for dir in test_*; do
        cp wait_and_evaluate.py $dir
        cp wait_on_queue.py $dir
done
