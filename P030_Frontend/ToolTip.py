import tkinter as tk


class CustomToolTip:
    """
    A class that manages the test frame on the GUI.

    ...

    Attributes
    ----------
    waittime : int | float
        Waiting time until the tooltip opens
    widget : Any
        Widget on which the tooltip should be displayed
    text : str
        The text of the tooltip
    id : Any
        The id of the scheduled tooltip
    tw : Any
        The Toplevel window that contains the tooltip widgets

    Methods
    -------
    enter(event)
        Calls the schedule method. Is triggered when the mouse cursor enters the bound widget
    leave(event)
        Calls the unschedule and hide_tip methods. Is triggered when the mouse cursor leaves the bound widget.
    schedule()
        Schedules the current tooltip and sets the waiting time until the tip is displayed
    unschedule()
        Unschedule old tooltip objects by canceling them from waiting list
    showtip()
        Defines the destination of the toplevel window and displays it
    hidetip()
        Destroys the toplevel window after unschedule the tooltip
    """

    def __init__(self, widget, text):
        self.waittime = 500  # Millisekunden
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        """
        Calls the schedule method. Is triggered when the mouse cursor enters the bound widget

        """
        self.schedule()

    def leave(self, event=None):
        """
        Calls the unschedule and hide_tip methods. Is triggered when the mouse cursor leaves the bound widget.

        """
        self.unschedule()
        self.hidetip()

    def schedule(self):
        """
        Schedules the current tooltip and sets the waiting time until the tip is displayed

        """
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        """
        Unschedule old tooltip objects by canceling them from waiting list

        """
        old_id = self.id
        self.id = None
        if old_id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        """
        Defines the destination of the toplevel window and displays it

        """
        if self.id is not None:
            x = y = 0
            x += self.widget.winfo_rootx() + 20
            y += self.widget.winfo_rooty() + self.widget.winfo_height()
            self.tw = tk.Toplevel(self.widget)
            # Toplevel Fenster ohne Rahmen anzeigen
            self.tw.wm_overrideredirect(True)
            self.tw.wm_geometry(f'+{x}+{y}')
            label = tk.Label(self.tw, text=self.text,
                             justify='left',
                             background="#f6efb9",
                             relief='solid',
                             borderwidth=1)
            label.pack(ipadx=1, ipady=2)

            self.tw.update()

            if label.winfo_width() > self.tw.winfo_width():
                self.tw.geometry(f'{label.winfo_width()}x{label.winfo_height()}')

    def hidetip(self):
        """
        Destroys the toplevel window after unschedule the tooltip

        """
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()
