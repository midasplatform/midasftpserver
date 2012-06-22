"""
Authentication module for communicating with a Midas server
"""
from zope.interface import implements
from twisted.internet.protocol import Protocol
from twisted.conch.interfaces import IConchUser
from twisted.conch.avatar import ConchUser
from twisted.conch.ssh.session import SSHSession, SSHSessionProcessProtocol, wrapProtocol
from twisted.conch.ssh.factory import SSHFactory
from twisted.conch.ssh.userauth import SSHUserAuthServer
from twisted.cred.checkers import ICredentialsChecker
from twisted.cred.credentials import IUsernamePassword
from twisted.python import log

from sftpServer import MyFileTransferServer

from twisted.cred import portal, checkers, credentials, error
from twisted.internet import defer
import pydas

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


class MidasAvatar(ConchUser):
    def __init__(self, avatarId):
        self.username, self.password = avatarId
        ConchUser.__init__(self)


class MidasRealm:
    implements(portal.IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        user = MidasAvatar(avatarId)
        user.channelLookup['session'] = SimpleSession
        user.subsystemLookup.update(
                {'sftp': MyFileTransferServer})
        return IConchUser, user, nothing

class MidasChecker(object):
    implements(ICredentialsChecker)
    credentialInterfaces = (IUsernamePassword,)
    
    def __init__(self, url):
        self.url = url

    def requestAvatarId(self, credentials):
        try:
            token = pydas.login(credentials.username, credentials.password, None, self.url)
        except:
            return defer.fail(error.LoginFailed("Wrong password"))
        if token is not None:
            return defer.succeed((credentials.username, credentials.password))
