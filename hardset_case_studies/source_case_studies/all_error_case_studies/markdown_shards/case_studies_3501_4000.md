# Error Case Studies 3501-4000

- Source model: `configured-llm`
- Cases: `3501` to `4000`

### case_id=3501 FN boilerplate_overlap

- 方法: `register` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Registers a user by encoding password, setting default authority, generating email hash, calling external phpBB URL for registration, persisting user, and sending confirmation email.
- B 摘要: Performs version check by reading version info from a URL, parsing build numbers, and calling a method to display version dialog.
- 静态失败原因: Static BERT models rely on token-level embeddings and attention; low token overlap (Jaccard 0.14) and different domain terms cause the model to miss the structural similarity of the URL reading pattern, leading to a false negative.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a clone because both functions contain a common code idiom of reading from a URL with BufferedReader readLine in a try-catch block, which constitutes partial functionality similarity acceptable for Type-3/4 clones.
- 共享行为: Both open a URL and read lines from it using BufferedReader；Both handle IOException with error logging or UI error display
- 行为差异: Function A modifies database and sends email; Function B only reads data and displays UI；Function A involves complex object manipulation and multiple side effects; Function B is a static utility with no persistent side effects；The data read from URL is processed differently: A sets forumID, B extracts build strings
- 修正建议: Use AST-based or graph-based models to capture structural patterns；Incorporate dataflow analysis to match control flow and API usage；Add a metric for detecting partial functional similarity

### case_id=3502 FN benchmark_preference_bias

- 方法: `testNetworkHTTP` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Test method making multiple HTTP GET requests to various URLs, discarding the response.
- B 摘要: Private static method reading comma-separated tokens from static strings and populating multiple hash sets and a mapping for character processing.
- 静态失败原因: Static BERT correctly predicted non-clone; it did not fail. The mismatch is due to BCB label being erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have incorrectly labeled this as clone due to a broad notion of 'data reading', but the actual purposes are entirely different; likely a labeling error.
- 共享行为: Both are void methods with try-catch blocks；Both involve loops reading input (network lines vs string tokens)
- 行为差异: Code A performs network I/O; Code B performs local string tokenization；Code A discards read data; Code B stores data in static collections；Code A is a test method; Code B is a setup/initialization method；Code A uses URL and HttpURLConnection; Code B uses StringTokenizer and HashSet
- 修正建议: Re-evaluate BCB label for this pair；Consider that high-level 'data reading' is too generic to define clone

### case_id=3503 FN partial_functionality

- 方法: `testNetworkHTTP` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs multiple HTTP GET requests to various URLs, reads and discards response lines.
- B 摘要: Reads a resource from the classpath, builds a string from its lines, and updates a GUI component.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token overlap and surface-level structure. The low Jaccard similarity (0.18) and differing method names (testNetworkHTTP vs run) likely led to a non-clone prediction, despite the underlying similarity in I/O operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often annotates clones based on similar control flow and I/O patterns (e.g., opening a resource, reading lines), even if the overall functionality differs. The shared pattern of URL-based line reading is sufficient for a positive label.
- 共享行为: Both open a URL-like resource；Both read lines using BufferedReader；Both handle exceptions in try-catch blocks
- 行为差异: A makes multiple network requests with parameters; B reads a single local resource；A discards all content read; B builds a string and displays it in GUI；A uses HttpURLConnection; B uses ClassLoader.getResource；A catches IOException only; B catches Exception
- 修正建议: Incorporate dataflow analysis to capture sequences of stream operations；Use API call sequence embeddings to recognize similar I/O patterns despite low token overlap；Train on BCB-style annotations which accept partial functionality clones

### case_id=3504 FP boilerplate_overlap

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses comma-separated tokens to populate multiple sets and maps for Tibetan transliteration.
- B 摘要: Copies a file from source to destination using NIO FileChannel.
- 静态失败原因: The static BERT model likely overemphasized the shared file I/O patterns and exception handling boilerplate, ignoring the vast difference in actual logic, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these as non-clones because their core functionality (parsing data structures vs. file copy) is completely different despite both using file I/O.
- 共享行为: Both involve file I/O operations (reading/writing files).
- 行为差异: One parses tokenized strings into sets/maps, the other copies bytes between files.；Different input types: one uses global string fields, the other uses File arguments.；Different output: one populates data structures, the other writes to a file.
- 修正建议: Improve model to focus on the main logic vs. boilerplate code.；Use dataflow analysis to distinguish between reading for parsing vs. copying.

### case_id=3505 FP lexical_or_api_overlap

- 方法: `main` vs `saveFileData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses command-line arguments, reads a Prolog file, generates adapter classes, and builds a JAR file with annotations and serialized data.
- B 摘要: Saves file data by copying file channels and optionally updating image dimensions and deleting thumbnails.
- 静态失败原因: The model likely overemphasized lexical overlaps such as 'File', 'FileChannel', 'FileInputStream', 'IOException', and 'transferTo', which are common in file handling code; it failed to capture the distinct high-level semantics and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeling is consistent because the two methods serve entirely different purposes and have no meaningful functional similarity beyond trivial file I/O common to many programs.
- 共享行为: Both use file I/O operations with FileInputStream/FileOutputStream and FileChannel.；Both have exception handling (try-catch or throws).
- 行为差异: Function A is a complete program entry point with argument parsing and complex adapter generation; Function B is a utility method for saving a single file.；Function A uses Prolog parsing and class generation; Function B involves resource caching and image processing.；Function A writes to a JAR file and handles class loading; Function B manipulates file channels and thumbnail deletion.
- 修正建议: Train the model with more negative examples that share vocabulary but differ in purpose.；Incorporate control-flow and data-flow features to distinguish high-level functionality.；Use contrastive learning to push apart embeddings of semantically different functions that share API calls.

### case_id=3506 FN boilerplate_overlap

- 方法: `readIntoList` vs `getEncoding`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL, parses HTML lines to create and populate a map of JMenuItems with action commands and listeners.
- B 摘要: Reads HTTP headers and response body from a URL to extract and return the character encoding.
- 静态失败原因: Static BERT models like GraphCodeBERT may fail because they rely on token-level embeddings and can be misled by the high lexical overlap in common Java I/O boilerplate (e.g., BufferedReader, URL, readLine, while loop). The models may not capture the deep semantic difference in the processing logic (menu item creation vs. encoding detection). Additionally, the models might be sensitive to identifier names and method signatures, which differ significantly (readIntoList vs getEncoding, parameters, return types).
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a clone because both functions are private helper methods that read from a URL, process lines of input, and share a similar boilerplate structure (open connection, read lines, parse strings). In a large benchmark, such pairs are often considered Type-3 clones due to the high structural similarity and common I/O pattern, even though the specific functionality differs.
- 共享行为: Both open a URL connection and read lines using BufferedReader；Both iterate over lines in a while loop until null；Both perform string parsing/checking on each line；Both have exception handling
- 行为差异: Function A creates and populates a map of JMenuItems, while Function B returns a string encoding；Function A sets action commands and adds action listeners, Function B does not；Function B also checks HTTP headers for encoding, Function A does not；Function A uses a Map parameter to store results, Function B does not have parameters
- 修正建议: Improve model's ability to differentiate boilerplate from core logic；Incorporate control flow and data flow analysis to capture the purpose of variables and method calls；Use contrastive learning on pairs with high structural similarity but different intent；Add features like method name and parameter types to guide semantic understanding

### case_id=3507 FN partial_functionality

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or local file) to a destination file using byte-by-byte stream I/O.
- B 摘要: Copies a source file to a destination file using NIO FileChannel transfer, with a same-path check.
- 静态失败原因: Static BERT models rely on token overlap and syntactic patterns; the low Jaccard similarity (0.196) and different API keywords (URL, FileChannel vs InputStream) caused the model to miss the functional equivalence.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels function pairs as clones if they share the same core functionality (copying data) despite differences in input types, APIs, and error handling, as they consider broader Type-3/Type-4 similarity.
- 共享行为: Both copy data from an input source to an output file；Both close input/output resources after copying
- 行为差异: copyResource supports URLs and local files; copyFile only accepts File objects；copyResource uses byte-by-byte streams; copyFile uses FileChannel.transferTo()；copyFile checks if source and destination are the same canonical path; copyResource does not；copyResource throws Exception; copyFile throws IOException and has a finally block for closing channels
- 修正建议: Use data-flow analysis to capture the copying behavior at a higher level；Incorporate knowledge of common I/O patterns (stream vs channel) as semantically equivalent；Augment training with examples of different I/O APIs performing the same task

### case_id=3508 FN partial_functionality

- 方法: `getFile` vs `upload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the wsdlsoap:address location to a given endpoint, and saves it to a temporary file, returning the file path.
- B 摘要: Copies an image file from a source path to a fixed destination path and returns the string "show".
- 静态失败原因: The model relies on lexical and syntactic similarity, which is low (Jaccard 0.0895), and lacks the ability to abstract high-level functional patterns like file copying across different APIs.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely classifies both as file I/O operations (Type-4 clone) due to high-level similarity in reading from a source and writing to a destination, despite different specific implementations.
- 共享行为: Both functions read from an input source and write to a file output stream.
- 行为差异: Code_a performs network I/O (URL) and XML parsing/modification, while code_b only copies a local file.；Code_a uses NIO channels and explicit stream management; code_b uses IOUtils.copy and closeQuietly.；Code_a handles multiple exception types with logging; code_b prints stack traces.；Code_a returns a file path; code_b returns a fixed string "show".
- 修正建议: Incorporate dataflow analysis to detect input-output transformations.；Use code summarization or functional embedding to capture high-level semantics.；Enhance training with more diverse Type-3/Type-4 clone examples.

### case_id=3509 FN benchmark_preference_bias

- 方法: `doGet` vs `copyTo`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests to retrieve and display a portal page, with logging and caching to file.
- B 摘要: Recursively copies a file or directory to a destination using NIO channels.
- 静态失败原因: The static model correctly identified them as not clones under strict semantic equivalence, but failed to match BCB's possibly overbroad annotation, likely due to low lexical overlap and different domain contexts.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to a very broad interpretation of Type-4 functional similarity (both involve writing data to files), but the core logic and purpose are entirely different.
- 共享行为: Both involve file I/O operations；Both use try-catch for error handling
- 行为差异: A is a servlet method handling HTTP requests; B is a static utility for file copying；A has complex logic for page retrieval, user permissions, logging, and caching; B has simple recursive directory copy；A uses HttpServletRequest/Response; B uses File and FileChannel；A writes HTML to a file cache; B copies any file type
- 修正建议: Re-evaluate BCB labels for such pairs to ensure consistency；Include functional similarity beyond file I/O, such as task-level classification

### case_id=3510 FN benchmark_preference_bias

- 方法: `doGet` vs `saveFileData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to retrieve and display a web page with access control and caching.
- B 摘要: Saves file data by copying and updating file content, updating image dimensions, and cleaning up thumbnail caches.
- 静态失败原因: The static model likely correctly identified the low lexical overlap (Jaccard 0.097) and semantic mismatch, predicting non-clone. The BCB label is likely incorrect, so the model 'failed' in the sense of disagreeing with a potentially erroneous ground truth.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label may be an annotation error, as there is no recognizable functional similarity even under broad Type-3/Type-4 criteria. Possibly the annotator considered both methods involve file operations and exception handling as sufficient similarity, but this is very weak.
- 共享行为: Both methods perform file I/O operations (writing files) as part of their logic.；Both methods involve logging or error handling.
- 行为差异: Function A is a servlet doGet method for HTTP request handling; Function B is a static file utility method.；A deals with web page retrieval, user permissions, and HTML output; B deals with file channels, image metadata, and cache management.；Inputs and outputs are completely different: A takes HttpServletRequest/Response, B takes File objects.；Their core purposes are unrelated.
- 修正建议: Review and correct the BCB annotation for this pair if it is indeed a false clone.；If the BCB label is kept, the model would need to capture very broad functional similarity, which may not be desirable.

### case_id=3511 FN partial_functionality

- 方法: `doTransfer` vs `callService`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Proxies an HTTP request by forwarding headers, method, and body from an incoming request to a target URL, then returning the response.
- B 摘要: Makes a simple HTTP GET request to a URL and stores the response as a string.
- 静态失败原因: The functions have very low token overlap and different structural patterns (one is a servlet method with request/response objects, the other a private helper using URL). The model likely couldn't capture the shared high-level concept.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'HTTP request execution' functions, thus labeling them as Type-4 semantic clones despite differences in complexity and usage.
- 共享行为: Both open an HTTP connection to a URL and read the response.
- 行为差异: A forwards the entire request (headers, body, method) and echoes the response to the output stream; B only reads a GET response and stores it in a field.；A uses HttpURLConnection with explicit method; B uses URL.openStream().
- 修正建议: Increase model's ability to recognize semantic equivalence across different APIs (e.g., URL.openStream vs HttpURLConnection) or use dataflow analysis.

### case_id=3512 FN partial_functionality

- 方法: `File2String` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file from a directory or system resource and returns its content as a string.
- B 摘要: Opens a URL to read version information and triggers a version check process.
- 静态失败原因: Static BERT models rely on token overlap and embedding similarity; the low Jaccard (0.23) and different method names, API usage (File vs URL), and distinct string processing cause low representation similarity, missing the structural commonality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often annotates Type-3 and Type-4 clones where the structure (open stream, read lines, close) is similar even if the purpose differs. This pair shares the core reading pattern, so BCB labels them as clones despite different output processing.
- 共享行为: Both open an input stream (FileInputStream/URL.openStream).；Both read lines using BufferedReader in a while loop.；Both close the stream after reading.
- 行为差异: A reads from a local file or classloader resource; B reads from a URL.；A returns the entire file content; B extracts specific build numbers and calls another method.；A terminates on error with System.exit; B shows an error dialog and continues.；A has fallback mechanism (directory + filename if local fails); B does not.
- 修正建议: Incorporate structural or control flow graphs to capture shared patterns like stream-read-loop.；Use dataflow analysis to recognize that both functions read from an input source line by line.；Consider subgraph matching for common patterns in AST or CFG.

### case_id=3513 FN benchmark_preference_bias

- 方法: `doTransfer` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request to a target URL, copying headers and body, and returning the response.
- B 摘要: Checks for a new software version by reading a version file from a URL and displaying a message.
- 静态失败原因: Static BERT correctly predicted non-clone based on low lexical overlap and different method names, but BCB's label may reflect a broader, pattern-based similarity that BERT did not capture.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to common boilerplate pattern of making HTTP requests, reading input streams, and exception handling, despite different domain logic.
- 共享行为: Both open a URL connection and read an input stream；Both handle IOException with exception handling
- 行为差异: Different purpose: proxy forwarding vs version checking；Different output: forwards response vs shows message to user
- 修正建议: Use semantic analysis focusing on actual purpose rather than superficial patterns；Require higher behavioral similarity threshold for clone classification

### case_id=3514 FN lexical_or_api_overlap

- 方法: `sendExceptionToServer` vs `readIntoList`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST and prints server response.
- B 摘要: Reads HTML from a URL, parses anchor tags, and populates a JMenu with items.
- 静态失败原因: Static BERT/GraphCodeBERT may have over-relied on lexical and API overlap (URL, BufferedReader, try-catch) and missed the distinct semantic operations.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might consider them clones due to shared boilerplate of URL reading and exception handling, but the core functionality is different.
- 共享行为: Open URL connection；Read lines with BufferedReader；Use try-catch for exception handling；Close the reader
- 行为差异: A sends data (POST) while B only reads (GET)；A constructs URL-encoded parameters; B parses HTML；A creates exception trace; B creates JMenuItems with listeners；A prints responses; B inserts items into a map
- 修正建议: Incorporate data-flow analysis to distinguish building payload vs. parsing HTML；Use AST-based comparison to capture structural differences in loop body；Add training examples that disambiguate similar API usage but different intent

### case_id=3515 FN boilerplate_overlap

- 方法: `addIDs` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses metabolite information from a remote database by fetching HTML pages and extracting IDs based on specific patterns.
- B 摘要: Fetches a web page and prints its content line by line to the console.
- 静态失败原因: Static models like GraphCodeBERT rely on token similarity and structure. The low token Jaccard (0.14) indicates little lexical overlap. The model correctly identified them as non-clones based on low surface similarity. But if the model incorrectly predicted non-clone, that is correct behavior; but here BCB label is 1, so the model 'failed' to match the BCB label. Actually, the model predicted 0, which matches strict analysis, but BCB says 1. So the model failed to recognize the BCB-style annotation preference for broad similarity. The model might have been too strict and missed the shared boilerplate pattern that BCB considered clone-worthy.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might label this as a clone due to the shared structural pattern of URL connection and line reading, which is a common boilerplate for web scraping. However, the core functionality differs significantly, so it is more likely a Type-3 clone based on shared API usage rather than semantic equivalence.
- 共享行为: Both open an HTTP connection to a URL；Both read lines from the input stream using BufferedReader；Both use URL and InputStreamReader
- 行为差异: addIDs parses HTML to extract metabolite IDs and sets them in a PeakListRow object, while main simply prints each line；addIDs has conditional logic to handle different HTML patterns, whereas main has no such logic；addIDs returns an integer score, main has no return value；addIDs handles exceptions with logging, main throws IOException
- 修正建议: Incorporate broader patterns of API usage, such as treating URL processing as a reusable component.；Use dataflow analysis to capture the intent of data ingestion vs. data processing.；Better handling of BCB's annotation guidelines which may include Type-4 clones based on similar I/O operations.

### case_id=3516 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles user selection of various application settings (graphviz, imagemagick, look and feel, etc.) and updates UI and preferences.
- B 摘要: Reads a log file, filters lines at intervals matching a token, and writes to an output file.
- 静态失败原因: Overlap in lexical tokens like 'File', 'IOException', 'catch', and generic API usage (JFileChooser/FileReader) caused the model to falsely detect similarity, ignoring the fundamental semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because functions are entirely unrelated in functionality and structure; they perform distinct tasks with no shared intent beyond basic Java I/O.
- 共享行为: Both involve file operations (JFileChooser vs FileReader) and string handling.
- 行为差异: GUI event-driven vs command-line main method；Complex settings dialog vs simple file filtering；Different purposes: preference management vs log trimming；Different control flow: long switch-like structure vs loop with condition
- 修正建议: Enhance model with control flow and data dependency awareness；Use graph-based code representations to distinguish context；Train on more diverse non-clone pairs with low Jaccard but high static similarity

### case_id=3517 FN partial_functionality

- 方法: `copyResource` vs `_checkLanguagesFiles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file byte-by-byte.
- B 摘要: For each language, ensures existence of two files and copies the first to the second if either was missing.
- 静态失败原因: Low lexical overlap (Jaccard 0.13) and different method names, variable names, and control structures misled static models; they fail to capture the shared file copy semantic due to partial functionality and long-range differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone because both functions implement a core file copy operation, which is a common functionality pattern considered similar under broad Type-4 annotation.
- 共享行为: File copying from a source to a destination using Java I/O
- 行为差异: Source types: URL/file vs. only file；Copy method: byte-by-byte read/write vs. FileChannel.transferFrom；Loop: single copy vs. loop over list of languages；Conditional copy: unconditional vs. only if files were created
- 修正建议: Use graph-based models that capture data flow and I/O operations.；Incorporate contrastive learning with functional equivalence examples.；Fine-tune on BigCloneBench with diverse Type-4 clones.；Utilize code summarization or API call sequence features.

### case_id=3518 FN benchmark_preference_bias

- 方法: `createDialogArea` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Creates a SWT dialog area that reads a license file from a bundle resource and displays it in a browser or text widget.
- B 摘要: Invokes a remote method via HTTP POST, reads the response, and deserializes it, with retry logic on connect timeout.
- 静态失败原因: Static BERT likely did not fail—it correctly predicted non-clone because the overall functionality and API usage are dissimilar; it captured the semantic difference.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider both as 'reading from a stream and processing lines', a common I/O pattern, thus labeling as Type-4 clone despite different contexts.
- 共享行为: Both use BufferedReader to read lines from an InputStream and append to StringBuilder.
- 行为差异: UI-related vs network RPC；Resource file input vs HTTP response input；Retry logic present only in B；Deserialization and exception handling differ
- 修正建议: Use more fine-grained clone annotation guidelines to avoid over-generalizing common patterns；Include domain/context information in clone detection models to distinguish different functional intents

### case_id=3519 FP lexical_or_api_overlap

- 方法: `checkForUpgrade` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for software upgrades by querying a server and database, updating UI components.
- B 摘要: Extracts a full screen video URL from a YouTube page by parsing HTML.
- 静态失败原因: Static BERT models may overemphasize lexical and API-level overlap (URLConnection, BufferedReader, string splitting) while missing the high-level semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the functions have entirely different purposes (upgrade management vs. video URL extraction) despite low-level I/O similarities.
- 共享行为: Both open a URL connection and read lines from the stream；Both use BufferedReader and split strings to extract data
- 行为差异: Function a performs database operations and UI updates; function b only returns a constructed URL；Function a handles license validation and upgrade records; function b extracts video parameters；Overall business logic is completely different
- 修正建议: Incorporate control-flow and data-flow features；Use models that capture program intent beyond lexical tokens；Add training examples with similar APIs but different overall functionality

### case_id=3520 FN partial_functionality

- 方法: `copyResource` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using InputStream and OutputStream, byte by byte.
- B 摘要: Copies a source file to a destination file using FileChannel and MappedByteBuffer.
- 静态失败原因: Low token Jaccard (0.228) and different API usage (streams vs NIO) lead models to focus on surface form, missing functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels as clone because both perform the same high-level file copy task, with minor API and error handling differences considered acceptable for Type-3/Type-4 clones.
- 共享行为: Both copy file content from source to destination；Both use Java I/O and close resources
- 行为差异: a can read from URL, b only from file；a uses byte-by-byte copying, b uses memory-mapped buffer；a uses instance methods for source/destination, b uses explicit string arguments；a throws Exception, b throws IOException
- 修正建议: Use data-flow analysis to detect file copy operations across different APIs；Incorporate type information to recognize functional equivalence of FileChannel and FileOutputStream；Leverage program dependency graphs to abstract away syntactic differences

### case_id=3521 FN benchmark_preference_bias

- 方法: `addDataFromURL` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads text from a URL line by line and appends it to a StringBuffer, handling exceptions by appending the URL string.
- B 摘要: Parses multiple comma-separated field strings into HashSets, then reads a file with a specific format to populate various data structures (maps, sets) for a Tibetan transliteration system.
- 静态失败原因: Static models like GraphCodeBERT typically rely on semantic similarity from the code structure and variable usage. The low token overlap and stark behavioral differences caused the model to correctly predict non-clone, but BCB's annotation preference for broad functional categories overrides this, making the prediction appear as a false negative.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'data reading' functions, categorizing them under a broad functional label, which can lead to Type-4 false positives even when actual behavior differs significantly.
- 共享行为: Both involve reading and processing text input；Both use BufferedReader for reading；Both have exception handling
- 行为差异: A reads from a URL, B reads from string fields and a local file；A simply appends lines to a buffer, B performs complex tokenization and data structure population；A has minimal error handling, B has detailed validation and custom error messages；A has no output parameters, B modifies multiple class-level collections
- 修正建议: Re-annotate this pair in BigCloneBench to reflect true functional dissimilarity；Train models with more granular functional taxonomies to reduce sensitivity to overly broad categories；Incorporate context (e.g., method surrounding class) to disambiguate generic 'read' operations

### case_id=3522 FP long_range_semantics

- 方法: `Song` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Constructor that parses a semicolon-separated string to initialize Song fields and compute SHA-1 hash of title and artist.
- B 摘要: Struts action method that validates session, processes concept classification request, sends XML via HTTP, and returns an ActionForward.
- 静态失败原因: Low token overlap (Jaccard=0.0546) suggests model may have been misled by superficial similarities like try-catch blocks or string tokenization, but more likely a benchmark anomaly; models may fail on long-range semantic differences when both methods have complex control flow.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels non-clone because functions have no semantic similarity and belong to unrelated applications.
- 共享行为: Both involve parsing strings into tokens；Both handle exceptions with try-catch
- 行为差异: Different purpose: constructor vs. Struts action；Different input/output: string parameter vs. HTTP request/response；Different domains: media metadata vs. enterprise classification；No functional overlap in business logic
- 修正建议: Train on more diverse non-clone pairs；Incorporate structural similarity metrics；Use data flow analysis to distinguish functionality

### case_id=3523 FP other

- 方法: `main` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.99`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads multiple input files and writes concatenated lines to an output file.
- B 摘要: Handles various UI actions in a settings dialog, including file chooser for external tools and preferences.
- 静态失败原因: The model likely overestimated superficial similarities such as both having loops or both using PrintWriter/File/Scanner and JFileChooser/File objects, but missed the completely different overall purpose. Low token Jaccard argues against lexical overlap, so the model may have relied on structural patterns or API usage that coincided.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labeled non-clone because there is zero functional overlap; one is a standalone file processing utility, the other is a UI event handler with settings management.
- 行为差异: Function A is a simple file concatenation; Function B is a complex event handler with multiple UI actions.；Function A has no user interface; Function B heavily interacts with GUI components.；Function A writes to a file; Function B reads/writes preferences and updates UI state.；Function A has no branching on command strings; Function B branches extensively on action commands.
- 修正建议: Incorporate dataflow analysis to capture high-level purpose (e.g., file I/O vs. UI event handling).；Train with contrastive examples of dissimilar functions sharing only superficial API calls.；Use program slicing to focus on core functionality rather than boilerplate code.

### case_id=3524 FN partial_functionality

- 方法: `main` vs `transport`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to files.
- B 摘要: Recursively copies files from a directory to a destination directory using file channels.
- 静态失败原因: Low token overlap (0.1279) and different syntactic structures; the model correctly recognized them as distinct tasks.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: The BCB annotator likely considered both as generic data transfer operations from input to output via file I/O, leading to a broad Type-4 clone label.
- 共享行为: Both read from an input source and write to output files using Java I/O.
- 行为差异: Different source types (URL vs directory)；Different input format (zip entries vs plain files)；Different output naming (entry names vs fixed destination)；Different I/O classes (ZipInputStream/BufferedOutputStream vs FileChannel.transferTo)
- 修正建议: Filter broad functional similarities that are not semantically equivalent.；Use task-specific features to improve clone detection precision.

### case_id=3525 FP lexical_or_api_overlap

- 方法: `callApiPost` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response InputStream.
- B 摘要: Checks for software upgrades by querying a remote server and updating UI and database accordingly.
- 静态失败原因: Static model likely overfitted on shared API calls (URLConnection, InputStream, etc.) and ignored method names and overall functional context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have entirely different purposes and logic, despite sharing low-level HTTP connection code.
- 共享行为: Both use URLConnection to make HTTP requests；Both handle input streams from the connection
- 行为差异: Function A uses POST; B uses GET；A sends parameters in request body; B appends parameters to URL query string；A returns an InputStream; B returns void and updates UI and database；A throws exceptions; B handles errors with messages
- 修正建议: Incorporate method name or broader context embeddings；Use data flow or control flow analysis to distinguish patterns；Add more negative examples with API overlap but different semantics

### case_id=3526 FP lexical_or_api_overlap

- 方法: `readData` vs `uncaughtException`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parsing comma-separated token lists from strings and a file to populate sets and maps for a Tibetan transliteration system.
- B 摘要: Handling an uncaught exception in an SWT application by showing an error dialog and optionally opening a bug tracker URL.
- 静态失败原因: The model likely overgeneralized from superficial lexical patterns (e.g., both contain 'throw new Error', 'catch', or 'Exception' keywords) or was misled by lengthy boilerplate parsing code in A that has no counterpart in B.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would clearly label these as not clones because they perform entirely different tasks with no shared functionality.
- 行为差异: Function A reads configuration data into collections; Function B handles runtime exceptions in a GUI.；Function A manipulates strings and parses files; Function B creates SWT widgets and launches external programs.；Function A is a private utility method; Function B is a public exception handler.；They share no meaningful functional overlap.
- 修正建议: Improve training data to include more negative examples with high surface similarity but different semantics.；Use structural or data-flow analysis to distinguish setup/initialization code from exception handling.；Incorporate token-level attention mechanisms that can ignore repeated boilerplate patterns.

### case_id=3527 FN partial_functionality

- 方法: `doTransfer` vs `readIntoList`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: HTTP proxy function that forwards a request to another URL and streams the response back.
- B 摘要: Parses an HTML page from a URL and builds a JMenu with action listeners.
- 静态失败原因: The static model likely focused on low token overlap (0.15), different method names, and the distinct high-level tasks (proxy vs menu builder), missing the common I/O pattern and exception handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may accept broad Type-4 clones where partial functionality (reading from URL and handling exceptions) is considered similar, even though the overall tasks differ.
- 共享行为: Both open a URL connection and read input from it；Both use try-catch blocks and print stack traces on exception
- 行为差异: A forwards HTTP requests and responses; B parses HTML to create UI menu items；A uses HttpURLConnection and streams; B uses BufferedReader and line parsing；A writes to servlet output; B populates a Map with JMenuItems
- 修正建议: Use semantic similarity that captures I/O patterns and exception handling；Improve attention to common substructures like opening URL and reading data

### case_id=3528 FN benchmark_preference_bias

- 方法: `doGet` vs `copyParseFileToCodeFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.1`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests for a page, including permission checks, logging, caching, and error handling.
- B 摘要: Copies a file from one path to another using a buffer.
- 静态失败原因: The static BERT model likely relies on token and structural similarity, which are very low (Jaccard=0.0537). The model correctly identified them as non-clones, but BCB's label might be erroneous, causing a false negative in the evaluation. Alternatively, if BCB's criteria are accepted, the model failed to capture the abstract I/O pattern.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider this a type-4 clone based on the very abstract similarity that both methods read data and write it somewhere, but this is extremely weak and unlikely to be labeled as clone in BCB. The given label may be a data error.
- 共享行为: Both perform I/O operations involving reading from an input stream and writing to an output stream.
- 行为差异: Function A is a complex web request handler with multiple try-catch blocks, conditional logic, and dependencies on portal objects; Function B is a simple file copy with no error handling.；Function A involves HTTP request/response, page navigation, permissions, and statistics; Function B is purely file I/O.；Function A has extensive logging and caching; Function B has no logging.；The scale and purpose are entirely different: one is an HTTP servlet, the other is a utility method.
- 修正建议: Verify ground truth labels in BCB dataset; possibly discard noisy pairs.；Improve semantic understanding in models to avoid over-relying on token overlap, but in this case the non-clone decision is likely correct.

### case_id=3529 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a newer version of jEdit by fetching a version file from a URL and comparing build numbers.
- B 摘要: Searches Google Images for album art of the current track and extracts image URLs.
- 静态失败原因: Static BERT likely focused on the overlapping API calls (URL, BufferedReader, while loop) and missed the different semantic contexts and data flows.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have different overall goals and domain-specific logic, even if they share generic I/O patterns.
- 共享行为: Both open a URL and read lines from the response；Both use BufferedReader and InputStreamReader
- 行为差异: Different purposes: version checking vs. image search；Different URL construction and parameter handling；Different parsing logic: key-value lines vs. HTML href extraction；Different UI interactions: one updates a view, the other populates a list
- 修正建议: Incorporate more fine-grained control flow and data dependency analysis；Use a model that captures program semantics beyond token sequences

### case_id=3530 FN benchmark_preference_bias

- 方法: `doGet` vs `unJarStart`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve and display a web page with access control, request logging, and caching to file.
- B 摘要: Extracts and copies files from a JAR archive that match a given entry prefix to a destination path.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on low token overlap (0.066) and different API usage (servlet vs. JAR), correctly predicting non-clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as methods that perform file operations with error handling and logging, possibly under a broad category of 'utility/file manipulation', but this is not clearly justified.
- 共享行为: Both involve file I/O operations (writing files) and error handling (try-catch).
- 行为差异: A is a servlet method handling HTTP request/response; B is a private utility for JAR extraction.；A performs access control and page rendering; B does not.；A uses HttpServletRequest/Response; B uses JarFile and ZipEntry.；A writes to temporary files for caching; B copies files from JAR to specified directory.
- 修正建议: Improve BCB annotation guidelines to avoid overly broad clones.；Use more strict semantic equivalence criteria.

### case_id=3531 FP lexical_or_api_overlap

- 方法: `getRequestContent` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens an HTTP connection to a given URL, reads and returns the first line of the response.
- B 摘要: Opens an HTTP connection to a Google image search URL, reads the entire response, parses image URLs from the HTML, and adds them to a list.
- 静态失败原因: The static model likely overemphasized lexical and API-level overlap (URL, HttpURLConnection, BufferedReader) while ignoring the distinct control flow, data flow, and functional purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because the only commonality is trivial HTTP boilerplate; the core functionality (returning a single line vs. parsing HTML for image URLs) is entirely different.
- 共享行为: Both open an HTTP URL connection and read from its input stream.
- 行为差异: Function A reads only the first line; function B reads all lines.；Function A returns a single line; function B extracts image URLs and populates a list, with no return value.；Function B adds a User-Agent header and handles spaces in the URL; function A does not.；Function A throws Exception; function B catches Exception and displays an error dialog.
- 修正建议: Incorporate dataflow analysis or a model that captures the full program semantics beyond API sequences.；Use token-level or structural features that differentiate partial reads vs. full reads and return vs. side-effect behavior.

### case_id=3532 FP lexical_or_api_overlap

- 方法: `downloadURLtoString` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A utility that downloads content from a URL and returns it as a string.
- B 摘要: A constructor for a GUI browser that reads XML from a URL, optionally applies XSLT transformation, and displays HTML.
- 静态失败原因: The static BERT/GraphCodeBERT model likely over-relied on the common API sequence (openStream, readLine, append) and ignored the surrounding code that defines vastly different purposes, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label them as clones because the overall functionality is completely different; the shared URL-reading code is incidental and does not represent the primary purpose of either function.
- 共享行为: Both read content from a URL using BufferedReader and InputStreamReader.；Both append lines to a StringBuffer.
- 行为差异: A simply returns the string content, while B sets up a GUI with panels and buttons.；B parses XML, handles stylesheets, applies XSLT transformation, and displays HTML in a JEditorPane.；B handles multiple exceptions and manages window layout.
- 修正建议: Incorporate structural or dataflow information to distinguish different intents.；Use contrastive learning to emphasize functional differences despite lexical overlap.；Increase context window or use graph-based representations to capture overall control flow.

### case_id=3533 FN partial_functionality

- 方法: `main` vs `CopyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from HTTP, extracts its ZIP entries, and writes each entry to a file.
- B 摘要: Copies a file from source path to destination path using FileChannel.
- 静态失败原因: Low token Jaccard (0.17) and different method names/signatures lead to low embedding similarity; model fails to capture the abstract functional overlap of file I/O operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as generic file copying/transfer tasks, ignoring the specific protocols and data processing details, thus labeling them as Type-4 clones (similar functionality).
- 共享行为: Both perform file I/O operations involving reading from an input source and writing to output files
- 行为差异: Source is HTTP URL with ZIP extraction vs local file without extraction；a writes multiple files from ZIP entries, b writes single file；a uses ZipInputStream and buffered streams, b uses FileChannel and transferTo
- 修正建议: Enhance training data with more diverse file I/O examples；Incorporate structural similarity beyond exact tokens, e.g., graph-based representations of data flow

### case_id=3534 FN partial_functionality

- 方法: `main` vs `executeHttpGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Main method that sends a POST request to RenRen API with multiple parameters and prints the response line by line.
- B 摘要: Private method that sends a GET request to a given URI and returns the response as a JSONObject.
- 静态失败原因: Low token Jaccard (0.09) due to different vocabulary (e.g., HttpURLConnection vs HttpClient, PostParameter vs HttpGet) and structural differences, causing the static model to miss the shared control flow pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone due to shared 'HTTP request + read response line by line' pattern, which is considered partial functional similarity (Type-4) under their broad annotation guidelines.
- 共享行为: Both perform an HTTP request and read the response line by line using a BufferedReader.
- 行为差异: Method type: static main vs private instance method；HTTP method: POST vs GET；Parameter handling: manual construction of PostParameter objects vs URI parameter；Output: prints to stdout vs returns JSONObject
- 修正建议: Use dataflow or graph-based representations to capture control flow similarity.；Incorporate contrastive learning on functionally equivalent code snippets.；Add I/O behavior features to distinguish partial similarity.

### case_id=3535 FN partial_functionality

- 方法: `copyResource` vs `fetchURLData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file.
- B 摘要: Fetches data from a URL (with optional proxy) and returns it as a byte array.
- 静态失败原因: Static BERT models rely heavily on lexical overlap and local syntactic patterns; the low token Jaccard (0.1165) and different API usages obscure the shared abstract behavior of reading from a URL and writing to an output stream.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones because both functions implement the common pattern of retrieving data from a URL-like source and outputting it, despite differences in output destination and extra HTTP configuration.
- 共享行为: Both functions read data from a URL or file source.；Both write the data to an output stream (file or byte array).；Both close input streams after use.
- 行为差异: copyResource writes to a file; fetchURLData returns a byte array.；fetchURLData supports HTTP proxies and user-agent headers; copyResource does not.；copyResource uses byte-by-byte copying; fetchURLData uses buffered IOUtils.copy.；copyResource throws Exception on missing resource; fetchURLData throws IOException.
- 修正建议: Incorporate dataflow analysis to track that both functions read from a source and write to a sink.；Use graph-based representations that capture IO operations and their connections.；Train on examples with low lexical overlap but high semantic similarity in data copying patterns.

### case_id=3536 FN partial_functionality

- 方法: `fileDownload` vs `handledRun`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a given URL to a local file named 'download.pdf'.
- B 摘要: Downloads a specific XML file from a fixed URL, checks version, and writes headers plus content to a local file if newer.
- 静态失败原因: Static BERT models rely on token embeddings and may be misled by low lexical overlap and different method names/control structures. The additional conditional logic and file handling in function b obscure the shared download pattern, causing the model to predict non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers Type-4 semantic clones where core functionality (downloading a file from URL to local storage) is shared, despite additional surrounding logic. The annotators likely focused on the common download behavior as the primary purpose.
- 共享行为: Both open a URL connection and read data from an input stream；Both write read data to a local file using FileOutputStream；Both use a while loop reading bytes until -1 to copy content
- 行为差异: Function a is generic (parameterized URL and destination directory); function b uses fixed URL and specific file path from GameDatabase；Function b includes version comparison logic and writes header lines before data；Function b has additional error handling for UnknownHost and shows dialog on exception；Function b calls GameDatabase methods to load and detect games
- 修正建议: Enhance model with data-flow analysis to identify core I/O operations (URL.openStream, FileOutputStream, read/write loops)；Use contrastive learning with positive pairs defined by behavioral similarity (e.g., file download) rather than exact token matches；Incorporate code summarization or functional role detection to abstract over implementation details

### case_id=3537 FN benchmark_preference_bias

- 方法: `createJAR` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Creates a JAR file or directory and writes a serialized document object to it.
- B 摘要: Configures and launches a NexOpen project in Eclipse, handling Maven POM files and Hibernate reverse engineering.
- 静态失败原因: Static models like GraphCodeBERT rely on token overlap and AST structure; the low token Jaccard correctly led to a non-clone prediction, but BCB's label appears incorrect, making the model's prediction a false negative in the benchmark.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to both involving file operations and exception handling, but overall functionality is completely different; BCB sometimes accepts broad Type-3/4 based on structural similarity.
- 共享行为: Both use file-related operations such as creating, writing, or copying files.
- 行为差异: A focuses on JAR/directory creation and serialization; B focuses on Eclipse project configuration and Maven build.；A uses low-level file I/O (FileChannel, ObjectOutputStream); B uses high-level Eclipse APIs (IFile, IProject).；A is standalone; B is part of Eclipse launch framework.
- 修正建议: Improve BCB annotation consistency to avoid labeling unrelated functions as clones.；Incorporate domain-specific features to differentiate Eclipse plugin code from generic file I/O.

### case_id=3538 FP boilerplate_overlap

- 方法: `updateFile` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file to a new location by removing a URL prefix using NIO FileChannel.
- B 摘要: Main method that parses command line, reads a Prolog file, parses it, and generates adapter classes and resources into a JAR.
- 静态失败原因: Likely over-relied on common boilerplate patterns like try-finally, IOException, and file-related keywords (File, FileInputStream, etc.) despite low Jaccard similarity, causing a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this non-clone because the functions have completely different purposes and only trivial syntactic overlap (both mention File). Type-3/Type-4 clones require some functional similarity, which is absent.
- 共享行为: Both involve file I/O operations using File objects
- 行为差异: updateFile only copies a single file; main performs complex multi-step adapter generation.；updateFile uses FileChannel; main uses various high-level file and bytecode manipulation libraries.；updateFile has no command-line parsing; main handles arguments and debug mode.；updateFile is a private helper; main is a public static entry point.
- 修正建议: Train model to distinguish semantically distinct uses of common file I/O patterns.；Incorporate control-flow and data-dependency analysis.；Use contrastive learning with harder negative examples involving similar lexical content but different semantics.

### case_id=3539 FN lexical_or_api_overlap

- 方法: `read` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a camera log from a URL line by line, parses each line into CameraLogRecord objects, collects and sorts them.
- B 摘要: Reads a file or classpath resource line by line and concatenates all lines into a single string.
- 静态失败原因: Static BERT (e.g., CodeBERT) relies on token embeddings and may be misled by low token Jaccard similarity (0.195) and different API usage (URL vs File), method names, and return types. It may not capture the structural/behavioral similarity of the read loop.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often accepts broad Type-3/Type-4 clones based on shared high-level behavior: reading lines from a stream using BufferedReader. Despite differences in input source and post-processing, the core loop structure is very similar, which BCB may consider sufficient for a clone label.
- 共享行为: Both read from an input source line by line using BufferedReader and readLine() loop；Both close the reader in a finally block；Both handle IOException
- 行为差异: Input source: A uses URL, B uses file or classpath resource；Output: A produces a sorted list of parsed records, B produces a concatenated string；Error handling: A uses logging, B uses System.out.println and System.exit；A parses each line into a structured object, B just appends lines
- 修正建议: Use AST-based or structural features to capture loop and I/O patterns；Train with contrastive learning that emphasizes common control flow patterns；Ignore method names and return types during clone detection for broad types；Consider data flow analysis to identify similar I/O sequences

### case_id=3540 FP long_range_semantics

- 方法: `main` vs `createButtonCopyToClipboard`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Command-line tool that reads a Prolog file, parses it, generates adapter classes, and writes them to a JAR.
- B 摘要: Creates a button in an SWT shell that, when clicked, copies the environment report to clipboard.
- 静态失败原因: Static BERT-like models may rely on superficial patterns like shared keywords (e.g., 'button' in B and 'adapter' in A are not shared), but here token overlap is very low. The false positive likely arises from the model's inability to capture the long-range semantic structure and dataflow, or possibly from training data bias where similar-looking boilerplate patterns were misassociated.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically marks these as non-clones because they share no common functionality or domain; the only similarity is that both are Java methods, but that is not enough for BCB's broad similarity.
- 共享行为: Both are Java methods；Both involve some I/O (file reading vs clipboard)；Both use external libraries (Prolog parser vs SWT)
- 行为差异: A is a top-level main method with complex file processing; B is a private GUI helper method；A generates code; B creates a UI element；A has error handling and user output; B has none；A operates on files and class loading; B operates on SWT widgets
- 修正建议: Use better structural matching；Incorporate dataflow and control flow analysis；Train with more diverse negative examples where methods share common Java idioms but differ in purpose

### case_id=3541 FP lexical_or_api_overlap

- 方法: `readRemoteFile` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a remote file line by line and returns the entire content as a single string.
- B 摘要: Downloads an RDF model from a URL, optionally setting HTTP headers, and returns the Model object.
- 静态失败原因: The model likely overemphasized lexical and API overlaps (URL, InputStream, IOException, try-catch blocks) and failed to capture the completely different return types and functional intents (string vs. model).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have different high-level purposes and output types, even if they share low-level steps like URL connection and stream reading.
- 共享行为: Both open a URL connection and read from an InputStream.；Both handle IOException exceptions.
- 行为差异: Function A returns a String, while Function B returns a Model object.；Function B sets HTTP request properties (Accept, Accept-Language) for HTTP connections; Function A does not.；Function A reads line by line into a string; Function B reads directly into an RDF model.；Function B wraps exceptions in RuntimeException; Function A prints error messages or handles EOF explicitly.
- 修正建议: Incorporate structural features like return type and method signature.；Use dataflow analysis to distinguish output construction patterns.；Add attention to method names and javadoc if available.

### case_id=3542 FN partial_functionality

- 方法: `copyFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Retrieves a resource as an InputStream, caching it to a local file if not already cached.
- 静态失败原因: Static BERT models rely on token overlap and surface patterns, which are low here; they miss the abstract semantic equivalence of 'file copy'.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones as Type-4 due to shared high-level intent of copying data from a source to a destination, even though implementations differ.
- 共享行为: Both perform file copy operations from a source to a destination
- 行为差异: Different sources (local file vs URL)；Different I/O mechanisms (FileChannel vs streams with caching)；Different error handling (logging vs printStackTrace)；Additional caching logic in function b
- 修正建议: Incorporate dataflow analysis to recognize input-output transformations；Use graph-based models to capture structural similarities over long ranges

### case_id=3543 FN partial_functionality

- 方法: `read` vs `fileDownload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads and parses a remote camera log file into records, then sorts them.
- B 摘要: Downloads a file from a URL and writes it to a local directory.
- 静态失败原因: Static BERT models like GraphCodeBERT often rely on token-level patterns and may overemphasize surface-level differences (e.g., method names 'read' vs 'fileDownload', different variable names). The models may fail to capture the shared I/O skeleton due to attention dispersion over divergent code sections (parsing vs writing). Also, the length and specialized API calls (e.g., CameraLogRecord, LogParseException) create high lexical divergence.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as broad Type-3/4 clones because they share the core pattern of opening a URL, reading input, and closing streams, with only the processing step differing. The structural similarity in the I/O pipeline and resource management is enough for a clone label under BigCloneBench's inclusive criteria.
- 共享行为: Both open a URL and read data through a BufferedReader；Both close the input stream in a finally block or similar；Both perform I/O operations on remote resources
- 行为差异: Function A parses lines into structured objects and handles parsing exceptions; Function B writes raw bytes to a file without parsing；Function A sorts the resulting list; Function B does no sorting；Function B writes to a file using FileOutputStream; Function A accumulates in memory；Function A uses logging extensively; Function B uses exception logging only
- 修正建议: Incorporate dataflow analysis to detect shared I/O patterns beyond token overlap；Use program slicing to isolate the common subgraph (URL open → read → close) and ignore divergent post-processing；Train on more diverse clone types emphasizing partial functionality similarity

### case_id=3544 FP lexical_or_api_overlap

- 方法: `importSequences` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Imports biological sequence data from a URL by parsing lines into names and sequences.
- B 摘要: Reads all lines from a web page URL into a buffer without storing or processing them.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-relied on lexical and API overlap (URL, InputStreamReader, IOException, readLine) and missed the critical difference in data flow and processing logic. The model predicted clone due to similar boilerplate code.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled these as non-clones because the core functionality is completely different: one imports biological sequence data, the other fetches a web page with no data extraction. The shared URL reading pattern is superficial.
- 共享行为: Both open a URL and read input using an InputStreamReader.；Both catch MalformedURLException and IOException.；Both use a loop to read lines of text input.
- 行为差异: Function A parses and stores structured data (names and sequences); Function B discards the data.；Function A uses ImportHelper with tokenization and sequence reading; Function B uses plain BufferedReader with no data processing.；Function A has a do-while loop and checks for '>' delimiter; Function B has a simple while loop reading until null.；Function A handles additional exceptions like EOFException; Function B does not.
- 修正建议: Incorporate control-flow and data-dependency awareness to distinguish data usage.；Enhance training on examples where API usage is similar but semantics differ.；Use graph-based representations that capture variable transformations and output differences.

### case_id=3545 FP lexical_or_api_overlap

- 方法: `getRequestContent` vs `parse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Opens a URL connection, reads the first line of the response, and returns it as a string.
- B 摘要: Parses a dataset from a URL or file, handling headers, types, and scientific notation, returning a DataSet object.
- 静态失败原因: The model might have been misled by shared lexical elements (URL, BufferedReader, InputStreamReader, openConnection/Stream) and the common pattern of reading from a URL, ignoring the vast difference in overall logic and output. The token Jaccard is low (0.05) but the model may have learned to associate such patterns as clones in other contexts.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have entirely different purposes (get first line vs. parse structured dataset) and complexity. Despite both involving URL reading, the functionality is too dissimilar for Type-3/4.
- 共享行为: Both read data from a URL (or file) using BufferedReader/InputStreamReader；Both handle potential I/O exceptions (though error handling differs)
- 行为差异: Function A reads only the first line; Function B reads and tokenizes the entire content；Function A returns a String; Function B returns a DataSet object；Function B includes complex parsing logic (StreamTokenizer, headers, types) not present in A；Function A uses HttpURLConnection; Function B uses DataInputStream.openStream()
- 修正建议: Add more negative examples where URL reading is used but for different purposes；Incorporate dataflow or structural analysis to capture overall function purpose；Use attention to distinguish between incidental API usage and core functionality

### case_id=3546 FP boilerplate_overlap

- 方法: `copyFile` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Reads and parses configuration data from a file to initialize multiple sets and maps for character encoding.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on superficial common keywords like 'IOException', 'throw', and 'catch' without understanding the overall structure and purpose, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the two functions have completely different purposes and no partial functionality overlap in terms of file copying vs. configuration parsing.
- 共享行为: Both handle I/O operations；Both may throw or catch IOException
- 行为差异: copyFile performs a simple file copy; readData parses a complex text file with multiple fields and initializes numerous data structures；copyFile has no branching or data parsing; readData has extensive conditional logic and tokenization；copyFile is generic; readData is domain-specific for Tibetan/Sanskrit character mapping
- 修正建议: Train with more diverse negative examples that share common exception handling patterns；Incorporate structural or data flow features to distinguish file I/O from parsing logic

### case_id=3547 FP lexical_or_api_overlap

- 方法: `getPagina` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a web page content as a string by reading lines from a URL.
- B 摘要: Downloads an RDF model from a URL with custom HTTP headers and parses it.
- 静态失败原因: Static BERT may have been misled by overlapping tokens like 'URL', 'IOException', 'openStream' and similar control flow structures (try-catch), causing it to overestimate similarity despite functional differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions perform entirely different tasks (web scraping vs RDF model loading) and have different output types and error handling strategies.
- 共享行为: Both open a URL and read data from an input stream.；Both handle MalformedURLException and IOException.；Both use a try-catch block for network operations.
- 行为差异: Function A returns a concatenated string of the page, while B returns an RDF Model object.；Function A uses Authenticator and reads line-by-line; B sets HTTP headers and reads the stream directly for model parsing.；Function A catches exceptions and returns error strings; B wraps exceptions and throws RuntimeException.；Function B uses HttpURLConnection and sets request properties; A does not.
- 修正建议: Incorporate type information (return type, library classes) to distinguish functions.；Use dataflow analysis to track how the input is processed (string concatenation vs model parsing).；Train on more diverse examples with fine-grained functional similarity.

### case_id=3548 FN benchmark_preference_bias

- 方法: `save` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Saves a list of byte array file contents to disk, creating directories and prepending a package declaration to each file.
- B 摘要: Launches an Eclipse project by processing launch configuration attributes, manipulating XML pom files, setting Hibernate properties, and running an install action.
- 静态失败原因: Static BERT correctly predicted non-clone; the 'failure' is only relative to the BCB label, which appears erroneous. The model captured the lack of semantic similarity due to low token overlap and different control flows.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB annotation likely stems from a mislabeling or an extremely broad interpretation of 'save' and 'launch' as similar high-level operations (saving files vs. launching a configuration). However, there is no functional overlap.
- 行为差异: Function A writes byte arrays to files and then copies them with added package lines; Function B reads and modifies XML files and sets runtime properties.；Function A is a simple file I/O utility; Function B is a complex Eclipse plug-in launch handler with configuration, project setup, and error handling.；They operate on completely different data structures and have no common domain logic.
- 修正建议: Re-annotate this pair as non-clone because the functions are semantically unrelated.；If the BCB label is trusted, consider that annotators might have used a very loose criterion like 'both involve file handling', but this is not standard clone detection practice.

### case_id=3549 FP boilerplate_overlap

- 方法: `init` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Initializes an XML report file for batch processing, handling backup, restart, and parsing of old reports.
- B 摘要: Handles GUI action events to set various user preferences like GraphViz, ImageMagick paths, and other settings.
- 静态失败原因: The model likely overfitted to boilerplate elements (e.g., file I/O, try-catch, logging) or long method length, ignoring semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled 0 because the functions are unrelated in domain, purpose, and logic, with no meaningful shared functionality.
- 共享行为: Both involve file handling (report file vs. configuration file).；Both use conditional logic and exception handling.
- 行为差异: Different purposes: report initialization vs. UI settings update.；Different contexts: batch processing (Gate) vs. GUI (Suku).；Different operations: XML stream writing and parsing vs. file chooser dialog and preference storage.；Different control flow: complex restart logic vs. multiple independent command handlers.
- 修正建议: Enhance model training with more diverse negative pairs that share boilerplate but differ in semantics.；Incorporate control-flow and data-flow abstractions to distinguish such cases.；Use hierarchical representations to capture method-level intent rather than token details.

### case_id=3550 FN partial_functionality

- 方法: `read` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads camera log from a URL, parses each line into CameraLogRecord objects, adds them to a list, and sorts them.
- B 摘要: Sends an HTTP POST request to a URL with parameters, reads the response line by line, concatenates into a string, and returns it, handling errors.
- 静态失败原因: Low token overlap and different method names, combined with distinct processing logic, cause the static model to miss the common pattern of network I/O with BufferedReader.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers these clones as Type-4 (semantic) because they share the high-level behavior of reading from a URL line-by-line using BufferedReader, even though the processing after reading differs.
- 共享行为: Both open a URL and use BufferedReader to read lines in a while loop；Both handle IOException and close resources
- 行为差异: A parses lines into domain objects and sorts; B concatenates lines into a string；A uses URL.openStream() directly; B uses HttpClient with POST method and checks HTTP status；A logs errors; B sets error codes and returns null on failure
- 修正建议: Enhance model to recognize common I/O patterns like while((line=reader.readLine())!=null) regardless of surrounding logic；Incorporate graph representations that capture data flow from URL to BufferedReader

### case_id=3551 FN benchmark_preference_bias

- 方法: `register` vs `parse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Registers a user by encoding password, setting date, adding default authority, creating forum user via URL, persisting, and sending confirmation email.
- B 摘要: Parses a data set from a file or URL, processing delimiter-separated values and constructing a DataSet object.
- 静态失败原因: Static BERT/GraphCodeBERT correctly identified low token overlap (Jaccard 0.1486) and dissimilar semantics, predicting non-clone. It did not fail; instead, the BCB annotation seems inconsistent with typical clone definitions.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to a high-level structural similarity: both functions perform input processing from external sources, handle errors, and produce an output. Possibly considered Type-4 where both are 'data processing' functions, but the actual functionality is distinct.
- 共享行为: Both use URL connections to read data from external sources；Both use BufferedReader and InputStreamReader for I/O；Both have try-catch error handling with IOException；Both involve iterating over input lines in a loop
- 行为差异: Function A performs user registration with password encoding and database persistence; B parses structured data into a DataSet.；Function A writes to an external system (phpBB URL) and sends confirmation email; B only reads input and constructs an output object.；Function A validates object type and sets multiple user properties; B handles tokenization, delimiter parsing, and scientific notation.；Function A uses a logger; B uses System.out.println for output.
- 修正建议: Re-evaluate this pair's BCB annotation; consider removing or re-labeling as non-clone.；Improve training data quality by filtering out low-similarity pairs that are functionally different.；Focus on functional equivalence rather than structural patterns.

### case_id=3552 FP lexical_or_api_overlap

- 方法: `getUser` vs `getURLContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user by login from DAO or parses a config file to find matching user credentials and saves it.
- B 摘要: Fetches the entire content from a given URL as a string.
- 静态失败原因: The model likely focused on lexical overlap (BufferedReader, URL, while loop) and similar structure (try-catch, stream reading), missing the semantic difference in overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the overall functionality, purpose, and output types are completely different despite some shared API usage.
- 共享行为: Both use BufferedReader to read line by line.；Both handle I/O operations.；Both use URL-related classes (URL, URLConnection).
- 行为差异: A is about user authentication and DAO persistence; B is generic URL content retrieval.；A parses tokens and creates User objects; B appends lines to a StringBuilder.；A returns a User object; B returns a String.；A reads from a classpath resource file; B reads from a network URL.
- 修正建议: Incorporate control flow and data flow analysis to differentiate variable usage.；Train on a larger variety of non-clone pairs with superficial similarities.；Use graph-based representations to capture higher-level semantics.

### case_id=3553 FP lexical_or_api_overlap

- 方法: `createFile` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a source file to a resource managed by a resource manager.
- B 摘要: Main method for an adapter generator that parses a Prolog file, generates adapter classes, and writes them to a JAR file.
- 静态失败原因: The static BERT model likely relied on token-level overlap (e.g., File, IOException, try, catch) and missed the vast structural and semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the functions have completely different purposes, control flow, and output; they only share trivial API usage.
- 共享行为: Both use File objects and handle IOException；Both use try-catch blocks
- 行为差异: Function A is a simple file copy; B is a complex multi-step code generation pipeline；A writes to a resource manager; B writes JAR files and generates Java classes；A has no conditional logic; B has extensive argument parsing and debugging options
- 修正建议: Use graph-based code representations (AST, CFG) to capture structural differences；Incorporate data flow analysis to distinguish simple copy from complex transformation；Train on more diverse negative pairs with low token similarity but different semantics

### case_id=3554 FP partial_functionality

- 方法: `handleHandshake` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Validates handshake data and authenticates with Minecraft session server.
- B 摘要: Reads the first line of content from a given URL.
- 静态失败原因: The model likely overfitted to the common subsequence of URL opening, reading, and closing, ignoring the surrounding context and different control flows.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels non-clone because the functions serve completely different purposes and only share a trivial utility pattern; they are not semantically equivalent or even substantially similar in functionality.
- 共享行为: Both open a URL connection and read a line of text.
- 行为差异: A has complex validation logic and handles authentication; B is a simple GET request.；A modifies network state (sends packets, shuts down connection); B does not.；A uses multiple separate code paths; B is linear.
- 修正建议: Train models to consider the overall purpose and control flow, not just common API patterns.；Use data augmentation that masks common utility patterns to reduce spurious correlations.；Incorporate task-level semantic understanding (e.g., function naming, surrounding context).

### case_id=3555 FP lexical_or_api_overlap

- 方法: `readUNI` vs `postXml`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads and parses tab-separated data from a URL stream, adding descriptions to a vector.
- B 摘要: Sends an XML SOAP request via HTTP POST and returns the response body as a string.
- 静态失败原因: Static models likely over-relied on lexical overlap such as 'URL', 'openStream', 'try-catch', 'IOException', and generic I/O patterns, ignoring the fundamental divergence in data flow direction and processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the core functionality is entirely different: one is a data ingestion parser, the other is an HTTP client for SOAP calls. No partial functionality overlap.
- 共享行为: Both involve opening a network connection to a URL and reading input streams
- 行为差异: A receives data, B sends data; A parses tab fields, B reads raw response; A modifies a vector, B returns a string; A catches exceptions silently, B propagates as RuntimeException
- 修正建议: Add awareness of method return type and input/output direction；Incorporate data flow analysis to distinguish read vs write operations；Detect distinct API usage patterns (Scanner vs HttpURLConnection)

### case_id=3556 FP lexical_or_api_overlap

- 方法: `getUser` vs `sendRequest`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from database or config file based on login.
- B 摘要: Sends an XML request to a servlet over HTTP and reads the response.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on lexical overlaps (URL, BufferedReader, try-catch) and similar structural patterns (opening streams, reading, exception handling), ignoring the semantic context and overall goal.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely annotates as non-clone because the functions serve completely different purposes: one is a user lookup, the other is an HTTP client. Even with some overlapping APIs, the core functionality is distinct.
- 共享行为: Both use java.net.URL to open a connection or resource；Both handle I/O with readers and streams；Both catch exceptions and print stack traces
- 行为差异: A reads from a local config file and database; B sends a network HTTP request；A returns a User object; B returns an empty string；A involves user authentication; B involves server communication and XML parsing；B includes a GUI dialog for IP/port configuration; A has no user interaction
- 修正建议: Incorporate dataflow analysis to distinguish local file access from network communication；Use finer-grained semantic features like method name and return type；Train on more diverse examples of non-clones with overlapping APIs but different intent

### case_id=3557 FP lexical_or_api_overlap

- 方法: `readUNI` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: readUNI reads a tab-separated file from a URL and extracts ID and description fields, adding them to a vector.
- B 摘要: SRWGuiClient is a constructor that initializes a Swing browser, loads an XML or HTML page from a URL, optionally applies XSLT transformation, and displays it.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the common tokens like 'URL', 'openStream', and 'while' loop, while ignoring the distinct method signatures and overall different purposes. The long code length may have caused attention to focus on overlapping substrings rather than global semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clones because they perform completely different functionalities (data extraction vs GUI construction) despite both reading from a URL. The annotation preference is for functional similarity, not just shared I/O patterns.
- 共享行为: Both open a URL and read content line by line
- 行为差异: readUNI extracts tab-separated fields and stores in a vector; SRWGuiClient constructs a GUI and processes XML/HTML；readUNI uses Scanner; SRWGuiClient uses BufferedReader and non-XML/XSLT processing；readUNI is a void method; SRWGuiClient is a constructor that sets up UI
- 修正建议: Improve model sensitivity to method structure and control flow differences；Incorporate more detailed data flow analysis to distinguish reading patterns；Use method name and signature as additional cues

### case_id=3558 FN partial_functionality

- 方法: `doTransfer` vs `load`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request to a specified URL, copying headers and body, and returns the response.
- B 摘要: Downloads XML content from a Pastebin URL given an ID and returns it as a string.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token and syntactic similarity. Low token Jaccard, different method names and parameters, and different code structures (A is much longer with complex I/O) led to low similarity scores. The models likely missed the high-level semantic commonality of performing an HTTP GET and reading the response.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'HTTP client operations that download content from a URL', which is a common functional category in BigCloneBench. The partial functionality similarity (making HTTP GET and reading response) is enough for a positive clone label in BCB's broad taxonomy.
- 共享行为: Both open an HTTP connection to a URL；Both read the response body from the connection；Both handle IO exceptions
- 行为差异: A forwards the entire request (headers, body) while B only does a simple GET；A sets multiple request properties; B only constructs a URL；A outputs the response to a servlet output stream; B returns a String；A uses HttpURLConnection and handles response codes; B uses URLConnection and ignores response code
- 修正建议: Use dataflow analysis to capture HTTP request/response patterns；Incorporate API usage embeddings (e.g., URL, URLConnection) to identify common I/O operations；Apply contrastive learning with functional role labeling to group similar tasks；Abstract control flow to high-level steps: open connection, read, close

### case_id=3559 FP long_range_semantics

- 方法: `actionPerformed` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles GUI action commands to set various application preferences, including file paths for external tools like Graphviz and ImageMagick, and settings for image scaling, date format, look-and-feel, etc.
- B 摘要: Copies a file from source to target using NIO FileChannels.
- 静态失败原因: The static model likely misclassified due to the extreme length difference: the very long function A may have caused the model to lose context, and the short function B may have been matched based on a few overlapping tokens (e.g., 'File', 'chooser', 'path') leading to a false positive. The token Jaccard is very low (0.037), but the model's attention might have overweighed those few tokens.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotations typically require functional similarity beyond trivial coincidences. These two functions have completely different purposes and implementations, so BCB would not consider them clones.
- 共享行为: Both methods operate on files in some way (selecting vs copying), but the operations are fundamentally different.
- 行为差异: Function A is a complex event handler with many conditional branches and GUI interactions; Function B is a simple utility with no conditions.；Function A has side effects on application state and UI; Function B only performs file I/O.；Function A is very long (~100+ lines); Function B is very short (5 lines).
- 修正建议: Improve model capacity to handle long sequences, e.g., by using hierarchical attention or better memory mechanisms.；Enhance tokenization to better capture structural differences.；Incorporate graph-based representations (e.g., AST, dataflow) to expose the large conceptual gap.

### case_id=3560 FN partial_functionality

- 方法: `testNetworkHTTP` vs `getXML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A test method that makes multiple HTTP GET requests to fixed URLs and discards the response.
- B 摘要: A utility method that performs an HTTP GET request with a parameter, reads the response, and returns it as a string.
- 静态失败原因: Low token overlap (0.2) and different function signatures (void vs String) mislead BERT; BERT may focus on structural differences like multiple loops vs single loop and different variable names.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: Both involve core HTTP GET workflow, and BCB may consider similar I/O operations and exception handling as Type-4 clone.
- 共享行为: Both open HTTP connections；Both read response line by line；Both handle IOException
- 行为差异: A makes multiple requests with hardcoded URLs; B makes a single request with an encoded parameter；A discards response; B returns response as string；A has no return value; B returns String
- 修正建议: Incorporate data flow analysis to capture similar API usage patterns；Use code summarization techniques that abstract away specific URLs and variable names

### case_id=3561 FP boilerplate_overlap

- 方法: `callService` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Connects to a URL constructed from instance fields, reads all lines from the response, and stores the entire content in the 'answer' field.
- B 摘要: Connects to a hardcoded URL, reads the last line from the response, and returns it as a string (or null on error).
- 静态失败原因: Static BERT models rely heavily on token overlap and structural similarity. Both functions share common 'URL', 'BufferedReader', and while-loop patterns, leading the model to overestimate similarity while missing semantic differences such as return type, field assignment vs return, and whether all lines or only the last line is used.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because despite similar URL-reading structure, the behaviors differ significantly: different return types, different handling of the read data (all lines vs last line), different URL construction, and different error handling. These differences likely exceed the threshold for Type-3/4 clone acceptance.
- 共享行为: Both open a URL connection and read line by line using BufferedReader；Both close the reader after reading
- 行为差异: A stores result in field 'answer' (void); B returns the result (String)；A reads all lines into a StringBuffer; B only keeps the last line；A constructs URL from dynamic fields; B uses a hardcoded URL；A catches specific exceptions; B catches generic Exception
- 修正建议: Incorporate dataflow or type information to distinguish how read data is consumed；Use contrastive learning to penalize pairs with differing return types or variable assignments；Add emphasis on method signatures and side effects during training

### case_id=3562 FP boilerplate_overlap

- 方法: `loadExistingAntlibs` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads antlib definitions by reading classpath resources, parsing URIs, and calling loadAntLib.
- B 摘要: Extracts a full-screen YouTube video URL by fetching a page, parsing for 'fullscreenUrl', and building a new URL.
- 静态失败原因: Static BERT/GraphCodeBERT may over-rely on lexical and syntactic overlap (e.g., similar variable names like 'url', 'conn', 'rd', common patterns like opening a stream and reading lines) while missing the distinct domain contexts and final actions (loading an antlib vs. constructing a YouTube URL).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functional purpose is entirely different, despite some shared I/O boilerplate. The annotation guidelines prioritize semantic equivalence or strong partial overlap, which is absent here.
- 共享行为: Both open a URL/stream connection；Both use BufferedReader to read lines；Both loop through lines and conditionally process them；Both handle IOException and use try-catch
- 行为差异: A loads antlib resources; B extracts YouTube video info；A uses Enumeration of multiple resource URLs; B uses single URL；A constructs antlib URIs and calls loadAntLib; B builds a get_video URL string；A handles URISyntaxException; B does not
- 修正建议: Use program-dependency graphs to model data-flow differences；Incorporate API call context and method names into embeddings；Apply contrastive learning with hard negative pairs that share I/O patterns but differ in intent

### case_id=3563 FP other

- 方法: `readAndRewrite` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads a DICOM file, parses header up to PixelData, reads pixel data, and writes to a new file.
- B 摘要: Handles GUI ActionEvent to set preferences for external tools (e.g., Graphviz, ImageMagick) and update UI components.
- 静态失败原因: The static model likely overfocused on shallow API references (e.g., File, streams) and ignored the vast semantic difference, possibly due to lack of domain-specific understanding.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels as non-clone when functions are completely different in domain and implementation; these two have no functional similarity.
- 共享行为: Both involve file-related operations (A: actual I/O; B: file path selection)；Both have exception handling constructs (A: IOException; B: SukuException)
- 行为差异: A: DICOM medical image format processing; B: GUI event handling for user settings；A: Uses ImageInputStream/OutputStream; B: Uses JFileChooser and preference storage；A: No user interaction; B: Interactive dialog and UI updates；A: Specific pixel data manipulation; B: Reading/writing preferences to controller
- 修正建议: Train on more diverse data to learn domain-specific patterns；Utilize structural information like AST or data flow to distinguish I/O operations vs GUI events；Set minimum token Jaccard threshold to filter extremely dissimilar pairs (0.02 is very low)

### case_id=3564 FP lexical_or_api_overlap

- 方法: `read` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a resource file, splits it into sections by '---', and validates the expected number of sections.
- B 摘要: Makes an HTTP GET request to a URL, reads the first line of the response, and returns it.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-relied on lexical overlap ('URL', 'BufferedReader', 'readLine') and structural similarity (reading from stream), ignoring the broader context and control flow that differentiate the functions.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have different overall functionality despite sharing some API usage patterns; here the purposes are completely different.
- 共享行为: Both open a URL-based input stream；Both use BufferedReader and InputStreamReader to read text；Both call readLine() on the reader
- 行为差异: A reads a local classpath resource; B makes an HTTP request to an external URL；A reads all lines and aggregates them into sections; B reads only the first line；A has validation logic for section count and throws specific exceptions; B has no such validation；Return type: A is void, storing lines into a list; B returns a String
- 修正建议: Incorporate type information (e.g., differentiate URL from HttpURLConnection)；Use data flow or control flow analysis to capture differences in loop structures and error handling；Train with contrastive examples that have similar API usage but different semantics

### case_id=3565 FN partial_functionality

- 方法: `copy` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using NIO FileChannel and MappedByteBuffer, with resource cleanup.
- B 摘要: Launches an Eclipse launch configuration for a NexOpen project, reading and processing Maven pom.xml files, setting up Hibernate dialect, and copying files if needed.
- 静态失败原因: The static model likely failed to recognize the clone because it focused on the overall semantic and structural differences, which are large, and did not capture the small shared sub-behavior of file copying. The low token Jaccard similarity further reinforced the non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: None
- 共享行为: Both perform file I/O operations including reading from and writing to files or streams.
- 行为差异: Function a is a simple file copy; function b involves complex project initialization, XML processing, and property setting.；Function a uses NIO MappedByteBuffer; function b uses standard streams and IOUtils.copy.；Function a has no side effects; function b modifies project properties and creates files.；Function a is short and focused; function b is long and multi-step.
- 修正建议: Enhance models to detect partial functional similarity by learning subgraph or subprocess alignment.；Incorporate data flow and variable semantics to identify common operations even in different contexts.；Use attention mechanisms to focus on specific shared behavior patterns.

### case_id=3566 FN benchmark_preference_bias

- 方法: `addToArchive` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Writes an input stream into a zip archive entry and returns a URL.
- B 摘要: Builds a site for editing by transforming XML, reading files, and writing output.
- 静态失败原因: Static BERT correctly predicted non-clone due to low lexical overlap and clear semantic difference; no failure.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled this as a clone due to annotation error or overly broad notion of 'writing output files'.
- 行为差异: Function A is a short utility for adding a file to a zip archive; Function B is a complex method for site generation using XML transformations and file I/O.
- 修正建议: Remove this pair from the benchmark as it is a false positive in BCB annotation.

### case_id=3567 FP lexical_or_api_overlap

- 方法: `readVersion` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads version, revision, and date from a system resource version file and stores them in fields.
- B 摘要: Imports sequences from a URL in FASTA format, extracting names and sequences into lists.
- 静态失败原因: The static BERT method likely over-fitted on lexical/API overlap (e.g., both use InputStream, InputStreamReader, readLine, try-catch, IOException). It may have been fooled by similar control flow structure (while loop reading lines) and similar exception handling, but missed the different domain-specific parsing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the functionality is entirely different; one reads version metadata, the other imports biological sequences. The only commonality is basic I/O boilerplate.
- 共享行为: Uses try-catch for IOException；Reads input stream line by line
- 行为差异: Different domains: version metadata vs biological sequences；Different parsing logic: key-value prefix matching vs FASTA tokenization；Different outputs: setting fields vs populating lists
- 修正建议: Incorporate more structural AST differences；Use dataflow analysis to distinguish actual transformations performed

### case_id=3568 FN benchmark_preference_bias

- 方法: `getFile` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint in the soap:address element, and saves to temp directory, returning the file path.
- B 摘要: Converts an ACRNEMA file to DICOM format by parsing and writing tags, writing pixel data to a destination file.
- 静态失败原因: The static BERT/GraphCodeBERT model correctly predicted non-clone (0), so it did not fail; this is a potential false negative in BCB annotation. The model likely captured the semantic gap between WSDL downloading and medical image conversion.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to broad Type-4 similarity: both functions are file-processing utilities that read a file, perform some transformation, and write output, with similar structural patterns (e.g., temporary files, streams, logging). However, the specific operations and domains are entirely different.
- 共享行为: Both perform file I/O and transformation on binary/XML files.；Both use try-catch blocks and handle exceptions.；Both involve reading from an input source and writing to an output destination.
- 行为差异: Function A deals with WSDL/XML files and URL downloading; Function B deals with medical image format conversion.；Function A modifies XML attributes; Function B modifies DICOM tags and pixel data.；Function A returns a String; Function B returns void.；Function A uses NIO channels; Function B uses traditional streams with buffering.
- 修正建议: Review BCB annotation guidelines to ensure consistency; such dissimilar functionalities should not be labeled as clones.；Use functional composition or domain-specific matching to avoid over-generalization.

### case_id=3569 FP boilerplate_overlap

- 方法: `readZoneIDs` vs `sendRequestObjectResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.99`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads integer zone IDs from a resource file.
- B 摘要: Sends an HTTP request to a server and saves the response to a file, returning the file path.
- 静态失败原因: Static BERT likely overemphasized common API tokens like 'URL', 'try', 'catch', and 'printStackTrace', leading to false positive despite low overall similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have completely different functionality and very low token overlap (0.07).
- 共享行为: Both use java.net.URL；Both use try-catch blocks with printStackTrace
- 行为差异: readZoneIDs reads from a local resource; sendRequestObjectResponse communicates with a remote server.；readZoneIDs returns a HashSet of integers; sendRequestObjectResponse returns a file name string.；sendRequestObjectResponse involves writing to output stream, handling content types, and creating files.；readZoneIDs has no HTTP or file output operations.
- 修正建议: Incorporate data flow analysis to distinguish local resource reading from HTTP communication.；Increase penalty for low token Jaccard similarity in combination with functional dissimilarity.；Use control flow graph differences to differentiate simple read from complex HTTP interaction.

### case_id=3570 FP boilerplate_overlap

- 方法: `googleImageSearch` vs `wordFrequency`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches image URLs from Google Images search results for the current artist/album.
- B 摘要: Queries a web service to compute the frequency of a given word by parsing the response with a regex pattern.
- 静态失败原因: The model likely over-weighted the common boilerplate (URL, HttpURLConnection, BufferedReader, try-catch) and ignored the distinct task-specific logic, leading to a false positive due to lexical and structural overlap in the boilerplate.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the core functionality differs entirely; only generic I/O code is shared, which is not sufficient for clone classification in BigCloneBench.
- 共享行为: Open HTTP connection to a URL；Read response line by line with BufferedReader；Handle IOException and other exceptions；Process string content from the web
- 行为差异: Different purpose: image search vs word frequency；Different parsing logic: split on href vs regex matching；Different return type: void vs int；A inputs: no arguments, uses instance fields; B inputs: a word argument
- 修正建议: Incorporate dataflow analysis to differentiate variable usage and function calls；Add attention to method name, return type, and parameters；Use contrastive learning with non-clone pairs that share boilerplate；Improve token embeddings to capture semantic roles (e.g., 'fetch images' vs 'compute frequency')

### case_id=3571 FP boilerplate_overlap

- 方法: `createHTML` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates an HTML page for different dashboard views, including dynamic content from database.
- B 摘要: Retrieves a list of tickets from a RequestTracker queue via HTTP and returns them.
- 静态失败原因: The static BERT/GraphCodeBERT may have been misled by token overlap in boilerplate API calls (BufferedReader, InputStreamReader, try-catch, logging) and the general pattern of reading lines and building a result, ignoring the completely different semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this non-clone because the functions have no common domain or purpose. The only shared patterns are generic I/O and error handling boilerplate, which is insufficient for clone acceptance even under broad Type-3/4 criteria.
- 共享行为: Both use buffered reading from input streams；Both handle exceptions with try-catch-finally；Both close resources in finally blocks；Both use logging for errors
- 行为差异: Different input parameters (enum vs string and long)；Different return types (String vs List<RTTicket>)；Different internal logic: HTML generation with SQL queries vs HTTP API calls；Different libraries: JDBC and Swing vs Apache HttpClient
- 修正建议: Improve model to focus on substantive logic (e.g., return types, method names, core API calls) rather than boilerplate；Incorporate type information and method signatures to distinguish data flow；Train on more non-clone pairs with similar boilerplate but different purpose

### case_id=3572 FP boilerplate_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses a Prolog file and generates adapter classes and resources.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: The static model likely overfit to lexical/API overlap (File, IOException, e.printStackTrace) and ignored the semantic difference in the overall task.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the two functions have entirely different functionality and only share trivial boilerplate exception handling.
- 共享行为: Both handle IOException with try-catch and print stack trace；Both use File objects
- 行为差异: Function A performs complex code generation and class writing; Function B performs simple file copy；Function A has conditional logic and multiple steps; Function B is straightforward；Function A returns void; Function B returns boolean；Function A has a main method signature; Function B is a protected method
- 修正建议: Train with more diverse non-clone pairs that share boilerplate but differ semantically；Incorporate data flow or control flow features to capture functional purpose；Use contrastive learning to penalize high similarity due to common APIs

### case_id=3573 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `init`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft handshake by validating username and performing server authentication via HTTP.
- B 摘要: Initializes servlet by loading controller classes from a registry file on classpath.
- 静态失败原因: Static models may over-rely on lexical overlap of common Java APIs (URL, BufferedReader, InputStreamReader) and exception handling patterns, missing the semantic differences in overall task.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions have distinct purposes and no overlapping functionality despite similar API usage.
- 共享行为: Both open an InputStream from a URL and wrap it in a BufferedReader；Both read lines from the stream；Both have exception handling with printStackTrace
- 行为差异: Function A interacts with a game session server and sends packets; Function B loads classes and registers them；Function A uses username validation and HTTP GET; Function B reads class names from a resource file；Different method signatures and contexts (handshake vs servlet init)
- 修正建议: Incorporate structural or data-flow analysis to differentiate between network handshake and class loading；Use context-aware embeddings that capture method role within the class；Increase weight on method signature and surrounding code

### case_id=3574 FN benchmark_preference_bias

- 方法: `doTransfer` vs `CheckUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request to a target URL by copying headers and body, and returning the response.
- B 摘要: Fetches the first line of content from a given URL as a string.
- 静态失败原因: The static BERT model correctly identified the low token overlap (0.125) and structural differences, leading to correct non-clone prediction, but this contradicts the potentially erroneous BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled it as a clone because both functions involve opening a URL connection and reading input, which could be considered partial functionality similarity under broad Type-4 criteria.
- 共享行为: Both create a URL object and open an HttpURLConnection
- 行为差异: A is a full HTTP proxy with request/response forwarding; B is a simple URL content fetcher；A handles headers, request body, response codes, and writes to output stream; B only reads first line and returns it；A takes HttpServletRequest/Response objects; B takes a String URL；A uses a method parameter and sets request method; B always uses GET
- 修正建议: Review BCB annotation guidelines to ensure consistency；Train model to recognize that common API boilerplate does not imply semantic equivalence

### case_id=3575 FN benchmark_preference_bias

- 方法: `doTransfer` vs `readReferenceText`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request to a remote URL, copying headers and body, then relaying the response.
- B 摘要: Reads the content of a local resource file identified by a name and returns it as a string.
- 静态失败原因: The static model focused on overall semantic equivalence and low token overlap, missing the broader clone definition used by BCB. It correctly identified strict non-clone but failed to match BCB's partial functionality criterion.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotators may consider these clones due to the common pattern of opening a URL, reading input, and handling IOExceptions, which is a Type-4 partial functionality match.
- 共享行为: Open a URL from a string；Read from an InputStream；Catch MalformedURLException and IOException
- 行为差异: A obtains URL from request parameter; B constructs URL from bundle path；A copies request headers and sends request body; B does not；A writes response to output stream; B returns string content；A manages multiple streams; B reads lines with BufferedReader
- 修正建议: Fine-tune on BCB data to learn partial clone patterns；Incorporate structural similarity beyond token overlap；Use multi-label or hierarchical clone classification

### case_id=3576 FN partial_functionality

- 方法: `setPayload` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.2`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies data from HeadlessData to a file specified by Headers[Index] using FileChannel, then updates state.
- B 摘要: Retrieves a resource from cache or downloads it, returning an InputStream.
- 静态失败原因: Static BERT models rely on token similarity and structure; the low Jaccard (0.074) and different method names led to a non-clone prediction. The model failed to recognize broader Type-4 similarity that BCB might have considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled them as clones due to both being part of a data transfer pipeline, with setPayload writing payload to file and getResourceAsStream reading from cache, but the functional roles are opposite and not semantically equivalent.
- 共享行为: Both perform file I/O operations
- 行为差异: setPayload writes data to file; getResourceAsStream reads data from file or network；setPayload uses FileChannel transferTo; getResourceAsStream uses buffered streams；setPayload is part of a stateful loop; getResourceAsStream is a single retrieval method with caching
- 修正建议: Improve model to capture higher-level functional roles beyond lexical tokens；Use data flow or call graph information to link read/write operations

### case_id=3577 FN benchmark_preference_bias

- 方法: `decodeFileToFile` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Decodes a Base64 encoded file and writes the decoded output to another file, returning success status.
- B 摘要: Modifies a locale-specific properties file by reading, replacing or appending a key-value pair, and writing back.
- 静态失败原因: The model correctly identified these as non-clones due to low token overlap (0.2058) and significant differences in method purpose, return type, and specific logic, but the BCB label disagrees because of the aforementioned boilerplate overlap.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone due to the presence of common I/O boilerplate (file streams, try-catch-finally, while loop with read/write), which could be considered partial functionality similarity under a lenient Type-4 definition.
- 共享行为: Read from an input file and write to an output file；Use buffered streams for I/O；Handle IOExceptions and close streams in finally blocks；Use while loops for reading and writing data
- 行为差异: Function A decodes Base64-encoded data; Function B processes properties file content；Function A uses a fixed buffer; Function B reads line-by-line with character-level operations；Function A returns a boolean success flag; Function B is void；Function B includes file existence check, key search, and conditional appending
- 修正建议: Enhance training data with more diverse negative pairs to reduce bias toward boilerplate similarity；Incorporate dataflow or program dependency features to capture functional semantics beyond lexical patterns；Use contrastive learning that emphasizes functional equivalence over structural commonalities

### case_id=3578 FN partial_functionality

- 方法: `main` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL and prints its content line by line to standard output.
- B 摘要: Reads a URL and logs its content as a single string using a debug logger.
- 静态失败原因: Static BERT models rely heavily on token overlap and syntactic similarity. The low token Jaccard (0.326) and different method names, strings, and API calls lead the model to deem them non-clones. It fails to capture the high-level semantic similarity of fetching and outputting URL content.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers these as Type-3 clones because both perform the same conceptual task: reading a URL and outputting its content. The minor differences in API, output target, and URL are considered implementation variations that do not change the core functionality.
- 共享行为: Both open a URL and read its content line by line.；Both use a BufferedReader to read the input stream.；Both close the reader after reading.；Both output the content, one to console, one to log.
- 行为差异: Different target URLs (one hardcoded, one variable).；Different API to obtain input stream (openStream vs openConnection().getInputStream).；Different output: System.out.println vs log.debug.；One is static main method, the other is instance method.
- 修正建议: Use code representations that abstract away constant values and specific method names.；Leverage dataflow or control flow graphs to capture structural similarity.；Train on more diverse URL reading examples to recognize the pattern.；Incorporate type information to see both use URL and BufferedReader.

### case_id=3579 FP lexical_or_api_overlap

- 方法: `getDatasetsList` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a list of datasets from a URL, caching results in a synchronized map.
- B 摘要: Retrieves the first line of content from a URL as a string, without caching.
- 静态失败原因: The model likely overemphasized the common API usage pattern (URL, BufferedReader, readLine) and structural similarity (method signature with URL parameter), ignoring fundamental differences in loop, caching, and exception handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels as non-clone when functions have significantly different functionality, such as different return types, input-output behavior, or side effects; here A is a caching list retriever and B is a single-line fetcher.
- 共享行为: Both open a URL and read at least one line using BufferedReader.
- 行为差异: Different return types (List<String> vs String)；A reads all lines while B reads only first；A caches results, B does not；A uses synchronized block, B does not
- 修正建议: Train model to differentiate between similar API sequences with different control flow and data structures；Add attention to return types and caching behavior；Use dataflow analysis to capture differences in variable usage and loops

### case_id=3580 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for new version of jEdit by reading a version-check URL and extracting build numbers.
- B 摘要: Extracts the full screen URL of a YouTube video by parsing the page source.
- 静态失败原因: Model likely focused on shared API usage (URL, BufferedReader, reading lines) and control flow, ignoring distinct business logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because functions serve entirely different purposes with no meaningful functional overlap.
- 共享行为: Both open a URL and read lines using BufferedReader；Both use substring/startsWith to parse lines；Both handle IOException
- 行为差异: Different output: void vs String；Different parsing logic: version numbers vs YouTube URL parameters；Different error handling: GUI error vs System.err.println
- 修正建议: Incorporate semantic features like method names and variable semantics；Use data flow analysis to capture output differences；Add training examples that distinguish generic I/O patterns from specific functionality

### case_id=3581 FP other

- 方法: `perform` vs `sha1`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles a web request to classify a concept, performing parameter extraction, HTTP POST to a classifier service, and parsing the XML result.
- B 摘要: Computes the SHA-1 hash of an input string and returns the hex representation.
- 静态失败原因: The static model likely overfitted to superficial similarities (e.g., exception handling, String operations) or made a random error due to the long length of function A, losing the overall semantic context.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would label this as non-clone because the two methods have entirely different functionality, one is a web request handler and the other is a cryptographic utility, with no shared behavior beyond basic Java boilerplate.
- 共享行为: Both are Java methods；Both handle exceptions
- 行为差异: Function A is a web action with session, request, response; B is a simple utility；A performs HTTP communication; B performs cryptographic hashing；A has complex control flow with multiple branches; B is linear；A returns an ActionForward; B returns a String
- 修正建议: Increase training data diversity for long methods；Incorporate structural or dataflow analysis to distinguish web handlers from utilities；Use a model that better captures function-level semantics, e.g., code summarization or AST-based methods

### case_id=3582 FN benchmark_preference_bias

- 方法: `testNetworkHTTP` vs `PhoneSetImpl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: A test method that makes multiple HTTP GET requests to various URLs and reads the response streams without processing.
- B 摘要: A constructor that reads a URL resource line by line, parses lines not starting with "***", and populates a map.
- 静态失败原因: The static model likely recognized the significant differences in control flow (multiple URLs vs one), exception handling, and data usage, and thus correctly identified them as non-clones. It did not fail but rather the BCB annotation is questionable.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: None
- 共享行为: Both create a URL and open a connection/stream to read its content；Both use BufferedReader to read lines
- 行为差异: A makes multiple requests to different URLs; B processes a single URL；A discards the read data; B parses and stores data in a map；A catches IOException and prints stack trace; B throws IOException；A uses HttpURLConnection with disconnect(); B uses URL.openStream() and close()
- 修正建议: Consider more fine-grained semantic features such as data flow and exception handling；Include purpose detection to differentiate test methods from constructors；Use code summarization to confirm behavioral similarity

### case_id=3583 FN benchmark_preference_bias

- 方法: `doFinishLoadAttachment` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles saving an email attachment to external storage or opening it in a viewer activity.
- B 摘要: Builds and transforms XML-based pages for a content management system, writing output files.
- 静态失败原因: The static model correctly predicted non-clone due to very low token overlap and different semantics; this is not a failure but rather an indication that BCB annotation is likely incorrect for this pair.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone due to broad interpretation of 'similar functionality' such as both involving file processing, but the tasks are completely unrelated and only share generic I/O patterns.
- 共享行为: Both perform file I/O operations (reading/writing files) but with entirely different purposes and contexts.
- 行为差异: Function A deals with Android attachment handling (content URIs, intents) while function B deals with XML transformations and web page generation.；Function A has conditional save vs. view logic; function B has complex XSLT transformation loop over pages.；No overlap in input parameters, data structures, or external APIs.
- 修正建议: Review BCB annotation guidelines to avoid over-generalizing functionality similarity.；Consider excluding pairs with very low token Jaccard and no shared domain from clone labels.

### case_id=3584 FN benchmark_preference_bias

- 方法: `doGet` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles an HTTP GET request to retrieve and render a portal page with permission checks, logging, and caching.
- B 摘要: Reads a DICOM file, parses it, reads pixel data, and writes the dataset to another file.
- 静态失败原因: Static BERT models rely on lexical and syntactic overlap, which is minimal here. They may fail to capture the abstract high-level functional similarity that BCB annotators perceived.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to a broad interpretation of Type-4 similarity, considering both as 'data processing' functions with a similar overall structure (read input, process, write output), despite different domains.
- 共享行为: Both perform input processing and output generation；Both use try-catch for error handling；Both involve logging
- 行为差异: Different input/output types (HTTP request vs. file, page vs. DICOM)；Different domain-specific logic and libraries；Function A includes permission checks and caching; Function B does not
- 修正建议: Include training examples with diverse domains but similar abstract functionality；Use graph-based models that capture data flow and control flow

### case_id=3585 FN partial_functionality

- 方法: `writeFileType` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads URIs from a file, visits each URL connection, analyzes first 100 lines for OWL/RDF patterns, and writes classification to an output file.
- B 摘要: Connects to a fixed URL, reads entire content, and logs it to a debug log.
- 静态失败原因: Static models rely on token and structural overlap, which is low (Jaccard=0.18). The functions have different control flow, method names, and signatures, leading to underestimation of shared URL reading behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as URL content retrieval functions sharing the core pattern of connecting to a URL and reading content, thus being a Type-4 clone despite different output processing.
- 共享行为: Both open a URL connection and read lines using BufferedReader.
- 行为差异: A processes multiple URLs from a file and writes classifications; B processes a single fixed URL and logs full content.；A includes error handling per URL; B does not.；A limits reading to 100 lines; B reads all lines.
- 修正建议: Incorporate data flow analysis to capture URL connection and input stream usage.；Use dynamic analysis or runtime trace to reveal similar I/O patterns.；Consider intent-level features like reading from external resource.

### case_id=3586 FP lexical_or_api_overlap

- 方法: `main` vs `copyResourceToFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file and generates adapter classes into a JAR file.
- B 摘要: Copies a resource file to a destination file.
- 静态失败原因: Static BERT models may over-rely on token-level API overlap (e.g., File, IOException, try-catch) and miss the overall semantic intent due to limited context understanding.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones as 0 because these functions have no functional similarity and are from different domains.
- 共享行为: Both involve file I/O operations but at different levels of abstraction.
- 行为差异: Function A is a complex main method for code generation; function B is a simple resource copy.；Function A parses Prolog and generates multiple classes; function B just copies bytes.；Function A has extensive logic for class loading, serialization, and adapter generation; function B is straightforward stream copying.
- 修正建议: Improve model sensitivity to high-level structure and purpose.；Use dataflow or control flow analysis to differentiate trivial file operations from complex transformations.

### case_id=3587 FN partial_functionality

- 方法: `fileDownload` vs `executeHttpGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL and saves it to a destination directory.
- B 摘要: Executes an HTTP GET request and returns the response as a JSON object.
- 静态失败原因: Low lexical overlap (Jaccard=0.106) and different return types/method names caused the model to miss the underlying common pattern of reading from a URL.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers both as HTTP GET operations that read data from a web resource, ignoring differences in output handling.
- 共享行为: Both open a connection to a URL or URI；Both read data via a BufferedReader from an InputStream
- 行为差异: Function A writes data to a file, while Function B constructs a string and parses JSON；Function A uses URLConnection, Function B uses HttpClient/HttpGet；Return type is void vs JSONObject
- 修正建议: Use graph-based representations capturing control and data flow；Incorporate structural similarity of I/O patterns；Consider method purpose from context

### case_id=3588 FN partial_functionality

- 方法: `moveFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Moves a file by copying its contents to a new location and deleting the original.
- B 摘要: Downloads a ZIP file from a URL, extracts its entries, and writes each entry to a file.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token-level embeddings and low lexical overlap (Jaccard=0.24) led to missing the structural similarity of the I/O loop pattern, focusing instead on method names and overall purpose.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a clone because both functions implement a common pattern of reading from an InputStream and writing to an OutputStream using a buffered loop, which is a typical Type-4 semantic clone in BigCloneBench.
- 共享行为: Both read from an input stream and write to an output stream using a byte buffer loop.
- 行为差异: Different data sources (local file vs. URL/ZIP).；Different output destinations (single file vs. multiple files from ZIP entries).；Additional protocol handling and ZIP extraction logic in B.；A deletes the original file; B does not.
- 修正建议: Train with more data augmentation focusing on structural I/O patterns.；Use dataflow-aware models to separate boilerplate I/O from specific functionality.

### case_id=3589 FP boilerplate_overlap

- 方法: `persist` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: persists a configuration object to a file by copying its input stream to an output stream.
- B 摘要: reads and initializes static data structures for Tibetan transliteration from a file and string tokens.
- 静态失败原因: The static model likely over-indexed on boilerplate elements (try-catch, IOException, file handling) and ignored the distinct logic and data structures, leading to a false positive despite low token overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions serve entirely different purposes and have no semantic overlap; even broad Type-4 similarity requires some shared functionality, which is absent.
- 共享行为: Both involve file I/O operations.；Both handle exceptions with try-catch blocks.；Both are void methods that do not return a value.
- 行为差异: A writes to a file, B reads from a file and string literals.；A uses parameterized objects and IOUtils.copy, B parses tokens and populates static sets/maps.；A throws a custom ConfigurationException, B catches IOException and prints an error.；A is a simple data transfer, B is a complex initialization with multiple parsing stages.
- 修正建议: Train with more diverse negative pairs that share common boilerplate but differ in semantics.；Improve model's ability to differentiate between general file I/O patterns and specific application logic.；Incorporate higher-level semantic abstractions such as method roles or domain-specific knowledge.

### case_id=3590 FP boilerplate_overlap

- 方法: `importSequences` vs `handledRun`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: reads sequences from a URL-based FASTA file and stores names and sequences.
- B 摘要: downloads gamedata XML from a URL and updates local file if version is newer.
- 静态失败原因: Static BERT models may rely heavily on token overlap and common API sequences (e.g., URL.openStream, BufferedReader, IOException). Both functions share this high-level I/O pattern, leading the model to false positive despite low Jaccard similarity and divergent semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench typically annotates clones based on functional similarity beyond boilerplate I/O patterns. These two methods perform entirely different tasks (sequence import vs game data update), so BCB would label them as non-clones.
- 共享行为: open a URL stream to read data from a remote server；use BufferedReader or InputStreamReader to read text；handle I/O exceptions with try-catch blocks；read lines or characters from the stream
- 行为差异: different data formats (FASTA vs XML headers and content)；different processing logic (parsing FASTA lines vs version comparison and file writing)；different outputs (ArrayList of names/sequences vs file on disk)；different exception handling strategies (printStackTrace vs logging and JOptionPane)
- 修正建议: Incorporate data-flow and control-flow analysis to distinguish different data manipulations；Consider method context (class, project) to identify domain differences；Train on more diverse negative examples that share I/O patterns but differ in purpose；Use heuristics to discount common boilerplate sequences when overall token similarity is low

### case_id=3591 FN lexical_or_api_overlap

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (file or URL) to a destination file using byte-by-byte stream copying.
- B 摘要: Copies a source file to a destination file using NIO FileChannel transfer.
- 静态失败原因: Static BERT methods rely heavily on token overlap; low Jaccard (0.109) and differing method signatures led to false negative.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB considers broad Type-3/Type-4 clones even if API differ, as long as core functionality (file copying) is preserved.
- 共享行为: Both copy content from a source to a destination file.；Both close input/output streams/channels after copying.
- 行为差异: Function A accepts a source string (URL or file path), while B requires a File object.；Function A reads byte-by-byte (stream), B uses FileChannel.transferFrom which is more efficient.；Error handling: A throws Exception, B catches IOException and returns boolean indicating success.
- 修正建议: Incorporate data flow analysis to capture semantic equivalence despite different APIs.；Use abstract syntax trees to focus on control flow structure rather than surface tokens.

### case_id=3592 FN partial_functionality

- 方法: `runScript` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from a URL byte by byte and returns its content as a string.
- B 摘要: Checks for software version updates by reading a version file from a URL, parsing lines, and invoking a version check dialog.
- 静态失败原因: Low token overlap (0.23) and different control flow beyond the common pattern likely misled the model; static BERT may not capture the shared URL-reading intent due to divergent surrounding context.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers functions sharing a common API usage pattern (URL.openStream, InputStream reading) as clones at a high level, even if their specific processing logic differs.
- 共享行为: Open a URL and read from an InputStream；Handle IO-related exceptions；Return or produce error messages on failure
- 行为差异: runScript reads raw bytes; doVersionCheck reads lines using BufferedReader；runScript returns a string; doVersionCheck is void and updates UI；Exception handling: runScript catches generic Exception; doVersionCheck catches IOException；Additional UI operations in doVersionCheck (show/hide wait cursor, error dialog)
- 修正建议: Incorporate data flow analysis to distinguish reading vs. parsing；Use graph-based representations to capture structural similarities beyond token overlap；Focus on semantic intent via function name and comment analysis

### case_id=3593 FN benchmark_preference_bias

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel with proper resource management.
- B 摘要: Builds a static site for editing by processing XML, reading/writing files, and performing string replacements, with extensive error handling.
- 静态失败原因: The static model likely relied on token overlap (Jaccard 0.0648) and structural similarity, which are low, so it correctly identified them as non-clones. The failure is due to BCB's potentially erroneous label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to the presence of file I/O operations (FileInputStream/FileOutputStream) in both, considering partial functionality similarity, but this seems overly broad.
- 共享行为: Both functions perform file I/O operations (reading and writing files).
- 行为差异: Code A is a simple file copy; Code B is a complex site generation process involving XML transformations, multiple file reads/writes, and string replacements.；Code B has many parameters and uses external libraries; Code A is self-contained.；Code B includes debugging output and FTP error handling; Code A does not.
- 修正建议: Improve model to detect functional similarity beyond token overlap, e.g., by incorporating program flow or using hierarchical representations.；Re-evaluate BCB labeling for this pair to ensure consistency.

### case_id=3594 FP boilerplate_overlap

- 方法: `get` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches game records from a URL using latitude, longitude, and count parameters, filters comment lines, and returns an array.
- B 摘要: Performs an HTTP GET with Basic Authentication, reads entire response into a string, and signals completion.
- 静态失败原因: Static BERT models rely on token overlap and surface-level patterns. Both functions share common HTTP client boilerplate (HttpURLConnection, BufferedReader, etc.) leading to a high token Jaccard similarity. The model fails to capture the semantic differences in request headers, output processing, and overall intent, causing a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have different overall functionality despite similar boilerplate. Here, one is a game record fetcher with filtering and typed output, the other is an authenticated downloader that concatenates all lines. The core purpose differs, so BCB correctly labels as non-clone.
- 共享行为: Both open an HTTP connection using HttpURLConnection with GET method.；Both set request properties on the connection.；Both read input using BufferedReader and iterate over lines.；Both use try-catch for IOException/Throwable.
- 行为差异: Function A uses custom headers for latitude, longitude, and count; Function B uses Authorization header for Basic Auth.；Function A filters lines starting with '#' and decodes GameRecord objects; Function B appends all lines to a StringBuffer.；Function A returns GameRecord[] or null; Function B sets instance variables result and finish, and has no return value.；Error handling differs: A prints stack trace and returns null; B stores exception in field this.e.
- 修正建议: Incorporate data flow analysis to track how request properties are set and how response is processed.；Use models that capture API call sequences and their parameters more precisely.；Consider output types and method signatures to disambiguate different functionalities.

### case_id=3595 FP lexical_or_api_overlap

- 方法: `main` vs `getZipAsFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses a Prolog file, generates adapter classes, and writes them to a JAR with serialized adapter layer.
- B 摘要: Helper method that extracts a DigitalObject's content stream into a zip file in a temporary folder.
- 静态失败原因: The static model likely over-relied on lexical overlap (e.g., common use of File, FileUtils, IOException, printStackTrace) and missed the semantic mismatch due to high-level goal differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions have fundamentally different purposes and functionality, despite superficial lexical similarities in I/O handling.
- 共享行为: Both involve file I/O operations (reading/writing files)；Both use Apache Commons IO (FileUtils) for file operations；Both handle IOException and print stack traces
- 行为差异: Function A is a complex main method for adapter generation; Function B is a simple file extraction helper；Function A processes Prolog files and generates Java classes; Function B extracts a DigitalObject's content to a zip；Function A has extensive logic for parsing, code generation, and serialization; Function B has minimal logic；Input types and output goals are completely different
- 修正建议: Incorporate semantic role labeling or code summarization to capture function purpose；Use control flow and data flow analysis to distinguish trivial vs complex I/O；Leverage function name and context (main vs private helper) to disambiguate

### case_id=3596 FP boilerplate_overlap

- 方法: `getURLContent` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads content from a URL and returns it as a single string, handling encoding.
- B 摘要: Reads a tab-separated file from a URL, parses specific fields, and populates a vector with concatenated id and description.
- 静态失败原因: Static BERT models often rely on token-level patterns and structural similarity. The high overlap in URL handling boilerplate (URL, openStream, close, try-catch-finally) can mislead the model into classifying them as clones, while overlooking the significant differences in data processing logic and output behavior. The model fails to capture the semantic distinction between returning a string vs. parsing TSV into a vector.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled these as non-clones because despite sharing boilerplate URL reading, their core functionality differs substantially: one is a generic URL-to-string utility, the other is a specific TSV parser for a particular data format. BigCloneBench typically considers Type-4 clones (functionally similar but different in specific behavior) as non-clones unless the similarity is very high.
- 共享行为: Both open a URL connection to a given URL string.；Both read text content line by line from the URL stream.；Both close the input stream or reader in a finally block.
- 行为差异: Function A returns the entire content as a string, while function B populates a provided vector with parsed data.；Function A handles character encoding explicitly; function B uses default encoding with Scanner.；Function A appends newline characters; function B parses tab-delimited fields and skips the first header line.；Function A uses BufferedReader; function B uses Scanner with custom delimiters.
- 修正建议: Incorporate data flow analysis to track outputs and how data is transformed.；Use method signatures and return types as additional features.；Apply contrastive learning on pairs with similar boilerplate but different semantics.；Consider contextual information like method names or import statements to disambiguate purpose.

### case_id=3597 FN benchmark_preference_bias

- 方法: `doGet` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to display a page after checking permissions and logging.
- B 摘要: Retrieves a resource as an InputStream, optionally caching it from a remote URL.
- 静态失败原因: A static model like GraphCodeBERT likely failed because it correctly identified the low lexical overlap and different API usage patterns, leading to a non-clone prediction, which is correct under strict semantics.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled them as clones based on a very broad interpretation of both involving HTTP GET operations (Function A implicitly via HTTP request handling, Function B explicitly using HTTP GET), but the actual functionality is entirely different.
- 共享行为: Both are Java methods that involve I/O operations and exception handling.；Both use some form of logging (myLogger vs System.out).
- 行为差异: Function A is a servlet handler that returns void and writes to HttpResponse; Function B returns an InputStream.；Function A deals with page objects, user permissions, and portal request context; Function B deals with URL connections, file caching, and cache hashtables.；Function A has complex business logic for page selection and rendering; Function B has a caching mechanism for remote resources.
- 修正建议: Re-examine BCB annotation for this pair; likely a labeling error.；If maintaining the clone label, define more refined criteria for functional similarity.

### case_id=3598 FN partial_functionality

- 方法: `doVersionCheck` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads a version check URL, parses build and stable build lines, and displays version info or error.
- B 摘要: Initializes character sets and parsing structures for Tibetan transcription by tokenizing comma-separated strings and reading a data file.
- 静态失败原因: Static BERT likely focused on low token overlap (0.098) and different APIs (URL vs StringTokenizer), missing the high-level pattern of input parsing and data population that BCB may consider similar.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone due to both being static methods that read input and populate data structures, possibly considered Type-4 (semantic similarity) under a very broad interpretation of 'data initialization'.
- 共享行为: Both read input data line by line；Both populate data structures (sets, maps)；Both handle IOException with error reporting
- 行为差异: Function A reads from a URL and checks specific line prefixes; Function B tokenizes string fields and reads a file with columns；Function A is much shorter and simpler; Function B is very long with complex conditional logic；Function A calls another method with results; Function B builds multiple sets and a hash map
- 修正建议: Use a hierarchical model that captures coarse-grained intent (e.g., 'reading and initializing')；Incorporate program slicing to extract core data flow；Add synthetic negative pairs with similar structure but different purpose

### case_id=3599 FN benchmark_preference_bias

- 方法: `doGet` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Forwards an HTTP GET request to a Fedora URL, copying response headers and body.
- B 摘要: Modifies a locale-specific properties file by replacing or adding a message key-value pair.
- 静态失败原因: The static model correctly identified them as non-clones given the low lexical overlap and clearly different semantics. The BCB label is likely an outlier.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these clones due to a broad interpretation of functionality related to 'modifying' or 'forwarding' content, despite very different contexts. Alternatively, this could be a labeling error.
- 共享行为: Both perform I/O operations (reading and writing streams/files).；Both use String manipulation and exception handling.
- 行为差异: Function A handles HTTP request/response headers and streams; Function B handles file system I/O on properties files.；Function A uses URLConnection and streams; Function B uses FileReader, FileWriter, and Properties.；Function A logs extensively; Function B prints stack trace on exception.；Function A has no explicit resource management; Function B closes readers/writers.
- 修正建议: Improve model to handle semantics beyond lexical similarity.；Review BCB annotations for potential noise.

### case_id=3600 FN partial_functionality

- 方法: `doGet` vs `parseContent`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles an HTTP GET request to retrieve and render a portal page, with error handling and caching.
- B 摘要: Parses HTML content from a stream, extracting metadata, links, body text, and language information.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token and structural similarities. With a Jaccard similarity of only 0.0845, very different method names (doGet vs. parseContent), and distinct logic (servlet vs. parser), the model likely failed to capture the abstract, high-level functional overlap that BCB considers. The model is biased toward lexical and syntactic matching, which are absent here.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both are part of a web processing pipeline, performing sequential steps to handle HTTP-related data, and share patterns like property lookups and exception handling. The broad functional similarity (web content processing) and overlapping utility code could justify a Type-3/Type-4 clone under BCB guidelines.
- 共享行为: Both involve processing input and generating output relevant to web content.；Both use property retrieval (Property.getProperty/getProperty) and handle exceptions.；Both reference HTTP-related concepts (headers, content type).
- 行为差异: Function A is a servlet doGet invoked by HTTP requests; Function B is a protected parseContent method for HTML parsing.；A writes to HttpServletResponse; B adds fields to a document (ParserFieldEnum).；A deals with page visibility and user permissions; B deals with charset detection and HTML provider selection.；A includes caching logic and statistics; B focuses on extracting and indexing web page content.
- 修正建议: Incorporate functional dependency or call-graph aware embeddings to recognize common sub-tasks.；Use contrastive learning with BCB labels to emphasize broad functional similarity over lexical overlap.；Add data augmentation that mixes methods from different modules but with shared high-level intent.

### case_id=3601 FP boilerplate_overlap

- 方法: `handleHandshake` vs `getXML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles server handshake by validating username and performing authentication via HTTP request.
- B 摘要: Retrieves XML content from a given URL using HTTP GET.
- 静态失败原因: The model may have overemphasized shared structural patterns (URL creation, BufferedReader usage) and missed the distinct intents due to limited context or lack of understanding of the overall workflow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label this as non-clone because the functions have completely different high-level semantics and are not near-miss clones; they only share common boilerplate HTTP connection code.
- 共享行为: Both create a URL and open a connection to a server；Both read from an input stream using BufferedReader；Both close the stream after reading；Both handle exceptions (though differently)
- 行为差异: Different purposes: authentication vs. XML retrieval；Different output: void vs. String；Different error handling: network shutdown vs. return null；Different input parameters and logic
- 修正建议: Incorporate data flow analysis to capture variable dependencies and output types；Use contrastive learning to discriminate between different high-level tasks；Improve representation of control flow and error handling patterns

### case_id=3602 FP lexical_or_api_overlap

- 方法: `sendRequest` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an XML request to a server with GZIP compression and reads the response.
- B 摘要: Imports FASTA-like sequences from a URL by reading lines and parsing tokens.
- 静态失败原因: The model likely picked up on the URL/IO boilerplate tokens (like 'URL', 'InputStream', 'try', 'catch') and the structural pattern of opening a connection and reading, but failed to capture the distinct data processing logic and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would consider them non-clones because the functionality is entirely different (sending request vs. importing sequences) and they share only trivial I/O boilerplate.
- 共享行为: Both open a URL connection and read from an InputStream.；Both handle IO exceptions with try-catch blocks.
- 行为差异: A sends data (writes) and then reads a response; B only reads.；A uses GZIP compression; B does not.；A processes XML; B processes tokenized sequence lines.；A returns an empty string; B populates lists.
- 修正建议: Incorporate data flow analysis and semantic understanding of the data manipulation.；Use more discriminative features like method name, parameters, return type, and the specific library calls (e.g., GZIP, SAXBuilder vs ImportHelper).

### case_id=3603 FN partial_functionality

- 方法: `getResourceAsStream` vs `copyTo`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a remote resource and caches it locally, returning an InputStream.
- B 摘要: Recursively copies a file or directory to a destination.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on lexical and structural similarity; the low token Jaccard (0.10), different method names, and distinct control flows cause the model to miss the underlying semantic similarity in data-copying patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely views both as Type-4 semantic clones because they share the core behavior of copying data from an input source to an output destination, despite differences in source type (network vs. file) and additional logic, aligning with BCB's broad interpretation of partial functionality.
- 共享行为: Both involve opening input and output streams to copy data.；Both use try-catch for I/O exception handling.；Both perform byte-level data transfer between sources and destinations.
- 行为差异: Function A handles HTTP connections and caching logic; Function B does not.；Function A returns an InputStream; Function B is void and creates files.；Function A copies byte-by-byte with BufferedStreams; Function B uses FileChannel.transferTo.；Function B handles directories recursively; Function A does not.
- 修正建议: Enhance models with data flow analysis or program dependence graphs to capture shared I/O operations.；Include more context for utility methods (e.g., class names, surrounding code) to infer similarity.；Train on fine-grained clone types like Type-4 with explicit data transfer annotations.

### case_id=3604 FN partial_functionality

- 方法: `copyFile` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file using NIO FileChannel transferTo.
- B 摘要: Modifies a properties file for a given locale, copying the English file if necessary, then reading, modifying, and writing properties.
- 静态失败原因: Low token overlap (Jaccard 0.087) and different method names; static BERT likely missed the subtle file copy similarity buried in B's larger logic, focusing on overall structure rather than partial functionality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone because function B contains a file copy sub-task functionally similar to A, and BCB allows Type-4 partial functionality similarity.
- 共享行为: Both perform file copying operations；Both close input/output streams；Both handle file I/O exceptions
- 行为差异: A copies entire file using NIO channels; B copies only if locale file missing using IO streams；B additionally reads, modifies, and writes properties；B has complex string parsing and conditional logic；A is straightforward file copy; B has multiple steps including file existence checks
- 修正建议: Train model to recognize sub-task similarity across different contexts；Use contrastive learning on pairs with partial functional overlap；Incorporate data flow analysis to detect shared operations like file copy

### case_id=3605 FN benchmark_preference_bias

- 方法: `doTransfer` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Proxies an HTTP request by forwarding headers and body to a target URL and returning the response.
- B 摘要: Registers a user by encoding password, setting metadata, persisting to database, and optionally creating a forum account via HTTP.
- 静态失败原因: Static BERT/GraphCodeBERT likely predicted non-clone because the token overlap is low (0.1129) and the high-level semantics diverge significantly. The model might have focused on the distinct method signatures (void vs boolean, different parameter types) and domain keywords (transfer vs register).
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered these clones due to overlapping API usage (URL, URLConnection, streams) and both involving network I/O. However, the functional purpose is entirely different; this likely represents an overly broad annotation.
- 共享行为: Both open HTTP connections to external URLs.；Both read from and/or write to streams.；Both handle IOException.
- 行为差异: A is a full HTTP proxy; B performs user registration with database operations.；A copies request headers and body; B only sends a GET-like request for forum registration.；A returns void via response object; B returns boolean success.；B includes encryption, database persistence, email sending; A does none of that.
- 修正建议: Improve training data by filtering out overly broad clone pairs.；Incorporate high-level semantic features like method purpose, not just API patterns.

### case_id=3606 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `createHTML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles a Minecraft handshake by validating a server key and optionally contacting a session server to log in.
- B 摘要: Generates HTML content for different page types by reading a CSS file and building page-specific HTML including database queries.
- 静态失败原因: Static BERT/GraphCodeBERT model likely overfitted on superficial lexical similarities such as 'BufferedReader', 'URL', 'openStream', 'try/catch' blocks, and method lengths, ignoring the vast semantic difference in domain and logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones for functions with entirely different purposes, even if they share some common coding patterns like reading streams or exception handling.
- 共享行为: Uses BufferedReader to read input streams；Handles exceptions with printStackTrace or logging；Calls methods on netManager or log objects
- 行为差异: Function A performs network authentication and login; Function B generates HTML for UI；Function A reads from a URL and sends packets; Function B reads from classpath resources and builds strings；Function A's control flow depends on username validation; Function B's flow depends on an enum page type with a switch case
- 修正建议: Improve model training with more negative examples that have overlapping API usage but different semantics；Incorporate control-flow or data-flow analysis to distinguish different operation patterns；Add attention to method names and overall purpose rather than just code tokens

### case_id=3607 FP lexical_or_api_overlap

- 方法: `truncate` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Truncates and compresses a log file into a zip archive if it is older than JVM start time.
- B 摘要: Main method that parses a Prolog file and generates a JAR file with adapter classes.
- 静态失败原因: A static BERT model likely over-relied on overlapping tokens (e.g., 'File', 'FileUtils', 'try', 'catch') and similar control flow, ignoring the high-level functional divergence.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these non-clones because they solve entirely different problems: one is file archiving, the other is code generation. The shared API calls and structural patterns do not imply semantic equivalence.
- 共享行为: Both use file I/O operations (File, FileUtils).；Both handle exceptions with try-catch blocks.；Both use loops for processing data.
- 行为差异: A compresses a single file into a zip; B generates multiple class files and serialization data.；A is a utility method for log management; B is a code generator for adapters from Prolog.；A uses ZipOutputStream and CRC checks; B uses ClassWriter, Assembler, and ObjectOutputStream.
- 修正建议: Incorporate data-flow or control-flow analysis to distinguish program intent.；Use function names and documentation as additional signals.；Train with contrastive examples that have similar surface forms but different semantics.

### case_id=3608 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a property file by reading it line by line, replacing or appending a key-value pair, and optionally copying a default English file if the target file does not exist.
- B 摘要: Copies a file from source to destination using NIO FileChannel.
- 静态失败原因: Low token Jaccard similarity (0.1146) indicates little lexical overlap. The functions have different method signatures, different libraries (java.io vs java.nio), and different overall logic. Static BERT models often rely on token-level patterns and may miss semantic similarity that spans different APIs or high-level tasks.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered the file copy operation as a shared functionality, even though it is a minor part of function A, and accepted it as a Type-4 clone (partial functionality).
- 共享行为: Both involve copying content from one file to another.
- 行为差异: Function A performs character-level copy and modifies property entries; Function B performs binary copy with no modification.；Function A handles conditional creation of the destination file via copy; Function B always creates the destination file if not existing.
- 修正建议: Use data augmentation that highlights partial functionality.；Incorporate semantic role labeling or task decomposition.；Consider using methods that capture control-flow and data-flow similarities even when lexically different.

### case_id=3609 FN boilerplate_overlap

- 方法: `decodeFileToFile` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Decodes a Base64-encoded input file and writes the decoded output to a file.
- B 摘要: Copies a default properties file if missing, then reads a locale-specific properties file, modifies a key-value pair, and writes back.
- 静态失败原因: Static models like CodeBERT rely on token overlap and method names; the low Jaccard similarity (0.204) and different names likely caused a non-clone prediction. The model may also focus on high-level semantics (decoding vs. property editing) rather than the shared low-level I/O pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones because both functions contain a core file I/O loop (reading and writing bytes/characters) with identical resource management patterns. The additional transformation logic (Base64 decoding vs. property editing) is treated as secondary, making it a Type-4 semantic clone.
- 共享行为: Both involve reading from an input stream and writing to an output stream in a loop；Both use try-catch-finally for resource management；Both close streams in finally blocks；Both handle IOException by printing stack trace
- 行为差异: Function A decodes Base64; Function B manipulates property file entries；Function B has conditional file copy and line-by-line parsing；Function B appends new key-value if not found; Function A simply copies decoded bytes
- 修正建议: Train models to recognize common I/O patterns as clone candidates；Use dataflow analysis to separate core logic from boilerplate；Incorporate contrastive learning on pairs with shared I/O but different transformations

### case_id=3610 FN partial_functionality

- 方法: `createFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies the contents of a source file to a resource identified by a filename, closing streams and logging errors.
- B 摘要: Launches a NexOpen project by validating configuration, processing pom.xml files, setting Hibernate dialect, and scheduling an install action.
- 静态失败原因: The static BERT/GraphCodeBERT model likely focused on the low token Jaccard similarity (0.0667) and different method names, missing the shared IOUtils.copy usage and treating them as entirely different. It may have been too strict on lexical and structural similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both methods as file I/O operations that use IOUtils.copy, thus as a broad Type-4 clone with partial functionality similarity (copying data from input to output).
- 共享行为: Both use IOUtils.copy to copy data from an input stream to an output stream
- 行为差异: A is a simple file copy; B is a complex Eclipse launch involving multiple steps；A operates on FileInputStream and a resource manager's OutputStream; B operates on Eclipse resources, XML files, and configuration；A only catches ResourceManagerException; B catches CoreException and IOException；A has no conditions or callbacks; B has multiple checks, callbacks, and property setting
- 修正建议: Incorporate API usage pattern detection (e.g., IOUtils.copy) as a feature；Use program slicing to isolate common functional fragments；Train on examples with broad Type-3/Type-4 clones that have low token overlap but similar API calls

### case_id=3611 FN partial_functionality

- 方法: `run` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads URL content, parses first two lines as version and URL, accumulates rest, handles errors with custom messages, and notifies listeners.
- B 摘要: Opens a hardcoded URL, reads all content into a string buffer, and logs the result, throwing exceptions on error.
- 静态失败原因: Low token overlap and different control flow (try-catch-finally vs simple try) misled the model to ignore the shared URL reading behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often accepts broad Type-3/4 clones where the core functionality (reading from a URL) matches, ignoring differences in error handling, parsing, and side effects.
- 共享行为: Both open a URL connection and read lines using BufferedReader
- 行为差异: A parses lines with a switch; B appends all lines indiscriminately；A has detailed error handling with custom messages; B throws Exception；A notifies listeners in finally; B logs the result；A uses a dynamic URL (urlInfo); B uses a hardcoded URL
- 修正建议: Enhance model to recognize data flow patterns (e.g., URL.openStream() -> BufferedReader)；Include abstract representations of I/O operations and exception handling；Use graph-based models to capture control and data flow similarities

### case_id=3612 FP lexical_or_api_overlap

- 方法: `copyFile` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Parses string tokens and a file to populate sets and mappings for Tibetan transliteration.
- 静态失败原因: The model may have been misled by overlapping keywords like 'IOException', 'try', 'catch', 'file', or common API usage, despite very low token Jaccard similarity. The long and complex nature of function B could cause the model to lose track of overall semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically annotates strong structural or behavioral clones; these functions have entirely different purposes and implementations, so they are non-clones.
- 共享行为: Both use try-catch exception handling；Both involve I/O operations (file read/write)
- 行为差异: copyFile copies file contents; readData parses configuration strings and files into data structures；copyFile uses FileChannel and FileInputStream/OutputStream; readData uses StringTokenizer and BufferedReader；copyFile has simple copy logic; readData has complex token processing and multiple set population；Different input/output: copyFile takes source and dest files; readData operates on static string fields and modifies internal sets
- 修正建议: Incorporate data flow analysis to differentiate file copy vs. token parsing；Use graph-based models that capture control flow and data dependencies；Improve handling of long functions by chunking or hierarchical encoding

### case_id=3613 FP lexical_or_api_overlap

- 方法: `readScalarpvviewerDocument` vs `getNetworkServersIPs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads an XML configuration file from a URL and updates UI components with parsed data.
- B 摘要: Reads a network server list from a text file at a URL and returns a vector of IP addresses.
- 静态失败原因: The model likely overemphasized lexical overlap (URL, BufferedReader, readLine, try-catch) and the while-loop structure, ignoring the distinct parsing and output logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these non-clones because their semantic purpose and functional behavior are entirely different, despite sharing boilerplate I/O patterns.
- 共享行为: Both open a URL connection and read lines using BufferedReader；Both handle IOExceptions with try-catch
- 行为差异: Different parsing logic: XML vs. custom text format；Different outputs: updates UI vs. returns vector of IPs；Different control flow: A has multiple nested conditions and loops, B is simpler
- 修正建议: Incorporate method-level context (method name, class) to disambiguate purpose；Use dataflow analysis to capture different variable transformations；Train on more diverse negative pairs with similar boilerplate but different semantics

### case_id=3614 FP boilerplate_overlap

- 方法: `decodeFileToFile` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Decodes a Base64-encoded file and writes decoded content to an output file, returning success status.
- B 摘要: Main method for a Prolog adapter generator that reads a Prolog file, parses it, generates adapter classes, and packages them into a JAR file.
- 静态失败原因: Static BERT may have been misled by high lexical overlap of common I/O terms like 'file', 'InputStream', 'OutputStream', 'IOException', and similar boilerplate try-catch-finally structure, ignoring the vastly different core logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have entirely different purposes and logic; one is a simple file decoding utility, the other is a complex code generation tool. No Type-3 or Type-4 similarity exists even with broad interpretation.
- 共享行为: Both perform file I/O (reading from a file and writing to another).；Both use try-catch blocks to handle IOException.；Both close streams in finally blocks.；Both utilize byte arrays or buffer for reading/writing.
- 行为差异: Function A is a simple Base64 decode and byte copy, while B is a complex multi-step code generation process.；A returns a boolean, B returns void and has command-line argument handling.；A uses Base64 decoding, B uses Prolog parsing and class generation libraries.；B involves many domain-specific objects (Parser, Visitor, ClassWriter, etc.) not present in A.
- 修正建议: Incorporate dataflow analysis to capture actual operations beyond boilerplate.；Use structure-based AST matching or graph-based representations to differentiate simple I/O from complex logic.；Train with more diverse negative examples that share I/O boilerplate but have different semantics.

### case_id=3615 FN partial_functionality

- 方法: `createTempFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Creates a temporary file by copying a classpath resource to it.
- B 摘要: Builds an HTML site for editing by processing XML transformations and writing output files for each page.
- 静态失败原因: Static BERT models rely on token overlap and structural similarity; the low token Jaccard (0.05) and vastly different code structure led to a non-clone prediction, missing the potential Type-4 semantic similarity that BCB might have annotated.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones under a broad 'file copy' category because both methods involve reading from an input stream and writing to a file, despite the significant difference in complexity and purpose.
- 共享行为: Both methods involve reading from an input stream and writing to an output file.
- 行为差异: Function A is a simple utility; Function B is a large, complex method with XML processing, loops, and multiple file operations.；Function A handles a single resource; Function B processes multiple pages and configuration parameters.；Function A does not involve string transformations or debugging; Function B does.
- 修正建议: Increase sensitivity to semantic similarity by incorporating data flow or program dependency analysis.；Use larger context windows to capture high-level behavior patterns.

### case_id=3616 FN partial_functionality

- 方法: `doVersionCheck` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs a version check by reading version numbers from a remote file and calling another method.
- B 摘要: Performs an HTTP request to an OPDS catalog, downloads book data or catalogs, handling pagination and errors.
- 静态失败原因: The low token Jaccard (0.108) and different method names plus divergent logic likely caused the static BERT model to miss the underlying semantic similarity, as it focuses on lexical and structural patterns which are dissimilar.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a clone due to both methods involving network I/O, reading from URLs, and line-by-line parsing, which fits broad Type-4 semantic similarity.
- 共享行为: Both open a URL connection and read from an input stream；Both parse lines from a remote text resource；Both handle IOExceptions and network errors
- 行为差异: A does a simple version extraction; B does complex catalog parsing and book download；A has a fixed URL property; B deals with multiple URLs and pagination；A shows/hides a wait cursor; B manages progress callbacks and engine lifecycle
- 修正建议: Train models to recognize high-level semantic patterns like 'network read and parse'；Incorporate structural abstractions (e.g., common API usage patterns) into the representation

### case_id=3617 FN partial_functionality

- 方法: `runInternal` vs `retrieveQ`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: An internal method that downloads an OPDS catalog or a book from a URL, handling redirects, progress, errors, and pagination.
- B 摘要: A static method that retrieves the entire content of a URL as a string.
- 静态失败原因: Low token overlap (Jaccard 0.11) and large structural differences cause static BERT models to miss the semantic partial overlap, as they rely on surface-level similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels them as clones because the core functionality of fetching data from a URL is present in both, and B's behavior is a subset of A's, which qualifies as a partial or Type-4 clone.
- 共享行为: Both open a URL connection and read input data from the URL.
- 行为差异: A includes progress reporting, error handling, redirect following, content-type checking, and supports paginated OPDS feeds; B does not handle any of these and simply returns the raw content.
- 修正建议: Increase training data with partial clones；Use data-flow or graph-based models to capture functional similarities；Incorporate side-effect aware embeddings

### case_id=3618 FP lexical_or_api_overlap

- 方法: `main` vs `cpFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter classes from a Prolog file by parsing and writing Java bytecode.
- B 摘要: Copies a source file to a target file with optional replacement and naming conflict resolution.
- 静态失败原因: The model likely over-relied on surface-level cues like common API usage (File, IOException, InputStream) and error handling patterns, ignoring the vast semantic difference in overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions are semantically unrelated despite both being Java utility methods; BCB annotations focus on functional similarity, not generic API usage.
- 共享行为: Both perform file I/O operations
- 行为差异: Function A is a complex code generator; Function B is a simple file copier；Function A involves parsing, class loading, and bytecode writing; Function B only reads and writes bytes；Function A has extensive error handling for parsing and generation; Function B has basic file existence checks
- 修正建议: Include more diverse non-clone pairs with similar lexical tokens but different semantics；Use data-flow or control-flow analysis to capture operational differences；Enhance model with task-specific objectives like program synthesis or reasoning

### case_id=3619 FN partial_functionality

- 方法: `gerarTutorialPage` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Generates a tutorial website by creating directories, copying CSS files, and writing HTML pages.
- B 摘要: Builds a website for editing using XML transformation, file reading, and string replacement with multiple configuration parameters.
- 静态失败原因: Static BERT models rely on token overlap and structural similarity; the Jaccard similarity is very low (0.065) and method signatures differ, causing the model to miss the semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers functions as clones if they share the same high-level purpose (site generation), even if implementations differ significantly, as in Type-4 semantic clones.
- 共享行为: Both functions generate a website from resources
- 行为差异: Function A uses simple file copying and HTML writing, while B uses XML/XSLT transformation；Function A returns boolean, B is void and throws exceptions；B has complex parameter list and uses external libraries like Gadgets
- 修正建议: Use contrastive learning with semantic labels；Incorporate code summarization or documentation embeddings；Leverage AST-based matching for control flow patterns

### case_id=3620 FP boilerplate_overlap

- 方法: `sendPost` vs `getWebByUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.99`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string, with basic error reporting.
- B 摘要: Downloads a web page via HTTP GET, saves it to a file, optionally recursively extracts URLs, and logs progress.
- 静态失败原因: The model likely over-relied on the lexical and API overlap (URL, URLConnection, BufferedReader, PrintWriter, try-catch) and the similar structure of reading lines, without distinguishing the fundamental differences in HTTP method, return type, and additional I/O operations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers the overall functionality: a simple POST client vs. a web crawler with persistence; despite similar HTTP reading patterns, they are semantically different tasks, so BCB would not label them as clones.
- 共享行为: Open an HTTP connection；Set doOutput to true；Read response line by line；Handle exceptions with error printing
- 行为差异: A uses POST method; B uses GET method；A returns the response string; B saves response to a file and does not return；B includes logging, recursive URL extraction, and file writing; A does not；A sets a custom Accept-Language header; B does not
- 修正建议: Incorporate flow-sensitive data dependencies to distinguish POST body from GET response；Consider method signature (return type, parameters) as a strong signal；Use type-aware analysis to separate different I/O patterns；Train on more diverse examples to reduce sensitivity to common boilerplate

### case_id=3621 FP lexical_or_api_overlap

- 方法: `readUNI` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads tab-separated data from a URL and populates a vector with id and description strings.
- B 摘要: Sends an HTTP POST request with parameters and returns the response string.
- 静态失败原因: The static model likely overemphasized structural similarities (URL, InputStream, try-catch-finally) and ignored differences in HTTP method, data parsing, and return type, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functional similarity; these methods have distinct purposes (data retrieval vs. data submission) despite structural overlap, so BCB would label as non-clone.
- 共享行为: Both open URL connections and read from InputStream.；Both handle exceptions and clean up resources in finally blocks.
- 行为差异: Different HTTP method: none (GET-like) vs POST.；A parses tab-separated lines; B reads raw response lines.；A has void return; B returns response string.；B configures connection for output and writes parameters.
- 修正建议: Include method signature and return type as features.；Use control flow and data flow analysis to differentiate operations.；Train on finer-grained functional distinctions.

### case_id=3622 FN partial_functionality

- 方法: `httpRequestByPOST` vs `load`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs an HTTP POST request with parameters, reads response line by line, returns the response string, sets error fields on failure.
- B 摘要: Performs an HTTP GET request to Pastebin, reads response line by line, returns the XML string, shows a dialog on error.
- 静态失败原因: Static BERT models like CodeBERT rely on lexical and token-level similarity; low token Jaccard and different API names (HttpClient vs URL) lead to low similarity scores, missing the high-level semantic similarity of downloading content from a URL.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both are functionally similar as 'HTTP request to retrieve a string from a URL', ignoring minor differences in library usage, error handling, and HTTP method.
- 共享行为: Both execute HTTP requests to retrieve remote content；Both read the response line by line and concatenate into a string；Both return the response content as a string
- 行为差异: HTTP method: POST vs GET；Error handling: field setting vs GUI dialog；Parameter passing: form entity vs URL query；Input validation: B checks id length, A does not
- 修正建议: Augment training data with pairs that share high-level intent but differ in API usage；Use dataflow or control flow representations to capture common patterns like HTTP request-response reading；Incorporate contrastive learning with keyword-based similarity for common operations

### case_id=3623 FP boilerplate_overlap

- 方法: `main` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Decompresses a .gz file to its original file using GZIPInputStream and FileOutputStream.
- B 摘要: Handles user actions in a settings dialog to update preferences for GRAPHVIZ, IMAGEMAGICK, and other settings.
- 静态失败原因: The static model likely over-relied on lexical overlaps like 'File', 'IOException', and common programming patterns (try-catch, variable assignments) without capturing the overall intent. The low token Jaccard suggests the model may have been misled by boilerplate code.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they have completely different functionality and no semantic similarity beyond basic Java constructs.
- 共享行为: Both use try-catch-finally blocks for exception handling；Both perform some form of file I/O (one decompression, one file chooser)
- 行为差异: Function A is a standalone command-line utility; function B is a GUI event handler；Function A performs one specific task (decompression); function B has multiple conditional branches for different settings；Function A has no GUI interaction; function B updates UI components and stores preferences
- 修正建议: Incorporate control-flow and data-flow analysis to understand high-level behavior；Use larger context, such as surrounding method calls and class structure, to infer purpose；Train on more diverse examples to reduce reliance on token-level similarities

### case_id=3624 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFileChannel`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request for a portal page, including authentication, page retrieval, caching, and logging.
- B 摘要: Copies a file from source to destination using NIO FileChannel, optionally preserving modification time.
- 静态失败原因: Static BERT/GraphCodeBERT likely correctly predicted non-clone because the tokens and API calls are completely different; thus, it did not fail but rather the BCB label may be erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to broad interpretation of 'file processing' or a possible annotation error; the token Jaccard is very low (0.069), suggesting low similarity.
- 共享行为: Both involve file I/O operations (one writes cache files, the other copies files).
- 行为差异: Function A is a servlet method handling web requests; B is a static utility for file copying.；A involves complex logic for user authentication, page lookup, and caching; B is straightforward file copy.；A depends on HTTP request/response objects; B works directly with files.
- 修正建议: Re-evaluate BCB annotation for this pair; consider removing or correcting the label.

### case_id=3625 FP long_range_semantics

- 方法: `actionPerformed` vs `convert`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles GUI action events by selecting file paths for tools and updating UI preferences.
- B 摘要: Converts an ACRNEMA stream file to DICOM format by parsing and writing pixel data.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by superficial common API calls (e.g., File, InputStream, try-finally) and ignored the overall semantic context, which is common when models rely on token overlap and fail to capture long-range semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled this as non-clone because the two functions have completely different functionality, domain, and structure, with no meaningful partial similarity.
- 行为差异: Function A is a GUI event handler for setting tool paths and preferences; Function B is a file format converter.；Function A uses JFileChooser and updates UI components; Function B uses file I/O streams and DICOM parsing.；Function A interacts with Suku.kontroller preferences and UI elements; Function B checks DICOM tags and writes pixel data.；Function A has multiple conditional branches for different commands; Function B has sequential logic for conversion.
- 修正建议: Improve training with hard negative examples that have high lexical overlap but different semantics.；Incorporate structural information like control flow or data flow graphs.；Use models with better long-range dependency capture, such as transformer architectures with larger context windows.

### case_id=3626 FN partial_functionality

- 方法: `main` vs `sendErrorMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its contents to disk using ZipInputStream.
- B 摘要: Creates a zip file from a log file and sends it as an error message via email using ZipOutputStream.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the overlapping zip-API tokens (ZipInputStream/OutputStream, buffers, entry loop) and missed the contrasting contexts (URL vs email, extraction vs compression).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have overgeneralized 'zip file manipulation' as sufficient functional similarity, ignoring the opposite directions (decompress vs compress) and differing final purposes.
- 共享行为: Both use zip I/O streams (ZipInputStream/OutputStream) and buffer read/write loops.
- 行为差异: A reads from a network URL and extracts existing zip entries; B creates a new zip file from a local log file and emails it.；A outputs extracted files; B sends an email with the zip attachment.；A uses ZipInputStream; B uses ZipOutputStream.
- 修正建议: Incorporate method names and surrounding class context to distinguish purposes.；Use dataflow analysis to differentiate read vs write operations.

### case_id=3627 FN partial_functionality

- 方法: `getFile` vs `testReadHelloWorldTxt`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint attribute, saves to a temp directory, and returns the file path.
- B 摘要: Reads a resource file from classpath, copies it to a test directory, and performs assertions to test a content resolver's retrieval.
- 静态失败原因: The model likely relied on lexical and structural similarity, which is very low (0.05 Jaccard), and could not infer the broad functional overlap that BCB might accept.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as performing file I/O operations (reading from a source and writing to a file), thus categorizing as Type-4 (partial functionality similarity) despite different purposes.
- 共享行为: Both copy data from an input stream to a file on the filesystem.
- 行为差异: Function A downloads from a URL and parses/modifies XML, Function B reads from classpath and does not modify content.；Function A returns a file path, Function B performs assertions on content.；Function A handles multiple specific exceptions, Function B throws generic Exception.
- 修正建议: Better align model training with BCB's annotation guidelines for Type-3/Type-4 clones.；Use functional similarity measures that capture high-level I/O patterns.

### case_id=3628 FP lexical_or_api_overlap

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Initializes multiple character sets (topSet, leftSet, etc.) from tokenized strings and reads a configuration file to populate mappings and sets.
- B 摘要: Copies a file from source to destination using a buffer, with optional force overwrite.
- 静态失败原因: The model likely overfitted to some overlapping API calls (e.g., 'IOException', 'HashSet', 'StringTokenizer') or was misled by the presence of file I/O in both, ignoring the vast difference in overall logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clones because they perform entirely different tasks: one is initialization of character sets, the other is file copying. No shared functionality beyond generic I/O.
- 行为差异: Function A populates data structures from tokenized strings and a file; Function B copies binary data from one file to another.；Function A has complex conditional logic for parsing file lines; Function B uses a simple read-write loop.；Function A modifies many static sets and maps; Function B only writes to the output file.；Function A throws various custom errors; Function B throws IOException for file overwrite issues.
- 修正建议: Enhance training with more negative examples that have low semantic similarity despite overlapping APIs.；Use code structure or dataflow analysis to distinguish between different high-level tasks.；Increase model capacity to handle long-range dependencies and diverse control flows.

### case_id=3629 FN long_range_semantics

- 方法: `getResourceAsStream` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Returns an InputStream for a resource, fetching and caching remote content locally with HTTP conditional requests.
- B 摘要: Converts an ACRNEMA medical image file to DICOM format, adding UIDs and handling pixel data byte manipulation.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token-level patterns and data flow; the low token Jaccard (0.1348) indicates little lexical overlap, and the core logic (HTTP caching vs. DICOM parsing) differs vastly, leading the model to see no semantic equivalence. The miss likely stems from not capturing the broad structural similarity that BCB annotators considered indicative of a Type-4 clone.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label these as Type-4 clones because both perform high-level file I/O transformations (read, process, write) with similar structural patterns (nested try, stream handling, byte copying), despite completely different domain logic.
- 共享行为: Both read from an input source and write to an output destination using buffered streams.；Both contain loops that copy byte data from input to output.；Both include error handling with try-catch-finally blocks and close streams.
- 行为差异: Function A deals with HTTP URL caching and returns an InputStream; Function B parses DICOM tags and writes to a file with specific byte encoding.；Function A uses a cache hashtable and conditional HTTP requests; Function B adds UIDs and checks file format validity.；Function A handles multiple exceptions in catch blocks; Function B uses a finally block to close input and output resources.
- 修正建议: Enhance model with program-level semantics, e.g., using code summarization or intention classifiers.；Incorporate high-level API usage patterns (e.g., InputStream/OutputStream handling) into the representation.

### case_id=3630 FN partial_functionality

- 方法: `writeConfiguration` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Writes configuration resource to a given Writer by copying from URL stream.
- B 摘要: Downloads a WSDL file from a URL, modifies XML endpoint, and saves to temp directory.
- 静态失败原因: Static BERT likely focused on different method names, low token overlap, and distinct control flow structures, missing the underlying common pattern of URL reading and output.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'resource download and output' methods with partial functional similarity, which falls under Type-4 clone.
- 共享行为: Both open a URL stream and read data to output.
- 行为差异: A writes directly to a Writer; B saves to a file with XML manipulation and error handling.；A is concise with minimal error handling; B has complex file operations, logging, and multiple exception catches.
- 修正建议: Include dataflow analysis to capture input/output relations across methods.；Enhance representation to focus on core I/O operations and resource handling.

### case_id=3631 FP partial_functionality

- 方法: `getLinksFromURLFast` vs `PageLoader`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens a URL, reads the entire page, extracts all hyperlinks and their text using regex, and returns them as two vectors.
- B 摘要: Opens a URL, reads all lines of the page content, and concatenates them into a single string stored in a class field.
- 静态失败原因: The model likely over-emphasized the shared boilerplate code (URL opening, BufferedReader, while loop) and missed the distinct post-processing and return types that differentiate the functions.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels as non-clone when functions have different purposes and output, even if they share common sub-steps like URL opening and reading.
- 共享行为: Open a URL using java.net.URL；Read the content of the URL via BufferedReader
- 行为差异: Function A extracts links and returns them; Function B does not extract links.；Function A uses regex to parse HTML; Function B only concatenates lines.；Function A returns two Vectors; Function B sets a field and does not return a value.；Function A includes time check and debug output; Function B includes a ready() check.
- 修正建议: Incorporate dataflow analysis to track how input flows to output.；Use control-flow graph features to distinguish different branches and post-processing.；Include return type and method signature as explicit features.

### case_id=3632 FN benchmark_preference_bias

- 方法: `getFile` vs `decodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint address in the XML, and saves it to a temporary file, returning the file path.
- B 摘要: Decodes a Base64-encoded input file and writes the decoded bytes to an output file, returning a success boolean.
- 静态失败原因: The static model correctly predicted non-clone; the BCB label appears to be a false positive, so the model did not fail but rather matched our analysis.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'file processing' utilities, but the core functionality (network download + XML manipulation vs. Base64 decoding) is fundamentally different. The low token Jaccard suggests minimal overlap, making a clone label unlikely under strict BCB Type-3/4 criteria.
- 共享行为: Both perform file I/O operations using streams and buffers.；Both handle exceptions (IOException) during file operations.
- 行为差异: A downloads content from a remote URL; B reads a local file.；A modifies XML content (replacing an attribute); B performs Base64 decoding.；A returns the file path as a String; B returns a boolean success status.；A uses temporary files and renaming; B writes directly to the output file.
- 修正建议: Review the BCB annotation for this pair to confirm if it is a mislabel.；Ensure the model's training data does not include such borderline pairs as clones.

### case_id=3633 FN lexical_or_api_overlap

- 方法: `doGet` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests to fetch and render a portal page with caching and logging.
- B 摘要: Reads a DICOM image file and writes it to an output file after parsing.
- 静态失败原因: The token Jaccard similarity is extremely low (0.039), and the APIs and domain-specific terms are completely different. A static BERT/GraphCodeBERT model relies heavily on lexical overlap and may fail to capture the deep semantic mismatch.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have considered both as 'read and write' operations (one reads page data and writes HTML, the other reads DICOM data and writes to file), but this is overly broad and likely a labeling error.
- 行为差异: A deals with HTTP request/response, user permissions, and page caching; B deals with DICOM file format and pixel data.；A involves servlet context and portal objects; B involves image streams and DICOM parsing/writing.；A has complex control flow with multiple exception handlers; B has a straightforward linear flow.
- 修正建议: Incorporate cross-domain semantic embeddings or pre-training on diverse codebases.；Use graph-based representations that capture control/data flow without relying on surface tokens.；Apply contrastive learning to distinguish functionally different code with low lexical similarity.

### case_id=3634 FP partial_functionality

- 方法: `getLinksFromURLFast` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts hyperlinks and their text from a given URL using regular expressions and returns them as vectors.
- B 摘要: Constructs a GUI browser window that downloads a URL, optionally transforms XML with XSLT, and displays the resulting HTML.
- 静态失败原因: The static BERT model may have focused on the lexical and structural overlap of the URL opening pattern (URL, BufferedReader, InputStreamReader) while ignoring the vast differences in overall purpose, output, and control flow. It might have been misled by the partial API usage similarity despite the low token Jaccard.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions perform entirely different high-level tasks; the mere commonality of reading from a URL is insufficient for a clone label under BCB's preference for semantic or functional similarity.
- 共享行为: Both open a URL connection and read data from it using BufferedReader and InputStreamReader.
- 行为差异: Function A extracts links, function B constructs a GUI and displays content.；Function A returns vectors of links and texts, function B does not return a value (constructor).；Function B handles XML/XSLT transformation and GUI layout, which is absent in function A.
- 修正建议: Incorporate control flow and data flow analysis to distinguish different processing after URL reading.；Use models that consider the return type and overall method signature.；Leverage method name and surrounding context (e.g., class name, imports) to infer high-level purpose.

### case_id=3635 FN partial_functionality

- 方法: `copyResource` vs `unJar`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file by reading and writing byte by byte.
- B 摘要: Extracts a specific entry from a JAR file and writes it to a file after creating necessary directories.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token similarity and syntactic structure. The low token Jaccard (0.1129) and different APIs (URL, FileInputStream vs JarFile, IOUtils) likely caused the model to miss the semantic similarity. The model may also lack understanding of long-range dependencies and dataflow that connect the input reading and output writing.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels as Type-3/Type-4 clones if both functions perform the core operation of copying data from an input source to an output file, even if the specific APIs and source types differ. The shared concept of 'resource copying' is considered a clone.
- 共享行为: Both read data from a source (external resource) and write it to a file on disk.
- 行为差异: copyResource supports both URL and local file as input, while unJar only reads from a JAR file entry.；copyResource uses a simple byte-by-byte loop; unJar uses IOUtils.copy for efficient copying.；unJar creates necessary directories before writing; copyResource does not.；Error handling differs: copyResource throws an exception if resource not found; unJar prints stack trace and returns path.
- 修正建议: Enhance model with dataflow analysis to track data flow from input to output.；Include more diverse training examples of 'copy' operations across different APIs.；Use code summarization or functional role detection to identify high-level intent.

### case_id=3636 FN benchmark_preference_bias

- 方法: `fileCopy` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copy a file from source to destination with extensive error checking and buffer-based I/O.
- B 摘要: Build a website for editing by reading XML templates, transforming them, and writing output files.
- 静态失败原因: Static BERT likely correctly identified the low token overlap (Jaccard 0.1) and deep semantic differences, but may have failed to recognize any broad Type-4 similarity that BCB might have perceived; however, the functions are not actually similar, so the model's prediction is arguably correct.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions involving file reading and writing, but this is too superficial; the core functionality and logic are entirely different.
- 共享行为: Both perform file I/O operations (reading from and writing to files).
- 行为差异: Function A is a simple, self-contained file copy utility; Function B is a complex web site builder with multiple steps and dependencies.；Function A uses standard Java I/O streams; Function B uses custom FileSystem class and XML transformers.；Function A has no iteration; Function B iterates over pages and performs multiple file reads/writes per iteration.；Function A handles a single source-destination pair; Function B handles multiple input paths and writes multiple output files.
- 修正建议: Train models to distinguish between superficial I/O operations and actual program logic similarity.；Incorporate high-level functional semantics through code summarization or program analysis.

### case_id=3637 FN partial_functionality

- 方法: `main` vs `recurseFiles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a ZIP file from a URL and extracts its entries to disk.
- B 摘要: Recursively traverses a directory and adds non-ZIP files to a ZIP archive.
- 静态失败原因: Static BERT models rely on token and structural similarity; low Jaccard (0.13), different APIs (ZipInputStream vs ZipArchiveOutputStream), different control flow (loop vs recursion) lead to low embedding similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a Type-4 clone because both functions are in the zip manipulation domain, sharing similar stream handling and zip entry processing, despite inverse directions.
- 共享行为: Both handle ZipEntry objects；Both perform file I/O with streams；Both deal with zip file operations
- 行为差异: A extracts from zip; B creates zip；A uses ZipInputStream; B uses ZipArchiveOutputStream；A writes extracted files to disk; B writes files into archive；A has loop over entries; B uses recursion over file tree
- 修正建议: Incorporate domain knowledge of zip operations；Use dataflow or program slicing to capture I/O direction；Train on more diverse zip-related pairs

### case_id=3638 FN partial_functionality

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a hardcoded URL, unzips it, and writes each entry to the local filesystem.
- B 摘要: Copies a source file to a destination file using buffered streams, with error handling for file not found and IO exceptions.
- 静态失败原因: The static BERT model likely relied on syntactic and lexical features (e.g., token Jaccard similarity of 0.205) and method name differences ('main' vs. 'copyFile'), which made the functions appear unrelated. It failed to recognize the shared underlying stream copy logic, which is a dataflow pattern not easily captured by static embeddings alone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both implement the core pattern of copying bytes from an input stream to an output stream, a common Type-3/Type-4 clone in BigCloneBench. The additional complexity in A (URL, zip) is seen as peripheral to the fundamental IO loop.
- 共享行为: Both read bytes from an InputStream into a buffer and write to an OutputStream.；Both use a while loop to read until end of stream.；Both close the streams after use.
- 行为差异: Function A opens a URL connection and uses ZipInputStream to extract entries; Function B simply copies a single file.；Function A writes multiple output files (one per zip entry); Function B writes a single output.；Function A has no exception handling; Function B catches FileNotFoundException and IOException.；Function A uses a hardcoded URL; Function B takes source and destination files as parameters.
- 修正建议: Train with examples that emphasize shared dataflow patterns over surface-level syntax.；Incorporate dataflow analysis or graph representations like GraphCodeBERT to capture stream operations.；Augment training data with positive pairs that have low lexical but high structural similarity in IO operations.

### case_id=3639 FP boilerplate_overlap

- 方法: `saveUser` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Saves a User object by hashing its password with MD5, setting registration date, and merging the entity.
- B 摘要: Processes an HTTP request to perform a classification action by validating session, handling form parameters, sending XML data, parsing response, and forwarding to success/failure page.
- 静态失败原因: The static BERT model likely focused on local patterns like try-catch blocks, exception wrapping (NestedException vs. logging), and some common API usage (e.g., getBytes, URL), but failed to understand the global context and purpose. The token Jaccard similarity is low, but the model may have overfit to boilerplate or error-handling structures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have no semantic overlap; they perform entirely different tasks with no shared core functionality, even under broad Type-4 definition.
- 共享行为: Both functions use try-catch blocks for exception handling.
- 行为差异: Function A performs password hashing and database persistence, while Function B handles HTTP request processing and XML-based classification.；Function A inputs a User object, Function B inputs ActionMapping, ActionForm, HttpServletRequest, HttpServletResponse.；Function A outputs a User, Function B outputs an ActionForward.；Function A has a single responsibility; Function B has multiple steps including session checking, parameter extraction, HTTP communication, and result building.
- 修正建议: Incorporate dataflow analysis to track data transformations and dependencies.；Use graph-based models that capture control flow and call graphs.；Include contrastive learning to penalize false positives from common exception handling patterns.；Augment training with examples that have similar boilerplate but different semantics.

### case_id=3640 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a new version of jEdit by fetching a version file and comparing build numbers, with error handling and UI feedback.
- B 摘要: Downloads a file from a URL to a temporary file with optional authentication and progress display.
- 静态失败原因: The static model overemphasized the structural similarity in API usage (URL, BufferedReader, readLine loop) and UI updates, ignoring the distinct functional intent and data transformations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the high-level purpose differs fundamentally (version check vs file download), despite sharing low-level I/O patterns.
- 共享行为: Both open a URL connection and read lines from an InputStream using BufferedReader
- 行为差异: A parses version/build fields and compares with local data; B writes all content to a file；A uses error handling with GUI messages; B throws IOException and prints to stdout；B includes authentication and progress label update; A does not
- 修正建议: Incorporate dataflow analysis to track how read data is processed；Use contrastive learning that penalizes matches on generic I/O patterns without functional equivalence；Add negative examples with similar API usage but different tasks during training

### case_id=3641 FP boilerplate_overlap

- 方法: `getUniqueKey` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates a unique key by MD5 hashing the current time, local host, and random number.
- B 摘要: Handles HTTP request to perform a concept classification workflow, involving session checks, parameter parsing, XML building, HTTP POST, and response parsing.
- 静态失败原因: The model likely overfitted to common Java patterns like try-catch, MD5 usage, and method calls, ignoring the higher-level semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely consider these non-clones because they perform completely different tasks with no functional overlap beyond trivial Java boilerplate.
- 共享行为: Both use try-catch for exception handling；Both involve string manipulation and method calls
- 行为差异: Function A generates a deterministic key; Function B handles web request/response flow；Function A has no side effects; Function B modifies session and returns ActionForward；Function A is static utility; Function B is Struts action method
- 修正建议: Train model to focus on functional behavior rather than syntactic patterns；Include more context-aware embeddings that capture purpose；Add code summarization or task-specific classification layers

### case_id=3642 FN benchmark_preference_bias

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.05`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Builds a website for editing by reading XML templates and generating HTML pages with string replacements.
- 静态失败原因: Static model correctly predicted non-clone due to low token overlap and clear difference in functionality and complexity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone because both methods contain file reading/writing operations (FileInputStream, FileOutputStream), possibly considering them as Type-4 functionally similar file processing tasks.
- 共享行为: Both perform file I/O operations
- 行为差异: copyFile is a simple file copy; buildSiteForEdit is complex page generation；copyFile uses FileChannel; buildSiteForEdit uses character buffers and file writing；buildSiteForEdit involves XML transformation and many parameters; copyFile has no such logic
- 修正建议: Verify BCB annotation quality; consider excluding false clones from benchmark；Use richer semantic features to capture method intent beyond surface API usage

### case_id=3643 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFromFileToFileUsingNIO`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to display a portal page, with access control, logging, and optional caching to file.
- B 摘要: Copies a file using NIO FileChannel from source to destination.
- 静态失败原因: The model correctly predicted non-clone; the BCB label is likely a benchmark error or due to an overly permissive semantic matching rule.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled as clone due to both functions involving file I/O (writing to file in A, copying file in B), but this is extremely weak and the dominant functionalities are unrelated.
- 行为差异: A is a servlet doGet method handling HTTP request/response; B is a static file copy utility.；A involves page lookup, user permissions, logging, and rendering; B performs simple I/O transfer.；A writes to file only as a caching step; B's entire purpose is file copy.
- 修正建议: Review BCB annotation guidelines to ensure such pairs are labeled non-clone.；Improve benchmark consistency by removing or re-evaluating weak semantic matches.

### case_id=3644 FN benchmark_preference_bias

- 方法: `doUpload` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP file uploads: processes multipart requests, creates temporary directories, extracts parameters, and writes responses.
- B 摘要: Builds a website page for editing: reads XML, applies XSLT transformations, and writes output files with post-processing.
- 静态失败原因: The static model correctly predicted non-clone due to low token overlap (Jaccard=0.103) and different surface-level APIs, but BCB's annotation considered them clones based on broader functional similarity or annotation bias.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered them clones due to overlapping operational patterns (file handling, logging, exception handling) and possibly similar code in the truncated parts, reflecting a lenient annotation policy for broad Type-3/Type-4 similarity.
- 共享行为: Both use logging (LOG.info/debug, DebugFile.writeln).；Both perform file I/O operations (create directories, read/write files).；Both handle exceptions with try-catch blocks.；Both use string manipulation and conditionals.
- 行为差异: Different domain: HTTP servlet vs. static site generation.；Different input/output: HTTP request/response vs. file paths and XML.；Different libraries: servlet API vs. XSLT/XML.；Different overall goal: upload resources vs. generate HTML pages.
- 修正建议: Improve handling of long-range semantics to distinguish different high-level purposes.；Use more representative training data that reduces reliance on superficial patterns.；Incorporate dataflow or dependency analysis to capture divergent behaviors.

### case_id=3645 FP lexical_or_api_overlap

- 方法: `sendPost` vs `read`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with given parameters and returns the response body as a string.
- B 摘要: Reads a UTF-8 encoded resource file, splits it into sections marked by '---', and stores them, throwing exceptions on errors.
- 静态失败原因: Static BERT or GraphCodeBERT may have focused on overlapping tokens like 'URL', 'BufferedReader', 'readLine', 'String', 'UTF-8', etc., and syntactic patterns like while loop reading lines. This lexical overlap and similar control flow (while readLine) could have misled the model into thinking they are clones, ignoring the larger context and semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled non-clone because despite both reading from a URL, the overall functionalities are different: one is network POST, the other is resource file parsing. BCB's Type-3/Type-4 require more congruent functionality.
- 共享行为: Both open a URL and read text using BufferedReader；Both use UTF-8 encoding；Both use readLine loop
- 行为差异: A writes to the URL output stream; B does not；A returns concatenated response; B builds a list of sections；A uses HttpURLConnection; B uses URL.openStream；A handles exceptions by showing message; B throws exceptions
- 修正建议: Improve model to consider the broader purpose and side effects (e.g., writing output vs. parsing sections)；Use structural information like method name or invocation patterns；Use dataflow analysis to see that the input/output types differ

### case_id=3646 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a new version of jEdit by reading a version check URL and showing a dialog if a newer version exists.
- B 摘要: Fetches and returns the first line of content from a given URL using HttpURLConnection.
- 静态失败原因: Static BERT models likely focused on overlapping API sequences (URL, BufferedReader, InputStreamReader) and ignored the differing control flow and purpose, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because their overall intent and output differ significantly; one is a UI-triggered version check, the other is a generic HTTP GET utility.
- 共享行为: Both create a URL and open an InputStream；Both use BufferedReader and InputStreamReader to read data
- 行为差异: Function A loops through multiple lines checking for .version and .build prefixes; Function B reads only the first line；Function A updates UI (shows wait cursor, messages); Function B returns a string and throws Exception；Function A compares build numbers; Function B simply returns the raw content
- 修正建议: Incorporate data flow analysis to distinguish side effects and return types；Use structural matching with awareness of loop vs single-line reads；Augment training with examples that have similar API usage but different semantics

### case_id=3647 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Validates a handshake packet and either shuts down the network or sends a login packet after authenticating with a session server.
- B 摘要: Reads lines from a URL, parses them into version/url/info fields, handles IO exceptions with custom messages, and notifies listeners.
- 静态失败原因: The static model likely focused on the lexical overlap of 'BufferedReader', 'InputStreamReader', 'URL', 'openStream', 'readLine', 'close', etc., and missed the overall control flow and purpose differences. It may have been misled by boilerplate code patterns common in network I/O.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the functions perform entirely different tasks (network handshake vs. generic URL reader) despite a superficial similarity in using URL reading API.
- 共享行为: Both use BufferedReader and InputStreamReader to read from a URL openStream.
- 行为差异: Different purpose: handshake vs. generic URL parsing.；A validates and conditionally shuts down or sends packets; B parses lines into fields and notifies listeners.；A handles NumberFormatException; B handles IOException and FileNotFoundException.；A's logic branches on username validation; B is a simple sequential read.
- 修正建议: Improve model to consider higher-level structure and context.；Use dataflow analysis to differentiate the variable usage (e.g., A uses mc.session, B uses urlInfo).；Add training examples that differentiate similar API usage with different semantics.

### case_id=3648 FN partial_functionality

- 方法: `writeFileType` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file of URIs, opens each URL, inspects first 100 lines for RDF/OWL keywords, and writes classification to output file.
- B 摘要: Performs HTTP POST request to a URL with parameters, reads response, and returns response string or null on error.
- 静态失败原因: The functions have low token overlap (Jaccard=0.14), different method names, and distinct overall logic (file processing vs. HTTP POST). Static BERT likely focused on surface tokens and missed the abstract similarity in network I/O and line-by-line reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as Type-4 (semantic) clones because both perform network I/O to read HTTP responses and process lines, ignoring the specific purpose (classification vs. retrieval) and output method (file vs. return).
- 共享行为: Both open URL connections and read response lines using BufferedReader.
- 行为差异: A reads multiple URLs from a file; B makes a single POST request.；A writes classification to file; B returns response string.；A inspects lines for specific keywords; B does not.；Different error handling: A writes BROKEN on exception; B sets error codes.
- 修正建议: Use graph-based code representations capturing data flow and I/O operations.；Include abstract syntax tree (AST) features to highlight structural patterns.；Train on pairs with similar I/O behavior even if different tasks.

### case_id=3649 FN lexical_or_api_overlap

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using InputStream/OutputStream.
- B 摘要: Copies a file to another file using NIO FileChannel transfer.
- 静态失败原因: The token Jaccard similarity is low (0.13), and the APIs differ (InputStream vs FileChannel), so the model likely saw them as different. Also the method names differ.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often considers functional similarity even if implementations differ; both achieve file copying, so they may be labeled as Type-4 clones.
- 共享行为: Both copy data from a source to a destination file；Both close streams/channels after copying
- 行为差异: copyResource supports reading from a URL or a file; copyFile only from a file；copyResource uses byte-by-byte reading; copyFile uses NIO channel transfer (more efficient)；copyResource throws generic Exception; copyFile throws IOException；copyResource reads from instance variable 'source' and writes to 'destinationFile()'; copyFile uses explicit parameters
- 修正建议: Improve semantic understanding by focusing on data-flow or high-level intent；Use more abstract representations capturing I/O operations；Include structural similarity ignoring detailed API differences

### case_id=3650 FN benchmark_preference_bias

- 方法: `doGet` vs `execute`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to retrieve and display a page based on a parameter, with visibility checks and logging.
- B 摘要: Converts a Java source file to HTML using given configuration, with file I/O and logging.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone, but this is a false negative relative to the likely incorrect BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label may be an annotation error, as there is no significant similarity in structure or functionality beyond generic I/O and logging.
- 共享行为: Both involve reading input and producing output；Both include logging statements
- 行为差异: Different domains (web servlet vs file conversion)；Different parameter types and return types；Different error handling and resource management
- 修正建议: Re-annotate this pair or remove from clone dataset；Improve dataset quality control to avoid such mismatches

### case_id=3651 FP lexical_or_api_overlap

- 方法: `main` vs `write`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses command line arguments, reads a Prolog file, generates adapters, and writes them to a JAR file.
- B 摘要: Method that writes a JAR output stream by merging entries from multiple JAR files, optionally resolving dependencies.
- 静态失败原因: Static BERT models may over-rely on token overlap (e.g., 'Jar', 'File', 'IOException') and common syntactic patterns (e.g., try-catch, loops) without capturing the high-level semantic difference. The presence of similar API calls and control flow could lead to a high similarity score despite different purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they perform entirely different tasks: one is a main method for adapter generation, the other is a JAR writing utility. Despite sharing some I/O patterns, the core functionality is unrelated.
- 共享行为: Both involve writing to JAR files；Both use Java I/O and JAR-related classes
- 行为差异: Function A is a complete program entry point with argument parsing and adapter generation logic; Function B is a utility method for merging JARs.；Function A reads a Prolog file and generates adapters; Function B merges existing JAR entries.；Function A includes multiple steps like parsing, visiting, looking up classes; Function B is a simpler loop over JAR entries.
- 修正建议: Improve model's ability to distinguish between shared utility patterns and core functionality；Incorporate task-specific context (e.g., method name, class hierarchy) to disambiguate；Use more robust semantic representation that captures intent beyond API usage

### case_id=3652 FN partial_functionality

- 方法: `fileDownload` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a given URL and saves it as download.pdf in the specified directory.
- B 摘要: Downloads and processes OPDS catalog feeds or eBooks from HTTP URLs, handling pagination, error recovery, and progress reporting.
- 静态失败原因: Low lexical overlap (token Jaccard 0.10) and different control flow structures; B has complex loops and conditionals that A lacks.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as download functions that retrieve data from a URL and store it locally, accepting broad functional similarity despite differences in complexity and additional features.
- 共享行为: Both open HTTP connections to URLs and read data streams from the network.
- 行为差异: A is a simple file download with fixed output filename; B includes HTTP header handling, redirects, content-type-based dispatch, pagination, and error handling.
- 修正建议: Use attention mechanisms or graph-based representations that capture long-range control flow and data dependencies.；Incorporate high-level intent via method names and comments.

### case_id=3653 FP lexical_or_api_overlap

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated token strings and a file to populate sets and hash maps for Tibetan/Sanskrit character sequences.
- B 摘要: Copies a file from source to destination using Java NIO FileChannel.
- 静态失败原因: The model likely relied on superficial lexical overlap such as 'IOException', 'File', 'try-catch', and general I/O patterns. The extremely long length of readData may have caused the model to miss its core logic, leading to a false positive based on API-level similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have entirely different purposes and implementations, even if both use I/O. The token-level and structural similarity is very low.
- 共享行为: Both involve file I/O (reading or writing).；Both catch IOException.
- 行为差异: readData parses token strings and reads a file line by line for complex data extraction; copyFile simply transfers bytes between channels.；readData populates multiple sets and hash maps; copyFile has no such data structure manipulation.；readData handles 13-column parsing and validation; copyFile checks for canonical path equality.；readData is extremely long and procedural; copyFile is short and straightforward.
- 修正建议: Improve context window or use hierarchical representations to capture long-range semantics.；Incorporate contrastive learning to distinguish similar API usage but different functionality.；Add structural similarity features like AST or control flow graph matching.；Increase training data with long-function pairs to better handle length.

### case_id=3654 FP lexical_or_api_overlap

- 方法: `init` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads controller classes from a configuration file into a servlet context.
- B 摘要: Reads tab-separated data from a URL and populates a vector of descriptions.
- 静态失败原因: The model likely over-fitted on lexical and API-level similarities (URL, openStream, while loop, try-catch) while ignoring the distinct core functionality and output types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as not clone because the functions have entirely different high-level purposes and output types, despite sharing some low-level I/O patterns.
- 共享行为: Both open a URL stream and read line by line.；Both use try-catch blocks for exception handling.
- 行为差异: Function A loads Java classes; Function B parses data into strings.；Different parsing logic: A reads class names and skips comments, B tab-delimits fields.；Different output: A adds Class objects, B adds concatenated id and description strings.；Different error handling: A handles IO and ClassNotFound separately, B catches MalformedURL and generic Exception.
- 修正建议: Incorporate function name or context to emphasize purpose.；Train on harder negatives that share API but differ in semantics.；Use contrastive learning with data flow analysis.

### case_id=3655 FP boilerplate_overlap

- 方法: `getJSONData` vs `getUser`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches JSON data from a given URL using HTTP and returns a JSONObject.
- B 摘要: Retrieves a User object by login from a database or a configuration file, parsing colon-separated fields.
- 静态失败原因: Static BERT models (e.g., GraphCodeBERT) may have been misled by the high lexical overlap in boilerplate code (e.g., BufferedReader, readLine, try-catch) and the similar control flow (reading lines, building a string). They may not capture the semantic difference in the purpose and the specific APIs used (e.g., DefaultHttpClient vs StringTokenizer). The token Jaccard similarity is 0.213, which is low, but the model likely focused on structural similarity of reading loops and exception handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels clones when functions perform the same task (e.g., both parse JSON or both authenticate users). Despite shared boilerplate, the core functionality differs significantly (network I/O vs file I/O, JSON vs tokenizer, different output types). Thus BCB considers them non-clones.
- 共享行为: Both read line by line from an input stream using BufferedReader；Both use try-catch to handle exceptions；Both return an object (or null) after processing
- 行为差异: Function A uses HTTP client to fetch data from a URL, while Function B reads from a local file or database；Function A parses the entire content as JSON, while Function B tokenizes lines with colon delimiter；Function A returns a JSONObject, Function B returns a User object；Function B includes a DAO layer for database operations, while A does not
- 修正建议: Train on more diverse examples that focus on distinguishing API-level differences beyond boilerplate；Incorporate type information (output type) and call dependencies (e.g., HTTP vs file) into the model；Use data flow analysis to capture that the source of the stream is different (URL vs file)

### case_id=3656 FP boilerplate_overlap

- 方法: `executePost` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response.
- B 摘要: Opens an HTTP GET connection to a fixed URL and reads the response without processing.
- 静态失败原因: The model likely over-relied on overlapping API usage tokens (URL, BufferedReader, InputStream) and failed to capture the semantic differences in HTTP method, parameter handling, and return value.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have different HTTP methods, different I/O handling, and different return types, indicating distinct intended functionality despite sharing HTTP boilerplate.
- 共享行为: Both create a URL object；Both open an input stream and read with BufferedReader；Both catch exceptions
- 行为差异: HTTP method: POST vs GET；A sends parameters, B does not；A returns response string, B is void；A writes output, B does not
- 修正建议: Incorporate method signatures (return type, parameters) to differentiate；Use control-flow analysis to distinguish POST vs GET logic；Explicitly model HTTP method and parameter emission

### case_id=3657 FP lexical_or_api_overlap

- 方法: `get` vs `readVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Makes an HTTP GET request with custom headers, reads response line by line, decodes GameRecord objects from non-comment lines, returns array or null.
- B 摘要: Reads a classpath resource file 'version', parses lines for version, revision, and date fields, sets instance variables, returns void.
- 静态失败原因: Static BERT models may over-rely on token-level overlap (BufferedReader, readLine, IOException, etc.) and miss the higher-level semantic differences in network vs. local I/O, different return types, and different logic after reading lines.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels as non-clone when functions have different purposes and outputs, even if they share common I/O boilerplate. The similarity in reading lines is not sufficient for Type-3/Type-4.
- 共享行为: Both read from an input stream line by line；Both use BufferedReader with InputStreamReader；Both handle IOException with printStackTrace；Both use conditional checks on line prefixes
- 行为差异: A performs network I/O via HTTP, B reads local resource file；A returns a GameRecord array, B sets instance fields and returns void；A filters lines not starting with '#', B parses lines starting with 'Version=', 'Revision=', 'Date='；A has different exception handling (returns null on failure), B has finally block to close reader
- 修正建议: Incorporate dataflow or flow-aware features；Add training examples that distinguish network I/O from local resource I/O；Use AST or control-flow features to capture different return types and output destinations

### case_id=3658 FP lexical_or_api_overlap

- 方法: `readAndRewrite` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads a DICOM image file and rewrites it to another file after processing pixel data.
- B 摘要: Parses tokenized configuration data from a file to populate various HashSets and maps for Tibetan transliteration.
- 静态失败原因: The model likely overfit to superficial features such as the method name containing 'read' or the presence of IOException/File operations, ignoring the completely different domain-specific APIs.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: None
- 共享行为: Both are private static void methods that perform I/O operations
- 行为差异: Code_a processes medical images using DICOM library; Code_b parses text configuration for transliteration；Code_a writes output file; Code_b populates data structures in memory；Code_a uses ImageInputStream/ImageOutputStream; Code_b uses StringTokenizer and file reading
- 修正建议: Improve contextual understanding of API calls and data flow；Add more training data with diverse I/O patterns to avoid false positives based on method name similarity

### case_id=3659 FN partial_functionality

- 方法: `fileDownload` vs `fetchUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads content from a URL and writes it to a file named 'download.pdf' in a specified directory.
- B 摘要: Fetches content from a URL and returns it as a String.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token-level and structural features; the low token Jaccard (0.21) and differences in method signatures and control flow (e.g., while loop vs. while reading lines, file writing vs. string building) likely caused the model to miss the underlying similarity in URL reading behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers these as clones because both perform the core task of fetching a URL and reading its content, which qualifies as Type-4 (functionally similar but not semantically equivalent).
- 共享行为: Both open a URL and establish a connection.；Both read from the input stream using BufferedReader.；Both handle exceptions related to URL processing.
- 行为差异: A writes the downloaded content to a file, while B returns it as a String.；A uses an InputStreamReader to read bytes as characters, B uses readLine() to read line by line.；A logs exceptions, B silently returns an empty string on failure.；A has a fixed output filename, B does not produce any file output.
- 修正建议: Train with more examples of Type-4 clones to recognize similar core functionality despite different output modalities.；Incorporate data flow analysis to capture shared data sources and sinks.；Use contrastive learning to emphasize functional similarity over lexical overlap.

### case_id=3660 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `callApiPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a specific Twitter timeline via HTTP GET and returns the response as a string.
- B 摘要: Sends an HTTP POST request with parameters to a given URL and returns the response as an InputStream.
- 静态失败原因: The model likely overemphasized shared tokens like 'Http', 'IOException', and 'connect', and the general boilerplate of HTTP request handling, without distinguishing between GET and POST or the specific logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the methods have different signatures, different HTTP methods, and different return types; they are not semantically similar beyond making an HTTP request.
- 共享行为: Both perform an HTTP request.；Both handle IOException.；Both use a URL connection or client.
- 行为差异: HTTP method: GET vs POST.；Target URL: hardcoded vs parameterized.；Return type: String vs InputStream.；Error handling: logging vs custom exception.
- 修正建议: Incorporate control flow and data flow to differentiate HTTP methods.；Train on more examples of different HTTP request patterns.；Use return type and method signature information.

### case_id=3661 FN partial_functionality

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Builds a site for editing by processing XML, transforming, and writing output files.
- 静态失败原因: Static models like BERT rely on token overlap (low Jaccard 0.07) and surface patterns, missing the high-level functional similarity in file I/O structure that BCB annotators might have considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled it a clone due to both involving file I/O with similar exception handling patterns, possibly considering it as Type-3 (near-miss) or Type-4 (functional) similarity based on core file transfer behavior.
- 共享行为: Both perform file I/O operations (reading and writing).；Both use FileInputStream and handle IOException.
- 行为差异: Function A is a simple file copy; Function B is a complex site generation process.；Function A has no XML processing, transformation, or string manipulation; Function B does.；Function A operates on a single file pair; Function B handles multiple pages and files.；Function A has a simple try-catch-finally; Function B has nested loops, conditionals, and multiple exception types.
- 修正建议: Incorporate dataflow analysis to capture I/O operations.；Use control-flow and dependency graphs to identify core file transfer patterns.；Train with more nuanced weak labels for partial functional similarity.

### case_id=3662 FN benchmark_preference_bias

- 方法: `main` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a hardcoded URL and extracts its zip entries to files.
- B 摘要: Reads a text file, applies text wrapping and title case filters, and writes to another file.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the low token overlap (0.219) and distinct API usage (ZipInputStream vs. BufferedReader) and control flow, correctly identifying the lack of semantic equivalence, but failed to match BCB's broader functional similarity criteria.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have annotated this as a clone due to both being main methods that perform file I/O operations with a read-process-write pattern, but the actual functionality differs significantly (zip extraction vs. text filtering).
- 共享行为: Both are public static void main methods；Both use Java I/O streams；Both read input and produce output
- 行为差异: A downloads from a URL and extracts zip; B reads from a local file and applies text filters；A uses ZipInputStream and FileOutputStream; B uses BufferedReader, Writer, and custom filters；A has fixed URL; B uses command line arguments for input and output files
- 修正建议: Improve training data by filtering out BCB false positive annotations like this；Incorporate more diverse negative examples to avoid overfitting to superficial boilerplate patterns；Use contrastive learning with more fine-grained functional labels

### case_id=3663 FN benchmark_preference_bias

- 方法: `writeFileType` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads URIs from a file, fetches each URL, detects presence of OWL/RDFS/RDF keywords in the first 100 lines, and writes classification to an output file.
- B 摘要: Performs an HTTP POST to a service endpoint with method invocation parameters, reads JSON response, and deserializes it to the expected return type, with retry on connection timeout.
- 静态失败原因: The static model correctly predicted non-clone due to low lexical overlap and distinct method names and logic; it likely captured the semantic difference via representation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered them clones due to superficial similarity in using URL connections, reading lines, and writing output, possibly as a broad Type-3 clone under 'network I/O operations'.
- 共享行为: Both use BufferedReader to read line by line；Both handle exceptions；Both involve network communication (URLConnection/HttpClient)；Both produce output based on input
- 行为差异: Different input: file vs method invocation；Different output: file write vs object return；Different logic: keyword detection vs JSON deserialization；Different error handling: write BROKEN vs retry
- 修正建议: Review BCB annotation for this pair; likely a mislabel.；If BCB label is correct, model should learn higher-level functional similarity, but current evidence suggests non-clone.

### case_id=3664 FP other

- 方法: `calculateProfileDiffDigest` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Computes MD5 digest of a profile diff string and returns Base64 encoded hash.
- B 摘要: Executes a Struts action performing concept classification, involving HTTP request handling, session management, XML parsing, and URL communication.
- 静态失败原因: Despite low token overlap (Jaccard 0.036), the model may have been misled by some common Java boilerplate (e.g., try-catch, string handling) or failed to capture the long-range semantics and diverse library usage.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels this as non-clone because the functions have no meaningful semantic similarity; they solve entirely different problems.
- 行为差异: Function A is a simple utility for hashing a string; function B is a complex web action with multiple steps.；Function A returns a String; function B returns an ActionForward.；Function A uses MessageDigest and BASE64Encoder; function B uses Struts, HTTP, XML, and custom beans.；No functional overlap in inputs, outputs, or operations.
- 修正建议: Improve context understanding for long and diverse methods.；Incorporate structural or dataflow analysis to differentiate utility functions from web actions.；Use contrastive learning on function-level semantics with diverse libraries.

### case_id=3665 FN partial_functionality

- 方法: `getHTML` vs `load`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads HTML from a specified URL with given encoding and optionally saves to a file.
- B 摘要: Downloads XML source from Pastebin based on an ID and returns it as a string.
- 静态失败原因: The low token Jaccard (0.23) and different method names and specific API calls (HttpURLConnection vs. URLConnection) caused the static BERT model to miss the semantic similarity. The model may focus on surface-level tokens and not capture the shared underlying operation of reading from a URL.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers this a clone because both functions implement the same high-level behavior: fetching content from a URL and returning it as a string. The differences in parameters, error handling, and URL construction are seen as non-essential variations.
- 共享行为: Both connect to a URL and read content line by line.；Both accumulate the read content into a string and return it.；Both use a BufferedReader to read from an input stream.
- 行为差异: A takes a full URL, encoding, and optional file path; B constructs a URL from an ID and has no file output.；A uses HttpURLConnection with a custom User-Agent header; B uses URL.openStream() directly.；A writes to a file if dirPath is provided; B does not.；B has a length check that returns empty string if id length < 5; A has no such check.
- 修正建议: Incorporate dataflow analysis to recognize that both functions perform an HTTP GET and read response.；Use API similarity embeddings to map HttpURLConnection to URLConnection.；Add training examples with varied APIs that achieve the same core functionality.

### case_id=3666 FP partial_functionality

- 方法: `sendPost` vs `postRequest`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with a raw string as the body.
- B 摘要: Sends an HTTP POST request with URL-encoded form data from a HashMap.
- 静态失败原因: The model likely focused on structural similarity and high token overlap (0.41) from common pattern of HTTP POST, missing the key differences in input parsing and URL encoding. Semantic similarity of method names may have biased the prediction.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: None
- 共享行为: Both perform HTTP POST requests.；Both set connection DoOutput and DoInput to true.；Both use PrintWriter to write data to the output stream.；Both read the response line by line using BufferedReader.
- 行为差异: A accepts a raw string as body; B accepts a HashMap and URL-encodes key-value pairs.；A sets Accept-Language header; B does not.；A uses HttpURLConnection; B uses URLConnection.；A explicitly sets charset UTF-8 for reading; B uses default charset.
- 修正建议: Incorporate data-flow analysis to track how input parameters are used.；Add training examples that distinguish between raw body and URL-encoded form data.；Encode structural differences in input processing more explicitly.

### case_id=3667 FP lexical_or_api_overlap

- 方法: `createJAR` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Creates a JAR file or directory, then serializes a document object and copies files around.
- B 摘要: Handles GUI action events by opening file choosers, storing preferences, and updating UI components.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by common Java idioms (try-catch, file operations) and similar structural patterns (if-else blocks, loops), leading to a false positive despite low token overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotation likely considered these as non-clones because they perform completely different tasks: one is a file creation utility, the other is a GUI event handler. Even under broad Type-4/partial similarity, there is no functional overlap beyond superficial use of File.
- 共享行为: Both involve the use of File objects and file paths；Both have try-catch blocks for exception handling
- 行为差异: A focuses on low-level file I/O with channels and serialization; B is a high-level event handler with user interaction via JFileChooser；A writes binary data and copies files; B reads user input and stores configuration preferences；A is deterministic and single-purpose; B is stateful and handles multiple distinct commands；A uses ObjectOutputStream; B uses Suku.kontroller.putPref and UI updates
- 修正建议: Incorporate dataflow or control-flow awareness to distinguish I/O operations from event handling；Use more fine-grained semantic role labeling for method calls and variable usage；Enhance training data with more diverse non-clone pairs involving similar surface forms but different intents

### case_id=3668 FN partial_functionality

- 方法: `extractResourceToFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts a resource from the classpath to a file using InputStream and FileOutputStream.
- B 摘要: Downloads a ZIP file from a URL and extracts its entries to files using ZipInputStream and FileOutputStream.
- 静态失败原因: Low token overlap, different method names, and structural differences (main vs. helper method) caused the static model to miss the semantic similarity of resource extraction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB's broad criteria often accept Type-4 clones where both functions share the high-level goal of extracting data from an input stream to a file, despite different sources or additional complexity.
- 共享行为: Both read from an input stream and write to a file output stream.；Both ensure streams are properly closed in finally blocks.
- 行为差异: A reads a single resource from classpath; B reads a remote ZIP file and processes multiple entries.；A uses FileUtils.openOutputStream; B uses direct FileOutputStream and BufferedOutputStream.；A does not handle ZIP nor buffering; B includes ZIP iteration and buffering.
- 修正建议: Train models to recognize common patterns of resource extraction abstractly.；Use data flow graphs or program dependency graphs to capture stream handling.；Consider extending training data with more diverse extraction patterns.

### case_id=3669 FN partial_functionality

- 方法: `scrapeForIsbns` vs `getEncoding`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Scrapes ISBN-10 numbers from a URL's HTML content, counting matches.
- B 摘要: Detects character encoding from HTTP headers or HTML content of a URL.
- 静态失败原因: Low token Jaccard (0.12381) indicates minimal lexical overlap; static BERT models rely on surface-level tokens and may miss the abstract structural pattern shared by both functions, treating them as entirely different tasks due to different method names and domain-specific words.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones due to common boilerplate (URL connection, BufferedReader, loop reading lines) and both performing data extraction from web pages, fitting Type-4 (functionally similar but different implementations) or broad Type-3 (structurally similar with minor differences).
- 共享行为: Both open a URL connection and read lines via BufferedReader.；Both iterate over lines and apply pattern matching (regex or string contains) to extract specific data.；Both involve error handling for I/O operations.
- 行为差异: A counts and stores ISBN matches; B returns an encoding string.；A uses a precompiled regex for ISBN-10; B uses string operations for charset.；A has retry logic on connection failure; B does not.；A does not explicitly close reader in finally; B does.
- 修正建议: Enhance training data with more diverse functional clones having low token overlap but similar control-flow patterns.；Incorporate data-flow or control-flow features to capture abstract behavior like 'open connection, read lines, extract patterns'.；Use contrastive learning to learn representations that group methods with similar I/O patterns.

### case_id=3670 FN dataflow_blindspot

- 方法: `doGet` vs `transformSingleFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.65`
- 推荐路线: `dynamic_equivalence_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles HTTP GET request to serve a web page, handling page lookup, user permissions, caching, and logging.
- B 摘要: Transforms an X3D file into a compressed .x3dv.gz file using GZIP compression with progress messages.
- 静态失败原因: GraphCodeBERT likely failed because it relied on data flow and structural patterns (like try-catch, file writing) that appear similar in abstract sense, but missed the domain-specific semantics and completely different functional purposes.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本可能是 API 写法不同但行为等价的漏报。建议测试目标为 input_output_equivalence。
- BCB 偏好解释: BCB may have labeled these as clones due to both involving file I/O and exception handling patterns, reflecting a broad Type-3/Type-4 similarity under partial functionality overlap.
- 共享行为: Both write output to a file/stream；Both include exception handling and logging；Both use file I/O operations
- 行为差异: Different input types: HTTP request vs X3D editor object；Different output types: HTML response vs compressed file；Different domains: web portal vs 3D graphics；Different processing logic: page generation vs file compression
- 修正建议: Improve model to capture domain-specific context (e.g., servlet vs 3D graphics)；Enhance training data with more diverse clones to avoid overgeneralizing file I/O patterns；Use fine-grained semantic analysis of method-level purposes beyond structural similarity

### case_id=3671 FP boilerplate_overlap

- 方法: `postData` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with data to a given URL and discards the response.
- B 摘要: Retrieves open tickets for a queue from a RequestTracker system via HTTP GET and returns a list of tickets.
- 静态失败原因: The model may have overemphasized overlapping API tokens (BufferedReader, InputStreamReader, URL) and general HTTP boilerplate, while overlooking the significant differences in control flow, HTTP method, data usage, and return type.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have distinct purposes and input/output specifications; one is a generic post utility, the other is a specific get query for a ticketing system. The core functionality differs even though both involve HTTP.
- 共享行为: Both perform HTTP requests.；Both read the HTTP response using BufferedReader and InputStreamReader.；Both use URL-related classes to construct connections.
- 行为差异: A uses HTTP POST, B uses HTTP GET.；A sends data in the request body, B sends parameters in the URL query string.；A discards the response, B parses the response to extract ticket IDs.；A has no return value, B returns a List of RTTicket objects.
- 修正建议: Incorporate structural features like control flow graphs and data flow dependencies.；Enhance model with understanding of HTTP methods and their semantics.；Use contrastive learning to distinguish similar API sequences with different intents.

### case_id=3672 FN partial_functionality

- 方法: `readPage` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL and returns its content as a string, optionally skipping comment lines starting with '#'.
- B 摘要: Performs an HTTP POST request with parameters and returns the response body as a string, or null on failure with error codes.
- 静态失败原因: GraphCodeBERT likely failed due to low token similarity (Jaccard 0.20) and large syntactic differences: different API calls, control flow, and error handling. The model could not abstract the high-level semantic equivalence of URL content retrieval.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers them clones because both ultimately fetch web content from a URL and return it as a string, which is a high-level semantic similarity. Differences in HTTP method, parameters, and error handling are seen as variations within the same functional category, fitting Type-4 clone criteria.
- 共享行为: Both read from a URL and return the content as a string；Both use BufferedReader to read line by line；Both concatenate lines into a single string
- 行为差异: A uses GET, B uses POST；A has optional comment filtering, B does not；A throws Exception on failure, B returns null and sets error fields；B has additional parameters and status code handling
- 修正建议: Train model on pairs with different HTTP methods but same high-level purpose；Use data augmentation to generate syntactically diverse but semantically equivalent functions；Incorporate method name/context as additional signal for high-level function

### case_id=3673 FP boilerplate_overlap

- 方法: `readZoneIDs` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads zone IDs from a resource file, parsing each line as an integer and returning a set.
- B 摘要: Fetches tickets for a queue via REST API, parses ticket IDs from response lines, retrieves each ticket, and returns a list.
- 静态失败原因: The static BERT model likely over-relied on surface-level similarities: both do line-by-line reading, integer parsing, exception handling, and return collections. The high frequency of common tokens like 'line', 'readLine', 'parseInt'/'parseLong', 'try', 'catch' may have biased the model towards a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotation typically treats functions with completely different I/O and domain as non-clones, even if they share generic code patterns like reading lines and parsing numbers. The partial similarity is not enough for Type-3/4 under BCB guidelines.
- 共享行为: Both read input line by line using BufferedReader or similar；Both parse integer IDs from lines；Both use try-catch for exception handling
- 行为差异: readZoneIDs reads from a local file resource; getTicketsForQueue makes HTTP requests to a remote server；readZoneIDs returns a HashSet<Integer>; getTicketsForQueue returns a List<RTTicket>；getTicketsForQueue involves multiple network calls, query parameters, and response status checking；getTicketsForQueue has additional logic for handling special lines ('does not exist.') and retrieving individual tickets
- 修正建议: Incorporate structural or control-flow features to distinguish local file I/O from HTTP API calls.；Use data-flow analysis to capture input/output types and sources (file vs. network).；Improve tokenization to differentiate domain-specific API calls (e.g., HttpGet vs. getClass().getResource).

### case_id=3674 FN benchmark_preference_bias

- 方法: `addIDs` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a page from a metabolite database, parses it to extract IDs and scores, and sets them on a PeakListRow object.
- B 摘要: Downloads a page from a generic URL, parses lines to extract version, URL, and information, then notifies listeners.
- 静态失败原因: The model likely correctly identified them as non-clones due to low token overlap and different function purposes. It did not fail; BCB annotation may be a false positive by the benchmark.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider these Type-3 clones due to similar structure of HTTP request and line-by-line reading, overlooking the completely different domain-specific parsing and output.
- 共享行为: Both open an HTTP URL and read lines using BufferedReader；Both have a while loop reading until null；Both catch IOException and handle errors
- 行为差异: Different URL sources and query parameters；Different parsing logic: A looks for specific HTML tags and splits strings; B uses a switch statement on line index；Different outputs: A updates a row object with many fields; B sets simple string fields and notifies listeners；A returns an integer score; B has void return and triggers actions
- 修正建议: Improve BCB annotation guidelines to avoid labeling boilerplate-heavy functions as clones when semantics differ；Use models that better capture function-level semantics beyond structural scaffolding

### case_id=3675 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `copyDeleting`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a specified locale by updating or adding a message key-value pair.
- B 摘要: Copies a file from source to destination using a buffer.
- 静态失败原因: The static model likely relied on low token overlap and different method names, correctly predicting non-clone. The BCB label may be erroneous or based on extremely broad criteria, so the model did not actually fail; the benchmark annotation may be biased.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely considered these clones due to shared file I/O pattern and use of try-finally, which may be seen as broad Type-4 similarity. However, the functional purpose is completely different, making this annotation questionable.
- 共享行为: Both perform file I/O operations (reading and writing).；Both use try-finally blocks for resource cleanup.
- 行为差异: A manipulates text properties files with specific key-value logic; B copies binary data.；A creates a properties file if it doesn't exist; B does not create files.；A handles multiple locales and modifies content; B is a generic file copy.；A uses reader/writer and string processing; B uses streams and byte buffer.
- 修正建议: Re-evaluate the BCB annotation for this pair; consider functional purpose rather than just structural patterns.；Use stricter criteria for clone definition; ensure that clones share at least partial functional similarity.

### case_id=3676 FN partial_functionality

- 方法: `copyResource` vs `storeImage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file via byte-by-byte reading and writing.
- B 摘要: Stores an image from an InputStream to a file with optional resizing and custom naming logic.
- 静态失败原因: Low token overlap (Jaccard=0.1176) and significant structural differences misled the model; the core copying behavior was overshadowed by divergent method names, length, and extra logic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as file-copying operations with similar input-output patterns, accepting broad functional similarity despite additional details.
- 共享行为: Both read data from an input source and write it to a file output
- 行为差异: A reads from URL or local file; B reads from InputStream；A writes each byte individually; B uses IOUtils.copyLarge；B creates directories and handles file naming; A does not；B optionally resizes images; A does not
- 修正建议: Use a semantic model like CodeBERT to capture functional similarity beyond tokens；Incorporate data-flow analysis to identify the common copy pattern

### case_id=3677 FN partial_functionality

- 方法: `main` vs `decodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its ZIP entries to files.
- B 摘要: Decodes a Base64-encoded file and writes the decoded content to another file, returning success status.
- 静态失败原因: The model relied on token-level similarity and method name context; low Jaccard similarity and different high-level tasks (URL extraction vs Base64 decode) caused it to miss the underlying structural I/O pattern, resulting in a non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might have labeled them as clones based on the common pattern of reading from an input stream and writing to an output stream with buffering, considering them as Type-4 functional similar operations of file conversion, despite differing in specific task details.
- 共享行为: Use buffered streams for I/O；Copy bytes from input to output in a loop；Use a fixed-size buffer array
- 行为差异: Different input sources (URL with file/http protocol vs local file)；Different output handling (extracting multiple ZIP entries vs single file)；Different data transformations (ZIP decompression vs Base64 decoding)；One is a main method without return, the other is a utility method returning boolean
- 修正建议: Improve model's ability to abstract over high-level task differences and recognize common I/O patterns；Use pre-training on dataflow graphs to better capture structural similarity

### case_id=3678 FN partial_functionality

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Builds a site for editing by processing XML, applying transformations, and writing output files.
- 静态失败原因: The model correctly predicted non-clone based on low lexical overlap and clear functional difference. From BCB's perspective, it failed to recognize a highly abstracted similarity that is not reflected in the code structure or tokens.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones due to very broad functional similarity: both perform file input/output operations and throw IOException. Such a label would be an extreme example of Type-4 clone acceptance, where only the most abstract purpose is shared.
- 共享行为: Both involve file I/O operations (reading and writing files).；Both throw IOException.
- 行为差异: copyFile is a simple, generic file copy function; buildSiteForEdit is a complex, domain-specific site builder.；copyFile uses FileChannel for efficient copying; buildSiteForEdit uses various I/O streams and custom file system operations.；buildSiteForEdit includes XML transformation, string replacement, FTP handling, and iterative page processing which are absent in copyFile.
- 修正建议: Incorporate high-level semantic tags or domain knowledge about file operations.；Use program summarization to compare overall intent rather than just code structure.；Consider downstream context such as method invocations to infer broader purpose.

### case_id=3679 FP lexical_or_api_overlap

- 方法: `load` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads content from a pastebin URL and returns it as a string.
- B 摘要: Downloads a file from a generic URL to a local destination, with progress updates, and returns success status.
- 静态失败原因: The static BERT model likely relied on lexical and API-level overlap (URL, openConnection, read loops, similar method names) and missed the fundamental difference in return type and file-writing vs string-accumulation semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench typically treats functions with different input/output signatures and different domain-specific behavior (pastebin vs generic download) as non-clones, even if they share common network IO patterns.
- 共享行为: Both open a URL connection and read data from the input stream.
- 行为差异: Function A returns the entire content as a string; Function B writes to a file and returns a boolean.；Function A uses BufferedReader for text; Function B uses BufferedInputStream for binary data.；Function A handles pastebin-specific URL; Function B takes arbitrary URL and destination.；Function A shows error dialog on failure; Function B updates a progress bar and returns true/false.
- 修正建议: Incorporate data flow analysis to track output type and destination.；Use type-aware embeddings that distinguish between writing to a file vs returning a string.；Train on more diverse examples that include both text loading and binary download to learn the functional distinction.

### case_id=3680 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `loadSourceCode`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks and anchor text from an HTML page fetched via a URL, returning a Vector array of links and texts.
- B 摘要: Loads source code from a resource file, applies syntax highlighting, and stores the result as an HTML string in a field.
- 静态失败原因: Static BERT models may over-emphasize the overlapping I/O-related tokens (BufferedReader, InputStreamReader, URL, readLine) and miss the entirely different semantic intents and outputs. The structural similarity in the reading loop and exception handling may mislead the model into thinking they are clones.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clones because despite sharing low-level I/O patterns, the core functionality (link extraction vs. source code display) is completely different and they serve different purposes. BCB typically requires at least partial semantic overlap, which is absent here.
- 共享行为: Both use BufferedReader and InputStreamReader to read text line by line.；Both open a connection/stream from a URL or file.；Both handle exceptions (one throws, one catches).；Both utilize similar I/O boilerplate code.
- 行为差异: Function A fetches from a URL, Function B loads from a local resource file.；Function A parses HTML with regex to extract links, Function B applies syntax highlighting to source code.；Function A returns a Vector array, Function B sets a field (void return).；Function A uses timing and debug output, Function B does not.
- 修正建议: Include function names and return types as additional features.；Use more contextual embeddings that capture method-level semantics beyond token overlap.；Train on pairs with low token similarity but different functionality to reduce API bias.

### case_id=3681 FP partial_functionality

- 方法: `readUNI` vs `CheckUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a tab-separated file from a URL, parses each line to extract an ID and description, and adds them to a provided vector.
- B 摘要: Opens a URL connection and returns the first line of the response as a string.
- 静态失败原因: Static models may focus on lexical overlap (e.g., URL, openStream) and overlook semantic differences in the loop structure, return type, and parameter usage, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled as non-clone because the functions have different purposes and outputs; the similarity is only in reading from a URL, but the core functionality is not the same.
- 共享行为: Both open a URL and read text from it.
- 行为差异: A reads multiple lines and parses tab-separated values into a vector; B reads only the first line and returns it as a string.；A uses a generic URL; B uses HttpURLConnection.；A handles closing the stream; B does not.；A catches MalformedURLException separately; B does not.
- 修正建议: Incorporate control flow and data dependency analysis.；Use AST-based features to distinguish loop patterns and output transformations.；Train on more diverse examples with similar API sequences but different logic.

### case_id=3682 FP lexical_or_api_overlap

- 方法: `addQDInformation` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads and parses a local or remote QD info file, updating internal data structures.
- B 摘要: Constructor for a Swing browser that loads an XML/HTML page from a URL, applies optional XSLT, and sets up the GUI.
- 静态失败原因: The model likely relied on lexical overlap (common tokens like 'URL', 'BufferedReader', 'InputStreamReader', 'try', 'catch') and similar API usage patterns, missing the semantic differences in processing logic and overall functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions have completely different purposes and logic, despite sharing some IO boilerplate.
- 共享行为: Both use URL.openStream, BufferedReader, InputStreamReader for reading input.；Both handle IOException and have try-catch blocks.；Both involve reading from a URL or file.
- 行为差异: Function A reads a specific file format (qdinfo.dat) and updates state; Function B reads any XML/HTML and displays it in a GUI.；Function A has no GUI; Function B is a constructor building a Swing GUI.；Function A parses lines with 'pg' and 'pt' prefixes; Function B processes XML stylesheets and transforms content.
- 修正建议: Incorporate dataflow analysis to distinguish reading/parsing vs. UI construction.；Use functional role or method context (e.g., method name, class hierarchy) as additional features.；Train on more diverse examples of IO usage with different intents.

### case_id=3683 FP lexical_or_api_overlap

- 方法: `readVersion` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a version resource file and extracts version, revision, and date.
- B 摘要: Constructor for a simple web browser GUI that fetches and displays HTML content, optionally applying an XSLT transformation.
- 静态失败原因: The model likely focused on superficial similarities: both use `URL`, `BufferedReader`, `InputStreamReader`, `url.openStream()`, and `readLine()` in a loop with similar exception handling. This lexical overlap might have triggered a false positive despite large semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because their functionality is completely different; one is a simple resource reader, the other is a complex GUI constructor with XML handling.
- 共享行为: Both open a URL and read lines from a BufferedReader.；Both use try-catch for IOException.；Both have loops reading lines from a stream.
- 行为差异: Function A reads a local resource file for version info; B reads a URL for web content.；A extracts key-value pairs; B parses XML and applies transformations.；A is a private void method; B is a public constructor with GUI building.；A has no GUI; B creates a full Swing interface with multiple components.
- 修正建议: Incorporate structural or data-flow analysis to distinguish simple property reading from complex GUI initialization.；Improve semantic understanding of the overall goal (e.g., reading version vs. displaying a web page).；Use larger context or function signatures to capture intent.

### case_id=3684 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `importRoles`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks and link texts from HTML page content retrieved from a URL.
- B 摘要: Parses XML role data from a URL and returns a list of RoleName objects.
- 静态失败原因: Static BERT models may overemphasize lexical and API-level similarities (URL, BufferedReader, while loop, StringBuffer) while ignoring the high-level semantic difference in data extraction/parsing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the core functionality differs: one extracts HTML links, the other parses XML roles. Despite similar boilerplate I/O code, the semantic purpose and output types are distinct.
- 共享行为: Both open a URL connection and read input line by line using BufferedReader.；Both use a StringBuffer to accumulate lines from the input.；Both return a collection derived from the parsed data.；Both handle exceptions with a catch block or explicit exception declaration.
- 行为差异: A uses regex to match anchor tags and extract links and texts, while B looks for a specific XML closing tag and parses role names.；A returns two separate Vectors for links and texts; B returns a single ArrayList of RoleName objects.；A includes additional logging and time-checking calls; B has none.；A processes the entire page content as a single string; B processes line by line, accumulating until a closing tag appears.
- 修正建议: Incorporate dataflow analysis to track how input lines are processed differently (regex vs. XML tag detection).；Use function name and method signature embeddings to capture domain-specific semantics.；Add attention to output types and return structures.

### case_id=3685 FN benchmark_preference_bias

- 方法: `testNetworkHTTP` vs `callService`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Performs multiple HTTP GET requests to various URLs, reading and discarding response lines, for testing purposes.
- B 摘要: Performs a single HTTP GET request to a constructed URL, reading and accumulating the response into a buffer, storing the result.
- 静态失败原因: Static BERT models may rely on token overlap and API sequence. The token Jaccard is low (0.208), but the API calls (URL, HttpURLConnection, BufferedReader, IOException) are common. However, the significant structural differences (multiple vs single requests, data disposal vs accumulation) might have led the model to classify as non-clone due to low overall similarity. The model may have focused on method signature and control flow differences.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone because both functions demonstrate the same core pattern of opening an HTTP connection, reading the response, and handling exceptions, despite differences in the number of requests and response handling. The shared API usage (URL, HttpURLConnection, BufferedReader) is typical for Type-3/Type-4 clones in benchmarks.
- 共享行为: Both create a URL object and open an HTTP connection；Both use BufferedReader to read the response line by line；Both handle IOException exceptions
- 行为差异: A makes multiple connections to different URLs, while B makes one to a single constructed URL；A discards the response data, while B accumulates it into a buffer；A disconnects in a finally block, B does not explicitly disconnect；A has logging, B does not
- 修正建议: Improve recognition of common API usage patterns despite differing control flow；Consider using graph-based models that capture data flow and resource usage；Train on more diverse clone types including partial functionality clones

### case_id=3686 FP lexical_or_api_overlap

- 方法: `getURLContent` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads content from a URL and returns the entire response as a string.
- B 摘要: Searches Google Images, parses HTML to extract image URLs, and updates UI components with the first image.
- 静态失败原因: The static model likely focused on the lexical overlap of common API calls (URL, BufferedReader, InputStreamReader, readLine) and the structural pattern of reading from a URL, ignoring the higher-level semantic differences in purpose, side effects, and output interpretation.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels functions that share a common high-level purpose but may differ in implementation as Type-4 clones. Here, the purposes are completely different (generic URL fetcher vs. specific image search with UI), so BCB labels as non-clone.
- 共享行为: Both open a URL connection and read lines of text from the input stream.
- 行为差异: Function A returns the raw content as a string; function B parses the content and extracts image URLs.；Function A uses generic URLConnection; function B uses HttpURLConnection with a User-Agent header.；Function A uses StringBuilder for efficiency; function B uses string concatenation.；Function B has side effects on UI (MusicBoxView) and is void; function A has no side effects and returns a string.
- 修正建议: Improve the model to incorporate semantic understanding of function purpose beyond API usage.；Use dataflow analysis to track how the read content is used after reading.；Train on more diverse examples to distinguish between utility functions and domain-specific functions.

### case_id=3687 FN partial_functionality

- 方法: `callApiPost` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Makes an HTTP POST request, sends parameters, and returns input stream after validating response code.
- B 摘要: Registers a user by encoding password, setting metadata, creating forum account via HTTP GET, persisting user, and sending confirmation email.
- 静态失败原因: Low token overlap combined with structural similarity in HTTP-related code blocks confused the model, which focused on the common pattern and missed the distinct business logic context due to limited attention or training data.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone because both involve HTTP requests and I/O exception handling, fitting a broad Type-3 or Type-4 pattern of network interaction despite different business purposes.
- 共享行为: Both perform HTTP URL connection operations.；Both handle IOException with error handling.
- 行为差异: A is a generic HTTP POST utility; B is a specific business-logic registration method.；B includes password encoding, database persistence, email sending; A does not.；B's HTTP call is a GET to a forum URL; A uses POST.；B has additional validation and exception types (NumberFormatException, MailException).
- 修正建议: Include more examples contrasting utility vs. business-logic functions with similar code blocks.；Use contrastive learning to differentiate functions based on overall purpose rather than local patterns.；Incorporate method signatures or docstrings as additional input features.

### case_id=3688 FN boilerplate_overlap

- 方法: `modifyApplicationMessage` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file for internationalization by updating or adding a key-value pair.
- B 摘要: Tests a custom StraightStreamReader by writing bytes to a file and reading them back with various read methods.
- 静态失败原因: Static BERT may have focused on token overlap (File, try, catch, while, etc.) and not captured the semantic difference in purpose and data manipulation.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might have labeled them as clones due to overlapping boilerplate (file handling, exception handling, loops) and both being Java utility functions, but the actual functionality is distinct.
- 共享行为: Both perform file I/O operations；Both use try-catch for exception handling；Both use loops for reading/writing
- 行为差异: Different objectives: one modifies configuration properties, the other tests stream reading；Different file types and formats: properties vs binary data；Different APIs: Properties vs FileInputStream/FileOutputStream；Different control flow: search-and-replace vs byte-by-byte verification
- 修正建议: Increase reliance on control flow and data flow dependencies；Use function call context to disambiguate；Incorporate domain-specific knowledge about file formats

### case_id=3689 FN partial_functionality

- 方法: `addIDs` vs `lookupFutureEvents`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Adds metabolite IDs from a GMD database to a row object by parsing HTML responses from HTTP requests.
- B 摘要: Fetches future events from the Meetup API, parses JSON responses, and returns a list of Event objects.
- 静态失败原因: Static BERT models rely heavily on lexical and syntactic similarity, which is low (token Jaccard=0.161) due to different API calls, variable names, and domain-specific literals, causing under-estimation of structural similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the high-level algorithmic pattern of fetching data from a URL, parsing the response, and populating objects as a Type-4 (conceptual) clone, even with different domains and details.
- 共享行为: Open a URL via HTTP and read input stream；Parse response (HTML or JSON) line by line；Extract data and populate domain objects
- 行为差异: Different data sources (metabolite database vs. Meetup API)；Different parse formats (HTML fragments vs. JSON)；Different return types (int with score vs. List<Event>)；Different error handling (log and return 0 vs. throw exception)
- 修正建议: Use graph-based models (e.g., code property graphs) to capture high-level control and data flow patterns；Incorporate attention to I/O patterns like HTTP requests to recognize similar behavior patterns；Train with more examples of diverse web-data-fetching tasks to learn the abstraction

### case_id=3690 FN partial_functionality

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.5`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using byte-by-byte writing.
- B 摘要: Copies a file to another file using NIO FileChannels, creating parent directories if needed.
- 静态失败原因: Low token overlap (0.178) and no shared API calls or control structures; model failed to infer the common high-level copying semantics.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may view both as file copy operations, tolerating differences in source type, I/O method, and directory creation as non-essential variations.
- 共享行为: Both copy data from a source to a destination file
- 行为差异: A supports URL sources, B only files；A uses byte-stream I/O, B uses NIO channels；B creates parent directories, A does not；B has different exception handling (throws as error)
- 修正建议: Train on tasks that emphasize functional similarity over lexical overlap；Incorporate data flow or I/O operation detection

### case_id=3691 FP lexical_or_api_overlap

- 方法: `decodeFileToFile` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Decodes a Base64-encoded input file and writes the decoded content to an output file.
- B 摘要: Reads and parses configuration strings and a file to populate hash maps and sets for Tibetan transliteration.
- 静态失败原因: The static BERT model likely overemphasized the lexical overlap in I/O code (e.g., 'InputStream', 'FileInputStream', 'try', 'catch', 'IOException') and the presence of loops reading buffers, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because their high-level purpose and algorithmic logic are entirely different, despite sharing some common I/O boilerplate.
- 共享行为: Both use try-catch-finally blocks for IOException handling.；Both involve reading from an InputStream and writing/buffering data.
- 行为差异: Function A performs Base64 decoding and file copying; Function B parses comma-separated tokens and initializes complex data structures.；Function A returns a boolean success flag; Function B is void and populates global/static collections.；Function A does not use StringTokenizer or manage multiple sets/maps.
- 修正建议: Incorporate dataflow or control-flow analysis to distinguish core logic from boilerplate.；Use larger context or attention to entire method semantics.；Fine-tune on a dataset that penalizes common API usage patterns.

### case_id=3692 FP lexical_or_api_overlap

- 方法: `readData` vs `decodeFileToFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses static string constants (tops, lefts, etc.) into sets and maps, then reads a file to populate additional data structures for Tibetan Wylie transliteration.
- B 摘要: Decodes a Base64-encoded input file and writes the decoded binary data to an output file, returning success status.
- 静态失败原因: The model likely over-relied on superficial lexical overlaps such as 'FileInputStream', 'BufferedInputStream', 'IOException', and common I/O boilerplate patterns, ignoring the distinct purposes and data flows.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label this as non-clone because the functionalities are entirely different: one is a data structure initializer, the other is a file format converter. The low token Jaccard (0.064) supports no clone.
- 共享行为: Both perform file I/O operations；Both use try-catch for IOException handling；Both involve reading from an input stream
- 行为差异: Function A processes configuration data to build internal data structures; Function B performs Base64 decoding without any data structure building；Function A reads from multiple static sources and a file; Function B reads one input file and writes to one output file；Function A has complex parsing logic with line-based processing; Function B uses a simple read-write loop
- 修正建议: Incorporate method-level context (e.g., method name, comments) to capture purpose；Use data flow analysis to distinguish between data transformation vs. data decoding；Train on more diverse examples to reduce bias towards API-level similarities

### case_id=3693 FP lexical_or_api_overlap

- 方法: `unzipModel` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Unzips a zip file by reading entries and writing them to files in a temp directory.
- B 摘要: Reads comma-separated token strings and a structured file to populate multiple sets and hash maps.
- 静态失败原因: The static model may have been misled by overlapping API keywords like FileInputStream, IOException, and generic loop structures, ignoring the completely different domain goals.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels Type-3/4 clones as those with similar functionality or structure. Here, functionality is entirely different (file extraction vs data parsing), so BCB correctly labels as non-clone.
- 共享行为: Both read from an input source；Both use exception handling；Both involve loops processing data
- 行为差异: A processes a zip archive; B processes string tokens and a specific file format；A writes binary output files; B populates in-memory data structures；A uses ZipInputStream and BufferedOutputStream; B uses StringTokenizer and file parsing with custom logic；Different error handling: A throws EDITSException; B prints stack trace and handles specific error conditions
- 修正建议: Incorporate task-level semantic understanding beyond API sequences；Use control flow graphs to detect different computational intents；Improve tokenization to distinguish between domain-specific operations

### case_id=3694 FP lexical_or_api_overlap

- 方法: `convert` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Converts an ACRNEMA stream file to DICOM format, handling pixel data inflation and UID generation.
- B 摘要: Generates adapter classes from a Prolog file and writes them to a JAR file, with debug options.
- 静态失败原因: The model may have been misled by overlapping tokens like 'File', 'IOException', 'System.out.println', 'for' loops, and similar boilerplate for reading/writing files and checking conditions.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because these are completely different tasks and domain-specific; no functional similarity.
- 共享行为: Both perform file I/O operations；Both use exception handling and print error messages；Both have a sequence of steps with conditional checks
- 行为差异: A handles DICOM medical image data; B generates Java adapter classes from Prolog；A reads and writes pixel data; B parses Prolog and writes Java classes；A's output is a DICOM file; B's output is a JAR file with adapter classes
- 修正建议: Improve model's ability to capture high-level semantics beyond lexical patterns；Incorporate structural or data-flow representations；Use contrastive learning on dissimilar pairs with low token overlap but similar API usage

### case_id=3695 FP lexical_or_api_overlap

- 方法: `getURLContent` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads entire content of a given URL and returns it as a string, appending newlines after each line.
- B 摘要: Fetches a version string from a specific hardcoded URL, returning only the first line (or null on failure).
- 静态失败原因: High lexical overlap (URL, URLConnection, BufferedReader, readLine) and similar structural pattern caused the model to treat them as clones, ignoring semantic differences in purpose, encoding, error handling, and output granularity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have different purposes (generic content retrieval vs. specific version fetch) and different return behavior (full content vs. single line), which are considered semantically distinct despite shared boilerplate.
- 共享行为: Both open a URL connection；Both read lines using BufferedReader；Both return a String
- 行为差异: Function A returns full content with newlines; Function B returns only the first line；Function A specifies encoding; Function B uses default；Function A throws IOException; Function B catches all exceptions and returns null；Function A uses a parameter URL; Function B uses a hardcoded URL
- 修正建议: Incorporate semantic understanding of function purpose；Pay attention to differences in error handling and encoding；Consider the return value scope (full content vs. single line)

### case_id=3696 FN partial_functionality

- 方法: `sendExceptionToServer` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an exception report to a remote server via HTTP POST, encoding system information and exception details.
- B 摘要: Downloads an OPDS catalog or book from a URL using HTTP, handling pagination, content types, and progress.
- 静态失败原因: Low lexical overlap (Jaccard 0.113) and different method names/specific operations caused the static model to focus on surface differences rather than the shared network communication pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled as clone due to both functions being network I/O operations that use URLConnection, set properties, and handle responses, which is a common pattern considered as Type-3/4 clone in BigCloneBench.
- 共享行为: Both open a URLConnection；Both set connection properties (e.g., request headers, timeouts)；Both handle I/O streams for reading/writing；Both catch exceptions and handle errors
- 行为差异: Function A sends a fixed set of parameters as POST data; Function B may GET or POST for different content types；Function B handles pagination and redirects; A does not；Function A is a simple one-shot request; B may perform multiple requests in a loop；Function B deals with content encoding and file naming; A does not
- 修正建议: Use a model that captures control-flow and data-flow patterns, e.g., graph-based or AST-based with API usage abstraction；Train on clone pairs that share only broad functional similarity (Type-4) to learn invariance to different details

### case_id=3697 FN benchmark_preference_bias

- 方法: `getFile` vs `decodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint location in the XML, and saves to a temp directory.
- B 摘要: Decodes a Base64-encoded file and writes the decoded content to an output file.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone because it captured the distinct APIs and dataflow, so it did not fail; the error is due to BCB's overly broad clone definition.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to superficial structural similarity in file I/O and stream processing, considering it a Type-3 clone where similar control flow and resource handling are present despite different core functionalities.
- 共享行为: File input/output operations；Exception handling with try-catch-finally；Stream closure in finally block
- 行为差异: Purpose: downloading and modifying WSDL vs Base64 decoding；Return type: String (file path) vs boolean (success)；Input parameters: service name, URL, endpoint vs input and output file paths；Code length and complexity: much longer with XML parsing vs simple buffer copy
- 修正建议: Refine BCB annotation guidelines to require functional similarity beyond boilerplate code；Use semantic similarity metrics that focus on core functionality rather than structural patterns

### case_id=3698 FP partial_functionality

- 方法: `convert` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Converts ACRNEMA stream files to DICOM format by parsing pixel data, adding UIDs, and writing output.
- B 摘要: Reads configuration data from file lines to populate lookup tables for Tibetan transliteration.
- 静态失败原因: The model likely focused on superficial similarities such as file I/O, error handling, and looping structures, missing the completely different semantic contexts and operations.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels these as non-clones because they have completely different high-level purposes and no shared functionality beyond basic Java constructs.
- 共享行为: Both involve reading data from an external source (file in A, file/string in B)；Both use try-catch for IOException handling；Both have loops and conditional logic
- 行为差异: A performs DICOM format conversion with specific pixel data handling; B initializes multiple sets and hash maps from parsed tokens；A writes output to a file; B populates in-memory data structures；A deals with medical imaging tags; B deals with linguistic character mappings
- 修正建议: Incorporate dataflow and control-flow analysis to distinguish different domain-specific operations；Use program slicing to highlight core functionality differences；Train on more diverse examples to avoid over-reliance on syntactic patterns

### case_id=3699 FP lexical_or_api_overlap

- 方法: `executePost` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Executes an HTTP POST request with parameters and returns the response string.
- B 摘要: Fetches a version check URL, parses lines for build numbers, and performs version check.
- 静态失败原因: The model likely relied on lexical and API-level overlap (URL, InputStream, BufferedReader, close patterns) and missed the semantic difference in HTTP methods, parameters, and purpose. The high structural similarity in reading streams may have triggered a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these non-clones because the core functionality is different: one is a generic HTTP POST utility, the other is a specific version-check logic. The common networking boilerplate is not sufficient for Type-3/4 similarity.
- 共享行为: Both open a URL and read an input stream.；Both use BufferedReader to read line by line.；Both close resources in a finally or after reading.
- 行为差异: executePost uses POST method with parameters; doVersionCheck uses GET.；executePost returns the full response; doVersionCheck parses specific lines and calls another method.；Error handling differs: executePost prints stack trace and returns null; doVersionCheck shows error dialog.；doVersionCheck shows/hides wait cursor on a View.
- 修正建议: Incorporate method name and comment semantics.；Use dataflow analysis to capture input/output types and dependencies.；Consider the overall return type and side effects (e.g., POST vs GET, version parsing).

### case_id=3700 FN benchmark_preference_bias

- 方法: `login` vs `getURLContent`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.5`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Logs into LOLA by sending a POST request with email and password, extracts and returns the session ID from the response, or returns empty string on error.
- B 摘要: Fetches the entire content of a given URL (GET) and returns it as a string, throwing IOException on failure.
- 静态失败原因: The model correctly identified the low token overlap (0.213) and likely recognized the different intents (login vs. content retrieval), but BCB's annotation preference for partial functionality similarity led to a clone label, causing the model's non-clone prediction to be marked as false negative.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotators may consider both methods as 'getting data from a URL' and may overlook differences in HTTP method and response processing, focusing on the shared boilerplate of URL connection and reading.
- 共享行为: Open a URLConnection and get an input stream；Use BufferedReader to read lines from the stream；Close resources (reader) after reading
- 行为差异: Function A uses POST with form-encoded parameters; Function B uses GET with no parameters；Function A only reads the first line to extract session ID; Function B reads all lines；Function A handles exceptions internally with a catch block; Function B declares throws IOException；Function A uses hardcoded URLs and writes output; Function B takes URL as parameter and only reads
- 修正建议: Use data flow analysis to distinguish POST vs GET and different response processing；Incorporate higher-level semantic features like method purpose or API usage patterns；Adjust clone detection thresholds for partial functionality clones based on benchmark guidelines

### case_id=3701 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `readScalarpvviewerDocument`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a new version of jEdit by parsing a version file from a URL and comparing build numbers.
- B 摘要: Reads an XML configuration file from a URL to restore the state of a scalar PV viewer.
- 静态失败原因: Static BERT methods may over-rely on lexical and structural features (both have BufferedReader, while loop, try-catch, URL) and miss the semantic gap due to lack of understanding of domain-specific APIs and the overall goal of each function. The token Jaccard similarity is low (0.16), but the model might have been misled by common programming idioms.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functional purpose and algorithmic logic are entirely different despite shared structural patterns like URL reading and exception handling. The annotation preference emphasizes semantic equivalence or near-miss similarity, not broad structural overlap.
- 共享行为: Both open a URL and read lines using BufferedReader.；Both handle IOException with a try-catch block.；Both perform some string parsing on each line.；Both display UI messages or update UI components.
- 行为差异: Different inputs: View object vs URL only.；Different parsing logic: version/build line prefix matching vs XML structure extraction.；Different outcomes: version comparison and notification vs restoring multiple UI settings (font, panels, PV values).；Different domain: jEdit version checking vs scientific data viewer configuration.
- 修正建议: Incorporate method name and context embeddings to capture purpose.；Use dataflow analysis or abstract syntax trees to distinguish control flow patterns.；Train with more diverse non-clone pairs that share structural boilerplate but differ in semantics.；Apply contrastive learning to push apart functions with different goals.

### case_id=3702 FN benchmark_preference_bias

- 方法: `doGet` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve and render a portal page with access control, logging, and caching.
- B 摘要: Reads a DICOM image file, parses its metadata, reads pixel data, and writes it to a new file.
- 静态失败原因: Static BERT correctly predicted non-clone due to low lexical overlap (token Jaccard 0.039), different APIs, and distinct control structures.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have mistakenly labeled as clone due to coarse semantic categories or annotation error; both functions involve reading, processing, and outputting data, but are fundamentally different in purpose and implementation.
- 共享行为: Both involve file or data I/O；Both use logging/informational output
- 行为差异: Different domains: web portal vs. medical image processing；Different I/O: HTTP request/response vs. file streams；Different data processing: page retrieval vs. DICOM parsing；Different complexity: A has extensive control flow and caching; B is straightforward conversion
- 修正建议: Re-annotate BCB label as non-clone to reflect actual semantic dissimilarity；Improve BCB annotation guidelines to avoid false positives from broad interpretation

### case_id=3703 FP boilerplate_overlap

- 方法: `encryptPassword` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Encrypts a password using MD5 hash and returns the hex string.
- B 摘要: Handles an HTTP request in a Struts action to classify a concept, involving XML parsing and remote server communication.
- 静态失败原因: The static BERT model likely failed due to boilerplate overlap (e.g., both use try-catch blocks, return statements, and common API calls like getBytes('UTF-8')). The model may have been misled by these superficial similarities and overlooked the vast semantic difference, possibly exacerbated by the truncation of function B in the input.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when there is no functional similarity beyond trivial boilerplate. Here, the functions have completely different purposes and implementations, so BCB correctly labeled them as non-clones.
- 共享行为: Both are Java methods returning a value.；Both may return a value in exceptional cases (catch block).
- 行为差异: Function A performs cryptographic hashing; Function B handles web request processing and classification.；Function A is short and simple; Function B is long and complex with many statements and objects.；Function A uses MessageDigest and byte2hex; Function B uses HTTP connections, XML parsing, and session management.
- 修正建议: Enhance model to capture long-range dependencies and overall program structure (e.g., using AST or data flow graphs).；Improve tokenization to reduce impact of common boilerplate tokens.；Use contrastive learning to distinguish truly similar functions from those with only lexical overlap.

### case_id=3704 FN benchmark_preference_bias

- 方法: `main` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request to the RenRen API with predefined parameters and prints the response.
- B 摘要: Reads a resource file from the classpath, concatenates its lines, and sets the text in a Swing component.
- 静态失败原因: The static BERT model likely relied on lexical and structural similarity (low token Jaccard of 0.116) and correctly detected no clone under strict semantics, but failed to recognize the broad behavioral pattern that BCB annotators considered similar.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered them clones due to the abstract pattern of reading an input stream line by line and outputting the content, which falls under a very broad Type-4 semantic similarity.
- 共享行为: Both use BufferedReader to read lines from an InputStream；Both have a while loop reading lines until null
- 行为差异: I/O source: HTTP network request vs classpath resource file；Output destination: console vs GUI component；Exception handling: throws IOException vs catches Exception；Context: standalone main method vs anonymous Runnable in a Swing application
- 修正建议: Train with more abstract behavioral representations；Include dataflow analysis to capture I/O patterns；Consider benchmark-specific clone definitions during evaluation

### case_id=3705 FP lexical_or_api_overlap

- 方法: `SRWGuiClient` vs `parse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Constructor for a GUI browser that loads XML from a URL, applies XSLT transformations, and displays HTML in a Swing JEditorPane.
- B 摘要: Parses delimited data from a file or URL using StreamTokenizer, builds a DataSet object, and handles headers and type conversions.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on overlapping lexical tokens (URL, openStream, BufferedReader, try, catch) and structural patterns (reading from URL in try-catch), ignoring the entirely different purposes (GUI vs parsing) and surrounding context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels clones only if functions share high-level functionality. Here, one is a GUI constructor and the other is a data parser, so they are functionally distinct. The low token Jaccard (0.12459) further supports non-cloneness.
- 共享行为: Both read data from a URL using BufferedReader and InputStreamReader；Both handle IO exceptions with try-catch blocks；Both use similar stream-reading constructs (openStream, readLine, append)
- 行为差异: Function A builds a Swing GUI with buttons and text fields, while Function B is a parsing method with no GUI；Function A applies XSLT transformations to XML and displays HTML, while Function B tokenizes delimited data and constructs a DataSet；Function A uses JEditorPane and JScrollPane, while Function B uses StreamTokenizer and NumberFormat
- 修正建议: Train with more examples that distinguish API usage context (GUI vs data processing)；Incorporate dataflow or control-flow analysis to capture overall functionality；Use larger context or method-level embeddings that capture the method's purpose beyond local token overlap

### case_id=3706 FN benchmark_preference_bias

- 方法: `sendExceptionToServer` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Sends an exception stack trace to a remote server via HTTP POST with URL-encoded parameters.
- B 摘要: Reads a configuration file, tokenizes its content, and populates multiple sets and hash maps for character mappings.
- 静态失败原因: Static BERT/GraphCodeBERT likely correctly predicted non-clone because the lexical and structural overlap is very low (Jaccard 0.099), and the semantic intentions are clearly different.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this as clone due to a broad interpretation of 'data transfer' or 'initialization' pattern, but the functions are fundamentally different in purpose and implementation.
- 共享行为: Both use try-catch for IOException handling.；Both involve reading input (one from exception, one from file).
- 行为差异: Function A sends data to a remote server via HTTP; Function B only reads local data and updates in-memory structures.；Function A uses StringBuilder to build URL-encoded parameters; Function B uses StringTokenizer to parse comma-separated tokens.；Function A writes to OutputStream and reads HTTP response; Function B populates HashSets and HashMaps.；Function A deals with exception objects and stack traces; Function B deals with Wylie-to-Unicode mapping data.
- 修正建议: Re-examine BCB annotation for this pair; consider removing it from clone set.；Improve benchmark consistency by requiring stronger functional overlap.

### case_id=3707 FN partial_functionality

- 方法: `CopyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel transfer.
- B 摘要: Generates website pages by transforming XML and writing output files with extensive processing.
- 静态失败原因: The static model likely failed because it relies on token overlap and syntactic similarity, which are very low (Jaccard=0.053). The functions share minimal common tokens beyond basic file I/O classes, and the semantic difference is huge.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as clone only if they consider file I/O as a broad functional category, but this seems insufficient for meaningful clone detection.
- 共享行为: Both perform file I/O operations (reading and writing).；Both use FileInputStream to read files.；Both handle file paths.
- 行为差异: A is a simple one-file copy; B generates multiple files in a loop with complex transformations.；A uses NIO FileChannel for efficient transfer; B uses basic streams and custom file system operations.；B includes debugging, error handling, and string manipulation; A has no such overhead.；The overall purpose and complexity are vastly different.
- 修正建议: Incorporate dataflow or control-flow analysis to capture file read/write patterns.；Use graph-based models that can abstract high-level operations, such as reading and writing files.；Include more robust similarity measures that consider partial functionality at an abstract level.

### case_id=3708 FP other

- 方法: `copyFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Utility method to copy a file using FileChannel.
- B 摘要: Event handler for GUI preferences dialog, processing file chooser commands and saving settings.
- 静态失败原因: Likely due to lexical overlap of common Java keywords (File, try-catch) and long code length that misled the model into superficial similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels non-clone due to completely different functionality and method names.
- 共享行为: Both involve file I/O indirectly (A copies files, B uses file chooser).
- 行为差异: A performs file copy; B handles GUI events and updates preferences.；A is static utility; B is instance method overriding ActionListener.；A uses FileChannel; B uses JFileChooser and property persistence.
- 修正建议: Incorporate method name and type signature into representation.；Use program slicing to focus on core behavior.

### case_id=3709 FN partial_functionality

- 方法: `copy` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source path to destination path using buffered byte streams.
- B 摘要: Launches a NexOpen project configuration in Eclipse, including checking project validity, modifying pom files, and setting up Hibernate reverse engineering file copying from bundle resources.
- 静态失败原因: The model likely focused on token overlap and syntactic patterns; due to very low token Jaccard and different method signatures, it predicted non-clone; it may have missed the shared I/O copy concept or that the I/O operation in B is a significant portion of its functionality (though minor in context).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled them as clones due to the common I/O copy operation and the finally block pattern for closing streams; however, the overall functionality is vastly different.
- 共享行为: Both perform data copying using InputStream/OutputStream；Both handle I/O exceptions and close streams
- 行为差异: A is a simple file copy; B is a complex Eclipse launch configuration with many steps；B has conditional logic, project validation, and attribute parsing；B uses external libraries and Eclipse APIs；B involves file copying only as a minor sub-task
- 修正建议: Improve model to recognize functional similarity even when tokens differ, e.g., by using data flow analysis to detect that both functions ultimately copy data from a source to a destination；Incorporate higher-level API recognition (e.g., file copy vs. bundle resource copy)

### case_id=3710 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `readURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Validates server handshake by checking username and authenticating via HTTP request to session server.
- B 摘要: Reads content from a URL and prints each line to standard output.
- 静态失败原因: Static models like GraphCodeBERT may focus on local structural patterns (e.g., URL.openStream, BufferedReader, catch Exception) and overlook the distinct control flow and semantic goals, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions serve entirely different purposes (authentication vs. content printing) and have minimal behavioral overlap despite some API usage similarity.
- 共享行为: Both open a URL connection and read a line using BufferedReader.
- 行为差异: Function A performs authentication and sends a login packet; B only prints lines in a loop.；A handles specific string validation and session details; B is generic URL reading.；A uses URL.openStream() inside a conditional branch; B uses it unconditionally.
- 修正建议: Incorporate data flow analysis to capture actual dependencies and output behavior.；Add contrastive training examples where API usage overlaps but semantics differ.；Enhance model with call graph context to distinguish authentication from generic I/O.；Use code summarization or comment embedding to capture high-level intent.

### case_id=3711 FP lexical_or_api_overlap

- 方法: `addDataFromURL` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads entire content from a URL and appends it to a text buffer.
- B 摘要: Reads FASTA-like sequences from a URL and parses them into names and sequences lists.
- 静态失败原因: Static BERT methods may rely on token-level similarity and structural patterns. Both functions share boilerplate code for URL input stream handling and exception catching, leading to high lexical overlap in API calls like openStream, InputStream, and try-catch blocks, causing a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically annotates Type-3/Type-4 clones if there is significant partial functional overlap. Here the only commonality is reading from a URL, but the processing logic and output are completely different, so it would not be considered a clone.
- 共享行为: Both open a URL stream and read data line by line
- 行为差异: Function A appends all lines into a single string; Function B parses structured FASTA data into separate lists；Function A uses BufferedReader directly; Function B uses ImportHelper class for parsing；Function A appends URL string on exception; Function B handles specific exceptions
- 修正建议: Improve sensitivity to data-flow and control-flow differences；Incorporate structural alignment ignoring common boilerplate；Use semantic similarity focusing on output behavior

### case_id=3712 FN partial_functionality

- 方法: `loadSourceCode` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a source file, applies syntax highlighting to each line, and builds an HTML string.
- B 摘要: Makes an HTTP POST request to a remote service, sends JSON arguments, reads the response, and parses it as JSON.
- 静态失败原因: Static models may have been misled by the shared I/O boilerplate (InputStream, BufferedReader) and failed to capture the distinct functional purposes and different API calls (syntaxHighlight vs JSON serialization).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have incorrectly labeled this as a Type-4 clone due to structural similarity in I/O patterns, but the functional divergence is too large.
- 共享行为: Both open an InputStream, wrap it in InputStreamReader and BufferedReader, and read lines in a loop.
- 行为差异: Method A reads from a local file resource; Method B reads from an HTTP response.；Method A performs syntax highlighting; Method B performs JSON serialization/deserialization.；Method A builds an HTML string; Method B returns a deserialized Java object.；Error handling differs: Method A catches generic Exception; Method B handles ConnectTimeoutException with retry logic.
- 修正建议: Improve model's ability to distinguish between different resource types (file vs network) by incorporating type information.；Use dataflow analysis to track the origin and destination of data.；Train on more diverse examples of non-clones with similar I/O patterns.

### case_id=3713 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint attribute in the XML, and saves it to a temporary location.
- B 摘要: Copies a file from source to destination using FileChannel transferTo.
- 静态失败原因: Static BERT models rely on token similarity and structural patterns; the low Jaccard similarity (0.129) and different control flows led to a non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone due to the shared use of FileChannel for file copying, considering the surrounding operations as noise, though this is a very broad interpretation.
- 共享行为: Both use Java NIO FileChannel for file I/O operations.
- 行为差异: Function A downloads from a URL, modifies XML, and checks file existence; Function B simply copies existing files.；Function A handles multiple specific exceptions; Function B throws generic Exception.；Function A returns a file path; Function B is void.；Function A has additional XML parsing and attribute setting.
- 修正建议: Incorporate functional semantics beyond token overlap, e.g., through data flow analysis.；Use graph-based code representations to capture control and data dependencies.；Leverage method names and signatures to infer high-level purpose.

### case_id=3714 FN lexical_or_api_overlap

- 方法: `main` vs `CheckUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Main method that constructs a POST request with multiple parameters for the RenRen API, sends it, and prints the response line by line.
- B 摘要: Method that takes a URL string, opens an HTTP connection (GET), reads the first line of response, and returns it.
- 静态失败原因: Static models rely on token overlap and surface structure; these functions have very low Jaccard similarity (0.13), different method names, and different parameter handling. The model likely missed the shared high-level intent due to lexical differences.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: Both functions perform the core task of opening an HTTP connection and reading the response, which is a common pattern. BCB may consider this partial functional similarity acceptable for a clone annotation.
- 共享行为: Open an HTTP URL connection；Read from the input stream using BufferedReader
- 行为差异: Function A uses POST with many parameters, B uses URL as argument (likely GET)；A prints multiple lines, B returns the first line only；A is a main method with no return, B returns a String；A handles IOException, B catches Exception broadly
- 修正建议: Enhance training data with more diverse implementations of HTTP reading patterns；Incorporate data flow analysis to capture common I/O operations despite surface differences；Use representations that abstract away API-specific details like parameter construction

### case_id=3715 FN benchmark_preference_bias

- 方法: `buildSiteForEdit` vs `streamContains`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Builds a site for editing by reading XML, processing pages, and writing output.
- B 摘要: Reads an InputStream, converts to UTF-8 string, and asserts it contains a given substring.
- 静态失败原因: The static BERT method likely did not fail; it correctly identified the lack of semantic equivalence. If the BCB label is considered ground truth, then the static method might have missed a very subtle semantic connection, but analysis suggests no meaningful clone relation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to a broad interpretation of Type-4 similarity, possibly considering both as file/string manipulation tasks, but this seems overly inclusive and likely a benchmark annotation error.
- 共享行为: Both involve reading from streams or files into strings.
- 行为差异: A is a large, multi-step transformation; B is a simple assertion utility.；A writes multiple files; B only checks a condition.；A handles XML and property files; B only handles byte streams.；A includes complex control flow and error handling; B is linear.
- 修正建议: Re-evaluate BCB annotation for this pair; it may be a false positive in the benchmark.；Improve static model to be more confident when functions are clearly different in size and purpose.

### case_id=3716 FN boilerplate_overlap

- 方法: `combineJs` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads multiple JavaScript files from URLs, optionally minifies them, and combines them into a single file, returning the modified link element.
- B 摘要: Downloads a WSDL file from a URL, modifies the SOAP address location, and saves it locally, returning the file path.
- 静态失败原因: Static BERT models like GraphCodeBERT rely heavily on token overlap and surface-level similarity. The low Jaccard similarity (0.16) and different method names/contexts made the model miss the underlying structural pattern of URL download and file manipulation, leading to a false negative.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely viewed both functions as clones because they share a common boilerplate pattern of downloading a file from a URL, saving it to a temporary location, and performing some file processing before output. This qualifies as Type-3 or Type-4 clone under BCB's broad similarity criteria.
- 共享行为: Download file from a URL using URL.openStream()；Write downloaded content to temporary files using FileOutputStream；Use java.io.tmpdir for temporary storage；Perform file I/O operations with try-catch blocks for IOException
- 行为差异: combineJs handles multiple JS files and combines them, while getFile handles a single WSDL file；combineJs optionally minifies JS using JavaScriptCompressor; getFile modifies XML using DOM；combineJs concatenates files and writes combined content; getFile modifies and renames files；combineJs returns a Node element; getFile returns a String file path
- 修正建议: Enhance model to recognize high-level structural patterns like download-process-save beyond token overlap.；Incorporate data flow or control flow features to capture common I/O operations.；Use graph-based representation to identify similar file handling structures.

### case_id=3717 FN partial_functionality

- 方法: `main` vs `PageLoader`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Main method that sends a POST request to RenRen API with constructed parameters and prints the response.
- B 摘要: Constructor that reads from a URL via GET and stores the entire response in a field.
- 静态失败原因: Low token overlap (0.117) and significant lexical differences (different method names, API-specific strings, and control flow) misled the static model; it overlooked the abstract semantic similarity of URL fetching.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them Type-4 clones because both share the core behavior of fetching URL content and reading line by line, despite different method signatures and parameter usage.
- 共享行为: Both open a URL connection and read the response line by line；Both handle IOExceptions
- 行为差异: A uses POST method with multiple parameters; B uses GET with no parameters；A prints response to console; B stores response in a field；A is a main method; B is a constructor；A uses specific RenRen API; B is generic
- 修正建议: Use data-flow analysis to capture URL connection and I/O patterns；Incorporate structural similarity for common programming idioms like URL reading；Fine-tune on partial functionality clones

### case_id=3718 FN partial_functionality

- 方法: `copyResource` vs `ExternalDecoder`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using byte-by-byte stream copy.
- B 摘要: Constructor that sets up an external decoder process and starts a thread to copy the input stream to the process's stdin, then closes.
- 静态失败原因: Low token overlap (0.0769) and dissimilar method signatures/structures; static models focusing on lexical or surface-level similarity would likely miss the abstract shared copy behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both methods ultimately perform a stream copy operation, which is a common high-level pattern. The differences in source/target and concurrency might be considered variations of Type-4 functional similarity.
- 共享行为: Both involve copying data from an input source to an output destination using streams.
- 行为差异: Function A copies to a file; function B copies to a process's stdin.；Function A uses a simple byte loop; function B uses IOUtils.copy and threading.；Function A handles source as URL or file; function B takes an InputStream directly.；Function A is synchronous; function B is asynchronous (starts a new thread).
- 修正建议: Use program dependency graphs or data flow analysis to capture core operations like copy/read/write.；Incorporate API call patterns (e.g., IOUtils.copy) as semantic features.；Consider multi-level representations combining structure and high-level intent.

### case_id=3719 FP lexical_or_api_overlap

- 方法: `read` vs `readZoneIDs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads camera log records from a URL, parses lines into CameraLogRecord objects, adds to list, and sorts.
- B 摘要: Reads zone IDs from a resource URL, parses lines as integers, and returns a HashSet.
- 静态失败原因: Static BERT model over-relied on surface-level API similarities (BufferedReader/LineNumberReader, openStream, while readLine) and control flow, missing the semantic differences in data transformation and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because, despite similar I/O structure, the domain-specific parsing and output types indicate different functionality.
- 共享行为: Both open a URL stream and read lines sequentially.
- 行为差异: Different parsing: CameraLogRecord vs integer.；Different output: sorted list vs HashSet.；Different error handling: logging vs printStackTrace.；Different return: void vs HashSet<Integer>.
- 修正建议: Train on more diverse negative examples with shared I/O but different business logic.；Incorporate data-flow or type information to distinguish parsing targets.；Use contrastive learning to emphasize semantic differences over structural similarities.

### case_id=3720 FP long_range_semantics

- 方法: `main` vs `parseContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads a Prolog file, parses it, and generates adapter JAR files.
- B 摘要: Parses HTML content, extracts metadata, links, and language information.
- 静态失败原因: The model may have been misled by common structural patterns: both have try-catch blocks, file reading, string operations, and loops. The token Jaccard is low, but the model might have overgeneralized from similar sequences in training, or missed the semantic context due to long code length.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled non-clone because the two functions have completely different purposes (main vs. parseContent), different inputs/outputs, and no meaningful overlap in logic beyond basic programming constructs.
- 共享行为: Both perform file/data parsing；Both handle exceptions with try-catch blocks；Both use I/O operations
- 行为差异: Function A is a command-line tool main method for generating adapters from Prolog files; Function B is an overridden method for parsing HTML content in a web crawling context；Function A writes JAR files and assembles classes; Function B extracts fields and adds them to a document；Function A uses Prolog grammar and ClassWriter; Function B uses HTML DOM and provider abstraction
- 修正建议: Improve model's ability to capture long-range dependencies and overall functionality；Incorporate cross-function structural comparison (e.g., control flow graphs) to differentiate semantics；Use contrastive learning to emphasize functional vs. non-functional similarities

### case_id=3721 FN boilerplate_overlap

- 方法: `modifyApplicationMessage` vs `copyToDir`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a specific property key-value pair in a locale-specific properties file, copying from an English template if necessary.
- B 摘要: Copies the current file to a specified directory, creating intermediate directories if needed.
- 静态失败原因: Static BERT models rely on token-level embeddings and may miss high-level structural similarity. The functions share common I/O boilerplate (File, InputStream, try-catch) but have different domain-specific logic (property parsing vs. binary copy). The model correctly saw they are semantically different, but BCB's broader definition considers them clones, so the model failed to align with BCB's preference.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled these as clones due to broad Type-4 similarity: both are file manipulation functions that read from one file and write to another, with similar control flow (create file, open streams, loop, close). The specific operations differ but the overarching pattern is considered similar by some annotation guidelines.
- 共享行为: Both perform file I/O operations with streams；Both handle exceptions with try-catch；Both use File objects and stream classes
- 行为差异: A modifies content of a properties file; B copies a file byte-by-byte；A involves text parsing and manipulation; B is pure binary copy；A has conditional logic for file existence and locale; B has early return if source parent equals target；A uses Reader/Writer; B uses InputStream/OutputStream
- 修正建议: Incorporate structural similarity metrics like AST-based matching to capture I/O patterns；Use contrastive learning to separate true semantic clones from boilerplate overlap；Fine-tune on BCB's annotation guidelines that tolerate partial functionality similarity

### case_id=3722 FN benchmark_preference_bias

- 方法: `copyResource` vs `uncaughtException`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a resource from a URL or file to a destination file.
- B 摘要: Handles an uncaught exception by showing an error dialog and optionally launching a URL.
- 静态失败原因: Very low token overlap and different method names lead to low similarity; the model likely relies on surface-level lexical features and misses abstract functional similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as resource-copying or exception-handling utilities, albeit in different domains, fitting a broad Type-4 clone.
- 共享行为: Both involve I/O operations (file/stream for A, clipboard/URL for B).；Both handle resources that need to be closed/disposed.
- 行为差异: A copies a file; B displays a dialog and launches a URL.；A uses byte-by-byte copying; B uses GUI components and clipboard.；A throws Exception; B catches Exception internally.
- 修正建议: Train on a larger dataset of abstract functional patterns.；Incorporate structural or data-flow information to capture resource management similarities.；Adjust threshold to accept broader functional equivalence for low-overlap pairs.

### case_id=3723 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `postData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads integers from a file resource specified by zoneFileName, parses each line as an integer, and returns a set of zone IDs.
- B 摘要: Sends an HTTP POST request with data to a given host and protocol, and reads the response, ignoring it.
- 静态失败原因: The static BERT model may have focused on shared API tokens like 'URL', 'InputStreamReader', 'readLine', and exception handling, while ignoring the different overall purpose and control flow. The token Jaccard is low, but the model may have learned to associate similar sequences of API calls as clones due to training data bias.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotation typically labels pairs with different functionality as non-clones, even if they share some common API usage or boilerplate code. Since one function reads IDs from a file and the other performs HTTP POST, they are clearly different functionalities.
- 共享行为: Both use URL and URL-related classes to access network resources；Both use InputStreamReader to read from streams；Both have a loop that reads lines from an input stream
- 行为差异: Function A reads from a local resource file, function B sends an HTTP POST request and reads the response；Function A parses lines as integers and adds to a set, function B does not parse the response and ignores it；Function A returns a HashSet, function B is void and throws Exception；Function B sets up HTTP connection properties and writes data, function A only reads
- 修正建议: Incorporate structural or dataflow features to differentiate reading vs. writing operations；Use contrastive learning with hard negatives that have API overlap but different semantics；Add domain-specific knowledge about HTTP vs file I/O

### case_id=3724 FN partial_functionality

- 方法: `checkInputStream` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads an input stream into a byte array and compares it byte-by-byte with a given byte array.
- B 摘要: Launches a NexOpen project configuration, handling Maven POM files, copying resources, and setting properties.
- 静态失败原因: Static BERT models rely on token overlap and structural similarity; the low token Jaccard (0.062) and different method structures led to a correct non-clone prediction, but BCB's broad definition may consider it a clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as clone due to the shared pattern of using IOUtils.copy and ByteArrayOutputStream, considering it a partial functionality clone (Type-4), but the overall semantic similarity is weak.
- 共享行为: Both use IOUtils.copy to read an InputStream into a ByteArrayOutputStream.
- 行为差异: A is a simple utility for stream comparison; B is a complex launch method with many unrelated steps.；A compares stream content to a given array; B processes configurations and manipulates files.；The shared code snippet is a minor part of B's overall functionality.
- 修正建议: Incorporate dataflow analysis to capture whole-function behavior.；Filter out trivial common API usage patterns that do not indicate semantic equivalence.；Use models that better distinguish utility code from core functionality.

### case_id=3725 FP lexical_or_api_overlap

- 方法: `main` vs `execute`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file, generates adapter classes from it, and writes them to a JAR file.
- B 摘要: Saves a HomeMap object to a database, copies an uploaded image file to a directory, and returns a list.
- 静态失败原因: The static BERT model likely overemphasized token-level similarities such as file I/O classes (File, FileOutputStream) and exception handling pattern (e.printStackTrace()), ignoring the larger context and different purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely marked as non-clone because the functions have completely different functionality and no shared domain logic.
- 共享行为: Both perform file I/O operations；Both handle IOExceptions with printStackTrace
- 行为差异: Different overall purpose (adapter generation vs. image saving)；Different control flow complexity (one has loops, the other simple sequential)；Different input/output (command-line args vs. form submission)
- 修正建议: Improve token embeddings to distinguish different file operation contexts；Incorporate structure-aware attention like data flow or control flow graphs

### case_id=3726 FP boilerplate_overlap

- 方法: `run` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A void method that reads from a fixed URL and discards all data, essentially a no-op.
- B 摘要: A method that opens a YouTube URL, parses the response for a fullscreen URL, extracts video parameters, constructs a new URL, and returns it.
- 静态失败原因: The model likely focused on surface-level API usage (URL, BufferedReader, try-catch) and missed the significant semantic differences in data processing and return values. The high overlap in boilerplate code misled the model.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label these as non-clones because the overall functionality is completely different despite sharing some I/O boilerplate. The methods have different names, return types, and purposes.
- 共享行为: Both create a URL object and open a connection.；Both use BufferedReader and InputStreamReader to read lines.；Both have try-catch blocks for exceptions.
- 行为差异: Code a returns void; code b returns a String.；Code a uses a hardcoded localhost URL; code b uses a member variable ytUrl.；Code a discards all read lines; code b searches for 'fullscreenUrl' and parses it.；Code b sets progress bar, prints debug info, and constructs a new URL.
- 修正建议: Incorporate control-flow and data-flow analysis to detect whether read data is actually used.；Consider method signatures (return type, parameters) as a strong differentiator.；Use graph-based representations that capture data dependencies more explicitly.

### case_id=3727 FN partial_functionality

- 方法: `main` vs `displayDiffResults`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, unzips it, and extracts entries to files.
- B 摘要: Generates an HTML diff report, copies a temporary file to the output stream, and launches a browser.
- 静态失败原因: The token overlap is low (Jaccard 0.135), and static BERT models rely on surface-level token similarity, missing the abstract I/O pattern due to different vocabulary and structure.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions perform a data copy loop (reading from an input stream and writing to an output stream) using a buffer, which represents a reusable I/O pattern even though the overall task differs.
- 共享行为: Both read from an InputStream and write to an OutputStream using a buffer；Both use a while loop with read() and write() to copy data；Both close streams and handle IOExceptions
- 行为差异: A downloads and unzips an archive; B generates an HTML report and copies a file；A writes to multiple files; B writes to a single output stream；A uses ZipInputStream; B uses FileInputStream；B manipulates tables and strings; A does not
- 修正建议: Use data-flow analysis to capture the read-write loop structure；Introduce patterns for I/O copy idioms；Consider abstract syntax tree (AST)-based features for loop bodies

### case_id=3728 FN benchmark_preference_bias

- 方法: `testCopyUnknownSize` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Unit test that copies a byte array input stream to an output stream and verifies the copy size and data.
- B 摘要: Complex method that builds an HTML site for editing by processing XML, transforming with XSLT, and writing output files.
- 静态失败原因: The static model correctly identified non-clone based on divergent semantics; BCB label appears erroneous or overly inclusive.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to a broad interpretation of 'copy' operations, but the functions share little actual semantics.
- 共享行为: Both involve reading input and writing output using Java I/O streams.
- 行为差异: Function A is a simple unit test with a few lines; Function B is a large method (over 100 lines) with complex file and XML operations.；Function A uses in-memory streams (ByteArrayInputStream/OutputStream); Function B uses FileInputStream, FileWriter, and custom FileSystem class.；Function A performs no data transformation; Function B performs XSLT transformations and string replacements.；Function A asserts correctness; Function B writes files to disk and handles many exceptions.
- 修正建议: Re-evaluate the BCB annotation for this pair; likely a mislabel.；Consider removing or correcting such pairs in the benchmark.

### case_id=3729 FN benchmark_preference_bias

- 方法: `process` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Processes a template with a model and writes generated output to a file, handling different template types (Freemarker, XSLT, copy).
- B 摘要: Downloads a WSDL file from a URL, modifies the SOAP address endpoint, and saves the modified WSDL to a temporary file.
- 静态失败原因: The model likely relied on token-level similarity (low Jaccard) and missed the abstract file-processing pattern. It was not trained to recognize partial functionality clones or high-level behavioral similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider these clones because both are file-processing utilities that read input, perform a transformation, and write output, sharing similar resource management and error handling patterns. However, this is a very broad interpretation and not typical for BigCloneBench.
- 共享行为: Both involve file I/O operations (reading input streams, writing output streams).；Both catch and handle I/O exceptions with custom exceptions.；Both output debug information (System.out or logging).
- 行为差异: A performs code generation from templates, while B downloads and modifies XML content.；A handles multiple template types (Freemarker, XSLT, copy) with complex conditional logic; B only handles WSDL download and endpoint replacement.；A's output is generated from a model and template, B's output is a modified copy of downloaded content.；A writes to a destination path based on package name or template path; B writes to a temporary directory.
- 修正建议: Train models to detect broader semantic categories like 'file processing with transformation'.；Use AST-based features to capture common structural patterns in resource handling.；Incorporate data flow analysis to identify input-output transformation chains.

### case_id=3730 FN benchmark_preference_bias

- 方法: `split` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Splits a FASTA file into multiple partitions based on size limits.
- B 摘要: Modifies a locale-specific properties file by updating or adding a key-value pair.
- 静态失败原因: The static model correctly predicted non-clone, aligning with strict semantics; the BCB label is erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Likely a benchmark labeling error, as there is no meaningful functional similarity beyond trivial file I/O.
- 共享行为: Both involve file reading and writing operations.
- 行为差异: Entirely different purpose: file partition vs. properties editing.；Different file formats: FASTA (biological sequences) vs. Java properties.；Different logic: complex state machine vs. line-by-line string manipulation.
- 修正建议: Correct the BCB annotation for this pair to non-clone.

### case_id=3731 FP lexical_or_api_overlap

- 方法: `getUser` vs `createHTML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from DB or falls back to reading a config file and saves to DB.
- B 摘要: Generates an HTML page header or dashboard content based on request type, reading a CSS file and querying DB.
- 静态失败原因: Likely overemphasized the shared use of URL, BufferedReader, and InputStreamReader patterns, mistaking structural similarity for semantic equivalence despite low token overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the overall functionality is completely different: one is user retrieval, the other is HTML generation. Any shared IO patterns are incidental boilerplate.
- 共享行为: Both use URL, InputStream, BufferedReader to read a resource line by line；Both have try-catch blocks for IO exceptions
- 行为差异: Function A returns a User object; Function B returns an HTML string；Function A handles user authentication; Function B generates UI markup；Function A uses StringTokenizer to parse config lines; Function B uses SQL queries and switch-case logic
- 修正建议: Increase weight on dataflow and functional outcome；Use API-usage patterns less discriminatively；Incorporate semantic role labeling or intent detection

### case_id=3732 FP boilerplate_overlap

- 方法: `main` vs `gerarTutorialPage`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter classes for a Prolog program and bundles them into a JAR file.
- B 摘要: Generates a tutorial website by copying CSS files and writing HTML content.
- 静态失败原因: Static BERT models may overemphasize shared boilerplate patterns like try-catch blocks, System.out.println, and File operations, while missing the semantic divergence due to long-range dependencies and domain-specific libraries.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates these as non-clones because they implement entirely different functionality with no common purpose or code reuse.
- 共享行为: Both perform file operations；Both use try-catch blocks for exception handling；Both print status messages to the console
- 行为差异: Function A parses Prolog source and generates Java adapters; Function B copies CSS files and writes HTML pages；Function A constructs a JAR file with classes and resources; Function B creates a directory structure for a website；Function A uses complex libraries (e.g., PrologParser, ClassWriter); Function B uses simple file I/O and channels；Function A has command-line argument parsing; Function B has no input arguments
- 修正建议: Incorporate data flow and control flow graphs to capture program semantics；Use AST-based representations that highlight structural differences；Apply a more domain-aware tokenization or filtering of common keywords

### case_id=3733 FN partial_functionality

- 方法: `sendExceptionToServer` vs `callApiPost`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST with URL-encoded parameters.
- B 摘要: Calls an API via HTTP POST with custom headers, parameters, and checks response code.
- 静态失败原因: Static BERT models rely on token-level similarity, which is low (0.158). They miss the abstract HTTP POST pattern due to syntactic differences like method names, parameter types, and error handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers both as HTTP POST clients with similar core functionality, despite differing implementations. The low token overlap is outweighed by the shared high-level behavior.
- 共享行为: Both perform HTTP POST requests with URL-encoded data.；Both set doOutput to true and write data to the output stream.
- 行为差异: A builds data manually using StringBuilder; B uses a helper method getParametersString.；A reads response line by line and checks for 'success'; B checks HTTP status code and returns an InputStream.；A uses URLConnection; B uses HttpURLConnection with additional settings like timeout and headers.；A prints output to console; B throws a custom exception on failure.
- 修正建议: Incorporate dataflow or graph-based representations to capture HTTP connection sequences.；Use API call embedding to recognize common patterns like URL.openConnection() and setDoOutput() as semantically similar.

### case_id=3734 FP boilerplate_overlap

- 方法: `doVersionCheck` vs `handleHandshake`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches version information from a URL and parses build numbers.
- B 摘要: Validates and processes a Minecraft server handshake by querying an authentication URL.
- 静态失败原因: Overlap in boilerplate code (URL, BufferedReader, try-catch) and method names suggesting network operations likely misled the model to ignore deeper semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considered these non-clones because they perform distinct tasks with different I/O and control flow, despite sharing a common pattern of URL reading.
- 共享行为: Both open a URL and read input stream using BufferedReader
- 行为差异: Different purpose: version checking vs. game authentication；Different URL construction and parsing logic；Different conditional branches and final actions
- 修正建议: Incorporate control flow or data flow analysis to capture semantics；Add context from class or surrounding code to disambiguate purpose

### case_id=3735 FN partial_functionality

- 方法: `import_hints` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a hint file from local or URL, parses piece data, and places hints on a game board, returning boolean success.
- B 摘要: Reads a file from local file or classpath resource and returns its entire content as a single string, exiting on error.
- 静态失败原因: Low token overlap (0.228) and different method names/return types led the model to focus on lexical differences, missing the structural similarity in the file-reading infrastructure.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the shared file-access pattern (local vs URL, BufferedReader, exception handling) as the primary functionality, viewing the rest as minor variations, thus labeling as a broad Type-3/Type-4 clone.
- 共享行为: Both read text files using BufferedReader；Both have fallback logic: first try local file, then use URL/classpath；Both handle IOException with try-catch
- 行为差异: A parses structured data and updates game board state; B concatenates lines into a string；A returns boolean; B returns string；A handles errors by returning false; B prints and calls System.exit()；A uses StringTokenizer for parsing; B uses StringBuffer for concatenation
- 修正建议: Enhance training data with more partial-functionality clones；Incorporate graph-based representations to capture control flow and data flow patterns；Use contrastive learning to emphasize shared sub-behaviors over lexical differences

### case_id=3736 FP lexical_or_api_overlap

- 方法: `readData` vs `recurseFiles`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses comma-separated strings to populate configuration sets and maps, then reads a file line by line to build lookup tables for Tibetan transliteration.
- B 摘要: Recursively traverses a directory tree and adds non-zip files to a Zip archive output stream.
- 静态失败原因: Despite low token overlap, the static BERT model may have been misled by generic tokens like 'IOException', 'File', 'while', and common API names (e.g., 'HashSet', 'StringTokenizer') appearing in both codes, or by the presence of exception handling and loops, leading to over-generalization.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have no common functionality or shared purpose; these two functions are completely different in goal and behavior.
- 共享行为: Both are static methods performing I/O operations；Both iterate over collections of items
- 行为差异: readData initializes data structures from string fields and parses a file; recurseFiles writes files to a zip archive；readData uses StringTokenizer and manual parsing; recurseFiles uses File, ZipArchiveOutputStream, and IOUtils；readData modifies multiple static HashSets and Maps; recurseFiles writes to a ZipArchiveOutputStream
- 修正建议: Improve training data to distinguish data parsing from file archiving tasks；Incorporate structural or dataflow features to capture function purpose；Use type-aware embeddings to differentiate classes like StringTokenizer vs. ZipArchiveOutputStream

### case_id=3737 FP lexical_or_api_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter code from a Prolog file by parsing, visiting facts, and assembling classes.
- B 摘要: Copies a file from source to destination using a buffer.
- 静态失败原因: The static model likely overemphasized superficial lexical overlaps like 'File', 'IOException', and 'try-catch', despite low Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have entirely different purposes, even if they share some file I/O.
- 共享行为: Both involve file I/O operations
- 行为差异: Function A is a complex adapter generation pipeline; Function B is a simple file copy.；Function A uses multiple libraries and file parsing; Function B only uses basic file streams.；Function A has extensive error handling and debugging; Function B throws exceptions.
- 修正建议: Incorporate dataflow analysis to distinguish I/O patterns.；Use finer-grained API usage modeling.；Leverage method name semantics (e.g., 'main' vs 'copyFile').

### case_id=3738 FN partial_functionality

- 方法: `getHTML` vs `executeHttpGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens an HTTP connection to a URL, reads the response with specified encoding, optionally writes it to a file, and returns the HTML string.
- B 摘要: Executes an HTTP GET using Apache HttpClient, reads the response, and returns a JSON object constructed from the response string.
- 静态失败原因: Static BERT models often rely on token-level similarity and may not capture high-level structural or functional similarity. The token Jaccard is 0.24, indicating low lexical overlap. The models may focus on exact method names and API calls (e.g., 'HttpURLConnection' vs 'HttpGet') and miss the shared pattern of HTTP GET request reading. Additionally, the different return types and additional parameters may confuse the model into thinking they are different.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may classify these as clones because both functions implement the core pattern of fetching a remote resource via HTTP GET and processing the response into a string, which is a common boilerplate. The differences in library choice, error handling, and output format are considered superficial for Type-3/Type-4 similarity.
- 共享行为: Perform HTTP GET request；Read response line by line；Build string from response；Return data derived from response
- 行为差异: Different HTTP client libraries (HttpURLConnection vs Apache HttpClient)；A has optional file output；B parses response as JSON, A returns raw string；A sets User-Agent header
- 修正建议: Enhance model with structural program analysis to recognize common HTTP GET patterns regardless of library；Use dataflow analysis to abstract I/O operations；Train on more Type-3/Type-4 examples with low lexical overlap but high functional similarity

### case_id=3739 FN partial_functionality

- 方法: `doTransfer` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A method that acts as an HTTP proxy, forwarding request headers and body to a target URL and returning the response.
- B 摘要: A method that downloads an OPDS catalog or book from an HTTP URL, handling redirects, file naming, and pagination.
- 静态失败原因: The static BERT model likely relied on lexical overlap (e.g., HttpURLConnection, getInputStream, setRequestProperty) and common control structures, missing the divergent high-level semantics. The low token Jaccard (0.1545) indicates sparse lexical matching, but the shared API calls may have caused false negative due to insufficient context.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as Type-4 clones because both involve HTTP communication, reading/writing streams, and are from similar domains (web/data transfer). The annotation might prioritize broad functional similarity over exact implementation details.
- 共享行为: Both use HttpURLConnection to make HTTP requests；Both set request properties on the connection；Both read from input streams (request body for A, response body for B)；Both handle HTTP responses and write to output streams (servlet response for A, file or parser for B)
- 行为差异: A forwards the incoming request to a target URL, while B initiates a download from a hardcoded or derived URL；A copies all request headers, B sets only specific headers (User-Agent, Referer)；A handles different HTTP methods (via method parameter), B always uses GET；A sends the request body from the original request, B does not send any request body
- 修正建议: Incorporate graph-based representations (e.g., AST, PDG) to capture control and data flow differences；Use contrastive learning to distinguish proxy vs. downloader semantics；Expand training data with diverse HTTP usage patterns；Leverage code summarization to capture overall intent

### case_id=3740 FP boilerplate_overlap

- 方法: `loadExistingAntlibs` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads Ant library definitions from classpath resources.
- B 摘要: Performs Google image search, parses HTML, and displays the first image.
- 静态失败原因: Model was misled by boilerplate I/O code patterns (try-catch, streams, BufferedReader) and structural similarities, ignoring semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: Functions have no functional overlap beyond generic I/O; BCB would not consider them clones
- 共享行为: Both use URL, InputStream, BufferedReader to read data from an external source；Both iterate over lines of text input
- 行为差异: Function A loads Ant libraries; Function B performs image search；Function A reads from classpath; Function B reads from HTTP；Function A calls loadAntLib; Function B updates UI and parses HTML；Exception handling: A wraps in RuntimeException; B shows error dialog
- 修正建议: Incorporate data flow analysis to capture actual operations；Use function signatures and docstrings more heavily；Train with more hard negatives with similar boilerplate but different functionality

### case_id=3741 FP boilerplate_overlap

- 方法: `downLoadZippedFile` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Downloads a zipped file from a URL, saves it to a temporary file, unzips it to a destination directory, and returns the local URL.
- B 摘要: Reads a configuration file (likely tibwn.ini), parses colon-delimited lines, and initializes multiple sets and hash maps for Tibetan/Sanskrit encoding conversion.
- 静态失败原因: The model likely overemphasized common structural patterns like try-finally with resource closing, ignoring the fundamentally different business logic and data flow. The low token Jaccard indicates little lexical overlap, but the model may have been misled by generic I/O and exception handling constructs.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators would label this as non-clone because the two functions have completely different purposes (downloading/unzipping vs. configuration parsing) despite some shared boilerplate (try-finally, resource handling).
- 共享行为: Both use try-finally blocks for resource cleanup；Both perform file I/O operations；Both handle exceptions
- 行为差异: A downloads from network; B reads a local file；A performs zip extraction; B parses structured text data；A returns a URL; B returns void and modifies global state；A uses IOUtils.copy; B uses manual line-by-line parsing
- 修正建议: Incorporate data flow analysis to distinguish different I/O operations；Use type-aware embeddings to differentiate network streams from file readers；Include negative examples of boilerplate-only similarity during training

### case_id=3742 FN partial_functionality

- 方法: `copyResource` vs `gzip`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using byte-by-byte reading.
- B 摘要: Compresses a file into a GZIP file using buffered reading.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token-level similarity, which is low (Jaccard 0.241). They fail to capture high-level structural patterns like the stream-copy idiom and are misled by differing method names, hardcoded paths, and specific library calls (GZIPOutputStream vs FileOutputStream).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions implement a common I/O stream-copy pattern with a read-write loop and stream closures, and the structural similarity (e.g., both use FileInputStream/FileOutputStream) is considered more important than the specific functionality (plain copy vs compression) in clone detection tasks.
- 共享行为: Both open an input stream and read bytes in a loop；Both write bytes to an output stream；Both close input and output streams
- 行为差异: copyResource reads byte by byte; gzip reads into a buffer；copyResource outputs a plain file; gzip outputs a GZIP compressed file；copyResource handles URL and file sources; gzip only reads from a hardcoded file path；gzip includes debug prints and file existence check
- 修正建议: Incorporate structural or AST-based features to recognize common I/O patterns；Use models that focus on control flow and data flow similarity rather than token overlap；Augment training data with examples of functionally similar but token-divergent clones

### case_id=3743 FN partial_functionality

- 方法: `callService` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Makes an HTTP GET request to a constructed URL, reads the response line by line, and stores the result in an instance variable, handling URL and I/O exceptions.
- B 摘要: Invokes a remote service via HTTP POST with JSON payload, reads and deserializes the JSON response, and implements retry logic on connection timeout.
- 静态失败原因: Static BERT/CodeBERT methods rely on token overlap and surface-level features; the low Jaccard similarity and different API calls (URL vs HttpClient) lead to a low similarity score, causing a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled them as clones because both perform the high-level task of calling a remote service and processing the HTTP response, considering differences in HTTP method, libraries, and retries as implementation details.
- 共享行为: Both make HTTP requests and read the response line by line
- 行为差异: A uses GET, B uses POST；A returns void, B returns Object；B has retry logic, A does not；B handles JSON serialization/deserialization, A does not
- 修正建议: Incorporate control flow or dataflow analysis to capture the common pattern of HTTP request and response handling；Use natural language descriptions or API documentation embeddings to supplement code tokens

### case_id=3744 FP partial_functionality

- 方法: `readData` vs `readAndRewrite`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Initializes multiple sets and maps by parsing comma-separated string constants using StringTokenizer and populating collections with token values.
- B 摘要: Reads a DICOM image file, parses its metadata, reads pixel data, and writes the dataset to another DICOM file.
- 静态失败原因: Static BERT may have overfitted to the method name prefix 'read' and the presence of while loops and set operations, overlooking the completely different APIs and input-output context. The low token Jaccard (0.03) suggests the model relied on structural patterns rather than lexical content.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the two functions perform entirely different tasks with no overlap in semantics or domain, despite both involving 'reading' and data structure population.
- 共享行为: Both are private static void methods that perform a reading-like operation and populate data structures.
- 行为差异: Input source: code_a reads from static string variables; code_b reads from a File.；Output: code_a populates in-memory collections; code_b writes to a File.；Domain: code_a is initialization for text processing; code_b is medical image I/O.；Exception handling: code_a has no declared exceptions; code_b throws IOException.
- 修正建议: Incorporate information about API calls and their domains (e.g., DICOM vs StringTokenizer).；Use input/output types and signatures to distinguish data flow.；Add training examples with low token overlap but similar method names to reduce false positives.

### case_id=3745 FN benchmark_preference_bias

- 方法: `sendErrorMessage` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Sends an error notification by email with zipped log file attachment.
- B 摘要: Launches a configuration for a NexOpen project, processing XML files and setting properties.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on lexical and syntactic overlap, which is very low (token Jaccard 0.054), so it correctly predicted non-clone. The model did not capture the possible broad structural similarity that BCB might have used; thus the model's prediction aligns with semantic judgment.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have considered these clones due to partial functionality overlap (e.g., both involve file I/O and exception handling) or because they both override/implement interface methods, but the semantic gap is large and the shared behavior is too generic; typical BCB clones require more specific similarity.
- 共享行为: Both involve file I/O operations；Both use try-catch blocks for exception handling；Both perform conditional checks before proceeding
- 行为差异: sendErrorMessage sends an email with a zip attachment; launch does not send emails；sendErrorMessage is shorter and simpler; launch is much longer and complex, involving multiple file reads and writes；sendErrorMessage deals with user management and logging; launch deals with project configuration and reverse engineering
- 修正建议: Ensure training data accurately reflects BCB's annotation criteria; if BCB really labels such pairs as clones, the model should be trained with more emphasis on structural patterns like try-catch and file I/O；Incorporate high-level task similarity (e.g., both are 'setup' or 'notification' methods) via code summarization or topic modeling；Use a more flexible notion of clone that includes functional similarity beyond lexical matching

### case_id=3746 FN benchmark_preference_bias

- 方法: `main` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its entries to files.
- B 摘要: Converts an ACRNEMA medical image stream to DICOM format.
- 静态失败原因: Static BERT or GraphCodeBERT correctly predicted non-clone due to low token overlap and different method names/structures, so it did not fail; the BCB label is likely incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as file I/O operations but overlooked the vastly different domains and specific processing, leading to a mislabel as clone.
- 共享行为: Both read from an input stream and write to an output stream.
- 行为差异: A extracts a ZIP archive; B parses and converts medical image data.；A uses ZipInputStream and writes entry files; B uses DICOM-specific parsing and output.；B has complex condition checks and pixel data handling; A is straightforward extraction.
- 修正建议: Re-evaluate the BCB label for this pair; consider it a false positive in the benchmark.；Improve dataset curation to avoid labeling clearly different functions as clones.

### case_id=3747 FP lexical_or_api_overlap

- 方法: `run` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a vector tile from a URL, parses its pieces into a geometry collection, and adds it to a data loader.
- B 摘要: Downloads an RDF model from a URL and reads it into a Model object.
- 静态失败原因: Static BERT may have focused on surface-level API overlap (URL, InputStream, exceptions) and overlooked the distinct semantic purposes and output types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely marks as non-clone because the core functionality (parsing and output) differs significantly, even though the URL-reading boilerplate is similar.
- 共享行为: Both open a URL connection and read an input stream.；Both handle MalformedURLException and IOException.
- 行为差异: Function A supports file and HTTP protocols; B only HTTP.；Function A parses geoJSON and creates geometry objects; B reads RDF data into a Model.；Function A adds to a data loader; B returns the Model.；Function A has additional synchronization logic.
- 修正建议: Incorporate method name or class context as features.；Use dataflow analysis to distinguish different processing paths after input reading.；Add more weight to the specific domain of the output (e.g., Model vs Geometry).

### case_id=3748 FN partial_functionality

- 方法: `getResourceAsStream` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource via URL, caches it locally, and returns an InputStream.
- B 摘要: Reads a DICOM file, parses its pixel data, and writes it to another file.
- 静态失败原因: Static BERT models rely on lexical and syntactic similarity, which is low (token Jaccard 0.0786). They miss the abstract I/O pattern that BCB captures, leading to false negative prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers these as Type-4 clones due to similar high-level structure: open input, read data, write to output, close streams, with error handling. Both are I/O-centric methods that copy or transform data from one location to another.
- 共享行为: Both perform I/O operations: reading from an input source and writing to a local file；Both use buffered streams；Both have logging statements
- 行为差异: A handles HTTP and caching logic; B uses DICOM-specific parsing and rewriting；A returns an InputStream; B is void；A has complex caching decisions; B has DICOM-specific data processing
- 修正建议: Incorporate structural or dataflow features to recognize common I/O patterns；Use method-level semantic embeddings that capture high-level behavior

### case_id=3749 FN benchmark_preference_bias

- 方法: `getFile` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file, optionally modifies the endpoint in the XML, and returns the file path.
- B 摘要: Reads a DICOM image file, parses it, and writes a copy to another file, effectively re-encoding the image data.
- 静态失败原因: Static models like GraphCodeBERT rely on token and AST similarity; here token Jaccard is very low (0.072) and AST structures diverge (XML vs DICOM), so it correctly predicted non-clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered this a Type-4 clone based on broad functionality of reading, modifying, and writing files with streams, despite the domains being entirely different.
- 共享行为: Both perform file I/O operations with exception handling.
- 行为差异: Function A deals with WSDL/XML files and modifies endpoint attributes, while B handles DICOM medical images with pixel data.；A uses NIO channels and XML parsing, B uses DICOM-specific libraries and ImageIO streams.；A conditionally downloads if file missing; B always reads and writes.；A returns a file path; B returns void.
- 修正建议: Re-evaluate BCB labeling for cross-domain pairs; consider tightening clone criteria to require domain consistency.；Alternatively, if keeping BCB labels, adjust model training to recognize broader functional patterns like file I/O with streams.

### case_id=3750 FP boilerplate_overlap

- 方法: `perform` vs `createVendorSignature`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A Struts action that processes a classification request by sending XML to a URL, parsing the response, and forwarding based on status.
- B 摘要: Generates an MD5-based RSA digital signature for a vendor using a private key.
- 静态失败原因: The static BERT model likely overemphasized lexical overlaps such as common boilerplate (try-catch, variable declarations) and API tokens (getBytes, Exception), leading to a false positive despite very low token Jaccard.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the methods have no shared functionality; they belong to completely different domains (web MVC vs crypto). BCB's broad Type-4 still requires some meaningful correspondence, which is absent here.
- 行为差异: Method purpose: web request handling vs cryptography；Input/output: HTTP request/response vs internal signature generation；Control flow: conditional branching and error reporting vs simple try-catch；External dependencies: Struts framework vs Java security API
- 修正建议: Train the model to recognize structural patterns beyond local token matches.；Incorporate dataflow or control-flow analysis to capture semantic intent.；Use contrastive learning to better distinguish unrelated methods.

### case_id=3751 FN benchmark_preference_bias

- 方法: `handle` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handle log file rotation, compression, and archiving.
- B 摘要: Build a site for editing by transforming XML and writing output files.
- 静态失败原因: The static model likely failed because it relied on low token overlap and surface-level syntax, and could not detect a hidden semantic similarity that BCB claimed.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider these clones due to superficial similarities like both using file streams, having long method bodies, and performing I/O operations, despite different business logic.
- 共享行为: Generic file I/O operations
- 行为差异: Primary purpose is entirely different: log rotation vs site generation；Log rotation uses GZIP compression and archiving; site generation uses XML transformation；Log rotation deletes original log file; site generation writes multiple output files；Different method signatures and parameters
- 修正建议: Improve annotation guidelines to avoid labeling unrelated methods as clones；Use dataflow analysis to capture semantic differences beyond file I/O

### case_id=3752 FN partial_functionality

- 方法: `copyResource` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using byte stream.
- B 摘要: Writes and reads a fixed string to a file, demonstrating encoding and ByteBuffer usage.
- 静态失败原因: Static BERT likely relied on low token overlap (0.12) and different API usage, failing to capture any high-level I/O semantic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might label this as a clone due to broad Type-4 similarity where both involve file I/O and exception handling, but the core functionality differs significantly.
- 共享行为: Both perform file I/O operations；Both handle exceptions with throws Exception
- 行为差异: A copies arbitrary data from source to destination; B writes and reads a specific string with encoding manipulations；A uses InputStream/OutputStream; B uses FileChannel and ByteBuffer；A performs a simple byte-by-byte copy; B performs multiple read/write operations with buffer flipping
- 修正建议: Improve representation to differentiate between copying and encoding demos；Use data flow analysis to capture read-write patterns

### case_id=3753 FP lexical_or_api_overlap

- 方法: `copy` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copy a file from source to destination using FileChannel.
- B 摘要: Handle action events to set GUI preferences like file paths for external tools and display settings.
- 静态失败原因: The static model likely overemphasized superficial token matches like 'File', 'filename', and 'getChannel' (though getChannel is only in A, but B has JFileChooser and File objects). Long method B with many API calls may have caused the model to misjudge similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotations typically consider whole-function semantics; these functions have entirely different purposes and no significant shared behavior, so they would be labeled non-clone.
- 共享行为: Both involve file operations (copy vs. file chooser dialog)
- 行为差异: Function A is a pure file copy utility; Function B is a GUI event handler with multiple conditional branches.；Function A returns void and focuses on I/O; Function B modifies UI components and stores preferences.；No overlap in control flow or intended output.
- 修正建议: Improve tokenization or weighting to downplay common API keywords.；Incorporate structural or flow analysis to differentiate between file copy and event handling.

### case_id=3754 FN benchmark_preference_bias

- 方法: `login` vs `loadExistingAntlibs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Logs in to LOLA by posting email and password to a login URL and extracting a session ID from the response.
- B 摘要: Loads existing Ant library definitions by reading resource files from the classpath and invoking loadAntLib for each package.
- 静态失败原因: Static BERT-based models rely on token overlap and deep contextual embeddings; the low token Jaccard (0.17) and distinct domain-specific words (login vs antlib, email vs resource) cause low similarity scores. Moreover, the model may not capture the high-level similarity of 'reading data from external sources' that BCB annotators might have used.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'loading from network/classpath' since they both involve opening connections/streams and reading data, albeit for different purposes. The broad Type-4 criteria could accept this as partial functional similarity in resource acquisition.
- 共享行为: Both open input streams and read data line by line using BufferedReader.；Both close streams and readers in a finally-like manner (implicitly via try-with-resources style? Actually not exactly, but they close at the end).；Both handle IOException and convert to runtime exceptions or print messages.；Both use URL or URI objects.
- 行为差异: A performs an HTTP POST (with output) to authenticate, B only reads resources (no output).；A returns a session ID string; B returns void and loads libraries into some context.；A uses URLConnection with output writing; B uses ClassLoader.getResources to enumerate URLs.；Error handling: A prints 'Login Error' and returns empty string; B wraps all exceptions in RuntimeException.
- 修正建议: Incorporate more explicit structural or dataflow analysis to capture underlying resource-reading behavior.；Use models that can align abstract functionality beyond lexical similarities, e.g., with program graphs or contrastive learning on functional tasks.；Reconsider BCB label validity for such pairs to reduce noise.

### case_id=3755 FN benchmark_preference_bias

- 方法: `process` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Processes a template and writes output files based on template type (freemarker, xslt, copy).
- B 摘要: Retrieves a resource as an InputStream, caching it locally after downloading from a URL.
- 静态失败原因: Static BERT correctly predicted non-clone based on low token overlap and semantic difference; BCB label seems incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as file/resource handling functions with similar I/O patterns, but the dissimilarity in core functionality makes it questionable.
- 共享行为: Both use file I/O streams and handle exceptions
- 行为差异: A writes files using template processing; B reads and caches remote resources；A uses switch on template type; B uses URL connection and caching logic；A throws ModelGenerationException; B throws generic Exception and returns null；A uses Writer; B uses InputStream and BufferedStreams
- 修正建议: Re-evaluate BCB annotation for this pair; likely should be non-clone；Improve clone detection models to discount superficial I/O similarities when core logic differs

### case_id=3756 FP lexical_or_api_overlap

- 方法: `readVersion` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `8.5`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a local version file from classpath and extracts version, revision, and date fields.
- B 摘要: Performs an HTTP request to check for upgrades, processes the response with database updates and UI modifications.
- 静态失败原因: The static BERT model likely overemphasized the shared API calls (URL, BufferedReader, InputStreamReader) and the similar loop structure, missing the large semantic gap in overall behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have entirely different high-level purposes despite low-level I/O similarity.
- 共享行为: Both open a URL and read lines using BufferedReader.；Both parse lines using split and conditionally assign values.
- 行为差异: A reads a local file; B makes a remote HTTP request.；A sets instance fields; B performs database and UI operations.；A is simple and single-purpose; B is complex with multiple side effects.；A handles IOException locally; B throws Exception upward.
- 修正建议: Incorporate data-flow and control-flow analysis to capture side effects.；Add type-based context (e.g., whether URL is local or network).；Use method-level summarization to compare high-level intents.

### case_id=3757 FN partial_functionality

- 方法: `getFile` vs `loadBinaryStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies SOAP address endpoint, and saves to local temp directory, returning the file path.
- B 摘要: Copies an input stream to an HTTP response output stream, setting content headers, for dynamic content delivery.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low token overlap (Jaccard=0.06) and significant differences in context, variable names, and control flow. The model may have missed the abstract stream-copying similarity because it focused on the overall distinctive tasks (WSDL download vs. HTTP response serving).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this pair as a clone because both functions fundamentally perform stream I/O (reading from an input and writing to an output), which is a common functional pattern. The additional XML processing in getFile might be considered extraneous to the core clone behavior.
- 共享行为: Both read from an input source (URL stream or passed stream) and write to an output target (file or HTTP response).
- 行为差异: getFile involves XML parsing and modification, file existence check, temp file handling, while loadBinaryStream is a simple stream copy with no processing.；getFile returns a file path; loadBinaryStream modifies the HTTP response and does not return a value.；getFile uses NIO channels; loadBinaryStream uses IOUtils.copy.
- 修正建议: Use data-flow analysis to identify stream read/write operations across different code structures.；Train models on pairs where only a subpart of the function is similar (partial clones).；Incorporate abstract API patterns like 'copy stream' in feature representations.

### case_id=3758 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `testReadHelloWorldTxt`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale by reading the English version and writing a new properties file with an updated message.
- B 摘要: Tests that a FSContentResolver reads HelloWorld.txt from various path formats and verifies the content.
- 静态失败原因: The low token overlap and distinct semantics correctly led to a non-clone prediction, but the BCB label is positive, so the model failed to align with the possibly erroneous benchmark annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Likely a mislabel; BCB may have considered both as file I/O operations, but the functionality is too distinct.
- 共享行为: Both read from input streams；Both write to files；Both use file paths
- 行为差异: Different purposes: modification vs testing；Different data: properties vs plain text；Different control flow: one updates existing properties, the other asserts content；Different error handling: one catches exceptions, the other throws
- 修正建议: Re-examine BCB annotation for this pair; likely a false positive.；Consider adding more contextual features to disambiguate file I/O from core logic.

### case_id=3759 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by replacing or adding a key-value pair, first copying the English file as template if the locale file does not exist.
- B 摘要: Recursively copies a file or directory to a destination directory, skipping .svn directories and files with identical modification times.
- 静态失败原因: Static BERT models rely heavily on token and structural similarity; the low Jaccard (0.139) led to a non-clone prediction. They failed to recognize the shared file-copying behavior as a significant functional overlap due to limited understanding of high-level semantics and partial functionality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: Despite low lexical overlap, BCB may have considered the shared file-copying functionality (A's template copy) as partial functional similarity, and both methods involve extensive file manipulation, which could be seen as Type-4 clones.
- 共享行为: Both perform file I/O operations.；Both check for file existence and handle file creation.；Both copy file contents (A copies English file as template, B copies files/directories).
- 行为差异: High-level purpose: configuration modification vs. file/directory copy.；A processes properties file line-by-line to replace/add a key-value; B blindly copies bytes.；A handles only one file; B recursively handles directories and multiple files.；A catches generic Exception; B throws IOException.
- 修正建议: Incorporate dataflow analysis to track that both methods perform file copying.；Use graph-based models that capture file I/O operations beyond token overlap.；Enhance training with examples of partial functionality clones.

### case_id=3760 FN partial_functionality

- 方法: `getEncoding` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts the character encoding from an HTTP response by checking headers and content.
- B 摘要: Reads and discards all lines from a specific URL's input stream.
- 静态失败原因: Static BERT likely focused on the low token overlap and distinct method names, return types, and specific logic (charset extraction) present only in A. It did not capture the underlying common structure of URL reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as Type-4 clones because both implement the same high-level task of reading from a URL, despite differing specifics. The shared pattern of opening a connection and reading lines aligns with BCB's broad notion of functional similarity.
- 共享行为: Open a URL connection and create a BufferedReader from its input stream；Read lines from the stream until null
- 行为差异: A checks HTTP headers for content-type and charset, then searches the content for charset patterns; B does no such processing；A returns the detected encoding or a default; B returns void；A uses a URL from a class field; B hardcodes a specific URL；A has a try-finally for resource cleanup; B uses try-catch with no cleanup
- 修正建议: Train with more examples of Type-4 clones that share only partial functionality；Use graph-based models that capture control flow and data flow to identify common patterns；Augment data with method name anonymization to reduce over-reliance on names

### case_id=3761 FP lexical_or_api_overlap

- 方法: `getRequestContent` vs `sendRequest`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads first line from a URL using HTTP GET.
- B 摘要: Sends an XML request via HTTP POST with gzip compression and parses the XML response.
- 静态失败原因: The model may have been misled by lexical and API overlap (e.g., URL, openConnection, InputStream) and the general 'network request' theme, failing to capture the large behavioral differences in protocol, data handling, and return behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely annotates as non-clone because the functions differ significantly in protocol, complexity, and purpose; partial functionality similarity is insufficient for a clone label.
- 共享行为: Both perform HTTP network requests using Java URLConnection.
- 行为差异: A uses GET, B uses POST.；A reads only first line, B reads and parses entire XML response.；A does not compress, B compresses output.；A returns the line, B returns empty string.
- 修正建议: Incorporate control/data flow features to distinguish GET vs POST.；Use method signatures and return types to capture differences.；Add attention to I/O direction and compression usage.；Leverage graph-based models that model data dependencies.

### case_id=3762 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `get`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Validates a Minecraft handshake packet by checking a server key and, if valid, authenticating via an HTTP request to session.minecraft.net, then sending a login packet or shutting down the connection.
- B 摘要: Fetches an array of GameRecord objects by making an HTTP GET request with custom headers to a given URL, parsing the response line by line and decoding non-comment lines.
- 静态失败原因: Static BERT models may have overestimated similarity due to overlapping tokens like 'URL', 'BufferedReader', 'readLine', 'catch(Exception)', and 'printStackTrace', ignoring the deeper semantic differences in the control flow and domain.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled these as non-clones because the overall functionality is distinct (handshake vs. data retrieval). While both use similar IO patterns, the purpose and output differ significantly.
- 共享行为: Both functions make an HTTP request and read the response using BufferedReader.；Both handle exceptions (e.g., IOException) and print stack traces.；Both perform conditional logic based on the response content.
- 行为差异: Function A validates a server key (hex string) before making the HTTP request; Function B does no such validation.；Function A sends a hardcoded URL to a specific authentication endpoint; Function B accepts a parameterized URL.；Function A's HTTP request uses GET with query parameters; Function B uses custom headers.；Function A sends network packets (Packet1Login) upon success; Function B returns an array of GameRecord objects.
- 修正建议: Incorporate structural information (e.g., control flow graphs) to distinguish different workflows.；Use program slicing to focus on the core computational logic rather than boilerplate IO.；Add type information or method-level documentation to emphasize differences in purpose.

### case_id=3763 FP boilerplate_overlap

- 方法: `loadSourceCode` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Load source code from a classpath resource, apply syntax highlighting to each line, and build an HTML string for display.
- B 摘要: Retrieve the latest version string from a remote URL by reading the last line of the response.
- 静态失败原因: Static BERT models rely heavily on token overlap and structural patterns; the high overlap in API usage (URL, BufferedReader, readLine, try-catch) leads to high similarity scores, ignoring the semantic differences in purpose and output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: Under BCB's broad clone categories, Type-3/Type-4 require functional similarity; these functions have different outputs and purposes, so they are likely not considered clones despite syntactic overlap.
- 共享行为: Open a URL connection and read lines using BufferedReader；Use try-catch to handle exceptions
- 行为差异: A reads from classpath resource, B from remote HTTP URL；A applies syntax highlighting, B does not；A builds HTML string and assigns to member variable, B returns plain string；A reads all lines, B uses only the last line
- 修正建议: Improve model's ability to distinguish between common boilerplate and core logic；Incorporate dataflow or program dependence analysis to capture output usage and intent；Train on more examples where API usage overlaps but functionality diverges

### case_id=3764 FP lexical_or_api_overlap

- 方法: `importRoles` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Imports roles by parsing XML from a URL and returning a list of RoleName objects.
- B 摘要: Loads a file from a URL with optional authentication, writes it to a temporary file, and updates a status label with download progress.
- 静态失败原因: Static BERT likely overemphasized the common token sequence (URL, BufferedReader, while loop) and missed the distinct data transformations and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB requires significant functional overlap; these functions share only URL reading boilerplate but differ in processing and output, so they are not clones.
- 共享行为: Both open a URL connection and read lines using BufferedReader.
- 行为差异: importRoles parses XML to extract RoleName objects; loadURL writes raw input lines to a file.；importRoles handles authentication-free basic URL; loadURL supports Basic Authentication.；importRoles returns a structured list; loadURL has void return and manages UI updates.；importRoles has no file I/O beyond reading; loadURL creates and writes to a temporary file.
- 修正建议: Incorporate data flow analysis to track transformations of the read data.；Weight method signatures and return types more heavily.；Include structural differences like exception handling or user interface interactions.

### case_id=3765 FN partial_functionality

- 方法: `getContent` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs HTTP GET using Apache HttpClient with timeouts and returns response body as string.
- B 摘要: Performs HTTP GET using HttpURLConnection with basic authentication and stores response body, tracking time and setting finish flag.
- 静态失败原因: Low token overlap and different library APIs misled the model; it failed to recognize the shared pattern of open connection, read lines, close.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers partial functionality similarity as clone; both functions fundamentally download text from a URL via GET and read it line-by-line, which is the core behavior.
- 共享行为: Both execute an HTTP GET request；Both read the response line by line；Both append lines with newline to a StringBuffer；Both close the reader and input stream
- 行为差异: Different HTTP client libraries (HttpClient vs HttpURLConnection)；code_a sets connection and socket timeouts; code_b does not；code_b includes basic authentication; code_a does not；code_b tracks last iteration time and sets a finish flag; code_a does not
- 修正建议: Enhance training with examples of different APIs performing same core function；Incorporate data-flow graphs to capture operation sequences；Add more functional-level features like 'performs HTTP GET' abstracted from specific libraries

### case_id=3766 FN partial_functionality

- 方法: `copy` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file character by character using FileReader and FileWriter.
- B 摘要: Launches a NexOpen project configuration by processing XML, setting Hibernate dialect, and performing reverse engineering file copying.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the low lexical overlap and different method names/structures, correctly predicting non-clone from a strict perspective. It failed to capture the potential BCB preference for partial file I/O similarity, possibly due to inability to recognize the copying sub-task in method B's complex code.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both methods contain file copying behavior (A explicitly, B as a sub-step), and BCB annotations sometimes consider partial functionality similarity (Type-3) when a common sub-task is present, even if the overall context differs.
- 共享行为: Both involve file I/O operations, specifically reading from a source and writing to a destination.
- 行为差异: Method A is purely a file copy function; Method B is a complex launch procedure with many steps beyond file I/O.；Method A uses simple character streams; Method B uses a mix of DOM parsing, properties, and IOUtils.copy for binary streams.；Method A lacks any project configuration or error handling beyond IOException; Method B has extensive error handling and resource management.
- 修正建议: Enhance model with sub-task detection to identify common operations like copy across different contexts.；Use hierarchical or graph-based representations to capture both global and local semantics.；Incorporate dataflow analysis to highlight read-write patterns.

### case_id=3767 FP boilerplate_overlap

- 方法: `GetResponse` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches the content of a given URL via HTTP GET and returns it as a string.
- B 摘要: Searches Google Images for a specific artist/album, parses the response to extract image URLs, and stores them in a list.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by the lexical and structural overlap of common HTTP boilerplate (HttpURLConnection, BufferedReader, while loop), overlooking the significant differences in purpose and post-processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labelled as non-clone because the overall functionality differs: one is a generic HTTP utility, the other is a specific image search with distinct data processing and output.
- 共享行为: Open HTTP connection to a URL；Read response line by line using BufferedReader；Handle exceptions
- 行为差异: A returns raw content; B extracts image URLs and stores in list；A takes URL as parameter; B constructs URL based on artist/album；B adds User-Agent header; A does not；B closes reader explicitly; A does not
- 修正建议: Enhance model to capture overall program intent and data flow beyond local patterns；Include data flow analysis to track how fetched data is used (return vs. further processing)；Train on more diverse examples to reduce overreliance on boilerplate code

### case_id=3768 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a key-value pair in a locale-specific properties file, creating the file if needed by copying from a default English file.
- B 摘要: Concatenates multiple input text files into a single output file specified as the last command-line argument.
- 静态失败原因: The static BERT/GraphCodeBERT model likely relies on token and syntax overlap, which is low (Jaccard 0.18), and fails to capture the abstract file I/O similarity that BCB annotators might have considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'file processing functions' that read input and write output, falling under a broad Type-4 category where high-level purpose ('modify a file' or 'concatenate files') is considered similar enough for clone labeling.
- 共享行为: Both perform file reading and writing；Both use File and handle file I/O exceptions
- 行为差异: A modifies a specific property key; B copies entire lines without modification；A deals with localization and properties file format; B handles arbitrary text files；A reads from classpath resources; B reads from command-line-specified files；A conditionally creates a file by copying; B does not create files (output file created by PrintWriter)
- 修正建议: Incorporate task-level semantics, e.g., by modeling file I/O operations and high-level purpose；Use code summarization or functional grouping to recognize common I/O patterns；Augment training with more Type-4 examples that have low lexical overlap

### case_id=3769 FP partial_functionality

- 方法: `readTwitterFead` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a fixed Twitter timeline JSON via HTTP and returns the response body as a string.
- B 摘要: Fetches tile data from a URL (file or HTTP), builds a GeoJSON string, processes it into a VectorTile, and adds the resulting geometries to a data loader, while managing concurrency and caching.
- 静态失败原因: The static BERT model may have been misled by the structural similarity in the URL-reading loop (while readLine != null) and similar exception handling, overemphasizing the common sub-pattern and ignoring the divergent overall logic.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotators likely considered these non-clones because the overall functionality and purpose differ substantially; the shared reading pattern is too small relative to the whole method.
- 共享行为: Both open a URL connection and read the content line by line into a string using BufferedReader.
- 行为差异: A uses Apache HttpClient, B uses URL.openStream.；A only returns the string, B further processes the content into geometries and updates data structures.；B includes synchronization and caching logic absent in A.；A catches ClientProtocolException, B catches FileNotFoundException and IOException.
- 修正建议: Incorporate more global context to capture method purpose and overall logic.；Train with contrastive examples where partial similarity does not imply clone.；Use data flow analysis to distinguish differences in output usage.；Consider method names and class contexts.

### case_id=3770 FN benchmark_preference_bias

- 方法: `getFile` vs `descargarArchivo`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies it by replacing the endpoint location, and saves it to a temporary directory, returning the file path.
- B 摘要: Copies a file from a source path (obtained from a data structure) to a destination path using file channel transfer.
- 静态失败原因: The model correctly identified the differences in functionality and considered them non-clones, but the benchmark's label (based on broad Type-3/Type-4 criteria) considered them clone, leading to a false negative from benchmark perspective.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to superficial similarity in file I/O patterns and use of FileChannel, even though the high-level functionality differs significantly.
- 共享行为: Both use FileChannel to transfer data between streams；Both handle IOException
- 行为差异: Source is URL vs local file；A modifies XML content, B does not；A returns String, B is void；A throws AxisFault, B prints error to stderr
- 修正建议: Re-evaluate BCB label to ensure it aligns with actual functional similarity；Focus on higher-level semantics rather than shared boilerplate in clone detection benchmarks

### case_id=3771 FN benchmark_preference_bias

- 方法: `copyResource` vs `parseContent`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.15`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a resource from a URL or local file to a destination file by reading bytes in a loop.
- B 摘要: Parses HTML content from an input stream, extracts metadata, links, body text, and language, then adds fields.
- 静态失败原因: Static BERT correctly predicted non-clone due to low token overlap and distinct control flow; it 'failed' to match a possibly erroneous BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled as clone based on overly broad similarity (both involve reading and processing input), but this is inconsistent with typical Type-3/Type-4 criteria.
- 共享行为: Both read from an input source (stream or file)；Both perform I/O operations and handle exceptions
- 行为差异: A is a simple byte-level copy; B is complex HTML parsing with charset detection, link extraction, and language detection；A writes to a file; B writes to a StringWriter and extracts structured information；A handles only one source; B processes multiple HTML nodes and metadata
- 修正建议: Re-evaluate BCB annotation for this pair；Improve benchmark consistency by requiring stronger semantic similarity

### case_id=3772 FN benchmark_preference_bias

- 方法: `readGeoParserResult` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Constructs an XML geolocation query, sends it via HTTP, parses the response to extract place names and associated gazetteer IDs, with retry logic on failure.
- B 摘要: Parses a configuration file and string tokens to initialize multiple hash sets and key mappings for Tibetan Wylie transliteration processing.
- 静态失败原因: The model correctly detected low lexical overlap (Jaccard=0.111) and distinctly different APIs and logic, leading to non-clone prediction.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to superficial similarity as 'data reading' functions, or as a benchmark annotation error.
- 共享行为: Both use loops and collections to accumulate data；Both involve reading external data (URL stream vs. file/strings)
- 行为差异: Function A performs network I/O and XML parsing; Function B reads from string tokens and a local file；Function A returns a collection of tuples; Function B populates static fields as side effects；Function A has retry logic; Function B has no retries；Domain: geolocation vs. Tibetan transliteration initialization
- 修正建议: Consider that this pair may be a false positive in BCB; review annotation guidelines；If retaining as clone, ensure clones capture functional similarity beyond reading data; current pair does not

### case_id=3773 FP lexical_or_api_overlap

- 方法: `sendPost` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Checks for software upgrades by querying a remote server, parsing XML-like response, updating a local database, and managing UI components.
- 静态失败原因: The model likely overfocused on the superficial IO pattern (URLConnection + BufferedReader readLine) and exception handling, ignoring the deep semantic differences in data flow, control flow, and domain logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones due to fundamentally different purposes: one is a generic HTTP post, the other is a complex upgrade check with database and UI interactions. Token Jaccard is very low, and there is no partial functional similarity.
- 共享行为: Both open a URL connection and read input line by line.；Both catch exceptions (though B throws Exception).
- 行为差异: A uses HTTP POST with request property; B uses HTTP GET with query parameters.；A returns a string; B returns void and has side effects (database, UI).；A is a general utility; B is domain-specific with database and UI operations.；B parses response into tokens and updates a database table; A simply concatenates lines.
- 修正建议: Augment training data with more diverse non-clone pairs sharing IO boilerplate.；Use graph-based models (e.g., CodeBERT with data flow graphs) to capture semantic differences.；Add contrastive learning objectives that penalize surface-level similarity without semantic alignment.

### case_id=3774 FP lexical_or_api_overlap

- 方法: `get` vs `handledRun`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves an array of GameRecord objects by sending an HTTP GET request with location headers and parsing lines that do not start with '#'.
- B 摘要: Downloads an updated gamedata XML file from a fixed URL if the local version is outdated, then loads the database.
- 静态失败原因: The static model was misled by common tokens such as 'URL', 'BufferedReader', 'try', 'catch', 'readLine', and 'IOException', which gave a false sense of similarity despite different overall logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label non-clone because the functions have different signatures, different logic flows, and different outputs; they share only superficial API usage but not similar functionality.
- 共享行为: Both make HTTP requests and read responses using BufferedReader；Both handle IOException
- 行为差异: Different purpose: fetching records vs. updating local file；Different URL construction and headers；Different response processing: line-by-line filtering vs. version check and byte copying；Different return values/effects: returns array vs. writes to file
- 修正建议: Enrich training data with negative examples where API usage overlaps but logic diverges；Incorporate control-flow or data-flow features to distinguish different program structures；Consider method signatures and return types to reduce false positives

### case_id=3775 FN partial_functionality

- 方法: `copyResource` vs `createTar`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file by reading and writing byte by byte.
- B 摘要: Creates a tar archive from a directory by collecting files and writing them to a tar output stream.
- 静态失败原因: The model focused on lexical and structural differences (different method names, libraries, and control flow) and low token overlap, failing to recognize the abstract I/O copying pattern that BCB considered similar.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them Type-4 clones due to the common core of reading data from an input and writing to an output, despite the different contexts (simple file copy vs. tar creation). The byte-copying loop is a shared functional pattern.
- 共享行为: Both involve reading from an input source and writing to an output stream.；Both handle file I/O and can throw exceptions.
- 行为差异: copyResource copies a single resource; createTar archives multiple files into a tar format.；createTar includes tar-specific metadata (TarEntry), directory traversal, and null/validity checks.；copyResource uses simple byte loop; createTar uses buffer and tar-specific stream wrappers.
- 修正建议: Enhance model with data flow analysis to capture abstract I/O patterns.；Add training examples where functions share a common sub-behavior despite different overall purposes.；Use multi-task learning to recognize both high-level purpose and low-level implementation details.

### case_id=3776 FP lexical_or_api_overlap

- 方法: `updateFile` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Copies a file to a destination path by replacing a prefix, using NIO channels.
- B 摘要: Parses static string fields and reads a file to populate data structures for Tibetan transliteration.
- 静态失败原因: Both functions contain file-related variable names and API calls (File, FileInputStream, etc.), causing the model to over-rely on lexical overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because they solve entirely different problems and have no semantic similarity.
- 共享行为: Both involve file operations (one copies, one reads)
- 行为差异: Different purpose: file copy vs. data initialization and parsing；Different input/output: FileChannel vs. sets/maps；Different control flow: simple copy vs. complex tokenization and file reading
- 修正建议: Use dataflow analysis to distinguish file copy from file parsing；Train on more diverse examples with varied purposes；Incorporate structural or semantic embeddings that differentiate high-level intent

### case_id=3777 FP lexical_or_api_overlap

- 方法: `getURLContent` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generic utility to fetch content from a URL and return it as a string.
- B 摘要: Fetches tickets from a Request Tracker queue by constructing a query, parsing ticket IDs, and retrieving each ticket.
- 静态失败原因: Static model may have been misled by shared keywords (URL, BufferedReader, InputStreamReader, line) and similar structural patterns like try-catch-finally, despite low token Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers functions non-clones because despite both involving HTTP, their purposes and complexities are vastly different; only superficial API usage overlaps.
- 共享行为: Both functions make HTTP requests；Both read response using BufferedReader and InputStreamReader；Both handle IOException indirectly
- 行为差异: A returns a String of the entire content; B returns a list of RTTicket objects；A is generic; B is specific to RT ticketing system；B includes query parameter construction, response parsing for ticket IDs, and additional error handling；A uses URLConnection; B uses Apache HttpClient
- 修正建议: Improve training with more negative examples that share API patterns；Integrate data flow or control flow features to distinguish different functionalities；Use function-level semantic summarization

### case_id=3778 FP boilerplate_overlap

- 方法: `readData` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Initializes data structures for Tibetan transliteration by parsing configuration strings and a data file.
- B 摘要: Tests the StraightStreamReader by writing and reading a file with all byte values.
- 静态失败原因: Static BERT models may have over-relied on superficial structural similarities like try-catch blocks, file I/O, loops, and class field accesses, while missing the fundamentally different intents. The truncation in code A may have also reduced distinguishing features.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have entirely different purposes and semantics: one is an initialization routine for a Tibetan linguistics system, the other is a unit test for a stream reader. They share no meaningful functionality or algorithmic similarity.
- 共享行为: Both perform file I/O operations.
- 行为差异: A parses configuration strings and populates sets/maps; B writes and reads a file to verify stream reader behavior.；A involves complex language-specific parsing; B is a unit test for a stream class.；A operates on predefined string fields; B operates on a temporary file.；A has nested conditional logic for parsing columns; B has sequential read tests.
- 修正建议: Incorporate data flow analysis to distinguish initialization vs. test logic.；Use larger context or whole-program analysis to capture overall function purpose.；Train on more diverse examples that highlight semantic differences despite structural overlap.

### case_id=3779 FN partial_functionality

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, extracts entries from a ZipInputStream, and writes each entry to a file.
- B 摘要: Copies a file from one location to another using FileChannel.
- 静态失败原因: Static BERT/GraphCodeBERT likely missed the high-level semantic difference because of low token overlap and the functions are structurally dissimilar; the model may have focused on the shared I/O patterns (FileInputStream, FileOutputStream) and ignored the distinct operations (unzipping vs channel copying).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered both as file copying/transfer operations, or the annotation might have been influenced by the presence of file I/O boilerplate (streams, buffers) and exception handling, leading to a broad Type-4 classification.
- 共享行为: Both involve reading from a source (URL/stream vs local file) and writing to a destination file.；Both handle I/O exceptions in some way (explicit or via throwAsError).
- 行为差异: Function A downloads over HTTP/unzips, while B copies a local file directly.；Function A writes multiple output files (zip entries), B writes a single output file.；Function A uses stream-based I/O, B uses FileChannel for potentially faster copying.；Function A lacks proper resource cleanup (streams not closed in finally), B uses try-finally.
- 修正建议: Incorporate program analysis to capture data flow from source to destination, distinguishing between downloading/unzipping and direct file copy.；Use a larger context window or abstract syntax tree to detect the different number of output files and the involvement of ZipInputStream.；Add a semantic layer that recognizes high-level operations like 'download and extract' vs 'copy file'.

### case_id=3780 FP boilerplate_overlap

- 方法: `readZoneIDs` vs `createHTML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a file line by line, parses each line as integer, and returns a set of zone IDs.
- B 摘要: Reads a CSS file, builds an HTML page header, and conditionally appends database-driven content based on page type, returning complete HTML string.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the structural similarity of the resource-reading boilerplate and ignored the divergent overall logic and output types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB label is 0 (non-clone) because the functions have completely different purposes and outputs, despite a small shared boilerplate pattern.
- 共享行为: Both use URL to open resource stream and read lines via InputStreamReader/BufferedReader.
- 行为差异: Function A reads integers; Function B reads CSS and builds HTML.；Function A returns a HashSet; Function B returns a String.；Function B has complex switch logic and database queries; Function A is purely file parsing.；Function A uses LineNumberReader; Function B uses BufferedReader.
- 修正建议: Train models to weigh short common patterns less when overall scope differs.；Use contrastive learning that penalizes high similarity from shared boilerplate.；Incorporate type signatures and external calls (e.g., database) into representation.

### case_id=3781 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `execute`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles various GUI settings and file selection for Graphviz and ImageMagick paths.
- B 摘要: Copies a file from source to destination with directory creation and I/O error handling.
- 静态失败原因: The model likely overfitted to common tokens like File, IOException, and try-catch, ignoring the overall semantic differences due to limited context length or attention spread.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have entirely different purposes, control flows, and API usage, despite shared basic Java constructs.
- 共享行为: Uses File and file I/O operations；Handles exceptions with try-catch
- 行为差异: Function A is a GUI event handler with multiple UI operations; Function B is a file copy utility.；Function A uses JFileChooser and stores preferences; Function B does not interact with UI.；Function A has complex conditional branching; Function B has a linear flow.
- 修正建议: Incorporate global structure information (e.g., control flow graphs)；Use hierarchical attention to differentiate between boilerplate and core logic；Add negative examples with high token overlap but different semantics

### case_id=3782 FP lexical_or_api_overlap

- 方法: `main` vs `checkInputStream`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method for AdapterGenerator that processes a Prolog file, generates adapters, and writes output.
- B 摘要: Helper method to check if an InputStream's content matches a given byte array.
- 静态失败原因: Static BERT likely over-relied on overlapping API tokens (e.g., InputStream, ByteArrayOutputStream) and missed the vast semantic and structural differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled 0 because the functions are completely different in purpose, size, and logic; they share only superficial I/O operations.
- 共享行为: Both use InputStream and ByteArrayOutputStream
- 行为差异: Function A is a complex main method with file I/O, parsing, and class generation；Function B is a simple test helper that compares streams
- 修正建议: Improve model capacity to recognize overall structure and intent；Incorporate data flow or control flow features；Use contrastive learning on diverse negative pairs

### case_id=3783 FN benchmark_preference_bias

- 方法: `readData` vs `PhoneSetImpl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads multiple static comma-separated strings and a file to populate various sets and maps for Tibetan text processing.
- B 摘要: Reads lines from a URL, skipping comment lines, and calls parseAndAdd to populate a phone set map.
- 静态失败原因: The token Jaccard is very low (0.057), and the functions differ greatly in length and complexity. Static BERT models heavily rely on token overlap and structural patterns, so they fail to recognize the high-level functional similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely considers these as Type-4 clones because both are initialization routines that read configuration data and store it in internal data structures, representing a broad functional similarity.
- 共享行为: Both read external data from a source (static strings/file vs. URL) and populate internal data structures；Both use a loop to process lines of input
- 行为差异: A uses StringTokenizer on static fields and a file; B uses BufferedReader on a URL；A populates multiple sets (topSet, leftSet, etc.) and maps; B populates a single map via parseAndAdd；A has complex column parsing and validation; B has simple comment-skipping and delegation；A is much longer and more complex than B
- 修正建议: Train models to recognize abstract functional patterns beyond token overlap；Incorporate program summarization or data flow analysis；Use more diverse Type-4 examples in training data

### case_id=3784 FN benchmark_preference_bias

- 方法: `main` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads a KMZ file from a URL, unzips it, and extracts its entries to local files.
- B 摘要: Copies an InputStream to an OutputStream using IOUtils.copyLarge with error logging and stream closing.
- 静态失败原因: The static BERT model likely relied on token-level and structural features, which showed very low similarity (Jaccard 0.04878) and completely different API usage, leading to a correct non-clone prediction. From the BCB perspective, it 'failed' because it did not recognize the vague commonality of stream handling.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered them clones under a very broad Type-4 (functional similarity) because both involve reading from an input stream and writing to an output stream, even though the operations differ significantly.
- 共享行为: Both perform I/O operations involving streams.
- 行为差异: A downloads from a URL and extracts ZIP; B copies arbitrary streams.；A writes to specific files; B writes to a generic sink.；A uses ZipInputStream and FileOutputStream; B uses IOUtils.copyLarge.；A throws Exception; B catches and logs IOException.
- 修正建议: Refine BCB annotation guidelines to avoid overly broad Type-4 pairs.；Incorporate functional semantics through program analysis or documentation to capture deep similarities.；Train models to consider the overall task purpose rather than just local patterns.

### case_id=3785 FP boilerplate_overlap

- 方法: `copyFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file from source to destination using NIO FileChannel transferTo.
- B 摘要: Handles ActionEvent commands by opening file choosers, setting paths, and saving user preferences.
- 静态失败原因: Despite low token overlap, the static BERT model might have been misled by the presence of common file-handling patterns (e.g., opening files, null checks) and the use of similar API classes (File, FileChooser), leading to a false positive. Additionally, the model may not capture the different control flow and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators typically consider functions with entirely different purposes and behavior as non-clones, even if they share some file-related keywords. The overall functionality is unrelated.
- 共享行为: Both involve file operations (copying vs. selecting file paths).
- 行为差异: Method A is a short utility for binary file copying.；Method B is a long UI event handler with multiple conditional branches.；Method A uses low-level I/O channels; Method B uses Swing components and preference storage.；Method A has no side effects beyond file I/O; Method B modifies UI and application state.
- 修正建议: Incorporate data flow analysis to distinguish file I/O from UI operations.；Use broader context (e.g., surrounding class or method names) to capture intent.；Apply structure-based features like control flow graphs to differentiate loops and conditionals.；Include type information (e.g., method signature, return type, exception clauses) to separate utility methods from event handlers.

### case_id=3786 FN benchmark_preference_bias

- 方法: `copy` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Recursively copies a file or directory to a destination, skipping .svn directories and skipping files with same last modified time.
- B 摘要: Launches a Hibernate tooling for a NexOpen project by reading pom.xml files, processing XML documents, setting properties, and scheduling an install job.
- 静态失败原因: The low token overlap and lack of syntactic similarity likely led the model to predict non-clone, and the semantic connection is too subtle for a static model to capture without understanding the Eclipse platform and build contexts.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as performing a series of steps that ultimately write data to files (copy in A, generated files in B), possibly categorizing as Type-4 semantic clones based on high-level 'data copying' behavior.
- 共享行为: Both methods involve file I/O operations；Both handle exceptions；Both have conditional logic
- 行为差异: Function A copies files recursively; Function B configures a build project；Function A deals with directories and files; Function B deals with Eclipse resources and XML documents；Function A is recursive; Function B is not recursive
- 修正建议: Improve focus on semantic equivalence through flow-aware models；Incorporate domain-specific knowledge for plugin methods

### case_id=3787 FP partial_functionality

- 方法: `main` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Main method that generates adapter classes from a Prolog file, involving parsing, class writing, and jar creation.
- B 摘要: Utility method that copies a file from source to destination using character-by-character reading.
- 静态失败原因: The model likely overemphasized the shared file I/O tokens (File, IOException, read/write) while ignoring the vast semantic gap in overall logic, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically requires functional similarity for clones; these functions are fundamentally different in purpose and behavior, so BCB correctly labels them as non-clones.
- 共享行为: Both perform file operations (reading and writing)；Both use File and IOException classes
- 行为差异: Function A is a complex pipeline with multiple stages (parsing, generation, writing), while B is a simple file copy；Function A handles command-line arguments and multiple error conditions; B has no argument parsing or extensive error handling；Function A writes to a jar file and generates classes; B writes to a plain file；Function A involves object serialization and class loading; B does not
- 修正建议: Incorporate structure-aware representations that capture control flow and data dependencies；Use methods that abstract the overall program intent beyond surface-level API calls；Employ contrastive learning to disambiguate functions with similar I/O but different semantics

### case_id=3788 FN benchmark_preference_bias

- 方法: `runInternal` vs `getEncoding`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads and parses OPDS catalog or book from an HTTP URL, handling redirects, pagination, and errors.
- B 摘要: Extracts character encoding from HTTP response headers or content body.
- 静态失败原因: The static model correctly identified the large structural and semantic differences and low token overlap, so it did not fail; rather, the BCB annotation may be overly generous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them clones due to shared boilerplate of URL connection handling and stream reading, but this is too broad and the core functionality differs entirely.
- 共享行为: Both open a URLConnection to an HTTP URL；Both read from an InputStream；Both handle exceptions during connection
- 行为差异: A handles complex catalog parsing and downloading, B only extracts encoding；A manages redirects and pagination, B does not；A has extensive error handling and progress reporting, B does not
- 修正建议: Increase requirement for behavioral similarity beyond shared API usage；Use more strict criteria for partial functionality clones

### case_id=3789 FN partial_functionality

- 方法: `readIntoList` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads from a URL, parses HTML-like lines to create JMenuItem objects with action commands and listeners, and populates a map.
- B 摘要: Reads from static string variables and a file, parses tokens and tab-separated lines to populate multiple sets and hash maps for a Tibetan transliteration system.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low lexical overlap (token Jaccard 0.101) and different API usage (BufferedReader vs StringTokenizer, JMenuItem vs HashSet). The model may rely on surface-level similarity and missed the abstract functional similarity of reading and parsing.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as clone because both methods read input data and populate data structures, which is a generic data-loading functionality. However, the specifics differ significantly.
- 共享行为: Both parse input data line by line；Both store parsed results into collections/maps
- 行为差异: Method A reads from a URL, method B reads from static strings and a file；Method A creates GUI components, method B builds data structures for transliteration；Method A uses HTML parsing, method B uses StringTokenizer and tab-separated values；Method B has complex column-specific handling, method A has simple HTML tag extraction
- 修正建议: Improve detection of high-level functional patterns；Use control flow graph matching to identify similar reading loops；Incorporate type information to see both use string inputs

### case_id=3790 FN partial_functionality

- 方法: `copyResource` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file using byte stream copying.
- B 摘要: Handles an HTTP GET request by proxying to another URL, copying response headers and body to the client.
- 静态失败原因: Static BERT models rely on lexical and syntactic overlap, which is low (token Jaccard 0.1075). The large difference in method names, framework usage, and surrounding code caused the model to miss the shared I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a Type-3/Type-4 clone because both functions perform a core input-to-output data copy operation, despite different contexts and additional logic.
- 共享行为: Both open an input stream and write to an output stream, effectively copying data.
- 行为差异: Function A copies raw bytes from a URL or file to a file; Function B proxies HTTP requests and handles headers, logging, and URL rewriting.；Function A is a private utility; Function B is a servlet method with specific HTTP semantics.；Function A has custom error handling for missing resources; Function B uses HTTP connection and servlet exceptions.
- 修正建议: Incorporate data flow analysis to identify core I/O operations.；Use graph-based representations that capture control and data flow.；Include framework-specific knowledge to recognize common patterns like proxying.

### case_id=3791 FP lexical_or_api_overlap

- 方法: `getRequestContent` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens a URL, reads the first line, and returns it.
- B 摘要: Opens a URL with optional authentication, reads all lines, writes them to a temporary file, and updates a status label.
- 静态失败原因: High lexical overlap in URL reading boilerplate (URL, openConnection, BufferedReader) led the model to overestimate similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have significantly different side effects and output, despite sharing some reading logic.
- 共享行为: Both open a URL and read lines via BufferedReader and InputStreamReader.
- 行为差异: A returns a single line; B writes all lines to a file and updates UI.；A does not handle authentication; B does.；A returns a value; B is void.
- 修正建议: Incorporate dataflow analysis to distinguish return values vs file writes.；Use contrastive learning to emphasize functional differences over API overlap.

### case_id=3792 FN benchmark_preference_bias

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file using FileChannel, with canonical path check and proper resource cleanup.
- B 摘要: Launches a NexOpen project configuration, performing project validation, XML handling, business profile processing, and file generation.
- 静态失败原因: The static model correctly predicted non-clone; it did not fail. The BCB label is inconsistent.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this as clone erroneously; there is no plausible partial functionality or Type-3/4 similarity. Possibly a labeling error in the benchmark.
- 行为差异: copyFile performs low-level file I/O; launch involves Eclipse API, project management, and XML parsing.；copyFile has no dependencies; launch depends on Eclipse, Hibernate, and Maven plugins.；copyFile is static and straightforward; launch is an override method with complex control flow.；No overlapping functionality or shared goals.
- 修正建议: Re-evaluate the BCB label for this pair; it appears to be a false positive.；If the benchmark intends broad clones, consider if there is any hidden similarity (e.g., both throw IOException/CoreException?), but still insufficient.

### case_id=3793 FP other

- 方法: `readData` vs `decodeBody`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads comma-separated tokens from static strings to initialize multiple HashSets and a map for valid sequences, and processes a configuration file to fill additional data structures.
- B 摘要: Decodes a MIME body by wrapping the input stream in a decoder if needed, then copies it to a temporary file body and returns the body.
- 静态失败原因: The model likely focused on surface-level patterns like loops and set operations in readData, while decodeBody has none; the error may come from unrelated boilerplate overlap or the truncated part of readData, but overall the prediction is a clear false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels non-clone because the functions perform entirely different tasks with no shared subfunctionality.
- 行为差异: readData initializes in-memory data structures from static strings; decodeBody processes an InputStream from an outside source.；readData uses StringTokenizer and HashSets; decodeBody uses InputStream, OutputStream, and specific decoder classes.；readData is a void method with side effects; decodeBody returns a Body object.；readData involves parsing configuration lines and error handling; decodeBody is a straightforward transformation.
- 修正建议: Improve model sensitivity to method name and signature differences.；Incorporate data flow analysis to distinguish I/O operations.；Use more context beyond local token overlap to infer purpose.

### case_id=3794 FN partial_functionality

- 方法: `main` vs `unJar`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts all its entries to files.
- B 摘要: Extracts a specific entry from a local JAR file to a file.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on low token overlap (0.094) and different method names, class context, and API calls (URL vs JarFile), failing to recognize the semantic similarity of the extraction logic due to surface-level control flow and I/O differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as clone because both functions share the core concept of extracting files from an archive, and the differences (download vs local, all vs one) are considered acceptable variations in Type-3/Type-4 clones.
- 共享行为: Both extract entries from archive files (zip/jar) and write them to disk.
- 行为差异: A downloads from URL, B uses local file.；A extracts all entries, B extracts a single entry.；A uses ZipInputStream, B uses JarFile.；A prints extraction info, B handles path creation and returns path.
- 修正建议: Use data augmentation with input/output examples.；Train on more diverse extraction patterns.；Incorporate control flow normalization.

### case_id=3795 FN partial_functionality

- 方法: `getResourceAsStream` vs `copyParseFileToCodeFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource by name, caches it locally after an HTTP GET, and returns an InputStream.
- B 摘要: Copies a file from one location to another using a buffer.
- 静态失败原因: The low token Jaccard similarity (0.13) and different method names, combined the extensive surrounding code in A that is absent in B, likely caused the model to focus on the overall function rather than the embedded copy pattern, leading to a non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as performing a 'file/stream copy' operation, and the core copy loop in A is functionally similar to the entirety of B, thus labeling them as Type-4 clones despite overall different purposes.
- 共享行为: Both read from an InputStream and write to an OutputStream in a loop.
- 行为差异: Function A involves URL resolution, HTTP connection, caching logic, and extensive error handling; function B is a simple file copy without caching or network I/O.；Function A returns an InputStream; function B returns void.；Function A is public synchronized; function B is private.
- 修正建议: Train models to detect functional sub-patterns or clone fragments.；Use data-flow analysis to identify common I/O operations.；Incorporate hierarchical representations that separate subsidiary operations from the main logic.

### case_id=3796 FP lexical_or_api_overlap

- 方法: `readData` vs `doGet`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated strings into sets and processes a file to build internal mappings
- B 摘要: Serves a static file from the filesystem to an HTTP response
- 静态失败原因: Static BERT models may have relied on common API terms like 'IOException' and 'file', or on the presence of file-reading boilerplate, but missed the overall semantic difference
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels such pairs as non-clones because the functions have completely different purposes and structures, despite both using file I/O
- 共享行为: Both involve reading from a file
- 行为差异: A parses many string tokens into sets and handles complex error conditions; B simply copies file content to output；A builds various hash maps and sets; B does not modify any data structures；A is a private static void method for initialization; B is a servlet doGet method
- 修正建议: Include more negative examples of unrelated functions that share I/O boilerplate；Use a model that captures higher-level semantics and function purpose

### case_id=3797 FP lexical_or_api_overlap

- 方法: `writeFileType` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a list of URIs from a file, fetches each URL's content up to 100 lines, detects presence of OWL/RDFS/RDF namespaces, and writes classification to an output file.
- B 摘要: Loads an OSGi FrameworkFactory implementation by reading a service configuration file from the classpath and instantiating the class.
- 静态失败原因: Static BERT/GraphCodeBERT models may over-rely on shallow lexical and API usage patterns (e.g., BufferedReader, URL, readLine, try-catch) and miss the higher-level semantic intent due to limited contextual understanding of the overall task.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: Human annotators in BCB consider these non-clones because the overall functionality is completely different, despite similar I/O patterns. They are Type-4 (different functionality) and not semantically equivalent.
- 共享行为: Both use BufferedReader to read lines from a stream.；Both open a URL/URLConnection and read lines.；Both handle exceptions using try-catch blocks.
- 行为差异: Different goals: document classification vs service loading.；Different input sources: file list of URIs vs classpath resource.；Different output: write classification to file vs return an object instance.；Different line processing: check for keywords vs check for non-comment lines and instantiate class.
- 修正建议: Incorporate data flow or control flow graphs to better capture program semantics.；Use contrastive learning to distinguish between similar API usage but different tasks.；Add more global context (method name, class name, imports) to disambiguate.

### case_id=3798 FN benchmark_preference_bias

- 方法: `doGet` vs `CopyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to serve a portal page, including authentication, caching, and logging.
- B 摘要: Copies a file from source to destination using NIO channels, ensuring parent directories exist.
- 静态失败原因: The model correctly identified the low token overlap (0.062) and distinct syntactic structures (servlet vs. file utilities), leading to a non-clone prediction. This aligns with strict semantic equivalence but disagrees with the BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a Type-4 clone because both functions involve file system interactions (writing to files) and some error handling, despite being otherwise unrelated. The annotation might be overly broad or reflect a focus on partial functionality overlap.
- 共享行为: Both perform file I/O operations (reading/writing files).；Both include error handling and logging.
- 行为差异: A is an HTTP request handler with complex control flow; B is a simple utility method.；A uses servlet API and portal framework; B uses NIO channels and standard file operations.；A conditionally caches page output to a file; B always copies a file completely.；A handles authentication, page visibility, and logging; B only handles file copying.
- 修正建议: Clarify BCB annotation guidelines to avoid overly broad Type-4 classifications.；Use semantic clustering or task-specific filtering to reduce such false positives in training data.

### case_id=3799 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a newer version of jEdit by reading a version file from a URL and comparing build numbers.
- B 摘要: Sends an HTTP POST request to a URL with parameters and returns the response body as a string.
- 静态失败原因: Static BERT/GraphCodeBERT may over-rely on common API sequences (URL, openStream, BufferedReader, readLine) and ignore the overall program logic and different input/output structures, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels based on functional equivalence. These two functions have different purposes and different I/O behavior, so BCB correctly labels as non-clone.
- 共享行为: Both open a URL connection and read data using BufferedReader；Both handle IO exceptions；Both use try-catch blocks
- 行为差异: Function A performs a GET request for version check; Function B performs a POST request with custom parameters；Function A outputs to GUI; Function B returns a string；Function A parses specific lines; Function B reads all lines；Function A uses jEdit properties; Function B is generic
- 修正建议: Improve model's ability to differentiate high-level semantics beyond API usage；Include control flow and data flow features to capture differences in I/O behavior

### case_id=3800 FP lexical_or_api_overlap

- 方法: `getNetworkServersIPs` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a server list from a URL to extract IP addresses.
- B 摘要: Parses a YouTube page to extract video parameters and construct a fullscreen URL.
- 静态失败原因: Static BERT models focus on lexical and API token overlap, missing the distinct semantic intents. The high similarity in common APIs (URL, URLConnection, BufferedReader, readLine, split) and control flow (while loop, try-catch) misled the model into classifying as clone.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the two functions serve entirely different purposes (server IP extraction vs. YouTube URL construction) despite sharing boilerplate URL reading code.
- 共享行为: Both open a URL connection and read lines from the input stream.；Both use BufferedReader and while loop to read lines.；Both parse lines using conditional checks and string operations.；Both handle exceptions with printStackTrace or error messages.
- 行为差异: Function A extracts IP addresses from server lines prefixed with '!SERVERS', while B extracts video_id, t, title from a line containing 'fullscreenUrl'.；Function A returns a Vector of Strings (IPs), B returns a single String (full URL).；Function A uses a boolean flag to toggle parsing state, B does not.；Function B sets progress bar indeterminate and updates class field ytTitle, A has no UI interaction.
- 修正建议: Incorporate data flow and control flow features to distinguish different data transformations.；Use program dependency graphs to capture output types and value flows.；Add domain-specific embeddings or task classification to reduce false positives from boilerplate overlap.

### case_id=3801 FP lexical_or_api_overlap

- 方法: `callApiPost` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs an HTTP POST request to an API with parameters, validates the response code, and returns the response input stream.
- B 摘要: Imports biological sequences from a URL by reading FASTA-like format, extracting names and sequences, and storing them in lists.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by overlapping tokens like 'URL', 'InputStream', 'IOException', 'catch', and the general try-catch boilerplate structure, ignoring the distinct business logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones for functions with different high-level purposes despite sharing low-level I/O patterns. The token Jaccard is very low (0.09), and the semantics are unrelated.
- 共享行为: Both open a connection to a URL and read an InputStream.
- 行为差异: Function A makes an HTTP POST request with parameters; Function B reads from a URL without writing (implicit GET).；Function A checks the HTTP response code and throws an exception if not expected; Function B does not check response codes.；Function A handles timeouts, sets headers, and uses PrintStream to write parameters; Function B uses a custom ImportHelper to parse a FASTA-like format.；Function A returns an InputStream; Function B populates member lists with parsed data.
- 修正建议: Improve model's ability to distinguish between generic I/O patterns and specific functional logic.；Incorporate more robust dataflow analysis or program dependence graphs to capture the actual data transformations.；Use contrastive learning with hard negative examples that share API calls but differ in purpose.

### case_id=3802 FP boilerplate_overlap

- 方法: `run` vs `readReferenceText`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a tile from a URL, parses it into geometric features, and adds them to a data layer with duplicate request prevention.
- B 摘要: Reads a reference text file from a bundle resource URL and returns its content as a string.
- 静态失败原因: The model likely overemphasized the overlapping I/O tokens (URL, InputStream, BufferedReader, readLine) and ignored the distinct surrounding logic and side-effect patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates based on overall functionality; these functions have different purposes and only share a common I/O boilerplate, so BCB would label them as non-clones.
- 共享行为: Both open a URL input stream, wrap it with BufferedReader, and read lines into a string buffer.
- 行为差异: Function A is void and has side effects (modifying data structures); Function B returns a string with no side effects.；Function A processes the read content into geometry objects; Function B returns the raw text.；Function A includes duplicate request checking and synchronization; Function B does not.；Error handling differs: A logs and returns; B logs and throws an exception.
- 修正建议: Incorporate data-flow and control-flow analysis to distinguish core functionality from boilerplate.；Use contrastive learning with hard negative examples that share code patterns but differ in intent.

### case_id=3803 FN partial_functionality

- 方法: `getFile` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint attribute, and saves it to a temporary local file, returning the file path.
- B 摘要: Copies a file from one local file path to another using FileChannel transfer.
- 静态失败原因: Static BERT/GraphCodeBERT models often rely on lexical overlap and API sequence similarity. Here, token Jaccard similarity is very low (0.111), and the API usage differs (ReadableByteChannel vs FileChannel, URL vs local file). The model likely focused on the low token overlap and different method signatures, failing to recognize the partial functional similarity in the file transfer operation. Additionally, the complex control flow in A (XML parsing, conditional download) may have obscured the shared sub-behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because function A contains a sub-task that is functionally similar to function B: both transfer bytes from an input source to a file. Specifically, A uses channelOut.transferFrom to download, which is analogous to B's transferTo. This partial functionality overlap is often accepted as a Type-4 clone under BCB's broad criteria.
- 共享行为: Both perform file I/O operations involving channels (ReadableByteChannel/FileChannel)；Both handle resource cleanup (closing channels/streams)；Both involve transferring data from an input source to a file output stream
- 行为差异: Function A downloads from a URL (network I/O) while B copies between local files；Function A involves XML parsing and manipulation, B does not；Function A returns the file path, B returns void；Function A has extensive error handling for multiple exceptions, B only throws IOException
- 修正建议: Improve model's ability to detect partial functionality by incorporating subgraph matching or focused attention on code regions；Use data augmentation that extracts sub-functions and treats them as separate clone candidates；Train on examples where one method contains a superset of another's functionality

### case_id=3804 FN partial_functionality

- 方法: `read` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a UTF-8 encoded skeleton file from classpath, splits into sections based on '---' delimiter, appends newlines, and validates section count.
- B 摘要: Reads a file from filesystem or classpath, concatenates all lines into a single string without newlines, prints canonical path, and exits on error.
- 静态失败原因: Low token Jaccard (0.2045) and different method signatures, exception handling, and processing logic caused the model to miss the conceptual similarity of reading from a resource.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones because both perform the high-level task of reading a text resource and processing its lines, with similar I/O patterns (BufferedReader, while loop, classpath loading). Differences in encoding, delimiters, and error handling are often tolerated in broad Type-3/Type-4 annotations.
- 共享行为: Both read text line by line from a resource using BufferedReader；Both handle resource location via classpath or file system alternatives
- 行为差异: Function A splits into sections by '---'; Function B concatenates all lines；Function A uses UTF-8; Function B uses default encoding；Function A appends newlines to each line; Function B does not；Function A throws exceptions; Function B prints and exits with -1
- 修正建议: Use dataflow-aware models that capture I/O sequences and resource loading patterns；Incorporate AST-based matching for structural similarity；Expand training data with diverse resource reading functions

### case_id=3805 FN benchmark_preference_bias

- 方法: `getFile` vs `testCopy_inputStreamToOutputStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL from a given URL, optionally modifies an endpoint address in the XML, and saves the result to a temporary file, then returns the file path.
- B 摘要: Tests that copying an InputStream to an OutputStream works correctly by using IOUtils.copy and asserting content equality.
- 静态失败原因: The static BERT model correctly identified them as non-clones (prediction 0), aligning with semantic differences. The 'misclassification' here is actually a BCB labeling error, so the model did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to a coarse categorization (e.g., both involve I/O stream operations) or a mislabel in the benchmark. The shared I/O stream usage is too superficial to consider them functionally similar.
- 共享行为: Both involve using InputStream, OutputStream, and basic I/O operations like reading and writing bytes.
- 行为差异: Function A (getFile) performs network download, XML parsing/modification, file management, and error handling specific to AxisFault.；Function B (testCopy_inputStreamToOutputStream) is a unit test that only copies one stream to another and verifies the result; it does not involve file creation, network, or XML.；Function A returns a file path string; Function B returns void and uses assertions.；Function A handles multiple exception types; Function B throws Exception.
- 修正建议: Consider adding context-awareness (e.g., distinguish test vs production code).；Use finer-grained semantic categories to avoid false positive clones in benchmarks.

### case_id=3806 FN benchmark_preference_bias

- 方法: `init` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Initializes servlet by loading controller classes from a registry file read via classpath resources.
- B 摘要: Downloads OPDS catalog or book data from HTTP URLs, parsing XML and handling pagination.
- 静态失败原因: The model correctly predicted non-clone based on low token overlap and clear semantic differences, but BCB labeled it as clone, suggesting the model's static representation missed a possible broad functional similarity that BCB valued.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered these clones due to both involving URL opening, stream reading, and exception handling, but the high-level functionality and implementation details are vastly different, making this an unlikely clone even under broad Type-3/4 criteria.
- 共享行为: Both open URLs and read input streams；Both handle IO exceptions；Both use logging for debugging
- 行为差异: Function A loads classes from classpath resources; function B downloads network content；Function A processes lines of class names; function B processes XML entries and downloads files；Function A uses ClassLoader and addClass; function B uses HttpURLConnection and callbacks；Function A is a simple linear read; function B has a loop with continuation and pagination
- 修正建议: Clarify BCB annotation guidelines to avoid labeling pairs with different high-level purposes as clones；Incorporate data flow analysis to distinguish between class loading and network download patterns

### case_id=3807 FN long_range_semantics

- 方法: `scrapeForIsbns` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Scrapes a webpage for ISBN-10 patterns using regex and returns the count of matches, with retry on connection failures.
- B 摘要: Sends an XML request to a GeoParser web service, parses the response to extract place names and gazetteer IDs, with retry on exceptions.
- 静态失败原因: A static model like GraphCodeBERT relies on lexical and structural similarities. These functions have low token Jaccard similarity (0.125) and different API calls, method names, and data types. The model likely fails to capture the abstract behavioral pattern of 'fetching with retries' because it is buried in different concrete implementations.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often considers functions as clones if they share a common high-level algorithmic pattern, such as fetching data from a URL with retries and parsing the response. Even though the details differ, the overall structure is similar enough for a Type-3/Type-4 clone classification.
- 共享行为: Both functions fetch data from a URL with retry logic on exceptions.；Both read line by line from an input stream obtained from the URL.；Both parse the retrieved content (regex or XML) to extract relevant information.；Both collect extracted data into a structure (set or list) and return it.
- 行为差异: Function A scrapes ISBNs from HTML pages using a simple regex, while Function B uses a complex XML request and response parsing.；Function A counts matches and stores them in a map, returning an integer; Function B returns a collection of tuples.；Function A's retry logic is only for ConnectException, while Function B catches all exceptions.；Function A uses a fixed number of retries (5), Function B uses 3.
- 修正建议: Enhance model to capture high-level control flow patterns like retry loops with I/O.；Use program slicing or dataflow analysis to abstract away concrete details.；Incorporate structural templates or clone detection based on graph isomorphism of control flow.

### case_id=3808 FP lexical_or_api_overlap

- 方法: `getUser` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from a DAO or a config file by reading lines from a resource URL.
- B 摘要: Constructs a Swing GUI browser that fetches XML from a URL and renders it as HTML.
- 静态失败原因: The static model likely overemphasized common tokens like 'URL', 'BufferedReader', 'openStream', and 'readLine', leading to a false positive despite low Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these as non-clones because they perform entirely different high-level tasks (user authentication vs. GUI initialization) with no functional overlap.
- 共享行为: Both read from a URL using BufferedReader and InputStreamReader.
- 行为差异: Function A retrieves a User object; Function B builds a GUI window.；Function A handles authentication logic; Function B handles XML parsing and transformation.；Function A returns a User; Function B does not return anything (constructor).；Function A uses StringTokenizer; Function B uses complex XML and XSLT processing.
- 修正建议: Incorporate control flow and call graph information.；Use type information to distinguish return types and external API calls.；Train on broader functional contexts to reduce reliance on surface-level API patterns.

### case_id=3809 FP long_range_semantics

- 方法: `actionPerformed` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles GUI action commands to configure Graphviz, ImageMagick, and other settings, storing preferences and updating UI.
- B 摘要: Copies a file from source to destination directory using a buffer, handling IOExceptions.
- 静态失败原因: The model likely over-generalized from superficial token overlap (e.g., 'File', 'String', 'Exception') or misinterpreted the long, branching structure of A as similar to B's control flow, missing the semantic difference.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotates non-clones when functions have entirely different overall goals, even if they share low-level operations; here goals are completely unrelated.
- 共享行为: Both use File objects
- 行为差异: A is an event handler that updates GUI preferences; B is a utility for file copy；A involves user interaction via JFileChooser; B uses file streams；A writes to preferences and enables/disables UI components; B reads and writes file bytes；A handles multiple commands and has complex logic; B is a straightforward copy loop
- 修正建议: Incorporate control and data flow analysis to capture overall program purpose；Use graph-based representations like AST or CFG to compare function structure；Train on more diverse non-clone pairs with long functions

### case_id=3810 FN partial_functionality

- 方法: `getFile` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint attribute, and saves to temporary directory.
- B 摘要: Copies a file from source to destination using a byte buffer.
- 静态失败原因: Low lexical overlap (Jaccard 0.1085) and different method names, plus extra XML manipulation and logging in A that are absent in B, led the model to predict non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'file copying' operations despite different sources and additional logic, focusing on the core I/O transfer.
- 共享行为: Reads data from a source (URL stream or file) and writes to a destination file using an output stream.
- 行为差异: A downloads from a network URL; B copies from a local file.；A modifies XML and logs extensively; B is a simple copy.；A returns a file path; B returns void.；A handles multiple exception types; B only handles IOException.
- 修正建议: Use dataflow analysis to detect byte transfer from input to output.；Normalize method names or incorporate semantic role labeling.；Consider structural similarity of try-catch-finally blocks.

### case_id=3811 FN boilerplate_overlap

- 方法: `getEncoding` vs `postData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts character encoding from an HTTP response by checking the Content-Type header and then the response body.
- B 摘要: Sends an HTTP POST request with provided data and consumes the response.
- 静态失败原因: Static BERT models rely on token similarity and method signatures; low token Jaccard (0.2169) and different method names (getEncoding vs postData) caused the model to miss the shared low-level I/O pattern. The model overfits to unique identifiers and specific API calls.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers both as HTTP communication utilities with similar structural patterns (URLConnection, stream handling, header manipulation), viewing them as Type-4 semantic clones despite different specific tasks.
- 共享行为: Open a URLConnection to a given URL；Read from the connection's input stream using BufferedReader；Access or set HTTP headers；Close streams and connections
- 行为差异: Function A reads headers and body to find charset; Function B sends data via output stream and ignores the response body；Function A sets doInput but not doOutput; Function B sets both doOutput and doInput；Function A returns a string encoding; Function B returns void；Function A uses PrintStream to write data; Function A does not write data
- 修正建议: Train with more functions that share I/O boilerplate but differ in specific logic to learn structural patterns.；Use graph-based models (e.g., graph neural networks) that capture data flow and control flow, reducing sensitivity to variable names.；Incorporate contrastive learning with pairs that have high structural but low textual similarity.

### case_id=3812 FN partial_functionality

- 方法: `doVersionCheck` vs `runScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for version updates by reading version info from a URL.
- B 摘要: Reads a script from a URL and returns its content as a string.
- 静态失败原因: Static BERT models often rely on token-level overlap and syntactic similarity, which is low here (Jaccard=0.214). They miss the high-level semantic pattern of URL-based I/O due to different method names, return types, and internal processing logic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone because both functions share the core pattern of fetching data from a URL and handling I/O exceptions, which is a common semantic clone type (Type-3/4) despite differences in the specific processing of the fetched content.
- 共享行为: Both open a URL using java.net.URL；Both read from an InputStream obtained from the URL；Both handle exceptions (IOException/Exception) with error handling
- 行为差异: A reads line-oriented and parses key-value pairs; B reads byte-by-byte and concatenates；A compares versions and shows UI messages; B returns the raw data string；A uses a BufferedReader; B uses a BufferedInputStream；A closes the stream; B does not explicitly close the stream
- 修正建议: Incorporate structural features like control-flow graphs to capture common I/O patterns；Use graph-based models that can represent data flow and call sequences；Augment training with more diverse examples of the same I/O pattern

### case_id=3813 FP boilerplate_overlap

- 方法: `SRWGuiClient` vs `wordFrequency`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Constructor that creates a GUI browser, reads XML from a URL, optionally applies XSLT transformation, and displays HTML content.
- B 摘要: Method that fetches a web page, searches for a regex pattern matching a frequency result, and returns the integer count.
- 静态失败原因: Static BERT likely focused on common API tokens like 'URL', 'BufferedReader', 'try-catch', and 'IOException', which appear in both functions, leading to a false positive. The model lacked understanding of the overall program intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the overall functionality is completely different: one is a GUI browser constructor, the other is a word frequency counter. Despite shared I/O patterns, the high-level purpose is distinct.
- 共享行为: Both open a URL and read data using BufferedReader；Both handle IOException
- 行为差异: Function A builds a GUI window, function B returns an integer；Function A processes XML and optionally applies XSLT, function B does regex matching on lines；Function A has complex GUI setup and event handling, function B is purely computational；Function A is a constructor, function B is a method
- 修正建议: Incorporate structural information (e.g., class name, method signature) to capture high-level purpose；Use graph-based models that capture data flow and control flow differences；Train on more diverse examples that emphasize functional dissimilarity despite lexical similarity

### case_id=3814 FN partial_functionality

- 方法: `doTransfer` vs `getNetworkServersIPs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request to another URL, acting as a proxy.
- B 摘要: Downloads a server list from a URL and parses IP addresses from lines starting with '!SERVERS'.
- 静态失败原因: Low token overlap (0.167) and different method names/signatures caused the model to miss the weak commonality of URL reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered both as network utility functions that open a URL and process incoming data, but this is too broad and likely a mislabel.
- 共享行为: Both open a URL connection and read from it
- 行为差异: A performs HTTP proxy with bidirectional data transfer; B only reads and parses text data；A uses HttpServletRequest/Response; B returns a Vector of strings；A handles request headers and methods; B has no concept of HTTP methods；A writes to the response; B has no output beyond return value
- 修正建议: Use AST-based features to capture shared API usage (URL, openConnection)；Incorporate data flow analysis to highlight both functions read from a URL connection

### case_id=3815 FN partial_functionality

- 方法: `getFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies the endpoint, and saves it to a temporary location.
- B 摘要: Reads page configurations, applies XSLT transformations, and writes output files for site editing.
- 静态失败原因: Static BERT models rely heavily on token overlap and method signatures; the low Jaccard similarity (0.106) and different method names ('getFile' vs. 'buildSiteForEdit') likely led to a non-clone prediction. The models may miss the shared structural patterns of file and XML processing that BCB considers.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as clone due to both functions performing similar low-level operations like file reading/writing, XML parsing, and exception handling, which are common patterns across many Java I/O utilities.
- 共享行为: File I/O operations；XML parsing and manipulation；Exception handling with logging；Use of temporary files or file channels
- 行为差异: Purpose: downloading WSDL vs. building site pages；Function A handles a single file; Function B iterates over multiple pages；Function A modifies WSDL endpoint; Function B applies XSLT transformations
- 修正建议: Improve model's ability to recognize structural clones beyond token overlap；Incorporate control flow and data flow features；Use graph-based representations to capture common I/O patterns

### case_id=3816 FP long_range_semantics

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Main method that parses a Prolog file, generates adapter JAR classes, and writes serialized adapter layer.
- B 摘要: Utility method that copies a file from one location to another using FileChannel.
- 静态失败原因: The static BERT model likely overemphasized superficial similarities like exception handling (try-catch, IOException), file-related classes (File, FileChannel, FileInputStream), and method signatures with void return, while missing the vastly different context and purpose due to limited understanding of long-range dependencies and library-specific semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labeled non-clone because the functions are semantically unrelated: one is a main routine for adapter generation, the other is a file copy utility. Even under broad Type-4 categorization, they do not share a common computational goal.
- 共享行为: Both involve file operations
- 行为差异: Code A is a complex program entry point with command-line parsing, parsing, and code generation; Code B is a simple file copy routine.；Code A writes multiple class files and serialized data; Code B only copies a single file.；Code A uses Prolog-specific parsing and adapter generation; Code B uses NIO channels.
- 修正建议: Improve model sensitivity to high-level task structure and intent.；Incorporate dataflow or program dependence information to distinguish between orchestration code and utility functions.

### case_id=3817 FP lexical_or_api_overlap

- 方法: `get` vs `CheckUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches an array of GameRecord objects from a URL using GET with latitude, longitude, and count headers, skipping comment lines.
- B 摘要: Fetches the first line of content from a URL using GET and returns it as a string.
- 静态失败原因: Static models may over-rely on lexically similar tokens (e.g., URL, HttpURLConnection, BufferedReader, getInputStream) and miss semantic differences due to different parameter handling, different output types, and different decoding logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones if functions have distinct return types, different parameter usage, and different processing logic, even if they share common boilerplate code for HTTP GET.
- 共享行为: Both perform an HTTP GET request to a URL and read data from the response using BufferedReader.
- 行为差异: Function A sets custom headers for location and count, filters out comment lines, and returns an array of GameRecord objects; function B returns the raw first line.；Function A has error handling returning null on failure; function B catches exceptions and returns empty string on error.；Function A checks response code and prints message on non-OK; function B ignores response code.
- 修正建议: Train with more contrastive examples of HTTP GET functions with different purposes.；Include structural features like return type and parameter count.；Use a model that captures dataflow beyond token overlap.

### case_id=3818 FP lexical_or_api_overlap

- 方法: `get` vs `retrieveQ`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves an array of GameRecord objects from a game server via HTTP GET with location headers, filtering comment lines.
- B 摘要: Retrieves the entire content of a URL as a single string, printing response message to stderr.
- 静态失败原因: The static BERT/GraphCodeBERT model may have focused on the token overlap (e.g., 'URL', 'openConnection', 'BufferedReader', 'readLine', 'InputStream', 'HttpURLConnection') and similar structure (opening connection, reading lines) without capturing the distinct data transformations and error handling that differentiate the methods.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because despite both performing HTTP GET, the data processing and return types are fundamentally different; the methods serve different purposes (retrieving game records vs raw text retrieval).
- 共享行为: Both make HTTP connections and read response line by line using BufferedReader.
- 行为差异: Function A filters out lines starting with '#' and decodes each line as a GameRecord, then returns an array; Function B concatenates all lines with newlines and returns a single string.；Function A uses custom headers (latitude, longitude, count) and checks HTTP_OK; Function B does not set custom headers and does not check response code before reading.；Exception handling differs: A catches IOException and prints stack trace, B throws MalformedURLException and IOException.
- 修正建议: Incorporate control-flow and data-flow information to distinguish transformation logic beyond API usage.；Use more granular semantic embeddings that capture return type and data processing patterns.；Add AST-based features to highlight differences in loop body and conditionals.

### case_id=3819 FN partial_functionality

- 方法: `serialize` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Serializes a content package to an output stream by writing to a temporary file and copying.
- B 摘要: Builds a website for editing by processing pages, applying XSLT transformations, and writing output files.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed to capture the clone relationship because of very low token overlap (Jaccard 0.05), different method names, and vast difference in code length and complexity, making it unable to see the weak partial similarity in file operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to both being part of a content management system and sharing low-level file I/O and exception handling patterns, despite very different high-level functionality.
- 共享行为: Both involve file I/O (reading/writing files or streams).；Both throw IOException.
- 行为差异: Function A is a short serialization utility; Function B is a long, multi-step site building routine.；Function A uses a temporary file and copies to an output stream; Function B writes directly to multiple output files.；Function A does no XML processing; Function B performs extensive XSLT transformations.；Function A has a simple single-output goal; Function B has many parameters and complex control flow.
- 修正建议: Use hierarchical or structural similarity metrics that can capture common I/O patterns.；Incorporate domain or library context to identify methods with similar roles in the system.；Re-evaluate BCB annotations for consistency, as this pair may be a false positive in BCB.

### case_id=3820 FP boilerplate_overlap

- 方法: `readData` vs `readAndRewrite`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses comma-separated string constants into various HashSets (topSet, leftSet, etc.) for Tibetan character sets.
- B 摘要: Reads a DICOM file, parses metadata, reads pixel data, and writes it to another file.
- 静态失败原因: Static predictor likely over-relied on superficial commonalities (method name prefix 'read', same visibility/static modifier, println calls) while missing the vast difference in domain-specific libraries and logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone (0) because the functions have no semantic or structural similarity; they belong to entirely different application domains.
- 共享行为: Both are private static void methods；Both use System.out.println for output
- 行为差异: Different domain: Tibetan text processing vs medical image DICOM I/O；Different API usage: StringTokenizer vs ImageIO/DcmParser；Different complexity and length
- 修正建议: Incorporate token-level IDF weighting to downplay common Java keywords；Add a domain classification module；Use a model that better captures long-range semantics and API usage patterns

### case_id=3821 FN benchmark_preference_bias

- 方法: `doGet` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request, retrieves a page by ID or name, checks user permissions, and renders the page with logging and caching.
- B 摘要: Entry point for Weka experiment setup GUI; parses command-line options, loads or creates an Experiment, displays a JFrame, and handles window closing with optional serialization.
- 静态失败原因: The static model likely relied on lexical and API overlap, which are minimal here (token Jaccard=0.093), and correctly predicted non-clone. The misclassification is due to BCB label possibly reflecting a high-level semantic similarity that is not captured by token-based models.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a Type-4 semantic clone because both functions serve as top-level orchestrators with similar structural patterns (input processing, error handling, logging), despite different domains and APIs.
- 共享行为: Both are entry points that process input, perform conditional logic, log information, and handle exceptions with try-catch blocks.
- 行为差异: A is a servlet method dealing with HTTP request/response; B is a standalone main method with command-line args.；A uses servlet APIs (HttpServletRequest, HttpServletResponse); B uses Swing, file I/O, and Weka classes.；A's core logic involves page retrieval and permission checks; B's core logic involves experiment serialization and GUI setup.
- 修正建议: Review BCB annotation guidelines for such cross-domain entry points; consider excluding pairs with low lexical overlap and different API domains from clone benchmarks.；Incorporate functional or semantic role classification (e.g., entry point, data processing) to refine clone detection thresholds.

### case_id=3822 FP lexical_or_api_overlap

- 方法: `run` vs `createDialogArea`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Asynchronously loads a tile from a data source, reads its content (HTTP or file), parses it into vector geometries, and adds them to a data loader.
- B 摘要: Creates a dialog area in an Eclipse plugin, reads a license file from the bundle, and displays it in a browser or text widget.
- 静态失败原因: Static BERT models may overemphasize surface-level token patterns, like the common code snippet of opening a URL, reading lines with BufferedReader, and appending to a StringBuffer. This overlap can trigger a false positive despite different overall semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically marks non-clones when functions differ significantly in purpose and data flow, even if sharing common I/O patterns. The low token Jaccard and distinct method contexts support a non-clone label.
- 共享行为: Both open a URL and read content line by line using BufferedReader.；Both handle IOException and print stack trace.；Both concatenate lines into a string (StringBuffer/StringBuilder).
- 行为差异: Function A retrieves tile data for mapping; Function B retrieves license text for UI.；Function A uses synchronization for HTTP request deduplication; Function B does not.；Function A parses geometry from GeoJSON and creates a GeometryCollection; Function B displays text in a Browser or Text widget.；Function A deals with multiple URL protocols and file I/O; Function B uses Eclipse bundle resources.
- 修正建议: Incorporate function-level context such as method name, class, and surrounding code.；Use data flow analysis to trace how the read data is used (e.g., geometry vs. text display).；Consider control flow and concurrency differences (e.g., synchronization in A vs none in B).

### case_id=3823 FN benchmark_preference_bias

- 方法: `main` vs `saveFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads a KMZ file from a URL, extracts its zip entries to files.
- B 摘要: Saves UI configuration (window positions, toolbars, sound settings) to an XML file.
- 静态失败原因: Static BERT models rely on lexical and structural overlap; the low token Jaccard (0.065) and distinct API usage led to a non-clone prediction, which aligns with semantic analysis but contradicts BCB's label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have considered both as file-writing operations with stream handling, but this is too superficial for a clone; likely an annotation error or overly broad type-4 categorization.
- 共享行为: Both write to files using FileOutputStream；Both handle exceptions and close streams
- 行为差异: Function A reads from a URL and unzips; Function B constructs XML and writes configuration；Function A uses ZipInputStream for extraction; Function B uses XMLOutputter and custom document building；Function A writes each zip entry as a separate file; Function B writes a single XML file with many attributes；Different control structures: while loop for entries vs. for loop over windows and toolbar units
- 修正建议: Improve semantic understanding by incorporating high-level task identification (e.g., file download vs. configuration save)；Use finer-grained functional similarity measures that distinguish between different domain operations；Re-evaluate BCB annotations for this pair to ensure consistency

### case_id=3824 FP boilerplate_overlap

- 方法: `main` vs `bootKernel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter code from a Prolog file, handling errors and writing output jars.
- B 摘要: Boots a kernel from a configuration file, copying assets and loading a kernel class.
- 静态失败原因: Static BERT models may overestimate similarity due to overlapping boilerplate code (file I/O, exception handling) and common API tokens (e.g., File, InputStream, Log), ignoring the completely different overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels 0 because the functions are semantically unrelated; they only share trivial patterns like exception handling and file operations, which is insufficient for clone detection.
- 共享行为: Both use try-catch for error handling；Both perform file I/O operations
- 行为差异: Different input formats (Prolog vs config properties)；Different output actions (generate code vs boot kernel)；Different library usage and domain
- 修正建议: Incorporate task-level or domain-level embeddings；Use dataflow or call graph features to capture semantic differences；Apply contrastive learning to distinguish boilerplate from real logic

### case_id=3825 FN partial_functionality

- 方法: `writeConfiguration` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Writes a configuration resource to a Writer by copying its input stream, with error handling for null resource.
- B 摘要: Launches a NexOpen project configuration, processing XML POM files, setting Hibernate properties, and executing project installation actions.
- 静态失败原因: Static BERT models rely on token overlap and syntactic structure; low Jaccard similarity (0.0857) and different method names led to a non-clone prediction, but it missed the potential high-level semantic similarity in configuration handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might have labeled this as a clone based on a broad interpretation of 'configuration writing' behavior, as both functions involve configuration resources and stream copying, despite vastly different contexts and complexity.
- 共享行为: Both use IOUtils.copy for stream copying；Both handle input/output streams；Both have error handling patterns (IOUtils.closeQuietly or try-finally)
- 行为差异: Function A is a simple single-purpose stream copy; Function B is a complex multi-step launch procedure；Function B involves XML DOM parsing, file existence checks, property setting, and project job scheduling；Function A writes to a Writer; Function B writes to ByteArrayOutputStream and creates files；Function B includes extensive exception handling and use of Eclipse/IDE specific APIs
- 修正建议: Enhance model to capture high-level semantic roles (e.g., both are 'configurators') via context-aware embeddings or program analysis；Incorporate API call patterns (e.g., IOUtils.copy) as features for broader functional similarity

### case_id=3826 FP lexical_or_api_overlap

- 方法: `main` vs `testCopy_inputStreamToOutputStream`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that reads a Prolog file, parses it, and generates adapter classes and resources into a JAR file.
- B 摘要: Test method that verifies copying from an input stream to an output stream using IOUtils.copy, checking that all bytes are copied correctly.
- 静态失败原因: The model may have been misled by the presence of similar API calls like ByteArrayOutputStream and stream copying patterns, causing a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: The BCB annotation for this pair is non-clone (0), likely because the functions have completely different purposes and implementation despite sharing some low-level stream operations.
- 共享行为: Both involve reading from a source and writing to a destination using streams
- 行为差异: A is a complex code generation pipeline with parsing, reflection, and JAR writing; B is a simple I/O copy test；A uses many domain-specific classes (PrologParser, FactVisitor, etc.); B uses generic IOUtils；A produces a JAR file as output; B produces a ByteArrayOutputStream for verification
- 修正建议: Improve training to focus on high-level semantics rather than low-level API usage；Incorporate control flow and data flow analysis to distinguish main functionality

### case_id=3827 FN partial_functionality

- 方法: `main` vs `testReadPerMemberSixSmall`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.45`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, unzips it, and extracts all entries to files.
- B 摘要: Tests reading multiple GZIP members by copying each to a null output stream and verifying byte counts.
- 静态失败原因: Low token overlap (Jaccard=0.108) and different API usage (ZipInputStream vs GZIPMembersInputStream, FileOutputStream vs NullOutputStream) mislead the model into classifying as non-clone, despite superficial similarity in high-level task structure.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators may consider both as examples of 'reading compressed streams and processing individual entries/members', a broad Type-4 partial functionality similarity, overlooking the specific compression format (zip vs gzip) and output behavior.
- 共享行为: Both read compressed data from an input stream (zip vs gzip).；Both iterate over multiple compressed entries/members.
- 行为差异: A uses ZipInputStream, B uses GZIPMembersInputStream.；A writes entries to files, B discards output via NullOutputStream.；A is a standalone main method, B is a unit test with assertions.；A has URL handling and file I/O, B uses preloaded byte array.
- 修正建议: Improve coverage of abstract functionality patterns (e.g., streaming decompression).；Use more robust representation that captures data flow between compression stream and output.；Consider fine-tuning on BCB's broad Type-4 annotations with low token overlap.

### case_id=3828 FN partial_functionality

- 方法: `File2String` vs `getXML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file from local filesystem or classpath resource and returns its content as a string, with error handling that prints messages and exits the program on failure.
- B 摘要: Fetches XML from a servlet URL, URL-encoding the request, and returns the content as a string, returning null on errors.
- 静态失败原因: Static BERT/GraphCodeBERT models often rely on token and syntactic similarity. Here, the token Jaccard is low (0.2985), method names differ, parameters differ, and error handling differs, so the model likely missed the abstract behavioral similarity of the core reading loop.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a clone because both functions implement the common pattern of reading all lines from a source and returning as a single string, which is considered similar functionality despite differences in I/O source and error handling.
- 共享行为: Both read lines from an input stream and concatenate them into a StringBuffer to produce a single string result.
- 行为差异: A reads from a local file or classpath while B reads from a URL.；A prints messages and calls System.exit on error while B returns null.；A uses a fallback mechanism to try different sources; B does not.
- 修正建议: Train models on a wider variety of I/O functions to recognize abstract patterns like read-all-lines.；Incorporate dataflow or control flow analysis to capture the essential line-read-and-append sequence regardless of surrounding code.

### case_id=3829 FN lexical_or_api_overlap

- 方法: `getFile` vs `createJAR`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies XML attributes, and saves to a temporary file, returning the file path.
- B 摘要: Creates a JAR file by copying a resource from the classpath, then serializes an object into a document within that JAR directory.
- 静态失败原因: The static model likely focused on lexical tokens and method names, resulting in low similarity (Jaccard 0.167) and missing the underlying semantic overlap in the file I/O pattern. The different return types and APIs also misled the model into predicting non-clone.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a clone because both functions perform a similar file transfer operation using FileChannel and create files, which is a non-trivial shared behavior. The broad Type-4 annotation in BCB accepts partial functional similarity, and the core file copy pattern is considered semantically similar despite different contexts.
- 共享行为: Use FileChannel to transfer data between input and output streams；Create new files or write to files；Use temporary files or directories；Involve file I/O operations with exception handling
- 行为差异: Source of data: URL (A) vs. classpath resource (B)；Purpose: Retrieve and modify WSDL (A) vs. create JAR with serialized object (B)；Return type: String (A) vs. void (B)；Exception handling: Specific exceptions (A) vs. generic Exception (B)
- 修正建议: Incorporate structural similarity analysis for file I/O patterns；Use graph-based representations to capture data flow of channels and streams；Train on cross-contextual semantics using contrastive learning with API call sequences

### case_id=3830 FN partial_functionality

- 方法: `getFileContentAsString` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file from a given path or classpath resource and returns its content as a String with specified encoding.
- B 摘要: Launches a NexOpen project configuration by processing pom.xml files, setting up Hibernate dialect and reverse engineering files, and scheduling an install action.
- 静态失败原因: Static BERT models (e.g., CodeBERT) rely on token embeddings and structural patterns. These two functions have very low token overlap (Jaccard=0.07) and different API calls (eclipse vs java.io), so the model likely did not capture the shared sub-behavior. The models may also be sensitive to function length and context, and the partial similarity is drowned by the massive differences in overall structure.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs as clones (Type-4, partial functionality) if one function contains a sub-task that is semantically equivalent to another function. Here, function B contains a code snippet that reads a bundle resource and converts it to a string, which is exactly what function A does, so BCB considered them clones.
- 共享行为: Both read a file/resource and convert its content to a String using IOUtils.copy.
- 行为差异: Function A is a simple utility to read any file; Function B is a complex launch method with many Eclipse-specific operations.；Function A returns the string; Function B uses the string to create a new file in the workspace.；Function B also handles XML parsing, properties, project configuration, and has error handling.
- 修正建议: Use methods that detect partial or semantic clones by focusing on sub-graphs or fine-grained embeddings.；Incorporate data-flow analysis to track resource reading patterns.；Improve training data with more partial-clone examples.

### case_id=3831 FN benchmark_preference_bias

- 方法: `DecodeMapFile` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Decodes a map file by XORing each byte with a changing key and writes to output file.
- B 摘要: Modifies a properties file by adding or updating a message name-value pair for a given locale.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token and syntactic overlap, which is low (Jaccard=0.18). They fail to capture the broad, high-level semantic similarity of file manipulation that BCB annotators might have considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as file transformation utilities with similar structure (open-read-process-write), and perhaps the annotation guidelines allowed partial functionality similarity (Type-4) for such high-level file manipulation patterns.
- 共享行为: Both perform file I/O: read from a source file, process content, write to a target file.；Both handle exceptions with try-catch blocks.
- 行为差异: Function A operates on binary bytes with XOR transformation, while Function B operates on text lines with property key-value replacement.；Function A uses a fixed buffer size and XOR key increment, while Function B uses line-by-line reading and string manipulation.；Function A creates output file directly; Function B may copy an English file to create a new locale file if missing.
- 修正建议: Improve model to recognize high-level semantic patterns beyond lexical overlap.；Incorporate structural similarity of file I/O patterns.

### case_id=3832 FN partial_functionality

- 方法: `copyFile` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Modifies a property file by reading, updating a specific key-value pair, and writing back; also copies default file if locale file missing.
- 静态失败原因: Static BERT models rely on token overlap and method name similarity; these methods share few tokens and have different names, leading to low similarity score and non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might have labeled these as clones due to both performing file write operations and having similar exception handling patterns, but the core functionality differs significantly.
- 共享行为: Both involve file I/O operations；Both handle exceptions and close streams；Both can result in writing to a file
- 行为差异: A is a simple binary copy without content interpretation; B parses text, splits lines, and modifies specific key-value pairs.；B has conditional logic to copy a default file if target missing; A always copies.；B interacts with properties files; A copies any file type.
- 修正建议: Use graph-based models capturing data flow and control flow to identify structural similarities beyond lexical overlap.；Incorporate semantic role labeling to distinguish primary vs secondary operations.

### case_id=3833 FN partial_functionality

- 方法: `doTransfer` vs `postData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Proxies an HTTP request by copying headers and forwarding body, then writing the response back.
- B 摘要: Sends a string payload via HTTP POST to a specified endpoint and reads the response (discarded).
- 静态失败原因: The model likely relied on lexical overlap (URL, URLConnection, streams) but failed to capture the distinct high-level intents (proxy vs. client) and the significant differences in data flow, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones under broad Type-4 (semantic similarity) because both perform a common pattern of making an HTTP request with a body and reading a response, despite different contexts and details.
- 共享行为: Both open an HTTP URL connection；Both set DoOutput and DoInput to true；Both write data to the output stream of the connection；Both read from the input stream of the connection
- 行为差异: Function A is a proxy that forwards entire request headers and body; B only sends a fixed string；Function A reads response and writes to the original response output stream; B discards the response；Function A supports any HTTP method via parameter; B is fixed POST；Function A handles error codes by sending error response; B does not handle errors
- 修正建议: Train on more diverse examples of HTTP communication to distinguish proxy vs. client patterns；Incorporate control flow analysis to capture data propagation differences；Use contrastive learning to emphasize functional differences over shared API calls

### case_id=3834 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `PhoneSetImpl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads an HTML page from a URL, extracts all hyperlinks and their text using regex, and returns them as two vectors.
- B 摘要: Reads a text file from a URL, parses each line that doesn't start with '***' using parseAndAdd, and populates a phone set map.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized the overlapping API usage (BufferedReader, InputStreamReader, URL) and ignored the significant difference in the processing logic. The low token Jaccard (0.14) suggests even lexical overlap is small, so the model may have mislearned that any pair with similar IO patterns is a clone.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the core functionality is completely different: one extracts hyperlinks from HTML, the other parses structured phone set data. The only overlap is in URL reading boilerplate, which does not make them clones under BCB's typical semantic criteria.
- 共享行为: Both read input from a URL using BufferedReader/InputStreamReader；Both iterate line by line over the input
- 行为差异: A uses regex to extract links from HTML, B uses a custom parser for a specific format；A returns vectors of links and texts, B builds a map of phone set data；A has timing checks, B counts lines；A processes entire page as a string buffer, B processes lines individually
- 修正建议: Incorporate control flow and dataflow representations to distinguish actual processing logic from I/O boilerplate.；Use structure-aware models like CodeBERT with data flow graphs to capture semantic differences.；Augment training data with more non-clone pairs that share I/O patterns but differ in core logic.

### case_id=3835 FN partial_functionality

- 方法: `main` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL via GET and prints each line of the response.
- B 摘要: Performs an HTTP POST request with parameters, reads the response line by line, and returns it as a string, handling errors.
- 静态失败原因: Static BERT/GraphCodeBERT may focus on surface-level differences (method signature, HTTP client classes) and miss the deeper IO pattern similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as performing HTTP GET-like reading of a URL, with structural similarity in reading lines; BCB often annotates clones where the core IO reading pattern is similar even if the HTTP method differs.
- 共享行为: Both make HTTP requests and read response line by line using BufferedReader；Both use InputStreamReader and BufferedReader to read the response
- 行为差异: A uses URL.openStream (implicit GET), B uses HttpPost (explicit POST)；A prints output, B returns string；A does not handle HTTP status codes or exceptions (throws IOException), B handles errors and returns null；A is a static main, B is an instance method that updates fields
- 修正建议: Improve model to recognize that both functions involve reading an HTTP response line by line, even if the HTTP method and output handling differ

### case_id=3836 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a zone file from classpath, parses each line as an integer, and returns a HashSet of zone IDs.
- B 摘要: Reads a resource file from classpath, concatenates all lines with newline separators, and sets the resulting text into a GUI text component.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on the lexical overlap (URL, InputStreamReader, readLine, try-catch) and ignored the differing data transformations and final outcomes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone (0) because the functions have completely different purposes and outputs; one is a utility to parse a set of integers, the other is a GUI update routine. They are not considered functionally similar in BigCloneBench's annotation guidelines.
- 共享行为: Both obtain a URL to a resource using classpath-based resource loading；Both open an InputStream from the URL and wrap it with InputStreamReader；Both read lines from the reader in a loop
- 行为差异: A returns a HashSet<Integer>; B sets text in a GUI component；A parses each line as integer; B appends lines with newline characters；A does not close resources; B explicitly closes streams and readers；A handles exceptions by printing stack trace; B catches and ignores exceptions
- 修正建议: Use dataflow analysis to capture how input tokens are transformed into outputs；Incorporate comparison of return types or side effects；Train on a dataset that penalizes false positives from boilerplate overlapping patterns

### case_id=3837 FN lexical_or_api_overlap

- 方法: `encodeFileToFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Encodes a file to Base64 and writes to another file, returning success status.
- B 摘要: Retrieves a resource by URL, caches it locally, and returns an InputStream to the cached file.
- 静态失败原因: Static BERT models may rely on lexical and structural patterns; the high overlap in stream handling code could cause confusion, but functional differences require deeper semantic understanding.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might consider them clones due to shared boilerplate of reading from an input and writing to an output using streams, ignoring the distinct operations.
- 共享行为: Both use buffered streams for I/O；Both have try-catch-finally blocks with stream closing
- 行为差异: Different core purposes: encoding vs caching；Different return types: boolean vs InputStream；B has HTTP connection and caching logic, A does not；B is synchronized, A is not
- 修正建议: Incorporate functional classification or program analysis to distinguish encoding from caching；Use dataflow analysis to capture transformation semantics

### case_id=3838 FN partial_functionality

- 方法: `main` vs `copyParseFileToCodeFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a zip file from a URL and extracts its entries to files.
- B 摘要: Copies the content of one file to another file using a buffer.
- 静态失败原因: Static models like GraphCodeBERT rely on token sequences and structure; they likely focused on the high-level differences (URL vs file, zip vs plain) and missed the underlying I/O loop pattern, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions implement a common buffered I/O copy loop, which is considered a Type-4 clone (similar functionality) despite different contexts.
- 共享行为: Both read data from an input stream and write it to an output stream using a byte buffer.；Both use a while loop to transfer data in chunks.
- 行为差异: A reads from a URL and processes zip entries; B reads from a local file.；A writes to multiple files (one per zip entry); B writes to a single file.；A creates multiple output streams; B creates one output stream.；A involves network I/O and zip decompression; B only local file I/O.
- 修正建议: Improve model sensitivity to common low-level I/O patterns even when high-level functionality differs.；Include more examples of buffered copy loops in various contexts during training.；Incorporate data flow analysis to recognize that both use InputStream/OutputStream in a while loop.

### case_id=3839 FP boilerplate_overlap

- 方法: `load` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads content from a Pastebin URL specified by an ID and returns it as a concatenated string, with error handling via dialog.
- B 摘要: Downloads content from a given URL with optional HTTP Basic Authentication, writes it to a temporary file, and updates a status label with download progress.
- 静态失败原因: The static model likely focused on the structural similarity of the BufferedReader read loop and URLConnection usage, while overlooking the larger semantic context: different method signatures, return types, error handling, and side effects (file writing, GUI updates). The model may have been misled by common boilerplate I/O patterns, treating them as indicative of clone behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels them as non-clones because they represent different functionalities: one is a simple download-to-string utility, the other is a file-download with authentication and progress reporting. Despite sharing a common read loop, the overall program purpose, input/output signatures, and side effects diverge significantly, placing them outside typical Type-3 clone boundaries.
- 共享行为: Both read from a URL connection line by line using BufferedReader.
- 行为差异: A returns the downloaded content as a string; B writes it to a temporary file.；A does not handle authentication; B supports Basic Authentication.；A shows an error dialog on IOException; B throws the exception.；A checks the ID length and returns empty string if less than 5; B has no such check.
- 修正建议: Incorporate full method signature analysis (parameters, return type).；Enhance dataflow tracking to distinguish how read data is used (returned vs written to file).；Include side-effect analysis (file creation, GUI updates) as features.；Use functional summaries that capture the overall purpose rather than local patterns.

### case_id=3840 FN partial_functionality

- 方法: `logging` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs inbound message details after processing encoding, headers, and content.
- B 摘要: Launches a configuration by setting up Maven project, handling XML profiles, properties, and reverse engineering files.
- 静态失败原因: Static models relied on lexical overlap of common Java idioms (e.g., IOUtils.copy, try-catch) and failed to capture the distinct high-level semantics.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled as clone due to shared API usage (IOUtils, InputStream, logger) and exception handling patterns, despite fundamentally different purposes.
- 共享行为: Both use I/O streams and copy operations；Both perform logging and error handling
- 行为差异: Function A is purely logging, while B is a complex project setup；B involves multiple file operations, configuration attributes, and property setting not present in A
- 修正建议: Incorporate high-level intent via task categorization；Use flow-sensitive analysis to differentiate control flow structures

### case_id=3841 FN partial_functionality

- 方法: `main` vs `hyperlinkUpdate`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a hard-coded URL, extracts its zip entries, and saves them to disk.
- B 摘要: Handles a hyperlink activation event by fetching the URL content and displaying it in a dialog.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token similarity and syntactic structure. The code has very low token Jaccard (0.11) and different method signatures, variable names, and control flows. The model likely failed to recognize the semantic connection of URL stream opening because it is overshadowed by many different tokens and operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a clone because both functions involve opening a URL, getting an InputStream, and processing the stream, albeit in different ways. The broad functional category of 'URL input stream processing' could be considered similar at a high level.
- 共享行为: Both open a URL and obtain an InputStream from it
- 行为差异: A extracts zip entries to files; B displays text content in a GUI dialog；A uses ZipInputStream and FileOutputStream; B uses IOUtils.copy and JEditorPane；A is a main method; B is an event handler method；A writes to files; B writes to a string and displays
- 修正建议: Improve model awareness of dataflow and API usage patterns, e.g., by focusing on common API calls like url.openStream() and stream close patterns.；Use graph-based representations that capture the sequence of operations on the same data object (e.g., URL -> openStream -> read/write).；Incorporate more diverse training examples that match based on high-level intent rather than exact syntax.

### case_id=3842 FN partial_functionality

- 方法: `doGet` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to retrieve a page, check permissions, generate HTML response, and optionally cache output to file.
- B 摘要: Recursively copies a file or directory to a new location using file streams.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on low token Jaccard and structural differences, and missed the partial functional overlap in the caching section, leading to a false negative prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered the caching part of doGet as a file copy operation, suggesting partial functionality overlap; however, the overall functions are too dissimilar to be clones.
- 共享行为: Both involve reading from a source and writing to a destination.；Both include error handling and logging for I/O exceptions.
- 行为差异: doGet involves complex page retrieval logic, user authorization, HTML generation, and optional caching; copy is purely file/directory duplication.；doGet interacts with HTTP request/response objects; copy uses file system APIs.；doGet handles multiple control flows for missing pages, permissions, and caching; copy has straightforward recursive logic.
- 修正建议: Improve modeling of partial functionality overlap by using segmented analysis or hierarchical representations.；Incorporate more abstract behavioral patterns like read-write operations across different domains.

### case_id=3843 FN benchmark_preference_bias

- 方法: `writeConfiguration` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Writes the content of a configuration resource (from myResource URL) to a Writer, with error handling if resource is null or stream is null.
- B 摘要: Modifies a specific key-value pair in a locale-specific properties file, creating the file if necessary by copying from an English template, and writes the updated content back.
- 静态失败原因: The static model correctly identified no semantic equivalence due to low lexical overlap and different control flows and data operations; BCB's clone label seems to be an over-generalization.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them clones due to a broad interpretation of 'configuration writing' functionality, as both functions write configuration-related data to an output, despite different specifics.
- 共享行为: Both perform I/O operations: reading from an input source and writing to an output.
- 行为差异: A writes the entire content of a resource; B modifies and writes a single property entry.；A writes to a generic Writer parameter; B writes to a specific file.；A handles a single resource URL; B handles multiple files and locale-specific paths.；B involves string manipulation of properties lines; A simply copies raw bytes.
- 修正建议: Adjust BCB annotation criteria to be more precise and avoid over-grouping dissimilar functions.；Incorporate deeper semantic analysis, such as data flow and API usage, to distinguish between generic I/O and specific property modification.

### case_id=3844 FP boilerplate_overlap

- 方法: `readData` vs `forBundle`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated string constants into sets and a validation map, with trivial error handling.
- B 摘要: Processes an OSGi bundle by zipping its files, writing a manifest, and installing/uninstalling plugins, with IOException handling.
- 静态失败原因: The model likely overfit to common API patterns (e.g., while loops with hasMoreTokens/hasMoreElements) and boilerplate structure (private, void, try-catch), ignoring the vast semantic gap in functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the functions implement completely different algorithms and serve distinct purposes; they share only superficial structural patterns.
- 共享行为: Both use loops to iterate over collections (StringTokenizer / Enumeration).；Both have error handling (thrown exceptions / try-catch).；Both are private methods performing initialization/configuration tasks.
- 行为差异: A populates static data structures from predefined strings; B manipulates OSGi bundles and plugin lifecycle.；A has no I/O operations beyond string tokenization; B involves file I/O, zip compression, and plugin installation.；A's error handling is rudimentary (throws Error); B uses try-catch with finally block and logging.；The domain and purpose are entirely different (character set initialization vs. bundle templating).
- 修正建议: Enhance training with more diverse examples to reduce sensitivity to boilerplate.；Incorporate dataflow or control-flow abstractions to distinguish different computation purposes.；Add negative mining for pairs with high structural but low semantic similarity.

### case_id=3845 FN lexical_or_api_overlap

- 方法: `modifyApplicationMessage` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale by updating or adding a key-value pair.
- B 摘要: Converts an ACRNEMA medical image file to DICOM format by adding UIDs and handling pixel data.
- 静态失败原因: The static model relied on token overlap (Jaccard 0.13) and common I/O tokens (File, InputStream, OutputStream, etc.), failing to capture the distinct domain-specific semantics. It could not differentiate between simple property file modification and complex medical image conversion.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled them as clones due to superficial similarity in structure: both use InputStream, File, FileWriter/OutputStream, and loops. The annotator may have considered both as 'file transformation' tasks, overlooking the domain-specific logic differences.
- 共享行为: Read a file, process its contents, and write to another file；Use I/O streams and exception handling；Contain loops
- 行为差异: Different input/output formats (properties vs medical image)；Different processing logic (string replacement vs pixel data handling)；Different purpose (i18n message modification vs medical format conversion)；Different error handling and conditions
- 修正建议: Incorporate dataflow analysis to distinguish different file operations；Add domain-specific training examples or fine-tuning on task-specific data；Use contrastive learning to separate unrelated file processing tasks

### case_id=3846 FN partial_functionality

- 方法: `getWebPage` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens a URL stream and reads all lines into a string, throwing an Error on IOException.
- B 摘要: Performs an HTTP POST request with parameters, reads the response line by line into a string, and returns null with error codes on failure.
- 静态失败原因: Static BERT models rely on token overlap (0.14 here) and surface syntax, missing the structural similarity in reading HTTP response. Differences in method names, API calls, and error handling dominate, leading to a non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels as clones functions that perform the same high-level task (web page retrieval) even if the HTTP method or detailed error handling differs, considering them Type-4 clones with shared core functionality.
- 共享行为: Read HTTP response line by line using BufferedReader and InputStreamReader；Concatenate lines into a single string；Handle IOException
- 行为差异: HTTP method: GET (A) vs POST (B)；Error handling: throws Error (A) vs returns null with error codes (B)；Input parameters: URL object (A) vs URL string, timeout, and parameter list (B)；API usage: URL.openStream (A) vs Apache HttpClient (B)
- 修正建议: Use graph-based or data-flow representations to capture the shared pattern of reading and concatenating lines；Incorporate API call abstraction (e.g., HTTP GET/POST as 'web request')；Train with more diverse Type-4 clone examples to recognize partial functionality

### case_id=3847 FN lexical_or_api_overlap

- 方法: `sendExceptionToServer` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.75`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a remote server via HTTP POST.
- B 摘要: Checks for the latest version by reading a version file via HTTP GET.
- 静态失败原因: Static BERT/GraphCodeBERT relied on lexical and API overlap (URL, BufferedReader, IOException) but missed the opposite data flow direction and different task semantics (send vs check). The model may have considered them similar due to boilerplate network IO code.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label them as clones due to similar structure: try-catch, URL, stream reading, and both perform network IO tasks. The high-level similarity in using HTTP connections and reading lines might be considered Type-3 or partial functionality.
- 共享行为: Both make HTTP connections and handle IOException；Both use BufferedReader to read server response line by line；Both involve URL creation and stream opening
- 行为差异: A sends data (POST) while B receives data (GET)；A encodes form parameters, B parses line prefixes；A has extensive error reporting, B shows wait cursor；Different exception handling: A prints, B shows error dialog
- 修正建议: Incorporate data flow analysis to distinguish input vs output operations；Add control flow features to capture branching differences；Use task-oriented embeddings that differentiate send vs receive patterns

### case_id=3848 FN benchmark_preference_bias

- 方法: `readData` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads and parses hardcoded string constants into sets and maps containing character and linguistic data.
- B 摘要: Performs an HTTP GET request with basic authentication and reads the response into a string.
- 静态失败原因: Static BERT models may have failed due to low token overlap and distinct API usage (StringTokenizer vs HttpURLConnection). The model might have relied on weak signals like the presence of 'read' in function names or common loops, but the overall semantics are dissimilar.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones because both involve 'reading data' (one from strings, one from HTTP) and both use loops to process tokens/lines. However, this is too broad and likely a misannotation or a very loose Type-4 clone that BCB sometimes accepts.
- 行为差异: Function A reads from local string constants and parses tokens into collections; Function B makes an HTTP request and reads the stream.；Function A does not involve network I/O; Function B does.；Function A populates multiple sets and maps; Function B stores the response in a single string.；Function A has no error handling for network failures; Function B catches exceptions and stores the error.
- 修正建议: Improve training data to include more negative samples with similar surface patterns but different semantics.；Use graph-based representations to capture data flow and call structure differences.；Incorporate semantic role labeling or domain-specific knowledge to distinguish I/O patterns.

### case_id=3849 FP lexical_or_api_overlap

- 方法: `loadMFileViaWeb` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a MATLAB file from a URL, reads it line by line, parses it into a UserFunction object, and returns it.
- B 摘要: Downloads a file from a URL to a local file with progress tracking using a buffer and streams, returns a boolean success flag.
- 静态失败原因: The model likely overemphasized the overlapping API tokens such as 'URL', 'InputStream', 'BufferedReader', and 'BufferedInputStream', and ignored the distinct overall purpose and output behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because their core functionality is entirely different: one is a specialized function parser, the other is a generic file download utility. The fact that both involve network I/O is superficial and does not make them clones.
- 共享行为: Both open a URL and create an input stream to read data from the network；Both use try/catch or throws for exception handling
- 行为差异: A parses and returns a UserFunction; B writes to a local file and returns boolean；A reads text line-by-line; B reads binary in fixed-size buffer；A uses debug logging; B updates a progress bar via MessageFrame；A handles exceptions internally; B throws Exception to caller
- 修正建议: Train the model to distinguish between functions that share only low-level API calls but have different high-level semantics；Incorporate more contrastive examples where I/O patterns are similar but tasks differ；Use code structure embeddings that capture function-level goals rather than just token sequences

### case_id=3850 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `sendPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft client authentication by parsing handshake username, validating it, and either sending login packet or performing a GET request to session server.
- B 摘要: Sends an HTTP POST request to a given URL with parameters and returns the response body as a string.
- 静态失败原因: Static BERT models rely on token and API overlap; both functions use similar I/O classes (URL, BufferedReader, Exception handling) leading to high similarity despite different semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions serve completely different purposes: one is domain-specific Minecraft handshake, the other is a generic HTTP client. They share only low-level API usage, not high-level functionality.
- 共享行为: Perform network I/O using URL and read response via BufferedReader
- 行为差异: A validates username and may send a login packet; B sends arbitrary POST parameters；A uses GET request while B uses POST；A modifies game state (addToSendQueue) and handles shutdown; B is a utility returning a string；A catches Exception and prints stack trace; B catches Exception and shows message via MsgPrint
- 修正建议: Incorporate data flow and control flow analysis to distinguish network utility code from domain-specific logic.；Use program structure features like method dependencies and state modifications to capture semantic intent.

### case_id=3851 FN benchmark_preference_bias

- 方法: `copyResource` vs `simulate`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file.
- B 摘要: Simulates a process by reading a file, making web service calls (rateUser, obtainUserReputation), and logging results.
- 静态失败原因: The static model correctly identified non-clone based on low token similarity (0.11) and distinct method names; BCB label appears erroneous, so no failure occurred.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled as clone due to superficial overlap in being private, throwing Exception, and having file I/O. However, the core functionality is entirely different, so under standard BCB guidelines it should not be a clone.
- 共享行为: Both are private void methods that throw Exception；Both perform file I/O (reading and writing)；Both close resources after use
- 行为差异: copyResource simply copies bytes; simulate invokes multiple web services with complex logic；copyResource has no branching or assertions; simulate has conditional error handling and test assertions；copyResource uses low-level streams; simulate uses high-level readers/writers and custom objects
- 修正建议: Re-annotate this pair in BigCloneBench; likely should be non-clone；Use multi-annotator consensus to reduce annotation noise

### case_id=3852 FN partial_functionality

- 方法: `testNetworkHTTP` vs `getWebByUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A hardcoded test method that makes multiple HTTP GET requests to specific URLs and reads but discards the response.
- B 摘要: A parameterized method that fetches web content from a given URL, saves it to a file, and recursively extracts links.
- 静态失败原因: Static models like GraphCodeBERT rely on token similarity and structural patterns; the low Jaccard similarity (0.158) and different method signatures, control flow (multiple sequential requests vs. single with recursion), and additional file I/O in B mislead the model to predict non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels these as clones because both perform the core functionality of fetching content over HTTP, which is a broad clone class in BigCloneBench where methods that implement HTTP GET requests are often considered Type-4 clones even with differing details.
- 共享行为: Both open an HTTP URL connection and read the response line by line.；Both handle IO exceptions with try-catch.；Both use BufferedReader to read from an InputStream.
- 行为差异: A hardcodes URLs and makes multiple sequential requests; B takes a URL as parameter and makes a single request.；A reads and discards the response; B writes the response to a file and may recursively extract URLs.；A uses HttpURLConnection with explicit disconnect; B uses URLConnection and does not disconnect.；B has additional logging and tracking of successes/failures.
- 修正建议: Incorporate dataflow analysis to capture the common HTTP request pattern.；Use semantic role labeling to identify the shared operation of fetching a URL.；Train on more diverse Type-4 examples with low lexical overlap.

### case_id=3853 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `testCopy_readerToWriter_nullIn`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a localized properties file by reading an English template, copying it if needed, then replacing or appending a specific message key-value pair.
- B 摘要: Tests that IOUtils.copy throws NullPointerException when the Reader argument is null, using a ByteArrayOutputStream and a custom OutputStream wrapper.
- 静态失败原因: Static BERT/GraphCodeBERT likely correctly predicted non-clone (0) because the semantic difference is large. The token Jaccard is low (0.103), and the structural patterns (file modification vs. unit test) are distinct. The model succeeded here.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both containing a while loop that copies data from a reader to a writer (in A: while ((c = in.read()) != -1) out.write(c); in B: IOUtils.copy internally does similar copying). However, the context and purpose are entirely different, and the token overlap is low.
- 共享行为: Both involve file or stream I/O operations
- 行为差异: Function A performs file modification with localization logic; Function B is a unit test for a library method with null input.；Function A creates, reads, and writes multiple files; Function B only writes to a byte array and expects an exception.；Function A handles property key-value replacement and appending; Function B has no data processing beyond exception testing.；Function A uses traditional FileReader/FileWriter and BufferedReader; Function B uses IOUtils.copy and OutputStreamWriter.
- 修正建议: Re-evaluate BCB label for this pair; likely a misannotation.；Ensure annotation guidelines distinguish between shared low-level I/O patterns and high-level functionality.；Use larger context or comment analysis to differentiate test code from production code.

### case_id=3854 FN partial_functionality

- 方法: `CheckUrl` vs `handledRun`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads the first line from a given URL and returns it as a string, with exception handling.
- B 摘要: Downloads and saves updated game data from a fixed URL if the local version is outdated, involving multiple reads, file writing, and database updates.
- 静态失败原因: The lexical overlap (Jaccard = 0.1237) is very low, and the overall code structures differ significantly. GraphCodeBERT likely relies on token similarity and local context; the long intervening code in B distracts from the initial similar pattern. The model may fail to recognize the partial clone due to the extensive additional logic in B.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone due to the shared core pattern of opening an HTTP URL and reading data line by line, which could be considered a Type-4 semantic similarity. The annotators might have focused on the common network-reading functionality despite differences in purpose and scope.
- 共享行为: Both open a URL connection and create a BufferedReader to read from the input stream.；Both use readLine() to read at least one line from the stream.；Both wrap the network operations in try-catch blocks for exception handling.
- 行为差异: A returns a single line; B does not return but writes to a file and updates a database.；A reads exactly one line; B reads two header lines and possibly the entire file content.；A has no side effects; B modifies the file system and game database.；B has conditional logic (version check) and additional exception handling for UnknownHost and general exceptions.
- 修正建议: Use a model that can detect partial clones or subgraph matching (e.g., data-flow-based models).；Incorporate hierarchical or block-level embeddings to isolate common subsequences.；Train on a dataset with more Type-3/Type-4 examples to learn functional similarity despite low token overlap.

### case_id=3855 FN dataflow_blindspot

- 方法: `getFile` vs `test`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `dynamic_equivalence_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a WSDL file from a URL to a temporary file, modifies the endpoint location, and returns the file path.
- B 摘要: Tests the StorageStringWriter class by writing and reading text to verify its functionality.
- 静态失败原因: Static BERT models rely on lexical token overlap and shallow syntactic patterns. The two functions have very low token Jaccard similarity (0.066) and different method names and vocabulary, so the model failed to recognize the shared abstract stream-copying behavior.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本可能是 API 写法不同但行为等价的漏报。建议测试目标为 input_output_equivalence。
- BCB 偏好解释: BCB may consider these as Type-4 clones because both implement the high-level concept of 'copying data from an input stream to an output stream with exception handling', despite differences in specific I/O sources and sinks.
- 共享行为: Both involve copying data from an input source to an output destination using stream operations.；Both handle IOException and other exceptions in a similar catch structure.；Both use try-catch blocks to manage stream resources.
- 行为差异: Function A downloads from a network URL to a file, while B uses in-memory storage.；Function A manipulates XML content, B does not.；Function A logs debug/error messages, B uses assertions and fail() calls.；Function A is a utility method, B is a unit test.
- 修正建议: Incorporate dataflow analysis or program slicing to capture common I/O patterns.；Use intermediate representations like control-flow graphs with data dependencies to identify stream operations.；Train on semantic similarity tasks that emphasize functional behavior over lexical overlap.

### case_id=3856 FP long_range_semantics

- 方法: `getHash` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Computes MD5 hash of input string and returns hex representation.
- B 摘要: Processes HTTP request to classify a concept, communicates with external service, and returns ActionForward.
- 静态失败原因: Static models may have been confused by low-level API overlap (e.g., StringBuffer, URLConnection) or general boilerplate (try-catch, loops). However, given very low token Jaccard similarity, it is surprising the static model predicted clone. Possibly the model has a limitation in long-range semantics and missed the context; or the model may have learned false correlations from training data. The error category is 'long_range_semantics' because the methods differ greatly in length and purpose.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have no overlapping functionality; one is a simple utility, the other is a complex web action.
- 行为差异: Function A computes a hash; Function B handles web request and external service interaction.；Function A returns a string; Function B returns ActionForward.；Function A is private; Function B is public and has complex control flow with session management and HTTP communication.
- 修正建议: Improve model's ability to capture high-level program intent, e.g., by incorporating method names and overall structure.；Use data flow analysis to distinguish local computation from external interactions.；Ensure training data includes diverse examples to reduce false positives from boilerplate overlap.

### case_id=3857 FN benchmark_preference_bias

- 方法: `getResourceAsStream` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Loads a resource as an InputStream, with caching to a local file and HTTP conditional GET.
- B 摘要: Reads a log file, filters lines every N lines that start with a token, and writes to a new file.
- 静态失败原因: Static models like CodeBERT may focus on token-level similarities (e.g., both use 'InputStream', 'Buffered', 'File', 'try-catch') and overlook the fundamental semantic difference in the overall task. The model might have been misled by the high overlap of common API calls and boilerplate error handling.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have considered both as involving file I/O and I/O streams, possibly categorizing them as Type-4 semantic clones due to similar structure (reading, processing, writing) despite different domains. However, this is a stretch and likely an annotation error.
- 共享行为: Both read from some input source (network or file) and write to a local file.；Both use buffered I/O streams.；Both have exception handling with printStackTrace.
- 行为差异: Function A fetches resource over HTTP with caching logic; Function B simply filters local log file.；Function A returns an InputStream; Function B writes to file and returns void.；Function A has complex cache validation and HTTP response handling; Function B has none.；Input source: A uses URL from getResource(); B uses command-line arguments for filename.
- 修正建议: Improve training data with clearer non-clone pairs that have similar boilerplate but different semantics.；Use dataflow or control-flow features to distinguish actual data processing differences.；Incorporate domain-specific knowledge about resource loading vs log filtering.

### case_id=3858 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs a version check by fetching version/build from a URL, compares with jEdit's build, and shows UI messages.
- B 摘要: Retrieves a version string from a URL and returns it, with no UI interaction.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-predicted due to high lexical overlap (URL, BufferedReader, readLine, version keywords) and similar control flow structure, missing the semantic differences in usage and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because the overall functionality and side effects differ significantly; they share only a common sub-task of reading a URL, but the purpose and integration differ.
- 共享行为: Both fetch a version string from a remote URL using URL and BufferedReader
- 行为差异: Function A has UI side effects (cursor wait, messages) while B has none；Function A extracts both version and build lines, B takes the whole line as version；Function A compares with jEdit's build and triggers UI actions, B simply returns the string；Function A is void, B returns a String
- 修正建议: Incorporate method signature and return type analysis；Use dataflow analysis to distinguish side effects (e.g., UI calls)；Train on more diverse examples of partial functionality clones

### case_id=3859 FN partial_functionality

- 方法: `copyFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to target using NIO FileChannel transferTo.
- B 摘要: Retrieves a resource as an InputStream, with caching, HTTP support, and file writing for local cache.
- 静态失败原因: The static BERT/GraphCodeBERT model relies heavily on lexical similarity and token overlap; the Jaccard similarity is very low (0.09). It also struggles with long-range semantic dependencies, such as recognizing that the inner while loop in getResourceAsStream performs a file copy similar to copyFile. The model likely focused on the surrounding complex logic and missed the shared file-copy sub-behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both functions as performing a 'file copy' operation in a broad sense. While copyFile directly copies files, getResourceAsStream includes a critical file copy segment when caching a resource locally. BCB's annotation preference may value partial functional overlap (Type-4) where a common sub-behavior exists, even if the overall purposes differ.
- 共享行为: Both perform file I/O operations involving reading from a source and writing to a destination.；Both close streams/channels after use.；Both handle IOException through explicit closing in finally blocks.
- 行为差异: copyFile is a simple file-to-file copy; getResourceAsStream is a resource retrieval with caching, network handling, and conditional logic.；copyFile returns void; getResourceAsStream returns an InputStream.；copyFile uses FileChannel.transferTo; getResourceAsStream uses BufferedInputStream/OutputStream with byte-by-byte loop.；getResourceAsStream has extensive exception handling and multiple return paths; copyFile throws IOException.
- 修正建议: Incorporate dataflow analysis to detect file copy operations (e.g., reading from a source and writing to a destination).；Use function-call-based representations to highlight core I/O patterns.；Train with examples that have low lexical overlap but share a sub-computation.；Include type-4 clone pairs with explicit partial functionality annotation.

### case_id=3860 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `readVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads JSON from a Twitter API endpoint using HTTP client and returns the entire response as a string.
- B 摘要: Reads a version file from the classpath, parses version, revision, and date lines, and sets class fields accordingly; returns void.
- 静态失败原因: Static models like GraphCodeBERT can be misled by overlapping low-level API usage (BufferedReader, InputStream, catch blocks) and similar control-flow structure (while loop reading lines), causing a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically marks non-clones when the functionalities are clearly different (network fetch vs. local config parsing), even if they share some boilerplate I/O patterns.
- 共享行为: Both use BufferedReader and InputStreamReader to read text line by line；Both handle IOException with e.printStackTrace()
- 行为差异: A performs network I/O via HTTP; B reads a local classpath resource；A returns a concatenated string; B modifies internal fields and returns void；A parses specific Twitter API endpoint; B parses a config file format；A uses HttpClient and HttpGet; B uses ClassLoader.getSystemResource and url.openStream
- 修正建议: Increase sensitivity to API-level semantics (e.g., distinguish HTTP client from classpath resource loading)；Incorporate more context about method signatures and return types；Use contrastive training with harder negative pairs that share boilerplate but differ in purpose

### case_id=3861 FN benchmark_preference_bias

- 方法: `doGet` vs `downloadFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to display a page, with parameter parsing, authentication, caching, and response generation.
- B 摘要: Downloads a file from S3, decrypts and decompresses it, and saves it to a local file.
- 静态失败原因: The static model did not fail; it correctly predicted non-clone (0). The benchmark label (1) is likely incorrect, making this a false negative in evaluation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to both functions involving file I/O (writing to file in A, reading and writing file in B) or perhaps because both parse/process data, but the similarity is superficial and the tasks are fundamentally different.
- 行为差异: Function A is a servlet doGet method for web page serving; function B is a private method for file download from cloud storage.；Function A involves HTTP request/response handling, user authentication, and page caching; function B involves S3 download, decryption, decompression, and local file management.；Function A has extensive logging and error handling for page not found, forbidden, etc.; function B throws IOException and handles file deletion on failure.
- 修正建议: Re-evaluate BCB label for this pair; consider correcting it to non-clone.；Improve benchmark curation to avoid such mismatched pairs.

### case_id=3862 FN benchmark_preference_bias

- 方法: `onlyFileCopy` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using FileChannel transferTo.
- B 摘要: Builds a website for editing by processing XML pages, transforming them with XSLT, and writing output files.
- 静态失败原因: Static BERT models had low token overlap (0.084) and could not capture any high-level similarity due to massive size and API differences. However, the static prediction (non-clone) actually aligns with strict judgment, so the model did not fail; rather, BCB's annotation may be biased.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as file I/O operations that move data from source to destination, potentially classifying them as Type-4 semantic clones (similar purpose, different implementation). However, the functionality divergence is large and the annotation is questionable.
- 共享行为: Both read from input files and write to output files.；Both handle IOException.；Both use FileInputStream.
- 行为差异: Function A is a simple file copy; B performs complex XML transformations and multiple file operations.；B has much larger size and many more steps.；B uses XSLT, StringWriter, and many helper classes.；A uses FileChannel transferTo for efficient copy.
- 修正建议: Improve tokenization to capture high-level semantics.；Use graph-based representations to model data flow.；Incorporate purpose-based classification.

### case_id=3863 FN partial_functionality

- 方法: `readGeoParserResult` vs `GetResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads geo parser result by constructing XML request, sending HTTP GET, parsing XML response to extract place names and optional gazetteer IDs, with retries.
- B 摘要: Performs HTTP GET request to given URL and returns the response body as a string.
- 静态失败原因: Low lexical overlap and large amount of unique code in A (XML manipulation, retries) misled the model, which failed to recognize the core I/O pattern similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely focused on the common pattern of HTTP GET and reading response, considering the additional functionality in A as separate but not negating the clone relation.
- 共享行为: Both open an HTTP connection using GET and read the response line by line building a string.
- 行为差异: A constructs and sends a specific XML request, parses the XML response to extract structured data, and includes retry logic; B simply returns the raw response string without any parsing or retries.
- 修正建议: Use dataflow or control flow analysis to capture the common HTTP GET and readline pattern.；Augment training with examples of functionally similar but lexically dissimilar pairs.

### case_id=3864 FP dataflow_blindspot

- 方法: `getContent` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_with_trace`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches HTTP response body as a string from an HttpUriRequest using HttpClient.
- B 摘要: Fetches content from a URL with optional basic auth, writes to a temporary file, and updates a UI label.
- 静态失败原因: Static models may overemphasize the similar BufferedReader readLine loop and miss the different return types and side effects, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 dataflow_trace_and_outputs。
- BCB 偏好解释: BCB typically requires high functional equivalence for Type-3/4 clones. These functions have different signatures, return types, and side effects (file I/O, UI), so they are not considered clones despite shared HTTP reading pattern.
- 共享行为: Both read from an HTTP source line by line using BufferedReader and InputStreamReader.
- 行为差异: A returns a String; B writes to a file and updates a UI label (void return).；A uses HttpClient with timeout settings; B uses URLConnection with auth.；B creates a temporary file and prints to stdout; A does not.；B updates a status label during reading; A does not.
- 修正建议: Incorporate data flow analysis to distinguish return values and side effects.；Add type information (return type, method signature) as features.；Use graph-based models that capture control and data dependencies.

### case_id=3865 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `PhoneSetImpl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft handshake by validating username and possibly authenticating via HTTP request.
- B 摘要: Constructor that loads phone set entries from a URL by reading and parsing lines.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-relied on lexical overlap of common API sequences (e.g., BufferedReader, url.openStream, reader.readLine) without considering the completely different overall logic and domain.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have no meaningful functional similarity beyond trivial I/O boilerplate.
- 共享行为: Both read from a URL using BufferedReader
- 行为差异: Different domains: Minecraft authentication vs phone set loading；Different control flow: conditional branching vs loop until null；Different outputs: network packets vs phone set map
- 修正建议: Incorporate control flow or data flow analysis to distinguish different program logic；Use structure-aware models that capture high-level functionality；Add training with more diverse clone types to avoid overfitting on API sequences

### case_id=3866 FN partial_functionality

- 方法: `testNetworkHTTP` vs `issueCommandToServer`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Test method that makes multiple HTTP GET requests to send device information and discard responses.
- B 摘要: Utility method that sends a command and data via HTTP POST and returns the server response.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on surface-level token and structural similarity. The low token Jaccard, different method signatures, and distinct API usage patterns (HttpURLConnection vs URLConnection, GET vs POST) obscure the underlying semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both implement the core pattern of making an HTTP request, sending data, and reading the response, which can be considered a Type-4 semantic clone despite differences in request type, payload format, and method signature.
- 共享行为: Both functions open an HTTP connection to a server and read the response line by line.
- 行为差异: A uses multiple GET requests with data in URL parameters and does not return; B uses one POST request with data in the body and returns the response.；A sends specific device info (IMEI, phone, etc.); B sends command and capsule object.；A is a void test method; B is a protected method returning String.
- 修正建议: Improve model ability to abstract common communication patterns across different HTTP methods.；Incorporate dataflow analysis to track that both functions ultimately read from an HTTP connection.；Use program slicing to focus on the input-output behavior of network operations.

### case_id=3867 FN benchmark_preference_bias

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file from one location to another using FileChannel, creating parent directories and handling exceptions.
- B 摘要: Builds a website page for editing by reading XML, applying XSLT transformations, and writing output files with extensive string processing.
- 静态失败原因: The static model correctly identified non-cloneness from low lexical overlap (Jaccard 0.07) and structural differences; the BCB label itself may be a misannotation, so the model did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely annotated this as a clone due to broad file I/O similarity, but the functions are too different in purpose and complexity to be considered clones under typical BCB guidelines.
- 共享行为: Both perform file I/O operations；Both include resource management and exception handling
- 行为差异: Function A is a simple file copy; Function B is a complex multi-step website generation；Function A uses FileChannel; Function B uses FileInputStream, FileReader, and transformers；Function A has minimal parameters; Function B has many configuration parameters；Function A produces no output beyond the copied file; Function B writes multiple output files with content modifications
- 修正建议: Re-annotate this pair in BCB to reflect actual semantic dissimilarity；If following BCB labels, consider adding a rule to avoid matching overly simple utilities with complex business logic

### case_id=3868 FN partial_functionality

- 方法: `doGet` vs `writeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET request, retrieves a page, checks permissions, renders the page, and caches the output to a file.
- B 摘要: Copies content from one file to another using FileChannel.
- 静态失败原因: The functions have very low token overlap (0.06), different method names, and different structures. BERT focused on surface form and failed to capture the file writing similarity that BCB considered. Also, the file writing in A is a small part of the overall function, which BERT may not weigh enough.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this clone because both functions perform file writing operations, albeit in different contexts. The partial similarity in writing to files might be considered a clone under broad Type-4 (functional similarity) classification.
- 共享行为: Both involve writing data to a file (A writes HTML to a temp file; B writes file contents to another file).；Both handle IO exceptions.
- 行为差异: A is a web request handler with authentication, rendering, logging; B is a simple file copy utility.；A uses FileWriter, B uses FileChannel.；A's file writing is conditional and part of caching; B's file writing is the main purpose.；A has complex control flow; B is linear.
- 修正建议: Use dataflow analysis to detect shared I/O patterns.；Consider subgraph matching for partial functionality.；Incorporate task-specific heuristics for I/O operations.

### case_id=3869 FP boilerplate_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter classes from a Prolog file by parsing, visiting, and writing JAR resources.
- B 摘要: Copies a file from source to destination using FileInputStream, FileOutputStream, and FileChannel.
- 静态失败原因: The static model may have been misled by surface-level similarities like common keywords (File, IOException, try-finally) or structural patterns (nested try-final blocks), despite very low token Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have completely different purposes and no overlapping core functionality.
- 共享行为: Both involve file I/O operations.；Both use try-finally blocks for resource cleanup.
- 行为差异: Function A is a complex main method for code generation, while B is a simple file copy utility.；Function A reads a Prolog file and generates multiple class files, whereas B only copies a single file.；Function A uses many specific libraries (PrologParser, FactVisitor, ClassWriter), B uses standard Java I/O.；Function A has command-line argument handling and debug output; B does not.
- 修正建议: Enrich training data with more diverse non-clone pairs that share boilerplate but differ in functionality.；Incorporate dataflow or type-inference analyzers to distinguish file manipulation vs. transformation tasks.；Use contrastive learning to emphasize semantic differences beyond lexical overlap.

### case_id=3870 FN partial_functionality

- 方法: `login` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs in to LOLA by sending encoded email and password via HTTP POST, reads response to extract session ID, returns it.
- B 摘要: Reads a file from a given directory and filename, falling back to classpath resource, concatenates lines into a string, returns it.
- 静态失败原因: Static BERT focuses on token-level semantics and may be misled by low token overlap (0.1667) and domain-specific terms (login vs file), missing the structural I/O pattern that BCB considers.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as instances of 'read from a stream and return a string' pattern, despite different I/O domains, thus a broad Type-4 clone based on similar high-level functionality.
- 共享行为: Both use BufferedReader to read lines from an input stream；Both build a string from line reads；Both handle exceptions with try-catch；Both print status messages to System.out
- 行为差异: Function A performs network I/O (HTTP POST) while B performs file I/O；Function A uses URLEncoder for data encoding, B does not；Function A extracts a session ID from a single line, B concatenates all lines；Function B includes System.exit on certain errors, A returns empty string
- 修正建议: Add structural features that capture common I/O patterns；Use data flow analysis to detect similarities in input/output；Train on more diverse examples of stream reading clones

### case_id=3871 FN partial_functionality

- 方法: `getHTML` vs `readURL`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a URL using HTTP connection, reads line by line, optionally writes to file, and returns the HTML string.
- B 摘要: Opens a URL stream, reads lines and prints each to standard output.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized differences in method signature (return type), API calls (HttpURLConnection vs URL.openStream), and low token overlap, missing the behavioral similarity of reading URL content.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers these as broad Type-4 clones because both share the core functionality of reading line by line from a URL, despite differences in output handling and additional parameters.
- 共享行为: Both open a URL and read its content line by line in a loop
- 行为差异: A returns the read content as a string; B prints to console and returns void；A uses HttpURLConnection with User-Agent and encoding; B uses URL.openStream()；A optionally writes content to a file; B does not
- 修正建议: Train on more examples where functions have different I/O but similar core loops；Incorporate data flow or control flow features to capture the common read loop

### case_id=3872 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `handler`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads integer IDs from a resource file into a set.
- B 摘要: Reads a web page, extracts substrings matching patterns, and updates a map.
- 静态失败原因: Static model likely overemphasized common API calls (URL, InputStreamReader, readLine) and loop structure, ignoring the distinct data processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones due to entirely different core functionality (parsing integers vs string extraction), despite superficial API overlap.
- 共享行为: Both use URL to open a stream；Both read lines in a loop；Both handle IO exceptions
- 行为差异: File vs web page reading；Integer parsing vs string extraction；Return set vs update map；Different exception handling
- 修正建议: Incorporate program analysis to capture data flow and transformation；Use structure-aware models like AST or CFG；Train on more diverse non-clone examples with API overlap

### case_id=3873 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles action events like GRAPHVIZ, IMAGEMAGICK, and other settings, updating UI and saving preferences.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: Overlap in keywords like File, chooser, and path led to false positive; static BERT ignored the vast structural and contextual differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones even if there is superficial file-related API usage because the overall functionality is completely different.
- 共享行为: Both may involve file paths (A uses file chooser, B copies file) but no shared functionality.
- 行为差异: A is a large event handler with many UI interactions and preference saving; B is a simple file copy utility.；A has no actual file copying; B does not handle any UI or preferences.；A depends on specific UI components and application state; B is stateless and generic.
- 修正建议: Incorporate structural similarity or method length normalization.；Use dataflow analysis to distinguish file selection from file copying.；Augment training data with more diverse negative examples.

### case_id=3874 FN partial_functionality

- 方法: `addIDs` vs `setMembers`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches metabolite information from a web database for a given name, parses HTML to extract IDs and scores, and sets various properties on a PeakListRow object.
- B 摘要: Fetches a Trac ticket page, parses HTML to extract component and priority options from select elements, and stores them in static arrays.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low token overlap (0.1655) and widely different surface forms: different variable names, library calls, control flow structures, and one function having a truncated middle. The model overfits to lexical and structural details rather than capturing the abstract common pattern of URL fetching and HTML parsing.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both implement a common pattern: fetching HTML from a URL and extracting configuration or data from specific HTML structures. This aligns with Type-4 (functionally similar) clones, where the high-level purpose (web scraping and data extraction) is similar despite different specific targets and outputs.
- 共享行为: Both fetch a URL and parse HTML using string patterns or regex to extract structured data.
- 行为差异: They extract different types of data from different web pages; A sets properties on an object and returns a score, B stores in static arrays and returns void; A uses a parameterized URL, B uses a fixed URL based on getTracUrl(); A has a complex nested if-else structure, B uses simple while and if with pattern matching.
- 修正建议: Use structure-aware models that capture high-level common patterns (e.g., URL opening, line-by-line reading, pattern matching).；Incorporate dataflow analysis to identify common operations like 'open URL, read lines, search for pattern, extract substring'.；Augment training data with abstracted semantic representations or clone pairs with low token similarity but high functional similarity.

### case_id=3875 FN partial_functionality

- 方法: `runScript` vs `getPagina`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Run a script from the codebase URL by reading bytes and concatenating into a string.
- B 摘要: Fetch a webpage from a given URL by reading lines and concatenating into a string.
- 静态失败原因: Static BERT-based models often rely on surface-level token overlap and structural patterns; here the token Jaccard is low (0.27), method names differ significantly, and the control flow structures are different (do-while vs while, different exception handling). The model likely focused on these syntactic differences and missed the shared semantic purpose.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB labels as clone because both functions have the same high-level goal: fetching content from a URL and returning it as a string. The differences in reading method and error handling are considered minor variants under broad Type-3/Type-4 similarity.
- 共享行为: Both fetch content from a URL；Both concatenate content into a string；Both return the string；Both handle exceptions
- 行为差异: A reads byte by byte, B reads line by line；A constructs URL from codebase and script name, B takes full URL as argument；A returns 'error!' on exception, B returns exception details；A does not close the stream, B does
- 修正建议: Incorporate program dependence or data-flow graphs to capture the shared URL reading behavior；Use code summarization or IR techniques to compare high-level intention；Fine-tune with more BCB-style examples that emphasize functional similarity over syntactic exactness

### case_id=3876 FN partial_functionality

- 方法: `main` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts ZIP entries to files.
- B 摘要: Copies a file using NIO FileChannel transfer.
- 静态失败原因: The static model likely focused on low token overlap (Jaccard 0.14) and dissimilar structure, missing the partial functional similarity that BCB accepts.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may classify as Type-4 semantic clone because both functions achieve the high-level goal of transferring data from an input source to an output file, despite different implementation details.
- 共享行为: Both perform I/O operations to read data from a source and write to a file destination.
- 行为差异: A uses URL and ZipInputStream to handle ZIP extraction, B uses FileChannel for direct file copy.；A writes multiple files from ZIP entries, B writes a single output file.；A is a main method, B is a utility method.
- 修正建议: Train with more Type-4 clone examples to capture partial functional similarity.；Incorporate intent or high-level semantic features (e.g., I/O operations).

### case_id=3877 FN benchmark_preference_bias

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file using NIO FileChannel transferTo.
- B 摘要: Launches an Eclipse project configuration by parsing XML, setting Hibernate dialect, and performing reverse engineering setup.
- 静态失败原因: Static BERT predicted non-clone correctly; the error is due to BCB label being incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as file-related operations, but this is a stretch; possibly an annotation error.
- 共享行为: Both perform file I/O operations
- 行为差异: Function A is a simple file copy; Function B is a complex multi-step launch process；A uses FileChannel; B uses InputStream, ByteArrayOutputStream, IOUtils, etc.；B involves XML parsing, property setting, and project configuration; A just copies content；B handles exceptions and progress monitoring; A does not
- 修正建议: Reconsider BCB annotation for this pair; likely should be non-clone.

### case_id=3878 FP lexical_or_api_overlap

- 方法: `main` vs `readFixString`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses a Prolog file and generates adapter classes and resources.
- B 摘要: Reads a fixed-length string from an input stream and returns it as a string.
- 静态失败原因: Static BERT models may over-rely on superficial cues like both using I/O, try-catch blocks, and method return statements, leading to a false positive despite low token overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions serve entirely different purposes (adapter generation vs. string reading) with no overlap in core functionality.
- 共享行为: Both use I/O operations (file reading and stream copying).；Both return a value or print output.；Both handle exceptions.
- 行为差异: Function A is a complex multi-step generation task, while B is a simple read operation.；A manipulates files, classes, and serialization; B only reads from an input stream.；A has many branches and external library calls; B is concise and uses IOUtils.；Their inputs and outputs are completely different (arguments vs. stream length).
- 修正建议: Incorporate more diverse negative examples that share boilerplate but differ semantically.；Use abstract syntax tree (AST) or data flow information to capture structural differences.；Implement contrastive learning to distinguish fine-grained semantic differences.

### case_id=3879 FP lexical_or_api_overlap

- 方法: `readData` vs `getFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.92`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads data from static string fields or a file and populates several sets and maps with parsed tokens.
- B 摘要: Gets a file by checking in user directory or copying from a classpath resource.
- 静态失败原因: The static BERT model likely overemphasized shared keywords like 'File', 'IOException', and the try-catch structure, while missing the vast difference in core functionality and state modification.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely reject this as a clone because the methods have fundamentally different purposes and implementations, with minimal semantic overlap beyond basic file I/O.
- 共享行为: Both involve I/O operations (file reading in A, file/resource access in B).；Both handle IOException.
- 行为差异: A is void and modifies global state; B returns a File.；A parses tokenized data into multiple collections; B simply ensures a local file exists.；A reads from a file and processes each line; B reads a resource and saves to a file.；A uses StringTokenizer and various sets/maps; B uses File and stream classes.
- 修正建议: Incorporate data-flow analysis to distinguish state-modifying methods from simple getters.；Increase sensitivity to method return type and side effects.；Use structural matching that penalizes shallow lexical overlaps when the overall logic diverges.

### case_id=3880 FN partial_functionality

- 方法: `copyResource` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a single resource (URL or file) to a destination file using byte-by-byte stream reading and writing.
- B 摘要: Recursively copies a file or directory to a destination path using NIO FileChannel and MappedByteBuffer for efficient bulk transfer.
- 静态失败原因: Low token overlap (0.2029) and distinct API usage (streams vs NIO) and structural patterns (while loop vs conditional recursion) likely led the model to miss the common file-copy intent.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'file copy' functions, treating the directory handling in B as an extension of core functionality, thus accepting them as broad Type-4 clones.
- 共享行为: Both copy a file from a source to a destination.
- 行为差异: A only handles single files (no directory recursion); B handles directories recursively.；A uses InputStream/OutputStream with byte-by-byte reading; B uses FileChannel and MappedByteBuffer.；A can read from a URL; B only reads from local files.；A is a private instance method; B is a public static method.
- 修正建议: Use fine-tuning with a dataset of varied file-copy implementations to learn the common semantic purpose.；Incorporate data-flow or AST-based features to capture structural similarities despite different syntax.

### case_id=3881 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Processes HTTP GET request, retrieves a page, checks permissions, and optionally caches the page output to a file.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: The model correctly identified low token overlap and structural dissimilarity, but BCB's ground truth may reflect a different clone definition that emphasizes partial functionality (file I/O), which static BERT models fail to capture due to reliance on surface form and control flow.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have annotated these as clones based on a very broad Type-4 notion (both perform file copying/writing), overlooking the vast difference in overall functionality and context. Alternatively, the label might be an annotation error.
- 共享行为: Both involve file I/O operations (writing a file in A, reading and writing in B).；Both handle IOException.
- 行为差异: A is an HTTP servlet handler with complex business logic; B is a simple utility method.；A uses FileWriter and temporary files; B uses FileChannel.transferTo.；A has many additional steps (page lookup, permission checks, logging); B is minimal.；A writes HTML content; B copies raw bytes.
- 修正建议: Review BCB annotation guidelines for consistency, especially for Type-4 clones.；Incorporate task-level semantic understanding, e.g., fine-tuning on diverse functional roles.；Use dataflow analysis to distinguish core I/O operations from peripheral ones.

### case_id=3882 FN partial_functionality

- 方法: `httpRequestByPOST` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs HTTP POST request using Apache HttpClient and returns response body as string, with error handling setting lastErrorCode/lastErrorMessage and returning null.
- B 摘要: Reads data from a URL using URL.openStream(), parses lines into object fields (version, url, informations), handles IOException with error flags, and notifies listeners in finally block.
- 静态失败原因: Low token Jaccard (0.171) and reliance on surface forms; the model misses the high-level similarity due to different method names, library APIs, and variable names, and fails to recognize the common HTTP I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might label as clone because both functions perform HTTP GET/POST requests and read the response line by line, a core functional similarity that falls under broad Type-3/Type-4 clones in BigCloneBench.
- 共享行为: Both open a network connection to a URL；Both read data line by line using BufferedReader；Both handle IOException and set error fields
- 行为差异: Function A uses Apache HttpClient for POST; Function B uses URL.openStream() for GET；Function A returns response string; Function B stores parsed data in fields and notifies listeners；Function A has conditional return based on HTTP status code; Function B always reads and parses；Function B has switch-case parsing specific lines; Function A appends all lines
- 修正建议: Use data augmentation with varied API calls (e.g., HttpClient vs URL.openStream) to make model invariant to implementation details；Incorporate code abstraction or type information to capture network I/O patterns；Train on more diverse examples of HTTP request handling

### case_id=3883 FN benchmark_preference_bias

- 方法: `uncaughtException` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles uncaught exceptions with SWT GUI, showing error message and offering to submit bug report.
- B 摘要: Builds a site for editing by transforming XML/HTML and writing output files, with extensive debug logging.
- 静态失败原因: Static method correctly predicted non-clone (0) due to very low lexical overlap (0.055 Jaccard) and clearly different APIs/structures. No failure; it aligns with our analysis.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both methods as involving error handling and logging, but they are fundamentally different operations. The label is likely a false positive due to overly broad criteria or annotation noise.
- 共享行为: Both methods perform logging/debugging (log.error and DebugFile traces).；Both methods handle exceptions (Throwable in A, various IO/Transformer exceptions in B).
- 行为差异: A is a simple GUI event handler; B is a complex file and XML transformation routine.；A uses SWT display and shell; B uses file I/O, transformers, and string buffers.；A has no loop; B has a loop over pages.；A's core purpose is error reporting; B's core purpose is site generation.
- 修正建议: Re-evaluate BCB annotation for this pair; likely mislabeled.；Improve dataset cleaning by filtering out pairs with dissimilar intent despite superficial logging/error handling.

### case_id=3884 FN benchmark_preference_bias

- 方法: `addFileToTarGz` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Adds a file or directory recursively to a tar archive stream.
- B 摘要: Handles an Eclipse launch configuration by validating project structure, processing XML files, setting Hibernate properties, and scheduling an installation action.
- 静态失败原因: The static BERT/GraphCodeBERT model likely correctly predicted non-clone due to low token overlap (0.054) and clear functional dissimilarity; the error is that the model correctly rejected the pair while BCB label is incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this pair as a clone due to a broad interpretation of Type-4 clones where both functions involve 'processing' or 'I/O operations', but this is a stretch and likely a labeling error.
- 共享行为: Both use IOUtils.copy to copy data from an input stream to an output stream；Both involve file I/O operations
- 行为差异: Function A is a self-contained utility for tar compression; Function B is a complex Eclipse RCP launch handler with multiple steps and dependencies on Eclipse framework；Function A operates on a single file/directory; Function B reads multiple configuration files and modifies workspace resources；Function A has no concept of project, launch configuration, or UI; Function B is tightly coupled to Eclipse and Maven project structure；Function A is static and private; Function B is public and part of an Eclipse plugin
- 修正建议: Review BCB annotation to correct false positive labels；Focus on functional similarity rather than broad I/O or processing overlap；Increase token threshold or use semantic similarity metrics to reject such pairs

### case_id=3885 FN partial_functionality

- 方法: `getResourceAsStream` vs `CopyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a resource from a URL, caches it locally, and returns an InputStream to the cached file.
- B 摘要: Copies the contents of a source file to a destination file using FileChannel.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on lexical and structural differences (method names, API calls, control flow) and missed the abstract similarity of data transfer due to low token overlap and different libraries.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as data copying operations, thus labeling them as Type-4 clones despite different inputs and outputs.
- 共享行为: Both read from a source and write to a destination.；Both perform file output operations.；Both may throw exceptions.
- 行为差异: A reads from a remote URL with HTTP handling, B reads from a local file.；A caches data and returns an InputStream, B writes directly to an output file and returns void.；A has conditional caching and retry logic, B is straightforward.；A uses HTTPURLConnection and BufferedStream, B uses FileChannel.
- 修正建议: Incorporate data flow analysis to track data movement across different APIs.；Use dynamic or symbolic analysis to capture high-level intent like copying data.；Train on more diverse examples of abstract functional similarity.

### case_id=3886 FP boilerplate_overlap

- 方法: `doVersionCheck` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a version check URL, parses lines for build version strings, and triggers a version check dialog.
- B 摘要: Searches Google Images for album art by constructing a query URL, parsing HTML for image links, and adding them to a list.
- 静态失败原因: The static model likely overemphasized the structural similarity (try-catch, URL, BufferedReader, while read loop, string operations) and misjudged it as a clone. The low Jaccard similarity (0.18) suggests that lexical overlap alone cannot explain the false positive; rather, the model may have learned that the combination of these API calls implies a 'read from URL and parse' template, without capturing the different semantic intents.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall purpose (version checking vs. image search) and specific logic are distinct, despite sharing a common networking and parsing skeleton. The annotation preference focuses on functional semantic equivalence rather than generic structural patterns.
- 共享行为: Both open a network connection and read data line by line；Both perform string parsing on each line；Both use a try-catch block for error handling
- 行为差异: Function A reads from a URL defined by jEdit property; Function B constructs a URL dynamically；Function A parses for specific line prefixes ('.build', '.stablebuild'); Function B parses HTML for image URLs；Function A shows and hides a wait cursor; Function B does not manipulate cursor；Function A catches IOException only; Function B catches generic Exception
- 修正建议: Incorporate data flow analysis to track how parsed data is used (e.g., version comparison vs. image URL extraction)；Use method name and comments as semantic hints；Train with hard negative examples that share boilerplate but differ in task；Add context about side effects (cursor changes, dialog invocation) to distinguish behavior

### case_id=3887 FN benchmark_preference_bias

- 方法: `testSimpleQuery` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: A test method that inserts user data into a JCR repository and asserts a query returns the correct user.
- B 摘要: A servlet doGet method that retrieves a page by parameter, checks visibility, and writes the page HTML to the HTTP response.
- 静态失败原因: The model relied on token overlap and structural similarity, which are extremely low (Jaccard=0.043). It failed to recognize any high-level semantic similarity that BCB annotators might have seen.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both performing a 'get' operation (query vs. GET request) and writing output, considering them broad Type-4 semantic clones despite very different implementations and domains.
- 共享行为: Both retrieve a resource (source/page) and produce some output (XML/HTML)
- 行为差异: testSimpleQuery is a test with assertions and cleanup; doGet is production code with error handling and caching；testSimpleQuery uses JCR API for content management; doGet uses servlet API and page management；testSimpleQuery writes XML content and reads it back; doGet writes page HTML directly to response；testSimpleQuery has no user permission checks; doGet checks visibility and editability
- 修正建议: Incorporate broader semantic understanding beyond token overlap；Use program analysis to detect abstract patterns like 'retrieve and output'；Calibrate model to accept very high-level Type-4 clones if needed for benchmark alignment

### case_id=3888 FN partial_functionality

- 方法: `copyResource` vs `cpFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using byte-by-byte streaming.
- B 摘要: Copies a file to a target, with options for replacing existing files, handling directories, and buffer size.
- 静态失败原因: Static BERT/GraphCodeBERT models often rely on lexical and structural similarity. The low token Jaccard (0.2676) and different method signatures (parameters, error handling) lead to a non-clone prediction. The model fails to abstract away surface-level differences like URL vs File, byte-by-byte vs buffered reading, and the extra conditionals in B.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled as clone because both implement the core functionality of copying a file/resource to a destination, which is a common pattern. The differences in API (URL vs File) and additional features (replace, buffer) are considered variations of Type-3/Type-4 clones at the functional level.
- 共享行为: Both copy data from a source to a destination using input/output streams.；Both read bytes from the source and write them to the destination.；Both close streams after copying.
- 行为差异: A reads from a URL or file; B only reads from a file.；A uses byte-by-byte read; B uses buffered read (buffer size configurable).；B includes logic for handling directory targets, naming conflicts, and replace flag; A does not.；A throws Exception generically; B throws IOException specifically.
- 修正建议: Use data-flow analysis to identify core 'read-write' pattern across different APIs.；Train on more diverse examples of file-copying with variations in source type and buffering.；Incorporate byte-level I/O abstraction as a common subpattern.

### case_id=3889 FN benchmark_preference_bias

- 方法: `runInternal` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Fetches and parses an OPDS catalog from a URL, handling pagination, headers, and downloads.
- B 摘要: Reads from a fixed URL and discards all content without any processing.
- 静态失败原因: The static model likely relied on token overlap and structural similarity, which are extremely low (Jaccard=0.068), and failed to recognize any high-level functional commonality.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled it as a clone because both involve opening an HTTP URL and reading data, but the functional overlap is minimal and broader context is ignored.
- 共享行为: Both use URL connections to read data from a remote URL
- 行为差异: A includes error handling, header setting, redirect following, and complex parsing logic; B has no error handling or processing.；A handles pagination and downloads files; B only reads lines and does nothing with them.；A is a long, stateful method with multiple concerns; B is a trivial one-liner.
- 修正建议: Improve semantic understanding by incorporating control flow and data flow information.；Use fine-grained functional decomposition to compare sub-tasks.

### case_id=3890 FN partial_functionality

- 方法: `main` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: This function reads command line arguments for input/output file paths and an offset, then copies the input file to the output file starting from that offset using a buffered stream.
- B 摘要: This function configures and launches a NexOpen project in Eclipse, processing Maven POM files and setting up Hibernate reverse engineering resources.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on lexical overlap and structural similarity, which are very low here (token Jaccard 0.068). The abstraction level required to see the high-level similarity is beyond static models' capability. They tend to focus on surface-level tokens and control flow, so they miss the weak conceptual link.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this pair as clones because both functions have a 'launch' or 'main' role and perform I/O operations (specifically copying files in part). Additionally, both involve dealing with configuration parameters and system output. The high-level similarity of 'reading parameters and performing file operations' may lead BCB to label it as a Type-4 clone.
- 共享行为: Both functions perform file I/O operations (reading and writing files)；Both functions handle command-line-like parameters (one from args, one from ILaunchConfiguration)；Both functions use byte streams for file operations
- 行为差异: Function A is a simple file copy with an offset, while Function B is a complex Eclipse launch configuration process involving XML parsing, profile management, and resource generation.；Function A has no dependencies on Eclipse or project frameworks, while Function B is tightly coupled to Eclipse and NexOpen project structure.；Function A operates on raw files, while Function B operates on project resources and uses Eclipse API.；Function A has no error recovery except for number parsing, while Function B has multiple exception handlers and logging.
- 修正建议: Improve model's ability to recognize high-level semantic roles (e.g., main/launch methods)；Use techniques that capture broad functional similarities, such as code summarization or topic modeling；Incorporate documentation or API usage patterns to infer intent

### case_id=3891 FN benchmark_preference_bias

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file using NIO FileChannel transfer.
- B 摘要: Builds an editable website by processing pages, reading configuration files, performing string replacements, and writing output files.
- 静态失败原因: Static BERT correctly identified low lexical and semantic similarity (low Jaccard, different method names and complexity), predicting non-clone. From BCB's perspective, it 'failed' because BCB expects a clone label, but model's prediction is actually reasonable.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to superficial similarity in using file I/O APIs and exception handling, or due to an annotation error in the benchmark.
- 共享行为: Both involve file input/output operations.；Both use FileInputStream and FileOutputStream.；Both handle exceptions.
- 行为差异: Function A is a simple file copy; Function B is a complex multi-step process.；Function B includes loops, XML parsing, configuration properties, and string manipulation.；Function B writes multiple output files, while A writes a single output file.；Function B has a large number of parameters and local variables.
- 修正建议: Improve clone definition consistency; ensure Type-4 clones require genuine semantic equivalence.；Filter out pairs where only boilerplate file I/O is shared.

### case_id=3892 FP lexical_or_api_overlap

- 方法: `getPagina` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a web page from a URL and returns its content as a string, handling exceptions by returning the error message.
- B 摘要: Reads a service file from the classpath, parses it to find a class name, and loads/instantiates that class as a FrameworkFactory, throwing an exception if not found.
- 静态失败原因: The static model likely relied on overlapping tokens (URL, BufferedReader, InputStreamReader, readLine) and similar loop structure, ignoring the different method names, return types, and the actual data processing logic. It over-generalized the reading pattern.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone (0) because the functions are not semantically equivalent; they serve different purposes and manipulate the read data in completely different ways, despite some superficial API similarity.
- 共享行为: Both use URL, BufferedReader, InputStreamReader, and readLine to read text line by line.；Both handle IO-related exceptions.；Both have a loop that reads lines until null.
- 行为差异: Function A reads from a network URL (user-provided), function B reads from a classpath resource (hardcoded path).；Function A concatenates all lines into a string, function B processes each line looking for a non-comment class name.；Function A returns a string (content or error), function B returns a FrameworkFactory object or throws an exception.；Function A sets an Authenticator, function B does not.
- 修正建议: Improve sensitivity to method names and return types.；Incorporate dataflow analysis to track how the read data is used.；Consider the overall purpose via documentation or context (e.g., class names).；Use contrastive learning to distinguish similar API sequences with different intents.

### case_id=3893 FP lexical_or_api_overlap

- 方法: `SRWGuiClient` vs `readURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Constructor for a Swing browser GUI that reads XML from a URL, applies XSLT transformation, and displays the result as HTML.
- B 摘要: Method that reads lines from a URL and prints them to standard output.
- 静态失败原因: The model likely overfit on the local API sequence (url.openStream(), BufferedReader, readLine) which appears in both functions, ignoring the surrounding GUI setup and XML transformation code that defines the method's true purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the overall functionality and purpose are completely different (GUI browser construction vs simple URL reading and printing). Even though they share a common I/O pattern, the high-level semantics diverge significantly.
- 共享行为: Both open a URL and read its content line by line using BufferedReader/InputStreamReader
- 行为差异: Function A is a constructor that sets up a full GUI with buttons, text fields, and a scrollable HTML pane.；Function A optionally transforms XML with XSLT and sets content type.；Function B is a simple method that only prints lines and closes streams in a finally block.；Function B catches generic Exception, while A catches IOException and TransformerException specifically.
- 修正建议: Incorporate broader context like method name, class name, or surrounding code structure.；Use graph-based embeddings that capture control and data flow beyond local token sequences.；Train on diverse examples to reduce reliance on shallow API patterns.

### case_id=3894 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `init`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a properties file for internationalization by reading, updating a message value, and writing back.
- B 摘要: Initializes a report file, handles backup of existing report, and restarts by parsing old XML to recover completed documents.
- 静态失败原因: Static BERT likely relied on low token overlap (Jaccard 0.1789) and distinct API calls, correctly predicting non-clone; it failed to match BCB's possibly overbroad annotation standard.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have annotated these as clones due to both being file-manipulation methods that read, modify, and write files, perhaps considering Type-4 partial functionality similarity in the domain of configuration file handling.
- 共享行为: Both perform file I/O with reading and writing.；Both handle file existence checks and backup or copying.；Both use try-catch for exception handling.
- 行为差异: A works with .properties files under a specific path; B works with XML report files.；A updates a single key-value pair; B writes XML headers and processes multiple XML events.；B includes complex logic for restarting from a backup and filtering documents; A does not have restart logic.
- 修正建议: Improve static models to detect broad functionality similarity beyond lexical overlap.；Incorporate dataflow or structural patterns for file I/O operations.；Use context-aware embeddings that capture high-level intent (e.g., configuration update).

### case_id=3895 FP boilerplate_overlap

- 方法: `executePost` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Executes an HTTP POST request with given parameters and returns the response as a string.
- B 摘要: Reads a version check URL, parses build numbers, and calls another method to handle version comparison.
- 静态失败原因: The static model likely over-relied on overlapping API calls (URL, HttpURLConnection, BufferedReader, etc.) and the similar structural pattern of reading from a URL in a try-catch block, ignoring the semantic differences in data sending, parsing logic, and return behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they perform fundamentally different operations (POST vs GET/read-only), have different return types, and the shared boilerplate (URL opening, stream reading) is not sufficient to consider them functionally similar.
- 共享行为: Both use URL and open an HTTP connection/stream；Both read data line by line using BufferedReader；Both handle IO exceptions；Both close streams in a standard try-catch pattern
- 行为差异: executePost sends POST data (urlParameters) via DataOutputStream; doVersionCheck only reads from URL without sending data；executePost returns a response string; doVersionCheck is void and shows/hides a wait cursor on a View；executePost parses the entire response line-by-line; doVersionCheck searches for specific lines starting with '.build' or '.stablebuild'；Error handling: executePost prints stack trace and returns null; doVersionCheck displays an error dialog
- 修正建议: Incorporate dataflow analysis to distinguish between writing and reading operations on the connection；Add attention to method signatures and return types to avoid confusing void with non-void methods；Use context-aware embeddings that capture the purpose of the network request (POST vs GET)；Include more nuanced features like the specific headers set and the presence of output streams

### case_id=3896 FN partial_functionality

- 方法: `main` vs `postXml`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Constructs and sends an HTTP POST request to RenRen API with hardcoded parameters and prints the response.
- B 摘要: Sends an HTTP POST request with XML payload to a given URL with SOAP action and returns the response string.
- 静态失败原因: The methods have different method names, parameter lists, and surface-level API calls (PostParameter vs. writing XML). Token Jaccard similarity is low (0.16). Static models relying on token overlap or simple AST matching miss the higher-level pattern of HTTP POST communication.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as implementations of 'HTTP POST with request body and response reading', ignoring specific data format and minor details, thus labeling as a broad Type-3/Type-4 clone.
- 共享行为: Both open an HTTP connection；Both set request method to POST；Both enable output；Both write data to the connection
- 行为差异: A uses PostParameter objects to build query string; B writes raw XML string；A prints response to stdout; B returns response as String；A hardcodes URL and parameters; B takes URL, SOAP action, and XML as parameters；A sets specific headers (Content-Type, Accept) differently; B sets Content-Type text/xml and Accept application/soap+xml
- 修正建议: Augment training with API call sequences or dataflow graphs capturing steps like 'openConnection-setMethod-setDoOutput-write-read'；Introduce contrastive learning for pairs with shared I/O patterns despite different data formats；Use program slicing to extract common sub-behaviors

### case_id=3897 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles UI action events for various settings like Graphviz path, ImageMagick path, and other preferences, updating UI components and storing in controller.
- B 摘要: Copies a file from source to destination using Java NIO FileChannel.
- 静态失败原因: The model likely picked up on superficial lexical or API overlap (e.g., both involve File objects) but failed to capture the overall semantic difference due to limited context or reliance on token-level patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as not clones because they have completely different functionality and purpose, even under broad Type-3/Type-4 similarity criteria.
- 共享行为: No significant shared behavior
- 行为差异: A handles UI events and updates preferences, B is a low-level file I/O utility；A has complex conditional logic and multiple branches, B is a simple sequential operation；A modifies UI components, B does not interact with UI
- 修正建议: Improve model's ability to distinguish different overall method purposes by incorporating higher-level semantic features；Use data flow or call graph information to differentiate between UI event handlers and utility functions

### case_id=3898 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `copyFiles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale by reading, updating, or appending a message entry.
- B 摘要: Recursively copies files or directories from source to destination using FileChannel.
- 静态失败原因: The static model predicted non-clone correctly, but the BCB ground truth considered them clones. If we assume BCB is correct, the model failed due to low token overlap and different syntactic structures; however, from a semantic perspective, the functions are not equivalent.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both involving file operations (reading from one file and writing to another) and the presence of common I/O boilerplate, despite different semantic purposes.
- 共享行为: Both perform file I/O operations using Java standard library classes
- 行为差异: Function A reads and writes properties files with line-by-line parsing; B copies arbitrary files byte-by-byte；A handles locale-specific configuration updates; B handles recursive directory structure；A uses Reader/Writer and manual splitting; B uses FileChannel for efficient transfer；A may create a new file by copying a template; B always creates a copy of the source
- 修正建议: Use task-specific functional clustering to avoid overbroad clone categories；Incorporate higher-level semantic understanding of file operations beyond low-level I/O

### case_id=3899 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests to display a portal page, including permission checks, caching, and logging.
- B 摘要: Copies a file from source to destination with user confirmation for overwrite, progress display, and error handling.
- 静态失败原因: The static BERT model likely failed to detect the clone (predicted non-clone) because the functions are semantically different with low token overlap; however, BCB labeled them as clone, so the model actually correctly rejected the pair, and the misclassification is a benchmark issue.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may classify these as clones under a very broad Type-4 definition where any file I/O operation is considered similar, or due to a labeling error in the benchmark.
- 共享行为: Both involve file I/O operations (writing to a temporary file vs copying a file)；Both use try-catch-finally for exception handling；Both include logging or console output for progress
- 行为差异: Primary purpose: HTTP request handling vs file copy；Input: HTTP request parameters vs file paths；Output: HTTP response vs console and file system；Control flow: complex nested conditions for page rendering vs sequential buffer copying
- 修正建议: Review BCB annotations for this pair to ensure consistency with standard clone definitions；Consider removing or correcting the label if the functions are not semantically equivalent

### case_id=3900 FP lexical_or_api_overlap

- 方法: `main` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Copies files from a source to multiple targets, optionally deleting original files and performing SVN operations.
- B 摘要: Reads comma-separated configuration strings to populate multiple sets and a hash table for Tibetan Wylie transliteration.
- 静态失败原因: The model likely focused on overlapping boilerplate tokens (e.g., 'System.out.printf', 'try', 'catch', 'finally', 'File') and similar control flow structures, ignoring the core semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires both functions to solve similar tasks; here they are completely different domains (file copying vs. data parsing), so BCB would label them as non-clones.
- 共享行为: Both use loops and try-catch-finally blocks；Both use standard Java I/O or collections；Both print messages to stdout for progress or errors
- 行为差异: A performs file copying and deletion; B parses strings and populates data structures；A interacts with the file system and SVN; B initializes internal data for transliteration；A uses FileChannel and FileInputStream/FileOutputStream; B uses StringTokenizer, HashSet, and HashMap；A's output is about file operations; B's output is debug/error information
- 修正建议: Improve model to distinguish between task-specific code and generic boilerplate patterns；Incorporate data flow or data dependency analysis to understand what operations are performed；Add more negative training examples with structural similarity but different functionality

### case_id=3901 FP long_range_semantics

- 方法: `actionPerformed` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles UI events for setting preferences like GraphViz path, ImageMagick path, and other settings.
- B 摘要: Copies a file from source to destination using NIO channels and memory-mapped buffer.
- 静态失败原因: The model likely misclassified due to the extreme length of function A causing truncation, losing the overall context, and possibly overemphasizing superficial file-related tokens.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would label non-clone because the functions perform completely different tasks without any meaningful functional similarity.
- 行为差异: Function A is a lengthy event handler for UI preferences; Function B is a short file copy utility.；No overlap in actual logic or purpose.
- 修正建议: Improve model capacity to handle very long functions via chunking or hierarchical encoding.；Include length-aware preprocessing or focus on critical semantic segments.

### case_id=3902 FN partial_functionality

- 方法: `getFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its XML to set the endpoint, and returns the local file path.
- B 摘要: Compresses a file using GZip and writes the output to a .gz file.
- 静态失败原因: Static models like CodeBERT rely on token sequences and have low lexical overlap (Jaccard=0.13). They fail to capture high-level semantic similarity in I/O patterns when functions have different goals.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to common file I/O patterns (open, read, write, close) and exception handling, possibly as Type-4 (similar in data processing functionality) despite different purposes.
- 共享行为: Both perform file I/O operations using streams；Both handle IOException with try-catch；Both read from an input stream and write to an output stream；Both close streams after use
- 行为差异: A downloads from a URL, B reads a local file；A processes XML and modifies it, B does not；A returns a String, B is void；A uses NIO channels, B uses byte buffer
- 修正建议: Use control flow graph or data flow analysis to detect common I/O patterns；Train on datasets emphasizing partial functionality clones；Incorporate structural features like stream usage and exception handling

### case_id=3903 FP lexical_or_api_overlap

- 方法: `copy` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Recursively copies a file or directory from a Hadoop filesystem to a local destination, optionally deleting the source.
- B 摘要: Main method of AdapterGenerator that parses a Prolog file, generates adapter classes, and writes them to a JAR file.
- 静态失败原因: Static BERT/GraphCodeBERT likely overfocused on shared low-level API tokens (File, IOException, etc.) and common control-flow structures (try-catch, if-else), ignoring the high-level semantic intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates these as non-clones because they implement entirely different functionalities with no semantic overlap beyond generic I/O patterns.
- 共享行为: Both perform file I/O operations；Both check file existence and handle IOException；Both use File and related classes
- 行为差异: Function A copies data from a distributed filesystem to local disk; Function B generates code and writes to a JAR；Function A uses recursion and works with directories; Function B processes a single file with a fixed pipeline；Function A's output is a local file copy; Function B's output is a compiled JAR with multiple classes；Function A is a utility method; Function B is a main entry point with command-line parsing
- 修正建议: Incorporate data-flow and control-flow analysis to capture program purpose；Use function-level summarization or context from method names；Train on pairs with more diverse I/O patterns to better distinguish core logic from boilerplate

### case_id=3904 FN benchmark_preference_bias

- 方法: `addDataFromURL` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads content from a URL line by line and appends it to an internal text buffer, with fallback appending the URL string on exception.
- B 摘要: Constructs HTTP POST parameters for a social network API, sends the request, and prints the response to console.
- 静态失败原因: The static model correctly predicted non-clone due to low token overlap (0.14) and drastically different code structure; it did not fail, rather the BCB label may be erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions involving reading from a URL with BufferedReader, possibly under a broad Type-4 category of 'URL reading' operations, despite the significant differences in overall functionality.
- 共享行为: Both open an input stream from a URL；Both read lines using BufferedReader
- 行为差异: A appends to a string buffer; B prints to console；A handles exceptions by printing and appending URL; B throws IOException；B builds query parameters and sends a POST request; A just reads from a URL (implicitly GET)；A is an instance method; B is static main
- 修正建议: Re-evaluate BCB labeling guidelines to exclude such pairs with only superficial API overlap.；Consider using more fine-grained clone categories that separate generic I/O from specific application logic.

### case_id=3905 FN partial_functionality

- 方法: `getResourceAsStream` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource from a URL, caches it locally, and returns an InputStream, with HTTP handling and caching logic.
- B 摘要: Copies the contents of one file to another using character streams.
- 静态失败原因: Static models like GraphCodeBERT rely on surface syntax and data flow, which are very different between the two methods. The low Jaccard similarity (0.13) indicates little lexical overlap. The models might not capture the high-level functional similarity of data copying due to significant differences in API usage and control flow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both implement the core functionality of copying data from a source to a destination using streams, despite differences in source type, caching, and error handling. This falls under Type-4 (functionally similar) clones.
- 共享行为: Both read data from a source and write it to a destination；Both use stream I/O reading and writing character by character (or byte by byte)；Both close streams after use
- 行为差异: Code A involves network resource fetching, caching, and HTTP conditional requests, while Code B is a simple file copy；Code A uses byte streams (BufferedInputStream/BufferedOutputStream), Code B uses character streams (FileReader/FileWriter)；Code A has complex error handling and caching logic, Code B has no error handling beyond throwing IOException；Code A returns an InputStream, Code B is void and writes to a file
- 修正建议: Incorporate functional semantics via program analysis or docstring representations；Use data flow analysis that abstracts I/O operations to recognize 'copy' patterns；Train with more diverse examples of Type-4 clones to capture behavioral similarity beyond syntax

### case_id=3906 FN partial_functionality

- 方法: `login` vs `wordFrequency`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs in to a remote service by sending email and password via HTTP POST, reads the response, extracts and returns a session ID, with error handling returning empty string.
- B 摘要: Queries a web service for the frequency of a given word by replacing a placeholder in a URL, opens the URL, reads lines, matches a pattern, and returns the frequency integer, with error handling returning 0.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token sequences and structural representations; the low token Jaccard (0.168831) and very different method names ('login' vs 'wordFrequency') result in low similarity scores, and the model fails to capture the abstract functional similarity of 'HTTP query-and-parse' due to lack of training on such semantic patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB labels this pair as a clone likely because both functions share the high-level semantic intent of 'making an HTTP request and parsing the response to extract a value', despite differences in HTTP method, request construction, and parsing details, which is typical for Type-4 semantic clones.
- 共享行为: Both perform an HTTP request to a predefined URL；Both read the response line by line using BufferedReader；Both parse a specific pattern to extract a value；Both return a value derived from the response
- 行为差异: Login uses HTTP POST with URL-encoded data; wordFrequency uses HTTP GET without sending data；Login parses only the first line for session ID; wordFrequency loops through all lines matching a regex pattern；Login returns a String; wordFrequency returns an int；Error handling: login prints 'Login Error' and returns ''; wordFrequency prints stack trace and returns 0
- 修正建议: Train on more examples of semantic clones that share abstract patterns like 'read from URL and parse'；Use graph-based representations that capture data flow (e.g., URL construction, stream handling) to expose common structures；Incorporate API call semantics to recognize frequent combinations like URL, BufferedReader, InputStreamReader

### case_id=3907 FN partial_functionality

- 方法: `load` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads content from a pastebin URL based on an ID, reads line by line, returns concatenated string with basic error handling.
- B 摘要: Reads from a hardcoded URL, concatenates lines into StringBuilder, logs the result, throws exceptions.
- 静态失败原因: Low token Jaccard (0.2667) and differences in method signatures, error handling, and working flag led the static model to focus on surface differences rather than the common pattern of URL reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers functions that perform the same core I/O operation (reading from URL, line-by-line, concatenation) as clones, ignoring differences in error handling, return type, or specific URL.
- 共享行为: Opens a URL connection；Reads lines from an input stream using BufferedReader；Concatenates lines into a string (using StringBuilder or string concatenation)
- 行为差异: Function A constructs URL from parameter, B uses fixed URL；Function A returns the string, B logs it and returns void；Function A has try-catch with dialog, B throws Exception；Function A uses a working flag, B does not
- 修正建议: Use control flow or data flow graph representations；Incorporate token similarity with allowance for structural variations；Train on more examples of Type-3/Type-4 clones

### case_id=3908 FP boilerplate_overlap

- 方法: `main` vs `unJarStart`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses a Prolog file, generates adapter classes and resources, and writes them into a JAR file.
- B 摘要: Private method that extracts files from a JAR archive starting with a given entry prefix to a specified path.
- 静态失败原因: The static model likely overemphasized boilerplate patterns like try-catch, e.printStackTrace(), File and JarFile usage, which are common in many Java functions, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically annotates based on functional similarity or syntactic similarity; these functions have no common domain logic and low token overlap, so they would be labeled as non-clone.
- 共享行为: Both involve file I/O and exception handling with try-catch blocks.
- 行为差异: Function A parses Prolog and generates adapters; Function B extracts files from a JAR.；Function A writes classes and resources; Function B copies JAR entries to the filesystem.；Function A uses complex visitor and generation patterns; Function B uses simple loop and copy.
- 修正建议: Improve training with negative examples of boilerplate-only similarity；Focus on behavioral semantics rather than surface patterns；Use dataflow analysis to distinguish different file processing logic

### case_id=3909 FN partial_functionality

- 方法: `getResourceAsStream` vs `extractFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource via URL, caches it locally, and returns an InputStream.
- B 摘要: Copies the content of an input file to an output file.
- 静态失败原因: Static BERT models rely on lexical and structural overlap; low token Jaccard (0.1456), different method names, APIs (URL vs FileReader), and control flow make them appear non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'stream copy' operations, ignoring higher-level context like caching and HTTP, thus labeling them as Type-4 clones.
- 共享行为: Reads from an input stream and writes to an output stream in a loop
- 行为差异: A involves HTTP connection, caching, and returns an InputStream; B is a simple file copy.；A uses BufferedInputStream/OutputStream; B uses byte array buffer.；A handles exceptions and prints progress messages; B throws exceptions out.
- 修正建议: Incorporate data-flow analysis to detect I/O patterns.；Use semantic models that abstract away specific APIs and focus on intent.

### case_id=3910 FP lexical_or_api_overlap

- 方法: `main` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Tests the StraightStreamReader class by writing bytes to a file and reading them back with various methods, verifying correctness.
- B 摘要: Handles GUI action events to configure application settings like file paths, look-and-feel, and other preferences.
- 静态失败原因: The model likely over-relied on superficial lexical overlaps (e.g., 'File f = new File') and the presence of loops and conditionals, while missing the entirely different overall semantics due to long-range dependencies and lack of understanding of the larger program context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions perform entirely different tasks with no shared algorithm or business logic. Here, the functions have no functional overlap beyond trivial file handling, so BCB correctly marks them as non-clones.
- 共享行为: Both use File objects for file operations.；Both contain try-catch blocks for exception handling.
- 行为差异: Function A is a unit test for stream reading; Function B is a GUI event handler.；Function A writes and reads binary data; Function B sets configuration preferences and opens file choosers.；Function A's control flow is linear with multiple read tests; Function B's control flow depends on action command strings.；Function A uses System.err for error output; Function B uses logger and dialog messages.
- 修正建议: Improve sensitivity to high-level syntactic structures like method declarations and control flow.；Incorporate program dependence or data-flow features to distinguish testing code from GUI code.；Use larger context windows or hierarchical encoding to capture method-level semantics.

### case_id=3911 FN benchmark_preference_bias

- 方法: `PageLoader` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads the entire content of a web page given by URL into a single string.
- B 摘要: Parses a configuration file for Tibetan transliteration, populating multiple sets and mapping tables.
- 静态失败原因: Static BERT models may not capture the high-level functional similarity that BCB annotators perceived; they rely more on token-level overlap which is low here. Also, the long length and truncation of function B may hinder understanding.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'loading data' functions even though the source and structure differ, possibly due to partial functionality similarity in generic input reading.
- 共享行为: Both read textual input；Both process data sequentially
- 行为差异: Function A fetches from URL; Function B reads from pre-parsed tokens and a file；Function A produces a single string; Function B populates multiple sets and maps；Function A is simple; Function B is complex with many conditional branches
- 修正建议: Incorporate structural information or data flow to better detect broad functional similarity；Use context-aware embeddings that capture long-range interactions

### case_id=3912 FN library_context_missing

- 方法: `copyResource` vs `doCopyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `context_recovery_then_expert`；动态可解性: `low`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using a byte-by-byte stream copy.
- B 摘要: Copies a file to another file using NIO channels with size verification and optional date preservation.
- 静态失败原因: Static BERT/GraphCodeBERT models often fail to capture structural similarities across different APIs (streams vs NIO channels), relying on token and AST patterns; low token Jaccard and different method signatures, control flow, and library usage lead to a non-clone prediction.
- 静态 case study: 该类错误缺少关键上下文或需要深层语义，纯静态方法不可靠。
- 动态 case study: 动态执行价值较低：样本可能依赖库、框架、网络、GUI、数据库或项目上下文，需要先恢复环境或 mock 依赖。
- BCB 偏好解释: BCB likely labels as clone because both functions accomplish the same high-level task of copying a file (or resource) to another location, considered the same functionality in their benchmark despite differing APIs and error handling.
- 共享行为: Both copy file contents from source to destination
- 行为差异: A supports URL sources, B only file；A uses stream read/write loop, B uses NIO transferFrom；A does not verify copy integrity, B checks file size；A does not preserve date, B optionally does
- 修正建议: Incorporate API knowledge via embedding or pre-training on code with diverse libraries；Use graph-based representations that capture data flow；Augment model with bytecode or dynamic analysis；Use contrastive learning to align semantically similar code using different APIs

### case_id=3913 FN partial_functionality

- 方法: `File2String` vs `PhoneSetImpl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file from local path or classpath resource, concatenates all lines into a string, and returns it, exiting on failure.
- B 摘要: Constructor that reads lines from a URL, filters out lines starting with '***', and adds them to a map using parseAndAdd.
- 静态失败原因: The low Jaccard similarity (0.24) and different method names, class names, and error handling tokens caused the model to miss the structural similarity of the line-reading loop. The model may lack sensitivity to common control flow patterns when surrounded by different context.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as clones because they share the core pattern of opening a stream and reading lines with BufferedReader, a common I/O boilerplate, and the differences in source type and post-processing are considered partial functionality changes.
- 共享行为: Both open an input stream and create a BufferedReader；Both read lines in a while loop until null；Both close the BufferedReader
- 行为差异: A reads from File or classpath URL; B reads from a single URL；A returns concatenated string; B modifies internal map；A uses System.exit on errors; B throws IOException；A reads all lines; B filters and processes lines
- 修正建议: Incorporate graph-based representations to capture data flow and control flow；Use normalization of common I/O patterns like reading lines；Train with more diverse examples of similar boilerplate patterns

### case_id=3914 FN benchmark_preference_bias

- 方法: `doGet` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Processes an HTTP GET request to retrieve a page, check permissions, log, and render the response.
- B 摘要: Demonstrates file channel I/O operations for reading and writing bytes to a file.
- 静态失败原因: Static BERT correctly predicted non-clone (0) based on low token overlap and semantic dissimilarity; it did not fail from our perspective. The error type FN indicates BCB considers it a clone, so from BCB's view, the model may have been misled by the lack of common API or structural similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both involving reading/writing data, but the functionality is entirely unrelated; this is likely a benchmark annotation error or overly broad Type-4 inclusion.
- 共享行为: No shared behavior; both perform I/O but in completely different contexts.
- 行为差异: Different inputs and outputs (HTTP request/response vs file system)；Different purpose (web page rendering vs file I/O demonstration)；Different libraries and APIs used (Servlet, Portal, vs FileChannel, ByteBuffer)
- 修正建议: Improve benchmark annotation consistency by ensuring Type-4 clones share core functionality.；Consider excluding such unrelated pairs from the gold standard.

### case_id=3915 FN partial_functionality

- 方法: `getHTML` vs `callApiPost`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML content from a URL via HTTP GET and optionally writes it to a file.
- B 摘要: Sends an HTTP POST request with parameters and returns an InputStream, checking response code.
- 静态失败原因: The model likely overemphasized lexical differences (low Jaccard, different method names, return types) and structural variations (GET vs POST, file writing), missing the core similarity of making an HTTP connection and processing the response. It may lack abstraction to recognize shared network communication patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs as clones if they perform the same high-level task (e.g., HTTP request/response handling) even with different implementations, considering them Type-4 functional clones.
- 共享行为: Both use HttpURLConnection to make an HTTP request.；Both set request properties (User-Agent or custom headers).；Both handle input streams from the connection.；Both include exception handling for I/O errors.
- 行为差异: A uses GET method; B uses POST method.；A returns a String; B returns an InputStream.；A optionally writes the response to a file; B does not.；B sends request parameters and checks expected response code; A does not.
- 修正建议: Augment training data with diverse HTTP client methods to teach model functional abstraction.；Incorporate dataflow analysis to detect common connection setup and data retrieval patterns.；Use API-level embeddings or domain-specific knowledge about HTTP operations.

### case_id=3916 FN benchmark_preference_bias

- 方法: `getEncoding` vs `readURL`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Opens a URL connection, reads headers and content to detect and return the character encoding.
- B 摘要: Opens a URL stream, reads lines and prints them to standard output.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed because the token Jaccard similarity is low (0.2), method names differ, and the behavioral goal is clearly different. The model may prioritize semantic equivalence over structural overlap, missing BCB's broader clone definition.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider this a Type-3 or Type-4 clone because both methods share a common structure: opening a URL, reading line by line, and closing resources. The overall task of 'reading from a URL' is considered similar, even if the extracted data is used differently.
- 共享行为: Both open a URL and read lines from it；Both use try-finally to ensure resource closure；Both catch exceptions (though B catches Exception, A throws IOException)
- 行为差异: A extracts encoding from headers and content; B prints each line to stdout；A returns a String; B returns void；A checks content-type header; B does not
- 修正建议: Increase sensitivity to structural patterns like try-finally with resource handling；Incorporate task-level similarity heuristics for I/O operations

### case_id=3917 FN benchmark_preference_bias

- 方法: `main` vs `transformSingleFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, unzips it, and extracts all entries to files.
- B 摘要: Compresses an X3D file to GZIP format using a helper transformation.
- 静态失败原因: Static BERT correctly predicted non-clone but was considered to fail relative to BCB label. The model likely captured semantic dissimilarity: one decompresses, the other compresses.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might label this as clone due to superficial structural similarity: both use FileInputStream, buffer loops, and stream chaining. The shared I/O pattern outweighs different high-level purposes in BCB annotation guidelines.
- 共享行为: Both read binary data in chunks using a buffer and write to output streams.
- 行为差异: Function A extracts from a ZIP archive; Function B compresses to GZIP.；Function A handles multiple entries; Function B handles a single file.；Function A has no error handling; Function B catches exceptions and returns null.；Function A is a standalone main; Function B is an overridden method in a larger system.
- 修正建议: Re-evaluate BCB label: these functions are not semantic clones.；If BCB intends to include broad I/O pattern clones, add more nuanced guidelines.；Use semantic-level features to distinguish compression vs. decompression.

### case_id=3918 FN partial_functionality

- 方法: `copyResource` vs `copyToDir`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (from URL or file) to a destination file using byte-by-byte read/write and throws exception on failure.
- B 摘要: Copies a file to a target directory using a buffered but buggy read-write loop, creates directories if needed, updates internal state, and logs exceptions.
- 静态失败原因: Low token overlap (0.267) and distinct method signatures, control flow, and variable names caused the model to miss the shared functional similarity. Static BERT models lack deep understanding of I/O operations and can be misled by surface differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels as clones when functions share high-level functionality like file copying, even with differences in buffering, error handling, and auxiliary behavior. The core operation is the same.
- 共享行为: Both copy file content from a source to a destination using FileInputStream and FileOutputStream.；Both read bytes until end of stream and close streams after operation.
- 行为差异: A reads one byte at a time; B uses a 1024-byte buffer (with a loop bug).；A can read from a URL; B only from a local file.；A creates no directories; B creates target directory if missing.；A throws Exception on failure; B catches IOException and logs it.
- 修正建议: Train on more diverse file copy examples with varying implementations.；Incorporate data-flow or control-flow graphs to capture structural similarity.；Use clone detection specific fine-tuning with contrastive learning on pairs like this.

### case_id=3919 FP boilerplate_overlap

- 方法: `doRawRequest` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs a raw HTTP POST request and returns the response as a string.
- B 摘要: Performs a Google image search, extracts image URLs, and updates the UI without returning a value.
- 静态失败原因: The model likely over-weighted the overlapping tokens (URL, openConnection, BufferedReader, readLine, loop) and ignored differences in HTTP method, return type, and post-processing logic. The boilerplate code is common, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled them as non-clones because the overall functionality and purpose differ significantly: one is a generic HTTP utility, the other is a specific application-level search with UI side effects. The shared URL-reading boilerplate is considered incidental, not core functionality.
- 共享行为: Open a URL connection；Read the response line by line using BufferedReader；Close the reader
- 行为差异: A uses POST (writes postData), B uses GET (no output)；A returns the raw response string, B does not return anything；B sets a User-Agent header, A does not；B parses the response to extract image URLs and updates global state and UI
- 修正建议: Incorporate method signature and return type information into the model；Use data flow analysis to distinguish between write and read operations；Consider side effects such as global variable updates or UI changes；Train with more examples that differentiate HTTP utilities from application-specific functions

### case_id=3920 FP boilerplate_overlap

- 方法: `readUNI` vs `sendRequest`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL, parses tab-separated lines, and adds ID and description to a list.
- B 摘要: Sends an XML request to a servlet via HTTP with GZIP compression, receives XML response, and parses it.
- 静态失败原因: The static model might have overemphasized common keywords like URL, InputStream, try-catch, and scanner/reader patterns, ignoring the drastic difference in overall logic and data flow. Possibly also due to limited context or shallow representation.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely correctly labels this as non-clone because the functions have completely different purposes and only superficial structural similarities (e.g., URL usage) that are too generic.
- 共享行为: Use URL to open connection/stream；Read from an input stream；Handle exceptions with try-catch-finally
- 行为差异: readUNI only reads data; sendRequest both sends and receives；readUNI parses plain text; sendRequest uses XML and GZIP；sendRequest involves complex URL construction from preferences and dialogs；sendRequest uses multiple compression and output streams
- 修正建议: Improve model to focus on semantic intent rather than just syntactic patterns；Incorporate data flow and control flow analysis；Use larger context or whole program analysis to differentiate

### case_id=3921 FN benchmark_preference_bias

- 方法: `addToArchive` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Writes input stream to a zip entry within a pod archive and returns a URL.
- B 摘要: Handles Eclipse launch configuration for NexOpen projects by parsing XML, setting properties, and creating reverse engineering files.
- 静态失败原因: Static BERT correctly identified these as non-clones (prediction 0), but the BCB label is 1, so it 'failed' to match the benchmark label. The failure is not a model error but a benchmark mislabeling.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to surface-level similarities: both methods involve file operations and use IOUtils, and both may be part of larger frameworks (pod or Eclipse). However, the overall functionality is distinct.
- 共享行为: Both use IOUtils.copy to copy input streams
- 行为差异: Function A is a short, focused utility to add a file to a zip archive; function B is a long, complex method with multiple sub-steps for launching an Eclipse configuration.；Function A has clear input-output (InputStream to ZipEntry, returns URL); function B has side effects (modifying project resources, creating files) and no return value.；The contexts are completely different: pod archive vs Eclipse IDE plugin launch.
- 修正建议: Re-evaluate the BCB label for this pair; it likely should be 0 (non-clone).；If the benchmark is considered ground truth, the model may need to better capture broad, thematic similarities, but that could degrade precision.

### case_id=3922 FP lexical_or_api_overlap

- 方法: `SRWGuiClient` vs `postXml`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Constructor that sets up a GUI browser, reads XML from a URL, optionally transforms it with XSLT, and displays HTML.
- B 摘要: Private method that sends an HTTP POST request with XML content and returns the response body as a string.
- 静态失败原因: The static BERT/GraphCodeBERT model likely over-relied on overlapping tokens like 'URL', 'BufferedReader', 'IOException', and similar control flow patterns (try-catch, while loop). It failed to capture the overall semantic context—one constructs a browser, the other posts XML.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels them as non-clone because they perform entirely different tasks: one is a GUI application initializer, the other is an HTTP client utility. The superficial API overlap (URL, BufferedReader) is not enough for functional similarity.
- 共享行为: Both use URL and URLConnection classes.；Both read from a BufferedReader.；Both handle IOException.
- 行为差异: Function A creates a GUI window and displays content; Function B is a utility method returning a string.；Function A reads XML from a URL via GET; Function B sends XML via HTTP POST with SOAP headers.；Function A may apply XSLT transformation; Function B does not transform.；Function A is a constructor with side effects; Function B is a simple method without GUI.
- 修正建议: Incorporate structural information (e.g., AST, data flow) to differentiate GUI code from networking code.；Use contrastive learning to emphasize semantic differences over lexical similarities.；Increase training data with examples where token overlap exists but semantics differ.；Add attention mechanisms that focus on method purpose or class context.

### case_id=3923 FP lexical_or_api_overlap

- 方法: `run` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads URL content, parses first two lines as version and URL, accumulates rest, and notifies listeners.
- B 摘要: Reads YouTube page, extracts fullscreen URL parameters, constructs and returns a video download URL.
- 静态失败原因: Static models may be misled by similar API usage (URL, BufferedReader, readLine) and control flow (try-catch, loop, string parsing), overlooking the distinct parsing logic and semantic intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions have different high-level goals despite sharing low-level I/O patterns; they are not functionally equivalent or substitutable.
- 共享行为: Open URL connection；Read lines with BufferedReader；Try-catch for IOException/Exception；Parse string data from lines
- 行为差异: Purpose: update version/URL info vs. extract YouTube video URL；Parsing logic: switch on line index vs. search for specific keyword；Output: store to class fields and notify listeners vs. return constructed URL；Error handling: specific French error messages vs. generic error print
- 修正建议: Emphasize unique string patterns and parsing targets；Incorporate data flow to track how parsed data is used；Add attention to method names and comments indicating purpose

### case_id=3924 FP boilerplate_overlap

- 方法: `getUser` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from a DAO or a config file with colon-separated values, parsing and saving the user.
- B 摘要: Queries a REST API for open tickets in a queue, parses the response to extract ticket IDs, then retrieves each ticket.
- 静态失败原因: Static BERT/GraphCodeBERT might have over-emphasized superficial similarities like BufferedReader usage, exception handling patterns, and parameter usage, while missing the fundamental difference in domain and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have completely different purposes and algorithmic logic, despite sharing generic I/O patterns.
- 共享行为: Both use BufferedReader to read lines from an input source.；Both handle exceptions with try-catch blocks.；Both return a value (User or List<RTTicket>).
- 行为差异: A reads from local file or database; B makes HTTP GET requests.；A returns a single User; B returns a List of tickets.；A uses StringTokenizer; B uses NameValuePair and URLEncodedUtils.；A's logic is about user authentication; B's logic is about fetching support tickets.
- 修正建议: Incorporate higher-level semantics by analyzing method names and comments.；Use data flow analysis to distinguish between local file I/O and network requests.；Train with more negative examples involving similar boilerplate but different functionality.

### case_id=3925 FP boilerplate_overlap

- 方法: `readData` vs `unzipEntry`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses CSV strings to populate various sets and maps for Tibetan transliteration data.
- B 摘要: Extracts a single entry from a zip file to a specified output directory.
- 静态失败原因: The static BERT model likely over-relied on surface-level patterns like 'private static void', 'IOException', and file-related keywords, ignoring the drastically different control flows and data manipulations. The low token Jaccard (0.025) indicates minimal lexical overlap, suggesting the model may have been misled by boilerplate common to many Java methods.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions perform completely different tasks: one is data initialization/parsing, the other is file extraction. They share no functional similarity.
- 共享行为: Both are private static void methods.；Both involve exception handling for IO operations.
- 行为差异: Function A parses string tokens and populates data structures; Function B performs file I/O extraction.；Function A is long and complex with many conditionals; Function B is short and straightforward.；Function A uses StringTokenizer; Function B uses BufferedInputStream/BufferedOutputStream and IOUtils.copy.；Function A has no return value and no parameters; Function B takes ZipFile, ZipEntry, and File parameters and throws IOException.
- 修正建议: Train model to distinguish high-level semantics using program analysis features like data flow and call graphs.；Incorporate method-level summaries from docstrings or identifiers to capture purpose.；Use contrastive learning with negative pairs that differ in functionality but share trivial patterns.

### case_id=3926 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `import_hints`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a Twitter user timeline JSON via HTTP and returns it as a string.
- B 摘要: Imports hints from a file or URL, parsing tokenized data to place puzzle pieces on a board.
- 静态失败原因: The model likely overemphasized the common I/O pattern (BufferedReader, InputStream, line reading) and exception handling, while ignoring the distinct API calls and post-read processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have entirely different purposes (raw data retrieval vs structured import with domain-specific operations) despite sharing I/O boilerplate.
- 共享行为: Both use BufferedReader and InputStreamReader to read input line by line；Both catch IOException
- 行为差异: A uses HttpClient for HTTP GET; B directly opens a URL stream or file；A appends lines to a StringBuilder and returns the result; B parses tokens and manipulates a game board；A logs failure on non-200 status; B returns false on IOException；A has no file/URL selection logic; B has conditional logic for byurl boolean
- 修正建议: Integrate dataflow analysis to track how read data is used after reading；Increase weight on method-specific API calls (e.g., HttpGet vs URL.openStream)；Train on more examples that distinguish boilerplate from core logic

### case_id=3927 FN partial_functionality

- 方法: `main` vs `extractImage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts all entries to local files using ZipInputStream.
- B 摘要: Processes an image file using Djatoka library, applies scaling/transform, and writes the result to an output file.
- 静态失败原因: Static BERT/GraphCodeBERT relies heavily on lexical overlap and syntactical structure; the low token Jaccard (0.16) and different domain-specific method names (main vs extractImage, ZipInputStream vs BufferedImage) cause it to miss the underlying functional similarity in I/O pipeline.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones as Type-4 (functionally similar) because both encapsulate a common pattern: obtain input, transform/process, write output. The broad acceptance of partial functionality similarity in BCB annotates them as clones despite different specific domains.
- 共享行为: Both read from an input source (URL stream or image file) and write to output files.；Both use BufferedOutputStream and FileOutputStream for writing.；Both perform data processing (extraction vs image transformation) before writing.
- 行为差异: Function_a extracts multiple files from a ZIP archive; function_b processes a single image.；Function_a writes each extracted entry individually; function_b writes one output file.；Function_a has no error handling; function_b has try-catch for IOExceptions.；Function_a uses URL and ZipInputStream; function_b uses Djatoka library and BufferedImage.
- 修正建议: Enhance model with dataflow analysis to recognize common I/O patterns across different libraries.；Include more diverse training examples of Type-4 clones with low lexical overlap.；Use a larger context window or structural embeddings to capture pipeline similarities.

### case_id=3928 FN boilerplate_overlap

- 方法: `getResourceAsStream` vs `writeData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource from a URL, caches it locally, and returns an InputStream.
- B 摘要: Writes data to a file in a tab-delimited format with metadata and peak values.
- 静态失败原因: Static BERT models rely heavily on token overlap and method name similarity, which are low in this pair (Jaccard 0.17). The model likely missed the structural similarity in I/O boilerplate, leading to a non-clone prediction.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled these as clones due to both containing file I/O operations and similar error handling patterns, but the core functionality is entirely different.
- 共享行为: Both perform file I/O operations；Both use try-catch blocks for exception handling；Both close streams/writers in a finally-like manner
- 行为差异: Function A reads from a network resource and caches to a file, while B writes formatted data to a file；Function A returns an InputStream, B returns void；Different method signatures and parameters；Function A involves HTTP connection and caching logic, B does not
- 修正建议: Enhance model to focus on control flow and data flow rather than just surface tokens；Incorporate API call sequences to detect functional similarity better

### case_id=3929 FN partial_functionality

- 方法: `getEncoding` vs `wordFrequency`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Get encoding from HTTP response headers or body.
- B 摘要: Get word frequency from a web service by replacing a placeholder.
- 静态失败原因: Low token overlap (0.21), different method names and return types, and different string operations lead the model to focus on lexical differences, missing the shared high-level control flow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: Both functions implement a common web scraping pattern: open URL, read lines, extract desired info. BCB's broad Type-3/Type-4 criteria accept such structural and behavioral similarity even if the specific domain differs.
- 共享行为: Open URL connection；Read input stream line by line；Parse/extract information from lines；Return a result
- 行为差异: A extracts encoding string from headers/body; B extracts integer frequency from body；A uses both header fields and body; B only uses body；A returns default encoding; B returns 0 on failure；Different input: none vs. word string
- 修正建议: Incorporate AST or CFG features to capture structural patterns；Use contrastive learning to better align similar patterns；Enhance training data with more diverse clones of web scraping patterns

### case_id=3930 FN benchmark_preference_bias

- 方法: `getDatasetsList` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Fetches a list of dataset names from a server URL by reading lines from the stream with caching.
- B 摘要: Reads a geo-parser result by constructing an XML request, fetching XML, parsing it to extract place names and optional gazetteer IDs, with retry logic.
- 静态失败原因: The static model correctly focused on low lexical and structural similarity, but BCB's broader definition of functional similarity may consider both as 'fetch-and-process' clones, leading to false negative.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider a broad Type-3/4 clone because both functions fetch data from a remote URL and process lines, but the specific domain and processing are very different.
- 共享行为: Both open a URL and read lines from the stream using BufferedReader.
- 行为差异: Different input and output types: String->List<String> vs (String, boolean)->Collection<Tuple>；A uses a cache, B does not; B has retry logic and a testing mode.；A performs no parsing, B involves complex XML processing.；URL construction differs: A appends a fixed query parameter, B builds an XML request and encodes it.
- 修正建议: Consider adjusting the model to better capture high-level intent like 'remote data retrieval'.；Alternatively, align training data with BCB's annotation style to reduce false negatives for such broad clones.

### case_id=3931 FN partial_functionality

- 方法: `getWebByUrl` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches a web page from a URL, reads it line by line, and writes the content to a local file, also recursively processes links.
- B 摘要: Reads a file from the filesystem or classpath resource line by line and returns its content as a string.
- 静态失败原因: Static models rely on token overlap, which is low (0.2 Jaccard), and focus on different API keywords (URL vs File), missing the structural similarity of the read loop.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers Type-3/Type-4 clones based on partial structural similarity, and the common readLine loop pattern may be enough to label them as clones despite different high-level functionality.
- 共享行为: Both read text input line by line using BufferedReader and InputStreamReader.
- 行为差异: A writes to a file and may recursively fetch links; B returns a string and reads from local/resource.；A handles URL connections; B handles file and resource loading.
- 修正建议: Enhance models to recognize common I/O patterns like readLine loops despite different variable names and surrounding code.；Incorporate dataflow or control-flow analysis to capture structural clones.

### case_id=3932 FN partial_functionality

- 方法: `copyResource` vs `upload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a resource from a URL or file to a destination file using a byte-by-byte loop.
- B 摘要: Uploads an image file to a fixed destination path using IOUtils.copy.
- 静态失败原因: Low lexical overlap (Jaccard 0.063) and different method names/libraries, causing the model to miss the functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered both as file copy operations, accepting broad Type-4 functional similarity despite API differences.
- 共享行为: Both copy data from an input source to an output file
- 行为差异: Source type: URL or file vs fixed file；Error handling: throws exception vs print stack trace；Copy method: manual loop vs IOUtils.copy；Return value: void vs String
- 修正建议: Use code embeddings that capture functional semantics beyond lexical tokens；Train with pairs having diverse APIs but similar data flow

### case_id=3933 FP lexical_or_api_overlap

- 方法: `postXml` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with XML payload and returns the response.
- B 摘要: Downloads a YouTube page, extracts video metadata, and constructs a full video URL.
- 静态失败原因: Static model likely over-relied on overlapping tokens like URLConnection, BufferedReader, setDoOutput, and exception handling, missing the semantic difference in control flow (POST vs GET, writing vs parsing).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as 0 because the functions have entirely different high-level purposes; structural overlap is only boilerplate Java networking code.
- 共享行为: Open a URL connection；Set doOutput to true；Read response with BufferedReader；Handle IOException
- 行为差异: A sends POST with XML; B does GET without writing；A sets multiple request headers; B does not；A writes XML to output stream; B only reads；B parses response for 'fullscreenUrl' and extracts parameters; A returns entire response
- 修正建议: Incorporate dataflow analysis to detect output stream usage vs. response parsing only；Train on more diverse examples to distinguish boilerplate from core logic

### case_id=3934 FN partial_functionality

- 方法: `encodeFileToFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Encodes a file to another file using Base64 encoding.
- B 摘要: Retrieves a resource as an InputStream, with caching behavior.
- 静态失败原因: The model overemphasized lexical and syntactic differences (different method names, types, conditions) and low token overlap (0.224), missing the high-level structural similarity in stream processing.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels clones based on structural similarity in I/O patterns, such as copying from input to output streams. Both methods share a common 'stream copy' skeleton with exception handling, which falls under Type-3/Type-4 clone categories.
- 共享行为: Both methods read from an input stream and write to an output stream in a loop.；Both handle exceptions and close streams in finally blocks.；Both use buffer sizes for reading/writing.
- 行为差异: Method A performs Base64 encoding; B does not.；Method B handles URL connections, caching, and conditional logic; A does not.；Method A returns a boolean; B returns an InputStream.；Method A writes to a specified output file; B writes to a cache file and returns a stream to it.
- 修正建议: Incorporate structural features like control flow graphs to detect common I/O patterns.；Add training examples that focus on stream copy operations with different sources/destinations.；Utilize data flow analysis to capture read-write cycles.

### case_id=3935 FN benchmark_preference_bias

- 方法: `doTransfer` vs `loadSourceCode`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request by copying headers and body from the incoming request to an outgoing connection.
- B 摘要: Loads a source code file from the classpath, reads it line by line, applies syntax highlighting, and returns as HTML.
- 静态失败原因: Static BERT models rely on token and API overlap, which is low (Jaccard 0.132). They fail to capture the broad functional category of 'reading input streams' that BCB sometimes accepts.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'stream reading' operations that read data from a source (URL or resource) and process it, valuing the structural similarity in stream handling despite different final purposes.
- 共享行为: Both open a URL or resource and read from an input stream.；Both handle exceptions with try-catch blocks.
- 行为差异: Function A is network I/O and HTTP forwarding; Function B is local file reading and text processing.；Function A writes to an output stream; Function B builds a string.；Function A sets request/response headers; Function B does syntax highlighting and HTML formatting.
- 修正建议: Use abstract representations of I/O operations and data flow.；Incorporate context about web application patterns to recognize both as serving content.

### case_id=3936 FN benchmark_preference_bias

- 方法: `sendExceptionToServer` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends exception details to an error server via HTTP POST, encoding parameters and reading response.
- B 摘要: Reads and prints the content of a URL via HTTP GET using a BufferedReader.
- 静态失败原因: The functions have low token Jaccard (0.1848), different method signatures, and different control flow (one has many append statements and exception handling, the other is a simple loop). The static model likely focused on syntactic and structural differences, missing the broader behavioral similarity of 'URL reading and printing' that BCB captures.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB often considers functions that perform similar I/O operations (e.g., reading from a URL and printing lines) as Type-3/Type-4 clones, even if the exact protocol or parameters differ. Both functions involve opening a URL, reading lines, and outputting them, which is a shared high-level behavior.
- 共享行为: Both open a URL connection；Both read lines of text from the connection；Both print lines to System.out
- 行为差异: A uses HTTP POST with encoded parameters; B uses HTTP GET without parameters；A handles IOException internally with try-catch; B declares throws IOException；A writes data to the connection before reading; B only reads；A checks for a 'success' response; B prints all lines without condition
- 修正建议: Incorporate high-level behavior descriptions using API usage patterns or call graphs；Use contrastive learning to recognize similar I/O patterns across different structures；Consider data flow to identify common operations like 'open URL, read lines, output'

### case_id=3937 FP lexical_or_api_overlap

- 方法: `main` vs `copyFileTo`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file, generates adapter classes, and packages them into a JAR.
- B 摘要: Copies the content of a source file to a destination file using a byte buffer.
- 静态失败原因: The static BERT model may have been misled by overlapping vocabulary related to file I/O (File, InputStream, OutputStream, read, write, close) and the presence of a while loop in B, which resembles the iteration in A. It likely lacks understanding of the overall application logic and treats API usage patterns as semantic equivalence.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotation considers Type-3 (near-miss) and Type-4 (semantic) clones only if functionality is similar. Here the functions have completely different purposes despite both handling files, so BCB correctly labels as non-clone.
- 共享行为: Both perform file I/O operations；Both use streams for reading/writing
- 行为差异: A is a complex program generation pipeline; B is a simple file copy.；A involves parsing, reflection, and JAR assembly; B only reads and writes bytes.；A has conditional debug mode and multiple file outputs; B is straightforward.；A uses custom classes like Parser, FactVisitor; B uses only standard Java I/O.
- 修正建议: Incorporate dataflow or control flow graphs to distinguish different operations on the same APIs.；Use program slicing to focus on high-level intent rather than low-level API sequences.；Improve training with more diverse non-clone pairs that share common libraries but differ in purpose.

### case_id=3938 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `doCopyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads and modifies a properties file for internationalization (i18n), updating or adding a key-value pair.
- B 摘要: Copies a file from source to destination using NIO channels, verifying size and optionally preserving file date.
- 静态失败原因: Static BERT correctly predicted 0 (no clone) because of low lexical overlap (Jaccard=0.106) and clearly different purposes; BCB label of 1 appears to be a benchmark mislabeling error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both methods involving file reading/writing, use of try-catch blocks, and similar API usage (File, streams), but this ignores the fundamentally different business logic and data processing.
- 共享行为: Both perform file I/O operations；Both use try-catch-finally or equivalent error handling；Both may create or overwrite files
- 行为差异: A reads/modifies properties files in text format; B copies binary files；A manipulates key-value pairs; B transfers bytes；A handles localization logic; B handles file size verification and date preservation；A uses Reader/Writer streams; B uses FileChannel
- 修正建议: Re-evaluate BCB label for this pair; it likely should be 0；Improve benchmark annotation guidelines to avoid labeling dissimilar file I/O functions as clones

### case_id=3939 FN lexical_or_api_overlap

- 方法: `doGet` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Serves a static file via HTTP GET request by reading the file and copying its content to the response output stream.
- B 摘要: Generates edited HTML pages from XML and other resources, applying transformations and writing output files to the filesystem.
- 静态失败原因: The static model likely relied on token similarity and structure, which are very low (Jaccard=0.06). It failed to recognize any underlying semantic commonality that BCB might perceive, possibly due to the model's inability to abstract to a very high-level functional category.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as clones due to shared high-level behavior of 'reading input and producing output' in a web context, or because both are methods that serve content. However, this is a stretch as the functionalities are vastly different.
- 共享行为: Both methods perform file I/O using FileInputStream；Both methods are part of a web-related application
- 行为差异: doGet is a simple servlet method handling a single GET request; buildSiteForEdit is a complex multi-step routine for site generation；doGet outputs to an HTTP response; buildSiteForEdit writes to the filesystem；buildSiteForEdit involves XML parsing, DOM operations, string replacement, and FTP; doGet does not；buildSiteForEdit has extensive error handling and debugging; doGet has minimal error handling
- 修正建议: Improve model's ability to capture high-level semantic roles beyond surface features；Incorporate domain knowledge about web application patterns；Use contrastive learning to separate such cases

### case_id=3940 FN partial_functionality

- 方法: `extractImage` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts an image from a file (or stdin), processes it with scaling and transforms, and writes the result to an output file.
- B 摘要: Retrieves a resource via URL, caches it locally with HTTP conditional fetching, and returns an InputStream.
- 静态失败原因: Low token overlap (Jaccard 0.1159) and different vocabulary/length lead to poor lexical matching; static BERT cannot capture the deep semantic similarity that BCB assumed.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled as clone due to similar high-level structure (input, processing, output with file I/O and error handling), even though domains differ, but it is unlikely given the vast difference in functionality.
- 共享行为: Both read from an input source and write to a file；Both handle IO exceptions with try-catch；Both use temporary files and close resources
- 行为差异: A processes image data; B downloads arbitrary resources；A writes using a custom writer; B caches and returns a stream；A handles stdin special case; B handles HTTP caching headers；A applies scaling and transforms; B does not
- 修正建议: Use a code representation that captures structural and data-flow patterns (e.g., AST or CFG).；Train with contrastive learning to distinguish subtle functional differences.；Include diverse negative mining to handle low lexical overlap.

### case_id=3941 FP lexical_or_api_overlap

- 方法: `writeFileType` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads URIs from a file, fetches each URL's content, classifies it based on ontology keywords, and writes results to an output file.
- B 摘要: Given a URL string, opens an HTTP connection, reads the first line of the response, and returns it as a string.
- 静态失败原因: Static BERT models may over-rely on common API tokens (URL, openConnection, BufferedReader, readLine) and miss the structural and semantic differences in control flow, data flow, and output behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have different I/O behavior and distinct purposes, despite sharing some API boilerplate. Token Jaccard is low (0.12766), indicating clear non-clone.
- 共享行为: Both open a URL connection using URL and openConnection.；Both read from the connection's input stream using BufferedReader.
- 行为差异: Function A writes classification results to a file; Function B returns a single line.；Function A processes multiple URIs from a file; Function B processes a single URL.；Function A reads multiple lines from each URL (up to 100); Function B reads only the first line.；Function A has complex conditional logic for ontology detection; Function B has no such logic.
- 修正建议: Incorporate data-flow analysis to track how inputs and outputs are used.；Use type information and method signatures to differentiate void and return methods.；Augment training with examples that share API usage but differ in purpose.

### case_id=3942 FN benchmark_preference_bias

- 方法: `doTransfer` vs `login`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request to a URL obtained from a parameter, copying headers and body, and returning the response.
- B 摘要: Performs a login to a service called LOLA by sending credentials and retrieving a session ID.
- 静态失败原因: Static BERT models rely heavily on token-level and syntactic similarity; the low Jaccard similarity (0.169) and different control flow caused the model to classify them as non-clones, missing the high-level functional similarity that BCB values.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely considers these as functional clones (Type-4) because both perform HTTP client operations, including establishing connections, writing to output streams, and reading responses, even though the specific tasks differ.
- 共享行为: Both involve making HTTP requests using URL/URLConnection.；Both write data to an output stream and read data from an input stream.；Both handle exceptions with try-catch blocks.
- 行为差异: Function A is a generic HTTP proxy that copies arbitrary requests; B is a specific login method.；Function A copies request headers and body to a new connection; B constructs form data with email and password.；Function A sends back the response from the target URL; B extracts a session ID from the response line.
- 修正建议: Train the model on a dataset that includes diverse Type-4 functional clones.；Incorporate structural or data-flow features to capture high-level intent.；Use contrastive learning to emphasize functional behavior over lexical overlap.

### case_id=3943 FN boilerplate_overlap

- 方法: `getDatasetsList` vs `addIDs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches and caches a list of dataset names from a provided URL by reading lines.
- B 摘要: Parses HTML from a metabolite database URL to extract IDs and set properties on a peak list row.
- 静态失败原因: Static BERT methods rely heavily on token overlap and structural patterns, and the low Jaccard similarity (0.20) indicates little lexical match. While both methods exhibit boilerplate patterns like URL/BufferedReader usage, the core logic differs significantly, leading the model to predict non-clone.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled this as clone because both methods share a common structural skeleton of URL fetching, line-by-line reading, and exception handling, which BCB may consider as partial functionality similarity.
- 共享行为: Both open a URL connection and read lines using BufferedReader；Both have exception handling for IOException；Both close the reader in a finally block
- 行为差异: Different URL formats and query parameters；Different parsing logic: line accumulation vs. HTML parsing with multiple branching；Different return types: List<String> vs. int；Different side effects: caching vs. modifying row properties
- 修正建议: Incorporate semantic understanding of the methods' core purpose beyond boilerplate；Use dataflow analysis to differentiate the actual transformations；Train with more diverse pairs where boilerplate overlaps but functionality differs

### case_id=3944 FP library_context_missing

- 方法: `addQDInformation` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `context_recovery_then_dynamic`；动态可解性: `low`；执行优先级: `medium`
- A 摘要: Updates project information from a QD info file, parsing lines starting with 'pg ' and 'pt ' and modifying internal state.
- B 摘要: Fetches a YouTube page, parses it to extract video_id and t parameters, and constructs a full screen URL.
- 静态失败原因: Static BERT models may have been misled by structural similarities such as both using URL, BufferedReader, while loop for reading, and parsing lines with conditionals. The methods have low lexical overlap, but some common patterns like opening a URL and reading lines could have caused the model to overestimate functional similarity.
- 静态 case study: 该类错误缺少关键上下文或需要深层语义，纯静态方法不可靠。
- 动态 case study: 动态执行价值较低：样本可能依赖库、框架、网络、GUI、数据库或项目上下文，需要先恢复环境或 mock 依赖。
- BCB 偏好解释: BCB would likely label this as not a clone because the functionalities are entirely different: one is about updating project information, the other about constructing a video URL. Although both involve reading from URLs and parsing lines, the core tasks and outputs are unrelated.
- 共享行为: Both methods open a URL or file and read lines using BufferedReader；Both parse each line to extract specific information；Both involve try-catch for IOExceptions
- 行为差异: Method A updates internal state for multiple projects; Method B returns a constructed URL string；Method A handles both local file and remote URL; Method B only remote URL；Method A parses lines starting with 'pg ' and 'pt '; Method B looks for 'fullscreenUrl' and then splits on '&'；Method A modifies _qdValue and _qdFileDate; Method B sets ytTitle and returns fullUrl
- 修正建议: Incorporate method name and type signature more heavily；Use data flow analysis to track how variables are used；Add more examples of methods with similar reading patterns but different purposes as negative samples

### case_id=3945 FN partial_functionality

- 方法: `copyResource` vs `download`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file path to a destination file using byte-by-byte stream copy, throwing exception on failure.
- B 摘要: Downloads a resource from classpath to a user-selected file path using IOUtils.copy, with error handling via dialog.
- 静态失败原因: Low token Jaccard similarity and syntactic differences in method names, control flow, and exception handling led the model to miss the functional equivalence.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers them Type-3 clones because the core I/O copy functionality is the same, and differences are in peripheral aspects like source/destination selection and error handling.
- 共享行为: Both copy an input stream to an output stream, eventually writing to a file.；Both close streams after copy.
- 行为差异: Source selection: A uses URL/File, B uses classpath.；Destination selection: A fixed, B via dialog.；Error handling: A throws, B catches and shows dialog.；Copying method: A uses loop, B uses IOUtils.copy.
- 修正建议: Incorporate dataflow analysis to detect stream copying patterns.；Augment training with diverse Type-3 examples having low lexical overlap.；Use AST-based matching to capture structural similarities.

### case_id=3946 FP lexical_or_api_overlap

- 方法: `getVersion` vs `GetResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches version string from a hardcoded URL via HTTP, returning the last line.
- B 摘要: Fetches HTTP GET response from a given URL, concatenating all lines into a string (with a bug causing leading 'null').
- 静态失败原因: The static model likely overestimated similarity due to high lexical overlap ('URL', 'openConnection', 'BufferedReader', 'readLine', 'InputStreamReader', 'return') and similar structure of URL reading boilerplate. It may have missed the semantic differences in input parameterization and output construction (overwrite vs concatenate with bug).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels pairs as clones if they perform the same high-level task. Here, both fetch HTTP content, but one is version-specific and non-parameterized, the other is generic. The bug in B and the different return semantics likely lead BCB to consider them non-clones because the functionality is not truly equivalent.
- 共享行为: Both open a URL connection and read the response using BufferedReader.；Both return a string derived from the HTTP response.；Both return null on exception.
- 行为差异: Function A uses a hardcoded URL, function B accepts URL as parameter.；Function A returns only the last line, function B concatenates all lines with an initial 'null' bug.；Function A prints debug output, function B does not.；Function A uses generic URLConnection, function B specifically uses HttpURLConnection with GET method and checks response code.
- 修正建议: Improve model to capture input/output parameter differences.；Add attention to variable initialization and data flow (e.g., content starts null vs version overwritten).；Consider that hardcoded URLs vs parameterized URLs indicate different functional scope.

### case_id=3947 FN partial_functionality

- 方法: `read` vs `CheckUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads content from a file or URL into an internal buffer, returning a status code.
- B 摘要: Checks a URL by opening an HTTP connection, reading the first line of the response, and returning it as a string.
- 静态失败原因: Static BERT/GraphCodeBERT models likely focused on structural differences such as different return types, method signatures, and the presence of a file reading branch in Code A. The low token overlap (0.256) and the missing implementation of the called 'read' method in Code A reduce structural similarity, causing the model to classify them as non-clones.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as clones because both involve opening a URL and reading input data, which represents a similar high-level task (Type-4 functional similarity). The inclusion of file reading in Code A might be overlooked if the URL reading portion is seen as the core functionality.
- 共享行为: Both open a URL using the java.net.URL class and read from its input stream.
- 行为差异: Code A can also read from a local file if the input does not contain '://', while Code B only handles HTTP URLs.；Code A reads the entire stream (via a call to another read method), while Code B reads only the first line.；Code A returns an integer status code, while Code B returns a string (the first line of the response).；Code A is an instance method and catches IOException only, while Code B is static and catches all Exceptions with stack trace printing.
- 修正建议: Improve handling of partial functionality similarity by focusing on subgraph matching for common URL reading logic.；Incorporate call graph analysis to understand the behavior of invisible methods like 'read(in)'.；Use data-flow or abstract interpretation to recognize that both functions consume a string and produce a result based on network I/O.

### case_id=3948 FN partial_functionality

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file by reading from an input stream and writing to an output stream using a fixed-size buffer.
- B 摘要: Builds a website for editing by reading XML files, transforming them via XSLT, and writing the result to multiple output files.
- 静态失败原因: Static BERT methods like GraphCodeBERT rely on token embeddings and attention. The low lexical overlap (Jaccard 0.082) and vastly different lengths make them appear dissimilar. The shared I/O pattern is a small part of function B, so the model likely overlooked it and judged them as non-clones based on overall structure.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones because both functions contain a common code pattern of reading from a file into a buffer and writing to another file, which could be considered a Type-3 clone if a detector focused on that shared segment. However, the overall functionality is very different.
- 共享行为: Both perform file I/O with buffered reading and writing.；Both contain try-catch-finally blocks that handle IOException and close streams.
- 行为差异: Function A is a simple generic file copy utility; Function B is a complex site builder with XML transformation, string manipulation, and multi-file processing.；Function B uses additional libraries (e.g., Transformer, FileSystem) and has many parameters.；Function A copies a single file; Function B processes a collection of pages and writes transformed content.
- 修正建议: Improve the model to recognize that a common sub-routine does not constitute a clone if the overall functionality differs significantly.；Consider using decomposition or graph-based representations to capture functional equivalence beyond lexical overlap.；Enhance training data with examples of partial functionality clones (Type-4) to teach the model to distinguish between trivial overlap and true semantic similarity.

### case_id=3949 FN benchmark_preference_bias

- 方法: `doVersionCheck` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads a version file from a URL, parses lines for version and build info, and compares with the current build to notify of updates.
- B 摘要: Reads a configuration file for Tibetan/Sanskrit character mappings, tokenizes multiple static strings into sets, and populates lookup tables from a delimited file with multiple columns.
- 静态失败原因: The static model correctly predicted non-clone because the token overlap is low (0.104) and the code structures are quite different; it did not fail but rather the BCB label is likely an outlier from overly lenient annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to a very broad interpretation of 'file reading and parsing' or 'configuration data loading', overlooking the vastly different domain logic and output structures.
- 共享行为: Both read lines from an input source (URL stream or file) and process textual data.；Both use try-catch blocks to handle I/O exceptions.；Both utilize helper methods (e.g., GUIUtilities.message vs. ThdlDebug.noteIffyCode) for user feedback or error logging.
- 行为差异: Function A performs a single specific task: version check via URL; Function B initializes multiple sets and parses a complex multi-column data file.；Function A reads only two specific line prefixes (.version, .build); Function B reads many lines with various delimiters and builds mappings.；Function A compares build numbers and shows messages; Function B populates hash tables and sets for later use in a character encoding system.；Function A has a simple loop reading lines; Function B has nested loops and switch-case for column indices.
- 修正建议: Refine BCB annotation guidelines to emphasize semantic equivalence rather than superficial I/O patterns.；Re-evaluate this pair with expert annotators to confirm non-clone status.；Increase token-level similarity thresholds where appropriate.

### case_id=3950 FP boilerplate_overlap

- 方法: `getJSONData` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches JSON data from a given URL using HttpClient, parses it into JSONObject.
- B 摘要: Fetches a YouTube video URL by parsing the response of a given YouTube page URL to extract video_id and t parameters.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overestimated similarity due to shared boilerplate code (e.g., try-catch, BufferedReader, URL connection setup). The model may not have captured the semantic difference in the high-level goal (generic JSON fetch vs. specific YouTube URL extraction).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled this as non-clone (0) because the functions have different purposes and low token similarity. Even though both involve HTTP requests and stream reading, the core functionality and output are distinct.
- 共享行为: Both perform HTTP GET requests to retrieve data from a URL.；Both read the response stream line by line using BufferedReader.；Both handle exceptions with try-catch and print stack traces.
- 行为差异: Method A is generic JSON retrieval; Method B is specific to YouTube URL parsing.；Method A uses Apache HttpClient; Method B uses URLConnection.；Method A returns a JSONObject; Method B returns a String.；Method B has additional logic to search for a specific substring and parse parameters.
- 修正建议: Enhance training data with more diverse examples showing that boilerplate similarity does not imply semantic equivalence.；Incorporate dataflow or control flow analysis to distinguish different operations after stream reading.；Use contrastive learning to penalize pairs with high lexical overlap but different domain-specific logic.

### case_id=3951 FN benchmark_preference_bias

- 方法: `doVersionCheck` vs `runScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a version file from a URL, reads lines, extracts devel and stable build versions, and calls a version check method.
- B 摘要: Downloads a script file from a URL, reads its bytes into a string, and returns that string or 'error!' on exception.
- 静态失败原因: Static BERT models rely on lexical and syntactic similarity (low Jaccard 0.23) and fail to recognize the common structural pattern of URL fetching and stream reading.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labels this as a Type-4 semantic clone because both functions implement the high-level task of downloading content from a URL and processing it, even though the specific processing differs.
- 共享行为: Both open a URL and read from an InputStream；Both handle exceptions during reading；Both use URL class to create the URL
- 行为差异: A reads line-by-line, B reads byte-by-byte；A parses specific line prefixes, B concatenates all data；A includes UI cursor changes and error dialog, B does not；A calls another method, B returns string
- 修正建议: Use graph-based code representation to capture data-flow and control-flow patterns；Incorporate functional similarity measures like API call sequences；Train on Type-4 clone examples to recognize semantic patterns

### case_id=3952 FN partial_functionality

- 方法: `runScript` vs `getWebByUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from the codebase URL and returns its content as a string, handling exceptions.
- B 摘要: Fetches a web page from a given URL, writes its content to a file, logs progress, and recursively processes links within depth limits.
- 静态失败原因: Static BERT models likely overemphasized the overlapping tokens (URL, InputStream, try-catch) and structural similarity, missing the divergent high-level purpose.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones based on the shared pattern of opening a URL and reading stream data, despite vastly different overall functionality.
- 共享行为: Both open a URL connection and read from an input stream.
- 行为差异: runScript reads character by character and returns a string; getWebByUrl reads line by line, writes to file, logs, and recursively processes links.
- 修正建议: Incorporate dataflow analysis to distinguish simple I/O from complex workflows.；Use longer-range context or functional summarization to capture overall intent.

### case_id=3953 FP lexical_or_api_overlap

- 方法: `read` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads camera log from URL, parses each line into CameraLogRecord, adds to list, sorts, logs.
- B 摘要: Reads tile data from URL as GeoJSON, parses into vector tiles, extracts geometries, adds to data source.
- 静态失败原因: The model overemphasized lexical and API overlaps like 'URL', 'BufferedReader', 'in.readLine()', 'IOException', and 'close()', missing the different data processing logic and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled non-clone because despite shared boilerplate of reading from URL, the core functionality (parsing and output) is entirely different, and they are not considered semantically equivalent or partial clones.
- 共享行为: Open a URL and read lines using BufferedReader；Handle IOException；Close the stream；Use logging
- 行为差异: Function A parses lines into CameraLogRecord objects; Function B concatenates lines into a GeoJSON string；Function A sorts records; Function B processes tiles and geometries；Function B has concurrency locking and URL protocol handling (file vs http)；Different output: A stores in list; B adds to data source
- 修正建议: Incorporate data flow analysis to track how read data is processed and used；Train on more diverse pairs with similar boilerplate but different semantics；Use contrastive learning to distinguish between structural overlap and semantic equivalence

### case_id=3954 FP boilerplate_overlap

- 方法: `hashKey` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes MD5 hash of a string, with fallback to Java hashCode.
- B 摘要: Handles HTTP request, validates session, and performs classification using XML/URL operations.
- 静态失败原因: Static models like GraphCodeBERT may rely on superficial lexical patterns; both methods share common boilerplate (try-catch, String operations) and control flow, leading to a false positive despite low Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because they have no functional similarity; BCB typically requires some level of functional overlap even for Type-4 partial clones.
- 共享行为: Both use try-catch blocks for exception handling.
- 行为差异: Function A is a simple hash utility; Function B is a complex web action handler.；Function A returns a String; Function B returns an ActionForward.；Function A has no side effects; Function B modifies session and interacts with network.
- 修正建议: Improve model to capture semantic intent rather than superficial patterns.；Include more diverse negative examples with boilerplate overlap.；Use dataflow or control-flow features to distinguish side effects and high-level purpose.

### case_id=3955 FP partial_functionality

- 方法: `readTwitterFead` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a Twitter timeline JSON via HTTP GET without authentication using HttpClient.
- B 摘要: Performs an authenticated HTTP GET request using HttpURLConnection, updating instance state.
- 静态失败原因: Static BERT models may have over-relied on overlapping tokens like 'HttpGet', 'BufferedReader', 'append', and the similar try-catch-read loop structure, missing the critical distinction in authentication and method purpose.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotations typically require substantial functional similarity. Despite both performing HTTP GET, the significant differences in authentication, context, and error handling likely led BCB to label as non-clone.
- 共享行为: Perform HTTP GET request；Read response line by line and append to string builder；Use Java I/O to read input stream
- 行为差异: Different HTTP libraries (Apache HttpClient vs HttpURLConnection)；Function A does not include authentication, Function B does；Function A returns the built string directly, Function B modifies instance variables；Function A appends lines without newline, Function B appends with newline
- 修正建议: Incorporate data flow analysis to track authentication and URL differences；Consider method signature and class context；Use finer-grained comparison of HTTP connection setup

### case_id=3956 FN benchmark_preference_bias

- 方法: `testNetworkHTTP` vs `init`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends device information (IMEI, phone number, message, file content, installed apps) via HTTP requests to remote servers.
- B 摘要: Reads a registry file from classpath to discover and load controller classes.
- 静态失败原因: The static model likely failed to recognize this as a clone due to low token Jaccard (0.202) and significant differences in API usage (HttpURLConnection vs ClassLoader.getResources), method names, and context. The model's representation may not capture abstract patterns like 'reading from URLs' without strong lexical overlap.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider this a clone because both functions implement the common pattern of reading lines from URLs via BufferedReader, which is considered a shared functionality. The annotation guidelines often accept partial functionality similarity, especially when the core operation (reading URL content line by line) is structurally similar.
- 共享行为: Both use BufferedReader to read lines from URLs in a while loop；Both catch IOException；Both have try-catch-finally structure
- 行为差异: Function A sends data to multiple remote servers; Function B loads classes locally from classpath；Function A uses HttpURLConnection; Function B uses classLoader.getResources；Function A includes URL parameter encoding; Function B does not；Function A performs multiple HTTP connections; Function B reads multiple URLs from enumeration
- 修正建议: Incorporate higher-level semantic features such as recognizing common I/O patterns；Use dataflow analysis to capture similar operations on input streams；Train with more diverse Type-4 clone examples to capture partial functionality similarity

### case_id=3957 FN benchmark_preference_bias

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using a byte buffer and handling exceptions.
- B 摘要: Builds a website for editing by processing XML configuration, applying XSLT transformations, performing string replacements, and writing multiple output files.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token overlap and method name similarity, both of which are extremely low here. The model correctly identified them as different because the lexical and structural patterns diverge significantly.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this pair as clone due to very high-level similarity (both involve file I/O), but the annotation is likely an error because the core functionality is completely different.
- 共享行为: Both perform file read operations using FileInputStream.；Both involve writing data to files.；Both catch IOExceptions.
- 行为差异: Function A is a straightforward file copy; Function B is a complex site-generation process with XML parsing, XSLT, and string manipulation.；Function A copies byte-for-byte; Function B transforms content before writing.；Function A handles only two exceptions; Function B handles multiple exception types including DOMException, TransformerException, etc.；Function A is static and generic; Function B is an instance method that depends on many parameters and internal state.
- 修正建议: Ensure BCB annotations consistently require substantial functional similarity, not just shared low-level operations.；Use data filtering to remove pairs with trivial or accidental I/O overlap.；Incorporate structural and data-flow analysis to distinguish simple copy from complex transformation.

### case_id=3958 FP lexical_or_api_overlap

- 方法: `retrieveQ` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves text content from a URL as a string, printing the HTTP response message to stderr.
- B 摘要: Downloads a file from a URL to a local destination with progress reporting via a UI component.
- 静态失败原因: Static BERT models may rely on token overlap (e.g., URL, openConnection, InputStream) and common boilerplate for URL reading, missing the different control flows and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions have different return types and side effects (string retrieval vs file download with progress), which are considered distinct functionalities.
- 共享行为: Both open a URL connection；Both read from the InputStream
- 行为差异: A returns a string of the content; B saves the content to a file and returns a boolean；A reads line by line; B reads in fixed-size buffers；A prints response message to stderr; B updates a progress bar；A does not handle file creation; B creates/deletes files
- 修正建议: Incorporate structural differencing (return type, file I/O vs string building)；Use data-flow analysis to capture output destination differences

### case_id=3959 FP lexical_or_api_overlap

- 方法: `read` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a camera log from a URL, parses each line into CameraLogRecord objects, catches parse errors, sorts records, and logs progress.
- B 摘要: Checks for software upgrades by querying a database, fetching license info from a URL, parsing XML-like data, and updating UI components.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on lexical overlap (BufferedReader, URL, while loop) and missed the semantic divergence in higher-level logic, data structures, and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones for functions with entirely different domain logic despite surface API overlap. These functions have no shared functionality beyond basic I/O patterns.
- 共享行为: Both use BufferedReader to read lines from a URL stream；Both use while loops to process input line by line；Both perform logging at info level
- 行为差异: Function A parses camera log records; Function B processes upgrade license data；Function A sorts records; Function B manipulates database and UI；Function A is instance method; Function B is static method with Event parameter
- 修正建议: Improve model to weigh structural flow and domain-specific operations more heavily；Add contrastive training on pairs with high API overlap but different semantics；Incorporate data flow analysis to distinguish variable usage patterns

### case_id=3960 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Event handler that processes GUI commands to set preferences for Graphviz, ImageMagick, and other settings.
- B 摘要: Main method that iterates over jar files, reads metadata, and writes license info to a file.
- 静态失败原因: The static model may have been misled by the presence of common API calls like FileOutputStream, File, loops, and string writes, causing a false positive due to lexical overlap despite different contexts.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because functions have entirely different purposes, one is GUI-related and the other is file processing, with no shared functionality beyond trivial use of Java APIs.
- 共享行为: Both use file I/O operations；Both iterate over some items (commands vs files)；Both write string data (to text fields vs file stream)
- 行为差异: Function A is a GUI event handler; B is a standalone main method；A handles user interaction via JFileChooser; B processes command-line arguments and files；A updates UI components and stores preferences; B writes to a static output file；A has many conditional branches for different commands; B has a loop over files
- 修正建议: Improve the model's ability to distinguish between different program contexts (e.g., GUI vs. batch processing)；Incorporate more structural features like method signature, return type, and control flow patterns；Train with more emphasis on long-range semantic dependencies and data flow

### case_id=3961 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFromFileToFileUsingNIO`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale by copying an English file if the locale file does not exist, then reads and updates a specific message key-value pair.
- B 摘要: Copies a source file to a destination file using NIO FileChannels.
- 静态失败原因: Static BERT models rely on token-level similarity and structural cues; the two functions have very different method names, APIs, and control flow. The token Jaccard is low (0.135), and the model failed to recognize the partial file copy functionality in code_a that matches code_b.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers this a clone under Type-4 (functional similarity) because code_a contains a file copy subtask similar to code_b, even though the overall purposes differ.
- 共享行为: Both read from and write to files；Both perform file copy operations (code_a copies a file if missing, code_b is a file copy)
- 行为差异: Code_a's copy is character-based using FileReader/FileWriter; Code_b uses NIO FileChannel.transferTo；Code_a additionally modifies properties file content after copy; Code_b only copies；Code_a handles missing locale file by creating it; Code_b assumes input file exists；Code_a writes back to the same file after modification; Code_b writes to a different output file
- 修正建议: Use graph-based models that capture dataflow and subgraph similarity；Incorporate long-range dependency modeling to identify shared subtasks across functions；Train with partial positive examples where only a sub-function matches

### case_id=3962 FN benchmark_preference_bias

- 方法: `getFile` vs `extractFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies an XML attribute, and saves to a temporary location, returning the file path.
- B 摘要: Copies the contents of an input file to an output file using a byte buffer.
- 静态失败原因: The static model correctly identified non-clone due to low token overlap and distinct control flow, but the benchmark's BCB label considers it a false negative, possibly because the model lacks the domain-specific reasoning to appreciate the annotator's broad view.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to a broad interpretation of file-transfer utilities, overlooking the distinct high-level semantics (WSDL download/modification vs. raw file copy). The low token similarity and different method signatures argue against clone status even under relaxed criteria.
- 共享行为: Both perform file I/O operations (reading and writing files).
- 行为差异: A downloads from a URL; B reads a local file.；A modifies XML content; B just copies bytes without transformation.；A returns a file location; B returns void.；A uses NIO channels and handles multiple exception types; B uses simple byte buffer and only ZipException/IOException.
- 修正建议: Re-evaluate the BCB annotation for this pair; consider if the functions truly share enough behavior to be clones.；Improve static detection by incorporating higher-level semantic features like file I/O patterns, but be cautious not to overgeneralize.

### case_id=3963 FN partial_functionality

- 方法: `main` vs `getZipAsFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to the current directory.
- B 摘要: Saves a zip file from a DigitalObject's content to a temporary directory and returns the file.
- 静态失败原因: Low token overlap (0.082), different method names ('main' vs 'getZipAsFile'), and distinct APIs (ZipInputStream vs IOUtils.copyLarge) led static models to overlook the conceptual similarity of zip file handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as clones because they are zip file utility functions that perform I/O on zip archives, falling under Type-3/Type-4 similarity despite different specific operations.
- 共享行为: Both handle zip files；Both read from an input stream and write to files；Both perform file I/O operations
- 行为差异: A extracts multiple entries; B saves a single file；A uses URL as source; B uses DigitalObject；A does not create directories; B creates temporary folder；A outputs to current directory; B outputs to temporary folder
- 修正建议: Incorporate API call sequence similarity；Use dependency graph or data flow to capture I/O patterns；Add training data with diverse zip-related functions

### case_id=3964 FP boilerplate_overlap

- 方法: `readData` vs `transformSingleFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads and parses comma-separated strings into multiple sets and maps for Tibetan transliteration.
- B 摘要: Converts an X3D file to X3DV format and compresses it to a gzip file.
- 静态失败原因: The model likely overgeneralized from common boilerplate patterns (try-catch, loops, string operations) and failed to capture the distinct semantic contexts.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they perform completely different tasks with no shared functionality or code reuse.
- 行为差异: Return type: void vs String；Purpose: data initialization vs file compression；Domain: linguistic transliteration vs 3D graphics；Use of class-level variables vs local variables
- 修正建议: Enhance model to weigh API calls and data flow more heavily than syntactic patterns.；Include more negative examples with similar boilerplate but different semantics.；Incorporate type and output information in embeddings.

### case_id=3965 FN partial_functionality

- 方法: `readGeoParserResult` vs `getEncoding`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses a geo-parser result by sending an XML request to a URL and extracting place names and gazetteer IDs.
- B 摘要: Detects the character encoding from an HTTP response by checking headers and content.
- 静态失败原因: Static BERT models like GraphCodeBERT are sensitive to token overlap and structural patterns. The low Jaccard similarity and different variable/function names led to a low similarity score. The model failed to recognize the underlying common behavior of reading from a URL and parsing response lines.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotation guidelines consider Type-4 clones as functionally similar even if not identical. Both methods perform network I/O and data extraction, which is sufficient for a broad clone label.
- 共享行为: Both open a URL connection and read lines from the input stream.
- 行为差异: Method A builds an XML request and parses XML to extract place names and IDs; Method B extracts charset from HTTP headers and content.；Method A has retry logic; Method B does not.；Method A uses XML parsing; Method B uses string matching.
- 修正建议: Train on more diverse clone pairs that share partial functionality but differ in specific domain logic.；Use data flow analysis to detect common patterns like URLConnection usage and line reading loops.

### case_id=3966 FN partial_functionality

- 方法: `copyFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from one location to another using FileChannel.
- B 摘要: Retrieves a resource as an InputStream with caching and HTTP conditional GET support.
- 静态失败原因: Low token Jaccard (0.127) and long code B with complex logic likely cause the static model to miss the partial I/O pattern overlap, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a clone due to the shared pattern of opening, reading/writing, and closing file streams, which could be seen as partial functionality (Type-3/4) in broad clone detection.
- 共享行为: Both involve file I/O operations；Both use FileInputStream/FileOutputStream；Both close streams/channels in finally blocks
- 行为差异: Function A copies a file; Function B retrieves a resource with caching logic；Function A uses FileChannel.transferTo; Function B uses BufferedStreams and URLConnection；Function B has HTTP conditional GET, caching, and directory creation
- 修正建议: Improve handling of long-range dependencies by leveraging hierarchical models or AST-based representations；Incorporate data-flow analysis to capture I/O stream usage patterns；Use contrastive learning to better distinguish partial functionality clones from non-clones

### case_id=3967 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for software version by reading a URL and parsing .version and .build lines, then comparing build numbers.
- B 摘要: Constructs a full YouTube video URL by reading a URL, parsing the 'fullscreenUrl' line, and extracting video_id, t, and title.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized lexical and API-level similarities (both use URL, BufferedReader, while loop, line parsing, exception handling) and missed the different semantic contexts and data usage (build comparison vs video URL construction).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the two methods belong to different domains (version check vs YouTube video URL retrieval) with different output types and UI interactions, despite a similar code structure of reading a URL and parsing lines.
- 共享行为: Both open a URL and read line by line using BufferedReader.；Both parse lines to extract specific information using conditional checks.；Both handle IO exceptions.
- 行为差异: A uses a View for UI (show/hide wait cursor, messages), B uses progressDown and prints debug info.；A extracts version and build strings; B extracts video_id, t, title to construct a URL.；A returns void (void method), B returns a String (fullUrl).；A compares build numbers; B does not compare but builds a new URL.
- 修正建议: Incorporate data flow analysis to track how parsed data is used (e.g., build comparison vs URL construction).；Use contrastive learning with more negative examples that share API calls but differ in intent.；Include broader context (e.g., class name, method name, surrounding code) to distinguish domains.

### case_id=3968 FP boilerplate_overlap

- 方法: `setBundleInfoName` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL and updates bundle names in a list based on key=value pairs.
- B 摘要: Reads a hardcoded URL to retrieve a version string.
- 静态失败原因: Static BERT/GraphCodeBERT may overemphasize overlapping API tokens (URL, BufferedReader, readLine) and ignore the differing semantics and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically treats clones as functionally equivalent or similar, but these functions have different purposes and data processing logic, so they are likely labeled non-clones.
- 共享行为: Both open a URL and read lines using BufferedReader；Both handle IOException with try-catch
- 行为差异: setBundleInfoName takes parameters and updates a list; getVersion takes no arguments and returns a string；setBundleInfoName parses key=value pairs; getVersion simply takes the last line as version；Different URL sources (parameter vs hardcoded)；Different return types (boolean vs String)
- 修正建议: Incorporate data flow analysis to capture how read data is used；Use control flow graphs to differentiate between structural boilerplate and actual logic

### case_id=3969 FP lexical_or_api_overlap

- 方法: `GetResponse` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches HTTP GET response as a concatenated string.
- B 摘要: Parses a YouTube page to extract video ID and timestamp, then constructs a download URL.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by the high token overlap (0.265 Jaccard) and common API usage (URL, openConnection, BufferedReader), ignoring the divergent control flow and domain-specific logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely consider these non-clones because the high-level functionality differs: one is a generic HTTP response fetcher, the other is a YouTube URL extractor. Despite shared low-level I/O patterns, the overall purpose and output are different.
- 共享行为: Both open an HTTP URL connection and read the response line by line using BufferedReader.
- 行为差异: Method A returns raw HTTP response content; Method B extracts specific parameters and constructs a new URL.；Method A is generic; Method B is specific to YouTube video metadata.；Method B updates a progress indicator and prints debug information; Method A does not.
- 修正建议: Incorporate data-flow analysis to distinguish different variable manipulations.；Add domain-specific context awareness.；Use contrastive training to differentiate similar API sequences with different intents.

### case_id=3970 FN benchmark_preference_bias

- 方法: `resolvePlugins` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.75`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads a plugins.xml file from a URL if not already cached locally, then delegates to another method.
- B 摘要: Builds a site for editing by reading configuration, processing pages with XML transformations, and writing output files.
- 静态失败原因: Static BERT likely relied on low lexical overlap (token Jaccard 0.054) and large structural differences, correctly predicting non-clone, while BCB label may be erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone based on both performing file downloading/reading and delegating to another method, but the significant difference in complexity and purpose makes this uncertain.
- 共享行为: Both perform file I/O operations.；Both have try-catch exception handling.
- 行为差异: Function A is short and focused on a single file download; Function B is long and complex with multiple processing steps.；Function A no parameters; Function B takes 11 parameters.；Function B involves XML parsing, character buffer manipulation, and multiple loops; Function A does not.；Function B uses FTP and regex operations; Function A only uses URL/IO streams.
- 修正建议: Review BCB annotations for consistency in Type-4 classification.；Include more negative examples with low token overlap but similar file I/O patterns.

### case_id=3971 FN benchmark_preference_bias

- 方法: `populateResources` vs `runScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Loads template files and images from predefined resource paths and saves them as data objects.
- B 摘要: Reads a script file from a URL relative to the codebase and returns its content as a string.
- 静态失败原因: The static model likely failed because it correctly identified the low token overlap (0.14) and diverging control flow and data dependencies, leading to a non-clone prediction. However, BCB's liberal labeling caused this false negative from the model's perspective.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'resource loading' utilities, focusing on the common pattern of URL stream reading and ignoring differences in purpose and output handling, thus labeling them as a Type-4 clone.
- 共享行为: Both open a URL stream and read data from it.；Both use try-catch for IO exceptions.
- 行为差异: populateResources saves data to persistent objects (Resource, Image, Property), while runScript only returns the data.；populateResources processes multiple files and images, runScript handles a single script.；populateResources has specific logic for filtering file types and building strings, runScript reads bytes one by one.
- 修正建议: Adjust the model's threshold to be more permissive for functions with shared I/O patterns.；Incorporate high-level semantic features like 'reading from URL' or 'loading resources' to align with BCB preferences.

### case_id=3972 FP dataflow_blindspot

- 方法: `run` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_with_trace`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses an XML document to generate a Firefox addon ZIP package containing manifest, install, JS, XUL, and icon files.
- B 摘要: Handles action commands in a settings dialog to configure file paths, look and feel, font size, and other preferences for a genealogy application.
- 静态失败原因: The model likely failed due to dataflow blindspot, focusing on superficial similarities (e.g., presence of try-catch, null checks, or API calls like 'getResourceAsStream') but missing the distinct semantic contexts and data flows.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 dataflow_trace_and_outputs。
- BCB 偏好解释: BCB typically annotates Type-3/Type-4 clones only when there is significant shared functionality or structural similarity; here the functions solve entirely different tasks with no common sub-task.
- 共享行为: Both involve some form of input processing (Reader vs ActionEvent)
- 行为差异: Different overall purpose: generating a Firefox addon vs configuring a settings dialog；Different I/O: ZipOutputStream vs JFileChooser and property storage；Different control flow: linear vs heavily conditional；Different domain-specific operations
- 修正建议: Incorporate dataflow analysis or structural abstraction (e.g., AST-based features) to distinguish different task types；Use contrastive learning to force models to focus on semantic differences；Include domain-specific or task-level context

### case_id=3973 FN partial_functionality

- 方法: `execute` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Method that performs bytecode injection on class files by reading, analyzing, and writing modified classes.
- B 摘要: Method that modifies a properties file by reading, updating or adding a key-value pair, and writing back.
- 静态失败原因: Static BERT models like GraphCodeBERT often rely on lexical and structural similarity. The token Jaccard is low (0.14), but the shared API tokens (e.g., File, InputStream, FileWriter) may cause confusion. However, the methods have very different control flow and processing logic. The model likely failed to recognize the clone because the code is too dissimilar in terms of API usage and structure, and the shared pattern is not captured by static analysis. The model may have focused on the specific library classes (ASM vs Properties) and deemed them different, missing the high-level semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both methods follow a common template: open a resource, iterate over its contents, apply transformation, and write back. This high-level read-modify-write pattern is considered similar behavior, even though the domain and specific operations differ.
- 共享行为: Both methods read from an input source, process the content, and write to an output source.；Both use try-catch for exception handling and close streams.
- 行为差异: Method A modifies Java bytecode using ClassReader/ClassWriter, while Method B modifies properties file content by parsing lines.；Method A processes multiple class files and aggregates sizes, while Method B processes a single properties file to add/update a key-value pair.
- 修正建议: Incorporate program analysis to detect read-write file modification patterns.；Augment training data with more cross-domain examples of file modification tasks.；Use dataflow-based features to capture the common input-process-output structure.

### case_id=3974 FN partial_functionality

- 方法: `copyResource` vs `encodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copy a resource (URL or file) to a destination file using raw byte copying.
- B 摘要: Encode a source file using Base64 and write the encoded content to an output file, with exception handling and return status.
- 静态失败原因: Static BERT models like GraphCodeBERT often rely on token-level features and may miss the high-level structural similarity, especially when the token overlap is low (0.19697) and method names differ significantly.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones due to the overall structural similarity of copying data from input to output streams, despite the encoding difference, as they share the core pattern of I/O streaming and bulk data transfer.
- 共享行为: Both copy data from an input source to an output file using streams.；Both use a while loop to read and write bytes.；Both involve closing input and output streams.
- 行为差异: Function A performs raw byte copying; Function B applies Base64 encoding during the copy.；Function A uses a single-byte read/write loop; Function B uses a buffered read with a larger buffer.；Function A throws an exception on failure; Function B returns a boolean and prints stack traces.；Function A reads from a URL or local file; Function B always reads from a local file.
- 修正建议: Enhance model to recognize common I/O patterns (stream copy) as functional similarity even when encoding steps differ.；Incorporate structural or dataflow analysis to capture the read-write loop pattern.；Consider lifting method-level semantics from comments or surrounding context.

### case_id=3975 FN benchmark_preference_bias

- 方法: `getResourceAsStream` vs `bootKernel`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads a resource from a URL, caches it locally, and returns an InputStream after handling HTTP and file I/O.
- B 摘要: Loads a kernel configuration from an Android asset, copies assets to sdcard, and boots a kernel class.
- 静态失败原因: The static model relied on low token overlap (0.069) and syntactic differences, failing to recognize the broad functional similarity that BCB considers.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may view both as implementing a general pattern of loading external resources and performing file I/O, despite different contexts and outcomes, leading to a Type-4 clone label.
- 共享行为: Both read from an input stream；Both write to files；Both handle exceptions with try-catch
- 行为差异: A deals with HTTP URL resources, B deals with Android assets；A returns an InputStream, B returns void；A caches resources, B does not cache；B instantiates and boots a kernel class, A does not
- 修正建议: Incorporate high-level functional intent via semantic role labeling；Use dataflow or program-dependence graphs to capture common I/O patterns

### case_id=3976 FP lexical_or_api_overlap

- 方法: `setMembers` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads HTML from a Trac new ticket page and extracts component and priority options using regex, setting static arrays.
- B 摘要: Reads tab-separated data from a URL and populates an input vector with concatenated id and description.
- 静态失败原因: The static BERT model likely overemphasized overlapping API tokens (URL, openStream, while loop, MalformedURLException) and structural similarity, missing the critical semantic difference in data format extraction and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the functions perform distinct tasks: one is specifically for Trac ticket metadata extraction, the other for generic TSV reading. The superficial structural similarity (URL I/O, line parsing) is insufficient for BCB's functional similarity criteria.
- 共享行为: Both open a URL and read lines from the response；Both parse each line to extract specific data；Both store extracted data into collections
- 行为差异: Different input parameters: none vs. source string and vector；Different data format: HTML select options vs. tab-separated values；Different output: sets static fields vs. populates passed vector；Different error handling: prints messages vs. silent catch with finally close
- 修正建议: Incorporate dataflow analysis to track how parsed variables are used；Add type-aware embeddings for method parameters and return types；Train on contrastive examples with high lexical overlap but different semantics

### case_id=3977 FN partial_functionality

- 方法: `copyResource` vs `encodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copy a resource (URL or file) to a destination file without transformation.
- B 摘要: Read a file, Base64 encode it, and write to an output file.
- 静态失败原因: The static BERT/GraphCodeBERT likely focused on low token overlap and failed to capture the high-level structural similarity of reading and writing streams, possibly due to the differing method signatures, variable names, and the presence of Base64 encoding details that obscured the common pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone because both functions perform a similar high-level operation: copying data from an input source to an output destination, with minor differences in data transformation (encoding) and error handling, which are considered partial functionality similarity under Type-4 clone category.
- 共享行为: Read bytes from an input source；Write bytes to an output file；Use stream read/write loop；Close streams after use
- 行为差异: Function A does not perform encoding, B does Base64 encoding；A throws exception on failure, B returns boolean；B uses buffered streams and a byte array buffer, A reads byte-by-byte；B has try-catch-finally for error handling, A does not
- 修正建议: Enhance model to recognize structural patterns of file copying even when encoding is added；Include data flow analysis to abstract away transformations like Base64；Augment training data with more diverse transformation examples

### case_id=3978 FN lexical_or_api_overlap

- 方法: `import_hints` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file or URL containing puzzle hint piece placements and places them on a board.
- B 摘要: Registers a user by encoding password, setting dates, creating a forum user via URL, persisting, and sending a confirmation email.
- 静态失败原因: The model likely relied on lexical and structural overlap, which is low (token Jaccard=0.137). It failed to recognize the abstract similarity in the overall I/O pattern and exception handling, possibly due to the absence of domain-specific knowledge.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a clone due to the high-level pattern of reading data from an external source (URL/file) and returning a success flag, which can be considered a Type-4 semantic clone.
- 共享行为: Both open a URL or file and use BufferedReader to read lines；Both handle IOException with try-catch；Both return a boolean indicating overall success or failure
- 行为差异: Function A processes piece IDs, columns, rows, rotations for a puzzle board; Function B processes user registration data；Function A uses StringTokenizer to parse space-separated values; Function B uses StringBuilder and URLConnection；Function A places pieces on a board and sets hints; Function B encodes passwords, sets authorities, persists user, and sends email
- 修正建议: Incorporate high-level functional role features；Use data flow analysis to capture external I/O patterns；Apply curriculum learning with more diverse Type-4 examples

### case_id=3979 FN benchmark_preference_bias

- 方法: `doTransfer` vs `setMembers`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request to another URL, acting as a proxy by copying headers and body.
- B 摘要: Parses HTML to extract component and priority options from a web form.
- 静态失败原因: The model focused on semantic and structural differences (proxy vs scraping) and low token overlap, missing the high-level pattern of URL connection and streaming that BCB considered clone-worthy.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely considered both as URL-based I/O operations with similar exception handling, accepting broad Type-4 functional similarity.
- 共享行为: Both open HTTP connections and read input streams；Both handle IOException and MalformedURLException
- 行为差异: A copies request headers and writes response; B parses HTML for specific patterns；A acts as a proxy; B scrapes metadata from a static page；A uses request/response objects; B is static with no parameters
- 修正建议: Include more Type-3/Type-4 clone examples in training；Incorporate API usage patterns or data flow features beyond lexical tokens

### case_id=3980 FN lexical_or_api_overlap

- 方法: `loadBinaryStream` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Loads a binary stream from an InputStream and writes it to the HTTP response output stream with headers set.
- B 摘要: Launches a NexOpen project configuration by validating project structure, processing POM files, setting Hibernate properties, and triggering an install action.
- 静态失败原因: The static model likely relied on token-level and structural similarity, which is very low (Jaccard=0.0487). It missed the subtle shared I/O pattern because the overall code and domain context are too divergent, and the model may not have learned to recognize such high-level semantic similarity from limited API overlap.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: None
- 共享行为: Both use IOUtils.copy to copy data from an InputStream to an OutputStream.；Both handle I/O resources with try-finally and close streams.
- 行为差异: A is a simple HTTP response stream copy; B involves complex project configuration, XML processing, and Eclipse resource management.；A has no branching or conditional logic; B has multiple condition checks and exception handling for project structure.；B deals with Hibernate dialect, reverse engineering files, and persistent properties; A has no such domain-specific logic.
- 修正建议: Enhance static models with more robust semantic understanding of I/O patterns.；Incorporate control-flow and data-flow features to capture common resource management idioms.；Use contrastive learning with examples of partial-functionality clones to improve recall.

### case_id=3981 FN benchmark_preference_bias

- 方法: `getResourceAsStream` vs `extractZipFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Retrieves a resource from a URL with caching and returns its InputStream.
- B 摘要: Extracts entries from a zip file to a destination directory.
- 静态失败原因: The static BERT model correctly predicted non-clone (0), but the BCB label is 1, so the model did not fail; the BCB annotation may be erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled these as clones due to superficial similarity in I/O operations (both involve reading and writing byte streams) and the presence of while loops, but this is too broad a category and likely a mislabel.
- 共享行为: Both read from an input stream and write to an output stream using buffered operations.；Both use while loops to read bytes until end of stream.
- 行为差异: Function A downloads and caches resources from URLs; Function B extracts a local zip file.；Function A returns an InputStream; Function B returns void and updates a UI component.；Function A handles HTTP caching, redirects, and conditional requests; Function B handles zip entries and directory creation.
- 修正建议: Re-evaluate this pair in the BCB dataset to confirm if it is a mislabel.；If it is a mislabel, remove the pair from clone set.

### case_id=3982 FN partial_functionality

- 方法: `getContent` vs `getEncoding`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Executes an HTTP request and returns the full response body as a string.
- B 摘要: Opens a URL connection and extracts the character encoding from HTTP headers or response content.
- 静态失败原因: Static models like BERT often rely on token overlap and API surface similarity. Here, token overlap is low (Jaccard 0.19), method names differ, and libraries (HttpClient vs URLConnection) are different. The model likely missed the higher-level behavioral similarity of processing HTTP responses.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both perform HTTP response processing, reading from streams, and extracting information (content vs. encoding). They share the common pattern of reading lines and using BufferedReader, and both are related to HTTP response handling.
- 共享行为: Both open HTTP connections and read from input streams；Both use BufferedReader to read lines of text；Both handle I/O exceptions
- 行为差异: A returns the entire response body; B returns only the encoding string；A uses HttpClient and sets timeouts; B uses URLConnection without timeout settings；A appends lines to a StringBuffer; B checks lines for charset/encoding patterns
- 修正建议: Use code structural similarity metrics (e.g., tree kernels, graph-based representations)；Incorporate cross-API mapping to recognize functionally equivalent operations；Train on more diverse examples of partial functionality clones

### case_id=3983 FN partial_functionality

- 方法: `PhoneSetImpl` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Constructor that reads lines from a URL, skips comment lines, and parses them to populate a phone set map.
- B 摘要: Method that opens a URL connection, reads all lines, concatenates them, and logs the entire string.
- 静态失败原因: Static BERT may rely on token similarity and API overlap, but the low Jaccard (0.30) and different method names suggest insufficient signal; the model fails to capture the fundamental difference in purpose and data flow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled as clone due to similar API sequence (URL, BufferedReader, readLine) and structural pattern, ignoring the distinct core logic (parsing vs logging).
- 共享行为: Both open a URL and read lines using BufferedReader；Both use while loop to read lines until null
- 行为差异: Function A filters lines starting with '***' and parses them into a map; Function B appends all lines to a StringBuffer；Function A is a constructor that initializes an object; Function B is a void method that logs the result；Function A counts lines; Function B does not；Function A uses url.openStream(); Function B uses url.openConnection().getInputStream()
- 修正建议: Incorporate data flow analysis to track how read lines are used (e.g., map vs buffer)；Use control flow graphs to distinguish filtering vs appending；Leverage method names and comments to infer intent；Train on more diverse patterns to avoid over-reliance on API sequence

### case_id=3984 FP partial_functionality

- 方法: `issueCommandToServer` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP command to a server by writing to a URL connection and reading the response line by line.
- B 摘要: Reads a service configuration file from the classpath via URL, parses lines to find a class name, and instantiates it as a FrameworkFactory.
- 静态失败原因: Static BERT models may over-rely on overlapping tokens (e.g., 'URL', 'BufferedReader', 'readLine') and similar syntactic structure (reading lines in a loop), ignoring the broader semantic context and data flow, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels clones based on functional similarity, not just structural I/O patterns. Since these functions serve entirely different purposes (one is a network client, the other is a service loader), BCB would correctly label them as non-clones.
- 共享行为: Both open a URL connection and use BufferedReader to read lines from the input stream in a while loop.
- 行为差异: A writes data to the output stream before reading; B only reads.；A returns a String (the HTTP response); B returns a FrameworkFactory object via reflection.；A uses HTTP parameters like command and capsule; B reads a specific service file for OSGi.；A has different exception handling (throws IOException); B throws a generic Exception if not found.
- 修正建议: Incorporate data flow analysis to distinguish writing vs reading operations.；Use type information (String vs FrameworkFactory) to differentiate return types.；Employ graph-based models that capture control dependencies and method calls.；Include method name embeddings to capture intent.

### case_id=3985 FN partial_functionality

- 方法: `getHTML` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads HTML from a URL using HttpURLConnection, optionally writes it to a file, and returns the HTML string.
- B 摘要: Reads a resource file from classpath and sets its content to a GUI text component.
- 静态失败原因: Low token Jaccard similarity (0.28) and different API usage (HttpURLConnection vs class loader) and output actions caused the static model to miss the shared reading pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels as clones when the core functionality of reading from a URL and building a string is shared, even if output contexts differ. The additional file writing or GUI update are considered extensions of the same base logic.
- 共享行为: Both read content from a URL-like source line by line.；Both build a string with newline separation using StringBuilder.；Both use BufferedReader and InputStreamReader.；Both handle exceptions (though differently).
- 行为差异: Function A writes to a file if dirPath is provided and returns the string; Function B sets GUI text and does not return.；Function A uses HttpURLConnection with custom User-Agent; Function B uses class loader to get resource.；Function A uses encoding parameter; Function B uses fixed UTF-8.；Exception handling: A prints stack trace; B silently ignores.
- 修正建议: Incorporate dataflow analysis to capture common reading logic.；Ignore output differences when evaluating core functionality.；Use graph-based representations that abstract over specific APIs.

### case_id=3986 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `logging`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies or adds a key-value pair in a localized properties file.
- B 摘要: Logs an inbound message with caching and optional truncation.
- 静态失败原因: Static model correctly predicted non-clone based on low token overlap and distinct semantics; the BCB label appears erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled this pair as clone; no meaningful functional or syntactic similarity justifies a Type-3/4 clone.
- 共享行为: Both use InputStream for reading data
- 行为差异: Different purpose: updating properties vs logging messages；Different output: writes to a file vs logs to a logger；Different processing: searching/replacing key-value vs copying and truncating payload
- 修正建议: Re-evaluate BCB label for this pair as likely false positive；If BCB label is correct, clarify functional similarity criteria

### case_id=3987 FN lexical_or_api_overlap

- 方法: `doRawRequest` vs `fileDownload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with given data and returns the response body as a string.
- B 摘要: Downloads a file from a given URL and saves it to a local directory.
- 静态失败原因: Low token similarity (0.208) and different method names/return types caused the model to miss the structural commonality of URL connection patterns. The model likely relied on lexical overlap, which is insufficient.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might consider these as sharing the core pattern of 'accessing a URL and processing its content', but the specific functionalities differ significantly. The BCB label of 1 may reflect a broad Type-3/Type-4 interpretation that groups any network I/O operations.
- 共享行为: Both open a URL connection and read from its input stream.；Both handle I/O operations with streams and readers.
- 行为差异: A sends POST data to the server, B does not send any data.；A returns the response as a string, B writes the response to a file on disk.；A reads line-by-line, B reads byte-by-byte (though using character streams).；A throws IOException, B catches Exception and logs.
- 修正建议: Incorporate structural features like API call sequences (e.g., URL, openConnection, getInputStream).；Use data-flow analysis to capture the pattern of reading from a URL.；Augment training data with functionally similar but lexically diverse examples.

### case_id=3988 FN benchmark_preference_bias

- 方法: `sendExceptionToServer` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.5`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends exception details (stack trace, config, user info) to a remote server via HTTP POST for error reporting.
- B 摘要: Sends an XML request to a geo-parser service and parses the response to extract place names and gazetteer IDs.
- 静态失败原因: Static BERT models rely on lexical/syntactic similarity; low token overlap (0.148) and different method names, parameters, and control flow (e.g., retry loop vs. no retry) led to a non-clone prediction. The models likely missed the high-level structural pattern of HTTP client usage.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'network communication' functions that send data to a server and handle responses, which could be viewed as a broad functional similarity (Type-4). However, the specific tasks are very different, and this pair likely represents a borderline or overly broad annotation.
- 共享行为: Both use HTTP to communicate with a remote server.；Both encode data (URL-encoding or XML) before sending.；Both read server response via BufferedReader.；Both print or log error messages on failure.
- 行为差异: A performs POST with form-encoded parameters; B performs GET with XML payload in URL.；A expects a simple "success" response; B parses XML to extract structured data.；B has retry logic (3 attempts); A does not retry.；A sends exception and system info; B sends geospatial query and processes place names.
- 修正建议: Use a model that incorporates runtime behavior or dataflow analysis to detect similar I/O patterns.；Train with a broader definition of clones that includes functional categories like 'HTTP client'.；Add domain-specific features for network communication (e.g., URL encoding, stream reading).

### case_id=3989 FN benchmark_preference_bias

- 方法: `getFile` vs `runDynusT`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies its endpoint, and saves it locally.
- B 摘要: Sets up a temporary directory, copies executable and model files, runs DynusT.exe, and optionally cleans up.
- 静态失败原因: The static model relied on low token Jaccard (0.064) and structural differences, missing the high-level functional similarity that BCB annotators might have perceived, though the model's prediction aligns with strict semantic assessment.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'file management' utilities with similar control flow patterns (loops, conditional checks, error handling), even though the core logic is different, favoring broad Type-4 partial functionality similarity.
- 共享行为: Both involve file I/O operations (creating, writing, copying).；Both use logging for progress and error tracking.；Both handle exceptions with try-catch blocks.；Both interact with the file system using temporary directories.
- 行为差异: Function A downloads from a URL, while Function B copies from local directories.；Function A parses and modifies XML, while Function B executes an external program.；Function A is a static utility returning a file location, while Function B is an instance method with side effects.；Function A deals with WSDL files, while Function B deals with simulation executables and config files.
- 修正建议: Improve annotation guidelines to distinguish superficial file operations from true semantic clones.；Incorporate data flow and API usage analysis to better capture behavioral similarity.；Use hierarchical or pipeline representations to model multi-step processes.

### case_id=3990 FP lexical_or_api_overlap

- 方法: `readData` vs `clonarFichero`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses comma-separated strings into sets and maps for Tibetan/sanskrit character processing.
- B 摘要: Copies a file from input stream to destination using FileChannel.
- 静态失败原因: The static BERT model likely overfocused on lexical similarities like 'HashSet', 'StringTokenizer', 'IOException', and general exception handling patterns. Additionally, both functions have similar boilerplate structure (try-catch with IOException). The model may have been misled by the overall pattern of reading and processing data, even though the specific data sources and operations are unrelated.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clones because the overall functionality and purpose are completely different; one is a character/Tibetan processing routine, the other is a file copy utility.
- 共享行为: Both use exception handling (IOException)；Both use System.out.println for debug/error messages
- 行为差异: Function A is about data parsing and set population; Function B is about file I/O copying；Function A has no I/O parameters; Function B takes file input stream and destination path；Function A is void; Function B returns boolean status
- 修正建议: Improve training data to include more diverse non-clone pairs with overlapping API usage；Use finer-grained semantic features focusing on data flow and function purpose；Consider adding code structure features that distinguish between data-parsing and file-copy tasks

### case_id=3991 FN partial_functionality

- 方法: `testReadPerMemberSixSmall` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Tests reading multiple GZIP members by copying to NullOutputStream and verifying byte counts.
- B 摘要: Launches a Maven-based project configuration setup, handling pom.xml files and Hibernate reverse engineering.
- 静态失败原因: Static model likely focused on token-level overlap, which is very low, and structural patterns; it failed to see any deeper semantic similarity that BCB might have considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might label as clone due to shared I/O utility usage and stream copying pattern, considering broad partial functionality similarity under Type-4.
- 共享行为: Both use IOUtils.copy to copy from an InputStream to an OutputStream；Both handle IOException (directly or via catch)；Both perform file-related operations (though different files)
- 行为差异: Function A is a unit test for GZIPInputStream, while Function B is a complex configuration method for Eclipse plugin；Function A has a loop over 3 iterations, Function B has conditional branches and no loop；Function A uses assertions; Function B uses logging and exception propagation；Function B interacts with Eclipse workspace resources and project metadata
- 修正建议: Improve model to recognize that generic I/O utility usage does not imply functional clone；Add context-aware semantic understanding beyond token overlap

### case_id=3992 FP boilerplate_overlap

- 方法: `encodeFileToFile` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Encodes a file to Base64 and writes to another file, returning success flag.
- B 摘要: Main method that reads a Prolog file, parses it, generates adapter code and writes output files.
- 静态失败原因: Static BERT may have been misled by common boilerplate patterns (try-catch-finally, while loop with stream reading) despite low token Jaccard, leading to false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have completely different goals and minimal semantic overlap beyond generic file operations.
- 共享行为: Both involve file I/O, error handling, and stream usage
- 行为差异: Different overall purpose (encoding vs code generation)；Different input processing (Base64 decode vs Prolog parsing)；Different output generation (write encoded bytes vs compile and write classes)；Different control flow and complexity
- 修正建议: Improve training data to include more diverse non-clone pairs with boilerplate overlap；Incorporate structural similarity or functional signature matching；Increase threshold for sequences with high boilerplate but low semantic similarity

### case_id=3993 FN partial_functionality

- 方法: `saveAttachmentBody` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Saves an email attachment body to a file and updates the database with its metadata.
- B 摘要: Launches a NexOpen project configuration by processing Maven POM files and setting up Hibernate properties.
- 静态失败原因: The static model relied on lexical and structural features, which had low overlap (token Jaccard 0.0625), correctly predicting non-clone. It missed the annotators' broad view of partial I/O pattern similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: The BCB annotators may have considered the shared IOUtils.copy pattern and file existence checks as evidence of partial functional similarity, leading to a Type-4 clone label despite different overall purposes.
- 共享行为: Both use IOUtils.copy to read from an InputStream and write to an OutputStream.；Both check for file existence before proceeding.；Both handle exceptions (throws or catches) during I/O operations.
- 行为差异: Function A is a stateless utility for saving attachments; Function B configures and launches an Eclipse project.；Function A writes to a file and updates a content URI; Function B writes to a ByteArrayOutputStream and creates files.；Function B involves complex XML processing and job scheduling; Function A does not.；Function A returns void; Function B is a void method but modifies project state.
- 修正建议: Use models that capture overall program semantics rather than surface-level patterns.；Incorporate dataflow and control flow analysis to distinguish core functionality from boilerplate I/O.；Reduce reliance on trivial shared utilities (e.g., IOUtils.copy) for clone detection.

### case_id=3994 FN benchmark_preference_bias

- 方法: `createOutputStream` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Creates a zip output stream by copying all entries from a zip input file except 'content.xml', then adds a new 'content.xml' entry and returns a BufferedWriter.
- B 摘要: Modifies a properties file for a given locale by copying an English file if missing, then reading and updating a specific key-value pair.
- 静态失败原因: The low token Jaccard (0.13) and different method names indicate little lexical overlap. Static BERT/GraphCodeBERT models rely on surface-level patterns and may miss the high-level functional similarity in file manipulation that BCB annotators consider.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label these as clones due to broad Type-3/Type-4 criteria: both functions perform file modification tasks with buffered I/O, involve conditional logic, and are part of configuration or resource handling, even though the exact data formats differ.
- 共享行为: Both perform file I/O with buffered readers/writers.；Both handle character encoding during read/write.；Both iterate over input file content and conditionally write to output.；Both use standard Java I/O classes (File, InputStream, OutputStream, Reader, Writer).
- 行为差异: A works with zip archives, B with plain text properties files.；A copies all entries except one, then adds a new entry; B modifies or appends a specific property.；A returns a BufferedWriter, B returns void.；A switches encoding from ISO-8859-1 to UTF8; B does not explicitly set encoding.
- 修正建议: Incorporate task-level structural patterns (e.g., file I/O, conditional processing) into the model.；Use contrastive learning on diverse file-processing functions to capture abstract similarities.；Augment training data with more Type-3/Type-4 clone pairs that share functional intent despite low lexical overlap.

### case_id=3995 FP partial_functionality

- 方法: `run` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a resource file from classloader and displays its content in a Swing text area.
- B 摘要: Reads a service configuration file from classloader and instantiates a FrameworkFactory from a class name.
- 静态失败原因: The static model likely overemphasized the overlapping API calls (getClassLoader, getResource, openStream, BufferedReader, readLine) and structural patterns, failing to capture the distinct high-level semantics and end goals.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels clones only when functions share similar core functionality or algorithmic intent. Here, despite a common pattern of reading a resource file, the purposes (GUI display vs. service loading) and subsequent operations are too divergent, so BCB correctly marked non-clone.
- 共享行为: Both obtain a URL from the classloader；Both open an InputStream and wrap with BufferedReader；Both read lines in a loop
- 行为差异: Different resource paths (context-specific vs. fixed META-INF/services path)；A appends lines with newline and sets GUI text; B searches for first non-comment line and instantiates a class；A swallows exceptions; B throws exception if factory not found；A uses SwingUtilities.invokeLater for GUI update; B returns an object
- 修正建议: Incorporate task-level context or summarize the intent of each function；Use graph-based representations to distinguish control/data flows toward different outcomes (GUI vs. reflection instantiation)；Train with more examples of reading patterns with different downstream purposes

### case_id=3996 FP partial_functionality

- 方法: `downloadURLtoString` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads the content of a URL into a single string by reading lines.
- B 摘要: Imports sequence data from a selected URL by parsing a FASTA-like format into two lists of names and sequences.
- 静态失败原因: The model likely over-weighted the shared boilerplate (opening streams, reading lines) and overlooked the distinct high-level purpose and data handling, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: Despite both involving URL reading, the overall functionality differs significantly: one is generic content retrieval, the other is domain-specific sequence import. BCB typically requires functional similarity for clone labeling, so they would not consider these clones.
- 共享行为: Both open a URL's input stream and read line by line.
- 行为差异: Function A simply concatenates all lines into one string; Function B parses lines to extract names and sequences in a specific format.；Function B uses a helper class for reading sequences, handles multiple records, and includes error handling for various exceptions.；Function B builds two separate lists (names and sequences) rather than returning a single string.
- 修正建议: Incorporate dataflow analysis to distinguish pure IO operations from domain-specific parsing.；Use method-level documentation or name embedding to capture intent.；Enhance token-level models with context about the broader class or API usage.

### case_id=3997 FP lexical_or_api_overlap

- 方法: `get` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches game records from a URL via HTTP GET, parses lines not starting with '#' into GameRecord array.
- B 摘要: Fetches ticket IDs for a queue from a REST API via HTTP GET, then retrieves each ticket individually, returning list of RTTicket.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized lexical and boilerplate overlap (HTTP GET, BufferedReader, error handling) while missing the differences in high-level intent and overall functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the functions serve distinct purposes (game records vs ticket tracking) and have significant differences in logic and API usage, despite both being HTTP GET retrievals.
- 共享行为: Both perform HTTP GET requests；Both parse response line by line using BufferedReader；Both return null on failure or error
- 行为差异: Different URL construction and request parameters；Different response parsing logic (A skips '#' lines, B looks for 'ticket/' and checks for 'does not exist.')；B includes an additional loop to fetch tickets after parsing IDs；B uses session management and different HTTP library (HttpClient vs HttpURLConnection)
- 修正建议: Train model to better differentiate between task-specific logic and common boilerplate；Incorporate task-level semantic information or use contrastive learning to separate similar-looking but different functions；Enhance model's ability to capture long-range dependencies and overall flow

### case_id=3998 FN benchmark_preference_bias

- 方法: `doGet` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET requests for a portal, resolving page parameters, checking user visibility, and optionally caching page output to a file.
- B 摘要: Recursively copies a file or directory using NIO FileChannel, handling type mismatches and ensuring target existence.
- 静态失败原因: Static BERT likely correctly identified these as non-clones due to very low token overlap (Jaccard 0.096) and distinct API usage (HttpServletRequest vs File). The model may have failed to consider that BCB's definition of clone includes partial functionality, which is a subjective preference.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider these clones due to partial functional similarity: both perform file creation/writing and handle I/O errors. However, the main logic is entirely different, so it is likely an annotation error or an overly broad Type-4 match.
- 共享行为: Both functions involve file I/O operations (creating, writing, or copying files).；Both perform existence checks before operations.；Both throw or catch IOException-related exceptions.
- 行为差异: Function A is a web servlet handler; Function B is a utility file copy method.；Function A uses HttpServletRequest/Response, Properties, Page objects, and caching logic.；Function B uses File, FileChannel, and recursive directory traversal.；Function A has complex conditional logic for page resolution and security; Function B has simple conditional logic for directory vs file.
- 修正建议: Increase training data for Type-4 clones that share only low-level I/O patterns.；Incorporate higher-level semantic understanding of method purpose (e.g., web vs file utility).；Use fine-grained API usage embeddings to distinguish different domains.

### case_id=3999 FN benchmark_preference_bias

- 方法: `writeFileType` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a file of URIs, fetches each URI's content, checks for OWL/RDFS/RDF namespaces, and writes classification to an output file.
- B 摘要: Constructs parameters for a RenRen API call, sends a POST request, and prints the response.
- 静态失败原因: Static BERT predicted non-clone, which aligns with semantic analysis; BCB label is likely an anomaly.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider both as network I/O routines that read from URLs, but this is a very broad Type-4 interpretation; likely an annotation error.
- 共享行为: Both use HTTP connections (URL, URLConnection) to fetch data.；Both read lines from an input stream.
- 行为差异: Different purpose: RDF classification vs social network API call.；Different output: file vs console.；Different control flow: skip lines, string matching vs parameter building and POST.；Different exception handling: write BROKEN on error vs print stack trace.
- 修正建议: Re-examine BCB annotation for potential mislabel.；Use stronger semantic features to avoid over-generalization.

### case_id=4000 FN benchmark_preference_bias

- 方法: `main` vs `readIntoList`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends a POST request to RenRen API with predefined parameters and prints the response.
- B 摘要: Reads HTML from a URL, parses anchor tags, and populates a JMenu with items that trigger actions.
- 静态失败原因: The static BERT/GraphCodeBERT model likely focused on the surface-level API differences (PostParameter, HttpURLConnection vs. BufferedReader, JMenuItem) and method signatures, failing to recognize the abstract commonality of reading from a URL. The low token Jaccard (0.112) also contributed to a low similarity score.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotators may have considered both functions as 'reading from a URL and processing each line', ignoring the context-specific details as variations. This broad interpretation treats any URL-reading loop as a clone, even with different processing logic.
- 共享行为: Open a URL and read lines using BufferedReader
- 行为差异: Function A sets up an HTTP connection with parameters and POST method; Function B does not.；Function A prints each line; Function B parses HTML and creates GUI components.；Function A is a static main method; Function B is a private instance method.；Function A has no parameters; Function B takes a URL and a Map.
- 修正建议: Use a model that can better capture abstract I/O patterns beyond lexical tokens.；Incorporate a broader notion of functional similarity that tolerates different API usage.；Retrain with more examples that have low lexical overlap but similar I/O structure.
