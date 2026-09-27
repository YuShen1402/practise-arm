import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import xacro

def generate_launch_description():

    xacro_path = os.path.join(
        get_package_share_directory('practise_description'),      
        'urdf', 'practise.xacro')                    
    robot_description = xacro.process_file(
        xacro_path,
        mappings={'use_gazebo': 'true'}                
    ).toxml()

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('gazebo_ros'),
                         'launch', 'gazebo.launch.py')))
    rsp = Node(package='robot_state_publisher',
               executable='robot_state_publisher',
               parameters=[{'robot_description': robot_description}])
    spawn = Node(package='gazebo_ros',
                 executable='spawn_entity.py',
                 arguments=['-topic', 'robot_description',   
                            '-entity', 'practise',       
                            '-z', '0.05'],            
                 output='screen')

    load_jsb = Node(package='controller_manager',
                    executable='spawner',
                    arguments=['joint_state_broadcaster'],   
                    output='screen')
    load_arm = Node(package='controller_manager',
                    executable='spawner',
                    arguments=['arm_controller'],          
                    output='screen')
    load_gripper = Node(package='controller_manager',
                        executable='spawner',
                        arguments=['gripper_controller'],  
                        output='screen')


    return LaunchDescription([
        gazebo, rsp, spawn,
        RegisterEventHandler(OnProcessExit(
            target_action=spawn, on_exit=[load_jsb])),
        RegisterEventHandler(OnProcessExit(
            target_action=load_jsb, on_exit=[load_arm])),
        RegisterEventHandler(OnProcessExit(
            target_action=load_arm, on_exit=[load_gripper])),
    ])

