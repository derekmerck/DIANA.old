import os
from flask import Flask, render_template, Markup, abort
import markdown
import logging
from jinja2 import FileSystemLoader, Environment
import yaml
import argparse


__version__ = "0.1.0"

from flask import Flask
app = Flask(__name__)


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()


def render_md(content, template='strapdown.html.j2'):
    title = config['title']
    content = Markup(markdown.markdown(content, ['markdown.extensions.extra']))
    return render_template(template, **locals())


@app.route('/')
def render_index():
    return render_md(pages['index'])


@app.route('/upload/<study_id>')
def render_upload(study_id):
    if 'upload_'+study_id not in pages.keys():
        abort(404)
    else:
        return render_md(pages['upload_' + study_id])


def prerender(config_file):

    def render_from_template(directory, template_name, **kwargs):
        loader = FileSystemLoader(directory)
        env = Environment(loader=loader)
        template = env.get_template(template_name)
        return template.render(**kwargs)

    with open(config_file) as f:
        config = yaml.load(f)

    pages = {'index': render_from_template('templates', 'index.md.j2', **config)}

    for network, value in config['studies'].iteritems():
        for study, value in value.iteritems():
            logging.debug(value)
            pages['upload_'+value['study_id']] = render_from_template('templates', 'upload.md.j2', **value)

    return config, pages


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    opts = parser.parse_args()

    config, pages = prerender(opts.config)
    app.run(host="0.0.0.0")