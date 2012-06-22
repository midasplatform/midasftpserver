
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
from twisted.python import log
from twisted.internet import reactor

from sftpServer import MySFTPAdapter
from authentication import MidasRealm, MidasChecker
import sys


components.registerAdapter(MySFTPAdapter, ConchUser, filetransfer.ISFTPServer)

def get_key(path):
    return Key.fromString(data=open(path).read())

def makeFactory():
    public_key = get_key('id_rsa.pub')
    private_key = get_key('id_rsa')

    factory = SSHFactory()
    log.msg("make Factory")
    factory.privateKeys = {'ssh-rsa': private_key}
    factory.publicKeys = {'ssh-rsa': public_key}
    factory.portal = Portal(MidasRealm())
    factory.portal.registerChecker(MidasChecker("http://localhost/midas"))

    return factory

if __name__ == '__main__':
    log.startLogging(sys.stdout)
    factory = makeFactory()
    reactor.listenTCP(8022, factory) #@UndefinedVariable
    reactor.run() #@UndefinedVariable
    
else:    
    application = service.Application("midas sftp server")
    factory = makeFactory()
    sftp_server = internet.TCPServer(8022, factory) #@UndefinedVariable
    sftp_server.setServiceParent(application)
