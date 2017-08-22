# Gazebo MOCAP

This script simulates a motion capture system using Gazebo to supply a MAVLink enabled drone with position data rather than GPS. 
The vehicles pose data is obtained in Gazebo through the
[pygazebo](https://github.com/jpieper/pygazebo/) module and sends
[ATT_POS_MOCAP](http://mavlink.org/messages/common#ATT_POS_MOCAP) MAVLink
messages using [DroneKit](https://github.com/dronekit/dronekit-python/). 
An overview of using external position estimation for PX4 can be found
[here](https://dev.px4.io/en/ros/external_position_estimation.html). 

# Dependencies 

* [pygazebo](https://github.com/jpieper/pygazebo/)
* [DroneKit](https://github.com/dronekit/dronekit-python/)

# Usage

Use default Gazebo connection `localhost:11345` and default normal MAVLink PX4 connection
`localhost:14550`,

```
python gazebo-mocap.py 
```

Optionally supply arguments for the connection, 

```
usage: gazebo-mocap.py [-h] [--gzhost GZHOST] [--gzport GZPORT]
                       [--px4host PX4HOST] [--px4port PX4PORT]

optional arguments:
  -h, --help         show this help message and exit
  --gzhost GZHOST    Gazebo SITL host
  --gzport GZPORT    Gazebo SITL port
  --px4host PX4HOST  PX4 onboard MAVLink host
  --px4port PX4PORT  PX4 onboard MAVLink port
```

# Additional Notes

This script cannot be run sharing the same MAVLink connection used by your
offboard flight computer. A heartbeat timeout will occur causing the motion
capture system to halt and the drone to fly out of control. For this reason the
MAVLink connection by default is for  [normal
mode](https://github.com/PX4/Devguide/issues/181) while your flight computer should use onboard mode.  To share the same MAVLink connection this script should run in a separate thread/process and share the same dronekit vehicle object. 
