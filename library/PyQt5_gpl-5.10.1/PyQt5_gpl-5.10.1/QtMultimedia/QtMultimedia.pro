TEMPLATE = lib
CONFIG += warn_on exceptions_off plugin plugin_bundle
QT += multimedia
CONFIG += release
CONFIG -= android_install
TARGET = QtMultimedia

win32 {
    PY_MODULE = QtMultimedia.pyd
    PY_MODULE_SRC = $(DESTDIR_TARGET)
} else {
    PY_MODULE = QtMultimedia.so

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
HEADERS = sipAPIQtMultimedia.h
SOURCES = sipQtMultimediaQAbstractVideoBuffer.cpp sipQtMultimediaQAbstractVideoFilter.cpp sipQtMultimediaQAbstractVideoSurface.cpp sipQtMultimediaQAudio.cpp sipQtMultimediaQAudioBuffer.cpp sipQtMultimediaQAudioDecoder.cpp sipQtMultimediaQAudioDeviceInfo.cpp sipQtMultimediaQAudioEncoderSettings.cpp sipQtMultimediaQAudioFormat.cpp sipQtMultimediaQAudioInput.cpp sipQtMultimediaQAudioOutput.cpp sipQtMultimediaQAudioProbe.cpp sipQtMultimediaQAudioRecorder.cpp sipQtMultimediaQCamera.cpp sipQtMultimediaQCameraCaptureModes.cpp sipQtMultimediaQCameraExposure.cpp sipQtMultimediaQCameraExposureFlashModes.cpp sipQtMultimediaQCameraFocus.cpp sipQtMultimediaQCameraFocusFocusModes.cpp sipQtMultimediaQCameraFocusZone.cpp sipQtMultimediaQCameraFrameRateRange.cpp sipQtMultimediaQCameraImageCapture.cpp sipQtMultimediaQCameraImageCaptureCaptureDestinations.cpp sipQtMultimediaQCameraImageProcessing.cpp sipQtMultimediaQCameraInfo.cpp sipQtMultimediaQCameraLockTypes.cpp sipQtMultimediaQCameraViewfinderSettings.cpp sipQtMultimediaQImageEncoderSettings.cpp sipQtMultimediaQList0100QAudioDeviceInfo.cpp sipQtMultimediaQList0100QAudioFormatEndian.cpp sipQtMultimediaQList0100QAudioFormatSampleType.cpp sipQtMultimediaQList0100QAudioRole.cpp sipQtMultimediaQList0100QCameraFocusZone.cpp sipQtMultimediaQList0100QCameraFrameRateRange.cpp sipQtMultimediaQList0100QCameraInfo.cpp sipQtMultimediaQList0100QCameraViewfinderSettings.cpp sipQtMultimediaQList0100QMediaContent.cpp sipQtMultimediaQList0100QMediaResource.cpp sipQtMultimediaQList0100QMediaTimeInterval.cpp sipQtMultimediaQList0100QVideoFramePixelFormat.cpp sipQtMultimediaQMediaBindableInterface.cpp sipQtMultimediaQMediaContent.cpp sipQtMultimediaQMediaControl.cpp sipQtMultimediaQMediaMetaData.cpp sipQtMultimediaQMediaObject.cpp sipQtMultimediaQMediaPlayer.cpp sipQtMultimediaQMediaPlayerFlags.cpp sipQtMultimediaQMediaPlaylist.cpp sipQtMultimediaQMediaRecorder.cpp sipQtMultimediaQMediaResource.cpp sipQtMultimediaQMediaService.cpp sipQtMultimediaQMediaTimeInterval.cpp sipQtMultimediaQMediaTimeRange.cpp sipQtMultimediaQMultimedia.cpp sipQtMultimediaQRadioData.cpp sipQtMultimediaQRadioTuner.cpp sipQtMultimediaQSound.cpp sipQtMultimediaQSoundEffect.cpp sipQtMultimediaQVideoEncoderSettings.cpp sipQtMultimediaQVideoFilterRunnable.cpp sipQtMultimediaQVideoFilterRunnableRunFlags.cpp sipQtMultimediaQVideoFrame.cpp sipQtMultimediaQVideoProbe.cpp sipQtMultimediaQVideoSurfaceFormat.cpp sipQtMultimediacmodule.cpp
