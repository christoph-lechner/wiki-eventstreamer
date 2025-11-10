Based on https://sqlfordevs.com/statistical-results-fill-gaps

## Step 1
```
WITH q AS (
	SELECT
	   DATE(ts_event_meta_dt) AS date, EXTRACT(HOUR FROM ts_event_meta_dt) AS hour,
	   COUNT(*)
	FROM wiki_change_events_test
	WHERE
	   event_type='edit' AND event_wiki='dewiki' AND event_title='Wolfgang Amadeus Mozart'
	GROUP BY
	   ts_event_meta_dt,DATE(ts_event_meta_dt),EXTRACT(HOUR FROM ts_event_meta_dt)
	ORDER BY
	   ts_event_meta_dt,DATE(ts_event_meta_dt),EXTRACT(HOUR FROM ts_event_meta_dt)
)
SELECT DATE(gs) AS gs_date, EXTRACT(HOUR FROM gs) AS gs_hour FROM generate_series((SELECT MIN(date) FROM q), (SELECT MAX(date) FROM q), interval '1 hour') AS gs
```

## Step 2
Still with NULL at the temporal gaps:
```
WITH q AS (
	SELECT
	   DATE(ts_event_meta_dt) AS date, EXTRACT(HOUR FROM ts_event_meta_dt) AS hour,
	   COUNT(*)
	FROM wiki_change_events_test
	WHERE
	   event_type='edit' AND event_wiki='dewiki' AND event_title='Wolfgang Amadeus Mozart'
	GROUP BY
	   ts_event_meta_dt,DATE(ts_event_meta_dt),EXTRACT(HOUR FROM ts_event_meta_dt)
	ORDER BY
	   ts_event_meta_dt,DATE(ts_event_meta_dt),EXTRACT(HOUR FROM ts_event_meta_dt)
),
times_without_gap AS(
SELECT
	DATE(gs) AS gs_date, EXTRACT(HOUR FROM gs) AS gs_hour
FROM
	generate_series((SELECT MIN(date) FROM q), (SELECT MAX(date) FROM q), interval '1 hour') AS gs
)
SELECT gs_date,gs_hour,q.* FROM times_without_gap
LEFT JOIN q ON (q.date=gs_date AND q.hour=gs_hour);
```

## Step 3
```
WITH q AS (
	SELECT
	   DATE(ts_event_meta_dt) AS date, EXTRACT(HOUR FROM ts_event_meta_dt) AS hour,
	   COUNT(*)
	FROM wiki_change_events_test
	WHERE
	   event_type='edit' AND event_wiki='dewiki' AND event_title='Wolfgang Amadeus Mozart'
	GROUP BY
	   ts_event_meta_dt,DATE(ts_event_meta_dt),EXTRACT(HOUR FROM ts_event_meta_dt)
	ORDER BY
	   ts_event_meta_dt,DATE(ts_event_meta_dt),EXTRACT(HOUR FROM ts_event_meta_dt)
),
times_without_gap AS(
SELECT
	DATE(gs) AS gs_date, EXTRACT(HOUR FROM gs) AS gs_hour
FROM
	generate_series((SELECT MIN(date) FROM q), (SELECT MAX(date) FROM q), interval '1 hour') AS gs
)
SELECT gs_date,gs_hour,q.date,q.hour,COALESCE(q.count,-10) FROM times_without_gap
LEFT JOIN q ON (q.date=gs_date AND q.hour=gs_hour);
```
