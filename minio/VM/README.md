## Start VM

```bash
vagrant up 

# vboxmanage list hdds
# vboxmanage closemedium <UUID> --delete 
ssh-copy-id root@172.16.16.100
ssh-copy-id root@172.16.16.101
ssh-copy-id root@172.16.16.102
ssh-copy-id root@172.16.16.103
ssh-copy-id root@172.16.16.104
```

## Install MINIO

```bash
root@minio1:~# lsblk
# NAME                      MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
# loop0                       7:0    0  63.4M  1 loop /snap/core20/1974
# loop1                       7:1    0  53.3M  1 loop /snap/snapd/19457
# loop2                       7:2    0 111.9M  1 loop /snap/lxd/24322
# loop3                       7:3    0  63.9M  1 loop /snap/core20/2318
# sda                         8:0    0   128G  0 disk 
# ├─sda1                      8:1    0     1M  0 part 
# ├─sda2                      8:2    0     2G  0 part /boot
# └─sda3                      8:3    0   126G  0 part 
#   └─ubuntu--vg-ubuntu--lv 253:0    0    63G  0 lvm  /
# sdb                         8:16   0    20G  0 disk 
# sdc                         8:32   0    20G  0 disk 
# sdd                         8:48   0    20G  0 disk 
# sde                         8:64   0    20G  0 disk 

# => sdb, sdc, sdd, sde are the storage disk for minio.
# => mount sdb, sdc, sdd, sde to /data/minio/data-1, /data/minio/data-2, /data/minio/data-3, /minio/data-4

# 4 disk sdb, sdc, sdd, sde chưa có mount point
# Tạo các mount point
root@minio1:~# mkdir -p /data/minio/data-1
root@minio1:~# mkdir -p /data/minio/data-2
root@minio1:~# mkdir -p /data/minio/data-3
root@minio1:~# mkdir -p /data/minio/data-4
root@minio1:~# mkfs.xfs /dev/sdb
root@minio1:~# mkfs.xfs /dev/sdc
root@minio1:~# mkfs.xfs /dev/sdd
root@minio1:~# mkfs.xfs /dev/sde

# mount disk vào mountpoints
root@minio1:~# echo "/dev/sdb /data/minio/data-1 xfs defaults,noatime,nofail 0 0" >> /etc/fstab
root@minio1:~# echo "/dev/sdc /data/minio/data-2 xfs defaults,noatime,nofail 0 0" >> /etc/fstab
root@minio1:~# echo "/dev/sdd /data/minio/data-3 xfs defaults,noatime,nofail 0 0" >> /etc/fstab
root@minio1:~# echo "/dev/sde /data/minio/data-4 xfs defaults,noatime,nofail 0 0" >> /etc/fstab
root@minio1:~# mount -a
root@minio1:~# lsblk 
# NAME                      MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
# ...
# sdb                         8:16   0    20G  0 disk /data/minio/data-1
# sdc                         8:32   0    20G  0 disk /data/minio/data-2
# sdd                         8:48   0    20G  0 disk /data/minio/data-3
# sde                         8:64   0    20G  0 disk /data/minio/data-4

# Cài đặt docker
root@minio1:~# curl -fsSL https://get.docker.com -o get-docker.sh
root@minio1:~# sh get-docker.sh

# Cài đặt minio (chú ý sửa file docker-compose.yml tương ứng với từng node)
root@minio1:~# docker compose -f docker-compose.minio1.yaml up -d
root@minio1:~# docker logs -f minio1

# Chú ý khi start có thể log ra lỗi, bình tĩnh start 3 node con lại sẽ hết lỗi. Nếu vẫn còn lôi thì mới check tiếp.

# Làm tương tự với các node khác.
root@minio2:~# docker compose -f docker-compose.minio2.yaml up -d
root@minio2:~# docker logs -f minio2

root@minio3:~# docker compose -f docker-compose.minio3.yaml up -d
root@minio3:~# docker logs -f minio3

root@minio4:~# docker compose -f docker-compose.minio4.yaml up -d
root@minio4:~# docker logs -f minio4
```

## Install HAProxy

```bash
root@loadbalancer:~# apt-get update && apt-get install -y haproxy
root@loadbalancer:~# cat >>/etc/haproxy/haproxy.cfg<<EOF

frontend minio-frontend
    bind *:9000
    mode tcp
    option tcplog
    default_backend minio-backend

backend minio-backend
    mode tcp
    option tcp-check
    balance roundrobin
    server minio-1 172.16.16.101:9000 check fall 3 rise 2
    server minio-2 172.16.16.102:9000 check fall 3 rise 2
    server minio-3 172.16.16.103:9000 check fall 3 rise 2
    server minio-4 172.16.16.104:9000 check fall 3 rise 2
	
frontend minio-console-frontend
    bind *:9001
    mode tcp
    option tcplog
    default_backend minio-console-backend

backend minio-console-backend
    mode tcp
    option tcp-check
    balance roundrobin
    server minio-1 172.16.16.101:9001 check fall 3 rise 2
    server minio-2 172.16.16.102:9001 check fall 3 rise 2
    server minio-3 172.16.16.103:9001 check fall 3 rise 2
    server minio-4 172.16.16.104:9001 check fall 3 rise 2
EOF
root@loadbalancer:~# systemctl enable haproxy.service
root@loadbalancer:~# systemctl restart haproxy.service
```

## Install complete

```bash
# go to: http://172.16.16.100:9001/ 
# user: admin
# pass: password 
```