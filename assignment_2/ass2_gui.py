import tkinter as tk
import ass2_base as base


class EntryGroup(tk.Frame):
    """
    Frame to contain a tk.Entry and label
    """
    def __init__(self, parent, label, width):
        super().__init__(parent)
        self.label = tk.Label(self, text=label)
        self.label.pack(side=tk.LEFT)

        self.entry = tk.Entry(self, width=width)
        self.entry.pack(side=tk.LEFT)

    def get(self):
        """
        returns the value
        :return: str
        """
        return self.entry.get()


class Toolbar(tk.Frame):
    """
    Toolbar for entering ip and host and pressing submit
    """
    def __init__(self, master, parent):
        super().__init__(master)
        self.relief = tk.RAISED

        self.dns = EntryGroup(self, "DNS Server: ", 30)
        self.dns.pack(side=tk.LEFT, padx=10)

        self.query = EntryGroup(self, "Query: ", 70)
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

    def submit(self):
        query = self.toolbar.query.get()
        dns = self.toolbar.dns.get()
        result = base.runner(dns, query)
        print(f"Host: {query}"
              f"\nIPv4: {result['ipv4']}")
        if "ipv6" in result:
            print(f"IPv6: {result['ipv6']}")


if __name__ == '__main__':
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()