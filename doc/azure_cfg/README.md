# Azure Deployment Notes
## Firewall Configuration
External access to the database is protected by multiple layers:
* A key component of the interfacing between the Internet and the internal database server is a `pgbouncer` installation that is configured to allow access only for one specific account with read-only database access. In addition, the database connection uses TLS for encryption.
* Firewalling permits access only from Azure-related source IP addresses. For this purpose, Microsoft provides a lists of IPv4 addresses that are updated on a weekly basis.

## Streamlit Application
For the streamlit application, using special Docker image built using git commit ID 36a8e76 (2026-01-06, 23:17).

After building the image we need to upload it to the Azure Container Registry (ACR):
```
$ docker tag streamlit:latest cldemo-<redacted>.azurecr.io/streamlit:v1
$ docker image push cldemo-<redacted>.azurecr.io/streamlit:v1
```

## Actual Deployment
Once this is complete, it is time to launch the application:
```
$ az container create --resource-group myResourceGroup --file deploy-streamlit-apache2.yaml
```
(Internal note: used `.7z` file from int. repo, commit id 780d7cc).
