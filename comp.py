#!/bin/python3
import argparse
import struct
import queue
import math

# Future:
'''

This project is a really rough proof of concept.
It uses static 1 byte symbols, so there is a hardcoded 256 byte header used to denote canonical code lengths.

In the future, I plan to incorporate multiple tree encodings and dynamic symbols (for hopefully better compression ratio).
But as for now, I am done with this project.

'''


parser = argparse.ArgumentParser(
                    prog='comp',
                    description='Compress files losslessly with Huffman encoding.',
                    epilog='Created by Stanley Wang (stanleymw).')

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-c", "--compress", action="store_true")
group.add_argument("-d", "--decompress", action="store_true")

parser.add_argument('infile', type=argparse.FileType("rb"),
                    help='File to be compressed/decompressed.')

parser.add_argument('outfile', type=argparse.FileType("ab"),
                    help="Output of compression/decompression.")

# parser.add_argument('outfile', type)

args = parser.parse_args()

if args.compress:
    count = {}
    unique_chars = 0

    # Count symbol occurences
    while (char := args.infile.read(1)):
        if char in count:
            count[char] += 1
        else:
            unique_chars += 1
            count[char] = 1

    sorted_raw = list(sorted(count.items(), key = lambda item : item[1]))

    class tree_node:
        def __init__(self, value, left, right, data = None):
            self.value = value
            self.left = left
            self.right = right
            self.data = data

        def __str__(self):
            return f"{self.value}: {self.data}"

        def __lt__(self, other):
            return self.value < other.value

    q = queue.PriorityQueue()
            
    # Generate Huffman tree
    for pair in sorted_raw:
        q.put(tree_node(pair[1], None, None, pair[0]))

    def smaller(a,b):
        if a < b:
            return a,b
        return b,a

    while (q.qsize() > 1):
        smallest_one, smallest_two = smaller(q.get(), q.get())

        q.put(tree_node(smallest_one.value + smallest_two.value, smallest_one, smallest_two, None))

    # Huffman tree generated
    root = q.get()

    symbols = {}

    def trav(node, path):
        # Path is path length (Encoding length in bits)
        if (node.data != None):
            symbols[node.data] = path
            return
        trav(node.left, path + 1)
        trav(node.right, path + 1)

    trav(root, 0)

    symbols = sorted(symbols.items(), key = lambda item : (item[1], item[0]))
    canonical_symbols = {}
    current_code = 0
    for i in range(len(symbols)):
        # i = ith symbol
        canonical_symbols[symbols[i][0]] = f"{current_code:b}".rjust(symbols[i][1], "0")

        if i == len(symbols)-1:
            break

        current_code = (current_code + 1) << (symbols[i+1][1] - symbols[i][1])


    # WRITE THE HEADER
    # 256 symbols
    # 1 byte for each



    class writeable_byte:
        def __init__(self):
            self.value = 0
            self.remaining_digits = 8

        def append(self, bits, num_digits_of_bits):
            # bits is a binary number
            self.value = self.value + (bits << (self.remaining_digits - num_digits_of_bits))
            self.remaining_digits -= num_digits_of_bits


    with args.outfile as binary_file:
        # Write header to file
        for i in range(2**8):
            sym = i.to_bytes()
            if sym in canonical_symbols:
                binary_file.write(len(canonical_symbols[sym]).to_bytes())
            else:
                binary_file.write(bytes(1))

        # Write encoded data to file
        write_buffer = []
        current_byte = writeable_byte()

        args.infile.seek(0)
        while (byte := args.infile.read(1)):
            symbol = canonical_symbols[byte]

            for bit in symbol:
                # bit is a string with 1 or 0
                # write each bit individually
                current_byte.append(int(bit, 2), 1)

                if current_byte.remaining_digits == 0:
                    # We finished building this byte, so lets write it to the file
                    binary_file.write(current_byte.value.to_bytes())
                    current_byte = writeable_byte()

        binary_file.write(current_byte.value.to_bytes())
    
    print("[!] Finished Compression")

if args.decompress:
    with args.outfile as out_file:
        with args.infile as binary_file:
            # first read the header
            reconstructed = {}

            for i in range(2**8):
                num = binary_file.read(1)
                val = int.from_bytes(num)
                if val != 0:
                    reconstructed[i.to_bytes()] = val

            reconstructed = sorted(reconstructed.items(), key = lambda item : (item[1], item[0]))
            canonical_symbols = {}
            current_code = 0
            for i in range(len(reconstructed)):
                # i = ith symbol
                canonical_symbols[reconstructed[i][0]] = f"{current_code:b}".rjust(reconstructed[i][1], "0")

                if i == len(reconstructed)-1:
                    break

                current_code = (current_code + 1) << (reconstructed[i+1][1] - reconstructed[i][1])

            class tree_node:
                def __init__(self, data = None):
                    self.left = None
                    self.right = None
                    self.data = data

            root = tree_node()

            for code in canonical_symbols.items():
                symbol = code[0]
                ptr = root
                st = code[1]
                for ch in st:
                    if ch == "0":
                        if ptr.left == None:
                            ptr.left = tree_node()
                        ptr = ptr.left
                    else:
                        if ptr.right == None:
                            ptr.right = tree_node()
                        ptr = ptr.right
                
                ptr.data = symbol

            ptr = root
            def trav(ptr, v):
                if ptr.data != None:
                    return
                trav(ptr.left, v + "0")
                trav(ptr.right, v + "1")

            trav(root, "")

            while (by := binary_file.read(1)):
                val = int.from_bytes(by)
                for bit in range(8,0,-1):
                    # read each bit individually
                    rb = ((val >> (bit-1)) % 2) == 1

                    if rb:
                        # 1
                        ptr = ptr.right
                    else:
                        ptr = ptr.left

                    if ptr.data != None:
                        out_file.write(ptr.data)
                        ptr = root



    print("[!] Finished Decompression!")








# will this get deleted?

