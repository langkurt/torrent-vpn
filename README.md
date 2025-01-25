# Torrent VPN with VirusTotal Integration

This project creates a Docker container that runs a torrent client (qBittorrent) with VPN support and scans all downloaded files through VirusTotal.

## Features
- Secure VPN connection using OpenVPN.
- Scans downloaded files with VirusTotal API.
- Only clean files are moved to the accessible volume.
- Supports Docker for easy deployment.

## Setup
Clone this repository:
   ```bash
   git clone <repo_url>
   cd torrent-vpn
  ```

### Notes on VPN

VPN Configuration File (vpn-config.ovpn)
Replace this with your actual VPN configuration file. If you use a provider like NordVPN, PIA, or others, download their .ovpn file.

To ensure your VPN is working and all torrent traffic is routed through it:
`docker exec -it torrent-vpn curl https://ifconfig.me`
This should show the IP address assigned by your VPN, not your actual IP.

### VNC Access
A VNC server is included to provide a graphical interface for the browser. You can connect to the container's desktop environment using any VNC viewer.


## Using Brave Browser in the Container

Brave Browser is installed in the container and can be accessed through the VNC session. Follow the steps below to run it:

### Launching Brave Browser
1. Connect to the container's VNC session (e.g., `localhost:5900`) using your preferred VNC viewer.
2. Open a terminal inside the VNC session.
3. Run the following command to start Brave Browser:
   ```bash
   brave-browser --no-sandbox &


### How to Use Docker

1.	Build the image:
`docker build -t torrent-vpn .`

2. Start the container:
```bash
   docker run -d --name torrent-vpn \
     --cap-add=NET_ADMIN \
     --device /dev/net/tun \
     -v /path/to/clean_downloads:/safe_downloads \
     -v /path/to/configs:/configs \
     -p 8080:8080 \
     -p 5900:5900 \
     torrent-vpn
```


3. Run the container:

```bash
docker run -d --name torrent-vpn \
  --cap-add=NET_ADMIN \
  --device /dev/net/tun \
  -v "/Users/kurtlang/Google Drive/My Drive/Rakuten Kobo":/root/safe_downloads \
  -p 8080:8080 \
  -p 5900:5900 \
  torrent-vpn
  ```

-	--cap-add=NET_ADMIN: Grants network configuration privileges.
-	--device /dev/net/tun: Enables the VPN’s tunneling functionality.


Start/Stop the Container:
```
docker start torrent-vpn
docker stop torrent-vpn
```

Check container logs:
```
docker logs torrent-vpn
docker logs torrent-vpn 2>&1 | grep -i password
docker exec -it torrent-vpn tail -f /var/log/file_scanner.log
```

Access the Shell:
`docker exec -it torrent-vpn bash`

