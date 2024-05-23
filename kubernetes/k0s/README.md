### Start Docker Container Like VM

```bash
bash ./multipass_create_instances.sh 

# Name                    State             IPv4             Image
# k0s-loadbalancer        Running           10.4.165.85      Ubuntu 22.04 LTS
# k0s-master-1            Running           10.4.165.45      Ubuntu 22.04 LTS
# k0s-master-2            Running           10.4.165.207     Ubuntu 22.04 LTS
# k0s-master-3            Running           10.4.165.154     Ubuntu 22.04 LTS
# k0s-worker-1            Running           10.4.165.199     Ubuntu 22.04 LTS
# k0s-worker-2            Running           10.4.165.114     Ubuntu 22.04 LTS
# k0s-worker-3            Running           10.4.165.245     Ubuntu 22.04 LTS
```

## Install k0sctl
```bash
go install github.com/k0sproject/k0sctl@latest
k0sctl version                                                                                                                        ─╯

# version: v0.17.8
# commit: unknown
```

## k0sctl.yaml
```yaml
apiVersion: k0sctl.k0sproject.io/v1beta1
kind: Cluster
metadata:
  name: k0s-cluster
spec:
  hosts:
    - ssh:
        address: 10.4.165.45
        user: k0s
        port: 22
        keyPath: ~/.ssh/id_rsa
      role: controller
    - ssh:
        address: 10.4.165.207
        user: k0s
        port: 22
        keyPath: ~/.ssh/id_rsa
      role: controller
    - ssh:
        address: 10.4.165.154
        user: k0s
        port: 22
        keyPath: ~/.ssh/id_rsa
      role: controller
    - ssh:
        address: 10.4.165.199
        user: k0s
        port: 22
        keyPath: ~/.ssh/id_rsa
      role: worker
    - ssh:
        address: 10.4.165.114
        user: k0s
        port: 22
        keyPath: ~/.ssh/id_rsa
      role: worker
    - ssh:
        address: 10.4.165.245
        user: k0s
        port: 22
        keyPath: ~/.ssh/id_rsa
      role: worker
  k0s:
    version: v1.30.0+k0s.0
    config:
      spec:
        api:
          externalAddress: 10.4.165.85
          sans:
            - 10.4.165.85

```
## Install 
## install HAProxy

```
ssh k0s@10.4.165.85
sudo -i
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
    server k0s-controller1 10.4.165.45:6443 check fall 3 rise 2
    server k0s-controller2 10.4.165.207:6443 check fall 3 rise 2
    server k0s-controller3 10.4.165.154:6443 check fall 3 rise 2
backend konnectivity_backend
    mode tcp
    option tcp-check
    balance roundrobin
    server k0s-controller1 10.4.165.45:8132 check fall 3 rise 2
    server k0s-controller2 10.4.165.207:8132 check fall 3 rise 2
    server k0s-controller3 10.4.165.154:8132 check fall 3 rise 2
backend controllerJoinAPI_backend
    mode tcp
    option tcp-check
    balance roundrobin
    server k0s-controller1 10.4.165.45:9443 check fall 3 rise 2
    server k0s-controller2 10.4.165.207:9443 check fall 3 rise 2
    server k0s-controller3 10.4.165.154:9443 check fall 3 rise 2

listen stats
   bind *:9999
   mode http
   stats enable
   stats uri /

```

## Start haproxy.service

```
systemctl enable haproxy
systemctl restart haproxy
systemctl status haproxy.service
```
## install k0s
```bash
k0sctl apply -c k0sctl.yaml
k0sctl kubeconfig > kubeconfig

kubectl --kubeconfig kubeconfig get no -owide
# NAME           STATUS   ROLES    AGE    VERSION       INTERNAL-IP    EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION       CONTAINER-RUNTIME
# k0s-worker-1   Ready    <none>   101s   v1.30.0+k0s   10.4.165.199   <none>        Ubuntu 22.04.4 LTS   5.15.0-107-generic   containerd://1.7.16
# k0s-worker-2   Ready    <none>   101s   v1.30.0+k0s   10.4.165.114   <none>        Ubuntu 22.04.4 LTS   5.15.0-107-generic   containerd://1.7.16
# k0s-worker-3   Ready    <none>   96s    v1.30.0+k0s   10.4.165.245   <none>        Ubuntu 22.04.4 LTS   5.15.0-107-generic   containerd://1.7.16
```

## Install Longhorn sc

```bash
export KUBECONFIG=./kubeconfig
helm repo add longhorn https://charts.longhorn.io
helm repo update
helm upgrade --install longhorn longhorn/longhorn --set persistence.defaultClassReplicaCount=1 --namespace longhorn-system --create-namespace --version 1.6.1 --debug

k -n longhorn-system get po

# persistence.defaultClassReplicaCount: 3
# defaultSettings.defaultDataPath: /var/lib/longhorn/
```

### install Nginx Ingress

```bash
export KUBECONFIG=./kubeconfig
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx --set controller.hostNetwork=true,controller.service.type="",controller.kind=DaemonSet --namespace ingress-nginx --version 4.10.1 --create-namespace --debug

k -n ingress-nginx get po -owide
# NAME                             READY   STATUS    RESTARTS   AGE   IP             NODE           NOMINATED NODE   READINESS GATES
# ingress-nginx-controller-84bfj   1/1     Running   0          12m   10.4.165.245   k0s-worker-3   <none>           <none>
# ingress-nginx-controller-f282p   1/1     Running   0          12m   10.4.165.114   k0s-worker-2   <none>           <none>
# ingress-nginx-controller-zdlcn   1/1     Running   0          12m   10.4.165.199   k0s-worker-1   <none>           <none>
```

## TEST

```bash
helm upgrade --install minio -n minio -f ../../charts/minio/minio-values.yaml ../../charts/minio --create-namespace --debug
k -n minio get po
# NAME                    READY   STATUS    RESTARTS   AGE
# minio-544bf66fb-nkn9w   1/1     Running   0          2m17s

k -n minio get pvc
# NAME    STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
# minio   Bound    pvc-2322fba2-7189-44ff-8287-1c15e07fa514   8Gi        RWO            longhorn       <unset>                 112s

k -n minio get ing
# NAME    CLASS   HOSTS                   ADDRESS        PORTS   AGE
# minio   nginx   minio.lakehouse.local   10.100.17.10   80      61s

# add new row to /etc/hosts 
# 10.4.165.245  minio.lakehouse.local
# go to http://minio.lakehouse.local (admin/password)
```

## Destroy

```bash
multipass list
multipass delete --all --purge
```
