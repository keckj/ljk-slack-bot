from slack_bolt import App
from .cemantix import cemantix_callback


def register(app: App):
    app.command("/cemantix")(cemantix_callback)
