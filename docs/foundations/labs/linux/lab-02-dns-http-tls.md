# Lab 2 - DNS vs HTTP vs TLS: isolate the failure

## Goal

Quickly determine whether a connectivity issue is DNS, routing, TCP, TLS, or
the application.

## Environment

- Host: macOS 26.3
- Hypervisor: UTM
- VM: Arch Linux (arch-m1) kernel 6.17.8-1-aarch64-ARCH>
- Network: host wifi
- Necessary packages: bind (dig), gnu-netcat (nc)

## 0) Baseline: IP + route

```sh
[root@arch-m1 ~]# ip a
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host noprefixroute
       valid_lft forever preferred_lft forever
2: enp0s1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 16:7c:df:f1:fc:de brd ff:ff:ff:ff:ff:ff
    altname enx167cdff1fcde
    inet 192.168.178.45/24 metric 1024 brd 192.168.178.255 scope global dynamic enp0s1
       valid_lft 861869sec preferred_lft 861869sec
    inet 192.168.178.47/24 brd 192.168.178.255 scope global secondary dynamic noprefixroute enp0s1
       valid_lft 861869sec preferred_lft 861869sec
    inet6 2003:e4:df40:2800:fe01:7e5b:ff9a:f5de/64 scope global dynamic noprefixroute
       valid_lft 6755sec preferred_lft 1355sec
    inet6 fdb7:5bd9:a39:0:42a8:c738:c114:6ce2/64 scope global dynamic noprefixroute
       valid_lft 6755sec preferred_lft 3155sec
    inet6 2003:e4:df40:2800:147c:dfff:fef1:fcde/64 scope global dynamic mngtmpaddr noprefixroute
       valid_lft 6755sec preferred_lft 1355sec
    inet6 fdb7:5bd9:a39:0:147c:dfff:fef1:fcde/64 scope global dynamic mngtmpaddr noprefixroute
       valid_lft 6755sec preferred_lft 3155sec
    inet6 fe80::e810:2768:b14b:30c1/64 scope link noprefixroute
       valid_lft forever preferred_lft forever
[root@arch-m1 ~]# ip route
default via 192.168.178.1 dev enp0s1 proto dhcp src 192.168.178.47 metric 100
default via 192.168.178.1 dev enp0s1 proto dhcp src 192.168.178.45 metric 1024
192.168.178.0/24 dev enp0s1 proto kernel scope link src 192.168.178.47 metric 100
192.168.178.0/24 dev enp0s1 proto kernel scope link src 192.168.178.45 metric 1024
192.168.178.1 dev enp0s1 proto dhcp scope link src 192.168.178.45 metric 1024
192.168.178.7 dev enp0s1 proto dhcp scope link src 192.168.178.45 metric 1024
[root@arch-m1 ~]#
```

## 1) Can I reach the internet without DNS?

```sh
[root@arch-m1 ~]# ping -c 1 1.1.1.1
PING 1.1.1.1 (1.1.1.1) 56(84) bytes of data.
64 bytes from 1.1.1.1: icmp_seq=1 ttl=56 time=10.9 ms

--- 1.1.1.1 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 10.922/10.922/10.922/0.000 ms
```

Expected: replies. If this fails, suspect routing/firewall/VPN.

## 2) DNS resolution (simple)

```sh
[root@arch-m1 ~]# dig jevops.de +short
15.197.162.184
[root@arch-m1 ~]# dig AAAA jevops.de +short
```

AAAA record didn't return anything as expected.

## 3) DNS resolution (system resolver view)

```sh
[root@arch-m1 ~]# resolvectl status
Global
           Protocols: +LLMNR +mDNS -DNSOverTLS DNSSEC=no/unsupported
    resolv.conf mode: uplink
  Current DNS Server: 9.9.9.9#dns.quad9.net
Fallback DNS Servers: 9.9.9.9#dns.quad9.net 2620:fe::9#dns.quad9.net 1.1.1.1#cloudflare-dns.com 2606:4700:4700::1111#cloudflare-dns.com
                      8.8.8.8#dns.google 2001:4860:4860::8888#dns.google

Link 2 (enp0s1)
    Current Scopes: DNS LLMNR/IPv4 LLMNR/IPv6
         Protocols: +DefaultRoute +LLMNR -mDNS -DNSOverTLS DNSSEC=no/unsupported
Current DNS Server: 192.168.178.7
       DNS Servers: 192.168.178.7 fd00::be24:11ff:fea6:4c5b
     Default Route: yes
[root@arch-m1 ~]# resolvectl query jevops.de
jevops.de: 15.197.162.184                      -- link: enp0s1

-- Information acquired via protocol DNS in 88.7ms.
-- Data is authenticated: no; Data was acquired via local or encrypted transport: no
-- Data from: network
```

If resolvectl is not available, record:

```sh
[root@arch-m1 ~]# cat /etc/resolv.conf
# This is /run/systemd/resolve/resolv.conf managed by man:systemd-resolved(8).
# Do not edit.
#
# This file might be symlinked as /etc/resolv.conf. If you're looking at
# /etc/resolv.conf and seeing this text, you have followed the symlink.
#
# This is a dynamic resolv.conf file for connecting local clients directly to
# all known uplink DNS servers. This file lists all configured search domains.
#
# Third party programs should typically not access this file directly, but only
# through the symlink at /etc/resolv.conf. To manage man:resolv.conf(5) in a
# different way, replace this symlink by a static file or a different symlink.
#
# See man:systemd-resolved.service(8) for details about the supported modes of
# operation for /etc/resolv.conf.

nameserver 192.168.178.7
nameserver fd00::be24:11ff:fea6:4c5b
search .
[root@arch-m1 ~]# getent ahosts jevops.de
15.197.162.184  STREAM jevops.de
15.197.162.184  DGRAM
15.197.162.184  RAW
```

## 4) DNS chain (authoritative trace)

```sh
[root@arch-m1 ~]# dig jevops.de +trace

; <<>> DiG 9.20.18 <<>> jevops.de +trace
;; global options: +cmd
.                       3589    IN      NS      l.root-servers.net.
.                       3589    IN      NS      m.root-servers.net.
.                       3589    IN      NS      a.root-servers.net.
.                       3589    IN      NS      b.root-servers.net.
.                       3589    IN      NS      c.root-servers.net.
.                       3589    IN      NS      d.root-servers.net.
.                       3589    IN      NS      e.root-servers.net.
.                       3589    IN      NS      f.root-servers.net.
.                       3589    IN      NS      g.root-servers.net.
.                       3589    IN      NS      h.root-servers.net.
.                       3589    IN      NS      i.root-servers.net.
.                       3589    IN      NS      j.root-servers.net.
.                       3589    IN      NS      k.root-servers.net.
.                       3589    IN      RRSIG   NS 8 0 518400 20260301170000 20260216160000 21831 . kzuQ0twnUcvauZggSskOD793a3848i4+wNFySzQ2IBbXcVFEGAyIdw9i 1IfwhXCfSH5WTlBchF0mPG7dY9GU/oa9R2jJGQLe4qyOXolYZgXXHBXr I4GMM2u7U9+OYBQgVOpLYZbboHgujFZTd+SSJvuywH4VbI0BAXlPRZte qEoR8ZB8qpQM2ZzesFWKKS5SSUwS9ZI7HScpuSD28UTHb0fNsgKiZBpl WmDVhF6nv9H8sE7IQxKLb2Fz55gdvMlh3P+bQCvB4cQIFAJ20ZUyNqCE rev7FSZYN4cDByxqnlahY746tsN5L08ZC9AEjiuZ37JVM2YI0bOljFan sDEfvQ==
;; Received 525 bytes from 192.168.178.7#53(192.168.178.7) in 6 ms

de.                     172800  IN      NS      a.nic.de.
de.                     172800  IN      NS      f.nic.de.
de.                     172800  IN      NS      l.de.net.
de.                     172800  IN      NS      n.de.net.
de.                     172800  IN      NS      s.de.net.
de.                     172800  IN      NS      z.nic.de.
de.                     86400   IN      DS      26755 8 2 F341357809A5954311CCB82ADE114C6C1D724A75C0395137AA397803 5425E78D
de.                     86400   IN      RRSIG   DS 8 1 86400 20260301170000 20260216160000 21831 . WpsU8XCMsV2c74yQbepgkxCLg+XfDH8XhhRfBv98Itt8/JF245wpHz+W j0gnHRM3Z82JNCifGmT/6PAdq6FuBbioYOuk6gsY7zV1d20QHVVxnb8K yoStQ9FvZjtye1Dc2at6Qt4AyKwQhbH0Dbwl+ijMTHpvGPYs+sUumSHl yVoKey4VYZcv9pRSPfxJeeyclZGSi6E/IKkTdQ8fSfGBLwabqMeoVoVJ jmOoKApZ+IcfoiJxGpz6SjyPp/eOr3RCHnMRyGBWwHw1c0IR0zMmEZjy QtgY1rrxur8kQy+m+1UR11xifJhpsecSTzFMBpb47+9TDU2vC2b2M0Id KfRyHw==
;; Received 743 bytes from 2001:500:9f::42#53(l.root-servers.net) in 23 ms

jevops.de.              86400   IN      NS      launch1.spaceship.net.
jevops.de.              86400   IN      NS      launch2.spaceship.net.
jevops.de.              86400   IN      DS      12702 13 2 2E9CFB6581AC04CB307928791C3C1BD93F46FA57C26B8E30EC960D09 D34CEA53
jevops.de.              86400   IN      RRSIG   DS 8 2 86400 20260301233344 20260215220344 14058 de. ByUvSm6AkE/jg9ZJlYaNraxjTJ6jeLAdeUkgD3N3ctN66xZFOgPJtb5W PqVc/dhyyxXZC4OvqpKS5i9w0G0hak2+AU7jWAXDbKTqXQvG0LkSZkCy fcYwJAXF3kzeHHvV8zu4U8V+fedbTWrr5YBaGVLl37ixRATpjf+Iuy47 cmc=
;; Received 305 bytes from 2a02:568:0:2::53#53(f.nic.de) in 17 ms

jevops.de.              300     IN      RRSIG   A 13 2 300 20260226000000 20260205000000 43443 jevops.de. GrCfrcLxWlzoiDbuDJKNq5UlP9Xsfn5QxJ1exoSvikmZnSavvqSMedHD NFw6cSVMEOU9DPFFXJo5F8zYibJaIg==
jevops.de.              300     IN      A       15.197.162.184
;; Received 159 bytes from 162.159.27.32#53(launch2.spaceship.net) in 18 ms
```

## 5) TCP reachability (is 443 reachable?)

```sh
[root@arch-m1 ~]# nc -vz jevops.de 443
jevops.de [15.197.162.184] 443 (https) open
[root@arch-m1 ~]# # Alternative without nc:
[root@arch-m1 ~]# curl -vI https://jevops.de --connect-timeout 5
* Host jevops.de:443 was resolved.
* IPv6: (none)
* IPv4: 15.197.162.184
*   Trying 15.197.162.184:443...
* ALPN: curl offers h2,http/1.1
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
* SSL Trust Anchors:
*   CAfile: /etc/ssl/certs/ca-certificates.crt
* TLSv1.3 (IN), TLS handshake, Server hello (2):
* TLSv1.3 (IN), TLS change cipher, Change cipher spec (1):
* TLSv1.3 (IN), TLS handshake, Encrypted Extensions (8):
* TLSv1.3 (IN), TLS handshake, Certificate (11):
* TLSv1.3 (IN), TLS handshake, CERT verify (15):
* TLSv1.3 (IN), TLS handshake, Finished (20):
* TLSv1.3 (OUT), TLS change cipher, Change cipher spec (1):
* TLSv1.3 (OUT), TLS handshake, Finished (20):
* SSL connection using TLSv1.3 / TLS_AES_256_GCM_SHA384 / X25519MLKEM768 / RSASSA-PSS
* ALPN: server accepted http/1.1
* Server certificate:
*   subject: CN=*.jevops.de
*   start date: Feb 16 00:20:56 2026 GMT
*   expire date: May 17 00:20:55 2026 GMT
*   issuer: C=US; O=Let's Encrypt; CN=R12
*   Certificate level 0: Public key type RSA (2048/112 Bits/secBits), signed using sha256WithRSAEncryption
*   Certificate level 1: Public key type RSA (2048/112 Bits/secBits), signed using sha256WithRSAEncryption
*   Certificate level 2: Public key type RSA (4096/152 Bits/secBits), signed using sha256WithRSAEncryption
*   subjectAltName: "jevops.de" matches cert's "jevops.de"
* SSL certificate verified via OpenSSL.
* Established connection to jevops.de (15.197.162.184 port 443) from 192.168.178.47 port 53600
* using HTTP/1.x
> HEAD / HTTP/1.1
> Host: jevops.de
> User-Agent: curl/8.17.0
> Accept: */*
>
* TLSv1.3 (IN), TLS handshake, Newsession Ticket (4):
* TLSv1.3 (IN), TLS handshake, Newsession Ticket (4):
* Request completely sent off
< HTTP/1.1 302 Moved Temporarily
HTTP/1.1 302 Moved Temporarily
< Date: Mon, 16 Feb 2026 22:35:55 GMT
Date: Mon, 16 Feb 2026 22:35:55 GMT
< Content-Type: text/html
Content-Type: text/html
< Content-Length: 55
Content-Length: 55
< Connection: keep-alive
Connection: keep-alive
< z-urlredirect-redirected-for: 1335318262
z-urlredirect-redirected-for: 1335318262
< Location: https://github.com/viprapp/jevops
Location: https://github.com/viprapp/jevops
<

* Connection #0 to host jevops.de:443 left intact
```

## 6) HTTP vs HTTPS behavior

HTTPS can be seen in 5) above

```sh
[root@arch-m1 ~]# curl -vI http://jevops.de
* Host jevops.de:80 was resolved.
* IPv6: (none)
* IPv4: 15.197.162.184
*   Trying 15.197.162.184:80...
* Established connection to jevops.de (15.197.162.184 port 80) from 192.168.178.47 port 49808
* using HTTP/1.x
> HEAD / HTTP/1.1
> Host: jevops.de
> User-Agent: curl/8.17.0
> Accept: */*
>
* Request completely sent off
< HTTP/1.1 302 Moved Temporarily
HTTP/1.1 302 Moved Temporarily
< Date: Mon, 16 Feb 2026 22:37:22 GMT
Date: Mon, 16 Feb 2026 22:37:22 GMT
< Content-Length: 55
Content-Length: 55
< Connection: keep-alive
Connection: keep-alive
< z-urlredirect-redirected-for: 1335318262
z-urlredirect-redirected-for: 1335318262
< Location: https://github.com/viprapp/jevops
Location: https://github.com/viprapp/jevops
< Content-type: text/html
Content-type: text/html
<

* Connection #0 to host jevops.de:80 left intact
```

- HTTP status codes 302 as expected
- redirecting to GH repo <https://github.com/viprapp/jevops>
- no TLS errors were found, looks good

## 7) TLS inspection (when HTTPS is weird)

```sh
[root@arch-m1 ~]# openssl s_client -connect jevops.de:443 -servername jevops.de -brief </dev/null
Connecting to 15.197.162.184
CONNECTION ESTABLISHED
Protocol version: TLSv1.3
Ciphersuite: TLS_AES_256_GCM_SHA384
Peer certificate: CN=*.jevops.de
Hash used: SHA256
Signature type: rsa_pss_rsae_sha256
Verification: OK
Negotiated TLS1.3 group: X25519MLKEM768
DONE
```

## 8) Local listeners (when debugging a server)

```sh
[root@arch-m1 ~]# ss -tulpn
Netid  State   Recv-Q  Send-Q                        Local Address:Port     Peer Address:Port  Process
udp    UNCONN  0       0                                127.0.0.54:53            0.0.0.0:*      users:(("systemd-resolve",pid=261,fd=24))
udp    UNCONN  0       0                             127.0.0.53%lo:53            0.0.0.0:*      users:(("systemd-resolve",pid=261,fd=22))
udp    UNCONN  0       0                     192.168.178.45%enp0s1:68            0.0.0.0:*      users:(("systemd-network",pid=273,fd=24))
udp    UNCONN  0       0                                   0.0.0.0:5353          0.0.0.0:*      users:(("systemd-resolve",pid=261,fd=17))
udp    UNCONN  0       0                                   0.0.0.0:5355          0.0.0.0:*      users:(("systemd-resolve",pid=261,fd=13))
udp    UNCONN  0       0                                      [::]:5353             [::]:*      users:(("systemd-resolve",pid=261,fd=18))
udp    UNCONN  0       0                                      [::]:5355             [::]:*      users:(("systemd-resolve",pid=261,fd=15))
udp    UNCONN  70880   0        [fe80::e810:2768:b14b:30c1]%enp0s1:546              [::]:*      users:(("NetworkManager",pid=334,fd=28))
udp    UNCONN  0       0        [fe80::e810:2768:b14b:30c1]%enp0s1:546              [::]:*      users:(("systemd-network",pid=273,fd=26))
tcp    LISTEN  0       4096                             127.0.0.54:53            0.0.0.0:*      users:(("systemd-resolve",pid=261,fd=25))
tcp    LISTEN  0       4096                          127.0.0.53%lo:53            0.0.0.0:*      users:(("systemd-resolve",pid=261,fd=23))
tcp    LISTEN  0       128                                 0.0.0.0:22            0.0.0.0:*      users:(("sshd",pid=358,fd=6))
tcp    LISTEN  0       4096                                0.0.0.0:5355          0.0.0.0:*      users:(("systemd-resolve",pid=261,fd=14))
tcp    LISTEN  0       128                                    [::]:22               [::]:*      users:(("sshd",pid=358,fd=7))
tcp    LISTEN  0       4096                                   [::]:5355             [::]:*      users:(("systemd-resolve",pid=261,fd=16))
[root@arch-m1 ~]# ss -tn state established
Recv-Q               Send-Q                               Local Address:Port                               Peer Address:Port
```

## Decision tree (what I concluded)

- If IP ping fails -> route/VPN/firewall issue.
- If IP ping works but DNS lookup fails -> resolver configuration issue.
- If DNS works but TCP connect to 443 fails -> firewall/routing/remote port issue.
- If TCP connect works but HTTPS fails -> TLS/certs/SNI/time issue.
- If HTTPS works but app returns 4xx/5xx -> application/config/logs.

### Notes on tools (canonical docs)

- `ip route` / `ip a` are iproute2 staples.
- `ss` is the modern socket tool (netstat replacement).
- `resolvectl` is for systemd-resolved environments.
- `dig` is the modern DNS lookup tool. (`getent` and `nslookup` are alternatives)

## “Done” checklist for this lab

- [x] `ip a` + `ip route` included
- [x] DNS results shown (at least `dig ... +short`)
- [x] One HTTP and one HTTPS request captured (`curl -vI`)
- [x] Decision tree filled with what happened on your system
