# practise-arm

A 3-DOF SCARA robotic arm with a 2-finger parallel gripper, performing pick-and-place in ROS 2 Humble using MoveIt 2 and pymoveit2.

Built as a portfolio project to prepare for HiWi applications at RWTH Aachen.

---

## Demo

*(Demo video coming soon.)*

---

## Tech Stack

- **OS**: Ubuntu 22.04 (VirtualBox VM)
- **ROS Distribution**: ROS 2 Humble
- **Simulation**: `mock_components/GenericSystem` (fake hardware)
- **Motion Planning**: MoveIt 2 (RRTConnect via OMPL)
- **Python API**: [pymoveit2](https://github.com/AndrejOrsula/pymoveit2)
- **Robot Description**: URDF + xacro
- **Build System**: colcon

---

## Project Structure

    practise-arm/
    ├── practise_description/          # Robot description package
    │   ├── urdf/
    │   │   └── practise.xacro         # 3-DOF SCARA + 2-finger gripper
    │   ├── launch/
    │   │   ├── display_launch.py      # RViz only
    │   │   └── gazebo_launch.py       # Gazebo integration (WIP)
    │   ├── practise_description/
    │   │   └── ex_practise_pick_and_place.py   # Main script
    │   └── config/
    │       └── cotrollers.yaml
    │
    └── practise_movelt_config/        # MoveIt configuration
        ├── config/
        │   ├── practise.srdf          # Planning groups, disable_collisions
        │   ├── joint_limits.yaml
        │   ├── ros2_controllers.yaml
        │   └── ...
        └── launch/
            └── demo.launch.py         # Full MoveIt system launcher

---

## Prerequisites

- Ubuntu 22.04
- ROS 2 Humble ([install guide](https://docs.ros.org/en/humble/Installation.html))
- MoveIt 2:

      sudo apt install ros-humble-moveit

- pymoveit2 (external library, clone into your workspace):

      cd ~/ros2_ws/src
      git clone https://github.com/AndrejOrsula/pymoveit2.git

---

## Quick Start

**1. Clone this repo into your ROS 2 workspace**

    cd ~/ros2_ws/src
    git clone https://github.com/YuShen1402/practise-arm.git
    mv practise-arm/* .

**2. Build**

    cd ~/ros2_ws
    colcon build --symlink-install
    source install/setup.bash

**3. Launch the MoveIt system (Terminal 1)**

    ros2 launch practise_movelt_config demo.launch.py

**4. Run the pick-and-place script (Terminal 2)**

    source ~/ros2_ws/install/setup.bash
    ros2 run practise_description ex_practise_pick_and_place

The arm will move through an 8-step sequence: home → pick above → pick down → close gripper → lift → place above → place down → open gripper → home.

---

## Design Decisions

*(Coming next — will document why SCARA over 6-DOF, why mock over Gazebo, why pymoveit2 over raw action clients.)*

---

## Debugging Journey

*(Coming next — will document the hardest bugs and how they were solved.)*

---

## Roadmap

- [x] URDF + xacro robot description
- [x] MoveIt config via Setup Assistant
- [x] pymoveit2 Python control
- [x] End-to-end pick-and-place in mock mode
- [ ] Gazebo integration
- [ ] Demo video
- [ ] Real hardware port (future work)

---

## Author

Yu Shen — MSc Robotic Systems Engineering @ RWTH Aachen (starting October 2026)
