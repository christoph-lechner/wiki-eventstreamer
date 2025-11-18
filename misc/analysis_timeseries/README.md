
## Building it
The build process is done using `CMake`.
```
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make
```

## To obtain the CSV file
Using client `pgcli`, execute the following command to get CSV file in suitable format written on client side (sorting in SQL query not needed as it will be done by the analysis program):
```
\copy (SELECT EXTRACT(EPOCH FROM ts_event_meta_dt) AS e FROM wiki_change_events_test) TO 'output.csv' CSV;
```

