/******************************************************************************

PROJECT:     Wavelet Image Compression Algorithm (WICA) Codec
             LGTCM S/W Lab, St. Petersburg, Russia

MODULE NAME: wci_qsp_compress.h

ABSTRACT:    This file contains definitions and data structures for compression of QSP buffers

AUTHORS:     Alexandr  Maiboroda              <alm@lgsoftlab.ru>,
             Sergey    Gramnitsky             <sernigra@lgsoftlab.ru>,				
					   Alexander Ivanov								  <alexi@lgsoftlab.ru>

HISTORY:     2004.08.19   v1.00

*******************************************************************************/

#ifndef QSP_COMPRESS_H
#define QSP_COMPRESS_H

#ifdef ENCODER_SUPPORT

#include "main/wci_codec.h"
#include "main/wci_global.h"
#include "bitstream/wci_bitstream.h"
#include "compress/wci_qsp.h"

//------------------------------------------------------------------------------

int wci_qsp_init_compressor(
  QSP_COMPRESSOR *     OUT prCompressor      //! Instance pointer
, int                  IN  iMode             //! Compression mode
, BYTE *               IN  pbtExternalBuffer //! External buffer pointer
                                             //!   If it equals NULL then memory
                                             //!   allocation is internal.
, int                  IN  iBufferLength     //! External buffer length
, ALIGNED_MEMMANAGER * IN  prMemHeap         //! Embedded Mem Manager or NULL if system mem
);

//------------------------------------------------------------------------------

void wci_qsp_done_compressor(
  QSP_COMPRESSOR *     IN OUT prCompressor //! Instance pointer
, ALIGNED_MEMMANAGER * IN     prMemHeap    //! Embedded Mem Manager or NULL if system mem 
);

//------------------------------------------------------------------------------

void wci_qsp_compress_layer(
  QSP_COMPRESSOR *    IN OUT prCompressor      //! Instance pointer
, QSP_BUFFER *        IN     prQSP             //! QSP buffer to compress
, int                 IN     iMode             //! Compression mode
, int                 IN     iBlocks           //! Number of QSP blocks to compress
, const QSP_SIZE *    IN     prBlockSize       //! Size of QSP block
, BITSTREAM *         IN OUT prBS              //! Output bit stream of compressed data
, QSP_SIZE *             OUT prCompressedSize  //! Compression statistics
, WCI_ALPHA_CHANNEL *  IN     pAlphaChannel    //! The presence of A channel
);

#endif  //ENCODER_SUPPORT

#endif // QSP_COMPRESS_H

