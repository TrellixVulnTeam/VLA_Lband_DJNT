#!/bin/bash
#SBATCH -t 1-00:00
#SBATCH --mem=512GB
#SBATCH --ntasks=32
#SBATCH --job-name=M33_dirty_cube
#SBATCH --output=casa-m33_dirtycube-%J.out
export OMP_NUM_THREADS=$SLURM_JOB_CPUS_PER_NODE

module restory my_default

source /home/ekoch/.bashrc
source /home/ekoch/preload.bash

export scratch_path=/home/ekoch/scratch/
export project_path=/home/ekoch/project/ekoch/

$HOME/casa-release-5.0.0-218.el7/bin/casa --nologger --nogui --log2term --nocrashreport -c $HOME/code/VLA_Lband/14B-088/HI/imaging/cedar/HI_dirty_cube.py $scratch_path

# Copy the dirty_cube folder into project space
cp -R $scratch_path/dirty_cube $project_path
