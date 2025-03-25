import sys
sys.path.append("C:\\Users\\lesen\\workspace\\clinic")

import pandas as pd
import matplotlib.pyplot as plt
from data_utils import DataContainer
from typing import Union, List, Literal, Optional
plt.rcParams['font.family'] = 'Yu Gothic'


class AGADataAnalyzer:
    def __init__(
            self,
            file_path: str,
            aga_rate: Optional[pd.DataFrame] = None, 
            age_comp: Optional[pd.DataFrame] = None, 
            sex: str = 'male' 
            ):
        self.file_path = file_path
        self.sex = sex
        self.data = DataContainer().load_data(file_path)
        if aga_rate is None:
            self.aga_rate = self.data.get_aga_rate()
        print(f"Loaded data for sex: {sex}")

    def show_aga_rate(self):
        print("AGA Rate:", self.aga_rate)

    def plot_bar_chart(self, title: Optional[str], ylabel, transpose=False):
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

