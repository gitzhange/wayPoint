'''
1. 计算圆弧的[圆心坐标]和[始末角度]
2. 计算A或者C偏移的两个点
'''


import numpy as np
import math
import sympy
from _pydecimal import Decimal, Context, ROUND_HALF_UP   # 解决round方法遇5不入的四舍五入的问题
import generate_point_1230

origin_point = [20195802, 2510283]

# 计算两点之间的欧式距离
def calculate_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    distance = math.sqrt((x1-x2)**2 + (y1-y2)**2)
    return distance

# 直线AB与BC相交，计算角B（小于pi）
def calculate_theta(pointA, pointB, pointC):
    AB = calculate_distance(pointA, pointB)
    BC = calculate_distance(pointB, pointC)
    AC = calculate_distance(pointA, pointC)
    cos_theta = (AB**2 + BC**2 - AC**2)/(2 * AB *BC)
    theta = math.acos(cos_theta)
    return theta

# 已知直线AB与CD上的的ABCD四个点左边，求两直线交点坐标
def cal_cross_point(pointA, pointB, pointC, pointD):
    xA, yA = pointA
    xB, yB = pointB
    k1 = sympy.Symbol('k1')
    b1 = sympy.Symbol('b1')
    k1_b1_dict = sympy.solve([k1 * xA + b1 - yA, k1 * xB + b1 - yB], [k1, b1])
    k1, b1 = k1_b1_dict[k1], k1_b1_dict[b1]
    # print('k1 = ',k1)

    xC, yC = pointC
    xD, yD = pointD
    k2 = sympy.Symbol('k2')
    b2= sympy.Symbol('b2')
    k2_b2_dict = sympy.solve([k2 * xC + b2 - yC, k2 * xD + b2 - yD], [k2, b2])
    k2, b2 = k2_b2_dict[k2], k2_b2_dict[b2]
    # print('k2 = ',k2)

    xO = sympy.Symbol('xO')
    yO= sympy.Symbol('yO')
    xO_yO_dict = sympy.solve([k1 * xO + b1 - yO, k2 * xO + b2 - yO], [xO, yO])
    xO, yO = xO_yO_dict[xO], xO_yO_dict[yO]
    return [xO, yO]
    # return k1 * k2

# 计算园与AB，BC相切的切点
def cal_pointD(radius, theta, pointA, pointB):
    BD = radius * math.tan(1/2*(math.pi-theta))
    AB = calculate_distance(pointA, pointB)
    xA, yA = pointA
    xB, yB = pointB
    xD = BD/AB * (xA - xB) + xB
    yD = BD/AB * (yA - yB) + yB
    pointD = [xD, yD]
    return pointD

# 当得知ABC坐标和切点D的坐标，求半径大小
def cal_radius(pointA, pointB, pointC, pointD):
    theta = calculate_theta(pointA, pointB, pointC)
    BD = calculate_distance(pointB, pointD)
    radius = BD / math.tan((math.pi - theta) / 2)
    return radius

# 计算圆心
def cal_arc_center(pointA,pointD, pointE, radius):
    xD, yD = pointD
    xE, yE = pointE
    # print(xA,yA,xB,yB,xD,yD,radius)
    x = sympy.Symbol('x')
    y = sympy.Symbol('y')
    centerPoint = sympy.solve([(x - xD)**2 + (y - yD)**2 - radius**2,
                               (x - xE)**2 + (y - yE)**2 - radius**2], [x, y])
    point1, point2 = centerPoint
    distance1 = calculate_distance(point1, pointA)
    distance2 = calculate_distance(point2, pointA)
    point = point1 if distance1 < distance2 else point2
    return list(point)

# 计算向量角度
def cal_vector_theta(pointD, pointO):
    xD, yD = pointD
    xO, yO = pointO
    vector_OD = [xD - xO, yD - yO]
    # vector_OX = [1, 0]
    # cos_theta = np.dot(vector_OD,vector_OX) / (math.sqrt(xD**2 + yD**2) * 1)
    # theta = math.acos(cos_theta)
    tan_theta = vector_OD[1] / vector_OD[0]
    theta = math.atan(tan_theta)
    return theta

# 计算圆弧的始末角度
def cal_arc_2theta(pointD, pointE, pointO):
    thetaD = cal_vector_theta(pointD, pointO)
    thetaE = cal_vector_theta(pointE, pointO)
    return [thetaD, thetaE]

# 得到圆弧的圆心坐标和始末角度
def get_arc_center_2theta(ABC_and_radius):
    pointA, pointB, pointC, radius = ABC_and_radius
    theta = calculate_theta(pointA, pointB, pointC)
    pointD = cal_pointD(radius, theta, pointA, pointB)
    pointE = cal_pointD(radius, theta, pointC, pointB)
    centerpoint = cal_arc_center(pointA, pointD, pointE, radius)
    two_theta = cal_arc_2theta(pointD, pointE, centerpoint)
    # print(theta)
    # print(pointD, pointE)
    # print((centerpoint))
    # print(two_theta)
    return centerpoint, two_theta

# 计算A或者C偏移的两个点
def cal_AC_leftright(pointAC, pointB):
    print('hello111')
    xx, yy = pointAC
    xB, yB = pointB
    x = sympy.Symbol('x')
    y = sympy.Symbol('y')
    pointFG = sympy.solve([(y - yy) / (x-xx) * (yB-yy) / (xB-xx) + 1,
                               (x - xx)**2 + (y - yy)**2 - 1**2], [x, y])
    point1, point2 = pointFG
    point1 = list(point1)
    point2 = list(point2)
    pointGAF = [point2, pointAC, point1]
    for point in pointGAF:
    #     point[0], point[1] = generate_point_1230.transform_xy(point[0], point[1])
        point[0] += origin_point[0]
        point[1] += origin_point[1]
    print('hello222')
    return pointGAF

# 入口函数
if __name__ == '__main__':
    # pointA = [0.0, 0.0]
    # pointB = [6.206, 120.280]
    # pointC = [-193.434, 138.631]
    # radius = 4
    # corner1_ABC_and_r_list = [pointA, pointB, pointC, radius]
    # centerpoint, two_theta = get_arc_center_2theta(corner1_ABC_and_r_list)
    # pointGAF = cal_AC_leftright(pointA, pointB)
    # print('centerpoint:', centerpoint, '\ntwo_theta:', two_theta, '\npointGAF:', pointGAF)
    cross_point = cal_cross_point([2, 0], [1, 1], [-2, 0], [-1, 1])
    # print(cross_point)
    # radius = cal_radius([2, 0], [0, 2], [-2, 0], [2, 0])
    # print(radius)

    # corner9_cross_point = cal_cross_point([-216.995, 245.824], [-206.115, 356.021],
    #                                       [-137.010, 372.985], [-84.690, 336.298])
    # corner9_radius = cal_radius([-216.995, 245.824], corner9_cross_point,
    #                             [-84.690, 336.298], [-206.115, 356.021])  # 最后一个参数 是切点
    # print(corner9_cross_point, corner9_radius)

    cal_cross_point([-216.995, 245.824], [-206.115, 356.021],
                    [-216.995, 245.824], [-383.365, 260.053])



