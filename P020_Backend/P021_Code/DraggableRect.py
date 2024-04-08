from matplotlib.patches import Rectangle
import numpy as np
import matplotlib.pyplot as plt
import matplotlib


class CustomRectangle(matplotlib.patches.Rectangle):
    """
    A class that defines a custom sized matplotlib rectangle patch

    """

    def __init__(self, cx: int = 0, cy: int = 0, col_width: int = 80, row_height: int = 50, n_rows: int = 3,
                 n_cols: int = 3, rotated: bool = False):
        """
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
        n_rows : int
            The number of rows contained in the matrix
        n_col : int
            The columns of rows contained in the matrix
        rotated : bool
            Information on whether the rectangle should be rotated or not

        """
        x = cx - col_width * n_cols / 2
        y = cy - row_height * n_rows / 2
        if rotated:
            rect_height = col_width * n_cols
            rect_width = row_height * n_rows
        else:
            rect_width = col_width * n_cols
            rect_height = row_height * n_rows
        super().__init__((x, y), rect_width, rect_height, fill=None, linewidth=3)


class DraggableRectangle:
    """
    This class was partially taken from the Matplotlib Tutorial - Event handling
    @website{
    author={The Matplotlib development team}
    title={Event handling and picking - Draggable Rectangle Excercise}
    year={w. d.}
    url={https://matplotlib.org/stable/users/explain/figure/event_handling.html}
    }

    """
    lock = None  # only one can be animated at a time

    def __init__(self, master, rect: matplotlib.patches.Rectangle, y_lim: tuple[float, float],
                 x_lim: tuple[float, float]):
        self.master = master
        self.rect = rect
        self.y_lim = y_lim
        self.x_lim = x_lim
        self.press = None
        self.background = None

        self.x = self.rect.get_x()
        self.y = self.rect.get_y()

        self.rotated = False

    def connect(self):
        """Connect to all the events we need."""
        self.cidpress = self.rect.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.rect.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.rect.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.cidkeypress = self.rect.figure.canvas.mpl_connect('key_press_event', self.on_key)

    def on_key(self, event):
        if event.key == "r":
            ax = self.rect.figure.get_axes()[0]
            ax.patches[0].remove()

            self.rect = Rectangle((self.x, self.y), self.rect.get_height(), self.rect.get_width(), fill=None,
                                   linewidth=3)

            ax.add_patch(self.rect)
            self.rect.figure.canvas.draw()
            if self.rotated:
                self.rotated = False
            else:
                self.rotated = True

        if event.key == "ctrl+c":
            bbox = self.rect.get_bbox()
            self.master.cut_event_handler(bbox, rotated=self.rotated)

    def on_press(self, event):
        """Check whether mouse is over us; if so, store some data."""
        if (event.inaxes != self.rect.axes
                or DraggableRectangle.lock is not None):
            return
        contains, attrd = self.rect.contains(event)
        if not contains:
            return

        self.press = self.rect.xy, (event.xdata, event.ydata)
        DraggableRectangle.lock = self

        # draw everything but the selected rectangle and store the pixel buffer
        canvas = self.rect.figure.canvas
        axes = self.rect.axes
        self.rect.set_animated(True)
        canvas.draw()
        self.background = canvas.copy_from_bbox(self.rect.axes.bbox)

        # now redraw just the rectangle
        axes.draw_artist(self.rect)

        # and blit just the redrawn area
        canvas.blit(axes.bbox)

    def on_motion(self, event):
        """Move the rectangle if the mouse is over us."""
        if (event.inaxes != self.rect.axes
                or DraggableRectangle.lock is not self):
            return
        (x0, y0), (xpress, ypress) = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress
        new_x = x0+dx
        new_y = y0+dy

        x_shift = self.rect.get_width()
        y_shift = self.rect.get_height()
        if self.x_lim[0] <= new_x <= self.x_lim[1] - x_shift:
            self.rect.set_x(new_x)
            self.x = new_x
        if self.y_lim[0] <= new_y <= self.y_lim[1] - y_shift:
            self.rect.set_y(new_y)
            self.y = new_y

        canvas = self.rect.figure.canvas
        axes = self.rect.axes
        # restore the background region
        canvas.restore_region(self.background)

        # redraw just the current rectangle
        axes.draw_artist(self.rect)

        # blit just the redrawn area
        canvas.blit(axes.bbox)

    def on_release(self, event):
        """Clear button press information."""
        if DraggableRectangle.lock is not self:
            return

        self.press = None
        DraggableRectangle.lock = None

        # turn off the rect animation property and reset the background
        self.rect.set_animated(False)
        self.background = None

        # redraw the full figure
        self.rect.figure.canvas.draw()

    def disconnect(self):
        """Disconnect all callbacks."""
        self.rect.figure.canvas.mpl_disconnect(self.cidpress)
        self.rect.figure.canvas.mpl_disconnect(self.cidrelease)
        self.rect.figure.canvas.mpl_disconnect(self.cidmotion)
