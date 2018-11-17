# Pykka Snapshot
Implements the Chandy-Lamport snapshot algorithm for saving the state of running Pykka actors.

## The Snapshotable Actor
SnapshotableActor is a subclass of pykka.ThreadingActor that can save its local state, and coordinate with other actors to save a global state to a file. Beacuse of this class heirarchy, any subclasses of SnapshotableActor can save their state and provide all the functionality of ThreadingActor.

## Usage
Key points for using SnapshotableActor are outlined here. You can also download the repo and run `python3 main.py -h` to run examples and reload from a directory.

### Initialization
Any subclasses of SnapshotableActor must call `super().__init__()`. The last step of the initialization routine for this class is to record all of the names of its attributes in a set. Then, when a snapshot is requested, all of the class variables are compared to this set and any new attributes are saved in the snapshot. This way, only attributes of the subclass of SnapshotableActor are saved.

### Messaging
This library introduces a Message object for sending messages between actors. It is important to use this class, as it contains information needed to identify the channel a message is send on when a snapshot is occuring. A sendable form of the Message object can be obtained by calling `Message.as_sendable()`, which returns a dictionary in the form `{ 'obj': <Message> }`.

Any subclasses to SnapshotableActor can implement the `on_receive()` method as they would if they were using the original ThreadingActor class. The only caveat is that `on_receive()` in the subclass must call `super().on_receive(message)` so that the snapshotable actor can handle snapshot requests and marker messages. Note that `SnapshotableActor.on_receive()` returns True if the message was handled in any way by the SnapshotableActor (i.e. the messge contained a request to start a snapshot or it was a marker message).

### Snapshotting
A snapshot can be initiated by sending a message to a SnapshotableActor with the key-value pair `{ 'init_snapshot': True }`. When a snapshot is initiated, the local state of the actor is saved to the `snapshots` attribute with an associated snapshot uuid, and marker messages are sent to all the actor's neighbors. It is possible to piggyback additional data for the subclas with the `init_snapshot` message.

A marker message simply contains the key-value pair `{ 'mark_snapshot': <snapshot_uuid> }`. If an actor receives a marker message with a snapshot uuid it has not seen before, it saves its local state and sends marker messaged to all its neighbors. If the snapshot uuid has been seen before, the channel that marker was received on is marked as closed.

Once all the channels have been marked closed, the snapshot is pickled and written to the snapshot directory.

If a message is received that is not a marker message, it is saved to the channel state for all ongoing snapshots where that channel is open.

### Neighbors
The current implementation requires that all of a SnapshotableActor's neighbors are known when the actor is started. The neighbors list should contain any actor the SnapshotableActor will share a message with at some point in its execution. In the future I aim to make neighbor detection dynamic.

You can use the neighbor list to send a message to a desired neighbor based on their index in the list. You can call `SnapshotableActor.send_messge_to_neighbor(neighbor_index, message_data_dictionary)`. This function builds the necessary Message object with the needed channel information.

A SnapshotableActor can also send a message to itself with the `send_message_to_self(message_data_dictionary)` method. The SnapshotableActor should not have a reference to itself in its list of neighbors.

### Reloading
Reloading is done by passing a snapshot directory to the `reload_snapshot()` method. The format for snapshot directories is a `info.txt` file with actor metadata, and group of pickled snapshot instances. The metadata includes the path to the original SnapshotableActor subclass, the class name, the short id of the actor, and the time the snapshot was written to disk.

## Todo
- Dynamically record neighbors
- Save snapshots as a diff to the previous snapshot

## References
[Pykka](https://github.com/jodal/pykka)

[Chandy-Lamport Snapshotting](https://lamport.azurewebsites.net/pubs/chandy.pdf)

