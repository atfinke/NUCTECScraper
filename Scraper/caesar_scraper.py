import argparse
import logging
import os

from time import sleep
from selenium import webdriver

from selenium.webdriver import ActionChains
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from caesar_authentication import authenticate
from bluera_ctec_scraper import scrape_loaded_ctec_page
import casear_navigation

spacer = "   "

def scrape_subject_ctecs(driver, logger, career, subject):
    logger.info("=============")

    try:
        if not casear_navigation.open_subject_ctecs_from_main_page(driver, logger, career, subject):
            return None
    except Exception as e:
        logger.error("Failed to open subject ctecs from main page")
        logger.error("ERROR INFO - " + str(e) + "\n")
        return None

    # Now viewing full ctec view (classes on left, section reviews table on right)
    ctec_page_all_class_rows = []
    while len(ctec_page_all_class_rows) == 0:
        links = driver.find_elements_by_class_name("psc_rowact")
        for link in links:
            if "NW_CT_PV_DRV$0_row_" in link.get_attribute('id'):
                ctec_page_all_class_rows.append(link.get_attribute('id'))
        sleep(0.25)

    logger.info("-------------")
    logger.info(subject + ": Found " +
                str(len(ctec_page_all_class_rows)) + " classes in sidebar")

    main_window = driver.current_window_handle
    scrappedCTECs = []

    ctec_page_class_scrape_count = 0
    last_class_inner_html = "N/A"

    for class_row_id in ctec_page_all_class_rows:
        ctec_page_class_scrape_count += 1

        sleep(5)

        attempts = 0
        while attempts < 3:
            attempts += 1

            try:
                # Click on the class on the left sidebar
                class_row_element = driver.find_element_by_id(class_row_id)
                class_row_element.click()
                classNumber = class_row_element.get_attribute(
                    'innerText').split('-')[0]

                logger.info(spacer + subject + " " +
                            str(classNumber) + ": Starting")

                try:
                    ctecs, resultsRowsText = scrape_class_ctecs(
                        driver, logger, main_window, career, subject, classNumber, last_class_inner_html)
                    scrappedCTECs = scrappedCTECs + ctecs

                    if resultsRowsText != "":
                        last_class_inner_html = resultsRowsText
                    break

                except Exception as e:
                    logger.error(spacer + subject + ": Restarting entire class scrapping (attempt #" + str(attempts) + ")\n")
                    logger.error(spacer + subject +
                                 ": ERROR INFO - " + str(e) + "\n")
                    continue
            except Exception as e:
                logger.error(
                    spacer + subject + ": Something unexpected happened when loading all class CTEC results, skipping class")
                logger.error(spacer + subject +
                             ": ERROR INFO - " + str(e) + "\n")
                continue

        logger.info(spacer + "Subject Progress: " + str(ctec_page_class_scrape_count) +
                    "/" + str(len(ctec_page_all_class_rows)) + "\n")

    try:
        os.remove("output/_TEMP-" + subject + "-CTECs")
    except:
        pass

    return scrappedCTECs


def scrape_class_ctecs(driver, logger, main_window, career, subject, classNumber, last_class_inner_html):
    sleep(2)

    class_inner_html = ""
    class_page_class_row = []

    try:
        is_showing_results_for_current_class = False
        attempts = 0

        logger.info(spacer + spacer + "Waiting 1 second to load")
        sleep(1)

        while (is_showing_results_for_current_class == False and attempts < 10):
            attempts += 1

            class_page_class_row = []
            class_inner_html = ""
            links = driver.find_elements_by_class_name("psc_rowact")
            class_inner_html = driver.find_element_by_id("NW_CT_PUB_RSLT_FL").get_attribute('innerHTML')

            for link in links:
                if "NW_CT_PV4_DRV$0_row_" in link.get_attribute('id'):
                    class_page_class_row.append(link)

            if class_inner_html != last_class_inner_html and class_inner_html != "":
                is_showing_results_for_current_class = True

            else:
                sleep(1)

        if is_showing_results_for_current_class == False:
            logger.warning(spacer + spacer +
                           "No CTEC result rows loaded, (same inner html) skipping class" + "\n")
            logger.warning(class_inner_html)

            raise ValueError("no rows found")
        elif attempts == 10:
            logger.warning(spacer + spacer +
                           "No CTEC result rows loaded, (timeout) skipping class" + "\n")
            raise ValueError("no rows found")

    except Exception as e:
        logger.error(spacer + spacer +
                     "Something unexpected happened when reading CTEC result rows, skipping class")
        logger.error(spacer + spacer + "ERROR INFO - " + str(e) + "\n")
        raise e

    class_page_ctec_scrape_count = 0

    sleep(1)

    new_subject_CTECs = []
    are_remaining_ctecs_too_old = False

    for class_row in class_page_class_row:
        if are_remaining_ctecs_too_old:
            break

        completed_class_row_parsing = False
        class_row_parsing_attempts = 0
        class_page_ctec_scrape_count += 1

        while not completed_class_row_parsing:
            class_row_parsing_attempts += 1
            if class_row_parsing_attempts > 2:
                break
            elif class_row_parsing_attempts > 1:
                logger.info(spacer + spacer + "Retrying last ctec")

            try:

                name = driver.find_element_by_id(
                    "MYDESCR$" + str(class_page_ctec_scrape_count - 1)).get_attribute("innerText")

                instructor = driver.find_element_by_id(
                    "CTEC_INSTRUCTOR$" + str(class_page_ctec_scrape_count - 1)).get_attribute("innerText")

                driver.execute_script(
                    "document.getElementById('" + class_row.get_attribute('id') + "').click();")

                WebDriverWait(driver, 10).until(
                    lambda d: len(d.window_handles) == 2)
            except Exception as e:
                logger.error(
                    spacer + spacer + "Something unexpected happened when clicking a CTEC result row, skipping row")
                logger.error(spacer + spacer + "ERROR INFO - " + str(e) + "\n")
                sleep(2)
                continue

            onCTECTab = False
            is_valid_bluera_ctec_page = False

            while onCTECTab == False:
                for handle in driver.window_handles:
                    driver.switch_to.window(handle)
                    sleep(0.5)
                    if "Northwestern - " in driver.title:
                        onCTECTab = True
                        is_valid_bluera_ctec_page = True
                        break
                    elif "NU:" in driver.title:
                        onCTECTab = True
                        is_valid_bluera_ctec_page = False
                        break
                    elif "NU CTEC Published Reports" in driver.title:
                        if handle != main_window:
                            onCTECTab = True
                            is_valid_bluera_ctec_page = False
                            are_remaining_ctecs_too_old = True
                            break

            if is_valid_bluera_ctec_page:
                delay = 30
                try:
                    myElem = WebDriverWait(driver, delay).until(
                        EC.presence_of_element_located((By.ID, 'reportView')))
                except TimeoutException:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    logger.error("Loading took too much time!")
                    continue

                scrape = scrape_loaded_ctec_page(driver)
                if len(scrape) > 1:
                    scrape["report_caesar_title"] = name # .replace(",", "|")
                    scrape["report_caesar_instructor"] = instructor
                    scrape["report_caesar_subject"] = subject

                    # The Graduate School or Undergraduate
                    scrape["report_caesar_career"] = career
                    scrape["report_caesar_class_number"] = classNumber
                    new_subject_CTECs.append(scrape)

                    completed_class_row_parsing = True
                    logger.info(spacer + spacer + "Class Progress: " +
                                str(class_page_ctec_scrape_count) + "/" + str(len(class_page_class_row)))
                else:
                    logger.warning(spacer + spacer +
                                   spacer + "CTEC page empty")


            elif are_remaining_ctecs_too_old:
                logger.info(spacer + spacer + "Class Progress: " +
                            str(class_page_ctec_scrape_count) + "/" + str(len(class_page_class_row)))
                logger.info(spacer + spacer +
                            "Only old CTECs left, skipping the rest")
                completed_class_row_parsing = True
            else:
                logger.warning(spacer + spacer +
                               "Invalid CTEC Page (Probably the bluera homepage)")

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    if len(new_subject_CTECs) == 0:
        raise ValueError("No valid CTECs found")

    return new_subject_CTECs, class_inner_html
