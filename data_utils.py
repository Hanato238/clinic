import sys
sys.path.append("C:\\Users\\lesen\\workspace\\clinic")

from dataclasses import dataclass
import pandas as pd
from typing import Dict, Literal, Optional, Union, List

@dataclass
class DataInfo:
    name: str
    df: pd.DataFrame

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

    # 実際のaga罹患率の取得
    def get_aga_rate(self) -> pd.Series:
        datum = self.data['SQ1_気になること'].df['薄毛である']
        datum = datum / 100
        return datum
    
    # 理美容室利用頻度の取得
    def get_freq(self, type: Literal['normal', 'aga'] = 'aga') -> pd.Series:
        if type == 'aga':
            datum = self.data['SQ10_理美容室利用頻度_薄毛'].df['年加重平均']
        elif type == 'normal':
            datum_total = self.data['SQ10_理美容室利用頻度'].df['年加重平均']
            datum_aga = self.data['SQ10_理美容室利用頻度_薄毛'].df['年加重平均']
            aga_rate = self.get_aga_rate()
            datum = (datum_total - datum_aga * aga_rate) / (1-aga_rate)
        else:
            raise ValueError("type must be either 'normal' or 'aga'")

        return datum

    # 1回あたりの美容院利用費用のデータ追加
    def get_ave_fee(self):
        if self.sex == 'male':
            ave_fee = pd.Series([4877, 4844, 4697, 4871, 4145], index=["20代", "30代", "40代", "50代", "60代"])
        elif self.sex == 'female':
            ave_fee = pd.Series([4877, 4844, 4697, 4871, 4145], index=["20代", "30代", "40代", "50代", "60代"])     
        return ave_fee
               
# \sum (basic_profit:散髪代金 + optional_profit：頭髪診断やパーマ、その他オプション代金) * ferq:来室頻度
# prof_total_pre = \sum (basic_prof * freq_ave_pre + optinal_prof * freq_aga_pre)
# prof_total_post = \sum (basic_prof * freq_ave_post + optinal_prof * freq_aga_post)


    # 1年間に各年代の一人の顧客が落とす散髪代金の期待値行列:basic_profit_series
    def get_expected_basic_profit_series(
        self,
        aga_rate: pd.Series = None
    ) -> float:
        # 各年代構成比＊各年代の利用頻度(aga+normal)*美容院にかける平均金額

        # aga/normalの利用頻度と美容院平均利用金額の取得
        freq_normal = self.get_freq(type='normal')
        freq_aga = self.get_freq(type='aga')
        ave_fee = self.get_ave_fee()

        # aga罹患率の取得。代入されていれば不要
        if self.aga_rate is None:
            self.aga_rate = self.get_aga_rate()

        ave_freq=  aga_rate * (freq_aga - freq_normal) + freq_normal
        expected_basic_profit_series = ave_freq * ave_fee
        return expected_basic_profit_series
    
    # AGA患者一人当たりの各サービスの年間期待利益行列の取得:optional_profit_matrix
    def get_expected_optional_profit_series(
        self,
        optional_service: Literal['パーマ', 'ヘッドスパ', '商品購入', '頭髪診断', '薄毛対策(現在)', '薄毛対策(上限)']
    ) -> pd.Series:
        # 受診頻度、薄毛率の取得
        freq_aga = self.get_freq(type='aga')
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
        profit_matrix = selected_data.mul(fee_series, axis=1).mul(freq_aga, axis=0).sum(axis=1)
        return profit_matrix
    
    # 各サービス満足度の取得
    def get_service_satisfaction_series(
            self, 
            optional_service: Literal['薄毛専門サロン', 'クリニック', 'パーマ', 'ヘッドスパ', '市販薬', '育毛エッセンス', '薄毛対策シャンプー', 'セルフマッサージ', '機械マッサージ', 'サプリメント', '生活習慣']
    ) -> pd.Series:
        if optional_service == '薄毛専門サロン':
            label = 'Q22S1_効果実感までの期間_薄毛専門サロンに行く_薄毛'
        elif optional_service == 'クリニック':
            label = 'Q22S2_効果実感までの期間_病院クリニックへ行く_薄毛'
        elif optional_service == 'パーマ':
            label = 'Q22S3_効果実感までの期間_ボリュームアップメニューのある理美容院へ行く_薄毛'
        elif optional_service == 'ヘッドスパ':
            label = 'Q22S4_効果実感までの期間_ヘッドスパ・ヘッドマッサージに行く_薄毛'
        elif optional_service == '市販薬':
            label = 'Q22S5_効果実感までの期間_市販の薬や漢方を使う_薄毛'
        elif optional_service == '育毛エッセンス':
            label = 'Q22S6_効果実感までの期間_育毛エッセンスローションを使う_薄毛'
        elif optional_service == '薄毛対策シャンプー':
            label = 'Q22S7_効果実感までの期間_薄毛対策シャンプーやトリートメントを使う_薄毛'
        elif optional_service == 'セルフマッサージ':
            label = 'Q22S8_効果実感までの期間_自宅で自身で頭皮マッサージを行う_薄毛'
        elif optional_service == '機械マッサージ':
            label = 'Q22S9_効果実感までの期間_自宅で器具を用いてマッサージする_薄毛'
        elif optional_service == 'サプリメント':
            label = 'Q22S10_効果実感までの期間_サプリメントを使う_薄毛'
        elif optional_service == '生活習慣':
            label = 'Q22S11_効果実感までの期間_生活習慣に気を付ける_薄毛'
        else:
            raise ValueError('optinal service is not existed')

        selected_data = self.data[label].df['効果実感あり計']
        return selected_data


    def get_optional_profit_matrix(
            self,
            items: Union[OptionalItem, List[OptionalItem]] = ['パーマ', 'ヘッドスパ', '商品購入', 
                                                              '頭髪診断', '薄毛対策(現在)', '薄毛対策(上限)']
        ) -> pd.DataFrame:
        if isinstance(items, str):
            items = [items]

        matrixes = {}
        for item in items:
            matrix = self.data.get_expected_optional_profit_series(item)
            matrixes[item] = matrix
        return pd.DataFrame(matrixes)

    def get_service_satisfaction_matrix(
            self, 
            items: Union[OptinalSatisfaction, List[OptinalSatisfaction]] = ['薄毛専門サロン', 'クリニック', 'パーマ', 'ヘッドスパ', '市販薬', '育毛エッセンス',
                      '薄毛対策シャンプー', 'セルフマッサージ', '機械マッサージ', 'サプリメント', '生活習慣']
        ) -> pd.DataFrame:
        if isinstance(items, str):
            items = [items]

        matrixes = {}
        for item in items:
            matrix = self.data.get_service_satisfaction_series(item)
            matrixes[item] = matrix
        return pd.DataFrame(matrixes).T