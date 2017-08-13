from Gateway import *
import datetime as dt
from hashlib import sha1, md5

logging.basicConfig(level=logging.DEBUG)

import yaml
with open('secrets.yaml') as f:
    credentials = yaml.load(f)

orthanc0 = OrthancGateway(address=credentials['orthanc0_address'])
orthanc1 = OrthancGateway(address=credentials['orthanc1_address'])
pacs_proxy = OrthancGateway(address=credentials['pacs_proxy_address'])
splunk = SplunkGateway(address=credentials['splunk_address'],
                       hec_address=credentials['hec_address'])

from IndexData import UpdatePatientDimensions

UpdatePatientDimensions(orthanc0, splunk)

exit()

# Read accession numbers
fn = "sw_accession_numbers.txt"
with open(fn) as f:
    content = f.readlines()
content = [x.strip() for x in content]

accessions = content
logging.info(accessions)

# Setup anonymizer function
def anonymizer(d):
    r = {'Replace': {
            'PatientName': md5(d['PatientID']),
            'PatientID': md5(d['PatientID']),
            'AccessionNumber': md5(d['AccessionNumber']) },
         'Keep': ['StudyDescription', 'SeriesDescription', 'ContrastBolusAgent', 'StationName']
        }
    return r

remote = 'gepacs'
remote1 = 'shearwave'

for accession_number in accessions[64:]:

    # Retrieve from remote
    pacs_proxy.level = 'studies'
    q = pacs_proxy.QueryRemote(remote, query={'AccessionNumber': accession_number})
    logging.debug(pprint.pformat(q))

    a = pacs_proxy.session.do_get('queries/{0}/answers/0/content?simplify'.format(q['ID']))
    logging.debug(pprint.pformat(a))

    pid = a['PatientID']
    stuid = a['StudyInstanceUID']
    t = sha1(pid + '|' + stuid).hexdigest()
    id = u'-'.join([t[n:n + 8] for n in range(0,40,8)])

    r = pacs_proxy.session.do_post('queries/{0}/answers/0/retrieve'.format(q['ID']), 'DEATHSTAR')
    logging.debug(pprint.pformat(r))

    s = pacs_proxy.GetItem(id)
    logging.debug(pprint.pformat(s))

    # Anonymize it
    t = pacs_proxy.session.do_post('studies/{0}/anonymize'.format(id), anonymizer(s))
    logging.debug(pprint.pformat(t))

    id_anon = t['ID']
    pname_anon = md5(s['PatientID']).hexdigest()

    # Send it to the AIR
    t = pacs_proxy.session.do_post('peers/{0}/store'.format(remote1), id_anon)

    # # Download it locally
    # data = pacs_proxy.session.do_get('studies/{0}/archive'.format(id_anon))
    # fn = '/Users/derek/Desktop/peco/{0}.zip'.format(pname_anon[0:8])
    #
    # f = open(fn, 'wb')
    # f.write(data)
    # f.close()

    # # Delete everything from source
    pacs_proxy.DeleteItem(id)
    pacs_proxy.DeleteItem(id_anon)

# splunk.index_names['series'] = 'air1'
# UpdateSeriesIndex(orthanc1,splunk)

exit()


# # Update the series index
# UpdateSeriesIndex(orthanc0, splunk)

# Update the dose reports

# Use the new  database
splunk.index_names['dose'] = 'dose_reports1'
# UpdateDoseReports(orthanc0, splunk)

# exit()


stuids = """1.3.12.2.1107.5.1.4.66615.30000017053009483632000000055
1.2.840.113619.2.334.3.2299169189.452.1495974787.47
1.2.840.113619.2.182.10168240389283.1496180369.4276613
1.2.840.113619.2.334.3.2299168078.99.1496143275.606
1.2.840.113619.2.334.3.2299168078.99.1496143275.329
1.2.840.113619.2.334.3.2299169189.452.1495974786.926
1.2.840.113619.2.182.10168240389283.1496180459.4276626
1.3.12.2.1107.5.1.4.66615.30000017053009483632000000052
1.2.840.113619.2.334.3.2299168078.99.1496143275.251
1.3.12.2.1107.5.1.4.66457.30000017053011451173800000038
1.2.840.113619.2.278.3.2299136347.540.1496144493.617
1.3.12.2.1107.5.1.4.66615.30000017053009483632000000049
1.2.840.113619.2.334.3.2299168078.99.1496143274.906
1.2.840.113619.2.334.3.2299135835.944.1496139311.52
1.3.12.2.1107.5.1.4.66615.30000017053009483632000000046
1.3.12.2.1107.5.1.4.66457.30000017053011451173800000035
1.3.12.2.1107.5.1.4.66457.30000017053011451173800000032
1.3.12.2.1107.5.1.4.66502.30000017053011365364100000020
1.2.840.113619.2.334.3.2299169189.452.1495974786.726
1.3.12.2.1107.5.1.4.66615.30000017053009483632000000043
1.2.840.113619.2.334.3.2299168078.99.1496143274.794
1.2.840.113619.2.334.3.2299135835.944.1496139310.937
1.2.840.113619.2.334.3.2299168078.99.1496143274.509
1.3.12.2.1107.5.1.4.66615.30000017053009483632000000040
1.2.840.113619.2.334.3.2299169189.452.1495974786.626
1.2.840.113619.2.55.3.2299153724.358.1496138497.53
1.3.12.2.1107.5.1.4.66615.30000017053009483632000000037
1.2.840.113619.2.334.3.2299135835.944.1496139310.804
1.3.12.2.1107.5.1.4.66457.30000017053011451173800000029
1.2.840.113619.2.334.3.2299135835.944.1496139310.689
1.2.840.113619.2.334.3.2299168078.99.1496143274.297
1.3.12.2.1107.5.1.4.66457.30000017053011451173800000026
1.3.12.2.1107.5.1.4.66502.30000017053011365364100000017
1.3.12.2.1107.5.1.4.66615.30000017053009483632000000034
1.2.840.113619.2.334.3.2299168078.99.1496143273.940
1.2.840.113619.2.334.3.2299135835.944.1496139310.608
1.2.840.113619.2.334.3.2299135835.944.1496139310.461
1.2.840.113619.2.182.10168240389283.1496168345.4276360
1.2.840.113619.2.278.3.2299136347.540.1496144493.500
1.2.840.113619.2.182.10168240389399.1496167345.4276205
1.3.12.2.1107.5.1.4.66457.30000017053011451173800000022
1.2.840.113619.2.334.3.2299168078.99.1496143273.832
1.3.12.2.1107.5.1.4.66502.30000017053011365364100000014
1.2.840.113619.2.55.3.2299153724.358.1496138496.977
1.2.840.113619.2.334.3.2299135835.944.1496139309.148"""

stuids = stuids.split('\n')
accessions = []

# StudyInstanceUID="1.3.12.2.1107.5.1.4.66615.30000017053009483632000000055"
for stuid in stuids:
    accessions.append( UpdateRemoteSeriesIndex(pacs_proxy, 'gepacs', splunk, stuid=stuid) )

logging.debug(accessions)
exit()

def UpdateRSIOverRange(year, month, day, n_days, h_incr=3, modality="CT"):

    if h_incr >= 6:
        # It looks like q/r can only handle about a hundred returned answers at a time
        logging.warn("Don't set the hourly increment any higher than 6 -- that is close to the upper limit for a normal day")

    for _day in range(0, n_days):
        d = dt.datetime(year, month, day) + dt.timedelta(_day)
        # logging.debug('date: {year}{month:02d}{day:02d}'.format(year=year, month=d.month, day=d.day))
        for t in range(0, 24, h_incr):
            UpdateRemoteStudyIndex(pacs_proxy, 'gepacs', splunk,
                                    study_date='{year}{month:02d}{day:02d}'.format(year=d.year, month=d.month, day=d.day),
                                    study_time='{start:02d}0000-{end:02d}5959'.format(start=t, end=t + h_incr - 1),
                                    modality=modality
                                   )

# UpdateRSIOverRange(2017, 5, 1, 18, modality="CT")

UpdateRemoteSeriesIndex(pacs_proxy, 'riha', splunk, accession_number='51475723')

# UpdateRemoteSeriesIndex(pacs_proxy, 'gepacs', splunk, accession_number='51432268')