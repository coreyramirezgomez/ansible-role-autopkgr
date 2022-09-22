"""munki_lander.py file contents."""
import json
import os
import subprocess
import sys

target_tag_name = "v5.1.2"
curl = "/usr/bin/curl"
installer = "/usr/sbin/installer"
gh_releses_url = "https://api.github.com/repos/munki/munki/releases"

if __name__ == "__main__":
    proc = subprocess.Popen([curl, "-s", gh_releses_url], stdout=subprocess.PIPE)
    (out, err) = proc.communicate()
    jdata = json.loads(out)
    package = ""
    for r in jdata:
        if r["tag_name"] == target_tag_name:
            browser_download_url = r["assets"][0]["browser_download_url"]
            package = "/tmp/{}".format(browser_download_url.split('/')[-1])
            break
    if package:
        proc = subprocess.Popen([curl, "-s", "-o", package, "-L", browser_download_url], stdout=subprocess.PIPE)
        proc.wait()
        proc = subprocess.Popen([installer, "-pkg", package, "-target", "/"], stdout=subprocess.PIPE)
        proc.wait()
        (out, err) = proc.communicate()
        print("### installer stdout ###\n{}".format(str(out).strip().decode('ascii')))
        print("### installer stderr ###\n{}".format(str(err).strip().decode('ascii')))
        os.remove(package)
        sys.exit(proc.returncode)
    else:
        print("No release data found for tag {}".format(target_tag_name))
        print("Retrieved release data:\n{}".format(json.dumps(jdata, indent=4)))
        sys.exit(1)
