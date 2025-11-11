wtbl umbenannt in stg_table

CREATE TABLE stg_table2 AS
SELECT
	MD5(CONCAT(CONCAT(event_meta_id,'_'),'-',CONCAT(event_meta_dt,'_'),'-',CONCAT(CAST(event_id AS TEXT),'_'),'-',CONCAT(event_user,'_'))) AS _h,
	TO_TIMESTAMP(event_meta_dt, 'YYYY-MM-DD T HH24:MI:SS.FF3 TZ') AS ts_event_meta_dt,
	event_meta_dt,event_meta_id,event_meta_domain,event_id,event_type,event_wiki,event_user,event_bot,event_title
FROM stg_table;

-- de-duplicate based on MD5 hash
CREATE TABLE stg_table3 AS
WITH q AS (
	SELECT *, ROW_NUMBER() OVER(PARTITION BY _h) AS _rn FROM stg_table2
)
SELECT _h,ts_event_meta_dt,event_meta_dt,event_meta_id,event_meta_domain,event_id,event_type,event_wiki,event_user,event_bot,event_title FROM q WHERE _rn=1;

Cross-check: the number of rows that made it into `stg_table3` is the same as the result of
```
SELECT COUNT(DISTINCT _h) FROM stg_table2;
```

```
MERGE
INTO
	manual_wtbl_from_stage3 AS dst
USING
	stg_table3 AS src
ON
	dst._h=src._h
WHEN MATCHED THEN DO NOTHING
WHEN NOT MATCHED THEN INSERT VALUES (_h,ts_event_meta_dt,event_meta_dt,event_meta_id,event_meta_domain,event_id,event_type,event_wiki,event_user,event_bot,event_title);
```
The output MERGE total_count is "the total number of rows changed (whether inserted, updated, or deleted)" https://www.postgresql.org/docs/current/sql-merge.html (access 2025-Nov-08)


## can one avoid the stage3 table and `ROW_NUMBER()`?
Let's see:
```
MERGE
INTO
	manual_wtbl_from_stage2 AS dst
USING
	stg_table2 AS src
ON
	dst._h=src._h
WHEN MATCHED THEN DO NOTHING
WHEN NOT MATCHED THEN INSERT VALUES (_h,ts_event_meta_dt,event_meta_dt,event_meta_id,event_meta_domain,event_id,event_type,event_wiki,event_user,event_bot,event_title);
```
--> result MERGE 21485198 (is exactly row count in stg_table2, so data was not deduplicated while inserting).
