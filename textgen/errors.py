import sys
import tkMessageBox

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

def getErrorMessage():
    """
    Returns the appropriate error message for the most recently raised 
    exception.
    """
    return {
        'TooLongFolderNameError': 'Main folder name cannot be longer than 20 '\
                                  'characters.',
        'InvalidMainFolderNameError': 'Invalid main folder name.',
        'InvalidDateTimeError': 'Entered date/time is invalid.',
        'InvalidElevationError': 'Specified elevation is invalid.',
        'InvalidAverageError': 'Invalid averaging parameters specified.',
        'InvalidSubbandError': 'Invalid subband specified.',
        'TooManyBeamletsError': 'No. of subbands x pointings cannot be more '\
                                'than 488.',
        'InvalidDurationError': 'Specified target scan duration is invalid.',
        'OutOfBoundsSubBandError': 'One of the specified subband is outside '\
                                   'the selected filter.',
        'InvalidSubBandOrderError': 'Invalid subband specification. X cannot '\
                                    'be greater than Y in "X..Y".',
        'InvalidATeamError': 'Invalid A-team source.',
        'TooManyAteamError': 'Cannot demix more than 2 sources.',
        'NoGoodLBACalibratorError': 'Could not find a good calibrator.',
    }[sys.exc_type.__name__]

def showErrorPopUp(message):
    """
    Display an error pop-up message
    """
    tkMessageBox.showerror('Error', message)

def showWarningPopUp(message):
    """
    Display a warning pop-up message
    """
    tkMessageBox.showinfo('Warning', message)
