from time import sleep
import requests
import json
import sqlite3
import telebot
import os
from dotenv import load_dotenv
import datetime
import schedule
from threading import Thread


load_dotenv()
API_KEY = os.getenv("API_KEY")

address = 'TSaJqQ1AZ2bEYyqBwBmJqCBSPv8KPRTAdv'
only_confirned = "true"
data_limit = "200"
order_by = "block_timestamp,asc"
# print(order_by)
#&order_by={order_by}
min_timestamp = "1635724800000"
url = f"https://api.trongrid.io/v1/accounts/{address}/transactions/trc20?only_confirmed={only_confirned}&min_timestamp={min_timestamp}&limit={data_limit}&order_by={order_by}"

headers = {"Accept": "application/json"}
try:
    response = requests.get(url, headers=headers)
except Exception as e:
    print(e)
# contract_address = '41b62570d190572fca2d6f0bd9debdca13f3bbd641'

default_symbol = "USDT"

connection = sqlite3.connect("trondb.db")
cursor = connection.cursor()

table = ''' CREATE TABLE transactions(
            timestamp INTEGER NOT NULL,
            transaction_id VARCHAR(350) NOT NULL,
            symbol CHAR(50) NOT NULL,
            to_address VARCHAR(350) NOT NULL,
            from_address VARCHAR(350) NOT NULL,
            amount INTEGER NOT NULL,
            status VARCHAR(30) NOT NULL
); '''

try:
    cursor.execute(table)
    print("table created successfully")
except Exception as e:
    print(e)

datas =response.json()


bot = telebot.TeleBot(API_KEY)
bot.config['api_key'] = API_KEY

for data in datas['data']:
    # print(data['transaction_id'])
    # try:
        #print(data)
        # print(data['raw_data']['contract'][0])
        # print(data['raw_data']['contract'][0]['parameter']['value']['amount'])
        # print(data['raw_data']['contract'][0]['parameter']['value']['owner_address'])
        # print(data['raw_data']['contract'][0]['parameter']['value']['to_address'])
    timestamp = data['block_timestamp']
    
    # db_selectall = '''
    #     SELECT timestamp FROM transactions
    # '''
    # cursor.execute(db_selectall)
    # db_timestamps = cursor.fetchall()
    # timestamp_list = []        
    
    # try:
    #     for times in db_timestamps:
    #         timestamp_list.append(times[0])
    # except Exception as e:
    #     print(e)


    transaction_id = data['transaction_id']
    symbol = data['token_info']['symbol']
    from_address = data['from']
    to_address = data['to']
    transaction_type = data['type']
    value = int(data['value'])
    timestamp_val = int(data['block_timestamp'])
    if symbol == default_symbol:
        my_time = datetime.datetime.utcfromtimestamp(int(timestamp)/1000)
        # print(timestamp)
        insert_query = '''INSERT INTO transactions
                            (timestamp, transaction_id, symbol, to_address, from_address, amount) VALUES (?,?,?,?,?,?,?);
                        '''
        data_tup = (timestamp_val,transaction_id,symbol,to_address,from_address,value)
        
        if to_address == address:
            # print(f"You have successfully received {value} from {from_address} to {to_address} with transaction ID {transaction_id} at {my_time} UTC.")
            cursor.execute("""INSERT INTO transactions
                            (timestamp, transaction_id, symbol, to_address, from_address, amount, status) VALUES (?,?,?,?,?,?,?);
                        """, (timestamp_val,transaction_id,symbol,to_address,from_address,value,'received'))
            connection.commit()
            bot.send_message("-1001778640424", f"You have successfully received {int(value)/1000000} USDT from {from_address} to {to_address} at {my_time} UTC. https://tronscan.org/#/transaction/{transaction_id}")
        
        if from_address == address:
            # print(f"You have successfully transfered {value} from {from_address} to {to_address} with transaction ID {transaction_id} at {my_time} UTC.")
            cursor.execute("""INSERT INTO transactions
                            (timestamp, transaction_id, symbol, to_address, from_address, amount, status) VALUES (?,?,?,?,?,?,?);
                        """, (timestamp_val,transaction_id,symbol,to_address,from_address,value,'sent'))
            connection.commit()
            bot.send_message("-1001778640424", f"You have successfully transfered {int(value)/1000000} USDT from {from_address} to {to_address} at {my_time} UTC. https://tronscan.org/#/transaction/{transaction_id}")
    # except Exception as e:
    #     print(e)
    #     sleep(40000)

def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(1)


def send_daily_report():
    try:
        select_top = """
            SELECT MAX(date) FROM daily ;
        """
        cursor.execute(select_top)
        top1 = cursor.fetchone()
        # print(top1[0])
        select_data = f"""
            SELECT * FROM daily WHERE date = '{top1[0]}'
        """
        cursor.execute(select_data)
        Data = cursor.fetchone()
        # print(Data[0])
        my_time = datetime.datetime.utcfromtimestamp(Data[0])
        # print(my_time)
        if Data:
            pass
            bot.send_message("-1001778640424",f"Your daily summary as on {my_time}UTC: \nTotal Received: {int(Data[1])/1000000}USDT \nTotal Transfers: {int(Data[2])/1000000}USDT \nNet Amount:{int(Data[3])/1000000}USDT \n")
    except Exception as e:
        return(e)


if __name__ == '__main__':
    schedule.every().day.at("00:00").do(send_daily_report)
    # schedule.every().second.do(send_daily_report)
    Thread(target=schedule_checker).start() 

bot.poll()

