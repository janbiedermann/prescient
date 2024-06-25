# Pres**ci**ent for Linux or Windows hosts using VirtualBox

## System Requirements

- VirtualBox 7.0 or greater on one or more *nixish hosts
- Git on one or more *nixish hosts, acting as git server(s)
- OpenSSH
- sh, zip, unzip, ssh, sshpass, shuf, grep, awk, timeout, tee, sed
- at, when using nq
- PowerShell on Windows VMs

## Installation and Configuration

The system consists of:
- git server, which triggers task runs on the executing hosts
- executing hosts, which execute the virtual machines
- virtual machines, which execute the tasks

They may be all on one machine or separate machines.

### Executing Hosts

Linux and Windows are supported. Choose either, when using Windows a Server version is recommended.

#### Linux

- install VirtualBox
- install nq or laminar
- when using nq, ensure cron/at works
- install unzip
- install sshpass
- ensure shuf, tee, timeout, awk, grep, ssh are available
- configure a user for running the virtual machines, the users shell should be sh compatible
- create the `$HOME/.prescient` directory, it is used to store some configuration and temporary repository data, it may need some space
- ports between 30000 and 40000 on localhost will be used by virtual machines

#### Using Windows as Executing Host

- install VirtualBox
- install cygwin with the tools as above as in section "Linux"
- use OpenSSH from cygwin to get bash as shell, run it as service, enable PermitUserEnvironment
- configure user as above
- add path of vboxmanage.exe to PATH in $HOME/.bashrc
- you may need to install in cygwin make and gcc-core, git, to clone and compile nq or laminar
- set env in .ssh/environment (`env > .ssh/environment` and cleanup connection specific vars)

#### When using Laminar

Ensure sed is available.
Ensure laminar can access the virtual machines. Easiest is to use the user configured for laminar for configuring the virtual machines too.

Copy `laminar/prescient.run*` to `/var/lib/laminar/cfg/jobs/` on the executing host, it will be linked to from post-receive.

The configuration examples provided in the laminar dir can be used to operate several execution hosts with one context/executor/queue per host.

When using the laminar host as executing host, ensure one executor and one context for executing the vms.
To achieve this, `context.conf` with `context_local.env` can be used, both named accordingly following the laminar docs and to your preferences.

### Virtual Machines on the Executing Hosts

Shells on on the VMs must support `echo`, `;` as command delimiter and the `$HOME` variable must be set.
This is true for most shells, also for PowerShell.

#### Windows

- configure the first network interface as NAT
- install VirtualBox Guest Utilities for performance
- install the latest [OpenSSH](https://github.com/PowerShell/Win32-OpenSSH), do not use the version included in Windows, its usually far beheind and does not work right
- make sure the host user can login via ssh using a password
- PowerShell must be available in the path when executing commands via ssh
- PowerShell must also be the [default shell](https://github.com/PowerShell/Win32-OpenSSH/wiki/DefaultShell) when logging in via ssh
- There may be problems with shutting down the machine, for a solution see [contrib/Add_Enable_forced_button...](/contrib/Add_Enable_forced_button-lid-shutdown_to_Power_Options.reg)

#### Linux

- configure the first network interface as NAT
- install VirtualBox Guest Utilities for performance
- install OpenSSH sshd
- make sure the host user can login via ssh using a password
- unzip must be available in the path when executing commands via ssh

#### BSD and others

- configure the first network interface as NAT
- install OpenSSH sshd
- make sure the host user can login via ssh using a password
- unzip must be available in the path when executing commands via ssh

### Git server(s)

- install at
- install shuf
- install zip
- create a `/var/lib/prescient` directory, make it writeable for the git server user, that executes the git hooks
- `/var/lib/prescient` is used to store the logs when using nq, give it some space
- configure git user and bare repos
- make sure the git server user, that executes the git hooks, can access the executing host and login via ssh public key authentication as the user, that can run and manage the virtual machines
- create and edit /etc/prescient.conf, see below
- install the git hooks in the bare repos, see below
- /tmp is used for temporary repository data, it may need some space
- make sure, the git user can schedule commands using at, eg. on FreeBSD add it to /var/at/at.allow

### /etc/prescient.conf

In this configuration file the available virtual machines are configured. It uses a very simple syntax. Each line defines a vm, each item on a line is separated by `|`, order of items is important.
It must be available on the git servers.

Example line:
`windows|host|host_user|WindowsVM|vm_user|vm_pass`

- First item: The machine name for the vm for usage by developers in the `.prescient` file (see below), in the example: `windows`
- Second item: The hostname or IP of the host where the vm is situated, the executing host, in the example: `host`
- Third item: The username, that is used by the git server user to ssh into the executing host, in the example `host_user`
- Fourth item: The name of the VM to start, in the example: `WindowsVM`
- Fifth item: The vm user to use, to execute scripts within the vm, in the example: `vm_user`
- Sixth item: The password for the vm user, to execute scripts within the vm, in the example: `vm_pass`

Yes, using clear text passwords. Scipts are easily adaptable to use public key auth, just grep for sshpass and change these lines accordingly after setting up the vms for public key auth.

### Git Hooks

#### When using nq

Copy the `nq/post-receive` git hook to each bare repos `hooks` directory, that is meant to be served for CI, or alternatively create a symbolic link to the script from a safe place (makes updating the hook easier). The git hook is written for sh. Make sure the git hook is executable.

#### When using Laminar

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

On the executing hosts the scripts will call a "plugin script" if it exists, right after the actual CI script has been executed on the VM.
The plugin scripts may be used to cache installed software or anything else.
They must be located in the `~/prescient` directory of the host user and must be named after the VM plus the '_plugin' suffix. For example with a VM named 'Windows10' the plugin script must be named 'Windows10_plugin':

`~/prescient/Windows10_plugin`

The script will be called with the name of original VM and name of the currently running VM, the VM user and password and ssh port, like:

`./prescient/Windows10_plugin Windows10 Windows10_Prescient vm_user vm_user_pass ssh_port`

In the contrib directory of this repo is a example plugin script, that caches Ruby gems.

## Execution log

When using nq, the execution log will be copied to the git server(s) `/var/lib/prescient`, to a directory named after the repo, commit and machine, eg: `/var/lib/prescient/my_repo.gi/d5660703f412dc854f8548b845b34eafe0ca3e6e_machine.log`.
When using laminar, it will be available from the web interface.

## prescient.cgi

![prescient.cgi screenshot](/contrib/prescient_cgi_screenshot.png)

If you have a web server on the git server, the `contrib/prescient.cgi` will provide a nice formatted overview of the CI runs.
It is a very simple sh script, that scans the log files for the pattern `[0-9]+ errors`, `[0-9]+ failures`, `[0-9]+ skips`, `[0-9]+ pending`, all case insensitive.
To use it, copy it to the cgi-bin directory of the web server and make it executable.

## Hints

- use '/' for paths also on Windows
- Apache 2 config snippet for serving result logs from `/var/lib/prescient`:
```
Alias /prescient/ "/data/prescient/"
<Directory "/data/prescient/">
   AllowOverride None
   Options Indexes
   Require all granted
</Directory>
```
- running multiple different VMs on the same host at the same time can be achieved by using a different host user per VM
- Scaling up! To run multiple VMs of the same kind on multiple hosts or multiple VMs of the same kind at the same host,
  simply add more lines with the same machine specifier for developers, but vary either host or user or both.
  The actual VM will be randomly selected at the time of commit, example:
```
windows|ci_host_1|ci_user_1|WindowsVM|vm_user|vm_pass
windows|ci_host_1|ci_user_2|WindowsVM|vm_user|vm_pass
windows|ci_host_2|ci_user_1|WindowsVM|vm_user|vm_pass
windows|ci_host_2|ci_user_2|WindowsVM|vm_user|vm_pass
```
- to follow and debug VM execution when using nq, login to the execution host and use `fq`
- when you want to change configuration of a VM and jobs are still enqueued, simply write a small script and enqueue the script from the host users $HOME directory with `nq my_change_script`, it will be nicely queued in. See `contrib/cmdvm.sh` for a start.
- when something goes wrong, places to look: on the git server the `/tmp/prescient*` directories, on the execution hosts the `$HOME/.prescient/*` directories and files
- for debugging you may use `set -x` in the sh scripts
