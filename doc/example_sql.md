# Example SQL Queries
On this page a few simple example SQL queries are compiled.
This only scratches the surface of what insights can be extracted for this database.

## Top Wikis

```
SELECT event_wiki,COUNT(*) FROM wiki_change_events GROUP BY event_wiki ORDER BY COUNT(*) DESC LIMIT 10;
```

## Types of Events
```
SELECT event_type,COUNT(*) FROM wiki_change_events GROUP BY event_type ORDER BY COUNT(*) DESC;
```

## Event Rates
Note: these queries count all types of events, not just edits.
### Hours with Highest Number of Events
```
SELECT
    DATE(ts_event_meta_dt) AS date, EXTRACT(HOUR FROM ts_event_meta_dt) AS hour, COUNT(*) AS c
FROM wiki_change_events
GROUP BY
    DATE(ts_event_meta_dt), EXTRACT(HOUR FROM ts_event_meta_dt)
ORDER BY
    COUNT(*) DESC
LIMIT 10;
```

### Days with Highest Number of Events
Here we also count just the "edit" events (these are approx. 50% of all events in the database).
```
WITH q AS (
    SELECT
        DATE(ts_event_meta_dt) AS date,
        COUNT(*)/86400.0 AS total_per_sec,
        SUM ( CASE WHEN event_type='edit' THEN 1 END )/86400.0 AS edits_per_sec
    FROM wiki_change_events
    GROUP BY
        DATE(ts_event_meta_dt)
)
SELECT * FROM q ORDER BY total_per_sec DESC;
```
The median event rate is about 35/second (computed over the day).

## Temporal Edit Distribution for 'dewiki'
*Note:* The code generating the data presented in the Streamlit user interfaces uses a more complicated query. The result of this query is stored as materialized view.
```
SELECT
   DATE(ts_event_meta_dt) AS date, EXTRACT(HOUR FROM ts_event_meta_dt) AS hour,
   COUNT(*)
FROM wiki_change_events
WHERE
   event_type='edit' AND event_wiki='dewiki'
GROUP BY
   DATE(ts_event_meta_dt),EXTRACT(HOUR FROM ts_event_meta_dt)
ORDER BY
   DATE(ts_event_meta_dt),EXTRACT(HOUR FROM ts_event_meta_dt);
```

## Top Pages
```
SELECT
   event_title,COUNT(*)
FROM wiki_change_events
WHERE 
   ts_event_meta_dt>'2025-11-26'
   AND event_type='edit'
   AND event_wiki='enwiki'
   -- exclude a few types of titles that may not be interesting
   AND (NOT event_title LIKE 'Talk:%')
   AND (NOT event_title LIKE 'User:%') AND (NOT event_title LIKE 'User talk:%')
   AND (NOT event_title LIKE 'Wikipedia:%') AND (NOT event_title LIKE 'Wikipedia talk:%')
GROUP BY event_title
ORDER BY COUNT(*) DESC
LIMIT 20;
```

## Edits of Specific Page
```
SELECT
   DATE(ts_event_meta_dt) AS date, EXTRACT(HOUR FROM ts_event_meta_dt) AS hour,
   COUNT(*)
FROM wiki_change_events
WHERE
   event_type='edit' AND event_wiki='dewiki' AND event_title='Wolfgang Amadeus Mozart'
GROUP BY
   DATE(ts_event_meta_dt),EXTRACT(HOUR FROM ts_event_meta_dt)
ORDER BY
   DATE(ts_event_meta_dt),EXTRACT(HOUR FROM ts_event_meta_dt);
```
