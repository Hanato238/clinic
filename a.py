import sys
sys.path.append("C:\\Users\\lesen\\workspace\\clinic")

import data_apps
import matplotlib.pyplot as plt
import pandas as pd
plt.rcParams['font.family'] = 'Yu Gothic'

file_path = 'data.xlsx'

analyzer = data_apps.AGADataAnalyzer(file_path)
#analyzer.analyze_optional_profit()
analyzer.analyze_clinic_profit()

#analyzer.show_aga_rate()

# ベース収益の期待値
basic_profit = analyzer.analyze_basic_profit()
print(f"ベース収益の期待値: {basic_profit}")







# 効果実感の分析とグラフ
satisfaction_items = ['薄毛専門サロン', 'クリニック', 'パーマ', 'ヘッドスパ', '市販薬', '育毛エッセンス',
                      '薄毛対策シャンプー', 'セルフマッサージ', '機械マッサージ', 'サプリメント', '生活習慣']
df_satisfaction = analyzer.get_service_satisfaction_matrix(satisfaction_items)
analyzer.plot_bar_chart(df_satisfaction, "年代別 効果実感あり比較", "効果実感あり（%）", transpose=True)


# あとはoptioal_profit_matrixに年代構成比とAGA罹患率、サービス利用率をかければOK
def calc_expected_profit(df: pd.DataFrame, aga_rate: pd.DataFrame, service_rate: pd.DataFrame):
    return df * aga_rate * service_rate
# 年代構成比の変化による収益


# 年代別薄毛率の変化による収益
## 寄与度を調べて最小値～最大値を求めよう！