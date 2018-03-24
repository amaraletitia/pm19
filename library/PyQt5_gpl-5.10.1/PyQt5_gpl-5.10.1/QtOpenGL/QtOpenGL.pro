TEMPLATE = lib
CONFIG += warn_on exceptions_off plugin plugin_bundle
QT += opengl
CONFIG += release
CONFIG -= android_install
TARGET = QtOpenGL

win32 {
    PY_MODULE = QtOpenGL.pyd
    PY_MODULE_SRC = $(DESTDIR_TARGET)
} else {
    PY_MODULE = QtOpenGL.so

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
HEADERS = sipAPIQtOpenGL.h
SOURCES = sipQtOpenGLQGL.cpp sipQtOpenGLQGLContext.cpp sipQtOpenGLQGLContextBindOptions.cpp sipQtOpenGLQGLFormat.cpp sipQtOpenGLQGLFormatOpenGLVersionFlags.cpp sipQtOpenGLQGLFormatOptions.cpp sipQtOpenGLQGLWidget.cpp sipQtOpenGLcmodule.cpp
