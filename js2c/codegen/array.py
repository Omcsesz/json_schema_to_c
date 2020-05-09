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
from typing import Optional
from .base import Generator


class ArrayGenerator(Generator):
    minItems: int = 0
    maxItems: Optional[int] = None

    def __init__(self, schema, name, generators):
        super().__init__(schema, name, generators)
        if self.maxItems is None:
            raise ValueError("Arrays must have maxItems")
        item_generator_class = generators[schema["items"]["type"]]
        self.item_generator = item_generator_class(
            schema["items"],
            "{}_item".format(name),
            generators
        )

    def generate_field_declaration(self, field_name, out_file):
        out_file.print_with_docstring(
            "{}_t {};".format(self.name, field_name), self.description
        )

    def generate_parser_call(self, out_var_name, out_file):
        out_file.print(
            "if(parse_{}(parse_state, {}))"
            .format(self.name, out_var_name)
        )
        with out_file.code_block():
            out_file.print("return true;")

    def generate_type_declaration(self, out_file, *, force=False):
        _ = force  # basically (void)force

        self.item_generator.generate_type_declaration(out_file)

        out_file.print("typedef struct {}_s ".format(self.name) + "{")
        with out_file.indent():
            out_file.print_with_docstring("uint64_t n;", "The number of elements in the array")
            self.item_generator.generate_field_declaration(
                "items[{}]".format(self.maxItems), out_file
            )
        out_file.print("}} {}_t;".format(self.name))
        out_file.print("")

    def generate_range_checks(self, out_file):
        out_file.print("if (n > {})".format(self.maxItems))
        with out_file.code_block():
            self.generate_logged_error(
                ["Array {} too large. Length: %i. Maximum length: {}.".format(self.name, self.maxItems), "n"],
                out_file
            )
        if self.minItems:
            out_file.print("if (n < {})".format(self.minItems))
            with out_file.code_block():
                self.generate_logged_error(
                    ["Array {} too small. Length: %i. Minimum length: {}.".format(self.name, self.minItems), "n"],
                    out_file
                )

    def generate_parser_bodies(self, out_file):
        self.item_generator.generate_parser_bodies(out_file)

        out_file.print("static bool parse_{name}(parse_state_t* parse_state, {name}_t* out)".format(name=self.name))
        with out_file.code_block():
            out_file.print("if(check_type(parse_state, JSMN_ARRAY))")
            with out_file.code_block():
                out_file.print("return true;")
            out_file.print("int i;")
            out_file.print("const int n = parse_state->tokens[parse_state->current_token].size;")
            self.generate_range_checks(out_file)
            out_file.print("out->n = n;")
            out_file.print("parse_state->current_token += 1;")
            out_file.print("for (i = 0; i < n; ++ i)")
            with out_file.code_block():
                self.item_generator.generate_parser_call(
                    "&out->items[i]",
                    out_file
                )
            out_file.print("return false;")
        out_file.print("")
