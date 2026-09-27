from threading import Thread
import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.node import Node
from pymoveit2 import MoveIt2, GripperInterface
from pymoveit2.robots import practise as robot  

def main():
    rclpy.init()
    node = Node("practise_pick_and_place")   
    callback_group = ReentrantCallbackGroup()

    moveit2 = MoveIt2(
        node=node,
        joint_names=robot.joint_names(),
        base_link_name=robot.base_link_name(),
        end_effector_name=robot.end_effector_name(),
        group_name=robot.MOVE_GROUP_ARM,
        callback_group=callback_group,
    )
    moveit2.max_velocity = 0.5       
    moveit2.max_acceleration = 0.5
    gripper = GripperInterface(
        node=node,
        gripper_joint_names=robot.gripper_joint_names(),
        open_gripper_joint_positions=robot.OPEN_GRIPPER_JOINT_POSITIONS,
        closed_gripper_joint_positions=robot.CLOSED_GRIPPER_JOINT_POSITIONS,
        gripper_group_name=robot.MOVE_GROUP_GRIPPER,
        callback_group=callback_group,
    )

    executor = rclpy.executors.MultiThreadedExecutor(2)
    executor.add_node(node)
    Thread(target=executor.spin, daemon=True).start()
    node.create_rate(1.0).sleep()   
    
    HOME        = [0.0, 0.0, 0.0]   
    PICK_ABOVE  = [0.0, 1.0, 1.0]  
    PICK_DOWN   = [0.0, 0.0, 1.0]   
    PLACE_ABOVE = [0.0, 1.0, 1.0]    
    PLACE_DOWN  = [1.0, 1.0, 1.0]    

    def move_arm(target, label):
        node.get_logger().info(f"→ Arm: {label}")
        moveit2.move_to_configuration(target)
        moveit2.wait_until_executed()

    node.get_logger().info("=== 开始 pick-and-place ===")

    move_arm(HOME, "home")
    move_arm(PICK_ABOVE, "pick above")
    move_arm(PICK_DOWN, "pick down")

    node.get_logger().info("→ Gripper: close")
    gripper.close()
    gripper.wait_until_executed()

    move_arm(PICK_ABOVE, "lift up")
    move_arm(PLACE_ABOVE, "place above")
    move_arm(PLACE_DOWN, "place down")

    node.get_logger().info("→ Gripper: open")
    gripper.open()
    gripper.wait_until_executed()

    move_arm(HOME, "back to home")

    node.get_logger().info("=== 完成 ===")
    rclpy.shutdown()
    exit(0)

if __name__ == "__main__":
    main()
