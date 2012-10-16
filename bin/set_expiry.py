def set_expiry(root, exchanges, symbols):
    """Return dict for expiry, keyed on symbols."""
    values = {}
    for i in exchanges:
        for j in symbols[i]:
            if os.path.isdir(os.path.join(root, i, j)):
                values[j] = os.listdir(os.path.join(root, i, j))
    return values
