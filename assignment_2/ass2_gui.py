import tkinter as tk
import ass2_base as base
#Anthony Carrick

DNS_SERVERS = ["8.8.8.8", "9.9.9.9", "1.1.1.1", "130.102.71.160"]
QUERIES = ["abc.net.au", "microsoft.com", "eait.uq.edu.au",
           "remote.labs.eait.uq.edu.au", "130.102.79.33"]


class Presets(tk.Frame):
    """
    Frame to make preset buttons
    """
    def __init__(self, parent, buttons):
        super().__init__(parent)
        self._parent = parent
        for button in buttons:
            tk.Button(self, text=button,
                      command=lambda button = button: self.update_entry(button)).pack(
                side=tk.LEFT, expand=1)

    def update_entry(self, text):
        self._parent.set(text)


class EntryGroup(tk.Frame):
    """
    Frame to contain a tk.Entry and label
    """
    def __init__(self, parent, label, width, buttons):
        super().__init__(parent)

        self.entry_frame = tk.Frame(self)
        self.entry_frame.pack(side=tk.TOP)
        self.label = tk.Label(self.entry_frame, text=label)
        self.label.pack(side=tk.LEFT)

        self.entry = tk.Entry(self.entry_frame, width=width)
        self.entry.pack(side=tk.LEFT)

        self.buttons = Presets(self, buttons)
        self.buttons.pack(side=tk.TOP)

    def get(self):
        """
        returns the value
        :return: str
        """
        return self.entry.get()

    def set(self, string):
        """
        sets the value of the text box
        :return: 
        """
        self.entry.delete(0, tk.END)
        self.entry.insert(0, string)


class Toolbar(tk.Frame):
    """
    Toolbar for entering ip and host and pressing submit
    """
    def __init__(self, master, parent):
        super().__init__(master)
        self.relief = tk.RAISED

        self.dns = EntryGroup(self, "DNS Server: ", 30, DNS_SERVERS)
        # self.dns.buttons
        self.dns.pack(side=tk.LEFT, padx=10)

        self.query = EntryGroup(self, "Query: ", 70, QUERIES)
        self.query.pack(side=tk.LEFT, padx=10)

        self.submit_button = tk.Button(self, text="Send!", width=10, padx=10,
                                       command=parent.submit)
        self.submit_button.pack(side=tk.LEFT, padx=10)


class GUI(object):
    """
    Top Level thing
    """
    HEIGHT = 240
    WIDTH = 400

    def __init__(self, master):
        master.title("Anthony Carrick's DNS thing")
        self._master = master

        # add the toolbar
        self.toolbar = Toolbar(master, self)
        self.toolbar.pack(expand=0, fill=tk.X, padx=0)

        self.output_display = tk.Text(master)
        self.output_display.pack(side=tk.TOP, expand=1)

    def submit(self):
        self.output_display.delete(1.0, tk.END)
        query = self.toolbar.query.get()
        dns = self.toolbar.dns.get()
        result = base.runner(dns, query)
        self.output_display.insert(tk.END, result)


if __name__ == '__main__':
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()