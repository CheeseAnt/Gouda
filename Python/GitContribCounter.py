import argparse
import os
from subprocess import check_output

parser = argparse.ArgumentParser()

parser.add_argument("directory", type=str, help="Directory to get log of")
parser.add_argument("author", type=str, help="Author to count num lines")

args = parser.parse_args()

if(os.path.isdir(args.directory)):
    os.chdir(args.directory)

    comm = "git log --author=".split(" ")
    comm.append(args.author)
    comm.extend("--pretty=tformat: --numstat".split(" "))

    output = check_output(comm).decode("utf-8")

    output = output.split("\n")

    lines_added = 0
    lines_deleted = 0

    for line in output:
        if(line != ""):
            line = line.split("\t")

            try:
                lines_added += int(line[0])
                lines_deleted += int(line[1])
            except ValueError:
                print("Could not parse line: " + " ".join(line))

    print("Author: " + args.author + " contributed " + str(lines_added) + " lines added and " +
            str(lines_deleted) + " lines deleted over " + str(len(output)) + " commits.")

    print("Net Lines: " + str(lines_added - lines_deleted))
else:
    print("Invalid directory specified: " + args.directory)
    parser.print_help()

