import XPS_Q8_drivers
import sys
import time
import json
import math

# from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QDialog, QMessageBox, QProgressBar
from mainwindow import Ui_MainWindow
from PyQt5.QtCore import *
# Connect to the XPS
myxps = XPS_Q8_drivers.XPS()
socketId_253 = myxps.TCP_ConnectToServer('192.168.0.253', 5001, 20)  # Check connection passed
socketId_254 = myxps.TCP_ConnectToServer('192.168.0.254', 5001, 20)  # Check connection passed

# 如果连接失败，弹出提示并退出
if socketId_253 == -1 or socketId_254 == -1:
    print('Connection to XPS failed, check IP & Port')
    app = QApplication(sys.argv)
    str_conectfail = 'Connection to XPS failed, check IP & Port'
    msg = QMessageBox()
    msg.setText(str_conectfail)
    msg.exec()
    sys.exit()


# xps 文档中推荐使用，用于的显示 error code
def displayErrorAndClose(socketId, errorCode, APIName):
    if errorCode != -2 and errorCode != -108:
        [errorCode2, errorString] = myxps.ErrorStringGet(socketId, errorCode)
        if errorCode2 != 0:
            print(APIName + ': ERROR ' + str(errorCode))
    else:
        if errorCode == -2:
            print(APIName + ': TCP timeout')
        if errorCode == -108:
            print(APIName + ': The TCP/IP connection was closed by an administrator')
    myxps.TCP_CloseSocket(socketId)
    return

# 两个全局Dict, 分别表示两台xps说控制的电机对应关系
MotorDict_253 = {'G1光栅Y平移': 'Group1.Pos', '样品台Z平移': 'Group2.Pos', '样品台Y旋转': 'Group3.Pos', '样品台Y平移': 'Group4.Pos',
                 'G1光栅Y旋转': 'Group5.Pos', 'G2光栅Z平移': 'Group6.Pos', 'G0光栅Z平移': 'Group7.Pos', 'G1光栅Z平移': 'Group8.Pos'}

MotorDict_254 = {'G0光栅X旋转': 'Group3.Pos', 'G0光栅Y旋转': 'Group7.Pos', 'G0光栅Z旋转': 'Group2.Pos', 'G1光栅X旋转': 'Group4.Pos',
                 'G1光栅Z旋转': 'Group4.Pos', 'G2光栅X旋转': 'Group5.Pos', 'G2光栅Y旋转': 'Group8.Pos', 'G2光栅Z旋转': 'Group6.Pos'}


class Motor:
    """
    操作电机的常用方法

    """
    # 初始化电机列表
    initiallize_motor_list = []

    def __init__(self):
        pass

    def motorname_group(self, motorname):
        if motorname in MotorDict_253.keys():
            group = str(MotorDict_253[motorname][0: 6])
            socketId = socketId_253
        else:
            group = str(MotorDict_254[motorname][0: 6])
            socketId = socketId_254
        return socketId, group

    def motorname_positioner(self, motorname):
        if motorname in MotorDict_253.keys():
            motor_positioner = MotorDict_253[motorname]
            socketId = socketId_253
        else:
            motor_positioner = MotorDict_254[motorname]
            socketId = socketId_254
        return socketId, motor_positioner

    def initiallize_single(self, motorname):
        socketId, group = self.motorname_group(motorname)

        [errorCode, returnString] = myxps.GroupKill(socketId, group)
        if errorCode != 0:
            displayErrorAndClose(socketId, errorCode, 'GroupKill')
            sys.exit()

        [errorCode, returnString] = myxps.GroupInitialize(socketId, group)
        if errorCode != 0:
            displayErrorAndClose(socketId, errorCode, 'GroupInitialize')
            sys.exit()

        [errorCode, returnString] = myxps.GroupHomeSearch(socketId, group)
        if errorCode != 0:
            displayErrorAndClose(socketId, errorCode, 'GroupHomeSearch')
            sys.exit()

        self.initiallize_motor_list.append(motorname)


    def initiallize_all(self):
        for motorname in MotorDict_253.keys():
            self.initiallize_single(motorname)
            self.initiallize_motor_list.append(motorname)

        for motorname in MotorDict_254.keys():
            self.initiallize_single(motorname)
            self.initiallize_motor_list.append(motorname)


    def move_abs(self, motorname, position):
        socketId, motor_positioner = self.motorname_positioner(motorname)

        absPosition = []
        absPosition.append(float(position))

        [errorCode, returnString] = myxps.GroupMoveAbsolute(socketId, motor_positioner, absPosition)
        if errorCode != 0:
            displayErrorAndClose(socketId, errorCode, 'GroupMoveAbsolute')
            sys.exit()


    def kill_all(self):
        for motorname in MotorDict_253.keys():
            group = str(MotorDict_253[motorname][0: 6])
            socketId = socketId_253
            [errorCode, returnString] = myxps.GroupKill(socketId, group)

        for motorname in MotorDict_254.keys():
            group = str(MotorDict_254[motorname][0: 6])
            socketId = socketId_254
            [errorCode, returnString] = myxps.GroupKill(socketId, group)

        self.initiallize_motor_list.clear()

    def kill(self, motorname):
        (socketId, group) = self.motorname_group(motorname)
        [errorCode, returnString] = myxps.GroupKill(socketId, group)
        self.initiallize_motor_list.remove(motorname)


    def get_position(self, motorname):
        socketId, positioner = self.motorname_positioner(motorname)
        [errorCode, currentPosition] = myxps.GroupPositionCurrentGet(socketId, positioner, 1)
        if (errorCode != 0):
            displayErrorAndClose (socketId, errorCode, 'GroupPositionCurrentGet')
            sys.exit()
        return float(currentPosition)




if __name__ == '__main__':
    from GUI import GUI
    app = QApplication(sys.argv)
    gui = GUI()
    gui.show()
    sys.exit(app.exec_())