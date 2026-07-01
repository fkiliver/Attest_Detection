# Error Case Studies 6001-6500

- Source model: `configured-llm`
- Cases: `6001` to `6500`

### case_id=6001 FN partial_functionality

- 方法: `login` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into a service by sending credentials via POST and returns a session ID.
- B 摘要: Checks for a newer version of an application by reading a URL and comparing build numbers.
- 静态失败原因: Static BERT models rely on token overlap and may be misled by low Jaccard similarity and distinct domain-specific tokens (e.g., 'email', 'LOLA' vs 'version', 'jEdit'), failing to recognize the shared structural pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones due to similar control flow: URL connection, buffered reading, line parsing, and exception handling, reflecting Type-3/4 structural similarity despite different intents.
- 共享行为: Open a URL connection；Read lines using BufferedReader from an InputStream；Parse data from lines；Handle exceptions with try-catch
- 行为差异: function_a uses POST with data; function_b uses GET；function_a parses a session ID; function_b parses version and build numbers；function_a returns a string; function_b returns void；function_a has side effect setting session; function_b shows GUI messages
- 修正建议: Incorporate structural features like AST or data flow graphs；Use contrastive learning with clone pairs having low lexical but high structural similarity；Augment training data with broad Type-3/4 clones from BCB

### case_id=6002 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies its endpoint, and saves to a temporary file, returning the file path.
- B 摘要: Copies a file from a source to a target using a file channel.
- 静态失败原因: Low token overlap (0.125) and different structure (long method with XML processing vs short method) made it hard for static BERT to capture the shared channel pattern as semantically similar.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these Type-4 clones because they share the core functionality of channel-based file transfer, which is a distinct and reusable pattern, even though surrounding logic differs.
- 共享行为: Both use FileChannel to transfer data between streams；Both involve file I/O operations
- 行为差异: A downloads from URL and processes XML; B only copies a local file；A has multiple exception handling; B only throws IOException；A returns file path; B is void；A uses transferFrom; B uses transferTo
- 修正建议: Incorporate dataflow analysis to detect channel usage patterns；Add attention to long-range dependencies in method bodies；Use program slicing to isolate shared partial functionality

### case_id=6003 FN partial_functionality

- 方法: `encodeFileToFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Encodes a file using Base64 and copies it to another file, returning success status.
- B 摘要: Builds a website for editing by applying XSLT transformations and inserting control files, writing the resulting pages.
- 静态失败原因: The model likely relied on lexical overlap (very low Jaccard) and method signatures, missing the subtle I/O pattern similarity that BCB considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled them as clones based on shared file I/O and exception handling patterns, though the core functionality differs significantly.
- 共享行为: Both perform file I/O using buffered streams；Both handle IOException and close streams in finally blocks
- 行为差异: A is a simple base64 encode-copy; B involves multiple file reads, XML transformations, string manipulation, and writes multiple output files；B has complex logic for page iteration and transformation, while A has a single read-write loop
- 修正建议: Incorporate control flow and data dependency features；Use better representation of high-level operations；Train on more fine-grained clone types like those in BigCloneBench

### case_id=6004 FP lexical_or_api_overlap

- 方法: `downloadURLtoString` vs `readScalarpvviewerDocument`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads the content of a URL as a single string by reading all lines.
- B 摘要: Reads and parses a specific XML document from a URL to configure a scalar PV viewer UI.
- 静态失败原因: Static BERT models may overemphasize shared lexical tokens (e.g., URL, BufferedReader, readLine) and initial structural similarity, missing the vast semantic difference in the rest of the code.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions serve entirely different purposes; the common URL-reading boilerplate is trivial and not considered a clone by human judges.
- 共享行为: Both open a URL and read lines using BufferedReader.
- 行为差异: A returns the concatenated string; B parses XML, updates UI components, and has complex error handling.；A reads all lines as-is; B filters out comments and stops at a specific token.；A is generic; B is application-specific with many side effects.
- 修正建议: Train models to ignore or downweight common I/O boilerplate patterns.；Incorporate task-level semantic understanding or longer-range dependencies.

### case_id=6005 FP boilerplate_overlap

- 方法: `main` vs `testReadPerMemberSixSmall`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.99`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that generates adapter classes from a Prolog file using a complex pipeline.
- B 摘要: Test method that reads small GZIP members from a byte array and validates the number of bytes read.
- 静态失败原因: Static BERT may have been misled by common boilerplate patterns (e.g., method signature, try-catch, loop structure) and a few overlapping keywords like 'IOException', despite very low token Jaccard.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have no overlapping functionality; one is a main method for generation, the other a unit test for I/O.
- 共享行为: Both use I/O streams
- 行为差异: Complete difference in purpose: adapter generation vs. GZIP reading test；Different libraries and APIs used；Different control flow and exception handling
- 修正建议: Increase sensitivity to specific API calls and domain keywords；Improve context capturing beyond local patterns；Use more diverse training examples with fine-grained structural differences

### case_id=6006 FP long_range_semantics

- 方法: `doGet` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET by forwarding request to a Fedora URL and copying response headers and body.
- B 摘要: Reads configuration data from a file to initialize various sets and hash maps for Tibetan transliteration.
- 静态失败原因: Static BERT might have overfitted on structural similarities like loops and method calls, or failed to capture the high-level semantic context due to long and complex code.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone due to completely different domain and purpose; no shared functionality beyond trivial I/O patterns.
- 共享行为: Both use InputStream and I/O operations；Both have loops iterating over data
- 行为差异: Function A is a servlet method for HTTP proxying, Function B is a private static initialization method；Function A uses URL and HttpURLConnection, Function B uses StringTokenizer and file reading；Function A copies HTTP response, Function B populates data structures for transliteration
- 修正建议: Improve model capacity to capture global program semantics；Use data flow or control flow features；Increase training data diversity for non-clone pairs with similar superficial patterns

### case_id=6007 FP lexical_or_api_overlap

- 方法: `loadExistingAntlibs` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads antlib definitions from classloader resources by reading lines and resolving URIs.
- B 摘要: Downloads content from a URL to a temporary file, optionally with authentication, and updates a status label.
- 静态失败原因: The model likely overemphasized the shared lexical tokens (BufferedReader, InputStreamReader, readLine, URL) and similar while-loop structure, missing the semantic divergence in purpose and output behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotations would likely reject this pair as clones because the overall functionality is entirely different (loading antlib definitions vs downloading a file), even though both read lines from streams.
- 共享行为: Both iterate over lines read from an input stream via BufferedReader
- 行为差异: Function A resolves antlib URIs and calls loadAntLib for each entry, while B writes lines to a temporary file；Function B has authentication handling and progressive status updates, absent in A；Function A handles classloader resource enumeration; B handles a single URL connection；Function A uses URL.openStream; B uses URLConnection with authentication
- 修正建议: Incorporate method name semantics and broader context；Use dataflow analysis to track how read data is processed (e.g., URI resolution vs file write)；Add features capturing the side effects and return values of the functions

### case_id=6008 FN partial_functionality

- 方法: `readRemoteFile` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a remote file line by line and returns its entire content as a string.
- B 摘要: Opens a file or URL stream and calls an overloaded read method, returning a status code.
- 静态失败原因: Static BERT methods like CodeBERT rely on token embeddings and context; they may not capture the high-level semantic difference between returning content vs returning status, and may be misled by overlapping tokens like 'URL', 'InputStream', 'IOException'.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB possibly considered both as 'reading from a URL' and handling IO exceptions, ignoring differences in return type and higher-level purpose.
- 共享行为: Both open a URL stream (though method B also handles local files)；Both handle IOException
- 行为差异: Return type: String vs int；Method A concatenates lines; method B delegates to another read method；Method A explicitly reads lines; method B likely reads bytes；Method A only reads remote; method B reads both local and remote
- 修正建议: Improve model's ability to distinguish return types and final purpose；Inject dataflow information to see that method A builds a string from lines while method B returns an integer status；Use larger context or method-level contrastive learning

### case_id=6009 FN partial_functionality

- 方法: `getHTML` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a URL with given encoding and optionally writes it to a file.
- B 摘要: Fetches content from a hardcoded URL and logs the result.
- 静态失败原因: Low token Jaccard (0.27), different method signatures, return types, and control flow branches cause the model to miss the shared reading pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers functions that perform the same core task (reading URL content) as clones, even with variations in parameters, return type, and output handling.
- 共享行为: Both open a URL connection and read its content line by line into a string buffer.
- 行为差异: A uses HttpURLConnection with a User-Agent header, while B uses URLConnection with no custom headers.；A handles exceptions by printing stack trace, while B throws Exception.；A optionally writes the content to a file, while B logs it via log.debug.；A returns the string, B is void.
- 修正建议: Abstract functions to remove parameter and return type differences.；Use code summarization to capture the shared intent of reading URL content.；Ignore logging and file writing branches during matching.

### case_id=6010 FP boilerplate_overlap

- 方法: `main` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method for an adapter generator that reads a Prolog file, parses it, generates adapter classes and writes them to a JAR file.
- B 摘要: Main method that reads a log file and writes a filtered subset of lines to a new file at regular intervals.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on common structural patterns (main method, try-catch, file reading/writing, argument parsing) and missed the deep semantic differences due to lack of understanding of the specific APIs and logic flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically considers clones as functions that implement the same algorithm or similar functionality. Here, despite both being main methods, the algorithms and purposes are entirely different, so BCB labels them as non-clones.
- 共享行为: Both are main methods that parse command-line arguments；Both use file I/O operations；Both handle exceptions with printStackTrace
- 行为差异: Function A generates Java bytecode and assembles classes; Function B simply filters and writes text lines；Function A involves complex parsing and class generation; Function B does simple line-based processing；Function A uses many external libraries (Prolog parser, ASM); Function B uses only standard Java IO
- 修正建议: Train on more diverse functions to distinguish boilerplate from core functionality；Incorporate semantic embeddings that capture the purpose of the function beyond superficial patterns；Use data-flow analysis to detect differences in how data is transformed

### case_id=6011 FN benchmark_preference_bias

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its ZIP entries to files.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: The static model correctly predicted non-clone (0); it did not fail in this case. The BCB label 1 appears erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'file output' tasks, but the difference in functionality (download+extract vs copy) is substantial; likely a mislabel.
- 共享行为: Both perform file I/O operations；Both write to files using FileOutputStream
- 行为差异: A involves network download and ZIP extraction; B is a direct file copy；A writes multiple extracted entries; B writes a single file；A prints progress; B does not；B uses NIO channels; A uses traditional IO streams
- 修正建议: Re-evaluate BCB label for this pair; consider correcting to 0；Ensure benchmark consistency in clone definitions

### case_id=6012 FN partial_functionality

- 方法: `main` vs `retrieveTemplate`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Demonstrates a POST request with multiple parameters to a social network API and prints the response.
- B 摘要: Retrieves and caches a template string from a blog URL by reading its content.
- 静态失败原因: Static model likely relied on token overlap and structural similarity, which are low, missing the common pattern of URL connection and stream reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as functions that perform HTTP requests and read response data, sharing partial functionality under a broad Type-3/Type-4 clone category.
- 共享行为: Both establish a URL connection and read data from the input stream using BufferedReader.
- 行为差异: A sends a POST request with parameters; B sends a GET request.；A prints the response to stdout; B returns and caches the response.；A does not cache; B caches the result.；A has hardcoded parameters; B derives URL from blog info.
- 修正建议: Include richer context about API usage or data flow.；Use models that capture control and data flow across network operations.

### case_id=6013 FP partial_functionality

- 方法: `doVersionCheck` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for a new version of jEdit by reading a remote version file and comparing build numbers with the current build.
- B 摘要: Fetches the first line of content from a given URL and returns it as a string.
- 静态失败原因: The model may have been misled by overlapping low-level IO patterns (URL, BufferedReader, readLine) and similar structural skeleton, ignoring the contrasting high-level logic (version comparison, UI interaction vs. simple retrieval).
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels non-clones because the overall functionality is distinct: one is a version check with UI, the other is a simple content retrieval. Even though both involve URL reading, the purpose and surrounding logic differ significantly.
- 共享行为: Both open a URL and read text using BufferedReader and InputStreamReader
- 行为差异: A reads multiple lines looking for specific prefixes ('.version', '.build'), B reads only the first line；A compares version/build numbers and shows UI dialogs, B just returns the line；A handles IOException with user error message, B throws Exception；A shows/hides wait cursor on a View, B has no UI interaction
- 修正建议: Incorporate method-level context such as class name or surrounding methods to capture intent；Use contrastive learning on pairs that share IO but differ in ultimate purpose；Enhance model with data flow and control flow awareness to distinguish version checking from generic URL reading

### case_id=6014 FN benchmark_preference_bias

- 方法: `truncate` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Truncates and compresses old log files into zip archives after checking file age.
- B 摘要: Handles HTTP GET requests to display a portal page, including page retrieval, user permissions, logging, and caching.
- 静态失败原因: The static BERT/GraphCodeBERT model correctly identified these as non-clones due to very low token overlap (Jaccard=0.105) and entirely different contexts (logging vs. web serving). The model's prediction of 0 is accurate; the benchmark label appears to be erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled this as clone due to superficial similarities: both methods have file writing operations, use logging, and have try-catch blocks. However, the core semantics are completely different, and BCB's broad interpretation should still require similar functionality. Likely a mislabel in the benchmark.
- 共享行为: Both involve file operations (writing to zip vs. writing cache file)；Both use logging and exception handling；Both check conditions before proceeding with core logic
- 行为差异: Function A compresses a single file into a zip archive; B serves a dynamic web page；A operates on files; B operates on HTTP request/response objects；A is a short, focused file utility; B is a long servlet method with complex control flow；A's output is a zip file; B's output is HTML response
- 修正建议: Re-evaluate BCB label for this pair; likely should be 0；If keeping benchmark, include better filtering to avoid such false positives from boilerplate overlap

### case_id=6015 FN long_range_semantics

- 方法: `copyFile` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Handles an HTTP GET request by retrieving a page, checking permissions, logging, and optionally caching the output to a file.
- 静态失败原因: The functions have low token overlap and require understanding of long-range dependencies and external library context (e.g., servlet API) that static models often miss.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have considered both as involving file operations and resource management (try-finally), leading to a loose Type-4 or partial functionality similarity despite very different overall purposes.
- 共享行为: Both perform file I/O operations
- 行为差异: DoGet handles HTTP request and page logic; copyFile only copies files；DoGet involves user permission checks and logging; copyFile does not；CopyFile uses NIO channels; DoGet uses FileWriter
- 修正建议: Incorporate structural or dataflow analysis to capture high-level intent；Use method names and signatures as features to distinguish distinct operations；Include library call patterns to differentiate I/O handling in different contexts

### case_id=6016 FN lexical_or_api_overlap

- 方法: `setBundleInfoName` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL with bundle name mappings and updates a list of BundleInfo objects with the parsed names.
- B 摘要: Reads an OPDS catalog from a URL, handles pagination, downloads books XML, and invokes callback with parsed entries.
- 静态失败原因: Static BERT models may focus on overlapping tokens like URL, openStream, readLine, and miss divergent control flow and side effects.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as 'reading a URL and processing content', a generic Type-4 similarity, or the annotation may be noisy.
- 共享行为: Both open a URL and read input streams；Both parse text lines from the stream
- 行为差异: A returns boolean and modifies a list; B is void with side effects (downloads, callbacks)；A parses simple key=value lines; B parses OPDS XML with complex structure；B handles HTTP specifics (redirects, timeouts, content-disposition) and pagination
- 修正建议: Incorporate structural data flow (e.g., graph-based models)；Use pre-training on diverse clone types focusing on semantics

### case_id=6017 FN partial_functionality

- 方法: `issueCommandToServer` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends a command and capsule to a server via HTTP POST and returns the response as a string.
- B 摘要: Fetches content from a hardcoded URL via HTTP GET and logs the response.
- 静态失败原因: The low token Jaccard (0.23) due to different method names, URL strings, and the presence of write operations in A caused the model to miss the structural similarity of the read loop. The model likely focused on surface-level lexical differences rather than the common control flow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions implement the core behavior of reading content from a URL connection using a BufferedReader loop, which is a distinctive shared pattern. The additional write operations in A are seen as an extension of the same basic task.
- 共享行为: Open a URL connection；Read lines from the connection using BufferedReader into a StringBuffer；Close the BufferedReader
- 行为差异: A writes HTTP POST data (command and capsule), B does not write any data；A uses a field 'serverURL' for the connection, B uses a hardcoded URL string；A returns the response string, B logs it with log.debug()；A uses OutputStreamWriter and write operations, B does not
- 修正建议: Normalize method names and ignore constant strings；Use AST-based or graph-based features to capture structural patterns like the read loop；Add dataflow analysis to recognize that the core read operation is identical；Train on more examples where one function is a subset of another

### case_id=6018 FP long_range_semantics

- 方法: `getButtonSonido` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Creates a GUI button that triggers a file chooser to select and copy a sound file.
- B 摘要: Parses multiple configuration strings into sets and hash maps for Tibetan transliteration data.
- 静态失败原因: The static model likely overfitted on superficial lexical or structural similarities such as common Java keywords and exception handling patterns, missing the semantic gap.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels as non-clone because the two functions serve completely different purposes and share no meaningful functionality.
- 共享行为: Both involve file I/O operations；Both use try-catch for IOException
- 行为差异: Purpose: GUI interaction vs data initialization；Data structures: JButton, ImageIcon vs HashSet, HashMap；Control flow: event-driven vs sequential parsing
- 修正建议: Incorporate class-level context；Enhance model with data flow analysis；Include method name information

### case_id=6019 FN benchmark_preference_bias

- 方法: `readPage` vs `sendExceptionToServer`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads the content of a URL, optionally skipping lines that start with '#', and returns the concatenated lines as a string.
- B 摘要: Sends an exception report to a server by building a POST request with various encoded parameters, sending it, and reading the response to confirm success.
- 静态失败原因: Static BERT likely failed due to low token Jaccard similarity (0.135) and different API usage (openStream vs URLConnection). The model may not capture the high-level similarity of network I/O patterns and instead relies on lexical and structural cues that are quite different here.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider these clones under a broad Type-4 category because both involve network I/O: opening a URL, reading lines, and handling I/O. The annotators might have focused on the structural similarity of reading from a URL connection using BufferedReader rather than the functional purpose.
- 共享行为: Both open a URL connection and read from it using BufferedReader and InputStreamReader.；Both handle I/O operations and exceptions.；Both use StringBuilder or string concatenation for building data.；Both have loops reading lines from the input stream.
- 行为差异: Function A only reads from the URL, while function B first writes data to the URL connection and then reads the response.；Function A returns the page content, function B prints the response to console.；Function A optionally filters lines starting with '#', function B does no filtering.；Function B extensively uses URLEncoder to encode parameters, while A does not.
- 修正建议: Improve training data to include more diverse pairs that share only high-level API patterns but differ in specific functionality.；Enhance model with context-aware embeddings that capture the domain (e.g., network I/O) rather than exact token overlap.；Use graph-based representations that highlight similar control flow patterns like open-connection-read-close.

### case_id=6020 FP boilerplate_overlap

- 方法: `convert` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Converts an ACRNEMA file to DICOM by parsing pixel data, adding UIDs, and writing output with possible pixel data inflation.
- B 摘要: Handles ActionEvent for a settings dialog, saving preferences for tools like GraphViz and ImageMagick, and applying UI settings.
- 静态失败原因: Likely due to over-reliance on superficial structural patterns (e.g., try-finally, if-return, file I/O) and long method length, ignoring semantic context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clones because the functions serve entirely different purposes and have no overlapping functionality beyond generic Java boilerplate.
- 行为差异: Purpose: file format conversion vs. GUI event handling and preferences saving；Core logic: DICOM-specific parsing and metadata manipulation vs. file chooser dialogs and preference storage；Domain: medical imaging vs. application configuration
- 修正建议: Incorporate control flow and data dependency analysis；Use function call graphs to identify distinct API usage patterns；Apply domain-specific knowledge (e.g., DICOM vs. Swing) to separate concerns

### case_id=6021 FP boilerplate_overlap

- 方法: `digest` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes the MD5 digest of a string and returns the byte array.
- B 摘要: Processes an HTTP request to classify a concept by building XML, sending it to a URL, parsing the response, and forwarding to a result page.
- 静态失败原因: The static model likely overgeneralized due to the presence of common Java tokens (try-catch, return, String, etc.) and maybe the method name 'digest' which could be misinterpreted as related to 'perform'? But more likely the model has a bias towards predicting clones when both functions have similar control flow patterns (e.g., try-catch, variable initialization, return statement) even though their domain and specific operations are entirely different.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the two functions have completely different purposes: one is a cryptographic hash function, the other is a web request handler. BCB annotation typically requires some functional similarity, even for broad Type-4.
- 共享行为: Both are Java methods that perform some computation and return a value.
- 行为差异: Function A is a simple cryptographic hash utility; Function B is a complex web controller with session management, HTTP calls, and XML parsing.；Function A exits the JVM on error; Function B returns a fail forward.；Function A uses MessageDigest; Function B uses Struts, Servlet API, and custom beans.
- 修正建议: Improve model capacity to understand domain-specific APIs and semantics beyond lexical patterns.；Incorporate structural information such as data flow and control flow graphs to differentiate low-level operations.；Use method documentation or type information to disambiguate the purpose of methods.

### case_id=6022 FN partial_functionality

- 方法: `copyResource` vs `testReadHelloWorldTxt`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file using byte-by-byte streaming.
- B 摘要: Tests a content resolver by copying a classpath resource to a temp file, then reading it back via the resolver and asserting content.
- 静态失败原因: Low token overlap (0.09) and different method names/structures caused the model to miss the high-level similarity. The copy logic is embedded in different patterns (byte loop vs IOUtils library call) and the test method has additional assertions, reducing lexical and structural cues.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often accepts partial functionality clones where the core operation (resource copying) is shared, even if surrounding context differs. The test method essentially performs the same copy operation as part of its setup, making them functionally similar.
- 共享行为: Open an input stream from a resource；Open an output stream to a file；Copy bytes from input to output；Close both streams
- 行为差异: copyResource uses byte-by-byte loop; testReadHelloWorldTxt uses IOUtils.copy；testReadHelloWorldTxt has assertions and uses a custom resolver；copyResource is generic; testReadHelloWorldTxt is specific to a test scenario；copyResource handles URL vs file; testReadHelloWorldTxt reads from classpath
- 修正建议: Train on more examples of utility methods and test methods that share core functionality；Use graph-based representations to capture resource flow (input-output streams)；Incorporate type information and library calls (IOUtils.copy) as semantic hints

### case_id=6023 FN partial_functionality

- 方法: `encodeFileToFile` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Encodes a file to another file using Base64.
- B 摘要: Downloads a WSDL file from a URL, modifies its endpoint, and saves it locally.
- 静态失败原因: The model likely failed because it relied on lexical and structural patterns (e.g., similar control flow and I/O operations) without understanding the distinct core semantics (Base64 encoding vs. XML manipulation).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have mistakenly considered them as clones due to superficial structural similarities (e.g., both use try-catch-finally, streams, and file I/O) but overlooked the fundamentally different core functionalities.
- 共享行为: Both perform I/O operations involving reading from a source and writing to a destination.
- 行为差异: A encodes data using Base64, B downloads and modifies XML.；A reads from a local file, B reads from a URL.；A writes to a specified output file, B writes to a temporary directory.；A returns a boolean success flag, B returns the file path.
- 修正建议: Enhance model understanding of core API calls and data transformations.；Incorporate dataflow analysis to differentiate operations.；Use type-aware embeddings to recognize different output types.

### case_id=6024 FP long_range_semantics

- 方法: `readData` vs `testCodingEmptyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses configuration data from string fields and an INI file, initializing various sets and maps for Tibetan transliteration.
- B 摘要: Tests encoding of data using LengthDelimitedEncoder with an empty file, verifying the encoded output.
- 静态失败原因: The static model may have been misled by overlapping API tokens (e.g., 'File', 'IOException') and common constructs like loops and try-catch blocks, combined with the long length of function A causing the model to rely on superficial similarities.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled this as non-clone because the two methods have completely different purposes and contexts, with no meaningful semantic overlap. The static method is internal data initialization, while the test method verifies encoding behavior.
- 共享行为: Both involve file I/O operations
- 行为差异: Function A is a private static method for configuration parsing; Function B is a public test method for encoding.；A uses StringTokenizer and file reading; B uses ByteArrayOutputStream, FileChannel, and LengthDelimitedEncoder.；A builds multiple HashSets and maps; B checks encoder completion and output string equality.；A has a large, complex structure with many loops and conditionals; B is relatively simple and linear.
- 修正建议: Improve handling of long functions by using hierarchical or chunked representations.；Incorporate data-flow analysis to capture actual dependencies and side effects.；Reduce reliance on token-level overlap for functions with low Jaccard similarity.

### case_id=6025 FN partial_functionality

- 方法: `createDialogArea` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Creates a dialog area for a license, reads an HTML or text license file from the plugin bundle resource, and displays it in a Browser or Text widget.
- B 摘要: Reads a file from a URL or local path into an input stream and delegates to another read method, returning a status.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed because it focuses on token-level similarity and overall structure. The token Jaccard is low (0.157), and the methods have different entry points and return types. The model may not capture the semantic similarity of the nested I/O loop pattern when it is embedded in larger, dissimilar code blocks.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both methods contain a similar sequence of operations: opening a URL stream, reading buffered text, handling IOException, and closing streams. This shared I/O pattern, despite differing contexts, can be considered a Type-4 semantic clone under BCB's broad criteria.
- 共享行为: Both open a URL input stream and read text using BufferedReader/InputStreamReader；Both handle IOException by printing stack trace or setting error status；Both close the streams in finally blocks
- 行为差异: Function A creates and returns a UI composite, sets dialog title and message；Function A conditionally creates a Browser or Text widget based on resource availability；Function A reads from a plugin bundle resource, not a user-provided URL；Function B reads from either URL or FileInputStream based on name content
- 修正建议: Train model with more examples of cross-method I/O patterns；Use dataflow analysis to highlight shared I/O operations；Incorporate task-specific embeddings for I/O and resource handling

### case_id=6026 FN benchmark_preference_bias

- 方法: `sendExceptionToServer` vs `runScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends exception details to a remote server via HTTP POST and prints the server response.
- B 摘要: Retrieves the content of a script file from the applet codebase over HTTP and returns it as a string.
- 静态失败原因: Low token overlap (Jaccard 0.12), different method names, different parameter lists, and long code with different control flows likely caused the model to miss the high-level semantic similarity of both being HTTP-based operations.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'Network I/O' clones because they both perform HTTP requests and read responses, falling under Type-4 semantic clone.
- 共享行为: Both open a URL connection to a remote server.；Both read response data from the connection.；Both handle exceptions during network communication.
- 行为差异: sendExceptionToServer uses HTTP POST to send data; runScript uses HTTP GET to fetch a file.；sendExceptionToServer constructs complex form data; runScript reads raw bytes.；sendExceptionToServer reads response line by line and prints; runScript reads byte by byte and returns as string.；Return type differs (void vs String).
- 修正建议: Incorporate structural awareness of URL connection usage patterns.；Use data flow analysis to capture sequences like open URL, read stream, handle exceptions.；Train on more diverse examples of I/O functions with different purposes but similar structure.

### case_id=6027 FN benchmark_preference_bias

- 方法: `doGet` vs `copyIconFiles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve a page, check permissions, and render response with caching and statistics.
- B 摘要: Copies 16x16 and 32x32 icon files for a UML class based on annotations to a destination directory.
- 静态失败原因: Static BERT correctly predicted non-clone due to low token overlap, different method names, and distinct domains; it failed to match the BCB label which likely is an anomaly.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this pair as a clone due to a very lenient interpretation of Type-4 similarity (both perform I/O with error handling) or an annotation error.
- 共享行为: Both use try-catch blocks for exception handling
- 行为差异: A handles HTTP request/response, B copies files；A involves page lookup and user permissions, B only file I/O；A has complex conditional logic and caching, B has simple annotation checks；Different domains: web vs. file system
- 修正建议: Re-evaluate BCB annotation for correctness；Add domain-specific features to model；Increase negative sampling for dissimilar pairs

### case_id=6028 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `unzip`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles GUI action events to set various application preferences such as file paths, image scaling, date format, look and feel, etc.
- B 摘要: Extracts contents of a zip file to a target directory, creating necessary directories and handling I/O errors.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by overlapping API tokens such as 'File', 'getAbsolutePath', 'mkdirs', and common control flow patterns (if-else, try-catch), causing it to overgeneralize 'file-handling' similarity despite distinct semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they serve entirely different purposes (GUI preference management vs. file extraction) with no meaningful functional overlap.
- 共享行为: Both use File objects for file system operations
- 行为差异: Function A is a GUI event handler that modifies UI components and preferences; Function B is a utility method for file extraction.；A uses JFileChooser and Swing components; B uses ZipInputStream and FileOutputStream.；A handles multiple commands and stores preferences; B only unzips a single file.；A involves user interaction and conditional UI updates; B is fully automated.
- 修正建议: Incorporate data flow or control flow analysis to distinguish use cases.；Train on more diverse negative pairs with similar API usage but different logic.；Add a classifier for functional roles (e.g., UI vs. I/O operations).

### case_id=6029 FP partial_functionality

- 方法: `sendPost` vs `callService`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Sends an HTTP GET request to a constructed URL and stores the response body in an instance variable.
- 静态失败原因: Static models may focus on overlapping tokens (URL, BufferedReader, while loop) and miss the crucial semantic difference in HTTP method and data flow.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically treats functions with different I/O patterns and control flow as non-clones, even if they share some infrastructure code.
- 共享行为: Open a URL connection；Read response line by line using BufferedReader；Accumulate lines into a string buffer
- 行为差异: A uses POST, B uses GET；A writes request parameters to output stream; B does not；A returns result; B sets an instance variable；A sets request headers; B does not
- 修正建议: Incorporate data flow analysis to detect whether output is written to the connection；Distinguish between POST and GET based on API usage (setDoOutput, PrintWriter vs openStream)；Consider call context and side effects (return vs instance variable assignment)

### case_id=6030 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles GUI action events to set paths for GRAPHVIZ, IMAGEMAGICK, and other settings, saving preferences and updating UI.
- B 摘要: Processes a list of files through a pseudolocalization pipeline, reading input and writing output with a modified suffix.
- 静态失败原因: The static model may have been misled by lexical overlaps like 'File', 'fileName', 'extension', 'suffix', and file chooser patterns that appear in both but in different contexts.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires strong functional similarity; these two functions are completely unrelated in purpose and implementation, hence non-clone.
- 共享行为: Both check for null or empty values and handle file paths；Both use conditional logic and loops；Both interact with input/output streams
- 行为差异: Function A is event-driven GUI code; Function B is batch file processing；Function A saves user preferences; Function B transforms file content；Function A has many UI components and settings; Function B is deterministic pipeline
- 修正建议: Improve sensitivity to overall program structure and intent；Incorporate data flow or control flow analysis to distinguish GUI event handlers from file processing pipelines；Use longer-range context or functional summaries

### case_id=6031 FP boilerplate_overlap

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated string constants to populate sets and maps for Tibetan character classification and transliteration.
- B 摘要: Copies a file from source to destination using NIO FileChannel.
- 静态失败原因: The model likely focused on the presence of I/O error handling (IOException) and the 'static private void' signature, overgeneralizing similarity from boilerplate patterns despite negligible lexical overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have entirely different functionality and no meaningful semantic overlap.
- 行为差异: Purpose: A initializes data structures for character processing; B performs file I/O copy.；Input: A uses static string fields; B takes File parameters.；Output: A modifies global sets/maps; B writes to a file.；Control flow: A has complex loops and conditionals; B is a straightforward sequence of channel operations.
- 修正建议: Train with more diverse negative examples to reduce bias towards method signatures and exception handling.；Incorporate structural similarity measures (e.g.,AST-based) to distinguish complex data initialization from simple I/O operations.

### case_id=6032 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles various action commands (GRAPHVIZ, IMAGEMAGICK, etc.) to set UI preferences and file paths for an application.
- B 摘要: Recursively copies a file or directory to a destination using byte streams.
- 静态失败原因: The static BERT model likely relied on overlapping API tokens (File, IOException, etc.) or structural patterns (try-catch, if-else) that appear in both, leading to a false positive. The low Jaccard similarity (0.128) suggests that the model's embedding captured some superficial similarity, but not the overall semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions are semantically unrelated: one is a UI action handler, the other is a file copy utility. They do not share the same functionality.
- 共享行为: Both involve file system interactions (opening files, reading/writing paths or bytes).；Both have error handling with try-catch blocks.
- 行为差异: Function A is a UI event handler that sets configuration preferences; Function B is a utility for actual file copying.；Function A uses JFileChooser and stores paths; Function B reads and writes file content.；Function A has many branches for different settings; Function B has conditional logic for directory vs file and loops over subfiles.
- 修正建议: Improve training data to include more diverse non-clone pairs with similar low-level API usage but different high-level goals.；Add explicit negative examples contrasting UI configuration vs. file I/O utilities.；Consider incorporating method-level documentation or usage context to disambiguate.

### case_id=6033 FN partial_functionality

- 方法: `getFile` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies the endpoint attribute, and saves it to a temporary file, returning the file path.
- B 摘要: Recursively copies a file or directory to a destination using file channels.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on token overlap (Jaccard 0.17) and syntactic structure, which differ significantly. It missed the semantic similarity in the FileChannel usage because it appears embedded in different contexts with different surrounding logic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone due to the shared pattern of file channel transfer, which is a distinctive semantic feature. The partial functionality of transferring bytes from input to output is common, and BCB annotations sometimes accept broad Type-3/Type-4 similarities.
- 共享行为: Both perform file I/O using Java NIO FileChannel for efficient data transfer.；Both read from a source and write to a destination.
- 行为差异: getFile downloads from a remote URL, while copy handles local files/directories.；getFile modifies XML content before saving, copy does not.；getFile returns a String, copy is void.；getFile uses transferFrom, copy uses transferTo.
- 修正建议: Enrich training data with partial functionality clones.；Use graph-based models capturing API call sequences and data flow.；Incorporate program slicing to focus on core data transfer logic.

### case_id=6034 FN partial_functionality

- 方法: `main` vs `actionPerformed`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts all entries from a zip file at a given URL to the current directory.
- B 摘要: Reads rs IDs from a gzipped file and queries NCBI's E-utilities via POST, writing the response to stderr.
- 静态失败原因: The model likely relied on token overlap and method name similarity, both low; it missed the underlying structural pattern of compressed I/O that BCB might recognize.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones based on a common pattern of handling compressed data and using URL resources, despite different overall tasks.
- 共享行为: Both open compressed input streams.；Both use URL objects for network I/O.；Both read data in loops and write to output streams.
- 行为差异: A extracts zip entries to local files; B processes text lines and sends to a web service.；B uses pattern matching and filtering; A does no filtering.；A writes to local files; B writes to a URL output stream and then to stderr.
- 修正建议: Increase training data for Type-4 clones with low token similarity.；Incorporate program dependence or data flow analysis to capture structural commonalities.

### case_id=6035 FN partial_functionality

- 方法: `addIDs` vs `writeFileType`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Queries the GMD database for a given metabolite name, parses the HTML response to extract a score and various identifiers, and updates a PeakListRow object.
- B 摘要: Reads a file containing URIs, for each URI fetches the content, checks for ontology namespace strings in the first 100 lines, and writes the file type classification to an output file.
- 静态失败原因: Static BERT models like CodeBERT rely heavily on token overlap and method name similarity. Low Jaccard (0.129) and different method names led the model to miss the shared high-level structure of URL processing and pattern matching, which BCB considers similar.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to both being 'network I/O with pattern matching' tasks, which can be considered Type-4 (semantic similarity) in BigCloneBench's broad annotation scheme.
- 共享行为: Both open HTTP connections to URLs and read line by line.；Both parse the read lines for specific patterns.；Both use try-catch blocks for exception handling.；Both write output (one to a row object, one to a file).
- 行为差异: A queries a single fixed URL based on input name, while B processes multiple URIs from a file.；A returns an integer score, while B writes classification strings to a file.；A parses HTML for metabolite IDs and multiple fields, while B checks for specific ontology namespace strings.；A updates a PeakListRow object, B writes to a file.
- 修正建议: Incorporate structural features like AST depth or control flow graphs to capture common I/O patterns.；Use a model that better handles long-range dependencies and structural similarity, such as GraphCodeBERT with data-flow edges.；Adjust threshold for considering a clone when API usage patterns are similar despite different domains.

### case_id=6036 FP boilerplate_overlap

- 方法: `getTicketsForQueue` vs `wordFrequency`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves open tickets for a given queue from a REST API, parsing ticket IDs from lines.
- B 摘要: Fetches web page content and counts word frequency using regex pattern matching.
- 静态失败原因: Static BERT/GraphCodeBERT may over-rely on surface-level token overlap (e.g., 'HttpGet', 'BufferedReader', 'readLine', 'URL') and common control flow patterns, missing the semantic divergence in high-level logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions serve entirely different purposes (ticket retrieval vs. word frequency counting) despite sharing some low-level IO patterns.
- 共享行为: Both use HTTP to fetch data；Both read line by line with BufferedReader；Both handle exceptions
- 行为差异: Function A returns list of RTTicket objects; Function B returns integer frequency；Function A uses GET request with query parameters; Function B uses URL directly with word replacement；Function A parses specific 'ticket/' prefix lines; Function B matches regex pattern；Function A has complex error handling and logging; Function B simple print stack trace
- 修正建议: Improve model's ability to distinguish between functional semantics and boilerplate patterns；Incorporate data flow analysis to capture variable usage differences；Use contrastive learning on large-scale non-clone pairs that share API usage but differ in purpose

### case_id=6037 FN partial_functionality

- 方法: `doTransfer` vs `fileDownload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Proxies HTTP requests to a remote URL, forwarding headers and body.
- B 摘要: Downloads a file from a URL and saves it to a local file.
- 静态失败原因: Low token Jaccard (0.16) indicates very little lexical/structural overlap; static BERT models rely on surface similarity and miss the shared URL-reading sub-task.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers clones based on high-level functional similarity; both fetch content from a URL using Java's URL/URLConnection API, which is a common pattern.
- 共享行为: Both open a URL connection and read data from it
- 行为差异: A handles request/response objects and forwards headers/body; B only reads and writes to file；A uses HttpURLConnection and servlet output; B uses URLConnection and file output
- 修正建议: Use graph-based representations to capture data flow and API call patterns；Incorporate task-level semantics via documentation or method names

### case_id=6038 FN partial_functionality

- 方法: `loadMFileViaWeb` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads an M-file from a web URL, reads its content line by line, parses it into a UserFunction, and returns it.
- B 摘要: Opens a URL connection to a fixed URL, reads the content line by line into a StringBuffer, and logs it.
- 静态失败原因: The model likely focused on differences in method names, return types, error handling, and the FunctionParser usage, which are unique to A. Also, token overlap is low (0.188), and the model may have learned that such differences indicate non-clones.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because they share the core logic of reading from a URL line by line using the same pattern, which is a common reusable code snippet. The later processing steps are considered extensions but the essential behavior is similar.
- 共享行为: Both open a URL, get an input stream, wrap in BufferedReader, read lines, and concatenate the content.
- 行为差异: A's URL is parameterized, B's URL is hardcoded；A processes the content via FunctionParser into a UserFunction, B only logs the raw content；A returns a UserFunction, B returns void；A catches exceptions and throws MathLibException, B declares throws Exception
- 修正建议: Augment training data with partially similar pairs；Use models that capture broader semantic similarity beyond lexical overlap；Incorporate control flow and data flow information to recognize shared patterns

### case_id=6039 FP boilerplate_overlap

- 方法: `executeHttpGet` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Executes an HTTP GET request and returns the response body as a JSONObject.
- B 摘要: Parses a YouTube page URL to extract video parameters and constructs a full screen video URL.
- 静态失败原因: Static BERT models likely overemphasized the lexical overlap of common Java I/O libraries (BufferedReader, InputStreamReader, etc.) and the similar structure of reading HTTP responses, missing the significant differences in return types and business logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have different input/output signatures and distinct core functionality, even if they share common I/O boilerplate.
- 共享行为: Both read from an HTTP response using BufferedReader and InputStreamReader.；Both handle exceptions with try-catch.；Both use a loop to read lines from the response.
- 行为差异: Function A uses Apache HttpClient (HttpGet, DefaultHttpClient) while B uses URLConnection.；Function A returns JSONObject, B returns String.；Function A reads all lines into a StringBuilder, B searches for a specific line containing 'fullscreenUrl'.；Function A is a generic HTTP GET, B is specialized for YouTube URL extraction.
- 修正建议: Train models to better distinguish boilerplate patterns from core functionality.；Incorporate dataflow analysis to trace how the read data is used and transformed.；Pay more attention to method signatures, return types, and input parameters.；Use contrastive learning to emphasize differences in output behavior.

### case_id=6040 FN partial_functionality

- 方法: `File2String` vs `fetchUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file (either from filesystem or classpath) and returns its content as a string, with error messages printed to stdout and program exit on failure.
- B 摘要: Fetches a URL, reads its content line by line, and returns the concatenated string; errors are caught silently and an empty string is returned.
- 静态失败原因: Static models like GraphCodeBERT rely heavily on token similarity and structural overlap; the low Jaccard (0.306) and different API usage (FileInputStream vs URL) likely caused the false negative. The model also may have been misled by the extra println/System.exit statements in function A, which are absent in B.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-4 (semantic) clones as positive when the core functionality (reading text and returning as string) is the same, despite differences in input sources and error handling. The annotators might consider these as 'doing the same thing' at an abstract level.
- 共享行为: Both read text input line by line using a BufferedReader.；Both append each line to a StringBuilder/StringBuffer.；Both return the concatenated string of all lines.
- 行为差异: Input source: filesystem/classpath vs URL.；Error handling: prints debug messages and calls System.exit() vs silent catch returning empty string.；Side effects: function A prints to stdout and may terminate JVM; function B has no side effects.；Return on failure: null vs empty string.
- 修正建议: Enhance training data with more Type-4 examples (different domains, similar logic).；Incorporate data flow or control flow abstractions that capture 'read all lines and concatenate' pattern.；Use contrastive learning to align semantic embeddings despite token differences.

### case_id=6041 FP lexical_or_api_overlap

- 方法: `main` vs `copyExternalResource`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that generates adapter JAR files from Prolog files with command-line options.
- B 摘要: Utility method that copies the content of a source file to a destination file using NIO channels.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by lexical overlaps such as 'File', 'IOException', 'try', and 'finally', which are common boilerplate in Java I/O, ignoring the major semantic divergence.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the high-level functionality is completely different, even though they share some low-level file handling tokens.
- 共享行为: Both perform file I/O operations；Both use try-catch-finally blocks for exception handling
- 行为差异: Function A parses Prolog, generates classes, and writes JARs; Function B simply copies bytes from one file to another；Function A involves complex logic with visitors, class loaders, and serialization; Function B is a straightforward copy；Function A has command-line argument parsing; Function B takes two File parameters
- 修正建议: Improve model's ability to differentiate between core logic and boilerplate code；Incorporate data flow or control flow analysis to capture program semantics；Add attention to method names and overall structure

### case_id=6042 FN boilerplate_overlap

- 方法: `modifyApplicationMessage` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.5`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a localized properties file by replacing or adding a key-value pair for a given locale.
- B 摘要: Serves a static file via HTTP by copying its contents to the response output stream.
- 静态失败原因: Static BERT model likely focused on significant differences in method names and overall program structure; token overlap is low, leading to a non-clone prediction; it missed the abstract file-handling pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as file manipulation tasks that involve reading a file and writing to some output, tolerating different output formats and processing logic.
- 共享行为: Both check if a file exists before performing file I/O；Both read from a file；Both write to an output destination (file or response stream)
- 行为差异: A modifies a properties file based on key lookup; B simply copies the entire file；A handles missing locale file by copying from default; B does not；A uses text processing (BufferedReader, splitting); B uses binary copy；A writes back to file; B writes to HTTP response
- 修正建议: Incorporate high-level functional role (e.g., file modification vs. file serving) into representation；Use data flow analysis to distinguish different transformation steps

### case_id=6043 FP other

- 方法: `testAddLinkToImage` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: A test method that copies three image files from the classpath to a report directory and adds hyperlinks to them.
- B 摘要: A main method that reads a Prolog file, parses it, generates adapter classes and lookup resources, and writes them into a JAR file.
- 静态失败原因: Static BERT likely overemphasized superficial similarities such as both having file I/O and exception handling, and possibly the presence of the word 'report' (though in different contexts). The low token Jaccard (0.046) indicates minimal lexical overlap, so the model may have been misled by a few shared technical keywords.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would not consider this a clone because the functions are completely unrelated in purpose and behavior. Even under broad Type-3/4 definitions, they share no significant functionality.
- 共享行为: Both perform file I/O operations；Both use try-catch for exception handling
- 行为差异: Function A is a simple test adding images to a report; Function B is a complex code generation tool.；Function A has no control flow beyond sequential execution; Function B has extensive conditionals, loops, and multiple sub-steps.；Function A uses IOUtils.copy and report.addLink; Function B uses FileUtils, Parser, ClassWriter, Assembler, etc.；Function A operates on three specific image files; Function B handles command-line arguments and Prolog program parsing.
- 修正建议: Improve model's ability to capture overall program purpose and control flow structure.；Introduce negative mining with diverse non-clone pairs that share common APIs but have different goals.；Use more context-aware embeddings that consider the sequence of operations and data dependencies.

### case_id=6044 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `getUser`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts all hyperlinks from a given URL and returns them along with their text.
- B 摘要: Retrieves a User object by login from a DAO or falls back to reading a config file.
- 静态失败原因: Static models like GraphCodeBERT may rely on surface-level features such as common API calls (BufferedReader, URL, readLine loop) and similar control flow structures, overlooking the semantic context and different domain-specific operations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality is completely different: link extraction vs user retrieval. Despite some common I/O patterns, the intent and output are unrelated.
- 共享行为: Both use BufferedReader to read data；Both handle text parsing with loops；Both involve URL/connection operations
- 行为差异: Function A parses HTML links; Function B parses user config file；Function A returns Vector arrays; Function B returns a User object；Function A does timing checks; Function B does DAO operations
- 修正建议: Improve model to capture high-level intent beyond API call sequences；Incorporate data flow analysis to distinguish data sources and processing

### case_id=6045 FN benchmark_preference_bias

- 方法: `doPost` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP POST request by parsing multipart form data to extract a webpage and URL, then generates and writes a mailer to the response output stream.
- B 摘要: Launches a NexOpen project configuration by reading Maven POM files, setting Hibernate dialect properties, and optionally generating a reverse engineering file.
- 静态失败原因: Static BERT/GraphCodeBERT correctly identified low lexical overlap and distinct API usage, leading to a non-clone prediction that disagrees with the possibly erroneous BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as Type-4 semantic clones based on a broad pattern of 'read input, process, produce output' despite different domains, or due to a potential annotation error.
- 共享行为: Both involve reading input data and producing output；Both use InputStream and ByteArrayOutputStream for I/O；Both catch and handle exceptions in try-catch blocks
- 行为差异: Input processing: A parses HTTP multipart form fields; B reads Eclipse project files and launch configuration attributes；Output: A writes a mailer to HTTP response; B configures project properties and manages Eclipse resources；Domain: A is web servlet; B is Eclipse plugin launch delegate；Control flow: A has multipart iteration and conditional forwarding; B has project validation and XML parsing
- 修正建议: Re-examine BCB label; likely not a true clone；Improve benchmark to avoid overgeneralization of semantic patterns；For model, consider focusing on functional equivalence rather than domain-specific patterns

### case_id=6046 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a new version of jEdit by fetching a version file from a URL and comparing build numbers.
- B 摘要: Loads an OSGi FrameworkFactory by reading a services file from the classpath and instantiating the specified class.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized the structural and lexical overlap (e.g., URL, BufferedReader, while loop, trim, etc.) and failed to capture the semantic divergence in the data processing logic and final outcome.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely marks this as non-clone because the overall functionality is completely different: one is a version check UI action, the other is a factory loading mechanism. Despite similar I/O patterns, the purpose and output are distinct.
- 共享行为: Both open a URL/stream and read lines using BufferedReader；Both parse lines inside a loop with conditional logic；Both handle I/O exceptions or close resources
- 行为差异: doVersionCheck reads from a web URL, getFrameworkFactory reads from a local classpath resource；doVersionCheck parses lines starting with '.version' and '.build', getFrameworkFactory parses lines ignoring comments to find a class name；doVersionCheck shows messages and hides cursor, getFrameworkFactory returns a FrameworkFactory instance or throws an exception；doVersionCheck has different error handling (shows error message), getFrameworkFactory throws a custom exception
- 修正建议: Incorporate dataflow analysis to track how data is transformed and used；Add contrastive learning examples that distinguish similar I/O patterns with different intents；Use AST-based features to differentiate control flow and data dependencies

### case_id=6047 FN partial_functionality

- 方法: `register` vs `CheckUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Registers a user in the system, encoding password, setting up authorities, and creating a forum user via HTTP.
- B 摘要: Fetches and returns the first line of content from a given URL.
- 静态失败原因: Static models like GraphCodeBERT rely on lexical tokens and structure; the low token Jaccard (0.14) and different method names/overall structure likely caused it to miss the shared HTTP interaction sub-pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as examples of 'URL fetching' functionality, despite differing contexts and additional logic, leading to a Type-4 clone classification based on partial similarity in the HTTP interaction pattern.
- 共享行为: Both open an HTTP connection to a URL and read a line from the response
- 行为差异: A performs many additional operations (password encoding, database persistence, email sending) beyond the HTTP call；B is a simple utility method that returns the string from the first line; A uses the read line to set a forum ID
- 修正建议: Leverage data flow or API call sequences to capture shared substructures like URL opening and reading；Incorporate context-aware embeddings that can abstract over different application domains

### case_id=6048 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `readScalarpvviewerDocument`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft handshake packet by validating server key and joining session if valid.
- B 摘要: Reads and parses an XML configuration file from a URL to set up a scalar PV viewer GUI.
- 静态失败原因: The static BERT/GraphCodeBERT model may have been misled by similar tokens and API usage patterns (URL.openStream, BufferedReader, InputStreamReader, exception handling) and the presence of code blocks that both read from URLs. The model might have overgeneralized the 'reading from URL' pattern as semantically similar without capturing the domain-specific differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they have completely different functionality: one is a network handshake, the other is an XML parser for GUI configuration. There is no functional similarity, even at Type-4 level.
- 共享行为: Both read data from a URL using BufferedReader and InputStreamReader.；Both handle IOException with a catch block.；Both check for null or empty conditions.
- 行为差异: Function A performs network authentication; Function B parses XML configuration.；Function A sends network packets; Function B updates UI components.；Function A validates a hex string; Function B ignores lines starting with '%'.；Function A has multiple conditional branches; Function B is sequential parsing.
- 修正建议: Increase training data with diverse URL-reading functions that are not clones.；Use more fine-grained semantic features like method name context or control flow.；Incorporate structural information like call graphs or data flow.

### case_id=6049 FP lexical_or_api_overlap

- 方法: `main` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses a Prolog file, generates adapter classes, and writes them to a JAR file.
- B 摘要: Recursive file copy method that copies files and directories using FileChannel.
- 静态失败原因: The model likely overemphasized superficial common API tokens (File, IOException) and control flow structures (try-catch), ignoring the vast difference in high-level semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers them non-clones because the functionality and intent are completely different; any overlap is just generic Java boilerplate.
- 共享行为: Both perform file I/O operations；Both use System.out for output；Both catch IOException
- 行为差异: A is a complex adapter generation pipeline; B is a simple file copy；A uses Prolog parsing, class writing, serialization; B uses directory traversal and channel-based copying；A has command-line argument handling; B has recursive directory handling
- 修正建议: Incorporate program dependence graphs or AST-based diff to capture semantic differences；Train on more diverse non-clone pairs that share common library usage but differ in purpose

### case_id=6050 FN partial_functionality

- 方法: `DecodeMapFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Decodes a map file by XOR with an incrementing key.
- B 摘要: Launches an Eclipse NexOpen project by processing POM files and setting up Hibernate properties.
- 静态失败原因: Static BERT models rely on token and structure overlap; these functions share very few tokens and have completely different control flows and APIs.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled as clone due to both being file processing methods, but the token Jaccard is very low (0.068) and functionalities are unrelated.
- 共享行为: Both read from files；Both throw exceptions；Both involve I/O operations
- 行为差异: Function A decodes a single file using XOR; function B processes multiple XML configuration files；Function A writes output to a file; function B does not produce a similar output file；Function B has complex Eclipse plugin integration; function A is a standalone utility
- 修正建议: Include data flow analysis to capture semantic role of I/O operations；Use dynamic execution traces to compare behavior；Incorporate domain-specific knowledge (e.g., Eclipse plugin vs simple file utility)

### case_id=6051 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads version build numbers from a remote URL and triggers version check logic.
- B 摘要: Parses a YouTube page to extract parameters and construct a fullscreen video URL.
- 静态失败原因: Static BERT/GraphCodeBERT models may rely heavily on token and API sequence similarities. Both functions share common tokens like 'URL', 'BufferedReader', 'readLine', 'try-catch', and loop structure, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functional similarity. Despite structural overlap in reading URLs, the core tasks (version checking vs. YouTube URL extraction) are unrelated, so BCB labels as non-clone.
- 共享行为: Both open a URL connection and read lines from it.；Both parse each line searching for specific patterns.；Both use try-catch blocks for exception handling.；Both perform some UI feedback (wait cursor / progress indicator).
- 行为差异: Function A outputs nothing directly; it calls another method with extracted version strings; Function B returns a constructed URL string.；Function A reads property 'version-check.url'; Function B uses a fixed instance variable 'ytUrl'.；Function A looks for lines starting with '.build' and '.stablebuild'; Function B looks for lines containing 'fullscreenUrl' and further parses it with '&' splitting.；Function A is static and takes a View parameter; Function B is private and takes no arguments.
- 修正建议: Include method name and context as features to differentiate purpose.；Use data flow analysis to track how read lines are transformed.；Train on more diverse examples to avoid over-weighting boilerplate patterns.

### case_id=6052 FN benchmark_preference_bias

- 方法: `addIDs` vs `fileDownload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Parses a web API response to extract chemical IDs and scores, updates a row object.
- B 摘要: Downloads a file from a URL and saves it to a local directory.
- 静态失败原因: Static BERT models (like GraphCodeBERT) rely on token-level and structural similarity. The low Jaccard similarity (0.185) and different control flows likely caused the model to predict non-clone. The model correctly identified the dissimilarity in token patterns and API usage.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to the shared pattern of opening a URL and reading input, despite different functional purposes. The benchmark's broad Type-4 category might consider any two functions that perform network I/O as semantically similar, which is too broad.
- 共享行为: Both open a URL connection and read from it using BufferedReader/InputStreamReader；Both use try-catch with logging of exceptions；Both perform network I/O
- 行为差异: Function A parses HTML and sets multiple fields in a row object; Function B writes raw bytes to a file.；Function A returns an integer score; Function B has void return.；Function A involves string manipulation and conditional parsing; Function B just copies bytes.
- 修正建议: Improve BCB annotation guidelines to avoid conflating general network I/O patterns with semantic similarity.；For models, incorporate high-level task description or intent detection to distinguish between data parsing and file download.

### case_id=6053 FP lexical_or_api_overlap

- 方法: `importSequences` vs `getXML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Imports biological sequences from a selected URL by parsing FASTA-like format into class fields.
- B 摘要: Fetches XML content from a servlet URL and returns it as a string.
- 静态失败原因: Static BERT/GraphCodeBERT may have overemphasized the lexical and API overlap (URL.openStream, InputStreamReader, try-catch blocks) while ignoring the critical differences in loop body logic and data handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have distinct domain-specific purposes and different behaviors (importing sequences vs fetching XML), despite sharing boilerplate IO patterns.
- 共享行为: Open a URL stream；Read input line-by-line；Handle IO exceptions (MalformedURLException, IOException)
- 行为差异: Return type: void vs String；Parsing logic: FASTA header/sequence vs raw XML content；Data storage: modifies class fields vs returns string；Exception handling: prints stack trace/ignores vs returns null
- 修正建议: Train model to weight loop body logic more heavily；Incorporate dataflow analysis to track variable transformations；Add attention to method signatures and return types

### case_id=6054 FP lexical_or_api_overlap

- 方法: `loadURL` vs `retrieveTemplate`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a URL, optionally with basic auth, reads lines and writes them to a temporary file while updating a status label with file size.
- B 摘要: Retrieves a template from a blog URL, reads all lines into a string, caches it, and returns the string.
- 静态失败原因: Likely due to lexical overlap in common API calls (BufferedReader, InputStreamReader, URL, readLine) and similar structural patterns of reading lines from a URL, causing the model to overlook differences in side effects and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically marks as clones only if the functions are semantically equivalent or very similar in functionality. Here, despite both reading from URLs, the overall goal and side effects differ, so BCB labeled as non-clone.
- 共享行为: Both open a URL and read lines from the input stream.
- 行为差异: A writes to a temp file; B appends to StringBuilder.；A handles authentication; B does not.；A updates a status label; B does not.；A prints progress; B does not.
- 修正建议: Improve model to consider overall purpose, return types, side effects, and data flow beyond surface-level API patterns.

### case_id=6055 FN partial_functionality

- 方法: `main` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to files.
- B 摘要: Compresses a local file using GZIP and writes the output to a .gz file.
- 静态失败原因: Static BERT/GraphCodeBERT may focus on lexical overlap of common APIs (e.g., FileInputStream, FileOutputStream, buffer loops) and the method name 'main', while ignoring the semantic direction (compress vs decompress) and the overall task context.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: Although both functions involve stream I/O and similar loop patterns, their high-level purposes (extract vs compress) are different. BCB typically requires more than just structural similarity; it expects functional similarity. Thus, BCB annotators would likely label this as non-clone.
- 共享行为: Both use input/output streams to read and write data；Both have a loop that reads chunks into a buffer and writes them to an output stream
- 行为差异: A decompresses a zip file (reading from URL), B compresses a file to gzip (reading from local file)；A uses ZipInputStream and extracts multiple entries, B uses GZIPOutputStream and handles a single file；A's output is multiple files, B's output is a single compressed file；A handles URL protocol detection, B handles command-line arguments
- 修正建议: Incorporate semantic role labeling or data flow to distinguish compression vs decompression；Use longer-range context to capture the overall purpose (e.g., from method names or comments)；Add negative examples with similar structure but different high-level operations during training

### case_id=6056 FN partial_functionality

- 方法: `run` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Runs an HTTP GET request with basic authentication and reads the response line by line into a string.
- B 摘要: Opens a URL or file input stream and delegates reading to another method, returning a status code.
- 静态失败原因: Low token overlap and surface-level structural differences caused the model to miss the high-level similarity of reading from a stream.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as I/O operations that read data from a source into memory with exception handling, emphasizing partial functional similarity over implementation details.
- 共享行为: Open a data source (HTTP connection or URL/file stream)；Read from an input stream；Handle I/O exceptions
- 行为差异: A uses HTTP with authentication; B supports both HTTP and files；A reads response directly in a loop; B delegates reading to a separate method；A returns void and updates fields; B returns an int status；A updates a timestamp field; B does not
- 修正建议: Improve model to recognize high-level I/O patterns across different APIs；Incorporate data flow analysis to capture that both functions ultimately read from an input stream

### case_id=6057 FN partial_functionality

- 方法: `copyFile` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Downloads a WSDL file from a URL, optionally modifies XML, and saves it locally.
- 静态失败原因: Static BERT models rely on token overlap and surface-level semantics; the low Jaccard similarity and different method signatures/overall structure obscured the shared FileChannel idiom.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a clone because both functions share a core file-writing behavior using FileChannel.transferFrom, which is a specific API usage pattern that constitutes partial functionality similarity.
- 共享行为: Both use FileChannel.transferFrom to transfer data from an input stream to an output file.；Both create FileInputStream and FileOutputStream and close channels after transfer.
- 行为差异: Function A is a simple file copy; Function B includes URL connection, XML parsing, logging, and custom error handling.；Function B checks file existence and conditional download; Function A does no such checks.；Function B modifies XML content and renames temporary files; Function A does not.
- 修正建议: Incorporate dataflow or program dependency information to capture shared API usage patterns.；Use AST-based models that can detect structural similarity despite different contexts.；Train on fine-grained clone types that recognize partial functionality overlap.

### case_id=6058 FN benchmark_preference_bias

- 方法: `login` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Logs into LOLA by sending a POST request with encoded credentials and extracts a session ID.
- B 摘要: Reads a resource file from the classpath, splits it into sections by '---' markers, and validates the number of sections.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on lexical overlap and structural patterns; the low Jaccard similarity and different control flow led to correct non-clone prediction, but BCB label contradicts.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to superficial I/O and URL usage, but the functionality and logic are entirely different; likely a false positive in BCB.
- 共享行为: Both use a URL to obtain an input stream；Both read lines using BufferedReader；Both process the input line by line
- 行为差异: A performs HTTP POST with output, B only reads a resource；A captures a single session ID, B splits content into multiple sections；A catches exceptions and returns empty, B throws exceptions；A prints messages, B does not
- 修正建议: Include more diverse examples in training to reduce bias towards specific API usage；Use dataflow-aware models to capture semantic differences in I/O operations

### case_id=6059 FP other

- 方法: `md5Crypt` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Implements MD5-based password hashing (crypt function) using multiple MD5 digests and a 1000-round loop.
- B 摘要: Processes an HTTP request in a Struts action, managing session, validating roles, and sending XML data to a URL for classification.
- 静态失败原因: The static model likely overgeneralized from shared tokens like 'byte', 'String', 'digest', or from syntactic structures (loops, conditionals) and missed the complete difference in domain and algorithm. The very low Jaccard (0.0825) suggests the model relied on non-informative patterns.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels non-clones (0) when functions have no semantic similarity despite having some trivial structural overlap. Both use Java standard libraries but for entirely different purposes, so BCB correctly rejects this pair.
- 共享行为: Both use loops and conditional branches；Both manipulate byte arrays or strings
- 行为差异: A performs cryptographic hashing; B performs web request handling and XML communication；A uses MessageDigest for MD5; B uses URLConnection and XML parsing；A returns a hash string; B returns an ActionForward for navigation；A has no I/O; B does network I/O and session management
- 修正建议: Improve model's ability to distinguish domain-specific libraries (e.g., cryptographic vs. web)；Incorporate semantic role labeling to separate data transformation from I/O operations；Use functional similarity metrics beyond token overlap

### case_id=6060 FN library_context_missing

- 方法: `sendExceptionToServer` vs `lookupFutureEvents`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `context_recovery_then_expert`；动态可解性: `low`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST with URL-encoded parameters.
- B 摘要: Fetches future events from a Meetup API via HTTP GET and parses JSON into Event objects.
- 静态失败原因: Static models rely on lexical and structural similarity; low token Jaccard and different domain-specific identifiers cause the model to miss the high-level functional similarity of HTTP request/response handling.
- 静态 case study: 该类错误缺少关键上下文或需要深层语义，纯静态方法不可靠。
- 动态 case study: 动态执行价值较低：样本可能依赖库、框架、网络、GUI、数据库或项目上下文，需要先恢复环境或 mock 依赖。
- BCB 偏好解释: BCB may consider both as network I/O operations that follow a similar pattern: construct URL, open connection, read/write, and handle exceptions, thus labeling them Type-4 clones despite different functionality.
- 共享行为: Both perform HTTP communication to interact with a remote server.
- 行为差异: One sends data (POST), the other retrieves data (GET).；One encodes exception info, the other parses JSON and constructs domain objects.；Error handling differs: one prints to console, the other throws custom exception.
- 修正建议: Incorporate high-level API usage patterns (e.g., HTTP request/response) as features.；Use contrastive learning to capture functional similarity even with low token overlap.

### case_id=6061 FN partial_functionality

- 方法: `getHTML` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML content from a URL and optionally writes it to a file, returning the content as a string.
- B 摘要: Checks for a newer version of jEdit by downloading and parsing a version file from a URL, displaying appropriate GUI messages.
- 静态失败原因: The low token overlap and differences in library calls, return types, and control flow misled the model into focusing on surface-level dissimilarities rather than the shared URL-reading subroutine.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs as clones if they share a common functional subtask, such as downloading and processing text from a URL line by line, even if the overall goals differ.
- 共享行为: Both open a URL connection and read lines from the input stream using BufferedReader.
- 行为差异: getHTML returns the fetched content as a string and may write to a file; doVersionCheck is void and shows GUI dialogs.；getHTML uses HttpURLConnection with custom User-Agent; doVersionCheck uses URL.openStream.；getHTML appends all lines; doVersionCheck parses lines for version/build info.
- 修正建议: Incorporate data augmentation with more partial functionality pairs.；Use a model that explicitly identifies shared subroutines via program slicing or graph-based matching.

### case_id=6062 FN lexical_or_api_overlap

- 方法: `testNetworkHTTP` vs `readVersion`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: testNetworkHTTP performs multiple HTTP GET requests to external URLs, reading and discarding responses, likely for data exfiltration.
- B 摘要: readVersion reads a local resource file to extract version, revision, and compile date.
- 静态失败原因: Static BERT/GraphCodeBERT likely relies on token overlap, which is low (0.246). The methods differ lexically and in length, so the model predicted non-clone despite structural similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider these clones as Type-4 because both implement a common pattern of reading lines from a URL using BufferedReader, with similar resource handling and exception management, despite different specific functionality.
- 共享行为: Both methods fetch text content via URL and read lines with BufferedReader.；Both use try-catch-finally blocks with IOException handling.；Both use InputStreamReader and BufferedReader to read streams.
- 行为差异: A connects to multiple external URLs; B reads a single local resource.；A discards all read data; B parses lines and sets fields.；A uses HttpURLConnection; B uses URL.openStream.；A does not close reader in finally; B closes reader.
- 修正建议: Enhance model to capture structural patterns like try-catch-finally with I/O operations.；Use AST-based or data-flow features to recognize common API usage sequences.；Train on broader definition of clones including partial functionality similarity.

### case_id=6063 FP partial_functionality

- 方法: `retrieveQ` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads entire content from a given URL as a string, printing the HTTP response message.
- B 摘要: Retrieves a version string from a hardcoded URL, returning the last line read or null if an exception occurs.
- 静态失败原因: Model over-relied on surface-level API overlap (URL, URLConnection, BufferedReader, readLine) and loop structure, failing to differentiate the overall purpose and the subtle difference in loop behavior (accumulating all lines vs. overwriting with last line).
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB considers core functionality distinct: one is a generic URL content fetcher, the other is a specific version checker. The shared boilerplate of URL reading is insufficient for clone classification.
- 共享行为: Open a URL connection and wrap input stream in BufferedReader；Read lines from the input stream in a loop；Close the BufferedReader
- 行为差异: retrieveQ takes a URL parameter; getVersion uses a hardcoded URL；retrieveQ reads all lines and concatenates with newlines; getVersion overwrites variable with each line, returning only the last line；retrieveQ prints the HTTP response message; getVersion does not；retrieveQ throws exceptions; getVersion catches all exceptions and returns null
- 修正建议: Incorporate data flow analysis to track how the return value is constructed (concatenation vs. overwrite)；Add capability to differentiate between reading all lines vs. a single line；Utilize method names and comments as contextual signals；Train on more examples that differ in control flow within similar API usage patterns

### case_id=6064 FP boilerplate_overlap

- 方法: `actionPerformed` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.05`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles various UI actions (GRAPHVIZ, IMAGEMAGICK, etc.) by opening file choosers and updating preferences and UI components.
- B 摘要: Copies a file from source to destination using NIO FileChannel.
- 静态失败原因: The model may have been misled by the presence of file-related keywords (e.g., 'File', 'IOException') and the boilerplate 'try/finally' structure in both, despite different semantics. The length of Function A might also cause loss of context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have completely different purposes: UI event handling vs. file copying, with no functional overlap.
- 共享行为: Both involve file I/O operations
- 行为差异: Function A is a UI event handler with complex state updates; Function B is a simple file copy utility；Function A uses JFileChooser; Function B uses FileInputStream/FileOutputStream；Function A has no file content copying; Function B does；Function A updates UI components and preferences; Function B does not
- 修正建议: Train with more diverse negative examples that share lexical features but differ semantically；Incorporate structural or dataflow analysis to distinguish UI event handlers from simple utilities

### case_id=6065 FN benchmark_preference_bias

- 方法: `doGet` vs `testCopy_inputStreamToOutputStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request for a portal page, including access control, caching, and logging.
- B 摘要: Unit test for copying bytes from an input stream to an output stream and verifying correctness.
- 静态失败原因: The static method correctly predicted non-clone; it didn't fail. The BCB label appears erroneous, so the 'failure' is a mismatch with a potentially incorrect ground truth.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label likely is a false positive; perhaps annotators considered both as involving I/O or stream operations, but the semantic gap is too large for any reasonable clone definition.
- 共享行为: Both involve I/O operations (HTTP response vs. streams), but at a very generic level.
- 行为差异: Function A is a complex servlet handler with business logic, access control, caching, and error handling.；Function B is a simple unit test for stream copying with assertions.；Function A operates on HTTP request/response; Function B operates on byte streams.；Function A has many external dependencies (PortalRequest, Property, etc.); Function B is self-contained.
- 修正建议: Review and correct BCB annotations for this pair.；Use a more rigorous clone definition that avoids such broad functional overlap.

### case_id=6066 FN partial_functionality

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file using FileChannel transfer.
- B 摘要: Builds a website for editing by processing multiple pages with XML transformations and file I/O.
- 静态失败原因: Static BERT models may fail to capture the vast difference in purpose due to limited context and focus on API usage overlap (both use FileInputStream and FileOutputStream).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as clone due to both functions performing file copy operations (A directly, B indirectly as part of building site), but the overall semantics are vastly different.
- 共享行为: Both use FileInputStream to read files.；Both involve writing files (A writes destination file, B writes output files).
- 行为差异: A is a simple single file copy; B is a multi-step site builder with XML processing, string replacement, and logging.；A returns boolean success; B returns void and throws exceptions.；B involves many additional operations like file system abstraction, property handling, and DOM parsing.
- 修正建议: Improve training data to include more diverse negative examples with similar API usage but different overall semantics.；Use dataflow analysis to distinguish between simple copy and complex multi-step processes.

### case_id=6067 FP boilerplate_overlap

- 方法: `googleImageSearch` vs `PhoneSetImpl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Searches Google Images for album art of the current track and populates a list of image URLs when the artist changes.
- B 摘要: Constructor that reads phone set entries from a URL into a map, skipping comment lines.
- 静态失败原因: The model likely overemphasized common API usage patterns (BufferedReader, InputStreamReader, URL, readLine, close) and overlooked the distinct surrounding logic and different method signatures/purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB defines clones as functionally similar code fragments; these two have only superficial I/O boilerplate overlap but completely different business logic, so they are not considered clones.
- 共享行为: Both use BufferedReader to read from a URL's input stream；Both process lines from a text resource
- 行为差异: A is a method that conditionally triggers a web search; B is a constructor that always loads data；A uses HttpURLConnection with custom headers; B uses URL.openStream()；A parses HTML to extract image URLs; B parses lines with a custom parseAndAdd method；A handles exceptions broadly; B throws IOException
- 修正建议: Incorporate data flow analysis to track variable usage and method call context；Use control flow graphs to capture different branching and exception handling；Improve tokenization to distinguish between method/constructor signatures and external dependencies

### case_id=6068 FN partial_functionality

- 方法: `runScript` vs `getXML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches a script from a URL relative to the codebase and returns its content as a string, returning 'error!' on failure.
- B 摘要: Fetches XML data from a constructed URL and returns the response as a string, returning null on failure.
- 静态失败原因: Static BERT/GraphCodeBERT relies heavily on lexical token overlap and structural patterns, missing the semantic commonality due to low Jaccard similarity (0.204), different method names, and different input/output conventions.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels functions with similar high-level semantics (fetching URL content and returning it) as clones, even if implementation details vary, because they perform the same task.
- 共享行为: Both open a URL connection and read the response content.；Both return the content as a string.
- 行为差异: URL construction method differs: A uses getCodeBase() + scriptName, B uses servletURL + request.；Reading mechanism differs: A reads characters one by one, B reads lines using BufferedReader.；Error handling differs: A returns 'error!' on any exception, B returns null on specific exceptions.；B has unused variable encodedRequest.
- 修正建议: Incorporate data-flow analysis to recognize common patterns like URL fetching.；Use semantic role labeling to abstract function behavior.；Augment training data with renamed variants of URL-fetching functions.

### case_id=6069 FN partial_functionality

- 方法: `runInternal` vs `parse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.5`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads an OPDS catalog from a URL via HTTP, handles pagination, downloads books, and updates Android UI.
- B 摘要: Parses a delimited data file or URL into a DataSet object using StreamTokenizer, with header and type handling.
- 静态失败原因: Low token Jaccard (0.108), long code length, and different APIs and control flow patterns caused the model to miss the loose functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to shared high-level functionality: reading data from a URL, parsing it, and handling errors, despite domain differences.
- 共享行为: Both read data from a URL using input streams；Both parse textual data (XML vs delimited)；Both handle I/O errors and exceptions
- 行为差异: Code_a is specific to OPDS protocol with pagination and book download; code_b is a generic data parser；Code_a uses Android UI and callbacks; code_b returns a DataSet object；Code_a involves multiple HTTP requests and connection management; code_b is single-pass parsing
- 修正建议: Use graph-based representations capturing I/O and parsing patterns；Incorporate domain-agnostic semantic schemas for URL reading and parsing

### case_id=6070 FN partial_functionality

- 方法: `testNetworkHTTP` vs `PageLoader`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Test method that makes multiple HTTP GET requests to various URLs and reads input streams without using the data.
- B 摘要: Constructor that takes a URL, opens an HTTP connection, reads all content into a string field, and throws an exception on failure.
- 静态失败原因: Static BERT models rely heavily on token overlap and structure, which is low here (Jaccard 0.15). They miss the underlying semantic similarity of HTTP fetching due to different method signatures, variable names, and control flow, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both involve the core pattern of opening an HTTP connection and reading from it, despite superficial differences in URL count, error handling, and data usage. The BCB annotation often tolerates Type-3/Type-4 variations when the essential behavior of fetching data over HTTP is preserved.
- 共享行为: Both perform HTTP GET requests；Both read from an InputStream via BufferedReader
- 行为差异: A makes multiple requests to different URLs, while B only makes one；A discards all read data, whereas B accumulates data into a field；A uses HttpURLConnection explicitly, B uses URL.openStream()；A catches IOException and prints stack trace, B throws Exception
- 修正建议: Improve model's ability to recognize partial functionality matches, e.g., by learning that multiple HTTP requests are a variant of a single request；Increase training data with such broad clone pairs；Use graph-based representations to capture data flow of network operations

### case_id=6071 FN partial_functionality

- 方法: `copyResource` vs `compress`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a single resource (URL or file) to a destination file by reading and writing byte by byte.
- B 摘要: Concatenates multiple input files into an output file and optionally compresses it using an external tool, reading in buffered chunks.
- 静态失败原因: The static BERT/GraphCodeBERT model likely failed due to low lexical overlap (token Jaccard 0.19), different method names ('copyResource' vs 'compress'), different parameter lists, and the presence of additional logic (compression, loop over multiple files) in B. The model may have been biased by surface-level differences rather than recognizing the shared I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both perform the core operation of reading data from input streams and writing to output streams, which is a fundamental file copying pattern. Despite differences in source handling and additional compression, the essential behavior is similar enough for a broad Type-3 clone annotation.
- 共享行为: Read from input streams and write to output streams in a loop until end of stream；Close input and output streams after copying
- 行为差异: A copies a single source; B concatenates multiple sources；A uses byte-by-byte reading; B uses buffered reading；B optionally invokes external compression; A does not；A handles both URL and file sources; B only handles file sources
- 修正建议: Incorporate data-flow or control-flow features to capture similar I/O patterns.；Train on more Type-3 clone examples where core behavior is shared despite different method names and auxiliary logic.；Use graph-based representations that abstract variable names and focus on structural similarity of loops and stream operations.

### case_id=6072 FN lexical_or_api_overlap

- 方法: `getFile` vs `fileCopy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint attribute, and saves it to a temporary directory, returning the file path.
- B 摘要: Copies a file from one location to another after performing various validation checks, with no return value.
- 静态失败原因: Static models like CodeBERT may over-rely on lexical overlaps (e.g., 'FileOutputStream', 'close', 'IOException') and miss the deeper semantic gap caused by network download and XML processing in A vs. simple file copy in B.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might consider these as clones due to common file I/O patterns (FileOutputStream, stream closing) and both achieving a 'file transfer' functionality, albeit from different sources (network vs local). However, the difference in overall purpose and complexity makes this a weak annotation.
- 共享行为: Both perform file output operations using FileOutputStream；Both involve reading from an input source and writing to a file
- 行为差异: A downloads from a network URL, while B copies a local file；A includes XML parsing and modification, B does not；A has a non-void return type (String), B is void；A uses NIO channels (ReadableByteChannel, FileChannel), B uses classic byte buffer
- 修正建议: Incorporate control flow and data flow analysis to distinguish network vs. local I/O；Use pre-trained models with better understanding of file and stream operations；Consider adding a filtering step for high-level functionality (e.g., network download vs. copy)

### case_id=6073 FN partial_functionality

- 方法: `setBundleInfoName` vs `addIDs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL to parse key-value pairs and updates BundleInfo objects' bundle names accordingly.
- B 摘要: Fetches a URL containing metabolite data, parses HTML-like content to extract IDs and scores, and sets various properties on a PeakListRow object.
- 静态失败原因: Static models like GraphCodeBERT rely on token similarity and structural patterns. Low Jaccard (0.20) indicates low lexical overlap, and the shared outer skeleton may be overshadowed by different inner details. Long functions may also suffer from truncation, losing the common pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both implement a 'data retrieval from URL and update' pattern, which could be classified under a broad 'data import' functionality, even though the specific data and parsing differ.
- 共享行为: Both open a URL and read lines from the response.；Both parse each line to extract specific information.；Both update a data structure (list or row) based on parsed data.
- 行为差异: Different input parameters: list and location vs row and name.；Different URL structures and parsing logic (key-value split vs HTML tags).；Different target data structures (BundleInfo list vs PeakListRow).；Different return types and values (boolean vs int).
- 修正建议: Use a model that captures overall functionality, e.g., dataflow or abstract syntax trees with graph neural networks.；Augment training with more examples of URL-reading patterns to improve recognition of I/O templates.；Consider truncation strategies that preserve the overall structure rather than fixed-length segments.

### case_id=6074 FN benchmark_preference_bias

- 方法: `getFile` vs `unJar`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL from a URL, modifies an endpoint attribute, and saves it to a temporary file, returning the file path.
- B 摘要: Extracts a specific entry from a JAR file and saves it to a directory derived from the JAR path, returning the path to the extracted file.
- 静态失败原因: The static model likely relied on token-level similarity (Jaccard 0.072) and API call overlap, which is minimal. It failed to capture the abstract high-level similarity in purpose, as the concrete implementations use entirely different libraries and control flows.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to considering both as 'get a file' operations that abstractly perform similar resource retrieval and local storage, even though the sources and processing differ. However, the very low token overlap (0.072) makes this a borderline Type-4 clone.
- 共享行为: Both involve file I/O and return a file path.；Both take a source identifier and a resource name.；Both are utility methods that handle errors.
- 行为差异: Function A downloads from a network URL; Function B extracts from a local JAR file.；Function A modifies XML content; Function B does not modify content.；Function A writes to a temp directory; Function B writes to a directory relative to the JAR path.；Function A uses multiple specific exception types; Function B uses a generic Exception.
- 修正建议: Incorporate method-level semantic embeddings from documentation or comments.；Use program dependency graphs to capture high-level dataflow (both produce a file path from an input resource).；Include task-specific classification heads for partial functionality matching.

### case_id=6075 FN partial_functionality

- 方法: `getEncoding` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts the character encoding from a URL response by first checking the Content-Type header, then scanning the response body for charset/encoding declarations.
- B 摘要: Reads the entire content of a hardcoded URL and logs it to debug output.
- 静态失败原因: Static BERT methods rely on token sequences and attention; here the token overlap is low (0.23), and the core functionality differs significantly. The model likely focused on the different method names and different core operations (e.g., 'extractEncoding' vs 'append'), leading to a non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'reading from URL and processing content' clones, but the specific processing (encoding extraction vs. dumping content) differs; however, the shared structure of opening connection and reading stream might be deemed sufficient for a broad Type-4 clone.
- 共享行为: both open a URL connection；read input stream via BufferedReader；process content line by line
- 行为差异: Function A parses HTTP headers and extracts encoding, while Function B does not；Function A returns an encoding string, Function B logs the full content；Function A handles resource management with try-finally, Function B does not；Function A uses a parameter URL, Function B hardcodes a URL
- 修正建议: Improve models to better capture functional similarity beyond token overlap；consider data-flow analysis to differentiate reading vs. manipulating content；add contrastive training on partially similar functions

### case_id=6076 FP boilerplate_overlap

- 方法: `actionPerformed` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: GUI event handler that processes several commands to update application preferences and UI settings (e.g., Graphviz path, image scaler, date format, look-and-feel).
- B 摘要: Static utility that copies a file from source to destination using a buffer and handles file-related exceptions.
- 静态失败原因: Static BERT may have over-relied on overlapping tokens such as 'File', 'IOException', 'catch', 'return', and other common Java boilerplate, while missing the high-level semantic difference in method purpose and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because they serve completely different purposes: one is a GUI event handler managing many settings, the other is a low-level file copy utility. Although both use File, the overall functionality is distinct.
- 共享行为: Both methods handle file-related operations using File objects and I/O streams
- 行为差异: Method A is a long action listener with multiple conditional branches for different GUI commands；Method B is a short file copy routine with no user interaction；Method A manages application preferences and updates UI components；Method B purely copies bytes from one file to another
- 修正建议: Improve the model's ability to distinguish between utility functions and complex event handlers；Incorporate method name and class context more explicitly；Use data-flow or control-flow features to highlight structural differences；Train with more diverse negative examples that share low-level I/O tokens but differ in higher-level functionality

### case_id=6077 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `decodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by updating or adding a key-value pair, copying the default English file if the locale file does not exist.
- B 摘要: Decodes a Base64-encoded input file and writes the decoded bytes to an output file.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the specific API calls and logic, recognizing that one manipulates properties and the other does Base64, leading to low similarity and classification as non-clone. It may not have captured the abstract file I/O pattern.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider both as file I/O operations that transform an input file to an output file, and thus classify them as Type-4 clones based on the common pattern of streaming bytes.
- 共享行为: Both read from an input stream and write to an output stream in a loop
- 行为差异: A handles property file format (splitting lines by '=', appending key-value)；B does Base64 decoding；A copies default file if missing；A modifies a specific key
- 修正建议: Improve detection of abstract I/O patterns；Incorporate high-level functional roles

### case_id=6078 FP lexical_or_api_overlap

- 方法: `setBundleInfoName` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL, parses key=value pairs to update bundle names in a list.
- B 摘要: Fetches a GeoJSON tile from URL, converts to geometries, and adds to a data loader.
- 静态失败原因: Model over-relied on shared lexical tokens and API calls (URL, BufferedReader, while readLine, IOException) without capturing the drastically different application logic and data transformations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because functions perform entirely different tasks despite sharing low-level API usage; functional similarity is minimal.
- 共享行为: Both open a URL and read lines using BufferedReader.；Both handle IOException with printStackTrace or logging.
- 行为差异: Purpose: updating bundle info vs. processing map tile data.；Output: returns boolean vs. void with side effects on data structures.；Parsing: simple key=value vs. complex GeoJSON geometry conversion.；Synchronization: absent in A, present in B for request deduplication.
- 修正建议: Incorporate data-flow analysis to distinguish how read lines are processed.；Use graph neural networks that model method-level semantics beyond token sequences.；Add training examples with similar API usage but different business logic.

### case_id=6079 FP boilerplate_overlap

- 方法: `addQDInformation` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads and parses QD information from a local or remote file, updating internal state.
- B 摘要: Downloads a file from a URL to a local destination with progress reporting.
- 静态失败原因: The model likely focused on overlapping tokens and API usage (URL, InputStream, BufferedReader, loops) without capturing the semantic purpose and side effects, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have completely different purposes and outputs, even though they share some I/O patterns.
- 共享行为: Both involve reading data from a URL or file stream；Both use try-catch or exception handling；Both have loops that read until end of stream；Both use InputStream/Reader and close resources
- 行为差异: A reads and parses structured text data; B writes raw bytes to a file；A updates instance fields; B is static and returns a boolean；A handles file not found silently; B throws exceptions；A uses character-based Reader; B uses binary BufferedInputStream
- 修正建议: Incorporate data flow analysis to track variable usage and return values；Use method signature and return type as strong signals；Train on contrastive examples that differentiate similar I/O patterns with different semantics

### case_id=6080 FP lexical_or_api_overlap

- 方法: `storeImage` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Stores an image from an InputStream to a file with optional resizing and returns the relative file path.
- B 摘要: Reads a configuration file and populates various sets and maps with tokenized data from each line.
- 静态失败原因: Static BERT may have been confused by shared keywords like 'File', 'IOException', 'HashSet', 'while', but the overall structure and purpose differ, and the model may have over-generalized from training data that pairs file-handling functions.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely saw completely different functionalities (image storage vs. config parsing) and no meaningful semantic overlap, thus labeling as non-clone.
- 共享行为: Both involve file I/O operations.；Both use exception handling (IOException).
- 行为差异: A writes image data to disk while B reads configuration data into memory.；A handles image resizing while B parses structured text lines.；A returns a path string while B modifies global data structures.
- 修正建议: Improve model's ability to distinguish between writing image data and parsing configuration files.；Add more training examples with similar lexical overlap but different semantics.；Incorporate control flow and data flow analysis to differentiate output vs input behavior.

### case_id=6081 FN partial_functionality

- 方法: `getFile` vs `doImageProcess`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies an endpoint attribute in the XML, and returns the file path.
- B 摘要: Processes an image request by reading an image stream and writing it to the HTTP response, with optional resizing.
- 静态失败原因: Static BERT models rely on token similarity and may have overemphasized common tokens like 'InputStream', 'response', 'URL' while missing the distinct overall workflows. Low Jaccard also suggests limited lexical overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled as clone due to broad functional similarity: both functions fetch a resource from a URL and process it (one modifies XML, the other resizes images). However, the specific purposes are completely different.
- 共享行为: Both open a URL input stream；Both handle exceptions；Both perform I/O operations
- 行为差异: A involves XML parsing and modification, B does image processing；A writes to a local file, B writes to HTTP response；A uses AxisFault, B uses IOException；A has multiple exception types, B only IOException
- 修正建议: Incorporate control-flow and data-flow analysis；Use graph-based models (e.g., CodeGraphBERT)；Improve training data with more diverse negative examples；Use contrastive learning to distinguish similar-sounding but different operations

### case_id=6082 FN partial_functionality

- 方法: `setMembers` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses HTML from a Trac URL to extract component and priority options into arrays
- B 摘要: Reads entire content from a fixed URL and logs it
- 静态失败原因: The functions have low lexical overlap and different method names; a static model likely focused on token and syntax differences, failing to capture the semantic similarity of the URL reading pattern because it is embedded in different contexts (parsing vs. logging) and uses different APIs (URL vs URLConnection)
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the common pattern of reading from a URL using BufferedReader as sufficient for a broad Type-3 clone, even though the post-processing differs
- 共享行为: Open a URL and read its content line by line using BufferedReader
- 行为差异: A parses HTML to extract specific <select> option values; B merely concatenates all lines；A populates class-level arrays; B logs the content；A handles specific exceptions; B throws generic Exception；A uses Pattern/Matcher; B does no parsing
- 修正建议: Use data augmentation to train on sub-patterns；Improve model's ability to recognize common I/O patterns；Use contrastive learning to focus on semantic rather than lexical similarity

### case_id=6083 FP lexical_or_api_overlap

- 方法: `read` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a skeleton file from the classpath, splits it into sections delimited by '---', and validates the number of sections.
- B 摘要: Fetches the latest version string from a remote URL.
- 静态失败原因: The model likely over-relied on surface-level similarities (URL, BufferedReader, while loop, exception handling) and failed to capture the distinct functional intents.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions serve entirely different purposes despite some structural API usage overlap.
- 共享行为: Both open a URL connection and read lines using BufferedReader
- 行为差异: A reads a local resource file; B fetches from a remote URL；A builds a list of sections; B returns a single version string；A validates section count and throws exception; B returns null on failure
- 修正建议: Incorporate dataflow or control-flow analysis to distinguish different input/output semantics；Train with more hard negatives that share API usage but differ in purpose；Add contrastive learning on functional behavior beyond token patterns

### case_id=6084 FN partial_functionality

- 方法: `issueCommandToServer` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with command and capsule, reads the response line by line, and returns the concatenated response.
- B 摘要: Reads a file from disk or classpath, reads its lines line by line, and returns the concatenated content.
- 静态失败原因: Static BERT models likely focused on token overlap and API usage, which are low (Jaccard 0.152). The method names and distinct APIs (URLConnection vs FileInputStream) dominate, masking the shared algorithmic pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a clone because both methods implement the common pattern of reading all lines from a text source (stream) and concatenating them, despite different I/O sources. The structural similarity in the core reading loop is high.
- 共享行为: Both open an input stream；Both wrap stream in BufferedReader；Both read lines in a loop appending to StringBuffer；Both return the concatenated string
- 行为差异: A uses URLConnection for HTTP; B uses FileInputStream or classpath URL；A has no error handling (throws exception); B catches exceptions and calls System.exit；A writes request data via OutputStreamWriter; B does not write；A has specific HTTP headers; B has none
- 修正建议: Abstract stream opening to generic 'openStream' during pre-processing；Train on data flow graphs to capture structural similarities；Include more negative examples with similar structure but different semantics

### case_id=6085 FP lexical_or_api_overlap

- 方法: `getUser` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves a User by login, first trying database DAO, then reading from a config file if not found.
- B 摘要: Checks for a new software version by reading a version file from a URL and comparing build numbers.
- 静态失败原因: Static BERT likely over-relied on lexical overlap (URL, BufferedReader, readLine) and ignored the distinct semantic contexts and data flows.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB focuses on functional equivalence; these functions have completely different goals despite sharing URL-reading boilerplate.
- 共享行为: Both open a URL stream and read lines with BufferedReader；Both handle IO exceptions
- 行为差异: Different purposes (user retrieval vs version check)；Different data parsing and logic；Different exception handling and messaging；Function A saves user to DAO, Function B shows UI messages
- 修正建议: Use control-flow and data-flow aware models；Add more training examples that distinguish boilerplate from core logic；Incorporate structural or semantic similarity measures beyond token overlap

### case_id=6086 FN benchmark_preference_bias

- 方法: `createHTML` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Generates an HTML page by reading a CSS file and appending content based on a page type, including database queries.
- B 摘要: Reads tokenized data from string constants and a configuration file to populate hashmaps and sets for Tibetan/Sanskrit text processing.
- 静态失败原因: The static model correctly predicted non-clone due to low token overlap (0.082) and distinct API usage (HTML vs. StringTokenizer, HashSet). BERT-based models rely heavily on lexical and structural similarity, which is lacking here.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to superficial similarities: both methods read files, use BufferedReader, and have while loops. This could be an overbroad interpretation of Type-3/Type-4 clones, where structural patterns are considered similar despite different functionality.
- 共享行为: Both read input data (file or stream) line by line using BufferedReader.；Both use while loops to process input lines.；Both perform string concatenation to build results.；Both handle IOException with logging or printing.
- 行为差异: createHTML builds an HTML string; readData builds HashSets and HashMaps.；createHTML queries a database; readData parses a structured file with columns.；createHTML has a switch on PAGE_TYPE; readData uses complex nested conditionals.；The domains and output structures are entirely different.
- 修正建议: Improve BCB annotation guidelines to avoid labeling methods with only generic I/O patterns as clones.；Enhance clone detection models to better differentiate boilerplate from core functionality.

### case_id=6087 FP lexical_or_api_overlap

- 方法: `loadSourceCode` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads source code from a local file resource, applies syntax highlighting, and returns it as an HTML string for display.
- B 摘要: Fetches the first line of content from a given URL via HTTP connection and returns that line as a string.
- 静态失败原因: Static BERT models often rely on lexical and syntactic overlap, and both functions share common Java IO patterns (BufferedReader, InputStreamReader, readLine) and variable names (reader, line, url). This leads the model to overestimate similarity, ignoring differences in method names, logic structure, and output handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the overall functionality is completely different: one is a source code viewer, the other is a simple HTTP line fetcher. Despite low-level IO similarities, the high-level purpose and output are distinct.
- 共享行为: Both use BufferedReader, InputStreamReader, and readLine() to read from a stream；Both handle exceptions (one catches Exception, the other throws Exception)；Both involve URL or file-related operations
- 行为差异: Function A reads multiple lines and builds an HTML string, Function B reads only the first line and returns it；Function A uses getClass().getResource() to locate a local file, Function B creates a URL object from a string and opens an HTTP connection；Function A applies syntax highlighting to each line, Function B does no formatting；Function A explicitly disconnects the HTTP connection, Function B does not
- 修正建议: Include more negative examples with similar API usage but different semantics in training；Use method-level context or code summaries to capture high-level purpose；Enhance model's ability to distinguish between boilerplate IO sequences and actual semantic logic

### case_id=6088 FN benchmark_preference_bias

- 方法: `doGet` vs `createJAR`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET requests for portal pages, including user authentication, page retrieval, caching, and logging.
- B 摘要: Creates a JAR file or directory, copies a resource JAR, and serializes a document object to a file.
- 静态失败原因: The low token Jaccard (0.082) and lack of overlapping keywords indicate negligible lexical similarity. Static BERT models rely on token-level patterns and would correctly predict non-clone; however, BCB's broader standard may consider them clones, leading to a false negative from the model's perspective.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have considered the presence of file creation and stream writing as a functional similarity, possibly viewing both as 'file output operations' despite different contexts. Alternatively, the annotation might be erroneous or based on a loose interpretation of Type-4 clones.
- 共享行为: Both involve file I/O operations (creating/writing files).
- 行为差异: Function A processes HTTP requests and manages web pages; Function B creates JAR archives and serializes objects.；Function A includes user permission checks and caching logic; Function B focuses solely on file and stream operations.；Function A uses servlet API and portal context; Function B uses file channels and object streams.；Function A has extensive error handling and logging; Function B has minimal exception handling.
- 修正建议: Consider incorporating structural or semantic features beyond token overlap.；Train models to recognize broader clone types (Type-4) by using data with diverse functional similarities.；Use control-flow or data-flow graphs to capture partial functionality overlap.

### case_id=6089 FN partial_functionality

- 方法: `doGet` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve and display a portal page, with access control, logging, and caching.
- B 摘要: Copies a file from input to output using character streams.
- 静态失败原因: Static model likely relies on lexical and structural features; low token overlap (0.059) and different method signatures led to non-clone prediction. It did not detect the small file copy fragment as semantically equivalent to B.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone due to the presence of file copy logic in A, albeit minor, considering Type-4 semantic similarity of data transfer. However, the core functionality differs significantly.
- 共享行为: Both involve reading and writing data; in A, caching writes page to file, in B, entire method is file copy.
- 行为差异: A uses Servlet API and portal context; B uses pure Java I/O.；A has complex control flow (try-catch, conditionals, error handling); B is a simple loop.；A's file write is a side part for caching; B's entire purpose is file copy.
- 修正建议: Improve detection of partial functionality clones by considering that a function may contain a sub-task similar to another function.；Use semantic decomposition to identify smaller functional units within large methods.

### case_id=6090 FP lexical_or_api_overlap

- 方法: `main` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a dataset from a zip file, parses probabilistic rules, evaluates performance using a pooled PR curve measure, and outputs averaged results.
- B 摘要: Handles GUI action events to configure external tool paths (Graphviz, ImageMagick), UI settings (font, look-and-feel), and country code, then applies settings and optionally restarts.
- 静态失败原因: Static BERT models may over-rely on lexical overlap (e.g., both use File, BufferedInputStream, etc.) and structural patterns (loops, if-else), missing the deep semantic difference in purpose and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because there is no semantic or functional similarity: one is a main method for performance evaluation, the other is a GUI event handler for settings.
- 共享行为: Both use file I/O (reading/writing) and conditional control flow.
- 行为差异: Function A is batch processing for scientific evaluation; Function B is interactive GUI preference management.；Function A operates on zip entries and rule parsing; Function B handles user selections and UI updates.；Their overall purpose and domain are completely unrelated.
- 修正建议: Incorporate data flow and control flow analysis to capture high-level intent.；Use larger context windows or sequence of method calls to distinguish domains.；Train on more diverse negative examples to reduce false positives from superficial API similarity.

### case_id=6091 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses HTML from a given URL, extracts links and anchor texts, and returns them as Vectors.
- B 摘要: Reads the entire content of a fixed localhost URL into a String variable with no processing.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the overlapping API calls (URL, BufferedReader, readLine) and missed the drastic difference in post-processing and return type.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have different high-level purposes despite sharing low-level I/O steps; here one is a link extractor, the other a simplistic page reader.
- 共享行为: Both open a URL connection and read its content using BufferedReader.
- 行为差异: getLinksFromURLFast parses HTML to extract links and texts; run() simply discards the read data.；getLinksFromURLFast returns structured data; run() has no return value.；getLinksFromURLFast uses a configurable URL parameter; run() uses a hardcoded URL.
- 修正建议: Train with more examples that differentiate I/O boilerplate from core logic.；Incorporate structure-aware representations like data flow or return types.

### case_id=6092 FN partial_functionality

- 方法: `read` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file or URL and returns a status code indicating success or open error.
- B 摘要: Performs a version check by reading a URL, parsing version/build info, and displaying GUI messages.
- 静态失败原因: Static models like BERT rely on token overlap and surface structure; with only 0.25 token Jaccard and different method names, return types, and control flows (conditional vs loop), the model fails to recognize the shared network IO pattern and thus predicts non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as 'read from external resource (URL/file) with error handling', a common pattern. Despite different high-level purposes (generic read vs version check), the partial functional similarity in network IO and exception handling may lead to a Type-3/Type-4 clone annotation.
- 共享行为: Both open a URL and create an InputStream.；Both catch IOException and handle errors.；Both perform reading operations from an input source.
- 行为差异: A can read from either URL or file; B only reads from URL.；A returns an integer status; B is void.；A delegates actual reading to another method; B reads lines and parses specific version/build strings.；B shows/hides a wait cursor and displays GUI messages; A does not.
- 修正建议: Enrich feature representation with control-flow and data-flow graphs to capture common IO patterns.；Use a model that abstracts over specific variable and method names, focusing on API usage (URL, openStream, IOException).；Include type information with awareness of different return types (void vs int) but still detect partial similarity.；Train on examples of diverse implementations with common sub-patterns to improve recognition of Type-3/Type-4 clones.

### case_id=6093 FN partial_functionality

- 方法: `main` vs `login`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Demonstrates posting a templatized action to the RenRen API using hardcoded parameters and printing the response.
- B 摘要: Logs into the LOLA service by sending a POST request with email and password, then extracts and returns the session ID.
- 静态失败原因: Static BERT models rely on token overlap and structural similarity; these functions have low token Jaccard similarity (0.14) and different method names and constant values, causing the model to miss the shared high-level behavior of HTTP POST.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions implement the same high-level pattern of sending an HTTP POST request with URL-encoded data and processing the response, despite differences in API details and purpose.
- 共享行为: Both functions perform an HTTP POST request to a URL, write data to the request body, and read the response line by line.
- 行为差异: Function A uses hardcoded parameters and prints the response, while Function B uses dynamic credentials and returns the session ID.；Function A targets the RenRen API, Function B targets the LOLA service.；Function A is a main method with no return, Function B returns a string.
- 修正建议: Improve representation to capture high-level API calls (e.g., HTTP operations) through function call graph or abstract patterns.；Use contrastive learning on pairs with similar I/O behaviors but different surface forms.；Incorporate type information or API usage embeddings.

### case_id=6094 FP lexical_or_api_overlap

- 方法: `createSettingsIfNecessary` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Creates a settings file if it does not exist by copying a default resource.
- B 摘要: Reads and parses a configuration file into multiple sets and maps for Tibetan transliteration.
- 静态失败原因: The static model may have been misled by the presence of similar API elements (FileOutputStream, IOUtils.copy vs. BufferedReader, StringTokenizer) and the shared IOException handling, overlooking the vast difference in functionality. Low token Jaccard (0.045) suggests the model relied on structural or API-level patterns rather than semantic understanding.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely not consider these clones because they perform fundamentally different tasks (settings initialization vs. data parsing) with no shared algorithmic core.
- 共享行为: Both perform file I/O operations；Both handle potential exceptions (IOException)
- 行为差异: Function A creates a file and copies a resource; Function B reads and parses a file line-by-line；Function A terminates after file copy; Function B builds multiple data structures；Function B has complex tokenization and state tracking; Function A is straightforward
- 修正建议: Incorporate data-flow analysis to capture that one function writes and the other reads；Use control-flow graph comparison to highlight divergent logic；Increase sensitivity to method-level semantics via contrastive learning on diverse tasks

### case_id=6095 FN partial_functionality

- 方法: `copyResource` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using byte streams.
- B 摘要: Reads a log file line by line, filters lines based on a condition, and writes the filtered lines to a new file.
- 静态失败原因: Static BERT models like GraphCodeBERT rely heavily on token-level and structural similarities which are low here (Jaccard 0.159). They also may not capture the high-level semantic similarity of file I/O operations when the APIs differ (Stream vs Reader/Writer). The model likely focused on surface differences such as method signature, variable names, and different control flow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators may have viewed both as 'copying data from a source to a destination' despite the filtering in B, considering it a variant of copying. The presence of read-write loop and stream handling might be seen as Type-3 clone with minor changes (line filtering added). BCB's broad clone definition includes functions with similar high-level functionality even if implementation details differ.
- 共享行为: Both perform file I/O: open input source, read data, write data to output destination, close streams.
- 行为差异: Function A copies bytes without processing; Function B processes lines with filtering logic.；Function A handles URL or file input; Function B only handles file input.；Function A uses InputStream/OutputStream; Function B uses Reader/Writer.；Different error handling: A throws Exception, B catches IOException.
- 修正建议: Improve training data to include more diverse I/O patterns that share high-level semantics.；Use dataflow analysis to capture read-write loop patterns irrespective of API.；Incorporate task-level representations (e.g., 'copy' vs 'filtered copy') to generalize across different I/O APIs.

### case_id=6096 FP boilerplate_overlap

- 方法: `testAddLinkToImage` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: A test method that copies image resources from classpath to a report folder and adds links to them.
- B 摘要: A private static method that parses comma-separated string constants into various sets and hash maps for a Tibetan transliteration system.
- 静态失败原因: The static BERT model likely overfocused on overlapping boilerplate patterns (e.g., 'new HashSet()', 'StringTokenizer', 'while (sTok.hasMoreTokens())') and missed the high-level semantic context and domain differences. The token Jaccard similarity is very low (0.03), suggesting the model may have been misled by syntactic similarities in unrelated code blocks.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels them as non-clones because they are semantically unrelated: one is a test case for report generation, the other is a data parsing/initialization routine. Even though both contain loops and collection usage, their overall purpose and outputs are completely different.
- 共享行为: Both use loops to process data (InputStream/IOUtils.copy vs StringTokenizer while loops)；Both involve creating and populating collections (Set and Map)
- 行为差异: Function A is a test method for adding links to images; Function B is a data initialization method for a transliteration system.；Function A performs file I/O (copying resources); Function B does not perform file I/O (uses string tokens).；Function A adds links to a report; Function B populates sets and maps for further processing.
- 修正建议: Improve model's ability to capture global program semantics rather than local token patterns.；Incorporate data flow and control flow analysis to distinguish between different usage of similar APIs.；Use larger context windows or graph-based representations to understand the overall function purpose.

### case_id=6097 FP lexical_or_api_overlap

- 方法: `truncate` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Compresses an old log file into a zip backup in a backup directory if the file is older than the JVM start time.
- B 摘要: Handles action events for a settings dialog by opening file choosers and saving preferences for various tools like Graphviz and ImageMagick.
- 静态失败原因: The static model likely over-relied on superficial lexical overlaps such as File, try-catch blocks, and similar exception handling patterns, ignoring the high-level semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the functions have entirely different purposes and no meaningful shared functionality.
- 行为差异: Function A performs file compression into a zip archive; Function B handles UI events and stores settings.；Function A deals with log file rotation; Function B deals with user-configurable tool paths.；Function A throws AppenderInitializationError on failure; Function B uses logging and UI updates.；Function A uses ZipOutputStream and FileInputStream; Function B uses JFileChooser and preference storage.
- 修正建议: Incorporate control-flow and data-flow analysis to distinguish file I/O from UI event handling.；Use AST-based features that capture method structure and dependencies.；Train on more diverse examples with similar API usage but different semantics.

### case_id=6098 FP lexical_or_api_overlap

- 方法: `main` vs `gzip`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapters from a Prolog file and writes them to a JAR.
- B 摘要: Compresses files from a directory into a gzip file.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by common token sequences such as 'FileInputStream', 'read', 'write', 'buffer', and 'System.out.println', which appear in both functions. The model may have focused on these superficial lexical and API similarities without understanding the distinct data transformations and overall goals.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone (0) because the functions have completely different functional semantics despite some low-level API overlap. BCB requires functional similarity, not just shared library calls.
- 共享行为: Both perform file I/O operations；Both read from a file and write to an output stream；Both use buffered byte reading in a loop；Both are static methods that perform a processing task
- 行为差异: Different overall purpose: adapter generation vs. compression；Different input handling: command-line arguments vs. hardcoded paths；Different output format: JAR vs. gzip；Different core operations: Prolog parsing/serialization vs. byte compression
- 修正建议: Incorporate dataflow analysis to distinguish different operations on data.；Use contrastive learning with hard negatives that have API overlap but different semantics.；Add attention to high-level control flow and method call sequences beyond token matching.

### case_id=6099 FN benchmark_preference_bias

- 方法: `doGet` vs `createButtonCopyToClipboard`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to display a page after permission checks and logging.
- B 摘要: Creates a SWT button that copies environment report to clipboard on click.
- 静态失败原因: The model correctly predicted non-clone due to very low token overlap (0.0156) and distinct API usage; BCB's label is likely an error or based on extremely loose criteria.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'UI-related actions' or 'user-triggered operations', but this is a very broad interpretation; likely an annotation error in the benchmark.
- 共享行为: No significant shared behavior; both involve user interaction but in completely different contexts.
- 行为差异: Function A processes HTTP requests and generates HTML responses; Function B creates a GUI button.；A involves complex logic for page retrieval, caching, and logging; B is a simple UI setup.；A uses servlet APIs; B uses SWT and clipboard utilities.；A has multiple error handling and permission checks; B has none.
- 修正建议: Review BCB annotation to ensure consistency; consider removing or correcting this pair.

### case_id=6100 FN benchmark_preference_bias

- 方法: `getFile` vs `recurseFiles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies a specific XML attribute, saves to a temporary file, and returns the file path.
- B 摘要: Recursively traverses a directory, skipping zip files, and adds each non-zip file to a ZipArchiveOutputStream for archiving.
- 静态失败原因: Static BERT models rely on lexical and structural overlap; with very low token Jaccard (0.0986) and no shared API calls or control flow, they correctly predicted non-clone. The model failed to align with BCB's possibly overly broad clone criteria.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone under a very broad interpretation of 'file processing utility' or due to dataset annotation noise; the functions share generic I/O patterns but differ fundamentally in purpose.
- 共享行为: Both involve file I/O operations (reading from a stream/file, writing to another stream/file).；Both handle IOException.；Both are static utility methods.
- 行为差异: A involves network download and XML parsing/modification; B involves directory recursion and zip archiving.；A uses Channels and FileOutputStream; B uses IOUtils.copy and ZipArchiveOutputStream.；A modifies content (XML attribute); B merely copies bytes.
- 修正建议: Re-evaluate BCB labeling for this pair; if indeed clone, incorporate broader functional similarity metrics beyond local syntax.；Alternatively, ignore this pair as noise due to inconsistent annotation.

### case_id=6101 FP lexical_or_api_overlap

- 方法: `postXml` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with XML content and returns the response string.
- B 摘要: Checks for software upgrades by querying a remote server, parsing XML, and updating local database and UI.
- 静态失败原因: The static model likely overfitted on shared API calls (URLConnection, BufferedReader) and generic string operations, ignoring the distinct control flow, business logic, and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled non-clone because the functions have fundamentally different purposes and logic, despite sharing some low-level I/O patterns. The high-level semantics are unrelated.
- 共享行为: Both use URLConnection to fetch data from a URL；Both read response line by line using BufferedReader
- 行为差异: Function A is a generic HTTP POST utility; Function B is a specific upgrade-checking routine；Function B includes database operations, UI updates, and complex XML parsing, which are absent in A；Function A throws RuntimeException on IOException; Function B throws Exception and handles specific error conditions
- 修正建议: Improve model training with more diverse examples of non-clone pairs to reduce sensitivity to common API usage；Incorporate control-flow or data-flow analysis to capture program semantics beyond token sequences

### case_id=6102 FN partial_functionality

- 方法: `fileDownload` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL to a local directory, writing raw bytes to a hardcoded 'download.pdf' file.
- B 摘要: Reads lines from a URL, parses them into version, url, and additional information fields, and notifies listeners upon completion.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the different output behaviors (file writing vs. line parsing) and different method names, causing low similarity. The token overlap is low (0.17), and models may miss the shared URL-reading structure as a significant commonality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both involve reading from a URL with similar structure (try-catch, BufferedReader, stream closing). The overall task of 'downloading/reading URL content' is deemed similar enough for a Type-4 clone in BigCloneBench.
- 共享行为: Open a URL；Read data using BufferedReader；Handle exceptions (IOException, etc.)；Close the input stream
- 行为差异: Function A writes raw bytes to a file; Function B parses lines into fields.；Function A uses byte-level reading; Function B uses line-level reading.；Function A hardcodes the output filename; Function B stores parsed data in fields.；Function B notifies listeners on completion; Function A does not.
- 修正建议: Improve representation of high-level API usage (e.g., URL opening) and structural patterns.；Incorporate dataflow to detect that both read from URL and handle exceptions even if downstream differs.

### case_id=6103 FN benchmark_preference_bias

- 方法: `copyResource` vs `addFileToTarGz`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file.
- B 摘要: Adds a file or directory recursively to a TarGz archive.
- 静态失败原因: Static BERT models may have detected the low Jaccard similarity (0.177) and the different method names and operations, correctly predicting non-clone. The FN error here is due to BCB labeling as clone, not the model's fault. The model did not fail; it correctly predicted non-clone according to strict semantics.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider them clones because both involve reading a file and writing its contents to an output stream, which is a common pattern that could be seen as type-3/type-4 similarity. However, the specific operations (plain copy vs tar archive addition) are distinct enough that many annotators would mark as non-clone.
- 共享行为: Both read from a file input stream；Both write to an output stream；Both perform byte-level I/O copying
- 行为差异: Function A copies to a plain file; Function B adds to a tar archive；Function A handles both URL and file sources; Function B only handles file source；Function B handles directories recursively and creates tar entries; Function A does not；Function A throws generic Exception; Function B throws IOException
- 修正建议: Clarify the definition of clone in benchmark to distinguish between partial I/O similarity and full functional equivalence；Consider using more fine-grained recovery of semantic roles in models to avoid over-matching on I/O patterns

### case_id=6104 FP lexical_or_api_overlap

- 方法: `main` vs `createNew`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Prolog file, parses it, generates adapter classes and writes them into a JAR file.
- B 摘要: Creates a new resource file under a folder if the client is allowed and the file name matches '.request' or '.tokens', copying content from an input stream.
- 静态失败原因: The static BERT/GraphCodeBERT model likely over-relied on lexical overlap (e.g., 'File', 'IOException', 'return', 'new File', 'FileOutputStream') and common patterns like error handling, ignoring the overall semantic and structural differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the functions have different names, signatures, return types, and perform entirely different tasks with no shared algorithmic structure. The low token Jaccard also supports this.
- 共享行为: Both perform file I/O operations using Java's File API.；Both handle IOException and use try-catch or try-finally blocks.
- 行为差异: Function A is a static main method for a command-line tool; Function B is an instance method for resource creation.；Function A parses Prolog code and generates multiple Java classes; Function B simply writes an input stream to a file and returns a resource object.；Function A has complex logic with multiple sub-steps (parsing, visiting, generating, assembling JAR); Function B has simple conditional logic.；Function A deals with class loaders, bytecode writing, and serialization; Function B does not.
- 修正建议: Incorporate method name, class context, and argument/return type information as features.；Use control flow and data flow analysis to capture distinct logic.；Train on more diverse examples to reduce sensitivity to common API usage patterns.

### case_id=6105 FP partial_functionality

- 方法: `readTwitterFead` vs `readURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches a Twitter feed from a hardcoded URL using Apache HttpClient and returns the response as a string.
- B 摘要: Reads a given URL using Java's URL.openStream and prints each line to the console, closing streams in a finally block.
- 静态失败原因: The static model may have been misled by structural similarities such as the try-catch blocks, BufferedReader loop, and use of e.printStackTrace(), which form a common boilerplate for network I/O. The model likely overlooked the differences in return types, HTTP client libraries, and output behaviors (building a string vs printing to console), leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels these as non-clones (Type-4) because although they share a common network reading pattern, their overall purposes and behaviors are different: one is a dedicated Twitter feed fetcher returning a string, the other is a generic URL content printer. The differences in API usage, error handling, and output direction outweigh the structural similarity.
- 共享行为: Both read data from a URL over the network；Both use BufferedReader to read lines of text；Both handle exceptions with printStackTrace
- 行为差异: Function A returns a concatenated string; Function B prints lines to console and returns void；Function A uses Apache HttpClient (HttpGet, DefaultHttpClient); Function B uses java.net.URL.openStream；Function A checks HTTP status code (200) and logs failure; Function B has no such check；Function A does not close streams; Function B explicitly closes streams in finally block
- 修正建议: Incorporate data flow analysis to track how the result of the read operation is used (e.g., return vs. print)；Consider method signatures and return types as features in the clone detection model；Add attention to the specific API calls (e.g., HttpClient vs  URL.openStream) to distinguish similar patterns with different implementations；Enhance training data with examples that share sub-task structure but differ in overall functionality

### case_id=6106 FP library_context_missing

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `context_recovery_then_dynamic`；动态可解性: `low`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated string fields to populate sets and hash maps, and reads an INI file to populate additional data structures.
- B 摘要: Copies a file from a source to a target using FileChannel's transferTo method.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized the presence of common I/O related keywords like 'IOException', 'File', and 'FileChannel', and was misled by the long, truncated code of function A containing file-reading logic, leading to a false positive.
- 静态 case study: 该类错误缺少关键上下文或需要深层语义，纯静态方法不可靠。
- 动态 case study: 动态执行价值较低：样本可能依赖库、框架、网络、GUI、数据库或项目上下文，需要先恢复环境或 mock 依赖。
- BCB 偏好解释: BCB likely labels this as non-clone because the two functions have completely different purposes and only share trivial I/O aspects, which does not constitute functional similarity even in broad Type-4 terms.
- 共享行为: Both involve file I/O operations (reading vs copying)；Both handle IOException (one catches, one throws)
- 行为差异: Function A is a complex data initialization routine; function B is a simple file copy utility；Function A parses string tokens and processes configuration files; function B transfers bytes between channels；Function A modifies multiple global collections; function B has no side effects beyond copying file content
- 修正建议: Incorporate control-flow and data-dependency analysis to distinguish between different I/O patterns；Use semantic similarity that accounts for overall program purpose rather than API token overlap；Train on more diverse negative pairs with superficial API similarity but different semantics

### case_id=6107 FN partial_functionality

- 方法: `getFile` vs `parse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies an XML attribute, and saves it to a temporary location, returning the file path.
- B 摘要: Parses an input stream, optionally writing it to a file if the resource name is in a map, otherwise delegates to a downstream parser.
- 静态失败原因: Static BERT/CodeBERT relies on lexical overlap and general embeddings; the low token Jaccard (0.096) and different method names/control flow make the abstract I/O similarity hard to capture.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'file downloading and saving' tasks with I/O and XML processing, interpreting them as type-3/4 clones with partial functionality similarity.
- 共享行为: Both write data from an input stream to a file output stream；Both use FileOutputStream for writing；Both involve conditional file existence or resource name check
- 行为差异: A always downloads and modifies WSDL, B conditionally writes or delegates parsing；A uses URL/URLConnection to obtain input, B receives an InputStream directly；A returns file path, B returns void；A handles multiple specific exceptions, B throws generic exceptions
- 修正建议: Incorporate dataflow analysis to highlight common I/O operations；Use structure-based representations like AST with path annotations for streams and file operations

### case_id=6108 FP lexical_or_api_overlap

- 方法: `main` vs `decodeFileToFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Prolog file, parses it, generates adapter code, and writes a JAR file with serialized adapter layer and class files.
- B 摘要: Decodes a Base64-encoded input file and writes the decoded bytes to an output file.
- 静态失败原因: The static model might have focused on the overlapping tokens related to file I/O (e.g., 'FileInputStream', 'BufferedOutputStream', 'IOException') and ignored the overall structure and logic. The functions are both relatively long and share some low-level patterns, but the semantic cores are different.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels them as non-clones because they have entirely different high-level functionalities: adapter generation vs. Base64 decoding. The only commonality is basic file I/O, which is too generic to consider them clones even under broad Type-4.
- 共享行为: Both read from an input file using streams；Both write to an output file using streams；Both handle IOException by printing stack trace
- 行为差异: A has complex parsing and code generation logic; B is simple byte copying；A handles multiple files and JAR packaging; B decodes Base64；A uses many external classes (Parser, ClassWriter, etc.); B uses Base64 and standard I/O；A has command-line argument parsing; B has no argument parsing (takes two strings)
- 修正建议: Use higher-level semantic features that capture the overall task (e.g., method name, class context, control flow)；Include structural information like AST or CFG to differentiate between different high-level scenarios；Train on more diverse examples to avoid over-reliance on file I/O token patterns

### case_id=6109 FN partial_functionality

- 方法: `populateResources` vs `login`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads template resources and images from predefined paths and saves them.
- B 摘要: Logs into a remote service via HTTP POST and returns a session ID.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed because the methods have very low token overlap (0.075) and completely different keywords (populateResources vs login, templates vs login, etc.). The model relied on surface form and AST structure; although both have similar control flow (try-catch, loops, BufferedReader), the semantic context diverges, leading to low embedding similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might have considered the shared I/O boilerplate and exception handling as sufficient structural similarity for a broad Type-3 clone, but the essential functionality differs significantly.
- 共享行为: Both use URL to open connections and read data；Both use BufferedReader and InputStreamReader；Both handle exceptions with try-catch
- 行为差异: Different primary purpose: resource loading vs. authentication；Function A is static, returns void; Function B returns a String (session ID)；Function A reads local files from classpath; Function B sends HTTP POST to remote server；Function A saves objects to database; Function B does not persist locally
- 修正建议: Improve representation to capture high-level intent beyond token overlap；Use structural embeddings that can distinguish between different I/O patterns；Incorporate domain-specific knowledge about method names and parameter types

### case_id=6110 FP lexical_or_api_overlap

- 方法: `getUser` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from a database or config file, parsing lines to find a matching login and saving the user.
- B 摘要: Fetches a URL and reads its content line by line without processing it.
- 静态失败原因: Static BERT/GraphCodeBERT methods often rely on lexical and structural overlap. The high overlap of API tokens (URL, BufferedReader, readLine) and the similar control flow pattern (try-catch, while loop) mislead the model into thinking they are functionally similar, while ignoring the core difference in data processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have completely different purposes (user authentication vs. web page retrieval), and the shared API usage is only superficial boilerplate. Significant behavioral differences in data handling and output reduce functional similarity.
- 共享行为: Both use URL, BufferedReader, InputStreamReader, and readLine() to read from a stream.；Both have try-catch blocks for exceptions.；Both use similar boilerplate for opening streams.
- 行为差异: A processes each line to extract tokens and conditionally creates a User object, while B does nothing with the read lines.；A may save a user object to a DAO, while B does not perform any save or transformative action.；A returns a User object, while B is void.；A reads from a classpath resource file, while B reads from a remote HTTP URL.
- 修正建议: Incorporate data flow analysis to track how variables are used after reading.；Add training examples that distinguish between reading for side effects vs. reading to transform data.；Use contrastive learning on tasks with similar API usage but different semantics.

### case_id=6111 FP boilerplate_overlap

- 方法: `doVersionCheck` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a new version of jEdit by reading version and build from a remote URL and comparing with current build.
- B 摘要: Loads content from a URL with optional basic authentication and writes it to a temporary file while updating a status label.
- 静态失败原因: The model likely overfitted to boilerplate code like URL opening, BufferedReader, and readLine loop, ignoring the divergent post-processing and distinct outputs.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators likely saw that the overall goals (version check vs. file download) are entirely different despite similar I/O patterns, making these non-clones under Type-4 partial similarity guidelines.
- 共享行为: Both open a URL and read lines using BufferedReader.
- 行为差异: A reads specific .version and .build lines to compare versions; B reads all lines and writes to a file.；A handles authentication via properties; B implements Basic Authentication via BASE64 encoding.；A catches IOException and shows error dialog; B throws IOException.；A updates UI with version-check messages; B updates a status label with file size.
- 修正建议: Add data-flow analysis to track how read data is used after the loop.；Incorporate task-specific embeddings (e.g., named entity recognition for version strings vs. file I/O).；Use contrastive learning examples that distinguish similar I/O patterns with different semantics.

### case_id=6112 FN partial_functionality

- 方法: `getResourceAsStream` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches a resource from a URL, caches it locally if needed, and returns an InputStream.
- B 摘要: Copies a file from one location to another using FileChannel transferTo.
- 静态失败原因: Low token Jaccard (0.155), different method names, different APIs (BufferedStream vs FileChannel), and distinct overall purposes caused the model to miss the underlying I/O similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both functions perform I/O data transfer from a source to a sink, which aligns with Type-4 functionality similarity despite different contexts.
- 共享行为: Both involve reading data from an input source and writing it to an output destination.；Both close streams/channels in finally blocks to release resources.
- 行为差异: Code_a is a resource caching mechanism with HTTP connectivity and conditional caching logic; code_b is a straightforward file copy.；Code_a uses BufferedInputStream/OutputStream with byte-by-byte copy; code_b uses NIO FileChannel transferTo for efficient copy.；Code_a returns an InputStream; code_b is void and throws IOException.
- 修正建议: Use graph-based or data flow representations to capture common I/O patterns.；Incorporate structural alignment that can match different API invocations with similar effects (e.g., write vs transferTo).

### case_id=6113 FN benchmark_preference_bias

- 方法: `createOutputStream` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Creates a BufferedWriter that copies entries from a zip input file to a zip output file, skipping 'content.xml', then adds a new 'content.xml' entry.
- B 摘要: Downloads a WSDL file from a URL, modifies its soap:address location, writes to a temp file, and returns the file path.
- 静态失败原因: Low token overlap (0.095) and different method names, plus different domain-specific APIs (zip vs. wsdl) led the model to focus on surface differences.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label these as clones due to both involving complex file/stream manipulation patterns and being considered broad Type-4 or partial functionality (e.g., both read/write files with buffering). However, this is a very weak connection.
- 共享行为: Both perform file I/O operations；Both use streams and buffers
- 行为差异: Function A processes zip files and returns a BufferedWriter; Function B downloads and modifies XML files and returns a file path；Function A skips and later adds a specific entry; Function B edits XML structure；Function A uses ZipInputStream/OutputStream; Function B uses URLConnection and NIO channels
- 修正建议: Train with better Type-4/partial clone examples；Use semantic-aware features beyond token overlap

### case_id=6114 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a localized properties file by reading, optionally copying from English default, then updating or adding a message key-value pair.
- B 摘要: Copies a file from source to destination using a buffered stream.
- 静态失败原因: Static BERT methods rely on token-level embeddings and may not capture high-level functional similarity due to low token Jaccard and different method names; they focus on surface-level syntax and semantics, missing the shared sub-task of file copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as clone because both functions involve file copying as a core step, and the overall task is to handle file content transfer. The broad similarity in I/O operations and file manipulation is considered sufficient for Type-3/4 clone.
- 共享行为: Both read from an input stream and write to an output stream.；Both involve file I/O operations.
- 行为差异: A includes properties file parsing and manipulation, conditional file copy if missing, and handles key-value pairs; B is a simple byte-level copy without parsing.；A writes after modifying content; B directly copies bytes.；A has error handling with catch block; B throws IOException.
- 修正建议: Improve model to recognize subfunctional similarity by using dataflow or control-flow analysis.；Incorporate task-level embeddings or broader context to capture common I/O patterns.

### case_id=6115 FN partial_functionality

- 方法: `loadMFileViaWeb` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads an M-file from a web URL, reads its lines, parses into a UserFunction, and returns it.
- B 摘要: Reads data from a URL or local file stream and returns a status code after processing.
- 静态失败原因: The static BERT model likely focused on the low token Jaccard similarity (0.17) and distinct return types, missing the underlying structural overlap in the URL reading and exception handling patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a clone because both functions share the core pattern of opening a URL stream and reading input, which aligns with broad Type-3/4 clone definitions that consider partial functional similarity.
- 共享行为: Both open a URL connection and read from an InputStream；Both handle exceptions using try-catch；Both involve reading data from external sources (web or file)
- 行为差异: A reads lines of text, concatenates, and parses as M-file code into a UserFunction; B reads arbitrary data and returns an int status；A always uses a URL constructed from codeBase and directory; B can also read local files；A has debug logging and sets function name; B does not；A throws a library exception on failure; B sets a status field
- 修正建议: Include dataflow or control flow features in the model；Use graph-based representations to capture shared API call sequences；Train with more examples of partial functionality clones

### case_id=6116 FN partial_functionality

- 方法: `getJSONData` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches JSON data from a given URL using Apache HttpClient and parses it into a JSONObject.
- B 摘要: Fetches HTML content from a hardcoded URL using URLConnection and logs the raw response string.
- 静态失败原因: Static BERT/GraphCodeBERT methods rely heavily on token-level overlap and structural similarity; the token Jaccard is low (0.24). Different HTTP libraries (HttpClient vs URLConnection) and return types (JSONObject vs void) cause low embedding similarity. The model fails to recognize the underlying common pattern of reading from a URL due to these surface-level differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a clone because both functions perform an HTTP GET to retrieve content from a URL and read it line by line. The core data retrieval and reading pattern is considered similar enough, and the JSON parsing in A is seen as an additional step that does not negate the clone relationship.
- 共享行为: Both open an HTTP connection to a URL；Both read the response line by line using BufferedReader；Both accumulate the read lines into a string buffer；Both close the reader after reading
- 行为差异: Function A uses Apache HttpClient while B uses standard URLConnection；Function A parses the response as JSON and returns a JSONObject; B logs the raw string and returns void；Function A takes a URL parameter; B uses a hardcoded URL；Function A handles exceptions internally; B declares them
- 修正建议: Use AST-based differencing that focuses on control flow and I/O patterns rather than exact API usage.；Train or augment with clone pairs that have different library choices but similar logic.；Incorporate data flow analysis to detect the common pattern of 'open connection, read lines, accumulate' despite different APIs.；Consider function-level semantic similarity via program analysis (e.g., symbolic execution) to abstract away library-specific details.

### case_id=6117 FP boilerplate_overlap

- 方法: `readPage` vs `getLinksFromURLFast`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: readPage reads a URL line-by-line, optionally skipping comment lines starting with '#', and returns the concatenated HTML string.
- B 摘要: getLinksFromURLFast reads a URL, parses it with regex to extract all hyperlinks and their text, converts relative URLs to absolute, and returns an array of two Vectors containing links and texts.
- 静态失败原因: The static BERT/GraphCodeBERT model likely focused on the overlapping API calls (e.g., URL, BufferedReader, InputStreamReader) and similar control flow (while loop), but did not capture the significant differences in post-processing logic. The model may treat such boilerplate patterns as strong evidence of a clone, ignoring the distinct functional outcomes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench typically labels non-clones when methods have different high-level functionality, even if they share common infrastructure like reading from a URL. Since the core purpose differs (retrieving raw content vs. extracting links), BCB would mark this as non-clone (Type-4 or non-clone).
- 共享行为: Both open a URL connection and read data using BufferedReader.；Both use while loops to process lines from the buffered reader.；Both handle exceptions thrown by IO operations.；Both involve reading HTML content from the web.
- 行为差异: readPage returns raw HTML (optionally filtered to remove comment lines), whereas getLinksFromURLFast extracts and returns a structured set of links and their text.；readPage processes lines individually and optionally skips lines starting with '#', while getLinksFromURLFast concatenates all lines and then uses regular expressions to find anchor tags.；getLinksFromURLFast performs complex URL manipulation (making links absolute) and uses multiple regex patterns, which readPage does not.；The output types are completely different: String vs. Vector[] of two Vectors.
- 修正建议: Incorporate data-flow analysis to track how data is transformed after reading (e.g., filter vs. regex extraction).；Use a more structured representation that captures the high-level purpose, such as an AST with control and data dependencies.；Include information about return types and their semantics to distinguish different tasks.；Train the model to downweight common I/O setup patterns when the rest of the logic diverges.

### case_id=6118 FP boilerplate_overlap

- 方法: `readData` vs `descargarArchivo`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads and parses configuration data from string tokens and a file into multiple sets and maps.
- B 摘要: Copies a file from a source path to a destination path using file channels.
- 静态失败原因: The model likely overemphasized common boilerplate patterns (try-catch, IOException, File streams) and ignored the fundamentally different semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label them as non-clones because they perform entirely different tasks despite both involving I/O operations.
- 共享行为: Both handle IOException with try-catch blocks
- 行为差异: readData initializes data structures from parsed input; descargarArchivo copies a file；readData is complex with multiple tokenizations and parsing; descargarArchivo is a simple file copy
- 修正建议: Improve detection of distinct functional intents beyond shared exception handling；Enhance semantic understanding of data transformation vs. file transfer

### case_id=6119 FN partial_functionality

- 方法: `doTransfer` vs `getWebPage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request from a servlet to a target URL, copying headers and body, and writing the response back to the servlet response.
- B 摘要: Fetches the content of a given URL as a string by reading line by line.
- 静态失败原因: The static BERT model likely failed due to low token Jaccard similarity and different method names, and it could not recognize the high-level semantic similarity of fetching a web page because it relies on local lexical and structural patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both functions have the core functionality of retrieving a web page over HTTP, which is a semantic similarity that BCB's broad Type-4 annotation captures, ignoring differences in input parameters, return types, and additional details.
- 共享行为: Both retrieve content from a URL via HTTP.；Both handle IOException.
- 行为差异: A performs a full request forwarding with header copying and method setting; B only reads the response.；A writes to the servlet response output stream; B returns a string.；A reads the request body and sends it; B does not send any request body.；A uses HttpURLConnection and handles response codes; B uses URL.openStream() and returns content directly.
- 修正建议: Enhance the model with task-aware embeddings or code summarization to capture high-level intent.；Use data augmentation with pairs of functions that share partial functionality.；Incorporate structural information like data flow or API call patterns.

### case_id=6120 FN boilerplate_overlap

- 方法: `readReferenceText` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a reference text from a file resource given an identifier, returning the content as a string.
- B 摘要: Performs an HTTP POST request and returns the response body as a string.
- 静态失败原因: Static BERT models likely focused on low token overlap (0.24) and the differing method names/parameters, missing the high-level structural similarity of the stream reading pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have considered these clones due to the identical boilerplate code for reading a stream into a string, viewing both as instances of 'input stream reading' with partial functionality similarity.
- 共享行为: Both use BufferedReader and InputStreamReader to read text from an InputStream and build a string using StringBuffer.
- 行为差异: Input source: A reads from a file URL, B reads from an HTTP response.；Error handling: A throws an exception if read fails, B sets error codes and returns null.；Line building: A appends newline characters, B does not.；Method signature: A takes a single string identifier, B takes URL, timeout, and parameter list.
- 修正建议: Incorporate data flow analysis to distinguish input sources.；Use graph-based models to capture control-flow patterns beyond token overlap.；Add semantic role labeling for I/O operations.

### case_id=6121 FP partial_functionality

- 方法: `run` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads version/URL from a remote file and notifies listeners on completion.
- B 摘要: Checks for software upgrades by querying a remote server and processing license/upgrade data, updating UI and database.
- 静态失败原因: The model likely overfocused on the surface-level similarity of using BufferedReader to read from a URL, ignoring the vast differences in control flow, side effects, and overall goals.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically considers functions as clones only if they implement the same or very similar functionality; these two serve entirely different purposes in the system, so BCB correctly labels them as non-clones.
- 共享行为: Both open a URL connection and read lines using BufferedReader.
- 行为差异: Function A parses first two lines as version and URL; function B parses XML-like rows for upgrade data.；Function A has minimal error handling; function B has extensive error handling with specific messages.；Function A notifies listeners; function B updates UI components and database.；Function A is a Runnable; function B is a static method with complex database and UI interactions.
- 修正建议: Enhance model to differentiate between common I/O patterns and actual functional logic.；Include structural features to capture the broader context and sequence of operations.；Use contrastive learning to penalize false positives from shallow lexical or structural overlaps.

### case_id=6122 FN partial_functionality

- 方法: `copyFileChannel` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file to another file using FileChannel, optionally preserving modification time.
- B 摘要: Retrieves a resource by name, caching it locally if needed, and returns an InputStream.
- 静态失败原因: Static BERT models may rely on token-level overlap and API names, which are very different (e.g., 'FileChannel' vs 'URLConnection'), missing the high-level semantic similarity of data copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as file copying utilities (Type-4), despite different sources (local vs. remote), because the core functionality of reading from a source and writing to a destination is similar. The common pattern of stream handling and resource management may qualify as a broad clone.
- 共享行为: Both open input and output streams/files for data transfer.；Both loop to transfer data from source to destination.；Both close resources in finally or catch blocks.；Both handle file modification time (A preserves it, B uses it for caching).
- 行为差异: A uses NIO FileChannel for transfer; B uses BufferedInputStream/BufferedOutputStream.；B involves URL fetching, HTTP headers, and conditional caching logic.；B has complex control flow with multiple conditional branches and exception handling.；B has side effects (caching, print statements) that A lacks.
- 修正建议: Incorporate high-level summarization of program purpose.；Use control-flow graph similarities or data-flow abstractions.；Train on pairs with low lexical overlap but similar high-level behavior.

### case_id=6123 FN partial_functionality

- 方法: `copy` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination with extensive error checking.
- B 摘要: Launches a NexOpen project configuration by validating project structure, processing XML files, setting properties, and executing a build action.
- 静态失败原因: The static BERT model likely relied on token overlap and overall structural similarity, which is very low (Jaccard 0.086), leading it to miss the tenuous I/O pattern similarity that BCB may have considered for clone annotation.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to the shared I/O pattern (file reading/writing with resource management) and the use of similar exception handling, considering a broad Type-4 partial functionality similarity.
- 共享行为: Both perform file I/O operations (reading/writing files).；Both use try-finally blocks for resource cleanup.
- 行为差异: Function A is a simple file copy; Function B involves complex project validation, XML parsing, property setting, and launching.；Function A has no project or configuration context; Function B is tightly integrated with Eclipse and the NexOpen framework.；Function B includes many external library calls, event handling, and multi-step orchestration absent in A.
- 修正建议: Incorporate data-flow analysis to detect shared I/O patterns beyond lexical tokens.；Use project-specific or domain-specific heuristics to recognize common boilerplate for file operations.；Train with broader clone types that allow partial functional overlap.

### case_id=6124 FP boilerplate_overlap

- 方法: `encodeFileToFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Encodes a file to Base64 and writes it to an output file, returning success status.
- B 摘要: Handles UI action commands from a settings dialog, updating preferences and UI components.
- 静态失败原因: The static model likely over-relied on overlapping boilerplate patterns (e.g., try-catch, null checks, common Java keywords) and missed the wide semantic gap in overall task and domain.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the two functions have completely different purposes (file encoding vs. event handling) and share no meaningful common functionality.
- 共享行为: Both use try-catch blocks for exception handling.；Both read or process some input (file stream vs. action command).
- 行为差异: Function A performs file I/O with Base64 encoding; function B handles GUI events and preference updates.；Function A has a simple loop reading and writing bytes; function B has many conditionals and UI component interactions.；Function A returns a boolean; function B is void and triggers UI changes.；Function A deals with Base64 streams; function B deals with Swing components and property settings.
- 修正建议: Incorporate control flow or data flow analysis to better distinguish algorithmic cores from boilerplate.；Use task-specific pretraining or contrastive learning to focus on high-level functionality.；Apply a more robust tokenization or attention mechanism to handle long-range dependencies and large structural differences.

### case_id=6125 FP lexical_or_api_overlap

- 方法: `copy` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Copies a file from source to destination with validation and stream cleanup.
- B 摘要: Reads and parses string data and a configuration file to populate various sets and maps.
- 静态失败原因: The model may have been misled by common file I/O patterns (File, IOException) and exception handling, ignoring the vastly different main operations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have no shared functionality despite some lexical overlap.
- 共享行为: Both involve file I/O operations
- 行为差异: Function A copies file content; Function B initializes data structures from strings and a file.；Function A uses FileInputStream/FileOutputStream; Function B uses StringTokenizer and populates collections.；Function A is a generic file copy utility; Function B is domain-specific for Tibetan transliteration data.
- 修正建议: Improve training to focus on core logic rather than boilerplate；Use dataflow analysis to differentiate I/O consumption vs. production

### case_id=6126 FP lexical_or_api_overlap

- 方法: `scrapeForIsbns` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Scrapes ISBN numbers from a URL using regex pattern matching.
- B 摘要: Extracts YouTube video parameters from a URL to construct a fullscreen video URL.
- 静态失败原因: Static models like GraphCodeBERT may over-rely on lexical and structural overlap (e.g., URL, BufferedReader, while loop, try-catch) and miss the semantic difference in purpose and data processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the overall functionality and output are entirely different (ISBN scraping vs YouTube URL construction), even though they share superficial code patterns.
- 共享行为: Both open a URL and read lines from the input stream；Both use try-catch for exception handling；Both perform pattern matching on each line
- 行为差异: A counts ISBN matches and stores them in a map, B extracts specific video parameters to build a URL；A has retry logic with sleep on connection failure, B does not retry；A uses regex Pattern, B uses string contains and split；A returns an int (count), B returns a String (full URL)
- 修正建议: Improve training to focus on high-level intent (e.g., what data is extracted and how it is used)；Add contrastive examples with similar API usage but different goals

### case_id=6127 FP long_range_semantics

- 方法: `send` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.99`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Sends an email using Apache Commons Email API, handling different formats, headers, attachments, quotas, and sending in a separate thread.
- B 摘要: Reads configuration data from string literals and a file to initialize sets for a Tibetan transliteration system.
- 静态失败原因: The model likely misclassified due to superficial structural similarities (e.g., loops, conditionals, try-catch) and possibly long context diluting the semantic differences.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels non-clones when functions have completely different purposes and no meaningful similarity, as here.
- 行为差异: Function A sends emails; Function B initializes data structures for text processing.；Function A uses email API (MimeMessage, HtmlEmail); Function B uses StringTokenizer and file I/O.；Function A has complex header and attachment handling; Function B populates multiple sets and maps.
- 修正建议: Improve model's ability to capture long-range dependencies and semantic intent.；Use data augmentation with contrasting examples having similar structure but different semantics.

### case_id=6128 FN partial_functionality

- 方法: `getHTML` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML content from a URL using HTTP connection and optionally saves to file.
- B 摘要: Reads a skeleton resource file and parses it into sections separated by '---' delimiter.
- 静态失败原因: Static model likely focused on low token overlap (0.22) and different API/method names (getHTML vs read), missing the shared structural pattern of reading and accumulating lines.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as reading a stream line by line into a StringBuilder, a common pattern for text processing tasks.
- 共享行为: Read lines from a text resource；Use BufferedReader and InputStreamReader；Accumulate lines into StringBuilder
- 行为差异: HTTP connection vs classpath resource loading；Optionally write to file vs store in sections list；Different exception handling；Different input parameters and return types
- 修正建议: Add training examples of BCB-labeled clones with low token overlap but shared line-reading pattern；Use data-flow and structural similarity beyond token overlap

### case_id=6129 FP lexical_or_api_overlap

- 方法: `sendPost` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request to a given URL with parameters and returns the response body as a string.
- B 摘要: Fetches a version string from a fixed URL via HTTP GET and returns it, or null on failure.
- 静态失败原因: The model overemphasized the common boilerplate of opening a URL, reading with BufferedReader, and returning a string, as indicated by the moderate token Jaccard similarity, while missing the critical difference in HTTP method and request body handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because the HTTP method difference (POST vs GET) and parameter handling significantly change the functionality, even though both fetch data from a URL.
- 共享行为: Both open an HTTP connection to a URL；Both read the response line by line with BufferedReader；Both return the response as a String；Both handle exceptions gracefully
- 行为差异: A uses POST method with request body; B uses GET method with no body；A takes two parameters (url, param); B takes no parameters and uses hardcoded URL；A sets additional HTTP headers and connection properties; B does not；A sends data via PrintWriter; B does not send any data
- 修正建议: Incorporate detection of HTTP method-specific calls (setDoOutput, PrintWriter) to differentiate POST from GET；Add dataflow analysis to track whether data is written to the output stream；Consider the presence of input parameters (url vs hardcoded) as a distinguishing feature

### case_id=6130 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `extractFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Event handler that processes action commands to update GUI preferences and settings.
- B 摘要: Static utility that copies a file from input path to output path using a byte buffer.
- 静态失败原因: The model likely focused on overlapping tokens like 'File', 'String', 'out', etc., and misjudged file-related operations as similar, ignoring the broader context and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled non-clone because the functions have entirely different semantics and purposes, despite both involving files.
- 共享行为: Both use file-related operations (file chooser dialog vs. file I/O).
- 行为差异: Function A is an event handler updating GUI state; Function B is a file copy utility.；Function A involves user interaction via dialogs; Function B has no user interaction.；Function A writes to application preferences; Function B writes to a file output stream.；Function A handles multiple commands (e.g., GRAPHVIZ, IMAGEMAGICK); Function B is single-purpose.
- 修正建议: Incorporate dataflow analysis to distinguish file I/O from file chooser dialogs.；Use longer-range attention or structural embeddings to capture method-level semantics.；Add training examples of functions sharing API calls but differing in purpose.

### case_id=6131 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `readIntoList`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Validates Minecraft handshake by checking username and contacting session server.
- B 摘要: Reads HTML from a URL to populate a map of JMenuItems for chat commands.
- 静态失败原因: Static BERT/GraphCodeBERT may have over-relied on overlapping API tokens (BufferedReader, InputStream, URL, catch) and ignored the distinct semantic contexts.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the overall functionality is entirely different despite similar low-level I/O patterns.
- 共享行为: Both read from a URL using BufferedReader and InputStreamReader.；Both catch exceptions and print stack traces.
- 行为差异: Different validation logic vs. HTML parsing.；Different output: sends network packets or shuts down vs. populates a menu map.；Different control flow: conditional based on username vs. loop over lines.；Different libraries: Minecraft session vs. Swing components.
- 修正建议: Incorporate data flow analysis to distinguish purposes.；Use models that capture long-range semantics and domain-specific intents.

### case_id=6132 FP lexical_or_api_overlap

- 方法: `downloadURLtoString` vs `getUser`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads content from a URL and returns it as a string.
- B 摘要: Loads a user from a DAO or parses a config file to create and save a user.
- 静态失败原因: Static BERT models likely relied on lexical and API overlap (BufferedReader, InputStreamReader, while loop) and ignored the differing semantics and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the functions have entirely different purposes and logic despite sharing some I/O boilerplate.
- 共享行为: Both use BufferedReader and InputStreamReader to read from a stream.；Both employ a while loop to read lines sequentially.
- 行为差异: Function A reads from a URL and returns the entire content; Function B reads from a local config file to find a specific user.；Function A has no conditionals or parsing; Function B contains tokenization, condition checks, and database operations.；Function A returns a raw string; Function B returns a User object after potentially saving it.
- 修正建议: Incorporate dataflow analysis to capture variable dependencies and output types.；Use graph neural networks that encode control flow and data dependencies.；Augment training data with more examples that contrast similar boilerplate but different semantics.

### case_id=6133 FN partial_functionality

- 方法: `fetchURLData` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches a URL (http/https/file) and returns its content as a byte array.
- B 摘要: Builds a website for editing by processing XML, replacing gadgets, and writing files.
- 静态失败原因: Static BERT methods rely on surface-level token similarity and structural patterns; the shared boilerplate (try-finally, InputStream, URL handling) may have been overshadowed by the vastly different token sets and method lengths.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled as clone due to the shared pattern of opening a file:// URL stream and reading input, even though the overall purposes differ significantly.
- 共享行为: Both handle file:// URLs when opening streams；Both use InputStream and try-finally for resource cleanup
- 行为差异: A is a simple URL fetcher returning bytes; B is a complex site builder with many parameters and steps.；A only reads; B reads, transforms, and writes multiple files.；B involves DOM manipulation, string replacement, and custom file system I/O; A uses standard Java I/O.；A is static and short; B is instance method and very long.
- 修正建议: Include dataflow analysis to distinguish simple fetch vs. complex transformation.；Enhance understanding of method-level semantics beyond local patterns.

### case_id=6134 FN partial_functionality

- 方法: `copyResource` vs `saveAttachmentBody`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file.
- B 摘要: Saves an attachment body to a file and updates metadata in the content provider.
- 静态失败原因: Low token overlap (0.13) and different method names/signatures caused the model to miss the shared copy behavior; also the additional operations in B dominate the embedding.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both focus on copying input stream to output file, and the additional database operations in B might be seen as extensions, not core functionality.
- 共享行为: Both read data from an input stream and write to an output stream.
- 行为差异: B uses IOUtils.copy instead of manual byte loop.；B contains additional database update operations.；B checks for null part body and creates directories.；Different source and context: A loads resource from URL or file, B from a part.
- 修正建议: Incorporate dataflow analysis to detect the copy pattern.；Use code summarization or method-level embeddings.；Train with more positive examples of partial functionality clones.

### case_id=6135 FN benchmark_preference_bias

- 方法: `sendExceptionToServer` vs `downloadURLtoString`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends an exception report to a server with encoded parameters and reads the response.
- B 摘要: Downloads the content of a URL and returns it as a string.
- 静态失败原因: The model correctly identified non-clone due to low token overlap and different method names/purposes; it did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both involving URL reading/writing, but this is too broad and likely an annotation error.
- 共享行为: Both perform network I/O using URL connections and read from streams.
- 行为差异: A sends a POST request with data; B only reads via GET.；A constructs complex encoded parameters; B simply reads lines.；A handles IOException internally; B declares throws IOException.；A returns void; B returns a String.
- 修正建议: Re-annotate this pair as non-clone in BCB.；Ensure BCB functional criteria are more strictly applied.

### case_id=6136 FP partial_functionality

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated string lists into sets and maps, with validation and error handling for file reading.
- B 摘要: Copies a file from source to target using FileChannel transfer.
- 静态失败原因: The static model likely overgeneralized the common occurrence of file I/O (IOException, file operations) in both methods, ignoring the vast difference in core logic due to token sparsity and long-range dependencies in A.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would label as non-clone because the functions perform entirely different tasks; B is a generic file copy while A is a domain-specific parsing and initialization routine.
- 行为差异: A involves complex parsing of string tokens and population of data structures; B is a simple file copy.；A handles domain-specific wylie encoding and multiple column formats; B has no such logic.
- 修正建议: Incorporate structural or data-flow analysis to distinguish file I/O patterns from domain-specific parsing.；Increase the similarity threshold or use ensemble of models to reduce false positives.

### case_id=6137 FN benchmark_preference_bias

- 方法: `populateResources` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.1`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Loads template resources from classpath and saves default images and properties.
- B 摘要: Sends a predefined HTTP POST request to RenRen API with hardcoded parameters and prints the response.
- 静态失败原因: The model correctly predicted non-clone due to low token overlap and completely different functional domains; the BCB label is likely a benchmark annotation error or overly broad interpretation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both functions as performing I/O operations with reading from URLs and processing lines, but this is a stretch given the significant difference in purpose and context.
- 行为差异: Different domains (resource initialization vs. API call)；Different I/O sources (local classpath vs. remote HTTP server)；One saves data persistently; the other prints to console；Different parameter setups and data structures
- 修正建议: Re-evaluate BCB annotation for this pair; consider removing from clone set.；Models should rely on low token Jaccard and structural dissimilarity.

### case_id=6138 FN partial_functionality

- 方法: `copyResource` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file by reading bytes and writing them using low-level I/O.
- B 摘要: Reads a DICOM file, parses its metadata, reads pixel data, and writes it to a new file with DICOM encoding.
- 静态失败原因: The low token overlap (0.1) and domain-specific API calls in B likely led the static model to underestimate similarity; it failed to recognize the high-level read-write pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered both as 'resource copy' operations at a high level, but this interpretation is overly broad given the distinct domains and complexity.
- 共享行为: Both read from a source (URL/file or inFile) and write to a destination file；Both use input/output streams；Both close streams after use
- 行为差异: A handles both URL and file sources; B only file；A uses generic byte-by-byte copy; B uses specialized DICOM parsing and pixel data handling；B includes progress messages; A does not；A uses simple streams; B uses ImageInputStream, ImageOutputStream, and DICOM-specific classes
- 修正建议: Use dataflow or semantic-aware models that capture high-level intent；Augment training with more Type-4 examples；Incorporate function-level summaries or documentation

### case_id=6139 FN partial_functionality

- 方法: `readReferenceText` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a plugin resource file identified by ident, returning its content as a string with line separators, and throws NoContentException on failure.
- B 摘要: Connects to a hardcoded URL, reads all lines, concatenates them without separators, logs the result, and throws Exception on failure.
- 静态失败原因: Static BERT models likely focused on differences in method names, exception handling, return types, and hardcoded strings, resulting in low token Jaccard (0.23) and missing the abstract common behavior of URL reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels as clones pairs that share the core algorithmic pattern of reading text from a URL line by line, even if the exact source, error handling, or output differ. This pair is considered a Type-4 partial functionality clone.
- 共享行为: Both open a URL connection and read from its input stream；Both use BufferedReader to read lines in a loop；Both accumulate lines into a StringBuffer
- 行为差异: Source: A reads from a bundle resource derived from ident; B reads from a hardcoded external URL；Return type: A returns String; B returns void and logs instead；Error handling: A catches specific exceptions and throws NoContentException; B throws generic Exception；Line separator: A appends newline after each line; B does not
- 修正建议: Incorporate data-flow analysis to detect the common pattern of URL connection and line-by-line reading；Abstract away specific exception types and method names during comparison；Use structure-based features (e.g., AST subtrees) to capture the loop and I/O operations

### case_id=6140 FN partial_functionality

- 方法: `copyResource` vs `gerarTutorialPage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a resource from a URL or file to a destination output stream.
- B 摘要: Generates a tutorial website by creating directories and copying CSS files using FileChannel, then writing HTML pages.
- 静态失败原因: The extremely low token Jaccard similarity and lack of lexical overlap caused the model to miss the shared file-copying behavior, as it relies on surface form rather than deeper semantic understanding.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both functions perform file copying operations, a common functionality that qualifies as partial similarity under Type-4 clone criteria.
- 共享行为: Both involve copying files from a source to a destination.
- 行为差异: A copies a single file; B creates directories and copies multiple CSS files.；A uses simple byte-by-byte stream copy; B uses FileChannel transfer.；B includes additional steps like writing HTML files and showing dialog messages.
- 修正建议: Incorporate dataflow analysis to detect file read/write operations as common behavior.；Train with more diverse Type-4 examples that have low lexical but high semantic similarity.；Use abstract syntax tree (AST) or control flow graph (CFG) features to capture structural patterns of I/O operations.

### case_id=6141 FP lexical_or_api_overlap

- 方法: `run` vs `getUser`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a resource file from classpath and sets its content as text in a Swing component.
- B 摘要: Loads a user from database; if not found, reads a config file to find and save the user, then returns the user.
- 静态失败原因: Static BERT models likely focused on lexical overlap of getResource, openStream, BufferedReader, and readLine, ignoring the different surrounding logic and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: The functions share only a common API usage pattern but have divergent functionality and structure, which BCB treats as non-clones.
- 共享行为: Both read a resource from classpath using getResource and BufferedReader
- 行为差异: Different overall purpose (UI update vs user retrieval)；Different error handling (silent catch vs print stack trace)；Different post-processing (Swing invokeLater vs saving to database)
- 修正建议: Incorporate structural information like control flow and data flow；Use context-aware embeddings that capture high-level intent

### case_id=6142 FN partial_functionality

- 方法: `login` vs `GetResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs in to LOLA by sending POST request with email and password, reads session ID from response.
- B 摘要: Performs HTTP GET request on given URL and returns concatenated response content.
- 静态失败原因: Static BERT likely focused on low token overlap and different method names, missing the structural similarity of HTTP I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled them as clones considering both are HTTP client operations with similar connection setup, despite different purposes.
- 共享行为: Both open HTTP connections；Both use BufferedReader to read response；Both handle IOExceptions
- 行为差异: HTTP method: POST vs GET；A sends form data, B does not；A extracts single session ID, B concatenates all lines；A has specific login logic and session management
- 修正建议: Enhance model with structural patterns of HTTP clients；Incorporate knowledge of common I/O idioms；Use dataflow analysis to capture sequence of network operations

### case_id=6143 FP library_context_missing

- 方法: `actionPerformed` vs `setup`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `context_recovery_then_dynamic`；动态可解性: `low`；执行优先级: `medium`
- A 摘要: Handles user actions to select file paths for external tools (Graphviz, ImageMagick) and save preferences, with GUI updates.
- B 摘要: Extracts native libraries from a jar file based on OS architecture to set up library path for a webcam application.
- 静态失败原因: Static model likely overgeneralized common Java patterns (file chooser, conditionals) and missed the distinct semantic contexts and data flows.
- 静态 case study: 该类错误缺少关键上下文或需要深层语义，纯静态方法不可靠。
- 动态 case study: 动态执行价值较低：样本可能依赖库、框架、网络、GUI、数据库或项目上下文，需要先恢复环境或 mock 依赖。
- BCB 偏好解释: BCB labeled non-clone because the functions have entirely different purposes and behavior, despite both performing file I/O.
- 共享行为: Both involve file system operations and conditional checks.
- 行为差异: Function A is an event-driven GUI configuration method with multiple branches; Function B is a static setup extracting native resources.；Different domains: A for GUI preferences, B for native library loading.
- 修正建议: Incorporate contextual embeddings that capture method-level purpose, such as using graph-based representations or focal attention on differences in data flow.

### case_id=6144 FN partial_functionality

- 方法: `fileCopy` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source path to destination path with validation and byte stream copying.
- B 摘要: Retrieves a resource as an InputStream, caching it locally with HTTP conditional GET and byte stream copying.
- 静态失败原因: Low token Jaccard (0.1567) and surface-level differences in method names, API calls, and structure masked the deeper shared I/O copying pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often annotates pairs with similar I/O copying patterns as clones, even if the surrounding context differs, likely considering them Type-4 (similar functionality).
- 共享行为: Both copy bytes from an input stream to an output stream using a buffer；Both handle stream closing in finally or catch blocks；Both involve reading from a file or URL and writing to a file
- 行为差异: A includes extensive file path validation and abort messages；B involves network URL handling, caching logic, HTTP conditional requests, and multiple early returns；B has a cache table and prints debug messages
- 修正建议: Incorporate data-flow analysis to detect shared byte copying loops；Train on examples of I/O utility functions to recognize common patterns；Use graph-based representations that highlight data dependencies

### case_id=6145 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a version-check URL, parses lines for build numbers, and calls another version check method if both builds are found.
- B 摘要: Sends an HTTP POST request with parameters, reads the response line by line, and returns the response string.
- 静态失败原因: Static models like BERT or GraphCodeBERT likely overemphasized lexical and structural similarities (both use URL, BufferedReader, while loops, try-catch) while ignoring differences in method purpose, control flow, and data dependencies.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would consider these non-clones because the overall functionality differs significantly: one is a version check utility, the other is a generic HTTP POST handler. The shared use of URL and BufferedReader is a common API pattern insufficient for clone annotation.
- 共享行为: Both open a URL connection and read input streams line by line using BufferedReader.；Both use try-catch for exception handling (IOException or Exception).
- 行为差异: Function A performs a GET request (via URL.openStream) and parses specific prefixes, while B performs a POST request with headers and writes parameters.；Function A calls another overloaded method and does not return a value; B returns the response string.；Function A has a finally block that hides wait cursor; B has a finally block that disconnects the HTTP connection.
- 修正建议: Incorporate data flow analysis to distinguish read vs. write operations.；Add awareness of method signatures and return types.；Use task-specific pre-training or contrastive learning to differentiate patterns with same API but different semantics.

### case_id=6146 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `callApiPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Scrapes hyperlinks and anchor text from an HTML page using regex.
- B 摘要: Makes an HTTP POST API call with parameters and returns the response InputStream.
- 静态失败原因: Static BERT models may have been misled by lexical and API-level overlap (common usage of URL, URLConnection, InputStream, and exception handling), ignoring the core semantic differences and method signatures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the high-level functionality (extracting links vs. API call) and return types (vectors vs. InputStream) are fundamentally different despite some shared IO boilerplate.
- 共享行为: Open a URL connection；Read from an InputStream；Use standard Java IO classes (URL, URLConnection, BufferedReader/PrintStream)
- 行为差异: A returns parsed vectors of links/texts; B returns InputStream；A uses GET implicitly; B uses POST explicitly；A performs regex parsing; B sends POST data and checks status；A's method is static; B's is instance method
- 修正建议: Include method signature differences (return type, parameters) as features；Focus on behavioral alignment of core logic beyond boilerplate；Use dataflow analysis to track how inputs are transformed into outputs

### case_id=6147 FN boilerplate_overlap

- 方法: `addRecord` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Adds a data record by streaming input to a file, computing a digest for deduplication.
- B 摘要: Builds a website for editing by transforming XML pages with XSLT and writing output files.
- 静态失败原因: Low token Jaccard (0.083) and very different vocabulary, method names, and data flow structures made the static model confidently predict non-clone.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones due to superficial similarities like file writing, stream usage, and exception handling, but the core functionality is entirely different.
- 共享行为: Both involve file I/O operations；Both handle exceptions；Both use streams for data processing
- 行为差异: Function A is about data storage with deduplication; Function B is about HTML site generation；A returns a DataRecord; B is void；A uses DigestOutputStream; B uses Transformer and XSLT；A processes a single input stream; B processes multiple pages and control files
- 修正建议: Use AST-based or graph-based models that capture structural semantics；Incorporate data flow analysis to differentiate storage vs. transformation tasks

### case_id=6148 FN partial_functionality

- 方法: `init` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.35`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Initializes a report file by handling backup, restart, and writing XML metadata.
- B 摘要: Launches an Eclipse configuration by setting up Maven project files and reverse engineering.
- 静态失败原因: Low token overlap (0.1) and differing method names likely caused the model to miss the partial XML-related functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as initialization methods that process XML files and handle errors, despite different domains.
- 共享行为: Both involve file I/O and XML processing.；Both use exception handling and logging.
- 行为差异: A focuses on writing/backup of a report file; B focuses on reading/processing POM files and project setup.；A includes restart recovery logic; B does not.；A writes XML stream; B reads and handles XML content via content handlers.
- 修正建议: Enhance model sensitivity to abstract functional roles like XML file initialization.；Incorporate domain-agnostic structural patterns in embeddings.

### case_id=6149 FN partial_functionality

- 方法: `sendExceptionToServer` vs `CheckUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a remote server via HTTP POST and checks for success response.
- B 摘要: Performs an HTTP GET on a given URL and returns the first line of the response.
- 静态失败原因: Low token similarity and different method signatures cause the model to focus on syntactic differences, missing the semantic overlap of URL connection and response reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers this a Type-4 clone because both functions involve making an HTTP request and reading a line from the response, despite differences in request method and additional logic.
- 共享行为: Both open an HTTP connection to a URL and read the first line of the response.
- 行为差异: Function A constructs a complex query string and sends via POST, while B uses GET.；Function A has extensive error handling and prints messages, while B returns empty string on error.；Function A includes additional logic for optional parameters and checks response for 'success'.
- 修正建议: Train with dataflow-aware models to recognize common API usage patterns like URL openConnection and BufferedReader readLine.；Incorporate task-level semantics such as 'makes HTTP request and reads response'.

### case_id=6150 FN lexical_or_api_overlap

- 方法: `processAddByURLSubmit` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Processes a URL by copying its stream to a StringWriter and then processing the DOAP content, handling FileNotFoundException and IOException.
- B 摘要: Launches an Eclipse launch configuration for a NexOpen project, reading Maven pom files, setting up Hibernate dialect, creating reverse engineering files, and scheduling an install project action.
- 静态失败原因: Static BERT models may over-rely on token-level similarities (e.g., 'IOUtils.copy', 'IOException', 'logger') and miss the overall semantic difference due to limited context and lack of deep dataflow understanding.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as a clone due to superficial API similarities like IOUtils.copy and exception handling, and possibly viewing both as 'processing input data' tasks, though they are fundamentally different.
- 共享行为: Use of IOUtils.copy to copy streams；Exception handling for IOException；Logging with logger/Logger
- 行为差异: Different input types: URL vs ILaunchConfiguration；Different domains: DOAP processing vs Eclipse project setup；Different control flow and conditions；Different overall purpose and output
- 修正建议: Enhance training with more diverse non-clone pairs that share API calls but differ in functionality；Incorporate dataflow or structural analysis to distinguish between different usage patterns of shared APIs

### case_id=6151 FP lexical_or_api_overlap

- 方法: `main` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that sets up a Weka Experiment GUI, loads/saves an experiment object, and displays it.
- B 摘要: ActionPerformed method that handles various UI commands (e.g., GRAPHVIZ, IMAGEMAGICK) in a genealogy application, saving preferences and updating UI.
- 静态失败原因: The static BERT model likely over-relied on lexical overlap, such as Swing API calls (JFrame, JFileChooser) and file I/O patterns, ignoring the high-level semantic differences in method purpose and context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators would not consider these clones because the overall intent and functionality are unrelated, despite some shared API usage.
- 共享行为: Both use Swing components like JFrame and JFileChooser.；Both perform file I/O operations.；Both have try-catch blocks for exception handling.；Both save configuration settings.
- 行为差异: Code_a is a program entry point (main method) with a specific workflow; Code_b is an event handler with multiple independent command responses.；Code_a focuses on experiment setup; Code_b focuses on application configuration.；The scope and context are entirely different.
- 修正建议: Incorporate deeper semantic understanding via AST or data flow.；Use contrastive learning to distinguish UI-related boilerplate code.；Train with better representation of method-level context (e.g., class name, field usage).

### case_id=6152 FP other

- 方法: `doCrypt` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Computes SHA-1 hash of input string and returns hex string.
- B 摘要: Processes HTTP request, validates session, builds XML data, performs URL connection to classify a concept, and returns appropriate ActionForward.
- 静态失败原因: Static BERT models may rely on embeddings that capture general patterns like method signatures or common API usage (e.g., both import MessageDigest vs HttpServlet), or they might be misled by boilerplate patterns (try-catch, throws clauses). However, token Jaccard is low, so likely the model overfits to superficial similarity like both being public static methods with exceptions or using BufferedReader/InputStreamReader? The failure is likely due to the model being sensitive to API-level overlap but missing the overall semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotation expects clones to share significant functional similarity; these two do not. Even Type-3/4 clones require some core similarity. Despite both having 'do' and 'perform' method names, no core functionality aligns.
- 共享行为: Both use some string encoding/decoding (UTF-8 in A, URL encoding in B)；Both involve I/O operations but at different levels (digest vs HTTP connection)
- 行为差异: Function A is a simple cryptographic hash with no external dependencies；Function B is a complex web action with session management, XML processing, and HTTP communication；Function A returns a hex string; Function B returns an ActionForward object；Function A uses SHA-1; Function B uses no cryptography
- 修正建议: Improve training to focus on behavioral similarity rather than method signatures；Use dataflow analysis to capture control and data dependencies；Increase weight for token-level differences when Jaccard is low

### case_id=6153 FN long_range_semantics

- 方法: `CopyTo` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file character by character using FileReader and FileWriter.
- B 摘要: Builds a website for editing by processing XML and writing transformed content to files.
- 静态失败原因: Low token overlap and vastly different functional complexity; long-range semantics of B (truncated) make it hard for Transformer models to capture similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as clone due to both involving file I/O with character streams and similar resource handling patterns, but the functional similarity is extremely low.
- 共享行为: Both read and write files using character streams.；Both handle IOException.；Both close resources in finally blocks.
- 行为差异: A is a simple file copy; B is a complex multi-step transformation.；A copies all characters; B processes XML and writes transformed content.；A reads from a single file; B reads from multiple sources (XML, control file, etc).；A writes to a single file; B writes to multiple output files.
- 修正建议: Improve handling of long-range dependencies in code.；Incorporate functional similarity beyond token overlap.；Use more robust embeddings that capture data flow.

### case_id=6154 FP boilerplate_overlap

- 方法: `importRoles` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: importRoles reads from a URL, parses XML fragments into RoleName objects, and returns a list of them.
- B 摘要: getFrameworkFactory reads a resource file, finds a non-comment line, instantiates a FrameworkFactory via reflection, and returns it or throws an exception.
- 静态失败原因: Static BERT models may have overestimated similarity due to overlapping API calls (URL, BufferedReader, readLine), similar variable names, and the shared pattern of reading a resource line-by-line, without capturing the distinct semantic goals.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels them as non-clones because the core functionality (parsing vs. reflection-based instantiation) is entirely different, and the structural overlap is limited to common I/O boilerplate, which BCB typically discounts.
- 共享行为: Both open a stream from a URL-like resource and read lines using BufferedReader.
- 行为差异: A parses XML-like lines to create RoleName objects; B looks for a line to instantiate a factory class.；A returns a list; B returns a single object.；A silently catches exceptions; B throws an exception if factory not found.；A appends lines to a buffer and resets on a closing tag; B trims lines and skips comments.
- 修正建议: Incorporate task-specific semantic information, such as output types and high-level intent.；Use contrastive learning to distinguish common boilerplate from core functionality.；Leverage dataflow analysis to understand data dependencies beyond surface tokens.

### case_id=6155 FN partial_functionality

- 方法: `getResourceAsStream` vs `buildDeb`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource from a URL with caching and returns an InputStream.
- B 摘要: Builds a Debian package file by writing archive header, control, and data files.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on lexical and syntactic cues, which differ greatly (method names, API calls), and fail to capture the abstract 'stream copy' pattern due to low token Jaccard and different overall structure.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this pair as a clone because both functions involve a common 'copy input stream to output stream' pattern, which is a Type-4 (functionally similar) clone despite different high-level purposes. The low token overlap is typical for such broad similarity.
- 共享行为: Both perform file I/O operations involving reading from an InputStream and writing to an OutputStream.；Both use buffered streams for efficiency.；Both have loops that read bytes from input and write to output.
- 行为差异: Function A retrieves a resource via URL with HTTP handling and caching, while Function B writes a specific Debian archive format.；Function A includes cache checking and HTTP response handling, whereas Function B has no such logic.；Function A uses a synchronized block and exception handling with cleanup, while Function B throws IOException and has no synchronization.；Function A has a different control flow with conditional caching decisions, while Function B follows a linear sequence of file entries.
- 修正建议: Incorporate data-flow analysis to identify stream passing and transformation patterns.；Train a model to recognize common I/O patterns independent of specific domain names.；Use contrastive learning with examples of Type-4 clones that have low lexical overlap.

### case_id=6156 FN benchmark_preference_bias

- 方法: `httpRequestByPOST` vs `handledRun`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with parameters, reads the response if successful (status < 400), returns the response string, or sets error fields and returns null on failure.
- B 摘要: Downloads a specific XML file from a URL, checks version, writes new data to a file if outdated, then loads game database; catches exceptions with logging or dialog.
- 静态失败原因: Static models like GraphCodeBERT may overemphasize token overlap (try-catch, BufferedReader) and structural patterns while missing the deep semantic difference: one is a generic HTTP utility returning data, the other is a file-update routine with version logic and persistent side effects.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone based on broad Type-3/4 similarity because both functions involve reading from a URL, buffering input, and handling IO errors. However, the intents and side effects are quite different; this seems more like a false positive annotation.
- 共享行为: Both perform network I/O to read data from a server.；Both use BufferedReader and InputStreamReader to read streamed data.；Both handle IOExceptions with error handling (error codes vs logging/dialogs).
- 行为差异: Function A is a generic HTTP POST client; Function B is a specific game data updater.；Function A returns a string or null; Function B writes to a file and triggers game database loading, with no return value.；Function A sets instance error fields; Function B logs, shows dialogs, and rethrows exceptions.；Function A checks HTTP status codes (<400); Function B compares version numbers from file headers.
- 修正建议: Improve model to distinguish between pure data retrieval (return-based) and persistent side-effect operations (file writes, DB loads).；Incorporate API-level semantics (HttpPost vs URL.openStream) and data flow (return vs output to file).；Use execution traces or dynamic analysis to capture actual behavior.

### case_id=6157 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `setPayload`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles user actions to set GUI preferences and file paths for Graphviz and ImageMagick tools.
- B 摘要: Appends data from a source file to a destination file and increments an index.
- 静态失败原因: The model may have overemphasized trivial lexical similarities (e.g., both contain 'File', 'IOException', 'if', 'return') or shared method name prefixes ('set'), while missing the overall context and intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have no semantic overlap in purpose or behavior; one is a GUI event handler, the other is a file copy utility.
- 共享行为: No significant shared behavior; both involve file-related operations but with entirely different intents.
- 行为差异: Function A is a GUI event handler for setting preferences; Function B is a file I/O operation.；Function A uses JFileChooser and updates UI components; Function B uses FileInputStream/FileOutputStream with FileChannel.；Function A has a large, complex structure with many conditional branches; Function B is short and linear.；Function A handles user interaction; Function B does not.
- 修正建议: Enhance model to capture high-level task semantics beyond local tokens.；Use code structure or data-flow analysis to distinguish GUI from I/O operations.；Include more negative examples of unrelated functions sharing common API keywords.

### case_id=6158 FN benchmark_preference_bias

- 方法: `execute` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Processes class files for code injection by reading, analyzing, modifying, and writing back bytecode.
- B 摘要: Configures and launches an Eclipse project by handling POM files, Hibernate dialect, and triggering an install action.
- 静态失败原因: The static model correctly identified them as non-clones given low token similarity and distinct domains; the BCB label likely represents an annotation error or overly permissive criteria.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider both as 'resource transformation' tasks due to common patterns like file reading, processing, and writing, but the lack of functional overlap suggests this labeling is erroneous or overly broad.
- 行为差异: Function A performs bytecode instrumentation on class files; Function B handles Maven project configuration in Eclipse.；Function A uses ClassReader/ClassWriter for bytecode manipulation; Function B uses ContentHandlerTemplate and Eclipse APIs for XML processing.；Function A is concerned with file sizes and injection statistics; Function B sets Eclipse resource properties and runs project jobs.
- 修正建议: Improve benchmark consistency by requiring clearer functional equivalence for clone labeling.；Use domain-specific features or API usage patterns to differentiate unrelated tasks.

### case_id=6159 FP partial_functionality

- 方法: `getContent` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches complete HTTP response body using Apache HttpClient with timeout settings.
- B 摘要: Fetches only the first line of an HTTP response using HttpURLConnection.
- 静态失败原因: Static BERT models may over-rely on lexical overlap (e.g., 'Http', 'BufferedReader', 'reader.readLine', 'return') and miss the structural difference of a loop in A vs. a single readLine in B, leading to false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels as non-clone when there are clear functional differences, such as returning full content vs. only the first line, even if the overall task is similar.
- 共享行为: Both perform an HTTP GET request and read the response body.
- 行为差异: A returns entire response body; B returns only first line.；A uses Apache HttpClient; B uses java.net.HttpURLConnection.；A sets connection and socket timeouts; B does not.；A reads until end-of-stream; B reads only one line.
- 修正建议: Improve model's ability to distinguish control flow differences (e.g., loops vs. no loops).；Incorporate structural or dataflow analysis to detect that A accumulates all lines while B returns only one.

### case_id=6160 FP lexical_or_api_overlap

- 方法: `sendPost` vs `getPagina`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with given parameters and returns the response body.
- B 摘要: Sends an HTTP GET request to a URL and returns the response body, with custom authentication.
- 静态失败原因: Static BERT/GraphCodeBERT models may focus on lexical and API-level overlap (e.g., both use URL, BufferedReader, readLine, etc.) and overlook the crucial distinction in HTTP method and data writing, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the difference in HTTP method (POST vs GET) and the presence of data transmission in sendPost represent significant behavioral divergence, beyond typical type-3/4 variations accepted by BCB.
- 共享行为: Both perform HTTP requests to retrieve a response；Both read the response line by line using BufferedReader；Both return the response as a concatenated string
- 行为差异: HTTP method: POST vs GET；sendPost sends parameter data in the request body; getPagina does not；sendPost sets request headers and connection properties; getPagina sets an authenticator；Error handling: sendPost prints error via MsgPrint; getPagina stores error message in result string
- 修正建议: Incorporate detection of HTTP method usage (e.g., setDoOutput) to distinguish POST from GET；Consider dataflow analysis to track whether output is written to the connection；Use structural features like explicit parameter writing or header settings as discriminators

### case_id=6161 FP lexical_or_api_overlap

- 方法: `executePost` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request and returns the response string.
- B 摘要: Loads an OSGi FrameworkFactory from a classpath resource file.
- 静态失败原因: The model may have overfocused on common API usage (URL, BufferedReader) and resource management structure, ignoring the distinct semantic intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the functions have completely different purposes and logic, despite sharing some basic I/O patterns.
- 共享行为: Both use URL and BufferedReader for I/O operations；Both close resources after use；Both handle exceptions
- 行为差异: executePost sends HTTP POST; getFrameworkFactory reads a config file；executePost returns response string; getFrameworkFactory returns a FrameworkFactory instance；executePost catches and prints exceptions; getFrameworkFactory throws exception；Different input parameters and error handling strategies
- 修正建议: Incorporate higher-level semantic features like method name and operation type；Use data flow analysis to capture the actual transformations

### case_id=6162 FP long_range_semantics

- 方法: `encrypt` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Computes SHA-1 hash of input string.
- B 摘要: Handles Struts action for concept classification, involving HTTP communication, XML parsing, and session management.
- 静态失败原因: Long sequence and complex control flow in B likely overwhelmed the model, while common boilerplate (e.g., 'throws Exception', getBytes) may have caused false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB emphasizes functional similarity; these two functions have no overlap in purpose or logic.
- 共享行为: Both throw exceptions；Both perform some data processing
- 行为差异: Encryption vs. web request handling；Simple single-step vs. multi-step workflow；No I/O vs. HTTP and XML I/O
- 修正建议: Improve model capacity for long-range dependencies；Use structural features like AST or data flow；Add more negative sampling with large functional differences

### case_id=6163 FP lexical_or_api_overlap

- 方法: `readIntoList` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads an HTML source from a URL, parses anchor tags to extract command names, and populates a map with JMenuItem objects having action listeners.
- B 摘要: Reads a tab-separated file from a URL, parses each line to extract an ID and description, and adds them to a vector.
- 静态失败原因: Static BERT likely over-relied on lexical and API overlap (e.g., URL, openStream, while loop, try-catch) and failed to capture the fundamental semantic difference in parsing logic and output construction.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have different functional behavior, even if they share some structural patterns. These functions serve entirely different purposes (building a menu vs. parsing TSV data), so they are not considered clones.
- 共享行为: Both read input from a URL using openStream()；Both iterate line-by-line through the input；Both handle exceptions with try-catch
- 行为差异: Different parsing: HTML anchor tags vs. tab-separated fields；Different output: Map<String, JMenuItem> vs. Vector<String>；Only function A creates UI components and attaches action listeners；Different URL handling: A takes a URL object, B takes a String source
- 修正建议: Incorporate dataflow or control-flow analysis to distinguish parsing patterns；Train on more diverse examples with similar APIs but different semantics；Use graph-based representations that capture variable dependencies and output types

### case_id=6164 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.5`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint in the XML, and saves to a temporary file, returning the file path.
- B 摘要: Copies a local file from source to destination using a FileChannel, returns success status.
- 静态失败原因: Static BERT models likely focused on lexical and syntactic similarity, which is low (Jaccard 0.134), and did not capture the shared FileChannel pattern as a semantic indicator of clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones because both implement file copying using NIO FileChannel.transferFrom, which is a distinctive pattern, and they considered the core functionality of writing data to a file as similar despite different overall purposes and additional operations.
- 共享行为: Both use FileChannel.transferFrom to copy data from an input channel to an output file.
- 行为差异: getFile involves network I/O and XML manipulation; copyFile only local file copy；getFile has complex error handling for multiple exceptions; copyFile catches Throwable；getFile returns a String; copyFile returns a boolean；getFile includes file deletion and renaming; copyFile does not
- 修正建议: Enhance model to recognize common sub-tasks like file copy by learning API usage patterns and considering partial functionality similarities.

### case_id=6165 FN partial_functionality

- 方法: `testNetworkHTTP` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens multiple HTTP connections to different URLs, reads and discards responses, logs progress, and handles IOException.
- B 摘要: Opens a single HTTP connection, reads and parses response lines into fields, sets error flags, and notifies listeners.
- 静态失败原因: Low token Jaccard (0.189) and different method names/overall logic (multiple vs single connection) caused the model to miss the underlying structural similarity. Static models often fail on such template-based clones with low lexical overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely annotated this as Type-3/4 clone because both functions exhibit the same boilerplate pattern of HTTP fetching: open connection, read lines, handle exception, and use finally. Despite different specific URLs and output handling, the core structural similarity in network IO suffices for BCB's broad clone annotation.
- 共享行为: Open an HTTP connection using URL and read lines；Use try-catch-finally with IOException handling；Disconnect or close stream in finally (A: disconnect; B: close reader)
- 行为差异: A connects to multiple URLs, B only one；A discards response, B parses into fields；A logs test steps, B sets error flags and notifies listeners
- 修正建议: Use AST-based or graph-based similarity to capture structural patterns like try-catch-finally and readLine loops；Incorporate dataflow analysis to recognize URL.openConnection usage；Augment training with more diverse partial functionality clones

### case_id=6166 FP boilerplate_overlap

- 方法: `main` vs `copyFromFileToFileUsingNIO`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: The main method parses command-line arguments, reads a Prolog file, generates adapter classes, and assembles them into a JAR file.
- B 摘要: The copyFromFileToFileUsingNIO method copies the contents of an input file to an output file using NIO FileChannel.
- 静态失败原因: Static models like GraphCodeBERT may over-rely on API names (e.g., File, IOException, try-catch) and structural patterns (e.g., try-finally, channel usage) that appear in both functions, leading to false positive clone detection despite low lexical overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have fundamentally different purposes and logic, even if they share trivial file I/O patterns. The two functions are clearly distinct in their core functionality, so BCB correctly identifies them as non-clones.
- 共享行为: Both involve file I/O operations: reading from a file (A reads Prolog, B reads via FileInputStream) and writing output (A writes JAR, B writes via FileOutputStream).；Both handle IOException in try-catch or throws clause.
- 行为差异: Function A is a complex command-line tool that parses Prolog, generates Java classes, and creates a JAR; Function B simply copies file bytes.；Function A uses many libraries (ASM, Prolog parser, etc.) while B uses only standard NIO channels.；Function A has detailed argument handling and debug output; Function B has no such logic.；Function A produces a complex output (adapter layer and JAR), whereas B produces an exact copy of the input file.
- 修正建议: Incorporate data flow analysis to capture distinct transformations and outputs.；Use contrastive learning with negative examples that share I/O boilerplate but differ semantically.；Enhance model with AST-based features that highlight computational differences.

### case_id=6167 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `addDataFromURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter feed from a hardcoded URL using HttpClient and returns the response body as a string.
- B 摘要: Reads text from a given URL by opening a stream and appends lines to a field variable.
- 静态失败原因: Static BERT/GraphCodeBERT may have overemphasized the common boilerplate pattern of BufferedReader and readLine loop, while ignoring differences in HTTP client usage, error handling, and output type.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered the functions non-clones because they use different HTTP libraries, have different error handling, and differ in output mechanism (return vs side effect), which are significant behavioral differences.
- 共享行为: Both fetch data from a URL；Both read the response line by line using BufferedReader
- 行为差异: A uses HttpClient with status check; B uses URL.openStream() without status check；A returns the result; B modifies a field；A catches specific exceptions (ClientProtocolException, IOException); B catches Exception broadly；A appends without newline; B appends with newline
- 修正建议: Incorporate control flow and data flow analysis to distinguish between different HTTP clients；Consider the method signature and return type as important context；Use more comprehensive tokenization that captures library-specific API calls

### case_id=6168 FP lexical_or_api_overlap

- 方法: `getVersion` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a version string from a hardcoded URL and returns it, ignoring errors.
- B 摘要: Checks for software updates by parsing version information from a configurable URL and updating the UI accordingly.
- 静态失败原因: Static BERT overemphasizes lexical and API overlap (URL, BufferedReader, etc.) while missing differences in control flow, return type, and UI interactions.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have distinct purposes and behaviors despite shared URL-reading pattern.
- 共享行为: Both fetch data from a URL；Both read lines using BufferedReader
- 行为差异: Different URL source: hardcoded vs property-based；Different parsing logic: last line vs specific prefixes；Different return type: String vs void；Different error handling: return null vs show error dialog
- 修正建议: Incorporate method signature (return type, parameters) into representation；Use data flow analysis to differentiate variable usage and side effects；Encode broader context, such as class or caller information

### case_id=6169 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `setBundleInfoName`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads Twitter JSON feed and returns the entire content as a string.
- B 摘要: Reads bundle info from a URL, parses key-value pairs, and updates a list of BundleInfo objects.
- 静态失败原因: The model overemphasized lexical and API-level overlap (BufferedReader, readLine, IOException, try-catch) and the similar loop structure, ignoring the differing high-level semantics, output types, and method names.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels based on functional similarity; these functions have completely different goals (retrieving Twitter timeline vs updating bundle info) despite sharing low-level IO operations, so they are non-clones.
- 共享行为: Both open a URL and read lines via BufferedReader；Both handle IOException with printStackTrace；Both use while loop to read lines until null
- 行为差异: A uses HttpClient/HttpGet; B uses URL.openStream；A returns the full content; B updates a list and returns boolean；A has no parsing; B parses lines with '=' and updates bundle names；A's purpose is data retrieval; B's purpose is data transformation from configuration
- 修正建议: Incorporate method names and return types into input features；Use data flow analysis to distinguish between data retrieval and data transformation；Add AST-based structural matching that captures purpose beyond API calls

### case_id=6170 FN benchmark_preference_bias

- 方法: `getFile` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the soap address endpoint, and returns the file path.
- B 摘要: Copies a file from input to output, optionally printing byte counts if diagnostic mode is enabled.
- 静态失败原因: The static BERT/GraphCodeBERT model likely focused on syntactic features and token overlap, which are low (Jaccard 0.1118), and failed to recognize the abstract functional similarity that BCB considered. The model lacks understanding of high-level data flow patterns that generalize across I/O tasks.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider them clones because both perform high-level file I/O operations (reading from a source and writing to a destination), which could be viewed as Type-4 functionally similar clones despite different domains and implementations.
- 共享行为: Both open input streams and output streams for file I/O.
- 行为差异: Different purposes: A downloads and modifies WSDL, B copies files.；Different sources: A reads from URL, B reads from local file.；Different processing: A does XML manipulation, B does simple copying with optional diagnostics.；Different outputs: A returns a string, B writes to a file and returns void.
- 修正建议: Incorporate more Type-4 clone examples in training to teach the model abstract functional similarity.；Use data flow or graph-based representations to capture I/O patterns beyond syntactic tokens.

### case_id=6171 FN benchmark_preference_bias

- 方法: `doGet` vs `makeBackup`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to retrieve and display a page, with caching and access control.
- B 摘要: Copies all files from a source directory to a destination backup directory, setting timestamps.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap and structural similarity. The token Jaccard is very low (0.095), and the control flow, API calls, and I/O patterns are very different. The model likely correctly identified them as non-clones, but BCB's broad criteria may consider them clones. The model's failure (from BCB's perspective) is due to BCB's lenient clone definition.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider these clones due to the presence of file writing operations in both. In BCB's Type-4 annotation, methods that perform similar I/O operations or have overlapping functionality can be considered clones, even if the overall context differs.
- 共享行为: Both involve file I/O operations (writing to files in A, copying files in B).
- 行为差异: A is a servlet method handling HTTP requests; B is a utility for directory backup.；A uses FileWriter to cache page output; B uses FileInputStream/FileOutputStream to copy files.；A has complex control flow with error handling and access control; B is a straightforward file copy loop.；A writes a single string to a file; B copies all files in a directory.
- 修正建议: Retrain with benchmark-specific labels if targeting BCB evaluation.；Incorporate domain information or functional APIs to capture I/O similarity.；Use a threshold that aligns with BCB's broader notion of clones.

### case_id=6172 FP lexical_or_api_overlap

- 方法: `handler` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handler reads a web page line by line, extracts a substring between markers for each entry in a map, and updates the map.
- B 摘要: Downloads an RDF/XML model from a URL, with HTTP header customization, and returns a Model object.
- 静态失败原因: The static BERT/GraphCodeBERT model might have been misled by the common structural pattern of opening a URL, reading input, catching exceptions, and similar variable names like 'url' and 'in'. However, the model likely failed to capture the entirely different logic after obtaining the input stream (line parsing vs model reading) and the different return types and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have fundamentally different purposes (URL content parsing vs model download), different signatures, and low lexical similarity. The shared pattern of opening a URL connection is too generic to indicate functional similarity.
- 共享行为: Both open a URL connection and read from it；Both catch MalformedURLException and IOException
- 行为差异: Function A modifies a provided map; Function B creates and returns a Model；Function A reads lines and extracts substrings; Function B reads the entire stream as an RDF model；Function A has empty catch blocks; Function B logs and rethrows；Function A takes additional TargetPage parameter for URL and parsing instructions; Function B only takes a URL string
- 修正建议: Improve training to distinguish between simple URL reading and different downstream data processing；Incorporate dataflow analysis to track how the input stream is used；Add negative sampling with similar lexical patterns but different semantics；Use type-aware analysis to differentiate void vs return type and map modification vs model creation

### case_id=6173 FN partial_functionality

- 方法: `copyResource` vs `MotixFileItem`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or local file) to a destination file by reading bytes and writing them with a manual loop.
- B 摘要: Constructs a MotixFileItem by reading an InputStream into a byte array, optionally processing it as an image, and storing the byte array as a new stream.
- 静态失败原因: Static BERT models rely on token overlap and structural similarity; these functions have low token Jaccard (0.109) and different structures (method vs constructor), so the model failed to capture the abstract I/O copying commonality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to partial functionality similarity: both involve copying bytes from an input to an output, which is a common I/O pattern accepted as Type-4 clone.
- 共享行为: Both read bytes from an input source and write them to an output stream (file output stream or ByteArrayOutputStream).
- 行为差异: copyResource writes to a file and uses a manual read-write loop; MotixFileItem writes to a ByteArrayOutputStream using IOUtils.copy, performs optional image processing, and sets multiple fields.；copyResource handles URL vs file existence; MotixFileItem always takes an InputStream and does not handle file/URL sources.；copyResource is a private method; MotixFileItem is a constructor.
- 修正建议: Incorporate dataflow analysis to trace input/output streams and byte copy operations.；Enrich training with annotations of high-level I/O patterns to capture partial functionality clones.

### case_id=6174 FN benchmark_preference_bias

- 方法: `sendExceptionToServer` vs `scrapeForIsbns`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST.
- B 摘要: Scrapes ISBN-10 codes from a web page using regex.
- 静态失败原因: Static BERT models rely on token-level similarity and structural patterns; low token Jaccard (0.0949) and completely different control flow caused it to miss the high-level network I/O pattern that BCB considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone due to overlapping API usage (URL, streams) and exception handling patterns, despite different semantics, reflecting a broad Type-3/Type-4 interpretation.
- 共享行为: Both use URL connection, InputStream, BufferedReader, and handle IOExceptions.
- 行为差异: One writes to server (POST), one reads from server (GET).；One encodes and sends structured data; one parses HTML for patterns.；Different output: one prints response, one returns count and populates a map.
- 修正建议: Incorporate high-level functional similarity detection beyond surface syntax.；Use contrastive learning on broader clone types to recognize shared I/O patterns.

### case_id=6175 FN partial_functionality

- 方法: `streamContains` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Checks if an InputStream contains a given string by copying it to a ByteArrayOutputStream and converting to UTF-8 string.
- B 摘要: Complex Eclipse launch configuration method that, among many other tasks, reads a file resource as an InputStream, copies it to ByteArrayOutputStream, converts to string, and replaces a placeholder.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on token-level and structural features; the low token Jaccard (0.0628) and the huge difference in function length and complexity likely led the model to focus on the overall dissimilarity. The model may not have captured the shared sub-pattern of InputStream-to-string conversion because it is buried in a much larger function. Additionally, the model may have been biased by the different method names and context.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a Type-4 semantic clone because both functions include the common utility pattern of reading an InputStream into a ByteArrayOutputStream and converting to a string, which is the primary functionality of A and a sub-task in B. BCB often accepts partial functional similarity, especially when the shared behavior is idiomatic.
- 共享行为: Both use IOUtils.copy to read an InputStream into a ByteArrayOutputStream and then convert to a string.
- 行为差异: B performs extensive Eclipse project operations, launch configuration, POM file handling, and profile management, while A is a simple test utility that only does the string containment check.
- 修正建议: Improve the model's ability to detect partial functional clones by incorporating sub-tree matching or data flow analysis that can identify common utility patterns even in different contexts.；Augment training data with more examples of Type-4 clones where the similarity is limited to a sub-function.

### case_id=6176 FP boilerplate_overlap

- 方法: `getUser` vs `loadExistingAntlibs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from a DAO or parses a config file to create and save a User object.
- B 摘要: Loads ant library definitions from resources by reading a file and resolving URIs.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on overlapping API calls (e.g., BufferedReader, InputStreamReader, URL) and ignored the semantic differences in data flow and purpose, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels true clones when functions share common high-level behavior, even with different implementations. Here, the goals are completely different (user login vs. ant library loading), so BCB would not consider them clones.
- 共享行为: Both read lines from a resource file using BufferedReader and InputStreamReader
- 行为差异: Function A creates a User object and saves it; Function B loads ant libraries and has no return；Function A uses StringTokenizer with colon delimiter; Function B uses line trimming and URI resolution；Function A has an outer try-catch printing stack trace; Function B rethrows exceptions as RuntimeException；Function A reads a single file 'users.cfg' from classLoader; Function B iterates over multiple resources from a classLoader
- 修正建议: Enhance training with data that distinguishes between boilerplate patterns and actual functional similarity；Incorporate data flow or control flow analysis to highlight differences in output usage

### case_id=6177 FN partial_functionality

- 方法: `dump` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to target using byte streams and returns success status.
- B 摘要: Handles a launch configuration for an Eclipse project by processing POM files, setting properties, and installing the project.
- 静态失败原因: The token Jaccard is very low (0.060) and the functions have vastly different lengths and structures. Function A is short and uses simple Java IO; function B is long, contains many Eclipse API calls, generics, and nested callbacks. The model likely relied on lexical and structural similarity, which is minimal here.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'file I/O' clones (Type-4) because they share the basic pattern of opening files, reading/writing, and closing. The partial functionality of reading from input and writing to output is common, even though the overall tasks differ drastically.
- 共享行为: Both perform file I/O operations (reading and writing files).；Both use try-catch blocks to handle IOException.
- 行为差异: Function A is a simple file copy; function B is a complex multi-step launch configuration setup.；Function A returns a boolean; function B returns void and throws CoreException.；Function A works with any files; function B specifically uses Eclipse project resources and configuration attributes.；Function B involves XML parsing, property setting, project management, and template processing; A has none of these.
- 修正建议: Incorporate semantic understanding of API usage patterns at a higher abstraction level.；Enrich features with data-flow analysis to capture shared I/O operations.；Consider partial clone detection with explicit sub-function matching.

### case_id=6178 FN long_range_semantics

- 方法: `httpRequestByPOST` vs `sendRequestObjectResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends HTTP POST request with URL-encoded form parameters and returns response body as string.
- B 摘要: Builds URL, opens HTTP connection, sends GZIP-compressed XML request, saves response to a file based on content type, and returns the filename.
- 静态失败原因: Low token overlap and different structural patterns; BERT may focus on surface similarity and miss the high-level semantic commonality in network communication.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as performing HTTP client operations, focusing on the network communication aspect, and overlook differences in response handling and UI.
- 共享行为: Both perform HTTP POST requests；Both read server responses
- 行为差异: A returns response string, B saves response to file and returns filename；A uses Apache HttpClient, B uses Java URLConnection；B includes UI components and file picker dialog；B handles errors differently (shows dialog vs. setting fields)
- 修正建议: Use AST-based or flow-based models to capture semantic intent beyond token overlap；Ignore UI and file-saving details, focusing on core I/O operations

### case_id=6179 FN benchmark_preference_bias

- 方法: `copyExternalResource` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel, handling creation and cleanup.
- B 摘要: Builds an HTML site for editing by reading XML templates, transforming them, and writing output files.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed to detect similarity because the token Jaccard is very low (0.05), and the structural and API usage patterns differ greatly; it correctly identified them as non-clones.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might label this as a clone due to a very broad interpretation of 'file handling' or a potential annotation error, as both functions involve reading and writing files, though at different scales and purposes.
- 共享行为: Both perform file I/O operations (reading from and writing to files).；Both handle IOException.
- 行为差异: A is a simple file copy without transformation; B is a complex multi-step site generation with XML transformation and string manipulation.；A uses FileChannel for efficient transfer; B uses FileInputStream and FileWriter.；A has 1 source and 1 destination; B processes multiple pages and files in a loop.；B has extensive debugging output and error handling for DOM and FTP exceptions, unlike A.
- 修正建议: Improve annotation consistency by requiring more specific functional similarity criteria.；Use task-specific features or context to differentiate simple file copying from complex site generation.；Consider using semantic parsing to extract high-level intent.

### case_id=6180 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `readVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks and their text from a given URL using regex.
- B 摘要: Reads version, revision, and compile date from a classpath resource file.
- 静态失败原因: The model likely focused on the common boilerplate pattern of reading lines with BufferedReader/InputStreamReader, ignoring the domain-specific operations inside the loop and the different output semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically annotates clones based on functional similarity. These functions serve entirely different purposes (web scraping vs resource parsing), so even with similar reading structure, they are unlikely to be considered clones.
- 共享行为: Both use BufferedReader and InputStreamReader to read lines from an input stream.；Both iterate line by line until null.
- 行为差异: A fetches from a URL, B reads from a classpath resource.；A parses HTML anchor tags, B parses key-value lines starting with 'Version=', 'Revision=', 'Date='.；A returns two Vector arrays, B sets instance variables.；A uses regex extensively, B uses string splitting.
- 修正建议: Train the model to differentiate between similar loops by focusing on the specific operations performed inside (regex vs split).；Incorporate data flow or output type information to distinguish functions that write to different destinations.；Use contrastive learning with pairs that share control flow but differ in semantics.

### case_id=6181 FP lexical_or_api_overlap

- 方法: `main` vs `write`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that generates adapter classes from a Prolog file and writes them to a JAR file.
- B 摘要: Write method that encrypts ByteBuffers using SSL, handling handshake and initial buffering.
- 静态失败原因: The model may have been misled by superficial lexical overlaps like 'ByteBuffer', 'write', 'buffer', 'IOException', or common control flow structures (while loop, try-catch), ignoring the overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely views these as non-clones because they perform entirely different tasks with no overlapping functionality beyond basic I/O patterns.
- 共享行为: Both involve writing data to some output (JAR file vs. encrypted buffers)；Both use try-catch for exception handling
- 行为差异: Function A parses Prolog and generates adapter code; Function B performs SSL encryption；Function A writes to a file system; Function B returns encrypted ByteBuffers；Function A is a static void main; Function B returns ByteBuffer[]；Function A has complex file I/O and class generation; Function B handles SSL engine state
- 修正建议: Improve training with more diverse non-clone pairs that share common APIs but differ in semantics；Incorporate structural or dataflow analysis to capture high-level intent

### case_id=6182 FN partial_functionality

- 方法: `testNetworkHTTP` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Test method that makes multiple HTTP GET requests to various URLs, reading but discarding the responses.
- B 摘要: Main method that makes a single HTTP GET request and prints the response line by line.
- 静态失败原因: Low token overlap (0.215) and differences in control flow (multiple loops vs one) and output handling led the model to focus on surface-level dissimilarities rather than the common network communication pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers Type-3/Type-4 clones, and both functions share the core behavior of performing HTTP GET requests and reading responses, even though the number of requests and output handling differ.
- 共享行为: Both open a URL and create a BufferedReader from the input stream.；Both read lines in a while loop.；Both close the connection/reader at the end.
- 行为差异: Function A makes 7 HTTP requests, while B makes 1.；Function A discards the response, while B prints it.；Function A uses HttpURLConnection explicitly, B uses URL.openStream().；Function A has try-catch-finally, B throws IOException.
- 修正建议: Train models on semantic similarity over data flow and API call sequences.；Incorporate detection of repeated patterns (e.g., multiple HTTP requests) as a common behavior.；Use function-level embeddings that capture I/O and resource usage patterns.

### case_id=6183 FN partial_functionality

- 方法: `execute` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Saves a HomeMap record and copies an uploaded image file to a new file named after the record's ID.
- B 摘要: Launches an Eclipse launch configuration for a NexOpen project, including project validation, pom.xml processing, Hibernate dialect setup, reverse engineering file generation, and scheduling an install action.
- 静态失败原因: Static BERT correctly predicted non-clone because the lexical overlap is very low (token Jaccard 0.05) and the overall semantics are clearly different. The model likely recognized the domains (simple web action vs. Eclipse plugin launch) and assigned non-clone. If BCB label is considered correct, the model missed the partial functional overlap due to long-range structural differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone due to the presence of a shared file-writing functional fragment and common exception handling patterns, despite major contextual differences. BCB's broad Type-4 criteria sometimes accept such partial functionality similarity.
- 共享行为: Both use IOUtils.copy to perform file I/O；Both handle exceptions (FileNotFoundException, IOException)；Both involve writing data to files
- 行为差异: A is a simple two-step operation; B is a complex multi-step configuration with project validation, XML processing, and scheduling；A operates on a single image file and a HomeMap object; B operates on multiple project files and configuration attributes；A uses basic file streams; B uses Eclipse/plugin APIs, Properties, and ByteArrayOutputStream；A has no branching; B has extensive branching and loops
- 修正建议: Incorporate dataflow analysis to detect shared I/O operations beyond lexical similarity；Use hierarchical attention or graph-based models to capture partial functional fragments；Train with more diverse partial clone examples to learn such subtle similarities

### case_id=6184 FP lexical_or_api_overlap

- 方法: `readData` vs `execute`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses comma-separated token strings into sets and reads a configuration file to populate lookup structures.
- B 摘要: Saves a HomeMap object to a database and copies a file to a directory, then returns a list view.
- 静态失败原因: Likely due to common API tokens like StringTokenizer, FileInputStream, IOException causing lexical overlap; or the model overgeneralized from boilerplate error handling patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because there is no meaningful functional similarity; even broad Type-4 clones require some common intent or behavior, lacking here.
- 共享行为: Both perform I/O operations (file reading vs. file copying).
- 行为差异: Different purpose: token parsing/configuration vs. database persistence and file management.；Different data structures and outputs: sets and maps vs. database entity and file.；Different control flow: iterative token processing vs. sequential save and copy.
- 修正建议: Improve the model to better capture semantic intent beyond surface API calls.；Add negative mining with low token overlap but same API usage.

### case_id=6185 FP lexical_or_api_overlap

- 方法: `executePost` vs `PhoneSetImpl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Executes an HTTP POST request with given URL and parameters, returns response string.
- B 摘要: Constructor that reads from a URL, parses lines (skipping those starting with '***'), and populates a map.
- 静态失败原因: Overemphasized common API tokens (URL, BufferedReader, readLine) and structural similarity (try-finally blocks), ignoring overall semantics and dataflow differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have distinct purposes and different I/O behavior, even if they share some API calls.
- 共享行为: Both use URL and BufferedReader to read data from a network resource
- 行为差异: One performs HTTP POST, the other reads from a URL constructor；One writes request parameters, the other parses lines and builds a map；One returns response string, the other initializes an object
- 修正建议: Incorporate control-flow and data-dependency analysis to distinguish setup-heavy functions from reading-only functions；Use method name embeddings or context to capture intent

### case_id=6186 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Event handler that processes various user actions (e.g., selecting file paths for GRAPHVIZ, IMAGEMAGICK, etc.) and updates UI preferences.
- B 摘要: Utility method that copies a file from source to destination using file channels.
- 静态失败原因: The static model likely overfit to shared low-level API tokens (File, FileInputStream, IOException, etc.) and ignored the vast behavioral and structural differences, treating file-handling boilerplate as a clone signal.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the functions are semantically unrelated: one orchestrates multiple UI settings, the other copies a file. They do not share any meaningful functional equivalence, not even partial.
- 共享行为: Both methods handle file-related operations (reading/writing file paths or copying files).；Both use File objects and throw IOException.
- 行为差异: actionPerformed is a complex event dispatcher handling many UI actions; copy is a focused file copy utility.；actionPerformed interacts with a Swing GUI and persists preferences; copy performs purely file I/O with no UI.；actionPerformed involves dialog selection and conditional logic; copy is a straightforward sequential copy.
- 修正建议: Enhance training with contrastive examples that share API usage but differ in high-level purpose.；Incorporate control flow and data flow structure to distinguish orchestration logic from utility operations.

### case_id=6187 FP boilerplate_overlap

- 方法: `sendPost` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Checks for software updates by fetching a version file and parsing build numbers, then invoking another version check method.
- 静态失败原因: The static model likely overemphasized the common structural patterns (try-catch, URL, BufferedReader, while loop) and missed the semantic differences in API usage (POST vs GET), error handling, and overall goal, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled non-clone because the functions have completely different purposes and logic, despite sharing boilerplate IO patterns. The similarity is superficial, not functional.
- 共享行为: Both open a URL and read its content line by line using a BufferedReader.；Both handle exceptions with error reporting.
- 行为差异: Function A uses HTTP POST, while function B uses HTTP GET (openStream).；Function A sends a parameter string, function B reads a specific file format with start markers.；Function A returns the response text, function B calls another method with parsed values.；Function A catches generic Exception, function B catches IOException.
- 修正建议: Incorporate method name and signature into the representation to capture intent.；Use data-flow analysis to distinguish between sending data (POST) and reading static content (GET).；Train with more diverse examples that emphasize functional differences.

### case_id=6188 FN boilerplate_overlap

- 方法: `createOutputStream` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Creates a modified zip file by copying all entries except 'content.xml', then adds a new 'content.xml' entry and returns a BufferedWriter for it.
- B 摘要: Builds a site for editing by iterating over pages, transforming XML, and writing output files with string manipulation and file I/O.
- 静态失败原因: The static model likely relied on token overlap and method name similarity, which are very low (Jaccard=0.05, different names), causing it to miss the structural I/O similarity that BCB considered.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as clone due to broad Type-4 semantic similarity based on common I/O patterns like buffered stream handling and character array loops, ignoring the distinct domain logic.
- 共享行为: Both use character buffers and loops to read and write data between streams.；Both involve file I/O with buffered readers/writers.；Both perform some form of data transformation (zip entry copy vs. XML transformation).
- 行为差异: Function A is a focused utility for zip file manipulation; Function B is a complex site builder with many steps.；Function A deals with zip entries and compression; Function B deals with XML, properties, and page rendering.；Function A returns a BufferedWriter; Function B is void and writes files directly.；Function A has a clear filter on a specific zip entry; Function B has conditional logic based on page options and error handling.
- 修正建议: Improve detection of structural I/O patterns beyond exact token matches.；Incorporate control-flow and data-flow analysis to distinguish between different transformation logic.；Use graph-based representation to capture nested stream wiring and buffer loops.

### case_id=6189 FN partial_functionality

- 方法: `copyResource` vs `copyTo`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a single resource (URL or local file) to a destination file using byte-by-byte stream copying.
- B 摘要: Recursively copies a file or directory to a destination, using FileChannel for file copying and handling directories.
- 静态失败原因: Static models like BERT rely on token overlap and syntactic structure. Low Jaccard similarity (0.14), different control flow (while loop vs. recursion), and distinct API usage (stream vs. channel) lead to low embedding similarity, causing a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a Type-4 clone because both functions implement a 'copy' operation from a source to a destination, ignoring differences in input handling, recursion, and error management.
- 共享行为: Both functions copy data from a source to a destination.；Both involve file I/O operations.；Both create output files.
- 行为差异: Function A copies only single files; Function B handles both files and directories recursively.；Function A uses InputStream/OutputStream byte-by-byte; Function B uses FileChannel.transferTo for efficient copying.；Function A throws exception on missing source; Function B logs errors and continues for files.；Function A uses instance fields for source/destination; Function B takes explicit File parameters.
- 修正建议: Incorporate dataflow analysis to capture shared I/O intent.；Normalize method signatures to focus on core functionality.；Use contrastive learning with functional-level labels to improve recognition of partial clones.

### case_id=6190 FN partial_functionality

- 方法: `runInternal` vs `import_hints`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads an OPDS catalog or book from a URL with support for redirects and pagination.
- B 摘要: Imports jigsaw puzzle hints from a file or URL by parsing coordinates and rotations.
- 静态失败原因: The model relied on lexical overlap and syntactic similarity, which are low (Jaccard=0.10), missing the high-level semantic similarity of both being URL-driven data parsers.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: Both functions involve reading structured data from a URL and parsing it, matching a broad Type-4 pattern of 'data ingestion from external source' that BCB sometimes accepts as clones.
- 共享行为: Both open a URL connection to read data from a remote source.；Both parse the input data line by line or token by token.；Both handle potential IO exceptions with a try-catch block.
- 行为差异: Function A handles HTTP-specific details (User-Agent, Referer, response codes), while B does not.；Function A can handle paginated OPDS catalogs, while B reads a fixed number of hint entries.；Function A triggers callbacks and progress updates, while B simply returns a boolean.
- 修正建议: Enhance training data with more diverse examples of Type-4 semantic clones.；Incorporate code summarization or abstract syntax tree (AST) comparisons to capture high-level structure.；Use contrastive learning to emphasize functional behavior over surface tokens.

### case_id=6191 FN boilerplate_overlap

- 方法: `sendExceptionToServer` vs `wordFrequency`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST and reads the response.
- B 摘要: Fetches a URL to query word frequency and parses the response.
- 静态失败原因: Static BERT models rely heavily on token overlap and surface-level patterns; the low Jaccard similarity and different domain-specific terms cause the model to miss the abstract structural similarity in network I/O operations.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as network communication functions that perform URL-based data retrieval and response processing, thus labeling them as Type-4 clones despite different domain-specific logic.
- 共享行为: Both create a URL and open a connection；Both read from an input stream line by line；Both handle IOExceptions
- 行为差异: A writes data to the server (POST), B only reads (GET)；A sends exception-specific data, B queries a word frequency endpoint；A includes complex data encoding and optional parameters, B uses a simple word replacement pattern
- 修正建议: Use a code model that captures control flow and API call sequences；Include graph-based representations to highlight similar subgraphs like URL handling and I/O loops

### case_id=6192 FN partial_functionality

- 方法: `sendExceptionToServer` vs `sendRequestObjectResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an exception report to a server by building a POST request with encoded parameters and prints the response.
- B 摘要: Sends an XML request to a server via HTTP POST with GZIP compression, saves the response to a file, and opens it in a browser.
- 静态失败原因: Low token Jaccard (0.169) indicates little lexical overlap. GraphCodeBERT may not capture the abstract pattern of HTTP client operations due to differing APIs and additional logic, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones (Type-4) because both perform HTTP communication with request/response, a common pattern. The annotation guidelines often accept broad functional similarity.
- 共享行为: Both open an HTTP connection and send data via POST；Both write to the output stream of the connection；Both read the input stream response；Both handle IO exceptions
- 行为差异: A builds key-value parameters manually; B uses GZIP compression and writes XML；A prints the response or success message; B saves the response to a file and shows it in a browser；A has error-reporting purpose; B is a generic request-response method returning a filename；B includes server URL discovery logic via preferences/dialog; A uses a fixed errorServerURL
- 修正建议: Use program slicing to isolate HTTP communication subroutines；Incorporate control flow and data flow for network operations；Train on more diverse Type-4 clone examples with low token overlap

### case_id=6193 FN partial_functionality

- 方法: `getResourceAsStream` vs `unzipEntry`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a resource from a URL, caches it locally, and returns an InputStream to the cached file.
- B 摘要: Extracts a single entry from a zip file and writes it to a file in the output directory.
- 静态失败原因: Low token overlap (0.11) and disparate vocabulary (URL vs zip) prevent the model from recognizing the shared I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may focus on the core streaming copy operation as common functionality, ignoring surrounding details like caching or URL handling.
- 共享行为: Both involve reading from an input source and writing to a file using buffered streams
- 行为差异: Method A includes HTTP handling, caching logic, and prints debug messages; Method B does not；Method A returns an InputStream; Method B is void；Method A writes byte-by-byte; Method B uses IOUtils.copy
- 修正建议: Enhance models with data-flow analysis to detect stream copy patterns；Use abstract representations of I/O operations

### case_id=6194 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `callApiPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads integers from a resource file line by line and returns them as a set.
- B 摘要: Makes an HTTP POST request to a URL, sends parameters, and returns the response input stream.
- 静态失败原因: Static model likely over-relied on lexical overlap (e.g., URL, openStream, catch Exception) and common API sequences, ignoring the completely different I/O semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones for such functionally different methods despite some overlapping API usage patterns.
- 共享行为: Both use URL and open a connection/stream；Both handle exceptions with try-catch；Both involve I/O operations
- 行为差异: A reads from a local resource file; B sends data to a remote server via HTTP POST；A returns a set of integers; B returns an InputStream；A catches Exception and prints stack trace; B catches IOException and throws custom exception；A uses LineNumberReader; B uses HttpURLConnection with headers, timeout, and request method
- 修正建议: Use dataflow analysis to distinguish reading from writing；Incorporate structural information like method return type and exception handling style；Train on more diverse pairs to reduce sensitivity to shared APIs

### case_id=6195 FN benchmark_preference_bias

- 方法: `storeImage` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Stores an uploaded image to a date-based directory, optionally creating resized versions, and returns a relative path.
- B 摘要: Downloads a WSDL file from a URL, saves it to a temp directory, optionally modifies XML endpoint, and returns the absolute file path.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on low lexical overlap (0.109 Jaccard) and distinct API calls (e.g., writeResizedImage vs XMLUtils), correctly identifying them as semantically different, thus predicting non-clone against a possibly overly broad BCB annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both involving file I/O, stream copying, and returning a file path, considering them as instances of 'storing/retrieving files' despite different specific functionalities.
- 共享行为: Both write data from an input source to a file on the filesystem.；Both create directories/files if needed.；Both return a string representing the file path.
- 行为差异: Source of data: InputStream vs URL download.；Post-processing: image resizing vs XML endpoint modification.；Error handling: throws generic Exception vs specific AxisFault exceptions.；Return value: relative path vs absolute path.
- 修正建议: Re-evaluate BCB annotation: these functions are not clones even under Type-4 similarity.；If BCB label is considered correct, expand the model's notion of similarity to include partial functional patterns like file I/O operations.；Alternatively, improve the model's ability to distinguish between genuinely similar file operations and those with distinct data sources and post-processing.

### case_id=6196 FP lexical_or_api_overlap

- 方法: `getURLContent` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads URL content and returns it as a string with newlines.
- B 摘要: Reads URL content with optional authentication, writes each line to a temporary file, and updates a status label.
- 静态失败原因: Static models like BERT may rely on lexical and API overlap (URLConnection, BufferedReader, InputStreamReader) and ignore structural differences, return types, and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because the methods have different signatures (String return vs void), different side effects (file writing, UI updates), and different core functionality (one retrieves as string, the other writes to file).
- 共享行为: Open a URL connection；Read lines using BufferedReader and InputStreamReader
- 行为差异: Method A returns the content as a string; Method B writes to a file and has side effects；Method B includes authentication (username/password) and sets Authorization header；Method B updates a UI status label and prints to console；Method A appends newline after each line; Method B writes lines to a file and also appends newline
- 修正建议: Incorporate dataflow and side-effect analysis；Use models that capture long-range dependencies and method signatures；Include return type information and method purpose context

### case_id=6197 FP lexical_or_api_overlap

- 方法: `get` vs `getURLContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches GameRecord objects from a URL by sending an HTTP GET request with geographical headers and parsing the response.
- B 摘要: Fetches the entire text content of a URL as a String, handling encoding.
- 静态失败原因: The model likely over-relied on lexical overlap (URL, BufferedReader, readLine) and boilerplate HTTP connection code, ignoring the critical differences in data processing logic and method signatures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels such pairs as non-clones because the return types and data transformations are fundamentally different, despite sharing the generic pattern of URL reading.
- 共享行为: Both open an HTTP URL connection and read the response line by line using BufferedReader.
- 行为差异: Function A sets custom headers and checks response code; B does not.；Function A filters out lines starting with '#' and decodes them into GameRecord objects; B returns raw text.；Function A returns an array; B returns a String.；Function A has exception handling that returns null; B throws IOException.
- 修正建议: Train model to distinguish data flow and return type semantics.；Incorporate structural information about method signatures.

### case_id=6198 FP boilerplate_overlap

- 方法: `readZoneIDs` vs `createDialogArea`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads zone IDs from a resource file and returns them as a HashSet of integers.
- B 摘要: Creates a dialog area, reads license text from a resource file, and displays it in a browser or text widget.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on lexical and structural similarities (e.g., common tokens like 'try', 'catch', 'url', 'openStream', 'readLine', 'while') and missed the divergent high-level semantics and method purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality is entirely different (data extraction vs UI construction), and the similarity is limited to a common boilerplate I/O pattern, which BCB typically does not consider sufficient for a clone.
- 共享行为: Both read lines from a resource file using URL and openStream.；Both catch exceptions and print stack traces.
- 行为差异: A returns a HashSet of integers; B sets UI text and returns a Composite.；A uses LineNumberReader; B uses BufferedReader.；A has no UI; B creates and configures SWT widgets.；A does not close streams; B closes streams in a finally block.
- 修正建议: Incorporate method name and return type as features.；Use control-flow and data-flow analysis to distinguish different operations on read data.；Train with more diverse examples of boilerplate code to reduce false positives.

### case_id=6199 FN benchmark_preference_bias

- 方法: `getResourceAsStream` vs `createButtonCopyToClipboard`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.1`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Retrieves a resource as an InputStream from a URL with caching to local file system.
- B 摘要: Creates a SWT button that copies the environment report to clipboard when clicked.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone because there is no lexical or structural similarity; the model was not tricked by any shared patterns.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have incorrectly labeled this pair as a clone due to a mistake in annotation; possibly they considered both as methods that 'acquire resources' (A acquires streams, B acquires clipboard content) but this is a stretch.
- 行为差异: Function A handles network I/O and file caching, while Function B creates a GUI button with a selection listener.；Function A is a public synchronized method returning an InputStream, Function B is a private void method.；Function A includes error handling with multiple catch blocks, Function B has no explicit error handling.；Function A uses classes like URLConnection, HttpURLConnection, File, etc., while Function B uses SWT Button, SelectionAdapter, IOUtils.
- 修正建议: Correct the BCB label to non-clone for this pair.；Improve BCB annotation guidelines to avoid such unrelated pairs.

### case_id=6200 FN benchmark_preference_bias

- 方法: `copyFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Retrieves a resource by URL, caches it locally, and returns an InputStream, with HTTP conditional requests and file caching.
- 静态失败原因: The static model correctly predicted non-clone (0) based on low token/structural similarity, agreeing with strict semantics.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label likely due to a lenient annotation where any file I/O operation is considered similar, or a data error in the benchmark.
- 共享行为: Both perform file I/O operations.；Both handle exceptions with printStackTrace.；Both involve reading from a source and writing to a destination.
- 行为差异: A copies entire files; B retrieves and caches remote resources.；A uses NIO FileChannel; B uses BufferedInputStream/OutputStream.；B includes HTTP request handling and caching logic; A does not.；B returns an InputStream; A returns void and writes to a file.
- 修正建议: Re-evaluate BCB annotation for this pair; they are not clones.；Consider removing or correcting the label in the dataset.

### case_id=6201 FN benchmark_preference_bias

- 方法: `getResourceAsStream` vs `tail`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Retrieves a resource via URL, caches it locally, and returns an InputStream.
- B 摘要: Implements the Unix 'tail' command, reading the last 1024 bytes of a file with optional follow mode.
- 静态失败原因: Static BERT models rely on token overlap and syntactic patterns; low Jaccard (0.125) and different vocabulary lead to prediction of non-clone, missing any broader semantic similarity BCB might have intended
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as Type-4 clones due to high-level similarity in stream I/O patterns, but this seems overly broad and likely a mislabel
- 共享行为: Both involve reading from an input stream and writing to an output stream；Both handle exceptions and may loop over I/O operations
- 行为差异: Completely different functionality: resource caching vs file tailing；Different return types (InputStream vs void)；Different inputs: URL name vs command-line arguments；Different control flow: A caches and returns, B repeatedly reads and prints
- 修正建议: Improve model understanding of overall functionality via semantic role labeling；Use dataflow or control-flow analysis to distinguish different tasks；Incorporate larger context or method-level summarization

### case_id=6202 FN benchmark_preference_bias

- 方法: `doGet` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Proxies an HTTP GET request to a Fedora URL, copying response status, headers, and body.
- B 摘要: Handles HTTP GET request to retrieve and render a page object, with access control, caching, and error handling.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token and structural similarity; the low Jaccard similarity (0.072) and differing control flow led them to correctly identify the pair as non-clones. They missed the high-level 'both are servlet GET handlers' abstraction, but that abstraction is too generic for clone detection.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones based on very broad criteria: both are servlet doGet methods that handle HTTP GET and produce a response. This overlooks significant differences in functionality.
- 共享行为: Both are Java servlet methods handling HTTP GET requests.；Both set response status and write to output stream.
- 行为差异: A proxies an external URL; B retrieves a Page object from a database.；A copies headers from proxied response; B constructs its own headers and content.；A has minimal error handling; B has extensive error handling and access control.；A does not handle page visibility or caching; B does.
- 修正建议: Re-evaluate the BCB label: consider whether such broad functional similarity should be considered a clone.；If retaining the label, develop a model that recognizes high-level servlet patterns, but balance against false positives.；Alternatively, correct the dataset by removing this pair if it does not meet standard clone definitions.

### case_id=6203 FN benchmark_preference_bias

- 方法: `main` vs `extractUninstallFiles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a ZIP file from a fixed URL and extracts all entries to the current directory.
- B 摘要: Manages extraction of uninstall files from a JAR during an installer upgrade, including backup, deletion, and conditional file copying.
- 静态失败原因: The static model likely correctly identified the low token overlap and structural differences, predicting non-clone. It did not fail; rather, the BCB annotation may be overbroad.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label these as clones because both involve reading archive entries and writing them to disk, a common cross-cutting concern. However, the contexts and additional logic differ significantly.
- 共享行为: Both iterate over entries in an archive (zip/jar) and write data to files.
- 行为差异: Function A downloads from a fixed URL; Function B is part of an installer managing version upgrades and backups.；Function A uses ZipInputStream directly; Function B uses JarInputStream and also writes to an output JAR.；Function B contains extensive error handling, backup logic, and conditionals missing in Function A.
- 修正建议: Consider whether the BCB label is accurate; if maintaining BCB style, the model could benefit from capturing shallow semantic patterns of archive extraction.；Alternatively, refine BCB annotations to avoid overly broad Type-4 clones.

### case_id=6204 FN benchmark_preference_bias

- 方法: `doVersionCheck` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Checks for a new version of jEdit by reading a version file from a URL and comparing build numbers.
- B 摘要: Reads and parses geo-parser results from a URL, extracting place names and gazetteer IDs.
- 静态失败原因: The static BERT model likely focused on token-level dissimilarity (low Jaccard) and domain-specific vocabulary, missing the high-level structural commonality of URL reading and processing.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB considers both as 'network I/O with result parsing', a broad functional category, thus accepting them as Type-3/Type-4 clones despite different domains.
- 共享行为: Both open a URL and read content line by line；Both use BufferedReader and InputStreamReader；Both handle exceptions with try-catch
- 行为差异: A compares version strings for update decision, B constructs XML requests and parses XML responses；A uses UI (view) to show messages, B returns a collection；B includes retry logic, A does not
- 修正建议: Incorporate task-level abstractions like 'URL reading' and 'data parsing' into representations；Use graph-based models that capture control flow and external API calls；Train with broader clone definitions that include partial functional similarity

### case_id=6205 FP lexical_or_api_overlap

- 方法: `checkHashBack` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes MD5 hash from request parameters and compares with a provided hash for verification.
- B 摘要: Handles a Struts action to classify concepts by sending an HTTP request to an external service and processing the XML response.
- 静态失败原因: Static models may rely on lexical overlap and common API usage (e.g., HttpServletRequest, getParameter, StringBuffer, etc.) and ignore semantic intent. The presence of similar structural patterns in reading parameters and building strings misleads the model.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones as they perform entirely different tasks: one is a simple hash check, the other is a complex action handler.
- 共享行为: Both use HttpServletRequest to extract parameters；Both involve string manipulation and I/O
- 行为差异: Function A performs cryptographic hash verification；Function B orchestrates a multi-step business workflow including HTTP communication and session management；Function A returns boolean; Function B returns ActionForward
- 修正建议: Improve training to focus on functional purpose rather than surface API usage；Incorporate data flow analysis to distinguish between different use cases of common objects

### case_id=6206 FP boilerplate_overlap

- 方法: `readScalarpvviewerDocument` vs `getWebByUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads an XML configuration file from a URL and parses it to update UI components of a scalar PV viewer.
- B 摘要: Fetches a web page from a URL, saves it to a file, and recursively processes embedded URLs for crawling.
- 静态失败原因: The model likely focused on the overlapping API calls (URL, openStream, BufferedReader, readLine) and the try-catch structure, which are common boilerplate. It may have missed the higher-level semantic differences because the data flow after reading is entirely different. The token overlap is low, but the structural similarity of the reading loop might have been weighted heavily.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the functions serve completely different purposes (configuration loading vs. web page fetching) despite sharing low-level I/O patterns. BCB's annotation requires some functional similarity or modification; here only the reading loop is similar, which is considered too trivial for Type-3.
- 共享行为: Open a URL and read its content line by line using BufferedReader；Use try-catch for exception handling
- 行为差异: A parses XML for UI configuration; B saves the raw content to a file；A uses XmlDataAdaptor to extract structured data; B simply appends lines to StringBuilder and writes to file；A updates UI components (title, fonts, panels, PVs); B prints status and recursively gets URLs；A has complex conditional logic based on line content (skip comment lines); B directly processes all lines
- 修正建议: Include functional context beyond just API sequences, e.g., the purpose of data transformation or output.；Use data flow analysis to distinguish between parsing and file writing.；Add negative examples with boilerplate similarity but different goals.

### case_id=6207 FP lexical_or_api_overlap

- 方法: `copy` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A utility method that copies a file from source to destination using a byte buffer.
- B 摘要: An event handler that processes various action commands to configure GUI settings and preferences.
- 静态失败原因: The static BERT/GraphCodeBERT model likely over-relied on overlapping boilerplate code patterns such as if-return, null checks, file-related classes (File, FileInputStream, FileOutputStream), and common method signatures, leading it to ignore the vastly different semantic intents.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB judged these as non-clones because they have completely different high-level functionality: one is a generic file copy, the other is a GUI configuration handler. The BCB annotation likely focuses on functional similarity, not low-level lexical overlap.
- 共享行为: Both methods involve file handling (creating file streams, selecting files via JFileChooser) and null checks.
- 行为差异: Function A is a simple file copy operation; Function B is a complex GUI event handler managing multiple settings.；Function A has no user interaction; Function B relies on user input via ActionEvent and displays dialogs.；Function A has no persistent storage of preferences; Function B saves preferences using Suku.kontroller.putPref.
- 修正建议: Enhance the model to better capture high-level semantic structure beyond local patterns.；Use control flow or data flow features to distinguish between simple utilities and event-driven actions.；Increase the weight of method signatures and class contexts.

### case_id=6208 FN benchmark_preference_bias

- 方法: `login` vs `readReferenceText`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Logs in to a service by sending an HTTP POST with credentials, extracting a session ID, and returning it.
- B 摘要: Reads a reference text file from a bundle resource, concatenates lines, and returns the content as a string.
- 静态失败原因: The static model correctly identified the semantic difference under a strict equivalence, but failed to align with BCB's broader annotation preference that accepts partial functional similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions sharing a superficial pattern of opening a URL/stream, reading lines, and returning a string, despite fundamentally different business logic.
- 共享行为: Both perform I/O operations using URL and BufferedReader；Both handle exceptions and return or throw on error
- 行为差异: Different functional purpose (authentication vs file reading)；Login uses HTTP POST with output and input; ReadReferenceText only reads a local resource；Error handling: login returns empty string; readReferenceText logs and throws custom exception
- 修正建议: Align model training with BCB's lenient annotation guidelines；Incorporate task-level context to distinguish similar I/O patterns with different intents

### case_id=6209 FN partial_functionality

- 方法: `doTransfer` vs `readURL`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Acts as an HTTP proxy: forwards the incoming request to a target URL and returns the response.
- B 摘要: Opens a URL, reads its content line by line, and prints it to standard output.
- 静态失败原因: The static BERT-like model likely focused on the low token overlap (Jaccard=0.18) and the distinct APIs and control flow, leading to a non-clone prediction. It failed to recognize the partial functional similarity that BCB might consider.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'reading from a URL and outputting content', which is a broad functional similarity. The shared pattern of opening an input stream, reading, and printing might be seen as a Type-4 semantic clone despite syntactic differences.
- 共享行为: Both open a URL connection and read input from it.；Both output the content (one to HTTP response, one to console).；Both use try-catch and printStackTrace for error handling.
- 行为差异: A handles HTTP request forwarding (headers, method, body), B does not.；A writes to an HTTP response output stream, B prints to System.out.；A checks HTTP response code and conditionally sends error, B does not.；A uses HttpURLConnection with explicit property setting, B uses URL.openStream().
- 修正建议: Incorporate program slicing to isolate the common URL reading sub-behavior.；Use contrastive learning with function-level semantics rather than token-level overlap.；Design a hierarchy of clone types to separate 'partial functionality' from full semantic equivalence.

### case_id=6210 FP lexical_or_api_overlap

- 方法: `getVersion` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves the latest version number from a remote URL.
- B 摘要: Constructs a Swing GUI browser that loads and displays an XML file with optional XSLT transformation.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-weighted the shared tokens (URL, BufferedReader, readLine, try-catch) and missed the broader semantic context, such as method name and overall goal.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled non-clone because the functions serve entirely different purposes (utility vs GUI construction) despite superficial API overlap. BCB emphasizes high-level functionality over token-level similarity.
- 共享行为: Both open a URL and use BufferedReader to read lines.；Both have try-catch blocks for IOException/Exception.
- 行为差异: Function A returns a String version, while B constructs a GUI browser object.；Function B involves extensive Swing GUI setup and event handling.；Function B parses XML, applies XSLT transformations, and sets HTML content.；Function A only reads a single line of text.
- 修正建议: Incorporate method signature and return type as features.；Use control-flow or data-flow analysis to differentiate simple URL reading from complex GUI initialization.；Train on more diverse examples that distinguish low-level API usage from higher-level semantics.

### case_id=6211 FN partial_functionality

- 方法: `getHTML` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a URL, reads line by line, optionally writes to file, and returns the HTML string.
- B 摘要: Fetches version check data from a URL, parses lines for build versions, and triggers version check logic.
- 静态失败原因: Low token Jaccard (0.217) and differing method names/constants caused the model to miss the high-level structural similarity of the URL reading pattern. The model likely overemphasized lexical differences and ignored the shared API sequence.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB's broad criteria often accept Type-3 clones where the core algorithmic structure (URL reading and line processing) is shared, even if post-processing differs. The lexical and structural overlap in the reading loop suffices for clone labeling.
- 共享行为: Open a URL connection and read input line by line using BufferedReader；Handle IOException with try-catch；Use similar boilerplate code patterns (URL, InputStream, BufferedReader)
- 行为差异: Function A returns the full HTML string and optionally writes to a file; function B parses specific lines for version numbers and calls another method；Function B includes UI cursor operations (show/hide wait cursor)；Function A has a parameter for encoding and directory path; function B has a fixed URL from a property
- 修正建议: Incorporate API call sequence features to capture shared patterns；Use data augmentation with URL reading examples；Train with contrastive learning on similar boilerplate code

### case_id=6212 FP lexical_or_api_overlap

- 方法: `SRWGuiClient` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Constructor that builds a GUI browser, reads XML from a URL, optionally applies XSLT transformation, and displays the result.
- B 摘要: Private method that downloads a YouTube page, parses the fullscreenUrl parameter, extracts video_id and t, and constructs a full video URL.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on lexical and API overlaps (e.g., URL, BufferedReader, reading lines) and missed the high-level semantic differences in overall functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones as 0; these functions have entirely different purposes and implementations despite some shared low-level I/O patterns.
- 共享行为: Both open a URL connection and read content line by line
- 行为差异: Function A is a constructor building a Swing GUI, Function B is a method returning a string；Function A processes XML/XSLT for display, Function B parses YouTube page URL parameters；Function A sets up UI components and event listeners, Function B has no UI interaction；Function A handles XML transformation and JEditorPane display, Function B constructs a download URL
- 修正建议: Incorporate structured features like control flow graphs or data flow to capture high-level semantics；Train on more diverse examples to reduce reliance on surface-level API co-occurrence；Use contrastive learning to push apart functionally different code with similar token patterns

### case_id=6213 FP partial_functionality

- 方法: `GetResponse` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens an HTTP connection to a URL, reads the response line by line, concatenates into a string and returns it.
- B 摘要: Opens a URL connection (with optional Basic Auth), reads the content line by line, writes each line to a temporary file while updating a status label, and does not return any value.
- 静态失败原因: GraphCodeBERT may have been misled by lexical overlap (e.g., 'url.openConnection()', 'BufferedReader', 'readLine()') and similar boilerplate for reading from a URL. The model may not have captured the critical differences in output handling (return vs file write), authentication, and UI updates due to limited context or reliance on surface-level patterns.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels clones based on overall functional similarity. Here, despite both reading from a URL, the purposes differ (one fetches content into a string, the other downloads to file with auth and UI). This is likely considered Type-4 (functionally unrelated) or broad Type-3 at best, but BCB's strict label 0 suggests they deemed it non-clone.
- 共享行为: Both functions open a URL connection (or HttpURLConnection) and read the input stream line by line using BufferedReader.
- 行为差异: Function A returns the concatenated response as a String; Function B returns void and writes output to a temporary file.；Function B includes optional HTTP Basic Authentication handling; Function A does not.；Function B updates a JLabel with download progress; Function A has no UI interaction.；Function A catches exceptions and prints stack traces; Function B throws IOException and does not handle exceptions.
- 修正建议: Train or fine-tune on examples that emphasize the overall purpose and output type rather than just shared I/O operations.；Incorporate method signatures and return types explicitly into the model input.；Add more examples of non-clone pairs that share common sub-tasks but differ in overall functionality.

### case_id=6214 FN partial_functionality

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using byte-by-byte stream copy.
- B 摘要: Copies a file to another file using FileChannel for efficient transfer, creating parent directories if needed.
- 静态失败原因: Static BERT models rely on token similarity and structural patterns; low Jaccard similarity and different API usage lead to false negative, missing the high-level copying semantic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as implementations of 'copy resource to file', accepting different I/O methods and source types as implementation variance.
- 共享行为: Copy data from a source to a destination file；Open input and output streams；Close streams after copying
- 行为差异: A supports URL and file sources; B only file sources；A uses byte-by-byte loop; B uses FileChannel.transferFrom；B creates missing parent directories; A does not；A throws Exception; B throws IOException with proper resource cleanup
- 修正建议: Use graph-based or data-flow representations to capture core copying pattern；Incorporate functional purpose classification during training；Augment training data with diverse implementations of same operation

### case_id=6215 FN benchmark_preference_bias

- 方法: `invoke` vs `parse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Invokes a remote HTTP service, sends request, reads response, and deserializes JSON with retry on timeout.
- B 摘要: Parses a delimited data file or URL into a structured DataSet, handling headers, types, and various formatting options.
- 静态失败原因: The model likely relied on lexical overlap (low Jaccard) and structural differences, leading to a non-clone prediction; the BCB label itself appears questionable.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'data retrieval and parsing' functions at a high level, but this is a very broad interpretation and unlikely to be a typical Type-3/4 clone.
- 共享行为: Both read input from an external source；Both parse content into a structured output；Both handle exceptions and errors
- 行为差异: A uses HTTP, B uses file/URL access；A uses JSON serialization, B uses delimited text parsing；A has retry logic, B does not；A returns a generic type, B returns a DataSet
- 修正建议: Re-evaluate BCB annotation for this pair; it may be a mislabel.；Improve models to detect semantic similarity despite low token overlap.；Use additional context or domain knowledge to avoid over-generalizing.

### case_id=6216 FN benchmark_preference_bias

- 方法: `encodeFileToFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Encodes a file using Base64 and writes the encoded content to another file.
- B 摘要: Launches a NexOpen project configuration by validating XML files, setting Hibernate dialect properties, and managing project resources within Eclipse.
- 静态失败原因: Static BERT correctly identified non-clone due to low token overlap and clearly different semantics; it did not 'fail' but disagreed with the BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled based on superficial similarity like both using I/O streams and exception handling, or due to a benchmark annotation error (false positive).
- 共享行为: Both involve file I/O operations with streams
- 行为差异: Domain: Base64 encoding vs Eclipse launch configuration；Input/output: single file pair vs complex configuration and project resources；Error handling: simple exception print vs throwing CoreException and RuntimeException；Complexity: simple loop vs multiple XML parsing, property setting, and resource adapters
- 修正建议: Re-examine BCB ground truth for this pair; likely a mislabel.；If using static model, ensure training data is cleaned of such false positives.

### case_id=6217 FP boilerplate_overlap

- 方法: `checkInputStream` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Verifies that bytes from an input stream match expected values.
- B 摘要: Handles various action commands from an event, such as selecting files for Graphviz/ImageMagick paths or saving UI preferences.
- 静态失败原因: The model likely over-relied on superficial lexical patterns like JFileChooser, null checks, or the presence of 'InputStream' and 'In' in both, or on common Java idioms. The large actionPerformed method contains many different code segments, and a static model might have matched some generic patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the functions have no functional overlap; actionPerformed involves GUI and configuration settings, while checkInputStream is a data validation helper.
- 行为差异: checkInputStream reads and compares binary data; actionPerformed manages UI dialogs and preferences.；checkInputStream is a short utility; actionPerformed is a long event handler with many branches.；No commonality in input/output or side effects.
- 修正建议: Use a model that captures structural and dataflow aspects at a higher granularity.；Filter out or downweight boilerplate patterns common in GUI event handlers.；Improve training data diversity to avoid false positives from long multi-branch methods.

### case_id=6218 FN lexical_or_api_overlap

- 方法: `copyResource` vs `createJAR`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using byte-by-byte streaming.
- B 摘要: Creates a JAR file or directory, copies a bundled jar into it, serializes an object to a file, and copies that file to the target directory.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token-level overlap (Jaccard 0.14) and surface syntax. Here, the method names, variable names, and API calls (e.g., FileChannel, ObjectOutputStream vs. InputStream/OutputStream) are very different, leading to low similarity. The model fails to capture the abstract file-copying intent due to lexical divergence.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a clone because both functions share the core behavior of copying a resource (file/jar) to a destination, which is a common I/O pattern. The additional steps in B (directory creation, serialization) are considered peripheral, so the pair is treated as a Type-4 (semantic) clone.
- 共享行为: Both functions copy data from a source to a destination using file streams.；Both handle file I/O and can deal with resources located via URLs or file paths.；Both ultimately produce a file at a designated destination.
- 行为差异: Function A only copies a single resource; function B also creates directories, serializes objects, and performs multiple copy operations.；Function A uses simple byte-by-byte read/write; function B uses FileChannel.transferTo for one copy and ObjectOutputStream for serialization.；Function B involves temporary files and cleanup (deletion), while Function A does not.；Function B has different control flow (conditional for .jar vs directory creation) making it more complex.
- 修正建议: Enhance model with data flow analysis to track write/read operations independent of specific APIs.；Use code summarization or semantic embeddings that capture high-level program intent.；Incorporate structural similarity (e.g., control flow graphs) to complement lexical matching.

### case_id=6219 FN partial_functionality

- 方法: `getFile` vs `gzip`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its service endpoint address, and saves the modified file.
- B 摘要: Compresses the contents of a directory into a GZIP file.
- 静态失败原因: The model focused on token-level differences (different method names, APIs like GZIP vs XML) and low Jaccard similarity, missing the abstract shared I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider this a clone if they focus on the generic 'read file and write to another file' pattern, ignoring specific transformations, but the low similarity and different functionality suggest it's a borderline Type-4.
- 共享行为: Both read from an input source and write to an output file using streams.
- 行为差异: Different input types: URL vs local directory.；Different processing: XML modification vs compression.；Different output format: plain text WSDL vs GZIP archive.；Different error handling: specific exceptions vs generic Exception.
- 修正建议: Incorporate data flow analysis to capture read-write patterns.；Use representation learning that abstracts over specific APIs.

### case_id=6220 FP lexical_or_api_overlap

- 方法: `import_hints` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads hint data from a file or URL and places puzzle pieces on a board, returning success status.
- B 摘要: Fetches a YouTube page, extracts video parameters, constructs a fullscreen URL, and returns it.
- 静态失败原因: The model likely focused on surface-level lexical overlap (e.g., URL, BufferedReader, try-catch) and structural patterns common in Java I/O code, ignoring the distinct semantic contexts and goals.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotations typically require at least partial functional similarity or shared domain-specific behavior. These functions have different purposes and operate on unrelated data, so they are not considered clones.
- 共享行为: Both open a URL connection and read input using BufferedReader.；Both parse lines of input using StringTokenizer or string operations.；Both handle IOException/Exception with try-catch.
- 行为差异: Function A places pieces on a board for a puzzle game; function B extracts video metadata and builds a URL.；Function A returns a boolean; function B returns a String.；Function A writes to the board; function B updates progress bars and prints debug info.；Parsing logic differs: A parses integer coordinates; B splits strings on '&' and '='.
- 修正建议: Incorporate global context or domain knowledge to distinguish game logic from web scraping.；Use contrastive learning to emphasize functional intent over common API usage patterns.；Augment training data with more pairs that share I/O structure but differ in purpose.

### case_id=6221 FN lexical_or_api_overlap

- 方法: `handler` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL line by line, extracts substrings based on target patterns, and updates a provided map in place.
- B 摘要: Sends an HTTP POST request with parameters and returns the full response body as a string, with error handling.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized token overlap (BufferedReader, readLine, IOException, URL) and structural patterns, missing the fundamentally different control flow and purpose.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as a clone due to superficial similarity: both involve reading text from a network source with BufferedReader, which is a common boilerplate pattern, and both have similar structure (try-catch, while loop).
- 共享行为: Both read data from a network resource line by line using BufferedReader；Both handle IOException
- 行为差异: A modifies an input map in place, B returns a string；A uses URL and openStream (GET-like), B uses Apache HttpClient POST；A parses lines for patterns, B appends entire lines；B sets error fields on failure, A silently catches exceptions
- 修正建议: Add more training examples that distinguish network resource reading from API-specific HTTP clients；Incorporate data flow analysis to track side effects and return values；Use contrastive learning to emphasize behavioral differences despite token overlap

### case_id=6222 FN benchmark_preference_bias

- 方法: `copyFileTo` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file to a destination using NIO FileChannel.
- B 摘要: Launches a NexOpen project configuration by validating project files, processing XML, and setting up Hibernate dialect.
- 静态失败原因: The model correctly identified low token overlap and distinct purposes; failure may stem from BCB label noise.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled due to both involving file I/O and exception handling, but this is insufficient for clone classification.
- 共享行为: None
- 行为差异: copyFileTo performs simple file copy via NIO channels；launch performs complex project setup with XML parsing, Maven profile handling, and job scheduling
- 修正建议: Review BCB annotation for this pair；Consider removing noisy labels from training data

### case_id=6223 FN partial_functionality

- 方法: `decodeFileToFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Decodes a Base64-encoded file and writes the decoded output to another file, returning success status.
- B 摘要: Downloads a KMZ file from a URL, extracts its zip entries, and writes each entry to a local file.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on low token overlap (0.22), different API calls (Base64 vs ZipInputStream), different exception handling structures, and different method signatures, leading to a non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered the core I/O loop pattern (read-write buffer) as sufficiently similar, ignoring the specific transformation (Base64 vs zip) as non-essential for a broad Type-4 clone classification.
- 共享行为: Both read from an input source and write to an output source using buffered streams.；Both use a while loop to read bytes into a buffer and write them out.；Both close the streams after processing.
- 行为差异: Function A decodes Base64; function B extracts zip entries.；Function A writes to a single file; function B writes multiple files from zip entries.；Function A uses try-catch-finally for exception handling; function B uses throws and no finally.；Function A returns a boolean; function B is void.
- 修正建议: Incorporate dataflow analysis to capture the core buffer copy pattern.；Use a model that can abstract away specific library calls and recognize underlying I/O semantics.；Include contrastive learning with diverse I/O examples to learn structural similarity.

### case_id=6224 FP boilerplate_overlap

- 方法: `sendPost` vs `postXml`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends HTTP POST with a generic parameter string, returns response body or empty string on exception.
- B 摘要: Sends HTTP POST with XML data and SOAP headers, returns response body or throws RuntimeException on exception.
- 静态失败原因: Static BERT models may overweigh the common HTTP POST boilerplate (open connection, setDoOutput, write, read response) and neglect differences in headers, error handling, and parameter semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone due to differing purposes (generic POST vs SOAP XML POST), distinct error handling strategies, and low token overlap, despite sharing HTTP POST boilerplate.
- 共享行为: Perform HTTP POST request；Write data to output stream；Read response line by line；Return response as string
- 行为差异: Error handling: A returns empty string, B throws RuntimeException；Headers: A sets Accept-Language, B sets Content-Type, Accept, and SOAPAction；Writer: A uses PrintWriter, B uses OutputStreamWriter；B sets timeouts and explicit request method, A does not
- 修正建议: Incorporate more nuanced understanding of error handling semantics；Differentiate between generic and specialized HTTP requests；Add attention to header and parameter differences；Use contrastive learning on similar boilerplate but different intent functions

### case_id=6225 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a new version by reading a version file from a URL and comparing build numbers.
- B 摘要: Extracts a full screen URL from a YouTube page by parsing HTML for 'fullscreenUrl' and constructing a video download URL.
- 静态失败原因: Static BERT/GraphCodeBERT may overemphasize lexical and API overlap (e.g., URL, BufferedReader, while loop) and miss the distinct semantic purpose, leading to false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the overall functionality is completely different (version check vs YouTube URL extraction), despite some superficial structural similarities in I/O pattern.
- 共享行为: Both open a URL and read input line by line.；Both parse lines for specific prefixes or substrings.；Both use BufferedReader and InputStreamReader.；Both handle exceptions with try-catch.
- 行为差异: A checks for version and build lines and compares build versions; B looks for 'fullscreenUrl' and extracts video parameters.；A prints to UI messages; B prints debug output to console.；A returns void; B returns a String URL.；A uses different condition structures and error handling (GUIUtilities vs System.err).
- 修正建议: Incorporate more abstract representations like control flow or data flow.；Use contrastive learning to discriminate based on task-level semantics.；Add structural similarity measures beyond token Jaccard.

### case_id=6226 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `postXml`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads integers from a resource file line by line and returns them as a HashSet.
- B 摘要: Sends an HTTP POST request with SOAP XML and returns the response body as a string.
- 静态失败原因: Static BERT models may have focused on token-level overlap like 'URL', 'InputStreamReader', 'readLine', 'try-catch', 'conn', etc., ignoring the drastically different control flow and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels Type-3/4 clones where functionality is partially similar; here there is no functional overlap beyond generic I/O boilerplate, so it's a non-clone.
- 共享行为: Both read input line by line (file vs HTTP response)；Both use URL and URLConnection；Both have exception handling (printStackTrace vs wrap in RuntimeException)
- 行为差异: Function A reads from local resource file, B sends HTTP request；Function A returns integers, B returns response string；Function A doesn't handle output, B writes request body；Function A ignores errors and returns partial result, B throws RuntimeException
- 修正建议: Enhance model with dataflow or control flow awareness；Add negative sampling of API-sharing non-clones；Incorporate semantic role labeling to distinguish reading vs writing

### case_id=6227 FP partial_functionality

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads multiple comma-separated string fields into sets and a map, then parses a file to populate a hash and additional sets for Tibetan/Sanskrit processing.
- B 摘要: Copies a file from source to destination with permission checks and overwrite prompt, showing progress.
- 静态失败原因: The static BERT model may have been misled by superficial similarities such as common I/O boilerplate (FileInputStream, IOException, try-catch) and the presence of loops with byte buffers. The truncated code_a includes a long file parsing section that resembles a generic reading loop, which could be confused with the copy loop in code_b.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would likely label non-clone because the functions have entirely different functionality and input/output. Even though both involve file reading, the intent and data transformation are fundamentally different.
- 共享行为: Both perform file I/O operations (reading a file in A, reading and writing in B).；Both handle IOException around file operations.；Both use loops to process data (tokenizing in A, copying buffer in B).
- 行为差异: Different primary purpose: data initialization vs file copying.；Different input/output: A reads multiple string fields and a configuration file; B copies a file bytewise.；Different control flow: A uses multiple StringTokenizer loops and conditional parsing; B uses a while loop with progress printing.；Different exception handling: A throws custom Error; B throws FileCopyException and catches IOException.
- 修正建议: Improve model sensitivity to high-level semantics by incorporating function name and signature analysis.；Enhance training data with more diverse negative pairs that share low-level I/O patterns but differ in purpose.；Use dataflow or program dependence graphs to capture actual data transformations.

### case_id=6228 FN benchmark_preference_bias

- 方法: `split` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: split a FASTA file into multiple files based on size or entry count
- B 摘要: launch a NexOpen project by configuring Maven POM files and Hibernate settings
- 静态失败原因: The static model correctly predicted non-clone; it did not fail. The supposed error is due to an incorrect BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label of 1 is likely an annotation error; there is no meaningful semantic or syntactic similarity between the two functions, even under broad Type-3/Type-4 criteria.
- 行为差异: function A performs file splitting; function B performs project launch configuration；A handles FASTA file I/O with FileChannel; B uses Eclipse/IDE APIs and XML processing；A has loops over file chunks; B has conditional checks on project files
- 修正建议: Re-evaluate the BCB label for this pair as non-clone；Include this pair as a negative example in the dataset

### case_id=6229 FP lexical_or_api_overlap

- 方法: `getXML` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches XML or response from a given URL by encoding the request, reading all lines, and returning the concatenated result.
- B 摘要: Fetches a YouTube page, extracts video parameters from a specific line, and constructs a full video URL.
- 静态失败原因: The model over-weighted lexical and API-level similarities (URL, BufferedReader, InputStreamReader, try-catch) and ignored differences in control flow and overall intent, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have fundamentally different purposes and only share generic boilerplate code for URL reading, lacking functional similarity.
- 共享行为: Both open a URL connection and read the response line by line.；Both use BufferedReader and InputStreamReader.；Both handle IO exceptions and return null or empty on failure.
- 行为差异: getXML returns all lines concatenated; getFullScreenUrl searches for a line containing 'fullscreenUrl' and parses it.；getXML takes parameters for URL and request; getFullScreenUrl uses a hardcoded instance variable.；getXML catches specific exceptions; getFullScreenUrl catches generic Exception.；getXML does not parse the response content; getFullScreenUrl extracts video_id, t, and title.
- 修正建议: Incorporate dataflow analysis to distinguish simple reading from conditional parsing.；Give higher weight to method names and context to capture intent.；Use contrastive learning to reduce sensitivity to common boilerplate.

### case_id=6230 FP lexical_or_api_overlap

- 方法: `importRoles` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Imports roles from a URL by buffering lines until a closing XML tag is found and parsing the buffer into RoleName objects.
- B 摘要: Reads tab-delimited data from a URL using a Scanner, extracts id and description, and adds them concatenated to a vector.
- 静态失败原因: The static BERT model likely focused on the similar API calls (URL, openStream, readLine/Scanner) and loop structure, lacking deeper semantic understanding of the different parsing logic and output types, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically considers functions as clones only if they perform the same specific task (e.g., both parse XML roles). Here the tasks differ fundamentally (XML role parsing vs tab-delimited data reading), so BCB would label non-clone despite similar I/O boilerplate.
- 共享行为: Open a URL and read its content line by line；Extract data from the input through parsing；Handle IO and URL-related exceptions
- 行为差异: Output type: ArrayList<RoleName> vs void (modifies Vector<String>)；Parsing logic: XML tag detection and buffer accumulation vs tab-delimited line-by-line scanning；Error handling: no resource cleanup in finally vs explicit stream close in finally；Accumulation strategy: buffer until tag vs immediate per-line extraction
- 修正建议: Incorporate dataflow or graph-based representations to track how data is transformed through variables；Use contrastive learning to distinguish functions with similar API but different semantics；Add attention to parsing-specific tokens and output structures

### case_id=6231 FP lexical_or_api_overlap

- 方法: `process` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Processes a template (Freemarker, XSLT, or copy) to generate a file in a build directory.
- B 摘要: Handles UI action events to configure settings like file paths, look-and-feel, and data formats.
- 静态失败原因: The model likely over-relied on shared lexical patterns (e.g., 'File', 'IOException', 'switch', 'try-catch') and similar control flow structures, ignoring the distinct semantic contexts and purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because these are completely different functionalities: code generation vs. UI event handling, with no overlapping business logic or intent.
- 共享行为: Both use file I/O operations；Both have conditional logic with switch/if-else；Both handle exceptions；Both involve directory/file path manipulation
- 行为差异: Process: generates output files based on templates；ActionPerformed: updates UI state and saves user preferences；Process: uses Freemarker/XSLT for content generation；ActionPerformed: shows file choosers and modifies UI components
- 修正建议: Increase training data diversity to reduce bias towards common Java idioms；Incorporate dataflow analysis to differentiate between code generation and UI event handling；Use function-level semantic clustering to separate unrelated domains

### case_id=6232 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request for portal pages, including authentication, caching, and error handling.
- B 摘要: Copies a file from source to destination using buffered I/O and exception handling.
- 静态失败原因: Static BERT model correctly predicted non-clone; the benchmark label appears to be a misannotation, causing disagreement.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled as clone due to broad Type-4 category or potential misinterpretation of both involving I/O operations, despite completely different application domains.
- 共享行为: Both contain try-catch blocks for exception handling
- 行为差异: Function A is a servlet doGet method dealing with HTTP requests, page retrieval, user permissions, and caching.；Function B is a static utility method for file I/O operations with no web-related logic.
- 修正建议: Re-evaluate BCB annotation for this pair to correct the label.；Enhance training data filtering to reduce noisy labels.

### case_id=6233 FP lexical_or_api_overlap

- 方法: `run` vs `scrapeForIsbns`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a map tile from a URL, reads its GeoJSON content, and adds it to the data source.
- B 摘要: Scrapes ISBN-10 numbers from a URL by reading lines and matching a regex pattern.
- 静态失败原因: The model likely over-emphasized the common API usage (URL, InputStream, BufferedReader, readLine) and error handling, ignoring the completely different processing after reading the stream. The semantic divergence was not captured due to long-range dependencies.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB intends to avoid labeling as clones code that only shares boilerplate patterns (e.g., reading from URL) without functional similarity. The functions' core purposes are entirely different.
- 共享行为: Both open a URL and read line by line using BufferedReader；Both handle IOException
- 行为差异: A constructs a GeoJSON string and processes it into geometry objects; B extracts ISBN strings using regex；A uses synchronization to avoid duplicate requests; B uses retry logic for connection failures；A returns void; B returns integer count of matches
- 修正建议: Incorporate data flow analysis to track how the read data is used；Focus on the return type and side effects to distinguish similar I/O patterns；Use contrastive learning to penalize pairs that only share boilerplate

### case_id=6234 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests to retrieve and serve a portal page with logging, caching, and permission checks.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: The low lexical overlap (token Jaccard 0.046) and different method signatures likely caused the model to predict non-clone, which is consistent with the semantic difference; the BCB label appears anomalous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider the presence of file I/O as partial functionality similarity, but this is weak given the completely different main purposes.
- 共享行为: Both involve file I/O operations (writing to temp file in A, copying file in B).；Both use Java I/O classes (File, FileWriter, FileChannel).
- 行为差异: A serves HTTP responses and manages page lifecycle; B is a simple file copy.；A has complex control flow, error handling, and external dependencies; B is straightforward.；A's file operation is a side effect for caching; B's core purpose is file copying.
- 修正建议: Verify the BCB annotation for this pair to ensure correctness.；Improve models to better handle cases where BCB labels may be inconsistent.

### case_id=6235 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `runDynusT`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles various UI preference settings via action commands, opening file choosers and updating UI components.
- B 摘要: Copies executable and model files to a temporary directory, runs an external simulation executable, and optionally cleans up.
- 静态失败原因: The static BERT model likely focused on superficial lexical similarities (e.g., both use File, JFileChooser, and similar variable names) and failed to capture the overall semantic context and dataflow differences, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label these as non-clones because they have completely different functionality and are from different application domains, with no shared behavior beyond superficial file operations.
- 行为差异: Function A is a UI event handler for setting preferences; Function B sets up and runs a simulation.；Function A uses JFileChooser for user file selection; Function B copies files programmatically.；Function A updates UI components and stores preferences; Function B runs an external process and handles I/O.；Function A is GUI-oriented; Function B is backend automation.
- 修正建议: Incorporate dataflow analysis to distinguish local file handling from UI preferences.；Use method names and surrounding context to disambiguate event handlers from automation routines.；Train on more diverse examples with lower token overlap but different semantics.

### case_id=6236 FN partial_functionality

- 方法: `addIDs` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Adds metabolite IDs from a web service to a peak list row by parsing HTML responses and extracting various database identifiers.
- B 摘要: Invokes a remote method via HTTP POST, parses the JSON response, and returns the deserialized object, with retry logic on timeout.
- 静态失败原因: Even though the functions share some API tokens like 'BufferedReader' and 'URL', the overall semantics diverge. Static models may miss the high-level task similarity and rely on local lexical matching, leading to false negative prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: Both functions involve network I/O and reading responses, which could be seen as a Type-4 'web service invocation' pattern. However, the specific logic and purpose are very different.
- 共享行为: Both make an HTTP request and read the response line by line using BufferedReader
- 行为差异: addIDs parses HTML to extract specific metabolite IDs and sets row properties; invoke is a generic RPC caller that deserializes JSON.；invoke includes retry logic on ConnectTimeoutException; addIDs does not.
- 修正建议: Incorporate global semantic information or code summarization to recognize common patterns like 'fetch and parse'.

### case_id=6237 FP boilerplate_overlap

- 方法: `PageLoader` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a web page's content into a string via URL and BufferedReader.
- B 摘要: Checks for software upgrades by querying a database and a remote license server, processing upgrade entries.
- 静态失败原因: The static model likely over-weighted the lexical overlap of URL/BufferedReader patterns, which are common boilerplate but do not indicate semantic similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels 0 because the functions have completely different purposes and semantics beyond the trivial I/O boilerplate; they are not even partial clones.
- 共享行为: Both open a URL connection and read lines using BufferedReader.；Both close the BufferedReader after reading.
- 行为差异: Function A is a constructor that simply concatenates all lines into a single string.；Function B performs database operations, license validation, UI updates, and logic for upgrade availability.；Function B handles multiple conditional cases and parses structured data (XML-like).
- 修正建议: Add a filter to ignore common boilerplate code (e.g., URL reading patterns) when they don't constitute the core logic.；Train with data where such boilerplate is explicitly labeled as non-clone.

### case_id=6238 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Modifies a properties file for a given locale, optionally copying a default English file as a template.
- B 摘要: Copies a file from source to target using NIO FileChannel.
- 静态失败原因: Low token overlap (Jaccard 0.05) and different API usage (NIO vs. IO) masked the underlying partial functional similarity of file copying embedded in Function A.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers clones even if only a sub-functionality (like file copy) is shared, as per Type-4 similar behavior criteria.
- 共享行为: Both involve copying the content of a source file to a destination file.
- 行为差异: Function A performs additional property reading, parsing, and rewriting, and handles missing locale files.；Function A uses byte-by-byte copy with FileReader/FileWriter, while B uses FileChannel.transferTo.；Function A's primary purpose is message modification, whereas B's sole purpose is file copy.；Function A includes error handling and file existence checks absent in B.
- 修正建议: Incorporate source code analysis to detect common sub-tasks like file copying.；Use program slicing or graph matching to align similar code fragments.；Train models with hierarchical functional decomposition awareness.

### case_id=6239 FN boilerplate_overlap

- 方法: `init` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads controller classes from a resource file by reading class names line by line from URLs found on the classpath.
- B 摘要: Performs an HTTP POST request and returns the response body as a string, handling HTTP errors and IO exceptions.
- 静态失败原因: The static model correctly predicted non-clone based on low token overlap and semantic differences, but BCB considered it a clone due to boilerplate similarity. The model did not fail; rather, the BCB label might be inconsistent.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled them as clones due to the similar structural pattern of reading lines from an input stream using BufferedReader within a try-catch block, which is a common boilerplate. However, the overall functionality is completely different, so this likely represents a borderline or erroneous annotation.
- 共享行为: Both use BufferedReader to read lines from an input stream；Both handle exceptions (IOException and ClassNotFoundException vs IOException) by logging or setting error fields
- 行为差异: Different purposes: class loading vs HTTP request；Different input sources (resource file URLs vs HTTP response stream)；Different error handling strategies (logging with stack trace vs setting error fields and returning null)；Different return types (void vs String)
- 修正建议: Increase emphasis on overall method purpose and API usage rather than local patterns.；Incorporate control-flow analysis to differentiate between different types of I/O operations.

### case_id=6240 FP lexical_or_api_overlap

- 方法: `retrieveTemplate` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches and caches the entire content of a blog URL as a string.
- B 摘要: Fetches a YouTube page, extracts specific parameters from a line containing 'fullscreenUrl', and constructs a full screen video URL.
- 静态失败原因: The model likely overemphasized the lexical and API overlap (URL, BufferedReader, while loop reading lines) and structural similarity, while ignoring the different output processing and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functional equivalence or very similar partial functionality. Here, the high-level goals differ significantly (template retrieval vs. YouTube URL extraction), so BCB would likely label them as non-clones.
- 共享行为: Both open a URL connection and read the response line by line using BufferedReader.
- 行为差异: Function A caches and returns the entire page content; Function B extracts specific parameters and constructs a new URL.；Function B includes output statements, progress bar updates, and error handling; A does not.；Function B uses URLConnection with setDoOutput(true); A uses URL.openStream() directly.；Function B only reads until it finds a specific line; A reads all lines.
- 修正建议: Incorporate method name and variable names as semantic clues.；Add attention to differences in output and control flow after the read loop.；Use contrastive learning with hard negatives that have API overlap but different semantics.

### case_id=6241 FN lexical_or_api_overlap

- 方法: `loadSourceCode` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a source file from classpath resource, applies syntax highlighting, and stores HTML-formatted result in a field.
- B 摘要: Reads a file from local path or classpath resource, concatenates lines into a string, and returns it, exiting on failure.
- 静态失败原因: Low token overlap (0.24) and differing API usage (CodeViewer vs System.exit) and return types misled the model; it missed the shared file-reading core.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often considers functions that read a file into a string as clones, even if output format differs, due to similar core functionality and control flow.
- 共享行为: Both read a text file from a classpath resource using BufferedReader；Both iterate over lines and concatenate them into a single string
- 行为差异: A applies syntax highlighting and wraps in HTML tags; B does not；A stores result in a field; B returns it；A catches exceptions silently; B prints stack traces and exits
- 修正建议: Augment training data with broad Type-4 clones；Use program dependence graphs to capture core behavior；Incorporate functional role classification

### case_id=6242 FP partial_functionality

- 方法: `addDataFromURL` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads content from a URL and appends it to a text buffer.
- B 摘要: Fetches ticket IDs from a REST API for a queue and retrieves each ticket, returning a list.
- 静态失败原因: The static BERT/GraphCodeBERT model may have been misled by the shared pattern of opening a stream, using BufferedReader to read lines, and handling exceptions, ignoring the larger functional context and different return types.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would likely annotate as non-clone because the core functionality is distinct: one is generic URL reading, the other is domain-specific ticket retrieval. Even though both involve reading from a stream, their overall purpose and complexity differ significantly.
- 共享行为: Both read text line by line from an input stream obtained from a URL/HTTP response.
- 行为差异: Function A is a simple one-shot read and append; B involves multiple steps including constructing a query, session handling, response parsing, and individual ticket fetching.；A appends to an internal text buffer; B returns a List of RTTicket objects.；B has specific business logic for checking existence and extracting ticket IDs; A does not.
- 修正建议: Train with contrastive examples that penalize pairs with only superficial stream-reading overlap.；Incorporate structural features like method signatures and call graphs to distinguish overall functionality.

### case_id=6243 FP lexical_or_api_overlap

- 方法: `serialize` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Serializes a content package to an output stream by parsing and copying a temporary file.
- B 摘要: Handles action events for GUI preferences, including file selection for Graphviz/ImageMagick paths and other settings.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized lexical overlap of terms like 'File', 'InputStream', and null checks, while missing the semantic context and overall functionality difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: None
- 共享行为: Both involve file operations (creating or selecting files).；Both perform null checks on objects before use.
- 行为差异: Function A writes serialized data to an output stream; function B updates GUI preferences.；Function A is I/O intensive with file copying; function B is event-driven with file chooser dialogs.；Function A has no user interaction; function B displays dialog boxes and updates UI components.；Function A is short and focused; function B is long and handles multiple commands.
- 修正建议: Use a model that captures long-range semantic intent and program logic.；Incorporate method signatures and class-level context to distinguish between file I/O and GUI event handling.；Apply contrastive learning to separate functions with similar API usage but different core tasks.

### case_id=6244 FP boilerplate_overlap

- 方法: `readUNI` vs `getEncoding`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a tab-separated file from a URL and extracts id and description into a vector.
- B 摘要: Extracts character encoding from HTTP response headers or body from a URL.
- 静态失败原因: Low token overlap but both involve URL reading, line scanning, and exception handling, which may have misled the model into considering them similar due to structural boilerplate.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones for functionally different tasks even if they share some I/O boilerplate.
- 共享行为: Both open a URL and read from it line by line；Both use I/O streams and handle exceptions；Both close resources in a finally block
- 行为差异: A reads tab-separated data records; B scans for charset keywords；A outputs to a vector; B returns an encoding string；A catches MalformedURLException and generic Exception; B throws IOException；A uses Scanner; B uses BufferedReader
- 修正建议: Increase sensitivity to core task semantics via dataflow analysis；Use contrastive learning on negative pairs with similar boilerplate but different purposes；Incorporate functional type information

### case_id=6245 FN benchmark_preference_bias

- 方法: `login` vs `handler`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Logs into a LOLA service via HTTP POST with email and password, reads the response's first line to extract and return a session ID.
- B 摘要: Reads a web page from a URL, extracts substrings based on markers for lines containing an include string, and updates a result map with the extracted values.
- 静态失败原因: Static BERT/GraphCodeBERT relies heavily on token and structural matching. The low token Jaccard (0.1585), different method signatures, and distinct string manipulation patterns led to a low similarity score, missing the broad functional overlap.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotators may have considered these Type-4 clones because both are high-level web data extraction tasks involving URL opening, line-by-line reading, and string parsing, despite different specific operations.
- 共享行为: Both perform HTTP requests to retrieve data from URLs.；Both use BufferedReader to read the response line by line.；Both handle IO exceptions with try-catch blocks.；Both involve string manipulation to extract specific information from the response.
- 行为差异: A uses HTTP POST with data encoding; B uses HTTP GET via openStream.；A only reads the first line; B reads all lines and processes each.；A returns a single session ID; B updates a map with possibly multiple extractions.；A has console output for logging; B is silent and catches exceptions without action.
- 修正建议: Incorporate data flow analysis to abstract the common pattern of HTTP data retrieval and extraction.；Use graph-based representations focusing on API call sequences and exception handling.；Train with more diverse Type-4 examples to capture high-level functional similarity.

### case_id=6246 FN lexical_or_api_overlap

- 方法: `save` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Saves given file contents to files and then copies them to a package directory with a package statement.
- B 摘要: Downloads a WSDL file from a URL, modifies it to update an endpoint, and saves it to a temporary directory.
- 静态失败原因: The static BERT model likely over-relied on lexical and API overlap (e.g., File, FileOutputStream, File.separator, directory creation) and missed the semantic difference in overall functionality. The high token Jaccard similarity (0.128) is not very high, but the presence of common file-handling idioms may have influenced the model.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels clones with significant syntactic similarity or partial functional overlap. Here, both functions involve file creation and writing, but their core purposes (saving data vs. downloading and modifying a WSDL) are too different for BCB to consider them clones. The BCB label of 1 may be an annotation error or based on very loose criteria.
- 共享行为: Both functions perform file I/O operations (creating files, writing to streams).
- 行为差异: Function A saves provided byte array contents to files; Function B downloads content from a URL.；Function A processes multiple files with a package statement; Function B downloads a single WSDL and modifies XML.；Function A throws generic Exception; Function B throws AxisFault and handles multiple specific exceptions.；Function A uses BufferedReader/BufferedWriter for file copying; Function B uses NIO channels and XML parsing.
- 修正建议: Incorporate higher-level semantic understanding, e.g., by modeling function purpose or using documentation/class context.；Improve representation learning to distinguish generic file I/O patterns from domain-specific functionality.；Use dataflow analysis to capture differences in data sources and transformations.

### case_id=6247 FP lexical_or_api_overlap

- 方法: `readRemoteFile` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a remote file and returns its entire content as a string by concatenating all lines.
- B 摘要: Reads a service configuration file and returns an instance of the framework factory class specified by the first non-comment line.
- 静态失败原因: The static model likely over-relied on token overlap (e.g., URL, BufferedReader, readLine, while loop structure) and ignored the differing return types and overall semantic purpose, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the functions have entirely different purposes and return types, despite superficial structural similarities. Their functionality is not equivalent even under Type-4 semantic clone criteria.
- 共享行为: Both use URL and BufferedReader to read lines from an input stream.；Both have a loop reading lines until termination.
- 行为差异: Function A concatenates all lines into a single string; Function B searches for a specific line to instantiate a class.；Function A returns a String; Function B returns a FrameworkFactory object or throws an exception.；Function A handles EOFException and IOException locally; Function B throws Exception and does not handle I/O errors within the method.；Function A closes the reader conditionally; Function B uses a finally block for guaranteed closure.
- 修正建议: Incorporate type information and dataflow analysis to distinguish concatenation versus reflective instantiation.；Use contrastive learning with hard negatives that share API usage but differ in goal.；Add attention to method names and return types.

### case_id=6248 FN partial_functionality

- 方法: `File2String` vs `parse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads a file from filesystem or classpath resource line by line and returns its content as a single string, exiting on failure.
- B 摘要: Parses a structured data file (CSV-like) with headers, types, and delimiter configuration into a DataSet object, handling URL or file input and throwing exceptions.
- 静态失败原因: The static BERT model likely focused on the high-level semantic difference (simple file reading vs structured data parsing) and failed to recognize the clone as defined by BCB, which may accept broader Type-4 similarity based on shared file-reading boilerplate and exception handling patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered both as file reading/parsing utilities and prioritized the shared pattern of opening files, reading lines, and handling IO errors over the higher-level differences in parsing logic and output format.
- 共享行为: Both open and read from a file or URL；Both use BufferedReader and handle IOExceptions；Both involve looping over lines of input
- 行为差异: Function A returns the entire file as a single string; Function B parses structured data into typed columns and returns a DataSet；Function A uses System.exit on failure; Function B throws exceptions；Function B handles headers, types, and tokenization; Function A does simple concatenation；Function B supports URL input and various delimiters; Function A handles filesystem and classpath
- 修正建议: Incorporate higher-level semantic understanding of method purpose (e.g., output type, method name) beyond token sequences；Use a more granular clone type classification that distinguishes between different levels of abstraction in file processing

### case_id=6249 FN boilerplate_overlap

- 方法: `testNetworkHTTP` vs `loadExistingAntlibs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Tests network HTTP connectivity by making multiple HTTP requests and reading response lines.
- B 摘要: Loads ant libraries from classpath resources by reading lines and resolving URIs.
- 静态失败原因: Static BERT predicted non-clone, correctly identifying semantic differences; the BCB ground truth label considered the structural I/O pattern a clone, so the model was too strict for BCB preferences.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider the shared I/O loop pattern and URL usage as sufficient for a Type-3 clone despite different semantic intents, due to broad definition of syntactic similarity.
- 共享行为: Both use BufferedReader to read lines from an InputStream obtained from a URL；Both loop until null reading lines；Both handle IOException
- 行为差异: A makes multiple sequential HTTP requests without processing read data; B iterates over classpath resources and processes each line to load ant libraries；A uses HttpURLConnection and disconnects; B uses ClassLoader.getResources and closes streams；A's URL targets are fixed; B's URLs are dynamically resolved from classpath resources
- 修正建议: Incorporate task-specific semantics or intent detection to distinguish I/O boilerplate from actual functionality clones；Use method-level embeddings that capture the purpose beyond common API usage patterns

### case_id=6250 FN partial_functionality

- 方法: `main` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to local files.
- B 摘要: Copies a source file to a target file using NIO FileChannel.
- 静态失败原因: Models focused on lexical and structural mismatches (different method names, APIs, token overlap) and missed the high-level semantic similarity of file copying operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as 'copying data from an input to an output' at a high abstraction level, ignoring specific input sources and output structures, thus a Type-4 clone.
- 共享行为: Both perform file I/O operations that read from a source and write to a destination；Both handle IOException
- 行为差异: Source is a URL in A, local file in B；A extracts a zip archive, B copies a single file；A outputs multiple files, B outputs one file；A uses ZipInputStream, B uses FileChannel
- 修正建议: Incorporate abstract semantic roles like 'source' and 'sink'；Train on broader clone types including Type-4；Use data-flow analysis to recognize read-write patterns

### case_id=6251 FN boilerplate_overlap

- 方法: `doVersionCheck` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a version check URL lines, extracts .build and .stablebuild values, and calls another method to execute version check.
- B 摘要: Reads a file or classpath resource line by line and concatenates all lines into a single string, with error handling that exits the program.
- 静态失败原因: Static BERT/GraphCodeBERT models might fail because they rely on token-level attention and may miss the overall semantic difference due to overlapping tokens like 'BufferedReader', 'InputStream', 'readLine', etc., focusing on the common I/O boilerplate and ignoring the essential differences in loop body processing.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as clone because both functions share a common pattern of reading lines from an input stream using BufferedReader, which is a classic Type-3 clone pattern despite different processing logic.
- 共享行为: Open an InputStream；Wrap in BufferedReader；Read lines in a while loop；Close the reader
- 行为差异: A reads from URL, B reads from file or classpath resource；A parses specific prefixes, B appends all lines；A calls another method, B returns concatenated string；A shows wait cursor and error dialog, B prints to console and exits on error
- 修正建议: Include more varied training examples where I/O patterns are similar but processing differs；Use data flow analysis to distinguish different uses of read lines；Add structure-aware encoding to focus on loop body content

### case_id=6252 FN partial_functionality

- 方法: `getJSONData` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches JSON data from a URL via HTTP and parses it into a JSONObject.
- B 摘要: Reads a file from filesystem or classpath and returns its content as a String.
- 静态失败原因: Static BERT models rely on lexical and API token overlaps, which are low (Jaccard=0.225) due to different APIs (HTTP vs file I/O) and method names, missing the abstract I/O pattern similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both perform I/O to obtain textual data, use a similar read-loop pattern, and return the content, aligning with Type-4 (functional similarity) or broad Type-3 (near miss) clones.
- 共享行为: Both open an input stream；Both use BufferedReader to read lines；Both append lines to a StringBuilder/StringBuffer；Both return the accumulated content
- 行为差异: A makes an HTTP request; B accesses local file or classpath resource；A returns JSONObject; B returns String；A uses JSONTokener for parsing; B performs no parsing；B has additional error handling and calls System.exit on failure
- 修正建议: Incorporate dataflow analysis to recognize abstract I/O patterns；Use control flow graph similarity focusing on loop structures and I/O operations；Augment training with more I/O-related clone examples across different sources

### case_id=6253 FN benchmark_preference_bias

- 方法: `readData` vs `loadExistingAntlibs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads initialization data from a file into multiple sets and maps for Tibetan and Sanskrit text processing.
- B 摘要: Loads antlib definitions from classpath resources, resolving URIs and calling loadAntLib for each.
- 静态失败原因: The static model correctly identified them as non-clones because semantic and functional differences dominate; BCB's label likely reflects a broad pattern-based bias that the model does not follow.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone based on superficial structural similarity: both read lines in a loop, parse tokens, and populate collections, despite entirely different domains and output purposes.
- 共享行为: Both iterate over multiple entries from an input source (file lines vs. classloader resources).；Both use while loops and handle I/O exceptions.
- 行为差异: Input source and format differ: structured file with delimiter vs. classpath resource text lines.；Data collected: sets and maps for linguistic processing vs. antlib URI loading.；Error handling: different messages and exception types.
- 修正建议: Re-evaluate BCB labels for partial functionality cases to ensure ground truth consistency.；Train models with more nuanced clone categories (e.g., Type-3 vs 4) to capture intended semantics.

### case_id=6254 FN partial_functionality

- 方法: `doTransfer` vs `wordFrequency`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request to a different URL by creating a new connection, copying headers, and streaming the request body and response.
- B 摘要: Fetches word frequency from a web service by sending a request to a URL template, reading the response, and matching a pattern to extract the frequency.
- 静态失败原因: The token Jaccard similarity is very low (0.159), and the method names and overall purpose differ, so the model likely focused on surface-level lexical differences and missed the underlying structural similarity of URL-based I/O patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions involve opening a URL connection, reading data, and processing it in a loop with similar I/O patterns and exception handling, which could be considered a 'URL access' type-4 semantic clone.
- 共享行为: Both create a URL from a string and open a connection.；Both read from an input stream in a loop.；Both handle MalformedURLException and IOException by printing stack traces.；Both use standard Java I/O classes (URL, InputStream, BufferedReader, etc.).
- 行为差异: A acts as a proxy forwarding full HTTP requests and responses; B extracts a single integer frequency.；A uses HttpURLConnection and sets many request headers; B uses URL.openStream() without custom headers.；A writes to an output stream (response); B returns an int.；A has complex output handling with multiple streams; B has simple line-by-line matching.
- 修正建议: Augment training data with examples of functions sharing structural patterns despite low lexical overlap.；Incorporate AST or graph-based features to capture common control flow and data flow (e.g., URL opening, stream reading, exception handling).；Use contrastive learning to emphasize shared behaviors over surface tokens.

### case_id=6255 FN partial_functionality

- 方法: `testCopyUnknownSize` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Tests copying an input stream to an output stream with unknown size using a utility method and verifies the result.
- B 摘要: Retrieves a resource via URL, caches it to a local file, and returns an InputStream from the cache.
- 静态失败原因: Static BERT models like GraphCodeBERT rely heavily on token and AST structure overlap, which is low here (Jaccard=0.064). They may fail to recognize the shared stream copying pattern due to different contexts, lengths, and API usage.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as a clone because both functions involve copying an input stream to an output stream, a common low-level functionality that fits Type-4 (weak) clones under BigCloneBench's broad annotation guidelines.
- 共享行为: Both involve reading from an InputStream and writing to an OutputStream.；Both perform a byte-level copy operation (one via utility, one manually).
- 行为差异: A is a unit test with assertions; B is a production method with caching and error handling.；A uses ExtraIOUtils.copy with a simple loop; B uses a manual read-write loop with buffered streams.；A operates on a fixed in-memory data; B reads from a network URL and caches to a file.
- 修正建议: Enhance model to focus on data flow of IO operations rather than surface tokens.；Incorporate external knowledge about utility methods like ExtraIOUtils.copy to infer high-level behavior.；Use contrastive learning to capture partial functionality similarity across different contexts.

### case_id=6256 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `issueCommandToServer`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks and their text from a given URL by parsing HTML.
- B 摘要: Sends a command and capsule data to a server via HTTP POST and returns the server response.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by overlapping API tokens (e.g., URLConnection, BufferedReader, InputStreamReader) and similar control flow (while loop reading lines), causing it to overestimate similarity despite low Jaccard index.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions perform fundamentally different tasks (link extraction vs. command sending), despite sharing low-level I/O patterns. The annotation tends to focus on functional similarity rather than structural alignment.
- 共享行为: Both open URL connections to interact with web resources；Both use BufferedReader to read data from the connection；Both handle IOException
- 行为差异: Function A parses HTML links; Function B sends a command with encoded parameters；Function A uses GET implicitly; Function B uses POST explicitly；Function A returns two vectors; Function B returns a single response string；Function A uses regex for extraction; Function B uses URLEncoder for encoding
- 修正建议: Incorporate task-level semantics via code summarization or docstring embeddings；Add data-flow and control-flow awareness to distinguish different I/O operations；Use contrastive learning with functionally annotated pairs

### case_id=6257 FP boilerplate_overlap

- 方法: `sendPost` vs `wordFrequency`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the full response as a string.
- B 摘要: Queries word frequency by replacing a placeholder in a URL, reading the response, and extracting a numeric frequency via pattern matching.
- 静态失败原因: The model may have focused on the common boilerplate (URL, BufferedReader, while readLine, exception handling) and ignored the different method signatures, return types, and core logic. Lexical overlap from shared API tokens (URL, BufferedReader, etc.) caused a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the overall functionality differs significantly: one is a generic POST sender, the other is a specific word frequency query. The token similarity is low, and the core logic (data sending vs. pattern extraction) diverges.
- 共享行为: Both open a URL and read data from an input stream using BufferedReader；Both handle exceptions (IO and URL malformation)；Both return a result after processing the response
- 行为差异: Function A uses HTTP POST with output (param), while B uses GET (implicit) without output；A sets request properties (Accept-Language) and uses PrintWriter; B does not；A returns concatenated response string; B returns an integer after pattern matching；B modifies a stored string (webQuery) with a placeholder; A takes URL and param as arguments
- 修正建议: Include structural features like method signature, return type, and control flow depth；Enhance training with negative examples that share API usage but differ in functionality；Use graph-based representations to capture data flow and control dependencies；Incorporate type information and method call patterns

### case_id=6258 FN benchmark_preference_bias

- 方法: `copyResource` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file byte by byte.
- B 摘要: Reads a DICOM file, parses its metadata, and rewrites it with a specific encoding.
- 静态失败原因: Static BERT/GraphCodeBERT correctly identified non-clone due to low token overlap and domain-specific APIs, but this resulted in a false negative against BCB's lenient clone definition.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as resource copying operations (read from source, write to destination) despite different formats and libraries, favoring broad functional similarity (Type-4).
- 共享行为: Both read from an input source and write to an output destination.；Both use file streams and handle I/O exceptions.
- 行为差异: copyResource performs a raw byte copy; readAndRewrite processes DICOM-specific data structures.；readAndRewrite uses specialized DICOM libraries; copyResource uses generic Java I/O.；readAndRewrite transforms the data (re-encodes); copyResource does a bitwise copy.
- 修正建议: Align model training with BCB-style annotations or define explicit functional similarity criteria.；Incorporate high-level task understanding (e.g., 'copy' vs 'rewrite DICOM') into clone detection.

### case_id=6259 FN partial_functionality

- 方法: `copyFileTo` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a source file to a destination file using a 1024-byte buffer.
- B 摘要: Builds an edited version of a web site by reading XML configuration and page files, transforming them with XSLT, and writing output files.
- 静态失败原因: Static BERT models rely on token overlap and structural similarity; the low Jaccard (0.061) and vastly different method signatures and control flow led to a non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as file I/O utilities that read and write data, thus a broad Type-3 clone despite different purpose.
- 共享行为: Both read from an input file using FileInputStream and write to an output file using a buffer.
- 行为差异: Function A is a straightforward file copy; function B involves XML parsing, XSLT transformation, string manipulation, multiple file I/O operations, and error handling.；Function B has complex control flow with loops and conditionals; function A is a simple linear sequence.；Function B operates on multiple files and directories; function A copies a single file.
- 修正建议: Incorporate data flow analysis to detect similar I/O patterns even in different contexts.；Use subgraph matching on ASTs to identify common code fragments like buffer-copy loops.

### case_id=6260 FN partial_functionality

- 方法: `testNetworkHTTP` vs `load`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A test method that performs multiple hardcoded HTTP GET requests and reads response lines without processing them.
- B 摘要: A utility method that performs an HTTP GET request to pastebin using a given ID and returns the accumulated response as a string.
- 静态失败原因: Static BERT models like CodeBERT rely heavily on lexical and structural surface forms. Here, token overlap is low (0.236), method names differ, return types differ, and the control flow patterns (multiple loops in A vs single loop in B) differ, leading the model to classify them as non-clones.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'HTTP download' or 'network fetch' operations, a common clone class where the core behavior (HTTP GET and reading response) is similar despite differences in number of requests and return type. The annotation guidelines often prioritize functional overlap over strict equivalence.
- 共享行为: Both open a URLConnection for HTTP GET；Both read lines from an InputStreamReader using BufferedReader
- 行为差异: A performs multiple requests to hardcoded URLs; B performs one request with a parameterized ID；A does not return any value; B returns the concatenated response；A uses HttpURLConnection explicitly; B uses URLConnection and openStream()；A has a finally block to disconnect; B does not disconnect
- 修正建议: Improve model sensitivity to common programming idioms like HTTP request patterns even with varying parameters and return types；Use dataflow or graph-based representations to capture the core I/O operations；Include more training examples of Type-4 clones with different return types

### case_id=6261 FN partial_functionality

- 方法: `invoke` vs `handledRun`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Generic HTTP RPC method that sends a POST request with JSON payload, reads response, and returns deserialized object, with retry logic for connection timeout.
- B 摘要: Specific method to download an XML file from a fixed URL, compare version, and update local game data file, with error handling.
- 静态失败原因: The static model relied on token overlap which is low (0.159), and the code structures differ significantly. It might not capture the high-level semantic similarity of 'HTTP-based data retrieval with error handling' due to different libraries and control flow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as Type-4 clones because both involve downloading data over HTTP and processing it, despite different specific purposes and implementations.
- 共享行为: Both perform HTTP network requests and read data from an input stream.；Both use BufferedReader and handle exceptions.；Both have conditional logic based on data read.
- 行为差异: A uses POST and deserializes JSON; B uses GET and writes to file.；A is generic and retries on timeout; B is specific and handles UnknownHostException.；A returns an object; B returns void.；A integrates with a service discovery mechanism; B does not.
- 修正建议: Use data flow analysis to identify similar I/O patterns.；Incorporate high-level semantic representations such as API call sequences.；Train on semantically similar pairs with low token overlap.

### case_id=6262 FN partial_functionality

- 方法: `saveProject` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Saves the current 3D visualization project to a zip file, including XML representations of layers and objects.
- B 摘要: Launches a NexOpen framework project by configuring Maven POM files and running a build action.
- 静态失败原因: Static BERT models rely heavily on token overlap and local syntactic patterns; the low Jaccard similarity (0.066) caused them to miss any deeper semantic similarity that annotators perceived.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as Type-4 clones because both functions are part of a 'project management' metaphor, involving file manipulation and XML processing, despite different specific tasks.
- 共享行为: Both perform file I/O operations.；Both handle XML content.；Both are operations on a project structure.
- 行为差异: Different intended purpose: save vs launch.；Different input/output structures and parameters.；Different domain-specific logic and libraries used.
- 修正建议: Use a model that captures higher-level semantic roles, such as code summarization or contrastive learning.；Incorporate structural information like control flow or data flow.

### case_id=6263 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `handler`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a Twitter user timeline JSON from a hardcoded URL and returns the response body as a string.
- B 摘要: Reads a URL from a TargetPage object, parses lines for specific substrings, and updates a map with extracted values.
- 静态失败原因: The model likely over-focused on common API calls (URL, BufferedReader, readLine) and similar control flow (try-catch, while loop), ignoring the distinct data processing logic and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the functions have different purposes and output types; the shared reading pattern is only boilerplate, and the core logic differs significantly.
- 共享行为: Both open a URL and read its content line by line using a BufferedReader.
- 行为差异: Function A downloads and returns the entire content as a string; function B modifies a map based on parsing each line for substring patterns.；Function A uses Apache HttpClient; function B uses URL.openStream().；Function A has error logging; function B has empty catch blocks.；Function A is private; function B is public.
- 修正建议: Incorporate dataflow or program dependence information to distinguish between reading data and processing it.；Use more fine-grained representations that capture the overall purpose and output type.

### case_id=6264 FP lexical_or_api_overlap

- 方法: `getUser` vs `postXml`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Gets a user by login from DAO or config file, returns User or null.
- B 摘要: Posts XML to a URL using HTTP, returns response as string.
- 静态失败原因: Static BERT overemphasized lexical overlap of common Java I/O and network API calls (BufferedReader, InputStreamReader, URL) and similar exception handling patterns, ignoring the distinct semantic contexts and high-level operations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because functionalities are entirely different: user lookup vs. HTTP client, with no shared purpose or output.
- 共享行为: Both use BufferedReader and InputStreamReader for I/O.；Both handle exceptions with try-catch blocks.；Both involve string operations.
- 行为差异: A reads from a local config file; B sends an HTTP POST request.；A returns a User object; B returns a String.；A performs DAO save; B sets HTTP headers.；A parses colon-separated tokens; B writes XML to output stream.
- 修正建议: Incorporate data-flow analysis to differentiate local file reading from network communication.；Include method signature and return type context to separate User retrieval from HTTP response.；Use structure-based features like control-flow graphs to capture unique behavior (e.g., DAO interaction vs. HTTP header setting).

### case_id=6265 FP boilerplate_overlap

- 方法: `getTicketsForQueue` vs `retrieveTemplate`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves open tickets for a given queue from a Request Tracker system via HTTP GET, parsing ticket IDs and fetching each ticket.
- B 摘要: Retrieves a blog template as a string from a URL, caching it after the first fetch.
- 静态失败原因: Static BERT/GraphCodeBERT may have overemphasized the structural similarity of HTTP client code patterns (HttpGet, BufferedReader) and missed the high-level semantic differences in purpose, return type, and logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered the overall functionality and domain completely different (ticketing system vs blog template retrieval), leading to a non-clone label despite some shared boilerplate.
- 共享行为: Both perform an HTTP GET request to a remote server.；Both read the response using BufferedReader and InputStreamReader.；Both handle I/O and potentially throw exceptions.
- 行为差异: Different return types: List<RTTicket> vs String.；Different purpose: fetching ticket data vs fetching blog template.；Function A parses response to extract ticket IDs and then retrieves each ticket; B simply concatenates all lines.；Function A does not cache; B caches the template.
- 修正建议: Incorporate task-level or domain-specific information to distinguish different applications.；Use data flow analysis to capture the different data transformations and final outputs.；Train on more diverse examples to reduce sensitivity to common boilerplate patterns.

### case_id=6266 FN benchmark_preference_bias

- 方法: `getFile` vs `tail`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file, modifies the soap:address location endpoint, and saves to a temporary file, returning the file path.
- B 摘要: Implements the tail command for HDFS files, printing the last 1024 bytes or following with -f option.
- 静态失败原因: Static BERT likely correctly predicted non-clone due to low token overlap (0.1058) and very different API usage and context, but the benchmark counts it as false negative against the BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label may be due to both methods involving file I/O and error handling, considered as broad Type-4 similarity in file utility functions.
- 共享行为: Both perform file I/O operations using Java streams.；Both handle exceptions such as IOException.
- 行为差异: A downloads from a URL and modifies XML; B reads from HDFS and outputs to stdout.；A writes to a file; B prints to console.；A processes XML nodes; B implements tail -f with sleep.；A deals with web service WSDL; B deals with Hadoop file system.
- 修正建议: Re-evaluate the BCB annotation for this pair; it may be a labeling error.；Use functional similarity criteria that better distinguish distinct domain operations.

### case_id=6267 FN benchmark_preference_bias

- 方法: `createSettingsIfNecessary` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Creates a settings file from a bundled resource if it doesn't exist, with proper stream handling.
- B 摘要: Builds a website for editing by processing pages, performing XML transformations, and writing output files.
- 静态失败原因: The static model correctly predicted non-clone due to very low token overlap (0.066) and no semantic similarity. The BCB label appears to be an anomaly; the model did not fail in this case.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label may have been based on very broad functional similarity (both involve file I/O and 'settings' conceptually), but the actual semantics differ completely. This is likely a mislabel.
- 共享行为: Both read from and write to files；Both close resources in finally blocks；Both involve I/O operations
- 行为差异: Function A simply checks and creates one settings file; Function B processes multiple pages with complex transformations；Function A uses a fixed bundled resource; Function B takes many parameters and reads various external files；Function B contains loops, DOM operations, and XSLT transformations; Function A does not；Function A is about 20 lines; Function B is over 100 lines with nested logic
- 修正建议: Re-evaluate BCB annotations for this pair; likely should be non-clone；Improve benchmark to require stricter functional similarity threshold

### case_id=6268 FP boilerplate_overlap

- 方法: `getDatasetsList` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Returns a cached list of dataset names from a server URL by reading lines.
- B 摘要: Reads tab-separated data from a URL and populates a vector with ID-description pairs.
- 静态失败原因: Overlap in boilerplate code (URL creation, stream opening, finally block) and common API calls masked the distinct processing logic, leading the model to incorrectly judge them as clones.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because despite both reading from URLs, their purpose and output differ significantly; one is a list retriever with caching, the other a parser for tab-separated data.
- 共享行为: Open URL connections；Read text line by line；Handle IO exceptions；Close resources in finally block
- 行为差异: Caching vs no caching；Return list vs populate external vector；Direct line reading vs tab parsing；Different error handling (throw vs print)
- 修正建议: Train with more diverse examples to reduce boilerplate bias；Incorporate dataflow or output-type differences；Use contrastive learning to emphasize semantic differences

### case_id=6269 FN dataflow_blindspot

- 方法: `addIDs` vs `sendRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `dynamic_equivalence_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Enriches a metabolite row by querying a web service for a given name and extracting IDs and molecular weight from HTML.
- B 摘要: Sends an XML request to a library servlet, receives a compressed XML response, parses it into a JDOM document, and returns an empty string.
- 静态失败原因: Low token Jaccard (0.077) and different method signatures caused the model to miss the high-level functional similarity of network I/O and parsing patterns.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本可能是 API 写法不同但行为等价的漏报。建议测试目标为 input_output_equivalence。
- BCB 偏好解释: BCB may consider both as 'web service query and response parsing' methods under a broad Type-4 (functionally similar) definition, despite low lexical overlap.
- 共享行为: Both perform HTTP requests to a web service；Both read and parse the response；Both handle exceptions during network I/O；Both use URL and URLConnection classes
- 行为差异: A reads HTML line by line, B uses SAXBuilder to parse XML；A sets multiple fields on a row object, B does not use the parsed data；A returns an integer score, B returns an empty string；A is private, B is public
- 修正建议: Incorporate data flow analysis to detect common patterns like 'open connection, read, parse', ；Use contrastive learning with functional similarity labels；Enhance token embeddings with domain-specific knowledge

### case_id=6270 FN partial_functionality

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a hardcoded URL and extracts its zip entries to files.
- B 摘要: Copies a file from source to destination using NIO channels.
- 静态失败原因: Static BERT methods rely heavily on token overlap and syntactic similarity; with a token Jaccard of 0.118 and distinct APIs (ZipInputStream, URL vs. FileChannel, transferFrom), the model sees little surface-level commonality and fails to recognize the underlying shared I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may regard both as instances of 'file copying' functionality under a broad Type-4 semantic category, as both transfer bytes from an input source to an output destination, despite differences in APIs and source types.
- 共享行为: Both involve reading data from an input source and writing it to output files.；Both handle I/O exceptions and close resources.
- 行为差异: A downloads and unzips a remote file; B copies a local file.；A uses stream-based I/O (ZipInputStream, FileOutputStream); B uses NIO channels (FileChannel).；A extracts multiple entries; B copies a single file.；A does not specify destination file path (uses entry name); B uses provided destFile.
- 修正建议: Enhance model with program flow analysis (e.g., data flow graphs) to capture read-write patterns.；Include tokenization that abstracts specific API calls to generic I/O operations.；Use data augmentation to learn that different I/O mechanisms can be semantically equivalent.

### case_id=6271 FN partial_functionality

- 方法: `copyFile` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Handles HTTP GET request to render a page, including authentication, caching, and error handling.
- 静态失败原因: The static model correctly identified the large semantic and structural differences, as evidenced by very low token Jaccard similarity (0.04), and thus predicted non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to both having file writing operations and IOException, accepting broad Type-4 partial functionality similarity.
- 共享行为: Both involve file I/O operations；Both throw IOException
- 行为差异: copyFile is a simple utility with no control flow；doGet has complex control flow for page rendering, user permissions, and caching；copyFile uses NIO channels, doGet uses traditional FileWriter
- 修正建议: Improve benchmark annotations to avoid labeling diverse functions as clones；Use finer-grained clone types to distinguish partial from full semantic clones

### case_id=6272 FP lexical_or_api_overlap

- 方法: `CopyFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file from source to destination, creating parent directories if necessary, using file channels.
- B 摘要: Handles GUI action events to set configuration preferences for external tool paths and UI settings.
- 静态失败原因: The static model likely overfit to lexical matches such as 'File', 'IOException', or exception-related keywords, and missed the high-level semantic difference due to limited context and lack of dataflow understanding.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label these as non-clones because they perform fundamentally different tasks with distinct control flows and purposes, despite some lexical overlap like 'File' and exception handling.
- 共享行为: Both involve file-related operations but at different abstraction levels: one copies file content, the other selects file paths.
- 行为差异: One performs actual file I/O copying; the other sets GUI configuration and updates UI.；One returns the destination file path; the other updates internal state and UI components.；One is a static utility method; the other is an event handler with no return value.
- 修正建议: Incorporate structural information like control flow and data dependencies.；Use methods that detect functional purpose beyond token overlap, such as graph-based models.

### case_id=6273 FN benchmark_preference_bias

- 方法: `testCopy_readerToWriter_nullIn` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Tests that IOUtils.copy throws NullPointerException when given a null Reader.
- B 摘要: Retrieves a resource as an InputStream with caching and network handling.
- 静态失败原因: Static model correctly predicted non-clone; the error is a benchmark mislabel.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to both being related to I/O operations, but the functions are semantically unrelated.
- 共享行为: Both involve I/O streams but in completely different contexts.
- 行为差异: Function A is a test method that expects an exception; Function B performs actual resource retrieval.；Function A has no real data processing; Function B has complex caching and network logic.；Function A uses Writer and OutputStream; Function B uses InputStream and file handling.
- 修正建议: Reevaluate BCB annotation for this pair.；Improve benchmark quality by removing such false positive clones.

### case_id=6274 FN partial_functionality

- 方法: `readGeoParserResult` vs `postXml`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an XML request to a geo-parsing service, retries on failure, parses the response into structured tuples.
- B 摘要: Posts an XML string to a URL using HTTP, reads the response, and returns it as a string.
- 静态失败原因: The low token Jaccard (0.12) and significant structural differences (e.g., retry loop, XML construction vs. parameter) led the model to predict non-clone. Models like GraphCodeBERT may overemphasize surface-level similarity and fail to recognize the common abstract pattern of HTTP XML communication.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers these as Type-3/Type-4 clones because the core operation of sending XML over HTTP and reading the response is semantically similar, despite differences in API specifics, error handling, and output processing. The shared abstract pattern outweighs the syntactic variations.
- 共享行为: Both open an HTTP connection and send XML data to a remote server.；Both read the HTTP response line by line using BufferedReader.；Both use StringBuilder to accumulate the response.
- 行为差异: A constructs the XML request internally; B receives it as a parameter.；A has retry logic (up to 3 attempts); B throws RuntimeException on any IOException.；A parses the response XML into a Collection of Tuples; B returns the raw response string.；A handles a specific geo-parsing protocol; B is a generic HTTP client.
- 修正建议: Train with more positive examples of partial-functionality clones.；Incorporate API-call sequence features or abstract syntax tree paths to capture similar patterns.；Use contrastive learning that rewards functional similarity even with low token overlap.

### case_id=6275 FN benchmark_preference_bias

- 方法: `doTransfer` vs `sendRequestObjectResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Forwards an incoming HTTP request to a specified URL and relays the response back to the original client.
- B 摘要: Sends a request string to a server determined by user input or preferences, saves the response to a file, and opens the file in a browser.
- 静态失败原因: The model likely relied on low token overlap (0.18) and different method names/parameters, missing the high-level HTTP communication pattern that BCB considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone because both functions involve making an HTTP request, writing, reading, and using similar stream handling patterns. However, the overall functionality and context are significantly different.
- 共享行为: Both open an HTTP URL connection and set request properties.；Both write data to the output stream of the connection.；Both read data from the input stream of the connection.；Both handle I/O exceptions with printStackTrace.
- 行为差异: Function A acts as a servlet proxy, forwarding headers and body from an incoming request; Function B constructs its own URL and sends a fixed request string.；Function A writes the response back to the original HTTP response; Function B saves the response to a local file and returns the filename.；Function B includes user interaction (dialog for IP/port) and preferences handling; Function A has no UI.；Function B compresses the request with GZIP; Function A does not.
- 修正建议: Improve model to recognize high-level architectural patterns beyond token overlap.；Incorporate structural or dataflow information to capture common sequences of operations.；Use transfer learning on broader clone detection benchmarks with diverse annotations.

### case_id=6276 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `getURLContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a resource file line by line, parses each line as an integer, and returns a set of integers.
- B 摘要: Opens a URL connection, reads the content line by line, concatenates lines with newlines, and returns the entire content as a string.
- 静态失败原因: The model likely over-emphasized the lexical overlap of API calls (e.g., URL, openStream, readLine) and the loop structure, while ignoring the distinct semantics of parsing integers vs building a string.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels clones only if functions have similar functionality or share significant behavioral overlap, which is not the case here due to differing output types and processing logic.
- 共享行为: Both open a URL-like resource and read lines in a loop until null.；Both use similar I/O classes (URL, InputStream, Reader, readLine).
- 行为差异: Different return types (HashSet<Integer> vs String).；Different input processing (parsing integers vs appending lines).；Different error handling (catch and print stack trace vs throws IOException with finally block).；Different input types (resource path vs URL string).
- 修正建议: Incorporate return type and output semantics in the embedding.；Use dataflow or dependency analysis to distinguish parsing from gathering raw content.；Augment training with pairs that share API calls but have different high-level goals.

### case_id=6277 FP boilerplate_overlap

- 方法: `read` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a camera log from a URL, parses each line into CameraLogRecord objects, sorts them, and logs progress.
- B 摘要: Queries a ticket tracking system for open tickets in a given queue, retrieves each ticket by ID, and returns a list of RTTicket objects.
- 静态失败原因: The static BERT/GraphCodeBERT model likely focused on the common boilerplate pattern of reading lines with BufferedReader in a try-catch-finally block, along with logging statements. This superficial structural similarity, combined with token overlap from common Java idioms, caused a false positive. The model failed to capture the entirely different application logic and domain-specific operations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as a non-clone because the functions serve completely different purposes (camera log parsing vs ticket querying) despite sharing a superficial reading-loop structure. The overall functionality, domain, and output are distinct, falling outside Type-4 similarity.
- 共享行为: Both use BufferedReader to read lines of text from a remote source.；Both handle exceptions and log errors or warnings.；Both loop through lines until null.；Both use try-catch-finally to ensure stream closure.
- 行为差异: Function A reads a log file; Function B queries a REST API for tickets.；Function A parses each line into a domain object (CameraLogRecord); Function B parses lines to extract ticket IDs then fetches additional data.；Function A sorts the collected records; Function B does not sort the final ticket list.；Different return types: void vs List<RTTicket>.
- 修正建议: Improve attention to method signatures, return types, and distinct API calls.；Incorporate dataflow analysis to differentiate between reading a local log vs. making HTTP requests with query parameters.；Use contrastive learning to distance functions with similar patterns but different core tasks.；Filter or downweight common boilerplate code during training.

### case_id=6278 FP boilerplate_overlap

- 方法: `scrapeForIsbns` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Scrapes ISBN-10 patterns from a URL by reading lines with regex, counts matches, and stores them in a map with retry logic on connection failures.
- B 摘要: Reads tab-delimited data from a URL using Scanner, extracts ID and description fields, and adds concatenated strings to a vector.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on lexical overlap such as common API calls (url.openStream, InputStream, try-catch) and similar variable names, while missing the fundamental differences in parsing strategy and output. The boilerplate of URL stream reading dominated the representation, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have different return types, different parsing logic, and distinct output behavior. The low token Jaccard (0.147) and contrasting method signatures ('int' vs 'void') indicate BCB would favor non-clone despite shared I/O boilerplate.
- 共享行为: Both open a URL stream and read line-by-line or token-by-token from an InputStream.；Both handle exceptions (IOException, etc.) and include logging or printing stack traces.；Both process incoming text data and store extracted information.
- 行为差异: Function A uses regex to match ISBN patterns; function B uses Scanner with delimiter to parse tab-separated fields.；Function A returns an integer count of matches; function B is void and populates a Vector externally.；Function A includes retry logic on ConnectException; function B does not.；Function A uses BufferedReader and manual line reading; function B uses Scanner with delimiter.
- 修正建议: Incorporate structural features like control flow graphs and data flow analysis to differentiate parsing logic.；Weight method signature (return type, parameters) more heavily in similarity computation.；Use contrastive learning with examples that have high boilerplate overlap but different core semantics.

### case_id=6279 FP lexical_or_api_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses command-line options, reads a Prolog file, generates adapters from it, and writes output as a JAR.
- B 摘要: Utility method that copies a file from one location to another using NIO FileChannels.
- 静态失败原因: The static BERT/GraphCodeBERT model probably overfitted on overlapping tokens like 'File', 'IOException', 'return', 'catch', and common structural patterns (try-catch, file channel usage), leading to a false positive due to lexical or API overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functionalities are completely different despite sharing some I/O boilerplate; BCB requires semantic similarity in purpose or behavior, which is absent here.
- 共享行为: Both involve file input/output operations.；Both handle exceptions with try-catch blocks.；Both are static methods.
- 行为差异: Function A performs complex code generation and JAR creation from Prolog parsing; Function B simply copies bytes from one file to another.；Function A has many external dependencies and specific domain logic; Function B is generic and independent.；Function A has ~70 lines of involved logic; Function B is ~10 lines of straightforward I/O.
- 修正建议: Incorporate data-flow analysis to distinguish between different file operation purposes.；Use finer-grained structural features like control-flow graphs or abstract syntax trees to capture logic differences.；Add attention to method-level semantics beyond token co-occurrence.

### case_id=6280 FP boilerplate_overlap

- 方法: `sendPost` vs `loadExistingAntlibs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Loads Ant library definitions from classpath resources by reading resource files and resolving URIs.
- 静态失败原因: The model was misled by the structural similarity of reading lines from a URL using common I/O boilerplate (BufferedReader, InputStreamReader, while loop) and similar token sequences, ignoring the distinct purposes (HTTP POST vs. Ant library loading).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions implement entirely different high-level functionalities despite sharing low-level I/O boilerplate.
- 共享行为: Both open a URL resource and read lines using BufferedReader with InputStreamReader；Both use try-catch for exception handling；Both close streams and readers after use
- 行为差异: sendPost sends data via PrintWriter, loadExistingAntlibs does not send data；sendPost returns concatenated response string, loadExistingAntlibs calls loadAntLib for each line；sendPost handles generic Exception, loadExistingAntlibs handles IOException and URISyntaxException differently；sendPost sets HTTP request properties, loadExistingAntlibs resolves URIs to URLs
- 修正建议: Incorporate data flow analysis to capture how input variables are used (param vs. pkg).；Train on pairs with shared boilerplate but divergent semantics to learn discriminative features.；Use method-level contrastive learning that rewards distinguishing based on core operation rather than peripheral I/O patterns.

### case_id=6281 FN benchmark_preference_bias

- 方法: `login` vs `startScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Logs into LOLA by sending credentials via HTTP POST and returns a session ID.
- B 摘要: Loads a script from a given URL and appends its content to a dialog.
- 静态失败原因: Static BERT models rely on lexical and structural similarity; the low Jaccard similarity and different control flow led it to correctly identify non-clone, but it missed the broad semantic interpretation desired by BCB.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may view both as sending HTTP requests to fetch remote resources, thus considering them Type-4 semantic clones despite different purposes.
- 共享行为: Both open a URL and read lines from its input stream using BufferedReader.；Both use try-catch for exception handling.
- 行为差异: The login method sends POST data (email, password) before reading; startScript does not send data.；login parses the response to extract a session ID, while startScript appends raw lines to a string.；login returns the session ID; startScript is void.；login catches general Exception; startScript catches IOException and calls System.exit.
- 修正建议: Re-evaluate BCB annotation: pair may be mislabeled.；Train models with better semantic understanding to distinguish different intents despite similar I/O patterns.

### case_id=6282 FN partial_functionality

- 方法: `unJar` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Extracts a single file from a JAR archive to a specified directory on the filesystem.
- B 摘要: Performs a complex launch process for a Maven-based project, including configuration handling, code generation, and file copy operations.
- 静态失败原因: Static BERT models rely heavily on token overlap and local semantics; the low Jaccard similarity (0.045) and long, structurally dissimilar code likely confused the model. The shared IOUtils.copy pattern was not enough to overcome the dominant differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones due to the shared use of IOUtils.copy and the concept of copying a resource from an input stream to a file, which could be considered a partial functional overlap (Type-4) despite different contexts.
- 共享行为: Both involve file I/O operations, specifically copying files from an input stream to an output stream.；Both use the IOUtils.copy method from Apache Commons IO.
- 行为差异: Function A is a simple extraction of a single JAR entry to a file; function B is a multi-step project launch and installation.；Function A returns a file path; function B has a void return and modifies project state.；Function B includes XML parsing, property handling, and persistent property setting, which are absent in A.；The overall purpose and complexity are vastly different.
- 修正建议: Incorporate dataflow analysis to capture the abstract behavior of copying files.；Use graph-based models (like CodeBERT with AST) to better understand the structural operations.；Train on broader clone types that handle partial functional similarity.

### case_id=6283 FN partial_functionality

- 方法: `copyFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from one location to another using FileChannel.
- B 摘要: Downloads a KMZ file from a URL, decompresses it, and writes the entries to files.
- 静态失败原因: Static models like BERT focus on low token overlap and structural similarity; these methods have different names, signatures, and control flow, leading to a low similarity score despite sharing the high-level concept of file copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones because both are file I/O operations that copy data from an input source to an output destination, considered Type-4 (semantic) similarity.
- 共享行为: Both read from a source (file or URL) and write to a destination file using streams/channels.
- 行为差异: A uses FileChannel for efficient file copy; B uses URLConnection and ZipInputStream for downloading and decompressing a zip archive.；A is a simple single-file copy; B is a multi-file extraction from a compressed archive.；A has no loops; B contains loops to iterate over zip entries and read/write data.
- 修正建议: Train models to recognize semantic roles (source, destination) rather than exact API calls.；Use program analysis to extract data flow and I/O operations.；Incorporate code summarization to capture high-level intent.

### case_id=6284 FN boilerplate_overlap

- 方法: `readGeoParserResult` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a geo parser result by sending an XML request to a geo-parsing service and extracting place names and gazetteer IDs from the response.
- B 摘要: Checks for jEdit version updates by reading a version file from a URL and extracting development and stable build numbers.
- 静态失败原因: Static BERT models often rely on token-level representations and may have been misled by the low token overlap (Jaccard 0.127) and very different domain-specific terms, failing to recognize the common high-level pattern of URL reading and line parsing.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled these as clones based on the shared pattern of reading a remote file over HTTP and parsing line by line, considering it as a common I/O boilerplate pattern that constitutes a functional similarity (Type-4).
- 共享行为: Both open a URL and read lines using InputStream and BufferedReader.；Both use a while loop to read lines until null.；Both perform line-based parsing of the response.
- 行为差异: A builds and sends an XML request; B only reads from a static URL.；A extracts and returns a collection of tuples; B extracts two build version strings and delegates to another method.；A has retry logic and dummy return for testing; B has cursor management and error dialog.；The overall purpose and data structures are completely different.
- 修正建议: Improve model's ability to recognize common I/O patterns across different domains.；Use graph-aware models to capture control flow and data dependencies rather than just lexical tokens.；Incorporate functional category information to disambiguate boilerplate from core functionality.

### case_id=6285 FN benchmark_preference_bias

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using NIO FileChannel transferFrom.
- B 摘要: Launches a NexOpen project configuration, involving reading XML files, copying resources, and scheduling build actions.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on lexical token overlap and code structure. The token Jaccard is very low (0.038), and the control flow, API usage, and domain context are completely different, leading the model to correctly identify them as non-clones.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone based on partial functionality similarity: both perform file copying operations (A copies a file directly; B copies a resource file in one part). However, the overall functionality is vastly different, and this label is likely erroneous or reflects an overly broad notion of clone.
- 共享行为: Both involve file I/O operations (reading and writing files).
- 行为差异: Function A is a simple file copy; Function B orchestrates a complex project build.；Function A uses FileChannel; Function B uses streams, Document parsing, and project resources.；Function A has no branching or exception handling beyond IOException; Function B has multiple condition checks and exception handling.；Function B performs configuration management, XML processing, and persistent property setting; A does not.
- 修正建议: Review and potentially correct BCB annotations for this pair.；Use more precise semantic analysis that considers high-level intent rather than just lexical/syntactic similarity.；Train models with better understanding of domain-specific functionality to avoid over-generalization.

### case_id=6286 FP lexical_or_api_overlap

- 方法: `importSequences` vs `postRequest`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Imports sequences from a URL by reading a file format with '>' delimiters.
- B 摘要: Sends an HTTP POST request with form data and returns the response.
- 静态失败原因: Static BERT models may rely on lexical and API overlap (e.g., URL, openStream/connection, BufferedReader, IOException) without understanding the distinct high-level semantics, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically annotates clones based on similar functionality; these functions have different purposes (importing sequences vs. HTTP request), so BCB labels non-clone.
- 行为差异: Function A reads a file format with '>' delimiters; B sends HTTP POST；A uses ImportHelper and StringTokenizer; B uses PrintWriter and BufferedReader；A extracts sequence names and data; B encodes and sends form parameters；A writes to internal lists; B returns a string
- 修正建议: Incorporate task labels or data flow analysis to distinguish I/O patterns；Use examples with similar API usage but different semantics to train model；Consider adding structure-aware features to differentiate reading vs. writing data

### case_id=6287 FP other

- 方法: `readData` vs `transferWSDL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses comma-separated string constants to initialize sets and maps for Tibetan transliteration processing.
- B 摘要: Downloads a WSDL XML file from a URL via HTTP GET, optionally with basic authentication, and saves it to a temporary file, returning its path.
- 静态失败原因: Static BERT models might be misled by the presence of common Java API patterns (e.g., HashSet, StringTokenizer, while loops) in function A and similar patterns (e.g., HttpURLConnection, File) in function B, but the overall semantics are completely different. Also, the truncated long code of A might cause the model to focus on local features rather than global intent.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotates strictly based on functional equivalence; these functions have no overlap in purpose or behavior, so labeled non-clone.
- 行为差异: Function A processes internal string constants into data structures; Function B fetches external resource over network.；Function A is void with side effects on static collections; Function B returns a file path and throws exceptions.
- 修正建议: Improve training data with more negative pairs that have low lexical overlap but different semantics.；Incorporate control flow and data flow analysis to distinguish initialization from I/O operations.

### case_id=6288 FP lexical_or_api_overlap

- 方法: `importSequences` vs `sendRequestObjectResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads sequences from a URL stream in FASTA-like format and stores them.
- B 摘要: Sends an HTTP request to a servlet, receives response, saves it to a file based on content type, and displays the file.
- 静态失败原因: Static models may over-rely on token-level overlap (e.g., URL, InputStream, try-catch) and miss the distinct control flow and API usage patterns that indicate different semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels 0 because these functions perform completely different tasks; any overlap is superficial and not indicative of cloned functionality.
- 共享行为: Both use java.net.URL and java.io.InputStream；Both have try-catch blocks for exceptions；Both involve reading from a network resource
- 行为差异: A parses sequence data format; B sends HTTP request and saves file；A returns void; B returns Object (filename string)；A uses ImportHelper; B uses many more classes (GZIPOutputStream, Preferences, etc.)
- 修正建议: Include structural similarity measures beyond token overlap；Incorporate control flow graph comparison；Filter out generic exception handling boilerplate

### case_id=6289 FP lexical_or_api_overlap

- 方法: `readData` vs `writeData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: readData initializes multiple sets from static string constants and parses a file to populate maps and sets with configuration data.
- B 摘要: writeData writes a tab-separated file with headers and rows of time-stamped peak data, then reads the file back for verification.
- 静态失败原因: The static BERT model likely overestimated similarity due to overlapping API tokens (e.g., StringTokenizer, PrintWriter, Scanner) and common programming constructs (loops, try-catch), despite the low token Jaccard, possibly misled by the presence of similar boilerplate code for I/O.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the functions have distinct high-level purposes (loading vs. saving) and share minimal structural similarity beyond generic I/O patterns.
- 共享行为: Both perform file I/O operations (readA reads, writeB writes)；Both use loops and conditionals to process data；Both involve string tokenization or formatting
- 行为差异: readA reads input from static strings and a file to populate in-memory data structures; writeB writes formatted output to a file and then reads it back；The data structures and logic are entirely different: A populates HashSets and maps, B outputs tabular data with peak values；The control flow and error handling differ (A catches IOException, B catches Exception)
- 修正建议: Incorporate finer-grained structural matching (e.g., AST or data-flow analysis) to distinguish reading vs. writing behaviors；Utilize method signatures (return type, parameter list) as additional features；Add attention to high-level semantics via documentation or function name embeddings

### case_id=6290 FN lexical_or_api_overlap

- 方法: `login` vs `addQDInformation`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs in to a service by POSTing credentials and extracting a session ID from the response.
- B 摘要: Reads a local or remote data file and parses lines to update project information records.
- 静态失败原因: The static model correctly identified them as non-clones (prediction=0), so it did not fail on this pair; the error is a false negative from BCB's perspective.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones due to superficial API-level similarity (URL handling, BufferedReader) and both being part of a larger system, but the functional intent is entirely different.
- 共享行为: Both use URL to open connections or streams；Both use BufferedReader to read text line by line；Both handle IOException and other exceptions
- 行为差异: A performs HTTP POST with form data; B performs HTTP GET or local file reading；A extracts a session ID from a single line; B parses multiple lines with specific prefixes (pg, pt)；A writes to the output stream; B only reads and updates internal data structures；A returns a session ID; B returns void and modifies object state
- 修正建议: Improve semantic understanding beyond API sequence similarity；Incorporate data-flow and control-flow analysis to differentiate actual operations；Use more fine-grained functional role detection (e.g., login vs. config parsing)

### case_id=6291 FP lexical_or_api_overlap

- 方法: `readData` vs `copyFileByNIO`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads and parses configuration data (likely Tibetan text mappings) from a file into various sets and maps.
- B 摘要: Copies a file from source to destination using NIO channels.
- 静态失败原因: The static model (e.g., GraphCodeBERT) might have been misled by the common presence of file I/O APIs (FileInputStream, FileChannel, IOException) and possibly the similar exception handling patterns. Despite low token Jaccard, the model might have focused on these overlapping keywords and the overall structure of a function that opens files, reads, and closes. It failed to recognize the vast difference in purpose and logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because the tasks are entirely different: one is data loading/parsing, the other is file copying. They share no meaningful functional similarity beyond basic I/O.
- 共享行为: Both involve file input/output operations.；Both may handle IOException (A catches, B throws).
- 行为差异: A reads and parses structured data into collections; B copies raw bytes.；A has complex parsing logic with multiple tokenizers and hash maps; B has a straightforward channel transfer.；A writes to multiple internal data structures; B writes to a file output stream.
- 修正建议: Improve model to distinguish between different file operations (e.g., copy vs. parse) by emphasizing functional purpose over low-level API usage.；Incorporate data flow analysis to see that A builds data structures while B transfers bytes.；Use contrastive learning on functions with similar API but different semantics.

### case_id=6292 FN partial_functionality

- 方法: `copyResource` vs `readFixString`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using byte-by-byte reading and writing.
- B 摘要: Reads a fixed-length string from a limited input stream into a StringWriter using IOUtils.copy.
- 静态失败原因: Static BERT models rely on token overlap and structural similarity; low Jaccard (0.107) and different method names, I/O types, and control flow caused it to miss the weak functional similarity that BCB accepts.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'copy' operations from input to output, accepting broad Type-3/Type-4 similarity based on shared I/O data copying functionality despite different output types and APIs.
- 共享行为: Both read from an input source and write to an output sink.；Both handle I/O operations and exceptions.
- 行为差异: A writes to a FileOutputStream; B writes to a StringWriter.；A reads raw bytes; B reads characters.；A uses a manual byte loop; B uses IOUtils.copy library call.；A has no input length limit; B limits to len.
- 修正建议: Use a model that captures I/O and stream semantics more broadly.；Incorporate dataflow or functional dependency analysis.；Leverage method name and library context for similarity.

### case_id=6293 FN partial_functionality

- 方法: `getDatasetsList` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Synchronized method that fetches a list of dataset names from a server URL, caching results per URL.
- B 摘要: Method that invokes a remote service method via HTTP POST with JSON serialization, including retry and service discovery.
- 静态失败原因: Static BERT models like GraphCodeBERT heavily rely on token-level patterns and structural similarity. The low token Jaccard (0.17) and different method names, return types, and API usage (HttpPost vs URL) likely caused the model to predict non-clone. Additionally, the model may not capture the high-level similarity of 'HTTP read' operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs with similar high-level structure, such as both performing HTTP communication and reading input streams, as Type-4 clones even if the specific semantics differ. The core pattern of opening a connection, reading lines, and error handling is considered functionally similar.
- 共享行为: Both make HTTP requests to a URL；Both use BufferedReader to read lines from an InputStream；Both handle exceptions by throwing RuntimeException；Both close the reader in a finally block or similar cleanup
- 行为差异: Function A uses GET request with a query parameter; Function B uses POST with JSON body；Function A caches results per URL; Function B does not cache but has retry logic；Function A returns a list of strings; Function B returns an object deserialized from JSON；Function B has retry and service discovery; Function A does not
- 修正建议: Improve model's ability to recognize similar control flow patterns (try-catch-finally with stream reading) even with different API calls；Incorporate more high-level semantic features like connection setup and response handling；Use data augmentation with functionally similar pairs that have low lexical overlap

### case_id=6294 FN partial_functionality

- 方法: `doImageProcess` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Serves an image to the HTTP response by reading from a URL or input stream, optionally resizing.
- B 摘要: Retrieves a resource by name, checking a local cache and downloading if necessary, then returns an InputStream.
- 静态失败原因: Low token overlap and structural differences overshadowed the shared URL-reading pattern; the model likely focused on surrounding code (response handling vs. caching) as distinguishing features.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: Annotators may have considered both as 'loading a resource from a URL' at a high level, despite different details and outputs, possibly as a Type-4 partial clone.
- 共享行为: Both open a URL to obtain an InputStream.
- 行为差异: One writes image data to an HTTP response output stream; the other caches to a file and returns an InputStream.；One handles image dimensions; the other handles HTTP conditional caching.；One closes output stream; the other handles multiple stream closures and exceptions.
- 修正建议: Incorporate data-flow information to identify common sub-patterns like opening a URL connection.；Use API-level embeddings to capture similar operations even in different contexts.

### case_id=6295 FN partial_functionality

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel transfer.
- B 摘要: Launches a configuration for a NexOpen project, involving Maven POM handling and Hibernate reverse engineering file creation, with some stream copying.
- 静态失败原因: Static BERT likely relied on low token overlap (0.0688) and context mismatch, leading to zero similarity prediction. It may not capture the hidden high-level similarity of stream copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled as clone because both involve stream copying (file I/O), and BCB may consider that as partial functionality similarity.
- 共享行为: Both perform I/O operations involving file streams, specifically copying data from an input to an output.
- 行为差异: A is a simple file copy with synchronization; B is a complex launch method with many external dependencies and configuration.；A returns a boolean; B returns void and throws CoreException.；A uses FileChannel; B uses IOUtils.copy and ByteArrayOutputStream.
- 修正建议: Improve representation to capture cross-cutting concerns like I/O patterns.；Use dataflow analysis to detect common sub-operations.

### case_id=6296 FN partial_functionality

- 方法: `copyResource` vs `displayDiffResults`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file.
- B 摘要: Generates and displays an HTML diff report from metric tables and binary diff data.
- 静态失败原因: Low token similarity (0.144) and different method names/overall structure dominant; static BERT likely judges based on surface form and ignores the shared byte-copying sub-pattern as insufficient for clone detection.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider any pair with similar low-level I/O patterns as clones, even if high-level intent differs, favoring broad Type-3/Type-4 similarity.
- 共享行为: Both involve reading from an input stream and writing to an output stream；Both use while loops to copy bytes
- 行为差异: Different source and destination types (URL/file vs temporary file/stream)；Different output content (binary copy vs HTML with diff metrics)；displayDiffResults also launches a browser; copyResource does not
- 修正建议: Use more global context or hierarchical representation to distinguish main purpose from sub-patterns；Incorporate functional signature and high-level intent embedding；Treat subfunction clones separately or weight I/O patterns appropriately

### case_id=6297 FP boilerplate_overlap

- 方法: `setMembers` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses HTML from a Trac ticket page to extract component and priority options and store them in member arrays.
- B 摘要: Checks for software upgrades by querying a remote server, parsing the response, updating a local database, and managing UI visibility.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on lexical overlap of common patterns like URL, BufferedReader, try-catch, leading to a false positive prediction despite low token Jaccard.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have distinct functionality, only sharing generic I/O boilerplate.
- 共享行为: Both open a URL connection and read input using BufferedReader.
- 行为差异: Different purposes: one sets trac ticket fields, the other checks upgrades.；Different data extraction: one uses regex for HTML select options, the other splits XML-like tags.；Different outputs: one populates member arrays, the other writes to database and updates UI.
- 修正建议: Enhance model to focus on semantic operations rather than syntactic structures.；Incorporate data flow and control flow analysis to differentiate similar I/O patterns.

### case_id=6298 FN lexical_or_api_overlap

- 方法: `login` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Log in to LOLA by sending POST request with email and password, then extract and return session ID from response.
- B 摘要: Send XML query to a geo parser service, parse response to extract place names and associated IDs, with retry on failure.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on low token overlap (12.5%) and different method names/patterns, leading to a non-clone prediction; it failed to recognize the broad Type-4 pattern that BCB may have accepted.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both clones due to commonality of HTTP communication and response parsing, but the functionality and data processing are fundamentally different; under strict criteria this would not be a clone.
- 共享行为: Both establish HTTP connection；Both read response via BufferedReader；Both use try-catch for exception handling；Both return a value after processing
- 行为差异: Post vs Get with XML in query string；Parse single line for session ID vs parse complex XML for multiple entries；Mutates session state vs pure function returning collection；No retry vs retry up to 3 times
- 修正建议: Improve model's ability to recognize structural patterns beyond token overlap；Incorporate control flow and I/O action similarity；Use models that capture sequence of API calls rather than just tokens

### case_id=6299 FN partial_functionality

- 方法: `runInternal` vs `handledRun`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads and processes an OPDS catalog, handling pagination and book downloads via HTTP.
- B 摘要: Downloads a game data XML file from the web and updates a local database if a newer version exists.
- 静态失败原因: Static BERT models rely on lexical and syntactic overlap, but the token Jaccard similarity is very low (0.106) due to different variable names, APIs, and code structure, causing the model to miss the high-level semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels these as clones because both functions perform a common pattern: 'download a resource via HTTP and process it locally', which is considered a Type-4 (semantic) clone despite domain-specific differences.
- 共享行为: Both establish an HTTP connection to download data from a URL.；Both read from an input stream and handle I/O exceptions.；Both involve writing data to a file or storage as part of processing.
- 行为差异: Function A processes an OPDS catalog with multiple entries and pagination, while Function B downloads a single XML file.；Function A uses a callback for asynchronous completion; Function B is synchronous and updates a database directly.；Function A handles multiple response types (catalog vs. book download); Function B has version check logic.；Error handling differs: Function A shows progress and uses specific error callbacks; Function B shows a dialog and rethrows exceptions.
- 修正建议: Incorporate abstract syntax tree (AST) or control flow graph (CFG) features to capture structural patterns.；Use models trained on cross-project clone detection with a focus on I/O and networking patterns.；Augment training data with more examples of 'download-and-process' clones from diverse domains.

### case_id=6300 FN partial_functionality

- 方法: `getPagina` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches a URL and returns its content as a string, handling exceptions and returning error messages.
- B 摘要: Fetches a hardcoded URL and logs its content, throwing exceptions upwards.
- 静态失败原因: Static BERT/GraphCodeBERT methods often rely on surface-level features like token overlap and control flow structure. The low token Jaccard (0.29) and differences in method signatures, exception handling, and library usage (Authenticator) likely caused the model to miss the shared I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers these as Type-4 clones because the core semantic of fetching and reading URL content is identical, despite differences in error handling, return type, and logging. The annotation guidelines for BigCloneBench accept partial functionality similarity.
- 共享行为: Opens a URL connection；Reads the input stream line by line；Concatenates lines into a single string
- 行为差异: A sets an authenticator, B does not；A returns the result string, B logs it and throws Exception；A catches specific exceptions and returns them, B propagates exceptions；A uses String concatenation in a loop, B uses StringBuffer
- 修正建议: Train on more diverse examples of I/O operations and URL fetching；Incorporate dataflow analysis to detect similar read-append patterns；Use graph-based representations that capture I/O operations and string building

### case_id=6301 FN partial_functionality

- 方法: `main` vs `write`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from HTTP, decompresses it, and extracts files to disk using ZipInputStream.
- B 摘要: Wraps ByteBuffer data into SSL/TLS encrypted buffers using SSLEngine, managing handshake state.
- 静态失败原因: Static BERT methods rely heavily on token-level overlap and local structure; the low Jaccard (0.098) and different APIs (ZipInputStream vs SSLEngine) led to a non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered them Type-4 clones based on the high-level concept of 'reading from a source and writing processed data', despite vastly different domains and complexity.
- 共享行为: Both involve reading input data and producing output in chunks (byte arrays/ByteBuffers).
- 行为差异: A is a simple sequential extraction; B involves complex SSL handshake and state management.；A writes to files; B returns ByteBuffer[] (no external I/O).；A uses ZipInputStream; B uses SSLEngine and a delegate writer.；B has branching logic for handshake status and initial buffer management.
- 修正建议: Enhance model with semantic understanding of I/O patterns beyond lexical surface.；Include context-aware pretraining on byte-level operations or abstract data flow.；Use graph-based methods to capture control-flow and data-flow similarities.

### case_id=6302 FP partial_functionality

- 方法: `getWebPage` vs `readScalarpvviewerDocument`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads the entire content of a web page from a URL and returns it as a String.
- B 摘要: Reads a specific XML document from a URL, parses it, and configures a UI viewer with the extracted parameters.
- 静态失败原因: GraphCodeBERT or similar static models may overemphasize the superficial similarity of the I/O loop (URL.openStream, BufferedReader, readLine) and the presence of exception handling, while missing the substantial differences in the rest of the code, especially the long and complex XML parsing and UI configuration in function B.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality is completely different: one is a generic web page retrieval, the other is a domain-specific document parser with UI configuration. They share only a common I/O pattern but diverge significantly in purpose and logic.
- 共享行为: Both open a URL connection and read data line by line using BufferedReader；Both handle IOException with error messages
- 行为差异: Function A returns the raw content as a String; Function B parses XML and updates UI components；Function A reads all lines without filtering; Function B skips comment lines and stops at '%=' marker；Function B performs extensive configuration of fonts, panels, and data structures; Function A has no such logic
- 修正建议: Include contrastive learning examples that differentiate generic I/O patterns from domain-specific processing；Use graph-based representations that capture long-range data dependencies to distinguish simple retrieval from complex parsing；Incorporate type information or API usage context beyond just token sequences

### case_id=6303 FP boilerplate_overlap

- 方法: `main` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Demonstrates PDF signing and verification using iText library.
- B 摘要: Generates Java adapter classes from Prolog specifications.
- 静态失败原因: Static BERT likely over-relied on boilerplate patterns (e.g., try-catch, FileOutputStream, System.out.println) and the common 'main' structure, failing to distinguish the domain-specific library calls and overall intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled non-clone because the functions have no semantic similarity beyond being generic main methods; their domains and high-level purposes are completely different.
- 共享行为: Both are Java main methods；Both read files from disk；Both produce output files；Both handle exceptions with printStackTrace
- 行为差异: A uses iText for PDF cryptographic signing; B uses Prolog parser and custom code generation；A performs digital signature creation and verification; B generates adapter classes and serializes metadata；A's input is a PDF and keystore; B's input is a Prolog file and classpath；A's output is signed PDFs; B's output is a JAR file with adapter classes
- 修正建议: Incorporate type usage and API call context to differentiate domain-specific operations；Use data flow and call graph to capture high-level semantics beyond surface syntax；Include token-level attention to distinctive identifiers like 'Signature', 'KeyStore', 'Prolog', 'Adapter'

### case_id=6304 FN partial_functionality

- 方法: `getFile` vs `createTempFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies the XML endpoint, and returns the local file path.
- B 摘要: Copies a classpath resource to a temporary file and stores the file reference in an instance variable.
- 静态失败原因: Static BERT models rely heavily on lexical token overlap and structural similarity. The low Jaccard (0.097) and distinct method names ('getFile' vs 'createTempFile') caused the model to miss the underlying shared I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: None
- 共享行为: Both open an input stream and write its contents to a local file.；Both close the output stream after writing.；Both create a file if not already present.
- 行为差异: Function A downloads from a URL, function B reads from a classpath resource.；Function A performs XML parsing and modification; function B only copies raw bytes.；Function A returns the file path; function B is void and assigns to an instance variable.；Function A checks for file existence and skips download if file exists and is non-empty.
- 修正建议: Incorporate behavioral or flow-based features that capture data movement (read-stream, write-file).；Use code summarization or abstract syntax tree (AST) matching to identify similar control-flow cores.；Train on more diverse clone types (Type-3/4) with combined lexical and semantic representations.

### case_id=6305 FN benchmark_preference_bias

- 方法: `recurseFiles` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Recursively traverses a directory, adding non-zip files to a zip archive.
- B 摘要: Launches an Eclipse configuration for a NexOpen project, handling POM files and setting properties.
- 静态失败原因: Static BERT correctly predicted non-clone; the BCB label is likely a false positive, not a model failure.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label may be erroneous; no plausible partial functionality or similar behavior justifies a clone annotation.
- 行为差异: Function A deals with zipping files; Function B deals with Eclipse launch configuration and Maven POM processing.；Function A uses recursion; Function B does not recurse.；Function A operates on files and zip streams; Function B operates on Eclipse resources, XML documents, and properties.；Function A has no dependencies on Eclipse or Maven; Function B is tightly coupled to Eclipse plugin APIs and Maven projects.
- 修正建议: Verify and correct the BCB label for this pair.；Ensure that benchmark annotations are consistent with strict semantic equivalence criteria.

### case_id=6306 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `convert`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Handles GUI actions for setting application preferences like paths for external tools and look-and-feel.
- B 摘要: Converts ACRNEMA stream files to DICOM format, validating and transforming pixel data and metadata.
- 静态失败原因: The model likely overfitted to common Java constructs such as try-finally blocks, file stream usage, and conditional checks for null or empty, ignoring the distinct high-level semantics and method names.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have entirely different purposes (GUI event handling vs. file format conversion) with no shared logic or data flow, despite some superficial lexical overlaps like file operations.
- 共享行为: Both involve file processing or file-related operations (file chooser vs file I/O)
- 行为差异: A is an event-driven GUI handler; B is a batch conversion method.；A manages user preferences; B transforms medical image data.；A uses JFileChooser for file selection; B directly reads/writes files with streams.；A writes to preferences storage; B writes to DICOM files with pixel manipulation.
- 修正建议: Incorporate method name and context in embeddings, e.g., using code summarization or docstrings.；Use control-flow and data-flow analysis to capture program logic rather than surface syntax.；Fine-tune on function-level clone detection with more diverse negative sampling.

### case_id=6307 FN partial_functionality

- 方法: `runInternal` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads and parses an OPDS catalog from HTTP, handling pagination and multiple entries.
- B 摘要: Opens a file or URL stream and delegates reading to another method, returning status.
- 静态失败原因: Static BERT models may focus on surface-level token overlap (e.g., 'URL', 'connection', 'openStream') and miss the global structure and high-level intent due to truncation or lack of data flow understanding.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider Type-4 clones based on loose functional similarity (both read data from URLs) or common API usage (URLConnection/InputStream), but the difference in complexity is substantial.
- 共享行为: Both open HTTP connections or streams；Both handle exceptions；Both involve reading data from a resource
- 行为差异: Function A is a complex loop with pagination, parsing, and callback；Function B is a simple open-and-delegate method；Function A sets many HTTP properties and handles redirects；Function B supports both files and URLs
- 修正建议: Use a model that captures control flow and data dependencies；Incorporate method names and class context；Enhance training with examples of functional composition vs. simple I/O

### case_id=6308 FN partial_functionality

- 方法: `copyFromTo` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using FileChannel, handles errors by printing messages and exiting, and preserves last modified timestamp.
- B 摘要: Builds a site for editing by reading XML files, applying XSLT transformations, performing string replacements, and writing output HTML files for each page.
- 静态失败原因: The static model likely relied on low token Jaccard similarity (0.1) and different method signatures, and failed to recognize any underlying partial semantic overlap because the functions have distinct logic beyond basic I/O.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones due to both functions performing file I/O with error handling, and both being utility-like methods that process files, despite different high-level purposes.
- 共享行为: Both involve file I/O operations (reading and writing files).；Both use FileInputStream for reading.；Both handle I/O exceptions with error messages or logging.
- 行为差异: copyFromTo copies a single file; buildSiteForEdit generates multiple output files from XML.；copyFromTo exits on errors (System.exit); buildSiteForEdit throws exceptions and continues loop.；copyFromTo preserves source file modification time; buildSiteForEdit does not.；buildSiteForEdit involves XML transformation and complex string manipulation; copyFromTo does raw channel copy.
- 修正建议: Incorporate data-flow analysis to detect common I/O patterns (read-process-write).；Use graph-based models capturing control and data dependencies to abstract away structural differences.；Provide more diverse training examples of Type-4 clones with shared sub-behaviors.

### case_id=6309 FP lexical_or_api_overlap

- 方法: `getWebByUrl` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads web page content from a URL and writes it to a local file with logging and recursive link extraction.
- B 摘要: Parses sequence data from a URL in FASTA-like format and stores names and sequences in lists.
- 静态失败原因: The model likely over-relied on surface-level API usage such as URL.openStream(), InputStream, BufferedReader, and try-catch structure, which are common boilerplate for any URL reading task. It failed to capture the distinct core logic and output behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB favors functional similarity; these two functions serve entirely different purposes (web scraping vs sequence parsing) and share only generic I/O patterns. The low token Jaccard (0.175) reinforces that they are not clones even under broad criteria.
- 共享行为: Both open a URL stream to read data；Both use try-catch blocks for exception handling；Both read input line-by-line or character-by-character
- 行为差异: A writes output to a file, B stores output in memory lists；A recursively follows links, B parses header-separated sequences；A uses PrintWriter for file writing, B uses an ImportHelper class；A logs progress, B silently collects data
- 修正建议: Include data flow analysis to distinguish different output operations；Use role-aware tokenization that discounts common I/O boilerplate；Incorporate method-level semantic embeddings or documentation

### case_id=6310 FP lexical_or_api_overlap

- 方法: `import_hints` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Imports hints from a file (URL or local) to place puzzle pieces on a board.
- B 摘要: Searches Google Images for an artist and album to retrieve image URLs.
- 静态失败原因: The model likely over-relied on overlapping structural elements (URL, BufferedReader, try-catch) and missed the domain-specific differences, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because they perform entirely different tasks (puzzle hint import vs. google image search), despite sharing some common I/O and URL handling patterns.
- 共享行为: Both use URL and BufferedReader to read data from a stream.；Both have exception handling with try-catch blocks.；Both involve I/O operations (reading from network/file).
- 行为差异: A reads a structured text file to place puzzle pieces; B fetches HTML from Google and parses image URLs.；A returns boolean indicating success/failure; B returns void.；A uses StringTokenizer for parsing; B does not.；A operates on puzzle board state; B updates a list of image URLs.
- 修正建议: Incorporate method name similarity or context from surrounding code.；Use additional semantic features like return types and class-level information.；Train with more diverse examples to reduce bias towards common API boilerplate.

### case_id=6311 FN partial_functionality

- 方法: `runInternal` vs `importRoles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads and parses OPDS catalog entries from an HTTP URL, handling pagination and downloading books.
- B 摘要: Fetches XML from a URL and parses RoleName elements into a list.
- 静态失败原因: Low token Jaccard (0.086) and very different method names/code structure made the model miss the high-level pattern of network I/O plus XML parsing.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: None
- 共享行为: Both open a URL connection and read input data.；Both parse XML content.；Both handle I/O exceptions.
- 行为差异: A handles HTTP redirects, content-disposition, and progress tracking; B does not.；A may download books and manage pagination; B only parses a specific XML structure.；A is much longer and has a loop for multiple pages; B is a single-pass parse.
- 修正建议: Use a model that captures structural patterns like control flow or data flow.；Add training data with cross-domain network I/O and parsing tasks.

### case_id=6312 FP long_range_semantics

- 方法: `actionPerformed` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles UI action commands by opening file choosers and saving preferences.
- B 摘要: Copies a file using FileChannel with synchronization.
- 静态失败原因: The model may have been misled by common patterns like file I/O and exception handling, but lacked understanding of overall context and semantics, leading to a false positive despite low token similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels non-clone because the functions have clearly different functionality and structure.
- 共享行为: Both use try-catch-finally for resource cleanup；Both involve file operations；Both have conditional checks
- 行为差异: Function A is a UI event handler; Function B is a file copy utility；Different parameters and return types；Different control flow and overall purpose
- 修正建议: Improve model's ability to capture overall functionality；Use more robust structural matching；Incorporate usage of return values and method signatures

### case_id=6313 FN partial_functionality

- 方法: `main` vs `decodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, extracts its zip entries, and writes each entry to a file.
- B 摘要: Reads a Base64-encoded file, decodes it, and writes the decoded bytes to an output file, returning success.
- 静态失败原因: Low token overlap and different API usage (URL/ZipInputStream vs FileInputStream/Base64) cause static models to overlook the abstract similarity of the stream-copying loop.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both implement the common pattern of stream-based data copying with buffering, focusing on the partial functionality of I/O transfer rather than the specific context.
- 共享行为: Both read from an input stream and write to an output stream using a byte buffer in a loop.
- 行为差异: Function A specifically handles zip entries and URL downloading, while B handles Base64 decoding.；Function A prints progress and does not return a value, B returns a boolean success flag.；Different buffer sizes (BUFFER vs 65536) and different stream types (ZipInputStream vs Base64.InputStream).
- 修正建议: Include more Type-4 examples with diverse I/O patterns in training.；Use dataflow or abstract syntax tree (AST) representations to capture the copy-loop structure.；Leverage graph-based models that focus on control and data flow.

### case_id=6314 FP partial_functionality

- 方法: `doRawRequest` vs `sendPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends postData to a hardcoded URL via HTTP POST and returns the response as a string, throwing IOException on failure.
- B 摘要: Sends param to a given URL via HTTP POST with an Accept-Language header and returns the response as a string, catching exceptions and showing a message on failure.
- 静态失败原因: The model likely over-relied on API token overlap (URL, openConnection, setDoOutput, getOutputStream, BufferedReader, etc.) and similar control flow, ignoring critical differences in exception handling and parameterization which require deeper semantic understanding.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as non-clone because the hardcoded URL and exception handling differences suggest distinct use cases and reliability expectations, making them not functionally equivalent even in a broad sense.
- 共享行为: Open HTTP connection；Set doOutput to true；Write payload to output stream；Flush output
- 行为差异: Function A uses hardcoded URL; B takes URL as parameter；A uses OutputStreamWriter; B uses PrintWriter；A does not set headers; B sets Accept-Language；A uses default charset; B uses UTF-8 for response
- 修正建议: Train with more examples that differ in error handling and method signatures；Incorporate dataflow analysis to capture exception paths and method dependencies；Use contrastive learning to distinguish similar but non-equivalent I/O patterns

### case_id=6315 FN benchmark_preference_bias

- 方法: `readAndRewrite` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a DICOM image file, parses it, and writes the pixel data to an output file.
- B 摘要: Builds a website by transforming XML pages and writing the rendered output to files.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone (0) because low token overlap (Jaccard 0.036) and no significant structural or semantic similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this as a clone due to a broad interpretation of 'data reading/writing and transformation', but the specific domains and operations are fundamentally different.
- 共享行为: Both perform file I/O operations (reading from input, writing to output).；Both involve some form of data transformation (DICOM pixel data vs. XML/site rendering).
- 行为差异: readAndRewrite specifically handles DICOM medical image format with pixel data reading/writing.；buildSiteForEdit processes a collection of pages with XML transformations and includes extensive string manipulation and state tracking.；readAndRewrite is a short private method; buildSiteForEdit is a long public method with many parameters and complex control flow.；The libraries and APIs used are completely different (DICOM vs. XML/website frameworks).
- 修正建议: Re-verify BCB annotation for this pair; likely a false positive in the benchmark.；If BCB intended Type-4 (functionally similar) clones, consider whether both perform 'read-transform-write' patterns at a high level, but the transformation logic is domain-specific and not semantically equivalent.

### case_id=6316 FN partial_functionality

- 方法: `copyResource` vs `resolvePlugins`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file using byte-by-byte stream copy.
- B 摘要: Downloads a plugins.xml file from a network URL to a cache directory if missing, then resolves plugins.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token and structural overlap. The low token Jaccard (0.16), different method names, and different copy implementations (while loop vs IOUtils.copy) cause the model to miss the functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a Type-3/4 clone because both functions implement the same abstract pattern of reading from an input source and writing to an output file, with minor variations in control flow and copy implementation.
- 共享行为: Open an input stream from a URL or file；Open an output stream to a file；Copy data from input to output；Close streams
- 行为差异: Function A always copies; Function B copies only if file does not exist；Function A uses byte-by-byte while loop; Function B uses IOUtils.copy；Function A throws Exception on missing source; Function B catches all exceptions；Function B has additional logic after copying (calls another resolvePlugins)
- 修正建议: Enhance model with dataflow analysis to track stream operations；Use graph-based neural networks to capture abstract I/O patterns；Train on functional equivalence tasks with contrastive learning

### case_id=6317 FN partial_functionality

- 方法: `runScript` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from a URL as a string.
- B 摘要: Checks for a new version by parsing a version file from a URL.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on lexical and structural overlap, which is low (token Jaccard 0.214). The models fail to capture the high-level semantic intent of URL reading due to differences in method names, variable names, and control flow (e.g., do-while vs while loop, string concatenation vs line parsing).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers these clones because both implement the high-level functionality of downloading data from a URL and processing it, even though the specific processing and output differ. This aligns with Type-4 (semantic) clone criteria where partial functionality overlap is accepted.
- 共享行为: Both open a URL connection.；Both read data from an input stream.；Both handle IOException with error handling.
- 行为差异: A reads raw bytes and concatenates into a string; B reads lines and parses version/build info.；A returns the entire data string; B updates UI with version check results.；A uses BufferedInputStream; B uses BufferedReader.
- 修正建议: Augment training data with Type-4 clones having low lexical similarity but shared high-level patterns.；Incorporate dataflow analysis to detect common API usage patterns like URL.openStream().；Use contrastive learning with semantic similarity from code summaries or docstrings.

### case_id=6318 FN partial_functionality

- 方法: `readIntoList` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads HTML-like lines from a URL and creates JMenuItem objects for a menu with action listeners.
- B 摘要: Sends XML request to a geoservice, parses response, and extracts place names and gazetteer IDs as tuples.
- 静态失败原因: Low token Jaccard (0.125) and very different method names, APIs, and control flow lead to non-clone prediction. The model lacked high-level understanding of the common pattern of reading from URL and parsing.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to both reading from a web resource and parsing structured lines/XML, broad input-output patterns, and both involve IO operations in similar exception handling style.
- 共享行为: Both read from URL via BufferedReader；Both parse lines/XML from the stream；Both handle exceptions with try-catch
- 行为差异: A builds UI components, B returns data tuples；A parses HTML tags, B parses XML elements and uses DocumentHelper；A adds action listeners, B does not handle UI；B has retry logic and XML construction, A does not
- 修正建议: Improve detection of domain-specific transformations；Enhance understanding of high-level semantics beyond token overlap；Consider dataflow patterns for IO and parsing

### case_id=6319 FP lexical_or_api_overlap

- 方法: `read` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a skeleton file from classpath, parsing lines into sections delimited by '---', and validates section count.
- B 摘要: Constructor for a Swing browser GUI that fetches an XML/HTML page from a URL, optionally applies XSLT transformation, and displays the result.
- 静态失败原因: Static BERT likely overfitted on the common token patterns like 'BufferedReader', 'InputStreamReader', 'url.openStream()', and 'readLine()', ignoring the divergent program logic and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the overall functionality differs completely; shared I/O patterns are too generic to indicate semantic similarity.
- 共享行为: Both open a URL or resource stream using BufferedReader and InputStreamReader；Both read lines in a loop
- 行为差异: A reads from classpath resource; B reads from network URL；A parses sections delimited by '---'; B parses XML/HTML with optional XSLT；A validates section count; B sets up GUI and handles events；A throws exceptions on error; B catches and logs errors
- 修正建议: Incorporate structural and dataflow analysis to distinguish parsing vs GUI construction；Use graph-based representations capturing control flow beyond API calls；Augment training data with examples where common APIs serve different purposes

### case_id=6320 FP long_range_semantics

- 方法: `main` vs `trainClassifier`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses a Prolog file and generates adapter classes into a JAR file.
- B 摘要: Trains a classifier by executing an external command with arguments.
- 静态失败原因: Static BERT methods often rely on token-level patterns and may be misled by common API calls (e.g., File, System.out) while missing the overall semantic dissimilarity due to the large difference in function length and complexity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels as non-clone because the functions have entirely different purposes and no significant functional overlap; they are from different domains (code generation vs classifier training).
- 共享行为: Both methods perform I/O operations (file reading/process execution).；Both use File objects to reference paths.
- 行为差异: Function A reads and parses a Prolog file, generates bytecode, and writes to a JAR.；Function B builds a command-line and runs a subprocess, capturing I/O.；Function A has complex control flow and multiple error handling paths.；Function B is a straightforward command execution with simple output forwarding.
- 修正建议: Enhance model with structured encoding to capture long-range control flow.；Incorporate function-level semantic embeddings derived from documentation or comments.；Use contrastive learning to better distinguish functions with low lexical overlap.

### case_id=6321 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getLinksFromURLFast`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a version check URL, parses build version lines, and calls a version comparison method.
- B 摘要: Connects to a URL, downloads HTML, and extracts all hyperlinks and their texts into vectors.
- 静态失败原因: The static BERT model likely focused on the common boilerplate of opening a URL, creating InputStream/Reader, and reading lines in a while loop, which are syntactically similar but semantically unrelated.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotations typically require functional equivalence or close similarity in behavior; these two functions have entirely different outputs and purposes, so BCB would label them non-clones.
- 共享行为: Both open a URL and read input using BufferedReader；Both use a while loop to read lines from the input stream
- 行为差异: A parses specific version number lines; B parses HTML anchor tags using regular expressions；A only reads each line for prefix matching; B concatenates all lines into a buffer then applies regex；A returns void and calls another method; B returns a Vector array；A shows/hides wait cursor and handles exceptions with error dialog; B throws Exception and logs timing
- 修正建议: Incorporate control flow and data dependency analysis to distinguish different processing logic；Use contrastive learning with hard negative examples that share boilerplate but differ in core behavior

### case_id=6322 FN benchmark_preference_bias

- 方法: `setContenu` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sets the content of an electronic file by copying from a source, checking for duplicates, and updating metadata.
- B 摘要: Builds a website for editing by processing XML, transforming, and writing output files.
- 静态失败原因: Static BERT models correctly predicted non-clone due to very low lexical overlap; the BCB label may be erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as file manipulation tasks, but the functionalities are fundamentally different; likely a benchmark mislabel.
- 共享行为: both write to output streams；both handle IOExceptions；both involve loops
- 行为差异: different overall purpose (content set vs site build)；different data structures and dependencies；different error handling and logging
- 修正建议: Re-evaluate BCB label; functions are clearly not clones.；Improve benchmark criteria to avoid over-broad Type-4 clones.

### case_id=6323 FN partial_functionality

- 方法: `doVersionCheck` vs `login`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for a newer version of jEdit by fetching a version-check URL and parsing version/build lines.
- B 摘要: Logs into a service (LOLA) by sending credentials via POST and extracting a session ID from the response.
- 静态失败原因: Static BERT models rely heavily on token-level overlap and named entities. The low Jaccard similarity (0.1778) and different method names, URLs, and string constants cause the model to miss the structural pattern of network I/O and response parsing.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers this a clone because both functions perform network I/O, parse a response, and handle exceptions, representing a common pattern (Type-4 similarity) even though the specific logic differs.
- 共享行为: Both open a URL connection and read input line by line.；Both handle IOException with error reporting.；Both parse the response to extract specific information.
- 行为差异: doVersionCheck uses GET; login uses POST with encoded form data.；doVersionCheck shows/hides wait cursor; login does not.；doVersionCheck compares versions; login sets session ID.；doVersionCheck returns void; login returns String (session ID).
- 修正建议: Use data-flow analysis to capture network I/O patterns.；Incorporate structural AST matching for common control-flow patterns like open-read-parse-close.；Train on broader Type-4 clone examples that share high-level intent but differ in specifics.

### case_id=6324 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `getWebPage`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a hardcoded Twitter feed using Apache HttpClient, checks HTTP 200, and returns content as a string, returning empty on failure.
- B 摘要: Reads any web page from a given URL using URL.openStream(), concatenates lines, and throws an Error on failure.
- 静态失败原因: Static BERT overemphasized lexical overlap (e.g., BufferedReader, while loop) and missed deeper semantic differences like error handling, API choice, and parameterization.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers non-clone due to significant differences in error handling, API usage, and parameterization, despite shared core functionality.
- 共享行为: Both read HTTP response line by line using BufferedReader and return as a string.
- 行为差异: A uses HttpClient with status check; B uses URL.openStream() without status check.；A has hardcoded URL; B takes URL as parameter.；A returns empty string on failure; B throws an Error.；A uses StringBuilder; B uses inefficient string concatenation.
- 修正建议: Incorporate dataflow analysis to track error paths.；Recognize different HTTP client patterns.；Consider parameter variability in input sources.

### case_id=6325 FN benchmark_preference_bias

- 方法: `getContent` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Executes an HTTP request and returns the response body as a string.
- B 摘要: Reads configuration data from static strings and a file to populate various sets and mappings for Tibetan transliteration.
- 静态失败原因: The static BERT model correctly identified them as non-clones; the supposed failure is due to a questionable BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to a broad interpretation of both methods performing 'data reading' or 'input processing', but the actual functionality is entirely different.
- 共享行为: Both methods process input data and populate data structures
- 行为差异: Different input sources (HTTP response vs static strings and file)；Different output (String return vs void with side effects)；Completely different data processing logic；Different external library usage (Apache HttpClient vs StringTokenizer and file I/O)
- 修正建议: Re-annotate this pair in BCB with a non-clone label；Improve annotation guidelines to require actual semantic similarity beyond vague I/O operations

### case_id=6326 FN benchmark_preference_bias

- 方法: `CopyFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a local file from source path to destination path, creating parent directories if needed.
- B 摘要: Retrieves a resource by name, either from a local cache or by downloading from a URL, caching it locally, and returns an InputStream.
- 静态失败原因: The model correctly identified low token overlap (0.099) and different method purposes, but BCB annotation might be erroneous or based on very broad semantic criteria.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered them clones based on broad I/O operations and directory creation, but this is a weak similarity; likely a labeling error.
- 共享行为: File I/O operations；Create directories with mkdirs()；Use FileInputStream and FileOutputStream；Close streams
- 行为差异: A copies a local file; B downloads from URL or uses cache；A returns destination path; B returns InputStream；A throws exceptions; B catches exceptions and returns null；B includes HTTP connection, caching logic, and modification time checks
- 修正建议: Review BCB annotations for consistency；Incorporate better semantic understanding to avoid overly broad clone detection

### case_id=6327 FN partial_functionality

- 方法: `executeHttpGet` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Executes an HTTP GET request to a given URI and returns the response body as a JSONObject.
- B 摘要: Registers a User object by encoding password, setting default authority, creating a hash, making an HTTP GET to a phpBB forum to obtain a forum ID, persisting the user, and sending a confirmation email; returns true on success, false on mail failure.
- 静态失败原因: Static BERT models rely on token-level representations; they may detect some lexical overlap (e.g., 'BufferedReader', 'readLine') but lack the semantic understanding to realize that the overall methods are fundamentally different in purpose and behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the shared HTTP GET pattern as a non-trivial functional similarity, qualifying as a Type-4 clone despite the overall functional mismatch.
- 共享行为: Both perform an HTTP GET request to a URL；Both read the response line by line using BufferedReader
- 行为差异: A's sole purpose is HTTP GET and JSON return; B's HTTP GET is a minor sub-step；B includes password encoding, authority setting, database persistence, email sending；A returns JSONObject; B returns boolean；B modifies the passed object and handles multiple exceptions; A throws Exception
- 修正建议: Use graph-based or dataflow-aware models to capture the overall program structure；Incorporate method names or documentation embeddings for better semantic disambiguation；Train with contrastive learning on functional similarity rather than syntactic overlap

### case_id=6328 FN partial_functionality

- 方法: `moveFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Moves a file by copying its contents to a target file and deleting the original.
- B 摘要: Retrieves a resource by URL, caches it locally if needed, and returns an InputStream to the cached file.
- 静态失败原因: The token Jaccard is low (0.127), and the functions have different method names, different control flow (try-catch, multiple conditions in B), and significantly different lengths and API calls (e.g., URLConnection, HttpURLConnection, cache logic). The model likely focused on lexical and API-level differences and did not capture the underlying semantic similarity of data copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both implement a 'copy file' functionality: one copies a local file to another local file, the other copies a remote resource to a local cache file. They share the core pattern of reading from a source and writing to a destination, which aligns with Type-4 (semantically similar but syntactically different).
- 共享行为: Both read data from an input stream and write it to an output stream using a buffer.；Both involve file I/O operations.
- 行为差异: moveFile operates on local files only and deletes the original; getResourceAsStream handles remote URLs, caching logic, and HTTP connections.；moveFile has void return type; getResourceAsStream returns an InputStream.；getResourceAsStream has complex control flow with try-catch and multiple conditions.
- 修正建议: Improve dataflow analysis to recognize the read-write loop pattern.；Incorporate functional semantics (e.g., file copy) into embeddings.；Use clone detection targets that focus on partial similarity.

### case_id=6329 FN dataflow_blindspot

- 方法: `addIDs` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `dynamic_equivalence_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Adds IDs from GMD database by parsing HTML responses and updating a PeakListRow.
- B 摘要: Performs an HTTP POST request and returns the response body as a string.
- 静态失败原因: Low token Jaccard (0.135) and domain-specific vocabulary differences caused the model to miss the structural I/O similarity. Static BERT models are sensitive to lexical overlap and may not capture long-range dataflow patterns shared by both functions.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本可能是 API 写法不同但行为等价的漏报。建议测试目标为 input_output_equivalence。
- BCB 偏好解释: BCB often considers functions performing network I/O with similar error handling and line-by-line reading as Type-3 or Type-4 clones, even if domain-specific logic differs.
- 共享行为: Both initiate an HTTP request and read the response line by line using BufferedReader.；Both handle IOException with error logging or setting error fields.；Both return a value indicating success/failure (int/string).
- 行为差异: Function A uses HTTP GET (via URL.openStream), while B uses HTTP POST (via HttpClient).；Function A parses HTML and updates a data structure, while B returns raw response.；Function A has integer return type and extensive conditional parsing, B returns string and has generic structure.；Error handling: A logs and returns 0, B sets instance error fields and returns null.
- 修正建议: Use graph-based code representations (e.g., AST or CFG) to capture structural I/O patterns.；Augment training data with I/O-heavy functions from different domains to learn similarity beyond tokens.；Employ contrastive learning to pull together functions with similar I/O flow despite different APIs.

### case_id=6330 FP boilerplate_overlap

- 方法: `byReference` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Creates a temporary file from an input stream and returns it as immutable content.
- B 摘要: Handles various action commands (like setting Graphviz path, ImageMagick path, scale, date format, look-and-feel) in a configuration dialog, with file choosers and preference saving.
- 静态失败原因: Static model may have been misled by shared tokens like 'File', 'IOException', 'JFileChooser', 'Suku'? Actually no common domain. More likely the model's attention focused on structural similarities like try-catch, null checks, and return statements, ignoring the high-level semantic differences. Also both have method bodies with multiple operations, but the operations differ. The model might have high false positives on functions with similar boilerplate (file handling, exception handling).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have completely different purposes and signatures; one is a static utility, the other is an action listener for GUI settings.
- 共享行为: Both involve file operations and exception handling.
- 行为差异: Function A is a utility to copy InputStream to a temp file, while B is a complex event handler for settings.；A has a single straightforward task, B has multiple conditional branches for different commands.；A returns an object, B returns void and updates UI.
- 修正建议: Improve model to focus on method name and overall purpose rather than low-level token matches.；Use code summarization or AST-based differences to detect domain mismatch.；Reduce false positives by requiring higher structural similarity, e.g., same method signature or class context.

### case_id=6331 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks and anchor texts from an HTML page fetched via URL, returning two vectors of links and texts.
- B 摘要: Fetches version build numbers from a URL and performs a version check using a separate method.
- 静态失败原因: Static BERT models like CodeBERT or GraphCodeBERT may have been misled by high lexical and API overlap (URL, BufferedReader, readLine loop) without capturing the distinct semantic purposes of the two functions.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functional similarity (Type-4) or near-miss structural similarity (Type-3). Here, the core functionality differs entirely (link extraction vs. version checking), so BCB would label it as non-clone despite some boilerplate API overlap.
- 共享行为: Open a URL connection and read lines via BufferedReader；Use a while loop to read lines until null
- 行为差异: Function A extracts and returns link data (href and text) after regex parsing; Function B extracts version strings and calls another method；Function A uses complex regular expressions for URL and HTML parsing; Function B uses simple string prefix checks；Function A returns a Vector array; Function B is void and may show an error dialog on failure
- 修正建议: Incorporate task-level or intent-aware representations；Use dataflow analysis to differentiate processing logic；Train on more diverse non-clone pairs with similar API usage but different semantics

### case_id=6332 FP lexical_or_api_overlap

- 方法: `postData` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Send HTTP POST request with form data to a URL and discard the response.
- B 摘要: Download an RDF model from a URL and return it.
- 静态失败原因: The model likely overfitted to overlapping API sequences (URLConnection, openConnection, setRequestProperty, getInputStream, close) and ignored higher-level semantics like output vs input, return types, and exception handling patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because despite sharing URLConnection boilerplate, the core functionality differs fundamentally: one is for sending data via POST, the other for downloading and parsing an RDF model. BCB favors functional similarity over boilerplate overlap.
- 共享行为: Open a URLConnection to a specified URL；Set request properties on the connection；Read from an input stream；Close the input stream
- 行为差异: Output: Function A writes data to the output stream, Function B only reads；Return type: Function A returns void, Function B returns a Model object；Function A sends form-encoded data, Function B downloads and parses RDF；Function A discards the response, Function B processes it into a model
- 修正建议: Incorporate data flow analysis to distinguish output vs input streams；Consider return type and method purpose (void vs Model)；Add analysis of exception handling patterns；Use type-aware graph embeddings that capture I/O direction

### case_id=6333 FN boilerplate_overlap

- 方法: `handler` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.65`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads from a parameterized URL and extracts substrings based on pattern parameters.
- B 摘要: Reads from a hardcoded URL, concatenates all lines into a StringBuffer, and logs the result.
- 静态失败原因: Low token Jaccard (0.21) and different method signatures/strings caused the model to focus on superficial differences, missing the structural I/O pattern that BCB values.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider the common boilerplate of URL reading (open connection, BufferedReader loop, close) as a Type-3 clone, despite different business logic, due to broad acceptance of partial functionality similarity.
- 共享行为: Both open a URL and read lines via BufferedReader；Both close the reader in a finally-like manner
- 行为差异: Function A uses parameterized URL and pattern extraction; Function B uses a hardcoded URL and simple concatenation；Function A modifies an input map; Function B logs output；Function A has nested loops for pattern matching; Function B has a single read loop
- 修正建议: Incorporate AST-based structural similarity to capture common I/O patterns；Use fine-tuning on datasets that emphasize boilerplate clones

### case_id=6334 FP lexical_or_api_overlap

- 方法: `getWebPage` vs `get`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a web page as a string from a URL, throwing an error on failure.
- B 摘要: Makes an HTTP GET request with custom headers, parses lines into GameRecord objects, returns array or null on failure.
- 静态失败原因: Static BERT/CodeBERT may over-rely on lexical and API overlaps (URL, BufferedReader, readLine, IOException) while ignoring differences in return type, error handling, and overall logic flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions serve different purposes despite similar API usage; here one is generic page fetch, the other is a specific game record query.
- 共享行为: Both open HTTP connections to read data from a URL.；Both use BufferedReader to read lines.；Both handle IOException.
- 行为差异: A returns a single string of all content; B parses lines into GameRecord objects and returns an array.；A throws a custom Error on IOException; B prints stack trace and returns null.；B uses custom HTTP headers and skips comment lines; A does not.；B returns null on non-OK response; A has no such logic.
- 修正建议: Incorporate data-flow or control-flow representations to capture semantic differences.；Use models that distinguish between generic I/O and specific data transformations.；Consider return type and error-handling patterns as discriminative features.

### case_id=6335 FP boilerplate_overlap

- 方法: `readPage` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads an HTML page from a URL, optionally ignoring comment lines, and returns the entire content as a string.
- B 摘要: Reads a service file from the classpath, skips comment lines, and returns an instance of the first non-comment class name found.
- 静态失败原因: The static BERT model likely over-relied on high lexical overlap in boilerplate patterns (BufferedReader, openStream(), while loop, comment check) and missed the semantic divergence in return types and control flow (early return vs accumulation).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have distinct purposes and outputs, despite a common reading pattern. The partial functionality overlap (comment skipping) is minor relative to overall task difference.
- 共享行为: Both open a URL and read lines with BufferedReader；Both skip lines that start with '#'
- 行为差异: A returns concatenated HTML string; B returns a single object from first non-comment line；A reads all lines; B stops after first valid line；B throws an exception if no factory found; A returns potentially empty string
- 修正建议: Incorporate data-flow analysis to track how read data is used；Emphasize method signatures, return types, and exception behavior；Use contrastive learning on negative pairs with lexical overlap but different semantics

### case_id=6336 FN partial_functionality

- 方法: `copy` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file by reading and writing characters one by one.
- B 摘要: Modifies a localized properties file by optionally copying a template, then reading, updating, and writing the file.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the overall method signature and high-level semantic difference, and the low token Jaccard similarity (0.188) caused it to miss the shared code block. The models may not have captured the local structural similarity within the larger function B.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB labels these as clones because they share a significant, identical code segment (the file copy loop) that is a core part of both functions. This is a classic Type-3 clone where one function embeds the other's functionality.
- 共享行为: Both include an identical block of code that copies a file using FileReader and FileWriter with a character-by-character read-write loop.
- 行为差异: Function A only copies files; Function B additionally checks file existence, reads and parses properties, modifies a specific key-value pair, and writes the modified content back.；Function B has error handling that prints stack traces; Function A throws exceptions.
- 修正建议: Include subgraph matching or attention to local code blocks.；Consider using data-flow analysis to detect embedded identical functionality.；Use a clone detector that explicitly recognizes copy-paste segments even within larger functions.

### case_id=6337 FP boilerplate_overlap

- 方法: `main` vs `readAndRewrite`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses command-line arguments, reads a Prolog file, generates Java adapter classes, and writes output as a JAR file.
- B 摘要: Reads a DICOM image file, extracts pixel data, and writes the modified dataset to an output file.
- 静态失败原因: The static BERT model may have been misled by the presence of common programming constructs (file reading, print statements, try-catch) and a similar sequential structure, ignoring the entirely different domain-specific operations and library APIs.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have different domain intents, even if they share trivial I/O patterns. The overall functionality is completely different.
- 共享行为: Both perform file I/O operations；Both print status messages to the console
- 行为差异: Function A processes Prolog files and generates Java bytecode; Function B processes DICOM medical images；Function A uses a complex workflow with parsers, visitors, and class writers; Function B uses DICOM-specific libraries for pixel data and dataset manipulation；Function A handles command-line arguments and multiple file outputs; Function B is a simple read-write pipeline
- 修正建议: Include semantic understanding by comparing high-level intent via API usage；Use dataflow analysis to distinguish domain-specific operations；Train with more examples of contrasting domains to reduce false positives from boilerplate

### case_id=6338 FN partial_functionality

- 方法: `sendExceptionToServer` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST and prints the server response.
- B 摘要: Checks for software version updates by reading a version file from a URL and shows appropriate GUI message.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low token overlap (0.218) and different domain keywords (exception vs version), missing the abstract structural similarity of URL reading and line processing.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both are static void methods that perform network I/O (opening a URL, reading lines), have similar control flow (try-catch, while loop), and are error-handling or version-checking utilities in a larger system.
- 共享行为: Both open a URL and read lines from the input stream；Both handle IOException with try-catch
- 行为差异: A uses HTTP POST with parameters, B uses HTTP GET without parameters；A writes exception data, B reads version/build numbers；A outputs to console, B outputs to GUI dialogs and manages cursor
- 修正建议: Use data augmentation with token substitution to capture structural patterns；Incorporate graph-based representations that highlight control flow similarities

### case_id=6339 FP lexical_or_api_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses a Prolog file and generates adapter classes and resources.
- B 摘要: Copies a file using NIO FileChannel with synchronized locking.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-relied on superficial lexical overlap (e.g., 'File', 'IOException', try-catch patterns) and ignored the vastly different control flow and semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these as non-clones because their functionalities are completely different; low token similarity and no shared domain logic.
- 共享行为: Both perform file I/O operations；Both handle IOException with try-catch
- 行为差异: Function A does complex code generation and class assembly; Function B does simple file copy；Function A uses multiple libraries and reflection; Function B uses only NIO channels；Function A is a command-line entry point; Function B is a utility method
- 修正建议: Incorporate dataflow or control flow analysis to differentiate file manipulation patterns；Use finer-grained API matching that distinguishes read/write vs. complex transformations

### case_id=6340 FN partial_functionality

- 方法: `httpRequestByPOST` vs `PhoneSetImpl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Constructor that reads lines from a URL and populates a phone set map.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on low token overlap (0.2) and different method signatures, error handling, and control flow, missing the high-level similarity of the read-loop structure.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both functions as performing stream-based line reading and processing, a common pattern, thus labeling them a clone under broad Type-4 criteria.
- 共享行为: Reads input line by line using BufferedReader；Processes each line until null is encountered
- 行为差异: A uses HttpClient for HTTP POST, B opens a URL stream directly；A returns null on error and sets error codes, B throws IOException；A filters based on HTTP status code, B skips lines starting with '***'；A appends lines to a StringBuffer for final response, B parses lines and adds to a map
- 修正建议: Improve model ability to recognize common patterns like stream reading across different contexts；Incorporate dataflow analysis to capture the read-process loop as a semantic fragment；Enhance training data with more diverse partial functionality clones

### case_id=6341 FP other

- 方法: `readData` vs `Converter`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses comma-separated string fields into various sets and maps for configuration.
- B 摘要: Reads a file in SJIS encoding and writes it to another file in UTF8 encoding.
- 静态失败原因: The large length and complexity of code_a may have caused the model to focus on local patterns (e.g., loops, API calls) that are also present in code_b, but the overall semantics are completely different. The model may have missed the global purpose due to attention limitations.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have entirely different purposes: one is configuration parsing, the other is file encoding conversion. No structural or functional similarity exists.
- 共享行为: None
- 行为差异: Function A operates on static string variables and populates in-memory data structures; Function B performs file I/O and character encoding conversion.；Function A is a void method with no parameters; Function B is a constructor that takes two file path strings.；Function A uses StringTokenizer and HashSet; Function B uses FileInputStream, BufferedReader, FileOutputStream, BufferedWriter.
- 修正建议: Improve training with more diverse non-clone pairs that share trivial API overlap.；Use a model with better long-range dependency handling (e.g., graph neural networks or transformers with larger context).；Incorporate control flow and data flow analysis to capture overall function semantics.

### case_id=6342 FP lexical_or_api_overlap

- 方法: `init` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Initializes a servlet by loading and registering classes listed in a registry file.
- B 摘要: Downloads a vector tile from a URL, parses it into geometries, and adds features to a map data source.
- 静态失败原因: Static models like CodeBERT may overemphasize lexical token overlaps (e.g., BufferedReader, readLine, IOException) and miss the distinct control flows, method signatures, and application domains.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because the shared code is generic boilerplate (I/O), while the core functionality is completely different (class loading vs. tile processing).
- 共享行为: Both use BufferedReader to read lines from an InputStream.；Both handle IOException exceptions.；Both use try-catch blocks for resource handling.
- 行为差异: Function a loads Java classes from a registry file; function b downloads and parses geographic tile data.；Function a iterates over multiple URLs; function b processes a single URL.；Function a registers classes for later use; function b adds geometries to a data source and synchronizes state.；Function b includes complex synchronization and data structure manipulation not present in a.
- 修正建议: Incorporate dataflow or control-flow analysis to differentiate boilerplate from core logic.；Use method signature and call context as additional features.；Train on negative examples with high lexical similarity but low semantic similarity.

### case_id=6343 FN benchmark_preference_bias

- 方法: `doGet` vs `testReadPerMemberSixSmall`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests to retrieve and display a web page, with caching and logging.
- B 摘要: Tests reading of multiple GZIP members from a compressed byte array using assertions.
- 静态失败原因: The static model correctly predicted non-clone because the token sequences, API usage, and overall semantics are highly dissimilar; low Jaccard similarity (0.0356) and distinct contexts made the clone signal absent.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have incorrectly labeled this as clone due to potential noise in the dataset; there is no apparent partial functionality or structural similarity to justify a clone annotation even under broad BCB-style preference.
- 共享行为: None; functions have no meaningful overlap.
- 行为差异: Different domains: web request handling vs. compression stream testing；Different APIs: HttpServletRequest/Response vs. GZIPMembersInputStream/IOUtils；Different control flow: conditional page retrieval and error handling vs. looped member reading with assertions；Different output: writes HTML response vs. performs unit test assertions
- 修正建议: Re-evaluate the BCB label for this pair as likely a misannotation；Improve dataset consistency by removing or correcting spurious clone pairs

### case_id=6344 FN benchmark_preference_bias

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using NIO FileChannel.
- B 摘要: Builds a website for editing by processing pages, applying XSLT transformations, and writing output files.
- 静态失败原因: The static BERT model likely focused on low token overlap (0.038) and different method names, leading to a non-clone prediction, which aligns with our analysis but contradicts the BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both involving file I/O, but the semantic functionality is entirely different, suggesting a possible mislabel or overly broad criteria.
- 共享行为: Both perform file I/O operations.
- 行为差异: copyFile is a simple file copy; buildSiteForEdit is a complex multi-step process with XSLT and string manipulation.；copyFile uses NIO channels; buildSiteForEdit uses FileInputStream and custom FileSystem methods.
- 修正建议: Refine BCB annotation guidelines to avoid overly broad type-4 clones.；Incorporate functional semantics beyond superficial I/O operations.

### case_id=6345 FN partial_functionality

- 方法: `run` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies files from a directory to a single output file using Hadoop FileSystem and IOUtils.
- B 摘要: Builds a website for editing by transforming XML pages and writing output files using a custom FileSystem and FTP.
- 静态失败原因: The low token Jaccard similarity (0.087) and different method names, combined with the lack of abstract reasoning about data flow, likely caused the model to miss this as a clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone due to the shared low-level pattern of reading from input and writing to output, but the functional semantics are vastly different.
- 共享行为: Both functions read from input sources and write to output destinations using streams.
- 行为差异: Function A is a simple command-line utility; Function B is a complex web page generation method.；Function A uses Hadoop FileSystem; Function B uses a custom FileSystem class and FTP.；Function A concatenates files; Function B performs XSLT transformations and string manipulations.；Function A has a single output stream; Function B writes multiple output files.
- 修正建议: Train models to recognize abstract I/O patterns across different contexts and programming paradigms.；Incorporate data-flow analysis to identify read-write operations regardless of surrounding logic.

### case_id=6346 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `readReferenceText`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks and their anchor texts from a given URL using regex, returning them as a pair of vectors.
- B 摘要: Reads the text content of a file identified by a string identifier from a bundle and returns it as a single string.
- 静态失败原因: The static model likely overemphasized the common structural pattern (URL opening, BufferedReader, line reading, StringBuffer) and ignored the unique functionality (regex-based link extraction vs. plain text reading).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically annotates as non-clone when functions have distinct high-level purposes, even if they share boilerplate I/O code. Here, one extracts hyperlinks and the other reads a text file, which are semantically different tasks.
- 共享行为: Both open a URL connection and read data line by line using BufferedReader；Both use StringBuffer to accumulate the read content；Both involve basic I/O operations with URL and streams
- 行为差异: Function A parses HTML to extract links via regex; Function B just reads raw text；Function A returns structured data (two vectors); Function B returns a single string；Function A handles URL base extraction and absolute link conversion; Function B does not；Function A includes debug print statements and time checks; Function B does not
- 修正建议: Incorporate dataflow analysis to capture key operations like regex matching；Train on harder negatives that share I/O patterns but differ in core logic；Use contrastive learning to distinguish functions with similar boilerplate but different semantics

### case_id=6347 FP lexical_or_api_overlap

- 方法: `doRawRequest` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends HTTP POST request with given data and returns the response body as a string.
- B 摘要: Retrieves tickets for a queue by performing an HTTP GET request, parsing ticket IDs, and fetching each ticket.
- 静态失败原因: The model may have been misled by the shared use of common Java I/O and HTTP classes (URLConnection, BufferedReader, InputStreamReader) and the pattern of opening a connection, reading lines, and closing resources, overlooking the entirely different logic and data processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they serve different purposes: one is a generic HTTP POST wrapper, the other is a specific ticket retrieval method. The token overlap is low, and the functionality is disjoint despite both using HTTP.
- 共享行为: Both functions perform HTTP requests to remote servers；Both read the response line by line using BufferedReader
- 行为差异: doRawRequest uses POST method; getTicketsForQueue uses GET；doRawRequest sends arbitrary data; getTicketsForQueue constructs query parameters for ticket search；doRawRequest returns raw string; getTicketsForQueue returns list of ticket objects；getTicketsForQueue includes error handling and multiple nested try-catch blocks
- 修正建议: Train with more negative examples that share API usage but differ in business logic；Incorporate data flow analysis to track how the HTTP response is processed and what is returned；Add attention to method names and comments for semantic context

### case_id=6348 FN partial_functionality

- 方法: `doTransfer` vs `readRemoteFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Proxies an HTTP request by forwarding it to a remote URL and returning the response.
- B 摘要: Reads a remote file line by line and returns its content as a string.
- 静态失败原因: Static BERT models rely on token overlap and shallow syntax; low Jaccard similarity and different control flow structures led to a non-clone prediction despite shared high-level semantics.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as reading data from a remote URL via HTTP, thus partial functionality overlap is sufficient for a Type-4 clone label.
- 共享行为: Both open a URL connection；Both read an InputStream from the URL
- 行为差异: A forwards request headers and body, B does not；A writes to response output stream, B returns a String；A handles multiple HTTP methods, B only reads；A checks HTTP response status and sends error if not OK, B does not
- 修正建议: Incorporate data flow analysis to capture shared URL reading pattern；Use a model that abstracts away parameters and return types；Augment with semantic role labeling for network I/O operations

### case_id=6349 FP partial_functionality

- 方法: `readTwitterFead` vs `getURLContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a hardcoded Twitter timeline URL using Apache HttpClient, checks HTTP status 200, reads response line by line into a StringBuilder without newline, logs error on failure, and catches ClientProtocolException and IOException.
- B 摘要: Fetches content from a given URL using java.net.URLConnection, determines encoding, reads line by line appending newlines, closes reader in finally, and throws IOException.
- 静态失败原因: The model may have been misled by lexical overlap (e.g., 'StringBuilder', 'BufferedReader', 'readLine', 'append', 'toString') and similar structural pattern (create reader, read lines, build string), but it overlooked the deeper differences in HTTP client library, status checking, error handling, and parameterization.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers them non-clone due to significant differences in API usage, error handling, URL flexibility, and newline behavior; these are more than mere syntactic variations and affect program behavior.
- 共享行为: Both perform an HTTP GET request to a URL and read the response content line by line, building a string from the lines.
- 行为差异: A uses Apache HttpClient, B uses java.net.URLConnection；A has hardcoded URL, B takes a parameter；A checks for HTTP status 200, B does not check status；A does not add newlines between lines, B adds newlines
- 修正建议: Improve model to distinguish between hardcoded vs parameterized URLs；Incorporate awareness of different HTTP client APIs (e.g., Apache HttpClient vs java.net)；Consider error handling patterns (logging vs throwing) as behavioral features；Use control-flow and data-flow analysis to capture structural differences

### case_id=6350 FP lexical_or_api_overlap

- 方法: `main` vs `recurseFiles`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses a Prolog file, generates adapter classes and a JAR archive.
- B 摘要: Recursively walks a directory and adds non-zip files to a ZIP archive.
- 静态失败原因: The model likely over-emphasized shared API keywords (File, IOException, FileInputStream) and both functions writing to archives, while missing the fundamental difference in algorithmic purpose and input/output semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they perform entirely different tasks: one is a code-generation main routine, the other is a file packaging utility. No functional similarity.
- 共享行为: Both perform file I/O operations (reading files, writing archives).；Both involve handling of file paths and file extensions.；Both use Java standard library classes like File, IOException, FileInputStream.
- 行为差异: Function A is a complex main method with argument parsing and multiple steps; Function B is a simple recursive utility method.；Function A generates a JAR file containing classes and serialized data; Function B produces a ZIP archive of existing files.；Function A processes only a single Prolog file; Function B processes all files in a directory tree.；Function A has extensive error handling and uses many external libraries; Function B has minimal error handling and uses Apache Commons IO.
- 修正建议: Improve training with more diverse examples to reduce reliance on common API tokens.；Incorporate structural or flow analysis to distinguish main methods from utility methods.；Use contrastive learning to emphasize semantic differences even when APIs overlap.

### case_id=6351 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `compress`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by replacing or adding a key-value pair.
- B 摘要: Concatenates multiple input files into one output file and optionally compresses it using an external tool.
- 静态失败原因: Static BERT models may focus on token-level semantic and syntactic features, and fail to capture broad structural commonalities like the overall I/O pattern. The low token Jaccard (0.1567) and different method names ('modifyApplicationMessage' vs 'compress') could lead the model to label as non-clone, despite shared underlying operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often classifies Type-4 clones as methods that perform similar file manipulation operations, even if the specific logic differs. Both functions follow a common pattern of opening files, processing data, and writing output, with similar exception handling and stream closure.
- 共享行为: Both read from input streams and write to output streams；Both handle file I/O and close streams；Both use file paths relative to a base directory
- 行为差异: Function A modifies property entries in a text file, while Function B concatenates binary/byte content；Function A uses character-based reading, Function B uses byte buffer；Function A conditionally copies a base file, Function B optionally runs external compression process
- 修正建议: Incorporate structural patterns like file I/O loops and stream handling into model features；Use program slicing to focus on core functionality beyond boilerplate

### case_id=6352 FN lexical_or_api_overlap

- 方法: `httpRequestByPOST` vs `postRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends HTTP POST request using Apache HttpClient with a list of NameValuePair parameters, returns response body as string or null on failure, setting error fields.
- B 摘要: Sends HTTP POST request using java.net.URLConnection with a HashMap of data, returns response body as string or null on failure.
- 静态失败原因: Low token Jaccard similarity (0.195) and different API vocabulary (e.g., HttpClient vs URL, NameValuePair vs HashMap) misled the static model to treat them as non-clones.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB considers broad functional similarity, accepting Type-3/Type-4 clones where the core behavior (HTTP POST with parameter encoding and response reading) is preserved despite different library usage and error handling.
- 共享行为: Both perform HTTP POST requests to a URL；Both encode parameters and send them in the request body；Both read the response and return it as a string；Both return null on error or non-success status
- 行为差异: Different HTTP client libraries (Apache HttpClient vs java.net.URLConnection)；Different input types (List<NameValuePair> vs HashMap)；Error handling: A sets error fields and returns null; B prints stack trace and returns null；A uses UrlEncodedFormEntity; B manually builds query string
- 修正建议: Improve representation to capture functional equivalence beyond lexical tokens, e.g., via data flow or API semantics；Include broader context or library usage patterns；Use more robust clone detection that abstracts over specific library calls

### case_id=6353 FN partial_functionality

- 方法: `getHTML` vs `getPagina`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a webpage with optional file writing and custom user-agent.
- B 摘要: Downloads a webpage and returns its content, with authentication and error messages.
- 静态失败原因: Static BERT models may focus on token-level overlap (Jaccard 0.28) and see differences in method signature, parameters, and control flow (file writing, authentication) as evidence of non-clone, missing the high-level semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB accepts Type-3/4 clones where the core functionality (downloading HTML) is the same despite differences in headers, error handling, and output formatting.
- 共享行为: Both fetch content from a URL and return it as a string.；Both read lines from a BufferedReader.；Both handle exceptions with try-catch.
- 行为差异: getHTML adds newlines between lines and optionally writes to file; getPagina concatenates without newlines.；getHTML uses specific User-Agent header; getPagina sets an Authenticator.；Error handling: getHTML returns empty string vs getPagina returns error description.；getHTML has additional parameters (encoding, dirPath); getPagina is static with single argument.
- 修正建议: Improve model's ability to recognize conceptual similarity even with different API usage (User-Agent vs Authenticator).；Incorporate dataflow analysis to see both ultimately return page content.；Use contrastive learning with positive pairs that have low lexical overlap but high semantic similarity.

### case_id=6354 FP boilerplate_overlap

- 方法: `getMD5` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes MD5 hash of a string and returns the hex string.
- B 摘要: Performs a complex Struts action for concept classification, involving session validation, parameter extraction, XML generation, HTTP communication, and result parsing.
- 静态失败原因: The static model likely picked up on superficial similarities (e.g., both have try-catch, return statements) and missed the vast semantic gap due to differences in length, domain, and complexity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have no meaningful semantic overlap; here, one is a utility hash and the other is a complex action, so BCB correctly identifies them as non-clones.
- 共享行为: Both have a try-catch block；Both return a value
- 行为差异: Function A is a simple hash function; Function B is a web application controller with multiple steps；Function A has no external dependencies; Function B uses session, HTTP, XML parsing；Function A has a single responsibility; Function B orchestrates many components
- 修正建议: Improve model training to better distinguish boilerplate from core logic；Use more granular token weighting to reduce impact of common patterns；Incorporate structural similarity metrics that penalize large differences in function complexity

### case_id=6355 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `setMembers`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks and anchor text from a given URL's HTML content.
- B 摘要: Retrieves component and priority options from a Trac website's newticket page and stores them in class-level arrays.
- 静态失败原因: The model overemphasized surface-level similarities (URL reading, regex, loops, collections) while missing the deeper semantic differences in purpose and output. The low token Jaccard suggests the model relied on structural overlap rather than functional equivalence.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have different purposes: one is a general link extractor, the other is a Trac-specific form option scraper. Despite shared boilerplate, the output and intent are distinct.
- 共享行为: Both open a URL and read its content using BufferedReader；Both use regex to extract substrings from HTML；Both collect extracted data into collections (Vector or array)
- 行为差异: A returns two Vectors of links and texts; B sets member arrays via side effect；A uses a generic regex to extract all hyperlinks; B looks for specific select elements；A performs URL resolution (toAbsolute); B recodes string encoding；Exception handling differs: A throws Exception, B catches specific exceptions
- 修正建议: Incorporate dataflow analysis to capture output types and side effects；Use abstract representations of function purpose (e.g., 'extract links' vs 'extract form options')；Downweight common I/O boilerplate when matching functionality

### case_id=6356 FN partial_functionality

- 方法: `copyResource` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using byte-by-byte streaming.
- B 摘要: Copies a file or directory recursively to a destination directory, with buffered streaming and skip-if-unchanged logic.
- 静态失败原因: Static models may overemphasize structural differences like recursion, different method signatures, and additional control flow (directory handling, early return), leading to low similarity detection. They may miss the core shared goal of copying data.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels any pair performing data copying via streams as clones, even if they differ in source type (URL vs File) and recursion. The core functionality of copying bytes from input to output is considered similar enough.
- 共享行为: Both copy data from a source to a destination using I/O streams.；Both handle files and streams, closing them after use.
- 行为差异: Function A only handles single file/resource, while B handles directories recursively.；Function A uses byte-by-byte reading, B uses buffered reading.；Function B has early return if file exists with same lastModified.；Function A can read from a URL, B only from File.
- 修正建议: Include data-flow analysis to track that both functions ultimately perform copy operations.；Incorporate structural information about method signatures (parameter types) to understand scope.；Use contrastive learning to recognize partial functionality similarity.

### case_id=6357 FP lexical_or_api_overlap

- 方法: `getVersion` vs `parse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Fetches a version string from a remote URL by reading the first line of the response.
- B 摘要: Parses a dataset from a file or URL, handling headers, data types, and delimiters, returning a DataSet object.
- 静态失败原因: Static BERT methods may have been misled by the shared presence of common Java I/O patterns (BufferedReader, URLConnection, openConnection, etc.), causing it to overestimate similarity. The low token Jaccard should have been a clue, but the deep learning model might have focused on the structural similarity of reading from a URL.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the methods have entirely different purposes and behavior, despite some superficial use of similar I/O classes.
- 共享行为: Both use BufferedReader to read input；Both handle I/O exceptions；Both potentially read from URLs
- 行为差异: Function A is simple and returns a version string; Function B is complex and returns a DataSet；Function A only reads one line; Function B reads multiple lines and tokenizes；Function A has minimal error handling; Function B has extensive error handling and validation；Function A does not parse structured data; Function B does
- 修正建议: Improve training data to include more negative examples with API overlap but different semantics；Incorporate more robust structural differencing；Use higher-level semantic features such as method names or return types

### case_id=6358 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file, copying a template if needed, and updates or appends a message key-value pair.
- B 摘要: Recursively copies files and directories from a source to a destination.
- 静态失败原因: Static BERT models typically rely on token overlap and structural similarity; the low Jaccard similarity and different task-level intent (property editing vs. directory copy) caused the model to predict non-clone, missing the BCB annotation bias toward broad I/O similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled this as a clone because function A contains a file copy operation that is a subset of function B's recursive file copy logic, and both involve similar low-level I/O patterns, which BCB considers as partial functional similarity (Type-4).
- 共享行为: Both perform file I/O operations (reading and writing files).；Both handle file existence checks.；Both close streams after use.
- 行为差异: Function A modifies properties file content, while B merely copies byte-by-byte without modification.；Function A handles only single file copy (only one level), whereas B is recursive for directories.；Function A includes configuration file path handling and string manipulation, absent in B.；Error handling differs: A catches Exception and prints stack trace; B throws IOException.
- 修正建议: Use data augmentation to include more partial-functionality pairs.；Incorporate fine-grained I/O operation detection to capture shared sub-tasks.；Adjust training to weight BCB-style annotations more heavily.；Consider using a model that embeds functional behavior beyond token overlap.

### case_id=6359 FN partial_functionality

- 方法: `main` vs `descargarArchivo`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts files from a ZIP archive accessed via HTTP or file URL.
- B 摘要: Copies a file from a source path to a destination path using file channels.
- 静态失败原因: Low token similarity (Jaccard=0.13) and different syntactic structures led the model to focus on surface-level differences, missing the semantic similarity of data transfer.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels as clone based on high-level functional similarity, such as file I/O operations. Both functions read an input stream and write to an output file, which fits a broad Type-3/Type-4 category.
- 共享行为: Both read from an input source and write to an output file.
- 行为差异: A handles HTTP URLs and ZIP extraction; B only handles local file copying.；A writes multiple files (ZIP entries); B writes a single file.；A uses ZipInputStream; B uses FileChannel.；A throws Exception; B catches IOException.
- 修正建议: Incorporate data-flow analysis to capture I/O operations.；Include more training examples of functionally similar but syntactically different file manipulation methods.；Use contrastive learning with positive pairs showing broad functional similarity.

### case_id=6360 FP lexical_or_api_overlap

- 方法: `copy` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file from source to destination with permission checks.
- B 摘要: Handles action events to configure application settings including file paths and preferences.
- 静态失败原因: The model may have been misled by common Java API usage (File, IOException) and similar structural patterns (ifs, try-finally) despite low token overlap, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the functions have entirely different purposes and logic.
- 行为差异: Function A is a file copy utility with no GUI interaction; function B is a GUI event handler that updates settings.；Function A has error messages and abort calls; function B saves preferences via Kontroller.；Function A reads and writes binary data; function B sets UI component values.
- 修正建议: Improve model's ability to distinguish GUI event handlers from utility functions.；Use structural features like method signatures and control flow patterns to disambiguate.；Incorporate functional role classification (e.g., IO vs GUI) as a preprocessing step.

### case_id=6361 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a newer version of jEdit by fetching a version file from a URL and comparing build numbers.
- B 摘要: Searches Google Images for a query, parses HTML to extract image URLs, and displays the first image.
- 静态失败原因: The model was misled by strong lexical and structural overlaps: both use URL, BufferedReader, readLine loop, and try-catch. Static models often focus on surface-level API calls without understanding the data transformation purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely annotates as non-clone because the high-level functionality is completely different: version checking vs. image search, despite shared low-level I/O patterns.
- 共享行为: Both open a URL connection and read content line by line using BufferedReader.；Both use try-catch blocks for exception handling.；Both perform some UI interaction at the end (hide wait cursor, enable button).
- 行为差异: Function A reads version/build info and compares strings; Function B parses HTML for image URLs and stores them.；Function A uses URL.openStream() directly; Function B uses HttpURLConnection with User-Agent header.；Function A's output is a version check message; Function B's output is setting an ImageIcon on a label.；Error handling differs: A catches IOException and uses GUIUtilities.error; B catches Exception and shows error dialog via MusicBoxView.
- 修正建议: Incorporate data-flow analysis to track how read data is used (e.g., string comparison vs. parsing/extraction).；Use contrastive learning to distinguish similar API usage with different semantic intents.；Add task-specific features like the presence of GUI components or specific string patterns (e.g., version format vs. img URL pattern).

### case_id=6362 FN benchmark_preference_bias

- 方法: `main` vs `testTrainingBackprop`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Extracts files from a ZIP archive downloaded via HTTP.
- B 摘要: Trains a neural network using a dataset loaded from a resource file.
- 静态失败原因: Static BERT/GraphCodeBERT correctly identified semantic dissimilarity via low token overlap and differing control flow, but BCB label indicates a clone, so the model's false negative is due to benchmark preference bias rather than model deficiency.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotation may have considered both as data processing pipelines with file I/O, but this is overly broad and likely an annotation error.
- 共享行为: Both involve reading from an InputStream and writing to files
- 行为差异: A decompresses ZIP entries; B trains a neural network；A uses ZipInputStream; B uses IOUtils.copy and Fann/Trainer；A processes multiple entries; B processes a single file for training；A is a main method; B is a unit test with assertions
- 修正建议: Re-evaluate BCB annotations for consistency；Use instance-level analysis incorporating broader program structure

### case_id=6363 FN partial_functionality

- 方法: `copyResource` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using byte stream I/O.
- B 摘要: Modifies a property in a locale-specific properties file, creating the file from a default if needed, using character stream I/O and property parsing.
- 静态失败原因: Low token similarity and different high-level logic caused the model to miss the abstract I/O pattern; static models struggle with long-range, multi-step semantics.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the stream copying pattern as functional similarity, classifying as Type-4 clone despite low token overlap.
- 共享行为: Both open an input stream and output stream to transfer data.；Both use a loop to read and write data until end-of-stream.；Both perform file existence checks before operations.
- 行为差异: Method A copies raw bytes; Method B copies characters and processes lines.；Method B includes property modification logic; Method A is a simple copy.；Method B has multiple stream operations and error handling with printStackTrace; Method A throws exceptions.
- 修正建议: Use dataflow or program slicing to extract core I/O behavior.；Train with contrastive pairs emphasizing functional similarity over syntactic overlap.；Incorporate source/target stream connection analysis.

### case_id=6364 FN benchmark_preference_bias

- 方法: `doGet` vs `cpFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET requests to retrieve a portal page, check visibility, log the request, render HTML output, and optionally cache the rendered page to a temporary file.
- B 摘要: Copies a file from a source path to a target path, with options for replacing existing files and specifying buffer size, handling naming conflicts.
- 静态失败原因: The static BERT model correctly predicted non-clone (0). It likely captured the low token overlap and distinct API usage, leading to a correct non-clone prediction. The BCB label is likely incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both containing file I/O (writing to file in A, copying file in B) and exception handling, but this is a very superficial similarity. The core functionality is entirely different, so BCB annotation is likely a false positive.
- 共享行为: Both involve I/O operations (reading and writing data).；Both handle exceptions related to I/O (IOException).
- 行为差异: Function A is a web request handler (servlet doGet) dealing with HTTP request/response, page retrieval, user permissions, and HTML rendering.；Function B is a utility to copy files, managing file streams, buffer allocation, and naming conventions.；A uses high-level web framework objects (HttpServletRequest, HttpServletResponse, PortalRequest, Page), whereas B uses low-level file I/O (FileInputStream, FileOutputStream).；A has complex logic for page caching and statistics, B has simple loop for reading and writing bytes.
- 修正建议: Re-annotate this pair as non-clone in BCB.；Improve BCB annotation guidelines to avoid marking functions with only superficial I/O similarity as clones.

### case_id=6365 FN partial_functionality

- 方法: `copyResource` vs `descargarArchivo`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file path to a destination file using InputStream and OutputStream.
- B 摘要: Copies a file from a selected material's path to a destination path using FileChannel.
- 静态失败原因: Low token overlap (0.076) and different API vocabulary (InputStream/OutputStream vs FileChannel) cause static models to miss the functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often annotates functions that perform the same high-level task (file copy) as clones, even if implementation details differ, aligning with Type-3/Type-4 clones.
- 共享行为: Both copy a file from a source to a destination
- 行为差异: Source can be URL or file (A) vs only file (B)；Exception handling: throws Exception (A) vs catches IOException (B)；Copying mechanism: byte-by-byte loop (A) vs FileChannel.transferTo (B)
- 修正建议: Train on more diverse API usages for same operations；Incorporate data flow or control flow analysis to capture shared behavior despite different APIs

### case_id=6366 FP boilerplate_overlap

- 方法: `readVersion` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads version, revision, and date from a classpath resource file.
- B 摘要: Performs a Google image search, parses image URLs, and updates a GUI with the first result.
- 静态失败原因: The static model likely focused on shared boilerplate patterns (URL, BufferedReader, readLine, try-catch) and overlooked the completely different functional logic and I/O destinations. The method names and overall task context were not given sufficient weight.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench typically labels clones only if they implement similar high-level functionality. These two functions have entirely different purposes (local config reading vs web scraping + GUI), so BCB would correctly label them as non-clones.
- 共享行为: Both open a URL and read lines using BufferedReader.；Both use try-catch blocks for IO exception handling.；Both close the reader in a finally block.
- 行为差异: Function A reads a local classpath resource; Function B performs an HTTP request to an external service.；Function A parses key-value pairs (Version, Revision, Date); Function B parses image URLs from HTML.；Function A sets internal fields; Function B updates GUI components (MusicBoxView).；Function A has no parameters; Function B takes a search query and a start parameter.
- 修正建议: Incorporate token-level AST or data flow features to distinguish local resource from HTTP URLs.；Use similarity of method names or comments as a negative signal.；Train with contrastive examples that have boilerplate but different semantics.；Add a classifier that explicitly checks for I/O type (file vs network) or output type (field vs GUI).

### case_id=6367 FN partial_functionality

- 方法: `sendExceptionToServer` vs `getXML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST and prints the response.
- B 摘要: Fetches content from a server via HTTP GET and returns the response string.
- 静态失败原因: The static model likely relied on low token overlap (0.225) and different method names and control flow, missing the high-level similarity in network I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may view both as 'HTTP request and response reading' functions, which are functionally related despite differing in HTTP method and specific parameters, thus labeling them as clones (Type-4).
- 共享行为: Both open an HTTP connection to a server；Both use URLEncoder.encode for parameter encoding；Both read the response line by line using BufferedReader；Both handle IOException
- 行为差异: HTTP method: POST vs GET；A sends multiple parameters (secret, version, os, etc.); B sends a single request string；A prints response to stdout; B returns the response string；A has complex parameter construction; B simple encoding
- 修正建议: Incorporate graph-based representations to capture API usage patterns (e.g., URL, BufferedReader, URLEncoder)；Use cross-function attention to identify common sub-patterns like open connection, read response

### case_id=6368 FP boilerplate_overlap

- 方法: `main` vs `clonarFichero`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter classes from a Prolog file by parsing, processing with a visitor, and writing output.
- B 摘要: Copies a file from an input stream to a destination path using file channels.
- 静态失败原因: Static BERT likely overfitted on common boilerplate patterns like try-catch, System.out.println, and file-related API calls (FileInputStream, FileOutputStream), leading to a false positive despite low token overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the two functions have no meaningful shared functionality; they perform completely different tasks with only superficial similarity in exception handling.
- 共享行为: Both use try-catch blocks for IOException handling；Both output messages to System.out
- 行为差异: Function A performs complex parsing and code generation; Function B performs simple file copying；Function A has many steps and multiple classes; Function B is straightforward with few statements；Function A returns void; Function B returns a boolean status；Different parameters and overall purpose
- 修正建议: Train on more diverse non-clone pairs with boilerplate similarity；Incorporate dataflow or structural analysis to distinguish task-level semantics

### case_id=6369 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `readIntoList`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches Twitter feed from a hardcoded URL and returns the entire response as a string.
- B 摘要: Reads HTML from a URL, extracts link text, creates JMenuItem objects with action listeners, and populates a map.
- 静态失败原因: The static BERT/GraphCodeBERT model likely focused on the lexical and API overlap (BufferedReader, readLine, try-catch) and ignored the critical differences in processing logic and final output, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically treats functions as non-clones when the core logic and output are vastly different, even if they share boilerplate I/O code. The BCB label of 0 aligns with the expectation that these functions are not similar enough to be considered clones.
- 共享行为: Both open a connection to a URL and read lines using BufferedReader；Both use a while loop to read each line；Both have try-catch blocks with e.printStackTrace()
- 行为差异: Function A returns the concatenated lines as a single String; Function B processes each line into UI components and stores them in a Map；Function A uses HttpClient; Function B uses URL.openStream()；Function A has HTTP status checking; Function B parses HTML and creates interactive menu items；Function A is for reading Twitter data; Function B is for building a menu from a list of links
- 修正建议: Incorporate data-flow analysis to track how input is transformed to output；Add attention to the specific purpose and structure of the loops and conditional branches；Use more discriminative features like return type and method signatures

### case_id=6370 FN partial_functionality

- 方法: `runScript` vs `createDialogArea`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from a URL and returns its content as a string.
- B 摘要: Creates a dialog area, reads a license file from a URL, and displays it in a browser or text widget.
- 静态失败原因: Low token overlap and different method names; BERT focuses on overall method purpose and signature, which differ significantly, and B has many GUI-specific tokens that dilute similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider reading from a URL as shared functionality, thus labeling as Type-3/4 clone despite different overall purposes.
- 共享行为: Both open an InputStream from a URL and read data
- 行为差异: A reads char-by-char, B reads line-by-line；A does not close streams, B does；A returns string, B sets text in GUI；A is a simple utility, B involves GUI creation
- 修正建议: Incorporate structural matching of common subroutines；Use data flow analysis to detect I/O patterns

### case_id=6371 FN partial_functionality

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copy a file from source to destination using byte buffer.
- B 摘要: Launch a NexOpen project configuration, involving XML processing, properties, and file copying as a sub-step.
- 静态失败原因: Static BERT models rely on token-level and structural similarity, which are very low (token Jaccard 0.0516). They likely overlook the partial functional overlap of the inner file copy subcomponent because it is a small part of the larger method.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a Type-4 clone because both functions contain the core semantics of copying data from an input stream to an output stream, even though the overall purposes differ.
- 共享行为: Both read from an input stream and write to an output stream (file copy operation).
- 行为差异: copyFile is a pure file copy utility; launch is a complex project launch with many other operations.；launch includes conditionals, XML handling, property setting, and project refresh.；The file copy in launch is only a small part of the overall functionality.
- 修正建议: Use slice-based or component-level clone detection to identify similar sub-functionality.；Incorporate dataflow analysis to capture common subcomputations.；Enhance attention mechanisms to focus on key operational blocks.

### case_id=6372 FP lexical_or_api_overlap

- 方法: `decodeFileToFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Decodes a Base64-encoded file and writes the decoded content to another file.
- B 摘要: Handles action events from UI components to set user preferences for external tool paths and other settings.
- 静态失败原因: Static BERT may have been misled by lexical overlap of common APIs (e.g., 'File', 'InputStream', 'OutputStream') and treated them as functionally similar, while ignoring the vastly different control flow and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the functions are completely unrelated: one is a utility for file decoding, the other is a UI event handler. There is no functional similarity even under broad Type-4 criteria.
- 行为差异: A performs file I/O with Base64 decoding; B handles UI events and updates application preferences.；A returns a boolean success flag; B is an event handler with no return value.；A uses InputStream/OutputStream; B uses JFileChooser, Suku.kontroller, etc.
- 修正建议: Include more diverse non-clone pairs with similar API tokens but different semantics in training.；Incorporate structural or data-flow analysis to distinguish utility methods from event handlers.；Emphasize method names and signatures as strong indicators of semantic difference.

### case_id=6373 FN partial_functionality

- 方法: `getZipAsFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Extracts a DigitalObject's content stream into a temporary file and returns that file.
- B 摘要: Launches a NexOpen Eclipse project configuration by processing pom files, setting Hibernate properties, and scheduling an install action.
- 静态失败原因: Static BERT/GraphCodeBERT failed to identify this as a clone because it focused on the overall functionality and low lexical overlap, which are insufficient for BCB's broad partial functionality similarity criteria. The model likely requires more explicit guidance to recognize that even small common patterns (data copying) can be considered clones in BCB's annotation scheme.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to both utilizing IOUtils for copying streams and having similar exception handling patterns, but this is a surface-level similarity and does not indicate functional similarity.
- 共享行为: Both read data from an input stream and write to an output stream using IOUtils.；Both handle IOException and FileNotFoundException (or similar) in catch blocks.
- 行为差异: Function A is a simple utility to save a stream to a file; Function B is complex Eclipse launch delegate with multiple configuration steps.；Function A returns a File; Function B is void and does not return a file.；Function A operates on a DigitalObject; Function B operates on Eclipse workspace resources.；Function B involves XML DOM handling, property setting, and project scheduling; Function A has none.
- 修正建议: Incorporate fine-grained functional similarity detection, e.g., recognizing common I/O patterns as potential clone indicators.；Consider using alignment of subroutines or data-flow graphs to capture partial functionality overlaps.

### case_id=6374 FP partial_functionality

- 方法: `handleHandshake` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Validates a Minecraft handshake packet and optionally authenticates with a session server.
- B 摘要: Downloads a file from a URL to a local destination with progress reporting.
- 静态失败原因: Static BERT models may have been misled by overlapping low-level API calls (URL, openStream, BufferedReader/BufferedInputStream, close), causing them to overlook the divergent semantic intent and conditional logic.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels non-clone because the functions have entirely different high-level purposes (handshake vs. file download) and distinct control flow, despite both involving network I/O.
- 共享行为: Both open a URL connection and read from an input stream；Both handle HTTP responses and close streams
- 行为差异: Function A validates server key and performs authentication; B downloads file to disk；Function A uses conditional logic based on packet content; B loops to read chunks and track progress；Function A uses BufferedReader for text; B uses BufferedInputStream for binary data
- 修正建议: Incorporate method name embeddings to capture intent；Use dataflow analysis to track how input/output values are used；Apply contrastive learning with negative samples that share API patterns but differ in functionality

### case_id=6375 FP lexical_or_api_overlap

- 方法: `loadExistingAntlibs` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads antlib resources from classloader, reads URIs from a resource file, resolves them, and loads each ant library.
- B 摘要: Downloads a file from a given URL to a local destination with progress updates.
- 静态失败原因: The model was likely misled by common vocabulary and structural patterns (URL, InputStream, BufferedReader, IOException) and the loop structure, ignoring the overall functionality difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled non-clone because the functions have completely different semantics and purpose, despite some I/O API overlap.
- 共享行为: Both involve reading from URLs；Both use I/O streams (InputStream, BufferedReader, BufferedOutputStream)
- 行为差异: Different purposes: loading ant libraries vs. downloading file；Different output: one calls loadAntLib, the other writes to file；Different error handling: one throws RuntimeException, other throws Exception；Progress reporting only in function B
- 修正建议: Incorporate method name similarity or purpose mining；Use AST-based or data-flow analysis to capture actual intent；Add global context like class/package names

### case_id=6376 FP lexical_or_api_overlap

- 方法: `getRequestContent` vs `issueCommandToServer`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens an HTTP connection to a given URL and returns the first line of the response.
- B 摘要: Sends a POST command with parameters to a server and returns the entire response.
- 静态失败原因: Static BERT models likely focused on lexical overlap (URL, BufferedReader, InputStreamReader) and similar structural boilerplate, missing the critical difference in data flow (output stream write) and looping behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because these functions have different purposes (GET vs POST), different signatures, and different control flow (single line read vs loop read). Even though both involve HTTP, the overall functionality is distinct.
- 共享行为: Both open an HTTP connection；Both read from the input stream
- 行为差异: A performs a GET (no output), B performs a POST (writes command and capsule data)；A reads only one line, B reads all lines in a loop；Different parameter lists (A: single URL string, B: command and ChangeCapsule)；A uses HttpURLConnection, B uses URLConnection
- 修正建议: Incorporate data flow analysis to distinguish read-only vs read-write connections；Require match on number of parameters and their types；Use control flow graph features to differentiate single read vs loop read；Add awareness of HTTP method semantics (GET vs POST)

### case_id=6377 FN lexical_or_api_overlap

- 方法: `unJar` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Extracts a specific entry from a JAR file and writes it to disk.
- B 摘要: Builds an entire website by transforming XML, reading multiple files, and writing generated pages.
- 静态失败原因: The low token Jaccard similarity (0.045) and the vast difference in length and complexity likely caused the static BERT model to miss any potential clone relationship that BCB annotators perceived, as the model relies heavily on lexical and structural overlap.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled these as clones due to a broad interpretation of Type-4 (functionally similar) where both functions read from one location and write to another, possibly involving file extraction and generation. However, this seems like a stretch.
- 共享行为: Both perform file I/O operations (reading from input streams and writing to files).
- 行为差异: A is a simple single-file extraction; B is a complex multi-step site generation with XML transformation and string replacement.；A handles one JAR entry; B iterates over many pages and performs numerous file operations.；A returns a file path; B returns void and writes multiple output files.
- 修正建议: Incorporate deeper semantic analysis beyond token overlap.；Use code summarization to capture high-level intent.；Consider the possibility of noisy BCB annotations in training data.

### case_id=6378 FP lexical_or_api_overlap

- 方法: `handler` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts substrings from web page lines based on include/from/to patterns and updates a map.
- B 摘要: Reads a service configuration file to instantiate a FrameworkFactory class.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on similar API usage patterns (URL, BufferedReader, InputStreamReader) and control flow, missing the different semantic purposes and data transformations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotation likely considered the overall functionality (web scraping vs service loading) as different, so not clones.
- 共享行为: Both use URL to open a stream；Both wrap with BufferedReader and read lines；Both close the reader
- 行为差异: A modifies a map parameter; B returns a new object；A has empty exception handling; B throws exception；A loops over all lines and all map entries; B stops at first non-comment line；A does substring extraction; B does class loading
- 修正建议: Use better data-flow analysis to track data transformations；Consider return type and method signature as discriminative features；Incorporate contextual information like method names and comments

### case_id=6379 FN benchmark_preference_bias

- 方法: `createOutputStream` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a zip file, copies all entries except 'content.xml', then adds a new 'content.xml' entry and returns a BufferedWriter to the output zip.
- B 摘要: Retrieves a resource as an InputStream, caching the stream to a local file if not already cached, updating cache based on modification times, and returning an InputStream to the cached file or null on error.
- 静态失败原因: Static BERT models rely on token overlap and syntactic structure; the low Jaccard similarity (0.123) and different method signatures led to correct non-clone prediction, but BCB's broader semantic criteria might label them as clones, causing a false negative for BCB.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'resource retrieval' or 'stream processing' clones based on the use of streams and file system operations, despite differing domain specificity.
- 共享行为: Both involve file I/O operations with streams；Both use buffered streams for reading/writing；Both handle exceptions with try-catch
- 行为差异: A processes zip entries specifically, while B handles HTTP caching and remote resources；A writes to a zip output file, B returns an InputStream for reading from cached file；A uses explicit charset conversion, B does not；B has caching logic and URL handling, A does not
- 修正建议: Incorporate high-level semantic patterns for I/O stream operations；Use data augmentation with non-clone pairs that have low lexical overlap but similar context；Fine-tune with explicit supervision on partial functionality clones

### case_id=6380 FP lexical_or_api_overlap

- 方法: `get` vs `GetResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP GET request with custom headers and decodes the response lines (skipping comments) into an array of GameRecord objects.
- B 摘要: Sends an HTTP GET request (no custom headers) and concatenates all response lines into a single string.
- 静态失败原因: High token overlap (0.4) due to common HTTP GET boilerplate (URL, HttpURLConnection, BufferedReader, etc.) and method name 'get', causing the model to overlook semantic differences in response processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions serve distinct purposes (game record decoding vs string concatenation) and have different signatures and output types.
- 共享行为: Establish HttpURLConnection, set method to GET, and check for HTTP_OK；Read response line by line using BufferedReader
- 行为差异: A takes lat, lon, count parameters; B takes a URL object；A sets custom request headers; B does not；A filters out lines starting with '#' and decodes into GameRecord; B concatenates all lines into a string；A returns an array; B returns a string
- 修正建议: Incorporate data-flow analysis to track how the response is processed after reading；Include method signature and surrounding class context；Use statement-level embeddings that capture semantic operations like decoding vs concatenation

### case_id=6381 FP boilerplate_overlap

- 方法: `fetchUrl` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches the entire content of a given URL and returns it as a string.
- B 摘要: Extracts a fullscreen video URL from a YouTube page by parsing the response for specific parameters.
- 静态失败原因: Static BERT/GraphCodeBERT models may over-rely on lexical and structural similarities (e.g., both use URL, BufferedReader, try-catch) and miss the semantic gap caused by different overall goals and data processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the two functions perform fundamentally different tasks despite sharing boilerplate URL-reading code; the core logic (page parsing vs. simple concatenation) is distinct.
- 共享行为: Both use java.net.URL to open a connection and read lines via BufferedReader；Both handle exceptions with try-catch and return a string on failure
- 行为差异: Function A returns the full page content; Function B returns a constructed URL after parsing；Function A takes a URL string as parameter; Function B uses an instance variable ytUrl；Function B has UI updates (progress bar) and debug prints; Function A has no side effects；Function B searches for a specific line containing 'fullscreenUrl'; Function A reads all lines
- 修正建议: Train with more diverse non-clone pairs that share low-level API usage but differ in high-level intent；Incorporate control-flow and data-flow features that capture output transformation；Use contrastive learning to emphasize semantic differences despite similar token sequences

### case_id=6382 FN boilerplate_overlap

- 方法: `addIDs` vs `import_hints`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches metabolite data from a web service and populates a row object with various IDs and molecular weight.
- B 摘要: Imports puzzle hints from a file or URL, parsing coordinates and rotation to place pieces on a board.
- 静态失败原因: Static BERT models rely on token-level patterns and may overgeneralize from the shared URL-opening and parsing structure, failing to recognize the fundamental domain and behavior differences.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might consider these Type-4 clones due to structural similarity in URL reading and parsing boilerplate, despite entirely different semantics, reflecting a broad interpretation of clone.
- 共享行为: Open a URL/stream and read lines with BufferedReader；Parse input lines with tokenization or string splitting；Handle IOException and return a default value on failure
- 行为差异: Different domains: metabolomics vs puzzle game hints；Different parsing logic: HTML scraping vs simple token parsing；Different outputs: return score vs boolean, set fields on row object vs place pieces on board
- 修正建议: Enrich training data with diverse domain examples having similar boilerplate but different logic；Incorporate data flow analysis to capture variable usage and function calls；Use cross-file context to detect incompatible method signatures and return types

### case_id=6383 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `loadExistingAntlibs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads integers from a resource file and returns a set of them.
- B 摘要: Loads ant libraries by reading package names from classpath resources and loading corresponding antlib XML files.
- 静态失败原因: The model likely relied on the high lexical and structural overlap in the boilerplate resource-reading pattern (try-catch, openStream, readLine loop) and missed the critical difference in how each line is processed (integer vs. package name).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the core functionality differs: one extracts numeric IDs, the other loads ant libraries from package names. The shared IO pattern is considered boilerplate, not sufficient for clone.
- 共享行为: Both read from a resource file using URL and openStream.；Both use BufferedReader/LineNumberReader to read lines in a loop.；Both have try-catch for IO exceptions.
- 行为差异: A reads from a single resource determined by parameter; B iterates over multiple resources for a fixed resource name.；A parses each line as an integer; B treats each line as a package name and loads an antlib.；A returns a HashSet; B is void and calls loadAntLib.；Error handling: A prints stack trace; B throws RuntimeException.
- 修正建议: Focus model attention on the data transformation inside the loop rather than the loop structure.；Use dataflow analysis to track how line content is used.；Distinguish between reading primitives (integers) and complex resource loading (antlib).

### case_id=6384 FN partial_functionality

- 方法: `httpRequestByPOST` vs `wordFrequency`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs an HTTP POST request with parameters and returns the response body as a string, handling errors and setting error codes.
- B 摘要: Retrieves a webpage content by URL, searches for a word frequency pattern, and returns the matched frequency or 0.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on token-level embeddings and may miss the structural similarity due to low lexical overlap (Jaccard=0.225), different method names, and different library usage (HttpClient vs URL). The model likely overfitted on surface-level features.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both follow a common pattern of network I/O: constructing a URL, opening a connection, reading line-by-line, and handling exceptions. The steps are structurally similar despite different specific APIs and output types.
- 共享行为: Both open an HTTP connection and read the response line by line.；Both handle IOExceptions with basic error reporting.；Both use BufferedReader and InputStreamReader for reading.
- 行为差异: httpRequestByPOST uses POST method with parameters; wordFrequency uses GET via URL.openStream().；httpRequestByPOST returns full response string; wordFrequency returns an integer frequency or 0.；httpRequestByPOST uses HttpClient and HttpPost; wordFrequency uses URL class.；wordFrequency searches for a regex pattern in each line; httpRequestByPOST simply reads all lines.
- 修正建议: Incorporate dataflow or control-flow graphs to capture structural patterns.；Train on examples where methods share common I/O design patterns despite different APIs.；Use AST-based or graph-based representations to abstract over library specifics.

### case_id=6385 FN partial_functionality

- 方法: `main` vs `makeBackup`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its ZIP entries to files in the current directory.
- B 摘要: Copies files from a source directory to a destination directory, creating the directory if needed and preserving timestamps.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on lexical and syntactic similarity. With low token Jaccard (0.206), different method names, parameters, and overall structure, the model likely detected no significant overlap, leading to a non-clone prediction despite the shared underlying behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a clone because both functions perform the fundamental operation of copying binary data from an input stream to an output stream, which is a common pattern in file I/O. The differences in source (ZIP vs. local) and destination (extracted files vs. copied files) might be considered superficial variations.
- 共享行为: Both read bytes from an input source and write to an output file.；Both use while loops to read and write bytes until end of stream.；Both close input and output streams after use.
- 行为差异: A reads from a URL (HTTP or file) using ZipInputStream; B reads from local directory using FileInputStream.；A extracts ZIP entries; B copies files directly without compression.；A creates output files with entry names; B preserves original filenames in a destination directory.；A uses buffered output (BufferedOutputStream) and a fixed buffer size; B reads/writes byte by byte.
- 修正建议: Enhance model with data flow analysis to capture read-write patterns.；Include training examples of file I/O operations with diverse contexts.；Use contrastive learning to emphasize semantic similarity over lexical similarity.

### case_id=6386 FN partial_functionality

- 方法: `read` vs `postXml`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens a URL or file input stream, reads data, and returns a status code.
- B 摘要: Sends an HTTP POST request with XML payload, reads the response, and returns the response body as a string.
- 静态失败原因: The model likely relied on low lexical overlap (Jaccard=0.135) and different API usage (BufferedInputStream vs HttpURLConnection), missing the abstract semantic similarity of reading from a resource.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both perform I/O to retrieve data from a URL (or file) and handle exceptions, falling under broad Type-4 functional similarity in network I/O operations.
- 共享行为: Both open a URL connection and read data from an external resource.
- 行为差异: A can also read from local files; B only from HTTP URLs.；A uses GET-like stream opening; B uses POST with custom headers and body.；A returns an int status; B returns a String response.；A rethrows IOException by setting status; B wraps IOException into RuntimeException.
- 修正建议: Incorporate higher-level functional semantics via program summarization or code abstractions.；Use data-flow analysis to detect that both functions read from a network resource.

### case_id=6387 FN benchmark_preference_bias

- 方法: `lookupFutureEvents` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Fetches and parses a list of future events from the Meetup API.
- B 摘要: Registers a new user by encoding password, calling a forum API, persisting to database, and sending confirmation email.
- 静态失败原因: The model correctly identified that the core functionalities are unrelated, but it failed to recognize that BCB's benchmark includes clones based on partial functional similarity, leading to a false negative relative to BCB.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label them as clones because both functions share a common sub-task of making an HTTP request and reading the response, which is considered sufficient for Type-4 clone under BCB's broad criteria.
- 共享行为: Both perform an HTTP GET request using URL and BufferedReader.；Both handle IOException.；Both use StringBuilder to construct the request URL.
- 行为差异: Different input/output types: String→List<Event> vs Object→boolean.；Different external APIs: Meetup vs phpBB.；Different data processing: JSON parsing vs setting user fields and DB persistence.；Error handling: throws GtugsException vs return false or throw RuntimeException.
- 修正建议: Adjust the model to match BCB's annotation criteria by weighing boilerplate code more heavily.；Use task-specific heuristics to identify shared sub-tasks even when main purposes differ.

### case_id=6388 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for new version by reading a URL, comparing build numbers, and showing UI messages.
- B 摘要: Fetches a version string from a URL and returns it without UI interaction.
- 静态失败原因: Static BERT models often rely on token overlap and common API patterns. Both functions use similar I/O patterns (URL, BufferedReader, readLine) and variable names like 'version', leading to false similarity despite different overall behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB's annotation guidelines require high semantic equivalence; the significant difference in UI interaction and overall purpose (version check vs. simple retrieval) makes them non-clones.
- 共享行为: Open a URL connection；Read lines from input stream；Extract version information from the read lines
- 行为差异: doVersionCheck shows/hides wait cursor, getVersion does not；doVersionCheck compares build versions and shows UI messages, getVersion only returns the version string；doVersionCheck handles IOException specifically, getVersion catches Exception broadly
- 修正建议: Incorporate control flow and data dependency analysis；Use graph-based models (e.g., GraphCodeBERT) to capture structural differences；Add context like method return type and calls to external methods (e.g., GUIUtilities)

### case_id=6389 FP boilerplate_overlap

- 方法: `getRequestContent` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads first line from a given URL using HttpURLConnection and returns it.
- B 摘要: Parses a YouTube page to extract video_id and t, then constructs and returns a fullscreen video URL.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the common token sequence of URL connection and BufferedReader usage, ignoring the distinct control flow and data transformations that differentiate the functions.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels based on functional similarity; these functions share only trivial boilerplate (URL opening/reading) but have entirely different purposes and outputs, so BCB annotates them as non-clones.
- 共享行为: Both create a URL object and open a connection.；Both use BufferedReader to read from an InputStream.
- 行为差异: Function A returns the first line; function B searches for a specific line containing 'fullscreenUrl' and extracts parameters.；Function A uses HttpURLConnection; function B uses URLConnection.；Function A has no side effects; function B prints debug output and updates a progress bar.；Function A takes a URL argument; function B uses an instance variable ytUrl.
- 修正建议: Enhance training with negative examples that share API calls but differ in logic.；Incorporate dataflow analysis to distinguish variable usage and transformations.；Use larger context windows or graph-based methods to capture overall method semantics.

### case_id=6390 FN benchmark_preference_bias

- 方法: `fileDownload` vs `addQDInformation`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL and saves it to a local file.
- B 摘要: Reads a configuration file (local or remote) and updates internal project data structures.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone due to low token overlap (Jaccard 0.14) and clear semantic difference, aligning with our analysis.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both involving network file access and I/O operations with similar API usage (URL, BufferedReader), despite differing overall functionality.
- 共享行为: Both use URL and BufferedReader for I/O；Both read data from an external source (file or URL)；Both contain try-catch blocks for IOException
- 行为差异: Function A writes to a file; Function B updates object fields；Function A downloads and saves; Function B parses and stores data；Functions have entirely different outputs: a file vs. internal state
- 修正建议: Review BCB annotation criteria for Type-3/Type-4 clones；Consider whether shared I/O patterns alone justify clone label in specific benchmarks；Ensure benchmark annotations align with semantic equivalence or functional similarity

### case_id=6391 FP lexical_or_api_overlap

- 方法: `sendPost` vs `getUser`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: sendPost sends an HTTP POST request and returns the response body as a string.
- B 摘要: getUser retrieves a user by login from a database or a config file, returning a User object.
- 静态失败原因: Static BERT likely overemphasized common structural patterns (try-catch, BufferedReader, while loop) and ignored distinct API calls and logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functional similarity; these functions have no overlapping functionality or purpose.
- 共享行为: Both use BufferedReader to read lines from an input stream.；Both use try-catch blocks to handle exceptions.；Both return a result (String or User).
- 行为差异: sendPost performs an HTTP network operation; getUser does database/file lookup.；sendPost uses PrintWriter to send data; getUser uses StringTokenizer to parse lines.；Exception handling differs: MsgPrint.showMsg vs printStackTrace.
- 修正建议: Incorporate deeper semantic features like API call sequences and data flow.；Consider method names and context to differentiate network I/O from data retrieval.；Use contrastive learning to separate similar boilerplate but different semantics.

### case_id=6392 FN long_range_semantics

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Builds a website for editing by reading XML pages, transforming them, and writing output files.
- 静态失败原因: Low token Jaccard (0.07) indicates little lexical overlap; B is very long, and the model may focus on local tokens like FileInputStream but miss the overall semantic difference.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: None
- 共享行为: Both involve file I/O operations (read and write files)；Both use FileInputStream and write to files
- 行为差异: A is a simple file copy; B involves complex XML transformation, multiple file reads/writes, and string manipulation；A returns boolean; B returns void and throws multiple exceptions；A uses FileChannel; B does not；A is static; B is an instance method
- 修正建议: Use models with better long-range context understanding；Incorporate dataflow or control flow analysis；Improve training data with more diverse functional types

### case_id=6393 FN partial_functionality

- 方法: `getContent` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Executes an HTTP request and returns the response body as a string.
- B 摘要: Opens a stream from a URL or file and returns a status code indicating success or failure after reading.
- 静态失败原因: Static BERT models rely on token overlap and structural similarity. The low Jaccard index (0.077) and different API usage (HttpClient vs URL/File) lead the model to classify as non-clone. The model may miss the broad functional similarity of 'reading from source' because it focuses on lexemes and control flow patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered these as Type-4 clones because both functions are high-level routines that read data from a source (network or file) and involve opening a stream and reading. Despite different return types and specific mechanisms, the core idea of fetching content from a resource is similar.
- 共享行为: Both read data from a source (HTTP response or URL/file)；Both use buffered input streams；Both handle I/O exceptions
- 行为差异: Different return types: String vs int；Different input: HttpUriRequest vs String name；A uses HttpClient, B uses URL/FileInputStream；B involves detecting URL scheme
- 修正建议: Use a graph-based representation to capture data flow and call dependencies；Incorporate type information to understand return types；Use a contrastive learning approach that focuses on functional intent rather than exact tokens；Employ code summarization to capture high-level purpose

### case_id=6394 FP boilerplate_overlap

- 方法: `init` vs `get`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads controller classes from a registry file, skipping commented lines.
- B 摘要: Fetches game records from an HTTP API, skipping lines starting with '#'.
- 静态失败原因: The static model likely over-emphasized the lexical overlap (e.g., while loop, BufferedReader, skipping '#' lines) and neglected the semantic differences in the output and the source of input, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the high-level intent differs significantly: one is a configuration loading routine, the other is an HTTP client fetching game data. The shared I/O pattern is common boilerplate and does not imply functional similarity.
- 共享行为: Reads lines from an input stream using BufferedReader；Skips lines that start with '#'；Handles IOException with stack trace printing
- 行为差异: Source of input: file-based (A) vs HTTP-based (B)；Output: adds classes to internal registry (A) vs returns array of GameRecord objects (B)；Error handling: A catches both IOException and ClassNotFoundException; B only catches IOException；Purpose: initialization (A) vs. data retrieval (B)
- 修正建议: Incorporate data flow analysis to distinguish between file I/O and network I/O；Add training examples that expose models to similar boilerplate but different semantics；Use structural differencing to highlight differences in method signatures and external API calls

### case_id=6395 FP lexical_or_api_overlap

- 方法: `readData` vs `convert`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Initializes multiple sets and a map from comma-separated string variables using StringTokenizer, building a look-up table for valid input sequences.
- B 摘要: Converts an ACRNEMA stream file to DICOM format by parsing header, validating pixel data length, and writing output with metadata and pixel data.
- 静态失败原因: The model likely over-relied on lexical matches such as the repeated use of 'StringTokenizer', 'HashSet', 'add', 'put', and while-loop structures. The token Jaccard similarity is low (0.079), but the presence of common API patterns may have misled the model into perceiving structural similarity. Additionally, static models may lack the ability to capture high-level semantic context across different application domains.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels as non-clone when functions serve entirely different purposes, even if they share some generic API usage like StringTokenizer or loops. The lack of any shared input/output behavior and completely different domains (text parsing vs. image file conversion) strongly indicate non-clone.
- 行为差异: Function A is a data initialization routine for a transliteration utility; Function B is a file format conversion method for DICOM images.；Function A operates on internal string fields; Function B operates on file I/O streams.；Function A populates set and map structures; Function B reads and writes binary data with specific byte-level operations.；Function A has no return value or output parameters; Function B writes to a destination file.
- 修正建议: Train models to incorporate type information and dataflow analysis to distinguish between initialization and file conversion.；Use contrastive learning to improve discrimination between functions with similar API calls but different semantics.；Incorporate documentation or method-level summaries to provide broader context.

### case_id=6396 FP partial_functionality

- 方法: `readData` vs `CopyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses comma-separated string constants into multiple sets and a valid input sequences map, and reads a structured file for Tibetan character processing with error handling.
- B 摘要: Copies a file from source to destination using FileChannel, creating parent directories if needed, and returns the destination path.
- 静态失败原因: The long and partially truncated code of A may have led the model to falsely associate file reading aspects (though different) with B's file copying, despite low token overlap. The model likely overfitted on superficial file-related keywords like 'IOException' or 'File'.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would label these as non-clones because they implement entirely different functionalities with no semantic similarity despite both involving file or data processing.
- 行为差异: Function A processes string constants and parses a file with multiple columns for Tibetan character encoding, while B copies a file.；Function A populates several sets and maps; B performs file I/O and returns a string.；Function A uses StringTokenizer and file reading with error handling on column counts; B uses FileChannel and checks directory existence.
- 修正建议: Improve context understanding to distinguish different file operations (parsing vs. copying).；Enhance representation to capture high-level purpose rather than token-level overlaps.；Incorporate data flow analysis to separate string parsing from file I/O.

### case_id=6397 FN partial_functionality

- 方法: `loadMFileViaWeb` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Loads a MATLAB file from a URL, reads its content line by line, and parses it into a UserFunction object.
- B 摘要: Reads data from comma-separated strings and a file (tibwn.ini) to populate sets and hash maps for Tibetan transliteration.
- 静态失败原因: Low lexical overlap (Jaccard=0.066), domain-specific vocabulary (e.g., MATLAB, tibetan, wylie), long code exceeding typical model context, and focus on surface tokens rather than high-level structural similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers broad functional similarity (Type-4) as clones; both functions perform 'read and parse data from external source into internal structures', which fits that category despite domain differences.
- 共享行为: Both read textual data from an external source (URL or file)；Both parse the input line by line；Both populate internal data structures (UserFunction vs sets/maps)
- 行为差异: Different domains (MATLAB loading vs Tibetan transliteration initialization)；Different source types (URL stream vs file and string constants)；Different output (returns a UserFunction vs populates global variables)
- 修正建议: Incorporate AST-based structural features；Use data flow analysis to capture input-output patterns；Train models with hierarchical or graph representations (e.g., GraphCodeBERT with data flow edges)

### case_id=6398 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter timeline JSON from a fixed URL using HttpClient and returns the concatenated response as a string.
- B 摘要: Reads a tab-separated file from a given URL using URL.openStream and Scanner, extracts id and description, and adds them to a Vector passed as parameter; no return value.
- 静态失败原因: The static model likely overemphasized structural similarities (both reading from URLs, using loops, exception handling) and missed the critical differences in return type, parsing logic, and method signatures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because their functionality is fundamentally different: one fetches a specific Twitter JSON and returns it, the other parses a tabular format and modifies a data structure. The low token Jaccard (0.1477) also supports non-clone.
- 共享行为: Both functions connect to a URL and read textual data line by line；Both use try-catch blocks to handle I/O exceptions
- 行为差异: Function A returns a string; Function B is void and populates an input Vector；Function A uses Apache HttpClient with status code checking; Function B uses URL.openStream directly；Function A concatenates all lines without parsing; Function B parses tab-separated fields；Function B closes the InputStream in a finally block; Function A does not explicitly close resources
- 修正建议: Incorporate dataflow analysis to distinguish output usage (return vs. side-effect)；Include method-level semantics such as return type and parameter effects；Use AST-based or graph-based matching that captures the core functionality beyond boilerplate

### case_id=6399 FN partial_functionality

- 方法: `createDialogArea` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Creates a dialog area with SWT components, reads a license file from a URL, and displays its content in a browser or text widget.
- B 摘要: Performs an HTTP POST request, reads the response content from the input stream, and returns it as a string, handling errors with status codes.
- 静态失败原因: The static BERT model likely overemphasized the high-level API and domain differences (SWT vs HTTP) and missed the shared low-level IO pattern, leading to a false negative prediction relative to BCB's broad clone definition.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones because both perform a common data-reading pattern (InputStream -> BufferedReader -> line-by-line appending to StringBuffer), which could be considered a Type-4 (semantic) clone in a very broad sense, despite different high-level purposes.
- 共享行为: Both use BufferedReader to read lines from an InputStream and append them to a StringBuffer.；Both handle IOException in try-catch blocks.
- 行为差异: Function A creates a UI dialog with SWT widgets; Function B performs network I/O with Apache HttpClient.；Function A reads a resource file within the application bundle; Function B reads an HTTP response.；Function A returns a Control (Composite); Function B returns a String.；Function A handles UI-specific exceptions; Function B handles HTTP status codes and sets error fields.
- 修正建议: Train the model on cross-domain clone examples that share common sub-patterns.；Incorporate dataflow embeddings to recognize similar I/O sequences.

### case_id=6400 FN benchmark_preference_bias

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file using FileChannel transferTo.
- B 摘要: Builds a website for editing by processing XML, transforming, and writing output files.
- 静态失败原因: Static BERT models correctly identified non-clone due to low lexical and structural overlap; they did not fail, but the BCB annotation is questionable.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones because both involve file I/O and data transfer from input to output, ignoring the vastly different complexity and purpose.
- 共享行为: Both perform file input and output operations.
- 行为差异: Function A is a simple file copy; function B is a complex site generation with XML transformation, multiple file reads/writes, and string manipulation.
- 修正建议: Re-evaluate BCB annotation for this pair; consider removing or correcting the clone label.

### case_id=6401 FN partial_functionality

- 方法: `doGet` vs `unzip`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request for a web page, including page lookup, visibility check, logging, and optional caching of the rendered page to a file.
- B 摘要: Unzips a ZIP file to a target directory, handling directory creation and file extraction with logging and proper resource management.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token-level similarity and structural features; the low Jaccard similarity (0.12) and distinct domain-specific keywords (servlet, page vs zip, unzip) caused it to correctly identify them as non-clones, aligning with the ground truth functional difference.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to the presence of file I/O, logging, and exception handling patterns, which could be seen as partial functionality similarity in a broad Type-4 sense, even though the core tasks are entirely different.
- 共享行为: Both use logging (myLogger.info vs LOG.info) for progress information.；Both involve file I/O operations (writing to files, directory creation).；Both use try-catch-finally blocks for exception handling and resource cleanup.；Both check conditions before proceeding (e.g., file existence, user visibility).
- 行为差异: Function A is a servlet handler processing HTTP requests; function B is a utility method for file decompression.；Function A deals with page objects, user permissions, and caching; function B deals only with file system operations.；Function A's file writing is optional and for caching; function B's file writing is the core task (extracting zip entries).；Inputs: A receives HttpServletRequest/Response; B receives File and ZipFile objects.
- 修正建议: Ensure that BCB annotation guidelines clearly distinguish between true functional clones and coincidental structural similarities.；Incorporate semantic or functional similarity measures that go beyond token overlap to capture overall purpose.；Consider domain-specific filtering to avoid false positives from boilerplate patterns.

### case_id=6402 FP lexical_or_api_overlap

- 方法: `getDatasetsList` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves and caches a list of dataset names from a server URL.
- B 摘要: Downloads a vector tile and processes it into a geometry collection for a tile layer.
- 静态失败原因: The model focused on overlapping lexical tokens (URL, BufferedReader, readLine, IOException) and synchronization, missing semantic differences in method signature, return type, and core logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely annotated as non-clone because the high-level functionality differs (data listing vs tile processing) despite shared low-level I/O patterns.
- 共享行为: Open URL and read lines with BufferedReader；Handle IOException；Use synchronization for thread safety
- 行为差异: Function A caches results; function B does not；Function A builds a list of strings; function B builds a GeoJSON string and parses into geometry objects；Different return types: List<String> vs void；Function B has additional protocol handling and complex post-processing
- 修正建议: Incorporate method name and return type features；Use data flow analysis to distinguish caching vs processing；Train on more diverse examples of I/O boilerplate in different contexts

### case_id=6403 FN partial_functionality

- 方法: `dump` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies content from a source file to a target file using byte-by-byte I/O.
- B 摘要: Retrieves a resource, possibly caching it by downloading from a URL to a local file, and returns an InputStream for the cached file.
- 静态失败原因: The functions have low lexical overlap (Jaccard 0.167) and different API usage, so a token-based model likely fails to recognize the structural similarity of the copy loop. The clone is a small semantic fragment embedded in larger, diverse contexts.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both functions contain the core pattern of copying data from an input stream to an output stream, which is a common functionality. The overall purpose of writing data to a file is similar in spirit, even though Function B has additional layers.
- 共享行为: Both read bytes from an InputStream and write them to an OutputStream in a loop.；Both involve file I/O and handling of streams.
- 行为差异: Function A is purely a file copy; Function B involves resource acquisition, cache lookup, HTTP handling, and more complex logic.；Function A returns boolean; Function B returns InputStream.；Function A uses is.available() for loop control; Function B uses read() > -1.；Function B has extensive error handling and logging; Function A has minimal exception handling.
- 修正建议: Incorporate data-flow analysis to detect common patterns like input-to-output copy loops.；Use graph-based representations that capture API-independent data flows.；Train on examples where clone is a subgraph of larger functions.

### case_id=6404 FP boilerplate_overlap

- 方法: `handleHandshake` vs `handler`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft client handshake by validating server key and optionally sending HTTP request to session server for authentication.
- B 摘要: Generic web page scraper that extracts substrings from lines matching conditions and updates a result map.
- 静态失败原因: Static BERT models often rely on token-level overlap and structural patterns. Both functions share a similar boilerplate of URL opening, BufferedReader usage, and exception handling, which may have misled the model into thinking they are clones despite the low Jaccard similarity and different overall semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels pairs as non-clones unless they share significant functional similarity or are near-miss syntactic variants. Here, the purposes are entirely different (authentication vs. web scraping), so BCB correctly labels 0.
- 共享行为: Both open a URL using java.net.URL；Both use BufferedReader and InputStreamReader to read line by line；Both handle exceptions (IOException, MalformedURLException or general Exception)；Both call reader.close() in a finally block or after reading
- 行为差异: Function A validates a hex string and decides to either send a login packet or shut down the network; Function B never sends packets or shuts down networks.；Function A's URL is constructed from session parameters; Function B's URL comes from target.getUrl().；Function A reads only one line and checks for "ok"; Function B reads all lines and extracts substrings based on patterns.；Function A has a specific Minecraft authentication logic; Function B is a generic extraction utility.
- 修正建议: Incorporate method-level semantic embedding that captures the overall goal rather than just API sequences.；Use dataflow analysis to distinguish between different manipulations of read data.；Add a type-aware component that recognizes the different domain-specific types (e.g., Packet2Handshake vs Map<String, String>).；Increase weight on method name and context to differentiate purposes.

### case_id=6405 FP partial_functionality

- 方法: `doVersionCheck` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for a new version of jEdit by fetching a version file from a URL and comparing build numbers.
- B 摘要: Checks for available upgrades for TobeOS by querying a license server, validating licenses, and updating the database and UI.
- 静态失败原因: Static BERT/GraphCodeBERT models may have focused on common API calls (URL, BufferedReader, while loop) and the general pattern of 'check for update', overlooking the deep semantic differences in business logic, database operations, and UI interactions.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers these non-clones because they are from different projects (jEdit vs TobeOS), have different purposes (simple version check vs complex upgrade with license and database), and low lexical overlap (Jaccard=0.1016).
- 共享行为: Open a URL and read lines from the response；Parse key-value fields from the response；Check for availability of an update/upgrade；Conditionally show messages or UI elements
- 行为差异: Different input types (View vs Event) and UI handling；Different URL sources and response formats；Function A only compares build numbers; Function B involves license validation, database operations, and multiple UI updates；Different error handling mechanisms
- 修正建议: Incorporate project-level context or domain knowledge into embeddings；Use graph-based representations that capture data flow and control flow with specific variable names and constants；Train on more diverse clones that distinguish similar API usage across different applications；Apply more sophisticated structural matching techniques

### case_id=6406 FP boilerplate_overlap

- 方法: `googleImageSearch` vs `postXml`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Searches Google Images, parses HTML to extract image URLs, updates UI with an image icon.
- B 摘要: Sends an XML SOAP request over HTTP POST and returns the response as a string.
- 静态失败原因: Static BERT focused on overlapping boilerplate code patterns (HTTP connection, stream reading) and missed the divergent application logic, method signatures, and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically considers high-level functionality; despite shared HTTP boilerplate, the core tasks are distinct (image search vs XML post), so they are non-clones.
- 共享行为: Open HTTP connection；Read response stream line by line；Use BufferedReader and InputStreamReader；Handle exceptions
- 行为差异: HTTP method: GET vs POST；Different purpose: image search vs SOAP call；Different output: void (updates UI) vs String return；Different error handling: show dialog vs wrap exception
- 修正建议: Incorporate method name and signature embeddings；Use graph-based representations to capture control/data flow；Add attention to high-level semantics via task-specific pre-training

### case_id=6407 FP lexical_or_api_overlap

- 方法: `copy` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Copies a source file to a destination file using buffered I/O.
- B 摘要: Parses comma-separated string constants into sets and maps for character translation or input validation.
- 静态失败原因: The static BERT model likely overemphasized lexical overlaps (e.g., common Java keywords like 'while', 'new', 'StringTokenizer') or general API usage patterns, ignoring the fundamental semantic difference in file copy vs. data parsing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have completely different functionality and structure; even broad Type-4 similarity does not apply as they solve different problems.
- 共享行为: Both contain while loops iterating over data.；Both involve some form of data processing.
- 行为差异: Function a performs file I/O copy; function b parses string tokens into collections.；Function a uses FileInputStream/FileOutputStream; function b uses StringTokenizer.；Function a writes to output stream; function b populates data structures.；Function a has exception handling; function b throws errors for invalid data.
- 修正建议: Incorporate dataflow analysis to distinguish between file I/O and string tokenization.；Use a higher similarity threshold for pairs with very low token Jaccard.；Consider method signatures and purpose (e.g., 'copy' vs. 'readData').

### case_id=6408 FN partial_functionality

- 方法: `createFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads from a source file and writes the content to a destination resource managed by fileResourceManager, closing streams and logging errors.
- B 摘要: Retrieves a resource by name, either from a local cache or by downloading from a URL and caching locally, returning an InputStream.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the low token overlap (0.07) and surface-level differences in method names, parameter types, and control flow, failing to recognize the abstract data-flow pattern common to both. The model may also be limited by the lack of understanding of the high-level resource management context.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both methods are involved in data transfer between I/O streams (copying from source to destination), a common pattern in file handling. Despite different inputs and outputs, the core logic of opening streams, copying data, and closing resources is semantically similar, qualifying as a Type-3 or Type-4 clone.
- 共享行为: Both perform file I/O operations involving reading and writing data via streams；Both close resources (streams) in try-catch blocks；Both handle exceptions and perform cleanup
- 行为差异: createFile writes to a resource (output) while getResourceAsStream reads from a resource (input)；createFile takes a source File and a filename as input; getResourceAsStream takes a resource name and returns an InputStream；getResourceAsStream involves URL/HTTP handling and caching; createFile does not；createFile is void, getResourceAsStream returns InputStream
- 修正建议: Improve representation of long-range data flow dependencies；Incorporate abstract syntax trees (AST) or control flow graphs (CFG) to capture structural similarities；Use contrastive learning to emphasize semantic equivalence over lexical overlap；Consider the role of I/O patterns as a type of program functionality

### case_id=6409 FP boilerplate_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses a Prolog file and generates adapter classes into a JAR file.
- B 摘要: Utility method that copies a file from one path to another.
- 静态失败原因: The model likely overemphasized common boilerplate patterns (try-catch, File, Exception) and ignored the distinct high-level semantics, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the functions perform completely different tasks, despite both involving file I/O. The Type-4/partial functionality criterion is not met as there is no functional overlap.
- 共享行为: Both methods involve file operations；Both use try-catch blocks for exception handling；Both print stack traces on error
- 行为差异: Function A is a complex workflow with parsing, code generation, and JAR writing；Function B is a simple file copy without parsing or generation；Function A uses command-line arguments and debug mode, B uses direct path parameters；Function A creates multiple files and writes resources, B only writes to one output file
- 修正建议: Incorporate control flow or data flow analysis；Use more training data with diverse exception handling patterns；Weight structural differences more heavily

### case_id=6410 FP lexical_or_api_overlap

- 方法: `run` vs `PageLoader`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a vector tile from a URL by reading GeoJSON, parsing geometries, and adding to a data layer with request deduplication.
- B 摘要: Reads the entire content of a web page from a URL and stores it as a string.
- 静态失败原因: The model focused on lexical and API overlap (URL, BufferedReader, while loop) and did not capture the broader context, additional logic, and differing method signatures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires significant functional similarity; here the shared URL-reading fragment is only a small part of A's overall functionality, and the methods have different purposes and complexity, so BCB would likely not label as clone.
- 共享行为: Both open a URL and read input line by line into a string.
- 行为差异: A handles deduplication of HTTP requests via synchronization; B does not.；A supports both file and http protocols; B only http.；A processes GeoJSON into geometry collections and integrates with a data layer; B only stores raw string.；A is a void run() method with robust error handling; B is a constructor with minimal error handling.
- 修正建议: Incorporate structural features like method signature and class hierarchy.；Use graph-based code representation to capture data flow and control dependencies.；Increase training data for cross-method-type (constructor vs. method) comparisons.

### case_id=6411 FP partial_functionality

- 方法: `handler` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a web page and extracts a substring from lines matching a pattern, updating a map with the extracted value.
- B 摘要: Queries a REST API for tickets of a given queue, parses ticket IDs, retrieves each ticket, and returns a list.
- 静态失败原因: The static BERT model likely overemphasized the structural similarity (both use BufferedReader, while loop reading lines, try-catch) and ignored the different semantics (one updates a map, the other builds a list of tickets). The method names and parameter types were not sufficiently considered.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels as not clones because the methods perform entirely different tasks: one is a generic web scraper updating a map, the other is a domain-specific ticket query. Even under BCB's broad Type-4 semantic similarity, the output types and purposes are too distinct.
- 共享行为: Both read from an HTTP response line by line using BufferedReader；Both handle exceptions with try-catch blocks
- 行为差异: A extracts a substring and updates a map; B extracts ticket IDs and retrieves full ticket objects；A uses target object for URL and pattern; B constructs URL with query parameters for ticket search；A modifies a pre-existing map; B creates and returns a list of tickets
- 修正建议: Incorporate data flow analysis to track how input variables are transformed to output；Use method name and type signature as explicit features；Train on more diverse examples to reduce reliance on surface-level patterns

### case_id=6412 FP boilerplate_overlap

- 方法: `encodeMd5` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes MD5 hash of a string and returns hex representation.
- B 摘要: Handles a web request to classify a concept, builds XML, sends it to a URL, parses result, and updates session.
- 静态失败原因: The model likely overemphasized shallow common patterns (try-catch, null return, String processing) and ignored the completely different domain and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because there is no functional similarity; one is a generic utility, the other is application-specific business logic.
- 共享行为: Both use try-catch for exception handling and return null on failure.
- 行为差异: Function A is a simple cryptographic hash; Function B is a complex web controller.；Function A takes a single String input; Function B takes multiple request objects.；Function A returns a hex string; Function B returns an ActionForward.；Function B involves URL communication, session management, and XML parsing; Function A does not.
- 修正建议: Improve training to distinguish utility functions from web controllers.；Use graph-based representations to capture data flow and call structures.；Increase weight on method signatures and input/output types.

### case_id=6413 FN benchmark_preference_bias

- 方法: `scrapeForIsbns` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Scrapes ISBN-10 patterns from a web page's HTML content with retry logic.
- B 摘要: Downloads and processes an OPDS catalog or book file from a URL, handling HTTP connections and XML parsing.
- 静态失败原因: Static model focused on low token overlap and distinct API usage (regex vs SAX parser), missing the shared network I/O pattern; also misled by different method names and functionality.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled as clone due to both performing network I/O with error handling and logging, but this is too broad and likely an annotation error or bias.
- 共享行为: Both open an HTTP connection to a URL；Both read data from an input stream；Both handle exceptions (especially IOExceptions)；Both log information
- 行为差异: Function A specifically looks for ISBN patterns and counts matches; Function B parses XML for catalog entries or downloads a file；Function A has explicit retry on connection failure; Function B has a loop for pagination but not retry on connection errors；Function A is simpler and returns an int; Function B modifies state (calls onError, callback, etc.) and does not return a value
- 修正建议: Incorporate a broader understanding of high-level functionality beyond token overlap；Use more robust structural matching that distinguishes generic I/O from specific processing logic

### case_id=6414 FN partial_functionality

- 方法: `getFile` vs `decodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies its endpoint attribute in the XML, and returns the local file path.
- B 摘要: Decodes a Base64 encoded file and writes the decoded content to an output file, returning a boolean success status.
- 静态失败原因: The static BERT model likely relied heavily on token overlap and method names, which are very low (0.14 Jaccard similarity) and unrelated, leading to a non-clone prediction. It failed to capture the abstract similarity of file I/O operations shared across both functions.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to both being file transformation utilities that perform I/O and return a result, despite different specific purposes. The annotation might rely on a high-level functional similarity (e.g., 'file processing') rather than exact semantic equivalence.
- 共享行为: Both involve reading from an input source and writing to a local file.；Both use file I/O and handle exceptions with try-catch blocks.；Both use buffered streams for I/O operations.
- 行为差异: Function A downloads from a remote URL, while Function B reads a local file.；Function A modifies XML content (wsdlsoap:address) before writing, Function B only decodes and copies.；Function A returns the file path as a String, Function B returns a boolean success indicator.；Function A uses channel-based transfer and XML parsing; Function B uses simple byte buffer and Base64 decoding.
- 修正建议: Enhance the model to recognize shared I/O patterns and abstract file transformation logic.；Incorporate data flow analysis to capture common operations like reading, writing, and exception handling.；Use contrastive learning focused on functional similarity beyond lexical overlap.

### case_id=6415 FN benchmark_preference_bias

- 方法: `readData` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads multiple sets of Tibetan character components from comma-separated strings and parses a configuration file to populate hash maps and sets for transliteration.
- B 摘要: Checks for a new software version by reading a version file from a URL and comparing build numbers.
- 静态失败原因: Static BERT models rely on token overlap (0.104) and structural similarity; the low lexical overlap and different control structures led the model to predict no clone, but BCB accepts broader functional similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely considered both as 'read and parse data' functions, thus functional similarity at a high level (Type-4), even though implementation and domain differ.
- 共享行为: Both read data from an external source (string tokens or URL stream)；Both parse lines or tokens；Both handle IOException
- 行为差异: One builds a transliteration database, the other checks version；One uses StringTokenizer, the other uses BufferedReader；One populates multiple sets and maps, the other extracts two string fields
- 修正建议: Incorporate hierarchical functional similarity metrics；Fine-tune with Type-4 examples；Use task-specific alignment or data augmentation for broad similarity

### case_id=6416 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `getContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft handshake packet: validates username, optionally contacts session server for authentication, then sends login or shuts down.
- B 摘要: Executes an HTTP request and returns the response body as a string.
- 静态失败原因: GraphCodeBERT may have been misled by overlapping tokens like 'BufferedReader', 'readLine', 'close', and 'Exception', as well as general network/IO context, while missing the high-level semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the functions have entirely different purposes and only share superficial network/IO boilerplate.
- 共享行为: Both perform network I/O and read from streams using BufferedReader.；Both involve exception handling (one catches, one throws).
- 行为差异: A is a Minecraft-specific handshake handler with authentication logic; B is a generic HTTP response fetcher.；A has multiple conditional branches; B is linear.；A uses URL construction and query parameters; B uses HttpClient.；A manipulates network manager and send queue; B returns a string.
- 修正建议: Enhance model with dataflow or control flow analysis to distinguish different control structures.；Use contrastive learning on hard negatives with similar code patterns but different semantics.；Incorporate more domain-specific patterns or abstract syntax tree (AST) features.

### case_id=6417 FP boilerplate_overlap

- 方法: `main` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file, generates adapter classes and a lookup, and writes them into a JAR.
- B 摘要: Copies a file from one path to another using NIO channels.
- 静态失败原因: The static BERT model likely overemphasized the common pattern of file I/O with try-catch blocks, which is present in both functions. The low token Jaccard (0.08) suggests the model relied on structural boilerplate rather than semantic content, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clones because they perform entirely different tasks. Even under the lenient Type-4 category (functionally similar), there is no functional overlap beyond basic file I/O, which is too generic to indicate a clone.
- 共享行为: Both involve file input/output operations (reading and writing files).；Both use try-catch blocks to handle exceptions during I/O.
- 行为差异: Function A is a lengthy `main` method with complex logic for adapter generation, while B is a short utility for file copying.；A processes Prolog files and generates Java classes; B simply copies any file byte-for-byte.；A has multiple nested try-catch blocks and exception handling; B has a single try-catch-finally.；A uses many library-specific classes (e.g., Parser, FactVisitor, ClassWriter); B uses only Java NIO.
- 修正建议: Incorporate method name embeddings to capture high-level intent.；Use control flow graph or data flow analysis to distinguish different program tasks.；Implement length-aware attention to prevent long functions from being truncated or misrepresented.；Train on more diverse non-clone pairs with shared I/O patterns to reduce false positives.

### case_id=6418 FN boilerplate_overlap

- 方法: `getHTML` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads HTML from a URL, optionally writes to a file, and returns the content as a string.
- B 摘要: Checks for a new software version by reading a version file from a URL and displaying a message.
- 静态失败原因: Static models rely heavily on token overlap and method names; the low Jaccard similarity (0.218) and different method names ('getHTML' vs 'doVersionCheck') likely caused the model to miss the structural similarity in the URL reading boilerplate.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label these clones due to the shared pattern of opening a URL, reading lines with BufferedReader, and processing the input line by line, even though the functional purpose differs.
- 共享行为: Open a URL connection and read lines from the input stream using BufferedReader；Iterate over lines until end of stream
- 行为差异: Function A returns the entire HTML content, while B parses lines for version and build strings；Function A optionally writes the content to a file; B does not write to file；Function B displays UI messages (new version or up-to-date); A has no UI interaction
- 修正建议: Enhance model sensitivity to common API usage patterns (e.g., URL + BufferedReader + readLine) as structural features；Incorporate graph-based or dataflow representations to capture shared control flow and I/O operations

### case_id=6419 FN partial_functionality

- 方法: `readGeoParserResult` vs `PhoneSetImpl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a text record, sends it to a geospatial parsing service, and collects place names and gazetteer IDs with retry logic.
- B 摘要: Reads a phone set definition file from a URL and populates an internal map with parsed lines.
- 静态失败原因: Static BERT models rely on token overlap and syntactic structure; the token Jaccard similarity is very low (0.10), the method names differ, and the specific API calls (e.g., XML parsing vs plain text) are distinct. The model likely saw no lexical or structural similarity and thus predicted non-clone, missing the abstract semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled this as a clone because both functions implement the same high-level pattern: reading data from a URL line by line and populating a data structure. Despite different specific formats and logic, the core behavior is similar enough for a Type-4 (semantic) clone under BCB's broad guidelines.
- 共享行为: Both open a URL and create a BufferedReader to read lines.；Both iterate over lines and perform processing to populate a data structure.；Both handle I/O operations and may throw exceptions.
- 行为差异: Function A constructs an XML request and parses XML responses; Function B reads plain text lines.；Function A includes retry logic and testing mode; Function B does not.；Function A returns a collection; Function B initializes an instance field.；Function A uses external service URL; Function B reads a local resource URL.
- 修正建议: Incorporate higher-level code summaries or documentation embeddings to capture intent.；Use data flow analysis to identify common patterns like URL reading and line iteration.；Augment training data with diverse examples of semantic clones that have low token overlap.；Consider using graph representations that abstract away specific API details.

### case_id=6420 FN partial_functionality

- 方法: `copyResource` vs `setContenu`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file byte by byte.
- B 摘要: Sets the content of a file by copying an input stream to an output stream, with duplicate checks and metadata updates.
- 静态失败原因: Static BERT models rely heavily on token overlap and structural similarity; the low Jaccard similarity and different method names, parameter lists, and surrounding code mask the abstract stream copy pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because they share the core functionality of copying an input stream to an output stream, which is a common pattern in file/resource handling, even though the broader context differs.
- 共享行为: Both copy data from an InputStream to an OutputStream.
- 行为差异: copyResource is a simple byte copy; setContenu includes duplicate validation, metadata setting, and exception handling.；copyResource uses a while loop; setContenu uses IOUtils.copy with proper resource management.；copyResource is private with minimal parameters; setContenu is public with many parameters for document management context.
- 修正建议: Train models to recognize common I/O patterns despite different contexts.；Incorporate dataflow or control flow abstraction to identify core operations.；Add synthetic training examples where clones share only a partial algorithmic core.

### case_id=6421 FN partial_functionality

- 方法: `addIDs` vs `wordFrequency`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Scrapes a metabolite database website to extract IDs and molecular weight, storing them on a row object and returning a score.
- B 摘要: Fetches word frequency from a web service by substituting a word into a URL and extracting the frequency via regex matching.
- 静态失败原因: The static model likely focused on low token Jaccard similarity (0.168) and different method names, missing the structural similarity in the web-scraping workflow. It did not capture the common API usage pattern (URL, BufferedReader, readLine) and control-flow structure.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels web-scraping functions as clones if they share the same high-level pattern of URL fetch, line-by-line parsing, and integer return, even if the parsing details differ. This pair matches that pattern.
- 共享行为: Both open a URL, read lines from the response, and parse the content to compute an integer return value.；Both use try-catch blocks for IOException handling.；Both use BufferedReader and InputStreamReader to read from a URL stream.
- 行为差异: Function A parses HTML with substring/contains operations, while B uses regex matching.；Function A has side effects on a PeakListRow object, modifying multiple fields; B has no side effects.；Function A supports multiple ID types (PubChem, ChEBI, KEGG, etc.), while B only extracts a single frequency value.；The parsing logic in A is more complex with multiple conditional branches; B has a single condition.
- 修正建议: Augment training data with more web-scraping pairs that have low lexical overlap but high structural similarity.；Enhance models with dataflow-aware or control-flow-aware features to capture I/O patterns.；Use graph-based representations that include API call chains.；Reduce reliance on token overlap by employing structure-based embeddings.

### case_id=6422 FN partial_functionality

- 方法: `handledRun` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads and updates a game data file from a URL if a newer version is available, with error handling and database loading.
- B 摘要: Fetches and logs the entire content of a URL as a string.
- 静态失败原因: The low token Jaccard (0.17) and different control flow (version check, file writing) obscure the shared I/O core. The model may overlook the similarity in URL reading due to divergent domain-specific terms and structural differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both functions perform the core task of reading data from a URL via InputStream and BufferedReader, despite differences in additional processing and error handling. The shared I/O pattern qualifies as Type-4 clone (functionally similar).
- 共享行为: Open a URL and read its content line by line using BufferedReader
- 行为差异: Function a conditionally writes data to a file based on version comparison; function b only logs the content.；Function a has extensive exception handling and a finally block for database loading; function b throws Exception generically.；Function a uses a specific URL constant; function b uses a hardcoded URL.；Function a has version checking logic; function b does not.
- 修正建议: Enhance models to recognize shared API usage patterns (e.g., sequence URL.openStream -> BufferedReader) across different contexts.；Incorporate dataflow analysis to abstract away variable names and focus on data processing pipelines.；Use graph representations that capture the structural skeleton of I/O operations.

### case_id=6423 FP boilerplate_overlap

- 方法: `readData` vs `write`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads and parses multiple comma-separated string fields to populate various sets and maps, and processes a file with delimiter-separated entries to fill tibHash and other mappings.
- B 摘要: Creates a JAR output stream and copies entries from included JAR files (with optional dependency expansion) into the output JAR.
- 静态失败原因: The static BERT model likely overfitted to common Java idioms (e.g., while loops, HashSets) and ignored the fundamental difference in I/O direction (reading vs writing) and overall purpose, possibly due to limited understanding of long-range dependencies or data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates non-clone because the functions perform completely different tasks (one is data initialization, the other is JAR creation) with no semantic similarity.
- 共享行为: Both use HashSet collections；Both involve looping over iterated elements
- 行为差异: Function A reads and parses data from strings and a file; Function B writes a JAR by copying entries from other JARs；Function A populates multiple sets and maps; Function B copies file entries to an output stream；Function A handles error cases with custom Error throws; Function B throws IOException
- 修正建议: Improve model's ability to capture overall function purpose (e.g., through contrastive learning on function summaries)；Incorporate data flow analysis to differentiate read vs write operations；Use code structure (e.g., API calls) to disambiguate different libraries (Java I/O vs JAR handling)

### case_id=6424 FN partial_functionality

- 方法: `doTransfer` vs `GetResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards entire HTTP request and response as a proxy, copying headers and body, and echoing the response.
- B 摘要: Performs a simple HTTP GET request and returns the response body as a concatenated string.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on low lexical overlap and different control flow structures, missing the high-level functional similarity that BCB considered acceptable.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label it as clone due to broad Type-4 semantic similarity: both functions involve making an HTTP request and reading the response, a common task in Java web programming.
- 共享行为: Both create an HttpURLConnection to a URL；Both set request method and check for HTTP_OK response；Both read response input stream
- 行为差异: A forwards request headers and body, B does not；A writes response to servlet output stream, B returns a string；A uses variable method (parameter), B always uses GET；A handles errors with sendError, B returns null
- 修正建议: Enhance model with domain-specific knowledge about HTTP communication patterns；Incorporate coarse-grained functional descriptors (e.g., 'HTTP client') into embeddings；Use dataflow-focused pre-training objectives to trace I/O interactions

### case_id=6425 FN boilerplate_overlap

- 方法: `readGeoParserResult` vs `createHTML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads geo-parser results by sending an XML request, parsing the response, and extracting place names with gazetteer IDs.
- B 摘要: Generates HTML content for different page types, including reading a CSS file and building HTML with database query results.
- 静态失败原因: Static BERT models focus on token-level embeddings and may overlook the shared structural pattern (while loop reading lines) due to low lexical overlap and the presence of many different tokens. The model likely classified them as non-clones because the overall semantics are different and the common boilerplate is not sufficient to overcome the dissimilarity in the rest of the code.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider the common pattern of reading lines from a stream and building a string as a Type-3 clone, despite different overall functionalities. The similar boilerplate code for I/O and exception handling might have been deemed sufficient for a clone annotation in the benchmark.
- 共享行为: Both functions read from an InputStream using BufferedReader to build a string representation of data.
- 行为差异: Function A sends an HTTP request and parses XML, function B reads a local CSS file and builds HTML; Function A returns a collection of tuples, function B returns an HTML string; Function A has retry logic, function B does not; Function B uses a switch on page type, function A uses a conditional for request format.
- 修正建议: Enhance the model to recognize structural patterns like common control flow idioms (e.g., while loop reading from BufferedReader) even when lexical tokens differ.；Use dataflow analysis to capture shared operations like 'read lines from stream and concatenate'.

### case_id=6426 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Check for version updates by reading a version check URL and parsing build numbers.
- B 摘要: Load a map tile from a URL, parse it into vector tile geometry, and add to data layer.
- 静态失败原因: Static models may over-rely on lexical overlap and API usage patterns, missing the semantic divergence in the post-read logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions serve entirely different functionalities despite sharing a common I/O pattern.
- 共享行为: Open a URL and read input stream；Use BufferedReader to read lines；Handle IOExceptions
- 行为差异: Different purposes (version checking vs. tile loading)；Different parsing logic (check line prefix vs. accumulate whole content)；Different output actions (call version check method vs. add geometry to data structure)；Different error handling (show error dialog vs. log and return)
- 修正建议: Train on more diverse data with functional labels；Incorporate data flow analysis to distinguish different post-processing steps；Use contrastive learning to separate based on final output behavior

### case_id=6427 FN benchmark_preference_bias

- 方法: `doGet` vs `testTrainingBackprop`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests for page rendering, including page lookup, access control, logging, and caching.
- B 摘要: Tests training of a neural network using backpropagation on XOR data, creating a temporary file and asserting mean squared error below a threshold.
- 静态失败原因: The static BERT/GraphCodeBERT model correctly predicted non-clone (0) due to very low token overlap (Jaccard=0.0447) and clear differences in method names, API usage, and control structures. The model's prediction aligns with expected semantic differences.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this as clone due to broad interpretation of both methods involving 'request handling' or 'data processing', but the functional domains are entirely different. The label might be erroneous or reflect a misalignment in BCB's annotation guidelines.
- 共享行为: Both involve file/IO operations (temporary file creation in B, response writing and caching in A)；Both check conditions and handle exceptions
- 行为差异: A is a web servlet method; B is a unit test method；A handles client requests, validates user permissions, and generates HTML output; B trains a neural network and validates accuracy；A uses HttpServletRequest/Response, Page, Property objects; B uses Layer, Fann, Trainer classes from FANN library；A involves multiple database-like lookups (page, property) and caching; B is a self-contained test with no external dependencies beyond file I/O
- 修正建议: Re-evaluate BCB annotation for this pair; likely a mislabel that should be corrected to non-clone.；Improve BCB annotation guidelines to exclude such evidently unrelated pairs from clone labels.

### case_id=6428 FN lexical_or_api_overlap

- 方法: `register` vs `PhoneSetImpl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Registers a user by encoding password, setting default authority, hashing email, creating phpBB forum user via HTTP, persisting user, and sending confirmation email.
- B 摘要: Constructs a PhoneSetImpl by reading lines from a URL, parsing and adding each line (except those starting with '***') to a map.
- 静态失败原因: Static BERT likely correctly identified low token overlap and different semantics; it may have failed only if it relied on overly coarse embeddings that grouped 'URL reading' together.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have considered both as 'reading from a URL' and 'processing input', but the tasks are fundamentally different; BCB might have mislabeled due to superficial similarity in using BufferedReader and URL.
- 共享行为: Both read from a URL using BufferedReader；Both have IOException handling
- 行为差异: Function A does user registration with multiple steps (password encoding, authority setting, email hashing, forum call, persistence, email sending); B only reads and parses lines into a map.；Function A has extensive error handling and logging; B has none.；Function A uses HTTP URL specifically (phpBB); B uses a generic URL.；Function A modifies a User object; B modifies a HashMap.
- 修正建议: Train models to ignore common API usage patterns when the overall goal differs.；Use structure-based analysis to capture flow differences.

### case_id=6429 FP long_range_semantics

- 方法: `update` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Updates LDAP directory attributes for a user, including optional password hashing and renaming of entry if email changed.
- B 摘要: Handles HTTP request for classifying a concept by sending XML to a web service, parsing the response, and storing results in session.
- 静态失败原因: The static model may have been misled by the presence of similar structural elements such as parameter lists, exception handling, and network I/O operations. However, the actual semantics differ significantly. The model might not have captured the high-level purpose due to long-range dependencies or lack of domain knowledge.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would likely not consider these clones because their core functionality is entirely different: one is LDAP directory update and the other is HTTP request handling for classification. They do not share similar input/output behavior or purpose.
- 共享行为: Both perform network operations (LDAP vs HTTP)；Both involve string manipulation and building of data；Both handle exceptions and use try-catch blocks
- 行为差异: Function A modifies LDAP directory entries; function B processes HTTP requests and calls an external classification web service；Function A uses JNDI and DirectoryContext; function B uses URLConnection and HttpSession；Function A's output is a modification of directory; function B's output is a forward to a Struts action；Function A works with user profile attributes; function B works with concept classification
- 修正建议: Improve training data to include more diverse non-clone pairs with low token similarity but similar structural features；Incorporate domain-specific knowledge or use code summarization to distinguish between different application domains；Enhance model's ability to capture overall program logic rather than surface-level API usage

### case_id=6430 FN boilerplate_overlap

- 方法: `getHTML` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML content from a URL, optionally saves it to a file, and returns the content as a string.
- B 摘要: Checks for a new version of jEdit by fetching and parsing a version file from a URL, and displays appropriate messages.
- 静态失败原因: Low token overlap (0.218) and different method names/return types cause the model to focus on surface-level differences rather than the shared I/O pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as fetching and processing data from a URL line by line, a common pattern, thus labeling them as clones despite different specific purposes.
- 共享行为: Both open an HTTP connection to a URL and read lines using BufferedReader；Both handle IOException in a catch block
- 行为差异: Function A returns the entire page content; B parses specific lines starting with .version and .build；A optionally writes to a file; B shows UI dialogs based on version comparison；A uses HttpURLConnection with custom User-Agent; B uses URL.openStream()
- 修正建议: Train with more examples of partial functional similarity；Use models like GraphCodeBERT that capture structural and data flow patterns

### case_id=6431 FN benchmark_preference_bias

- 方法: `doGet` vs `processAddByURLSubmit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.1`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to display a page after checking permissions and logging.
- B 摘要: Processes a URL submission by fetching DOAP data from the URL and processing it.
- 静态失败原因: Static BERT correctly identified low lexical and structural similarity; BCB label is likely incorrect, so static model did not fail but correctly predicted non-clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this as clone erroneously, possibly due to broad categorization of web-related operations or misannotation.
- 共享行为: Both handle exceptions (e.g., IOException) and use logging.
- 行为差异: Function A is a servlet doGet method for page display; Function B processes a submitted URL to import DOAP data.；Function A involves user authentication and page caching; Function B does not.；Function A outputs HTML; Function B outputs nothing (processes data).
- 修正建议: Review and correct BCB annotation for this pair.；Use domain-specific semantic analysis to distinguish fundamentally different functionalities.

### case_id=6432 FN benchmark_preference_bias

- 方法: `getEncoding` vs `lookupFutureEvents`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Opens a URL connection, reads HTTP headers and response body to extract charset encoding.
- B 摘要: Fetches JSON from a Meetup API, parses it, and constructs a list of Event objects.
- 静态失败原因: A static model might have correctly identified low lexical overlap and lack of shared functionality, leading to non-clone prediction.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to both functions using URL connection and BufferedReader, but this is a weak boilerplate similarity; likely an annotation error.
- 共享行为: Both involve opening a URL and reading data via BufferedReader
- 行为差异: Function A extracts a single encoding string; Function B parses JSON into multiple Event objects；Function A uses URLConnection; Function B uses URL.openStream()；Function A returns a String; Function B returns a List<Event>
- 修正建议: Re-annotate BCB pair as non-clone；Add more data to distinguish URL-reading boilerplate from true semantic clones

### case_id=6433 FP lexical_or_api_overlap

- 方法: `get` vs `postXml`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP GET request with geographic parameters and parses response lines into an array of GameRecord objects.
- B 摘要: Sends an HTTP POST request with XML content and returns the response as a string.
- 静态失败原因: The model was misled by overlapping API usage (HttpURLConnection, BufferedReader, IOException) and similar try-catch structure, ignoring semantic differences in HTTP method and response processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have different input/output types and distinct purposes, despite sharing HTTP-related boilerplate.
- 共享行为: Both open HTTP connections and set request properties；Both read response from input stream
- 行为差异: HTTP method: GET vs POST；Request body: none vs XML content；Response parsing: filters lines starting with '#' and decodes into GameRecord vs concatenates all lines as string；Error handling: prints error and returns null vs throws RuntimeException
- 修正建议: Incorporate method name and parameter analysis to distinguish GET vs POST patterns；Better capture return type differences and response handling logic；Use data flow analysis to differentiate between reading request body vs writing output

### case_id=6434 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `write`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies or appends a message in locale-specific .properties files.
- B 摘要: Creates a JAR file by copying entries from included JARs.
- 静态失败原因: The functions have near-zero token overlap and different structural patterns; the shared stream-copy pattern is not reflected in lexical or AST-based features.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may treat both as instances of 'stream copying' operations (reading from an InputStream/Reader and writing to an OutputStream/Writer) with additional processing, accepting broad Type-4 similarity.
- 共享行为: Both functions read from an input source and write to an output destination.
- 行为差异: A manipulates property strings with key-value replacement; B copies binary entries from JAR files.；A has conditional file copy and missing-file handling; B has dependency expansion and exclusion of manifest entries.；A writes to a plain text file; B writes to a compressed JAR archive.
- 修正建议: Incorporate I/O operation patterns as features for clone detection.；Use data-flow analysis to identify stream copying operations.

### case_id=6435 FN benchmark_preference_bias

- 方法: `main` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to local files.
- B 摘要: Reads a DICOM image file and rewrites it to another file with possibly different encoding.
- 静态失败原因: Static BERT models rely on token similarity and structural embeddings. The low token Jaccard (0.118) and different API usage lead to a low similarity score, causing the model to correctly predict non-clone according to its learned representation. The model fails to recognize the broad 'I/O processing' similarity that BCB might have accepted, but that similarity is too vague for clone detection.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Possibly BCB annotators considered both as 'read and rewrite' operations on binary data, or they may have considered them as both being main-like routines that process files. However, the functionality is fundamentally different.
- 共享行为: Both perform I/O operations involving reading from an input source and writing to an output destination.
- 行为差异: Function A deals with zip extraction from a URL stream, while Function B deals with DICOM image parsing and rewriting.；Function A uses standard Java I/O and zip libraries; Function B uses specialized DICOM libraries.；Function A processes multiple files (zip entries), while Function B processes a single image and writes to a specific output file.；Function A outputs console messages during extraction; Function B outputs progress messages about reading and writing.
- 修正建议: Improve training data to include more diverse I/O patterns to capture broad semantic clones.；Use domain adaptation or task-specific embeddings that can recognize generic data processing patterns.；Incorporate explicit functional annotations to distinguish between domain-specific and generic processing.

### case_id=6436 FN partial_functionality

- 方法: `addIDs` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads metabolite data from a web page for a given name and updates a peak list row with various identifiers and molecular weight.
- B 摘要: Reads version check data from a web page and compares build versions to trigger a version check dialog.
- 静态失败原因: Low token Jaccard similarity (0.16) and focus on specific vocabulary like 'metabolite', 'CAS', 'version' may have obscured the shared structural pattern of URL I/O and line-by-line processing.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the common boilerplate pattern of URL reading, line parsing, and exception handling as sufficient for a broad Type-3/Type-4 clone, ignoring the domain-specific differences.
- 共享行为: Open a URL and read lines using BufferedReader；Parse lines based on specific patterns；Handle IOException with logging or error dialog
- 行为差异: Different data extraction goals: metabolite IDs vs version strings；Different output actions: set row variables vs call doVersionCheck；Different loop and parsing logic: one looks for href patterns, the other for line prefixes
- 修正建议: Incorporate structural embeddings that capture control flow and data flow patterns；Use contrastive learning to emphasize shared I/O patterns while distinguishing different post-processing

### case_id=6437 FP boilerplate_overlap

- 方法: `retrieveQ` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves the content of a URL as a string, printing the response message to stderr.
- B 摘要: Queries a RequestTracker for open tickets in a queue, parses ticket IDs from the response, fetches each ticket, and returns a list of RTTicket objects.
- 静态失败原因: Static BERT models likely overemphasized the common lexical tokens (URL, BufferedReader, InputStreamReader) and missed the different business logic, return types, and control flow structures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have completely different functionality (generic HTTP fetch vs domain-specific ticket retrieval) despite sharing HTTP boilerplate.
- 共享行为: Performs HTTP GET requests；Reads response line by line using BufferedReader；Handles IOException via throws or try-catch
- 行为差异: A returns raw string, B returns list of RTTicket objects；A does not parse the content, B extracts ticket IDs and fetches each ticket；A prints response message to stderr, B does not；A throws MalformedURLException, B handles exceptions internally
- 修正建议: Incorporate data flow analysis to track how data is transformed；Use type information to distinguish return types and method signatures；Leverage AST or graph representations to capture higher-level semantics

### case_id=6438 FP lexical_or_api_overlap

- 方法: `importSequences` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Imports sequences from a FASTA-like file accessed via URL.
- B 摘要: Searches Google Images for album art and extracts image URLs.
- 静态失败原因: The model likely over-emphasized the lexical overlap of URL handling, Input/Output stream usage, and similar method signatures (public void methodName()), while missing the semantic intent differences. The token Jaccard is low (0.11), but the model might have been misled by the structural similarity of 'try-catch, open stream, read loop' patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels clones based on functional similarity, not just shared I/O patterns. The methods perform entirely different tasks (sequence import vs. image search), so BCB correctly marked them as non-clones.
- 共享行为: Open a URL connection；Read input from the stream
- 行为差异: A parses FASTA sequence data; B parses HTML image search results.；A stores sequences in lists; B accumulates image URLs in a collection.；A uses explicit file format parsing; B uses string splitting and pattern matching.；A handles multiple sequences in a loop; B handles a single page of image results.
- 修正建议: Incorporate dataflow analysis to understand what the parsed text is used for.；Use code summarization to capture purpose (e.g., 'import fasta' vs 'google search').；Enhance training with more functional similarity examples, not just structural patterns.

### case_id=6439 FP boilerplate_overlap

- 方法: `getDatasetsList` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches and caches a list of dataset names from a server using a URL.
- B 摘要: Searches Google Images for artist/album and parses image URLs from HTML.
- 静态失败原因: Static BERT/GraphCodeBERT may have overfitted on shared boilerplate patterns like URL opening, BufferedReader, and while loop, ignoring distinct domain semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions serve entirely different purposes (dataset list vs. image search) despite similar I/O boilerplate.
- 共享行为: Both open an HTTP connection using URL and BufferedReader；Both read lines in a loop and add to a list；Both handle exceptions
- 行为差异: Different URL construction and parameters；Different data parsing (line-by-line vs. split on regex)；A caches results, B does not；A is synchronized, B is not
- 修正建议: Use contrastive learning to distinguish boilerplate from core semantics；Incorporate dataflow analysis to capture different variable usage；Add training examples with similar I/O but different tasks

### case_id=6440 FP boilerplate_overlap

- 方法: `googleImageSearch` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs a Google image search by constructing a URL, fetching HTML, parsing image URLs, and updating a UI component.
- B 摘要: Downloads an RDF model from a URL by opening an HTTP connection with accept headers and parsing the response into a Jena Model object.
- 静态失败原因: The static model likely overemphasized the similar token sequences and structural patterns (URL, HttpURLConnection, input stream, exception handling) while ignoring the differing high-level purpose and output behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically marks non-clones when core functionality differs, even if some networking boilerplate overlaps. Therefore, they assigned label 0 (non-clone).
- 共享行为: Open HTTP connections to URLs；Read input streams from connections；Handle MalformedURLException and IOException
- 行为差异: Function A constructs a query URL for Google Images; Function B expects a direct RDF URL；Function A parses HTML to extract image URLs; Function B uses Jena Model to read RDF data；Function A has side effects on UI and global list; Function B returns a Model without side effects；Exception handling differs: A shows error dialog, B logs and throws RuntimeException
- 修正建议: Incorporate data-flow analysis to distinguish side-effect vs. return-value functions；Use higher-level semantic representations (e.g., API call chains, output types)；Improve training data to include more diverse networking functions with different domain-specific logic

### case_id=6441 FN dataflow_blindspot

- 方法: `writeFileType` vs `runScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `dynamic_equivalence_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads URIs from a file, fetches each URL, inspects the first 100 lines for OWL/RDFS/RDF namespaces, and writes the classification to an output file.
- B 摘要: Constructs a URL from a script name, reads all bytes from the stream, and returns the content as a string.
- 静态失败原因: Static BERT models rely heavily on lexical overlap and structural similarity; the low token Jaccard (0.14) and different control flow make it hard to detect the shared network I/O pattern without understanding the overall intent.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本可能是 API 写法不同但行为等价的漏报。建议测试目标为 input_output_equivalence。
- BCB 偏好解释: BCB may label this as a Type-4 clone because both functions perform network I/O with exception handling, a common high-level pattern considered semantically similar despite different specific logic and output handling.
- 共享行为: Both open a URL and read data from it；Both use try-catch to handle IOExceptions；Both involve fetching data over network
- 行为差异: writeFileType processes a list of URIs from a file and writes results to another file; runScript takes a single script name and returns its content；writeFileType reads lines and checks for specific namespaces; runScript reads raw bytes into a string；Different error handling: writeFileType writes 'BROKEN' on error; runScript returns 'error!'
- 修正建议: Enhance model to capture high-level semantic patterns like network I/O across different structures；Incorporate data flow analysis to recognize common API usage sequences；Use contrastive learning on pairs with low lexical overlap but similar functionality

### case_id=6442 FN benchmark_preference_bias

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using NIO FileChannel transfer.
- B 摘要: Builds a web site for editing by reading XML, transforming, and writing multiple output files.
- 静态失败原因: The static BERT model likely correctly predicted non-clone due to low token overlap and clear semantic difference; the 'failure' is relative to the BCB label which may be erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB typically requires significant functional similarity; these functions share only generic file operations, unlikely to be considered clones under BCB guidelines, suggesting a possible annotation error.
- 共享行为: Both perform file I/O operations
- 行为差异: A is a simple file copy; B is a complex multi-step site builder；A uses FileChannel and transferTo; B uses FileInputStream, StringWriter, and Transformer；A has no parameters besides file objects; B has many parameters including paths, properties, etc.；A is deterministic; B involves iteration over pages, error handling, and string replacement
- 修正建议: Re-evaluate the BCB label for this pair, possibly correcting it to non-clone；Improve model robustness by focusing on high-level semantic matching beyond token overlap

### case_id=6443 FN benchmark_preference_bias

- 方法: `fileDownload` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a file from a given URL and saves it to a destination directory.
- B 摘要: Checks for a new version of jEdit by fetching and parsing a text file from a URL, then updating the UI.
- 静态失败原因: Static BERT models rely on lexical and structural features; the low token Jaccard (0.2) and different method names and task-specific code (file writing vs. version parsing) likely led it to correctly deem them non-clones, but it missed the broader pattern that BCB annotators might have considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as common network I/O operations that follow a similar pattern (open URL, read, close, catch), potentially classifying them as Type-3 clones despite low syntactic overlap, or as functional clones in a very broad sense of 'fetching data from a URL'.
- 共享行为: Open a URL connection；Read data using BufferedReader/InputStreamReader；Handle IOException via try-catch
- 行为差异: A writes raw bytes to a local file; B parses text lines for version info；A uses character streams for potentially binary data; B uses proper text reading；A has no UI interaction; B shows wait cursor and dialogs
- 修正建议: Include more context about project-specific idioms；Use graph-based models to capture control-flow similarities；Adjust training data to reflect BCB's preference for pattern-based clones

### case_id=6444 FN benchmark_preference_bias

- 方法: `writeFileToFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies entire content of one file to another using FileChannel.
- B 摘要: Builds a website for editing by transforming XML and writing multiple output files.
- 静态失败原因: The static model correctly predicted non-clone due to low token overlap and different structures; it did not fail, rather BCB label appears erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as file-writing methods, but this is overly broad and ignores the distinct high-level purposes.
- 共享行为: Both write data to files.；Both handle IOException.
- 行为差异: A is a simple file copy; B is a complex multi-step transformation.；A uses FileChannel.transferTo; B uses custom file writing after XSLT.；B involves XML parsing, XSLT, and iteration over pages; A does not.
- 修正建议: Re-evaluate BCB annotation for this pair.；Consider using more specific functional criteria.

### case_id=6445 FN partial_functionality

- 方法: `getResourceAsStream` vs `save`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource from a URL, caches it locally, and returns an InputStream.
- B 摘要: Saves a byte array to a file using IOUtils.copy and returns the number of bytes copied.
- 静态失败原因: Static models may focus on token overlap and shallow syntax, missing the high-level semantic similarity of stream copying due to low token Jaccard and different method names; they fail to capture the common data flow pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'copying data from an input to an output file' with similar stream setup and closing patterns, classifying them as Type-4 (semantically similar) clones despite different source types.
- 共享行为: Both read from an input source and write to a file output stream；Both create parent directories if needed；Both handle stream closing in finally or catch blocks
- 行为差异: Function A involves network connection, URL handling, and caching decision based on modification time；Function B is a straightforward copy from byte array to file without caching logic；Function A uses multiple conditional branches and prints debug info
- 修正建议: Use graph-based models that capture data flow and control dependencies；Incorporate code summarization to compare high-level intent；Augment training data with Type-4 clones examples

### case_id=6446 FP lexical_or_api_overlap

- 方法: `readVersion` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads version, revision, and date from a bundled resource file and assigns to instance variables.
- B 摘要: Downloads an RDF model from a URL with HTTP headers and returns it.
- 静态失败原因: Static models like CodeBERT likely over-relied on lexical overlap (URL, InputStream, IOException, try-catch) and missed the semantic mismatch in overall task and data flow, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the functions have entirely different high-level purposes and outputs, despite sharing some I/O boilerplate and API usage patterns.
- 共享行为: Both open a URL stream and read data (lines or bytes).；Both handle IOException with try-catch blocks.
- 行为差异: readVersion parses specific key-value lines from a local resource file; downloadModel downloads a remote model over HTTP.；readVersion sets instance variables; downloadModel returns a Model object.；readVersion uses ClassLoader.getSystemResource; downloadModel uses new URL and openConnection.；downloadModel sets HTTP request properties; readVersion does not.
- 修正建议: Incorporate dataflow or structural information to differentiate assignment vs. return.；Use contrastive learning with more diverse negative examples to reduce sensitivity to boilerplate overlap.

### case_id=6447 FN lexical_or_api_overlap

- 方法: `writeFileType` vs `readIntoList`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads URIs from a file, skips initial lines, then for each URI opens URL, checks for OWL/RDFS/RDF keywords within first 100 lines, and writes classification to output file.
- B 摘要: Reads from a URL, extracts link text between HTML tags, creates menu items with action listeners, and populates a map.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low lexical overlap (Jaccard 0.20354) and significant differences in API usage (File I/O vs GUI components) and domain-specific keywords, causing the model to miss potential higher-level similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled these as clones due to both performing I/O operations on text/URLs, using similar loop structures, and exception handling, which could be considered Type-4 semantic similarity under a broad interpretation.
- 共享行为: Both read line by line from a source using BufferedReader；Both use try-catch blocks to handle exceptions
- 行为差异: A writes classification results to a file; B populates a map with GUI menu items；A has nested loops and skips initial lines; B has a single loop and extracts substrings；A checks for ontology keywords; B creates ActionListeners
- 修正建议: Improve handling of structural similarity beyond lexical overlap；Incorporate data-flow analysis to better capture intent；Use graph-based representations to model control flow and data dependencies

### case_id=6448 FN partial_functionality

- 方法: `clonarFichero` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Clones a file from a FileInputStream to a destination file using FileChannel.
- B 摘要: Retrieves a resource as an InputStream, caching it locally if not already cached.
- 静态失败原因: Static BERT models rely heavily on token overlap and syntactic structure, which are low here (Jaccard 0.14); they miss the abstract I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone due to the shared high-level functionality of copying data from an input to a local file, accepting partial similarity as Type-4.
- 共享行为: Both involve reading from an input source and writing data to a file.
- 行为差异: Different input sources: local FileInputStream vs. remote URL.；Different output mechanisms: FileChannel transfer vs. Buffered streams.；Function B includes caching and HTTP request logic.；Different return types: boolean vs. InputStream.
- 修正建议: Enhance models with dataflow analysis to capture read-write patterns.；Train on abstracted I/O operations to improve detection of partial functionality clones.

### case_id=6449 FP boilerplate_overlap

- 方法: `hashPasswordForOldMD5` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes MD5 hash of a password and returns hex string.
- B 摘要: Handles a Struts action for classifying a concept by sending XML data to a remote service and processing the response.
- 静态失败原因: Static BERT models may have been misled by overlapping lexical tokens like 'StringBuffer', 'try', 'catch', 'for', 'byte', etc., or by the presence of similar code structures (digest? but method B has no digest). Possibly the model over-generalized from training data where methods with similar structural patterns (e.g., building a string from bytes) were common.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these as clones because they have entirely different functionality, despite some superficial code patterns (try-catch, StringBuilder, loops) being common. BCB requires meaningful functional similarity.
- 行为差异: One computes a cryptographic hash; the other performs a web service call for ontology classification.；Different input/output: password string vs HTTP request/response.；Different exception handling: IllegalStateException vs IOException/ServletException.
- 修正建议: Train models to focus on semantic roles (e.g., input-output mapping) rather than local patterns.；Include type information and API calls in representations to differentiate domains.；Use control-flow dataflow analysis to capture computation essence.；Augment training with pairs that have lexical overlap but different semantics (hard negatives).

### case_id=6450 FN benchmark_preference_bias

- 方法: `copyFileChannel` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file using FileChannel, optionally preserving modification time, with proper resource cleanup.
- B 摘要: Launches an Eclipse-based build configuration, checking project structure, processing POM files, and generating reverse engineering files.
- 静态失败原因: Static model correctly predicted non-clone (low similarity, distinct semantics); it did not fail. The error type FN indicates the model disagreed with the ground truth, which is likely incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled due to overbroad criteria or annotation error; both methods touch file I/O but at different abstraction levels and with no shared functionality.
- 共享行为: Both methods perform file I/O operations；Both use try-finally or try-catch for resource management
- 行为差异: copyFileChannel is a pure file copy utility; launch is a complex build/launch handler；launch involves project validation, XML parsing, property setting, and multiple file operations; copyFileChannel only copies a single file；launch creates files from templates; copyFileChannel duplicates an existing file；launch interacts with Eclipse workspace and API; copyFileChannel is independent
- 修正建议: Re-evaluate BCB annotation for this pair; likely false positive.；Use more precise clone definitions (e.g., functional similarity criteria).

### case_id=6451 FN partial_functionality

- 方法: `doTransfer` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Acts as an HTTP proxy, forwarding a request to another URL and returning the response.
- B 摘要: Reads a camera log from a URL, parses each line into records, sorts them, and stores them.
- 静态失败原因: Low token overlap (0.15) and vastly different control flow and API usage; static models lack understanding of high-level semantics and purpose.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might have considered both as 'reading from a URL and processing data', but the core functionality is very different (HTTP proxy vs. log parsing), making a clone annotation unlikely.
- 共享行为: Both open a URL connection and read from an input stream.
- 行为差异: Function A writes data to an HTTP response output stream; Function B does not write to any output stream.；Function A copies HTTP headers and uses request method; Function B does not handle headers.；Function B parses lines into CameraLogRecord objects and sorts them; Function A does no parsing or sorting.；Function A handles request and response objects; Function B only reads from a URL.
- 修正建议: Incorporate data flow analysis to distinguish writing vs. reading only.；Use AST-based features capturing overall structure and purpose.；Train on more diverse examples of non-clones with low token similarity but different semantics.

### case_id=6452 FN benchmark_preference_bias

- 方法: `run` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Processes pseudolocalization arguments to read files or stdin, apply a pipeline, and write transformed messages.
- B 摘要: Handles Eclipse launch configuration for NexOpen projects by validating project structure, processing XML files, and scheduling an installation job.
- 静态失败原因: Static BERT/GraphCodeBERT methods rely on token similarity and structural overlap; here token Jaccard is very low (0.06) and the code structure is completely different, making it correctly predict non-clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones based on a broad interpretation of 'input-processing-output' or 'file manipulation' patterns, ignoring the distinct domain and logic.
- 共享行为: Both perform file I/O operations；Both check for file existence before processing；Both use streams for reading/writing
- 行为差异: A processes text messages with a pseudolocalization pipeline; B processes Maven POM files and handles Hibernate dialect；A writes output to files or stdout; B schedules an InstallProjectAction and sets persistent properties；A is a command-line tool; B is an Eclipse plugin launch handler；A handles multiple files in a loop; B handles a single project configuration
- 修正建议: Re-evaluate BCB label for this pair; likely a false positive in the benchmark；If BCB label is correct, the model needs to learn high-level functional similarity beyond lexical/syntax, which is difficult；Use semantic-based methods that capture intent, but extremely challenging for such dissimilar functions

### case_id=6453 FN partial_functionality

- 方法: `copyResource` vs `uploadFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or local file) to a destination file using byte-by-byte streaming.
- B 摘要: Copies a local file to a target destination, optionally creating directories, with a rename optimization; falls back to buffered stream copy.
- 静态失败原因: Static models like GraphCodeBERT rely on lexical and syntactic patterns; the low token Jaccard (0.295) and structural differences (rename branch, URL handling, buffer usage) lead to focusing on dissimilarities, missing the high-level functional similarity of the core copy operation.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often annotates file copy/upload functions as clones even if one has extra features like rename or directory creation, because the core functionality of reading bytes from input to output is present and the variations are considered partial clones (Type-3/4).
- 共享行为: Both copy data from a source to a file destination using InputStream and OutputStream.；Both read and write bytes until end of stream.；Both close streams after copying.
- 行为差异: A can read from URL; B only from local file.；B attempts rename first; A always uses stream copy.；B creates parent directories if needed; A does not.；A reads/writes single bytes; B uses buffered array.
- 修正建议: Use data augmentation to create variants with and without rename/directory creation.；Incorporate data-flow analysis to highlight the core data transfer loop.；Train on more Type-3/4 clones with low lexical overlap.；Use AST-based similarity metrics that ignore variable names and syntactic sugar.

### case_id=6454 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts all hyperlinks and anchor texts from an HTML page given a URL using regex.
- B 摘要: Checks for a newer version of jEdit by reading a version file from a URL and comparing build numbers.
- 静态失败原因: The model may have overemphasized the common boilerplate pattern of opening a URL, reading lines, and the while loop structure, ignoring the divergent domain-specific logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically only clones similar functionality. Here, despite shared I/O boilerplate, the core tasks are unrelated, so BCB labels non-clone (0).
- 共享行为: Both open a URL connection and read lines using BufferedReader；Both use a while loop to read lines until null
- 行为差异: Function A parses HTML to extract links and texts; Function B parses version information lines；Function A returns a Vector array of links and texts; Function B shows GUI messages and returns void；Function A uses regex extensively; Function B uses simple string startsWith checks
- 修正建议: Incorporate structural or data-flow differences beyond token sequences；Use contrastive learning to distinguish similar boilerplate with different semantics；Focus on the return type and side effects to differentiate

### case_id=6455 FP boilerplate_overlap

- 方法: `importRoles` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Imports role names from an XML file accessible via a URL.
- B 摘要: Performs a Google image search, downloads the results page, extracts image URLs, and updates the UI with an image.
- 静态失败原因: The model likely over-relied on surface-level similarities such as URL creation, BufferedReader.readLine loop, and exception handling, ignoring the fundamental differences in purpose and output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels clones based on functional similarity; here the core functionality is different (XML role import vs image search), so they are likely non-clones despite shared HTTP boilerplate.
- 共享行为: Both fetch content from a URL using HTTP GET.；Both read the response line by line with BufferedReader.
- 行为差异: Function A parses XML to extract role names, while Function B parses HTML to extract image URLs.；Function A returns an ArrayList of role names, while Function B is void and updates UI components.；Error handling differs: A swallows exceptions and returns empty list, B shows error dialogs and continues execution.
- 修正建议: Incorporate method name semantics or context-level features.；Train on distinguishing actual data processing logic from boilerplate I/O code.；Consider return types and side effects as distinguishing signals.

### case_id=6456 FP lexical_or_api_overlap

- 方法: `readUNI` vs `getNetworkServersIPs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads tab-separated lines from a URL and adds concatenated id and desc to a provided vector.
- B 摘要: Reads a server list from a URL and extracts IPs from lines after '!SERVERS', returning a vector of IPs.
- 静态失败原因: The model likely overemphasized lexical and API overlap (URL, InputStream, Scanner, IOException, etc.) and the structural skeleton of try-catch-finally, while missing the distinct parsing semantics and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clones because the core functionality and output are entirely different despite shared URL-reading boilerplate.
- 共享行为: Opens a URL and reads lines from it；Parses each line using string manipulation；Handles MalformedURLException and IOException
- 行为差异: Function A modifies an input vector, while B returns a new vector；Different parsing logic: tab-delimited vs colon-delimited with state flags；Different error handling: A silently catches MalformedURLException, B prints stack trace; A catches generic Exception, B does not；Function B does not close the stream in finally, A does
- 修正建议: Incorporate control-flow and data-flow analysis to distinguish different parsing techniques；Use semantic similarity models that focus on the actual data transformations rather than surface API usage；Apply contrastive learning to differentiate reading-URL boilerplate from core logic

### case_id=6457 FP boilerplate_overlap

- 方法: `combineJs` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Combines multiple JavaScript files from URLs into one minified or concatenated file.
- B 摘要: Handles action events in a settings dialog, configuring paths for external tools and updating UI components.
- 静态失败原因: Static BERT likely overemphasized surface-level similarities like file I/O boilerplate, exception handling patterns, and loops, ignoring the high-level semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotation focuses on overall functionality and context; these functions have completely different purposes (file combining vs. UI event handling), so they are non-clones despite some low-level I/O overlap.
- 共享行为: Both perform file I/O operations；Both handle exceptions；Both use conditional logic based on configuration
- 行为差异: A processes JavaScript files from URLs; B handles UI events and preference saving；A creates temporary files for minification; B uses file chooser dialogs to select executables；A returns a Node element; B is a void method；A is a utility method; B is an event listener
- 修正建议: Incorporate method name and class context into embeddings；Use data flow analysis to distinguish different API usage patterns；Train with contrastive learning to separate similar boilerplate from true clones

### case_id=6458 FP boilerplate_overlap

- 方法: `populateResources` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Populates resources by loading templates and default images from classpath.
- B 摘要: Checks for software upgrade by querying a remote server and processing license/upgrade data.
- 静态失败原因: The static model likely relied on common tokens such as 'static', 'void', 'throws', 'try', 'catch', 'URL', 'BufferedReader', etc., leading to a false positive due to lexical/API overlap rather than semantic equivalence.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels them as non-clones because they perform entirely different business logic despite minor structural similarities. The benchmark prefers semantic similarity over boilerplate or API patterns.
- 共享行为: Both are static void methods that perform I/O operations and save data.；Both use try-catch for exception handling.；Both iterate over collections (List of URLs, array of images, array of upgrade entries).
- 行为差异: populateResources loads local templates and images; checkForUpgrade performs network request and database operations.；populateResources saves Resource and Image objects; checkForUpgrade manipulates UI and database.；populateResources uses file I/O; checkForUpgrade uses HTTP and SQL commands.
- 修正建议: Incorporate data-flow and control-flow analysis to capture actual operations.；Use graph-based representations (e.g., AST or PDG) to distinguish different functional behaviors.；Train on more diverse examples to reduce reliance on boilerplate patterns.

### case_id=6459 FN benchmark_preference_bias

- 方法: `doTransfer` vs `loadExistingAntlibs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Proxies an HTTP request to a remote URL by forwarding headers and body, then returning the response.
- B 摘要: Loads ant library definitions from classpath resources by reading package names and loading corresponding antlib XML files.
- 静态失败原因: The static model correctly predicted non-clone due to low token Jaccard (0.162) and clear semantic divergence, but BCB's annotation (likely an error or overly broad criteria) considered it a false negative.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as clone based on a very broad interpretation of 'resource loading via URL streams', ignoring the completely different domain-specific tasks and control flow.
- 共享行为: Both iterate over an Enumeration of URLs (request headers vs. classpath resources)；Both open InputStreams from URLs and read data；Both use InputStreamReader/BufferedReader to process text
- 行为差异: Function A acts as an HTTP proxy; Function B loads ant library configuration；Different input sources (HTTP request parameters vs. classpath resources)；Different output (HTTP response forwarding vs. internal antlib loading)；Distinct error handling (printStackTrace vs. RuntimeException)
- 修正建议: Improve BCB annotation consistency to avoid spurious clone labels；Enhance static models with domain-specific knowledge or task-oriented features

### case_id=6460 FP boilerplate_overlap

- 方法: `readData` vs `extractUninstallFiles`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads comma-separated tokens from static strings into hash sets and a map, building character and vowel length data.
- B 摘要: Extracts uninstall files by managing directories, copying old classes, and processing jar entries while handling upgrade logic.
- 静态失败原因: The model likely over-generalized due to common boilerplate patterns (e.g., loops, try-catch blocks, string manipulation) that appear in many Java functions, causing it to ignore the fundamental semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have entirely different purposes (data parsing vs. file extraction), no shared domain, and low lexical overlap, so they are not even partial functionality clones.
- 行为差异: Function A processes static string tokens into in-memory sets/maps; Function B performs file I/O, directory creation, and jar manipulation.；Function A uses StringTokenizer and loops; Function B uses file streams, zip entries, and error handling.；Function A has no file operations; Function B heavily depends on file system operations.；Function A is a private void method; Function B returns a File object.
- 修正建议: Improve training data to include more diverse non-clone pairs with similar syntactic structures but different semantics.；Incorporate dataflow analysis to distinguish between internal data processing and external I/O operations.；Add a feature that captures method purpose (e.g., return type, called system APIs) to better differentiate.

### case_id=6461 FN partial_functionality

- 方法: `addDataFromURL` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads lines from a URL and appends them with newlines to a 'thetext' buffer, with error handling that appends the URL string on exception.
- B 摘要: Reads a file or classpath resource lines without newlines into a StringBuffer and returns the string, with error handling that prints messages and exits the program.
- 静态失败原因: Static BERT methods rely on token overlap and structural similarity, which are low here (Jaccard=0.344). Different method names, source types, control flow (multiple try-catch), and output signatures masked the shared reading loop. The model failed to recognize the partial functional equivalence.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers this a clone because both functions implement the same core functionality of reading text lines from an input stream and accumulating them into a string buffer. Differences in source type, newline handling, output method, and error handling are considered non-essential for Type-3/Type-4 clone annotation in BCB.
- 共享行为: Reads lines from an InputStream using BufferedReader；Reads text input line by line；Appends lines to a text buffer (StringBuilder or StringBuffer)
- 行为差异: addDataFromURL reads from a URL; File2String reads from a file or classpath resource；addDataFromURL appends newlines; File2String does not；addDataFromURL appends to a global variable; File2String returns a String；Error handling differs: addDataFromURL prints and appends URL; File2String prints and exits
- 修正建议: Improve recognition of core input-output transformation patterns (read lines into buffer) across varying error handling and output styles；Incorporate data-flow analysis to abstract the reading operation；Use contrastive learning on pairs with high behavioral similarity but low token overlap

### case_id=6462 FN benchmark_preference_bias

- 方法: `readPage` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a webpage line by line, optionally skipping comment lines (starting with '#'), and returns the concatenated HTML string.
- B 摘要: Opens a URL or file stream, reads it via another method, and returns a status code indicating success or failure.
- 静态失败原因: The model focused on syntactic differences (different return types, method names, parameters) and low token overlap (0.227), missing the shared URL-reading core.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'reading from a URL' functions, thus functionally similar at a high level despite different outputs.
- 共享行为: Both open a URL stream using url.openStream().
- 行为差异: Return type and meaning: String (page content) vs int (status code).；Error handling: throws Exception vs catches IOException and sets status.；Source: only URL vs URL or local file.；Input processing: optional comment filtering vs delegated to another method.
- 修正建议: Incorporate more Type-4 (semantic) clone examples in training.；Use attention mechanisms on API calls to capture functional similarity.；Consider multi-task learning with clone and functional classification.

### case_id=6463 FN partial_functionality

- 方法: `fileDownload` vs `CheckUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL to a local directory, saving as download.pdf.
- B 摘要: Checks a URL by reading the first line of its HTTP response and returns it as a string.
- 静态失败原因: Static BERT models rely heavily on lexical and structural token overlap; here the overlap is low (0.246), method names are different, and the dissimilarities in return type and file I/O obscure the shared URL reading pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely treats both as instances of 'URL reading' operations, where the core functionality of connecting to a URL and reading data is present, and the differences in output handling are considered acceptable variants for partial functionality similarity.
- 共享行为: Both create a URL object from a string；Both open a URL connection and get an input stream；Both use BufferedReader to read from the stream；Both handle exceptions with a catch block
- 行为差异: fileDownload writes all bytes from the stream to a file; CheckUrl reads only the first line and returns it；fileDownload does not return a value; CheckUrl returns a String；fileDownload logs exceptions via Logger; CheckUrl prints stack trace；fileDownload uses int-by-int read loop; CheckUrl uses readLine()
- 修正建议: Incorporate higher-level task semantics via program summarization or API call sequences；Enhance representation with data flow graphs to capture the full read-write path；Use contrastive learning to distinguish between similar but not identical I/O patterns

### case_id=6464 FN partial_functionality

- 方法: `getFile` vs `copyDeleting`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies an XML attribute (endpoint), and saves the result to a temporary directory.
- B 摘要: Copies a file from a source to a destination using a byte buffer, with proper stream closure.
- 静态失败原因: The static model correctly identified the low token overlap (0.1) and different method signatures, but the BCB label likely reflects a preference for partial functionality similarity, causing a false negative from the benchmark perspective.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have annotated these as clones due to the common file I/O and stream copying pattern, considering it a broad Type-3 or Type-4 clone even though the high-level functionality differs.
- 共享行为: Both perform file I/O operations；Both use input and output streams；Both handle IOException by throwing or logging；Both close streams in finally blocks
- 行为差异: Function A downloads from a URL and parses XML; B copies a local file；Function A uses NIO channels and transferFrom; B uses byte array buffer；Function A creates temporary files and renames; B writes directly to destination；Function A includes logging and multiple exception types; B only throws IOException
- 修正建议: Use semantic similarity models that capture functional intent beyond literal I/O patterns；Improve training data to distinguish between generic I/O utilities and specific business logic

### case_id=6465 FN partial_functionality

- 方法: `fileDownload` vs `getURLContent`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads content from a URL and writes it to a fixed file name in a destination directory, with logging of exceptions.
- B 摘要: Fetches content from a URL and returns it as a String, throwing IOExceptions.
- 静态失败原因: Static models may focus on surface-level features like token overlap (Jaccard=0.22973 is low), method names are different ("fileDownload" vs "getURLContent"), and there are structural differences (one uses FileOutputStream, the other StringBuilder). They may miss the underlying semantic similarity of reading from a URL.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as clone because both functions implement the core task of retrieving content from a URL and processing it, despite differences in output method (file vs string). BCB often accepts pairs with similar functionality but different I/O patterns as Type-3/Type-4 clones.
- 共享行为: Both open a URL connection to a given URL.；Both read the input stream using BufferedReader.；Both iterate over the entire content (character-wise or line-wise).
- 行为差异: Function A writes the content to a file ("download.pdf") using FileOutputStream, while Function B accumulates the content in a StringBuilder and returns it.；Function A reads character by character, Function B reads line by line.；Function A catches and logs exceptions, Function B declares throws IOException.；Function A is void, Function B returns String.
- 修正建议: Incorporate more structure-aware representations such as data flow graphs to capture that both functions perform a URL read operation.；Use contrastive learning to recognize common API usage patterns across varying I/O configurations.；Train models to distinguish between I/O variations while recognizing shared sub-tasks.

### case_id=6466 FN partial_functionality

- 方法: `doTransfer` vs `sendRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request to another URL, acting as a proxy with full header propagation.
- B 摘要: Sends an XML request via HTTP to a servlet, with GZIP compression and response XML parsing.
- 静态失败原因: Static BERT models rely on token overlap and syntactic patterns; these functions share low token overlap (Jaccard 0.19) and differ in vocabulary and control flow, obscuring the semantic similarity of core HTTP communication.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: None
- 共享行为: Open an HTTP connection；Set request properties and output mode；Write data to output stream；Read response from input stream
- 行为差异: A uses HttpServletRequest and response objects; B uses string parameters and preferences.；A forwards all request headers; B sets a fixed Content-type header.；A sends request body as plain text; B compresses request with GZIP.；A copies response directly to output stream; B decompresses and builds XML document.
- 修正建议: Use graph-based code representations that capture data and control flow；Incorporate program dependency analysis to detect similar I/O operations；Train with more diverse positive examples of functional similarity

### case_id=6467 FP boilerplate_overlap

- 方法: `md5` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes the MD5 hash of a string and returns its hexadecimal representation.
- B 摘要: Processes an HTTP request to classify a concept, involving session validation, parameter extraction, and an HTTP call to an external service.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by common Java patterns like 'for' loops, 'StringBuffer', and 'if' statements, plus the presence of 'catch' blocks, causing over-generalization despite very low token overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones for functions with clearly different domains (hashing vs. web workflow) even if they share some syntactic similarities.
- 共享行为: Both use StringBuffer to build strings；Both contain loops and conditional statements
- 行为差异: A performs cryptographic hashing, B performs web request handling and business logic；A has no external I/O, B involves network communication and session management；A is a standalone utility, B is part of a Struts action framework
- 修正建议: Incorporate dataflow analysis to distinguish control-flow vs. computational logic；Use AST-based features to capture structural differences；Augment training with more diverse non-clone pairs that share boilerplate but differ semantically

### case_id=6468 FP boilerplate_overlap

- 方法: `main` vs `displayDiffResults`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file, generates adapter classes, and writes them to a JAR file.
- B 摘要: Creates an HTML report of file differences and launches a browser to display it.
- 静态失败原因: The static BERT model likely focused on lexical and API-level overlap (e.g., both use File, FileOutputStream, BufferedWriter, IOException, out.write, out.close), mistaking these boilerplate patterns for deeper semantic equivalence. It failed to capture the distinct domain-specific logic and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the two functions have completely different high-level purposes: one is for generating Java adapters, the other for displaying diff results. Even under broad Type-4 semantics, they share no meaningful functional similarity.
- 共享行为: Both involve file I/O operations；Both handle exceptions
- 行为差异: Function A is a main entry point for code generation from Prolog; Function B is a private method for diff visualization.；Function A writes class files to a JAR; Function B writes an HTML report and opens it in browser.；Function A uses complex objects like FactVisitor, ClassWriter; Function B uses simple text writing.
- 修正建议: Incorporate control flow and data flow analysis to distinguish high-level purpose.；Use functional dependency graphs or program slicing to capture intent.；Enhance training with more examples of diverse API usage to avoid over-reliance on common I/O patterns.

### case_id=6469 FN partial_functionality

- 方法: `CopyTo` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file character by character from an image file to a destination file.
- B 摘要: Modifies a message in a locale-specific properties file, creating it via copy from English if needed.
- 静态失败原因: Static BERT models rely on token overlap and method-level semantics; the low Jaccard similarity (0.24) and different method names/contexts prevent recognizing the embedded copy loop as a clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels clones based on shared code fragments (Type-3/4), and the identical file-copy loop is a significant shared fragment, even though the overall methods differ in purpose.
- 共享行为: Both contain a loop that reads characters from a file using FileReader and writes them using FileWriter.
- 行为差异: Function A only performs file copy; Function B also reads properties, modifies a specific key-value pair, and writes back the updated content.；Function B handles file existence checks and exception handling differently.
- 修正建议: Introduce structural clone detection or data-flow analysis to identify shared subfunctions.；Consider program slicing to compare functional fragments.

### case_id=6470 FN dataflow_blindspot

- 方法: `doGet` vs `CopyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `dynamic_equivalence_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles HTTP GET request to retrieve and serve a portal page, with caching and permission checks.
- B 摘要: Copies a file from source path to destination path using FileChannel.
- 静态失败原因: The models rely on token overlap and structural patterns, which are very low (Jaccard 0.05) and completely different; they fail to abstract to the shared file I/O concept due to lack of semantic understanding.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本可能是 API 写法不同但行为等价的漏报。建议测试目标为 input_output_equivalence。
- BCB 偏好解释: BCB may consider both as file I/O operations with similar high-level goal of writing to a file, accepting broad Type-4 semantic similarity despite different contexts.
- 共享行为: Both involve writing data to a file (A writes cached page to temp file, B copies file content).
- 行为差异: A is an HTTP servlet method with complex control flow for page retrieval, permission checks, logging, and caching; B is a static utility method with straightforward file copy logic.；A operates on HttpServletRequest/Response, PortalRequest, Page objects; B operates on File, FileInputStream, FileOutputStream, FileChannel.；A writes a String to a file via FileWriter; B transfers bytes between channels.；A has extensive error handling and multiple branches; B has minimal error handling.
- 修正建议: Incorporate dataflow analysis to trace file I/O operations across different APIs.；Use a more abstract representation like code property graphs that capture high-level I/O operations.

### case_id=6471 FP lexical_or_api_overlap

- 方法: `writeFileType` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a file of URIs, fetches each URI, checks for RDF/OWL/RDFS content, and writes classification result to an output file.
- B 摘要: Fetches a YouTube video page, extracts the full screen URL by parsing the response for video_id and t parameters, and returns the constructed URL.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the lexical and API-level overlap (URL, BufferedReader, URLConnection, try-catch loops) and control flow similarities, ignoring the actual semantic purpose and different output handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the functions do completely different tasks (file type classification vs. YouTube URL extraction), even though they share some common I/O patterns.
- 共享行为: Both use URL, URLConnection, BufferedReader, and InputStreamReader to fetch a URL.；Both read lines from a web response in a while loop.
- 行为差异: Function A processes multiple URIs read from a file; Function B processes a single YouTube URL stored in an instance variable.；Function A writes classification results to a file; Function B returns a constructed URL string.；Function A checks for specific RDF/OWL/RDFS strings; Function B parses a YouTube video page for video_id and t parameters.；Function A has error handling that writes 'BROKEN' to file on failure; Function B just prints error and returns empty string.
- 修正建议: Incorporate more structural or semantic features, such as method name, variable names, and domain-specific context.；Use contrastive learning with harder negative examples that share API usage but differ in task.；Add attention to data flow and output types to distinguish different computations.

### case_id=6472 FN partial_functionality

- 方法: `invoke` vs `getXML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Invokes a remote method via HTTP POST with retry logic, deserializes JSON response and handles connection timeouts.
- B 摘要: Fetches XML from a given URL via HTTP GET, reads the response as a string, returns null on failure.
- 静态失败原因: Static BERT models rely heavily on lexical token overlap and structural patterns. The low Jaccard similarity (0.149) and different APIs (HttpClient vs URL, HttpPost vs openStream) mislead the model, while the shared high-level semantic pattern of fetching and reading a URL is not captured.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels functions with partial functional similarity as clones, especially when they share core HTTP request-response reading behavior despite differences in HTTP method, error handling, and data processing.
- 共享行为: Both construct a URL and make an HTTP request.；Both read the HTTP response content line by line.；Both return a string representation of the response body.
- 行为差异: Function A uses HTTP POST while B uses HTTP GET.；Function A includes retry logic and service discovery, B does not.；Function A deserializes JSON to a specific type, B returns raw string.；Function A throws exceptions on non-2xx status, B returns null on any error.
- 修正建议: Use dataflow-aware models that capture shared semantics of HTTP request-response loops.；Incorporate type-aware embeddings to recognize similar API usage patterns.；Add more training examples of broadly similar web service functions with different implementations.

### case_id=6473 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `PhoneSetImpl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads integers from a resource file and returns a HashSet of Integer objects.
- B 摘要: Reads lines from a URL, skips lines starting with "***", and populates a HashMap via parseAndAdd.
- 静态失败原因: The model likely overemphasized lexical and API overlap (e.g., URL, InputStreamReader, readLine) and ignored the different processing logic and return types, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the core functionality differs significantly: one reads integers into a set, the other reads structured lines into a map, with different filtering and output.
- 共享行为: Both open a stream from a URL and read lines sequentially.
- 行为差异: readZoneIDs parses each line as an integer and adds to a HashSet; PhoneSetImpl parses lines with custom logic and populates a HashMap.；PhoneSetImpl skips lines starting with "***" and updates a line counter; readZoneIDs does not filter lines.；readZoneIDs returns a collection; PhoneSetImpl is a constructor that initializes a map field.
- 修正建议: Incorporate data-flow analysis to distinguish different uses of stream data.；Train on more diverse pairs that share API patterns but differ in semantics.；Use type information (return type vs. side effect) as a feature.

### case_id=6474 FN benchmark_preference_bias

- 方法: `main` vs `testCopyUnknownSize`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.4`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to files.
- B 摘要: Tests copying an InputStream of unknown size to an OutputStream and verifies data.
- 静态失败原因: Low token overlap (0.13) and different method names/structures cause models to miss the shared I/O pattern.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as stream copying operations (Type-4 partial similarity) despite different contexts.
- 共享行为: Both involve reading from an InputStream and writing to an OutputStream
- 行为差异: A writes to files, B writes to in-memory stream；A uses ZipInputStream and loops over entries, B uses simple copy with unknown size；A is a main method with hardcoded URL, B is a test method with assertions
- 修正建议: Focus on dataflow rather than surface tokens；Use finer-grained I/O operation matching

### case_id=6475 FP lexical_or_api_overlap

- 方法: `GetResponse` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens an HTTP GET connection to a URL, reads the response line by line and concatenates them into a String, returning null if the response code is not OK.
- B 摘要: Creates an HTTP connection to a URL, sets request properties, reads the input stream into an RDF Model, and returns the Model, throwing RuntimeException on failure.
- 静态失败原因: Static BERT/GraphCodeBERT methods may have over-relied on lexical and API-level overlaps such as URL, HttpURLConnection, getInputStream, and exception types (MalformedURLException, IOException). The model may have learned a pattern of 'HTTP GET + read input stream' as a clone indicator, ignoring the divergent data flow and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have different return types (String vs Model) and different post-processing (text concatenation vs RDF parsing), indicating distinct high-level functionality. BCB typically requires strong functional equivalence or near-equivalence, which is not present here.
- 共享行为: Both open an HTTP connection to a URL；Both read from the input stream of the connection；Both catch MalformedURLException and IOException
- 行为差异: Function A returns a String of raw text; function B returns an RDF Model object；Function A only reads on HTTP_OK (200); function B reads regardless of response code；Function A returns null on error; function B throws RuntimeException；Function B sets additional HTTP request properties (Accept, Accept-Language); function A does not
- 修正建议: Incorporate data flow analysis to track how the input stream is processed；Add attention to return types and method signatures；Use contrastive learning with negative examples that share API calls but differ in logic

### case_id=6476 FN benchmark_preference_bias

- 方法: `getDatasetsList` vs `fileDownload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Retrieves a list of dataset names from a server URL, caching results in a map.
- B 摘要: Downloads a file from a URL and saves it to a local directory with fixed filename.
- 静态失败原因: Static models like GraphCodeBERT rely on structural and token similarity; although both functions share common tokens (URL, BufferedReader, IOException, Logger, close), the overall semantic intent differs significantly. The low token Jaccard (0.26) and distinct method signatures, return types, and inner logic (cache vs. file write) likely led to a false negative prediction under strict semantics, while BCB's broad criteria consider them clones.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotators may consider both as URL reading operations with similar error handling and resource management, thus classifying them as Type-3 or Type-4 clones despite differing high-level purposes.
- 共享行为: Open a URL connection；Read from a BufferedReader；Handle IOException with logger；Close the reader
- 行为差异: Function A returns a cached list of strings, while B writes to a file and returns void；A adds '?server=list' query parameter, B extracts filename from URL；A caches results in a HashMap, B does not cache；A rethrows RuntimeException, B only logs
- 修正建议: Incorporate explicit detection of boilerplate vs. core logic to align with BCB's broad criteria.；Use contrastive learning to distinguish similar structural patterns with different semantics.；Adjust threshold or apply ensemble methods that account for annotation bias.

### case_id=6477 FN boilerplate_overlap

- 方法: `doGet` vs `decodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles HTTP GET requests to display a portal page, with caching and permission checks.
- B 摘要: Decodes a Base64-encoded input file and writes the decoded content to an output file.
- 静态失败原因: Static BERT models rely on token-level overlap and surface patterns; here, token Jaccard is very low (0.083) and the API calls, variable names, and structure are dissimilar, causing the model to predict non-clone.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as clone if they consider partial functional similarity (both involve file I/O) or shared boilerplate (exception handling), but the core semantics are very different.
- 共享行为: Both perform file I/O operations (reading/writing files).；Both use try-catch-finally for exception handling.
- 行为差异: Primary functionality: web request handling vs. file format conversion.；Complexity: code_a has extensive logic for page retrieval, user permissions, and caching; code_b is a straightforward I/O utility.；API usage: code_a uses servlet and portal-specific classes; code_b uses standard Java I/O and Base64.；Output: code_a writes HTML to response or cache file; code_b writes decoded file bytes.
- 修正建议: Improve semantic understanding by incorporating functional role or higher-level behavior (e.g., data flow or purpose).；Use techniques that capture long-range dependencies and overall intent rather than local token matches.；Consider data flow or control flow graphs to distinguish core logic from boilerplate.

### case_id=6478 FP boilerplate_overlap

- 方法: `doVersionCheck` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Shows wait cursor, reads version-check URL from jEdit property, parses specific lines to extract devel and stable build numbers, then calls an overloaded method.
- B 摘要: Reads version string from a hardcoded URL and returns it, with basic error handling.
- 静态失败原因: Static BERT may over-rely on superficial token overlap (URL, BufferedReader, readLine) and structural similarity, missing crucial semantic differences like UI side effects, return type, and domain-specific parsing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the methods have different signatures (static void vs private static String), different domain contexts (jEdit vs kmttg), and different overall functionality despite shared boilerplate URL reading.
- 共享行为: Open a URL and read lines using BufferedReader；Close the stream after reading
- 行为差异: A has UI interaction (show/hide wait cursor), B does not；A uses jEdit property for URL, B uses hardcoded URL；A parses specific line prefixes (.build, .stablebuild), B takes the last line as version；A calls another method, B returns a String
- 修正建议: Incorporate method signature and return type information；Detect UI-related API calls (showWaitCursor, hideWaitCursor)；Distinguish between different URL sources (property vs hardcoded)；Model the control flow more precisely (e.g., return vs void)

### case_id=6479 FN boilerplate_overlap

- 方法: `decodeFileToFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Decodes a Base64-encoded file and writes the decoded bytes to an output file.
- B 摘要: Fetches a resource via URL, caches it locally, and returns an InputStream to the cached file or directly from the network.
- 静态失败原因: The static BERT/GraphCodeBERT model likely captured the significant semantic differences in purpose and control flow, leading to a non-clone prediction. It did not consider the boilerplate stream handling as sufficient for clone label, especially given low token overlap score (0.224). The model correctly rejected this pair, while BCB's label may be erroneous.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as clone due to superficial structural similarities, such as both having try-catch-finally blocks with stream closing and using similar I/O classes (InputStream, OutputStream, Buffered*). The annotation might have overlooked the completely different core functionality.
- 共享行为: Both use InputStream and OutputStream for I/O operations.；Both close streams in finally blocks.；Both print stack traces on exception.
- 行为差异: A performs Base64 decoding; B does HTTP-based caching and resource fetching.；A writes to a user-specified file; B returns an InputStream and may cache to a generated file.；B has conditional logic based on cache existence and modification dates; A does not.；A uses a fixed buffer size for reading; B reads byte-by-byte.
- 修正建议: Include higher-level semantic context such as method names and surrounding code to disambiguate purpose.；Use dataflow analysis to capture the core transformation (e.g., decode vs. fetch-cache).；Re-evaluate BCB annotation for this pair; consider it a possible labeling error.

### case_id=6480 FP long_range_semantics

- 方法: `DecodeMapFile` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Decodes a map file by XORing each byte with a key that increments.
- B 摘要: Parses multiple comma-separated strings and a complex configuration file to populate sets and hash maps.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by the presence of common keywords (e.g., 'HashSet', 'StringTokenizer', 'while') and structural patterns, or it failed to capture the long-range dependencies and actual semantics of the second function due to its length.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels non-clone because the functions have completely different purposes and no functional similarity; they operate on different data and produce different outputs.
- 共享行为: Use of basic Java I/O and collections
- 行为差异: Function A performs XOR encryption/decryption; Function B initializes data structures for Tibetan transliteration.；Function A reads/writes files; Function B parses strings and a configuration file.；Function A is simple and linear; Function B is complex with nested conditionals and error handling.
- 修正建议: Improve model ability to capture long-range dependencies and global program structure.；Incorporate dataflow analysis to distinguish between pure data transformation and configuration parsing.；Use contrastive learning to emphasize functional similarity over lexical overlap.

### case_id=6481 FN benchmark_preference_bias

- 方法: `addQDInformation` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Updates project information by reading a local or remote qdinfo.dat file and parsing lines starting with 'pg ' and 'pt ' to modify internal state.
- B 摘要: Registers a user by encoding password, setting default authority, creating a forum user via URL, persisting the user, and sending a confirmation email.
- 静态失败原因: A static BERT model might have failed to detect this as a non-clone because it focuses on local token patterns and may overemphasize shared API calls like URL, BufferedReader, and readLine, leading to a false positive in similarity estimation. However, given the low token Jaccard (0.125), it likely correctly predicted non-clone. The BCB label might be an annotation error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered these clones due to the shared use of URL connections, BufferedReader, and line-by-line parsing, which are common patterns in data retrieval tasks. However, the overall functionality is quite different.
- 共享行为: Both methods read from an external source (file or URL) using a BufferedReader and readLine loop.；Both methods handle exceptions with try-catch blocks.；Both methods parse lines from the input to extract data.
- 行为差异: Method A has no return value, while Method B returns a boolean.；Method A updates internal project information, while Method B registers a new user in a system.；Method A handles local or remote file reading, while Method B only uses URL connections.；Method A parses specific 'pg ' and 'pt ' prefixes, while Method B reads a single line to set forumID.
- 修正建议: If the BCB label is correct, models need to better capture high-level semantic differences beyond API usage.；If the BCB label is incorrect, the benchmark annotation needs reviewing.

### case_id=6482 FN partial_functionality

- 方法: `runScript` vs `issueCommandToServer`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from the server URL and returns its content as a string, or 'error!' on failure.
- B 摘要: Sends a command and capsule data to the server via HTTP POST and returns the response string.
- 静态失败原因: The low token Jaccard similarity (0.0769) and different method signatures, control flows, and API calls make it difficult for static BERT models to capture the high-level similarity that BCB annotators may have perceived.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: None
- 共享行为: Both involve network communication and return a string
- 行为差异: Different input parameters: A takes a script name, B takes a command and a capsule object；A reads a file via GET, B sends a command via POST with content-type；A uses raw byte reading, B uses buffered line reading；A catches exceptions and returns 'error!', B throws IOException
- 修正建议: Incorporate data flow and API call patterns to capture I/O operations；Use dynamic analysis or execution traces to compare runtime behavior；Utilize a graph-based representation that abstracts function intent

### case_id=6483 FN partial_functionality

- 方法: `issueCommandToServer` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Sends an HTTP POST command to a server with a capsule object and returns the response as a string.
- B 摘要: Reads data from a URL or file and returns a status integer.
- 静态失败原因: Static BERT/GraphCodeBERT models may have failed because they rely on token similarity and structural patterns. The low Jaccard and different method names likely caused a low similarity score. Also, the models may not capture the partial similarity in I/O operations due to the distinct overall logic and different return types.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label it as clone due to the common pattern of opening a network connection and reading data, overlooking the write operation and return type differences. The annotators might have considered them as both performing I/O from a URL.
- 共享行为: Both open a connection/stream to read data from a URL；Both use buffered I/O (BufferedReader/BufferedInputStream)；Both handle IOException (either throw or catch)
- 行为差异: Method A writes data to the server before reading, while B only reads；Method A returns a String response, B returns an int status；Method A takes command and ChangeCapsule; B takes a name string；B also supports file reading, A only HTTP
- 修正建议: Improve model's ability to recognize shared I/O patterns despite different method names and return types.；Incorporate data-flow analysis to detect common operations like opening streams and reading data.；Add supervision specifically for Type-4 clones that share only high-level functionality.

### case_id=6484 FN partial_functionality

- 方法: `getURLContent` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads entire content from a URL and returns as a String.
- B 摘要: Reads from a URL or file, processes via another read method, and returns a status code.
- 静态失败原因: Low token overlap (0.16) and surface-level differences (return types, method names, file handling) caused static BERT to miss the semantic connection of URL reading and I/O processing.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered these as clones because both functions involve reading from a URL and handling I/O, which is a core shared functionality despite differences in return type and additional file reading capability.
- 共享行为: Both open a URL connection and read input from it.；Both handle IOException.
- 行为差异: Function A only reads from URLs, while B also reads from local files.；Function A returns the entire content as a String, B returns a status code.；Function A uses BufferedReader to read line by line and appends newlines, B uses BufferedInputStream and delegates to another read method.；Function B sets a status field and returns an int, while A directly returns the string.
- 修正建议: Incorporate data flow analysis to capture URL opening and stream reading patterns.；Use control flow and I/O operation sequences to detect similar network read operations.；Train on pairs with low lexical but high structural similarity.

### case_id=6485 FP lexical_or_api_overlap

- 方法: `populateResources` vs `readZoneIDs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Populates predefined templates and images from resources into the database.
- B 摘要: Reads zone IDs from a resource file and returns them as a HashSet of integers.
- 静态失败原因: Static BERT likely overfitted on shared API calls (getResource, openStream, readLine, try-catch) and didn't capture the distinct overall semantics and side effects (save vs. return).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have no overlapping functionality; they serve entirely different purposes (populating resources vs. reading IDs).
- 共享行为: Both read from resources using URL and InputStream；Both use a loop to read lines from a file；Both handle IO exceptions
- 行为差异: A saves data to database via Resource, Image, Property objects; B returns a HashSet；A processes both XML/text templates and multiple images; B parses integers from a single file；A uses Logger for errors; B uses printStackTrace
- 修正建议: Incorporate data flow analysis to track whether data is stored or returned；Enhance modeling of return types and method signatures；Add contrastive learning to distinguish functions with similar API usage but different goals

### case_id=6486 FN benchmark_preference_bias

- 方法: `testCodingEmptyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Test method that writes data to a file channel using LengthDelimitedEncoder and verifies the output.
- B 摘要: Method that builds a website by processing XML, replacing strings, and writing output files.
- 静态失败原因: Static BERT (or GraphCodeBERT) likely correctly identified non-clone due to low token overlap and very different code structures. It did not fail; BCB label may be incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotation may have been too broad, considering any file-handling method as similar, but this is likely an annotation error.
- 共享行为: Both use file I/O (reading and writing files)
- 行为差异: Different purpose: testing encoder vs building website；Different libraries and data flow；Function A is simple and sequential, function B has loops and conditionals；Function A checks encoder completion, function B handles exceptions and transformations
- 修正建议: Review BCB annotation guidelines for this pair to ensure consistency；Consider whether file I/O alone qualifies as clone; likely not

### case_id=6487 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens a URL from jEdit property, reads lines, parses version strings, and calls overloaded version check method.
- B 摘要: Downloads a file from a URL to a local destination, tracking progress via MessageFrame.
- 静态失败原因: Static BERT (like GraphCodeBERT) may rely on overlapping tokens like 'URL', 'InputStream', 'readLine', 'close', and the common structural pattern of opening a URL and reading stream, leading to a false positive. It likely misses the semantic divergence in data processing and UI interaction.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB generally labels non-clones when functions have distinct purposes (version check vs download) despite both using URL/stream, because BCB emphasizes functional similarity over structural overlap.
- 共享行为: Both involve opening a URL and reading from an input stream.
- 行为差异: A performs version string parsing from text lines, while B performs binary file download and saves to disk.；A interacts with a View UI element for cursor and error display, while B updates a progress frame.；A has no file output, B writes to a file.；A calls another method with parsed versions, B returns boolean.
- 修正建议: Incorporate dataflow analysis to track how the read data is used (parsed vs. written to file).；Add awareness of method signatures and return types.；Use contrastive learning or task-specific fine-tuning to separate different high-level tasks.

### case_id=6488 FP lexical_or_api_overlap

- 方法: `copyFile` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Copy a file from source to destination using FileChannel.
- B 摘要: Read and parse configuration data from strings into various sets and maps.
- 静态失败原因: Static BERT models may have been misled by lexical overlaps such as 'IOException', 'close()', and loops, while lacking understanding of the overall different intents.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have completely different purposes and no meaningful semantic overlap, even if they share some generic programming patterns.
- 共享行为: Both involve some form of data processing；Both use exception handling
- 行为差异: Different input/output: file copy vs. string parsing；Different data structures: FileChannel vs. HashSets and HashMaps；Different complexity: simple file I/O vs. complex parsing logic
- 修正建议: Incorporate control flow and data flow analysis to capture function semantics；Use code summarization to differentiate high-level purpose；Train on more diverse negative examples with similar tokens but different semantics

### case_id=6489 FN partial_functionality

- 方法: `doRawRequest` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with given data and returns the response as a string.
- B 摘要: Sends a hardcoded HTTP POST request with parameters and prints the response to the console.
- 静态失败原因: Static BERT methods like GraphCodeBERT rely heavily on token similarity and structural overlap. The two functions have low token Jaccard (0.1667), different method signatures (doRawRequest vs main), and different patterns (parameterized vs hardcoded, return vs print). The model likely missed the high-level semantic similarity of the HTTP request-response loop due to these surface-level differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-3/Type-4 clones as clones when they share significant behavioral similarity, even if not exact. Here, both functions perform the core task of making an HTTP POST and reading the response, so BCB likely considered them functionally similar enough.
- 共享行为: Both open a URL connection；Both set doOutput to true；Both write data to the output stream；Both read the response via BufferedReader
- 行为差异: A takes input parameter; B uses hardcoded parameters；A returns response string; B prints response to console；A uses generic URLConnection; B uses HttpURLConnection and sets request method explicitly；B includes additional print statements and setup for parameters
- 修正建议: Use graph-based representations that capture data flow and control flow to better identify functional equivalence beyond token overlap.；Incorporate contrastive learning with positive pairs that differ in non-functional details (like parameterization or output method) but share core behavior.；Enhance training with code summarization or documentation to capture high-level intent.

### case_id=6490 FP long_range_semantics

- 方法: `readData` vs `createNew`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads and parses configuration data from string fields and a file, populating multiple sets and a hash map.
- B 摘要: Creates a new file resource from an input stream, with ownership checks and special handling for certain filenames.
- 静态失败原因: The static model likely focused on surface-level similarities such as both methods having try-catch blocks, file operations, and loops, while missing the drastically different overall semantics due to long-range dependencies and complex control flow in function A.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels non-clones when functions have different purposes and no significant shared behavior, even if both perform file I/O. The functions are completely unrelated in functionality.
- 行为差异: Function A parses tokens and populates data structures; Function B writes an input stream to a file.；Function A is a private static void method; Function B is a public method returning a Resource.；Function A involves reading from a file and parsing lines; Function B writes to a file.；Function A uses StringTokenizer and HashSet/Map manipulations; Function B uses FileOutputStream and IOUtils.
- 修正建议: Incorporate data flow or control flow analysis to capture actual data transformations.；Use sequence models with attention to better handle long-range dependencies and distinguish different file operations (read vs. write).

### case_id=6491 FN benchmark_preference_bias

- 方法: `testSimpleQuery` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: JCR test method that writes XML user data, queries for teamspace, and verifies results.
- B 摘要: Main method that downloads a KMZ file from HTTP, extracts ZIP entries, and writes them to local files.
- 静态失败原因: Static BERT/GraphCodeBERT likely correctly predicted non-clone due to low token overlap and different APIs. The model failed to match the BCB label, which seems inconsistent with typical clone definitions.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have considered both as 'data streaming and resource management' tasks, despite different domains. However, token similarity is very low (0.12), making this an unlikely clone even in broad Type-4; the BCB label may be an error in the dataset.
- 共享行为: Both use InputStream and OutputStream for I/O operations.；Both close streams after use.
- 行为差异: A is a unit test; B is a command-line tool.；A manipulates JCR nodes and XML; B manipulates ZIP archives and file system.；Different APIs: JCR vs. java.util.zip.；Different overall goals: querying repository vs. extracting archive.
- 修正建议: Review BCB ground truth for this pair; consider relabeling as non-clone.；If BCB label is correct, improve model by emphasizing high-level I/O patterns across domains.；Incorporate more structural and control-flow similarity measures.

### case_id=6492 FN benchmark_preference_bias

- 方法: `convert` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Converts an ACRNEMA stream file to DICOM format, assigning UIDs and handling pixel data.
- B 摘要: Launches a NexOpen project configuration, checking Maven pom files and setting Hibernate dialect.
- 静态失败原因: Static BERT correctly predicted non-clone (0) because it recognized the semantic gap; the BCB label is likely erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled due to both functions containing file I/O, try-finally blocks, and exception handling, but their domains and purposes are entirely different.
- 行为差异: Function A processes medical image data (ACRNEMA/DICOM), while function B configures Eclipse project settings.；Function A reads and writes binary pixel data, function B manipulates XML documents and properties.；Function A checks UIDs and pixel data length; function B checks project structure and file existence.；Function A uses low-level I/O streams; function B uses higher-level Eclipse API and XML handling.
- 修正建议: Re-evaluate BCB annotation for this pair to correct the false positive.；Improve BCB guidelines to avoid labeling functions from vastly different domains as clones.；Consider using functional or API-level similarity instead of surface patterns.

### case_id=6493 FN boilerplate_overlap

- 方法: `uploadFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Uploads a file to a target location, attempting rename first then fallback to stream copy.
- B 摘要: Retrieves a resource as an InputStream with caching from a URL to a local file.
- 静态失败原因: The model may have focused on the common stream copy loop (e.g., while ((bytes = in.read(line)) != -1) out.write(...)) and missed the distinct high-level contexts (local file upload vs. URL download with caching). The long and complex code in B may have diluted the overall semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled these as clones due to both performing file I/O and stream copying, possibly considering them as Type-4 (functionally similar but different). However, the token Jaccard is low and the intents are distinct, so this may be an annotation error.
- 共享行为: Both involve reading bytes from an input source and writing them to an output destination.
- 行为差异: uploadFile is a local file move/copy; getResourceAsStream downloads a resource from a URL with caching.；uploadFile uses renameTo for efficiency; getResourceAsStream always does streaming.；uploadFile does not handle HTTP or caching; getResourceAsStream has complex cache logic and HTTP handling.；Error handling differs: uploadFile lets IOException propagate; getResourceAsStream catches exceptions and returns null.
- 修正建议: Incorporate call context or API usage patterns to distinguish local file operations from network operations.；Use program dependence graphs or control-flow analysis to capture different intents.

### case_id=6494 FP other

- 方法: `encodeFileToFile` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Base64-encodes an input file and writes the encoded data to an output file.
- B 摘要: Reads a configuration file or string, tokenizes by comma, and populates various data structures (sets and maps) used for Tibetan transliteration.
- 静态失败原因: Despite low token overlap, the model may have been misled by superficial similarities (e.g., both have try-catch blocks, while loops, or variable names like 'read'). However, such common patterns are insufficient for semantic equivalence, indicating the model lacks deep understanding of functionality.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BigCloneBench annotations typically require significant functional overlap. These two functions have entirely different purposes (file encoding vs. configuration parsing), so they are correctly labeled non-clones.
- 行为差异: Function A performs file I/O with base64 encoding; Function B parses configuration strings and populates in-memory data structures.；Function A uses InputStream/OutputStream for encoding; Function B uses StringTokenizer and HashSet/Map for parsing.；Function A has a success return value; Function B is void and modifies global or instance variables.；Function A handles a single file pair; Function B processes multiple predefined string fields without writing to file.
- 修正建议: Train on more diverse negative examples with similar syntactic structures but different semantics.；Use graph-based representations to capture dataflow and control dependencies beyond token sequences.；Incorporate functional level descriptors or method summaries to improve semantic understanding.

### case_id=6495 FN benchmark_preference_bias

- 方法: `copy` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file using NIO FileChannel.transferTo.
- B 摘要: Launches a NexOpen project in Eclipse, performing XML handling, property setting, and conditional file copy.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on token overlap and structural similarity, which are very low (Jaccard=0.0667), leading to a correct non-clone prediction that contradicts the subjective BCB annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to the presence of file copying functionality in both methods, focusing on partial similarity rather than overall purpose.
- 共享行为: Both involve file I/O operations, specifically copying a file in A and a conditional file copy in B.
- 行为差异: A is a simple file copy utility; B is a complex launch method with many steps like XML parsing, property management, and project operations.；A operates only on file channels; B uses streams, properties, and Eclipse resources.；B has extensive error handling and logging; A simply throws exceptions.
- 修正建议: Train models to recognize partial functionality similarity or adopt a hierarchical clone detection approach that considers sub-tasks.；Re-evaluate BCB annotations for consistency and clarity regarding partial clones.

### case_id=6496 FP boilerplate_overlap

- 方法: `main` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A main method that parses a Prolog file, generates adapter code, and writes a JAR file.
- B 摘要: A utility method that copies a file from source to destination using byte streams.
- 静态失败原因: The static model likely overfit on common boilerplate patterns (e.g., try-catch, resource handling) and the presence of I/O-related keywords (File, InputStream, IOException), despite the low token overlap. It failed to capture the vastly different program logic and library usage.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the two functions have entirely different high-level purposes and no meaningful functional overlap beyond trivial I/O primitives, which is insufficient for Type-3/Type-4 similarity.
- 共享行为: Both perform file I/O operations.；Both handle IOException.；Both close resources (explicitly or via framework).
- 行为差异: Function A is a complex pipeline: parsing, code generation, serialization, and JAR assembly.；Function B is a simple byte-level file copy with stream handling.；A uses many external libraries (PrologParser, ASM, etc.), B uses only standard Java IO.；A writes a structured JAR file, B writes an exact binary copy.
- 修正建议: Incorporate control-flow and data-flow analysis to distinguish high-level intent.；Add negative samples with similar boilerplate but different functionality during training.；Use graph-based representations (e.g., AST or CFG) to capture structural differences.

### case_id=6497 FP boilerplate_overlap

- 方法: `readZoneIDs` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads integer IDs from a resource file and returns them as a HashSet.
- B 摘要: Performs a version check by reading lines from a URL and invoking another method with extracted version strings.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the lexical and structural similarity of common I/O patterns (URL, openStream, readLine) and missed the functional divergence due to different data usage and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the two functions have fundamentally different purposes despite sharing boilerplate I/O code.
- 共享行为: Both open a URL and read lines from it using a reader.；Both use a try-catch block to handle exceptions.；Both loop through lines until null.
- 行为差异: Function A returns a set of integers; Function B has void return and calls another method.；Function A uses LineNumberReader; Function B uses BufferedReader.；Function A parses each line as integer; Function B checks line prefixes and extracts substrings.；Function A prints stack trace on exception; Function B shows GUI error dialog.
- 修正建议: Incorporate dataflow analysis to track how parsed data is used.；Focus on method signatures and return types to distinguish purposes.；Use contrastive learning on pairs with high boilerplate overlap but different semantics.

### case_id=6498 FP lexical_or_api_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses command-line arguments, reads a Prolog file, generates adapter code, and writes output files.
- B 摘要: Copies a file from source to destination using a buffer.
- 静态失败原因: The model may have been misled by overlapping API usage (File, InputStream/OutputStream, IOException) and structured exception handling, ignoring the overall semantic difference in goals.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the two functions implement completely different tasks: one is a complex workflow for adapter generation, the other is a simple file copy utility.
- 共享行为: Both involve file I/O operations like reading and writing files；Both handle exceptions (IOException)
- 行为差异: A performs complex parsing and code generation, while B only copies a single file；A has command-line argument handling and conditional logic, B has none；A writes multiple artifacts (JAR, serialized data), B writes a single destination file
- 修正建议: Improve model's ability to capture high-level task semantics beyond low-level API patterns；Incorporate control flow and data dependency analysis to distinguish complex workflows from simple utilities

### case_id=6499 FN benchmark_preference_bias

- 方法: `main` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Writes library license information to a file by scanning a directory of JAR files with metadata.
- B 摘要: Launches a NexOpen project configuration, checks for pom.xml files, processes them, and sets up Hibernate properties.
- 静态失败原因: The static model may have incorrectly relied on overlapping API calls (e.g., File, InputStream) or structural patterns like file handling loops, despite the low token Jaccard. Alternatively, benchmark noise.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Likely a misannotation in BCB, as there is no significant functional similarity. Possibly the annotator considered both as 'writing output' or 'processing files', but that is too broad.
- 行为差异: Function A is a utility for generating a license file; Function B is an Eclipse plugin launch handler.；A uses file I/O to write license text; B uses project resources, XML processing, and Maven POM handling.；A deals with a fixed set of libraries; B handles project-specific configurations like Hibernate dialects and reverse engineering files.；A is a static main method; B is an instance method with launch lifecycle and progress monitoring.
- 修正建议: Review BCB annotation for this pair; likely should be non-clone.；Use more robust semantic models that capture overall program intent.

### case_id=6500 FN benchmark_preference_bias

- 方法: `getFile` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint address in the XML, and saves it locally.
- B 摘要: Reads a DICOM image file, parses it, and rewrites it to a new file.
- 静态失败原因: The model likely relied on lexical and structural overlap, which is low (Jaccard 0.072). It may have learned to reject pairs with different library calls and domain terms. Since BCB's label is unexpected, the model correctly predicted non-clone under typical clone definitions.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this pair as clones due to both performing file I/O operations with a read-transform-write pattern, despite different domains. However, this interpretation is very broad and likely a mislabel.
- 共享行为: Both read from an input source and write to an output destination.；Both handle I/O exceptions.
- 行为差异: Function A downloads from a URL, Function B reads a local file.；Function A manipulates XML/WSDL, Function B manipulates DICOM medical images.；Function A uses URLConnection and file channels, Function B uses ImageIO and DICOM-specific APIs.；Function A returns a file path, Function B is void and writes directly.
- 修正建议: Re-evaluate BCB annotation for this pair; likely a labeling error.；If BCB intends broad functional similarity, adjust training data to include diverse I/O operations.；Use models that capture high-level intent beyond lexical overlap.
