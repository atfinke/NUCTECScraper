import json

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Text, Column, Integer, UnicodeText, Boolean, Float, PrimaryKeyConstraint
from sqlalchemy.types import TypeDecorator

Base = declarative_base()

SIZE = 4096


class TextArrayPickleType(TypeDecorator):

    impl = Text()

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


class CTEC(Base):
    __tablename__ = 'CTEC'

    report_caesar_title = Column(UnicodeText, nullable=False)
    report_caesar_instructor = Column(UnicodeText, nullable=False)
    report_caesar_class_number = Column(UnicodeText, nullable=False)
    report_caesar_subject = Column(UnicodeText, nullable=False)
    report_caesar_career = Column(UnicodeText, nullable=False)

    report_bluera_page_title = Column(UnicodeText, nullable=False)

    report_term = Column(UnicodeText, nullable=False)
    report_response_count = Column(Integer, nullable=False)
    report_invited_count = Column(Integer, nullable=False)
    report_creation_date = Column(UnicodeText)

    course_instruction_rating_response_count = Column(Integer)
    course_instruction_rating_mean = Column(Float)
    course_overall_rating_response_count = Column(Integer)
    course_overall_rating_mean = Column(Float)
    course_learned_rating_response_count = Column(Integer)
    course_learned_rating_mean = Column(Float)
    course_challenging_rating_response_count = Column(Integer)
    course_challenging_rating_mean = Column(Float)
    course_interest_rating_response_count = Column(Integer)
    course_interest_rating_mean = Column(Float)

    time_spent_3_or_fewer = Column(Integer)
    time_spent_4_to_7 = Column(Integer)
    time_spent_8_to_11 = Column(Integer)
    time_spent_12_to_15 = Column(Integer)
    time_spent_16_to_19 = Column(Integer)
    time_spent_20_or_more = Column(Integer)

    demographics_school_education = Column(Integer)
    demographics_school_communication = Column(Integer)
    demographics_school_graduate = Column(Integer)
    demographics_school_kgsm = Column(Integer)
    demographics_school_mccormick = Column(Integer)
    demographics_school_medill = Column(Integer)
    demographics_school_music = Column(Integer)
    demographics_school_summer = Column(Integer)
    demographics_school_sps = Column(Integer)
    demographics_school_wcas = Column(Integer)

    demographics_class_freshman = Column(Integer)
    demographics_class_sophomore = Column(Integer)
    demographics_class_junior = Column(Integer)
    demographics_class_senior = Column(Integer)
    demographics_class_graduate = Column(Integer)
    demographics_class_other = Column(Integer)

    demographics_reason_requirement_distribution = Column(Integer)
    demographics_reason_requirement_major_minor = Column(Integer)
    demographics_reason_requirement_elective = Column(Integer)
    demographics_reason_requirement_none = Column(Integer)
    demographics_reason_requirement_other = Column(Integer)

    demographics_previous_interest_1 = Column(Integer)
    demographics_previous_interest_2 = Column(Integer)
    demographics_previous_interest_3 = Column(Integer)
    demographics_previous_interest_4 = Column(Integer)
    demographics_previous_interest_5 = Column(Integer)
    demographics_previous_interest_6 = Column(Integer)

    report_bluera_url = Column(UnicodeText, nullable=False)
    reactions = Column(TextArrayPickleType())

    __table_args__ = (
        PrimaryKeyConstraint(
            report_caesar_title,
            report_bluera_page_title,
            report_caesar_instructor,
            report_term,
            report_bluera_url),
        {})

    def __init__(self, dictionary):
        self.report_caesar_title = dictionary["report_caesar_title"]
        self.report_caesar_instructor = dictionary["report_caesar_instructor"]
        self.report_caesar_class_number = dictionary["report_caesar_class_number"]
        self.report_caesar_subject = dictionary["report_caesar_subject"]
        self.report_caesar_career = dictionary["report_caesar_career"]

        self.report_bluera_page_title = dictionary["report_bluera_page_title"]

        self.report_term = dictionary["report_term"]
        self.report_response_count = dictionary["report_response_count"]
        self.report_invited_count = dictionary["report_invited_count"]
        self.report_creation_date = dictionary["report_creation_date"]

        if "course_instruction_rating_response_count" in dictionary and isfloat(dictionary[
                "course_instruction_rating_response_count"]):
            self.course_instruction_rating_response_count = dictionary[
                "course_instruction_rating_response_count"]
        if "course_instruction_rating_mean" in dictionary and isfloat(dictionary[
                "course_instruction_rating_mean"]):
            self.course_instruction_rating_mean = dictionary[
                "course_instruction_rating_mean"]

        if "course_overall_rating_response_count" in dictionary and isfloat(dictionary[
                "course_overall_rating_response_count"]):
            self.course_overall_rating_response_count = dictionary[
                "course_overall_rating_response_count"]
        if "course_overall_rating_mean" in dictionary and isfloat(dictionary[
                "course_overall_rating_mean"]):
            self.course_overall_rating_mean = dictionary[
                "course_overall_rating_mean"]

        if "course_learned_rating_response_count" in dictionary and isfloat(dictionary[
                "course_learned_rating_response_count"]):
            self.course_learned_rating_response_count = dictionary[
                "course_learned_rating_response_count"]
        if "course_learned_rating_mean" in dictionary and isfloat(dictionary[
                "course_learned_rating_mean"]):
            self.course_learned_rating_mean = dictionary[
                "course_learned_rating_mean"]

        if "course_challenging_rating_response_count" in dictionary and isfloat(dictionary[
                "course_challenging_rating_response_count"]):
            self.course_challenging_rating_response_count = dictionary[
                "course_challenging_rating_response_count"]
        if "course_challenging_rating_mean" in dictionary and isfloat(dictionary[
                "course_challenging_rating_mean"]):
            self.course_challenging_rating_mean = dictionary[
                "course_challenging_rating_mean"]

        if "course_interest_rating_response_count" in dictionary and isfloat(dictionary[
                "course_interest_rating_response_count"]):
            self.course_interest_rating_response_count = dictionary[
                "course_interest_rating_response_count"]
        if "course_interest_rating_mean" in dictionary and isfloat(dictionary[
                "course_interest_rating_mean"]):
            self.course_interest_rating_mean = dictionary[
                "course_interest_rating_mean"]

        if "time_spent_3_or_fewer" in dictionary and isfloat(dictionary[
                "time_spent_3_or_fewer"]):
            self.time_spent_3_or_fewer = dictionary["time_spent_3_or_fewer"]
            self.time_spent_4_to_7 = dictionary["time_spent_4_to_7"]
            self.time_spent_8_to_11 = dictionary["time_spent_8_to_11"]
            self.time_spent_12_to_15 = dictionary["time_spent_12_to_15"]
            self.time_spent_16_to_19 = dictionary["time_spent_16_to_19"]
            self.time_spent_20_or_more = dictionary["time_spent_20_or_more"]

        if "demographics_school_education" in dictionary and isfloat(dictionary[
                "demographics_school_education"]):
            self.demographics_school_education = dictionary["demographics_school_education"]
            self.demographics_school_communication = dictionary["demographics_school_communication"]
            self.demographics_school_graduate = dictionary["demographics_school_graduate"]
            self.demographics_school_kgsm = dictionary["demographics_school_kgsm"]
            self.demographics_school_mccormick = dictionary["demographics_school_mccormick"]
            self.demographics_school_medill = dictionary["demographics_school_medill"]
            self.demographics_school_music = dictionary["demographics_school_music"]
            self.demographics_school_summer = dictionary["demographics_school_summer"]
            self.demographics_school_sps = dictionary["demographics_school_sps"]
            self.demographics_school_wcas = dictionary["demographics_school_wcas"]

        if "demographics_class_freshman" in dictionary and isfloat(dictionary[
                "demographics_class_freshman"]):
            self.demographics_class_freshman = dictionary["demographics_class_freshman"]
            self.demographics_class_sophomore = dictionary["demographics_class_sophomore"]
            self.demographics_class_junior = dictionary["demographics_class_junior"]
            self.demographics_class_senior = dictionary["demographics_class_senior"]
            self.demographics_class_graduate = dictionary["demographics_class_graduate"]
            self.demographics_class_other = dictionary["demographics_class_other"]

        if "demographics_reason_requirement_distribution" in dictionary and isfloat(dictionary[
                "demographics_reason_requirement_distribution"]):
            self.demographics_reason_requirement_distribution = dictionary[
                "demographics_reason_requirement_distribution"]
            self.demographics_reason_requirement_major_minor = dictionary[
                "demographics_reason_requirement_major_minor"]
            self.demographics_reason_requirement_elective = dictionary[
                "demographics_reason_requirement_elective"]
            self.demographics_reason_requirement_none = dictionary[
                "demographics_reason_requirement_none"]
            self.demographics_reason_requirement_other = dictionary[
                "demographics_reason_requirement_other"]

        if "demographics_previous_interest_1" in dictionary and isfloat(dictionary[
                "demographics_previous_interest_1"]):
            self.demographics_previous_interest_1 = dictionary["demographics_previous_interest_1"]
            self.demographics_previous_interest_2 = dictionary["demographics_previous_interest_2"]
            self.demographics_previous_interest_3 = dictionary["demographics_previous_interest_3"]
            self.demographics_previous_interest_4 = dictionary["demographics_previous_interest_4"]
            self.demographics_previous_interest_5 = dictionary["demographics_previous_interest_5"]
            self.demographics_previous_interest_6 = dictionary["demographics_previous_interest_6"]

        self.report_bluera_url = dictionary["report_bluera_url"]
        if "reactions" in dictionary:
            self.reactions = dictionary["reactions"]


class Instructor(Base):
    __tablename__ = 'Instructor'

    name = Column(UnicodeText, nullable=False)
    subjects = Column(UnicodeText, nullable=False)

    response_count = Column(Integer, nullable=False)

    course_instruction_rating_mean = Column(Float)
    course_overall_rating_mean = Column(Float)
    course_learned_rating_mean = Column(Float)
    course_challenging_rating_mean = Column(Float)
    course_interest_rating_mean = Column(Float)

    __table_args__ = (
        PrimaryKeyConstraint(
            name),
        {})

    def __init__(self, dictionary):
        self.name = dictionary["name"]
        self.subjects = dictionary["subjects"]
        self.response_count = dictionary["response_count"]

        if "course_instruction_rating_mean" in dictionary and isfloat(dictionary[
                "course_instruction_rating_mean"]):
            self.course_instruction_rating_mean = dictionary[
                "course_instruction_rating_mean"]

        if "course_overall_rating_mean" in dictionary and isfloat(dictionary[
                "course_overall_rating_mean"]):
            self.course_overall_rating_mean = dictionary[
                "course_overall_rating_mean"]

        if "course_learned_rating_mean" in dictionary and isfloat(dictionary[
                "course_learned_rating_mean"]):
            self.course_learned_rating_mean = dictionary[
                "course_learned_rating_mean"]

        if "course_challenging_rating_mean" in dictionary and isfloat(dictionary[
                "course_challenging_rating_mean"]):
            self.course_challenging_rating_mean = dictionary[
                "course_challenging_rating_mean"]

        if "course_interest_rating_mean" in dictionary and isfloat(dictionary[
                "course_interest_rating_mean"]):
            self.course_interest_rating_mean = dictionary[
                "course_interest_rating_mean"]
