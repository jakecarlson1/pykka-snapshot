from snapshotting import Message
from importlib.util import spec_from_file_location, module_from_spec
import json
import pickle
import sys

def reload_snapshot(snapshot_dir):
    meta_data = load_meta_data(snapshot_dir)
    return reload_from_meta_data(meta_data, snapshot_dir)

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
    loaded_actors = {}
    for actor_string, meta in meta_data.items():
        class_name = actor_string.split('-')[0]
        if class_name not in loaded_modules.keys():
            module = load_module(class_name, meta['class_path'])
            loaded_modules[class_name] = module

        module = loaded_modules[class_name]
        cls = eval("module.{}".format(class_name))
        actor, snapshot = start_and_reload_actor(actor_string, snapshot_dir, cls)
        loaded_actors[actor_string] = {
            'actor': actor,
            'snapshot': snapshot
        }
    
    restore_channels(loaded_actors)

    restore_neighbors(loaded_actors)

    return [d['actor']._restart() for d in loaded_actors.values()]

def load_module(name, path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    
    if name in str(module):
        spec.loader.exec_module(module)

    return module

def start_and_reload_actor(actor_string, snapshot_dir, cls):
    actor = cls.__new__(cls)
    super(cls, actor).__init__()

    snapshot = {}
    with open("{}/{}.pkl".format(snapshot_dir, actor_string), 'rb') as f:
        snapshot = pickle.load(f)
    
    for k, v in snapshot.saved_actor_state.items():
        setattr(actor, k, v)

    return actor, snapshot

def restore_channels(actors):
    old_to_new_id_short = {a.split('-')[1]:d['actor'].id_short 
                           for a,d in actors.items()}
    print(old_to_new_id_short)
    for a, d in actors.items():
        queue = build_queue_from_channels_for_actor(a, actors, old_to_new_id_short)
        actors[a]['queue'] = queue
    for a, d in actors.items():
        ref = d['actor'].actor_ref
        for m in d['queue']:
            ref.tell(m.as_sendable())

def build_queue_from_channels_for_actor(actor_string, actors, id_short_map):
    queue = []
    channels = [i for i in actors[actor_string]['snapshot'].saved_channels.items()]
    curr_idx = [0 for _ in range(len(channels))]
    rr_idx = 0
    channel_lengths = [len(c[1].messages) for c in channels]
    while sum([curr_idx[i] < channel_lengths[i] 
               for i in range(len(channel_lengths))]) > 0:
        if curr_idx[rr_idx] < channel_lengths[rr_idx]:
            queue.append(channels[rr_idx][1].messages[curr_idx[rr_idx]])
            curr_idx[rr_idx] += 1

        rr_idx += 1
        rr_idx %= len(channel_lengths)

    remapped_queue = []
    for m in queue:
        remapped_queue.append(Message(
            id_short_map[m.sender], id_short_map[m.receiver], m.data
        ))
        
    return remapped_queue

def restore_neighbors(actors):
    pass

