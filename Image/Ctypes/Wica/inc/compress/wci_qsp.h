/******************************************************************************

PROJECT:     Wavelet Image Compression Algorithm (WICA) Codec
             LGTCM S/W Lab, St. Petersburg, Russia

MODULE NAME: wci_qsp.h

ABSTRACT:    This file contains definitions and data structures for compression of QSP buffers

AUTHORS:     Alexandr  Maiboroda              <alm@lgsoftlab.ru>,
             Sergey    Gramnitsky             <sernigra@lgsoftlab.ru>,				
					   Alexander Ivanov								  <alexi@lgsoftlab.ru>

HISTORY:     2004.08.19   v1.00

*******************************************************************************/

#ifndef QSP_H
#define QSP_H

#include "wci_portab.h"
#include "utils/wci_mem_align.h"

//------------------------------------------------------------------------------

#define QSP_CMP_NONE        0x0
#define QSP_CMP_BIT_RAW     0x1
#define QSP_CMP_RAW         0x2
#define QSP_CMP_VLC         0x3
#define QSP_CMP_HUFFMAN     0x4
#define QSP_CMP_RLE         0x5
#define QSP_CMP_RLE_VLC     0x6
//#define QSP_CMP_ARITH     0x7
//#define QSP_CMP_ARITH0    0x8
//#define QSP_CMP_RANGE     0x9
#define QSP_CMP_RLE_HUFFMAN 0xA

#define QSP_CMP_MODE_MASK   0xF

#define QSP_Q_FLAG_SHIFT  8
#define QSP_S_FLAG_SHIFT  4
#define QSP_P_FLAG_SHIFT  0

#define QSP_Q_FLAG(field) ((field >> QSP_Q_FLAG_SHIFT) & QSP_CMP_MODE_MASK)
#define QSP_S_FLAG(field) ((field >> QSP_S_FLAG_SHIFT) & QSP_CMP_MODE_MASK)
#define QSP_P_FLAG(field) ((field >> QSP_P_FLAG_SHIFT) & QSP_CMP_MODE_MASK)

//------------------------------------------------------------------------------

typedef struct 
{
  BYTE *pbtQ;              //! Buffer of positive quanted values
  BYTE *pbtS;              //! Sign buffer of quanted values
  BYTE *pbtP;              //! Partion decision buffer

  int  iQ_Pos;             //! position in Q-buffer
  int  iS_Pos;             //! position in S-buffer
  int  iP_Pos;             //! position in P-buffer

  int  iQ_Length;          //! Q-buffer length
  int  iS_Length;          //! S-buffer length
  int  iP_Length;          //! P-buffer length

} QSP_BUFFER;

//------------------------------------------------------------------------------

typedef struct tagQSP_COMPRESSOR
{
  int    iMode;                  //! Compression mode

  BOOL   bExternalBuffer;        //! Memory allocation in external buffer
  BYTE * pbtBuffer;              //! Pointer to auxiliary buffer
  void * prCompressTable;        //! Pointer to the compress table   
} QSP_COMPRESSOR;

//------------------------------------------------------------------------------

int wci_qsp_init_buffer
(
  int                  IN     iComponentSize
, ALIGNED_MEMMANAGER * IN OUT prMemHeap
, QSP_BUFFER *            OUT prQSP
);

void wci_qsp_done_buffer(
  QSP_BUFFER *         IN OUT prQSP
, ALIGNED_MEMMANAGER * IN OUT prMemHeap
);

int wci_qsp_calc_crc( 
  QSP_BUFFER * IN prQSP
);

//------------------------------------------------------------------------------

static void __inline
wci_qsp_duplicate(
  const QSP_BUFFER * IN  prSrc //! Source
, QSP_BUFFER *       OUT prDst //! Destination
)
{
  prDst->pbtQ = prSrc->pbtQ;
  prDst->pbtS = prSrc->pbtS;
  prDst->pbtP = prSrc->pbtP;
  prDst->iQ_Pos = prDst->iS_Pos = prDst->iP_Pos = 0;
  prDst->iQ_Length = prDst->iS_Length = prDst->iP_Length = 0;
}

//------------------------------------------------------------------------------

static void __inline
wci_qsp_copy_pointers(
  const QSP_BUFFER * IN  prSrc //! Source
, QSP_BUFFER *       OUT prDst //! Destination
)
{
  prDst->pbtQ = prSrc->pbtQ;
  prDst->pbtS = prSrc->pbtS;
  prDst->pbtP = prSrc->pbtP;
}

//------------------------------------------------------------------------------

static void __inline
wci_qsp_reset_lengths( QSP_BUFFER *prQSP )
{
  prQSP->iQ_Length = prQSP->iS_Length = prQSP->iP_Length = 0;
}

//------------------------------------------------------------------------------

static void __inline
wci_qsp_resetpos( QSP_BUFFER *prQSP )
{
  prQSP->iQ_Pos = prQSP->iS_Pos = prQSP->iP_Pos = 0;
}

//------------------------------------------------------------------------------

static void __inline
wci_qsp_offset_pointers(
  QSP_BUFFER *prQSP
, const int   iOffset
)
{
  prQSP->pbtQ += iOffset;
  prQSP->pbtS += iOffset;
  prQSP->pbtP += iOffset;
}

#endif // #ifndef QSP_H

