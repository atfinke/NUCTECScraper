from time import sleep
from selenium import webdriver


def scrapLoadedCTECPage(driver):
    def removeElements(text):
        return text.replace("\n", " ").replace(",", ".").replace("  ", " ")

    classProperties = {
        "url": driver.current_url
    }

    sleeps = 0
    foundStudentReport = False

    while (len(driver.find_elements_by_tag_name("table")) < 2 or not foundStudentReport) and sleeps < 10:
        sleep(0.15)
        sleeps += 1
        for element in driver.find_elements_by_tag_name("span"):
            text = element.text
            if "Course and Teacher Evaluations are intended solely for the use of faculty" in text:
                foundStudentReport = True

    for element in driver.find_elements_by_class_name("coverPageTitleBlock"):
        classProperties["report_title"] = element.get_attribute("innerText")
        break

    for element in driver.find_elements_by_tag_name("span"):
        text = element.text
        if "Course and Teacher Evaluations CTEC " in text:
            classProperties["term"] = text[len(
                "Course and Teacher Evaluations CTEC "):]
        elif "_lblSubjectName" in element.get_attribute("id"):
            classProperties["term"] = text.split(
                "Course and Teacher Evaluations CTEC ")[1]
        elif "_lblResponded" in element.get_attribute("id"):
            classProperties["responded"] = text
        elif "_lblRespRateValue" in element.get_attribute("id"):
            classProperties["respondedRate"] = text

    for element in driver.find_elements_by_tag_name("table"):
        title = element.get_attribute("summary")
        ratingScript = """ return document.getElementById('""" + element.get_attribute(
            "id") + """').querySelector('td[headers="statValueID Mean"]').innerHTML; """
        if "Provide an overall rating of the instruction" in title:
            classProperties["rating_instruction"] = driver.execute_script(
                ratingScript)
        elif "Provide an overall rating of the course." in title:
            classProperties["rating_course"] = driver.execute_script(
                ratingScript)
        elif "Estimate how much you learned in the course." in title:
            classProperties["rating_learned"] = driver.execute_script(
                ratingScript)
        elif "Rate the effectiveness of the course in challenging you intellectually." in title:
            classProperties["rating_challenging"] = driver.execute_script(
                ratingScript)
        elif "Rate the effectiveness of the instructor in stimulating your interest in the subject." in title:
            classProperties["rating_interest"] = driver.execute_script(
                ratingScript)

    for key in classProperties:
        classProperties[key] = removeElements(classProperties[key])

    return classProperties


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
