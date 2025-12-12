**currently under development**

## docker compose
To bring the service up (the service runs in foreground), run
```
sudo make up
```
This always launches the build process. This build process takes less than a second if there were no changes (same git commit ID). If the git commit ID was changed (or there were changes, resulting in a commit ID with suffix `-dirty`), the entire build process runs through.

To check, obtain container ID using `docker ps` and then execute
```
sudo docker exec -it 5304c272e9d2 cat /app/git_info.txt
```

### collection of useful commands
* Diagnosing environment variable substitution: `docker compose config` 
* To force rebuilding the image: `sudo docker compose build --no-cache`

## building/running image without "docker compose"
To build it (`name_of_image` could be something like `wikistreamreader:latest`):
```
sudo docker build --build-arg GIT_INFO=$(git describe --dirty --always --tags) -t <name_of_image> .
```

To run it:
```
sudo docker run --user=1000:1000 -v "./datadir:/data" -p 9999:8080 --rm -it <name_of_image>
```

If the python3 process is terminated (via SIGTERM or Ctrl-C), then the docker run ends.




