import os

import open3d
import numpy as np
import pandas as pd


class Cloud:
    """
    A class that is used to process a point cloud

    ...

    Attributes
    ----------
    pcd : Any
        The point cloud object
    pcd_path : Any
        The storage path where the point cloud is saved/The memory path where the point cloud data is located

    Methods
    -------
    set(pcd_path)
        Retrieves the data from the specified storage path and loads the point cloud as an open3D vector object
    remove_points_from_threshold(axis, threshold, direction)
        Removes the points in the point cloud that exceed/fall below the specified threshold value
    get_voxels(voxel_size)
        Creates the voxel grid from the given point cloud data
    get_heatmap(voxel_size)
        Creates the heatmap from the given point cloud data
    get()
        Returns the current point cloud data
    save_pcd(cutout_path, filename)
        Saves the point cloud data at the given memory path

    """

    def __init__(self):
        self.pcd = None
        self.pcd_path = None

    def set(self, pcd_path: str = None):
        """
        Retrieves the data from the specified storage path and loads the point cloud as an open3D vector object

        Parameter
        ---------
        pcd_path : str
            Memory path of the point cloud to be opened

        """
        if pcd_path:
            path = pcd_path
        elif self.pcd_path:
            path = self.pcd_path
        else:
            path = None

        if path.endswith(".csv"):
            data = np.genfromtxt(path, delimiter=";")
            pcd = open3d.geometry.PointCloud()
            pcd.points = open3d.utility.Vector3dVector(data)
        elif path.endswith(".npy"):
            data = np.load(path)
            pcd = open3d.geometry.PointCloud()
            pcd.points = open3d.utility.Vector3dVector(data)
        elif path.endswith(".ply"):
            pcd = open3d.io.read_point_cloud(path)
        else:
            raise AttributeError

        if pcd:
            self.pcd = pcd
            self.pcd_path = path
            self.remove_points_from_threshold("Z", -2.5, ">")

    def remove_points_from_threshold(self, axis: str = 'Z', threshold: float = -6.8, direction: str = '>'):
        """
        Removes the points in the point cloud that exceed/fall below the specified threshold value

        Parameter
        --------
        axis : str
            The axis on which the points are to be removed
        threshold : float
            The threshold value that the point have to exceed/fall below
        direction : str
            The direction in which the points are to be maintained

        """
        points = np.asarray(self.pcd.points)
        if axis == 'X':
            ax = 0
        elif axis == 'Y':
            ax = 1
        else:
            ax = 2

        if direction == '=':
            pcd_sel = self.pcd.select_by_index(np.where(points[:, ax] == threshold)[0])
        elif direction == '>=':
            pcd_sel = self.pcd.select_by_index(np.where(points[:, ax] >= threshold)[0])
        elif direction == '<=':
            pcd_sel = self.pcd.select_by_index(np.where(points[:, ax] <= threshold)[0])
        elif direction == '<':
            pcd_sel = self.pcd.select_by_index(np.where(points[:, ax] < threshold)[0])
        elif direction == '!=':
            pcd_sel = self.pcd.select_by_index(np.where(points[:, ax] != threshold)[0])
        else:
            pcd_sel = self.pcd.select_by_index(np.where(points[:, ax] > threshold)[0])

        self.pcd = pcd_sel

    def get_voxels(self, voxel_size: int = 2):
        """
        Creates the voxel grid from the given point cloud data

        Parameter
        --------
        voxel_size : int
            The size of the voxels

        """
        center = self.pcd.get_center()
        voxel_grid = open3d.geometry.VoxelGrid.create_from_point_cloud(input=self.pcd, voxel_size=voxel_size)
        resolution = np.round(voxel_grid.get_max_bound() - voxel_grid.get_min_bound()).astype(int)
        voxel_array = np.zeros((resolution[0], resolution[1], resolution[2]))
        voxels = voxel_grid.get_voxels()

        for voxel in voxels:
            voxel_index = voxel.grid_index * voxel_size
            voxel_array[int(voxel_index[0]), int(voxel_index[1]), int(voxel_index[2])] = 1

        indices = np.where(voxel_array == 1)
        shift_x = resolution[0] / 2
        shift_y = resolution[1] / 2
        voxel_data = np.vstack((indices[0], indices[1], indices[2])).T
        voxel_data[:, 0] = voxel_data[:, 0] - shift_x + center[0]
        voxel_data[:, 1] = voxel_data[:, 1] - shift_y + center[1]

        return voxel_data

    def get_heatmap(self, voxel_size: int = 10):
        """
        Creates the heatmap from the given point cloud data

        Parameter
        ---------
        voxel_size : int
            The size of the voxels from which the heatmap is generated

        """
        voxels = self.get_voxels(voxel_size)
        x_values = np.unique(voxels[:, 0])
        y_values = np.unique(voxels[:, 1])
        x_sorted = x_values[x_values[:].argsort()]
        y_sorted = y_values[y_values[:].argsort()]

        df = pd.DataFrame(index=y_sorted, columns=x_sorted)
        for col, x in enumerate(df.columns):
            for idx, y in enumerate(df.index):
                try:
                    array_idx = np.where((voxels[:, 0] == x) & (voxels[:, 1] == y))[0]
                    if array_idx.any():
                        array_idx = max(array_idx)
                        df.iloc[idx, col] = voxels[array_idx, 2]
                except IndexError:
                    pass

        df = df.fillna(0)
        return df

    def get(self):
        """
        Returns the current point cloud data

        """
        return self.pcd

    def save_pcd(self, cutout_path, filename):
        """
        Saves the point cloud data at the given memory path

        """
        memory_path = os.path.join(cutout_path, filename)
        if os.path.exists(memory_path):
            os.remove(memory_path)
        points = np.asarray(self.pcd.points)
        np.savetxt(memory_path, points, delimiter=";")
