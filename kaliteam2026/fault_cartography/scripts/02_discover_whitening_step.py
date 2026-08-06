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

gdb.execute("continue")  # stop at handler entry, round 0
inferior = gdb.selected_inferior()
state_before = bytes(inferior.read_memory(base+0x4180, 48))
print("STATE BEFORE ROUND0 HANDLER:", state_before.hex())

gdb.execute("continue")  # should stop at bp_resume (0x1959) right after longjmp returns
pc = int(gdb.parse_and_eval("$pc"))
print("stopped at", hex(pc))
state_after = bytes(inferior.read_memory(base+0x4180, 48))
print("STATE AFTER ROUND0:", state_after.hex())

gdb.execute("detach")
gdb.execute("quit")
