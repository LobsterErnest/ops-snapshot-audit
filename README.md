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

Adds intelligent analysis of audit data using OpenAI's GPT models or Google Gemini. When an AI API key is provided, the `ai_analysis` role processes collected data and generates actionable insights, anomaly detection, and diagnostic recommendations.

### Configuration
Set the `openai_api_key` or `gemini_api_key` variable in your inventory or pass it as an extra var:

```yaml
# inventory.yml
all:
  vars:
    openai_api_key: "your-api-key-here"   # For OpenAI
    gemini_api_key: "your-api-key-here"   # For Google Gemini
    ai_provider: "openai"                 # Optional: "openai" or "google" (defaults to openai)
```

or via command line:

```bash
ansible-playbook -i inventory.yml -e "openai_api_key=your-api-key-here" playbooks/snapshot.yml
ansible-playbook -i inventory.yml -e "gemini_api_key=your-api-key-here" -e "ai_provider=google" playbooks/snapshot.yml
```

The AI analysis will only run when a corresponding API key is provided and non‑empty.

### Provider Selection
Use the `--provider` flag with the CLI wrapper to specify which AI provider to use (`openai` or `google`). Default is `openai`.

```bash
python opssnap/cli.py -i inventory.yml -p profile.yml --provider google
```

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
│   ├── security_baseline/    # SSH hardening, permissions, SUID/SGID, world-writable
│   ├── user_audit/           # Local users, groups, recent logins
│   ├── auth_audit/           # Authentication log tail
│   ├── network_audit/        # IPs, routes, DNS, firewall status
│   ├── time_sync/            # NTP/chrony/timedate status
│   ├── compliance_cis/       # Lightweight CIS-style checks
│   ├── nginx/                # Validate config and tail logs
│   ├── logs_collect/         # Generic log collection
│   ├── updates_readonly/     # List pending updates (no installation)
│   ├── ai_analysis/          # AI-powered analysis of audit data
│   └── reporting/            # Generate summary Markdown/JSON + metrics
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
modules:
  - linux_base
  - systemd_checks
  - security_baseline
  - user_audit
  - auth_audit
  - network_audit
  - time_sync
  - compliance_cis
  - nginx
  - logs_collect
  - updates_readonly
  - ai_analysis
  - reporting
security:
  scan_suid: true
  scan_world_writable: true
  list_limit: 50
  suid_warn_threshold: 200
  world_writable_warn_threshold: 200
auth_audit:
  lines: 100
user_audit:
  last_logins: 50
  group_limit: 200
network_audit:
  rules_limit: 200
```

## Safety Guarantee

The toolkit includes a safety test (`tests/test_safety.py`) that scans all YAML files for prohibited modules (`apt`, `yum`, `file`, `copy`, `shell` with `rm`, etc.). If any are found, the test fails.

This ensures the project stays strictly read‑only.

## CLI Wrapper

The `opssnap/cli.py` script provides a convenient command‑line interface:

```
usage: cli.py [-h] [-i INVENTORY] [-p PROFILE] [--provider {openai,google}] [-z] [--zip-name ZIP_NAME]

Ops Snapshot Audit - Agentless read‑only Linux audit via SSH

optional arguments:
  -h, --help            show this help message and exit
  -i INVENTORY, --inventory INVENTORY
                        Path to Ansible inventory file
  -p PROFILE, --profile PROFILE
                        Path to audit profile YAML
  --provider {openai,google}
                        AI provider to use for analysis (openai or google)
  -z, --zip             Package output into a zip file after audit
  --zip-name ZIP_NAME   Custom name for the zip file
```

## Output

After each run, a directory is created under `output/<hostname>/<date>/` containing:

- `linux_base.txt` – System information
- `systemd_checks.txt` – Service statuses
- `security_baseline.txt` – SSH hardening and permissions
- `user_audit.txt` – Users/groups and recent logins
- `auth_audit.txt` – Authentication log tail
- `network_audit.txt` – IPs, routes, DNS, firewall state
- `time_sync.txt` – Time synchronization status
- `compliance_cis.txt` – Lightweight CIS checks
- `nginx.txt` – NGINX config and logs (if applicable)
- `logs_collect.txt` – Tail of defined logs
- `updates_readonly.txt` – Pending package updates
- `ai_analysis.txt` – AI analysis summary
- `summary-*.md` – Consolidated Markdown report
- `summary-*.json` – Machine‑readable JSON report
- `metrics.prom` – Prometheus textfile metrics

## Monitoring Integration

The reporting role emits a Prometheus textfile at `metrics.prom`. You can copy or symlink this file into a node_exporter textfile collector directory to surface audit health in monitoring dashboards and alerts.

## License

MIT
