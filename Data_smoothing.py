'''Data smoothing :
指數平滑法是從移動平均法發展而來的，是一種改良的加權平均法，在不
舍棄歷史數據的前提下，對離預測期較近的歷史數據給予較大的權數，權
數由近到遠按指數規律遞減。 指數平滑法根據本期的實際值和預測值，
並借助於平滑系數α進行加權平均計算，預測下一期的值。
它是對時間序列數據給予加權平滑，從而獲得其變化規律與趨勢。
1. 降噪音 + 擬和 = 識別特徵
2. 卷積 + 多項式函數 = 數學方法'''
import numpy as np
import matplotlib.pyplot as mp
import matplotlib.dates as md
import datetime as dt


mp.figure("Data Smoothing Returns", facecolor="lightgrey", figsize=(16, 7))
mp.title("2603.TWD / 2609.TWS \nData smoothing", fontsize=20)
mp.xlabel("Dates", fontsize=14)
mp.ylabel("Returns", fontsize=14)


def y2ce(ymd):
    ymd = str(ymd, encoding="utf-8")
    y, m, d = ymd.split("/")
    ymd = str(int(y)+1911) + "-" + m + "-" + d          # 將中華民國轉西元年
    ymd = dt.datetime.strptime(ymd, "%Y-%m-%d").date()
    return ymd


dates, open_prices, high_prices, low_prices, close_prices, volumes = \
    np.loadtxt("./2603.TWD.csv", delimiter=',', usecols=(1, 3, 4, 5, 6, 7),
               unpack=True, dtype="M8[D],f4,f4,f4,f4,U10", converters={1: y2ce})

yangming_close_prices = np.loadtxt("./2609.TWD.csv", delimiter=',', usecols=6, unpack=True)
'''假設設定每天都以買收盤價，隔天賣收盤價為收益，去計算。報酬率=(今天收盤價-昨天收盤價)收益/今天又買收盤價(成本)
假設共1,2,3,4,5天，會只有4個收益，拿收益(4個)/又買收盤價(成本)只會算到倒數第2天的位置，因最後一天又買，但是明天還沒到沒法賣，所以沒收益，不能計算'''
# np.diff()方法為今天-昨天
Eva_Marine_ROI = np.diff(close_prices)/close_prices[:-1]
Yang_Ming_Marine_ROI = np.diff(yangming_close_prices)/yangming_close_prices[:-1]

# 以下為報酬率線繪製,只會算到倒數第2天的位置，因最後一天又買，但是明天還沒到沒法賣，所以沒收益，無法計算
mp.plot(dates[:-1], Eva_Marine_ROI, linewidth=2, c='green', alpha=0.25, label="Eva Marine ROI")
mp.plot(dates[:-1], Yang_Ming_Marine_ROI, linewidth=2, c='coral', alpha=0.25, label="Yang Ming ROI")

weights8 = np.hanning(8)    # 以漢寧法取權重(8日)
weights8 /= weights8.sum()  # 10日權重/權重之和
Eva_Marine_SMT = np.convolve(Eva_Marine_ROI, weights8, 'valid')
Yang_Ming_Marine_SMT = np.convolve(Yang_Ming_Marine_ROI, weights8, 'valid')
# 以下為卷積數據平滑線繪製, 8日平均點，前7天沒有值，所以從第8天開始[7:]
mp.plot(dates[7:-1], Eva_Marine_SMT, linewidth=2, c='green', label="Eva Marine Smooth Lines")
mp.plot(dates[7:-1], Yang_Ming_Marine_SMT, linewidth=2, c='coral', label="Yang Ming Smooth Lines")

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

ax = mp.gca()
ax.xaxis.set_major_locator(md.WeekdayLocator(byweekday=md.MONDAY))
ax.xaxis.set_minor_locator(md.DayLocator())
ax.xaxis.set_major_formatter(md.DateFormatter('%d-%b'))
mp.tick_params(labelsize=8)
mp.xticks(rotation=35)
mp.grid(linestyle=':')

mp.text(dates[29], -0.055, s='20210115\nDora practise.', fontsize=20, alpha=0.15)
mp.legend()
mp.show()
