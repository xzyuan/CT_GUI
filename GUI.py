import XPS_Q8_drivers
import sys
import time
import json
import math

# from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QDialog, QMessageBox, QProgressBar
from mainwindow import Ui_MainWindow
from PyQt5.QtCore import *


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

# 两个全局Dict, 分别表示两台xps说控制的电机对应关系
MotorDict_253 = {'G1光栅Y平移': 'Group1.Pos', '样品台Z平移': 'Group2.Pos', '样品台Y旋转': 'Group3.Pos', '样品台Y平移': 'Group4.Pos',
             'G1光栅Y旋转': 'Group5.Pos', 'G2光栅Z平移': 'Group6.Pos', 'G0光栅Z平移': 'Group7.Pos', 'G1光栅Z平移': 'Group8.Pos'}

MotorDict_254 = {'G0光栅X旋转': 'Group3.Pos', 'G0光栅Y旋转': 'Group7.Pos', 'G0光栅Z旋转': 'Group2.Pos', 'G1光栅X旋转': 'Group4.Pos',
             'G1光栅Z旋转': 'Group4.Pos', 'G2光栅X旋转': 'Group5.Pos', 'G2光栅Y旋转': 'Group8.Pos', 'G2光栅Z旋转': 'Group6.Pos'}


class Motor:
    """
    实现电机的各种操作！

    :parameter


    functions:
        initialize：
        move_abs：
        kill：
        kill_all：
        get_motor_position:

    """
    def __init__(self):
        pass





class Thread4Motor(QThread):

    finishOneMotor = pyqtSignal(str)

    motor_stop = False  # 表示电机是否停止

    def __init__(self):
        super().__init__()
        self.mutex = QMutex()


    def run(self):

        filename = "move_parameter.json"
        with open(filename, 'r') as f:
            self.motor_abs_move = json.load(f)

        # self.initiallize_motor_list.clear()
        for motorname in self.motor_abs_move:
            if motorname in MotorDict_253.keys():
                group = str(MotorDict_253[motorname][0: 6])
                motor_positioner = MotorDict_253[motorname]
                socketId = socketId_253
            else:
                group = str(MotorDict_254[motorname][0: 6])
                motor_positioner = MotorDict_254[motorname]
                socketId = socketId_254

            # 当前电机位移参数为0，则跳过
            if self.motor_abs_move[motorname] == 0:
                continue

            # self.initiallize_motor_list.append(motorname)

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


        for motorname in self.motor_abs_move:
            if motorname in MotorDict_253.keys():
                group = str(MotorDict_253[motorname][0: 6])
                motor_positioner = MotorDict_253[motorname]
                socketId = socketId_253
            else:
                group = str(MotorDict_254[motorname][0: 6])
                motor_positioner = MotorDict_254[motorname]
                socketId = socketId_254

            with QMutexLocker(self.mutex):
                # time.sleep(1)
                if self.motor_stop:
                    break

                # 当前电机位移参数为0，则跳过
                if self.motor_abs_move[motorname] == 0:
                    continue

                absPosition = []
                absPosition.append(float(self.motor_abs_move[motorname]))
                [errorCode, returnString] = myxps.GroupMoveAbsolute(socketId, motor_positioner, absPosition)
                if errorCode != 0:
                    displayErrorAndClose(socketId, errorCode, 'GroupMoveAbsolute')
                    sys.exit()


                # 当前电机运行完成发送发送电机名
                self.finishOneMotor.emit(motorname)




    def motor_stop_move(self):

        with QMutexLocker(self.mutex):
            print("thread stop")
            self.motor_stop = True

            for motorname in self.motor_abs_move:
                if motorname in MotorDict_253.keys():
                    group = str(MotorDict_253[motorname][0: 6])
                    motor_positioner = MotorDict_253[motorname]
                    socketId = socketId_253
                else:
                    group = str(MotorDict_254[motorname][0: 6])
                    motor_positioner = MotorDict_254[motorname]
                    socketId = socketId_254

                    # Kill the group
                    [errorCode, returnString] = myxps.GroupKill(socketId, group)
                    # print (returnString)


class GUI(QMainWindow):

    def __init__(self):
        super(Motor, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


        self.system_enable(False)
        self.display_scan_parameter()
        # self.setWindowFlags(self.windowFlags() & ~ (Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint));
        # self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)

        # flags = 0
        # flags |= Qt.FramelessWindowHint
        # flags |= Qt.WindowTitleHint
        # self.setWindowFlags(flags)

        #login
        self.ui.btn_login.clicked.connect(self.login)

        # quit system
        # TODO: maybe need reimplement this function，弹窗确认
        self.ui.btn_quit.clicked.connect(self.quit_all)

        # displacement_move page
        self.ui.btn_displacement_move_start_move.setEnabled(False)
        self.ui.btn_displacement_move_stop_move.setEnabled(False)
        self.ui.btn_displacement_move_initiallize_motor.setEnabled(True)

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
            "样品视场Y方向长度L": 0,
            "样品台轴向步进层数M": 0  # 步数 M = [H / L] 向上取整 ， 每次走L， 样品高度 H
        }
        CTscan_parameter["G1光栅步进步数N"] = self.ui.lineEdit_CTscan_parameter_N.text()
        CTscan_parameter["G1光栅周期P"] = self.ui.lineEdit_CTscan_parameter_P.text()
        CTscan_parameter["样品转台采集次数K"] = self.ui.lineEdit_CTscan_parameter_K.text()
        CTscan_parameter["样品视场Y方向长度L"] = self.ui.lineEdit_CTscan_parameter_L.text()
        CTscan_parameter["样品高度H"] = self.ui.lineEdit_CTscan_parameter_H.text()

        # TODO 参数限制  How to restrict user input in QLineEdit in pyqt
        if not self.scan_parameter_strict(CTscan_parameter):
            return

        H = float(CTscan_parameter["样品高度H"])
        L = float(CTscan_parameter["样品视场Y方向长度L"])
        CTscan_parameter["样品台轴向步进层数M"] = math.ceil(H / L)

        msg = "确认需要写入如下参数：\n" + ''.join('{} = {}\n'.format(key, val) for key, val in CTscan_parameter.items())
        ret = QMessageBox.information(self, "scan", msg, QMessageBox.Yes | QMessageBox.No)

        if ret == QMessageBox.Yes :
            with open('conf.json', 'w') as f:
                json.dump(CTscan_parameter, f)
            # write log
            currtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            dailylog = currtime + " write parameter !\n" + ''.join('{} = {}\n'.format(key, val) for key, val in CTscan_parameter.items())
            self.ui.textEdit_log_daily_log.append(dailylog)
        else:
            return


#    log
    def write_start_log(self):
        ''' after login ,write the login log '''
        currtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        dailylog = "\n" + currtime + " " + "login."
        self.ui.textEdit_log_daily_log.append(dailylog)

    def write_manual_log(self):
        manual_log = "[手动添加日志]" + self.ui.textEdit_log_manual_record.toPlainText()

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


        if motorname not in self.motor_abs_move:  # 如果该电机不存在，则三个按钮全部变灰
            # self.ui.btn_displacement_move_initiallize_motor.setEnabled(False)
            # self.ui.btn_displacement_move_start_move.setEnabled(False)
            # self.ui.btn_displacement_move_stop_move.setEnabled(False)
            QMessageBox.information(self, "motor error", motorname + "电机不存在，请重新选择！", QMessageBox.Cancel)
            return

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

        # 参数检查
        if not self.move_placement_parameter_strict():
            self.ui.btn_displacement_move_start_move.setEnabled(True)
            return

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

        # msg = QMessageBox()
        # msgRet = msg.information(self, "upload", "正在加载参数！", QMessageBox.Cancel)

        # filename = "move_parameter.json"
        # with open(filename, 'r') as f:
        #     self.motor_abs_move = json.load(f)
        #
        # self.initiallize_motor_list.clear()
        #
        # for motorname in self.motor_abs_move:
        #
        #     # if msgRet == msg.Cancel:
        #     #     break
        #     # else:
        #     #     msg.setText("xxxxxx")
        #
        #     if motorname in MotorDict_253.keys():
        #         group = str(MotorDict_253[motorname][0: 6])
        #         motor_positioner = MotorDict_253[motorname]
        #         socketId = socketId_253
        #     else:
        #         group = str(MotorDict_254[motorname][0: 6])
        #         motor_positioner = MotorDict_254[motorname]
        #         socketId = socketId_254
        #
        #     if self.motor_abs_move[motorname] == 0:
        #         continue
        #
        #     self.initiallize_motor_list.append(motorname)
        #
        #     [errorCode, returnString] = myxps.GroupKill(socketId, group)
        #
        #     if errorCode != 0:
        #         displayErrorAndClose(socketId, errorCode, 'GroupKill')
        #         sys.exit()
        #
        #     [errorCode, returnString] = myxps.GroupInitialize(socketId, group)
        #
        #     if errorCode != 0:
        #         displayErrorAndClose(socketId, errorCode, 'GroupInitialize')
        #         sys.exit()
        #
        #     [errorCode, returnString] = myxps.GroupHomeSearch(socketId, group)
        #
        #     if errorCode != 0:
        #         displayErrorAndClose(socketId, errorCode, 'GroupHomeSearch')
        #         sys.exit()
        #
        #     absPosition = []
        #     absPosition.append(float(self.motor_abs_move[motorname]))
        #     [errorCode, returnString] = myxps.GroupMoveAbsolute(socketId, motor_positioner, absPosition)
        #     if errorCode != 0:
        #         displayErrorAndClose(socketId, errorCode, 'GroupMoveAbsolute')
        #         sys.exit()

        #退出前把当前位置更新
        # self.display_motor_position()

        self.motorThread = Thread4Motor()
        if not self.motorThread.isRunning():
            self.motorThread.finishOneMotor.connect(self.motor_parameter_upload_status_display)
            self.motorThread.finished.connect(self.motor_parameter_upload_thread_end)
            # self.ui.btn_displacement_move_upload.setEnabled(False)
            self.ui.btn_displacement_move_upload.setText("停止运行")
            self.motorThread.start()
        else:
            self.motorThread.motor_stop_move()
            self.ui.statusBar.showMessage("停止运行", 1)
            # self.motorThread.terminate()
            # self.motorThread.wait()
            self.ui.btn_displacement_move_upload.setText("上传参数")

            print("tingzhiyunxing")

    def motor_parameter_upload_thread_end(self):
        self.ui.statusBar.clearMessage()
        self.ui.btn_displacement_move_upload.setText("上传参数")

    def motor_parameter_upload_status_display(self, motorname):
        # statusBar = self.ui.statusBar()
        # statusBar.setStatusBar(motorname + "电机已经移动到指定位置")
        self.ui.statusBar.showMessage(motorname + "电机已经移动到指定位置")
        print(motorname)


    def motor_parameter_save_all(self):
        ''' save the motor_abs_move dict in move_parameter.json'''
        filename = "move_parameter.json"
        with open(filename, 'w') as f:
            json.dump(self.motor_abs_move, f)

        # write log
        currtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        dailylog = currtime + " save all parameter. "
        self.ui.textEdit_log_daily_log.append(dailylog)


    def quit_all(self):
        reply = QMessageBox.critical(self, self.tr("退出软件"), "退出CT控制软件？", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return
        else:
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

            # 等待线程结束
            self.motorThread.motor_stop_move()
            self.motorThread.wait()

            # write log
            currtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            dailylog = currtime + " kill all motor and quit system "
            self.ui.textEdit_log_daily_log.append(dailylog)
            # quit
            quit()

    def login(self):
        self.test()
        passwd = self.ui.lineEdit_login_passwd.text()
        username = self.ui.lineEdit_login_username.text()
        if passwd == "nsrl" and username == "CT":
            self.system_enable(True)
            QMessageBox.information(self, "login", "欢迎使用CT控制软件", QMessageBox.Ok)
            self.ui.lineEdit_login_passwd.clear()
            self.ui.lineEdit_login_username.clear()
        else:
            QMessageBox.information(self, "login", "用户名密码不匹配，请重试！", QMessageBox.Cancel)




    def system_enable(self, flag):
        self.ui.tab_2.setEnabled(flag)
        self.ui.tab_3.setEnabled(flag)
        self.ui.tab_4.setEnabled(flag)
        self.ui.tab_5.setEnabled(flag)
        self.ui.tab_6.setEnabled(flag)
        # self.ui.tab_7.setEnabled(flag)
        self.ui.tab_9.setEnabled(flag)
        self.ui.tab.setEnabled(flag)

    def display_scan_parameter(self):
        with open('conf.json', 'r') as f:
            CTscan_parameter = json.load(f)
        self.ui.lineEdit_CTscan_parameter_N.setText(CTscan_parameter["G1光栅步进步数N"])
        self.ui.lineEdit_CTscan_parameter_P.setText(CTscan_parameter["G1光栅周期P"] )
        self.ui.lineEdit_CTscan_parameter_K.setText(CTscan_parameter["样品转台采集次数K"])
        self.ui.lineEdit_CTscan_parameter_L.setText(CTscan_parameter["样品视场Y方向长度L"])
        self.ui.lineEdit_CTscan_parameter_H.setText(CTscan_parameter["样品高度H"])


    def get_picture(self):
        print("get a picture")


    def setMaximizable(self):
        self.setWindowFlags(self.windowFlags() & ~ Qt.WindowMaximizeButtonHint)

    def scan_parameter_strict(self, CTscan_parameter):
        CTscan_strict = {
            "G1光栅周期P": (0, 100),  # 周期 P
            "G1光栅步进步数N": (0, 100),  # N - 1 次， 每次步进 P / N
            "样品转台采集次数K": (0, 100),  # 一圈要采集 K 次, 每次动 2π / K
            "样品高度H": (0, 100),
            "样品视场Y方向长度L": (0.001, 100),
            "样品台轴向步进层数M": 0  # 步数 M = [H / L] 向上取整 ， 每次走L， 样品高度 H
        }

        for x in CTscan_parameter.keys():
            if x == "样品台轴向步进层数M":
                continue
            if not CTscan_strict[x][0] <= float(CTscan_parameter[x]) <= CTscan_strict[x][1]:
                QMessageBox.information(self, "parameter error", x + "参数输入有误，请重新输入", QMessageBox.Cancel)
                return False
        return True


    def move_placement_parameter_strict(self):
        motor_strict = {'G1光栅Y平移': (-10, 10), '样品台Z平移': (-10, 10), '样品台Y旋转': (-10, 10), '样品台Y平移': (-10, 10),
                          'G1光栅Y旋转': (-10, 10), 'G2光栅Z平移': (-10, 10), 'G0光栅Z平移': (-10, 10), 'G1光栅Z平移': (-10, 10),
                          'G0光栅X旋转': (-10, 10), 'G0光栅Y旋转': (-10, 10), 'G0光栅Z旋转': (-10, 10), 'G1光栅X旋转': (-10, 10),
                          'G1光栅Z旋转': (-10, 10), 'G2光栅X旋转': (-10, 10), 'G2光栅Y旋转': (-10, 10), 'G2光栅Z旋转': (-10, 10)}

        motor_name = self.get_motor_name()
        parameter = self.ui.lineEdit_displacement_move_input_displacement.text()
        x = float(parameter)
        if motor_strict[motor_name][0] <= x <= motor_strict[motor_name][1]:
            return True
        else:
            QMessageBox.information(self, "parameter error", motor_name + "参数输入有误，请重新输入", QMessageBox.Cancel)
            self.ui.lineEdit_displacement_move_input_displacement.clear()
            return False

    def display_motor_position(self):
        pass

    def test(self):
        pass
        # import time
        # self.setStatusTip("hahahha")
        # msg = QMessageBox()
        # msgRet = msg.information(self, "upload", "正在加载参数！", QMessageBox.Cancel)
        # for x in range(10):
        #     if msgRet == msg.Cancel:
        #         break
        #     else:
        #         msg.setText(str(x) + "xxx")
        #         time.sleep(1)
        # pro = QProgressBar(self)
        # pro.setMinimum(0)
        # pro.setMaximum(10)
        # for x in range(11):
        #     pro.setValue(x)
        #     time.sleep(1)
        # dlg = QDialog()
        # pro = QProgressBar(dlg)
        # pro.setMinimum(0)
        # pro.setMaximum(10)
        # dlg.show()
        # for x in range(11):
        #     pro.setValue(x)
        #     time.sleep(1)




if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    gui = GUI()
    gui.show()
    sys.exit(app.exec_())

