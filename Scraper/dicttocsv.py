import os

def saveDictionariesToCSV(dictionaries, fileName):

    if (len(dictionaries) == 0):
        return

    csvFirstLine = "";
    csvContent = "";
    keys = sorted(dictionaries[0].keys())
    for key in keys:
        csvFirstLine += key + ","

    for dictionary in dictionaries:
        for key in keys:
            if key in dictionary:
                csvContent += dictionary[key].encode('utf-8') + ","
            else:
                csvContent += "N/A,"
        csvContent += "\n"
    csvContent = csvFirstLine + "\n" + csvContent

    if not os.path.exists("output"):
        os.makedirs("output")

    path = "output/" + fileName + ".csv"
    print("Saving CSV to " + path)
    with open(path, "w") as text_file:
        text_file.write(csvContent)
