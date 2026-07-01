/*
 * Harness.template.java — the FIXED execution driver for a single Java snippet.
 *
 * This is a TEMPLATE. The orchestrator (attest/stage2_make_runnable.py)
 * asks the LLM to fill exactly four holes (each a double-at-sign token of the
 * form NAME, listed below). Each token appears exactly once, at its insertion
 * point further down; they are referred to here by bare name to avoid being
 * substituted themselves:
 *
 *   SNIPPET   the candidate method(s)/class(es), pasted verbatim, plus any
 *             faithful minimal stubs for missing domain types. The snippet's
 *             algorithm must NOT be altered.
 *   SETUP     given one input case's args (a Map) and a fresh scratch dir,
 *             materialize the environment the snippet needs (e.g. write the
 *             input bytes to a source file) and return an Env holder.
 *   INVOKE    call the snippet with arguments adapted from (args, env) and
 *             return its result (or Env.NO_RETURN for void methods).
 *   OBSERVE   given (returnValue, env), produce the observable output object
 *             per the contract's `observe` spec (e.g. read the dest file's
 *             bytes). Return a value the canonicalizer understands.
 *
 * Everything else — argument parsing, the per-case loop, error capture, the
 * canonicalizer, size caps, incremental/atomic output — is infrastructure the
 * LLM must NOT touch. Json.java is compiled alongside this file.
 *
 * Contract with the orchestrator:
 *   argv[0] = path to inputs.json   {protocol, observe, cases:[{id, kind, args}]}
 *   argv[1] = path to outputs.json  {protocol, results:[{id, ok|error|void}]}
 * Results are streamed and the temp file atomically renamed on clean finish, so
 * a mid-run System.exit() still leaves earlier cases persisted.
 */

import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.Writer;
import java.math.BigDecimal;
import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.Base64;
import java.util.IdentityHashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

public final class Harness {

    // ------- size / safety caps (orchestrator-side backstops exist too) ----
    static final int    INLINE_BYTES_THRESHOLD = 64 * 1024;     // base64-inline below this
    static final int    MAX_VALUE_BYTES        = 1  * 1024 * 1024;
    static final int    MAX_ELEMS              = 100_000;
    static final int    MAX_DEPTH              = 64;
    static final long   CASE_TIMEOUT_MS        = 5_000;         // per-case soft timeout

    // =================================================================== //
    // BEGIN snippet region (LLM-filled). Faithful stubs allowed; no logic edits.
    // =================================================================== //

    @@SNIPPET@@

    // =================================================================== //
    // END snippet region.
    // =================================================================== //

    /** Opaque per-case environment produced by SETUP and consumed by INVOKE/OBSERVE. */
    static final class Env {
        /** Sentinel meaning "the invoked method has no meaningful return value". */
        static final Object NO_RETURN = new Object();
        final Path dir;                       // this case's scratch subdir
        final Map<String, Object> slots = new LinkedHashMap<>();
        Env(Path dir) { this.dir = dir; }
        Env put(String k, Object v) { slots.put(k, v); return this; }
        Object get(String k) { return slots.get(k); }
    }

    // ---- LLM-filled adapter holes ---------------------------------------- //

    /** Materialize the environment for one input case. */
    static Env setup(Map<String, Object> args, Path caseDir) throws Exception {
        @@SETUP@@
    }

    /** Invoke the snippet; return its value or Env.NO_RETURN for void. */
    static Object invoke(Map<String, Object> args, Env env) throws Throwable {
        @@INVOKE@@
    }

    /** Produce the observable output object per the contract's observe spec. */
    static Object observe(Object returnValue, Env env, Object observeSpec) throws Exception {
        @@OBSERVE@@
    }

    // =================================================================== //
    // BELOW: fixed infrastructure. Do not modify.
    // =================================================================== //

    public static void main(String[] argv) throws Exception {
        if (argv.length < 2) {
            System.err.println("usage: Harness <inputs.json> <outputs.json>");
            System.exit(2);
        }
        Path inputsPath = Paths.get(argv[0]);
        Path outputsPath = Paths.get(argv[1]);
        Path tmpPath = Paths.get(argv[1] + ".tmp");

        String inputText = new String(Files.readAllBytes(inputsPath), StandardCharsets.UTF_8);
        Map<String, Object> env = Json.asMap(Json.parse(inputText));
        Object observeSpec = env.get("observe");
        List<Object> cases = (env.get("cases") instanceof List)
                ? Json.asList(env.get("cases")) : new ArrayList<>();

        Path scratchRoot = Files.createTempDirectory("harn_cases_");

        // Stream results so an abrupt exit keeps earlier cases. We open the array,
        // append each result with a flush, then close + atomic-rename at the end.
        try (Writer w = new OutputStreamWriter(
                Files.newOutputStream(tmpPath), StandardCharsets.UTF_8)) {
            w.write("{\"protocol\":1,\"results\":[");
            boolean first = true;
            for (Object cObj : cases) {
                Map<String, Object> c = Json.asMap(cObj);
                String id = String.valueOf(c.get("id"));
                Map<String, Object> args = (c.get("args") instanceof Map)
                        ? Json.asMap(c.get("args")) : new LinkedHashMap<>();
                Map<String, Object> result = runOneCase(id, args, observeSpec, scratchRoot);
                if (!first) w.write(",");
                first = false;
                w.write(Json.stringify(result));
                w.flush();
            }
            w.write("]}");
        }
        Files.move(tmpPath, outputsPath, StandardCopyOption.ATOMIC_MOVE);
        // Explicit exit so a lingering non-daemon thread spawned by the snippet
        // cannot keep the JVM alive past the orchestrator's timeout.
        System.exit(0);
    }

    /** Run a single case under a per-case soft timeout; never throws. */
    static Map<String, Object> runOneCase(
            String id, Map<String, Object> args, Object observeSpec, Path scratchRoot) {
        ExecutorService pool = Executors.newSingleThreadExecutor(r -> {
            Thread t = new Thread(r, "case-" + id);
            t.setDaemon(true);
            return t;
        });
        try {
            Future<Map<String, Object>> fut = pool.submit(
                    (Callable<Map<String, Object>>) () -> runCaseBody(id, args, observeSpec, scratchRoot));
            try {
                return fut.get(CASE_TIMEOUT_MS, TimeUnit.MILLISECONDS);
            } catch (TimeoutException te) {
                fut.cancel(true);
                return errorResult(id, "__CaseTimeout__",
                        "case exceeded " + CASE_TIMEOUT_MS + "ms");
            } catch (Throwable t) {
                Throwable cause = (t.getCause() != null) ? t.getCause() : t;
                return errorResult(id, cause.getClass().getName(), safeMessage(cause));
            }
        } finally {
            pool.shutdownNow();
        }
    }

    static Map<String, Object> runCaseBody(
            String id, Map<String, Object> args, Object observeSpec, Path scratchRoot)
            throws Exception {
        Path caseDir = scratchRoot.resolve("c_" + sanitize(id));
        Files.createDirectories(caseDir);
        try {
            Env env = setup(args, caseDir);
            Object ret;
            try {
                ret = invoke(args, env);
            } catch (Throwable snippetError) {
                // A throw from the snippet IS observable behavior — record it.
                return errorResult(id, snippetError.getClass().getName(),
                        safeMessage(snippetError));
            }
            Object observed = observe(ret, env, observeSpec);
            Map<String, Object> r = new LinkedHashMap<>();
            r.put("id", id);
            // The result is "void" only when OBSERVE itself yields nothing to
            // observe. A void *return* is fine and expected for side-effecting
            // snippets (artifact/composite modes) — there OBSERVE reads the
            // artifact and returns a real value, so we must not short-circuit on
            // ret == NO_RETURN.
            if (observed == Env.NO_RETURN) {
                r.put("ok", null);
                r.put("void", Boolean.TRUE);
            } else {
                r.put("ok", canonicalize(observed, 0, new IdentityHashMap<>()));
            }
            return r;
        } finally {
            deleteTree(caseDir);
        }
    }

    // ---- canonicalizer: arbitrary Java value -> tagged JSON tree --------- //

    static Object canonicalize(Object v, int depth, IdentityHashMap<Object, Object> seen) {
        if (depth > MAX_DEPTH) return tag("__truncated__", "max depth");
        if (v == null) return null;
        if (v instanceof String) return capString((String) v);
        if (v instanceof Boolean) return v;
        if (v instanceof Character) return String.valueOf(v);

        if (v instanceof Float || v instanceof Double) {
            double d = ((Number) v).doubleValue();
            if (Double.isNaN(d)) return tag("__f64__", "NaN");
            if (Double.isInfinite(d)) return tag("__f64__", d > 0 ? "Infinity" : "-Infinity");
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("__f64__", d);
            return m;
        }
        if (v instanceof BigInteger || v instanceof BigDecimal) {
            return tag("__bignum__", v.toString());
        }
        if (v instanceof Byte || v instanceof Short || v instanceof Integer || v instanceof Long) {
            return ((Number) v).longValue();
        }
        if (v instanceof byte[]) {
            return encodeBytes((byte[]) v);
        }

        // guard against cycles for the composite/container cases below
        if (seen.containsKey(v)) return tag("__cycle__", v.getClass().getName());
        seen.put(v, Boolean.TRUE);
        try {
            if (v instanceof Map) {
                Map<?, ?> src = (Map<?, ?>) v;
                Map<String, Object> out = new LinkedHashMap<>();
                int n = 0;
                for (Map.Entry<?, ?> e : src.entrySet()) {
                    if (n++ >= MAX_ELEMS) { out.put("__truncated__", true); break; }
                    out.put(String.valueOf(e.getKey()),
                            canonicalize(e.getValue(), depth + 1, seen));
                }
                return out;
            }
            if (v instanceof Iterable) {
                List<Object> out = new ArrayList<>();
                int n = 0;
                for (Object item : (Iterable<?>) v) {
                    if (n++ >= MAX_ELEMS) { out.add(tag("__truncated__", "max elems")); break; }
                    out.add(canonicalize(item, depth + 1, seen));
                }
                return out;
            }
            if (v.getClass().isArray()) {
                List<Object> out = new ArrayList<>();
                int len = java.lang.reflect.Array.getLength(v);
                for (int i = 0; i < len && i < MAX_ELEMS; i++) {
                    out.add(canonicalize(java.lang.reflect.Array.get(v, i), depth + 1, seen));
                }
                return out;
            }
        } finally {
            seen.remove(v);
        }

        // Fallback: present the value's stringification, flagged as opaque so the
        // comparator/diff-explainer knows it was not a structured observation.
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("__opaque__", v.getClass().getName());
        m.put("toString", capString(String.valueOf(v)));
        return m;
    }

    static Object encodeBytes(byte[] b) {
        Map<String, Object> m = new LinkedHashMap<>();
        String sha = sha256Hex(b);
        if (b.length > INLINE_BYTES_THRESHOLD) {
            // Too big to inline: digest + length is enough to decide byte-equality.
            Map<String, Object> ref = new LinkedHashMap<>();
            ref.put("sha256", sha);
            ref.put("len", (long) b.length);
            m.put("__bytes_ref__", ref);
        } else {
            m.put("__bytes__", Base64.getEncoder().encodeToString(b));
            m.put("len", (long) b.length);
            m.put("sha256", sha);
        }
        return m;
    }

    static Object capString(String s) {
        byte[] raw = s.getBytes(StandardCharsets.UTF_8);
        if (raw.length <= MAX_VALUE_BYTES) return s;
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("__truncated_string__", true);
        m.put("len", (long) raw.length);
        m.put("sha256", sha256Hex(raw));
        return m;
    }

    static Map<String, Object> tag(String key, Object val) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put(key, val);
        return m;
    }

    static Map<String, Object> errorResult(String id, String type, String message) {
        Map<String, Object> err = new LinkedHashMap<>();
        err.put("type", type);
        err.put("message", message == null ? "" : message);
        Map<String, Object> r = new LinkedHashMap<>();
        r.put("id", id);
        r.put("error", err);
        return r;
    }

    // ---- small helpers ---------------------------------------------------- //

    static String safeMessage(Throwable t) {
        String m = t.getMessage();
        if (m == null) return "";
        return m.length() > 4096 ? m.substring(0, 4096) : m;
    }

    static String sanitize(String id) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < id.length() && i < 64; i++) {
            char c = id.charAt(i);
            sb.append((Character.isLetterOrDigit(c) || c == '-' || c == '_') ? c : '_');
        }
        return sb.length() == 0 ? "x" : sb.toString();
    }

    static String sha256Hex(byte[] b) {
        try {
            byte[] d = java.security.MessageDigest.getInstance("SHA-256").digest(b);
            StringBuilder sb = new StringBuilder(d.length * 2);
            for (byte x : d) sb.append(Character.forDigit((x >> 4) & 0xF, 16))
                               .append(Character.forDigit(x & 0xF, 16));
            return sb.toString();
        } catch (Exception e) {
            return "";
        }
    }

    static void deleteTree(Path dir) {
        if (dir == null || !Files.exists(dir)) return;
        try {
            Files.walk(dir)
                 .sorted((a, b) -> b.getNameCount() - a.getNameCount())
                 .forEach(p -> { try { Files.deleteIfExists(p); } catch (IOException ignored) {} });
        } catch (IOException ignored) {
        }
    }
}
