from time import time, sleep

__all__ = ['Rate']

class Rate(object):
    """
    Convenience class for sleeping in a loop at a specified rate
    From ROS: https://github.com/ros/ros_comm/blob/indigo-devel/clients/rospy/src/rospy/timer.py
    """
    def __init__(self, hz):
        """
        Constructor.
        :param hz: hz rate to determine sleeping
        """
        self.last_time = float('inf')
        self.sleep_dur = 1./hz

    def _remaining(self, curr_time):
        """
        Calculate the time remaining for rate to sleep.
        :param curr_time: current time
        :return: time remaining
        """
        # detect time jumping backwards
        if self.last_time > curr_time:
            self.last_time = curr_time

        # calculate remaining time
        elapsed = curr_time - self.last_time
        return max(0, self.sleep_dur - elapsed)

    def sleep(self):
        """
        Attempt sleep at the specified rate. sleep() takes into account the time elapsed since the last successful sleep().
        """
        curr_time = time()
        sleep(self._remaining(curr_time))
        self.last_time = self.last_time + self.sleep_dur

        # detect time jumping forwards, as well as loops that are inherently too slow
        if curr_time - self.last_time > self.sleep_dur * 2:
            self.last_time = curr_time


