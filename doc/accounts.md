For running the various components of the data pipeline, several users were created on the systems:
| on machine running streamreader | on internal machine running DB | remarks | |
| --- | --- | --- | --- |
| dataacq | | user running downloader | `streamreader/config_permissions.md` |
| dataxfer | | user for source side of data transfers | `streamreader/config_permissions.md` |
| | wikidata | user running jobs to transfer stream dumps, owner of stream dump files (read-only for anybody else on the system) | |
| | wikiproj | user performing database loading and running streamlit app | |
