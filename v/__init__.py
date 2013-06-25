#!/usr/bin/env python
'''
Command line script for opening a file in vim
that lies in the current working directory's
subtree matching a partially given filename.
'''


REQUIRED_PYTHON = (2, 7)
SYS_ERROR = 42
VERBOSE = False
CHAR_COMBOS = {}


try:
    import os
    import re
    import sys
except ImportError as e:
    module = str(e).split()[-1]
    print "Required Python module missing: ", e
    sys.exit(SYS_ERROR)


def calculate_score(regex, literal, path):
    '''
    Get the score for a given path matching a pattern
    If the path ends with the pattern, give the highest score
    Also if the pattern is an exact match in the path, give a high score
    Otherwise, do more complicated algorithm to decide what I'm really
    trying to find.
    Also if no 2 characters in the string are in a row, assume that
    isn't really what we're looking for and discard
    '''
    if path.endswith(literal):
        score = 100
    elif literal in path:
        # This is an exact match to give it a high score
        # Start with 100, but give more precendence to an exact match
        # ending with the exact match
        match = re.search(regex, path)
        len_from_end = len(path) - match.end()
        score = 100 - len_from_end
    else:
        match = re.search(regex, path)
        # A match is scored more if the characters in the patterns are closer
        # to each other and if it's closer to the end of the path
        if match is None:
            score = 0
        else:
            # Check if any 2 characters in the pattern are consecutive in path
            char_combos = get_char_combos(literal)
            any_match = False
            for cc in char_combos:
                if cc in path:
                    any_match = True
                    break

            if any_match is False:
                score = 0
            else:
                distance_between = match.end() - match.start()
                len_from_end = len(path) - match.end()
                score = 100 - len_from_end - distance_between

    return score


def check_version():
    '''
    Check python version
    If less than 2.6 print message that Python 2.6 or higher is required
    '''
    if sys.version_info < REQUIRED_PYTHON:
        print "Python {major}.{minor} or greater is required".format(
            major=REQUIRED_PYTHON[0], minor=REQUIRED_PYTHON[1]
        )
        sys.exit(SYS_ERROR)
    return True


def find(partial):
    '''
    Walk directory path and find files matching search
    If multiple files are found, call prompt() with list
    '''
    # Make the search fuzzy match
    search = '.*?'.join(map(re.escape, list(partial)))

    rootdir = os.getcwd()
    all_files = []
    for root, subFolders, files in os.walk(rootdir):
        for f in files:
            # Skip files that end in .swp
            if f.endswith(('.swp', '.pyc')):
                continue

            full_path = os.path.abspath(os.path.join(root, f))

            # Also skip files in .git folder
            if '.git' in full_path:
                continue

            all_files.append(full_path)

    scores = []
    for f in all_files:
        scores.append(calculate_score(search, partial, f))

    # Zip scores & all files together, but only for scores > 0
    matches = [f for (score, f) in sorted(zip(scores, all_files),
               reverse=True) if score > 0]

    if len(matches) == 1:
        target = matches[0]
    else:
        target = prompt(matches)

    return target


def get_char_combos(chars):
    '''
    Get the 2 letter character combos from a string
    '''
    global CHAR_COMBOS
    combo_list = CHAR_COMBOS.get(chars)

    if combo_list is None:
        char_list = []
        combo_list = []
        for char in chars:
            char_list.append(char)
        for key, val in enumerate(char_list):
            try:
                next_key = key + 1
                combo_list.append(val + char_list[next_key])
            except IndexError:
                break
        CHAR_COMBOS[chars] = combo_list

    return combo_list


def main():
    '''
    Run
    '''
    try:
        check_version()
        partial = parse_args()
        path = find(partial)
        vim_open(path)
    except KeyboardInterrupt:
        sys.exit(SYS_ERROR)


def parse_args():
    '''
    Check to see if passed command is valid
    '''
    args = sys.argv[1:]
    filtered_args = []

    # Check if -h or --help were given and ignore rest
    for arg in args:
        if arg == '-h' or arg == '--help':
            usage()
        elif arg == '-v' or arg == '--verbose':
            global VERBOSE
            VERBOSE = True
        else:
            filtered_args.append(arg)

    if len(filtered_args) < 1:
        usage()

    return filtered_args[0]


def prompt(file_list):
    '''
    Accept list of options and prompt user for choice
    Return string of choice path
    '''
    i = 0
    for fl in file_list:
        print "[{0}] {1}".format(i, fl)
        i += 1

    while True:
        choice = input('Please choose a file: ')
        if isinstance(choice, int):
            break
        else:
            print 'Invalid choice {0}'.format(choice)

    return file_list[choice]


def usage(error=""):
    '''
    Print script usage with an optional error message passed in
    '''
    message = error
    message += '''
Usage:
    v [-h|--help] [-v|--verbose] partial_file_name

Commands:
    * None                  No subcommands

    Optional:
    * -h | --help           Display this menu
    * -v | --verbose        Verbose ouptput
    '''
    sys.exit(message)


def vim_open(path):
    '''
    Open the given file path in vim
    '''
    os.execlp('vim', 'vim', path)


if __name__ == '__main__':
    main()
