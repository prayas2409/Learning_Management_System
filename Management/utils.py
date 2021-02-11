import enum


class Degree(enum.Enum):

    TENTH = 'TENTH'
    HS = 'HS'
    UG = 'UG'
    PG = 'PG'


class Pattern(enum.Enum):

    GIT_PATTERN = "^(https://github.com/)[a-zA-Z0-9]{1,}(/)?"
    MOBILE_PATTERN = "^(\+91|91|0)?[6-9]{1}[0-9]{9}$"
    NAME_PATTERN = "^[A-Z]{1}[a-zA-Z]{2,}$"

    SID = '^(SI-)[1-9]{1}[0-9]{3}$'
    CID = '^(CI-)[1-9]{1}[0-9]{3}$'
    WEEK = '^(Week|week|WEEK)[ ][1-9]{1,2}$'


class ExcelHeader(enum.Enum):
    SID = 'SID'
    CID = 'CID'
    WEEK = 'WEEK'
    SCORE = 'SCORE'

class ValueRange(enum.Enum):
    SCORE_MAX_VALUE = 10
    SCORE_MIN_VALUE = 0
    


