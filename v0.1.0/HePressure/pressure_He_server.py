import time
# from uncertainties import ufloat
from threading import Thread, Event

import zmq
import logging
# from threading import Thread

logger = logging.getLogger('HeServer')


class genericAnswer(Exception):
    pass


class customEx(Exception):
    pass


class zmqDevice(object):
    """docstring for ZMQdevice"""

    def __init__(self, zmqcontext=None, port_rep=5556, port_req=5557, *args, **kwargs):
        """reverse portnumbers for server devices!"""
        super(zmqDevice, self).__init__(*args, **kwargs)
        try:

            self.tcp_rep = self.zmq_context.socket(zmq.REP)
            self.tcp_req = self.zmq_context.socket(zmq.REQ)
        except AttributeError:
            self.zmqcontext = zmq.Context()
            self.tcp_rep = self.zmq_context.socket(zmq.REP)
            self.tcp_req = self.zmq_context.socket(zmq.REQ)

        self.tcp_rep.bind(f"tcp://*:{port_rep}")
        self.tcp_req.bind(f"tcp://*:{port_req}")

    def zmqquery_handle(self):
        # signal.signal(signal.SIGINT, signal.SIG_DFL)
        # context = zmq.Context()
        # self.self.socket = context.self.socket(zmq.REP)
        # self.socket.bind("tcp://*:{}".format(5556))

        # handles all currently available messages
        try:
            while True:
                message = self.tcp_rep.recv(flags=zmq.NOBLOCK)
                logger.debug(f'received message: {message}')
                # print(f'received message: {message}')
                try:
                    self.handlefun(message=message)
                except genericAnswer as gen:
                    self.tcp_rep.send_string("{}".format(gen))
        except zmq.Again:
            pass
            # print('nothing to work')

    def zmqquery(self, query):
        # signal.signal(signal.SIGINT, signal.SIG_DFL);
        # context = zmq.Context()
        # self.socket = context.self.socket(zmq.REQ)
        # self.socket.connect("tcp://localhost:5556")
        try:
            self.tcp_req.send_string(f'{query}')
            while True:
                try:
                    message = self.tcp_req.recv(flags=zmq.NOBLOCK)
                    raise customEx
                except zmq.Again:
                    time.sleep(0.2)
                    print('no answer')
        except zmq.ZMQError as e:
            logger.exception('There was an error in the zmq communication!', e)
            return -1
        except customEx:
            return message

    def zmqquery_dict(self, query):
        # signal.signal(signal.SIGINT, signal.SIG_DFL);
        # context = zmq.Context()
        # self.socket = context.self.socket(zmq.REQ)
        # self.socket.connect("tcp://localhost:5556")
        try:
            self.tcp_req.send_string(f'{query}')
            while True:
                try:
                    message = self.tcp_req.recv_json(flags=zmq.NOBLOCK)
                    raise customEx
                except zmq.Again:
                    time.sleep(0.2)
                    print('no answer')
        except zmq.ZMQError as e:
            logger.exception('There was an error in the zmq communication!', e)
            return -1
        except customEx:
            return message

    def handlefun(self, message):
        """to be implemented by specific device"""
        raise NotImplementedError


class zmqServer(zmqDevice):
    """docstring for zmqDealer"""

    def __init__(self, *args, **kwargs):
        super(zmqServer, self).__init__(
            port_rep=5557, port_req=5556, *args, **kwargs)


class Timerthread(Thread):

    def __init__(self, event=None, interval=0.5, *args, **kwargs):
        super(Timerthread, self).__init__(*args, **kwargs)
        self.interval = interval
        if event is None:
            self.stopped = Event()
        else:
            self.stopped = event

    def run(self):
        while not self.stopped.wait(self.interval):
            print("my thread is working hard!")
            self.work()

    def work(self):
        """to be implemented by child class!"""
        raise NotImplementedError


class PressureHandler(zmqServer, Timerthread):
    """docstring for PressureHandler"""

    def __init__(self, event, *args, **kwargs):
        super(PressureHandler, self).__init__(*args, **kwargs)
        self._pressure = 5

    def handlefun(self, message):
        if message == 'p?':
            self.tcp_rep.send_string(f'{self._pressure}')
        else:
            self.tcp_rep.send_string(f'received: {message}')

    def work(self):
        self.zmqquery_handle()


if __name__ == '__main__':
    dev = PressureHandler()
