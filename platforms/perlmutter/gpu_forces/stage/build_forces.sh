#!/bin/bash

mpicc -DGPU -O3 -fopenmp -mp=gpu -o forces.x forces.c