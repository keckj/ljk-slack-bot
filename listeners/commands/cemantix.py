from slack_bolt import Ack, Respond, Say
from logging import Logger

from utils.cemantix import CemantixSession

def cemantix_callback(command, ack: Ack, respond: Respond, say: Say, logger: Logger):
    if not hasattr(cemantix_callback, "session"):
        cemantix_callback.session = None
    session = cemantix_callback.session
    try:
        ack()
        if session is None:
            respond(f"Starting a cemantix session, please wait...")
            session = CemantixSession()
            session.start()
            cemantix_callback.session = session
            say(channel='games', text=f"<@{command['user_name']}> started cemantix with token {session.token}.")
        else:
            respond(f"A cémantix session is already running, join with token {session.token}.")
    except Exception as e:
        logger.error(e)
