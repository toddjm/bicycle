def read_file(path, name):
    """Read file and return a list of strings without newlines."""
    if not os.path.isdir(path):
        print("{0} is not a directory.").format(path)
        sys.exit()
    if not os.path.isfile(os.path.join(path, name)):
        print("{0} is not a file.").format(name)
        sys.exit()
    filename = os.path.join(path, name)
    with open(filename, 'r') as infile:
        values = infile.readlines()
    values = [i.strip() for i in values]
    return values
