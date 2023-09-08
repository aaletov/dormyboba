import getopt
import sys
import requests
from xml.etree import ElementTree

def convert(docType: str, filename: str) -> ElementTree.ElementTree:
    if not docType in {"mermaid", "bpmn"}:
        raise RuntimeError("Unsupported docType: ", docType)
    
    fileContent: str = ""
    with open(filename, "r", encoding="utf8") as file:
        fileContent = file.read()

    body = {
        "diagram_source": fileContent,
        "diagram_type": docType,
        "output_format": "svg",
    }

    r = requests.post('http://0.0.0.0:8000/', json=body)
    
    if r.status_code != 200:
        raise RuntimeError("Failed to convert doc: ", str(r.content))

    element = ElementTree.fromstring(r.content)
    return ElementTree.ElementTree(element)

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
        et = convert(docType, filename)
        et.write(outFile, encoding="utf8")

    except RuntimeError as err:
        print(str(err))
        exit(1)
