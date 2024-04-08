import tkinter as tk
from tkinter import messagebox
import os

import matplotlib.pyplot as plt

from Toolbar import ToolBar
from W1_FileStructure import FileStructure


class Root(tk.Tk):
    """
    A class that represents the main window of a GUI

    ...

    Attributes
    ----------
    active_frame : None
        The frame currently displayed on the GUI
    toolbar : ToolBar
        ToolBar Object
    file_structure : FileStructure
        FileStructure Object


    Methods
    -------
    get_size(event)
        Returns the current size of the GUI when the event is activated
    show_frame(frame)
        Places the transferred frame on the GUI
    close()
        Shows closing query
    """

    def __init__(self):
        super().__init__()

        # -----------WINDOW-SETTINGS-------------
        self.title("Advanced Engineering - Gripping Direction Classifier")
        # 1250x550
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.iconbitmap(os.path.join(os.getcwd(), "Icon", "WeidmullerSymbol.ico"))

        # -----------FRAMES-------------
        self.active_frame = None
        self.toolbar = ToolBar(self)
        self.toolbar.grid(column=0, columnspan=2, row=0, sticky="NSWE")

        self.file_structure = FileStructure()
        self.file_structure.grid(column=0, row=1, sticky="NSWE")

        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=2)

        # self.bind("<Configure>", self.get_size)

    def get_size(self, event):
        """
        Returns the current size of the GUI when the event is activated.

        Parameters
        ----------
        event : Configure
            The event that activates the method
        """
        print(self.winfo_width())
        print(self.winfo_height())

    def show_frame(self, frame):
        """
        Places the transferred frame on the GUI.

        Parameters
        ----------
        frame : tk.Frame | tk.LabelFrame
        """
        if self.active_frame:
            del self.active_frame
        self.active_frame = frame
        self.active_frame.grid(column=1, row=1, pady=(0.2, 0), sticky="NSWE")

    def close(self):
        """
        Shows closing query.

        """
        event = messagebox.askquestion("Fenster schließen", "Wollen Sie die Anwendung beenden?")
        if event == "yes":
            self.quit()
        else:
            pass


if __name__ == "__main__":
    root = Root()
    root.mainloop()
