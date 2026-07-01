"""Real case-study pairs from BigCloneBench, baked as fixtures.

These are the primary correctness gate for the pipeline:
  * CASE_2284 — copyResource (hand-written byte loop) vs copyFromTo (NIO
    transferTo). BCB labels these clones; GraphCodeBERT misses it (token
    Jaccard 0.12). Expected pipeline verdict: CLONE, via destination-file bytes.
  * ANAGRAM   — a full-Unicode anagram check vs an ASCII-128-only one. Equivalent
    on ASCII inputs but the ASCII-only version throws on non-ASCII (é). Expected:
    a behavioral divergence surfaced on the non-ASCII case.
"""

from __future__ import annotations

from attest.schemas import Pair, Snippet

# --------------------------------------------------------------------------- #
# Case 2284: file-copy clones with completely different implementations.
# --------------------------------------------------------------------------- #

_COPY_A = r"""
private void copyResource() throws Exception {
    URL url = getResource(source);
    InputStream input;
    if (url != null) {
        input = url.openStream();
    } else if (new File(source).exists()) {
        input = new FileInputStream(source);
    } else {
        throw new Exception("Could not load resource: " + source);
    }
    OutputStream output = new FileOutputStream(destinationFile());
    int b;
    while ((b = input.read()) != -1) output.write(b);
    input.close();
    output.close();
}
""".strip()

_COPY_B = r"""
public static void copyFromTo(File srcFile, File destFile) {
    FileChannel in = null, out = null;
    FileInputStream fis = null;
    FileOutputStream fos = null;
    try {
        fis = new FileInputStream(srcFile);
    } catch (FileNotFoundException fnfe) {
        System.out.println("File: " + srcFile.toString());
        System.exit(-1);
    }
    try {
        fos = new FileOutputStream(destFile);
    } catch (FileNotFoundException fnfe) {
        System.out.println("File: " + destFile.toString());
        System.exit(-1);
    }
    try {
        in = fis.getChannel();
        out = fos.getChannel();
        in.transferTo(0, in.size(), out);
        fos.flush();
        fos.close();
        out.close();
        fis.close();
        in.close();
    } catch (IOException ioe) {
        System.out.println("IOException copying file: " + ioe.getMessage());
        System.exit(-1);
    }
    long srcModified = srcFile.lastModified();
    if (srcModified > 0L && destFile.exists()) {
        destFile.setLastModified(srcModified);
    }
}
""".strip()

CASE_2284 = Pair(
    pair_id="bcb_2284",
    a=Snippet(id="3584508", code=_COPY_A, language="java"),
    b=Snippet(id="16557837", code=_COPY_B, language="java"),
    label=1,
    meta={"source": "BigCloneBench", "case_id": 2284, "note": "GraphCodeBERT FN"},
)

# --------------------------------------------------------------------------- #
# Anagram: full-Unicode vs ASCII-128-only (hidden input-domain divergence).
# --------------------------------------------------------------------------- #

_ANAGRAM_FULL = r"""
public static boolean isAnagram(String s, String t) {
    if (s.length() != t.length()) return false;
    java.util.HashMap<Character, Integer> count = new java.util.HashMap<>();
    for (int i = 0; i < s.length(); i++) {
        count.merge(s.charAt(i), 1, Integer::sum);
    }
    for (int i = 0; i < t.length(); i++) {
        Integer c = count.get(t.charAt(i));
        if (c == null || c == 0) return false;
        count.put(t.charAt(i), c - 1);
    }
    return true;
}
""".strip()

_ANAGRAM_ASCII = r"""
public static boolean isAnagram(String s, String t) {
    if (s.length() != t.length()) return false;
    int[] count = new int[128];
    for (int i = 0; i < s.length(); i++) {
        count[s.charAt(i)]++;
        count[t.charAt(i)]--;
    }
    for (int c : count) if (c != 0) return false;
    return true;
}
""".strip()

ANAGRAM = Pair(
    pair_id="anagram_unicode",
    a=Snippet(id="anagram_full", code=_ANAGRAM_FULL, language="java"),
    b=Snippet(id="anagram_ascii", code=_ANAGRAM_ASCII, language="java"),
    label=0,  # they diverge on non-ASCII; treated as a behavioral-difference probe
    meta={"source": "observation", "note": "ASCII-only crashes on non-ASCII"},
)
