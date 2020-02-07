import time
import os
import curses
import praw
from random import randint, choice
from slack import RTMClient


class Botovkov:

    def __init__(self):
        """

        """
        print("Starting Botovkov ...")
        self.reddit = praw.Reddit(client_id=os.environ["REDDIT_ID"],
                                  client_secret=os.environ["REDDIT_SECRET"],
                                  password=os.environ["REDDIT_PASSWORD"],
                                  user_agent="Maxim",
                                  username=os.environ["REDDIT_USERNAME"])
        self.slack_token = os.environ["SLACK_API_TOKEN"]
        self.rtm_client = RTMClient(token=self.slack_token)
        self.rtm_client.run_on(event='message')(self.process_incoming_msg)
        self.joke_count = 0
        self.fun_fact_count = 0
        self.jokes = None
        self.facts = None

    def run(self):
        """

        :return:
        """
        print("Running command listener ...")
        self.rtm_client.start()

    def process_incoming_msg(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        print("Received a message. Processing.")
        if "data" in kwargs:
            data = kwargs["data"]
            if "text" in data:
                msg = data["text"]
                if msg.startswith("$"):
                    command, param = self.extract_command(msg)
                    if hasattr(self, command):
                        msg = getattr(self, command)(param.lower())
                    else:
                        msg = self.default_msg(command)
                    web_client = kwargs['web_client']
                    channel_id = data["channel"]
                    for line in msg:
                        self.respond(web_client, channel_id, line)
                        time.sleep(3)

    @staticmethod
    def extract_command(full_msg):
        user_input = full_msg.split(" ")
        command = user_input[0][1:]
        if len(user_input) > 1:
            param = full_msg.split(" ")[1]
        else:
            param = ""
        return command, param

    @staticmethod
    def respond(web_client, channel, msg):
        """

        :param web_client:
        :param channel:
        :param msg:
        :return:
        """
        web_client.chat_postMessage(channel=channel, text=msg)

    @staticmethod
    def default_msg(command):
        """

        :return:
        """
        return ["Command ${} does not exist. Ask the BIG BOI to implement it for you.".format(command)]

    def joke(self, param):
        """

        :return:
        """
        if self.jokes is None:
            hot = self.reddit.subreddit("DirtyJokes").hot()
            self.jokes = []
            for post in hot:
                if post.selftext != "":
                    self.jokes.append([post.title, post.selftext])
                else:
                    self.jokes.append([post.title, "Ha ha"])
        self.joke_count += 1
        if self.joke_count <= len(self.jokes):
            return self.jokes[self.joke_count - 1]
        else:
            self.jokes = None
            return self.joke()

    def funfact(self, param):
        """

        :return:
        """
        if self.facts is None:
            hot = self.reddit.subreddit("todayilearned").hot()
            self.facts = [[post.title, post.url] for post in hot]
        self.fun_fact_count += 1
        if self.fun_fact_count <= len(self.facts):
            return self.facts[self.fun_fact_count - 1]
        else:
            self.facts = None
            return self.funfact()

    def curse(self, language):
        """

        :param language:
        :return:
        """
        if language is not None:
            if language in curses.curses:
                return [curses.curses[language][randint(0, len(curses.curses[language]) - 1)]]
        else:
            key = randint(0, len(curses.curses) - 1)
            lst = curses.curses[list(curses.curses)[key]]
            return [lst[randint(0, len(lst) - 1)]]
            # return [curses.curses[lang][randint(0, len(curses.curses[lang]))]]


def main():
    botovkov = Botovkov()
    botovkov.run()


if __name__ == "__main__":
    main()
