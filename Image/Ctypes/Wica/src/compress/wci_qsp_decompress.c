/******************************************************************************

PROJECT:     Wavelet Image Compression Algorithm (WICA) Codec
             LGTCM S/W Lab, St. Petersburg, Russia

MODULE NAME: QSP_decompress.c

ABSTRACT:    This file contains procedures for decompression of QSP buffers

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
#include "compress/wci_qsp_decompress.h"
#include "compress/wci_qsp_header.h"
#include "compress/wci_vlc.h"
#include "compress/wci_rle.h"
#include "compress/wci_huff_decompress.h"
#ifdef QSP_CMP_ARITH
  #include "compress/Arith_codec.h"
#endif
#ifdef QSP_CMP_ARITH0
  #include "compress/Arith0_codec.h"
#endif
#ifdef QSP_CMP_RANGE
  #include "compress/Range_codec.h"
#endif


static void __inline wci_qsp_get_bit
(
  BITSTREAM * IN OUT prBS   //! The input bitstream
, int         IN     iBits
, BYTE *         OUT pbtBit 
)
{
// This function gets array of  bits to the stream.

  int iCycles = iBits/32, i = 0;

  while ( iCycles-- > 0 )
  {
    int iValue = wci_bitstream_get_bits( prBS, 32 );
    int iBit;
    
    for ( iBit=0; iBit<32; iBit++ )
    {
      pbtBit[i++] = (BYTE)((iValue & 0x80000000) != 0);
      iValue <<= 1;
    }
  }
  for ( ; i<iBits; i++ )
  {
    pbtBit[i] = (BYTE)wci_bitstream_get_bit( prBS );
  }
}

//------------------------------------------------------------------------------

static int __inline
wci_qsp_huffman_decompress_block(
 HUFF_TABLE *   IN      prDecompressTable
,  uint         IN      nBlockLength   //! The block data length
, BITSTREAM *   IN OUT  prBS           //! The input bitstream
, BYTE *           OUT  pbtData        //! The pointer to the output buffer
)
{
// This function decompresses block of data from the stream to the buffer.
  BYTE *     pbtBitstream;
  HUFF_CONTEXT rContext;
  
  pbtBitstream = (BYTE*)prBS->tail + prBS->pos/8;
  
  wci_huff_init_context( pbtBitstream, &rContext);

  if( wci_huff_decompress_data( prDecompressTable, &rContext, nBlockLength, pbtData))
    return -1;

  wci_bitstream_skip_bits( prBS, ( (ptr_t)rContext.pbtBuf - (ptr_t)pbtBitstream)*8 );
  return 0;
}

//------------------------------------------------------------------------------

static void __inline
wci_qsp_huffman_decompress_table(
  HUFF_TABLE *OUT    prDecompressTable
, BITSTREAM * IN OUT prBS
)
{
  BYTE *  pbtBitstream;
  uint    tab_size;

  pbtBitstream = (BYTE*)prBS->tail + prBS->pos/8;
  
  wci_huff_decompress_table(pbtBitstream, prBS->length-wci_bitstream_pos(prBS), prDecompressTable, &tab_size);

  wci_bitstream_skip_bits( prBS, tab_size*8 );
}

//------------------------------------------------------------------------------
static int __inline
wci_qsp_huffman_decompress(
  int         IN     iMaxDataLength //! The maximal data length
, BITSTREAM * IN OUT prBS           //! The input bitstream
, BYTE *         OUT pbtData        //! The pointer to the output buffer
)
{
// This function decompresses data from the stream to the buffer.

  HUFF_TABLE rTable;
  BYTE *     pbtBitstream;
  int        iOutLength = 0;
  int        err;  
  
  pbtBitstream = (BYTE*)prBS->tail + prBS->pos/8;

  err= wci_huff_decompress_buffer(&rTable, pbtBitstream, iMaxDataLength, pbtData, (uint32_t*)&iOutLength);
  
  wci_bitstream_skip_bits( prBS, (uint32_t)iOutLength*8 );

  return err;
}

//------------------------------------------------------------------------------

static int wci_qsp_decompress_component_block(
  int              IN     nFlags       //! Decompression mode
, int              IN     nOutSize     //! Uncompressed size of the block
, int              IN     anCompressedSize[MAX_COMPRESSION_STEPS]  //! Compressed size of the block
, QSP_COMPRESSOR * IN OUT prCompressor //! Instance pointer
, void  *          IN     prDecompressTable
, BITSTREAM *      IN OUT prBS         //! Input bit stream of compressed data
, BYTE *              OUT pbtOutData   //! 
)
{
  if ( nOutSize > 0 )
  {
    switch( nFlags )
    {
    case QSP_CMP_RAW:
      wci_bitstream_get_buffer( prBS, pbtOutData, nOutSize );
      break;

    case QSP_CMP_BIT_RAW:
      wci_qsp_get_bit( prBS, nOutSize, pbtOutData );
      wci_bitstream_byte_align( prBS );
      break;

    case QSP_CMP_VLC:
    {
      if ( wci_vlc_decode_buffer( prBS, nOutSize, pbtOutData ) != 0 )
      {
        return ERR_FORMAT;
      }
      wci_bitstream_byte_align( prBS );
      break;
    }

    case QSP_CMP_HUFFMAN:
      if ( wci_qsp_huffman_decompress_block( (HUFF_TABLE *)prDecompressTable, nOutSize, prBS, pbtOutData ) != 0 )
      {
        return ERR_FORMAT;
      }
      break;

    case QSP_CMP_RLE_VLC:
    {
      int iDecompressedLength;

      iDecompressedLength = anCompressedSize[COMPRESSION_STEP1];
      if ( wci_vlc_decode_buffer( prBS, iDecompressedLength, prCompressor->pbtBuffer ) != 0 )
      {
        return ERR_FORMAT;
      }
      
      iDecompressedLength = wci_rle_decompress_bit_buffer( prCompressor->pbtBuffer, iDecompressedLength, pbtOutData );
      if ( nOutSize != iDecompressedLength )
      {
        return ERR_FORMAT;
      }
      break;
    }

  #ifdef QSP_CMP_ARITH
    case QSP_CMP_ARITH:
      ArithN_ExpandBuffer( prBS, nOutSize, pbtOutData );
      break;
  #endif

  #ifdef QSP_CMP_ARITH0
    case QSP_CMP_ARITH0:
      Arith0_ExpandBuffer( prBS, nOutSize, pbtOutData );
      break;
  #endif

  #ifdef QSP_CMP_RANGE
    case QSP_CMP_RANGE:
      Range_ExpandBuffer( prBS, nOutSize, pbtOutData );
      break;
  #endif

    default:
      return ERR_FORMAT;
    }
  }

  return ERR_NONE;
}

//------------------------------------------------------------------------------

static int wci_qsp_decompress_component(
  int              IN     nFlags       //! Decompression mode
, int              IN     nOutSize
, QSP_COMPRESSOR * IN OUT prCompressor //! Instance pointer
, BITSTREAM *      IN OUT prBS         //! Input bit stream of compressed data
, BYTE *              OUT pbtOutData   //! 
)
{
  if ( nOutSize > 0 )
  {
    switch( nFlags )
    {
    case QSP_CMP_RAW:
      wci_bitstream_get_buffer( prBS, pbtOutData, nOutSize );
      break;

    case QSP_CMP_BIT_RAW:
      wci_qsp_get_bit( prBS, nOutSize, pbtOutData );
      wci_bitstream_byte_align( prBS );
      break;

    case QSP_CMP_VLC:
    {
      if ( wci_vlc_decode_buffer( prBS, nOutSize, pbtOutData ) != 0 )
      {
        return ERR_FORMAT;
      }
      wci_bitstream_byte_align( prBS );
      break;
    }

    case QSP_CMP_HUFFMAN:
      if ( wci_qsp_huffman_decompress( nOutSize, prBS, pbtOutData ) != 0 )
      {
        return ERR_FORMAT;
      }
      break;

    case QSP_CMP_RLE_VLC:
    {
      int iOutLength, iDecompressedLength;

      iOutLength = wci_bitstream_get_bits( prBS, 32 );
      if ( iOutLength > nOutSize )
      {
        return ERR_FORMAT;
      }
      if ( wci_vlc_decode_buffer( prBS, iOutLength, prCompressor->pbtBuffer ) != 0 )
      {
        return ERR_FORMAT;
      }
      
      iDecompressedLength = wci_rle_decompress_bit_buffer( prCompressor->pbtBuffer, iOutLength, pbtOutData );
      if ( nOutSize != iDecompressedLength )
      {
        return ERR_FORMAT;
      }
      break;
    }

  #ifdef QSP_CMP_ARITH
    case QSP_CMP_ARITH:
      ArithN_ExpandBuffer( prBS, nOutSize, pbtOutData );
      break;
  #endif

  #ifdef QSP_CMP_ARITH0
    case QSP_CMP_ARITH0:
      Arith0_ExpandBuffer( prBS, nOutSize, pbtOutData );
      break;
  #endif

  #ifdef QSP_CMP_RANGE
    case QSP_CMP_RANGE:
      Range_ExpandBuffer( prBS, nOutSize, pbtOutData );
      break;
  #endif

    default:
      return ERR_FORMAT;
    }
  }

  return ERR_NONE;
}
//------------------------------------------------------------------------------

static void * wci_qsp_decompress_table(
  uint             IN     nFlags            //! Compression mode
, BITSTREAM *      IN OUT prBS              //! 
)
{
  void * prDecompressTable= NULL;

    switch( nFlags )
    {
      case QSP_CMP_RAW:
      case QSP_CMP_BIT_RAW:
      case QSP_CMP_VLC:
      case QSP_CMP_RLE_VLC:
      default:
        break;

      case QSP_CMP_HUFFMAN:
        prDecompressTable= wci_aligned_malloc( sizeof(HUFF_TABLE), CACHE_LINE, NULL);
        wci_qsp_huffman_decompress_table( (HUFF_TABLE *)prDecompressTable, prBS);
        break;
    }
  return prDecompressTable;
}

//------------------------------------------------------------------------------

int wci_qsp_decompress_layer(
  QSP_COMPRESSOR * IN OUT prCompressor //! Instance pointer
, BITSTREAM *      IN OUT prBS         //! Input bit stream of compressed data
, QSP_BUFFER *        OUT prQSP        //! output QSP buffer
)
{
// This function decompresses data from the stream to QSP buffer.

  QSP_COMPRESS_HEADER rHeader;
  int                 err;

  err = wci_qsp_get_header( prBS, &rHeader );
  if ( err != ERR_NONE )
  {
    return err;
  }

  err = wci_qsp_check_header( &rHeader, prQSP );
  if ( err != ERR_NONE )
  {
    return err;
  }
  if( rHeader.iCompressMode & QSP_BLOCK_PACK_FLAG)
  {
    int i, iBlockOffset;
    void * prDecompressTable;
    int *paiCompressedBlockSize;

    prDecompressTable= wci_qsp_decompress_table( QSP_P_FLAG(rHeader.iCompressMode), prBS);
    for ( i=0, iBlockOffset= 0; i<rHeader.iBlocks; ++i )
    {
      int k;

      for(k=0; k< MAX_PARTITION_COMPONENTS; k++)
      {
          paiCompressedBlockSize= &rHeader.rCompressedBlockSize[i].aiP[k][COMPRESSION_STEP1];
          err = wci_qsp_decompress_component_block( QSP_P_FLAG(rHeader.iCompressMode), rHeader.rBlockSize[i].aiP[k], paiCompressedBlockSize, prCompressor, prDecompressTable, prBS, prQSP->pbtP + iBlockOffset );
          if ( err != ERR_NONE )
          {
            return err;
          }
          iBlockOffset += rHeader.rBlockSize[i].aiP[k];
      }
    }

    if( prDecompressTable)
      wci_aligned_free( prDecompressTable, NULL);

    prDecompressTable= wci_qsp_decompress_table( QSP_Q_FLAG(rHeader.iCompressMode), prBS);
    for ( i=0, iBlockOffset= 0; i<rHeader.iBlocks; ++i )
    {
      paiCompressedBlockSize= rHeader.rCompressedBlockSize[i].iQ;
      err = wci_qsp_decompress_component_block( QSP_Q_FLAG(rHeader.iCompressMode), rHeader.rBlockSize[i].iQ, paiCompressedBlockSize, prCompressor, prDecompressTable, prBS, prQSP->pbtQ + iBlockOffset );
      if ( err != ERR_NONE )
      {
        return err;
      }
      iBlockOffset += rHeader.rBlockSize[i].iQ;
    }
    if( prDecompressTable)
      wci_aligned_free( prDecompressTable, NULL);

    prDecompressTable= wci_qsp_decompress_table( QSP_S_FLAG(rHeader.iCompressMode), prBS);
    for ( i=0, iBlockOffset= 0; i<rHeader.iBlocks; ++i )
    {
      paiCompressedBlockSize= rHeader.rCompressedBlockSize[i].iS;
      err = wci_qsp_decompress_component_block( QSP_S_FLAG(rHeader.iCompressMode), rHeader.rBlockSize[i].iS, paiCompressedBlockSize, prCompressor, prDecompressTable, prBS, prQSP->pbtS + iBlockOffset );
      if ( err != ERR_NONE )
      {
        return err;
      }
      iBlockOffset += rHeader.rBlockSize[i].iS;
    }
    if( prDecompressTable)
      wci_aligned_free( prDecompressTable, NULL);
  }
  else
  {
    err = wci_qsp_decompress_component( QSP_P_FLAG(rHeader.iCompressMode), rHeader.rTotalSize.aiP[0], prCompressor, prBS, prQSP->pbtP );
    if ( err != ERR_NONE )
    {
      return err;
    }

    err = wci_qsp_decompress_component( QSP_Q_FLAG(rHeader.iCompressMode), rHeader.rTotalSize.iQ, prCompressor, prBS, prQSP->pbtQ );
    if ( err != ERR_NONE )
    {
      return err;
    }

    err = wci_qsp_decompress_component( QSP_S_FLAG(rHeader.iCompressMode), rHeader.rTotalSize.iS, prCompressor, prBS, prQSP->pbtS );
    if ( err != ERR_NONE )
    {
      return err;
    }
  }

  prQSP->iQ_Pos = rHeader.rTotalSize.iQ;
  prQSP->iS_Pos = rHeader.rTotalSize.iS;
  prQSP->iP_Pos = rHeader.rTotalSize.aiP[0];
  
  if (rHeader.iCompressMode & QSP_CRC)
    if ( rHeader.iCRC != wci_qsp_calc_crc( prQSP ) )
      return ERR_FORMAT;

  return ERR_NONE;
}