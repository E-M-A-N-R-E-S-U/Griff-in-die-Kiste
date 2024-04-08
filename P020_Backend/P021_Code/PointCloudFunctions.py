import os
import open3d
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from mpl_toolkits.axes_grid1 import make_axes_locatable


def remove_points_from_threshold(pcd: open3d.geometry.PointCloud, axis: str = 'Z', threshold: float = -6.8,
                                 direction: str = '>'):

    # Punkte aus der Punktwolke als Array holen
    points = np.asarray(pcd.points)
    if axis == 'X':
        ax = 0
    elif axis == 'Y':
        ax = 1
    else:
        ax = 2

    if direction == '=':
        pcd_sel = pcd.select_by_index(np.where(points[:, ax] == threshold)[0])
    elif direction == '>=':
        pcd_sel = pcd.select_by_index(np.where(points[:, ax] >= threshold)[0])
    elif direction == '<=':
        pcd_sel = pcd.select_by_index(np.where(points[:, ax] <= threshold)[0])
    elif direction == '<':
        pcd_sel = pcd.select_by_index(np.where(points[:, ax] < threshold)[0])
    elif direction == '!=':
        pcd_sel = pcd.select_by_index(np.where(points[:, ax] != threshold)[0])
    else:
        pcd_sel = pcd.select_by_index(np.where(points[:, ax] > threshold)[0])

    return pcd_sel


def display_inlier_outlier(pcd: open3d.geometry.PointCloud, ind: int):
    inlier_cloud = pcd.select_by_index(ind)
    outlier_cloud = pcd.select_by_index(ind, invert=True)

    outlier_cloud.paint_uniform_color([1, 0, 0])
    inlier_cloud.paint_uniform_color([0.8, 0.8, 0.8])
    open3d.visualization.draw_geometries([inlier_cloud, outlier_cloud])


def show_sampled_cloud(pcd: open3d.geometry.PointCloud, sample_rate: int = 60):
    uni_down_pcd = pcd.uniform_down_sample(sample_rate)
    pcd_as_ar = np.asarray(uni_down_pcd.points)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(pcd_as_ar[:, 0], pcd_as_ar[:, 1], pcd_as_ar[:, 2], s=sample_rate/5, c=pcd_as_ar[:, 2], cmap="jet",
               picker=True, pickradius=1)

    y_min, y_max = ax.get_ylim()
    x_min, x_max = ax.get_xlim()
    ax.text3D(x_min-200, y_min-20, 0, "Ref. UL", color="red", zdir="x")
    ax.plot([x_min], [y_min], "2", color="red")

    ax.set_title("Sampled Pointcloud", fontsize=15)
    ax.set_xlabel("x [cm]", fontsize=10)
    ax.set_ylabel("y [cm]", fontsize=10)
    ax.set_zlabel("z [cm]", fontsize=10)
    ax.set_aspect("equal", adjustable="box")
    ax.view_init(elev=90, azim=-90, roll=0)
    # plt.show()

    return fig, ax, uni_down_pcd


def get_voxels(pcd: open3d.geometry.PointCloud, voxel_size: int = 2):
    center = pcd.get_center()
    voxel_grid = open3d.geometry.VoxelGrid.create_from_point_cloud(input=pcd, voxel_size=voxel_size)
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


def show_voxel(pcd: open3d.geometry.PointCloud, voxel_size: int = 10):
    voxels_as_array = get_voxels(pcd, voxel_size)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(voxels_as_array[:, 0], voxels_as_array[:, 1], voxels_as_array[:, 2], s=voxel_size / 5,
               c=voxels_as_array[:, 2], cmap="jet",
               picker=True, pickradius=1)

    y_min, y_max = ax.get_ylim()
    x_min, x_max = ax.get_xlim()
    ax.text3D(x_min - 200, y_min - 20, 0, "Ref. UL", color="red", zdir="x")
    ax.plot([x_min], [y_min], "2", color="red")

    ax.set_title("Voxel Cloud", fontsize=15)
    ax.set_xlabel("x [cm]", fontsize=10)
    ax.set_ylabel("y [cm]", fontsize=10)
    ax.set_zlabel("z [cm]", fontsize=10)
    ax.set_aspect("equal", adjustable="box")
    ax.view_init(elev=90, azim=-90, roll=0)
    # plt.show()

    pcd = open3d.geometry.PointCloud()
    pcd.points = open3d.utility.Vector3dVector(voxels_as_array)

    return fig, ax, pcd


def show_voxel_heatmap(pcd: open3d.geometry.PointCloud, voxel_size: int = 10):
    # voxel_grid = open3d.geometry.VoxelGrid.create_from_point_cloud(input=pcd, voxel_size=voxel_size)
    # voxels = voxel_grid.get_voxels()
    # resolution = np.round(voxel_grid.get_max_bound() - voxel_grid.get_min_bound()).astype(int)
    # shift_x = resolution[0] / 2
    # shift_y = resolution[1] / 2
    # voxels_as_array = np.stack(list(vx.grid_index*voxel_size for vx in voxels))
    # voxels_as_array[:, 0] = voxels_as_array[:, 0] - shift_x
    # voxels_as_array[:, 1] = voxels_as_array[:, 1] - shift_y
    # voxels_as_array = voxels_as_array[voxels_as_array[:, 0].argsort()]
    voxels_as_array = get_voxels(pcd, voxel_size)

    x_values = np.unique(voxels_as_array[:, 0])
    y_values = np.unique(voxels_as_array[:, 1])
    x_sorted = x_values[x_values[:].argsort()]
    y_sorted = y_values[y_values[:].argsort()]

    df = pd.DataFrame(index=y_sorted, columns=x_sorted)
    for col, x in enumerate(df.columns):
        for idx, y in enumerate(df.index):
            try:
                array_idx = np.where((voxels_as_array[:, 0] == x) & (voxels_as_array[:, 1] == y))[0]
                if array_idx.any():
                    array_idx = max(array_idx)
                    df.iloc[idx, col] = voxels_as_array[array_idx, 2]
            except IndexError:
                pass

    df = df.fillna(0)
    z_values = df.to_numpy()
    fig, ax = plt.subplots(1, 1)
    im = ax.imshow(z_values, cmap='jet', interpolation='bessel', origin='lower', aspect='equal',
                   extent=[min(x_sorted), max(x_sorted), min(y_sorted), max(y_sorted)])
    ax.set_aspect("equal", adjustable="box")
    plt.title("Voxel Heatmap", fontsize=15)
    plt.xlabel("X [cm]", fontsize=10)
    plt.ylabel("Y [cm]", fontsize=10)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    plt.colorbar(im, cax=cax, label="Z [cm]")

    # plt.show()

    pcd = open3d.geometry.PointCloud()
    pcd.points = open3d.utility.Vector3dVector(voxels_as_array)

    return fig, ax, pcd


def get_pcd(pcd_path):
    if pcd_path.endswith(".csv"):
        data = np.genfromtxt(pcd_path, delimiter=";")
        pcd = open3d.geometry.PointCloud()
        pcd.points = open3d.utility.Vector3dVector(data)
    elif pcd_path.endswith(".npy"):
        data = np.load(pcd_path)
        pcd = open3d.geometry.PointCloud()
        pcd.points = open3d.utility.Vector3dVector(data)
    elif pcd_path.endswith(".ply"):
        pcd = open3d.io.read_point_cloud(pcd_path)
    else:
        pcd = None

    if pcd:
        # pcd, _ = pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=3.0)
        pcd = remove_points_from_threshold(pcd, "Z", -2.5, ">")

    return pcd


def prepare_clouds(path):
    for pc in os.listdir(path):
        file = os.path.join(path, pc)
        try:
            data = np.load(file)
            pcd = open3d.geometry.PointCloud()
            pcd.points = open3d.utility.Vector3dVector(data)
            pcd = remove_points_from_threshold(pcd, "Z", -2.5, ">")
            data = np.asarray(pcd.points)
            data = data*10
            np.save(file, data)
        except EOFError:
            os.remove(file)


if __name__ == "__main__":
    cloud_file = r"CloudData\pointcloud_0_59.npy"

    cloud = get_pcd(cloud_file)

    if cloud is not None:
        # uni_down_pcd = cloud.uniform_down_sample(20)
        # cl, ind = uni_down_pcd.remove_statistical_outlier(nb_neighbors=10, std_ratio=2.0)
        # display_inlier_outlier(uni_down_pcd, ind)
        # show_sampled_cloud(cloud, 60)
        # show_voxel(cloud, 2)
        fig, ax = show_voxel_heatmap(cloud, 2)

        plt.show()
