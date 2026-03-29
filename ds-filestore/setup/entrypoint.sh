#!/bin/bash
service cron start
/usr/sbin/sshd
exec /usr/sbin/vsftpd /etc/vsftpd.conf
