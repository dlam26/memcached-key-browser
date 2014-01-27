"""

    (eventually will) display easy point-and-click way GUI to view
    memcached key values!

    good reads:
        http://effbot.org/tkinterbook/
        http://effbot.org/tkinterbook/pack.htm
        http://effbot.org/tkinterbook/grid.htm


        Q. How to center a window on screen?
        A. http://stackoverflow.com/questions/14910858/


    TODO
        - show expiry timestamp formatted as a readable datetime!


"""


import Tkinter as tk
from ScrolledText import ScrolledText
import telnetlib
import time

USE_LISTBOX = True
"""http://effbot.org/tkinterbook/listbox.htm
   http://stackoverflow.com/questions/8647735/tkinter-listbox
"""

USE_GRID = False
"""http://effbot.org/tkinterbook/grid.htm"""

STATS_ITEM_HELP_MSG = """
Format:
    ITEM local:/the-sims-3/cheats/: [139428 b; 1377820642 s]
         <prefix>:<key> [<size> b;  <expiration timestamp> s]

"""

MEMCACHED_END = "END"

def format_epoch_timestamp(ts):
    return time.strftime('%m/%d/%Y %I:%M %p',  time.gmtime(float(ts)))

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
            tn.write("stats cachedump {0} {1}\r\n".format(slab_id, count))
            output += tn.read_until(MEMCACHED_END)


for i in range(3):      # print some horizontal separator bars
    print '=' * 80

print """
Epoch Time:  {0}

""".format(int(time.time()))

print STATS_ITEM_HELP_MSG

root = tk.Tk()
root.wm_title('Browsing keys in memcached at {0}:{1}'.format(tn.host, tn.port))
w, h, ws, hs = 1000, 750,  root.winfo_screenwidth(), root.winfo_screenheight()
x = (ws/2) - (w/2)   # find the x,y coordinates, of a centered point
y = (hs/2) - (h/2)
root.geometry('%dx%d+%d+%d' % (w, h, x, y))  # set dimensions of the screen and where it is placed

if USE_LISTBOX:
    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=tk.YES)
    listbox = tk.Listbox(frame)
    listbox.configure(background='HotPink1')
    listbox.pack(fill=tk.BOTH, expand=tk.YES)
    for i, line in enumerate(output.split("\n")):
        listbox.insert(i, line)

    scrollbar = tk.Scrollbar(listbox, orient=tk.VERTICAL)
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)  # moving one, moves the other

    def handleClick(event):  #   event is a tkinter.Event
#         index = listbox.curselection()
        index = event.widget.curselection()
        cachedump_line = listbox.get(index)

        toks = cachedump_line.split()
        try:
            if toks[0] == 'ITEM':
                key = toks[1]
                size_and_expiry = toks[2:]
                size = size_and_expiry[0]
                expiry = size_and_expiry[2]
                tn.write("get {0}\r\n".format(key))
                value = tn.read_until(MEMCACHED_END)
                print("*** value of key '{0}' which expires {1} is... {2}".format(
                      key, format_epoch_timestamp(expiry), value))
        except IndexError:
            pass

    listbox.bind('<<ListboxSelect>>', handleClick)


elif USE_GRID:
    for i, line in enumerate(output.split("\n")):
        tk.Label(root, text=line).grid(row=i, column=1)
else:
    #  http://stackoverflow.com/questions/17657212/how-to-code-the-tkinter-scrolledtext-module
    keys_display = ScrolledText(root, width=400, height=400,)
    keys_display.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
    keys_display.insert(tk.INSERT, output)



root.mainloop()
