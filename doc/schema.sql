-- Database schema
--
-- Christoph Lechner, 2025-12-12

CREATE TABLE wiki_datafiles(
    filename TEXT UNIQUE,
    file_hash TEXT,
    filename_xferlog TEXT,
    ts_entry_creation TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ts_file_transfer TIMESTAMP WITH TIME ZONE,
    ts_load_begin TIMESTAMP WITH TIME ZONE,
    ts_load_end TIMESTAMP WITH TIME ZONE,
    loadstat_events_in_file INT,
    loadstat_events_merged INT,
    ts_file_archive TIMESTAMP WITH TIME ZONE
);

CREATE TABLE wiki_change_events(
    -- MD5 hash over a few fields, ensures deduplication (data is loaded into this table using MERGE command)
    _h TEXT,
    ts_event_meta_dt TIMESTAMP WITH TIME ZONE,
    event_meta_dt TEXT,
    event_meta_id TEXT,
    event_meta_domain TEXT,
    event_id BIGINT,
    event_type TEXT,
    event_wiki TEXT,
    event_user TEXT,
    event_bot BOOLEAN,
    event_title TEXT,
    UNIQUE(_h,event_wiki)
) PARTITION BY LIST(event_wiki);
CREATE TABLE wiki_change_events_dewiki
	PARTITION OF wiki_change_events
	FOR VALUES IN ('dewiki');
CREATE TABLE wiki_change_events_enwiki
	PARTITION OF wiki_change_events
	FOR VALUES IN ('enwiki');
CREATE TABLE wiki_change_events_hightraffic
	PARTITION OF wiki_change_events
	FOR VALUES IN ('commonswiki','wikidatawiki');
CREATE TABLE wiki_change_events_otherwikis
	PARTITION OF wiki_change_events DEFAULT;

--------

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
ORDER BY date,hour,event_wiki;

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
ORDER BY date,hour,event_wiki;

