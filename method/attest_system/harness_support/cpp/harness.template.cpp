// harness.template.cpp — the FIXED execution driver for one C/C++ snippet.
//
// This is a TEMPLATE compiled as C++17. The orchestrator fills exactly four
// holes (each a double-at-sign token of the form NAME, referred to here by bare
// name so they are not substituted themselves; each appears once below):
//
//   SNIPPET  the candidate code with its algorithm UNCHANGED, plus faithful
//            minimal stubs/#includes needed to compile. If the snippet is a
//            stdin/stdout program, RENAME its `int main(...)` to
//            `int snippet_entry()` (keep the body identical) so the driver can
//            call it repeatedly; do not leave a second `main`.
//   SETUP    body of `void setup(const scx::JsonValue& args, Env& env)`:
//            prepare one case. For stdin programs, set `env.stdin_text` from the
//            case args. For a plain function, stash decoded args in `env`.
//   INVOKE   body of `void invoke(const scx::JsonValue& args, Env& env)`:
//            run the snippet for this case. For a stdin/stdout program call
//            `run_entry(env)` (it feeds env.stdin_text to snippet_entry() and
//            captures stdout into env.stdout_text). For a function, call it and
//            store its result in `env.result`.
//   OBSERVE  body of `scx::JsonValue observe(Env& env, const scx::JsonValue& observeSpec)`:
//            return the one observable output. For stdout programs:
//            `return scx::JsonValue::str(env.stdout_text);`  For a function,
//            return its result as a JsonValue.
//
// Everything else (argument parsing, per-case loop, stdout capture, error
// capture, output writing) is infrastructure and must not be changed.
// json.hpp is compiled alongside (included below) and must not be modified.
//
// Protocol: argv[1] = inputs.json, argv[2] = outputs.json (same as the Java
// harness). Results stream to outputs.json which is renamed on clean finish.

#include "json.hpp"

#include <csignal>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>

using scx::JsonValue;

// Per-case environment shared by the LLM-filled holes.
struct Env {
  std::string stdin_text;    // input fed to a stdin/stdout snippet
  std::string stdout_text;   // captured stdout of the snippet
  JsonValue result;          // for function-style snippets
  bool has_result = false;
};

// ===================================================================== //
// BEGIN snippet region (LLM-filled). Rename any `main` to snippet_entry().
// ===================================================================== //

@@SNIPPET@@

// ===================================================================== //
// END snippet region.
// ===================================================================== //

// Runs snippet_entry() with REAL OS-level stdin/stdout redirection, so it
// captures BOTH C stdio (scanf/printf — what OJClone programs use) and C++
// iostreams. We write env.stdin_text to a temp file, freopen stdin/stdout to
// temp files, run, then restore the original streams via saved dup'd fds and
// read the captured stdout back.
#include <fcntl.h>
#include <unistd.h>

template <typename F>
static void run_entry_impl(Env& env, F entry) {
  // unique-ish temp paths in the (writable) cwd; the container cwd is /work
  static long counter = 0;
  std::string base = "case_" + std::to_string(counter++);
  std::string in_path = base + "_in.txt";
  std::string out_path = base + "_out.txt";

  { std::ofstream f(in_path, std::ios::binary); f << env.stdin_text; }

  std::fflush(stdout);
  int saved_in = dup(fileno(stdin));
  int saved_out = dup(fileno(stdout));

  std::FILE* fin = std::freopen(in_path.c_str(), "rb", stdin);
  std::FILE* fout = std::freopen(out_path.c_str(), "wb", stdout);
  (void)fin; (void)fout;

  bool threw = false;
  try {
    entry();
  } catch (...) {
    threw = true;
  }

  std::fflush(stdout);
  std::cout.flush();
  // restore original stdin/stdout from the saved descriptors
  dup2(saved_in, fileno(stdin));
  dup2(saved_out, fileno(stdout));
  close(saved_in);
  close(saved_out);
  clearerr(stdin);
  clearerr(stdout);

  { std::ifstream f(out_path, std::ios::binary);
    std::ostringstream ss; ss << f.rdbuf(); env.stdout_text = ss.str(); }
  std::remove(in_path.c_str());
  std::remove(out_path.c_str());

  if (threw) throw std::runtime_error("snippet_entry threw");
}

// Convenience the INVOKE hole can call when snippet_entry() exists.
#define run_entry(env) run_entry_impl((env), []() { snippet_entry(); })

// ---- LLM-filled holes ------------------------------------------------- //

static void setup(const scx::JsonValue& args, Env& env) {
  @@SETUP@@
}

static void invoke(const scx::JsonValue& args, Env& env) {
  @@INVOKE@@
}

static scx::JsonValue observe(Env& env, const scx::JsonValue& observeSpec) {
  @@OBSERVE@@
}

// ===================================================================== //
// Fixed infrastructure below. Do not modify.
// ===================================================================== //

static std::string read_file(const std::string& path) {
  std::ifstream f(path, std::ios::binary);
  std::ostringstream ss;
  ss << f.rdbuf();
  return ss.str();
}

static JsonValue make_error(const std::string& id, const std::string& type,
                            const std::string& msg) {
  JsonValue r = JsonValue::object();
  r.set("id", JsonValue::str(id));
  JsonValue e = JsonValue::object();
  e.set("type", JsonValue::str(type));
  e.set("message", JsonValue::str(msg));
  r.set("error", e);
  return r;
}

static JsonValue run_one_case(const JsonValue& c) {
  std::string id = c.find("id") ? c.find("id")->as_string() : "?";
  const JsonValue* args = c.find("args");
  JsonValue empty = JsonValue::object();
  const JsonValue& a = args ? *args : empty;
  try {
    Env env;
    setup(a, env);
    JsonValue observed;
    try {
      invoke(a, env);
    } catch (const std::exception& ex) {
      return make_error(id, "std::exception", ex.what());
    } catch (...) {
      return make_error(id, "unknown", "non-standard exception");
    }
    observed = observe(env, JsonValue::null());
    JsonValue r = JsonValue::object();
    r.set("id", JsonValue::str(id));
    r.set("ok", observed);
    return r;
  } catch (const std::exception& ex) {
    return make_error(id, "setup_error", ex.what());
  }
}

int main(int argc, char** argv) {
  if (argc < 3) {
    std::fprintf(stderr, "usage: harness <inputs.json> <outputs.json>\n");
    return 2;
  }
  std::string inputs_path = argv[1];
  std::string outputs_path = argv[2];
  std::string tmp_path = outputs_path + ".tmp";

  JsonValue root;
  try {
    root = JsonValue::parse(read_file(inputs_path));
  } catch (const std::exception& ex) {
    std::fprintf(stderr, "failed to parse inputs: %s\n", ex.what());
    return 3;
  }

  const JsonValue* cases = root.find("cases");
  {
    std::ofstream w(tmp_path, std::ios::binary);
    w << "{\"protocol\":1,\"results\":[";
    w.flush();  // flush the header immediately so a crash on case 0 still leaves
                // a recoverable file (empty results array) on disk
    bool first = true;
    if (cases && cases->type() == JsonValue::Type::Array) {
      for (const auto& c : cases->arr()) {
        JsonValue r = run_one_case(c);
        if (!first) w << ",";
        first = false;
        w << r.dump();
        w.flush();  // stream so a crash keeps earlier cases
      }
    }
    w << "]}";
  }
  std::rename(tmp_path.c_str(), outputs_path.c_str());
  return 0;
}
