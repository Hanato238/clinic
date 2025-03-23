from dataclasses import dataclass
import pandas as pd
from typing import Dict, Literal

@dataclass
class DataInfo:
    name: str
    df: pd.DataFrame

# データの読み込み
def data_loader(file_path: str) -> Dict[str, DataInfo]:
    sheets: Dict[str, pd.DataFrame] = pd.read_excel(file_path, sheet_name=None)
    sheet_names = list(sheets.keys())

    sheet_info_dict: Dict[str, DataInfo] = {}

    for sheet_name in sheet_names:
        df = sheets[sheet_name]

        if df.empty:
            continue

        new_sheet_name = str(df.columns[0])

        if pd.notna(new_sheet_name):
            df = df.set_index(df.columns[0]).rename_axis('年代')
            sheet_info_dict[new_sheet_name] = DataInfo(name=new_sheet_name, df=df)
    return sheet_info_dict

# 薄毛率の取得
def get_aga_rate(data: Dict[str, DataInfo], sex: Literal['male', 'female'] = 'male') -> pd.Series:
    if sex == 'male':
        datum = data['SQ1_気になること_男性'].df['薄毛である']
    elif sex == 'female':
        datum = data['SQ1_気になること_女性'].df['薄毛である']
    else:
        raise ValueError("sex must be either 'male' or 'female'")
    datum = datum / 100
    return datum

# 理美容室利用頻度の取得
def get_freq(data: Dict[str, DataInfo], sex: Literal['male', 'female'] = 'male', type: Literal['normal', 'aga'] = 'aga') -> pd.Series:
    if sex == 'male' and type == 'aga':
        datum = data['SQ10_理美容室利用頻度_薄毛_男性'].df['年加重平均']
    elif sex == 'female' and type == 'aga':
        datum = data['SQ10_理美容室利用頻度_薄毛_女性'].df['年加重平均']
    elif sex == 'male' and type == 'normal':
        datum_total = data['SQ10_理美容室利用頻度_男性'].df['年加重平均']
        datum_aga = data['SQ10_理美容室利用頻度_薄毛_男性'].df['年加重平均']
        aga_rate = get_aga_rate(data, sex)
        datum = (datum_total - datum_aga * aga_rate) / (1-aga_rate)
    elif sex == 'female' and type == 'normal':
        datum_total = data['SQ10_理美容室利用頻度_女性'].df['年加重平均']
        datum_aga = data['SQ10_理美容室利用頻度_薄毛_女性'].df['年加重平均']
        aga_rate = get_aga_rate(data, sex)
        datum = (datum_total - datum_aga * aga_rate) / (1-aga_rate)
    else:
        raise ValueError("sex must be either 'male' or 'female'")

    return datum

def get_expected_profit(
    N: int = 100,
    age_comp_rate: pd.Series = None,
    freq: pd.Series = None,
    data: Dict[str, pd.DataFrame] = None
) -> float:
    # データ範囲の選定と百分率化
    selected_data = data.df.iloc[:5, 1:7] / 100

    # サービス単価（例：年齢層ごとに設定、6カテゴリ）
    if data.name.startswith('Q21'):
        fee_matrix = [2000, 3000, 4000, 5000, 10000, 10000]
    elif data.name.startswith('Q8'):
        fee_matrix = [1000, 2000, 3000, 5000, 10000, 15000]
    else:
        raise ValueError("data.name must start with 'Q21' or 'Q8'")

    # Series化（列方向と整合するように転置しておく）
    fee_series = pd.Series(fee_matrix, index=selected_data.columns).T

    # 期待利益の計算
    profit_matrix = selected_data.mul(fee_series, axis=1).mul(age_comp_rate, axis=0).mul(freq, axis=0)
    profit = profit_matrix.sum().sum()
    return profit

# 1年間に一人の顧客が落とす散髪代金の期待値
def get_expected_basic_profit(
    age_comp_rate: pd.Series = None,
    aga_rate: pd.Series = None,
    freq_normal: pd.Series = None,
    freq_aga: pd.Series = None
) -> float:
    # 各年代構成比＊各年代の利用頻度(aga+normal)*美容院にかける平均金額
    ave_fee = pd.Series([4877, 4844, 4697, 4871, 4145], index=["20代", "30代", "40代", "50代", "60代"])
    ave_freq=  aga_rate * (freq_aga - freq_normal) + freq_normal
    expected_basic_profit_series = age_comp_rate * ave_freq * ave_fee
    print(expected_basic_profit_series)
    expected_basic_profit = expected_basic_profit_series.sum()
    return expected_basic_profit

def get_age_comp_rate() -> pd.Series:
    age_comp_rate = pd.Series([0.25, 0.30, 0.25, 0.15, 0.05], index=["20代", "30代", "40代", "50代", "60代"])
    return age_comp_rate

# \sum (basic_profit:散髪代金 + optional_profit：頭髪診断やパーマ、その他オプション代金) * ferq:来室頻度