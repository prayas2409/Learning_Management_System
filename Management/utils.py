import enum


class Degree(enum.Enum):

    TENTH = 'TENTH'
    HS = 'HS'
    UG = 'UG'
    PG = 'PG'


class Pattern(enum.Enum):

    GIT_PATTERN = "^(https://github.com/)[a-zA-Z0-9]{1,}(/)?"
    MOBILE_PATTERN = "^(\+91|91|0)?[6-9]{1}[0-9]{9}$"