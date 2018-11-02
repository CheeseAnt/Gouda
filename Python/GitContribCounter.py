import argparse
import os
from subprocess import check_output

parser = argparse.ArgumentParser()

parser.add_argument("directory", type=str, help="Directory to get log of")
parser.add_argument("author", type=str, help="Author to count num lines")

args = parser.parse_args()

if(os.path.isdir(args.directory)):
    os.chdir(args.directory)

    output = check_output("git log --author=\"" + args.author + "\" --pretty=tformat: --numstat").decode("utf-8")

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

    print("Author:", args.author, "contributed", lines_added, "lines added and", lines_deleted,
            "lines deleted over", len(output), "commits.")

    print("Net Lines: " + str(lines_added - lines_deleted))
else:
    print("Invalid directory specified: " + args.directory)
    parser.print_help()

