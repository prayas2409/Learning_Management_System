import enum

from Auth.models import Roles
from .utils import ExcelHeader, ValueRange, Pattern
import sys
sys.path.append('..')

# class ExceptionType(enum.Enum):
    

class ExcelException(Exception):
    """This is a custom exception class"""
    def __init__(self, message):
        super().__init__()
        self.message = message
    
    def __str__(self):
        return self.message


class ExcelValidator:
    
    @staticmethod
    def validate_header(df, role):
        # checking the header 
            input_file_header_set = set(df.columns)
            required_header_set = set([ExcelHeader.SID.value, ExcelHeader.CID.value, 
            ExcelHeader.WEEK.value, ExcelHeader.SCORE.value, ExcelHeader.REVIEW_DATE.value, ExcelHeader.REMARKS.value])
            if role == Roles.objects.get(role='admin'):
                required_header_set.add(ExcelHeader.MID.value)
            if input_file_header_set != required_header_set:
                raise ExcelException('Check file Header. '+ str(required_header_set) + ' expeced')
    
    @staticmethod
    def validate_null_fields(df):
         #checking the null values
            if df.isnull().values.any():
                null_list = [(col.value, df.loc[:,col.value].isnull().sum()) for col in ExcelHeader if df.loc[:,col.value].isnull().sum() > 0 ]
                raise ExcelException('Null values found ' + str(null_list))
    
    @staticmethod
    def validate_data_type(df):
        #checking the data types
            if (df[ExcelHeader.SCORE.value].map(type) == str).any():
                raise ExcelException(ExcelHeader.SCORE.value + ' should not be a string')
            
    @staticmethod
    def validate_score_range(df):
        if df[ExcelHeader.SCORE.value].max() > ValueRange.SCORE_MAX_VALUE.value:
                raise ExcelException(ExcelHeader.SCORE.value + ' should not be a beyond ')
        if df[ExcelHeader.SCORE.value].min() < ValueRange.SCORE_MIN_VALUE.value:
                raise ExcelException(ExcelHeader.SCORE.value + ' should not be a bellow ')  

    @staticmethod
    def validate_pattern(df, role):
        if role == Roles.objects.get(role='admin'):
            if (df[ExcelHeader.MID.value].map(type) == int).any() or not df[ExcelHeader.MID.value].str.match(Pattern.MID.value).all():
                raise ExcelException('MID pattern does not match, [MI-0000] expected')

        if (df[ExcelHeader.CID.value].map(type) == int).any() or not df[ExcelHeader.CID.value].str.match(Pattern.CID.value).all():
                raise ExcelException('CID pattern does not match, [CI-0000] expected')
            
        # checking the CID pattern
        if (df[ExcelHeader.SID.value].map(type) == int).any() or not df[ExcelHeader.SID.value].str.match(Pattern.SID.value).all():
                raise ExcelException('SID pattern does not match, [SI-0000] expected')
            
        #checking week pattern
        if (df[ExcelHeader.WEEK.value].map(type) == int).any() or not df[ExcelHeader.WEEK.value].str.match(Pattern.WEEK.value).all():
                raise ExcelException('WEEK pattern does not match, [week xx, Week xx, WEEK xx] expected')
        
        if not df[ExcelHeader.REVIEW_DATE.value].str.match(Pattern.REVIEW_DATE.value).all():
                raise ExcelException('Invalid date or date pattern found, [dd-mm-yyyy] expected')
    
    @staticmethod
    def validate_duplicate_data(df):
        # list of set of CID, SID and WEEK to check duplicate records
        row_tuple_list = [( row[1][0], row[1][1], row[1][2].split(' ')[1] ) for row in df.iloc[0:,0:3].iterrows()]
    
        #checking duplicate records
        row_tuple_list_set = set(row_tuple_list)
        if len(row_tuple_list) != len(row_tuple_list_set):
            raise ExcelException('Duplicate reocrds found. [SID, CID, WEEK] should not be duplicate')
    
    
    @staticmethod
    def validateExcel(df, role):
        ExcelValidator.validate_header(df, role)            # validating header
        ExcelValidator.validate_null_fields(df)             # validating null fields
        ExcelValidator.validate_data_type(df)               # validating data types
        ExcelValidator.validate_score_range(df)             # validating Score Range  
        ExcelValidator.validate_pattern(df, role)           # validating CID and SID 
        ExcelValidator.validate_duplicate_data(df)          # validate duplicate data

            