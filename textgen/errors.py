class InvalidATeamError(Exception):
    """Raised when invalid demix source is specified"""
    pass

class TooManyAteamError(Exception):
    """Raised when more than 2 A-team sources are specified"""
    pass

class TooManyBeamletsError(Exception):
    """Raised if more than 488 beamlets are specified"""
    pass

class TooLongFolderNameError(Exception):
    """Raised when the main folder name is too long"""
    pass

class InvalidMainFolderNameError(Exception):
    """Raised when the main folder name is invalid"""
    pass

class InvalidDateTimeError(Exception):
    """Raised when the specified date/time is invalid"""
    pass

class InvalidElevationError(Exception):
    """Raised when the specified elevation is invalid"""
    pass

class InvalidAverageError(Exception):
    """Raised if the averaging parameters are wrong"""
    pass

class InvalidSubbandError(Exception):
    """Raised if the subband list is invalid"""
    pass

class InvalidDurationError(Exception):
    """Raised if the specified duration is invalid"""
    pass

class OutOfBoundsSubBandError(Exception):
    """Raised if the specified subband is outside the filter"""
    pass

class InvalidSubBandOrderError(Exception):
    """Raised if B>A in A..B"""
    pass

class NoGoodLBACalibratorError(Exception):
    """Raised if no good calibrator could be found"""
    pass
