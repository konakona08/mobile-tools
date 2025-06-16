#include <stdlib.h>
#include <stdio.h>


#define BYTEPOS(val, pos)                (((val) >> ((pos) << 3)) & 0xFF)
#define BYTE( data, pos )               (*(unsigned char *)((data)+(pos)))
#define HALF( data, pos )               (*(unsigned short *)((data)+(pos)))
#define WORD( data, pos )               (*(unsigned int *)((data)+(pos)))


#define GET_BYTE( data, pos )           ( ( (unsigned char *)( data ) )[pos] )
#define GET_HALF( data, pos )           ( ( GET_BYTE ( data, ( ( pos ) + 1 ) ) << 8 ) | GET_BYTE ( data, ( pos ) ) )
#define GET_WORD( data, pos )           ( ( GET_HALF ( data, ( ( pos ) + 2 ) ) << 16 ) | GET_HALF ( data, ( pos ) ) )
#define SET_BYTE( data, pos, val )      do { ( (unsigned char *)( data ) )[pos] = val; } while ( 0 )
#define SET_HALF( data, pos, val )      do { SET_BYTE ( data, ( pos ) + 1, ( ( val ) >> 8 ) & 0xFF ); SET_BYTE ( data, ( pos ), ( val ) & 0xFF ); } while ( 0 )
#define SET_WORD( data, pos, val )      do { SET_HALF ( data, ( pos ) + 2, ( ( val ) >> 16 ) & 0xFFFF ); SET_HALF ( data, ( pos ), ( val ) & 0xFFFF ); } while ( 0 )

#define GET_HALF_BIG( data, pos )           ( ( GET_BYTE ( data, ( ( pos ) ) ) << 8 ) | GET_BYTE ( data, ( pos + 1 ) ) )
#define GET_WORD_BIG( data, pos )           ( ( GET_HALF ( data, ( ( pos ) ) ) << 16 )| GET_HALF ( data, ( pos + 2 ) ) )
#define SET_HALF_BIG( data, pos, val )      do { SET_BYTE ( data, ( pos ), ( ( val ) >> 8 ) & 0xFF ); SET_BYTE ( data, ( pos + 1 ), ( val ) & 0xFF ); } while ( 0 )
#define SET_WORD_BIG( data, pos, val )      do { SET_HALF ( data, ( pos ), ( ( val ) >> 16 ) & 0xFFFF ); SET_HALF ( data, ( pos + 2 ), ( val ) & 0xFFFF ); } while ( 0 )

#if defined(_MSC_VER)
//  Microsoft 
#define EXPORT __declspec(dllexport)
#define IMPORT __declspec(dllimport)
#elif defined(__GNUC__)
//  GCC
#define EXPORT __attribute__((visibility("default")))
#define IMPORT
#else
//  do nothing and hope for the best?
#define EXPORT
#define IMPORT
#pragma warning Unknown dynamic link import/export semantics.
#endif

EXPORT void* my_malloc(size_t size) {
	void* ptr = malloc(size);
	return ptr;
}

EXPORT void my_free(void* ptr) {
	if (ptr) {
		free(ptr);
	}
}

EXPORT unsigned int decompress(unsigned char* src, unsigned char* pWrite) {
	unsigned int count_in1 = 0, count_in2 = 0, count_write = 0;
	unsigned char* src1, * src2, * pRead;
	unsigned int data = 0, count = 0;

	src += 16;

	unsigned int offset = (GET_HALF(src, 0) << 0x8 | GET_HALF(src, 0) >> 0x8) & 0xFFFF;
	src2 = src + 2 + offset;
	src1 = src + 2;

	if ((offset & 1) != 0) { //Если установлен младший бит, т.е. офсет нечетное число

		offset = (offset & 0xFFFE) | (GET_BYTE(src, 2) << 15) | (GET_BYTE(src, 3) << 23);
		src2 = src + 4 + offset;
		src1 = src + 4;
	}

	do {
		data = GET_HALF(src2, (count_in2 << 1));
		SET_HALF(pWrite, (count_write << 1), data);
		count_write++; count_in2++;

	} while ((data & 0x20) == 0);

	SET_HALF(pWrite, (count_write - 1) << 1, (data & ~0x20));

	if (offset > 0) { // Если старший бит не установлен
		do {

			unsigned short  a = BYTE(src1, count_in1);
			unsigned short  b = BYTE(src1, (count_in1 + 1));

			pRead = pWrite + ((count_write - ((a & 7) << 8 | b)) << 1);

			count = 0;

			do {
				SET_HALF(pWrite, (count_write) << 1, GET_HALF(pRead, count << 1));
				SET_HALF(pWrite, (count_write + 1) << 1, GET_HALF(pRead, (count + 1) << 1));
				count_write += 2; count += 2;
			} while (count < (a >> 4) - 2);

			while (count < (a >> 4)) {
				SET_HALF(pWrite, count_write << 1, GET_HALF(pRead, count << 1));
				count_write++; count++;

			}

			if ((a & 8) != 0) { // если 4й бит не установлен

				do {
					data = GET_HALF(src2, (count_in2 << 1));
					SET_HALF(pWrite, (count_write << 1), data);
					count_write++; count_in2++;

				} while ((data & 0x20) == 0);

				SET_HALF(pWrite, (count_write - 1) << 1, (data & ~0x20));
			}

			count_in1 += 2;

		} while (count_in1 < offset);

	}
	if ((offset & 1) != 0) {
		data = GET_HALF(src2, (count_in2 << 1));
		SET_HALF(pWrite, (count_write << 1), data);
		count_write++; count_in2++;
	}
	return count_write;
};

EXPORT unsigned int decompress_big(unsigned char* src, unsigned char* pWrite) {
	unsigned int count_in1 = 0, count_in2 = 0, count_write = 0;
	unsigned char* src1, * src2, * pRead;
	unsigned int data = 0, count = 0;

	src += 16;

	unsigned int offset = (GET_HALF(src, 0) << 0x8 | GET_HALF(src, 0) >> 0x8) & 0xFFFF;
	src2 = src + 2 + offset;
	src1 = src + 2;

	if ((offset & 1) != 0) { //Если установлен младший бит, т.е. офсет нечетное число

		offset = (offset & 0xFFFE) | (GET_BYTE(src, 2) << 15) | (GET_BYTE(src, 3) << 23);
		src2 = src + 4 + offset;
		src1 = src + 4;
	}

	do {
		data = GET_HALF_BIG(src2, (count_in2 << 1));
		SET_HALF(pWrite, (count_write << 1), data);
		count_write++; count_in2++;

	} while ((data & 0x20) == 0);

	SET_HALF(pWrite, (count_write - 1) << 1, (data & ~0x20));

	if (offset > 0) { // Если старший бит не установлен

		do {

			unsigned short  a = BYTE(src1, count_in1);
			unsigned short  b = BYTE(src1, (count_in1 + 1));


			pRead = pWrite + ((count_write - ((a & 7) << 8 | b)) << 1);

			count = 0;

			do {
				SET_HALF(pWrite, (count_write) << 1, GET_HALF(pRead, count << 1));
				SET_HALF(pWrite, (count_write + 1) << 1, GET_HALF(pRead, (count + 1) << 1));
				count_write += 2; count += 2;
			} while (count < (a >> 4) - 2);

			while (count < (a >> 4)) {
				SET_HALF(pWrite, count_write << 1, GET_HALF(pRead, count << 1));
				count_write++; count++;

			}

			if ((a & 8) != 0) { // если 4й бит не установлен

				do {
					data = GET_HALF_BIG(src2, (count_in2 << 1));
					SET_HALF(pWrite, (count_write << 1), data);
					count_write++; count_in2++;

				} while ((data & 0x20) == 0);

				SET_HALF(pWrite, (count_write - 1) << 1, (data & ~0x20));
			}

			count_in1 += 2;

		} while (count_in1 < offset);

	}
	if ((offset & 1) != 0) {
		data = GET_HALF_BIG(src2, (count_in2 << 1));
		SET_HALF(pWrite, (count_write << 1), data);
		count_write++; count_in2++;
	}
	return count_write;
}