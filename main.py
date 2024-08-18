import os
import argparse
import json
import time
startTime = time.time()

class UnknownError(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)

class DotDict:
    def __init__(self, dictionary):
        self.__dict__['_data'] = dictionary

    def __getattr__(self, item):
        if item in self.__dict__['_data']:
            return self.__dict__['_data'][item]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")

    def __setattr__(self, key, value):
        if key in self.__dict__['_data']:
            self.__dict__['_data'][key] = value
        else:
            raise AttributeError(f"Cannot set attribute '{key}'")

    def __repr__(self):
        return repr(self.__dict__['_data'])

class ProgramDefinedValues:
    string = DotDict({'name': 'string', 'reference': 'str', 'identifiers': ['"', "'"]})
    integer = DotDict({'name': 'integer', 'reference': 'int', 'identifiers': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']})
    variable = DotDict({'name': 'variable', 'reference': 'var', 'identifiers': ["var "]})

def getArgs():
    parser = argparse.ArgumentParser(description="Yellow compiler")
    parser.add_argument('-i', '--input', help='Path to the input file')
    parser.add_argument('-o', '--output', help='Path to the output file')
    parser.add_argument('-r', '--run', action='store_true', help='Run a json instead of compiling')
    args = parser.parse_args()
    return args

def getFileObj(relPath):
    path = os.path.join(os.path.dirname(__file__), relPath)
    try:
        temp = open(path, 'r')
        return temp
    except FileNotFoundError:
        raise FileNotFoundError(f'File at path {path} could not be found or was not able to be accessed.')
    except:
        raise UnknownError('An unknown error occured while getting the file.')

def tokenize(fileObj):
    file = fileObj.read()
    tok = ''
    doingCode = ''
    doingExtra = ''
    tokens = {'code' : []}
    tokenIndex = 0
    line = 1
    for char in file:
        tok += char
        if tok == ' ':
            tok = ''
        elif tok == '\n':
            line += 1
            tok = ''
        elif char in ProgramDefinedValues.string.identifiers:
            if doingCode == "print":
                if doingExtra == "string":
                    if tokenIndex >= len(tokens['code']):
                        tokens['code'].append({})
                    tokens['code'][tokenIndex] = {'print' : {ProgramDefinedValues.string.name: [tok.split('"')[0]]}, 'line' : line}
                    tokenIndex += 1
                    doingExtra = ''
                    doingCode = ''
                elif doingExtra == '':
                    doingExtra = "string"
            tok = ''
        elif tok == "print":
            doingCode = "print"
            tok = ''
    return tokens

def writeJson(tokenDict, outputFile):
    writeObject = open(outputFile, 'w')
    json.dump(tokenDict, writeObject, indent=4)

def run(inputFile):
    try:
        path = os.path.join(os.path.dirname(__file__), inputFile)
        with open(path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f'File at path {inputFile} could not be found or was not able to be accessed.')
    except json.JSONDecodeError:
        raise ValueError('Error decoding JSON from the file.')
    except Exception as e:
        raise UnknownError(f'An unknown error occurred: {e}')
    
    for block in data['code']:
        if list(block.keys())[0] == "print":
            block1 = block['print']
            if list(block1.keys())[0] == "string":
                values = block1['string']
                if len(values) == 1:
                    print(values[0])
                elif len(values) == 0:
                    print('NonLethalError: Can not print nothing')
                    print(f'Line {block['line']}')

def main():
    args = getArgs()
    if args.run:
        run(args.input)

        elapsedTime = time.time()
        print(f'Finished runtime in {elapsedTime-startTime:.3f}s.')
    else:
        fileObject = getFileObj(args.input)
        tokenDict = tokenize(fileObject)
        writeJson(tokenDict, args.output)

        elapsedTime = time.time()
        print(f'Finished compilation in {elapsedTime-startTime:.3f}s.')

if __name__ == '__main__':
    main()