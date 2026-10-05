import launch
import launch_ros
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # 1.声明一个launch的参数
    action_declare_arg_background_g = launch.actions.DeclareLaunchArgument('launch_arg_bg',default_value='150')
    # 2.把launch参数手动传递给某个节点
    
    """
    产生launch的描述
    """
    action_node_turtlesim_node = launch_ros.actions.Node(
        package='turtlesim',
        executable='turtlesim_node',
        parameters=[{'background_g':launch.substitutions.LaunchConfiguration('launch_arg_bg',default='150')}],
        output = 'screen'
    )

    return launch.LaunchDescription([
        # actions动作        
        action_declare_arg_background_g,
        action_node_turtlesim_node,
        
    ])