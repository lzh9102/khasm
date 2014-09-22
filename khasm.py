#!/usr/bin/env python3

import sys
import re

CATEGORY_DA = 0
CATEGORY_DI = 1
CATEGORY_DAI = 2
CATEGORY_DAB = 3
CATEGORY_DAS = 4
CATEGORY_AB = 5
CATEGORY_AI = 6
CATEGORY_I = 7
CATEGORY_N = 8
CATEGORY_A = 9
CATEGORY_D = 10

INSTRUCTION = {
#   mnemonics: opcode+mode, category
    "nop":  (0b00000000, CATEGORY_N),
    "mov":  (0b00000000, CATEGORY_DA),
    "mvn":  (0b00000001, CATEGORY_DA),

    "movi": (0b00001000, CATEGORY_DI),
    "mvhi": (0b00001001, CATEGORY_DAI),
    "mvli": (0b00001010, CATEGORY_DAI),

    "add":  (0b00010000, CATEGORY_DAB),
    "addf": (0b00010001, CATEGORY_DAB),
    "sub":  (0b00010010, CATEGORY_DAB),
    "subf": (0b00010011, CATEGORY_DAB),
    "and":  (0b00010100, CATEGORY_DAB),
    "or":   (0b00010101, CATEGORY_DAB),
    "xor":  (0b00010110, CATEGORY_DAB),
    "cmp":  (0b00010111, CATEGORY_AB),

    "addi":  (0b00011000, CATEGORY_DAI),
    "addfi": (0b00011001, CATEGORY_DAI),
    "subi":  (0b00011010, CATEGORY_DAI),
    "subfi": (0b00011011, CATEGORY_DAI),
    "cmpi":  (0b00011111, CATEGORY_AI),

    "shl": (0b00100111, CATEGORY_DAS),
    "shr": (0b00101000, CATEGORY_DAS),
    "rol": (0b00101001, CATEGORY_DAS),
    "ror": (0b00101010, CATEGORY_DAS),
    "asr": (0b00101011, CATEGORY_DAS),

    "ldr": (0b00110000, CATEGORY_DA),
    "str": (0b00111000, CATEGORY_DA),

    "bnt": (0b01000000, CATEGORY_I),
    "beq": (0b01000001, CATEGORY_I),
    "bne": (0b01000010, CATEGORY_I),
    "bcs": (0b01000011, CATEGORY_I),
    "bcc": (0b01000100, CATEGORY_I),
    "bmi": (0b01000101, CATEGORY_I),
    "bpl": (0b01000110, CATEGORY_I),
    "bvs": (0b01000111, CATEGORY_I),
    "bvc": (0b01001000, CATEGORY_I),
    "bhi": (0b01001001, CATEGORY_I),
    "bls": (0b01001010, CATEGORY_I),
    "bge": (0b01001011, CATEGORY_I),
    "blt": (0b01001100, CATEGORY_I),
    "bgt": (0b01001101, CATEGORY_I),
    "ble": (0b01001110, CATEGORY_I),
    "bal": (0b01001111, CATEGORY_I),

    "jp":  (0b01010000, CATEGORY_A),
    "jpl": (0b01010001, CATEGORY_A),
    "ret": (0b01011000, CATEGORY_N),

    "in":  (0b01100000, CATEGORY_D),
    "out": (0b01101000, CATEGORY_AB),
}

ALIAS = {
    "not": "mvn",
    "bhs": "bcs",
    "blo": "bcc",
}

class AsmLineParser(object):

    def __init__(self):
        self.label = None
        self.instruction = ""
        self.args = []

    def getLabel(self):
        return self.label

    def getInstruction(self):
        return self.instruction

    def getArgs(self):
        return self.args

    def parseLine(self, line):
        assert(type(line) == str)
        match = re.match(r"\s*((?P<label>[a-zA-Z0-9_$]+):)?\s*(?P<inst>[a-zA-Z0-9_]+)?(\s+(?P<argline>.*))$",
                         line)
        if match:
            self.label = match.group('label')
            self.instruction = match.group('inst')
            argline = match.group('argline')
            self.args = self.parseArgLine(argline)
            return True
        else:
            return False

    def parseArgLine(self, line):
        assert(line == None or type(line) == str)
        if line == None or line.strip() == "":
            return []
        args = []
        for token in line.split(","):
            arg = token.strip()
            if arg == "": # error: empty argument
                return None
            args.append(arg)
        return args


class Assembler(object):

    def __init__(self):
        self.code = {}
        self.labels = {}
        self.codeptr = 0

    def assembleFile(self, filename):
        self._parseFile(filename)

    def _parseFile(self, filename):
        assert(type(filename) == str)
        with open(filename, "r") as f:
            parser = AsmLineParser()
            lineno = 1
            for line in f:
                # parse
                if not parser.parseLine(line):
                    raise Exception("line %d: syntax error" % (lineno))
                label = parser.getLabel()
                instruction = parser.getInstruction()
                args = parser.getArgs()

                try:
                    # generate code
                    if label:
                        self._putLabel(label)
                    if instruction:
                        self._putInstruction(instruction, args)
                except Exception as e:
                    raise Exception("line %d: %s" % (lineno, str(e)))

                # increment line number
                lineno += 1

    def _putLabel(self, label):
        assert(type(label) == str)
        self.labels[label] = self.codeptr

    def _putCode(self, code):
        """ generate a 32-bit integer code """
        assert(type(code) == int)
        self.code[self.codeptr] = code
        self.codeptr += 1

    def _putInstruction(self, instruction, args):
        if instruction in ALIAS: # substitute alias
            instruction = ALIAS[instruction]
        if instruction not in INSTRUCTION:
            raise Exception("unknown instruction %s" % (instruction))

if __name__ == "__main__":
    asm = Assembler()
    try:
        asm.assembleFile(sys.argv[1])
    except Exception as e:
        print("error: %s" % (str(e)))
