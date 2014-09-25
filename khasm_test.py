#!/usr/bin/env python3

import unittest
import khasm

class TestAsmLineParser(unittest.TestCase):

    def testParseLine(self):
        asm = khasm.AsmLineParser()
        # with label
        self.assertTrue(asm.parseLine("label: inst a1, a2, a3"))
        self.assertEqual(asm.getLabel(), "label")
        self.assertEqual(asm.getInstruction(), "inst")
        self.assertListEqual(asm.getArgs(), ["a1", "a2", "a3"])
        # without label
        self.assertTrue(asm.parseLine("inst a1, a2, a3"))
        self.assertEqual(asm.getLabel(), None)
        self.assertEqual(asm.getInstruction(), "inst")
        self.assertListEqual(asm.getArgs(), ["a1", "a2", "a3"])
        # empty line
        self.assertTrue(asm.parseLine("  "))
        self.assertEqual(asm.getLabel(), None)
        self.assertEqual(asm.getInstruction(), None)
        self.assertListEqual(asm.getArgs(), [])

    def testParseArgLine(self):
        asm = khasm.AsmLineParser()
        # should split and strip args
        self.assertListEqual(asm.parseArgLine("1, 2, 3"), ["1", "2", "3"])
        self.assertListEqual(asm.parseArgLine(" a0 ,   b2 "), ["a0", "b2"])
        # should output None for incorrect inputs (missing arguments)
        self.assertEqual(asm.parseArgLine("a0,"), None)
        self.assertEqual(asm.parseArgLine(",b"), None)
        # return empty list if argline=None is given or argline is empty
        self.assertListEqual(asm.parseArgLine(""), [])
        self.assertListEqual(asm.parseArgLine(" "), [])
        self.assertListEqual(asm.parseArgLine(None), [])

class TestHelperFunctions(unittest.TestCase):

    def testRegToInt(self):
        self.assertEqual(khasm.regToInt("r0"), 0)
        self.assertEqual(khasm.regToInt("r1"), 1)
        self.assertEqual(khasm.regToInt("r5"), 5)
        self.assertEqual(khasm.regToInt("r10"), 10)
        self.assertEqual(khasm.regToInt("r11"), 11)
        self.assertEqual(khasm.regToInt("r15"), 15)
        self.assertRaises(khasm.AsmException, khasm.regToInt, "r16")
        self.assertRaises(khasm.AsmException, khasm.regToInt, "ar0b")

    def testPatchCode(self):
        self.assertEqual(khasm.patchCode(0x00000000, 0x7f, 8), 0x0000007f)
        self.assertEqual(khasm.patchCode(0x00000000, 0x7f, 4), 0x0000000f)
        self.assertEqual(khasm.patchCode(0x00000000, 0x7f, 3), 0x00000007)
        self.assertEqual(khasm.patchCode(0x00000000, 0x51234, 16), 0x00001234)
        self.assertEqual(khasm.patchCode(0x00000000, 0x51234, 24), 0x00051234)

    def testNBitInteger(self):
        self.assertEqual(khasm.nBitInteger("3", 8), 0x03)
        self.assertEqual(khasm.nBitInteger("-3", 8), 0xfd)
        self.assertRaises(khasm.AsmException, khasm.nBitInteger, "-3", 1)

if __name__ == "__main__":
    unittest.main()
