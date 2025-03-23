import sys
sys.path.append("C:\\Users\\lesen\\workspace\\clinic")


import new_utils

file_path = 'data.xlsx'
data = new_utils.DataContainer().load(file_path)
print(data.get_aga_rate())
optionals = ['パーマ', 'ヘッドスパ', '商品購入', '頭髪診断', '薄毛対策(現在)', '薄毛対策(上限)']
optinal_profit_matrixes= {}
for optional in optionals:
    matrix = data.get_expected_optional_profit_matrix(optional)
    optinal_profit_matrixes[optional] = matrix
    print(matrix.keys)


# 年代構成比の変化による収益


# 年代別薄毛率の変化による収益
## 寄与度を調べて最小値～最大値を求めよう！