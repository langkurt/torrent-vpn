#!/bin/bash

# Ensure xterm is available as x-terminal-emulator
if [ ! -f /usr/bin/x-terminal-emulator ]; then
    ln -s /usr/bin/xterm /usr/bin/x-terminal-emulator
fi

# Clean up stale X server lock files
if [ -f /tmp/.X0-lock ]; then
    echo "Removing stale X server lock file..."
    rm -f /tmp/.X0-lock
fi

# Start OpenVPN client
openvpn --config /etc/openvpn/client.conf --daemon

# Wait for VPN connection
echo "Waiting for VPN connection..."
while ! curl -s --head https://www.google.com > /dev/null; do
    sleep 2
done
echo "VPN is connected!"

# Configure iptables to route traffic through the VPN
VPN_INTERFACE=$(ip route | grep default | awk '{print $5}')
echo "Using VPN interface: $VPN_INTERFACE"
iptables -A OUTPUT -o "$VPN_INTERFACE" -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT
iptables -A OUTPUT -d 127.0.0.1 -j ACCEPT
iptables -A OUTPUT -j DROP

# Start X virtual framebuffer for GUI
export DISPLAY=:0
Xvfb :0 -screen 0 1920x1080x24 &

# Start VNC server
x11vnc -display :0 -nopw -forever &

# Start lightweight window manager
fluxbox &

# Start file scanner in the background
python3 /file_scanner.py &

# Start qBittorrent
qbittorrent-nox