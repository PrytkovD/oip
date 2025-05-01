from __future__ import annotations

import os.path
from timeit import default_timer as timer

from database.aggeration import Aggregation
from database.column import Column
from database.expression import Expression
from database.select import select_from
from database.table import Table


def histogram(data, bins=10):
    if not data:
        return [], []
    min_val = min(data)
    max_val = max(data)
    if min_val == max_val:
        return [len(data)], [min_val, min_val]
    bin_width = (max_val - min_val) / bins
    counts = [0] * bins
    for value in data:
        index = int((value - min_val) / bin_width)
        if index >= bins:
            index = bins - 1
        counts[index] += 1
    edges = [min_val + i * bin_width for i in range(bins + 1)]
    return counts, edges


def visualize_histogram(counts, edges, bar_width=20):
    if not counts or not edges:
        return ""

    def get_decimals(f):
        s = "{0:.10f}".format(f)
        if '.' not in s:
            return 0
        integer_part, fractional_part = s.split('.')
        fractional_part = fractional_part.rstrip('0')
        return len(fractional_part) if fractional_part else 0

    decimals = max(get_decimals(edge) for edge in edges)
    num_format = "{{0:.{0}f}}".format(decimals)

    formatted_edges = [num_format.format(edge) for edge in edges]

    max_count = max(counts) if counts else 0
    bin_lines = []
    partial_blocks = [' ', '▏', '▎', '▍', '▌', '▋', '▊', '▉']

    for i, count in enumerate(counts):
        # Format bin range
        lower = formatted_edges[i]
        upper = formatted_edges[i + 1]
        bin_range = f"[{lower}, {upper})".ljust(decimals * 2 + 8)

        # Create bar
        if max_count == 0:
            scaled = 0
        else:
            scaled = (count / max_count) * bar_width

        full_blocks = int(scaled)
        fraction = scaled - full_blocks
        partial_index = int(fraction * 8)
        partial_block = partial_blocks[partial_index] if partial_index < 8 else ' '

        bar = '█' * full_blocks + partial_block
        bar = bar.ljust(bar_width)

        # Format count with consistent width
        count_str = str(count).rjust(len(str(max_count)))

        bin_lines.append(f"{bin_range} | {count_str} | {bar}")

    return '\n'.join(bin_lines)


if __name__ == '__main__':
    a = Column('a')
    b = Column('b')
    c = Column('c')
    d = Column('d')

    foo = Table('foo', a, b, storage_dir=os.path.join('out', 'foo'))
    bar = Table('bar', c, d, storage_dir=os.path.join('out', 'bar'))

    x = Expression.constant(5)
    y = Expression.constant(6)
    z = Expression.constant(7)

    for i in range(1000):
        foo.insert({foo.a: i, foo.b: i * 2})
        bar.insert({bar.c: i * 2, bar.d: i * 3})

    records = (select_from(foo)
               .columns((Expression.raw('total') + 1).alias('total+1'))
               .join(bar, foo.b, bar.c)
               .where((foo.a > 1) & (bar.d < 20))
               .group_by(foo.b)
               .aggregate(Aggregation.sum(foo.a + bar.c).alias('total'))
               .order_by((Expression.raw('total+1'), True))
               .execute())

    start = timer()
    for record in records:
        print(record)
    end = timer()
    print(end - start)
