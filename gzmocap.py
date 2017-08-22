""" SITL MOCAP simulator for PX4 obtaining location information from Gazebo"""
__author__ = "William Koch"

import time
import pygazebo
import pygazebo.msg.poses_stamped_pb2

# There is no Python 3 support for drone kit so use trollius
# WARNING: trollius is depreciated
import trollius
from trollius import From
import trollius as asyncio

from dronekit import connect, Command, LocationGlobal, Vehicle
from pymavlink import mavutil
import time, argparse

class GazeboMOCAP(object):
    """
    PX4 will timeout with "mocap timeout" if there is not a message
    sent at least ever 0.2 seconds see src/modules/local_position_estimator/sensors/mocap.cpp
    Look at this discussion for frame conversions
    https://github.com/mavlink/mavros/issues/216


    The reason we are losing the heartbeat is because we start the second mavlink connection
    What we need is to either share the connection or set up and communicate on another mavlink instance

    https://github.com/PX4/Devguide/issues/181
    """
    def __init__(self, gazebo_host, gazebo_port, px4_host=None, px4_port=None, vehicle=None):
        if vehicle:
            self.vehicle = vehicle
        else:
            px4_connection_string = "{}:{}".format(px4_host, px4_port)
            self.vehicle = connect(px4_connection_string, wait_ready=True)

        self.gazebo_host = gazebo_host
        self.gazebo_port = gazebo_port

    def ENUtoNEDBodyFrame(self, x, y, z):
        return (x, -y, -z)

    def _send_att_pos_mocap(self, q, x, y, z):
        """
        http://mavlink.org/messages/common#ATT_POS_MOCAP
        http://osrf-distributions.s3.amazonaws.com/gazebo/msg-api/7.1.0/poses__stamped_8proto.html
        """
        time_usec = int(round(time.time() * 1000000))
        self.vehicle._master.mav.att_pos_mocap_send(time_usec, q, x, y, z)

    def _poses_callback(self, data):
        msg = pygazebo.msg.poses_stamped_pb2.PosesStamped()
        msg.ParseFromString(data)
        for pose in msg.pose:
            if pose.name == "iris":
                pos = pose.position 
                o = pose.orientation
                (ned_x, ned_y, ned_z) = o_ned = self.ENUtoNEDBodyFrame(o.x, o.y, o.z)
                q = [o.w, ned_x, ned_y, ned_z]
                (ned_pos_x, ned_pos_y, ned_pos_z) = self.ENUtoNEDBodyFrame(pos.x, pos.y, pos.z)
                self._send_att_pos_mocap(q, ned_pos_x, ned_pos_y, ned_pos_z)

    def _get_poses(self):
        #start listening for the event
        manager = yield From(pygazebo.connect((self.gazebo_host, self.gazebo_port)))
        subscriber = manager.subscribe('/gazebo/default/pose/info', 'gazebo.msgs.PosesStamped', self._poses_callback)
        while True:
            yield From(subscriber.wait_for_connection())

    def start(self):
        loop = trollius.get_event_loop()
        loop.run_until_complete(self._get_poses())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gzhost", default="localhost", help="Gazebo SITL host")
    parser.add_argument("--gzport", default=11345, help="Gazebo SITL port")
    parser.add_argument("--px4host", default="localhost", help="PX4 onboard MAVLink host")
    parser.add_argument("--px4port", default=14550, help="PX4 onboard MAVLink port")

    args = parser.parse_args()
    mocap = GazeboMOCAP(args.gzhost, args.gzport, args.px4host, args.px4port)
    mocap.start()
