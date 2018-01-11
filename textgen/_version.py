"""Version module.

This module stores the version number and the changelog
"""

# Version number
__version__ = '0.1.3'

# Changelog
def changelog():
    """
    Changelog:
    0.1.3   2017/12/08   Use proper labels for reference beams.
                         Demixing interval is forced to be an integer multiple 
                         of the averaging parameters.
    0.1.2   2017/12/08   Ignore spaces in the pointing string.
                         Warn if the Sun is less than 30 degrees away.
    0.1.0   2017/12/08   Code supports all imaging modes for both LBA and HBA.
    """
