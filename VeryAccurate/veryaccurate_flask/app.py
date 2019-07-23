import json
import subprocess
import time
from queue import Queue
from veryaccurate import VeryAccurate
from flask import Flask, request
from gevent.pywsgi import WSGIServer


app = Flask(__name__)


#
# @app.route('/VeryAccurate/<flight_num>&<date>',methods=['GET', 'POST'])
# def VeryAccurate(flight_num,date):
#     # t1 = time.time()
#     if request.method == 'GET':
#         spider_name = "veryaccurate"
#         subprocess.check_output(['scrapy', 'crawl', spider_name, '-a',flight_num,'-a',date])
#         with open(r'./flight_info.json',encoding='utf-8') as items_file:
#             data = items_file.read()
#             #t2 = time.time()
#             # print(f"耗时: {t2-t1}")
#             return data

@app.route('/VeryAccurate2/<flight_num>&<date>',methods=['GET', 'POST'])
def VeryAccurate2(flight_num,date):
    if request.method == 'GET':
        flight_num = flight_num.split('=')[1].upper().strip()
        date = date.split('=')[1]
        data =  VeryAccurate(flight_num,date).MyThread()
        if data[0] != "暂无数据":
            data = {"result": data}
            return json.dumps(data,ensure_ascii=False)

        else:
            data = {"result": data[0]}
            return json.dumps(data, ensure_ascii=False)




if __name__ == '__main__':
    app.config["JSON_AS_ASCII"] = False
    #app.run(debug=True,host= '0.0.0.0',port=5000)
    WSGIServer(('0.0.0.0', 5000), app).serve_forever()
