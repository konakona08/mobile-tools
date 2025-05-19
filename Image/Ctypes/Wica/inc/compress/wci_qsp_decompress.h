/******************************************************************************

PROJECT:     Wavelet Image Compression Algorithm (WICA) Codec
             LGTCM S/W Lab, St. Petersburg, Russia

MODULE NAME: wci_qsp_decompress.h

ABSTRACT:    This file contains definitions and data structures for decompression of QSP buffers

AUTHORS:     Alexandr  Maiboroda              <alm@lgsoftlab.ru>,
             Sergey    Gramnitsky             <sernigra@lgsoftlab.ru>,				
					   Alexander Ivanov								  <alexi@lgsoftlab.ru>

HISTORY:     2004.08.19   v1.00

*******************************************************************************/

#ifndef QSP_DECOMPRESS_H
#define QSP_DECOMPRESS_H

#include "main/wci_codec.h"
#include "main/wci_global.h"
#include "bitstream/wci_bitstream.h"
#include "compress/wci_qsp.h"

//------------------------------------------------------------------------------

int wci_qsp_decompress_layer(
  QSP_COMPRESSOR *prCompressor                   //! [in]     Instance pointer
, BITSTREAM *     prBS                           //! [in/out] Input bit stream of compressed data
, QSP_BUFFER *    prQSP                          //! [out]    QSP buffer to decompress
);

#endif // QSP_DECOMPRESS_H

