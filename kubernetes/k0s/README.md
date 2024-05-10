## Install sysbox runtime

```bash
## https://github.com/nestybox/sysbox/blob/master/docs/user-guide/install-package.md#installing-sysbox

wget https://downloads.nestybox.com/sysbox/releases/v0.6.4/sysbox-ce_0.6.4-0.linux_amd64.deb
docker rm $(docker ps -a -q) -f
sudo apt-get install jq
sudo apt-get install ./sysbox-ce_0.6.4-0.linux_amd64.deb
```

## Start docker container like VM

```bash
docker-compose up -d
docker ps -q | xargs -n 1 docker inspect --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}} {{ .Name }}' | sed 's/ \// /'
#ssh user: admin/admin
```

## Install k0sctl
```bash
go install github.com/k0sproject/k0sctl@v0.17.4
```

## ssh_key
```
ssh-keygen
ssh-copy-id admin@172.25.1.2
ssh-copy-id admin@172.25.1.3
ssh-copy-id admin@172.25.1.4
ssh-copy-id admin@172.25.1.5
ssh-copy-id admin@172.25.1.6
ssh-copy-id admin@172.25.1.7
ssh-copy-id admin@172.25.1.8 
```

## install HAProxy

```
ssh admin@172.25.1.2
apt update && apt install haproxy -y
```

## Add the following lines to the end of the /etc/haproxy/haproxy.cfg

```
frontend kubeAPI
    bind *:6443
    mode tcp
    option tcplog
    default_backend kubeAPI_backend
frontend konnectivity
    bind *:8132
    mode tcp
    option tcplog
    default_backend konnectivity_backend
frontend controllerJoinAPI
    bind *:9443
    mode tcp
    option tcplog
    default_backend controllerJoinAPI_backend

backend kubeAPI_backend
    mode tcp
    option tcp-check
    balance roundrobin
    server k0s-controller1 172.25.1.3:6443 check fall 3 rise 2
    server k0s-controller2 172.25.1.4:6443 check fall 3 rise 2
    server k0s-controller3 172.25.1.5:6443 check fall 3 rise 2
backend konnectivity_backend
    mode tcp
    option tcp-check
    balance roundrobin
    server k0s-controller1 172.25.1.3:8132 check fall 3 rise 2
    server k0s-controller2 172.25.1.4:8132 check fall 3 rise 2
    server k0s-controller3 172.25.1.5:8132 check fall 3 rise 2
backend controllerJoinAPI_backend
    mode tcp
    option tcp-check
    balance roundrobin
    server k0s-controller1 172.25.1.3:9443 check fall 3 rise 2
    server k0s-controller2 172.25.1.4:9443 check fall 3 rise 2
    server k0s-controller3 172.25.1.5:9443 check fall 3 rise 2

listen stats
   bind *:9000
   mode http
   stats enable
   stats uri /

```

## Start haproxy.service

```
systemctl start haproxy.service
systemctl status haproxy.service
```

env SSH_KNOWN_HOSTS=/dev/null k0sctl apply -c k0sctl.yaml

apt update
apt install uuid-runtime 
UUID=$(uuidgen)
echo "$UUID" > /etc/machine-id