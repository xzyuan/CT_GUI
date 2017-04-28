# --------- Python program: XPS controller demonstration --------
import XPS_Q8_drivers
import sys
import time

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
socketId = myxps.TCP_ConnectToServer('192.168.0.253', 5001, 20) # Check connection passed
if (socketId == -1):
    print ('Connection to XPS failed, check IP & Port')
    sys.exit ()
# Add here your personal codes, below for example:

# print "work"


# Define the positioner
# group = 'Group7'
# positioner = group + '.Pos'

Motor = {'Group1': 'Group1.Pos', 'Group2': 'Group2.Pos', 'Group3': 'Group3.Pos', 'Group4': 'Group4.Pos',
         'Group5': 'Group5.Pos', 'Group6': 'Group6.Pos', 'Group7': 'Group7.Pos', 'Group8': 'Group8.Pos'}



# except group1
def initiallizeAllMotor():
    for motor in range(2, 9, 1):
        group = 'Group' + str(motor)

        # positioner = group + '.Pos'
        # Kill the group
        [errorCode, returnString] = myxps.GroupKill(socketId, group)
        # print returnString
        if (errorCode != 0):
            displayErrorAndClose(socketId, errorCode, 'GroupKill')
            sys.exit()
        # Initialize the group
        [errorCode, returnString] = myxps.GroupInitialize(socketId, group)
        # print returnString
        if (errorCode != 0):
            displayErrorAndClose(socketId, errorCode, 'GroupInitialize')
            sys.exit()
        # Home search
        [errorCode, returnString] = myxps.GroupHomeSearch(socketId, group)
        # print returnString
        if (errorCode != 0):
            displayErrorAndClose(socketId, errorCode, 'GroupHomeSearch')
            sys.exit()

        print (group + " has been initialized !")


# except group1
def killAllMotor():
    for motor in range(2, 9, 1):
        group = 'Group' + str(motor)
        # positioner = group + '.Pos'

        # Kill the group
        [errorCode, returnString] = myxps.GroupKill(socketId, group)
        print (returnString)
        if (errorCode != 0):
            displayErrorAndClose(socketId, errorCode, 'GroupKill')
            sys.exit()


def mototMoveAbsolute(motorNumber, absPosition):

    group = 'Group' + str(motorNumber)
    positioner = group + '.Pos'

    [errorCode, returnString] = myxps.GroupMoveAbsolute(socketId, positioner, absPosition)
    # print returnString

    if (errorCode != 0):
        displayErrorAndClose (socketId, errorCode, 'GroupMoveAbsolute')
        sys.exit ()


def motorJogMove(motorNumber, velocity, acceleration, runtime):

    group = 'Group' + str(motorNumber)
    positioner = group + '.Pos'

    # enable Jog mode
    [errorCode, returnString] = myxps.GroupJogModeEnable(socketId, group)
    # print returnString
    if (errorCode != 0):
        displayErrorAndClose(socketId, errorCode, 'GroupJogModeEnable')
        sys.exit()

    [errorCode, returnString] = myxps.GroupJogParametersSet(socketId, positioner, velocity, acceleration)
    # print returnString
    time.sleep(int(runtime))


# Test
if __name__ == '__main__':

    #except 1
    initiallizeAllMotor()
    print ('Move Absolute')

    try:
        while True:
            motorNumber = input('input MotorNumber(1 - 9): ')
            if motorNumber not in ('123456789'):
                break
            position = []
            position.append( float(input('input Position: ')) )
            mototMoveAbsolute(motorNumber, position)
    finally:
        print ('kill all & close socket')
        killAllMotor()
        myxps.TCP_CloseSocket(socketId)





# try:
#
#     [errorCode, returnString] = myxps.GroupJogModeEnable(socketId, group)
#     if (errorCode != 0):
#         displayErrorAndClose(socketId, errorCode, 'GroupJogModeEnable')
#         sys.exit()
#
#     while True:
#         v = raw_input("input velocity: ")
#         if v == '33':
#             break
#         velovity = []
#         velovity.append(v)
#
#         [errorCode, returnString] = myxps.GroupJogParametersSet(socketId, positioner, velovity, [30.0])
#         [erroCode, returnString] = myxps.GroupSpinParametersSet(socketId, positioner, velovity, [10.0, 10.0])
        # print returnString
        # time.sleep(4)
        #
        # Make some moves
        # for index in range(10):
        # Forward
        # pos = raw_input("input position: ")
        # position = []
        # position.append(pos)
        # [errorCode, returnString] = myxps.GroupMoveAbsolute(socketId, positioner, position)
        # if (errorCode != 0):
        #     displayErrorAndClose (socketId, errorCode, 'GroupMoveAbsolute')
        #     sys.exit ()

        # Get current position
        # [errorCode, currentPosition] = myxps.GroupPositionCurrentGet(socketId, positioner, 1)
        # if (errorCode != 0):
        #     displayErrorAndClose (socketId, errorCode, 'GroupPositionCurrentGet')
        #     sys.exit()
        # else:
        #     print 'Positioner ' + positioner + ' is in position ' + str(currentPosition)


# except:
#     print 'disable jog mod & close socket'
#     erroCode = myxps.GroupJogModeDisable(socketId, positioner)
#     myxps.TCP_CloseSocket(socketId)



# Backward
# [errorCode, returnString] = myxps.GroupMoveAbsolute(socketId, positioner, [-20.0])
# if (errorCode != 0):
#     displayErrorAndClose (socketId, errorCode, 'GroupMoveAbsolute')
#     sys.exit ()


# Get current position
# [errorCode, currentPosition] = myxps.GroupPositionCurrentGet(socketId, positioner, 1)
# if (errorCode != 0):
#     displayErrorAndClose (socketId, errorCode, 'GroupPositionCurrentGet')
#     sys.exit()
# else:
#     print 'Positioner ' + positioner + ' is in position ' + str(currentPosition)


# Close connection
# myxps.TCP_CloseSocket(socketId)
#----------- End of the demo program ----------#