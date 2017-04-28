import json


# 转台转动一圈，采集一次，G1光栅步进一步， 样平台Y轴平动1层
conf_1 = {
    "move_mode": "mode_1",
    "样品转台": 0,  # 旋转圈数
    "G1光栅": 0,  # 步数
    "样品台Y轴平动":  0  #步数
}

# 光栅G1步进一步， 样品转台旋转1角度G1归零， 样品台轴向步进1层，样品台旋转1电机归零G1电机归零
conf_2 = {
    "move_mode": "mode_2",
    "样品转台": 0,  # 旋转角度
    "G1光栅": 0,  # 步数
    "样品台Y轴平动":  0  #步数
}

# 样品转台旋转一周，触发获取一幅图像， 样品台轴向步进1层
conf_3 = {
    "move_mode": "mode_3",
    "样品转台": 0,  # 旋转角度
    "G1光栅": 0,  # 步数
    "样品台Y轴平动":  0  #步数
}

with open('conf_1.json', 'w') as f:
    json.dump(conf_1, f)

with open('conf_2.json', 'w') as f:
    json.dump(conf_2, f)

with open('conf_3.json', 'w') as f:
    json.dump(conf_3, f)

with open('conf_2.json', 'r') as f:
    m = json.load(f)

print(m)


def mode_2():
    print('ssss')

eval(m['move_mode'])()  # 注意这种用法！