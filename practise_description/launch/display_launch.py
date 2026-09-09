import os
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue   # ← 加这一行导入
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_share = get_package_share_directory('practise_description')
    urdf_path = os.path.join(pkg_share, 'urdf', 'practise.xacro')
    
    # 用 ParameterValue 包起来,明确说是字符串
    robot_description = {
        'robot_description': ParameterValue(
            Command(['xacro ', urdf_path]),
            value_type=str
        )
    }

    return LaunchDescription([
        Node(package='robot_state_publisher',
             executable='robot_state_publisher',
             parameters=[robot_description]),
        Node(package='joint_state_publisher_gui',
             executable='joint_state_publisher_gui'),
        Node(package='rviz2',
             executable='rviz2'),
    ])
