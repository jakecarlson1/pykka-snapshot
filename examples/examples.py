from examples.example_1.incrementor import Incrementor
import inspect
import sys
import time

ACTOR_PROXIES = []

def run_example_1():
    print("Setting up example 1")

    inc1 = Incrementor.start(0.2).proxy()
    inc2 = Incrementor.start(0.8).proxy()
    inc_proxies = [inc1, inc2]

    ACTOR_PROXIES.extend(inc_proxies)

    for i, p in enumerate(inc_proxies):
        proxies_to_send = [ip for j, ip in enumerate(inc_proxies) if j != i]
        p.save_neighbors(proxies_to_send).get()

    print("Starting example 1")

def cleanup():
    print("\nCleaning up example")

    for a in ACTOR_PROXIES:
        print("Stopping", a.id.get())
        a.stop()

    print("Done!")

def get_available_examples():
    return [name for name, obj in inspect.getmembers(sys.modules[__name__])
            if inspect.isfunction(obj) and "run_example_" in name]

def run_example(n):
    example_target = "run_example_{}".format(n)
    if example_target in get_available_examples():
        try:
            exec(example_target + "()")
            while True:
                time.sleep(100)
        except (KeyboardInterrupt):
            cleanup()
    else:
        print("Example not implemented")

