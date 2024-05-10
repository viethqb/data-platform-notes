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
    && rm -rf /var/lib/apt/lists/* \
    && mkdir /home/admin/.ssh \
    && chown admin:admin /home/admin/.ssh

RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

EXPOSE 22

# Set systemd as entrypoint.
ENTRYPOINT [ "/sbin/init", "--log-level=err" ]