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

if __name__ == "__main__":
    unittest.main()
