import sys


def read_lines(path):
    with open(path, "rb") as f:
        lines = f.read().split(b"\n")
    if lines[-1] == b"":
        lines.pop()
    return lines


def backtrack(trace, n, m, last_d):
    deleted, inserted = [], []
    x, y = n, m
    for d in range(last_d, 0, -1):
        v = trace[d]
        k = x - y
        if k == -d or (k != d and v[k - 1 + d] < v[k + 1 + d]):
            prev_k = k + 1
            prev_x = v[prev_k + d]
            inserted.append(prev_x - prev_k)
        else:
            prev_k = k - 1
            prev_x = v[prev_k + d]
            deleted.append(prev_x)
        x, y = prev_x, prev_x - prev_k
    return deleted[::-1], inserted[::-1]


def myers(a, b):
    n, m = len(a), len(b)
    off = n + m + 1
    v = [0] * (2 * off + 1)
    trace = []
    for d in range(n + m + 1):
        trace.append(v[off - d: off + d + 1])
        for k in range(-d, d + 1, 2):
            if k == -d or (k != d and v[off + k - 1] < v[off + k + 1]):
                x = v[off + k + 1]
            else:
                x = v[off + k - 1] + 1
            y = x - k
            while x < n and y < m and a[x] == b[y]:
                x += 1
                y += 1
            v[off + k] = x
            if x == n and y == m:
                return backtrack(trace, n, m, d)


def diff(a, b):
    start = 0
    while start < len(a) and start < len(b) and a[start] == b[start]:
        start += 1
    end_a, end_b = len(a), len(b)
    while end_a > start and end_b > start and a[end_a - 1] == b[end_b - 1]:
        end_a -= 1
        end_b -= 1
    deleted, inserted = myers(a[start:end_a], b[start:end_b])
    return [i + start for i in deleted], [j + start for j in inserted]


def to_ranges(positions):
    if not positions:
        return "."
    runs = []
    for p in positions:
        if runs and runs[-1][1] == p:
            runs[-1][1] = p + 1
        else:
            runs.append([p, p + 1])
    return ",".join(f"{s}-{e}" for s, e in runs)


def highlight(old, new):
    deleted, inserted = diff(old.decode(), new.decode())
    return f"? {to_ranges(deleted)} | {to_ranges(inserted)}\n".encode()


def main():
    mode, path_a, path_b = sys.argv[1:4]
    try:
        a, b = read_lines(path_a), read_lines(path_b)
    except OSError as e:
        sys.stderr.write(f"error: {e}\n")
        return 2
    deleted, inserted = diff(a, b)
    deleted, inserted = set(deleted), set(inserted)
    out = []
    i = j = 0
    while i < len(a) or j < len(b):
        if i in deleted or j in inserted:
            old, new = [], []
            while i in deleted:
                old.append(i)
                i += 1
            while j in inserted:
                new.append(j)
                j += 1
            out += [b"-" + a[p] + b"\n" for p in old]
            for t, q in enumerate(new):
                out.append(b"+" + b[q] + b"\n")
                if mode == "highlight" and t < len(old):
                    out.append(highlight(a[old[t]], b[q]))
        else:
            out.append(b" " + a[i] + b"\n")
            i += 1
            j += 1
    sys.stdout.buffer.write(b"".join(out))
    return 0


sys.exit(main())