<img src="https://raw.githubusercontent.com/janbiedermann/prescient/master/prescient.webp" alt="Prescient">
<small>(Original Image by <a href="https://www.freepik.com/free-photo/fortune-teller-with-crystal-globe-front-view_35816174.htm">Freepik</a>)</small>

# Pres**ci**ent

A simple, reliable continuous integration for Git and FreeBSD hosts with bhyve and [laminar](https://github.com/ohwgiles/laminar) in ~150 lines of sh.
Running forever with little maintenenace required.
But installtion is a long read and may needs some patience and learning.

For a Linux and VirtualBox version see branch "linux".

## Features

- use any script language you love for CI runs, no need for YAML
- using very little CPU/RAM resources for itself
- can scale up to many virtual machines on different hosts
- very adaptable to individual needs, just a few lines of sh

## Installation and Configuration

### Overview

The system consists of:
- a Git Server, which triggers task
- a Laminar Server, which queues and schedules the tasks
- one or more Executing Hosts, which execute the Virtual Machines
- Virtual Machines on the excuting hosts, which execute the tasks

They may be all on one machine or separate machines.

```
+------------+       +----------------+
| Git Server |------>| Laminar Server |
+------------+       +----------------+
                     /       |        \
                    /        |         \
                   /         |          \
  +----------------+ +----------------+
  | Executing Host | | Executing Host |  ...
  | VM | VM | ...  | | VM | VM | ...  |
  +----------------+ +----------------+
```

Other variations, e.g. several Git Servers or Lmainar Servers, are absolutely possible with slight adaption of the configuration.

### Git Server

- recommended OS: FreeBSD 14.1 or later
- install zip: `pkg install zip`
- install git: `pkg install git`
- add a `git` user for the repos, and a few bare repos
- make sure the `git` user, that executes the git hooks, can access the Laminar Server and login via ssh public key authentication as the user, that can schedule laminar tasks, e.g. `laminar`, see below
- copy prescient_g2l.conf from the repo to /usr/local/etc/prescient_g2l.conf, edit accordingly
- install the git hooks in the bare repos, see below
- /tmp is used for temporary repository data, it may need some space
- ensure the `git` user can login to the Laminar Server as `laminar` user via ssh using public keys

### Laminar Server

- recommended OS: FreeBSD 14.1 or later
- install laminar: `pkg install laminar`
- install sudo: `pkg install sudo`

By default the laminar package uses the www user. Its best to use a separate user for laminar.
Add a user `laminar` to the system.
Change the user in /usr/local/etc/rc.d/laminard accordingly.
Ensure parmissions for the laminar directory match the new user: `chown -R laminar:laminar /var/db/laminar`.

Ensure laminar can start vms by giving it access to the `vm` command via sudo.
Create a file `/usr/local/etc/sudoers.d/laminar` with the following content: `laminar ALL=(root:wheel) NOPASSWD: /usr/local/sbin/vm`

Copy `laminar/prescient.run*` from the repo to `/var/db/laminar/cfg/jobs/` on the executing host, it will be linked to from post-receive.

The context examples provided in the laminar dir can be used to operate several execution hosts with one context/executor/queue per host.

See the official laminar documentatio about [Contexts](https://laminar.ohwg.net/docs.html#Contexts).

In case the Laminar server shall also function as a Exuting Host, the `context.conf` with `context_local.env` can be used, renamed according to the laminar documentation.

When using additional hosts as Executing Hosts, the `context.conf` with `context_remote.env` can be used, adapted and renamed according to the laminar documentation and your environment. One context per Executing Host must be used.

### Executing Hosts

- recommended OS: FreeBSD 14.1 or later, but may work with other operating systems that are compatible with vm-bhyve
- install unzip, `pkg install unzip`
- install sshpass, `pkg install sshpass`
- install vm-bhyve, `pkg install vm-bhyve`
- install sudo, `pkg install sudo`
- ensure sed, shuf, tee, timeout, awk, grep, ssh are available
- configure a user for running the virtual machines, the users shell should be sh compatible
- create the `$HOME/.prescient` directory, it is used to store some configuration and temporary repository data, it may need some space

### Virtual Machines on the Executing Hosts

Shells on on the VMs must support `echo`, `;` as command delimiter and the `$HOME` variable must be set.
This is true for most shells, also for PowerShell.

In general follow instructions for [vm-bhyve](https://github.com/churchers/vm-bhyve) on how to setup virtual machines, however ensure you use ZFS for all disk devices so that snapshots work.

#### Windows

- follow instructions in the [vm-bhyve wiki](https://github.com/churchers/vm-bhyve/wiki/Running-Windows)
- install the latest [OpenSSH](https://github.com/PowerShell/Win32-OpenSSH), do not use the version included in Windows, its usually far behind and does not work right
- make sure the host user can login via ssh using a password
- PowerShell must be available in the path when executing commands via ssh
- PowerShell must also be the [default shell](https://github.com/PowerShell/Win32-OpenSSH/wiki/DefaultShell) when logging in via ssh
- There may be problems with shutting down the machine, for a solution see [contrib/Add_Enable_forced_button...](/contrib/Add_Enable_forced_button-lid-shutdown_to_Power_Options.reg)

#### Linux, BSD and others

- install OpenSSH sshd
- make sure the host user can login via ssh using a password
- unzip must be available in the path when executing commands via ssh



### /etc/prescient.conf

In this configuration file the available virtual machines are configured. It uses a very simple syntax. Each line defines a vm, each item on a line is separated by `|`, order of items is important.
It must be available on the git servers.

Example line:
`windows|exehost|exehost_user|WindowsVM|windows-vm|vm_user|vm_pass`

- First item: The machine name for the vm for usage by developers in the `.prescient` file (see below), in the example: `windows`
- Second item: The hostname or IP of the host where the vm is situated, the executing host, in the example: `exehost`
- Third item: The username, that is used by the git server user to ssh into the executing host, in the example `exehost_user`
- Fourth item: The name of the VM to start, in the example: `WindowsVM`
- Fifth item: The hostname of the VM to connect to via ssh: `windows-vm`
- Sixth item: The port of the VM to connect to via ssh: `22`
- Seventh item: The vm user to use, to execute scripts within the vm, in the example: `vm_user`
- Eigth item: The password for the vm user, to execute scripts within the vm, in the example: `vm_pass`

Yes, using clear text passwords. Scipts are easily adaptable to use public key auth, just grep for sshpass and change these lines accordingly after setting up the vms for public key auth.

### Git Hooks

Copy the `laminar/post-receive` git hook to each bare repos `hooks` directory, that is meant to be served for CI, or alternatively create a symbolic link to the script from a safe place (makes updating the hook easier). The git hook is written for sh. Make sure the git hook is executable.

## Usage from within the developers git repository

Developers create a `.prescient` file in the repo.
It contains the names of the virtual machines, that are meant to be used by the tasks, as configured in `/etc/prescient.conf` (first item), and the commands to execute from within the repo, for example:
```
windows:powershell -Command prescient_ci/windows.bat
linux:bash -l prescient_ci/linux.sh
```
Machine names for developers (first item of /etc/prescient.conf) must match the pattern `[a-zA-Z0-9_-]+`

Depending on VM configuration, it may be required to use a login shell on *nixish VMs to execute commands.

When pushing to the git server, it will tell when CI runs are enqueued:
```
... git messages ...
remote: Enqueueing CI run for c4168a062696c632850efc8a19aaf38b9905e2c3 on 'windows'.
remote: Enqueueing CI run for c4168a062696c632850efc8a19aaf38b9905e2c3 on 'linux'.
... git messages ...
```

Job execution will timeout after 12 hours.

Example integration:

[speednode](https://github.com/janbiedermann/speednode)

- [`.prescient`](https://github.com/janbiedermann/speednode/blob/master/.prescient)
- [CI scripts](https://github.com/janbiedermann/speednode/tree/master/ci)

## Provisioning of VMs and Execution of Scripts

With each push to the git server(s) above, the git hook enqueues the execution of the scripts in the `.prescient.conf` file on the specified machines. On the executing host, when the queue is ready, execution will start:

- First, the determined target VM will be cloned from a snapshot of the original VM, creating a linked clone, a snapshot of the clone will be prepared, this snapshot will then be used for the actual execution. Cloning of the vm will happen only, if a change on the original vm has been detected, or a clone doesn't exist yet.
- The snapshot will be started.
- The git repo will copied to the vm
- The command as specified in the `.prescient.conf` file of the repo will be executed from within the checked out repo via ssh

### Plugin Scripts

On the executing hosts the scripts will call "plugin scripts" if they exists.
The plugin scripts may be used to cache installed software or anything else.
They must be located in the `~/prescient` directory of the host user and must be named after the VM plus the `_plugin_after_ci` or `_plugin_after_poweroff` suffix.
For example with a VM named 'Windows10' the plugin scripts must be named:

`~/prescient/Windows10_plugin_after_ci` and `~/prescient/Windows10_plugin_after_poweroff`

The script will be called with the following args:
- the name of VM
- the VM hostname
- the VM ssh port
- the VM user
- the VM users password

For example: `./prescient/Windows10_plugin Windows10 windows-vm 22 vm_user vm_user_pass`

In the contrib directory of this repo there are example plugin scripts, that cache Ruby gems.

The `_plugin_after_ci` script is called, while the VM is still running. It can be used to gather information from the VM after the ci run, like for example a list of Ruby gems installed during the run.
The `_plugin_after_poweroff` script is called after everything is cleaned up and the VM powered off. It can be used to prepare the VM for the next run, like for example installing Ruby gems known to be required.

## Hints

- use '/' for paths also on Windows
- Scaling up! To run multiple VMs of the same kind on multiple hosts or multiple VMs of the same kind at the same host,
  simply add more lines with the same machine specifier for developers, but vary either host or user or both.
  The actual VM will be randomly selected at the time of commit, example:
```
windows|ci_host_1|ci_user_1|WindowsVM|vm_user|vm_pass
windows|ci_host_1|ci_user_2|WindowsVM|vm_user|vm_pass
windows|ci_host_2|ci_user_1|WindowsVM|vm_user|vm_pass
windows|ci_host_2|ci_user_2|WindowsVM|vm_user|vm_pass
```
- when something goes wrong, places to look: on the git server the `/tmp/prescient*` directories, on the execution hosts the `laminar` user `$HOME/.prescient/*` directories and files
- for debugging you may use `set -x` in the sh scripts
