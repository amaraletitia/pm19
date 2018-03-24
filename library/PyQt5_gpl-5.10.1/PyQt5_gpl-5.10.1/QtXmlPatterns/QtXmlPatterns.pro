TEMPLATE = lib
CONFIG += warn_on exceptions_off plugin plugin_bundle
QT -= gui
QT += xmlpatterns network
CONFIG += release
CONFIG -= android_install
TARGET = QtXmlPatterns

win32 {
    PY_MODULE = QtXmlPatterns.pyd
    PY_MODULE_SRC = $(DESTDIR_TARGET)
} else {
    PY_MODULE = QtXmlPatterns.so

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
HEADERS = sipAPIQtXmlPatterns.h
SOURCES = sipQtXmlPatternsQAbstractMessageHandler.cpp sipQtXmlPatternsQAbstractUriResolver.cpp sipQtXmlPatternsQAbstractXmlNodeModel.cpp sipQtXmlPatternsQAbstractXmlReceiver.cpp sipQtXmlPatternsQSimpleXmlNodeModel.cpp sipQtXmlPatternsQSourceLocation.cpp sipQtXmlPatternsQVector0100QXmlName.cpp sipQtXmlPatternsQVector0100QXmlNodeModelIndex.cpp sipQtXmlPatternsQXmlFormatter.cpp sipQtXmlPatternsQXmlItem.cpp sipQtXmlPatternsQXmlName.cpp sipQtXmlPatternsQXmlNamePool.cpp sipQtXmlPatternsQXmlNodeModelIndex.cpp sipQtXmlPatternsQXmlQuery.cpp sipQtXmlPatternsQXmlResultItems.cpp sipQtXmlPatternsQXmlSchema.cpp sipQtXmlPatternsQXmlSchemaValidator.cpp sipQtXmlPatternsQXmlSerializer.cpp sipQtXmlPatternscmodule.cpp
