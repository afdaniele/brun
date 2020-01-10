import sys
import traceback

from queue import Queue
from threading import Thread, Event, Semaphore
from time import sleep
from collections import defaultdict
from copy import copy

from brun import brlogger
from brun.exceptions import TaskFailureError


class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, name, queue, results, abort, idle, exception_handler, stats):
        Thread.__init__(self)
        self.name = name
        self.queue = queue
        self.results = results
        self.abort = abort
        self.idle = idle
        self.exception_handler = exception_handler
        self.stats = stats
        self.daemon = True
        self.start()

    """Thread work loop calling the function with the params"""

    def run(self):
        #keep running until told to abort
        while not self.abort.is_set():
            try:
                #get a task and raise immediately if none available
                func, args, kwargs = self.queue.get(False)
                self.idle.clear()
            except:
                #no work to do
                self.idle.set()
                sleep(0.5)
                continue

            try:
                #the function may raise
                result = func(*args, **kwargs)
                self.stats.increase('tasks_completed')
                if (result is not None):
                    self.results.put(result)
            except TaskFailureError:
                # get info about the error
                ex_type, ex, tb = sys.exc_info()
                # get partial results and errors
                result = ex.result
                if (result is not None):
                    self.results.put(result)
                #so we move on and handle it in whatever way the caller wanted
                self.stats.increase('tasks_failed')
                self.exception_handler(self.name, ex_type, ex, tb, args, kwargs)
            except:
                ex_type, ex, tb = sys.exc_info()
                self.stats.increase('tasks_failed')
                traceback.print_exception(ex_type, ex, tb, file=sys.stderr)
            finally:
                #task complete no matter what happened
                self.queue.task_done()


class Pool:
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, thread_count, exception_handler):
        #batch mode means block when adding tasks if no threads available to process
        self.queue = Queue()
        self.resultQueue = Queue()
        self.thread_count = thread_count
        self.exception_handler = exception_handler
        self.stats = StatisticsCollector()
        self.aborts = []
        self.idles = []
        self.threads = []

    """Tell my threads to quit"""

    def __del__(self):
        self.abort()

    """Start the threads, or restart them if you've aborted"""

    def run(self, block=False):
        #either wait for them to finish or return false if some arent
        if block:
            while self.alive():
                sleep(1)
        elif self.alive():
            return False

        #go start them
        self.aborts = []
        self.idles = []
        self.threads = []
        for n in range(self.thread_count):
            abort = Event()
            idle = Event()
            self.aborts.append(abort)
            self.idles.append(idle)
            self.threads.append(
                Worker('thread-%d' % n, self.queue, self.resultQueue, abort, idle,
                       self.exception_handler, self.stats))
        return True

    """Add a task to the queue"""

    def enqueue(self, func, *args, **kargs):
        self.queue.put((func, args, kargs))
        self.stats.increase('tasks_total')

    """Wait for completion of all the tasks in the queue"""

    def join(self):
        self.queue.join()

    """Tell each worker that its done working"""

    def abort(self, block=False):
        #tell the threads to stop after they are done with what they are currently doing
        for a in self.aborts:
            a.set()
        # clear the queue
        while not self.queue.empty():
            try:
                _, args, _ = self.queue.get(False)
                cmd, *_ = args
                self.queue.task_done()
                brlogger.info(':brun: Aborted < {0}'.format(' '.join(cmd)))
                self.stats.increase('tasks_aborted')
            except:
                pass
        #wait for them to finish if requested
        while block and self.alive():
            sleep(1)

    """Returns True if any threads are currently running"""

    def alive(self):
        return True in [t.is_alive() for t in self.threads]

    """Returns True if all threads are waiting for work"""

    def idle(self):
        return False not in [i.is_set() for i in self.idles]

    """Returns True if not tasks are left to be completed"""

    def done(self):
        return self.queue.empty()

    """Get the set of results that have been processed, repeatedly call until done"""

    def results(self, wait=0):
        sleep(wait)
        results = []
        try:
            while True:
                #get a result, raises empty exception immediately if none available
                results.append(self.resultQueue.get(False))
                self.resultQueue.task_done()
        except:
            pass
        return results

    """Wait for the pool to complete and return the results as soon as they are ready"""

    def iterate_results(self):
        while not self.done() or not self.idle():
            for r in self.results():
                yield r
        for r in self.results():
            yield r

    def get_stats(self):
        stats = self.stats.get_stats()
        stats['jobs_idle'] = len([1 for i in self.idles if i.is_set()])
        stats['jobs_max'] = len([1 for t in self.threads if t.is_alive()])
        stats['tasks_queued'] = self.queue.qsize()
        return stats


class StatisticsCollector():
    def __init__(self):
        self.lock = Semaphore(1)
        self.data = defaultdict(lambda: 0)

    def set(self, key, value):
        self.lock.acquire()
        self.data[key] = value
        self.lock.release()

    def increase(self, key):
        self.lock.acquire()
        self.data[key] += 1
        self.lock.release()

    def decrease(self, key):
        self.lock.acquire()
        self.data[key] -= 1
        self.lock.release()

    def get_stats(self):
        self.lock.acquire()
        stats = copy(self.data)
        self.lock.release()
        return stats
