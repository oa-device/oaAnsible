# OrangeAd Mac Setup Playbook

Ansible playbook for automated setup and configuration of macOS devices for OrangeAd. This repository is part of the `oaPangaea` monorepo and provides
comprehensive macOS device management capabilities.

## Features

- Automated Homebrew installation and package management
- Python environment setup with pyenv
- Node.js setup with NVM
- Tailscale network configuration with DNS management
- macOS API service for device monitoring and management
- Dynamic inventory using Tailscale API
- Enhanced security and system settings configuration
- Environment-specific configurations (staging/production)
- Comprehensive verification system
- Development cleanup tools

## Prerequisites

1. On your control machine:

   ```sh
   # Install Ansible
   pip3 install ansible

   # Clone this repository
   git clone https://github.com/oa-device/macos-setup.git
   cd macos-setup

   # Install required Ansible roles and collections
   ansible-galaxy install -r requirements.yml
   ```

2. On target machines:
   - macOS (Intel or Apple Silicon)
   - SSH access configured
   - Sudo privileges
   - Minimum 8GB RAM

## Directory Structure

```tree
oaAnsible/
├── inventory/                # Environment-specific inventories
│   ├── production/           # Production environment
│   │   ├── hosts.yml         # Production hosts
│   │   └── group_vars/       # Production variables
│   ├── staging/              # Staging environment
│   │   ├── hosts.yml         # Staging hosts
│   │   └── group_vars/       # Staging variables
│   └── dynamic_inventory.py  # Dynamic inventory script using Tailscale API
├── roles/
│   ├── macos/                # macOS-specific roles
│   │   ├── api/              # macOS API service deployment
│   │   ├── base/             # Base system configuration
│   │   ├── network/          # Network configuration
│   │   │   └── tailscale/    # Tailscale VPN setup
│   │   ├── node/             # Node.js setup
│   │   ├── python/           # Python setup
│   │   ├── security/         # Security settings
│   │   └── settings/         # System preferences
│   ├── elliotweiser.osx-command-line-tools/  # External role (from Galaxy)
│   └── geerlingguy.dotfiles/                 # External role (from Galaxy)
├── macos-api/                # FastAPI service for macOS monitoring
│   ├── core/                 # Core functionality
│   ├── models/               # Data models
│   ├── routers/              # API endpoints
│   ├── services/             # Business logic
│   └── main.py               # Entry point
├── tasks/                    # Global tasks
│   ├── pre_checks.yml        # System verification
│   └── verify.yml            # Post-install checks
├── scripts/                  # Convenience scripts
│   ├── run-staging.sh        # Run playbook on staging
│   ├── run-production.sh     # Run playbook on production
│   ├── deploy-macos-api.sh   # Deploy macOS API only
│   └── verify-macos-api.sh   # Verify macOS API deployment
├── group_vars/               # Global variables
│   └── all/                  # Variables for all hosts
│       └── vault.yml         # Encrypted sensitive variables
├── main.yml                  # Main playbook
├── deploy-macos-api.yml      # macOS API deployment playbook
└── dev-cleanup.yml           # Development reset playbook
```

## Usage

### Quick Start

1. For staging environment:

   ```bash
   ./scripts/run-staging.sh
   ```

2. For production environment:

   ```bash
   ./scripts/run-production.sh
   ```

### Mac Mini M1 Onboarding

To onboard a new Mac Mini M1 device with Tailscale, macos-api, and oaTracker:

```bash
# Navigate to the oaAnsible directory
cd /path/to/oaPangaea/oaAnsible

# Run the onboarding script
./scripts/onboard-mac.sh
```

The script will:

1. Prompt for target Mac information (IP address, SSH username, hostname)
2. Create a temporary inventory file
3. Deploy core macOS configuration and Tailscale using the `macos` tag
4. Deploy the macOS API service
5. Deploy the oaTracker application

#### Deployment Architecture

- **User Account**: Both services run as the `ansible_user` (typically the `admin` user)
- **Service Management**: Services are managed by `launchd` with automatic startup
- **Directory Structure**:
  - macOS API: `/usr/local/orangead/macos-api/`
  - oaTracker: `/usr/local/orangead/tracker/`
- **Logs**:
  - macOS API: `/usr/local/orangead/macos-api/logs/`
  - oaTracker: `/usr/local/orangead/tracker/logs/`

#### Tailscale Setup

The playbook installs Tailscale using the Go install method rather than Homebrew:

1. Downloads the latest stable Tailscale binary directly from the official source
2. Installs it to `/usr/local/bin/`
3. Configures the system daemon using `tailscaled install-system-daemon`
4. Sets up DNS configuration for the OrangeAd network

**Note on Node Identity**: When a Mac is reimaged or reinstalled, it may appear as a new device in the Tailscale admin console. You may need to remove the old
device entry to avoid confusion.

#### Security Considerations

- **macOS API Security**: The macOS API service is secured through Tailscale's network-level security. Only devices on the Tailscale network with the
  appropriate ACLs can access the API endpoints.
- **No API Keys**: The current implementation relies on Tailscale IP-based access control rather than API keys.
- **User Account**: Both services run as the `ansible_user` (typically the `admin` user) for easier management and camera access permissions.

### Environment Differences

| Feature           | Staging  | Production |
| ----------------- | -------- | ---------- |
| Host Key Checking | Disabled | Enabled    |
| Debug Mode        | Enabled  | Disabled   |
| Dev Packages      | Full Set | Minimal    |
| DNS Management    | Optional | Required   |
| Security Checks   | Basic    | Strict     |

### Available Tags

- `setup`: Base system configuration
- `cli`: Command Line Tools installation
- `homebrew`: Package management
- `python`: Python/pyenv setup
- `node`: Node.js/nvm setup
- `tailscale`: Network configuration
- `security`: Security settings
- `settings`: System preferences
- `api`: macOS API service
- `verify`: Verification tasks
- `dev`: Development tools
- `network`: Network settings
- `configuration`: General configuration tasks

## Configuration

### Environment Variables

Each environment (staging/production) has its own configuration in `inventory/[env]/group_vars/all.yml`:

- Runtime versions (Python, Node.js)
- Feature toggles
- System packages
- Network settings

### Feature Toggles

```yaml
configure:
  tailscale: true/false
  pyenv: true/false
  node: true/false
  security: true/false
  settings: true/false
  api: true/false
```

## Verification System

Run verification independently:

```sh
# Full verification
ansible-playbook main.yml --tags "verify" -i inventory/[env]/hosts.yml

# Component-specific verification
ansible-playbook main.yml --tags "verify,python" -i inventory/[env]/hosts.yml

# Verify macOS API specifically
./scripts/verify-macos-api.sh
```

Verifies:

- System requirements
- Package installations
- Runtime environments
- Network connectivity
- macOS API service status
- Security settings
- System preferences

## Development Tools

### Development Cleanup Playbook

⚠️ **STAGING ENVIRONMENT ONLY** ⚠️

Reset your staging environment to a clean state:

```bash
ansible-playbook dev-cleanup.yml -K -i inventory/staging/hosts.yml
```

**Safety Features:**

1. Staging inventory only
2. Interactive confirmation
3. Comprehensive warnings
4. Cannot affect production

### macOS API Deployment

Deploy only the macOS API service to staging:

```bash
./scripts/deploy-macos-api.sh
```

### Mac Mini Onboarding

For a streamlined onboarding process of new Mac Mini devices, use the onboard-mac.sh script:

```bash
# Navigate to the oaAnsible directory
cd /path/to/oaPangaea/oaAnsible

# Run the onboarding script
./scripts/onboard-mac.sh
```

The script will:

1. Prompt for target Mac information (IP address, SSH username, hostname)
2. Create a temporary inventory file
3. Deploy core macOS configuration and Tailscale
4. Deploy macOS API service
5. Deploy oaTracker application
6. Provide verification steps and next actions

This is the recommended method for onboarding new Mac Mini devices as it ensures all components are properly installed and configured.

This script:

1. Runs the dedicated `deploy-macos-api.yml` playbook
2. Configures the macOS API service on the target machine
3. Sets up the launchd service to run as the `ansible_user` (typically the `admin` user)

### Enhanced Dynamic Inventory

The enhanced dynamic inventory script (`scripts/dynamic-inventory.py`) provides:

1. **Automatic Discovery**: Uses Tailscale API to find macOS devices
2. **Safety Mechanisms**: Connectivity validation for production environments
3. **Fallback Support**: Falls back to static inventory if API fails
4. **Environment Aware**: Handles both staging and production configurations
5. **Backup Creation**: Automatically backs up static inventories

#### Usage

```bash
# Generate inventory for staging
./scripts/dynamic-inventory.py --list --env staging

# Generate inventory for production (with safety checks)
./scripts/dynamic-inventory.py --list --env production

# Use with ansible-playbook
ansible-playbook main.yml -i scripts/dynamic-inventory.py

# Safe production deployment
./scripts/safe-run-prod
```

#### Migration from Legacy

The new script replaces the old `inventory/dynamic_inventory.py` and `inventory/dynamic_inventory.sh` with enhanced features:

- Better error handling and fallbacks
- Production safety mechanisms
- Connectivity validation
- Automatic backup creation
- Environment-specific configurations

## Troubleshooting

1. Enable debug output:

   ```sh
   ansible-playbook main.yml -vvv -i inventory/[env]/hosts.yml
   ```

2. Run in check mode:

   ```sh
   ansible-playbook main.yml --check -i inventory/[env]/hosts.yml
   ```

3. Common Issues:
   - Insufficient system resources
   - Network connectivity problems
   - Permission issues
   - Shell configuration conflicts
