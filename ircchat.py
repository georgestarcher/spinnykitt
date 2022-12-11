import re
import datetime as dt
from datetime import timedelta

class chat_frame:

    __author__ = "Numerical Analysis Intelligence (NumbersAI) Group"

    """
        IRC Chat Processing Class
        Keyword Arguments:
            frame_size -- the number of chat lines to buffer in the frame object. Defaults to 5
        Example Init:
            from ircchat import chat_frame
            frame = chat_frame()
     """

    import statistics
    import pickle
    
    def __init__(self,frame_size=5):
        self.frame_contents = list()
        self.frame_size = frame_size
        self.model = self.pickle.load(open('spinnyKitty.pkl', 'rb'))

    @property
    def is_ready(self):

        """
        property to return if the frame buffer is full and the feature values are ready for use
        """

        if len(self.frame_contents) == self.frame_size:
            return(True)
        else:
            return(False)
    
    @property   
    def mean_tokens(self):

        """
        property to return the mean count of all text tokens in the frame across the buffered chat messages
        Notes:
            a token is a text string delimited by spaces        
        """

        if self.is_ready:
            token_counts = [ message.get('token_count') for message in self.frame_contents ]
            return(self.statistics.mean(token_counts))
        else:
            return(0)
    
    @property
    def mean_spinny(self):

        """
        property to return the mean count of the spinny kitty tokens in the frame across the buffered chat messages
        Notes:
            a token is a text string delimited by spaces                       
        """

        if self.is_ready:
             spinny_counts = [ message.get('spinny_count') for message in self.frame_contents ]
             return(self.statistics.mean(spinny_counts))
        else:
             return(0)

    @property
    def distinct_user_count(self):

        """
        property to return the distinct count of users in the frame across the buffered chat messages
        Notes:
            this is to help reduce false positives by a single user spamming chat multiple times                      
            it also only counts where the message has spinny kitty tokens to avoid non spinny messages throwing it off
        """

        if self.is_ready:
            return(len(set([message.get('user') for message in self.frame_contents if message.get('spinny_count') >=1 ])))
        else:
            return(0)
        
    @property
    def time_range(self):

        """
        property to return the time range in seconds in the frame across the buffered chat messages
        Notes:
            this is to help group chat messages in time to help define a spinny kitty event
        """

        if self.is_ready:
            min_time = min([message.get('time') for message in self.frame_contents])
            max_time = max([message.get('time') for message in self.frame_contents])
            return((max_time-min_time).total_seconds())
        else:
            return(0)

    @property
    def frame_features(self):

        """
        property to return the extracted frame features as a single feature group a machine learning model can use
        Notes:
            call this after adding the current chat message so it's features are part of the frame for context
        """

        if self.is_ready:
            return([[ self.time_range, self.distinct_user_count, self.mean_tokens, self.mean_spinny ]])
        else:
            return([[ 0.0, 0, 0, 0 ]])

    def process_line(self,line):

        """
        method to process a fully logged IRC Chat message
        Notes:
            expects the string line to begin with a well formed ISO format timestamp
            any logged lines missing a timestamp need to be repaired prior to submitting to this method 
        """
    
        if line is None or line=="":
            return()

        timestamp_format = '%Y-%m-%dT%H:%M:%S%z'
        regex_time_stamp = '^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}-\d{4})'
    
        message_regex = '^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}-\d{4}).+:(.*)\!.*@.*\.tmi\.twitch\.tv PRIVMSG #(.*) :(.*)'

        try:
            timestamp_str, username, channel, message = re.search(message_regex, line).groups()
        except Exception as e:
            return()

        timestamp = dt.datetime.strptime(timestamp_str,timestamp_format)
        message = re.sub(' +', ' ', message)
        tokens = message.split()
        token_count = len(tokens)
        spinny_count = len([token for token in tokens if token=='hermitSpinnyKitty'])

        return_message = dict()
        return_message['time'] = timestamp
        return_message['user'] = username
        return_message['token_count'] = token_count
        return_message['spinny_count'] = spinny_count
        return_message['message'] = message
    
        return(return_message)
                            
    def is_spinnyKitty(self,message):

        """
        reserved method to assist in classification during machine learning model generation
        Notes:
            expects a processed frame record
        """

        if self.is_ready:
            condition = 0
            if self.time_range <=30:
                condition += 1
            if self.distinct_user_count >=3:
                condition += 1
            if self.mean_tokens >=6:
                condition += 1
            if self.mean_spinny >=4:
                condition += 1
            if message.get('spinny_count') == 0:
                condition -= 1
            if condition == 4:
                return(True)
            else:
                return(False)
        else:
            return(False)
            
            
    def add_message(self,message):

        """
        method to add  a fully logged IRC Chat message to the frame object
        Notes:
            expects the string message to begin with a well formed ISO format timestamp
            any logged lines missing a timestamp need to be repaired prior to submitting to this method
        """

        if  not isinstance(message, dict):
            return(self.is_ready)

        if message.get('user') == 'fossabot':
            return(self.is_ready)
        if message.get('message') in ['ping','pong']:
            return(self.is_ready)
        
        if self.is_ready:
            del self.frame_contents[0]
        
        message.pop('message')
        self.frame_contents.append(message)
        return (self.is_ready)

