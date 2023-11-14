from slack_bolt import App
from .cemantix import cemantix_callback, cemantle_callback


def register(app: App):
    app.command("/cemantix")(cemantix_callback)
    app.command("/cemantle")(cemantle_callback)
