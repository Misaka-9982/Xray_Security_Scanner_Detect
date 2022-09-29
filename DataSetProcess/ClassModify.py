import os

for i in os.listdir('./x_ray_dataset/labels/train'):
    if i[0] == '0' and int(i.split('.')[0]) < 358:   # 仅处理名字为0开头的
        with open('./x_ray_dataset/labels/train/'+i, 'r+') as f:
            f.write('5')
    if i[0] == '0' and int(i.split('.')[0]) >= 358:
        with open('./x_ray_dataset/labels/train/'+i, 'r+') as f:
            f.write('6')






