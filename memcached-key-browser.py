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
        - make classes!

        - system clipboard?   Maybe see how IDLE does it cross platform!

            http://stackoverflow.com/questions/579687/how-do-i-copy-a-string-to-the-clipboard-on-windows-using-python/4203897#4203897


"""


import Tkinter as tk
from ScrolledText import ScrolledText
from sys import platform as _platform
import os
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

popups = list()

def format_epoch_timestamp(ts):
    return time.strftime('%m/%d/%Y %I:%M %p',  time.gmtime(float(ts)))


def clear_popups(foo=None):
    for p in popups:
        p.destroy()
    popups[:] = []      # clear the list!

def open_popup(with_this_text='', and_this_title=''):
    clear_popups()
    popup = tk.Toplevel()
    popup.title("c to close window")
    popup.bind('<c>', clear_popups)
    popups.append(popup)
    text_widget = tk.Text(popup, borderwidth=0)
    text_widget.insert(tk.INSERT, with_this_text)
    text_widget.grid(row=2, column=1)

    def copy_to_clipboard():
        # FIXME
        if _platform == 'darwin':
            cmd = u'echo %s | tr -d "\n" | pbcopy' % unicode(text_widget.selection_get())
#             print u'cmd: ' + unicode(cmd)
            os.system(cmd)
        else:
            # for some reason, the the basic tkinter clipboard interface
            # dosen't work on Mac 10.8!   See "Programming Python" pg. 537
            root.clipboard_clear()
            root.clipboard_append(text_widget.selection_get())

    tk.Label(popup, text=and_this_title, justify=tk.LEFT, anchor=tk.W).grid(row=1, column=1)
    tk.Button(popup, text='Close', command=popup.destroy).grid(row=1, column=2)
    tk.Button(popup, text='Copy', command=copy_to_clipboard).grid(row=1, column=3)



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
root.wm_title('Browsing keys in memcached at {0}:{1}   (press Q to quit)  '.format(tn.host, tn.port))
w, h, ws, hs = 1000, 750,  root.winfo_screenwidth(), root.winfo_screenheight()
x = (ws/2) - (w/2)   # find the x,y coordinates, of a centered point
y = (hs/2) - (h/2)
root.geometry('%dx%d+%d+%d' % (w, h, x, y))  # set dimensions of the screen and where it is placed


def jKey(event):
    print 'pressed letter j!'
root.bind('<j>', jKey)

def kKey(event):
    print 'pressed letter k!'
root.bind('<k>', kKey)

def quit(event):
    root.quit()
root.bind('<Q>', quit)

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
                open_popup(value.decode('unicode-escape'),
                           'Expires ' + format_epoch_timestamp(expiry))

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
