#!/usr/bin/env python3
#
# MIT License
#
# Copyright (c) 2020 Alex Badics
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


class CodeBlockContextManager:
    def __init__(self, printer, indent_level, indent_only=False):
        self.printer = printer
        self.indent_level = indent_level
        self.indent_only = indent_only

    def __enter__(self):
        if not self.indent_only:
            self.printer.print("{")
        self.printer.indent_level += self.indent_level
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.printer.indent_level -= self.indent_level
        if not self.indent_only:
            self.printer.print("}")


class CodeBlockPrinter:
    def __init__(self, file):
        self.file = file
        self.indent_level = 0

    def print(self, line):
        """ Print an indented line """
        if not line:
            self.file.write("\n")
        else:
            self.file.write("{}{}\n".format(" "*self.indent_level, line))

    def print_separator(self, separator_str):
        pad_length = (70 - len(separator_str))//2
        self.print("/* {p} {s} {p} */".format(p="=" * pad_length, s=separator_str))

    def write(self, data):
        """ Write raw data to the file """
        self.file.write(data)

    def code_block(self, indent_level=4):
        return CodeBlockContextManager(self, indent_level)

    def indent(self, indent_level=4):
        return CodeBlockContextManager(self, indent_level, indent_only=True)
