/*
** ===========================================================================
** File: WcaLib.h
** Description: WICA library defines
** Copyright (c) 2023 raulmrio28-git and contributors.
** WICA Copyright: Copyright 2004-2012 LGTCM S/W Lab.
** History:
** when			who				what, where, why
** MM-DD-YYYY-- --------------- --------------------------------
** 05/20/2024	raulmrio28-git	Encoder
** 12/23/2023	raulmrio28-git	Initial version
** ===========================================================================
*/

/*
**----------------------------------------------------------------------------
**  Includes
**----------------------------------------------------------------------------
*/

#include <stdbool.h>

/*
**----------------------------------------------------------------------------
**  Definitions
**----------------------------------------------------------------------------
*/

// The following ifdef block is the standard way of creating macros which make exporting
// from a DLL simpler. All files within this DLL are compiled with the WCALIB_EXPORTS
// symbol defined on the command line. This symbol should not be defined on any project
// that uses this DLL. This way any other project whose source files include this file see
// WCALIB_API functions as being imported from a DLL, whereas this DLL sees symbols
// defined with this macro as being exported.
#ifdef WCALIB_EXPORTS
#define WCALIB_API __declspec(dllexport)
#else
#define WCALIB_API __declspec(dllimport)
#endif

// WcaLib handle
typedef void* WcaLib_Handle;
typedef enum {
	WCA_IO_FILE,
	WCA_IO_MEMORY
} WcaLib_IOType;

typedef enum {
	WcaLib_CSP_AUTO = 0,
	WcaLib_CSP_USER = (1 << 0), //! 4:2:0 planar  = (1<<(==I420, except for pointers/strides)
	WcaLib_CSP_I420 = (1 << 1), //! 4:2:0 planar
	WcaLib_CSP_YV12 = (1 << 2), //! 4:2:0 planar
	WcaLib_CSP_YV24 = (1 << 3), //! 4:4:4 planar
	WcaLib_CSP_YUY2 = (1 << 4), //! 4:2:2 packed
	WcaLib_CSP_UYVY = (1 << 5), //! 4:2:2 packed
	WcaLib_CSP_YVYU = (1 << 6), //! 4:2:2 packed
	WcaLib_CSP_BGRA = (1 << 7), //! 32-bit BGRA packed
	WcaLib_CSP_ABGR = (1 << 8), //! 32-bit ABGR packed
	WcaLib_CSP_RGBA = (1 << 9), //! 32-bit RGBA packed
	WcaLib_CSP_ARGB = (1 << 10), //! 32-bit ARGB packed
	WcaLib_CSP_BGR = (1 << 11), //! 24-bit BGR packed
	WcaLib_CSP_RGB = (1 << 12), //! 24-bit RGB packed
	WcaLib_CSP_RGB555 = (1 << 13), //! 15-bit RGB555 packed into 16 bit
	WcaLib_CSP_RGB565 = (1 << 14), //! 16-bit RGB565 packed into 16 bit
	WcaLib_CSP_RGB666 = (1 << 15), //! 18-bit RGB666 packed into 24 bit
	WcaLib_CSP_GRAYSCALE = (1 << 16), //! only luma component
	WcaLib_CSP_RGB56588 = (1 << 17), //! 16-bit RGB565 and alpha channel packed into 32 bit
	WcaLib_CSP_RGB6668 = (1 << 18), //! 18-bit RGB666 and alpha channel packed into 32 bit
	WcaLib_CSP_YV12A = (1 << 23), //! 4:2:0 planar with alpha channel
	WcaLib_CSP_YV24A = (1 << 24), //! 4:4:4 planar with alpha channel
	WcaLib_CSP_VFLIP = (1 << 30) //! vertical flip mask
} WcaLib_CSP;

typedef enum
{
	WcaLib_DecodeSpeed_Normal = 0,
	WcaLib_DecodeSpeed_Fast,
	WcaLib_DecodeSpeed_Max
} WcaLib_DecodeSpeed;

typedef struct
{
	unsigned char* pbtData;             //! [in] Input bitstream data buffer pointer
	int       iLength;                   //! [in] Input bitstream length [bytes]
	int       iOffset;                   //! [in\out] Size of processed data [bytes]

} WcaLib_Stream;

#ifdef __cplusplus
extern "C" {
#endif

// functions
WCALIB_API extern WcaLib_Handle WcaLib_Create(void *pData, int nSize, WcaLib_IOType eType);
WCALIB_API extern bool WcaLib_SetDecoderCSP(WcaLib_Handle pHandle, WcaLib_CSP eCSP);
WCALIB_API extern bool WcaLib_Decode(WcaLib_Handle pHandle, int nFrame, int* pnDelay);
WCALIB_API extern unsigned char* WcaLib_GrabImage(WcaLib_Handle pHandle);
WCALIB_API extern bool WcaLib_GrabDimensions(WcaLib_Handle pHandle, int* pnWidth, int* pnHeight, int* pnBitsPerPixel);
WCALIB_API extern bool WcaLib_GrabFrames(WcaLib_Handle pHandle, int* pnFrames, int* pnFps);
WCALIB_API extern void WcaLib_Destroy(WcaLib_Handle pHandle);
#ifdef ENCODER_SUPPORT
WCALIB_API extern WcaLib_Handle WcaLib_EncoderCreate(int nWidth, int nHeight, int nFrames);
WCALIB_API extern bool WcaLib_WriteImage(WcaLib_Handle pHandle, char* pImage, WcaLib_CSP eCSP);
WCALIB_API extern bool WcaLib_SetEncodeParam(WcaLib_Handle pHandle, WcaLib_CSP eCSP, WcaLib_DecodeSpeed eDecSpeed, int iQuality);
WCALIB_API extern bool WcaLib_EncodeNewFrame(WcaLib_Handle pHandle);
WCALIB_API extern void WcaLib_GetEncodedData(WcaLib_Handle pHandle, unsigned char** ppbtData, int* piLength);
WCALIB_API extern bool WcaLib_EncoderAssemble(WcaLib_Handle pHandle, int iFPS);
WCALIB_API extern WcaLib_Stream* WcaLib_GetAssembledData(WcaLib_Handle pHandle);
WCALIB_API extern bool WcaLib_RemoveFrame(WcaLib_Handle pHandle);
WCALIB_API extern void WcaLib_EncoderDestroy(WcaLib_Handle pHandle);
#endif
#ifdef __cplusplus
}  /* extern "C" */
#endif