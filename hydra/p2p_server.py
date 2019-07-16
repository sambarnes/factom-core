import base64
import bottle
import sys
import factom_core.messages

"""
A quick and hacky tool to listen for p2p messages forwarded from a factomd node

Place the following snippet at this line of Who's p2p package: https://github.com/WhoSoup/factom-p2p/blob/master/peer.go#L243


if msg.IsApplicationMessage() {
    go func() {
        forwardedMessageBody, _ := json.Marshal(map[string]string{
            "payload": base64.StdEncoding.EncodeToString(msg.Payload),
        })
        resp, _ := http.Post("http://localhost:8000", "application/json", bytes.NewBuffer(forwardedMessageBody))
        if err != nil {
            // handle error
        }
        time.Sleep(time.Millisecond * 50)
        if resp != nil {
            _ = resp.Body.Close()
        }
    }()
}


Then rebuild and run his branch: https://github.com/WhoSoup/factomd/tree/FACTOMIZE_new_p2p
"""

bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024
app = bottle.default_app()


@bottle.hook("before_request")
def strip_path():
    """Strip trailing '/' on all requests. '/foo' and /foo/' are two unique endpoints in bottle"""
    bottle.request.environ["PATH_INFO"] = bottle.request.environ["PATH_INFO"].rstrip(
        "/"
    )


@bottle.get("/health")
def health_check():
    return {"data": "Healthy!"}


@bottle.post("/")
def receive():
    """Receive a forwarded p2p message"""
    req = bottle.request
    payload = base64.b64decode(req.json.get("payload").encode())
    msg = factom_core.messages.unmarshal_message(raw=payload)
    msg_filter = {
        factom_core.messages.DirectoryBlockState.TYPE,
        # factom_core.messages.DirectoryBlockSignature.TYPE,
        # factom_core.messages.EndOfMinute.TYPE,
    }
    if msg.TYPE in msg_filter:
        print(msg.__class__.__name__, msg.directory_block.header.height)
    return


def run():
    print("Starting Hacky P2P Server (localhost:8001)...")
    try:
        bottle.run(host="localhost", port=8001, quiet=True)
    except (KeyboardInterrupt, SystemExit):
        sys.exit()


if __name__ == "__main__":
    run()
