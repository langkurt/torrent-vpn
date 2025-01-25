# Base image
FROM ubuntu:24.10

# Install dependencies
RUN apt-get update && apt-get install -y \
    qbittorrent-nox \
    openvpn \
    iptables \
    curl \
    iproute2 \
    python3 \
    python3-pip \
    python3-venv \
    wget \
    chromium-browser \
    xvfb \
    x11vnc \
    fluxbox \
    && apt-get clean

# Create a virtual environment for Python
RUN python3 -m venv /venv

# Activate the virtual environment and install Python packages
RUN /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install requests

# Set environment variables for the virtual environment
ENV PATH="/venv/bin:$PATH"

# Add the file scanner script
COPY file_scanner.py /file_scanner.py

# Add the environment variables
COPY configs/env.json /root/env.json

# Add OpenVPN configuration
COPY configs/vpn-configs/vpn-config.ovpn /etc/openvpn/client.conf

# Add entrypoint script
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose necessary ports
EXPOSE 8080 8999 5900

# Set up entrypoint
ENTRYPOINT ["/entrypoint.sh"]