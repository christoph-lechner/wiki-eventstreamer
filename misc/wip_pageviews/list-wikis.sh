#!/usr/bin/env bash

# C. Lechner, 2026-01-29
#
# List all wikis in downloaded pageviews dump (.bz-compressed container)

# stop if command returns non-zero exit code
set -e

RAWDUMP=pageviews-20260127-user-dev.bz2

cat $RAWDUMP | bunzip2 -f | \
	# awk default delimiter is SPACE
	awk '{print $1}' | \
	env LC_ALL=C sort | \
	uniq -c
