The `pve_exporter` Role
=======================

Install the Python `prometheus-pve-exporter` module and configure it to gather metrics for Grafana Prometheus or Grafana Mimir.

Requirements
------------

- Proxmox_VE installed on hosts.
- Python `proxmoxer` module.
- Python `openssh_wrapper` module.

Role Variables
--------------

**`pve_exporter_api_host`**

Default: Unset

The host for all Proxmox API calls for creating the Datacenter User and API Token. Otherwise, either a token file must exist that can be read or the token must be provided with `pve_exporter_datacenter_token_secret`.

**`pve_exporter_api_port`**

Default: `22`

The SSH port for connecting to `pve_exporter_api_host`.

**`pve_exporter_api_sudo`**

Default: `false`

If SSH will need to use `sudo` when running commands on `pve_exporter_api_host`.

**`pve_exporter_api_user`**

Default: `root`

The SSH user for connecting to `pve_exporter_api_host`.

**`pve_exporter_config_directory`**

Default: `/etc/prometheus`

The directory where the `pve_exporter_config_file` configuration file is created.

**`pve_exporter_config_file`**

Default: `pve.yml`

The name of the configuration file.

**`pve_exporter_datacenter_token_name`**

Default: `prometheus`

The name of the API token used by exporter to gather metrics, along with the `pve_exporter_datacenter_user`.
This is used as part of the local Secrets file name.
This, and the ACLs for it, will be created when `pve_exporter_api_host` is set.

**`pve_exporter_datacenter_token_secret`**

Default: `""`

The API token secret used by exporter to gather metrics.
This will be created during the creation of the token when `pve_exporter_api_host` is set. Otherwise, it must either be read from the secrets file or provided.

**`pve_exporter_datacenter_user`**

Default: `exporter@pve`

The Datacenter user used by exporter to gather metrics, along with the `pve_exporter_datacenter_token_name`.
It must be specified in the `user@realm` format.
This will be created when `pve_exporter_api_host` is set.

**`pve_exporter_datacenter_verify_ssl`**

Default: `false`

Declare if SSL is used by exporter to gather metrics.

**`pve_exporter_directory`**

Default: `/opt/prometheus-pve-exporter`

The directory that will contain a Python virtual environment. This will have the `prometheus-pve-exporter` module installed in it and run from it.

**`pve_exporter_token_secret_prefix` and `pve_exporter_token_secret_suffix`**

Default: `""`

These are used to add a prefix and/or suffix to the local secrets file name. The file name is built from these along with the `pve_exporter_datacenter_user` (the `@` is replaced with a `-`) and the `pve_exporter_datacenter_token_name`, with `.token` appended to it. The file is located in the `pve_exporter_token_secrets_dir`.

**`pve_exporter_token_secrets_dir`**

Default: `~/.pve_tokens`

The directory in which the `pve_exporter_datacenter_token_secret` will be read. And potentially created.

**`pve_exporter_user`**

Default: `pve-exporter`

The system User that will run the `prometheus-pve-exporter` systemd service.

Dependencies
------------

When setting `pve_exporter_api_host`, the control node must be able to SSH into that host without requesting a password or prompting to accept the host key. If the datacenter user and API token are not created using this role, then they must exist and the token secret must either be provided placing it in a properly named secrets file or set using `pve_exporter_datacenter_token_secret`.

Example Playbook
----------------

```yml
---
- name: Configure Alloy on the Proxmox PVE hosts.
  hosts: proxmox_hosts

  vars:
    pve_exporter_api_host: "{{ groups['proxmox_hosts'] | first }}"

  roles:
    - role: proxmox_openssh_pve_exporter
```
