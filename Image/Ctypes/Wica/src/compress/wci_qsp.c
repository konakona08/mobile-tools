/******************************************************************************

PROJECT:     Wavelet Image Compression Algorithm (WICA) Codec
             LGTCM S/W Lab, St. Petersburg, Russia

MODULE NAME: QSP.c

ABSTRACT:    This file contains procedures for initialization of QSP buffers

AUTHORS:     Alexandr  Maiboroda              <alm@lgsoftlab.ru>,
             Sergey    Gramnitsky             <sernigra@lgsoftlab.ru>,				
					   Alexander Ivanov								  <alexi@lgsoftlab.ru>

HISTORY:     2004.08.19   v1.00

*******************************************************************************/

#include <stdlib.h>
#include <string.h>

#include "wci_portab.h"
#include "main/wci_codec.h"
#include "utils/wci_mem_align.h"
#include "compress/wci_qsp.h"

//------------------------------------------------------------------------------

int wci_qsp_init_buffer
(
  int                  IN     iComponentSize
, ALIGNED_MEMMANAGER * IN OUT prMemHeap
, QSP_BUFFER *            OUT prQSP
)
{
// This function performs initialization of QSP buffer. Return value is error code.
// Size of P component is equal max size of Q component in lossless mode.

  if((prQSP->pbtQ = (BYTE *)wci_aligned_malloc(iComponentSize, CACHE_LINE, prMemHeap)) == NULL)
    return ERR_MEMORY;
  //wci_memset(prQSP->pbtQ, 0, iComponentSize);
  prQSP->iQ_Length = iComponentSize;
  prQSP->iQ_Pos = 0;

  if((prQSP->pbtS = (BYTE *)wci_aligned_malloc( iComponentSize, CACHE_LINE, prMemHeap) ) == NULL)
    return ERR_MEMORY;
  //wci_memset(prQSP->pbtS, 0, iComponentSize);
  prQSP->iS_Length = iComponentSize;
  prQSP->iS_Pos = 0;

  if((prQSP->pbtP = (BYTE *)wci_aligned_malloc( iComponentSize, CACHE_LINE, prMemHeap) ) == NULL)
    return ERR_MEMORY;
  //wci_memset(prQSP->pbtP, 0, iComponentSize);
  prQSP->iP_Length = iComponentSize;
  prQSP->iP_Pos = 0;

  return ERR_NONE;
}

//------------------------------------------------------------------------------

int wci_qsp_calc_crc( QSP_BUFFER * IN prQSP)
{
  int i, s = 0;

  for( i=0; i<prQSP->iQ_Pos; i++ )
    s += prQSP->pbtQ[i];
  for( i=0; i<prQSP->iS_Pos; i++ )
    s += prQSP->pbtS[i];
  for( i=0; i<prQSP->iP_Pos; i++ )
    s += prQSP->pbtP[i];

  return s;
}

//------------------------------------------------------------------------------

void wci_qsp_done_buffer(
  QSP_BUFFER *         IN OUT prQSP
, ALIGNED_MEMMANAGER * IN OUT prMemHeap
)
{
// This function performs freeing of QSP buffer

  wci_aligned_free(prQSP->pbtQ, prMemHeap);
  prQSP->pbtQ = NULL;
  wci_aligned_free(prQSP->pbtS, prMemHeap);
  prQSP->pbtS = NULL;
  wci_aligned_free(prQSP->pbtP, prMemHeap);
  prQSP->pbtP = NULL;
}
