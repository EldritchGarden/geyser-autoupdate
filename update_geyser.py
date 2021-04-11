"""A small script which auto-updates the GeyserMC plugin for Minecraft Spigot/Paper servers
with FTP file access
"""

import json
import os
import shutil
from pathlib import Path
from urllib import request
from ftplib import FTP, error_perm

# Parse config host.json #
with open("host.json", 'r') as config:
    host = json.load(config)

save_dir = Path("download")


def send(file:str, loc: str):
    """send a file named file_name to loc on the server"""

    print("Sending file...")
    try:
        ftp = FTP(host=host['ftp_server'], user=host['username'], passwd=host['password'])
        ftp.cwd(loc)
        with open(file, 'rb') as fh:
            name = file.split(os.sep)[-1]
            ftp.storbinary(f"STOR %s" % name, fh)  # send STOR command
        print("Success")
    except error_perm as err:
        print("An FTP Error Has Occured: {}".format(err))

    ftp.quit()  # exit ftp session


def delete(file: str, loc: str):
    """Delete a file off the ftp server, be careful"""

    try:
        ftp = FTP(host=host['ftp_server'], user=host['username'], passwd=host['password'])
        ftp.cwd(loc)
        response = ftp.delete(file)
        print(response)
    except error_perm as err:
        print("An FTP Error Has Occured: {}".format(err))


def get_latest_build():
    """Get latest build artifacts from jenkins and download
    
    Currently only downloads the Spigot version, and renames it with the build number
    """

    with open("host.json", 'r') as file:
        build_host = json.load(file)['jenkins_host']

    last_build_api = build_host + "lastSuccessfulBuild/api/json"
    last_build_art = build_host + "lastSuccessfulBuild/artifact/"

    print("Getting last build info")
    with request.urlopen(last_build_api) as response:
        last_build = json.loads(response.read().decode('utf-8'))  # will read as bytes

    # check that this is a newer build
    if host['last_build'] == last_build['displayName']:
        print("No new build, exiting")
        raise SystemExit

    # check that build was successful
    if last_build['result'] != "SUCCESS":
        print("Latest build was failure, exiting")
        raise SystemExit

    print("Downloading Artifacts")
    artifacts = last_build['artifacts']
    for item in artifacts:
        if 'spigot' in item['fileName'].lower():
            rel_path = last_build_art + item['relativePath']
            loc_path = Path(save_dir / (f"Geyser-Spigot-%s.jar" % last_build['displayName']))
            if not loc_path.exists():
                request.urlretrieve(rel_path, str(loc_path))  # download files to loc_path
            else:
                print("File already downloaded")

    return last_build['displayName']


if __name__ == "__main__":
    if not save_dir.exists():  # create download folder if necessary
        os.makedirs(str(save_dir))

    # check current download space usage
    size = 0
    for item in os.scandir(str(save_dir)):
        size += os.path.getsize(item)

    if size > 100000000:  # remove files if over 100MB
        shutil.rmtree(str(save_dir))
        os.makedirs(str(save_dir))

    # download latest file
    latest  = get_latest_build()
    up_file = f"Geyser-Spigot-%s.jar" % latest  # file name to send

    # send file
    send(str(Path(save_dir / up_file)), "plugins")

    # delete old file
    old_file = f"Geyser-Spigot-%s.jar" % host['last_build']
    delete(old_file, "plugins")

    # store latest build in host.json
    host['last_build'] = latest
    with open("host.json", 'w') as update:
        json.dump(host, update)
