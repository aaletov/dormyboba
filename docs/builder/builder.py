import getopt
import sys
import requests

def convertBPMN(filename: str, outFile: str) -> None:
    fileContent: str = ""

    with open(filename, "r", encoding="utf8") as file:
        fileContent = file.read()

    body = {
        "diagram_source": fileContent,
        "diagram_type": "bpmn",
        "output_format": "svg",
    }

    r = requests.post('http://0.0.0.0:8000/', json=body)

    if r.status_code != 200:
        raise RuntimeError("Failed to convert doc: ", str(r.content))

    decoded = bytes.decode(r.content, encoding="utf8")

    with open(outFile, "w", encoding="utf8") as file:
        file.write(decoded)

    return

def convertMMD(filename: str, outFile: str) -> None:
    fileContent: str = ""

    with open(filename, "r", encoding="utf8") as file:
        file.readline()
        fileContent = file.read()[:-3]

    body = {
        "diagram_source": fileContent,
        "diagram_type": "mermaid",
        "output_format": "png",
    }

    r = requests.post('http://0.0.0.0:8000/', json=body)

    if r.status_code != 200:
        raise RuntimeError("Failed to convert doc: ", str(r.content))

    with open(outFile, "wb") as file:
        file.write(bytes(r.content))

    return

if __name__ == "__main__":
    argumentList = sys.argv[1:]
    options = "t:f:o:"

    filename: str = ""
    docType: str = ""
    outFile: str = ""

    try:
        arguments, values = getopt.getopt(argumentList, options)

        for arg, value in arguments:
            if arg == "-f":
                filename = value
            if arg == "-t":
                docType = value
            if arg == "-o":
                outFile = value

    except getopt.error as err:
        print(str(err))
        exit(1)

    try:
        if docType == "bpmn":
            convertBPMN(filename, outFile)
        elif docType == "mermaid":
            convertMMD(filename, outFile)


    except RuntimeError as err:
        print(str(err))
        exit(1)
