from time import sleep
from selenium import webdriver


def scrapLoadedCTECPage(driver):
    def removeElements(text):
        return text.replace("\n", " ").replace(",", ".").replace("  ", " ")

    report_details = {
        "report_url": driver.current_url
    }

    sleeps = 0
    foundStudentReport = False

    result_tables = []

    while (len(result_tables) < 1 or not foundStudentReport) and sleeps < 10:
        sleep(0.15)
        sleeps += 1
        result_tables = driver.find_elements_by_class_name("CondensedTabularFixedHalfWidth")
        for element in driver.find_elements_by_tag_name("span"):
            text = element.text
            if "Course and Teacher Evaluations are intended solely for the use of faculty" in text:
                foundStudentReport = True

    for element in driver.find_elements_by_class_name("coverPageTitleBlock"):
        report_details["report_ctec_title"] = element.get_attribute("innerText")
        break

    for element in driver.find_elements_by_tag_name("span"):
        text = element.text
        if "Course and Teacher Evaluations CTEC " in text:
            report_details["report_term"] = text[len("Course and Teacher Evaluations CTEC "):]
        elif "_lblSubjectName" in element.get_attribute("id"):
            report_details["report_term"] = text.split("Course and Teacher Evaluations CTEC ")[1]
        elif "_lblResponded" in element.get_attribute("id"):
            report_details["report_response_count"] = text
        elif "_lblRespRateValue" in element.get_attribute("id"):
            report_details["report_response_percent"] = text

    result_tables = driver.find_elements_by_class_name("CondensedTabularFixedHalfWidth")
    for table in result_tables:
        summary = table.get_attribute("summary")
        print(summary)

        if "Provide an overall rating of the instruction" in summary:
            rows = table.find_elements_by_tag_name("tr")
            if len(rows) > 2:
                headers = rows[1].find_elements_by_tag_name("td")
                print(headers)
                if len(headers) > 0:
                    report_details["course_instruction_rating_response_count"] = headers[0].text
                data = rows[2].find_elements_by_tag_name("td")
                if len(data) > 0:
                    report_details["course_instruction_rating_mean"] = data[0].text
        elif "Provide an overall rating of the course" in summary:
            rows = table.find_elements_by_tag_name("tr")
            if len(rows) > 2:
                headers = rows[1].find_elements_by_tag_name("td")
                print(headers)
                if len(headers) > 0:
                    report_details["course_overall_rating_response_count"] = headers[0].text
                data = rows[2].find_elements_by_tag_name("td")
                if len(data) > 0:
                    report_details["course_overall_rating_mean"] = data[0].text
        elif "Estimate how much you learned in the course" in summary:
            rows = table.find_elements_by_tag_name("tr")
            if len(rows) > 2:
                headers = rows[1].find_elements_by_tag_name("td")
                print(headers)
                if len(headers) > 0:
                    report_details["course_learning_rating_response_count"] = headers[0].text
                data = rows[2].find_elements_by_tag_name("td")
                if len(data) > 0:
                    report_details["course_learning_rating_mean"] = data[0].text
        elif "Rate the effectiveness of the course in challenging you intellectually" in summary:
            rows = table.find_elements_by_tag_name("tr")
            if len(rows) > 2:
                headers = rows[1].find_elements_by_tag_name("td")
                print(headers)
                if len(headers) > 0:
                    report_details["course_challenging_rating_response_count"] = headers[0].text
                data = rows[2].find_elements_by_tag_name("td")
                if len(data) > 0:
                    report_details["course_challenging_rating_mean"] = data[0].text
        elif "Rate the effectiveness of the instructor in stimulating your interest in the subject" in summary:
            rows = table.find_elements_by_tag_name("tr")
            if len(rows) > 2:
                headers = rows[1].find_elements_by_tag_name("td")
                print(headers)
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
            if len(rows) > 6:
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

        ""
        ""
        ""
        ""
        ""

        "demographics_previous_interest_1"
        "demographics_previous_interest_2"
        "demographics_previous_interest_3"
        "demographics_previous_interest_4"
        "demographics_previous_interest_5"
        "demographics_previous_interest_6"




    for key in report_details:
        report_details[key] = removeElements(report_details[key])

    pretty(report_details)
    return report_details

def pretty(d, indent=0):
   for key, value in d.items():
      print('\t' * indent + str(key))
      if isinstance(value, dict):
         pretty(value, indent+1)
      else:
         print('\t' * (indent+1) + str(value))

def scrapCTECPage(driver, url):
    driver.get(url)

    classTitle = ""
    while len(classTitle) == 0:
        elements = driver.find_elements_by_class_name("coverPageTitleBlock")
        if len(elements) > 0:
            classTitle = elements[0].get_attribute("innerText")
        else:
            sleep(0.5)

    scrapLoadedCTECPage(driver)
