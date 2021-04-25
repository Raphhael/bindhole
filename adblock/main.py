from concurrent.futures import ThreadPoolExecutor
from threading import Lock

import requests
from yaml import safe_load

with open("config.yaml") as f:
    config = safe_load(f)
sources = config.get('sources') or {}
hosts = sources.get('by_hosts') or []
domain_lists = sources.get('by_domains') or []

data = set()
lock = Lock()


def add_host(host):
    if host and host not in ['0.0.0.0', '127.0.0.1', 'localhost']:
        host = host.strip(". \t\n").split(' ')[0] + " CNAME ."
        data.add("*." + host)
        data.add(host)


def process_domains(content):
    for line in content.splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            add_host(line)


def process_hosts(content):
    for line in content.splitlines():
        line = line.strip()
        if line.startswith('127.0.0.1') or line.startswith('0.0.0.0'):
            chunks = line.split()
            if len(chunks) >= 2:
                ip, host = chunks[:2]
                add_host(host)


def download_file(url, ftype):
    try:
        print("download", url)
        resp = requests.get(url)
        resp.raise_for_status()
        with lock:
            if ftype == "hosts":
                process_hosts(resp.text)
            elif ftype == "domains":
                process_domains(resp.text)
            else:
                print("wrong ftype :", ftype)

    except requests.RequestException as err:
        print("URL ERROR : ", err)


with ThreadPoolExecutor(4) as executor:
    for file in set(hosts):
        executor.submit(download_file, file, "hosts")
    for file in set(domain_lists):
        executor.submit(download_file, file, 'domains')

header = """
$TTL 2w

@ IN SOA localhost. root.localhost. (
  2   ; serial
  2w  ; refresh
  2w  ; retry
  2w  ; expiry
  2w  ; minimum
)

@ IN NS localhost.

*.numericable.fr CNAME .
"""
data = sorted(set(data))

with open(config.get('zone_file', 'zone.txt'), "w") as zone:
    zone.write(header)
    zone.write('\n'.join(data))
    zone.write('\n')

print(len(data), "entries")
