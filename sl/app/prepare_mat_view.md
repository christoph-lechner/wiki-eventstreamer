CL, 2025-11-16

Note 2025-11-19: Table `wiki_change_events_test` was renamed to `wiki_change_events` and the VIEWs were recreated with the updated name.

## First Query
```
SELECT DATE(ts_event_meta_dt) AS date, EXTRACT(HOUR FROM ts_event_meta_dt) AS hour,event_wiki,
1 AS count_bot_flagignore,
(CASE WHEN event_bot=TRUE THEN 1 END) AS count_bot_true,
(CASE WHEN event_bot=FALSE THEN 1 END) AS count_bot_false
FROM wiki_change_events_test
LIMIT 10;
```

## First Step to Compute Event Counts
```
SELECT
	DATE(ts_event_meta_dt) AS date, EXTRACT(HOUR FROM ts_event_meta_dt) AS hour,event_wiki,
	SUM(1) AS count_bot_flagignore,
	SUM((CASE WHEN event_bot=TRUE THEN 1 END)) AS count_bot_true,
	SUM((CASE WHEN event_bot=FALSE THEN 1 END)) AS count_bot_false
FROM wiki_change_events_test
GROUP BY date,hour,event_wiki
ORDER BY date,hour,event_wiki
```
It turns out that there are `NULL` values in the computed columns (if there were no events of this kind in that hour). Replace these by `0` using `COALESCE`.

## Improved Query to Compute Event Counts
```
SELECT
	DATE(ts_event_meta_dt) AS date, EXTRACT(HOUR FROM ts_event_meta_dt) AS hour,event_wiki,
	COALESCE( SUM(1),0 ) AS count_bot_flagignore,
	COALESCE( SUM((CASE WHEN event_bot=TRUE  THEN 1 END)),0 ) AS count_bot_true,
	COALESCE( SUM((CASE WHEN event_bot=FALSE THEN 1 END)),0 ) AS count_bot_false
FROM wiki_change_events_test
GROUP BY date,hour,event_wiki
ORDER BY date,hour,event_wiki
```

## Final Query and Definition of Materialized View
Note: This uses PostgreSQL-specific syntax
```
CREATE MATERIALIZED VIEW wiki_matview_countsall AS
SELECT
	DATE(ts_event_meta_dt) AS date, EXTRACT(HOUR FROM ts_event_meta_dt) AS hour,event_wiki,
	COALESCE( SUM(1),0 ) AS count_bot_flagignore,
	COALESCE( SUM((CASE WHEN event_bot=TRUE  THEN 1 END)),0 ) AS count_bot_true,
	COALESCE( SUM((CASE WHEN event_bot=FALSE THEN 1 END)),0 ) AS count_bot_false
FROM wiki_change_events_test
WHERE
	-- the streamreader rotates the stream dumps no at the full hour
	-- -> cut away the final (incomplete) hour
	ts_event_meta_dt<(SELECT DATE_TRUNC('HOUR',MAX(ts_event_meta_dt)) FROM wiki_change_events_test) 
GROUP BY date,hour,event_wiki
ORDER BY date,hour,event_wiki
```

To update this materialized view, we could add to the loader script:
```
REFRESH MATERIALIZED VIEW wiki_matview_countsall;
```

### Consistency Check
These two queries should give the same result (provided the view is up-to-date):
```
SELECT SUM(count_bot_flagignore) FROM wiki_matview_countsall;
```
```
SELECT COUNT(*) FROM wiki_change_events_test
WHERE
	ts_event_meta_dt<(SELECT DATE_TRUNC('HOUR',MAX(ts_event_meta_dt)) FROM wiki_change_events_test);
```

### View only for edits
```
CREATE MATERIALIZED VIEW wiki_matview_countsedits AS
SELECT
	DATE(ts_event_meta_dt) AS date, EXTRACT(HOUR FROM ts_event_meta_dt) AS hour,event_wiki,
	COALESCE( SUM(1),0 ) AS count_bot_flagignore,
	COALESCE( SUM((CASE WHEN event_bot=TRUE  THEN 1 END)),0 ) AS count_bot_true,
	COALESCE( SUM((CASE WHEN event_bot=FALSE THEN 1 END)),0 ) AS count_bot_false
FROM wiki_change_events_test
WHERE
	-- the streamreader rotates the stream dumps no at the full hour
	-- -> cut away the final (incomplete) hour
	ts_event_meta_dt<(SELECT DATE_TRUNC('HOUR',MAX(ts_event_meta_dt)) FROM wiki_change_events_test)
	AND event_type='edit'
GROUP BY date,hour,event_wiki
ORDER BY date,hour,event_wiki
```
