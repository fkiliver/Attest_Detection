"""Attest — semantic (Type-4) clone detection via functional-evidence construction.

A single LLM backbone drives a 4-stage pipeline that decides whether two code
snippets are clones by *executing* both on a shared input set and comparing
observable behavior, rather than by static similarity:

    1. comprehend  -> functional labels + a unified test contract
    2. make runnable -> complete each snippet into a runnable harness
    3. synth inputs  -> one shared, intent-covering input batch
    4. execute & compare -> run both, normalize, judge residual diffs, verdict

See the README for the pipeline overview and usage.
"""

__version__ = "0.1.0"
