from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from threading import Lock

import requests
from yaml import safe_load

with open("config.yaml") as f:
    config = safe_load(f)
sources = config.get('sources') or {}
hosts = sources.get('by_hosts') or []
domain_lists = sources.get('by_domains') or []
other = sources.get('others') or []
whitelist = set(config.get('whitelist', []) or [])


def add_host(host):
    if host:
        host = host.strip(". \t\n").split(' ')[0]
        if host not in whitelist and not host.startswith('#'):
            data.add(host + " CNAME .")
            # data.add("*." + host)


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
    for i in range(5):
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


if __name__ == '__main__':
    data = set()
    lock = Lock()
    list(map(add_host, other))
    with ThreadPoolExecutor(4) as executor:
        for file in set(hosts):
            executor.submit(download_file, file, "hosts")
        for file in set(domain_lists):
            executor.submit(download_file, file, 'domains')

    header = f"""
$TTL 2w

@ IN SOA localhost. root.localhost. (
    {datetime.now().strftime("%Y%m%d")}   ; serial
    604800     ; refresh
    14400      ; retry
    1209600    ; expiry
    345600     ; minimum
)

@ IN NS localhost.

"""

    data = sorted(set(data))

    with open(config.get('zone_file', 'zone.txt'), "w") as zone:
        zone.write(header)
        zone.write('\n'.join(data))
        zone.write('\n')

    print(len(data), "entries")
