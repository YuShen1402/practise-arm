# practise-arm

> A 3-DOF SCARA robotic arm with a 2-finger parallel gripper, performing pick-and-place in ROS 2 Humble using MoveIt 2 and pymoveit2.

Built as a portfolio project to prepare for HiWi applications at RWTH Aachen (starting October 2026).

![ROS 2](https://img.shields.io/badge/ROS%202-Humble-blue)
![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04-orange)
![MoveIt 2](https://img.shields.io/badge/MoveIt-2-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## Table of Contents

- [Demo](#demo)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Design Decisions](#design-decisions)
- [Debugging Journey](#debugging-journey)
- [Roadmap](#roadmap)
- [Author](#author)

---

## Demo

*(Demo video coming soon — will be linked here.)*

The arm executes an 8-step pick-and-place sequence in RViz:
`home → pick_above → pick_down → close gripper → lift → place_above → place_down → open gripper → home`.

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

---

## Design Decisions

This section documents *why* the project was built this way, not just *what* it does.

### Why a 3-DOF SCARA arm instead of a 6-DOF arm?

A pick-and-place task from a flat surface only needs the gripper to point straight down and reach any XY position with adjustable height. That is exactly what SCARA provides:

- All three revolute joints rotate around the vertical Z axis.
- The gripper naturally faces down — no need to plan orientation.
- 3 DOF is enough for XY position and vertical motion.

A 6-DOF arm would be overkill: harder to plan, more collision cases to handle, and more parameters to tune, all for capabilities the task doesn't need. SCARA is the **minimal viable structure** for this scope.

### Why `mock_components` instead of Gazebo?

The goal of this project is to validate the full software pipeline — URDF → MoveIt → controllers → hardware interface — not to simulate physics.

- `mock_components/GenericSystem` writes commands into memory and reports them back as state. No physics, no latency, no noise.
- It boots in seconds, stays stable, and lets me focus on ROS integration.
- Gazebo would add hours of debugging (plugin versions, physics parameters, launch ordering) for zero gain at this stage.

Crucially, the architecture is portable: switching to Gazebo (or real hardware) means **swapping only the hardware interface plugin** — the URDF, controllers, MoveIt config, and Python code stay identical.

### Why `pymoveit2` instead of writing raw ROS action clients?

`pymoveit2` is a Python wrapper around the MoveIt action interface. Without it, sending a single motion goal would require:

- Creating an action client for `/move_action`
- Subscribing to `/joint_states` for the current state
- Constructing a `MotionPlanRequest` with joint constraints, tolerances, and planning parameters
- Handling goal acceptance, feedback callbacks, result futures, and error codes

That's ~50 lines of boilerplate per motion. With `pymoveit2`:

    moveit2.move_to_configuration([0.5, 0.3, 0.2])
    moveit2.wait_until_executed()

Two lines. This lets me focus on task logic (the pick-and-place sequence) instead of ROS plumbing. It's community-tested, official, and there's no reason to reinvent the wheel for a portfolio project.

---

## Debugging Journey

Real projects always hit walls. Here are the two that took the longest and taught the most.

### Bug 1: Every motion failed with "Planning failed! FAILURE"

**Symptom**: After a clean build, every step of the pick-and-place script failed. The Python client only reported `Planning failed! Error code: FAILURE` — no further details.

**Investigation**: Initial attempts to fix the script itself went nowhere. The client only sees a short status code; the real error lives in the server node's log. I redirected the launch output to a file and grepped `move_group`'s prefix for keywords:

    ros2 launch practise_movelt_config demo.launch.py 2>&1 | tee /tmp/demo_log.txt
    grep -aE "move_group-2.*(WARN|ERROR|collision)" /tmp/demo_log.txt

**Root cause**: `Start state appears to be in collision`. The gripper fingers overlapped the wrist plate at the initial pose. Setup Assistant's default collision sampling density (10,000 samples) had missed the geometry overlap.

**Fix**: Manually added `<disable_collisions>` entries to the SRDF:

    <disable_collisions link1="left_finger"  link2="wrist_plate" reason="Adjacent"/>
    <disable_collisions link1="right_finger" link2="wrist_plate" reason="Adjacent"/>
    <disable_collisions link1="left_finger"  link2="right_finger" reason="Never"/>

Rebuilt, retried — a second collision surfaced (`lower_arm` vs fingers). Added two more entries. Third try worked.

**Lesson**: **Client only shows *what* failed. Server logs show *why*.** From now on, I go straight to server logs when the client reports a generic failure.

### Bug 2: Setup Assistant silently overwriting manual edits

**Symptom**: After tweaking my URDF and re-running Setup Assistant to refresh the MoveIt config, previous manual edits vanished — `joint_limits.yaml` numbers reverted to integers, `ros2_controllers.yaml` lost my custom gripper controller, and a duplicate `ros2_control` block appeared.

**Root cause**: Setup Assistant is a **generator, not an editor**. Every regeneration rewrites its output files from scratch based on the current URDF + SRDF, discarding any hand edits.

**Fix**: After every Setup Assistant run, re-verify:

- `joint_limits.yaml`: convert integer velocities/accelerations back to floats
- `ros2_controllers.yaml`: re-add manually configured controllers (gripper_controller)
- `package.xml`: re-fill email fields
- URDF: remove duplicate `ros2_control` blocks generated by `<robot>.ros2_control.xacro`

**Lesson**: Auto-generators are a starting point, not a source of truth. **Any file the generator produces is a candidate for re-verification after regeneration.**

---

## Roadmap

- [x] URDF + xacro robot description (3-DOF SCARA + 2-finger gripper)
- [x] MoveIt config via Setup Assistant
- [x] pymoveit2 Python control
- [x] End-to-end pick-and-place in mock mode
- [ ] Demo video
- [ ] Gazebo integration
- [ ] Real hardware port (future work)

---

## Author

**Yu Shen** — MSc Robotic Systems Engineering @ RWTH Aachen (starting October 2026)

- BSc Mechanical Engineering, Nanjing Forestry University (2026)
- Currently transitioning from mechanical design to robotics software

---

## License

MIT
