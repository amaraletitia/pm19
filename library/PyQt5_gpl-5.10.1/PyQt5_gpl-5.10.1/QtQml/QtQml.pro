TEMPLATE = lib
CONFIG += warn_on exceptions_off plugin plugin_bundle
QT += qml
CONFIG += release
CONFIG -= android_install
TARGET = QtQml

win32 {
    PY_MODULE = QtQml.pyd
    PY_MODULE_SRC = $(DESTDIR_TARGET)
} else {
    PY_MODULE = QtQml.so

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
DEFINES += Py_LIMITED_API=0x03040000
INCLUDEPATH += ../qpy/QtQml
HEADERS = sipAPIQtQml.h ../qpy/QtQml/qpyqml_api.h ../qpy/QtQml/qpyqml_listdata.h ../qpy/QtQml/qpyqmllistproperty.h ../qpy/QtQml/qpyqmllistpropertywrapper.h ../qpy/QtQml/qpyqmlobject.h ../qpy/QtQml/qpyqmlsingletonobject.h
SOURCES = sipQtQmlQJSEngine.cpp sipQtQmlQJSEngineExtensions.cpp sipQtQmlQJSValue.cpp sipQtQmlQJSValueIterator.cpp sipQtQmlQList0100QJSValue.cpp sipQtQmlQList0100QQmlError.cpp sipQtQmlQList0100QQmlProperty.cpp sipQtQmlQQmlAbstractUrlInterceptor.cpp sipQtQmlQQmlApplicationEngine.cpp sipQtQmlQQmlComponent.cpp sipQtQmlQQmlContext.cpp sipQtQmlQQmlEngine.cpp sipQtQmlQQmlError.cpp sipQtQmlQQmlExpression.cpp sipQtQmlQQmlExtensionPlugin.cpp sipQtQmlQQmlFileSelector.cpp sipQtQmlQQmlImageProviderBase.cpp sipQtQmlQQmlImageProviderBaseFlags.cpp sipQtQmlQQmlIncubationController.cpp sipQtQmlQQmlIncubator.cpp sipQtQmlQQmlListProperty0100QObject.cpp sipQtQmlQQmlListReference.cpp sipQtQmlQQmlNetworkAccessManagerFactory.cpp sipQtQmlQQmlParserStatus.cpp sipQtQmlQQmlProperty.cpp sipQtQmlQQmlPropertyMap.cpp sipQtQmlQQmlPropertyValueSource.cpp sipQtQmlQQmlScriptString.cpp sipQtQmlcmodule.cpp ../qpy/QtQml/qpyqml_listdata.cpp ../qpy/QtQml/qpyqml_post_init.cpp ../qpy/QtQml/qpyqml_qjsvalue.cpp ../qpy/QtQml/qpyqml_register_singleton_type.cpp ../qpy/QtQml/qpyqml_register_type.cpp ../qpy/QtQml/qpyqmllistproperty.cpp ../qpy/QtQml/qpyqmllistpropertywrapper.cpp ../qpy/QtQml/qpyqmlobject.cpp ../qpy/QtQml/qpyqmlsingletonobject.cpp
