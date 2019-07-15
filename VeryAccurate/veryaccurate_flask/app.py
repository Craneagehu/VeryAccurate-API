import json
import subprocess
import time
from queue import Queue
import VariFlight
from flask import Flask, request

app = Flask(__name__)



@app.route('/VeryAccurate/<flight_num>&<date>',methods=['GET', 'POST'])
def VeryAccurate(flight_num,date):
    # t1 = time.time()
    if request.method == 'GET':
        spider_name = "veryaccurate"
        subprocess.check_output(['scrapy', 'crawl', spider_name, '-a',flight_num,'-a',date])
        with open(r'F:\\Pycharm_projects\\VeryAccurate\\VeryAccurate\\veryaccurate_flask\\flight_info.json',encoding='utf-8') as items_file:
            data = items_file.read()
            #t2 = time.time()
            # print(f"耗时: {t2-t1}")
            return data

@app.route('/VeryAccurate2/<flight_num>&<date>',methods=['GET', 'POST'])
def VeryAccurate2(flight_num,date):
    if request.method == 'GET':
        flight_num = flight_num.split('=')[1]
        date = date.split('=')[1]
        VariFlight.VariFlight(flight_num,date).MyThread()

        with open(r'F:\\Pycharm_projects\\VeryAccurate\\VeryAccurate\\veryaccurate_flask\\flight_info2.json',encoding='utf-8') as items_file:
            data = items_file.read()

            return data



if __name__ == '__main__':
    app.run(debug=True,host= '0.0.0.0',port=5000)
