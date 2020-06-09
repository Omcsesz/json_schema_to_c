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

import argparse
import os

from js2c.schema import load_schema
from js2c.codegen.root import RootGenerator
from js2c.settings import Settings


def parse_args():
    parser = argparse.ArgumentParser(description="Create a JSON parser in C based on a json schema")
    parser.add_argument(
        "schema_file",
        type=argparse.FileType('r'),
        help="Filename of the JSON schema to use. Schema version 7 is supported.",
    )
    parser.add_argument(
        "c_file",
        type=argparse.FileType('w'),
        help="Filename of the generated parser .c file",
    )
    parser.add_argument(
        "h_file",
        type=argparse.FileType('w'),
        help="Filename of the generated parser .h file",
    )
    Settings.fill_argparse(parser)
    return parser.parse_args()


def main(args):
    schema = load_schema(args.schema_file)
    settings = Settings(vars(args))
    root_generator = RootGenerator(schema, settings)
    root_generator.generate_parser_h(
        args.h_file,
        args.h_prefix_file.read() if args.h_prefix_file is not None else None,
        args.h_postfix_file.read() if args.h_postfix_file is not None else None,
    )
    root_generator.generate_parser_c(
        args.c_file,
        os.path.basename(args.h_file.name),
        args.c_prefix_file.read() if args.c_prefix_file is not None else None,
        args.c_postfix_file.read() if args.c_postfix_file is not None else None,
    )


if __name__ == "__main__":
    main(parse_args())
