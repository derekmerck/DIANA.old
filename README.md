
# DICOM Analytics and Archive (DIANA)
[![Build Status](https://travis-ci.org/derekmerck/DIANA.svg?branch=master)](https://travis-ci.org/derekmerck/DIANA)

Derek Merck <derek_merck@brown.edu>  
Brown University and Rhode Island Hospital  

<https://github.com/derekmerck/DIANA>


## Overview

Hospital picture archive and communications systems (PACS) are not well suited for "big data" analysis.  It is difficult to identify and extract datasets in bulk, and moreover, high resolution data is often not even stored in the clinical systems.

**DIANA** is a [DICOM][] imaging informatics platform that can be attached to the clinical systems with a very small footprint, and then tuned to support a range of tasks from high-resolution image archival to cohort discovery to radiation dose monitoring.

It is similar to [XNAT][] in providing DICOM services, image data indexing, REST endpoints for scripting, and user access control.  It is dissimilar in that it is not a monolithic codebase, but an amalgamation of free and free and open source (FOSS) systems.  Indeed, XNAT can be setup as a component of DIANA.

[DICOM]: http://dicom.nema.org
[XNAT]:  http://www.xnat.org


## Dependencies

- [Docker][] for service virtualization
- [Ansible][], [pyyaml][], [jinja2][] for service orchestration
- [Orthanc][] for DICOM storage and bridging DICOM to REST
- [Postgresql][] 9.5+ for scalable Orthanc backend
- [Splunk][] 6.6+ for data indexing
- [Python][] 2.7.11+ for scripting

[Docker]:http://www.docker.com
[Orthanc]: https://orthanc.chu.ulg.ac.be
[Splunk]: https://www.splunk.com
[Postgresql]:http://www.postgresql.org
[Orthanc]:http://www.orthanc-server.com
[Python]:http://www.python.org
[pyyaml]:http://pyyaml.org
[jinja2]:http://jinja.pocoo.org
[ansible]:http://www.ansible.com


## Setup

### Quick Start

Setup an image archive and a Splunk index.

```
$ ...
```


## Components


### DIANA-services
Ansible scripts for reproducible configurations

* DICOM image archives and routing (Orthanc)
* data index and forwarding (Splunk)


### DIANA-apps
Splunk apps and dashboards for informatics and data review

* `status` (services introspection)
* [`rad_rx`](/apps/rad_rx) (DICOM SRDR)
* `workload` (hl7)


### DIANA-connect
Python gateway API's for scripting indexing or data transfer jobs.

* `update_index`
* `pacs_crawler`
* `montage_crawler`
* `find_studies` (identify image populations)
* `get_studies` (build secondary image registries)


### muDIANA
Extensions supporting high-throughput microscopy data and image analytics and archive

* Monitoring for Phenix Opera logs
* Read spreadsheets of data properties
* Post-processing including ROI cropping and 3D CLAHE
* Use disk compressed storage b/c of all the zeros
* get_samples Find sample cores in each well, extract ROI on pull



## Use Cases


### DIANA for Mass DICOM Archive

role: `dicom_archive`

1. Create an index role
2. Create a DB role
3. Create n+m DICOM repo roles
   - n archive workers
   - m queues, muxes
4. Create an http reverse proxy role for archive workers
5. Create a bridge role repo/series -> index

6. Install the _dicom-series_ dashboards

Creating the index first allows the system to ship logs directly to the index


### DIANA for PACS Crawling

role: `pacs_crawler`

1. Create an index role
2. Create a DICOM repo role
3. Create a bridge role repo/remote -> index

4. Register the Orthanc repo with the PACS as a valid query source and move target
5. Install the _remote-studies_ dashboards


### DIANA for VPN'd DICOM forwarding

role: `vpn_forwarder`

1. Create a VPN client role
2. Create a DICOM repo role
   - configure as a queue that receives locally and forwards to the VPN

Great for small, low powered devices at remote facilities that need to send images or structured dose reports to a primary archive.  Building on ARM (Raspberry Pi 3) is problematic.


### DIANA for Dose Management

role: `dose_monitor`

1. Create an index role
2. Create a DICOM repo role
3. Create a bridge role repo/dose -> index

4. Point modality dose reports to the dose repo
5. Install the _dose-monitoring_ dashboards


#### Reconciling Missing Data on Dose Reports

Occassionally the EHR will be unavailable to automatically assign accession numbers or protocols as the studies are performed.  For example, we recently lost LifeChart for 4 hours, and ended up with about 40 studies that had absent or hand-input improper accession numbers assigned.  Because the index assumes the accession numbers are correct, this can lead to missing studies in the summary information.

Reconciling this is somewhat complicated, but can be scripted with CopyDICOM.

index = Splunk gateway
dicom_node = Orthanc with structured dose reports
remote_bridge = Orthanc with access to the PACS where the updated accession numbers live


1. Extract the Study Instance UID of the bad reports from Splunk

```
study_ids = index.DoQuery( "index=dose_reports | ..."" )
```

2. Ask the PACS for the updated accession numbers for those StudyInstanceUIDs.
```
for study_id in study_ids:
  accessions.append( remote_bridge.DoRemoteQuery( {"StudyInstanceUID": study_id} ) )
```

3. Modify each report in the DICOM node
```
For study_id, accession_num in zip( study_ids, accessions ):
  dicom_node.modify( {"StudyInstanceUID": study_id}, {"AccessionNumber": accession_num} )
```

4. Drop the bad reports from the indices
```
index.DoQuery( "index=dicom_series | ... | del" )
index.DoQuery( "index=dose_reports | ... | del" )
```

5. Re-index the modified files and update the dose registry
```
index.UpdateSeries( dicom_node )
index.UpdateDoseRegistry( dicom_node )
```


### DIANA for HL7 Dashboards

role: `hl7_consumer`

1. Create an index role
2. Create an FTP forwarder role

3. Install dashboards


## License

MIT
