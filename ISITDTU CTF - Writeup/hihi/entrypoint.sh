#!/bin/bash
set -e

rm /bin/sleep
rm /usr/bin/apt

iptables -P OUTPUT DROP

iptables -P INPUT ACCEPT

iptables -A OUTPUT -o lo -j ACCEPT
iptables -A INPUT -i lo -j ACCEPT


iptables -A OUTPUT -p udp --dport 53 -j ACCEPT
iptables -A OUTPUT -p tcp --dport 53 -j ACCEPT


iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT


iptables -A OUTPUT -j DROP

RANDOM_NAME=$(head /dev/urandom | tr -dc a-z0-9 | head -c 12)

mv flag.txt "$RANDOM_NAME"

chattr +i $RANDOM_NAME

exec java -jar /app/app.jar
