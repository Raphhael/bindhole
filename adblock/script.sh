
#!/bin/ash -xe

echo "Start update"

/root/adblock/venv/bin/python3 main.py
cp /etc/bind/db.rpz-adblock "/root/adblock/backups/db.$(date +%s)"
named-checkzone rpz-adblock /root/adblock/db-adblock
mv /root/adblock/db-adblock /etc/bind/db.rpz-adblock
# rndc reload
killall named
named

