import asyncio
import random
from multiprocessing import Pipe
from select import select

# Rather than implement P2P from scratch and have to worry about encoding and decoding golang gobs,
# This class will serve as a proxy to a separate microservice that handles P2P message sending and receiving.
# That service will be an implementation of https://github.com/WhoSoup/factom-p2p


class P2PProxy:

    def __init__(self):
        self.inbox_pipe_r, self.inbox_pipe_w = Pipe(duplex=False)
        self.outbox_pipe_r, self.outbox_pipe_w = Pipe(duplex=False)
        self.stop_pipe_r, self.stop_pipe_w = Pipe(duplex=False)

    async def start(self):
        await asyncio.gather(self.run())

    async def run(self):

        while True:
            ready, _, _ = select([self.inbox_pipe_r, self.outbox_pipe_r, self.stop_pipe_r], [], [])
            which = random.choice(ready)
            if which == self.inbox_pipe_r:
                self.inbox_pipe_r.recv()
                print('Received value from inbox')
            elif which == self.outbox_pipe_r:
                self.outbox_pipe_r.recv()
                print('Received value from outbox')
                # Send out to queue for P2P service
            elif which == self.stop_pipe_r:
                self.stop_pipe_r.recv()
                print('Received stop signal')
                return

    def stop(self) -> None:
        """
        Sends a signal down the stop pipe to end the processing of messages
        :return: None
        """
        self.stop_pipe_w.send(0)

    def send(self, message) -> None:
        """
        Enqueue a given message to the P2PProxy's outbox to be sent to the P2P service for fanout
        :return: None
        """
        self.outbox_pipe_w.send(message)

    def receive(self):
        """
        Dequeue a message from the P2P Service and dispatch it to the proper internal application queue to be processed
        :return: None
        """
        pass
