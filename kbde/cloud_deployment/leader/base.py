"""
A module to check to see if the instance it is being run on is a "leader"

A "leader" is a single instance in an autoscling group which is responsible for
    running tasks which should only be run once, such as Django database migrations.
"""

import requests


class Leader:

    def get_is_leader(self):
        """
        Returns `True` if this instance is a leader, `False` otherwise
        """
        try:
            instance_id = self.get_instance_id()
            all_instance_ids = self.get_all_instance_ids()

            return instance_id == all_instance_ids[0]

        except requests.exceptions.ConnectionError:
            # We were not able to connect to the servers which give us this information
            # We are likely not even on this platform

            return None

    def get_all_instance_ids(self):
        """
        Return a list of instance ids from the instance group of this machine.

        This function should return the instances in a deterministic order.
        """
        raise NotImplementedError("{self.__class__.__name__} must implement `self.get_all_instance_ids()`")

    def get_instance_id(self):
        """
        Return the instance id for the current running insance
        """
        raise NotImplementedError("{self.__class__.__name__} must implement `self.get_insance_id()`")
