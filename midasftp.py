
from twisted.application import service, internet
"""
Midas SFTP Service
"""
from twisted.python import components
from twisted.cred.portal import Portal
from twisted.conch.ssh.factory import SSHFactory
from twisted.conch.ssh.keys import Key
from twisted.conch.avatar import ConchUser
from twisted.conch.ssh import filetransfer

from sftpServer import MySFTPAdapter
from authentication import MidasRealm, DummyChecker


components.registerAdapter(MySFTPAdapter, ConchUser, filetransfer.ISFTPServer)

def get_key(path):
    return Key.fromString(data=open(path).read())

def makeService():
    public_key = get_key('id_rsa.pub')
    private_key = get_key('id_rsa')

    factory = SSHFactory()
    factory.privateKeys = {'ssh-rsa': private_key}
    factory.publicKeys = {'ssh-rsa': public_key}
    factory.portal = Portal(MidasRealm())
    factory.portal.registerChecker(DummyChecker())

    return internet.TCPServer(8022, factory)


application = service.Application("midas sftp server")
sftp_server = makeService()
sftp_server.setServiceParent(application)
