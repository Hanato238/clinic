import sys
sys.path.append("C:\\Users\\lesen\\workspace\\clinic")


import data_utils

file_path = 'data.xlsx'
data = data_utils.DataContainer().load(file_path).filer_by_sex('male')
print(data.get_aga_rate())
optionals = ['パーマ', 'ヘッドスパ', '商品購入', '頭髪診断', '薄毛対策(現在)', '薄毛対策(上限)']
optinal_profit_matrixes= {}
'''
for optional in optionals:
    matrix = data.get_expected_optional_profit_matrix(optional)
    optinal_profit_matrixes[optional] = matrix
    print(matrix.keys)
'''
services_satisfaction = ['薄毛専門サロン', 'クリニック', 'パーマ', 'ヘッドスパ', '市販薬', '育毛エッセンス', '薄毛対策シャンプー', 'セルフマッサージ', '機械マッサージ', 'サプリメント', '生活習慣']
for optional in services_satisfaction:
    matrix = data.get_service_satisfaction_series(optional)

# あとはoptioal_profit_matrixに年代構成比とAGA罹患率、サービス利用率をかければOK

# 年代構成比の変化による収益


# 年代別薄毛率の変化による収益
## 寄与度を調べて最小値～最大値を求めよう！