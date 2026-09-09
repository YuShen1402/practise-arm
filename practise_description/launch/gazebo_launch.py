import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import xacro

def generate_launch_description():
    # ===== 步骤 1:展开 xacro 成 Gazebo 模式 URDF =====
    xacro_path = os.path.join(
        get_package_share_directory('practise_description'),      # ← 改包名
        'urdf', 'practise.xacro')                    # ← 改 xacro 名
    # ⚠️ 关键:必须传 mappings,否则展开的是 mock URDF
    robot_description = xacro.process_file(
        xacro_path,
        mappings={'use_gazebo': 'true'}                  # 硬编码 true,别改
    ).toxml()

    # ===== 步骤 2:引用 gazebo_ros 官方 launch(起 gzserver + gzclient) =====
    # 这一段照抄别改
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('gazebo_ros'),
                         'launch', 'gazebo.launch.py')))

    # ===== 步骤 3:起 robot_state_publisher =====
    rsp = Node(package='robot_state_publisher',
               executable='robot_state_publisher',
               parameters=[{'robot_description': robot_description}])

    # ===== 步骤 4:把机器人生成到 Gazebo 世界里 =====
    spawn = Node(package='gazebo_ros',
                 executable='spawn_entity.py',
                 arguments=['-topic', 'robot_description',   # 从这个话题读 URDF,固定
                            '-entity', 'practise',       # ← 改实体名
                            '-z', '0.05'],             # ← 改初始高度
                 output='screen')

    # ===== 步骤 5:加载三个 controller(名字要和 controllers.yaml 对上) =====
    load_jsb = Node(package='controller_manager',
                    executable='spawner',
                    arguments=['joint_state_broadcaster'],   # 固定名字,不改
                    output='screen')
    load_arm = Node(package='controller_manager',
                    executable='spawner',
                    arguments=['arm_controller'],           # ← 改成 controllers.yaml 里的名字
                    output='screen')
    load_gripper = Node(package='controller_manager',
                        executable='spawner',
                        arguments=['gripper_controller'],   # ← 改成 controllers.yaml 里的名字(没夹爪就删这段)
                        output='screen')

    # ===== 步骤 6:排顺序 —— spawn 完了再加载 jsb,jsb 完了再 arm,再 gripper =====
    # 这一段照抄别改,只在有夹爪 controller 时需要最后那行
    return LaunchDescription([
        gazebo, rsp, spawn,
        RegisterEventHandler(OnProcessExit(
            target_action=spawn, on_exit=[load_jsb])),
        RegisterEventHandler(OnProcessExit(
            target_action=load_jsb, on_exit=[load_arm])),
        RegisterEventHandler(OnProcessExit(
            target_action=load_arm, on_exit=[load_gripper])),
    ])

