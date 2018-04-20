# -*- coding:utf-8 -*-

import paramiko
import re, StringIO, time, datetime
from sys import stdin, stdout, stderr
import multiprocessing

if __name__ == '__main__':
    # host = '10.171.165.7'
    # port = 1046
    # username = 'hzchensheng15'
    # key_file = 'C:\\Users\\CS\\Documents\\Identity'
    host = '59.111.103.119'
    port = 22
    username = 'root'
    key_file = 'C:\\Users\\CS\\.ssh\\id_rsa'
    ssh_key = paramiko.RSAKey.from_private_key_file(key_file)

    # 实例化SSHClient
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    # 自动添加策略，保存服务器的主机名和密钥信息
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 连接SSH服务端，以秘钥方式
    ssh_client.connect(host, port, username, pkey=ssh_key)

    stdin, stdout, stderr = ssh_client.exec_command('cd /home/blog;ls')
    print stdout.readlines()
    print stderr.readlines()
    ssh_client.close()


