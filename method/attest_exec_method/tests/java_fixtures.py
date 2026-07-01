"""Reusable hand-filled Java harness holes for tests.

These let tests exercise the executor and protocol WITHOUT calling the LLM, so
the offline suite is deterministic and free. Each entry is a dict of holes ready
for :func:`attest.harness_fill.fill_template`.
"""

from __future__ import annotations

# A pure value-returning snippet: sum of an int array (mode=return).
SUM_HOLES = {
    "SNIPPET": r"""
    static int sum(int[] a) {
        int s = 0;
        for (int x : a) s += x;
        return s;
    }
""",
    "SETUP": r"""
        java.util.List<Object> arr = Json.asList(args.get("arr"));
        int[] a = new int[arr.size()];
        for (int i = 0; i < a.length; i++) a[i] = (int) Json.asLong(arr.get(i));
        return new Env(caseDir).put("a", a);
""",
    "INVOKE": r"""
        return sum((int[]) env.get("a"));
""",
    "OBSERVE": r"""
        return returnValue;
""",
}

# A snippet that throws on a poison flag, to test structured error capture.
THROW_HOLES = {
    "SNIPPET": r"""
    static int firstElem(int[] a) {
        return a[0]; // AIOOBE on empty array
    }
""",
    "SETUP": r"""
        java.util.List<Object> arr = Json.asList(args.get("arr"));
        int[] a = new int[arr.size()];
        for (int i = 0; i < a.length; i++) a[i] = (int) Json.asLong(arr.get(i));
        return new Env(caseDir).put("a", a);
""",
    "INVOKE": r"""
        return firstElem((int[]) env.get("a"));
""",
    "OBSERVE": r"""
        return returnValue;
""",
}

# A side-effecting file copy: observe the destination file bytes (mode=artifact).
COPY_HOLES = {
    "SNIPPET": r"""
    static void copyBytes(java.io.File src, java.io.File dst) throws Exception {
        try (java.io.InputStream in = new java.io.FileInputStream(src);
             java.io.OutputStream out = new java.io.FileOutputStream(dst)) {
            int b;
            while ((b = in.read()) != -1) out.write(b);
        }
    }
""",
    "SETUP": r"""
        byte[] srcBytes = java.util.Base64.getDecoder().decode(
                Json.asString(args.get("src_b64")));
        java.nio.file.Path src = caseDir.resolve("src.bin");
        java.nio.file.Path dst = caseDir.resolve("dst.bin");
        java.nio.file.Files.write(src, srcBytes);
        return new Env(caseDir).put("src", src.toFile()).put("dst", dst.toFile());
""",
    "INVOKE": r"""
        copyBytes((java.io.File) env.get("src"), (java.io.File) env.get("dst"));
        return Env.NO_RETURN;
""",
    "OBSERVE": r"""
        java.io.File dst = (java.io.File) env.get("dst");
        if (!dst.exists()) return Env.NO_RETURN;
        return java.nio.file.Files.readAllBytes(dst.toPath());
""",
}

# An infinite loop to exercise the wall-clock timeout + process-tree kill.
INFLOOP_HOLES = {
    "SNIPPET": r"""
    static void spin() { while (true) { /* burn */ } }
""",
    "SETUP": r"""
        return new Env(caseDir);
""",
    "INVOKE": r"""
        spin();
        return Env.NO_RETURN;
""",
    "OBSERVE": r"""
        return Env.NO_RETURN;
""",
}
