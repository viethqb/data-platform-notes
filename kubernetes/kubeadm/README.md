## Start VM

```bash
vagrant up 

ssh-copy-id root@172.16.16.100
ssh-copy-id root@172.16.16.101
ssh-copy-id root@172.16.16.102
ssh-copy-id root@172.16.16.103
ssh-copy-id root@172.16.16.201
ssh-copy-id root@172.16.16.202
ssh-copy-id root@172.16.16.203
```

## Install Loadbalancer
```bash
root@loadbalancer:~# bash loadbalancer.sh 
```

## Install Kubernetes Master
```bash
root@kmaster1:~# bash prepare_all_k8s_node.sh 
root@kmaster1:~# bash bootstrap_kmaster_1.sh 

# You can now join any number of the control-plane node running the following command on each as root:
#
#   kubeadm join 172.16.16.100:6443 --token yh7m40.3x1lsloo6xauqyj7 \
#         --discovery-token-ca-cert-hash sha256:ca9a0dc20d83c5628bb761cda891cef4c6da9aab3bf6667d6a5d831977c64742 \
#         --control-plane --certificate-key 1c69a134ef43074815918c214a99d7941162b8ef7cdb4fadeede0b6d33cd5d35
# Then you can join any number of worker nodes by running the following on each as root:
#
# kubeadm join 172.16.16.100:6443 --token yh7m40.3x1lsloo6xauqyj7 \
#         --discovery-token-ca-cert-hash sha256:ca9a0dc20d83c5628bb761cda891cef4c6da9aab3bf6667d6a5d831977c64742 

root@kmaster1:~# kubectl --kubeconfig=/etc/kubernetes/admin.conf get no -owide 
# NAME       STATUS   ROLES           AGE     VERSION   INTERNAL-IP     EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION      CONTAINER-RUNTIME
# kmaster1   Ready    control-plane   2m12s   v1.29.5   172.16.16.101   <none>        Ubuntu 22.04.3 LTS   5.15.0-91-generic   containerd://1.6.32

root@kmaster2:~# bash prepare_all_k8s_node.sh 
root@kmaster2:~# kubeadm join 172.16.16.100:6443 --token yh7m40.3x1lsloo6xauqyj7 \
        --discovery-token-ca-cert-hash sha256:ca9a0dc20d83c5628bb761cda891cef4c6da9aab3bf6667d6a5d831977c64742 \
        --control-plane --certificate-key 1c69a134ef43074815918c214a99d7941162b8ef7cdb4fadeede0b6d33cd5d35 --apiserver-advertise-address 172.16.16.102
# kubeadm reset cleanup-node
root@kmaster3:~# bash prepare_all_k8s_node.sh 
root@kmaster3:~# kubeadm join 172.16.16.100:6443 --token yh7m40.3x1lsloo6xauqyj7 \
        --discovery-token-ca-cert-hash sha256:ca9a0dc20d83c5628bb761cda891cef4c6da9aab3bf6667d6a5d831977c64742 \
        --control-plane --certificate-key 1c69a134ef43074815918c214a99d7941162b8ef7cdb4fadeede0b6d33cd5d35 --apiserver-advertise-address 172.16.16.103
root@kmaster3:~# mkdir -p $HOME/.kube
root@kmaster3:~# cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
root@kmaster3:~# chown $(id -u):$(id -g) $HOME/.kube/config
root@kmaster3:~# kubectl get nodes
```


## Install Kubernetes Worker

```bash
root@kworker1:~# bash prepare_all_k8s_node.sh 
root@kworker1:~# kubeadm join 172.16.16.100:6443 --token yh7m40.3x1lsloo6xauqyj7 \
        --discovery-token-ca-cert-hash sha256:ca9a0dc20d83c5628bb761cda891cef4c6da9aab3bf6667d6a5d831977c64742 

root@kworker2:~# bash prepare_all_k8s_node.sh 
root@kworker2:~# kubeadm join 172.16.16.100:6443 --token yh7m40.3x1lsloo6xauqyj7 \
        --discovery-token-ca-cert-hash sha256:ca9a0dc20d83c5628bb761cda891cef4c6da9aab3bf6667d6a5d831977c64742 

root@kworker3:~# bash prepare_all_k8s_node.sh 
root@kworker3:~# kubeadm join 172.16.16.100:6443 --token yh7m40.3x1lsloo6xauqyj7 \
        --discovery-token-ca-cert-hash sha256:ca9a0dc20d83c5628bb761cda891cef4c6da9aab3bf6667d6a5d831977c64742 
```

## Install kubernetes Components:

```bash
root@kmaster3:~# kubectl get nodes
# NAME       STATUS   ROLES           AGE    VERSION
# kmaster1   Ready    control-plane   151m   v1.29.5
# kmaster2   Ready    control-plane   72m    v1.29.5
# kmaster3   Ready    control-plane   58m    v1.29.5
# kworker1   Ready    <none>          12m    v1.29.5
# kworker2   Ready    <none>          8m1s   v1.29.5
# kworker3   Ready    <none>          3m2s   v1.29.5

root@kmaster3:~# curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
root@kmaster3:~# bash ./get_helm.sh 

# Install ingress nginx
root@kmaster3:~# helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
root@kmaster3:~# helm repo update
root@kmaster3:~# helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx --set controller.hostNetwork=true,controller.service.type="",controller.kind=DaemonSet --namespace ingress-nginx --version 4.10.1 --create-namespace --debug

# Install Longhorn sc
root@kmaster3:~# helm repo add longhorn https://charts.longhorn.io
root@kmaster3:~# helm repo update
root@kmaster3:~# helm upgrade --install longhorn longhorn/longhorn --set persistence.defaultClassReplicaCount=1 --namespace longhorn-system --create-namespace --version 1.6.1 --debug
root@kmaster3:~# kubectl -n longhorn-system get po

# Install Metric server
root@kmaster3:~# kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
root@kmaster3:~# kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'
root@kmaster3:~# kubectl top no
root@kmaster3:~# kubectl -n ingress-nginx top po
```

## destroy cluster

```bash
vagrant destroy -f
```
