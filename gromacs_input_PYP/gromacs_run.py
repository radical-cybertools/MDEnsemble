import os
import time
if __name__ == "__main__":
    t1=time.time()
    os.system('/bin/bash -l -c "module load gromacs"')
    os.system('/bin/bash -l -c "module load openmpi"')
    os.system('/bin/bash -l -c "grompp -n index.ndx"')
    os.system('/bin/bash -l -c "mdrun"')
