# Agent class: hierarchy, messaging and treading
from threading import Thread, Event
from datetime import datetime


class Agent(Thread):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.composition = None
        self.details = []
        # self.thread = None
        self.started = Event()
        self.do_stop = Event()
        self.do_abort = Event()

    # def set_parent(self, parent):
    #     self.parent = parent

    def add_detail(self, detail):
        self.details.append(detail)
        detail.composition = self
        self.msg("Added detail {}".format(detail.name))

    def full_name(self):
        if self.composition is None:
            return self.name
        else:
            return self.composition.full_name() + '.' + self.name

    def fatal(self, msg):
        self.msg("FATAL!!! "+msg)
        exit()

    def warn(self, msg):
        self.msg("WARNING: "+msg)

    def err(self, msg):
        self.msg("ERROR: "+msg)

    def msg(self, msg):
        if self.composition is None:
            print("{0}> {1}: {2}".format(datetime.today().time(), self.name, msg))
        else:
            self.composition.__msg("{0}: {1}".format(self.name, msg))

    def __msg(self, msg):
        if self.composition is None:
            print("{0}> {1}: {2}".format(datetime.today().time(), self.name, msg))
        else:
            self.composition.__msg("{0}.{1}".format(self.name, msg))

    # if there is dependency in starting details you SHOULD deal with the dependency here!!!
    def process_start(self):
        for detail in self.details: detail.start(blocking=True)

    # This SHOULD be finished when everything is done or by self.do_stop event!!!
    def process_body(self):
        self.do_stop.wait()

    # if there is dependency in stopping details you SHOULD deal with the dependency here!!!
    def process_finish(self):
        if self.do_abort.is_set():
            for detail in self.details: detail.abort(blocking=True)
        else:
            for detail in self.details: detail.stop(blocking=True)

    # you should not have any reason to redefine this
    def run(self):
        self.process_start()
        self.msg("Process is started")
        self.started.set()
        self.process_body()
        self.msg("Finishing Process")
        self.process_finish()
        self.msg("Process is stopped")

    # you should not have any reason to redefine this
    def start(self, blocking=True):  # you will not be able to start it twice!!!
        self.msg("Starting process")
        if self.is_alive():
            self.msg("WARNING: already started")
        else:
            Thread.start(self)
        if blocking: self._wait_started()

    # you should not have any reason to redefine this
    def wait_started(self):
        self.msg("Waiting for started")
        self._wait_started()

    # you don't have to have any reason to redefine this
    def _wait_started(self):
        self.started.wait()

    # you should not have any reason to redefine this
    def stop(self, blocking=True):   # you will not be able to start it again!!!
        self.msg("Stopping process")
        if not self.is_alive():
            self.msg("WARNING: already stopped or not started")
        else:
            self.do_stop.set()
        if blocking: self._wait_stopped()

    # you don't have to have any reason to redefine this
    def abort(self, blocking=True):
        self.msg("Aborting process")
        if not self.is_alive():
            self.msg("WARNING: already stopped or not started")
        else:
            self.do_abort.set()
            self.do_stop.set()
        if blocking: self._wait_stopped()

    # you should not have any reason to redefine this
    def wait_stopped(self):
        self.msg("Waiting for stopped")
        self._wait_stopped()

    # you don't have to have any reason to redefine this
    def _wait_stopped(self):
        if self.is_alive(): self.join()


if __name__ == '__main__':
    a1 = Agent("a1")
    a2 = Agent("a2")
    aa = Agent("aa")
    aa.add_detail(a1)
    aa.add_detail(a2)

    aa.start(blocking=False)
    aa.wait_started()
    aa.stop(blocking=False)
    aa.wait_stopped()
    aa.msg("Is over")
