import multiprocessing
import socketserver
import sys
import factom_core.messages

"""
A quick and hacky tool to listen for p2p messages forwarded from a factomd node

Place the following snippet at this line of Who's p2p package: https://github.com/WhoSoup/factom-p2p/blob/master/peer.go#L243


if msg.IsApplicationMessage() {
    go func() {
        conn, err := net.Dial("tcp", "127.0.0.1:8001")
        if err != nil {
            return
        }
        payload := append(msg.Payload, []byte("\n")...)
        _, _ = conn.Write(payload)
    }()
}


Then rebuild and run his branch: https://github.com/WhoSoup/factomd/tree/FACTOMIZE_new_p2p
"""


class P2PServer(socketserver.TCPServer):
    def __init__(
        self,
        inbox: multiprocessing.Queue,
        server_address,
        RequestHandlerClass,
        bind_and_activate=True,
    ):
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)
        self.inbox = inbox


class P2PHandler(socketserver.StreamRequestHandler):
    def handle(self):
        payload = self.rfile.readline().strip()
        msg = factom_core.messages.unmarshal_message(raw=payload)
        self.server.inbox.put(msg)


def run(inbox: multiprocessing.Queue):
    print("Starting Hacky P2P Server (localhost:8001)...")
    server = P2PServer(inbox, ("localhost", 8001), P2PHandler)
    try:
        server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
