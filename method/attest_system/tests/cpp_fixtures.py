"""Hand-filled C++ harness holes for offline-ish (Docker) executor tests.

These mirror the OJClone shape: a `main`-style program reading stdin and
printing to stdout, renamed to `snippet_entry()` so the driver can run it per
case with injected stdin.
"""

from __future__ import annotations

# A stdin/stdout C program: read two ints, print their sum.
SUM_STDIN_HOLES = {
    "SNIPPET": (
        "#include <cstdio>\n"
        "int snippet_entry() {\n"
        "    int a, b;\n"
        '    if (scanf("%d %d", &a, &b) == 2) printf("%d\\n", a + b);\n'
        "    return 0;\n"
        "}\n"
    ),
    "SETUP": (
        '    const scx::JsonValue* s = args.find("stdin");\n'
        '    env.stdin_text = s ? s->as_string() : "";\n'
    ),
    "INVOKE": "    run_entry(env);\n",
    "OBSERVE": "    return scx::JsonValue::str(env.stdout_text);\n",
}

# A variant that reverses a string read from stdin (covers non-ASCII bytes).
ECHO_STDIN_HOLES = {
    "SNIPPET": (
        "#include <iostream>\n"
        "#include <string>\n"
        "int snippet_entry() {\n"
        "    std::string line;\n"
        "    std::getline(std::cin, line);\n"
        "    std::cout << line;\n"
        "    return 0;\n"
        "}\n"
    ),
    "SETUP": (
        '    const scx::JsonValue* s = args.find("stdin");\n'
        '    env.stdin_text = s ? s->as_string() : "";\n'
    ),
    "INVOKE": "    run_entry(env);\n",
    "OBSERVE": "    return scx::JsonValue::str(env.stdout_text);\n",
}
