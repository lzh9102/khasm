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
CATEGORY_I24 = 7
CATEGORY_N = 8
CATEGORY_A = 9
CATEGORY_D = 10

CATEGORY_ARG_COUNT = {
    CATEGORY_DA: 2,
    CATEGORY_DI: 2,
    CATEGORY_DAI: 3,
    CATEGORY_DAB: 3,
    CATEGORY_DAS: 3,
    CATEGORY_AB: 2,
    CATEGORY_AI: 2,
    CATEGORY_I24: 1,
    CATEGORY_N: 0,
    CATEGORY_A: 1,
    CATEGORY_D: 1,
}

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

    "bnt": (0b01000000, CATEGORY_I24),
    "beq": (0b01000001, CATEGORY_I24),
    "bne": (0b01000010, CATEGORY_I24),
    "bcs": (0b01000011, CATEGORY_I24),
    "bcc": (0b01000100, CATEGORY_I24),
    "bmi": (0b01000101, CATEGORY_I24),
    "bpl": (0b01000110, CATEGORY_I24),
    "bvs": (0b01000111, CATEGORY_I24),
    "bvc": (0b01001000, CATEGORY_I24),
    "bhi": (0b01001001, CATEGORY_I24),
    "bls": (0b01001010, CATEGORY_I24),
    "bge": (0b01001011, CATEGORY_I24),
    "blt": (0b01001100, CATEGORY_I24),
    "bgt": (0b01001101, CATEGORY_I24),
    "ble": (0b01001110, CATEGORY_I24),
    "bal": (0b01001111, CATEGORY_I24),

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

def regToInt(name):
    """ convert register name to number """
    match = re.match(r"r([0-9]+)", name)
    if match:
        index = int(match.group(1))
        if 0 <= index <= 15:
            return index
    raise AsmException("incorrect register %s" % name)

def nBitInteger(s, bits):
    """ Convert string 's' to an n-bit signed integer.
        Raises an exception if s cannot be accommodated in an n-bit signed integer
    """
    try:
        value = int(s)
        rep = ('{0:' + str(bits) + 'b}').format(value)
        if len(rep) > bits:
            raise AsmException("immediate value excceeds %d bit: %s"
                                % (bits, s))
        return value
    except ValueError:
        raise AsmException("invalid integer value: %s" % s)

def patchCode(code, value, bits):
    """ patch the last bits of <code> to <value> """
    assert(type(code) == type(value) == type(bits) == int)
    mask = 2**bits-1
    return (code & ~mask) | (value & mask)

def int16(s):
    """ convert string to 16 bit signed integer representation """
    try:
        value = int(s)
        rep = '{0:16b}'.format(value)
        if len(rep) > 16:
            raise AsmException("immediate value excceeds 16 bit: %s" % s)
    except Exception:
        raise AsmException("incorrect immediate value: %s" % s)

def int24(s):
    """ convert string to 24 bit signed integer binary representation """
    try:
        value = int(s)
        rep = '{0:24b}'.format(value)
        if len(rep) > 24:
            raise AsmException("immediate value excceeds 24 bit: %s" % s)
    except Exception:
        raise AsmException("incorrect immediate value: %s" % s)

class AsmException(Exception):
    pass

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
        line = re.sub(r";.*", "", line) # strip comments
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
        self._reset()

    def assembleFile(self, filename):
        self._reset()
        self._parseFilePass(filename)
        self._backpatchPass()
        return self.code

    def _reset(self):
        self.code = {}
        self.labels = {}
        self.codeptr = 0
        self.backpatchQueue = [] # second stage (resolving forward reference)

    def _parseFilePass(self, filename):
        """ assembler first pass: convert source file to binary array """
        assert(type(filename) == str)
        with open(filename, "r") as f:
            parser = AsmLineParser()
            lineno = 1
            for line in f:
                # parse
                if not parser.parseLine(line):
                    raise AsmException("line %d: syntax error" % (lineno))
                label = parser.getLabel()
                instruction = parser.getInstruction()
                args = parser.getArgs()

                try:
                    # generate code
                    if label:
                        self._putLabel(label)
                    if instruction:
                        self._putInstruction(instruction, args)
                except AsmException as e:
                    raise AsmException("line %d: %s" % (lineno, str(e)))

                # increment line number
                lineno += 1

    def _backpatchPass(self):
        """ assembler second pass: fill in label addresses """
        for (codeptr, label, bits, relative) in self.backpatchQueue:
            value = self.labels[label]
            if relative:
                value = value - (codeptr + 1)
            self.code[codeptr] = patchCode(self.code[codeptr], value, bits)

    def _putLabel(self, label):
        assert(type(label) == str)
        self.labels[label] = self.codeptr

    def _markForBackpatch(self, index, label, bits, relative):
        """ Mark the last <bits> bits of the <index> position for later label
            backpatch (second stage). """
        assert(type(label) == str)
        assert(type(relative) == bool)
        self.backpatchQueue.append((self.codeptr, label, bits, relative))

    def _putCode(self, code):
        """ generate a 32-bit integer code """
        assert(type(code) == int)
        self.code[self.codeptr] = code
        self.codeptr += 1

    def _putInstruction(self, instruction, args):
        if instruction in ALIAS: # substitute alias
            instruction = ALIAS[instruction]
        if instruction not in INSTRUCTION:
            raise AsmException("unknown instruction %s" % (instruction))
        # get instruction info
        info = INSTRUCTION[instruction]
        opcode = info[0]
        category = info[1]

        # check number of arguments
        assert(category in CATEGORY_ARG_COUNT)
        expected_arg_count = CATEGORY_ARG_COUNT[category]
        if len(args) != expected_arg_count:
            raise AsmException("incorrect number of arguments. except %d, got %d"
                               % (expected_arg_count, len(args)))

        # call handler
        if category == CATEGORY_DA:
            handler = self._putInstruction_DA
        elif category == CATEGORY_DI:
            handler = self._putInstruction_DI
        elif category == CATEGORY_DAI:
            handler = self._putInstruction_DAI
        elif category == CATEGORY_DAB:
            handler = self._putInstruction_DAB
        elif category == CATEGORY_DAS:
            handler = self._putInstruction_DAS
        elif category == CATEGORY_AB:
            handler = self._putInstruction_AB
        elif category == CATEGORY_AI:
            handler = self._putInstruction_AI
        elif category == CATEGORY_I24:
            handler = self._putInstruction_I24
        elif category == CATEGORY_N:
            handler = self._putInstruction_N
        elif category == CATEGORY_A:
            handler = self._putInstruction_A
        elif category == CATEGORY_D:
            handler = self._putInstruction_D
        else:
            assert(False) # unhandled instruction category
        handler(opcode, args)

    def _generateRegister(self, reg):
        assert(type(reg) == str)
        value = regToInt(reg)
        assert(0 <= value <= 16)
        return value

    def _generateImmediate(self, imm, bits, relative):
        assert(type(imm) == str)
        assert(type(bits) == int)
        assert(type(relative) == bool)
        if re.match(r"-?[0-9]+", imm): # is integer
            return nBitInteger(imm, bits)
        elif re.match(r"[a-zA-Z0-9_$]+", imm): # is label
            label = imm
            self._markForBackpatch(self.codeptr, label, bits, relative)
            return 0 # temporary fill in zero and wait for backpatch
        else:
            raise AsmException("incorrect immediate value: %s" % imm)

    def _putInstruction_DA(self, opcode, args):
        reg_d = self._generateRegister(args[0])
        reg_a = self._generateRegister(args[1])
        self._putCode((opcode << 24) | (reg_d << 20) | (reg_a << 16))

    def _putInstruction_DI(self, opcode, args):
        reg_d = self._generateRegister(args[0])
        imm = self._generateImmediate(args[1], 16, relative=False)
        self._putCode((opcode << 24) | (reg_d << 20) | (imm))

    def _putInstruction_DAI(self, opcode, args):
        reg_d = self._generateRegister(args[0])
        reg_a = self._generateRegister(args[1])
        imm = self._generateImmediate(args[2], 16, relative=False)
        self._putCode((opcode << 24) | (reg_d << 20) | (reg_a << 16) | imm)

    def _putInstruction_DAB(self, opcode, args):
        reg_d = self._generateRegister(args[0])
        reg_a = self._generateRegister(args[1])
        reg_b = self._generateRegister(args[2])
        self._putCode((opcode << 24) | (reg_d << 20) | (reg_a << 16) | (reg_b << 12))

    def _putInstruction_DAS(self, opcode, args):
        reg_d = self._generateRegister(args[0])
        reg_a = self._generateRegister(args[1])
        reg_s = self._generateImmediate(args[2], 5, relative=False)
        self._putCode((opcode << 24) | (reg_d << 20) | (reg_a << 16) | (reg_s))

    def _putInstruction_AB(self, opcode, args):
        reg_a = self._generateRegister(args[0])
        reg_b = self._generateRegister(args[1])
        self._putCode((opcode << 24) | (reg_a << 16) | (reg_b << 12))

    def _putInstruction_AI(self, opcode, args):
        reg_a = self._generateRegister(args[0])
        imm = self._generateImmediate(args[1], 16, relative=False)
        self._putCode((opcode << 24) | (reg_a << 16) | (imm))

    def _putInstruction_I24(self, opcode, args):
        imm = self._generateImmediate(args[0], 24, relative=True)
        self._putCode((opcode << 24) | (imm))

    def _putInstruction_N(self, opcode, args):
        self._putCode((opcode << 24))

    def _putInstruction_A(self, opcode, args):
        reg_a = self._generateRegister(args[0])
        self._putCode((opcode << 24) | (reg_a << 16))

    def _putInstruction_D(self, opcode, args):
        reg_d = self._generateRegister(args[0])
        self._putCode((opcode << 24) | (reg_d << 20))

class CoeWriter(object):

    def __init__(self, file=sys.stdout):
        self.fout = file

    def write(self, code):
        assert(type(code) == dict)
        self.fout.write("MEMORY_INITIALIZATION_RADIX=2;\n")
        self.fout.write("MEMORY_INITIALIZATION_VECTOR=\n")
        for index in sorted(code.keys()):
            assert(type(index) == int)
            line = '{0:032b},\n'.format(code[index])
            self.fout.write(line)

class TextFormatWriter(object):

    def __init__(self, file=sys.stdout):
        self.fout = file

    def write(self, code):
        assert(type(code) == dict)
        for index in sorted(code.keys()):
            assert(type(index) == int)
            line = "%(addr)x %(value)x\n" % {'addr': index, 'value': code[index]}
            self.fout.write(line)

if __name__ == "__main__":
    asm = Assembler()
    try:
        code = asm.assembleFile(sys.argv[1])
        with open("output.txt", "w") as f:
            writer = TextFormatWriter(f)
            writer.write(code)
    except AsmException as e:
        print("error: %s" % (str(e)))
