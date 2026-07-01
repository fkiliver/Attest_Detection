// json.hpp — a tiny, dependency-free JSON value type for Attest C/C++
// harnesses. Mirrors the responsibilities of the Java Json.java: parse a JSON
// document into a value tree and serialize back, with UTF-8 strings escaped as
// \uXXXX (>= 0x7F), integral vs floating numbers kept distinct, and bounded
// recursion depth. This is INFRASTRUCTURE — the generated harness may use it but
// must not modify it.
//
// Compiled as C++17. Single header, no external dependencies.

#ifndef ATTEST_JSON_HPP
#define ATTEST_JSON_HPP

#include <cstdint>
#include <cmath>
#include <map>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace scx {

class JsonValue;
using JsonArray = std::vector<JsonValue>;
// Preserve insertion order like the Java LinkedHashMap: a vector of pairs.
using JsonObject = std::vector<std::pair<std::string, JsonValue>>;

class JsonError : public std::runtime_error {
 public:
  explicit JsonError(const std::string& m) : std::runtime_error(m) {}
};

class JsonValue {
 public:
  enum class Type { Null, Bool, Int, Double, String, Array, Object };

  JsonValue() : type_(Type::Null) {}
  static JsonValue null() { return JsonValue(); }
  static JsonValue boolean(bool b) { JsonValue v; v.type_ = Type::Bool; v.bool_ = b; return v; }
  static JsonValue integer(long long n) { JsonValue v; v.type_ = Type::Int; v.int_ = n; return v; }
  static JsonValue number(double d) { JsonValue v; v.type_ = Type::Double; v.dbl_ = d; return v; }
  static JsonValue str(const std::string& s) { JsonValue v; v.type_ = Type::String; v.str_ = s; return v; }
  static JsonValue array() { JsonValue v; v.type_ = Type::Array; return v; }
  static JsonValue object() { JsonValue v; v.type_ = Type::Object; return v; }

  Type type() const { return type_; }
  bool is_null() const { return type_ == Type::Null; }

  bool as_bool() const { require(Type::Bool); return bool_; }
  long long as_int() const {
    if (type_ == Type::Int) return int_;
    if (type_ == Type::Double) return static_cast<long long>(dbl_);
    throw JsonError("not an int");
  }
  double as_double() const {
    if (type_ == Type::Double) return dbl_;
    if (type_ == Type::Int) return static_cast<double>(int_);
    throw JsonError("not a number");
  }
  const std::string& as_string() const { require(Type::String); return str_; }
  JsonArray& arr() { require(Type::Array); return arr_; }
  const JsonArray& arr() const { require(Type::Array); return arr_; }
  JsonObject& obj() { require(Type::Object); return obj_; }
  const JsonObject& obj() const { require(Type::Object); return obj_; }

  // Object lookup by key (returns nullptr if absent). Last-wins on duplicates is
  // handled at parse time.
  const JsonValue* find(const std::string& key) const {
    if (type_ != Type::Object) return nullptr;
    const JsonValue* hit = nullptr;
    for (const auto& kv : obj_) if (kv.first == key) hit = &kv.second;
    return hit;
  }
  void set(const std::string& key, JsonValue v) {
    require(Type::Object);
    for (auto& kv : obj_) { if (kv.first == key) { kv.second = std::move(v); return; } }
    obj_.emplace_back(key, std::move(v));
  }
  void push_back(JsonValue v) { require(Type::Array); arr_.push_back(std::move(v)); }

  std::string dump() const { std::string out; write(out, 0); return out; }

  static JsonValue parse(const std::string& text) {
    Parser p(text);
    p.skip_ws();
    JsonValue v = p.parse_value(0);
    p.skip_ws();
    if (!p.at_end()) throw JsonError("trailing content in JSON");
    return v;
  }

 private:
  static constexpr int kMaxDepth = 200;
  Type type_;
  bool bool_ = false;
  long long int_ = 0;
  double dbl_ = 0.0;
  std::string str_;
  JsonArray arr_;
  JsonObject obj_;

  void require(Type t) const {
    if (type_ != t) throw JsonError("json type mismatch");
  }

  // ---- serialize ---- //
  void write(std::string& out, int depth) const {
    if (depth > kMaxDepth) throw JsonError("max depth exceeded (serialize)");
    switch (type_) {
      case Type::Null: out += "null"; break;
      case Type::Bool: out += (bool_ ? "true" : "false"); break;
      case Type::Int: out += std::to_string(int_); break;
      case Type::Double: {
        if (std::isnan(dbl_) || std::isinf(dbl_))
          throw JsonError("cannot serialize non-finite double");
        std::ostringstream ss;
        ss.precision(17);
        ss << dbl_;
        std::string s = ss.str();
        if (s.find('.') == std::string::npos && s.find('e') == std::string::npos &&
            s.find('E') == std::string::npos)
          s += ".0";
        out += s;
        break;
      }
      case Type::String: write_string(out, str_); break;
      case Type::Array: {
        out += '[';
        for (size_t i = 0; i < arr_.size(); ++i) {
          if (i) out += ',';
          arr_[i].write(out, depth + 1);
        }
        out += ']';
        break;
      }
      case Type::Object: {
        out += '{';
        bool first = true;
        for (const auto& kv : obj_) {
          if (!first) out += ',';
          first = false;
          write_string(out, kv.first);
          out += ':';
          kv.second.write(out, depth + 1);
        }
        out += '}';
        break;
      }
    }
  }

  static void write_string(std::string& out, const std::string& s) {
    static const char* HEX = "0123456789abcdef";
    out += '"';
    size_t i = 0;
    while (i < s.size()) {
      unsigned char c = static_cast<unsigned char>(s[i]);
      if (c == '"') { out += "\\\""; ++i; }
      else if (c == '\\') { out += "\\\\"; ++i; }
      else if (c == '\b') { out += "\\b"; ++i; }
      else if (c == '\f') { out += "\\f"; ++i; }
      else if (c == '\n') { out += "\\n"; ++i; }
      else if (c == '\r') { out += "\\r"; ++i; }
      else if (c == '\t') { out += "\\t"; ++i; }
      else if (c < 0x20) {
        out += "\\u00"; out += HEX[(c >> 4) & 0xF]; out += HEX[c & 0xF]; ++i;
      } else if (c < 0x80) {
        out += static_cast<char>(c); ++i;
      } else {
        // Decode one UTF-8 code point and emit \uXXXX (with surrogate pair for
        // code points above U+FFFF), so output is pure ASCII and charset-proof.
        uint32_t cp = 0; int n = 0;
        if ((c & 0xE0) == 0xC0) { cp = c & 0x1F; n = 1; }
        else if ((c & 0xF0) == 0xE0) { cp = c & 0x0F; n = 2; }
        else if ((c & 0xF8) == 0xF0) { cp = c & 0x07; n = 3; }
        else { cp = 0xFFFD; n = 0; }  // invalid lead byte
        ++i;
        for (int k = 0; k < n && i < s.size(); ++k, ++i)
          cp = (cp << 6) | (static_cast<unsigned char>(s[i]) & 0x3F);
        emit_u(out, cp, HEX);
      }
    }
    out += '"';
  }

  static void emit_u(std::string& out, uint32_t cp, const char* HEX) {
    auto u4 = [&](uint32_t x) {
      out += "\\u";
      out += HEX[(x >> 12) & 0xF]; out += HEX[(x >> 8) & 0xF];
      out += HEX[(x >> 4) & 0xF]; out += HEX[x & 0xF];
    };
    if (cp > 0xFFFF) {
      cp -= 0x10000;
      u4(0xD800 + (cp >> 10));
      u4(0xDC00 + (cp & 0x3FF));
    } else {
      u4(cp);
    }
  }

  // ---- parse ---- //
  struct Parser {
    const std::string& s;
    size_t pos = 0;
    explicit Parser(const std::string& str) : s(str) {}
    bool at_end() const { return pos >= s.size(); }
    void skip_ws() {
      while (pos < s.size()) {
        char c = s[pos];
        if (c == ' ' || c == '\t' || c == '\n' || c == '\r') ++pos; else break;
      }
    }
    char peek() { if (at_end()) throw JsonError("unexpected end"); return s[pos]; }
    char next() { if (at_end()) throw JsonError("unexpected end"); return s[pos++]; }
    void expect(char c) { if (next() != c) throw JsonError(std::string("expected ") + c); }

    JsonValue parse_value(int depth) {
      if (depth > kMaxDepth) throw JsonError("max depth exceeded (parse)");
      skip_ws();
      char c = peek();
      if (c == '{') return parse_object(depth);
      if (c == '[') return parse_array(depth);
      if (c == '"') return JsonValue::str(parse_string());
      if (c == 't' || c == 'f') return parse_bool();
      if (c == 'n') { expect_lit("null"); return JsonValue::null(); }
      if (c == '-' || (c >= '0' && c <= '9')) return parse_number();
      throw JsonError(std::string("unexpected char ") + c);
    }
    JsonValue parse_object(int depth) {
      expect('{');
      JsonValue v = JsonValue::object();
      skip_ws();
      if (peek() == '}') { ++pos; return v; }
      while (true) {
        skip_ws();
        if (peek() != '"') throw JsonError("expected string key");
        std::string key = parse_string();
        skip_ws();
        expect(':');
        v.set(key, parse_value(depth + 1));  // set() => last-wins
        skip_ws();
        char c = next();
        if (c == '}') break;
        if (c != ',') throw JsonError("expected , or }");
      }
      return v;
    }
    JsonValue parse_array(int depth) {
      expect('[');
      JsonValue v = JsonValue::array();
      skip_ws();
      if (peek() == ']') { ++pos; return v; }
      while (true) {
        v.push_back(parse_value(depth + 1));
        skip_ws();
        char c = next();
        if (c == ']') break;
        if (c != ',') throw JsonError("expected , or ]");
      }
      return v;
    }
    std::string parse_string() {
      expect('"');
      std::string out;
      while (true) {
        if (at_end()) throw JsonError("unterminated string");
        char c = s[pos++];
        if (c == '"') break;
        if (c == '\\') {
          char e = next();
          switch (e) {
            case '"': out += '"'; break;
            case '\\': out += '\\'; break;
            case '/': out += '/'; break;
            case 'b': out += '\b'; break;
            case 'f': out += '\f'; break;
            case 'n': out += '\n'; break;
            case 'r': out += '\r'; break;
            case 't': out += '\t'; break;
            case 'u': append_utf8(out, parse_hex4()); break;
            default: throw JsonError("bad escape");
          }
        } else {
          out += c;  // pass-through raw UTF-8 bytes
        }
      }
      return out;
    }
    uint32_t parse_hex4() {
      uint32_t cp = read_hex4();
      // Combine a surrogate pair if present.
      if (cp >= 0xD800 && cp <= 0xDBFF && pos + 1 < s.size() &&
          s[pos] == '\\' && s[pos + 1] == 'u') {
        pos += 2;
        uint32_t lo = read_hex4();
        cp = 0x10000 + ((cp - 0xD800) << 10) + (lo - 0xDC00);
      }
      return cp;
    }
    uint32_t read_hex4() {
      if (pos + 4 > s.size()) throw JsonError("truncated \\u");
      uint32_t v = 0;
      for (int i = 0; i < 4; ++i) {
        char h = s[pos++];
        v <<= 4;
        if (h >= '0' && h <= '9') v |= (h - '0');
        else if (h >= 'a' && h <= 'f') v |= (h - 'a' + 10);
        else if (h >= 'A' && h <= 'F') v |= (h - 'A' + 10);
        else throw JsonError("bad hex digit");
      }
      return v;
    }
    static void append_utf8(std::string& out, uint32_t cp) {
      if (cp < 0x80) out += static_cast<char>(cp);
      else if (cp < 0x800) {
        out += static_cast<char>(0xC0 | (cp >> 6));
        out += static_cast<char>(0x80 | (cp & 0x3F));
      } else if (cp < 0x10000) {
        out += static_cast<char>(0xE0 | (cp >> 12));
        out += static_cast<char>(0x80 | ((cp >> 6) & 0x3F));
        out += static_cast<char>(0x80 | (cp & 0x3F));
      } else {
        out += static_cast<char>(0xF0 | (cp >> 18));
        out += static_cast<char>(0x80 | ((cp >> 12) & 0x3F));
        out += static_cast<char>(0x80 | ((cp >> 6) & 0x3F));
        out += static_cast<char>(0x80 | (cp & 0x3F));
      }
    }
    JsonValue parse_bool() {
      if (s.compare(pos, 4, "true") == 0) { pos += 4; return JsonValue::boolean(true); }
      if (s.compare(pos, 5, "false") == 0) { pos += 5; return JsonValue::boolean(false); }
      throw JsonError("invalid literal");
    }
    void expect_lit(const char* lit) {
      size_t n = std::char_traits<char>::length(lit);
      if (s.compare(pos, n, lit) != 0) throw JsonError("invalid literal");
      pos += n;
    }
    JsonValue parse_number() {
      size_t start = pos;
      bool is_double = false;
      if (peek() == '-') ++pos;
      if (!at_end() && s[pos] == 'I') throw JsonError("Infinity not allowed");
      while (!at_end()) {
        char c = s[pos];
        if (c >= '0' && c <= '9') ++pos;
        else if (c == '.' || c == 'e' || c == 'E' || c == '+' || c == '-') { is_double = true; ++pos; }
        else break;
      }
      std::string num = s.substr(start, pos - start);
      try {
        if (is_double) return JsonValue::number(std::stod(num));
        return JsonValue::integer(std::stoll(num));
      } catch (const std::out_of_range&) {
        return JsonValue::number(std::stod(num));  // overflow -> double
      } catch (const std::exception&) {
        throw JsonError("invalid number");
      }
    }
  };
};

}  // namespace scx

#endif  // ATTEST_JSON_HPP
