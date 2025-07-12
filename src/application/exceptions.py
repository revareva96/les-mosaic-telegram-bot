class ApplicationException(Exception):
    pass


class NotEnoughUpdateInfoException(ApplicationException):
    pass

class NotCorrectedProductType(ApplicationException):
    pass
