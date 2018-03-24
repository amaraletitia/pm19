TEMPLATE = lib
CONFIG += warn_on exceptions_off plugin plugin_bundle
QT += quick
CONFIG += release
CONFIG -= android_install
TARGET = QtQuick

win32 {
    PY_MODULE = QtQuick.pyd
    PY_MODULE_SRC = $(DESTDIR_TARGET)
} else {
    PY_MODULE = QtQuick.so

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
INCLUDEPATH += ../qpy/QtQuick
HEADERS = sipAPIQtQuick.h ../qpy/QtQuick/qpyquick_api.h ../qpy/QtQuick/qpyquick_chimera_helpers.h ../qpy/QtQuick/qpyquick_register_type.h ../qpy/QtQuick/qpyquickframebufferobject.h ../qpy/QtQuick/qpyquickitem.h ../qpy/QtQuick/qpyquickpainteditem.h
SOURCES = sipQtQuickQList0101QQuickItem.cpp sipQtQuickQQuickAsyncImageProvider.cpp sipQtQuickQQuickCloseEvent.cpp sipQtQuickQQuickFramebufferObject.cpp sipQtQuickQQuickFramebufferObjectRenderer.cpp sipQtQuickQQuickImageProvider.cpp sipQtQuickQQuickImageResponse.cpp sipQtQuickQQuickItem.cpp sipQtQuickQQuickItemFlags.cpp sipQtQuickQQuickItemGrabResult.cpp sipQtQuickQQuickItemItemChangeData.cpp sipQtQuickQQuickItemUpdatePaintNodeData.cpp sipQtQuickQQuickPaintedItem.cpp sipQtQuickQQuickPaintedItemPerformanceHints.cpp sipQtQuickQQuickRenderControl.cpp sipQtQuickQQuickTextDocument.cpp sipQtQuickQQuickTextureFactory.cpp sipQtQuickQQuickView.cpp sipQtQuickQQuickWindow.cpp sipQtQuickQQuickWindowCreateTextureOptions.cpp sipQtQuickQSGAbstractRenderer.cpp sipQtQuickQSGAbstractRendererClearMode.cpp sipQtQuickQSGBasicGeometryNode.cpp sipQtQuickQSGClipNode.cpp sipQtQuickQSGDynamicTexture.cpp sipQtQuickQSGEngine.cpp sipQtQuickQSGEngineCreateTextureOptions.cpp sipQtQuickQSGFlatColorMaterial.cpp sipQtQuickQSGGeometry.cpp sipQtQuickQSGGeometryAttribute.cpp sipQtQuickQSGGeometryAttributeSet.cpp sipQtQuickQSGGeometryColoredPoint2D.cpp sipQtQuickQSGGeometryNode.cpp sipQtQuickQSGGeometryPoint2D.cpp sipQtQuickQSGGeometryTexturedPoint2D.cpp sipQtQuickQSGMaterial.cpp sipQtQuickQSGMaterialFlags.cpp sipQtQuickQSGMaterialShader.cpp sipQtQuickQSGMaterialShaderRenderState.cpp sipQtQuickQSGMaterialShaderRenderStateDirtyStates.cpp sipQtQuickQSGMaterialType.cpp sipQtQuickQSGNode.cpp sipQtQuickQSGNodeDirtyState.cpp sipQtQuickQSGNodeFlags.cpp sipQtQuickQSGOpacityNode.cpp sipQtQuickQSGOpaqueTextureMaterial.cpp sipQtQuickQSGSimpleRectNode.cpp sipQtQuickQSGSimpleTextureNode.cpp sipQtQuickQSGSimpleTextureNodeTextureCoordinatesTransformMode.cpp sipQtQuickQSGTexture.cpp sipQtQuickQSGTextureMaterial.cpp sipQtQuickQSGTextureProvider.cpp sipQtQuickQSGTransformNode.cpp sipQtQuickQSGVertexColorMaterial.cpp sipQtQuickcmodule.cpp ../qpy/QtQuick/qpyquick_chimera_helpers.cpp ../qpy/QtQuick/qpyquick_post_init.cpp ../qpy/QtQuick/qpyquick_register_type.cpp ../qpy/QtQuick/qpyquickframebufferobject.cpp ../qpy/QtQuick/qpyquickitem.cpp ../qpy/QtQuick/qpyquickpainteditem.cpp
