import tkinter as tk
from tkinter import ttk
import os
from tkinter import filedialog
from tkinter import messagebox

BACKEND_FOLDER = "F02_Backend"
DATASET_FOLDER = "F021_Dataset"

ORANGE = "#eb8c00"
LIGHT_ORANGE = "#ffc54b"
DARK_ORANGE = "#e18200"
WHITE = "#FFFFFF"
GREY = "#ededed"
DARK_GREY = "#767676"
RED = '#EE0000'
GREEN = '#008B00'
BLUE = '#1874CD'
YELLOW = '#FFFF00'


class FileStructure(tk.Frame):
    """
    A class that represents a frame containing a tree view file structure on a GUI

    ...

    Attributes
    ----------
    file_treeview : ttk.Treeview
        The tree view object
    tw : tk.Toplevel
        A toplevel window used as a tooltip
    path : str
        The current path leading to the opened dataset

    Methods
    -------
    askdirectory()
        Asks the user for a file path in which the dataset is contained and sets the root of the treeview to that path
    update_treeview()
        Updates the treeview object by reloading the data contained at the current path
    set_file_structure(parent, path)
        Inserts the files and folders contained at the given path recursively to the treeview object
    check_for_parents(child_iid, iids)
        Returns the parent node of a passed child node from the treeview object
    get_path()
        Returns the filepath of the currently selected item in the treeview object
    get_item()
        Returns the name of the item currently selected in the treeview object
    select_item_by_name(filename, item="")
        Selects the passed item in the treeview object
    add_treeview_bindings(treeview_object)
        Binds the events required to use drag and drop to the passed widget
    on_start()
        Creates the animation of the floating label of the Drag and Drop event
    on_drag()
        Updates the current coordinates of the floating label of the Drag and Drop event
    on_drop()
        Finds the widget under the cursor at the drop event and calls a further method
    get_cutout_path()
        Creates the constant path to store the cutout data
    """

    def __init__(self):
        super().__init__(highlightbackground="black", highlightthickness=1)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", background=LIGHT_ORANGE,
                        fieldbackground=LIGHT_ORANGE, foreground="black")

        self.file_treeview = ttk.Treeview(self)
        self.file_treeview.grid(column=0, row=0, sticky="NSWE")
        self.file_treeview.heading("#0", text="Datensatz öffnen", command=self.askdirectory, anchor="w")
        self.add_treeview_bindings(self.file_treeview)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.tw = None
        self.path = None

    def askdirectory(self):
        """
        Asks the user for a file path in which the dataset is contained and sets the root of the treeview to that path.


        """
        init_dir = os.path.join("C:\\", *os.getcwd().split("\\")[1:-1], BACKEND_FOLDER, DATASET_FOLDER)
        path = filedialog.askdirectory(initialdir=init_dir)

        if path:
            self.file_treeview.delete(*self.file_treeview.get_children())
            root_node = self.file_treeview.insert("", "end", text=f"{path}", open=True)
            self.set_file_structure(root_node, path)
            self.path = path
        else:
            pass

    def update_treeview(self):
        """
        Updates the treeview object by reloading the data contained at the current path.

        """
        self.file_treeview.delete(*self.file_treeview.get_children())
        root_node = self.file_treeview.insert("", "end", text=f"{self.path}", open=True)
        self.set_file_structure(root_node, self.path)

    def set_file_structure(self, parent, path):
        """
        Inserts the files and folders contained at the given path recursively to the treeview object.
        If the current path is a folder path, it is searched for further files.

        Parameter
        ---------
        parent : Any
            Parent node in the treeview object
        path : str
            The path to be searched for files
        """
        for file in os.listdir(path):
            abspath = os.path.join(path, file)
            isdir = os.path.isdir(abspath)
            oid = self.file_treeview.insert(parent, 'end', text=file, open=False)
            if isdir:
                self.set_file_structure(oid, abspath)

    def check_for_parents(self, child_iid, iids):
        """
        Returns the parent node of a passed child node from the treeview object.

        Parameter
        ---------
        child_iid : Any
            The iid of the child node whose parent node is to be searched for
        iids : list
            A list to be filled with all parent node iids found while searching for the passed child iid
            (lowest to highest node)
        """
        parent_iid = self.file_treeview.parent(child_iid)
        if parent_iid:
            iids.append(parent_iid)
            self.check_for_parents(parent_iid, iids)
        return iids

    def get_path(self):
        """
        Returns the filepath of the currently selected item in the treeview object.

        """
        path = ""
        item_iid = self.file_treeview.selection()[0]
        iids = [item_iid]
        self.check_for_parents(item_iid, iids)
        reordered_iids = [iids[i] for i in range(len(iids) - 1, -1, -1)]
        for iid in reordered_iids:
            filename = self.file_treeview.item(iid)["text"]
            path = os.path.join(path, filename)
        return path

    def get_item(self):
        """
        Returns the name of the item currently selected in the treeview object.

        """
        item_iid = self.file_treeview.selection()[0]
        item = self.file_treeview.item(item_iid)["text"]
        return item

    def select_item_by_name(self, filename, item=""):
        """
        Selects the passed item in the treeview object.

        Parameter
        ---------
        filename : str
            The filename to be searched for in the tree view items
        item : any
            The iid of the last node at which the filename was searched for
        """
        for iid in self.file_treeview.get_children(item):
            name = self.file_treeview.item(iid)["text"]
            if name == filename:
                parent = self.file_treeview.parent(iid)
                self.file_treeview.item(parent, open=True)
                self.file_treeview.selection_set(iid)
            else:
                self.select_item_by_name(filename, iid)

    def add_treeview_bindings(self, widget):
        """
        Binds the events required to use drag and drop to the passed widget.

        Parameter
        --------
        widget : any
            The tree view widget to which the events should be bound
        """
        widget.bind("<ButtonPress-1>", self.on_start)
        widget.bind("<B1-Motion>", self.on_drag)
        widget.bind("<ButtonRelease-1>", self.on_drop)
        widget.configure(cursor="hand2")

    def on_start(self, event):
        """
        Creates the animation of the floating label of the Drag and Drop event.
        The label is placed on a tkinter toplevel window. The shown text is equal to the selected filename in the
        tree view object.

        Parameter
        ---------
        event : any
            The Button press event which starts the drag and drop event

        """
        # Koordinaten des widgets an dem angezeigt werden soll (obere rechte Ecke)
        x, y = event.widget.winfo_pointerxy()
        self.tw = tk.Toplevel(self)
        # Toplevel Fenster ohne Rahmen anzeigen
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry(f'+{x}+{y}')

        iid = event.widget.identify_row(event.widget.winfo_pointerxy()[1]-event.widget.winfo_rooty())

        label = tk.Label(self.tw, text=f"{event.widget.item(iid)['text']}",
                         justify='left',
                         background="#D1EEEE",
                         borderwidth=1)
        label.grid(column=0, row=0, ipadx=1, ipady=1)

        self.tw.update()

    def on_drag(self, event):
        """
        Updates the current coordinates of the floating label of the Drag and Drop event.

        Parameter
        ---------
        event : any
            The motion event while moving the selection to the desired target
        """
        x, y = event.widget.winfo_pointerxy()
        self.tw.geometry(f"+{x + 5}+{y + 5}")

    def on_drop(self, event):
        """
        Finds the widget under the cursor at the drop event and calls a further method.
        The further method processes the passed information about the target and the item dropped at the target.

        Parameter
        ---------
        event : any
            The button release event to drop the selection at the desired target
        """
        x, y = event.widget.winfo_pointerxy()
        target = event.widget.winfo_containing(x, y)
        try:
            item_name = self.get_item()
            path = self.get_path()
            items = (item_name, path)
            self.master.active_frame.set_at_target(target, items)
        except IndexError:
            pass

        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()

    def get_cutout_path(self, kernel_size: str = "3x3"):
        """
        Creates the constant path to store the cutout data.

        Parameter
        ---------
        kernel_size : str
            The kernel size which defines the name of the folder to be created. It depends on which point cloud cutouts
            (of which size) are made in the GUI.
        """
        try:
            cutout_path = os.path.join(self.path, f"Cutout_{kernel_size}")

            if os.path.exists(cutout_path):
                return cutout_path
            else:
                os.mkdir(cutout_path)
                self.update_treeview()
                return cutout_path
        except Exception:
            messagebox.showerror("Kein Speicherpfad", "Es konnte kein Speicherpfad erstellt werden.")
            return None
