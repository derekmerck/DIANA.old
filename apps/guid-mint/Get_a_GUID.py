import os
from flask import Flask, request, render_template, Markup
import markdown
from GUIDMint import GUIDMint
import logging
import json

__version__ = "0.2.0"


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()


app = Flask(__name__)


@app.route('/')
def index():
    content = read('README.md')
    content = content + "\n\n" + "Mint version: {0} | API version: {1}".format(mint.__version__, __version__)
    content = Markup(markdown.markdown(content, ['markdown.extensions.extra']))
    return render_template('index.html', **locals())


@app.route('/version')
def version():
    res = {'version':
               {'mint': mint.__version__,
                'api': __version__}}

    return json.dumps(res)


@app.route('/guid')
def get_guid():
    value = request.args.get('value')
    guid = mint.mint_guid(value)

    res = {'guid': guid}
    return json.dumps(res)


@app.route('/pseudonym')
def get_psuedonym():
    guid = request.args.get('guid')
    gender = request.args.get('gender')
    n = mint.pseudonym(guid, gender)

    res = {'name': n}
    return json.dumps(res)


@app.route('/pseudo_dob')
def get_pseudo_dob():
    guid = request.args.get('guid')
    dob = request.args.get('dob')
    d = mint.pseudo_dob(guid, dob)

    res = {'dob': d}
    return json.dumps(res)


@app.route('/pseudo_identity')
def get_pseudo_identity():
    name   = request.args.get('name')
    gender = request.args.get('gender')
    dob    = request.args.get('dob')
    age    = int(request.args.get('age'))
    g,n,d = mint.pseudo_identity(name, gender=gender, dob=dob, age=age)

    res = {'guid': g, 'name': n, 'dob':  d}
    return json.dumps(res)


@app.route('/ndar')
def get_ndar_guid():
    # TODO: Add NDAR translator
    return "NDAR GUID translator is not implemented yet"


@app.route('/link')
def link_hashes():
    # TODO: Add DB for hash linking
    return "Hash linking is not implemented yet"


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("Get-a-GUID")

    mint = GUIDMint()

    # This works nicely with Heroku
    port = int(os.environ.get('PORT', 5000))
    if port is 5000:
        host = None
    else:
        host = '0.0.0.0'

    app.run(host=host, port=port)
