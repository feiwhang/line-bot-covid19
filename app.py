import json
from helper import world, cases, country, news
from linebot import LineBotApi, WebhookHandler
from flask import (Flask, abort, request, send_file, render_template, Markup)
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


@app.route('/')
def mainPage():
    w = world()
    worldPlot = Markup(w.getWorldMapHTML())
    worldRank = Markup(w.getWorldHTML())
    return render_template('world.html', worldPlot=worldPlot, worldRank=worldRank)


@app.route('/world')
def worldPage():
    w = world()
    worldPlot = Markup(w.getWorldMapHTML())
    worldRank = Markup(w.getWorldHTML())
    total = w.getWorldTotal()

    return render_template('world.html', worldPlot=worldPlot, worldRank=worldRank, totalConfirmed=total['Confirmed'],
                           totalRecovered=total['Recovered'], totalDeath=total['Death'])


@app.route('/cases')
def casesPage():
    c = cases()
    casesRank = Markup(c.getCasesHTML())
    data = c.getCasesSummary()

    return render_template('cases.html', casesRank=casesRank, confirmed=data['confirmed'], death=data['death'],
                           recovered=data['recovered'], added=data['added'])


@app.route('/country/<name>')
def countryPage(name):
    c = country()
    name = name.replace('-', ' ')

    emojiName = c.getEmojiName(name)

    try:
        countryPlot = c.getCountryPlot(name)
        countryData = c.getCountryData(name)

        return render_template('country.html', confirmed=countryData[0], death=countryData[2],
                               recovered=countryData[1], countryPlot=countryPlot, name=emojiName)
    except KeyError or Exception:
        return "ไม่พบประเทศนี้ {}".format(name)


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
    input_message = event.message.text.lower()      # input message

    # Select Country Rich menus
    if input_message == 'country':
        with open('permanentfiles/country.json', 'r') as fp:
            content = json.load(fp)
        message = FlexSendMessage(alt_text='Country', contents=content)

    # News Rich menus
    elif input_message == 'news':
        content = news().getNewsJSON()
        message = FlexSendMessage(alt_text='News', contents=content)

    else:
        message = TextSendMessage(text='ไม่พบคำสั่ง {}'.format(
            input_message))  # output message

    line_bot_api.reply_message(event.reply_token, message)


@handler.add(MessageEvent, message=LocationMessage)
def handle_message(event):
    message = TextSendMessage(text='In development')
    line_bot_api.reply_message(event.reply_token, message)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
