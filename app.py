from multiprocessing import connection
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
import sqlite3
import datetime
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)

CORS(app)

class HelloWorld(Resource):
    def get(self):
        return({"message":"Hello World."})

class ShowData(Resource):
    def get(self):
        try:
            connection = sqlite3.connect("trondb.db")
            cursor = connection.cursor()
            selectQuery = """
                SELECT * FROM transactions ORDER BY timestamp DESC LIMIT 50
            """
            cursor.execute(selectQuery)
            allData = cursor.fetchall()
            # print(allData)
            return({"data":allData})
        except Exception as e:
            return({"message":str(e)})

class ShowDailyData(Resource):
    def get(self):
        try:
            connection = sqlite3.connect("trondb.db")
            cursor = connection.cursor()
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
            my_time = str(datetime.datetime.utcfromtimestamp(Data[0]))
            return({"date":my_time, "received":Data[1], "sent": Data[2], "net": Data[3]})
        except Exception as e:
            return({"message":"Interal server error."})

api.add_resource(HelloWorld,"/")
api.add_resource(ShowData, "/show")
api.add_resource(ShowDailyData, "/daily")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
