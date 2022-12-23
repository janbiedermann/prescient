# pres**ci**ent

A simple, reliable, *nixish continuous integration for Git and VirtualBox in ~140 lines of bash.

## System Requirements

- VirtualBox on one or more *nixish hosts
- Git on one or more *nixish hosts, acting as git server(s)
- ssh for public key access and command execution
- bash, at, zip, unzip
- [nq](https://github.com/leahneukirchen/nq)

## Installation and Configuration

### Executing Hosts

- install nq, probably something like `apt install nq`
- install VirtualBox
- install unzip
- configure a user for running the virtual machines
- ensure the git server(s) can access the executing host and login via ssh and manage the virtual machines

### Virtual Machines on the Executing Hosts

- install OS according to your requirements
- on *nixish vms, the vm users home directory must be in /home/ and bash must be available at /bin/bash
- on Windows vms, the vm users home directory must be in C:/Users/

### Git server(s)

- install at
- install zip
- create a `/var/lib/prescient` directory, make it writeable for the git server user, that executes the git hooks
- configure git user and bare repos
- make sure the git server user, that executes the git hooks, can ssh into the executing hosts and manage the virtual machines
- create and edit /etc/prescient.conf, see below
- install the git hooks in the bare repos, see below

### /etc/prescient.conf

In this configuration file the available virtual machines are configured. It uses a very simple syntax. Each line defines a vm, each item on a line is separated by `|`, order of items is important.

Example line:
`windows|ci_host|ci_user|WindowsVM|vm_user|vm_pass`

- First item: The machine name for the vm for usage by developers in the `.prescient` file (see below), in the example: `windows`
- Second item: The hostname or IP of the host where the vm is situated, in the example: `ci_host`
- Third item: The username, that is used by the git server user to ssh into the vm host, in the example `ci_user`
- Fourth item: The name of the VM to start, in the example: `WindowsVM`
- Fifth item: The vm user to use, to execute scripts within the vm, in the example: `vm_user`
- Sixth item: The password for the vm user, to execute scripts within the vm, in the example: `vm_pass`

### Git Hooks

Copy the `post-receive` git hook to each bare repos `hooks` directory, that is meant to be served for CI. The git hook is written for bash. Make sure the git hooks is executable.

## Usage from within the developers git repository

Developers create a `.prescient` file in the repo.
It contains the names of the virtual machines, that are meant to be used by developers, as configured in `/etc/prescient.conf` (first item), and the commands to execute from within the repo, for example:
```
windows:.prescient_ci/windows.bat
linux:.prescient_ci/linux.sh
```

## Provisioning of VMs and Execution of Scripts

With each push to the git server(s) above, the git hook enqueues the execution of the scripts in the `.prescient.conf` file on the specified machines. On the VM host, when the queue is ready, execution will start:

- First, the determined target VM will be cloned, a snapshot of the clone will be prepared, this snapshot will then be used for the actual execution. (Cloning of the vm will happen only, if a change on the original vm has been detected, or a clone doesn't exist yet.)

- The snapshot will be started.

- The git repo will copied to the vm

- The command as specified in the `.prescient.conf` file of the repo will be executed from within the checked out repo

## Execution log

The execution log will be copied to the git server(s) `/var/lib/prescient` directory named after the repo, commit and machine, eg: `/var/lib/prescient/my_repo.gi/d5660703f412dc854f8548b845b34eafe0ca3e6e_machine.log`

## Hints

- use '/' for paths also on Windows
- machine names (first item of /etc/prescient.conf) must match the pattern [a-zA-Z0-9_-]+
