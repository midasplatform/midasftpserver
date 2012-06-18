# ckeygen -t rsa -f id_rsa
# 
# ssh-passwords
# bob:password
# foo:foo

from twisted.application import service, internet
from zope.interface import implements
from twisted.python import components
from twisted.internet.protocol import Protocol
from twisted.python import log, failure
from twisted.cred.portal import Portal
from twisted.cred.checkers import FilePasswordDB
from twisted.conch.ssh.factory import SSHFactory
from twisted.internet import reactor
from twisted.conch.ssh.keys import Key
from twisted.conch.interfaces import IConchUser
from twisted.conch.avatar import ConchUser
from twisted.conch.unix import UnixConchUser
from twisted.conch.ssh import filetransfer
from twisted.conch.ssh.session import SSHSession, SSHSessionProcessProtocol, wrapProtocol
from twisted.cred.checkers import ICredentialsChecker
from twisted.cred.credentials import IUsernamePassword

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
