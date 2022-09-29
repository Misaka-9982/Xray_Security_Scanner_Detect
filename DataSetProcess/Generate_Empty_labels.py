"""创建空标签"""
import os

path = './x_ray_dataset/images'

for name in os.listdir(path):
    name = name.split('.')
    if name[0][0] == 'N':
        with open(f'./x_ray_dataset/labels/{name[0]}.txt', 'w'):   # 运行配置中工作目录是\X-ray Security Scanner Detect
            pass

