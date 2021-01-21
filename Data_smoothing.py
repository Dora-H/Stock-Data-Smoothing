# 導入需要使用到的模組
import numpy as np
import matplotlib.pyplot as mp
import matplotlib.dates as md
import datetime as dt

# 資料視覺圖示標題
mp.figure("Data Smoothing Returns", facecolor="lightgrey", figsize=(16, 7))
mp.title("2603.TWD / 2609.TWS \nData smoothing", fontsize=20)
# 資料視覺圖示X, Y座標設定
mp.xlabel("Dates", fontsize=14)
mp.ylabel("Returns", fontsize=14)


# 將資料內的中華民國日期轉西元年
def y2ce(ymd):
    ymd = str(ymd, encoding="utf-8")
    y, m, d = ymd.split("/")
    ymd = str(int(y)+1911) + "-" + m + "-" + d
    ymd = dt.datetime.strptime(ymd, "%Y-%m-%d").date()
    return ymd

# 依據 開盤、高價、低價、收盤價資料傳入
dates, open_prices, high_prices, low_prices, close_prices, volumes = \
    np.loadtxt("./2603.TWD.csv", delimiter=',', usecols=(1, 3, 4, 5, 6, 7), unpack=True, 
               dtype="M8[D],f4,f4,f4,f4,U10", converters={1: y2ce})

yangming_close_prices = np.loadtxt("./2609.TWD.csv", delimiter=',', usecols=6, unpack=True)

'''假設設定每天都以買收盤價，隔天賣收盤價為收益，去計算。報酬率=(今天收盤價-昨天收盤價)收益/今天又買收盤價(成本)
又假設共1,2,3,4,5天，會只有4個收益，拿收益(4個)/又買收盤價(成本)只會算到倒數第2天的位置，因最後一天又買，但是明天還沒到沒法賣，所以沒收益，不能計算'''
# np.diff()方法為今天-昨天
Eva_Marine_ROI = np.diff(close_prices)/close_prices[:-1]
Yang_Ming_Marine_ROI = np.diff(yangming_close_prices)/yangming_close_prices[:-1]

# 以下為報酬率線繪製,只會算到倒數第2天的位置，因最後一天又買，但是明天還沒到沒法賣，所以沒收益，無法計算
mp.plot(dates[:-1], Eva_Marine_ROI, linewidth=2, c='green', alpha=0.25, label="Eva Marine ROI")
mp.plot(dates[:-1], Yang_Ming_Marine_ROI, linewidth=2, c='coral', alpha=0.25, label="Yang Ming ROI")

# 以漢寧法取權重(8日)
weights8 = np.hanning(8)
# 10日權重/權重之和
weights8 /= weights8.sum()  
# 使用卷積方法
Eva_Marine_SMT = np.convolve(Eva_Marine_ROI, weights8, 'valid')
Yang_Ming_Marine_SMT = np.convolve(Yang_Ming_Marine_ROI, weights8, 'valid')
# 以下為卷積數據平滑線繪製, 8日平均點，前7天沒有值，所以從第8天開始[7:]
mp.plot(dates[7:-1], Eva_Marine_SMT, linewidth=2, c='green', label="Eva Marine Smoothing Lines")
mp.plot(dates[7:-1], Yang_Ming_Marine_SMT, linewidth=2, c='coral', label="Yang Ming Smoothing Lines")

# 找出數學多項式擬和公式，繪製擬和線
days = dates[7:-1].astype(int)
# 以多項式擬和三次方擬和
degree = 3
Eva_coefficient = np.polyfit(days, Eva_Marine_SMT,  degree)
Ymg_coefficient = np.polyfit(days, Yang_Ming_Marine_SMT,  degree)
Eva_poly_Fvalues = np.polyval(Eva_coefficient, days)
Ymg_poly_Fvalues = np.polyval(Ymg_coefficient, days)
# 以下為多項式擬和線繪製
mp.plot(dates[7:-1], Eva_poly_Fvalues, linewidth=5, c='green', label="Eva Marine Fitting Lines")
mp.plot(dates[7:-1], Ymg_poly_Fvalues, linewidth=5, c='coral', label="Yang Ming Fitting Lines")

# 找出兩條擬和線之交叉點
truning_points = np.polysub(Eva_poly_Fvalues, Ymg_poly_Fvalues)  # 先求出之差
R_x = np.roots(truning_points)                                   # 再求出交叉之根
R_y = np.polyval(Eva_coefficient, R_x)                           # 以根求出y
R_x = R_x.astype(int).astype('M8[D]')
#mp.scatter(R_x, R_y, marker="x", label="Turning Points")

# 設定格線繪製
ax = mp.gca()
# 設定x軸主要刻度(依據每周周一，不含周末)
ax.xaxis.set_major_locator(md.WeekdayLocator(byweekday=md.MONDAY))
# 設定x軸主要次刻度(依據天數)
ax.xaxis.set_minor_locator(md.DayLocator())
# 設定X軸主刻度顯示方式(日期/月份英文縮寫)
ax.xaxis.set_major_formatter(md.DateFormatter('%d-%b'))
mp.tick_params(labelsize=8)
mp.xticks(rotation=35)
mp.grid(linestyle=':')

mp.text(dates[29], -0.055, s='20210115\nDora practise.', fontsize=20, alpha=0.15)
mp.legend()
mp.show()
