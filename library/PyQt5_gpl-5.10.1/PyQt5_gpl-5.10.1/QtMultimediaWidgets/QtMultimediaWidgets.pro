TEMPLATE = lib
CONFIG += warn_on exceptions_off plugin plugin_bundle
QT += multimediawidgets multimedia
CONFIG += release
CONFIG -= android_install
TARGET = QtMultimediaWidgets

win32 {
    PY_MODULE = QtMultimediaWidgets.pyd
    PY_MODULE_SRC = $(DESTDIR_TARGET)
} else {
    PY_MODULE = QtMultimediaWidgets.so

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
HEADERS = sipAPIQtMultimediaWidgets.h
SOURCES = sipQtMultimediaWidgetsQCameraViewfinder.cpp sipQtMultimediaWidgetsQGraphicsVideoItem.cpp sipQtMultimediaWidgetsQVideoWidget.cpp sipQtMultimediaWidgetscmodule.cpp
