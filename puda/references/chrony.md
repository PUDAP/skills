# Chrony NTP sync

PUDA timestamps, discovery leases, and experiment provenance depend on host clocks. Sync every PUDA host to the **site NTP server** (Chrony on the NATS machine). The edge process does not talk NTP; it uses the host clock. Do not run Chrony inside an edge Docker container.

```text
public/campus NTP  →  chrony on the NATS host  →  chronyd / w32time on each edge host
```

## When to use

- Setting up a new site, NATS host, or edge PC
- Clock skew, stale discovery timestamps, or mismatched logs across machines
- User mentions Chrony, NTP, time sync, or `timedatectl`

**Ask the user for the NTP server host IP if you are unsure.** Do not assume, guess, or reuse an example address. Do not proceed with edge client setup until the user confirms it.

Use `HOST_IP` from the site Chrony `.env` when that file is present and the value is clearly this site's (Tailscale IP, LAN IP, or Tailscale MagicDNS). Example shape only: `100.118.119.115` or `bears`. Never use `host.docker.internal`.

## Identify the host

| This machine | Action |
|---|---|
| NATS host (site NTP server) | Run the Chrony **container**. Do not run the edge client scripts. |
| Edge host | Point Chrony / Windows Time at `HOST_IP`. Do not start a second NTP server. |
| Edge container | Inherit the host clock. Stop if you were about to install Chrony here. |

If Docker container `chrony` is already running on this host, it is the site NTP server and already disciplines this clock. Skip client setup.

## Site NTP server (NATS host)

Run this on the **same computer as NATS**. Only one process can bind UDP 123 or set the system clock.

```bash
sudo timedatectl set-ntp false
sudo systemctl disable --now chrony chronyd systemd-timesyncd 2>/dev/null || true
```

From `infra/chrony` in the PUDA repo:

```bash
cp .env.example .env
# Set HOST_IP to this machine's Tailscale/LAN address (edges use this value).
docker compose up -d --build
sudo ufw allow 123/udp   # if a host firewall is enabled
```

The container must use **host networking**. Docker bridge port publish SNATs the NTP reply source port; edge `chronyd` then drops the packet (`Reach 0`).

Verify the server is locked to upstream:

```bash
docker compose ps
docker exec chrony chronyc tracking
docker exec chrony chronyc sources -v
```

`Leap status : Normal` means this server is locked. From another host (replace with `HOST_IP`):

```bash
chronyd -Q "server <NTP_SERVER> iburst"
```

To use campus NTP instead of `pool ntp.ubuntu.com`, edit `chrony.conf` and recreate:

```conf
server ntp.example.edu iburst
```

```bash
docker compose up -d --force-recreate
```

## Edge host — Linux

Prefer the setup script shipped with the edge (`chrony/setup.sh` or `test-edge/chrony/setup.sh`):

```bash
sudo ./setup.sh <NTP_SERVER>
```

If the script is not present, configure Chrony as a **client only**:

```bash
sudo timedatectl set-ntp false
sudo apt update && sudo apt install -y chrony
sudo systemctl disable --now systemd-timesyncd ntp ntpd 2>/dev/null || true
```

Write `/etc/chrony/chrony.conf` (or `/etc/chrony.conf`). Comment out any `pool` lines. `port 0` means this host does not serve NTP:

```conf
server <NTP_SERVER> iburst
port 0
makestep 1.0 3
rtcsync
driftfile /var/lib/chrony/chrony.drift
```

Ubuntu also ships pool sources under `/etc/chrony/sources.d`. Move those files aside so the host locks to site NTP only.

```bash
sudo systemctl enable --now chrony
sudo systemctl restart chrony
```

On Debian/Ubuntu the unit is `chrony.service`; on RHEL/Fedora it is `chronyd.service`. systemd 255+ refuses to enable aliases — enable the real unit.

## Edge host — Windows

Elevated PowerShell. Prefer `chrony/setup.ps1` when present:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1 -NtpServer <NTP_SERVER>
```

Manual equivalent:

```powershell
Set-Service -Name w32time -StartupType Automatic
Start-Service -Name w32time
w32tm /config /manualpeerlist:"<NTP_SERVER>,0x8" /syncfromflags:manual /reliable:YES /update
Restart-Service -Name w32time
w32tm /resync /force
```

## Verify lock

Status printed immediately after setup is often still unlocked (`Leap status : Not synchronised`, source state `?`). Wait one or two minutes, then check again.

Linux:

```bash
chronyc tracking
chronyc sources -v
```

Locked when:

- `Leap status : Normal`
- `*` next to the NTP server (not `?`)
- `Reach` climbing toward `377` (`1` → `3` → `7` → `17` → …)

`^?` with a non-zero Reach and a Last sample means packets arrived; wait for more polls. `Reach 0` means replies are not getting back (wrong address, firewall, or NTP served through Docker bridge NAT).

Windows:

```powershell
w32tm /query /status
w32tm /query /peers
```

Locked when Source is the NTP server and Last Successful Sync Time is recent, not `1/1/1901` or empty.
