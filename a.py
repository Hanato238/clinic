import sys
sys.path.append("C:\\Users\\lesen\\workspace\\clinic")


from data_utils import data_loader, get_aga_rate, get_freq, get_expected_profit

file_path = 'data.xlsx'
data = data_loader(file_path)
freq = get_freq(data)
aga = get_aga_rate(data)
datum = data['Q8S1_薄毛対策へかけている金額_薄毛_男性']
profit = get_expected_profit(data, freq, aga, datum)

for name in data:
    print(name)