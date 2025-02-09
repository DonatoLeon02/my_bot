# Copyright 2020 ros2_control Development Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler,IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution, LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Declare arguments
    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
           "gui",
           default_value="true",
           description="Start RViz2 automatically with this launch file.",
        )
    )
#    declared_arguments.append(
#        DeclareLaunchArgument(
#            "use_mock_hardware",
#            default_value="false",
#            description="Start robot with mock hardware mirroring command to its states.",
#        )
#    )

    # Initialize Arguments
    gui = LaunchConfiguration("gui")
#    use_mock_hardware = LaunchConfiguration("use_mock_hardware")

    # Get URDF via xacro
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare("my_bot"), "description", "realbot.urdf.xacro"]
            ),
#            " ",
#            "use_mock_hardware:=",
#            use_mock_hardware,
        ]
    )
    robot_description = {"robot_description": robot_description_content}

    robot_controllers = PathJoinSubstitution(
        [
            FindPackageShare("my_bot"),
            "config",
            "realbot_controllers.yaml",
        ]
    )
    rviz_config_file = PathJoinSubstitution(
       [FindPackageShare("my_bot"), "config", "real_bot.rviz"]
   )

    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            robot_description,
            robot_controllers
        ],
        output="both",
    )
    robot_state_pub_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[robot_description],
        remappings=[
            ("/my_bot/cmd_vel_unstamped", "/cmd_vel"),
        ],
    )
    rviz_node = Node(
       package="rviz2",
       executable="rviz2",
       name="rviz2",
       output="log",
       arguments=["-d", rviz_config_file],
       condition=IfCondition(gui),
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )

    robot_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["my_bot", "--controller-manager", "/controller_manager"],
    )

#    Delay rviz start after `joint_state_broadcaster`
    delay_rviz_after_joint_state_broadcaster_spawner = RegisterEventHandler(
       event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[rviz_node],
       )
    )

    # Delay start of robot_controller after `joint_state_broadcaster`
    delay_robot_controller_spawner_after_joint_state_broadcaster_spawner = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[robot_controller_spawner],
        )
    )

    # delay_teleop_twist_keyboard_after_controller = RegisterEventHandler(
    #     event_handler=OnProcessExit(
    #         target_action=robot_controller_spawner,
    #         on_exit=[
    #             Node(
    #                 package='teleop_twist_keyboard',
    #                 executable='teleop_twist_keyboard',
    #                 name='teleop_keyboard',
    #                 output='screen',
    #                 remappings=[('/cmd_vel', '/my_bot/cmd_vel')],
    #                 parameters=[{'stamped': True}],
    #                 prefix='gnome-terminal --'
    #             ),
    #         ],
    #     )
    # )

    joystick_launch_file = PathJoinSubstitution([FindPackageShare("my_bot"), "launch", "joystick.launch.py"])

    # Register event handler to delay joystick nodes after controller spawner
    delay_joystick_launch_after_controller = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=robot_controller_spawner,
            on_exit=[
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(joystick_launch_file)
                ),
            ],
        )
    )

    # Path to the RPLIDAR launch file
    rplidar_launch_file = PathJoinSubstitution([FindPackageShare("rplidar_ros"), "launch", "rplidar_a1_launch.py"])

    # Include the RPLIDAR launch file
    rplidar_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(rplidar_launch_file)
    )

    nodes = [
        control_node,
        robot_state_pub_node,
        joint_state_broadcaster_spawner,
        delay_rviz_after_joint_state_broadcaster_spawner,
        delay_robot_controller_spawner_after_joint_state_broadcaster_spawner,
        #delay_teleop_twist_keyboard_after_controller,
        delay_joystick_launch_after_controller,
        rplidar_node
    ]

    return LaunchDescription(declared_arguments + nodes)