import sys
sys.path.append("C:\\Users\\lesen\\workspace\\clinic")

import pandas as pd
import matplotlib.pyplot as plt
from data_utils import DataContainer, CustomerDist, EstimateCustomers
from typing import Union, List, Literal, Optional, Callable
plt.rcParams['font.family'] = 'Yu Gothic'


class AGADataAnalyzer:
    def __init__(
            self,
            file_path: str,
            sex: str = 'male' 
            ):
        self.data = DataContainer().load_data(file_path, sex)
        # 解析対象となる高階関数の作成
        calculator = DataCalculator(self.data)
        self.calc_expected_basic_profit: Callable[[pd.Series, pd.Series], float] = calculator.calc_expected_basic_profit
        self.calc_expected_optional_profit: Callable[[pd.Series, pd.Series, pd.Series], dict[str, float]] = calculator.calc_expected_optional_profit
        self.customer = CustomerDist().get_normal_dist(self.data)

        print(f"Load completed for sex: {sex}")

    def analyze_basic_profit(self) -> None:
        # 解析したい式self.calc_expected_basic_profit: Callable[[pd.Series, pd.Series], float] = calculator.calc_expected_basic_profitは線形式
        # 解析される式の変数はaga_rate, age_compでいずれも大きさ5のpd.Series
        # 
        return
    
    def analyze_optional_profit(self) -> None:
        fee_list = [1000, 1500, 2000, 2500, 3000, 5000]
        dict = {}
        for fee in fee_list:
            optional_profit = self.calc_expected_optional_profit(self.customer, '頭髪診断', fee)
            dict[fee] = optional_profit
        df = pd.DataFrame(dict, orient='index', columns=['頭髪診断'])
        df.index.name = '価格'
        df.plot(title='頭髪診断の価格による収益期待値', ylabel='収益期待値', xlabel='価格', figsize=(8, 5), kind='bar')
        plt.show()
        # self.calc_expected_optional_profit: Callable[[pd.Series, pd.Series, pd.Series], dict[str, float]] = calculator.calc_expected_optional_profit_dictは線形式
        # 解析される式の変数はaga_rate, age_comp, utility_rateでいずれも大きさ5のpd.Series
        #
        return
    
    def show_aga_rate(self):
        print("AGA Rate:", self.aga_rate)

    # 介入によるage_compの変化を複数のシナリオとして構築：dict[str, pd.Series]
    def _var_age_comp(self, age_comp: pd.Series, x: float) -> pd.Series:
        result

    def _plot_bar_chart(self, title: Optional[str], ylabel, transpose=False):
        if title == '':
            df = self.data.get_optional_profit_matrix
        elif title == '':
            df = self.data.get_service_satisfaction_matrix

        if transpose:
            df = df.T
        ax = df.plot.bar(rot=0, figsize=(8, 5), title=title)
        for container in ax.containers:
            ax.bar_label(container, fmt='%.1f')
        plt.ylabel(ylabel)
        plt.tight_layout()
        plt.show()


class DataCalculator:
    def __init__(self, data: DataContainer):
        self.data = data
        self.basic_profit_dict = data.get_basic_profit_dict()

### 顧客一人当たりの年間期待利益→集客効果を考慮していない
    def calc_expected_basic_profit(
            self,
            customers: CustomerDist
    ) -> float:
        if customers is None:
            raise ValueError('customers is None')
        age_comp = customers.age_comp
        aga_rate = customers.aga_rate

        basic_aga_profit = self.basic_profit_dict['aga']
        basic_normal_profit = self.basic_profit_dict['normal']

        expected_aga_basic_profit = basic_aga_profit.mul(age_comp).mul(aga_rate).sum()
        expected_normal_basic_profit = basic_normal_profit.mul(age_comp).mul((1-aga_rate)).sum()
        return expected_aga_basic_profit + expected_normal_basic_profit

    def calc_expected_optional_profit(
            self,
            customers: CustomerDist,
            optional_service: str,
            cost: int = 0
    ) -> pd.Series:
        if customers is None:
            raise ValueError('customers is None')
        age_comp = customers.age_comp
        aga_rate = customers.aga_rate

        # オプションサービスのラベル生成
        label = self._gen_labels(optional_service)
        # オプションサービスのデータ取得
        data = self.data.get_optional_service_data(label)
        # 価格に依存したオプションサービスの利用率の取得
        acceptance = self._get_cost_acceptance(label, data, cost)

        # ある価格に対する各年代の1人1回当たりのオプションサービスの期待収益
        optional_profit_series = data.mul(acceptance, axis=1).sum(axis=0, skipna=True)
        # オプションサービスの期待収益
        optional_profit = optional_profit_series.mul(age_comp).mul(aga_rate).sum()
        return optional_profit
    

    def _gen_labels(self, optional_service:str) -> str:
        if optional_service == 'パーマ':
            label = 'Q21S01_理美容院でかけてよい金額(自発ベース)_ボリュームアップパーマ_薄毛'
        elif optional_service == 'ヘッドスパ':
            label = 'Q21S02_理美容院でかけてよい金額(自発ベース)_ヘッドスパマッサージ_薄毛'
        elif optional_service == '商品購入':
            label = 'Q21S03_理美容院でかけてよい金額(自発ベース)_商品購入_薄毛'
        elif optional_service == '頭髪診断':
            label = 'Q21S04_理美容院でかけてよい金額(自発ベース)_頭髪診断_薄毛'
        elif optional_service == '薄毛対策(現在)':
            label = 'Q08S01_薄毛対策へかけている金額_薄毛'
        elif optional_service == '薄毛対策(上限)':
            label = 'Q08S02_薄毛対策へかけてもよい金額_薄毛'
        else:
            raise ValueError('optinal service is not existed')
        
        return label
    
    def _get_cost_acceptance(self, label:List, data:pd.Series, cost:float) -> pd.Series:
        # labelごとの価格区分
        if label.startswith('Q21'):
            fee_list = [2000, 3000, 4000, 5000, 10000, 10000]
        elif label.startswith('Q08'):
            fee_list = [1000, 2000, 3000, 5000, 10000, 15000]
        else:
            raise ValueError("label must start with 'Q21' or 'Q08'")
        
        list = []
###ここから再開＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃
        for i in range(len(list)):
            list[i] = fee_list[i] / cost
            if list[i] > 1:
                list[i] = 1        
            list[i] = list[i] * fee_list[i]

        print(list)
        expected_fee_series = pd.Series(list, index=data.columns).T

        return expected_fee_series