# Example SQL Queries
## Top Wikis

```
SELECT event_wiki,COUNT(*) FROM wiki_change_events GROUP BY event_wiki ORDER BY COUNT(*) DESC LIMIT 10;
```

## Types of Events
```
SELECT event_type,COUNT(*) FROM wiki_change_events GROUP BY event_type ORDER BY COUNT(*) DESC;
```

## Temporal Edit Distribution for 'dewiki'
*Note:* In the code compiling the data for the plots, a more complicated query is used that fill the time gaps (hours without any edits) with zeros. See `db_query.py`.
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
   event_type='edit' AND event_wiki='enwiki' 
   AND (NOT event_title LIKE 'Talk:%')
   AND (NOT event_title LIKE 'User:%') AND (NOT event_title LIKE 'User talk:%')
   AND (NOT event_title LIKE 'Wikipedia:%') AND (NOT event_title LIKE 'Wikipedia talk:%')
GROUP BY event_title
ORDER BY COUNT(*) DESC
LIMIT 50;
```

## edits for a single page
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
