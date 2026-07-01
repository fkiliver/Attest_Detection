/*
 * JsonTest.java — standalone (no JUnit) unit tests for Json.java.
 * Run:  javac Json.java JsonTest.java && java JsonTest
 * Exits non-zero on first failure. Lives next to Json.java so the harness build
 * never ships it.
 */

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class JsonTest {

    static int passed = 0;

    static void check(boolean cond, String what) {
        if (!cond) {
            System.err.println("FAIL: " + what);
            System.exit(1);
        }
        passed++;
    }

    static void eq(Object a, Object b, String what) {
        boolean ok = (a == null) ? b == null : a.equals(b);
        if (!ok) {
            System.err.println("FAIL: " + what + "  expected=" + b + " got=" + a);
            System.exit(1);
        }
        passed++;
    }

    static boolean throwsOn(String json) {
        try { Json.parse(json); return false; }
        catch (Json.JsonException e) { return true; }
    }

    public static void main(String[] args) {
        // ---- scalars & types ---------------------------------------------
        eq(Json.parse("42"), 42L, "integral -> Long");
        eq(Json.parse("-7"), -7L, "negative Long");
        check(Json.parse("3.14") instanceof Double, "fractional -> Double");
        check(Json.parse("1e10") instanceof Double, "exponent -> Double");
        check(Json.parse("1E-5") instanceof Double, "neg-exponent -> Double");
        eq(Json.parse("true"), Boolean.TRUE, "true");
        eq(Json.parse("false"), Boolean.FALSE, "false");
        eq(Json.parse("null"), null, "null");
        eq(Json.parse("\"hi\""), "hi", "simple string");
        // Long overflow falls back to Double.
        check(Json.parse("123456789012345678901234567890") instanceof Double,
                "huge integral -> Double fallback");

        // ---- whitespace tolerance ----------------------------------------
        eq(Json.parse("   \n\t 5 \r\n "), 5L, "surrounding whitespace ok");

        // ---- reject invalid / non-standard tokens ------------------------
        check(throwsOn("NaN"), "reject NaN");
        check(throwsOn("Infinity"), "reject Infinity");
        check(throwsOn("-Infinity"), "reject -Infinity");
        check(throwsOn("5 6"), "reject trailing content");
        check(throwsOn("{\"a\":1"), "reject unterminated object");
        check(throwsOn("[1,2"), "reject unterminated array");
        check(throwsOn("\"abc"), "reject unterminated string");
        check(throwsOn("{a:1}"), "reject unquoted key");
        check(throwsOn(""), "reject empty input");

        // ---- string escaping round-trip ----------------------------------
        String tricky = "quote=\" back=\\ slash=/ tab=\t nl=\n ctrl= del=";
        eq(Json.parse(Json.stringify(tricky)), tricky, "tricky string round-trip");

        // ---- unicode + surrogate pairs -----------------------------------
        String accent = "café déjà vu é=é"; // codepoint 233
        eq(Json.parse(Json.stringify(accent)), accent, "non-ASCII round-trip");
        String emoji = "rocket=🚀 face=😀"; // > U+FFFF
        eq(Json.parse(Json.stringify(emoji)), emoji, "surrogate-pair round-trip");
        // Stringify must escape non-ASCII as backslash-u (charset-proof bytes).
        check(Json.stringify(accent).indexOf('é') == -1,
                "non-ASCII escaped on output");
        check(Json.stringify(accent).contains("\\u00e9"), "é emitted as \\u00e9");
        // Parsing a backslash-u escape must reconstruct the char.
        eq(Json.parse("\"\\u00e9\""), "é", "\\u00e9 parses to é");
        eq(Json.parse("\"\\uD83D\\uDE80\""), "🚀", "surrogate escape parses");

        // ---- numbers stay typed across round-trip ------------------------
        eq(Json.parse(Json.stringify(2.0)), 2.0, "2.0 stays Double");
        check(Json.stringify(2.0).equals("2.0"), "2.0 stringifies as 2.0 not 2");
        eq(Json.parse(Json.stringify(2L)), 2L, "2 stays Long");

        // ---- objects: order preserved, last-wins duplicates --------------
        Object o = Json.parse("{\"b\":1,\"a\":2,\"c\":3}");
        List<String> keys = new ArrayList<>(Json.asMap(o).keySet());
        eq(keys.toString(), "[b, a, c]", "object key order preserved");
        eq(Json.asMap(Json.parse("{\"x\":1,\"x\":2}")).get("x"), 2L, "duplicate key last-wins");

        // ---- nested structures -------------------------------------------
        Object nested = Json.parse("{\"arr\":[1,2,{\"k\":[true,null,\"z\"]}],\"n\":3.5}");
        Map<String, Object> m = Json.asMap(nested);
        eq(Json.asList(m.get("arr")).size(), 3, "nested array size");
        eq(Json.asDouble(m.get("n")), 3.5, "nested double value");

        // ---- empty containers --------------------------------------------
        eq(Json.asList(Json.parse("[]")).size(), 0, "empty array");
        eq(Json.asMap(Json.parse("{}")).size(), 0, "empty object");

        // ---- typed accessors + getPath -----------------------------------
        Object root = Json.parse("{\"observe\":{\"mode\":\"artifact\",\"depth\":2}}");
        eq(Json.getPath(root, "observe.mode"), "artifact", "getPath nested string");
        eq(Json.getPath(root, "observe.depth"), 2L, "getPath nested long");
        eq(Json.getPath(root, "observe.missing"), null, "getPath missing -> null");
        eq(Json.getPath(root, "nope.x"), null, "getPath bad path -> null");

        // ---- serializer guards -------------------------------------------
        boolean nanGuard = false;
        try { Json.stringify(Double.NaN); } catch (Json.JsonException e) { nanGuard = true; }
        check(nanGuard, "stringify(NaN) throws");

        // ---- deep nesting must not StackOverflow (bounded) ---------------
        StringBuilder deep = new StringBuilder();
        for (int i = 0; i < 5000; i++) deep.append('[');
        boolean depthGuard = false;
        try { Json.parse(deep.toString()); }
        catch (Json.JsonException e) { depthGuard = true; }
        check(depthGuard, "excessive depth rejected, not StackOverflow");

        // ---- a representative tagged value the harness will emit ----------
        Map<String, Object> bytes = new LinkedHashMap<>();
        bytes.put("__bytes__", "aGVsbG8=");
        bytes.put("len", 5L);
        String s = Json.stringify(bytes);
        eq(Json.getPath(Json.parse(s), "__bytes__"), "aGVsbG8=", "tagged bytes round-trip");

        System.out.println("OK: " + passed + " checks passed");
    }
}
