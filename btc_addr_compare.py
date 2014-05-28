#!/usr/bin/python
# PupyBF.py

#
# Let us have a file filled with a lot of (non zero balance) bitcoin adresses
# for example ref_file.txt
# 
# 1Ceywpv86A1h4ABujceSjT9TJzFDoZKdmt
# 18Xiicd8eNRPUE5HKzHgjQpm8eWCqULP4b
# 12XK8XG3qxHFjkpBpX41PSVtq7LtL2mBSv
# 1E1o9GQY9V9cSTAAjQMWWUrgVhBb4opFQU
# 1DQUNz9iXN9Qz5BqoQHZkNVaHeg7g5evMT
# 17w3kRzRT3oXBueEYLpfAaPpr3RwooYeGY
# 
# 
# So let us do a b58decode on each line
# we get a fixed-size hexalooking bitcoin address
# and while b58 is bijective ... you gess what !?
# 
# 
# 007fd84f4a9aed43b8f016b2a2127bb6fcf3ac32a4ba0157cb
# 0052982eef9d42eaf9097884d4b0b08d92a052d5694d9d89d0
# 0010b3bd10b4541e9a1c509fa222fc7e9c4f5fcefafabff857
# 008ec0272c237aa586acf24f5cb2b674a6127fa2d1294c55e1
# 008811ee7113ee88f91791ab89f46c074db257e4639ae23c7e
# 004c0982dfe12128e389a7b41187d7a918af1267376671d5b1
# 
# Now we can strip the leading zeros
#
# 7fd84f4a9aed43b8f016b2a2127bb6fcf3ac32a4ba0157cb
# 52982eef9d42eaf9097884d4b0b08d92a052d5694d9d89d0
# 10b3bd10b4541e9a1c509fa222fc7e9c4f5fcefafabff857
# 10b3bd10b4541e9a1c509fa222fc7e9c4f5fcefafabff857
# 8ec0272c237aa586acf24f5cb2b674a6127fa2d1294c55e1
# 8811ee7113ee88f91791ab89f46c074db257e4639ae23c7e
# 4c0982dfe12128e389a7b41187d7a918af1267376671d5b1
#
# We get 48's hexa per line so we get 48^16 lines to test :)
#

# === IMPORT ===
import random
import struct
import hashlib
import time

# === DEFINE OPERATORS ===
ROR = lambda x, y: (((x & 0xffffffff) >> (y & 31)) | (x << (32 - (y & 31)))) & 0xffffffff
Ch = lambda x, y, z: (z ^ (x & (y ^ z)))
Maj = lambda x, y, z: (((x | y) & z) | (x & y))
S = lambda x, n: ROR(x, n)
R = lambda x, n: (x & 0xffffffff) >> n
Sigma0 = lambda x: (S(x, 2) ^ S(x, 13) ^ S(x, 22))
Sigma1 = lambda x: (S(x, 6) ^ S(x, 11) ^ S(x, 25))
Gamma0 = lambda x: (S(x, 7) ^ S(x, 18) ^ R(x, 3))
Gamma1 = lambda x: (S(x, 17) ^ S(x, 19) ^ R(x, 10))
SHA_BLOCKSIZE = 64
SHA_DIGESTSIZE = 32
__b58chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
__b58base = len(__b58chars)

# === FUNC b58encode ===
def b58encode(v):
    long_value = 0L
    for (i, c) in enumerate(v[::-1]):
        long_value += (256**i) * ord(c)
    result = ''
    while long_value >= __b58base:
        div, mod = divmod(long_value, __b58base)
        result = __b58chars[mod] + result
        long_value = div
    result = __b58chars[long_value] + result
    nPad = 0
    for c in v:
        if c == '\0': nPad += 1
        else: break
    return (__b58chars[0]*nPad) + result


# === FUNC hash160 ===
def hash_160(p_key):
 	md = hashlib.new('ripemd160')
	md.update(hashlib.sha256(p_key).digest())
	return md.digest()


# === FUNC hex_64 ===
def hex_64(n):
    return "%s"%("00000000000000000000000000000000000000000000000000000000000000000%x"%(n&0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff))[-64:]

def hex_02(n):
    return "%s"%("00%x"%(n&0xff))[-2:]

def hex_128(n):
    return "%s"%("0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000%x"%(n&0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff))[-128:]

# === FUNC new_shaobject ===
def new_shaobject():
    return {
        'digest': [0]*8,
        'count_lo': 0,
        'count_hi': 0,
        'data': [0]* SHA_BLOCKSIZE,
        'local': 0,
        'digestsize': 0
    }

# === FUNC  test ===
def test():
    a_str = "just a test string"
    assert 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' == sha256().hexdigest()
    assert 'd7b553c6f09ac85d142415f857c5310f3bbbe7cdd787cce4b985acedd585266f' == sha256(a_str).hexdigest()
    assert '8113ebf33c97daa9998762aacafe750c7cefc2b2f173c90c59663a57fe626f21' == sha256(a_str*7).hexdigest()
    
    s = sha256(a_str)
    s.update(a_str)
    assert '03d9963e05a094593190b6fc794cb1a3e1ac7d7883f0b5855268afeccc70d461' == s.hexdigest()

# === FUNC sha_transofrm ===
def sha_transform(sha_info):
    W = []
    
    d = sha_info['data']
    for i in xrange(0,16):
        W.append( (d[4*i]<<24) + (d[4*i+1]<<16) + (d[4*i+2]<<8) + d[4*i+3])
    
    for i in xrange(16,64):
        W.append( (Gamma1(W[i - 2]) + W[i - 7] + Gamma0(W[i - 15]) + W[i - 16]) & 0xffffffff )
    
    ss = sha_info['digest'][:]
    
    def RND(a,b,c,d,e,f,g,h,i,ki):
        t0 = h + Sigma1(e) + Ch(e, f, g) + ki + W[i];
        t1 = Sigma0(a) + Maj(a, b, c);
        d += t0;
        h  = t0 + t1;
        return d & 0xffffffff, h & 0xffffffff
    
    ss[3], ss[7] = RND(ss[0],ss[1],ss[2],ss[3],ss[4],ss[5],ss[6],ss[7],0,0x428a2f98);
    ss[2], ss[6] = RND(ss[7],ss[0],ss[1],ss[2],ss[3],ss[4],ss[5],ss[6],1,0x71374491);
    ss[1], ss[5] = RND(ss[6],ss[7],ss[0],ss[1],ss[2],ss[3],ss[4],ss[5],2,0xb5c0fbcf);
    ss[0], ss[4] = RND(ss[5],ss[6],ss[7],ss[0],ss[1],ss[2],ss[3],ss[4],3,0xe9b5dba5);
    ss[7], ss[3] = RND(ss[4],ss[5],ss[6],ss[7],ss[0],ss[1],ss[2],ss[3],4,0x3956c25b);
    ss[6], ss[2] = RND(ss[3],ss[4],ss[5],ss[6],ss[7],ss[0],ss[1],ss[2],5,0x59f111f1);
    ss[5], ss[1] = RND(ss[2],ss[3],ss[4],ss[5],ss[6],ss[7],ss[0],ss[1],6,0x923f82a4);
    ss[4], ss[0] = RND(ss[1],ss[2],ss[3],ss[4],ss[5],ss[6],ss[7],ss[0],7,0xab1c5ed5);
    ss[3], ss[7] = RND(ss[0],ss[1],ss[2],ss[3],ss[4],ss[5],ss[6],ss[7],8,0xd807aa98);
    ss[2], ss[6] = RND(ss[7],ss[0],ss[1],ss[2],ss[3],ss[4],ss[5],ss[6],9,0x12835b01);
    ss[1], ss[5] = RND(ss[6],ss[7],ss[0],ss[1],ss[2],ss[3],ss[4],ss[5],10,0x243185be);
    ss[0], ss[4] = RND(ss[5],ss[6],ss[7],ss[0],ss[1],ss[2],ss[3],ss[4],11,0x550c7dc3);
    ss[7], ss[3] = RND(ss[4],ss[5],ss[6],ss[7],ss[0],ss[1],ss[2],ss[3],12,0x72be5d74);
    ss[6], ss[2] = RND(ss[3],ss[4],ss[5],ss[6],ss[7],ss[0],ss[1],ss[2],13,0x80deb1fe);
    ss[5], ss[1] = RND(ss[2],ss[3],ss[4],ss[5],ss[6],ss[7],ss[0],ss[1],14,0x9bdc06a7);
    ss[4], ss[0] = RND(ss[1],ss[2],ss[3],ss[4],ss[5],ss[6],ss[7],ss[0],15,0xc19bf174);
    ss[3], ss[7] = RND(ss[0],ss[1],ss[2],ss[3],ss[4],ss[5],ss[6],ss[7],16,0xe49b69c1);
    ss[2], ss[6] = RND(ss[7],ss[0],ss[1],ss[2],ss[3],ss[4],ss[5],ss[6],17,0xefbe4786);
    ss[1], ss[5] = RND(ss[6],ss[7],ss[0],ss[1],ss[2],ss[3],ss[4],ss[5],18,0x0fc19dc6);
    ss[0], ss[4] = RND(ss[5],ss[6],ss[7],ss[0],ss[1],ss[2],ss[3],ss[4],19,0x240ca1cc);
    ss[7], ss[3] = RND(ss[4],ss[5],ss[6],ss[7],ss[0],ss[1],ss[2],ss[3],20,0x2de92c6f);
    ss[6], ss[2] = RND(ss[3],ss[4],ss[5],ss[6],ss[7],ss[0],ss[1],ss[2],21,0x4a7484aa);
    ss[5], ss[1] = RND(ss[2],ss[3],ss[4],ss[5],ss[6],ss[7],ss[0],ss[1],22,0x5cb0a9dc);
    ss[4], ss[0] = RND(ss[1],ss[2],ss[3],ss[4],ss[5],ss[6],ss[7],ss[0],23,0x76f988da);
    ss[3], ss[7] = RND(ss[0],ss[1],ss[2],ss[3],ss[4],ss[5],ss[6],ss[7],24,0x983e5152);
    ss[2], ss[6] = RND(ss[7],ss[0],ss[1],ss[2],ss[3],ss[4],ss[5],ss[6],25,0xa831c66d);
    ss[1], ss[5] = RND(ss[6],ss[7],ss[0],ss[1],ss[2],ss[3],ss[4],ss[5],26,0xb00327c8);
    ss[0], ss[4] = RND(ss[5],ss[6],ss[7],ss[0],ss[1],ss[2],ss[3],ss[4],27,0xbf597fc7);
    ss[7], ss[3] = RND(ss[4],ss[5],ss[6],ss[7],ss[0],ss[1],ss[2],ss[3],28,0xc6e00bf3);
    ss[6], ss[2] = RND(ss[3],ss[4],ss[5],ss[6],ss[7],ss[0],ss[1],ss[2],29,0xd5a79147);
    ss[5], ss[1] = RND(ss[2],ss[3],ss[4],ss[5],ss[6],ss[7],ss[0],ss[1],30,0x06ca6351);
    ss[4], ss[0] = RND(ss[1],ss[2],ss[3],ss[4],ss[5],ss[6],ss[7],ss[0],31,0x14292967);
    ss[3], ss[7] = RND(ss[0],ss[1],ss[2],ss[3],ss[4],ss[5],ss[6],ss[7],32,0x27b70a85);
    ss[2], ss[6] = RND(ss[7],ss[0],ss[1],ss[2],ss[3],ss[4],ss[5],ss[6],33,0x2e1b2138);
    ss[1], ss[5] = RND(ss[6],ss[7],ss[0],ss[1],ss[2],ss[3],ss[4],ss[5],34,0x4d2c6dfc);
    ss[0], ss[4] = RND(ss[5],ss[6],ss[7],ss[0],ss[1],ss[2],ss[3],ss[4],35,0x53380d13);
    ss[7], ss[3] = RND(ss[4],ss[5],ss[6],ss[7],ss[0],ss[1],ss[2],ss[3],36,0x650a7354);
    ss[6], ss[2] = RND(ss[3],ss[4],ss[5],ss[6],ss[7],ss[0],ss[1],ss[2],37,0x766a0abb);
    ss[5], ss[1] = RND(ss[2],ss[3],ss[4],ss[5],ss[6],ss[7],ss[0],ss[1],38,0x81c2c92e);
    ss[4], ss[0] = RND(ss[1],ss[2],ss[3],ss[4],ss[5],ss[6],ss[7],ss[0],39,0x92722c85);
    ss[3], ss[7] = RND(ss[0],ss[1],ss[2],ss[3],ss[4],ss[5],ss[6],ss[7],40,0xa2bfe8a1);
    ss[2], ss[6] = RND(ss[7],ss[0],ss[1],ss[2],ss[3],ss[4],ss[5],ss[6],41,0xa81a664b);
    ss[1], ss[5] = RND(ss[6],ss[7],ss[0],ss[1],ss[2],ss[3],ss[4],ss[5],42,0xc24b8b70);
    ss[0], ss[4] = RND(ss[5],ss[6],ss[7],ss[0],ss[1],ss[2],ss[3],ss[4],43,0xc76c51a3);
    ss[7], ss[3] = RND(ss[4],ss[5],ss[6],ss[7],ss[0],ss[1],ss[2],ss[3],44,0xd192e819);
    ss[6], ss[2] = RND(ss[3],ss[4],ss[5],ss[6],ss[7],ss[0],ss[1],ss[2],45,0xd6990624);
    ss[5], ss[1] = RND(ss[2],ss[3],ss[4],ss[5],ss[6],ss[7],ss[0],ss[1],46,0xf40e3585);
    ss[4], ss[0] = RND(ss[1],ss[2],ss[3],ss[4],ss[5],ss[6],ss[7],ss[0],47,0x106aa070);
    ss[3], ss[7] = RND(ss[0],ss[1],ss[2],ss[3],ss[4],ss[5],ss[6],ss[7],48,0x19a4c116);
    ss[2], ss[6] = RND(ss[7],ss[0],ss[1],ss[2],ss[3],ss[4],ss[5],ss[6],49,0x1e376c08);
    ss[1], ss[5] = RND(ss[6],ss[7],ss[0],ss[1],ss[2],ss[3],ss[4],ss[5],50,0x2748774c);
    ss[0], ss[4] = RND(ss[5],ss[6],ss[7],ss[0],ss[1],ss[2],ss[3],ss[4],51,0x34b0bcb5);
    ss[7], ss[3] = RND(ss[4],ss[5],ss[6],ss[7],ss[0],ss[1],ss[2],ss[3],52,0x391c0cb3);
    ss[6], ss[2] = RND(ss[3],ss[4],ss[5],ss[6],ss[7],ss[0],ss[1],ss[2],53,0x4ed8aa4a);
    ss[5], ss[1] = RND(ss[2],ss[3],ss[4],ss[5],ss[6],ss[7],ss[0],ss[1],54,0x5b9cca4f);
    ss[4], ss[0] = RND(ss[1],ss[2],ss[3],ss[4],ss[5],ss[6],ss[7],ss[0],55,0x682e6ff3);
    ss[3], ss[7] = RND(ss[0],ss[1],ss[2],ss[3],ss[4],ss[5],ss[6],ss[7],56,0x748f82ee);
    ss[2], ss[6] = RND(ss[7],ss[0],ss[1],ss[2],ss[3],ss[4],ss[5],ss[6],57,0x78a5636f);
    ss[1], ss[5] = RND(ss[6],ss[7],ss[0],ss[1],ss[2],ss[3],ss[4],ss[5],58,0x84c87814);
    ss[0], ss[4] = RND(ss[5],ss[6],ss[7],ss[0],ss[1],ss[2],ss[3],ss[4],59,0x8cc70208);
    ss[7], ss[3] = RND(ss[4],ss[5],ss[6],ss[7],ss[0],ss[1],ss[2],ss[3],60,0x90befffa);
    ss[6], ss[2] = RND(ss[3],ss[4],ss[5],ss[6],ss[7],ss[0],ss[1],ss[2],61,0xa4506ceb);
    ss[5], ss[1] = RND(ss[2],ss[3],ss[4],ss[5],ss[6],ss[7],ss[0],ss[1],62,0xbef9a3f7);
    ss[4], ss[0] = RND(ss[1],ss[2],ss[3],ss[4],ss[5],ss[6],ss[7],ss[0],63,0xc67178f2);
    
    dig = []
    for i, x in enumerate(sha_info['digest']):
        dig.append( (x + ss[i]) & 0xffffffff )
    sha_info['digest'] = dig

# === FUNC inverse_mod ===
def inverse_mod( a, m ):
  if a < 0 or m <= a: a = a % m
  c, d = a, m
  uc, vc, ud, vd = 1, 0, 0, 1
  while c != 0:
    q, c, d = divmod( d, c ) + ( c, )
    uc, vc, ud, vd = ud - q*uc, vd - q*vc, uc, vc
  assert d == 1
  if ud > 0: return ud
  else: return ud + m

# === FUNC  sha_init ===
def sha_init():
    sha_info = new_shaobject()
    sha_info['digest'] = [0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19]
    sha_info['count_lo'] = 0
    sha_info['count_hi'] = 0
    sha_info['local'] = 0
    sha_info['digestsize'] = 32
    return sha_info

# === FUNC sha224_init ===
def sha224_init():
    sha_info = new_shaobject()
    sha_info['digest'] = [0xc1059ed8, 0x367cd507, 0x3070dd17, 0xf70e5939, 0xffc00b31, 0x68581511, 0x64f98fa7, 0xbefa4fa4]
    sha_info['count_lo'] = 0
    sha_info['count_hi'] = 0
    sha_info['local'] = 0
    sha_info['digestsize'] = 28
    return sha_info

# === FUNC getbuff ===
def getbuf(s):
    if isinstance(s, str):
        return s
    elif isinstance(s, unicode):
        return str(s)
    else:
        return buffer(s)

# === FUNC sha_update ===
def sha_update(sha_info, buffer):
    count = len(buffer)
    buffer_idx = 0
    clo = (sha_info['count_lo'] + (count << 3)) & 0xffffffff
    if clo < sha_info['count_lo']:
        sha_info['count_hi'] += 1
    sha_info['count_lo'] = clo
    
    sha_info['count_hi'] += (count >> 29)
    
    if sha_info['local']:
        i = SHA_BLOCKSIZE - sha_info['local']
        if i > count:
            i = count
        
        # copy buffer
        for x in enumerate(buffer[buffer_idx:buffer_idx+i]):
            sha_info['data'][sha_info['local']+x[0]] = struct.unpack('B', x[1])[0]
        
        count -= i
        buffer_idx += i
        
        sha_info['local'] += i
        if sha_info['local'] == SHA_BLOCKSIZE:
            sha_transform(sha_info)
            sha_info['local'] = 0
        else:
            return
    
    while count >= SHA_BLOCKSIZE:
        # copy buffer
        sha_info['data'] = [struct.unpack('B',c)[0] for c in buffer[buffer_idx:buffer_idx + SHA_BLOCKSIZE]]
        count -= SHA_BLOCKSIZE
        buffer_idx += SHA_BLOCKSIZE
        sha_transform(sha_info)
        
    
    # copy buffer
    pos = sha_info['local']
    sha_info['data'][pos:pos+count] = [struct.unpack('B',c)[0] for c in buffer[buffer_idx:buffer_idx + count]]
    sha_info['local'] = count

# === FUNC _final ===
def sha_final(sha_info):
    lo_bit_count = sha_info['count_lo']
    hi_bit_count = sha_info['count_hi']
    count = (lo_bit_count >> 3) & 0x3f
    sha_info['data'][count] = 0x80;
    count += 1
    if count > SHA_BLOCKSIZE - 8:
        # zero the bytes in data after the count
        sha_info['data'] = sha_info['data'][:count] + ([0] * (SHA_BLOCKSIZE - count))
        sha_transform(sha_info)
        # zero bytes in data
        sha_info['data'] = [0] * SHA_BLOCKSIZE
    else:
        sha_info['data'] = sha_info['data'][:count] + ([0] * (SHA_BLOCKSIZE - count))
    
    sha_info['data'][56] = (hi_bit_count >> 24) & 0xff
    sha_info['data'][57] = (hi_bit_count >> 16) & 0xff
    sha_info['data'][58] = (hi_bit_count >>  8) & 0xff
    sha_info['data'][59] = (hi_bit_count >>  0) & 0xff
    sha_info['data'][60] = (lo_bit_count >> 24) & 0xff
    sha_info['data'][61] = (lo_bit_count >> 16) & 0xff
    sha_info['data'][62] = (lo_bit_count >>  8) & 0xff
    sha_info['data'][63] = (lo_bit_count >>  0) & 0xff
    
    sha_transform(sha_info)
    
    dig = []
    for i in sha_info['digest']:
        dig.extend([ ((i>>24) & 0xff), ((i>>16) & 0xff), ((i>>8) & 0xff), (i & 0xff) ])
    return ''.join([chr(i) for i in dig])

# === FUNC generate ===
def generate(z):  
   ### generate privkey
   randrange = random.SystemRandom().randrange
   n = g.order()
   secret = randrange( 1, n )
   #print 'random_private=', hex_64(secret)
   for t in range (z):
      pubkey = Public_key( g, g * secret )
      btc_pubkey = hex_02(04)+ hex_64(pubkey.point.x())+hex_64(pubkey.point.y())
      btc_pubkey_sha256=hashlib.sha256(btc_pubkey.decode('hex')).digest()
      btc_pubkey_ripemd160=hash_160(btc_pubkey.decode('hex')).encode('hex')
      netadd='00'+str(btc_pubkey_ripemd160)
      netadd_sha256=hashlib.sha256(netadd.decode('hex')).digest()
      netadd_sha256_256=hashlib.sha256(netadd_sha256).digest()
      btcadd_hexa=netadd+str(netadd_sha256_256.encode('hex')[0:8])
      #btcadd=b58encode(btcadd_hexa.decode('hex'))
      secret = secret +1
      #print 'btc_address=',btcadd
      #print 'btc_address_hex=',btcadd_hexa
      print btcadd_hexa[2:] # Assume that b58decode the wall ref_file is quicker than b58encode all tested addresses 

# === CLASS sha224 === 
class sha224(object):
    digest_size = digestsize = 28

    def __init__(self, s=None):
        self._sha = sha224_init()
        if s:
            sha_update(self._sha, getbuf(s))

    def copy(self):
        new = sha224.__new__(sha224)
        new._sha = self._sha.copy()
        return new

# === CLASS sha256 ===
class sha256(object):
    digest_size = digestsize = SHA_DIGESTSIZE
    block_size = SHA_BLOCKSIZE

    def __init__(self, s=None):
        self._sha = sha_init()
        if s:
            sha_update(self._sha, getbuf(s))
    
    def update(self, s):
        sha_update(self._sha, getbuf(s))
    
    def digest(self):
        return sha_final(self._sha.copy())[:self._sha['digestsize']]
    
    def hexdigest(self):
        return ''.join(['%.2x' % ord(i) for i in self.digest()])

    def copy(self):
        new = sha256.__new__(sha256)
        new._sha = self._sha.copy()
        return new

# === CLASS CurveFP ===
class CurveFp( object ):
  def __init__( self, p, a, b ):
    self.__p = p
    self.__a = a
    self.__b = b

  def p( self ):
    return self.__p

  def a( self ):
    return self.__a

  def b( self ):
    return self.__b

  def contains_point( self, x, y ):
    return ( y * y - ( x * x * x + self.__a * x + self.__b ) ) % self.__p == 0

# === CLASS Signature ===
class Signature( object ):
  def __init__( self, r, s ):
    self.r = r
    self.s = s
    
# === CLASS Point ===
class Point( object ):
  def __init__( self, curve, x, y, order = None ):
    self.__curve = curve
    self.__x = x
    self.__y = y
    self.__order = order
    if self.__curve: assert self.__curve.contains_point( x, y )
    if order: assert self * order == INFINITY
 
  def __add__( self, other ):
    if other == INFINITY: return self
    if self == INFINITY: return other
    assert self.__curve == other.__curve
    if self.__x == other.__x:
      if ( self.__y + other.__y ) % self.__curve.p() == 0:
        return INFINITY
      else:
        return self.double()

    p = self.__curve.p()
    l = ( ( other.__y - self.__y ) * \
          inverse_mod( other.__x - self.__x, p ) ) % p
    x3 = ( l * l - self.__x - other.__x ) % p
    y3 = ( l * ( self.__x - x3 ) - self.__y ) % p
    return Point( self.__curve, x3, y3 )

  def __mul__( self, other ):
    def leftmost_bit( x ):
      assert x > 0
      result = 1L
      while result <= x: result = 2 * result
      return result / 2

    e = other
    if self.__order: e = e % self.__order
    if e == 0: return INFINITY
    if self == INFINITY: return INFINITY
    assert e > 0
    e3 = 3 * e
    negative_self = Point( self.__curve, self.__x, -self.__y, self.__order )
    i = leftmost_bit( e3 ) / 2
    result = self
    while i > 1:
      result = result.double()
      if ( e3 & i ) != 0 and ( e & i ) == 0: result = result + self
      if ( e3 & i ) == 0 and ( e & i ) != 0: result = result + negative_self
      i = i / 2
    return result

  def __rmul__( self, other ):
    return self * other

  def __str__( self ):
    if self == INFINITY: return "infinity"
    return "(%d,%d)" % ( self.__x, self.__y )

  def double( self ):
    if self == INFINITY:
      return INFINITY

    p = self.__curve.p()
    a = self.__curve.a()
    l = ( ( 3 * self.__x * self.__x + a ) * \
          inverse_mod( 2 * self.__y, p ) ) % p
    x3 = ( l * l - 2 * self.__x ) % p
    y3 = ( l * ( self.__x - x3 ) - self.__y ) % p
    return Point( self.__curve, x3, y3 )

  def x( self ):
    return self.__x

  def y( self ):
    return self.__y

  def curve( self ):
    return self.__curve
  
  def order( self ):
    return self.__order
    
# === CLASS Public_Key ===
class Public_key( object ):
  def __init__( self, generator, point ):
    self.curve = generator.curve()
    self.generator = generator
    self.point = point
    n = generator.order()
    if not n:
      raise RuntimeError, "Generator point must have order."
    if not n * point == INFINITY:
      raise RuntimeError, "Generator point order is bad."
    if point.x() < 0 or n <= point.x() or point.y() < 0 or n <= point.y():
      raise RuntimeError, "Generator point has x or y out of range."

  def verifies( self, hash, signature ):
    G = self.generator
    n = G.order()
    r = signature.r
    s = signature.s
    if r < 1 or r > n-1: return False
    if s < 1 or s > n-1: return False
    c = inverse_mod( s, n )
    u1 = ( hash * c ) % n
    u2 = ( r * c ) % n
    xy = u1 * G + u2 * self.point
    v = xy.x() % n
    return v == r

# === CLASS Private_Key ===
class Private_key( object ):
  def __init__( self, public_key, secret_multiplier ):
    self.public_key = public_key
    self.secret_multiplier = secret_multiplier

  def der( self ):
    hex_der_key = '06052b8104000a30740201010420' + \
                  '%064x' % self.secret_multiplier + \
                  'a00706052b8104000aa14403420004' + \
                  '%064x' % self.public_key.point.x() + \
                  '%064x' % self.public_key.point.y()
    return hex_der_key.decode('hex')

  def sign( self, hash, random_k ):
    G = self.public_key.generator
    n = G.order()
    k = random_k % n
    p1 = k * G
    r = p1.x()
    if r == 0: raise RuntimeError, "amazingly unlucky random number r"
    s = ( inverse_mod( k, n ) * \
          ( hash + ( self.secret_multiplier * r ) % n ) ) % n
    if s == 0: raise RuntimeError, "amazingly unlucky random number s"
    return Signature( r, s )

# ===DEFINE SECP256-K1 ===
_p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2FL
_r = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141L
_b = 0x0000000000000000000000000000000000000000000000000000000000000007L
_a = 0x0000000000000000000000000000000000000000000000000000000000000000L
_Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798L
_Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8L

# === DECLARE STATICALS ===
INFINITY = Point( None, None, None )
curve_256 = CurveFp( _p, _a, _b )
generator_256 = Point( curve_256, _Gx, _Gy, _r )
g = generator_256

# === MAIN ===
if __name__ == "__main__":
  #generate()
  #import timeit
  #print(timeit.timeit("generate()", setup="from __main__ import generate",number=100))
  #print '======================================================================='
  
  for m in range (100):
     for n in range (100):
	  #loop=time.time()
	  generate(100)
          #print 'GenRate (Add/sec) : ',1/((time.time()-loop)/10)
  ### set privkey
  #secret = 0xC85AFBACCF3E1EE40BDCD721A9AD1341344775D51840EFC0511E0182AE92F78EL
  ### print privkey
  #print 'secret', hex(secret)

  #print 'btc_randpriv_ecdsa=', hex_64(secret)
  ### generate pubkey
  #pubkey = Public_key( g, g * secret )
  ### set pubkey
  #pubkey = Public_key(g, Point( curve_256, 0x40f9f833a25c725402e242965410b5bb992dc4fea1328681f0a74571c3104e36L,
  #                                         0x0882ea6ae14b6b1316e71e76cc51867cba20cafabd349753058b8c4677be50caL))
  ### print pubkey
  #print 'pubkey', hex(pubkey.point.x()), hex(pubkey.point.y())
  #btc_pubkey = hex_02(04)+ hex_64(pubkey.point.x())+hex_64(pubkey.point.y())
  #btc_pubkey_sha256=hashlib.sha256(btc_pubkey.decode('hex')).digest()
  #btc_pubkey_ripemd160=hash_160(btc_pubkey.decode('hex')).encode('hex')
  #netadd='00'+str(btc_pubkey_ripemd160)
  #netadd_sha256=hashlib.sha256(netadd.decode('hex')).digest()
  #netadd_sha256_256=hashlib.sha256(netadd_sha256).digest()
  #btcadd_hexa=netadd+str(netadd_sha256_256.encode('hex')[0:8])
  #btcadd=b58encode(btcadd_hexa.decode('hex'))
  
 
  #print 'btc_pubkey_as_hex=', btc_pubkey.decode('hex')
  #privkey = Private_key( pubkey, secret )
  
  # set hash
  #hash = randrange( 1, n )
  #hash = 0x0000000000000000000000000000000000000000000000000000000000000000L

  ### make signature on hash
  #signature = privkey.sign( hash, randrange( 1, n ) )
  ### set signature
  #signature = Signature(0x0000000000000000000000000000000000000000000000000000000000000000L,
  #                      0x0000000000000000000000000000000000000000000000000000000000000000L)
                        
  ### print signature
  #print 'signature', signature.r, signature.s


  #print '======================================================================='
  #print 'verifies', pubkey.verifies( hash, signature )
  #print '======================================================================='
  #btc_pubkey_sha256 = sha256()
  #btc_pubkey_sha256.update(btc_pubkey)
  #print 'btc_pubkey_sha256=', hashlib.sha256(btc_pubkey).digest()
  #print 'btc_ecdsa_pubkey=',btc_pubkey
  #print 'btc_ecdsa_pubkey_sha256=',btc_pubkey_sha256.encode('hex')
  #print 'btc_ecdsa_pubkey_sha256_ripemd160=',hash_160(btc_pubkey.decode('hex')).encode('hex')
  #print 'btc_ecdsa_pubkey_sha256_ripemd160_netadd=',netadd
  #print 'btc_ecdsa_pubkey_sha256_ripemd160_netadd_sha256=', netadd_sha256.encode('hex')
  #print 'btc_ecdsa_pubkey_sha256_ripemd160_netadd_sha256_sha256=',netadd_sha256_256.encode('hex')
  #print 'four-bytes=',netadd_sha256_256.encode('hex')[0:8]
  #print 'btcadd_hexa=',btcadd_hexa
  #print 'btcadd=',btcadd
