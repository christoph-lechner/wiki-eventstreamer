## Running it
Command line syntax:
```
simple_import.py [-z] filename
```
The file can be gzip-compressed, then the `-z` switch has to be present.

## Description
The script performs the following tasks:
* Load event data in JSON format from file (one line per event) 
* Insert data into temporary table

Next, transformative steps are carried out:
* Generate a MD5 hash containing the following fields (helps to avoid loading data we already have):
 * metadata event id (Note that according to the schema, this field is not required to exist. But typically it is present and it may help to have it included as there can be multiple events with same `request_id` but different ids)
 * metadata event timestamp (is required to be present according to the schema)
 * user name (not required to be present)
 * event ID (not required to be present
* The timestamp was imported as string. It is converted into the appropriate SQL.

Then we deduplicate based on the MD5 hash we have just created. This is needed as sometimes the identical event is sent multiple times.

Finally, a `MERGE` query is executed. The criterion for rows to be skipped is that their MD5 hash is already present in the destination table.
