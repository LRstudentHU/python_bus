import re
import urllib.request
import datetime

expression = re.compile('(frame_.+?)\{(.+?)\}', re.IGNORECASE | re.MULTILINE | re.DOTALL)
url = "https://raw.githubusercontent.com/R2D2-2019/internal_communication/master/code/headers/frame_types.hpp"
splitString = "/** USER STRUCTS */"


def getGit(url, splitString):
    rawContents = urllib.request.urlopen(url).read()
    decodedContents = rawContents.decode("utf-8")
    contents = decodedContents.split(splitString)
    return contents[1]


def parseGit(input):
    matches = expression.findall(input)
    results = []
    for idx, match in enumerate(matches):
        lines = match[1].split('\n')
        items = []
        for line in lines:
            line = line.strip()

            # Skip empty or commented lines
            if not line or line.startswith('//'):
                continue

            # Remove trailing ;
            if line.endswith(';'):
                line = line[:-1]
            items.append(line.strip())

        results.append((match[0].strip(), items))

    return results

    # for result in results:
    #   print(result)


def generatePyFile(filename, frames):
    # Write the file start
    output = "# this class was generated by Nicky's script on " + str(datetime.datetime.now()) + "\n\n"
    output += "from .common import FrameType, Frame" + "\n"
    output += "import struct" + "\n\n"

    # The different format converters
    typeFormats = {
        'char': 'c',
        'int8_t': 'c',
        'signed char': 'b',
        'unsigned char': 'B',
        'uint8_t': 'B',
        '_Bool': '?',
        'bool': '?',
        'short': 'h',
        'int16_t': 'h',
        'unsigned short': 'H',
        'uint16_t': 'H',
        'int': 'i',
        'int32_t': 'i',
        'unsigned int': 'I',
        'uint32_t': 'I',
        'long': 'l',
        'int64_t': 'l',
        'unsigned long': 'L',
        'uint64_t': 'L',
        'long long': 'q',
        'unsigned long long': 'Q',
        'ssize_t': 'n',
        'size_t': 'N',
        'float': 'f',
        'double': 'd',
        'char[]': 's',
        'void*': 'P',
        'void *': 'P'
    }

    # For each frame int the file
    for frame in frames:

        # Get the elements of the class name
        classNameWords = frame[0][:-2].split("_")

        # The FrameType enumeration name
        frameType = '_'.join(classNameWords[1:]).upper()

        # Capitalize all the word in the class name to conform
        # to PEP-8
        for wordNr, word in enumerate(classNameWords):
            classNameWords[wordNr] = word.capitalize()

        # The frame format for in the class, follows
        # the format of the 'struct' Python 3.7 package
        frameFormat = ''

        # A list of arguments for the 'set_data' method
        argumentList = []
        for type in frame[1]:
            split = type.split(' ')
            frameFormat += typeFormats[split[0]]
            argumentList.append(split[1])

        output += "class " + ''.join(classNameWords) + "(Frame):\n"
        output += "\tdef __init__(self):\n"
        output += "\t\tsuper(" + ''.join(classNameWords) + ", self).__init__()\n"
        output += "\t\tself.type = FrameType." + frameType + '\n'
        output += "\t\tself.format = '" + frameFormat + "'\n\n"
        output += "\tdef set_data(self, " + ', '.join(argumentList) + '):\n'
        output += "\t\tself.data = struct.pack(self.format, " + ', '.join(argumentList) + ')\n'
        output += "\n"

        # Write the output to the file
        with open(filename + ".py", "w") as file:
            file.write(output.replace('\t', '    '))

generatePyFile("frames", parseGit(getGit(url, splitString)))