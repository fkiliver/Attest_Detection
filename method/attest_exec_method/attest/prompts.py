"""All LLM prompts, centralized.

Keeping prompts in one module makes them easy to tune and to cite in the paper's
methodology, and keeps the stage modules focused on control flow. Each builder
returns a list of OpenAI-style messages.

Design rules encoded throughout (see project memory + plan):
  * The LLM completes scaffolding/adapters, never the snippet's algorithm.
  * Missing domain types become FAITHFUL minimal stubs, never `return null`
    placeholders (the explicit contrast with jcoffee/HOLMES).
  * The harness must conform to the fixed Json/driver protocol it is given.
"""

from __future__ import annotations

from .schemas import Contract, Pair, Snippet

# --------------------------------------------------------------------------- #
# Shared protocol explainer injected into stage-2 prompts.
# --------------------------------------------------------------------------- #

_JAVA_PROTOCOL = r"""
You are filling holes in a FIXED Java driver template. You will be given the
template; you must return ONLY the contents of these holes:
  - SNIPPET : the candidate code, pasted with its algorithm UNCHANGED, plus any
              faithful minimal stubs needed to compile. A stub must implement the
              real intended behavior as far as the snippet relies on it; it must
              NOT be an empty body or `return null` placeholder.
  - SETUP   : body of `static Env setup(Map<String,Object> args, Path caseDir)`.
              Decode one input case's args and build the environment the snippet
              needs (e.g. write input bytes to `caseDir.resolve("src.bin")`).
              Return an Env (use `new Env(caseDir).put("k", v)`).
  - INVOKE  : body of `static Object invoke(Map<String,Object> args, Env env)`.
              Call the snippet with arguments adapted from args/env and return its
              result. For a void/side-effecting snippet, return `Env.NO_RETURN`.
  - OBSERVE : body of `static Object observe(Object returnValue, Env env, Object observeSpec)`.
              Produce the ONE observable output per the contract's observe mode:
                * return  -> return `returnValue`
                * artifact-> read the artifact (e.g. the dest file's bytes via
                             `Files.readAllBytes`) and return it (byte[] is fine)
                * state   -> return a small Map of the whitelisted accessor values
                * composite-> return a Map with one entry per part
              Return `Env.NO_RETURN` only if there is genuinely nothing to observe.

Helper API available (DO NOT reimplement, DO NOT modify Json.java):
  Json.asMap(o) Json.asList(o) Json.asString(o) Json.asLong(o) Json.asDouble(o)
  Json.asBool(o) Json.getPath(root,"a.b")
The driver already imports java.io.*, java.nio.file.*, java.util.*, java.util.Base64.
Hard rules:
  - Do NOT write the two-character sequence backslash-u anywhere except as a
    valid 4-hex-digit escape (Java lexes it even inside comments).
  - Do NOT print to stdout for the protocol; the driver writes outputs itself.
  - Keep the snippet's computation intact; only add scaffolding and the adapter.
"""

_CPP_PROTOCOL = r"""
You are filling holes in a FIXED C++ driver template (compiled as C++17). Return
ONLY the contents of these holes:
  - SNIPPET : the candidate code with its algorithm UNCHANGED, plus faithful
              minimal stubs/includes needed to compile. No empty stubs. CRITICAL:
              if the snippet is a `main`-style program, rename `int main(...)` to
              `int snippet_entry()` AND ensure it ENDS WITH `return 0;` — a
              value-returning function that falls off the end is undefined
              behavior and will crash (C's implicit main-return does not apply to
              snippet_entry). Always add the trailing `return 0;`.
  - SETUP   : prepare one input case. The input args are available as a parsed
              JSON object `args` (a JsonValue). For stdin-style programs, write
              the program's stdin text into the string `env.stdin_text`.
  - INVOKE  : run the snippet for this case. If the snippet is a `main`-style
              program that reads stdin and writes stdout, call
              `run_with_stdin(env)` which feeds env.stdin_text and captures
              stdout into env.stdout_text; otherwise call the function directly
              and store its result in env.
  - OBSERVE : return the observable output as a JsonValue per the observe mode:
                * return  -> the function's return value
                * artifact (stdout) -> JsonValue::str(env.stdout_text)
Available helpers: JsonValue (parse/serialize), run_with_stdin(env). Do NOT use
network. Keep computation intact; only add scaffolding and the adapter.
"""


def protocol_for(language: str) -> str:
    return _CPP_PROTOCOL if language in ("cpp", "c") else _JAVA_PROTOCOL


# --------------------------------------------------------------------------- #
# Stage 1: comprehend + unified contract
# --------------------------------------------------------------------------- #


def stage1_messages(pair: Pair) -> list[dict[str, str]]:
    system = (
        "You are an expert program-comprehension assistant for a semantic "
        "code-clone detector. You analyze two code snippets and decide HOW to "
        "test them for behavioral equivalence. You are precise and return "
        "strict JSON only."
    )
    user = f"""Two code snippets are given (language: {pair.a.language}).

For EACH snippet, write a one-line functional label: what observable task does it
perform? Then decide whether the two snippets attempt the SAME function (same
observable task), ignoring surface differences in API, control flow, or style.

Judge `same_function` by the CORE TASK only. Set it to false ONLY when the two
snippets clearly solve DIFFERENT problems (e.g. "sort a list" vs "hash a
string"). Do NOT set it to false merely because of: a stricter/looser input
validation or accepted character set, different handling of edge/degenerate or
out-of-range inputs, an incidental bug in one side, or different output
formatting. Those still count as the same function — they will be sorted out
later by actual execution. When the core task matches, set same_function=true and
let the pipeline run them.

Then define a UNIFIED TEST CONTRACT for exercising both identically:
- unified_signature: a short description of the common input(s) the pair will be
  fed and the output that will be observed.
- input_fields: a list of {{"name","type","desc"}} describing the fields each
  test case's `args` object must contain (the SAME for both snippets). Use simple
  JSON-friendly types (e.g. "int[] as JSON array", "string", "bytes as base64").
- observe: how to obtain ONE comparable observation from each run. Choose:
    {{"mode":"return"}}  -> compare the return value
    {{"mode":"artifact","artifact":{{"kind":"file_bytes|file_text|stdout","path_role":"dest","charset":"UTF-8"}}}}
        -> the snippets express their result as a side effect (e.g. writing a
           destination file, or printing to stdout). Compare that artifact.
    {{"mode":"state","accessors":["getX()", ...]}} -> compare projected fields of a returned object.
    {{"mode":"composite","parts":[{{"name":...,"mode":...}}, ...]}} -> compare several parts.

Guidance:
- If the snippets COPY/WRITE data to a file, prefer artifact/file_bytes on the dest.
- If they are whole programs reading stdin and printing results, prefer artifact/stdout.
- If they return a value, prefer return.
- Pick the observation that best captures the SHARED core behavior.

IMPORTANT about input_fields — make the HARNESS own the data, not the filesystem:
- The harness controls the environment per case. So when a snippet reads/writes
  files, do NOT make the input a path the caller must pre-create. Instead make the
  input the CONTENT (e.g. a field "src_bytes_b64": base64 of the source file's
  bytes). The adapter will write that content into a scratch file and point the
  snippet at it, then observe the destination file, so both snippets are fed
  identical content and their outputs are directly comparable.
- Only use path/string inputs when the function genuinely operates on a path value
  itself (not on the file's content).

CRITICAL for whole programs that read STDIN and print to STDOUT (observe mode
artifact/stdout): the unified input MUST be the RAW STDIN TEXT, as a single field
named exactly "stdin" (type string) that contains the COMPLETE bytes to feed on
standard input, already formatted exactly as the program expects to read them
(including the right separators and newlines). Do NOT decompose the input into
semantic fields like "n", "source", "items" — if you do, the two snippets' adapters
will re-serialize stdin differently (one space-separated, one newline-separated)
and the programs will receive DIFFERENT input, producing spurious differences. One
raw "stdin" string, fed verbatim to BOTH programs, is the only correct shape here.

Also state the VALID INPUT DOMAIN the snippets assume — the preconditions a
caller is expected to satisfy (value ranges, sizes, counts, format guarantees,
e.g. "n >= 1", "all integers are non-negative and < 1000", "the string is
non-empty ASCII"). Competition/programming-task code is typically written for a
specific input range and may legitimately misbehave outside it; capturing that
range lets the tester avoid manufacturing spurious differences on inputs the
code was never meant to handle. If there is no obvious restriction, say "any
valid input of the stated types".

CRITICAL — give BOTH lower and upper bounds, inferred from how the code INDEXES
and ITERATES, not just sizes. Inspect both snippets for implicit minimum-size
assumptions and state them explicitly. Examples of implicit lower bounds:
- an access like a[len-2] or s[i+k-2] implies that token is at least 2 chars;
- a loop "for i in 1..n" or reading the first element before a loop implies n>=1;
- subtracting a fixed offset from a length implies a minimum length.
State the domain as the INTERSECTION of both snippets' assumptions (the inputs on
which BOTH are intended to work), e.g. "source non-empty; pattern length >= 2 and
<= 99; replacement length >= 1". If the two snippets assume DIFFERENT minimums,
report the larger minimum (the shared safe domain). Do not emit only upper bounds.

Snippet A (id={pair.a.id}):
```{pair.a.language}
{pair.a.short()}
```

Snippet B (id={pair.b.id}):
```{pair.b.language}
{pair.b.short()}
```

Return STRICT JSON with keys exactly:
{{"label_a": str, "label_b": str, "same_function": bool,
  "unified_signature": str, "input_fields": [{{"name":str,"type":str,"desc":str}}],
  "input_domain": str, "observe": {{...}}, "rationale": str}}"""
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


# --------------------------------------------------------------------------- #
# Stage 2: make runnable (fill harness holes for one side)
# --------------------------------------------------------------------------- #


def stage2_messages(
    snippet: Snippet,
    contract: Contract,
    template: str,
) -> list[dict[str, str]]:
    system = (
        "You are an expert at making incomplete code runnable WITHOUT changing "
        "what it computes. You complete missing scaffolding and write a thin I/O "
        "adapter so the code conforms to a fixed test harness. You return strict "
        "JSON only."
    )
    protocol = protocol_for(snippet.language)
    contract_json = contract.to_json()
    user = f"""{protocol}

The unified test contract for this pair:
{_compact(contract_json)}

The fixed driver TEMPLATE you are filling (study its Env type and helper methods;
fill the holes so it compiles and runs):
```{snippet.language}
{template}
```

The snippet to make runnable (id={snippet.id}); keep its algorithm intact:
```{snippet.language}
{snippet.code}
```

Produce the hole contents so that, given a test case whose `args` match the
contract's input_fields, the harness exercises THIS snippet and OBSERVE yields the
observation specified by the contract's observe mode.

Handling FILE and ENVIRONMENT dependencies (critical for a faithful run):
- If the snippet reads a file (FileInputStream/FileReader/RandomAccessFile/
  Files.read*/getResourceAsStream), do NOT stub the read to return canned data.
  Instead, in SETUP, materialize a REAL temporary file whose bytes come from the
  case's content field (e.g. base64 in args), then make the snippet read THAT
  path. Create a fresh temp dir per case; both snippets thus read identical bytes.
- If the snippet writes a file (FileOutputStream/FileWriter/Files.write), let it
  write to a real temp path and have OBSERVE read that file's bytes back.
- If the snippet hardcodes a path or URL, redirect it: replace the hardcoded
  location with the per-case temp file you created (for a file path) so the run is
  deterministic and identical across both snippets. Keep the algorithm intact ---
  only the location it reads/writes changes, not what it does with the data.
- ONLY stub a dependency when it is genuinely non-file and non-deterministic
  (live network host, system clock, randomness) AND the contract's observe mode
  does not depend on it; never stub a file read when the case provides its content.

Return STRICT JSON with keys exactly: {{"holes": {{"SNIPPET": str, "SETUP": str,
"INVOKE": str, "OBSERVE": str}}, "notes": str}}. Each hole value is raw source
code (no markdown fences)."""
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def stage2_repair_messages(
    snippet: Snippet,
    contract: Contract,
    template: str,
    previous_source: str,
    diagnostics: str,
    compile_command: str,
    kind: str = "compile",
) -> list[dict[str, str]]:
    """Feed compiler/startup diagnostics back to fix the harness."""
    system = (
        "You fix compilation and startup errors in a generated test harness. You "
        "change ONLY what is needed to make it compile and run; you never alter "
        "the snippet's algorithm or the fixed driver infrastructure. Strict JSON."
    )
    what = (
        "The harness failed to COMPILE. Fix the compile errors."
        if kind == "compile"
        else "The harness COMPILED but produced no usable output (it crashed at "
        "startup before writing results, or every case failed with the same "
        "infrastructure error). Fix the wiring — NOT the snippet's logic. Note: a "
        "snippet that genuinely throws on a given input is correct behavior, not a "
        "bug to fix."
    )
    user = f"""{what}

Exact command:
{compile_command}

Diagnostics:
{_clip(diagnostics, 6000)}

The current full harness source (line-numbered for reference):
```{snippet.language}
{_number_lines(previous_source)}
```

Reminder of the rules:
- Missing types/methods -> faithful minimal stubs, never empty / `return null`.
- Do NOT modify Json.java or the fixed driver sections.
- Do NOT write the backslash-u sequence except as a real 4-hex escape.

Return STRICT JSON with keys exactly: {{"holes": {{"SNIPPET": str, "SETUP": str,
"INVOKE": str, "OBSERVE": str}}, "notes": str}} — the COMPLETE corrected holes."""
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


# --------------------------------------------------------------------------- #
# Stage 3: synthesize the shared input batch
# --------------------------------------------------------------------------- #


def stage3_messages(contract: Contract, n: int = 12) -> list[dict[str, str]]:
    system = (
        "You design test inputs that cover a function's intended behavior, "
        "including edge cases that reveal hidden behavioral differences. You "
        "return strict JSON only."
    )
    user = f"""Design ONE shared batch of about {n} input cases to exercise a pair of
snippets that implement this function:

unified_signature: {contract.unified_signature}
label: {contract.label_a}
input_fields (each case's `args` MUST contain exactly these fields):
{_compact(contract.input_fields)}
VALID INPUT DOMAIN (preconditions the code assumes):
{contract.input_domain or "any valid input of the stated types"}
observe mode: {contract.observe.mode.value}

Requirements:
- Stay INSIDE the valid input domain above. The goal is to compare the two
  snippets on inputs they are actually meant to handle, so that genuine
  functional differences show up while inputs the code was never designed for do
  NOT manufacture spurious divergences.
- Respect EVERY bound in the domain, both lower and upper. "Smallest allowed
  input" means the domain's stated MINIMUM, never below it: if the domain says
  "pattern length >= 2", do NOT emit a 0- or 1-character pattern as a normal/
  boundary case; if it says "n >= 1", never emit n=0. Re-read the domain's
  minimums before writing each case and check the case satisfies them.
- Within that domain, cover normal/representative inputs AND meaningful edge
  cases that are STILL VALID: the smallest input that still SATISFIES the minimums,
  the largest allowed, values just inside the bounds, duplicates, ordering
  variations, and (only if the domain permits them) non-ASCII / Unicode.
- Do NOT generate inputs that violate the stated preconditions (e.g. n=0 when the
  domain says n>=1, a 1-char token when the code indexes token[len-2], negative
  numbers when the domain says non-negative, malformed format) as NORMAL cases. But
  you MUST ALSO include 2-3 deliberate ROBUSTNESS PROBES that step just outside the
  domain to surface hidden divergences (e.g. empty input, a value below a minimum,
  and especially NON-ASCII / Unicode when the domain is ASCII-only) --- these often
  expose a latent crash in one implementation. Tag EACH such probe's `kind` with the
  prefix "ood_" (e.g. "ood_nonascii", "ood_empty"). They are recorded as evidence
  and reported, but EXCLUDED from the pass-rate verdict, so they reveal differences
  without penalizing inputs the code was never required to handle. A case that sits
  AT a valid minimum is normal, not ood_; a case BELOW a minimum or outside the
  charset must be ood_.
- Every case's args must be concrete JSON matching input_fields. Encode bytes as
  base64 strings; encode arrays as JSON arrays. If input_fields is a single
  "stdin" field, put the COMPLETE raw standard-input text there, formatted
  exactly as the program reads it (correct separators/newlines) — do not split it
  into multiple fields.
- Keep each case SMALL: a "large" case should be at most a few hundred elements
  / a few hundred bytes (base64 under ~400 chars). Do NOT inline kilobytes of
  data — large-but-bounded is enough to probe behavior and keeps output compact.
- Give each case a short stable id ("c0","c1",...) and a `kind` tag
  (normal|min|max|boundary|duplicates|nonascii|ood_*|...).

Return STRICT JSON: {{"cases": [{{"id":str,"kind":str,"args":{{...}}}}, ...]}}"""
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


# --------------------------------------------------------------------------- #
# Stage 4: diff explainer (real vs cosmetic)
# --------------------------------------------------------------------------- #


def stage4_diff_messages(
    contract: Contract,
    differences: list[dict],
) -> list[dict[str, str]]:
    system = (
        "You judge whether differences between two programs' observed outputs "
        "reflect a REAL functional divergence or are merely COSMETIC "
        "(representation-only) differences. You are conservative: a genuine "
        "difference in computed result, thrown error class, or side effect is "
        "REAL. You return strict JSON only."
    )
    user = f"""Two snippets were run on identical inputs. After rule-based
normalization (float tolerance, unordered collections, whitespace), these cases
still differ. For each, decide if the residual difference is a real functional
divergence (different computed behavior) or cosmetic (same behavior, different
representation/formatting).

Tagged-value conventions in the observations:
- {{"__f64__": n}} is a float (already compared with tolerance upstream).
- {{"__bytes__": b64, "len", "sha256"}} or {{"__bytes_ref__": {{...}}}} is raw bytes;
  equality means identical bytes (sha256/len).
- {{"error": {{"type", "message"}}}} means the run threw; compare primarily on type.
- {{"__opaque__": cls}} means the value could not be structured.

function under test: {contract.label_a}
observe mode: {contract.observe.mode.value}

Differences:
{_compact(differences)}

Return STRICT JSON: {{"verdicts": [{{"id": str, "real_difference": bool,
"explanation": str}}, ...]}} with one entry per input id above."""
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def stage4_adjudicate_messages(
    pair: Pair,
    contract: Contract,
    pass_rate: float,
    n_cases: int,
    divergences: list[dict],
) -> list[dict[str, str]]:
    """Final holistic clone judgment when execution shows partial divergence.

    Triggered when the two snippets agree on some inputs but diverge on others
    (pass-rate below threshold but not zero). The LLM weighs the actual code and
    the concrete divergent behaviors to decide whether the snippets are clones in
    the practical sense — equivalent on the core intended task — versus genuinely
    different functions. This deliberately tolerates divergences that come from
    one side's incidental bug or a narrower input-domain check, which still count
    as clones under benchmark conventions (e.g. programming-contest solutions that
    both solve the same problem on its intended inputs).
    """
    system = (
        "You are the final adjudicator of a behavioral code-clone detector. Two "
        "snippets were actually executed on a shared set of inputs; they matched "
        "on some and diverged on others. Using BOTH the source code and the "
        "observed divergences, decide whether they are clones — implementations "
        "of the SAME core task — or genuinely different functions. Return strict "
        "JSON only."
    )
    user = f"""Two snippets implement (per Stage-1 comprehension) this task:
  A: {contract.label_a}
  B: {contract.label_b}
input domain: {contract.input_domain or "unspecified"}

They were executed on {n_cases} shared inputs and agreed on a fraction
pass_rate={pass_rate:.3f}. The remaining inputs diverged as follows
(a = snippet A's observed output/result, b = snippet B's):
{_compact(divergences)}

Snippet A:
```{pair.a.language}
{pair.a.short()}
```
Snippet B:
```{pair.b.language}
{pair.b.short()}
```

Decide CLONE vs NON-CLONE. Treat as CLONE if both implement the same core task
and the divergences are attributable to: an incidental bug in one side that does
not change its intended purpose, a stricter/looser input-validation or
input-domain check, handling of out-of-range/degenerate inputs the task never
intended, or representation-only differences. Treat as NON-CLONE only if the
snippets compute fundamentally DIFFERENT functions / solve different problems
(the divergences reflect a real difference in intended behavior on normal,
in-domain inputs).

Return STRICT JSON: {{"clone": bool, "confidence": number, "reason": str}}"""
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


# --------------------------------------------------------------------------- #
# Baseline: direct LLM clone judgment (for comparison + ablation fallback)
# --------------------------------------------------------------------------- #


def baseline_direct_messages(pair: Pair) -> list[dict[str, str]]:
    system = (
        "You are a code-clone detector. Decide whether two snippets are semantic "
        "clones (perform the same function). Strict JSON only."
    )
    user = f"""Are these two snippets semantic clones (do they perform the same
observable function, regardless of implementation)?

Snippet A:
```{pair.a.language}
{pair.a.short()}
```
Snippet B:
```{pair.b.language}
{pair.b.short()}
```

Return STRICT JSON: {{"clone": bool, "confidence": number, "reason": str}}"""
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def improved_direct_messages(pair: Pair) -> list[dict[str, str]]:
    """A behavior-focused direct judge.

    The plain baseline over-predicts clone on pairs that share surface API
    structure (both open a URL, both copy a file) but differ in what they
    actually compute. This prompt forces the model to reason about observable
    behavior --- inputs, outputs, side effects, and especially what makes the two
    DIFFER --- before answering, and to default to NON-clone when a concrete
    behavioral difference exists, even if the code looks similar.
    """
    system = (
        "You are a precise semantic code-clone detector. Two snippets are clones "
        "ONLY IF, given the same inputs and environment, they produce the same "
        "observable behavior (return value, outputs, side effects). Sharing APIs, "
        "control structure, or topic is NOT sufficient. You think step by step "
        "about behavior, then return strict JSON."
    )
    user = f"""Decide whether snippets A and B are semantic clones: do they compute
the SAME function / produce the SAME observable behavior on the same inputs?

Judge by BEHAVIOR, not surface form. Concretely:
1. State A's core behavior: what input does it consume, what does it return or
   write, what side effects does it have?
2. State B's core behavior the same way.
3. List any CONCRETE behavioral DIFFERENCE. Common real differences that look
   like clones on the surface:
   - different data source/target (a hardcoded URL/path vs a parameter; reads
     stdin vs reads a file; different endpoint or resource);
   - different transformation/computation (different hash, different formula,
     different filtering, with/without a step like authentication, salting,
     sorting, or validation);
   - different output shape, ordering, encoding, or error/exception behavior;
   - one has an extra effect the other lacks (logging that changes output,
     deleting, retrying, timestamping).
4. Decision rule: if A and B would return/emit DIFFERENT results or have
   different side effects on some reasonable shared input, answer NON-clone
   (clone=false), even if the code looks similar. Answer clone=true only if you
   are confident they are behaviorally interchangeable across their shared input
   domain. When genuinely unsure, prefer clone=false.

Snippet A:
```{pair.a.language}
{pair.a.short()}
```
Snippet B:
```{pair.b.language}
{pair.b.short()}
```

Return STRICT JSON:
{{"a_behavior": str, "b_behavior": str, "differences": [str],
  "clone": bool, "confidence": number, "reason": str}}"""
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def case_study_messages(pair: Pair) -> list[dict[str, str]]:
    """Deep structured case-study analysis of one pair.


    Produces a rich behavioral analysis intended for the paper's error-analysis
    section AND for discovering label-free reliability signals (e.g. whether a
    confident verdict is possible at all from the code alone, or whether the pair
    hinges on an external environment that no static read can settle). Sees only
    code; never any label.
    """
    system = (
        "You are an expert software engineer performing a rigorous case study to "
        "decide whether two code fragments are semantic clones --- implementations "
        "of the SAME function producing the SAME observable behavior on the same "
        "inputs. You analyze deeply and report a structured, calibrated verdict. "
        "Strict JSON only."
    )
    user = f"""Perform a careful case study of this pair.

Analyze, in order:
1. core_task_a / core_task_b: the essential function each computes (one line each).
2. inputs_outputs: what inputs each consumes and what it returns / writes / emits.
3. behavioral_differences: concrete differences that would make them diverge on
   some shared input (different computation, data source/target, transformation,
   error/exception behavior, side effects, output shape/order/encoding). Empty
   list if none.
4. external_dependency: true if deciding equivalence REQUIRES executing against an
   external/ambient resource that the code does not fully determine (network host,
   specific file contents, system clock, randomness, database, environment) ---
   i.e. a static reading cannot settle it with confidence.
5. decidable_from_code: true if you can confidently decide clone-ness from the
   code alone; false if it genuinely depends on runtime behavior you cannot
   determine here.
6. clone: your best boolean verdict (same core behavior across the shared, intended
   input domain). Prefer false when a concrete behavioral difference exists.
7. confidence: 0..1 calibrated to how sure you are.

Snippet A:
```{pair.a.language}
{pair.a.short()}
```
Snippet B:
```{pair.b.language}
{pair.b.short()}
```

Return STRICT JSON with keys exactly:
{{"core_task_a": str, "core_task_b": str, "inputs_outputs": str,
  "behavioral_differences": [str], "external_dependency": bool,
  "decidable_from_code": bool, "clone": bool, "confidence": number,
  "reason": str}}"""
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def clone_finder_messages(pair: Pair) -> list[dict[str, str]]:
    """Balanced clone finder that separates IMPLEMENTATION vs FUNCTIONAL diffs.

    The earlier behavior-focused prompts over-reject: told to "list differences",
    the model finds surface/implementation differences in any two distinct
    snippets and calls them non-clone --- it mislabeled ~52% of reliable true
    clones. This prompt fixes that by forcing the model to FIRST classify each
    difference as implementation-only (does NOT change the result) vs functional
    (DOES change the observable result), and to judge clone by whether a
    FUNCTIONAL difference exists. Sees only code; no label.
    """
    system = (
        "You decide whether two code fragments are semantic clones: same observable "
        "behavior on the same inputs. The hard part is distinguishing an "
        "IMPLEMENTATION difference (different code, SAME result) from a FUNCTIONAL "
        "difference (DIFFERENT result/side effect). Two fragments that reach the "
        "same result by different means ARE clones. You are careful not to mistake "
        "stylistic or library differences for behavioral ones. Strict JSON only."
    )
    user = f"""Decide if A and B are semantic clones (same observable behavior).

Step 1 - list each notable difference and CLASSIFY it:
  - "implementation": different code, but SAME observable result. Examples:
    FileChannel vs buffered stream copy (same bytes copied); StringBuilder vs +;
    different loop style; different local variable names; logging that does not
    change the returned/written result; a different but equivalent library call;
    reading the SAME data via a different API.
  - "functional": changes the observable result/side effect. Examples:
    DIFFERENT algorithm with different output (MD5 vs SHA-1; encode vs decode);
    different output encoding/format actually returned (Base64 vs hex);
    different data acted upon (deletes table X vs table Y; different URL CONTENT);
    different return semantics (returns content vs returns boolean); an extra
    effect that changes outcome (deletes a file the other keeps).
Be strict about what counts as functional: it must plausibly change what a caller
observes. Charset/encoding counts as functional ONLY if it changes the actual
returned/written bytes for realistic inputs.

Step 2 - decide:
  - clone = true if there is NO functional difference (all differences are
    implementation-only), i.e. they are behaviorally interchangeable on their
    shared intended inputs.
  - clone = false if at least one functional difference exists.

Snippet A:
```{pair.a.language}
{pair.a.short()}
```
Snippet B:
```{pair.b.language}
{pair.b.short()}
```

Return STRICT JSON with keys exactly:
{{"differences": [{{"desc": str, "kind": "implementation"|"functional"}}],
  "has_functional_difference": bool, "clone": bool, "confidence": number,
  "reason": str}}"""
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def functional_clone_messages(pair: Pair) -> list[dict[str, str]]:
    """Judge clone-ness under the BCB *functionality* definition (shared task),
    not strict behavioral equivalence.

    BigCloneBench labels a pair a clone when both fragments IMPLEMENT THE SAME
    TARGET FUNCTIONALITY, even if one performs additional unrelated work and the
    token overlap is low. This judge aligns with that (looser) definition: it asks
    whether the two share a common intended functionality, rather than whether they
    are behaviorally interchangeable on every input. NOTE: this measures agreement
    with the functionality-level labeling convention, not strict semantic
    equivalence; it is reported as a label-convention-consistency judge.
    """
    system = (
        "You are a code clone detector using the BigCloneBench definition of a "
        "clone: two code fragments are clones if they IMPLEMENT THE SAME "
        "FUNCTIONALITY (perform the same kind of task), even when one also does "
        "additional unrelated work, the code looks very different, or only part of "
        "each method realizes the shared task. You judge shared functionality, not "
        "line-by-line or input-by-input equivalence. Strict JSON only."
    )
    user = f"""Do snippets A and B share a common functionality, in the
BigCloneBench sense (clone = same functional intent / same kind of task that a
developer searching for that functionality would consider equivalent)?

Guidance:
- Focus on the PRIMARY task each method accomplishes (e.g. "copy a file",
  "compute an MD5 digest", "open a URL and read it", "create a temp file from a
  resource", "parse CSV into collections").
- Count as a clone (clone=true) if both methods carry out the SAME such task, even
  if: identifiers/structure differ greatly, token overlap is low, one method wraps
  the task in extra unrelated logic, or only a portion of each method implements
  the shared task.
- Count as non-clone (clone=false) only if their primary tasks are genuinely
  different kinds of operation (e.g. "sort a list" vs. "send an email").

Snippet A:
```{pair.a.language}
{pair.a.short()}
```
Snippet B:
```{pair.b.language}
{pair.b.short()}
```

Return STRICT JSON: {{"task_a": str, "task_b": str, "shared_functionality": str,
  "clone": bool, "confidence": number, "reason": str}}"""
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def fallback_contract_messages(
    pair: Pair, contract: "Contract"
) -> list[dict[str, str]]:
    """Contract-aware fallback judgment when execution could not be performed.

    Used only when the pipeline could not construct runnable behavioral evidence
    (e.g. a snippet could not be completed into a compilable harness within the
    repair budget). Rather than fall back to the blind direct judge, we give the
    model what the pipeline already established in Stage 1 — the per-snippet
    functional labels and the same-function assessment — together with the code.
    This is strictly more information than the blind baseline and reflects the
    pipeline's own comprehension step.
    """
    system = (
        "You are the fallback adjudicator of a behavioral code-clone detector. "
        "Execution-based evidence could not be constructed for this pair, so you "
        "must judge from the Stage-1 comprehension and the source code whether "
        "the two snippets are clones — implementations of the SAME core task. "
        "Return strict JSON only."
    )
    user = f"""The detector's Stage-1 comprehension found:
  label A: {contract.label_a}
  label B: {contract.label_b}
  same_core_task (Stage-1): {contract.same_function}
  intended input domain: {contract.input_domain or "unspecified"}

Decide CLONE vs NON-CLONE. Treat as CLONE if both implement the same core task,
even when one side has an incidental bug, a stricter/looser input check, or
different formatting. Treat as NON-CLONE only if they compute fundamentally
DIFFERENT functions / solve different problems.

Snippet A:
```{pair.a.language}
{pair.a.short()}
```
Snippet B:
```{pair.b.language}
{pair.b.short()}
```

Return STRICT JSON: {{"clone": bool, "confidence": number, "reason": str}}"""
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def _compact(obj) -> str:
    import json

    return json.dumps(obj, ensure_ascii=False, indent=2)


def _clip(s: str, n: int) -> str:
    return s if len(s) <= n else s[:n] + "\n...[clipped]"


def _number_lines(src: str) -> str:
    return "\n".join(f"{i:4} {line}" for i, line in enumerate(src.splitlines(), 1))
