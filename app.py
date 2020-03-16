import codecs
from datetime import datetime
from helper import writePage
from linebot import LineBotApi, WebhookHandler
from flask import Flask, abort, request, send_file
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage


app = Flask(__name__)

with open("keys/channel_access_token.txt", "r") as file:
    channel_access_token = file.read()
with open("keys/channel_secret.txt", "r") as file:
    channel_secret = file.read()

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


def getPage(mode):
    while True:
        try:
            now = datetime.utcnow()

            html = codecs.open('pages/' + mode + '.html', 'r').read()
            htmlTime = datetime.strptime(html[-26:], "%Y-%m-%d %H:%M:%S.%f")
            differ = now - htmlTime
            print(differ.seconds)
            # throw exception when more than 15 mins
            if differ.seconds > 15*60:
                raise Exception

            return html

        except NameError:
            print("Something's wrong with the name")
            break
        except IOError:
            print("File not Found")
            writePage('country')
            continue
        except Exception:
            writePage('country')
            continue

        break


@app.route('/country')
def country():
    getPage('country')


@app.route('/state')
def state():
    getPage('state')


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
    message = TextSendMessage(text='กำลังพัฒนาฟังชั่นก์นี้')  # output message
    line_bot_api.reply_message(event.reply_token, message)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
