/*
 * Interface wrapper code.
 *
 * Generated by SIP 4.19.8
 *
 * Copyright (c) 2018 Riverbank Computing Limited <info@riverbankcomputing.com>
 * 
 * This file is part of PyQt5.
 * 
 * This file may be used under the terms of the GNU General Public License
 * version 3.0 as published by the Free Software Foundation and appearing in
 * the file LICENSE included in the packaging of this file.  Please review the
 * following information to ensure the GNU General Public License version 3.0
 * requirements will be met: http://www.gnu.org/copyleft/gpl.html.
 * 
 * If you do not wish to use this file under the terms of the GPL version 3.0
 * then you may purchase a commercial license.  For more information contact
 * info@riverbankcomputing.com.
 * 
 * This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
 * WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
 */

#include "sipAPIQtSensors.h"

#line 46 "/Users/GYUNAM/Documents/PyProM/library/PyQt5_gpl-5.10.1/PyQt5_gpl-5.10.1/sip/QtSensors/qaccelerometer.sip"
#include <qaccelerometer.h>
#line 29 "/Users/GYUNAM/Documents/PyProM/library/PyQt5_gpl-5.10.1/PyQt5_gpl-5.10.1/QtSensors/sipQtSensorsQAccelerometerFilter.cpp"

#line 28 "/Users/GYUNAM/Documents/PyProM/library/PyQt5_gpl-5.10.1/PyQt5_gpl-5.10.1/sip/QtSensors/qaccelerometer.sip"
#include <qaccelerometer.h>
#line 33 "/Users/GYUNAM/Documents/PyProM/library/PyQt5_gpl-5.10.1/PyQt5_gpl-5.10.1/QtSensors/sipQtSensorsQAccelerometerFilter.cpp"


class sipQAccelerometerFilter : public  ::QAccelerometerFilter
{
public:
    sipQAccelerometerFilter();
    sipQAccelerometerFilter(const  ::QAccelerometerFilter&);
    virtual ~sipQAccelerometerFilter();

    /*
     * There is a protected method for every virtual method visible from
     * this class.
     */
protected:
    bool filter( ::QAccelerometerReading*);

public:
    sipSimpleWrapper *sipPySelf;

private:
    sipQAccelerometerFilter(const sipQAccelerometerFilter &);
    sipQAccelerometerFilter &operator = (const sipQAccelerometerFilter &);

    char sipPyMethods[1];
};

sipQAccelerometerFilter::sipQAccelerometerFilter():  ::QAccelerometerFilter(), sipPySelf(0)
{
    memset(sipPyMethods, 0, sizeof (sipPyMethods));
}

sipQAccelerometerFilter::sipQAccelerometerFilter(const  ::QAccelerometerFilter& a0):  ::QAccelerometerFilter(a0), sipPySelf(0)
{
    memset(sipPyMethods, 0, sizeof (sipPyMethods));
}

sipQAccelerometerFilter::~sipQAccelerometerFilter()
{
    sipInstanceDestroyedEx(&sipPySelf);
}

bool sipQAccelerometerFilter::filter( ::QAccelerometerReading*a0)
{
    sip_gilstate_t sipGILState;
    PyObject *sipMeth;

    sipMeth = sipIsPyMethod(&sipGILState,&sipPyMethods[0],sipPySelf,sipName_QAccelerometerFilter,sipName_filter);

    if (!sipMeth)
        return 0;

    extern bool sipVH_QtSensors_7(sip_gilstate_t, sipVirtErrorHandlerFunc, sipSimpleWrapper *, PyObject *,  ::QAccelerometerReading*);

    return sipVH_QtSensors_7(sipGILState, sipImportedVirtErrorHandlers_QtSensors_QtCore[0].iveh_handler, sipPySelf, sipMeth, a0);
}


PyDoc_STRVAR(doc_QAccelerometerFilter_filter, "filter(self, QAccelerometerReading) -> bool");

extern "C" {static PyObject *meth_QAccelerometerFilter_filter(PyObject *, PyObject *);}
static PyObject *meth_QAccelerometerFilter_filter(PyObject *sipSelf, PyObject *sipArgs)
{
    PyObject *sipParseErr = NULL;
    PyObject *sipOrigSelf = sipSelf;

    {
         ::QAccelerometerReading* a0;
         ::QAccelerometerFilter *sipCpp;

        if (sipParseArgs(&sipParseErr, sipArgs, "BJ8", &sipSelf, sipType_QAccelerometerFilter, &sipCpp, sipType_QAccelerometerReading, &a0))
        {
            bool sipRes;

            if (!sipOrigSelf)
            {
                sipAbstractMethod(sipName_QAccelerometerFilter, sipName_filter);
                return NULL;
            }

            sipRes = sipCpp->filter(a0);

            return PyBool_FromLong(sipRes);
        }
    }

    /* Raise an exception if the arguments couldn't be parsed. */
    sipNoMethod(sipParseErr, sipName_QAccelerometerFilter, sipName_filter, doc_QAccelerometerFilter_filter);

    return NULL;
}


/* Cast a pointer to a type somewhere in its inheritance hierarchy. */
extern "C" {static void *cast_QAccelerometerFilter(void *, const sipTypeDef *);}
static void *cast_QAccelerometerFilter(void *sipCppV, const sipTypeDef *targetType)
{
     ::QAccelerometerFilter *sipCpp = reinterpret_cast< ::QAccelerometerFilter *>(sipCppV);

    if (targetType == sipType_QSensorFilter)
        return static_cast< ::QSensorFilter *>(sipCpp);

    return sipCppV;
}


/* Call the instance's destructor. */
extern "C" {static void release_QAccelerometerFilter(void *, int);}
static void release_QAccelerometerFilter(void *sipCppV, int sipState)
{
    if (sipState & SIP_DERIVED_CLASS)
        delete reinterpret_cast<sipQAccelerometerFilter *>(sipCppV);
    else
        delete reinterpret_cast< ::QAccelerometerFilter *>(sipCppV);
}


extern "C" {static void dealloc_QAccelerometerFilter(sipSimpleWrapper *);}
static void dealloc_QAccelerometerFilter(sipSimpleWrapper *sipSelf)
{
    if (sipIsDerivedClass(sipSelf))
        reinterpret_cast<sipQAccelerometerFilter *>(sipGetAddress(sipSelf))->sipPySelf = NULL;

    if (sipIsOwnedByPython(sipSelf))
    {
        release_QAccelerometerFilter(sipGetAddress(sipSelf), sipIsDerivedClass(sipSelf));
    }
}


extern "C" {static void *init_type_QAccelerometerFilter(sipSimpleWrapper *, PyObject *, PyObject *, PyObject **, PyObject **, PyObject **);}
static void *init_type_QAccelerometerFilter(sipSimpleWrapper *sipSelf, PyObject *sipArgs, PyObject *sipKwds, PyObject **sipUnused, PyObject **, PyObject **sipParseErr)
{
    sipQAccelerometerFilter *sipCpp = 0;

    {
        if (sipParseKwdArgs(sipParseErr, sipArgs, sipKwds, NULL, sipUnused, ""))
        {
            sipCpp = new sipQAccelerometerFilter();

            sipCpp->sipPySelf = sipSelf;

            return sipCpp;
        }
    }

    {
        const  ::QAccelerometerFilter* a0;

        if (sipParseKwdArgs(sipParseErr, sipArgs, sipKwds, NULL, sipUnused, "J9", sipType_QAccelerometerFilter, &a0))
        {
            sipCpp = new sipQAccelerometerFilter(*a0);

            sipCpp->sipPySelf = sipSelf;

            return sipCpp;
        }
    }

    return NULL;
}


/* Define this type's super-types. */
static sipEncodedTypeDef supers_QAccelerometerFilter[] = {{53, 255, 1}};


static PyMethodDef methods_QAccelerometerFilter[] = {
    {SIP_MLNAME_CAST(sipName_filter), meth_QAccelerometerFilter_filter, METH_VARARGS, SIP_MLDOC_CAST(doc_QAccelerometerFilter_filter)}
};

PyDoc_STRVAR(doc_QAccelerometerFilter, "\1QAccelerometerFilter()\n"
"QAccelerometerFilter(QAccelerometerFilter)");


static pyqt5ClassPluginDef plugin_QAccelerometerFilter = {
    0,
    0,
    0,
    0
};


sipClassTypeDef sipTypeDef_QtSensors_QAccelerometerFilter = {
    {
        -1,
        0,
        0,
        SIP_TYPE_ABSTRACT|SIP_TYPE_SUPER_INIT|SIP_TYPE_LIMITED_API|SIP_TYPE_CLASS,
        sipNameNr_QAccelerometerFilter,
        {0},
        &plugin_QAccelerometerFilter
    },
    {
        sipNameNr_QAccelerometerFilter,
        {0, 0, 1},
        1, methods_QAccelerometerFilter,
        0, 0,
        0, 0,
        {0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
    },
    doc_QAccelerometerFilter,
    -1,
    -1,
    supers_QAccelerometerFilter,
    0,
    init_type_QAccelerometerFilter,
    0,
    0,
#if PY_MAJOR_VERSION >= 3
    0,
    0,
#else
    0,
    0,
    0,
    0,
#endif
    dealloc_QAccelerometerFilter,
    0,
    0,
    0,
    release_QAccelerometerFilter,
    cast_QAccelerometerFilter,
    0,
    0,
    0,
    0,
    0,
    0
};