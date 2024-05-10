FROM ghcr.io/nestybox/ubuntu-jammy-systemd:latest

# Install Sshd
RUN apt-get update \
    && apt-get install --no-install-recommends -y openssh-server uuid-runtime\
    apt-transport-https \
    bash-completion vim less man jq bc \
    lsof tree psmisc htop lshw sysstat dstat \
    iproute2 iputils-ping iptables dnsutils traceroute \
    netcat curl wget nmap socat netcat-openbsd rsync \
    p7zip-full \
    git tig \
    binutils acl pv \
    strace tcpdump \
    open-iscsi nfs-common \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir /home/admin/.ssh \
    && chown admin:admin /home/admin/.ssh

# Enable sudo without password
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Enable ssh password authentication
RUN sed -i 's/^PasswordAuthentication .*/PasswordAuthentication yes/' /etc/ssh/sshd_config
RUN echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config

# Set Root password
RUN echo "admin\nadmin" | passwd root

EXPOSE 22

# Set systemd as entrypoint.
ENTRYPOINT ["/sbin/init", "--log-level=err"]