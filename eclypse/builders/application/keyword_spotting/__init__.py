"""The keyword spotting application models an edge inference pipeline.

Short audio windows are captured, preprocessed, classified, and turned into a
command decision. It is inspired by the keyword spotting workload from MLPerf
Tiny.

Source:
    `MLPerf Tiny Inference Benchmark
    <https://mlcommons.org/2021/06/mlperf-tiny-inference-benchmark/>`_
"""
