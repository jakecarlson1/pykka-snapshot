import json
import sys
from importlib.util import spec_from_file_location, module_from_spec

def reload_snapshot(snapshot_dir):
    print(snapshot_dir)
    meta_data = load_meta_data(snapshot_dir)
    print(meta_data)
    reload_from_meta_data(meta_data, snapshot_dir)

def load_meta_data(snapshot_dir):
    data = {}
    with open(snapshot_dir + '/info.txt', 'r') as f:
        start_time = f.readline()
        actor_data = ""
        for l in f.readlines():
            l = l.strip()
            actor_data += l
            if l == "}":
                name, meta_data = parse_meta_data(actor_data)
                data[name] = meta_data
                actor_data = ""

    return data

def parse_meta_data(actor_data):
    split = actor_data.find(": ")
    actor_name = actor_data[:split]
    meta_data = json.loads(actor_data[split+2:])
    
    return actor_name, meta_data

def reload_from_meta_data(meta_data, snapshot_dir):
    loaded_modules = {}
    for actor, meta in meta_data.items():
        class_name = actor.split('-')[0]
        if class_name not in loaded_modules.keys():
            module = load_module(class_name, meta['class_path'])
            loaded_modules[class_name] = module
        module = loaded_modules[class_name]
        cls = eval("module.{}".format(class_name))
        start_and_reload_actor(class_name, snapshot_dir, cls)

def load_module(name, path):
    spec = spec_from_file_location(name, path)
    print(spec)
    module = module_from_spec(spec)
    print(module)
    if name in str(module):
        spec.loader.exec_module(module)

    return module

def start_and_reload_actor(class_name, snapshot_dir, cls):
    alloc = cls.__new__(cls)
    print(alloc)
    super(cls, alloc).__init__()
    print(alloc)
    # TODO: load pickle data into class
    
