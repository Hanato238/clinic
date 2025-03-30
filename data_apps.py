import sys
sys.path.append("C:\\Users\\lesen\\workspace\\clinic")

import pandas as pd
import matplotlib.pyplot as plt
from data_utils import DataContainer
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
        self.calc_expected_optional_profit: Callable[[pd.Series, pd.Series, pd.Series], dict[str, float]] = calculator.calc_expected_optional_profit_dict

        print(f"Load completed for sex: {sex}")

    def analyze_basic_profit(self) -> None:
        # 解析したい式self.calc_expected_basic_profit: Callable[[pd.Series, pd.Series], float] = calculator.calc_expected_basic_profitは線形式
        # 解析される式の変数はaga_rate, age_compでいずれも大きさ5のpd.Series
        # 
        return
    
    def analyze_optional_profit(self) -> None:
        # self.calc_expected_optional_profit: Callable[[pd.Series, pd.Series, pd.Series], dict[str, float]] = calculator.calc_expected_optional_profit_dictは線形式
        # 解析される式の変数はaga_rate, age_comp, utility_rateでいずれも大きさ5のpd.Series
        #
        return

    def show_aga_rate(self):
        print("AGA Rate:", self.aga_rate)


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
        self.optional_profit_dict = data.get_optional_profit_dict()

    def calc_expected_basic_profit(
            self,
            aga_rate: pd.Series = None,
            age_comp: pd.Series = None
    ) -> float:
        if aga_rate is None:
            aga_rate = self.data.get_aga_rate
        if age_comp is None:
            age_comp = self.data.get_age_comp

        basic_aga_profit = self.basic_profit_dict['aga']
        basic_normal_profit = self.basic_profit_dict['normal']

        expected_aga_basic_profit = basic_aga_profit.mul(age_comp).mul(aga_rate).sum()
        expected_normal_basic_profit = basic_normal_profit.mul(age_comp).mul((1-aga_rate)).sum()
        return expected_aga_basic_profit + expected_normal_basic_profit

    def calc_expected_optional_profit_dict(
            self,
            aga_rate: pd.Series,
            age_comp: pd.Series,
            utility_rate
    ) -> dict[str, float]:
        if aga_rate is None:
            aga_rate = self.data.get_aga_rate
        if age_comp is None:
            age_comp = self.data.get_age_comp
        if utility_rate is None:
            utility_rate = self.data.get_utility_rate
        
        expected_optional_profit_dict = {}
        services = self.optional_profit_series
        for name, series in services:
            expected_profit = series.mul(age_comp).mul(aga_rate).mul(utility_rate).sum()
            expected_optional_profit_dict[name] = expected_profit
        return expected_optional_profit_dict
    

