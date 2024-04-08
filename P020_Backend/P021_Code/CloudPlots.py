import matplotlib.pyplot as plt
import open3d
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
import pandas as pd
import matplotlib
from P020_Backend.P021_Code.DraggableRect import DraggableRectangle, CustomRectangle


class VoxelPlot:
    """
    A class that defines a voxel plot (figure and axis)

    ...

    Attributes
    ----------
    master : tk.Frame
        The frame on which the plot is displayed
    plot_data : Any
        The data that will be displayed in the plot
    fig : Any
        The matplotlib figure
    ax : Any
        The axis object of the figure (3D Scatter Plot)
    c_pick : CustomPick
        An object of the class that defines the pick event

    Methods
    -------
    get_plot()
        Returns the figure and the axis object
    get_plot_data()
        Returns the plot data
    pick_event_handler()
        Processes the data of the pick event

    """

    def __init__(self, master, voxels, voxel_size: int = 10):
        """
        Parameter
        ---------
        master : Any
            The frame on which the plot is displayed
        voxels : Any
            The voxels that will be displayed in the plot
        voxel_size : int
            The size of the voxels

        """
        self.master = master

        self.plot_data = voxels

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection="3d")
        self.ax.scatter(self.plot_data[:, 0], self.plot_data[:, 1], self.plot_data[:, 2], s=voxel_size / 5,
                        c=self.plot_data[:, 2], cmap="jet",
                        picker=True, pickradius=1)

        y_min, y_max = self.ax.get_ylim()
        x_min, x_max = self.ax.get_xlim()
        width = x_max - x_min
        height = y_max - y_min

        if width < height:
            self.ax.text3D(x_min - 100, y_max - 20, 0, "Ref. UL", color="red", zdir="x")
            self.ax.plot([x_min], [y_max], "2", color="red", markersize=20)
        else:
            self.ax.text3D(x_min - 200, y_min - 20, 0, "Ref. UL", color="red", zdir="x")
            self.ax.plot([x_min], [y_min], "2", color="red", markersize=20)

        self.c_pick = CustomPick(self, self.fig)

        self.ax.set_title("Voxel Cloud", fontsize=15)
        self.ax.set_xlabel("x [cm]", fontsize=10)
        self.ax.set_ylabel("y [cm]", fontsize=10)
        self.ax.set_zlabel("z [cm]", fontsize=10)
        self.ax.set_aspect("equal", adjustable="box")
        self.ax.view_init(elev=90, azim=-90, roll=0)

    def get_plot(self):
        """
        Returns the figure and the axis object

        """
        return self.fig, self.ax

    def get_plot_data(self):
        """
        Returns the plot data as open3D Vector

        """
        pcd = open3d.geometry.PointCloud()
        pcd.points = open3d.utility.Vector3dVector(self.plot_data)
        return pcd

    def pick_event_handler(self, event_data):
        """
        Processes the data of the pick event. Accepts the highest point among the selected points and returns its
        x- y-coordinates.

        """
        ind = event_data
        data_as_array = np.asarray(self.get_plot_data().points)
        argmax = np.argmax(data_as_array[ind, 2])
        pick_x = int(data_as_array[ind[argmax], 0])
        pick_y = int(data_as_array[ind[argmax], 1])
        self.master.event_handler("pick_event", (pick_x, pick_y))


class SampledCloudPlot:
    """
    A class that defines a sampled cloud plot (figure and axis)

    ...

    Attributes
    ----------
    master : tk.Frame
        The frame on which the plot is displayed
    plot_data : Any
        The data that will be displayed in the plot
    fig : Any
        The matplotlib figure
    ax : Any
        The axis object of the figure (3D Scatter Plot)
    c_pick : CustomPick
        An object of the class that defines the pick event

    Methods
    -------
    get_plot()
        Returns the figure and the axis object
    get_plot_data()
        Returns the plot data
    pick_event_handler()
        Processes the data of the pick event

    """

    def __init__(self, master, pcd: open3d.geometry.PointCloud, sample_rate: int = 60):
        """
        Parameter
        ---------
        master : Any
            The frame on which the plot is displayed
        pcd : open3d.geometry.PointCloud
            The point cloud that will be displayed in the plot
        sample_rate : int
            The sampling rate k. Every k-th point of the point cloud is accepted.

        """
        self.master = master

        self.plot_data = pcd.uniform_down_sample(sample_rate)
        pcd_as_ar = np.asarray(self.plot_data.points)
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection="3d")
        self.ax.scatter(pcd_as_ar[:, 0], pcd_as_ar[:, 1], pcd_as_ar[:, 2], s=sample_rate / 5, c=pcd_as_ar[:, 2], cmap="jet",
                        picker=True, pickradius=1)

        y_min, y_max = self.ax.get_ylim()
        x_min, x_max = self.ax.get_xlim()
        width = x_max - x_min
        height = y_max - y_min

        if width < height:
            self.ax.text3D(x_min - 100, y_max - 20, 0, "Ref. UL", color="red", zdir="x")
            self.ax.plot([x_min], [y_max], "2", color="red", markersize=20)
        else:
            self.ax.text3D(x_min - 200, y_min - 20, 0, "Ref. UL", color="red", zdir="x")
            self.ax.plot([x_min], [y_min], "2", color="red", markersize=20)

        self.c_pick = CustomPick(self, self.fig)

        self.ax.set_title("Sampled Pointcloud", fontsize=15)
        self.ax.set_xlabel("x [cm]", fontsize=10)
        self.ax.set_ylabel("y [cm]", fontsize=10)
        self.ax.set_zlabel("z [cm]", fontsize=10)
        self.ax.set_aspect("equal", adjustable="box")
        self.ax.view_init(elev=90, azim=-90, roll=0)

    def get_plot(self):
        """
        Returns the figure and the axis object

        """
        return self.fig, self.ax

    def get_plot_data(self):
        """
        Returns the plot data (Pointcloud data)

        """
        return self.plot_data

    def pick_event_handler(self, event_data):
        """
        Processes the data of the pick event. Accepts the highest point among the selected points and returns its
        x- y-coordinates.

        """
        ind = event_data
        data_as_array = np.asarray(self.plot_data.points)
        argmax = np.argmax(data_as_array[ind, 2])
        pick_x = int(data_as_array[ind[argmax], 0])
        pick_y = int(data_as_array[ind[argmax], 1])
        self.master.event_handler("pick_event", (pick_x, pick_y))


class VoxelHeatmapPlot:
    """
    A class that defines a voxel heatmap plot (figure and axis)

    ...

    Attributes
    ----------
    master : tk.Frame
        The frame on which the plot is displayed
    plot_data : Any
        The data that will be displayed in the plot
    fig : Any
        The matplotlib figure
    ax : Any
        The axis object of the figure (3D Scatter Plot)

    Methods
    -------
    add_draggable_rect(cx, cy, col_width, row_height, kernel_size, rotated)
        Adds a draggable rectangle to the plot
    get_plot()
        Returns the figure and the axis object
    get_plot_data()
        Returns the plotted data
    cut_event_handler(event_data, rotated)
        Processes the data of the cut event
    calc_zero_offset(x1, y1, x2, y2, rotated_rect)
        Computes the zero offset of all grasp direction starting points

    """

    def __init__(self, master, heatmap: pd.DataFrame):
        """
        Parameter
        ---------
        master : Any
            The frame on which the plot is displayed
        heatmap : pd.DataFrame
            The heatmap array that will be displayed in the plot

        """
        self.master = master

        self.plot_data = heatmap

        z_values = self.plot_data.to_numpy()
        x_values = self.plot_data.columns
        y_values = self.plot_data.index

        width = max(x_values) - min(x_values)
        height = max(y_values) - min(y_values)
        x_axis = "X [cm]"
        y_axis = "Y [cm]"

        if width < height < 500:
            z_values = np.rot90(z_values, axes=(1, 0))
            copy = x_values
            x_values = y_values
            y_values = copy
            x_axis = "Y [cm]"
            y_axis = "X [cm]"

        self.fig, self.ax = plt.subplots(1, 1)
        im = self.ax.imshow(z_values, cmap='jet', interpolation='bessel', origin='lower', aspect='equal',
                            extent=[min(x_values), max(x_values), min(y_values), max(y_values)])
        self.ax.set_aspect("equal", adjustable="box")

        plt.title("Voxel Heatmap", fontsize=15)
        plt.xlabel(x_axis, fontsize=10)
        plt.ylabel(y_axis, fontsize=10)
        divider = make_axes_locatable(self.ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        plt.colorbar(im, cax=cax, label="Z [cm]")

    def add_draggable_rect(self, cx: int = 0, cy: int = 0, col_width: int = 80, row_height: int = 50,
                           kernel_size: str = "3x3", rotated: bool = False):
        """
        Adds a draggable rectangle to the plot. If the rectangle crosses the boundaries, it is placed at the point in
        the plot where it does not cross the boundaries. The required events are assigned to the rectangle via
        the DraggableRect class.

        Parameter
        ---------
        cx : int
            x-coordinate of the point selected in the point cloud or voxel grid
        cy : int
            y-coordinate of the point selected in the point cloud or voxel grid
        col_width : int
            The width of one matrix element
        row_height : int
            The height of one matrix element
        kernel_size : str
            The size of the matrix
        rotated : bool
            Information on whether the rectangle should be rotated or not
        """
        x_borders = self.ax.get_xlim()
        y_borders = self.ax.get_ylim()
        n_rows = int(kernel_size.split("x")[0])
        n_cols = int(kernel_size.split("x")[1])
        cx_min_dist, cx_max_dist = x_borders[0] + col_width / 2 * n_cols, x_borders[1] - col_width / 2 * n_cols
        cy_min_dist, cy_max_dist = y_borders[0] + row_height / 2 * n_rows, y_borders[1] - row_height / 2 * n_rows
        if not cx_min_dist <= cx:
            cx = cx_min_dist
        elif not cx <= cx_max_dist:
            cx = cx_max_dist
        if not cy_min_dist <= cy:
            cy = cy_min_dist
        elif not cy <= cy_max_dist:
            cy = cy_max_dist
        rect = CustomRectangle(cx, cy, col_width, row_height, n_rows, n_cols, rotated)
        self.d_rect_event = DraggableRectangle(self, rect, self.ax.get_ylim(), self.ax.get_xlim())
        self.ax.add_patch(rect)
        self.d_rect_event.connect()

    def get_plot(self):
        """
        Returns the figure and the axis object

        """
        return self.fig, self.ax

    def get_plot_data(self):
        """
        Returns the plotted data

        """
        pcd = open3d.geometry.PointCloud()
        pcd.points = open3d.utility.Vector3dVector(self.plot_data)
        return pcd

    def cut_event_handler(self, event_data, rotated: bool):
        """
        Processes the data of the cut event

        Parameter
        ---------
        event_data : Any
            The data passed by the event
        rotated : bool
            Information on whether the draggable rectangle is rotated or not

        """
        points = event_data.get_points()
        x1, y1, x2, y2 = points[0, 0], points[0, 1], points[1, 0], points[1, 1]
        zero_offsets = self.calc_zero_offset(x1, y1, x2, y2, rotated)
        self.master.event_handler("cut_event", (x1, y1, x2, y2, zero_offsets))

    @staticmethod
    def calc_zero_offset(x1: float, y1: float, x2: float, y2: float, rotated_rect: bool):
        """
        Computes the zero offset of all grasp direction starting points

        Parameter
        ---------
        x1 : float
            x-coordinate of the left corners of the bounding box
        y1 : float
            y-coordinate of the bottom corners of the bounding box
        x2 : float
            x-coordinate of the right corners of the bounding box
        y2 : float
            y-coordinate of the upper corners of the bounding box
        rotated_rect : bool
            Information on whether the draggable rectangle is rotated or not

        """
        lo = (x1, y2)
        o = (x1 + (x2 - x1) / 2, y2)
        ro = (x2, y2)

        l = (x1, y1 + (y2 - y1) / 2)
        center = (x1 + (x2 - x1) / 2, y1 + (y2 - y1) / 2)
        r = (x2, y1 + (y2 - y1) / 2)

        lu = (x1, y1)
        u = (x1 + (x2 - x1) / 2, y1)
        ru = (x2, y1)

        # if rotated, change the labels so that there is no difference for the nn.
        # The reference point from which the labels are labeled also changes in the GUI so that the labels remain
        # identical
        if rotated_rect:
            zero_offsets = {"offset_lo": ro, "offset_o": r, "offset_ro": ru,
                            "offset_l": o, "center": center, "offset_r": u,
                            "offset_lu": lo, "offset_u": l, "offset_ru": lu}
        else:
            zero_offsets = {"offset_lo": lo, "offset_o": o, "offset_ro": ro,
                            "offset_l": l, "center": center, "offset_r": r,
                            "offset_lu": lu, "offset_u": u, "offset_ru": ru}

        return zero_offsets


class CustomPick:
    """
    A class that defines a custom pick event for the point cloud and voxel plot

    ...

    Attributes
    ----------
    master : tk.Frame
        The frame on which the plot is displayed
    fig : Any
        The matplotlib figure to which the event is to be bound
    keypress : Any
        Keypress Event
    keyrelease : Any
        Keyrelease Event
    pick : Any
        Pick Event

    Methods
    -------
    custom_pick(event)
        Bounds the pick event to the passed figure
    on_pick(event)
        Processes the pick event and passes the data to the masters pick event handler
    disconnect_pick(event)
        Disconnects the pick event so that the user always has to execute the keypress event before the pick event

    """

    def __init__(self, master, figure: matplotlib.pyplot.figure):
        self.master = master
        self.fig = figure
        self.keypress = self.fig.canvas.mpl_connect("key_press_event", self.custom_pick)
        self.keyrelease = self.fig.canvas.mpl_connect("key_release_event", self.disconnect_pick)
        self.pick = None

    def custom_pick(self, event):
        """
        Bounds the pick event to the passed figure

        """
        self.pick = self.fig.canvas.mpl_connect("pick_event", self.on_pick)

    def on_pick(self, event):
        """
        Processes the pick event and passes the data to the masters pick event handler

        """
        ind = event.ind
        self.master.pick_event_handler(ind)

    def disconnect_pick(self, event):
        """
        Disconnects the pick event so that the user always has to execute the keypress event before the pick event

        """
        if self.pick:
            self.fig.canvas.mpl_disconnect(self.pick)
            self.pick = None
