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
	   DATE(ts_event_meta_dt),EXTRACT(HOUR FROM ts_event_meta_dt)
	ORDER BY
	   DATE(ts_event_meta_dt),EXTRACT(HOUR FROM ts_event_meta_dt)
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
	   DATE(ts_event_meta_dt),EXTRACT(HOUR FROM ts_event_meta_dt)
	ORDER BY
	   DATE(ts_event_meta_dt),EXTRACT(HOUR FROM ts_event_meta_dt)
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
	   DATE(ts_event_meta_dt),EXTRACT(HOUR FROM ts_event_meta_dt)
	ORDER BY
	   DATE(ts_event_meta_dt),EXTRACT(HOUR FROM ts_event_meta_dt)
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

## Step 4
Further improvements: series used for gap filling is no longer extending beyond event counts obtained from DB:
```
WITH q AS (
    SELECT
       DATE(ts_event_meta_dt) AS date, EXTRACT(HOUR FROM ts_event_meta_dt) AS hour,
       COUNT(*),
		   -- To determine time range for zero-gap filling in result
		   -- MIN(ts_event_meta_dt) AS col_min, MAX(ts_event_meta_dt) AS col_max,
       -- need start of hour, see https://www.postgresql.org/docs/current/functions-datetime.html
		   DATE_TRUNC('HOUR', MIN(ts_event_meta_dt)) AS col_min_startofhour
    FROM wiki_change_events_test
    WHERE
       event_type='edit' AND event_wiki='dewiki' AND event_title='Wolfgang Amadeus Mozart'
    GROUP BY
       DATE(ts_event_meta_dt),EXTRACT(HOUR FROM ts_event_meta_dt)
    ORDER BY
       DATE(ts_event_meta_dt),EXTRACT(HOUR FROM ts_event_meta_dt)
),
times_without_gap AS(
SELECT
	DATE(gs) AS gs_date, EXTRACT(HOUR FROM gs) AS gs_hour
FROM
	generate_series((SELECT MIN(col_min_startofhour) FROM q), (SELECT MAX(col_min_startofhour) FROM q), interval '1 hour') AS gs
)
SELECT
    -- column for development purposes in pgadmin
    gs_date,gs_hour,q.date,q.hour,COALESCE(q.count,-10) FROM times_without_gap
    -- the gs_* columns are not-NULL
    -- gs_date,gs_hour,COALESCE(q.count,0) FROM times_without_gap
LEFT JOIN q ON (q.date=gs_date AND q.hour=gs_hour);
```
