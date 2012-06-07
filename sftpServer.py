from zope.interface import implements
from twisted.enterprise import adbapi

from twisted.application import service, internet
from twisted.internet import reactor
from twisted.conch import error, recvline, interfaces as conchinterfaces
from twisted.conch.avatar import ConchUser
from twisted.conch.ssh.keys import Key
from twisted.conch.ssh.factory import SSHFactory
from twisted.conch.ssh import userauth, connection, session, forwarding, filetransfer
from twisted.conch.unix import UnixSSHRealm, SFTPServerForUnixConchUser, UnixConchUser
from twisted.cred.checkers import ICredentialsChecker
from twisted.cred.credentials import IUsernamePassword
from twisted.cred import portal, checkers, credentials
from twisted.cred.portal import Portal
from twisted.conch.insults import insults
from twisted.python import components, log
import struct, os, time, socket
import fcntl, tty
import pwd, grp
import pty

import sys 
sys.path.insert(0, ".")

from authentication import MidasRealm
from authentication import MidasPasswordChecker
from authentication import DummyChecker

def get_key(path):
    return Key.fromString(data=open(path).read())

DB_DRIVER = "MySQLdb"
DB_ARGS = {
    "db":"midas",
    "user": "midas",
    "password":"midas"}


def makeService():
    public_key = get_key('id_rsa.pub')
    private_key = get_key('id_rsa')

    factory = SSHFactory()
    factory.privateKeys = {'ssh-rsa': private_key}
    factory.publicKeys = {'ssh-rsa': public_key}
    connection = adbapi.ConnectionPool(DB_DRIVER, **DB_ARGS)
    factory.portal = Portal(MidasRealm())
    factory.portal.registerChecker(MidasPasswordChecker(connection))

    return internet.TCPServer(6666, factory)


application = service.Application("sftp server")
sftp_server = makeService()
sftp_server.setServiceParent(application)
