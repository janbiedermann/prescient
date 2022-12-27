# pres**ci**ent

A simple, reliable, *nixish continuous integration for Git and VirtualBox in ~150 lines of bash.

## System Requirements

- VirtualBox on one or more *nixish hosts
- Git on one or more *nixish hosts, acting as git server(s)
- OpenSSH
- bash, at, zip, unzip, ssh, sshpass, shuf, grep, awk
- [nq](https://github.com/leahneukirchen/nq)
- PowerShell on Windows VMs

## Installation and Configuration

### Executing Hosts

- Linux is recommended
- install nq, probably something like `apt install nq`
- install at
- install VirtualBox
- install unzip
- install sshpass
- configure a user for running the virtual machines, the users shell should be bash
- ports between 30000 and 40000 on localhost will be used by virtual machines

### Virtual Machines on the Executing Hosts

Shells on on the VMs must support `echo`, `;` as command delimiter and the `$HOME` variable must be set.
This is true for most shells, also for PowerShell.

#### Windows

- configure the first network interface as NAT
- install VirtualBox Guest Utilities for performance
- install [OpenSSH](https://github.com/PowerShell/Win32-OpenSSH)
- make sure the host user can login via ssh using a password
- PowerShell must be available when logging in via ssh
 
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
- install zip
- create a `/var/lib/prescient` directory, make it writeable for the git server user, that executes the git hooks
- configure git user and bare repos
- make sure the git server user, that executes the git hooks, can access the executing host and login via ssh public key authentication as the user, that can run and manage the virtual machines
- create and edit /etc/prescient.conf, see below
- install the git hooks in the bare repos, see below

### /etc/prescient.conf

In this configuration file the available virtual machines are configured. It uses a very simple syntax. Each line defines a vm, each item on a line is separated by `|`, order of items is important.

Example line:
`windows|host|host_user|WindowsVM|vm_user|vm_pass`

- First item: The machine name for the vm for usage by developers in the `.prescient` file (see below), in the example: `windows`
- Second item: The hostname or IP of the host where the vm is situated, in the example: `host`
- Third item: The username, that is used by the git server user to ssh into the vm host, in the example `host_user`
- Fourth item: The name of the VM to start, in the example: `WindowsVM`
- Fifth item: The vm user to use, to execute scripts within the vm, in the example: `vm_user`
- Sixth item: The password for the vm user, to execute scripts within the vm, in the example: `vm_pass`

### Git Hooks

Copy the `post-receive` git hook to each bare repos `hooks` directory, that is meant to be served for CI, or alternatively create a symbolic link to the script from a safe place (makes updating the hook easier). The git hook is written for bash. Make sure the git hook is executable.

## Usage from within the developers git repository

Developers create a `.prescient` file in the repo.
It contains the names of the virtual machines, that are meant to be used by developers, as configured in `/etc/prescient.conf` (first item), and the commands to execute from within the repo, for example:
```
windows:powershell -Command prescient_ci/windows.bat
linux:bash -l prescient_ci/linux.sh
```
Machine names for developers (first item of /etc/prescient.conf) must match the pattern `[a-zA-Z0-9_-]+`
Depending on VM configuration, it may be required to use a login shell on *nixish VMs.

When pushing to the git server, it will tell when CI runs are enqueued:
```
... git messages ...
remote: Enqueueing CI run for c4168a062696c632850efc8a19aaf38b9905e2c3 on 'windows'.
remote: Enqueueing CI run for c4168a062696c632850efc8a19aaf38b9905e2c3 on 'linux'.
... git messages ...
```

## Provisioning of VMs and Execution of Scripts

With each push to the git server(s) above, the git hook enqueues the execution of the scripts in the `.prescient.conf` file on the specified machines. On the VM host, when the queue is ready, execution will start:

- First, the determined target VM will be cloned, a snapshot of the clone will be prepared, this snapshot will then be used for the actual execution. Cloning of the vm will happen only, if a change on the original vm has been detected, or a clone doesn't exist yet.
- The snapshot will be started.
- The git repo will copied to the vm
- The command as specified in the `.prescient.conf` file of the repo will be executed from within the checked out repo via ssh

### Plugin Scripts

On the executing hosts the scripts will call a "plugin script" if it exists, right after the actual CI script has been executed on the VM.
The plugin scripts may be used to cache installed software or anything else.
They must be located in the `~/prescient` directory of the host user and must be named after the VM, example with a VM named 'Windows10':

`~/prescient/Windows10`

The script will be called with the name of original VM and name of the currently running VM, the VM user and password and ssh port, like:

`./prescient/Windows10 Windows10 Windows10_Prescient vm_user vm_user_pass ssh_port`

In the contrib directory of this repo is a example plugin script, that caches Ruby gems.

## Execution log

The execution log will be copied to the git server(s) `/var/lib/prescient`, to a directory named after the repo, commit and machine, eg: `/var/lib/prescient/my_repo.gi/d5660703f412dc854f8548b845b34eafe0ca3e6e_machine.log`

## prescient.cgi

![prescient.cgi screenshot](/contrib/prescient_cgi_screenshot.png)

If you have a web server on the git server, the `contrib/prescient.cgi` will provide a nice formatted overview of the CI runs.
It is a simple bash script, that scans the log files for the pattern `[0-9]+ errors`, `[0-9]+ failures`, `[0-9]+ skips`.
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
- to follow and debug VM execution, login to the execution host and use `fq`
- when you want to change configuration of a VM and jobs are still enqueued, simply write a small script and enqueue the script from the host users $HOME directory with `nq my_change_script`, it will be nicely queued in.
