import pandas as pd
from typing import Dict, Literal

# データの読み込み
def data_loader(file_path: str) -> Dict[str, pd.DataFrame]:
    sheets: Dict[str, pd.DataFrame] = pd.read_excel(file_path, sheet_name=None)
    sheet_names = list(sheets.keys())

    data: Dict[str, pd.DataFrame] = {}
    
    for sheet_name in sheet_names:
        df = sheets[sheet_name]
        
        if df.empty:
            continue
        
        new_sheet_name = str(df.columns[0])

        if pd.notna(new_sheet_name):
            #df = df.iloc[1:1].reset_index(drop=True)
            data[new_sheet_name] = df

    new_data = {name: df.set_index(df.columns[0]).rename_axis('年代') for name, df in data.items()}
    return new_data

# 薄毛率の取得
def get_aga_rate(data: Dict[str, pd.DataFrame], sex: Literal['male', 'female'] = 'male') -> pd.Series:
    if sex == 'male':
        datum = data['SQ01_気になること_男性']['薄毛である']
    elif sex == 'female':
        datum = data['SQ01_気になること_女性']['薄毛である']
    else:
        raise ValueError("sex must be either 'male' or 'female'")
    return datum

# 理美容室利用頻度の取得
def get_freq(data: Dict[str, pd.DataFrame], sex: Literal['male', 'female'] = 'male', type: Literal['normal', 'aga'] = 'aga'):
    if sex == 'male' and type == 'aga':
        datum = data['SQ10_理美容室利用頻度_薄毛_男性']['年加重平均']
    elif sex == 'female' and type == 'aga':
        datum = data['SQ10_理美容室利用頻度_薄毛_女性']['年加重平均']
    elif sex == 'male' and type == 'normal':
        datum_total = data['SQ10_理美容室利用頻度_男性']['年加重平均']
        datum_aga = data['SQ10_理美容室利用頻度_薄毛_男性']['年加重平均']
        aga_rate = get_aga_rate(data, sex)
        datum = (datum_total - datum_aga * aga_rate) / (1-aga_rate)
    elif sex == 'female' and type == 'normal':
        datum_total = data['SQ10_理美容室利用頻度_女性']['年加重平均']
        datum_aga = data['SQ10_理美容室利用頻度_薄毛_女性']['年加重平均']
        aga_rate = get_aga_rate(data, sex)
        datum = (datum_total - datum_aga * aga_rate) / (1-aga_rate)
    else:
        raise ValueError("sex must be either 'male' or 'female'")
    return datum

def get_expected_profit(
    N: int = 100,
    age_comp_rate: pd.DataFrame = None,
    freq: pd.DataFrame = None,
    data: pd.DataFrame = None,
    sex: Literal['male', 'female'] = 'male'
) -> float:
    # サービス単価（例：年齢層ごとに設定、6カテゴリ）
    fee_matrix_A = [2000, 3000, 4000, 5000, 10000, 10000]

    fee_matrix_B = [1000, 2000, 3000, 5000, 10000, 15000]

    # 性別に応じて料金行列を選択
    fee_matrix = fee_matrix_A if sex == 'male' else fee_matrix_B

    # Series化してDataFrameとブロードキャスト可能に
    fee_series = pd.Series(fee_matrix, index=data.index)

    # 各構成要素の整合性チェック
    if not (age_comp_rate.shape == freq.shape == data.shape):
        raise ValueError("age_comp_rate, freq, data は同じ形状である必要があります。")

    # 期待利益の計算
    profit_matrix = N * age_comp_rate * freq * data.multiply(fee_series, axis=0)
    profit = profit_matrix.sum().sum()
    return profit


# \sum (basic_profit:散髪代金 + optional_profit：頭髪診断やパーマ、その他オプション代金) * ferq:来室頻度

'''
\\\下記はdfのリスト
Q11_理美容院への相談経験_薄毛_女性
Q11_理美容院への相談経験_薄毛_男性
Q13_理美容室への相談意向_薄毛_女性
Q13_理美容室への相談意向_薄毛_男性
Q14_相談できていない理由_薄毛_女性
Q14_相談できていない理由_薄毛_男性
Q15_相談したくない理由_薄毛_女性
Q15_相談したくない理由_薄毛_男性
Q16_どうすれば相談したくなるか(したくないベース)_薄毛_女性
Q16_どうすれば相談したくなるか(したくないベース)_薄毛_男性
Q17_試したことのあるボリュームアップのための施術_薄毛_女性
Q17_試したことのあるボリュームアップのための施術_薄毛_男性
Q20S1_理美容院でやってみたいこと(自発ベース)_薄毛_女性
Q20S1_理美容院でやってみたいこと(自発ベース)_薄毛_男性
Q21S4_理美容院でかけてよい金額(自発ベース)_頭髪診断_薄毛_女性
Q21S4_理美容院でかけてよい金額(自発ベース)_頭髪診断_薄毛_男性
Q22S1_効果実感までの期間_薄毛専門サロンに行く_薄毛_女性
Q22S1_効果実感までの期間_薄毛専門サロンに行く_薄毛_男性
Q22S10_効果実感までの期間_サプリメントを使う_薄毛_女性
Q22S10_効果実感までの期間_サプリメントを使う_薄毛_男性
Q22S11_効果実感までの期間_生活習慣に気を付ける_薄毛_女性
Q22S11_効果実感までの期間_生活習慣に気を付ける_薄毛_男性
Q22S2_効果実感までの期間_病院クリニックへ行く_薄毛_女性
Q22S2_効果実感までの期間_病院クリニックへ行く_薄毛_男性
Q22S3_効果実感までの期間_ボリュームアップメニューのある理美容院へ行く_薄毛_女性
Q22S3_効果実感までの期間_ボリュームアップメニューのある理美容院へ行く_薄毛_男性
Q22S4_効果実感までの期間_ヘッドスパ・ヘッドマッサージに行く_薄毛_女性
Q22S4_効果実感までの期間_ヘッドスパ・ヘッドマッサージに行く_薄毛_男性
Q22S5_効果実感までの期間_市販の薬や漢方を使う_薄毛_女性
Q22S5_効果実感までの期間_市販の薬や漢方を使う_薄毛_男性
Q22S6_効果実感までの期間_育毛エッセンスローションを使う_薄毛_女性
Q22S6_効果実感までの期間_育毛エッセンスローションを使う_薄毛_男性
Q22S7_効果実感までの期間_薄毛対策シャンプーやトリートメントを使う_薄毛_女性
Q22S7_効果実感までの期間_薄毛対策シャンプーやトリートメントを使う_薄毛_男性
Q22S8_効果実感までの期間_自宅で自身で頭皮マッサージを行う_薄毛_女性
Q22S8_効果実感までの期間_自宅で自身で頭皮マッサージを行う_薄毛_男性
Q22S9_効果実感までの期間_自宅で器具を用いてマッサージする_薄毛_女性
Q22S9_効果実感までの期間_自宅で器具を用いてマッサージする_薄毛_男性
Q8S1_薄毛対策へかけている金額_薄毛_女性
Q8S1_薄毛対策へかけている金額_薄毛_男性
Q8S2_薄毛対策へかけてもよい金額_薄毛_女性
Q8S2_薄毛対策へかけてもよい金額_薄毛_男性
SQ1_気になること_女性
SQ1_気になること_男性
SQ2S1_薄毛の悩み_女性
SQ2S1_薄毛の悩み_男性
SQ3S1_薄毛への不安_女性
SQ3S1_薄毛への不安_男性
SQ05_現在行っている対策_女性
SQ05_現在行っている対策_男性
SQ5_今後試したい対策_女性
SQ5_今後試したい対策_男性
SQ10_理美容院利用頻度_女性
SQ10_理美容院利用頻度_男性
SQ10_理美容室利用頻度_薄毛_女性
SQ10_理美容室利用頻度_薄毛_男性
SQ5_過去の対策_薄毛_女性
SQ5_過去の対策_薄毛_男性
SQ5_現在の対策_薄毛_女性
SQ5_現在の対策_薄毛_男性
SQ5_今後試したい対策_薄毛_女性
SQ5_今後試したい対策_薄毛_男性
'''