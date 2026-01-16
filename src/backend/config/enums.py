from enum import Enum

class ConductorMaterial(str, Enum):
    COPPER = "CU"
    ALUMINIUM = "AL"

class ValidationStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_FOUND = "NOT_FOUND"