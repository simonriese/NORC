"""
Core analysis module for test_util.py in the NORC toolkit.

Copyright (c) 2026 TU Darmstadt, Germany
Version: v0.2
Date: 2026-02-27

Licensed under the BSD 3-Clause License.
For more information, see the LICENSE file in the project root:
https://github.com/tuda-parallel/NORC/blob/main/LICENSE
"""
"""
Unit tests for the utility functions and shared classes in NORC analysis.

Copyright (c) 2026 TU Darmstadt, Germany
Version: v0.2
Date: 2026-02-27

Licensed under the BSD 3-Clause License.
For more information, see the LICENSE file in the project root:
https://github.com/tuda-parallel/NORC/blob/main/LICENSE
"""

from norc.helpers.util import (
    counted_set,
    experiment_filter,
    measurement_info,
    sorted_index_map,
)


def test_measurement_info_key():
    info = measurement_info()
    info.benchmark = "test_bench"
    info.system = "test_sys"
    info.noise_pattern = "test_noise"
    info.counter = "test_counter"

    assert info.key() == ("test_bench", "test_sys", "test_noise", "test_counter")
    assert info.noiseless_key() == ("test_bench", "test_sys", "NO_NOISE", "test_counter")


def test_experiment_filter():
    # Test with empty filters (should accept everything)
    f = experiment_filter()
    info = measurement_info()
    info.benchmark = "any"
    info.system = "any"
    info.noise_pattern = "NO_NOISE"
    info.counter = "any"
    assert f.check(info) is True

    # Test with specific filters
    f2 = experiment_filter(
        benchmarks="b1,b2", systems="s1", noise_patterns="n1", counters="c1"
    )

    info.benchmark = "b1"
    info.system = "s1"
    info.noise_pattern = "n1"
    info.counter = "c1"
    assert f2.check(info) is True

    info.benchmark = "b3"
    assert f2.check(info) is False


def test_counted_set():
    cs = counted_set()
    cs.insert("a")
    cs.insert("b")
    cs.insert("a")  # Duplicate

    assert cs.counts["a"] == 0
    assert cs.counts["b"] == 1
    assert len(cs.counts) == 2
    assert cs.ordered_elements() == ["a", "b"]


def test_sorted_index_map():
    l = ["b", "a", "c"]
    mp = sorted_index_map(l)

    assert mp["a"] == 0
    assert mp["b"] == 1
    assert mp["c"] == 2
