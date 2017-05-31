import sys
import time
import json
import math

# from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from mainwindow import Ui_MainWindow
from PyQt5.QtCore import *
from Motor import Motor

class Thread4Motor(QThread):

    finishOneMotor = pyqtSignal(str)
    # motor_stop = False  # 表示电机是否停止
    motor = Motor()

    def __init__(self):
        super().__init__()
        self.mutex = QMutex()
        self.motor_stop = False

    def run(self):
        self.motor_stop = False
        filename = "move_parameter.json"
        with open(filename, 'r') as f:
            self.motor_abs_move = json.load(f)

        for motorname in self.motor_abs_move:
            # 当前电机位移参数为0，则跳过
            if self.motor_abs_move[motorname] == 0:
                continue
            self.motor.initiallize_single(motorname)

            with QMutexLocker(self.mutex):
                if self.motor_stop:
                    break

            absPosition = float(self.motor_abs_move[motorname])
            self.motor.move_abs(motorname, absPosition)
            print(motorname + str(absPosition))
            # 当前电机运行完成发送发送电机名
            self.finishOneMotor.emit(motorname)

    def motor_stop_move(self):
        with QMutexLocker(self.mutex):
            print("thread stop")
            self.motor_stop = True


class GUI(QMainWindow):

    motor = Motor()

    # CTscan stop flag
    CTscan_stop_flag = True

    # 所有电机位置
    motor_abs_move = {'G1光栅Y平移': 0, '样品台Z平移': 0, '样品台Y旋转': 0, '样品台Y平移': 0,
                     'G1光栅Y旋转': 0, 'G2光栅Z平移': 0, 'G0光栅Z平移': 0, 'G1光栅Z平移': 0,
                     'G0光栅X旋转': 0, 'G0光栅Y旋转': 0, 'G0光栅Z旋转': 0, 'G1光栅X旋转': 0,
                     'G1光栅Z旋转': 0, 'G2光栅X旋转': 0, 'G2光栅Y旋转': 0, 'G2光栅Z旋转': 0}

    def __init__(self):
        super(GUI, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.motorThread = Thread4Motor()

        self.system_enable(False)
        self.display_scan_parameter()

        # 以下代码可以去掉最大化，最小化，关闭按钮
        # flags = 0
        # flags |= Qt.FramelessWindowHint
        # flags |= Qt.WindowTitleHint
        # self.setWindowFlags(flags)

        #login
        self.ui.btn_login.clicked.connect(self.login)

        # quit system
        self.ui.btn_quit.clicked.connect(self.quit_all)

        # displacement_move page
        self.ui.btn_displacement_move_initiallize_motor.clicked.connect(self.motor_initiallize)
        self.ui.btn_displacement_move_start_move.clicked.connect(self.motor_start_move)
        self.ui.btn_displacement_move_stop_move.clicked.connect(self.motor_stop_move)
        self.ui.btn_displacement_move_kill_all.clicked.connect(self.motor_kill_all)
        self.ui.btn_displacement_move_upload.clicked.connect(self.motor_parameter_upload)
        self.ui.btn_displacement_move_save_all.clicked.connect(self.motor_parameter_save_all)

        self.ui.comboBox_displacement_move_displacement_number.currentIndexChanged.connect(self.change_Initiallize_btn)
        self.ui.comboBox_displacement_move_displacement_comboBox_displacement_move_displacement_axis.currentIndexChanged.connect(self.change_Initiallize_btn)
        self.ui.comboBox_displacement_move_displacement_type.currentIndexChanged.connect(self.change_Initiallize_btn)

        self.ui.btn_displacement_move_start_move.setEnabled(False)
        self.ui.btn_displacement_move_stop_move.setEnabled(False)
        self.ui.btn_displacement_move_initiallize_motor.setEnabled(True)
        
        # log
        self.ui.btn_log_write.clicked.connect(self.write_manual_log)
        self.ui.textEdit_log_daily_log.textChanged.connect(self.write_daily_log)

        # scanning
        self.ui.btn_CTscan_start_scan.clicked.connect(self.start_scan)
        self.ui.btn_CTscan_stop_scan.clicked.connect(self.stop_scan)
        self.ui.btn_CTscan_parameter_write.clicked.connect(self.CTscan_parameter_write)

        # doc  https://htmlg.com/html-editor/
        self.display_doc()


    def get_motor_name(self):
        """ 获取电机名 """
        motorname = self.ui.comboBox_displacement_move_displacement_number.currentText() + \
                    self.ui.comboBox_displacement_move_displacement_comboBox_displacement_move_displacement_axis.currentText() + \
                    self.ui.comboBox_displacement_move_displacement_type.currentText()
        return str(motorname)

#     doc
    def display_doc(self):
        self.ui.textBrowser_doc.setSource(QUrl("./doc.html"))

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
        CTscan_parameter["G1光栅步进步数N"] = float(self.ui.lineEdit_CTscan_parameter_N.text())
        CTscan_parameter["G1光栅周期P"] = float(self.ui.lineEdit_CTscan_parameter_P.text())
        CTscan_parameter["样品转台采集次数K"] = float(self.ui.lineEdit_CTscan_parameter_K.text())
        CTscan_parameter["样品视场Y方向长度L"] = float(self.ui.lineEdit_CTscan_parameter_L.text())
        CTscan_parameter["样品高度H"] = float(self.ui.lineEdit_CTscan_parameter_H.text())

        # 参数限制
        if not self.scan_parameter_restrict(CTscan_parameter):
            return
        H = float(CTscan_parameter["样品高度H"])
        L = float(CTscan_parameter["样品视场Y方向长度L"])
        CTscan_parameter["样品台轴向步进层数M"] = math.ceil(H / L)

        msg = "确认需要写入如下参数：\n" + ''.join('{} = {}\n'.format(key, val) for key, val in CTscan_parameter.items())
        ret = QMessageBox.information(self, "scan", msg, QMessageBox.Yes | QMessageBox.No)

        if ret == QMessageBox.Yes:
            with open('conf.json', 'w') as f:
                json.dump(CTscan_parameter, f)
            # write log
            dailylog = " write parameter !\n" + ''.join('{} = {}\n'.format(key, val) for key, val in CTscan_parameter.items())
            dailylog += "\n"
            self.write_log(dailylog)
        else:
            return


#    log


#   log
    def write_log(self, strlog):
        """
        写日志
        :param strlog:日志内容
        :return:
        """
        currtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        dailylog = "\n" + currtime + " " + strlog
        self.ui.textEdit_log_daily_log.append(dailylog)

    def write_manual_log(self):
        manual_log = "[手动添加日志]" + self.ui.textEdit_log_manual_record.toPlainText()
        self.write_log(manual_log)

    def write_daily_log(self):
        """
        将日志写入文件，文件名以日期命名
        :return:
        """
        logfilename = time.strftime("%Y-%m-%d", time.localtime()) + ".txt"
        log = self.ui.textEdit_log_daily_log.toPlainText()
        with open(logfilename, 'a', encoding='utf-8') as f:
            f.write(log)

#    motor move

#   single move
    def change_Initiallize_btn(self):
        """ 没有初始化的电机，可以被初始化 """
        motorname = self.get_motor_name()
        if motorname not in self.motor_abs_move:  # 如果该电机不存在
            QMessageBox.information(self, "motor error", motorname + "电机不存在，请重新选择！", QMessageBox.Cancel)
            return
        if motorname not in self.motor.initiallize_motor_list:
            self.ui.btn_displacement_move_initiallize_motor.setEnabled(True)
            self.ui.btn_displacement_move_start_move.setEnabled(False)
            self.ui.btn_displacement_move_stop_move.setEnabled(False)
        else:
            # TODO display_motor_position()
            self.ui.lineEdit_displacement_move_current_displacement.setText(str(self.motor_abs_move[motorname]))
            self.ui.btn_displacement_move_initiallize_motor.setEnabled(False)
            self.ui.btn_displacement_move_start_move.setEnabled(True)
            self.ui.btn_displacement_move_stop_move.setEnabled(True)
            self.display_motor_position(motorname)

    def display_motor_position(self, motorname):
        if motorname not in self.motor_abs_move.keys():
            self.ui.lineEdit_displacement_move_current_displacement.setText(str(0))
            return

        pos = self.motor.get_position(motorname)
        self.motor_abs_move[motorname] = pos
        curr_motorname = self.get_motor_name()
        pos = self.motor.get_position(curr_motorname)
        self.motor_abs_move[curr_motorname] = pos
        self.ui.lineEdit_displacement_move_current_displacement.setText(str(pos))

    def motor_initiallize(self):
        motorname = self.get_motor_name()
        if motorname not in self.motor_abs_move:  # 如果该电机不存在
            QMessageBox.information(self, "motor error", motorname + "电机不存在，请重新选择！", QMessageBox.Cancel)
            return

        self.motor.initiallize_single(motorname)
        self.display_motor_position(motorname)

        # write log
        dailylog = " " + motorname + " has been initialized !"
        self.write_log(dailylog)

        self.ui.btn_displacement_move_start_move.setEnabled(True)
        self.ui.btn_displacement_move_stop_move.setEnabled(True)
        self.ui.btn_displacement_move_initiallize_motor.setEnabled(False)

    def motor_start_move(self):
        self.ui.btn_displacement_move_start_move.setEnabled(False)
        self.ui.btn_displacement_move_stop_move.setEnabled(True)

        motorname = self.get_motor_name()

        # 参数检查
        if not self.move_placement_parameter_restrict():
            self.ui.btn_displacement_move_start_move.setEnabled(True)
            return

        absPosition = float(self.ui.lineEdit_displacement_move_input_displacement.text())
        self.motor.move_abs(motorname, absPosition)

        self.motor_abs_move[motorname] = absPosition
        self.display_motor_position(motorname)

        # write log
        dailylog = " " + motorname + " move absolutely to " + " %f" % absPosition
        self.write_log(dailylog)
        self.ui.btn_displacement_move_start_move.setEnabled(True)

    def motor_stop_move(self):
        self.ui.btn_displacement_move_start_move.setEnabled(False)

        motorname = self.get_motor_name()
        self.motor.kill(motorname)

        # write log
        dailylog = " " + motorname + " has been killed !"
        self.write_log(dailylog)

        self.ui.btn_displacement_move_stop_move.setEnabled(False)
        self.ui.btn_displacement_move_initiallize_motor.setEnabled(True)

    def motor_kill_all(self):
        self.motor.kill_all()
        # write log
        dailylog = " kill all motor. "
        self.write_log(dailylog)
        self.change_Initiallize_btn()


    def motor_parameter_upload(self):
        if not self.motorThread.isRunning():
            self.motorThread.finishOneMotor.connect(self.motor_parameter_upload_status_display)
            self.motorThread.finished.connect(self.motor_parameter_upload_thread_end)
            self.ui.btn_displacement_move_upload.setText("停止运行")
            self.motorThread.start()
        else:
            self.motorThread.motor_stop_move()
            self.ui.statusBar.showMessage("停止运行", 1)
            self.ui.btn_displacement_move_upload.setText("上传参数")

    def motor_parameter_upload_thread_end(self):
        motorname = self.get_motor_name()
        self.display_motor_position(motorname)
        self.ui.statusBar.clearMessage()
        self.ui.btn_displacement_move_upload.setText("上传参数")

    def motor_parameter_upload_status_display(self, motorname):
        # statusBar = self.ui.statusBar()
        # statusBar.setStatusBar(motorname + "电机已经移动到指定位置")
        self.ui.statusBar.showMessage(motorname + "电机已经移动到指定位置")
        print(motorname)

    def motor_parameter_save_all(self):
        ''' 保存当前电机运行的所有位置 '''
        # TODO ：扫描时需要将扫描结束的电机清零
        filename = "move_parameter.json"
        with open(filename, 'w') as f:
            json.dump(self.motor_abs_move, f)

        # write log
        dailylog = " save all parameter. "
        self.write_log(dailylog)

#    login and quit
    def quit_all(self):
        reply = QMessageBox.critical(self, self.tr("退出软件"), "退出CT控制软件？", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return
        else:
            self.motor.kill_all()

            # 等待线程结束
            # self.motorThread.motor_stop_move()
            # self.motorThread.wait()

            # write log
            dailylog = " kill all motor and quit system "
            self.write_log(dailylog)
            # quit
            # TODO 重写退出事件
            quit()

    def login(self):
        passwd = self.ui.lineEdit_login_passwd.text()
        username = self.ui.lineEdit_login_username.text()
        if passwd == "nsrl" and username == "CT":
            self.system_enable(True)
            QMessageBox.information(self, "login", "欢迎使用CT控制软件", QMessageBox.Ok)
            self.ui.lineEdit_login_passwd.clear()
            self.ui.lineEdit_login_username.clear()
            log = username + "login\n"
            self.write_log(log)
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
        self.ui.lineEdit_CTscan_parameter_N.setText(str(CTscan_parameter["G1光栅步进步数N"]))
        self.ui.lineEdit_CTscan_parameter_P.setText(str(CTscan_parameter["G1光栅周期P"]))
        self.ui.lineEdit_CTscan_parameter_K.setText(str(CTscan_parameter["样品转台采集次数K"]))
        self.ui.lineEdit_CTscan_parameter_L.setText(str(CTscan_parameter["样品视场Y方向长度L"]))
        self.ui.lineEdit_CTscan_parameter_H.setText(str(CTscan_parameter["样品高度H"]))

    def scan_parameter_restrict(self, CTscan_parameter):
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

    def move_placement_parameter_restrict(self):
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

