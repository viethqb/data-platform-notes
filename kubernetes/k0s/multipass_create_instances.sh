#!/usr/bin/env bash
if ! command -v multipass &> /dev/null
then
    echo "multipass could not be found"
    echo "Check <https://github.com/canonical/multipass> on how to install it"
    exit
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# 3 VMs MASTER & 3 WORKER & 1 LB
NUMBER_OF_MASTER=${1:-3}
NUMBER_OF_WORKER=${1:-3}
echo "Create cloud-init to import ssh key..."

# https://github.com/canonical/multipass/issues/965#issuecomment-591284180
cat <<EOF > "${DIR}"/multipass-cloud-init.yml
---
users:
  - name: k0s
    sudo: ALL=(ALL) NOPASSWD:ALL
    shell: /usr/bin/bash
    ssh_authorized_keys:
      - $( cat "$(ls -1 ~/.ssh/id_*.pub | head -1)" )
packages:
  - open-iscsi
  - nfs-common
runcmd:
  - cp /etc/netplan/50-cloud-init.yaml /etc/netplan/50-cloud-init.yaml.bak
  - sed -i -e '13i\\            nameservers:' /etc/netplan/50-cloud-init.yaml
  - sed -i -e '14i\\                addresses:\ [8.8.8.8, 8.8.4.4]' /etc/netplan/50-cloud-init.yaml
  - netplan apply
  - systemd-resolve --status | grep 'DNS Servers' -A2
  - DEBIAN_FRONTEND=noninteractive  apt-get update -y && apt-get upgrade -y
  - apt-get -y autoremove
EOF

multipass launch jammy \
  --name k0s-loadbalancer  \
  --cpus 1 \
  --memory 2048M \
  --disk 20G \
  --cloud-init "${DIR}"/multipass-cloud-init.yml

for ((i = 1 ; i <= "${NUMBER_OF_MASTER}" ; i++)); do
  echo "[${i}/${NUMBER_OF_MASTER}] Creating instance k0s-${i} with multipass..."
  multipass launch jammy \
  --name k0s-master-"${i}"  \
  --cpus 1 \
  --memory 2048M \
  --disk 20G \
  --cloud-init "${DIR}"/multipass-cloud-init.yml
done

for ((i = 1 ; i <= "${NUMBER_OF_WORKER}" ; i++)); do
  echo "[${i}/${NUMBER_OF_WORKER}] Creating instance k0s-${i} with multipass..."
  multipass launch jammy \
  --name k0s-worker-"${i}"  \
  --cpus 1 \
  --memory 2048M \
  --disk 20G \
  --cloud-init "${DIR}"/multipass-cloud-init.yml
done

multipass list 


