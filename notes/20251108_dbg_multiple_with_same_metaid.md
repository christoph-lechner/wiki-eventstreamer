After loading multiple files, there are several "meta id" values appearing multiple times.

To find them, we run the SQL query
```
WITH q AS(
	SELECT event_meta_id,COUNT(*)
	FROM wtbl
	-- WHERE NOT (event_type='log')
	GROUP BY event_meta_id
	HAVING COUNT(*)>=2
	ORDER BY event_meta_id,COUNT(*) DESC
	-- LIMIT 100
)
SELECT * FROM q;
```

For instance `960a2797-8911-4dd0-8b82-0618a64c83cd` appears 2 times in the database table `wtbl` (with all values identical), but running a `zgrep` on all data files used to populate the DB gives only a single hit.

## Investigation
Renamed old table to retain contents.

Started another import process.

Quite early, the `event_meta_id` `72067411-6ffa-45de-98e8-8a3ed5bf3ab1` appears twice. These are inserted as file `streamdata/stream_20251107T135657_000000007.gz.ready` is loaded.
Adding a `print` to the `simple_import` script, it turns out that the `INSERT` is executed twice with this value for `event_meta_id`.

Using grep on the logfile, we can locate the `meta_event_id` values to prepare comparison with the input file (not offset because tool also writes one line saying which file is being read).
```
(venv_ws) cl@clsrv:~/work/wiki-eventstreamer/data$ grep -C 3 -n 72067411-6ffa log
86637---- 39768e57-31e8-4f04-b7e7-af144a10e293
86638---- 542a88a7-f882-4dfe-a266-756f27d066f8
86639---- c15ae7a7-1dd1-49f8-8bbf-282160ec44e4
86640:--- 72067411-6ffa-45de-98e8-8a3ed5bf3ab1
86641---- f4d6c86f-685c-4534-964a-f4753b5602b0
86642:--- 72067411-6ffa-45de-98e8-8a3ed5bf3ab1
86643---- f4d6c86f-685c-4534-964a-f4753b5602b0
86644---- 6953762a-52e2-4d20-a2b1-e5f4702716f2
86645---- ed9e172a-0029-4e58-aad2-53013a95294b
(venv_ws) cl@clsrv:~/work/wiki-eventstreamer/data$
```
Analysis of the JSON data in the input file reveals that the `meta_event_id` values were actually sent twice.

Conclusion: A deduplication mechanism is needed. Actually this issue was detected while preparing one...
