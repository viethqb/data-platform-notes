## Install Sysbox Runtime

```bash
## https://github.com/nestybox/sysbox/blob/master/docs/user-guide/install-package.md#installing-sysbox
wget https://downloads.nestybox.com/sysbox/releases/v0.6.4/sysbox-ce_0.6.4-0.linux_amd64.deb
docker rm $(docker ps -a -q) -f
sudo apt-get install jq
sudo apt-get install ./sysbox-ce_0.6.4-0.linux_amd64.deb
```
## Start Docker Container Like VM
```bash
docker-compose up -d
docker ps -q | xargs -n 1 docker inspect --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}} {{ .Name }}' | sed 's/ \// /'
# ssh user: admin(root)/admin
# 172.25.2.5 doris-3
# 172.25.2.4 doris-2
# 172.25.2.3 doris-1
```
## Add SSH Key And Change Machine Id
```bash
ssh-keygen
ssh-copy-id root@172.25.2.3
ssh-copy-id root@172.25.2.4
ssh-copy-id root@172.25.2.5
ssh root@172.25.2.3 'echo $(uuidgen) > /etc/machine-id'
ssh root@172.25.2.4 'echo $(uuidgen) > /etc/machine-id'
ssh root@172.25.2.5 'echo $(uuidgen) > /etc/machine-id'
```

## Install Doris

```bash
root@doris-1:~# curl -fsSL https://get.docker.com -o get-docker.sh
root@doris-1:~# bash ./get-docker.sh 
root@doris-1:~# systemctl enable docker --now
root@doris-1:~# docker compose -f ./docker-compose.doris-1.yaml up -d

root@doris-2:~# curl -fsSL https://get.docker.com -o get-docker.sh
root@doris-2:~# bash ./get-docker.sh 
root@doris-2:~# systemctl enable docker --now
root@doris-2:~# docker compose -f ./docker-compose.doris-2.yaml up -d

root@doris-3:~# curl -fsSL https://get.docker.com -o get-docker.sh
root@doris-3:~# bash ./get-docker.sh 
root@doris-3:~# systemctl enable docker --now
root@doris-3:~# docker compose -f ./docker-compose.doris-3.yaml up -d
```
