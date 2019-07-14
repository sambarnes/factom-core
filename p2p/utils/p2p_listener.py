import base64
import bottle
import factom_core.messages

# A quick and hacky tool to run and listen for p2p messages forwarded from a factomd node


@bottle.hook('before_request')
def strip_path():
    """Strip trailing '/' on all requests. '/foo' and /foo/' are two unique endpoints in bottle"""
    bottle.request.environ['PATH_INFO'] = bottle.request.environ['PATH_INFO'].rstrip('/')


@bottle.get('/health')
def health_check():
    return {'data': 'Healthy!'}


bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024


@bottle.post('/')
def receive():
    """Receive a forwarded p2p message"""
    req = bottle.request
    payload = base64.b64decode(req.json.get('payload').encode())
    msg = factom_core.messages.unmarshal_message(raw=payload)
    print(msg)
    return


# Entry point ONLY when run locally. The docker setup uses gunicorn and this block will not be executed.
if __name__ == '__main__':
    bottle.run(host='localhost', port=8000)

app = bottle.default_app()
