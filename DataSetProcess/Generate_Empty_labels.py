"""创建空标签"""
import os

path = './data/images'

for name in os.listdir(path):
    name = name.split('.')
    if name[0][0] == 'N':
        with open(f'./data/labels/{name[0]}.txt', 'w'):   # 运行配置中工作目录是\X-ray Security Scanner Detect
            pass

