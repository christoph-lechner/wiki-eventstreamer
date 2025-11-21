Schema fuer neue Tabellen ab 20251111T2148
(basierend auf 20251109_plotoptim.md)

CREATE TABLE wiki_change_events_test(
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

CREATE TABLE wiki_change_events_test_20251111_dewiki
	PARTITION OF wiki_change_events_test
	FOR VALUES IN ('dewiki');
CREATE TABLE wiki_change_events_test_20251111_enwiki
	PARTITION OF wiki_change_events_test
	FOR VALUES IN ('enwiki');
CREATE TABLE wiki_change_events_test_20251111_hightraffic
	PARTITION OF wiki_change_events_test
	FOR VALUES IN ('commonswiki','wikidatawiki');
CREATE TABLE wiki_change_events_test_20251111_otherwikis
	PARTITION OF wiki_change_events_test DEFAULT;
	
CREATE INDEX wiki_change_events_test_20251111_ts_event_meta_dt_idx ON wiki_change_events_test (ts_event_meta_dt);
CREATE INDEX wiki_change_events_test_20251111_event_title ON wiki_change_events_test (event_title);

CREATE TABLE wiki_loaderperfdata(
	tstart timestamp with time zone,
	dur float,
	func text,
	infotxt text
)

