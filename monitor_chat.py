
from irclog import irclogger

# credentials and channel
nickname = 'TWITCHUSERNAME'
token = 'TWITCHOAUTHTOKEN'
channel = '#streammernamehere'

irc = irclogger(token,channel,nickname)
irc.connect()
irc.monitor()

