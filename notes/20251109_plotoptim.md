2025-11-09

Running with DB already on new computer. Data covering 2025-11-01T00:00:00Z -- 2025-11-08T18:04:59Z (21.5 mio rows).

## Initial measurements
Measurement with script, commit id 91a9013
```
(venv) cl@cl-ThinkPad-X390:~/work/wikitest$ ./simple_plot.py 
time for data collection: 8.6214280128479
time for data collection: 13.27658486366272
```

Measurement with script reflecting improved table structure (with timestamp conversion already while loading), commit id 6071373
```
(venv) cl@cl-ThinkPad-X390:~/work/wikitest$ ./simple_plot.py 
time for data collection: 8.622257947921753
time for data collection: 10.600998640060425
```
Verified that these reported times are reproducible.


## Test with partitioning
Refs:
* https://www.postgresql.org/docs/current/ddl-partitioning.html (access 2025-11-09)

TODO:
For the query
```
SELECT * FROM wiki_change_events WHERE event_meta_id='8037d3bb-7d8a-43af-a89a-d81779a166aa'
```
two events (with different MD5 hash) but time stamps `2025-11-05 02:55:54.613+00` and `2025-11-05 02:55:54.678+00` are returned.

Create table schema.
Note: had to change the `UNIQUE` constraint, think if this is still working for the deduplication (event_wiki is not included in the MD5 hash).
This avoids the error message (see https://stackoverflow.com/q/76071450)
```
ERROR:  unique constraint on partitioned table must include all partitioning columns
UNIQUE constraint on table "wiki_change_events_test" lacks column "event_wiki" which is part of the partition key. 

SQL state: 0A000
Detail: UNIQUE constraint on table "wiki_change_events_test" lacks column "event_wiki" which is part of the partition key.
```
The schema for this _experiment_ is therefore:
```
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
```

Most of our per-article queries include a `WHERE` condition filtering for the country, typically `dewiki` and `enwiki` are used. Therefore:
```
CREATE TABLE wiki_change_events_test_dewiki
	PARTITION OF wiki_change_events_test
	FOR VALUES IN ('dewiki');
CREATE TABLE wiki_change_events_test_enwiki
	PARTITION OF wiki_change_events_test
	FOR VALUES IN ('enwiki');
CREATE TABLE wiki_change_events_test_otherwikis
	PARTITION OF wiki_change_events_test DEFAULT;
```

Checking in pgcli:
```
postgres@localhost:wikidb> \d+ wiki_change_events_test
+-------------------+--------------------------+-----------+----------+
| Column            | Type                     | Modifiers | Storage  |
|-------------------+--------------------------+-----------+----------|
| _h                | text                     |           | extended |
| ts_event_meta_dt  | timestamp with time zone |           | plain    |
| event_meta_dt     | text                     |           | extended |
| event_meta_id     | text                     |           | extended |
| event_meta_domain | text                     |           | extended |
| event_id          | bigint                   |           | plain    |
| event_type        | text                     |           | extended |
| event_wiki        | text                     |           | extended |
| event_user        | text                     |           | extended |
| event_bot         | boolean                  |           | plain    |
| event_title       | text                     |           | extended |
+-------------------+--------------------------+-----------+----------+
Indexes:
    "wiki_change_events_test__h_event_wiki_key" UNIQUE CONSTRAINT, btree btree (_h, event_wiki)
Partition key: LIST (event_wiki)
Partitions: public.wiki_change_events_test_dewiki FOR VALUES IN ('dewiki')
            public.wiki_change_events_test_enwiki FOR VALUES IN ('enwiki')
            public.wiki_change_events_test_otherwikis DEFAULT
```

Let's populate the table (query took 13min):
```
INSERT INTO wiki_change_events_test
SELECT * FROM wiki_change_events;
```

After changing to the new partitioned table, the article-specific query (the first one) becomes fast, the query computing total number of edits for a few selected courties becomes slower than before:
```
(venv) cl@cl-ThinkPad-X390:~/work/wikitest$ ./simple_plot.py 
time for data collection: 2.643923044204712
time for data collection: 78.99680876731873
(venv) cl@cl-ThinkPad-X390:~/work/wikitest$ ./simple_plot.py 
time for data collection: 0.7782554626464844
time for data collection: 43.524115562438965
(venv) cl@cl-ThinkPad-X390:~/work/wikitest$ ./simple_plot.py 
time for data collection: 0.7622954845428467
time for data collection: 42.70251250267029
```

Another test: Since most of the countries in the country plot have rather low traffic, add an index on `event_wiki`:
```
CREATE INDEX wiki_change_events_test_wiki_idx ON wiki_change_events_test (event_wiki);
```
Running three times again (script git commit id 554aa1a):
```
(venv) cl@cl-ThinkPad-X390:~/work/wikitest$ ./simple_plot.py 
time for data collection: 0.7640612125396729
time for data collection: 9.033792495727539
(venv) cl@cl-ThinkPad-X390:~/work/wikitest$ ./simple_plot.py 
time for data collection: 0.7816879749298096
time for data collection: 3.994915008544922
(venv) cl@cl-ThinkPad-X390:~/work/wikitest$ ./simple_plot.py 
time for data collection: 0.7415037155151367
time for data collection: 3.8598783016204834
```
Preparing the data for the second plot is now faster than before.

## Another round
There are two high-traffic wikis that we currently don't use in our analysis: `commonswiki` and `wikidatawiki`. With above partitioning approach, these dominate the wiki types in the DEFAULT partition.
```
postgres@localhost:wikidb> SELECT event_wiki,COUNT(*) FROM wiki_change_events GR
 OUP BY event_wiki ORDER BY COUNT(*) DESC LIMIT 10;
+--------------+---------+
| event_wiki   | count   |
|--------------+---------|
| commonswiki  | 8884073 |
| wikidatawiki | 3233113 |
| enwiki       | 2287601 |
| idwiki       | 559278  |
| ruwikinews   | 536982  |
| enwiktionary | 510121  |
| ruwiki       | 439795  |
| frwiki       | 366649  |
| ckbwiki      | 301614  |
| dewiki       | 276737  |
+--------------+---------+
```
Therefore it might be expected that by holding these in a dedicated partition, the query times when analyzing events for specific languages would improve.
Let's try this is.
```
CREATE TABLE wiki_change_events_test_dewiki
	PARTITION OF wiki_change_events_test
	FOR VALUES IN ('dewiki');
CREATE TABLE wiki_change_events_test_enwiki
	PARTITION OF wiki_change_events_test
	FOR VALUES IN ('enwiki');
CREATE TABLE wiki_change_events_test_hightraffic
	PARTITION OF wiki_change_events_test
	FOR VALUES IN ('commonswiki','wikidatawiki');
CREATE TABLE wiki_change_events_test_otherwikis
	PARTITION OF wiki_change_events_test DEFAULT;
```

Running it (without the additional index)
```
(venv) cl@cl-ThinkPad-X390:~/work/wikitest$ ./simple_plot.py 
time for data collection: 0.8697710037231445
time for data collection: 3.817462921142578
(venv) cl@cl-ThinkPad-X390:~/work/wikitest$ ./simple_plot.py 
time for data collection: 0.7576980590820312
time for data collection: 3.641813278198242
(venv) cl@cl-ThinkPad-X390:~/work/wikitest$ ./simple_plot.py 
time for data collection: 0.7603030204772949
time for data collection: 3.65541934967041
(venv) cl@cl-ThinkPad-X390:~/work/wikitest$
```

Here the additional index on `event_wiki` does not improve:
```
(venv) cl@cl-ThinkPad-X390:~/work/wikitest$ ./simple_plot.py 
time for data collection: 0.7704546451568604
time for data collection: 3.1617066860198975
(venv) cl@cl-ThinkPad-X390:~/work/wikitest$ ./simple_plot.py 
time for data collection: 0.7725253105163574
time for data collection: 3.1204419136047363
(venv) cl@cl-ThinkPad-X390:~/work/wikitest$ ./simple_plot.py 
time for data collection: 0.7753701210021973
time for data collection: 3.1303231716156006
(venv) cl@cl-ThinkPad-X390:~/work/wikitest$
```
