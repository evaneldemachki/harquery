class QueryError(Exception):
    """Exception raised when invalid query string is passed"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class WorkspaceNotFoundError(Exception):
    """Exception raised when '.hq' folder is not found in working directory"""
    def __init__(self):
        self.message = "Workspace not found in working directory"
        super().__init__(self.message)