import tkinter as tk
import os
from PIL import Image, ImageTk
from W2_Labeling import LabelingFrame
from W3_Training import TrainingFrame
from W4_Test import TestFrame

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


class ToolBar(tk.Frame):
    """
    A class that represents a Toolbar

    Attributes
    ----------
    root : tk.Tk
        The main window on which the toolbar is placed
    images : dict
        A dictionary in which the image references are stored
    button_list : list
        A list in which the toolbars button widgets are stored
    labeling : tk.Button
        A Button to switch to a labeling frame
    training : tk.Button
        A Button to switch to a training frame
    test : tk.Button
        A Button to switch to a test frame

    Methods
    -------
    img_dict()
        Stores the image references to the images list
    change_button_color(active_button)
        Changes the button color of the currently activated (pressed) button.
    show_frame(var)
        Switches between the given frames by a passed variable
    """

    def __init__(self, root):
        """
        Parameters
        ----------
        root : tk.Tk
            The main window on which the toolbar is placed
        """
        super().__init__(root, highlightbackground="black", highlightthickness=1, bg=LIGHT_ORANGE)

        self.root = root

        self.images = self.img_dict()
        self.button_list = []

        self.labeling = tk.Button(self,
                                  text=" Labeling  |",
                                  relief=tk.FLAT,
                                  compound=tk.LEFT,
                                  image=self.images["Labeling"],
                                  cursor="hand2",
                                  command=lambda var="labeling": self.show_frame(var))
        self.labeling.grid(column=0, row=0)
        self.button_list.append(self.labeling)

        self.training = tk.Button(self,
                                  text=" Training  |",
                                  compound=tk.LEFT,
                                  relief=tk.FLAT,
                                  image=self.images["Train_Val"],
                                  command=lambda var="training": self.show_frame(var),
                                  cursor="hand2")
        self.training.grid(column=1, row=0)
        self.button_list.append(self.training)

        self.test = tk.Button(self,
                              text=" Test   ",
                              compound=tk.LEFT,
                              relief=tk.FLAT,
                              image=self.images["Train_Val"],
                              command=lambda var="test": self.show_frame(var),
                              cursor="hand2")
        self.test.grid(column=2, row=0)
        self.button_list.append(self.test)

        self.show_frame(var="labeling")

    @staticmethod
    def img_dict():
        """
        Stores the image references to the images list. The images are saved in a fixed path in the frontend folder.

        :return:
            A dictionary with image names as keys and associated image objects as values.

        """

        img_dict = {}
        for file in os.listdir(os.getcwd() + "\\Icon"):
            if file != "WeidmullerSymbol.ico":
                filename = file.split(".")[0]
                img = Image.open(os.getcwd() + "\\Icon\\" + file).resize((20, 20))
                img_dict[filename] = ImageTk.PhotoImage(img)
        return img_dict

    def change_button_color(self, active_button):
        """
        Changes the button color of the currently activated (pressed) button.

        Parameters
        ----------
        active_button : tk.Button
            The currently activated button object.

        """

        for button in self.button_list:
            if button != active_button:
                button.configure(background=LIGHT_ORANGE)
            else:
                button.configure(background=DARK_ORANGE)

    def show_frame(self, var):
        """
        Calls the root function to switch between the given frames by a passed variable.

        Parameters
        ----------
        var : str
            A variable that is assigned to the respective button. It is transferred when the button is pressed.
            The variable contains information about which frame should be displayed.

        """
        if var == "training":
            frame = TrainingFrame().show()
            self.change_button_color(self.training)
        elif var == "labeling":
            frame = LabelingFrame().show()
            self.change_button_color(self.labeling)
        elif var == "test":
            frame = TestFrame().show()
            self.change_button_color(self.test)

        self.root.show_frame(frame)
