#!/usr/bin/env python3
# backup script for byro, requires, that the /opt/byro/.ssh/backup key can login in server and homedir of user is writable
import datetime
import tempfile
import tarfile
import subprocess
import itertools
import sys
cmd = ["/usr/bin/pg_dump", "-d", "byro"]

import destinations
try:
    with tempfile.TemporaryDirectory() as d:
        with open(d + "/byro.pgdump",'wb') as f:
            popen = subprocess.run(cmd, stdout=f, universal_newlines=True)

        currentTime = str(datetime.datetime.today().isoformat()).replace(":", "-")
        filename = "byro.backup." + currentTime + ".tar.xz"
        filepath = d + "/" +filename

        with tarfile.open(name=filepath,  mode='x:xz') as t:
            t.add(d + "/byro.pgdump", arcname="byro/byro.pgdump")
            t.add("/opt/byro/static", arcname="byro/static")
            t.add("/opt/byro/data", arcname="byro/data")

        with open(filepath, 'rb') as t:
            agefilepath = "/opt/byro/backup/" + filename + ".age"
            with open(agefilepath, 'wb') as f:
                recipents_list = []
                for key in destinations.keys:
                    recipents_list += ["-r"] + [f"{key}"]
                subprocess.run(["/opt/byro/bin/age"] + recipents_list , stdin=t, stdout=f)

        print("foo")
        for server in destinations.ssh_hosts:
            subprocess.run(["/usr/bin/scp", "-i", "/opt/byro/.ssh/backup", "-P", str(server.port), agefilepath, f"{server.user}@{server.host}:" ]).check_returncode()
except Exception as e:
    print(e)
    sys.exit(1)
