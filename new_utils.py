import sys
sys.path.append("C:\\Users\\lesen\\workspace\\clinic")

from dataclasses import dataclass
import pandas as pd
from typing import Dict, Literal, Optional

@dataclass
class DataInfo:
    name: str
    df: pd.DataFrame


class DataContainer:
    def __init__(self, data: Optional[Dict[str, DataInfo]] = None):
        self.data: Dict[str, DataInfo] = data if data else {}

    # loader
    def load(self, file_path: str) -> 'DataContainer':
        """Excelファイルからデータを読み込んで DataInfo に変換"""
        sheets: Dict[str, pd.DataFrame] = pd.read_excel(file_path, sheet_name=None)

        sheet_info_dict: Dict[str, DataInfo] = {}

        for sheet_name, df in sheets.items():
            if df.empty:
                print(f"[SKIP] Sheet '{sheet_name}' is empty.")
                continue

            new_sheet_name = str(df.columns[0])

            if pd.notna(new_sheet_name):
                df = df.set_index(df.columns[0]).rename_axis('年代')
                sheet_info_dict[new_sheet_name] = DataInfo(name=new_sheet_name, df=df)
            else:
                print(f"[SKIP] Sheet '{sheet_name}' has NaN as first column name.")

        self.data = sheet_info_dict
        return self

    # 実際のaga罹患率の取得
    def get_aga_rate(self, sex: Literal['male', 'female'] = 'male') -> pd.Series:
        if sex == 'male':
            datum = self.data['SQ1_気になること_男性'].df['薄毛である']
        elif sex == 'female':
            datum = self.data['SQ1_気になること_女性'].df['薄毛である']
        else:
            raise ValueError("sex must be either 'male' or 'female'")
        datum = datum / 100
        return datum
    
    # 理美容室利用頻度の取得
    def get_freq(self, sex: Literal['male', 'female'] = 'male', type: Literal['normal', 'aga'] = 'aga') -> pd.Series:
        if sex == 'male' and type == 'aga':
            datum = self.data['SQ10_理美容室利用頻度_薄毛_男性'].df['年加重平均']
        elif sex == 'female' and type == 'aga':
            datum = self.data['SQ10_理美容室利用頻度_薄毛_女性'].df['年加重平均']
        elif sex == 'male' and type == 'normal':
            datum_total = self.data['SQ10_理美容室利用頻度_男性'].df['年加重平均']
            datum_aga = self.data['SQ10_理美容室利用頻度_薄毛_男性'].df['年加重平均']
            aga_rate = self.get_aga_rate(sex)
            datum = (datum_total - datum_aga * aga_rate) / (1-aga_rate)
        elif sex == 'female' and type == 'normal':
            datum_total = self.data['SQ10_理美容室利用頻度_女性'].df['年加重平均']
            datum_aga = self.data['SQ10_理美容室利用頻度_薄毛_女性'].df['年加重平均']
            aga_rate = self.get_aga_rate(sex)
            datum = (datum_total - datum_aga * aga_rate) / (1-aga_rate)
        else:
            raise ValueError("sex must be either 'male' or 'female'")

        return datum

# \sum (basic_profit:散髪代金 + optional_profit：頭髪診断やパーマ、その他オプション代金) * ferq:来室頻度

    # 1年間に各年代の一人の顧客が落とす散髪代金の期待値行列:basic_profit_series
    def get_expected_basic_profit_series(
        self,
        aga_rate: pd.Series = None,
        sex: Literal['male', 'female'] = 'male'
    ) -> float:
        # 各年代構成比＊各年代の利用頻度(aga+normal)*美容院にかける平均金額
        # 美容センサスによる男性の美容院にかける1回あたりの平均金額
        ave_fee = pd.Series([4877, 4844, 4697, 4871, 4145], index=["20代", "30代", "40代", "50代", "60代"])

        # aga/normalの利用頻度の取得
        freq_normal = self.get_freq(type='normal')
        freq_aga = self.get_freq(type='aga')

        # aga罹患率の取得。代入されていれば不要
        if self.aga_rate is None:
            self.aga_rate = self.get_aga_rate()

        ave_freq=  aga_rate * (freq_aga - freq_normal) + freq_normal
        expected_basic_profit_series = ave_freq * ave_fee
        return expected_basic_profit_series
    
    # AGA患者一人当たりの各サービスの年間期待利益行列の取得:optional_profit_matrix
    def get_expected_optional_profit_matrix(
        self,
        optional_service: Literal['パーマ', 'ヘッドスパ', '商品購入', '頭髪診断', '薄毛対策(現在)', '薄毛対策(上限)'],
        sex: Literal['male', 'female'] = 'male'
    ) -> pd.DataFrame:
        # 受診頻度、薄毛率の取得
        freq_aga = self.get_freq(sex)
        # オプションサービスのラベル生成
        if optional_service == 'パーマ':
            label = 'Q21S1_理美容院でかけてよい金額(自発ベース)_ボリュームアップパーマ_薄毛'
        elif optional_service == 'ヘッドスパ':
            label = 'Q21S2_理美容院でかけてよい金額(自発ベース)_ヘッドスパマッサージ_薄毛'
        elif optional_service == '商品購入':
            label = 'Q21S3_理美容院でかけてよい金額(自発ベース)_商品購入_薄毛'
        elif optional_service == '頭髪診断':
            label = 'Q21S4_理美容院でかけてよい金額(自発ベース)_頭髪診断_薄毛'
        elif optional_service == '薄毛対策(現在)':
            label = 'Q8S1_薄毛対策へかけている金額_薄毛'
        elif optional_service == '薄毛対策(上限)':
            label = 'Q8S2_薄毛対策へかけてもよい金額_薄毛'
        else:
            raise ValueError('optinal service is not existed')
        
        print(label)
        if sex == 'male':
            label += '_男性'
        elif sex == 'female':
            label += '_女性'
        else:
            raise ValueError('sex is not true')

        # データ範囲の選定と百分率化
        selected_data = self.data[label].df.iloc[:5, 1:7] / 100

        # サービス単価（例：年齢層ごとに設定、6カテゴリ）
        if label.startswith('Q21'):
            fee_matrix = [2000, 3000, 4000, 5000, 10000, 10000]
        elif label.startswith('Q8'):
            fee_matrix = [1000, 2000, 3000, 5000, 10000, 15000]
        else:
            raise ValueError("label must start with 'Q21' or 'Q8'")

        # Series化（列方向と整合するように転置しておく）
        fee_series = pd.Series(fee_matrix, index=selected_data.columns).T

        # 年間期待利益の計算
        profit_matrix = selected_data.mul(fee_series, axis=1).mul(freq_aga, axis=0)
        return profit_matrix
    

