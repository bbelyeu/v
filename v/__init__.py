#!/usr/bin/env python
'''
Command line script for opening a file in vim
that lies in the current working directory's
subtree matching a partially given filename.
'''


REQUIRED_PYTHON = (2, 7)
SYS_ERROR = 42
VERBOSE = False


try:
    import os
    import re
    import sys
except ImportError as e:
    module = str(e).split()[-1]
    print "Required Python module missing: ", e
    sys.exit(SYS_ERROR)


def calculate_score(pattern, path):
    '''
    Get the score for a given path matching a pattern
    '''
    match = re.search(pattern, path)

    return 0 if match is None else \
        100.0 / ((1 + match.start()) * (match.end() - match.start() + 1))


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
            if f.endswith('.swp'):
                continue

            full_path = os.path.abspath(os.path.join(root, f))

            # Also skip files in .git folder
            if '.git' in full_path:
                continue

            all_files.append(full_path)

    scores = []
    for f in all_files:
        scores.append(calculate_score(search, f))

    # Zip scores & all files together, but only for scores > 0
    matches = [f for (score, f) in sorted(zip(scores, all_files),
               reverse=True) if score > 0]

    if len(matches) == 1:
        target = matches[0]
    else:
        target = prompt(matches)

    return target


def main():
    '''
    Run
    '''
    check_version()
    partial = parse_args()
    path = find(partial)
    vim_open(path)


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
