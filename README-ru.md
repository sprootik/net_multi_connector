![](https://img.shields.io/badge/python-3.10-green)
# net_multi_connector  

Модуль для многопоточного подключения к сетевому железу. Основан на библиотеке netmiko.

Данный модуль позволяет подключаться в n процессов по m потоков в каждом. Регулируя количество процессов и потоков, мы можем увеличить нагрузку на процессоры и уменьшить время работы, либо же уменьшить нагрузку на процессоры, но увеличить время работы. 

### примеры использования
Различные примеры использования находятся в [examples.py](./examples.py) 

Создаем список хостов и выполняемых команд


    from multi_connector import net

    hosts = [net.Host(name='R1', ip='192.168.122.2'),
            net.Host(name='R2', ip='192.168.122.3'),
            net.Host(name='R3', ip='172.17.3.1'),
            net.Host(name='R4', ip='172.17.4.1', dev_type='cisco_ios'),
            net.Host(name='not_exist', ip='1.1.1.1')
            ]

    commands = ["show interfaces description", "show ip interface brief"]

Каждый хост должен быть записан в именованный кортеж Host. Если dev_type не указан, происходит автоматическое детектирование. Так же есть возможность произвести только детектирование без выполнения команд (см. [examples.py](./examples.py) ).

Создаем экземпляр класса коннектора

    connector = net.MultiNetConnect(login='test', password='test', hosts=hosts,
                                    enable_password='test')

При передаче списка хостов в инициализаторе, срабатывает datadescriptor, который удаляет дубли на основании ip адреса, либо имени и ip адреса.  Так же  проверяется валидность переданных параметров.

Подключаемся к оборудованию и выполняем команды из привилегированного режима. Так же есть возможность выполнять команды из режима конфигурации (см. [examples.py](./examples.py) ).

    result = connector.multy_connect(commands=commands, process=1,
                                    threads_per_process=5)

В данном случае мы используем один процесс и 5 потоков в нем. Соответственно, время выполнения задания будет равно времени выполнения его на одном (самом медленном) хосте. Если process*threads_per_process будет меньше числа хостов, обработка происходит итерационно (частями). 

Результат выполнения:

    [Result(name='R2', ip='192.168.122.3', dev_type='cisco_ios', commands=['Interface                      Status         Protocol Description\nGi0/0                          up             up       to WAN\nGi0/1                          down           down     \nGi0/2                          down           down     \nGi0/3                          down           down     ', 'Interface                  IP-Address      OK? Method Status                Protocol\nGigabitEthernet0/0         192.168.122.3   YES NVRAM  up                    up      \nGigabitEthernet0/1         unassigned      YES NVRAM  down                  down    \nGigabitEthernet0/2         unassigned      YES NVRAM  down                  down    \nGigabitEthernet0/3         unassigned      YES NVRAM  down                  down    ']),
    Result(name='R3', ip='172.17.3.1', dev_type='cisco_ios', commands=['Interface                      Status         Protocol Description\nGi0/0                          admin down     down     to WAN\nGi0/1                          up             up       to Jump host\nGi0/2                          down           down     \nGi0/3                          down           down     ', 'Interface                  IP-Address      OK? Method Status                Protocol\nGigabitEthernet0/0         192.168.122.4   YES NVRAM  administratively down down    \nGigabitEthernet0/1         172.17.3.1      YES NVRAM  up                    up      \nGigabitEthernet0/2         unassigned      YES NVRAM  down                  down    \nGigabitEthernet0/3         unassigned      YES NVRAM  down                  down    ']),
    Result(name='R1', ip='192.168.122.2', dev_type='cisco_ios', commands=['Interface                      Status         Protocol Description\nGi0/0                          up             up       to WAN\nGi0/1                          down           down     \nGi0/2                          down           down     \nGi0/3                          down           down     ', 'Interface                  IP-Address      OK? Method Status                Protocol\nGigabitEthernet0/0         192.168.122.2   YES NVRAM  up                    up      \nGigabitEthernet0/1         unassigned      YES NVRAM  down                  down    \nGigabitEthernet0/2         unassigned      YES NVRAM  down                  down    \nGigabitEthernet0/3         unassigned      YES NVRAM  down                  down    ']),
    Error(name='not_exist', ip='1.1.1.1', dev_type='not determined', error='connection failed'),
    Result(name='R4', ip='172.17.4.1', dev_type='cisco_ios', commands=['Interface                      Status         Protocol Description\nGi0/0                          down           down     to WAN\nGi0/1                          up             up       to Jump host\nGi0/2                          down           down     \nGi0/3                          down           down     ', 'Interface                  IP-Address      OK? Method Status                Protocol\nGigabitEthernet0/0         192.168.122.5   YES NVRAM  down                  down    \nGigabitEthernet0/1         172.17.4.1      YES NVRAM  up                    up      \nGigabitEthernet0/2         unassigned      YES NVRAM  down                  down    \nGigabitEthernet0/3         unassigned      YES NVRAM  down                  down    '])]


Как можно видеть, результат записывается в именованный кортеж Result, а ошибки в Error. 
