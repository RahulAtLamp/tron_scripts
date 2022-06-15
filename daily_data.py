import datetime
import sqlite3
from dotenv import load_dotenv

current_time = datetime.datetime.now()  # use datetime.datetime.utcnow() for UTC time
one_day_ago = current_time - datetime.timedelta(days=1)
current_epoch = (current_time.timestamp()*1000)
one_day_ago_epoch = (one_day_ago.timestamp()*1000)
print(int(current_epoch),"\n", int(one_day_ago_epoch))
connection = sqlite3.connect("trondb.db")
cursor = connection.cursor()

'''
Create DB.
'''

try:
    create_query = """
        CREATE TABLE daily(
            date INTEGER NOT NULL,
            inwards INTEGER NOT NULL,
            outwards INTEGER NOT NULL,
            net INTEGER NOT NULL
        );
    """
    cursor.execute(create_query)
except Exception as e:
    print(e)

'''
Fetch Data from DB.
'''
# one_day_ago_epoch = 1640995365
# current_epoch = 1641000351
try:
    select_query = f"""
        SELECT amount FROM transactions WHERE status='sent' AND timestamp < '{int(current_epoch*1000)}' AND timestamp > '{int(one_day_ago_epoch*1000)}'
    """
    cursor.execute(select_query)
    sent_today = cursor.fetchall()
    # print(sent_today)
    total_transfers = 0
    for today in sent_today:
        # print(today[0])
        total_transfers = total_transfers + int(today[0])
    print("data executed")
    print(total_transfers/1000000)
except Exception as e:
    print(e)

try:
    select_query = f"""
        SELECT amount FROM transactions WHERE status='received' AND timestamp < '{int(current_epoch*1000)}' AND timestamp > '{int(one_day_ago_epoch*1000)}'
    """
    cursor.execute(select_query)
    sent_today = cursor.fetchall()
    # print(sent_today)
    total_received = 0
    for today in sent_today:
        # print(today[0])
        total_received = total_transfers + int(today[0])
    print("data executed")
    print(total_received/1000000)
except Exception as e:
    pass

net = total_received - total_transfers

try:
    insert_query = """
        INSERT INTO daily(date,inwards,outwards,net) VALUES (?,?,?,?)
    """
    insert_data = (int(datetime.datetime.now().timestamp()),total_received, total_transfers, net)
    cursor.execute(insert_query,insert_data)
    connection.commit()
except Exception as e:
    print(e)

