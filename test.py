from functools import partial
import threading
from wsgiref.simple_server import make_server

import pychromecast
import click


#media_file = 'sintel-1024-surround.mp4'
media_file = 'Sintel.2010.720p.mkv'


def media_app(environ, start_response):
    BUFSIZE = 4096

    status = '200 OK'
    headers = [('Content-type', 'video/mp4')]

    start_response(status, headers)
    mf = open(media_file)
    return iter(partial(mf.read, BUFSIZE), '')


@click.group()
@click.option('--host', '-h')
@click.pass_context
def cli(ctx, host):
    assert host, 'autodiscovery not implemeted yet, use --host'
    ctx.obj = {
        'cc': pychromecast.Chromecast(host)
    }
    print 'connected to', ctx.obj['cc']


@cli.command()
@click.argument('file', type=click.Path(exists=True, dir_okay=False))
@click.option('--port', '-p', type=int, default=8000,
              help='Port to use for the media server')
@click.option('--addr', '-a', default=None,
              help='Serevr address to advertise')
@click.pass_obj
def play(obj, file, port, addr):
    cc = obj['cc']
    mc = cc.media_controller
    print 'media controller', mc
    print 'status: ', mc.status

    httpd = make_server('', port, media_app)

    print 'serving media'
    t = threading.Thread(target=httpd.serve_forever)
    t.start()

    # race condition here...
    url = 'http://{}'.format(addr)

    print 'starting playback: {}'.format(url)
    mc.play_media(url, content_type=u'video/mp4')

    print 'joinig...'
    t.join()


if __name__ == '__main__':
    cli()
