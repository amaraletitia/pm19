TEMPLATE = lib
CONFIG += warn_on exceptions_off plugin plugin_bundle
QT += designer
CONFIG += release
CONFIG -= android_install
TARGET = QtDesigner

win32 {
    PY_MODULE = QtDesigner.pyd
    PY_MODULE_SRC = $(DESTDIR_TARGET)
} else {
    PY_MODULE = QtDesigner.so

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
INCLUDEPATH += ../qpy/QtDesigner
HEADERS = sipAPIQtDesigner.h ../qpy/QtDesigner/qpydesignercontainerextension.h ../qpy/QtDesigner/qpydesignercustomwidgetcollectionplugin.h ../qpy/QtDesigner/qpydesignercustomwidgetplugin.h ../qpy/QtDesigner/qpydesignermembersheetextension.h ../qpy/QtDesigner/qpydesignerpropertysheetextension.h ../qpy/QtDesigner/qpydesignertaskmenuextension.h
SOURCES = sipQtDesignerQAbstractExtensionFactory.cpp sipQtDesignerQAbstractExtensionManager.cpp sipQtDesignerQAbstractFormBuilder.cpp sipQtDesignerQDesignerActionEditorInterface.cpp sipQtDesignerQDesignerContainerExtension.cpp sipQtDesignerQDesignerCustomWidgetCollectionInterface.cpp sipQtDesignerQDesignerCustomWidgetInterface.cpp sipQtDesignerQDesignerFormEditorInterface.cpp sipQtDesignerQDesignerFormWindowCursorInterface.cpp sipQtDesignerQDesignerFormWindowInterface.cpp sipQtDesignerQDesignerFormWindowInterfaceFeature.cpp sipQtDesignerQDesignerFormWindowManagerInterface.cpp sipQtDesignerQDesignerMemberSheetExtension.cpp sipQtDesignerQDesignerObjectInspectorInterface.cpp sipQtDesignerQDesignerPropertyEditorInterface.cpp sipQtDesignerQDesignerPropertySheetExtension.cpp sipQtDesignerQDesignerTaskMenuExtension.cpp sipQtDesignerQDesignerWidgetBoxInterface.cpp sipQtDesignerQExtensionFactory.cpp sipQtDesignerQExtensionManager.cpp sipQtDesignerQFormBuilder.cpp sipQtDesignerQList0101QDesignerCustomWidgetInterface.cpp sipQtDesignerQPyDesignerContainerExtension.cpp sipQtDesignerQPyDesignerCustomWidgetCollectionPlugin.cpp sipQtDesignerQPyDesignerCustomWidgetPlugin.cpp sipQtDesignerQPyDesignerMemberSheetExtension.cpp sipQtDesignerQPyDesignerPropertySheetExtension.cpp sipQtDesignerQPyDesignerTaskMenuExtension.cpp sipQtDesignercmodule.cpp
