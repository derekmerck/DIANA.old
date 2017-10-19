import os
from flask import Flask, render_template, Markup
from flask_restplus import Resource, Api, reqparse, fields
import markdown
import logging
import random
from datetime import datetime, timedelta
from GUIDMint import GUIDMint

__version__ = "0.2.0"


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

app = Flask(__name__)
api = Api(app, version=__version__, title='GUIDMint API',
    description='GUIDMint API', doc='/doc/')

@app.route('/')
def index():
    content = read('README.md')
    content = content + "\n\n" + "Mint version: {0} | API version: {1}".format(mint.__version__, __version__)
    content = Markup(markdown.markdown(content, ['markdown.extensions.extra']))
    return render_template('index.html', **locals())


class Info(Resource):
    def get(self):
        res = {'version':
                   {'mint': mint.__version__,
                    'api': __version__}}

        return res

@api.route('/pseudo_id')
class PseudoID(Resource):

    pseudo_id_fields = api.model('pseudo_id', {
        'guid': fields.String,
        'name': fields.String,
        'gender': fields.String,
        'dob': fields.String
    })

    parser = reqparse.RequestParser()
    parser.add_argument('name', help='Subject name or other id (req\'d)', required=True)
    parser.add_argument('gender', help='Subject gender (M, F, U) (opt)', choices=('M', 'F', 'U'), default='U')
    parser.add_argument('dob', help='Date of birth (%Y-%m-%d) (opt)')
    parser.add_argument('age', help='Age (int) (opt)', type=int)

    @api.marshal_with(pseudo_id_fields)
    @api.expect(parser)
    def get(self):

        args = self.parser.parse_args()

        name = args.get('name')
        gender = args.get('gender')
        dob = args.get('dob')
        age = args.get('age')

        random.seed('name')
        if not dob and not age:
            age = random.randint(19,65)

        if not dob and age:
            ddob = datetime.now()-timedelta(days=age*365.25)
            dob = str(ddob.date())

        v = "|".join([name, dob, gender])

        g = mint.mint_guid(v)

        res = {'guid': g, 'gender': gender}

        d = None
        if dob or age:
            d = mint.pseudo_dob(g, dob=dob)
            res['dob'] = d

        if gender:
            n = mint.pseudonym(g, gender)
            res['name'] = n

        return res

api.add_resource(Info,       '/info')


@app.route('/ndar')
def get_ndar_guid():
    # TODO: Add NDAR translator
    return "NDAR GUID translator is not implemented yet"


@app.route('/link')
def link_hashes():
    # TODO: Add DB for hash linking
    return "Hash linking is not implemented yet"


import json
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

