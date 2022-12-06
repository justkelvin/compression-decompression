#!/usr/bin/env python3

# module imports
import sys
from bitstring import BitArray, Bits 

def lz77(textFile, windowBits, lengthBits):
    """Compresses a file using LZ77 and writes the compressed data to a file"""
    with open(textFile, "rb") as inputFile:
        data = BitArray(inputFile.read())
    compressed = compress(data, windowBits, lengthBits) # compress the data
    decompressed = decompress(compressed, windowBits, lengthBits) # decompress the data
    
    # write the compressed data to a file
    with open("compressed.bin", "wb") as compressedFile:
       compressed.tofile(compressedFile)

    # write the decompressed data to a file
    with open("decompressed.txt", "wb") as decompressedFile:
       decompressed.tofile(decompressedFile)
    
    print("Data length: {} bits".format(len(data))) # print the length of the data
    print("Compressed length: {} bits".format(len(compressed))) # print the length of the compressed data
    
    if (data == decompressed):
        print("Successful compression and decompression")
    else:
        print("Error in compression and decompression")

def compress(data, windowBits, lengthBits):
    """Compresses a BitArray using LZ77"""
    maxWindowLength = 2**windowBits - 1
    bufferLength = 2**lengthBits - 1
    buffer = data[:bufferLength] # initialize the buffer
    substring = buffer # initialize the substring
    compressed = BitArray()
    window = BitArray('') # initialize the window

    #constants in the case that a match is not found
    zeroPos = Bits(uint=0, length=windowBits)
    zeroLength = Bits(uint=0, length=lengthBits)

    bufferPos = 0
    maxLength = len(data)
    while ((bufferPos) < maxLength):
        bufferExtend = min(bufferPos + bufferLength, maxLength)
        buffer = data[bufferPos: bufferExtend]
        bufferStepper = len(buffer) 
        tripletAdded = False
        while bufferStepper > 0 and not tripletAdded:
            substring = buffer[0:bufferStepper]
            
            if (window.find(substring) != ()):
                position =  len(window) - int(window.find(substring)[0])
                
                length = len(substring)
                nextCharIndex = bufferPos + length
                if nextCharIndex > len(data) - 1:
                    nextCharIndex -= 1
                    substring = substring[:-1]
                    length = len(substring)
                nextChar = data[nextCharIndex:nextCharIndex+1]
                
                bitsPosition = Bits(uint=position, length=windowBits)
                bitsLength = Bits(uint=length, length=lengthBits)

                compressedTriplet = bitsPosition + bitsLength + nextChar
                substring += nextChar
                length += 1
                tripletAdded = True
            
            elif len(substring) == 1:
                length = 1
                compressedTriplet = zeroPos + zeroLength + substring
                tripletAdded = True
            bufferStepper -= 1
        bufferPos += length
        window += substring

        if len(window) > maxWindowLength:
            startIndex = len(window) -  maxWindowLength
            window = window[startIndex:]
        compressed += compressedTriplet
        
    return compressed

def decompress(compressed, windowBits, lengthBits):
    """Decompresses a BitArray using LZ77"""
    decompressedData = BitArray('')
    i = 0
    while i in range(len(compressed)):
        pos = compressed[i:(i+windowBits)].uint
        i += windowBits
        length = compressed[i:(i+lengthBits)].uint
        i += lengthBits
        char = compressed[i:(i+1)]
        i += 1
        if (pos == 0 and length == 0):
            decompressedData += char
        else:
            startPos = len(decompressedData) - pos
            endPos = startPos + length
            substring = decompressedData[startPos:endPos] + char # add the next character
            decompressedData += substring
    return decompressedData

if __name__ == "__main__":
    lz77(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))