#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from unittest import TestCase, main
from multi_connector import net


class MultiNetConnectTest(TestCase):
    def test_correct_init(self):
        self.assertEqual(net.MultiNetConnect("test", "test", [net.Host(
            name="R1", ip="1.1.1.1")]).hosts, [net.Host(name="R1", ip="1.1.1.1")])

    def test_fail_init_hosts(self):
        bad_hosts = ["wrong type", [], {"name": "R1"}]
        for host in bad_hosts:
            with self.assertRaises(ValueError) as e:
                net.MultiNetConnect("test", "test", host, ["test command"])
            self.assertEqual(f"parameter {host} is invalid. Must be list[Host] or tuple[Host]", e.exception.args[0])

    def test_fail_init_commands(self):
        bad_commands = ["wrong commands", [], {"R1": "command"}]
        connector = net.MultiNetConnect("test", "test", [net.Host(name="R1", ip="1.1.1.1")])
        for command in bad_commands:
            with self.assertRaises(ValueError) as e:
                connector.commands = command
            self.assertEqual(
                f"parameter {command} is invalid. Must be list or tuple with commands", e.exception.args[0])

    def test_fail_init_cli_mode(self):
        bad_cli_mode = "qwerty"
        with self.assertRaises(ValueError) as e:
            net.MultiNetConnect(login="test", password="test", hosts=[net.Host(
                name="R1", ip="1.1.1.1")], cli_mode=bad_cli_mode)
        self.assertEqual(
            f"parameter {bad_cli_mode} is invalid. Must be 'enable' or 'config'", e.exception.args[0])

    def test_fail_init_any_type(self):
        connector = net.MultiNetConnect("test", "test", [net.Host(name="R1", ip="1.1.1.1")])
        with self.assertRaises(ValueError) as e:
            connector.login = 123
        self.assertEqual("parameter 123 have invalid type.", e.exception.args[0])

        with self.assertRaises(ValueError) as e:
            connector.port = "qwerty"
        self.assertEqual("parameter qwerty have invalid type.", e.exception.args[0])

        with self.assertRaises(ValueError) as e:
            connector.read_timeout = {'a': 2.0}
        self.assertEqual("parameter {'a': 2.0} have invalid type.", e.exception.args[0])

    def test_hosts_validator(self):
        hosts = [net.Host(name="R1", ip="1.1.1.1"),
                 net.Host(name="R1", ip="1.1.1.1"),
                 net.Host(name="R2", ip="1.1.1.1")]
        result = [net.Host(name='R1', ip='1.1.1.1')]
        connector = net.MultiNetConnect("test", "test", hosts)
        self.assertEqual(connector.hosts, result)
        connector.hosts = hosts
        self.assertEqual(connector.hosts, result)

    def test_connection(self):
        hosts = [net.Host(name="R1", ip="1.1.1.1")]
        result = [net.Error(name="R1", ip="1.1.1.1", dev_type="not determined", error="connection failed")]
        self.assertEqual(net.MultiNetConnect("test", "test", hosts).multy_connect(
            ["command"], process=2, threads_per_process=2), result)


if __name__ == '__main__':
    main()
