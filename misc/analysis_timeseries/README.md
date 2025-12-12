# Burst Rates
Obtain the highest number of events seen in any 900-second-long time interval.

## SQL Solution
```
WITH q AS (
	SELECT
		ts_event_meta_dt AS window_end,
		COUNT(*) OVER (
			ORDER BY ts_event_meta_dt
			RANGE BETWEEN INTERVAL '900 SECONDS' PRECEDING AND CURRENT ROW
		) AS c
	FROM
		wiki_change_events
	-- LIMIT 10
)
SELECT window_end,c
FROM q
ORDER BY c DESC
LIMIT 1;
```

## C++ Solution
### Building it
The build process is done using `CMake`.
```
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make
```

### To obtain the CSV file
Using client `pgcli`, execute the following command to get CSV file in suitable format written on client side (sorting in SQL query not needed as it will be done by the analysis program):
```
\copy (SELECT EXTRACT(EPOCH FROM ts_event_meta_dt) AS e FROM wiki_change_events) TO 'output.csv' CSV;
```

