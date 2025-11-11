2025-Nov-11

## Setting up user accounts
```
cl@ubuntu:~$ sudo adduser --disabled-password dataacq
[sudo] password for cl: 
Adding user `dataacq' ...
Adding new group `dataacq' (1004) ...
Adding new user `dataacq' (1004) with group `dataacq' ...
Creating home directory `/home/dataacq' ...
Copying files from `/etc/skel' ...
Changing the user information for dataacq
Enter the new value, or press ENTER for the default
	Full Name []: user for data acquisition
	Room Number []: 
	Work Phone []: 
	Home Phone []: 
	Other []: 
Is the information correct? [Y/n] 
cl@ubuntu:~$ id dataacq
uid=1004(dataacq) gid=1004(dataacq) groups=1004(dataacq)
cl@ubuntu:~$ sudo adduser --disabled-password dataxfer
Adding user `dataxfer' ...
Adding new group `dataxfer' (1005) ...
Adding new user `dataxfer' (1005) with group `dataxfer' ...
Creating home directory `/home/dataxfer' ...
Copying files from `/etc/skel' ...
Changing the user information for dataxfer
Enter the new value, or press ENTER for the default
	Full Name []: user for data transfer
	Room Number []: 
	Work Phone []: 
	Home Phone []: 
	Other []: 
Is the information correct? [Y/n] 
cl@ubuntu:~$ id dataxfer
uid=1005(dataxfer) gid=1005(dataxfer) groups=1005(dataxfer)
cl@ubuntu:~$ sudo addgroup wikidata
Adding group `wikidata' (GID 1006) ...
Done.
cl@ubuntu:~$ sudo adduser dataacq wikidata
Adding user `dataacq' to group `wikidata' ...
Adding user dataacq to group wikidata
Done.
cl@ubuntu:~$ id dataacq
uid=1004(dataacq) gid=1004(dataacq) groups=1004(dataacq),1006(wikidata)
cl@ubuntu:~$
```
Note that dataxfer was not added to the new group.

## Setting up SSH login with public key auth
This will be needed for automatic transfers of the stored data.

### ONLY IF NEEDED: prepare public key
```
cl@clsrv:~$ ssh-keygen
Generating public/private ed25519 key pair.
Enter file in which to save the key (/home/cl/.ssh/id_ed25519): 
Enter passphrase (empty for no passphrase): 
Enter same passphrase again: 
Your identification has been saved in /home/cl/.ssh/id_ed25519
Your public key has been saved in /home/cl/.ssh/id_ed25519.pub
The key fingerprint is:
SHA256:[redacted] cl@clsrv
The key's randomart image is:
+--[ED25519 256]--+
[..]
+----[SHA256]-----+
cl@clsrv:~$
```

### Transfer public key to target account
Since password-based log in as `dataxfer` is disabled, the following manual way is pursued.
```
cl@clsrv:~/.ssh$ cat id_ed25519.pub 
ssh-ed25519 [redacted] cl@clsrv
```

On the server on which the streamreader will be running:
```
cl@ubuntu:~$ sudo -i
root@ubuntu:~# su - dataxfer
dataxfer@ubuntu:~$ ls -l .ssh
ls: cannot access '.ssh': No such file or directory
dataxfer@ubuntu:~$ mkdir .ssh
dataxfer@ubuntu:~$ cd .ssh
dataxfer@ubuntu:~/.ssh$ vim authorized_keys
dataxfer@ubuntu:~/.ssh$ ls -l
total 4
-rw-rw-r-- 1 dataxfer dataxfer 90 Nov 10 15:21 authorized_keys
dataxfer@ubuntu:~/.ssh$ chmod 600 authorized_keys 
dataxfer@ubuntu:~/.ssh$
```


## Prepare data directory
```
cl@ubuntu:~$ sudo mkdir /srv/wikiproj/
cl@ubuntu:~$ sudo mkdir /srv/wikiproj/streamdata_in
cl@ubuntu:~$ sudo chown dataacq:wikidata /srv/wikiproj/streamdata_in
cl@ubuntu:~$ sudo chmod 750 /srv/wikiproj/streamdata_in
cl@ubuntu:~$ ls -ld /srv/wikiproj/streamdata_in
drwxr-x--- 2 dataacq wikidata 4096 Nov 10 23:04 /srv/wikiproj/streamdata_in
cl@ubuntu:~$
```
User needing *read access* to the data directory can be added to the `wikidata` group as needed.
