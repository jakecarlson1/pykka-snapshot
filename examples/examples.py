from examples.example_1 import Incrementor
from pykka import ActorRegistry
from pykka.exceptions import ActorDeadError
import inspect
import sys
import time

from snapshotting import Message

ACTOR_PROXIES = []

def run_example_1(args):
    print("Setting up example 1")
    
    probs = args['send_probs']
    num_incs = len(probs)

    incs = []
    inc_proxies = []
    for i in range(num_incs):
        inc = Incrementor.start(probs[i])
        incs.append(inc)
        inc_proxies.append(inc.proxy())

    ACTOR_PROXIES.extend(inc_proxies)

    for i, p in enumerate(inc_proxies):
        proxies_to_send = [ip for j, ip in enumerate(inc_proxies) if j != i]
        p.save_neighbors(proxies_to_send).get()

    print("Starting example 1")
    start_msg = { "start": True, "logical_clock": 0 }
    start_msg = Message(0, incs[0].proxy().id_short.get(), start_msg).as_sendable()
    incs[0].tell(start_msg)

    time.sleep(1)
    snapshot_msg = { "init_snapshot": True }
    snapshot_msg = Message(0, incs[0].proxy().id_short.get(), snapshot_msg).as_sendable()
    incs[0].tell(snapshot_msg)

def cleanup():
    print("\nCleaning up example")

    ActorRegistry.stop_all()

    # for a in ACTOR_PROXIES:
    #     try:
    #         print("Stopping", a.id.get())
    #         a.stop()
    #     except (ActorDeadError):
    #         print("Dead actor:", a)
    #         continue

    print("Done!")

def get_available_examples():
    return [name for name, obj in inspect.getmembers(sys.modules[__name__])
            if inspect.isfunction(obj) and "run_example_" in name]

def run_example(args):
    # import logging
    # import signal
    # import pykka.debug
    # logging.basicConfig(level=logging.DEBUG)
    # signal.signal(signal.SIGUSR1, pykka.debug.log_thread_tracebacks)
    n = int(args['example'])
    example_target = "run_example_{}".format(n)
    if example_target in get_available_examples():
        try:
            exec(example_target + "(args)")
            while True:
                time.sleep(100)
        except (KeyboardInterrupt):
            cleanup()
    else:
        print("Example not implemented")

