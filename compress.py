#!/bin/python3
import argparse
import struct
import queue
import math

parser = argparse.ArgumentParser(
                    prog='comp',
                    description='Compress files losslessly with Huffman encoding.',
                    epilog='Created by Stanley Wang (stanleymw).')

parser.add_argument
parser.add_argument('infile', type=argparse.FileType("rb"),
                    help='File to be compressed.')

# parser.add_argument('outfile', type)

args = parser.parse_args()

text = args.infile.read()

count = {}
# count = []
unique_chars = 0

for char in text:
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
        
for pair in sorted_raw:
    print(pair[1], pair[0])
    q.put(tree_node(pair[1], None, None, pair[0]))


def smaller(a,b):
    if a < b:
        return a,b
    return b,a

while (q.qsize() > 1):
    smallest_one, smallest_two = smaller(q.get(), q.get())

    q.put(tree_node(smallest_one.value + smallest_two.value, smallest_one, smallest_two, None))

root = q.get()
print("TREE GENERATED")

print("ROOT NODE:", root)

symbols = {}

def trav(node, path):
    # path is an integer representation of a byte
    if (node.data != None):
        symbols[node.data] = path
        return
    trav(node.left, path << 1)
    trav(node.right, (path << 1) + 1)

trav(root, 0)
print("SYMBOLS:", symbols)
for (i,v) in symbols.items():
    print(f"{i}: {v:b}")
dcode = {b:a for (a,b) in symbols.items()}
print("DECODE:", dcode)
# TODO: canonical coding
# symbols = sorted(symbols, key = lambda item: len(item[1]))
# print(symbols)
# print("modify..")
# current_code = 0
# for i in range(len(symbols)):
#     if i == 0:
#         symbols[i][1]
#
#     symbols[i+1][1] = current_code
# bits = "10101010"

class writeable_byte:
    def __init__(self):
        self.value = 0
        self.remaining_digits = 8

    def append(self, bits, num_digits_of_bits):
        # bits is a binary number
        self.value = self.value | (bits << (self.remaining_digits - num_digits_of_bits))
        self.remaining_digits -= num_digits_of_bits

        print(f"[!] current write: {self.value:b} | bits left: {self.remaining_digits}")

with open("out.txt", "ab") as binary_file:
    # Write bytes to file
    # binary_file.write(struct.pack('c', int(bits, 2)))

    # this is not encoded correctly: TODO: FIX
    write_buffer = []
    current_byte = writeable_byte()
    for byte in text:
        symbol = symbols[byte]
        if symbol == 0:
            symbol_size = 1
        else:
            symbol_size = math.floor(math.log(symbol, 2)) + 1

        # lets see how many bytes this will use
        # number_of_bytes_required = (symbol_size//8) + 1

        print(f"DEBUG: {symbol:b} [{symbol_size}]")
        for bit_number in range(symbol_size, 0, -1):
            # write each bit individually
            this_bit = (symbol >> (bit_number-1)) % 2
            current_byte.append(this_bit, 1)

            if current_byte.remaining_digits == 0:
                write_buffer.append(current_byte)
                current_byte = writeable_byte()

        # current_byte += (symbol_size <<

        while len(write_buffer) > 0:
            # print(f"{write_buffer.pop().value.to_bytes()}")
            binary_file.write(write_buffer.pop().value.to_bytes())

with open("out.txt", "rb") as binary_file:
    while (by := binary_file.read(1)):
        val = int.from_bytes(by)
        for bit in range(8,0,-1):
            print((val >> (bit-1)) % 2)
