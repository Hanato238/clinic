import sys
sys.path.append("C:\\Users\\lesen\\workspace\\clinic")


from data_utils import data_loader, get_aga_rate, get_freq

file_path = 'data.xlsx'
data = data_loader(file_path)
for name in data:
    print(name)