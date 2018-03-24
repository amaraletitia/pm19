TEMPLATE = lib
CONFIG += warn_on exceptions_off plugin plugin_bundle
QT += bluetooth
CONFIG += release
CONFIG -= android_install
TARGET = QtBluetooth

win32 {
    PY_MODULE = QtBluetooth.pyd
    PY_MODULE_SRC = $(DESTDIR_TARGET)
} else {
    PY_MODULE = QtBluetooth.so

    macx {
        PY_MODULE_SRC = $(TARGET).plugin/Contents/MacOS/$(TARGET)

        QMAKE_LFLAGS += "-undefined dynamic_lookup"

        equals(QT_MINOR_VERSION, 5) {
            QMAKE_RPATHDIR += $$[QT_INSTALL_LIBS]
        }
    } else {
        PY_MODULE_SRC = $(TARGET)
    }
}

QMAKE_POST_LINK = $(COPY_FILE) $$PY_MODULE_SRC $$PY_MODULE

target.CONFIG = no_check_exist
target.files = $$PY_MODULE

target.path = /Users/GYUNAM/.pyenv/versions/3.4.5/lib/python3.4/site-packages/PyQt5
INSTALLS += target
DEFINES += SIP_PROTECTED_IS_PUBLIC protected=public
INCLUDEPATH += .
INCLUDEPATH += /Users/GYUNAM/.pyenv/versions/3.4.5/include/python3.4m
win32 {
    LIBS += -L
}
HEADERS = sipAPIQtBluetooth.h
SOURCES = sipQtBluetoothQBluetooth.cpp sipQtBluetoothQBluetoothAddress.cpp sipQtBluetoothQBluetoothDeviceDiscoveryAgent.cpp sipQtBluetoothQBluetoothDeviceInfo.cpp sipQtBluetoothQBluetoothDeviceInfoCoreConfigurations.cpp sipQtBluetoothQBluetoothDeviceInfoServiceClasses.cpp sipQtBluetoothQBluetoothHostInfo.cpp sipQtBluetoothQBluetoothLocalDevice.cpp sipQtBluetoothQBluetoothSecurityFlags.cpp sipQtBluetoothQBluetoothServer.cpp sipQtBluetoothQBluetoothServiceDiscoveryAgent.cpp sipQtBluetoothQBluetoothServiceInfo.cpp sipQtBluetoothQBluetoothServiceInfoSequence.cpp sipQtBluetoothQBluetoothSocket.cpp sipQtBluetoothQBluetoothTransferManager.cpp sipQtBluetoothQBluetoothTransferReply.cpp sipQtBluetoothQBluetoothTransferRequest.cpp sipQtBluetoothQBluetoothUuid.cpp sipQtBluetoothQList0100QBluetoothAddress.cpp sipQtBluetoothQList0100QBluetoothDeviceInfo.cpp sipQtBluetoothQList0100QBluetoothHostInfo.cpp sipQtBluetoothQList0100QBluetoothServiceInfo.cpp sipQtBluetoothQList0100QBluetoothUuid.cpp sipQtBluetoothQList0100QLowEnergyCharacteristic.cpp sipQtBluetoothQList0100QLowEnergyDescriptor.cpp sipQtBluetoothQList1600.cpp sipQtBluetoothQLowEnergyCharacteristic.cpp sipQtBluetoothQLowEnergyCharacteristicPropertyTypes.cpp sipQtBluetoothQLowEnergyController.cpp sipQtBluetoothQLowEnergyDescriptor.cpp sipQtBluetoothQLowEnergyService.cpp sipQtBluetoothQLowEnergyServiceServiceTypes.cpp sipQtBluetoothcmodule.cpp sipQtBluetoothquint128.cpp
