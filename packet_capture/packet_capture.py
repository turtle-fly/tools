import paramiko
import threading
import json
import datetime
import time

capture_point = []


def analyze_inventory(path="inventory"):
    with open(path, "r") as fp:
        for line in fp.readlines():
            if line.strip().startswith("#"):
                continue
            if line.strip() == "":
                continue
            info_list = []
            info = {}
            info_list = line.split(" ", 4)
            info["type"] = info_list[0]
            info["host"] = info_list[1]
            info["username"] = info_list[2]
            info["password"] = info_list[3]
            info["cmd"] = info_list[4].strip()
            info["pid"] = -1
            info["ssh"] = paramiko.SSHClient()
            info["sshc"] = None
            info["interface"] = ""
            info["log"] = ""
            if info["type"] == "esxi":
                if "--uplink" in info["cmd"]:
                    info["interface"] = info["cmd"].split("--uplink")[1].strip().split(" ")[0]
                else:
                    info["interface"] = "all"
                info["log"] = info["cmd"].split("--outfile")[1].strip().split(" ")[0]
            elif info["type"] == "linux":
                if "-i" in info["cmd"]:
                    info["interface"] = info["cmd"].split("-i")[1].strip().split(" ")[0]
                else:
                    info["interface"] = "all"
                info["log"] = info["cmd"].split("-w")[1].strip().split(" ")[0]
            capture_point.append(info)


def start_capture():
    for info in capture_point:
        info["ssh"].set_missing_host_key_policy(paramiko.AutoAddPolicy())
        info["ssh"].connect(info["host"], username=info["username"], password=info["password"])
        info["sshc"] = info["ssh"].invoke_shell()
        info["sshc"].settimeout(120)
        info["sshc"].send(chr(13))
        time.sleep(1)
        if info["type"] == "linux":
            info["sshc"].send("echo {} | sudo -S {}{}".format(info["password"], info["cmd"], chr(13)))
        elif info["type"] == "esxi":
            info["sshc"].send("{}{}".format(info["cmd"], chr(13)))
        print "Capturing {} {} {}...".format(info["type"], info["host"], info["interface"])
        time.sleep(2)
        print info["sshc"].recv(1000)


def stop_capture():
    for info in capture_point:
        # send Ctrl-C
        info["sshc"].send(chr(3))
        info["sshc"].close()
        info["ssh"].close()
        print "Stop {} {} {}...".format(info["type"], info["host"], info["interface"])


def fetch_capture():
    curr_time = datetime.datetime.fromtimestamp(time.time()).strftime("%Y%m%d%H%M%S")
    for info in capture_point:
        dst = "{}_{}_{}_{}.pcapng".format(curr_time, info["type"], info["host"], info["interface"])
        t = paramiko.Transport((info["host"], 22))
        t.connect(username=info["username"], password=info["password"])
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.get(info["log"], dst)


if __name__ == "__main__":
    print "-"*40
    print "To Capture:"
    analyze_inventory()
    for info in capture_point:
        print "{0:<8}{1:<18}{2:<8}".format(info["type"], info["host"], info["interface"])

    print "-"*40
    start_capture()

    print "-"*40
    while 1:
        if raw_input("Stop? (y/n): ").lower().startswith("y"):
            break

    print "-"*40
    stop_capture()
    time.sleep(2)

    print "-"*40
    fetch_capture()
