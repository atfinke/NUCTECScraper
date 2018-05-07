import os


def saveDictionariesToCSV(dictionaries, fileName):

    if (len(dictionaries) == 0):
        return

    csvFirstLine = ""
    csvContent = ""

    keys = [
        "report_caesar_title",
        "report_caesar_instructor",
        "report_caesar_subject",
        "report_caesar_class_number",
        "report_caesar_career",

        "report_ctec_title",

        "report_term",
        "report_response_count",
        "report_invited_count",

        "course_instruction_rating_response_count",
        "course_instruction_rating_mean",
        "course_overall_rating_response_count",
        "course_overall_rating_mean",
        "course_learned_rating_response_count",
        "course_learned_rating_mean",
        "course_challenging_rating_response_count",
        "course_challenging_rating_mean",
        "course_interest_rating_response_count",
        "course_interest_rating_mean",

        "time_spent_3_or_fewer",
        "time_spent_4_to_7",
        "time_spent_8_to_11",
        "time_spent_12_to_15",
        "time_spent_16_to_19",
        "time_spent_20_or_more",

        "demographics_school_education",
        "demographics_school_communication",
        "demographics_school_graduate",
        "demographics_school_kgsm",
        "demographics_school_mccormick",
        "demographics_school_medill",
        "demographics_school_music",
        "demographics_school_summer",
        "demographics_school_sps",
        "demographics_school_wcas",

        "demographics_class_freshman",
        "demographics_class_sophomore",
        "demographics_class_junior",
        "demographics_class_senior",
        "demographics_class_graduate",
        "demographics_class_other",

        "demographics_reason_requirement_distribution",
        "demographics_reason_requirement_major_minor",
        "demographics_reason_requirement_elective",
        "demographics_reason_requirement_none",
        "demographics_reason_requirement_other",

        "demographics_previous_interest_1",
        "demographics_previous_interest_2",
        "demographics_previous_interest_3",
        "demographics_previous_interest_4",
        "demographics_previous_interest_5",
        "demographics_previous_interest_6",

        "report_url"
    ]

    for idx, key in enumerate(keys):
        csvFirstLine += key
        if idx != len(keys) - 1:
            csvFirstLine += ","

    for dictionary in dictionaries:
        for idx, key in enumerate(keys):
            if key in dictionary:
                csvContent += dictionary[key].encode('utf-8')
            if idx != len(keys) - 1:
                csvContent += ","
        csvContent += "\n"
    csvContent = csvFirstLine + "\n" + csvContent

    if not os.path.exists("output"):
        os.makedirs("output")

    path = "output/" + fileName + ".csv"
    print("Saving CSV to " + path)
    with open(path, "w") as text_file:
        text_file.write(csvContent)
