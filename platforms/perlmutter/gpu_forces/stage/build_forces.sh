#!/bin/bash

cc -DGPU -Wl,-znoexecstack -O3 -fopenmp -mp=gpu -target-accel=nvidia80 -o forces_gpu.x forces.c
cc -Wl,-znoexecstack -O3 -fopenmp -o forces_cpu.x forces.c