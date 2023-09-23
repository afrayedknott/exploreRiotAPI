from enum import Enum

class ParamType(Enum):
    PATH = "path"
    QUERY = "query"

    def str(self) -> str:
        return self.value