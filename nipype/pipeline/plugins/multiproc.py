# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""Parallel workflow execution via multiprocessing

Support for child processes running as non-daemons based on
http://stackoverflow.com/a/8963618/1183453
"""

from multiprocessing import Process, Pool, cpu_count, pool
from traceback import format_exception
import sys

from .base import (DistributedPluginBase, report_crash)
import semaphore_singleton



def run_node(node, updatehash):
    result = dict(result=None, traceback=None)
    try:
        result['result'] = node.run(updatehash=updatehash)
    except:
        etype, eval, etr = sys.exc_info()
        result['traceback'] = format_exception(etype,eval,etr)
        result['result'] = node.result
    return result



def release_lock(args):
    print 'releasing semaphore'
    semaphore_singleton.semaphore.release()


class NonDaemonProcess(Process):
    """A non-daemon process to support internal multiprocessing.
    """
    def _get_daemon(self):
        return False

    def _set_daemon(self, value):
        pass

    daemon = property(_get_daemon, _set_daemon)

class NonDaemonPool(pool.Pool):
    """A process pool with non-daemon processes.
    """
    Process = NonDaemonProcess

class MultiProcPlugin(DistributedPluginBase):
    """Execute workflow with multiprocessing

    The plugin_args input to run can be used to control the multiprocessing
    execution. Currently supported options are:

    - n_procs : number of processes to use
    - non_daemon : boolean flag to execute as non-daemon processes

    """

    def __init__(self, plugin_args=None):
        super(MultiProcPlugin, self).__init__(plugin_args=plugin_args)
        self._taskresult = {}
        self._taskid = 0
        non_daemon = True
        n_procs = cpu_count()
        if plugin_args:
            if 'n_procs' in plugin_args:
                n_procs = plugin_args['n_procs']
            if 'non_daemon' in plugin_args:
                non_daemon = plugin_args['non_daemon']
        if non_daemon:
            # run the execution using the non-daemon pool subclass
            self.pool = NonDaemonPool(processes=n_procs)
        else:
            self.pool = Pool(processes=n_procs)


    def _get_result(self, taskid):
        if taskid not in self._taskresult:
            raise RuntimeError('Multiproc task %d not found'%taskid)
        if not self._taskresult[taskid].ready():
            return None
        return self._taskresult[taskid].get()

    def _submit_job(self, node, updatehash=False):
        self._taskid += 1
        try:
            if node.inputs.terminal_output == 'stream':
                node.inputs.terminal_output = 'allatonce'
        except:
            pass
        self._taskresult[self._taskid] = self.pool.apply_async(run_node, (node,
                                                                updatehash,), callback=release_lock)
        return self._taskid

    def _report_crash(self, node, result=None):
        if result and result['traceback']:
            node._result = result['result']
            node._traceback = result['traceback']
            return report_crash(node,
                                traceback=result['traceback'])
        else:
            return report_crash(node)

    def _clear_task(self, taskid):
        del self._taskresult[taskid]





import numpy as np
from copy import deepcopy
from ..engine import (MapNode, str2bool)
import datetime
import psutil
from ... import logging
logger = logging.getLogger('workflow')

class ResourceMultiProcPlugin(MultiProcPlugin):

    def __init__(self, plugin_args=None):
        super(ResourceMultiProcPlugin, self).__init__(plugin_args=plugin_args)
        self.plugin_args = plugin_args

    def _send_procs_to_workers(self, updatehash=False, graph=None):
        """ Sends jobs to workers when system resources are available.
            Check memory (mb) and cores usage before running jobs.
        """
        executing_now = []
        processors = cpu_count()
        memory = psutil.virtual_memory()
        memory = memory.total / (1024*1024)
        if self.plugin_args:
            if 'n_procs' in self.plugin_args:
                processors = self.plugin_args['n_procs']
            if 'memory' in self.plugin_args:
                memory = self.plugin_args['memory']

        # Check to see if a job is available
        jobids = np.flatnonzero((self.proc_pending == True) & (self.depidx.sum(axis=0) == 0).__array__())

        #check available system resources by summing all threads and memory used
        busy_memory = 0
        busy_processors = 0
        for jobid in jobids:
            busy_memory+= self.procs[jobid]._interface.memory
            busy_processors+= self.procs[jobid]._interface.num_threads
                
        free_memory = memory - busy_memory
        free_processors = processors - busy_processors


        #check all jobs without dependency not run
        jobids = np.flatnonzero((self.proc_done == False) & (self.depidx.sum(axis=0) == 0).__array__())


        #sort jobs ready to run first by memory and then by number of threads
        #The most resource consuming jobs run first
        jobids = sorted(jobids, key=lambda item: (self.procs[item]._interface.memory, self.procs[item]._interface.num_threads))

        logger.debug('Free memory: %d, Free processors: %d', free_memory, free_processors)


        #while have enough memory and processors for first job
        #submit first job on the list
        for jobid in jobids:
            logger.debug('Next Job: %d, memory: %d, threads: %d' %(jobid, self.procs[jobid]._interface.memory, self.procs[jobid]._interface.num_threads))

            if self.procs[jobid]._interface.memory <= free_memory and self.procs[jobid]._interface.num_threads <= free_processors:
                logger.info('Executing: %s ID: %d' %(self.procs[jobid]._id, jobid))
                executing_now.append(self.procs[jobid])
                
                if isinstance(self.procs[jobid], MapNode):
                    try:
                        num_subnodes = self.procs[jobid].num_subnodes()
                    except Exception:
                        self._clean_queue(jobid, graph)
                        self.proc_pending[jobid] = False
                        continue
                    if num_subnodes > 1:
                        submit = self._submit_mapnode(jobid)
                        if not submit:
                            continue

                # change job status in appropriate queues
                self.proc_done[jobid] = True
                self.proc_pending[jobid] = True

                free_memory -= self.procs[jobid]._interface.memory
                free_processors -= self.procs[jobid]._interface.num_threads

                # Send job to task manager and add to pending tasks
                if self._status_callback:
                    self._status_callback(self.procs[jobid], 'start')
                
                if str2bool(self.procs[jobid].config['execution']['local_hash_check']):
                    logger.debug('checking hash locally')
                    try:
                        hash_exists, _, _, _ = self.procs[
                            jobid].hash_exists()
                        logger.debug('Hash exists %s' % str(hash_exists))
                        if (hash_exists and (self.procs[jobid].overwrite == False or (self.procs[jobid].overwrite == None and not self.procs[jobid]._interface.always_run))):
                            self._task_finished_cb(jobid)
                            self._remove_node_dirs()
                            continue
                    except Exception:
                        self._clean_queue(jobid, graph)
                        self.proc_pending[jobid] = False
                        continue
                logger.debug('Finished checking hash')

                if self.procs[jobid].run_without_submitting:
                    logger.debug('Running node %s on master thread' %self.procs[jobid])
                    try:
                        self.procs[jobid].run()
                    except Exception:
                        self._clean_queue(jobid, graph)
                    self._task_finished_cb(jobid)
                    self._remove_node_dirs()

                else:
                    print('submitting', jobid)
                    tid = self._submit_job(deepcopy(self.procs[jobid]), updatehash=updatehash)
                    if tid is None:
                        self.proc_done[jobid] = False
                        self.proc_pending[jobid] = False
                    else:
                        self.pending_tasks.insert(0, (tid, jobid))
            else:
                break

        logger.debug('No jobs waiting to execute')