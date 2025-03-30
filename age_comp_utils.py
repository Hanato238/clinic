import pandas as pd

class AgeCompUtils:
    def __init__(self, sex: str = 'male') -> None:
        self.sex = sex
        if sex == 'male':
            data = {
                '20代': 6082,
                '30代': 6857,
                '40代': 9067,
                '50代': 8197,
                '60代': 7624
            }
        elif sex == 'female':
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
        self.age_comp = series
        return
    
    def get_local_age_comp(self):
        # 年代別構成比
        age_comp = {
            '20～29歳': 0.15,
            '30～39歳': 0.25,
            '40～49歳': 0.25,
            '50～59歳': 0.20,
            '60～69歳': 0.15
        }
        return age_comp

    def create_age_comp_dict(self) -> dict[str, pd.Series]:
        # 年代別構成比のシナリオ
        age_comp_series = pd.Series(age_comp)
        age_comp_series = age_comp_series / age_comp_series.sum()
        return age_comp_series