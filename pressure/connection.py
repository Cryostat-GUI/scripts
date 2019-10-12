from pymeasure.instruments.srs import SR830

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import random
from time import sleep
from pymeasure.log import console_log
from pymeasure.display import Plotter
from pymeasure.experiment import Procedure, Results, Worker
from pymeasure.experiment import IntegerParameter, FloatParameter, Parameter


class Measuringproc(Procedure):

    iterations = IntegerParameter('Loop Iterations')
    delay = FloatParameter('Delay Time', units='s', default=0.2)
    # seed = Parameter('Random Seed', default='12345')

    # DATA_COLUMNS = ['Iteration', 'Random Number']

    def startup(self):
        log.info("Setting the seed of the random number generator")
        # random.seed(self.seed)
        self.lockin1 = SR830('GPIB::9')

    def execute(self):
        # log.info("Starting the loop of %d iterations" % self.iterations)
        # while True:
        for _ in self.iterations:
            data = {
                'voltage 1': self.lockin1.x,
                'voltage 2': self.lockin1.y
            }
            self.emit('results', data)
            log.debug("Emitting results: %s" % data)
            sleep(self.delay)
            if self.should_stop():
                log.warning("Caught the stop flag in the procedure")
                break


if __name__ == "__main__":
    console_log(log)

    log.info("Constructing a RandomProcedure")
    procedure = Measuringproc()
    procedure.iterations = 10000

    data_filename = 'measured.csv'
    log.info("Constructing the Results with a data file: %s" % data_filename)
    results = Results(procedure, data_filename)

    log.info("Constructing the Plotter")
    plotter = Plotter(results)
    plotter.start()
    log.info("Started the Plotter")

    log.info("Constructing the Worker")
    worker = Worker(results)
    worker.start()
    log.info("Started the Worker")

    log.info("Joining with the worker in at most 1 hr")
    # worker.join(timeout=3600) # wait at most 1 hr (3600 sec)
    log.info("Finished the measurement")
