from flask import Flask, request
import json
import telegram
from datetime import datetime
from secrets import route, bottoken, group, meetinglink, pinnedmsg
import threading
import time
import schedule

bot = telegram.Bot(token=bottoken)

app = Flask(__name__)

try:
    with open('users.json') as userfile:
        users = json.load(userfile)
except:
    with open('users.json', 'w+') as userfile:
        users = {}

participants = []
breakout = []


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
        try:
            name = x['payload']['object']['participant']['user_name']
        except:
            name = 'No Name'
        roomtype = x['payload']['object']['type']
        try:
            topic = x['payload']['object']['topic']
        except:
            topic = 'No Topic'
        try:
            host_id = x['payload']['object']['host_id']
        except:
            host_id = 'No Host'
        try:
            timestamp = x['payload']['object']['participant']['join_time']
        except:
            timestamp = x['payload']['object']['participant']['leave_time']
        global users
        if userid not in users:
            users[userid] = name
            with open('users.json', 'w') as userfile:
                json.dump(users, userfile)
        now = datetime.now()
        current_time = now.strftime("%d/%m/%Y %H:%M:%S")
        try:
            logline = timestamp
        except:
            logline = current_time
        if name == 'Life YF':
            return '{"success":"true"}', 200
        if event == 'meeting.participant_joined':
            if roomtype > 0:
                logline += ',Joined Meeting,{},{}'.format(name, topic)
                if host_id != 'OsaME2VKSpyEh6dQhVjLmw':
                    with open('otherlog.txt', 'a+') as log:
                        log.write(logline + '\n')
                    return '{"success":"true"}', 200
                participants.append(userid)
                '''
                num = len(participants)
                if num == 1:
                    msg = '<b>Life YF Zoom: </b><i>{}</i> is in the house. <a href="{}">Click here</a> to join!'.format(
                        name, pinnedmsg)
                    try:
                        bot.send_message(
                            chat_id=group, text=msg, parse_mode=telegram.ParseMode.HTML, disable_web_page_preview=True)
                    except:
                        pass
                '''
            else:
                logline += ',Enter Breakout Room,{}'.format(name)
                breakout.append(userid)
        elif event == 'meeting.participant_left':
            if roomtype > 0:
                logline += ',Left Meeting,{},{}'.format(name, topic)
                if host_id != 'OsaME2VKSpyEh6dQhVjLmw':
                    with open('otherlog.txt', 'a+') as log:
                        log.write(logline + '\n')
                    return '{"success":"true"}', 200
                try:
                    participants.remove(userid)
                except:
                    pass
            else:
                logline += ',Exit Breakout Room,{}'.format(name)
                try:
                    breakout.remove(userid)
                except:
                    pass
        with open('yflog.txt', 'a+') as log:
            log.write(logline + '\n')
        msg = '<b>Life YF Zoom</b>\n<i>Meeting Link:</i> {}\n\n<u>Current Participants</u>\n'.format(
            meetinglink)
        count = 1
        for userid in participants:
            if userid not in breakout:
                msg += str(count) + '. ' + users[userid] + '\n'
                count += 1
        inbreakout = len(breakout)
        if inbreakout > 0:
            msg += '({} in Breakout Rooms)\n'.format(str(inbreakout))
        msg += '\nLast updated: {}'.format(current_time)
        try:
            bot.edit_message_text(
                chat_id=group,
                message_id=1571,
                text=msg,
                parse_mode=telegram.ParseMode.HTML,
                disable_web_page_preview=True
            )
        except:
            pass
        return '{"success":"true"}', 200


def clearmem():
    global participants
    participants = []
    global breakout
    breakout = []
    msg = '<b>Life YF Zoom</b>\n<i>Meeting Link:</i> {}\n\nNo Participants'
    try:
        bot.edit_message_text(
            chat_id=group,
            message_id=1571,
            text=msg,
            parse_mode=telegram.ParseMode.HTML,
            disable_web_page_preview=True
        )
    except:
        pass


def scheduler():
    schedule.every().day.at("04:00").do(clearmem)
    print("Task scheduled")
    clearmem()
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    thread = threading.Thread(target=scheduler, daemon=True)
    thread.start()
    app.run(host='0.0.0.0', port=80, threaded=True, debug=True)
