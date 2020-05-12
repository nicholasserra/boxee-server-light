import logging
import os
import time

from flask import Flask, request, Response, send_from_directory


try:
    logging.basicConfig(filename='/var/log/flask/flask.log', level='ERROR')
except IOError:
    # Testing outside of Docker container?
    pass


app = Flask(__name__)
app.subdomain_matching = True
app.config['SERVER_NAME'] = 'boxee.tv'

APPS_FOLDER = os.path.join(os.path.dirname(__file__), 'apps')
UPGRADE_FOLDER = os.path.join(os.path.dirname(__file__), 'version', '1.5.1.23735')


"""
from werkzeug.debug import DebuggedApplication
app.wsgi_app = DebuggedApplication(app.wsgi_app, True)
app.debug = False
"""


@app.errorhandler(404)
def page_not_found(e):
    logging.debug(request)
    return Response('404', status=404, mimetype='text/html')


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
def dlink_ping():
    p = request.args.get('p')
    t = int(time.time())
    xml = "<?xml version='1.0' encoding='ISO-8859-1' ?><ping><cmds ping_version='{}'></cmds><timestamp utc='{}' /></ping>".format(p, t)
    return Response(xml, mimetype='text/xml')


@app.route('/api/login', subdomain='app')
@app.route('/api/login', subdomain='api')
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


@app.route('/chkupd/dlink.dsm380/<string:one>/<string:two>/<string:three>/<string:four>/<string:five>/<string:six>', subdomain='app')
@app.route('/chkupd/dlink.dsm380/<string:one>/<string:two>/<string:three>/<string:four>/<string:five>/<string:six>', subdomain='api')
@app.route('/ping/dlink.dsm380/<string:one>/<string:two>/<string:three>', subdomain='app')
@app.route('/ping/dlink.dsm380/<string:one>/<string:two>/<string:three>', subdomain='api')
def chkupd_ping(*args, **kwargs):
    t = int(time.time())
    xml = "<?xml version='1.0' encoding='ISO-8859-1' ?><ping><cmds ping_version='1.2.3.20490'></cmds><timestamp utc='{}' /><version_update build-num='1.5.1.23735' update-descriptor-path='dl.boxee.tv/version/dlink.dsm380/1.5.1.23735/boxee.iso' update-descriptor-hash='a7be254904a55ea7d87ba3a5c9633952' /></ping>".format(t)
    return Response(xml, mimetype='text/xml')


@app.route('/appindex/dlink.dsm380/1.5.1', subdomain='app')
@app.route('/appindex/dlink.dsm380/1.5.1', subdomain='api')
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
def netflix():
    return send_from_directory(APPS_FOLDER, 'nrd-1.1-dlink.dsm380.zip', as_attachment=True, attachment_filename='nrd-1.1-dlink.dsm380.zip')


# TODO dynamic file names
@app.route('/version/dlink.dsm380/1.5.1.23735/boxee.iso', subdomain='dl')
def upgrade():
    return send_from_directory(UPGRADE_FOLDER, 'boxee.iso', as_attachment=True, attachment_filename='boxee.iso')
