# TODO
* If connection breaks, make automatic reconnection more robust: Don't break after the first non-200 response (when testing the software I had a 503 which caused the loading process to abort). Idea would be to keep trying every minute (maybe with callback function that gets called after some time, to inform admins).
* In case of disconnects: Think about ways to resume the streaming where the connection broke. This avoids losing events. See the end of the example program for a guideline how this could be done. 
