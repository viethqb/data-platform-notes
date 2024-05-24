#!/bin/bash

## !IMPORTANT ##
#
echo "[TASK 1] Update /etc/hosts file"
cat >>/etc/hosts<<EOF
172.16.16.100   loadbalancer
172.16.16.101   kmaster1
172.16.16.102   kmaster2
172.16.16.103   kmaster3
172.16.16.201   kworker1
172.16.16.202   kworker2
172.16.16.203   kworker3
EOF

echo "[TASK 2] Install HAProxy"
apt-get update && apt-get install -y haproxy

echo "[TASK 3] Update HAProxy configs /etc/haproxy/haproxy.cfg"
cat >>/etc/haproxy/haproxy.cfg<<EOF

frontend kubernetes-frontend
    bind *:6443
    mode tcp
    option tcplog
    default_backend kubernetes-backend

backend kubernetes-backend
    mode tcp
    option tcp-check
    balance roundrobin
    server kmaster1 kmaster1:6443 check fall 3 rise 2
    server kmaster2 kmaster2:6443 check fall 3 rise 2
    server kmaster3 kmaster3:6443 check fall 3 rise 2
EOF

echo "[TASK 4] Restart HAProxy service"
systemctl restart haproxy.service
