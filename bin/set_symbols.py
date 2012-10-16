def set_symbols(root, exchanges):
    """Return dict of symbols, keyed on exchanges."""
    values = {}
    for i in exchanges:
        values[i] = os.listdir(os.path.join(root, i))
    return values
