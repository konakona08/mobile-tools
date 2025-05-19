// WcaLib.cpp : Defines the exported functions for the DLL.
//

#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include "WicaLib.h"
#include "main/wci_codec.h"

#ifdef _MSC_VER
#pragma warning(suppress : 6387)
#endif

typedef struct {
	STREAM stStream;
	STREAM_INFO stStreamInfo;
	DECODE_PARAM stDecodeParams;
	int nCurrentFrame;
} stWcaImg;

typedef struct {
	STREAM *pstEncodedImgs;
	STREAM stAssembleImage;
	FRAME_IMAGE_INFO stFrameImageInfo;
	STREAM stOutStream;
	ENCODE_PARAM stEncodeParams;
	char* pImg;
	int nCurrentFrame;
	int nFrames;
} stWcaEncoderImg;

WcaLib_Handle WcaLib_Create(void* pData, int nSize, WcaLib_IOType eType)
{
	stWcaImg *me;
	if (!pData || (!nSize && eType == WCA_IO_MEMORY))
		return NULL;
	me = (stWcaImg*)malloc(sizeof(stWcaImg));
	if (!me)
		return NULL;
	memset(me, 0, sizeof(stWcaImg));
	if (eType == WCA_IO_FILE)
	{
		FILE* pFile;
#ifdef WIN32
		struct _stat stStat;
#else
		struct stat stStat;
#endif //WIN32
#if defined(_MSC_VER) && !defined (_CRT_SECURE_NO_WARNINGS)
		fopen_s(&pFile, (const char*)pData, "rb");
#else
		pFile = fopen(pData, "rb");
#endif
		if (!pFile)
			return NULL;
#ifdef WIN32
		if (_stat(pData, &stStat) != 0)
#else
		if (stat(pData, &stStat) != 0)
#endif //WIN32
			return NULL;
		me->stStream.pbtData = (unsigned char*)malloc(stStat.st_size);
		if (!me->stStream.pbtData)
			return NULL;
		me->stStream.iLength = stStat.st_size;
		fread(me->stStream.pbtData, stStat.st_size, 1, pFile);
		fclose(pFile);
	}
	else
	{
		me->stStream.pbtData = (unsigned char*)malloc(nSize);
		if (!me->stStream.pbtData)
			return NULL;
		memcpy(me->stStream.pbtData, pData, nSize);
		me->stStream.iLength = nSize;
	}
	me->stStream.iOffset = 0;
	if (wci3_get_stream_info(&me->stStream, &me->stStreamInfo) != ERR_NONE)
		return NULL;
	if (!((me->stStreamInfo.eFormat == SF_STILL_IMAGE_V1) || (me->stStreamInfo.eFormat == SF_IMAGE_SEQUENCE_V1)
	   || (me->stStreamInfo.eFormat == SF_STILL_IMAGE_V2) || (me->stStreamInfo.eFormat == SF_IMAGE_SEQUENCE_V2)))
		return NULL;
	// allocate buffer as size of 32-bit image buffer
	me->stDecodeParams.pbtImage = (unsigned char*)malloc(me->stStreamInfo.iMaxWidth * me->stStreamInfo.iMaxHeight * sizeof(unsigned int));
	if (!me->stDecodeParams.pbtImage)
		return NULL;
	me->stDecodeParams.eColorSpace = CSP_BGRA|CSP_VFLIP;
	me->stDecodeParams.rScalability.eMode = SSM_NONE;
	me->stDecodeParams.rScalability.iZoomOut = 0;
	me->stDecodeParams.rScalability.rClipRect.left = 0;
	me->stDecodeParams.rScalability.rClipRect.top = 0;
	me->stDecodeParams.rScalability.rClipRect.right = me->stStreamInfo.iMaxWidth;
	me->stDecodeParams.rScalability.rClipRect.bottom = me->stStreamInfo.iMaxHeight;
	me->nCurrentFrame = 0;
	return (WcaLib_Handle)me;
}

unsigned char* WcaLib_GrabImage(WcaLib_Handle pHandle)
{
	stWcaImg* me = (stWcaImg*)pHandle;
	if (!me)
		return NULL;
	return me->stDecodeParams.pbtImage;
}

int WcaLib_internalDetermineBits(WcaLib_CSP eColorSpace, bool is_size)
{
	//! is_size bit values are rounded to 8, non is_size are BPP as-is
	if (is_size == true)
	{
		switch (eColorSpace & ~CSP_VFLIP)
		{
			case CSP_GRAYSCALE:
				return 8;
			case CSP_I420:
			case CSP_YV12:
			case CSP_YUY2:
			case CSP_YVYU:
			case CSP_UYVY:
			case CSP_RGB555:
			case CSP_RGB565:
				return 16;
			case CSP_RGB666:
			case CSP_BGR:
			case CSP_RGB:
			case CSP_YV12A:
			case CSP_YV24:
				return 24;
			case CSP_RGB56588:
			case CSP_RGB6668:
			case CSP_BGRA:
			case CSP_RGBA:
			case CSP_ABGR:
			case CSP_ARGB:
			case CSP_YV24A:
				return 32;
			default:
				return 0;
		}
	}
	else
	{
		switch (eColorSpace & ~CSP_VFLIP)
		{
			case CSP_GRAYSCALE:
				return 8;
			case CSP_I420:
			case CSP_YV12:
			case CSP_YV12A:
				return 12;
			case CSP_RGB555:
				return 15;
			case CSP_YUY2:
			case CSP_YVYU:
			case CSP_UYVY:
			case CSP_RGB565:
			case CSP_RGB56588:
				return 16;
			case CSP_RGB666:
			case CSP_RGB6668:
				return 18;
			case CSP_BGR:
			case CSP_RGB:
			case CSP_YV24A:
			case CSP_YV24:
				return 24;
			case CSP_BGRA:
			case CSP_RGBA:
			case CSP_ABGR:
			case CSP_ARGB:
				return 32;
			default:
				return 0;
		}
	}
}

bool WcaLib_SetDecoderCSP(WcaLib_Handle pHandle, WcaLib_CSP eCSP)
{
	stWcaImg* me = (stWcaImg*)pHandle;
	if (!me)
		return false;
	me->stDecodeParams.eColorSpace = (COLOR_SPACE)eCSP;
	//! note, any decoded image will be destroyed here
	if (me->stDecodeParams.pbtImage)
		free(me->stDecodeParams.pbtImage);
	me->stDecodeParams.pbtImage = (unsigned char*)malloc(me->stStreamInfo.iMaxWidth * me->stStreamInfo.iMaxHeight * (WcaLib_internalDetermineBits(eCSP, true)/8));
	if (!me->stDecodeParams.pbtImage)
		return false;
	return true;
}

bool WcaLib_GrabDimensions(WcaLib_Handle pHandle, int* pnWidth, int* pnHeight, int* pnBitsPerPixel)
{
	stWcaImg* me = (stWcaImg*)pHandle;
	if (!me)
		return false;
	if (pnWidth)
		*pnWidth = me->stStreamInfo.iMaxWidth;
	if (pnHeight)
		*pnHeight = me->stStreamInfo.iMaxHeight;
	if (pnBitsPerPixel)
		*pnBitsPerPixel = WcaLib_internalDetermineBits((WcaLib_CSP)me->stDecodeParams.eColorSpace, false);
	return true;
}

bool WcaLib_GrabFrames(WcaLib_Handle pHandle, int* pnFrames, int* pnFps)
{
	stWcaImg* me = (stWcaImg*)pHandle;
	if (!me)
		return false;
	if (pnFrames)
		*pnFrames = me->stStreamInfo.iFrames;
	if (pnFps)
		*pnFps = me->stStreamInfo.iFrameRate;
	return true;
}

bool WcaLib_Decode(WcaLib_Handle pHandle, int nFrame, int *pnDelay)
{
	stWcaImg* me = (stWcaImg*)pHandle;
	FRAME_INFO stFrameInfo;
	FRAME_IMAGE_INFO stImageInfo;
	int i = 0;
	DPRINTF(DPRINTF_DEBUG, "[WcaLib_DoDecode] : Start\n");
	if (!me)
		return false;
	if (nFrame > (me->stStreamInfo.iFrames - 1))
		nFrame = me->stStreamInfo.iFrames - 1;
	me->stStream.iOffset = 0;
	for (i = 0; i < me->stStreamInfo.iFrames; i++)
	{
		me->stStream.iOffset = wci3_find_frame(&me->stStream, &stFrameInfo);
		if (me->stStream.iOffset < 0)
			break;	// found no frames

		if (i == nFrame)
		{	// frame found
			DPRINTF(DPRINTF_DEBUG, "[WcaLib_DoDecode] : Frame found -> %d\n", i);
			if (nFrame > 1) // there is sequence of frames
			{	// set frame delay ptr
				if (pnDelay)
					*pnDelay = stFrameInfo.iDuration;
			}
			break;
		}
		me->stStream.iOffset += stFrameInfo.iLength;	// jump to the next frame
	}
	if (wci3_get_frame_info(&me->stStream, &stImageInfo) != ERR_NONE)
		return false;
	DPRINTF(DPRINTF_DEBUG, "[WcaLib_DoDecode] : Image info -> iWidth:%d,iHeight:%d\niResolutionHorz:%d\niResolutionVert:%d\niImageSize:%08x\niMaxZoomOut:%d\niQuality:%d\n",
							stImageInfo.iWidth,
							stImageInfo.iHeight,
							stImageInfo.iResolutionHorz,
							stImageInfo.iResolutionVert,
							stImageInfo.iImageSize,
							stImageInfo.iMaxZoomOut,
							stImageInfo.iQuality
							);
	if (me->stDecodeParams.pbtProcBuf)
		free(me->stDecodeParams.pbtProcBuf);
	me->stDecodeParams.iProcBufSize = wci3_get_decoder_buffer_size(&stImageInfo, me->stDecodeParams.rScalability.iZoomOut);
	if (me->stDecodeParams.iProcBufSize <= 0)
		return false;
	me->stDecodeParams.iProcBufSize++;
	DPRINTF(DPRINTF_DEBUG, "[WcaLib_DoDecode] : stDecodeParams.pbtProcBuf:%d\n", me->stDecodeParams.iProcBufSize);
	me->stDecodeParams.pbtProcBuf = (BYTE*)malloc(me->stDecodeParams.iProcBufSize);
	if (!me->stDecodeParams.pbtProcBuf)
		return false;
	if (wci3_decode_frame(&me->stDecodeParams, &me->stStream, &stImageInfo) != ERR_NONE)
		return false;
	DPRINTF(DPRINTF_DEBUG, "[WcaLib_DoDecode] : Success\n");
	return true;
}

void WcaLib_Destroy(WcaLib_Handle pHandle)
{
	stWcaImg* me = (stWcaImg*)pHandle;
	//set me for resetting pointers
	if (!me)
		return;
	if (me->stStream.pbtData)
		free(me->stStream.pbtData);
	if (me->stDecodeParams.pbtImage)
		free(me->stDecodeParams.pbtImage);
	if (me->stDecodeParams.pbtProcBuf)
		free(me->stDecodeParams.pbtProcBuf);
	me = NULL; //to make sure phandle is properly freed, we unset me
	free(pHandle);
}

#ifdef ENCODER_SUPPORT
WcaLib_Handle WcaLib_EncoderCreate(int nWidth, int nHeight, int nFrames)
{
	stWcaEncoderImg *me;
	if (!nWidth || !nHeight)
		return NULL;
	me = (stWcaEncoderImg*)malloc(sizeof(stWcaEncoderImg));
	if (!me)
		return NULL;
	memset(me, 0, sizeof(stWcaEncoderImg));
	me->stFrameImageInfo.iWidth = nWidth;
	me->stFrameImageInfo.iHeight = nHeight;
	me->stFrameImageInfo.iResolutionHorz = me->stFrameImageInfo.iResolutionVert = 0;
	me->stFrameImageInfo.iMaxZoomOut = 2;
	me->nFrames = nFrames;
	me->pstEncodedImgs = (STREAM*)malloc(sizeof(STREAM)*me->nFrames);
	if (!me->pstEncodedImgs)
		return NULL;
	memset(me->pstEncodedImgs, 0, sizeof(STREAM)*me->nFrames);
	me->pImg = (char*)malloc(me->stFrameImageInfo.iWidth*me->stFrameImageInfo.iHeight*4);
	if (!me->pImg)
		return NULL;
	return (WcaLib_Handle)me;
}

bool WcaLib_WriteImage(WcaLib_Handle pHandle, char* pImage, WcaLib_CSP eCSP)
{
	stWcaEncoderImg *me = (stWcaEncoderImg*)pHandle;
	if (!me)
		return FALSE;
	memcpy(me->pImg, pImage, me->stFrameImageInfo.iWidth*me->stFrameImageInfo.iHeight*WcaLib_internalDetermineBits(eCSP, true)/8);
	me->stFrameImageInfo.eColorSpace = eCSP;
	me->stFrameImageInfo.iImageSize = me->stFrameImageInfo.iWidth*me->stFrameImageInfo.iHeight*WcaLib_internalDetermineBits(eCSP, true)/8;
	return TRUE;
}

bool WcaLib_SetEncodeParam(WcaLib_Handle pHandle, WcaLib_CSP eCSP, WcaLib_DecodeSpeed eDecSpeed, int iQuality)
{
	stWcaEncoderImg *me = (stWcaEncoderImg*)pHandle;
	if (!me)
		return FALSE;
	me->stEncodeParams.eColorSpace = eCSP;
	me->stEncodeParams.eSpeed = eDecSpeed;
	me->stEncodeParams.iQuality = iQuality;
	return TRUE;
}

//Use bool to tell if ok or not
bool WcaLib_EncodeNewFrame(WcaLib_Handle pHandle)
{
	stWcaEncoderImg *me;
	DPRINTF(DPRINTF_DEBUG, "[WcaLib_DoEncode] : Start\n");

	me = (stWcaEncoderImg*)pHandle;
	if (!me)
	{
		DPRINTF(DPRINTF_DEBUG, "[WcaLib_DoEncode] : Handle missing!\n");
		return FALSE;
	}
	if (me->nCurrentFrame+1>me->nFrames)
	{
		DPRINTF(DPRINTF_DEBUG, "[WcaLib_DoEncode] : Can't continue: please remove unnecessary image and try again\n");
		return FALSE;
	}
	me->pstEncodedImgs[me->nCurrentFrame].pbtData = (unsigned char*)malloc(me->stFrameImageInfo.iWidth *
																		   me->stFrameImageInfo.iHeight*4);
	if (!me->pstEncodedImgs[me->nCurrentFrame].pbtData)
	{
		DPRINTF(DPRINTF_DEBUG, "[WcaLib_DoEncode] : Can't continue: fail to allocate encode buffer\n");
		return FALSE;
	}
	me->pstEncodedImgs[me->nCurrentFrame].iLength = me->stFrameImageInfo.iWidth * me->stFrameImageInfo.iHeight*4;
	// Encode the frame
	if (wci3_encode_frame(&me->stEncodeParams, me->pImg,
						  &me->stFrameImageInfo, &me->pstEncodedImgs[me->nCurrentFrame]) != ERR_NONE) {
		DPRINTF(DPRINTF_DEBUG, "[WcaLib_DoEncode] : Failed\n");
		free(me->pstEncodedImgs[me->nCurrentFrame].pbtData); // Free the allocated memory
		me->pstEncodedImgs[me->nCurrentFrame].iLength = me->pstEncodedImgs[me->nCurrentFrame].iLength = 0;
		return FALSE;
	}
	// Encoded frame. Encoded data stored in prStream.pbtData
	DPRINTF(DPRINTF_DEBUG, "[WcaLib_DoEncode] : Success, data=%x, size=%d\n",
			me->pstEncodedImgs[me->nCurrentFrame].pbtData, me->pstEncodedImgs[me->nCurrentFrame].iLength);
	me->nCurrentFrame++;
	return TRUE;
}

void WcaLib_GetEncodedData(WcaLib_Handle pHandle, unsigned char** ppbtData, int* piLength)
{
	stWcaEncoderImg *me = (stWcaEncoderImg*)pHandle;
	if (!me)
		return;
	*ppbtData = me->pstEncodedImgs[me->nCurrentFrame-1].pbtData;
	*piLength = me->pstEncodedImgs[me->nCurrentFrame-1].iLength;
}

bool WcaLib_RemoveFrame(WcaLib_Handle pHandle)
{
	stWcaEncoderImg *me;
	DPRINTF(DPRINTF_DEBUG, "[WcaLib_RemoveFrame] : Start\n");

	me = (stWcaEncoderImg*)pHandle;
	if (!me)
	{
		DPRINTF(DPRINTF_DEBUG, "[WcaLib_RemoveFrame] : Handle missing!\n");
		return FALSE;
	}
	free(me->pstEncodedImgs[me->nCurrentFrame-1].pbtData);
	me->pstEncodedImgs[me->nCurrentFrame-1].iLength = me->pstEncodedImgs[me->nCurrentFrame-1].iOffset = 0;
	// Encoded frame. Encoded data stored in prStream.pbtData
	DPRINTF(DPRINTF_DEBUG, "[WcaLib_RemoveFrame] : Success\n");
	me->nCurrentFrame--;
	return TRUE;
}

bool WcaLib_EncoderAssemble(WcaLib_Handle pHandle, int iFPS)
{
	stWcaEncoderImg* me;
	FAT stFAT;
	STREAM_INFO stStreamInfo;
	int i;
	int iSizeSum = 0;
	DPRINTF(DPRINTF_DEBUG, "[WcaLib_DoAssemble] : Start\n");

	me = (stWcaEncoderImg*)pHandle;
	if (!me)
	{
		DPRINTF(DPRINTF_DEBUG, "[WcaLib_DoAssemble] : Handle missing!\n");
		return FALSE;
	}
	if (!me->nFrames)
	{
		DPRINTF(DPRINTF_DEBUG, "[WcaLib_DoAssemble] : No frame to assemble!\n");
		return FALSE;
	}
	stStreamInfo.eFormat = SF_IMAGE_SEQUENCE_V1;
	stStreamInfo.iFrameRate = iFPS;
	stStreamInfo.iFrames = me->nFrames;
	stStreamInfo.iMaxWidth = me->stFrameImageInfo.iWidth;
	stStreamInfo.iMaxHeight = me->stFrameImageInfo.iHeight;
	stStreamInfo.iMaxZoomOut = me->stFrameImageInfo.iMaxZoomOut;
	if (me->stAssembleImage.pbtData)
	{
		free(me->stAssembleImage.pbtData);
		me->stAssembleImage.pbtData = NULL;
		me->stAssembleImage.iLength = 0;
		me->stAssembleImage.iOffset = 0;
	}
	for (i = 0; i < me->nFrames; i++)
	{
		char* pData = me->pstEncodedImgs[i].pbtData;
		iSizeSum += me->pstEncodedImgs[i].iOffset;
	}
	stFAT.iFrames = me->nFrames;
	stFAT.iMaxOffsets = me->nFrames;
	stFAT.piOffset = (int*)malloc(sizeof(int)*stFAT.iFrames);
	if (!stFAT.piOffset)
	{
		DPRINTF(DPRINTF_DEBUG, "[WcaLib_DoAssemble] : Failed, cannot allocate FAT offset!\n");
		return FALSE;
	}
	//First offset = size of streaminfo (4+PREAMBLE_SIZE+1+2+2+2+2+1)
	//             + size of FAT without frame offsets (4+PREAMBLE_SIZE+4)
	//             + (4*stFAT.iFrames)
	stFAT.piOffset[0] = 16+22+(4*stFAT.iFrames);
	iSizeSum += 16 + 22 + (4 * stFAT.iFrames);
	for (i = 1; i < me->nFrames; i++)
	{ 
		char* pData = me->pstEncodedImgs[i-1].pbtData;
		stFAT.piOffset[i] = pData[3] + (pData[2] << 8) + (pData[1] << 16) + (pData[0] << 24);
	}
	me->stAssembleImage.pbtData = (unsigned char*)malloc(iSizeSum);
	if (!me->stAssembleImage.pbtData)
	{
		DPRINTF(DPRINTF_DEBUG, "[WcaLib_DoAssemble] : Failed, cannot allocate data!\n");
		return FALSE;
	}
	me->stAssembleImage.iLength = iSizeSum;
	me->stAssembleImage.iOffset = 0;
	if (wci3_put_stream_info(&stStreamInfo, &me->stAssembleImage) != ERR_NONE)
	{
		DPRINTF(DPRINTF_DEBUG, "[WcaLib_DoAssemble] : Failed, cannot put stream info!\n");
		return FALSE;
	}
	if (wci_put_fat(&stFAT, &me->stAssembleImage) != ERR_NONE)
	{
		DPRINTF(DPRINTF_DEBUG, "[WcaLib_DoAssemble] : Failed, cannot put FAT!\n");
		return FALSE;
	}
	for (i = 0; i < me->nFrames; i++)
	{
		int iSize;
		char* pData = me->pstEncodedImgs[i].pbtData;
		iSize = me->pstEncodedImgs[i].iOffset;
		memcpy(&me->stAssembleImage.pbtData[me->stAssembleImage.iOffset], pData, iSize);
		printf("size..........%08x\n", iSize);
		me->stAssembleImage.iOffset += iSize;
	}
}

WcaLib_Stream* WcaLib_GetAssembledData(WcaLib_Handle pHandle)
{
	stWcaEncoderImg* me = (stWcaEncoderImg*)pHandle;
	if (!me)
		return NULL;
	return (WcaLib_Stream*)&me->stAssembleImage;
}

void WcaLib_EncoderDestroy(WcaLib_Handle pHandle)
{
	stWcaEncoderImg* me = (stWcaEncoderImg*)pHandle;
	int nCurrFrame;
	//set me for resetting pointers
	if (!me)
		return;
	for (nCurrFrame=0; nCurrFrame<me->nFrames; nCurrFrame++)
	{
		if(me->pstEncodedImgs[nCurrFrame].pbtData)
		{
			free(me->pstEncodedImgs[nCurrFrame].pbtData);
			me->pstEncodedImgs[nCurrFrame].pbtData = NULL;
		}
		me->pstEncodedImgs[nCurrFrame].iLength = me->pstEncodedImgs[nCurrFrame].iOffset = 0;
	}
	free(me->pstEncodedImgs);
	me->pstEncodedImgs = NULL;
	if(me->stOutStream.pbtData)
	{
		free(me->stOutStream.pbtData);
		me->stOutStream.pbtData = NULL;
	}
	me->stOutStream.iLength = me->stOutStream.iOffset = 0;
	if(me->pImg)
	{
		free(me->pImg);
		me->pImg = NULL;
	}
	memset(&me->stEncodeParams, 0, sizeof(ENCODE_PARAM));
	memset(&me->stFrameImageInfo, 0, sizeof(FRAME_IMAGE_INFO));
	me->nFrames = me->nCurrentFrame = 0;
	if (me->stAssembleImage.pbtData)
	{
		free(me->stAssembleImage.pbtData);
		me->stAssembleImage.pbtData = NULL;
		me->stAssembleImage.iLength = 0;
		me->stAssembleImage.iOffset = 0;
	}
	me = NULL; //to make sure phandle is properly freed, we unset me
	free(pHandle);
}
#endif