/******************************************************************************

PROJECT:     Wavelet Image Compression Algorithm (WICA) Codec
             LGTCM S/W Lab, St. Petersburg, Russia

MODULE NAME: QSP_compress.c

ABSTRACT:    This file contains procedures for compression of QSP buffers

AUTHORS:     Alexandr  Maiboroda              <alm@lgsoftlab.ru>,
             Sergey    Gramnitsky             <sernigra@lgsoftlab.ru>,				
					   Alexander Ivanov								  <alexi@lgsoftlab.ru>

HISTORY:     2004.08.19   v1.00

*******************************************************************************/

#ifdef ENCODER_SUPPORT

#include <stdlib.h>
#include <string.h>

#include "wci_portab.h"
#include "main/wci_codec.h"
#include "utils/wci_mem_align.h"
#include "compress/wci_qsp_compress.h"
#include "compress/wci_qsp_header.h"
#include "compress/wci_vlc.h"
#include "compress/wci_rle.h"
#include "compress/wci_huff_compress.h"
#ifdef QSP_CMP_ARITH
  #include "compress/Arith_codec.h"
#endif
#ifdef QSP_CMP_ARITH0
  #include "compress/Arith0_codec.h"
#endif
#ifdef QSP_CMP_RANGE
  #include "compress/Range_codec.h"
#endif

//------------------------------------------------------------------------------

// buffer size is depend on image size
#define QSP_CMP_BUFFER_SIZE      (MAX_IMAGE_WIDTH*MAX_IMAGE_HEIGHT)

//------------------------------------------------------------------------------

int wci_qsp_init_compressor(
  QSP_COMPRESSOR *     OUT prCompressor      //! Instance pointer
, int                  IN  iMode             //! Compression mode
, BYTE *               IN  pbtExternalBuffer //! External buffer pointer
                                             //!   If it equals NULL then memory
                                             //!   allocation is internal.
, int                  IN  iBufferLength     //! External buffer length
, ALIGNED_MEMMANAGER * IN  prMemHeap         //! Embedded Mem Manager or NULL if system mem
)
{
// This function performs initialization of QSP_COMPRESSOR structure
// RETURN VALUE: error code       


  wci_memset( prCompressor, 0, sizeof(QSP_COMPRESSOR) );
  prCompressor->iMode = iMode;

  if ( pbtExternalBuffer != NULL )
  {
    if(iBufferLength < QSP_CMP_BUFFER_SIZE) // must be that iBufferLength >= QSP_CMP_BUFFER_SIZE
      return ERR_PARAM;
    prCompressor->pbtBuffer = pbtExternalBuffer;
    prCompressor->bExternalBuffer = TRUE;
  }
  else
  {
    prCompressor->pbtBuffer = wci_aligned_malloc( QSP_CMP_BUFFER_SIZE, CACHE_LINE, prMemHeap );
    if ( prCompressor->pbtBuffer == NULL )
    {
      return ERR_MEMORY;
    }
    prCompressor->bExternalBuffer = FALSE;
  }
  prCompressor->prCompressTable= wci_aligned_malloc( sizeof(HUFF_PARAM), CACHE_LINE, prMemHeap);
  if ( prCompressor->prCompressTable == NULL )
  {
      return ERR_MEMORY;
  }
  return ERR_NONE;
}

//------------------------------------------------------------------------------

void wci_qsp_done_compressor(
  QSP_COMPRESSOR *     IN OUT prCompressor //! Instance pointer
, ALIGNED_MEMMANAGER * IN     prMemHeap    //! Embedded Mem Manager or NULL if system mem 
)
{
// This function performs freeing of QSP_COMPRESSOR structure

  if ( prCompressor != NULL )
  {
    if ( !prCompressor->bExternalBuffer )
    {
      wci_aligned_free( prCompressor->pbtBuffer, prMemHeap );
      prCompressor->pbtBuffer = NULL;
    }
    if ( prCompressor->prCompressTable)
    {
      wci_aligned_free( prCompressor->prCompressTable, prMemHeap );
      prCompressor->prCompressTable = NULL;
    }
  }
}

//------------------------------------------------------------------------------

static void __inline
wci_qsp_huffman_compress(
  BYTE *      IN     pbtData     //! The pointer to the data buffer
, int         IN     iDataLength
, BITSTREAM * IN OUT prBS
)
{
// This function compresses data from the buffer to the stream.
  HUFF_PARAM rHP;
  BYTE *     pbtBitstream;
  int        iOutLength;

  pbtBitstream = wci_bitstream_lock_buffer( prBS );
  wci_memset( &rHP, 0, sizeof(HUFF_PARAM) );
  wci_huff_compress_buffer( &rHP, pbtData, (uint32_t)iDataLength, pbtBitstream, (uint32_t*)&iOutLength );
  wci_bitstream_unlock_buffer( prBS, pbtBitstream, (uint32_t)iOutLength );
}

//------------------------------------------------------------------------------

static void __inline
wci_qsp_huffman_compress_table(
  BYTE *      IN     pbtData     //! The pointer to the data buffer
, int         IN     iDataLength
, HUFF_PARAM *OUT    prCompressTable
, BITSTREAM * IN OUT prBS
, uint *      OUT    nCompressedTableLength
)
{
  BYTE *     pbtBitstream = wci_bitstream_lock_buffer( prBS );

  wci_memset( prCompressTable, 0, sizeof(HUFF_PARAM) );
  wci_huff_compress_table( pbtData, iDataLength, prCompressTable, pbtBitstream , prBS->length-wci_bitstream_pos(prBS), nCompressedTableLength);
  
  wci_bitstream_unlock_buffer( prBS, pbtBitstream, *nCompressedTableLength);
}

//------------------------------------------------------------------------------

static void __inline
wci_qsp_huffman_compress_block(
  BYTE *      IN     pbtData     //! The pointer to the data buffer
, uint        IN     iDataLength
, HUFF_PARAM *IN     prCompressTable
, BITSTREAM * IN OUT prBS
)
{
// This function compresses data from the buffer to the stream.
  BYTE *     pbtBitstream;
  uint       nOutLength;

  pbtBitstream = wci_bitstream_lock_buffer( prBS );

  wci_huff_compress_data( pbtData, iDataLength, prCompressTable, pbtBitstream , prBS->length-wci_bitstream_pos(prBS), &nOutLength);

  wci_bitstream_unlock_buffer( prBS, pbtBitstream, nOutLength );
}

//------------------------------------------------------------------------------

static void __inline
wci_qsp_put_bit(
  BYTE *          pbtData         //! [in] The pointer to the bit buffer
, int             iDataLength     //! [in] The array length
, BITSTREAM *     prBS            //! [in/out] The output bitstream
)
{
// This function puts array of  bit to the stream.

  int i;

  for ( i=0; i<iDataLength; i++ )
  {
    wci_bitstream_put_bit( prBS, pbtData[i] );
  }
}

//------------------------------------------------------------------------------

static void __inline
wci_qsp_put_bits(
  BYTE *          pbtData                        //! [in]
, int             iDataLength                    //! [in]
, int             iBits                          //! [in]
, BITSTREAM *     prBS                           //! [in/out]
)
{
  int i;

  for ( i=0; i<iDataLength; i++ )
  {
    wci_bitstream_put_bits( prBS, pbtData[i], iBits );
  }
}

//------------------------------------------------------------------------------

static int __inline
wci_qsp_put_bit_to_buffer( BYTE* pbtBit, int iBits, BYTE* pbtData )
{
  BITSTREAM rBS;
  int       i;

  wci_bitstream_init( &rBS, pbtData, 0 );
  for ( i=0; i<iBits; i++ )
  {
    wci_bitstream_put_bits( &rBS, pbtBit[i], 1 );
  }
  wci_bitstream_pad( &rBS );
  wci_bitstream_flush(&rBS);
  return wci_bitstream_pos( &rBS );
}

//------------------------------------------------------------------------------

BOOL wci_qsp_remove_non_significant_zero(
  BYTE *          pbtData                        //! [in]
, int             iDataLength                    //! [in]
, int *           piCompressedDataLength )       //! [out]
{
// This function removes nonsignificant zeroes.
//RETURN VALUE: boolean flag       bCompress

  BOOL bCompress = FALSE;
  BYTE btMax = 0;
  int  i;
  uint uUsedBits;

  int  iFreq[256];
  wci_memset( iFreq, 0, sizeof(iFreq) );
  
  for ( i=0; i<iDataLength; i++ )
  {
    btMax |= pbtData[i];
    iFreq[pbtData[i]] ++;
  }
  for ( uUsedBits=0; uUsedBits<8; uUsedBits++ )
  {
    if ( btMax < (1 << uUsedBits) )
      break;
  }

  if (uUsedBits <= 4)
  {
    BITSTREAM rBS;
    wci_bitstream_init( &rBS, pbtData, 0 );
    for ( i=0; i<iDataLength; i++ )
    {
      wci_bitstream_put_bits( &rBS, (uint)pbtData[i], uUsedBits );
    }    
    wci_bitstream_pad( &rBS );
    wci_bitstream_flush( &rBS );    
    *piCompressedDataLength = wci_bitstream_pos( &rBS );
    bCompress = TRUE;
  }
  
  return bCompress;
}

//------------------------------------------------------------------------------

static void wci_qsp_compress_component(
  QSP_COMPRESSOR * IN OUT prCompressor      //! Instance pointer
, BYTE *           IN     pbtInData         //! 
, int              IN     nInSize
, int              IN     nFlags            //! Compression mode
, BITSTREAM *      IN OUT prBS              //! 
)
{
  if ( nInSize > 0 )
  {
    switch( nFlags )
    {
      case QSP_CMP_RAW:
        wci_bitstream_add_buffer( prBS, pbtInData, nInSize );
  	    break;

      case QSP_CMP_BIT_RAW:
        wci_qsp_put_bit( pbtInData, nInSize, prBS );
        wci_bitstream_pad( prBS );
  	    break;

      case QSP_CMP_VLC:
        wci_vlc_encode_buffer( pbtInData, nInSize, prBS );
        wci_bitstream_pad( prBS );
        break;

    #ifdef QSP_CMP_ARITH
      case QSP_CMP_ARITH:
        ArithN_CompressBuffer(pbtInData, nInSize, prBS);
        break;
    #endif

    #ifdef QSP_CMP_ARITH0
      case QSP_CMP_ARITH0:
        Arith0_CompressBuffer(pbtInData, nInSize, prBS);
        break;
    #endif

    #ifdef QSP_CMP_RANGE
      case QSP_CMP_RANGE:
        Range_CompressBuffer(pbtInData, nInSize, prBS);
        break;
    #endif

      case QSP_CMP_RLE_VLC:
      {
        int iInLength;
        
        #if defined(_DEBUG)
        {
          int i;
          for ( i=0; i<nInSize; i++ )
          {
            assert( pbtInData[i] <= 1 );
          }
        }
        #endif

        iInLength = wci_rle_compress_bit_buffer( pbtInData, nInSize, prCompressor->pbtBuffer );
        wci_vlc_encode_buffer( prCompressor->pbtBuffer, iInLength, prBS );
        break;
      }

      default:
      case QSP_CMP_HUFFMAN:
        wci_qsp_huffman_compress( pbtInData, nInSize, prBS );
        break;
    }
  }
}

//------------------------------------------------------------------------------

static void wci_qsp_compress_table(
  QSP_COMPRESSOR * IN OUT prCompressor      //! Instance pointer
, BYTE *           IN     pbtInData         //! 
, int              IN     nInSize
, uint             IN     nFlags            //! Compression mode
, BITSTREAM *      IN OUT prBS              //! 
, uint *           OUT   nCompressedTableSize
)
{
  if ( nInSize > 0 )
  {
    switch( nFlags )
    {
      case QSP_CMP_RAW:
      case QSP_CMP_BIT_RAW:
      case QSP_CMP_VLC:
      case QSP_CMP_RLE_VLC:
      default:
        break;

      case QSP_CMP_HUFFMAN:
      case QSP_CMP_RLE_HUFFMAN:
        wci_qsp_huffman_compress_table( pbtInData, nInSize, (HUFF_PARAM *)prCompressor->prCompressTable, prBS, nCompressedTableSize );
        break;
    }
  }
}

//------------------------------------------------------------------------------

static void wci_qsp_compress_component_block(
  QSP_COMPRESSOR * IN OUT prCompressor      //! Instance pointer
, BYTE *           IN     pbtInData         //! 
, int              IN     nInSize
, int              IN     nFlags            //! Compression mode
, BITSTREAM *      IN OUT prBS              //! 
, int               OUT   anCompressedSize[MAX_COMPRESSION_STEPS]  //! Compressed size of the block
)
{
  if ( nInSize > 0 )
  {
    uint iBitstreamLength = wci_bitstream_pos( prBS );

    switch( nFlags )
    {
      case QSP_CMP_RAW:
        wci_bitstream_add_buffer( prBS, pbtInData, nInSize );
  	    break;

      case QSP_CMP_BIT_RAW:
        wci_qsp_put_bit( pbtInData, nInSize, prBS );
        wci_bitstream_pad( prBS );
  	    break;

      case QSP_CMP_VLC:
        wci_vlc_encode_buffer( pbtInData, nInSize, prBS );
        wci_bitstream_pad( prBS );
        break;

      case QSP_CMP_RLE_VLC:
      {
        int iInLength;
        
        #if defined(_DEBUG)
        {
          int i;
          for ( i=0; i<nInSize; i++ )
          {
            assert( pbtInData[i] <= 1 );
          }
        }
        #endif

        iInLength = wci_rle_compress_bit_buffer( pbtInData, nInSize, prCompressor->pbtBuffer );
        anCompressedSize[COMPRESSION_STEP1]= iInLength;
        wci_vlc_encode_buffer( prCompressor->pbtBuffer, iInLength, prBS );
        wci_bitstream_flush( prBS );
        anCompressedSize[COMPRESSION_STEP2] = wci_bitstream_pos( prBS ) - iBitstreamLength;
        return ;
        break;
      }

      default:
      case QSP_CMP_HUFFMAN:
        wci_qsp_huffman_compress_block( pbtInData, nInSize, (HUFF_PARAM *)prCompressor->prCompressTable, prBS );
        break;
    }
      wci_bitstream_flush( prBS );
      anCompressedSize[COMPRESSION_STEP1] = wci_bitstream_pos( prBS ) - iBitstreamLength;
  }
}

//------------------------------------------------------------------------------

void wci_qsp_compress_layer(
  QSP_COMPRESSOR *    IN OUT prCompressor      //! Instance pointer
, QSP_BUFFER *        IN     prQSP             //! 
, int                 IN     iMode             //! Compression mode
, int                 IN     iBlocks           //! Number of QSP blocks to compress
, const QSP_SIZE *    IN     prBlockSize       //! Size of QSP block
, BITSTREAM *         IN OUT prBS              //! 
, QSP_SIZE *             OUT prCompressedSize  //! Compression statistics
, WCI_ALPHA_CHANNEL*  IN     pAlphaChannel
)
{
// This function compresses QSP data  to the stream corresponding to coding scheme.

  BITSTREAM           rHeaderBS;
  QSP_COMPRESS_HEADER rHeader;
  QSP_SIZE            rCompressedSize;
  QSP_SIZE            rSize;
  int                 iBitstreamLength;
  int                 iPartitionBlocks = iBlocks;

  // Save bitstream position
  wci_bitstream_pad( prBS );
  iBitstreamLength = wci_bitstream_pos( prBS );

  rHeaderBS = *prBS;

  // Put QSP bitstream block header
  wci_memset(&rHeader, 0, sizeof(QSP_COMPRESS_HEADER));
 
  rHeader.rTotalSize.iQ = prQSP->iQ_Pos;

  if(pAlphaChannel->isAlphaCannel) 
  {
    rHeader.rTotalSize.iQ -= pAlphaChannel->iQBlockSize;
    iPartitionBlocks = pAlphaChannel->iAlphaBlockNumber - 1;
  }

  rHeader.rTotalSize.iS = prQSP->iS_Pos;
  rHeader.rTotalSize.aiP[0] = prQSP->iP_Pos;

  rHeader.iCompressMode = iMode;


  if ( iPartitionBlocks > 0 && prBlockSize != NULL )
  {
    int i;

    if( iMode & QSP_BLOCK_PACK_FLAG)
        rHeader.iCompressMode |= QSP_BLOCK_PACK_FLAG;

    rHeader.iBlocks = iPartitionBlocks;


    for ( i=0; i< iPartitionBlocks; ++i )
      rHeader.rBlockSize[i] = prBlockSize[i];
  }


  wci_qsp_put_header( &rHeader, prBS );


  // Compress QSP components
  if ( iMode & QSP_BLOCK_PACK_FLAG && iPartitionBlocks > 0 && prBlockSize != NULL )
  {
    int i;
    uint  nCompressedTableSize;
    int *paiCompressedBlockSize;
  
    wci_memset(&rSize, 0, sizeof(QSP_SIZE));
    wci_memset(&rCompressedSize, 0, sizeof(QSP_SIZE));
    wci_qsp_compress_table( prCompressor, prQSP->pbtP, prQSP->iP_Pos, QSP_P_FLAG(iMode), prBS, &nCompressedTableSize);
    for ( i=0; i<iPartitionBlocks; ++i )
    {
      int k;
      for(k=0; k< MAX_PARTITION_COMPONENTS; k++)
      {
        paiCompressedBlockSize= &rHeader.rCompressedBlockSize[i].aiP[k][COMPRESSION_STEP1];
        wci_qsp_compress_component_block( prCompressor, &prQSP->pbtP[rSize.aiP[0]], prBlockSize[i].aiP[k], QSP_P_FLAG(iMode), prBS, paiCompressedBlockSize);
         rSize.aiP[0] += prBlockSize[i].aiP[k];
         rCompressedSize.aiP[0] += (paiCompressedBlockSize[COMPRESSION_STEP2]) ? paiCompressedBlockSize[COMPRESSION_STEP2] : paiCompressedBlockSize[COMPRESSION_STEP1];
      }
    }

    wci_qsp_compress_table( prCompressor, prQSP->pbtQ, prQSP->iQ_Pos, QSP_Q_FLAG(iMode), prBS, &nCompressedTableSize );
     
    for ( i=0; i< iPartitionBlocks ; ++i )
    {
      paiCompressedBlockSize= rHeader.rCompressedBlockSize[i].iQ;
      wci_qsp_compress_component_block( prCompressor, &prQSP->pbtQ[rSize.iQ], prBlockSize[i].iQ, QSP_Q_FLAG(iMode), prBS, paiCompressedBlockSize);

      rSize.iQ += prBlockSize[i].iQ;
      rCompressedSize.iQ += (paiCompressedBlockSize[COMPRESSION_STEP2]) ? paiCompressedBlockSize[COMPRESSION_STEP2] : paiCompressedBlockSize[COMPRESSION_STEP1];
    }


    wci_qsp_compress_table( prCompressor, prQSP->pbtS, prQSP->iS_Pos, QSP_S_FLAG(iMode), prBS, &nCompressedTableSize);
    for ( i=0; i<iPartitionBlocks; ++i )
    {
      paiCompressedBlockSize = rHeader.rCompressedBlockSize[i].iS;
      wci_qsp_compress_component_block( prCompressor, &prQSP->pbtS[rSize.iS], prBlockSize[i].iS, QSP_S_FLAG(iMode), prBS, paiCompressedBlockSize );
      rSize.iS += prBlockSize[i].iS;
      rCompressedSize.iS += (paiCompressedBlockSize[COMPRESSION_STEP2]) ? paiCompressedBlockSize[COMPRESSION_STEP2] : paiCompressedBlockSize[COMPRESSION_STEP1];
    }
  }
  else
  {
    iBitstreamLength = wci_bitstream_pos( prBS );
    wci_qsp_compress_component( prCompressor, prQSP->pbtP, prQSP->iP_Pos, QSP_P_FLAG(iMode), prBS );
    wci_bitstream_flush( prBS );
    rCompressedSize.aiP[0] = wci_bitstream_pos( prBS ) - iBitstreamLength;

    iBitstreamLength = wci_bitstream_pos( prBS );
    wci_qsp_compress_component( prCompressor, prQSP->pbtQ, prQSP->iQ_Pos, QSP_Q_FLAG(iMode), prBS );
    wci_bitstream_flush( prBS );
    rCompressedSize.iQ = wci_bitstream_pos( prBS ) - iBitstreamLength;

    iBitstreamLength = wci_bitstream_pos( prBS );
    wci_qsp_compress_component( prCompressor, prQSP->pbtS, prQSP->iS_Pos, QSP_S_FLAG(iMode), prBS );
    wci_bitstream_flush( prBS );
    rCompressedSize.iS = wci_bitstream_pos( prBS ) - iBitstreamLength;
  }

  iBitstreamLength = wci_bitstream_pos( prBS );

  if (rHeader.iCompressMode & QSP_CRC)
    rHeader.iCRC = wci_qsp_calc_crc( prQSP );

  rHeader.iCompressedLength = wci_bitstream_pos( prBS ) - iBitstreamLength;
  wci_qsp_put_header( &rHeader, &rHeaderBS );
 
  wci_bitstream_flush( &rHeaderBS );

  if ( prCompressedSize != NULL )
  {
    *prCompressedSize = rCompressedSize;
  }

  if(pAlphaChannel->isAlphaCannel)
  { 
 
    BITSTREAM           rHeaderBSAlpha;
    QSP_COMPRESS_HEADER rHeaderAlpha;
    int                 iLength   ;
    uint8_t*            pbtBuffer;


    iBlocks = 1;  // Add one block with Alpha channel
    wci_bitstream_pad( prBS );

    rHeaderBSAlpha = *prBS;

    // Put QSP bitstream block header
    wci_memset(&rHeaderAlpha, 0, sizeof(QSP_COMPRESS_HEADER));
    rHeaderAlpha.rTotalSize.iQ = prBlockSize[pAlphaChannel->iAlphaBlockNumber - 1].iQ;
    rHeaderAlpha.rTotalSize.iS = prBlockSize[pAlphaChannel->iAlphaBlockNumber - 1].iS;
    rHeaderAlpha.rTotalSize.aiP[0] = rHeaderAlpha.rTotalSize.aiP[1]= rHeaderAlpha.rTotalSize.aiP[2]\
      = prBlockSize[pAlphaChannel->iAlphaBlockNumber - 1].aiP[0];
    rHeaderAlpha.iCompressMode = QSP_CMP_RLE << QSP_Q_FLAG_SHIFT;

    if( iMode & QSP_BLOCK_PACK_FLAG)
      rHeaderAlpha.iCompressMode |= QSP_BLOCK_PACK_FLAG;
    rHeaderAlpha.iBlocks = iBlocks;
    rHeaderAlpha.rBlockSize[0] = prBlockSize[pAlphaChannel->iAlphaBlockNumber - 1];

    wci_qsp_put_header( &rHeaderAlpha, prBS );
    wci_bitstream_flush( prBS );
    pbtBuffer = wci_bitstream_lock_buffer(prBS);
    iLength = wci_rle_compress_buffer( &prQSP->pbtQ[pAlphaChannel->iQOffset], pAlphaChannel->iQBlockSize, pbtBuffer);
    wci_bitstream_unlock_buffer(prBS, pbtBuffer, iLength);
    wci_bitstream_flush( prBS );
    rHeaderAlpha.rCompressedBlockSize[0].iQ[0] = iLength;
    wci_qsp_put_header( &rHeaderAlpha, &rHeaderBSAlpha );
    wci_bitstream_flush( &rHeaderBSAlpha );
   
  }
}

//------------------------------------------------------------------------------

#endif  //ENCODER_SUPPORT