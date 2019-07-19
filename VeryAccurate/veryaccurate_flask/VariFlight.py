import pymysql
import json
import requests
import threading
from queue import Queue


class VariFlight(object):
    def __init__(self,flight_num,date):
        self.flight_num = flight_num
        self.date = date
        self.Info = []
        self.base_url = 'http://webapp.veryzhun.com/h5/flightsearch?'
        self.headers = {
                'Accept': '*/*',
                'Origin': 'http://www.variflight.com',

                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',

        }
        self.q = Queue()
        self.q.put((self.flight_num,self.date))
        self.lock = threading.Lock()
        self.conn = pymysql.connect(host='localhost', user='root', password='admin', database='data_query', port=3306,charset='utf8')
        self.cur = self.conn.cursor()

    #返回数据
    def return_data(self,json_data):

        #航班号
        FlightNo = json_data['FlightNo']
        # 航空公司
        FlightCompany = json_data['FlightCompany']

        # 出发城市及机场
        FlightDepAirport = json_data['FlightDepAirport']

        # 登机口
        FlightHTerminal = json_data['FlightHTerminal']

        # 计划起飞
        FlightDeptimePlan = json_data['FlightDeptimePlanDate'].split()[1]

        # 实际起飞
        FlightDeptime = json_data['FlightDeptimeDate']
        if FlightDeptime:
            FlightDeptime = json_data['FlightDeptimeDate'].split(' ')[1]
        else:
            FlightDeptime = ''

        # 降落城市和机场
        FlightArrAirport = json_data['FlightArrAirport']

        # 降落出口
        FlightTerminal = json_data['FlightTerminal']

        # 计划到达
        FlightArrtimePlan = json_data['FlightArrtimePlanDate'].split()[1]

        # 实际到达
        FlightArrtime = json_data['FlightArrtimeDate']
        if FlightArrtime:
            FlightArrtime = json_data['FlightArrtimeDate'].split()[1]
        else:
            FlightArrtime = ''

        #机型
        generic = json_data['generic']

        #机龄
        FlightYear = json_data['FlightYear']

        # 历史准点率
        OntimeRate = json_data['OntimeRate']

        # 总里程
        distance = json_data['distance']

        # 飞行时间
        FlightDuration = json_data['FlightDuration']

        # 飞机状态
        FlightState = json_data['FlightState']

        info_dic = {}

        info_dic['FlightNo'] = FlightNo
        info_dic['FlightCompany'] = FlightCompany
        info_dic['FlightDepAirport'] = FlightDepAirport
        info_dic['FlightHTerminal'] = FlightHTerminal
        info_dic['FlightDeptimePlan'] = FlightDeptimePlan
        info_dic['FlightDeptime'] = FlightDeptime
        info_dic['FlightArrAirport'] = FlightArrAirport
        info_dic['FlightTerminal'] = FlightTerminal
        info_dic['FlightArrtimePlan'] = FlightArrtimePlan
        info_dic['FlightArrtime'] = FlightArrtime
        info_dic['generic'] = generic
        info_dic['FlightYear'] = FlightYear
        info_dic['OntimeRate'] = OntimeRate
        info_dic['distance'] = distance
        info_dic['FlightDuration'] = FlightDuration
        info_dic['FlightState'] = FlightState

        self.Info.append(info_dic)

        #保存到数据库
        self.save2Mysql(info_dic)

        with open('flight_info2.json','w',encoding='utf-8') as f:
            f.write(json.dumps(self.Info,ensure_ascii=False)+ '\n')

    def save2Mysql(self,data):
        keys = ','.join(data.keys())
        values = ','.join(['%s'] * len(data))

        insert_sql = "insert into flight_info (%s) values (%s)" % (keys, values)
        self.cur.execute(insert_sql, tuple(data.values()))
        self.conn.commit()

    #主函数
    def run(self):
        if not self.q.empty():
            tup = self.q.get()
            flight_num = tup[0]
            date = tup[1]
            date = date[:4] + '-' + date[4:6] + '-' + date[6:8]
            self.lock.acquire()

            data = {
                'fnum': flight_num,
                'date': date,
                'token': '74e5d4cac3179fc076af4f401fd4ebe3'

            }
            response = requests.get(self.base_url,params=data,headers=self.headers)
            response.encoding = 'utf-8'
            json_data = json.loads(response.text)
            #print(len(json_data))

            #判断返回数据类型
            #查到一条数据
            if len(json_data)== 1:
                json_data = json_data[0]
                self.return_data(json_data)

            # 未查到数据
            elif len(json_data)== 2:
                json_data = json_data['error']
                self.Info.append(json_data)

                info_dic = {}

                info_dic['FlightNo'] = flight_num
                info_dic['FlightCompany'] = ''
                info_dic['FlightDepAirport'] = ''
                info_dic['FlightHTerminal'] = ''
                info_dic['FlightDeptimePlan'] = ''
                info_dic['FlightDeptime'] = ''
                info_dic['FlightArrAirport'] = ''
                info_dic['FlightTerminal'] = ''
                info_dic['FlightArrtimePlan'] = ''
                info_dic['FlightArrtime'] = ''
                info_dic['generic'] = ''
                info_dic['FlightYear'] = ''
                info_dic['OntimeRate'] = ''
                info_dic['distance'] = ''
                info_dic['FlightDuration'] = ''
                info_dic['FlightState'] = ''

                self.save2Mysql(info_dic)

            #存在多条数据
            elif len(json_data)> 2:
                for each_data in json_data:
                    #print(each_data)
                    data = self.return_data(each_data)
                return data

            self.lock.release()

    #创建多线程
    def MyThread(self):
        thread_list = []
        for i in range(6):
            thread = threading.Thread(target=self.run)
            thread_list.append(thread)
            thread.start()

        for t in thread_list:
            t.join()
        return self.Info

#主函数入口
if __name__ == '__main__':

    flight_num = input("请输入航班号: ").upper().strip()
    date = input("请输入查询日期: ").strip()
    variflitht = VariFlight(flight_num,date)
    data = variflitht.MyThread()
    print(data)