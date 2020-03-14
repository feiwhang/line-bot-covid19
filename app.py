from scraper import get_html
from line_command import output
from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage


app = Flask(__name__)

with open("keys/channel_access_token.txt", "r") as file:
    channel_access_token = file.read()
with open("keys/channel_secret.txt", "r") as file:
    channel_secret = file.read()

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


@app.route('/')
def table():
    return get_html()


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    input_message = event.message.text      # input message

    output_message = output(input_message)

    message = TextSendMessage(text=output_message)  # output message
    line_bot_api.reply_message(event.reply_token, message)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
