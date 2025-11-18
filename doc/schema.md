## Mat. Views for Edit Analysis
Materialized views for edit analysis: see sl/app/prepare_mat_view.md
```
CREATE MATERIALIZED VIEW wiki_matview_countsall AS
SELECT
        DATE(ts_event_meta_dt) AS date, EXTRACT(HOUR FROM ts_event_meta_dt) AS hour,event_wiki,
        COALESCE( SUM(1),0 ) AS count_bot_flagignore,
        COALESCE( SUM((CASE WHEN event_bot=TRUE  THEN 1 END)),0 ) AS count_bot_true,
        COALESCE( SUM((CASE WHEN event_bot=FALSE THEN 1 END)),0 ) AS count_bot_false
FROM wiki_change_events
WHERE
        -- the streamreader rotates the stream dumps no at the full hour
        -- -> cut away the final (incomplete) hour
        ts_event_meta_dt<(SELECT DATE_TRUNC('HOUR',MAX(ts_event_meta_dt)) FROM wiki_change_events) 
GROUP BY date,hour,event_wiki
ORDER BY date,hour,event_wiki
```

```
CREATE MATERIALIZED VIEW wiki_matview_countsedits AS
SELECT
        DATE(ts_event_meta_dt) AS date, EXTRACT(HOUR FROM ts_event_meta_dt) AS hour,event_wiki,
        COALESCE( SUM(1),0 ) AS count_bot_flagignore,
        COALESCE( SUM((CASE WHEN event_bot=TRUE  THEN 1 END)),0 ) AS count_bot_true,
        COALESCE( SUM((CASE WHEN event_bot=FALSE THEN 1 END)),0 ) AS count_bot_false
FROM wiki_change_events
WHERE
        -- the streamreader rotates the stream dumps no at the full hour
        -- -> cut away the final (incomplete) hour
        ts_event_meta_dt<(SELECT DATE_TRUNC('HOUR',MAX(ts_event_meta_dt)) FROM wiki_change_events)
        AND event_type='edit'
GROUP BY date,hour,event_wiki
ORDER BY date,hour,event_wiki
```

Materialized view `wiki_matview_editburst`: see 20251116__materialized_view.md
