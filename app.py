import logging
import os
import time

from datetime import datetime, timedelta
from functools import wraps

import pytz

from flask import Flask, request, Response, send_from_directory
from flask_sqlalchemy import SQLAlchemy


try:
    logging.basicConfig(filename='/var/log/flask/flask.log', level='ERROR')
except IOError:
    # Testing outside of Docker container?
    pass

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'apps')
TRACK_REQUESTS = bool(os.environ.get('TRACK_REQUESTS') and os.environ['TRACK_REQUESTS'] == "True")

app = Flask(__name__)
app.subdomain_matching = True

if os.environ.get('ENVIRONMENT') == 'local':
    app.config['SERVER_NAME'] = 'boxee.test'

    from werkzeug.debug import DebuggedApplication
    app.wsgi_app = DebuggedApplication(app.wsgi_app, True)
    app.debug = True
else:
    app.config['SERVER_NAME'] = 'boxee.tv'

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Here because circ dep
from models import AppRequest


def track_request(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if TRACK_REQUESTS:
            # Figure out real client IP ( because of reverse proxies)
            trusted_proxies = {'127.0.0.1'}
            route = request.access_route + [request.remote_addr]
            remote_addr = next((addr for addr in reversed(route) 
                                if addr not in trusted_proxies), request.remote_addr)

            existing_row = db.session.query(AppRequest) \
                .filter_by(ip=remote_addr, endpoint=str(request.url_rule)) \
                .first()

            now = datetime.utcnow().replace(tzinfo=pytz.utc)

            if existing_row:
                existing_row.timestamp = now
            else:
                new_row = AppRequest(ip=remote_addr, endpoint=str(request.url_rule), timestamp=now)
                db.session.add(new_row)

            db.session.commit()

        return f(*args, **kwargs)
    return wrapped


def authenticate(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not os.environ.get('STATS_USER') or not os.environ.get('STATS_PASS'):
            return Response('No', 401, {})

        auth = request.authorization
        if not auth or not auth.username or not auth.password or \
            not (auth.username == os.environ['STATS_USER'] and auth.password == os.environ['STATS_PASS']):

            return Response('Login', 401, {'WWW-Authenticate': 'Basic'})
        return f(*args, **kwargs)
    return wrapper


@app.errorhandler(404)
def page_not_found(e):
    logging.debug(request)
    return Response('404', status=404, mimetype='text/html')


@app.route('/stats-all', subdomain='app')
@authenticate
def stats_all():
    if not TRACK_REQUESTS:
        return Response('No', 400, {})

    response = ''
    for row in db.session.query(AppRequest).all():
        response = response + ('{} {} {} {}\n'.format(row.id, row.ip, row.endpoint, row.timestamp))
    return Response(response, mimetype='text/plain')


@app.route('/stats-recent-ips', subdomain='app')
@authenticate
def stats_recent_ips():
    if not TRACK_REQUESTS:
        return Response('No', 400, {})

    day_ago = datetime.utcnow().replace(tzinfo=pytz.utc) - timedelta(days=1)

    ips = []
    count = 0

    for row in db.session.query(AppRequest).filter(AppRequest.timestamp >= day_ago):
        ips.append(row.ip)
        count += 1

    ips = list(set(ips))

    response = 'Total IPs: {}\n\n'.format(len(ips))
    response = response + '\n'.join(ips)

    return Response(response, mimetype='text/plain')


@app.route('/', subdomain='app')
@app.route('/', subdomain='api')
@track_request
def status():
    return Response('OK {}'.format(int(time.time())), mimetype='text/plain')


@app.route('/', subdomain='0.ping')
@app.route('/', subdomain='1.ping')
@app.route('/', subdomain='2.ping')
@app.route('/', subdomain='3.ping')
@app.route('/', subdomain='4.ping')
@app.route('/', subdomain='5.ping')
@app.route('/', subdomain='6.ping')
@app.route('/', subdomain='7.ping')
@app.route('/', subdomain='8.ping')
@app.route('/', subdomain='9.ping')
@track_request
def ping():
    return Response('pong', mimetype='text/html')


@app.route('/dlink.dsm380/', subdomain='0.ping')
@app.route('/dlink.dsm380/', subdomain='1.ping')
@app.route('/dlink.dsm380/', subdomain='2.ping')
@app.route('/dlink.dsm380/', subdomain='3.ping')
@app.route('/dlink.dsm380/', subdomain='4.ping')
@app.route('/dlink.dsm380/', subdomain='5.ping')
@app.route('/dlink.dsm380/', subdomain='6.ping')
@app.route('/dlink.dsm380/', subdomain='7.ping')
@app.route('/dlink.dsm380/', subdomain='8.ping')
@app.route('/dlink.dsm380/', subdomain='9.ping')
@track_request
def dlink_ping():
    p = request.args.get('p')
    t = int(time.time())
    xml = "<?xml version='1.0' encoding='ISO-8859-1' ?><ping><cmds ping_version='{}'></cmds><timestamp utc='{}' /></ping>".format(p, t)
    return Response(xml, mimetype='text/xml')


@app.route('/api/login', subdomain='app')
@app.route('/api/login', subdomain='api')
@track_request
def login():
    xml = """<?xml version="1.0" encoding="UTF-8" ?><object type="user" id="666">
    <name>Boxee User</name>
    <short_name>Boxee</short_name>
    <thumb>http://public-nicholasserra.s3.amazonaws.com/web/boxeeskull200.png</thumb>
    <thumb_small>http://public-nicholasserra.s3.amazonaws.com/web/boxeeskull78.png</thumb_small>
    <user_id>666</user_id>
    <user_display_name>Boxee User</user_display_name>
    <user_first_name>Boxee</user_first_name>
    <user_last_name>User</user_last_name>
    <country>US</country>
    <show_movie_library>1</show_movie_library>
</object>"""
    return Response(xml, mimetype='text/xml')


@app.route('/api/get_featured', subdomain='app')
@app.route('/api/get_featured', subdomain='api')
@track_request
def featured():
    messages = []
    for x in range(1, 6):
        messages.append("""
        <message type="featured" score="0" referral="{}" source="boxee">
            <timestamp>{}</timestamp>
            <description>[B][/B]</description>
            <object type="stream_video" id="stv_{}">
                <name>[B][/B]</name>
                <url></url>
                <thumb>http://public-nicholasserra.s3.amazonaws.com/web/boxee/boxee-bg-{}.png</thumb>
                <description></description>
            </object>
            <object type="user" id="nicholasserra">
                <name>nicholasserra</name>
                <short_name>nicholasserra</short_name>
                <thumb>http://public-nicholasserra.s3.amazonaws.com/web/boxeeskull200.png</thumb>
                <thumb_small>http://public-nicholasserra.s3.amazonaws.com/web/boxeeskull78.png</thumb_small>
                <user_id>nicholasserra</user_id>
                <user_display_name>nicholasserra</user_display_name>
                <user_first_name>Nicholas</user_first_name>
                <user_last_name>Serra</user_last_name>
                <show_movie_library>0</show_movie_library>
            </object>
        </message>
        """.format(x, int(time.time()), x, x))
    xml = """<?xml version="1.0" encoding="UTF-8"?><boxeefeed><timestamp>{}</timestamp><last>40</last>{}</boxeefeed>""".format(int(time.time()), ''.join(messages))
    return Response(xml, mimetype='text/xml')


@app.route('/chkupd/dlink.dsm380/<string:one>/<string:two>/<string:three>/<string:four>/<string:five>/<string:six>', subdomain='app')
@app.route('/chkupd/dlink.dsm380/<string:one>/<string:two>/<string:three>/<string:four>/<string:five>/<string:six>', subdomain='api')
@app.route('/ping/dlink.dsm380/<string:one>/<string:two>/<string:three>', subdomain='app')
@app.route('/ping/dlink.dsm380/<string:one>/<string:two>/<string:three>', subdomain='api')
@track_request
def chkupd_ping(*args, **kwargs):
    p = request.args.get('p')
    t = int(time.time())
    xml = "<?xml version='1.0' encoding='ISO-8859-1' ?><ping><cmds ping_version='{}'></cmds><timestamp utc='{}' /></ping>".format(p, t)
    return Response(xml, mimetype='text/xml')


@app.route('/appindex/dlink.dsm380/1.5.1', subdomain='app')
@app.route('/appindex/dlink.dsm380/1.5.1', subdomain='api')
@track_request
def applications():
    xml = """<apps>
    <app>
        <id>nrd</id>
        <version>1.1</version>
        <name>Netflix</name>
        <platform>dlink.dsm380,intel.ce4100</platform>
        <description>Watch as many movies as you want! For $7.99 a month. (Ver 1.1)</description>
        <thumb>http://dir.boxee.tv/apps/netflix/thumb.png</thumb>
        <releasedate>1297711563</releasedate>
        <media>video</media>
        <copyright>Boxee</copyright>
        <email>support@boxee.tv</email>
        <type>native</type>
        <minversion>1.0.4</minversion>
        <repositoryid>tv.boxee</repositoryid>
        <country-allow>us gu vi pr as mp ca</country-allow>
        <signature-dlink.dsm380>hZrXbDTsk4L5T9Cy676h/MsEf5uPCxnD+2frinKS/0bkwdv0NMQHGk/v+lADQuMObUaXR5Wglhg7vpUpUcnAhBavmkjqiTR7NsW3x2qc9KcoqpMxiPRYw4nHyNZXa3C9etvzUMrARTlVOzV+vZt5CY7lC3U4nrkgn5G0sC3Tw1g=</signature-dlink.dsm380>
        <signature-intel.ce4100>hZrXbDTsk4L5T9Cy676h/MsEf5uPCxnD+2frinKS/0bkwdv0NMQHGk/v+lADQuMObUaXR5Wglhg7vpUpUcnAhBavmkjqiTR7NsW3x2qc9KcoqpMxiPRYw4nHyNZXa3C9etvzUMrARTlVOzV+vZt5CY7lC3U4nrkgn5G0sC3Tw1g=</signature-intel.ce4100>
    </app>
</apps>"""
    return Response(xml, mimetype='text/xml')


# TODO dynamic file names
@app.route('/apps/download/nrd-1.1-dlink.dsm380.zip/', subdomain='dir')
@track_request
def netflix():
    return send_from_directory(UPLOAD_FOLDER, 'nrd-1.1-dlink.dsm380.zip', as_attachment=True, attachment_filename='nrd-1.1-dlink.dsm380.zip')
