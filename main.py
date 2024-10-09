import sys
from PyQt5.QtWidgets import *
import Kiwoom
import time
from pandas import DataFrame
import datetime
import os


MARKET_KOSPI = 0
MARKET_KOSDAQ = 10


class PyMon:
    def __init__(self):
        self.kiwoom = Kiwoom.Kiwoom()
        self.kiwoom.comm_connect()
        self.get_code_list()

    def get_code_list(self):
        self.kospi_codes = self.kiwoom.get_code_list_by_market(MARKET_KOSPI)[0:500]
        self.kosdaq_codes = self.kiwoom.get_code_list_by_market(MARKET_KOSDAQ)[0:500]

    def get_ohlcv(self, code, start):
        self.kiwoom.ohlcv = {'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}
        self.kiwoom.set_input_value("종목코드", code)
        self.kiwoom.set_input_value("기준일자", start)
        self.kiwoom.set_input_value("수정주가구분", 1)
        self.kiwoom.comm_rq_data("opt10081_req", "opt10081", 0, "0101")
        time.sleep(0.6)
        df = DataFrame(self.kiwoom.ohlcv, columns=['open', 'high', 'low', 'close', 'volume'], index=self.kiwoom.ohlcv['date'])
        return df

    def save_to_csv(self, df, code):
        """데이터프레임을 csv 파일로 지정한 경로에 저장"""
        save_path = 'C:/Users/home/Desktop/kosdaq/'  # 원하는 저장 경로를 지정
        if not os.path.exists(save_path):
            os.makedirs(save_path)  # 경로가 없으면 생성
        file_name = os.path.join(save_path, f'{code}.csv')  # 저장 경로와 파일명을 합쳐서 지정
        df.to_csv(file_name, encoding='utf-8-sig')  # CSV로 저장
        #print(f"Saved {file_name}")

    def check_speedy_rising_volume(self, code):
        nBefore = 0
        PivotDatetime = datetime.datetime.now()
        before = PivotDatetime - datetime.timedelta(days=nBefore)
        today = before.strftime('%Y%m%d')
        df = self.get_ohlcv(code, today)
        volumes = df['volume']

        if len(volumes) <= 136:
            return False

        # 볼륨 상승 여부를 확인하는 로직 추가 (임시 로직으로 수정 가능)
        return True

    def update_buy_list(self, buy_list):
        with open("pymon_list.txt", "wt") as f:
            for code in buy_list:
                f.write(f"{code}\n")

    def run(self):
        buy_list = []

        for i, code in enumerate(self.kosdaq_codes):
            #print(i, '/', len(self.kosdaq_codes))

            if self.check_speedy_rising_volume(code):
                print(f"'{code}',")
                buy_list.append(code)

                # OHLCV 데이터 가져와서 CSV로 저장
                today = datetime.datetime.now().strftime('%Y%m%d')
                df = self.get_ohlcv(code, today)
                self.save_to_csv(df, code)

        self.update_buy_list(buy_list)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pymon = PyMon()
    pymon.run()
