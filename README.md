![](https://img.shields.io/badge/python-3.10-green)   
Eng | [Rus](./README-ru.md)
# net_multi_connector  

Module for multi-threaded connection to network hardware. Based on the netmiko library.

This module allows you to connect to n processes with m threads each. By adjusting the number of processes and threads, we can increase the load on the processors and reduce the running time, or reduce the load on the processors, but increase the running time.

### examples
Examples usage examples are in [examples.py](./examples.py) 

Create a list of hosts and executable commands  


    from multi_connector import net

    hosts = [net.Host(name='R1', ip='192.168.122.2'),
            net.Host(name='R2', ip='192.168.122.3'),
            net.Host(name='R3', ip='172.17.3.1'),
            net.Host(name='R4', ip='172.17.4.1', dev_type='cisco_ios'),
            net.Host(name='not_exist', ip='1.1.1.1')
            ]

    commands = ["show interfaces description", "show ip interface brief"]

Each host must be written to a named tuple Host. If dev_type is not specified, automatic detection occurs. It is also possible to perform only detection without executing commands (see [examples.py](./examples.py) ).

Create an instance of the connector class  

    connector = net.MultiNetConnect(login='test', password='test', hosts=hosts,
                                    enable_password='test')

When passing a list of hosts in the initializer, the datadescriptor is triggered, which removes duplicates based on the ip address, or the name and ip address. The validity of the passed parameters is also checked.

We connect to the equipment and execute commands from privileged mode. It is also possible to execute commands from configuration mode (see [examples.py](./examples.py) ).

    result = connector.multy_connect(commands=commands, process=1,
                                    threads_per_process=5)

In this case, we use one process and 5 threads in it. Accordingly, the task execution time will be equal to its execution time on one (slowest) host. If process*threads_per_process is less than the number of hosts, processing is iterative (parts).

Execution result:

    [Result(name='R2', ip='192.168.122.3', dev_type='cisco_ios', commands=['Interface                      Status         Protocol Description\nGi0/0                          up             up       to WAN\nGi0/1                          down           down     \nGi0/2                          down           down     \nGi0/3                          down           down     ', 'Interface                  IP-Address      OK? Method Status                Protocol\nGigabitEthernet0/0         192.168.122.3   YES NVRAM  up                    up      \nGigabitEthernet0/1         unassigned      YES NVRAM  down                  down    \nGigabitEthernet0/2         unassigned      YES NVRAM  down                  down    \nGigabitEthernet0/3         unassigned      YES NVRAM  down                  down    ']),
    Result(name='R3', ip='172.17.3.1', dev_type='cisco_ios', commands=['Interface                      Status         Protocol Description\nGi0/0                          admin down     down     to WAN\nGi0/1                          up             up       to Jump host\nGi0/2                          down           down     \nGi0/3                          down           down     ', 'Interface                  IP-Address      OK? Method Status                Protocol\nGigabitEthernet0/0         192.168.122.4   YES NVRAM  administratively down down    \nGigabitEthernet0/1         172.17.3.1      YES NVRAM  up                    up      \nGigabitEthernet0/2         unassigned      YES NVRAM  down                  down    \nGigabitEthernet0/3         unassigned      YES NVRAM  down                  down    ']),
    Result(name='R1', ip='192.168.122.2', dev_type='cisco_ios', commands=['Interface                      Status         Protocol Description\nGi0/0                          up             up       to WAN\nGi0/1                          down           down     \nGi0/2                          down           down     \nGi0/3                          down           down     ', 'Interface                  IP-Address      OK? Method Status                Protocol\nGigabitEthernet0/0         192.168.122.2   YES NVRAM  up                    up      \nGigabitEthernet0/1         unassigned      YES NVRAM  down                  down    \nGigabitEthernet0/2         unassigned      YES NVRAM  down                  down    \nGigabitEthernet0/3         unassigned      YES NVRAM  down                  down    ']),
    Error(name='not_exist', ip='1.1.1.1', dev_type='not determined', error='connection failed'),
    Result(name='R4', ip='172.17.4.1', dev_type='cisco_ios', commands=['Interface                      Status         Protocol Description\nGi0/0                          down           down     to WAN\nGi0/1                          up             up       to Jump host\nGi0/2                          down           down     \nGi0/3                          down           down     ', 'Interface                  IP-Address      OK? Method Status                Protocol\nGigabitEthernet0/0         192.168.122.5   YES NVRAM  down                  down    \nGigabitEthernet0/1         172.17.4.1      YES NVRAM  up                    up      \nGigabitEthernet0/2         unassigned      YES NVRAM  down                  down    \nGigabitEthernet0/3         unassigned      YES NVRAM  down                  down    '])]


As you can see, the result is written to the named tuple Result, and the errors to Error.
