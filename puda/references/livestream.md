# Livestream (USB / IP cameras)

Use [PUDAP/livestream](https://github.com/PUDAP/livestream) when a PUDA machine host has USB cameras, webcams, or IP cameras and operators need live video over RTSP, RTMP, HLS, or WebRTC.

Requires Docker Engine and Docker Compose on the camera host. Operators must reach that host on the same VPN used for PUDA.

Do not assume, guess, or reuse example devices, URLs, stream names, or host addresses. After the user confirms the values below, clone/configure the stack and start it. Do not stop at printed instructions.

## Collect from the user

Ask for all of these before writing config or starting containers:

1. **Camera** — a local USB `/dev/video*` path, or a network camera URL (`rtsp://...`).
2. **Stream name** — public name in stream URLs. Lowercase, no spaces. Examples of *shape* only: `livestream`, `ipcam0`.
3. **Host address** — `MTX_WEBRTCADDITIONALHOSTS`: the Tailscale IP or MagicDNS name operators will use to open the stream.

List USB cameras on this host before asking which one to use:

```bash
ls -l /dev/video*
```

If `v4l-utils` is installed:

```bash
v4l2-ctl --list-devices
```

For IP cameras, the user supplies the stream URL from the camera admin UI or vendor docs. Shape only:

```text
rtsp://user:pass@192.168.1.50:554/stream1
```

If `MTX_WEBRTCADDITIONALHOSTS` is unknown, suggest a detected Tailscale address (`tailscale ip -4` or MagicDNS from `tailscale status --json`) and wait for confirmation. Never write an example IP into `.env`.

## Setup

Work on the **camera host**. Clone [PUDAP/livestream](https://github.com/PUDAP/livestream) to `~/workspace/livestream`. Reuse that checkout if it already exists.

```bash
git clone https://github.com/PUDAP/livestream.git ~/workspace/livestream
cd ~/workspace/livestream
cp .env.example .env
```

Set `MTX_WEBRTCADDITIONALHOSTS` in `.env` to the confirmed host address.

Write `streams.conf`. Each non-blank, non-comment line is `INPUT STREAM_NAME` separated by whitespace. Comment out or remove example lines that are not this host's camera.

USB camera:

```text
/dev/video0 livestream
```

Network camera:

```text
rtsp://user:pass@192.168.1.50:554/stream1 ipcam0
```

Replace those examples with the confirmed camera and stream name.

Docker does not see host video devices unless they are mapped. For each USB `/dev/video*` input in `streams.conf`, add a matching `devices:` entry on the `ffmpeg` service in `compose.yml`:

```yaml
devices:
  - /dev/video0:/dev/video0
```

IP camera URLs do not need a device mapping. If this host is network-camera only, remove the default `/dev/video0` mapping so Compose does not fail on a missing device.

Start the stack:

```bash
docker compose up -d
docker compose ps
```

Both `mediamtx` and `ffmpeg` should be running. If config changed on an existing checkout, recreate:

```bash
docker compose up -d --force-recreate
```

## Stream URLs

Ports published by `compose.yml`:

```yaml
ports:
  - "8554:8554" # RTSP
  - "1935:1935" # RTMP
  - "8888:8888" # HLS
  - "8889:8889" # WebRTC HTTP/WHIP/WHEP
  - "8189:8189/udp" # WebRTC ICE/UDP
  - "8189:8189/tcp" # WebRTC ICE/TCP
```

Report these URLs using the confirmed host and stream name:

| Protocol | URL |
| --- | --- |
| RTSP | `rtsp://HOST:8554/STREAM_NAME` |
| RTMP | `rtmp://HOST:1935/STREAM_NAME` |
| HLS | `http://HOST:8888/STREAM_NAME/` |
| WebRTC | `http://HOST:8889/STREAM_NAME/` |

HLS and WebRTC open in a browser. Manual-control UIs can embed the HLS or WebRTC URL.

## Troubleshooting

```bash
docker compose logs -f mediamtx ffmpeg
```

From another machine that can reach the livestream host:

```bash
ffprobe rtsp://HOST:8554/STREAM_NAME
```

USB stream missing: the device path is wrong, another process holds the camera, or `compose.yml` has no matching `devices:` mapping.

Network stream missing: the RTSP URL is wrong, or the camera host cannot reach the camera IP.

WebRTC fails in the browser but RTSP works: `MTX_WEBRTCADDITIONALHOSTS` does not match the address the operator used.
