'''
本模块是为了制作航迹点的圆弧部分；
场景如下：直线p1p2-->圆弧p2p3-->直线p3p4(p1 p2 p3 p4 依次为采集到的数据点)
本模块的思维流程如下：
1 通过 p1 p2 p3 p4 计算2条直线的交点p23(注意:当直线平行与Y轴时,无法计算直线的斜率,此时需要微调整数据来避免这种情况)
2 通过 p2 p23 p3 计算 角度 angle_p23
3 通过 angle_p23 p23 p3 计算半径 radius
4 通过 p2 p3 radius 计算 圆心center(难点1:算出两个圆心,怎样选择)
5 通过 center  p2 p3 计算 圆心角的始末角度(难点2:怎样计算向量的绝对角度)
author：zhange
date: 2020-05-16
'''

import numpy as np
import math
import sympy
from sympy import *
from _pydecimal import Decimal, Context, ROUND_HALF_UP   # 解决round方法遇5不入的四舍五入的问题

# 计算两点之间的欧式距离
def calculate_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    distance = math.sqrt((x1-x2)**2 + (y1-y2)**2)
    return distance

# 1 通过 p1 p2 p3 p4 计算2条直线的交点p23
def cal_cross_point(p1, p2, p3, p4):
    xA, yA = p1
    xB, yB = p2
    k1 = sympy.Symbol('k1')
    b1 = sympy.Symbol('b1')
    k1_b1_dict = sympy.solve([k1 * xA + b1 - yA, k1 * xB + b1 - yB], [k1, b1])
    print('ennn--->', k1_b1_dict)
    k1, b1 = k1_b1_dict[k1], k1_b1_dict[b1]
    # print('k1 = ',k1)

    xC, yC = p3
    xD, yD = p4
    k2 = sympy.Symbol('k2')
    b2= sympy.Symbol('b2')
    k2_b2_dict = sympy.solve([k2 * xC + b2 - yC, k2 * xD + b2 - yD], [k2, b2])
    k2, b2 = k2_b2_dict[k2], k2_b2_dict[b2]
    # print('k2 = ',k2)

    xO = sympy.Symbol('xO')
    yO= sympy.Symbol('yO')
    xO_yO_dict = sympy.solve([k1 * xO + b1 - yO, k2 * xO + b2 - yO], [xO, yO])
    xO, yO = xO_yO_dict[xO], xO_yO_dict[yO]
    print('1 交点是：', [xO, yO])
    return [xO, yO]
    # return k1 * k2


# 2 通过 p2 p23 p3 计算 角度 angle_p23（小于pi）
def calculate_theta(p2, p23, p3):
    AB = calculate_distance(p2, p23)
    BC = calculate_distance(p23, p3)
    AC = calculate_distance(p2, p3)
    cos_theta = (AB**2 + BC**2 - AC**2)/(2 * AB *BC)
    theta = math.acos(cos_theta)
    print('2 angle_p23是：', theta)
    return theta


# 3 通过 angle_p23 p23 p3 计算半径 radius
def cal_radius(angle_p23, p23, p3):
    zhibian = calculate_distance(p23, p3)
    radius = zhibian / math.tan((math.pi - angle_p23) / 2)
    print('3 radius是：', radius)
    return radius

# 4 通过 p1 p2 p3 radius 计算 圆心center
def cal_arc_center(p1, p2, p3, radius):
    xD, yD = p2
    xE, yE = p3
    # print(xA,yA,xB,yB,xD,yD,radius)
    x = sympy.Symbol('x')
    y = sympy.Symbol('y')
    centerPoint = sympy.solve([(x - xD)**2 + (y - yD)**2 - radius**2,
                               (x - xE)**2 + (y - yE)**2 - radius**2], [x, y])
    print('***centerPoint:***', centerPoint)
    valid_center = []
    for point in centerPoint:
        print('', type(point[0]), type(point[1]))
        if isinstance(point[0], add.Add) or isinstance(point[1], add.Add):
            continue
        valid_center.append(point)
    print('***valid_center:***', valid_center)

    min_distance = 10000
    min_index = 0
    for index in range(len(valid_center)):
        distance = calculate_distance(valid_center[index], p1)
        print(valid_center[index], p1, distance)
        if distance < min_distance:
            min_distance = distance
            min_index = index

    # point1, point2 = centerPoint
    # distance1 = calculate_distance(point1, p1)
    # distance2 = calculate_distance(point2, p1)
    # point = point1 if distance1 < distance2 else point2
    print('4 圆心center是：', valid_center[min_index])
    print('----*********----\n\n')
    return valid_center[min_index]

# 计算向量角度
def cal_vector_theta(pointD, pointO):
    xD, yD = pointD
    xO, yO = pointO
    vector_OD = [xD - xO, yD - yO]
    theta = math.atan2(vector_OD[1], vector_OD[0])
    return theta

# 5 通过 center  p2 p3 计算 圆心角的始末角度
def cal_arc_2theta(p2, p3, center):
    thetaD = cal_vector_theta(p2, center)
    thetaE = cal_vector_theta(p3, center)
    return [thetaD, thetaE]

# 通过上面的函数1,2,3,4,5，得到 圆心，半径，圆心角始末角度
def get_center_radius_startEndAngle(li):
    p1, p2, p3, p4 = li

    p23 = cal_cross_point(p1, p2, p3, p4)
    angle_p23 = calculate_theta(p2, p23, p3)
    radius = cal_radius(angle_p23, p23, p3)
    center = cal_arc_center(p1, p2, p3, radius)
    startEndAngle = cal_arc_2theta(p2, p3, center)

    return [center, radius, startEndAngle]

def main():
    # case1
    p1 = [1.1, 4]
    p2 = [1, 2]
    p3 = [2, 1]
    p4 = [4, 1]

    # case2
    # p1 = [1.1, 1]
    # p2 = [2, 2]
    # p3 = [4, 2]
    # p4 = [5, 1]
    li = [p1, p2, p3, p4]
    center_radius_startEndAngle = get_center_radius_startEndAngle(li)
    print(center_radius_startEndAngle)


# 入口函数
if __name__ == '__main__':
    main()