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
import os
import re

from .code_block_printer import CodeBlockPrinter

from .generator_factory import GeneratorFactory


DIR_OF_THIS_FILE = os.path.dirname(__file__)

NOTE_FOR_GENERATED_FILES = """
/* This file was generated by JSON Schema to C.
 * Any changes made to it will be lost on regeneration. */
"""


class RootGenerator:
    def __init__(self, schema, args):
        self.args = args
        self.root_generator = GeneratorFactory.get_generator_for(schema, schema['$id'], args)
        self.name = schema['$id']

    def generate_root_parser(self, out_file):
        out_file.print("bool json_parse_{name}(const char* json_string, {name}_t* out)".format(name=self.name))
        with out_file.code_block():
            out_file.print("parse_state_t parse_state_var;")
            out_file.print("parse_state_t* parse_state = &parse_state_var;")
            out_file.print("if(builtin_parse_json_string(parse_state, json_string))")
            with out_file.code_block():
                out_file.print("return true;")
            self.root_generator.generate_parser_call(
                "out",
                out_file,
            )
            out_file.print("return false;")
        out_file.print("")

    def generate_parser_h(self, h_file, prefix, postfix):
        h_file_name = h_file.name
        h_file = CodeBlockPrinter(h_file)

        h_file.write(NOTE_FOR_GENERATED_FILES)

        header_guard_name = re.sub("[^A-Z0-9]", "_", os.path.basename(h_file_name).upper())
        h_file.print("#ifndef {}".format(header_guard_name))
        h_file.print("#define {}".format(header_guard_name))

        h_file.print("#include <stdint.h>")
        h_file.print("#include <stdbool.h>")

        if prefix:
            h_file.print_separator("User-added prefix")
            h_file.write(prefix)

        h_file.print_separator("Generated type declarations")
        self.root_generator.generate_type_declaration(h_file, force=True)
        h_file.print("bool json_parse_{name}(const char* json_string, {name}_t* out);".format(name=self.name))

        if postfix:
            h_file.print_separator("User-added postfix")
            h_file.write(postfix)

        h_file.print("#endif /* {} */".format(header_guard_name))

    def generate_parser_c(self, c_file, h_file_name, prefix, postfix):
        c_file = CodeBlockPrinter(c_file)

        c_file.write(NOTE_FOR_GENERATED_FILES)
        c_file.print('#include "{}"'.format(h_file_name))

        if prefix:
            c_file.print_separator("User-added prefix")
            c_file.write(prefix)

        with open(os.path.join(DIR_OF_THIS_FILE, '..', '..', 'jsmn', 'jsmn.h')) as jsmn_h:
            c_file.print("")
            c_file.print('#define JSMN_STATIC')
            c_file.print('#define JSMN_STRICT')
            c_file.print("")
            c_file.print_separator("jsmn.h (From https://github.com/zserge/jsmn)")
            c_file.write(jsmn_h.read())
            c_file.print("")

        with open(os.path.join(DIR_OF_THIS_FILE, 'builtin_parsers.c')) as builtins_file:
            c_file.print_separator("builtin_parsers.c")

            max_token_num = self.root_generator.max_token_num()
            if self.args.additional_token_number is not None:
                max_token_num += self.args.additional_token_number
            c_file.print("#define MAX_TOKEN_NUM {}\n".format(max_token_num))
            c_file.write(builtins_file.read())
            c_file.print("")

        c_file.print_separator("Generated parsers")
        c_file.print("")
        self.root_generator.generate_parser_bodies(c_file)
        self.generate_root_parser(c_file)

        if postfix:
            c_file.print_separator("User-added postfix")
            c_file.write(postfix)
