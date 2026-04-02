# Digital Shield Corporation

```
    ╔═══════════════════════════════════════════════╗
    ║                                               ║
    ║   🛡️  DIGITAL SHIELD CORPORATION              ║
    ║                                               ║
    ║   Red Team Assessment Lab                     ║
    ║   Multi-Network Pivoting Environment          ║
    ║                                               ║
    ╚═══════════════════════════════════════════════╝
```

A realistic multi-network attack lab designed for practicing red team operations, C2 framework testing, and penetration testing training. Built with Docker, deployable anywhere.

## Overview

Digital Shield Corporation is a fictional cybersecurity company with a fully functional corporate infrastructure — website, webmail, developer portal, file servers, monitoring, databases, and a secrets vault. Your mission: compromise the entire organization from a single entry point.

**10 containers | 4 networks | 10 flags | 1,750 points**

## Network Topology

```
ATTACKER (Your Machine)
    │
    ├── Port 8888 ──► Company Website
    └── Port 9999 ──► CTF Scoreboard
    │
═══ DMZ (10.10.10.0/24) ════════════════════════════════
║  ds-gateway    10.10.10.10   Corporate Website         ║
║  ds-webmail    10.10.10.20   Employee Webmail           ║
║  ds-devportal  10.10.10.30   Developer Portal + Redis   ║
║  ds-jumphost   10.10.10.40   SSH Bastion ──────────────╬──┐
═════════════════════════════════════════════════════════    │
                                                            │
═══ CORPORATE (10.10.20.0/24) [Internal] ═══════════════    │
║  ds-jumphost   10.10.20.10   SSH Bastion (from DMZ) ◄──┘ ║
║  ds-filestore  10.10.20.20   File Server (FTP/SSH) ────╬──┐
║  ds-monitoring 10.10.20.30   Monitoring Dashboard      ║  │
║  ds-webserver  10.10.20.40   Apache+PHP Client Portal  ║  │
═════════════════════════════════════════════════════════    │
                                                            │
═══ RESTRICTED (10.10.30.0/24) [Internal] ══════════════    │
║  ds-filestore  10.10.30.2    File Server (from Corp) ◄─┘ ║
║  ds-database   10.10.30.10   PostgreSQL Database        ║
║  ds-vault      10.10.30.20   Secrets Vault API (HTTPS)  ║
═════════════════════════════════════════════════════════
```

**Key challenge:** Corporate and Restricted networks are `internal: true` — no direct access from your machine. You must pivot through dual-homed hosts.

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Linux (native, WSL2, or VM)

### Installation

```bash
# Clone the repository
git clone https://github.com/phantom-offensive/DigitalShieldCorp.git
cd DigitalShieldCorp

# Start the lab
sudo docker compose up -d

# Verify all containers are running
sudo docker ps
```

### Access

| Service | URL | Container | Internal IP |
|---------|-----|-----------|-------------|
| Company Website | http://localhost:8888 | ds-gateway | 10.10.10.10 |
| Employee Webmail | http://localhost:8025 | ds-webmail | 10.10.10.20 |
| Monitoring Dashboard | http://localhost:8090 | ds-monitoring | 10.10.20.30 |
| CTF Scoreboard | http://localhost:9999 | ds-scoreboard | 10.10.40.10 |

> **IMPORTANT:** Internal Docker IPs (10.10.10.x, 10.10.20.x, 10.10.30.x) are **NOT** reachable from your browser or host machine. Always use the `localhost` URLs above. Internal IPs are only accessible from **inside containers** after pivoting.

Containers with no port mapping (must pivot to reach):

| Container | Internal IP | Network | Services |
|-----------|-------------|---------|----------|
| ds-devportal | 10.10.10.30 | DMZ | Developer Portal, Redis :6379 |
| ds-jumphost | 10.10.10.40 / 10.10.20.10 | DMZ + Corporate | SSH :22 (bridge host) |
| ds-webserver | 10.10.20.40 | Corporate | Apache+PHP :80 |
| ds-filestore | 10.10.20.20 / 10.10.30.2 | Corporate + Restricted | FTP :21, SSH :22 (bridge host) |
| ds-database | 10.10.30.10 | Restricted | PostgreSQL :5432, SSH :22 |
| ds-vault | 10.10.30.20 | Restricted | Vault API :8443, SSH :22 |

### Stop / Reset

```bash
# Stop the lab
sudo docker compose down

# Full reset (rebuild from scratch)
sudo docker compose down && sudo docker compose up -d --build
```

## Difficulty

**Overall: 6-7/10 (Intermediate)**

| Aspect | Details |
|--------|---------|
| Initial Access | Web application exploitation (auth bypass, LFI, command injection, file upload) |
| Credential Discovery | No plaintext password files — must exploit services, crack hashes, read emails |
| Pivoting | Internal networks require multi-hop SSH or SOCKS proxy tunneling |
| Privilege Escalation | GTFOBins techniques (tcpdump, rsync, openssl) |
| Services | Flask apps, Apache+PHP, Redis, PostgreSQL, FTP, SSH |
| Decoys | 7+ rabbit holes to waste your time |

## Flags

| # | Points | Difficulty | Category |
|---|--------|------------|----------|
| 1 | 100 | Easy | Web Exploitation |
| 2 | 100 | Easy | OSINT |
| 3 | 150 | Medium | Misconfiguration |
| 4 | 200 | Medium | Privilege Escalation |
| 5 | 150 | Medium | Data Exfiltration |
| 6 | 100 | Easy | Web Exploitation |
| 7 | 250 | Hard | Cryptography |
| 8 | 200 | Medium | Privilege Escalation |
| 9 | 200 | Medium | API Exploitation |
| 10 | 300 | Hard | Privilege Escalation |

**Total: 1,750 points**

Submit flags at the scoreboard: `http://localhost:9999`

## Skills Tested

- Web application enumeration and exploitation
- Credential brute forcing and password cracking
- Service misconfiguration exploitation (Redis, FTP, Apache)
- Web shell upload and execution (PHP, ASP, JSP)
- Multi-network pivoting and tunneling
- SSH key/credential reuse attacks
- Linux privilege escalation (SUID, sudo, cron)
- Database exploitation (PostgreSQL)
- API authentication bypass
- Data exfiltration techniques
- OSINT and intelligence gathering from emails/files

## Recommended Tools

- **C2 Framework** — [Phantom C2](https://github.com/phantom-offensive/Phantom), Sliver, Cobalt Strike, or Metasploit
- **Scanning** — nmap, rustscan
- **Web** — Burp Suite, ffuf, nikto
- **Brute Force** — hydra, medusa
- **Password Cracking** — hashcat, john
- **Pivoting** — chisel, ligolo-ng, SSH tunneling, proxychains
- **Redis** — redis-cli or raw netcat
- **Database** — psql, pgcli

## Remote Access (For Instructors)

Share the lab with students using Tailscale:

```bash
# Install Tailscale on the lab host
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# Students install Tailscale, get approved, then access:
#   http://<tailscale-ip>:8888  (Website)
#   http://<tailscale-ip>:9999  (Scoreboard)
```

No port forwarding or domain needed. Manage access at [Tailscale Admin](https://login.tailscale.com/admin/machines).

## Architecture

```
DigitalShieldCorp/
├── docker-compose.yml          # Orchestration (9 services, 4 networks)
├── ds-gateway/                 # Corporate website (Flask + LFI + cmd injection)
├── ds-webmail/                 # Employee webmail (Flask + brute force + SSRF)
├── ds-devportal/               # Developer portal (Flask + Redis + session hijack)
├── ds-jumphost/                # SSH bastion (bridges DMZ → Corporate)
├── ds-filestore/               # File server (FTP + SSH, bridges Corp → Restricted)
├── ds-monitoring/              # Monitoring dashboard (HTTP Basic Auth + LFI)
├── ds-webserver/               # Apache+PHP client portal (file upload → web shell)
├── ds-database/                # PostgreSQL (credential chain + RCE)
├── ds-vault/                   # Secrets vault API (HTTPS + bearer auth)
└── ds-scoreboard/              # CTF scoreboard (flag submission + leaderboard)
```

## Hints

<details>
<summary>Stuck? Click for general guidance (no spoilers)</summary>

1. **Start with recon** — read everything on the website carefully
2. **Check common files** — robots.txt, API endpoints, staff pages
3. **Think about password patterns** — corporations often use predictable formats
4. **Redis** — does it require authentication? Try connecting directly
5. **Email is intelligence** — people share too much information in emails
6. **Check system files** — crontabs, bash_history, config files in /opt
7. **Pivoting is key** — some networks are unreachable without tunneling
8. **GTFOBins** — always check what you can run with sudo
9. **Base64 is your friend** — complex commands through SSH chains need encoding
10. **Don't trust everything** — some credentials are intentionally wrong

</details>

## Disclaimer

**This lab is designed for authorized security training and education only.**

All systems, credentials, and data are fictional. Do not deploy this lab on production networks or use the techniques learned here without proper authorization.

## Author

**Opeyemi Kolawole** — [GitHub](https://github.com/phantom-offensive) | ckkolawole77@gmail.com

## License

MIT License — see [LICENSE](LICENSE) for details.
