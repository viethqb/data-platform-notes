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
#ssh user: admin(root)/admin
```

## ssh_key
```
ssh-keygen
ssh-copy-id root@172.25.1.2
ssh-copy-id root@172.25.1.3
ssh-copy-id root@172.25.1.4
ssh-copy-id root@172.25.1.5
ssh-copy-id root@172.25.1.6
ssh-copy-id root@172.25.1.7
ssh-copy-id root@172.25.1.8 
```

## Change /etc/machine-id
```bash
ssh root@172.25.1.2 'echo $(uuidgen) > /etc/machine-id && apt-get update && apt-get install -y haproxy'
ssh root@172.25.1.3 'echo $(uuidgen) > /etc/machine-id'
ssh root@172.25.1.4 'echo $(uuidgen) > /etc/machine-id'
ssh root@172.25.1.5 'echo $(uuidgen) > /etc/machine-id'
ssh root@172.25.1.6 'echo $(uuidgen) > /etc/machine-id'
ssh root@172.25.1.7 'echo $(uuidgen) > /etc/machine-id'
ssh root@172.25.1.8 'echo $(uuidgen) > /etc/machine-id'
```



## Add the following lines to the end of the /etc/haproxy/haproxy.cfg

```
ssh root@172.25.1.2

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
    server master-1 172.25.1.3:6443 check fall 3 rise 2
    server master-2 172.25.1.4:6443 check fall 3 rise 2
    server master-3 172.25.1.5:6443 check fall 3 rise 2

listen stats
   bind *:9999
   mode http
   stats enable
   stats uri /
EOF
```

## Start haproxy.service

```
systemctl start haproxy.service
systemctl status haproxy.service
```

## Install k3s

### Master-1

```bash
curl -sfL https://get.k3s.io | K3S_TOKEN=DC87A250BCBA499994CF808CEADD1BCC INSTALL_K3S_VERSION=v1.29.4+k3s1 sh -s - server \
    --cluster-init \
    --disable traefik --disable servicelb \
    --tls-san=172.25.1.2
```

### Master-2, 3

```bash
curl -sfL https://get.k3s.io | K3S_TOKEN=DC87A250BCBA499994CF808CEADD1BCC INSTALL_K3S_VERSION=v1.29.4+k3s1 sh -s - server \
    --server https://172.25.1.3:6443 \
    --disable traefik --disable servicelb \
    --tls-san=172.25.1.2
```

### Worker-1, 2, 3
```bash
curl -sfL https://get.k3s.io | K3S_TOKEN=DC87A250BCBA499994CF808CEADD1BCC INSTALL_K3S_VERSION=v1.29.4+k3s1 sh -s - agent --server https://172.25.1.2:6443
```

### Copy kubectl config

```bash
scp root@172.25.1.3:/etc/rancher/k3s/k3s.yaml .
sed -i -e 's/127.0.0.1/172.25.1.2/g' ./k3s.yaml

k get no --kubeconfig ./k3s.yaml
```

### install Nginx ingress

```
export KUBECONFIG=./k3s.yaml
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx --set controller.hostNetwork=true,controller.service.type="",controller.kind=DaemonSet --namespace ingress-nginx --version 4.10.1 --create-namespace --debug
```

### Test Nginx Ingress

```
helm upgrade --install minio -n minio -f ../../charts/minio/minio-values.yaml ../../charts/minio --create-namespace --debug

# add new row to /etc/hosts 
# 172.25.1.3  minio.lakehouse.local
# go to http://minio.lakehouse.local
```

### Install Longhorn
```
# Longhorn not work trên môi trường container. Thử  lại trên môi trường VM
helm repo add longhorn https://charts.longhorn.io
helm repo update
helm upgrade --install longhorn longhorn/longhorn --namespace longhorn-system --create-namespace --version 1.6.1 --debug

# persistence.defaultClassReplicaCount: 3
# defaultSettings.defaultDataPath: /var/lib/longhorn/

ssh root@172.25.1.3 'mount --make-rshared /'
ssh root@172.25.1.4 'mount --make-rshared /'
ssh root@172.25.1.5 'mount --make-rshared /'
ssh root@172.25.1.6 'mount --make-rshared /'
ssh root@172.25.1.7 'mount --make-rshared /'
ssh root@172.25.1.8 'mount --make-rshared /'
```