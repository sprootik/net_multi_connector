#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pprint import pprint
from multi_connector import net

# create list of hosts
hosts = [net.Host(name='R1', ip='192.168.122.2'),
         net.Host(name='R2', ip='192.168.122.3'),
         net.Host(name='R3', ip='172.17.3.1'),
         net.Host(name='R4', ip='172.17.4.1', dev_type='cisco_ios'),
         net.Host(name='not_exist', ip='1.1.1.1')
         ]

# create lost of commands
commands = ["show interfaces description", "show ip interface brief"]

# initialize connection
connector = net.MultiNetConnect(login='test', password='test', hosts=hosts,
                                enable_password='test')

# connect and run commands
result = connector.multy_connect(commands=commands, process=1,
                                 threads_per_process=5)
pprint(result)

# only detect dev type without run commands
commands = ["test"]
connector.multy_connect(commands=commands, process=1, threads_per_process=5,
                        update_dev_type=True)
hosts = connector.hosts
pprint(hosts)

# run command in config mode
commands = ["interface loopback 1", "description TEST"]
connector = net.MultiNetConnect(login='test', password='test', hosts=hosts,
                                enable_password='test', cli_mode='config')
result = connector.multy_connect(commands=commands, process=1,
                                 threads_per_process=5)
pprint(result)
