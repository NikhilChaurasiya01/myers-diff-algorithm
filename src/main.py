import sys


def read_lines(path):
    with open(path, "rb") as f:
        data = f.read()
    parts = data.split(b"\n")
    if parts and parts[-1] == b"":
        parts.pop()
    return parts


def myers_core(a, b):
    """a, b: int lists with no common prefix/suffix.
    Returns raw ops in order: ('=', i) / ('-', i) with i in a, ('+', j) with j in b."""
    n, m = len(a), len(b)
    max_d = n + m
    off = max_d + 1
    v = [0] * (2 * max_d + 3)
    trace = [None]  # trace[d] = v values for k in [-d, d] at the start of round d
    found = -1
    for d in range(max_d + 1):
        if d:
            trace.append(v[off - d: off + d + 1])
        for k in range(-d, d + 1, 2):
            if k == -d or (k != d and v[off + k - 1] < v[off + k + 1]):
                x = v[off + k + 1]          # move down (insert)
            else:
                x = v[off + k - 1] + 1      # move right (delete)
            y = x - k
            while x < n and y < m and a[x] == b[y]:
                x += 1
                y += 1
            v[off + k] = x
            if x == n and y == m:
                found = d
                break
        if found >= 0:
            break

    # backtrack
    ops = []
    x, y = n, m
    for d in range(found, 0, -1):
        vv = trace[d]
        k = x - y
        if k == -d or (k != d and vv[k - 1 + d] < vv[k + 1 + d]):
            pk = k + 1
        else:
            pk = k - 1
        px = vv[pk + d]
        py = px - pk
        while x > px and y > py:
            x -= 1
            y -= 1
            ops.append(('=', x))
        if x == px:
            ops.append(('+', py))   # came down: b[py] inserted
        else:
            ops.append(('-', px))   # came right: a[px] deleted
        x, y = px, py
    while x > 0 and y > 0:          # d == 0: leading diagonal
        x -= 1
        y -= 1
        ops.append(('=', x))
    ops.reverse()
    return ops


def diff(A, B):
    """Works on any two sequences (lists of bytes, or strings)."""
    n, m = len(A), len(B)
    p = 0
    while p < n and p < m and A[p] == B[p]:
        p += 1
    s = 0
    while s < n - p and s < m - p and A[n - 1 - s] == B[m - 1 - s]:
        s += 1
    ids = {}
    a = [ids.setdefault(x, len(ids)) for x in A[p:n - s]]
    b = [ids.setdefault(x, len(ids)) for x in B[p:m - s]]
    ops = [('=', i) for i in range(p)]
    if a or b:
        ops.extend((c, i + p) for c, i in myers_core(a, b))
    ops.extend(('=', n - s + t) for t in range(s))
    return ops


def blocks(ops):
    """Yield ('=', i) or ('B', dels, adds); delete-first order inside each block."""
    dels, adds = [], []
    for c, i in ops:
        if c == '=':
            if dels or adds:
                yield ('B', dels, adds)
                dels, adds = [], []
            yield ('=', i)
        elif c == '-':
            dels.append(i)
        else:
            adds.append(i)
    if dels or adds:
        yield ('B', dels, adds)


def fmt_ranges(pos):
    if not pos:
        return b"."
    out = []
    start = prev = pos[0]
    for q in pos[1:]:
        if q == prev + 1:
            prev = q
        else:
            out.append((start, prev + 1))
            start = prev = q
    out.append((start, prev + 1))
    return ",".join(f"{s}-{e}" for s, e in out).encode()


def highlight_line(old, new):
    o = old.decode("utf-8")
    nw = new.decode("utf-8")
    od, nd = [], []
    for c, i in diff(o, nw):
        if c == '-':
            od.append(i)
        elif c == '+':
            nd.append(i)
    return b"? " + fmt_ranges(od) + b" | " + fmt_ranges(nd)


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in ("lines", "highlight"):
        sys.stderr.write("usage: main.py lines|highlight A B\n")
        return 2
    mode, pa, pb = sys.argv[1:4]
    try:
        A = read_lines(pa)
        B = read_lines(pb)
    except OSError as e:
        sys.stderr.write(f"error: {e}\n")
        return 2

    ops = diff(A, B)
    out = []
    hl = (mode == "highlight")
    for blk in blocks(ops):
        if blk[0] == '=':
            out.append(b" " + A[blk[1]] + b"\n")
            continue
        _, dels, adds = blk
        for i in dels:
            out.append(b"-" + A[i] + b"\n")
        for t, j in enumerate(adds):
            out.append(b"+" + B[j] + b"\n")
            if hl and t < len(dels):
                out.append(highlight_line(A[dels[t]], B[j]) + b"\n")
    sys.stdout.buffer.write(b"".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())