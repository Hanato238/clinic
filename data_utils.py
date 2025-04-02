import sys
sys.path.append("C:\\Users\\lesen\\workspace\\clinic")

from dataclasses import dataclass
import pandas as pd
from typing import Dict, Literal, Optional, Union, List

@dataclass
class DataInfo:
    name: str
    df: pd.DataFrame

@dataclass
class CustomerDist:
    sex: str = 'male'
    age_comp: pd.Series = None
    aga_rate: pd.Series = None
    age_num: pd.Series = None
    aga_num: pd.Series = None
    total: int = 100

### 延べ人数と常連顧客の母数を調べる
    def calc_fm_dist(self):
        age_num = age_comp * freq_total
        aga_num = age_num * aga_rate 
        return

    def calc_dict(self):
        
        return


OptionalItem = Literal['パーマ', 'ヘッドスパ', '商品購入', '頭髪診断', '薄毛対策(現在)', '薄毛対策(上限)']
OptinalSatisfaction = Literal['薄毛専門サロン', 'クリニック', 'パーマ', 'ヘッドスパ', '市販薬', '育毛エッセンス',
                      '薄毛対策シャンプー', 'セルフマッサージ', '機械マッサージ', 'サプリメント', '生活習慣']

## 男女でDataContainer分けてもいいかも：filterメソッドを作成しました
class DataContainer:
    def __init__(self, data: Optional[Dict[str, DataInfo]] = None):
        self.data: Dict[str, DataInfo] = data if data else {}

    def load_data(self, file_path: str, sex: Literal['male', 'female'] = 'male') -> 'DataContainer':
        self.file_path = file_path
        self.sex = sex
        # filterをかけた後に各リスト名を変更する必要があるためloaderとfilterを分けています
        return self._loader(self.file_path)._filter_by_sex(self.sex)

    # loader
    def _loader(self, file_path: str) -> 'DataContainer':
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
    # filter
    def _filter_by_sex(self, sex: Literal['male', 'female'] = 'male') -> 'DataContainer':
        if sex == 'male':
            label = '_男性'
        elif sex == 'female':
            label = '_女性'
        else:
            raise ValueError('sex is not true')

        sheet_info_dict: Dict[str, DataInfo] = {}
        filterd_sheets = {name: df for name, df in self.data.items() if name.endswith(label)}
        for sheet_name, datainfo in filterd_sheets.items():
            if datainfo.df.empty:
                print(f"[SKIP] Sheet '{sheet_name}' is empty.")
                continue
            new_sheet_name = sheet_name[:-3]

            if pd.notna(new_sheet_name):
                sheet_info_dict[new_sheet_name] = DataInfo(name=new_sheet_name, df=datainfo.df)
            else:
                print(f"[SKIP] Sheet '{sheet_name}' has NaN as first column name.")

        self.data = sheet_info_dict
        return self


# ----------美容センサスからのデータ
    # 1回あたりの美容院利用費用のデータ追加：pd.Series
    def _get_ave_fee(self) -> pd.Series:
        ave_fee = self.data['S02_1回あたり利用金額'].df.iloc[:, 0]
        return ave_fee
    
    # 年齢階級別理美容院利用率(過去1年以内の利用を継続利用者と仮定しています)：pd.Series
    def _get_utility_rate(self) -> pd.Series:
        utility_rate = self.data['S01_理美容院利用率(過去1年)'].df.iloc[:,0]/100
        return utility_rate

    # 実際のaga罹患率の取得：pd.Series
    def _get_aga_rate(self) -> pd.Series:
        datum = self.data['SQ01_気になること'].df['薄毛である']
        datum = datum / 100
        return datum
    
    # 理美容室利用頻度の取得：Dict[str, pd.Series]
    def get_freq_dict(self) -> Dict[str, pd.Series]:
        data = {}
        # aga患者の利用頻度
        datum_aga = self.data['SQ10_理美容室利用頻度_薄毛'].df['年加重平均']
        data['aga'] = datum_aga
        # 非aga患者の利用頻度
        datum_total = self.data['SQ10_理美容室利用頻度'].df['年加重平均']
        aga_rate = self._get_aga_rate()
        datum_normal = (datum_total - datum_aga * aga_rate) / (1-aga_rate)
        data['normal'] = datum_normal
        return data

    # 通常の年齢階級別構成比の取得：pd.Series
    def _get_normal_age_comp(self) -> pd.Series:
        if self.sex == 'male':
            data = {
                '20代': 6082,
                '30代': 6857,
                '40代': 9067,
                '50代': 8197,
                '60代': 7624
            }
        elif self.sex == 'female':
            data = {
                '20代': 5775,
                '30代': 6625,
                '40代': 8801,
                '50代': 8102,
                '60代': 7955
            }
        else:
            raise ValueError('sex is not true')
        series = pd.Series(data)
        series = series / series.sum()
        return series

#-----------顧客一人当たりの年間期待利益の算出のためのデータ
    # 1年間に各年代の一人の顧客が落とす散髪代金の期待値行列：Dict[pd.Series]
    def get_basic_profit_dict(
        self
    ) -> dict[str, pd.Series]:
        dict = {}
        freq_dict = self.get_freq_dict()
        ave_fee = self._get_ave_fee()

    # 各年代構成比＊各年代の利用頻度(aga+normal)*美容院にかける平均金額
        # 年代別AGA患者の年間平均売上
        freq_aga = freq_dict['aga']
        aga_basic_profit_series = freq_aga * ave_fee
        dict['aga'] = aga_basic_profit_series
        
        # 年代別健常患者の年間平均売上
        freq_normal = freq_dict['normal']
        normal_basic_profit_series = ave_fee * freq_normal
        dict['normal'] = normal_basic_profit_series

        return dict
   
    # AGA患者一人当たりの各サービスの年間期待利益行列の取得:pd.Series
    def get_optional_service_data(
        self,
        label: str,
    ) -> pd.Series:
        
        # データ範囲の選定と百分率化
        selected_data = self.data[label].df.iloc[:5, 1:7] / 100
        return selected_data
    
    # 各サービス満足度の取得：pd.Series
    def get_service_satisfaction_series(
            self, 
            optional_service: Literal['薄毛専門サロン', 'クリニック', 'パーマ', 'ヘッドスパ', '市販薬', '育毛エッセンス', '薄毛対策シャンプー', 'セルフマッサージ', '機械マッサージ', 'サプリメント', '生活習慣']
    ) -> pd.Series:
        if optional_service == '薄毛専門サロン':
            label = 'Q22S01_効果実感までの期間_薄毛専門サロンに行く_薄毛'
        elif optional_service == 'クリニック':
            label = 'Q22S02_効果実感までの期間_病院クリニックへ行く_薄毛'
        elif optional_service == 'パーマ':
            label = 'Q22S03_効果実感までの期間_ボリュームアップメニューのある理美容院へ行く_薄毛'
        elif optional_service == 'ヘッドスパ':
            label = 'Q22S04_効果実感までの期間_ヘッドスパ・ヘッドマッサージに行く_薄毛'
        elif optional_service == '市販薬':
            label = 'Q22S05_効果実感までの期間_市販の薬や漢方を使う_薄毛'
        elif optional_service == '育毛エッセンス':
            label = 'Q22S06_効果実感までの期間_育毛エッセンスローションを使う_薄毛'
        elif optional_service == '薄毛対策シャンプー':
            label = 'Q22S07_効果実感までの期間_薄毛対策シャンプーやトリートメントを使う_薄毛'
        elif optional_service == 'セルフマッサージ':
            label = 'Q22S08_効果実感までの期間_自宅で自身で頭皮マッサージを行う_薄毛'
        elif optional_service == '機械マッサージ':
            label = 'Q22S09_効果実感までの期間_自宅で器具を用いてマッサージする_薄毛'
        elif optional_service == 'サプリメント':
            label = 'Q22S10_効果実感までの期間_サプリメントを使う_薄毛'
        elif optional_service == '生活習慣':
            label = 'Q22S11_効果実感までの期間_生活習慣に気を付ける_薄毛'
        else:
            raise ValueError('optinal service is not existed')

        selected_data = self.data[label].df['効果実感あり計']
        return selected_data

