from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler,IncludeLaunchDescription,ExecuteProcess,TimerAction
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution, LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Declare the launch argument for the rosbag file
    declared_arguments = [
        DeclareLaunchArgument(
            'rosbag_file',
            default_value='/home/donato/ros2_ws/src/my_bot/bags/RosBags/RosBags_0.db3',  # Absolute path to your rosbag
            description='Path to the rosbag file'
        ),
    ]

    # Command to run ros2 bag play with the path to the rosbag file
    play_bag_command = ExecuteProcess(
        cmd=['ros2', 'bag', 'play', LaunchConfiguration('rosbag_file'), '--rate', '1.0', '--delay', '5'],
        output='screen'
    )

    # Repeat the command indefinitely by using a TimerAction or continuous process restarts
    repeat_playback = ExecuteProcess(
        cmd=['ros2', 'bag', 'play', LaunchConfiguration('rosbag_file'), '--rate', '1.0', '--delay', '5'],
        output='screen',
        respawn=True,  # This will restart the rosbag play command once it finishes
        respawn_delay=1.0  # Delay before restarting the rosbag play command
    )

    return LaunchDescription(declared_arguments + [repeat_playback])
