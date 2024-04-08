import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from P020_Backend.P021_Code import CloudProcessing
from P020_Backend.P021_Code import CloudPlots
from P020_Backend.P021_Code.LabelingResults import ResultsDataFrame
from ToolTip import CustomToolTip
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk


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

OPEN_CLOUD = False


class LabelingFrame(tk.Frame):
    """
    A class that manages the GUI labeling frame.

    ...

    Attributes
    ----------
    point_cloud_display : PointCloud
        An object of the PointCloud class that represents the point cloud labeling frame
    selection_options : SelectionOptions
        An object of the SelectionOptions class that represents the labeling options label frame

    Methods
    -------
    show()
        Returns the class instance so that the frame can be displayed on the main window
    set_at_target(target, items)
        Distributes the parameters transferred in a drop event to the respective class objects (label frames)
    """

    def __init__(self):
        super().__init__(highlightbackground="black", highlightthickness=1)

        self.point_cloud_display = PointCloud(self)
        self.point_cloud_display.grid(row=0, column=0, columnspan=2, rowspan=2, padx=5, pady=10, sticky="NSWE")

        self.selection_options = SelectionOptions(self)
        self.selection_options.grid(row=0, column=2, padx=(5, 10), pady=10, sticky="NSWE")

        self.labeling_options = LabelingOptions(self)
        self.labeling_options.grid(row=1, column=2, padx=10, pady=(5, 10), sticky="NSWE")

        self.rowconfigure(0, weight=1, uniform='row')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1, uniform='row')
        self.columnconfigure(1, weight=1)

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
        global OPEN_CLOUD
        try:
            if target == self.point_cloud_display or target == self.point_cloud_display.canvas.get_tk_widget():
                item, path = items
                if "Cutout" in item:
                    self.labeling_options.release()
                    filename = os.path.splitext(item)[0]
                    kernel_size = filename.split("_")[-1]
                    dirname = os.path.dirname(path)
                    results_df = ResultsDataFrame(dirname, kernel_size)
                    label = results_df.get_label(item)
                    self.labeling_options.set_label(label)
                    self.point_cloud_display.cutout.set(True)
                    self.selection_options.save_result_bt.configure(state="normal")
                else:
                    self.point_cloud_display.cutout.set(False)
                    self.labeling_options.set_label(label=None)
                    self.labeling_options.disable()
                    self.selection_options.save_result_bt.configure(state="disabled")

                self.point_cloud_display.cloud.set(path)
                self.selection_options.file_name.set(item)
                self.point_cloud_display.reset_variables()
                self.point_cloud_display.show_plot()
                self.selection_options.status.set("Nicht gespeichert")
                OPEN_CLOUD = True
        except AttributeError:
            pass


class SelectionOptions(tk.LabelFrame):
    """
    A class that manages the selection menu widgets on the labeling frame

    ...

    Attributes
    ----------
    root : tk.Frame
        The root window/frame on which this frame is placed
    kernel_lb : tk.Label
        A label with the info text about the kernel size
    kernel_cbb : ttk.Combobox
        A combobox containing the kernel size selection parameters
    pc_info_lb : tk.Label
        A label with the info text about the currently open point cloud file
    file_name : tk.StringVar
        A string variable with the name of the opened point cloud file
    pc_file_name_lb : tk.Label
        A label containing the file_name attribute
    save_result_bt : tk.Button
        A button to save the labeling results
    status : tk.StringVar
        A string variable with the memory status
    status_lb : tk.Label
        A label containing the status attribute


    Methods
    -------
    combobox_event(event)
        Manages the processes triggered by the combobox selection event
    save_result()
        Manages the processes to save the current labeling result to the results csv

    """

    def __init__(self, root):
        """
        Parameter
        ---------
        root : tk.Tk
            The root window/frame on which this frame is placed
        """
        super().__init__(root, text="Optionen", padx=5, pady=5)
        self.root = root

        # -----------KERNEL-WIDGETS------------
        kernel_sizes = ["3x3", "5x5"]
        self.kernel_lb = tk.Label(self, text="Kernel Größe: ", justify="left", anchor="w")
        self.kernel_lb.grid(column=0, row=0, padx=5, pady=10, sticky="NSWE")
        self.kernel_cbb = ttk.Combobox(self, values=kernel_sizes, state="readonly", exportselection=True)
        self.kernel_cbb.bind("<<ComboboxSelected>>", self.combobox_event)
        self.kernel_cbb.current(0)
        self.kernel_cbb.grid(column=1, row=0, pady=10, sticky="NSWE")

        # -----------INFO-WIDGETS------------
        self.pc_info_lb = tk.Label(self, text="Geöffnete Punktwolke: ", justify="left", anchor="w")
        self.pc_info_lb.grid(column=0, row=1, padx=5, pady=10, sticky="NSWE")
        self.file_name = tk.StringVar()
        self.pc_file_name_lb = tk.Label(self, textvariable=self.file_name, justify="left", anchor="w")
        self.pc_file_name_lb.grid(column=1, row=1, pady=10, sticky="NSWE")

        # -----------ZU-CSV-BUTTON-------------
        self.save_result_bt = tk.Button(self, text="Ergebnis Speichern", command=self.save_result, state="disabled")
        self.save_result_bt.grid(column=0, row=2, padx=10, pady=10, sticky="NSWE")
        self.status = tk.StringVar()
        self.status.set("Nicht gespeichert")
        self.status_lb = tk.Label(self, textvariable=self.status)
        self.status_lb.grid(column=1, row=2, padx=5, sticky="NSWE")

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def combobox_event(self, event):
        """
        Manages the processes triggered by the combobox selection event. It resets the display so that the user
        is able to label the currently opened point cloud with respect to the newly selected kernel size.

        Parameter
        ---------
        event : Any
            The bound combobox selection event
        """
        if OPEN_CLOUD:
            self.save_result_bt.configure(state="disabled")
            self.root.labeling_options.disable()
            self.root.point_cloud_display.cutout.set(False)
            self.root.point_cloud_display.cloud.set()
            self.root.point_cloud_display.show_plot()

    def save_result(self):
        """
        Manages the processes to save the current labeling result to the results csv. It gets the path rooting to the
        cutout file with respect to the kernel size, saves the currently labeled point cloud file at that path and
        saves the labeling results in the results csv file.

        """
        cutout_dir = self.root.master.file_structure.get_cutout_path(self.kernel_cbb.get())
        if cutout_dir:
            filename = self.file_name.get()
            if "Cutout" not in filename:
                filename = filename.split(".")
                filename = f"{filename[0]}_Cutout_{self.kernel_cbb.get()}.csv"
            self.root.point_cloud_display.cloud.save_pcd(cutout_dir, filename)
            label = self.root.labeling_options.get_label()
            offsets = self.root.point_cloud_display.get_zero_offsets()
            results_df = ResultsDataFrame(cutout_dir, self.kernel_cbb.get())
            results_df.append_result(filename, label, offsets)
            results_df.to_csv()
            self.root.master.file_structure.update_treeview()
            self.root.master.file_structure.select_item_by_name(self.file_name.get())
            self.status.set("Gespeichert")


class LabelingOptions(tk.LabelFrame):
    """
    A class that manages the labeling button on the labeling frame

    ...

    Attributes
    ----------
    root : tk.Frame
        The root frame on which this labeling frame is placed
    frame_for_button : tk.Frame
        The frame in which the buttons are placed
    arrow_button : dict
        A dictionary containing the labeling button objects as values and their label as keys
    labeling_reference_list : list
        A list containing the button label
    object_la : tk.Label
        A label which displays the gripping object in the center of the labeling button

    Methods
    -------
    set_button(button)
        Changes the background color of the currently pressed labeling button (triggered by button press event)
    get_label()
        Returns a dictionary containing the button label as keys and the one hot encoded selection as values
    set_label(label)
        Changes the background color of the labeling button with respect to the registered results in the results csv
        (triggered if an already labeld point cloud is opened again on the GUI)
    release()
        Releases all labeling button so that they can be pressed
    disable()
        Disables all labeling button so that they can not be pressed

    """

    IMAGE_REFERENCES = {}

    def __init__(self, root):
        """
        Parameter
        ---------
        root : tk.Frame
            The root frame on which this labeling frame is placed

        """
        super().__init__(root, padx=5, pady=5, text="Labeling")

        self.root = root

        # -----------ARROW-BUTTON-------------
        self.frame_for_button = tk.Frame(self)
        self.frame_for_button.grid(row=0, column=0, padx=5, pady=5, sticky="NSEW")
        self.arrow_button = {}
        self.labeling_reference_list = []
        path_to_images = os.path.join(os.getcwd(), "Images")
        for image_name in os.listdir(path_to_images):
            row, col, image = tuple(image_name.split("_"))
            image_of_arrow = Image.open(os.path.join(path_to_images, image_name))
            image_of_arrow.thumbnail((50, 50), Image.LANCZOS)
            photo_of_image = ImageTk.PhotoImage(image_of_arrow)
            LabelingOptions.IMAGE_REFERENCES[image_name.split(".")[0]] = photo_of_image
            self.arrow_button[image.lower().split(".")[0]] = tk.Button(self.frame_for_button,
                                                                       image=photo_of_image,
                                                                       width=120,
                                                                       height=70,
                                                                       bg='white',
                                                                       command=lambda name=image.lower().split(".")[0]: self.set_button(button=name),
                                                                       state="disabled")
            self.arrow_button[image.lower().split(".")[0]].grid(column=int(col), row=int(row), sticky="NSWE")
            self.labeling_reference_list.append(image.lower().split(".")[0])
        self.object_la = tk.Label(self.frame_for_button, bg="black")
        self.object_la.grid(column=1, row=1, sticky="NSWE")

        self.frame_for_button.columnconfigure(0, weight=1)
        self.frame_for_button.rowconfigure(0, weight=1)
        self.frame_for_button.columnconfigure(1, weight=1)
        self.frame_for_button.rowconfigure(1, weight=1)
        self.frame_for_button.columnconfigure(2, weight=1)
        self.frame_for_button.rowconfigure(2, weight=1)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def set_button(self, button):
        """
        Changes the background color of the currently pressed labeling button (triggered by button press event)

        Parameter
        --------
        button : str
            Label of the pressed button

        """
        for button_name in self.labeling_reference_list:
            if button_name != button:
                self.arrow_button[button_name]["bg"] = "white"

        state = str(self.arrow_button[button]["bg"])
        if state == "white":
            self.arrow_button[button]["bg"] = DARK_ORANGE
        else:
            self.arrow_button[button]["bg"] = "white"

    def get_label(self):
        """
        Returns a dictionary containing the button label as keys and the one hot encoded selection as values.

        """
        label = {}

        for button_name in self.arrow_button.keys():
            state = str(self.arrow_button[button_name]["bg"])
            if state == DARK_ORANGE:
                label[button_name] = 1
            else:
                label[button_name] = 0

        return label

    def set_label(self, label):
        """
        Changes the background color of the labeling button with respect to the registered results in the results csv
        (triggered if an already labeld point cloud is opened again on the GUI).

        Parameter
        --------
        label : Any
            A list that contains the registered label result from the result csv (one hot encoded)

        """
        if label:
            indices = [i for i, x in enumerate(label) if x == 1]
            button_names = [name for i, name in enumerate(self.labeling_reference_list) if i in indices]

            for button_name in self.labeling_reference_list:
                if button_name in button_names:
                    self.arrow_button[button_name]["bg"] = DARK_ORANGE
                else:
                    self.arrow_button[button_name]["bg"] = "white"
        else:

            for button_name in self.labeling_reference_list:

                self.arrow_button[button_name]["bg"] = "white"

    def release(self):
        """
        Releases all labeling button so that they can be pressed.

        """
        for button_name in self.arrow_button.keys():
            self.arrow_button[button_name]["state"] = "normal"

    def disable(self):
        """
        Disables all labeling button so that they can not be pressed.

        """
        for button_name in self.arrow_button.keys():
            self.arrow_button[button_name]["state"] = "disabled"


class PointCloud(tk.LabelFrame):
    """
    A class that manages the point cloud plots on the labeling frame

    ...

    Attributes
    ----------
    root : tk.Frame
        The root frame on which this label frame is placed
    pcd_var : tk.IntVar
        A variable that assumes the value one if the point cloud plot is displayed on the GUI
    cb_pcd : tk.Checkbutton
        The checkbutton to display the point cloud plot
    sample_rate : tk.StingVar
        The sample rate at which the point cloud is sampled
    lb_sample_rate :  tk.Label
        A label with the info text about the sample rate
    en_sample_rate : tk.Entry
        An entry in which the sample rate is written
    voxel_var : tk.IntVar
        A variable that assumes the value one if the voxel plot is displayed on the GUI
    cb_voxel : tk.Checkbutton
        The checkbutton to display the voxel plot
    voxel_size : tk.StingVar
        The size of the displayed voxels
    lb_voxel_size : tk.Label
        A label with the info text about the voxel size
    en_voxel_size : tk.Entry
        An entry in which the voxel size is written
    heatmap_var : tk.IntVar
        A variable that assumes the value one if the heatmap is displayed on the GUI
    cb_heatmap : tk.Checkbutton
        The checkbutton to display the heatmap plot
    lb_info : tk.Label
        The label showing the tooltip
    canvas : Any
        The canvas object displaying the plots
    toolbar : Any
        The matplotlib toolbar object
    cloud : PointCloud
        The point cloud object to process the point clouds
    plot : Any
        The current matplotlib plot object (figure)
    cutout : tk.BooleanVar
        A boolean variable that assumes the value one if a cutout point cloud is displayed on the GUI
    pick_x : Any
        The x coordinates of a picked point (Determined when a cutoff event is triggered)
    pick_y : Any
        The y coordinates of a picked point (Determined when a cutoff event is triggered)
    zero_offsets : Any
        The zero offset value to the cutout rectangle of the heatmap plot (Determined when a cutoff event is triggered)

    Methods
    -------
    set_cb(value)
        Deselects the unselected checkboxes and triggers the show plot method
    get_plot()
        Gets the plot classes with respect to the selected checkbox
    show_plot()
        Places the selected plot in the frame (displays it)
    update_plot(event)
        Updates the plot to a new voxel size or sample rate if one of them was written in the associated entry and
        logged by pressing return
    event_handler(event_type, event_data)
        Manages the following processes after a plot event was triggered
    get_zero_offsets()
        Returns the information about the current zero offset
    reset_variables()
        Resets all variables to their default values

    """

    def __init__(self, root):
        """
        Parameter
        ---------
        root : tk.Frame
            The root frame on which this labeling frame is placed

        """
        super().__init__(root, padx=5, pady=5, text="Punktwolke")
        self.root = root

        self.pcd_var = tk.IntVar()
        self.cb_pcd = tk.Checkbutton(self, text="Punktwolke", justify="left", anchor="w", variable=self.pcd_var,
                                     command=lambda x="pcd": self.set_cb(x))
        self.cb_pcd.select()
        self.cb_pcd.grid(column=0, row=0, padx=5, pady=5)

        self.sample_rate = tk.StringVar()
        self.sample_rate.set("60")
        self.lb_sample_rate = tk.Label(self, text="Sample rate:")
        self.lb_sample_rate.grid(column=1, row=0, padx=(0, 3), pady=5)
        self.en_sample_rate = tk.Entry(self, textvariable=self.sample_rate, width=5)
        self.en_sample_rate.grid(column=2, row=0, pady=5)
        self.en_sample_rate.bind("<Return>", self.update_plot)

        self.voxel_var = tk.IntVar()
        self.cb_voxel = tk.Checkbutton(self, text="Voxel", justify="left", anchor="w", variable=self.voxel_var,
                                       command=lambda x="voxel": self.set_cb(x))
        self.cb_voxel.grid(column=4, row=0, padx=5, pady=5)

        self.voxel_size = tk.StringVar()
        self.voxel_size.set("10")
        self.lb_voxel_size = tk.Label(self, text="Voxel size:")
        self.lb_voxel_size.grid(column=5, row=0, padx=(0, 3), pady=5)
        self.en_voxel_size = tk.Entry(self, textvariable=self.voxel_size, width=5)
        self.en_voxel_size.grid(column=6, row=0, pady=5)
        self.en_voxel_size.bind("<Return>", self.update_plot)

        self.heatmap_var = tk.IntVar()
        self.cb_heatmap = tk.Checkbutton(self, text="Heatmap", justify="left", anchor="w", variable=self.heatmap_var,
                                         command=lambda x="heatmap": self.set_cb(x))
        self.cb_heatmap.grid(column=8, row=0, padx=5, pady=5)

        try:
            info_icon_path = os.path.join(os.getcwd(), r"Icon\Info.png")
            info_icon_img = Image.open(info_icon_path)
            info_icon_img.thumbnail((20, 20), Image.LANCZOS)
            self.info_icon_photo = ImageTk.PhotoImage(info_icon_img)
            self.lb_info = tk.Label(self, image=self.info_icon_photo)
        except FileNotFoundError:
            self.lb_info = tk.Label(self, text="i", font="bold")
        CustomToolTip(self.lb_info, "1. Öffnen Sie links einen Datensatz in dem\n"
                                    "   Punktwolke-Dateien enthalten sind.\n\n"
                                    "2. Ziehen Sie eine Punktwolke-Datei aus\n"
                                    "   der Ordnerstruktur in das freie\n"
                                    "   Feld im Bereich 'Punktwolke'.")
        self.lb_info.grid(column=9, row=0, padx=5, pady=5)

        self.columnconfigure(3, weight=1, uniform="empty")
        self.columnconfigure(7, weight=1, uniform="empty")

        self.canvas = None
        self.toolbar = None
        self.cloud = CloudProcessing.Cloud()
        self.plot = None
        self.cutout = tk.BooleanVar()

        self.pick_x = None
        self.pick_y = None

        self.zero_offsets = None

    def set_cb(self, value):
        """
        Deselects the unselected checkboxes and triggers the show plot method.

        Parameter
        ---------
        value : str
            The key value to differentiate between the plot types
        """
        if value == "pcd":
            self.cb_voxel.deselect()
            self.cb_heatmap.deselect()
        elif value == "voxel":
            self.cb_pcd.deselect()
            self.cb_heatmap.deselect()
        elif value == "heatmap":
            self.cb_pcd.deselect()
            self.cb_voxel.deselect()

        if OPEN_CLOUD:
            self.show_plot()

    def get_plot(self):
        """
        Gets the plot objects with respect to the selected checkbox and changes the tooltip.

        """
        if self.pcd_var.get():
            sample_rate = int(self.sample_rate.get())
            pcd = self.cloud.get()
            self.plot = CloudPlots.SampledCloudPlot(self, pcd, sample_rate)
            CustomToolTip(self.lb_info, text="'Strg+Maustaste': Wahl einer Klemme im Plot\n\n"
                                             "'RechteMaustaste': Zoom\n\n"
                                             "'LinkeMaustaste': Drehen der Punktwolke\n\n"
                                             "'Mausrad': Verschieben der Punktwolke")
        elif self.voxel_var.get():
            voxel_size = int(self.voxel_size.get())
            data = self.cloud.get_voxels(voxel_size)
            self.plot = CloudPlots.VoxelPlot(self, data, voxel_size)
            CustomToolTip(self.lb_info, text="'Strg+Maustaste': Wahl einer Klemme im Plot\n\n"
                                             "'RechteMaustaste': Zoom\n\n"
                                             "'LinkeMaustaste': Drehen der Punktwolke\n\n"
                                             "'Mausrad': Verschieben der Punktwolke")
        else:
            voxel_size = int(self.voxel_size.get())
            data = self.cloud.get_heatmap(voxel_size)
            self.plot = CloudPlots.VoxelHeatmapPlot(self, data)
            if not self.cutout.get():
                kernel_size = self.root.selection_options.kernel_cbb.get()
                if self.pick_x and self.pick_y:
                    self.plot.add_draggable_rect(self.pick_x, self.pick_y, kernel_size=kernel_size)
                else:
                    self.plot.add_draggable_rect(kernel_size=kernel_size)
            CustomToolTip(self.lb_info, text="1. Verschieben Sie das Rechteck so, dass \n"
                                             "   die zu greifende Klemme in der Mitte liegt.\n\n"
                                             "2. Ausschneiden der Punkte im Rechteck mit 'Strg+c'.\n\n"
                                             "3. Auswahl der Greifrichtung im Bereich 'Labeling'.\n\n"
                                             "4. Speichern der Punktwolke.")

    def show_plot(self):
        """
        Places the selected plot in the frame (displays it).

        """
        try:
            plt.close()
        except Exception:
            pass

        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
        if self.toolbar is not None:
            self.toolbar.grid_forget()

        self.get_plot()
        fig, ax = self.plot.get_plot()

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.get_tk_widget().grid(column=0, columnspan=9, row=1, padx=5, pady=5, sticky="NSWE")
        self.canvas.draw()
        self.toolbar = NavigationToolbar2Tk(self.canvas, self, pack_toolbar=False)
        self.toolbar.grid(column=0, columnspan=9, row=2)
        self.toolbar.update()

        self.rowconfigure(1, weight=1)

    def update_plot(self, event=None):
        """
        Updates the plot to a new voxel size or sample rate if one of them was written in the associated entry and
        logged by pressing return.

        Parameter
        --------
        event : Any
            Return event after writing something in the sample rate or voxel size entrys
        """
        try:
            self.show_plot()
        except ValueError:
            pass

    def event_handler(self, event_type, event_data):
        """
        Manages the following processes after a plot event was triggered.
        Pick event:
            Determines the x- and y-coordinates of the picked point in point cloud or voxel plot
            Displays the heatmap plot with the cutout rectangle placed at the x- and y-coordinates
        Cut event:
            Determines the zero offset variable
            Crops the point cloud to the size of the given bbox coordinates
            Displays the cropped cloud
            Releases the labeling button

        Parameters
        ----------
        event_type : str
            The event type triggered through the plot objects
        event_data : Any
            The passed event data (X-, Y-coordinates - pick event, bbox-coordinates and zero_offsets - cut event)
        """
        if event_type == "pick_event":
            self.pick_x, self.pick_y = event_data
            self.cb_heatmap.select()
            self.set_cb("heatmap")
        elif event_type == "cut_event":
            if not self.cutout.get():
                x1, y1, x2, y2, zero_offsets = event_data
                self.zero_offsets = zero_offsets
                self.cloud.remove_points_from_threshold(axis="X", threshold=x1, direction=">=")
                self.cloud.remove_points_from_threshold(axis="X", threshold=x2, direction="<=")
                self.cloud.remove_points_from_threshold(axis="Y", threshold=y1, direction=">=")
                self.cloud.remove_points_from_threshold(axis="Y", threshold=y2, direction="<=")
                self.cutout.set(True)
                self.show_plot()
                self.root.labeling_options.release()
                self.root.selection_options.save_result_bt.configure(state="normal")
            else:
                messagebox.showinfo("Existierender Cutout", "Die angezeigte Punktwolke ist bereits ein Ausschnitt.")

    def get_zero_offsets(self):
        """
        Returns the information about the current zero offset value.

        """
        if self.cutout.get() and self.zero_offsets:
            return self.zero_offsets
        else:
            return None

    def reset_variables(self):
        """
        Resets all variables to their default values.

        """
        self.pick_x = None
        self.pick_y = None

        self.cb_pcd.select()
        self.cb_voxel.deselect()
        self.cb_heatmap.deselect()
        self.voxel_size.set("10")
        self.sample_rate.set("60")
