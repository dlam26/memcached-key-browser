"""

    (eventually will) display easy point-and-click way GUI to view
    memcached key values!

    good reads:
        http://effbot.org/tkinterbook/
        http://effbot.org/tkinterbook/pack.htm
        http://effbot.org/tkinterbook/grid.htm
        http://effbot.org/tkinterbook/listbox.htm
       http://stackoverflow.com/questions/8647735/tkinter-listbox

        Q. How to center a window on screen?
        A. http://stackoverflow.com/questions/14910858/


    TODO
        - make classes!

        - system clipboard?   Maybe see how IDLE does it cross platform!

            http://stackoverflow.com/questions/579687/how-do-i-copy-a-string-to-the-clipboard-on-windows-using-python/4203897#4203897

    FIXME
        - if a key value has the string 'END' anywhere, the
          displayed value will be truncated where it does
          'tn.read_until(MEMCACHED_END)'

"""
global listbox

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk   # python 3
# from ScrolledText import ScrolledText
from _socket import error as socketerror
from sys import platform as _platform
import os
import pickle
import sys
import telnetlib
import time

STATS_ITEM_HELP_MSG = """
Format:
    ITEM local:/the-sims-3/cheats/: [139428 b; 1377820642 s]
         <prefix>:<key> [<size> b;  <expiration timestamp> s]

"""

MEMCACHED_END = "END"
popups = list()

try:
    tn = telnetlib.Telnet("localhost", 11211)
except socketerror:
    print('ERROR:  Memcached must be running on port 11211!')
    sys.exit(1)


def format_epoch_timestamp(ts):
    return time.strftime('%m/%d/%Y %I:%M %p',  time.gmtime(float(ts)))

def clear_popups(foo=None):
    for p in popups:
        p.destroy()
    popups[:] = []      # clear the list!

def open_popup(with_this_text='', and_this_title=''):
    """Opens tkinter Toplevel widget containing given text and title!"""
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
            os.system(cmd)
        else:
            # for some reason, the the basic tkinter clipboard interface
            # dosen't work on Mac 10.8!   See "Programming Python" pg. 537
            root.clipboard_clear()
            root.clipboard_append(text_widget.selection_get())

    tk.Label(popup, text=and_this_title, justify=tk.LEFT, anchor=tk.W).grid(row=1, column=1)
    tk.Button(popup, text='Close', command=popup.destroy).grid(row=1, column=2)
    tk.Button(popup, text='Copy', command=copy_to_clipboard).grid(row=1, column=3)

def refresh_stats_items_listbox():
    listbox.delete(0, tk.END)

    output = ''
    tn.write("stats items\r\n")
    items = tn.read_until(MEMCACHED_END)
    try:
        for line in items.split("\r\n"):
            if line and line != MEMCACHED_END:
                stat, slab, count = line.strip().split(' ')
                items, slab_id, stat_name = slab.split(':')
                if stat_name == 'number' and count > 0:
                    output += '\n\n\t------------ Slab {0} -------------'.format(slab_id, count)
                    tn.write("stats cachedump {0} {1}\r\n".format(slab_id, count))
                    output += tn.read_until(MEMCACHED_END)

        for i, line in enumerate(output.split("\n")):
            if MEMCACHED_END != line:
                listbox.insert(i, line)
    except Exception as exc:
        print 'Arg! got stack!  {0!r}'.format(exc)


for i in range(3):      # print some horizontal separator bars
    print('=' * 80)
print ("""
Epoch Time:  {0}

{1}
""".format(int(time.time()), STATS_ITEM_HELP_MSG))

root = tk.Tk()
root.wm_title('Browsing keys in memcached at {0}:{1}   (press Q to quit)  '.format(tn.host, tn.port))
w, h, ws, hs = 1000, 700,  root.winfo_screenwidth(), root.winfo_screenheight()
x = (ws/2) - (w/2)   # find the x,y coordinates, of a centered point
y = (hs/2) - (h/2)
root.geometry('%dx%d+%d+%d' % (w, h, x, y))  # set dimensions of the screen and where it is placed

# add a menu bar!
menu = tk.Menu(root)
root.config(menu=menu)
toolsmenu = tk.Menu(menu)
menu.add_cascade(label="Tools", menu=toolsmenu)
toolsmenu.add_command(label="Refresh", command=refresh_stats_items_listbox)


def jKey(event):
    print('pressed letter j!')
root.bind('<j>', jKey)

def kKey(event):
    print('pressed letter k!')
root.bind('<k>', kKey)

def quit(event):
    root.quit()
root.bind('<Q>', quit)

# ...now build the UI!

key_browser = tk.PanedWindow(master=root, orient=tk.VERTICAL)
key_browser.pack(fill=tk.BOTH, expand=tk.YES)

list_of_keys_frame = tk.Frame(root)
list_of_keys_frame.pack(fill=tk.BOTH, expand=tk.YES)
listbox = tk.Listbox(list_of_keys_frame)
listbox.configure(background='HotPink1')
listbox.pack(fill=tk.BOTH, expand=tk.YES)
refresh_stats_items_listbox()

# Make list of keys 70% of the screen!
# Also .winfo_height() can return 1, so that's why we call update_idletasks()
# http://effbot.org/tkinterbook/widget.htm#Tkinter.Widget.winfo_height-method
root.update_idletasks()
key_browser.add(list_of_keys_frame, height=root.winfo_height() * 0.70)

value_display = tk.Text(key_browser, background='Orange')
value_display.insert(tk.INSERT, 'Clicking on a key above ^ and its value '
                     'will will display here.')
key_browser.add(value_display)

scrollbar = tk.Scrollbar(listbox, orient=tk.VERTICAL)
scrollbar.config(command=listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
listbox.config(yscrollcommand=scrollbar.set)  # moving one, moves the other

def try_unpickle(val):
    """Return python object stored as a bytestring in memcached!

    >>> val_from_memcached = '\r\nVALUE :1:dadict 1 58\r\n\x80\x02}q\x01(U\x08lastnameq\x02U\x03Lamq\x03U\x03ageq\x04K\x1eU\tfirstnameq\x05U\x05Davidq\x06u.\r'
    >>> try_unpickle(val_from_memcached)
    {'lastname': 'Lam', 'age': 30, 'firstname': 'David'}
    """
    try:
        return (True, pickle.loads(val.split('\r\n')[-2]))
    except:
        return (False, val)

def selectedKey(event):
    """Display value of key in memcached!

    'event' is a tkinter.Event
    """
    value_display.delete("1.0", tk.END)   # clear the display
    index = event.widget.curselection()
    toks = listbox.get(index).split()
    try:
        if toks[0] == 'ITEM':
            key = toks[1]
            size_and_expiry = toks[2:]
            size = size_and_expiry[0]
            expiry = size_and_expiry[2]
            tn.write("get {0}\r\n".format(key))
            val = tn.read_until(MEMCACHED_END)
            was_python_object, val = try_unpickle(val)
#             print("*** value of key '{0}' of size {1} which expires {2} is... {3}".format(key, size[1:], format_epoch_timestamp(expiry), val))

            if was_python_object:
                value_display.insert(tk.INSERT, 'Got python object!  '
                    'Type: ' + str(type(val)) + '\n\n\t' + str(val))
            else:
                val = val.decode('unicode-escape')
                # get rid of the memcached response VALUE / END pair
                val = ''.join(val.split('\r\n')[2:-1])
                value_display.insert(tk.INSERT, val)

#           open_popup(value_escaped, 'Expires ' + format_epoch_timestamp(expiry))

    except IndexError:
        pass

listbox.bind('<<ListboxSelect>>', selectedKey)
tk.mainloop()
