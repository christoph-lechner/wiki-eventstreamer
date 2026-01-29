#!/usr/bin/env bash

# C. Lechner, 2026-01-29
#
# Initial processing of downloaded pageviews dump (still in
# .bz-compressed container)

# stop if command returns non-zero exit code
set -e

RAWDUMP=pageviews-20260127-user-dev.bz2

OUTFILE=pageviews-20260127-user-dev.bgzip.gz

cat $RAWDUMP | bunzip2 -f | \
	# Select wikipedia editions of interest
	grep -E "^(de|en).wikipedia" | \
	# Sort text lines
		# -> it is Unicode, but we sort it binary (for efficient information retrieval it is only important that the programs agree on the sort order, the interpretation of the Unicode is then up to the program reporting data to the user)
	env LC_ALL=C sort "--buffer-size=20%" | \
	# Compress data using 'bgzip': Compressed data file is made up of chunks, allowing efficient seeking within the un-compressed data stream
	bgzip --compress-level 9 -f > $OUTFILE
