def batched(iterable, batch_size):
    i = 0
    while i < len(iterable):
        yield iterable[i: i + batch_size]
        i += batch_size
