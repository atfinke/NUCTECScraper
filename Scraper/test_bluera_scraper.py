from bluera_ctec_scraper import scrape_loaded_ctec_page
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import json

url = "https://northwestern.bluera.com/northwestern/rpv.aspx?lang=eng&redi=1&SelectedIDforPrint=9069f81e1fff8fccf3c222f29993048a5915b3189a57f260d07d1cec125f2b7dab8092ea6e4d5c72d1846903549a865b&ReportType=2&regl=en-US"
url = "https://northwestern.bluera.com/northwestern/rpv-eng.aspx?lang=eng&redi=1&SelectedIDforPrint=807ab7bd79d0e7aae1c8b01cdb1455f447af4f54f02d66461ff39ae900d0f598f570086e0d778da384e5bb246236f88d&ReportType=2&regl=en-US"
url = "https://northwestern.bluera.com/northwestern/rpv-eng.aspx?lang=eng&redi=1&SelectedIDforPrint=b78cc593e617e0f91b654f870f6df37ffcb8ef1e490aed4abce4511b61fbd81236e6fb1393ff043630bc3c90db32a08f&ReportType=2&regl=en-US"


options = Options()
options.set_headless(True)

firefox_profile = webdriver.FirefoxProfile()
firefox_profile.set_preference('permissions.default.image', 2)
firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

driver = webdriver.Firefox(options=options, firefox_profile=firefox_profile, executable_path="/usr/local/bin/geckodriver")
driver.set_window_size(1000, 1000)

driver.get(url)

scrape = scrape_loaded_ctec_page(driver)
parsed = json.loads(json.dumps(scrape))

print(json.dumps(parsed, indent=4, sort_keys=True))

driver.quit()
