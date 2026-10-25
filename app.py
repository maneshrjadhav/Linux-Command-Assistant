"""
Linux Command Assistant — Smart Linux Learning Platform
Flask Backend for AIAD College Project

A secure, educational platform providing:
  - In-memory knowledge base with 50+ Linux commands
  - Smart command tokenizer supporting flags, paths, and sudo
  - Fuzzy suggestion engine for unknown commands
  - Zero host shell execution security guarantee
"""

import difflib
import posixpath
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# ============================================================================
# COMPREHENSIVE LINUX COMMAND KNOWLEDGE BASE (50+ Commands)
# Categories:
#   1. Files and directories
#   2. File permissions
#   3. Text processing
#   4. Processes and system monitoring
#   5. Networking
#   6. Package management
#   7. Storage and disk usage
#   8. System services
# ============================================================================
COMMAND_KNOWLEDGE_BASE = {
    # ------------------------------------------------------------------------
    # 1. FILES AND DIRECTORIES
    # ------------------------------------------------------------------------
    "ls": {
        "name": "ls",
        "meaning": "List Directory Contents",
        "syntax": "ls [options] [directory_or_file]",
        "purpose": "Lists files and directories contained within the current or specified directory.",
        "example": "ls -la",
        "example_explanation": "Lists all files (including hidden files starting with a dot) in long listing format showing permissions, owner, file size, and modification date.",
        "category": "Files and directories",
        "difficulty": "Beginner",
        "safety_warning": "",
        "options": [
            {"flag": "-l", "desc": "Use long listing format (permissions, owner, size, date)."},
            {"flag": "-a", "desc": "Include entries starting with . (hidden files)."},
            {"flag": "-h", "desc": "Print human-readable sizes (e.g. 1K, 234M, 2G)."},
            {"flag": "-t", "desc": "Sort by modification time, newest first."}
        ],
        "use_cases": ["Checking folder contents", "Verifying file permissions", "Finding hidden configuration dotfiles"],
        "related_commands": ["pwd", "dir", "tree", "find"],
        "beginner_notes": "Combine options like 'ls -lah' for human-readable long listing with hidden files."
    },
    "pwd": {
        "name": "pwd",
        "meaning": "Print Working Directory",
        "syntax": "pwd [options]",
        "purpose": "Outputs the absolute, full pathname of the current working directory.",
        "example": "pwd",
        "example_explanation": "Prints the current directory path (such as /home/student/projects) so you always know where you are in the filesystem.",
        "category": "Files and directories",
        "difficulty": "Beginner",
        "safety_warning": "",
        "options": [
            {"flag": "-L", "desc": "Display logical current directory path including symlinks (default)."},
            {"flag": "-P", "desc": "Display physical current working directory, resolving all symlinks."}
        ],
        "use_cases": ["Confirming current location before copying or deleting files", "Copying absolute path for scripts"],
        "related_commands": ["cd", "ls", "whoami"],
        "beginner_notes": "Useful when lost in deeply nested directory structures."
    },
    "mkdir": {
        "name": "mkdir",
        "meaning": "Make Directory",
        "syntax": "mkdir [options] directory_name",
        "purpose": "Creates one or more new directories (folders) in the filesystem.",
        "example": "mkdir practice",
        "example_explanation": "Creates a new folder named 'practice' in your current working directory.",
        "category": "Files and directories",
        "difficulty": "Beginner",
        "safety_warning": "",
        "options": [
            {"flag": "-p", "desc": "Create parent directories as needed without reporting an error if they exist."},
            {"flag": "-v", "desc": "Verbose mode: print a message for each created directory."},
            {"flag": "-m", "desc": "Set file permission mode for the new directory directly."}
        ],
        "use_cases": ["Organizing new projects", "Creating nested directory trees with 'mkdir -p a/b/c'"],
        "related_commands": ["rmdir", "touch", "cp"],
        "beginner_notes": "Always use '-p' flag when creating nested directories in one go: 'mkdir -p project/src/tests'."
    },
    "cp": {
        "name": "cp",
        "meaning": "Copy Files and Directories",
        "syntax": "cp [options] source_file destination",
        "purpose": "Copies files or directories from a source location to a target destination.",
        "example": "cp notes.txt backup_notes.txt",
        "example_explanation": "Creates an exact duplicate of 'notes.txt' and saves it as 'backup_notes.txt' without modifying the original.",
        "category": "Files and directories",
        "difficulty": "Beginner",
        "safety_warning": "Will overwrite destination files with identical names without confirmation unless '-i' is passed.",
        "options": [
            {"flag": "-r / -R", "desc": "Copy directories recursively."},
            {"flag": "-i", "desc": "Interactive: prompt before overwriting existing files."},
            {"flag": "-v", "desc": "Verbose: explain what is being done."},
            {"flag": "-u", "desc": "Update: copy only when source file is newer than destination."}
        ],
        "use_cases": ["Creating backup copies before modifying configs", "Duplicating project templates"],
        "related_commands": ["mv", "scp", "rsync"],
        "beginner_notes": "Remember the '-r' flag is mandatory when copying directories."
    },
    "mv": {
        "name": "mv",
        "meaning": "Move / Rename",
        "syntax": "mv [options] source destination",
        "purpose": "Moves files or directories to a different directory, or renames them if the target is in the same folder.",
        "example": "mv report.txt documents/",
        "example_explanation": "Moves the file 'report.txt' from the current folder into the 'documents' directory.",
        "category": "Files and directories",
        "difficulty": "Beginner",
        "safety_warning": "Can overwrite existing files in destination silently unless '-i' flag is used.",
        "options": [
            {"flag": "-i", "desc": "Prompt before overwriting an existing destination file."},
            {"flag": "-n", "desc": "Do not overwrite any existing destination file."},
            {"flag": "-v", "desc": "Verbose mode: explain what is being moved or renamed."}
        ],
        "use_cases": ["Renaming a file: 'mv old.py new.py'", "Organizing files into subdirectories"],
        "related_commands": ["cp", "rm", "rename"],
        "beginner_notes": "In Linux, renaming and moving are the exact same operation performed by 'mv'."
    },
    "rm": {
        "name": "rm",
        "meaning": "Remove (Delete)",
        "syntax": "rm [options] file...",
        "purpose": "Removes (deletes) files or directories from the filesystem permanently.",
        "example": "rm temp.txt",
        "example_explanation": "Permanently deletes the file 'temp.txt' from the current directory.",
        "category": "Files and directories",
        "difficulty": "Beginner",
        "safety_warning": "CRITICAL: Linux has NO recycle bin! Files deleted with 'rm' are permanently lost. Never run 'rm -rf /' or with wildcards without checking first.",
        "options": [
            {"flag": "-r / -R", "desc": "Remove directories and their contents recursively."},
            {"flag": "-f", "desc": "Force: ignore nonexistent files and never prompt before deletion."},
            {"flag": "-i", "desc": "Interactive: prompt for confirmation before every removal."}
        ],
        "use_cases": ["Cleaning up temporary logs and build artifacts", "Deleting obsolete project directories"],
        "related_commands": ["rmdir", "unlink", "shred"],
        "beginner_notes": "Use '-i' when you are unsure to confirm deletion before any file is removed."
    },
    "cd": {
        "name": "cd",
        "meaning": "Change Directory",
        "syntax": "cd [directory_path]",
        "purpose": "Changes the current working directory in the terminal shell.",
        "example": "cd /var/log",
        "example_explanation": "Navigates your terminal directly into the '/var/log' directory.",
        "category": "Files and directories",
        "difficulty": "Beginner",
        "safety_warning": "",
        "options": [
            {"flag": "~", "desc": "Shortcut for the user's home directory ('cd ~')."},
            {"flag": "-", "desc": "Switch back to the previous working directory ('cd -')."},
            {"flag": "..", "desc": "Move up one directory level to the parent folder ('cd ..')."}
        ],
        "use_cases": ["Navigating filesystem", "Switching quickly to home folder with plain 'cd'"],
        "related_commands": ["pwd", "pushd", "popd"],
        "beginner_notes": "Typing 'cd' alone without arguments always takes you back to your home directory."
    },
    "touch": {
        "name": "touch",
        "meaning": "Change File Timestamps / Create File",
        "syntax": "touch [options] file...",
        "purpose": "Updates the access and modification times of each file, or creates an empty file if it does not already exist.",
        "example": "touch app.py",
        "example_explanation": "Creates a new empty file named 'app.py' if it doesn't exist, or refreshes its timestamp if it does.",
        "category": "Files and directories",
        "difficulty": "Beginner",
        "safety_warning": "",
        "options": [
            {"flag": "-c", "desc": "Do not create any files if they do not exist."},
            {"flag": "-a", "desc": "Change only the access time."},
            {"flag": "-m", "desc": "Change only the modification time."}
        ],
        "use_cases": ["Quickly creating empty script or text files", "Updating timestamps to trigger build scripts"],
        "related_commands": ["nano", "cat", "mkdir"],
        "beginner_notes": "The fastest way to scaffold new empty source files in Linux."
    },
    "find": {
        "name": "find",
        "meaning": "Find Files in Directory Hierarchy",
        "syntax": "find [path] [expression]",
        "purpose": "Searches for files and directories in a directory hierarchy based on criteria like name, size, type, or modification date.",
        "example": "find . -name \"*.py\"",
        "example_explanation": "Searches the current directory and all subdirectories for files ending with the .py extension.",
        "category": "Files and directories",
        "difficulty": "Intermediate",
        "safety_warning": "When using '-delete' or '-exec rm', always run without those flags first to verify the matched files list.",
        "options": [
            {"flag": "-name", "desc": "Search for files by filename pattern (case-sensitive)."},
            {"flag": "-iname", "desc": "Case-insensitive search by filename."},
            {"flag": "-type f / d", "desc": "Filter by file type: 'f' for regular file, 'd' for directory."},
            {"flag": "-size", "desc": "Filter by size (e.g., '+100M' for larger than 100 megabytes)."}
        ],
        "use_cases": ["Locating lost config files", "Finding large files hogging disk space", "Batch processing files with -exec"],
        "related_commands": ["locate", "grep", "which", "whereis"],
        "beginner_notes": "Always quote wildcard patterns like \"*.log\" so your current shell doesn't expand them first."
    },
    "ln": {
        "name": "ln",
        "meaning": "Link (Create Links Between Files)",
        "syntax": "ln [options] target link_name",
        "purpose": "Creates hard links or symbolic (soft) links pointing to target files or directories.",
        "example": "ln -s /var/www/html site",
        "example_explanation": "Creates a symbolic link named 'site' that points directly to '/var/www/html'.",
        "category": "Files and directories",
        "difficulty": "Intermediate",
        "safety_warning": "",
        "options": [
            {"flag": "-s", "desc": "Create a symbolic (soft) link instead of a hard link."},
            {"flag": "-f", "desc": "Force: remove existing destination files before creating link."},
            {"flag": "-v", "desc": "Verbose: print the name of each linked file."}
        ],
        "use_cases": ["Shortcutting long deep directory paths", "Managing library versions in /usr/lib"],
        "related_commands": ["cp", "readlink", "ls"],
        "beginner_notes": "Always use '-s' for symbolic links unless you have a specific requirement for a hard link."
    },
    "tree": {
        "name": "tree",
        "meaning": "Tree View of Directory Hierarchy",
        "syntax": "tree [options] [directory]",
        "purpose": "Recursively displays directories and files in an indented depth-colored visual tree format.",
        "example": "tree -L 2",
        "example_explanation": "Shows the directory structure up to a maximum depth of 2 levels below the current folder.",
        "category": "Files and directories",
        "difficulty": "Beginner",
        "safety_warning": "",
        "options": [
            {"flag": "-L level", "desc": "Max display depth of the directory tree."},
            {"flag": "-d", "desc": "List directories only, omitting files."},
            {"flag": "-a", "desc": "Include all files, including hidden dotfiles."},
            {"flag": "-h", "desc": "Print size of files in human-readable units."}
        ],
        "use_cases": ["Visualizing project structures for documentation", "Auditing folder layouts"],
        "related_commands": ["ls", "find"],
        "beginner_notes": "In deep repositories, always specify '-L 2' or '-L 3' to avoid scrolling through thousands of lines."
    },

    # ------------------------------------------------------------------------
    # 2. FILE PERMISSIONS
    # ------------------------------------------------------------------------
    "chmod": {
        "name": "chmod",
        "meaning": "Change Mode (Permissions)",
        "syntax": "chmod [options] mode file_or_directory",
        "purpose": "Modifies file system access permissions (read, write, execute) for the file owner, user group, and others.",
        "example": "chmod 755 script.sh",
        "example_explanation": "Grants the owner full permissions (Read, Write, Execute = 7), while granting the group and others Read and Execute permissions (5).",
        "category": "File permissions",
        "difficulty": "Intermediate",
        "safety_warning": "Avoid setting 'chmod 777' on sensitive system files or web directories; it grants everyone write access.",
        "options": [
            {"flag": "-R", "desc": "Change files and directories recursively."},
            {"flag": "+x", "desc": "Add execute permission for all users."},
            {"flag": "u+rwx", "desc": "Symbolic notation: give user/owner read, write, and execute permissions."}
        ],
        "use_cases": ["Making a shell script executable: 'chmod +x run.sh'", "Securing private SSH keys: 'chmod 600 id_rsa'"],
        "related_commands": ["chown", "chgrp", "umask", "ls"],
        "beginner_notes": "Numeric modes: 4 = Read, 2 = Write, 1 = Execute. Add them: 4+2+1=7 (Full), 4+1=5 (Read+Execute)."
    },
    "chown": {
        "name": "chown",
        "meaning": "Change Owner",
        "syntax": "chown [options] [owner][:group] file...",
        "purpose": "Changes the user ownership and/or group ownership of files and directories.",
        "example": "chown -R www-data:www-data /var/www/html",
        "example_explanation": "Recursively assigns the user 'www-data' and group 'www-data' as owners of all files under '/var/www/html'.",
        "category": "File permissions",
        "difficulty": "Intermediate",
        "safety_warning": "Requires superuser (sudo) privileges. Changing ownership of system directories can break OS services.",
        "options": [
            {"flag": "-R", "desc": "Operate on files and directories recursively."},
            {"flag": "-v", "desc": "Verbose: output diagnostic messages for every file processed."},
            {"flag": "--reference=RFILE", "desc": "Use RFILE's owner and group rather than specifying OWNER:GROUP values."}
        ],
        "use_cases": ["Granting web server access to uploaded files", "Fixing permission denied errors after copying files as root"],
        "related_commands": ["chgrp", "chmod", "groups", "id"],
        "beginner_notes": "Only root (sudo) can give away ownership of a file to another user."
    },
    "chgrp": {
        "name": "chgrp",
        "meaning": "Change Group Ownership",
        "syntax": "chgrp [options] group file...",
        "purpose": "Changes the group ownership of specified files or directories.",
        "example": "chgrp developers project.py",
        "example_explanation": "Assigns the 'developers' group as the group owner of 'project.py'.",
        "category": "File permissions",
        "difficulty": "Intermediate",
        "safety_warning": "User must belong to the target group or have sudo rights to change group ownership.",
        "options": [
            {"flag": "-R", "desc": "Operate recursively on directories and their contents."},
            {"flag": "-v", "desc": "Output a diagnostic message for every file processed."}
        ],
        "use_cases": ["Enabling shared collaboration for members of a team group", "Configuring web group permissions"],
        "related_commands": ["chown", "groups", "id"],
        "beginner_notes": "'chown :groupname file' can also be used as a convenient shorthand for chgrp."
    },
    "umask": {
        "name": "umask",
        "meaning": "User File Creation Mask",
        "syntax": "umask [options] [mask]",
        "purpose": "Sets or displays default permission mask for newly created files and directories.",
        "example": "umask 022",
        "example_explanation": "Sets default mask where new files are created with 644 (rw-r--r--) and directories with 755 (rwxr-xr-x).",
        "category": "File permissions",
        "difficulty": "Advanced",
        "safety_warning": "",
        "options": [
            {"flag": "-S", "desc": "Print mask in human-readable symbolic form (e.g., u=rwx,g=rx,o=rx)."},
            {"flag": "-p", "desc": "Output in form that can be reused as input."}
        ],
        "use_cases": ["Securing default file permissions in automated scripts", "Checking current session creation mask"],
        "related_commands": ["chmod", "touch", "mkdir"],
        "beginner_notes": "Umask subtracts permissions from 777 (directories) or 666 (files)."
    },

    # ------------------------------------------------------------------------
    # 3. TEXT PROCESSING
    # ------------------------------------------------------------------------
    "grep": {
        "name": "grep",
        "meaning": "Global Regular Expression Print",
        "syntax": "grep [options] 'pattern' [filename]",
        "purpose": "Searches for specified text patterns or regular expressions inside files or standard input.",
        "example": "grep \"error\" server.log",
        "example_explanation": "Scans the file 'server.log' and displays every single line that contains the word 'error'.",
        "category": "Text processing",
        "difficulty": "Beginner",
        "safety_warning": "",
        "options": [
            {"flag": "-i", "desc": "Ignore case distinctions in patterns and input data."},
            {"flag": "-r / -R", "desc": "Read all files under each directory recursively."},
            {"flag": "-n", "desc": "Prefix each line of output with its 1-based line number."},
            {"flag": "-v", "desc": "Invert match: select non-matching lines."},
            {"flag": "-c", "desc": "Suppress normal output; print count of matching lines instead."}
        ],
        "use_cases": ["Searching log files for errors or warnings", "Piping command outputs: 'ps aux | grep nginx'"],
        "related_commands": ["awk", "sed", "find", "ripgrep"],
        "beginner_notes": "Use 'grep -rn \"pattern\" .' to search all files in the current directory and display line numbers."
    },
    "cat": {
        "name": "cat",
        "meaning": "Concatenate and Display",
        "syntax": "cat [options] [file...]",
        "purpose": "Reads files sequentially and writes their contents to standard output.",
        "example": "cat main.py",
        "example_explanation": "Prints the entire contents of 'main.py' directly onto the terminal screen.",
        "category": "Text processing",
        "difficulty": "Beginner",
        "safety_warning": "",
        "options": [
            {"flag": "-n", "desc": "Number all output lines starting from 1."},
            {"flag": "-b", "desc": "Number only non-empty output lines."},
            {"flag": "-E", "desc": "Display a $ at the end of each line."}
        ],
        "use_cases": ["Viewing short scripts or configs", "Concatenating two files: 'cat a.txt b.txt > full.txt'"],
        "related_commands": ["less", "more", "head", "tail"],
        "beginner_notes": "For long files, prefer 'less' or 'head' so the text doesn't flood your terminal screen."
    },
    "head": {
        "name": "head",
        "meaning": "Output First Part of Files",
        "syntax": "head [options] [file...]",
        "purpose": "Prints the first 10 lines (or specified number of lines) of one or more text files.",
        "example": "head -n 20 data.csv",
        "example_explanation": "Displays the first 20 lines of 'data.csv' including header columns.",
        "category": "Text processing",
        "difficulty": "Beginner",
        "safety_warning": "",
        "options": [
            {"flag": "-n count", "desc": "Print first count lines instead of default 10."},
            {"flag": "-c bytes", "desc": "Print first specified number of bytes."}
        ],
        "use_cases": ["Previewing headers of CSV or data files", "Checking initial lines of server logs"],
        "related_commands": ["tail", "cat", "sed"],
        "beginner_notes": "Combine with 'tail' to extract specific line ranges."
    },
    "tail": {
        "name": "tail",
        "meaning": "Output Last Part of Files",
        "syntax": "tail [options] [file...]",
        "purpose": "Prints the last 10 lines of files, and can stream new lines as they are appended in real-time.",
        "example": "tail -f /var/log/syslog",
        "example_explanation": "Continuously streams new messages appended to '/var/log/syslog' in real-time until you press Ctrl+C.",
        "category": "Text processing",
        "difficulty": "Beginner",
        "safety_warning": "",
        "options": [
            {"flag": "-f", "desc": "Follow: output appended data as the file grows in real time."},
            {"flag": "-n count", "desc": "Output the last specified number of lines."},
            {"flag": "-F", "desc": "Follow by name and keep trying if file is rotated or recreated."}
        ],
        "use_cases": ["Monitoring application logs in real-time during debugging", "Checking last errors written to log"],
        "related_commands": ["head", "less", "journalctl"],
        "beginner_notes": "'tail -f' is one of the most frequently used commands by DevOps engineers for monitoring live systems."
    },
    "sed": {
        "name": "sed",
        "meaning": "Stream Editor",
        "syntax": "sed [options] 'script' [input-file]",
        "purpose": "Performs basic text transformations on an input stream or file (find and replace, insertions, deletions).",
        "example": "sed 's/localhost/127.0.0.1/g' config.txt",
        "example_explanation": "Replaces all occurrences of 'localhost' with '127.0.0.1' in 'config.txt' and outputs the result.",
        "category": "Text processing",
        "difficulty": "Intermediate",
        "safety_warning": "The '-i' flag edits files in-place! Always backup or test without '-i' first before modifying files.",
        "options": [
            {"flag": "-i", "desc": "Edit files in-place (directly modifies target file)."},
            {"flag": "-n", "desc": "Suppress automatic printing of pattern space."},
            {"flag": "-e", "desc": "Add the script to the commands to be executed."}
        ],
        "use_cases": ["Automated configuration file replacement", "Batch string replacements across codebases"],
        "related_commands": ["awk", "grep", "tr"],
        "beginner_notes": "Syntax formula: 's/find/replace/g' means Substitute 'find' with 'replace' Globally on all lines."
    },
    "awk": {
        "name": "awk",
        "meaning": "Aho, Weinberger, and Kernighan (Pattern Scanning & Processing)",
        "syntax": "awk 'pattern { action }' [file]",
        "purpose": "A powerful programming language designed for pattern scanning and columnar data extraction.",
        "example": "awk '{print $1, $3}' data.txt",
        "example_explanation": "Extracts and prints the 1st and 3rd whitespace-separated columns of each row from 'data.txt'.",
        "category": "Text processing",
        "difficulty": "Advanced",
        "safety_warning": "",
        "options": [
            {"flag": "-F fs", "desc": "Set the input field separator (e.g., -F',' for CSV files)."},
            {"flag": "-v var=val", "desc": "Assign a variable value before running the script."},
            {"flag": "-f file", "desc": "Read the awk script from a file instead of the command line."}
        ],
        "use_cases": ["Extracting specific columns from tabular command outputs", "Summing numeric fields in logs"],
        "related_commands": ["sed", "cut", "grep", "sort"],
        "beginner_notes": "$0 represents the whole line, while $1, $2, $3 represent individual columns."
    },
    "sort": {
        "name": "sort",
        "meaning": "Sort Lines of Text Files",
        "syntax": "sort [options] [file...]",
        "purpose": "Sorts lines of text files alphabetically or numerically.",
        "example": "sort -n scores.txt",
        "example_explanation": "Sorts the lines in 'scores.txt' according to numeric value in ascending order.",
        "category": "Text processing",
        "difficulty": "Beginner",
        "safety_warning": "",
        "options": [
            {"flag": "-n", "desc": "Compare according to string numerical value."},
            {"flag": "-r", "desc": "Reverse the result of comparisons (descending order)."},
            {"flag": "-u", "desc": "Output only the first of an equal run (unique lines)."},
            {"flag": "-k pos", "desc": "Sort via a key specified by column position."}
        ],
        "use_cases": ["Sorting usernames or IP addresses", "Organizing log metrics before feeding into uniq"],
        "related_commands": ["uniq", "wc", "awk"],
        "beginner_notes": "Always pair 'sort' before 'uniq', because 'uniq' only detects adjacent repeated lines."
    },
    "uniq": {
        "name": "uniq",
        "meaning": "Report or Omit Repeated Lines",
        "syntax": "uniq [options] [input [output]]",
        "purpose": "Filters adjacent matching lines from input, displaying unique lines or frequency counts.",
        "example": "sort ips.txt | uniq -c",
        "example_explanation": "Sorts the IP address list, then groups identical entries and prints the occurrence count next to each IP.",
        "category": "Text processing",
        "difficulty": "Beginner",
        "safety_warning": "",
        "options": [
            {"flag": "-c", "desc": "Prefix lines by the number of occurrences."},
            {"flag": "-d", "desc": "Only print duplicate lines (lines that appear more than once)."},
            {"flag": "-u", "desc": "Only print unique lines (lines that appear exactly once)."}
        ],
        "use_cases": ["Finding top visiting IP addresses in web logs", "Deduplicating lists of entries"],
        "related_commands": ["sort", "wc", "grep"],
        "beginner_notes": "Uniq only filters adjacent lines; you MUST sort the text first with 'sort'!"
    },
    "wc": {
        "name": "wc",
        "meaning": "Word Count",
        "syntax": "wc [options] [file...]",
        "purpose": "Prints newline, word, and byte counts for each file.",
        "example": "wc -l server.log",
        "example_explanation": "Counts and prints the total number of lines in 'server.log'.",
        "category": "Text processing",
        "difficulty": "Beginner",
        "safety_warning": "",
        "options": [
            {"flag": "-l", "desc": "Print the newline (line) counts only."},
            {"flag": "-w", "desc": "Print the word counts only."},
            {"flag": "-c", "desc": "Print the byte counts only."}
        ],
        "use_cases": ["Counting total entries or lines in logs", "Checking how many matches were produced by grep"],
        "related_commands": ["grep", "cat", "sort"],
        "beginner_notes": "Piping grep to wc -l ('grep error app.log | wc -l') gives you the exact count of errors."
    },
    "diff": {
        "name": "diff",
        "meaning": "Compare Files Line by Line",
        "syntax": "diff [options] file1 file2",
        "purpose": "Compares files line by line and displays the differences between them.",
        "example": "diff -u file_v1.py file_v2.py",
        "example_explanation": "Outputs differences between version 1 and 2 in unified format (with '+' for added lines and '-' for removed lines).",
        "category": "Text processing",
        "difficulty": "Intermediate",
        "safety_warning": "",
        "options": [
            {"flag": "-u", "desc": "Output three lines of unified context."},
            {"flag": "-y", "desc": "Output in two columns side-by-side."},
            {"flag": "-i", "desc": "Ignore case differences in file contents."}
        ],
        "use_cases": ["Reviewing changes between code versions", "Verifying backup configuration modifications"],
        "related_commands": ["patch", "cmp", "git"],
        "beginner_notes": "Unified diffs ('-u') are the foundation of Git commit diffs and patch files."
    },

    # ------------------------------------------------------------------------
    # 4. PROCESSES AND SYSTEM MONITORING
    # ------------------------------------------------------------------------
    "ps": {
        "name": "ps",
        "meaning": "Process Status",
        "syntax": "ps [options]",
        "purpose": "Provides a snapshot of currently running processes on the system.",
        "example": "ps aux",
        "example_explanation": "Displays every active process running on the system along with user, CPU %, and memory % usage.",
        "category": "Processes and system monitoring",
        "difficulty": "Beginner",
        "safety_warning": "",
        "options": [
            {"flag": "aux", "desc": "BSD syntax: show processes for all users (a), with process owner (u), including processes without a tty (x)."},
            {"flag": "-ef", "desc": "Standard UNIX syntax: show every process (-e) in full-format listing (-f)."}
        ],
        "use_cases": ["Finding the Process ID (PID) of an application", "Detecting resource-heavy processes"],
        "related_commands": ["top", "htop", "pgrep", "kill"],
        "beginner_notes": "Usually piped to grep: 'ps aux | grep python' to find running Python scripts."
    },
    "top": {
        "name": "top",
        "meaning": "Display Linux Processes",
        "syntax": "top [options]",
        "purpose": "Provides an interactive, real-time dynamic view of running system processes, CPU, and memory loads.",
        "example": "top",
        "example_explanation": "Opens a live dashboard showing system load, task states, CPU percentages, and top resource-consuming processes.",
        "category": "Processes and system monitoring",
        "difficulty": "Beginner",
        "safety_warning": "",
        "options": [
            {"flag": "-d delay", "desc": "Specifies the delay between screen updates in seconds."},
            {"flag": "-u user", "desc": "Monitor only processes owned by the given user."}
        ],
        "use_cases": ["Monitoring system responsiveness and load average", "Identifying memory leaks and runaway processes"],
        "related_commands": ["htop", "ps", "uptime", "vmstat"],
        "beginner_notes": "Press 'q' to exit top, 'M' to sort by Memory, and 'P' to sort by CPU usage."
    },
    "htop": {
        "name": "htop",
        "meaning": "Interactive Process Viewer",
        "syntax": "htop [options]",
        "purpose": "An enhanced, user-friendly, colored terminal interactive process viewer with mouse support.",
        "example": "htop",
        "example_explanation": "Launches a colored interactive monitor showing per-core CPU meters, RAM bar graphs, and an interactive process list.",
        "category": "Processes and system monitoring",
        "difficulty": "Beginner",
        "safety_warning": "",
        "options": [
            {"flag": "-u user", "desc": "Show only processes of a specified user."},
            {"flag": "-d delay", "desc": "Update interval in tenths of a second."}
        ],
        "use_cases": ["Real-time visual monitoring of server health", "Easily killing processes with F9 without looking up PIDs"],
        "related_commands": ["top", "glances", "ps"],
        "beginner_notes": "Much easier for beginners than 'top'; you can scroll horizontally and use function keys F1-F10."
    },
    "kill": {
        "name": "kill",
        "meaning": "Send Signals to Terminate Processes",
        "syntax": "kill [options] <pid>...",
        "purpose": "Sends a specified signal (such as termination or kill) to one or more processes specified by Process ID (PID).",
        "example": "kill -9 1234",
        "example_explanation": "Sends SIGKILL (signal 9) to forcibly stop the process with PID 1234 immediately.",
        "category": "Processes and system monitoring",
        "difficulty": "Intermediate",
        "safety_warning": "Using signal -9 (SIGKILL) forces immediate termination without allowing the program to save data or close network connections cleanly.",
        "options": [
            {"flag": "-15 (SIGTERM)", "desc": "Graceful termination request; allows process to save state and exit cleanly (default)."},
            {"flag": "-9 (SIGKILL)", "desc": "Forced kill; immediately destroys process at kernel level."},
            {"flag": "-l", "desc": "List all available signal names and numbers."}
        ],
        "use_cases": ["Closing unresponsive or frozen background programs", "Gracefully terminating web servers"],
        "related_commands": ["killall", "pkill", "ps", "top"],
        "beginner_notes": "Always try plain 'kill <pid>' (SIGTERM) first; only use 'kill -9' if the process refuses to exit."
    },
    "killall": {
        "name": "killall",
        "meaning": "Kill Processes by Name",
        "syntax": "killall [options] name...",
        "purpose": "Kills all processes matching a given name rather than targeting a specific PID.",
        "example": "killall firefox",
        "example_explanation": "Terminates every running instance and child process of 'firefox'.",
        "category": "Processes and system monitoring",
        "difficulty": "Intermediate",
        "safety_warning": "Be careful: affects ALL processes matching the name, which could include background workers.",
        "options": [
            {"flag": "-i", "desc": "Interactive: ask for confirmation before killing each process."},
            {"flag": "-9", "desc": "Send SIGKILL for forceful immediate termination."},
            {"flag": "-u user", "desc": "Kill only processes owned by the specified user."}
        ],
        "use_cases": ["Closing all tabs/instances of a crashing desktop app", "Terminating batch workers"],
        "related_commands": ["pkill", "kill", "pgrep"],
        "beginner_notes": "Useful when multiple instances of a script or process are running simultaneously."
    },
    "nice": {
        "name": "nice",
        "meaning": "Run Command with Modified Scheduling Priority",
        "syntax": "nice [options] [command [arg...]]",
        "purpose": "Launches a process with an altered scheduling priority (niceness) so it consumes less or more CPU.",
        "example": "nice -n 10 python heavy_job.py",
        "example_explanation": "Runs 'heavy_job.py' with a niceness of 10, giving other programs higher priority on the CPU.",
        "category": "Processes and system monitoring",
        "difficulty": "Advanced",
        "safety_warning": "Negative nice values (higher priority) require superuser privileges.",
        "options": [
            {"flag": "-n adjustment", "desc": "Integer priority value from -20 (highest priority) to 19 (lowest priority)."}
        ],
        "use_cases": ["Running long backups or video encodes in the background without slowing down the desktop", "Scientific computations"],
        "related_commands": ["renice", "top", "ps"],
        "beginner_notes": "High niceness number = 'nice' to other programs (lets them use the CPU first)."
    },
    "pgrep": {
        "name": "pgrep",
        "meaning": "Process Grep",
        "syntax": "pgrep [options] pattern",
        "purpose": "Looks through the currently running processes and lists the Process IDs (PIDs) that match the selection criteria.",
        "example": "pgrep -l nginx",
        "example_explanation": "Finds all active processes with 'nginx' in their name and displays their PIDs and process names.",
        "category": "Processes and system monitoring",
        "difficulty": "Intermediate",
        "safety_warning": "",
        "options": [
            {"flag": "-l", "desc": "List the process name as well as the process ID."},
            {"flag": "-u user", "desc": "Only match processes belonging to the specified effective user."},
            {"flag": "-a", "desc": "List the full command line used to launch the process."}
        ],
        "use_cases": ["Quickly finding the PID of a service to kill it", "Verifying whether a daemon process is currently running"],
        "related_commands": ["pkill", "pidof", "ps"],
        "beginner_notes": "Combines 'ps aux' and 'grep' into one clean, specialized utility."
    },

    # ------------------------------------------------------------------------
    # 5. NETWORKING
    # ------------------------------------------------------------------------
    "ping": {
        "name": "ping",
        "meaning": "Packet Inter-Network Groper",
        "syntax": "ping [options] destination",
        "purpose": "Sends ICMP ECHO_REQUEST packets to network hosts to test connectivity and measure round-trip latency.",
        "example": "ping -c 4 google.com",
        "example_explanation": "Sends 4 test packets to google.com, measures round-trip response time, and prints statistics.",
        "category": "Networking",
        "difficulty": "Beginner",
        "safety_warning": "",
        "options": [
            {"flag": "-c count", "desc": "Stop after sending count ECHO_REQUEST packets (default on Linux sends packets indefinitely)."},
            {"flag": "-i interval", "desc": "Wait specified interval seconds between sending each packet."},
            {"flag": "-W timeout", "desc": "Time to wait for a response in seconds."}
        ],
        "use_cases": ["Verifying internet or local router connectivity", "Checking DNS resolution and packet loss"],
        "related_commands": ["traceroute", "curl", "ip"],
        "beginner_notes": "On Linux, ping runs forever until you press Ctrl+C or supply the '-c' flag."
    },
    "curl": {
        "name": "curl",
        "meaning": "Client URL",
        "syntax": "curl [options] [URL...]",
        "purpose": "A versatile tool to transfer data to or from a network server using protocols like HTTP, HTTPS, and FTP.",
        "example": "curl -I https://example.com",
        "example_explanation": "Fetches only the HTTP response headers from 'example.com' without downloading the body.",
        "category": "Networking",
        "difficulty": "Intermediate",
        "safety_warning": "Be careful when piping curl commands directly to bash ('curl ... | bash'); inspect scripts first!",
        "options": [
            {"flag": "-I / --head", "desc": "Fetch the HTTP response headers only."},
            {"flag": "-O", "desc": "Write output to a local file named like the remote file."},
            {"flag": "-L", "desc": "Follow HTTP redirects (301, 302)."},
            {"flag": "-X METHOD", "desc": "Specify request method (GET, POST, PUT, DELETE)."},
            {"flag": "-d data", "desc": "Sends the specified data in a POST request."}
        ],
        "use_cases": ["Testing REST APIs from the terminal", "Downloading files and web pages", "Verifying SSL certificates"],
        "related_commands": ["wget", "httpie", "ssh"],
        "beginner_notes": "Use 'curl -s' (silent) to suppress the progress meter when parsing output in scripts."
    },
    "wget": {
        "name": "wget",
        "meaning": "World Wide Web Get",
        "syntax": "wget [options] [URL...]",
        "purpose": "Non-interactive network downloader that retrieves files from the web over HTTP, HTTPS, and FTP.",
        "example": "wget https://example.com/installer.tar.gz",
        "example_explanation": "Downloads 'installer.tar.gz' directly to your current working directory with a progress bar.",
        "category": "Networking",
        "difficulty": "Beginner",
        "safety_warning": "",
        "options": [
            {"flag": "-c", "desc": "Continue: resume getting a partially downloaded file."},
            {"flag": "-O file", "desc": "Write documents to file instead of original remote filename."},
            {"flag": "-b", "desc": "Go to background immediately after startup."}
        ],
        "use_cases": ["Downloading ISO images and datasets", "Resuming interrupted downloads with -c"],
        "related_commands": ["curl", "scp", "rsync"],
        "beginner_notes": "Best suited for downloading complete large files in the background."
    },
    "netstat": {
        "name": "netstat",
        "meaning": "Network Statistics",
        "syntax": "netstat [options]",
        "purpose": "Prints network connections, routing tables, interface statistics, masquerade connections, and multicast memberships.",
        "example": "netstat -tuln",
        "example_explanation": "Lists all active listening TCP (-t) and UDP (-u) sockets numerically (-n) without resolving hostnames.",
        "category": "Networking",
        "difficulty": "Intermediate",
        "safety_warning": "",
        "options": [
            {"flag": "-t", "desc": "Display TCP sockets."},
            {"flag": "-u", "desc": "Display UDP sockets."},
            {"flag": "-l", "desc": "Show only listening sockets."},
            {"flag": "-n", "desc": "Show numerical addresses instead of resolving hostnames."},
            {"flag": "-p", "desc": "Show PID and name of program to which each socket belongs (requires sudo)."}
        ],
        "use_cases": ["Finding which port an application is listening on", "Troubleshooting port conflicts"],
        "related_commands": ["ss", "ip", "lsof"],
        "beginner_notes": "On modern Linux systems, 'ss' is the faster successor, but netstat remains widely used."
    },
    "ssh": {
        "name": "ssh",
        "meaning": "Secure Shell",
        "syntax": "ssh [options] [user@]hostname",
        "purpose": "Logs into a remote machine and provides an encrypted terminal session for executing commands remotely.",
        "example": "ssh student@192.168.1.50",
        "example_explanation": "Opens a secure encrypted terminal session on the remote host 192.168.1.50 as the user 'student'.",
        "category": "Networking",
        "difficulty": "Intermediate",
        "safety_warning": "Protect your private SSH keys (~/.ssh/id_rsa); never share them or upload them publicly.",
        "options": [
            {"flag": "-p port", "desc": "Port to connect to on the remote host (default is 22)."},
            {"flag": "-i identity_file", "desc": "Selects a file from which the private key for public key authentication is read."},
            {"flag": "-v", "desc": "Verbose mode: debug connection and authentication failures."}
        ],
        "use_cases": ["Managing remote cloud servers (AWS, DigitalOcean, GCP)", "Running automated remote maintenance"],
        "related_commands": ["scp", "ssh-keygen", "sftp"],
        "beginner_notes": "Set up SSH key-based authentication with 'ssh-copy-id' for secure passwordless logins."
    },
    "scp": {
        "name": "scp",
        "meaning": "Secure Copy Protocol",
        "syntax": "scp [options] source destination",
        "purpose": "Securely copies files between hosts on a network over the encrypted SSH protocol.",
        "example": "scp report.pdf user@server:/var/www/uploads/",
        "example_explanation": "Transfers 'report.pdf' from your local computer to '/var/www/uploads/' on 'server' using SSH encryption.",
        "category": "Networking",
        "difficulty": "Intermediate",
        "safety_warning": "Will overwrite destination files without prompt if write permissions exist.",
        "options": [
            {"flag": "-r", "desc": "Recursively copy entire directories."},
            {"flag": "-P port", "desc": "Specifies the port to connect to on the remote host."},
            {"flag": "-i identity_file", "desc": "Selects the private key file for SSH authentication."}
        ],
        "use_cases": ["Deploying code build files to a remote server", "Downloading backup logs from a cloud VM"],
        "related_commands": ["ssh", "rsync", "sftp"],
        "beginner_notes": "Format: [user@]host:/remote/path for remote endpoints."
    },
    "ip": {
        "name": "ip",
        "meaning": "IP (Network Device & Routing Tool)",
        "syntax": "ip [options] object {command}",
        "purpose": "Modern Linux tool to show and manipulate network interfaces, IP addresses, and routing tables.",
        "example": "ip addr show",
        "example_explanation": "Displays all active network interfaces (e.g. eth0, wlan0) and their assigned IP addresses.",
        "category": "Networking",
        "difficulty": "Intermediate",
        "safety_warning": "Altering IP addresses or routes can immediately disconnect your active network connection.",
        "options": [
            {"flag": "addr", "desc": "Protocol (IP or IPv6) address management."},
            {"flag": "route", "desc": "Routing table management (e.g. 'ip route show')."},
            {"flag": "link", "desc": "Network device configuration (e.g. 'ip link set eth0 up')."}
        ],
        "use_cases": ["Finding your current IP address", "Checking gateway router IP", "Troubleshooting network link state"],
        "related_commands": ["ifconfig", "ping", "netstat", "route"],
        "beginner_notes": "Replaces the deprecated 'ifconfig' command on modern Linux distributions."
    },

    # ------------------------------------------------------------------------
    # 6. PACKAGE MANAGEMENT
    # ------------------------------------------------------------------------
    "apt": {
        "name": "apt",
        "meaning": "Advanced Package Tool",
        "syntax": "apt [options] command",
        "purpose": "High-level package manager for Debian and Ubuntu-based Linux distributions to install, update, and remove software.",
        "example": "sudo apt update && sudo apt install nginx",
        "example_explanation": "Updates the local package index cache, then downloads and installs the 'nginx' web server package.",
        "category": "Package management",
        "difficulty": "Beginner",
        "safety_warning": "Requires sudo privileges. Always run 'apt update' before installing packages to ensure dependency versions match.",
        "options": [
            {"flag": "update", "desc": "Download latest package lists from software repositories."},
            {"flag": "upgrade", "desc": "Upgrade all installed packages to their newest versions."},
            {"flag": "install pkg", "desc": "Install specified package and required dependencies."},
            {"flag": "remove pkg", "desc": "Remove specified package while keeping configuration files."}
        ],
        "use_cases": ["Installing development compilers like gcc or python3", "Keeping Ubuntu systems up to date"],
        "related_commands": ["dpkg", "apt-get", "apt-cache"],
        "beginner_notes": "Provides friendly progress bars and unified commands compared to older 'apt-get'."
    },
    "dpkg": {
        "name": "dpkg",
        "meaning": "Debian Package Manager",
        "syntax": "dpkg [options] action [package...]",
        "purpose": "Low-level package manager for Debian that installs, builds, removes, and manages individual .deb files.",
        "example": "sudo dpkg -i package.deb",
        "example_explanation": "Installs the standalone local Debian package file 'package.deb'.",
        "category": "Package management",
        "difficulty": "Intermediate",
        "safety_warning": "Does not automatically fetch missing dependencies from repositories; use 'apt --fix-broken install' if it halts.",
        "options": [
            {"flag": "-i", "desc": "Install the specified .deb package file."},
            {"flag": "-l", "desc": "List all packages matching given pattern installed on the system."},
            {"flag": "-r", "desc": "Remove an installed package."},
            {"flag": "-s", "desc": "Report status of specified package."}
        ],
        "use_cases": ["Installing software downloaded directly from vendor websites (.deb)", "Checking package installation status"],
        "related_commands": ["apt", "rpm"],
        "beginner_notes": "Use 'dpkg -l | grep package' to verify whether a particular program is installed."
    },
    "yum": {
        "name": "yum",
        "meaning": "Yellowdog Updater, Modified",
        "syntax": "yum [options] command [package...]",
        "purpose": "Package manager for RPM-based Linux distributions like CentOS and Red Hat Enterprise Linux (RHEL).",
        "example": "sudo yum install httpd",
        "example_explanation": "Downloads and installs the Apache HTTP server ('httpd') on RHEL/CentOS systems.",
        "category": "Package management",
        "difficulty": "Beginner",
        "safety_warning": "Requires root/sudo privileges.",
        "options": [
            {"flag": "install pkg", "desc": "Install a package and its dependencies."},
            {"flag": "update", "desc": "Update all packages to the latest available versions."},
            {"flag": "remove pkg", "desc": "Remove specified package from system."}
        ],
        "use_cases": ["Managing software packages on enterprise CentOS / RHEL servers"],
        "related_commands": ["dnf", "rpm", "apt"],
        "beginner_notes": "Succeeded by 'dnf' in modern versions of Fedora, RHEL 8+, and Rocky Linux."
    },
    "dnf": {
        "name": "dnf",
        "meaning": "Dandified YUM",
        "syntax": "dnf [options] command [package...]",
        "purpose": "Next-generation package manager for RPM-based distributions (Fedora, RHEL 8+, Rocky Linux) replacing YUM.",
        "example": "sudo dnf upgrade",
        "example_explanation": "Calculates dependencies and upgrades all installed packages on the system to their newest versions.",
        "category": "Package management",
        "difficulty": "Beginner",
        "safety_warning": "Requires root/sudo privileges.",
        "options": [
            {"flag": "check-update", "desc": "Check for available package updates without installing."},
            {"flag": "install pkg", "desc": "Install a new package with automatic dependency resolution."},
            {"flag": "autoremove", "desc": "Remove unneeded dependency packages left behind."}
        ],
        "use_cases": ["Modern package management on Fedora and Rocky Linux", "Faster dependency resolution"],
        "related_commands": ["yum", "rpm"],
        "beginner_notes": "Has the same command syntax as yum, but is significantly faster and uses less memory."
    },
    "pacman": {
        "name": "pacman",
        "meaning": "Package Manager (Arch Linux)",
        "syntax": "pacman [options] [targets]",
        "purpose": "The default package manager for Arch Linux and derived distributions (Manjaro, EndeavourOS).",
        "example": "sudo pacman -Syu",
        "example_explanation": "Synchronizes repository databases (-y) and updates all out-of-date packages (-u) on Arch Linux.",
        "category": "Package management",
        "difficulty": "Intermediate",
        "safety_warning": "Requires sudo privileges. Do not interrupt pacman during a rolling upgrade.",
        "options": [
            {"flag": "-Syu", "desc": "Synchronize package databases and perform a complete system upgrade."},
            {"flag": "-S pkg", "desc": "Install a specific package from official repositories."},
            {"flag": "-R pkg", "desc": "Remove a specific package."},
            {"flag": "-Ss string", "desc": "Search for packages matching a string."}
        ],
        "use_cases": ["Managing packages on Arch Linux and Manjaro", "Installing rolling release software"],
        "related_commands": ["apt", "dnf", "yay"],
        "beginner_notes": "The famous '-Syu' is the standard way to update an entire Arch Linux installation."
    },

    # ------------------------------------------------------------------------
    # 7. STORAGE AND DISK USAGE
    # ------------------------------------------------------------------------
    "df": {
        "name": "df",
        "meaning": "Disk Free",
        "syntax": "df [options] [file...]",
        "purpose": "Reports file system disk space usage and free capacity for all mounted partitions.",
        "example": "df -h",
        "example_explanation": "Displays disk usage for all mounted filesystems in human-readable units (e.g. 50G total, 12G used, 38G available).",
        "category": "Storage and disk usage",
        "difficulty": "Beginner",
        "safety_warning": "",
        "options": [
            {"flag": "-h", "desc": "Human-readable: print sizes in powers of 1024 (e.g., 1023M, 2G)."},
            {"flag": "-T", "desc": "Print file system type (e.g., ext4, xfs, btrfs)."},
            {"flag": "-i", "desc": "List inode information instead of block usage."}
        ],
        "use_cases": ["Checking if the main disk or root partition is running out of space", "Verifying mounted external drives"],
        "related_commands": ["du", "lsblk", "fdisk"],
        "beginner_notes": "Look closely at the 'Use %' on the root mount '/' to prevent server disk-full crashes."
    },
    "du": {
        "name": "du",
        "meaning": "Disk Usage",
        "syntax": "du [options] [path...]",
        "purpose": "Estimates file space usage of directories and files recursively.",
        "example": "du -sh /var/log",
        "example_explanation": "Displays the summary (-s) total disk space consumed by '/var/log' in human-readable (-h) format.",
        "category": "Storage and disk usage",
        "difficulty": "Beginner",
        "safety_warning": "",
        "options": [
            {"flag": "-s", "desc": "Summary: display only a total for each argument."},
            {"flag": "-h", "desc": "Print sizes in human-readable format (e.g., 1K, 234M, 2G)."},
            {"flag": "-d N / --max-depth=N", "desc": "Print total for directory only if it is N or fewer levels below command line argument."}
        ],
        "use_cases": ["Finding which subdirectory is consuming the most disk space", "Checking folder download sizes"],
        "related_commands": ["df", "ncdu", "ls"],
        "beginner_notes": "Use 'du -sh * | sort -h' to sort all subfolders in the current directory by size."
    },
    "fdisk": {
        "name": "fdisk",
        "meaning": "Format Disk / Partition Table Manipulator",
        "syntax": "fdisk [options] device",
        "purpose": "A dialogue-driven program for creation and manipulation of partition tables on storage drives.",
        "example": "sudo fdisk -l",
        "example_explanation": "Lists the partition tables for all detected hard drives and SSDs without modifying them.",
        "category": "Storage and disk usage",
        "difficulty": "Advanced",
        "safety_warning": "DANGER: Writing partition changes with fdisk can permanently destroy data on your hard drives. Use with extreme caution.",
        "options": [
            {"flag": "-l", "desc": "List the partition tables for the specified devices and exit."},
            {"flag": "-s partition", "desc": "Display size of partition in blocks."}
        ],
        "use_cases": ["Inspecting drive partition layouts", "Creating new disk partitions for mounting"],
        "related_commands": ["parted", "lsblk", "mkfs"],
        "beginner_notes": "Always use 'fdisk -l' to safely inspect partitions without entering interactive edit mode."
    },
    "mount": {
        "name": "mount",
        "meaning": "Mount Filesystem",
        "syntax": "mount [options] [device] [directory]",
        "purpose": "Attaches a storage device or filesystem to the directory tree, making its files accessible.",
        "example": "sudo mount /dev/sdb1 /mnt/usb",
        "example_explanation": "Attaches the partition '/dev/sdb1' (such as a USB flash drive) into the folder '/mnt/usb'.",
        "category": "Storage and disk usage",
        "difficulty": "Intermediate",
        "safety_warning": "Target directory should be empty; existing files in the mountpoint are hidden while mounted.",
        "options": [
            {"flag": "-t type", "desc": "Indicate filesystem type (ext4, ntfs, vfat, nfs)."},
            {"flag": "-o options", "desc": "Comma-separated mount options (ro, rw, noexec, user)."},
            {"flag": "-a", "desc": "Mount all filesystems mentioned in /etc/fstab."}
        ],
        "use_cases": ["Accessing external USB drives and network shares (NFS)", "Mounting ISO images"],
        "related_commands": ["umount", "lsblk", "df"],
        "beginner_notes": "In Linux, drives do not have drive letters like C: or D:; they attach as directories in the root tree."
    },
    "umount": {
        "name": "umount",
        "meaning": "Unmount Filesystem",
        "syntax": "umount [options] {directory|device}",
        "purpose": "Detaches a mounted file system from the file system hierarchy safely, flushing disk caches.",
        "example": "sudo umount /mnt/usb",
        "example_explanation": "Safely unmounts the device attached at '/mnt/usb' so it can be safely disconnected.",
        "category": "Storage and disk usage",
        "difficulty": "Intermediate",
        "safety_warning": "Fails with 'target is busy' if any terminal, program, or file is open inside that directory.",
        "options": [
            {"flag": "-f", "desc": "Force unmount (in case of an unreachable NFS system)."},
            {"flag": "-l", "desc": "Lazy unmount: detach filesystem now and clean up references when no longer busy."}
        ],
        "use_cases": ["Safely ejecting USB flash drives without data corruption", "Unmounting network storage"],
        "related_commands": ["mount", "eject", "lsof"],
        "beginner_notes": "Notice the spelling is 'umount' (no 'n'). If busy, change out of the directory with 'cd ~' first."
    },
    "lsblk": {
        "name": "lsblk",
        "meaning": "List Block Devices",
        "syntax": "lsblk [options] [device...]",
        "purpose": "Lists information about all available or specified block devices in a visual tree format.",
        "example": "lsblk -f",
        "example_explanation": "Outputs all block devices (disks, partitions, LVM) along with filesystem types, labels, and mountpoints.",
        "category": "Storage and disk usage",
        "difficulty": "Beginner",
        "safety_warning": "",
        "options": [
            {"flag": "-f", "desc": "Output filesystem information: NAME, FSTYPE, FSVER, LABEL, UUID, and MOUNTPOINT."},
            {"flag": "-a", "desc": "List all devices including empty devices."},
            {"flag": "-m", "desc": "Output device permissions, owner, and group."}
        ],
        "use_cases": ["Identifying device names (sda, sdb) before formatting or mounting", "Verifying USB detection"],
        "related_commands": ["df", "fdisk", "blkid"],
        "beginner_notes": "Does not require sudo, making it the safest and quickest way to inspect storage layout."
    },

    # ------------------------------------------------------------------------
    # 8. SYSTEM SERVICES
    # ------------------------------------------------------------------------
    "systemctl": {
        "name": "systemctl",
        "meaning": "System Control (systemd Manager)",
        "syntax": "systemctl [command] [service_name]",
        "purpose": "Controls and inspects the state of systemd system services and the init system.",
        "example": "systemctl status nginx",
        "example_explanation": "Displays the current status, active state, process ID, and recent log messages for the 'nginx' web server service without modifying it.",
        "category": "System services",
        "difficulty": "Intermediate",
        "safety_warning": "Stopping or restarting critical services like 'sshd' or 'network' on remote machines can disconnect your session.",
        "options": [
            {"flag": "status <unit>", "desc": "Show runtime status information about a unit."},
            {"flag": "start <unit>", "desc": "Start (activate) one or more units immediately (requires sudo)."},
            {"flag": "stop <unit>", "desc": "Stop (deactivate) one or more units immediately (requires sudo)."},
            {"flag": "restart <unit>", "desc": "Stop and then start one or more units (requires sudo)."},
            {"flag": "enable <unit>", "desc": "Enable one or more units to start automatically at boot time."}
        ],
        "use_cases": ["Checking if a database or web server is running", "Configuring services to start at boot"],
        "related_commands": ["journalctl", "service", "systemd"],
        "beginner_notes": "Viewing service status with 'systemctl status <service>' does NOT require root/sudo privileges."
    },
    "journalctl": {
        "name": "journalctl",
        "meaning": "Query systemd Journal Logs",
        "syntax": "journalctl [options] [matches...]",
        "purpose": "Queries and displays logs generated by the systemd journal service, including kernel and service logs.",
        "example": "journalctl -u nginx -n 50 --no-pager",
        "example_explanation": "Retrieves the last 50 log messages generated specifically by the 'nginx' service without paging.",
        "category": "System services",
        "difficulty": "Intermediate",
        "safety_warning": "",
        "options": [
            {"flag": "-u unit", "desc": "Show logs for the specified systemd service unit."},
            {"flag": "-n count", "desc": "Show the most recent specified number of journal events."},
            {"flag": "-f", "desc": "Follow: continuously output live incoming log entries (like tail -f)."},
            {"flag": "-p err", "desc": "Filter by message priority (emerg, alert, crit, err, warning, notice, info)."},
            {"flag": "-b", "desc": "Show log entries recorded since the current system boot only."}
        ],
        "use_cases": ["Debugging why a service failed to start", "Inspecting system boot errors"],
        "related_commands": ["systemctl", "tail", "dmesg"],
        "beginner_notes": "Use 'journalctl -xe' to jump straight to the end of the log with explanatory context after a service error."
    },
    "cron": {
        "name": "cron",
        "meaning": "Time-Based Job Scheduler Daemon",
        "syntax": "crontab [options]",
        "purpose": "Schedules and executes periodic shell scripts or commands automatically at specified intervals and times.",
        "example": "crontab -l",
        "example_explanation": "Lists all scheduled cron automation jobs configured for the current user.",
        "category": "System services",
        "difficulty": "Intermediate",
        "safety_warning": "Be careful with 'crontab -r'; it removes your entire scheduled crontab file without prompting!",
        "options": [
            {"flag": "-e", "desc": "Edit current user's crontab using the default text editor."},
            {"flag": "-l", "desc": "List the current user's crontab entries."},
            {"flag": "-u user", "desc": "Specify which user's crontab is to be examined or edited (requires sudo)."}
        ],
        "use_cases": ["Scheduling automated nightly backups at 2 AM", "Running cleanup maintenance scripts weekly"],
        "related_commands": ["systemctl", "at", "sleep"],
        "beginner_notes": "Five-star schedule format: 'minute hour day-of-month month day-of-week command'."
    }
}

# The 8 core commands specifically tested for beginner guidance
DEFAULT_SUGGESTIONS = ["ls", "pwd", "mkdir", "cp", "mv", "grep", "chmod", "systemctl"]

# All valid categories in the knowledge base
CATEGORIES = [
    "Files and directories",
    "File permissions",
    "Text processing",
    "Processes and system monitoring",
    "Networking",
    "Package management",
    "Storage and disk usage",
    "System services"
]

# ============================================================================
# COMPREHENSIVE COMMAND ENRICHMENT: Illustrative Outputs & Troubleshooting
# Fulfills Module 2: Illustrative sample output, common mistakes & lessons
# ============================================================================
COMMAND_DETAILS_EXTRA = {
    # 1. Files and directories
    "ls": {
        "expected_output": "total 24\ndrwxr-xr-x 3 student student 4096 Oct 25 10:00 .\ndrwxr-xr-x 5 student student 4096 Oct 25 09:30 ..\n-rw-r--r-- 1 student student  220 Oct 25 09:30 .bashrc\n-rw-r--r-- 1 student student 1024 Oct 25 10:00 notes.txt\ndrwxr-xr-x 2 student student 4096 Oct 25 09:45 practice",
        "common_mistakes": "Forgetting the '-a' flag when attempting to inspect hidden dotfiles (e.g. .bashrc, .env).",
        "recommended_lesson": "Lesson 1: Terminal Orientation & Path Navigation"
    },
    "pwd": {
        "expected_output": "/home/student/projects/linux-lab",
        "common_mistakes": "Confusing 'pwd' with changing directories; pwd only reports your current position in the filesystem.",
        "recommended_lesson": "Lesson 1: Terminal Orientation & Path Navigation"
    },
    "mkdir": {
        "expected_output": "(Directory 'practice' created successfully in the current working directory)",
        "common_mistakes": "Trying to create nested directory trees without passing '-p' (e.g. 'mkdir a/b/c' fails if 'a' or 'b' do not exist).",
        "recommended_lesson": "Lesson 2: Creating, Moving, and Renaming Files"
    },
    "cp": {
        "expected_output": "(Exact duplicate created at destination path)",
        "common_mistakes": "Omitting the '-r' flag when copying an entire folder hierarchy; cp will refuse to copy directories without recursive mode.",
        "recommended_lesson": "Lesson 2: Creating, Moving, and Renaming Files"
    },
    "mv": {
        "expected_output": "(File moved/renamed to destination location)",
        "common_mistakes": "Accidentally overwriting an existing destination file without confirmation; use 'mv -i' for safe prompt confirmation.",
        "recommended_lesson": "Lesson 2: Creating, Moving, and Renaming Files"
    },
    "rm": {
        "expected_output": "(File unlinked and permanently deleted)",
        "common_mistakes": "Assuming Linux has a desktop Recycle Bin; deleted files with 'rm' cannot be recovered from a trash can.",
        "recommended_lesson": "Lesson 4: Safe Removal & Space Exploration"
    },
    "cd": {
        "expected_output": "(Working directory updated silently; prompt changes to new directory)",
        "common_mistakes": "Confusing relative path 'cd folder' with absolute path 'cd /folder' (which targets the root filesystem).",
        "recommended_lesson": "Lesson 1: Terminal Orientation & Path Navigation"
    },
    "touch": {
        "expected_output": "(Empty file created or existing timestamp updated)",
        "common_mistakes": "Expecting touch to launch an editor; touch only creates an empty file or updates access/modification timestamps.",
        "recommended_lesson": "Lesson 2: Creating, Moving, and Renaming Files"
    },
    "find": {
        "expected_output": "./docs/report.pdf\n./archive/2026/annual_report.pdf",
        "common_mistakes": "Not enclosing wildcards in quotes (e.g. 'find . -name *.log' causes premature shell expansion errors; use 'find . -name \"*.log\"').",
        "recommended_lesson": "Lesson 7: Searching and Pattern Filtering with Grep"
    },
    "ln": {
        "expected_output": "(Symbolic link created: shortcut.log -> /var/log/app.log)",
        "common_mistakes": "Reversing arguments; syntax is 'ln -s <existing_target> <new_shortcut_name>'.",
        "recommended_lesson": "Lesson 5: Visualizing Trees and Creating Soft Links"
    },
    "tree": {
        "expected_output": ".\n├── assets\n│   └── logo.png\n├── package.json\n└── src\n    └── index.js\n2 directories, 3 files",
        "common_mistakes": "Running tree in deeply nested roots like '/' without limiting depth using '-L 2'.",
        "recommended_lesson": "Lesson 5: Visualizing Trees and Creating Soft Links"
    },

    # 2. File permissions
    "chmod": {
        "expected_output": "(Permissions updated: -rwxr-xr-x 1 student student script.sh)",
        "common_mistakes": "Using 'chmod 777' as a quick fix; this exposes systems to security risks by giving everyone write and execution permissions.",
        "recommended_lesson": "Lesson 6: Linux Permission Architecture (rwx)"
    },
    "chown": {
        "expected_output": "(Owner updated to 'www-data' for /var/www/html)",
        "common_mistakes": "Attempting chown without 'sudo'; normal users cannot reassign file ownership to other accounts.",
        "recommended_lesson": "Lesson 6: Linux Permission Architecture (rwx)"
    },
    "chgrp": {
        "expected_output": "(Group updated to 'developers' for shared_project/)",
        "common_mistakes": "Specifying a group that does not exist in /etc/group or which you are not a member of.",
        "recommended_lesson": "Lesson 6: Linux Permission Architecture (rwx)"
    },
    "umask": {
        "expected_output": "0022",
        "common_mistakes": "Confusing umask with direct permissions; umask specifies bits to mask out (subtract) from 666 for files or 777 for directories.",
        "recommended_lesson": "Lesson 6: Linux Permission Architecture (rwx)"
    },

    # 3. Text processing
    "grep": {
        "expected_output": "server.log:142: 2026-10-25 10:14:02 [ERROR] Database connection timed out\nserver.log:189: 2026-10-25 10:22:15 [ERROR] Failed to bind port 8080",
        "common_mistakes": "Forgetting the '-i' flag for case-insensitive matching, missing capitalized matches like 'Error' or 'Failed'.",
        "recommended_lesson": "Lesson 7: Searching and Pattern Filtering with Grep"
    },
    "cat": {
        "expected_output": "PORT=5000\nENV=production\nDEBUG=false",
        "common_mistakes": "Running cat on multi-gigabyte log files; this floods your terminal. Use 'less', 'head', or 'tail' instead.",
        "recommended_lesson": "Lesson 3: Inspecting File Contents & Basic Text Viewing"
    },
    "head": {
        "expected_output": "id,name,role,department\n1,Alice,Engineer,Platform\n2,Bob,Analyst,Data\n3,Charlie,Designer,Product",
        "common_mistakes": "Forgetting that default head displays 10 lines; specify '-n <count>' to change the output count.",
        "recommended_lesson": "Lesson 3: Inspecting File Contents & Basic Text Viewing"
    },
    "tail": {
        "expected_output": "10.0.0.1 - - [25/Oct/2026:10:30:00] \"GET /api/stats HTTP/1.1\" 200 482\n10.0.0.2 - - [25/Oct/2026:10:30:02] \"POST /api/command HTTP/1.1\" 200 1204",
        "common_mistakes": "Closing the terminal window to exit 'tail -f' instead of pressing the standard interrupt key 'Ctrl + C'.",
        "recommended_lesson": "Lesson 3: Inspecting File Contents & Basic Text Viewing"
    },
    "sed": {
        "expected_output": "Updated occurrences: 'localhost' changed to '127.0.0.1'",
        "common_mistakes": "Using 'sed -i' without creating a backup copy first; changes directly modify the original file on disk.",
        "recommended_lesson": "Lesson 10: Sorting, Deduplication, and Column Extraction"
    },
    "awk": {
        "expected_output": "root: /bin/bash\ndaemon: /usr/sbin/nologin\nstudent: /bin/bash",
        "common_mistakes": "Forgetting that awk defaults to whitespace delimiters; use '-F:' when parsing colon-separated files like /etc/passwd.",
        "recommended_lesson": "Lesson 10: Sorting, Deduplication, and Column Extraction"
    },
    "sort": {
        "expected_output": "apple\nbanana\ncherry\ndate",
        "common_mistakes": "Sorting numeric columns alphabetically (e.g. 10 appears before 2); use '-n' for numeric sorting.",
        "recommended_lesson": "Lesson 10: Sorting, Deduplication, and Column Extraction"
    },
    "uniq": {
        "expected_output": "   3 ERROR\n   8 INFO\n   1 WARNING",
        "common_mistakes": "Running uniq on unsorted input; uniq only collapses adjacent identical lines, so always sort first ('sort | uniq').",
        "recommended_lesson": "Lesson 10: Sorting, Deduplication, and Column Extraction"
    },
    "wc": {
        "expected_output": " 142  890 6420 access.log",
        "common_mistakes": "Confusing line count with word count; remember '-l' is lines, '-w' is words, and '-c' is bytes.",
        "recommended_lesson": "Lesson 7: Searching and Pattern Filtering with Grep"
    },
    "diff": {
        "expected_output": "--- old_config.py\n+++ new_config.py\n@@ -5,2 +5,2 @@\n-DEBUG = True\n+DEBUG = False",
        "common_mistakes": "Reading default diff output without unified mode; use '-u' for standard patch-style readability.",
        "recommended_lesson": "Lesson 7: Searching and Pattern Filtering with Grep"
    },

    # 4. Processes and system monitoring
    "ps": {
        "expected_output": "USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND\nroot         1  0.0  0.1 168344 11420 ?        Ss   09:00   0:02 /sbin/init\nstudent   1420  0.2  1.4  42100 28900 pts/0    S+   09:30   0:01 python app.py",
        "common_mistakes": "Running plain 'ps' without options, which only displays processes attached to your current terminal session.",
        "recommended_lesson": "Lesson 8: Real-Time Process & Resource Monitoring"
    },
    "top": {
        "expected_output": "top - 10:35:10 up 1:35, 1 user, load average: 0.15, 0.20, 0.18\nTasks: 182 total, 1 running, 181 sleeping\n%Cpu(s): 2.4 us, 1.1 sy, 0.0 ni, 96.2 id, 0.3 wa\nMiB Mem : 7850.2 total, 3420.5 free, 2120.4 used",
        "common_mistakes": "Not knowing how to quit the interactive top view; press the 'q' key to return to prompt.",
        "recommended_lesson": "Lesson 8: Real-Time Process & Resource Monitoring"
    },
    "htop": {
        "expected_output": "[||||||||                28.4%]   Tasks: 75, 120 thr; 1 running\n[||||||                  18.2%]   Load average: 0.24 0.18 0.15\nMem[|||||||||||||||   1.85G/7.67G]   Uptime: 01:45:20",
        "common_mistakes": "Expecting htop to be preinstalled on minimal distributions; it often requires 'sudo apt install htop'.",
        "recommended_lesson": "Lesson 8: Real-Time Process & Resource Monitoring"
    },
    "kill": {
        "expected_output": "(Process 1420 received SIGTERM and terminated gracefully)",
        "common_mistakes": "Using forced kill -9 immediately before attempting graceful termination with standard 'kill <PID>'.",
        "recommended_lesson": "Lesson 9: Terminating Processes & Signal Management"
    },
    "killall": {
        "expected_output": "(All instances of process 'nginx' terminated)",
        "common_mistakes": "Accidentally terminating vital system processes by entering broad process names.",
        "recommended_lesson": "Lesson 9: Terminating Processes & Signal Management"
    },
    "nice": {
        "expected_output": "(Process launched with reduced CPU priority +10)",
        "common_mistakes": "Confusing positive and negative niceness: positive means lower priority (nicer), negative requires root.",
        "recommended_lesson": "Lesson 15: Scheduled Automation & Crontab Jobs"
    },
    "pgrep": {
        "expected_output": "1420\n1421",
        "common_mistakes": "Running pgrep without '-l' and seeing only PID numbers without process names for verification.",
        "recommended_lesson": "Lesson 8: Real-Time Process & Resource Monitoring"
    },

    # 5. Networking
    "ping": {
        "expected_output": "64 bytes from 8.8.8.8: icmp_seq=1 ttl=117 time=14.2 ms\n64 bytes from 8.8.8.8: icmp_seq=2 ttl=117 time=13.8 ms\n--- 8.8.8.8 ping statistics ---\n2 packets transmitted, 2 received, 0% packet loss",
        "common_mistakes": "On Linux, ping runs forever by default; press 'Ctrl + C' to stop or specify packet count with '-c 4'.",
        "recommended_lesson": "Lesson 12: Network Connectivity & Socket Auditing"
    },
    "curl": {
        "expected_output": "HTTP/1.1 200 OK\nContent-Type: application/json\n{\"status\": \"online\", \"service\": \"api-gateway\"}",
        "common_mistakes": "Forgetting the '-L' flag to follow HTTP 301/302 redirects, or omitting '-o' when downloading binary files.",
        "recommended_lesson": "Lesson 12: Network Connectivity & Socket Auditing"
    },
    "wget": {
        "expected_output": "Saving to: 'data.zip'\ndata.zip  100%[===================>]  4.20M  12.4MB/s  in 0.3s\n2026-10-25 10:40:00 (12.4 MB/s) - 'data.zip' saved",
        "common_mistakes": "Not using '-c' to resume interrupted network downloads, having to restart large downloads from zero.",
        "recommended_lesson": "Lesson 12: Network Connectivity & Socket Auditing"
    },
    "netstat": {
        "expected_output": "Proto Recv-Q Send-Q Local Address   Foreign Address   State   PID/Program name\ntcp        0      0 0.0.0.0:80      0.0.0.0:*         LISTEN  1024/nginx: master\ntcp        0      0 127.0.0.1:5000  0.0.0.0:*         LISTEN  1420/python",
        "common_mistakes": "Running netstat without '-n', causing lengthy pauses while it attempts reverse DNS lookups on all IPs.",
        "recommended_lesson": "Lesson 12: Network Connectivity & Socket Auditing"
    },
    "ssh": {
        "expected_output": "Welcome to Ubuntu 24.04 LTS (GNU/Linux 6.8.0-generic x86_64)\nstudent@cloud-host:~$",
        "common_mistakes": "Permissive permissions on private key files; SSH aborts if private keys are accessible by other users ('chmod 600 id_rsa').",
        "recommended_lesson": "Lesson 13: Remote Shell & Encrypted File Transfers"
    },
    "scp": {
        "expected_output": "app.tar.gz  100%   14MB  18.2MB/s   00:00",
        "common_mistakes": "Reversing local and remote arguments or forgetting the colon (':') separator on remote hosts.",
        "recommended_lesson": "Lesson 13: Remote Shell & Encrypted File Transfers"
    },
    "ip": {
        "expected_output": "2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP\n    inet 192.168.1.105/24 brd 192.168.1.255 scope global eth0",
        "common_mistakes": "Using deprecated 'ifconfig'; the modern standard command across all Linux distributions is 'ip addr'.",
        "recommended_lesson": "Lesson 12: Network Connectivity & Socket Auditing"
    },

    # 6. Package management
    "apt": {
        "expected_output": "Reading package lists... Done\nBuilding dependency tree... Done\nThe following NEW packages will be installed: curl\n1 upgraded, 1 newly installed, 0 to remove.",
        "common_mistakes": "Forgetting to run 'sudo apt update' before attempting to install new packages.",
        "recommended_lesson": "Lesson 11: Controlling Background Services with systemd"
    },
    "dpkg": {
        "expected_output": "Selecting previously unselected package.\nPreparing to unpack package.deb ...\nUnpacking package (1.2.0) ...\nSetting up package (1.2.0) ...",
        "common_mistakes": "Expecting dpkg to automatically fetch missing dependencies; use 'sudo apt --fix-broken install' if it halts.",
        "recommended_lesson": "Lesson 11: Controlling Background Services with systemd"
    },
    "yum": {
        "expected_output": "Resolving Dependencies\n--> Running transaction check\n---> Package httpd.x86_64 0:2.4.6-97.el7.centos will be installed\nComplete!",
        "common_mistakes": "Using yum on modern RHEL/Fedora releases where 'dnf' is the official modern successor.",
        "recommended_lesson": "Lesson 11: Controlling Background Services with systemd"
    },
    "dnf": {
        "expected_output": "Dependencies resolved.\nInstalling: nginx  x86_64  1:1.24.0-1.fc39  fedora  580 k\nComplete!",
        "common_mistakes": "Attempting package installations without 'sudo' root elevation.",
        "recommended_lesson": "Lesson 11: Controlling Background Services with systemd"
    },
    "pacman": {
        "expected_output": "resolving dependencies...\nlooking for conflicting packages...\nPackages (1) git-2.44.0-1\nTotal Installed Size: 32.40 MiB\n:: Proceed with installation? [Y/n]",
        "common_mistakes": "Confusing uppercase and lowercase operation flags; pacman uses capital letters for main modes (e.g. -S for sync, -R for remove).",
        "recommended_lesson": "Lesson 11: Controlling Background Services with systemd"
    },

    # 7. Storage and disk usage
    "df": {
        "expected_output": "Filesystem     Type      Size  Used Avail Use% Mounted on\n/dev/sda1      ext4       50G   22G   26G  46% /\ntmpfs          tmpfs     3.9G     0  3.9G   0% /dev/shm",
        "common_mistakes": "Running plain 'df' without '-h', displaying sizes in blocks instead of human-readable gigabytes.",
        "recommended_lesson": "Lesson 4: Safe Removal & Space Exploration"
    },
    "du": {
        "expected_output": "4.2M    ./docs\n180M    ./images\n240M    .",
        "common_mistakes": "Running 'du' without '-s', which spews every single nested subdirectory instead of a summary.",
        "recommended_lesson": "Lesson 4: Safe Removal & Space Exploration"
    },
    "fdisk": {
        "expected_output": "Disk /dev/sda: 500 GiB, 536870912000 bytes, 1048576000 sectors\nDevice     Boot Start        End    Sectors  Size Id Type\n/dev/sda1  *     2048    1050623    1048576  512M  b W95 FAT32\n/dev/sda2     1050624 1048575966 1047525343  499G 83 Linux",
        "common_mistakes": "Committing changes with 'w' before verifying partition boundaries; partition errors lead to immediate data corruption.",
        "recommended_lesson": "Lesson 14: Storage Partitions & Filesystem Mounting"
    },
    "mount": {
        "expected_output": "(Partition /dev/sdb1 successfully mounted at /mnt/data)",
        "common_mistakes": "Mounting to a folder with existing files; this hides preexisting contents until unmounted.",
        "recommended_lesson": "Lesson 14: Storage Partitions & Filesystem Mounting"
    },
    "umount": {
        "expected_output": "(Filesystem detached and disk buffers flushed)",
        "common_mistakes": "Trying to unmount while inside the mount directory ('target is busy'); change directory away first ('cd ~').",
        "recommended_lesson": "Lesson 14: Storage Partitions & Filesystem Mounting"
    },
    "lsblk": {
        "expected_output": "NAME   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS\nsda      8:0    0 465.8G  0 disk \n├─sda1   8:1    0   512M  0 part /boot/efi\n└─sda2   8:2    0 465.3G  0 part /",
        "common_mistakes": "Running without '-f' and missing partition filesystem types (ext4, vfat, xfs) and UUIDs.",
        "recommended_lesson": "Lesson 14: Storage Partitions & Filesystem Mounting"
    },

    # 8. System services
    "systemctl": {
        "expected_output": "● nginx.service - A high performance web server\n     Loaded: loaded (/lib/systemd/system/nginx.service; enabled)\n     Active: active (running) since Fri 2026-10-25 09:15:20; 1h 25min ago\n   Main PID: 1042 (nginx)",
        "common_mistakes": "Confusing 'systemctl start' (temporary until reboot) with 'systemctl enable' (configure to launch at boot).",
        "recommended_lesson": "Lesson 11: Controlling Background Services with systemd"
    },
    "journalctl": {
        "expected_output": "-- Boot b83949e2901a41a49ba383e20194 --\nOct 25 09:15:20 server systemd[1]: Started A high performance web server.\nOct 25 09:30:15 server nginx[1043]: 192.168.1.1 - GET / HTTP/1.1 200",
        "common_mistakes": "Running journalctl without filters on servers with gigabytes of logs; use '-u <service>' or '-b' to filter.",
        "recommended_lesson": "Lesson 11: Controlling Background Services with systemd"
    },
    "cron": {
        "expected_output": "# Active crontab:\n0 2 * * * /home/student/scripts/backup.sh > /dev/null 2>&1",
        "common_mistakes": "Assuming cron jobs run in the user's interactive shell PATH; always use absolute binary paths in cron entries.",
        "recommended_lesson": "Lesson 15: Scheduled Automation & Crontab Jobs"
    }
}

# Apply enrichment cleanly to all 53 knowledge base entries
for cmd_name, extra_data in COMMAND_DETAILS_EXTRA.items():
    if cmd_name in COMMAND_KNOWLEDGE_BASE:
        COMMAND_KNOWLEDGE_BASE[cmd_name].update(extra_data)

# Ensure fallback defaults exist for any command
for cmd_name, data in COMMAND_KNOWLEDGE_BASE.items():
    if "expected_output" not in data:
        data["expected_output"] = f"$ {data['example']}\n[Simulated illustrative output for {data['name']}]"
    if "common_mistakes" not in data:
        data["common_mistakes"] = "Passing invalid syntax or omitting mandatory arguments."
    if "recommended_lesson" not in data:
        data["recommended_lesson"] = "Linux Foundations"

# ============================================================================
# FAQ & SMART COMMAND HELPER (Deterministic Local Educational Helper)
# Fulfills Module 7: Answers natural Linux-learning questions without AI APIs
# ============================================================================
FAQ_KNOWLEDGE_BASE = {
    "permissions": {
        "triggers": ["how to change permissions", "change permission", "chmod help", "file permission", "make executable", "rwx mode"],
        "title": "Changing File Permissions in Linux",
        "answer": "Use 'chmod' to modify read (r=4), write (w=2), and execute (x=1) permissions. For example, 'chmod +x script.sh' makes a shell script runnable, while 'chmod 755 file' gives owner full access and group/others read and execute access.",
        "primary_command": "chmod",
        "recommended_lesson": "Lesson 6: Linux Permission Architecture (rwx)"
    },
    "find_files": {
        "triggers": ["how to find files", "search files", "locate file", "find a file", "search for text in file"],
        "title": "Searching for Files & Text Patterns",
        "answer": "To search for files by name in a directory hierarchy, use 'find . -name \"filename\"'. To search for specific text inside files, use 'grep -rn \"search_term\" .'.",
        "primary_command": "grep",
        "recommended_lesson": "Lesson 7: Searching and Pattern Filtering with Grep"
    },
    "processes": {
        "triggers": ["how to see processes", "view running processes", "check cpu usage", "list processes", "running programs", "check memory"],
        "title": "Inspecting System Processes & Resource Usage",
        "answer": "Run 'ps aux' for a complete snapshot of all running processes, or run 'top' / 'htop' for an interactive real-time dashboard displaying CPU and RAM consumption per process ID (PID).",
        "primary_command": "top",
        "recommended_lesson": "Lesson 8: Real-Time Process & Resource Monitoring"
    },
    "kill_process": {
        "triggers": ["how to kill a process", "stop a process", "kill program", "terminate process", "force quit", "kill -9"],
        "title": "Terminating Running Processes Safely",
        "answer": "First find the process PID with 'ps aux' or 'pgrep <name>'. Then send a graceful termination signal with 'kill <PID>' (SIGTERM 15). If the process is frozen or unresponsive, use forced termination 'kill -9 <PID>' (SIGKILL).",
        "primary_command": "kill",
        "recommended_lesson": "Lesson 9: Terminating Processes & Signal Management"
    },
    "disk_space": {
        "triggers": ["how to check disk space", "disk full", "check storage", "free disk space", "check folder size"],
        "title": "Checking Disk Usage and Free Space",
        "answer": "Use 'df -h' to see total, used, and available space on all mounted filesystems in human-readable units (GB/MB). To find out how much space a specific folder consumes, use 'du -sh <folder>'.",
        "primary_command": "df",
        "recommended_lesson": "Lesson 4: Safe Removal & Space Exploration"
    },
    "services": {
        "triggers": ["how to restart service", "service status", "start service", "stop service", "systemctl status", "manage background service"],
        "title": "Managing System Services with systemd",
        "answer": "Use 'systemctl status <service>' to check if a service like nginx is active. To restart a service, run 'sudo systemctl restart <service>'. To make it start automatically on boot, run 'sudo systemctl enable <service>'.",
        "primary_command": "systemctl",
        "recommended_lesson": "Lesson 11: Controlling Background Services with systemd"
    },
    "sudo_help": {
        "triggers": ["what is sudo", "how to use sudo", "root privileges", "permission denied", "superuser"],
        "title": "Understanding Superuser Privileges (sudo)",
        "answer": "'sudo' (SuperUser DO) executes commands with administrative/root privileges. Use it only when necessary (e.g. installing packages or managing services), and never run untrusted scripts with sudo as it can modify core system files.",
        "primary_command": "chmod",
        "recommended_lesson": "Lesson 6: Linux Permission Architecture (rwx)"
    },
    "pipe_redirection": {
        "triggers": ["what is a pipe", "what is redirection", "pipe operator", "how to pipe", "how to redirect output"],
        "title": "UNIX Pipes (|) and Stream Redirection (>, >>)",
        "answer": "The pipe operator '|' feeds the standard output of one command as standard input into another (e.g. 'ps aux | grep nginx'). The '>' operator overwrites output into a file ('echo hi > file.txt'), while '>>' appends to it without erasing previous content.",
        "primary_command": "cat",
        "recommended_lesson": "Lesson 10: Sorting, Deduplication, and Column Extraction"
    }
}


def check_faq_match(query: str):
    """
    Checks if a student query matches any common Linux learning questions.
    Returns matched FAQ dictionary or None.
    """
    q_lower = query.lower().strip()
    for key, item in FAQ_KNOWLEDGE_BASE.items():
        for trigger in item["triggers"]:
            if trigger in q_lower:
                return item
    return None


def extract_base_command(raw_text: str) -> str:
    """
    Extracts the root command token from user input.
    Handles:
      - Whitespace: '  ls  ' -> 'ls'
      - Command arguments: 'ls -la /var' -> 'ls'
      - Absolute executable paths: '/usr/bin/grep' -> 'grep'
      - Sudo prefixes: 'sudo mkdir test' -> 'mkdir'
    """
    if not raw_text or not isinstance(raw_text, str):
        return ""

    tokens = raw_text.strip().split()
    if not tokens:
        return ""

    first_token = tokens[0]

    # Handle sudo elevation prefix
    if first_token.lower() == "sudo" and len(tokens) > 1:
        first_token = tokens[1]

    # Extract basename if an absolute or relative path was supplied
    base_name = posixpath.basename(first_token)
    return base_name.lower()


def find_close_matches(query: str, limit: int = 3) -> list:
    """Finds closest matching known commands using difflib fuzzy matching."""
    return difflib.get_close_matches(query.lower(), COMMAND_KNOWLEDGE_BASE.keys(), n=limit, cutoff=0.5)


# ============================================================================
# APPLICATION ROUTES
# ============================================================================

@app.route("/", methods=["GET"])
def index():
    """Renders the main web interface."""
    return render_template("index.html")


@app.route("/api/command", methods=["POST"])
def explain_command():
    """
    Accepts JSON: {"command": "<user_input>"}
    Returns structured explanation or friendly guidance.
    
    SECURITY GUARANTEE:
    This endpoint only performs text matching against COMMAND_KNOWLEDGE_BASE.
    It never invokes os.system(), subprocess, eval(), or any shell interpreter.
    """
    payload = request.get_json(silent=True)

    if payload is None:
        return jsonify({
            "status": "error",
            "found": False,
            "message": "Invalid request. Please submit a valid JSON payload with a 'command' field."
        }), 400

    raw_command = payload.get("command", "")

    # Validate empty input
    if not isinstance(raw_command, str) or not raw_command.strip():
        return jsonify({
            "status": "error",
            "found": False,
            "message": "Please enter a Linux command to explain."
        }), 400

    clean_query = raw_command.strip()
    command_name = extract_base_command(clean_query)

    # 1. Search in knowledge base (direct command match)
    if command_name in COMMAND_KNOWLEDGE_BASE:
        details = COMMAND_KNOWLEDGE_BASE[command_name]
        return jsonify({
            "status": "success",
            "found": True,
            "is_faq": False,
            "query": clean_query,
            "command": command_name,
            "data": details
        }), 200

    # 2. Check FAQ matching for natural student queries (Module 7: Deterministic Local Helper)
    faq_match = check_faq_match(clean_query)
    if faq_match:
        primary_cmd = faq_match["primary_command"]
        primary_data = COMMAND_KNOWLEDGE_BASE.get(primary_cmd)
        return jsonify({
            "status": "success",
            "found": True,
            "is_faq": True,
            "query": clean_query,
            "command": primary_cmd,
            "title": faq_match["title"],
            "answer": faq_match["answer"],
            "recommended_lesson": faq_match.get("recommended_lesson", ""),
            "data": primary_data
        }), 200

    # 3. Command not found in knowledge base
    close_matches = find_close_matches(command_name)
    suggestions_str = "ls, pwd, mkdir, cp, mv, grep, chmod, or systemctl"

    msg = f"I couldn't find '{clean_query}' in my knowledge base. Please try {suggestions_str}."
    if close_matches:
        matches_formatted = ", ".join([f"'{m}'" for m in close_matches])
        msg = f"I couldn't find '{clean_query}'. Did you mean {matches_formatted}? Please try {suggestions_str}."

    return jsonify({
        "status": "success",
        "found": False,
        "is_faq": False,
        "query": clean_query,
        "command": command_name,
        "close_matches": close_matches,
        "message": msg,
        "unsupported_reason": f"The query '{clean_query}' is not indexed in the local 53-command educational database."
    }), 200


@app.route("/api/commands", methods=["GET"])
def get_all_commands():
    """
    Returns list of all commands for client-side search, category filtering,
    sorting, and autocomplete dropdowns.
    """
    category_filter = request.args.get("category")
    difficulty_filter = request.args.get("difficulty")
    sort_order = request.args.get("sort", "asc")

    results = []
    for cmd_key, data in sorted(COMMAND_KNOWLEDGE_BASE.items()):
        if category_filter and data.get("category") != category_filter:
            continue
        if difficulty_filter and data.get("difficulty") != difficulty_filter:
            continue
        results.append(data)

    if sort_order == "desc":
        results.sort(key=lambda x: x["name"], reverse=True)
    elif sort_order == "category":
        results.sort(key=lambda x: (x["category"], x["name"]))
    else:
        results.sort(key=lambda x: x["name"])

    return jsonify({
        "status": "success",
        "total": len(results),
        "commands": results
    }), 200


@app.route("/api/categories", methods=["GET"])
def get_categories():
    """Returns all categories with command count stats."""
    cat_counts = {cat: 0 for cat in CATEGORIES}
    for item in COMMAND_KNOWLEDGE_BASE.values():
        c = item.get("category")
        if c in cat_counts:
            cat_counts[c] += 1

    return jsonify({
        "status": "success",
        "categories": [{"name": k, "count": v} for k, v in cat_counts.items()]
    }), 200


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Returns global platform statistics calculated from the knowledge base."""
    total_cmds = len(COMMAND_KNOWLEDGE_BASE)
    diff_counts = {"Beginner": 0, "Intermediate": 0, "Advanced": 0}
    for item in COMMAND_KNOWLEDGE_BASE.values():
        d = item.get("difficulty", "Beginner")
        if d in diff_counts:
            diff_counts[d] += 1

    return jsonify({
        "status": "success",
        "total_commands": total_cmds,
        "total_categories": len(CATEGORIES),
        "difficulty_breakdown": diff_counts
    }), 200


# ============================================================================
# COMMAND COMPARISON & SAFETY MATRIX DATA (Phase 5 & Phase 9)
# ============================================================================
COMMAND_COMPARISONS = [
    {
        "id": "cp-vs-mv",
        "title": "cp vs mv (Duplicating vs Moving/Renaming)",
        "cmd1": "cp",
        "cmd2": "mv",
        "category": "Files and directories",
        "key_difference": "'cp' creates a new independent duplicate copy while preserving the original source file. 'mv' transfers the file to a new path or renames it in place, unlinking the original source.",
        "cmd1_summary": {
            "name": "cp",
            "purpose": "Copy files or directory trees.",
            "syntax": "cp [options] source destination",
            "example": "cp report.txt backup_report.txt",
            "use_case": "Creating backups before editing critical configurations.",
            "disk_impact": "Consumes additional disk space equal to the copied file size."
        },
        "cmd2_summary": {
            "name": "mv",
            "purpose": "Move or rename files and directories.",
            "syntax": "mv [options] source destination",
            "example": "mv draft.txt final_report.txt",
            "use_case": "Renaming files or moving finished work into archive folders.",
            "disk_impact": "Within the same filesystem, only updates directory pointers (inodes); instant execution."
        },
        "rule_of_thumb": "Use 'cp -i' when you want to keep the original file untouched; use 'mv -i' when you are reorganizing or renaming."
    },
    {
        "id": "grep-vs-find",
        "title": "grep vs find (Searching File Content vs Directory Trees)",
        "cmd1": "grep",
        "cmd2": "find",
        "category": "Text processing & Files",
        "key_difference": "'grep' opens files and searches inside their text contents for matching regex patterns or words. 'find' searches through the filesystem hierarchy based on file metadata (name, size, modification date, permissions).",
        "cmd1_summary": {
            "name": "grep",
            "purpose": "Search text patterns inside files or streamed pipes.",
            "syntax": "grep [options] 'pattern' file",
            "example": "grep -rn 'Database connection failed' /var/log/",
            "use_case": "Locating specific error messages or variables inside source code and log files.",
            "search_target": "Inside file contents"
        },
        "cmd2_summary": {
            "name": "find",
            "purpose": "Locate files in directory trees matching metadata criteria.",
            "syntax": "find [path] [expression]",
            "example": "find /var/log -name '*.log' -size +10M",
            "use_case": "Finding all files modified in the last 24 hours or cleaning up large log files.",
            "search_target": "Filesystem paths and file attributes"
        },
        "rule_of_thumb": "Ask yourself: 'Am I looking for a file by its name/properties (find) or text written inside it (grep)?'"
    },
    {
        "id": "chmod-vs-chown",
        "title": "chmod vs chown (Access Permissions vs Identity Ownership)",
        "cmd1": "chmod",
        "cmd2": "chown",
        "category": "File permissions",
        "key_difference": "'chmod' (Change Mode) alters what actions (read, write, execute) can be performed by the owner, group, and others. 'chown' (Change Owner) alters who the actual owner user and group are.",
        "cmd1_summary": {
            "name": "chmod",
            "purpose": "Modify read, write, and execute permission bits.",
            "syntax": "chmod [options] mode file",
            "example": "chmod 755 deploy.sh",
            "use_case": "Making a script executable (+x) or securing private keys (600).",
            "privilege": "File owner or superuser (sudo)"
        },
        "cmd2_summary": {
            "name": "chown",
            "purpose": "Change the user and/or group owner of a file.",
            "syntax": "chown [options] owner[:group] file",
            "example": "sudo chown -R www-data:www-data /var/www/html",
            "use_case": "Reassigning uploaded web files to the web server process user.",
            "privilege": "Superuser (sudo) required to transfer ownership"
        },
        "rule_of_thumb": "Use 'chown' to answer 'Whose file is this?'; use 'chmod' to answer 'What are they allowed to do with it?'"
    },
    {
        "id": "pwd-vs-ls",
        "title": "pwd vs ls (Where Am I vs What Is Here)",
        "cmd1": "pwd",
        "cmd2": "ls",
        "category": "Files and directories",
        "key_difference": "'pwd' returns a single absolute path string representing your exact active position in the filesystem tree. 'ls' lists the directory entries (subdirectories and files) residing in that location.",
        "cmd1_summary": {
            "name": "pwd",
            "purpose": "Print current working directory absolute path.",
            "syntax": "pwd",
            "example": "pwd",
            "use_case": "Confirming your path before running commands that use relative paths.",
            "output_type": "Single path string (e.g. /home/student/projects)"
        },
        "cmd2_summary": {
            "name": "ls",
            "purpose": "List contents of the current or specified directory.",
            "syntax": "ls [options] [path]",
            "example": "ls -la",
            "use_case": "Viewing files, file sizes, timestamps, and hidden configuration dotfiles.",
            "output_type": "Directory contents listing"
        },
        "rule_of_thumb": "Run 'pwd' when orienting your current location; run 'ls -la' to see what files exist around you."
    },
    {
        "id": "apt-vs-dpkg",
        "title": "apt vs dpkg (Repository Dependency Manager vs Low-Level Package Installer)",
        "cmd1": "apt",
        "cmd2": "dpkg",
        "category": "Package management",
        "key_difference": "'apt' queries remote online repositories, automatically computes dependency trees, and downloads/installs all prerequisite packages. 'dpkg' is a low-level offline tool that installs a local .deb file directly without resolving dependencies.",
        "cmd1_summary": {
            "name": "apt",
            "purpose": "High-level package manager with automatic dependency resolution.",
            "syntax": "apt [options] command [package]",
            "example": "sudo apt update && sudo apt install nginx",
            "use_case": "Standard software installation and system updates on Debian/Ubuntu.",
            "dependency_resolution": "Automatic via remote repository mirrors"
        },
        "cmd2_summary": {
            "name": "dpkg",
            "purpose": "Low-level Debian package manager for standalone .deb files.",
            "syntax": "dpkg [options] -i package.deb",
            "example": "sudo dpkg -i google-chrome-stable_current_amd64.deb",
            "use_case": "Installing locally downloaded packages or inspecting raw .deb contents.",
            "dependency_resolution": "Manual; fails if prerequisite packages are absent"
        },
        "rule_of_thumb": "Always prefer 'apt install' for daily software management. Only use 'dpkg -i' when you have manually downloaded a standalone .deb file."
    }
]

SAFETY_RISK_MATRIX = {
    "tiers": [
        {
            "tier": 1,
            "level": "Low Risk / Safe",
            "badge": "Safe (Read-Only)",
            "color": "emerald",
            "description": "Informational commands that query status, display files, or measure system health without altering any system state.",
            "commands": ["ls", "pwd", "whoami", "date", "cat", "head", "tail", "wc", "grep", "df", "du", "top", "ps", "ping", "tree"],
            "guideline": "Safe to execute freely without superuser elevation. No risk of accidental data deletion."
        },
        {
            "tier": 2,
            "level": "Moderate Risk / File State",
            "badge": "Caution (State Changes)",
            "color": "amber",
            "description": "Commands that create, move, or adjust metadata on files. Can overwrite destination files if not monitored.",
            "commands": ["touch", "mkdir", "cp", "mv", "chmod", "chown", "chgrp", "umask", "ln", "echo"],
            "guideline": "Always use the '-i' (interactive) flag with 'cp' and 'mv' to prompt before overwriting existing files."
        },
        {
            "tier": 3,
            "level": "Elevated Risk / System Admin",
            "badge": "Privileged (Admin Impact)",
            "color": "orange",
            "description": "Administrative commands that alter running background services, network interfaces, or software packages.",
            "commands": ["sudo", "systemctl", "mount", "umount", "apt", "dpkg", "yum", "dnf", "pacman", "ip", "nice"],
            "guideline": "Requires superuser (root) privileges. Verify service name and network interface names before modifying."
        },
        {
            "tier": 4,
            "level": "Critical Risk / Destructive",
            "badge": "Critical (Permanent Action)",
            "color": "rose",
            "description": "Commands that permanently delete data, alter disk partition boundaries, or terminate processes abruptly.",
            "commands": ["rm", "kill", "killall", "fdisk", "dd", "mkfs", "shutdown", "reboot"],
            "guideline": "Linux has no desktop Recycle Bin. Never run 'rm -rf' without double-checking 'pwd'. Avoid 'kill -9' before attempting SIGTERM."
        }
    ],
    "golden_rules": [
        "1. Confirm your current directory with 'pwd' before executing deletion commands.",
        "2. Add the '-i' flag (e.g. 'rm -i', 'cp -i', 'mv -i') to trigger a confirmation prompt before destructive actions.",
        "3. Always back up configuration files ('cp config.conf config.conf.bak') before editing.",
        "4. Never grant universal 777 permissions ('chmod 777') to fix permission errors; use least-privilege principles.",
        "5. Test wildcards with 'ls' or 'echo' before passing them into 'rm' (e.g. verify 'ls *.log' before 'rm *.log')."
    ]
}


@app.route("/api/comparisons", methods=["GET"])
def get_comparisons():
    """Returns curated command comparisons for interactive comparison lab (Phase 5)."""
    return jsonify({
        "status": "success",
        "total": len(COMMAND_COMPARISONS),
        "comparisons": COMMAND_COMPARISONS
    }), 200


@app.route("/api/safety", methods=["GET"])
def get_safety_matrix():
    """Returns safety risk tiers and rules for Linux safety learning (Phase 9)."""
    return jsonify({
        "status": "success",
        "safety": SAFETY_RISK_MATRIX
    }), 200


# ============================================================================
# SAFE ERROR HANDLERS (No tracebacks exposed)
# ============================================================================

@app.errorhandler(404)
def handle_not_found(error):
    if request.path.startswith("/api/"):
        return jsonify({"status": "error", "found": False, "message": "API endpoint not found."}), 404
    return render_template("index.html"), 404


@app.errorhandler(405)
def handle_method_not_allowed(error):
    return jsonify({"status": "error", "found": False, "message": "HTTP method not allowed."}), 405


@app.errorhandler(500)
def handle_server_error(error):
    return jsonify({"status": "error", "found": False, "message": "An unexpected server error occurred. Please try again."}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
