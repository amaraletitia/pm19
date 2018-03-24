TEMPLATE = lib
CONFIG += warn_on exceptions_off plugin plugin_bundle
QT += positioning
CONFIG += release
CONFIG -= android_install
TARGET = QtPositioning

win32 {
    PY_MODULE = QtPositioning.pyd
    PY_MODULE_SRC = $(DESTDIR_TARGET)
} else {
    PY_MODULE = QtPositioning.so

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
HEADERS = sipAPIQtPositioning.h
SOURCES = sipQtPositioningQGeoAddress.cpp sipQtPositioningQGeoAreaMonitorInfo.cpp sipQtPositioningQGeoAreaMonitorSource.cpp sipQtPositioningQGeoAreaMonitorSourceAreaMonitorFeatures.cpp sipQtPositioningQGeoCircle.cpp sipQtPositioningQGeoCoordinate.cpp sipQtPositioningQGeoLocation.cpp sipQtPositioningQGeoPositionInfo.cpp sipQtPositioningQGeoPositionInfoSource.cpp sipQtPositioningQGeoPositionInfoSourcePositioningMethods.cpp sipQtPositioningQGeoRectangle.cpp sipQtPositioningQGeoSatelliteInfo.cpp sipQtPositioningQGeoSatelliteInfoSource.cpp sipQtPositioningQGeoShape.cpp sipQtPositioningQList0100QGeoAreaMonitorInfo.cpp sipQtPositioningQList0100QGeoCoordinate.cpp sipQtPositioningQList0100QGeoSatelliteInfo.cpp sipQtPositioningQNmeaPositionInfoSource.cpp sipQtPositioningcmodule.cpp
