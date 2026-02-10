"""
Filename Utility Module

Provides utilities for generating unique filenames based on timestamps. Used to
create unique names for saving annotated measurement results without overwriting
previous saves.
"""

from datetime import datetime


class Filename:
    """
    Utility class for generating timestamped filenames.

    Creates unique filenames based on current date and time, useful for saving
    multiple results without manual conflict resolution.
    """

    @staticmethod
    def main():
        """
        Generate a timestamp for use as a filename.

        Returns the current date and time as a datetime object, which can be
        converted to a string to create a unique filename for saving results.

        Returns:
            datetime.datetime: The current date and time object with microsecond precision.
                              Can be converted to string via str() for use as filename.
        """
        return datetime.now()
