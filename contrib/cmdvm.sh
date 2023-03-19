#!/bin/sh
# simple script to start a vm for service with a random ssh port or execute a command_file
# run like: ./startvm.sh MyVM username password [command_file]
# each line of the optional command_file is executed seprately in order, when command_file is given
# without the command_file option, the vm is only started for further manual access
vm=$1
vm_user=$2
vm_user_pass=$3
command_file=$4

if [ -z "$vm" ] || [ -z "$vm_user" ] || [ -z "$vm_user_pass"]; then
  echo "Execute like:"
  echo "cmdvm.sh VMName vm_user vw_user_password [optional_script]"
  exit 1
fi

vm_port=`shuf -i 30000-40000 -n 1`

vboxmanage startvm "$vm" --type=headless
vboxmanage controlvm "$vm" natpf1 delete cmd_ssh 2>/dev/null
vboxmanage controlvm "$vm" natpf1 "cmd_ssh,tcp,127.0.0.1,$vm_port,,22"

echo "listening on port $vm_port"

started=''
while [ -z "$started" ]; do
  started=`sleep 10; sshpass -p "$vm_user_pass" ssh -n -o LogLevel=ERROR -o ConnectTimeout=10 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -l "$vm_user" -p $vm_port 127.0.0.1 'echo started' 2>/dev/null`
done

echo "'$vm' ready"

if [ -n "$command_file" ]; then
  echo "Command file '$command_file' given."
  while read -r command <&3; do
    echo "Executing command: $command"
    timeout 1h sshpass -p "$vm_user_pass" ssh -n -o LogLevel=ERROR -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -l "$vm_user" -p $port 127.0.0.1 "$command" 2>&1 | tr -d '\r'
  done 3< "$command_file"
  echo "All done, shutting down."
  vboxmanage controlvm "$vm" natpf1 delete cmd_ssh
  vboxmanage controlvm "$vm" acpipowerbutton 2>&1
  running=`vboxmanage list runningvms | grep "$vm"`
  while [ -n "$running" ]; do
    running=`sleep 10; vboxmanage list runningvms | grep "$vm"`
  done
fi
