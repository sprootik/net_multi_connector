#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netmiko import ConnectHandler, NetmikoAuthenticationException, NetmikoTimeoutException, BaseConnection, SSHDetect
from netmiko.exceptions import ReadTimeout
from typing import Union, Generator, NamedTuple
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Pool, cpu_count

# Debug
# import logging.handlers
# logging.basicConfig(format=f"%(asctime)s - [%(levelname)s] - %(name)s - %(message)s", level=logging.DEBUG)


class Host(NamedTuple):
    name: str
    ip: str
    dev_type: str = 'autodetect'


class Result(NamedTuple):
    name: str
    ip: str
    dev_type: str
    commands: list


class Error(NamedTuple):
    name: str
    ip: str
    dev_type: str
    error: str


class _Validator:
    def __init__(self, mode):
        """Data descriptor for class MultiNetConnect

        Args:
            mode (_type_): Validator mode. Must be: "hosts" | "commands" |
            "cli_mode" | "str" | "int" | "float"
        """
        self.__mode = mode

    @classmethod
    def __commands_validator(cls, obj: Union[tuple[Host], list[str]]) -> Union[tuple[Host], list[str]]:
        if isinstance(obj, list | tuple) and len(obj) and all(isinstance(x, str) for x in obj) > 0:
            return obj
        else:
            raise ValueError(f"parameter {obj} is invalid. Must be list or tuple with commands")

    @classmethod
    def __hosts_validator(cls, obj: Union[list[Host], tuple[Host]]) -> list[Host]:
        """check the correctness of the values and add only unique hosts"""
        if not isinstance(obj, list | tuple) or len(obj) == 0:
            raise ValueError(f"parameter {obj} is invalid. Must be list[Host] or tuple[Host]")

        unic_ips = set()
        hosts = set()
        for data in obj:
            match data:
                case Host(ip=ip_address):
                    if ip_address not in unic_ips:
                        unic_ips.add(ip_address)
                        hosts.add(data)
                case _:
                    raise ValueError(f"parameter {data} is invalid. Must be Host")
        return list(hosts)

    @classmethod
    def __cli_mode_validator(cls, obj: str) -> str:
        match obj:
            case str('enable') | str('config'):
                return obj
            case _:
                raise ValueError(f"parameter {obj} is invalid. Must be 'enable' or 'config'")

    @classmethod
    def __parameters_validator(cls, obj: str | int | float, mode: str) -> str | int | float:
        match (obj, mode):
            case (str(), "str") | (int(), "int") | (float(), "float"):
                return obj
            case _:
                raise ValueError(f"parameter {obj} have invalid type.")

    def __set_name__(self, _, name):
        self.name = "_" + name

    def __get__(self, instance, _):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        match self.__mode:
            case "hosts":
                instance.__dict__[self.name] = self.__hosts_validator(value)
            case "commands":
                instance.__dict__[self.name] = self.__commands_validator(value)
            case "cli_mode":
                instance.__dict__[self.name] = self.__cli_mode_validator(value)
            case str("str" | "int" | "float") as mode:
                instance.__dict__[self.name] = self.__parameters_validator(value, mode)


class MultiNetConnect:
    number_of_processors = cpu_count()
    # Data descriptor
    login = _Validator("str")
    password = _Validator("str")
    hosts = _Validator("hosts")
    commands = _Validator("commands")
    port = _Validator("int")
    auth_timeout = _Validator("int")
    timeout = _Validator("int")
    enable_password = _Validator("str")
    cli_mode = _Validator("cli_mode")
    read_timeout = _Validator("float")
    banner_timeout = _Validator("int")

    def __init__(self, login: str, password: str, hosts: list[Host], enable_password: str = "",
                 cli_mode: str = 'enable', port: int = 22, auth_timeout: int = 30, timeout: int = 120,
                 read_timeout: float = 60.0, banner_timeout: int = 60):
        self.login = login
        self.password = password
        self.hosts = hosts
        # self.commands = commands
        self.port = port
        self.auth_timeout = auth_timeout
        self.timeout = timeout
        self.enable_password = enable_password
        self.cli_mode = cli_mode
        self.read_timeout = read_timeout
        self.banner_timeout = banner_timeout
        self._update_dev_type = False

    @staticmethod
    def separation_of_values(lst, n: int) -> Generator:
        """
        Args:
            lst: list or tuple with values
            n: separation step
        Returns:
            split list or tuple
        """
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    def _single_connect(self, host: Host) -> Result | Error | Host:
        host_name = host.name
        ip = host.ip
        device_type = host.dev_type

        net_parameters = {
            'device_type': device_type,
            'ip': ip,
            'username': self.login,
            'password': self.password,
            'port': self.port,
            'auth_timeout': self.auth_timeout,
            'timeout': self.timeout,
            'banner_timeout': self.banner_timeout,
            'secret': self.enable_password
        }

        # detect device_type
        if device_type == 'autodetect':
            try:
                guesser = SSHDetect(**net_parameters)
            except (NetmikoTimeoutException, ReadTimeout):
                return Error(name=host_name, ip=ip, dev_type="not determined", error="connection failed")
            except NetmikoAuthenticationException:
                return Error(name=host_name, ip=ip, dev_type="not determined", error="authentication failed")
            else:
                # detect dev_type
                device_type = guesser.autodetect()
                if device_type is None:
                    return Error(name=host_name, ip=ip, dev_type="not determined",
                                 error="failed to determine device type")
                net_parameters['device_type'] = device_type
                if self._update_dev_type is True:
                    return Host(name=host_name, ip=ip, dev_type=device_type)
        elif self._update_dev_type is True:
            return Error(name=host_name, ip=ip, dev_type=device_type, error="host has device type")

        # connect
        try:
            with ConnectHandler(**net_parameters) as connection:
                if not connection.check_enable_mode():
                    connection.enable()
                match self.cli_mode:
                    case "enable":
                        output = self._send_enable_commands(connection)
                    case "config":
                        output = self._change_config_commands(connection)
                return Result(name=host_name, ip=ip, dev_type=device_type, commands=output)
        except NetmikoTimeoutException:
            return Error(name=host_name, ip=ip, dev_type=device_type, error="connection failed")
        except NetmikoAuthenticationException:
            return Error(name=host_name, ip=ip, dev_type=device_type, error="authentication failed")
        except Exception as e:
            return Error(name=host_name, ip=ip, dev_type=device_type, error=f"{e}")

    def _send_enable_commands(self, connection: BaseConnection) -> list[str]:
        """from enable mode"""
        output = []
        for cmd in self.commands:
            out = connection.send_command(cmd, read_timeout=self.read_timeout)
            output.append(out)
        return output

    def _change_config_commands(self, connection: BaseConnection) -> list[str]:
        """from configure terminal mode"""
        output = connection.send_config_set(self.commands, read_timeout=self.read_timeout)
        return output

    def _thread_multy_connect(self, part_of_hosts: list[Host]) -> list[Result | Error | Host]:
        """connecting via single connect to n threads"""
        summary_result: list = []
        thread_pools = len(part_of_hosts) + 4

        with ThreadPool(thread_pools) as pool:
            result = pool.map(self._single_connect, part_of_hosts)
            summary_result.extend(result)
        # pool.close()
        # pool.terminate()
        return summary_result

    def multy_connect(
            self, commands: list[str], process: int = number_of_processors, threads_per_process: int = 100,
            update_dev_type: bool = False) -> list[Result | Error | Host]:
        """Connection using processes and threads. Each process handles multiple threads.

        Args:
            process (int, optional): How many processes to create on connection. Defaults to number_of_processors.
            threads_per_process (int, optional): Number of concurrent connections handled by each process.
            Each thread handles one host. Defaults to 100.
            update_dev_type: If True, will return list of hosts with update device_type and will update self.hosts.
            Doesn't try to connect and execute commands. If False, will detect device_type (if not set) and try
            to connect and execute commands.
        """

        self._update_dev_type = update_dev_type
        self.commands = commands

        summary_result = []
        host_list = self.separation_of_values(self.hosts, threads_per_process)

        with Pool(process) as pool:
            result = pool.map(self._thread_multy_connect, host_list)
            for part in result:
                summary_result.extend(part)

        if self._update_dev_type is True:
            for host in summary_result:
                if isinstance(host, Host):
                    self.hosts.remove(Host(name=host.name, ip=host.ip))
                    self.hosts.append(host)

        return summary_result
