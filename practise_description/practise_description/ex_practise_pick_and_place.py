from threading import Thread
import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.node import Node

from pymoveit2 import MoveIt2, GripperInterface
from pymoveit2.robots import practise as robot   # ← 只改这里的 import


def main():
    # ---- 初始化 ROS(照抄) ----
    rclpy.init()
    node = Node("practise_pick_and_place")   # 节点名,自己起,一般 <robot_name>_pick_and_place
    callback_group = ReentrantCallbackGroup()

    # ---- 手臂客户端(照抄,参数从名片文件读) ----
    moveit2 = MoveIt2(
        node=node,
        joint_names=robot.joint_names(),
        base_link_name=robot.base_link_name(),
        end_effector_name=robot.end_effector_name(),
        group_name=robot.MOVE_GROUP_ARM,
        callback_group=callback_group,
    )
    moveit2.max_velocity = 0.5       # 0~1,越小越慢
    moveit2.max_acceleration = 0.5

    # ---- 夹爪客户端(如果没夹爪,删这一段) ----
    gripper = GripperInterface(
        node=node,
        gripper_joint_names=robot.gripper_joint_names(),
        open_gripper_joint_positions=robot.OPEN_GRIPPER_JOINT_POSITIONS,
        closed_gripper_joint_positions=robot.CLOSED_GRIPPER_JOINT_POSITIONS,
        gripper_group_name=robot.MOVE_GROUP_GRIPPER,
        callback_group=callback_group,
    )

    # ---- 后台线程 spin(照抄,别改) ----
    executor = rclpy.executors.MultiThreadedExecutor(2)
    executor.add_node(node)
    Thread(target=executor.spin, daemon=True).start()
    node.create_rate(1.0).sleep()   # 等 1 秒让 action 连接建好,不能省

    # ============================================================
    # 姿态定义(改这里)
    # 数组长度和顺序 = joint_names() 的顺序
    # 数值单位:revolute joint 是弧度,prismatic joint 是米
    # ============================================================
    HOME        = [0.0, 0.0, 0.0]   # 原位(所有关节归零一般是好选择)
    PICK_ABOVE  = [0.0, 1.0, 1.0]   # 抓取点正上方
    PICK_DOWN   = [0.0, 0.0, 1.0]   # 抓取点(下降到物体高度)
    PLACE_ABOVE = [0.0, 1.0, 1.0]    # 放置点正上方
    PLACE_DOWN  = [1.0, 1.0, 1.0]    # 放置点

    # ---- 辅助函数(照抄) ----
    def move_arm(target, label):
        node.get_logger().info(f"→ Arm: {label}")
        moveit2.move_to_configuration(target)
        moveit2.wait_until_executed()

    # ============================================================
    # 动作序列(可以改,但基本 8 步流程适用于大多数 pick-and-place)
    # ============================================================
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

    # ---- 收尾(照抄) ----
    node.get_logger().info("=== 完成 ===")
    rclpy.shutdown()
    exit(0)


if __name__ == "__main__":
    main()
