#!/bin/bash

if [[ $EUID -ne 0 ]]; then
	echo "This script must be run with superuser privileges." >&2
	exit 1
fi
# exit 0

# equivalent to manual steps in streamreader/config_permissions.md
# (git commit id 82404aa, Nov 18, 2025)
useradd -m -c "user for data acquisition" -s /bin/bash dataacq
useradd -m -c "user for data transfer" -s /bin/bash dataxfer
groupadd wikidata
adduser dataacq wikidata
adduser dataxfer wikidata
id dataacq
id dataxfer
