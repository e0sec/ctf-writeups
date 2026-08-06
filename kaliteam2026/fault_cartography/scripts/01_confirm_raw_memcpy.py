import gdb
gdb.execute("set architecture i386:x86-64")
gdb.execute("target remote localhost:1234")
base = 0x4000000000
bp = base + 0x1494  # right after memcpy_chk call returns
gdb.execute("break *0x%x" % bp)
gdb.execute("continue")
inferior = gdb.selected_inferior()
state = bytes(inferior.read_memory(base+0x4180, 96))
print("STATE_AFTER_MEMCPY:", state.hex())
gdb.execute("detach")
gdb.execute("quit")
