import os
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
from threading import Thread
from ToolTip import CustomToolTip
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from P020_Backend.P023_Model import Model
from P020_Backend.P021_Code.ResultPlots import TrainingResPlot


BACKEND_FOLDER = "F02_Backend"
DATASET_FOLDER = "F021_Dataset"
NETWORK_FOLDER = "F022_Network"


class TrainingFrame(tk.Frame):
    """
    A class that manages the training frame on the GUI.

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
    bt_start_training : tk.Button
        A button to start the training loop
    stop : tk.BooleanVar
        A variable to display the stop event of the training loop
    bt_stop_training : tk.Button
        A button to stop the training loop

    Methods
    -------
    set_label()
        Automatically fills the entry field for the result csv if the naming convention is adhered to
    stop_training()
        Sets the stop variable if the stop button is pressed
    check_entries()
        Checks whether something has been entered in both entry fields
    train()
        Starts the thread for the training loop
    train_model(memory_path, kernel_size)
        Starts the training loop
    disable_start_training()
        Disables the start training button
    enable_start_training()
        Enables the start training button

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
        self.features.set("Feature Datensatz")
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

        self.bt_start_training = tk.Button(self, text="Training starten", command=self.train)
        self.bt_start_training.grid(column=0, row=1, padx=(50, 25), pady=5, sticky="NSWE")

        self.stop = tk.BooleanVar()
        self.stop.set(False)
        self.bt_stop_training = tk.Button(self, text="Training stoppen", command=self.stop_training)
        self.bt_stop_training.grid(column=1, row=1, padx=(25, 50), pady=5, sticky="NSWE")

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

    def stop_training(self):
        """
        Sets the stop variable if the stop button is pressed.

        """
        self.stop.set(True)

    def check_entries(self):
        """
        Checks whether something has been entered in both entry fields.

        """
        if not self.en_features:
            return False
        if not self.en_labels:
            return False

        return True

    def train(self):
        """
        Starts the thread for the training loop. First gets the memory path for the model and the kernel size to
        select the correct model type.

        """
        try:
            self.stop.set(False)

            basename = os.path.basename(self.en_features.path)
            if "Cutout" not in basename:
                raise Exception

            memory_path = filedialog.askdirectory(title="Modelle Speicherpfad")

            kernel_size = basename.split("_")[-1]

            thread = Thread(daemon=True,
                            target=lambda a=memory_path, b=kernel_size: self.train_model(a, b))
            thread.start()

        except Exception as train_exception:
            print(train_exception.with_traceback())
            tk.messagebox.showerror("Fehler beim starten des Trainings", "Beim starten des Trainings ist ein "
                                                                         "Fehler aufgetreten: "
                                                                         ""
                                                                         f"{train_exception}")

    def train_model(self, memory_path, kernel_size):
        """
        Starts the training loop.

        Parameter
        ---------
        memory_path : str
            Memory path for the model
        kernel_size : str
            Kernel size used to cut out the point clouds to be used for training

        """
        self.root.results.tb_console.insert(tk.END, "Vorbereiten der Feature Dateien \n")
        self.root.master.config(cursor="watch")

        training_set = Model.PointCloudSet(self.en_labels.path, self.en_features.path)

        training_set, valid_set = Model.random_split(training_set, [0.8, 0.2])

        train_loader = Model.DataLoader(training_set, batch_size=10, shuffle=True)
        valid_loader = Model.DataLoader(valid_set, batch_size=len(valid_set))

        self.root.master.config(cursor="")

        nn = Model.Network(kernel_size)

        nn.perform_training(train_loader, valid_loader, frame=self.root, memory_path=memory_path)

    def disable_start_training(self):
        """
        Disables the start training button

        """
        self.bt_start_training.configure(state="disabled")

    def enable_start_training(self):
        """
        Enables the start training button

        """
        self.bt_start_training.configure(state="normal")


class Results(tk.LabelFrame):
    """
    A class that manages the results frame on the GUI.

    ...

    Attributes
    ----------
    root : tk.Frame
        The root window/frame on which this frame is placed
    tb_console : ScrolledText
        The console in which the training results are written
    status : tk.StringVar
        A variable which contains information about the current training status
    lb_status_info : tk.Label
        A label which contains the text of the status variable
    pb_training_progress : ttk.Progressbar
        A progressbar showing the current training progress
    training_history : dict
        A dictionary containing the training data for the result plots
    result_plot : TrainingResPlot
        An object of the TrainingResPlot class which prepares and manages the result plots
    canvas : Any
        The canvas to display the result plots

    Methods
    -------
    clear_all()
        Clears the training history, console and plots
    set_status(text)
        Sets the passed text to the status variable
    update_progress(progress)
        Updates the progressbar to the passed progress value
    update_console(message)
        Inserts the passed message to the console
    update_training_history(loss, train_accuracy, valid_accuracy)
        Inserts the passed data to the training history and updates the result plots

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

        self.tb_console = ScrolledText(self, height=21)
        self.tb_console.insert(tk.END, "TRAININGSERGEBNISSE: \n")
        self.tb_console.insert(tk.END, "-----------------------------------------------"
                                       "--------------\n")
        self.tb_console.grid(column=0, columnspan=2, row=0, rowspan=2, padx=5, pady=10, sticky="NSWE")

        self.status = tk.StringVar()
        self.status.set("Kein Training gestartet")
        self.lb_status_info = tk.Label(self, textvariable=self.status)
        self.lb_status_info.grid(column=0, row=2, padx=5, pady=5, sticky="w")

        self.pb_training_progress = ttk.Progressbar(self, mode="determinate", orient="horizontal")
        self.pb_training_progress.grid(column=1, row=2, padx=20, pady=5, sticky="NSWE")

        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.training_history = {"train_accuracy": [],
                                 "valid_accuracy": []}

        self.result_plot = TrainingResPlot()
        fig = self.result_plot.get()
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.get_tk_widget().grid(column=2, row=0, padx=5, pady=(10, 5), sticky="NSWE")

    def clear_all(self):
        """
        Clears the training history, console and plots.

        """
        for key in self.training_history.keys():
            self.training_history[key].clear()

        self.tb_console.delete(1.0, tk.END)

        self.result_plot.clear()
        self.canvas.draw()

    def set_status(self, text):
        """
        Sets the passed text to the status variable.

        Parameter
        --------
        text : str
            The text to be displayed

        """
        self.status.set(text)

    def update_progress(self, progress):
        """
        Updates the progressbar to the passed progress value

        Parameter
        ---------
        progress : Any
            The update value (progress)

        """
        self.pb_training_progress["value"] = progress
        self.pb_training_progress.update()

    def update_console(self, message):
        """
        Inserts the passed message to the console.

        Parameter
        --------
        message : str
            The message to display on the console

        """
        self.tb_console.insert(tk.END, message)
        self.tb_console.insert(tk.END, "\n")
        self.tb_console.see(tk.END)

    def update_training_history(self, loss, train_accuracy, valid_accuracy):
        """
        Inserts the passed data to the training history and updates the result plots

        Parameter
        ---------
        loss : Any
            The current loss history
        train_accuracy : Any
            The current accuracy computed on the training data
        valid_accuracy : Any
            The current accuracy computed on the validation data

        """
        self.training_history["train_accuracy"].append(train_accuracy)
        self.training_history["valid_accuracy"].append(valid_accuracy)

        tacc = self.training_history["train_accuracy"]
        vacc = self.training_history["valid_accuracy"]
        self.result_plot.update(tacc, vacc, loss)
        self.canvas.draw()
