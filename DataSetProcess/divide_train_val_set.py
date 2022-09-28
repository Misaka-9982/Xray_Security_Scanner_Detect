from pathlib import Path
import random
import shutil

# 按比例分割训练集和测试集
# exp: 0.jpg->0.txt
val_rate = 0.2
assert Path('./data/images/train').is_dir()
assert Path('./data/images/val').is_dir()
assert Path('./data/labels/train').is_dir()
assert Path('./data/labels/val').is_dir()

files = [*Path('./data/images/train').glob('*.jpg')]  # *解包迭代器
labels = [*Path('./data/labels/train').glob('*.txt')]

assert len(files), '无图片文件！'
assert len(labels), '无标签文件！'

files_name = [x.name.split('.')[0] for x in files]
labels_name = [x.name.split('.')[0] for x in labels if x.name.split('.')[0][0] == 'N' or x.name.split('.')[0][0] == 'P']

num_train = len([*Path('./data/images/train').glob('*.jpg')])
num_val = len([*Path('./data/images/val').glob('*.jpg')])
assert num_val/(num_train+num_val) <= val_rate, '测试集与训练集之比已经达到/超过目标比例'  # 防止数据集比例混乱

num_files = len(files)
r_file_name = random.sample(files_name, int((num_train+num_val)*val_rate-num_val))
for i in range(len(r_file_name)):
    if r_file_name[i] in labels_name:
        try:
            shutil.move(f'./data/images/train/{r_file_name[i]}.jpg', './data/images/val')
            shutil.move(f'./data/labels/train/{r_file_name[i]}.txt', './data/labels/val')
        except shutil.Error:  # 存在同名文件
            pass
    else:
        print(f'未找到{r_file_name[i]}.jpg对应标签')

num_train = len([*Path('./data/images/train').glob('*.jpg')])
num_val = len([*Path('./data/images/val').glob('*.jpg')])
print(f'共移动{len(r_file_name)}组图片和标签')
print(f'train : val = {num_train} : {num_val}')
