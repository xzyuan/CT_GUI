import XPS_Q8_drivers
import sys
import time
import json
import math

from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QDialog, QMessageBox
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
socketId_253 = myxps.TCP_ConnectToServer('192.168.0.253', 5001, 20)  # Check connection passed
socketId_254 = myxps.TCP_ConnectToServer('192.168.0.254', 5001, 20)  # Check connection passed

if socketId_253 == -1 or socketId_254 == -1:
    print ('Connection to XPS failed, check IP & Port')

    # TODO : qmassage! : and quit
    app = QApplication(sys.argv)
    str_conectfail = 'Connection to XPS failed, check IP & Port'
    msg = QMessageBox()
    msg.setText(str_conectfail)
    msg.exec()

    sys.exit()

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

        self.ui.btn_displacement_move_kill_all.clicked.connect(self.motor_kill_all)
        self.ui.btn_displacement_move_upload.clicked.connect(self.motor_parameter_upload)
        self.ui.btn_displacement_move_save_all.clicked.connect(self.motor_parameter_save_all)

        self.ui.comboBox_displacement_move_displacement_number.currentIndexChanged.connect(self.change_Initiallize_btn)
        self.ui.comboBox_displacement_move_displacement_comboBox_displacement_move_displacement_axis.currentIndexChanged.connect(self.change_Initiallize_btn)
        self.ui.comboBox_displacement_move_displacement_type.currentIndexChanged.connect(self.change_Initiallize_btn)

        # log
        self.ui.btn_log_write.clicked.connect(self.write_manual_log)
        self.ui.textEdit_log_daily_log.textChanged.connect(self.write_daily_log)

        # scanning
        self.ui.btn_CTscan_start_scan.clicked.connect(self.start_scan)
        self.ui.btn_CTscan_stop_scan.clicked.connect(self.stop_scan)
        self.ui.btn_CTscan_parameter_write.clicked.connect(self.CTscan_parameter_write)



        # after login, write some log
        self.write_start_log()



    # initiallized motor name, to make some button enable or disable
    initiallize_motor_list = []

    # CTscan stop flag
    CTscan_stop_flag = True

    motor_abs_move = {'G1光栅Y平移': 0, '样品台Z平移': 0, '样品台Y旋转': 0, '样品台Y平移': 0,
                     'G1光栅Y旋转': 0, 'G2光栅Z平移': 0, 'G0光栅Z平移': 0, 'G1光栅Z平移': 0,
                     'G0光栅X旋转': 0, 'G0光栅Y旋转': 0, 'G0光栅Z旋转': 0, 'G1光栅X旋转': 0,
                     'G1光栅Z旋转': 0, 'G2光栅X旋转': 0, 'G2光栅Y旋转': 0, 'G2光栅Z旋转': 0}


    def get_motor_name(self):
        """ :return motor name"""
        motorname = self.ui.comboBox_displacement_move_displacement_number.currentText() + \
                    self.ui.comboBox_displacement_move_displacement_comboBox_displacement_move_displacement_axis.currentText() + \
                    self.ui.comboBox_displacement_move_displacement_type.currentText()
        return str(motorname)


#    CT scan
    def start_scan(self):
        with open('conf.json', 'r') as f:
            CTscan_parameter = json.load(f)

        mode = self.ui.comboBox_CTscan_scan_mode.currentText()
        if mode == "Mode_1":
            print(CTscan_parameter)
        elif mode == "Mode_2":
            print("mode2")
        elif mode == "Mode_3":
            print("mode2")
        elif mode == "Mode_4":
            print("mode2")
        elif mode == "Mode_5":
            print("mode2")

    def stop_scan(self):
        self.CTscan_stop_flag = False

    def CTscan_parameter_write(self):
        CTscan_parameter = {
            "G1光栅周期P": 0,  # 周期 P
            "G1光栅步进步数N": 0,  # N - 1 次， 每次步进 P / N
            "样品转台采集次数K": 0,  # 一圈要采集 K 次, 每次动 2π / K
            "样品高度H": 0,
            "样品台轴向步进长度L": 0,
            "样品台轴向步进层数M": 0  # 步数 M = [H / L] 向上取整 ， 每次走L， 样品高度 H
        }
        CTscan_parameter["G1光栅步进步数N"] = self.ui.lineEdit_CTscan_parameter_N.text()
        CTscan_parameter["G1光栅周期P"] = self.ui.lineEdit_CTscan_parameter_P.text()
        CTscan_parameter["样品转台采集次数K"] = self.ui.lineEdit_CTscan_parameter_K.text()
        CTscan_parameter["样品台轴向步进长度L"] = self.ui.lineEdit_CTscan_parameter_L.text()
        CTscan_parameter["样品高度H"] = self.ui.lineEdit_CTscan_parameter_H.text()

        # TODO 参数限制  How to restrict user input in QLineEdit in pyqt
        try:
            H = float(CTscan_parameter["样品高度H"])
            L = float(CTscan_parameter["样品台轴向步进长度L"])
        except ValueError:
            msg = QMessageBox()
            msg.setText("非法值")
            msg.show()

        CTscan_parameter["样品台轴向步进层数M"] = math.ceil(H / L)

        with open('conf.json', 'w') as f:
            json.dump(CTscan_parameter, f)


#    log
    def write_start_log(self):
        ''' after login ,write the login log '''
        currtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        dailylog = "\n" + currtime + " " + "login."
        self.ui.textEdit_log_daily_log.append(dailylog)

    def write_manual_log(self):
        manual_log = self.ui.textEdit_log_manual_record.toPlainText()

        # write log
        currtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        dailylog = currtime + " " + manual_log
        self.ui.textEdit_log_daily_log.append(dailylog)

    def write_daily_log(self):
        """build a file named with the date. log is a string add to the log file"""
        logfilename = time.strftime("%Y-%m-%d", time.localtime()) + ".txt"
        log = self.ui.textEdit_log_daily_log.toPlainText()
        # f = open(logfilename, 'a', encoding='utf-8')
        # f.write(log)
        # f.close()
        with open(logfilename, 'a', encoding='utf-8') as f:
            f.write(log)


#    motor move
    def change_Initiallize_btn(self):
        """ only the motor is not initiallized can be initiallize"""
        motorname = self.get_motor_name()
        if motorname not in self.initiallize_motor_list:
            self.ui.btn_displacement_move_initiallize_motor.setEnabled(True)
            self.ui.btn_displacement_move_start_move.setEnabled(False)
            self.ui.btn_displacement_move_stop_move.setEnabled(False)
        else:
            self.ui.lineEdit_displacement_move_current_displacement.setText(str(self.motor_abs_move[motorname]))

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

        self.ui.lineEdit_displacement_move_current_displacement.setText('0')

        # write log
        currtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        dailylog = currtime + " " + motorname + " has been initialized !"
        self.ui.textEdit_log_daily_log.append(dailylog)

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

        if errorCode != 0:
            displayErrorAndClose(socketId, errorCode, 'GroupMoveAbsolute')
            sys.exit()

        self.motor_abs_move[motorname] = absPosition[0]
        self.ui.lineEdit_displacement_move_current_displacement.setText(str(absPosition[0]))

        # write log
        currtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        dailylog = currtime + " " + motorname + " move absolutely to " + " %f" % (absPosition[0])
        self.ui.textEdit_log_daily_log.append(dailylog)

        self.ui.btn_displacement_move_start_move.setEnabled(True)

        # print(motor_positioner + " move absolute to ",)
        # print(absPosition[0])

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

        if errorCode != 0:
            displayErrorAndClose(socketId, errorCode, 'GroupKill')
            sys.exit()

        # push the kill button will make motor move parameter = 0
        self.motor_abs_move[motorname] = 0

        # write log
        currtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        dailylog = currtime + " " + motorname + " has been killed !"
        self.ui.textEdit_log_daily_log.append(dailylog)

        self.initiallize_motor_list.remove(motorname)
        self.ui.btn_displacement_move_stop_move.setEnabled(False)
        self.ui.btn_displacement_move_initiallize_motor.setEnabled(True)

        print(group + " Group killed ")

    def motor_kill_all(self):

        for motorname in self.initiallize_motor_list:
            if motorname in MotorDict_253.keys():
                group = str(MotorDict_253[motorname][0: 6])
                socketId = socketId_253
            else:
                group = str(MotorDict_254[motorname][0: 6])
                socketId = socketId_254

            # Kill the group
            [errorCode, returnString] = myxps.GroupKill(socketId, group)
            # print (returnString)

            self.initiallize_motor_list.remove(motorname)


        # write log
        currtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        dailylog = currtime + " kill all motor. "
        self.ui.textEdit_log_daily_log.append(dailylog)

    def motor_parameter_upload(self):
        filename = "move_parameter.json"
        with open(filename, 'r') as f:
            self.motor_abs_move = json.load(f)

        self.initiallize_motor_list.clear()

        for motorname in self.motor_abs_move:

            if motorname in MotorDict_253.keys():
                group = str(MotorDict_253[motorname][0: 6])
                motor_positioner = MotorDict_253[motorname]
                socketId = socketId_253
            else:
                group = str(MotorDict_254[motorname][0: 6])
                motor_positioner = MotorDict_254[motorname]
                socketId = socketId_254

            if self.motor_abs_move[motorname] == 0:
                continue

            self.initiallize_motor_list.append(motorname)

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

            absPosition = []
            absPosition.append(float(self.motor_abs_move[motorname]))
            [errorCode, returnString] = myxps.GroupMoveAbsolute(socketId, motor_positioner, absPosition)
            if errorCode != 0:
                displayErrorAndClose(socketId, errorCode, 'GroupMoveAbsolute')
                sys.exit()

            self.ui.lineEdit_displacement_move_current_displacement.setText(str(absPosition[0]))




    def motor_parameter_save_all(self):
        ''' save the motor_abs_move dict in move_parameter.json'''
        filename = "move_parameter.json"
        with open(filename, 'w') as f:
            json.dump(self.motor_abs_move, f)

        # write log
        currtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        dailylog = currtime + " save all parameter. "
        self.ui.textEdit_log_daily_log.append(dailylog)



    def get_picture(self):
        print("get a picture")


if __name__ == '__main__':
    import sys
    from Login import Login

    app = QApplication(sys.argv)
    login = Login()
    if login.exec_() == QDialog.Accepted:
        Motor = Motor()
        Motor.show()
        sys.exit(app.exec_())

