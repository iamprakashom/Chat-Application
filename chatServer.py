from __future__ import print_function
import socket
from asyncore import dispatcher
from asynchat import async_chat
import asyncore
# import logging
# import pdb
# logging.basicConfig(level=logging.DEBUG)

PORT = 8500
NAME = 'Chat Server'


class EndSession(Exception):
    pass


class CommandHandler:
    """
    Simple command handler to accept command from the stdin
    """
    def unknown(self, session, cmd):
        session.push('Unknown command : %s\n' % cmd)

    def handle(self, session, line):
        if not line.strip():
            return
        parts = line.split(' ', 1)
        cmd = parts[0].strip()
        try:
            line = parts[1].strip()
        except IndexError:
            line = ''
        meth = getattr(self, 'do_'+cmd, None)
        try:
            meth(session, line)
        except TypeError:
            self.unknown(session, cmd)


class Room(CommandHandler):
    """
    A Chat Room which may contain one or more users
    (sessions). It takes care of basic command handling.
    """

    def __init__(self, server):
        self.server = server
        self.sessions = []

    def add(self, session):
        self.sessions.append(session)

    def remove(self, session):
        self.sessions.remove(session)

    def broadcast(self, line):
        for session in self.sessions:
            session.push(line)

    def do_stop(self, session, line):
        raise EndSession


class LoginRoom(Room):
    """
    A Room meant for single person who has just connected.
    """

    def add(self, session):
        Room.add(self, session)
        # when user joins, greets him/her.
        self.broadcast('Welcome to {}\n' .format(self.server.name))
        session.push('To log in use "login <nick> "\n')

    def unknown(self, session, cmd):
        session.push('Invalid login command, use "login <nick>"\n')

    def do_login(self, session, line):
        name = line.strip()
        if not name:
            session.push('Please enter a name \n')
        elif name in self.server.users:
            session.push('The name {} is taken. \n' .format(name))
            session.push('Please try again. \n')
        else:
            session.name = name
            session.enter(self.server.main_room)


class ChatRoom(Room):
    """
    A room meant for multiple users who can chat with the others in the room.
    """

    def add(self, session):
        self.broadcast(session.name + ' has entered the room \n')
        self.server.users[session.name] = session
        Room.add(self, session)
        print("Successful login by user : {}" .format(session.name))

    def remove(self, session):
        Room.remove(self, session)
        self.broadcast(session.name + ' has left the room \n')

    def do_say(self, session, line):
        self.broadcast(session.name + ':' + line + '\n')


class LogoutRoom(Room):
    """
    To remove user's name from the server.
    """

    def add(self, session):
        try:
            del self.server.users[session.name]
        except KeyError:
            pass


class ChatSession(async_chat):
    """
    single session to handle communication of single user.
    """

    def __init__(self, server, sock):
        async_chat.__init__(self, sock)
        self.server = server
        self.set_terminator("\n")  # setting line terminator to \n
        self.data = []
        self.name = None
        self.enter(LoginRoom(server))

    def enter(self, room):
        try:
            cur = self.room
        except AttributeError:
            pass
        else:
            cur.remove(self)
        self.room = room
        room.add(self)

    def collect_incoming_data(self, data):
        """
        collecting incoming message
        """
        self.data.append(data)

    def found_terminator(self):
        """
        Broadcast message to user if line terminator is found in line.

        """
        line = ''.join(self.data)
        self.data = []  # clears the buffer
        try:
            self.room.handle(self, line)
        except EndSession:
            self.handle_close()

    def handle_close(self):
        async_chat.handle_close(self)
        self.enter(LogoutRoom(self.server))


class ChatServer(dispatcher):
    def __init__(self, port, name):
        dispatcher.__init__(self)

        # create socket for connection
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()  # reuse the same address again, if server crashed
        self.bind(('', port))
        self.listen(5)  # listen for 5 incoming connection
        self.name = name
        self.users = {}
        self.main_room = ChatRoom(self)

    def handle_accept(self):
        """
        This creates a new ChatSession object and appends it to list of
        sessions.
        """
        conn, addr = self.accept()
        ChatSession(self, conn)


if __name__ == '__main__':
    print("To exit press Ctrl + C")
    s = ChatServer(PORT, NAME)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass
