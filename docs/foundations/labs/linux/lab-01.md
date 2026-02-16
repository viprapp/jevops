# Lab 1 - Service lifecycle + journald (sshd)

## Goal

Prove I can: capture baseline, induce a controlled failure, extract relevant
logs, recover, and verify state.

## Environment

- Host: macOS 26.3
- Hypervisor: UTM
- VM: Arch Linux (arch-m1) kernel 6.17.8-1-aarch64-ARCH

## Safety

Stopping sshd may drop SSH/network connectivity. Run from local console.

## Baseline

```sh
> systemctl status sshd.service --no-pager
● sshd.service - OpenSSH Daemon
     Loaded: loaded (/usr/lib/systemd/system/sshd.service; enabled; preset: disabled)
     Active: active (running) since Mon 2026-02-16 19:52:10 CET; 2min 55s ago
 Invocation: fb86d4ed3b284cad82e28aeb842e58f1
       Docs: man:sshd(8)
             man:sshd_config(5)
   Main PID: 363 (sshd)
      Tasks: 1 (limit: 2268)
     Memory: 1.9M (peak: 2.6M)
        CPU: 6ms
     CGroup: /system.slice/sshd.service
             └─363 "sshd: /usr/bin/sshd -D [listener] 0 of 10-100 startups"

Feb 16 19:52:10 arch-m1 systemd[1]: Starting OpenSSH Daemon...
Feb 16 19:52:10 arch-m1 sshd[363]: Server listening on 0.0.0.0 port 22.
Feb 16 19:52:10 arch-m1 sshd[363]: Server listening on :: port 22.
Feb 16 19:52:10 arch-m1 systemd[1]: Started OpenSSH Daemon.
> systemctl is-active sshd.service
active
```

## Controlled failure

```sh
> sudo systemctl stop sshd.service
> systemctl is-active sshd.service
inactive
```

## Failure evidence (logs)

```sh
> sudo journalctl -u sshd.service -b --since "2 min ago" -n 50 --no-pager
Feb 16 20:02:34 arch-m1 systemd[1]: Stopping OpenSSH Daemon...
Feb 16 20:02:34 arch-m1 sshd[363]: Received signal 15; terminating.
Feb 16 20:02:34 arch-m1 systemd[1]: sshd.service: Deactivated successfully.
Feb 16 20:02:34 arch-m1 systemd[1]: Stopped OpenSSH Daemon.
```

## Recovery

```sh
> sudo systemctl start sshd.service
> systemctl is-active sshd.service
active
```

## Recovery evidence (logs + status)

```sh
> sudo journalctl -u sshd.service -b --since "2 min ago" -n 80 --no-pager
Feb 16 20:02:34 arch-m1 systemd[1]: Stopping OpenSSH Daemon...
Feb 16 20:02:34 arch-m1 sshd[363]: Received signal 15; terminating.
Feb 16 20:02:34 arch-m1 systemd[1]: sshd.service: Deactivated successfully.
Feb 16 20:02:34 arch-m1 systemd[1]: Stopped OpenSSH Daemon.
Feb 16 20:03:53 arch-m1 systemd[1]: Starting OpenSSH Daemon...
Feb 16 20:03:53 arch-m1 sshd[972]: Server listening on 0.0.0.0 port 22.
Feb 16 20:03:53 arch-m1 sshd[972]: Server listening on :: port 22.
Feb 16 20:03:53 arch-m1 systemd[1]: Started OpenSSH Daemon.
> systemctl status sshd.service --no-pager
● sshd.service - OpenSSH Daemon
     Loaded: loaded (/usr/lib/systemd/system/sshd.service; enabled; preset: disabled)
     Active: active (running) since Mon 2026-02-16 20:03:53 CET; 46s ago
 Invocation: ac265230659f42299bdc0b7998cffed1
       Docs: man:sshd(8)
             man:sshd_config(5)
   Main PID: 972 (sshd)
      Tasks: 1 (limit: 2268)
     Memory: 1.3M (peak: 1.7M)
        CPU: 6ms
     CGroup: /system.slice/sshd.service
             └─972 "sshd: /usr/bin/sshd -D [listener] 0 of 10-100 startups"

Feb 16 20:03:53 arch-m1 systemd[1]: Starting OpenSSH Daemon...
Feb 16 20:03:53 arch-m1 sshd[972]: Server listening on 0.0.0.0 port 22.
Feb 16 20:03:53 arch-m1 sshd[972]: Server listening on :: port 22.
Feb 16 20:03:53 arch-m1 systemd[1]: Started OpenSSH Daemon.
```

## What I learned

- `systemctl stop/start` changes unit state and is reflected in
  `systemctl status/is-active`.
- `journalctl -u <unit> -b` reliably narrows logs to one unit in the current
  boot.

Why these commands are “canonical”: `systemctl start/stop/status` are standard
systemd operations and `journalctl` is the standard interface to query the
systemd journal with unit filtering.
