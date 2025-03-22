import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm


# データの初期値設定
r = np.array([0.2, 0.25, 0.3, 0.15, 0.1])  # 年代構成比
p = np.array([0.1, 0.2, 0.3, 0.4, 0.5])  # 薄毛率
f = np.array([2, 3, 4, 5, 6])  # 健常者の年間来院頻度
f_prime = np.array([4, 5, 6, 7, 8])  # 薄毛者の年間来院頻度
s = np.array([0.7, 0.75, 0.8, 0.85, 0.9])  # 満足度
B = np.array([10000, 15000, 20000, 25000, 30000])  # 価格
E = np.random.uniform(0.1, 0.9, (5, 5))  # サービス利用率行列（ランダム）

# 年間売上期待値の計算
sales_matrix = E * r[:, None] * f_prime[:, None] * s[:, None] * B[:, None]
total_sales = np.sum(sales_matrix)

# 説明変数（各変数の影響を分析）
data = pd.DataFrame({
    'r1': r[0], 'r2': r[1], 'r3': r[2], 'r4': r[3], 'r5': r[4],
    'p1': p[0], 'p2': p[1], 'p3': p[2], 'p4': p[3], 'p5': p[4],
    'f': f,
    'f_prime': f_prime,
    's': s,
    'B': B,
    'sales': np.sum(sales_matrix, axis=1)  # 各年代の売上貢献度
})

# 回帰分析（目的変数: sales, 説明変数: 各要素）
X = data[['r1', 'r2', 'r3', 'r4', 'r5', 'p1', 'p2', 'p3', 'p4', 'p5', 'f', 'f_prime', 's', 'B']]
X = sm.add_constant(X)  # 定数項追加
Y = data['sales']
model = sm.OLS(Y, X).fit()

# 結果の表示
print(model.summary())

# 影響度の可視化
coefficients = model.params[1:]  # 定数項を除く
plt.figure(figsize=(10, 6))
plt.bar(coefficients.index, coefficients.values)
plt.xlabel('variables')
plt.ylabel('coefficients')
plt.title('each variable\'s influence')
plt.xticks(rotation=45)
plt.show()
