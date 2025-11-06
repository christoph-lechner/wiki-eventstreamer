## top wikis
```
postgres@localhost:postgres> SELECT event_wiki,COUNT(*) FROM wtbl GROUP BY event_wiki ORDER BY COUNT(*) DESC LIMIT 10;
+--------------+---------+
| event_wiki   | count   |
|--------------+---------|
| commonswiki  | 1216270 |
| wikidatawiki | 579388  |
| enwiki       | 327960  |
| cewiki       | 89457   |
| ruwikinews   | 69451   |
| frwiki       | 45425   |
| ckbwiki      | 41283   |
| ruwiki       | 38411   |
| dewiki       | 33899   |
| ukwiki       | 31065   |
+--------------+---------+
```

## types of events
```
postgres@localhost:postgres> SELECT event_type,COUNT(*) FROM wtbl GROUP BY event_type ORDER BY COUNT(*) DESC;
+------------+---------+
| event_type | count   |
|------------+---------|
| edit       | 1507772 |
| categorize | 1149944 |
| log        | 211157  |
| new        | 75872   |
| <null>     | 114     |
+------------+---------+
```

## temporal edit distribution for dewiki
```
WITH q AS (
   SELECT
      TO_TIMESTAMP(event_meta_dt, 'YYYY-MM-DD T HH24:MI:SS') AS ts_event_meta_dt,
      event_meta_id,event_meta_domain,event_id,event_wiki,event_user,event_type
   FROM wtbl
   WHERE
      event_type='edit' AND event_wiki='dewiki')
SELECT
   DATE(ts_event_meta_dt) AS date, EXTRACT(HOUR FROM ts_event_meta_dt) AS hour,
   COUNT(*)
FROM q
GROUP BY
   DATE(ts_event_meta_dt),EXTRACT(HOUR FROM ts_event_meta_dt)
ORDER BY
   DATE(ts_event_meta_dt),EXTRACT(HOUR FROM ts_event_meta_dt);
+------------+------+-------+
| date       | hour | count |
|------------+------+-------|
| 2025-11-05 | 16   | 1300  |
| 2025-11-05 | 17   | 1314  |
| 2025-11-05 | 18   | 1371  |
| 2025-11-05 | 19   | 1327  |
| 2025-11-05 | 20   | 1204  |
| 2025-11-05 | 21   | 1028  |
| 2025-11-05 | 22   | 908   |
| 2025-11-05 | 23   | 645   |
| 2025-11-06 | 0    | 423   |
| 2025-11-06 | 1    | 304   |
| 2025-11-06 | 2    | 280   |
| 2025-11-06 | 3    | 483   |
| 2025-11-06 | 4    | 433   |
| 2025-11-06 | 5    | 779   |
| 2025-11-06 | 6    | 971   |
| 2025-11-06 | 7    | 1309  |
| 2025-11-06 | 8    | 1285  |
| 2025-11-06 | 9    | 1126  |
| 2025-11-06 | 10   | 1408  |
| 2025-11-06 | 11   | 1187  |
| 2025-11-06 | 12   | 1038  |
| 2025-11-06 | 13   | 1295  |
| 2025-11-06 | 14   | 1394  |
| 2025-11-06 | 15   | 1344  |
+------------+------+-------+
```

## top pages
```
WITH q AS (
   SELECT
      TO_TIMESTAMP(event_meta_dt, 'YYYY-MM-DD T HH24:MI:SS') AS ts_event_meta_dt,
      event_meta_id,event_meta_domain,event_id,event_wiki,event_user,event_type,event_title
   FROM wtbl
   WHERE
      event_type='edit' AND event_wiki='enwiki')
SELECT
   event_title,COUNT(*)
FROM q
GROUP BY event_title
ORDER BY COUNT(*) DESC
LIMIT 10;
+--------------------------------------------------------+-------+
| event_title                                            | count |
|--------------------------------------------------------+-------|
| UPS Airlines Flight 2976                               | 380   |
| Wikipedia:In the news/Candidates                       | 311   |
| Wikipedia:Administrator intervention against vandalism | 219   |
| Wikipedia:Sandbox                                      | 214   |
| Zohran Mamdani                                         | 212   |
| Wikipedia:Administrators' noticeboard/Incidents        | 190   |
| Wikipedia:Requests for page protection/Increase        | 174   |
| 2025 New York City mayoral election                    | 148   |
| User:AmandaNP/UAA/Time                                 | 145   |
| Talk:UPS Airlines Flight 2976                          | 122   |
+--------------------------------------------------------+-------+
```

## edits for a single page
```
WITH q AS (
   SELECT
      TO_TIMESTAMP(event_meta_dt, 'YYYY-MM-DD T HH24:MI:SS') AS ts_event_meta_dt,
      event_meta_id,event_meta_domain,event_id,event_wiki,event_user,event_type,event_title
   FROM wtbl
   WHERE
      event_type='edit' AND event_wiki='dewiki' AND event_title='Wolfgang Amadeus Mozart')
SELECT
   DATE(ts_event_meta_dt) AS date, EXTRACT(HOUR FROM ts_event_meta_dt) AS hour,
   COUNT(*)
FROM q
GROUP BY
   DATE(ts_event_meta_dt),EXTRACT(HOUR FROM ts_event_meta_dt)
ORDER BY
   DATE(ts_event_meta_dt),EXTRACT(HOUR FROM ts_event_meta_dt);
+------------+------+-------+
| date       | hour | count |
|------------+------+-------|
| 2025-11-05 | 17   | 13    |
| 2025-11-05 | 18   | 17    |
| 2025-11-05 | 19   | 3     |
| 2025-11-05 | 22   | 17    |
| 2025-11-05 | 23   | 18    |
| 2025-11-06 | 0    | 2     |
| 2025-11-06 | 8    | 3     |
| 2025-11-06 | 9    | 3     |
| 2025-11-06 | 11   | 4     |
+------------+------+-------+
```
