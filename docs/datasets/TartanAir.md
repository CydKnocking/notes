[TartanAir link](https://theairlab.org/tartanair-dataset/)

Type: `synthesized`

Data type: `Stereo RGB, Stereo Depth, flow, segmentation, Pose`

### How to process the data ([link](https://github.com/castacks/tartanair_tools/blob/master/data_type.md))

#### Camera intrinsics:
```
fx = 320.0  # focal length x
fy = 320.0  # focal length y
cx = 320.0  # optical center x
cy = 240.0  # optical center y

fov = 90 deg # field of view

width = 640
height = 480
```

#### Pose format

- Each line is a camera pose of the corresponding color frame with respect to the world frame.
- In each line: `tx ty tz qx qy qz qw`
- **Important:** the motion is in NED frame, with x-axis pointing to the cam's forward, the y-axis to the right, and the z-axis to the downward.

**Read the camera pose and depth, convert the coordinate system, and generate the point cloud in the world coordinate system**

注意:

1. 读取pose后需要从NED坐标系转换到一般的相机右手坐标系(x右，y下，z前)
   
2. 转换成4x4后的pose矩阵就是从相机坐标系到世界坐标系矩阵，不用取逆inv
   
3. 转换成4x4后的pose矩阵左乘point。
   
```
import os, sys
import cv2
import numpy as np
from scipy.spatial.transform import Rotation as R

# 加载深度文件
def load_depth(depth_file):
    return np.load(depth_file)

# 加载相机位姿真值文件（四元数格式，NED坐标系）
def load_poses(pose_file):
    """加载相机位姿真值文件
        Args:
        - pose_file (str): 位姿文件名

        Returns:
        - poses (List[np.array]): 位姿列表，每个都是4x4的矩阵
    """
    poses = []
    with open(pose_file, 'r') as f:
        for line in f:
            # 每一行格式为: tx ty tz qx qy qz qw
            pose_data = np.array([float(x) for x in line.strip().split()])
            
            ######## NED坐标系转到一般的右手坐标系 ########
            pose_data = pose_data[[1,2,0,4,5,3,6]]
            
            # 提取平移向量 (tx, ty, tz)
            translation = pose_data[:3]
            
            # 提取四元数 (qx, qy, qz, qw)
            quaternion = pose_data[3:]
            
            # 将四元数转换为旋转矩阵
            rotation = R.from_quat(quaternion).as_matrix()
            
            # 构建4x4的位姿矩阵
            pose_matrix = np.eye(4)
            pose_matrix[:3, :3] = rotation
            pose_matrix[:3, 3] = translation
            
            # 添加到位姿列表
            poses.append(pose_matrix)
    
    return poses

def project_to_world(depth_map, K, pose):
    """将深度图中的像素点从相机坐标系转换到世界坐标系
        Args:
        - depth_map (np.array): 深度图，大小为 (height, width)
        - K (np.array): 相机内参矩阵，大小为 (3, 3)
        - pose (np.array): 4x4 位姿矩阵，包含相机的旋转和平移

        Returns:
        - world_points (np.array): 转换后的世界坐标系中的点，形状为 (N, 3)，其中 N 为点的数量
    """
    height, width = depth_map.shape
    mask = depth_map > 0

    # 生成像素网格坐标
    u, v = np.meshgrid(np.arange(width), np.arange(height))
    u = u[mask]
    v = v[mask]

    depth_map = depth_map[mask]

    # 将像素坐标转换为相机坐标系
    x_camera = (u - K[0, 2]) * depth_map / K[0, 0]
    y_camera = (v - K[1, 2]) * depth_map / K[1, 1]
    z_camera = depth_map

    # 将相机坐标系中的点（x_camera, y_camera, z_camera）转换为世界坐标系
    # 需要将其从相机坐标系转换为世界坐标系
    camera_points = np.vstack((x_camera.flatten(), y_camera.flatten(), z_camera.flatten(), np.ones_like(x_camera.flatten())))
    
    ##############################
    # 位姿矩阵为 4x4，根据定义直接左乘来将相机坐标系转换到世界坐标系
    world_points_homogeneous = pose @ camera_points
    
    return world_points_homogeneous[:3, :].T  # 只返回 x, y, z 坐标
```
