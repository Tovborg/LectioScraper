class ElementNotFoundError(Exception):
    """Raised when an element is not found"""  
    def __init__(self, element, id_class=None, message="not found, this is most likely due to a lectio update. Or it's a server or login error."):
        if id_class is None:
            super().__init__(f"{element} {message}")
        else:
            super().__init__(f"{element} with id or class {id_class} {message}")

class LoginError(Exception):
    """Raised when login fails"""



class ServerError(Exception):
    # ! Need to figure out how to determine if this is a server error or a login error
    """Raised when server returns an error"""

class RequestError(Exception):
    """Raised when request fails"""
    def __init__(self, URL) -> None:
        super().__init__(f"Request to {URL} failed, this could be due to a lectio URL change or a server error. \n Please try updating the URL in the code, or try again later.")

class LectioLayoutChangeError(Exception):
    """Raised when lectio layout changes"""
    def __init__(self,page, message="Lectio layout has changed its layout on the {} page, the code needs to be updated."):
        super().__init__(message.format(page))