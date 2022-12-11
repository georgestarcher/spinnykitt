
# Imports
import re, socket
from _thread import *
import threading
from emoji import demojize

class irclogger:

    __author__ = "Numerical Analysis Intelligence (NumbersAI) Group"

     """
        IRC Chat Logger  Class
        Keyword Arguments:
            token -- a Twitch oauth login token - required
            nickname  -- Twitch chat nickname - required
            channel -- Twitch stream channel chat to log - required
            server -- IRC server. Defaults to Twitch IRC
            port -- IRC Port. Defaults to 6667
        Example Usage:
            from irclog import irclogger

            nickname = 'TWITCHUSERNAME'
            token = 'TWITCHOAUTHTOKEN'
            channel = '#generikb'

            irc = irclogger(token,channel,nickname)
            irc.connect()
            irc.monitor()
     """

    import logging

    def __init__(self, token=None, channel=None, nickname='chatter', server='irc.chat.twitch.tv', port=6667):

        if token is None:
            raise(ValueError("Missing Oauth Token."))

        if channel is None:
            raise(ValueError("Missing Channel Value. Use format #generikb"))

        self.token = token
        self.channel = channel
        self.server = server
        self.port = port
        self.nickname = nickname

        # Setup the network socket
        self.sock = socket.socket()

        # Setup Logger to the chat.log file
        chat_log_file = './logs/chat.log'

        self.logging.basicConfig(level=self.logging.DEBUG,
                    format='%(asctime)s — %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S%z',
                    handlers=[self.logging.FileHandler(chat_log_file, encoding='utf-8')])

    def connect(self):

        """
        method to connect to IRC chat
        Notes:
            uses the twitch nickname and expected valid oauth token as password
            joins the specified irc channel for the stream 
        """

        self.sock.connect((self.server, self.port))
        self.sock.send(f"PASS {self.token}\n".encode('utf-8'))
        self.sock.send(f"NICK {self.nickname}\n".encode('utf-8'))
        self.sock.send(f"JOIN {self.channel}\n".encode('utf-8'))

    def messageParse(self,username_message):

        """
        method to parse the message into components for easy logging.
        """


        if 'PRIVMSG' not in username_message:
            return()

        username = ""
        channel = ""
        message = ""

        try:    
            username, channel, message = re.search(':(.*)\!.*@.*\.tmi\.twitch\.tv PRIVMSG #(.*) :(.*)', username_message).groups()
        except Exception as e:
            return(None, None, None)

        return(username, channel, message)

    def handle_message(self,resp):

        """
        method to process a message off the socket and log it to file.
        Notes:
            this method is launched as a thread so it can complete independantly of receiving new messages off the socket 
            if the message is a PING for a keep alive it sends the PONG back to the IRC server over the socket
        """

        if resp.startswith('PING'):
            self.sock.send("PONG :tmi.twitch.tv\n".encode('utf-8'))

        elif len(resp) > 1:
            resp_text = demojize(resp).replace("\n","")
            if 'PRIVMSG' in resp_text:
                self.logging.info(resp_text)
                username, channel, message = self.messageParse(resp_text)
                if message is not None:
                    print(f"Channel: {channel} \nUsername: {username} \nMessage: {message}")

    def monitor(self):

        """
        method to monitor the chat stream until the program is forably ended 
        Notes:
            receives messages and launches a processing thread so reading the chat stream is not blocked by processing and logging 
        """

        while True:
            resp = self.sock.recv(2048).decode('utf-8')

            if len(resp) >1:
                thread_handle_message =  threading.Thread(target=self.handle_message, args=(resp,))
                thread_handle_message.start()
      

