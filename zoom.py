from flask import Flask, request
import json
import telegram
from datetime import datetime
from secrets import route, bottoken, group, meetinglink, meetingpw, pinnedmsg, route2, bottoken2, group2, meetinglink2

bot = telegram.Bot(token=bottoken)
tulbot = telegram.Bot(token=bottoken2)

app = Flask(__name__)

try:
    with open('users.json') as userfile:
        users = json.load(userfile)
except:
    with open('users.json', 'w+') as userfile:
        users = {}

participants = set()
breakout = set()
tulparticipants = set()


@app.route(route, methods=['POST'])
def zoom():
    if request.method == 'POST':
        x = request.json
        event = x['event']
        try:
            userid = x['payload']['object']['participant']['id']
            if not userid:
                raise ValueError
        except:
            userid = x['payload']['object']['participant']['user_id']
        name = x['payload']['object']['participant']['user_name']
        roomtype = x['payload']['object']['type']
        if name == 'Life YF':
            return '{"success":"true"}', 200
        global users
        if userid not in users:
            users[userid] = name
            with open('users.json', 'w') as userfile:
                json.dump(users, userfile)
        else:
            name = users[userid]
        now = datetime.now()
        current_time = now.strftime("%d/%m/%Y %H:%M:%S")
        logline = current_time
        if event == 'meeting.participant_joined':
            if roomtype > 0:
                logline += ',Joined Meeting,{},{}'.format(name, userid)
                participants.add(userid)
                num = len(participants)
                if num == 1:
                    msg = '<b>Life YF Zoom: </b><i>{}</i> is in the house. <a href="{}">Click here</a> to join!'.format(
                        name, pinnedmsg)
                    bot.send_message(
                        chat_id=group, text=msg, parse_mode=telegram.ParseMode.HTML, disable_web_page_preview=True)
                elif num % 5 == 0:
                    msg = '<b>Life YF Zoom: </b>{} people are here. <a href="{}">Click here</a> to join!'.format(
                        num, pinnedmsg)
                    bot.send_message(
                        chat_id=group, text=msg, parse_mode=telegram.ParseMode.HTML, disable_web_page_preview=True)
            else:
                logline += ',Enter Breakout Room,{},{}'.format(name, userid)
                breakout.add(userid)
        elif event == 'meeting.participant_left':
            if roomtype > 0:
                logline += ',Left Meeting,{},{}'.format(name, userid)
                participants.remove(userid)
            else:
                logline += ',Exit Breakout Room,{},{}'.format(name, userid)
                breakout.remove(userid)
        with open('log.txt', 'a+') as log:
            log.write(logline + '\n')
        msg = '<b>Life YF Zoom</b>\n<i>Meeting Link:</i> {}\n<i>Password:</i> {}\n\n<u>Current Participants</u>\n'.format(
            meetinglink, meetingpw)
        count = 1
        for userid in participants:
            msg += str(count) + '. ' + users[userid] + '\n'
            count += 1
        for userid in breakout:
            msg += str(count) + '. ' + users[userid] + ' (Breakout Room)\n'
            count += 1
        msg += '\nLast updated: {}'.format(current_time)
        bot.edit_message_text(
            chat_id=group,
            message_id=1571,
            text=msg,
            parse_mode=telegram.ParseMode.HTML,
            disable_web_page_preview=True
        )
        return '{"success":"true"}', 200


@app.route(route2, methods=['POST'])
def zoom2():
    if request.method == 'POST':
        x = request.json
        event = x['event']
        name = x['payload']['object']['participant']['user_name']
        if event == 'meeting.participant_joined':
            tulparticipants.add(name)
            logline = '{} joined'.format(name)
        elif event == 'meeting.participant_left':
            tulparticipants.remove(name)
            logline = '{} left'.format(name)
        msg = "<b>Tullie's CB zoomzoomz</b>\n\n<i>Join Zoom Meeting</i>\n{}\n\n<u>Current Participants</u>\n".format(
            meetinglink2)
        count = 1
        for user in tulparticipants:
            msg += str(count) + ') ' + user + '\n'
            count += 1
        msg = msg.strip()
        tulbot.edit_message_text(
            chat_id=group2,
            message_id=411,
            text=msg,
            parse_mode=telegram.ParseMode.HTML,
            disable_web_page_preview=True
        )
        with open('tullog.txt', 'a+') as tullog:
            tullog.write(logline + '\n')
        return '{"success":"true"}', 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, threaded=True, debug=True)
