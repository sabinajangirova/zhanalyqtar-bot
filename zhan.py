from bs4 import BeautifulSoup
from telegram import * 
from telegram.ext import * 
import requests
from selenium import webdriver
import datetime

#this function gets several news from several sites and returns the string
def get_news():
    #page = requests.get("https://24.kz/kz/zha-aly-tar")
    soup = BeautifulSoup(html, 'html.parser')
    div_itemBlock = soup.find('div', {'id':'itemListLeading'})
    for i in div_itemBlock.find_all('div', {'class':'itemContainer'}):
        link = i.find(class_='itemsContainerWrap').find(class_='itemBlock').find('header').find('h2').find('a')
        n.append((link.getText(), 'https://24.kz'+link.get('href')))
    
    return n
#this function sends a message with the news

def give_news(update, context):
    msg = n.pop(0)
    bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg[0]
    )
    bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg[1]
    )

DAY, HOUR = range(0,2)

def schedule_days(update:Update, context:CallbackContext):
    reply_markup=[["MWF", "TR"]]

    update.message.reply_text(
        "Let's schedule newsletter to be sent 5 minutes before the lecture time. \n"
        "Please indicate days of your lecture sessions",
        reply_markup=ReplyKeyboardMarkup(reply_markup, one_time_keyboard=True)
    )

    return DAY

def schedule_hour(update:Update, context:CallbackContext):
    user=update.message.from_user
    reply_markup=[]
    for i in range(9, 19):
        reply_markup.append([str(i)+".00"])
    
    global d
    d = update.message.text
    update.message.reply_text(
        f"The days chosen are {d}\nNow choose the time of the lecture sessions",
        reply_markup=ReplyKeyboardMarkup(reply_markup, one_time_keyboard=True)
    )

    return HOUR

def ending(update:Update, context:CallbackContext):
    user=update.message.from_user

    global h
    h = update.message.text.partition('.')[0]
    
    bot.send_message(
        chat_id=update.effective_chat.id,
        text = f"Okay, I've set news to be sent on {d} at {int(h)-1}.55"
    )
    if d == "MWF":
        j.run_daily(callback=give_news, days=(0,2,4), time=datetime.time(hour=int(h)-1, minute=55, second=00))
    else:
        j.run_daily(callback=give_news, days=(1,3), time=datetime.time(hour=int(h)-1, minute=55, second=00))
    
    return ConversationHandler.END

def cancel(update:Update, context:CallbackContext):
    update.message.reply_text(
        "Scheduling is canceled",
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

bot = Bot("1670596826:AAGNUZCPmm_vHxNGuU4-zfUGiTv5h77eXlU")

updater = Updater("1670596826:AAGNUZCPmm_vHxNGuU4-zfUGiTv5h77eXlU", use_context=True)
dp = updater.dispatcher
driver = webdriver.Chrome(executable_path="c:\\Users\\Мечта\\Desktop\\chromedriver")
driver.get("https://24.kz/kz/zha-aly-tar")
html = driver.page_source
n = []
n = get_news()

dp.add_handler(CommandHandler('news', give_news))

j = updater.job_queue
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('schedule', schedule_days)],
    states={
        DAY: [MessageHandler(Filters.regex('^(MWF|TR)$'), schedule_hour)],
        HOUR: [MessageHandler(Filters.regex('^(9.00|1[0-8].00)$'), ending)]
    },
    fallbacks=[CommandHandler('cancel_scheduling', cancel)],
)
dp.add_handler(conv_handler)
updater.start_polling()