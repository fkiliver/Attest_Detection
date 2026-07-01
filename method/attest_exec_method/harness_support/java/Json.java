/*
 * Json.java — a tiny, dependency-free JSON parser/serializer for Attest
 * harnesses.
 *
 * THIS FILE IS INFRASTRUCTURE. The LLM-generated harness code may CALL it but
 * must NEVER modify it. It is authored once and unit-tested hard, so that the
 * generated adapter only does typed value conversion, never JSON plumbing.
 *
 * Design constraints (see the project plan):
 *   - UTF-8 everywhere; on output, escape every code unit >= 0x7F as a
 *     backslash-u hex escape so the bytes are charset-proof regardless of the
 *     reader's platform default.
 *   - Correct surrogate-pair handling for code points > U+FFFF (emoji, etc.).
 *   - Integral numbers parse to Long, fractional/exponent numbers to Double, so
 *     the comparator can tell "3" from "3.0".
 *   - Reject the non-standard bare tokens NaN / Infinity / -Infinity on input;
 *     the harness encodes those as tagged strings, never raw.
 *   - Bounded recursion depth on both parse and stringify to defeat adversarial
 *     deep nesting (no StackOverflow, no infinite cycle walk).
 *   - Object key order preserved (LinkedHashMap); duplicate keys: last wins.
 *
 * Value mapping:
 *   JSON object  <-> java.util.LinkedHashMap<String,Object>
 *   JSON array   <-> java.util.ArrayList<Object>
 *   JSON string  <-> java.lang.String
 *   JSON number  <-> java.lang.Long   (no '.', 'e', 'E')  or  java.lang.Double
 *   JSON true/false <-> java.lang.Boolean
 *   JSON null    <-> null
 */

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class Json {

    /** Maximum nesting depth accepted on parse and emitted on stringify. */
    public static final int MAX_DEPTH = 200;

    private Json() {}

    public static final class JsonException extends RuntimeException {
        public JsonException(String msg) { super(msg); }
    }

    // ===================================================================== //
    // Public API
    // ===================================================================== //

    /** Parse a JSON document into a tree of Map/List/String/Long/Double/Boolean/null. */
    public static Object parse(String text) {
        if (text == null) throw new JsonException("null input");
        Parser p = new Parser(text);
        p.skipWs();
        Object v = p.parseValue(0);
        p.skipWs();
        if (!p.atEnd()) {
            throw new JsonException("trailing content at index " + p.pos);
        }
        return v;
    }

    /** Serialize a value tree back to compact JSON. */
    public static String stringify(Object value) {
        StringBuilder sb = new StringBuilder();
        write(sb, value, 0);
        return sb.toString();
    }

    // ----- typed accessors (so harness code avoids raw casts) ------------- //

    @SuppressWarnings("unchecked")
    public static Map<String, Object> asMap(Object o) {
        if (o instanceof Map) return (Map<String, Object>) o;
        throw new JsonException("expected object, got " + typeName(o));
    }

    @SuppressWarnings("unchecked")
    public static List<Object> asList(Object o) {
        if (o instanceof List) return (List<Object>) o;
        throw new JsonException("expected array, got " + typeName(o));
    }

    public static String asString(Object o) {
        if (o instanceof String) return (String) o;
        throw new JsonException("expected string, got " + typeName(o));
    }

    public static long asLong(Object o) {
        if (o instanceof Long) return (Long) o;
        if (o instanceof Double) return (long) (double) (Double) o;
        if (o instanceof String) return Long.parseLong((String) o);
        throw new JsonException("expected number, got " + typeName(o));
    }

    public static double asDouble(Object o) {
        if (o instanceof Double) return (Double) o;
        if (o instanceof Long) return (double) (Long) o;
        if (o instanceof String) return Double.parseDouble((String) o);
        throw new JsonException("expected number, got " + typeName(o));
    }

    public static boolean asBool(Object o) {
        if (o instanceof Boolean) return (Boolean) o;
        throw new JsonException("expected boolean, got " + typeName(o));
    }

    /** Dotted lookup, e.g. getPath(root, "observe.kind"). Returns null if absent. */
    public static Object getPath(Object root, String dotted) {
        Object cur = root;
        for (String key : dotted.split("\\.")) {
            if (!(cur instanceof Map)) return null;
            cur = ((Map<?, ?>) cur).get(key);
            if (cur == null) return null;
        }
        return cur;
    }

    private static String typeName(Object o) {
        return o == null ? "null" : o.getClass().getSimpleName();
    }

    // ===================================================================== //
    // Serializer
    // ===================================================================== //

    private static void write(StringBuilder sb, Object v, int depth) {
        if (depth > MAX_DEPTH) {
            throw new JsonException("max depth exceeded while stringifying");
        }
        if (v == null) {
            sb.append("null");
        } else if (v instanceof String) {
            writeString(sb, (String) v);
        } else if (v instanceof Boolean) {
            sb.append(((Boolean) v) ? "true" : "false");
        } else if (v instanceof Double || v instanceof Float) {
            double d = ((Number) v).doubleValue();
            if (Double.isNaN(d) || Double.isInfinite(d)) {
                // Must never emit bare NaN/Infinity — not valid JSON. Callers are
                // expected to tag these as strings upstream; this is a guard.
                throw new JsonException("cannot serialize non-finite double " + d
                        + " (encode as a tagged string instead)");
            }
            sb.append(formatDouble(d));
        } else if (v instanceof Number) {
            // Long / Integer / Short / Byte / BigInteger -> integral text.
            sb.append(v.toString());
        } else if (v instanceof Map) {
            writeObject(sb, (Map<?, ?>) v, depth);
        } else if (v instanceof List) {
            writeArray(sb, (List<?>) v, depth);
        } else if (v instanceof Object[]) {
            writeArray(sb, java.util.Arrays.asList((Object[]) v), depth);
        } else {
            // Unknown type: fail loudly rather than silently stringify .toString().
            throw new JsonException("cannot serialize type " + v.getClass().getName());
        }
    }

    private static void writeObject(StringBuilder sb, Map<?, ?> map, int depth) {
        sb.append('{');
        boolean first = true;
        for (Map.Entry<?, ?> e : map.entrySet()) {
            if (!first) sb.append(',');
            first = false;
            writeString(sb, String.valueOf(e.getKey()));
            sb.append(':');
            write(sb, e.getValue(), depth + 1);
        }
        sb.append('}');
    }

    private static void writeArray(StringBuilder sb, List<?> list, int depth) {
        sb.append('[');
        boolean first = true;
        for (Object item : list) {
            if (!first) sb.append(',');
            first = false;
            write(sb, item, depth + 1);
        }
        sb.append(']');
    }

    private static String formatDouble(double d) {
        // Keep integral doubles as e.g. "2.0" (so they stay Double on round-trip),
        // but otherwise rely on Java's shortest round-trippable representation.
        if (d == Math.floor(d) && !Double.isInfinite(d)
                && Math.abs(d) < 1e15) {
            return (long) d + ".0";
        }
        return Double.toString(d);
    }

    private static void writeString(StringBuilder sb, String s) {
        sb.append('"');
        final int n = s.length();
        for (int i = 0; i < n; i++) {
            char c = s.charAt(i);
            switch (c) {
                case '"':  sb.append("\\\""); break;
                case '\\': sb.append("\\\\"); break;
                case '\b': sb.append("\\b"); break;
                case '\f': sb.append("\\f"); break;
                case '\n': sb.append("\\n"); break;
                case '\r': sb.append("\\r"); break;
                case '\t': sb.append("\\t"); break;
                default:
                    if (c < 0x20 || c >= 0x7F) {
                        // Control chars AND everything non-ASCII are escaped as
                        // backslash-u hex. Java chars are UTF-16 code units, so a
                        // surrogate pair is emitted as two such escapes
                        // automatically (which is correct).
                        sb.append("\\u");
                        appendHex4(sb, c);
                    } else {
                        sb.append(c);
                    }
            }
        }
        sb.append('"');
    }

    private static void appendHex4(StringBuilder sb, int c) {
        final char[] HEX = "0123456789abcdef".toCharArray();
        sb.append(HEX[(c >> 12) & 0xF]);
        sb.append(HEX[(c >> 8) & 0xF]);
        sb.append(HEX[(c >> 4) & 0xF]);
        sb.append(HEX[c & 0xF]);
    }

    // ===================================================================== //
    // Parser
    // ===================================================================== //

    private static final class Parser {
        final String s;
        int pos;

        Parser(String s) { this.s = s; this.pos = 0; }

        boolean atEnd() { return pos >= s.length(); }

        void skipWs() {
            while (pos < s.length()) {
                char c = s.charAt(pos);
                if (c == ' ' || c == '\t' || c == '\n' || c == '\r') pos++;
                else break;
            }
        }

        Object parseValue(int depth) {
            if (depth > MAX_DEPTH) throw new JsonException("max depth exceeded while parsing");
            skipWs();
            if (atEnd()) throw new JsonException("unexpected end of input");
            char c = s.charAt(pos);
            switch (c) {
                case '{': return parseObject(depth);
                case '[': return parseArray(depth);
                case '"': return parseString();
                case 't': case 'f': return parseBoolean();
                case 'n': return parseNull();
                default:
                    if (c == '-' || (c >= '0' && c <= '9')) return parseNumber();
                    throw new JsonException("unexpected character '" + c + "' at index " + pos);
            }
        }

        Object parseObject(int depth) {
            expect('{');
            Map<String, Object> map = new LinkedHashMap<>();
            skipWs();
            if (peek() == '}') { pos++; return map; }
            while (true) {
                skipWs();
                if (peek() != '"') throw new JsonException("expected string key at index " + pos);
                String key = parseString();
                skipWs();
                expect(':');
                Object val = parseValue(depth + 1);
                map.put(key, val); // duplicate keys: last wins
                skipWs();
                char c = next();
                if (c == '}') break;
                if (c != ',') throw new JsonException("expected ',' or '}' at index " + (pos - 1));
            }
            return map;
        }

        Object parseArray(int depth) {
            expect('[');
            List<Object> list = new ArrayList<>();
            skipWs();
            if (peek() == ']') { pos++; return list; }
            while (true) {
                Object val = parseValue(depth + 1);
                list.add(val);
                skipWs();
                char c = next();
                if (c == ']') break;
                if (c != ',') throw new JsonException("expected ',' or ']' at index " + (pos - 1));
            }
            return list;
        }

        String parseString() {
            expect('"');
            StringBuilder sb = new StringBuilder();
            while (true) {
                if (atEnd()) throw new JsonException("unterminated string");
                char c = s.charAt(pos++);
                if (c == '"') break;
                if (c == '\\') {
                    if (atEnd()) throw new JsonException("unterminated escape");
                    char e = s.charAt(pos++);
                    switch (e) {
                        case '"':  sb.append('"'); break;
                        case '\\': sb.append('\\'); break;
                        case '/':  sb.append('/'); break;
                        case 'b':  sb.append('\b'); break;
                        case 'f':  sb.append('\f'); break;
                        case 'n':  sb.append('\n'); break;
                        case 'r':  sb.append('\r'); break;
                        case 't':  sb.append('\t'); break;
                        case 'u':  sb.append(parseHex4()); break;
                        default: throw new JsonException("invalid escape \\" + e + " at index " + (pos - 1));
                    }
                } else if (c < 0x20) {
                    throw new JsonException("unescaped control char U+"
                            + Integer.toHexString(c) + " in string");
                } else {
                    // Pass through any literal char, including raw UTF-16 surrogate
                    // pairs from a UTF-8 source — they re-pair correctly in String.
                    sb.append(c);
                }
            }
            return sb.toString();
        }

        char parseHex4() {
            if (pos + 4 > s.length()) throw new JsonException("truncated \\u escape");
            int v = 0;
            for (int i = 0; i < 4; i++) {
                char h = s.charAt(pos++);
                int d;
                if (h >= '0' && h <= '9') d = h - '0';
                else if (h >= 'a' && h <= 'f') d = h - 'a' + 10;
                else if (h >= 'A' && h <= 'F') d = h - 'A' + 10;
                else throw new JsonException("bad hex digit '" + h + "' in \\u escape");
                v = (v << 4) | d;
            }
            return (char) v; // surrogate halves recombine naturally in the StringBuilder
        }

        Object parseNumber() {
            int start = pos;
            boolean isDouble = false;
            if (peek() == '-') pos++;
            // Reject the non-standard "-Infinity" form early.
            if (!atEnd() && s.charAt(pos) == 'I') {
                throw new JsonException("Infinity is not valid JSON at index " + start);
            }
            while (!atEnd()) {
                char c = s.charAt(pos);
                if (c >= '0' && c <= '9') {
                    pos++;
                } else if (c == '.' || c == 'e' || c == 'E' || c == '+' || c == '-') {
                    isDouble = true;
                    pos++;
                } else {
                    break;
                }
            }
            String num = s.substring(start, pos);
            try {
                if (isDouble) {
                    double d = Double.parseDouble(num);
                    if (Double.isNaN(d) || Double.isInfinite(d)) {
                        throw new JsonException("non-finite number '" + num + "'");
                    }
                    return d;
                }
                return Long.parseLong(num);
            } catch (NumberFormatException ex) {
                // Long overflow on an integral literal -> fall back to Double.
                if (!isDouble) {
                    try { return Double.parseDouble(num); }
                    catch (NumberFormatException ignored) { /* fall through */ }
                }
                throw new JsonException("invalid number '" + num + "' at index " + start);
            }
        }

        Object parseBoolean() {
            if (s.startsWith("true", pos)) { pos += 4; return Boolean.TRUE; }
            if (s.startsWith("false", pos)) { pos += 5; return Boolean.FALSE; }
            throw new JsonException("invalid literal at index " + pos);
        }

        Object parseNull() {
            if (s.startsWith("null", pos)) { pos += 4; return null; }
            // Reject "NaN" explicitly for a clear message (starts with 'N' not 'n',
            // so it won't reach here, but guard the lowercase confusion anyway).
            throw new JsonException("invalid literal at index " + pos);
        }

        // -- low-level cursor helpers -- //
        char peek() {
            if (atEnd()) throw new JsonException("unexpected end of input");
            return s.charAt(pos);
        }

        char next() {
            if (atEnd()) throw new JsonException("unexpected end of input");
            return s.charAt(pos++);
        }

        void expect(char c) {
            char got = next();
            if (got != c) throw new JsonException("expected '" + c + "' but got '" + got + "' at index " + (pos - 1));
        }
    }
}
