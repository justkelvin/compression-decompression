# compression algorithm in python using heapq and Counter from collections

# -*- coding: utf-8 -*-

try:
    import heapq
    import os
    from collections import Counter
    from rich import print
    from rich.console import Console
except ImportError:
    print("Please install the required modules")
    exit()

console = Console()
# class for Huffman nodes
class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    # defining comparators less_than and equals
    def __lt__(self, other):
        return self.freq < other.freq

    def __eq__(self, other):
        if(other == None):
            return False
        if(not isinstance(other, HuffmanNode)):
            return False
        return self.freq == other.freq

# class for Huffman coding
class HuffmanCoding:
    # Initializes the path and heap
    def __init__(self, path):
        self.path = path
        self.heap = []
        self.codes = {}
        self.reverse_mapping = {}

    # functions for compression and decompression:
    def create_frequency_dict(self, text):
        """ Returns a dictionary with the frequency of each character in the text """
        return Counter(text)

    def create_heap(self, frequency_dict):
        """ Makes a heap from the frequency dictionary """
        self.heap = [HuffmanNode(key, frequency_dict[key]) for key in frequency_dict]
        heapq.heapify(self.heap)
    
    def merge_nodes(self):
        """ Merges the nodes of the heap until there is only one node left """
        while len(self.heap) > 1:
            node1, node2 = heapq.heappop(self.heap), heapq.heappop(self.heap)
            merged = HuffmanNode(None, node1.freq + node2.freq)
            merged.left, merged.right = node1, node2
            heapq.heappush(self.heap, merged)
    
    def create_codes_helper(self, root, current_code):
        """ Makes the codes for the characters in the text """
        if root is None:
            return
        
        if root.char is not None:
            self.codes[root.char] = current_code
            self.reverse_mapping[current_code] = root.char
            return
        
        self.create_codes_helper(root.left, current_code + "0")
        self.create_codes_helper(root.right, current_code + "1")

    def create_codes(self):
        """ Makes the codes for the characters in the text """
        root = heapq.heappop(self.heap)
        current_code = ""
        self.create_codes_helper(root, current_code)

    def encoded_text(self, text):
        """ Returns the encoded text """
        encoded_text = ""
        for char in text:
            encoded_text += self.codes[char]
        return encoded_text
    
    def pad_encoded_text(self, encoded_text):
        """ Pads the encoded text """
        extra_padding = 8 - len(encoded_text) % 8
        encoded_text += "0" * extra_padding
        return "{0:08b}".format(extra_padding) + encoded_text

    def get_byte_array(self, padded_encoded_text):
        """ Returns the byte array """
        if(len(padded_encoded_text) % 8 != 0):
            console.print("Encoded text not padded properly", style="bold red")
            exit(0)
        b = bytearray()
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i+8]
            b.append(int(byte, 2))
        return b

    # function to compress the text
    def compress(self):
        """ Compresses the text """
        filename, file_extension = os.path.splitext(self.path)
        output_path = filename + ".bin"

        with open(self.path, 'r+') as file, open(output_path, 'wb') as output:
            text = file.read()
            text = text.rstrip()

            frequency_dict = self.create_frequency_dict(text)
            self.create_heap(frequency_dict)
            self.merge_nodes()
            self.create_codes()

            encoded_text = self.encoded_text(text)
            padded_encoded_text = self.pad_encoded_text(encoded_text)

            b = self.get_byte_array(padded_encoded_text)
            output.write(bytes(b))

        console.print("Original file size: ", style="bold green")
        console.print(os.stat(self.path).st_size, style="bold green")
        console.print("Compressed file size: ", style="bold green")
        console.print(os.stat(output_path).st_size, style="bold green")
        console.print("Compression ratio: ", style="bold green")
        console.print(os.stat(self.path).st_size / os.stat(output_path).st_size, style="bold green")
        console.print("Compression finished.", style="bold green")

        return output_path

    # function to decompress the text
    def decompress(self, input_path):
        """ Decompresses the text """
        filename, file_extension = os.path.splitext(self.path)
        output_path = filename + "_decompressed" + ".txt"

        with open(input_path, 'rb') as file, open(output_path, 'w') as output:
            bit_string = ""

            byte = file.read(1)
            while(len(byte) > 0):
                byte = ord(byte)
                bits = bin(byte)[2:].rjust(8, '0')
                bit_string += bits
                byte = file.read(1)

            extra_padding = int(bit_string[:8], 2)
            bit_string = bit_string[8:]
            encoded_text = bit_string[:-1*extra_padding]

            current_code = ""
            decoded_text = ""

            for bit in encoded_text:
                current_code += bit
                if(current_code in self.reverse_mapping):
                    character = self.reverse_mapping[current_code]
                    decoded_text += character
                    current_code = ""

            output.write(decoded_text)
        console.print("Decompression finished.", style="bold green")
        console.print("Original file size: ", style="bold green")
        console.print(os.stat(self.path).st_size, style="bold green")
        console.print("Decompressed file size: ", style="bold green")
        console.print(os.stat(output_path).st_size, style="bold green")
        console.print("Compression ratio: ", style="bold green")
        console.print(os.stat(self.path).st_size / os.stat(output_path).st_size, style="bold green")

        return output_path

# main function
def main():
    """ Main function """
    path = "input_lower.txt"
    h = HuffmanCoding(path)
    output_path = h.compress()
    h.decompress(output_path)

if __name__ == "__main__":
    main()
