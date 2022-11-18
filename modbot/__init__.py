from praw import Reddit


class Bot:

    def __init__(self, reddit_client_id: str, reddit_client_secret: str, reddit_username: str, reddit_password: str,
                 subreddit: str, discord_webhook_url: str):
        """
        Configures an instance of the modbot.

        Parameters
        ----------
        reddit_client_id : str
            The client ID of the Reddit bot application.
        reddit_client_secret : str
            The client secret of the Reddit bot application.
        reddit_username : str
            The username of the Reddit bot user.
        reddit_password : str
            The password of the Reddit bot user.
        subreddit : str
            The name of the subreddit to monitor (e.g. 'lfg' or 'askreddit')
        discord_webhook_url : str
            The URL of the webhook created in Discord.
        """
        if None in [reddit_client_id, reddit_client_secret, reddit_username, reddit_password, subreddit,
                    discord_webhook_url]:
            raise ValueError('All init parameters are required for modbot to function properly.')

        self.r_client_id = reddit_client_id
        self.r_client_secret = reddit_client_secret
        self.r_username = reddit_username
        self.r_password = reddit_password
        self.subreddit_name = subreddit
        self.d_webhook_url = discord_webhook_url

        # Setup instance-specific values
        self.last_modqueue_check = None
        self.last_modqueue_count_alerted = 0
        self.last_modmail_check = None
        self.last_modmail_count_alerted = 0

        # Connect to Reddit via praw
        reddit = Reddit(client_id=self.r_client_id,
                        client_secret=self.r_client_secret,
                        user_agent='ModAutomation',
                        username=self.r_username,
                        password=self.r_password)

        self.subreddit = reddit.subreddit(self.subreddit_name)
        if not self.subreddit:
            raise ValueError(f'Could not access {self.subreddit_name} using the provided credentials.')
