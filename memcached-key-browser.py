"""

    (eventually will) display easy point-and-click way GUI to view
    memcached key values!


"""
import telnetlib
from Tkinter import *

MEMCACHED_END = "END"

output = ''
tn = telnetlib.Telnet("localhost", 11211)
tn.write("stats items\r\n")
items = tn.read_until(MEMCACHED_END)
for line in items.split("\n"):
    if line != MEMCACHED_END:
        stat, slab, count = line.strip().split(' ')
        items, slab_id, stat_name = slab.split(':')
        if stat_name == 'number' and count > 0:
            output += '\n\n\t------------ Slab {0} -------------'.format(slab_id, count)
            tn.write("stats cachedump {0} {1}\r\n".format( slab_id, count))
            output += tn.read_until(MEMCACHED_END)
print output

for i in range(3):      # print some horizontal separator bars
    print '=' * 80

print """
Format:

    ITEM local:/the-sims-3/cheats/: [139428 b; 1377820642 s]
         <prefix>:<key> [<size> b;  <expiration timestamp> s]
"""


root = Tk()

scrollbar = Scrollbar(root)
scrollbar.pack(side=RIGHT, fill=Y)
label = Label(root, text=output)                  # <-- works!
label.pack(side=RIGHT, expand=YES, fill=BOTH)


root.tkraise()          # <-- no working
root.mainloop()
