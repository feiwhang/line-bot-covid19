from helper import getPage
from linebot import LineBotApi, WebhookHandler
from flask import (Flask, abort, request, send_file)
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (MessageEvent, TextMessage, TextSendMessage,
                            ImageSendMessage, QuickReply, LocationMessage,
                            LocationAction, QuickReplyButton, FlexSendMessage)


app = Flask(__name__)

with open("keys/channel_access_token.txt", "r") as file:
    channel_access_token = file.read()
with open("keys/channel_secret.txt", "r") as file:
    channel_secret = file.read()

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


@app.route('/country')
def country():
    return getPage('country')


@app.route('/state')
def state():
    return getPage('state')


@app.route("/image/<message_id>/<cmd>")
def image(cmd):
    return cmd


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
    if input_message == 'location':
        getLocation = QuickReply(items=[
            QuickReplyButton(action=LocationAction(
                label="Location", text="text"))])
        message = TextSendMessage(
            text='กดปุ่มข้างล่างเพื่อแชร์ Location', quick_reply=getLocation)

    elif input_message == 'country':
        contents = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {
                        "type": "message",
                        "style": "primary",
                        "action": {
                            "type": "uri",
                            "label": "Thailand",
                        }
                    }
                ]
            }
        }
        message = FlexSendMessage(alt_text='Country', contents=contents)

    elif input_message == 'state':
        contents = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {
                        "type": "message",
                        "style": "primary",
                        "action": {
                            "type": "uri",
                            "label": "Hubei",
                        }
                    }
                ]
            }
        }
        message = FlexSendMessage(alt_text='State', contents=contents)

    else:
        message = TextSendMessage(text='เกิดข้อผิดพลาด')

    line_bot_api.reply_message(event.reply_token, message)

    # message_id = event.message.id

    # image_url = 'https://line-bot-covid19-ljnm7xnh6a-de.a.run.app/image/' + \
    #     message_id + '/' + input_message

    # image_message = ImageSendMessage(
    #     original_content_url=image_url, preview_image_url=image_url)

    # try:
    #     line_bot_api.reply_message(event.reply_token, image_message)
    # except LineBotApiError:
    #     output_message = 'ไม่พบ {}'.format(input_message)
    #     message = TextSendMessage(text=output_message)  # output message
    #     line_bot_api.reply_message(event.reply_token, message)
    # output message


@handler.add(MessageEvent, message=LocationMessage)
def handle_message(event):
    message = TextSendMessage(text='In development')
    line_bot_api.reply_message(event.reply_token, message)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
