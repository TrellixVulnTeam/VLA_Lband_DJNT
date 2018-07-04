#!/bin/bash
#SBATCH --time=30:00:00
#SBATCH --mem=515000M
#SBATCH --ntasks-per-node=32
#SBATCH --nodes=1
#SBATCH --job-name=M33_transform_and_uvsub-%J
#SBATCH --output=casa-m33_transform_and_uvsub-%J.out

export OMP_NUM_THREADS=$SLURM_JOB_CPUS_PER_NODE

module restore my_default

source /home/ekoch/.bashrc
source /home/ekoch/preload.bash

export scratch_path=/home/ekoch/scratch/17B-162_imaging/

# Move to scratch space b/c casa write out the temporary files into the same folder
cd $scratch_path

Xvfb :1 &
export DISPLAY=:1

$HOME/casa-release-5.3.0-143.el7/bin/casa --nologger --nogui --log2term --nocrashreport -c $HOME/code/VLA_Lband/17B-162/imaging/M33_transform_and_uvsub.py
