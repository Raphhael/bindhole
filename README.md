# Example of home adblock BIND9 server

Theses examples are made from VM alpine linux;

- Install bind9, example files in bind directory (`apk add bind`)

- Copy directory `adblock` in `/root`

- Install python & requirements :
    - `apk add python3`
    - `apk add py3-virtualenv`
    - `virtualenv venv`
    - `source venv/bin/activate`
    - `pip install -r requirements.txt`

- To create ad list in bind9 format, run `python3 main.py`

- To update ads list, please run `script.sh` (you can use crontab). Edit service name as needed.

I use it in alpine vm, and default named service always fail.
The "custom-named" service in the script.sh is defined in *`/etc/init.d/custom-named`* file as :
```
#!/sbin/openrc-run

name=custom-named
command=/usr/sbin/named

depend() {
        need net
        need localmount
}
```
