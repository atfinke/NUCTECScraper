def fetchClassData(driver, term, subject, classNumber):
    print("=============")
    classDescription = subject + " " + classNumber + " during " + term
    print("Starting class infomation fetch for " + classDescription)

    url = "https://caesar.ent.northwestern.edu/psc/s9prod_5/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.CLASS_SEARCH.GBL?Page=SSR_CLSRCH_ENTRY&Action=U&ACAD_CAREER=UGRD&EMPLID=2966592&ENRL_REQUEST_ID=&INSTITUTION=NWUNV&STRM=4680"
    driver.get(url)

    selects = [];
    while len(selects) < 5:
        selects = driver.find_elements_by_tag_name("select");
        sleep(0.1)

    for select in selects:
        selectID = select.get_attribute('id')
        if "CLASS_SRCH_WRK2_STRM" in select.get_attribute('name'):
            # Term (2017 Fall)
            options = driver.execute_script("return document.getElementById('" + selectID + "').options")
            termValue = None;
            for option in options:
                if option.get_attribute("innerHTML") == term:
                    termValue = option.get_attribute("value")
                    break;

            if termValue is None:
                driver.quit();
                raise ValueError("Invalid term")

            driver.execute_script("document.getElementById('" + selectID + "').value = '" + termValue + "'");
            driver.execute_script("document.getElementById('" + selectID + "').onchange();");

            if str(driver.find_element_by_id(selectID).get_attribute('value')) == str(termValue):
                print("Successfully set term to " + term)
            else:
                driver.quit();
                raise ValueError("Failed to set term")

        elif "SSR_CLSRCH_WRK_SUBJECT_SRCH" in select.get_attribute('name'):
            # Subject (MATH)
            sleep(0.2);

            options = driver.execute_script("return document.getElementById('" + selectID + "').options")

            validClass = False;
            for option in options:
                if (option.get_attribute('value') == subject):
                    validClass = True;

            if (validClass == False):
                driver.quit();
                raise ValueError("Invalid subject")

            driver.execute_script("document.getElementById('" + selectID + "').value = '" + subject + "'");
            driver.execute_script("document.getElementById('" + selectID + "').onchange();");

            if str(driver.find_element_by_id(selectID).get_attribute('value')) == str(subject):
                print("Successfully set subject to " + subject)
            else:
                driver.quit();
                raise ValueError("Failed to set subject")

        elif "SSR_CLSRCH_WRK_SSR_EXACT_MATCH1" in select.get_attribute('name'):
            # Number (is equal to ) [Not Implemented]
            driver.execute_script("document.getElementById('SSR_CLSRCH_WRK_CATALOG_NBR$1').value = '" + classNumber + "'");
            driver.execute_script("document.getElementById('SSR_CLSRCH_WRK_CATALOG_NBR$1').onchange();");

            if str(driver.find_element_by_id('SSR_CLSRCH_WRK_CATALOG_NBR$1').get_attribute('value')) == str(classNumber):
                print("Successfully set class number to " + classNumber)
            else:
                driver.quit();
                raise ValueError("Failed to set class number")

            sleep(0.25);

    driver.execute_script("document.getElementById('SSR_CLSRCH_WRK_SSR_OPEN_ONLY_LBL$3').click();");
    driver.execute_script("document.getElementById('CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH').click();");

    classElements = [];
    while len(classElements) == 0:
        links = driver.find_elements_by_tag_name("a");
        for link in links:
            if "MTG_CLASS_NBR" in link.get_attribute('name'):
                classElements.append(link);
        sleep(0.25)

    print("Found " + str(len(classElements)) + " results for " + classDescription)


    allClassProperties = [];
    for classElement in classElements:
        print("Gathering Class data (" + str(len(allClassProperties) + 1) + "/" + str(len(classElements)) + ")")
        clickedClassElement = False;
        while clickedClassElement == False:
            try:
                driver.execute_script("document.getElementById('" + classElement.get_attribute('id') + "').click();");
                clickedClassElement = True;
            except:
                sleep(0.5);

        foundTitle = False;
        while foundTitle == False:
            try:
                titleElement = driver.find_element_by_id("DERIVED_CLSRCH_DESCR200")
                foundTitle = True;
            except:
                sleep(0.5);
                pass

        allClassProperties.append(scrapClassPage(driver));
        driver.execute_script("document.getElementById('CLASS_SRCH_WRK2_SSR_PB_BACK').click();");

    driver.quit();

    if len(allClassProperties) == 0:
        raise ValueError("Failed to get any class properties")

    saveDictionariesToCSV(allClassProperties, classDescription + "-CLASS_DATA")

def scrapClassPage(driver):

    def removeElements(text):
        return strip_tags(text).replace("\n", " ").replace(",", ".");

    def text(elementID):
        return removeElements(str(driver.find_element_by_id(elementID).get_attribute("innerHTML")));

    name = text("DERIVED_CLSRCH_DESCR200");

    classNumber = text("SSR_CLS_DTL_WRK_CLASS_NBR");
    units = text("SSR_CLS_DTL_WRK_UNITS_RANGE");

    career = text("PSXLATITEM_XLATLONGNAME");
    dates = text("SSR_CLS_DTL_WRK_SSR_DATE_LONG");
    grading = text("GRADE_BASIS_TBL_DESCRFORMAL");
    campus = text("CAMPUS_TBL_DESCR");

    times = text("MTG_SCHED$0");
    room = text("MTG_LOC$0");
    instructor = text("MTG_INSTR$0");
    dates = text("MTG_DATE$0");

    capacity = text("SSR_CLS_DTL_WRK_ENRL_CAP");
    enrollment = text("SSR_CLS_DTL_WRK_ENRL_TOT");
    waitListCapacity = text("SSR_CLS_DTL_WRK_WAIT_CAP");
    waitListTotal = text("SSR_CLS_DTL_WRK_WAIT_TOT");

    classProperties = {
        "name": name,

        "classNumber": classNumber,
        "units": units,

        "career": career,
        "dates": dates,
        "grading": grading,
        "campus": campus,

        "times": times,
        "room": room,
        "instructor": instructor,
        "dates": dates,

        "capacity": capacity,
        "enrollment": enrollment,
        "waitListCapacity": waitListCapacity,
        "waitListTotal": waitListTotal,
    }

    try:
        components = driver.find_element_by_class_name("PSTEXT").get_attribute("textContent");
        classProperties["components"] = removeElements(str(components));
    except:
        pass;

    return classProperties
