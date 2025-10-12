import tkinter as tk
from tkinter.scrolledtext import ScrolledText

class GUI(tk.Tk):
    def __init__(self, config, client):
        tk.Tk.__init__(self)
        self.config = config
        self.client = client
        self.title(config["default"]["title"])
        self.protocol("WM_DELETE_WINDOW", self.client.exit)
        self.resizable(False, False)
        self.frame = tk.Frame(self)
        self.frame.pack(fill="both", expand=True)
        self.create_widgets(config)
        self.app_is_closing = False

    def create_widgets(self, config):
        bgcolor = config["default"]["bg"]
        fgcolor = config["default"]["fg"]
        fontname = config["default"]["fontname"]
        fontsize = int(config["default"]["fontsize"])
        self.chat_ta = ScrolledText(self.frame,
            width=80,
            height=30,
            wrap="word", 
            bg=bgcolor,
            fg=fgcolor,
            font=(fontname, fontsize)) 
        self.chat_ta.grid(row=0, column=0)
        self.chat_ta.bind("<Key>", self.handle_key_press)
        self.dm_ta = ScrolledText(self.frame,
            width=80,
            height=6,
            wrap="word",
            bg=bgcolor,
            fg=fgcolor,
            font=(fontname, fontsize))
        self.dm_ta.bind("<Return>", self.handle_return)
        self.dm_ta.grid(row=1, column=0)
        self.userlist_ys = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.userlist_ys.grid(row=0, column=2, rowspan=2, sticky="ns")
        self.userlist_xs = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.userlist_xs.grid(row=2, column=1, sticky="ew")
        self.userlist_lb = tk.Listbox(self.frame, bg=bgcolor, fg=fgcolor)
        self.userlist_lb.config(yscrollcommand=self.userlist_ys.set)
        self.userlist_lb.config(xscrollcommand=self.userlist_xs.set)
        self.userlist_ys.config(command=self.userlist_lb.yview)
        self.userlist_xs.config(command=self.userlist_lb.xview)
        self.userlist_lb.grid(column=1, row=0, rowspan=2, sticky="nsew")

    def handle_key_press(self, event):
        return "break"

    def handle_return(self, event):
        message = self.dm_ta.get("1.0", tk.END)
        if self.client.is_command(message):
            self.client.process_command(message)
        else:
            self.client.send_message(message)
        if not self.app_is_closing:
            self.dm_ta.delete("1.0", tk.END)
            return "break"

    def add_message(self, message):
        self.chat_ta.insert(tk.END, message)

    def clear_userlist(self):
        self.userlist_lb.delete(0, tk.END)

    def add_user(self, username):
        self.userlist_lb.insert(tk.END, username)
