Coupled Simulation-Analysis Execution (ExTASY)
===============================================

Provides a command line interface to run multiple Molecular Dynamics (MD) simulations, which can be coupled to an analysis tool. The coupled simulation-analysis execution pattern (aka ExTASY pattern) currently supports two examples: 
(a) Gromacs as the "Simulator" and LSDMap as the "Analyzer"; (b) AMBER as the simulation engine and COCO as the analyzer. Due to the plugin-based architecture, this execution pattern, will be 
expandable as to support more Simulators and Analyzers.


Requirements
============

* python >= 2.7
* virtualenv >= 1.11
* pip >= 1.5
* Password-less ssh login to remote machine

> Some tips to setup a password-less login
> ```
> http://www.linuxproblem.org/art_9.html
> ```


Installation
=============

To install the ExTASY framework, create a virtual environment and use pip to install the package

```
virtualenv /tmp/test
source /tmp/test/bin/activate
cd /tmp/
pip install --upgrade git+https://github.com/radical-cybertools/radical.pilot.git@master#egg=radical.pilot
pip install --upgrade git+https://github.com/radical-cybertools/radical.ensemblemd.mdkernels.git@master#egg=radical.ensemblemd.mdkernels
git clone -b devel https://github.com/radical-cybertools/ExTASY.git
cd ExTASY
python setup.py install
export PYTHONPATH=$PYTHONPATH:/tmp/ExTASY
pip install numpy
```
> If you have multiple allocations on the same system, set the environment variable PROJECT_ID 
> to your allocation number 
>
> ```
> export PROJECT_ID = 'ABCXYZ123'
> ```

To verify the installation, check the current version

```
python -c 'import radical.ensemblemd.extasy as extasy; print extasy.version'
```

USAGE
======


RP_config
-----------

The RP_config file is used for defining the parameters related to Radical Pilot.

* Load_Preprocessor : The preprocessor to be used. Can be 'Gromacs' or 'Namd'
* Load_Simulator    : The Simulator to be loaded. Can be 'Gromacs' or 'Namd'
* Load_Analyzer     : The Analyzer to be loaded. Can be 'LSDMap' or 'CoCo'
* UNAME         : Username to access the remote machine
* REMOTE_HOST   : URL of remote machine
* WALLTIME      : Walltime for the complete job
* PILOTSIZE     : No. of cores to reserved for the entire job
* DBURL         : MongoDB URL

The above five variables are to be set before running any test or workload (Simulator only/ Analyzer only/ Sim-Analysis chain)

Kernel_config
-----------

The Kernel_config file is used for defining the parameters required in the Simulators and Analyzers. They are discussed 
as and when utilized below.



Running the workload
--------------------

1) **Simulator**


* To run just the Simulator, you will have to set the Load_Preprocessor, Load_Simulator variables in ``` /tmp/ExTASY/config/RP_config.py``` to 'Gromacs'. This
tells the tool to load the Gromacs Simulator.

* Next, open up the ```/tmp/ExTASY/config/kernel_config.py``` to set values which are kernel specific. For the Simulation you will have to set,


```

num_sims = 64 

input_gro_loc = '/tmp/ExTASY/run'
input_gro = 'input.gro'

grompp_loc = '/tmp/ExTASY/run'
grompp_name = 'grompp.mdp'

topol_loc = '/tmp/ExTASY/run'
topol_name = 'topol.top'

tmp_grofile = 'tmp.gro'

system_name = 'aladip_1000.gro'

```

> num_sims                  : Number of CUs. The input.gro file is divided such that each CU gets equal number of frames
>
> input_gro_loc, input_gro  : Location and name of the input file
>
> grompp_loc, grompp_name   : Location and name of the mdp file
>
> topol_loc, topol_name     : Location and name of the top file
>
> tmp_grofile               : Name of the temporary gro file
>
> system_name               : Name of the molecule, used in filenames

* Run ```extasy``` 


**What this does ...**

This command starts the execution. It will first submit a pilot on the REMOTE_HOST and reserve the number of cores as defined by the
PILOTSIZE. Once the pilot goes through the queue, the Preprocessor splits the input gro file as defined by ```input_gro``` into
temporary smaller files based on ```num_sims```. The Simulator is then loaded which submits Compute Units to the REMOTE_HOST
and takes as input the temporary files, a mdp file and a top file and runs the MD. The output is aggregated into one gro file to be used 
during the Analysis phase.

* * *

2) **Analyzer**

* To run just the Analyzer, you will have to set the Load_Analyzer variable in ``` /tmp/ExTASY/config/RP_config.py``` to 'LSDMap'. This
tells the tool to load the LSDMap Analyzer .

* Next, open up the ```/tmp/ExTASY/config/kernel_config.py``` to set values which are kernel specific. For the Analysis you will have to set,

```
lsdm_config = '/tmp/ExTASY/config'

system_name = 'out'

num_runs = 10000
```


> lsdm_config               : Location of the lsdmap config file (/config.ini)
> 
> system_name               : Name of the molecule, used in filenames
>
> num_runs                  : Number of runs during Analysis stage

> Rest of the variables are set based on ```system_name```

> egfile                    : Name of the eigen vector file
>
> evfile                    : Name of the eigen value file
>
> nearest_neighbor_file     : Name of the nearest neighbour file
>
> num_clone_files           : Name of clone file


* Run ```extasy```


**What this does ...**

This command starts the execution. It will first submit a pilot on the REMOTE_HOST and reserve the number of cores as defined by the
PILOTSIZE. Once the pilot goes through the queue, the Analyzer is loaded which looks for a gro file as defined by ```tmp_grofile```
in ```kernel_config.py``` in the current directory (from where ```extasy``` is run) and runs LSDMap on it based on the parameters
defined in ```/tmp/ExTASY/config/config.ini```.

* * *


3) **Simulator + Analyzer**

* To run both the Simulator and Analyzer as a Sim-Analysis chain set Load_Preprocessor, Load_Simulator and Load_Analyzer in ```../config/RP_kernel.py```.

* Set all the variables as before. Also set,

```
num_iterations = 1
```

> num_iterations              : Number of times the entire Sim-Analysis chain has to be performed

* Run ```extasy```


**What this does ...**

This command starts the execution.It will first submit a pilot on the REMOTE_HOST and reserve the number of cores as defined by the
PILOTSIZE. Once the pilot goes through the queue, the Preprocessor splits the input gro file as defined by ```input_gro``` into
temporary smaller files based on ```num_sims```. The Simulator is then loaded which submits Compute Units to the REMOTE_HOST
and takes as input the temporary files, a mdp file and a top file and runs the MD. The output is aggregated into one gro file to be used 
during the Analysis phase. The Analyzer is then loaded which looks for a gro file as defined by ```tmp_grofile```
in ```kernel_config.py``` in the current directory (from where ```extasy``` is run) and runs LSDMap on it based on the parameters
defined in ```/tmp/ExTASY/config/config.ini```.