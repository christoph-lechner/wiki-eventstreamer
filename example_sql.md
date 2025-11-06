## top wikis
```
postgres@localhost:postgres> SELECT event_wiki,COUNT(*) FROM wtbl GROUP BY event_wiki ORDER BY COUNT(*) DESC LIMIT 10;
+--------------+--------+
| event_wiki   | count  |
|--------------+--------|
| commonswiki  | 401842 |
| wikidatawiki | 239365 |
| enwiki       | 93081  |
| cewiki       | 32790  |
| ruwikinews   | 20397  |
| frwiki       | 18280  |
| ukwiki       | 13944  |
| ckbwiki      | 12733  |
| dewiki       | 12587  |
| ruwiki       | 11440  |
+--------------+--------+
```

## types of events
```
postgres@localhost:postgres> SELECT event_type,COUNT(*) FROM wtbl GROUP BY event_type ORDER BY COUNT(*) DESC;
+------------+--------+
| event_type | count  |
|------------+--------|
| edit       | 537744 |
| categorize | 370772 |
| log        | 67757  |
| new        | 23692  |
| <null>     | 35     |
+------------+--------+
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
| UPS Airlines Flight 2976                               | 142   |
| Wikipedia:In the news/Candidates                       | 132   |
| Zohran Mamdani                                         | 87    |
| Wikipedia:Sandbox                                      | 82    |
| Wikipedia:Administrators' noticeboard/Incidents        | 82    |
| Wikipedia:Administrator intervention against vandalism | 74    |
| List of acts of the Parliament of Northern Ireland     | 68    |
| User:Eurodog/sandbox473                                | 66    |
| Template:Zionism UK                                    | 58    |
| Dennis Harrison                                        | 51    |
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
| 2025-11-05 | 22   | 8     |
+------------+------+-------+
```
