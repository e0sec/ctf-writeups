import gdb
gdb.execute("set architecture i386:x86-64")
gdb.execute("target remote localhost:1234")
gdb.execute("handle SIGSEGV nostop noprint pass")
gdb.execute("handle SIGILL nostop noprint pass")
gdb.execute("handle SIGFPE nostop noprint pass")
base = 0x4000000000

bp_handler = base + 0x1ae0
bp_resume = base + 0x1959

gdb.execute("break *0x%x" % bp_handler)
gdb.execute("break *0x%x" % bp_resume)

inferior = gdb.selected_inferior()

for i in range(8):
    gdb.execute("continue")  # stop at handler entry
    pc = int(gdb.parse_and_eval("$pc"))
    fields = bytes(inferior.read_memory(base+0x4150, 24))
    print("ROUND", i, "entry pc", hex(pc), "fields", fields.hex())
    gdb.execute("continue")  # stop at resume (after mutation)
    pc2 = int(gdb.parse_and_eval("$pc"))
    state = bytes(inferior.read_memory(base+0x4180, 48))
    print("ROUND", i, "resume pc", hex(pc2), "state_after", state.hex())

gdb.execute("detach")
gdb.execute("quit")
