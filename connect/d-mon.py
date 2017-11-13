#! /usr/bin/python

import requests
import logging
from hashlib import md5
from pprint import pformat
import json
import argparse
import time
import yaml


def handle_study(s, task):

    url = "{0}/studies/{1}/shared-tags?simplify".format(task.source, s)
    r = requests.get(url, auth=task.auth)
    info = r.json()
    # logging.debug(pformat(info))

    t = None  # Deidentified study id, s is presumed to have PHI

    if task.anonymize:

        deidentified = False
        if info.get("PatientIdentityRemoved")=="Yes" or \
           info["PatientName"].startswith(task.anon_prefix):

            deidentified = True
            logging.debug("{0} is already deidentified".format(info['PatientName']))
            t = s
            s = None

        if not deidentified:
            # Deidentify
            anon = anonymizer(info, task.anon_prefix)
            logging.debug(json.dumps(anon))
            url = "{0}/studies/{1}/anonymize".format(task.source, s)
            r = requests.post(url, data=json.dumps(anon), auth=task.auth, headers={'content-type': 'application/json'})

            # Get anon id back
            info = r.json()
            logging.debug(pformat(info))
            t = info['ID']

    if task.dest:
        if task.anonymize:
            data = t
        else:
            data = s
        url = "{0}/peers/{1}/store".format(task.source, task.dest)
        r = requests.post(url, data=data, auth=task.auth, headers={'content-type': 'application/text'})

    if task.delete_anon and t:
        # Delete deidentified data from source
        url = "{0}/studies/{1}".format(task.source, t)
        r = requests.delete(url, auth=task.auth)

    if task.delete_phi and s:
        # Delete PHI data from source
        url = "{0}/studies/{1}".format(task.source, s)
        r = requests.delete(url, auth=task.auth)


def continous():

    for task in tasks:

        # logging.debug(task)

        # Deidentify and move a few _recent_ studies to dest
        url = "{0}/changes".format(task.source)
        r = requests.get(url,
                         params = {'since': task.current,
                                 'limit': 100},
                         auth=task.auth)
        q = r.json()
        # logging.debug(pformat(q))

        for change in q['Changes']:
            if change['ChangeType'] == 'StableStudy':
                handle_study(change['ID'], task)

        task.current = q['Last']

        if q['Done']:
            logging.debug('Everything has been processed up to {0}: Waiting...'.format(task.current))


def one_shot():

    logging.debug('Starting one shot processing')

    for task in tasks:

        # Deidentify and move _all_ studies to dest
        url = "{0}/studies".format(task.source)
        r = requests.get(url, auth=task.auth)
        studies = r.json()

        logging.debug(studies)

        for s in studies:
            handle_study(s, task)

# Simple anonymization function
def anonymizer(d, anon_prefix):
    r = {'Replace': {
            'PatientName':      anon_prefix + md5(d['PatientID']).hexdigest()[0:8],
            'PatientID':        md5(d['PatientID']).hexdigest(),
            'AccessionNumber':  md5(d['AccessionNumber']).hexdigest()
         },
         'Keep': ['StudyDescription', 'SeriesDescription', 'StudyDate'],
         # Need 'Force' to change PatientID
         'Force': True
        }
    return r


def parse_config(fn):

    tasks = []
    with open(fn) as f:
        config = yaml.load(f)
        for task in config['tasks']:
            tasks.append(Task(task))

    return tasks, config.get('delay')


def parse_args():

    parser = argparse.ArgumentParser(prog='d-mon')

    # In config, multiple tasks may be defined with these params
    parser.add_argument('--source',      help='http://host:port/api')
    parser.add_argument('--user')
    parser.add_argument('--password')
    parser.add_argument('--dest',        help='Orthanc peer name in source', default=None)
    parser.add_argument('--anonymize',   help='True/False (False)', default=None, action='store_true')
    parser.add_argument('--anon_prefix', help="If anonymizing, optional prefix for new name (None)", default=None)
    parser.add_argument('--delete_phi',  help='True/False (False)', action='store_true')
    parser.add_argument('--delete_anon', help='True/False (False)', action='store_true')

    # Only one delay and config allowed
    parser.add_argument('--delay',       help='-1 for one shot, otherwise seconds (2)', default=2)
    parser.add_argument('--config',      help='YML config file for multiple tasks (None)', default=None)

    return parser.parse_args()


class Task(object):

    def __init__(self, d):
        self.source = d.get('source')
        self.auth =  (d.get('user', 'Orthanc'),
                      d.get('password'))
        self.dest =   d.get('dest')
        self.anonymize = d.get('anonymize')
        self.anon_prefix = d.get('anon_prefix')
        self.delete_phi = d.get('delete_phi')
        self.delete_anon = d.get('delete_anon')
        self.current = 0

    def __str__(self):
        return str( self.__dict__ )


if __name__=="__main__":

    logging.basicConfig(level=logging.DEBUG)

    opts = parse_args()

    # If a config file is given, register multiple tasks
    if opts.config:
        # Need to parse out multiple tasks

        tasks, c_delay = parse_config(opts.config)
        if c_delay:
            opts.delay = c_delay

    # Otherwise there is only one task to register
    else:
        tasks = [Task(opts)]

    for task in tasks:
        logging.debug(task)

    if opts.delay<0:
        # Single shot update
        one_shot()

    else:
        # Loop and monitor changes
        while True:
            continous()
            time.sleep(opts.delay)