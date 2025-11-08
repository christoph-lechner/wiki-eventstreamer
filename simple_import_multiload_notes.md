CL, 2025-11-08

In directory containing `.ready` files that are to be loaded:
```
find streamdata -iname '*.ready' -print | sort > LOF
```

```
$ script -f log_20250811T2030.txt
Script started, output log file is 'log_20250811T2030.txt'.
$ source /home/[redacted]/venv_ws/bin/activate

(venv_ws) $ cat LOF | xargs -n 1 ../simple_import.py -z
[..]
```
