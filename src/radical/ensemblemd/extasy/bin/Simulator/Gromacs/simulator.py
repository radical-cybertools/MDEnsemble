__author__ = 'vivek'

import radical.pilot
import os
import time
from config.parameters import *
import saga

def Simulator(umgr):


    p1 = time.time()
    input_to_data_transfer_task = ['%s/%s' % (grompp_loc, grompp_name), '%s/%s' % (topol_loc, topol_name)]

    #SHARED INPUT TASK
    data_transfer_task = radical.pilot.ComputeUnitDescription()
    data_transfer_task.executable = "/bin/true"
    data_transfer_task.cores = 1
    data_transfer_task.input_data = input_to_data_transfer_task

    units = umgr.submit_units(data_transfer_task)

    # Wait for data transfer task to finish.
    umgr.wait_units()

    print 'grompp and topol sent'

    shared_input_url = saga.Url(units.working_directory).path

    curdir = os.path.dirname(os.path.realpath(__file__))

    gromacs_tasks = []
    for i in range(0, 64):
        gromacs_task = radical.pilot.ComputeUnitDescription()
        gromacs_task.executable = "/bin/bash"
        gromacs_task.arguments = ['-l','-c','". run_simulator.sh %s %s %s %s"' % (shared_input_url,grompp_name,topol_name,outgrofile_name)]
        gromacs_task.input_data = ['%s/run_simulator.sh'%curdir,'%s/run.sh > run.sh'%curdir,'%s/temp/start%s.gro > start.gro' % (os.getcwd(), i)]
        gromacs_task.output_data = ['out.gro > out%s.gro' % i]
        gromacs_task.cores = 1

        gromacs_tasks.append(gromacs_task)

    units = umgr.submit_units(gromacs_tasks)

    # Wait for all compute units to finish.
    umgr.wait_units()

    if os.path.exists('%s/%s' % (os.getcwd(),outgrofile_name)):
        os.remove(os.getcwd() + '/' + outgrofile_name)

    with open(outgrofile_name, 'w') as output_grofile:
        for i in range(0,64):
            with open('out%s.gro' % i, 'r') as output_file:
                for line in output_file:
                    print >> output_grofile, line.replace("\n", "")
            os.remove('out%s.gro'%i)
    p2 = time.time()

    print 'Simulation Time : ', (p2-p1)
