# ops-snapshot-audit

Agentless, read‑only toolkit for auditing Linux servers via SSH (Ansible).

## Philosophy

**No changes, no installations, no modifications.**  
This toolkit runs exclusively in “read‑only” mode:
- It never installs or removes packages.
- It never modifies configuration files.
- It never starts, stops, or restarts services.
- It only collects information and validates the current state.

All commands are safe, non‑destructive and can be run on production systems without risk.

## AI-Powered Analysis

Adds intelligent analysis of audit data using OpenAI's GPT models. When an OpenAI API key is provided, the `ai_analysis` role processes collected data and generates actionable insights, anomaly detection, and diagnostic recommendations.

### Configuration
Set the `openai_api_key` variable in your inventory or pass it as an extra var:

```yaml
# inventory.yml
all:
  vars:
    openai_api_key: "your-api-key-here"
```

or via command line:

```bash
ansible-playbook -i inventory.yml -e "openai_api_key=your-api-key-here" playbooks/snapshot.yml
```

The AI analysis will only run when the key is provided and non‑empty.

## Requirements

- Python 3.6+
- Ansible 2.9+
- SSH access to target servers (password or key‑based)

## Quick Start

1. Clone the repository.
2. Adjust the inventory (`inventories/example.yml`) with your servers.
3. Edit the audit profile (`profiles/mipro‑linux.yml`) to define which services and logs to check.
4. Run the audit:

```bash
python opssnap/cli.py -i inventories/example.yml -p profiles/mipro‑linux.yml
```

The results will be saved under `output/<hostname>/<date>/`.

## Structure

```
ops‑snapshot‑audit/
├── ansible.cfg               # Ansible configuration
├── playbooks/
│   └── snapshot.yml          # Main playbook that imports roles
├── roles/
│   ├── linux_base/           # OS, kernel, CPU, RAM, disk, top processes
│   ├── systemd_checks/       # Status of defined services
│   ├── nginx/                # Validate config and tail logs
│   ├── logs_collect/         # Generic log collection
│   ├── updates_readonly/     # List pending updates (no installation)
│   ├── ai_analysis/          # AI-powered analysis of audit data
│   └── reporting/            # Generate summary Markdown report
├── profiles/
│   └── mipro‑linux.yml       # Example profile with services, logs, thresholds
├── inventories/
│   └── example.yml           # Example inventory (localhost)
├── opssnap/
│   └── cli.py               # CLI wrapper (run audit & zip results)
└── tests/
    └── test_safety.py       # Safety test: ensures no prohibited modules
```

## Profiles

Profiles are YAML files that define what to audit. Example:

```yaml
name: mipro‑linux
services:
  - nginx
  - mysql
  - sshd
logs:
  - path: /var/log/syslog
    lines: 100
thresholds:
  disk_usage_warn: 80
```

## Safety Guarantee

The toolkit includes a safety test (`tests/test_safety.py`) that scans all YAML files for prohibited modules (`apt`, `yum`, `file`, `copy`, `shell` with `rm`, etc.). If any are found, the test fails.

This ensures the project stays strictly read‑only.

## CLI Wrapper

The `opssnap/cli.py` script provides a convenient command‑line interface:

```
usage: cli.py [-h] [-i INVENTORY] [-p PROFILE] [-z] [--zip-name ZIP_NAME]

Ops Snapshot Audit - Agentless read‑only Linux audit via SSH

optional arguments:
  -h, --help            show this help message and exit
  -i INVENTORY, --inventory INVENTORY
                        Path to Ansible inventory file
  -p PROFILE, --profile PROFILE
                        Path to audit profile YAML
  -z, --zip             Package output into a zip file after audit
  --zip-name ZIP_NAME   Custom name for the zip file
```

## Output

After each run, a directory is created under `output/<hostname>/<date>/` containing:

- `linux_base.txt` – System information
- `systemd_checks.txt` – Service statuses
- `nginx.txt` – NGINX config and logs (if applicable)
- `logs_collect.txt` – Tail of defined logs
- `updates_readonly.txt` – Pending package updates
- `ai_analysis.txt` – AI analysis summary
- `summary.md` – Consolidated Markdown report

## License

MIT