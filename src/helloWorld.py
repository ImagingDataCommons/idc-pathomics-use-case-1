#!/usr/bin/env python3

# Copyright (c) Fraunhofer MEVIS, Germany. All rights reserved.
# **InsertLicense** code

from shutil import copyfile

if __name__ == "__main__":
    print("Hello world!")

    # demo use of input and output mount
    copyfile("/input/someFile.txt", "/output/someOutputFile.txt")
