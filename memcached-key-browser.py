"""

    (eventually will) display easy point-and-click way GUI to view
    memcached key values!

    good reads:

        http://effbot.org/tkinterbook/pack.htm

        Q. How to center a window on screen?
        A. http://stackoverflow.com/questions/14910858/

"""
from Tkinter import *
from ScrolledText import ScrolledText
import telnetlib

STATS_ITEM_HELP_MSG = """
Format:
    ITEM local:/the-sims-3/cheats/: [139428 b; 1377820642 s]
         <prefix>:<key> [<size> b;  <expiration timestamp> s]

"""

MEMCACHED_END = "END"
output = ''
tn = telnetlib.Telnet("localhost", 11211)
tn.write("stats items\r\n")
items = tn.read_until(MEMCACHED_END)
for line in items.split("\r\n"):
    if line != MEMCACHED_END:
        stat, slab, count = line.strip().split(' ')
        items, slab_id, stat_name = slab.split(':')
        if stat_name == 'number' and count > 0:
            output += '\n\n\t------------ Slab {0} -------------'.format(slab_id, count)
            tn.write("stats cachedump {0} {1}\r\n".format( slab_id, count))
            output += tn.read_until(MEMCACHED_END)

output = STATS_ITEM_HELP_MSG + output

for i in range(3):      # print some horizontal separator bars
    print '=' * 80
print STATS_ITEM_HELP_MSG

root = Tk()
w, h, ws, hs = 1000, 750,  root.winfo_screenwidth(), root.winfo_screenheight()

x = (ws/2) - (w/2)   # find the x,y coordinates, of a centered point
y = (hs/2) - (h/2)
root.geometry('%dx%d+%d+%d' % (w, h, x, y))  # set dimensions of the screen and where it is placed

#  http://stackoverflow.com/questions/17657212/how-to-code-the-tkinter-scrolledtext-module
keys_display = ScrolledText(root, width=400, height=400,)
keys_display.pack(side=LEFT, padx=5, pady=5, fill=BOTH, expand=True)
keys_display.insert(INSERT, output)

def callback():
    print "click!"
b = Button(root, text="OK", command=callback)
b.pack()

quit = Button(root, text='Quit')    # FIXME
quit.pack(side=RIGHT, anchor=NE)

root.mainloop()
