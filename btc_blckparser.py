# PURE PYTHON BITCOIN BLOCKPARSER
# CC-BY-NC-ND
#

import binascii

filename = 'blk00000.dat'
with open(filename, 'rb') as f:
   print ("Please wait while "+str(filename)+" is loading")
   content = f.read()

BLCKCOUNT=1
BLCKOFFSET=0 #??
for i in range (BLCKCOUNT):
   OFFSET=BLCKOFFSET*(i)
   print ("=====")
   print("Block Number        : "+str(i+1))
   print("Magic ID            : "+binascii.hexlify(content[3+OFFSET])+binascii.hexlify(content[2+OFFSET])+binascii.hexlify(content[1+OFFSET])+binascii.hexlify(content[0+OFFSET]))
   last=3+OFFSET+1
   print("Block Length        : "+binascii.hexlify(content[last:last+4]))
   last=last+4+1
   print("Version Number      : "+binascii.hexlify(content[last:last+4]))
   last=last+4+1
   print("Previous Block Hash : "+binascii.hexlify(content[last:last+32]))
   last=last+32+1
   print("MerkleRoot          : "+binascii.hexlify(content[last:last+32]))
   last=last+32+1
   print("Time Stamp          : "+binascii.hexlify(content[last:last+4]))
   last=last+4+1
   print("Target Difficulty   : "+binascii.hexlify(content[last:last+4]))
   last=last+4+1
   print("Nonce               : "+binascii.hexlify(content[last:last+4]))
   last=last+4+1
   print(binascii.hexlify(content[last]))
