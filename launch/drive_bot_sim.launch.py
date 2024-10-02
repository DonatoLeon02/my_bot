from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
import xacro
import os

def generate_launch_description():
    # Path to your URDF file
    urdf_file = os.path.join(
        get_package_share_directory('my_bot'),  # Replace with your package name
        'description',
        'robot.urdf.xacro'  # Replace with your actual URDF file name
    )
    robot_description_content = xacro.process_file(urdf_file).toxml()

    # Path to RViz configuration file
    rviz_config_file = os.path.join(
        get_package_share_directory('my_bot'),  # Replace with your package name
        'config',
        'sim_lidar.rviz'  # Replace with your actual RViz config file name
    )

    #Path to Gazebo world file
    gazebo_world_file = os.path.join(
        get_package_share_directory('my_bot'),  # Replace with your package name
        'worlds',  # Make sure this is the correct directory
        'maze.world'  # Replace with your actual world file name
    )


    # Launch robot state publisher node
    node_robot_state_publisher = Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description_content},
                        {'use_sim_time': True}]
        )

    # Include the Gazebo launch file, provided by the gazebo_ros package
    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
                launch_arguments={'world':gazebo_world_file}.items()
             )

    # Run the spawner node from the gazebo_ros package. The entity name doesn't really matter if you only have a single robot.
    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-topic', 'robot_description',
                                   '-entity', 'my_bot'],
                        output='screen')

    # Launch RViz node
    node_rviz = Node(
            package='rviz2',
            executable='rviz2',
            output='screen',
            arguments=['-d', rviz_config_file]
        )
    
    node_teleop = Node(
        package='teleop_twist_keyboard',
        executable='teleop_twist_keyboard',
        output='screen',
        prefix='gnome-terminal --',  # This will open a new terminal for the teleop node
    )

    
    return LaunchDescription([
        node_robot_state_publisher,
        gazebo,
        spawn_entity,
        node_rviz,
        node_teleop
    ])