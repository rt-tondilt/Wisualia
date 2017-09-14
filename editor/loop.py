# This file contains the main generator loop.

import subprocess
import os
from time import perf_counter as get_time

import mypy.api
from gi.repository import GLib
import state
from state import Please
from gui import input_buffer, output_buffer, set_status_bar_text, drawing_area, scale
from worker import Worker, InitSuccess, Success, Failure, CompileRequest, DrawRequest
from dir_tools import get_dir


os.environ['MYPYPATH'] = get_dir('library')
CB_TIME = 10
FRAME_TIME = 40

# A Loop object, that takes a generator and calls it repeatedly.
# If generator yields N then the generator will be called again after N ms.
# Yielding None pauses the loop until .start() is called.
class Loop(object):
    def __init__(self, generator):
        self.generator = generator()
        self.callback_time = None #type: Optional[int]
    def start(self):
        if self.callback_time == None:
            self.run()
    # PRIVATE METHOD
    def run(self):
        new_callback_time = next(self.generator)
        if new_callback_time != self.callback_time:
            self.callback_time = new_callback_time
            if self.callback_time != None:
                GLib.timeout_add(self.callback_time, self.run)
            return False
        return True

# This exception is raised inside subgenerators of main_task() to
# kill the engine.
class FailureException(Exception):
    def __init__(self, error: str) -> None:
        self.error = error

# Usage:
# yield from yield_from_while(generator, lamda: x>3)
def yield_from_while(generator, condition):
    while condition():
        try:
            y = next(generator)
        except StopIteration as e:
            raise e
        yield y

def main_task():
    while True:
        while state.engine == Please.Idle:
            print('IDELE')
            yield None
        worker = Worker()
        try:
            while True:
                if state.compile_needed:
                    state.compile_needed = False
                    # wait until worker is ready
                    for i in range(10):
                        if not worker.is_working():
                            break
                        yield CB_TIME
                    else: # tired of waiting
                        worker = Worker() # kill and replace

                    yield from yield_from_while(compile_task(worker),
                        lambda: state.engine == Please.Run)
                    if state.engine != Please.Run:
                        raise FailureException('Programm aborted.')

                else:
                    yield from yield_from_while(show_task(worker),
                        lambda: state.engine == Please.Run and not state.compile_needed)
                    if state.engine != Please.Run:
                        raise FailureException('Programm aborted.')
        except FailureException as e:
            output_buffer.set_text(e.error)
        del worker
        set_status_bar_text('No programm running.')
        if state.engine == Please.Restart:
            state.engine = Please.Run
        else:
            state.engine = Please.Idle

state.loop = Loop(main_task)

def compile_task(worker):
    print('COMPILE')
    set_status_bar_text('Programm starting.')
    if state.file_name is None:
        raise FailureException('File name missing.')

    code = input_buffer.get_text(input_buffer.get_start_iter(), input_buffer.get_end_iter(), True)

    worker.send(CompileRequest(code, state.file_name))
    response = worker.recv()
    while response == None:
        print('karju')
        yield CB_TIME
        response = worker.recv()

    if isinstance(response, Failure):
        raise FailureException(response.error)

    assert isinstance(response, InitSuccess)
    output_buffer.set_text('')
    set_status_bar_text('Programm running.')

def show_task(worker):
    while True:
        print('show_task, s')
        if state.playing:
            yield from play_task(worker)
        else:
            yield from update_task(worker)
            if not state.playing:
                yield None

def play_task(worker):
    target_time = get_time()
    while state.playing:
        ut = update_task(worker, target_time)
        yield from ut
        scale.set_value(round(scale.get_value()+ FRAME_TIME /1000, 2))
        target_time = get_time() + FRAME_TIME/1000
        if scale.get_value() >= 10:
            state.play(None)


def update_task(worker, target_time = 0):
    successful_response = None
    print('update_task')
    worker.send(state.request)
    while True:
        response = worker.recv()
        if isinstance(response, Failure):
            print('VIGA<', response.error, '>VIGA')
            state.playing = False
            raise FailureException(response.error)
        elif isinstance(response, Success):
            successful_response = response
            break
        yield CB_TIME
    while True:
        current_time = get_time()
        if target_time < current_time:
            state.buffer_surface = successful_response.data.get_surface() #type: ignore
            output_buffer.set_text(successful_response.result)
            drawing_area.queue_draw()
            return
        yield CB_TIME
