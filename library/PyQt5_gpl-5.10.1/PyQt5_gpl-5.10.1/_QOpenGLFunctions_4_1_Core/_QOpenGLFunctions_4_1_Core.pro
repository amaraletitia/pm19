TEMPLATE = lib
CONFIG += warn_on exceptions_off plugin plugin_bundle
CONFIG += release
CONFIG -= android_install
TARGET = _QOpenGLFunctions_4_1_Core

win32 {
    PY_MODULE = _QOpenGLFunctions_4_1_Core.pyd
    PY_MODULE_SRC = $(DESTDIR_TARGET)
} else {
    PY_MODULE = _QOpenGLFunctions_4_1_Core.so

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
HEADERS = sipAPI_QOpenGLFunctions_4_1_Core.h
SOURCES = sip_QOpenGLFunctions_4_1_CoreQOpenGLFunctions_4_1_Core.cpp sip_QOpenGLFunctions_4_1_Corecmodule.cpp
