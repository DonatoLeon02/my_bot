from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
from launch.actions import DeclareLaunchArgument
import xacro
import os

def generate_launch_description():
    # Path to your URDF file
    urdf_file = os.path.join( 
        get_package_share_directory('my_bot'),  # acceses directory of package my_bot
        'description', # look inside description folder
        'robot.urdf.xacro'  # look at selected file
    )

    robot_description_content = xacro.process_file(urdf_file).toxml() # convert Xacro file to xml

    # Path to your RViz configuration file
    rviz_config_file = os.path.join( 
        get_package_share_directory('my_bot'),  # Access directory of package my_bot
        'config', # look in config folder
        'view_bot.rviz'  # look at selected file
    )

    return LaunchDescription([
        DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation time if true'
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description_content},
                        {'use_sim_time': LaunchConfiguration('use_sim_time')}]
        ),

        # Launch Joint State Publisher
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            output='screen'
        ),

        # Launch Joint State Publisher GUI
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            output='screen'
        ),

        # Launch RViz
        Node(
            package='rviz2',
            executable='rviz2',
            output='screen',
            arguments=['-d', rviz_config_file]
        ),
    ])
