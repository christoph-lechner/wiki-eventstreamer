To build it (`name_of_image` could be something like `cl/dev_wikistreamreader`):
```
sudo docker build -t <name_of_image> .
```

To run it:
```
docker run --user=cl -v "./datadir:/data" -p 9999:8080 -it <name_of_image>
sudo docker run --user=1000:1000 -v "./datadir:/data" -p 9999:8080 -it <name_of_image>
```

If the python3 process is terminated (via SIGTERM or Ctrl-C), then the docker run ends.
