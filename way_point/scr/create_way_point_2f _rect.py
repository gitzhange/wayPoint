#!/usr/bin/env python
# coding: utf-8

# 为 Autoware矢量图 生成 waypionts文件
'''
难点1:圆弧处走向为顺时针或者逆时针时waypoint方向与圆弧轨迹方向的关系
难点2:圆弧跨越180度时圆弧的始末角度怎么处理
'''

import math
import pandas as pd
import util


# 从文件中读取参数，返回参数的的dataframe
def get_data_to_df(datapath):
    ffile = open(datapath,'r')
    x_list =[]
    y_list =[]
    z_list =[]
    yaw_list =[]
    flag_list =[]
    arc_dir_list = []
    # crossPi_list = []
    for index,line in enumerate(ffile.readlines()):
        if index == 0:
            continue
        one_line = line.strip().split(',')
#         print(one_line)
#         if one_line:
        one_line = [float(ele) for ele in one_line]
        
        # 下面1行代码为了满足旋转的需求
        # one_line = rotate(one_line)
        x,y,z,yaw,falg,arc_dir = one_line
        # velocity = 3  # 将 直线速度 修改为3
        x_list.append(x)
        y_list.append(y)
        z_list.append(z)
        yaw_list.append(yaw)
        flag_list.append(falg)
        arc_dir_list.append(arc_dir)
        # crossPi_list.append(crossPi)
        
    # 将各列元素合并，组成一个DataFrame
    ddict = {'x' : x_list,
             'y' : y_list,
             'z' : z_list,
             'yaw' : yaw_list,
             'falg' : flag_list,
             'arc_dir' : arc_dir_list}
    para_df = pd.DataFrame(ddict)
    
    return para_df  


# 参数形式： x = -10.7265, y = -1.2615, z = 0.3209, yaw = 0, velocity = 0, change_flag = 0
# 将这一段路分成n段

# 生成直线道路上waypionts的dataframe
def generate_line_df(start,end):
    x1,y1,z1,yaw1,falg1 = start[:5]
    x2,y2,z2,yaw2,falg2 = end[:5]
    
    length = math.sqrt((x1-x2)**2+(y1-y2)**2)
    n = math.ceil(length) * 2

    x_step = (x2 - x1) / n
    y_step = (y2 - y1) / n
    z_step = (z2 - z1) / n

    # 生成每一列元素
    x_list = [x1 + ele * x_step for ele in range(n+1)]
    y_list = [y1 + ele * y_step for ele in range(n+1)]
    z_list = [z1 + ele * z_step for ele in range(n+1)]
    yaw_list = [yaw1] * (n+1)

    # 将 直线速度 修改为2
    velocity_list = [2] * (n+1)
    change_flag_list = [0] * (n+1)

    # 将各列元素合并，组成一个DataFrame
    ddict = {'x' : x_list,
             'y' : y_list,
             'z' : z_list,
             'yaw' : yaw_list,
             'velocity' : velocity_list,
             'change_flag' : change_flag_list}
    df = pd.DataFrame(ddict)
    
    return df


# 生成圆弧上一个点的坐标xy
def generate_arc_point(centerpoint,radius,theta):
    x = radius * math.cos(theta)
    y = radius * math.sin(theta)
    x += centerpoint[0]
    y += centerpoint[1]
    return x,y
# 生成圆弧上所有点的坐标xy 和 角度yaw,圆弧分5段,共有6个点
def generate_arc_point_group(centerpoint,radius,theta_start,theta_end):
    length = abs((theta_end - theta_start) * radius)
    n = math.ceil(length) * 2
    theta_list = [(theta_end - theta_start) / n * ele + theta_start for ele in range(n+1)]
    x_list = []
    y_list = []
    for theta in theta_list:
        x,y = generate_arc_point(centerpoint,radius,theta)
        x_list.append(x)
        y_list.append(y)
    return x_list, y_list, n
# 生成转弯waypionts的dataframe
def generate_arc_df(before_start, start, end, after_end, arc_dir):
    li = [before_start[:2], start[:2], end[:2], after_end[:2]]
    center_radius_startEndAngle = util.get_center_radius_startEndAngle(li)
    center = center_radius_startEndAngle[0]
    radius = center_radius_startEndAngle[1]
    trajectory_start_end = center_radius_startEndAngle[2]

    # 如果圆弧way point方向是顺时针
    if 1 == arc_dir:
        # 如果圆弧跨越了180度
        # if 1 == crossPi:
        #     print('顺时针 跨越180度 trajectory_start_end为:', trajectory_start_end)
        if trajectory_start_end[0] < trajectory_start_end[1]:
            trajectory_start_end = [trajectory_start_end[0] + 3.14*2, trajectory_start_end[1]]
        direction_start_end = [trajectory_start_end[0] - 1.57, trajectory_start_end[1] - 1.57]
    # 如果圆弧way point方向是逆时针
    if 0 == arc_dir:
        # 如果圆弧跨越了180度
        # if 1 == crossPi:
        #     print('逆时针 跨越180度 trajectory_start_end为:', trajectory_start_end)
        if trajectory_start_end[0] > trajectory_start_end[1]:
            trajectory_start_end = [trajectory_start_end[0], trajectory_start_end[1] + 3.14*2]
        direction_start_end = [trajectory_start_end[0]+1.57, trajectory_start_end[1]+1.57]

    x_list, y_list, n=generate_arc_point_group(center,radius,trajectory_start_end[0],trajectory_start_end[1])
    z_list = [0] * (n+1)
    yaw_list = [(direction_start_end[1] - direction_start_end[0]) / n * ele + direction_start_end[0] for ele in
                range(n + 1)]
    velocity_list = [2] * (n+1)
    change_flag_list = [0] * (n+1)
    # 将各列元素合并，组成一个DataFrame
    ddict = {'x' : x_list,
             'y' : y_list,
             'z' : z_list,
             'yaw' : yaw_list,
             'velocity' : velocity_list,
             'change_flag' : change_flag_list}
    df = pd.DataFrame(ddict)
    return df


def get_all_list(para_df):
    line_df_list = []
    for index in range(len(para_df)):
        if index == len(para_df) - 1:
            continue
        start = list(para_df.iloc[index])
        end = list(para_df.iloc[index + 1])
        if start[4] == 0:
            before_start = list(para_df.iloc[index-1])
            after_end = list(para_df.iloc[index + 2])
            arc_dir = start[5]
            # crossPi = start[6]
            line_df = generate_arc_df(before_start, start, end, after_end, arc_dir)
        else:
            line_df = generate_line_df(start, end)

        line_df_list.append(line_df)
    return line_df_list


# 将DataFrame保存为csv文件
def save_df2csv(df, csv_path):
    df.to_csv(csv_path,sep=',',header=True,index=False)

def run_main_stair():

    datapath = '/home/zg/PycharmProjects/proj1/wayPoint/way_point/data/data_test_8c_noPi'
    para_df1 = get_data_to_df(datapath)
    all_list = get_all_list(para_df1)

    df_concat = pd.concat(all_list)  # pd.concat是两个dataframe上下拼接成一个dataframe

    csv_path = '/home/zg/PycharmProjects/proj1/wayPoint/way_point/data/way_point_test_8c.csv'
    save_df2csv(df_concat, csv_path)


if __name__ == '__main__':
    run_main_stair()






