import enum
import random
import string
from . import models


class Degree(enum.Enum):

    SSC = 'SSC'
    HSC = 'HSC'
    UG = 'UG'
    PG = 'PG'

class GeneratePassword:
    def generate_password(self):
        # generates letters
        letters = string.ascii_letters
        str_part = ''.join(random.choice(letters) for i in range(5)) 

        # generates digits
        digits = string.digits
        int_part = ''.join(random.choice(digits) for i in range(5)) 

        return str_part+"-"+int_part

class GetFirstNameAndLastName:
    def get_last_name(name):
        name_data = name.split(' ')
        if len(name_data) > 1:
            last_name = name_data[-1]
        else:
            last_name = ''
        return last_name

    def get_first_name(name):
        name_data = name.split(' ')
        if len(name_data) > 1:
            first_name_data = name_data[0:-1]
            first_name = first_name_data[0]
            if len(first_name_data) > 1:
                for i in range(len(first_name_data)-1):
                    first_name = first_name+" "+first_name_data[i+1]
        else:
            first_name = name_data[0]
        return first_name

class Pattern(enum.Enum):

    GIT_PATTERN = "^(https://github.com/)[a-zA-Z0-9]{1,}(/)?"
    MOBILE_PATTERN = "^(\+91|91|0)?[6-9]{1}[0-9]{9}$"
    NAME_PATTERN = "^[A-Z]{1}[a-zA-Z]{2,}$"

    SID = '^(SI-)[1-9]{1}[0-9]{3}$'
    CID = '^(CI-)[1-9]{1}[0-9]{3}$'
    MID = '^(MI-)[1-9]{1}[0-9]{3}$'
    WEEK = '^(Week|week|WEEK)[ ][1]?[0-9]{1}$'
    REVIEW_DATE = '^(((0[1-9]|[12][0-9]|30)[-\/]?(0[13-9]|1[012])|31[-\/]?(0[13578]|1[02])|(0[1-9]|1[0-9]|2[0-8])[-\/]?02)[-]?[0-9]{4}|29[-\/]?02[-\/]?([0-9]{2}(([2468][048]|[02468][48])|[13579][26])|([13579][26]|[02468][048]|0[0-9]|1[0-6])00))$'


class ExcelHeader(enum.Enum):
    SID = 'SID'
    CID = 'CID'
    WEEK = 'WEEK'
    SCORE = 'SCORE'
    REVIEW_DATE = 'REVIEW DATE'
    REMARKS = 'REMARKS'
    MID = 'MID'


class ValueRange(enum.Enum):
    SCORE_MAX_VALUE = 10
    SCORE_MIN_VALUE = 0


class Default(enum.Enum):
    SID = 'SI-1000'
    CID = 'CI-1000'
    MID = 'MI-1000'
    

class Configure:
    @staticmethod
    def get_configured_excel_data(row, mentor_id):
        """This function configures excel data and returns """
        dd, mm, yyyy = row[1][4].split('-') # formating date
        date = f"{yyyy}-{mm}-{dd}"

        data = {
        'student': models.Student.objects.get(sid=row[1][0]).id,
        'course': models.Course.objects.get(cid=row[1][1]).id,
        'week_no': row[1][2].split(' ')[1],
        'score': row[1][3],
        'review_date': date,
        'remark': row[1][-1],
        'mentor': mentor_id
        }
        return data
