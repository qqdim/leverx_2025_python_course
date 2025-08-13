import functools
from itertools import zip_longest
import re


@functools.total_ordering
class Version:
    def __init__(self, version):
        self.main, _, self.pre = version.partition('-')

    def __eq__(self, other):
        return self.main == other.main and self.pre == other.pre

    def __lt__(self, other):
        def compare_parts(a, b):
            for x, y in zip_longest(a.split('.'), b.split('.'), fillvalue=''):
                if x == y:
                    continue
                x_num = re.match(r'^(\d+)', x)
                y_num = re.match(r'^(\d+)', y)
                if x_num and y_num:
                    return int(x_num.group(1)) < int(y_num.group(1))
                return x < y

        if self.main != other.main:
            return compare_parts(self.main, other.main)
        elif self.pre != other.pre:
            if self.pre and not other.pre:
                return True
            elif not self.pre and other.pre:
                return False
            else:
                return compare_parts(self.pre, other.pre)


def main():
    to_test = [
        ("1.0.0", "2.0.0"),
        ("1.0.0", "1.42.0"),
        ("1.2.0", "1.2.42"),
        ("1.1.0-alpha", "1.2.0-alpha.1"),
        ("1.0.1b", "1.0.10-alpha.beta"),
        ("1.0.0-rc.1", "1.0.0"),
    ]

    for left, right in to_test:
        assert Version(left) < Version(right), "le failed"
        assert Version(right) > Version(left), "ge failed"
        assert Version(right) != Version(left), "neq failed"

if __name__ == "__main__":
    main()
