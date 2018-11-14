import json
import importlib.util

def reload_snapshot(snapshot_dir):
    print(snapshot_dir)
    meta_data = load_meta_data(snapshot_dir)
    print(meta_data)

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

