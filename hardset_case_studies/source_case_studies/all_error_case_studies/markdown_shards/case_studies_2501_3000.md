# Error Case Studies 2501-3000

- Source model: `configured-llm`
- Cases: `2501` to `3000`

### case_id=2501 FN partial_functionality

- 方法: `main` vs `sendRequestObjectResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Main method constructs HTTP POST request with multiple parameters to RenRen API, sends it, and prints response.
- B 摘要: Method sends an HTTP request with XML content (optionally compressed) to a servlet, saves response to a file based on content type, and returns the file path.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token similarity and structural patterns; very low Jaccard similarity (0.079) and different API usage lead to prediction of non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'sending HTTP requests and handling responses' functional pattern, albeit with different specifics, thus labeling as clone under broad Type-4 similarity.
- 共享行为: Both open an HTTP connection and set DoOutput to true.；Both write data to the output stream of the connection.；Both read the response from the input stream and print some output to System.out.；Both use java.net.URL and HttpURLConnection/URLConnection.
- 行为差异: Method A uses POST with pre-built parameters; Method B uses a generic request string and supports compression (GZIP).；Method A does not process response further; Method B saves response to a file and returns its path.；Method B has extensive error handling with dialog; Method A prints stack trace only.；Method B handles content type to determine file extension; Method A does not handle file output.
- 修正建议: Increase sensitivity to high-level functional similarity even with low lexical overlap.；Incorporate data flow analysis to detect common patterns like network request handling.；Use hierarchical embeddings that capture overall task structure.

### case_id=2502 FP lexical_or_api_overlap

- 方法: `hashPassword` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Hashes a password using SHA and Base64 encoding.
- B 摘要: Performs a Struts action that handles a classification request involving session validation, XML data preparation, URL connection, and result parsing.
- 静态失败原因: Static BERT models may have been misled by token-level overlap of common API names like 'MessageDigest' vs 'MessageResources', 'String', and 'IOException', or by the presence of logging and exception handling boilerplate.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotation considers these non-clones because they have completely different purposes and implementations; no functional overlap.
- 行为差异: Function A is a password hashing utility with no side effects beyond returning a hash string.；Function B is an action handler with extensive web logic, session manipulation, and external communication.；Function A uses MessageDigest for cryptographic hashing; function B uses MessageResources for error messages.；Function B involves multiple conditional branches and error handling; function A is a straightforward sequence.
- 修正建议: Increase weight on structural and dataflow differences.；Use longer context windows or graph-based representations to capture program semantics beyond token sequences.；Train on more diverse negative samples to reduce sensitivity to coincidental lexical matches.

### case_id=2503 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a new version of jEdit by reading a remote version file and comparing builds.
- B 摘要: Retrieves a list of open tickets for a queue from a Request Tracker via REST API.
- 静态失败原因: The model likely over-relied on lexical overlap (e.g., BufferedReader, readLine, exception handling) and general boilerplate patterns, failing to capture the divergent high-level semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotation typically treats these as non-clones because they perform completely different tasks with distinct inputs, outputs, and side effects.
- 共享行为: Both use BufferedReader to read lines from an input stream；Both handle exceptions with try-catch blocks；Both use URL or HTTP connection to fetch data
- 行为差异: Function A shows UI cursor changes and displays user messages; Function B does not；Function A reads a simple version and build number; Function B parses ticket IDs and fetches full ticket objects；Function A is a void method with side effects; Function B returns a list of tickets；Function B involves HTTP GET request with parameters; Function A uses raw URL stream
- 修正建议: Incorporate dataflow analysis to distinguish different uses of stream data；Use contrastive learning that emphasizes functional semantics over superficial patterns；Augment training data with harder negative pairs that share API usage but differ in intent

### case_id=2504 FP lexical_or_api_overlap

- 方法: `getRequestContent` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens a given URL, reads the first line, and returns it.
- B 摘要: Opens a hardcoded URL, reads all lines without processing, handles exceptions.
- 静态失败原因: The model likely overemphasized the shared API calls (URL, BufferedReader, InputStreamReader) and structural similarity (try-catch, while loop), ignoring the semantic differences in return type and data handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label these as non-clones due to different signatures, return types, and functional purpose (one extracts data, the other discards it).
- 共享行为: Both create a URL object；Both use BufferedReader to read from an InputStream；Both close the reader after reading
- 行为差异: A takes a URL parameter; B uses a hardcoded URL；A returns a String; B is void；A reads only the first line; B reads all lines until null；A disconnects the connection; B does not
- 修正建议: Enhance training data with negative examples sharing API calls but differing in intent；Incorporate return type and parameter analysis；Emphasize control flow differences (single line read vs. loop until null)

### case_id=2505 FP boilerplate_overlap

- 方法: `main` vs `upload`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Entry point that parses a Prolog file, generates adapter layers, and outputs a JAR with compiled classes and resources.
- B 摘要: Uploads an image file to a specified destination directory using file I/O utilities.
- 静态失败原因: Static BERT models may over-rely on overlapping tokens like 'File', 'IOException', 'System.out.println', and try-catch blocks, failing to capture the deep semantic divergence between a code generation pipeline and a simple file upload.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires some level of functional or syntactic similarity beyond trivial boilerplate; these two functions share only common Java idioms and have completely different purposes and complexity, so they are considered non-clones.
- 共享行为: Both use java.io.File and handle IOException with try-catch and printStackTrace.；Both perform file I/O operations (read/write).；Both use System.out.println for output.
- 行为差异: Function A is a complex multi-step code generation pipeline; Function B is a simple file copy.；Function A takes command-line arguments and produces compiled output; Function B copies one file to a fixed destination.；Function A returns void; Function B returns a String.；Function A uses many domain-specific classes (Parser, FactVisitor, etc.); Function B uses only standard I/O utilities.
- 修正建议: Train on more diverse examples to reduce sensitivity to common boilerplate patterns.；Incorporate data-flow or control-flow features to differentiate simple I/O routines from complex multi-step processes.；Use contrastive learning to emphasize semantic differences even when surface tokens overlap.

### case_id=2506 FP lexical_or_api_overlap

- 方法: `main` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Tests StraightStreamReader by writing bytes to a file and reading them back with various methods.
- B 摘要: Handles GUI action commands for setting preferences like Graphviz path, ImageMagick path, and other settings.
- 静态失败原因: High lexical overlap (File, IOException, try-catch) and common code patterns misled the model into detecting similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB requires functional similarity; these functions have no overlapping purpose beyond standard library usage.
- 共享行为: Both use File and IOException；Both have try-catch blocks
- 行为差异: A performs file I/O testing; B handles GUI events and preferences；A is a test harness; B is a settings dialog event handler；A is static main; B is instance actionPerformed
- 修正建议: Improve semantic understanding of overall function purpose；Incorporate control flow and data flow analysis to distinguish test vs. GUI logic；Use larger context or method-level embeddings that capture domain

### case_id=2507 FN long_range_semantics

- 方法: `getResourceAsStream` vs `unzip`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a resource from a URL using HTTP, caches it locally, and returns an InputStream from the local file.
- B 摘要: Extracts a ZIP file by iterating through entries and writing them to a directory.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on lexical overlap and method names, which are very different (0.16 token Jaccard), and missed the abstract I/O pattern shared by both functions. The model failed to capture the structural similarity of the byte-copying loop and buffer management.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label these as clones because both functions exhibit a similar core I/O pattern of reading from a stream and writing to a file using buffered streams, which is a common Type-3/Type-4 scenario where the overall algorithmic structure is considered similar despite different external functionalities.
- 共享行为: Both read from an input stream and write to local files using buffered streams.；Both use a while loop to read bytes and write them to an output stream.；Both involve file creation and directory management.
- 行为差异: Function A handles HTTP caching, conditional requests, and returns an InputStream; Function B is void and handles ZIP entries.；Function A reads bytes one at a time; Function B reads into a buffer.；Function A has extensive exception handling; Function B throws exceptions.；Function A interacts with a cache hashtable; Function B does not.
- 修正建议: Incorporate graph-based representations to capture data flow and control flow structures.；Use code simplification or AST-based matching to highlight the core I/O loop.；Augment training data with pairs that share structural patterns but differ in domain-specific code.

### case_id=2508 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getUser`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a new jEdit version by reading a version file from a URL and comparing builds.
- B 摘要: Retrieves a user by login; if not found in DAO, loads user data from a config file and saves it.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized the lexical and API overlap (BufferedReader, URL, InputStream, readLine, while loops) and the similar control flow structure, ignoring the semantic differences in the data being processed and the overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically considers clones if functions share core functionality or have similar high-level purpose. Here, both involve reading a remote file and parsing, but the domains (version check vs user management) are entirely different, so they are not considered clones.
- 共享行为: Both read lines from an InputStream using BufferedReader.；Both parse each line to extract data (using startsWith or StringTokenizer).；Both handle exceptions (IOException/Exception) with error messages or stack traces.
- 行为差异: Different purposes: version check vs user retrieval/creation.；Different data sources: version URL vs config file from classpath.；Different parsing: single-line prefix check vs multi-field tokenization.；Different actions: show message or call newVersionAvailable vs create User and save to DAO.
- 修正建议: Incorporate data flow analysis to track variable types and usage (e.g., version vs user).；Use structural similarity measures that weigh statement sequence more heavily.；Include domain-specific features like method name similarity or output type.

### case_id=2509 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `sendRequest`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks and link texts from a given URL by reading the HTML and applying regex patterns.
- B 摘要: Sends an XML request via HTTP with GZIP compression to a server and parses the XML response using JDOM, but returns an empty string.
- 静态失败原因: The model likely focused on similar API usage (URL, URLConnection, getInputStream, BufferedReader) and method signatures (both involve 'URL' and 'request'), leading to a false positive by boilerplate overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because overall functionality is completely different despite some low-level I/O overlap, and the annotation guidelines emphasize functional purpose.
- 共享行为: Both create a URL and open a connection；Both read from an input stream using BufferedReader/InputStreamReader
- 行为差异: A reads HTML and extracts links; B sends a request and parses XML response；A uses regex for link extraction; B uses JDOM SAXBuilder for XML parsing；A returns extracted link and text vectors; B returns an empty string (response built but not returned)；A is designed for web crawling; B is for applet server communication
- 修正建议: Incorporate high-level semantic goals (link extraction vs. XML request) into the model；Use graph-based representations capturing control/data flow differences；Add context from surrounding code or documentation to disambiguate purpose

### case_id=2510 FN benchmark_preference_bias

- 方法: `getFile` vs `write`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint attribute in the XML document, and returns the local file path, with extensive logging and exception handling.
- B 摘要: Encrypts ByteBuffer arrays using SSLEngine, handling SSL handshake and application data wrapping, and returns encrypted ByteBuffer arrays.
- 静态失败原因: The static model correctly predicted non-clone (0) due to very low token overlap (0.07) and distinct API usage. It did not fail; the BCB label appears inconsistent.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones based on a broad categorization as 'network-related utilities' or 'I/O-heavy operations', accepting partial functionality similarity, or it could be a labeling error.
- 共享行为: Both use I/O operations (streams, channels, buffers).；Both include try-catch blocks for exception handling.；Both utilize logging via a logger object.
- 行为差异: Function A deals with file downloading and XML manipulation; Function B performs SSL encryption on byte buffers.；Function A returns a String file path; Function B returns an array of ByteBuffers.；Function A uses URL, File, and XML APIs; Function B uses SSLEngine and NIO buffers.；Function A has no SSL or encryption logic; Function B has no file or XML operations.
- 修正建议: Verify and correct the BCB label for this pair if it is indeed a mislabel.；Improve model to handle low lexical overlap cases; it already did well here.；Consider that static models may sometimes miss clones with low token overlap, but this case is a true negative.

### case_id=2511 FN partial_functionality

- 方法: `Converter` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.15`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Converts a file from SJIS encoding to UTF8 encoding using buffered I/O.
- B 摘要: Builds an edited version of a website by processing XML files, applying XSLT transformations, and writing output files with various replacements.
- 静态失败原因: Static models like GraphCodeBERT may focus on surface-level token similarities (e.g., 'FileInputStream', 'char', 'buf', 'read', 'write') and miss the deep semantic differences in functionality and context.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone due to both functions performing file I/O with buffered character transfer, a common partial functionality pattern, but the overall semantics are vastly different.
- 共享行为: Reads from an input file and writes to an output file using character buffers
- 行为差异: Code A is a simple encoding converter; Code B involves complex website building with XSLT, multiple file operations, and property handling；Code A has no dependencies; Code B uses many libraries (DOM, XSLT, FTP, etc.)；Code A is a constructor; Code B is a void method
- 修正建议: Incorporate structural analysis like AST or data flow to capture algorithmic differences；Use contrastive learning to discriminate between similar I/O patterns with different intents；Include method signature and context embeddings to distinguish constructors from complex methods

### case_id=2512 FP boilerplate_overlap

- 方法: `decodeFileToFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Decodes a Base64 input file to an output file using streams, handling exceptions and cleanup.
- B 摘要: Handles action events from a UI, managing preferences and file chooser dialogs for various settings.
- 静态失败原因: Static models like BERT or GraphCodeBERT may overemphasize lexical or structural boilerplate patterns (e.g., try-catch, resource closing) and overlook the distinct semantic purposes. The low token Jaccard suggests limited overlap, but the model might have been misled by common keywords like 'File' and 'filename', or by similar control flow structures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they have completely different functionalities: one is a file decoding utility, the other is a UI event handler. The only overlap is generic exception handling and resource cleanup, which is not sufficient for functional similarity.
- 共享行为: Both use try-catch for exception handling；Both have variable initialization and conditional checks；Both close resources (streams in A, UI components in B?)
- 行为差异: A performs file I/O and Base64 decoding; B updates UI and stores preferences；A uses InputStream/OutputStream; B uses JFileChooser and puts preferences；A returns boolean success; B is void and does not return a value
- 修正建议: Incorporate data flow analysis to differentiate between file I/O and UI actions；Use context from method names or surrounding classes to disambiguate；Train with more diverse examples of event handlers vs. utility functions

### case_id=2513 FN partial_functionality

- 方法: `getFile` vs `decodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies XML attribute, and saves to temp directory.
- B 摘要: Decodes a Base64-encoded input file and writes the decoded output to another file.
- 静态失败原因: Low token overlap (Jaccard 0.14) and different APIs (Axis vs Base64) make static models miss any semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered both as file I/O utility functions, but this is too broad and likely a misannotation.
- 共享行为: Both read from an input source (URL stream vs file) and write to a file output stream.；Both handle I/O exceptions and use buffered streams.
- 行为差异: Function A downloads over HTTP and modifies XML; Function B decodes Base64.；Function A returns file path; Function B returns boolean success.；Function A uses URL, XML parsing, and file renaming; Function B uses Base64 decoding.；Function A has more complex error handling with specific exceptions; Function B uses generic IOException.
- 修正建议: Use more comprehensive code embeddings capturing high-level intent.；Incorporate code documentation or method name semantics.

### case_id=2514 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft handshake by validating username and verifying session via HTTP.
- B 摘要: Performs Google image search by fetching and parsing image URLs from HTTP response.
- 静态失败原因: Relied on lexical and API overlap (URL, BufferedReader) and similar syntactic patterns, ignoring domain-specific logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB focuses on functional similarity; these functions have entirely different purposes despite similar API usage.
- 共享行为: Both open HTTP connections and read data；Both use URL and BufferedReader；Both handle exceptions
- 行为差异: Different input parameters and outputs；Different URL construction and parsing logic；Different error handling；Different conditions and control flow
- 修正建议: Enhance model to distinguish based on specific domain logic；Use task-specific features or data augmentation for functional semantics

### case_id=2515 FP lexical_or_api_overlap

- 方法: `testCodingEmptyFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Tests encoding of data using LengthDelimitedEncoder with file channel transfer and assertion of output.
- B 摘要: Handles GUI action events to update configuration preferences, such as setting paths for external tools and UI settings.
- 静态失败原因: Despite low token Jaccard, the model might have relied on overlapping API terms like 'File', 'FileOutputStream', and 'String', or misinterpreted the truncated code B's structure as similar to code A's file handling, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have completely different purposes (test vs. GUI event handler) and share no meaningful functionality beyond generic Java I/O operations.
- 行为差异: A is a unit test for encoding; B is a GUI event handler for preference updates.；A uses LengthDelimitedEncoder for byte transfers; B uses JFileChooser and preference storage.；A has no user interaction; B involves user dialogs and UI updates.；A is short and focused; B is long with multiple command branches.
- 修正建议: Increase sensitivity to functional context (test vs. GUI).；Incorporate control flow and data dependency analysis to distinguish test methods from event handlers.；Use longer-range context or structural templates to avoid false matches on common API usage.

### case_id=2516 FN benchmark_preference_bias

- 方法: `readPage` vs `addIDs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a URL line by line, optionally discarding lines starting with '#', and returns the concatenated HTML string.
- B 摘要: Reads a URL line by line, parses HTML to extract metabolite IDs and score, and updates a PeakListRow object with various chemical identifiers, returning the score as an integer.
- 静态失败原因: Static BERT/GraphCodeBERT likely captured the different return types, functional purposes, and overall logic, leading to a non-clone prediction. However, BCB's broad Type-3/Type-4 criteria may have considered the shared I/O pattern sufficient for clone labeling, causing a mismatch.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label them as clones due to superficial structural similarity: both use BufferedReader to read from a URL and process lines in a loop, which could be considered a Type-3 clone pattern under a broad interpretation of functional similarity.
- 共享行为: Both use BufferedReader to read from a URL line by line；Both use a while loop with readLine() until null；Both handle I/O exceptions implicitly or explicitly
- 行为差异: readPage returns a concatenated HTML string; addIDs returns an integer score and modifies a PeakListRow object；readPage optionally ignores comment lines; addIDs performs complex HTML parsing and conditional updates；addIDs has multiple conditional branches and nested parsing logic; readPage has a simple conditional for comment filtering
- 修正建议: Improve model to focus on functional semantics rather than structural patterns；Use dataflow or dependency analysis to capture true behavioral differences；Adjust training to penalize superficial I/O pattern matches when output semantics differ

### case_id=2517 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `checkInputStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a properties file for a given locale, modifies or adds a message, and writes back.
- B 摘要: Compares the content of an input stream to a given byte array, optionally checking full length.
- 静态失败原因: Static BERT likely correctly predicted non-clone due to low lexical overlap and different control flow; the BCB label is questionable, so the error is due to benchmark preference bias rather than model deficiency.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both methods using InputStream and byte arrays, but the overall functionality and context are completely different, suggesting a broad Type-4 or false positive annotation.
- 共享行为: Both involve reading from an InputStream；Both handle byte-level data；Both are utility methods that may be used in testing or configuration
- 行为差异: A performs file I/O and property manipulation; B only compares byte arrays；A modifies a file on disk; B is read-only；A is for localization; B is for verification；A handles multiple encoding steps; B is straightforward comparison
- 修正建议: Re-evaluate BCB annotation for this pair；Use stricter functional equivalence criteria；Consider context and domain of the functions

### case_id=2518 FP lexical_or_api_overlap

- 方法: `getNetworkServersIPs` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches server IPs from a URL by parsing lines after a marker.
- B 摘要: Checks for software upgrades by querying a remote server and updating local database.
- 静态失败原因: Static BERT/GraphCodeBERT models may be misled by the lexical overlap of URL/URLConnection/BufferedReader and the sequential reading loop, ignoring the distinct higher-level semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the overall functionality and intent are completely different despite sharing common API usage patterns.
- 共享行为: Both open a URL connection and read lines from the input stream.
- 行为差异: Function A returns a vector of IPs; function B performs database operations, UI visibility changes, and shows messages.；Function A parses specific lines (with '!SERVERS' and ':'); function B parses XML-like rows and handles upgrade logic.；Function B has complex conditional branches for error handling and upgrade types; function A is straightforward.
- 修正建议: Incorporate data flow and control flow analysis to differentiate distinct operations.；Use contrastive learning with negative samples that share API usage but differ in intent.

### case_id=2519 FP lexical_or_api_overlap

- 方法: `setBundleInfoName` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads key-value pairs from a URL and updates bundle info list entries matching the symbolic name.
- B 摘要: Downloads an RDF model from a URL and returns it as a Model object.
- 静态失败原因: The static model likely overemphasized lexical overlap (URL, InputStream, catch IOException) and common method structure (try-catch, reading from URL), missing the distinct post-processing logic and different return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would consider these non-clones because they perform fundamentally different tasks: one is configuration update, the other is model download. The shared URL-opening pattern is too generic to indicate semantic similarity.
- 共享行为: Both open a URL and read from its input stream.；Both handle IOException with a catch block.
- 行为差异: A parses lines as key=value pairs and modifies a list; B reads entire stream into an RDF model.；A returns boolean success flag; B returns a Model or throws RuntimeException.；A loops over list entries to update; B sets HTTP headers and uses a specific library (Jena).
- 修正建议: Incorporate data-flow analysis to track how the input stream content is used post-read.；Consider return type differences and the presence of library-specific calls (e.g., model.read).；Use larger context or graph representations that capture the semantics of the entire function beyond token overlap.

### case_id=2520 FP boilerplate_overlap

- 方法: `main` vs `genCustRatingFileAndMovieIndexFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file and generates adapter classes into a JAR file.
- B 摘要: Reads a binary rating file and generates separate index and rating output files.
- 静态失败原因: Possibly due to over-reliance on shared API usage (File, ByteBuffer, FileChannel) and exception handling patterns, leading the model to think they are similar when they are not.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the functions have entirely different purposes and structures, despite some superficial file I/O similarities.
- 共享行为: Both perform file I/O operations and write binary data to files；Both use try-catch for exception handling
- 行为差异: A processes Prolog source code to generate Java classes; B processes binary movie data；A is a main entry point; B is a private helper method；A has complex class generation and serialization logic; B has simple record parsing
- 修正建议: Improve handling of long-range semantics to differentiate domain logic；Incorporate functional type information；Use control flow analysis to distinguish high-level purpose

### case_id=2521 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint in the XML, and saves it to a temporary file, returning the file path.
- B 摘要: Copies a file from source to destination using FileChannel, creating directories if needed.
- 静态失败原因: Static models may focus on method names and overall control flow, which are quite different. The lexical overlap is low (0.1746), and the similar channel-copying logic is a small part of the code, easily overlooked by attention mechanisms. Additionally, BERT may not capture the structural similarity of the nested channel operations across different contexts.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions contain a core file copying operation using the same pattern (FileChannel.transferFrom), which is considered a partial functionality similarity (Type-3/Type-4). The overall context is different, but the shared sub-task drives the clone label.
- 共享行为: Both use FileChannel.transferFrom to copy data from an input channel to an output channel.；Both handle file I/O with try-finally blocks for resource cleanup.
- 行为差异: A downloads from a URL and modifies XML content; B only copies local files.；A has complex error handling with multiple exceptions; B only throws IOException.；A checks file existence and length before copying; B always tries to copy.；B creates parent directories; A does not.
- 修正建议: Use data-flow analysis to extract common sub-patterns like file channel copy.；Design a model that can match similar I/O idioms independent of surrounding code.；Incorporate knowledge of common file operation libraries (e.g., java.nio.channels).

### case_id=2522 FN partial_functionality

- 方法: `setBundleInfoName` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses a URL-accessible properties file to update bundle names in a list.
- B 摘要: Fetches and logs the entire content of a fixed URL.
- 静态失败原因: The static model likely relied on token overlap (Jaccard 0.149) and syntactic similarity, which are low, and failed to recognize the shared URL-reading pattern that BCB considered semantically similar.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'URL reading and line processing' clones due to the shared boilerplate of opening a URL and using BufferedReader, possibly ignoring the different processing logic.
- 共享行为: Both open a URL and read lines using BufferedReader.
- 行为差异: A returns boolean success/failure and modifies an input list; B is void and only logs.；A parses key-value pairs separated by '='; B reads all lines without parsing.；A explicitly sets UTF-8 encoding; B uses default encoding.；A handles IOException by printing stack trace; B throws Exception.
- 修正建议: Improve detection of common API usage patterns (e.g., URL.openStream, BufferedReader.readLine) across different tasks.；Incorporate program flow analysis to identify that both functions primarily read and process URL content.

### case_id=2523 FN partial_functionality

- 方法: `copyResource` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file path to a destination file by reading bytes one-by-one and closing streams.
- B 摘要: Copies bytes from an InputStream to an OutputStream using IOUtils.copyLarge, with error logging and stream closing in finally.
- 静态失败原因: Low token Jaccard (0.107) and differences in method signature, libraries, and error handling caused the model to focus on surface dissimilarity rather than the shared semantics of copying data.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels data-copying functions as clones even if implementations differ, as the core behavior (copying bytes) is semantically equivalent.
- 共享行为: Both copy bytes from an input source to an output sink；Both close the input and output streams after copying
- 行为差异: A resolves the source from a URL or local file; B takes pre-opened streams；A writes to a specific destination file; B writes to any OutputStream；A copies byte-by-byte manually; B uses buffered library method；A throws Exception on missing resource; B logs and throws FaultException on IO error
- 修正建议: Use dataflow or graph-based models that track the flow of data from input to output；Incorporate API call similarity (e.g., both read and write streams)；Train on pairs with similar high-level intent but different implementation details

### case_id=2524 FN benchmark_preference_bias

- 方法: `main` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its entries to the file system.
- B 摘要: Modifies a localized properties file by updating or appending a message key-value pair.
- 静态失败原因: Static BERT correctly predicted non-clone due to low token overlap and clear semantic differences. The model did not fail; the BCB label is questionable.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label may be a misannotation, as the functions share only generic file I/O structure but completely different functionality. Possibly an error in the benchmark.
- 共享行为: Both perform file I/O operations；Both use while loops to read data from input streams；Both handle exceptions via try-catch or throws
- 行为差异: A extracts multiple files from a ZIP archive; B modifies a single properties file；A uses network protocols (HTTP/file); B operates on local files only；A uses ZipInputStream and ZipEntry; B uses BufferedReader and FileWriter；A is a static main method; B is an instance method with parameters for locale, messageName, messageValue
- 修正建议: Review and correct BCB annotations for this pair；For static models, focus on semantic understanding beyond token overlap, but in this case the model was correct

### case_id=2525 FN partial_functionality

- 方法: `onlyFileCopy` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file using NIO FileChannel transferTo.
- B 摘要: Downloads a KMZ file from a URL, decompresses it, and saves entries to disk.
- 静态失败原因: Low token overlap and lexical differences cause the model to focus on distinct APIs (FileChannel vs ZipInputStream) rather than the shared high-level behavior of data transfer.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'file copying' operations because they transfer data from an input source to an output destination, accepting broad Type-4 similarity.
- 共享行为: Both perform file I/O operations that read from an input source and write to output files.
- 行为差异: A uses NIO FileChannel with transferTo; B uses buffered streams and ZipInputStream.；A copies a single file; B handles URL download, zip extraction, and multiple outputs.；A is a protected method; B is a public static main method.
- 修正建议: Incorporate dataflow analysis to identify common I/O patterns.；Train on more examples of functionally similar but syntactically different code pairs.

### case_id=2526 FN benchmark_preference_bias

- 方法: `doGet` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to display a page, checking permissions, logging, and optionally caching output to a file.
- B 摘要: Concatenates multiple input files into one output file using a command-line interface.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed to detect the clone because the functions are lexically and syntactically very different (low token Jaccard) and the abstract semantic similarity (I/O processing) is too broad and not captured by the model's focus on local syntactic patterns.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider this a broad Type-4 clone under high-level functional similarity: both functions take input and produce output (I/O operations), despite different domains and complexity.
- 共享行为: Both involve reading input (request parameters or file contents) and writing output (response or output file).
- 行为差异: Function A handles HTTP request/response lifecycle; Function B is a standalone file utility.；A involves complex logic for page retrieval, user permissions, logging, and caching; B simply reads lines and writes.；A writes to a network response; B writes to a file.；A uses exception handling and logging; B throws IllegalArgumentException.
- 修正建议: Incorporate functional role labeling to recognize high-level I/O patterns.；Use graph-based representations to abstract away domain-specific details.；Consider training on a wider range of clone types including broad Type-4.

### case_id=2527 FN partial_functionality

- 方法: `serialize` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Serializes an IMS content package to an output stream.
- B 摘要: Handles an HTTP GET request for a portal page, retrieves the page, checks permissions, and writes the page content to the response.
- 静态失败原因: Static BERT/GraphCodeBERT methods rely heavily on lexical and syntactic overlap (token Jaccard=0.0445) and cannot capture the high-level semantic similarity of 'outputting data' due to the vast difference in vocabulary, structure, and length. The model likely sees no surface-level matches and confidently predicts non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may annotate this as a Type-4 semantic clone because both functions are fundamentally about taking input, processing it, and writing output to a stream, albeit in very different domains. The broad goal of 'outputting data' could be considered partial functional similarity.
- 共享行为: Both functions output data to a stream (OutputStream or HttpServletResponse).；Both involve exception handling (IOException, etc.) and logging.；Both perform some form of parsing or lookup (package parsing vs page lookup).
- 行为差异: Code_a serializes a package to a file/stream; code_b serves a web page with authentication and caching.；Code_a is short and simple; code_b is long and complex with multiple branches and error handling.；Code_a reads from a temporary file; code_b reads from database/properties and uses request parameters.；Code_b involves user permissions and session management; code_a does not.
- 修正建议: Incorporate data flow or control flow graphs to capture structural patterns.；Train on more diverse Type-4 clone examples to learn abstract semantics.；Use a contrastive learning framework that emphasizes functional intent over lexical similarity.

### case_id=2528 FP lexical_or_api_overlap

- 方法: `loadURL` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: loadURL downloads content from a URL to a temporary file, with optional HTTP Basic authentication, and updates a GUI progress label with the file size.
- B 摘要: downloadModel downloads an RDF model from a URL by opening a connection, setting HTTP headers, and parsing the input stream into a Jena Model object.
- 静态失败原因: Static BERT models may focus on lexical and API-level similarities such as 'URLConnection', 'openConnection', 'getInputStream', 'IOException', leading to a false positive clone detection. They might miss the overall control flow and purpose differences, especially the distinct operations after reading: writing to file vs parsing into a model.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: None
- 共享行为: Open URL connection and read input stream；Handle IO exceptions；Ignore HTTP response status codes
- 行为差异: A writes data to a temporary file; B parses data into an in-memory Model object；A uses BASIC authentication; B sets Accept and Accept-Language headers；A updates a GUI label; B returns a Model；A is instance method; B is static
- 修正建议: Improve training data to include more examples where API overlap exists but semantic purpose diverges；Incorporate structural or dataflow analysis that captures the different outcome types (file output vs model object)；Use graph-based representations that better capture the different data flows

### case_id=2529 FN partial_functionality

- 方法: `copyFile` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from input to output using FileChannel.transferTo.
- B 摘要: Downloads a WSDL file from a URL, modifies its endpoint, and saves it locally, returning the file path.
- 静态失败原因: Static BERT models rely on token overlap and method names; low Jaccard (0.136) and different names ('copyFile' vs 'getFile') caused misclassification, missing the shared NIO channel usage.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers Type-4 clones where the core file channel transfer operation is similar, despite different overall functionality.
- 共享行为: Both use FileChannel for transferring data between streams
- 行为差异: Function B involves URL connection, XML parsing, and file modification, while A only copies；Function B has extensive logging and multiple exception types, A has minimal error handling；Function B creates and deletes temporary files, A directly copies
- 修正建议: Incorporate data flow and API usage patterns into model；Train on more Type-4 examples with partial functional overlap；Use graph-based representations to capture file channel operations

### case_id=2530 FP lexical_or_api_overlap

- 方法: `get` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches and decodes game records from a URL using HTTP GET.
- B 摘要: Checks for software upgrades by querying a remote license server and processing upgrade database.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on overlapping tokens such as 'URL', 'openConnection', 'BufferedReader', 'readLine', and the control flow pattern of reading lines, leading to a false positive based on lexical and structural similarity, while missing the high-level semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: None
- 共享行为: Both perform an HTTP GET request to a URL and read the response line by line using BufferedReader.
- 行为差异: Function A returns an array of GameRecord; Function B returns void and updates UI components and database.；Function A filters lines starting with '#'; Function B parses XML-like structure.；Function A is a simple data fetch; Function B involves license validation and upgrade logic.；Different URL construction: A uses parameters lat, lon, count; B constructs a complex URL with version, unit ID, MAC.
- 修正建议: Incorporate dataflow analysis to capture the overall data transformation and output.；Use contrastive learning to distinguish tasks with different goals.；Include more global context such as method signature, comments, or surrounding code.

### case_id=2531 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `getLinksFromURLFast`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a specific Twitter user timeline JSON feed via HttpClient and returns the response body as a string.
- B 摘要: Fetches a web page from a URL, extracts all hyperlinks from anchor tags using regex, and returns two vectors containing links and link texts.
- 静态失败原因: The high lexical overlap of common boilerplate patterns (BufferedReader, readLine, append) and similar structural steps (open connection, read lines) misled the model into thinking they are semantically equivalent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered these non-clones because the overall functionality is different: one reads a specific Twitter feed, the other extracts links from arbitrary web pages. The shared boilerplate of reading lines from a URL is not enough to consider them similar under BCB guidelines.
- 共享行为: Both open a URL connection and read the response line by line into a buffer.
- 行为差异: A uses HttpClient/HttpGet with specific Twitter API URL; B uses URL.openConnection with arbitrary URL.；A returns a single string of raw JSON content; B parses HTML to extract links and texts and returns two Vectors.；A is a private instance method; B is a public static method that throws Exception.；A catches specific exceptions; B does not catch exceptions.
- 修正建议: Incorporate output type awareness and method signature analysis.；Use data flow analysis to differentiate how the buffered content is processed.；Train on more diverse examples where boilerplate is not sufficient for clone classification.

### case_id=2532 FN partial_functionality

- 方法: `extractResourceToFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Extracts a resource from the classpath and copies it to a file.
- B 摘要: Launches a complex IDE configuration process involving Maven POM handling, profile management, and file resource extraction.
- 静态失败原因: Low token overlap and no shared API signatures beyond generic InputStream/OutputStream caused the model to miss the small functional overlap; it relied on lexical and structural matching.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: The sole commonality (IOUtils.copy usage) is a minor sub-operation in B; BCB may have labeled as clone due to partial functional overlap in resource extraction, though the overall tasks are distinct.
- 共享行为: Both read from an InputStream and write to an OutputStream using IOUtils.copy
- 行为差异: A is a simple utility; B is a multi-step configuration launcher encompassing XML parsing, property handling, and project operations；A has no conditionals or project context; B is deeply tied to Eclipse/IDE and NexOpen project structure；A's only output is a file; B's primary effects are project configuration and launching
- 修正建议: Improve detection of sub-task similarity via data flow analysis；Add capability to identify common utility patterns within larger methods

### case_id=2533 FN partial_functionality

- 方法: `ExternalDecoder` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Constructor that sets up an asynchronous copy from an input stream to a process's standard input.
- B 摘要: Method that downloads a resource from a URL, caches it to a file, and returns its input stream.
- 静态失败原因: Static BERT models rely on token overlap and structural similarity; the low Jaccard (0.089) and different method signatures led to a non-clone prediction. The model missed the broader I/O pattern that BCB prioritizes.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to the shared pattern of reading from an input stream and writing to an output stream with exception handling, which is a common I/O boilerplate. This aligns with BCB's tolerance for Type-3/4 similarity where functional goals differ but core data flow is similar.
- 共享行为: Both handle InputStream reading；Both involve writing to an OutputStream (process stdin or file)；Both include exception handling and stream closing
- 行为差异: Function A is a constructor that copies asynchronously; Function B is a synchronous method with caching；Function A writes to a process's stdin; Function B writes to a local file cache；Function A lacks caching and URL handling; Function B lacks process interaction
- 修正建议: Incorporate data flow analysis to capture stream copying patterns；Add features for I/O-related control structures (e.g., reading-writing loops)；Use contrastive learning on I/O-centric clone examples

### case_id=2534 FN partial_functionality

- 方法: `getResourceAsStream` vs `setup`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource as InputStream with local file caching and conditional download.
- B 摘要: Extracts native libraries from a JAR file to a temp directory and adds that directory to the library path.
- 静态失败原因: The model likely over-focused on lexical/API differences (e.g., HTTP vs ZIP, cache vs extraction) and missed the high-level similarity of resource management file I/O, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely annotated this as clone because both involve 'resource loading with file caching/extraction' as a broad Type-4 functional similarity, even though the exact purpose differs.
- 共享行为: Both perform file I/O operations (reading/writing streams)；Both use BufferedInputStream/OutputStream for efficiency；Both handle exceptions with try-catch blocks
- 行为差异: getResourceAsStream returns an InputStream for a given resource name; setup extracts native files and configures library path, no return value；getResourceAsStream has caching logic based on last-modified; setup unconditionally extracts ZIP entries from a JAR；getResourceAsStream uses HTTP connection logic; setup uses ZIP extraction；Different error handling: getResourceAsStream resets streams on exception; setup propagates exception
- 修正建议: Incorporate structural or control-flow features to distinguish high-level purpose；Use contrastive learning to penalize false negatives with low token overlap but shared I/O patterns；Add domain knowledge about resource loading vs library extraction

### case_id=2535 FN partial_functionality

- 方法: `doGet` vs `_checkLanguagesFiles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to retrieve and serve a page, with user authentication, caching, and error handling.
- B 摘要: Checks and copies language property files from global to temporary directory if they don't exist.
- 静态失败原因: Static method correctly identified non-clone due to low token overlap, different method names, and distinct API usage.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled as clone due to the shared pattern of file existence check and copy, overlooking the overall different contexts and purposes.
- 共享行为: Both may create or copy files conditionally based on existence check
- 行为差异: A is a complex servlet handler with authentication, caching, and logging; B is a simple file copy routine；A uses Property and Page objects; B uses list of Language objects；A interacts with HTTP request/response; B operates on local file system
- 修正建议: Improve clone detection to focus on full semantic equivalence rather than partial patterns；Use dynamic analysis or higher-level semantics to distinguish file operations in different contexts

### case_id=2536 FN partial_functionality

- 方法: `fileDownload` vs `readURL`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads content from a URL string and writes it to a fixed filename in a destination directory.
- B 摘要: Reads content from a URL object and prints each line to standard output.
- 静态失败原因: Static BERT models rely heavily on token overlap and syntactic structure; low Jaccard similarity (0.24), different method signatures, output statements, and resource handling led to a non-clone prediction, missing the high-level semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as Type-4 clones because the core functionality of reading from a URL is preserved; differences in output destination and parameter types are often tolerated in broad functional categories.
- 共享行为: Both open a URL and read its content using BufferedReader.；Both handle exceptions with logging or printing stack traces.
- 行为差异: A writes the content to a file ('download.pdf'), while B prints to console.；A uses a fixed output filename; B does not write to a file.；A reads character-by-character using read() and write(int), B reads line-by-line.；A has incomplete resource management (fails to close output stream), B properly closes all streams in finally block.
- 修正建议: Incorporate dataflow analysis to capture I/O patterns beyond surface tokens.；Use function role/context embeddings (e.g., API invocation sequences) to recognize shared purpose.；Train with more diverse Type-4 clone examples that differ in output sinks.

### case_id=2537 FN benchmark_preference_bias

- 方法: `write` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Writes ByteBuffer data through an SSL engine, handling handshake and encryption.
- B 摘要: Launches a NexOpen project configuration, setting up Maven POMs and Hibernate reverse engineering files.
- 静态失败原因: Static BERT model correctly predicted non-clone (token Jaccard 0.055); it did not fail but the BCB benchmark label is inconsistent.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to both functions involving I/O operations and exception handling, or due to a benchmark annotation error.
- 行为差异: Function A performs SSL/TLS encryption of byte buffers; Function B configures and launches a project in an Eclipse plugin.；Function A deals with low-level network I/O; Function B deals with file I/O and project metadata.；Function A returns encrypted ByteBuffer arrays; Function B returns void and modifies project resources.
- 修正建议: Re-evaluate BCB annotation for this pair; likely a mislabel.；No fix needed for static model; its prediction aligns with semantic content.

### case_id=2538 FP lexical_or_api_overlap

- 方法: `copyFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file from source to destination using a buffer, with an option to force overwrite.
- B 摘要: Handles UI actions in a settings dialog, processing commands to store preferences and update UI components.
- 静态失败原因: The static model likely over-relied on overlapping file-related tokens (e.g., 'File', 'IOException') and the presence of try-catch blocks, ignoring the large structural and semantic differences. The low Jaccard may have been offset by these high-weight tokens in the embedding.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when methods have distinct high-level purposes, even if they share low-level file-related tokens. Here, the lack of semantic overlap in functional behavior leads to a non-clone label.
- 共享行为: Both methods involve file operations: A copies file content, B selects file paths via JFileChooser.；Both use conditional checks: A checks if destination exists, B checks command strings.
- 行为差异: A is a file I/O utility with no UI interaction; B is a complex event handler with JFileChooser, preference storage, and UI updates.；A handles IOException explicitly; B catches SukuException and logs exceptions.；A has a try-finally block to close streams; B lacks such structured resource handling.；The overall purpose and logic are entirely different: copying vs. configuration management.
- 修正建议: Introduce more negative examples with lexical overlap but different semantics.；Use dataflow or graph-based models that capture read/write dependencies and control flow.；Incorporate method-purpose classification as a feature.

### case_id=2539 FN benchmark_preference_bias

- 方法: `getFile` vs `uploadFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its wsdlsoap:address endpoint, and saves it locally.
- B 摘要: Copies or moves a file from a source to a target location using rename or stream copy.
- 静态失败原因: The static model correctly predicted non-clone due to low token overlap and different method names/domains.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as file manipulation utilities with stream copying, but the distinct purposes and extra XML processing in A make them non-clones even under broad Type-3/4 criteria.
- 共享行为: Both perform file I/O with streams.；Both handle IOException.
- 行为差异: Function A involves network download and XML parsing/modification; Function B does not.；Function A uses NIO channels for copying; Function B uses byte array.；Function A writes to temp directory; Function B writes to user-specified target.；Function A has complex multi-exception handling; Function B only throws IOException.
- 修正建议: Incorporate domain-specific semantics to distinguish download+XML from simple file copy.

### case_id=2540 FP lexical_or_api_overlap

- 方法: `loadSourceCode` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads source code from a file and returns an HTML string with syntax highlighting.
- B 摘要: Checks for software upgrades by querying a database and a remote license server, then updates UI components accordingly.
- 静态失败原因: Static BERT models may over-rely on token-level similarities (e.g., both use BufferedReader, InputStreamReader, URL, and similar loop patterns) while missing the overall functional context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have entirely different purposes and no meaningful functional overlap beyond generic I/O boilerplate.
- 共享行为: Both use BufferedReader to read line by line from an input stream；Both handle exceptions with try-catch blocks
- 行为差异: A reads a local file; B reads from a URL connection and database；A produces an HTML string; B performs upgrade logic and updates UI；A uses CodeViewer for syntax highlighting; B does not；B manipulates UI components and executes database commands; A does not
- 修正建议: Use dataflow or control-flow analysis to distinguish I/O patterns from actual logic；Incorporate dataset-specific fine-tuning with emphasis on functional diversity；Apply hierarchical models that consider method-level semantics beyond token sequences

### case_id=2541 FN benchmark_preference_bias

- 方法: `getFile` vs `unzip`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint in the XML, and saves it to a temp directory.
- B 摘要: Extracts all entries from a zip file to a target directory, creating directories as needed.
- 静态失败原因: Static BERT models like GraphCodeBERT focus on token-level and syntactic overlap, and the low Jaccard similarity (0.138) led to a non-clone prediction. They failed to recognize the broader structural similarity that BCB's annotation prefers.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may accept these as clones because both follow a high-level pattern of downloading/extracting and transforming file content, with similar structure (check existence, create files, stream read/write, exception handling). This could be considered Type-4 (semantic) similarity under a generous interpretation.
- 共享行为: Both perform file I/O operations (create, read, write) with FileInputStream/FileOutputStream.；Both include logging for debugging and error reporting.；Both handle IOException and throw a custom exception (AxisFault/BusinessException).
- 行为差异: Code A retrieves content from a URL and modifies XML; Code B reads from a zip file and writes individual entries.；Code A has XML manipulation and temporary file renaming; Code B iterates over zip entries and handles directory creation.；Code A uses NIO channels for transfer; Code B uses a byte buffer loop.
- 修正建议: Incorporate higher-level structural patterns (e.g., file transformation pipeline) into the model.；Use a more flexible threshold for partial functionality clones.；Fine-tune on BCB's annotation style to capture Type-4 similarities.

### case_id=2542 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint in the XML, and returns the temporary file path.
- B 摘要: Copies a local file to a destination with optional overwrite using a specified buffer size.
- 静态失败原因: GraphCodeBERT likely failed due to low lexical overlap (Jaccard 0.1748), different method names, return types, and distinct high-level logic. It missed the structural similarity in the file I/O subroutines because they are implemented with different APIs (channels vs. byte buffer).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones based on partial functional similarity: both involve file copying with streams and error handling, which is a common pattern. The annotators might have focused on the I/O structure rather than the overall purpose.
- 共享行为: Both involve reading data from a source (URL stream or file) and writing to a file.；Both use file I/O streams and handle I/O exceptions.；Both perform logging around the operation.
- 行为差异: Function A downloads from a URL and involves XML parsing/manipulation, while B copies a local file directly.；Function A creates temporary files and modifies XML content, B does not.；Function A returns a String (file location), B returns void.；Function A uses NIO channels for transfer, B uses traditional byte buffer copying.
- 修正建议: Incorporate data-flow analysis to detect common sub-patterns like read-write loops across different APIs.；Train on clone pairs that include partial functional overlap, not just full semantic equivalence.；Use structure-based embeddings that capture control flow and data dependencies beyond lexical tokens.

### case_id=2543 FP lexical_or_api_overlap

- 方法: `issueCommandToServer` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends a command and capsule to a server via HTTP and reads the response.
- B 摘要: Imports sequences from a URL by parsing FASTA-like format.
- 静态失败原因: The static BERT model likely over-relied on lexical overlap of common Java I/O constructs (like InputStreamReader, BufferedReader, readLine) and similar code structure (try-catch, while loop), failing to capture the distinct high-level intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB label is 0 because these functions have no functional similarity; one is an HTTP client command, the other is a sequence file parser.
- 共享行为: Both read data from an external source line by line using Java I/O.
- 行为差异: One sends data to a server (HTTP POST), the other only reads data from a URL.；One uses URLConnection and writes to output stream, the other uses InputStream from URL.；One parses key-value pairs and JSON, the other parses lines starting with '>' and sequence data.；One returns a response string, the other stores sequences in lists.
- 修正建议: Incorporate method names and class context into the model.；Train on more diverse non-clone pairs with high lexical overlap but different semantics.；Use data flow analysis to distinguish input/output patterns.

### case_id=2544 FN other

- 方法: `doGet` vs `extractZipFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET request: retrieves a page parameter, checks user permissions, generates HTML response, and optionally caches the page.
- B 摘要: Extracts a ZIP file: reads a zip input stream, creates directories and files, and updates a progress text pane.
- 静态失败原因: The static BERT model correctly predicted non-clone based on very low token overlap and distinct API usage; the 'failure' is relative to an erroneous BCB label.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: This appears to be a misannotation in BCB; the methods have no meaningful semantic overlap, and BCB likely erred due to superficial similarity in exception handling and stream usage.
- 共享行为: Both use input streams and output streams；Both include error handling with try-catch；Both involve logging or progress updates
- 行为差异: A handles HTTP requests and user permissions; B extracts ZIP archive；A writes HTML response to HTTP output stream; B writes extracted files to file output streams；A uses portal server context and properties; B uses pure file I/O
- 修正建议: Re-annotate this pair as non-clone in the BCB dataset.；Audit the BCB annotation guidelines to avoid such false positives.

### case_id=2545 FP partial_functionality

- 方法: `getRequestContent` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens HTTP connection to a URL and returns the first line of the response.
- B 摘要: Opens a URL stream and parses FASTA sequences, populating internal lists of names and sequences.
- 静态失败原因: Static BERT might have focused on overlapping tokens like URL, InputStream, readLine, etc., and missed the structural and semantic differences in control flow and data processing. The token Jaccard is low (0.078), but maybe the model overemphasized shared API usage.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels as not clone because they perform entirely different tasks: one fetches a single line, the other parses multi-sequence data. Even though both involve URL I/O, the functionality and intent are distinct.
- 共享行为: Both open a URL connection/stream and read text data via InputStream/Reader.
- 行为差异: Function A reads only one line; Function B reads multiple sequences with parsing.；Function A returns the line; Function B populates instance variables.；Function A uses HttpURLConnection; Function B uses URL.openStream().；Function A is simple; Function B has complex parsing logic.
- 修正建议: Improve model's ability to distinguish between simple I/O and complex parsing by incorporating data flow or control flow analysis.；Include more examples of non-clones that share API but differ in overall logic.

### case_id=2546 FN partial_functionality

- 方法: `copyResource` vs `save`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file by reading bytes one by one.
- B 摘要: Writes a byte array to a file using IOUtils.copy with cleanup in finally block.
- 静态失败原因: Low token Jaccard (0.14) and lexical differences (method names, API calls, control flow) caused the static model to miss the higher-level similarity of both functions writing bytes to a file. The model overemphasized surface form over functional equivalence.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers them clones because both achieve the core functionality of copying data to a file, despite differences in input source and error handling. The broad Type-3/Type-4 annotation in BCB accepts such partial functional overlap.
- 共享行为: Both write data to a file via FileOutputStream.；Both handle IO exceptions.；Both eventually close input and output streams.
- 行为差异: A reads from external resource (URL or file), B takes in-memory byte array.；A uses manual byte-by-byte copy, B uses IOUtils.copy.；A does not use try-finally for close, B does with multiple close attempts.；A throws Exception, B throws IOException; B also creates parent directories.
- 修正建议: Incorporate data flow and API usage patterns to capture functional overlap.；Use contrastive learning with more diverse clone pairs.；Augment models with method names and comments for context.

### case_id=2547 FP boilerplate_overlap

- 方法: `readUNI` vs `startScript`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads tab-separated lines from a URL and adds id+desc to a vector, skipping the first line.
- B 摘要: Reads lines from a URL and appends them to dialog.script, beginning and ending a script block.
- 静态失败原因: The model may have overgeneralized the common pattern of opening a stream, reading lines, and closing, ignoring the distinct data processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the high-level purpose is different (data extraction vs script loading), despite the shared boilerplate of reading from a URL.
- 共享行为: Both open a URL stream and read lines；Both process each line in a loop；Both handle exceptions and close the stream
- 行为差异: Function A parses tab-separated fields, Function B reads whole lines；Function A populates a Vector, Function B modifies dialog.script；Function A skips header line, Function B does not；Error handling differs: A prints stack trace, B prints message and exits
- 修正建议: Train with more emphasis on semantic differences in the processing loop；Use dataflow analysis to differentiate variable usage

### case_id=2548 FN partial_functionality

- 方法: `testNetworkHTTP` vs `executeHttpGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: testNetworkHTTP makes multiple hardcoded HTTP GET requests for testing, discarding the response.
- B 摘要: executeHttpGet performs a single HTTP GET request to a given URI and returns the response as a JSONObject.
- 静态失败原因: Static BERT models like GraphCodeBERT often rely on token and structural similarity. The low Jaccard similarity (0.11) and different API usage (HttpURLConnection vs HttpClient) likely caused the model to predict non-clone. The model might not capture the shared high-level semantic of 'HTTP GET and read response' due to its focus on local token patterns and the absence of explicit data flow or global context.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both methods implement the core functionality of making an HTTP GET request and reading the response line by line, which is a common pattern. The specific differences (number of requests, return type, library used) may be considered less important under a broad Type-4 semantic similarity criterion.
- 共享行为: Both perform HTTP GET requests and read the response line by line using a BufferedReader.
- 行为差异: testNetworkHTTP makes multiple requests (6) while executeHttpGet makes one.；testNetworkHTTP discards the response; executeHttpGet parses it as JSON.；testNetworkHTTP uses HttpURLConnection; executeHttpGet uses Apache HttpClient.；testNetworkHTTP returns void; executeHttpGet returns JSONObject.
- 修正建议: Improve model to recognize higher-level semantic patterns such as HTTP GET operations.；Include more training examples of HTTP GET methods with different libraries and structures.；Use data flow analysis to capture that both methods read from an HTTP response stream.

### case_id=2549 FP lexical_or_api_overlap

- 方法: `executePost` vs `fetchUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Executes an HTTP POST request with parameters, reads response line by line with carriage returns, returns response string or null on error.
- B 摘要: Fetches content via HTTP GET, reads response line by line, returns content string or empty string on error.
- 静态失败原因: Static BERT likely overemphasized the shared boilerplate (URL creation, stream reading, line-by-line processing) and ignored the distinct HTTP method, parameter handling, and error return patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires significant functional similarity for Type-3/Type-4 clones. Here, the core functionality differs (POST with parameters vs plain GET), and error handling/output formatting differ, so BCB likely considers them non-clones.
- 共享行为: Both fetch content from a URL via HTTP；Both read response line by line using BufferedReader；Both return resulting string
- 行为差异: HTTP method: POST vs GET；A sends parameters and sets multiple headers; B does not；A appends carriage returns to each line; B does not；A returns null on exception; B returns empty string
- 修正建议: Incorporate method signature or HTTP method detection；Add data flow analysis for parameters vs plain URL；Train on more diverse HTTP-related code to learn method-specific patterns

### case_id=2550 FN benchmark_preference_bias

- 方法: `fileDownload` vs `setMembers`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a file from a given URL and saves it to a local directory with a fixed filename 'download.pdf'.
- B 摘要: Fetches an HTML page from a Trac URL, parses it to extract component and priority options from select elements, and stores them in class fields.
- 静态失败原因: Static models like GraphCodeBERT may overemphasize lexical overlap (e.g., URL, BufferedReader) and miss the divergent control flow and data dependencies, leading to a false negative prediction. However, in this case the model correctly identified non-clones, and the error is due to BCB's lenient annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The functions share the general concept of reading from a URL, which might be considered broad functional similarity under Type-4 semantic clones in BigCloneBench, even though their specific operations and purposes are different.
- 共享行为: Both open a URL connection and read from the input stream using BufferedReader.
- 行为差异: A writes the raw input to a file; B parses HTML line by line using regex.；A ignores the content structure; B looks for specific HTML tags and extracts option values.；A has a fixed output filename; B sets class-level string arrays based on parsed data.；Exception handling differs: A logs via Logger, B prints messages to stdout.
- 修正建议: Incorporate method names and documentation into the model to capture intent.；Use a more fine-grained semantic analysis that distinguishes between different types of URL-based operations.；Employ a large language model for reasoning about functional equivalence.

### case_id=2551 FN partial_functionality

- 方法: `readGeoParserResult` vs `callApiPost`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an XML request to a geo-parser service to extract place names with optional gazetteer IDs, with retries and error handling.
- B 摘要: Sends an HTTP POST request with parameters to a given API URL, handling timeouts and status codes, and returns the response stream.
- 静态失败原因: Low token overlap and different method names, libraries, and output types caused the model to miss the shared HTTP communication intent.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both functions perform network communication and data exchange, a common high-level functional pattern, despite different specifics.
- 共享行为: Both make HTTP requests to external services；Both handle response data；Both include error handling
- 行为差异: Different request formats (XML vs POST parameters)；Different output types (collection of tuples vs InputStream)；Different error handling (retries vs throwing exception)
- 修正建议: Use models that capture data flow and API usage patterns；Augment training data with low lexical overlap but similar functional intent pairs

### case_id=2552 FN lexical_or_api_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a ZIP file from a URL and extracts all its entries to files.
- B 摘要: Copies a single file from source to destination.
- 静态失败原因: Static BERT models rely heavily on lexical overlap and token embeddings, which are low here due to different method names, classes (ZipInputStream vs FileInputStream), and URL handling code. The model likely missed the structural similarity of the copy loop.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider this a Type-3 clone because both functions implement the core pattern of copying data from an input to an output stream, common in I/O operations.
- 共享行为: Both read bytes from an InputStream and write to an OutputStream using a buffer array.
- 行为差异: A extracts ZIP entries; B copies a single file.；A uses URL/HTTP protocol; B uses local file system.；A uses ZipInputStream; B uses FileInputStream.；Error handling differs: A throws Exception, B checks arguments.
- 修正建议: Train on more diverse I/O patterns without emphasis on method names.；Use graph-based representations to capture dataflow and control structure.；Add explicit token masking for common library class names.

### case_id=2553 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint in the XML, and saves it to a temporary file.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: Static BERT models rely on lexical overlap and local context; the low token Jaccard and different method names/structures prevent recognizing the shared FileChannel pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the core file-transfer operation (FileChannel.transferFrom) as a shared functional behavior, and both are utility methods for file I/O, thus labeling them as type-4 clones.
- 共享行为: Both use FileChannel.transferFrom to copy data between streams.
- 行为差异: getFile involves network download and XML parsing/modification; copyFile does not.；getFile handles multiple exceptions (AxisFault, etc.); copyFile only throws IOException.；getFile creates temporary files and renames; copyFile simply overwrites destination.
- 修正建议: Train models to recognize structural patterns beyond lexical similarity, e.g., using AST or data-flow graphs.

### case_id=2554 FP lexical_or_api_overlap

- 方法: `copyFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.99`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file from source to destination using NIO FileChannel.
- B 摘要: Handles various GUI action commands, including file selection for external tool paths and saving preferences.
- 静态失败原因: The model likely relied on lexical overlaps (e.g., 'File', 'filename', null checks) and overlooked the fundamental difference in program logic, possibly due to function B's length causing truncation or attention dilution.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they have entirely different purposes (file copy vs. GUI event handling) and minimal functional overlap.
- 共享行为: Both involve file operations: copying in A, selecting file paths in B.
- 行为差异: A performs actual file I/O to copy content; B only opens file chooser dialogs and stores file paths.；A is a utility method for file system operations; B is an event handler for a settings dialog.；A uses FileChannel for efficient transfer; B does not do any file content manipulation.
- 修正建议: Improve model's ability to capture long-range dependencies and control flow structure.；Incorporate data flow or graph-based representations to distinguish file I/O from UI event handling.

### case_id=2555 FN boilerplate_overlap

- 方法: `copyResourceToFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.5`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource file to a destination file using I/O streams with proper cleanup.
- B 摘要: Configures and launches an Eclipse job for a NexOpen project, involving multiple file operations, property handling, and XML processing.
- 静态失败原因: The static BERT model relied on token overlap and data flow analysis, which showed low similarity (low Jaccard) and different variable usage, leading to a non-clone prediction.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as a clone due to the presence of common boilerplate code for stream handling and error management, which can be considered a Type-3/Type-4 similarity pattern despite different overall functionality.
- 共享行为: Both involve file I/O operations with input and output streams.；Both use try-finally blocks for resource cleanup.
- 行为差异: Function A is a simple file copy utility; Function B is a complex launch method with many steps beyond file I/O.；Function B includes project-specific checks, property setting, XML handling, and job scheduling.
- 修正建议: Incorporate training examples that distinguish between genuine semantic clones and incidental boilerplate overlap.；Enhance representation learning to focus on high-level functionality rather than syntactic patterns.；Consider adding manual inspection or rule-based filtering for methods with high similarity in exception handling but low overall semantic match.

### case_id=2556 FP boilerplate_overlap

- 方法: `getRequestContent` vs `load`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads only the first line from a given URL and returns it.
- B 摘要: Reads all lines from a pastebin download URL constructed from an id and returns concatenated XML string with error handling.
- 静态失败原因: The model likely overemphasized the common boilerplate (URL, BufferedReader, InputStreamReader) and ignored the critical difference in loop structure and error handling, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled non-clone because the functions have different purposes (get first line vs. all lines) and different error handling, despite sharing boilerplate URL reading code.
- 共享行为: Both open an HTTP URL connection and use BufferedReader to read text.；Both return a String value.；Both close the reader after reading.
- 行为差异: A returns only the first line; B returns all lines concatenated.；A uses HttpURLConnection and explicitly disconnects; B uses URLConnection and url.openStream().；A has no error handling; B has try-catch for IOException and shows a dialog.；A takes a full URL as input; B constructs URL from an id.
- 修正建议: Train the model to differentiate between single-line and multi-line reading patterns.；Incorporate control flow features to capture loop vs. non-loop.；Use data flow analysis to track number of lines read.；Improve handling of exception handling differences.

### case_id=2557 FN partial_functionality

- 方法: `trainClassifier` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Executes an external training command by building a command line, running the process, and copying its output and error streams to standard output and error.
- B 摘要: Launches an Eclipse launch configuration for a NexOpen project by validating parameters, manipulating Maven pom files with ContentHandlerTemplate, handling Hibernate dialect and reverse engineering files, and scheduling an install project action.
- 静态失败原因: Static BERT models rely heavily on lexical and structural similarity; the low token Jaccard (0.044) and vastly different structures led them to correctly predict non-clone, but they missed the potential broad semantic overlap that BCB annotators might have recognized.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to the presence of IOUtils.copy and file path construction, considering them as high-level semantic clones involving stream copying and file handling, even though the domain and complexity differ greatly.
- 共享行为: Both use IOUtils.copy to copy input to output streams
- 行为差异: Core purpose: training a classifier vs. configuring an Eclipse project；Execution context: command-line process vs. Eclipse IDE plugin；Complexity: simple command execution vs. multi-step file manipulation and property handling
- 修正建议: Train models to recognize common utility patterns (e.g., IOUtils.copy) as functional building blocks that may indicate partial similarity；Incorporate data flow or API usage patterns beyond lexical overlap to capture shared stream-handling semantics

### case_id=2558 FP lexical_or_api_overlap

- 方法: `callService` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens a URL and reads all lines into a StringBuffer, storing the result in a field 'answer'; handles MalformedURLException and IOException.
- B 摘要: Opens a YouTube URL, reads lines to find 'fullscreenUrl', parses that line to extract video_id, t, title, constructs a full video URL, and returns it; updates progress and prints debug info.
- 静态失败原因: The static model may have been misled by the high lexical overlap of common patterns like URL, BufferedReader, InputStreamReader, readLine, etc. These are frequently co-occurring in network-related code, causing the model to overestimate similarity despite different semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the methods have different intended purposes (generic HTTP fetch vs. YouTube-specific URL extraction), different signatures, and only share boilerplate code. BCB often considers functional similarity, not just structural overlap.
- 共享行为: Both create a URL object and open a connection.；Both use BufferedReader to read lines from an InputStream.；Both close the reader after reading.
- 行为差异: Method a reads all lines (full content) and stores in a field; method b only reads until it finds a specific line containing 'fullscreenUrl'.；Method a returns void; method b returns a constructed URL string.；Method a has specific exception handling for MalformedURLException and IOException; method b uses a generic Exception catch.；Method b includes UI progress bar updates and extensive debug output.
- 修正建议: Add more weight to method signatures and return types.；Incorporate data flow analysis to distinguish reading all lines vs. conditional parsing.；Use contrastive learning with harder negative examples of boilerplate-only similarity.

### case_id=2559 FN partial_functionality

- 方法: `doGet` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: HTTP servlet handler that processes page requests, checks permissions, logs, and generates output, with optional caching to file.
- B 摘要: File copy utility that reads from a source file and writes to a destination file using a byte buffer.
- 静态失败原因: Static BERT models rely on token similarity and API usage patterns; low token Jaccard (0.057) and different API sets (Servlet vs. java.io) caused the model to miss latent functional similarity in stream copying that BCB annotators considered. Also, the model may not capture the partial functionality overlap (caching part in A) due to long-range dependencies.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to both involving reading from a source and writing to a destination (stream-based I/O) with error handling, possibly under a broad Type-4 category of 'file/stream copy' where the specific data source/sink are abstracted.
- 共享行为: Both perform I/O operations with exception handling；Both use try-catch/finally for resource management
- 行为差异: Function A involves HTTP request handling, user authentication, page rendering, and caching; Function B is pure file I/O.；A uses many external APIs (Servlet, Page, Property), while B uses only java.io.；A has complex logic for page resolution, visibility checks, and statistics; B is a straightforward loop.
- 修正建议: Use dataflow analysis to identify similar I/O patterns；Consider partial clone detection with functional decomposition；Incorporate more context-aware models that can match subroutines

### case_id=2560 FP boilerplate_overlap

- 方法: `readData` vs `WebmillDeploy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Initializes sets and maps from string tokens and a configuration file for a Tibetan text processing system.
- B 摘要: Constructs an object that processes a WAR file, parses XML, and creates a new WAR file for Webmill deployment.
- 静态失败原因: The model likely over-emphasized structural similarities like nested try-finally blocks and loops, and generic file reading patterns, while missing the vast difference in domain-specific logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these non-clones because the core functionality is entirely different despite some superficial similarity in file I/O patterns.
- 共享行为: Both involve file I/O and processing data from files/streams；Both have exception handling with try-catch-finally blocks
- 行为差异: Different input sources: static strings vs. constructor parameters and a JAR file；Different output: populating static collections vs. creating a WAR file；Different domains: text processing vs. web application deployment；Different data structures: HashSet/HashMap vs. JarFile/Document
- 修正建议: Improve model's ability to distinguish domain-specific logic from boilerplate；Add more training examples with different file I/O patterns but different purposes；Use more context-aware embeddings that capture high-level intent

### case_id=2561 FN benchmark_preference_bias

- 方法: `decodeFileToFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Decodes a Base64-encoded input file and writes the decoded content to an output file.
- B 摘要: Launches a NexOpen project configuration by parsing Maven POM files and setting up Hibernate reverse engineering.
- 静态失败原因: Static BERT models rely heavily on token overlap and semantic similarity; with a Jaccard of 0.067 and no shared high-level semantics, the model correctly predicted non-clone. It failed to match the BCB label because the BCB label appears inconsistent.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB annotator may have considered both as 'file processing' tasks due to shared use of I/O streams and file handling, but this is a very broad interpretation and likely a mislabel.
- 共享行为: Both perform file I/O operations using streams; both use try-finally blocks for resource cleanup.
- 行为差异: Function A is a simple file decoding utility; Function B is a complex Eclipse launch delegate with workspace and configuration handling.；A returns a boolean success flag; B is void and throws CoreException.；A uses Base64 decoding; B involves XML parsing, resource management, and property setting.
- 修正建议: Re-evaluate BCB annotation for correctness; if anchor is correct, incorporate domain-specific knowledge to recognize broad functional similarities; otherwise, improve benchmark consistency.

### case_id=2562 FP boilerplate_overlap

- 方法: `perform` vs `getRandomGUID`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Processes a classification request in a Struts action, handling session, parameters, and forwarding to success or failure.
- B 摘要: Generates a random GUID using MD5 hashing of time and random values.
- 静态失败原因: Static BERT may have been misled by overlapping boilerplate patterns like try-catch, StringBuffer usage, and method-level structure, despite low token Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have entirely different purposes and logic, even if they share some superficial code patterns.
- 共享行为: Both use try-catch blocks for exception handling；Both use StringBuffer for string building；Both involve encoding or hashing of strings
- 行为差异: A is a Struts ActionForward method handling HTTP request; B is a private no-return method generating a GUID；A has complex logic with session, request parameters, XML processing; B has simple random number and MD5 hashing；A returns an ActionForward; B sets instance variables valueBeforeMD5 and valueAfterMD5；A handles multiple conditions and forwards; B only has one conditional for secure flag
- 修正建议: Incorporate deeper semantic analysis beyond token overlap；Use data-flow or control-flow graphs to distinguish different behaviors

### case_id=2563 FP lexical_or_api_overlap

- 方法: `getFrameworkFactory` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads an OSGi FrameworkFactory from a service file using URL class loader.
- B 摘要: Downloads a URL with optional basic authentication and writes the content to a temporary file, updating a status label.
- 静态失败原因: Static BERT/GraphCodeBERT models may have overfocused on the lexical overlap of common API tokens (BufferedReader, InputStreamReader, URL, etc.) and missed the distinct high-level purposes. The partial structural similarity of reading lines from a URL could have triggered a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as not clones because their overall functionality is completely different: one is service loading, the other is file download. The shared use of BufferedReader and URL is too superficial to be considered a clone under BCB's annotation guidelines, which emphasize functional similarity.
- 共享行为: Both use BufferedReader and InputStreamReader to read from a URL connection.；Both open a URL and read lines in a loop.
- 行为差异: Function A returns an instance of FrameworkFactory; function B writes to a file and returns void.；Function A handles comments in the service file; function B handles authentication and progress display.；Function A throws Exception on failure; function B throws IOException and prints progress.；Function A uses Class.forName to instantiate; function B writes to a temporary file.
- 修正建议: Incorporate dataflow or program dependence analysis to capture the overall data transformation.；Train on more diverse negative examples that share API usage but differ in functionality.；Use contrastive learning with functional semantics rather than token-level similarity.

### case_id=2564 FP lexical_or_api_overlap

- 方法: `main` vs `unJar`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file, generates adapter classes, and writes them to a JAR file with serialized data and shared classes.
- B 摘要: Extracts a specific entry from a JAR file and saves it to a local directory path.
- 静态失败原因: The static model likely overemphasized lexical overlap of common terms like 'File', 'JarFile', 'IOException', and 'printStackTrace', and possibly structural similarity in try-catch blocks, leading to a false positive despite low Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have entirely different purposes and complexities; they share only trivial, common Java I/O and exception-handling patterns, which are not sufficient for clone classification.
- 共享行为: Both perform file I/O operations.；Both use try-catch blocks and print exception stack traces.
- 行为差异: Function A is a long, complex main routine with multiple steps (parsing, class generation, assembly).；Function B is a short, simple helper that extracts a single file from a JAR.；Function A handles Prolog parsing and class generation, while B handles JAR extraction only.；Function A writes multiple files (classes, resources); B writes a single file.
- 修正建议: Incorporate dataflow analysis to capture actual functionality.；Use function-length normalization to differentiate complex vs simple methods.；Weigh syntactic features with semantic role labeling to avoid trivial API overlaps.

### case_id=2565 FP lexical_or_api_overlap

- 方法: `createDialogArea` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Creates a dialog area that reads a license file from a bundle resource and displays its content in a Browser or Text widget.
- B 摘要: Extracts video parameters from a YouTube URL to construct a full download URL, with progress indicator updates.
- 静态失败原因: Static BERT/GraphCodeBERT models may over-rely on token overlap and common API sequences (URL, BufferedReader, while loop) without understanding the high-level semantic differences. The similar I/O structure and variable names (e.g., 'in', 'url') led to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions serve entirely different purposes (GUI dialog creation vs. URL construction), despite sharing some I/O boilerplate. The overall functionality and domain are distinct.
- 共享行为: Both use URL and URLConnection to open streams；Both read lines with BufferedReader in a loop；Both perform I/O operations with try-catch-finally blocks；Both manipulate strings to extract or construct data
- 行为差异: A builds a GUI component; B does not；A reads a local resource file; B reads a remote web page；A displays text in a widget; B constructs a URL string from parsed parameters；A handles multiple widget types (Browser or Text); B has no GUI involvement
- 修正建议: Incorporate data flow analysis to distinguish local file reads from web accesses；Use token-level attention with contextual embeddings that capture function purpose；Include negative examples with similar API usage but different domain intents during training

### case_id=2566 FP lexical_or_api_overlap

- 方法: `init` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Initializes controllers by loading class names from a registry file embedded in the classpath.
- B 摘要: Extracts a fullscreen video URL from a YouTube page by parsing the response and constructing a get_video URL.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the overlapping structural patterns (URL connection, BufferedReader, while loop) and missed the semantic context (servlet initialization vs. YouTube URL parsing). The token Jaccard similarity is low (0.144), but the model may have been misled by common API usage.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have completely different purposes: one is for controller initialization, the other for URL extraction. Despite similar low-level I/O patterns, the high-level semantics differ.
- 共享行为: Both use try-catch blocks for exception handling.；Both open a URL connection and read lines using BufferedReader.；Both iterate over lines and perform conditional checks.；Both log or print debug information.
- 行为差异: Function A reads class names from a file and loads classes via ClassLoader, while function B reads HTML to extract specific parameters.；Function A writes to logging, function B uses System.out.println.；Function A is a void init method for servlet context, function B returns a constructed URL string.；Function A adds classes to a registry, function B does not add any objects.
- 修正建议: Incorporate data flow analysis to track the purpose of output variables.；Use function names and surrounding context (method names, parameters) to disambiguate.；Train on more diverse examples of boilerplate-heavy code to avoid over-reliance on common API sequences.

### case_id=2567 FN benchmark_preference_bias

- 方法: `testStandardTee` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Tests TeeWriter by copying a string to multiple writers and verifying the output.
- B 摘要: Launches a NexOpen project configuration, handling file checks, XML profiles, properties, and project installation.
- 静态失败原因: Low token overlap (Jaccard 0.0588) and different contexts misled the model into predicting non-clone, which aligns with low functional similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label might be due to the shared IOUtils.copy usage, but the overall functionality is vastly different; annotation may be an error.
- 共享行为: Both use IOUtils.copy for stream copying
- 行为差异: A is a simple unit test; B is a complex launch handler；A has no project or file existence checks; B does extensive file operations；A asserts string equality; B throws exceptions and manages project resources
- 修正建议: Review BCB annotation for consistency; consider if IOUtils.copy usage alone justifies a clone label.；Improve model's ability to recognize that shared API calls do not imply functional equivalence.

### case_id=2568 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: GUI event handler that processes various configuration commands via file chooser dialogs and updates UI preferences.
- B 摘要: Utility function that copies a file using FileChannel.
- 静态失败原因: The model likely overemphasized common keywords like 'File', 'if', and 'return', despite very low Jaccard similarity, possibly due to overfitting on superficial lexical patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they have completely different purposes and behaviors; one is an event-driven UI method, the other is a low-level file utility, with no functional overlap.
- 行为差异: Function A is a complex GUI event handler with branching logic for multiple commands; Function B is a straightforward file copy.；Function A involves user interaction through dialogs; Function B has no user interaction.；Function A sets application preferences and updates UI components; Function B only performs file I/O.
- 修正建议: Increase diversity in non-clone training pairs with low token overlap.；Incorporate structural features (e.g., AST or dataflow) to better capture functional differences.

### case_id=2569 FN partial_functionality

- 方法: `getFile` vs `downloadFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies its endpoint, and returns the file path.
- B 摘要: Downloads a file from S3, decrypts and decompresses it, and saves it to a local file.
- 静态失败原因: Static BERT models rely on token overlap and syntactic structure; low similarity (0.113) and different API calls led the model to miss the shared high-level functionality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a Type-4 (conceptual) clone because both functions achieve the high-level goal of downloading a remote file to local storage, despite differences in protocol, processing, and output.
- 共享行为: Both download a remote file to the local filesystem；Both handle exceptions；Both use input/output streams
- 行为差异: A uses HTTP URL and processes XML; B uses S3 with decryption；A returns file path as String; B writes to a given File object；Different error handling and exception types
- 修正建议: Incorporate dataflow analysis to capture remote-to-local file transfer semantics；Use contrastive learning on functional similarity across different API implementations

### case_id=2570 FN benchmark_preference_bias

- 方法: `getFile` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its wsdlsoap:address endpoint attribute, and saves it locally, returning the file path.
- B 摘要: Reads a DICOM image file, parses it, reads pixel data, and writes it to an output file.
- 静态失败原因: The static model correctly predicted non-clone due to extremely low lexical overlap (Token Jaccard 0.072) and entirely different APIs, but BCB considers them similar, causing a false negative error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone under a very broad Type-4 interpretation, considering both as 'read-modify-write' functions, despite entirely different domains and logic.
- 共享行为: Both perform file I/O using streams and handle IOException.
- 行为差异: Different input types (String/URL vs File)；Different output (String vs void)；Different data formats (WSDL/XML vs DICOM)；Different operations (XML attribute modification vs pixel data copying)
- 修正建议: Use a representation that captures abstract workflow structure beyond lexical tokens.；Consider functional similarity measures that account for domain-specific operations.

### case_id=2571 FP other

- 方法: `encrypt` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Encrypts a plain text string using SHA-1 hash and Base64 encoding.
- B 摘要: Handles an HTTP request for concept classification, involving form processing, XML, and URL connections.
- 静态失败原因: Static BERT models may over-rely on superficial similarities like exception handling patterns, string operations, or common Java idioms, ignoring the fundamentally different purposes.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels Type-1/2/3/4 clones; these functions have no functional overlap, so BCB correctly labels as non-clone.
- 行为差异: Function A performs cryptographic hashing; Function B processes web requests and business logic.；Function A has no I/O or networking; Function B uses HTTP and XML.；Function A returns a string; Function B returns an ActionForward.；Function A is synchronized; Function B is not.
- 修正建议: Improve model's understanding of method purpose via semantic role labeling.；Use larger context or whole-method embeddings to capture high-level intent.；Incorporate data-flow analysis to distinguish cryptographic vs. web processing APIs.

### case_id=2572 FP boilerplate_overlap

- 方法: `doVersionCheck` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs a version check by fetching and parsing a build version file from a URL, then calls another method with extracted versions.
- B 摘要: Reads a tab-separated file from a URL, parses each line into an ID and description, and adds them to a vector.
- 静态失败原因: The model likely focused on lexical/API overlap (URL, openStream, while loop, line reading) and missed the semantic differences in parsing and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB expects functional similarity; the only commonality is the boilerplate of reading from a URL, but the core logic and purpose differ, so BCB would label non-clone.
- 共享行为: Both open a URL stream and read lines；Both handle I/O exceptions；Both close the input stream
- 行为差异: Different parsing logic: A looks for specific prefixes, B uses tab delimiters；Different output: A calls another method, B modifies a vector；Different error handling: A shows error dialog, B prints stack trace or catches silently
- 修正建议: Incorporate method name or class context to capture purpose；Improve representation of control flow and data dependencies to distinguish different parsing patterns

### case_id=2573 FP boilerplate_overlap

- 方法: `toMd5` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes MD5 hash of input string, returning hex-encoded digest.
- B 摘要: Processes a web request to classify a concept, performing HTTP communication and XML parsing.
- 静态失败原因: Despite low token Jaccard, the model may have been misled by superficial similarities such as exception handling blocks, loops with StringBuffer, and common Java idioms. The model likely over-generalized from patterns in training data where such boilerplate code indicated clone pairs.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotation typically requires some shared functional logic or code-level similarity. These two functions have completely different purposes and contexts, so BCB would not consider them clones.
- 共享行为: Both are public Java methods；Both use try-catch exception handling；Both contain loops that iterate over arrays/lists
- 行为差异: toMd5 is a static utility function; perform is an instance method in Struts Action class；toMd5 takes a single String and returns a String; perform takes multiple objects (ActionMapping, ActionForm, etc.) and returns ActionForward；toMd5 performs cryptographic hashing; perform does HTTP request/response and session management；toMd5 has no side effects beyond console output; perform modifies session attributes and makes network calls
- 修正建议: Enhance model with control-flow and data-flow awareness；Use type information and API call sequences to distinguish cryptographic utility code from web action code；Expand training data to include more diverse non-clone pairs with similar boilerplate

### case_id=2574 FN benchmark_preference_bias

- 方法: `doGet` vs `transferWSDL`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET requests for portal pages, managing user sessions, page visibility, logging, caching, and error handling.
- B 摘要: Downloads a WSDL file over HTTP, saves it to a temporary file, and returns the file path.
- 静态失败原因: A static BERT model likely correctly identified low token overlap and different API usage, thus predicting non-clone. However, BCB's label may be erroneous or based on a different notion of similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to both involving HTTP GET operations and file handling, but their purposes and implementations are vastly different, indicating a broad interpretation of similarity.
- 共享行为: Both perform HTTP GET requests；Both handle exceptions and errors
- 行为差异: Function A is a servlet handler that interacts with a portal system, user sessions, and page objects; Function B downloads a remote file and writes to disk.；Function A sends HTTP responses; Function B returns a file path string.；Function A involves complex logic for page visibility, caching, and logging; Function B is a simple file download.；The data types and libraries used are completely different (HttpServletRequest vs URL, Page vs File).
- 修正建议: Re-evaluate BCB annotation for this pair to ensure consistency.；Use more precise semantic similarity measures beyond token overlap.；Consider context-aware embeddings that capture high-level purpose.

### case_id=2575 FP lexical_or_api_overlap

- 方法: `copy` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file using NIO channels with proper resource cleanup.
- B 摘要: Handles GUI events to configure application settings and paths for various tools.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized lexical overlap (like 'FileInputStream', 'FileOutputStream', 'FileChannel') and the try-finally structure, mistaking boilerplate for semantic similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones (0) because they have completely different functionality, no shared algorithmic or semantic core, and the only overlap is trivial use of standard library classes.
- 共享行为: Use of File-related classes；Exception handling with try-catch-finally
- 行为差异: Function A is a utility method for file copying; Function B is a GUI event handler；Function A focuses on I/O streams and channels; Function B handles user commands and updates UI components；Function A has a deterministic, single-purpose flow; Function B has multiple conditional branches for different commands
- 修正建议: Improve handling of boilerplate structures like try-finally blocks；Add more weight to method signature and purpose；Use finer-grained tokenization to distinguish API usage contexts

### case_id=2576 FP lexical_or_api_overlap

- 方法: `loadURL` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a VRML file from a URL with optional HTTP basic authentication and writes it to a temporary file while updating a progress label.
- B 摘要: Checks for software upgrades by querying a license server with client version/ID/MAC, parsing XML-like responses, updating a local database, and showing UI notifications.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-relied on overlapping API calls (URLConnection, BufferedReader, readLine loops) and ignored the drastically different control flow, data usage, and overall goal.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the functions have entirely different purposes and only share superficial I/O patterns, not functional similarity.
- 共享行为: Both open a URLConnection and read line by line from the input stream.
- 行为差异: Function A downloads a file and writes to a temporary file, while Function B processes license/upgrade data and updates a database.；Function A uses basic authentication, while Function B constructs a URL with query parameters.；Function A updates a status label with file size, while Function B manipulates UI component visibility and shows message dialogs.；Function B includes complex database operations, conditional logic, and XML parsing not present in A.
- 修正建议: Incorporate method name semantics or broader context (e.g., class hierarchy).；Use data-flow analysis to distinguish different output sinks (file vs. database).；Train on contrastive examples that penalize false positive pairs with only trivial API sharing.

### case_id=2577 FN partial_functionality

- 方法: `readGeoParserResult` vs `handledRun`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads and parses geographic parser results from a web service, retrying up to 3 times on failure.
- B 摘要: Downloads and updates game data file from a URL if a newer version is available, handling network and IO exceptions.
- 静态失败原因: Static BERT/GraphCodeBERT relies on token-level similarity and structural features like AST. The low token Jaccard (0.13) indicates very different vocabulary and code structure. The model probably focused on the lack of overlapping tokens and distinct method signatures, outputting non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as clone due to broad functional similarity: both functions perform network data retrieval, parsing, and error handling, considered as Type-4 (semantic) clones. The annotation may prioritize the common pattern of reading from a URL, parsing content, and handling exceptions, despite different specific domains and operations.
- 共享行为: Uses URL to open network input stream；Uses BufferedReader to read data from stream；Contains try-catch for exception handling；Performs some data parsing (XML vs header parsing)
- 行为差异: Function A parses XML to extract place names and IDs, while Function B reads header lines to check version and conditionally writes binary data to a file.；Function A has explicit retry loop (3 attempts); Function B does not retry.；Function A is static and returns a collection; Function B is void and modifies a game database.；Function A uses DocumentHelper for XML; Function B uses simple line reading and byte writing.
- 修正建议: Improve model to incorporate higher-level semantic patterns like network IO operations and exception handling structure.；Use dataflow analysis to capture that both functions read from URL and process data.；Train on broader clone definitions including Type-4, but careful with over-generalization.

### case_id=2578 FP lexical_or_api_overlap

- 方法: `getTicketsForQueue` vs `handledRun`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a list of ticket IDs from a request tracker queue via HTTP GET, then retrieves each ticket's details.
- B 摘要: Downloads an updated gamedata XML file from a remote URL if the local version is outdated.
- 静态失败原因: Static BERT or GraphCodeBERT likely overemphasized the structural similarity of I/O patterns (BufferedReader, try-catch, resource closing) and ignored the domain-specific semantics, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled these as non-clones because the high-level functionality (ticket retrieval vs game data update) is entirely different, despite sharing similar I/O boilerplate.
- 共享行为: Both perform network I/O to fetch remote data；Both use BufferedReader/InputStreamReader to read text data；Both handle exceptions and logging/error messages
- 行为差异: Function A queries a REST API with parameters; Function B opens a direct URL stream；Function A parses ticket IDs from lines; Function B reads version info from header lines；Function A retrieves individual tickets after getting IDs; Function B writes downloaded data to a file；Function A deals with multiple tickets; Function B deals with a single versioned file
- 修正建议: Incorporate method names and class context into embeddings；Use contrastive learning to distinguish boilerplate from core logic；Add attention to domain-specific API calls (e.g., getTicket vs URL opening)

### case_id=2579 FN benchmark_preference_bias

- 方法: `getFile` vs `streamContains`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies the endpoint, and returns the file path.
- B 摘要: Checks if an InputStream contains a given substring, used for testing.
- 静态失败原因: The static BERT model correctly predicted non-clone due to low token overlap and different method names; the error is from the BCB ground truth, not the model.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label of 1 may be a benchmark error or due to overly broad notion of 'functionality similarity' (both involve I/O and string processing), but there is no meaningful semantic overlap.
- 共享行为: Both involve reading data from a source and processing it
- 行为差异: A writes to files and modifies XML; B only asserts string containment；A returns a file path; B has no return value；A handles multiple exceptions; B only throws IOException；A is a static utility method; B is a private instance method
- 修正建议: Verify BCB label correctness; consider removing outlier pairs with very low similarity

### case_id=2580 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: modifies a property in a locale-specific properties file, copying the English file if the target does not exist
- B 摘要: copies a file or directory recursively, creating the target if needed
- 静态失败原因: Static BERT models rely on lexical and syntactic overlap; low token Jaccard (0.15) and distinct method names lead to non-clone prediction, failing to capture the shared file-copying behavior
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider partial functional overlap (file copying when target missing) sufficient for a Type-4 clone, grouping them under broad file I/O operations
- 共享行为: both check file existence and create new file if not exists；both involve file copying when destination is missing
- 行为差异: A is specialized for .properties file modification with key-value parsing, B is generic recursive copy；A only copies a single English file as a fallback, B copies entire directories；A modifies file content (string replacement), B copies bytes unchanged；A handles locale and message name, B handles directory recursion
- 修正建议: improve training data with more diverse functional similarity annotations；use dataflow or program dependency analysis to identify common sub-tasks

### case_id=2581 FP other

- 方法: `ExternalDecoder` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Constructor that initializes external process I/O and starts a thread to copy input stream to process output stream.
- B 摘要: Event handler that processes GUI action commands, opening file choosers and updating application preferences and UI components.
- 静态失败原因: The static BERT model likely focused on superficial similarities such as the presence of exception handling (IOException, ActionEvent) or the use of streams, but ignored the overall semantics. The low token Jaccard (0.0556) suggests that the model might have been misled by rare shared tokens or context windows that captured non-informative patterns.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels clones based on functional similarity. These functions have completely different functionalities, so they would not be considered clones even under broad Type-4 tolerance.
- 行为差异: Function A deals with external process I/O and threading, while Function B handles GUI events and user preferences.；Function A uses IOUtils for stream copying, whereas Function B uses JFileChooser and application-specific controllers.；Function A is a constructor, Function B is an event listener method.；No overlap in logic or purpose.
- 修正建议: Incorporate more comprehensive structural analysis (e.g., control flow graphs, data dependency) to differentiate unrelated functionalities.；Use contrastive learning with hard negative examples to reduce false positives from superficial similarities.；Augment training data with diverse non-clone pairs that share exception handling or I/O operations but have different purposes.

### case_id=2582 FP lexical_or_api_overlap

- 方法: `loadMFileViaWeb` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a MATLAB function from a web URL, reads the source code, parses it into a UserFunction object, and returns it.
- B 摘要: Imports sequences from a selected URL, parses sequence names and sequences from a FASTA-like format, and stores them in lists.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the lexical overlap in URL reading and stream handling (e.g., 'URL', 'openStream', 'InputStream', 'readLine'), leading to a false positive. The models may have missed the distinct domain-specific parsing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because despite sharing the boilerplate of opening a URL stream and reading lines, the core functionality (parsing MATLAB functions vs. importing sequences) and output are completely different.
- 共享行为: Both open a URL stream and read text data line by line using standard Java I/O.
- 行为差异: Function A parses the entire text as MATLAB source code and returns a UserFunction; Function B parses sequences in FASTA format and populates lists.；Function A uses BufferedReader; Function B uses ImportHelper with custom readSequence method.；Function A sets the function name and returns; Function B adds names and sequences to ArrayLists.；Error handling differs: Function A catches Exception, Function B catches specific exceptions.
- 修正建议: Train with more diverse negative examples that share common API calls but differ in business logic.；Incorporate control-flow or data-flow features to distinguish parsing stages.；Use contrastive learning to penalize false positives from API-level similarities.

### case_id=2583 FP boilerplate_overlap

- 方法: `run` vs `startScript`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a tile from a URL, parses geometry, and adds to data loader.
- B 摘要: Loads a script from a URL and appends to dialog.
- 静态失败原因: It likely over-weighted the structural similarity of the I/O boilerplate and ignored the distinct post-processing and context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered the core functionality different: one is a tile data pipeline, the other is a script loader; the I/O pattern is common but not sufficient for clone.
- 共享行为: Both read from a URL using BufferedReader, read lines sequentially, and concatenate them into a string.
- 行为差异: A handles file and http, uses synchronization, processes geometry after reading; B only http, no synchronization, exits on IO error, no post-processing.
- 修正建议: Include structural context like the overall method purpose, data structures used, and error handling behavior; use data flow analysis to differentiate.

### case_id=2584 FN benchmark_preference_bias

- 方法: `main` vs `getResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to files.
- B 摘要: Parses an HTTP request byte array and returns the appropriate HTTP response with the requested resource.
- 静态失败原因: The static BERT model correctly predicted non-clone (0) because the semantic gap is large; the miss in the case comes from BCB's label being inaccurate, not the model.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled this as a clone due to superficial similarity in I/O operations and stream handling, despite fundamentally different purposes.
- 共享行为: Both read input streams and write output streams；Both use try-catch for IOException
- 行为差异: Function A handles zip extraction from a network stream; Function B implements HTTP response logic；Function A writes to files; Function B returns a byte array；Function A uses ZipInputStream; Function B uses ByteArrayInputStream and PrintStream
- 修正建议: Re-evaluate this pair in the benchmark; it should be labeled as non-clone (0).；Improve BCB annotation guidelines to avoid labeling based on weak I/O pattern overlap.

### case_id=2585 FN lexical_or_api_overlap

- 方法: `PageLoader` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads entire content from a URL using java.net and stores in instance variable.
- B 摘要: Sends HTTP POST request with parameters using Apache HttpClient and returns response body as string.
- 静态失败原因: Low token Jaccard (0.13), different API calls (java.net vs Apache HttpClient), and divergent control flow (while condition) cause the static model to miss the semantic similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often considers pairs with similar functionality (e.g., HTTP client reading response body) as clones, even with different libraries or HTTP methods, treating them as Type-3 or Type-4.
- 共享行为: Both perform HTTP requests and read response body into a string using BufferedReader.
- 行为差异: A uses GET (default), B uses POST.；A uses java.net.URL, B uses Apache HttpClient.；A reads with while(ready()) (may miss data), B uses standard while((line=...)!=null).；A sets instance variable inputLine, B returns string.
- 修正建议: Enhance representation to capture functional similarity like HTTP client behavior.；Use dataflow analysis to abstract common patterns (e.g., read from URL stream).；Include API-agnostic features (e.g., 'HTTP request', 'BufferedReader read loop').

### case_id=2586 FN partial_functionality

- 方法: `getHTML` vs `getWebPage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a URL using HttpURLConnection, optionally writes to a file, and returns the content as a string.
- B 摘要: Fetches web page content from a URL using URL.openStream() and returns it as a string.
- 静态失败原因: Static BERT/GraphCodeBERT models often rely on token-level and structural overlap. Here, the token Jaccard is low (0.165), method names differ, and the code structures (HttpURLConnection vs. URL.openStream(), file writing option) are distinct, causing the model to miss the semantic similarity in the core web-page retrieval functionality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may annotate as clone because both functions perform the core task of retrieving web page content as a string, which is considered functionally similar despite differences in HTTP connection method, error handling, and additional file-writing capability. BCB's Type-3/4 definitions allow for such variations.
- 共享行为: Both retrieve web page content from a URL as a string；Both read lines from an input stream and accumulate them
- 行为差异: Function A uses HttpURLConnection with custom User-Agent; Function B uses URL.openStream()；Function A can optionally write the content to a file; Function B does not；Function A handles exceptions by printing stack trace; Function B throws an Error with a custom message；Function A uses StringBuilder; Function B uses string concatenation
- 修正建议: Use data-flow analysis to capture that both functions produce a string from a URL input；Train on more diverse clone pairs that include variations in HTTP library usage and error handling；Incorporate abstract syntax tree (AST) or code graph representations to abstract over API choices

### case_id=2587 FN partial_functionality

- 方法: `getFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Gets or creates a file in the user's home directory by copying from classpath resource if not present, and returns the File object.
- B 摘要: Returns an InputStream for a named resource, caching it locally from a URL with HTTP conditional GET and debug output.
- 静态失败原因: The static model likely relied on lexical/syntactic similarity (low token Jaccard) and missed the high-level functional similarity of resource caching. It may not capture long-range dataflow patterns or abstract semantics like 'cache local copy from remote' across different APIs.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider these as Type-4 clones because both perform resource caching: check local existence, download from remote, and return a handle. The differences in parameters, return types, and protocols may be seen as partial functionality similarity.
- 共享行为: Both functions ensure a local copy of a resource exists before returning a handle to it.；Both involve downloading a resource from a remote location and saving it to a local file.；Both use classpath or URL-based resource access and file I/O.
- 行为差异: Function A takes no arguments and uses a fixed file prefix; Function B takes a resource name parameter.；Function A returns a File object; Function B returns an InputStream.；Function A throws an exception if resource not found; Function B returns null.；Function B implements HTTP caching with If-Modified-Since and conditional GET; Function A only copies once.
- 修正建议: Include more training examples of Type-4 clones with different method signatures but similar caching logic.；Enhance model to recognize control-flow patterns like check-cache-then-download independently of API details.；Incorporate structure-aware features that abstract over return types and parameter differences.

### case_id=2588 FN benchmark_preference_bias

- 方法: `main` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Main method creating a signed PDF using iText library with certificate handling and signature verification.
- B 摘要: doGet method processing HTTP requests to render a portal page with access control and caching.
- 静态失败原因: Static BERT correctly identified them as non-clones; the BCB label appears to be an annotation error or extremely broad interpretation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have considered both as 'utilities' with complex exception handling and I/O, but this is a very broad interpretation likely not intended for Type-3/Type-4 clones.
- 共享行为: Both use try-catch blocks for exception handling；Both perform I/O operations (file or network)；Both include logging or printing output
- 行为差异: A focuses on PDF signing/certificates; B on HTTP request handling and page rendering；Different libraries: iText vs servlet/jsp internals；A is a static main; B is a servlet doGet method；Control flow and data structures are entirely distinct
- 修正建议: Re-annotate the pair as non-clone in the benchmark；Use stricter guidelines for Type-4 clones to avoid false positives

### case_id=2589 FP lexical_or_api_overlap

- 方法: `addQDInformation` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a QD info file from local or remote URL and updates internal project information structures.
- B 摘要: Performs a Google image search, parses the HTML response to extract image URLs, and updates a GUI component with the first image.
- 静态失败原因: The model likely over-relied on lexical and API overlaps (e.g., URL, BufferedReader, InputStreamReader, try-catch) and control flow similarity (while read line, string parsing), missing the divergent semantic intent indicated by method names and the specific data being processed.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the methods have entirely different semantic purposes (configuration loading vs. image search) despite some structural similarity in I/O handling.
- 共享行为: Both methods open a URL or file and read text line by line.；Both use BufferedReader and InputStreamReader to read input.；Both parse the read lines to extract specific data and update internal data structures.；Both handle I/O exceptions with try-catch blocks.
- 行为差异: A reads a proprietary file format (pg, pt lines) for QD information; B reads HTML response from Google image search.；A updates internal Information objects; B updates a GUI (MusicBoxView) component.；A has conditional logic to read from local file or URL based on a local flag; B always uses an HTTP URL.；A checks file modification timestamps; B does not.
- 修正建议: Incorporate method name semantics into the representation.；Use finer-grained semantic analysis to differentiate between similar I/O patterns with different business logic.；Consider the types and structures of data being processed (e.g., file format vs. HTML).；Reduce weight on common API sequences in favor of higher-level program structure.

### case_id=2590 FN partial_functionality

- 方法: `main` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a fixed URL, unzips it, and extracts all entries to the current directory.
- B 摘要: Downloads all files from an HDFS directory and concatenates them into a single local file.
- 静态失败原因: Low token overlap (Jaccard 0.17) and differing method signatures caused GraphCodeBERT to miss the underlying streaming pattern; the model likely focused on surface-level differences rather than the abstract I/O flow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'file copy' operations involving reading from a source and writing to a destination, thus labeling them as Type-4 clones despite different sources and output structures.
- 共享行为: Both open input and output streams；Both loop over multiple files/entries；Both close streams in finally blocks
- 行为差异: Function A downloads from a specific HTTP URL; function B reads from HDFS based on CLI args；Function A extracts a zip archive; function B concatenates raw file contents；Function A creates separate output files per entry; function B writes to a single output file；Function A lacks error handling; function B checks arguments and directory status
- 修正建议: Enrich training data with more diverse streaming examples；Incorporate data-flow analysis to recognize common I/O patterns；Use contrastive learning to highlight structural versus lexical similarity

### case_id=2591 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft handshake by validating username and performing session verification via HTTP request.
- B 摘要: Performs version check for jEdit by fetching a URL and parsing version strings from lines.
- 静态失败原因: Static BERT models often rely on lexical and API overlap; here the common use of URL, BufferedReader, and similar structure (try-catch, reading lines) led to false positive, ignoring the fundamental semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have different domain-specific logic and purpose, even if they share common API usage patterns.
- 共享行为: Both use URL and BufferedReader to read content from a URL；Both have try-catch blocks for IOException；Both process lines read from an InputStream
- 行为差异: A validates a hex string and sends login packets, B parses specific line prefixes and delegates to another method；A disconnects on invalid input, B shows/hides wait cursor and handles errors differently；The purpose is completely different: Minecraft session login vs jEdit version check
- 修正建议: Incorporate project-specific context or domain knowledge；Use dataflow or more detailed structural analysis to capture distinct control flow；Fine-tune on more diverse negative examples with high API overlap

### case_id=2592 FP boilerplate_overlap

- 方法: `readData` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses comma-separated tokens from global strings into various sets and maps, building a lookup structure for Tibetan and Sanskrit characters.
- B 摘要: Copies a file from source to destination using NIO file channels and memory-mapped buffers.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-indexed on common lexical elements (IOException, File, throws, private static) and boilerplate structure (try-catch-finally) while missing the vast difference in overall semantics due to limited capacity for long-range semantic understanding.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because functions have completely different purposes and no substantial functional overlap; they are not even Type-3/4 similar.
- 共享行为: Both are private static methods that perform I/O operations；Both can throw or handle IOException
- 行为差异: A parses and populates in-memory data structures; B copies bytes from one file to another；A uses StringTokenizer and HashSet; B uses FileChannel and MappedByteBuffer；A has complex conditional logic and error messages; B is a straightforward utility
- 修正建议: Incorporate data-flow analysis to track output side effects；Enhance model with graph representations capturing control flow and data dependencies；Use cross-function context or method name embeddings to disambiguate purpose

### case_id=2593 FN benchmark_preference_bias

- 方法: `getResourceAsStream` vs `WebmillDeploy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Retrieves a resource as an InputStream with caching and HTTP conditional GET logic.
- B 摘要: Constructs a WebmillDeploy object by processing a JAR file, rewriting XML, and creating a WAR file.
- 静态失败原因: The model likely failed because it was misled by lexical overlap of common API terms and boilerplate, while missing the semantic divergence in the core logic. BCB's broad definition of clones might have caused the false negative.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label them as clones due to similar structural patterns (resource management, boilerplate code) and common utility operations, even though core functionality differs.
- 共享行为: Both use try-catch-finally blocks for resource cleanup.；Both perform file I/O operations and use stream classes.；Both include System.out.println statements for debugging.
- 行为差异: Function A retrieves remote resources and caches local copies; Function B transforms local JAR files for deployment.；Function A returns an InputStream; Function B is a constructor with side effects.；Function A includes HTTP connection handling; Function B involves XML parsing and JAR entry enumeration.
- 修正建议: Improve the model to distinguish core functionality from boilerplate code.；Use hierarchical or flow-aware representations to capture program intent beyond surface structure.；Incorporate type or documentation information to identify different purposes.

### case_id=2594 FN partial_functionality

- 方法: `execute` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Processes Java class files by reading bytecode, analyzing methods, and injecting additional bytecode to instrument methods, then writing modified classes.
- B 摘要: Downloads a KMZ file from a URL, unzips it, and extracts each entry to a file on disk.
- 静态失败原因: The functions have low token overlap (Jaccard 0.1136). A static BERT model relies on token sequences and may not capture the high-level structural similarity of 'iterate-process-write' pattern. The model likely focused on concrete API tokens (e.g., ClassReader, ClassWriter vs ZipInputStream, ZipEntry) and found them dissimilar, predicting non-clone. The model lacks understanding of abstract functionality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have annotated this as clone because both functions follow a similar pattern: iterate over a collection, read each item, perform some processing, and write the result. Both involve input/output streams and use loops. However, the specific processing logic is entirely different, and they belong to different domains. Under a strict semantic interpretation, they are not clones; BCB's annotation might be considered a false positive.
- 共享行为: Both read data from input streams；Both iterate over a collection of items；Both write data to output streams；Both handle exceptions with try-catch
- 行为差异: A transforms bytecode using ASM library; B merely extracts files without modification；A operates on pre-existing class file resources; B fetches a remote zip file；A logs statistics about injected classes; B prints extraction progress；A handles a specific CallStack class; B handles arbitrary zip entries
- 修正建议: Use more robust structure-aware models that capture control flow and data flow patterns.；Incorporate program dependence graphs or abstract syntax tree features.；Include domain-specific embeddings for common I/O patterns.；Augment training data with semantically similar pairs from different domains.

### case_id=2595 FP boilerplate_overlap

- 方法: `getRequestContent` vs `loadExistingAntlibs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads the first line from an HTTP URL.
- B 摘要: Loads Ant library definitions from classpath resources by iterating over multiple URLs and lines.
- 静态失败原因: Static models like GraphCodeBERT may rely on overlapping tokens like 'URL', 'BufferedReader', 'reader.readLine()', 'reader.close()', which are common boilerplate. The low Jaccard (0.13) suggests limited lexical overlap, but the model might still be biased by these salient tokens and miss the larger control-flow differences and functional divergence.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators likely view these as completely different tasks—A is a simple URL content fetcher, B is a classpath resource loader that parses and loads libraries. Despite shared I/O patterns, the functionality and purpose are entirely different, so BCB labels as non-clone.
- 共享行为: Both open a stream from a URL；Both use BufferedReader to read lines；Both close resources
- 行为差异: A returns a single line; B is void and processes multiple lines；A uses HttpURLConnection; B uses classpath resources；A has no loop; B loops over resources and lines；B calls loadAntLib on each package; A just returns
- 修正建议: Train on more diverse non-clone pairs that share boilerplate but differ in intent；Incorporate control-flow graphs or data-flow analysis to distinguish simple vs. loop-intensive logic；Use AST-based similarity with pruning of common subpatterns

### case_id=2596 FP partial_functionality

- 方法: `readTwitterFead` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a Twitter feed JSON using HttpClient and returns the entire response as a string.
- B 摘要: Fetches a version string from a URL using URLConnection and returns the last line read.
- 静态失败原因: Static BERT may have overemphasized the structural similarity of the read-loop pattern and ignored the distinct APIs and output semantics, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considered the different HTTP libraries, different output processing, and different error handling as sufficient to label them not clones, as they are not semantically equivalent and only share a general pattern.
- 共享行为: Both perform an HTTP GET request to retrieve text content from a URL.；Both read the response line by line using BufferedReader.
- 行为差异: A uses Apache HttpClient (HttpGet, DefaultHttpClient) while B uses java.net.URL/URLConnection.；A appends all lines to a StringBuilder and returns the full content; B assigns each line to version variable, effectively returning only the last line.；A logs errors to Android Log; B catches Exception broadly and returns null on failure.；A is an instance method; B is static.
- 修正建议: Enhance training data with more negative examples of similar patterns with different API usage.；Incorporate data-flow analysis to track how the output is constructed (full vs last line).

### case_id=2597 FN partial_functionality

- 方法: `simulate` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Simulates a reputation system by reading user actions from a file, calling web services, printing results, and writing to a log file.
- B 摘要: Handles HTTP GET requests to retrieve and render a portal page, with visibility checks, logging, and caching.
- 静态失败原因: Static BERT models typically rely on lexical and structural similarity (e.g., token overlap, AST patterns). With a token Jaccard of 0.09 and vastly different APIs and logic, the model correctly predicted non-clone. The failure here is that BCB's label may be erroneous or based on a very permissive clone definition that static models cannot capture.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones based on a broad Type-4 interpretation, possibly due to both methods containing try-catch blocks, logging, file I/O, and similar control flow patterns (e.g., reading input, processing, writing output). However, the functionality is entirely different, and the low token Jaccard suggests very little lexical similarity.
- 行为差异: Function A reads from a file and calls remote services; Function B handles HTTP requests and interacts with a page model.；Function A performs assertions for testing; Function B generates HTTP responses.；Function A has a while loop processing multiple lines; Function B is single-request without loops.；Different input/output: file vs HTTP request/response.
- 修正建议: Incorporate higher-level semantic features such as code summarization or intent classification.；Use contrastive learning with functional annotations to distinguish true clones from coincidental structural similarity.；Benchmark models on diverse clone types to reduce bias toward lexical similarity.

### case_id=2598 FN lexical_or_api_overlap

- 方法: `main` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Signs a PDF document using a keystore, then verifies signatures on a signed PDF.
- B 摘要: Downloads a WSDL file from a URL, modifies the endpoint address, and saves it locally.
- 静态失败原因: Static BERT models rely heavily on token overlap and structural similarity; the low Jaccard similarity (0.081) and vastly different API usage (iText vs Apache Axis) led the model to correctly classify them as non-clones, but BCB label indicates a false negative in the context of BCB's annotation.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: It is unlikely BCB would label these as clones; possibly an annotation error or the truncated middle of code_a contains similar code not visible.
- 共享行为: Both use file I/O operations (FileOutputStream, InputStream)；Both handle exceptions with try-catch blocks；Both use logging (System.out vs mLog)
- 行为差异: Function A deals with PDF signing and verification; Function B deals with WSDL file download and XML modification；Function A uses KeyStore, PrivateKey, Certificate; Function B uses URL, XML parsing (Document, NodeList)；Function A has complex cryptographic operations; Function B has simple file download and XML editing；Function A returns void; Function B returns String
- 修正建议: Improve model to incorporate functional semantics beyond token overlap；Use context-aware models that can identify underlying intent (e.g., both are 'file processing' utilities)

### case_id=2599 FP lexical_or_api_overlap

- 方法: `get` vs `scrapeForIsbns`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches game records from a URL by sending a GET request with custom headers and parsing lines that do not start with '#'.
- B 摘要: Scrapes ISBN-10 codes from a URL by reading lines, matching a regex pattern, and retrying on connection failure.
- 静态失败原因: The static model may have been misled by the similar API usage (URL, BufferedReader, while loop) and the common pattern of reading lines from a URL. It likely overemphasized these structural similarities while ignoring the distinct parameters, logic, and output types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality is completely different: one is a generic GET for game records, the other is a specific ISBN scraper with retries. Despite sharing a URL-reading boilerplate, the core purpose and output differ significantly.
- 共享行为: Both open a connection to a URL and read lines from the input stream.；Both perform some line-by-line processing of the response.；Both handle I/O exceptions.
- 行为差异: Function A sends a GET request with custom headers (latitude, longitude, count); function B does not set headers.；Function A decodes lines into GameRecord objects; function B matches ISBN patterns and stores them in a map.；Function A returns an array of GameRecord or null; function B returns an integer count of matches.；Function B includes retry logic with sleep on ConnectException; function A does not retry.
- 修正建议: Incorporate dataflow analysis to track how inputs are used and outputs are produced.；Use type information and method signatures more explicitly.；Enhance training with more negative examples that share API calls but different semantics.

### case_id=2600 FN benchmark_preference_bias

- 方法: `copyResource` vs `doUpload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a resource from a URL or file to a destination file stream.
- B 摘要: Handles HTTP multipart file upload, processes parameters, and writes responses.
- 静态失败原因: Static BERT models like CodeBERT may over rely on API similarity (e.g., File, InputStream) and fail to capture the high-level semantic difference between a simple copy utility and a full upload servlet.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider both as performing some form of resource copying (copyResource copies a resource; doUpload copies uploaded files to a temp directory), but the overall functionality and complexity differ greatly.
- 共享行为: Both involve file I/O operations
- 行为差异: copyResource is a simple file copy from any source to a destination；doUpload is a complex servlet for uploading files with session management, multipart parsing, and response handling；copyResource has no HTTP or servlet context；doUpload includes error handling, logging, and redirects
- 修正建议: Incorporate control flow and data dependencies；Use graph-based models that capture long-range semantics；Improve training data with more negative examples of semantically different functions with similar API usage

### case_id=2601 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Static method checks for a new version by reading a version file from a URL and comparing build numbers.
- B 摘要: Constructor of a web browser GUI that reads an XML/HTML page from a URL, optionally applies XSLT transformation, and displays the result.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the common API calls (URL, BufferedReader, IOException) and the try-catch structure, ignoring the distinct business logic and different control flows.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers them non-clones because they have completely different overall functionality (version check vs. GUI browser constructor) even though they share some API usage patterns.
- 共享行为: Both open a URL and read lines using BufferedReader
- 行为差异: A is a utility method for version checking; B is a GUI constructor for a web browser；A interacts with a View object for cursor and messages; B sets up Swing components and handles transformation；A only parses simple key-value lines; B parses XML, applies XSLT, and displays HTML content
- 修正建议: Incorporate data flow and control flow awareness；Use contrastive learning to distinguish common boilerplate from unique behavior；Add more context-sensitive features like method signatures and class relationships

### case_id=2602 FN partial_functionality

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to files.
- B 摘要: Copies a file from source to destination with configurable buffer size and force overwrite.
- 静态失败原因: Static BERT models rely on token similarity and structural overlap; low Jaccard similarity (0.256) and different method signatures/API calls (ZipInputStream vs FileInputStream) caused it to miss the shared pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers these clones because both implement a stream copy loop pattern with buffer, and the core functionality of reading from input and writing to output is shared, despite different sources and zip handling.
- 共享行为: Reads bytes from an input stream into a buffer；Writes buffer bytes to an output stream；Uses byte buffer loop pattern
- 行为差异: A reads from URL and ZipInputStream; B reads from FileInputStream；A extracts zip entries; B copies single file；A uses BufferedOutputStream; B uses plain FileOutputStream；B has overwrite handling and logging; A does not
- 修正建议: Enhance detection of abstract I/O copy patterns via data-flow analysis；Use graph-based models to capture common control flow (read-write loop) independent of specific stream types；Reduce sensitivity to method names and parameters

### case_id=2603 FP other

- 方法: `perform` vs `digest`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles a web request to classify a concept, manages session, parses XML, and sends HTTP POST.
- B 摘要: Computes SHA-256 hash of a message and returns base64-encoded digest.
- 静态失败原因: The model likely picked up on superficial similarities like method signatures with String parameters/returns or exception handling, lacking deeper semantic understanding.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would not consider them clones because they implement entirely different functionalities with no overlap.
- 行为差异: A: web request handling, session management, XML parsing; B: cryptographic hashing；A: returns ActionForward; B: returns String；A: complex control flow with conditions and loops; B: linear sequence
- 修正建议: Incorporate more robust semantic features like data flow or API call sequences.；Use contrastive learning to distinguish unrelated methods.

### case_id=2604 FN benchmark_preference_bias

- 方法: `CopyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination, creating parent directories if necessary, using NIO channels.
- B 摘要: Builds a website for editing by reading XML, transforming it, and writing output pages to files.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed to detect a clone because the token Jaccard similarity is very low (0.066), and the functions perform entirely different high-level tasks. The model correctly identified them as non-clones, but the BCB label is contradictory.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider them clones due to shared file I/O operations and the fact that both functions ultimately write to files, but this is a very loose interpretation. The low token similarity and vastly different logic make a clone judgment unlikely even under broad Type-4 criteria. The BCB label may be an error.
- 共享行为: Both involve file I/O operations (FileInputStream, FileOutputStream/FileWriter).；Both handle exceptions (IOException, etc.).；Both create directories or write files to the filesystem.
- 行为差异: A is a simple file copy; B is a complex multi-step process with XML transformation and string manipulation.；A returns a String; B returns void.；A uses NIO channels; B uses traditional streams and readers.；A has no loops; B loops over a collection of pages.
- 修正建议: Improve the benchmark annotation consistency to avoid labeling clearly different functions as clones.；Use more targeted similarity metrics that capture functional equivalence beyond low-level API usage.；Train models with more discriminative features to avoid being misled by trivial shared tokens.

### case_id=2605 FP lexical_or_api_overlap

- 方法: `sendPost` vs `setMembers`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Connects to a Trac URL, parses HTML to extract component and priority options, and stores them in arrays.
- 静态失败原因: Static models like GraphCodeBERT may rely on token overlap (URL, BufferedReader, etc.) and common API usage patterns, without capturing the fundamental difference in intent and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the functions have distinct purposes and behavior; the shared HTTP boilerplate is insufficient for clone annotation.
- 共享行为: Both open a URL connection and read lines from the input stream using BufferedReader.
- 行为差异: sendPost uses POST method and writes parameters to the output stream; setMembers uses GET (implicitly via openStream) and does not send data.；sendPost returns the entire response as a string; setMembers parses specific HTML select elements and populates instance variables.；sendPost catches generic Exception and shows message; setMembers catches specific MalformedURLException and IOException with print statements.；sendPost is a public static utility; setMembers is private static and side-effectful.
- 修正建议: Incorporate structural information like control flow and data dependencies.；Use contrastive learning to distinguish utility methods from domain-specific logic.；Add more training examples of methods that share API but differ in goal.

### case_id=2606 FN partial_functionality

- 方法: `copyResource` vs `encodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file, throwing an exception on failure.
- B 摘要: Reads a file, Base64 encodes it, and writes the encoded data to another file, returning a boolean success flag.
- 静态失败原因: The model likely relied on token overlap (low Jaccard) and surface features like method names and API calls, missing the high-level structural similarity of the stream-copy pattern. Differences in buffer size, exception handling, and encoding logic further confused the representation.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as clone because both follow the same streaming I/O pattern (open, read-write loop, close) and the encoding could be viewed as an additional step that does not change the underlying copy structure. The broad Type-3/4 acceptance in BCB might tolerate such functional embellishments.
- 共享行为: Both open an input stream and an output stream to files.；Both read data in chunks (byte-by-byte or buffer) and write to the output stream.；Both close streams after operation.
- 行为差异: Function B performs Base64 encoding, while Function A performs a plain copy.；Function B uses buffered streams and a 64KB buffer; Function A reads single bytes.；Function B returns a boolean and handles exceptions; Function A throws an exception on failure.；Function A can read from a URL; Function B reads from a file path only.
- 修正建议: Incorporate dataflow analysis to capture stream connections and read-write loops.；Use graph-based representations that abstract over specific API calls (e.g., InputStream/OutputStream patterns).；Train on augmented data that includes variants of copy operations with minor transformations (like encoding).

### case_id=2607 FN partial_functionality

- 方法: `main` vs `lookupFutureEvents`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Main method that sends a POST request to RenRen API with multiple parameters and prints the response.
- B 摘要: Method that fetches future events from Meetup API by group identifier, parses JSON into list of Event objects.
- 静态失败原因: Low token overlap, different method names and structures, and reliance on external library context (e.g., RenRen vs Meetup) cause the model to miss the generic HTTP pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones based on a broad Type-4 interpretation where any two functions making HTTP requests and parsing responses are considered similar, ignoring the specific API semantics.
- 共享行为: Both create a URL from string concatenation；Both open an HTTP connection and read response line by line
- 行为差异: Different HTTP methods (POST vs GET)；Different API endpoints and parameters；A prints response to console, B parses into domain objects；B handles exceptions and returns a list, A does not handle exceptions and returns void
- 修正建议: Enhance model with pre-training on code that captures high-level API usage patterns；Incorporate data flow graphs to identify common I/O operations；Use contrastive learning to distinguish between specific and generic functionality

### case_id=2608 FN partial_functionality

- 方法: `doTransfer` vs `getURLContent`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request to a given URL, transferring request body and response stream.
- B 摘要: Fetches the content of a URL as a string.
- 静态失败原因: The functions have low token Jaccard and different control flow; static BERT might focus on surface form and miss high-level semantic similarity of URL connection reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones because they both involve opening a URL and reading content from it, considering broad Type-4 functional similarity.
- 共享行为: Both open a URL connection and read its input stream.
- 行为差异: A writes the incoming request body to the URL connection's output stream, handles request headers, sets request method, and writes the response back to the servlet response output stream.；B simply reads the input stream line by line and returns a string, without any output writing.
- 修正建议: Use dataflow analysis to capture that both retrieve data from a URL.；Incorporate functional signatures or use graph-based representations that abstract away detailed IO operations.

### case_id=2609 FP partial_functionality

- 方法: `readPage` vs `get`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a webpage from a URL and returns the HTML content as a string, optionally skipping lines starting with '#'.
- B 摘要: Fetches game records from a URL using HTTP GET with custom headers, parses lines (skipping '#') into GameRecord objects, and returns an array.
- 静态失败原因: Static BERT/GraphCodeBERT may overemphasize the common control-flow pattern (open URL, read lines, filter comments) and miss the divergence in return type and data transformation. The model may have treated the similar IO structure as sufficient evidence for a clone, ignoring functional semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels clones only if the functions perform the same operation despite structural variations. Here, function A is a generic page reader, while B is a specific game record fetcher; their core purposes differ, so BCB annotates as non-clone even though they share some implementation details.
- 共享行为: Open a URL connection and read lines from an input stream；Skip lines starting with '#'；Use BufferedReader and InputStreamReader
- 行为差异: A returns concatenated HTML string; B returns array of GameRecord objects；A does not handle HTTP status codes or set custom headers；A throws Exception; B catches exceptions and prints stack trace；A has an optional flag to ignore comments; B always ignores comments
- 修正建议: Incorporate dataflow analysis to track how read data is transformed；Use function signature and return type as strong signals；Train on tasks that differentiate between similar-looking but semantically different code

### case_id=2610 FP lexical_or_api_overlap

- 方法: `get` vs `issueCommandToServer`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Makes an HTTP GET request with custom headers, reads response lines, skips comment lines, decodes each as GameRecord, and returns an array or null on failure.
- B 摘要: Makes an HTTP POST request with a command and JSON-encoded ChangeCapsule, reads response lines, concatenates them, and returns the full string; throws IOException on failure.
- 静态失败原因: Static BERT likely relied on lexical overlap of common HTTP I/O API patterns (URLConnection, BufferedReader, readLine) and overlooked the significant differences in HTTP method, parameter handling, and response parsing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers functions that perform similar core logic (e.g., both HTTP GET that parse a list of records) as clones, but here the functions differ in HTTP method, response processing, and purpose, making them non-clones even under broad Type-3/Type-4.
- 共享行为: Both open a URL connection and set request properties；Both read the response line by line using BufferedReader；Both return a result built from the response lines
- 行为差异: HTTP method: GET vs POST；Request parameters: headers (lat, lon, count) vs URL-encoded body (command, capsule)；Response parsing: skips '#' lines and decodes GameRecord vs concatenates all lines as raw string；Error handling: returns null and prints stack trace vs throws IOException
- 修正建议: Add features to capture HTTP method (e.g., presence of setRequestMethod or setDoOutput)；Incorporate semantic understanding of method names and parameter types；Use dataflow analysis to distinguish direction of communication (read vs write)

### case_id=2611 FN partial_functionality

- 方法: `testLoadSource` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: A test method that loads an article source via a DAO facade and asserts the content contains a specific string.
- B 摘要: A method that retrieves a resource as an InputStream, with caching logic including HTTP requests and file caching.
- 静态失败原因: The static BERT model likely relied on lexical token overlap and syntactic structure, which are very low (Jaccard similarity 0.058), and failed to capture the abstract functional similarity that BCB annotated.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as broad Type-4 clones because they share the high-level functionality of 'obtaining an InputStream from a source' even though implementations differ drastically.
- 共享行为: Both methods return an InputStream from a resource (one from a DAO, one from URL/file cache).
- 行为差异: Function A is a unit test with assertions; Function B is a production caching method.；Function A uses a specific DAO; Function B uses URL connections and file caching.；Function B includes HTTP status checks and cache management; Function A does not.
- 修正建议: Incorporate data flow analysis to detect that both methods ultimately produce an InputStream.；Use a larger context or call graph to infer functional equivalence.

### case_id=2612 FN benchmark_preference_bias

- 方法: `doTransfer` vs `parse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Forwards an HTTP request to a given URL by copying request headers and body and returning the response.
- B 摘要: Parses a data file or URL into a DataSet object using StreamTokenizer, handling headers and types.
- 静态失败原因: The static model did not fail; it correctly identified non-clone due to low token overlap and differing high-level semantics. The BCB annotation is questionable.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled as clone due to both involving URL connections and I/O stream handling, but the overall functionality is too different.
- 共享行为: Both read from a URL or stream using I/O classes.；Both handle exceptions with try-catch.
- 行为差异: A proxies an HTTP request; B parses structured data into a DataSet.；A uses HttpURLConnection and writes to ServletOutputStream; B uses StreamTokenizer and returns DataSet.；A has many debug print statements; B has none.
- 修正建议: Review BCB annotation for this pair; consider re-annotating with stricter criteria.

### case_id=2613 FN partial_functionality

- 方法: `getEncoding` vs `fetchUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts character encoding from a URL by checking HTTP headers and then reading the response body for charset hints.
- B 摘要: Fetches the entire content of a URL as a string by reading all lines from the input stream.
- 静态失败原因: Static BERT methods rely on token overlap and control-flow structure; here token Jaccard is low (0.267) and method names differ, leading to low similarity. The models may fail to recognize the shared URL-reading core due to different surface forms.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label Broad Type-4 clones, considering both as 'fetching data from URL' with partial functionality overlap, despite different final outputs.
- 共享行为: Both open a URL connection and read from an InputStream using a BufferedReader.；Both return a String value based on the content read from the URL.
- 行为差异: A reads HTTP headers and searches for charset/encoding, while B reads all lines and concatenates them.；A has complex parsing logic (extractEncoding), B simply appends lines.；A can throw IOException from its signature, B catches exceptions and returns empty string.；A has a fallback default encoding (STANDARDENCODING), B returns empty string on failure.
- 修正建议: Incorporate dataflow analysis to trace input/output behavior and recognize common subroutines.；Use fine-grained semantic matching that captures intention (e.g., 'reading from a URL') even if post-processing differs.

### case_id=2614 FN boilerplate_overlap

- 方法: `doVersionCheck` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a remote URL to check for version information by parsing lines starting with '.build' and '.stablebuild'.
- B 摘要: Reads a file from disk or classpath and returns its entire content as a string.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token overlap and method name similarity, which are low (22.9% Jaccard). The models also fail to capture the abstract IO reading pattern shared across different contexts, leading to a non-clone prediction.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones because both implement a similar pattern: reading from an input stream, buffering, and line-by-line processing. The broad Type-3/Type-4 clone definition in BigCloneBench includes such structural similarities even if the task differs.
- 共享行为: Both open an input stream from a resource (URL or file) and wrap it in a BufferedReader.；Both read lines in a while loop and perform some processing per line.；Both handle IOException and have fallback mechanisms (A: error dialog, B: system exit).
- 行为差异: A reads from a remote URL defined by a property; B reads from a local file or classpath resource.；A only processes lines starting with specific prefixes; B appends all lines to a StringBuffer.；A calls another method after extracting versions; B returns the concatenated string.；A shows/hides wait cursor and shows error dialogs; B prints debug messages and calls System.exit on errors.
- 修正建议: Incorporate data flow analysis to capture the stream-read-loop pattern independent of token overlap.；Train on more diverse examples of IO-related clones to improve generalization.；Use graph-based representations (e.g., AST with control flow) to highlight structural similarity.

### case_id=2615 FP lexical_or_api_overlap

- 方法: `handler` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts values from a web page by searching for delimiters and updating map entries.
- B 摘要: Imports biological sequences (FASTA-like) from a URL using an ImportHelper.
- 静态失败原因: Static BERT/GraphCodeBERT may over-rely on token overlap (URL, openStream, IOException, readLine, etc.) and miss deeper semantic structure, mistaking generic I/O patterns for similar functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the functional purpose and data processing logic are completely different, despite shared boilerplate I/O patterns.
- 共享行为: Both open a URL stream and read character data；Both use InputStreamReader and BufferedReader/ImportHelper；Both handle IOException and MalformedURLException；Both perform a while loop reading lines
- 行为差异: Function A extracts arbitrary key-value pairs using include/from/to strings; function B parses sequences with tokenization and helper methods；Function A modifies an existing map; function B populates new lists；Function A's logic depends on TargetPage fields; function B uses a combo box and ImportHelper
- 修正建议: Incorporate data-flow analysis to distinguish different variable types and transformations；Use domain-specific embeddings or fine-tuning on code clones to reduce boilerplate bias

### case_id=2616 FN benchmark_preference_bias

- 方法: `copyOverWarFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies war files from a directory to the apps data directory, unzips and extracts them.
- B 摘要: Launches a NexOpen project by processing Maven pom files and configuring Hibernate reverse engineering, optionally copying a resource file from the bundle.
- 静态失败原因: Static BERT or GraphCodeBERT models typically rely on token-level embeddings and structural features. These two functions have very low token Jaccard (0.0769) and different method structures, so the model correctly identified them as non-clones. The static model fails to capture the broad semantic similarity that BCB might have intended.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled these as clones because both methods perform file copy operations using IOUtils.copy within a larger file management context. The BCB benchmarks sometimes consider Type-4 clones where functions have similar high-level purpose (deployment/configuration) even if detailed implementation differs.
- 共享行为: Both use IOUtils.copy to copy file contents from input stream to output stream；Both involve file operations on project directories；Both use Logger for logging exceptions
- 行为差异: Function A is focused solely on copying war files, while function B is a complex launch method with many other steps like XML parsing and property setting；Function A works with war files, function B works with Maven project files and Hibernate configuration；Function A sets system properties and JFileChooser, function B manages Eclipse launch configurations and project resources
- 修正建议: Improve model to be less sensitive to lexical differences when functions share high-level file operation logic；Consider training with more Type-4 clone examples；Use dataflow or program dependence graphs to capture I/O operations

### case_id=2617 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a specific locale by reading, optionally copying an English file, and updating or adding a key-value pair.
- B 摘要: Recursively copies a file or directory from source to destination using byte-by-byte I/O.
- 静态失败原因: Static BERT methods may rely heavily on lexical and structural similarity, which is low (token Jaccard 0.25). They may miss the shared file-copy subfunction due to long-range dependencies and different surrounding logic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them Type-4 clones because both contain a loop that reads bytes from a FileInputStream and writes them to a FileOutputStream, which is a common functional pattern. The broad annotation policy might accept this partial similarity.
- 共享行为: Both read from an input stream and write to an output stream byte by byte.
- 行为差异: A is specific to properties files and updates a particular message; B is a generic file/directory copier.；A includes properties parsing and manipulation; B handles directory recursion and error logging.；A conditionally copies a file only if target doesn't exist; B always copies recursively.
- 修正建议: Incorporate subgraph matching for I/O patterns.；Use dataflow analysis to detect similar byte-copy loops across different methods.；Consider contrastive learning that pairs methods with shared subfunctionality.

### case_id=2618 FN dataflow_blindspot

- 方法: `getHTML` vs `loadSourceCode`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `dynamic_equivalence_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches HTML content from a URL and optionally writes it to a file.
- B 摘要: Loads source code from a local resource file, applies syntax highlighting, and wraps it in HTML tags.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on method names, API calls, and variable usage, which differ significantly, and the low token overlap and different control flow caused the model to miss the underlying common pattern of reading lines and building a string.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本可能是 API 写法不同但行为等价的漏报。建议测试目标为 input_output_equivalence。
- BCB 偏好解释: BCB often labels as clones functions that perform similar tasks of fetching and building a string from line-by-line input, considering the shared core logic as a broad Type-3/Type-4 clone despite differing sources and final destinations.
- 共享行为: Both read lines from an input stream using BufferedReader and build a resulting string by concatenating lines.
- 行为差异: Function A fetches from a remote URL, while function B reads from a local resource file.；Function A optionally writes the result to a file, while function B stores it in an instance variable.；Function B applies syntax highlighting and wraps result in HTML tags, function A does not.
- 修正建议: Incorporate graph-based data flow analysis to capture the core loop of reading lines and concatenating.；Use code summarization or intent detection to group functions with similar basic operations.

### case_id=2619 FN benchmark_preference_bias

- 方法: `getFile` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its wsdlsoap:address location, and saves it to a temporary file, returning the file path.
- B 摘要: Converts an ACRNEMA format file to DICOM by parsing pixel data, adding UIDs, and writing the output, with error checks.
- 静态失败原因: The static model correctly predicted non-clone; the BCB label is likely an error, so the model did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled this pair, possibly due to overbroad interpretation of 'file processing' or a data error in the benchmark.
- 共享行为: Both perform file I/O operations；Both use input streams and output streams；Both involve conditional checks and loops
- 行为差异: Different domains: WSDL download vs medical image conversion；Different input/output: URL to file vs file to file；Different processing: XML modification vs pixel data manipulation；Different error handling: AxisFault vs IOException
- 修正建议: Review the benchmark annotation for this pair；Ensure clones require functional similarity beyond generic I/O；Consider removing or correcting the label

### case_id=2620 FP boilerplate_overlap

- 方法: `onlyFileCopy` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel transfer.
- B 摘要: Initializes data structures by parsing comma-separated strings and reading a configuration file.
- 静态失败原因: The model likely over-relied on superficial boilerplate (try-catch, IOException) and ignored the completely different core logic and data flow. Low token overlap (0.0588) suggests the model may have been misled by the truncated file-reading part of code_b.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers functions non-clones if they perform fundamentally different tasks, even if they share I/O. These two differ entirely in purpose and implementation.
- 共享行为: Both involve file I/O operations；Both handle IOException
- 行为差异: onlyFileCopy transfers bytes between file channels; readData parses strings into collections；onlyFileCopy is parameterized with files; readData uses static global variables；onlyFileCopy is for copying; readData is for initialization；onlyFileCopy uses NIO channels; readData uses StringTokenizer and HashSets
- 修正建议: Incorporate data flow analysis to capture actual transformations；Train on more negative pairs with similar I/O but different semantics；Use graph-based representations to distinguish control vs data operations

### case_id=2621 FP partial_functionality

- 方法: `getRequestContent` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves the first line of content from a given URL as a string.
- B 摘要: Performs a version check by reading a remote version file, parsing version and build numbers, comparing them with current version, and notifying the user through the UI.
- 静态失败原因: The model likely over-emphasized the lexical and API overlap (URL, BufferedReader, InputStreamReader) and the initial sequence of opening a URL and reading, while ignoring the substantial additional logic in B (looping, parsing, UI). The shorter length of A and the longer context in B may have caused the model to focus on shared patterns rather than the complete semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled these as non-clones because the core functionality is different: one is a simple HTTP GET of the first line, the other is a version check with parsing, comparison, and UI feedback. Even under broad Type-4 similarity, the behavioral divergence is too large.
- 共享行为: Both open a URL and read text input using BufferedReader and InputStreamReader.；Both close the input stream after reading.；Both handle network IO (though A declares Exception, B catches IOException).
- 行为差异: A only reads the first line, while B reads all lines and parses them for version/build information.；B includes UI interactions (showing wait cursor, displaying messages), whereas A has no UI.；B has complex conditional logic for version comparison and error handling with user notifications.；A returns the read line, while B performs side effects and returns void.
- 修正建议: Incorporate control flow and data flow graphs to capture structural differences.；Use method-level embeddings that consider entire method body rather than just token sequences.；Include features like method length, number of branches, and external API calls to distinguish simple from complex logic.；Train with contrastive learning that penalizes false positives from high token overlap but different intent.

### case_id=2622 FP boilerplate_overlap

- 方法: `get` vs `PhoneSetImpl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Static method that makes an HTTP GET request with specific headers, reads lines from the response, skips lines starting with '#', decodes them into GameRecord objects, and returns an array of GameRecord.
- B 摘要: Constructor that opens a URL stream, reads lines, skips lines starting with '***', parses each line and adds to a HashMap, and does not return anything.
- 静态失败原因: The static BERT/GraphCodeBERT model likely focused on the high lexical and structural overlap of boilerplate code (BufferedReader, readLine, line.startsWith, while loop) and missed the critical functional differences such as method signature, return type, HTTP-specific headers, and different processing logic. The model may have been misled by the common pattern of reading lines from a URL stream.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled this as non-clone because the two functions have fundamentally different purposes and outcomes: one is a data retrieval method with HTTP specifics, the other is a constructor that populates a map. Even under lenient BCB-style annotation, the differences in method type, return type, and detailed logic likely outweigh the superficial similarity of reading lines from a URL.
- 共享行为: Both open a connection/stream to a URL and read lines using BufferedReader；Both skip lines that start with a specific comment pattern ('#' or '***')；Both process each line after reading (decode vs parseAndAdd)
- 行为差异: Function A is a static method returning an array; Function B is a constructor returning void；Function A uses HTTP connection with request method, headers, and response code check; Function B directly opens the URL stream；Function A skips lines starting with '#'; Function B skips lines starting with '***'；Function A processes lines into GameRecord objects; Function B processes lines into a HashMap via parseAndAdd
- 修正建议: Incorporate method signature features (return type, static vs constructor) into the model；Use dataflow or control-flow analysis to distinguish between different processing steps；Add attention to the purpose of the function (e.g., HTTP request vs constructor initialization)

### case_id=2623 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `testLoadSource`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by updating or adding a message key-value pair.
- B 摘要: Tests loading a source from an arXiv DAO facade and verifying its content contains a specific phrase.
- 静态失败原因: Static BERT relies on token overlap and structural patterns; low Jaccard (0.072) and differing method names led to non-clone prediction, but BCB annotation expected clone due to broad I/O similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'resource loading and processing' with I/O boilerplate, potentially broad Type-4 clone under manual annotation criteria.
- 共享行为: Both perform I/O operations: reading from an input stream and writing to a writer
- 行为差异: Function A modifies a file based on key-value replacement; Function B only reads and asserts；Function A handles file existence and defaults; Function B is a test with assertions；Different data types: Properties vs. arbitrary text content
- 修正建议: Incorporate functional role analysis；Use data flow or call-graph context to identify I/O-intensive methods as potentially similar across domains；Train with broad clone categories including Type-4

### case_id=2624 FP lexical_or_api_overlap

- 方法: `sendPost` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a concatenated string.
- B 摘要: Performs an HTTP GET request to read and parse lines into version, URL, and info fields, managing error flags and notifying listeners.
- 静态失败原因: Static BERT models like CodeBERT rely on token overlap and API sequence patterns. Both functions share common tokens (URL, BufferedReader, InputStreamReader, readLine, close, catch) and control flow (try-catch, while loop), leading the model to overestimate similarity despite different semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have different high-level functionality despite shared API usage. Here, one is a POST sender and the other is a GET parser, which are different operations, so the non-clone label (0) aligns with BCB preferences.
- 共享行为: Both open a URL connection and read lines from an input stream.；Both handle IO exceptions by printing error messages or setting error flags.；Both use BufferedReader and InputStreamReader to read the response.
- 行为差异: Function A sends a POST request with output (param), while Function B uses GET with no output.；Function A returns the entire response as a string; Function B parses lines into specific fields and triggers listeners.；Function A handles generic Exception; Function B specifically handles IOException with custom messages.
- 修正建议: Include method name and parameter types as additional features to distinguish request type.；Use data-flow analysis to capture that A writes to output stream while B only reads.；Train on more diverse examples that differentiate POST vs GET operations.

### case_id=2625 FP lexical_or_api_overlap

- 方法: `readData` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads and parses initialization data from string tokens and a file into various sets and a hash.
- B 摘要: Downloads, decrypts, and decompresses a file from S3 and moves it to a target location.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to over-reliance on common API mentions (IOException, InputStream, try-catch) without understanding the high-level task difference. The model may have been misled by the presence of file-related operations and error handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have entirely different purposes and no overlapping functionality beyond basic Java IO patterns.
- 共享行为: Both use InputStream and IOException；Both have try-catch blocks；Both involve file operations
- 行为差异: Function A parses configuration data; Function B downloads and processes a file；Function A is static and uses global/class-level fields; Function B is instance-level with S3；Function A has complex tokenization; Function B uses compression and encryption streams；Function A uses StringTokenizers and sets; Function B uses file streams and IOUtils
- 修正建议: Improve training to focus on high-level functionality rather than low-level API overlap；Use more detailed structural features like data flow or call graph；Incorporate method-level documentation or comment understanding；Add more negative examples where IO operations appear but tasks differ

### case_id=2626 FN partial_functionality

- 方法: `runScript` vs `wordFrequency`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from a URL and returns its content as a string, with error handling returning "error!".
- B 摘要: Queries a web service for word frequency by replacing a placeholder in a URL, reads the response, and returns the frequency integer, with error handling returning 0.
- 静态失败原因: Static BERT models rely heavily on token overlap and syntactic structure; the low token Jaccard (0.254) and different variable names, lengths, and return types cause it to miss the abstract structural similarity of the IO pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels as clone when functions share a common structural pattern (open URL, read, return) even if the data processing differs, considering it a Type-4 semantic clone.
- 共享行为: Both open a URL connection and read input from a stream.；Both have try-catch blocks for exception handling.；Both return a value (string or int) derived from the stream content.
- 行为差异: A reads entire file as raw bytes; B reads lines and matches a regex pattern.；A returns string; B returns int.；A constructs URL from getCodeBase() and scriptName; B uses a pre-defined pattern with placeholder replacement.；Error handling: A returns "error!"; B returns 0 and prints stack trace.
- 修正建议: Use graph-based or flow-based models that capture data flow and control flow patterns.；Incorporate execution traces or dynamic analysis to identify IO operations.；Train on more diverse examples of IO-based clones.；Use AST-based differencing focusing on structural subgraph matching.

### case_id=2627 FP lexical_or_api_overlap

- 方法: `addDataFromURL` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens a URL stream, reads all lines, and appends them to a text buffer, with error handling that prints the exception and appends the URL string.
- B 摘要: Constructor for a Swing browser GUI that initializes UI components, loads a URL, optionally processes XML with XSLT stylesheets, and displays the result in an HTML pane.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized lexical and API overlaps (URL, BufferedReader, openStream, readLine, try-catch) while ignoring the vast differences in function length, control flow, and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB experts would not consider these clones because the overall functionality is entirely different: one is a simple URL reader, the other is a GUI constructor with XML processing. The shared URL reading is incidental and not the main purpose of either function.
- 共享行为: Both open a URL using openStream() and read lines using BufferedReader；Both handle exceptions with try-catch blocks；Both print messages to stdout in error cases
- 行为差异: Function A is a void method that only appends to a field; Function B is a constructor that sets up a full GUI and displays content；Function B includes complex XML parsing, stylesheet detection, and XSLT transformation；Function B manages window size, visibility, and event listeners; Function A has no GUI；Exception handling is different: A catches generic Exception, B catches specific IOException and TransformerException
- 修正建议: Incorporate global context by considering function length and structural complexity；Use a method-level classifier that distinguishes between constructors and utility methods；Add features capturing the purpose (e.g., presence of GUI components, XML parsing)；Employ dataflow analysis to highlight different data sinks and sources

### case_id=2628 FN benchmark_preference_bias

- 方法: `handle` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles log file rotation: compresses, deletes, and archives old log files based on a day threshold.
- B 摘要: Retrieves a resource as an InputStream from a URL, with caching to a local file system.
- 静态失败原因: The low token Jaccard (0.18) and distinct method names and contexts led the model to correctly predict non-clone, so it did not fail; the BCB label is questionable.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both involving file I/O and stream handling, but their overall functionality and context are vastly different.
- 共享行为: Both perform file I/O operations (read/write files).
- 行为差异: Function A rotates and compresses log files; Function B fetches and caches remote resources.；Function A uses GZIP compression; Function B does not compress.；Function A creates directories and archives; Function B uses URL connections and HTTP.；Function A is void; Function B returns an InputStream.
- 修正建议: Verify BCB annotations for consistency, especially for broad file I/O functions.；Use more fine-grained clone types to avoid over-generalization.

### case_id=2629 FP boilerplate_overlap

- 方法: `executeHttpGet` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Executes an HTTP GET request and returns the response as a JSONObject.
- B 摘要: Constructor for a Swing browser GUI that fetches XML from a URL, optionally applies XSLT transformation, and displays the result as HTML.
- 静态失败原因: The static BERT model likely focused on the shared I/O boilerplate code (BufferedReader, InputStreamReader, url.openStream()) and the presence of similar string operations, leading to a false positive despite very different overall functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label these as non-clones because they serve entirely different purposes despite a trivial I/O overlap. The functions are in different classes and have no meaningful semantic equivalence.
- 共享行为: Both use BufferedReader and InputStreamReader to read data from a URL stream.
- 行为差异: Function A is a simple utility method; B is a constructor setting up a complex GUI.；A returns a JSONObject; B initializes a UI and displays HTML.；A does not handle XML or transformations; B handles XSLT and XML parsing.；B creates a full window with panels, buttons, and scroll panes; A has no UI.
- 修正建议: Train with examples that emphasize functional purpose over common library usage.；Use structure-aware models that capture control flow and method signatures.；Leverage code summarization or docstring embeddings to capture intent.

### case_id=2630 FN partial_functionality

- 方法: `main` vs `createTempFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a Zip file from a URL and extracts its entries to files.
- B 摘要: Copies a resource from the classpath to a temporary file.
- 静态失败原因: GraphCodeBERT or similar static models likely relied on low token overlap and structural differences, missing the high-level I/O pattern similarity that BCB annotators may have considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a weak Type-4 clone because both functions involve common I/O patterns of reading from a stream and writing to a file, despite different overall purposes. The low token similarity suggests BCB's label might be based on functional similarity in data transfer.
- 共享行为: Reads input from a stream (URL stream / classpath resource stream)；Writes output to a FileOutputStream；Uses buffered I/O；Throws IOException
- 行为差异: Function A processes a Zip archive and extracts multiple entries; Function B copies a single resource to a temp file；Function A selects input based on URL protocol; Function B uses classpath resource lookup；Function A does not handle resource name embedded in URL; Function B handles resource as a string parameter；Function A includes console output; Function B does not
- 修正建议: Train models to recognize abstract I/O patterns beyond token similarity；Incorporate data flow analysis to detect read-write stream operations；Use contrastive learning on pairs with low lexical but high functional similarity

### case_id=2631 FP boilerplate_overlap

- 方法: `extractResourceToFile` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts a resource from the classpath and copies it to a file using IOUtils.copy, with proper stream closing.
- B 摘要: Main method that parses a Prolog file, generates adapters, writes classes and resources to a JAR file, with extensive error handling.
- 静态失败原因: The model likely overemphasized boilerplate patterns (try-catch, stream closing) and common API usage (FileUtils, IOUtils) while ignoring the overall semantic context. The large size and structural complexity of function B may cause the model to focus on local similarities rather than global functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because functions are semantically unrelated; one is a utility to copy a resource, the other is a complex main method for a code generator. Even under broad Type-3/4, they share no significant functional overlap.
- 共享行为: Both involve file I/O operations (reading/writing).；Both use exception handling with try-catch-finally blocks.；Both close streams in finally blocks.
- 行为差异: Function A is a simple resource extraction; B is a complex code generation pipeline.；A has no conditional logic; B has many conditionals and loops.；A operates on single file; B operates on many files and resources.；A uses InputStream; B uses multiple streams, class loaders, and serialization.
- 修正建议: Train on more diverse negative pairs with similar boilerplate but different core logic.；Use graph-based models that capture data/control flow to distinguish long-range semantics.；Apply program slicing to focus on essential behavior.；Incorporate method name and API call sequences more discriminatively.

### case_id=2632 FP lexical_or_api_overlap

- 方法: `copyFile` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file from source to destination using byte streams.
- B 摘要: Main method that parses command-line args, reads and parses a Prolog file, generates adapter classes, and writes output to a JAR.
- 静态失败原因: The static BERT-based model likely overemphasized lexical/API overlaps (e.g., 'File', 'IOException', 'OutputStream') and common Java boilerplate (try-catch, main method patterns), leading to a false positive prediction.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: None
- 共享行为: Both handle IOException；Both use File and FileInputStream/FileOutputStream or similar I/O classes
- 行为差异: A is a simple file copy; B is a complex generation pipeline；A has no conditional logic; B has extensive conditionals, loops, and error handling；A returns void; B is a main method with System.exit；B uses many unique classes (Parser, FactVisitor, etc.) not present in A
- 修正建议: Incorporate task-level semantic understanding (e.g., using data-flow or control-flow graphs) to distinguish file copy from code generation；Add negative sampling with high lexical overlap but different semantics；Use contrastive learning to penalize such false positives

### case_id=2633 FP boilerplate_overlap

- 方法: `setBundleInfoName` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL containing bundle symbolic name and name pairs, and updates matching BundleInfo entries with the bundle name.
- B 摘要: Reads the first line from a given URL via HTTP connection and returns it.
- 静态失败原因: The static model likely overfitted on the lexical overlap of common API usage (URL, BufferedReader, InputStreamReader, readLine), ignoring the drastically different control flow, data processing, and return types. The Jaccard similarity is low but the token overlap in methods and classes may have misled the model.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered them non-clones because despite the shared URL-reading boilerplate, the core functionalities differ completely: one modifies a data structure based on parsed content, the other simply retrieves a single line. The similarity is superficial and not indicative of even Type-3 partial similarity.
- 共享行为: Both use URL class to open a connection or stream；Both use BufferedReader and InputStreamReader to read from the URL
- 行为差异: Function A iterates over all lines, parses key-value pairs, and modifies a list; function B reads only the first line and returns it as a string；Function A returns a boolean success flag; function B returns the first line content；Function A uses URL.openStream() and catches IOException; function B uses HttpURLConnection with explicit connect/disconnect and throws Exception；Function A includes a for loop over a list; function B does not
- 修正建议: Incorporate control flow structure, such as loops vs. sequential execution, into the model representation；Augment training data with negative pairs that share API calls but differ in logic；Use graph-based models that include data dependencies and distinguish between reading all lines vs. first line；Include return type and side-effect analysis as features

### case_id=2634 FN benchmark_preference_bias

- 方法: `readData` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated string fields into HashSets and a hash map, building data structures for Tibetan transliteration mapping.
- B 摘要: Opens an HTTP URL connection, reads the entire response into a StringBuffer, and logs it.
- 静态失败原因: The static model correctly predicted non-clone; the BCB label of 1 appears to be an annotation error, not a model failure.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have incorrectly labeled this pair as clone due to a loose interpretation of 'data reading' or a labeling error; no actual functional similarity exists.
- 行为差异: Function A processes predefined string constants to populate sets and maps; Function B performs network I/O.；Function A has complex conditional and loop logic for parsing a file-like structure; Function B simply reads lines from a BufferedReader.；Function A updates multiple data structures (tibSet, vowelSet, etc.) and uses a hash map; Function B only collects and logs the response.；Function A is private static, no external side effects besides data structure modifications; Function B has network access and logging.
- 修正建议: Re-evaluate the BCB ground truth label for this pair; it is likely a mislabeling.；If labeling is correct, consider if some hidden similarity (e.g., both involve I/O) was intended, but that seems insufficient.

### case_id=2635 FP boilerplate_overlap

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads and parses multiple token sets from string constants and a file to populate various data structures for Tibetan transliteration.
- B 摘要: Copies a file from source to destination using NIO FileChannel.
- 静态失败原因: A static BERT model might overemphasize superficial syntactic patterns such as try-catch blocks and file channel usage, while ignoring the vast difference in control flow and data processing. The low token Jaccard (0.0376) indicates minimal lexical overlap, but the model may have been misled by the presence of common programming idioms (e.g., file reading, exception handling) and the truncation of code_a, losing context of its actual complexity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically annotates clones based on substantial functional overlap. Here, the only commonality is basic file I/O, which is too generic to indicate a clone. The core functionality (parsing vs. file copy) is entirely different, so BCB correctly labels these as non-clones.
- 共享行为: Both involve file I/O operations (reading/writing files) and handle IOException.
- 行为差异: readData performs extensive string parsing and population of multiple hash sets, while copyFile simply transfers bytes between channels.；readData includes complex logic for reading a configuration file and building a hash map; copyFile has straightforward copy logic.；readData is much longer and includes multiple loops and conditional branches; copyFile is short and linear.
- 修正建议: Improve the model's ability to distinguish between core functionality and boilerplate code, e.g., by using AST-based features that capture structural differences.；Incorporate data flow analysis to differentiate between data processing and simple I/O.；Use longer context or full function representations to avoid underestimating the complexity of long functions.

### case_id=2636 FN partial_functionality

- 方法: `getHTML` vs `retrieveQ`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches an HTML page from a URL, optionally writes it to a file, and returns the page content as a string.
- B 摘要: Fetches a web page from a URL and returns its content as a string, printing the HTTP response message to stderr.
- 静态失败原因: Static BERT models may overemphasize lexical differences (e.g., method names, line separators, file writing) and miss the higher-level semantic similarity due to low token overlap (Jaccard 0.301) and structural differences in error handling and side effects.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely focuses on the core functionality of retrieving URL content and returning it as a string, considering differences like file writing and line separators as non-essential variations.
- 共享行为: Both open a URL connection and read the page content line by line.；Both return the concatenated page content as a string.
- 行为差异: A optionally writes the content to a file; B does not.；A uses '\r\n' line separator; B uses '\n'.；A sets User-Agent header and disconnects connection; B does not.；B prints HTTP response message to System.err; A does not.
- 修正建议: Use dataflow analysis to abstract away conditional file writing.；Normalize line separators and user-agent settings before comparison.；Focus on input-output behavior rather than exact API usage.

### case_id=2637 FP boilerplate_overlap

- 方法: `storeImage` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Saves an uploaded image to a timestamped directory with optional resizing.
- B 摘要: Generates an adapter JAR file from a Prolog source file and classpath.
- 静态失败原因: Static BERT models may over-rely on token-level patterns and common API usage (File, I/O streams, try-catch) while missing the distinct semantic contexts, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions have entirely different purposes and domain logic, despite superficial similarities in I/O boilerplate.
- 共享行为: Both perform file I/O operations；Both use exception handling
- 行为差异: Function A handles image upload and resizing; Function B generates Java bytecode from Prolog；Function A uses InputStream and OutputStream; Function B reads a file as string and writes JAR entries；Function A returns a path string; Function B has no return value；Function A relies on properties configuration; Function B parses command-line arguments
- 修正建议: Incorporate dataflow analysis to distinguish core logic from boilerplate；Use graph-based representations to capture control and data dependencies beyond token overlap；Train on more diverse non-clone pairs with shared boilerplate to reduce false positives

### case_id=2638 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `GetResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads integer zone IDs from a resource file and returns them as a HashSet.
- B 摘要: Sends an HTTP GET request and returns the response body as a concatenated string.
- 静态失败原因: The static model likely overfocused on common API usage (InputStreamReader, BufferedReader, readLine) and while-loop structure, ignoring the significant difference in data source, parsing logic, and output type.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB correctly labels these as non-clones because the core functionality (file parsing vs HTTP client) is entirely different, despite superficial structural similarities.
- 共享行为: Both open an input stream and read lines in a while loop using BufferedReader and InputStreamReader.；Both handle exceptions using try-catch blocks.
- 行为差异: Function A reads from a local resource file, while Function B reads from a remote HTTP response.；Function A parses each line as an integer, while Function B concatenates lines as strings.；Function A returns a HashSet<Integer>, Function B returns a String.；Function A uses URL.getResource, Function B uses HttpURLConnection with GET method and checks response code.
- 修正建议: Incorporate data flow analysis to distinguish between different resource types and transformations.；Use method names and broader context (e.g., class-level information) to disambiguate purpose.；Train on more examples where similar code patterns have different semantics to reduce reliance on lexical overlap.

### case_id=2639 FN long_range_semantics

- 方法: `main` vs `writeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to files.
- B 摘要: Copies content from a source file to a destination file using FileChannel.
- 静态失败原因: Static BERT models rely on lexical and structural similarity; the low token Jaccard and different API usage (ZipInputStream vs FileChannel) lead to a non-clone prediction, missing the high-level semantic similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider these clones as Type-4 (semantic) because both functions ultimately perform file writing from an input source, despite different contexts and APIs.
- 共享行为: Both copy data from an input resource to an output resource in the filesystem.
- 行为差异: Function A extracts multiple zip entries; Function B copies a single file.；Function A uses IO streams (ZipInputStream, FileOutputStream); Function B uses NIO FileChannel.；Function A has a hardcoded URL and prints progress; Function B takes explicit file parameters with an append flag.；Function A uses a fixed buffer; Function B uses transferTo for potentially efficient copy.
- 修正建议: Incorporate data-flow analysis to capture I/O patterns.；Use contrastive learning with positive pairs of functionally similar but lexically distinct code.；Augment training with examples of diverse implementations of common I/O operations.

### case_id=2640 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `uncaughtException`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Modify a locale-specific properties file by updating or appending a key-value pair.
- B 摘要: Handle an uncaught exception by showing an error dialog and optionally opening the issue tracker.
- 静态失败原因: The static model correctly identified them as non-clones; the error is not a model failure but likely a mislabel in BCB.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both methods being categorized as 'exception handling' or 'utility' functions, but this is an overly broad interpretation not typical for BigCloneBench.
- 共享行为: Both methods handle exceptions (A uses try-catch, B is an uncaught exception handler).
- 行为差异: Different purposes: localization vs error reporting.；Different APIs: file I/O vs GUI (SWT).；Different outputs: file update vs dialog display.；No overlap in control flow or data manipulation.
- 修正建议: Re-evaluate BCB annotation for this pair; likely false positive.；Improve benchmark consistency in labeling semantic clones.

### case_id=2641 FN benchmark_preference_bias

- 方法: `doGet` vs `displayDiffResults`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to display a portal page with authorization checks and caching.
- B 摘要: Generates HTML diff report for file changes and launches browser.
- 静态失败原因: The static model correctly predicted non-clone due to low lexical overlap and distinct logic; the BCB label appears to be an annotation error, not a model failure.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled due to superficial similarity of both methods writing HTML, but they serve completely different purposes and share no meaningful functional behavior.
- 行为差异: Different domains: servlet request handling vs. diff report generation；Different output targets: HTTP response vs. local file；Different logic: page retrieval and rendering vs. building tables of file statistics；No overlapping functionality beyond generic HTML output
- 修正建议: Review BCB annotations for false positives due to shallow heuristics；Train models with larger and more diverse data to reduce bias towards generic I/O patterns

### case_id=2642 FP boilerplate_overlap

- 方法: `getDatasetsList` vs `handleHandshake`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches and caches a list of dataset names from a remote server given a base URL.
- B 摘要: Handles an incoming handshake packet by validating the username and optionally performing a session check against a Minecraft session server.
- 静态失败原因: The static BERT model overemphasized the structural similarity of URL opening and line reading, ignoring divergent overall logic and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone due to distinct functionality and domain, despite shared I/O pattern.
- 共享行为: Both use URL and BufferedReader to make HTTP requests and read response lines
- 行为差异: A is a getter with caching; B is a command handler with multiple branches；A reads multiple lines and caches the list; B reads a single line and does not cache；A throws RuntimeException on failure; B shuts down network or sends packets
- 修正建议: Use flow-based models to capture data dependencies and control flow；Incorporate method-level context (e.g., class, surrounding code)

### case_id=2643 FN partial_functionality

- 方法: `testNetworkHTTP` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs multiple HTTP GET requests to various URLs, reading and discarding response lines, logging the test.
- B 摘要: Reads a file from disk or classpath, concatenates lines into a string, and returns it.
- 静态失败原因: Static models may rely heavily on token similarity and API calls. The token Jaccard is low (0.17), and the APIs differ (HttpURLConnection vs FileInputStream/ClassLoader). Static models may not capture the shared abstract pattern of reading lines, focusing instead on method-level semantics.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely annotated this clone because both functions share the structural pattern of reading lines from an input stream via BufferedReader, which is a common I/O idiom. The differences in input source and data usage are considered acceptable for Type-3/Type-4 clones under broad functional similarity.
- 共享行为: Both open an input stream, wrap in BufferedReader, read lines in a while loop
- 行为差异: A makes HTTP connections, B reads files；A discards lines, B accumulates them；A has multiple connections, B single；A has no return value, B returns the string
- 修正建议: Train with more emphasis on structural I/O patterns；Use dataflow or control flow graphs to capture abstract behavior；Incorporate I/O abstraction like 'input stream reader' into representations

### case_id=2644 FN partial_functionality

- 方法: `copyResource` vs `saveFileData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using byte-by-byte streaming.
- B 摘要: Saves file data with conditional copying using NIO channels, cache invalidation, image dimension extraction, and thumbnail deletion.
- 静态失败原因: Static BERT models rely on token and structural similarity. The Jaccard similarity is low (0.106) due to different APIs (FileChannel vs. InputStream), additional identifiers in B, and different control flow (while loop vs. conditional channels). The model failed to capture the underlying file copy commonality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels functions that share a core functionality (file copying) as clones, even if one has additional features. Here, both functions ultimately copy file content from a source to a destination, so they are considered semantically similar enough.
- 共享行为: Both read from a source (file/stream) and write to a destination file.；Both handle exceptions and close resources.
- 行为差异: A uses simple byte-by-byte copy; B uses NIO FileChannel.transferTo for efficient copying.；B has multiple conditional branches (if destination != null, if newDataFile != null) with different copy actions.；B includes cache removal, image metadata extraction, and thumbnail deletion.；B is significantly longer and more complex.
- 修正建议: Use data-flow analysis to detect common read-write patterns.；Employ graph-based approaches that model inter-procedural data flow.；Consider training with examples where one function is a superset of another's core functionality.

### case_id=2645 FP boilerplate_overlap

- 方法: `loadMFileViaWeb` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a MATLAB file from a web URL, reads it line by line, and parses it into a UserFunction.
- B 摘要: Constructor for a simple Swing browser GUI that reads XML from a URL, optionally transforms it with XSLT, and displays HTML content.
- 静态失败原因: The static BERT model likely over-emphasized common API usage (URL, BufferedReader, InputStreamReader) and error handling patterns, ignoring the distinct application domains and overall logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB label 0 indicates these are not considered clones even by broad Type-3/4 standards, as they differ in overall purpose and functionality despite shared URL-reading scaffolding.
- 共享行为: Both open a URL and read data line by line using BufferedReader and InputStreamReader.
- 行为差异: Function A parses MATLAB code and returns a UserFunction; Function B sets up a GUI, processes XML/XSLT, and displays HTML.；Function A is a utility method; Function B is a constructor with extensive UI setup.；Function B includes conditional XML processing and XSLT transformation; Function A does not.
- 修正建议: Enhance model to consider class and method context (e.g., class name, surrounding code).；Incorporate dataflow analysis to distinguish different final outputs.；Use contrastive learning with negative examples that share API usage but differ in semantics.

### case_id=2646 FN partial_functionality

- 方法: `copyResource` vs `copyTextFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using unbuffered byte-by-byte streaming, throwing an exception on failure.
- B 摘要: Copies a source file to a destination file using buffered chunked streaming, returning a boolean indicating success and logging errors.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token similarity and surface form; low Jaccard (0.17) and differences in method signatures, I/O patterns, and error handling caused misclassification. They missed the high-level semantic similarity of copying data from input to output.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels as clones functions that share core functionality (file copying) even with different implementations (buffered vs unbuffered, different error handling), considering partial functional similarity sufficient.
- 共享行为: Both copy content from an input source to an output file using byte-level I/O；Both close streams after operation
- 行为差异: A supports both URL and file source; B only file；A uses unbuffered single-byte reads; B uses buffered 1024-byte chunks；A throws exception on failure; B returns false and logs；A does not flush; B flushes output
- 修正建议: Improve models to focus on core data flow (input-stream-to-output-stream pattern) rather than exact API calls；Incorporate program slicing or data flow analysis to identify byte-copying loops；Augment training data with more diverse implementations of the same functionality

### case_id=2647 FN benchmark_preference_bias

- 方法: `cpFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.5`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file from source to target with replacement and buffer size options.
- B 摘要: Builds an edited version of a website by processing XML, performing transformations, and writing output files.
- 静态失败原因: Static BERT models rely heavily on lexical overlap and surface-level similarity. The token Jaccard is low, and the code structures are very different. The model likely correctly identified them as non-clones based on semantics, but it failed to match the BCB label because the BCB label may be incorrect or based on a different notion of similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both methods involving file reading and writing, and because both have a similar pattern of opening input and output streams. However, this is a very weak similarity, and likely the BCB annotation is erroneous or based on a broader interpretation that includes any file-copy-like behavior.
- 共享行为: Both perform file input and output operations.
- 行为差异: A is a straightforward file copy; B involves multiple processing steps including XML transformation, string replacement, and handling of many configuration parameters.；B processes multiple pages in a loop; A handles a single file.；A has a mechanism for unique file names when target exists and replacement is false; B does not have such logic.
- 修正建议: Review BCB annotation for correctness; this pair may be a mislabel in the benchmark.；If BCB style is to be followed, incorporate additional similarity heuristics like file I/O patterns.；Improve model to better handle semantic differences in complex functions.

### case_id=2648 FN partial_functionality

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, unzips it, and extracts its contents to the current directory.
- B 摘要: Copies a file from one location to another using NIO FileChannel, with a check to avoid copying to the same file.
- 静态失败原因: Low token overlap (0.18) and different method names; the model likely focused on surface-level differences and missed the abstract I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both involve reading from an input stream and writing to an output stream (file I/O), a broad Type-4 similarity.
- 共享行为: Both read data from a source and write to a destination；Both perform file I/O operations
- 行为差异: Function A downloads from an HTTP URL, unzips, and writes multiple files; Function B copies a single file using FileChannel；Function A uses ZipInputStream and BufferedOutputStream; Function B uses FileChannel.transferTo；Function B has a canonical path check to avoid self-copy; Function A does not
- 修正建议: Incorporate dataflow or I/O operation recognition；Use code summarization to capture high-level intent；Augment training data with more diverse I/O patterns

### case_id=2649 FN partial_functionality

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a remote KMZ file and extracts its zip entries to local files.
- B 摘要: Copies a local file to a destination file with a given buffer size and force overwrite option.
- 静态失败原因: Static models like GraphCodeBERT may focus on high-level API calls and method names, missing the underlying similarity of the stream copying pattern. The differences in URL vs file and ZIP vs plain copy overshadowed the common loop structure.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs as clones if they share a common I/O pattern such as reading from a stream and writing to another with buffering, even if one involves additional extraction logic. The structural similarity in the data transfer loop is strong enough for a positive BCB label.
- 共享行为: Both read from an input stream and write to an output stream.；Both use a byte buffer in a loop to transfer data.；Both close streams after use.
- 行为差异: A downloads from a URL and handles ZIP format; B copies local files without compression.；A prints progress messages; B handles overwrite control with a force flag.；A uses ZipInputStream and ZipEntry; B uses plain InputStream and OutputStream.
- 修正建议: Use a dataflow-aware model that captures the core data transfer loop.；Incorporate structural features like loop patterns and stream usage.；Consider fine-tuning on pairs with partial functionality overlap.

### case_id=2650 FP boilerplate_overlap

- 方法: `getUser` vs `setMembers`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from a DAO or parses a colon-delimited config file to create and save a user.
- B 摘要: Fetches a Trac newticket page and extracts component and priority options from HTML select elements into static arrays.
- 静态失败原因: The model likely over-weighted the generic I/O pattern (URL, BufferedReader, while loop with readLine) and missed the semantic context of the core operations (user authentication vs. HTML parsing).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: Even under broad Type-4 (functionally similar but different implementation), these functions perform completely different tasks; the only overlap is generic I/O boilerplate, which is insufficient for a clone label.
- 共享行为: Both use BufferedReader to read line by line from a URL stream.
- 行为差异: Different purposes: user authentication vs. web scraping.；Different data structures: User object vs. static String arrays.；Different dependencies: UserDAO vs. Trac URL and HTML parsing.；A has a parameter and returns a value; B is void and static.
- 修正建议: Incorporate dataflow and type information to distinguish core logic from I/O boilerplate.；Use method signatures and return types as additional features.；Focus on the actual data transformations and external dependencies.

### case_id=2651 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a new version of jEdit by reading version/build info from a URL.
- B 摘要: Downloads an RDF model from a URL and returns it.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on lexical overlap of API calls (URL, InputStream, IOException) and control flow (try-catch), ignoring the distinct domain-specific logic and data processing that differ fundamentally.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers non-clones when the similarity is limited to common I/O boilerplate (URL opening, stream reading) without shared core functionality. The overall semantics are unrelated.
- 共享行为: Both open a URL and read from an InputStream.；Both handle IOException.
- 行为差异: Different purpose: version check vs model download.；Different data processing: parsing lines for version/build vs reading RDF model.；Different error handling: GUI messages vs logging and throwing RuntimeException.；Different parameters and return types.
- 修正建议: Improve model to consider the purpose and data transformations beyond surface API calls.；Add contrastive training with negative examples that share API sequences but differ in logic.；Incorporate data flow and control flow analysis to distinguish different operations on the same data types.

### case_id=2652 FP other

- 方法: `readData` vs `internalCopy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads string tokens from multiple predefined variables, populates several HashSets and a HashMap with those tokens, and performs additional processing.
- B 摘要: Copies a file from source to destination using a byte buffer.
- 静态失败原因: Likely due to boilerplate code or specific API tokens (e.g., HashSet, StringTokenizer, FileInputStream) that may have matched in embedding space, or the model was not sensitive enough to overall control and data flow.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB requires semantic equivalence for clone labeling, and these functions have entirely different semantics, so BCB correctly labels as non-clone.
- 共享行为: Both are private methods；Both handle some data manipulation
- 行为差异: A processes string tokens and populates data structures; B copies file bytes；A has no file I/O; B uses file I/O streams；A has complex logic with fall-through in switch; B is simple sequential stream copy
- 修正建议: Train with more diverse negative pairs；Incorporate data flow or control flow analysis；Use contrastive learning to distinguish different functionalities

### case_id=2653 FN partial_functionality

- 方法: `readGeoParserResult` vs `setMembers`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads geo-parser results by sending an XML request to a URL and parsing the response to extract place names and gazetteer IDs.
- B 摘要: Sets component and priority members by fetching a Trac new ticket page and parsing HTML select options using regex.
- 静态失败原因: The functions have low lexical overlap (token Jaccard 0.16) and operate on different domain-specific terms, causing static BERT models to miss the abstract structural similarity in data flow and parsing logic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions implement a similar pattern: fetching data from a URL, parsing it (XML/HTML), and extracting structured information, which fits a broad Type-4 semantic clone category despite different domains.
- 共享行为: Both open a URL and read its content line by line.；Both parse the retrieved content using pattern matching or document parsing.；Both extract specific values and store them in collections.；Both handle IO exceptions.
- 行为差异: Function A constructs an XML request based on input; B fetches a fixed URL.；A parses XML with XPath; B parses HTML with regex.；A includes retry logic with up to 3 attempts; B has no retry.；A extracts place names and IDs; B extracts component and priority names.
- 修正建议: Enhance training data with more examples of web-scraping semantic clones across domains.；Incorporate structural or graph-based representations (e.g., data flow graphs) to capture shared patterns.；Use contrastive learning or fine-tuning on functional similarity rather than token overlap.

### case_id=2654 FN boilerplate_overlap

- 方法: `readGeoParserResult` vs `startScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Constructs an XML request to a geo parser service, sends it, and parses the response to extract place names and gazetteer IDs.
- B 摘要: Reads a script from a URL and appends it to a dialog object.
- 静态失败原因: Static models focused on lexical overlap (BufferedReader, URL, readLine) and missed the distinct core logic (XML construction, retries, return type), leading to a false negative.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as 'reading from a URL and processing lines', a common pattern, and thus label them clones despite different contexts.
- 共享行为: Both open a URL and read its content line by line using BufferedReader；Both handle IO errors with a try-catch block
- 行为差异: Function A builds an XML request and processes XML response; function B does not.；Function A has retry logic on failure; function B exits on error.；Function A returns a collection of tuples; function B returns void and modifies a dialog.
- 修正建议: Use models that capture dataflow and program structure beyond token sequences；Incorporate task-level context or discriminative features like I/O boundaries

### case_id=2655 FN benchmark_preference_bias

- 方法: `readData` vs `getWebByUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Initializes multiple sets and maps from string fields and a file for Tibetan transliteration configuration.
- B 摘要: Downloads a web page from a URL, saves it to a file, and recursively processes links.
- 静态失败原因: The model correctly identified no semantic similarity (low token Jaccard, different purpose), but BCB label is 1, causing a false negative.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'data loading' functions, but this is overly broad and likely a labeling error.
- 共享行为: Both read data from an input source (string/file vs URL) line by line
- 行为差异: A primarily populates in-memory collections; B writes to a file and invokes recursive URL processing.；A uses StringTokenizer and parsing of predefined string fields; B uses URL connection and HTTP streaming.；A has extensive error handling for file format; B handles network exceptions and reports success/failure.；A is a private static initializer; B is a public instance method.
- 修正建议: Review BCB annotation: these functions are not clones even by broad Type-3/4 standards.；Consider filtering out pairs with very low token overlap and obviously different domain/purpose.

### case_id=2656 FN benchmark_preference_bias

- 方法: `setImg` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Selects an image file via JFileChooser, copies it to an images directory, and sets it as a background image.
- B 摘要: Launches a NexOpen project by validating and processing Maven pom.xml files, configuring Hibernate dialect, and triggering an install project action.
- 静态失败原因: Static BERT likely correctly identified no semantic similarity; the BCB label appears to be a false positive, so the model did not fail but rather disagreed with a possibly erroneous annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB annotation may be an error or based on a very broad interpretation of 'setup' functionality, but no meaningful shared semantics.
- 共享行为: Both perform file I/O operations；Both contain error handling with try-catch blocks
- 行为差异: One is a simple GUI image setter, the other is a complex Eclipse launch configuration handler；Different domains: image processing vs. project build configuration；No overlap in APIs or logic
- 修正建议: Review and correct BCB annotation for this pair；Improve annotation guidelines to reduce false positives

### case_id=2657 FP lexical_or_api_overlap

- 方法: `loadSourceCode` vs `readZoneIDs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a source file line by line, applies syntax highlighting, and accumulates HTML string with highlighted lines.
- B 摘要: Reads a file of zone IDs line by line, parses each line as an integer, and returns a set of those integers.
- 静态失败原因: Static BERT models often rely on lexical and structural overlap. The high API overlap (getResource, openStream, InputStreamReader, readLine) and similar control flow likely dominated the representation, causing the model to overlook the critical semantic differences in loop body operations and output type.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone (0) because the functions have completely different purposes (HTML generation vs. integer set building) despite sharing a common file-reading loop. BCB typically requires functional similarity beyond just I/O pattern.
- 共享行为: Both read a resource file line by line using similar API calls (getClass().getResource, openStream, InputStreamReader).；Both use a while loop to read lines until null.；Both handle exceptions with a generic catch block.
- 行为差异: A builds an HTML string with syntax highlighting; B builds a HashSet<Integer>.；A stores result in a field; B returns the set.；A adds line breaks and HTML tags; B parses each line as an integer.；A uses BufferedReader; B uses LineNumberReader.
- 修正建议: Train with contrastive examples emphasizing loop body semantics.；Incorporate dataflow analysis to track variable transformations.；Use type information (return type, field assignments) as discriminative features.

### case_id=2658 FN boilerplate_overlap

- 方法: `modifyApplicationMessage` vs `Converter`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file by replacing or adding a key-value pair for a specified locale.
- B 摘要: Converts a file from SJIS to UTF8 encoding by copying with a buffer.
- 静态失败原因: Static model relies on token overlap (low) and method name, missing the broad functional alignment based on I/O structure that BCB might have used.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as file I/O utilities with similar boilerplate, possibly labeling as Type-4 based on high-level functional similarity of 'file transformation'.
- 共享行为: Both read from a file；Both write to a file using Writer classes；Both use try-catch for exception handling
- 行为差异: A parses lines as key-value pairs; B copies fixed-size char buffers；A creates files conditionally; B only opens existing files；A modifies content; B only changes encoding
- 修正建议: Incorporate structural similarity of I/O patterns；Use functional flow analysis to distinguish different transformations

### case_id=2659 FN partial_functionality

- 方法: `main` vs `createNew`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a ZIP file from a URL and extracts its entries to files.
- B 摘要: Writes an InputStream to a file in a managed directory after an ownership check.
- 静态失败原因: Low token Jaccard (0.134) and different API usage (BufferedOutputStream vs. IOUtils.copy, ZipInputStream vs. FileOutputStream) cause the static model to miss the shared I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both functions as performing file output from an input stream, a common pattern, and overlook the additional context as boilerplate.
- 共享行为: Both write data from an input stream to a file output stream.
- 行为差异: A handles URL connection and ZIP extraction; B does not.；A does not perform ownership checks; B includes ownership logic.；A uses a hardcoded URL; B takes parameters.；A writes to the current directory; B writes to a managed file path.
- 修正建议: Incorporate data flow analysis to detect that both functions ultimately write an InputStream to a FileOutputStream.；Normalize API calls to abstract patterns like 'stream copy'.

### case_id=2660 FN partial_functionality

- 方法: `copyResource` vs `logging`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using byte-by-byte stream copy.
- B 摘要: Logs inbound message by reading content from an InputStream, caching it, and writing to a log buffer with truncation.
- 静态失败原因: Low token overlap and different API usage (simple loop vs IOUtils.copy) make the model miss the underlying stream-copy pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as stream copy patterns (Type-4), viewing them as functionally similar in transferring data from an InputStream to an OutputStream, even though the context and additional behavior differ.
- 共享行为: Both read from an InputStream and write to an OutputStream or buffer.；Both handle resource closure and error handling.
- 行为差异: A copies raw bytes to a file; B logs message to a buffer with caching and truncation.；A uses simple byte loop; B uses IOUtils.copy and CachedOutputStream.；A throws Exception; B throws Fault.；B includes logging and encoding/header handling not present in A.
- 修正建议: Augment training data with diverse implementations of stream copy.；Incorporate functional or structural analysis focusing on input-output data flow.；Use models that capture high-level I/O patterns beyond lexical similarity.

### case_id=2661 FN benchmark_preference_bias

- 方法: `main` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a source file to multiple target files using FileChannel, with optional SVN operations.
- B 摘要: Downloads a KMZ file from a URL and extracts all zip entries to files.
- 静态失败原因: Static BERT models correctly detected low lexical and structural similarity, predicting non-clone, which contradicts BCB's broad labeling.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: None
- 共享行为: Both are main methods that perform file I/O operations and print progress.；Both process multiple items in a loop.；Both use InputStream/OutputStream/FileChannel.
- 行为差异: A uses local file system and FileChannel; B uses URL and ZipInputStream.；A copies file content; B extracts zip entries.；A includes SVN integration; B does not.；A handles command-line arguments; B uses hardcoded URL.
- 修正建议: Clarify BCB annotation guidelines to distinguish partial functionality clones from true semantic clones.；For static models, incorporate functional-level features or use program analysis to capture high-level intent.

### case_id=2662 FN other

- 方法: `decodeFileToFile` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Decodes a Base64-encoded input file and writes the decoded bytes to an output file.
- B 摘要: Modifies a locale-specific properties file by replacing the value of a given property name, or appending it if not present.
- 静态失败原因: The static model correctly predicted non-clone; the error is in the BCB label. If assuming model should match BCB, it failed because of low token overlap (0.206) and different method names, but semantic analysis confirms they are not clones.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely incorrectly labeled this as clone due to superficial similarity in file I/O structure and resource management, ignoring completely different domain logic.
- 共享行为: Both perform file I/O with stream operations；Both use try-catch-finally for exception handling；Both close resources in finally block
- 行为差异: Function A decodes Base64 data; Function B modifies text properties file；Function A uses binary byte streams; Function B uses character streams；Function A writes decoded bytes directly; Function B reads, parses, modifies, and writes text lines
- 修正建议: Verify BCB label for potential mislabeling；Improve model to capture deeper semantic differences beyond surface I/O patterns

### case_id=2663 FN benchmark_preference_bias

- 方法: `getFile` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint attribute, and saves it to a local temporary file.
- B 摘要: Converts an ACRNEMA stream file to DICOM format by adding UIDs and handling pixel data, with format validation.
- 静态失败原因: The model correctly predicted non-clone because the token overlap is very low (0.117), method names differ, and the logic is semantically unrelated. It did not fail; it correctly rejected the pair.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to both being 'file processing utilities' that involve downloading/converting files, but this is an overly broad interpretation that ignores the entirely different domains and operations.
- 共享行为: Both perform file I/O operations (reading and writing files).；Both use streams and handle exceptions (IOException).；Both involve conditional logic based on file existence or content.
- 行为差异: Function A downloads from a URL and modifies XML/WSDL; Function B converts a medical image format.；Function A uses URL connections and XML parsing; Function B uses DICOM-specific parsing and pixel data manipulation.；Function A writes to temporary files and renames; Function B writes directly to a destination file.；Function A has multiple exception types (MalformedURLException, ParserConfigurationException, SAXException); Function B only throws IOException.
- 修正建议: Re-evaluate BCB annotation for this pair as it appears to be a false positive in the benchmark.；Consider using more domain-specific or structural features to avoid over-generalization.

### case_id=2664 FN lexical_or_api_overlap

- 方法: `addIDs` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses metabolite IDs from a web service to update a peak list row.
- B 摘要: Reads a skeleton property file and splits it into sections.
- 静态失败原因: Static BERT model correctly predicted non-clone (0). It did not fail; it accurately captured the semantic difference.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as clone due to superficial similarity: both functions open a URL, read lines with BufferedReader, and assign values to an object. This could be considered Type-3 (near miss) under a lenient interpretation, but the actual semantics differ significantly.
- 共享行为: Both use BufferedReader to read from an input stream obtained from a URL.
- 行为差异: Function A parses HTML/XML responses to extract metabolite IDs and scores, while function B splits lines based on a delimiter.；Function A modifies a PeakListRow object with multiple fields, while function B appends to a list of sections.；Function A handles HTTP URLs, function B handles classpath resources.；Function A has try-catch for IOException, function B throws Exception.
- 修正建议: Improve AST or flow analysis to distinguish trivial I/O pattern from actual business logic.；Use data-flow analysis to trace how parsed data is used, revealing different purposes.；Consider domain-specific knowledge (metabolite database vs. property file) to avoid false positives from BCB.

### case_id=2665 FN benchmark_preference_bias

- 方法: `doTransfer` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request to a specified URL, copying headers and body, and returns the response.
- B 摘要: Reads a file from the file system or classpath and returns its content as a string.
- 静态失败原因: Static BERT models rely on lexical and structural similarities; here token Jaccard is low (0.15873), and the overall structure differs (HTTP handling vs file reading). The model failed to recognize the abstract I/O pattern similarity that BCB annotators considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone because both functions perform input stream reading and output data processing (stream copy pattern), despite different contexts. The broad definition of Type-4 clones can include functional similarity in data processing.
- 共享行为: Both use InputStream and BufferedReader/InputStreamReader to read data.；Both perform I/O operations with error handling using try-catch blocks.；Both read data in chunks and process it sequentially.
- 行为差异: Function A handles HTTP request/response lifecycle (headers, status codes), while B only reads a file.；Function A writes to an output stream, whereas B concatenates to a StringBuffer.；Function A involves network communication; B is local file I/O.
- 修正建议: Incorporate more Type-3 and Type-4 clone examples in training data.；Use graph-based representations to capture data flow and I/O patterns.；Fine-tune with BCB-style annotations to adapt to broader clone definitions.

### case_id=2666 FP lexical_or_api_overlap

- 方法: `main` vs `setup`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter code and JAR from a Prolog file, parsing and transforming it with various visitors and writers.
- B 摘要: Extracts native library files from a JAR file and sets up the library path based on the operating system architecture.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on lexical overlap (e.g., 'File', 'IOException', 'System.out.println') and boilerplate error handling, mistaking superficial similarity for functional equivalence.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functionalities are completely different: one is a code generator, the other is a native library extractor. Despite similar API usage patterns, the core semantics diverge.
- 共享行为: Both read from files and perform I/O operations.；Both involve checking file existence and handling exceptions.；Both print status messages to standard output.
- 行为差异: Code A parses Prolog and generates bytecode; Code B extracts native libraries from a ZIP/JAR.；Code A uses complex OOP patterns (visitors, writers, generators); Code B uses simple stream copying.；Code A writes output JAR file; Code B creates temporary directory and modifies library path.；Code A handles command-line arguments; Code B uses hardcoded paths and system properties.
- 修正建议: Enhance model with dataflow analysis to distinguish variable roles.；Include target method calls and object types for better semantic understanding.；Use larger context or structural comparison of control flow.；Incorporate task-aware embeddings (e.g., generation vs. extraction).

### case_id=2667 FN boilerplate_overlap

- 方法: `modifyApplicationMessage` vs `doRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by updating or adding a key-value pair for an application message.
- B 摘要: Serves a static resource file as an HTTP response based on the request path and alias.
- 静态失败原因: The static model correctly identified them as non-clones under strict semantic equivalence, but failed to align with a potentially broader BCB annotation that may accept high-level functional similarity based on I/O boilerplate.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have considered this a Type-4 clone due to both functions involving reading from a source and writing to a destination, which can be seen as functionally similar at a high level of abstraction, though the specifics differ greatly.
- 共享行为: Both read from a file/resource using InputStream.；Both write to an output stream (FileWriter/OutputStream).；Both handle I/O exceptions (though differently).
- 行为差异: A modifies a properties file with line-by-line parsing and key-value replacement; B copies a resource stream directly to HTTP response.；A handles locale-specific file creation and missing key appending; B handles alias path checking and MIME type setting.；A writes to a file on disk; B writes to an HTTP response output stream.；A returns void; B returns boolean indicating success.
- 修正建议: Incorporate dataflow analysis to differentiate core logic from boilerplate I/O.；Train with more diverse examples of Type-4 clones to capture broader functional similarity.；Use graph-based methods to better abstract functional intent beyond lexical similarity.

### case_id=2668 FN partial_functionality

- 方法: `doPost` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles HTTP POST multipart form data by extracting a webpage and URL, then generating a mailer and writing it to the response output stream.
- B 摘要: Retrieves a resource by URL with local caching, returning an InputStream after possibly downloading and caching the content to a file.
- 静态失败原因: The static BERT/GraphCodeBERT model relies heavily on token overlap and syntactic structure; the low token Jaccard (0.098) and different method names, control flow, and purpose caused the model to miss the underlying I/O pattern similarity that BCB annotators considered relevant. The model failed to recognize the clone due to low lexical overlap and different high-level context.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones due to shared low-level I/O operations (URL opening, stream reading/writing, exception handling) which are considered a generic 'resource fetching' or 'file I/O' functionality, even though the high-level purposes differ significantly. The broad Type-3/Type-4 criteria often accept such partial functionality similarity.
- 共享行为: Open URL connections to fetch remote content；Read input streams and copy data using IOUtils or similar；Handle exceptions with try-catch blocks and cleanup of streams；Use BufferedInputStream, BufferedOutputStream, and ByteArrayOutputStream
- 行为差异: A is a servlet doPost handler; B is a resource caching method；A processes multipart form data (webpage, weburl); B directly opens a URL from a string name；A writes to the HTTP response output stream; B caches to a file on disk and returns InputStream；A uses ToMailerDelegate to generate a mailer; B uses cacheHashtable for caching metadata
- 修正建议: Incorporate dataflow analysis or program slicing to extract common I/O sub-patterns across functions；Train models on broader clone benchmarks that include partial functionality clones；Use graph-based representations that capture API usage and stream flows independent of surrounding code

### case_id=2669 FN partial_functionality

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination directory using a buffer.
- B 摘要: Launches a NexOpen project configuration, involving Maven pom handling, property setting, and resource file creation.
- 静态失败原因: Low lexical overlap (0.053) and different method names/signatures likely caused the model to predict non-clone, but BCB may consider them clones due to abstract file handling similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might label these as clones due to both involving file I/O operations (e.g., reading/writing streams), despite different overarching purposes.
- 共享行为: Both use file I/O streams; method B contains a small file copy sub-operation.
- 行为差异: Method A is a simple file copy; method B is a complex launch initialization.；Method B involves XML parsing, project configuration, and resource management; method A does not.；Method B has extensive error handling and logging; method A only has a catch clause.
- 修正建议: Improve semantic understanding of nested operations; consider data flow of file handling as a possible clone signal.

### case_id=2670 FN partial_functionality

- 方法: `getFile` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Downloads a WSDL file from a URL, modifies its wsdlsoap:address location, and saves it to a temporary file, returning the file path.
- B 摘要: Copies the content of one file to another using FileReader and FileWriter.
- 静态失败原因: Static BERT models often rely on lexical and structural similarity, which is very low (token Jaccard=0.0625). They fail to capture the high-level semantic similarity of file copying due to different API usage and surrounding code.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as Type-4 clones because they both perform file copy operations, albeit with different sources (network vs file) and additional complexity in A. The core behavior of reading from a source and writing to a destination is shared.
- 共享行为: Both functions transfer data from a source to a destination file.
- 行为差异: Function A involves network I/O and XML modification, while function B only does local file copy.；Function A uses NIO channels for efficient transfer; function B uses character streams.；Function A handles complex error handling and logging; function B is simple with single exception.
- 修正建议: Improve model's ability to recognize partial functionality clones.；Use data flow or graph representations to capture common operations like file copy.；Train on more Type-4 clone examples with diverse implementations.

### case_id=2671 FP long_range_semantics

- 方法: `testIdentification` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: A JUnit test that verifies user identification by mocking dependencies and using MD5.
- B 摘要: A Struts action that processes form input, builds XML, sends HTTP request, and handles classification result.
- 静态失败原因: The model likely over-relied on superficial similarities like try-catch blocks, loops, or common API names (e.g., 'getBytes', 'MessageDigest' in A vs. 'ErrorMessages' in B) while missing the overall semantic context due to long code length.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels based on functional similarity; these two functions perform entirely different tasks (authentication test vs. web request processing), so they are not clones.
- 行为差异: Function A is a test, B is production logic；A uses mocking framework, B interacts with real HTTP；A involves MD5 hashing, B involves XML/HTTP；A has no I/O, B does network I/O
- 修正建议: Use cross-context contrastive learning to penalize dissimilar semantics；Incorporate control-flow or data-flow graphs to capture execution intent；Augment training with more diverse non-clone pairs

### case_id=2672 FN benchmark_preference_bias

- 方法: `getResourceAsStream` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Retrieves a resource from a URL with caching to local file system.
- B 摘要: Reads a DICOM image file and rewrites it to another file.
- 静态失败原因: The static model likely failed because it captured the low lexical similarity and recognized the different domains and operations. It correctly identified them as non-clones, while BCB label might be erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as clone due to both functions involving file I/O and stream manipulation, but this is a very broad Type-4 similarity. However, the core functionality is completely different, so it's likely a mislabel.
- 共享行为: Both handle file input/output with buffered streams；Both print progress messages to standard output.
- 行为差异: Function A fetches resources from a network URL with caching logic; Function B processes DICOM medical image files.；Function A manages a cache directory and uses URL connections and HTTP; Function B uses DICOM-specific libraries for parsing and writing pixel data.；Function A returns an InputStream; Function B writes to a file and has void return.
- 修正建议: Improve benchmark annotation consistency；Use more fine-grained clone types；Incorporate domain knowledge.

### case_id=2673 FP boilerplate_overlap

- 方法: `perform` vs `decode`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles HTTP classify request, processes concept data, sends POST to external service, and manages session attributes.
- B 摘要: Decrypts a byte array using password-based key derivation with hashing and symmetric cipher.
- 静态失败原因: Likely misled by boilerplate patterns such as try-catch blocks, loops, and common Java imports, while ignoring the entirely different domain-specific logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones based on functional dissimilarity; these functions share no common purpose or logic.
- 行为差异: One is a web action handler, the other is a cryptographic decryption function.；Different input/output: A returns ActionForward, B returns byte[].；A involves HTTP communication and session management; B involves cryptographic primitives.；Control flow: A has complex conditional branching; B is a linear sequence of cryptographic operations.
- 修正建议: Train on more diverse datasets to reduce reliance on surface-level patterns.；Incorporate dataflow analysis to capture actual semantics.；Use contrastive learning to distinguish between different functional domains.

### case_id=2674 FP lexical_or_api_overlap

- 方法: `getUser` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves a User object from DAO or parses a configuration file by login name.
- B 摘要: Sends an HTTP POST request to a target URL with parameters and returns the response string.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-emphasized lexical overlap of common Java API tokens (URL, BufferedReader, try-catch) and ignored semantic differences in method intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have different names, parameters, and overall purpose despite some shared I/O patterns.
- 共享行为: Both use URL and open connections/streams；Both read from streams using BufferedReader；Both handle exceptions with try-catch and print stack traces
- 行为差异: Function A loads user data; function B performs network I/O；Function A returns User object; function B returns String；Function B sends data (POST) and reads response; function A only reads data；Function A includes parsing of tokens from a config file; function B does not
- 修正建议: Incorporate method name and signature information into the model；Use dataflow or control flow graphs to capture distinct behaviors；Apply attention to higher-level semantics, such as the type of data being processed

### case_id=2675 FP lexical_or_api_overlap

- 方法: `setBundleInfoName` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a bundle info file from a URL and updates the bundle names in a given list based on key-value pairs.
- B 摘要: Reads a service configuration file from the classpath, loads the specified framework factory class, and returns a new instance.
- 静态失败原因: The static BERT model likely overemphasized the lexical and API overlap (URL, BufferedReader, readLine, string parsing) and the similar control flow structure, ignoring the critical difference in what is done with the parsed data.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone (0) because the functions have entirely different purposes and outputs, despite sharing some I/O boilerplate. BCB typically requires substantial functional overlap for Type-3/4 clones.
- 共享行为: Both open a URL resource and read lines with BufferedReader；Both use a while loop or for loop to iterate over lines
- 行为差异: Function A modifies a list of BundleInfo objects; Function B instantiates a class and returns it；Function A returns boolean success/failure; Function B returns a FrameworkFactory or throws Exception；Function A reads from an arbitrary URL parameter; Function B reads from a fixed classpath resource
- 修正建议: Enrich training data with negative pairs that share I/O patterns but diverge in downstream logic；Use data flow or program dependence graphs to capture the purpose of parsed data；Apply contrastive learning to distinguish syntactic similarity from semantic equivalence

### case_id=2676 FP boilerplate_overlap

- 方法: `readScalarpvviewerDocument` vs `parse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads an XML configuration from a URL to set up a GUI scalar PV viewer.
- B 摘要: Parses a delimited text file or URL into a DataSet using a tokenizer.
- 静态失败原因: Static BERT likely overemphasized lexical overlap like 'BufferedReader', 'url.openStream()', and 'while' loops, missing the semantic gap in domain-specific logic and output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions serve entirely different domains (specific XML viewer vs generic data parser) and share only common I/O boilerplate.
- 共享行为: Both read input from a URL or file using BufferedReader；Both use try-catch for IOException
- 行为差异: A uses XML-specific parsing and updates GUI components; B parses delimited text and returns a DataSet；A uses XmlDataAdaptor; B uses StreamTokenizer；A sets up viewer parameters; B handles headers and types generically
- 修正建议: Incorporate dataflow to track how parsed data is used；Emphasize method names and return types；Use structure-aware embeddings that capture API call differences

### case_id=2677 FN benchmark_preference_bias

- 方法: `combineJs` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Combines multiple JavaScript files from URLs, minifies/concatenates them, and saves the result to a file, returning the modified HTML element.
- B 摘要: Downloads a KMZ file from a URL, extracts its entries using ZipInputStream, and writes each entry to a separate file.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on lexical token overlap and syntactic structure, which are low (Jaccard=0.13) and very different between these functions. They fail to capture the abstract, high-level similarity of URL-to-file streaming operations because the data flow and control flow diverge significantly.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider these as Type-4 clones due to the common high-level pattern of 'fetching data from a URL and writing it to local files', despite different file formats and post-processing steps. The annotation preference accepts partial functional similarity if the core I/O behavior aligns.
- 共享行为: Both open a URL and read an input stream.；Both write data to output files on the local filesystem.；Both handle I/O exceptions and manage resources like streams.
- 行为差异: Function A processes multiple JS files with optional minification and concatenation; Function B extracts a single zip archive and writes each entry separately.；Function A involves file naming, temporary directories, and conditional logic based on minification failures; Function B simply extracts all entries without such logic.；Function A returns a modified HTML element; Function B has no return value (void).
- 修正建议: Train models with broader clone definitions that include Type-4 functional similarity.；Incorporate data flow features that highlight resource handling patterns (open, read, write).；Use contrastive learning on pairs that share only high-level behavior but differ syntactically.

### case_id=2678 FP partial_functionality

- 方法: `readTwitterFead` vs `handledRun`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a fixed Twitter timeline JSON feed over HTTP and returns the response body as a string.
- B 摘要: Downloads a gamedata XML file from a remote server if a newer version is detected, writes it to a local file, and updates game data.
- 静态失败原因: A static BERT model may have overgeneralized the presence of common API patterns (URL, BufferedReader, try-catch) and both being 'network download' tasks, ignoring the distinct control flow, side effects, and output types. The low token Jaccard (0.097) suggests limited lexical overlap, but the model might have relied on structural similarity of I/O loops.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotates these as non-clones because the core functionality differs significantly: one is a simple HTTP fetch returning a string, the other is a conditional file download with versioning and state updates. Even under broad Type-4/partial similarity, the behavioral differences outweigh the shared network I/O pattern.
- 共享行为: Both perform network I/O (HTTP GET or URL.openStream) to download data from a remote server.；Both read data from an input stream using a BufferedReader.；Both handle exceptions (IOException, Exception).
- 行为差异: Function A returns a string of the response body; Function B modifies local files and game state.；Function A uses HttpClient; Function B uses URL.openStream().；Function B includes version checking, conditional download, and file writing; Function A does not.；Function B has a finally block that reloads game databases; Function A does not.
- 修正建议: Incorporate explicit detection of side effects (file writes, state changes) and return types.；Use dataflow analysis to distinguish between pure data retrieval and stateful downloads.；Train with more fine-grained labels that separate 'fetch data' from 'update local resources'.

### case_id=2679 FN partial_functionality

- 方法: `run` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads all lines from a local URL but discards them, catching exceptions silently.
- B 摘要: Reads all lines from an external URL, accumulates them in a StringBuffer, and logs the result, throwing exceptions.
- 静态失败原因: The model likely focused on token-level differences such as method name, exception handling clauses (empty catch vs throws), and variable names, and also the low Jaccard similarity discouraged clone classification. The model may not capture the structural similarity of read-loop pattern due to tokenization differences (e.g., 'BufferedReader', 'URL', 'readLine').
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often annotates broad functional similarity as clone, especially when both snippets perform core functionality of opening a URL and reading its contents line by line, despite differences in error handling and post-processing. This pair is considered Type-3 due to small modifications.
- 共享行为: Both create a URL object pointing to a web resource；Both open an input stream to the URL；Both read all lines from the response using a BufferedReader in a loop；Both close the reader after reading
- 行为差异: Function A discards the content read, while Function B stores it in a StringBuffer and logs it；Function A has empty catch blocks for MalformedURLException and IOException, Function B throws Exception；Function A uses url.openStream() directly, Function B uses url.openConnection().getInputStream()；Function A does not include any logging, Function B logs the response
- 修正建议: Use data augmentation to emphasize structural patterns over lexical details；Incorporate dataflow or control flow features to recognize similar loop and stream patterns；Include more examples of partial-functionality clones in training

### case_id=2680 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `transformSingleFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a specific locale by updating or adding a message key-value pair.
- B 摘要: Compresses an X3D file to a GZIP file and returns the output path.
- 静态失败原因: The model correctly identified the functions as non-clones (strict semantics), so it did not fail under typical clone detection. However, BCB's label contradicts strict semantics, so the 'failure' is in matching the benchmark's preference, not in semantic understanding.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled as clone due to superficial structural similarity: both open files, process data line-by-line (or byte-by-byte), and write output. The benchmark may have a broad interpretation of Type-3 clones, but this pair has no functional overlap.
- 共享行为: Both perform file I/O operations using File, FileReader, FileWriter, FileInputStream, FileOutputStream.；Both handle exceptions with try-catch blocks.
- 行为差异: Function A modifies properties files (key-value replacement), while B compresses binary data.；A reads lines and processes text; B reads bytes and writes compressed output.；A is void; B returns a string path.；A copies a default file if locale file missing; B does not.
- 修正建议: Re-examine BCB annotations for this pair; likely a false positive that should be corrected.；If maintaining BCB style, consider adding more context to distinguish simple file-processing loops from actual clone pairs.；Model's prediction is correct; no fix needed for the model.

### case_id=2681 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft handshake by validating username and optionally sending an HTTP request to session server to join.
- B 摘要: Checks for jEdit version update by reading a version URL and parsing version/build lines.
- 静态失败原因: Lexical overlap (both use URL, BufferedReader, InputStreamReader, try-catch) and similar API calls caused the model to overestimate similarity, failing to capture the high-level semantic difference in domain and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions serve entirely different purposes (Minecraft login vs jEdit version check) despite sharing network I/O boilerplate.
- 共享行为: Both open a URL with URL and openStream；Both read lines with BufferedReader and InputStreamReader；Both close the stream and handle exceptions；Both conditionally act based on response content
- 行为差异: Different domain: Minecraft login vs jEdit version check；Different input: Packet2Handshake vs View；Different output: network shutdown/addToSendQueue vs GUI messages；A has username validation before HTTP request, B does not
- 修正建议: Train with more diverse examples where similar API usage occurs in different domains；Incorporate task-oriented embeddings or domain context；Use data flow analysis to distinguish different control flow sequences

### case_id=2682 FN benchmark_preference_bias

- 方法: `getFile` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint attribute, and saves to a temporary file.
- B 摘要: Parses an XML input, modifies the DOM (adds a label attribute if missing), and generates a XUL extension package as a ZIP output.
- 静态失败原因: Static BERT models rely heavily on token overlap and structural similarity, which are low here. They fail to capture abstract conceptual similarity that BCB annotators might have considered (both being 'utility methods that process XML and write output').
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions involving XML parsing and file I/O, despite the entirely different domain-specific logic and end results.
- 共享行为: Both use Java DOM for XML manipulation.；Both perform file I/O operations (reading/writing streams).；Both have exception handling for I/O and parsing errors.
- 行为差异: A downloads from a URL; B reads from a Reader.；A modifies wsdlsoap:address attribute; B adds/modifies a label attribute.；A writes to a local file; B writes to a ZipOutputStream.；A returns a String; B returns void.
- 修正建议: Incorporate program flow analysis to identify abstract functional patterns.；Use contrastive learning to align representations of functionally similar but lexically different code.；Leverage domain knowledge or metadata from comments/identifiers to infer broader purpose.

### case_id=2683 FP lexical_or_api_overlap

- 方法: `PhoneSetImpl` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads lines from a URL, skips those starting with '***', and populates a phone set map.
- B 摘要: Reads lines from a URL with optional authentication and writes them to a temporary file while updating a status label.
- 静态失败原因: Static BERT likely overemphasized lexical overlap (e.g., 'BufferedReader', 'readLine()', 'URL') and loop structure, while ignoring the divergent data flow and method semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clones because the overall functionality and output are different: one constructs a data structure, the other downloads to a file. The shared read loop pattern is not enough for Type-3/4 similarity given the distinct purposes.
- 共享行为: Both open a URL and read lines using BufferedReader.
- 行为差异: Function A processes lines locally to build a phone set map; Function B writes lines to a file.；Function A includes line counting; Function B includes file size monitoring and authentication.；Function A skips lines starting with '***'; Function B does not skip any lines.；Function B writes to a temporary file and prints debug information; Function A does not.
- 修正建议: Incorporate dataflow analysis to track how read lines are used.；Add semantic role labeling to distinguish different consumption patterns.；Use graph-based representations that capture output differences.

### case_id=2684 FN partial_functionality

- 方法: `copyFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Retrieves a resource as an InputStream with caching, downloading if needed.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on similar token patterns (e.g., FileInputStream, FileOutputStream) and missed the overall task difference, leading to a false negative prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled them as clones due to overlapping low-level I/O operations and file handling, despite vastly different high-level purposes.
- 共享行为: Both use FileInputStream and FileOutputStream for file I/O.；Both create files as part of their operation.；Both handle exceptions and close streams in finally blocks.
- 行为差异: copyFile performs a direct file copy; getResourceAsStream fetches from URL and caches.；copyFile uses FileChannel.transferFrom; getResourceAsStream uses buffered stream copying.；getResourceAsStream involves network access, cache checking, and caching logic.；copyFile is static and synchronous; getResourceAsStream is synchronized and instance method.
- 修正建议: Incorporate dataflow or control flow analysis to distinguish function-level behavior.；Use task-specific features or longer context to capture the overall purpose.；Improve training data to include diverse pairs with similar low-level API but different high-level tasks.

### case_id=2685 FP long_range_semantics

- 方法: `actionPerformed` vs `tail`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles GUI action commands to set various preferences (e.g., file paths, image scaler, date format, look-and-feel) and optionally restart.
- B 摘要: Implements the Unix tail command: reads a file from the end and optionally follows changes with a 5-second interval.
- 静态失败原因: Static BERT/GraphCodeBERT likely classified as clone due to lexical overlap of common Java constructs (if, try, catch, IOException) and perhaps boilerplate patterns (exception handling, file I/O) in both functions, while missing the high-level semantic purpose. Truncation of the long Function A may have also caused loss of context.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would not label these as clones because they have completely different functionality (GUI settings vs. file tail) and very low lexical overlap (token jaccard 0.088). They are clearly Type-1/2 unrelated.
- 行为差异: Function A is a GUI event handler for setting preferences; Function B is a CLI command for file tailing.；A operates on user interface components and preferences; B operates on HDFS file system and stdout.；A involves file chooser dialogs, save preferences, and restart prompt; B involves reading files, seeking, and optional periodic follow.；A is long and covers many settings; B is focused on a single utility function.
- 修正建议: Use models with longer context windows or hierarchical encoding.；Incorporate program analysis (e.g., dataflow, call graphs) to capture semantics.；Improve training data to reduce false positives from boilerplate-like code.

### case_id=2686 FN lexical_or_api_overlap

- 方法: `read` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads camera log from a URL, parses each line into CameraLogRecord objects, adds to a list, sorts, and logs progress.
- B 摘要: Invokes a remote service via HTTP POST, reads the JSON response, deserializes it into the expected return type, and handles retries on timeout.
- 静态失败原因: Static BERT models may have been misled by lexical/API overlap (BufferedReader, InputStreamReader, logging constructs) into predicting non-clone due to low token Jaccard and differing method names and context.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as implementing a similar pattern of reading and processing lines from a stream, labeling them as Type-4 (semantic similarity) despite different domains and output.
- 共享行为: Use BufferedReader to read lines from an input stream；Logging statements for info；Exception handling with try-catch-finally
- 行为差异: Different domain: camera log parsing vs HTTP RPC invocation；Output: A adds parsed records to a list; B returns a deserialized object or null；Input source: A reads from a URL stream; B reads from an HTTP response entity；Error handling: A continues on parse errors; B retries on timeout
- 修正建议: Incorporate dataflow analysis to trace how inputs and outputs are used；Use domain-specific embeddings or functional role identification；Add larger context windows or graph-based representations to capture program semantics

### case_id=2687 FN partial_functionality

- 方法: `httpRequestByPOST` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string, or null with error codes on failure.
- B 摘要: Registers a User object by encoding password, setting date, adding authority, hashing email, making an HTTP request to a forum for user creation, persisting the user, and sending a confirmation email; returns boolean success.
- 静态失败原因: The model likely relied on low token Jaccard (0.137) and method name differences, failing to recognize the embedded HTTP pattern due to different API usage and surrounding context.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone due to the shared HTTP request-read response pattern, indicating partial functionality similarity often accepted in broad Type-3/Type-4 annotations.
- 共享行为: Both make an HTTP request and read the response line by line using BufferedReader.
- 行为差异: A is a generic HTTP utility; B is a specific registration process with multiple side effects.；A returns response string or null; B returns boolean and throws runtime exceptions.；A uses HttpClient and HttpPost; B uses URLConnection and URL.；B has additional steps like password encoding, DB persistence, email sending.
- 修正建议: Enhance models to detect sub-function similarity by focusing on API call sequences or control flow patterns.；Include more training examples where a common utility pattern is embedded in different overall functionalities.

### case_id=2688 FN partial_functionality

- 方法: `testNetworkHTTP` vs `handledRun`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Makes multiple HTTP GET requests to send sensitive device data and discards responses.
- B 摘要: Downloads a versioned XML file from a URL and updates game data if newer.
- 静态失败原因: Low token Jaccard similarity (0.134) and distinct vocabulary (e.g., different URL strings, method names) caused the model to miss the abstract functional similarity. Static BERT lacks awareness of control flow and data flow patterns that would link the common 'HTTP GET + read loop' structure.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because they share a common pattern of network I/O: opening a URL, reading lines, and handling exceptions. Despite different intents, the structural flow and boilerplate code are similar, fitting broad Type-3 criteria.
- 共享行为: Both perform HTTP GET requests to fetch data；Both use BufferedReader/InputStreamReader to read responses；Both have try-catch-finally blocks for exception handling with stream cleanup
- 行为差异: A sends multiple requests with different URLs and discards all input; B reads a version header and conditionally downloads to file；A uses HttpURLConnection explicitly; B uses URL.openStream()；A catches only IOException; B catches UnknownHostException and generic Exception；B includes additional logic for file creation, writing, and database loading
- 修正建议: Use models that incorporate control flow and data flow, such as GraphCodeBERT or AST-based GNNs；Include feature engineering for network I/O operation patterns；Train with more diverse positive pairs that have low token overlap but similar I/O structure

### case_id=2689 FN partial_functionality

- 方法: `fileDownload` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a given URL and saves it to a specified file path, reading byte by byte.
- B 摘要: Reads content from a hardcoded URL line by line and logs the result.
- 静态失败原因: Static BERT/GraphCodeBERT models likely focus on structural and lexical differences (low token Jaccard, different I/O classes, different control flow), missing the high-level semantic similarity of URL reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as semantic clones (Type-4) because the core functionality of opening a URL connection and reading its content is shared, despite differences in output destination and exact I/O handling.
- 共享行为: Both open a URL connection and get an input stream；Both read data from the stream；Both close the reader
- 行为差异: fileDownload writes to a file; seeURLConnection stores in memory；fileDownload reads bytes; seeURLConnection reads lines；fileDownload has parameters; seeURLConnection hardcodes the URL；fileDownload catches exceptions; seeURLConnection throws
- 修正建议: Incorporate data flow analysis for URL connection objects；Use graph-based representations to capture common sub-patterns；Train on more diverse semantic clone examples

### case_id=2690 FP boilerplate_overlap

- 方法: `load` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads the content of a pastebin paste given an id and returns it as a string.
- B 摘要: Searches Google Images for a query, parses the results, extracts image URLs, and updates the UI with an album art image.
- 静态失败原因: Static BERT models like GraphCodeBERT rely heavily on token-level and structural patterns. The shared boilerplate code (URLConnection, BufferedReader, readLine loop) likely caused the model to overestimate similarity. The model may not capture the long-range dependencies and semantic differences in how the read data is used afterward (one returns raw data, the other parses HTML and updates UI). The low token Jaccard (0.17757) indicates limited lexical overlap, but the syntactic pattern common in many web-scraping functions may have misled the model.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires a high degree of functional similarity or structural similarity. These two functions, while sharing a common pattern of reading from a URL, have fundamentally different purposes (data retrieval vs. image search with GUI update). BCB likely labels this as non-clone (0) because the semantic intent and outputs differ significantly.
- 共享行为: Both open a URL connection and read text line by line using BufferedReader；Both use try-catch for exception handling；Both append lines to a string buffer
- 行为差异: Function A returns a String, function B is void and updates GUI；Function A loads a single paste, function B performs a search and parses multiple results；Function B has additional logic for URL manipulation (replacing spaces) and User-Agent header；Function B processes the HTML to extract image URLs and then sets an icon on a label
- 修正建议: Enhance model to distinguish between utility functions that only read data and those that process data for specific purposes；Incorporate data-flow analysis to track how the read content is used (e.g., returned vs. parsed and used for GUI updates)；Include task-specific context such as method signature (return type) and final output usage；Use contrastive learning to separate similar structural patterns with different semantic outcomes

### case_id=2691 FN benchmark_preference_bias

- 方法: `main` vs `persist`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts all its entries to local files.
- B 摘要: Copies an input stream from a configurable object to a properties file.
- 静态失败原因: Static BERT likely relied on low token overlap and different method names/return types, correctly predicting non-clone according to strict criteria, but the BCB label is based on broader functional similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label it as clone due to the common pattern of reading an input stream and writing to a file, which is a broad Type-4 semantic similarity that tolerates partial functionality overlap.
- 共享行为: Both read from an input source and write to a file output stream.；Both involve basic file I/O operations.
- 行为差异: Source type: A reads from URL+zip stream, B reads from a custom configurable object.；Processing: A unzips multiple entries, B directly copies without unzipping.；Output: A creates multiple files, B writes to a single file.；Error handling: A throws Exception, B catches Exception and wraps in ConfigurationException.
- 修正建议: Use finer-grained functional labels that distinguish between generic I/O operations and specific business logic.；Incorporate dataflow analysis to differentiate sources and transformations (e.g., zip vs direct copy).；Train models on multi-level clone definitions or use task-specific thresholds.

### case_id=2692 FP lexical_or_api_overlap

- 方法: `addDataFromURL` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads content from a URL and appends it to thetext with basic error handling.
- B 摘要: Loads tile data from a URL, parses it into geometry, and adds it to a data structure with synchronization and error handling.
- 静态失败原因: The static model likely overemphasized lexical and API overlaps (e.g., URL, BufferedReader, openStream, readLine) and missed the larger structural and semantic differences due to limited context or lack of dataflow awareness.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically considers clones only when functions share significant functional behavior beyond trivial patterns. Here, the common URL-reading pattern is overshadowed by different overall purposes, so BCB annotates as non-clone.
- 共享行为: Open a URL and read lines using BufferedReader；Use try-catch blocks for exceptions；Close the input stream after reading
- 行为差异: Function A appends lines to thetext; function B concatenates lines into geoJSON and processes geometry；Function A has simple error handling; function B has protocol-specific stream handling and multiple catch blocks；Function B includes synchronization, key management, and complex geometry creation
- 修正建议: Incorporate method-level context (class, method name, surrounding code) to distinguish generic utility functions from domain-specific ones；Use data flow or control flow graphs to capture differences in variable mutations and output；Train on more diverse negative examples with similar API usage but different logic

### case_id=2693 FP partial_functionality

- 方法: `readTwitterFead` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a hardcoded Twitter timeline URL and returns the concatenated JSON response as a String.
- B 摘要: Queries a REST API for open tickets in a given queue, parses ticket IDs, retrieves each ticket, and returns a list of RTTicket objects (or null).
- 静态失败原因: Static BERT may have overvalued structural similarities (HTTP GET, line-by-line reading) while ignoring domain-specific semantics, leading to a false clone prediction.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels these as non-clones because the high-level functionality and output type differ significantly, despite shared HTTP boilerplate.
- 共享行为: Both perform an HTTP GET request.；Both read the response line by line using BufferedReader.；Both handle HTTP status codes and exceptions.；Both use similar try-catch-finally patterns.
- 行为差异: A returns a single String; B returns a List of domain objects.；A uses a hardcoded URL; B constructs the URL with query parameters.；B includes additional parsing logic to extract ticket IDs.；B has different error handling (throws exceptions, custom logging).
- 修正建议: Incorporate semantic role labeling for method purposes.；Use AST-based differencing to capture goal-level differences.；Train on datasets with diverse tasks to reduce boilerplate bias.

### case_id=2694 FP boilerplate_overlap

- 方法: `readVersion` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads version, revision, and date from a 'version' resource file on the classpath and sets instance fields.
- B 摘要: Reads a service provider configuration file and returns a FrameworkFactory instance by instantiating the first non-comment class name.
- 静态失败原因: Static BERT models like GraphCodeBERT often rely on token-level patterns and structural skeletons. Both functions share high token overlap in I/O setup (URL, BufferedReader, while loop, try-finally) and similar control flow, but fail to capture the completely different semantic intent and return type. The model likely picked up on the common 'open resource, read lines, close' pattern as a clone indicator, ignoring deeper differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench typically requires functional similarity beyond boilerplate I/O. Here the core purpose differs: one is a version reader, one is a service loader. Despite structural overlap, BCB would annotate as non-clone (Type-4 or unrelated) because the output and domain-specific logic are different.
- 共享行为: Both open a resource via URL from classpath loader；Both wrap URL stream in BufferedReader and read line by line；Both use a while loop to process lines；Both close resources in a finally block
- 行为差异: Function A parses specific key=value patterns and sets multiple fields; Function B returns an object based on class name found in a single line；Function A uses 'getSystemResource' with path 'version'; Function B uses a custom class loader and a specific services path；Function A catches IOException and prints stack trace; Function B throws Exception upward；Function A returns void; Function B returns a FrameworkFactory
- 修正建议: Incorporate dataflow analysis to trace how parsed data is used (field assignments vs object creation)；Add token-level attention to distinguishing keywords like 'return', specific string patterns, and exception handling style；Use contrastive learning with examples of similar I/O boilerplate but different functionality

### case_id=2695 FN partial_functionality

- 方法: `getHTML` vs `GetResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a URL with specified encoding and optionally writes to file.
- B 摘要: Fetches HTTP response body from a URL and returns as string.
- 静态失败原因: Static BERT models rely on token overlap and structural similarity; the relatively low token Jaccard (0.338) and additional file-writing logic in Function A may have caused the model to miss the shared HTTP fetching purpose.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as clones because they share the core functionality of fetching an HTTP resource and returning its content as a string, tolerating differences in encoding, file writing, and error handling as Type-3/4 variations.
- 共享行为: Opens HTTP connection to retrieve response；Reads response line by line；Returns response as string
- 行为差异: Function A supports encoding parameter and custom User-Agent；Function A optionally writes content to a file；Function B explicitly sets HTTP method to GET and checks response code；Function B uses inefficient string concatenation instead of StringBuilder
- 修正建议: Train models on pairs with varied I/O (e.g., optional file write) to recognize core behavior；Include dataflow or API-call-sequence features；Use contrastive learning that emphasizes shared control flow patterns

### case_id=2696 FN benchmark_preference_bias

- 方法: `test` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Tests StorageStringWriter for write/read and exception handling.
- B 摘要: Launches a NexOpen project configuration, handling Maven pom files and Hibernate settings.
- 静态失败原因: Static model correctly identified very low token Jaccard similarity (0.07) and no shared semantic flow, thus predicting non-clone; BCB label appears to be an annotation error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as performing I/O operations (stream copying) and configuration-like steps, but the domains are too different to be considered clones even under broad Type-3/Type-4 criteria.
- 共享行为: Both use IOUtils.copy for stream copying
- 行为差异: A tests string storage; B manages project configuration；A is a unit test; B is an Eclipse launch configuration；A uses StorageStringWriter; B uses IProject, IFile, etc.；A has no external dependencies; B depends on Eclipse/RCP framework
- 修正建议: Remove this pair from benchmark or correct BCB label to non-clone；Increase token similarity threshold；Use dataflow analysis to detect semantic mismatch

### case_id=2697 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `retrieveQ`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks and their text from a web page and returns them as two vectors.
- B 摘要: Reads the entire content of a web page and returns it as a single string.
- 静态失败原因: Static BERT/GraphCodeBERT models often rely on token-level similarity and may be misled by the common boilerplate code (URL, URLConnection, BufferedReader, reading lines) while missing the semantic divergence in the rest of the function.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label these as non-clones because the core functionality differs (link extraction vs. raw retrieval) and the output structures are distinct, despite shared I/O boilerplate.
- 共享行为: Both open a URL connection and read lines from the input stream.
- 行为差异: Function A parses the page to extract links using regex, while B just appends lines to a StringBuilder.；Function A returns a Vector array of links and texts; B returns a single String of the page content.；Function A includes debugging output and time checks; B does not.；Function A calls toAbsolute to resolve relative URLs; B does not.
- 修正建议: Use dataflow analysis to track how the read content is processed (e.g., split vs. accumulate).；Encode return type and structural output differences more explicitly.；Train with contrastive examples that emphasize functional roles beyond I/O patterns.

### case_id=2698 FN boilerplate_overlap

- 方法: `sendExceptionToServer` vs `addQDInformation`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details (stack trace, config, system info) to a server via HTTP POST and prints server response.
- B 摘要: Reads and parses project information from a local file or HTTP URL, updating internal data structures.
- 静态失败原因: Static models like CodeBERT likely focused on token overlap (low Jaccard) and distinct API sequences, missing the high-level boilerplate pattern that BCB considered as functional similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled these as clones due to structural similarities (URL, streams, BufferedReader, try-catch) and both involving network communication, despite different directions and data formats. This is a broad Type-4 interpretation.
- 共享行为: Both use URL and stream I/O for data communication；Both handle IOException with try-catch；Both read lines using BufferedReader
- 行为差异: Function A sends data (HTTP POST), while Function B reads data (HTTP GET or file read)；Function A constructs URL-encoded parameters, Function B parses custom line formats；Function A has a server response check, Function B updates internal state
- 修正建议: Improve training with clone pairs that share only high-level I/O patterns；Incorporate data flow analysis to distinguish send vs. receive semantics

### case_id=2699 FN boilerplate_overlap

- 方法: `main` vs `scrapeForIsbns`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Constructs and sends an HTTP POST request to the RenRen API with predefined parameters and prints the response.
- B 摘要: Scrapes a URL for ISBN-10 patterns using regex, retries on connection errors, and collects matches into a map.
- 静态失败原因: Static BERT models rely heavily on token overlap and shallow structural similarity; the low Jaccard similarity (0.105) and divergent literals (API keys vs ISBN patterns) caused the model to miss the underlying URL I/O pattern shared by both functions.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often treats as clones code that shares common I/O patterns even if the surrounding logic differs. Here both perform URL reading with similar boilerplate (create URL, open stream, read lines), which falls under a broad Type-3 or partial functionality clone.
- 共享行为: Both open an HTTP connection to a URL and read the response line by line.；Both handle IOException by logging or printing an error.；Both use a while loop with BufferedReader.readLine() to process the response.
- 行为差异: A uses POST method; B uses GET (via url.openStream()).；A constructs many parameters; B uses regex pattern matching.；A prints response to stdout; B stores matches in a map and returns a count.；B implements retry logic with Thread.sleep; A has no retries.
- 修正建议: Train models to recognize common programming idioms (e.g., URL reading loop) beyond surface tokens.；Incorporate data-flow or control-flow features to capture structural patterns.；Use code representations that abstract away concrete literals and method names.

### case_id=2700 FN partial_functionality

- 方法: `fileDownload` vs `wordFrequency`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL and saves it to a local destination directory.
- B 摘要: Retrieves a webpage, searches for a pattern matching a word frequency, and returns the integer frequency if found.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on lexical and structural similarity, which is low (Jaccard=0.2), so they correctly predict non-clone. However, BCB's broader functional interpretation considers them clones, leading to a false negative by the model.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as clones because they perform internet resource operations with similar boilerplate code (URL, BufferedReader loop), despite different final purposes.
- 共享行为: Both open a URL and read data using BufferedReader；Both handle I/O exceptions
- 行为差异: Purpose: file download vs. word frequency counting；Output: void vs. int return；Loop: reads bytes and writes to file vs. reads lines and matches regex；Error handling: logs error vs. prints stack trace and returns 0
- 修正建议: Incorporate high-level API usage patterns beyond token overlap；Use program analysis to detect common I/O patterns；Adjust clone definition thresholds to align with BCB's broader similarity interpretation

### case_id=2701 FN benchmark_preference_bias

- 方法: `getFile` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies the endpoint, and returns the local file path.
- B 摘要: Reads a DICOM image file, parses pixel data, and writes the processed data to another file.
- 静态失败原因: Static BERT predicted non-clone correctly due to very low lexical overlap (token Jaccard = 0.07) and different API calls; the model did not fail—the BCB label is likely erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone based on a very broad interpretation of 'file reading/writing with transformation', which is not typically considered a semantic clone in BCB's own guidelines.
- 共享行为: Both perform file I/O operations involving reading from a source, processing data, and writing to a destination.
- 行为差异: Function A downloads from a URL and handles XML modification; Function B reads a local DICOM file and handles pixel data.；Function A returns a file path; Function B returns void.；Function A uses AxisFault for error handling; Function B throws IOException.；Entirely different domain-specific APIs and data formats (WSDL vs DICOM).
- 修正建议: Re-validate the BCB label for this pair; it is likely a false positive in the benchmark.；If BCB label is incorrect, remove or correct it to improve model evaluation.

### case_id=2702 FN benchmark_preference_bias

- 方法: `convert` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Converts an ACRNEMA image file to DICOM format, handling pixel data and UIDs.
- B 摘要: Launches a NexOpen project configuration, processing pom files and setting up Hibernate reverse engineering.
- 静态失败原因: Static BERT correctly predicted non-clone, so it did not fail; the BCB label appears to be an annotation error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to superficial similarities like complex control flow and stream handling, but their functionality is completely unrelated.
- 共享行为: Both use try-finally blocks for resource management；Both perform file I/O operations
- 行为差异: Function A processes medical image data and transforms pixel formats；Function B sets up project build configurations and handles Maven POM files；Function A uses DICOM tags and UIDs; Function B uses Eclipse workspace resources and launch configurations
- 修正建议: Review and correct BCB annotations for pairs with low semantic similarity；Use semantic-aware features to reduce false positives from boilerplate overlap

### case_id=2703 FN partial_functionality

- 方法: `getFile` vs `setContenu`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads WSDL file from a URL, modifies the SOAP address, and saves to a temporary directory, returning the file path.
- B 摘要: Sets the content and metadata of a file electronic object after validating and copying an input stream.
- 静态失败原因: Very low token Jaccard (0.083) and differing code structures (English vs French, different APIs) caused the model to miss the shared stream-copying pattern, relying on surface form similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the stream copying and file handling as a core functional similarity, accepting broad Type-4 clones that manage file content despite different specifics.
- 共享行为: Both copy an input stream to an output stream (file I/O)；Both handle exceptions and close streams；Both perform file-related operations
- 行为差异: A downloads from a network and modifies XML; B does not；A returns a file path; B returns void；A uses NIO channels; B uses IOUtils.copy；A has multiple specific exception catch blocks; B uses nested try-finally
- 修正建议: Use dataflow analysis to identify common stream copying operations；Incorporate structural clone detection focusing on I/O patterns；Enhance embeddings with semantics of common library usage

### case_id=2704 FP lexical_or_api_overlap

- 方法: `readData` vs `getZipAsFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated string constants and a file to populate sets and maps for Tibetan transliteration.
- B 摘要: Downloads a file from a DigitalObject to a temporary directory.
- 静态失败原因: Similar exception handling patterns (try-catch with IOException) and common API classes (File, FileOutputStream) may have misled the model, despite low token Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels it non-clone because the functions are completely different in purpose and logic, despite some superficial lexical overlap.
- 共享行为: Both involve I/O operations and handle exceptions.
- 行为差异: A is large with complex tokenization and file parsing; B is small and simple.；A modifies many global data structures; B creates a temporary file and returns its reference.；A uses StringTokenizer; B uses IOUtils and FileOutputStream.
- 修正建议: Incorporate control-flow and data-dependency graphs to distinguish complex processing from simple file writes.；Use code summarization or AST-based features to capture functional intent.

### case_id=2705 FP boilerplate_overlap

- 方法: `main` vs `saveFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses command line arguments, reads a Prolog file, parses it, and generates adapter classes and JAR file output.
- B 摘要: Saves UI configuration settings (window positions, look and feel, toolbars) to an XML file using JDOM.
- 静态失败原因: Static BERT likely over-relied on shared API tokens (File, FileOutputStream, try-catch) and structural patterns, missing the vast difference in high-level semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotation typically requires significant semantic overlap; these functions serve entirely different purposes despite sharing basic I/O boilerplate, so BCB would label as non-clone.
- 共享行为: Both perform file I/O operations and handle exceptions
- 行为差异: One is a main method for code generation; the other saves UI state；Different input/output types (Prolog file vs UI window)；Uses different libraries (Prolog parser vs JDOM XML)；Different control flow and logic complexity
- 修正建议: Incorporate dataflow or program dependency graph features；Use method name and class context more heavily；Filter out common boilerplate patterns

### case_id=2706 FP boilerplate_overlap

- 方法: `init` vs `sendPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads controller classes from a registry file using classloader.
- B 摘要: Sends an HTTP POST request and returns the response string.
- 静态失败原因: Static BERT likely overemphasized surface-level API calls like BufferedReader, InputStreamReader, and URL, ignoring the semantic divergence in their overall functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these non-clones because they serve completely different purposes (class loading vs HTTP request) despite overlapping I/O APIs.
- 共享行为: Both use BufferedReader and InputStreamReader to read input streams；Both have try-catch exception handling；Both use URL class
- 行为差异: Function A loads classes dynamically from file content; Function B performs network I/O；Function A initializes a servlet context; Function B is a utility for HTTP communication；Function A uses logging; Function B uses a custom message display
- 修正建议: Enhance model to distinguish between data processing and network communication patterns；Incorporate higher-level semantic features like method purpose or external library usage

### case_id=2707 FN partial_functionality

- 方法: `main` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends a hardcoded HTTP POST request to a specific API endpoint with predefined parameters and prints the response.
- B 摘要: Fetches OPDS catalog entries using HTTP GET with dynamic parameters, handles redirects, timeouts, content parsing, and pagination.
- 静态失败原因: The token overlap is extremely low (0.08), and the model likely focused on the surface differences (different method names, hardcoded vs dynamic, POST vs GET). Without capturing the abstract HTTP communication pattern, the model correctly predicted non-clone for strict semantics but failed to align with BCB's broader clone definition.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might treat these as Type-4 clones due to the shared pattern of using HttpURLConnection for network communication, despite different specifics. The low-level operations (open, set properties, connect, read) are common and could be considered 'functionally similar' under broad annotation guidelines.
- 共享行为: Both use HttpURLConnection to make HTTP requests.；Both set connection properties (e.g., setDoInput, setRequestProperty).；Both obtain and log the HTTP response code.；Both read input from the connection stream.
- 行为差异: A uses POST method; B uses GET method.；A has hardcoded parameters; B uses dynamic state variables.；B handles redirects, timeouts, content-disposition, and content encoding; A does not.；B implements pagination with a loop; A makes a single request.
- 修正建议: Improve model sensitivity to high-level network I/O patterns by including more diverse examples of HTTP client usage.；Use graph-based representations that capture API call sequences (e.g., open->setProperty->connect->getResponseCode).；Incorporate semantic understanding of common library usage (java.net.HttpURLConnection) to detect similar functionality even with different parameters.

### case_id=2708 FP partial_functionality

- 方法: `readData` vs `getProjectTreeData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Initializes multiple character sets and a mapping from Wylie to Tibetan character codes by parsing static string fields and a configuration file.
- B 摘要: Fetches an XML file over HTTP, parses it to extract project tree data (pid, ppid, p), and returns a 2D array.
- 静态失败原因: Static BERT/GraphCodeBERT may have overgeneralized due to both functions containing common Java patterns (try-catch, loops, file I/O) and ignored the distinct semantic contexts and APIs used.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would likely label as non-clone because the functions have entirely different purposes and implementations, even though both involve parsing and data population.
- 共享行为: Both parse input data and populate data structures
- 行为差异: Different input sources: static fields vs HTTP/XML file；Different output: void vs String[][]；Different parsing logic: StringTokenizer vs DOM XML parsing；Different domain: Tibetan character initialization vs project tree retrieval
- 修正建议: Incorporate type-aware analysis to distinguish domain-specific APIs like StringTokenizer vs DocumentBuilder；Use data-flow analysis to capture different output types and side effects；Train on more diverse examples to avoid shallow pattern matching

### case_id=2709 FP boilerplate_overlap

- 方法: `getURLContent` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches the entire content of a URL as a string.
- B 摘要: Parses a YouTube URL to extract parameters and construct a fullscreen video URL.
- 静态失败原因: Static BERT/GraphCodeBERT models may have over-relied on the overlapping API sequence (URL, URLConnection, BufferedReader, readLine) and missed the distinct logic after reading lines. The shared boilerplate dominates the representation, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions have very different purposes and outputs, even though they share boilerplate URL reading code. The core functionality is not similar enough for Type-3/4 clone acceptance.
- 共享行为: Both open a URL connection and read lines using BufferedReader.；Both close the BufferedReader in a finally or after use.
- 行为差异: A returns the full concatenated content of the URL; B returns a newly constructed URL based on parsing a specific line.；B has side effects like setting progress indicators, printing debug info, updating an instance variable (ytTitle), and has different error handling.；B reads only until it finds a line containing 'fullscreenUrl', then stops reading further; A reads all lines.；B processes the querystring format to extract parameters; A does no parsing.
- 修正建议: Train the model to distinguish boilerplate from core functionality using contrastive learning.；Include more negative examples with similar boilerplate but divergent semantics.；Incorporate data-flow or control-flow information to capture differences in variable usage and output construction.

### case_id=2710 FP lexical_or_api_overlap

- 方法: `readPage` vs `readZoneIDs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL page, optionally skipping comment lines, and returns the content as a string.
- B 摘要: Reads integer zone IDs from a resource file and returns them as a HashSet.
- 静态失败原因: Static BERT/CodeBERT models often rely on token-level similarity and may be misled by the high lexical overlap of common I/O patterns (BufferedReader, InputStreamReader, readLine, while loop, etc.), overlooking the semantic differences in return type and data processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have different input/output types and distinct business logic (reading HTML vs. parsing integers). The shared boilerplate of reading lines is insufficient for a clone pair in BCB.
- 共享行为: Both open a URL stream；Both read lines until null；Both close the reader or implicitly
- 行为差异: A returns concatenated HTML string; B returns HashSet of Integers；A handles comment lines; B does not；A throws exception; B catches exception；A uses BufferedReader; B uses LineNumberReader
- 修正建议: Improve model ability to encode return types and external behavior；Use dataflow or context beyond token sequences；Incorporate type information and method signatures

### case_id=2711 FP lexical_or_api_overlap

- 方法: `getWebPage` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a web page from a URL and returns its content as a single string.
- B 摘要: Loads and instantiates an OSGi FrameworkFactory from a classpath resource file.
- 静态失败原因: Static BERT/GraphCodeBERT overemphasized lexical and structural similarities (e.g., BufferedReader, InputStreamReader, readLine) and missed semantic intent differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because methods have completely different functionality and output types despite similar I/O patterns.
- 共享行为: Both open a URL input stream；Both use BufferedReader to read lines
- 行为差异: Function A returns concatenated web page content; Function B returns an instantiated object via reflection；Function B reads a specific resource path and filters comments; Function A reads entire page
- 修正建议: Incorporate method name embeddings；Use dataflow analysis to track output usage；Add training examples with similar I/O but different semantics

### case_id=2712 FN benchmark_preference_bias

- 方法: `postData` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends HTTP POST request with data to a specified URL and reads the response.
- B 摘要: Opens an HTTP connection to a fixed URL and reads the response, logging it.
- 静态失败原因: The functions have low token Jaccard (0.27) and different method names and parameters; static models may focus on lexical overlap and miss the conceptual similarity of using URLConnection for HTTP communication.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as performing URL connection reading, and the core of reading from a URLConnection is similar, even though one does POST and the other does GET. Broad type-3/4 clone.
- 共享行为: Both open a URLConnection and read the response using BufferedReader.
- 行为差异: A sends a POST request with form data and sets request properties; B performs a GET request to a hardcoded URL and logs the response.
- 修正建议: Improve model to recognize structural patterns of URLConnection usage.；Include API usage context like openConnection, getInputStream.

### case_id=2713 FP lexical_or_api_overlap

- 方法: `copyFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file from source to target using NIO FileChannel.
- B 摘要: Handles GUI action events to set preferences for various tools like GRAPHVIZ and IMAGEMAGICK.
- 静态失败原因: The model likely over-relied on superficial lexical matches like 'File', 'IOException', and control flow patterns (e.g., null checks), despite very low Jaccard similarity (0.02). It may have misjudged the truncated portion of B as similar to A's pattern.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this non-clone because the functions are semantically unrelated: one is a utility for file copying, the other is a GUI action listener managing application settings.
- 共享行为: Both involve file-related operations (reading/writing files in A, selecting files in B).；Both handle exceptions (IOException in A, caught exceptions in B).
- 行为差异: A performs a specific file copy; B is a complex event handler with multiple conditional branches.；A is concise and focused; B is lengthy with user interaction, preference updates, and UI modifications.；A uses FileChannel; B uses JFileChooser and Swing components.
- 修正建议: Incorporate dataflow analysis to capture actual variable dependencies.；Use function-level embedding with attention to long-range semantic context.；Improve handling of low similarity pairs by requiring higher threshold or semantic constraints.

### case_id=2714 FP partial_functionality

- 方法: `readRemoteFile` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads entire content of a remote file from a fixed URL, concatenating all lines into a single string.
- B 摘要: Reads the first line of an HTTP response from a given URL and returns that single line.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-weighted structural similarities (both use URL, BufferedReader, readLine) and missed the semantic difference in control flow (loop vs no loop) and data flow (concatenation vs single line).
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically requires near-full functional equivalence for Type-3/4 clones; here the functions differ in core behavior (read all vs read first line), so they are not considered clones.
- 共享行为: Both open a URL connection and use a BufferedReader to read from an InputStream；Both return a String obtained from the HTTP/file response
- 行为差异: Function A reads all lines until EOF, concatenating them; Function B reads only the first line；Function A uses generic URL.openStream(); Function B uses HttpURLConnection and explicitly connects and disconnects；Function A handles EOF and IO exceptions; Function B throws Exception without handling
- 修正建议: Incorporate control-flow analysis to detect loops and distinguish iteration patterns；Use data-flow analysis to track how many lines are read and aggregated；Employ more abstract semantic representations that capture whether all lines or only the first line is returned

### case_id=2715 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts all hyperlinks and their display texts from a given URL's HTML using regex, returning them as two vectors.
- B 摘要: Constructs a Google image search URL for the current track's artist and album, fetches HTML, and parses to extract image URLs, storing them in an instance collection.
- 静态失败原因: The model likely overfocused on overlapping API calls (URL, URLConnection, BufferedReader, InputStreamReader) and similar boilerplate code, missing the core semantic differences in input, output, and parsing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: Despite both involving URL fetching and HTML parsing, the functions serve distinct purposes and have different implementations; BCB would label non-clone due to semantic mismatch in final goal and data handling.
- 共享行为: Both fetch web content via HTTP；Both read HTML response line by line；Both use string manipulation to extract links
- 行为差异: Input: A takes a URL string; B uses instance fields (artist, album)；Output: A returns a vector array; B modifies internal state (side effect)；Parsing: A uses regex for all <a> tags; B splits on Google-specific pattern for image URLs；Scope: A is generic link extractor; B is specific to Google image search
- 修正建议: Incorporate task-specific semantic labels to distinguish generic vs. specialized web scraping；Use data-flow analysis to capture differences in input-output transformations；Add negative examples with similar API usage but different functionality to training data

### case_id=2716 FP lexical_or_api_overlap

- 方法: `retrieveQ` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs a GET request to a URL and returns the response body as a string, printing the response message to stderr.
- B 摘要: Performs a POST request to a URL with URL-encoded parameters and returns the response body as a string, handling exceptions and disconnecting the connection.
- 静态失败原因: The static BERT/GraphCodeBERT model likely focused on the lexical and API overlap (URL, URLConnection, InputStream, BufferedReader, etc.) and the similar control flow (reading lines into a string). It may have missed the difference in HTTP method and the presence of parameter sending and error handling. The high Jaccard similarity (0.2588) might be due to common boilerplate code for HTTP response reading, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels such pairs as not clones because they have different HTTP methods and different functionality (GET vs POST). Even though they share a common pattern of reading an HTTP response, the core behavior is distinct and not considered a Type-3 or Type-4 clone. BCB annotations often rely on functional equivalence, and here the functions are not interchangeable.
- 共享行为: Both create a URL and open an HTTP connection；Both read the response stream using BufferedReader and accumulate lines into a StringBuilder/StringBuffer；Both return the accumulated string as the response；Both use InputStreamReader and readLine()
- 行为差异: Function A uses GET method, function B uses POST method；Function B sends parameters via DataOutputStream and sets additional request headers (Content-Type, Content-Length, etc.)；Function B has exception handling returning null on error, function A throws exceptions；Function B explicitly disconnects the connection in finally block, function A does not
- 修正建议: Incorporate control flow and data flow differences, such as the HTTP method used and the presence of output stream writes；Add more robust semantic understanding by comparing method signatures and parameter usage；Consider method name and context to distinguish GET vs POST operations

### case_id=2717 FP lexical_or_api_overlap

- 方法: `handler` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses HTML content from a URL and extracts substrings to update a map.
- B 摘要: Fetches a version string from a fixed URL and returns it.
- 静态失败原因: Static models may over-rely on lexical and API-level overlap (URL, BufferedReader, readLine) and miss the distinct data flow and output behavior (map vs return, specific parsing vs simple read).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the core functionality differs significantly (generic scraper vs specific version fetcher) despite sharing boilerplate URL reading code.
- 共享行为: Both open a URL connection；Both read lines using BufferedReader；Both handle IOExceptions
- 行为差异: A modifies a map parameter, B returns a string；A uses a TargetPage object for URL and parsing parameters, B uses a fixed URL；A performs substring extraction based on include/from/to strings, B simply reads the last line；A has nested loops and conditional logic, B has a single read loop
- 修正建议: Incorporate data flow analysis to distinguish map modifications from return values；Train on examples with diverse semantics despite similar boilerplate；Use contrastive learning to separate functions with different purposes

### case_id=2718 FN boilerplate_overlap

- 方法: `testNetworkHTTP` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.4`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A test method that makes multiple HTTP connections to various URLs, reads and discards response lines.
- B 摘要: Reads a skeleton file from the classpath, parses it into sections separated by '---' lines, and validates section count.
- 静态失败原因: Static models like BERT/GraphCodeBERT rely heavily on token overlap and local context. The token Jaccard similarity is low (0.157). The high-level pattern of URL opening and line reading is overshadowed by different method names, different surrounding logic, and different parameter/exception handling.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider this a clone because both functions share the common pattern of opening a URL, wrapping in BufferedReader, and reading lines until null. Despite different purposes, the I/O boilerplate is similar enough to be considered Type-3 or Type-4 clone in a broad sense.
- 共享行为: Both open a URL/stream；Both use BufferedReader to read lines in a loop；Both handle I/O within try-catch or throws Exception
- 行为差异: Method A makes multiple external HTTP requests, method B reads a local classpath resource；Method A discards all read data, method B accumulates lines into sections；Method B includes validation and exception for incorrect section count；Method A is a test method with no return value, method B returns void but modifies internal state
- 修正建议: Enhance models to recognize common I/O patterns even when lexical overlap is low；Use dataflow or control-flow analysis to capture shared structures like open-read-close；Add training examples that pair different implementations of similar I/O idioms

### case_id=2719 FN benchmark_preference_bias

- 方法: `doExecute` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Processes an HTTP multipart request to send an email with attachments.
- B 摘要: Retrieves a resource as an InputStream, with local caching and conditional fetching.
- 静态失败原因: Static BERT/GraphCodeBERT models use token-level similarity; the very low Jaccard similarity (0.0857) correctly predicted non-clone. BCB's label likely reflects a broad behavioral interpretation that static models cannot capture.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions involving I/O, caching, and error handling patterns, but their core semantics are entirely different.
- 共享行为: Both involve file I/O operations；Both use try-catch for exception handling
- 行为差异: A is an email-sending action in Struts; B is a resource caching helper；A parses multipart form data; B fetches remote resources via HTTP；A deals with ActionForward and error messages; B returns InputStream or null；No overlap in core functionality such as email vs. caching
- 修正建议: Re-evaluate BCB annotation criteria to ensure consistency；Improve models to detect long-range structural patterns, but this pair is genuinely non-clone

### case_id=2720 FN partial_functionality

- 方法: `seeURLConnection` vs `parse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads a hardcoded URL and logs its content line by line.
- B 摘要: Parses data from a file or URL into a DataSet with configurable headers, types, delimiters, and error handling.
- 静态失败原因: Static BERT models may have predicted non-clone (0) because the token Jaccard is very low and the overall code structure and functionality are clearly different. However, if BCB considered them clones due to URL reading, the model failed to recognize that shared high-level behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone due to the shared pattern of reading from a URL using BufferedReader, considering it a Type-4 clone based on common functionality of URL data retrieval, ignoring the significant differences in processing and return type.
- 共享行为: Both open a URL connection and read data via BufferedReader.
- 行为差异: Function A simply concatenates lines and logs, while Function B structures data into columns with type conversion.；Function A has no error handling or parsing logic; Function B has extensive error handling, tokenization, and type inference.；Function A returns void; Function B returns a DataSet.；Function A hardcodes the URL; Function B supports both file and URL input with configuration.
- 修正建议: Improve model's ability to identify high-level semantic similarity beyond token overlap, possibly using data flow or method call analysis.；Incorporate broader context of method purposes, e.g., via API usage patterns.

### case_id=2721 FN partial_functionality

- 方法: `copyResource` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using a manual byte-by-byte loop.
- B 摘要: Handles an HTTP GET request by reading a file from the request path and copying it to the response output stream using IOUtils.copyLarge.
- 静态失败原因: The model relied on low lexical overlap and different method signatures (private vs protected, different names) and missed the underlying structural similarity of the copy operation, possibly distracted by HTTP-specific code in B.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers them clones because both perform the core functionality of copying data from input to output, which is a common pattern, and the differences in source/destination and error handling are considered superficial variations.
- 共享行为: Reads bytes from an input source；Writes bytes to an output destination；Uses file I/O and stream copying
- 行为差异: Source: A from URL or file; B from file based on request path；Destination: A to file; B to HTTP response output stream；Error handling: A throws Exception; B throws IOException；Copying method: A manual loop; B uses IOUtils.copyLarge
- 修正建议: Train on more diverse clone pairs with low lexical overlap but similar semantics；Incorporate data flow analysis to capture core I/O operations；Use graph-based models that abstract away method signatures

### case_id=2722 FN partial_functionality

- 方法: `copyResource` vs `copyFileChannel`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using InputStream/OutputStream.
- B 摘要: Copies a file to another file using FileChannel, optionally preserving modification time.
- 静态失败原因: Static BERT was likely misled by low token overlap (0.19) and different API calls (InputStream vs FileChannel), focusing on surface-level syntax rather than the common copying behavior, and lacked understanding of Java I/O semantics.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels file copying operations as clones despite different APIs because the core functionality (copying file contents) is semantically equivalent and the structural differences are considered superficial in the broader Type-3/4 clone definition.
- 共享行为: Both copy data from a source to a destination file.；Both release resources after copying.
- 行为差异: code_a accepts both URL and file sources; code_b only accepts file sources.；code_a uses byte-by-byte read/write; code_b uses channel transferTo for potentially faster copying.；code_b optionally preserves file modification time; code_a does not.；code_a throws generic Exception; code_b throws IOException and uses finally block for resource management.
- 修正建议: Use fine-grained semantic similarity that captures file I/O operations at a higher level.；Train on diverse file copy patterns with varying APIs.

### case_id=2723 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads Twitter user timeline JSON and returns the raw content as a string.
- B 摘要: Checks for a new version of jEdit by reading a text file from a URL and displays a message.
- 静态失败原因: The model likely focused on the common structural pattern (URL opening, BufferedReader loop, exception handling) and ignored the differing method names, URL strings, and overall context. This led to a false positive due to lexical and API overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they serve entirely different purposes (Twitter feed reader vs version checker). Although there is structural similarity in reading from a URL, the functionality and output are distinct, and BCB typically requires similar semantic behavior for clones.
- 共享行为: Open a URL to fetch remote data；Read content line by line using BufferedReader；Handle IOException
- 行为差异: Different URL and expected content format (JSON vs .version/.build lines)；Different error handling: logging vs GUI messages；Different return type: String vs void with UI updates；Different HTTP libraries: HttpClient vs URL.openStream()
- 修正建议: Incorporate method names and surrounding class context into the model；Use data flow analysis to distinguish variable assignments and output；Attend to constant strings like URLs and specific property names

### case_id=2724 FP lexical_or_api_overlap

- 方法: `executePost` vs `sendRequestObjectResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs an HTTP POST request with form-urlencoded parameters and returns the response body as a string.
- B 摘要: Sends an XML request to a servlet via HTTP with GZIP compression, saves the response to a file based on content type, and shows the file in a browser, returning the file path.
- 静态失败原因: The static BERT/GraphCodeBERT model likely over-relied on lexical and API-level overlaps (e.g., URL, URLConnection, setDoOutput, getOutputStream, getInputStream), which are common patterns in HTTP client code, and missed the significant differences in control flow, data processing, and error handling. The model lacks understanding of the broader context and semantics of the methods.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because the high-level purpose is fundamentally different: one is a generic HTTP POST utility, the other is a domain-specific method for a library system with additional GUI, compression, and file handling. The partial overlap in HTTP request boilerplate is insufficient for Type-3/4 similarity.
- 共享行为: Both perform HTTP POST-like operations using URLConnection with setDoOutput(true).；Both open a connection, write data to the output stream, read from the input stream, and handle exceptions.
- 行为差异: Method A uses explicit POST method and sends url-encoded parameters; Method B sends XML with GZIP compression via OutputStreamWriter.；Method A returns the response string directly; Method B saves the response to a file and returns the file path.；Method B includes GUI dialogs for IP/Port configuration, logging to file, and browser display; Method A does not.；Error handling differs: A returns null on exception; B shows a JOptionPane and returns empty string.
- 修正建议: Incorporate structural features like control flow graphs and data flow analysis to capture differences in branching and output handling.；Use a more context-aware model that considers method signatures, parameter types, and return types.；Include token-level features with attention to unique identifiers (e.g., servletName, GZIP, file paths) beyond common API calls.

### case_id=2725 FN benchmark_preference_bias

- 方法: `getFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Gets a file from user directory or copies from classpath resource if not present; throws exception if resource not found.
- B 摘要: Launches a NexOpen project configuration, verifying project structure, processing XML pom files, setting Hibernate properties, creating reverse engineering files, and scheduling installation actions.
- 静态失败原因: The static model likely focused on the structural differences and low token overlap (0.0995) and correctly identified them as non-clones; however, it may have missed the subtle file I/O similarity that BCB considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled these as clones due to the presence of similar file copying patterns (IOUtils.copy) and resource loading, but the overall functionality is very different; BCB annotations sometimes miss contextual differences.
- 共享行为: Both involve file existence checks；Both use IOUtils.copy to copy from InputStream to OutputStream
- 行为差异: Completely different overall purpose: returns a file vs. launches a project；Function B has complex control flow with callbacks and multiple file operations；Function A is simple and focused on a single file retrieval
- 修正建议: Incorporate more context-aware features to capture overall function purpose；Use hierarchical representations to distinguish main functionality from auxiliary code snippets

### case_id=2726 FN benchmark_preference_bias

- 方法: `unzip` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Unzips a zip file, creating directories and extracting entries to a target directory using ZipInputStream.
- B 摘要: Builds a website for editing by processing pages with XSL transformations and writing output files with various string replacements.
- 静态失败原因: The static model correctly captured low token similarity and structural differences, predicting non-clone; if BCB considers it a clone, the model failed to recognize the broad I/O pattern, but in this case the model was likely correct.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled these as clones due to both being file I/O-intensive with buffered streams and iteration, but this is overly broad and not typical for BCB's annotations; possibly a benchmark annotation error.
- 共享行为: Both involve reading input from files and writing output to files using buffered streams.；Both have a loop iterating over a collection (zip entries or pages) to perform file operations.
- 行为差异: A extracts zip archives; B processes HTML/XML pages with XSLT and string replacements.；A is a small utility; B is a large method with many parameters and dependencies.；A uses ZipInputStream; B uses FileInputStream and StreamSource.；A's loop is while over zip entries; B's loop is for over pages with complex internal logic.
- 修正建议: Review BCB annotation for this pair; likely a false positive.；If BCB is correct, the model could be improved by incorporating higher-level I/O patterns, but this is not recommended due to risk of over-generalization.

### case_id=2727 FP lexical_or_api_overlap

- 方法: `scrapeForIsbns` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Scrapes ISBN numbers from a URL using regex, with retry logic on connection failures.
- B 摘要: Constructor for a Swing browser GUI that reads and transforms XML content from a URL and sets up the interface.
- 静态失败原因: Overemphasized lexical and API overlap (e.g., URL.openStream, BufferedReader, try-catch) common to many network-IO Java snippets, ignoring the distinct high-level purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled as non-clone because the functions perform entirely different tasks (ISBN scraping vs. GUI initialization) and share only trivial IO boilerplate.
- 共享行为: Both read from a URL using BufferedReader and handle IOException
- 行为差异: A only scrapes ISBN strings via regex; B sets up a full GUI and processes XML/XSLT；A uses retry logic with sleep on ConnectException; B does not；A uses a shared queue outputIsbns; B creates UI components and uses transformers
- 修正建议: Incorporate abstract syntax tree (AST) or control-flow analysis to distinguish core logic from boilerplate；Use data-flow tracking to detect different output/effects

### case_id=2728 FP lexical_or_api_overlap

- 方法: `main` vs `byReference`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses a Prolog file, generates adapter classes, and writes them to a JAR file.
- B 摘要: Copies an InputStream to a temporary file and returns an ImmutableContent object.
- 静态失败原因: Static BERT models likely overemphasized common tokens like 'File', 'IOException', and 'e.printStackTrace()', ignoring the distinct control flow and domain-specific logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these non-clones because their overall functionality and purpose are completely different, despite minor API overlap.
- 共享行为: Both use File and IOException；Both print stack traces on exceptions
- 行为差异: Function A is a complex adapter generator; Function B is a simple input stream to file copy；Function A creates multiple files and classes; Function B creates a single temp file；Function A uses many domain-specific classes (Parser, FactVisitor, etc.); Function B uses generic I/O utilities
- 修正建议: Incorporate data flow and control flow analysis；Use graph-based models (e.g., Code Property Graphs) to capture structural differences；Train on more diverse non-clone pairs with overlapping tokens but different semantics

### case_id=2729 FP boilerplate_overlap

- 方法: `get` vs `wordFrequency`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Makes an HTTP GET request to retrieve GameRecord objects based on location and count, parsing lines from the response.
- B 摘要: Retrieves word frequency from a web service by replacing a placeholder in a URL and parsing the response for a pattern.
- 静态失败原因: Static BERT models capture token-level patterns and may overemphasize the shared boilerplate code (HTTP connection, stream reading, exception handling) while ignoring the core differences in parsing logic and return type. The model may have learned that such patterns often appear in clones due to similar tasks.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this non-clone because the functions have different signatures, return types, and business logic, despite sharing some structural boilerplate. Token similarity is low (0.24), and functional purpose is distinct.
- 共享行为: Both make HTTP requests to fetch data from a URL；Both read response line by line using BufferedReader；Both handle IOException with printed stack trace or message；Both return a default value (null or 0) on error
- 行为差异: Different return types: GameRecord[] vs int；Different HTTP request setup (explicit GET vs implicit via openStream)；Different response parsing logic (skip '#' and decode vs regex match)；Different error handling (print message and return null vs print stack trace and return 0)
- 修正建议: Incorporate control flow and data flow features to distinguish different processing logic；Use AST or PDG to capture semantics beyond token sequences；Consider types and return values as distinguishing factors

### case_id=2730 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `get`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a web page and extracts all hyperlinks and their text using regex, returning two vectors.
- B 摘要: Sends an HTTP GET request with custom headers to retrieve game records, parsing lines not starting with '#' and returning an array of GameRecord.
- 静态失败原因: Static BERT models may over-rely on lexical and API-level overlap, such as 'URL', 'openConnection', 'BufferedReader', 'readLine', and the common while-loop pattern for reading lines, ignoring the different data transformations and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels pairs with distinct functional purposes as non-clones, even if they share boilerplate code. Here, A is a web scraper for links, B is a game record fetcher; they are functionally unrelated.
- 共享行为: Both open a URL connection and read lines from an input stream.
- 行为差异: A extracts hyperlinks and their text; B parses game records from lines.；A uses regex for extraction; B uses simple line prefix checking.；A returns two Vectors; B returns an array of GameRecord.；A includes debug prints; B sets custom HTTP headers.
- 修正建议: Incorporate data flow analysis to track how the input is transformed and what output is produced.；Add contrastive training with negative examples that share boilerplate but differ in functionality.；Use program slicing to isolate the core logic and compare semantics rather than token sequences.

### case_id=2731 FN benchmark_preference_bias

- 方法: `testSimpleQuery` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Tests JCR query by creating nodes, writing XML, executing query, and verifying a single result.
- B 摘要: Caches remote resources locally and returns an InputStream, handling HTTP connections and file caching.
- 静态失败原因: Static BERT correctly predicted non-clone (0); the error is in BCB label. The model likely captured the lack of semantic similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to superficial overlap in using streams and file operations, despite completely different purposes.
- 共享行为: Both use InputStream and OutputStream；Both perform file I/O operations
- 行为差异: A is a test method for JCR query; B is a resource caching utility；A writes XML content to nodes; B downloads and caches remote files；A queries and asserts results; B returns input streams from cache；A uses JCR API; B uses URL, HTTP, and file system
- 修正建议: Re-annotate this pair as non-clone；Improve benchmark annotation guidelines to avoid labeling based on low-level I/O similarities

### case_id=2732 FN partial_functionality

- 方法: `addIDs` vs `getNetworkServersIPs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: addIDs fetches metabolite IDs from a web page by parsing HTML for specific patterns and sets various properties on a PeakListRow object, returning a score.
- B 摘要: getNetworkServersIPs fetches server IP addresses from a network address by parsing lines starting with '!SERVERS' and extracting IP components, returning a vector of strings.
- 静态失败原因: Low token overlap (Jaccard=0.147) and different method signatures cause the model to miss the high-level structural similarity of URL fetching and line parsing.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as instances of 'fetch data from URL and parse lines' tasks, ignoring domain-specific output and logic differences, leading to a Type-4 clone annotation.
- 共享行为: Both open an HTTP connection to a URL；Both read lines from the input stream；Both parse lines for specific patterns to extract data
- 行为差异: A modifies a row object with multiple fields and returns an integer; B returns a vector of IP strings；A parses for 'Metabolites/' or 'Analytes/' patterns; B parses for '!SERVERS' flag and splits by ':'；A has multiple conditional branches for different ID types; B uses a boolean flag to control parsing state
- 修正建议: Enhance model with data-flow or abstract syntax tree features to capture common patterns；Include more training examples of URL-parsing functions with varying specifics；Use contrastive learning on pairs with similar control flow but different domains

### case_id=2733 FN partial_functionality

- 方法: `getResourceAsStream` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a resource from a URL with caching, returns an InputStream.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: Static BERT models like GraphCodeBERT focus on token-level similarity and miss high-level functional similarity; low token Jaccard and different control flow obscure the shared I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones because both perform a file copy operation (A copies from network to cache, B copies from source to dest) and use similar I/O stream patterns, which qualifies as partial functionality similarity under BCB's lenient guidelines.
- 共享行为: Both involve reading from an input source and writing to an output file/stream.；Both close resources in finally blocks.
- 行为差异: A returns an InputStream; B returns void.；A uses HTTP connection and caching; B uses FileChannel.；A handles network responses; B does not.；A is synchronized; B is static.
- 修正建议: Incorporate data-flow or program-dependence graphs to capture common I/O patterns.；Use larger context or method summaries.；Train with more examples of Type-4 clones where overall functionality is similar but implementation differs.

### case_id=2734 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `internalCopy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles various command actions in a preferences dialog, saving settings and optionally triggering a restart.
- B 摘要: Copies a file from source to destination, skipping files named 'Thums.db'.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on token-level overlap (e.g., 'File', 'IOException', 'Suku') and missed the vast difference in context and purpose. The model may have been misled by the truncated code and lack of understanding of the overall method structure.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have no semantic overlap, even if they share common API calls like 'File' or 'IOException'. There is no functional similarity.
- 行为差异: Function A is a large UI event handler; B is a small file copying utility.；A deals with preferences and user interface components; B performs low-level I/O.；A has complex logic with multiple commands and conditional restarts; B is straightforward stream copying.；No overlapping functionality or data flow between the two methods.
- 修正建议: Enhance model with global structure awareness, e.g., control flow graphs or abstract syntax trees.；Include method size and cyclomatic complexity as features to distinguish large handlers from small utilities.；Improve handling of long-range semantics by using hierarchical models or attention over larger contexts.

### case_id=2735 FN partial_functionality

- 方法: `main` vs `copyToDir`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts all zip entries to files in the current directory.
- B 摘要: Copies a source file to a specified directory, creating directories as needed.
- 静态失败原因: Static BERT may have focused on the lexical differences (different method names, different API calls) and missed the structural similarity of the read-write loop. The token Jaccard is low (0.23), so the lexical overlap is small.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider both as file I/O operations with a similar buffered copy loop, thus labeling as Type-3/Type-4 clone despite different sources and purposes.
- 共享行为: Both use a buffered read-write loop to transfer data from input to output streams.
- 行为差异: code_a downloads from HTTP and handles zip entries; code_b copies a local file directly.；code_a extracts multiple files; code_b copies a single file.；code_a does not create directories; code_b creates the target directory.；code_a uses ZipInputStream; code_b uses FileInput/OutputStream.
- 修正建议: Improve detection of structural patterns such as buffered I/O loops even across different API calls.；Use dataflow analysis to identify the common stream copy pattern.

### case_id=2736 FN partial_functionality

- 方法: `doTransfer` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an incoming HTTP request to a specified URL, copying headers and body, then writes the response back.
- B 摘要: Fetches a hardcoded URL and reads the response line by line without processing it.
- 静态失败原因: The static model relied heavily on token overlap and structural similarity, which are low (Jaccard=0.132). It failed to recognize the shared abstract behavior of HTTP connection handling due to differing APIs and variable names.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both methods as belonging to the 'HTTP request' semantic category, and thus accept them as Type-4 clones despite differences, because the shared core of opening an HTTP connection and handling exceptions is evident.
- 共享行为: Both open an HTTP connection via URL object；Both read from the input stream of the connection；Both handle MalformedURLException and IOException
- 行为差异: doTransfer forwards request headers and body, and writes the response; run does not forward any data；doTransfer uses HttpURLConnection with DoOutput; run uses URL.openStream() with only input；doTransfer supports multiple HTTP methods; run performs a simple GET
- 修正建议: Incorporate API usage patterns (e.g., URL, HttpURLConnection) as features；Use graph-based representations to capture data flow of HTTP objects；Train with contrastive learning on semantically similar but lexically distinct pairs

### case_id=2737 FN boilerplate_overlap

- 方法: `dump` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies bytes from a source file to a target file using buffered streams.
- B 摘要: Builds an editable website by processing XML/XSLT transformations and writing output files for each page.
- 静态失败原因: The low token Jaccard similarity (0.0556) and very different method names, parameter lists, and code length likely led the model to predict non-clone. Static models lack understanding of broader functional categories like 'file writing' and focus on surface-level syntax.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a clone due to both functions involving file I/O operations, specifically reading input streams and writing output streams, which is a common high-level pattern. However, the core functionality differs significantly; this is likely an annotation error or overly lenient partial similarity.
- 共享行为: Both read from an input stream and write to an output stream；Both handle IOException；Both use FileInputStream
- 行为差异: A is a simple byte-by-byte file copy; B is a multi-step site generation with page iteration, XSLT transformation, and string manipulation；A returns boolean success; B returns void and throws multiple exception types；B uses custom FileSystem and StringWriter, while A uses standard FileOutputStream；B has extensive debugging and conditional logic; A is minimal
- 修正建议: Incorporate API call sequence embeddings to capture shared I/O patterns；Use graph-based models sensitive to data flow and control flow；Train with techniques that distinguish between boilerplate and core logic, e.g., attention over AST paths

### case_id=2738 FN partial_functionality

- 方法: `writeFileType` vs `getContent`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads URIs from a file, for each URI fetches the content via URLConnection, checks for RDF keywords in first 100 lines, and writes classification to an output file.
- B 摘要: Executes an HTTP request using HttpClient, reads the response content line by line, and returns it as a string.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on lexical and syntactic differences (low token Jaccard, different method names, different libraries) and failed to recognize the high-level functional commonality of fetching and reading network content line by line. The model may lack understanding of the overarching 'HTTP retrieval' behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'read content from a network resource and process lines' which could be seen as partial functionality clone (broad Type-4). The shared loop structure and stream reading pattern might be considered sufficient for a lenient annotation.
- 共享行为: Both use BufferedReader to read line by line from an input stream.；Both involve network resource access (HTTP fetch).；Both loop until end of stream.
- 行为差异: A reads URIs from a file and filters by line number; B directly executes an HttpUriRequest.；A writes to a file; B returns a string.；A classifies content based on ontology keywords; B simply aggregates all lines.；A uses URLConnection; B uses HttpClient.
- 修正建议: Incorporate dataflow analysis to identify common patterns like 'open stream, read lines, close stream'.；Use pre-training on code with more emphasis on functional similarity and library-independent behavior.；Consider fine-tuning on clone detection tasks that include Type-4 clones with low syntactic overlap.

### case_id=2739 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts all hyperlinks and anchor texts from a given URL's HTML content and returns them as vectors.
- B 摘要: Searches Google Images for a query, extracts image URLs from the result page, and updates a UI component with the first image.
- 静态失败原因: The model was misled by lexical and API overlap (URL, HttpURLConnection, BufferedReader, InputStreamReader) and similar control flow (while read loop), ignoring deeper semantic differences in domain and output behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: Although both fetch HTML and extract URLs via regex, their functional domains (general link extraction vs. Google image search) and output semantics (return value vs. side effects) are sufficiently distinct that BCB likely labels them as non-clones.
- 共享行为: Open a URL connection and read HTML content line by line；Concatenate lines into a single string；Use regular expressions to extract URLs from the HTML
- 行为差异: A extracts arbitrary hyperlinks from any URL; B specifically extracts image URLs from Google Images results；A returns two vectors containing links and texts; B modifies a class variable and updates UI components；A uses multiple regex patterns and converts relative URLs to absolute; B uses a single split pattern on Google-specific markup
- 修正建议: Incorporate data-flow analysis to differentiate return-based vs. side-effect-based outputs；Focus on method's functional purpose by detecting domain-specific constants (e.g., 'images.google.com') or output types；Use context about class fields and UI interactions to distinguish methods with different external effects

### case_id=2740 FP lexical_or_api_overlap

- 方法: `perform` vs `calculate`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A Struts action that processes a classification request by reading form data, building XML, sending it to a service, and returning a forward based on success or failure.
- B 摘要: A utility method that computes the SHA-1 hash digest of a file's contents and returns it as a hex string.
- 静态失败原因: The static model likely focused on shared API usage (BufferedReader, StringBuffer, while-readline pattern) and overlooked the completely different high-level semantics, leading to a false positive clone prediction.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench labels Type-4 clones as functionally similar but with different implementations. Here, the two functions have completely different purposes (web classification vs. file hashing), so BCB would never consider them clones even under broad Type-4 criteria.
- 行为差异: Function A handles HTTP request/response and session management, while B just processes a file.；Function A builds XML and makes a network call, B computes a hash.；Function A returns an ActionForward for navigation, B returns a String hash.；Function A has complex control flow with multiple conditions and error handling specific to classification, B is straightforward with simple file reading and hashing.
- 修正建议: Improve training with more diverse examples of non-clones that share common I/O patterns but differ in purpose.；Incorporate structural or data-flow information to distinguish between different tasks (e.g., hash vs. network communication).；Add contrastive learning on pairs with similar boilerplate but different semantics.

### case_id=2741 FP lexical_or_api_overlap

- 方法: `downloadURLtoString` vs `readZoneIDs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads content from a URL and returns it as a single string.
- B 摘要: Reads integer IDs from a resource file and returns them as a HashSet.
- 静态失败原因: Static BERT models often rely on token overlap and structural patterns. Here, both functions share common APIs like URL.openStream(), InputStreamReader, readLine(), and a while loop structure, leading to high similarity in token sequences despite different functionality. The model may have prioritized these shared library calls over the distinct semantics of string concatenation vs integer parsing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels Type-4 (different functionality) as non-clones. Although both read from a URL, the purpose and output differ significantly, so BCB would not consider them clones.
- 共享行为: Both open a URL stream；Both read lines in a loop；Both close resources (A closes BufferedReader, B closes internally via try-with-resources? Not shown but LineNumberReader is closed)；Both use InputStreamReader to read text from URL stream
- 行为差异: Return type: String vs HashSet<Integer>；Input: URL object vs String zoneFileName；Line processing: A appends each line to a StringBuffer, B parses each line as Integer and adds to set；Error handling: A throws IOException to caller, B catches Exception and prints stack trace
- 修正建议: Include learning of program output types and data flow；Incorporate control flow and data dependency analysis；Use graph-based representations that capture the transformation of data (e.g., type changes, set vs string)；Add contrastive training on examples with similar API usage but different functionality

### case_id=2742 FP lexical_or_api_overlap

- 方法: `getUser` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Load a User by login from DAO or parse a config file
- B 摘要: Construct a YouTube download URL by parsing page data
- 静态失败原因: The model likely over-weighted common API tokens (BufferedReader, InputStreamReader, URL, etc.) and structural similarity, ignoring differences in return types and parameters.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered non-clone because the two functions serve entirely different business logic despite sharing common I/O patterns.
- 共享行为: Read data from a URL/stream line by line；Parse tokens from lines using delimiters；Use try-catch for exception handling
- 行为差异: Function A returns a User object; Function B returns a String URL；Function A is parameterized by userlogin; Function B uses an instance variable；Function A involves saving to a DAO; Function B does not；Different overall purpose: authentication vs. URL extraction
- 修正建议: Incorporate data-flow and control-flow analysis to differentiate business logic；Leverage type information of parameters and return values；Use task-specific training to ignore boilerplate code

### case_id=2743 FN partial_functionality

- 方法: `copyResource` vs `testAddLinkToImage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file using a manual byte-by-byte stream copy.
- B 摘要: Copies multiple image resources from the classpath to the current test folder and adds links to them in a report.
- 静态失败原因: The model likely relied on lexical similarity (low Jaccard=0.09) and structural matching, missing the deeper semantic equivalence of stream copying due to different method names, variable names, and the presence of test-specific code in B.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a Type-4 clone because both functions perform the core semantic operation of copying an input stream to a file output stream, even though the contexts differ. The manual loop in A and the IOUtils.copy in B are functionally equivalent for this purpose.
- 共享行为: Both open an InputStream from a resource location；Both write the stream content to a FileOutputStream；Both involve copying data from input to output in a file context
- 行为差异: Function A uses a manual read-write loop; Function B uses the library method IOUtils.copy；Function A copies a single resource; Function B copies multiple images and adds report links；Function B is a test method with annotations and report-specific logic not present in A
- 修正建议: Train the model to recognize functional equivalence between manual stream loops and library methods like IOUtils.copy；Include more diverse examples of stream-copy patterns in different contexts；Incorporate data-flow analysis to capture the core I/O operation despite syntactic differences

### case_id=2744 FN benchmark_preference_bias

- 方法: `loadDefaultSettings` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a default configuration file from classpath to a specified file path, handling exceptions and closing streams.
- B 摘要: Handles an HTTP GET request by retrieving a page parameter, querying a page object, checking permissions, rendering the page with caching and logging, and managing responses.
- 静态失败原因: Static BERT correctly predicted non-clone because it identified the vast difference in functionality and low token overlap. This is not a failure; the BCB label is likely erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this pair as clones due to superficial similarities in structure (try-catch-finally) and I/O operations, which can be considered Type-4 (semantic) clones under a very broad interpretation, but this is unlikely.
- 共享行为: Both use try-catch-finally blocks for resource management and exception handling.
- 行为差异: Function A performs a simple file copy; Function B performs complex web request handling with page retrieval, user permissions, caching, and HTML generation.；Function A deals with a single static resource; Function B interacts with HTTP requests and responses, database-like queries, and session management.；The complexity and length of Function B far exceed those of Function A.；Function A is a utility method; Function B is a core servlet handler.
- 修正建议: Re-evaluate the BCB annotation for this pair; it may be a false positive in the benchmark.；Use more rigorous functional criteria to distinguish such pairs in clone detection benchmarks.

### case_id=2745 FN lexical_or_api_overlap

- 方法: `runScript` vs `setMembers`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from a URL byte by byte and returns its content as a string.
- B 摘要: Fetches an HTML page from a URL, parses it to extract component and priority options from select elements, and stores them in class-level arrays.
- 静态失败原因: Static BERT models may have focused on the shared API calls (URL, openStream) and simple loops, while missing the dramatically different downstream processing. The token Jaccard is low (0.15), but models might be misled by overlapping tokens like 'URL', 'try', 'catch', 'Exception', 'String'.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as a clone due to both methods involving URL.openStream() and reading data, a common pattern that could be considered a Type-3 clone with similar I/O structure, but the actual functionality is very different.
- 共享行为: Both open a URL stream and read input data.
- 行为差异: Code A reads raw bytes and concatenates into a string; Code B reads lines and parses HTML.；Code A returns the data; Code B sets class fields with parsed values.；Code A has no HTML parsing; Code B uses regex to extract options.；Error handling differs: Code A returns 'error!' string; Code B prints messages.
- 修正建议: Incorporate control flow and data dependency information to distinguish different processing of read data.；Use graph-based models that capture variable usage patterns and output types.；Train on more diverse examples to avoid overemphasizing common API sequences.

### case_id=2746 FN partial_functionality

- 方法: `download` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Downloads a resource from the classpath to a user-selected file using a save dialog and IOUtils.copy.
- B 摘要: Launches a build configuration for a NexOpen project, including conditional copying of a reverse engineering file from bundle resources to the project.
- 静态失败原因: Static BERT/GraphCodeBERT models often rely on token similarity and API overlap, which are very low (Jaccard 0.065). The shared subpattern (resource copy) is overshadowed by the vastly different overall structure, length, and domain-specific APIs, causing the model to miss the clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this as a clone because both functions contain a similar sub-operation: copying a classpath resource to a file via IOUtils.copy, which is a common utility pattern. Despite differing contexts, BigCloneBench annotations sometimes include such partial functionality clones.
- 共享行为: Both copy a resource from classpath/bundle to a file using IOUtils.copy.；Both handle IOException and use exception dialogs/logging.
- 行为差异: Function A is a simple file download triggered by a user save dialog, while B is part of a complex Eclipse launch configuration.；Function B involves XML parsing, project property manipulation, and conditional file creation, which A does not.；Function A only copies one resource; B conditionally copies a resource based on dialect and also writes a string replacement.；Function A uses Activator.showSaveDialog and Activator.showExceptionDialog; B uses Eclipse-specific APIs like ContentHandlerTemplate, InstallProjectAction, etc.
- 修正建议: Enhance the model to recognize common utility patterns across different contexts, e.g., by learning subgraph matching for I/O copy operations.；Use dependency-based features or program slicing to isolate shared sub-behaviors.；Incorporate more robust structural matching that can capture partial clones with low token overlap.

### case_id=2747 FP boilerplate_overlap

- 方法: `importRoles` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads an XML-like list of role names from a URL and parses each role name into a RoleName object.
- B 摘要: Fetches a version string from a fixed remote URL by reading the first line.
- 静态失败原因: Static BERT/GraphCodeBERT may have over-emphasized token overlap (URL, BufferedReader, readLine, while loop) and missed the semantic difference in the loop's accumulation logic and the return type.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones for functions that have different output types and different core logic, even if they share common I/O boilerplate.
- 共享行为: Both open a URL and read lines using BufferedReader；Both catch IOException (and other exceptions) and return a default value；Both use similar HTTP GET boilerplate
- 行为差异: Function A parses multiple XML-like segments into an ArrayList of RoleName objects, while Function B returns a single string；Function A accumulates lines into a buffer until a closing tag, while Function B simply reads all lines and keeps the last one；Function A involves XML parsing via ProfileParser, while Function B does no parsing
- 修正建议: Incorporate dataflow analysis to distinguish accumulation vs simple reading；Use type/return-type information as a feature；Train with more examples where boilerplate code is shared but semantics differ

### case_id=2748 FN benchmark_preference_bias

- 方法: `readPage` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a URL line by line, optionally skipping lines starting with '#', and returns concatenated HTML content.
- B 摘要: Sends an XML request to a geo-parser URL, reads the response line by line, parses XML to extract place names and optional gazetteer IDs, implements retry logic, and returns a collection of tuples.
- 静态失败原因: The static BERT model correctly identified the low lexical overlap (Jaccard=0.12) and large structural differences, predicting non-clone. However, the BCB label reflects a more lenient annotation standard, causing a mismatch.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to broad Type-4 functional similarity: both 'read data from a URL with a boolean flag affecting processing', ignoring the significant differences in domain and complexity.
- 共享行为: Both read lines from a URL using BufferedReader and InputStreamReader；Both have a boolean parameter that modifies processing within a while loop；Both concatenate lines read from the URL
- 行为差异: Function A returns raw HTML string; Function B returns a structured collection of tuples；Function B constructs complex XML request, handles multiple encodings, and includes error handling with retries；Function B parses XML response and extracts specific elements; Function A performs no parsing；Function A conditionally skips comment lines; Function B conditionally requests gazetteer IDs
- 修正建议: Use a model that captures high-level functional similarity beyond lexical overlap；Incorporate task-specific heuristics to recognize broad I/O patterns；Re-evaluate BCB annotations for consistency with strict or partial clones

### case_id=2749 FP lexical_or_api_overlap

- 方法: `import_hints` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a hint file from a URL or file, parses piece placements, and sets them on a board.
- B 摘要: Makes an HTTP GET request to a URL and returns the first line of the response.
- 静态失败原因: The static embedding model likely overemphasized the lexical similarity (both use URL, BufferedReader, readLine) and missed the deeper semantic differences in purpose and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically marks as non-clone when functions have different domains and are not semantically equivalent, even if there is some API overlap.
- 共享行为: Both open a URL and create a BufferedReader from an InputStream.；Both read the first line of input using readLine().；Both use java.net.URL and java.io.BufferedReader.
- 行为差异: Function A parses multiple lines of tokens to place pieces on a board; Function B only reads a single line and returns it.；Function A handles both URL and file-based input; Function B only uses HTTP via HttpURLConnection.；Function A has a loop and interacts with a game board; Function B simply disconnects after reading.；Function A can catch IOException and return false; Function B throws Exception.
- 修正建议: Incorporate structural or dataflow analysis to capture distinct control flow and data usage patterns.；Use contrastive learning to penalize high similarity scores for functions with different high-level goals.

### case_id=2750 FP lexical_or_api_overlap

- 方法: `getRequestContent` vs `readURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads the first line of content from a URL specified as a string, returning that line.
- B 摘要: Opens a URL and prints all lines of its content to standard output, with exception handling and stream cleanup.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token-level overlap and sequence similarity; both functions share common API tokens (BufferedReader, InputStreamReader, readLine) leading to false positive, while ignoring semantic differences in control flow and return value.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically does not consider these clones because the output behavior differs significantly (return vs print) and input types differ, despite shared I/O boilerplate.
- 共享行为: Both read content from a URL using BufferedReader/InputStreamReader/InputStream；Both use readLine() to read lines
- 行为差异: A returns the first line as a String; B prints all lines to System.out and returns void；A uses HttpURLConnection; B uses URL.openStream()；A throws Exception; B catches exceptions and prints stack trace；A reads only one line; B reads all lines in a loop
- 修正建议: Incorporate control flow analysis (loop vs no loop) into model；Consider return type and side effects (printing vs returning)；Use data flow or more fine-grained semantic representations；Include exception handling patterns

### case_id=2751 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `writeData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by updating or adding a named message-value pair.
- B 摘要: Writes a tab-separated file containing acquisition metadata and peak data derived from input arrays.
- 静态失败原因: The static model correctly identified them as non-clones due to low lexical overlap and distinct structural patterns (properties vs. tabular writing). The BCB label itself may be anomalous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'writing to a file' and overlooked the entirely different data formats and logic, possibly due to a broad interpretation of file output clones.
- 共享行为: Both perform file I/O to write content to a file.
- 行为差异: Code A reads and modifies an existing properties file; Code B writes a new file with tabular data.；Code A handles locale-specific files and updates a key-value pair; Code B writes a multi-column table with dates and peaks.；Code A uses BufferedReader/FileWriter; Code B uses PrintWriter and Scanner.；Code A checks for file existence and copies a default; Code B does not.
- 修正建议: Improve annotation guidelines to require more than superficial file I/O similarity.；Verify BCB annotations for potential mislabeling in this case.

### case_id=2752 FN partial_functionality

- 方法: `runInternal` vs `sendRequestObjectResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Establishes HTTP connection to fetch and parse an OPDS catalog with pagination and file download.
- B 摘要: Sends an XML request to a servlet via HTTP, receives response, and saves it to a file based on content type.
- 静态失败原因: The model likely focused on low token overlap (Jaccard 0.145) and missed the structural similarity of HTTP connection patterns, due to different method names, comments, and high-level logic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers broad Type-3/Type-4 clones: both are HTTP client methods with similar connection setup, stream handling, and error management, despite different specific purposes.
- 共享行为: Both use HttpURLConnection to open network connections；Both set request properties (User-Agent, Content-type)；Both handle input/output streams and errors
- 行为差异: A parses OPDS catalog entries; B saves response to a file and opens browser；A handles pagination via nextLink; B does not；A returns void via callback; B returns a filename string
- 修正建议: Incorporate program structure or data flow analysis to detect common HTTP request patterns；Use graph-based models that capture control flow similarities；Increase training data for partial function clones

### case_id=2753 FN partial_functionality

- 方法: `readFixString` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a fixed number of bytes from an input stream and returns them as a string, wrapping IOException in a runtime exception.
- B 摘要: Builds an editable site by processing page data, reading configuration files, performing XML transformations, and writing output files.
- 静态失败原因: The static model correctly identified low token overlap and different method names, but failed to recognize the abstract similarity that BCB considered, likely because the model lacks reasoning about high-level functional purpose beyond token and structure.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered both as I/O operations that read from streams and write to string buffers, accepting broad type-4 similarity based on generic functionality despite different contexts.
- 共享行为: Both use StringWriter to accumulate string output；Both read data from input streams
- 行为差异: Function A reads a fixed-length string; Function B builds a whole website from multiple files；Function A is a utility method; Function B is a complex business logic method with side effects；Function A returns the string; Function B writes to output files and returns void；Function A uses IOUtils.copy; Function B uses custom file system operations and XML transformations
- 修正建议: Incorporate functional flow analysis to detect abstract I/O patterns；Improve semantic embeddings to capture higher-level similarities like 'read from stream to string'

### case_id=2754 FP long_range_semantics

- 方法: `parse` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses an InputStream by checking resource name in metadata and either copying to a file or delegating to downstream parser.
- B 摘要: Reads string constants to populate multiple hash sets and a map for a Wylie transcription system, including parsing a file.
- 静态失败原因: The static BERT/GraphCodeBERT model likely misclassified due to the presence of common tokens (e.g., 'parse', 'stream', 'IOException') and the overall data-processing theme, but the functions are semantically disjoint and the model may have been fooled by the long and complex function B.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would not consider these clones as they have different method names, parameters, and completely different functionality; they are semantically unrelated.
- 共享行为: Both involve reading input data for further processing.
- 行为差异: Function A uses InputStream and delegates parsing; Function B tokenizes static string constants and initializes data structures.；Function A interacts with files and downstream parser; Function B builds hash sets and maps.；Function A is a short conditional; Function B has many loops and complex file parsing logic.
- 修正建议: Improve long-range semantic understanding through hierarchical models or graph-based representations.；Use better feature extraction to capture function-level semantics beyond token overlap.

### case_id=2755 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `sendRequestObjectResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs an HTTP GET request to a fixed Twitter URL and returns the response body as a string.
- B 摘要: Sends an HTTP POST request with XML data (gzipped) to a configurable server, saves the response to a file based on content type, and returns the file path.
- 静态失败原因: The model likely overemphasized shared API usage (e.g., HttpClient, InputStream, exceptions) and ignored the divergent control flow, data processing, and output behavior, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have very different purposes (simple fetch vs. complex file download) and significant behavioral differences, even though both involve HTTP.
- 共享行为: Both use HTTP client for network communication；Both read from an InputStream；Both handle exceptions
- 行为差异: A uses GET with fixed URL; B uses POST with dynamic URL and XML data；A returns response string; B saves response to file and returns file path；B includes compression, content-type detection, file creation, and user dialogs；B has extensive server configuration and error handling
- 修正建议: Incorporate data flow and control flow analysis；Use graph-based representations to capture structural differences；Include more discriminative features like output type and side effects

### case_id=2756 FN benchmark_preference_bias

- 方法: `getFile` vs `createButtonCopyToClipboard`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint address, and saves it to a temporary directory, returning the file path.
- B 摘要: Creates a button in a SWT shell that copies an environment report to clipboard when clicked.
- 静态失败原因: Static BERT correctly identified the lack of similarity due to low token overlap and completely different contexts; the BCB label appears to be a mislabel.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label may be erroneous or result from an overly broad interpretation of 'resource copying' (A copies a file, B copies to clipboard), but the functions share no meaningful functional similarity.
- 行为差异: Function A performs network I/O and file manipulation with XML parsing; Function B creates a GUI component with event handling.；Function A returns a String; Function B returns void.；Function A handles multiple exceptions; Function B has no exception handling.；Function A involves downloading and modifying remote content; Function B interacts with the system clipboard.
- 修正建议: Re-examine the BCB ground truth for this pair; consider removing or re-labeling such pairs to avoid bias.

### case_id=2757 FP lexical_or_api_overlap

- 方法: `addFileToTarGz` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Recursively adds a file or directory to a tar.gz archive, handling both files and subdirectories.
- B 摘要: Handles UI action events from various buttons, updates preferences, and refreshes UI components accordingly.
- 静态失败原因: The static model likely false-positives due to superficial similarities like using File, IOUtils, and file path handling in both, plus the presence of common Java structural elements (e.g., try-catch, for loops) that the model overweights.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they have entirely different purposes and no shared logical behavior.
- 行为差异: Function A performs file compression; function B handles UI events.；Function A uses TarArchiveOutputStream; function B uses JFileChooser and UI components.；Function A is recursive over the filesystem; function B is event-driven with conditional commands.；Function A saves to an archive; function B saves user preferences and updates UI state.
- 修正建议: Incorporate dataflow analysis to distinguish file I/O from UI event handling.；Use program dependency graphs to capture high-level intent rather than token-level patterns.；Train with more diverse negative examples to reduce overgeneralization of common APIs.

### case_id=2758 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for version updates by reading a version check URL and parsing build numbers.
- B 摘要: Loads an OSGi framework factory by reading a service configuration file and instantiating a class.
- 静态失败原因: Static model likely overemphasized token overlap like 'BufferedReader', 'readLine', 'close', and 'URL', ignoring the distinct method names, comments, and overall purpose. It was misled by common boilerplate for reading from a URL/stream.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because despite similar I/O patterns, the functionality and semantics are entirely different. BCB prioritizes functional equivalence over syntactic overlap.
- 共享行为: Both read a URL/stream line by line using BufferedReader；Both parse lines for specific patterns；Both close the stream after reading
- 行为差异: Different purpose: version checking vs. OSGi factory loading；Different URL sources: remote URL vs. classpath resource；Different parsing logic: build numbers vs. class name；Different error handling: exception caught vs. thrown
- 修正建议: Incorporate method names and higher-level code semantics；Use AST-based features to distinguish structural patterns from semantics；Train on more non-clone pairs with similar boilerplate to reduce false positives

### case_id=2759 FN partial_functionality

- 方法: `copyResource` vs `process`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file path to a destination file using byte-by-byte stream copy.
- B 摘要: Processes a template to generate an output file, handling multiple template types (freemarker, xslt, copy) and constructing destination paths.
- 静态失败原因: The static BERT/GraphCodeBERT model correctly predicted non-clone based on low token overlap and clear structural differences; it did not fail but rather disagreed with the BCB annotation.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to the 'copy' subcase in B resembling A's functionality, and a broad interpretation of file/resource copying as a shared high-level behavior.
- 共享行为: Both involve reading from an input source and writing to an output destination.；Both close streams/resources (A explicitly, B via IOUtils.closeQuietly).；Both handle exceptions (A throws, B wraps in ModelGenerationException).
- 行为差异: A is a simple file/resource copy; B is a template processing engine with multiple cases.；A uses InputStream and OutputStream; B uses InputStream and Writer.；B determines destination path based on template properties and type; A has fixed destination.；B has a 'copy' subcase that approximates A, but also handles freemarker and xslt transformations.
- 修正建议: Train models to recognize that partial overlap in a subcase does not imply whole-function clone.；Incorporate control-flow and call-graph analysis to distinguish simple copy from complex template processing.；Use finer-grained clone types or label noise handling.

### case_id=2760 FN partial_functionality

- 方法: `runScript` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from the applet's codebase into a string.
- B 摘要: Checks for version updates by reading a version file from a URL and parsing build numbers.
- 静态失败原因: The static model focused on token-level differences (low Jaccard similarity) and specific identifiers, missing the structural similarity of the URL reading boilerplate.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled as clone because both functions share the high-level pattern of fetching data from a URL, reading it until EOF, and handling exceptions, which is a common Type-3/Type-4 scenario in BigCloneBench.
- 共享行为: Both functions open a URL and read from an InputStream.；Both handle IOException with a catch block.；Both perform a read loop until EOF.
- 行为差异: Function A returns the entire content as a string; function B parses specific lines and calls another method.；Function A is generic script loading; function B is specific version checking with GUI interaction.；Function A uses BufferedInputStream and byte-level reading; function B uses BufferedReader and line-level reading.；Function A returns "error!" on exception; function B shows an error dialog and hides wait cursor.
- 修正建议: Use AST-based or graph-based clone detection to capture higher-level structural patterns.；Consider dataflow analysis to identify common I/O operations (URL opening, stream reading, error handling).；Weigh method-level similarity more than token-level for such boilerplate-heavy functions.

### case_id=2761 FP lexical_or_api_overlap

- 方法: `getJSONData` vs `get`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A generic function that fetches a URL using Apache HttpClient and parses the response as a JSON object.
- B 摘要: A function that fetches game records from a URL using HttpURLConnection, with custom headers, parsing lines into GameRecord objects while skipping comments.
- 静态失败原因: Static BERT models often rely on token-level overlap and API sequences. Both functions share common tokens like 'URL', 'get', 'BufferedReader', 'readLine', 'while', 'catch', which cause high lexical similarity. The model may miss the semantic differences in parsing and return types due to limited understanding of data flow and high-level purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically considers functions performing distinct tasks (e.g., JSON parsing vs. tabular record parsing) as non-clones, even if they both fetch URLs. The return types and processing logic are fundamentally different, so BCB likely labels this as non-clone.
- 共享行为: Both perform an HTTP GET request to a given URL.；Both read the response stream using BufferedReader.；Both return null on error.
- 行为差异: Function A uses Apache HttpClient, while Function B uses HttpURLConnection.；Function A parses the entire response as JSON; Function B parses lines into GameRecord objects.；Function A returns a single JSONObject; Function B returns an array of GameRecord.；Function A has only the URL parameter; Function B has additional parameters for latitude, longitude, and count.
- 修正建议: Incorporate type information and method signatures into the model.；Use graph-based representations that capture control and data flow differences.；Train with more contrastive examples that separate HTTP fetching with different parsing targets.；Include return type matching in the clone criteria.

### case_id=2762 FN partial_functionality

- 方法: `httpRequestByPOST` vs `getPagina`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs an HTTP POST request with parameters and returns the response body as a string, returning null on error.
- B 摘要: Performs an HTTP GET request to a URL and returns the page content as a string, returning error message on exception.
- 静态失败原因: Static BERT models rely on surface-level token similarity and may have been misled by different method names, library usage (APIs), different parameter lists, and error handling patterns. The low Jaccard similarity (0.23) and lack of background knowledge about HTTP methods likely caused it to miss the high-level functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers broad Type-3/Type-4 clones where the overall task (fetching a web page) is the same, even if HTTP method, error handling, or libraries differ. The core functionality of making an HTTP request and reading the response aligns.
- 共享行为: Both fetch content from a URL；Both read the response line by line into a string；Both return a string containing the fetched content or error
- 行为差异: Function A uses POST with URL-encoded parameters; function B uses GET without parameters；Function A uses Apache HttpClient; function B uses java.net.URL；Function A returns null on error; function B returns the error message as a string；Function A has a timeout parameter (unused) and sets error code fields; function B does not
- 修正建议: Incorporate dataflow analysis to track that both functions connect to a URL and retrieve content；Use AST-based differencing with semantic abstraction of HTTP operations；Leverage code summarization or comments to infer the high-level task；Contrast examples of similar tasks with different libraries to learn equivalence

### case_id=2763 FP lexical_or_api_overlap

- 方法: `main` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter JAR from a Prolog file by parsing and applying adapters.
- B 摘要: Generates a license file listing libraries and their metadata from a directory.
- 静态失败原因: Static model may have focused on common keywords like 'main', 'File', 'FileOutputStream', and loop patterns, missing the semantic divergence.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because functions have entirely different core functionality despite both being main methods; the structural overlap is minimal (low Jaccard).
- 共享行为: Both are main methods that process command-line arguments；Both perform file I/O operations
- 行为差异: A parses Prolog and generates adapters, B reads library metadata and writes license info；A writes a JAR file, B writes a text file；Different file processing logic and error handling
- 修正建议: Incorporate dataflow or control flow analysis to distinguish functionality；Train on more diverse examples to avoid overfitting to boilerplate patterns；Use fine-grained semantic similarity metrics

### case_id=2764 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for updated version by reading a version file from a URL and comparing build numbers.
- B 摘要: Retrieves open tickets for a given queue from a Request Tracker REST API by parsing ticket IDs.
- 静态失败原因: Static models like GraphCodeBERT may over-rely on overlapping API calls and control structures (e.g., BufferedReader, try-catch, while loops) while ignoring the high-level intent, leading to a false positive clone prediction.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the two functions have completely different purposes and logic, despite sharing some superficial I/O patterns. The BCB annotation guidelines emphasize functional equivalence or strong similarity, which is absent here.
- 共享行为: Both open a URL connection or HTTP request；Both read input line by line using BufferedReader；Both handle exceptions with try-catch blocks
- 行为差异: Function A checks version info; function B queries a ticket system；Function A uses a hardcoded URL property; function B constructs a dynamic URL with query parameters；Function A only reads with BufferedReader; function B also parses ticket IDs and makes additional API calls
- 修正建议: Incorporate method name or docstring embeddings to capture purpose；Train on data that penalizes superficial API similarity without semantic alignment；Use dataflow analysis to distinguish different data manipulation goals

### case_id=2765 FP long_range_semantics

- 方法: `actionPerformed` vs `copyFromFileToFileUsingNIO`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles various UI actions (Graphviz, ImageMagick, scaling, look-and-feel) in a settings dialog.
- B 摘要: Copies a file to another using NIO FileChannel transfer.
- 静态失败原因: The model likely focused on superficial patterns (e.g., try-catch, method calls) or was confused by the truncated length of code_a, missing the overall semantic context.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would not consider these clones because they perform entirely different operations with no overlap in functionality or implementation structure.
- 共享行为: No meaningful shared behavior; both are Java methods but differ completely in purpose.
- 行为差异: Function A is a large event handler for a GUI; Function B is a short file copy utility.；Function A uses Swing and custom controllers; Function B uses NIO streams.；Function A has many conditional branches; Function B is linear.
- 修正建议: Improve model to capture global program semantics through code summarization or graph-based representations.；Use hierarchical attention to handle long methods.

### case_id=2766 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft handshake by validating username and contacting a session server for authentication.
- B 摘要: Imports biological sequences from a URL by parsing a FASTA-like format into lists of names and sequences.
- 静态失败原因: Static BERT models may focus on surface-level similarities like URL operations, try-catch blocks, and parsing, ignoring the entirely different semantic purposes, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have different domain-specific logic and no functional similarity, even if they share common boilerplate like I/O and exception handling.
- 共享行为: Both use try-catch blocks for exception handling；Both open a URL stream and read data
- 行为差异: Different domains: Minecraft authentication vs. bioinformatics sequence import；Different parsing logic: one validates a username and sends packets, the other tokenizes lines and builds sequence strings；Different control flow: one has multiple conditionals for validation, the other uses a loop until delimiter；Different output: one sends network packets, the other populates lists
- 修正建议: Train with more diverse non-clone pairs emphasizing domain differences；Incorporate structural embeddings that capture high-level semantics；Use data augmentation to reduce sensitivity to boilerplate code

### case_id=2767 FN benchmark_preference_bias

- 方法: `copyFromTo` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using NIO FileChannel, with error handling and preserving the last modified timestamp.
- B 摘要: Launches an Eclipse launch configuration by processing Maven POM files, generating Hibernate reverse engineering resources, and scheduling a project install job.
- 静态失败原因: The static BERT model correctly predicted non-clone because it captured low token overlap and structural differences, indicating no strong semantic similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this pair as a clone due to both methods involving file copying operations and similar exception handling patterns, leading to a broad Type-4 classification based on partial I/O functionality.
- 共享行为: Performs file I/O operations；Handles exceptions with logging or printing
- 行为差异: Function A is a simple file copy utility; Function B is a complex Eclipse launch handler with XML processing and project configuration.；Function A uses FileChannel for efficient copying; Function B uses InputStream/OutputStream and IOUtils for copying within a larger workflow.；Function A has a single clear purpose; Function B involves multiple sub-tasks including property handling, file creation, and job scheduling.
- 修正建议: Refine annotation guidelines to require stronger semantic equivalence beyond shared I/O operations.；Use functional decomposition to ensure partial overlaps are not overemphasized.

### case_id=2768 FP lexical_or_api_overlap

- 方法: `readData` vs `execute`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses string constants into sets and maps for Tibetan transliteration initialization.
- B 摘要: Copies a file from source to destination using file streams with logging and error handling.
- 静态失败原因: Static BERT may have been misled by superficial similarities like common tokens (e.g., 'while', 'new', 'HashSet') or method structure (void, no return), overlooking the entirely different domain and logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB judges clones by semantic similarity; these functions have completely different purposes and no functional overlap, so they are correctly labeled non-clones.
- 共享行为: Both are void methods；Both use try-catch for exception handling
- 行为差异: readData initializes data structures from string tokens；execute performs file I/O operations；Different parameters and no shared logic
- 修正建议: Train on more diverse examples to reduce reliance on keyword overlap；Incorporate data flow or type information to distinguish initialization from I/O

### case_id=2769 FP boilerplate_overlap

- 方法: `encrypt` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes MD5 hash of input string and returns base64-encoded hash.
- B 摘要: Processes Struts form submission by validating session, building XML, sending HTTP request, parsing response, and returning action forward.
- 静态失败原因: Despite low token Jaccard, the model may have been misled by shared boilerplate patterns (try-catch, string operations, method calls) or a bias towards longer functions with similar control flow structures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have distinct purposes, even if both use common Java constructs. These two functions have entirely different domains (encryption vs web action) and no functional overlap.
- 行为差异: Function A is a simple encryption method; function B is a complex web request handler.；A uses MD5 and Base64; B uses XML, HTTP, and session management.；A returns a String; B returns an ActionForward object.；A is synchronized; B is not.
- 修正建议: Train on more diverse non-clones with similar boilerplate but different semantics.；Incorporate structure-aware features that capture overall purpose, such as API usage profiles or data flow.

### case_id=2770 FN benchmark_preference_bias

- 方法: `doGet` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests to serve a portal page, with authentication, caching, and logging.
- B 摘要: Copies a file from source to destination using NIO channels.
- 静态失败原因: The static model correctly detected no strict semantic equivalence, but failed to match the BCB annotation preference which may accept very broad functional similarity (Type-4). The model likely relied on lexical/syntactic features which had low overlap (Jaccard 0.046), so it predicted non-clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as Type-4 (very high-level similarity) because both functions output data to a destination after reading from a source, but this interpretation is too broad and unlikely; the BCB label of 1 may be a mislabel or error.
- 共享行为: Both involve reading from a source and writing to a destination (network response for A, file for B)
- 行为差异: A handles HTTP requests and servlet context; B is a pure file copy；A has authentication, authorization, and logging; B has none；A uses complex control flow and multiple error handling; B is simple and linear；A interacts with servlet API and portal framework; B uses only Java IO
- 修正建议: Train the model to recognize Type-4 clones with very high-level functional similarity；Refine the dataset to remove inconsistent labels where functions have no meaningful similarity

### case_id=2771 FP lexical_or_api_overlap

- 方法: `readData` vs `testReadHelloWorldTxt`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads a configuration file to initialize various character sets and mappings for Tibetan text processing.
- B 摘要: Tests the FSContentResolver by copying a resource file and retrieving its content via different paths, asserting expected results.
- 静态失败原因: The static model likely overemphasized common I/O API tokens (InputStream, FileOutputStream, IOUtils) and overlooked the distinct semantic contexts (initialization vs. testing), possibly due to the truncation in code_a which hid key structural differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB prefers non-clone because the functions have entirely different goals and the only overlap is generic I/O, which is insufficient for Type-3 or Type-4 similarity.
- 共享行为: Both involve reading file content via input streams.；Both use file I/O operations (FileOutputStream, File, etc.).
- 行为差异: A builds data structures for Tibetan character parsing; B asserts file content retrieval from a content resolver.；A is private initialization; B is a JUnit test with assertions.；A processes multiple columns and populates sets/maps; B copies a file and compares strings.；A has complex logic for parsing ini-like files; B has straightforward copy and get operations.
- 修正建议: Enrich training with more examples of test vs. non-test functions.；Incorporate method-level metadata (e.g., visibility, annotations) to distinguish init code from test code.；Use whole-function context rather than truncated code to capture full logic.

### case_id=2772 FN benchmark_preference_bias

- 方法: `serialize` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Serializes an IMS content package to an output stream using a ZIP parser.
- B 摘要: Launches a NexOpen project by processing Maven POM files, setting Hibernate properties, and triggering an install action.
- 静态失败原因: The low token Jaccard (0.051) and clearly different method signatures and logic led the model to correctly predict non-clone, but the BCB label says clone; thus the model appears to have 'failed' only if BCB is assumed ground truth. The model likely relied on lexical and structural cues.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to the presence of IOUtils.copy and stream copying patterns, which might be considered Type-4 (similar functionality at a high level). However, the overall tasks are fundamentally different.
- 共享行为: Both use IOUtils.copy to stream data.；Both involve file I/O operations.
- 行为差异: A: serializes a pre-parsed content package; B: reads and modifies build configuration files.；A: simple copy of a file to an output stream; B: complex Eclipse launch with multiple steps and exception handling.；A: works with IMSCP packages; B: works with NexOpen project structure and Hibernate dialect.；A: uses a parser to serialize to disk then copies; B: directly processes XML documents and properties.
- 修正建议: Re-evaluate the BCB ground-truth label for this pair; it may be a mislabel.；If the label is correct, identify the specific shared sub-behavior (e.g., stream copying) and consider whether that alone justifies a clone according to the benchmark's guidelines.

### case_id=2773 FP lexical_or_api_overlap

- 方法: `addQDInformation` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a local or URL file to update project information with parsed date and value data.
- B 摘要: Loads a OSGi framework factory from a classpath resource file via reflection.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-weighted lexical overlap (URL, BufferedReader, try-finally) and missed the semantic divergence in purpose and output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the overall functionality and purpose are entirely different, despite some I/O boilerplate similarity.
- 共享行为: Both use BufferedReader to read lines from a stream.；Both handle exceptions (IOException, etc.).；Both have try-finally blocks to close resources.
- 行为差异: A updates internal state (_qdDate, _qdValue); B returns a new FrameworkFactory instance.；A reads from file or URL based on a local flag; B loads from classpath resource.；A specifically parses lines starting with 'pg ' and 'pt '; B looks for first non-comment line.；A uses Integer and Double parsing; B uses Class.forName and newInstance.
- 修正建议: Include method signatures and return types in representation.；Use dataflow analysis to distinguish state-updating vs. value-returning.；Add contrastive training on pairs with similar boilerplate but different semantics.

### case_id=2774 FN benchmark_preference_bias

- 方法: `doGet` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET requests for a page, performing authorization, caching, and rendering.
- B 摘要: Copies files from a source directory to a destination directory using file channels.
- 静态失败原因: The static BERT/GraphCodeBERT model correctly predicted non-clone (0) due to low token overlap (Jaccard 0.0856) and clearly different semantics.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label of 1 is likely an annotation error or an outlier, as the two functions share no meaningful functional similarity.
- 行为差异: Function A is a servlet doGet method handling HTTP requests and page rendering; Function B is a main method for file copying.；Function A uses HttpServletRequest/Response and deals with page objects; Function B uses FileChannel and ByteBuffer.；They have no overlap in input parameters, control flow, or output.
- 修正建议: Review and correct the BCB annotation for this pair.；Consider excluding such pairs from evaluation or using majority voting in annotations.

### case_id=2775 FN benchmark_preference_bias

- 方法: `convert` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Converts an ACRNEMA stream file to DICOM format, handling pixel data and UIDs.
- B 摘要: Builds a website for editing by processing pages with XSLT transformations and file I/O.
- 静态失败原因: The static model likely focused on low lexical overlap and lack of shared API calls, but may have missed potential partial functionality similarity in file I/O; however, the functions are semantically distinct, so the model's negative prediction seems correct.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled them as clones due to both functions involving file conversion with similar high-level I/O patterns and error handling, but this is a very broad interpretation that likely does not align with typical Type-3/4 clone definitions.
- 共享行为: Both perform file I/O operations (read and write files).；Both use try-finally blocks for resource management.；Both have loops over data (pixels or pages) and output progress.
- 行为差异: Function A processes image pixel data; Function B processes XML/HTML pages.；Function A checks DICOM headers and UIDs; Function B uses XSLT transformations and string replacements.；Function A has specific logic for 12-bit to 16-bit inflation; Function B handles multiple configuration parameters and file search paths.；The domain-specific operations (DICOM vs. web page generation) are entirely distinct.
- 修正建议: Review BCB annotation for possible mislabel given the low token Jaccard and distinct functionality.；Consider whether both functions share a specific sub-task (e.g., reading a file line by line) that could be refactored, but overall they are not clones.

### case_id=2776 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getUser`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a new version by reading a remote version file and comparing build numbers.
- B 摘要: Retrieves a user by login, loading from DAO or parsing a local config file if not found.
- 静态失败原因: Static BERT models may over-rely on token-level similarity (e.g., 'BufferedReader', 'URL', 'InputStream', 'readLine', 'while') and structural patterns (try-catch, loop), ignoring high-level semantics and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels based on functional equivalence; these functions have completely different goals and behaviors, so they are not clones.
- 共享行为: Open a URL/stream and read lines；Use BufferedReader and InputStream；Parse lines with conditionals；Handle exceptions (IOException/Exception)
- 行为差异: Different purpose: version check vs user retrieval；Different data sources: remote URL vs classpath resource；Different parsing: .version/.build prefixes vs colon-separated tokens；Different output: message display vs User object
- 修正建议: Incorporate dataflow analysis to track variable transformations；Use function name or API call semantics to distinguish domains；Add attention to control-flow differences (e.g., output type)；Train with more diverse negative examples having similar API usage but different functionality

### case_id=2777 FP boilerplate_overlap

- 方法: `run` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a resource file from the classpath and sets its content as text in a Swing component.
- B 摘要: Performs a Google image search by fetching HTML and parsing image URLs from the response.
- 静态失败原因: The static BERT model likely overemphasized the overlapping lexical tokens (URL, BufferedReader, readLine, etc.) and missed the high-level semantic difference in what the functions accomplish.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have completely different purposes, despite sharing some boilerplate I/O code.
- 共享行为: Both open a URL and read lines from a stream using BufferedReader
- 行为差异: Function A reads from a local classpath resource; Function B makes an HTTP request to an external API；Function A updates a Swing component with the file content; Function B parses image URLs and adds them to a list；Function A uses multiple character streams (InputStreamReader, BufferedReader); Function B uses HttpURLConnection and directly reads from its input stream
- 修正建议: Incorporate dataflow analysis to track how the read data is used；Use graph-based code representations that capture control and data dependencies beyond token sequences；Add attention to method names and surrounding context (e.g., class or caller) to disambiguate purpose

### case_id=2778 FP boilerplate_overlap

- 方法: `getContent` vs `getUser`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Executes an HTTP request and returns the response body as a string.
- B 摘要: Retrieves a user object from a DAO or parses a config file if not found, then returns the user.
- 静态失败原因: Static BERT may have overemphasized the shared lexical patterns (e.g., BufferedReader, while loop, try-catch) and missed the distinct higher-level semantics and different I/O sources.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality and output types are completely different, even though both involve reading input streams.
- 共享行为: Both use BufferedReader to read text.；Both have try-catch for exception handling.；Both use while loops to read lines.
- 行为差异: Function A makes an HTTP request; Function B accesses a database or config file.；Function A returns a String; Function B returns a User object.；Function B performs conditional logic to parse tokens and create an object.
- 修正建议: Include more context about the external APIs used.；Use data flow analysis to capture the different sources and sinks.；Train on more diverse examples to reduce reliance on boilerplate tokens.

### case_id=2779 FN benchmark_preference_bias

- 方法: `test` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Tests a StorageStringWriter class for write, read, and exception handling behavior.
- B 摘要: Builds a site for editing by transforming XML files and assembling output pages.
- 静态失败原因: The model correctly predicted non-clone due to low token overlap and clear structural differences; the BCB label appears to be an annotation error or overly broad interpretation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The annotated clone label may have been based on superficial similarity such as both using StringWriter and IOException, or the presence of InputStream and text manipulation, but the overall functionality is entirely different.
- 共享行为: Both use StringWriter and InputStream for I/O operations.
- 行为差异: A is a simple unit test for a storage class; B is a complex multi-step site builder.；A focuses on validating exception throwing and text retrieval; B performs XML transformation, file system operations, FTP interactions, and string manipulation.；A's flow is linear; B has a loop over pages with conditional logic and error handling.；A uses IOUtils.copy for stream copying; B uses custom FileSystem and gadgets for string replacement.
- 修正建议: Review and refine BCB annotation guidelines to avoid labeling based on trivial API usage.；Consider using behavioral or semantic similarity measures rather than superficial token matching.

### case_id=2780 FP boilerplate_overlap

- 方法: `scramble411` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Hashes a password with SHA-1 using two-stage digest and XOR.
- B 摘要: Processes a web form to classify a concept, communicates with an external service via XML/HTTP, and forwards the result.
- 静态失败原因: The model likely over-relied on superficial structural patterns (e.g., try-catch, loops, method calls) shared across many functions, ignoring the wide semantic gap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they perform entirely different functions with no meaningful similarity in algorithm or purpose.
- 共享行为: Both use try-catch blocks for exception handling；Both contain loops (for loop in A, for loop in B)；Both return a value (byte[] in A, ActionForward in B)
- 行为差异: A computes a cryptographic hash; B handles web request/response in a Struts action；A uses MessageDigest for SHA-1; B uses URL/URLConnection for HTTP；A operates on strings and bytes; B operates on session attributes, beans, and XML；A has a single return point; B has multiple conditional return paths
- 修正建议: Train with more diverse negative examples that share boilerplate structure but differ semantically；Incorporate dataflow or call-graph features to capture actual behavior

### case_id=2781 FN benchmark_preference_bias

- 方法: `displayDiffResults` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.0`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Generates an HTML diff report and launches it in a browser.
- B 摘要: Configures and launches a NexOpen Eclipse project, reading POM files and setting properties.
- 静态失败原因: Static BERT models rely on token and structural similarity; these functions have very low token overlap and entirely different code structures, so they should not be considered clones.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotation may have mislabeled due to both involving file I/O and writing output, but that is too broad for a clone.
- 共享行为: Both perform file I/O operations；Both involve writing to output streams
- 行为差异: Different domains: HTML report generation vs Eclipse project launch configuration；Function A is short and focused on presentation, Function B is long and handles project setup, property management, and Maven integration；No common logic or data structures
- 修正建议: Re-evaluate BCB labeling for this pair to correct false positive；Improve training data to avoid labeling unrelated functions as clones

### case_id=2782 FP lexical_or_api_overlap

- 方法: `setBundleInfoName` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a properties file from a URL and updates bundle names in a list based on key-value pairs.
- B 摘要: Constructor for a Swing browser that reads XML from a URL, optionally transforms it with XSL, and displays the result.
- 静态失败原因: The model likely overemphasized the shared API usage (URL, BufferedReader, InputStreamReader) and similar control flow (read loop, try-catch) while missing the high-level semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label non-clone because the functionalities are entirely different: one is a data mapping utility, the other is a GUI constructor.
- 共享行为: Both read from a URL using BufferedReader and InputStreamReader.；Both handle IOException with try-catch.；Both iterate over lines read from the stream.
- 行为差异: Function A processes simple key-value pairs separated by '='; Function B processes XML/XSL with stylesheets and transformers.；Function A updates a list of BundleInfo objects; Function B constructs and displays a GUI browser window.；Function A returns a boolean; Function B is a constructor with no return value.
- 修正建议: Include method name and return type as features.；Use a model that captures overall purpose or class context.；Train on more diverse negative examples with overlapping APIs but different semantics.

### case_id=2783 FN partial_functionality

- 方法: `populateResources` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Populates initial database resources by loading templates and images from resource URLs.
- B 摘要: Reads data from a URL or file path and returns an integer status.
- 静态失败原因: Low token Jaccard similarity (0.104) and different overall program structure (loop vs single read) led the model to focus on lexical differences, missing the shared subsequence of opening a URL and reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may accept as clone because both perform reading from URLs, and the template-reading part of A is similar to B's core functionality, representing partial functionality overlap.
- 共享行为: Both open URL streams；Both handle IOException；Both involve reading from resources
- 行为差异: A saves loaded content as persistent objects; B only returns status；A selects resources from a fixed list; B uses the provided name；A includes image processing; B does not
- 修正建议: Improve handling of subgoal equivalence；Incorporate graph-based data flow to match common I/O patterns

### case_id=2784 FN partial_functionality

- 方法: `getFile` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies soap:address endpoint, and saves to a temporary file.
- B 摘要: Converts an ACRNEMA medical image file to DICOM format by parsing and adding UIDs.
- 静态失败原因: GraphCodeBERT likely focused on the low token overlap and different API calls, correctly predicting non-clone. It might have missed a high-level abstract pattern of 'download/read, modify, save' that BCB considers similar.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'file conversion' utilities that involve reading an input, processing, and writing output, despite different domains. Broad Type-4 could allow partial functional similarity like transforming external data.
- 共享行为: Both read from an input stream and write to an output stream.；Both handle IOException and perform file I/O operations.
- 行为差异: getFile downloads from a URL, converts XML content; convert reads a local file and processes medical image data.；getFile modifies XML elements; convert manipulates DICOM tags and pixel data.；getFile uses NIO channels and streams; convert uses buffered streams and custom pixel encoding.；They target completely different domains (web services vs. medical imaging).
- 修正建议: Add domain-specific features to distinguish web service WSDL processing from medical DICOM conversion.；Use more fine-grained semantic annotations that capture the actual transformation logic.；Train on more examples of Type-4 clones with very different surface forms but similar I/O patterns.

### case_id=2785 FP boilerplate_overlap

- 方法: `readRemoteFile` vs `get`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a remote file line by line and concatenates all lines into a single string, handling EOF and IO errors.
- B 摘要: Sends an HTTP GET request with custom headers, reads the response line by line, filters out comment lines, decodes each line into a GameRecord object, and returns an array of GameRecord, or null on failure.
- 静态失败原因: The static model likely overemphasized lexical overlap in common I/O patterns (URL, BufferedReader, readLine) and missed the semantic differences in data transformation and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have different purposes (generic file reader vs. API client with specific parsing), and the shared boilerplate is insufficient for functional similarity.
- 共享行为: Both open a URL connection and read lines using BufferedReader；Both handle IOException
- 行为差异: code_a returns a concatenated string; code_b returns an array of GameRecord objects；code_a reads a fixed URL; code_b takes parameters and sets HTTP method and headers；code_b filters out lines starting with '#' and decodes them；code_a concatenates all lines including first line; code_b collects objects after filtering
- 修正建议: Incorporate type and return type information into the model；Use data-flow analysis to capture transformations；Train with contrastive examples focusing on functional vs. structural similarity

### case_id=2786 FN partial_functionality

- 方法: `addIDs` vs `callService`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches metabolite IDs and molecular weight from a web service and updates a PeakListRow based on parsed response.
- B 摘要: Fetches raw response from a web service and stores it in an instance variable.
- 静态失败原因: Static BERT models rely on token overlap, which is low (0.15), and may miss the structural similarity of try-catch with URL reading; GraphCodeBERT might not capture the shared dataflow of opening a URL and reading input.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider any pair that uses similar I/O patterns (URL connection, BufferedReader) as functionally related, even if the data processing differs, aligning with Type-4 or partial functional similarity.
- 共享行为: Open HTTP URL and read response line by line using BufferedReader；Close the BufferedReader after reading
- 行为差异: addIDs parses response for specific patterns and sets multiple fields; callService concatenates all lines and stores raw string；addIDs returns an integer score; callService sets an instance variable and has no return value；addIDs takes parameters and modifies an input object; callService uses instance fields and has side effects on an instance variable
- 修正建议: Improve model to recognize common I/O patterns even with different variable names；Use control-flow graph or data-flow similarity to capture shared sequence of URL open-read-close；Consider high-level intent matching via program summarization

### case_id=2787 FP boilerplate_overlap

- 方法: `readData` vs `readAndRewrite`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses comma-separated strings to populate several HashSet collections and reads a configuration file to build mappings for Tibetan, Sanskrit, and other character sets.
- B 摘要: Reads a DICOM image file and rewrites it to another file using DICOM-specific libraries for pixel data handling.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized common boilerplate patterns (static void method, loops, I/O) and failed to capture domain-specific API calls and data structures, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the functions have entirely different domains (text/character set processing vs. DICOM image processing) and share no meaningful functional similarity beyond generic boilerplate.
- 共享行为: Both are private static void methods；Both involve file I/O operations；Both use loops and conditional logic
- 行为差异: Function A initializes multiple sets from tokenized strings; Function B copies DICOM pixel data；Function A parses a complex configuration file; Function B uses DICOM APIs；Function A populates data structures for character mappings; Function B manipulates image files
- 修正建议: Incorporate API call embeddings or domain-specific token embeddings；Focus on core logic rather than infrastructure code；Use a more fine-grained tokenization that distinguishes domain terms

### case_id=2788 FP lexical_or_api_overlap

- 方法: `read` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads and parses camera log records from a URL, handling parsing errors, and sorts the records.
- B 摘要: Fetches a version string from a remote URL, returning the last line read.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on the lexical and structural overlap of opening a URL, reading lines, and closing, missing the high-level semantic difference in data usage. The common API calls (BufferedReader, readLine, close) likely triggered a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functionality is clearly different: reading a camera log vs fetching a version string. Despite similar I/O structure, the methods have different names, return types, and purposes.
- 共享行为: Open a URL connection and create BufferedReader over InputStreamReader；Read lines in a while loop；Close the reader in a finally or catch block；Handle exceptions (one logs, one catches all)
- 行为差异: A processes multiple lines into structured CameraLogRecord objects; B only stores the last line as a string；A sorts the records after reading; B does no sorting；A logs detailed progress; B only prints a debug statement；A throws IOException; B catches all exceptions and returns null on failure
- 修正建议: Train on more examples requiring understanding of method intent beyond API patterns；Incorporate data flow analysis to track how read data is used after reading；Use method names and return types as additional features

### case_id=2789 FN partial_functionality

- 方法: `copyResource` vs `extractResourceToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file using byte-by-byte reading and writing.
- B 摘要: Copies a classpath resource to a file using IOUtils.copy with proper stream management.
- 静态失败原因: Low lexical overlap (Jaccard 0.156) and differences in method structure, API usage, and parameterization prevent BERT from recognizing the semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels methods with the same high-level functionality (copying a resource to a file) as clones, even if implementation details differ significantly, aligning with Type-3/Type-4 classification.
- 共享行为: Both copy a resource to an output file.；Both use input and output streams.；Both close streams after operation.
- 行为差异: A can fallback to local file if URL is null; B only uses classpath resource.；A copies byte by byte; B uses buffered copy via IOUtils.；A uses fields for source/destination; B takes parameters.；B has proper finally block for closing streams; A closes without try-finally.
- 修正建议: Use dataflow analysis to capture resource copy patterns.；Incorporate API aliasing (e.g., getResource vs getResourceAsStream).；Consider abstract syntax trees with structural matching.；Train on broader clone types including many-to-many mappings.

### case_id=2790 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `copyTextFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a Java properties file for a given locale by reading, updating, or adding a property.
- B 摘要: Copies a file from source to destination using buffered byte streams.
- 静态失败原因: Static BERT correctly predicted non-clone because lexical and structural overlap is low; the predicted label 0 is accurate, so the static method did not fail; the discrepancy arises from BCB's overly broad clone definition.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider the file copy sub-step in A as similar to B's entire functionality, leading to a broad Type-3/Type-4 annotation.
- 共享行为: Both perform file I/O with read-write loops
- 行为差异: A processes text properties with parsing and modification; B performs exact binary copy；A includes conditional file creation and property search; B is straightforward copy with error handling；A uses character streams; B uses byte streams
- 修正建议: Re-evaluate BCB annotation for this pair；Use stricter functional equivalence criteria for clone labeling

### case_id=2791 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file by reading, editing, or appending a key-value pair, with fallback copy of English properties file if locale file missing.
- B 摘要: Copies a file from source to destination using buffered byte streams.
- 静态失败原因: Assuming BCB is correct, the model likely relied on low token overlap (0.19) and different method names, ignoring the shared file I/O pattern; but BCB annotation is questionable.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone due to shared file copy sub-functionality in A, considering broad Type-4 functional similarity, but overall semantic intent differs significantly.
- 共享行为: Both read from a file and write to another file；Both close streams in a finally block or after use；Both throw exceptions for invalid states
- 行为差异: A modifies specific properties with key-value editing; B performs generic file copy；A conditionally copies English file only if locale file missing; B always copies；A reads lines and parses key-value pairs; B reads bytes in fixed-size buffer
- 修正建议: Improve semantic understanding of overall method purpose vs. sub-tasks；Incorporate control flow and data flow analysis to distinguish editing from copying；Adjust benchmark to avoid over-labeling based on low-level I/O commonality

### case_id=2792 FN partial_functionality

- 方法: `httpRequestByPOST` vs `fetchUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with parameters, checks status code, reads response body, returns it or null on error with error fields set.
- B 摘要: Fetches URL content via HTTP GET, reads response line by line, returns empty string on exception.
- 静态失败原因: Low token Jaccard (0.275) and differences in API calls (HttpClient vs URL) and error handling patterns led the model to underestimate functional similarity; it missed the high-level purpose of fetching URL content.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as Type-4 clones because both are URL fetching utilities with similar core read-loop behavior, despite differing HTTP methods and error handling.
- 共享行为: Both open a connection to a URL；Both read the response line by line into a string buffer；Both return the resulting string
- 行为差异: Function A uses POST with parameters; B uses GET without；Function A checks HTTP status code < 400; B ignores status；Function A returns null on error and sets error fields; B returns empty string and catches exceptions silently；Function A has a timeout parameter; B does not
- 修正建议: Incorporate data-flow or program dependency analysis to identify common functional purpose；Use high-level semantic representations like code2seq or AST-based techniques；Train on more Type-4 clone examples to learn functional similarity beyond lexical overlap

### case_id=2793 FN benchmark_preference_bias

- 方法: `copy` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file or directory from a Hadoop FileSystem to a local destination, optionally deleting the source.
- B 摘要: Launches a build configuration for a NexOpen Eclipse project, handling Maven POM files and setting up Hibernate reverse engineering.
- 静态失败原因: The static BERT model likely relied on token and structural similarity, which is very low (Jaccard 0.0789), leading to a non-clone prediction. It failed to recognize any hidden similarity that BCB might have seen, possibly due to lack of domain-specific knowledge.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered the common use of IOUtils and file operations as partial functionality similarity, but the methods are too distinct in purpose and structure for a Type-3/Type-4 clone.
- 共享行为: Both involve file system operations (read/write)；Both use IOUtils for stream copying
- 行为差异: Different purpose: file copy vs project build launch；Different input/output: FileSystem path and File vs ILaunchConfiguration and monitors；Different control flow: recursion vs sequential steps；Different exception handling: throws IOException vs throws CoreException and RuntimeException
- 修正建议: Improve semantic understanding by incorporating program flow and domain knowledge；Use fine-grained alignment of API usage patterns with context

### case_id=2794 FN boilerplate_overlap

- 方法: `modifyApplicationMessage` vs `uploadFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale by replacing or adding a key-value pair.
- B 摘要: Copies a file from source to target, either by renaming or by copying bytes.
- 静态失败原因: Static BERT/GraphCodeBERT might have been misled by the lexical overlap of file I/O APIs (File, InputStream, OutputStream, read/write loops, close), focusing on boilerplate similarity rather than high-level purpose.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have considered these as clones because both methods involve reading from an input stream and writing to an output stream with a buffer loop, and both deal with file paths.
- 共享行为: Both involve file I/O operations (reading and writing files)
- 行为差异: A modifies property content; B copies entire file；A uses Properties and BufferedReader to parse key-value; B uses raw byte streams；A handles locale-specific file creation; B handles directory creation and rename；A prints stack trace on exception; B throws IOException
- 修正建议: Use data-flow analysis to capture the transformation of data (properties vs arbitrary bytes)；Incorporate control flow and data dependencies to see that A processes lines, B copies raw bytes；Use more specific API call patterns (like Properties vs FileOutputStream) as distinguishing features

### case_id=2795 FP lexical_or_api_overlap

- 方法: `get` vs `sendRequest`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Makes an HTTP GET request with custom headers to retrieve game records from a URL and returns an array of GameRecord objects.
- B 摘要: Constructs an HTTP URL, opens a connection, sends a GZIP-compressed XML request via POST, receives a GZIP-compressed XML response, parses it with JDOM, but returns an empty string.
- 静态失败原因: The static model might have been misled by the similar boilerplate code for opening HTTP connections and handling exceptions, causing false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions serve different purposes (retrieval vs submission) and have different input/output signatures, despite both being network I/O routines.
- 共享行为: Both establish HTTP connections to remote servers；Both set request properties；Both read from the connection's input stream；Both catch exceptions
- 行为差异: Function A uses GET method, Function B uses POST (doOutput=true)；Function A sends latitude/longitude/count headers, Function B sends XML content with compression；Function A returns an array of GameRecord, Function B returns an empty string；Function A ignores header lines ('#'), Function B uses GZIP compression on both request and response
- 修正建议: Improve detection of different HTTP methods and different response handling；Incorporate structural differences in I/O processing；Use data flow analysis to see output differences

### case_id=2796 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the SOAP address endpoint, and returns the file path.
- B 摘要: Copies a local file to a specified directory using NIO file channels.
- 静态失败原因: Low token overlap and different control flow (e.g., XML manipulation, exception types) led the model to focus on overall semantic mismatch, missing the shared I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the core file copying logic (using transferFrom) as a reused pattern, making them a partial functionality clone despite different overall tasks.
- 共享行为: Both use FileChannel.transferFrom to copy file content between input and output streams.
- 行为差异: One involves network download, XML parsing, and temporary file manipulation; the other is a simple local file copy.；Different exception handling: AxisFault vs IOException.；Different return types: String vs void.；Function A has logging and conditional file existence check; B does not.
- 修正建议: Enhance models to recognize common I/O patterns like NIO channel usage across different contexts.；Incorporate program flow analysis to detect similar subroutines within larger functions.；Use contrastive learning on pairs with partial functional overlap.

### case_id=2797 FN boilerplate_overlap

- 方法: `setBundleInfoName` vs `runScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL, parses key-value pairs to update bundle names in a list.
- B 摘要: Reads a script from a URL and returns its content as a string.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on method names and high-level semantics, missing the underlying I/O pattern due to different purposes and return types.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones because both involve reading from a URL and handle I/O, a common boilerplate pattern, and may accept broad Type-4 similarity.
- 共享行为: Both open a URL and read input streams.；Both use try-catch for I/O exceptions.
- 行为差异: A returns boolean; B returns string.；A parses lines with '=' to update a list; B reads all bytes and concatenates.；A uses BufferedReader; B uses BufferedInputStream.；A checks for null lines; B reads until end of stream.
- 修正建议: Incorporate explicit I/O pattern recognition.；Use contrastive learning on URL reading operations.；Add dataflow analysis to compare input/output transformations.

### case_id=2798 FP lexical_or_api_overlap

- 方法: `readIntoList` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads HTML from a URL, extracts link text and command substrings, creates JMenuItem objects with action listeners, and populates a map.
- B 摘要: Queries Google Images for artist/album, downloads the result page, extracts image URLs from href attributes, and stores them in a list.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token patterns and may overweight common I/O tokens (URL, BufferedReader, openStream, etc.) while missing the semantic differences in parsing logic and output types. The high lexical overlap in boilerplate code overshadowed the divergent purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically distinguishes Type-4 clones based on high-level functional similarity. Despite shared I/O boilerplate, the core purpose (GUI menu creation vs. web scraping for images) is distinct, so BCB likely labels as non-clone.
- 共享行为: Open an HTTP connection to a URL；Read input stream using BufferedReader and InputStreamReader；Parse HTML content for specific patterns using string operations；Handle exceptions with try-catch blocks
- 行为差异: readIntoList creates GUI components (JMenuItem) with action listeners; googleImageSearch only collects string URLs；readIntoList processes lines individually; googleImageSearch concatenates all lines before parsing；readIntoList uses URL.openStream(); googleImageSearch uses HttpURLConnection with a User-Agent header；Parsing target: readIntoList extracts anchor text between > and </a>; googleImageSearch extracts image URLs after /imgres?imgurl= and before &amp;
- 修正建议: Incorporate dataflow analysis to track how extracted data is used (e.g., GUI components vs. list storage).；Enhance input with structural information like method return type and parameter types.；Use larger context such as class name or method invocations to capture domain-specific semantics.

### case_id=2799 FP boilerplate_overlap

- 方法: `getVersion` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a version string from a hardcoded URL and returns it.
- B 摘要: Downloads content from a given URL to a temporary file with authentication and progress tracking.
- 静态失败原因: The static model likely overemphasized token overlap (e.g., 'URL', 'openConnection', 'BufferedReader', 'readLine') and structural similarity of the reading loop, ignoring differences in return type, method purpose, and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because the overall functionality differs significantly (version retrieval vs file download with progress). The shared pattern is generic boilerplate.
- 共享行为: Both open a URL connection and read lines using BufferedReader.
- 行为差异: Function A returns a string; function B is void.；Function A uses a hardcoded URL; function B takes URL as parameter.；Function B includes authentication, file writing, and status label updates.
- 修正建议: Incorporate method signature and return type comparison.；Add data flow analysis to distinguish how read data is used.；Include features for method length and complexity.

### case_id=2800 FN benchmark_preference_bias

- 方法: `getFile` vs `decodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the wsdlsoap:address location, and saves the modified XML to a temporary file, returning the file path.
- B 摘要: Reads a Base64-encoded input file, decodes it, and writes the decoded content to an output file, returning a boolean success flag.
- 静态失败原因: The static model likely correctly identified low token overlap (Jaccard 0.144) and different method names, leading to a non-clone prediction; it did not fail but disagreed with a possibly lenient BCB annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'file transformation' functions with input-output stream handling, thus categorizing them as Type-4 clones despite different transformations.
- 共享行为: Both involve reading from an input source and writing to an output file using I/O streams.
- 行为差异: Function A fetches data from a network URL, parses XML, and modifies elements; Function B decodes Base64 data.；Function A returns a file path; Function B returns a boolean.；Function A checks file existence and handles multiple exception types; Function B only catches IOException.
- 修正建议: Re-evaluate BCB annotation consistency for abstract functional similarity.；If aligning with BCB, incorporate broader semantic categories like 'file I/O with transformation'.

### case_id=2801 FN partial_functionality

- 方法: `main` vs `createHTML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.5`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Constructs and sends an HTTP POST request to a social network API with hardcoded parameters and prints the response.
- B 摘要: Generates an HTML page by reading a CSS file and querying a database for dashboard content based on a page type enum.
- 静态失败原因: Static BERT models rely heavily on token-level and structural similarity. The functions have very low token Jaccard (0.067) and share only generic I/O patterns (BufferedReader, URL, etc.). The semantic similarity at a higher level (both do I/O) is not captured by token embeddings. Additionally, GraphCodeBERT may not capture the long-range dataflow similarity as the data sources are completely different.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as Type-4 clones because both functions perform I/O operations (reading from a URL/resource and producing output) using similar low-level patterns (BufferedReader, URL). The overall task of 'reading and outputting' might be considered a common functionality, even though the specific data sources and output formats differ.
- 共享行为: Both use URL to access a resource；Both use BufferedReader to read line by line；Both involve string concatenation/build of output
- 行为差异: Function A sends an HTTP POST request while B reads a local file from classpath；Function A uses HttpURLConnection and prints to console, B returns an HTML string；Function B includes database queries and conditional logic based on an enum, A has none；Function A contains hardcoded API parameters, B has dynamic content from DB
- 修正建议: Improve model's ability to recognize common I/O patterns as indicating semantic similarity；Use dataflow analysis to identify that both functions read from an external source and produce output；Incorporate API usage similarity (both use URL, BufferedReader)

### case_id=2802 FP lexical_or_api_overlap

- 方法: `addQDInformation` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Updates QD information by reading a file (local or remote) and parsing specific line prefixes.
- B 摘要: Checks for software upgrades by querying a license server, parsing response, and updating database and UI.
- 静态失败原因: Static model overemphasized common API keywords (URL, BufferedReader, while loop) and missed the distinct purpose and logic, possibly due to limited contextual understanding and long-range dependencies.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone due to low token similarity (Jaccard 0.12) and distinct high-level functionality; BCB typically requires moderate functional or structural similarity.
- 共享行为: Both use URL connections and BufferedReader to read data line by line
- 行为差异: Different purpose: A updates QD info, B checks for upgrades；A reads from a file or URL, B reads from a license server URL；A parses lines starting with 'pg' and 'pt', B parses XML-like response with </ROW> and </FLD>；A updates internal data structures, B updates database and UI components
- 修正建议: Use dataflow-aware models like GraphCodeBERT or code property graphs；Incorporate method-level call graphs to capture functional context；Add contrastive learning to distinguish pairs with similar APIs but different semantics

### case_id=2803 FN partial_functionality

- 方法: `doTransfer` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request to a specified URL, copying headers and streaming the request and response bodies.
- B 摘要: Opens a fixed URL, reads its content into a string buffer, and logs it.
- 静态失败原因: Low token Jaccard similarity (0.126) and different method names, combined with distinct structural patterns (servlet vs standalone), caused the model to miss the shared URL-reading behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions perform a URL connection and read data, which aligns with Type-4 clone detection that considers high-level functional similarity despite different contexts.
- 共享行为: Both open a URL connection and read input from it
- 行为差异: Function A is a servlet proxy that forwards requests and handles headers, while B is a simple standalone URL reader；A writes response back to the client, B only logs the content；A uses dynamic URL from request parameter, B uses hardcoded URL
- 修正建议: Incorporate data flow analysis to identify common operations like URL.openConnection and read；Use graph-based models that capture partial functional similarity；Augment training with examples of broad functional clones with low lexical overlap

### case_id=2804 FN partial_functionality

- 方法: `main` vs `patch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts all entries to the current directory.
- B 摘要: Backs up the Minecraft jar file by copying it to a backup path, then opens the original jar as a JarFile.
- 静态失败原因: The low token Jaccard similarity (0.09589) and different method names, control flow, and API usage make it hard for static models relying on surface-level features to detect semantic similarity. The functions share only a high-level 'archive I/O' concept that is not captured by token overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled these as clones due to both functions handling compressed archives (zip/jar) and performing file copy/write operations, which may be considered a broad Type-4 semantic clone under the BCB annotation scheme.
- 共享行为: Both involve file I/O operations on compressed archives (zip/jar).
- 行为差异: Code A extracts multiple entries from a zip; Code B copies the entire jar file and then opens it without extraction.；Code A uses a URL to fetch the file; Code B operates on local paths.；Code A is a static main method; Code B is an instance method with an early return condition.；Code A writes each entry to a separate file; Code B writes a single backup file and reads the original.
- 修正建议: Enhance training data with more diverse I/O operations on archives to learn common patterns.；Incorporate data flow analysis to detect structural similarities in stream handling.；Use code summarization or docstring embeddings to capture semantic intent.

### case_id=2805 FP boilerplate_overlap

- 方法: `doVersionCheck` vs `readZoneIDs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Connects to a URL for version checking, reads lines to extract version and build, compares with current build, and displays appropriate UI messages.
- B 摘要: Reads integer IDs from a resource file line by line, parses them, and returns a HashSet of zone IDs.
- 静态失败原因: The static BERT model likely over-weighted the common I/O pattern (URL, openStream, readLine loop, catch) and ignored the distinct parsing and output logic, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the core functionality (version checking vs. ID parsing) is entirely different, despite shared I/O boilerplate.
- 共享行为: Both open a URL/Resource and read lines in a loop using readLine()；Both handle exceptions with catch blocks
- 行为差异: A performs version comparison and UI updates; B parses integers and returns a set；A uses BufferedReader, B uses LineNumberReader；A's input is a View, B's input is a resource filename；A has UI interactions (cursor, messages); B has none
- 修正建议: Enhance training with examples that distinguish between shared boilerplate and actual semantic intent；Incorporate dataflow or control flow analysis to capture differences after the read loop；Use fine-grained token-level attention to differentiate key operations vs. common I/O

### case_id=2806 FP lexical_or_api_overlap

- 方法: `addQDInformation` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads QD information from a local file or a remote URL, parsing lines starting with 'pg' and 'pt' to update internal project data.
- B 摘要: Executes an HTTP POST request to a target URL with parameters and returns the response string.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by the lexical overlap in API calls (URL, InputStream, BufferedReader, try-catch) and the presence of similar I/O patterns. Without understanding the overall method intent or data flow, the model may have classified them as clones due to these surface similarities.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the methods have distinct functionalities: one is a data-loading method with specific parsing logic, the other is a generic HTTP client method. Despite overlapping API usage, they serve different purposes and are not functionally equivalent or structurally similar beyond common boilerplate.
- 共享行为: Both use BufferedReader to read from an InputStream.；Both have try-catch blocks for exception handling.；Both involve I/O operations (file or network).；Both use URL and InputStream/Reader classes.
- 行为差异: A reads a specific data format (qdinfo.dat) to update internal state; B sends a generic HTTP POST and returns a response.；A has conditional logic for local vs remote; B always does a remote POST.；A parses lines with specific prefixes ('pg', 'pt'); B just reads all lines into a string.；A returns void; B returns a String or null on failure.
- 修正建议: Include method-level context such as method name and class hierarchy to better capture intent.；Use data flow analysis to differentiate between input and output operations.；Train on more diverse examples of network vs file I/O to reduce bias.；Incorporate control flow and data dependency features beyond token overlap.

### case_id=2807 FN benchmark_preference_bias

- 方法: `getEncoding` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Extracts character encoding from HTTP response headers and body of a URL connection.
- B 摘要: Opens a file or URL stream and reads into an internal buffer, returning status.
- 静态失败原因: The model likely correctly identified semantic difference (encoding extraction vs. stream reading), but BCB's annotation may be biased towards general IO functionality overlap.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them clones based on broad IO operations involving URL connections and stream reading, but the semantic goals differ significantly.
- 共享行为: Both involve opening a URL connection and reading from an input stream.
- 行为差异: A specifically searches for charset/encoding information; B reads raw stream.；A returns a String encoding; B returns an int status.；A uses BufferedReader and reads lines; B uses BufferedInputStream and delegates to another read method.；B has fallback to FileInputStream; A only handles URL.
- 修正建议: Re-evaluate BCB label for this pair to ensure consistent semantic similarity guidelines.；Improve model with contrastive learning that emphasizes functional semantics over high-level IO patterns.

### case_id=2808 FN benchmark_preference_bias

- 方法: `copyIconFiles` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies 16x16 and 32x32 icon files from annotation paths to a resource directory.
- B 摘要: Builds an editable version of a web site by reading XML, transforming pages, and writing output files.
- 静态失败原因: The static model correctly predicted non-clone based on low token overlap and semantic mismatch. The model's failure relative to BCB is due to the benchmark's potentially erroneous label, not a model deficiency.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to the common presence of file copy operations and exception handling, despite the vast difference in overall functionality. This likely reflects an over-broad interpretation of Type-3/Type-4 similarity.
- 共享行为: Both perform file I/O operations (reading and writing files).；Both handle potential exceptions with try-catch blocks.
- 行为差异: A only copies icon files; B generates entire web pages.；A uses FileChannel for efficient copying; B uses FileInputStream and FileWriter.；A is deterministic based on annotations; B involves complex transformations and loops.；B has many more parameters and dependencies.
- 修正建议: Review and correct BCB annotations for this pair.；Train models on more consistently annotated data to avoid such outliers.

### case_id=2809 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads zone IDs from a resource file and returns a set of integers.
- B 摘要: Executes an HTTP GET request with basic authentication, reads the response line by line, and stores the result along with last interaction timestamp.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized lexical and API overlap: both use BufferedReader, InputStreamReader, readLine, and try-catch. The model may have missed the semantic difference in the overall goal due to focusing on common I/O patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the functions perform completely different tasks (file parsing vs HTTP request). The only overlap is the generic line-reading boilerplate, which is insufficient for clone labeling.
- 共享行为: Both read input line by line using a BufferedReader/InputStreamReader pattern；Both have try-catch exception handling
- 行为差异: Function A reads from a local resource file, while B makes an HTTP request to a remote server；Function A parses each line as an integer and adds to a set, B concatenates lines into a string buffer；Function A returns a HashSet, B sets instance variables and a finish flag
- 修正建议: Incorporate method-level context like method name and class structure；Use control-flow and data-flow features to capture distinct operations (e.g., URL construction vs resource loading)；Add attention to output types and invocation patterns (returning set vs setting fields)

### case_id=2810 FN partial_functionality

- 方法: `getFile` vs `loadDefaultSettings`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint address, and saves it to a temporary location, returning the file path.
- B 摘要: Copies a default configuration file from the classpath to a specified file.
- 静态失败原因: Low token overlap (0.086) and different method signatures (return type) indicate static models rely on lexical similarity, missing the high-level semantic commonality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions perform the high-level task of 'loading a file from a source' and writing to disk, a common utility pattern, despite differences in source and transformations.
- 共享行为: Both copy a resource to a local file；Both handle I/O exceptions
- 行为差异: A downloads from network and modifies XML content; B copies from classpath without modification；A returns a file path; B returns void；A uses NIO channels and detailed error handling; B uses Apache IOUtils and simple try-catch-finally
- 修正建议: Incorporate high-level task classification；Use IR-based features or program slicing；Leverage method names and comments for semantic clues

### case_id=2811 FN partial_functionality

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using stream I/O.
- B 摘要: Copies a source file to a destination file using NIO FileChannel.
- 静态失败原因: The static model likely focused on token-level differences such as 'FileChannel', 'transferFrom', 'URL', etc., and the dissimilar method signatures and control flow, leading to a low similarity score. It may not have recognized the semantic equivalence of the copy operation.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as Type-3/4 clones because they perform the same high-level operation of copying a source to a file, despite differences in source type (URL vs file) and I/O mechanism (stream vs NIO). The labeling reflects functional similarity in intent.
- 共享行为: Both copy a source (file or resource) to a destination file.；Both read from source and write to destination.；Both close resources after copying.
- 行为差异: Function A can read from a URL, while B only handles files.；Function A uses byte-by-byte streaming, B uses NIO channels with transferFrom.；Function A throws Exception generically, B throws IOException specifically and handles close exceptions differently.；Function A names destination via destinationFile() (not shown), B computes destination from path and source filename.
- 修正建议: Train model on more diverse examples of 'copy' operations to recognize different I/O patterns.；Incorporate functional similarity measures that abstract away API details.；Use code transformation techniques to normalize different copy implementations.；Add data-level augmentation with semantically equivalent but syntactically different code pairs.

### case_id=2812 FP lexical_or_api_overlap

- 方法: `downloadURLtoString` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a URL's content and returns it as a string.
- B 摘要: Downloads a URL with optional authentication, writes content to a temporary file, and updates a status label during download.
- 静态失败原因: The model likely overemphasized lexical and API similarities (URL, BufferedReader, readLine) and ignored differences in output, side effects, and authentication logic, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires significant functional overlap; here the core purpose differs (return string vs save to file with authentication and UI), so BCB would likely label as non-clone.
- 共享行为: Open a URL connection；Read lines from the input stream using BufferedReader；Process line-by-line reading loop
- 行为差异: downloadURLtoString returns the entire content as a string; loadURL writes to a temporary file and does not return content；loadURL supports HTTP Basic Authentication; downloadURLtoString does not；loadURL updates a JLabel with download progress and prints to System.out; downloadURLtoString has no such side effects；loadURL creates a temporary file and writes each line; downloadURLtoString appends to a StringBuffer
- 修正建议: Incorporate dataflow analysis to distinguish output vs side-effect behaviors；Use method-level semantic embeddings that capture return type and method signature；Train on examples with varying I/O patterns to reduce over-reliance on common APIs

### case_id=2813 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `get`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a Twitter feed from a fixed URL using Apache HttpClient and returns the raw JSON string.
- B 摘要: Sends a GET request with custom headers to a given URL using HttpURLConnection and returns an array of GameRecord objects parsed from filtered response lines.
- 静态失败原因: The static model likely over-relied on lexical and structural similarities, such as the common boilerplate of try-catch, BufferedReader, while loop, and HTTP request setup, missing the key semantic differences in return type and data transformation.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have different core functionality: one returns raw text, the other parses structured objects. The only commonality is the HTTP GET pattern, which is too generic for a clone.
- 共享行为: Perform HTTP GET request；Read response line by line；Check for HTTP 200 status；Catch IOException
- 行为差异: Different HTTP library (HttpClient vs HttpURLConnection)；Different input parameters (none vs url, lat, lon, count)；Different URL source (hardcoded vs parameter)；Different response processing (append all lines vs filter and decode)
- 修正建议: Incorporate data-flow analysis to track how the response is used and return types.；Enhance model with type information or output specification.；Use contrastive learning to distinguish similar boilerplate with different semantics.

### case_id=2814 FP lexical_or_api_overlap

- 方法: `importRoles` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses an XML stream containing RoleName elements from a URL and returns a list of RoleName objects.
- B 摘要: Parses a text stream containing sequence names and sequences from a URL and populates internal lists.
- 静态失败原因: The static model likely relied on lexical overlap (common API usage like URL, BufferedReader, similar exception handling) and structural patterns, ignoring the semantic differences in parsing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because the core functionality differs: importing roles vs. importing sequences. The structural similarity is incidental and not sufficient for clone annotation.
- 共享行为: Both read from a URL using InputStream/Reader；Both loop over input lines and accumulate data into lists；Both handle MalformedURLException, IOException, and other exceptions；Both use StringBuffer to build strings
- 行为差异: Different parsing logic: XML tag-based vs tokenizer/sequence reading；Different output types: ArrayList<RoleName> vs two ArrayList<String>；Different method signatures: static with URL parameter vs non-static without parameters
- 修正建议: Incorporate data flow analysis to differentiate parsing contexts；Use method name and return type information to disambiguate；Train on more diverse examples to reduce sensitivity to boilerplate patterns

### case_id=2815 FN partial_functionality

- 方法: `downloadURLtoString` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads content from a URL and returns it as a string.
- B 摘要: Parses a geospatial XML record by constructing a request URL, downloading the response, and extracting place names with IDs, with retries.
- 静态失败原因: Static models like GraphCodeBERT rely heavily on token-level and structural similarities. The token Jaccard is very low (0.109), indicating low lexical overlap. The model may have focused on the significant differences in input/output types and extra logic (e.g., XML parsing, retries) and missed the shared URL-reading pattern because it is a small fraction of the longer function B. The model might not recognize the common subroutine if it is not highlighted by attention or if the overall semantics differ.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled them as clones due to the identical code pattern of reading a URL line by line using BufferedReader, which is a common reusable routine. Even though the overall functions differ, the presence of this shared subroutine could be considered partial functionality similarity under a broad Type-3/Type-4 interpretation.
- 共享行为: Both open a URL stream and read lines into a StringBuffer.；Both use BufferedReader and InputStreamReader to read from a URL.
- 行为差异: Function A is a generic utility; function B involves complex XML construction and parsing.；Function A returns the raw string; function B parses the XML and returns a collection of tuples.；Function B includes conditional testing mode, retry logic, and error handling; function A just throws IOException.
- 修正建议: Train the model with more examples of partial functionality clones, where one function contains a subset of another's behavior.；Use data-flow analysis to identify shared subroutines even if they are embedded in larger functions.；Enhance representation with patterns of common API usage sequences.

### case_id=2816 FP long_range_semantics

- 方法: `perform` vs `encrypt`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: A web action method that processes a request for classifying a concept, involving session attributes, building XML data, making an HTTP POST, and parsing the result.
- B 摘要: A utility method that encrypts a password using SHA-1 and Base64 encoding.
- 静态失败原因: Static models may have been misled by common API patterns (try-catch, string conversion) and the truncation of function A due to length, causing loss of overall semantic context.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels non-clone because the functions have no functional similarity and low syntactic overlap; they belong to different domains.
- 共享行为: Both involve handling of strings and exceptions.
- 行为差异: A handles HTTP requests and sessions; B has no web context.；A builds and sends XML; B hashes and encodes a password.；A has complex control flow with multiple branches; B is simple.；A uses various custom classes; B uses standard Java crypto and Base64.
- 修正建议: Ensure full function input without truncation; use sliding window or chunking.；Improve training to distinguish between web action and utility functions.

### case_id=2817 FP lexical_or_api_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A main method that parses a Prolog file, generates adapter classes, and writes a jar.
- B 摘要: A method that copies a file using FileChannel.
- 静态失败原因: Probably because both use common Java I/O classes (File, InputStream, OutputStream), leading the model to overestimate similarity based on API usage.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because functions have no semantic or structural similarity, even under broad Type-4 partial functionality.
- 共享行为: Both interact with files and use file I/O APIs
- 行为差异: Different purposes: adapter generation vs file copy；Different complexity: many steps vs simple transfer；Different error handling: multiple checks vs single throws IOException
- 修正建议: Train on more discriminating features like control flow and data dependencies；Use contrastive learning to distinguish different tasks with similar APIs

### case_id=2818 FN benchmark_preference_bias

- 方法: `doGet` vs `addFileToTarGz`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests to retrieve and serve a portal page, with caching and error handling.
- B 摘要: Recursively adds files to a tar.gz archive using TarArchiveOutputStream.
- 静态失败原因: Static BERT correctly predicted non-clone; from BCB perspective, it failed because BCB label is likely incorrect. The low token overlap and different method signatures made BERT predict non-clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Probably an annotation error; BCB might have considered both as 'file handling' or 'utility' functions, but the semantics are entirely different.
- 共享行为: Both involve file I/O operations (reading/writing files) but in entirely different contexts.
- 行为差异: Function A processes HTTP requests and responses, while B only deals with file archiving.；Function A has complex logic for page access control and caching, B is purely additive and recursive.；Function A interacts with a web server and user sessions, B has no web or user interaction.
- 修正建议: Re-evaluate the BCB annotation for this pair; consider removing or correcting the label.

### case_id=2819 FN benchmark_preference_bias

- 方法: `copy` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file using FileChannel transfer.
- B 摘要: Launches a NexOpen project in Eclipse, handling Maven POMs, Hibernate dialect, and reverse engineering files.
- 静态失败原因: The model correctly predicted non-clone (0) due to low lexical overlap and different semantics; the error is in the BCB label, not the prediction.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Likely a false positive in BCB, possibly due to both containing file resource handling, but the overall functionality is completely different.
- 共享行为: Both perform file I/O operations；Both handle exceptions
- 行为差异: Simple file copy vs. complex Eclipse launch configuration；Different domains (file I/O vs. IDE configuration)；Different APIs and control flow
- 修正建议: Consider the BCB label as potentially incorrect for this pair；The model prediction is actually correct; no fix needed for the model

### case_id=2820 FP lexical_or_api_overlap

- 方法: `readUNI` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads tab-separated lines from a URL and populates a vector with concatenated id and description.
- B 摘要: Reads an OSGi service file from classpath to instantiate and return a FrameworkFactory instance.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-emphasized the lexical overlap of URL opening, line reading, and stream closing patterns while ignoring the completely different purpose and output behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these not clones because the overall functionality (populating descriptions vs. loading OSGI factory) is entirely different despite similar reading boilerplate.
- 共享行为: Both open a URL/stream and read lines；Both use try-finally to close the stream；Both process text lines from a resource
- 行为差异: A parses tab-separated fields; B skips comments and loads a class；A populates an externally provided vector; B returns an instance of FrameworkFactory；A silently catches exceptions; B throws Exception if resource not found；A uses Scanner; B uses BufferedReader
- 修正建议: Incorporate data-flow or control-flow analysis to distinguish variable usage after reading；Add cross-function context or API call semantics to differentiate factory instantiation from data collection；Use contrastive learning on negative pairs with high lexical overlap but different semantics

### case_id=2821 FP lexical_or_api_overlap

- 方法: `run` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a tile from a URL or file, parses it into geometric features, and adds them to a data layer.
- B 摘要: Fetches a version check file from a URL, parses build numbers, and triggers a version check dialog.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-relied on lexical overlap (e.g., URL, BufferedReader, readLine) and ignored the distinct semantic goals and data transformations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functional similarity; these functions serve entirely different purposes despite a common I/O pattern, so they are not considered clones.
- 共享行为: Both open a URL stream and read lines using BufferedReader
- 行为差异: Different input URL and data format: tile data vs version properties；Different parsing: concatenates all lines vs extracting specific prefixed lines；Different output: adds features to data source vs calls version check method
- 修正建议: Train with more diverse negative examples that share API usage but differ in intent；Incorporate dataflow analysis to capture differences in variable dependencies and output

### case_id=2822 FN partial_functionality

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to display a portal page, with caching to a file for non-editable pages.
- B 摘要: Copies a file using buffered input/output streams.
- 静态失败原因: The static model likely correctly identified non-clone due to low token overlap (0.07) and different API usage (HTTP vs file I/O), but may have missed the subtle file I/O commonality that BCB considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to partial overlap in file writing functionality (the caching part in A resembles a file copy), but the overall semantics are vastly different.
- 共享行为: Both involve file I/O operations (reading/writing files) in some part of the code.
- 行为差异: Function A is an HTTP servlet handler; Function B is a utility for file copying.；Function A deals with HTTP request/response, user permissions, and page rendering; Function B only copies file content.；Function A writes to a file as a cache, but only in a specific conditional branch; Function B's entire purpose is file copying.；Error handling and logging differ significantly.
- 修正建议: Improve detection of partial functional similarity, e.g., by decomposing functions into sub-operations.；Use dataflow analysis to identify common I/O patterns even in small code fragments.

### case_id=2823 FN partial_functionality

- 方法: `createJAR` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Creates a JAR file by copying a resource JAR and serializing a document object into it.
- B 摘要: Retrieves a resource via URL, caches it locally, and returns an InputStream to the cached file.
- 静态失败原因: The static model relied on low token overlap (Jaccard 0.1667) and failed to recognize the abstract structural similarity in I/O handling that BCB considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as Type-4 clones because both perform file I/O with error handling, using similar Java I/O classes and patterns, even though the specific tasks differ.
- 共享行为: Both involve file I/O operations with streams；Both use exception handling with try-catch；Both create and manipulate File objects
- 行为差异: A creates a JAR and serializes objects; B downloads and caches resources；A uses ObjectOutputStream; B uses BufferedInputStream/OutputStream；A writes to file; B returns an InputStream
- 修正建议: Incorporate structural features like control flow and data flow；Use code summarization to capture high-level semantics；Train on more diverse I/O examples to recognize patterns

### case_id=2824 FN partial_functionality

- 方法: `readPage` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a web page from a URL, optionally skipping lines starting with '#', and returns the concatenated HTML string.
- B 摘要: Invokes a remote method via HTTP POST, reads the response stream line by line, builds a string, optionally deserializes JSON, and retries on timeout.
- 静态失败原因: The static model likely focused on different method signatures, parameters, and control flow, and the token Jaccard similarity is low (0.167), so the common I/O pattern was too small relative to the whole function to influence the prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the common line-reading pattern as a significant sub-function, classifying as Type-3 or Type-4 clone despite different overall contexts.
- 共享行为: Both read lines from an input stream using BufferedReader and append them to a string buffer.
- 行为差异: A ignores comments; B does not.；A only reads; B also deserializes JSON and handles retry.；A uses URL directly; B constructs URL from service.；A returns raw HTML; B returns an object (or null).
- 修正建议: Use dataflow-based models to detect common sub-patterns like stream reading and string building.；Apply local similarity weighting to highlight shared I/O operations.

### case_id=2825 FP boilerplate_overlap

- 方法: `readAndRewrite` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads a DICOM file, parses metadata and pixel data, and writes the dataset to a new file.
- B 摘要: Reads a configuration file, tokenizes strings, populates multiple sets and hash maps for linguistic data processing.
- 静态失败原因: The model may have been misled by superficial similarities such as file I/O, while loops, and string tokenization, while missing the overall semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions are from entirely different domains with no meaningful functional overlap beyond basic I/O.
- 共享行为: Both involve reading from a file；Both use loops to process data；Both involve string parsing
- 行为差异: Completely different domain: DICOM image processing vs. linguistic configuration parsing；Different libraries: DcmParser, ImageIO vs. StringTokenizer, custom data structures；Different output: writes a DICOM file vs. populates hash maps and sets；Different error handling: throws IOException vs. prints error and continues
- 修正建议: Incorporate domain-specific API usage patterns into the model；Use data flow analysis to capture the actual purpose of functions；Train on more diverse examples to reduce reliance on boilerplate similarities

### case_id=2826 FN partial_functionality

- 方法: `copyFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using FileChannel transfer.
- B 摘要: Retrieves a resource (possibly remote) by caching it locally and returning a FileInputStream of the cached file.
- 静态失败原因: Low token overlap and different syntactic structures; the model lacks understanding of high-level functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may classify them as clones because both are file-related operations that involve reading and writing data, despite different levels of abstraction and additional functionality in B.
- 共享行为: Both involve reading from an input source and writing to an output destination
- 行为差异: copyFile transfers directly between files using NIO channels; getResourceAsStream handles URL fetching, caching logic, HTTP connections, and returns an InputStream
- 修正建议: Use models that capture high-level semantic intent；Incorporate data flow and control flow analysis；Leverage code summarization or comment matching

### case_id=2827 FN benchmark_preference_bias

- 方法: `doTransfer` vs `getWebByUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request to a target URL, copying headers and body, and returns the response.
- B 摘要: Downloads a web page from a URL and saves it to a file, recursively processing links.
- 静态失败原因: The static model correctly predicted non-clone (0) indicating it did not fail; the BCB label is 1, so the model disagreed with BCB's broader annotation preference.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them clones due to the common 'URL fetch and output' pattern, despite functional differences, aligning with Type-4/partial functionality similarity.
- 共享行为: Both open a URL connection and read from an input stream.；Both write to an output stream (response or file).
- 行为差异: A uses HttpURLConnection with full request handling; B uses URLConnection and reads line-by-line.；A writes to servlet response; B writes to file.；A handles HTTP method and headers; B does not.；B includes recursive link extraction and reporting; A does not.
- 修正建议: Train model to recognize broader clone types if aligning with BCB annotations.；Alternatively, use a more nuanced multi-label classification for different clone types.

### case_id=2828 FN partial_functionality

- 方法: `main` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its contents to the current directory.
- B 摘要: Copies a file from a source to a destination with validation of existence, permissions, and directory structure.
- 静态失败原因: Static BERT may rely on token similarity and API overlap; the low Jaccard (0.23) and different method names/structures likely caused a false non-clone prediction, missing the underlying I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-4 clones based on a common dataflow pattern (stream copy) even if contexts differ, and considers partial functionality similarity acceptable.
- 共享行为: Reads bytes from an input stream and writes to an output stream using a buffer；Closes streams in a finally block
- 行为差异: A uses URL connection and zip entries; B uses local file paths and validates source/destination；A lacks error checking; B has extensive validation for file existence and permissions；A extracts multiple files; B copies exactly one file
- 修正建议: Use dataflow analysis to capture the core stream copy pattern；Include control flow abstraction to generalize over validation branches；Incorporate structural similarity of I/O loops across methods

### case_id=2829 FP lexical_or_api_overlap

- 方法: `callService` vs `getUser`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads from a URL, builds a string from all lines, stores in field, handles exceptions.
- B 摘要: Reads from a config file to find a user by login, creates user object if found, saves to DAO, returns user.
- 静态失败原因: The static model likely focused on common API calls (URL, BufferedReader, InputStreamReader, while loop) and ignored the surrounding context and different semantics, overfitting to lexical overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the methods have distinct purposes: one is a generic service call, the other is user retrieval with fallback. The shared I/O pattern is overshadowed by different business logic.
- 共享行为: Both open a URL resource and read lines in a while loop using BufferedReader.
- 行为差异: Method A builds a string from all lines and stores in a field; Method B tokenizes each line, checks condition, creates User, and saves it.；Error handling differs (specific exceptions vs generic).；Return type and side effects differ (void vs User).
- 修正建议: Improve training to consider high-level intent.；Add contrastive learning on similar API usage with different semantics.；Incorporate dataflow analysis.

### case_id=2830 FP lexical_or_api_overlap

- 方法: `run` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads GeoJSON tile data from a URL, parses geometries, and adds them to the data source.
- B 摘要: Downloads YouTube page, extracts video_id, t, title parameters from fullscreenUrl, and constructs a video download URL.
- 静态失败原因: Static BERT models rely heavily on token and structural overlap. Both functions contain URL, BufferedReader, while(readLine), and try-catch blocks, leading to high representation similarity despite divergent semantics. The model could not distinguish between different higher-level intents.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these non-clones because they perform distinct domain-specific tasks (tile loading vs. YouTube URL extraction) despite sharing common I/O patterns. The annotation emphasizes functional purpose over boilerplate API usage.
- 共享行为: Open HTTP connection；Read lines using BufferedReader；Catch exceptions (IOException, MalformedURLException, etc.)；Use URL class
- 行为差异: Function A processes tile geometries; function B parses YouTube-specific query parameters.；Function A uses synchronized blocks and a request tracking list; function B does not.；Function A outputs to data source; function B returns a constructed URL string.；Function A handles file protocol; function B only HTTP.
- 修正建议: Incorporate dataflow analysis or program dependence graphs to capture actual computation path differences.；Use instruction-level semantic embeddings that abstract away common library calls.；Train with more negative examples that share API usage but differ in purpose.

### case_id=2831 FP boilerplate_overlap

- 方法: `run` vs `readURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a tile from a URL, parses GeoJSON, builds geometries, and adds to a data source with concurrency control.
- B 摘要: Opens a URL, reads lines, and prints them to standard output.
- 静态失败原因: The model likely focused on the common I/O boilerplate (URL opening, BufferedReader) and missed the vastly different post-processing and output behavior, possibly due to limited context understanding or over-reliance on token patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions differ significantly in purpose and output, even if they share some I/O boilerplate.
- 共享行为: Both open a URL and read lines from it using BufferedReader.
- 行为差异: A has concurrency control (synchronized) and handles multiple protocols; B does not.；A parses GeoJSON and creates geometry collections; B only prints lines.；A writes to a data source and cache; B has no output beyond printing.；A has complex error handling for different protocols; B catches all exceptions generically.
- 修正建议: Improve training to emphasize overall function purpose beyond boilerplate.；Incorporate dataflow analysis to track how read data is used.

### case_id=2832 FN partial_functionality

- 方法: `fileDownload` vs `getWebByUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads content from a given URL to a PDF file in a destination directory.
- B 摘要: Fetches web content from a URL and saves it as an HTML file, with additional logging and recursive URL extraction.
- 静态失败原因: Low token Jaccard similarity (0.2268) and syntactic differences in control flow (while loops, print statements) distract the static BERT model, which lacks dataflow awareness to capture the core download-and-save pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as clones because both functions fundamentally perform the same task of downloading URL content to a file, which is a common pattern, and the differences are in peripheral concerns like logging and recursion.
- 共享行为: Both open a URL connection and read input stream；Both write the read content to a local file
- 行为差异: fileDownload writes to a fixed 'download.pdf' file, while getWebByUrl writes to a dynamically named HTML file；getWebByUrl includes logging, recursive crawling, and uses PrintWriter differently；Different method signatures and parameters
- 修正建议: Use dataflow analysis or program dependence graphs to identify core I/O operations；Focus on the essential sequence: open URL -> read -> write to file, ignoring extra features；Train models to recognize semantic similarity despite syntactic variations

### case_id=2833 FN partial_functionality

- 方法: `copyFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to target using NIO FileChannel transferTo.
- B 摘要: Retrieves a resource via URL, caches it locally, and returns an InputStream.
- 静态失败原因: Static BERT/GraphCodeBERT relies on token overlap and structural similarity, which are low in this pair, causing it to miss the partial I/O similarity that BCB considers.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider any pair that contains a file copy operation as functionally similar, even if the overall tasks differ, leading to a Type-4 clone label.
- 共享行为: Both involve reading from a source and writing to a destination file
- 行为差异: copyFile is a simple local file copy; getResourceAsStream handles network, HTTP, caching, and returns a stream；copyFile uses transferTo; getResourceAsStream uses buffered byte-by-byte copy；copyFile has no error handling beyond throwing IOException; getResourceAsStream has extensive exception handling and logging
- 修正建议: Incorporate dataflow analysis to detect shared I/O patterns；Use cross-function attention to capture partial functionality；Fine-tune on BCB-style annotations that emphasize broad semantic similarity

### case_id=2834 FP boilerplate_overlap

- 方法: `run` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs an authenticated GET request to a URL and reads the entire response body into a string.
- B 摘要: Fetches a YouTube page, parses HTML to extract video_id and t parameters, and constructs a full video URL.
- 静态失败原因: The static model overemphasized the boilerplate code such as URL opening, BufferedReader usage, and while-reading lines, while ignoring the divergent core logic and different high-level goals.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically annotates similar functional behavior; these two functions have very different outputs and purposes (authentication vs. video URL extraction), so they are unlikely to be considered clones even under broad Type-4 criteria.
- 共享行为: Both open an HTTP(S) connection and read response data line by line.；Both use BufferedReader and InputStreamReader to read the response.；Both handle exceptions via try-catch.
- 行为差异: Function A includes HTTP basic authentication; function B does not.；Function B parses the response looking for a specific substring (fullscreenUrl) and then splits to extract parameters; function A simply appends all lines to a response buffer.；Function B updates UI components (progress bar) and prints debug output; function A updates a timestamp and sets a finish flag.；Function A stores the entire response as a string and sets a finish flag; function B returns a constructed URL and stores video title separately.
- 修正建议: Train on a dataset where boilerplate code is weighted less or use functional signature embeddings.；Incorporate data flow analysis to distinguish between different use of the read data.；Use finer-grained structural matching that captures the semantic intent beyond common API patterns.

### case_id=2835 FP partial_functionality

- 方法: `setBundleInfoName` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses a key-value file from a URL to update bundle names in a list.
- B 摘要: Imports sequence data from a URL and stores names and sequences in lists.
- 静态失败原因: The model may have over-relied on common API calls (openStream, readLine, try-catch) and loop patterns, missing the fundamental difference in data processing and purpose.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels as non-clone because the core functionality is unrelated despite superficial structural similarities.
- 共享行为: Read from a URL；Handle IOException；Use loops
- 行为差异: Different data format processed: key-value vs. sequence；Different output: modifies existing list vs. populates new lists；Different parsing logic: simple line split vs. ImportHelper；Different control structure: while loop vs. do-while
- 修正建议: Incorporate semantic role labeling to distinguish data processing stages；Use data flow analysis to track how inputs are transformed；Include method name and context more explicitly in the representation

### case_id=2836 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens a URL, reads the HTML page, extracts all hyperlinks and their text using regex, and returns them as a pair of vectors.
- B 摘要: Opens a version check URL, reads lines, parses build version, and displays a message or error to the user.
- 静态失败原因: The static BERT model likely overfitted to the lexical overlap of URL, BufferedReader, readLine, and the while-read loop pattern, missing the diverging semantics of what is extracted and how.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label these as non-clones because the high-level purpose and output differ significantly: one is a generic link extractor, the other is a version checker with UI feedback. The shared URI-reading boilerplate is insufficient for Type-3/4 similarity.
- 共享行为: Both open a URL connection and read lines using BufferedReader；Both parse each line to extract specific information
- 行为差异: Function A returns extracted links and texts; Function B is void and interacts with UI (View, GUIUtilities)；Function A uses regex to parse HTML anchor tags; Function B uses simple prefix matching (.version, .build)；Function A has no error handling; Function B catches IOException and shows error dialog
- 修正建议: Incorporate method name and comment embeddings to capture intent；Use dataflow or control-flow graphs to highlight different variable usage；Train on more diverse negative examples with similar API usage but different goals

### case_id=2837 FN benchmark_preference_bias

- 方法: `copyTextFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.1`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using buffered I/O streams, returning true on success or false on exception.
- B 摘要: Launches a complex Eclipse RCP configuration process involving XML file checking, property setting, and project installation with file copying.
- 静态失败原因: The static BERT model correctly identified them as non-clones, but BCB's label of 1 is a false positive in strict semantics. The model failed to match BCB's broader preference, possibly due to lexical disparity (low Jaccard) and different APIs.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both functions involving file I/O and stream copying, which aligns with a broad Type-3/Type-4 view of partial functionality similarity in file handling.
- 共享行为: Both perform file I/O operations (reading and writing files)
- 行为差异: Function A is a simple file copy with no external dependencies; Function B is a multi-step launch workflow involving XML parsing, property manipulation, and project management.；Function A returns a boolean indicating success; Function B void and throws CoreException.；Function B modifies project resources and uses Eclipse-specific APIs; Function A is a utility method.
- 修正建议: Verify BCB annotation for this pair; if incorrect, correct the label to non-clone.；If BCB intends partial functionality clones, refine guidelines to avoid over-broad matching.

### case_id=2838 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests to retrieve and display a portal page, with permission checks, logging, and optional caching of rendered output to a file.
- B 摘要: Copies a source file to a destination directory using FileChannel transfer.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed because the two functions have very low lexical overlap (token_jaccard=0.069) but share boilerplate patterns (try-catch, file I/O) that could cause false positives in some models. However, here it correctly predicted non-clone (0), which aligns with strict semantics but conflicts with BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to broad acceptance of Type-4 (similar functionality in different contexts) or because both involve file operations and resource cleanup, or due to an annotation error.
- 共享行为: Both involve file I/O operations (writing or copying files)；Both use try-finally blocks to ensure resource cleanup
- 行为差异: Function A is a web servlet handler processing HTTP requests; Function B is a utility for file copying.；Function A checks user permissions, logs, and handles page not found errors; Function B has no such logic.；Function A writes to a temp file based on complex conditions; Function B copies a file from a given path.；Function A uses HttpServletRequest/Response; Function B uses FileInputStream/FileOutputStream and FileChannel.
- 修正建议: Ensure training data for clone detection emphasizes semantic equivalence rather than partial functional overlap.；Use more robust dataflow or program dependence analysis to distinguish core functionality from boilerplate.

### case_id=2839 FN benchmark_preference_bias

- 方法: `readAndRewrite` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a DICOM file, parses headers and pixel data, then writes out the dataset and pixel data to another file.
- B 摘要: Processes a set of pages: reads XML, applies XSLT transformations, replaces strings, and writes resulting HTML files to an output directory.
- 静态失败原因: Static model correctly predicted non-clone due to very low lexical overlap and vastly different API usage; it was not misled by superficial similarities.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to a broad interpretation of Type-4 (functional similarity) where both are seen as 'file transformation' routines, despite differing domains and implementation details.
- 共享行为: Both perform file input and output operations.；Both involve reading a source, processing data, and writing results.
- 行为差异: Different data formats: DICOM medical images vs. XML/HTML web content.；Different processing: pixel data reading and writing vs. XSLT transformation and string replacement.；Different libraries and APIs used (e.g., DcmParser vs. Transformer).；Different output structure: single output file vs. multiple output files per page.
- 修正建议: Review BCB annotation guidelines to ensure consistency in labeling broad Type-4 clones.；Consider using domain-specific semantics or program flow analysis to refine clone detection.

### case_id=2840 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads integers from a file resource and returns them as a HashSet.
- B 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- 静态失败原因: The model may have been misled by overlapping API calls like URL, openStream, LineNumberReader, and the try-catch pattern, ignoring the core logic differences in I/O direction and return type.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions have completely different purposes and output types, despite some superficial API overlap. BCB emphasizes semantic equivalence.
- 共享行为: Both use URL and URLConnection/InputStream openStream；Both use BufferedReader or LineNumberReader to read lines；Both have try-catch for exception handling
- 行为差异: One reads from a local resource file, the other makes an HTTP POST request；One returns a collection of integers, the other returns a response string；One uses LineNumberReader, the other uses BufferedReader and DataOutputStream for writing；executePost has connection management and output writing; readZoneIDs does not
- 修正建议: Improve the model's ability to distinguish broader functional context beyond local API usage；Add more discriminative features like method return type and I/O direction (read vs write)；Train on more diverse non-clone pairs with API overlap to reduce false positives

### case_id=2841 FN partial_functionality

- 方法: `CopyTo` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file char by char from image to dest with resource cleanup.
- B 摘要: Launches a NexOpen configuration: validates project, processes XML profiles, generates reverse engineering file, and schedules install job.
- 静态失败原因: Low token similarity (0.06), different method names and contexts; static BERT cannot capture the subtle partial I/O similarity that spans few lines in a long method.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as implementing a file copy sub-task (B includes a copy of a bundle resource to a project file), thus labeling as Type-4 partial functionality clone.
- 共享行为: Both involve file I/O operations；Both handle resource closing in finally blocks
- 行为差异: A is a pure file copy; B performs many domain-specific tasks；B includes XML processing, project validation, property setting, job scheduling
- 修正建议: Use dataflow analysis to detect file copy patterns；Incorporate program slicing to isolate sub-tasks；Add training on partial functionality clones

### case_id=2842 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `read`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads Twitter JSON feed from hardcoded URL using HttpClient and returns as string.
- B 摘要: Reads camera log from configurable URL using URL.openStream(), parses each line into CameraLogRecord, sorts, and logs progress.
- 静态失败原因: Static BERT/GraphCodeBERT likely overweighed the lexical and API overlap (BufferedReader, readLine, while loop, URL handling) and missed semantic differences in data usage and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have different inputs, outputs, and processing logic despite similar I/O boilerplate. The functional purpose differs significantly (retrieving a feed vs. parsing structured records).
- 共享行为: Both read data from a URL line by line using BufferedReader；Both use a while loop to read lines until null；Both involve I/O operations and exception handling
- 行为差异: Function A returns a concatenated string; Function B populates a list of parsed objects and sorts them；Function A uses hardcoded URL and Apache HttpClient; Function B uses variable url and Java URL.openStream()；Function A catches exceptions and prints stack trace; Function B throws IOException and uses finally to close reader；Function A logs an error on non-200 status; Function B logs info messages throughout
- 修正建议: Incorporate data flow analysis to track how the read data is used (e.g., returned as string vs. parsed into objects)；Add finer-grained semantic matching that considers the overall function purpose and return type；Use structure-based features to differentiate resource management patterns (finally block vs. none)

### case_id=2843 FP partial_functionality

- 方法: `readURL` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads from a URL and prints each line to standard output.
- B 摘要: Downloads an RDF model from a URL by opening a connection and reading into a Model object, with HTTP header customization.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the common boilerplate pattern (try-catch, URL connection, stream reading) and overlooked the semantic differences in what is done with the data (printing vs. model loading) and the divergent error handling. It may have been fooled by similar API calls (URL, InputStream, close) despite low token Jaccard.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled non-clone because although both functions involve reading from a URL, their purposes and outcomes differ significantly: one is a simple print operation, the other is a structured data download. The partial overlap is not sufficient for BCB's broader clone definition.
- 共享行为: Open a URL and obtain an input stream；Read data from the stream；Close resources in finally block
- 行为差异: readURL prints lines to console, while downloadModel loads data into an RDF Model object；Different error handling: readURL prints stack trace, downloadModel logs and throws RuntimeException；downloadModel sets HTTP request headers, readURL does not；downloadModel returns a Model, readURL returns void
- 修正建议: Incorporate data flow analysis to track how the read data is used (e.g., printed vs. parsed into a model)；Add contrastive training with pairs that share boilerplate but have different post-processing；Use graph representations that capture control and data dependencies beyond simple API call sequences

### case_id=2844 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `handledRun`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses an HTML page from a URL to extract links and link texts using regular expressions.
- B 摘要: Downloads and updates game data from a URL if the local version is outdated.
- 静态失败原因: Static BERT/GraphCodeBERT may have over-relied on lexical and syntactic similarities like common API calls (URL, BufferedReader, InputStreamReader) and structural patterns (try-catch, while loops), ignoring the semantic differences in the core business logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotations typically require significant functional overlap, not just shared boilerplate code. These functions have entirely different purposes and logic, so BCB would label them as non-clones.
- 共享行为: Both use URL and BufferedReader/InputStreamReader to read data from a URL.；Both involve opening network connections and reading input streams.
- 行为差异: Function A extracts anchor tags from HTML; Function B reads XML version info and downloads binary data.；Function A uses regular expressions for parsing; Function B uses string splitting and file I/O.；Function A returns a Vector array of links/texts; Function B updates a local file and logs messages.；Exception handling differs: A throws Exception, B catches and logs specific exceptions.
- 修正建议: Use data flow and control flow representations to distinguish different processing logic.；Incorporate higher-level semantic understanding of the task (e.g., HTML parsing vs. file downloading).；Reduce false positives from shared boilerplate by weighting unique functional elements more heavily.

### case_id=2845 FN benchmark_preference_bias

- 方法: `testStandardTee` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Tests the TeeWriter class by copying a string to two StringWriters and verifying they receive the same content.
- B 摘要: Retrieves a resource as an InputStream from a URL, with caching to local files and handling HTTP responses.
- 静态失败原因: Static BERT methods rely on token similarity and structural patterns; the token Jaccard is very low (0.05) and the code structures are entirely different (test vs. resource loading). The model correctly predicted non-clone due to lack of surface similarity, but the BCB label says clone, so the model 'failed' only if we consider BCB label correct.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider them clones under a very broad definition of 'stream copying functionality', focusing on the essential operation of reading from one stream and writing to another, despite different contexts.
- 共享行为: Both perform I/O operations involving reading and writing data streams.
- 行为差异: Function A is a simple test using StringReader/StringWriter; Function B is a complex resource caching mechanism with HTTP and file I/O.；Function A copies data to two destinations (Tee); Function B copies from URL to local file and returns input stream.；Function A uses IOUtils.copy; Function B uses manual byte-by-byte copy.；Function A deals with character streams; Function B deals with byte streams.
- 修正建议: Improve the model to handle broad conceptual similarity, possibly with dataflow analysis capturing that both involve stream I/O.；Alternatively, reconsider the benchmark label consistency.

### case_id=2846 FN benchmark_preference_bias

- 方法: `callApiPost` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Performs an HTTP POST request with parameters, checks response code, and returns the response input stream wrapped appropriately.
- B 摘要: Reads a file from the filesystem or classpath, concatenates lines, and returns the content as a string.
- 静态失败原因: The static BERT model correctly identified these as non-clones due to low token overlap (0.13) and large semantic difference. The model is not misled by the superficial I/O similarity because the specific APIs and control flow are distinct.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to broad Type-4 similarity: both functions read data from a source (network or file) and handle I/O exceptions. However, the functionality is entirely different in terms of purpose and implementation details.
- 共享行为: Both open and read from an input stream；Both handle IOException via try-catch blocks；Both return a processed result (InputStream vs String)
- 行为差异: Data source: HTTP request vs file system/classpath；Output type: InputStream vs String；Error handling: thrown exception vs print and System.exit；Presence of HTTP-specific setup (headers, method, parameters) in A but not in B
- 修正建议: Reconsider BCB annotation for this pair; it may be a false positive in the benchmark.；If BCB intends broad Type-4 clones, ensure annotation guidelines are consistently applied.；For model training, use more stringent clone definitions or filter out such pairs to avoid noise.

### case_id=2847 FN partial_functionality

- 方法: `downloadURLtoString` vs `runScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads content from a URL and returns it as a string, throwing IOException on failure.
- B 摘要: Downloads a script file from the applet's code base and returns its content as a string, returning 'error!' on failure.
- 静态失败原因: Static models like GraphCodeBERT may rely on surface-level token overlap (low jaccard) and ignore high-level functional similarity. They may not infer the core purpose when variable names and control flow differ.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels functionally similar code (Type-4) as clones, even when input handling and error strategies differ. Both achieve the same high-level goal of downloading URL content to string.
- 共享行为: Reads from a URL and returns the content as a string
- 行为差异: Input: A takes a URL object, B takes a script name and constructs URL using getCodeBase()；Error handling: A throws IOException, B catches Exception and returns error string；Reading method: A uses BufferedReader to read lines, B uses BufferedInputStream to read bytes；Applet context: B relies on applet environment, A is independent
- 修正建议: Train on more diverse Type-4 examples with similar high-level behavior but different implementations；Incorporate applet-specific patterns or use dataflow analysis to capture I/O sequences

### case_id=2848 FN partial_functionality

- 方法: `createOutputStream` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Creates a BufferedWriter that copies all entries from an input ZIP file to an output ZIP file, skipping 'content.xml', then adds a new 'content.xml' entry.
- B 摘要: Launches a NexOpen project configuration by processing Maven POM files, setting Hibernate properties, copying reverse engineering resources, and scheduling an install project action.
- 静态失败原因: Static BERT failed due to very low token overlap (Jaccard=0.049) and inability to recognize the abstract I/O functionality that BCB considered; the model relied on lexical and syntactic similarity which is missing.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered both as 'file I/O and stream manipulation' functions under a broad Type-4 interpretation, despite their vastly different high-level purposes.
- 共享行为: Both involve reading and writing files/streams；Both use ByteArrayOutputStream and InputStream for data copying；Both handle exceptions with try-catch blocks
- 行为差异: A is a simple ZIP entry copy with a skip; B is a complex launch configuration involving multiple external APIs and project state；A returns a BufferedWriter; B returns void；A deals with ODF content; B deals with project metadata and Hibernate dialect configuration
- 修正建议: Incorporate semantic role labeling to distinguish generic I/O from domain-specific tasks；Use API call sequence embeddings to capture high-level intentions；Apply contrastive learning on diverse functional groups to avoid overgeneralization

### case_id=2849 FN benchmark_preference_bias

- 方法: `hyperlinkUpdate` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles hyperlink activation in a Swing component by fetching URL content and displaying it in a dialog.
- B 摘要: Launches an Eclipse project configuration, processes Maven pom files, sets up Hibernate dialect, and installs the project.
- 静态失败原因: Static BERT models often rely on token-level patterns and may fail to capture deep semantic differences. In this case, the low Jaccard similarity and distinct domain-specific APIs (Swing vs Eclipse) should have prevented a false clone prediction. The FN error suggests the model correctly identified non-clone, but BCB's ground truth is questionable.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to some superficial similarity (e.g., both use IOUtils.copy and have try-finally blocks), but the core functionality is entirely different. This appears to be an annotation error or an overly broad interpretation of Type-4 clones.
- 共享行为: Both use IOUtils.copy for stream copying.；Both handle exceptions (IOException or CoreException).；Both involve reading from a stream and writing to another (string writer or byte array).
- 行为差异: Function A is a GUI event handler; function B is a launch configuration handler in an Eclipse plugin.；Function A reads a URL and displays text; function B processes XML files and sets up a project build.；Function A creates a simple dialog; function B interacts with Eclipse workspace, resources, and jobs.；Function B has complex attribute handling and conditional logic; function A is straightforward.
- 修正建议: Review and correct BCB annotations for this pair to ensure consistency with functional semantics.；Train models with more emphasis on high-level semantic intent rather than low-level API usage overlap.；Consider using domain-specific or intent-aware embeddings to reduce false positives from token overlap.

### case_id=2850 FP lexical_or_api_overlap

- 方法: `getRequestContent` vs `sendRequestObjectResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs an HTTP GET request and returns the first line of the response.
- B 摘要: Sends an HTTP POST request with compressed XML payload, saves the response to a file based on content type, and displays the file in a browser.
- 静态失败原因: The static BERT/GraphCodeBERT model likely relied on token-level similarities (e.g., 'URL', 'url.openConnection()', 'InputStream') and overlooked the vast difference in overall logic and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely marked non-clone because the functions are fundamentally different in purpose and complexity; they only share superficial API usage patterns.
- 共享行为: Both establish an HTTP connection via URL and URLConnection；Both read input from the connection's input stream；Both handle exceptions
- 行为差异: Function A uses GET; Function B uses POST with output and compression；Function A returns a single line; Function B returns a file path and displays the file；Function B includes complex setup (preferences, dialogs) and error handling with GUI messages；Function B saves response to local files and logs request data
- 修正建议: Enhance model with structural information (e.g., AST depth, control flow graphs)；Train on contrasting examples where API usage is similar but semantics differ；Incorporate token-based but also holistic semantic similarity with contrastive learning

### case_id=2851 FN partial_functionality

- 方法: `getContent` vs `postRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP request using Apache HttpClient and returns the response body as a string.
- B 摘要: Sends an HTTP POST request using URLConnection and returns the response body as a string, with error handling returning null.
- 静态失败原因: Static BERT models rely on token overlap and structural similarity. These functions have low token Jaccard (0.17284) and different API usage (HttpClient vs URLConnection). The model likely focused on different method signatures and error handling, missing high-level semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers Type-4 clones, so two functions that both perform HTTP requests and return response body are considered clones despite different input parameters and implementation details.
- 共享行为: Both perform HTTP requests and return the response body as a string.
- 行为差异: Different input types: HttpUriRequest vs URL string and HashMap.；Different error handling: throws Exception vs returns null on exception.；Different HTTP libraries: Apache HttpClient vs java.net.URLConnection.；Function B builds POST parameters; A expects pre-built request.
- 修正建议: Use dataflow or control flow analysis to capture common pattern of HTTP request and response reading.；Train on broader clone types including Type-4.；Incorporate API-level abstraction to recognize different HTTP libraries perform similar tasks.

### case_id=2852 FP long_range_semantics

- 方法: `perform` vs `encryptPassword`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Performs HTTP-based classification of a concept in a Struts action, including building XML, sending request, parsing result, and setting session attributes.
- B 摘要: Hashes a password using SHA-1 and returns Base64-encoded hash.
- 静态失败原因: The model likely was misled by truncation of the long function A, losing its core logic and only seeing generic boilerplate code that resembles many action methods. The short function B also has generic method signature, leading to false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels as clones only functions that implement the same or highly similar functionality. Here the functionalities are entirely different (HTTP classification vs. password hashing), so BCB correctly marks as non-clone.
- 共享行为: Both are Java methods that return a String and can throw Exception.
- 行为差异: Function A performs complex HTTP I/O and session management; Function B performs local cryptographic hashing.；Function A has multiple branches for error handling; Function B has no error handling (throws Exception).；Function A uses Struts framework objects; Function B uses MessageDigest and Base64Encoder.；Function A is a controller action; Function B is a utility method.
- 修正建议: Improve handling of long functions by using hierarchical representations or better segmentation.；Augment training data with more diverse non-clone pairs that share only boilerplate.；Incorporate functional call graph or API usage information to distinguish local computation from I/O.

### case_id=2853 FN partial_functionality

- 方法: `unzipModel` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts a zip file from a given filename to a specified temp directory.
- B 摘要: Downloads a zip file from a hardcoded URL and extracts its contents to the current directory, printing progress.
- 静态失败原因: Static BERT likely overemphasized lexical and structural differences such as the URL handling, exception catching, printing, and method signature, while failing to recognize the identical core loop and data copy logic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers functions with the same core algorithm (zip extraction) as clones, even with different I/O and error handling, because they implement the same conceptual functionality.
- 共享行为: Iterates over zip entries using ZipInputStream；Reads entry data in buffered chunks of BUFFER size；Writes each entry to a file using BufferedOutputStream
- 行为差异: Input source: A uses a local file path; B uses a URL (HTTP or file).；Output destination: A writes to a provided tempdir; B writes to the current working directory.；Error handling: A catches exceptions and wraps in EDITSException; B throws Exception.；Side effects: B prints "Extracting: " for each entry; A has no output.
- 修正建议: Train on more varied zip extraction examples with different I/O patterns.；Incorporate program dependence or dataflow features to capture core algorithmic similarity.；Use AST-based or graph-based code representations that abstract over trivial differences.

### case_id=2854 FN partial_functionality

- 方法: `sendExceptionToServer` vs `startScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST and reads the response.
- B 摘要: Reads a script from a URL and appends it to a dialog buffer.
- 静态失败原因: Static BERT models rely on token overlap and control flow; low Jaccard similarity and different API usage (URLConnection vs URL.openStream) caused the model to miss the broader structural similarity in I/O handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones due to shared pattern of performing network I/O with URL connections and reading/writing streams, even though specific data handling differs.
- 共享行为: Both use URL to establish network connections；Both read input from streams；Both handle IOException
- 行为差异: A sends data and reads response; B only reads data；A builds POST data; B does not；A has more conditional logic; B is simpler
- 修正建议: Increase training data with diverse I/O patterns；Use contrastive learning to focus on structural similarity；Incorporate data flow analysis to capture I/O direction

### case_id=2855 FP boilerplate_overlap

- 方法: `readIntoList` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads an HTML file from a URL, extracts link text, and creates JMenuItems with action commands.
- B 摘要: Reads a service file from the classpath, loads the first non-comment class name, and returns an instantiated FrameworkFactory.
- 静态失败原因: The model likely overfocused on the common pattern of opening a URL and reading lines with BufferedReader, missing the fundamentally different processing inside the loop.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functionality is completely different, despite shared I/O boilerplate.
- 共享行为: Both open a URL and read lines with BufferedReader
- 行为差异: A parses HTML tags and creates GUI components; B parses service file and loads a class via reflection；A populates a Map; B returns an object or throws exception；A handles exceptions by printing stack trace; B throws exception
- 修正建议: Incorporate dataflow analysis to distinguish different processing logic；Use contrastive learning to penalize over-reliance on common I/O patterns

### case_id=2856 FN partial_functionality

- 方法: `runScript` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a script file from a URL and returns its content as a string, with error handling returning 'error!'.
- B 摘要: Invokes a remote service method via HTTP POST with retry logic and deserializes the JSON response.
- 静态失败原因: Static BERT models often rely on token overlap and shallow syntactic cues. With a token Jaccard of only 0.1228, the model sees little surface similarity. Additionally, the APIs used (URL vs HttpClient) and control flow differ significantly, masking the underlying common pattern of network I/O.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone due to broad Type-4 similarity: both functions involve making an HTTP request to fetch data and reading the response stream, albeit with different protocols and error handling.
- 共享行为: Both perform HTTP requests to a remote server.；Both read response data from an input stream.
- 行为差异: A uses a simple GET request (URL.openStream) while B uses HTTP POST with JSON payload.；A reads raw bytes and concatenates; B reads line-by-line, appends newlines, and then removes trailing newline.；A returns 'error!' on any exception; B retries on timeout and throws others.；A does not check HTTP status codes; B checks for >=300 and throws exception.
- 修正建议: Incorporate control-flow and data-flow features to capture the 'HTTP request-response' pattern.；Use code summarization or docstring embeddings to identify high-level intent.；Augment training data with diverse implementations of similar tasks to generalize beyond exact API usage.

### case_id=2857 FP lexical_or_api_overlap

- 方法: `getFrameworkFactory` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads an OSGi FrameworkFactory by reading a service configuration file from the classpath and instantiating the class by name.
- B 摘要: Checks for software upgrades by querying a remote license server, processing license and upgrade records, updating a database, and showing UI messages.
- 静态失败原因: The model may have been misled by the overlapping use of common APIs like BufferedReader and URL, and the general pattern of reading lines, ignoring the large semantic gap in overall functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers functional similarity, and these two functions have entirely different purposes and behaviors, so they would not be labeled as clones.
- 共享行为: Both use BufferedReader to read text line by line.；Both handle exceptions with try-catch or throws.；Both perform I/O operations (file vs network).
- 行为差异: A reads a local classpath resource; B reads from a remote URL.；A returns an object; B is void and modifies UI/database.；A performs class loading; B performs database and network operations.；A is a private utility; B is a public event handler.
- 修正建议: Include method name and surrounding class context in the model.；Train on more varied examples to reduce bias towards common I/O patterns.；Use a model that captures long-range semantic dependencies better.

### case_id=2858 FN lexical_or_api_overlap

- 方法: `fileDownload` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a given URL and saves it to a local directory.
- B 摘要: Checks for software version updates by reading a version file from a URL.
- 静态失败原因: The model likely focused on lexical tokens (method names, variable names, specific logic) and missed the abstract structural similarity due to high token dissimilarity and different surface-level semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider this a clone because both methods share a common structural pattern of reading from a URL using BufferedReader, which is a typical Type-3/Type-4 clone scenario where the functional similarity is in the generic 'read from URL' behavior, despite different specific outputs.
- 共享行为: Both open a URL connection and read input using BufferedReader.；Both handle IOExceptions in a try-catch block.；Both close the stream after reading.
- 行为差异: Method A downloads and saves file content; Method B parses text lines for version numbers.；Different parameters: Method A takes a URL and directory string; Method B takes a View object and uses jEdit properties.；Different exception handling: Method A logs; Method B shows error dialog and hides wait cursor.
- 修正建议: Use dataflow-aware models that capture control and data dependencies.；Incorporate structural similarity metrics like AST matching alongside token-based features.；Train on more diverse clone pairs with low token overlap but high structural similarity.

### case_id=2859 FP boilerplate_overlap

- 方法: `main` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method of an adapter generator that parses a Prolog file, generates adapter layers and classes, and writes them to a JAR file.
- B 摘要: Recursive file copy function that copies a file or directory to a destination using FileChannel.
- 静态失败原因: The static model may have over-relied on superficial API usage (File, IOException) and structural patterns (if-else, try-catch) while missing the distinct high-level semantics of adapter generation vs. file copying.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the functions have entirely different purposes and actual functionality, despite both using File and IOException.
- 共享行为: Both methods use file I/O operations (File, IOException).
- 行为差异: Code A is a complex main method for adapter generation involving Prolog parsing, class writing, and serialization.；Code B is a simple utility for copying files recursively, with directory handling.
- 修正建议: Incorporate dataflow analysis to capture domain-specific operations.；Use more fine-grained tokenization to distinguish library-specific calls.；Add contrastive learning with hard negative pairs that share APIs but differ in purpose.

### case_id=2860 FN benchmark_preference_bias

- 方法: `readRemoteFile` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a hardcoded remote file via URL stream and concatenates lines into a string, with simple error printing.
- B 摘要: Performs an HTTP POST request with parameters, reads the response body into a string, returns null on error with error fields set.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on token/API overlap and structural patterns; the low token Jaccard (0.23) and differing API usage (URL vs HttpClient) prevented recognizing the shared core functionality of fetching HTTP content.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB labels this as a clone because both functions fundamentally implement 'reading an HTTP response body into a string', a high-level semantic similarity that overrides differences in protocol, error handling, and parameters. BCB's Type-3/4 clone definition includes partial functional overlap.
- 共享行为: Both make an HTTP request to a remote server.；Both read the response body line by line and concatenate into a single string.；Both return a string containing the response body on success.
- 行为差异: Function A uses a GET request (default openStream), Function B uses POST with parameters.；Function A has no error status handling and always returns a string; Function B returns null on HTTP errors or IOExceptions and sets error fields.；Function A catches EOFException separately; Function B does not.；Function A has no parameters; Function B takes URL, timeout, and params.
- 修正建议: Train models with broader functional equivalence labels, e.g., using API call patterns and ignoring parameter/error handling details.；Incorporate control-flow abstraction that normalizes different loop structures (while-eof vs while-assign).；Use graph representations that capture data flow of HTTP response retrieval regardless of specific libraries.

### case_id=2861 FN boilerplate_overlap

- 方法: `main` vs `handle`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a hardcoded URL, unzips it, and extracts entries to current directory.
- B 摘要: Handles log file rotation by optionally compressing, moving to a destination, deleting old files, and archiving.
- 静态失败原因: Static BERT likely correctly identified the low token overlap and distinct vocabulary (e.g., KMZ vs log rotation) and functional difference, predicting non-clone.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as 'data copying' tasks involving I/O streams, but the functional purpose and complexity differ significantly; the annotation is overly broad.
- 共享行为: Both perform file I/O operations involving reading and writing bytes in a loop.；Both use stream classes like InputStream, OutputStream, and buffered streams.
- 行为差异: A is a single-shot extraction of a zip from a URL; B is a complex log rotation with conditional compression, archiving, and file deletion.；A's output is unzipped files; B's output is rotated/compressed log files with management logic.；A has no file management or cleanup; B handles timestamps, directory creation, and deletion.
- 修正建议: Re-annotate pair as non-clone.；Improve BCB guidelines to avoid labeling such different tasks as clones.

### case_id=2862 FP boilerplate_overlap

- 方法: `googleImageSearch` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs Google image search by fetching and parsing HTML to extract image URLs.
- B 摘要: Performs version check by fetching a properties file and extracting build numbers.
- 静态失败原因: The model likely overemphasized the lexical and API-level overlap (URL, BufferedReader, readLine) and missed the semantic divergence in purpose and data processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely annotates as non-clone because the functions have distinct high-level goals and the common URL-fetching pattern is considered boilerplate, not sufficient for clone classification.
- 共享行为: Both open URL connections to fetch remote data；Both read lines from input streams；Both handle IOExceptions
- 行为差异: Different purposes: image search vs. version check；Different URL construction and query parameters；Different parsing logic: HTML parsing for image URLs vs. properties file parsing；Different usage of results: storing image URLs vs. triggering version comparison
- 修正建议: Incorporate dataflow analysis to track how fetched data is used；Use models that capture task intent beyond surface patterns；Add examples of non-clone pairs with similar I/O patterns but different semantics

### case_id=2863 FN benchmark_preference_bias

- 方法: `getButtonSonido` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Creates a JButton with an action listener that opens a file chooser to select and copy a sound file.
- B 摘要: Builds an entire site for editing by transforming XML pages, reading/writing files, and performing string replacements.
- 静态失败原因: Static BERT/GraphCodeBERT likely correctly predicted non-clone due to low token overlap and clearly different contexts (GUI vs server-side), but it may have been misled by the BCB label if trained on BCB labels.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have incorrectly labeled these as clones due to an overly broad interpretation of partial functionality, such as both involving file reading/writing and initialization steps, but there is no core semantic overlap.
- 共享行为: Both perform file I/O operations；Both use try-catch blocks for IOException
- 行为差异: A is GUI-oriented with JButton and file chooser; B is server-side page generation；A deals with a single sound file; B processes multiple pages and various paths；A uses FileChannel for copying; B uses FileReader/FileWriter
- 修正建议: Improve BCB annotation consistency；Include more detailed functional similarity criteria

### case_id=2864 FN partial_functionality

- 方法: `testNetworkHTTP` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs multiple HTTP GET requests to send device information to remote servers, discarding responses.
- B 摘要: Performs a single authenticated HTTP GET request, reads response into a string buffer and signals completion.
- 静态失败原因: Static BERT models rely on token overlap and syntactic similarity. The low token Jaccard (0.24) and differences in method names, comments, and request details cause the model to miss the underlying HTTP client pattern shared across both functions.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels functions as clones if they share the same core API usage pattern, even if the specifics (URLs, authentication, number of requests) differ. Here both functions implement the HTTP GET and read response pattern, which is considered a Type-3 clone due to structural similarity.
- 共享行为: Both use HttpURLConnection to open an HTTP connection；Both get an InputStream and wrap it in BufferedReader；Both read lines from the server response using a while loop；Both handle exceptions with try-catch blocks
- 行为差异: Function A makes multiple GET requests (7) while B makes only one；Function B includes HTTP Basic Authentication header; A does not；Function A discards the response body; B accumulates it into a StringBuffer；Function A logs debug messages; B updates a 'finish' flag
- 修正建议: Train models to recognize repeated patterns and abstract API usage；Incorporate data-flow analysis to capture connection lifecycle；Use contrastive learning to align similar API usage patterns despite lexical differences

### case_id=2865 FP boilerplate_overlap

- 方法: `copyFile` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Copies a file from input path to output path using NIO FileChannel.
- B 摘要: Reads comma-separated string tokens from class fields, populates sets and maps for Tibetan transliteration processing.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized the presence of boilerplate code (try-catch blocks, IOException handling) and common API terms (File, StringTokenizer) while missing the fundamental difference in purpose. Low token Jaccard (0.0557) suggests the model did not rely on token overlap; instead, it may have been misled by structural patterns such as both having a try block with resource management.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the two functions have completely different functionality (file copy vs data parsing) and only share trivial common Java patterns (exception handling, variable declarations).
- 共享行为: Both use try-catch for exception handling；Both involve I/O operations (file vs string tokenization)；Both use Java APIs (FileChannel, StringTokenizer)
- 行为差异: Function A copies file content; Function B processes string tokens to build data structures；Function A uses FileChannel; Function B uses StringTokenizer and HashSet/Map；Function A has no side effects on global state; Function B populates global/instance variables；Function A is a utility method; Function B is a configuration loader
- 修正建议: Incorporate dataflow or control-flow analysis to distinguish functional intent.；Augment training data with non-clone pairs sharing syntactic boilerplate but differing in semantics.；Use models that capture long-range dependencies and call relationships to understand overall purpose.

### case_id=2866 FN benchmark_preference_bias

- 方法: `doGet` vs `test`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request for a portal page, resolves page from parameter, checks user visibility, logs request, and optionally caches output.
- B 摘要: JUnit test that initializes a traffic simulation with an XML definition, sets frame properties, and runs simulation steps printing vehicle positions.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone; the failure is due to a mislabeled BCB annotation, not a model error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label of 1 is likely an annotation error or due to very loose criteria that are not justified by the code; no reasonable interpretation of partial functionality similarity.
- 共享行为: None; both are Java methods using standard libraries but no functional overlap.
- 行为差异: Different domains: servlet vs simulation test；Completely different input/output and purpose；No shared logic or data structures
- 修正建议: Verify and correct BCB annotation for this pair；Exclude this pair from evaluation if annotation is erroneous

### case_id=2867 FN partial_functionality

- 方法: `WebmillDeploy` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Deploys a webmill application by reading a WAR file, extracting and rewriting XML configurations (web.xml, portlet.xml, context.xml), and outputting a new WAR file.
- B 摘要: Builds a site for editing by reading XML from a file, applying XSLT transformations and string replacements, and writing multiple output HTML files.
- 静态失败原因: Static BERT/GraphCodeBERT relies heavily on token-level similarity, which is low (Jaccard 0.1156). It fails to capture the abstract semantic pattern of file transformation with XML processing, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as Type-4 (semantic) clones due to high-level similarity: both are file transformation tasks involving XML parsing/writing, resource management, and producing output files from input files.
- 共享行为: Both involve reading input files, processing XML, and writing output files.；Both manage file resources (streams, channels) with cleanup in finally blocks.
- 行为差异: Function A specifically repackages a portlet WAR; Function B generates a multi-page website.；Function A uses JAR/ZIP entries; Function B uses XSLT transformations and per-page processing.；The XML processing and output formats are entirely different.
- 修正建议: Use program dependency graphs or dataflow analysis to capture structural similarities.；Train on more diverse examples of file transformation tasks.；Incorporate explicit feature extraction for common patterns (file I/O, XML parsing, resource management).

### case_id=2868 FN benchmark_preference_bias

- 方法: `ExternalDecoder` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Constructor that copies an input stream to a process's standard input in a background thread.
- B 摘要: Downloads a KMZ file from a URL and extracts its entries to files.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone due to low lexical overlap (token Jaccard 0.08), different method names, and structural differences. The model did not fail; it aligned with strict semantic equivalence.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to broad Type-4 similarity: both functions perform stream copying (read from source, write to sink) and handle IO exceptions, but this is overly broad and not typical of BCB annotations.
- 共享行为: Both read data from an input source and write to an output destination
- 行为差异: A copies raw bytes to a process's stdin; B decompresses ZIP and writes files；A uses multithreading; B is single-threaded；A operates on any InputStream; B specifically handles ZIP files；A's output is a process's stdin; B's output is the file system
- 修正建议: Re-evaluate BCB label for this pair as likely incorrect；Refine BCB annotation guidelines to avoid overly broad Type-4 clones；Use stricter thresholds for partial functionality similarity

### case_id=2869 FN lexical_or_api_overlap

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using a byte buffer and file streams.
- B 摘要: Builds a site for editing by reading XML, transforming with XSLT, and writing output files, with extensive parameter handling and error logging.
- 静态失败原因: The static model likely failed due to low token overlap (Jaccard 0.06) and vast difference in method length and complexity, causing it to miss the underlying similarity in file I/O pattern amidst the unrelated code in B.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled it as a clone due to both methods performing file read-write operations with a buffer, which fits broad Type-3/Type-4 clones that share partial functionality or similar I/O patterns, even though overall intent differs.
- 共享行为: Both read from a file using FileInputStream and write to another file using a buffer.
- 行为差异: A is a simple generic file copy; B is a complex site-building method with many parameters and steps beyond file I/O.；A uses byte array buffer; B uses char array buffer and performs string transformations.；A writes directly to FileOutputStream; B writes via a custom FileSystem class.；A has minimal error handling; B has extensive error handling, debug tracing, and DOM/XML processing.
- 修正建议: Enhance model with dataflow analysis to capture read-write operations across different method lengths.；Use embedding techniques that identify sub-patterns or partial functionality clones.

### case_id=2870 FN partial_functionality

- 方法: `encodeFileToFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Encodes a file using Base64 encoding and writes the result to another file, with buffered I/O and error handling.
- B 摘要: Builds a site for editing by reading XML files, performing transformations, and writing the resulting pages to output files, involving multiple file I/O operations and string manipulations.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on token-level patterns and lexical overlap. With a token Jaccard of only 0.0667 and widely different method names, the model failed to capture the high-level semantic commonality. The model may have been biased by the length and complexity difference (function B is much longer) and the distinct API calls (Base64 vs. Transformer).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: The BCB annotator may have considered these clones because both implement a high-level 'file transformation' pattern: read from one or more sources, process the data, and write to output. The common I/O infrastructure (streams, buffers, exception handling) outweighs the specific transformation differences, aligning with Type-4 semantic similarity.
- 共享行为: Both perform file-to-file data transfer using buffered streams；Both use try-catch-finally blocks for I/O error handling；Both involve loops that read/write data in chunks (byte or character buffers)
- 行为差异: Function A is a simple standalone encoding operation; Function B is a complex multi-step site building method；Function A has a single input and output file; Function B uses multiple input sources (paths, properties) and writes multiple output files；Function A returns a boolean success flag; Function B is void and throws multiple checked exceptions；Function A involves Base64 encoding; Function B involves XML/DOM transformations and string replacements
- 修正建议: Use data flow analysis to abstract the 'read-process-write' pattern；Incorporate hierarchical structural features (e.g., AST subtrees for I/O operations)；Train with contrastive learning on pairs with low lexical overlap but high semantic similarity；Add domain knowledge about common file processing patterns

### case_id=2871 FN benchmark_preference_bias

- 方法: `readData` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads configuration data from strings and a file, parses lines, and populates multiple data structures for Tibetan/sanskrit character handling.
- B 摘要: Opens a URL to a daily trend page, reads the response line by line, and discards all content.
- 静态失败原因: Low token overlap (0.06) and distinct data flow/control structures led the model to predict non-clone, missing the broad I/O-level similarity that BCB annotators may have considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'reading data from an external source' (file vs URL) with a similar while-loop pattern, accepting broad Type-4/partial functionality similarity despite differences in processing.
- 共享行为: Read input line by line using a loop
- 行为差异: A reads from multiple sources (strings and file), B reads from a single URL；A processes the read data extensively (populating sets, maps), B completely ignores the read lines；A has complex conditional logic and error handling, B has empty catch blocks；A modifies global state, B does not
- 修正建议: Train models with BCB-style annotations that accept broad Type-3/Type-4 clones；Incorporate high-level I/O pattern recognition (e.g., reading input loops) into the model

### case_id=2872 FN partial_functionality

- 方法: `readGeoParserResult` vs `loadExistingAntlibs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads geospatial XML data from a URL, parses place names and gazetteer IDs with retry and error handling.
- B 摘要: Loads ant library definitions from classpath resources by reading URLs and iterating over lines.
- 静态失败原因: The model relied on token overlap (Jaccard 0.13) and missed the shared I/O reading pattern due to different variable names and API calls, failing to abstract the common control flow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a Type-3 clone because both functions share the significant structural pattern of reading lines from a URL using BufferedReader with exception handling, despite different domain-specific processing.
- 共享行为: Both open a URL (or URL-like resource) and create a BufferedReader.；Both read lines in a while loop and process each line.；Both close streams and handle IOExceptions.
- 行为差异: Function A parses XML and constructs a collection of tuples; Function B constructs URIs and loads antlibs.；Function A has retry logic on failure; Function B does not.；Function A uses XML parsing libraries; Function B uses simple string processing and URI manipulation.
- 修正建议: Train model on structural patterns like BufferedReader usage with while loops over streams.；Incorporate control flow graph or program dependency graph features.；Use data flow analysis to recognize common I/O initialization and iteration patterns.

### case_id=2873 FN partial_functionality

- 方法: `lookupFutureEvents` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a list of future events from the Meetup API via HTTP GET and parses JSON response into Event objects.
- B 摘要: Invokes a remote method via HTTP POST, serializes arguments as JSON, retrieves response, and deserializes it into the method's return type, with retry logic on timeout.
- 静态失败原因: A static model like GraphCodeBERT might have focused on syntactic similarity (low Jaccard=0.13) and failed to recognize the abstract similarity of HTTP+JSON pattern. The model may be sensitive to specific method names, URL construction, and specific API calls, which are very different here.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might have labeled them as clones due to the common pattern of making an HTTP request, reading response, and parsing JSON, which are shared high-level steps. However, the specific functionality and data handling differ significantly.
- 共享行为: Both perform HTTP requests；Both read HTTP response body using BufferedReader；Both parse JSON data from response
- 行为差异: Different HTTP methods (GET vs POST)；Different URL construction (fixed template vs service URL + method name)；Different return types (List<Event> vs Object)；Different error handling (custom exception vs RuntimeException/retry)
- 修正建议: Incorporate data flow analysis to understand the transformation of input to output；Use models that capture higher-level program intentions beyond token overlap；Include more diverse training examples of functions that share partial functionality but differ in context

### case_id=2874 FN partial_functionality

- 方法: `readReferenceText` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a reference text file from a bundle resource and returns its content as a string.
- B 摘要: Invokes a remote HTTP service, reads the JSON response, deserializes it, and returns the result, with retry logic on timeout.
- 静态失败原因: A static BERT/GraphCodeBERT model likely failed due to low lexical and API overlap (token Jaccard 0.16) and focus on domain-specific APIs (URL, HttpPost vs. URL, InputStream), missing the shared underlying stream-reading pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both methods share a common pattern of reading from an input stream line by line and building a string, which is considered a similar functionality in a broad sense (Type-4 or partial functionality).
- 共享行为: Both use BufferedReader to read lines from an InputStream and accumulate them into a StringBuilder/StringBuffer with newlines.
- 行为差异: A reads from a local resource file, while B makes an HTTP POST request.；A returns the raw text as a String, while B parses JSON and returns an Object.；B has retry logic on ConnectTimeoutException, while A has no retry.；A throws NoContentException on failure, while B throws RuntimeException or passes through the exception.
- 修正建议: Enhance model to recognize common I/O patterns across different domains.；Incorporate control flow or data flow analysis to detect similar substructures.；Use AST-based features that capture reading-while-loop idioms.；Train on more examples of cross-domain partial clones.

### case_id=2875 FN partial_functionality

- 方法: `copyResource` vs `copyFiles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a single resource (from URL or local file) to a destination file using byte-by-byte copying.
- B 摘要: Recursively copies files or directories from source path to destination path using FileChannel for file-to-file copies.
- 静态失败原因: The token Jaccard similarity is low (0.20339), and the code structures are quite different (one uses InputStream/OutputStream, the other uses FileChannel and recursion). Static models relying on lexical overlap or surface-level patterns fail to capture the underlying semantic similarity because the shared functionality is implemented with different APIs and control flow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs as clones if they implement the same high-level functionality (file copy), even if the implementation details differ (e.g., recursive vs non-recursive, different I/O APIs). This pair both serve the purpose of copying files.
- 共享行为: Both copy data from a source to a destination.；Both use file I/O and handle exceptions.；Both close streams/channels after copying.
- 行为差异: Function A handles URLs as source; function B does not.；Function B handles directories recursively; function A does not.；Function A uses InputStream/OutputStream byte-by-byte; function B uses FileChannel.transferTo for files.；Function A determines destination via destinationFile(); function B takes destination path as parameter.
- 修正建议: Train a model with contrastive learning on pairs that have low lexical overlap but high semantic similarity.；Incorporate program analysis (e.g., data flow graphs or type dependencies) to detect semantic clones.；Use a hierarchical representation that captures both local and global code structure.

### case_id=2876 FN boilerplate_overlap

- 方法: `doGet` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles an HTTP GET request to retrieve and render a portal page after checking visibility and permissions, with caching and logging.
- B 摘要: Launches a build/configuration process for a NexOpen project by parsing XML files, setting up Hibernate properties, and copying resource files.
- 静态失败原因: The static model (e.g., GraphCodeBERT) likely predicted non-clone because token overlap (Jaccard=0.0838) is very low and the specific identifiers, APIs, and domain terms are completely different, despite similar structural patterns.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might have labeled them as clones under a broad Type-4 semantic similarity, considering both as 'initialization/handler' methods that take a request/configuration, perform conditional checks, access properties, and handle exceptions.
- 共享行为: Both methods contain try-catch blocks for exception handling.；Both use logging (myLogger.info, Logger.getLog().info).；Both perform file/resource operations (FileWriter, InputStream, etc.).；Both have conditional logic to handle different cases.
- 行为差异: Function A is a web request handler (doGet) processing HTTP request/response; B is a project launch handler (launch) for Eclipse.；A deals with page rendering and user permissions; B deals with Maven POM files and Hibernate configuration.；A outputs an HTML page via PrintWriter; B sets up project files and properties.；The core domain objects (HttpServletRequest, Page vs ILaunchConfiguration, IProject) are completely different.
- 修正建议: Incorporate more domain-aware features or context into the model.；Use a stricter definition focusing on core functionality rather than structural patterns.；Consider using dynamic analysis or API call sequence similarity.

### case_id=2877 FP lexical_or_api_overlap

- 方法: `getUser` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from a DAO or from a local config file if not found, creating and saving the user if matching login found.
- B 摘要: Fetches a version string from a remote URL by reading the first line of the response.
- 静态失败原因: Static BERT models rely heavily on lexical overlap and API sequence patterns. Both methods use similar API calls (URL, BufferedReader, readLine, try-catch, return null), leading to high similarity in token embeddings, while ignoring semantic differences in method name, return type, and overall goal.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically considers functional similarity; these methods serve entirely different purposes (user authentication vs version retrieval), so they are non-clones.
- 共享行为: Both use URL and BufferedReader to read textual content over network or classpath；Both loop over lines (though B only uses first)；Both return a result or null on exception
- 行为差异: Different inputs: userlogin vs none；Different output types: User object vs String；Different data sources: local config file vs remote version URL；Different parsing logic: tokenizing by colon vs taking whole line
- 修正建议: Incorporate method name and return type into the representation；Use data flow analysis to distinguish I/O and state；Train with contrastive examples that have similar APIs but different semantics

### case_id=2878 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter timeline from a fixed URL and returns the entire JSON response as a string.
- B 摘要: Imports biological sequences from a selected URL, parsing FASTA-like format and storing names and sequences into lists.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on overlapping tokens like 'InputStream', 'IOException', 'readLine', and the general try-catch structure, ignoring the fundamental semantic differences in parsing logic and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have entirely different domains (Twitter vs biology), different data formats, and different return types. The only generic similarity is reading from a URL, which is too broad for Type-3/4 similarity.
- 共享行为: Both open an HTTP connection to read data from a URL；Both read data line by line using BufferedReader/Reader；Both include try-catch blocks for IOException handling
- 行为差异: Different URL sources: hardcoded vs user-selected from combo box；Different data parsing: JSON response vs FASTA-like sequence format；Different output: returns a single String vs populates two ArrayLists (names and sequences)；Different classes used: HttpClient vs custom ImportHelper
- 修正建议: Incorporate data flow analysis to track output types and transformations；Consider method names and comments for domain context；Use larger context windows to capture overall behavior beyond common IO patterns

### case_id=2879 FN partial_functionality

- 方法: `main` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Constructs a RenRen API POST request with many parameters, opens an HttpURLConnection, sends the request, and prints the response.
- B 摘要: Opens a URLConnection to a fixed URL using GET, reads the response with BufferedReader, and logs the content.
- 静态失败原因: The model relied on token similarity and Jaccard coefficient, which is low (0.16) due to different method names, class names (RenRenConstant, PostParameter), and output methods. It failed to capture the structural and functional similarity of the URL reading pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels such pairs as Type-3/Type-4 clones because the core pattern of opening a URL, reading the stream, and outputting is identical despite differences in method name, specific API, and request method. The high-level goal of fetching and outputting URL content is shared.
- 共享行为: Opens a URL connection；Reads response using BufferedReader and readLine() loop；Outputs the response (print/log)
- 行为差异: A uses POST with parameters; B uses GET；A constructs URL with dynamic parameters; B uses fixed URL；A uses HttpURLConnection, B uses URLConnection；A outputs via System.out; B logs
- 修正建议: Use data flow or control flow graphs to capture the common I/O pattern.；Train with more diverse examples of URL fetching clones.；Incorporate program slicing to focus on the core functionality.

### case_id=2880 FP lexical_or_api_overlap

- 方法: `read` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads camera log entries from a URL, parses each line into a CameraLogRecord, and sorts the records.
- B 摘要: Imports FASTA sequences from a URL by parsing lines starting with '>' and extracting sequence data.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized lexical and API-level overlaps (e.g., 'openStream', 'readLine', 'IOException', try-catch) and similar control structures (while loop), ignoring the domain-specific parsing logic that makes them semantically different.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the core functionality differs significantly: one is for camera data aggregation, the other for biological sequence import. Only superficial I/O patterns match, which is insufficient for clone labeling under BCB's semantic criteria.
- 共享行为: Both open a URL stream and read input line-by-line.；Both handle IOException and use try-catch for error handling.；Both perform simple parsing on each line.
- 行为差异: Function A processes camera log records and sorts them; Function B processes biological sequences and stores names and sequences.；Function A uses a custom parser for camera logs with a specific exception; Function B uses a custom ImportHelper for FASTA parsing.；Function A logs progress; Function B uses combo box for URL selection and handles more exception types (MalformedURLException, EOFException).
- 修正建议: Train with more examples that differentiate domain-specific behavior from shared I/O boilerplate.；Incorporate data flow and dependency analysis to capture distinct processing logic.；Use contrastive learning to push apart functions with different core semantics despite similar APIs.

### case_id=2881 FN benchmark_preference_bias

- 方法: `decodeFileToFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.5`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Decodes a Base64-encoded input file and writes the decoded bytes to an output file, returning success status.
- B 摘要: Fetches a resource by name, caches it locally if not already cached, and returns a FileInputStream from the cache.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on lexical and syntactic overlap, which is low (Jaccard 0.224). They lack understanding of deep semantics and cannot recognize that despite different surface forms, both functions perform data copying from input to output with error handling. The model likely saw the low token overlap and predicted non-clone, missing the high-level structural similarity that BCB considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely considered these as Type-4 clones because both involve reading from an input stream (file or URL) and writing to an output stream (file or cache) with similar error-handling patterns, despite fundamental differences in purpose and logic. The BCB annotation guidelines for Type-4 include functionally similar but different implementations, and here the stream copying pattern is similar.
- 共享行为: Both perform file I/O operations；Both use try-catch-finally for error handling；Both use BufferedInputStream/BufferedOutputStream for reading/writing；Both close streams in finally blocks
- 行为差异: Function A decodes Base64, Function B downloads and caches resources；Function A returns boolean, Function B returns InputStream；Function A works with local files only, Function B works with remote URLs；Function B has complex caching logic including HTTP headers and cache file management
- 修正建议: Incorporate dataflow analysis to capture input-output transformations；Use semantic role labeling to abstract functions as reading from a source and writing to a sink；Introduce training examples that highlight structural similarity despite different APIs

### case_id=2882 FP lexical_or_api_overlap

- 方法: `saveAttachmentBody` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Saves an attachment body from a part to a file and updates the attachment record in a content provider.
- B 摘要: Main method that parses a Prolog file, generates adapter classes and a lookup, and writes them to a JAR file.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on superficial token overlaps (e.g., 'File', 'InputStream', 'out') and similar control flow patterns (if, try-catch), ignoring the completely different domain-specific logic and data flows.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones for functions with entirely different purposes, even if they share some low-level API usage like file streams.
- 共享行为: Both involve file I/O operations (reading, writing files).；Both use try-catch for exception handling.；Both create and manipulate File objects.
- 行为差异: Function A is a utility for storing email attachments; Function B is a code generation tool entry point.；Function A interacts with Android content providers; Function B uses ASM and class loaders for bytecode generation.；Function A has no command-line argument handling; Function B parses arguments for debug mode and file paths.
- 修正建议: Include more context-aware training that captures high-level intent.；Use data-flow analysis to distinguish different uses of common APIs.；Add negative sampling with similar token overlap but different semantics.

### case_id=2883 FN partial_functionality

- 方法: `testNetworkHTTP` vs `fileDownload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Tests multiple HTTP GET requests by reading responses line-by-line and discarding output.
- B 摘要: Downloads a file from a given HTTP URL and writes it to a local destination directory.
- 静态失败原因: Static BERT models rely on token similarity and structural patterns; low Jaccard similarity, different method signatures, I/O patterns, and exception handling likely led to low similarity features, causing false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both functions as performing HTTP data retrieval, where the exact handling of the read data is secondary, thus labeling them as clones under broad semantic similarity.
- 共享行为: Opens an HTTP connection to a URL；Reads from the input stream
- 行为差异: A reads from multiple URLs, B from one；A discards all read data, B writes data to a file；A has a specific finally block to disconnect, B does not
- 修正建议: Improve model to recognize structural patterns of HTTP communication even with different processing.；Use dataflow analysis to identify common operations like opening connection and reading.；Consider token-level augmentation with API call sequences.

### case_id=2884 FN benchmark_preference_bias

- 方法: `main` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its entries to files.
- B 摘要: Converts an ACRNEMA stream file to DICOM format with UID generation and pixel data handling.
- 静态失败原因: The static model correctly identified the lack of semantic equivalence due to low token overlap (0.152) and distinct functionality. It failed relative to BCB because BCB's label appears erroneous or based on criteria outside semantic similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both being file-processing routines with similar I/O patterns, despite entirely different domains. The broad Type-4 interpretation might consider them as 'conversion utilities' but this is tenuous.
- 共享行为: Both open an input stream and process data sequentially.；Both use while loops to read data chunks.；Both write data to an output stream.；Both close streams in a finally-like manner.
- 行为差异: A handles ZIP extraction; B handles DICOM metadata and pixel data.；A reads from URL or file; B reads only from file.；A writes extracted files with their original names; B writes a single converted file.；B includes complex DICOM-specific validation and UID generation.
- 修正建议: Review BCB labeling guidelines to ensure consistency.；Consider excluding pairs with extremely low token similarity from clone annotations.；Use domain-specific filtering to avoid false positives from generic I/O functions.

### case_id=2885 FP lexical_or_api_overlap

- 方法: `writeFileType` vs `sendPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a file of URIs, opens each URI, checks for RDF ontology keywords in its content, and writes the classification to an output file.
- B 摘要: Sends an HTTP POST request with a parameter and returns the response as a string.
- 静态失败原因: The model likely overemphasized the lexical overlap of common API calls (URL, BufferedReader, etc.) and the boilerplate structure (try-catch, BufferedReaders), while missing the fundamental difference in purpose (file-type detection vs HTTP POST). The long code of A may have distracted the model from the key behavioral differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled these as non-clones (0) because the core functionality differs: one is for file type classification based on ontology keywords, the other is a generic HTTP POST client. The shared boilerplate (URL, BufferedReader, exception handling) is insufficient for a clone label under BCB's criteria, which favor overall functional similarity.
- 共享行为: Both use URL and URLConnection to interact with web resources.；Both use BufferedReader to read line by line from an input stream.；Both handle exceptions with try-catch blocks.
- 行为差异: A performs GET requests to read web pages; B performs a POST request with parameters.；A reads line numbers to skip lines, then processes each URI; B directly sends a POST to a single URL.；A writes output to a file; B returns a string result.；A checks for specific RDF vocabulary; B does not analyze content beyond reading lines.
- 修正建议: Train with more non-clone examples that share API calls but differ in data flow and output.；Incorporate control-flow and data-flow features to distinguish reading vs writing and different operation types.；Add heuristics to recognize when common libraries (java.net.URL, java.io.BufferedReader) are used for distinct tasks.

### case_id=2886 FP lexical_or_api_overlap

- 方法: `callService` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Makes an HTTP GET request to a constructed URL and stores the response as a string.
- B 摘要: Fetches a tile from a file or HTTP URL, parses the GeoJSON response into vector tile data, updates the data layer, and prevents duplicate requests.
- 静态失败原因: Static BERT/GraphCodeBERT models may focus on overlapping API usage (URL, BufferedReader, readLine) and common exception handling, ignoring the additional complex code in B that changes the overall behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when one function contains significantly more functionality (tile parsing, concurrency, data loading) beyond the shared simple HTTP fetch, making them functionally dissimilar even under broad Type-4 criteria.
- 共享行为: Both construct a URL, open an input stream, read lines into a string, and handle MalformedURLException and IOException.
- 行为差异: B includes duplicate request prevention via synchronized list.；B handles both file and HTTP protocols.；B parses the response into vector tile objects and updates data structures.；B is a public method overriding Runnable.run(); A is private.
- 修正建议: Incorporate data flow and side-effect analysis to distinguish simple fetch from complex processing.；Use method-level context (class, overriding) as a feature.；Require the model to consider the entire method body and not just common subsequences.

### case_id=2887 FP lexical_or_api_overlap

- 方法: `readReferenceText` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a reference text file from a plugin bundle and returns its content as a string.
- B 摘要: Loads a URL with optional authentication, reads its content, and writes it to a temporary file while updating a status label.
- 静态失败原因: The model likely overemphasized lexical/API overlap (URL, BufferedReader, readLine) without capturing the broader semantic differences in data flow and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions have different purposes and outputs: one returns text, the other writes to a file with UI updates.
- 共享行为: Both open a URL stream and read lines using BufferedReader.
- 行为差异: Function A returns the content as a string, while B writes to a file.；B includes authentication logic and updates a UI label.；A uses explicit UTF-8 encoding; B uses default encoding.；A catches multiple exceptions and throws NoContentException; B throws IOException only.
- 修正建议: Incorporate dataflow analysis to track how read data is used.；Consider return types and side effects to distinguish output purposes.

### case_id=2888 FP boilerplate_overlap

- 方法: `executePost` vs `lookupFutureEvents`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with URL parameters and returns the response body as a string.
- B 摘要: Retrieves future events from the Meetup API via HTTP GET, parses the JSON response, and returns a list of Event objects.
- 静态失败原因: The model likely focused on the common boilerplate pattern of opening a URL, reading with BufferedReader, and looping over lines, which appears in both functions. This structural overlap, combined with a lack of understanding of the overall purpose and output type, led to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the functionalities are entirely different: one is a generic HTTP POST utility, the other is a domain-specific event lookup. Even though both involve HTTP and I/O, the core logic and purpose are distinct.
- 共享行为: Both make HTTP requests (one POST, one GET) using java.net.URL；Both read the response with BufferedReader and InputStreamReader；Both handle exceptions with try-catch
- 行为差异: HTTP method: POST vs GET；Input: URL+parameters string vs group identifier+API key；Output: raw response string vs parsed list of Event objects；A writes data to output stream; B does not
- 修正建议: Enhance model with dataflow analysis to differentiate reading vs writing；Incorporate method name and signature information to capture intent；Use contrastive learning on functions with similar I/O patterns but different semantics

### case_id=2889 FN partial_functionality

- 方法: `getHTML` vs `setMembers`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a given URL and optionally saves it to a file.
- B 摘要: Fetches the new ticket page from a Trac instance and parses component and priority selections into class fields.
- 静态失败原因: Static BERT models like GraphCodeBERT rely heavily on token similarity and structural overlap; the low token Jaccard (0.177) and very different method signatures, variable names, and overall logic misled the model to classify as non-clone. The semantic similarity in the HTTP reading section is overshadowed by the larger syntactic differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions involve the common sub-pattern of fetching HTML via HTTP GET and reading it line by line, which is a non-trivial behavioral similarity, and BCB's broad Type-4 annotation may accept such partial functionality matches.
- 共享行为: Opens an HTTP connection to a URL；Reads the response line by line using BufferedReader
- 行为差异: getHTML returns the entire HTML string and can save to file; setMembers silently extracts specific XML-like elements and stores in arrays；getHTML is instance method with parameters; setMembers is static and uses getTracUrl() for URL；setMembers uses regex parsing with Recoder encoding; getHTML does no parsing；setMembers modifies class state; getHTML returns a value
- 修正建议: Train with more emphasis on partial functionality clones；Use dataflow or control flow alignment to highlight shared subroutines；Incorporate AST subtree matching for common patterns like HTTP connection setup

### case_id=2890 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens a version-check URL, reads lines to extract build version strings, then calls another method with the versions.
- B 摘要: Opens a URL with optional authentication, reads lines and writes them to a temporary file while updating a status label with the file size.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the overlapping API calls (URL, BufferedReader, readLine) and control flow, ignoring the different semantic contexts and post-processing steps.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically treats functions as non-clones when their high-level purpose differs, even if they share low-level I/O patterns. Here, one is a version checker, the other is a file downloader.
- 共享行为: Both open a URL and read lines via BufferedReader in a loop.
- 行为差异: Function A extracts version info from lines; function B writes lines to a file.；Function A shows/hides cursor and handles errors with dialog; function B throws IOException and updates a progress label.；Function A has no authentication; function B supports basic authentication.；Function A reads from a property-defined URL; function B takes URL as parameter.
- 修正建议: Incorporate data flow analysis to track how the read lines are used.；Use contrastive learning with negative pairs that share API calls but diverge in purpose.；Add task-level metadata or comments as features.

### case_id=2891 FN partial_functionality

- 方法: `doGet` vs `doCopyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles an HTTP GET request by retrieving a page, checking permissions, rendering it, and optionally caching the response to a file.
- B 摘要: Copies a file from source to destination using file channels, verifying size and optionally preserving the last-modified timestamp.
- 静态失败原因: Very low token Jaccard similarity (0.08) and different method names lead the static model to predict non-clone, as it relies on lexical overlap and does not capture the deep semantic difference.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: The BCB annotation likely considered the small file I/O sub-operation in A as partial functionality similarity with B's file copy, or possibly an annotation error given the extreme difference in overall purpose.
- 共享行为: Both involve file I/O operations (writing to a temp file vs copying a file).
- 行为差异: A is a web request handler; B is a file copy utility.；A uses HttpServletRequest/Response; B uses FileChannel.；A has complex permission and caching logic; B is straightforward copy.；A logs extensively; B does not log.
- 修正建议: Improve semantic understanding to differentiate primary functionality from incidental sub-operations.；Use code structure or data-flow analysis to focus on main behavior.；Incorporate method-level context (e.g., class, inheritance) to disambiguate.

### case_id=2892 FN benchmark_preference_bias

- 方法: `main` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies files from a source to multiple targets using NIO FileChannel, then optionally deletes or SVN deletes the source and prints status, exiting on error.
- B 摘要: Retrieves a resource via URL, caches it locally after checking for modifications, and returns an InputStream, with extensive error handling and printing.
- 静态失败原因: The static BERT model correctly captured the semantic dissimilarity due to low lexical overlap and different control flow structures, but the BCB benchmark label is overly broad, leading to a false negative relative to the benchmark.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to broad Type-4 similarity: both involve file reading/writing, error handling, and status printing, which some annotators might consider as 'file manipulation with error handling and printing', though the high-level purpose differs significantly.
- 共享行为: Both perform file I/O operations (reading/writing files, using streams).；Both use try-catch-finally for exception handling.；Both print status messages to System.out.
- 行为差异: A is a main method for copying files; B is a resource caching method returning an InputStream.；A uses NIO FileChannel.transferTo; B uses buffered streams and manual byte copying.；A handles multiple target files and deletion; B handles URL connections, caching, and cache validation.；A exits the program on failure; B returns null and closes streams.
- 修正建议: Refine BCB annotation guidelines to avoid labeling such semantically distinct functions as clones.；Increase token-level overlap thresholds for clone detection in datasets.

### case_id=2893 FN boilerplate_overlap

- 方法: `logging` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs an inbound message by copying content to a cached output stream and writing to a log buffer.
- B 摘要: Modifies a properties file for internationalization by replacing or adding a message key-value pair.
- 静态失败原因: Static BERT models may fail because of low token overlap (0.152) and different domain-specific APIs, focusing on method names and constants that are entirely distinct, missing the abstract I/O pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled as clone due to broad Type-4 similarity: both are I/O-heavy operations that read input, process it, and write output, with similar try-catch patterns.
- 共享行为: Perform file/stream I/O with error handling
- 行为差异: a logs message data; b modifies internationalization properties files；a uses CachedOutputStream and logging framework; b uses FileReader/Writer and BufferedReader；a writes to a log buffer; b writes to a .properties file
- 修正建议: Use data-flow or control-flow analysis to capture abstract I/O patterns；Increase training data with diverse I/O tasks；Incorporate structural similarity heuristics beyond token overlap

### case_id=2894 FN benchmark_preference_bias

- 方法: `convert` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Converts ACRNEMA DICOM files to standard DICOM format with pixel data processing.
- B 摘要: Builds HTML pages for site editing by transforming XML with XSLT and applying post-processing.
- 静态失败原因: Static model predicted non-clone correctly based on low token overlap and distinct semantics; the BCB label is likely erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have incorrectly labeled due to superficial similarity in file I/O and transformation patterns, but the functions serve completely different domains and purposes.
- 共享行为: Both read input files and write output files.；Both use loops and conditional logic.
- 行为差异: Function A processes medical image data; Function B processes web page templates.；Function A handles pixel data and DICOM tags; Function B handles XML, XSLT, and HTML generation.
- 修正建议: Re-examine BCB annotation for this pair; consider removing if domain mismatch is clear.；Improve clone detection by requiring higher functional similarity.

### case_id=2895 FN boilerplate_overlap

- 方法: `import_hints` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads hints from a file or URL and places puzzle pieces on a board.
- B 摘要: Invokes a remote service via HTTP POST, sends JSON arguments, and deserializes the JSON response.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on token-level similarity and captured common patterns (BufferedReader, try-catch) but missed the overall semantic difference because the functions are from different domains and have low lexical overlap. It predicted non-clone, which aligns with strict semantics but disagrees with BCB's broad preference.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider these as clones because both follow a pattern of reading external data (file or HTTP response) and processing it line by line / token by token, with error handling. The annotators might have focused on structural similarity rather than domain-specific behavior.
- 共享行为: Both use BufferedReader to read lines of text.；Both use try-catch blocks for IOException handling.；Both parse data from string tokens or lines.；Both involve loops over input lines.
- 行为差异: A is for placing puzzle pieces; B is for RPC invocation.；A returns boolean; B returns Object.；A reads from local file or URL; B makes HTTP POST request.；A does not handle retries; B has retry logic.
- 修正建议: Incorporate more semantic-level features to distinguish domain-specific logic.；Use code summarization to capture intent rather than just structure.；Include task-specific knowledge or API call sequences.

### case_id=2896 FN partial_functionality

- 方法: `getFile` vs `transferWSDL`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies the endpoint in the XML, and saves it to a temporary directory.
- B 摘要: Downloads a WSDL file from a URL with optional authentication and saves it to a configured temporary directory.
- 静态失败原因: The low token Jaccard (0.128) and different method names, parameters, and control flow caused the model to focus on syntactic differences and miss the underlying functional similarity. Static models struggle to capture long-range semantic correspondence when surface forms diverge.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: Both functions perform the core task of downloading a WSDL file from a URL and saving it to a local file, which is a common functionality in web service tools. BCB often considers such functional similarity as a clone, even with implementation differences (Type-4).
- 共享行为: Download a WSDL file from a URL；Save the downloaded content to a local file
- 行为差异: Code A modifies the WSDL content by changing the wsdlsoap:address location, while Code B does not modify content.；Code B handles HTTP authentication (Basic Auth), while Code A does not.；Different file naming: Code A uses serviceName.wsdl, Code B uses Wise<ID>.xml.；Different I/O implementations: Code A uses NIO channels, Code B uses IOUtils.copyStream.
- 修正建议: Use data augmentation with semantic-preserving transformations to train on functional similarity.；Incorporate additional features like data flow or program dependency graphs.；Employ contrastive learning on pairs with similar I/O behavior regardless of syntax.

### case_id=2897 FP lexical_or_api_overlap

- 方法: `run` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a file from the classpath as text and sets it in a GUI component.
- B 摘要: Downloads a file from a URL to a local file, reporting download progress.
- 静态失败原因: The model likely over-relied on lexical overlap of I/O and UI tokens (e.g., 'url', 'InputStream', 'BufferedReader', 'close', 'SwingUtilities') and the loop structure, ignoring the different semantics and output destinations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB expects non-clones for functionally different tasks; these functions serve entirely different purposes despite similar I/O patterns.
- 共享行为: Both open an input stream to read data；Both read data in a loop；Both close streams after use；Both update a GUI component after reading
- 行为差异: A reads text line-by-line; B reads bytes；A outputs to a GUI text area; B writes to a file；B tracks download progress; A does not；A uses classpath resource; B uses external URL
- 修正建议: Incorporate data flow analysis to track how data is used (file vs. GUI)；Add attention to method calls and their purposes；Use structure-based features to differentiate reading for UI display vs. file download

### case_id=2898 FP lexical_or_api_overlap

- 方法: `getDatasetsList` vs `readScalarpvviewerDocument`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches and caches a list of dataset names from a server URL.
- B 摘要: Reads and parses an XML configuration file from a URL to restore UI settings.
- 静态失败原因: The model overemphasized lexical and API overlap (BufferedReader, url.openStream, readLine) and ignored the drastically different logic and output types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label non-clone because the functions have entirely different purposes and outputs; the shared I/O pattern is generic and insufficient for semantic similarity.
- 共享行为: Both read lines from a URL using BufferedReader；Both handle IOException
- 行为差异: A returns a List<String>; B is void and updates UI；A caches results in a HashMap; B does not cache；A appends '?server=list' to URL; B expects XML format；A simply collects all lines; B parses XML to extract many fields
- 修正建议: Incorporate data flow and output type analysis；Use graph-based code representations to distinguish different data manipulations；Train on more diverse negative examples to reduce sensitivity to boilerplate

### case_id=2899 FN benchmark_preference_bias

- 方法: `main` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Extracts a KMZ file from a URL and writes its ZIP entries to disk.
- B 摘要: Builds a site for editing by reading XML, transforming it, and writing output files.
- 静态失败原因: Low token Jaccard (0.084) and very different code structure, method names, and lengths led the static model to predict non-clone, missing the broad I/O pattern similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both functions performing file I/O (reading from a stream and writing to files), considering high-level functional similarity despite vastly different implementations and complexity.
- 共享行为: Both involve reading from an input stream and writing to output files.
- 行为差异: A is a simple main method for archive extraction; B is a complex method with XML transformations, multiple file operations, and property handling.；A deals with a single URL stream and ZIP entries; B processes a list of pages, handles FTP, and uses external libraries.
- 修正建议: Incorporate functional abstraction or data-flow analysis to capture I/O patterns.；Use dynamic analysis or method summarization for high-level behavior matching.

### case_id=2900 FN benchmark_preference_bias

- 方法: `main` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Concatenates multiple input files into one output file using command-line arguments.
- B 摘要: Builds a website for editing by transforming XML and writing pages to output files.
- 静态失败原因: The static model likely relied on low token overlap and structural differences, correctly predicting non-clone; the BCB label may be an error or overly broad.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might label this a clone due to both involving file I/O operations in loops, but this is too broad; the specific semantics differ greatly.
- 共享行为: Both read from file sources and write to file outputs using loops and exception handling.
- 行为差异: A is a simple file concatenation with no transformation; B is a complex site builder involving XML transformations, multiple configuration parameters, and per-page output.
- 修正建议: Improve benchmark annotations to avoid overly broad clone labeling.；Train models to ignore trivial boilerplate similarities and focus on semantic equivalence.

### case_id=2901 FN partial_functionality

- 方法: `getFile` vs `getFileContentAsString`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.35`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies it by setting the endpoint attribute, saves it locally, and returns the file path.
- B 摘要: Reads a file from the classpath or filesystem and returns its contents as a string using a specified encoding.
- 静态失败原因: Low token Jaccard (0.106) and minimal lexical overlap; static models often miss semantically related but lexically divergent pairs, especially when functionality is partially similar but not identical.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as reading from a source and returning a string representation, but the specific purposes (WSDL download/modification vs generic file reading) are substantially different, and the return types differ. The annotation may be a broad Type-4 or a potential mislabel.
- 共享行为: Both open an input stream from a resource (URL or file/classpath).；Both read data and produce a string output (file path vs content).；Both handle I/O exceptions.
- 行为差异: A downloads from a URL and saves to disk; B reads a local resource or file.；A modifies XML content; B does not modify content.；A returns a file path; B returns the actual content.；A uses NIO channels; B uses IOUtils with streams.
- 修正建议: Use dataflow-aware models (e.g., GraphCodeBERT) to capture structural and semantic similarities.；Include more diverse examples of reading and processing file resources with different output forms.；Consider hierarchical or multi-granularity representations to abstract common I/O patterns.

### case_id=2902 FN partial_functionality

- 方法: `doTransfer` vs `addIDs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Proxies HTTP requests by forwarding headers and body between client and target URL.
- B 摘要: Scrapes a metabolite database website to retrieve IDs and sets them on a peak list row.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token overlap and API usage patterns; the low Jaccard (0.098) and distinct API sets (request/response vs. database-specific methods) led to a non-clone prediction, missing the broader network I/O similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered these as Type-4 (partial) clones due to shared network I/O boilerplate (URL opening, stream handling) and error handling patterns, despite differing functional purposes.
- 共享行为: Both use java.net.URL and HttpURLConnection to open HTTP connections.；Both read from input streams and write to output streams.；Both include try-catch for IOException and print errors.
- 行为差异: doTransfer forwards an entire HTTP request (headers, body) and returns the response; addIDs parses specific HTML content to extract metabolite information.；doTransfer is void and deals with HttpServletRequest/Response; addIDs returns an int score and modifies a PeakListRow object.；doTransfer handles all HTTP methods; addIDs performs only HTTP GET to a fixed base URL.；doTransfer prints debug output extensively; addIDs selectively parses and processes ID data.
- 修正建议: Incorporate data flow and control flow dependencies to distinguish high-level intent.；Use method name and return type as discriminators to avoid overgeneralizing network I/O patterns.；Enrich representation with context like class name or surrounding code to infer purpose.

### case_id=2903 FN benchmark_preference_bias

- 方法: `createTar` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Creates a tar archive from a given directory, writing each file into a TarOutputStream.
- B 摘要: Launches a NexOpen project by configuring Maven pom files and handling Hibernate reverse engineering.
- 静态失败原因: The static BERT/GraphCodeBERT model did not fail; it correctly predicted non-clone (0) due to low token overlap and divergent semantics.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB presumably labeled this as clone erroneously, possibly due to a mistake in the benchmark annotation process.
- 行为差异: Function A performs file archiving; function B performs Eclipse project launch configuration.；Function A uses TarOutputStream and FileInputStream; function B uses Eclipse APIs and Maven pom.xml handling.；Their I/O operations, libraries, and control flow are completely different.；No common logical steps or data transformations.
- 修正建议: Review and correct the BCB annotation for this pair.；Ensure benchmark labels match semantic equivalence criteria.

### case_id=2904 FN partial_functionality

- 方法: `getHTML` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A utility method that fetches HTML content from a URL via HTTP GET and optionally writes it to a file.
- B 摘要: A method that opens an HTTP connection to retrieve and parse an OPDS catalog feed or download a book, with pagination and error handling.
- 静态失败原因: Static BERT models like GraphCodeBERT rely heavily on token overlap and structural similarity. The low Jaccard similarity (0.1287) and the presence of distinct GUI, parsing, and pagination logic in function B (which is truncated) cause the model to perceive them as entirely different. The model fails to abstract away the non-core differences and misses the shared HTTP connection skeleton.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB human annotators often classify pairs as clones if they share the core functionality of fetching content over HTTP, even if one is significantly simpler or more complex. The common pattern of opening a connection, setting headers, reading data, and cleaning up is considered sufficient for partial functionality similarity (Type-3/4).
- 共享行为: Both open an HTTP connection using HttpURLConnection；Both set a User-Agent request header；Both read from the input stream of the connection；Both close the connection in a finally block
- 行为差异: Function A simply reads all lines and returns HTML string; function B processes content type to either parse XML feed or download a file；Function B has complex logic for pagination, redirects, timeouts, progress reporting, and callback execution; function A is simpler；Function A supports optional file writing; function B does not write to a file directly but downloads as book；Function B handles HTTPS rejection and sets additional headers (Referer, follow redirects, etc.)
- 修正建议: Train models to focus on critical API call sequences (e.g., URL.openConnection, setRequestProperty, getInputStream, disconnect) rather than overall token distribution；Use dataflow analysis or program slicing to isolate the HTTP interaction parts；Incorporate domain-specific knowledge (e.g., web fetching) to generalize simpler vs. complex implementations

### case_id=2905 FN partial_functionality

- 方法: `runScript` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from a URL relative to the applet codebase and returns its content as a string, returning 'error!' on exception.
- B 摘要: Reads data from a file or URL and returns an integer status code, with error handling for IOException.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on lexical and API-level similarities (e.g., BufferedInputStream, URL) but failed to capture the different return types (String vs int) and distinct reading logic (loop vs delegated read), leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both methods perform a similar high-level task of reading data from an external source (URL or file) with BufferedInputStream and error handling, albeit with different return types and reading strategies, fitting broad Type-3/Type-4 similarity.
- 共享行为: Both open an input stream from a URL or file using BufferedInputStream.；Both handle exceptions and return a special value on error.
- 行为差异: Method A returns the full content as a String; method B returns an integer status code.；Method A reads byte-by-byte in a loop; method B delegates reading to another method.；Method A only accepts URLs relative to codebase; method B accepts absolute URLs and file paths.；Exception handling: A catches generic Exception; B catches IOException.
- 修正建议: Incorporate explicit data-flow analysis to track return type and output usage.；Use training data that includes more diverse return types and partial functionality clones.；Consider graph-based models that better represent control flow and data dependencies.

### case_id=2906 FP lexical_or_api_overlap

- 方法: `downloadURLtoString` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a URL and returns its content as a single concatenated string.
- B 摘要: Loads a FrameworkFactory from a service resource file, returning an instance of the class specified in the first non-comment line, or throws an exception.
- 静态失败原因: The model likely over-relied on lexical overlap (e.g., common pattern of URL.openStream, BufferedReader, readLine loop) and ignored the distinct return types, different processing logic, and overall functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires high functional similarity; here although the code structure is similar (URL reading loop), the outputs and purposes are entirely different, so BCB correctly labels as non-clone.
- 共享行为: Both use URL.openStream() and BufferedReader to read from a URL line by line；Both close the BufferedReader after reading
- 行为差异: Function A returns a String (content of the URL); function B returns a FrameworkFactory object；Function B includes error handling (throws Exception if no factory found); A throws IOException but not on missing data；Function B processes lines: trims, ignores comments, and uses the first valid line to instantiate a class; A simply appends all lines
- 修正建议: Incorporate dataflow analysis to track return types and transformations；Use contrastive training to penalize false positives with similar structure but different semantics；Add structural information like method signature and exception handling patterns

### case_id=2907 FP boilerplate_overlap

- 方法: `addDataFromURL` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads text from a URL and appends it line by line to a StringBuilder field.
- B 摘要: Downloads an RDF model from a URL by opening an HTTP connection and reading the model data into a Model object.
- 静态失败原因: Static BERT may have overemphasized common token patterns like 'InputStream', 'URL', 'try-catch', 'close', leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically treats functions with different output types and purposes as non-clones; despite similar URL reading boilerplate, the core functionality differs (text vs RDF model).
- 共享行为: Open an InputStream from a URL；Read data from the stream；Close the stream
- 行为差异: Output: appends text to StringBuilder (A) vs returns a Model object (B)；Error handling: prints error and appends URL (A) vs logs and throws RuntimeException (B)；Network setup: just openStream (A) vs HTTP connection with headers (B)；Data parsing: reads lines (A) vs reads RDF model (B)
- 修正建议: Incorporate structural features like data flow graphs or control flow graphs；Use function-level embedding that captures output type and purpose；Add negative sampling on boilerplate-heavy pairs

### case_id=2908 FP boilerplate_overlap

- 方法: `sendRequest` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP request with compressed XML payload and parses the response into a JDOM document, returning an empty string.
- B 摘要: Fetches a YouTube video page, parses it to extract video ID and timestamp, constructs a fullscreen URL, and returns it.
- 静态失败原因: The model likely focused on the common sequence of opening a URL, setting properties, and reading input, which are standard Java networking patterns. This boilerplate overlap outweighed the divergent overall logic, causing a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers non-clone because the core functionality differs fundamentally: one is a generic HTTP request sender with XML handling, the other is a specific YouTube URL extractor. The shared URL connection boilerplate is insufficient for functional similarity.
- 共享行为: Both open a URLConnection and read from an input stream.；Both print debug information to System.out.；Both handle exceptions with catch blocks.
- 行为差异: Function A sends a request (writes compressed XML), while B only reads.；Function A uses Preferences and a dialog to get server settings; B uses a class field ytUrl.；Function A returns an empty string; B returns a constructed URL.；Function A builds a JDOM document; B parses plain text lines for specific patterns.
- 修正建议: Incorporate data flow analysis to track what data is written/read and how it is processed.；Include structure-aware features that distinguish sending vs. receiving data.；Train with more examples where similar boilerplate wraps different core behavior.

### case_id=2909 FP lexical_or_api_overlap

- 方法: `setBundleInfoName` vs `getUser`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Updates bundle names in a list by parsing lines from a URL resource with '=' delimiter.
- B 摘要: Loads a user from a DAO or parses a config file to create a user object if login matches.
- 静态失败原因: Static model likely over-emphasized surface-level similarities like BufferedReader, while loop, and token overlap, while missing the distinct domain logic and method purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as not clone because the overall functionality and input/output semantics are different, despite some structural similarity in reading and parsing.
- 共享行为: Reads input line by line using BufferedReader；Parses each line using a delimiter；Uses try-catch for exception handling；Loops until end of input
- 行为差异: Function A modifies an existing list, while B creates and returns a new object；A uses remote URL, B uses classpath resource；A updates multiple entries, B creates at most one user；Different delimiters and parsing logic
- 修正建议: Incorporate dataflow analysis to capture variable dependencies and transformations；Use method name and signature as features；Apply contrastive learning to distinguish similar structure with different semantics

### case_id=2910 FN partial_functionality

- 方法: `httpRequestByPOST` vs `retrieveTemplate`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with parameters and reads the response body into a string, handling HTTP status codes and exceptions.
- B 摘要: Retrieves the content from a URL using a GET request, caches the result, and returns it as a string without explicit error handling.
- 静态失败原因: The low token Jaccard (0.2) and different API usage (HttpClient vs URL) cause static BERT to focus on distinct tokens, missing the shared structural pattern of reading lines from a stream.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider both as 'reading content from a URL' and ignore differences in HTTP method, parameter handling, and error handling due to broad Type-3/Type-4 criteria, but the low token overlap (0.2) and distinct functionalities make this unlikely.
- 共享行为: Both read from a URL and accumulate lines into a string using BufferedReader
- 行为差异: HTTP method: POST vs GET；Parameter handling: A sends form parameters; B does not；Error handling: A explicitly checks status code and catches IOException; B throws generic Exception；Caching: B caches the result; A does not
- 修正建议: Improve representation to capture abstract patterns like 'read from URL into string' even with different libraries；Use graph-based models to align control flow and data flow of input/output operations

### case_id=2911 FP boilerplate_overlap

- 方法: `getDatasetsList` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a list of dataset names from a URL, caching results in a map.
- B 摘要: Queries a ticket tracking system for open tickets in a queue and retrieves each ticket's details.
- 静态失败原因: The model overemphasized structural patterns common in HTTP clients (open stream, read lines, try-catch) and failed to capture the semantic distinction in the data being fetched and the surrounding logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the overall purpose and domain differ significantly, despite sharing low-level I/O boilerplate. The functionality is not semantically similar enough for a Type-4 clone.
- 共享行为: Both make HTTP requests and read responses line by line.；Both use BufferedReader and handle IOExceptions.；Both accumulate results into a list.
- 行为差异: Different source systems: datasets URL vs REST API for ticket tracking.；Different return types: List<String> vs List<RTTicket>.；Function A caches results; function B does not.；Function A uses synchronized; function B does not.
- 修正建议: Incorporate method name semantics and return type analysis.；Use API endpoint and parameter awareness.；Train on more diverse data to reduce boilerplate bias.

### case_id=2912 FN partial_functionality

- 方法: `copyResource` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a local file using byte-by-byte streaming.
- B 摘要: Downloads a ZIP file from a URL and extracts its entries to individual files using ZipInputStream and buffered streams.
- 静态失败原因: The low token Jaccard (0.263) and different method names ('copyResource' vs 'main') led to low surface similarity. Static BERT/GraphCodeBERT relies on lexical and syntactic overlap, missing the shared abstract I/O behavior due to structural differences (e.g., ZipInputStream, multiple output files).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both implement a core pattern of reading from an input stream and writing to an output file, which is a common Type-3/Type-4 clone in BigCloneBench, even though the specific file formats and number of files differ.
- 共享行为: Both read from an input stream and write to an output file using a byte copy loop.
- 行为差异: Function A copies a single source to one destination; function B extracts multiple entries from a ZIP archive.；Function A uses unbuffered streams; function B uses buffered streams and handles ZIP compression.；Function A is a private method; function B is a main method with fixed URL and file handling.
- 修正建议: Incorporate dataflow analysis to capture core I/O patterns independent of specific APIs.；Train on more diverse examples of stream copy with varying file formats to learn the essential copying semantics.；Use graph neural networks that model control and data flow to identify similar loop structures.

### case_id=2913 FP lexical_or_api_overlap

- 方法: `get` vs `getXML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Method A sends an HTTP GET request with custom headers, reads the response line by line, skips comment lines, decodes each line into GameRecord objects, and returns an array of GameRecord.
- B 摘要: Method B sends an HTTP GET request to a servlet, reads the response line by line, appends all lines to a StringBuffer, and returns the concatenated string as raw XML.
- 静态失败原因: Static BERT/GraphCodeBERT models likely relied on surface-level similarities such as common API usage (URL, BufferedReader, while loop reading lines) and similar control flow structure, overlooking the critical differences in data processing and return type.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when methods have different return types and perform distinct data processing, even if they share the common pattern of HTTP GET and line-by-line reading. The functionality is not semantically equivalent nor a simple transformation.
- 共享行为: Both methods perform an HTTP GET request；Both read the response line by line using BufferedReader；Both return null or handle exceptions by returning null/printing
- 行为差异: Return type differs: GameRecord[] vs String；Method A sets custom headers (latitude, longitude, count); method B does not；Method A parses lines into GameRecord objects; method B returns raw concatenated text；Method A skips lines starting with '#'; method B does not
- 修正建议: Train model to distinguish between generic boilerplate code and task-specific logic；Incorporate type information and method signatures more explicitly；Use contrastive learning with functional similarity metrics beyond token overlap

### case_id=2914 FN partial_functionality

- 方法: `doGet` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request for displaying a portal page, including permission checks and optional caching of rendered output to a file.
- B 摘要: Copies files from a source directory to multiple target directories, with optional SVN operations and deletion of old files.
- 静态失败原因: Static BERT models like GraphCodeBERT rely heavily on lexical and structural similarity. With token Jaccard of 0.101, the lexical overlap is minimal. However, the model might have been confused by the low overlap and correctly predicted non-clone, but the BCB label is uncertain. The misclassification might be due to the model's inability to see the high-level structural similarity that BCB annotators might infer.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider this a clone because both functions have a similar structure of try-catch-finally with resource management, and both involve file operations. The truncated part of doGet includes file caching which resembles file copy, potentially leading annotators to see partial functional similarity.
- 共享行为: Both perform file I/O operations；Both handle exceptions and log errors；Both have conditional logic based on input
- 行为差异: One is a web servlet reacting to HTTP request, the other is a standalone file copy utility；One uses portal domain objects (Page, Property), the other uses file system APIs；One outputs HTML, the other outputs file bytes；One handles user permissions, the other handles file deletion
- 修正建议: Improve representation of high-level control flow and resource management patterns；Use contrastive learning to distinguish between truly similar partial functionality and coincidental structural overlap

### case_id=2915 FN benchmark_preference_bias

- 方法: `setMembers` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Parses HTML from a Trac newticket page to extract component and priority options, populating static arrays.
- B 摘要: Registers a new user by encoding password, setting default authority, generating email hash, calling a PHP forum registration URL, persisting user, and sending confirmation email.
- 静态失败原因: The static model correctly identified the functions as non-clones based on low token overlap (0.11465) and distinct semantics; it failed to align with BCB's annotation because BCB's clone definition may be overly broad in this case.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to both functions involving HTTP requests and setting internal state, but the specific purposes are entirely different, making this a questionable Type-4 clone under broad interpretation.
- 共享行为: Both use URL, BufferedReader, InputStreamReader for HTTP communication；Both handle IOException with error logging or printing；Both perform some string manipulation；Both may set fields (but different fields)
- 行为差异: Function A extracts options from HTML select elements; Function B performs user registration including password encoding and database persistence；Function A is static and returns void; Function B is non-static and returns boolean；Function A populates two static string arrays; Function B persists a User entity；Function A catches MalformedURLException explicitly; Function B catches NumberFormatException
- 修正建议: Review BCB annotation guidelines to ensure consistency with semantic equivalence；Train models with clearer distinction between Type-4 clones and non-clones；Incorporate more complete data-flow and intention analysis to avoid overmatching on API usage

### case_id=2916 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks and anchor text from an HTML page given a URL, returning two vectors.
- B 摘要: Fetches a GeoJSON tile from a URL, parses it into geometric features, and adds them to a data loader for map rendering.
- 静态失败原因: The model likely overfitted to structural and lexical overlap (URL, BufferedReader, while loop) without capturing the distinct domain semantics and output types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functional similarity beyond generic I/O patterns; these two functions perform entirely different domain-specific tasks (link extraction vs. tile loading), so they are non-clones even under broad Type-3/4 criteria.
- 共享行为: Both open a URL and read lines from the input stream；Both use BufferedReader and InputStreamReader
- 行为差异: Different input/output: A returns links and texts; B processes tile data for display；Different parsing logic: A uses regex for anchor tags; B parses JSON into vector geometries；Different side effects: A has none; B updates data loader and layer cache
- 修正建议: Enhance training data with more negative pairs that share boilerplate but differ in core logic；Incorporate data flow analysis to highlight differences in variable usage and output；Use contrastive learning to distinguish superficial similarity from semantic equivalence

### case_id=2917 FN benchmark_preference_bias

- 方法: `saveProject` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Saves a 3D project to a zip file, including version info, databases, images, trajectories, and XML representations of layers.
- B 摘要: Builds a web site from a page set, applying XSLT transformations and adding control/menu content.
- 静态失败原因: The static model correctly identified the low token overlap (Jaccard=0.075) and distinct syntactic structures, leading to a correct non-clone prediction. The discrepancy arises from a likely erroneous BCB annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to a focus on general file-writing functionality and presence of loops that write multiple files, but this is a very broad interpretation that likely goes beyond intended clone types.
- 共享行为: Both perform file I/O operations to create output files.；Both handle exceptions and may write multiple files.；Both involve some form of XML or structured data processing.
- 行为差异: Different domains: 3D visualization vs web site generation.；Different data structures: file-based project vs page-based site.；Different processing steps: copying databases, writing tracks vs XSLT transforms, string replacements.；Different input parameters and output formats.
- 修正建议: Re-evaluate BCB annotation for this pair; consider removing or correcting the clone label.；Improve training data quality by filtering such low-similarity pairs.

### case_id=2918 FP lexical_or_api_overlap

- 方法: `importRoles` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Imports roles by reading an XML file from a URL, parsing RoleName elements, and returning a list, with exceptions silently swallowed.
- B 摘要: Downloads an RDF model from a URL by opening a connection with HTTP headers, reading the model from the input stream, and returns it, wrapping exceptions in RuntimeException.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by shared lexical tokens (e.g., URL, MalformedURLException, IOException, try-catch blocks) and the structural pattern of opening a URL and reading input, causing it to overlook semantic differences in parsing and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions perform fundamentally different operations (XML role parsing vs RDF model download) with distinct outputs and error handling, despite both involving URL I/O.
- 共享行为: Both open a URL and read data from the network.；Both handle MalformedURLException and IOException.
- 行为差异: Different return types: ArrayList<RoleName> vs Model.；Different data parsing: XML line-by-line parsing vs RDF model reading.；Different error handling: silent ignoring vs logging and rethrowing as RuntimeException.；Function B adds HTTP request headers; A does not.
- 修正建议: Incorporate type information for return types and method names.；Add attention to the specific parsing or processing logic inside the loop.；Use contrastive learning to distinguish between similar I/O patterns with different semantics.

### case_id=2919 FP long_range_semantics

- 方法: `actionPerformed` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles UI actions for setting file paths for GraphViz, ImageMagick, and other preferences.
- B 摘要: Downloads all files from a Hadoop filesystem directory to a local output stream.
- 静态失败原因: The model likely failed due to the long length of function A (truncated) and the presence of common programming patterns (loops, try-finally, I/O calls), which caused it to overlook the fundamental difference in functionality. The low token Jaccard suggests the model relied on structural rather than semantic similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labeled non-clone (0) because the functions have no semantic similarity in purpose or behavior; they are from entirely different domains (GUI settings vs. file download).
- 共享行为: Both use loops to iterate over collections or arrays.；Both have try-finally blocks for resource management.；Both use conditional statements to handle different cases.
- 行为差异: Function A is a GUI event handler with JFileChooser and preference storage; Function B is a command-line file download utility.；Function A operates on local files and user preferences; Function B operates on a distributed filesystem (Hadoop) and writes to a local file.；Function A involves user interaction and multiple configuration options; Function B has a straightforward sequential file copy.；The control flow and data dependencies are completely different.
- 修正建议: Use a model that captures long-range dependencies more effectively, such as a transformer with positional encoding for longer sequences.；Incorporate data flow analysis or control flow graphs to better understand the program's behavior.；Include method signature and class context to disambiguate purpose.

### case_id=2920 FN partial_functionality

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file using byte-by-byte stream copying.
- B 摘要: Copies a file to another file using FileChannel transferTo for efficient transfer.
- 静态失败原因: Static BERT models rely heavily on token overlap and API surface; here token Jaccard is low (0.204) and APIs differ (FileChannel vs InputStream), causing the model to miss the high-level semantic equivalence.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as implementations of file copying despite different I/O APIs, focusing on the core functionality of copying from source to destination.
- 共享行为: Both copy content from a source to a destination file.；Both involve opening input and output streams/channels.；Both ensure resources are closed after copying.
- 行为差异: copyResource can read from a URL or file, while copyFile takes only file paths.；copyResource uses InputStream/OutputStream and reads byte-by-byte; copyFile uses FileChannel and transferTo for bulk transfer.；copyResource throws Exception, copyFile throws IOException.；copyResource uses a method destinationFile() for output; copyFile takes destination as parameter.
- 修正建议: Incorporate dataflow analysis to track bytes transferred.；Abstract I/O operations to recognize common patterns like 'copy'.；Use functional similarity measures beyond token overlap.

### case_id=2921 FP boilerplate_overlap

- 方法: `lookupFutureEvents` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches and parses event data from Meetup API, returning a list of Event objects.
- B 摘要: Fetches and parses image URLs from Google Image Search, adding them to a list.
- 静态失败原因: The static model likely focused on the shared boilerplate pattern (URL connection, buffered reader, while loop, exception handling) and ignored the distinct domain-specific logic and output, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires semantic equivalence in the overall task; these two functions serve entirely different purposes, so they are not considered clones.
- 共享行为: Both open a URL, read response line by line, and handle IOException with try-catch.
- 行为差异: Different API endpoints and parameters；Different response parsing (JSON vs HTML)；Different output (return list vs void with side effects)；Different conditions (artist comparison in B)
- 修正建议: Introduce more discriminative features that capture the actual data processing and output semantics；Use data flow analysis to distinguish between different API calls and output types；Include context about method names and class structures

### case_id=2922 FP other

- 方法: `logging` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs inbound message details including encoding, headers, and content up to a size limit.
- B 摘要: Handles GUI action events to set various application preferences like file paths, fonts, look-and-feel, etc.
- 静态失败原因: The static model likely overfitted to common API call patterns (e.g., using 'getInputStream', 'logger', etc.) or misinterpreted generic method signatures, ignoring the surrounding context of completely different application domains.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels non-clones because the functions have completely different purposes and no shared functionality.
- 行为差异: Function A is a logging utility; Function B is a GUI event handler for preference settings.；Function A deals with I/O streams and log messages; Function B manipulates UI components and stores preferences.；Function A uses a logger; Function B uses JFileChooser, JOptionPane, and UIManager.
- 修正建议: Include more diverse non-clone pairs with different domain contexts.；Use contrastive learning to better distinguish between distinct functionalities.；Incorporate structural or data-flow information to capture semantic differences.

### case_id=2923 FP lexical_or_api_overlap

- 方法: `wordFrequency` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Counts word frequency by downloading a web page and parsing a line with a regex pattern.
- B 摘要: Downloads an RDF/XML model from a URL and reads it into a Model object.
- 静态失败原因: Static BERT may overemphasize lexical overlap (common tokens like URL, MalformedURLException, IOException) and structural similarity of try-catch blocks, ignoring distinct return types and core logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the core functionality differs significantly despite shared boilerplate; BCB requires functional similarity beyond common API usage.
- 共享行为: Both open a URL connection and read input；Both handle MalformedURLException and IOException
- 行为差异: Different return types: int vs Model；Different input handling: regex line matching vs RDF model reading；Different error handling: print stack trace vs throw RuntimeException；Resource management: A does not close stream, B closes stream
- 修正建议: Incorporate data flow analysis to track variable types and transformations；Use method name embeddings to capture intention；Add control flow graph features to differentiate exception handling patterns

### case_id=2924 FN partial_functionality

- 方法: `getFile` vs `resolvePlugins`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its soap:address element, and saves it to a temp directory, returning the file path.
- B 摘要: Downloads a plugins.xml file from a URL if not cached, saves it to a local cache directory, and then resolves plugins.
- 静态失败原因: Static BERT models rely on token-level similarity and may not capture the shared high-level workflow due to low lexical overlap (Jaccard=0.078) and long code lengths. The model likely focused on surface differences (method names, APIs) and missed the underlying structural similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB labels these as clones because both implement a common core pattern: check if a file exists locally, if not, download from a URL. Despite different details, the essential workflow is considered similar under broad Type-3/Type-4 criteria.
- 共享行为: Both check if a local file exists before downloading; if not, they download a remote file via URL and write it to the local filesystem.
- 行为差异: Function A modifies the downloaded XML file (changes an attribute) while B does not.；Function A returns a file path; B is void.；Function A is static; B is not.；Exception handling differs: A throws AxisFault after logging; B prints stack trace.
- 修正建议: Use AST-based or dataflow analysis to detect common patterns like file existence check + download.；Incorporate code summarization or program slicing to focus on core functionality.；Improve handling of long-range dependencies in Transformer models.

### case_id=2925 FN partial_functionality

- 方法: `readGeoParserResult` vs `readURL`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses a record content to query a geo-parser web service and extract place names and gazetteer IDs.
- B 摘要: Reads the content of a URL and prints each line to standard output.
- 静态失败原因: Static BERT models like GraphCodeBERT may have missed the clone because although there is lexical overlap in the URL reading code, the overall function structure, purpose, and output are very different, leading the model to predict non-clone. The model may not capture the semantic alignment of the shared sub-task.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely marked this as a clone because both functions share a common sub-pattern: opening a URL stream and reading lines with BufferedReader. Despite high-level purpose differences, BCB may accept Type-3 or Type-4 similarity for overlapping code fragments.
- 共享行为: Both open a URL connection and read lines using a BufferedReader；Both use while loops to read lines until null
- 行为差异: Function A creates an XML request and sends it to a specific geo-parser service, while B just reads from any URL；Function A parses the response XML to extract specific data (place names and IDs) and returns a collection, while B prints lines and returns void；Function A has retry logic (3 attempts) and a testing shortcut, B has none；Function A uses error logging and console output, B uses print stack trace and stream closing
- 修正建议: Improve detection of partial functionality clones by using models that can align subroutines or API usage patterns；Use dataflow or program slicing to focus on overlapping code regions

### case_id=2926 FN partial_functionality

- 方法: `init` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Initializes servlet by loading controller class names from registry files on classpath.
- B 摘要: Invokes a remote service method via HTTP POST, processes response, and handles retry on timeout.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token similarity and API call patterns. The token Jaccard similarity is very low (0.14), and the APIs used are completely different (class loading vs HTTP). The model did not capture the high-level procedural similarity of reading lines, which may be considered a deeper functional similarity in BCB. Models lack understanding of abstract behaviors like 'stream reading'.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider these clones due to shared patterns of reading streamed input line-by-line and handling exceptions, which are common boilerplate in many Java methods that process external resources. The annotators may have focused on the procedural similarity of reading and processing lines, overlooking the domain differences.
- 共享行为: Reads from an input stream using BufferedReader and InputStreamReader；Processes input line by line in a while loop；Logs debug and error information；Catches and handles exceptions
- 行为差异: Function A loads Java classes from classpath resources; Function B makes HTTP requests to a remote service；Function A is a one-time initialization; Function B is designed to be called multiple times with potential retries；Function A uses class loading and registry; Function B uses HTTP client and JSON serialization
- 修正建议: Enhance model with control flow graph or abstract syntax tree similarity to capture structural patterns like loops and streams；Use data flow analysis to track that both functions read from a stream and produce output；Incorporate comment and method name context to infer high-level purpose

### case_id=2927 FN lexical_or_api_overlap

- 方法: `login` vs `createDialogArea`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs HTTP login to LOLA, sends POST request with email and password, reads response to extract session ID, and returns it.
- B 摘要: Creates a SWT dialog area, reads a license file from the bundle, displays its content in a browser or text widget, and returns the composite.
- 静态失败原因: Static BERT/GraphCodeBERT models might have been misled by overlapping API usage (URL, InputStreamReader, BufferedReader, readLine) and boilerplate exception handling, despite low token Jaccard.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as a false positive clone due to lenient criteria considering both involve I/O operations with URLs and line-by-line reading, but it's likely an annotation error.
- 共享行为: Both use URL to access a resource；Both use BufferedReader and InputStreamReader to read data line by line；Both handle IOException and close streams in finally blocks
- 行为差异: A sends HTTP POST request with output; B only reads input from a local resource；A encodes parameters and writes data to URLConnection; B creates GUI components；A returns a session ID string; B returns a Control object；A sets session state; B sets dialog title and message
- 修正建议: Incorporate semantic role labeling to differentiate data flow (output vs input)；Use structured representation of method purpose (e.g., control-flow graph with I/O direction)；Enhance training with more diverse negative examples having similar boilerplate but different goals

### case_id=2928 FN boilerplate_overlap

- 方法: `scrapeForIsbns` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Scrapes ISBN-10 numbers from a web page by reading HTML lines and matching a regex, with retry logic and error handling.
- B 摘要: Registers a User object by setting properties, making an HTTP request to a forum for user creation, persisting to database, and sending a confirmation email.
- 静态失败原因: The static model correctly focused on low token overlap and different high-level functionality, but it failed to align with BCB's possibly overbroad annotation that considers boilerplate code as a clone indicator.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as a clone due to the shared I/O boilerplate (URL, BufferedReader, exception handling) and the fact that both involve network communication and line-by-line reading, which could be considered a functional similarity under a very broad Type-4 definition.
- 共享行为: Both functions use URL connections to read data from remote servers.；Both use BufferedReader to read lines of text.；Both handle IOException with logging.；Both use logging for debug/error messages.
- 行为差异: Function A returns an integer count of matches; Function B returns a boolean success status.；Function A has retry logic on connection failure; Function B does not retry.；Function A performs regex matching for ISBNs; Function B reads a numeric forumID from the response.；Function A does not modify persistent state; Function B modifies and persists a User object to the database.
- 修正建议: Improve training data to exclude pairs with only common I/O patterns but no functional similarity.；Incorporate higher-level semantic analysis to distinguish between different application domains.；Use control flow and data flow graphs to capture functional behavior beyond surface-level API usage.

### case_id=2929 FN partial_functionality

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to disk.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: The static model likely focused on token-level semantics (low Jaccard similarity) and did not capture the abstract I/O-heavy nature that might have been annotated as a type-4 clone in BCB.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones if considering broad 'file copying' functionality despite different input sources and algorithms, or if the annotator focused on the common I/O usage (streams, channels) as a partial functionality clone.
- 共享行为: Both perform file I/O operations；Both write to output streams/channels
- 行为差异: A reads from a URL stream, B reads from a local file；A extracts multiple files from a zip archive, B copies a single file；A uses ZipInputStream and individually writes each entry, B uses FileChannel.transferTo for bulk copy
- 修正建议: Include data augmentation that mixes file I/O patterns across different input sources；Use contrastive learning with pairs that share I/O structure but differ in detailed operation

### case_id=2930 FP lexical_or_api_overlap

- 方法: `main` vs `CopyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file and generates adapter classes and resources into a JAR file.
- B 摘要: Copies a file from source to destination using FileChannel, creating parent directories if needed.
- 静态失败原因: Static BERT likely focused on overlapping tokens like 'File', 'IOException', 'System.out', and 'catch' blocks, ignoring the vastly different control flow and domain-specific logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they implement entirely different functionalities (generator vs. file copy), despite sharing some low-level I/O operations.
- 共享行为: Both handle file paths and use File class；Both can throw IOException；Both use System.out for error messages；Both involve reading or writing files
- 行为差异: Function A is a complex Prolog-to-Java adapter generator; B is a simple file copy；A processes Prolog source and generates multiple classes; B only copies bytes；A has a command-line interface; B is a helper method；A uses JarEntryWriter, ClassWriter, ObjectOutputStream; B uses FileChannel
- 修正建议: Train with more diverse non-clone pairs that share API usage but differ in intent；Incorporate structural or dataflow analysis to distinguish file-copy from code generation；Use contrastive learning with hard negative examples involving common frameworks

### case_id=2931 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a resource file line by line, parses each line as integer, and returns a set of integers.
- B 摘要: Reads version information from a URL, extracts version/build strings, and displays an update message if a newer version is available.
- 静态失败原因: The model likely over-relied on common tokens like 'URL', 'openStream', 'InputStreamReader', 'readLine', causing false positive; lacks understanding of overall program semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functional purpose is completely different: one parses zone IDs, the other checks version; despite shared I/O boilerplate, the semantic intent and data processing are distinct.
- 共享行为: Both open a URL/stream；Both read lines in a loop；Both use standard input stream reading
- 行为差异: Different input sources (class resource vs URL)；Different parsing logic (parseInt vs string prefix check)；Different output (HashSet of integers vs UI message)；Error handling differs (Exception vs IOException, stack trace vs GUI error)
- 修正建议: Incorporate method names and variable names more strongly；Train with more negative examples that share API but differ in semantics；Use control flow and data flow analysis to distinguish purposes

### case_id=2932 FN partial_functionality

- 方法: `readAndRewrite` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a DICOM file, parses it, and writes pixel data to a new file.
- B 摘要: Retrieves a resource via URL, caches it locally, and returns an InputStream.
- 静态失败原因: Static BERT likely focused on low token overlap and specific APIs, missing the abstract I/O pattern similarity that BCB annotators considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones due to shared high-level I/O operations and stream handling, which fits broad Type-3/4 criteria despite domain differences.
- 共享行为: Both perform file I/O using buffered streams；Both handle IOException with try-catch；Both print status messages
- 行为差异: Different data formats (DICOM vs arbitrary resource)；Different input sources (local file vs URL)；Function B includes caching and HTTP logic absent in A
- 修正建议: Train on more I/O-intensive examples；Enhance model with abstract operation detection；Use data augmentation with similar stream patterns

### case_id=2933 FP partial_functionality

- 方法: `readZoneIDs` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file containing zone IDs (one integer per line) into a HashSet.
- B 摘要: Imports sequences from a URL in FASTA format, extracting names and sequences into class fields.
- 静态失败原因: The model may have been misled by overlapping patterns such as try-catch blocks, while loops reading lines, and collection addition, overlooking the fundamental differences in data format and output semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled as non-clone because the functions serve different purposes (zone ID extraction vs sequence import) and have distinct parsing logic and output types, despite both involving reading from a stream.
- 共享行为: Both open a stream to read input data；Both read line by line and parse input；Both store parsed elements into collections；Both handle exceptions with stack trace printing
- 行为差异: Input source: file path vs URL from combo box；Data format: plain integers per line vs FASTA with header lines starting with '>'；Output: returns HashSet<Integer> vs populates class fields (ArrayList<String> names and sequences)；Exception handling: generic Exception vs specific MalformedURLException, EOFException, IOException
- 修正建议: Incorporate data flow analysis to differentiate output types and data formats；Use type information (e.g., return type, field types) to disambiguate；Train with more examples of domain-specific parsing patterns

### case_id=2934 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Modifies a localized properties file by updating or adding a specific key-value pair.
- B 摘要: Reads a DICOM image file, parses its content, and writes it to a new file.
- 静态失败原因: Static BERT likely correctly predicted non-clone due to very low token overlap and no structural similarity; the model failed to match the erroneous BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB annotation may incorrectly consider both as 'file read-modify-write' tasks, which is too broad.
- 共享行为: Both perform file I/O operations (reading and writing)
- 行为差异: Different domains: properties file editing vs. DICOM image processing；Different libraries used；Different data structures and logic
- 修正建议: Re-evaluate the BCB annotation for this pair；Incorporate domain-specific understanding to avoid spurious functional similarity

### case_id=2935 FN benchmark_preference_bias

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Launches a NexOpen project by processing pom.xml files, configuring Hibernate dialect, and setting up reverse engineering.
- 静态失败原因: Static model did not fail; it correctly predicted non-clone due to low lexical overlap and dissimilar structure.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have mistakenly labeled as clone due to benchmark noise or overly broad partial functionality criteria, though no evident shared behavior.
- 行为差异: Function a transfers file content; function b processes project configuration.；Function a is I/O utility; function b is Eclipse launch framework with complex logic.；Function a has no dependencies; function b depends on Eclipse, Maven, Hibernate APIs.
- 修正建议: Reexamine BCB annotation for potential error.；Ensure clone pairs have at least partial algorithmic similarity.

### case_id=2936 FN benchmark_preference_bias

- 方法: `testAddLinkToImage` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: A test method that copies image files from classpath to a report folder and adds links to them.
- B 摘要: A method that modifies a properties file for a given locale by reading, updating or adding a message key-value pair.
- 静态失败原因: The model correctly predicted non-clone based on low token overlap (0.07563) and lack of semantic similarity, but BCB label disagrees, so the model did not fail; the BCB label may be erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled it as clone due to superficial similarity in performing file I/O and resource handling, which may be considered broad Type-4 in some contexts, but this is a stretch.
- 共享行为: Both involve file I/O operations (reading from classpath and writing to file system)；Both handle resources and file paths
- 行为差异: Function A is a test method specifically for adding image links to a report, while B is a utility for modifying localization properties；A copies multiple image files and adds links; B reads a properties file, updates or appends a message, and writes back；A uses IOUtils.copy and report.addLink; B uses manual line-by-line parsing and StringBuilder
- 修正建议: Re-evaluate BCB label for correctness in this pair；If BCB label is correct, need to understand deeper hidden similarity; otherwise, treat as noise in benchmark

### case_id=2937 FN benchmark_preference_bias

- 方法: `uploadFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Uploads a file by renaming or copying bytes from input to output stream.
- B 摘要: Builds a website for edit by processing pages, reading XML, performing transformations, and writing output files.
- 静态失败原因: The static BERT model correctly identified the low token Jaccard similarity (0.09) and distinct method signatures/contexts, leading to a non-clone prediction that aligns with strict semantic equivalence.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to the presence of similar low-level file I/O patterns (e.g., FileInputStream/FileOutputStream) despite the vast difference in overall purpose and complexity, reflecting a broad Type-4 semantic interpretation.
- 共享行为: Both perform file I/O operations (reading and writing files)
- 行为差异: Function A is a simple file upload/copy utility; Function B is a complex multi-step site generation method；Function A handles only one file; Function B processes multiple pages and involves multiple file operations；Function B includes many additional concerns like DOM manipulation, string transformations, and property handling
- 修正建议: Require clone definitions to consider method-level intention and control flow similarity beyond shared API calls；Incorporate higher-level semantic features to avoid false positives from generic I/O patterns

### case_id=2938 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a newer version of jEdit by reading a version file from a URL and comparing build numbers.
- B 摘要: Sends an HTTP POST request with parameters and returns the response as a string.
- 静态失败原因: Static BERT/GraphCodeBERT may have over-relied on token overlap (e.g., URL, BufferedReader, InputStream) and common structural patterns, missing the semantic difference in purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the overall functionality is different: version check vs. HTTP POST execution, despite sharing some network I/O patterns.
- 共享行为: Both open a URL connection and read data from an input stream；Both use BufferedReader to read lines；Both handle exceptions (IOException or Exception)
- 行为差异: A performs a GET request for version checking; B performs a POST request with parameters；A parses lines for version/build info and shows UI messages; B sends parameters and returns the response string；A returns void; B returns a String
- 修正建议: Increase representation of non-clone pairs with similar API usage but different tasks in training data；Incorporate more semantic features, e.g., method intent or control flow differences

### case_id=2939 FN partial_functionality

- 方法: `main` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file's content to another file using FileChannel and ByteBuffer.
- B 摘要: Downloads a KMZ file from a URL and extracts its ZIP entries to local files.
- 静态失败原因: Low token Jaccard (0.28) and different API usage (FileChannel vs ZipInputStream) caused the model to miss the structural similarity in the I/O loop pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions implement a general pattern of reading from an I/O source and writing to one or more outputs, with similar loop and buffer usage, aligning with Type-3/Type-4 semantic similarity.
- 共享行为: Both are main methods that read data in chunks from a source and write to output streams/files using a while loop and buffer management.
- 行为差异: Source type: file vs URL；Number of outputs: single file vs multiple files；Data processing: raw copy vs zip extraction
- 修正建议: Incorporate structural features like control flow graph isomorphism or data flow patterns.；Use models that capture high-level semantic patterns beyond token overlap.

### case_id=2940 FN partial_functionality

- 方法: `getContent` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Executes an HTTP request and returns the response body as a string with lines separated by newline.
- B 摘要: Reads a file or classpath resource and returns its content as a string without newlines, exiting on failure.
- 静态失败原因: The static model likely focused on token overlap (0.195) and saw different APIs (HttpClient vs FileInputStream) and different method signatures, leading to low similarity. It missed the common line-reading loop pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers both functions as reading textual data line by line and returning a concatenated string, which is a common pattern for resource reading. The specific I/O source and error handling differences are considered superficial in Type-4 clone detection.
- 共享行为: Reads text line by line using a BufferedReader；Appends lines to a StringBuffer；Returns the concatenated string
- 行为差异: Source of content (HTTP response vs file/classpath resource)；Error handling (throws Exception vs System.exit)；Newline handling (appends newline vs no newline)
- 修正建议: Increase sensitivity to structural patterns like loops over readers；Add data-flow analysis to track string buffer concatenation；Train with more diverse I/O sources to learn similarity of reading patterns

### case_id=2941 FN partial_functionality

- 方法: `getHTML` vs `retrieveTemplate`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a URL with encoding and optionally writes to a file.
- B 摘要: Fetches a template from a blog URL and caches it.
- 静态失败原因: Static BERT models may overemphasize lexical and structural differences (e.g., parameters, caching, file writing) and miss the high-level semantic intent of URL content retrieval.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both functions as 'fetch URL content and return as string' clones, emphasizing functional similarity over implementation details.
- 共享行为: Both retrieve content from a URL and return it as a string.
- 行为差异: A appends newlines after each line; B concatenates lines without newlines.；A optionally writes to a file; B caches the result.；A catches exceptions internally; B throws Exception.；A sets User-Agent header; B does not.
- 修正建议: Train with more examples of Type-4 clones that share intent but differ in implementation.；Incorporate data-flow or control-flow alignment to recognize similar high-level behavior.；Use graph-based representations that abstract away surface-level details.

### case_id=2942 FN benchmark_preference_bias

- 方法: `copyResourceToFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a resource file to a destination file using input and output streams with proper cleanup.
- B 摘要: Builds an HTML site for editing by processing XML, transforming pages, and writing output files.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low token overlap (0.066) and distinct structural patterns, correctly predicting non-clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both involving file copying/stream handling, potentially categorized as Type-4 (functionally similar but different implementations) or due to annotation error.
- 共享行为: Both perform file I/O operations；Both use try-finally blocks for stream cleanup
- 行为差异: Different overall purpose: resource copy vs site generation；Function B has complex XML processing and page iteration, absent in A；Function A is simple and generic; B is large and domain-specific
- 修正建议: Review BCB annotation for correctness；Consider whether broad file I/O similarity should count as clone

### case_id=2943 FP lexical_or_api_overlap

- 方法: `sendRequest` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an XML request to a configurable server over HTTP with GZIP compression and parses the response as XML.
- B 摘要: Performs a Google image search by fetching HTML, parsing image URLs, and updating a UI component with an image.
- 静态失败原因: The static model likely overemphasized the lexical overlap in HTTP-related API calls (URL, URLConnection, streams) and similar exception handling structure, while missing the distinct semantics and data flow differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically considers Type-1 to Type-4 clones; this pair shares only common API usage (HTTP) but differs in core functionality, so it is not a clone even under Type-4 (functionally similar).
- 共享行为: Both use HTTP connections (URL, URLConnection/HttpURLConnection) to communicate over the network.；Both handle I/O streams and exceptions.
- 行为差异: Function A writes compressed XML output and parses XML response; Function B only reads HTML and extracts image URLs.；Function A involves complex configuration (server URL from preferences, dialog); Function B uses fixed Google URL.；Function A returns a String (empty), Function B is void and updates UI.；Function B processes HTML text with string splitting; Function A uses SAX parser.
- 修正建议: Incorporate deeper semantic analysis focusing on method purpose and data transformations.；Use methods' names and signatures as strong features to distinguish domain-specific behaviors.；Enhance training data with more negative examples that share API usage but differ in intent.

### case_id=2944 FN partial_functionality

- 方法: `doVersionCheck` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens a URL from a property, reads version and build information, compares with current build, and shows a message if a new version is available or that it's up-to-date, with wait cursor and error handling.
- B 摘要: Opens a hardcoded URL, reads its content line by line into a StringBuffer, and logs the result without any UI or error handling.
- 静态失败原因: Static BERT models like GraphCodeBERT might fail because they rely on token sequence and structure, but the high-level purpose differs (version checking vs. simple HTTP fetch). The low token overlap (0.194) and different method names also contribute to low similarity score, causing false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions involve establishing a URL connection, reading data line by line, and closing the stream, which is a common pattern considered as Type-4 (similar functionality) in BigCloneBench.
- 共享行为: Both open a URL and read lines from its input stream using BufferedReader.
- 行为差异: Function A has UI interaction (show/hide wait cursor, display messages), while B only logs.；Function A parses specific lines for version/build, B just appends all lines.；Function A uses a configurable URL from properties, B uses a hardcoded URL.；Function A catches IOException, B throws Exception.
- 修正建议: Incorporate structural or control flow information to capture the common pattern of URL reading despite different contexts.；Use contrastive learning to emphasize functional similarity over literal token overlap.；Consider using a graph-based representation that highlights the data flow from URL opening to stream reading.

### case_id=2945 FN lexical_or_api_overlap

- 方法: `runScript` vs `parse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads a script file from a URL and returns its content as a string, with error handling returning 'error!'.
- B 摘要: Parses a structured data file (from URL or local file) into a DataSet object using a StreamTokenizer, handling headers, types, delimiter, and scientific notation.
- 静态失败原因: Low token Jaccard (0.091) and different API usage (BufferedInputStream vs DataInputStream/StreamTokenizer) caused model to miss the shared URL-reading pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as 'reading from URL and processing input' clones, emphasizing shared I/O pattern over processing details.
- 共享行为: Both open a URL stream using openStream()；Both read data from an input stream；Both catch IO exceptions
- 行为差异: A reads raw bytes and concatenates into a single string; B parses tokens into structured data；A has no concept of headers, types, or delimiters; B has complex parsing logic；A returns a string or 'error!'; B returns a DataSet object or null；B handles both URL and local file sources, while A only uses URL
- 修正建议: Incorporate dataflow analysis to capture shared I/O patterns；Use graph-based representations to link similar low-level operations；Augment training with more diverse URL-reading examples

### case_id=2946 FN benchmark_preference_bias

- 方法: `getFile` vs `transformSingleFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies the endpoint address in the WSDL, and saves it to a temporary file, returning the file path.
- B 摘要: Compresses a VRML file using GZIP and saves it with a .x3dv.gz extension, returning the output file path.
- 静态失败原因: The model correctly identified low token overlap (Jaccard=0.09) and syntactic/structural dissimilarity, but the benchmark label (1) may be influenced by a high-level functional similarity that static models cannot capture without deeper semantic understanding.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'file transformation' methods that take some input, process it, and save to a file, returning the path, accepting this as a broad Type-4 semantic clone despite vastly different domain-specific logic.
- 共享行为: Both involve file I/O operations: reading an input source and writing to an output file.；Both return a file path string as the result.
- 行为差异: Input source: URL vs existing file.；Output format: WSDL (XML) vs GZIP compressed file.；Transformation: XML manipulation (endpoint substitution) vs data compression.；Error handling: throws AxisFault vs returns null.
- 修正建议: Re-evaluate benchmark annotation for consistency; consider if broad file-processing tasks should be considered clones.；Enhance model with domain-specific contextual embeddings or data flow analysis to distinguish between different file operations.

### case_id=2947 FN partial_functionality

- 方法: `copyResource` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using a byte-by-byte stream copy.
- B 摘要: Copies a file to another file (with .out extension) using a Pump abstraction, potentially with optional diagnostic byte counting.
- 静态失败原因: Static BERT models rely on token similarity and structural patterns. The low token Jaccard (0.2) and the presence of complex, framework-specific code in B (inner classes, $declass, Pump) leads the model to view them as unrelated, missing the shared functionality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels clones based on high-level functional similarity even with significant syntactic differences. Both functions perform the core task of copying data from an input source to an output file, which aligns with BCB's broad criteria for Type-3/Type-4 clones.
- 共享行为: Opens an input stream from a source (URL/file for A, file for B).；Opens an output stream to a destination file.；Copies data from input to output.；Closes both streams after copying.
- 行为差异: A can read from a URL or file; B only reads from a file argument.；A uses simple while loop for byte-by-byte copy; B uses a Pump class (may involve encryption/transformation).；A throws exception if source not found; B assumes file exists.；B has an optional diagnostic mode that counts bytes; A does not.
- 修正建议: Incorporate data-flow analysis to capture input-output relationships.；Use functional similarity measures that abstract away IO mechanism details.；Train on examples with low token overlap but high semantic similarity.

### case_id=2948 FN partial_functionality

- 方法: `sendExceptionToServer` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a fixed server URL via HTTP POST using URLConnection, prints response status.
- B 摘要: Generic HTTP POST method using Apache HttpClient that returns response string or null on error.
- 静态失败原因: Static models rely on token overlap and syntactic structure; low Jaccard (0.176) and different library APIs lead to low similarity scores, missing the high-level semantic similarity of HTTP POST.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators may have considered them clones due to shared HTTP POST functionality with URL encoding, despite library and detail differences.
- 共享行为: Both perform HTTP POST requests；Both URL-encode parameters；Both read and handle HTTP response
- 行为差异: Different HTTP client libraries (URLConnection vs HttpClient)；Different error handling (prints vs returns null with error codes)；Different return types (void vs String)；Different parameter handling (manual encoding vs NameValuePair list)
- 修正建议: Incorporate dataflow or API usage patterns to recognize HTTP POST operations；Use graph-based representations to capture semantic intent beyond surface syntax

### case_id=2949 FP boilerplate_overlap

- 方法: `postRequest` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends a POST request with URL-encoded form data from a HashMap and returns the response body as a string.
- B 摘要: Performs a Google image search for the current track's artist and album, parsing HTML to extract image URLs and adding them to a list.
- 静态失败原因: The static BERT model was misled by overlapping boilerplate code (URL opening, BufferedReader reading, exception handling) and common API calls (URLEncoder, URLConnection), despite the different core logic and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because the functions have distinct high-level purposes (generic POST vs. specific image search) and low token similarity (Jaccard 0.192). Even broad Type-3/4 criteria require some functional similarity, which is lacking here.
- 共享行为: Both open an HTTP connection to a URL；Both read the response line by line using BufferedReader；Both handle exceptions with try-catch blocks
- 行为差异: A uses POST method and writes form data; B uses GET method with query parameters in URL；A returns the response body as a string; B parses HTML to extract image URLs and modifies instance state；A is a generic utility; B is application-specific with side effects (populates a list and checks condition)；A uses URLConnection; B uses HttpURLConnection with a custom User-Agent header
- 修正建议: Enhance model to capture method-level semantics and purpose, e.g., using method names and signatures.；Incorporate data flow analysis to distinguish between write and read operations.；Add attention to task-specific differences (e.g., POST vs GET, parameter handling).

### case_id=2950 FP lexical_or_api_overlap

- 方法: `PageLoader` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Constructor that reads entire content from a URL into a field.
- B 摘要: Method that reads first line from a URL connection and returns it.
- 静态失败原因: Model relied on high token overlap (URL, BufferedReader, etc.) and common boilerplate, missing structural differences in loops and return statements.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because functions differ in return type, control flow (loop vs no loop), API usage, and overall purpose, which is too divergent for even Type-4 similarity.
- 共享行为: Both open a URL and read text from it using BufferedReader.
- 行为差异: A reads all lines in a loop, B reads only first line.；A uses plain URL.openStream(), B uses HttpURLConnection with explicit connect/disconnect.；A stores result in field, B returns a String.
- 修正建议: Incorporate dataflow analysis to detect reading multiple lines vs single line.；Add control flow features to distinguish loops from sequential code.；Include type information (constructor vs method) and return type.

### case_id=2951 FP lexical_or_api_overlap

- 方法: `run` vs `wordFrequency`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads map tiles from a URL, parses GeoJSON into geometries, and adds them to a data loader.
- B 摘要: Fetches a web page, searches for a pattern matching a word frequency, and returns the frequency.
- 静态失败原因: The model likely over-relied on lexical and structural similarities (e.g., both create URL, use BufferedReader, handle MalformedURLException and IOException) without capturing the distinct high-level semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these non-clones because they implement completely different functionalities (map rendering vs. text mining), despite sharing basic I/O patterns.
- 共享行为: Both use URL and BufferedReader to read data line by line
- 行为差异: Different overall purpose: tile loading vs. word frequency extraction；Different data processing: geometry collection vs. regex matching；Different output: void vs. int return；Different input: implicit via getKey() vs. explicit word parameter
- 修正建议: Incorporate higher-level semantic understanding via control flow or data flow analysis；Increase weight on method name and domain-specific context；Use a more fine-grained tokenization that distinguishes I/O boilerplate from core logic

### case_id=2952 FN benchmark_preference_bias

- 方法: `addIDs` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Fetches metabolite data from a web service and populates a PeakListRow with IDs and molecular weight.
- B 摘要: Reads a configuration file to initialize sets and hash maps for Tibetan/Sanskrit transliteration.
- 静态失败原因: The model correctly identified the low token overlap and distinct functional logic, resulting in a non-clone prediction. The BCB label of 1 appears to be a misannotation or an outlier, so the model did not fail in terms of semantic similarity detection.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone based on a very broad interpretation of 'data loading' or 'initialization' patterns, but the functional purpose and implementation are completely unrelated, which usually would not qualify under BCB's Type-3/Type-4 criteria.
- 共享行为: Both perform initialization/loading of data from external sources (web vs. file).
- 行为差异: Different data sources (URL vs. file with tokens)；Different processing logic (HTML parsing vs. token splitting)；Different output targets (row object fields vs. static sets/maps)；Different domains (metabolomics vs. transliteration)
- 修正建议: Re-annotate this pair as non-clone in the ground truth；If retaining the clone label, use a more nuanced similarity threshold that accounts for domain-specific differences

### case_id=2953 FP lexical_or_api_overlap

- 方法: `getURLContent` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads entire content from a URL as a string.
- B 摘要: Downloads an RDF model from a URL using HTTP headers.
- 静态失败原因: Static BERT/GraphCodeBERT was misled by lexical and API overlaps (URL, URLConnection, openConnection, getInputStream) and similar structural patterns (try-catch, reading, closing). It lacked understanding of the different return types and downstream usage.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions serve distinct purposes: generic URL-to-string vs. RDF model downloader. The output types and processing logic differ significantly, despite similar URL reading steps.
- 共享行为: Both open a URL connection and read from an input stream.；Both handle IOException (one throws, one wraps).
- 行为差异: Function A returns a String; Function B returns a Model.；Function A reads line-by-line; Function B parses RDF/XML via model.read.；Function B sets HTTP headers; Function A does not.；Function A explicitly handles encoding; Function B relies on parser.
- 修正建议: Incorporate dataflow and type information to capture differences in return types.；Use contrastive training examples that disambiguate similar API usage but different semantics.；Add heuristics to detect whether the output is consumed as raw text or parsed into a model.

### case_id=2954 FP lexical_or_api_overlap

- 方法: `copyFileTo` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Handles GUI action events to update application preferences and settings.
- 静态失败原因: The model likely picked up on superficial lexical overlaps (e.g., both use File, logger, and Java API calls) but failed to capture the vast semantic and structural differences. The high prediction may be due to a false positive from boilerplate or common API usage, or a model calibration error.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the two functions have completely different functionality and no significant code reuse or structural similarity.
- 行为差异: Function A performs a specific file copy operation; function B handles multiple GUI-based configuration changes.；Function A uses low-level I/O channels; function B uses Swing components and preference storage.；Function A has no user interaction; function B relies on user input via dialogs and selections.；Function A is short and focused; function B is long and branching with many conditionals.
- 修正建议: Improve semantic understanding by incorporating data flow or control flow graphs.；Train on more diverse negative pairs to reduce false positives from incidental API overlap.；Use a longer context or hierarchical representation to capture overall function purpose.

### case_id=2955 FP partial_functionality

- 方法: `setBundleInfoName` vs `readZoneIDs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL, parses key-value pairs, updates bundle names in a list, returns success status.
- B 摘要: Reads a URL, parses each line as an integer, collects into a set, returns set.
- 静态失败原因: Static model likely focused on the common structural pattern of URL reading and line-by-line processing, ignoring the different data processing logic.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels as non-clone because the functions have different purposes and output types, and the shared I/O pattern is incidental.
- 共享行为: Both read from a URL using InputStreamReader；Both use while loop reading lines；Both handle exceptions with printStackTrace
- 行为差异: Function A updates a list of BundleInfo objects; Function B creates a HashSet of integers；Function A parses key=value pairs; Function B parses integers；Function A returns boolean; Function B returns HashSet；Function A has logic to match bundle symbolic name; Function B adds all lines as integers
- 修正建议: Improve model to capture detailed data flow and transformation logic；Use contrastive learning to distinguish common boilerplate from core semantics

### case_id=2956 FP boilerplate_overlap

- 方法: `readZoneIDs` vs `readIntoList`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads zone IDs from a text file resource, parsing each line as an integer into a set.
- B 摘要: Reads HTML anchor tags from a resource, extracts link text, creates menu items with action commands and listeners, and populates a map.
- 静态失败原因: The model likely overfit on the common I/O boilerplate (reading lines, exception handling) and missed the distinct data processing logic, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically annotates clones as Type-4 when there is high-level semantic similarity, but here the core functionality differs fundamentally (data extraction vs UI population), so BCB correctly labels as non-clone.
- 共享行为: Both read lines from a URL resource；Both use BufferedReader/LineNumberReader to read line by line；Both catch exceptions and print stack traces
- 行为差异: Input: A takes a String filename, B takes a URL and a Map；Output: A returns a HashSet<Integer>, B modifies a Map side effect；Line processing: A parses integers, B parses HTML and creates UI components；B includes action listener setup, A does not
- 修正建议: Train on more diverse examples where I/O structure is similar but processing logic differs；Incorporate dataflow analysis to differentiate between integer parsing and HTML parsing；Use contrastive learning to emphasize functional differences over structural skeletons

### case_id=2957 FP boilerplate_overlap

- 方法: `readData` vs `encodeFileToFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads a data file and populates multiple sets and maps with parsed tokens (e.g., wylie, unicode) after complex conditional processing.
- B 摘要: Reads a file, Base64-encodes its content, and writes the encoded output to another file, returning success status.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized the boilerplate file I/O structure (buffered streams, try-catch, while loop), which is common in many Java functions, while missing the distinct core semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels clones based on functional similarity; these functions serve entirely different purposes (parsing vs encoding), so BCB would label them as non-clones.
- 共享行为: Both involve file I/O with buffered streams and exception handling (try-catch-finally).；Both use while loops to process data chunks.
- 行为差异: Core logic: A parses structured text into data structures (sets, maps) with field validation; B performs Base64 encoding and simple copy.；Output: A updates internal state; B writes to an output file and returns boolean.；Complexity: A has extensive conditional logic for different columns; B is a straightforward encode-and-write loop.
- 修正建议: Improve model to better capture high-level functional semantics beyond low-level control flow.；Use dataflow analysis to distinguish different transformation pipelines.；Incorporate program dependency graphs to separate boilerplate from core logic.

### case_id=2958 FN benchmark_preference_bias

- 方法: `copyResource` vs `checkInputStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file.
- B 摘要: Reads an InputStream and compares its content to an expected byte array.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on token-level similarity and low Jaccard score, missing the high-level functional overlap in stream I/O patterns that the benchmark recognizes.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone because both functions involve reading from an InputStream and writing to an OutputStream, fitting a broad Type-4 semantic clone definition of stream I/O operations.
- 共享行为: Read from an InputStream；Write bytes to an OutputStream
- 行为差异: copyResource loads resource from source; checkInputStream takes an already-open stream；copyResource writes to a FileOutputStream and file; checkInputStream writes to a ByteArrayOutputStream for comparison；copyResource does not compare output; checkInputStream compares output to expected bytes
- 修正建议: Incorporate data flow analysis to capture stream I/O patterns；Enhance training with more Type-4 clone examples

### case_id=2959 FN boilerplate_overlap

- 方法: `importRoles` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL, parses XML role names, and returns an ArrayList of RoleName objects.
- B 摘要: Reads a fixed URL, concatenates lines, and logs the content.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low token Jaccard (0.2456) and different method names, causing it to miss the shared I/O boilerplate. The model may not recognize that the core reading loop is functionally similar despite different surrounding context.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider this a Type-3 clone because both functions have the same core I/O pattern (read URL line by line using BufferedReader and StringBuffer), and the structural similarity outweighs the differing post-processing and return types.
- 共享行为: Both create a URL object and open a stream；Both read lines using BufferedReader；Both append lines to a StringBuffer
- 行为差异: A returns a list of parsed RoleName objects; B logs the content and returns void；A parses XML tags (RoleName) and accumulates lines until a closing tag; B simply concatenates all lines；A uses a parameter for the URL string; B uses a hardcoded URL；A handles multiple exceptions internally; B throws Exception
- 修正建议: Augment training data with pairs that share common I/O boilerplate but differ in high-level logic；Add a token-level attention mechanism that captures common API call sequences (e.g., URL, openStream, BufferedReader, readLine)；Use a graph-based representation that abstracts over variable names and method signatures

### case_id=2960 FN benchmark_preference_bias

- 方法: `main` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.1`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Compresses a file using GZIP with error handling and user feedback.
- B 摘要: Builds an editable web site by transforming XML pages with file I/O and string processing.
- 静态失败原因: GraphCodeBERT likely focused on token overlap and syntactic structure, which are very low here, so it correctly predicted non-clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might label these as clones due to both involving file I/O and exception handling, but the functional equivalence is extremely weak and likely a mislabel in the benchmark.
- 共享行为: Both perform file I/O operations；Both use try-catch for exception handling
- 行为差异: A is a simple single-file compression utility; B is a complex multi-step site builder；A takes only command-line arguments; B takes many configuration parameters；A outputs a binary gzip file; B outputs transformed HTML/text files；B involves XML parsing, transformer chains, and string replacement; A has none of that
- 修正建议: Ensure benchmark labels are consistent with semantic equivalence；Use human re-annotation to remove such far-apart pairs

### case_id=2961 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale, updating or adding a key-value pair.
- B 摘要: Copies a file from a source path to a destination directory.
- 静态失败原因: Low token overlap (0.12) and different method names; the file copy sub-task is relatively short and the models may not capture partial functionality similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: None
- 共享行为: Both perform file I/O operations；Both copy the content of a file to another location
- 行为差异: A modifies a properties file by parsing and rewriting; B performs a byte-level copy；A handles missing locale files by copying a default; B does not；A reads and writes text; B copies binary
- 修正建议: Train with examples that highlight sub-function similarity；Use graph-based models that capture data flow and file I/O operations

### case_id=2962 FN benchmark_preference_bias

- 方法: `testCodingEmptyFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Tests a LengthDelimitedEncoder by writing bytes to a buffer and transferring from a file channel.
- B 摘要: Retrieves a resource from a URL, caches it locally to a file, and returns an InputStream.
- 静态失败原因: Static BERT/GraphCodeBERT likely correctly captured the large behavioral and structural differences, as evidenced by token Jaccard of only 0.083 and distinct control flows, thus predicting non-clone. It 'failed' only relative to a potentially erroneous BCB annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to both functions heavily utilizing Java I/O (FileInputStream, FileOutputStream, channels) and file manipulation, leading to a very broad Type-3/Type-4 similarity based on low-level API usage despite different high-level purposes.
- 共享行为: Both create temporary files.；Both write bytes to files using output streams.；Both read bytes from files using input streams.；Both perform cleanup of streams and files.
- 行为差异: Function A is a unit test that checks encoder completion and output content; function B is a resource caching method with HTTP conditional GET.；Function A uses LengthDelimitedEncoder and HTTP transport classes; function B uses URLConnection and HttpURLConnection.；Function A writes predetermined strings; function B writes arbitrary bytes from network.；Function A does not involve network access; function B downloads from a URL.
- 修正建议: Improve BCB annotation guidelines to avoid labeling functions with only superficial API overlap as clones.；Include higher-level semantic considerations such as overall purpose and logic flow.；Use additional context (e.g., method names, class names) to disambiguate similar low-level patterns.

### case_id=2963 FN partial_functionality

- 方法: `doGet` vs `resolvePlugins`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests to retrieve and render a portal page with caching and security checks.
- B 摘要: Resolves and caches a plugin list from a remote URL for a text editor.
- 静态失败原因: Low token overlap (Jaccard=0.05) and different method names cause the model to miss the high-level functional similarity (both are caching resource resolvers). The model is sensitive to lexical surface forms.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a Type-4 clone because both are 'resource resolution with caching' functions, despite different domains and implementation details.
- 共享行为: Both perform resource retrieval with caching and error handling.
- 行为差异: Function A is a servlet doGet that handles page rendering with user authentication and logging; Function B downloads a plugin XML file from the internet if not cached.；Function A involves extensive user permission checks and output caching, whereas Function B simply checks file existence and downloads once.
- 修正建议: Incorporate control flow and data flow analysis to capture functional similarity despite low lexical overlap.；Use hierarchical embeddings that capture resource operations.

### case_id=2964 FN partial_functionality

- 方法: `getJSONData` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches JSON data from a URL via HTTP GET using DefaultHttpClient and returns a JSONObject.
- B 摘要: Fetches and processes OPDS catalog data from a URL via HttpURLConnection, handling pagination, progress, and download.
- 静态失败原因: The static model likely overemphasized the low lexical overlap (Jaccard=0.088) and the differences in libraries and complexity, missing the shared HTTP GET core functionality that BCB considers sufficient for a clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as Type-4 clone because both functions implement the high-level task of fetching data from a URL over HTTP and parsing the response, despite different formats and additional logic.
- 共享行为: Both perform HTTP GET requests；Both read response content from the input stream；Both handle exceptions during network operations
- 行为差异: Function A returns a JSONObject; Function B processes OPDS entries and downloads books；Function A uses DefaultHttpClient; Function B uses HttpURLConnection with custom headers；Function B includes pagination, progress tracking, and multiple callback mechanisms；Function B is significantly more complex with error recovery and partial loading
- 修正建议: Use code embeddings that capture high-level API call sequences；Incorporate structural similarity (e.g., AST subgraph matching) to detect shared data flow patterns；Add training examples that include Type-4 clones with low lexical overlap

### case_id=2965 FP boilerplate_overlap

- 方法: `createHTML` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates an HTML page by reading a CSS file and optionally querying a database for content.
- B 摘要: Fetches Google image search results, extracts image URLs, and displays the first image on a UI component.
- 静态失败原因: The model likely overemphasized shared lexical patterns (URL, BufferedReader, try-catch) and string building, mistaking boilerplate similarity for semantic similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because functions have entirely different purposes and only share common I/O boilerplate, which is not sufficient for clone detection.
- 共享行为: Both use URL, BufferedReader, and string concatenation for reading data
- 行为差异: Function a generates HTML string from local resources and database; function b fetches web data and updates UI；Function a returns a string; function b returns void；Function a uses switch-case on page type; function b constructs a Google search URL；Function a is purely backend; function b has UI side effects
- 修正建议: Enhance model to distinguish between core logic and common I/O patterns；Incorporate data flow and type analysis；Consider function signature and return type

### case_id=2966 FN partial_functionality

- 方法: `copyResource` vs `persist`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file by reading byte-by-byte.
- B 摘要: Persists a configuration by copying an input stream provided by a configurable object to a file using IOUtils.copy.
- 静态失败原因: Low token overlap (Jaccard=0.12) and reliance on surface features; the model did not capture the shared data flow of reading an input stream and writing to a file output stream, nor abstract away implementation details like library calls vs. manual loops.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels functions as clones if they perform the same high-level task (copying data to a file), even with different implementations and minor variations, reflecting a Type-3/4 tolerance.
- 共享行为: Both read from an input source and write to an output file stream.；Both involve file I/O operations to copy data.
- 行为差异: copyResource() reads from a URL or file path; persist() reads from an InputStream provided by a parameter.；copyResource() uses manual byte-by-byte copying; persist() uses IOUtils.copy for bulk copy.；copyResource() throws generic Exception; persist() throws ConfigurationException.；Different method signatures, parameters, and naming.
- 修正建议: Train models to recognize dataflow patterns (e.g., read->write) using graph-based representations.；Incorporate library function semantics (e.g., IOUtils.copy as a copy operation).；Augment training data with Type-3/4 clone pairs to improve semantic understanding.

### case_id=2967 FN benchmark_preference_bias

- 方法: `main` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies files from a source directory to a destination directory using FileChannel and ByteBuffer.
- B 摘要: Configures a NexOpen project launch by processing pom.xml files and setting up reverse engineering resources.
- 静态失败原因: The static BERT model did not fail; it correctly predicted non-clone. The BCB label is likely a false positive due to benchmark annotation error or overly broad clone criteria.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this clone due to superficial similarities in file manipulation (e.g., both read and write files, use InputStream/OutputStream) and the presence of boilerplate code like try-catch blocks, leading to a Type-4 or mistaken Type-3 annotation.
- 共享行为: Both perform file I/O operations
- 行为差异: Different domains: file copy vs. project configuration；Code_a uses FileChannel and ByteBuffer; Code_b uses Eclipse APIs and external libraries；Code_a is a simple standalone main method; Code_b is an Eclipse launch handler with error handling and property management；Code_b involves XML processing and resource creation based on configuration attributes; Code_a does not
- 修正建议: Review BCB annotation for this pair; consider excluding when functions have no semantic overlap despite shared low-level I/O operations

### case_id=2968 FP partial_functionality

- 方法: `onlyFileCopy` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file using FileChannel and transferTo.
- B 摘要: Main method for AdapterGenerator that parses command-line arguments, reads a Prolog file, parses it, generates adapter classes, and writes them to a JAR.
- 静态失败原因: Static model may have been misled by overlapping tokens like FileChannel, IOException, File, and similar control flow patterns (loops, try-catch-finally), leading to a false positive clone detection.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels as non-clone because the functions have completely different purposes and logic, despite sharing some I/O patterns.
- 共享行为: Both use File I/O and handle exceptions.；Both close resources in finally blocks.
- 行为差异: Function A only copies a file; Function B generates code from Prolog.；Function A is a utility method; Function B is a program entry point.；Function B has complex logic including parsing, class writing, and resource assembly.
- 修正建议: Incorporate structural or semantic features that capture high-level purpose.；Use hierarchical code representations to distinguish utility functions from complex orchestrations.；Train on more diverse examples to reduce sensitivity to token overlaps in I/O patterns.

### case_id=2969 FN benchmark_preference_bias

- 方法: `writeFileType` vs `login`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads URIs from a file, skips a given number, then for each URI connects to the URL, reads the first few lines to detect OWL/RDFS/RDF namespaces, and writes the URI with the detected type to an output file.
- B 摘要: Performs a login to a website by sending an HTTP POST with email and password, extracts a session ID from the response, and returns it.
- 静态失败原因: The static model correctly identified them as non-clones due to low token similarity (0.18) and distinct purposes; however, if BCB label is taken as ground truth, the model failed to recognize the superficial structural similarity that BCB might have considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to both functions using similar network I/O patterns (URLConnection, BufferedReader) and exception handling, but this is a weak similarity and likely a mislabel in the benchmark.
- 共享行为: Both use URL and URLConnection to establish network connections；Both read from an input stream using BufferedReader；Both handle exceptions with try-catch blocks
- 行为差异: A's purpose is to classify URIs by RDF type; B's purpose is to authenticate and retrieve a session ID；A reads from a local file first to get URIs, then connects to each; B directly connects to a fixed login endpoint；A writes results to a file; B returns a string；A processes multiple URIs in a loop; B performs a single login
- 修正建议: Re-evaluate BCB label for this pair; consider using functional categorization to avoid false positives from generic I/O patterns；Improve model to ignore boilerplate patterns and focus on core functionality

### case_id=2970 FN partial_functionality

- 方法: `run` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses XML input, manipulates DOM, and creates a ZIP package containing XUL extension resources (manifest, install.rdf, library.js, menu.xul, icon).
- B 摘要: Validates project configuration, processes pom.xml files, performs reverse engineering setup, and launches an installation action for a NexOpen Eclipse project.
- 静态失败原因: Low token-level overlap (Jaccard=0.10) and different method names and signatures caused GraphCodeBERT to capture no structural similarity. The semantic similarity is only at a shallow abstraction level, which neural models often miss.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as clone due to both methods involving XML parsing, file I/O, and exception handling, indicating broad functional similarity (Type-4) where both 'process XML and write output files'.
- 共享行为: Both parse XML documents using DocumentBuilder (or ContentHandlerTemplate).；Both perform file I/O operations including reading and writing streams.；Both handle exceptions with try-catch blocks.
- 行为差异: Code A builds a ZIP package for a XUL extension; Code B configures and launches an Eclipse project.；Code A outputs a complete ZIP file; Code B modifies project files and runs a job.；Different inputs (Reader vs. ILaunchConfiguration) and different contexts (private method vs. public launch delegate).
- 修正建议: Use a more fine-grained approach that focuses on high-level functional abstraction beyond tokens.；Consider program slicing to isolate the XML processing parts and compare those.；Incorporate domain knowledge about common library usage patterns.

### case_id=2971 FN partial_functionality

- 方法: `main` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Main method that downloads a specific KMZ file from a given URL and extracts its zip entries to the current directory.
- B 摘要: Method that retrieves a resource as an InputStream, with caching: downloads from URL if not cached, caches locally, and returns cached file input stream.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on surface-level token overlap and code structure, which are low here (token Jaccard 0.19). They may miss semantic similarity due to different method names, control flow, and specific operations (zip extraction vs. caching).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs as clones if they share similar high-level functionality, even if implementations differ. Here both functions download a file from a URL and save it locally, which aligns with Type-3/Type-4 clone criteria.
- 共享行为: Both open a URL connection and read an input stream.；Both write data to local files.
- 行为差异: A is a one-off main method with a fixed URL; B is a reusable method that handles any resource name.；A extracts zip entries; B implements caching with HTTP conditional requests.；A writes extracted entries; B caches the entire resource and returns an InputStream.
- 修正建议: Use code summarization or semantic role labeling to capture high-level intent before comparison.；Employ contrastive learning with functional equivalence examples to improve generalization.；Incorporate dynamic analysis or execution traces to capture runtime behavior similarity.

### case_id=2972 FN benchmark_preference_bias

- 方法: `getFile` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint attribute, and saves it to a temporary file.
- B 摘要: Copies a file from one local path to another using character streams.
- 静态失败原因: Static BERT/GraphCodeBERT relies on lexical and structural overlap; with a very low token Jaccard similarity (0.09375) and completely different APIs and control flow, the model could not detect any semantic similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone because both functions perform file I/O operations (reading and writing files), and under broad Type-4 semantic similarity, they share the high-level goal of transferring data from a source to a file, despite different sources and transformations.
- 共享行为: Both involve reading from a source and writing to a file；Both create File objects and handle I/O exceptions；Both close input/output streams after use
- 行为差异: getFile downloads from a URL and parses XML, while copy reads from a local file；getFile modifies the WSDL content, copy does not transform data；getFile uses NIO channels and FileOutputStream, copy uses Reader/Writer；getFile returns the file path, copy is void
- 修正建议: Incorporate abstract semantic representations like data flow or functional purpose；Train on more diverse examples of broad clone types to capture partial functionality similarity；Use larger context windows or graph-based models to understand overall intent

### case_id=2973 FN benchmark_preference_bias

- 方法: `copyResource` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using a simple byte-by-byte loop.
- B 摘要: Parses XML input into a DOM, modifies it, and writes multiple files (chrome.manifest, install.rdf, library.js, menu.xul, an icon) into a ZIP archive.
- 静态失败原因: The static model likely did not fail; it correctly identified non-clone due to low lexical overlap and different structures. The BCB label may be erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label of 1 might be a mislabel, as the functions share no significant functional similarity beyond basic I/O. Possibly the annotator considered both as 'resource copying' methods at a very abstract level.
- 共享行为: Both perform I/O operations (reading input and writing output).；Both handle exceptions.
- 行为差异: Function A copies a single resource to a single file; Function B creates a ZIP archive with multiple entries.；Function A does simple byte copying; Function B involves XML parsing, DOM manipulation, and writing structured content.；Function A uses a basic while loop; Function B uses various libraries (DocumentBuilder, ZipOutputStream, IOUtils).；Function A has straightforward control flow; Function B has complex conditional and sequential steps.
- 修正建议: Re-evaluate the BCB annotation for this pair; consider it a false positive in BCB.；If the model is to match BCB, it would need to capture extremely abstract functional similarity, which is not feasible.

### case_id=2974 FN partial_functionality

- 方法: `copyResource` vs `loadBinaryStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file using a byte-by-byte loop.
- B 摘要: Loads a binary stream from an InputStream into an HTTP response with headers and buffered copy.
- 静态失败原因: Low token Jaccard (0.117), different method names and signatures, and different APIs (URL/File vs HttpServletResponse/IOUtils) caused the model to miss the high-level semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as 'copying data from an input to an output' and treats them as Type-4 clones, ignoring details like source/destination type and high-level API usage.
- 共享行为: Both copy data from an input source to an output destination.；Both close the streams after copying.
- 行为差异: A writes to a file; B writes to an HTTP response.；A reads from URL or file; B reads from a provided InputStream.；A uses a manual loop; B uses IOUtils.copy.；A sets no headers; B sets content type, disposition, and length.
- 修正建议: Incorporate data-flow analysis to detect input-output copy patterns.；Use API mappings to recognize equivalent operations (e.g., various stream copy methods).；Train on more diverse clone types to generalize beyond lexical overlap.

### case_id=2975 FP boilerplate_overlap

- 方法: `DecodeMapFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a map file, XORs each byte with an incrementing key, and writes the result to an output file.
- B 摘要: Handles GUI action events to set file paths for external tools (GraphViz, ImageMagick) and update preferences.
- 静态失败原因: Likely due to low-level lexical or API overlap (e.g., repeated try-catch blocks, file handling keywords) that the model overgeneralized, despite the overall semantics being completely different.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because they perform entirely different tasks (file decoding vs. GUI event handling) with no functional similarity beyond generic language constructs.
- 共享行为: Both use try-catch blocks for exception handling；Both involve file I/O in a broad sense (but different specifics)
- 行为差异: One is a pure file transformation, the other is a GUI event handler；One uses simple byte-wise XOR, the other uses JFileChooser and preference storage；One has a single loop with a magic key, the other has conditional branches based on action commands
- 修正建议: Include more diverse training examples with contrasting functionalities；Incorporate structural or dataflow analysis to distinguish trivial I/O patterns from core logic

### case_id=2976 FN partial_functionality

- 方法: `testCopy_inputStreamToOutputStream` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A test method that copies an input stream to an output stream and verifies content equality.
- B 摘要: A method that launches a NexOpen project by setting up project files, processing XML, copying a resource stream, and modifying project properties.
- 静态失败原因: Static models like CodeBERT rely on token overlap and syntactic similarity, which are very low (token Jaccard 0.0766) between these methods. They fail to recognize the embedded functional similarity because it is a small sub-task within a larger, unrelated method.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone due to the shared functionality of copying an InputStream to an OutputStream using IOUtils.copy, considering it a Type-4 functional similarity clone.
- 共享行为: Both use IOUtils.copy to copy bytes from an InputStream to an OutputStream (specifically to a ByteArrayOutputStream).
- 行为差异: Method A is a simple test with no side effects; Method B has extensive file operations, XML parsing, property handling, and project resource management.；Method A uses only ByteArrayInputStream and ByteArrayOutputStream; Method B uses file streams and properties.；Method A includes assertions; Method B includes error handling and UI-related calls.
- 修正建议: Enhance models with dataflow analysis or program slicing to isolate common sub-computations.；Incorporate API usage patterns and type information to detect similar operations across different contexts.；Use contrastive learning on pairs with partial functional overlap.

### case_id=2977 FN partial_functionality

- 方法: `addIDs` vs `readReferenceText`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses a web page to extract metabolite IDs and sets them on a PeakListRow object, returning a score.
- B 摘要: Reads a text file from a plugin bundle and returns its content as a string.
- 静态失败原因: Static models rely heavily on lexical overlap (low Jaccard) and surface syntax; they miss high-level structural pattern of URL reading due to differences in variable names, method signatures, and overall complexity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: Both functions involve reading from a URL and processing lines, which BCB may treat as a common data retrieval pattern (Type-4/partial functionality) despite differences in output and processing details.
- 共享行为: Open URL and create BufferedReader；Read lines in a loop；Handle IOException via catch block
- 行为差异: A parses HTML for specific IDs; B simply concatenates all lines；A modifies a PeakListRow object with multiple fields; B returns a String；A returns an integer score; B returns the full text or throws an exception
- 修正建议: Incorporate I/O structural patterns (e.g., URL open, BufferedReader) as features；Use control-flow or graph representations that capture reading loops；Train with more Type-4 examples that share sub-tasks

### case_id=2978 FP other

- 方法: `testCopy_readerToWriter_nullIn` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Tests that passing null reader and writer to IOUtils.copy throws NullPointerException.
- B 摘要: Reads and parses a set of comma-separated string constants into multiple HashSet collections for Tibetan transliteration data.
- 静态失败原因: The static method likely over-relied on superficial token overlap or common structural patterns (e.g., method declaration, try-catch), despite very low Jaccard similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would label as non-clone because functions serve entirely different purposes and share no meaningful semantic overlap.
- 行为差异: Function A is a unit test for exception handling; Function B is a data initialization routine.；Function A uses I/O streams and writers; Function B uses StringTokenizer and string parsing.；Function A is short and focused; Function B is long and complex with multiple loops and conditionals.
- 修正建议: Improve training data diversity for non-clone pairs.；Use more robust structural representations that capture high-level intent.；Incorporate method-level context like class name and imports.

### case_id=2979 FN benchmark_preference_bias

- 方法: `loadSourceCode` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Loads source code from a local file via class resource, applies syntax highlighting, and generates an HTML string for display.
- B 摘要: Connects to an HTTP URL, downloads and processes an OPDS catalog, handles pagination and errors, and downloads books or parses catalog entries.
- 静态失败原因: Static BERT methods rely on lexical overlap and API sequence similarity; here token Jaccard is very low (0.08) and the functions use different APIs (CodeViewer vs. HttpsURLConnection), so the model correctly identified non-clone from a strict viewpoint but missed the BCB broad interpretation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone due to broad Type-4 similarity: both functions involve reading from a URL (one class resource, one HTTP) and processing lines, which some annotators consider partial functionality similarity.
- 共享行为: Both open a stream/connection (URL-based) and read line-by-line content.；Both handle exceptions with fallback behavior.；Both use BufferedReader to read lines in a loop.
- 行为差异: Function A reads from a local classpath resource; B reads from an HTTP URL with connection setup (headers, timeouts, redirects).；Function A applies syntax highlighting; B parses XML/Atom feeds or downloads files.；Function A builds an HTML string; B tracks progress, paginates, and invokes callbacks.；Function A is a void method; B manages state (loadNext, visited) and may call other methods like downloadBook.
- 修正建议: Incorporate high-level intent understanding, possibly via code summarization or API purpose embeddings.；Use fine-tuning on BCB-specific broad clone definitions to capture partial functionality matches.；Consider hierarchical representation that captures task-level similarity (e.g., 'read from source and process').

### case_id=2980 FN partial_functionality

- 方法: `getResourceAsStream` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Caches and retrieves a resource from a URL, returning an InputStream.
- B 摘要: Copies a source file to a destination file using FileChannels.
- 静态失败原因: The low token overlap and different method names likely caused the model to underestimate the abstract file-copy similarity, and the model may not generalize well to cross-project functions with different I/O patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones because both functions involve reading from a source and writing to a file, which could be seen as a common pattern of file copying, despite the additional complexity in A.
- 共享行为: Both perform file I/O operations；Both create parent directories before writing；Both close resources in a try-finally fashion
- 行为差异: Function A involves HTTP connection and caching logic; B does not；Function A returns an InputStream; B is void；Function A uses byte-by-byte stream copying; B uses channel transfer；Function A prints status messages; B does not
- 修正建议: Improve training data with more diverse file I/O clones；Enhance model with dataflow or structural embeddings to capture FileChannel vs. Stream patterns

### case_id=2981 FN lexical_or_api_overlap

- 方法: `CheckUrl` vs `retrieveTemplate`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches the first line from a given URL and returns it as string, with error handling returning empty string.
- B 摘要: Fetches all lines from the blog's URL, caches the result, and returns the full content as string, throwing exception on error.
- 静态失败原因: Low lexical overlap (Jaccard 0.2558) and structural differences (e.g., while loop vs single readLine, caching logic) cause static embeddings to miss semantic similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers both as retrieving text from a URL, with differences in caching, error handling, and line count being minor for Type-4 clone classification.
- 共享行为: Both open an HTTP connection to a URL；Both read text using BufferedReader and InputStreamReader
- 行为差异: A reads only first line, B reads all lines；A has no caching, B caches the result；A returns empty on exception, B throws exception；A is static with URL parameter, B is instance with field-derived URL
- 修正建议: Train with more diverse semantic equivalences；Incorporate control flow and data flow features；Use graph-based models that capture API usage patterns

### case_id=2982 FP lexical_or_api_overlap

- 方法: `getUser` vs `executeHttpGet`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user by login from a DAO or fallback config file, parsing lines with colon-separated tokens.
- B 摘要: Executes an HTTP GET request and parses the response body into a JSONObject.
- 静态失败原因: High lexical overlap of common API calls (BufferedReader, InputStreamReader, readLine) and sequential reading pattern causing false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have completely different functionality, even though they share a common boilerplate reading pattern.
- 共享行为: Both use BufferedReader and InputStreamReader to read line by line from a stream.
- 行为差异: Different domains: user authentication vs HTTP client.；Different data sources: local file vs HTTP response.；Different return types: User object vs JSONObject.；Different exception handling: caught vs thrown.
- 修正建议: Use code embeddings that capture semantic roles and data flow.；Incorporate domain-specific knowledge or type information.；Focus on control flow and external API calls to distinguish purpose.

### case_id=2983 FN benchmark_preference_bias

- 方法: `doGet` vs `test`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles an HTTP GET request to retrieve and render a page based on a parameter, including permission checks and caching.
- B 摘要: Tests the StorageStringWriter class by writing, reading, and verifying text content, and checking unsupported operations.
- 静态失败原因: The static BERT model correctly identified the functions as semantically distinct due to low token overlap and different control flow, thus the prediction of non-clone is accurate. The BCB label appears to be an error, so the model did not fail; rather the benchmark label is suspect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label may be a misannotation, possibly due to both methods using HttpServletResponse (response) and IOException, but otherwise unrelated.
- 行为差异: Code A processes HTTP requests and manages page rendering with complex permission and caching logic；Code B is a unit test for a string storage utility, focusing on I/O operations and exception handling
- 修正建议: Re-evaluate the BCB annotation for this pair, as the functions are clearly not clones.；If the model was expected to match the BCB label, then adjust training data or add more diverse examples to reduce bias.

### case_id=2984 FP boilerplate_overlap

- 方法: `main` vs `encodeFileToFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter classes from a Prolog file and writes them to a JAR file.
- B 摘要: Encodes a file to another file using Base64 encoding.
- 静态失败原因: Static BERT/GraphCodeBERT may have over-emphasized the shared boilerplate (file I/O, try-catch, stream closing) and overlooked the completely different core functionality, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the two functions have entirely different goals and implementation logic; the only overlap is boilerplate I/O patterns, which is insufficient for semantic similarity.
- 共享行为: Both involve reading from input files and writing to output files；Both use try-catch blocks for exception handling；Both close streams in finally blocks
- 行为差异: A generates Java adapter classes and metadata; B simply encodes binary data；A uses complex parsing and class generation libraries; B uses Base64 encoding stream；A produces multiple outputs (classes, serializer, etc.); B produces a single encoded file；A is a main method with command-line argument handling; B is a utility method called programmatically
- 修正建议: Increase training on distinguishing domain-specific logic from boilerplate；Incorporate data-flow analysis to capture the essential transformation differences；Use contrastive learning to penalize reliance on common structural patterns

### case_id=2985 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a new version of jEdit by reading a URL, extracting devel and stable build versions, and calling another method if both found.
- B 摘要: Fetches a version string from a URL and returns it, returning null on failure.
- 静态失败原因: Static BERT models may overweigh the common API tokens (URL, BufferedReader, InputStreamReader, while loop) and structural similarity, while missing the semantic differences in return type, side effects, and overall control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because, despite similar core I/O pattern, the overall functionality and purpose differ significantly: one is a UI-triggered version check that triggers further action, the other is a pure version string retrieval.
- 共享行为: Both open a URL connection and read lines from an InputStream using BufferedReader；Both parse version-related information from the read lines
- 行为差异: doVersionCheck is void and shows/hides a wait cursor, while getVersion returns a String；doVersionCheck reads multiple lines to find two build versions, getVersion overwrites version with each line；doVersionCheck calls another method to perform the actual version check, getVersion simply returns the version；Error handling differs: doVersionCheck shows an error dialog, getVersion returns null silently
- 修正建议: Incorporate data-flow analysis to track variable types and method calls；Use AST differencing to detect structural differences like return statements and method calls；Add a threshold for token overlap combined with functional similarity heuristics；Train on more diverse negative examples with similar API usage but different semantics

### case_id=2986 FN partial_functionality

- 方法: `runInternal` vs `load`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: This method loads an OPDS catalog from a URL via HTTP, parses XML/ATOM feed entries, handles pagination and errors, and downloads books if needed, with progress display and callback notifications.
- B 摘要: This method loads a paste from pastebin.com by constructing a URL, opening an HTTP connection, reading the content line by line into a string, and returning it.
- 静态失败原因: The static BERT model likely relied on token overlap and structural similarity, which are low (Jaccard 0.1055). It failed to recognize the high-level semantic similarity due to the vast differences in method length, APIs, and control flow. The model may have been misled by the Android-specific and OPDS-specific tokens in A that are absent in B.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both implement the core functionality of loading data from a URL via HTTP, which is a common pattern. Despite differences in complexity and additional processing, the high-level semantic intent (retrieving remote content) is similar, fitting Type-4 clone criteria favored by BCB.
- 共享行为: Both open a URL connection and read data from it via HTTP.；Both handle IO exceptions (though A does more extensive error handling).；Both are focused on retrieving content from a URL.
- 行为差异: A handles OPDS catalog format with SAX parsing and pagination; B only reads raw lines into a string.；A has progress display, callback mechanism, and can download files; B has none of these.；A supports redirects, timeout settings, and custom User-Agent; B uses default settings.；A is a long, multi-stage method; B is short and straightforward.
- 修正建议: Use a representation that captures semantic intent, such as data-flow or control-flow graphs, to focus on core operations (URL opening, reading).；Employ techniques like API call clustering or argument-driven analysis to abstract away implementation details.；Consider incorporating domain knowledge about common HTTP retrieval patterns to handle partial functionality overlap.

### case_id=2987 FN lexical_or_api_overlap

- 方法: `run` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL, parses first two lines as version and URL, accumulates the rest as a string, and notifies listeners upon completion or error.
- B 摘要: Registers a User object by encoding password, setting reg date, adding authority, generating hash, calling a phpBB forum registration URL to obtain forum ID, persisting the user, sending confirmation email, and returning success/failure.
- 静态失败原因: Static BERT models likely over-relied on lexical and API-level overlap (BufferedReader, InputStreamReader, URL, IOException, etc.) and missed the stark difference in overall purpose and control flow.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as clone due to the shared URL reading pattern and error handling, considering broad Type-3/Type-4 similarity where partial functionality overlap (reading from URL) is enough.
- 共享行为: Both open a URL connection and read lines using BufferedReader；Both catch IOException；Both use input stream readers
- 行为差异: Function A is a simple URL content reader/parser; Function B performs complex user registration with multiple side effects；Function A returns void; Function B returns boolean；Function A has custom French error messages; Function B uses English logging and throws RuntimeException；Function A notifies listeners; Function B does not
- 修正建议: Incorporate dataflow or control-flow analysis to capture the difference in imperative steps；Use method name and signature as additional features to distinguish void vs boolean and specific domain；Train with more diverse negative pairs that have similar API usage but different semantics

### case_id=2988 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `copyExternalResource`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles UI action events to configure settings like Graphviz path, image scaler, date format, etc.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: Low token overlap but both contain File-related classes (e.g., File, FileChooser) and try-catch blocks, causing superficial lexical or API overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have no common purpose or output; here they are completely unrelated.
- 行为差异: Function A is an event-driven UI handler that saves preferences and updates UI components.；Function B is a utility function for file copying.；No overlapping functionality.
- 修正建议: Improve negative sampling with unrelated tasks.；Incorporate semantic similarity based on program behavior, not just API usage.；Use longer context or dataflow analysis to distinguish event handling from file I/O.

### case_id=2989 FN benchmark_preference_bias

- 方法: `copyResource` vs `clonarFichero`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a resource (URL or file) to a destination file using byte-by-byte stream copy.
- B 摘要: Copies a file from an InputStream to a destination file using FileChannel transfer with boolean return status.
- 静态失败原因: Low lexical overlap (Jaccard 0.0597), different method names and natural language (English vs Spanish), and reliance on surface form similarity rather than semantic equivalence.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely considers both as Type-4 clones because they perform the same high-level task of copying file data, ignoring implementation details or language.
- 共享行为: Both copy data from a source to a destination file.
- 行为差异: A handles multiple source types (URL, file), B only FileInputStream.；A uses byte-by-byte copy, B uses channel transfer.；A throws exception on failure, B returns boolean.；B has print statements and error handling, A does not.
- 修正建议: Incorporate dataflow or CFG features to capture I/O operations.；Use cross-vocabulary embeddings to recognize synonyms like copy/clone.；Train with BCB-style annotations that accept partial functionality similarity.

### case_id=2990 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `read`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a fixed Twitter timeline URL via HTTP and returns the raw JSON response as a string.
- B 摘要: Reads a classpath resource file, splits it into sections based on '---' delimiters, and stores them in a list, throwing exceptions on error.
- 静态失败原因: The static BERT/GraphCodeBERT method likely overfitted on the lexical overlap of BufferedInputStream/readLine pattern, ignoring the distinct semantic contexts and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled non-clone because the functions have fundamentally different purposes, inputs, and outputs, despite sharing some I/O boilerplate.
- 共享行为: Both use BufferedReader and StringBuilder to read input.；Both read line by line until null.；Both accumulate lines into a StringBuilder.
- 行为差异: A accesses a hardcoded URL via HTTP; B loads a local resource via classpath.；A returns the accumulated string; B splits content into multiple sections.；A handles HTTP errors with logging; B throws custom exceptions.；A is private, returns String; B is public, returns void, populates a list.
- 修正建议: Incorporate control flow and data flow analysis to distinguish I/O patterns.；Consider method signatures and external API usage (e.g., HTTP vs. classpath).；Use structure-based differencing beyond token-level similarity.

### case_id=2991 FP boilerplate_overlap

- 方法: `run` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: An anonymous Runnable that reads a resource file from the classpath and sets the text in a MainPanel component.
- B 摘要: A static method that checks for software upgrades by querying a remote server and database, updating UI visibility accordingly.
- 静态失败原因: The model likely focused on lexical overlap in boilerplate code (BufferedReader, URL, while loop reading lines), ignoring the surrounding context that differentiates the purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have completely different purposes, even if they share common I/O patterns. The overall functionality is unrelated.
- 共享行为: Both use BufferedReader to read text line by line；Both involve GUI components and UI updates；Both use URL objects to access resources (local for A, remote for B)
- 行为差异: A reads a static resource from classpath; B queries a remote server for upgrade data；A sets text in a text component; B updates visibility of multiple UI components；A has no database interaction; B performs SQL queries and inserts；A handles exceptions silently; B throws Exception
- 修正建议: Use a model that captures semantic structure and dataflow, not just token sequences；Include method-level context (class, surrounding methods) to disambiguate purpose；Train on pairs with similar I/O patterns but different functionality to reduce false positives

### case_id=2992 FN partial_functionality

- 方法: `runScript` vs `retrieveTemplate`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from the applet's code base URL, returning its content as a string, or 'error!' on failure.
- B 摘要: Retrieves and caches the blog template from the blog's URL, returning the cached content.
- 静态失败原因: Static BERT models rely heavily on lexical and structural similarity. Here, token Jaccard is low (0.2449), method signatures differ, and control flow (do-while vs while) appears different. The model likely focused on these surface differences and missed the high-level functional similarity of fetching URL content.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers two functions as clones if they implement the same or similar functionality, even with structural differences. Both functions download a web resource and convert it to a string, so the core purpose is identical. Differences in caching, error handling, and buffering are viewed as implementation variations.
- 共享行为: Both open a URL connection and read the entire content into a string.；Both return the fetched string as the result.
- 行为差异: A takes a script name parameter; B has no parameters and uses a fixed blog URL.；A reads byte-by-byte and concatenates; B reads line-by-line using StringBuilder.；A returns 'error!' on any exception; B throws the exception.；B caches the result; A does not.
- 修正建议: Train on more diverse clone pairs that emphasize functional similarity despite structural differences.；Incorporate dataflow or dependency analysis to capture resource usage patterns (e.g., URL opening and reading).；Use code comments or documentation to infer intent.

### case_id=2993 FN partial_functionality

- 方法: `runScript` vs `postRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from the codebase URL and returns its content as a string.
- B 摘要: Sends an HTTP POST request with form data to a given URL and returns the response as a string.
- 静态失败原因: Static BERT/GraphCodeBERT models often rely on token overlap and structural similarity; these functions have low Jaccard similarity (0.246), different API calls (BufferedInputStream vs BufferedReader, URL vs URLConnection, etc.), and different method signatures, so the model deemed them dissimilar.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers functions that perform HTTP network I/O and return the response as clones, even if one is GET-like and the other POST-like, because the core behavior of fetching data over HTTP is similar.
- 共享行为: Both open a network connection to a URL；Both read data from the connection；Both handle exceptions by returning error strings or null；Both return the data read as a string
- 行为差异: Function a uses GET-like reading from a URL derived from codebase; function b uses POST with parameters to a direct URL；Function a reads raw bytes via BufferedInputStream; function b reads character lines via BufferedReader；Function a constructs URL from getCodeBase plus scriptName; function b takes full URL string；Function a returns 'error!' on exception; function b returns null and prints stack trace
- 修正建议: Improve training data with more diverse examples of HTTP operations；Incorporate knowledge of HTTP client patterns (e.g., using URLConnection) into the model；Use dataflow analysis to capture the sequence of connection establishment, I/O, and exception handling

### case_id=2994 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a new version of jEdit by fetching a version file from a URL and comparing build numbers.
- B 摘要: Imports biological sequences from a URL by parsing a FASTA-like format.
- 静态失败原因: The static BERT model likely over-relied on lexical overlap in API calls (InputStream, openStream, readLine, IOException) and structural similarity in the try-catch pattern, ignoring domain-specific logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because the core functionality is entirely different despite superficial API overlap.
- 共享行为: Both open a URL stream and read lines of text；Both handle IOExceptions in try-catch blocks
- 行为差异: Different data formats (version lines vs FASTA sequences)；Different processing logic (startsWith vs tokenization)；Different outputs (version check dialog vs list of sequences)
- 修正建议: Incorporate data-flow or control-flow analysis to distinguish real functionality；Use contrastive learning with negative samples that have API overlap but different semantics

### case_id=2995 FN partial_functionality

- 方法: `getDatasetsList` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Synchronized method that fetches a list of dataset identifiers from a remote URL, caching results in a map, and returns the list; throws RuntimeException on IOException.
- B 摘要: Method that registers a User object by encoding password, setting registration date, adding default authority, creating email hash, making an HTTP call to a forum to create a phpBB user, persisting the user via entity manager, and sending a confirmation email; returns true on success or false on mail exception, throws RuntimeExceptions on other failures.
- 静态失败原因: Static BERT/GraphCodeBERT models often rely on token-level patterns and may not capture the overall functional similarity of the HTTP-reading boilerplate. The low token Jaccard (0.16) and different method names, return types, and surrounding logic likely led the model to classify them as non-clones. Additionally, the models may be sensitive to the structural differences (synchronized vs not, different exception handling).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely annotated this as a clone due to the shared pattern of making an HTTP request and reading lines, which is considered a Type-4 (semantically similar) clone under a very broad interpretation of functionality, ignoring the different contexts and additional steps.
- 共享行为: Both open a URL connection；Both use BufferedReader to read lines from the HTTP response；Both catch IOException and wrap it in a RuntimeException
- 行为差异: Purpose: retrieving dataset list vs. user registration with multiple business logic steps；Data processing: A returns a cached list; B persists a user, sets hash, encodes password, sends email；Error handling: A only handles IOException; B handles IOException, NumberFormatException, and MailException separately；Synchronization: A is synchronized; B is not
- 修正建议: Use dataflow-aware models that capture side effects and control dependencies；Incorporate more abstract representations like API call sequences or structured input/output summaries；Train on a balanced set of Type-4 clones to better recognize shared functionality despite different contexts

### case_id=2996 FN partial_functionality

- 方法: `runInternal` vs `executeHttpGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP connection with redirects, downloads OPDS catalog or book, and manages progress and error handling.
- B 摘要: Performs an HTTP GET request and returns the response as a JSON object.
- 静态失败原因: Static BERT models might focus on lexical overlap (e.g., 'HttpGet', 'HttpURLConnection') and API usage patterns, missing the overall structure and control flow differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered them clones because both involve HTTP GET operations, but that is a very broad similarity.
- 共享行为: Both make HTTP GET requests.
- 行为差异: A handles redirects, downloads, error handling, and progress; B simply returns JSON.；A is complex with multiple branches; B is straightforward.；A interacts with UI components; B does not.
- 修正建议: Improve structural matching by comparing control flow and data flow graphs.；Use more context or dependency analysis to differentiate simple vs complex methods.

### case_id=2997 FN partial_functionality

- 方法: `main` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sets up and sends a POST request to RenRen API with multiple parameters, reads and prints the response.
- B 摘要: Reads lines from a URL, parses them into specific fields (version, url, informations) and notifies listeners upon completion or error.
- 静态失败原因: Static BERT models like GraphCodeBERT may rely heavily on token overlap and method-level patterns. The token Jaccard is very low (0.129), and the method names differ ('main' vs 'run'). The functions have different API calls and data structures, leading the model to classify them as non-clone. However, the model may miss the underlying shared control flow and I/O structure, which requires a deeper understanding of data-flow and graph dependencies that static models might not capture fully.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as clone because both functions share a common I/O pattern: reading lines from a URL input stream in a while loop, using the same Java constructs (BufferedReader, InputStreamReader). Despite different purposes, the core data retrieval code is structurally similar, fitting BCB's Type-3/4 broad clone definition.
- 共享行为: Both open a URL and read lines from it using BufferedReader and InputStreamReader；Both handle IOException；Both perform a loop reading lines until null
- 行为差异: Function A sends a POST request before reading; Function B just opens a URL (likely GET)；Function A prints response lines; Function B parses lines into specific variables；Function A uses specific RenRen API parameters; Function B has switch-case parsing；Function B handles errors with specific messages and notifies listeners; Function A does not
- 修正建议: Improve model's ability to recognize common sub-patterns like URL reading loops；Use data-flow analysis to capture that both functions open a URL connection and iterate over lines；Incorporate subgraph matching or structure-based similarity measures beyond tokens

### case_id=2998 FN partial_functionality

- 方法: `doRequest` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Serves an HTTP request by copying a resource identified by path from an HTTP context to the response output stream.
- B 摘要: Retrieves a resource as an InputStream, with caching to a local file system, using URL connections and HTTP conditional requests.
- 静态失败原因: Low token overlap and different method names/structures led the model to focus on lexical differences; it missed the shared pattern of URL resource access and stream handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'resource retrieval from URL' tasks, sharing high-level functionality of reading from a URL and outputting a stream, thus labeling them as broad Type-4 clones despite implementation differences.
- 共享行为: Both open a URL and read its contents as an input stream.；Both handle exceptions and stream closing.；Both produce an output stream (one writes to response, one returns as InputStream).
- 行为差异: A writes to HTTP response output stream; B caches to file and returns FileInputStream.；A uses servlet context; B uses cache hashtable and HTTP conditional requests.；A returns boolean; B returns InputStream or null.；B has caching logic; A does not.
- 修正建议: Use dataflow analysis to capture shared operations like opening URL and reading streams.；Train on more diverse examples of semantic clones with low lexical overlap.；Incorporate code summarization or functional categorization.

### case_id=2999 FN partial_functionality

- 方法: `runScript` vs `sendRequestObjectResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from the applet's codebase URL and returns its content as a string.
- B 摘要: Sends an HTTP request to a servlet, receives a response, saves it to a file, and returns the file path.
- 静态失败原因: Low token overlap (10.7%) and high syntactic difference; static model likely relied on surface features and missed the underlying common I/O pattern due to long code length in B.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'network resource retrieval' operations, accepting them as Type-4 semantic clones despite syntactic differences.
- 共享行为: Both establish a URL connection and read from an input stream；Both handle exceptions (IOException or general Exception)
- 行为差异: A reads a single file content; B sends a request and receives a response；A returns file content as string; B returns a file path after saving response；B includes extensive setup (server discovery, preferences, compression, file saving) not present in A
- 修正建议: Incorporate dataflow analysis to detect common URL connection and input reading patterns；Use structure-based representations that abstract away control flow differences；Include more training examples of partial functionality clones

### case_id=3000 FN partial_functionality

- 方法: `main` vs `setup`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts all its entries to files using ZipInputStream.
- B 摘要: Extracts native libraries from a JAR file based on system architecture and sets the library path.
- 静态失败原因: Static models like GraphCodeBERT rely on token overlap and syntactic similarity. The low Jaccard similarity (0.225) and different method names, string literals, and additional logic in B cause the model to treat them as different, missing the semantic similarity of the extraction routine.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as clones because both implement a common ZIP extraction algorithm, ignoring differences in source and filtering, focusing on the structural similarity of the core extraction loop.
- 共享行为: Both read entries from a ZipInputStream and write them to FileOutputStream using a buffer.
- 行为差异: A extracts all entries, B filters entries by the 'native' prefix.；A gets input from a URL stream, B from a local JAR file.；B checks system properties and sets the library path, which A does not.
- 修正建议: Train with more contrastive examples highlighting ZIP extraction pattern as a clone.；Incorporate data-flow analysis to recognize isomorphic extraction loops.
