
# DICOM Analytics and Archive (DIANA)

Derek Merck <derek_merck@brown.edu>
Brown University and Rhode Island Hospital  

<https://github.com/derekmerck/DIANA>


## Overview

Hospital picture archive and communications systems (PACS) are not well suited for "big data" analysis.  It is difficult to identify and extract datasets in bulk, and moreover, high resolution data is often not even stored in the clinical systems.

`DIANA` is a [DICOM][] imaging informatics platform that can be attached to the clinical systems with a very small footprint, and then tuned to support a range of tasks from high-resolution image archival to cohort discovery to radiation dose monitoring.

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


## License

MIT
