from slack_bolt import Ack, Respond, Say
from logging import Logger

from utils.cemantix import CemantixSession, CemantleSession

def cemantix_callback(command, ack: Ack, respond: Respond, say: Say, logger: Logger):
    if not hasattr(cemantix_callback, "session"):
        cemantix_callback.session = None
    session = cemantix_callback.session

    cemantix_url = f'<{CemantixSession.game_url}|{CemantixSession.game_name}>'
    cmd = command['text'].strip()

    try:
        ack()
        if cmd:
            try:
                permile = int(cmd)
                if permile<0 or permile>1000:
                    raise ValueError
                if session is None:
                    respond(f"Cannot get hints, {CemantixSession.game_name} session is not running.")
                elif session.guesses:
                    guesses = list(filter(lambda guess: guess[-1] <= permile, session.guesses))
                    if guesses:
                        response = ""
                        for guess in guesses[:min(len(guesses), 10)]:
                            response += "\n" + " ".join(map(str, guess))
                        respond(response)
                    else:
                        respond(f"Cannot get hints, no solutions under {permile}‰ have been found yet.")
                else:
                    respond("Cannot get hints, no solutions have been found yet.")
            except ValueError:
                respond("Invalid format, expected a number between 0 and 1000.")
        else:
            if (session is None) or session.time_is_over:
                respond(f"Starting a persistent {cemantix_url} session, please wait...")
                session = CemantixSession()
                session.start()
                cemantix_callback.session = session
                say(channel='games', text=f"<@{command['user_name']}> started {cemantix_url} with token {session.token}.")
            elif session.solution_found:
                respond(f"Today's solution was already found, use /cemantix_url [0-1000] to get hints about the solution.")
            elif session.has_guesses:
                word, temp, emoji, permile = session.best_guess
                respond(f"A {cemantix_url} session is already running, join with token {session.token}, current best guess is {temp}°C {emoji} ({permile}‰).")
            else:
                respond(f"A {cemantix_url} session is already running, join with token {session.token}, no solutions have been found yet.")
    except Exception as e:
        logger.error(e)


def cemantle_callback(command, ack: Ack, respond: Respond, say: Say, logger: Logger):
    if not hasattr(cemantle_callback, "session"):
        cemantle_callback.session = None
    session = cemantle_callback.session

    cemantle_url = f'<{CemantleSession.game_url}|{CemantleSession.game_name}>'
    cmd = command['text'].strip()

    try:
        ack()
        if cmd:
            try:
                permile = int(cmd)
                if permile<0 or permile>1000:
                    raise ValueError
                if session is None:
                    respond(f"Cannot get hints, {CemantleSession.game_name} session is not running.")
                elif session.guesses:
                    guesses = list(filter(lambda guess: guess[-1] <= permile, session.guesses))
                    if guesses:
                        response = ""
                        for guess in guesses[:min(len(guesses), 10)]:
                            response += "\n" + " ".join(map(str, guess))
                        respond(response)
                    else:
                        respond(f"Cannot get hints, no solutions under {permile}‰ have been found yet.")
                else:
                    respond("Cannot get hints, no solutions have been found yet.")
            except ValueError:
                respond("Invalid format, expected a number between 0 and 1000.")
        else:
            if (session is None) or session.time_is_over:
                respond(f"Starting a persistent {cemantle_url} session, please wait...")
                session = CemantleSession()
                session.start()
                cemantle_callback.session = session
                say(channel='games', text=f"<@{command['user_name']}> started {cemantle_url} with token {session.token}.")
            elif session.solution_found:
                respond(f"Today's solution was already found, use /cemantle_url [0-1000] to get hints about the solution.")
            elif session.has_guesses:
                word, temp, emoji, permile = session.best_guess
                respond(f"A {cemantle_url} session is already running, join with token {session.token}, current best guess is {temp}°C {emoji} ({permile}‰).")
            else:
                respond(f"A {cemantle_url} session is already running, join with token {session.token}, no solutions have been found yet.")
    except Exception as e:
        logger.error(e)

