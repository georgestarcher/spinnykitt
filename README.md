# spinnykitty
Project Spinny Kitty that identifies events from twitch chat

### IRC Logger: monitor_chat.py

This is the main script to run to monitor chat and log it to logs/chat.log.
You set your twitch nickname (username) and set a twitch oauth token here for the password.

The class file irclog.py is used to watch chat and log it to file by spinning off a quick thread so no messages are missed while logging chat to a file.

### Jupyter Notebook:

This Jupyter Notebook is used to build the Machine Learning model from the chat log. Several full streams of chat is recommended.

#### Machine Learning Model:

We do not want to rely on a single chat message to declare a Spinny Kitty event. The pattern is several viewers will post a message mostly comprising of the custom emoji within a short time window as GenerikB steps away.

We want to be able to apply the model to a chat log stream so we can identify the chat line that tips the measurement into a Spinny Kitty event.

To do this we created a class called `chat_frame` that represents five lines of chat in a buffer. This frame object has properities that give us the desired features for a line of chat plus it's previous lines in the frame.

* `is_ready`: this says if the frame has the full five chat lines in it's buffer.
* `mean_tokens`: the mean number of the count of text tokens across the five lines in the buffer. A token is the space delimited words.
* `mean_spinny`: the mean number of the count of `hermitSpinnyKitty` tokens across the lines in the buffer.
* `distinct_user_count`: the distinct number of users with messages in the frame buffer.
* `time_range`: the number of seconds between the earliest and latest message in the frame buffer.

These features do a good job of identifying a `Spinny Kitty Event`. We do avoid adding the `fossabot` user to the frame so the bot does not throw off chat behavior as the bot will usually spam reply `hermitSpinnyKitty` to someone else's message.

##### The Classification Cheat

So normally when training a model you want to have the data labeled with what you know it should be. Since chat logs can be large especially for 12 hour streams we cheated.  We used the following criteria to classify the logs on the fly since on manual inspection it felt right for recognizing an event we knew happened.

This does mean our model simply very closely fits the if statements below. BUT that is the joke about ML that it is just a small compact if statement processing engine. We do end up with what we want. A simple model file we can load and apply to live chat or run across the stored chat log from a stream.

```
    def is_spinnyKitty(self,message):
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
```

### Finding Spinny Kitty Events: twitchChat.py

This script runs across all the accumulated logs in chat.log and gives only a timestamp of an identified event.
It uses the established machine learning model and pushes the accumulated chat through it as if it were a live data stream.

This could be used on a live chat stream as it comes in. However some extra coding would have to be done to emulate the timestamp the logging to file provides.

### Twitch and OAuth:

You will need an OAuth token to use for the IRC password. You could use one of the public token generator sites. However, you have to keep their application in your allowed connections for your account. Also they may want more permissions for general purpsoes than we need here. To get your own token here are a few simple steps.

1. Go to your Twitch Dev Console: https://dev.twitch.tv/console
1. Click Register your Application
1. Name: HermitChat
1. OAuth Redirect URL: https://localhost
1. Category: `Chat Bot`
1. Click Create after the captcha
1. Copy the `Client ID`
1. Edit and paste the following URL into a web browser tab.
1. Click Accept from Twitch 
1. It will redirect your browser to an empty tab. However copy the URL from the tab bar. This URL has the token.

You will form a URL to paste into a web browser tab. It contains just the `chat:read` permission scope. 
* Reference: https://dev.twitch.tv/docs/authentication/scopes

```
https://id.twitch.tv/oauth2/authorize?response_type=token&client_id=CLIENTIDHERE&redirect_uri=http://localhost&scope=chat%3Aread&state=c3ab8aa609ea11e793ae92361f002671
```

This is an example of the URL that your browser gets redirected to. Which is an empty page since you don't have a listening web server.
```
http://localhost/#access_token=ptubexg32qfwnqzvdaktvmke7khb61&scope=chat%3Aread&state=c3ab8aa609ea11e793ae92361f002671&token_type=bearer
```

Note the `access_token=` section. That is the value you will paste into our script for the password in the form:
`oauth:ptubexg32qfwnqzvdaktvmke7khb61`

### Optional Notes:

After all this I did find an interesting third party library that supports chat and the Twitch API. 
* https://github.com/Teekeks/pyTwitchAPI


