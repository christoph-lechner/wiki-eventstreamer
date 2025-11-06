# Note: Manual Data Import
CL, 2025-Nov-06

```
(venv) cl@cl-ThinkPad-X390:~/work/wikitest$ date
Do 6. Nov 17:02:08 CET 2025
(venv) cl@cl-ThinkPad-X390:~/work/wikitest$ zcat changes__starting20251105T1630_finaltest.txt.gz | wc

gzip: changes__starting20251105T1630_finaltest.txt.gz: unexpected end of file
3018301 84207108 4038822022
(venv) cl@cl-ThinkPad-X390:~/work/wikitest$ zcat changes__starting20251105T1630_finaltest.txt.gz | tail -n 3018300 > events_in.json 

gzip: changes__starting20251105T1630_finaltest.txt.gz: unexpected end of file
```

```
(venv) cl@cl-ThinkPad-X390:~/work/wikitest$ ./simple_import.py 
..............................
(venv) cl@cl-ThinkPad-X390:~/work/wikitest$ date
Do 6. Nov 17:11:25 CET 2025
```

```
(venv) cl@cl-ThinkPad-X390:~/work/wikitest$ pgcli -h localhost -p 15432 -u postgres -d wikidb
Password for postgres: 
Using local time zone Europe/Berlin (server uses Etc/UTC)
Use `set time zone <TZ>` to override, or set `use_local_timezone = False` in the config
Server: PostgreSQL 14.19 (Debian 14.19-1.pgdg13+1)
Version: 4.3.0
Home: http://pgcli.com
postgres@localhost:wikidb> WITH q AS (
    SELECT
       TO_TIMESTAMP(event_meta_dt, 'YYYY-MM-DD T HH24:MI:SS') AS ts_event_meta_dt,
       event_meta_id,event_meta_domain,event_id,event_wiki,event_user,event_type,event_title
    FROM wtbl)
 SELECT
    DATE(ts_event_meta_dt) AS date, EXTRACT(HOUR FROM ts_event_meta_dt) AS hour,
 
    COUNT(*)
 FROM q
 GROUP BY
    DATE(ts_event_meta_dt),EXTRACT(HOUR FROM ts_event_meta_dt)
 ORDER BY 
    DATE(ts_event_meta_dt),EXTRACT(HOUR FROM ts_event_meta_dt);
+------------+------+--------+
| date       | hour | count  |
|------------+------+--------|
| 2025-11-05 | 15   | 65862  |
| 2025-11-05 | 16   | 144801 |
| 2025-11-05 | 17   | 149786 |
| 2025-11-05 | 18   | 138319 |
| 2025-11-05 | 19   | 157260 |
| 2025-11-05 | 20   | 142806 |
| 2025-11-05 | 21   | 135308 |
| 2025-11-05 | 22   | 115117 |
| 2025-11-05 | 23   | 118470 |
| 2025-11-06 | 0    | 107815 |
| 2025-11-06 | 1    | 107599 |
| 2025-11-06 | 2    | 113100 |
| 2025-11-06 | 3    | 110153 |
| 2025-11-06 | 4    | 101959 |
| 2025-11-06 | 5    | 110908 |
| 2025-11-06 | 6    | 116054 |
| 2025-11-06 | 7    | 114244 |
| 2025-11-06 | 8    | 107812 |
| 2025-11-06 | 9    | 106299 |
| 2025-11-06 | 10   | 103720 |
| 2025-11-06 | 11   | 108881 |
| 2025-11-06 | 12   | 108068 |
| 2025-11-06 | 13   | 129619 |
| 2025-11-06 | 14   | 137277 |
| 2025-11-06 | 15   | 159484 |
| 2025-11-06 | 16   | 7578   |
+------------+------+--------+
SELECT 26
Time: 1.724s (1 second), executed in: 1.715s (1 second)
postgres@localhost:wikidb>
```

Manually removing data outside of the 24-hour range:
```
postgres@localhost:wikidb> SELECT COUNT(*) FROM wtbl WHERE TO_TIMESTAMP(event_meta_dt, 'YYYY-MM-DD T HH24:MI:SS') >= '2025-11-06 16:00:00'
+-------+
| count |
|-------|
| 7578  |
+-------+
SELECT 1
Time: 0.623s
postgres@localhost:wikidb> DELETE FROM wtbl WHERE TO_TIMESTAMP(event_meta_dt, 'YYYY-MM-DD T HH24:MI:SS') >= '2025-11-06 16:00:00'
You're about to run a destructive command.
Do you want to proceed? [y/N]: y
Your call!
DELETE 7578
Time: 1.889s (1 second), executed in: 1.889s (1 second)
postgres@localhost:wikidb> SELECT COUNT(*) FROM wtbl WHERE TO_TIMESTAMP(event_meta_dt, 'YYYY-MM-DD T HH24:MI:SS') < '2025-11-05 16:00:00'
+-------+
| count |
|-------|
| 65862 |
+-------+
SELECT 1
Time: 0.624s
postgres@localhost:wikidb> DELETE FROM wtbl wtbl WHERE TO_TIMESTAMP(event_meta_dt, 'YYYY-MM-DD T HH24:MI:SS') < '2025-11-05 16:00:00';
You're about to run a destructive command.
Do you want to proceed? [y/N]: y
Your call!
DELETE 65862
Time: 1.791s (1 second), executed in: 1.791s (1 second)
postgres@localhost:wikidb>
```
