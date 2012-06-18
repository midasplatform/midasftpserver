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

from sftpServer import MyFileTransferServer

class EchoProtocol(Protocol):


    def connectionMade(self):
        self.transport.write("Echo protocol connected\r\n")


    def dataReceived(self, bytes):
        self.transport.write("echo: " + repr(bytes) + "\r\n")


    def connectionLost(self, reason):
        print 'Connection lost', reason


    def eofReceived(self):
        print 'eofReceived'


    def closed(self):
        print 'closed'


    def closedReceived(self):
        print 'closeReceived'



class SCPProtocol(Protocol):

    def connectionMade(self):
        print 'connection made'
        self.transport.write('some data')
        self.transport.loseConnection()
    
    
    def dataReceived(self, bytes):
        print 'dataReceived: %r' % bytes
    
    
    def connectionLost(self, reason):
        print 'connectionLost', reason



def nothing():
    pass



class SimpleSession(SSHSession):
    name = 'session'


    def request_pty_req(self, data):
        return True


    def request_shell(self, data):
        protocol = EchoProtocol()
        transport = SSHSessionProcessProtocol(self)
        protocol.makeConnection(transport)
        transport.makeConnection(wrapProtocol(protocol))
        self.client = transport
        return True


    def request_exec(self, data):
        print 'request_exec', data
        protocol = SCPProtocol()
        transport = SSHSessionProcessProtocol(self)
        protocol.makeConnection(transport)
        transport.makeConnection(wrapProtocol(protocol))
        self.client = transport
        return True

class MidasRealm(object):

    def requestAvatar(self, avatarId, mind, *interfaces):
        user = ConchUser()
        user.channelLookup['session'] = SimpleSession
        user.subsystemLookup.update(
                {'sftp': MyFileTransferServer})
        return IConchUser, user, nothing

class DummyChecker(object):
    credentialInterfaces = (IUsernamePassword,)
    implements(ICredentialsChecker)

    def requestAvatarId(self, credentials):
        return credentials.username