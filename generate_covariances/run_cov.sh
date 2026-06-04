#!/bin/bash
#SBATCH --job-name=COV_LSST
#SBATCH --output=./projects/lsst_wz_forecasts/logs/%x_%a_%A.out
#SBATCH --error=./projects/lsst_wz_forecasts/logs/%x_%a_%A.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=05:00:00
#SBATCH --partition=standard
#SBATCH --account=timeifler

echo Job starting at `date` on node `hostname`

# Clear the environment from any previously loaded modules
module purge > /dev/null 2>&1
source ~/.bashrc
# module load python/3.11

cd $SLURM_SUBMIT_DIR

case "${SLURM_ARRAY_TASK_ID}" in
  1) YEAR=1 ;;
  2) YEAR=10 ;;
  *) echo "Unexpected SLURM_ARRAY_TASK_ID: ${SLURM_ARRAY_TASK_ID}" >&2; exit 1 ;;
esac

export OMP_PROC_BIND=close
export OMP_PLACES=cores
export OMP_NUM_THREADS=1

srun python3 ./cosmocov_process.py --year ${YEAR} --workers $SLURM_CPUS_PER_TASK