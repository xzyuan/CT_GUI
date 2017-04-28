import XPS_Q8_drivers
import sys
import time

from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from mainwindow import Ui_MainWindow

# Display error function: simplify error print out and closes socket
def displayErrorAndClose (socketId, errorCode, APIName):
    if (errorCode != -2) and (errorCode != -108):
        [errorCode2, errorString] = myxps.ErrorStringGet(socketId, errorCode)
        if (errorCode2 != 0):
            print (APIName + ': ERROR ' + str(errorCode))
    else:
        if (errorCode == -2):
            print (APIName + ': TCP timeout')
        if (errorCode == -108):
            print (APIName + ': The TCP/IP connection was closed by an administrator')
    myxps.TCP_CloseSocket(socketId)
    return

# Instantiate the class
myxps = XPS_Q8_drivers.XPS()
# Connect to the XPS
socketId_253 = myxps.TCP_ConnectToServer('192.168.0.253', 5001, 20) # Check connection passed
socketId_254 = myxps.TCP_ConnectToServer('192.168.0.254', 5001, 20) # Check connection passed

if socketId_253 == -1 or socketId_254 == -1:
    print ('Connection to XPS failed, check IP & Port')
    # TODO : qmassage! : and quit
    sys.exit ()

# Define the positioner
# group = 'Group7'
# positioner = group + '.Pos'

MotorDict_253 = {'G1光栅Y平移': 'Group1.Pos', '样品台Z平移': 'Group2.Pos', '样品台Y旋转': 'Group3.Pos', '样品台Y平移': 'Group4.Pos',
             'G1光栅Y旋转': 'Group5.Pos', 'G2光栅Z平移': 'Group6.Pos', 'G0光栅Z平移': 'Group7.Pos', 'G1光栅Z平移': 'Group8.Pos'}

MotorDict_254 = {'G0光栅X旋转': 'Group3.Pos', 'G0光栅Y旋转': 'Group7.Pos', 'G0光栅Z旋转': 'Group2.Pos', 'G1光栅X旋转': 'Group4.Pos',
             'G1光栅Z旋转': 'Group4.Pos', 'G2光栅X旋转': 'Group5.Pos', 'G2光栅Y旋转': 'Group8.Pos', 'G2光栅Z旋转': 'Group6.Pos'}


class Motor(QMainWindow):
    def __init__(self):
        super(Motor, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # quit system
        # TODO: maybe need reimplement this function
        self.ui.btn_quit.clicked.connect(quit)

        # displacement_move page
        self.ui.btn_displacement_move_start_move.setEnabled(False)
        self.ui.btn_displacement_move_stop_move.setEnabled(False)

        self.ui.btn_displacement_move_initiallize_motor.clicked.connect(self.motor_initiallize)
        self.ui.btn_displacement_move_start_move.clicked.connect(self.motor_start_move)
        self.ui.btn_displacement_move_stop_move.clicked.connect(self.motor_stop_move)

        self.ui.comboBox_displacement_move_displacement_number.currentIndexChanged.connect(self.change_Initiallize_btn)
        self.ui.comboBox_displacement_move_displacement_comboBox_displacement_move_displacement_axis.currentIndexChanged.connect(self.change_Initiallize_btn)
        self.ui.comboBox_displacement_move_displacement_type.currentIndexChanged.connect(self.change_Initiallize_btn)

    # initiallized motor name, to make some button enable or disable
    initiallize_motor_list = []

    def get_motor_name(self):
        """ :return motor name"""
        motorname = self.ui.comboBox_displacement_move_displacement_number.currentText() + \
                    self.ui.comboBox_displacement_move_displacement_comboBox_displacement_move_displacement_axis.currentText() + \
                    self.ui.comboBox_displacement_move_displacement_type.currentText()
        return str(motorname)

    def change_Initiallize_btn(self):
        """ only the motor is not initiallized can be initiallize"""
        motorname = self.get_motor_name()
        if motorname not in self.initiallize_motor_list:
            self.ui.btn_displacement_move_initiallize_motor.setEnabled(True)
            self.ui.btn_displacement_move_start_move.setEnabled(False)
            self.ui.btn_displacement_move_stop_move.setEnabled(False)
        else:
            self.ui.btn_displacement_move_initiallize_motor.setEnabled(False)
            self.ui.btn_displacement_move_start_move.setEnabled(True)
            self.ui.btn_displacement_move_stop_move.setEnabled(True)


    def motor_initiallize(self):

        motorname = self.get_motor_name()
        while (motorname not in MotorDict_253.keys()) and (motorname not in MotorDict_254.keys()):
            print(motorname)
            # TODO : qmessage : not in dict
            return

        if motorname in MotorDict_253.keys():
            group = str(MotorDict_253[motorname][0: 6])
            socketId = socketId_253
        else:
            group = str(MotorDict_254[motorname][0: 6])
            socketId = socketId_254

        self.initiallize_motor_list.append(motorname)

        [errorCode, returnString] = myxps.GroupKill(socketId, group)
        # print returnString
        if errorCode != 0:
            displayErrorAndClose(socketId, errorCode, 'GroupKill')
            sys.exit()
        # Initialize the group
        [errorCode, returnString] = myxps.GroupInitialize(socketId, group)
        # print returnString
        if errorCode != 0:
            displayErrorAndClose(socketId, errorCode, 'GroupInitialize')
            sys.exit()
        # Home search
        [errorCode, returnString] = myxps.GroupHomeSearch(socketId, group)
        # print returnString
        if errorCode != 0:
            displayErrorAndClose(socketId, errorCode, 'GroupHomeSearch')
            sys.exit()

        self.ui.btn_displacement_move_start_move.setEnabled(True)
        self.ui.btn_displacement_move_stop_move.setEnabled(True)
        self.ui.btn_displacement_move_initiallize_motor.setEnabled(False)

        print(group + " has been initialized !")

    def motor_start_move(self):
        self.ui.btn_displacement_move_start_move.setEnabled(False)
        self.ui.btn_displacement_move_stop_move.setEnabled(True)

        motorname = self.get_motor_name()
        if motorname in MotorDict_253.keys():
            motor_positioner = MotorDict_253[motorname]
            socketId = socketId_253
        else:
            motor_positioner = MotorDict_254[motorname]
            socketId = socketId_254

        absPosition = []
        absPosition.append(float(self.ui.lineEdit_displacement_move_input_displacement.text()))

        [errorCode, returnString] = myxps.GroupMoveAbsolute(socketId, motor_positioner, absPosition)
        # print returnString

        if (errorCode != 0):
            displayErrorAndClose(socketId, errorCode, 'GroupMoveAbsolute')
            sys.exit()

        self.ui.btn_displacement_move_start_move.setEnabled(True)

        print(motor_positioner + " move absolute to ",)
        print(absPosition[0])

    def motor_stop_move(self):
        self.ui.btn_displacement_move_start_move.setEnabled(False)

        motorname = self.get_motor_name()
        if motorname in MotorDict_253.keys():
            group = str(MotorDict_253[motorname][0: 6])
            socketId = socketId_253
        else:
            group = str(MotorDict_254[motorname][0: 6])
            socketId = socketId_254

        # Kill the group
        [errorCode, returnString] = myxps.GroupKill(socketId, group)
        print (returnString)
        if errorCode != 0:
            displayErrorAndClose(socketId, errorCode, 'GroupKill')
            sys.exit()

        self.initiallize_motor_list.remove(motorname)
        self.ui.btn_displacement_move_stop_move.setEnabled(False)
        self.ui.btn_displacement_move_initiallize_motor.setEnabled(True)

        print(group + " Group killed ")


    def get_picture(self):
        print("get a picture")


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    Motor = Motor()
    Motor.show()
    sys.exit(app.exec_())
