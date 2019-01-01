from time import sleep
from selenium import webdriver

def scrape_loaded_ctec_page(driver):
    attempts = 0
    result_tables = []

    while len(result_tables) < 1 and attempts < 10:
        sleep(0.05)
        attempts += 1
        result_tables = driver.find_elements_by_class_name("CondensedTabularFixedHalfWidth")

    report_details = {
        "report_bluera_url": driver.current_url,
        "report_bluera_page_title": driver.title
    }

    for element in driver.find_elements_by_class_name("coverPageTitleBlock"):
        report_details["report_ctec_title"] = element.get_attribute("innerText")
        break

    creation_date_elements = driver.find_elements_by_class_name("coverPageSignatureBlock")
    if len(creation_date_elements) == 1:
        report_details["report_creation_date"] = creation_date_elements[0].text.replace("Creation Date", " ").lstrip()

    cover_elements = driver.find_elements_by_class_name("coverFullTitle")
    if len(cover_elements) > 0:
        cover_span_elements = cover_elements[0].find_elements_by_tag_name("span")
        for element in cover_span_elements:
            text = element.text
            element_id = element.get_attribute("id")
            if "Course and Teacher Evaluations CTEC " in text:
                report_details["report_term"] = text[len("Course and Teacher Evaluations CTEC "):]
            elif "_lblSubjectName" in element_id:
                report_details["report_term"] = text.split("Course and Teacher Evaluations CTEC ")[1]
            elif "_lblResponded" in element_id:
                report_details["report_response_count"] = text
            elif "_lblInvited" in element_id:
                report_details["report_invited_count"] = text

    for table in result_tables:
        summary = table.get_attribute("summary")

        if "Provide an overall rating of the instruction" in summary:
            rows = table.find_elements_by_tag_name("tr")
            if len(rows) > 2:
                headers = rows[1].find_elements_by_tag_name("td")
                if len(headers) > 0:
                    report_details["course_instruction_rating_response_count"] = headers[0].text
                data = rows[2].find_elements_by_tag_name("td")
                if len(data) > 0:
                    report_details["course_instruction_rating_mean"] = data[0].text
        elif "Provide an overall rating of the course" in summary:
            rows = table.find_elements_by_tag_name("tr")
            if len(rows) > 2:
                headers = rows[1].find_elements_by_tag_name("td")
                if len(headers) > 0:
                    report_details["course_overall_rating_response_count"] = headers[0].text
                data = rows[2].find_elements_by_tag_name("td")
                if len(data) > 0:
                    report_details["course_overall_rating_mean"] = data[0].text
        elif "Estimate how much you learned in the course" in summary:
            rows = table.find_elements_by_tag_name("tr")
            if len(rows) > 2:
                headers = rows[1].find_elements_by_tag_name("td")
                if len(headers) > 0:
                    report_details["course_learned_rating_response_count"] = headers[0].text
                data = rows[2].find_elements_by_tag_name("td")
                if len(data) > 0:
                    report_details["course_learned_rating_mean"] = data[0].text
        elif "Rate the effectiveness of the course in challenging you intellectually" in summary:
            rows = table.find_elements_by_tag_name("tr")
            if len(rows) > 2:
                headers = rows[1].find_elements_by_tag_name("td")
                if len(headers) > 0:
                    report_details["course_challenging_rating_response_count"] = headers[0].text
                data = rows[2].find_elements_by_tag_name("td")
                if len(data) > 0:
                    report_details["course_challenging_rating_mean"] = data[0].text
        elif "Rate the effectiveness of the instructor in stimulating your interest in the subject" in summary:
            rows = table.find_elements_by_tag_name("tr")
            if len(rows) > 2:
                headers = rows[1].find_elements_by_tag_name("td")
                if len(headers) > 0:
                    report_details["course_interest_rating_response_count"] = headers[0].text
                data = rows[2].find_elements_by_tag_name("td")
                if len(data) > 0:
                    report_details["course_interest_rating_mean"] = data[0].text
        elif "Estimate the average number of hours per week you spent on this course outside of class and lab time" in summary:
            rows = table.find_elements_by_tag_name("tr")
            if len(rows) > 6:
                for idx, row in enumerate(rows):
                    data = row.find_elements_by_tag_name("td")
                    if len(data) > 0:
                        if idx == 1:
                            report_details["time_spent_3_or_fewer"] = data[0].text
                        elif idx == 2:
                            report_details["time_spent_4_to_7"] = data[0].text
                        elif idx == 3:
                            report_details["time_spent_8_to_11"] = data[0].text
                        elif idx == 4:
                            report_details["time_spent_12_to_15"] = data[0].text
                        elif idx == 5:
                            report_details["time_spent_16_to_19"] = data[0].text
                        elif idx == 6:
                            report_details["time_spent_20_or_more"] = data[0].text
        elif "What is the name of your school?" in summary:
            rows = table.find_elements_by_tag_name("tr")
            if len(rows) > 10:
                for idx, row in enumerate(rows):
                    data = row.find_elements_by_tag_name("td")
                    if len(data) > 0:
                        if idx == 1:
                            report_details["demographics_school_education"] = data[0].text
                        elif idx == 2:
                            report_details["demographics_school_communication"] = data[0].text
                        elif idx == 3:
                            report_details["demographics_school_graduate"] = data[0].text
                        elif idx == 4:
                            report_details["demographics_school_kgsm"] = data[0].text
                        elif idx == 5:
                            report_details["demographics_school_mccormick"] = data[0].text
                        elif idx == 6:
                            report_details["demographics_school_medill"] = data[0].text
                        elif idx == 7:
                            report_details["demographics_school_music"] = data[0].text
                        elif idx == 8:
                            report_details["demographics_school_summer"] = data[0].text
                        elif idx == 9:
                            report_details["demographics_school_sps"] = data[0].text
                        elif idx == 10:
                            report_details["demographics_school_wcas"] = data[0].text
        elif "Your Class" in summary:
            rows = table.find_elements_by_tag_name("tr")
            if len(rows) > 6:
                for idx, row in enumerate(rows):
                    data = row.find_elements_by_tag_name("td")
                    if len(data) > 0:
                        if idx == 1:
                            report_details["demographics_class_freshman"] = data[0].text
                        elif idx == 2:
                            report_details["demographics_class_sophomore"] = data[0].text
                        elif idx == 3:
                            report_details["demographics_class_junior"] = data[0].text
                        elif idx == 4:
                            report_details["demographics_class_senior"] = data[0].text
                        elif idx == 5:
                            report_details["demographics_class_graduate"] = data[0].text
                        elif idx == 6:
                            report_details["demographics_class_other"] = data[0].text
        elif "What is your reason for taking the course" in summary:
            rows = table.find_elements_by_tag_name("tr")
            if len(rows) > 5:
                for idx, row in enumerate(rows):
                    data = row.find_elements_by_tag_name("td")
                    if len(data) > 0:
                        if idx == 1:
                            report_details["demographics_reason_requirement_distribution"] = data[0].text
                        elif idx == 2:
                            report_details["demographics_reason_requirement_major_minor"] = data[0].text
                        elif idx == 3:
                            report_details["demographics_reason_requirement_elective"] = data[0].text
                        elif idx == 4:
                            report_details["demographics_reason_requirement_none"] = data[0].text
                        elif idx == 5:
                            report_details["demographics_reason_requirement_other"] = data[0].text
        elif "What was your Interest in this subject before taking the course" in summary:
            rows = table.find_elements_by_tag_name("tr")
            if len(rows) > 5:
                for idx, row in enumerate(rows):
                    data = row.find_elements_by_tag_name("td")
                    if len(data) > 0:
                        if idx == 1:
                            report_details["demographics_previous_interest_1"] = data[0].text
                        elif idx == 2:
                            report_details["demographics_previous_interest_2"] = data[0].text
                        elif idx == 3:
                            report_details["demographics_previous_interest_3"] = data[0].text
                        elif idx == 4:
                            report_details["demographics_previous_interest_4"] = data[0].text
                        elif idx == 5:
                            report_details["demographics_previous_interest_5"] = data[0].text
                        elif idx == 6:
                            report_details["demographics_previous_interest_6"] = data[0].text

    reactions_tables = driver.find_elements_by_class_name("CondensedTabular")
    for table in reactions_tables:
        summary = table.get_attribute("summary")

        if "Please summarize your reaction to this course focusing on the aspects that were most important to you" in summary:
            rows = table.find_elements_by_tag_name("tr")
            reactions = []
            for idx, row in enumerate(rows):
                if idx != 0:
                    reactions.append(row.text)
            report_details["reactions"] = reactions

    return report_details
