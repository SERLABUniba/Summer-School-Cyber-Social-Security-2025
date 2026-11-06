# Summer School Cyber-Social Security 2025

Repository containing the educational material and CTF platform for the Cyber-Social Security Summer School. The project includes a **game dashboard** with team authentication, module management, flag validation, scoring, and a scoreboard.

## Authors and references

_Vita Santa Barletta, Danilo Caivano, Gabriel Cellammare, Samuele Del Vescovo, Rebecca Margiotta, and Davide Pio Posa._

## Repository contents

The activities are organized into the following modules:

- **Cyber-Social Security in Multi-Domain Operations (MDO)**: correlation across the cyber, informational, cognitive, and physical domains.
- **Cyber Threat Intelligence (CTI)**: OSINT, profile identification, indicators, malware, APTs, and MITRE ATT&CK TTPs.
- **Red Team vs Blue Team**: practical attack and defense exercises involving phishing, credential theft, lateral movement, EDR, firewalls, and SIEM.
- **Malware Analysis**: static triage, strings, PCAP, persistence, C2, payloads and YARA rules, without executing real samples.
- **Wargaming**: operational decision-making simulations involving dynamic events such as GPS spoofing, deepfakes, and satellite outages.
- **Hybrid Warfare**: correlation of cyberattacks, drones, propaganda, sabotage, and social engineering.
- **Generative AI for Cyber-Social Security**: detection of deepfakes, synthetic images and audio, and LLM-generated phishing.

Module content is described by the JSON files in the `css_mdo/`, `cti/`, `AI_CSS/` and `CTF-Base_Hybrid-Malaware/` directories. The `red_vs_blue/` directory contains the executable web challenges.

## Challenge architecture

### Red Team vs Blue Team: challenge machines

The Red Team vs Blue Team challenges are web applications exposed as separate machines through Docker Compose:

| Challenge | Technique | Local port |
|---|---|---:|
| Harbor Gate | SQL injection / login bypass | 8081 |
| Trident Notes | Stored XSS in comments | 8082 |
| Trident Check 1 | Command injection | 8083 |
| Trident Check 2 | Blind command injection | 8084 |

### Other modules: static pages

For the other modules, challenges are published as static pages or educational material, without a dedicated challenge machine:

- `css_mdo/`: HTML pages for MDO exercises.
- `CTF-Base_Hybrid-Malaware/`: static dashboard with Hybrid Warfare and Malware Analysis material.
- `cti/`: Cyber Threat Intelligence exercise datasets.
- `AI_CSS/`: datasets for generative AI exercises.

The central dashboard reads this content and presents the modules to the teams.

## Starting the platform with Docker

Run these commands from the repository root. The complete platform can be started with:

```bash
docker compose -f ctf_dashboard_app/docker-compose.yml up -d --build
docker compose -f red_vs_blue/harbor_gate/docker-compose.yml up -d --build
docker compose -f red_vs_blue/trident_notes/docker-compose.yml up -d --build
docker compose -f red_vs_blue/trident_check_1/docker-compose.yml up -d --build
docker compose -f red_vs_blue/trident_check_2/docker-compose.yml up -d --build
```

Alternatively, to start only the dashboard:

```bash
docker compose -f ctf_dashboard_app/docker-compose.yml up -d --build
```

To check the status and stop the containers:

```bash
docker compose -f ctf_dashboard_app/docker-compose.yml ps
docker compose -f red_vs_blue/harbor_gate/docker-compose.yml ps
docker compose -f ctf_dashboard_app/docker-compose.yml down
```

The dashboard listens on `127.0.0.1:8080`; the four challenges listen on ports `8081`, `8082`, `8083`, and `8084`, respectively. The ports are bound to the loopback interface so that public access goes through nginx.

## Exposing the platform through nginx

The ready-to-use configuration is [nginx/ctf.conf](nginx/ctf.conf). The expected mapping is:

| URL | Destination |
|---|---|
| `/` | Central dashboard, `127.0.0.1:8080` |
| `/red_vs_blue/harbor_gate/` | Harbor Gate challenge, `127.0.0.1:8081` |
| `/red_vs_blue/trident_notes/` | Trident Notes challenge, `127.0.0.1:8082` |
| `/red_vs_blue/trident_check_1/` | Trident Check 1 challenge, `127.0.0.1:8083` |
| `/red_vs_blue/trident_check_2/` | Trident Check 2 challenge, `127.0.0.1:8084` |
| `/css_mdo/md5` | Static MDO MD5 page |
| `/css_mdo/inj` | Static MDO injection page |
| `/hybrid_mal/` | Static Hybrid Warfare/Malware dashboard |

The configuration uses `proxy_pass` for the dashboard and Docker machines, and `alias` for static content. Before enabling it, verify that the absolute paths in `nginx/ctf.conf` match the target server.

Example installation and activation:

```bash
sudo cp nginx/ctf.conf /etc/nginx/sites-available/ctf.conf
sudo ln -s /etc/nginx/sites-available/ctf.conf /etc/nginx/sites-enabled/ctf.conf
sudo nginx -t
sudo systemctl reload nginx
```

If the default virtual host intercepts the traffic, disable it only after checking the other configured sites:

```bash
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

The currently configured hostname and address are `www-thehackspace.hosting.uniba.it` and `193.206.44.31`; replace them with the values used by your installation.

## Main structure

```text
ctf_dashboard_app/              Flask dashboard and Docker Compose
red_vs_blue/                    Containerized web challenges
css_mdo/                        Static MDO challenges
cti/                            Cyber Threat Intelligence datasets
AI_CSS/                         AI for Cyber-Social Security datasets
CTF-Base_Hybrid-Malaware/       Static Hybrid/Malware dashboard
nginx/                          Virtual host for public exposure
```

## Security notes

Before a public deployment:

- replace the example keys and passwords in the Compose files;
- verify that flags and instructor playbooks are not exposed to students;
- use HTTPS and configure a certificate in the nginx virtual host;
- restrict administrative access and access to solution material.

These activities are for educational purposes only and must be run only on authorized systems and networks.

### Related Academic Work

```bibtex
@article{caivano2025red,
  title={Red Team Knife to improve Cyber Security Education},
  author={Caivano, Danilo and Gentile, Adriano and Del Campo, Gennaro and Posa, Davide Pio and Piccinno, Antonio},
  year={2025}
}

@inproceedings{barletta2025cyber,
  title={Cyber Digital Twin to improve Security Education: the RedTeam Knife approach},
  author={Barletta, Vita Santa and Caivano, Danilo and Catalano, Christian and Gentile, Adriano and Posa, Davide Pio and Piccinno, Antonio},
  booktitle={Proceedings of the 16th Biannual Conference of the Italian SIGCHI Chapter},
  pages={1--7},
  year={2025}
}
```
