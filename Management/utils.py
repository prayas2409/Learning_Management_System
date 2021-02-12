import enum
import random
import string


class Degree(enum.Enum):

    TENTH = 'TENTH'
    HS = 'HS'
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

    def get_first_anme(name):
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
