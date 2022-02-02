'''
    Helper app to convert JPL/NASA files into CSV. Run like this:
    python to_csv.py -infile JPL.txt > JPL.csv
'''

import os
import re
import sys
import argparse
import platform


def to_csv_helper(filename):
    '''
    to_csv_helper extracts the file contents in-between
    the markers $$SOE and $$EOE
    '''
    with open(filename, 'r') as file:
        filedata = file.read()

    begin, end = filedata.split('$$SOE', 1)
    extract, _ = end.split('$$EOE', 1)
    return extract


def to_csv(filename):
    '''
    the main function that converts into CSV
    '''
    filedata = to_csv_helper(filename)

    # first prepare the data for conversion
    r1 = re.sub('= +', '=', filedata)
    r2 = re.sub(' =', '=', r1)
    r3 = re.sub(' ', ',', r2)
    r4 = re.sub(r'=A\.D\.,', '=TS,DT=', r3)
    r5 = re.sub(',TDB', '=TDB', r4)
    r6 = re.sub('\n', ',', r5)

    # break all the data into individual words
    words = []
    for word in r6.split(','):
        word.strip()
        if word and word != ',':
            words.append(word)

    # the header line with the column names
    header = ["TS", "DT", "TDB", "X", "Y", "Z",
              "VX", "VY", "VZ", "LT", "RG", "RR"]

    # the column names we are looking for as tags
    tags = ["(.*)=TS", "DT=(.*)", "(.*)=TDB", "X=(.*)", "Y=(.*)", "Z=(.*)",
            "VX=(.*)", "VY=(.*)", "VZ=(.*)", "LT=(.*)", "RG=(.*)", "RR=(.*)"]
    ntags = len(tags)
    line = ''

    # print the header line with the column names
    print(', '.join(header))

    # iterate over all words and assign to individual lines
    for (word, i) in zip(words, range(len(words))):
        # extract the value
        val = re.search(tags[i % ntags], word).group(1)

        # is this the last tag?
        if re.search(tags[ntags - 1], word):
            # if this is the last tag, then complete the line and print it
            line += re.search(tags[ntags - 1], word).group(1)
            print(line)
            line = ''
        else:
            # if it is not the last tag, then keep appending to the line
            line += val + ', '


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""Retrieve and process files""")
    parser.add_argument('-infile', '--input-file',
                        help='read an input file and convert to CSV',
                        dest='infile', action='store', nargs='?',
                        default=r'default')
    args = parser.parse_args()

    if (args.infile != r'default' and not os.path.exists(args.infile)):
        print(f"Cannot find input file {args.infile}")
        sys.exit(-1)

    to_csv(args.infile)