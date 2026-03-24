# Change log

# version 3.0.0

- Updated to use the `community.proxmox` collection instead of the now deprecated Proxmox modules that have been removed from `community.general`.
- Changed the default of `datacenter_local_storage_content` to include `import` instead of `images`.
- Set `datacenter_add_configs_storage` default value to `false`. This has possibly caused issues when upgrading Proxmox VE versions. Having this located under `/etc/pve` may be causing an issue. The task was left in the role for those that want to use it but it would be better to add snippets to some other shared storage.

# version 2.0.0

### Fully breaking changes

- Removed the `proxmox_ve` role.
  Created a new [`proxmox_ve`](https://github.com/cloudcodger/proxmox_ve) collection for everything this role did.
- Replaced the `proxmox_datacenter` role with the `datacenter` role.
  The new role has different variable naming to pass linting.
- Removed the `proxmox_snippet` role. This was more of a showcase on how to do this and not a good role.
- Removed the `pve_exporter` role. Moved to the new `proxmox_ve` collection.
  The new `datacenter` role creates an `Auditor` group and an auditor token `exporter@pve!prometheus` for use by the role. The other tasks did not belong with the openssh items here.

# version 1.3.1

- Added the `pve_exporter` role.
- Minor README.md file changes.

# version 1.2.1

- Fix to prevent `proxmox_ve` from removing sym-link to `authorized_keys` for `root` user.

# version 1.2.0

- Added port and sudo to the proxmoxer ssh connections in `proxmox_opsnssh.py` module util. - Rina-Y

# version 1.1.0

- Added the `proxmox_snippet` role.

# version 1.0.3

- Removed no longer supported `get_md5`.

# version 1.0.2

- Fixed `proxmox_ve` wait for file that had a hard coded value.

# version 1.0.1

- Fixed `proxmox_storage_dir` improper check for `shared` as bool.
- Updated `README.md`.

# version 1.0.0

- The initial release
