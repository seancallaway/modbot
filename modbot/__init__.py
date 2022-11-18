from logging import getLogger

from praw import Reddit


log = getLogger(__name__)


class Bot:

    def send_discord_alert(self, message: str) -> bool:
        """
        Sends a message via Discord webhook.

        Parameters
        ----------
        message : str
            The message to send.

        Returns
        -------
        bool
            True if the message send successfully. Otherwise, False.
        """
        # TODO: Implement this (#7).
        return True

    def check_modmail(self) -> None:
        """Checks for unread modmail and alerts where there are more than last seen."""
        try:
            count = self.subreddit.modmail.unread_count()['unread']
        except KeyError:
            log.error('Reddit API not returning modmail entries. This could be an authentication issue.')
            return

        if count > 0 and count != self.last_modmail_count_alerted:
            log.info(f'Alerting on {count} unread modmail messages.')
            if not self.send_discord_alert(f'Modmail has {count} unread message(s).'):
                log.error('Failed to send Discord message for modmail.')
            self.last_modmail_count_alerted = count
        elif count == 0 and self.last_modmail_count_alerted != 0:
            log.info('Modmail read.')
            self.last_modmail_count_alerted = 0

    def check_modqueue(self) -> None:
        """Checks the modqueue and alerts when there are more items in the queue than last seen."""
        count = 0
        for _ in self.subreddit.mod.modqueue(limit=None):
            # This is needed because modqueue is an Iterable, but has no count() or len() method.
            count += 1

        if count > 0 and count != self.last_modqueue_count_alerted:
            log.info(f'Alerting on {count} items in modqueue.')
            if not self.send_discord_alert(f'The modqueue has {count} item(s) in it.'):
                log.error('Failed to send Discord message for modqueue.')
            self.last_modqueue_count_alerted = count
        elif count == 0 and self.last_modqueue_count_alerted != 0:
            log.info('Modqueue emptied.')
            self.last_modqueue_count_alerted = 0

    def __init__(self, reddit_client_id: str, reddit_client_secret: str, reddit_username: str, reddit_password: str,
                 subreddit: str, discord_webhook_url: str, modqueue_check_interval: int = 300):
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
        modqueue_check_interval : int
            The number of seconds between modqueue checks. Default 300.
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
        self.modqueue_check_interval = modqueue_check_interval

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
