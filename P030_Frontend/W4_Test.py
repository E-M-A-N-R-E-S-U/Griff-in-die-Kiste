import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from threading import Thread
import matplotlib
import torch
from ToolTip import CustomToolTip
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from P020_Backend.P023_Model import Model
from P020_Backend.P021_Code.ResultPlots import TestResPlot


BACKEND_FOLDER = "F02_Backend"
DATASET_FOLDER = "F021_Dataset"
NETWORK_FOLDER = "F022_Network"


class TestFrame(tk.Frame):
    """
    A class that manages the test frame on the GUI.

    ...

    Attributes
    ----------
    options : Options
        An object of the Options class that represents the options label frame
    results : Results
        An object of the Results class that represents the results label frame

    Methods
    -------
    show()
        Returns the class instance so that the frame can be displayed on the main window
    set_at_target(target, items)
        Distributes the parameters transferred in a drop event to the respective class objects (label frames)
    """
    def __init__(self):
        super().__init__(highlightbackground="black", highlightthickness=1)

        self.options = Options(self)
        self.options.grid(column=0, row=0, padx=10, pady=10, sticky="NSWE")

        self.results = Results(self)
        self.results.grid(column=0, row=1, padx=10, pady=(0, 10), sticky="NSWE")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

    def show(self):
        """
        Returns the class instance so that the frame can be displayed on the main window

        """
        return self

    def set_at_target(self, target, items):
        """
        Distributes the parameters transferred in a drop event to the respective class objects (label frames)

        Parameter
        ---------
        target : Any
            The target widget
        items : Any
            The item dropped from the tree view

        """
        item, path = items
        try:
            target.textvar.set(item)
            target.path = path
            if target == self.options.en_features:
                self.options.set_label()
        except AttributeError:
            pass


class Options(tk.LabelFrame):
    """
    A class that manages the option menu widgets on the training frame

    ...

    Attributes
    ----------
    root : tk.Frame
        The root window/frame on which this frame is placed
    features : tk.StringVar
        A string variable with the name of the opened/dropped feature dataset
    en_features : tk.Entry
        An entry in which the feature dataset is dropped
    labels : tk.StringVar
        A string variable with the name of the opened/dropped results csv file
    en_labels : tk.Entry
        An entry in which the results csv file is dropped
    bt_start_test : tk.Button
        A button to start the test loop
    stop : tk.BooleanVar
        A variable to display the stop event of the test loop
    bt_stop_test : tk.Button
        A button to stop the test loop

    Methods
    -------
    set_label()
        Automatically fills the entry field for the result csv if the naming convention is adhered to
    stop_test()
        Sets the stop variable if the stop button is pressed
    check_entries()
        Checks whether something has been entered in both entry fields
    test()
        Starts the thread for the test loop
    test_model(memory_path, kernel_size)
        Starts the test loop
    disable_start_test()
        Disables the start test button
    enable_start_test()
        Enables the start test button

    """

    def __init__(self, root):
        """
        Parameter
        ---------
        root : tk.Frame
            The root frame on which this labeling frame is placed

        """
        super().__init__(master=root, text="Optionen")
        self.root = root

        self.features = tk.StringVar()
        self.features.set("Features Datensatz")
        self.en_features = tk.Entry(self, textvariable=self.features, state="readonly")
        self.en_features.textvar = self.features
        self.en_features.path = None
        self.en_features.grid(column=0, columnspan=2, row=0, padx=5, pady=5, sticky="NSWE")
        CustomToolTip(self.en_features, text="Einfügen des Ordners in dem die ausgeschnittenen\n"
                                             "Punktwolken liegen (per Drag and Drop).")

        self.labels = tk.StringVar()
        self.labels.set("Labels Datei")
        self.en_labels = tk.Entry(self, textvariable=self.labels, state="readonly")
        self.en_labels.textvar = self.labels
        self.en_labels.path = None
        self.en_labels.grid(column=2, columnspan=2, row=0, padx=5, pady=5, sticky="NSWE")
        CustomToolTip(self.en_labels, text="Einfügen der Label CSV-Datei (per Drag and Drop).")

        self.bt_start_test = tk.Button(self, text="Test starten", command=self.test)
        self.bt_start_test.grid(column=0, row=1, padx=(50, 25), pady=5, sticky="NSWE")

        self.stop = tk.BooleanVar()
        self.stop.set(False)
        self.bt_stop_test = tk.Button(self, text="Test stoppen", command=self.stop_test)
        self.bt_stop_test.grid(column=1, row=1, padx=(25, 50), pady=5, sticky="NSWE")

        self.columnconfigure("all", weight=1, uniform="cols")
        self.rowconfigure(0, weight=1, uniform="opt")
        self.rowconfigure(1, weight=1, uniform="opt")

    def set_label(self):
        """
        Automatically fills the entry field for the result csv if the naming convention is adhered to.
        Is triggered when the dataset entry field has been filled

        """
        try:
            for filename in os.listdir(self.en_features.path):
                if filename.endswith(".csv") and "Results_Labeled" in filename:
                    self.labels.set(filename)
                    path = os.path.join(self.en_features.path, filename)
                    self.en_labels.path = path
        except Exception:
            pass

    def stop_test(self):
        """
        Sets the stop variable if the stop button is pressed.

        """
        self.stop.set(True)

    def check_entries(self):
        """
        Checks whether something has been entered in both entry fields

        """
        if not self.en_features:
            return False
        if not self.en_labels:
            return False

        return True

    def test(self):
        """
        Starts the thread for the test loop

        """
        try:
            self.stop.set(False)

            basename = os.path.basename(self.en_features.path)
            if "Cutout" not in basename:
                raise Exception

            model = filedialog.askopenfilename(title="Modell auswählen")

            kernel_size = basename.split("_")[-1]

            # create training thread
            test_thread = Thread(daemon=True,
                                 target=lambda a=model, b=kernel_size: self.test_model(a, b))
            # start training thread
            test_thread.start()

        except Exception as test_exception:
            tk.messagebox.showerror("Fehler beim starten des Tests", "Beim starten des Tests ist ein "
                                                                     "Fehler aufgetreten: "
                                                                     ""
                                                                     f"{test_exception}")

    def test_model(self, model, kernel_size):
        """
        Starts the test loop

        Parameter
        ---------
        model : str
            Memory path of the model
        kernel_size : str
            Kernel size used to cut out the point clouds to be used for testing

        """
        self.root.master.config(cursor="watch")

        test_set = Model.PointCloudSet(self.en_labels.path, self.en_features.path, train=False)
        test_loader = Model.DataLoader(test_set, batch_size=1)

        self.root.master.config(cursor="")

        nn = Model.Network(kernel_size, model=model)

        nn.perform_test(test_loader, frame=self.root)

    def disable_start_test(self):
        """
        Disables the start test button

        """
        self.bt_start_test.configure(state="disabled")

    def enable_start_test(self):
        """
        Enables the start test button

        """
        self.bt_start_test.configure(state="normal")


class Results(tk.LabelFrame):
    """
    A class that manages the results frame on the GUI.

    ...

    Attributes
    ----------
    root : tk.Frame
        The root window/frame on which this frame is placed
    status : tk.StringVar
        A variable which contains information about the current test status
    lb_status_info : tk.Label
        A label which contains the text of the status variable
    pb_test_progress : ttk.Progressbar
        A progressbar showing the current test progress
    test_history : dict
        A dictionary containing the test data for the result plots
    result_plot : TestResPlot
        An object of the TestResPlot class which prepares and manages the result plots
    canvas : Any
        The canvas to display the result plots

    Methods
    -------
    clear_all()
        Clears the training history and plots
    set_status(text)
        Sets the passed text to the status variable
    reset_progress()
        Resets the progress bar
    update_progress(progress)
        Updates the progressbar to the passed progress value
    update_test_history(epoch, f1, accuracy, conf_matrix)
        Inserts the passed data to the test history and updates the result plots

    """

    def __init__(self, root):
        """
        Parameter
        ---------
        root : tk.Frame
            The root frame on which this labeling frame is placed

        """
        super().__init__(master=root, text="Ergebnisse")
        self.root = root

        self.result_plot = TestResPlot()
        fig = self.result_plot.get()
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.get_tk_widget().grid(column=0, columnspan=4, row=0, padx=5, pady=(10, 5), sticky="NSWE")
        self.canvas.draw()

        self.status = tk.StringVar()
        self.status.set("Kein Test gestartet")
        self.lb_status_info = tk.Label(self, textvariable=self.status)
        self.lb_status_info.grid(column=0, row=1, padx=5, pady=5, sticky="w")

        self.pb_test_progress = ttk.Progressbar(self, mode="determinate", orient="horizontal")
        self.pb_test_progress.grid(column=1, row=1, padx=20, pady=5, sticky="NSWE")

        self.columnconfigure("all", weight=1, uniform="cols")
        self.rowconfigure(0, weight=1)

        self.test_history = {"epochs": [],
                             "f1": [],
                             "accuracy": []}

    def clear_all(self):
        """
        Clears the training history and plots

        """
        for key in self.test_history.keys():
            self.test_history[key].clear()

        self.result_plot.clear()
        self.canvas.draw()

    def set_status(self, text):
        """
        Sets the passed text to the status variable

        """
        self.status.set(text)

    def reset_progress(self):
        """
        Resets the progress bar

        """
        self.pb_test_progress["value"] = 0
        self.pb_test_progress.update()

    def update_progress(self, progress):
        """
        Updates the progressbar to the passed progress value

        """
        self.pb_test_progress["value"] = progress
        self.pb_test_progress.update()

    def update_test_history(self, epoch, f1, accuracy, conf_matrix):
        """
        Inserts the passed data to the test history and updates the result plots

        Parameter
        ---------
        epoch : Any
            The current test epoch
        f1 : Any
            The current f1-score computed on the test data
        accuracy : Any
            The current accuracy computed on the test data
        conf_matrix : Any
            The current confusion matrix computed on the test data

        """
        self.test_history["epochs"].append(epoch)
        self.test_history["f1"].append(f1)
        self.test_history["accuracy"].append(accuracy)

        ep = self.test_history["epochs"]
        f1 = self.test_history["f1"]
        acc = self.test_history["accuracy"]
        self.result_plot.update(conf_matrix, acc, f1, ep)
        self.canvas.draw()
