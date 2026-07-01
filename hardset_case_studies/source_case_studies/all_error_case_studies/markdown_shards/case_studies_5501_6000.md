# Error Case Studies 5501-6000

- Source model: `configured-llm`
- Cases: `5501` to `6000`

### case_id=5501 FP boilerplate_overlap

- 方法: `dump` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Copies a file from source to target using buffered I/O streams and returns true on success.
- B 摘要: Reads comma-separated tokens from class fields and populates several sets and a hash map for configuration.
- 静态失败原因: The static model likely overfitted to common tokens like 'while', 'try', 'catch', 'IOException', and 'String' present in both functions, despite the low Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: Even under broad BCB criteria, these functions are not clones because they have no functional similarity or syntactic overlap beyond generic boilerplate (try-catch, loops).
- 共享行为: Both read data from some source (file vs string fields) but with completely different purposes and structures.
- 行为差异: Function A performs file copy; B parses configuration strings.；A uses file streams; B uses StringTokenizer and sets.；A returns boolean; B is void.；A has a simple loop; B has many nested loops and conditional formatting.
- 修正建议: Include method signature and purpose analysis.；Use functional similarity based on I/O operations vs data parsing.；Increase sensitivity to structural differences like unique API calls.

### case_id=5502 FN partial_functionality

- 方法: `File2String` vs `readURL`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a local file with fallback to classpath resource and returns its text content as a single string, exiting on failure.
- B 摘要: Reads a URL and prints each line to standard output, with exception handling and resource cleanup.
- 静态失败原因: Static BERT likely failed due to low lexical overlap (Jaccard 0.317) and significant differences in method signature, control flow, and I/O behavior, causing it to classify as non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled them as clones due to the shared pattern of reading text from an external source using BufferedReader, considering them as Type-3 or Type-4 clones despite differences in input type and output destination.
- 共享行为: Both read text from an input source line by line using BufferedReader.；Both use try-catch for exception handling.；Both involve opening a stream and reading lines.
- 行为差异: Input: A takes a directory and filename, B takes a URL.；Output: A returns a string, B is void and prints to console.；Error handling: A exits on failure, B prints stack trace and continues.；Resource loading: A has fallback to classpath, B opens URL directly.
- 修正建议: Incorporate dataflow analysis to capture the core reading pattern.；Use contrastive learning on pairs with similar structure but different I/O destinations.；Consider method-level semantics beyond lexical tokens.

### case_id=5503 FP partial_functionality

- 方法: `getWebByUrl` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches a web page and writes its content to a file, recursively processing embedded URLs up to a depth limit.
- B 摘要: Constructs a Swing-based web browser GUI that loads a URL, optionally transforms XML with XSLT, and displays the result.
- 静态失败原因: Static models may rely on lexical and structural similarities (e.g., both contain URL, BufferedReader, try-catch, while loops) and fail to capture the overarching intent difference.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels as non-clone because the functions serve completely different purposes (file downloader vs. GUI browser). The shared URL reading is too generic to override the overall functional difference.
- 共享行为: Both open a URL and read its content line by line using BufferedReader.
- 行为差异: A writes content to a file; B displays content in a GUI.；A recursively processes URLs; B does not.；B includes GUI construction and XML/XSLT handling; A has no GUI.；B handles different exception types; A catches generic Exception.
- 修正建议: Improve model's ability to capture high-level semantics using program dependency graphs or call graph context.；Incorporate task-specific features (e.g., file I/O vs. GUI components).；Use contrastive learning with negative samples of similar tokens but different behavior.

### case_id=5504 FN lexical_or_api_overlap

- 方法: `getResourceAsStream` vs `forBundle`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches a resource from a URL with caching and returns an InputStream.
- B 摘要: Creates a JAR file from a bundle's VM files and installs it as a plugin.
- 静态失败原因: Static BERT methods often rely on token overlap and structural similarity; here the Jaccard is low but both use similar API calls (URL, streams, exceptions) which may cause false negative if the model is not sensitive to high-level semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might have considered them clones due to common use of URL and file I/O patterns, and both appear in a similar context (e.g., enterprise Java apps), but the actual logic is very different.
- 共享行为: Both use URL and streams for I/O operations；Both handle exceptions and print stack traces；Both involve file system operations
- 行为差异: Function A returns an InputStream after caching, while Function B has no return value and performs plugin installation；Function A has caching logic and conditional HTTP handling, while Function B uses bundle entries and ZipOutputStream；Function A deals with web resources, while Function B deals with OSGi bundles
- 修正建议: Improve modeling of long-range dependencies and control flow；Incorporate dataflow information to distinguish caching vs installation；Use more discriminative features like method signatures and return types

### case_id=5505 FN benchmark_preference_bias

- 方法: `loadExistingAntlibs` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Loads ant library definitions from classpath resources by reading URLs, iterating lines, and loading each antlib.
- B 摘要: Opens a URL connection to a hardcoded web address, reads content line by line, and logs the concatenated string.
- 静态失败原因: Static BERT models likely emphasized the significant syntactic and semantic differences (different method names, URI resolution vs simple reading, different exception handling) and missed the high-level IO pattern that BCB considers similar.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them clones because both perform similar I/O operations (opening a stream from a URL, reading lines, handling input), matching a broad Type-3/Type-4 pattern where the core structure is similar despite different specific tasks.
- 共享行为: Both open a URL or URLConnection and read lines using BufferedReader；Both close the input stream and reader after processing
- 行为差异: A reads from classpath resources via an enumeration; B reads from a single hardcoded web URL；A processes each line as a package name and loads a resource; B appends lines to a string buffer and logs；A involves URI resolution and custom error handling; B has simpler exception handling
- 修正建议: Train with BCB-style annotation labels or fine-tune on a dataset that captures broad functional similarity；Use contrastive learning to emphasize high-level patterns (e.g., reading from URL) while tolerating low-level differences；Incorporate hierarchical representations that capture both abstract patterns and detailed implementations

### case_id=5506 FP lexical_or_api_overlap

- 方法: `getFrameworkFactory` vs `retrieveTemplate`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a framework factory by reading a service provider configuration file from the classpath.
- B 摘要: Retrieves a web page template by reading content from a URL and caching it.
- 静态失败原因: Static models like BERT might overemphasize lexical and structural similarities (e.g., same method signature pattern, use of BufferedReader and URL), ignoring the different domain-specific operations (class loading vs. string building) and the different sources (classpath vs. HTTP).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers them non-clones because the core functionality differs: one is a service loader, the other is a web page fetcher. Despite similar structural patterns, the semantic intent is different.
- 共享行为: Both read line by line from an input stream；Both use BufferedReader and InputStreamReader；Both throw Exception on failure
- 行为差异: Source of data: classpath resource vs. HTTP URL；Processing: filters comments and instantiates class vs. appends all lines to string；Return type: FrameworkFactory object vs. String；Caching: no caching vs. cached template
- 修正建议: Include more context from surrounding code or method names to distinguish intent；Add a step that checks for semantic role of the input/output (e.g., is it loading a class or fetching content?)；Use dataflow analysis to track how the read data is used (e.g., reflection instantiation vs. string concatenation)

### case_id=5507 FP boilerplate_overlap

- 方法: `handleHandshake` vs `readVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: handles Minecraft handshake authentication by validating username and making an HTTP request to verify server key
- B 摘要: reads version information from a classpath resource file parsing key-value pairs
- 静态失败原因: The static model likely over-weighted common lexical patterns (BufferedReader, url.openStream(), readLine, close, try-catch) and missed the semantic context of completely different domains (network authentication vs. resource parsing)
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the functions have entirely different purposes and only share superficial I/O boilerplate, which does not constitute functional similarity
- 共享行为: Both use BufferedReader and InputStreamReader to read from a stream；Both handle IOException and close resources in finally block
- 行为差异: A performs authentication logic with HTTP request; B parses local resource file；A sends network packets and shuts down connection; B sets internal version fields；A uses external URL; B uses ClassLoader.getSystemResource
- 修正建议: Incorporate type-aware embeddings to differentiate argument types (Packet2Handshake vs URL)；Add control-flow analysis to capture different decision structures；Increase penalty on low token overlap (Jaccard 0.17) when other features disagree

### case_id=5508 FN lexical_or_api_overlap

- 方法: `doImageProcess` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Serves an image file from a URL or input stream, optionally resizing it, and writes it to an HTTP response.
- B 摘要: Modifies a key-value pair in a locale-specific properties file, creating it if necessary, by reading, updating, and writing the file.
- 静态失败原因: Static BERT models rely on token overlap and syntactic patterns; the low Jaccard similarity (0.129) and distinct domain-specific terms (image vs. properties, HttpServletResponse vs. FileWriter) caused the model to predict non-clone, missing the abstract 'read-modify-write' pattern that BCB annotators considered.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as 'resource modification' methods that perform I/O and error handling, aligning with a broad Type-4 semantic similarity despite different domains.
- 共享行为: Both involve reading from an input source (image stream or properties file) and writing to an output destination (HTTP response or file).；Both check for missing resources and throw or handle exceptions.
- 行为差异: Function A serves binary image data with optional resizing; Function B modifies text-based properties files.；Function A uses HTTP response output stream; Function B uses FileWriter.；Function A reads from a URL or inputStream; Function B reads from a classpath resource or file.；Function B performs line-by-line parsing and replacement; Function A may resize images using getImageBytes.
- 修正建议: Incorporate source code structural features like control flow and data flow.；Use models that capture long-range dependencies and abstract operations.；Augment training data with more diverse semantic clone pairs.

### case_id=5509 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter timeline from a fixed URL and returns the JSON content as a string.
- B 摘要: Searches Google images, parses HTML to extract image URLs, stores them, and displays the first image on a UI component.
- 静态失败原因: The model may have falsely predicted clone due to over-reliance on the common boilerplate pattern of HTTP GET followed by BufferedReader.readLine(). It likely ignored the significant differences in URL construction, parsing logic, and side effects, treating the structural skeleton as a clone indicator.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers them non-clones because the core functionality is different (Twitter feed retrieval vs Google image search with UI update). The shared HTTP GET + line reading is too generic and does not constitute sufficient functional similarity to be a Type-3 or Type-4 clone under BCB guidelines.
- 共享行为: Both perform an HTTP GET request to a remote server.；Both read the HTTP response line by line using a BufferedReader.
- 行为差异: Different URLs: fixed Twitter endpoint vs dynamically constructed Google image search URL.；Different HTTP libraries: HttpClient (Apache) vs HttpURLConnection.；Different response processing: A appends all lines to a StringBuilder and returns; B concatenates lines, replaces newlines, splits by regex, and collects image URLs, then updates a UI component.；Different error handling: A logs errors and returns partial result; B shows error dialogs and enables UI button.
- 修正建议: Augment training data with more contrasting examples sharing I/O boilerplate but different business logic.；Incorporate data-flow analysis to distinguish how the read data is used (e.g., returned as-is vs parsed for specific content).；Use graph-based representations that capture semantic roles of variables beyond shallow tokens.

### case_id=5510 FP lexical_or_api_overlap

- 方法: `getTicketsForQueue` vs `getNetworkServersIPs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches open tickets from a Request Tracker system via HTTP, parses ticket IDs, and retrieves each ticket.
- B 摘要: Retrieves server IPs from a network configuration file over HTTP, parsing lines after a marker.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on shared tokens (URL, BufferedReader, readLine, etc.) and similar control flow structure, ignoring semantic differences in data processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone (0) because the functions have fundamentally different purpose and logic, despite some superficial API similarity.
- 共享行为: Perform HTTP requests to fetch data；Read response line by line with BufferedReader；Use try-catch for exception handling；Return a collection of parsed items
- 行为差异: Different domain: ticket tracking vs network server discovery；Different output types: List<RTTicket> vs Vector<String>；Different parsing logic: ticket ID extraction vs IP extraction；Different error handling: throws exceptions vs print stack traces
- 修正建议: Incorporate data flow analysis to distinguish different parsing targets；Use type information of return values and parameters；Include domain-specific knowledge or broader context；Apply more robust structural matching

### case_id=5511 FP lexical_or_api_overlap

- 方法: `run` vs `callApiPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads vector tile geometry from a URL (http or file), parses GeoJSON, and adds to a data structure.
- B 摘要: Sends an HTTP POST request with parameters and returns an InputStream, handling timeouts and response codes.
- 静态失败原因: Static BERT likely over-relied on lexical overlap of common API patterns (URL, InputStream, try-catch) and missed the distinct business logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these non-clones because they serve different purposes (tile loading vs generic API call) despite shared HTTP boilerplate.
- 共享行为: Both open URL connections and read input streams；Both handle IOExceptions
- 行为差异: A also handles file:// protocol and parses GeoJSON into geometry objects；B sets HTTP method POST, sends parameters, and checks response status
- 修正建议: Incorporate data flow and control flow graphs to distinguish core functionality；Train on more diverse examples to reduce boilerplate bias

### case_id=5512 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `read`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft handshake by validating server key and optionally sending a login packet after verifying session via HTTP.
- B 摘要: Reads a camera log from a URL, parses each line into a CameraLogRecord, and stores sorted records.
- 静态失败原因: Static BERT may have focused on the lexical overlap of 'BufferedReader', 'InputStreamReader', and 'url.openStream()', ignoring the divergent control flow and domain logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions serve entirely different purposes despite a minor I/O overlap, which does not constitute Type-3/4 similarity.
- 共享行为: Both open a URL and read line by line using BufferedReader and InputStreamReader
- 行为差异: A validates handshake data and interacts with a game session server; B parses log records and sorts them；A performs network shutdown on invalid conditions; B collects and sorts records；A uses HTTP GET to a session server; B reads from a static URL；A may send a packet; B only processes local data
- 修正建议: Incorporate control-flow and data-flow features；Add context about function names and surrounding class；Use a more discriminative loss or contrastive learning for fine-grained differences

### case_id=5513 FN benchmark_preference_bias

- 方法: `read` vs `sendRequestObjectResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a file or URL and returns a status code.
- B 摘要: Sends an XML request to a servlet, saves the response to a file, and returns the file path.
- 静态失败原因: Static models rely on lexical and structural similarity, which are low here (Jaccard 0.084). They correctly identified functional dissimilarity but disagreed with the BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label might be based on superficial similarity of using URL and streams, or a labeling error; it does not align with typical Type-3/4 functionality.
- 共享行为: Both handle URL connections and stream I/O.
- 行为差异: A only reads input; B writes a request and reads response.；A returns an integer status; B returns a file path string.；A has simple error handling; B has extensive setup, logging, and UI interactions.；B involves compression, preferences, and file management.
- 修正建议: Verify BCB annotation for this pair; consider relabeling as non-clone.；Use dynamic analysis or deeper semantic understanding to avoid false positives from broad I/O patterns.

### case_id=5514 FN partial_functionality

- 方法: `copyResource` vs `fileCopy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource, either from a URL or a file, to a destination file using single-byte streaming.
- B 摘要: Copies a source file to a destination file after extensive validation, using buffered streaming with proper resource cleanup.
- 静态失败原因: Low lexical overlap (Jaccard 0.21) and differing control flow structures mask the underlying semantic similarity of the copy operation.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often annotates clones based on shared core functionality (file copying) despite differences in error handling, source type, or performance optimizations.
- 共享行为: Copy data from an input source to a file output stream
- 行为差异: Source can be URL or file vs only file；Validation is minimal vs extensive；Reads byte-by-byte vs using buffer；Simple close vs try-finally resource management
- 修正建议: Use dataflow-aware models that capture input-output transformations；Augment training with diverse file copy implementations；Employ contrastive learning to focus on core behavior over surface form

### case_id=5515 FN benchmark_preference_bias

- 方法: `logging` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Logs the content of an inbound message by copying its input stream to a cached output stream and writing the payload to a logger.
- B 摘要: Builds a site for editing by reading XML files, performing XSL transformations, and writing output files for each page.
- 静态失败原因: Static BERT correctly identified non-clone due to low token overlap and different functionality, so it didn't fail; the BCB label may be incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider both as clone due to shared use of logging and I/O operations, but this is likely a mislabel.
- 共享行为: Both involve reading from input streams and handling I/O exceptions.
- 行为差异: Different purposes: logging vs. site building.；Different parameters and return types.；Different output: log message vs. file output.
- 修正建议: Re-evaluate BCB annotation for this pair; likely non-clone.

### case_id=5516 FN partial_functionality

- 方法: `main` vs `copyExternalResource`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a hardcoded URL and extracts its entries to the current directory using ZipInputStream.
- B 摘要: Copies a source file to a destination file using FileChannel with try-finally cleanup.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap and structural similarity, which are low (token Jaccard=0.13). The methods differ in name, control flow, and API usage, making it hard to detect the high-level semantic similarity that BCB considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to both performing a 'file copy' operation at a high level: A copies a remote resource to local files (via extraction), B copies a local file to another location. The similarity in intent (transferring data from one place to another) and the use of file streams may have been considered sufficient for a Type-4 clone.
- 共享行为: Both involve reading from an input source and writing to output files.；Both use file I/O streams.；Both are static methods.
- 行为差异: A uses HTTP/URL handling and ZIP extraction; B is a simple file copy.；A writes multiple files named by zip entries; B writes a single file.；A uses BufferedOutputStream; B uses FileChannel.transferFrom.；A has no error handling (throws Exception); B has try-finally with closeQuietly.
- 修正建议: Enhance model with a broader understanding of file I/O operations.；Use code summarization or docstring similarity to capture high-level intent.；Incorporate data-flow analysis to see that both read from a source and write to files.

### case_id=5517 FP boilerplate_overlap

- 方法: `uncaughtException` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles uncaught exceptions by showing an error dialog and optionally launching the bug report URL.
- B 摘要: Handles action events for a settings panel, saving various preferences and updating UI components.
- 静态失败原因: The model likely overfit on the common 'event handler' pattern, including dialog creation, conditional logic, and try-catch blocks, ignoring the distinct domains and separate method names.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the methods share no functional overlap; one is for exception handling, the other for GUI preferences, with very low token similarity.
- 共享行为: Both are event-handling methods triggered by user actions；Both display dialogs and update system state based on user choices；Both contain conditional branches and use try-catch for error handling
- 行为差异: Different events handled: uncaught exceptions vs action commands；Different UI libraries: SWT (A) vs Swing (B)；Different purpose: error reporting (A) vs settings configuration (B)；Different output actions: clipboard copy and URL launch (A) vs preference storage (B)
- 修正建议: Incorporate method name and broader context to distinguish handler types；Train on more diverse examples to avoid shallow pattern matching；Use code structure analysis to differentiate between error handling and UI configuration

### case_id=5518 FN benchmark_preference_bias

- 方法: `copyResource` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file byte by byte.
- B 摘要: Tests StraightStreamReader by writing predetermined bytes to a file and reading them back with various methods to verify correctness.
- 静态失败原因: The static model likely correctly identified the lack of deep semantic equivalence and low token overlap, but BCB label may be an error or based on very broad criteria.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone due to superficial similarity in file I/O operations (reading/writing bytes) and possibly due to both being related to stream handling, but the overall semantics and purpose are very different.
- 共享行为: Both use FileInputStream and FileOutputStream；Both read/write bytes in loops
- 行为差异: Code A is a generic resource copy; Code B is a specific test with validation and error checking；Code B writes specific bytes (0x00-0xFF) then reads back; Code A does not write predetermined data；Code B uses a custom StraightStreamReader class; Code A uses standard InputStream/OutputStream；Code B has multiple read loops with different buffer offsets and sizes; Code A has a simple single read-write loop
- 修正建议: Consider adjusting BCB annotation guidelines to exclude such pairs with different purposes；Enhance model to better detect partial functionality? But in this case, the model prediction seems correct.

### case_id=5519 FP boilerplate_overlap

- 方法: `ExternalDecoder` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Constructor that starts a thread to copy input stream to process output and close.
- B 摘要: Main method that reads a Prolog file, generates adapter code, and writes output JAR.
- 静态失败原因: The model likely overfitted on boilerplate patterns such as try-catch, IOUtils calls, and general structure, failing to capture the high-level semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the functions have no functional or structural similarity, performing entirely different tasks.
- 共享行为: Both use try-catch blocks for exception handling；Both involve I/O operations
- 行为差异: Function A is a constructor initializing a decoder and spawning a thread；Function B is a complex main method for code generation with multiple steps；Overall purpose and logic are completely unrelated
- 修正建议: Incorporate dataflow or control-flow analysis to better distinguish different behaviors；Use a more discriminative representation focusing on core logic rather than common idioms

### case_id=5520 FP lexical_or_api_overlap

- 方法: `googleImageSearch` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs a Google image search by querying an HTTP URL, parses the HTML response for image URLs, stores them, and displays the first image as an icon.
- B 摘要: Loads a URL with optional HTTP authentication, reads the response line by line, writes it to a temporary file, and updates a status label with the file size.
- 静态失败原因: The static BERT/GraphCodeBERT model likely focused on the overlapping API tokens (e.g., URL, BufferedReader, HttpURLConnection) and the similar control flow (try-catch, while loop), ignoring the different data processing and final output. The model lacks understanding of the broader task context and the specific domain (image search vs. file download).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators likely considered these as non-clones because the overall functionality is completely different: one is an image search, the other is a file download. The shared low-level I/O pattern is insufficient to override the distinct high-level purposes.
- 共享行为: Open a URL connection (HttpURLConnection or URLConnection) and read lines using BufferedReader
- 行为差异: Function A is specific to Google Images, while B is a generic URL loader；A parses HTML to extract image URLs; B writes raw response to a file；A handles authentication; B does not；A updates UI with an image icon; B updates UI with file size
- 修正建议: Incorporate data flow analysis to track how input data is transformed (e.g., HTML parsing vs. file writing)；Enhance model with task-level semantics or use contrastive learning on functional roles；Consider additional features like method names, comments, or external API usage to disambiguate purpose

### case_id=5521 FP lexical_or_api_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that processes command-line arguments to parse Prolog files and generate adapters.
- B 摘要: Utility method to copy a file from source to destination with progress display and overwrite confirmation.
- 静态失败原因: Static models likely over-relied on lexical overlaps like 'File', 'IOException', 'System.out' and structural patterns like try-catch, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the two functions serve completely different purposes: one is a main entry for a code generator, the other is a file copy utility. They share only superficial boilerplate and API calls.
- 共享行为: Both handle files and use File class；Both use try-catch for exception handling；Both print messages to standard output
- 行为差异: A parses Prolog and generates Java classes, B copies a file byte by byte；A involves complex adapter generation and class writing, B is a simple file copy with progress bar；A checks command-line arguments, B checks file existence and permissions
- 修正建议: Incorporate method name/signature as a strong clue；Add training on distinguishing file I/O utilities from other logic；Use awareness of high-level task structure (e.g., main vs. utility)

### case_id=5522 FN benchmark_preference_bias

- 方法: `getFileContentAsString` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a file from classpath or file system and returns its content as a string using IOUtils.copy.
- B 摘要: Builds a site for editing by processing multiple pages, applying XSLT transformations, and writing output files with various string manipulations.
- 静态失败原因: Static BERT correctly predicted non-clone based on low lexical overlap and different semantics; BCB label appears incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled as clone due to superficial similarity in reading files and producing strings, but this ignores the vast difference in complexity and purpose.
- 共享行为: Both read file input and produce string output (e.g., IOUtils.copy vs FileInputStream/readfilestr).
- 行为差异: Function A is a simple utility reading a single file; B is a complex site builder with loops, transformations, and multiple file operations.；Function B interacts with many external objects (Transformer, Page, FileSystem) and has extensive error handling; A has minimal error handling.；The overall purpose is entirely different: one is file-to-string, the other is multi-step site generation.
- 修正建议: Reevaluate BCB annotation for this pair; confirm if it should be non-clone.；If model is to agree with BCB, it would need to ignore functional differences and focus on shared low-level I/O operations.

### case_id=5523 FN boilerplate_overlap

- 方法: `copy` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Recursively copies a file or directory from source to destination using byte-level I/O.
- B 摘要: Builds a site by reading XML/HTML templates, transforming them, and writing output files; involves complex string replacement and file operations.
- 静态失败原因: Static BERT models rely heavily on lexical and syntactic overlap, which is very low here (Jaccard=0.097). The method names and overall structure differ significantly, leading the model to predict non-clone.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a clone because both functions involve reading from a file and writing to another file, a common pattern that could be considered Type-3/Type-4 similarity despite different contexts and levels of abstraction.
- 共享行为: Both perform file I/O operations, reading from a source and writing to a destination.；Both handle I/O exceptions and logging.；Both use character array buffers for reading/writing.
- 行为差异: Function A is a generic recursive file copy; Function B is a specific site builder with transformation and string replacement.；Function A uses byte-by-byte copying; Function B uses buffered reading and separate writing methods.；Function A operates on a single file/directory; Function B processes a list of pages with multiple properties.；Function A uses recursion for directories; Function B uses loops and external libraries for FTP and regex.
- 修正建议: Use a dataflow-aware model to capture common I/O patterns beyond surface tokens.；Incorporate AST-based features to identify structural similarities in error handling and resource management.；Increase training data with diverse file manipulation tasks to recognize higher-level functional similarities.

### case_id=5524 FN partial_functionality

- 方法: `read` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads from a file or URL, returns status code indicating success or failure.
- B 摘要: Reads from a URL, parses lines to extract version and URL, notifies listeners on completion.
- 静态失败原因: Low lexical overlap (Jaccard 0.189) and different method signatures likely misled the model, which failed to capture the common pattern of URL reading and error handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators may consider both as Type-4 clones because they share the high-level behavior of reading from a URL with exception handling, despite differences in processing logic.
- 共享行为: Both read from a URL；Both handle IOException with error handling；Both open a stream and read input
- 行为差异: A reads from file or URL, B only from URL；A uses BufferedInputStream and delegates to another read method, B uses BufferedReader and parses text；A returns a status code, B sets instance variables and notifies listeners；B has specific parsing logic for version and url fields
- 修正建议: Improve representation of data flow and control flow to capture high-level patterns；Use contrastive learning with positive pairs that have low lexical overlap but similar functionality

### case_id=5525 FN partial_functionality

- 方法: `read` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file or URL and returns an integer status code.
- B 摘要: Reads a file or classpath resource and returns its content as a string, exiting on failure.
- 静态失败原因: Low token overlap (0.164) and significant differences in return type, control flow, and error handling cause static embedding models to miss the shared purpose of resource reading. The model focuses on surface syntax rather than underlying intent.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both functions ultimately read data from a file or URL resource, albeit with different return types and error handling. The core functionality of opening and reading a resource is similar, fitting a broad Type-3 or Type-4 clone.
- 共享行为: Both open and read data from a file or URL.；Both handle IOException by setting a status or exiting.；Both attempt to read from a resource specified by name.
- 行为差异: Function A returns an integer status, while B returns a String content.；Function B reads line by line and appends; A calls another read method.；Function B includes fallback to classpath resource and System.exit on error; A uses status codes.；Function A handles both HTTP URLs and local files; B primarily uses classpath after file failure.
- 修正建议: Increase training data for resource-reading patterns across different APIs.；Incorporate structural alignment or program slicing to focus on I/O operations.；Use dataflow analysis to capture that both methods attempt to open a stream from a resource.

### case_id=5526 FN benchmark_preference_bias

- 方法: `copyFile` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using byte stream.
- B 摘要: Modifies a properties file for a given locale by copying a default file if missing, then updating or appending a message.
- 静态失败原因: Static models rely on token overlap and structural similarity; low Jaccard (0.14) and differing method signatures/tasks led to non-clone prediction, missing the shared low-level copy pattern.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them Type-4 clones because both contain a file-copy sub-task (reading from one file and writing to another), even though the overall functionality differs significantly.
- 共享行为: Both perform file I/O with input and output streams.；Both use a while loop to read and write data.
- 行为差异: Function A is a generic file copy; Function B specifically manages localization properties.；Function B involves conditional file creation, property parsing, and string manipulation.；Function B has error handling and multiple file operations beyond simple copy.
- 修正建议: Use models that can detect sub-function clones or partial functionality matches.；Consider ensemble methods that weigh both token-based and semantic embeddings.；Re-evaluate BCB annotation for potential overbroad labeling.

### case_id=5527 FP other

- 方法: `perform` vs `encrypt`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Processes a web classification request: validates session, extracts parameters, builds XML data, sends HTTP POST, parses XML response, and stores results in session.
- B 摘要: Computes MD5 hash of a password and returns hex string.
- 静态失败原因: Despite low token overlap, the model might have been misled by both methods containing common English words like 'return', 'String', 'null', or by both having a similar structure of method definition. Additionally, the model may have failed to capture the long-range dependencies and complex control flow in function A, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions perform completely different tasks: one is a web controller handling classification logic, the other is a cryptographic hash utility. No semantic overlap in functionality.
- 共享行为: Both are single public methods that accept input and return output.
- 行为差异: Function A has complex control flow with session management, HTTP networking, XML parsing; Function B is a simple hash computation.；Function A interacts with external services; Function B is self-contained.；Function A returns ActionForward; Function B returns String.
- 修正建议: Increase diversity of training data to include more non-clone pairs with similar superficial structures but different semantics.；Use better representation that captures control flow and data dependencies.；Train with contrastive learning to discriminate functional semantics.

### case_id=5528 FP boilerplate_overlap

- 方法: `sendPost` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with Accept-Language header, writes parameters via PrintWriter, reads response concatenating lines, returns empty string on error.
- B 摘要: Sends an HTTP POST request with explicit POST method and multiple headers (Content-Type, Content-Length, Content-Language, no cache), writes parameters via DataOutputStream, reads response appending carriage returns, returns null on error and disconnects in finally.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overfitted on common lexical tokens (URL, HttpURLConnection, setDoOutput, BufferedReader) and the standard HTTP POST pattern, ignoring the specific differences in headers and error handling. The high token overlap (Jaccard=0.325) and similar control flow misled the model into false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators likely considered these non-clones because the differences in headers, exception handling, and response formatting are non-trivial, even though the core HTTP POST logic is similar. The broader BCB annotation guideline often requires more than just common boilerplate to label as clones.
- 共享行为: Both perform an HTTP POST request to a given URL with parameters.；Both set doOutput and doInput to true.；Both read the response line by line using BufferedReader.；Both handle exceptions and return a string result.
- 行为差异: Function A sets only Accept-Language header; Function B sets Content-Type, Content-Length, Content-Language, and disables cache.；Function A uses PrintWriter; Function B uses DataOutputStream to write parameters.；Function A concatenates lines without extra carriage returns; Function B adds \r after each line.；Function A handles exception by displaying message and returning empty string; Function B prints stack trace and returns null.
- 修正建议: Incorporate data-flow analysis to distinguish different stream and connection usage patterns.；Train on more diverse HTTP client examples with varying headers and error handling.；Use contrastive learning to emphasize functional differences beyond lexical similarity.；Add attention to method-level configuration details like exception handling and response formatting.

### case_id=5529 FN partial_functionality

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a single file using NIO FileChannel.
- B 摘要: Builds an editable site by processing multiple pages with XML transformations and file I/O.
- 静态失败原因: Model likely focused on low token overlap (0.0476) and structural differences, missing the partial functionality similarity in file I/O operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone due to common use of file I/O APIs (FileInputStream, FileOutputStream) and stream closing, treating them as type-4 clones.
- 共享行为: Both perform file I/O operations using FileInputStream and FileOutputStream
- 行为差异: copyFile copies one file; buildSiteForEdit processes many files with complex transformations；buildSiteForEdit includes XML parsing, DOM handling, and string replacements；buildSiteForEdit has extensive logging and parameter handling
- 修正建议: Incorporate data flow analysis to detect shared I/O patterns；Use multiple granularity levels for clone detection, including API-level similarity

### case_id=5530 FN partial_functionality

- 方法: `onlyFileCopy` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file using FileChannel transferTo with chunked transfer.
- B 摘要: Handles HTTP GET request by resolving a Page, checking permissions, and rendering response with optional caching to temp file.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on token-level overlap and method names, which were very low. The broad functional similarity (I/O copy) was not captured due to large lexical and structural differences, leading to a false negative relative to BCB's loose annotation standards.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled them as clones due to a broad interpretation of Type-4 similarity: both functions ultimately copy data from one source to another (file-to-file vs HTTP response-to-file) using I/O streams, despite vastly different contexts and functionalities.
- 共享行为: Both perform file I/O operations (reading/writing files)；Use try-catch-finally for resource management
- 行为差异: A is a pure file copy utility; B is a complex web request handler with multiple concerns；A uses FileChannel for efficient binary transfer; B uses FileWriter for text output；A's primary purpose is copying; B's primary purpose is serving web pages with caching as a side effect
- 修正建议: Incorporate data-flow analysis to detect implicit input-output relationships；Use language models with longer context to capture high-level purpose similarity

### case_id=5531 FN benchmark_preference_bias

- 方法: `displayDiffResults` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Generates an HTML diff report and opens it in a browser.
- B 摘要: Transforms and writes HTML pages for editing based on XML and properties.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on lexical overlap (Jaccard=0.0868 is very low) and structural patterns; the low token overlap correctly suggests non-clone, but BCB's broader definition may overemphasize superficial I/O patterns.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered them clones due to both being HTML output generation functions that write to files and use IO streams, despite vastly different semantics and complexity.
- 共享行为: Both write HTML content to files.；Both use FileOutputStream or FileWriter for output.；Both involve reading from an input source.
- 行为差异: Function A creates a temporary file and launches a browser; B writes to specified output path without launching.；Function A writes diff results (tables); B applies XSLT transformation and processes multiple pages.；Function A uses BufferedWriter and StringBuffer; B uses StringWriter and FileSystem helper.；Function A has no XML/XSLT processing; B heavily uses XSLT and DOM.
- 修正建议: Increase sensitivity to deeper semantic similarity beyond I/O patterns.；Use data-flow analysis to distinguish between file generation tasks.；Adjust BCB annotation criteria to avoid grouping functions with only high-level I/O similarity.

### case_id=5532 FN partial_functionality

- 方法: `getResourceAsStream` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource by name with caching and HTTP conditional get, returning an InputStream.
- B 摘要: Copies a file or directory recursively from source to destination.
- 静态失败原因: Static BERT models rely on token-level similarity and may miss the partial functional overlap in streaming logic, leading to a non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone due to the shared low-level pattern of streaming bytewise copy (Type-4), despite different high-level purposes.
- 共享行为: Both read from an input stream and write to an output stream byte by byte；Both handle exceptions and close streams in finally blocks
- 行为差异: A includes URL resolution, HTTP connection, caching logic, and returns an InputStream; B recursively copies directories and handles file existence checks；A uses System.out for debug messages; B uses log.error for errors
- 修正建议: Incorporate dataflow or control-flow features to capture low-level I/O patterns；Train with synthetic partial clones to improve robustness to structural similarity

### case_id=5533 FP other

- 方法: `perform` vs `getMD5_Base64`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Processes an HTTP request to classify a concept by interacting with a remote URL and managing session attributes.
- B 摘要: Computes MD5 hash of a string and returns the Base64 encoded result.
- 静态失败原因: The static model likely made a false positive due to relying on superficial token overlaps or boilerplate patterns (e.g., try-catch, string building) that are coincidentally present in both methods, despite vastly different semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels only functionally equivalent or highly similar code as clones; these functions share no common behavior, so they are correctly marked as non-clones.
- 行为差异: Different input and output types and purposes；No overlapping logic or data flow；Code A involves web, session, XML, and error handling for classification; code B is a pure cryptographic hash utility
- 修正建议: Improve training data to include more diverse negative examples with low lexical overlap；Use contrastive learning to better separate distinct semantic categories；Incorporate deeper structural or dataflow analysis beyond token-level patterns

### case_id=5534 FP lexical_or_api_overlap

- 方法: `importSequences` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads sequences from a URL in FASTA-like format and stores names and sequences in lists.
- B 摘要: Checks for a newer version of jEdit by reading a version file from a URL and comparing build numbers.
- 静态失败原因: The model likely overfitted on lexical overlap (e.g., 'URL', 'openStream', 'InputStream', 'IOException') and similar control flow (try-catch, loop), missing the semantic divergence in purpose and data processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires significant functional overlap or similar core logic. Here, only generic boilerplate of opening a URL and reading lines is shared, not the specific domain logic, so BCB would not label as clone.
- 共享行为: Both open a URL and read text input.；Both handle IOException with catch blocks.
- 行为差异: Different purposes: importing biological sequences vs. checking software version.；Different parsing logic: reading until '>' and tokenizing vs. checking line prefixes.；Different output: storing in lists vs. showing messages to user.；Different exception handling: A catches multiple specific exceptions, B only catches IOException.
- 修正建议: Train with more contrastive examples that have similar APIs but different semantics.；Incorporate data flow analysis to distinguish variable usage patterns.；Use domain-specific pre-training or fine-tuning to capture functional intent.

### case_id=5535 FP partial_functionality

- 方法: `sendPost` vs `readURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Opens a URL, reads its content line by line, and prints each line to standard output.
- 静态失败原因: Static model was misled by lexical overlap in URL reading pattern (BufferedReader, while loop) and try-catch structure, ignoring fundamental differences in HTTP method and output behavior.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled 0 because functions have different purposes (send data vs read data) and different output (return string vs console print). Similarity in reading code is considered boilerplate not sufficient for clone label.
- 共享行为: Open URL connections；Read response lines using BufferedReader
- 行为差异: A uses POST method with output stream to send parameters; B uses GET via openStream；A returns concatenated result; B prints lines to console；A does not use finally for resource cleanup; B uses finally block with IOUtilities；A handles exceptions by showing message via MsgPrint; B prints stack trace
- 修正建议: Incorporate data flow analysis to track input/output；Penalize models for focusing on boilerplate；Add attention to high-level operations like HTTP method

### case_id=5536 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles action events in a GUI to set file paths and preferences for various tools like Graphviz and ImageMagick.
- B 摘要: Main method that parses command-line arguments and converts an input file to an output file using HTML entity decoding.
- 静态失败原因: The model likely over-relied on common tokens like 'File', 'Exception', and I/O operations, missing the stark difference in purpose and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they perform completely different high-level tasks with no overlap in core functionality.
- 行为差异: A is event-driven, B is a linear command-line program；A uses GUI components (JFileChooser), B uses command-line parsing；A saves user preferences, B performs file conversion；A handles multiple commands, B handles a single file format
- 修正建议: Incorporate structural features like control flow graphs；Use longer sequence models or hierarchical attention to capture overall function purpose；Train on more diverse non-clone pairs to avoid false positives from API overlap

### case_id=5537 FP boilerplate_overlap

- 方法: `readURL` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL and prints its content line by line to standard output.
- B 摘要: Fetches a YouTube video URL by parsing the HTML response of a given YouTube watch URL.
- 静态失败原因: The static BERT model likely focused on overlapping boilerplate code (try-catch, BufferedReader usage, println) and ignored the fundamental difference in computational logic. The model may have been biased by the similar API calls and structural patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when the core functionality differs. Here, one is a generic URL content dumper, the other is a specific YouTube URL extractor, so BCB would label them as non-clone.
- 共享行为: Both open a network connection and read text input using BufferedReader.；Both use try-catch for exception handling.；Both output debug information to System.out.；Both close resources (implicitly or explicitly) in a finally block (A explicitly closes, B closes rd explicitly).
- 行为差异: Function A prints all lines from the URL content; Function B searches for a specific string containing 'fullscreenUrl' and parses it.；Function A is a void method; Function B returns a constructed full URL string.；Function A takes a URL parameter; Function B uses a field ytUrl and sets progress bar indicators.；Function B performs additional parsing to extract video_id, t, and title; Function A does no parsing.
- 修正建议: Incorporate data-flow analysis to track how input data is transformed and used.；Train on more diverse examples to distinguish common I/O patterns from actual functional similarity.；Use contrastive learning that penalizes pairs with similar structure but different semantics.

### case_id=5538 FP lexical_or_api_overlap

- 方法: `addDataFromURL` vs `readScalarpvviewerDocument`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL line by line and appends all content to a text buffer.
- B 摘要: Reads a URL containing XML configuration data, parses it, and updates application state and UI with the extracted parameters.
- 静态失败原因: The static model likely over-emphasized the common lexical pattern of opening a URL, creating a BufferedReader, and looping reading lines, while ignoring the vastly different subsequent processing. This lexical and API overlap triggered a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the overall functionality is very different: one is a generic text fetcher, the other is a specific XML configuration loader with numerous side effects. The shared I/O boilerplate is insufficient for clone classification.
- 共享行为: Both open a URL and read its content line by line；Both handle IOException
- 行为差异: Function A simply concatenates all lines; Function B processes lines with specific filters and termination conditions；Function A has no XML parsing; Function B parses XML using XmlDataAdaptor and extracts many configuration parameters；Function B performs multiple UI updates and side effects (set title, font, chart updates) not present in A；Function B has complex control flow with multiple conditional checks and an XML parsing library; A is straightforward
- 修正建议: Enhance the model to focus on the core semantics beyond I/O boilerplate；Incorporate control-flow or data-flow analysis to distinguish simple concatenation from complex XML parsing；Add training examples where similar superficial patterns lead to different behavior

### case_id=5539 FN benchmark_preference_bias

- 方法: `init` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Initializes a servlet context by loading controller classes from a registry file.
- B 摘要: Reads geo-parser results by sending an XML request to a URL and parsing the response.
- 静态失败原因: The static BERT model correctly predicted non-clone (0), but BCB label is 1; the model was not misled due to low token overlap and different method names.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have annotated this pair as a clone because both functions involve reading data from an external source and processing it line by line, which could be seen as a Type-4 clone based on partial functionality similarity in data processing patterns.
- 共享行为: Both read text line by line from an input stream using BufferedReader.；Both catch exceptions and log errors.
- 行为差异: Function A loads classes from the classpath and registers them; Function B makes HTTP requests and parses XML.；Function A adds classes to a collection; Function B returns a collection of tuples.；Function B includes retry logic; Function A does not.；Function B constructs and sends an XML request; Function A reads a plain text file.
- 修正建议: Re-evaluate BCB annotation for this pair; consider whether the broad interpretation of clone is appropriate.；Adjust training data to avoid overly broad clone labeling from BCB.

### case_id=5540 FN partial_functionality

- 方法: `createDialogArea` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Creates a dialog area with a browser or text widget and loads a license text from a bundle resource.
- B 摘要: Reads a file from filesystem or classpath and returns its content as a string.
- 静态失败原因: The methods have very different contexts (UI vs file utility) and low lexical overlap (Jaccard 0.224), causing the model to miss the partial functional similarity in reading text.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered the common core of reading text from an InputStream and building a string as sufficient for functional similarity, ignoring the different contexts.
- 共享行为: Both read text from an InputStream using BufferedReader, appending lines to a StringBuffer.
- 行为差异: A creates UI components and sets layout; B is a pure file-reading utility.；A handles failure to create browser by falling back to Text; B prints errors and exits on failure.；A returns a Composite; B returns a String.；A uses a resource URL; B uses File or system resource.
- 修正建议: Incorporate data flow analysis to detect shared behaviors like resource reading.；Enhance representation with control flow patterns for input handling.；Consider type of usage (e.g., reading a textual resource) as a feature.

### case_id=5541 FN partial_functionality

- 方法: `sendExceptionToServer` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a remote server via HTTP POST and reads the response.
- B 摘要: Checks for software version updates by fetching and parsing a version file from a URL.
- 静态失败原因: Low token overlap (0.218) and different API usage (URLConnection vs URL.openStream) misled the model; it failed to recognize the shared structural pattern of URL opening followed by line-by-line reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BigCloneBench annotators likely considered both as network communication functions that fetch or send data over HTTP, a common high-level pattern even if details differ.
- 共享行为: Open a URL and establish a network connection；Read data from the connection using BufferedReader；Handle IOException with error reporting
- 行为差异: sendExceptionToServer writes data to the connection (POST-like), doVersionCheck only reads (GET)；Different URL sources (hardcoded vs property) and URL object creation methods；Different response parsing: one expects 'success', the other extracts version/build strings；Different output methods: console messages vs GUI dialogs
- 修正建议: Enhance model with dataflow or control-flow graphs to capture network I/O patterns；Use contrastive learning on high-level semantic categories (e.g., 'network communication')；Include more training pairs that share only abstract behavior with low syntactic similarity

### case_id=5542 FN partial_functionality

- 方法: `doBody` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads a file from a request and copies its content to the response output stream, with stream cleanup.
- B 摘要: Builds an editable site by processing XML, transforming pages, and writing output files using various I/O operations.
- 静态失败原因: Static models like GraphCodeBERT rely on token overlap and local patterns; low overlap (0.045) and huge size difference cause it to miss the semantic gap. The models fail to capture long-range control flow and distinct data dependencies.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled as clone due to superficial similarities like both performing file reading and writing, but the overall functionality is entirely different.
- 共享行为: Both use file I/O operations.；Both utilize buffered streams.；Both include exception handling and resource cleanup.
- 行为差异: Function A is a simple file copy to HTTP response; B is a complex site generation with multiple steps and parameters.；Function A has no XML transformation or page loop; B involves XML parsing, transformation, and writing multiple files.；Function A uses request/response objects; B operates on file paths and properties.；Function A is concise (10 lines); B is lengthy (~100 lines) with nested loops and conditionals.
- 修正建议: Incorporate dataflow analysis to distinguish high-level goals.；Use AST-based or graph-based matching to compare structural patterns.；Train on more diverse examples with clear semantic boundaries.

### case_id=5543 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `retrieveQ`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles a handshake packet by validating username and performing authentication via session server.
- B 摘要: Fetches the content of a URL and returns it as a string.
- 静态失败原因: Static model likely over-relied on surface-level API tokens (URL, BufferedReader) and control flow patterns (try-catch, while loops) without capturing the distinct high-level semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functional similarity beyond common API usage; these functions have entirely different purposes.
- 共享行为: Both use URL and BufferedReader to read from a remote resource.
- 行为差异: A performs authentication logic; B simply reads and returns content.；A conditionally sends a login packet or shuts down network; B returns a string.；A handles exceptions internally; B throws them.；B prints response message to stderr; A does not.
- 修正建议: Enhance training with more diverse non-clone pairs that share APIs but differ in goal.；Incorporate dataflow or program-dependency information to distinguish control flow intent.

### case_id=5544 FP lexical_or_api_overlap

- 方法: `readIntoList` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads HTML from a URL, parses anchor tags to extract menu item names and commands, creates JMenuItems with action listeners, and populates a map.
- B 摘要: Reads the first line from a given URL and returns it as a string.
- 静态失败原因: Static BERT models may over-rely on surface-level token overlap (URL, BufferedReader, readLine, etc.) and similar I/O boilerplate, ignoring higher-level semantic differences in control flow, string manipulation, and GUI construction. The shared motifs of URL reading and buffered I/O likely triggered a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones for pairs that differ in core functionality. Here, method A builds a GUI component from web data, while method B is a simple HTTP GET returning a single line. Their purposes are distinct, so BCB would not consider them clones.
- 共享行为: Both open a URL and create a BufferedReader from an InputStream；Both read lines from the reader；Both close the reader after reading
- 行为差异: Method A reads all lines in a loop, while Method B reads only the first line；Method A parses HTML-like content to extract substrings between '>' and '</a>', Method B does no parsing；Method A creates and configures JMenuItem objects and adds them to a map, Method B simply returns the raw line；Method A has action listener registration, Method B does not
- 修正建议: Encode control flow structure (e.g., loop vs no loop) more explicitly；Incorporate data-flow analysis to distinguish I/O-only from parsing + GUI creation；Use contrastive learning on negative examples with high token overlap but different semantics

### case_id=5545 FP lexical_or_api_overlap

- 方法: `main` vs `setPayload`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A main method that parses command-line arguments, reads a Prolog file, generates adapter classes, and writes output files.
- B 摘要: A private method that appends data from one file to another, recursively calls itself, and updates state.
- 静态失败原因: Static BERT/GraphCodeBERT may have overemphasized lexical overlap of common I/O API calls (FileOutputStream, FileInputStream, FileChannel) and ignored the vast difference in overall logic and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have no meaningful semantic overlap beyond basic I/O operations, which is insufficient for Type-3 or Type-4 similarity.
- 共享行为: Both perform file I/O operations using Java file APIs.
- 行为差异: Function A is a complex entry point with argument parsing, error handling, and code generation; function B is a simple file-copy loop.；Function A involves parsing, class generation, and serialization; function B only copies binary data.；Function A uses many external libraries (e.g., Prolog parser, ASM); function B uses only standard Java I/O.；Function A has multiple conditional exits and a try-catch-all; function B returns boolean based on index check.
- 修正建议: Incorporate control-flow and data-flow information to distinguish different high-level tasks.；Use semantic role labeling to identify the main purpose of each function (e.g., code generation vs. file copy).；Increase sensitivity to method signature and context (private vs. public, main vs. helper).

### case_id=5546 FP partial_functionality

- 方法: `getJSONData` vs `readZoneIDs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches JSON data from a URL via HTTP and returns a JSONObject.
- B 摘要: Reads integer IDs from a class resource file line by line and returns a HashSet<Integer>.
- 静态失败原因: The model likely overemphasized common boilerplate patterns (while-readline, try-catch) and API overlap (InputStreamReader, BufferedReader) while missing the semantic differences in input source and return type, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labeled non-clone because the methods have distinct high-level purposes (HTTP JSON retrieval vs resource ID reading) despite low-level structural overlap. The functional semantics are too different for even broad Type-4 similarity.
- 共享行为: Reads lines in a while loop from an input stream.；Uses try-catch exception handling and prints stack trace.；Returns a container object (JSONObject or HashSet<Integer>).
- 行为差异: Input source: HTTP URL vs class resource file.；Return type: JSONObject vs HashSet<Integer>.；Line processing: appends to StringBuilder and parses JSON vs parses lines as integers directly.
- 修正建议: Incorporate data flow analysis to distinguish HTTP vs resource access.；Add training examples that distinguish similar structural patterns with different external APIs.；Use return type information to better capture semantic purpose.

### case_id=5547 FP lexical_or_api_overlap

- 方法: `caml_md5_string` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes MD5 hash of a substring of the input string.
- B 摘要: Handles an HTTP request to classify a concept using a web service and updates session attributes.
- 静态失败原因: The low token Jaccard (0.033) suggests minimal lexical overlap; however, the static model might have been confused by superficially similar class names (e.g., MessageDigest vs. MessageResources) or common structural patterns (try-catch, return).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires some functional similarity (Type-3/4); these functions have entirely different purposes, so BCB would label as non-clone.
- 共享行为: Both methods involve string handling and network or hash operations, but no shared behavior.
- 行为差异: Function A computes a cryptographic hash; Function B processes a web request and sends HTTP POST.；Function A has no side effects beyond returning a value; Function B modifies session and communicates with external URL.；Function A uses MessageDigest; Function B uses HttpSession, ActionMapping, URLConnection, etc.
- 修正建议: Improve negative sampling with diverse domains and longer functions.；Incorporate dataflow or control-flow reasoning to distinguish cryptographic vs. web request logic.

### case_id=5548 FN benchmark_preference_bias

- 方法: `convert` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Converts an ACRNEMA file to DICOM format by parsing the input stream, adding UIDs, and writing pixel data.
- B 摘要: Downloads a WSDL file from a URL, modifies the soap:address endpoint, and saves it locally, returning the file path.
- 静态失败原因: The static BERT/GraphCodeBERT model likely correctly identified the semantic dissimilarity (low token overlap, different domains), leading to a non-clone prediction. It 'failed' only by disagreeing with BCB's overly broad annotation, which may be biased toward structural similarity over semantic meaning.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to a broad interpretation of 'file conversion' or 'file processing', despite entirely different domains and operations. The shared use of streams and file output may have been seen as sufficient for a Type-3/Type-4 clone.
- 共享行为: Both use file I/O streams (FileInputStream, FileOutputStream).；Both write to an output file after processing.；Both handle exceptions with try-catch-finally blocks.；Both check conditions before proceeding (e.g., file existence, UID presence).
- 行为差异: A processes medical images (ACRNEMA/DICOM); B downloads and modifies XML (WSDL).；A reads from a local file; B reads from a URL.；A adds metadata (UIDs) and writes pixel data; B modifies XML attributes and saves.；A has complex pixel data inflation logic; B has no such transformation.
- 修正建议: Use domain-aware semantic embeddings to distinguish medical vs. web service code.；Incorporate task-specific fine-tuning to avoid overgeneralizing file I/O patterns.；Re-evaluate BCB labels to ensure consistency with strict semantic equivalence.

### case_id=5549 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the XML endpoint, and returns the file path.
- B 摘要: Copies a file from source to destination using NIO FileChannel transfer.
- 静态失败原因: Static BERT models rely on token-level similarity; the low Jaccard (0.097) and different method names/parameter types caused it to miss the structural similarity of the channel transfer sub-pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled as Type-3 clone because B performs a subset of the file I/O operations in A (the channel-based copy). The reuse of the same NIO pattern is considered a clone under broad annotation guidelines.
- 共享行为: Both use FileChannel.transferFrom to copy data from an input channel to an output channel.
- 行为差异: A involves network download, XML parsing/modification, and error handling for multiple exceptions; B is a simple local file copy.；A returns a String; B is void.；A handles file existence and uses temporary files; B does not.
- 修正建议: Use graph-based representations (e.g., AST or data flow graphs) to capture subgraph similarities.；Train models to recognize functional subsumption relations.；Incorporate structure-aware attention mechanisms.

### case_id=5550 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `sendPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for new version by reading a remote file and extracting build numbers.
- B 摘要: Sends an HTTP POST request with a parameter and returns the response.
- 静态失败原因: The model likely focused on surface-level lexical and API overlap (URL, BufferedReader, while loop, try-catch) while missing the overall purpose and differences in inputs/outputs.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels it non-clone because the core functionality differs (version check vs. POST request), and the superficial API overlap is insufficient for Type-3/4 similarity.
- 共享行为: Both open a URL connection and read lines from the input stream using BufferedReader.
- 行为差异: Input parameters: A takes a View for UI, B takes two Strings.；HTTP method: A uses GET (URL.openStream), B uses POST with output.；Return type: A void, B returns response string.；Error handling: A catches IOException only, B catches all exceptions.
- 修正建议: Incorporate dataflow analysis to track how inputs are used and outputs produced.；Use graph-based representations (e.g., AST, CFG) to capture structural semantics beyond tokens.；Train on more diverse examples to learn functional semantics rather than API co-occurrence.

### case_id=5551 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `createOutputStream`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Event handler that processes UI action commands like setting GraphViz/ImageMagick paths and other preferences.
- B 摘要: Creates a BufferedWriter that copies entries from a ZIP file to another, special-casing 'content.xml' entry.
- 静态失败原因: The static model likely relied on token-level similarities (e.g., 'File', 'BufferedWriter', 'IOException') and ignored the structural and semantic differences, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have entirely different purposes and no meaningful shared behavior beyond basic Java syntax.
- 共享行为: Both use file-related APIs (File, FileInputStream, etc.) but in different contexts.
- 行为差异: Function A is an event handler with UI interactions; Function B is a pure I/O utility.；Function A modifies UI state and preferences; Function B produces a BufferedWriter for output.；Function A handles multiple command buttons; Function B processes ZIP entries with specific skipping logic.；Function A has no return value; Function B returns a BufferedWriter.
- 修正建议: Incorporate structure-aware features like data flow and control flow.；Use a model that captures long-range dependencies and method-level semantics.；Train on more diverse examples to reduce bias towards common API tokens.

### case_id=5552 FP boilerplate_overlap

- 方法: `postRequest` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with URL-encoded form data and returns the response body as a string.
- B 摘要: Downloads an RDF model from a URL via HTTP, parsing the response into a Model object.
- 静态失败原因: Static models like GraphCodeBERT may have been misled by the lexical and structural overlap in opening a URLConnection, handling exceptions, and reading from an input stream. The shared boilerplate patterns (try-catch, InputStream) can dominate the representation, causing the model to ignore the fundamentally different purposes (writing form data vs. parsing an RDF model).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because the overall functionality is completely different: one is a generic HTTP POST, the other is a domain-specific download of an RDF model. The return types and core operations diverge significantly, so BCB's semantic annotations would treat them as distinct.
- 共享行为: Open a URLConnection and get an InputStream；Catch IOException and handle errors
- 行为差异: A sends POST data; B only performs GET；A returns a String; B returns a Model；B sets HTTP headers (Accept, Accept-Language); A does not；A writes to output stream; B does not
- 修正建议: Incorporate dataflow analysis to distinguish write vs read operations.；Add return type information as an auxiliary feature.；Train on tasks that require understanding method-level semantics beyond shared API usage.

### case_id=5553 FN long_range_semantics

- 方法: `createOutputStream` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Creates a BufferedWriter targeting a new ZIP output stream, copying all entries from an input ZIP except 'content.xml', then adding a new 'content.xml' entry.
- B 摘要: Builds a website for editing by iterating over pages, transforming XML, reading control files, performing string replacements, and writing output files.
- 静态失败原因: Low token overlap (0.054), different method names, and function B's truncated code may have prevented the model from capturing the high-level semantic difference; the model likely relied on surface similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled these as clones erroneously, possibly due to both involving file processing with streams and character encoding, or due to an annotation mistake. BCB typically requires some functional similarity, which is lacking here.
- 共享行为: Both involve file I/O operations (reading and writing).；Both handle character streams and encoding.；Both perform some form of data transformation.
- 行为差异: Function A processes a single ZIP file, while Function B builds a multi-page website.；Function A returns a BufferedWriter, Function B is void.；Function A has a specific focus on handling 'content.xml', Function B has no such focus.；Function B has extensive error handling and debugging output, Function A does not.
- 修正建议: Improve semantic understanding with graph-based or dataflow analysis.；Use method name and context to infer purpose.；Train on more diverse clones to avoid overfitting to token overlap.

### case_id=5554 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `testCopyUnknownSize`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles various GUI action commands and updates UI settings for a Suku application.
- B 摘要: Tests copying an input stream to an output stream with unknown size.
- 静态失败原因: The model might have been misled by common tokens like 'if', 'return', 'null', 'String', or the presence of 'Suku' (project prefix) in both, leading to a false positive due to lexical overlap in boilerplate patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because they have entirely different functionality; one is a GUI event handler, the other is a utility test.
- 共享行为: Both are Java methods that involve some I/O (file chooser vs. stream copy)；Both use if statements for control flow
- 行为差异: Function A is a complex GUI event handler with many options; Function B is a simple unit test for stream copying.；Function A interacts with UI components and preferences; Function B only uses streams and asserts.；The purpose and functionality are completely different.
- 修正建议: Improve model's ability to distinguish boilerplate from core logic.；Use functional similarity rather than token overlap.

### case_id=5555 FN benchmark_preference_bias

- 方法: `doTransfer` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Transfers an HTTP request to another URL, acting as a proxy by copying headers, request body, and returning the response.
- B 摘要: Checks for a new version of jEdit by reading a remote version file and comparing build numbers.
- 静态失败原因: Static BERT/GraphCodeBERT models often rely on token and API-level overlaps; here the low token Jaccard (0.157) and different control flow led it to correctly identify non-clonality under strict semantics, but it failed to recognize the broad structural similarity of network I/O operations that BCB might consider.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both methods involving network access, opening a URL, reading input streams, and handling IO exceptions, which could be considered a Type-3 clone under a broad interpretation of similar structure and partial functionality.
- 共享行为: Both open a URL and read data from the network；Both handle IOException with try-catch
- 行为差异: A performs full duplex HTTP proxy with request and response streams; B only reads a simple text file；A writes to both the connection's output stream and the HTTP response; B only reads and parses lines；A uses HttpURLConnection with multiple properties; B uses URL.openStream() and a BufferedReader；A has complex I/O stream management; B has simple line-by-line reading
- 修正建议: Incorporate high-level task category recognition (e.g., network I/O operations) as features；Use graph or dataflow analysis to identify shared sub-patterns like URL open + stream read + error handling；Adjust threshold for Type-3 clones by considering method length and I/O operations

### case_id=5556 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `getPagina`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a hardcoded Twitter URL using HttpClient and returns the response body as a string.
- B 摘要: Reads a given URL using Java URL connection and returns the page content as a string.
- 静态失败原因: The model likely over-relied on the common boilerplate pattern of reading lines from a stream and the presence of HTTP-related classes, ignoring the differences in libraries and context (hardcoded vs parameterized, error handling).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone due to different HTTP libraries, error handling strategies, and the fact that A is specific to Twitter while B is generic, leading to insufficient similarity for Type-3/4.
- 共享行为: Both fetch content from a URL over HTTP.；Both concatenate lines read from an input stream into a string.
- 行为差异: A uses Apache HttpClient; B uses Java URL.openStream().；A hardcodes the URL; B takes a URL parameter.；A logs error on non-200 status; B returns error message as string on exceptions.；B sets an Authenticator; A does not.
- 修正建议: Incorporate features that distinguish between different HTTP client libraries.；Add attention to constant vs. variable URL sources.；Include error-handling patterns more explicitly.

### case_id=5557 FN lexical_or_api_overlap

- 方法: `copyResource` vs `copyFileByNIO`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using byte-by-byte stream I/O.
- B 摘要: Copies a file to another file using NIO FileChannel transferTo method.
- 静态失败原因: Static BERT models rely on token and API overlap, which is low (Jaccard 0.14). The APIs (InputStream/OutputStream vs FileChannel) and source types (URL vs File) are completely different, so the model fails to recognize semantic similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers both as 'file copying' operations, focusing on the core byte transfer behavior and ignoring differences in input source type and I/O mechanism.
- 共享行为: Both copy the content of a source to a destination file.
- 行为差异: Source can be a URL or file in A; B only accepts File inputs.；A uses InputStream/OutputStream byte loop; B uses NIO FileChannel.；A throws Exception; B throws IOException.；A uses destinationFile() method for output; B takes output File parameter.
- 修正建议: Incorporate dataflow or control flow analysis to detect similarity in high-level functionality.；Use program dependence graphs to capture semantic equivalence despite different APIs.

### case_id=5558 FN benchmark_preference_bias

- 方法: `testCodingEmptyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Tests encoding of data through LengthDelimitedEncoder, writing to a ByteArrayOutputStream and transferring from a file channel.
- B 摘要: Launches a NexOpen project configuration, handling Maven POM files, setting Hibernate properties, and potentially creating a reverse engineering file.
- 静态失败原因: Static model likely correctly identified them as non-clones due to very low token overlap (0.046) and entirely different API calls and contexts; it failed to align with BCB's exceptionally broad annotation preference.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled due to superficial overlap (ByteArrayOutputStream, file I/O) rather than true functional similarity; such broad interpretation is inconsistent with typical Type-3/Type-4 clone definitions.
- 共享行为: Both use ByteArrayOutputStream for temporary byte storage；Both involve file I/O operations
- 行为差异: Function A is a unit test for HTTP encoding; Function B is a complex project launch routine；A uses LengthDelimitedEncoder and file channel transfer; B does not；B involves XML parsing, project configuration, and job scheduling; A does not；A has simple assertions; B has exception handling and resource management
- 修正建议: Re-evaluate BCB annotation for this pair to ensure consistency with clone definitions；Consider excluding pairs with only trivial API overlaps from clone labels；Improve model robustness by training on more diverse negative examples

### case_id=5559 FP lexical_or_api_overlap

- 方法: `init` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads controller classes from a file using class loader.
- B 摘要: Performs Google image search using HTTP connection.
- 静态失败原因: Static BERT may have focused on common API sequences (BufferedReader, InputStreamReader, URL) and try-catch blocks, missing the high-level semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have completely different overall functionality despite some shared IO patterns.
- 共享行为: Both use BufferedReader to read from streams；Both have try-catch exception handling；Both iterate over lines of input
- 行为差异: Different purposes: class loading vs image search；Different input sources: file from classpath vs HTTP response；Different output: adds classes to registry vs populates image list
- 修正建议: Use embeddings that better capture method purpose；Incorporate control flow or data flow info；Train on more diverse non-clone pairs with API overlap

### case_id=5560 FN partial_functionality

- 方法: `copy` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Simple file copy from source to destination using a buffer.
- B 摘要: Complex method to build a site for editing, involving XML processing, transformation, and multiple file writes.
- 静态失败原因: Static models like BERT rely on token and structural similarity; the low Jaccard similarity and high complexity of B cause them to predict non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might have considered that both functions perform file I/O operations, but the overall functionality is vastly different, making this potentially a misannotation.
- 共享行为: Both read from an input file and write to an output file using FileInputStream/FileOutputStream.
- 行为差异: A is a straightforward copy; B involves XML parsing, transformation, looping over pages, reading control files, string replacement, and writing multiple files.；B has extensive error handling, debugging, and multiple parameters; A is minimal.
- 修正建议: Incorporate control and data flow analysis to differentiate simple file operations from complex pipelines.；Consider functional context or API usage patterns beyond raw tokens.

### case_id=5561 FN partial_functionality

- 方法: `doVersionCheck` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads version information from a URL and compares with current build.
- B 摘要: Opens a file or URL and reads its content, returning a status code.
- 静态失败原因: Static BERT models rely on token overlap and syntactic structure; these methods have low token Jaccard (0.25), different method names and signatures, and diverge in later processing, making them appear non-clone despite shared I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone due to the common pattern of opening a URL, streaming data, and handling IOExceptions, which constitutes significant functional similarity under broad Type-3/Type-4 definitions.
- 共享行为: Open a URL stream；Wrap stream in buffered readers/input streams；Handle IOException
- 行为差异: doVersionCheck parses specific lines for version/build and shows UI messages; read returns a status and delegates to another read method.；doVersionCheck uses a View object for cursor and messages; read does not involve UI.；doVersionCheck reads only text lines; read reads binary data via BufferedInputStream.
- 修正建议: Use models that capture data flow and API call sequences.；Incorporate functional purpose via documentation or type signatures.；Consider graph-based representations like Code Property Graphs.

### case_id=5562 FN partial_functionality

- 方法: `doVersionCheck` vs `login`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for latest version by fetching and parsing a version file from a URL.
- B 摘要: Logs in to a service by sending credentials via HTTP POST and extracting session ID from response.
- 静态失败原因: Static BERT models rely on token-level similarity and structural patterns, but these functions have low token Jaccard (0.16) and different method names, so the model fails to capture the semantic similarity of the network communication pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this pair as clone because both functions implement a high-level pattern of HTTP connection, reading response, extracting information, and error handling, which are considered functionally similar despite different specifics.
- 共享行为: Both open a URL and read input stream；Both parse lines of text from response；Both handle exceptions with error reporting
- 行为差异: Different HTTP methods: GET vs POST；Different parsing logic: startsWith vs reading first line；Different error handling: dialog vs sysout；Different return types: void vs String
- 修正建议: Use graph-based models that capture data flow and control flow；Incorporate system call or API usage sequences；Train on structural clones with diverse surface forms

### case_id=5563 FP lexical_or_api_overlap

- 方法: `sendPost` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: sendPost performs an HTTP POST request with given parameters and returns the response body as a string.
- B 摘要: doVersionCheck checks the latest jEdit version by reading a version file from a URL and displays an update message if needed.
- 静态失败原因: The functions share many common API tokens (URL, BufferedReader, readLine, try-catch) and structural patterns, leading the model to overemphasize boilerplate similarity and overlook the distinct logic of POST vs. version parsing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels clones based on similar functionality. These functions have different core purposes (generic POST utility vs. version checker), so BCB would likely label them as non-clones.
- 共享行为: Both open a URL connection and read data from an input stream.；Both use BufferedReader to read lines.；Both handle IOExceptions with logging or UI messages.
- 行为差异: sendPost sends data (param) via POST, doVersionCheck only reads (GET).；sendPost returns the response string, doVersionCheck returns void and updates UI.；sendPost uses HttpURLConnection with output enabled, doVersionCheck uses URL.openStream().；sendPost sets request properties (Accept-Language), doVersionCheck does not.
- 修正建议: Incorporate data flow analysis to distinguish POST vs. GET operations.；Use control flow analysis to capture different conditional logic.；Train on diverse examples to reduce reliance on common I/O patterns.；Add attention to method names and parameter usage for semantic cues.

### case_id=5564 FP other

- 方法: `getDigest` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Computes a cryptographic message digest for an OMAttribute, excluding namespace attributes.
- B 摘要: Handles a Struts action to classify a concept by building XML, sending it to a remote service, parsing the result, and updating session attributes.
- 静态失败原因: The static model likely overfitted on superficial features like exception handling patterns or common library imports, but the token Jaccard similarity is very low (0.0568), suggesting a false positive due to random noise or model misclassification.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB correctly labels as non-clone because the functions have completely different purposes and no functional similarity under Type-3/4 criteria.
- 行为差异: Function A deals with cryptographic hashing of attribute data; Function B deals with web request processing and remote service interaction.；Function A returns a byte array; Function B returns an ActionForward.；Function A uses MessageDigest; Function B uses URLConnection, XML parsing, and session management.；Function A has a conditional skip for xmlns attributes; Function B has extensive logic for form data and role handling.
- 修正建议: Improve model training to focus on semantic structure rather than lexical overlap.；Incorporate more robust contextual understanding to differentiate between distinct domains like cryptography and web actions.

### case_id=5565 FN lexical_or_api_overlap

- 方法: `unzipModel` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts all entries from a zip file and writes them to a specified temporary directory.
- B 摘要: Downloads a WSDL file from a URL, modifies an XML attribute, and saves it to a temporary file.
- 静态失败原因: Static BERT/GraphCodeBERT relies on token overlap and syntactic structure; the Jaccard similarity is very low (0.114) and the API calls differ significantly, so it predicted non-clone.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have annotated this as a clone due to the broad Type-4 category of 'file I/O utilities', but the functionalities are too distinct for a typical clone.
- 共享行为: Both perform file I/O operations with buffered streams.；Both write output to files in a temporary location.；Both handle exceptions and wrap them in custom exceptions.
- 行为差异: A reads from a local zip file, B reads from a remote URL.；A extracts multiple files, B writes a single modified XML file.；B involves XML parsing and modification, A does not.；Different exception handling: A throws EDITSException, B throws AxisFault with logging.
- 修正建议: Incorporate higher-level semantic features like functional purpose or dataflow patterns.；Use models that capture long-range dependencies and API call semantics.；Train on datasets with more diverse Type-4 clones.

### case_id=5566 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `readZoneIDs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter timeline from a fixed URL via HTTP and returns the entire response as a string.
- B 摘要: Reads zone IDs from a given resource file and returns them as a HashSet of integers.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-relied on the common pattern of reading lines in a while loop and catching exceptions, while ignoring the fundamentally different I/O sources, data types, and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they perform entirely different tasks (reading social media feed vs parsing configuration IDs) and have low structural or semantic similarity.
- 共享行为: Both read lines from an input stream using a buffered reader.；Both use try-catch blocks to handle IOException.；Both build a collection (StringBuilder vs HashSet) from the lines.；Both return the built collection.
- 行为差异: A uses HttpClient for HTTP GET request; B uses URL.openStream() to read a local resource.；A returns all text concatenated; B parses each line as integer and adds to set.；A has a hardcoded URL; B takes filename as parameter.；A logs a message on failure; B prints stack trace.
- 修正建议: Train the model to incorporate data-flow analysis and type information.；Focus on the semantic purpose of the function rather than just syntactic patterns.；Use contrastive learning to better distinguish between different I/O operations.；Incorporate return type and API usage patterns into the representation.

### case_id=5567 FN dataflow_blindspot

- 方法: `getButtonSonido` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `dynamic_equivalence_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: This method creates a button that, when clicked, opens a file chooser to select a sound file, copies it to a target directory using FileChannel, and updates the UI.
- B 摘要: This method downloads a WSDL file from a URL to a temporary directory if not present, modifies its soap address via XML manipulation, and returns the file path.
- 静态失败原因: The static BERT model likely failed to recognize the clone because it focused on high-level semantic differences (UI vs. utility, local vs. remote) and ignored the underlying shared dataflow pattern of file copying with FileChannel.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本可能是 API 写法不同但行为等价的漏报。建议测试目标为 input_output_equivalence。
- BCB 偏好解释: BCB likely labeled this pair as a clone due to the common low-level file transfer pattern using FileChannel and similar file existence checks, interpreting both as 'file copy' operations under broad Type-4 similarity.
- 共享行为: Both methods perform file copy/transfer using FileChannel from a source to a destination.；Both check file existence before copying.；Both handle IOExceptions and use try-catch blocks.；Both use System properties for file paths (user.dir or java.io.tmpdir).
- 行为差异: A is a private instance method triggered by a UI button; B is a public static utility method.；A copies from a local user-selected file; B downloads from a remote URL.；A does not modify the file content; B modifies XML after download.；A updates UI components; B returns a string and logs debug messages.
- 修正建议: Incorporate data flow analysis or structural similarity measures (e.g., program dependency graphs) to capture shared low-level operations.；Use contrastive learning with broader clone definitions including Type-4.；Add attention to common API usage patterns like FileChannel transfer.

### case_id=5568 FN benchmark_preference_bias

- 方法: `doGet` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.1`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve a portal page, check permissions, log, and render HTML with caching.
- B 摘要: Reads a DICOM image file, parses pixel data, and writes the dataset to an output file.
- 静态失败原因: Static BERT correctly predicted non-clone due to low token overlap and distinct structures; it did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled due to very abstract 'read-process-write' pattern, or annotation error.
- 共享行为: Perform input/output operations
- 行为差异: Different domains: web servlet vs medical imaging file processing；Different data types: HTTP request/response vs DICOM file streams；Different output: HTML page with caching vs DICOM file with pixel data；Error handling: HTTP error codes vs exceptions
- 修正建议: Re-annotate the pair as non-clone in BCB；Review other BCB labels for similar false positives

### case_id=5569 FP boilerplate_overlap

- 方法: `main` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses a Prolog file, generates adapters, and packages them into a JAR file.
- B 摘要: Run method that pseudolocalizes message catalogs from files or stdin based on arguments.
- 静态失败原因: GraphCodeBERT may have overfitted on common patterns like checking args, using File, try-catch, loops over items, leading to high similarity in embeddings despite different semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because functions have completely different domains and outputs; despite some structural similarities in argument parsing and file handling, the core functionality is unrelated.
- 共享行为: Both check for required arguments or conditions.；Both handle file I/O and output.；Both iterate over collections (adapter layer vs. file names).
- 行为差异: Function A generates Java adapters from Prolog facts; B transforms message catalogs for localization.；A serializes adapter layer and writes to JAR; B writes processed messages to output files or stdout.；A uses complex class loading and assembler; B uses FormatRegistry for message catalog types.；A has specific dependency on PrologParser and FactVisitor; B uses PseudolocalizationPipeline.
- 修正建议: Add more training examples with distinct application contexts.；Use hierarchical representations that capture high-level intent rather than token patterns.；Incorporate functional metadata like method name, class, and package names to disambiguate.；Consider control-flow graph or data-flow attention to differentiate I/O transformations.

### case_id=5570 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads Twitter user timeline JSON via HTTP and returns it as a string.
- B 摘要: Reads a resource file from classpath, builds a string with line breaks, and sets it as text in a UI component.
- 静态失败原因: Static models like BERT may focus on token-level similarities (e.g., BufferedReader, StringBuilder, readLine pattern) and miss the broader context of method names, import statements, and the surrounding code (e.g., HttpClient vs URL, UI update). The Jaccard similarity is low (0.158), but the model might have been misled by the common boilerplate of reading streams.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clones because the high-level functionality differs: one is an HTTP download, the other is a resource file read with UI update.
- 共享行为: Both use BufferedReader and StringBuilder to read line by line from an InputStream.；Both open a stream and wrap it in InputStreamReader and BufferedReader.
- 行为差异: Function A fetches data from a remote HTTP server; Function B reads a local resource file.；Function A returns the string; Function B updates a UI component via SwingUtilities.invokeLater.；Function A appends lines without newline; Function B adds carriage return and newline.；Function A logs errors; Function B catches all exceptions silently.
- 修正建议: Incorporate method name and context (e.g., class name, method calls) into representation.；Use graph-based embeddings that capture control and data flow to distinguish between different uses of the read-line pattern.；Include type information (e.g., HttpClient vs URL) to differentiate remote vs local IO.

### case_id=5571 FN partial_functionality

- 方法: `readGeoParserResult` vs `getPagina`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a record content, sends it to a geo-parser web service, parses XML response, and returns a collection of place names with associated IDs.
- B 摘要: Fetches the content of a given URL as a string.
- 静态失败原因: Static BERT relies heavily on lexical overlap and token similarity; the Jaccard similarity is low (0.128). It probably missed the high-level semantic similarity because the APIs and data structures differ significantly. The model may not generalize well to tasks that require recognizing common sub-patterns like URL reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as Type-4 (semantic) clones because both functions share the core behavior of fetching data from a URL via HTTP GET and returning a result, despite different data formats and processing details.
- 共享行为: Both create a URL object and open a stream；Both read lines from the stream using BufferedReader；Both concatenate lines into a string or collection；Both handle exceptions (IOException, etc.)
- 行为差异: Function A builds an XML request before sending; B does not；Function A parses XML response; B returns raw content；Function A has retry logic (3 attempts); B does not；Function A returns a collection of tuples; B returns a single string
- 修正建议: Include data augmentations that highlight shared sub-routines (e.g., URL fetching as a clone)；Use structural AST-based features to capture common control flow patterns；Train on broader Type-3/Type-4 examples with low lexical overlap

### case_id=5572 FN partial_functionality

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Main method that downloads a zip file from a URL and extracts all entries to the current directory.
- B 摘要: Method that copies a file from a source to a destination, creating directories if necessary, using FileChannel.transferFrom.
- 静态失败原因: Static models may rely on surface-level features like method name, token Jaccard (0.1625), and structural differences (loops vs. sequential), missing the underlying I/O semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered both as file copying utilities, where A copies files from a zip archive and B copies a single file, thus sharing core I/O semantic similarity.
- 共享行为: Both read from an input source and write to an output destination；Both involve file I/O operations；Both use try-finally resource management
- 行为差异: A downloads from HTTP and decompresses ZIP entries; B copies a local file；A processes multiple files in a loop; B copies a single file；A uses ZipInputStream and BufferedOutputStream; B uses FileChannel and FileOutputStream
- 修正建议: Improve semantic matching by incorporating high-level task descriptions；Use graph-based representations that capture data flow between input and output；Train on more diverse I/O examples to recognize file copy patterns

### case_id=5573 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `parse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Fetches a Twitter timeline from a hardcoded URL via HTTP and returns the response body as a string.
- B 摘要: Parses a data file (from URL or file) with configurable delimiters and type handling, returning a DataSet object.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on surface-level common patterns like BufferedReader, while loop, and IOException catch, leading to a false positive due to boilerplate overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators likely considered these as unrelated tasks despite both reading streams, because the core functionality (simple fetch vs. complex parser) is completely different, falling outside their broad Type-3/Type-4 criteria.
- 共享行为: Both use BufferedReader to read input line by line；Both handle I/O exceptions with try-catch
- 行为差异: A performs a simple HTTP GET on a fixed URL; B reads from a URL or local file with complex configuration；A returns a plain string; B returns a structured DataSet after parsing tokenized fields；B includes header/skip lines, multiple delimiters, scientific notation, and type conversion; A does not
- 修正建议: Include data-flow or control-flow information to distinguish simple fetch from complex parsing；Add contrastive learning with hard negative pairs that differ in functionality despite similar boilerplate

### case_id=5574 FP lexical_or_api_overlap

- 方法: `loadMFileViaWeb` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a MATLAB M-file from a web URL and parses it into a UserFunction object.
- B 摘要: Downloads an RDF model from a URL and returns it.
- 静态失败原因: Static BERT likely overemphasized lexical/API overlap (e.g., URL, InputStream, try-catch) and ignored the high-level semantic disparity due to lack of domain-specific knowledge about MATLAB functions vs RDF models.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because despite both involving URL downloads, the processed data types and output objects are semantically distinct, matching Type-4 (functionality unrelated) rather than Type-3.
- 共享行为: Open a URL connection；Read from an input stream；Handle exceptions during I/O
- 行为差异: A reads line-by-line and concatenates; B reads directly into model；A does not set HTTP headers; B sets Accept and Accept-Language headers；A parses content as MATLAB function; B interprets as RDF；A returns UserFunction; B returns Model
- 修正建议: Incorporate type information of parameters and return values；Add representation of domain-specific concepts (e.g., RDF, MATLAB)；Use contrastive learning with hard negative examples that share API calls but differ in purpose

### case_id=5575 FN partial_functionality

- 方法: `main` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using FileChannel and ByteBuffer.
- B 摘要: Downloads a WSDL file from a URL, optionally modifies its endpoint, and saves it locally with logging and error handling.
- 静态失败原因: The model focused on lexical and syntactic similarity, which is low; it failed to recognize the partial functionality overlap that BCB might accept.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to the shared file copy operation pattern, even though the overall functionality differs significantly.
- 共享行为: Both functions perform file I/O operations: reading from an input and writing to an output.
- 行为差异: B involves network download, XML parsing, endpoint modification, multiple file operations, logging, and exception handling; A is a simple file copy.
- 修正建议: Enhance model to detect shared sub-functionality even when overall semantics differ.；Incorporate more abstract representations of I/O operations.

### case_id=5576 FP lexical_or_api_overlap

- 方法: `PageLoader` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Constructor that loads a web page via GET and stores its content in a field.
- B 摘要: Method that sends an HTTP POST request with parameters and returns the response string.
- 静态失败原因: Static BERT/GraphCodeBERT may have overfitted on the lexical overlap of common HTTP API calls (URL, BufferedReader, readLine, openStream) and ignored the differences in method signatures, control flow, and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions have different purposes (constructor vs method, GET vs POST), different control flow (exception handling, disconnection), and different output (field vs return value). They are not semantically equivalent even in a broad Type-4 sense.
- 共享行为: Both create a URL object；Both open a connection to a URL；Both read input using BufferedReader
- 行为差异: A uses GET (default), B uses POST；A is a constructor, B is a method；A stores result in a field, B returns the response；A does not handle exceptions or disconnect, B does
- 修正建议: Incorporate method signature and return type information；Capture control flow differences (exception handling, finally block)；Distinguish between constructor and method；Consider data flow of parameters vs field assignment

### case_id=5577 FN partial_functionality

- 方法: `copyFile` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using NIO FileChannel.
- B 摘要: Modifies a properties file for a given locale, including copying a default English file if the target does not exist.
- 静态失败原因: The low token Jaccard (0.076) and different method names and control structures caused the static model to focus on surface-level differences, missing the partial functional overlap of file copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely annotated this as a clone because both functions involve file copying (B's copy step is analogous to A's entire function) and are both file utility functions, aligning with BCB's broad Type-3/Type-4 acceptance.
- 共享行为: Both functions perform file I/O operations (reading and writing files).；Function B includes a file copy step that mirrors the functionality of function A.
- 行为差异: Function A only copies a file using NIO channels, while function B modifies a properties file by parsing and updating key-value pairs.；Function A uses byte streams (FileChannel), function B uses character streams (FileReader/FileWriter).；Function B includes conditional logic for file existence and property parsing, function A does not.
- 修正建议: Enable models to detect sub-functional similarities, e.g., by using graph-based representations that capture subroutines.；Incorporate task-specific fine-tuning on file I/O operations.

### case_id=5578 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a webpage, parses all hyperlinks and link texts, returns them as two Vectors.
- B 摘要: Loads an OSGi FrameworkFactory from a service file in the classpath using reflection.
- 静态失败原因: The model likely over-weighed common tokens (URL, BufferedReader, readLine, Exception) and ignored the high-level semantic difference (web scraping vs. service loading).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench treats functions with entirely different purposes as non-clones, even if they share some low-level API usage patterns.
- 共享行为: Both open a resource (URL or classpath file) for reading.；Both use BufferedReader to read line by line.；Both throw Exception on failure.
- 行为差异: A reads from a network URL; B reads from a classpath resource.；A parses HTML with regex to extract links; B reads a service file and instantiates a class.；A returns two Vectors of extracted data; B returns a single FrameworkFactory instance.；A prints debug info; B does not.
- 修正建议: Incorporate structural or data-flow features to capture the overall purpose.；Use contrastive learning to separate functions with different domain intents.；Augment training data with more negative pairs that share similar API calls but differ in functionality.

### case_id=5579 FN partial_functionality

- 方法: `getEncoding` vs `retrieveTemplate`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts character encoding from HTTP response headers or HTML content read from a URL.
- B 摘要: Retrieves and caches an HTML template string from a blog URL.
- 静态失败原因: Static BERT models (like CodeBERT) rely heavily on token matching and local context. The low token Jaccard (0.258) and different method names ('getEncoding' vs 'retrieveTemplate') lead to low similarity. The model fails to recognize the structural pattern of URL reading because it gets distracted by different output computations and exception handling details.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers Type-3/Type-4 clones based on structural similarity and shared data flow. The core pattern of opening a URL, reading lines with BufferedReader, and processing text is common, even though the specific processing differs. The boilerplate code for URL I/O makes them similar enough for BCB's broad definition.
- 共享行为: Both open a URL connection and read its input stream using BufferedReader；Both read lines in a loop until end of stream；Both handle exceptions (throws IOException/Exception)
- 行为差异: A extracts encoding substring from headers/content; B concatenates all lines into a template string；A doesn't cache; B caches the result in cachedTemplate；A checks HTTP headers before reading content; B reads content directly；Different return types: String encoding vs String template
- 修正建议: Incorporate dataflow analysis to capture common I/O operations；Use graph-based models (e.g., GraphCodeBERT) that capture structural dependencies；Train on more examples where similar boilerplate code serves different purposes

### case_id=5580 FP lexical_or_api_overlap

- 方法: `importSequences` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL to import biological sequences, parsing names and sequences.
- B 摘要: Reads a service configuration file from classpath to instantiate an OSGi FrameworkFactory.
- 静态失败原因: The static model likely overemphasized lexical overlap (e.g., URL, openStream, BufferedReader) and control flow structure (loop reading lines), lacking deep semantic understanding to distinguish the completely different purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the two functions perform entirely different domain tasks (biological sequence import vs. OSGi service loading) despite sharing superficial IO patterns.
- 共享行为: Both open a URL and read content line by line.；Both use BufferedReader/InputStreamReader.；Both handle IO exceptions.
- 行为差异: A imports sequences into lists; B returns a single FrameworkFactory instance.；A uses ImportHelper for parsing; B uses simple line reading with comment skipping.；A reads from user-selected URLs; B reads from a fixed classpath resource.；Different string parsing logic: tokenizer vs. trim/charAt checks.
- 修正建议: Incorporate task-level semantic knowledge (e.g., via docstring or type usage).；Use program analysis to capture data flow and output types.；Train on more diverse examples to differentiate similar API usage patterns.

### case_id=5581 FN partial_functionality

- 方法: `runInternal` vs `readVersion`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: runInternal() opens an HTTP connection, downloads and parses an OPDS catalog, handles pagination, and downloads books with progress reporting and error handling.
- B 摘要: readVersion() reads a version file from the classpath, parses key-value lines for version, revision, and date, and sets corresponding fields.
- 静态失败原因: Static BERT/GraphCodeBERT relies heavily on token overlap and syntactic structure, which are very low (Jaccard=0.096). It fails to capture the abstract functional pattern of 'read-parse from URL' that BCB considers a clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely annotates this as a clone because both functions share the high-level pattern of reading from a URL, parsing lines, and extracting information, which qualifies as a Type-4 clone under their broad functional similarity criteria.
- 共享行为: Both open a URL and read from it；Both read lines and parse them into data；Both handle I/O exceptions and close resources
- 行为差异: A uses HTTP with headers, redirects, and progress; B uses classpath resource without network settings；A parses OPDS XML and may fetch multiple pages; B parses simple key-value text from a single file；A has complex logic for download and error recovery; B is straightforward property parsing
- 修正建议: Incorporate data flow or program dependence graphs to capture I/O and parsing patterns；Use contrastive learning with Type-4 clone examples to learn functional similarity beyond token overlap；Add training data with diverse but functionally similar methods

### case_id=5582 FN partial_functionality

- 方法: `httpRequestByPOST` vs `startScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request to a URL with parameters, reads the response line by line, and returns the response string or null on error.
- B 摘要: Reads a script from a URL specified in attributes, reads the content line by line, appends it to a dialog script, and exits on IO error.
- 静态失败原因: The static model likely relied on token overlap and API-level similarity. Low Jaccard similarity (0.156) and different method names, API calls (HttpClient vs URL), and error handling patterns caused it to miss the core structural clone of the reading loop.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often annotates as clones pairs that share a common code pattern (reading URL content line by line) even if the overall functionality is different, considering it a Type-3/Type-4 clone due to partial functionality similarity.
- 共享行为: Reads from a URL line by line using BufferedReader wrapping InputStreamReader；Handles IOException in a try-catch block；Appends lines to a String/StringBuffer
- 行为差异: Function A uses HTTP POST with parameters and timeout; Function B uses HTTP GET via URL.openStream()；Function A returns the response string or null and sets error fields; Function B modifies dialog.script and prints error to stderr then exits；Function A uses Apache HttpClient; Function B uses standard java.net.URL；Function A has multiple return statements; Function B does not return a value (void)
- 修正建议: Incorporate dataflow analysis to detect common idioms like reading from a URL；Improve training with more examples of partial functionality clones；Use control-flow based features that highlight the sequence of stream operations；Implement a graph-based model that captures subgraph isomorphisms for common patterns

### case_id=5583 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter feed from a fixed URL using HttpClient and returns the response as a string.
- B 摘要: Downloads a file from a parameterized URL with optional Basic Auth, writes it to a temporary file, and updates a status label.
- 静态失败原因: The model likely over-weighted the common boilerplate code (BufferedReader, while loop, readLine) and ignored differences in return type, network library, and side effects (file writing, UI update).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clone when functions have different overall goals and I/O behavior, despite some shared reading pattern.
- 共享行为: Both perform HTTP GET requests；Both read response line by line using BufferedReader；Both use InputStreamReader to convert stream
- 行为差异: A uses Apache HttpClient, B uses URLConnection；A has fixed URL, B takes URL as parameter；A returns string, B writes to file and is void；A includes error logging, B throws IOException
- 修正建议: Include more structure-aware features like return type and method signatures；Add dataflow analysis to track how the read data is used

### case_id=5584 FN benchmark_preference_bias

- 方法: `getFile` vs `MotixFileItem`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.1`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a remote URL, modifies the endpoint attribute in the XML, and saves it to a temporary file.
- B 摘要: Constructor that reads an input stream into a byte array and optionally extracts image metadata using Sanselan.
- 静态失败原因: The static model likely predicted non-clone due to low token overlap and distinct purposes. BCB's clone label may be an annotation error or based on non-functional similarity, which static models are not designed to capture.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled these as clones based on a very broad interpretation of file processing routines, possibly considering both as 'file-related' operations. However, the specific functionality differs significantly.
- 共享行为: Both involve reading from an input source and processing data.
- 行为差异: A writes to a file and modifies XML; B stores in memory and extracts image info.；A uses NIO channels; B uses Apache IOUtils.；A has multiple catch blocks; B uses try-finally.
- 修正建议: Validate BCB annotations for consistency；Incorporate domain-specific knowledge or task context

### case_id=5585 FN benchmark_preference_bias

- 方法: `main` vs `bootKernel`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a zip file from a URL and extracts its entries to files.
- B 摘要: Reads a configuration from assets, copies sdcard assets to /sdcard/, and boots a custom kernel via reflection.
- 静态失败原因: The model likely focused on the significant structural and functional differences (different entry points, different purposes) and correctly predicted non-clone, but the BCB label may be incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both involving file I/O and stream processing patterns, though this is a very broad Type-4 interpretation that is likely a labeling error.
- 共享行为: Both perform file I/O operations using InputStream and OutputStream；Both involve loops reading data from streams
- 行为差异: A extracts a zip from HTTP; B copies assets and loads a kernel class；A is a standalone main method; B is an Android boot routine with configuration and reflection；A outputs to file names from zip entries; B outputs to /sdcard/ with predefined names
- 修正建议: Re-evaluate BCB annotations for consistency；Improve model to better capture high-level semantics and reject low-similarity pairs

### case_id=5586 FN partial_functionality

- 方法: `init` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Loads Java classes from a registry file and registers them via a controller.
- B 摘要: Reads Tibetan transliteration configuration from strings and a file to populate character sets and mappings.
- 静态失败原因: Low token overlap (0.08) and domain-specific APIs (Java reflection vs. StringTokenizer) caused the model to miss the high-level structural similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones because both are initialization methods that read configuration data and populate data structures using similar iterative patterns, fitting broad Type-3/Type-4 clone categories.
- 共享行为: Both read from input sources (file/string) in a loop；Both parse lines/tokens and process them conditionally；Both populate internal data structures (collections/maps)；Both handle I/O exceptions
- 行为差异: Different input types: Java classloader vs. StringTokenizer and file reader；Different output: class registration vs. character set construction；Different specific logic: class loading vs. character mapping and error handling for column counts；Different error handling: logging vs. print statements and throw errors
- 修正建议: Enhance model with AST or data-flow features to capture structural patterns；Use contrastive learning to recognize similar control flow and I/O patterns；Incorporate method-level documentation or comments as features

### case_id=5587 FN benchmark_preference_bias

- 方法: `doGet` vs `tail`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to retrieve and serve a portal page with permission checks, logging, and caching.
- B 摘要: Implements the tail command to read and output the last part of a file, optionally following new content.
- 静态失败原因: Because of very low lexical overlap, different method names, different libraries (javax.servlet vs java.io), and totally different control flows, the model confidently predicted non-clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'request processing' functions that read input, perform computation, and return output, despite different domains.
- 共享行为: Both handle input parameters (request parameter vs command-line argument)；Both read from a source (page from database vs file from filesystem)；Both produce output (HTTP response vs stdout)；Both have error handling and logging
- 行为差异: A is web-based, B is file I/O；A involves user permissions and session, B does not；A writes to HTTP response, B writes to stdout；A has caching logic, B has file seeking
- 修正建议: Improve model's ability to capture high-level semantic similarity across different APIs；Incorporate program analysis features like dataflow or API usage patterns；Use contrastive learning on diverse clone types

### case_id=5588 FN lexical_or_api_overlap

- 方法: `getFile` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies an endpoint attribute, and saves it to a temp file.
- B 摘要: Recursively copies a file or directory to a target location.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on token/API overlap (e.g., FileInputStream, FileOutputStream, logging) and missed the higher-level semantic distinction between network download and local file copy.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled them as clones due to both involving file I/O, stream operations, and logging, which can be considered broad Type-3/Type-4 similarity under partial functionality overlap.
- 共享行为: Both perform file input/output operations using streams.；Both include exception handling with logging.；Both check file existence or length before operations.
- 行为差异: Function A downloads from a URL and processes XML; function B copies local files/directories.；Function A returns a file location string; function B is void.；Function A involves XML parsing and modification; function B does plain byte/character copying.；Function B handles directory recursion; function A does not.
- 修正建议: Incorporate data flow analysis to capture the direction and source of data (network vs local).；Use control flow structure to distinguish iterative copying from XML manipulation.；Add context-aware embeddings that differentiate between download and copy semantics.

### case_id=5589 FN partial_functionality

- 方法: `doTransfer` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: This method acts as a servlet proxy, forwarding HTTP requests to another URL by copying headers and streaming request and response bodies.
- B 摘要: This method performs an HTTP POST request using Apache HttpClient with form parameters and returns the response body as a string.
- 静态失败原因: The functions have low token overlap and different APIs (servlet vs HttpClient). The model likely focuses on lexical tokens and may not capture the high-level HTTP concept.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider both as 'HTTP request handling' tasks, and thus label as clone despite different libraries and contexts.
- 共享行为: Both functions initiate HTTP connections and handle I/O between client and server.
- 行为差异: A uses servlet API and streams request/response; B uses HttpClient and returns a string.；A proxies requests including headers and body; B only sends form-encoded POST.；A writes to response output stream; B returns string.；A handles both request and response; B only handles response.
- 修正建议: Use more semantic-aware features, consider library usage patterns, or train on broader clone types.

### case_id=5590 FN partial_functionality

- 方法: `doTransfer` vs `getJSONData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an incoming HTTP request to another URL and returns the response to the original client.
- B 摘要: Fetches JSON data from a given URL using HTTP GET and returns the parsed JSON object.
- 静态失败原因: Static models like CodeBERT rely on token-level embeddings and may have missed the high-level semantic similarity due to low token Jaccard (0.13) and different API usage (HttpURLConnection vs HttpClient).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB labels this as a clone because both functions share the high-level goal of performing an HTTP request and processing the response, which is considered Type-4 functional similarity.
- 共享行为: Both make an HTTP request to a URL；Both read the response stream；Both handle exceptions and close resources
- 行为差异: doTransfer is a proxy that preserves headers and request method and writes the response to the output stream; getJSONData is a simple GET fetcher that returns a JSON object；doTransfer uses HttpURLConnection from java.net; getJSONData uses Apache HttpClient；doTransfer writes request body from the original request; getJSONData has no request body
- 修正建议: Use a model that captures overall program flow and high-level intent；Incorporate dataflow analysis or graph-based representations；Increase training data for abstract functional clones

### case_id=5591 FN benchmark_preference_bias

- 方法: `doGet` vs `setImg`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to retrieve and display a portal page, with permission checks, logging, and caching.
- B 摘要: Opens a file chooser to select an image, copies it to an images directory, and sets an image icon, with error handling and logging.
- 静态失败原因: Static BERT/GraphCodeBERT models typically focus on token-level and structural similarities; the low token Jaccard and disparate API usage led to a non-clone prediction. They failed to capture the high-level semantic alignment that BCB's broad definition accepts.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider these clones due to broad Type-4 semantic similarity: both are 'service methods' that process an input, perform file operations, handle errors, and log. The overall structure of try-catch, logging, and file I/O could be seen as functionally similar at a high abstraction level.
- 共享行为: Both perform file I/O operations (writing to temp file or copying image).；Both include exception handling with logging.；Both involve conditional checks (e.g., permission, file existence).
- 行为差异: Function A is a servlet handling web requests; Function B is a GUI method for image selection.；Function A has complex permission and caching logic; Function B has simple file copy and icon setting.；Function A logs via myLogger; Function B uses LogHandler and JOptionPane for user feedback.；Function A interacts with request/response objects; Function B uses JFileChooser and file streams.
- 修正建议: Incorporate higher-level abstraction features (e.g., control flow patterns, role of function).；Use graph-based models that capture long-range semantic dependencies.；Train with Type-4 clone examples to recognize behavioral similarity beyond lexical overlap.

### case_id=5592 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `wordFrequency`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft server handshake by validating username and session.
- B 摘要: Fetches word frequency from a web service using a pattern.
- 静态失败原因: Static BERT relied on lexical overlaps (e.g., URL, BufferedReader, try-catch) without understanding the distinct higher-level semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because they solve entirely different problems with no functional similarity.
- 共享行为: Both use try/catch blocks；Both use URL and BufferedReader for network I/O；Both print stack traces on exceptions
- 行为差异: Domain: Minecraft login vs word frequency query；Output: network shutdown or login packet vs integer frequency；Logic: username validation vs regex matching on web content
- 修正建议: Incorporate deeper semantic understanding via control-flow or data-flow analysis；Use graph-based representations to capture program structure；Fine-tune on BCB-style annotations to penalize shallow lexical matches

### case_id=5593 FN boilerplate_overlap

- 方法: `modifyApplicationMessage` vs `testCodingEmptyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale by updating or appending a key-value pair.
- B 摘要: Tests that a LengthDelimitedEncoder correctly handles an empty file by transferring zero bytes.
- 静态失败原因: The static model likely relied on low token Jaccard (0.08) and distinct method names/purposes, predicting non-clone. However, BCB's broader criteria might have missed that these are functionally unrelated beyond basic I/O.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have considered both as clones due to shared use of java.io.File, file reading/writing, and string manipulation, despite very different high-level purposes.
- 共享行为: Both involve file input/output operations；Both manipulate strings
- 行为差异: A: modifies properties files; B: tests an encoder；A: reads/writes .properties files with locale-specific logic; B: uses ByteArrayOutputStream and FileChannel；A: utility method; B: unit test method；A: handles exceptions by printing stack trace; B: throws Exception
- 修正建议: Incorporate better detection of partial functionality overlap；Avoid using generic I/O operations as strong clone evidence；Consider complementing token-level with structural or control-flow features

### case_id=5594 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a file of zone IDs and returns a set of integers.
- B 摘要: Reads a version check file, extracts build numbers, and performs a version check with UI feedback.
- 静态失败原因: The model likely focused on lexical overlap (URL, openStream, InputStreamReader, readLine, while loop) and similar exception handling structure, missing the semantic intent of the extracted data and the downstream logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the two functions have distinctly different purposes: one is a simple utility to read integer IDs, the other is a version check with conditional logic and UI. The shared boilerplate (URL reading) is not sufficient for Type-4 similarity.
- 共享行为: Both open a URL or resource stream；Both read lines using while loop with readLine；Both parse each line；Both handle exceptions
- 行为差异: A parses every line as integer and adds to set; B checks line prefixes and extracts substrings；A returns a set; B is void and calls another method；A prints stack trace on exception; B shows error dialog and hides wait cursor；B has UI interactions (wait cursor, error dialog), A does not
- 修正建议: Improve model to consider method names and complete control flow；Use data flow analysis to capture transformations of the data；Train on more diverse examples to distinguish boilerplate from core semantics

### case_id=5595 FP long_range_semantics

- 方法: `copyFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Handles actionPerformed event for UI settings, including file choosers and preference updates.
- 静态失败原因: The model might have been misled by surface-level features like both methods having File objects and try-catch blocks, or due to long-range dependencies in function B making it difficult to capture the full context.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled as non-clone because functions are semantically unrelated despite both having file operations; B's primary purpose is UI event handling.
- 共享行为: Both involve file I/O in some form (function A does file copy, function B uses JFileChooser to select files).
- 行为差异: Function A is a focused utility for copying files; function B is a large event handler managing multiple UI commands and preferences.
- 修正建议: Improve handling of long methods with sliding window or hierarchical attention.；Incorporate structural information like method signatures and class context.

### case_id=5596 FN partial_functionality

- 方法: `httpRequestByPOST` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with parameters and reads the response, returning the response string or null on error.
- B 摘要: Opens a URL, reads lines, extracts build version strings, and calls another method for version check, showing an error dialog on failure.
- 静态失败原因: The model likely focused on different method names, parameter lists, and error handling, missing the high-level structural similarity of the HTTP request-response loop; low token Jaccard (0.22) and different API usage (HttpClient vs URL) contributed.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions perform an HTTP request and read the response line by line, a common pattern despite differences in method details, fitting Type-4 semantic similarity.
- 共享行为: Both make an HTTP request；Both read response line by line using BufferedReader；Both handle IOException
- 行为差异: A uses POST with parameters; B uses GET with no parameters；A returns a String; B is void and calls another method；A sets error fields and returns null; B shows an error dialog；A uses Apache HttpClient; B uses java.net.URL
- 修正建议: Train on more diverse semantic clone examples with different APIs and error handling；Use structural or dataflow representations capturing request-response I/O pattern；Incorporate knowledge of common HTTP client patterns across libraries

### case_id=5597 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint, and saves it to a temporary file.
- B 摘要: Copies a local file to a destination file using FileChannel.transferFrom.
- 静态失败原因: Static BERT models rely on token sequence similarity, which is low (Jaccard 0.12). The semantic similarity through transferFrom is subtle and not captured by surface-level tokens, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled as clone because both functions share the core pattern of transferring bytes using FileChannel.transferFrom, considered functionally similar at a low level (Type-4 clone).
- 共享行为: Both use FileChannel.transferFrom to transfer data between channels；Both perform file I/O with streams and channels；Both include logging
- 行为差异: A downloads from URL and modifies XML; B copies a local file；A returns a file path string; B returns void；A has extensive error handling for multiple exceptions; B only throws IOException；A creates temporary files and renames; B does not
- 修正建议: Use graph-based code representations to capture data flow and channel operations；Include more training examples of Type-4 clones where a small core pattern is shared despite different contexts

### case_id=5598 FN benchmark_preference_bias

- 方法: `unzipModel` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: unzipModel extracts all entries from a zip file and writes them to a temporary directory.
- B 摘要: getResourceAsStream retrieves a resource (possibly from remote URL with caching) and returns its InputStream, caching the content locally.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted no clone because the functions have fundamentally different control flows and purposes (zip extraction vs. URL caching), with low token overlap (0.168).
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider these clones due to shared stream-based I/O patterns (Type-4 functional similarity), despite differing high-level purposes.
- 共享行为: Both use buffered I/O streams (BufferedInputStream, BufferedOutputStream) to read and write data in a loop
- 行为差异: unzipModel iterates over zip entries, while getResourceAsStream handles caching, URL connections, and HTTP responses；unzipModel writes directly to files in a directory, whereas getResourceAsStream manages a cache and returns an InputStream
- 修正建议: Refine BCB annotation criteria to avoid overly broad Type-4 clones；Incorporate higher-level semantic understanding of function purpose beyond I/O patterns

### case_id=5599 FP lexical_or_api_overlap

- 方法: `GetResponse` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A private method that performs an HTTP GET request and returns the response body as a string, handling exceptions silently.
- B 摘要: A GUI browser constructor that reads a URL, optionally transforms XML with XSLT, and displays the result in a JEditorPane, with full UI setup.
- 静态失败原因: Static BERT models may rely on surface-level patterns like 'URL', 'BufferedReader', 'readLine', and 'IOException' which appear in both snippets, causing a false positive due to lexical/API overlap neglect of context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels Type-3/4 clones as positive only if there is a substantial functional overlap. Here, despite both reading a URL, the purposes and code structures are vastly different, so BCB correctly judged them as non-clones.
- 共享行为: Both open a URL and read content from it using BufferedReader.；Both handle IOException with basic error reporting.
- 行为差异: Function A is a simple HTTP GET returning a string; function B is a GUI constructor with complex XML/XSLT processing and UI layout.；Function A silently catches exceptions without user feedback; function B warns the user on IOException.；Function A returns null on failure; function B sets up a visible window regardless.；Function B involves XML parsing, stylesheet transformation, and HTML rendering, none of which exist in A.
- 修正建议: Increase reliance on structural differences (e.g., method length, control flow complexity).；Add features capturing the functional role (utility method vs. GUI constructor).；Use data flow analysis to distinguish the different purposes of the I/O operations.

### case_id=5600 FP boilerplate_overlap

- 方法: `cookieString` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes an SHA-1 hash of concatenated URL, IP, and salt, returning hex string.
- B 摘要: Handles HTTP request, validates session, processes form data, sends HTTP POST, parses XML response, and forwards to a view.
- 静态失败原因: The static BERT model likely was misled by superficial similarities such as both methods having try-catch blocks and logging, and possibly the truncated code B caused the model to miss the core logic, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have completely different purposes and algorithms; no shared functionality.
- 共享行为: Both use try-catch for exception handling.
- 行为差异: Function A is a simple hash utility; Function B is a complex web controller with multiple responsibilities.；Function A uses MessageDigest; Function B does not.；Function A returns a hash string; Function B returns an ActionForward.；Function B involves session management, HTTP connections, XML parsing; Function A does none of these.
- 修正建议: Avoid truncating long methods during input preprocessing; use full method body or better segmentation.；Incorporate data flow and control flow analysis to differentiate shallow code patterns.；Train on more diverse examples to reduce false positives from boilerplate code.

### case_id=5601 FP boilerplate_overlap

- 方法: `encrypt` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reverses input string and computes its SHA-256 hash.
- B 摘要: Handles HTTP request to classify a concept, builds XML, sends it to a URL, parses response, and returns forward action.
- 静态失败原因: The static method likely focused on surface-level patterns (loops, string operations) and ignored overall semantics due to the length and complexity of function B, possibly truncated.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones as they share no functional similarity; the label 0 aligns with typical Type-3/Type-4 criteria.
- 共享行为: Both use loops and string building (StringBuilder/StringBuffer).；Both handle exceptions (e.g., NoSuchAlgorithmException, IOException).
- 行为差异: Different domain: encryption vs web request handling.；Different inputs and outputs: encrypt takes string and returns hash; perform takes HTTP objects and returns ActionForward.；Different operations: reverse+hash vs HTTP communication and XML processing.
- 修正建议: Improve long-range semantic understanding via graph neural networks or data flow analysis.；Use code summary or method-level embeddings to capture purpose.；Incorporate domain-specific features (e.g., API calls).

### case_id=5602 FP lexical_or_api_overlap

- 方法: `getVersion` vs `fetchUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves version string from a hardcoded URL, returning first line or null.
- B 摘要: Fetches entire content of a given URL as a single string, returning empty string on failure.
- 静态失败原因: High lexical and API overlap (URL, BufferedReader, while loop) misled the model into considering them clones despite different semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions have different purposes (version checker vs generic URL fetcher) and different error handling policies, even though they share similar I/O boilerplate.
- 共享行为: Both open a URL connection；Both read lines from an input stream
- 行为差异: A hardcodes URL, B takes parameter；A returns only first line, B concatenates all lines；A returns null on exception, B returns empty string；A is private static, B is public static
- 修正建议: Incorporate structural program matching；Differentiate data flow and error handling；Consider function signatures and purpose

### case_id=5603 FN lexical_or_api_overlap

- 方法: `main` vs `buildDeb`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to files.
- B 摘要: Builds a Debian package archive from control and data files.
- 静态失败原因: Static BERT models may over-rely on lexical and API token overlap (e.g., FileInputStream, read, write) and fail to capture the distinct high-level purposes.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled as clone due to structural similarity in the stream copying pattern, which is a common code fragment across different applications.
- 共享行为: Both use input/output streams with buffered reading and writing.；Both have loops that read from an input stream and write to an output stream.
- 行为差异: Function A handles HTTP URL and zip extraction, while B creates a specific archive format.；Function A processes multiple zip entries, B creates specific archive headers.；Function A uses ZipInputStream, B uses custom start/end file entry methods.
- 修正建议: Incorporate data flow analysis to distinguish different program intents.；Use contextual embeddings that consider method names and comments.；Train on diverse negative samples with similar API usage but different semantics.

### case_id=5604 FP partial_functionality

- 方法: `importRoles` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads roles from a URL by parsing XML-like lines and returns a list of RoleName objects.
- B 摘要: Retrieves tickets for a specific queue from a REST API by parsing response and fetching each ticket, returning a list of RTTicket.
- 静态失败原因: The model may have been misled by overlapping boilerplate code (URL, BufferedReader, try-catch, list returning) and token similarity from common Java keywords, causing a false positive. The method names and domain-specific logic are too different for a correct clone classification.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled as non-clones because the functions serve entirely different business purposes and produce different types of output, despite sharing a general reading/parsing pattern. The high-level functionality is not semantically similar.
- 共享行为: Both read from remote URLs using BufferedReader/InputStreamReader；Both iterate over lines and collect results；Both have try-catch for I/O exceptions
- 行为差异: Different HTTP methods (plain URL vs HttpGet with parameters)；Different parsing logic (checking for </RoleName> vs lines starting with 'ticket/')；Different error handling (silent catch vs logging and returning null)；Different domain objects (RoleName vs RTTicket)
- 修正建议: Incorporate structural alignment to focus on method-level semantics；Use more discriminative features like method names and domain types；Train with more contrasting examples of partial functionality

### case_id=5605 FN partial_functionality

- 方法: `runInternal` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Connects to an HTTP URL, handles redirects and errors, reads OPDS catalog entries with pagination or downloads a book, with progress reporting.
- B 摘要: Connects to a hardcoded HTTP URL, reads the entire response into a string buffer, and logs it.
- 静态失败原因: Extremely low token Jaccard (0.0777) means almost no lexical overlap. The long context and many unique identifiers in A (e.g., CoolReader-specific names) dominate the embedding, masking the shared HTTP operations. BERT models struggle to abstract the core semantic pattern from such different surface forms.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often annotates as clones functions that share a core functionality (HTTP GET and read response) even if one is much simpler. The annotator likely considered the essential similarity of fetching URL content, tolerating the additional complexity in A.
- 共享行为: Both open an HTTP URL connection using URL.openConnection()；Both read data from the input stream of the connection
- 行为差异: Function A has complex pagination logic with multiple iterations; B is a single read；Function A handles HTTPS rejection, redirects, timeouts, content-disposition, and multiple content types; B has no such handling；Function A includes progress reporting and callbacks; B just logs；Function A has extensive error handling; B has none (throws Exception)
- 修正建议: Extract sub-graphs of API call sequences (e.g., URL.openConnection, getInputStream) and compare them；Use code summarization to capture high-level intent (fetch URL content) rather than raw tokens；Apply data-flow analysis to focus on critical I/O operations；Consider type-based matching for URLConnection usages

### case_id=5606 FN partial_functionality

- 方法: `copyResource` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or local file) to a destination file using byte-by-byte streaming, throwing an exception on failure.
- B 摘要: Copies a file or directory recursively to a destination using FileChannel, with null-checks, console logging, and error printing.
- 静态失败原因: Low token Jaccard (0.173) indicates minimal lexical overlap; the model relied on token and surface-level structure, which differ significantly (e.g., recursion, FileChannel vs InputStream, error handling patterns), leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered that both functions achieve the core goal of copying data from a source to a destination, despite differences in implementation details and additional functionality.
- 共享行为: Both copy data from a source to a destination
- 行为差异: A supports URL sources; B only File objects；A uses byte-by-byte loop; B uses FileChannel for efficient transfer；B handles directories recursively; A does not；B includes null checks and exits on null; A throws exceptions
- 修正建议: Incorporate dataflow or control-flow analysis to recognize common high-level semantics；Use program summarization or clone detection techniques that abstract over API choices；Train on examples that are semantically similar but lexically diverse

### case_id=5607 FP lexical_or_api_overlap

- 方法: `readRemoteFile` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a remote file from a hardcoded URL and returns its content as a string.
- B 摘要: Loads a URL (with optional basic authentication), reads its content, writes it to a temporary file, and updates a UI label with download progress.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-emphasized the lexical and API overlap (URL, BufferedReader, readLine) and structural similarity, missing the divergent IO operations and UI interactions.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions differ significantly in side effects and output handling, despite sharing core URL reading logic.
- 共享行为: Open a URL connection；Read content using BufferedReader；Read lines in a loop
- 行为差异: Function A returns the content as a string; function B writes content to a file and updates UI.；Function B handles authentication; A does not.；Function B creates a temporary file and manages file writing; A does not.；Function B updates a status label; A prints errors to console.
- 修正建议: Incorporate dataflow or control-flow features to distinguish side effects like file writing and UI updates.；Use contrastive training on pairs that differ in IO behavior despite similar API sequences.；Add static analysis to capture output destinations and external interactions.

### case_id=5608 FP lexical_or_api_overlap

- 方法: `scrapeForIsbns` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Scrapes ISBN-10 numbers from a URL with retry and exception handling.
- B 摘要: Searches Google Images, extracts image URLs, and updates a GUI component.
- 静态失败原因: Static BERT/GraphCodeBERT likely overfit to structural boilerplate (opening URL, reading lines, using BufferedReader) and ignored deeper semantics and specific parsing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers functional equivalence; these functions have different purposes and outputs, so they are not clones even under broad Type-3/4 criteria.
- 共享行为: Open a URL and read response line by line；Use BufferedReader and InputStreamReader；Perform text matching/regex operations on the response
- 行为差异: Input types differ: URL vs. String+String；Return type: int count vs. void；Parsing target: ISBN-10 numbers vs. image URLs；B includes GUI updates and image display
- 修正建议: Enhance training data with examples where similar API usage patterns lead to different functionalities.；Incorporate variable names and comments or use data-flow analysis to distinguish parsing targets.

### case_id=5609 FP boilerplate_overlap

- 方法: `readData` vs `compress`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads configuration data from string tokens and a file into various sets and maps for script processing.
- B 摘要: Concatenates input files into an output file and optionally compresses it using an external tool.
- 静态失败原因: A static BERT/GraphCodeBERT likely overemphasized common API tokens (e.g., 'File', 'IOException', 'while', 'String') and boilerplate patterns, missing the deep semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this non-clone because the functions have entirely different functionality and structure, despite both containing loops and I/O; task overlap is minimal.
- 共享行为: Both use loops to process multiple items (tokens or files)；Both involve file I/O operations
- 行为差异: Function A parses tokens and a file to build data structures; Function B concatenates files and invokes a compressor；Function A has complex conditional logic for parsing; Function B is straightforward file copying；Function A uses HashSets/HashMaps; Function B uses file streams
- 修正建议: Incorporate dataflow analysis to differentiate core logic from boilerplate；Use contrastive learning with more varied non-clone pairs sharing APIs；Enhance model attention to task-specific identifiers and control flow

### case_id=5610 FN partial_functionality

- 方法: `copyResource` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file byte by byte.
- B 摘要: Downloads a WSDL file from a URL, optionally modifies its XML content, and saves it to a temporary directory, returning the file path.
- 静态失败原因: The low token Jaccard similarity (0.1185) and significant differences in method signatures, control flow, and additional logic (XML parsing, file checks) caused the static BERT model to overlook the underlying semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may view both functions as performing the core task of 'copying a resource from a URL to a file', considering the additional XML manipulation and file existence checks in B as extensions rather than a different functionality, thus labeling it as a Type-3/Type-4 clone.
- 共享行为: Both read data from a URL；Both write data to a file；Both can throw exceptions during I/O；Both use InputStream and OutputStream (or similar) for basic I/O
- 行为差异: B modifies XML content after download; A does not；B checks if file already exists and skips download if present; A always overwrites；B uses NIO channels for efficient transfer; A reads byte-by-byte；B returns a file path; A returns void
- 修正建议: Train models to identify core functionality even when embedded in larger contexts, e.g., via dataflow analysis.；Use contrastive learning to emphasize semantic intent over lexical overlap.；Include training examples with varying levels of additional logic around a common core.

### case_id=5611 FP lexical_or_api_overlap

- 方法: `populateResources` vs `getUser`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Populates default templates and image properties from resources.
- B 摘要: Retrieves a user by login, loading from DAO or parsing a configuration file.
- 静态失败原因: The model likely relied on superficial lexical similarities (BufferedReader, URL, try-catch) and common programming patterns, ignoring the distinct semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider them clones because they have completely different purposes; only superficial lexical overlap like reading files.
- 共享行为: Both use BufferedReader to read from file resources
- 行为差异: populateResources is static void and loads multiple resources into database；getUser returns a User object and performs authentication logic
- 修正建议: Enhance training data with non-clone pairs sharing API calls but different semantics；Improve dataflow analysis to capture variable purposes and data dependencies

### case_id=5612 FN other

- 方法: `modifyApplicationMessage` vs `getResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by updating or adding a key-value pair for internationalization.
- B 摘要: Generates an HTTP response byte array by parsing a GET request and serving a classpath resource.
- 静态失败原因: Static BERT may have focused on low token overlap and completely different method names and domains, leading to low similarity prediction. It likely missed the weaker structural similarity in I/O patterns.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have considered both as 'resource loading and writing' operations, overlooking domain differences due to superficial similarity in stream handling and conditional logic.
- 共享行为: Both read input from streams (file/classpath) and write output to streams (file/bytearray).；Both handle cases where resource may not exist (file not found / resource null).
- 行为差异: Function A modifies an existing properties file, while B generates a fresh HTTP response.；Function A reads and writes properties files in a specific format, B reads and writes byte streams with HTTP headers.；Function A has copy-file-on-first-use logic, B does not.；Function A uses line-by-line parsing for key-value pairs, B uses line parsing for GET command extraction.
- 修正建议: Include more contextual information such as method names and class hierarchy to disambiguate.；Use dataflow analysis to distinguish file modification from HTTP response generation.；Re-evaluate BCB annotations for this pair; it may be a benchmark error.

### case_id=5613 FN benchmark_preference_bias

- 方法: `logging` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Logs inbound message details by extracting encoding, headers, and content stream, caching the payload, and logging it.
- B 摘要: Handles HTTP GET request to retrieve and render a page, with logging of requests and caching of output.
- 静态失败原因: The static BERT/GraphCodeBERT model likely failed because the low token Jaccard (0.093) and very different API surfaces made it correctly identify them as non-clones, but BCB considered them clones based on vague structural similarities, which the model could not capture.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to both methods containing similar structural patterns (logging, exception handling, I/O) and possibly considering them as partial functionality overlaps, but this is a very broad interpretation.
- 共享行为: Both use logging frameworks to output information；Both handle exceptions using try-catch blocks；Both involve I/O operations (InputStream, writing to streams)
- 行为差异: A is a generic logging utility for messages; B is a specific servlet method with page retrieval and rendering；B includes complex logic for page visibility, authorization, and caching; A is straightforward logging；B interacts with HTTP request/response objects and database; A only deals with message wrapping
- 修正建议: Re-examine BCB labels for such pairs to ensure consistency；Use more refined clone detection criteria that focus on actual semantic equivalence；Incorporate human verification for ambiguous cases

### case_id=5614 FP partial_functionality

- 方法: `get` vs `startScript`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP GET request with custom headers to retrieve game records from a URL, reads the response line by line, filters out comment lines, decodes each line as a GameRecord, and returns an array of GameRecord objects.
- B 摘要: Reads a script from a URL specified in an attribute, opens a stream, reads each line and appends it with a newline to a dialog script string, and exits on error.
- 静态失败原因: The static BERT model overemphasized the common subsequence of reading lines from a URL (boilerplate) and ignored the semantic differences in line processing and output/side effects, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers these non-clones because the overall behavior and purpose are different: one retrieves structured game records, the other loads an unstructured script. Despite shared I/O patterns, the processing logic and outputs are distinct.
- 共享行为: Both open a URL connection and read content line by line using BufferedReader and InputStreamReader
- 行为差异: Function A uses HTTP GET with custom headers (latitude, longitude, count), while function B directly opens a stream without headers.；Function A parses lines into GameRecord objects skipping comment lines; function B concatenates raw lines into a script string.；Function A returns an array of GameRecord; function B modifies a dialog object (side effect) and returns void.；Error handling: function A prints exception and returns null; function B prints error and exits.
- 修正建议: Incorporate data flow analysis to track how each line is processed (parsing vs concatenation).；Compare output types and side effects (return type vs void with state modification).；Use contrastive learning to differentiate activities like 'fetching records' vs 'loading script'.

### case_id=5615 FP lexical_or_api_overlap

- 方法: `encode` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Encodes a string to its MD5 hexadecimal representation.
- B 摘要: Performs a Struts action that processes a classification request, sends XML to a remote URL, and sets session attributes.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on common API calls (getBytes, digest, StringBuffer) and lexical overlap, missing the stark semantic differences in overall functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the functions have completely different purposes and behaviors, despite superficial similarities like using StringBuffer and exception handling.
- 共享行为: Both use StringBuffer to build a result string.；Both have try-catch blocks for exception handling.
- 行为差异: Function A calculates an MD5 hash; Function B handles a web request and classification logic.；Function A takes a single string input; Function B takes an ActionMapping, ActionForm, and HTTP objects.；Function A returns a hex string; Function B returns an ActionForward for navigation.；Function B involves network I/O, session management, and multiple business objects.
- 修正建议: Improve training data to include more diverse non-clone pairs with low token overlap but similar API usage.；Enhance model with dataflow or control flow analysis to distinguish different high-level intents.；Use contrastive learning to penalize incorrect similarity for functions with different purposes.

### case_id=5616 FN benchmark_preference_bias

- 方法: `addIDs` vs `readURL`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Fetches metabolite data from a URL constructed from a name, parses HTML to extract metabolite IDs and related properties, and updates a PeakListRow object.
- B 摘要: Reads content from a URL and prints each line to standard output.
- 静态失败原因: Static BERT models rely on token and structural similarity. These functions have low token overlap (0.13) and different control flows (complex conditionals vs. simple loop). The model correctly identified them as non-clones based on lack of semantic similarity; the BCB label appears to be an outlier.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones because both involve reading from a URL using BufferedReader and processing the content line by line, suggesting a common pattern of URL reading. However, the specific processing and output differ greatly, and BCB typically requires more than just shared API usage for Type-4 clones.
- 共享行为: Both open a URL and read lines using BufferedReader.
- 行为差异: Code A parses HTML to extract metabolite IDs and updates a data row; code B simply prints lines.；Code A returns an integer score; code B returns void.；Code A constructs a specific URL based on input; code B takes an already constructed URL.；Code A uses conditional logic to handle different HTML patterns; code B has no conditional logic.
- 修正建议: Re-evaluate BCB label: these functions are not semantically similar and should not be clones.；If BCB expects broad Type-4, clarify annotation guidelines to avoid such false positives.；Train models with better semantic understanding, e.g., using control flow graphs or attention to I/O patterns.

### case_id=5617 FP boilerplate_overlap

- 方法: `doVersionCheck` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for updated version by reading lines from a URL and parsing version numbers.
- B 摘要: Downloads an RDF model from a URL using HTTP connection and returns it.
- 静态失败原因: Static BERT likely relied on token overlap (URL, InputStream, IOException) and structural similarity, misclassifying due to overgeneralization of common API usage patterns as indicative of clones.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels clones based on functional similarity; here functionality is completely different despite shared API usage, so non-clone.
- 共享行为: Both open a URL connection and read from an InputStream.；Both handle IOException.
- 行为差异: Different overall goal: version check vs model download.；Different input and output types.；Different data processing: line-by-line vs entire stream into model.；Different error handling: GUI error vs logging and Runtime exception.
- 修正建议: Improve model to capture higher-level semantic intent beyond API surface.；Incorporate control-flow and data-flow analysis.；Increase diversity in training to distinguish similar API usage with different purposes.

### case_id=5618 FN partial_functionality

- 方法: `unzipEntry` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Extracts a single zip entry to a file, creating directories and using buffered stream copy with resource cleanup.
- B 摘要: Launches a NexOpen project configuration by handling Maven POM files, setting up Hibernate properties, creating reverse engineering files, and scheduling an install action, with stream copy and property manipulation.
- 静态失败原因: Static BERT models rely on token and structure overlap; token Jaccard is very low (0.05), method names differ, and overall code structures are dissimilar. The shared stream copy behavior is a small part of function B, not dominant, so the model failed to detect the partial clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a Type-4 clone due to shared stream copy and IO handling patterns, despite different high-level purposes, considering partial functionality similarity.
- 共享行为: Both involve reading an input stream and writing to an output stream using IOUtils.copy；Both use try-finally for resource cleanup；Both handle IO exceptions and create files
- 行为差异: Function A is a simple file extraction of a zip entry; function B is a complex Eclipse launch with multiple steps；Function A operates on ZipFile and ZipEntry; function B operates on ILaunchConfiguration, IProject, and Eclipse resources；Function B includes property setting, persistent property manipulation, and project scheduling not present in A
- 修正建议: Train models to recognize common IO patterns across different contexts；Use dataflow analysis to detect stream copying subroutines；Combine structural and semantic matching at multiple granularity levels

### case_id=5619 FP lexical_or_api_overlap

- 方法: `copy` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file from source to destination using FileChannel's transferTo method.
- B 摘要: Main method of an adapter generator that parses a Prolog file and generates adapter classes and a JAR file.
- 静态失败原因: Static BERT models may have been misled by lexical overlap (e.g., 'File', 'IOException', 'try') and boilerplate exception handling, despite no real functional similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because their functionality is entirely different, and even a broad Type-4 interpretation would not find semantic similarity.
- 共享行为: Both use File objects and handle IOException.
- 行为差异: Function A is a simple file copy; Function B is a complex multi-step process.；Function A uses FileChannel; Function B uses FileUtils, Parser, ClassWriter, etc.；Function A throws IOException; Function B catches exceptions internally.；Function B produces console output; Function A does not.
- 修正建议: Incorporate control flow and data flow information to distinguish simple I/O from complex logic.；Use larger negative mining that includes functions with only superficial token overlap.

### case_id=5620 FN partial_functionality

- 方法: `getURLContent` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads content from a given URL and returns it as a string.
- B 摘要: Executes an HTTP POST RPC invocation, reads the response, deserializes JSON, with retry and service discovery.
- 静态失败原因: Static BERT models rely on token-level similarity and function names; the low Jaccard score (0.20354) and different method signatures caused the model to miss the shared reading pattern embedded in a larger, different context.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both contain a core pattern of reading an HTTP response as text, which is a common functional fragment. BCB's guidelines often allow broad Type-3/Type-4 similarity based on partial functionality.
- 共享行为: Reads HTTP response content line by line into a StringBuilder with newlines
- 行为差异: A takes a URL string; B takes an invocation object and builds a full HTTP POST request.；A uses URLConnection; B uses HttpClient with retry and error handling.；A returns raw string; B deserializes JSON and handles return types.；B includes service discovery and relocation logic; A does not.
- 修正建议: Incorporate dataflow analysis to identify common subroutines like reading HTTP response.；Use graph-based models that capture control/data flow patterns.；Augment training data with pairs exhibiting partial functional similarity.

### case_id=5621 FP lexical_or_api_overlap

- 方法: `main` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method of an adapter generator that parses Prolog files and generates adapter JARs.
- B 摘要: Main method demonstrating file I/O with FileChannel and ByteBuffer for different encodings.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by lexical overlaps such as common API usage (File, FileChannel, ByteBuffer) and the generic 'main' method name, ignoring the vastly different overall behavior and logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the two functions have no semantic similarity: one is a sophisticated code generation tool, the other an educational file I/O snippet.
- 共享行为: Both are public static void main methods；Both perform file I/O using File, FileChannel, ByteBuffer；Both use System.out.println for output
- 行为差异: Function A is a complex tool with parsing, reflection, and JAR generation; Function B is a simple file I/O demo；Function A uses multiple libraries (Prolog, ASM); Function B only uses standard I/O and NIO；Function A has extensive error handling; Function B throws Exception；Function A writes binary data and metadata; Function B writes and reads text using different character sets
- 修正建议: Use structural or data-flow analysis to capture high-level differences in functionality；Incorporate larger context or documentation embeddings；Fine-tune on task-specific negative examples with low token Jaccard but high API overlap

### case_id=5622 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads zone IDs from a resource file by parsing each line as an integer and returns a set.
- B 摘要: Downloads content from a URL with optional HTTP authentication, writes it to a temporary file, and updates a status label with progress.
- 静态失败原因: Static BERT/GraphCodeBERT may overemphasize lexical overlap (e.g., 'readLine', 'URL', 'InputStreamReader') and structural pattern of reading lines, ignoring critical differences in data handling and auxiliary operations (authentication, file writing, UI update). The model might be biased towards common boilerplate patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones due to significant differences in overall purpose, input/output, and complexity. While both read lines, the core functionality differs substantially: one is a data extraction, the other is file download with progress.
- 共享行为: Both open a connection and read lines from an input stream line by line.
- 行为差异: A parses each line as integer and stores in HashSet; B writes raw lines to a file and updates UI.；A handles resource from classpath; B handles remote URLs with authentication.；A is static and returns a set; B is void and instance method, writes to temp file.；A has simple exception handling; B throws IOException and has complex logic.
- 修正建议: Include dataflow analysis to track how read lines are used (parsed vs. written to file).；Add context of method signature (return type, parameters, exception) to distinguish.；Use structural similarity based on control flow and data dependencies, not just API calls.

### case_id=5623 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `copyTo`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles various UI action commands to set preferences like graphviz, imagemagick, scale image, date format, look and feel, etc., using file choosers and updating the UI.
- B 摘要: Recursively copies a file or directory to a destination using file channels, handling hidden files and directory creation.
- 静态失败原因: The model likely over-relied on surface-level tokens like 'File' and basic control structures (if-else, try-catch) present in both, without understanding the high-level semantic context. The low Jaccard similarity suggests the model should have predicted non-clone; this false positive may be due to training data noise or insufficient disambiguation of file-related operations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have entirely different purposes and no meaningful shared functionality, despite both involving files.
- 共享行为: Both operate on files as part of their input/output
- 行为差异: Function A is a UI event handler that sets application preferences through dialogs；Function B is a file system utility that copies files/directories；Function A uses JFileChooser for user interaction, Function B uses FileChannel for data transfer；Function A updates global controller state (Suku.kontroller), Function B does not interact with any application state
- 修正建议: Enhance model with structural similarity metrics like AST or data-flow graphs；Incorporate method-level documentation or type signatures to disambiguate UI event handlers from utility methods

### case_id=5624 FP lexical_or_api_overlap

- 方法: `readData` vs `copyJar`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads and parses multiple comma-separated string fields from class-level variables to populate various sets and a hash map for Tibetan transliteration data, including file reading.
- B 摘要: Copies a file from source to destination using NIO FileChannels with exception handling.
- 静态失败原因: Likely due to both functions mentioning File operations and exception handling (IOException, try/catch), causing a spurious similarity. Static models may over-rely on overlapping tokens like 'IOException', 'file', 'try', 'catch' without understanding semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones for functions with completely different tasks, even if both involve I/O. The functions have no overlapping functionality.
- 共享行为: Both are static or private methods handling I/O operations；Both catch IOException
- 行为差异: A parses configuration data into sets and maps; B copies a file byte-by-byte；A uses StringTokenizer and complex logic; B uses FileChannel.transferFrom；A reads from a file and populates data structures; B writes to a file；A has a long, multi-step initialization; B is a short utility
- 修正建议: Incorporate dataflow analysis to distinguish I/O utility from data parsing；Use structural similarity or finer token distinction (e.g., differentiate API usage patterns)；Employ context-aware embeddings that capture task-level semantics

### case_id=5625 FN boilerplate_overlap

- 方法: `doImageProcess` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Processes an image from a URL or input stream and writes it to the HTTP response, optionally resizing.
- B 摘要: Handles an HTTP GET request for a page, retrieves page content from a database, and writes it to the response, including caching logic.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token and syntactic similarity, which is low (Jaccard 0.097). The models likely missed the high-level functional similarity that BCB annotators saw, possibly due to capturing boilerplate patterns as different from the core domain-specific code.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as servlet request handlers that produce output, and thus deem them as Type-4 clones under a broad interpretation of semantic similarity, focusing on the overall pattern of reading input and writing to the response.
- 共享行为: Both take HttpServletRequest and HttpServletResponse parameters；Both write output to the response OutputStream；Both flush and close the OutputStream；Both handle exceptions and send error responses
- 行为差异: Function A processes image data; Function B processes page objects and HTML；Function A reads from a URL or input stream; Function B reads from a database using page IDs or names；Function B includes user authorization, logging, caching, and page rendering; Function A does not；Function A may resize images; Function B does not
- 修正建议: Incorporate higher-level semantic representations of servlet request handling patterns；Use data flow or control flow analysis to abstract common I/O patterns；Train with more examples of Type-3/Type-4 clones that share boilerplate but differ in domain

### case_id=5626 FN partial_functionality

- 方法: `sendExceptionToServer` vs `import_hints`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST.
- B 摘要: Imports puzzle hints from a file or URL and places pieces on a board.
- 静态失败原因: Static models like GraphCodeBERT likely relied on token overlap and syntactic structure, which are low (Jaccard 0.1475). The model may not have captured the high-level conceptual similarity of URL I/O because the specific API calls are embedded in different contexts and overall control flow differs.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered these as Type-4 clones due to both involving URL-based I/O operations, despite completely different application logic. However, the functional similarity is minimal and debatable.
- 共享行为: Both use java.net.URL to establish a connection or open a stream.；Both handle IOExceptions with try-catch blocks.；Both use BufferedReader to read from an input stream.
- 行为差异: Function A sends data (POST) and reads a response; Function B only reads data.；Function A constructs a query string with encoded parameters; Function B parses space-separated tokens.；Function A outputs messages to console; Function B modifies a game board.；Function A has void return; Function B returns boolean.
- 修正建议: Incorporate data flow analysis to detect common API usage patterns.；Use graph-based models that capture the flow of data through network operations.；Fine-tune on BCB's Type-4 clones with low token overlap.

### case_id=5627 FP partial_functionality

- 方法: `readUNI` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a tab-separated file from a URL, extracts id and description, and adds them to a vector.
- B 摘要: Downloads content from a URL to a temporary file with optional authentication and progress display.
- 静态失败原因: Static BERT may have over-relied on the common pattern of opening a URL stream and reading lines, ignoring the significantly different post-processing and output. The API-level similarity (URL, openStream) caused a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the core functionality differs: one parses structured data, the other downloads to a file. Despite both reading from URLs, the high-level purpose and output are distinct.
- 共享行为: Both open a URL and read line-by-line from the input stream.
- 行为差异: A parses tab-separated fields; B writes raw lines to a file.；A adds data to an in-memory vector; B writes to a temporary file.；B implements HTTP basic authentication; A does not.；B updates a GUI label with file size; A has no GUI interaction.
- 修正建议: Use data-flow analysis to capture transformations applied to read data.；Train on more diverse positive and negative examples to reduce overemphasis on boilerplate I/O patterns.；Inject token-level or statement-level difference features.

### case_id=5628 FN partial_functionality

- 方法: `addDataFromURL` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads from a URL and appends all lines to a text buffer, handling exceptions by printing error and appending URL string.
- B 摘要: Invokes a remote method via HTTP POST with retry logic, reads and parses JSON response, returning deserialized object.
- 静态失败原因: Low token Jaccard similarity (0.156) and large structural differences led GraphCodeBERT to predict non-clone; it failed to recognize the partial functional overlap in reading from a URL and buffering lines.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have focused on the common line-reading and appending pattern, considering both as fetching data from a URL and processing line-by-line, despite major differences in purpose and complexity.
- 共享行为: Open an InputStream from a URL；Wrap in BufferedReader and read lines；Append lines to a StringBuilder
- 行为差异: Function B constructs HTTP POST with method invocation and arguments, sets entity, and executes request；Function B checks HTTP status code and throws RuntimeException if not successful；Function B deserializes JSON response to typed object；Function B implements retry logic on ConnectTimeoutException
- 修正建议: Train models to weight partial functionality patterns；Incorporate functional call graphs or hierarchical embeddings；Use data augmentation with more diverse partial clones

### case_id=5629 FP lexical_or_api_overlap

- 方法: `getUser` vs `addQDInformation`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Returns a User object by loading from DAO or parsing a config file when not found.
- B 摘要: Updates internal project information by reading a local or remote data file and parsing specific lines.
- 静态失败原因: The static method may have misclassified due to lexical overlap (both use BufferedReader, File, URL, etc.) and similar control flow (while loop reading lines), causing it to overgeneralize.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the functions have entirely different purposes and functionality; they only share a generic file-reading pattern but not the core business logic.
- 共享行为: Both read lines from a file using BufferedReader；Both parse tokens using string operations；Both have try-catch for exceptions
- 行为差异: Different input (userlogin vs. no parameter)；Different output (returns User vs. void with side effects)；Different file content format；Different purpose
- 修正建议: Better training to distinguish API usage contexts；Incorporate semantic understanding of the overall function purpose；Use more discriminative features or contrastive learning

### case_id=5630 FN partial_functionality

- 方法: `populateResources` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads template files and images from classpath resources and saves them to database.
- B 摘要: Fetches OPDS catalog entries or downloads books from HTTP URLs, handling pagination and network errors.
- 静态失败原因: Low token overlap (Jaccard 0.103) and different domain-specific terms led static BERT to assign low similarity, missing the broad functional overlap BCB accepted.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered both as 'resource loading' functions due to shared pattern of reading from URLs, despite very different endpoints and purposes.
- 共享行为: Both open URL connections and read input streams.；Both handle I/O exceptions and perform logging.
- 行为差异: A loads local resources; B connects to remote HTTP servers.；A saves data to database; B parses XML feeds and downloads files.；A is static; B is an instance method with complex state management.；B handles HTTP-specific features like redirects, timeouts, and content types.
- 修正建议: Incorporate coarse-grained functional classification (e.g., 'I/O resource loading') to detect partial similarity.；Use data flow analysis to recognize common stream-reading patterns beyond surface tokens.

### case_id=5631 FN boilerplate_overlap

- 方法: `addIDs` vs `postXml`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Queries a metabolite database by name, parses HTML to extract IDs and molecular weight, updates a row object, and returns a score.
- B 摘要: Performs an HTTP POST request with XML content and returns the response body as a string.
- 静态失败原因: Low lexical overlap (Jaccard 0.12) and different domain-specific terms; the model likely correctly captured the semantic dissimilarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have considered both as 'web service interaction' clones due to shared network I/O and response reading boilerplate, but this is a very broad interpretation.
- 共享行为: Both make an HTTP request via URL and read the response
- 行为差异: Different HTTP methods (GET vs POST)；Different input parameters and return types；Function A has complex parsing logic specific to metabolite IDs；Function A modifies an external object (row), while B has no side effects
- 修正建议: No fix needed; model prediction is likely correct. If BCB annotation is considered ground truth, then incorporate higher-level structural patterns like API call sequences.

### case_id=5632 FP boilerplate_overlap

- 方法: `actionPerformed` vs `encodeFileToFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles user actions in a settings dialog, updating UI components and saving preferences.
- B 摘要: Reads a file, base64 encodes it, and writes the result to another file.
- 静态失败原因: Static BERT models may rely on token patterns and could be misled by common Java boilerplate (e.g., try-catch, if statements) present in both, while missing high-level semantic differences due to limited context understanding.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled these as non-clones because they perform completely different tasks with no functional overlap, even under broad Type-4 criteria.
- 行为差异: A is an event-driven UI handler; B is a static utility method.；A modifies UI components; B performs file encoding.；A involves multiple conditional branches; B is linear.；A depends on external classes like Suku.kontroller and JFileChooser; B uses standard Java I/O.
- 修正建议: Use graph-based models that capture control flow and data dependencies.；Include method-level semantic features like method name and class context.；Train with contrastive learning tasks that emphasize functional similarity.

### case_id=5633 FN benchmark_preference_bias

- 方法: `fileDownload` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL and writes it to a local file named 'download.pdf'.
- B 摘要: Registers a user by encoding password, setting metadata, creating a phpBB user via URL, persisting to database, and sending confirmation email, returning success status.
- 静态失败原因: The static model likely focused on overall functionality and semantic mismatch, predicting non-clone correctly; it did not overfit to the common URL reading boilerplate.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered the common pattern of opening a URL connection, reading data, and handling exceptions as sufficient for Type-4 clone similarity, or possibly a labeling error.
- 共享行为: Both use URL and URLConnection to read data from a URL；Both have try-catch blocks with logging
- 行为差异: Function A purely downloads a file; Function B performs multiple user registration steps including password encoding, database persistence, email sending；Function A writes bytes to a file; Function B reads a line and sets forum ID；Return types differ (void vs boolean)
- 修正建议: Re-evaluate BCB annotation for this pair；If BCB label is correct, models should be trained to recognize partial functional similarity even across distinct tasks

### case_id=5634 FN partial_functionality

- 方法: `postData` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Posts data to a URL via HTTP POST, discarding the response.
- B 摘要: Reads from a URL or file stream, returning a status code.
- 静态失败原因: Static BERT models rely heavily on lexical overlap and method name similarity; here token Jaccard is low (0.098) and method names differ (postData vs read), so the model failed to capture the underlying structural similarity of URL-based I/O operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB labels these as clones likely because both are network I/O functions that open a URL, perform stream I/O, and close resources; the overall pattern is similar although the direction differs.
- 共享行为: Both interact with URLs to perform I/O operations；Both use streams (PrintStream vs BufferedInputStream) and close them；Both handle exceptions (one throws, one catches)
- 行为差异: A sends data (output), B receives data (input)；A sets HTTP request properties (Content-type, Content-length), B does not；A discards response, B processes and returns status；A uses URLConnection with doOutput/doInput, B uses openStream
- 修正建议: Enhance training data with more examples of I/O functions with different method names；Use a model that captures semantic similarity of API usage patterns；Incorporate control-flow or data-flow features that highlight similar structures

### case_id=5635 FP boilerplate_overlap

- 方法: `decodeBody` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Decodes an email body input stream based on content-transfer-encoding, copies to a temporary file, and returns the body.
- B 摘要: Handles UI action events to configure application preferences like Graphviz path, ImageMagick path, and display settings.
- 静态失败原因: The static model likely relied on superficial common patterns such as if-else chains and null checks, ignoring the domain and method names.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because these functions serve entirely different purposes (data decoding vs UI event handling) with no functional overlap even at a broad Type-4 level.
- 共享行为: Both use conditional blocks with string comparisons.
- 行为差异: Function A processes binary data streams; Function B handles UI events.；Function A returns a Body object; Function B has no return value and modifies UI state.；Function A is short and focused; Function B is long and handles multiple unrelated commands.；Function A uses I/O utilities like IOUtils.copy; Function B uses JFileChooser and Swing components.
- 修正建议: Incorporate method name and signature similarity.；Use type information (e.g., parameter and return types) to distinguish dissimilar functions.；Train on larger diverse dataset to reduce sensitivity to boilerplate patterns.

### case_id=5636 FN partial_functionality

- 方法: `addIDs` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches metabolite information from a web service and populates a PeakListRow with various IDs and molecular weight.
- B 摘要: Checks for a new version of jEdit by fetching a version file from a URL and comparing build numbers.
- 静态失败原因: The static model likely focused on lexical overlap (low Jaccard), different method names, domain-specific APIs (GCGCColumnName vs jEdit), and different return types, missing the abstract similarity of URL fetching and line parsing.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'network-based data retrieval and parsing' with similar control flow, thus a Type-4 clone based on functional similarity.
- 共享行为: Both open a URL, read lines, parse specific substrings, handle IOException, and close streams.
- 行为差异: A processes multiple lines and extracts multiple fields; B extracts only version and build.；A returns an int score; B is void and shows dialog messages.；A uses specific patterns like href="Metabolites/"; B uses line starts with ".version" etc.；A modifies a PeakListRow; B interacts with View (show/hide cursor, message dialogs).
- 修正建议: Improve model with dataflow analysis to recognize common patterns of URL connection, reading, parsing lines, exception handling.；Augment training data with more abstract clone types.

### case_id=5637 FN benchmark_preference_bias

- 方法: `fileCopy` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination with comprehensive validation and buffered I/O.
- B 摘要: Launches a NexOpen project configuration by processing Maven pom files and setting up Hibernate reverse engineering artifacts.
- 静态失败原因: The low token Jaccard (0.09) and entirely different vocabulary and APIs caused the model to correctly predict non-clone; the model lacks context to align the two dissimilar functionalities.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label may have been assigned erroneously due to a benchmark annotation error, or based on a very broad interpretation of file operation similarity despite minimal semantic overlap.
- 共享行为: Both perform file existence checks；Both use try-finally for resource cleanup
- 行为差异: Function A is a generic file copy utility; Function B is an Eclipse plugin launch handler；Function A uses java.io.FileInputStream/FileOutputStream; Function B uses Eclipse APIs and XML processing；Function A has no side effects beyond copying; Function B modifies project properties and creates files
- 修正建议: Review and correct BCB annotations for such pairs；Train models to better distinguish domain-specific tasks

### case_id=5638 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyTo`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies or adds a property in a locale-specific properties file, copying from an English file if the locale file does not exist.
- B 摘要: Recursively copies a file or directory to a destination path using FileChannel transfer.
- 静态失败原因: The static model likely relied on low token Jaccard (0.118) and structural differences, and thus predicted non-clone. It may have missed a weak semantic similarity (file copying) that BCB annotators possibly considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone due to both functions involving file copy operations (A copies an English file to a locale file if not present) and generic I/O patterns, but this is a stretch given the distinct primary purposes.
- 共享行为: Both perform file I/O operations (reading/writing files)
- 行为差异: Function A modifies properties files; Function B copies files/directories；Function A has complex string processing to update key-value pairs; Function B uses FileChannel for direct transfer；Function A conditionally copies a file only if missing; Function B always copies；Function A handles a specific resources path; Function B works with generic File objects
- 修正建议: Incorporate more high-level semantic understanding or functional summarization；Use program analysis to detect common sub-operations like file copy；Improve handling of partial functionality clones where only a segment of code is similar

### case_id=5639 FN partial_functionality

- 方法: `testCopy_inputStreamToOutputStream` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Tests copying an InputStream to an OutputStream using IOUtils.copy and verifies content equality.
- B 摘要: Downloads a resource from a URL, caches it locally by copying from network InputStream to file OutputStream, and returns a FileInputStream.
- 静态失败原因: Static BERT/GraphCodeBERT focused on low token overlap (10%) and method name/signature differences, missing the high-level behavioral similarity of stream copying, especially since one uses a library call and the other a manual loop.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone because both functions perform the core operation of reading from an InputStream and writing to an OutputStream, a specific data flow pattern that matches broad Type-4 clone criteria.
- 共享行为: Both involve copying bytes from an InputStream to an OutputStream
- 行为差异: A is a unit test with assertions, uses IOUtils.copy; B is a production method with caching, error handling, and returns an InputStream
- 修正建议: Incorporate data flow analysis to detect similar I/O patterns；Use program slicing to extract core functionality for comparison

### case_id=5640 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `getUser`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a file of integers line by line and returns a set of those integers.
- B 摘要: Looks up a user by login, and if not found, reads a configuration file to create and persist the user.
- 静态失败原因: The model likely overweighs lexical and API-level similarities (e.g., URL, InputStream, readLine, exception handling) and ignores the different input/output types and overall purpose, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB emphasizes whole-function semantic equivalence; these functions perform completely different tasks (reading zone IDs vs. user authentication), so they are not considered clones.
- 共享行为: Both read a resource file from classpath using URL and InputStream；Both read lines from the file in a loop；Both handle exceptions by printing stack trace
- 行为差异: A returns a set of integers; B returns a User object and optionally saves it；A's file contains only integers; B's file is colon-delimited with three fields；B may load from a database first before fallback to file; A does not have any database interaction；B has conditional logic to match user login; A does not have any conditional matching beyond parsing integer
- 修正建议: Enhance training to focus on semantic role of variables and output types；Incorporate dataflow analysis to distinguish different processing logic

### case_id=5641 FP boilerplate_overlap

- 方法: `readData` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Initializes data structures (sets and maps) from string tokenization and file parsing for Tibetan transliteration.
- B 摘要: Copies all files from a source directory to a destination directory using file channels.
- 静态失败原因: The model may have been misled by common Java boilerplate (e.g., try-catch for IOException, loops) and the truncated code in function A, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions are completely unrelated in purpose and implementation; there is no partial functionality overlap.
- 共享行为: Both involve reading input (strings or files) and processing
- 行为差异: Function A populates multiple sets and maps for linguistic data, while Function B copies file contents.；Function A uses StringTokenizer and file parsing, while Function B uses FileChannel and ByteBuffer.；Function A modifies static fields, while Function B is self-contained and writes to files.
- 修正建议: Improve training data to include more diverse non-clone pairs with similar boilerplate.；Use structural information like data flow graphs to distinguish different operations.；Ensure full function code is available to avoid missing critical logic.

### case_id=5642 FN partial_functionality

- 方法: `getHTML` vs `sendRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a URL, optionally writes to a file, and returns the HTML content.
- B 摘要: Sends an XML request to a servlet via HTTP with compression, parses the XML response, but returns an empty string.
- 静态失败原因: The model likely overemphasized surface-level differences in library usage (e.g., JDOM, GZIP) and control flow (file writing vs. compression), missing the high-level functional similarity of HTTP client operations. Low token overlap also contributed to the false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider them clone because both are HTTP communication methods that open a connection, read data, and handle exceptions. The broad Type-4 criteria may accept similarity in overall network communication pattern.
- 共享行为: Both open HTTP connections to URLs；Both read from input streams；Both handle exceptions；Both use URL/URLConnection classes
- 行为差异: Function A fetches HTML (GET) while B sends an XML request (POST)；Function A writes to file optionally, B does not；Function A returns the fetched HTML, B ignores the response and returns empty string；Function B uses GZIP compression and checksum, A does not
- 修正建议: Use data augmentation with more diverse Type-4 clones；Incorporate high-level functional information such as API call patterns；Train with contrastive learning that emphasizes functional similarity despite low lexical overlap

### case_id=5643 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `addRecord`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a specific message in a locale-specific properties file, creating the file if missing by copying from English.
- B 摘要: Adds a record from an input stream to a data store using content-based addressing via digest, handling collisions.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on low token overlap (Jaccard=0.137) and correctly predicted non-clone; it failed to recognize the possible broad functional similarity that BCB might have annotated.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'file manipulation' functions that process input and produce output, thus partially similar in functionality, despite different domains.
- 共享行为: Both perform file I/O operations；Both use try-catch exception handling；Both involve reading from an input stream or file and writing to a file
- 行为差异: modifyApplicationMessage modifies a properties file for localization; addRecord stores data with content-based addressing；modifyApplicationMessage searches and replaces a line; addRecord computes digest and renames a temporary file；modifyApplicationMessage creates files by copying; addRecord handles collisions and digest
- 修正建议: Better understand BCB's annotation criteria; consider including more contextual features beyond lexical overlap；Use models that capture long-range semantics or data flow

### case_id=5644 FN benchmark_preference_bias

- 方法: `simulate` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Simulates a test sequence by reading input lines, making SOAP web service calls (rateUser and obtainUserReputation), and verifying responses with JUnit assertions.
- B 摘要: Launches a NexOpen project within Eclipse IDE by configuring Maven POM files, setting Hibernate dialect, and scheduling an install action with progress monitoring.
- 静态失败原因: The static model focused on low token overlap and semantic differences, predicting non-clone. It failed to match BCB's broader criteria that may accept partial functionality similarity, possibly due to annotation inconsistency or benchmark preference bias.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions involving complex multi-step processes with external interactions and resource management, despite the distinct application domains.
- 共享行为: Both perform file input/output operations；Both use try-catch blocks for exception handling
- 行为差异: Different overall purpose (simulation vs. launch)；Different parameter signatures and return types；Use different libraries (SOAP vs. Eclipse/XML)；Control flow differs (loop vs. callback and sequential steps)
- 修正建议: Re-examine BCB annotation consistency for this pair；Train models to recognize broader clone categories including Type-3/Type-4；Incorporate domain-specific features to capture high-level process similarity

### case_id=5645 FN benchmark_preference_bias

- 方法: `doGet` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request for a page, including retrieval, permission checks, logging, and caching of page output.
- B 摘要: Recursively copies files or directories, skipping .svn directories and files with identical modification times.
- 静态失败原因: The static BERT model likely predicted non-clone due to very low token overlap (0.0876) and clear syntactic and semantic differences. It correctly identified them as non-clones.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both methods performing I/O operations and involving file creation, but the overall functionality is completely different. Possibly an annotation error.
- 行为差异: Function A is an HTTP request handler; Function B is a file copy utility.；Function A involves web logic (session, permissions, caching); Function B is purely file I/O.；Function A uses many external services (Property, Page, PortalRequest); Function B only uses java.io.
- 修正建议: Investigate whether the BCB annotation is correct; if it is an error, correct the benchmark.；If BCB intended a broad Type-4 clone, ensure the model captures abstract I/O patterns, but this seems unlikely.

### case_id=5646 FP boilerplate_overlap

- 方法: `sendPost` vs `import_hints`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Reads a file or URL to import hint pieces for a puzzle board, returning success status.
- 静态失败原因: Static BERT models like GraphCodeBERT may focus on lexical and syntactic patterns, overemphasizing shared boilerplate (URL, BufferedReader, try-catch) while missing the crucial semantic differences in data flow and external API usage. The model likely assigned high similarity due to common Java I/O idioms.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have entirely different purposes and logic, despite some superficial I/O API overlap. The token Jaccard similarity is low, and the functional behavior is unrelated.
- 共享行为: Both perform I/O operations using URL and BufferedReader.；Both use try-catch blocks to handle exceptions.；Both involve reading input from a stream.
- 行为差异: Function A writes data (param) to the server via POST, while Function B only reads data.；Function A returns the server response as a String; Function B returns a boolean and processes data into board pieces.；Function A uses HttpURLConnection for HTTP; Function B uses URL.openStream for generic URL/file reading.；Function A sets request properties (e.g., Accept-Language); Function B does not.
- 修正建议: Incorporate more training examples where similar boilerplate code has different semantics to reduce false positives.；Use data-flow or control-flow analysis to distinguish variable usage and method calls beyond surface-level tokens.；Add attention to method names and parameter types to capture domain-specific intent.；Employ contrastive learning to separate functions with high lexical but low semantic similarity.

### case_id=5647 FN benchmark_preference_bias

- 方法: `loadBinaryStream` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a binary stream from an InputStream and writes it to an HTTP response output stream, with content type and disposition headers.
- B 摘要: Builds a website for editing by reading multiple files, applying XSLT transformations, and writing output to files, involving complex DOM and file system operations.
- 静态失败原因: The static BERT model correctly identified the lack of semantic overlap based on low lexical similarity and different control flows. However, it failed to match the BCB label because it did not capture the broad 'I/O utility' category that BCB annotators might have considered, possibly due to not being trained on such loose Type-4 annotations.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: None
- 共享行为: Both perform I/O operations involving reading input and writing output；Both handle exceptions and close streams；Both operate in the context of a web application
- 行为差异: Function A is a simple stream copy with HTTP response, while B is a complex multi-step site generation；B involves DOM parsing, XSLT, multiple file reads/writes, FTP, and string manipulation；A has no file system or transformation logic
- 修正建议: Increase robustness to BCB-style loose annotations by incorporating task-level or domain-level features；Use contrastive learning to distinguish between truly different functionalities despite superficial I/O similarities；Incorporate data flow analysis to highlight the different endpoints (HTTP response vs file system)

### case_id=5648 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint, and returns the file path.
- B 摘要: Copies a file from source to destination with user confirmation and progress display.
- 静态失败原因: Static BERT likely relied on lexical overlap (e.g., file I/O, try-catch) and missed the distinct high-level semantics: downloading and modifying WSDL vs. local file copy.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered them clones due to both performing file transfer operations and sharing similar error handling and file I/O patterns, though the core tasks are different.
- 共享行为: Both use file input/output streams.；Both check file existence.；Both handle exceptions with try-catch.
- 行为差异: Function A downloads a remote file; Function B copies a local file.；Function A modifies XML content; Function B does not.；Function A returns a file path; Function B is void.；Function B prompts user for overwrite permission; Function A does not.
- 修正建议: Incorporate task-level understanding (e.g., download vs. copy).；Use structural differencing that captures distinct operations (XML modification, user prompts).；Improve training data to distinguish similar-looking but functionally different code.

### case_id=5649 FN benchmark_preference_bias

- 方法: `testAddLinkToImage` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: A test method that copies image files to a report folder and adds links to them in the report.
- B 摘要: A launch method for a NexOpen project that validates project structure, handles XML profiles, and copies reverse engineering files.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone because the token Jaccard is very low (0.042) and the overall control flow, API usage beyond IOUtils.copy, and domain context are vastly different, indicating no semantic equivalence.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled this as a clone due to a lenient interpretation of Type-4 (semantic) clones, focusing on the shared low-level pattern of copying files with IOUtils.copy. Alternatively, it could be a benchmark annotation error.
- 共享行为: Both use IOUtils.copy to copy files from an input stream to a file output stream.；Both involve file I/O operations.
- 行为差异: Function A is a unit test for adding links to image files in a test report; Function B is a production launch configuration handler for an Eclipse plugin.；Function A copies static image resources from classpath; Function B copies dynamically generated reverse engineering files based on configuration.；Function A adds links to the report; Function B modifies project persistent properties and triggers build actions.；The domains, intent, and control flow are entirely different.
- 修正建议: Re-annotate this pair as non-clone in the benchmark to match strict functional equivalence.；If retaining as clone for Type-4, clarify criteria that such superficial I/O similarity is considered clone.；Improve model training with more discriminative features to ignore low-level I/O patterns when high-level semantics differ.

### case_id=5650 FN lexical_or_api_overlap

- 方法: `fileDownload` vs `GetResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL and saves it to a local directory.
- B 摘要: Sends an HTTP GET request and returns the response content as a string.
- 静态失败原因: Static models like GraphCodeBERT rely on token and structural similarity; low token Jaccard and different API usage (URLConnection vs HttpURLConnection, file output vs string return) likely pushed embeddings apart. The model failed to recognize the shared control flow pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label these as clones because both functions perform the high-level task of fetching data from a URL, despite differences in I/O specifics. The broad Type-3/Type-4 clone definition can include such partial functionality similarity.
- 共享行为: Open a URL connection；Read input data from the connection；Handle exceptions with try-catch
- 行为差异: A writes to a file, B returns a string；A uses URLConnection, B uses HttpURLConnection；A reads raw bytes, B reads lines；A catches generic Exception, B catches MalformedURLException and IOException
- 修正建议: Use API-level abstraction or control flow graphs to capture high-level patterns；Incorporate semantic role labeling for I/O operations；Augment training with more diverse Type-4 clones

### case_id=5651 FN partial_functionality

- 方法: `readGeoParserResult` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A function that sends an XML-based GET request to a geo-parser service, parses the response XML, and returns a collection of tuples.
- B 摘要: A function that sends an HTTP POST request with form parameters, reads the response, and returns the response string or null on error.
- 静态失败原因: Static BERT/GraphCodeBERT relies heavily on token overlap and local patterns; the low Jaccard similarity (0.132) and different API usage (XML vs HttpClient) caused it to miss the shared network request behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators likely considered these as Type-4 clones because both functions involve making an HTTP request and reading the response, which is a high-level functional similarity despite low token overlap.
- 共享行为: Both perform an HTTP request to a remote service.；Both read the response line by line using BufferedReader.；Both build a StringBuffer from the response lines.；Both return a result derived from the response.
- 行为差异: Function A uses GET request with XML payload; function B uses POST with form parameters.；Function A parses XML response; function B returns raw string.；Function A has retry logic and a testing mode; function B does not.；Function A returns a collection of tuples; function B returns a string or null.
- 修正建议: Use a code representation that captures high-level control flow and data flow, such as graph neural networks or program dependence graphs.；Incorporate knowledge of common API patterns for HTTP requests to recognize functional similarity.；Train on more diverse examples of partial functional similarity.

### case_id=5652 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by updating or adding a key-value pair.
- B 摘要: Downloads all files from a Hadoop filesystem directory to a local output file.
- 静态失败原因: Static BERT models may rely on token-level overlap and method name, which are low here. The low Jaccard similarity and different method names likely led to correct prediction of non-clone, but BCB's label contradicts this.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled this as a clone due to broad Type-4 criteria, considering both as 'file I/O utility methods' that read and write files, despite different specific purposes.
- 共享行为: Both read from an input source (filesystem or classpath) and write to an output file.；Both handle exceptions with try-catch or throws.；Both use Java I/O streams (InputStream, OutputStream, FileReader, FileWriter).
- 行为差异: A parses and modifies properties file content; B copies raw file content without modification.；A deals with locale-specific files and may copy a default file if missing; B handles Hadoop FileSystem directory listing.；A writes to a specific file determined by locale; B writes all files into a single output stream.；A uses BufferedReader line-by-line processing; B uses IOUtils.copyBytes for binary copy.
- 修正建议: Incorporate structural or dataflow analysis to distinguish file modification from file copying.；Use fine-grained understanding of string manipulation vs. raw byte copy.；Adjust clone detection thresholds to avoid over-generalizing file I/O operations.

### case_id=5653 FN benchmark_preference_bias

- 方法: `doTransfer` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Forward an HTTP request to another URL, copying headers and request body, and returning the response.
- B 摘要: Invoke a remote service method via HTTP POST, serializing arguments as JSON and deserializing the response, with retry on timeout.
- 静态失败原因: Static BERT likely failed due to low lexical overlap and different code structure, missing the high-level similarity that BCB annotators considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have considered both as HTTP client operations with stream handling, thus labeling as clone under broad functional similarity.
- 共享行为: Both make an HTTP request and process the response
- 行为差异: Different purpose: proxy vs. RPC invocation；Different HTTP methods: any vs. POST；Different data formats: raw vs. JSON；Different error handling: no retry vs. retry logic
- 修正建议: Train models with task-specific annotations that align with BCB's broad criteria；Incorporate functional semantics beyond lexical matching

### case_id=5654 FP boilerplate_overlap

- 方法: `readZoneIDs` vs `get`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads zone IDs from a resource file and returns them as a set of integers.
- B 摘要: Fetches game records from a web service via HTTP GET and returns them as an array.
- 静态失败原因: The model likely overfocused on common Java I/O boilerplate (BufferedReader, readLine, try-catch) and variable names like 'line' and 'url', leading to a false positive despite low token Jaccard.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB correctly labels these as non-clones because the functionality is entirely different (one reads local zone IDs, the other fetches game records via HTTP). Only superficial boilerplate patterns are shared.
- 共享行为: Both open a stream and read lines in a loop；Both use try-catch blocks for exception handling；Both utilize BufferedReader and InputStreamReader
- 行为差异: Function A reads from a local resource file; function B makes an HTTP GET request；Function A parses integers; function B decodes GameRecord objects；Function A returns a HashSet<Integer>; function B returns a GameRecord[] or null；Function B has multiple HTTP headers and conditional logic on response code
- 修正建议: Train on more diverse examples that differentiate domain logic from structural boilerplate；Incorporate dataflow or type analysis to capture semantic differences；Add negative sampling of pairs with high boilerplate overlap but different functionality

### case_id=5655 FP boilerplate_overlap

- 方法: `main` vs `saveProject`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Main method that reads a Prolog file, generates adapter classes, and writes them to a JAR file.
- B 摘要: Method that saves a project with types, images, trajectories, and other data into files and a zip archive.
- 静态失败原因: The model likely overfitted on boilerplate patterns like file manipulation, IOException handling, and use of File class, leading to false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because functions have no semantic similarity; one is a main entry point for a code generator, the other is a project save operation.
- 共享行为: Both perform file I/O；Both use File, FileInputStream, FileOutputStream；Both handle IOException
- 行为差异: Completely different purpose: adapter generation vs project saving；Different return types: void vs boolean；Different parameters and logic；Different external library dependencies
- 修正建议: Improve training data diversity to reduce boilerplate false positives；Add negative examples with similar I/O patterns but different semantics；Use better representation of control flow and data dependencies

### case_id=5656 FN benchmark_preference_bias

- 方法: `readAndRewrite` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: reads a DICOM file and rewrites it to another file.
- B 摘要: configures and launches a NexOpen project based on Maven pom.xml files.
- 静态失败原因: The static model correctly predicted non-clone due to very low lexical overlap (Jaccard=0.0317) and distinct API usage, but BCB's broader definition may still accept them as similar.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as file-processing utilities that involve reading and writing, leading to a broad Type-4 similarity based on high-level behavior (file I/O with error handling).
- 共享行为: both perform file I/O operations；both handle exceptions
- 行为差异: completely different domains (medical imaging vs. Eclipse project configuration)；different data formats and processing logic；different control flow and API usage
- 修正建议: re-annotate this pair as non-clone in BCB if strict semantics are desired；increase model sensitivity to domain-specific API patterns

### case_id=5657 FP lexical_or_api_overlap

- 方法: `encodePassword` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Encodes a password using SHA-1 hashing and Base64 encoding, returning the encoded string.
- B 摘要: Processes an HTTP request to classify a concept, handling session, form parameters, and XML communication with a remote server, returning an ActionForward.
- 静态失败原因: The model likely focused on superficial lexical similarities like 'Message*' classes (MessageDigest vs MessageResources) or 'encode*' method names, while missing the vast structural and semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have entirely different purposes, even if both involve encoding or exception handling; the functionality is disjoint.
- 共享行为: Both use try-catch blocks for exception handling；Both perform some form of data transformation/encoding
- 行为差异: Function A is a simple one-purpose password encoding; Function B is a complex web action with session management, XML parsing, and HTTP communication；Function A uses SHA-1 and Base64; Function B uses URL encoding and XML；Function A returns a string; Function B returns an ActionForward object
- 修正建议: Improve model's ability to distinguish similar API usage in different contexts；Add more training data with diverse method signatures and long-range dependencies；Incorporate structural similarity measures that account for method length and control flow complexity

### case_id=5658 FP partial_functionality

- 方法: `getJSONData` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches a JSON object from a URL using Apache HttpClient and parses the full response content.
- B 摘要: Fetches the first line of text content from a URL using HttpURLConnection and returns it as a string.
- 静态失败原因: Static models like GraphCodeBERT may over-rely on lexical overlaps (e.g., URL, BufferedReader, reader, line) and similar structural patterns (try-catch, while loop in A vs simple read in B). They fail to capture the semantic difference of JSON parsing versus plain text extraction, treating them as similar due to boilerplate HTTP GET code.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically requires strong functional equivalence (exact or near-exact signature and behavior). The return type difference (JSONObject vs String) and different output processing (full JSON parsing vs single line retrieval) make these distinct functionalities, so BCB labels them as non-clones.
- 共享行为: Both perform HTTP GET requests to a given URL.；Both use BufferedReader and InputStreamReader to read the response stream.；Both handle network I/O and return a value (or null).
- 行为差异: Function A uses Apache HttpClient (DefaultHttpClient, HttpGet), while B uses java.net.HttpURLConnection.；Function A parses the entire response into a JSONObject using JSONTokener; B reads only the first line and returns it as a raw String.；Function A catches broad Exception and returns null on failure; B throws Exception to the caller.；Function A builds a URI from the URL string; B directly uses the URL string.
- 修正建议: Train with more examples that distinguish between data retrieval and data transformation/parsing.；Incorporate data flow analysis to track how the response content is processed (e.g., whether it undergoes parsing).；Add features that capture the return type and surrounding context (e.g., JSONTokener usage vs simple string return).

### case_id=5659 FP lexical_or_api_overlap

- 方法: `sendPost` vs `sendRequest`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: sendPost sends a simple HTTP POST request with a string parameter and returns the response body as a string.
- B 摘要: sendRequest sends an XML request to a servlet with compression, parses XML response using JDOM, and returns an empty string.
- 静态失败原因: The model likely over-relied on lexical and API-level overlap (HttpURLConnection, setDoOutput, stream reading) and the common boilerplate of HTTP calls, ignoring the significant semantic and structural differences in URL construction, data handling, and return values.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clones because the functions serve different purposes (generic POST vs. compressed XML servlet request), have different inputs/outputs, and contain distinct logic blocks (setup, compression) that outweigh the superficial HTTP communication similarity.
- 共享行为: Both open HTTP connections with DoOutput set to true；Both write data to the output stream and read response from input stream；Both use try-catch for exception handling
- 行为差异: sendPost uses HttpURLConnection directly; sendRequest uses URLConnection with GZIP compression；sendPost returns the response body; sendRequest returns an empty string；sendRequest includes extensive server URL configuration logic (preferences, applet, dialog)；sendRequest parses XML response with SAXBuilder; sendPost reads raw text
- 修正建议: Train with a dataset that includes more varied HTTP function examples to learn beyond boilerplate similarity；Incorporate data-flow or control-flow features to differentiate simple POST from complex request construction；Use a model that can capture long-range dependencies to distinguish setup code from core request logic

### case_id=5660 FN benchmark_preference_bias

- 方法: `main` vs `copyJar`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to local files.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: Static model correctly predicted non-clone; it did not fail. The BCB label is likely a false positive.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may overgeneralize file I/O operations as clones, despite different purposes and logic.
- 共享行为: Both perform file I/O operations；Both use Java I/O classes (InputStream, OutputStream, Channel)
- 行为差异: A reads from a URL, B reads from a local file；A extracts zip entries (ZipInputStream), B copies raw bytes (FileChannel)；A writes multiple output files (one per entry), B writes a single output file；A has no error handling, B has try-catch-finally and logging
- 修正建议: Refine BCB annotation guidelines to avoid labeling different file I/O operations as clones；Use semantic similarity thresholds to filter out such pairs

### case_id=5661 FP lexical_or_api_overlap

- 方法: `readData` vs `parseContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Initializes multiple sets and maps by tokenizing comma-separated strings from predefined fields.
- B 摘要: Parses HTML content from a stream, extracts metadata, links, and body text.
- 静态失败原因: Static BERT models likely focused on surface-level token overlap (e.g., StringTokenizer, HashSet) and common Java syntax, missing the vast semantic gap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB non-clone because functions are semantically unrelated; one is a one-time initialization, the other is a complex HTML parser.
- 共享行为: No shared behavior
- 行为差异: Different purpose: data initialization vs. HTML parsing；Different inputs: static fields vs. stream and URL；Different outputs: populated data structures vs. indexed document fields
- 修正建议: Use data-flow and control-flow graphs to capture true logic；Incorporate type and method signature information；Train with more diverse negative samples that share tokens but differ in semantics

### case_id=5662 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `getNetworkServersIPs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter timeline JSON from a fixed URL and returns the raw response as a string.
- B 摘要: Parses a server list from a given URL, extracting IP addresses into a vector.
- 静态失败原因: Static BERT/GraphCodeBERT may over-rely on common tokens and structural patterns (BufferedReader, readLine, exception handling) and miss the semantic divergence in output type and parsing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the structural similarity (URL reading line by line) is superficial, and the functionality and output are entirely different. BCB prefers semantic equivalence or clear partial functionality; here the resemblance is only boilerplate.
- 共享行为: Both perform HTTP GET requests and read the response line by line.；Both handle IOException similarly with stack traces.
- 行为差异: A returns a single string, B returns a vector of strings.；A uses a hardcoded URL, B uses a parameter.；A uses HttpClient, B uses URLConnection.；A has no parsing logic, B has stateful parsing to extract IPs.
- 修正建议: Incorporate data-flow analysis to track how input is transformed into output.；Train with contrastive examples that share API calls but differ in business logic.；Use type information to distinguish return types.

### case_id=5663 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft server handshake by validating username and joining server via HTTP request.
- B 摘要: Performs Google image search by fetching HTML, extracting image URLs, and updating a UI.
- 静态失败原因: Static BERT likely overemphasized lexical overlap in URL opening and stream reading patterns, ignoring the distinct domain contexts.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels by functional similarity; these functions accomplish entirely different tasks despite sharing boilerplate HTTP code.
- 共享行为: Both open HTTP connections and read data from streams.；Both perform string parsing and validation.；Both handle exceptions with try-catch blocks.
- 行为差异: Completely different domains: Minecraft networking vs. Google image search.；Different input/output: one processes a handshake packet, the other takes a search query and updates UI.；Different control flow and logic: one validates server keys, the other parses HTML for image URLs.
- 修正建议: Incorporate dataflow analysis to distinguish different I/O and state transformations.；Use contrastive learning to separate functions from different domains.；Add context-aware training that considers method names and surrounding code.

### case_id=5664 FN benchmark_preference_bias

- 方法: `getFile` vs `parseContent`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint location, and returns the file path.
- B 摘要: Parses HTML content from a stream, extracts metadata, links, body text, and detects language.
- 静态失败原因: The static model correctly predicted non-clone due to extremely low token overlap and different API patterns. It 'failed' only relative to the benchmark label, which is likely incorrect here.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to broad Type-4 criteria, perhaps considering both as 'downloading and processing web content', but the specific tasks are unrelated; likely a labeling error in the benchmark.
- 共享行为: Both use input streams and file I/O；Both handle exceptions；Both perform logging
- 行为差异: A downloads and modifies a WSDL file; B parses HTML content；A manipulates XML nodes; B processes HTML nodes；A returns a file path; B adds fields to a document；A uses URLConnection and FileChannel; B uses IOUtils and StringWriter
- 修正建议: Re-evaluate the alignment of benchmark labels with clone definitions；Increase token overlap threshold or use semantic similarity embeddings

### case_id=5665 FP lexical_or_api_overlap

- 方法: `run` vs `parse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Loads a vector tile from a URL or file and adds it to a data source's layer.
- B 摘要: Parses a dataset from a file or URL using a configurable delimiter and returns a DataSet object.
- 静态失败原因: Static BERT/GraphCodeBERT models may rely on keyword overlap (URL, BufferedReader, InputStream, IOException, etc.) and ignore the structural and semantic differences, leading to false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates based on functional equivalence; these functions have entirely different purposes (tile loading vs dataset parsing) and only share trivial I/O patterns, so BCB labels non-clone.
- 共享行为: Reads data from a URL or file using BufferedReader and InputStreamReader；Handles IOException and FileNotFoundException
- 行为差异: Function A creates a VectorTile and adds geometries to a data source; Function B parses tabular data with headers and returns a DataSet；Function A uses a synchronous lock on lauchedHTTPRequests; Function B does not；Function A has a simpler parsing (reads lines); Function B uses StreamTokenizer with complex tokenization rules
- 修正建议: Increase training data diversity to reduce reliance on API tokens；Incorporate dataflow or program dependence analysis to capture long-range semantics；Use contrastive learning with hard negatives that share I/O patterns but different logic

### case_id=5666 FP boilerplate_overlap

- 方法: `getUser` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from a DAO, falling back to parsing a config file to create and save the user if not found.
- B 摘要: Reads lines from a URL, parses them into version, url, and information, handles errors, and notifies listeners.
- 静态失败原因: Static BERT models often overemphasize overlapping API sequences (BufferedReader, InputStreamReader, URL, openStream, readLine) and structural patterns, ignoring high-level goal differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the overall functionality differs: user lookup vs URL download. The shared I/O boilerplate does not imply semantic equivalence.
- 共享行为: Both use BufferedReader to read lines from an InputStream；Both use a while loop to iterate over lines；Both use try-catch for exception handling
- 行为差异: Function A is for user authentication; B is for downloading and parsing URL content；A uses StringTokenizer for parsing, B uses a switch on line index；A returns a User object; B sets instance variables and calls listeners；A saves user to DAO; B has no such persistence
- 修正建议: Incorporate control flow and data dependency analysis to distinguish I/O patterns from core logic；Use functional summarization or comment-aware embeddings；Add a post-processing filter to penalize pairs with high boilerplate but different data flows

### case_id=5667 FP other

- 方法: `encrypt` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.99`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Encrypts a plaintext string using SHA-1 hash and Base64 encoding.
- B 摘要: Handles a Struts action request for concept classification, including form processing and HTTP communication.
- 静态失败原因: The model likely predicted as clone due to some lexical overlap (e.g., 'MessageDigest', 'catch', 'throw') or because both are static methods with similar boilerplate, but the semantic mismatch is vast.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels this as non-clone because the two functions have completely different purposes and structures, despite both being Java methods.
- 共享行为: Both use try-catch blocks for exception handling.；Both involve string manipulation and network-related code (though different purposes).
- 行为差异: Function A is a simple utility performing cryptographic hashing; Function B is a complex web request handler.；Function A has no branching or state management; Function B has multiple conditionals, session management, and forward logic.；Function A uses MessageDigest and Base64; Function B uses HttpSession, ActionMapping, and XML/HTTP utilities.；Function B is orders of magnitude larger and incorporates external IO and parsing.
- 修正建议: Improve model's ability to capture program semantics beyond token overlap.；Incorporate data flow and control flow features to distinguish simple utilities from complex handlers.；Use larger context or hierarchy information to recognize different domains.

### case_id=5668 FN partial_functionality

- 方法: `getHTML` vs `handledRun`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a given URL and optionally writes the content to a local file.
- B 摘要: Downloads an XML game data file from a fixed URL, checks version, and updates the local file if newer.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap and structural similarity; low Jaccard similarity (0.201) and different method names, variable names, and control flow (version check) caused the model to miss the high-level common pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators consider both as 'downloading a file from URL and saving locally', a common functionality pattern, thus a Type-3/4 clone despite differences in details.
- 共享行为: Both open a URL connection and read data using BufferedReader.；Both write data to a file using BufferedWriter/FileOutputStream.；Both handle exceptions with try-catch-finally blocks and close resources.
- 行为差异: Function A writes to file only if a directory path is provided; Function B always writes conditionally based on version comparison.；Function A uses a parameterized URL; Function B uses a fixed URL and parses headers for version.；Function B has version checking and more complex error handling (dialog, logging); Function A prints stack trace.
- 修正建议: Incorporate data flow analysis to recognize common IO patterns like 'read from URL, write to file'.；Use program similarity based on functional purpose rather than syntactic overlap.；Train on clone benchmarks that include partial functionality clones (Type-3/4).

### case_id=5669 FN benchmark_preference_bias

- 方法: `login` vs `setMembers`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Logs in to LOLA by sending email and password via HTTP POST, extracts session ID, and returns it.
- B 摘要: Fetches a ticket creation page via HTTP GET and parses HTML to populate component and priority arrays.
- 静态失败原因: Static BERT/GraphCodeBERT likely captured the semantic difference in purpose and correctly predicted non-clone, so it did not fail; BCB label may be a false positive.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have considered both functions as involving HTTP communication and string processing, possibly viewing them as broad Type-4 clones due to similar high-level functionality (web scraping) despite different specific tasks.
- 共享行为: Both make HTTP connections and read from InputStream/Reader.；Both use try-catch blocks and print error messages.；Both involve URL construction and network I/O.
- 行为差异: A performs authentication (POST with credentials), B performs data extraction (GET and HTML parsing).；A returns a session ID, B sets static fields with component/priority options.；A uses URLEncoder and OutputStreamWriter, B uses BufferedReader and regex pattern matching.；Different URLs and parameter handling.
- 修正建议: Increase token similarity threshold to avoid considering loose Type-4 pairs.；Incorporate task-specific semantic roles (e.g., authentication vs. parsing) to reduce false positives.；Use a more fine-grained clone type definition that requires functional equivalence at the method level.

### case_id=5670 FP boilerplate_overlap

- 方法: `getMD5` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes the MD5 digest of a password string and returns its hexadecimal representation.
- B 摘要: Handles a web request to classify a concept, involving session management, XML encoding, HTTP POST, and response parsing.
- 静态失败原因: The static BERT model may have been misled by superficial similarities like try-catch blocks and method signatures, failing to capture the entirely different semantics and long-range data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions perform completely different tasks with no overlapping functionality, even under broad similarity criteria.
- 共享行为: Both contain try-catch blocks for exception handling.；Both return a value (String or ActionForward).
- 行为差异: Function A computes a cryptographic hash; Function B executes complex business logic including HTTP communication.；Function A is stateless and accepts a single string; Function B is stateful and interacts with session and request objects.；Function A is short (< 10 lines); Function B is long (> 100 lines) with many operations.；Function A uses MessageDigest and byte conversion; Function B uses URL connection, XML parsing, and JSP forwarding.
- 修正建议: Use training data with more diverse exception handling patterns to avoid overfitting to try-catch blocks.；Enhance the model with dataflow or dependency analysis to distinguish pure data transformation from control-heavy business logic.；Incorporate identifier names and API calls more heavily to differentiate domains.

### case_id=5671 FP other

- 方法: `perform` vs `MD5`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles a web request to classify a biomedical concept by sending XML to a remote service and parsing the result.
- B 摘要: Computes the MD5 hash of a given string and returns the hexadecimal representation.
- 静态失败原因: The low token Jaccard (0.047) suggests that the static model may have been misled by some coincidental structural patterns or by the presence of common programming constructs (e.g., return statements, string handling). However, given the extreme dissimilarity, this appears to be a clear false positive likely due to limitations in the model's ability to capture overall semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels these as non-clones because they perform entirely different tasks: one is a Struts action for classification, the other is a utility for MD5 hashing. There is no semantic similarity even at a broad level.
- 共享行为: Both are Java methods that return a value.；Both contain string manipulation and conversion.
- 行为差异: Function A performs complex web request handling, session management, and XML parsing.；Function B is a simple one-purpose cryptographic hash function.；Function A has multiple conditional branches and error handling; Function B is linear.；Function A involves I/O operations and external service calls; Function B is pure computation.
- 修正建议: Enhance training data with more diverse non-clone examples.；Improve negative sampling to avoid spurious similarities.；Incorporate task-specific features such as method signatures and imports to disambiguate.

### case_id=5672 FP boilerplate_overlap

- 方法: `logging` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Logs inbound message content, handling encoding, headers, and payload with truncation and temporary file support.
- B 摘要: Main method that generates adapter classes from Prolog files, parsing input, and assembling JAR resources.
- 静态失败原因: Static BERT may have been misled by common structural patterns like try-catch blocks and use of InputStream/OutputStream, or by generic API usage (File, IOException) that are prevalent across Java programs, but the methods have negligible lexical overlap and clearly distinct semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions perform entirely different tasks with no shared functionality or common goal.
- 行为差异: Different purpose: logging vs. code generation.；Different I/O: reading/writing message streams vs. file and JAR manipulation.；Different control flow and exception handling.；Function A is part of a web service interceptor; Function B is a command-line tool main method.
- 修正建议: Enhance model with semantic role labeling or intent detection.；Use contrastive learning with hard negative examples.；Incorporate class-level context or package information.

### case_id=5673 FN partial_functionality

- 方法: `getFile` vs `copyLogic`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint in the XML, and saves it to a temporary file, returning the file path.
- B 摘要: Copies a class file from a source path to a destination path using FileChannel, with state management.
- 静态失败原因: Static BERT models rely heavily on token-level overlap and may miss the structural similarity of the FileChannel pattern. The low token Jaccard (0.11) and different domain-specific terms (WSDL vs class file) likely caused the model to predict non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as clones due to the common file copy pattern using FileChannel, which is a distinct functional behavior. The broad Type-3/Type-4 criteria often accept such partial functionality similarity, where the core I/O operation is structurally identical despite different contexts.
- 共享行为: Use of FileChannel for transferring data between input and output streams；Exception handling for IOException；Use of FileInputStream and FileOutputStream or similar
- 行为差异: getFile downloads from a URL, while copyLogic copies from a local file system；getFile modifies XML content, copyLogic does not modify data；getFile returns a String, copyLogic returns void；getFile has logging via mLog, copyLogic uses printStackTrace
- 修正建议: Enhance model with structural information like AST or dataflow graphs to capture common patterns；Use contrastive learning to align partial functionality sequences；Incorporate domain-agnostic I/O operation detectors

### case_id=5674 FN partial_functionality

- 方法: `getResourceAsStream` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource from a URL, caches it locally, and returns an InputStream.
- B 摘要: Copies all files from a source directory to a destination directory using NIO channels.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on low token overlap and surface-level differences in method names and structure, classifying as non-clone. The model may have missed the high-level functional similarity in data transfer operations due to lack of context about the shared I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone because both functions perform data transfer from a source to a destination using I/O streams, which is a common pattern in Type-4 clones (functionally similar even if not equivalent). The presence of file I/O and the general structure of reading and writing data might be considered a clone by BCB's broad criteria.
- 共享行为: Both perform file I/O involving reading and writing bytes；Both handle exceptions (though differently)；Both involve streams/channels for data transfer
- 行为差异: Method A downloads from remote URL, Method B copies local files；Method A implements caching logic, Method B does not；Method A handles HTTP connections, Method B does not；Method A returns an InputStream, Method B returns void
- 修正建议: Incorporate structural pattern matching for common I/O operations；Use data-flow analysis to detect similar read-write patterns；Train on more diverse Type-4 clones to recognize partial functionality

### case_id=5675 FP lexical_or_api_overlap

- 方法: `main` vs `_checkLanguagesFiles`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses command line arguments, reads a Prolog file, generates adapter JAR with compiled classes and resources.
- B 摘要: For each language in a list, ensures existence of properties and temporary files, copying content if needed.
- 静态失败原因: Static BERT/GraphCodeBERT likely overfocused on common API sequences (File, FileInputStream, try-catch) and missed the larger context differences. The model may not capture deep semantics of purpose (generation vs. check/copy).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because token Jaccard is very low, and the functionalities are entirely different despite some lexical overlap in file handling.
- 共享行为: Both use File and FileInputStream/FileOutputStream；Both handle IOException；Both have try-catch blocks；Both involve file system operations
- 行为差异: Function A generates a JAR file with complex adapter generation logic；Function B only copies files based on language IDs；Function A processes command-line arguments, Function B processes portlet request attributes；Function A has output (JAR), Function B has side-effect of file creation/copy
- 修正建议: Include control flow and data flow features explicitly；Use AST-based features to capture structural differences；Add more training data with similar API usage but different intent；Consider task-specific embeddings that distinguish high-level purpose

### case_id=5676 FP lexical_or_api_overlap

- 方法: `copyFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file from source to destination using a buffer.
- B 摘要: Handles various action commands in a GUI preferences dialog, including file choosers, scaling, date format, and look-and-feel settings.
- 静态失败原因: Despite low token overlap, the static model may have falsely flagged due to presence of 'File', 'InputStream', 'OutputStream' in A and 'JFileChooser', 'File' in B, or due to model overfitting on common I/O patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators would see no meaningful code clone under any type; the functions differ entirely in purpose and structure.
- 共享行为: Both involve file operations (reading/writing files in A, selecting files in B).
- 行为差异: Function A is a straightforward file copy utility.；Function B is a large event handler with multiple conditional branches for different UI settings.
- 修正建议: Train with more diverse negative pairs that have low token overlap.；Incorporate structural or dataflow information to distinguish file copying from UI event handling.

### case_id=5677 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyResourceToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a locale-specific properties file, modifies or adds a message, and writes it back, copying the English file if the locale file does not exist.
- B 摘要: Copies a resource file to a destination file using IOUtils, handling stream closing in a finally block.
- 静态失败原因: The low token Jaccard (0.125) and different high-level semantics (property modification vs. file copy) likely caused the static model to miss the underlying I/O pattern, especially since the shared sub-task is embedded within a larger function and uses different APIs.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider that both functions encapsulate the common pattern of reading a file and writing to another file, which is a shared low-level behavior. Additionally, function A includes a file copy sub-task that closely resembles the entire function B. Thus, under BCB's broad type-3 criteria, they could be considered clones due to this partial functionality overlap.
- 共享行为: Both operations involve reading from an input source and writing to an output file.；Both handle file stream closing to release resources.
- 行为差异: Function A modifies properties content, while Function B performs a direct binary copy.；Function A conditionally copies the English file as a prelude to modification, whereas Function B always copies the given resource.；Function A uses custom reading/writing with FileReader/FileWriter and string manipulation, while Function B uses IOUtils.copyStream.
- 修正建议: Incorporate dataflow analysis to detect composed sub-tasks.；Use hierarchical embedding techniques to capture shared low-level operations despite different high-level purposes.；Consider sub-graph matching to identify partial functional clones.

### case_id=5678 FN partial_functionality

- 方法: `readData` vs `import_hints`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads multiple comma-separated token strings and a file to populate sets and maps for Tibetan transliteration data.
- B 摘要: Reads a file of space-separated integers to place hint pieces on a puzzle board.
- 静态失败原因: Static BERT models rely heavily on token-level embeddings and are sensitive to lexical overlap. With a Jaccard similarity of 0.11, the model likely focused on the different domain-specific vocabulary (Tibetan vs. puzzle) and missed the common structural pattern of file reading and tokenization. The model lacks awareness of higher-level algorithmic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels broad Type-3/4 clones as clones, especially when both functions perform similar data import patterns (open file, read line, tokenize, parse, store into structures). Despite different domains, the algorithmic skeleton is comparable, making it a typical broad clone in BigCloneBench.
- 共享行为: Both use StringTokenizer to parse delimited input strings/lines.；Both read from a file (or static strings in A) to populate internal data structures.；Both involve error handling with IOException (explicit in B, implicit in A).；Both perform initialization of sets/maps or board state.
- 行为差异: A populates multiple domain-specific sets (topSet, vowelSet, tibSet, etc.) and a map; B places pieces on a board.；A is static void; B is instance method returning boolean.；A has complex error handling with multiple column cases; B has simple IOException catch.；A tokenizes with comma; B tokenizes with space.
- 修正建议: Train the model with more examples of broad structural clones (Type-3/4) to recognize common I/O patterns despite lexical differences.；Incorporate control flow or dataflow features to capture repeated patterns (e.g., read-loop-tokenize-store).；Use contrastive learning to emphasize algorithmic similarity over lexical similarity.

### case_id=5679 FN partial_functionality

- 方法: `getFile` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies an attribute in the XML, and saves it locally, returning the file path.
- B 摘要: Copies a file from source to destination using FileChannel and MappedByteBuffer.
- 静态失败原因: Static BERT models like GraphCodeBERT rely heavily on lexical tokens and structural patterns. The low token Jaccard similarity (0.13) and different method signatures (String vs void) likely caused the model to miss the shared file I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone due to the shared file I/O pattern using FileChannel and FileOutputStream, which could be considered a similar sub-functionality (Type-3 or Type-4) even though the overall goals differ.
- 共享行为: Both perform file I/O operations involving reading from a source (URL stream vs FileInputStream) and writing to a file output stream.；Both use FileChannel for efficient data transfer.
- 行为差异: Function A includes XML parsing and attribute modification, while Function B is a straightforward file copy.；Function A handles complex exception types (SAXException, ParserConfigurationException) and fallback logic, whereas Function B only handles IOException.；Function A checks if the target already exists, while Function B does not.；Function A uses a temporary file and renames, while Function B writes directly.
- 修正建议: Improve model sensitivity to long-range semantic overlaps where a small block of code is structurally similar.；Use data-flow analysis to detect similar I/O operations across different functions.；Consider hierarchical or multi-level representation that captures functional primitives.

### case_id=5680 FP lexical_or_api_overlap

- 方法: `main` vs `doUpload`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses a Prolog file, generates runtime adapter classes, and writes them to a JAR output.
- B 摘要: Handles HTTP file upload requests, saves files to a temporary directory, processes parameters, and returns XML or forwards to a view.
- 静态失败原因: Static BERT models rely heavily on lexical token overlap and structural patterns; the presence of similar API calls (File, IOException, logging) and control-flow patterns (if, try-catch) likely caused false positive classification.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires significant functional overlap; these functions share only generic boilerplate and no domain-specific logic.
- 共享行为: Both use java.io.File for file operations；Both have error handling with try-catch blocks；Both use logging (System.out or LOG)
- 行为差异: Function A is a command-line main method; Function B is an HTTP servlet handler；Function A parses Prolog and generates Java classes; Function B handles multipart uploads；Function A writes a JAR file; Function B redirects or returns XML responses；Function A uses ObjectOutputStream; Function B uses PrintWriter and RequestDispatcher
- 修正建议: Use data-flow analysis to capture semantic intent；Include context about method signatures and surrounding classes；Train models to distinguish between generic error handling and core functionality

### case_id=5681 FP partial_functionality

- 方法: `checkForUpgrade` vs `getXML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for software upgrades by querying a license server, parsing the response, updating database records, and managing UI visibility.
- B 摘要: Fetches XML content from a given URL by sending a request and reading the response line by line, returning the result as a string.
- 静态失败原因: Static BERT/GraphCodeBERT may have overemphasized the common token sequence (URL, BufferedReader, InputStreamReader, readLine) and syntactic pattern of opening and reading a connection, ignoring the surrounding logic and semantic purpose.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled non-clone because despite a shared low-level I/O pattern, the overall functionality and logic are entirely different, which would not be considered Type-3/4 in BigCloneBench.
- 共享行为: Make HTTP request to a URL and read response using BufferedReader
- 行为差异: A performs database operations and UI updates; B does not.；A parses response into structured fields; B returns raw string.；A has complex conditional logic based on response; B handles exceptions and returns null.；A is void; B returns String.
- 修正建议: Include method-level semantic embeddings focusing on overall purpose and side effects.；Use data-flow analysis to capture interactions like database writes and UI changes.；Augment training with pairs that share small I/O patterns but differ in main behavior.

### case_id=5682 FN benchmark_preference_bias

- 方法: `DialogHelper` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Constructs a dialog to display an image and provides UI to save the image to a file with overwrite handling.
- B 摘要: Reads a locale-specific properties file, modifies or adds a key-value pair for a message, and writes the updated content back.
- 静态失败原因: The static model (e.g., GraphCodeBERT) likely correctly identified no semantic similarity due to low token overlap and distinct control flow; it failed only in the sense that it did not match the (potentially incorrect) BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB annotation may be erroneous or based on superficial overlaps like file I/O and property file handling, but the functions serve completely different purposes.
- 行为差异: Function A deals with image saving; function B deals with properties file modification.；Function A is a GUI constructor; function B is a server-side utility method.；Function A uses JDialog, JFileChooser, FileChannel; function B uses Properties, FileReader, FileWriter.；Function A has user interaction; function B is fully automated.
- 修正建议: Re-evaluate the BCB annotation for this pair; consider removing or correcting the clone label.；Improve static models to handle noisy ground truth, e.g., using confidence thresholds or filtering.

### case_id=5683 FN partial_functionality

- 方法: `getFile` vs `copyFileByNIO`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint in the XML, and saves to a temporary file.
- B 摘要: Copies a file from source to destination using NIO FileChannel.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token and structural similarity; the token Jaccard is very low (0.1157), and the functions differ significantly in size and logic, causing the model to miss the common NIO transfer pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the NIO channel transfer pattern as a shared behavioral fragment, accepting partial functional similarity as a clone (Type-3/Type-4).
- 共享行为: Both use FileChannel transferFrom/transferTo for data transfer between channels.
- 行为差异: getFile downloads from URL, parses and modifies XML, and handles multiple exceptions; copyFileByNIO only copies a local file.；getFile has lengthy error handling and logging; copyFileByNIO is concise with no error handling beyond throwing IOException.；getFile returns the file path; copyFileByNIO returns void.
- 修正建议: Incorporate data-flow analysis to detect common library API usage (e.g., FileChannel.transferXXX).；Use a hybrid approach that combines lexical, structural, and semantic features to capture partial functional overlap.

### case_id=5684 FN benchmark_preference_bias

- 方法: `descargarArchivo` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Transforms XML and generates HTML pages for a website editing environment.
- 静态失败原因: Static BERT correctly identified non-clone due to very low token Jaccard (0.0545) and distinct method names and functionality; the BCB label appears to be a false positive.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both containing FileInputStream and FileOutputStream usage, but overall functionality is entirely different.
- 共享行为: Both perform file I/O operations；Both handle IOException
- 行为差异: Function A is a simple file copy; Function B is a complex site builder with XML transformation, multiple file reads/writes, and DOM manipulation
- 修正建议: Re-evaluate BCB label for this pair；Consider adding more diverse non-clone examples in training data to avoid overfitting to generic I/O patterns

### case_id=5685 FN benchmark_preference_bias

- 方法: `readAndRewrite` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads and rewrites a DICOM image file by parsing and copying pixel data.
- B 摘要: Launches a NexOpen project configuration by setting up Maven POM files and Hibernate dialect, then scheduling an install action.
- 静态失败原因: Static BERT correctly predicted non-clone due to low textual overlap and distinct semantics.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled due to superficial structural similarity (both involve file reading/writing and parameter handling) but actual functionality is unrelated.
- 共享行为: both use file I/O streams
- 行为差异: completely different domains (DICOM vs Eclipse project configuration)；different libraries and APIs；no shared logic or algorithm
- 修正建议: review BCB annotation for this pair；ensure clone pairs have meaningful semantic similarity

### case_id=5686 FP lexical_or_api_overlap

- 方法: `retrieveQ` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads entire content from a URL into a single string, printing HTTP response message.
- B 摘要: Reads tab-separated lines from a URL and populates a vector with extracted ID and description.
- 静态失败原因: The model overemphasized shared API usage (URL, InputStream) and the general pattern of reading from URLs, ignoring the significant differences in data processing and output types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers the functions as non-clones because they have different output goals (raw content vs. structured extraction) and different error handling, making them distinct functionalities despite both reading from URLs.
- 共享行为: Both open a URL and read input line by line.
- 行为差异: A returns the raw text as a string; B extracts specific columns and adds to a vector.；A uses BufferedReader; B uses Scanner.；A prints the HTTP response message; B catches exceptions silently.；A declares thrown exceptions; B handles them internally.
- 修正建议: Incorporate data flow and output type analysis to distinguish between raw retrieval and structured parsing.；Train on examples with similar API calls but different final behavior.

### case_id=5687 FN partial_functionality

- 方法: `runInternal` vs `lookupFutureEvents`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Method to fetch and process an OPDS catalog or download a book via HTTP, handling pagination and progress.
- B 摘要: Method to fetch and parse a list of future Meetup events from a JSON API, returning them as Event objects.
- 静态失败原因: Static BERT models rely on token overlap and syntactic patterns. The low Jaccard similarity (0.09) and different method names, domains, and APIs result in low embedding similarity, causing a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers broad Type-4 clones as positive, focusing on overall functionality like 'HTTP data retrieval and parsing'. Despite differences, both methods serve a similar purpose: fetching structured data from a web service and processing it.
- 共享行为: Both connect to a remote URL via HTTP；Both read data from the input stream；Both parse the response (XML/JSON)；Both handle IO exceptions
- 行为差异: Different data sources (OPDS catalog vs Meetup API)；Different output: void with callback vs List<Event>；Pagination handling in A only；Progress display in A only
- 修正建议: Use code representations that capture functional intent (e.g., data flow graphs, API call sequences)；Incorporate context from surrounding class or method usage；Leverage models that handle long-range dependencies

### case_id=5688 FN benchmark_preference_bias

- 方法: `copyResource` vs `testSimpleQuery`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using byte-by-byte stream copying.
- B 摘要: Tests a JCR query by setting up data, writing XML, executing a query, and verifying results using assertions and stream copying via IOUtils.copy.
- 静态失败原因: The static model correctly identified the lack of semantic equivalence; the BCB annotation is likely an outlier due to overly broad clone criteria.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both methods performing stream copying operations, ignoring the distinct high-level purposes (utility vs. test) and different contexts.
- 共享行为: Both use InputStream and OutputStream for reading and writing data.；Both close streams after use.
- 行为差异: A is a general utility for copying any resource to a file; B is a specific test with multiple JCR operations and assertions.；A reads from a URL or file; B reads from JCR nodes and writes XML content.；A copies byte-by-byte in a while loop; B uses IOUtils.copy for one part and performs many other operations.
- 修正建议: Use stricter clone definition that requires structural or semantic similarity beyond basic I/O operations.；Filter out test methods from utility methods in training data.

### case_id=5689 FP lexical_or_api_overlap

- 方法: `readUNI` vs `issueCommandToServer`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads tab-separated data from a URL and populates a vector with id and description pairs.
- B 摘要: Sends a command and a capsule object as an HTTP POST request to a server and returns the response string.
- 静态失败原因: Static BERT/GraphCodeBERT models may over-rely on lexical and API-level overlap (e.g., both use URL, streams, loops, try-catch) and miss the difference in overall intent and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clones because the functions serve completely different tasks, despite sharing some I/O boilerplate.
- 共享行为: Both perform network I/O；Both read data from streams；Both close resources；Both use loops to process lines
- 行为差异: Different purpose: data retrieval vs command submission；Different protocols: HTTP GET-like reading vs POST with parameters；Different output: populate a vector vs return a string；Different data format: tab-separated parsing vs URL-encoded parameters
- 修正建议: Incorporate structural differencing to detect different data flow patterns；Use contrastive learning that penalizes semantic divergence beyond lexical similarity

### case_id=5690 FN benchmark_preference_bias

- 方法: `doTransfer` vs `import_hints`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: HTTP proxy function that reads a URL parameter, forwards the request and response streams, and handles HTTP methods.
- B 摘要: Imports puzzle hints from a file or URL, parsing lines to place pieces on a board.
- 静态失败原因: Static BERT correctly identified non-clone; the BCB label is likely an overgeneralization based on superficial API similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled due to both functions involving URL reading and stream processing, despite fundamentally different purposes.
- 共享行为: Both potentially open a URL connection to read input；Both use InputStream and BufferedReader to read data
- 行为差异: A acts as an HTTP proxy, copying request and response streams and setting headers；B parses a specific text format containing piece coordinates and rotations；A writes output to a servlet response, while B modifies a board object；A handles HTTP methods and response codes, while B has no HTTP handling
- 修正建议: Refine clone criteria to require semantic equivalence beyond common library usage；Use data flow and control flow analysis to distinguish different computational intents

### case_id=5691 FP boilerplate_overlap

- 方法: `createDialogArea` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Creates a dialog area to display a license file from a bundle resource, using a Browser or Text widget.
- B 摘要: Performs a Google image search, parses the response to extract image URLs, and updates a GUI component.
- 静态失败原因: Static BERT likely over-relied on the similar I/O boilerplate (URL opening, BufferedReader, exception handling) and failed to capture the high-level semantic difference and distinct data processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the overall functionality is completely different; the shared I/O boilerplate is insufficient to consider them clones under their annotation guidelines.
- 共享行为: Both open a URL and read from an InputStream using BufferedReader.；Both handle IOExceptions with try-catch-finally blocks.；Both close resources (BufferedReader and InputStream) in finally blocks.
- 行为差异: Function A displays a license file in a dialog; Function B performs image search and updates an album art label.；Function A reads a local resource file; Function B sends an HTTP request to a remote service.；Function A uses a Browser or Text widget; Function B parses HTML and extracts image URLs.；Function A returns a Composite; Function B has void return and manipulates a global list and GUI.
- 修正建议: Enhance model with control flow and data flow analysis to distinguish high-level intent.；Use contrastive learning to discriminate between functions that share boilerplate but differ in core functionality.；Incorporate more structural features like method call sequences and API usage patterns.

### case_id=5692 FP lexical_or_api_overlap

- 方法: `loadMFileViaWeb` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a MATLAB .m file from a web URL, reads its content, and returns a UserFunction object after parsing.
- B 摘要: Connects to a YouTube video URL, extracts video ID and time parameters from the response, and returns a full download URL string.
- 静态失败原因: The model likely focused on lexical and structural similarities (e.g., both use URL, BufferedReader, while loop, try-catch) and missed the semantic differences due to limited understanding of long-range dependencies and differing domain contexts.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the functions serve completely different purposes: one loads a MATLAB function, the other retrieves a YouTube video URL. Although they share similar boilerplate for URL reading, the core functionality and output are distinct.
- 共享行为: Both open a URL and read its content line by line using BufferedReader；Both close the reader and handle IOExceptions
- 行为差异: Different return types: UserFunction vs String；Different URL sources and parsing logic: one concatenates all lines, the other searches for a specific parameter line；One returns a parsed object, the other constructs a new URL string
- 修正建议: Improve training data with more negative examples having similar boilerplate but different semantics；Include type information of variables and return types to disambiguate；Use dataflow analysis to capture how data is transformed rather than just sequence of API calls

### case_id=5693 FP lexical_or_api_overlap

- 方法: `readPage` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL and returns its content as a string, optionally ignoring comment lines starting with '#'.
- B 摘要: Reads a URL with basic authentication, writes the content to a temporary file, and updates a status label with file size.
- 静态失败原因: The static model likely overemphasized the common structural pattern of opening a URL, creating a BufferedReader, reading lines in a while loop, and closing the reader. It may have also been misled by similar API usage (URL, BufferedReader, InputStreamReader). However, the Jaccard similarity is low, so it might be a failure in capturing control flow or data dependencies that distinguish the two functions.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the functions have fundamentally different purposes (reading vs writing to file, optional authentication, progress reporting) despite sharing a basic URL reading pattern. The behavioral differences outweigh the shared structure.
- 共享行为: Both read from a URL line by line using BufferedReader.；Both use InputStreamReader and openStream/getInputStream.
- 行为差异: Function A returns the content as a string; Function B writes to a file.；Function A has an ignoreComments parameter that skips lines starting with '#'; Function B does not.；Function B performs basic authentication if username is provided; Function A does not.；Function B updates a status label with file size; Function A has no UI interaction.
- 修正建议: Include additional features capturing overall function purpose (e.g., return type, method name, or summary).；Enhance model with dataflow analysis to distinguish between returning content vs writing to file.；Use contrastive learning with negative examples that share API usage but differ in semantics.

### case_id=5694 FP partial_functionality

- 方法: `getWebPage` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Fetches the content of a web page from a URL and returns it as a string, throwing an error on failure.
- B 摘要: Performs a software upgrade check by querying a database, fetching upgrade information from a URL, processing XML-like responses, and updating UI components accordingly.
- 静态失败原因: The static model might have been misled by the lexical and structural overlap of the common pattern of opening a URL, reading lines with BufferedReader, and concatenating. Despite low Jaccard similarity (0.0628), the model may have weighted this pattern heavily, ignoring the vast differences in the rest of the code, especially since function B is long and complex.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled this as non-clone because the functions have different names, return types, parameters, and overall purpose. The shared pattern of reading from a URL is a small portion of function B's behavior, and BCB typically requires more substantial functional similarity to consider them clones.
- 共享行为: Open a URL connection；Read lines from a BufferedReader；Concatenate lines into a string
- 行为差异: Function A returns the fetched content; function B does not return a value but updates UI.；Function A is a simple utility; function B involves database queries, XML parsing, and UI manipulation.；Function A throws an Error; function B throws a checked Exception.；Function A has minimal logic; function B has complex conditional logic and loops.
- 修正建议: Incorporate method-level context (name, return type, parameters) as additional features.；Use program dependency graphs or data flow analysis to distinguish core functionality from boilerplate.；Apply thresholding on the proportion of overlapping code relative to total function length.

### case_id=5695 FP lexical_or_api_overlap

- 方法: `main` vs `createNew`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that reads a Prolog file, generates Java adapter classes, and writes them to a JAR file.
- B 摘要: Method that creates a new resource file by copying an input stream to a destination file, with ownership check.
- 静态失败原因: The static model likely overestimated similarity due to lexical overlap of common Java I/O classes (File, FileOutputStream) and similar exception handling patterns, despite the completely different high-level purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled these as non-clones because they perform vastly different tasks with no shared functionality beyond basic file I/O operations, which is too generic to indicate a clone.
- 共享行为: Both write data to files using FileOutputStream.；Both handle I/O exceptions.；Both use try-finally for resource management.
- 行为差异: Function A is a main method with complex workflow including parsing, code generation, and serialization; Function B is a simple file copy operation.；Function A involves class loading, annotation generation, and multiple file writes; Function B writes a single file.；Function A is standalone; Function B is part of a resource manager and checks ownership.；Function A reads from a Prolog file; Function B reads from an InputStream.
- 修正建议: Incorporate control flow and data flow analysis to distinguish different file I/O contexts.；Use more fine-grained semantic embeddings that capture the overall task rather than local patterns.；Add training examples with high lexical but low semantic similarity to reduce false positives.

### case_id=5696 FN partial_functionality

- 方法: `getHTML` vs `addQDInformation`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads HTML from a given URL using HTTP connection, optionally writes the content to a file, and returns the HTML string.
- B 摘要: Reads a local or remote file containing QD information, parses lines to update internal project data structures with timestamps and values.
- 静态失败原因: Static models like GraphCodeBERT focus on lexical and structural similarity. Although both functions have similar control flow, the token Jaccard is low (0.218) due to different identifiers, API calls, and comments, causing the model to miss the structural clone relationship.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions share a common pattern of opening a URL/file, reading lines in a BufferedReader loop, and handling exceptions, which qualifies as a Type-3 or Type-4 clone with partial functionality overlap in data retrieval.
- 共享行为: Both open a URL or file as an input stream.；Both use BufferedReader to read lines in a while loop.；Both handle exceptions with try-catch and close resources in finally blocks.；Both perform network I/O operations.
- 行为差异: A returns the full HTML string; B updates internal state without returning a value.；A uses HttpURLConnection for HTTP download; B uses FileReader or URL.openStream.；A optionally writes output to a file; B parses specific line formats (e.g., 'pg ', 'pt ') and extracts structured data.；B has conditional logic based on file modification dates and local vs. remote mode.
- 修正建议: Train on more Type-3/4 examples with diverse API usage.；Incorporate dataflow or control-flow features to capture common patterns.；Use contrastive learning with functional summaries to identify partial behavioral overlap.

### case_id=5697 FP boilerplate_overlap

- 方法: `getDatasetsList` vs `readTwitterFead`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Caches and retrieves a list of dataset names from a server URL by reading lines.
- B 摘要: Downloads a JSON Twitter timeline from a fixed URL and concatenates lines into a single string.
- 静态失败原因: Static BERT models likely overemphasized overlapping tokens like 'BufferedReader', 'readLine', 'IOException', and 'URL', and the common boilerplate pattern of opening a stream and reading lines, while missing the semantic differences in caching, return type, and exception propagation.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered non-clone due to different return types, caching behavior, URL sources, and exception handling. The structural similarity in reading lines was insufficient to override significant functional differences.
- 共享行为: Both open a URL and read lines via BufferedReader；Both handle IOException；Both build a result from the read lines
- 行为差异: A caches results in a map; B does not cache；A returns List<String>; B returns String；A uses parameterized URL; B uses hardcoded URL；A throws RuntimeException on error; B logs and returns possible empty string
- 修正建议: Incorporate method name and surrounding context to capture intent；Use data flow analysis to track transformations (e.g., list vs string) and caching；Add features for exception handling style and I/O patterns

### case_id=5698 FN lexical_or_api_overlap

- 方法: `getEncoding` vs `GetResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads HTTP response headers and body to extract character encoding, returning encoding or default.
- B 摘要: Sends HTTP GET request and reads entire response body into a string, returning content.
- 静态失败原因: Static BERT/GraphCodeBERT predicted non-clone likely due to relatively low token Jaccard (0.2769) and lexical differences (method names, exception handling, return type). The model did not capture the underlying semantic similarity of both being HTTP response readers, possibly because it lacks understanding of the shared high-level operation.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely classifies as Type-4 clone because both methods read textual data from HTTP responses using similar I/O patterns (BufferedReader, InputStream), despite different return values. The core network-reading behavior is considered functionally similar.
- 共享行为: Open URL connection；Use BufferedReader and InputStreamReader to read lines from response stream；Return a String
- 行为差异: A extracts encoding from headers/body; B returns full content；A uses URLConnection; B uses HttpURLConnection and checks response code；A closes reader in finally; B does not close resources；A propagates IOException; B catches exceptions silently
- 修正建议: Incorporate AST or data-flow features to capture structural patterns of network I/O；Use contrastive learning with functionally similar examples from BigCloneBench；Add domain-specific knowledge (e.g., HTTP request/response handling patterns) to the model

### case_id=5699 FN benchmark_preference_bias

- 方法: `getFile` vs `dump`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint in the XML, and returns the file path.
- B 摘要: Copies a source file to a target file using buffered streams and returns a boolean status.
- 静态失败原因: Static BERT models likely correctly identified low token overlap (Jaccard 0.123) and distinct control flows, but BCB's broad cloning criteria may consider generic file I/O as sufficient semantic overlap, causing the model's prediction to mismatch the BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones because both are file manipulation utilities that handle I/O exceptions and use similar stream patterns, reflecting a broad Type-4 view of functionality.
- 共享行为: Both involve file I/O operations using FileInputStream and FileOutputStream
- 行为差异: Function A downloads from a network URL; function B copies from a local file.；Function A modifies XML content; function B does a raw byte copy.；Function A returns a file path; function B returns a boolean.；Function A has complex control flow with existence checks and multiple exceptions; function B is simple.
- 修正建议: Incorporate explicit file I/O pattern detection to recognize boilerplate similarities.；Use a more nuanced clone definition that distinguishes core functionality from auxiliary I/O.；Adjust training labels for pairs with significant structural differences but shared generic operations.

### case_id=5700 FP partial_functionality

- 方法: `getWebByUrl` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Connects to a URL, reads HTML content line by line, writes to a file with newlines, and recursively extracts URLs from each line up to a depth limit, with logging.
- B 摘要: Downloads a file from a URL to a destination path, reading bytes in fixed-size chunks and updating a progress bar, returning a boolean success status.
- 静态失败原因: Static BERT/GraphCodeBERT may have over-generalized based on the common pattern of URL connection, input stream, file output, and try-catch. It likely ignored the fine-grained differences in I/O handling (line vs byte), the presence of recursive call in A, and the distinct side effects, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels these as non-clones because the functions have distinct high-level purposes: extracting links from an HTML page vs binary file download. The additional specialized logic in each (recursive URL extraction vs progress tracking) makes them semantically different even if the core I/O pattern overlaps.
- 共享行为: Open URL connection to a given URL；Read from an input stream obtained from the connection；Write to a file output stream
- 行为差异: A reads line-by-line with BufferedReader and writes with PrintWriter; B reads bytes in chunks with BufferedInputStream and writes with BufferedOutputStream；A appends newlines and processes each line for URL extraction; B has no such processing；A has progress logging via println and addReport; B updates a progress bar via MessageFrame；A catches exceptions and prints failure; B throws exceptions and returns boolean
- 修正建议: Enhance model to distinguish between line-oriented and byte-oriented I/O；Incorporate structural analysis of additional control flow (e.g., recursive calls) and side effects；Use contrastive learning to emphasize differences in method names and parameter usage

### case_id=5701 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads integers from a resource file and returns them as a set.
- B 摘要: Performs a version check by parsing a version file from a URL and displays UI messages.
- 静态失败原因: Static BERT models may be misled by lexical and API overlap (e.g., URL, InputStreamReader, readLine) and common boilerplate code (try-catch), failing to capture the distinct semantic intents.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label as non-clone because the two functions have fundamentally different purposes and outputs, despite sharing some structural patterns like reading lines from a URL.
- 共享行为: Both open a URL and read lines from an input stream.；Both use try-catch for exception handling.；Both utilize InputStreamReader to read text from a stream.
- 行为差异: readZoneIDs returns a HashSet of integers; doVersionCheck returns void and updates UI.；readZoneIDs catches all exceptions and prints stack trace; doVersionCheck specifically catches IOException and shows error dialog.；readZoneIDs reads from a class resource; doVersionCheck reads from a URL defined in a property.；readZoneIDs parses each line as an integer; doVersionCheck searches for specific prefixes and extracts version/build strings.
- 修正建议: Incorporate analysis of method-level data flow and control flow to differentiate purposes.；Use semantic role labeling of method outputs and side effects.；Train on more diverse negative pairs with similar API usage but different functionality.

### case_id=5702 FN benchmark_preference_bias

- 方法: `testLoadSource` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Loads an arXiv article source from a DAO facade into an InputStream, reads it into a string, and asserts the content contains a specific phrase.
- B 摘要: Builds a web site for editing by iterating over pages, reading XML and control files, applying XSL transformations and string replacements, and writing output files.
- 静态失败原因: Static BERT/GraphCodeBERT correctly identified the low token overlap (Jaccard 0.054) and structural dissimilarity, but failed to match BCB's likely overbroad functional similarity criterion, leading to a false negative relative to the benchmark.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to broad Type-4 classification where both functions perform file I/O and string processing, ignoring the vast difference in purpose and complexity.
- 共享行为: Both use InputStream and StringWriter for I/O operations；Both involve reading file contents into strings
- 行为差异: a is a simple test loading one source; b is a complex multi-step site generation with file I/O, transformation, and error handling；a has no parameters; b has 8 parameters and uses many external libraries (DOM, XSLT, FTP)；a's output is an assertion; b's output is writing transformed HTML files
- 修正建议: Review BCB annotation for potential mislabeling; these functions are not semantic clones；If retaining BCB label, use a more fine-grained clone type system to distinguish Type-4 clones from unrelated code

### case_id=5703 FN partial_functionality

- 方法: `login` vs `sendRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into LOLA by sending email and password via HTTP POST and extracting session ID from response.
- B 摘要: Sends an XML request to a configurable servlet with GZIP compression and parses the XML response.
- 静态失败原因: The low token Jaccard (0.19) and different API usage (e.g., URLEncoder vs GZIPOutputStream) cause static models to miss the structural similarity. Static BERT-based methods rely on lexical overlap or API sequence matching, which are insufficient for this Type-4 clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels methods as clones if they perform similar high-level tasks, like network communication with request/response processing, even if implementation details differ. Both functions share the core pattern of opening a connection, writing data, and reading a response.
- 共享行为: Both open HTTP connections using URLConnection.；Both set DoOutput to true and write data to the output stream.；Both read response from the input stream.；Both handle exceptions with try-catch.
- 行为差异: A sends form-encoded data; B sends XML with GZIP compression.；A reads a single line to extract session ID; B uses SAXBuilder to parse XML.；A returns the session ID; B returns an empty string.；B includes server URL configuration logic (preferences, dialog).
- 修正建议: Use graph-based code representations (e.g., CFG, AST with data flow) to capture structural patterns.；Incorporate program analysis to abstract over specific API implementations.；Increase training data with Type-3 and Type-4 clones to improve generalization.

### case_id=5704 FN partial_functionality

- 方法: `getWebByUrl` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches a web page from a URL, saves it to a file, logs progress, and recursively crawls links.
- B 摘要: Opens an input stream from a URL or file and reads it via a delegate method, returning a status code.
- 静态失败原因: Low token overlap (0.15), different method names, different control flow, and additional complexity in A hides the shared URL reading core, leading static models to miss the partial functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs as clones if they share a common operation like URL content retrieval, even if overall functionality differs, accepting broad Type-3/Type-4 similarity.
- 共享行为: Both can open a URL and read its content.
- 行为差异: A writes the content to a file and recursively crawls links; B delegates reading to another method and returns a status code.；A uses BufferedReader and PrintWriter; B uses BufferedInputStream.；A handles only URLs; B also handles local files.；A includes logging and progress reporting; B does not.
- 修正建议: Incorporate dataflow analysis to identify common operations like opening a URL and reading an input stream.；Use contrastive learning to emphasize shared subfunctionalities over syntactic differences.

### case_id=5705 FP lexical_or_api_overlap

- 方法: `get` vs `load`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches game records from a URL based on location and count, parsing lines into GameRecord objects.
- B 摘要: Loads a pastebin XML document by ID, concatenating all lines into a single string.
- 静态失败原因: The static model likely over-relied on lexical overlap of common Java HTTP/IO code patterns (URL, BufferedReader, readLine, try-catch) and missed the semantic differences in headers, data parsing, and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clones because the functions have distinct purposes, input/output types, and processing logic, despite sharing a common boilerplate pattern of HTTP reading.
- 共享行为: Both open an HTTP connection and read lines from a URL response using BufferedReader.；Both handle IOException with try-catch blocks.
- 行为差异: Function A uses HttpURLConnection with specific request headers; Function B uses URLConnection and openStream directly.；Function A returns an array of GameRecord; Function B returns a String.；Function A filters out lines starting with '#'; Function B concatenates all lines.；Function A takes parameters URL, lat, lon, count; Function B takes a single string id.
- 修正建议: Train with more diverse examples that emphasize differences in API usage context.；Incorporate type information for output to distinguish different return types.；Use data flow analysis to capture differences in how data is processed after reading.

### case_id=5706 FP partial_functionality

- 方法: `getWebByUrl` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a web page, saves it to a file, and recursively processes embedded URLs.
- B 摘要: Performs an HTTP GET request and returns the first line of the response as a string.
- 静态失败原因: The model likely overfitted to lexical and structural similarities (e.g., URL creation, BufferedReader, InputStreamReader) and missed the critical side effects and control flow differences (file writing, recursion, exception handling patterns).
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels these as non-clones because the core functionality differs significantly: one is a full-page downloader with file I/O and recursion, the other is a simple single-line fetcher. Even broad Type-3/4 categories require similar functionality, which is absent here.
- 共享行为: Both open a URL connection and read from an InputStream using BufferedReader.
- 行为差异: A writes content to a file and logs progress; B only returns a string.；A reads all lines and recursively processes URLs; B reads only the first line and returns immediately.；A uses generic URLConnection and prints/ logs; B uses HttpURLConnection and throws exceptions.
- 修正建议: Incorporate dataflow analysis to track side effects like file writes and recursion.；Use graph-based models that capture control and data dependencies beyond token sequences.；Add training examples that highlight functionality differences despite API overlaps.

### case_id=5707 FP boilerplate_overlap

- 方法: `PageLoader` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Constructor that reads the entire content of a given URL into a string member variable and throws an exception on failure.
- B 摘要: Method that performs a Google image search by constructing a URL, fetching the results, parsing image URLs, updating UI components, and handling errors with dialog boxes.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized the common NLP pattern of reading from a URL (try-catch, BufferedReader, while loop) while ignoring the distinct semantic contexts and additional operations. The model may have been biased by the structural similarity in the first few lines of code, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the overall functionality and intended use are very different—one is a generic page loader, the other is a specific image search with UI updates. The low token Jaccard (0.1236) supports minimal lexical overlap, and BCB prioritizes behavioral similarity over shared boilerplate patterns.
- 共享行为: Open a URL and read its content line by line into a string buffer
- 行为差异: Function A is a constructor with no return value and throws Exception; Function B is a void method that catches exceptions and updates UI.；Function A reads from a raw URL stream; Function B uses HttpURLConnection with a custom User-Agent header.；Function B parses the response to extract image URLs and updates UI components; Function A only stores the raw page content.；Function B has multiple side effects (clearing a list, enabling a button, setting an icon); Function A has no side effects besides initializing inputLine.
- 修正建议: Incorporate data flow analysis to track the use of read data beyond the reading loop.；Weigh API calls and method names more heavily (e.g., constructor vs. method, HttpURLConnection vs. URL.openStream).；Use a classifier that differentiates between core logic and boilerplate code, perhaps by computing similarity only on non-boilerplate parts.；Integrate static analysis of method signatures, return types, and exception handling to better capture functional intent.

### case_id=5708 FN long_range_semantics

- 方法: `copyResource` vs `testCopyUnknownSize`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using byte-by-byte I/O.
- B 摘要: Tests copy method by copying ByteArrayInputStream to ByteArrayOutputStream and verifying data.
- 静态失败原因: Static BERT models rely on lexical and structural similarity; here token overlap is low (10%), and the functions have different control flows and API calls, causing the model to miss the semantic commonality of copying.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as data copy operations (Type-4), focusing on the shared high-level behavior of copying from input to output despite different contexts.
- 共享行为: Both copy data from an input source to an output destination.
- 行为差异: Different source/target types: URL/file vs ByteArray streams；One is a utility method, the other is a test with assertions；Different copy implementations: manual loop vs library call；Exception handling differs
- 修正建议: Improve representation of high-level intent (e.g., using data flow or semantic role labeling)；Use contrastive learning to learn broader semantic equivalence

### case_id=5709 FN lexical_or_api_overlap

- 方法: `modifyApplicationMessage` vs `decodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a message in a properties file for a given locale, creating a localized file if needed.
- B 摘要: Decodes a Base64-encoded file and writes the decoded output to another file.
- 静态失败原因: Low token Jaccard (0.206) and distinct API usage (Properties vs Base64) misled the model to focus on lexical differences, ignoring the shared boilerplate pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled these as clone due to similar file I/O structure and resource management, accepting broad Type-3/Type-4 similarity based on skeleton rather than core functionality.
- 共享行为: Reads from an input file using InputStream/Reader；Writes to an output file using FileWriter/OutputStream；Uses try-catch blocks for exception handling；Closes streams in finally or after use
- 行为差异: A processes properties files (text key-value pairs) with locale-specific logic; B decodes binary Base64 data；A uses Properties, BufferedReader, and StringBuilder; B uses Base64.InputStream and byte buffer；A conditionally copies a file if missing and performs line-by-line parsing; B uses fixed-size buffer and streaming
- 修正建议: Incorporate structural similarity (e.g., control flow) beyond tokens；Use dataflow analysis to capture file I/O operations；Train on examples where high-level structure (read-process-write) indicates clone even with different libraries

### case_id=5710 FP other

- 方法: `copyIconFiles` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.75`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies icon files from annotation-specified paths for UML class icons.
- B 摘要: Reads and parses configuration data from strings and a file to populate sets and maps for Tibetan transliteration.
- 静态失败原因: The model likely overgeneralized from superficial similarities (both are void methods with I/O and loops) and misattributed high similarity due to local code structures (e.g., multiple if-blocks, file handling idioms) despite very low token overlap.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically requires at least partial functional overlap; here the functions perform entirely different tasks (icon file copying vs. data parsing) with no shared input/output or purpose.
- 共享行为: Both perform file I/O operations.；Both use try-catch blocks for exception handling.；Both iterate over collections of data.
- 行为差异: A copies files using FileChannel; B reads and parses text data.；A works on specific annotations (icon16/icon32); B processes a complex configuration file.；A produces output files; B builds in-memory data structures (sets, maps).；A only uses two specific file types; B deals with numerous string tokens and conditional logic.
- 修正建议: Incorporate data-flow analysis to distinguish productive vs. consumer operations.；Improve detection of method-level intent via higher-level semantic embeddings.；Avoid relying on boilerplate patterns (e.g., try-catch with printStackTrace) as clone indicators.

### case_id=5711 FN benchmark_preference_bias

- 方法: `getFile` vs `WebmillDeploy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint attribute, and saves it to a temporary location.
- B 摘要: Processes a JAR file, parses and rewrites XML files (web.xml, portlet.xml, context.xml), and creates a WAR file.
- 静态失败原因: The static model correctly predicted non-clone because the token Jaccard is low and the overall program structure and intent are dissimilar. The model did not fail; the BCB annotation appears to be a false positive due to oversensitivity to shared API calls.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may incorrectly label this as a clone due to surface-level similarities: both functions perform file I/O, XML manipulation, and use similar constructs like FileChannel and logging. However, the core functionality is fundamentally different.
- 共享行为: Both involve file I/O operations (reading, writing, and channel transfer).；Both parse and modify XML documents.；Both use try-catch-finally for resource management and error handling.；Both log progress and handle exceptions with custom messages.
- 行为差异: Function A downloads content from a remote URL; Function B reads from a local JAR file.；Function A only modifies the 'location' attribute in a single XML element; Function B performs extensive XML rewriting using a separate rewriter class.；Function A produces a .wsdl file; Function B produces a .war file.；Function B deals with multiple XML files and adds JAR entries; Function A does not handle JAR files.
- 修正建议: Re-annotate the pair in BCB as non-clone to correct the benchmark.

### case_id=5712 FN benchmark_preference_bias

- 方法: `main` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Demonstrates file channel I/O with various character encodings and buffer operations.
- B 摘要: Launches a NexOpen Eclipse plugin configuration, handling Maven POM files and setting Hibernate properties.
- 静态失败原因: Static BERT correctly predicted non-clone due to low lexical and semantic overlap, but BCB label is inconsistent with content.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Uncertain, likely a labeling error in BCB given the very low token Jaccard and entirely different functionality.
- 共享行为: Both involve file I/O at a high level
- 行为差异: A is a simple file reading/writing example, B is a complex Eclipse plugin launch configuration；A uses NIO channels, B uses Eclipse API and DOM；A is standalone, B is part of an Eclipse plugin
- 修正建议: Re-evaluate BCB label for this pair；Ensure consistency in clone annotation guidelines

### case_id=5713 FN benchmark_preference_bias

- 方法: `doGet` vs `handle`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests to retrieve and display a page with permission checks and caching.
- B 摘要: Handles log file rotation, compression, and archiving based on configuration.
- 静态失败原因: Static BERT/GraphCodeBERT likely correctly predicted non-clone due to low token overlap and different API usage, but BCB considers them clones possibly due to broad functional similarity in handling events.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to both being void methods that handle events (HTTP request and log rotation) and using similar error handling patterns, but the core functionality is entirely different.
- 共享行为: Both use try-catch blocks for exception handling.；Both use logging (myLogger vs Debug.debug).
- 行为差异: Function A processes HTTP requests and serves web pages; Function B rotates and compresses log files.；Function A involves user permission checks and page rendering; Function B involves file I/O, compression, and archiving.；Function A uses servlet API (HttpServletRequest, HttpServletResponse); Function B uses file and compression APIs.；Function A has caching logic; Function B has archive deletion logic.
- 修正建议: Include more discriminative features for event-handling tasks.；Use broader context to differentiate between HTTP and file I/O handlers.

### case_id=5714 FP other

- 方法: `write` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Writes byte buffers through SSL engine, handling handshake and wrapping.
- B 摘要: Handles GUI action events for setting application preferences and file paths.
- 静态失败原因: Static BERT/GraphCodeBERT likely overfit to structural patterns like loops and exception handling, which appear in both but are generic, missing the vast difference in domain and data flow.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have completely different purposes (one is SSL data handling, the other is GUI event handling) with no meaningful shared functionality, even at a high level.
- 共享行为: Both contain loops and conditional checks；Both handle exceptions via try-catch
- 行为差异: A performs SSL encryption and buffer management; B manages GUI settings and file chooser dialogs；A returns ByteBuffer[]; B is void and updates UI components；A deals with network security; B deals with user configuration
- 修正建议: Incorporate data flow analysis to distinguish input/output types and transformations；Use longer-range contextual embeddings to capture overall function purpose；Add negative sampling with more diverse non-clone pairs to reduce false positives on unrelated functions

### case_id=5715 FN partial_functionality

- 方法: `fileDownload` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL and saves it to a local file.
- B 摘要: Reads a file from local filesystem or classpath and returns its content as a string.
- 静态失败原因: The low token Jaccard similarity (0.193) and different method names, coupled with distinct syntactic structures, likely caused the model to predict non-clone despite some behavioral overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone due to the common pattern of opening an input stream, reading data, and outputting it, despite different output destinations and sources. However, the low token similarity and different functional purposes suggest it might be a borderline case.
- 共享行为: Both functions read data from an external source (URL or file) using input streams.
- 行为差异: Function A writes data to a local file (download.pdf), while function B returns data as a string.；Function A uses URL connection; function B uses file or classpath resource.；Function A reads character-by-character; function B reads line-by-line.；Function A ignores the original filename from the URL; function B uses the given filename.
- 修正建议: Enhance model with data flow analysis to recognize functional similarities across different I/O patterns.；Include broader context like method name semantics and comment documentation.

### case_id=5716 FP lexical_or_api_overlap

- 方法: `getUser` vs `readVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves a User object by login, first checking a DAO, then parsing a config file if not found.
- B 摘要: Reads version metadata from a system resource file and sets instance variables.
- 静态失败原因: Static BERT likely overemphasized lexical and API-level overlap (BufferedReader, URL, parse loop) while missing the distinct high-level semantics and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because the overall functionality is different (user authentication vs version retrieval) despite similar I/O patterns.
- 共享行为: Both use BufferedReader to read from a URL resource line by line.；Both parse each line to extract specific information.；Both handle IOException and print stack traces.
- 行为差异: Function A returns a User object; function B is void and sets instance fields.；Function A first attempts to load via DAO; B directly reads a resource.；Function A parses lines with a specific pattern (colon-delimited tokens); B parses lines with key=value prefixes.；Function A may save a new user to DAO; B does not persist data.
- 修正建议: Incorporate structural or data-flow analysis to distinguish different processing logic.；Train or fine-tune on examples where API similarity does not imply semantic equivalence.；Use a more granular token similarity threshold or consider function name and return type.

### case_id=5717 FN benchmark_preference_bias

- 方法: `truncate` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Compresses and archives an old log file into a zip backup, then deletes the original.
- B 摘要: Downloads a WSDL file from a URL, modifies its endpoint, saves it locally, and returns the file path.
- 静态失败原因: The model detected low lexical overlap (Jaccard 0.105) and different API usage, correctly predicting non-clone; it could not infer the high-level functional similarity that BCB might have assumed.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'file processing with output generation' despite different transformations, accepting broad Type-4 similarity based on general file I/O and modification.
- 共享行为: Both read from a source (file or URL) and write to a destination file；Both involve conditional checks before processing (file age or existence)；Both use logging and exception handling
- 行为差异: A compresses data (zip), B downloads and modifies XML content；A deletes the original file, B does not delete the source；A uses ZipOutputStream and FileInputStream, B uses URL, ReadableByteChannel, and DOM parser；A returns void, B returns a String file path
- 修正建议: No fix needed if model's judgment is considered correct; for alignment with BCB, inject domain knowledge or use fine-grained functional categorization

### case_id=5718 FN benchmark_preference_bias

- 方法: `createHTML` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Builds an HTML page string by reading a CSS file and appending content based on a page type (logo or home), querying a database for dashboard content.
- B 摘要: Downloads and processes an OPDS catalog or book from an HTTP URL, handling redirects, content types, and iterating over next links.
- 静态失败原因: The model likely relied on low token/lexical overlap and distinct control structures, correctly predicting non-clone; the BCB label appears erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to shared use of URL/stream reading and HTML-related content, but this overgeneralizes; the core semantics are unrelated.
- 共享行为: Both read from a stream obtained via a URL；Both use try-catch for error handling；Both involve string concatenation for result building
- 行为差异: Function A constructs static HTML with SQL queries; Function B handles HTTP networking and file downloads；Function A has no network I/O beyond reading a local CSS file; Function B is entirely network-driven；Function A's output is a single HTML string; Function B's output involves callback and file saving；Control flow: A uses switch-case; B uses a do-while loop with state variables
- 修正建议: Improve training data quality to reduce mislabeled pairs；Use functional dependency or program flow analysis to distinguish different high-level purposes；Incorporate domain-specific knowledge to differentiate UI generation from network I/O

### case_id=5719 FP boilerplate_overlap

- 方法: `checkForUpgrade` vs `parse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Checks for software upgrades by querying a license server and updating a local database with upgrade information.
- B 摘要: Parses a structured data file (CSV-like) from a file or URL into a DataSet object, handling headers and data types.
- 静态失败原因: The static BERT model overemphasized shared I/O boilerplate (URL, BufferedReader, while loops) and ignored the distinct semantic contexts, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clones due to entirely different functionality despite some structural I/O similarity, as BCB focuses on functional equivalence or strong semantic similarity, which is absent here.
- 共享行为: Both use BufferedReader and InputStreamReader to read data from an external source (HTTP URL or file).；Both process input line by line using while loops.；Both perform string splitting and iterate over resulting arrays.；Both have conditional checks based on parsed data.
- 行为差异: Different domain: upgrade management vs data parsing.；Different output: void vs DataSet return.；Different control flow: license status checks vs tokenizer-based parsing.；Different data structures: SQL database and UI components vs DataSet and column headers.
- 修正建议: Incorporate method-level context (e.g., method names, class hierarchy) into representation.；Use control flow and data flow graphs to capture behavior beyond lexical tokens.；Apply project-level or domain-specific embeddings to differentiate common I/O patterns from actual semantic similarity.

### case_id=5720 FN benchmark_preference_bias

- 方法: `main` vs `readFixString`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, unzips it, and saves each entry to the local filesystem.
- B 摘要: Reads a fixed-length string from an input stream using IOUtils.copy and returns it as a String.
- 静态失败原因: Static BERT models typically rely on lexical overlap and structural similarity; the token and AST overlap is very low (Jaccard 0.088), so the model correctly (by standard metrics) predicted non-clone, but BCB's lenient annotation considered them clones due to a generic stream-handling pattern.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'stream I/O' utilities performing read/write operations, under a very broad notion of clone that overlooks the distinct application-level purposes.
- 共享行为: Both involve reading from an InputStream；Both handle IOExceptions；Both use byte/character buffers internally
- 行为差异: A writes to files, B writes to a StringWriter；A iterates over zip entries, B reads a single string；A uses ZipInputStream, B uses a generic limited InputStream；A outputs to console, B returns a String
- 修正建议: Increase threshold for functional similarity in BCB annotations；Incorporate high-level purpose alignment via documentation or API call context；Use data-flow analysis to differentiate sink and source operations

### case_id=5721 FN benchmark_preference_bias

- 方法: `download` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads a resource file from classpath to a user-selected file path via save dialog.
- B 摘要: Builds a website for editing by processing pages, transforming XML, and writing output files.
- 静态失败原因: The static BERT model correctly identified low lexical and structural similarity, but BCB's ground truth is likely erroneous or overly broad, causing a false negative relative to BCB.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both methods containing common boilerplate code for stream handling and exception management, which can be a basis for broad Type-3/Type-4 classification despite different high-level functionality.
- 共享行为: Both involve reading from an input stream and writing to an output stream.；Both handle IOException and close streams in finally blocks.
- 行为差异: Function A is a simple single-file copy; Function B is a complex multi-file site generation.；Function A uses a save dialog; Function B takes many parameters for paths and configuration.；Function A reads from classpath; Function B reads from files and performs XML transformations.；Function B has extensive logging and string manipulation; Function A does not.
- 修正建议: Train the model to disregard generic boilerplate and focus on core algorithmic logic.；Re-evaluate or filter BCB ground truth to remove pairs that only share trivial I/O patterns.

### case_id=5722 FN benchmark_preference_bias

- 方法: `send` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends an email with specified parameters, including charset, headers, priority, and attachments, using Jakarta Mail.
- B 摘要: Retrieves a resource from a URL, caching it to a local file, and returns an InputStream.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone (0) because lexical and structural overlap is minimal (Jaccard 0.0996); no obvious reason for false negative.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to a very broad interpretation of Type-4 similarity, possibly because both involve network resource access or because of common boilerplate like try-catch and stream handling.
- 共享行为: Both include I/O operations and exception handling
- 行为差异: A constructs and sends an email message; B downloads and caches a resource.；A uses Hibernate session and user identity; B uses URLConnection and local file cache.；A handles email headers and priority; B handles HTTP response codes and caching.
- 修正建议: Improve annotation consistency in BCB for Type-4 clones.；Add more diverse negative examples in training.

### case_id=5723 FP boilerplate_overlap

- 方法: `main` vs `convert`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses command-line arguments, reads a Prolog file, generates adapter code, and writes output to a JAR file.
- B 摘要: Converts an ACRNEMA stream file to DICOM format by parsing the input, manipulating medical image tags, and writing the output.
- 静态失败原因: Static models like GraphCodeBERT may over-rely on shared structural patterns (file reading, parsing, writing) and common API calls (File, InputStream, OutputStream, System.out) while missing domain-specific semantics, leading to false positives.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB usually labels non-clones when functions perform completely different task-domain operations despite sharing similar I/O boilerplate. The low token Jaccard (0.08871) confirms minimal lexical overlap.
- 共享行为: Both read input files and perform conditional checks before processing.；Both write output to files after transformation.；Both use try-catch-finally blocks for exception handling.；Both print diagnostic messages to System.out.
- 行为差异: Function A generates adapters for Prolog programs; Function B converts medical image formats.；Different domain-specific data structures and operations (Prolog classes vs DICOM tags).；Function A handles multiple command-line options and debug mode; Function B does not.；Function B has low-level pixel data manipulation; Function A deals with class generation and serialization.
- 修正建议: Incorporate finer-grained semantic analysis of domain-specific operations.；Use more discriminative features like method purpose from documentation or comments.；Apply stronger weighting to unique identifiers and domain terminology.；Train on a more balanced dataset with higher discrimination for boilerplate-heavy non-clones.

### case_id=5724 FN benchmark_preference_bias

- 方法: `doFinishLoadAttachment` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Loads an attachment and either saves it to external storage or opens it with an intent based on a flag.
- B 摘要: Handles an HTTP GET request to fetch and render a page, with access control and caching logic.
- 静态失败原因: Static BERT correctly predicted non-clone due to very low token overlap (0.071) and distinct vocabularies; it did not fail from a strict semantic viewpoint.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label 1 is likely a labeling error, as these functions share no meaningful semantic similarity; potential confusion due to both having file saving and error handling, but that is too superficial.
- 共享行为: Both involve file I/O operations；Both have error handling blocks
- 行为差异: Different domains: Android attachment handling vs Java servlet page request；Different inputs, outputs, and control flow；No overlap in core functionality
- 修正建议: Re-evaluate BCB annotation for this pair；Improve token-based similarity thresholds or incorporate semantic analysis

### case_id=5725 FN partial_functionality

- 方法: `doBody` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file's content to an HTTP response output stream.
- B 摘要: Modifies or adds a key-value entry in a localized properties file.
- 静态失败原因: Low token overlap and surface-level differences in method names and domain-specific terms prevented the model from recognizing underlying file I/O similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered both as Type-4 clones due to shared file manipulation patterns, despite different domain contexts.
- 共享行为: Both involve file I/O operations；Both have try-catch-finally blocks to handle exceptions
- 行为差异: Method A serves a file to an HTTP response; Method B edits a properties file；Method A uses IOUtils.copy; Method B manually reads/writes lines；Different input parameters and output purposes
- 修正建议: Enhance model with dataflow analysis to detect file I/O patterns；Use intermediate representation that abstracts common operations like reading/writing streams

### case_id=5726 FN other

- 方法: `login` vs `parse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Logs into LOLA by sending HTTP POST with email and password, returns session ID.
- B 摘要: Parses a data file (from URL or local) into a DataSet with headers and types.
- 静态失败原因: Static model correctly identified non-clone, so it did not fail; it disagreed with BCB label.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have considered both as operations involving network I/O and input reading, but the functional difference is substantial.
- 共享行为: Both use BufferedReader to read input；Both handle exceptions
- 行为差异: Purpose: authentication vs data parsing；Output: session string vs DataSet object；Complexity: simple HTTP request vs complex tokenizer parsing
- 修正建议: Review BCB annotation for potential mislabel；Improve model to handle broad BCB criteria by adding domain-specific features

### case_id=5727 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `handleHandshake`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks and their text from a given URL using regex and returns them as two vectors.
- B 摘要: Handles a Minecraft handshake packet by validating a server key and optionally authenticating via session.minecraft.net.
- 静态失败原因: Static BERT models likely overemphasized lexical and API overlap (URL, BufferedReader, InputStreamReader, etc.) and possibly similar control flow (reading from URL, loops, exception handling), while missing the vast difference in overall purpose and logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clones because they have completely different functionality and purpose, despite sharing some common APIs. BCB typically requires a higher level of semantic similarity, often involving same or similar functionality.
- 共享行为: Both use java.net.URL and java.io.BufferedReader to read content from a URL.
- 行为差异: Function A extracts links and returns structured data; Function B handles network game protocol and returns nothing (void).；Function A uses regex for parsing; Function B uses string comparison and exception handling.；Function A is a utility for web scraping; Function B is part of a game client's authentication flow.
- 修正建议: Train models to focus on higher-level semantics rather than low-level API usage.；Use dataflow or program dependency graphs to capture the actual computational intent.；Incorporate domain-specific knowledge to distinguish between different application domains.

### case_id=5728 FP boilerplate_overlap

- 方法: `readData` vs `bootKernel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses comma-separated strings to initialize sets and maps for Tibetan transliteration.
- B 摘要: Loads a configuration from assets, copies sdcard assets, and boots an Android kernel.
- 静态失败原因: The model likely overfitted to common structural patterns (e.g., while loops with iterators, try-catch) and ignored domain-specific context, causing a false positive despite low token Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these non-clones because the functionality is entirely unrelated; they do not perform similar tasks even at a high level.
- 共享行为: Both use try-catch blocks and loops
- 行为差异: Different purpose: data initialization vs. kernel booting；Different APIs: StringTokenizer vs. AssetManager, Log；Different domains: text processing vs. Android kernel
- 修正建议: Train on more diverse data to reduce reliance on boilerplate patterns；Incorporate program dependency analysis or dataflow features

### case_id=5729 FN partial_functionality

- 方法: `testNetworkHTTP` vs `sendRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends multiple HTTP GET requests to hardcoded URLs and discards the responses.
- B 摘要: Sends a single HTTP POST request with compressed XML data and parses the compressed response into a JDOM document.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token overlap and surface structure; the functions have very low token Jaccard similarity (0.09) and different control flows, so the model fails to detect the high-level semantic similarity recognized by BCB.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as Type-4 clones because they share the high-level concept of making an HTTP connection and reading the response, despite significant syntactic and functional differences.
- 共享行为: Both use URL and HttpURLConnection to make HTTP requests；Both read responses from input streams；Both handle IOException and disconnect the connection in finally block
- 行为差异: A uses GET requests; B uses a POST request；A does not send any data; B sends XML data with GZIP compression；A reads plain text responses; B reads compressed responses and parses XML；A is a void method; B returns a String (empty)
- 修正建议: Use graph-based models that capture data flow and API call sequences；Incorporate task-oriented embeddings that abstract common patterns；Enhance training with examples of Type-4 clones to improve semantic understanding

### case_id=5730 FP lexical_or_api_overlap

- 方法: `importSequences` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Imports FASTA sequences from a remote URL, parsing headers and sequences.
- B 摘要: Checks for new software version from a remote URL by parsing version/build numbers.
- 静态失败原因: Static BERT/GraphCodeBERT relied heavily on token overlap (URL, InputStream, readLine, IOException) and similar control flow, missing the semantic gap in domain-specific operations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because the core functionality differs entirely (biological sequence import vs. software version check), despite shared I/O patterns.
- 共享行为: Both open a URL stream and read data line by line；Both handle IOException with try-catch；Both parse specific prefix patterns from lines
- 行为差异: A parses FASTA sequences and stores them in lists; B parses version/build info and performs comparison；A uses ImportHelper class for reading; B uses BufferedReader directly；A has nested loops for reading; B uses a single while loop
- 修正建议: Incorporate dataflow analysis to distinguish how parsed data is used；Add domain-specific embeddings or use contrastive learning on similar API usage with different intents

### case_id=5731 FN partial_functionality

- 方法: `getResourceAsStream` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource from a URL, caches it locally, and returns an InputStream.
- B 摘要: Copies a file from a source path to a destination path.
- 静态失败原因: The model relied on low token overlap (Jaccard 0.224) and different method names/API calls, missing the shared stream-copying pattern that is not lexically evident.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers these clones because both implement the core pattern of reading bytes from an input stream and writing to an output stream with exception handling, which is a common reusable code snippet.
- 共享行为: Both read bytes from an input stream and write to an output stream using a while loop until end-of-stream.
- 行为差异: Function A performs network retrieval with caching and returns an InputStream; function B is a local file copy with no caching.；Function A uses Buffered streams and checks HTTP response codes; function B uses direct File streams.；Function A has complex conditional logic for cache handling; function B is straightforward.
- 修正建议: Incorporate dataflow analysis to detect generic IO streaming patterns.；Use graph-based representations that capture the read-write loop structure.

### case_id=5732 FP partial_functionality

- 方法: `handleHandshake` vs `executeHttpGet`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Validates a handshake packet by checking the username and optionally performs an HTTP GET request to authenticate with a Minecraft session server.
- B 摘要: Executes an HTTP GET request to a given URI and parses the response body as JSON.
- 静态失败原因: Static BERT methods may have focused on common keywords like 'HttpGet', 'BufferedReader', etc., and not captured the broader control flow and purpose. They might have overgeneralized the pattern of 'making HTTP request and reading response' as a clone.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality and purpose differ significantly. The HTTP GET part is a small fragment in A, while it's the entirety of B. The additional logic in A changes the semantic context.
- 共享行为: Both make an HTTP GET request and read the response line by line using a BufferedReader.
- 行为差异: A validates the input username before making the HTTP request; B directly makes the request.；A only reads the first line and checks if it equals 'ok'; B reads all lines and parses JSON.；A has network shutdown and packet sending logic; B returns JSONObject.；A uses java.net.URL; B uses Apache HttpClient.
- 修正建议: Improve the model's ability to understand the overall purpose and control flow, not just local patterns.；Use dataflow analysis to see that the HTTP part in A is conditional and leads to different outcomes.；Consider the domain context.

### case_id=5733 FN lexical_or_api_overlap

- 方法: `copyResource` vs `copyParseFileToCodeFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file, reading byte by byte.
- B 摘要: Copies a file from a specific path to another file using a buffered read.
- 静态失败原因: Low token-level similarity (Jaccard ~0.3) and different method names, control flow, and exception handling likely caused the static model to miss the clone.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often treats functions that perform the same high-level task (data copying) as clones even with implementation variations in error handling and reading method.
- 共享行为: Both copy data from an input source to an output file；Both close input and output streams after copying
- 行为差异: Function A reads byte-by-byte; Function B uses a buffer；Function A handles both URL and file sources; Function B only handles file sources；Function A throws generic Exception; Function B throws IOException
- 修正建议: Improve model to recognize data copying patterns despite different input handling；Use structural similarity or data flow analysis to capture the common read-write loop；Include more training examples with varying input sources and read methods

### case_id=5734 FN partial_functionality

- 方法: `doTransfer` vs `importRoles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an incoming HTTP request to another URL, copying headers and body, and returns the response.
- B 摘要: Reads XML from a URL, parses <RoleName> elements, and returns a list of RoleName objects.
- 静态失败原因: The static model likely relies on high token overlap and structural similarity; low Jaccard (0.1478) and differing API usage (HttpURLConnection vs URL.openStream) led it to classify as non-clone, missing the abstract 'network I/O' similarity that BCB emphasizes.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider both as 'URL-to-data-processing' tasks, emphasizing commonality in URL opening and data reading, and de-emphasizing the specific output logic.
- 共享行为: Both open a URL connection and read input data.；Both handle IOException and MalformedURLException.；Both use similar I/O patterns (InputStreamReader, BufferedReader).
- 行为差异: doTransfer acts as a proxy: forwards headers, writes request body, and returns response; importRoles only reads and parses XML.；doTransfer uses HttpURLConnection and handles HTTP methods and response codes; importRoles uses URL.openStream() and BufferedRreader.；doTransfer writes to response output stream; importRoles accumulates data in ArrayList.；The purpose is entirely different: servlet forwarding vs. XML role extraction.
- 修正建议: Incorporate higher-level task categorization (e.g., network I/O, data transformation) into training.；Use contrastive learning with functional labels to capture broader clone definitions.；Improve model's ability to abstract away from specific API calls to general behavior.

### case_id=5735 FP boilerplate_overlap

- 方法: `getUser` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves a user object by login, optionally loading from a config file if not found in database.
- B 摘要: Downloads content from a URL to a temporary file, with optional authentication and progress display.
- 静态失败原因: The model likely overemphasized the lexical overlap of BufferedReader, InputStreamReader, and the while-readLine pattern, mistaking boilerplate code for semantic similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically considers broad Type-3/4 similarity, but these functions have no shared core functionality beyond boilerplate I/O code, so they would be considered non-clones.
- 共享行为: Reads line-by-line from a stream using BufferedReader and InputStreamReader
- 行为差异: Different purpose: user authentication vs file download；Different input parameters and return types；A uses a StringTokenizer, B uses Base64 encoding；A saves to database, B writes to temp file and updates UI
- 修正建议: Incorporate deeper semantic analysis of method purpose, e.g., via method name and return type；Use data flow or program dependence graphs to distinguish control flow differences；Train on more diverse examples to reduce sensitivity to common structural patterns

### case_id=5736 FN benchmark_preference_bias

- 方法: `CopyTo` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file to a destination file using FileReader and FileWriter.
- B 摘要: Handles an HTTP GET request to retrieve and display a page, with logging and optional caching to a file.
- 静态失败原因: The model likely focused on token overlap (Jaccard=0.084) and overall structure, correctly identifying them as non-clones. It failed to match the BCB annotation, which may have been influenced by a bias towards file I/O patterns despite functional divergence.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled as clone due to both containing file I/O (FileWriter) and similar exception handling boilerplate, which can be seen as a partial functional overlap, but the overall functionality is vastly different.
- 共享行为: Both use FileWriter to write to a file；Both handle IOException and use try-catch-finally for resource cleanup
- 行为差异: Function A is a simple file copy; Function B is a complex web request handler；Function A reads from a FileReader; Function B reads from HTTP request parameters and database；Function A writes every byte from source; Function B writes a specific string (HTML) as part of caching；Function A has no logic beyond copy; Function B includes authentication, logging, exception handling, and response generation
- 修正建议: Consider that BCB labels may include Type-4 partial functionality; models should incorporate functional abstraction recognition beyond token overlap；Fine-tune on cases where weak file I/O similarity is not considered a clone；Use contextual understanding to distinguish between core behavior and auxiliary operations

### case_id=5737 FN partial_functionality

- 方法: `runScript` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script from a URL by appending scriptName to the codebase URL, reads bytes until EOF, and returns the entire content as a string, returning "error!" on exception.
- B 摘要: Overrides Runnable.run(), reads from a URL (urlInfo), parses lines into version, url, and informations fields, handles IOExceptions with specific messages, sets error flags, and notifies listeners.
- 静态失败原因: The token Jaccard similarity is low (0.1899), and the models rely heavily on surface-level token overlap. They miss the higher-level semantic similarity of URL I/O operations due to different APIs and control flow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a Type-4 clone because both involve fetching and parsing data from a URL, which is a semantically similar operation despite syntactic and implementation differences.
- 共享行为: Both fetch content from a remote URL over HTTP.；Both convert input stream to character data.；Both handle IO exceptions (though differently).
- 行为差异: A returns entire content as string; B parses lines into fields and does not return value.；A reads byte by byte; B reads line by line.；A's error handling is minimal (returns "error!"); B has complex error handling with multiple error types and listener notification.；A reads a script file; B reads a specific URL for update information.
- 修正建议: Incorporate data flow analysis to capture shared I/O patterns.；Use graph-based representations that abstract over specific library calls.；Train with more examples of partial functionality clones.

### case_id=5738 FP lexical_or_api_overlap

- 方法: `executePost` vs `retrieveTemplate`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Executes an HTTP POST request to a target URL with parameters and returns the response body as a string.
- B 摘要: Retrieves a cached template from a blog URL via HTTP GET, returning the content as a string.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overfitted on overlapping boilerplate tokens such as 'URL', 'BufferedReader', 'StringBuilder', and the common while loop pattern. It failed to capture the semantic differences in HTTP method, parameters, headers, exception handling, and caching behavior, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates these as non-clones because the overall functionality is fundamentally different: one is a generic HTTP POST executor, the other is a template retriever with caching. Even though both involve reading from a URL, the intent and operational details differ significantly, making them partial functionality at best but not similar enough for Type-3/4 clones under typical BCB guidelines.
- 共享行为: Both read from a URL over HTTP.；Both use BufferedReader to read lines from the response stream.；Both append lines to a StringBuffer/StringBuilder.
- 行为差异: HTTP method: POST vs GET.；Function A sends URL parameters in the request body; B does not.；A sets multiple request headers; B does not.；A returns null on exception; B throws an exception.
- 修正建议: Incorporate data-flow analysis to track how URL and parameters are used.；Consider method names and HTTP method strings as additional features.；Use AST-based diffing to detect structural changes like additional headers or connection management.；Augment training data with more examples of similar boilerplate but different API usage.

### case_id=5739 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `scrapeForIsbns`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter feed from a fixed URL using HttpClient and returns the entire response as a string.
- B 摘要: Scrapes ISBN-10 codes from a given URL by reading line by line, matching a regex pattern, and returns the count of matches with retry logic.
- 静态失败原因: Static models relying on token overlap and shallow structural patterns may be misled by common API usage (HttpClient, BufferedReader) and similar control flow, missing the divergent semantic intents.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions serve distinct functional purposes despite sharing low-level I/O patterns.
- 共享行为: Both open a URL to read data；Both read the input line by line using BufferedReader；Both handle IOException
- 行为差异: Different purpose: Twitter feed retrieval vs. ISBN extraction；Different URL handling: fixed vs. parameterized；Different processing: appending all lines vs. regex matching；Different return type: String vs. int
- 修正建议: Incorporate method name and docstring embeddings to capture intent；Use graph-based models that track data flow and I/O transformations；Train with more contrastive examples of similar API usage but different functionality

### case_id=5740 FP lexical_or_api_overlap

- 方法: `executePost` vs `issueCommandToServer`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends HTTP POST request to a given URL with URL-encoded parameters, returns response string or null on failure, and disconnects the connection.
- B 摘要: Sends a command to a server by constructing a query string with command and capsule JSON, using a predefined server URL, and returns response string, throwing IOException on failure.
- 静态失败原因: The static BERT model likely overestimated similarity due to high lexical and API overlap (URLConnection, OutputStream, BufferedReader, StringBuffer, etc.) and similar control flow. It may have focused on common boilerplate code and missed the nuanced differences in error handling and connection management.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this non-clone because of significant behavioral differences in error handling (return null vs throw) and resource management (disconnect vs none), despite similar overall structure. The differences affect reliability and exception semantics, which BCB considers important for functional equivalence.
- 共享行为: Both send data via HTTP POST；Both read response line by line using BufferedReader and accumulate into StringBuffer；Both return the accumulated response as a string
- 行为差异: A has explicit exception handling returning null; B throws IOException；A disconnects HttpURLConnection in finally; B does not disconnect；A uses HttpURLConnection with explicit setRequestMethod("POST"); B uses URLConnection with implicit POST via setDoOutput；A constructs URL from parameter; B uses a member field serverURL
- 修正建议: Incorporate dataflow analysis to track exception handling paths and resource management；Use graph-based representations that capture control flow and data dependencies more explicitly；Train on more examples that differentiate error-handling styles and connection patterns

### case_id=5741 FP boilerplate_overlap

- 方法: `setBundleInfoName` vs `readScalarpvviewerDocument`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a key-value file from a URL to set bundle names in a list.
- B 摘要: Reads an XML configuration file from a URL to initialize a scalar PV viewer application.
- 静态失败原因: The model focused on shared structural pattern (URL stream, while loop, readLine, IOException) and ignored completely different business logic and data processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely marks as non-clone because functionality is completely different; high-level intent and output are unrelated despite shared I/O boilerplate.
- 共享行为: Both read from a URL using BufferedReader and InputStreamReader；Both handle IOException in a try-catch block
- 行为差异: A processes key-value pairs, B processes XML；A updates BundleInfo objects, B updates UI components；A returns boolean, B returns void；A stops on null line, B stops on line starting with '%='
- 修正建议: Use representations capturing data flow or program dependence graphs；Train model to weigh core logic higher than boilerplate code；Incorporate semantics of APIs used beyond lexical overlap

### case_id=5742 FN boilerplate_overlap

- 方法: `fileDownload` vs `loadExistingAntlibs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL to a local directory by reading bytes from the URL connection and writing them to a file.
- B 摘要: Loads antlib definitions from classpath resources by reading lines from URL streams and invoking loadAntLib for each.
- 静态失败原因: Low token overlap (Jaccard 0.136) and different method names/structures led the model to miss the shared low-level I/O pattern, which is obscured by different surrounding logic.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider these clones because both involve similar I/O boilerplate patterns (URL, stream, reader, loop) and error handling, despite different high-level purposes.
- 共享行为: Both open a URL, create an InputStream, wrap with BufferedReader, and read data.；Both handle IOException via catch blocks.
- 行为差异: A writes bytes to a FileOutputStream; B parses text lines and calls loadAntLib with URI.；A deals with a single URL; B iterates over multiple resources from classloader.；A uses File and FileOutputStream; B uses URI and resolves relative paths.
- 修正建议: Use data-flow or control-flow features that capture the common I/O pattern.；Incorporate comment and method name semantics to infer similar intent.；Augment training with examples of different functionality but similar I/O boilerplate.

### case_id=5743 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `CopyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.5`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a localized properties file by reading, updating, or appending a message value.
- B 摘要: Copies a file from source to destination, creating parent directories if needed.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low token overlap and syntactic differences (different method names, libraries, exception handling). The model may not capture the functional similarity in the file copying subtask without understanding the dataflow or conditional logic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones because both functions involve a file copying step as part of their operation, and they share broad file manipulation functionality with error handling, fitting Type-4 partial functionality similarity.
- 共享行为: Both perform file I/O operations (read from a source file and write to a destination file).；Both check for file existence (destination file in A, parent directory in B).；Both close file resources after use.
- 行为差异: A's file copy is conditional (only if locale file missing) and part of a larger modification task; B always copies.；A processes text lines and modifies content; B performs raw binary copy.；A handles properties file format; B is generic.；A catches all exceptions; B throws specific exceptions and returns the destination path.
- 修正建议: Incorporate dataflow analysis to detect shared file I/O patterns.；Use contrastive learning to align functions with partial functional overlap.；Add heuristics for file copy operations as a clone indicator.

### case_id=5744 FN partial_functionality

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using byte-by-byte stream I/O.
- B 摘要: Copies a file to another file using FileChannel.transferTo for efficient copying.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap and structural similarity; the low Jaccard (0.175) and different APIs (InputStream vs FileChannel, URL vs File) cause the model to miss the semantic similarity. The models may also be biased by method signatures (private vs public static) and lack understanding of dataflow equivalence.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-3/Type-4 clones, where the core functionality (file copy) is the same despite differences in source type, I/O method, and API usage. The low token similarity (0.175) but shared semantic purpose justifies a clone label.
- 共享行为: Both copy the entire content from a source to a destination file；Both use file output streams to write the destination；Both handle resource cleanup (close streams/channels)
- 行为差异: Source A can be a URL or local file; Source B is always a local file；A uses InputStream/OutputStream byte-by-byte copying; B uses FileChannel.transferTo for potentially faster copying；A has instance dependencies (fields); B is static with explicit parameters；Error handling differs: A throws Exception; B wraps IOException in RuntimeException
- 修正建议: Incorporate dataflow analysis to recognize that both achieve the same file copy operation；Use graph-based representations that abstract away low-level I/O API differences；Train on more diverse clones that include different API implementations of the same functionality；Consider method-level context (e.g., source type) to handle partial functionality matches

### case_id=5745 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `copyFileChannel`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale by reading, replacing a message value, or appending if not found.
- B 摘要: Copies a file from source to destination using FileChannel, optionally preserving the modification time.
- 静态失败原因: Static BERT models rely on token overlap and data flow, which are low (Jaccard 0.13). The model focused on the different method names and specific I/O patterns, missing the broad file I/O purpose that BCB might accept.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might label these as Type-4 clones because both are general file manipulation utilities that read and write files, close streams, and are of similar length and structure, accepting partial functionality similarity.
- 共享行为: Both perform file I/O operations (reading and writing).；Both close resources in a finally or catch block.；Both use a loop for reading/writing data.
- 行为差异: A modifies text content of a properties file; B copies binary file content.；A reads lines and processes them line-by-line; B uses FileChannel.transferTo().；A writes a specific message value; B preserves modification time if flag is set.；A handles missing locale file by copying from default; B throws IOException on failure.
- 修正建议: Incorporate high-level purpose classification using code summaries or docstrings.；Use a task-specific representation that captures common I/O patterns.；Adjust clone thresholds to accommodate weak semantic similarity for utility functions.

### case_id=5746 FP partial_functionality

- 方法: `readZoneIDs` vs `import_hints`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads zone IDs from a resource file and returns a HashSet of integers.
- B 摘要: Imports hint pieces from a file by URL, parses structured input, and places pieces on a board, returning success boolean.
- 静态失败原因: Static BERT models (e.g., GraphCodeBERT) rely on code structure and token similarity. Both functions use similar I/O and parsing APIs (URL.openStream, BufferedReader, Integer.parseInt), which may dominate the representation. The model likely overlooked the high-level semantic differences in method signature (return type, side effects) and control flow (first-line count handling vs. simple loop).
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would likely not label these as clones because they have fundamentally different purposes and outputs: one is a simple file-to-collection utility, the other is a complex initialization method for a puzzle board. Their behavioral differences outweigh shared low-level I/O and parsing patterns.
- 共享行为: Both open a file/URL stream and read lines using BufferedReader.；Both parse integers from lines using Integer.parseInt.；Both use try-catch for exception handling.
- 行为差异: Function A returns a HashSet<Integer>; Function B returns a boolean and modifies board state.；Function A reads all lines into a set; Function B first reads a count line, then processes individual piece data with multiple fields.；Function A catches generic Exception and prints stack trace; Function B catches only IOException and returns false.；Function A uses Class.getResource; Function B uses URL with baseURL or FileReader depending on a boolean flag.
- 修正建议: Enhance model to incorporate return type and method purpose via data flow analysis.；Use type-aware embeddings that distinguish between collection-returning methods and state-modifying methods.；Train on more diverse examples where I/O patterns are present but overall semantics differ.

### case_id=5747 FN partial_functionality

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a hardcoded URL and extracts all zip entries to files.
- B 摘要: Copies a single file from source to destination using buffered streams.
- 静态失败原因: Static BERT likely focused on low token overlap (0.26) and specific differences like URL/zip handling, predicting non-clone, but BCB's broad definition considers the shared stream-copy pattern sufficient.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as stream-based I/O operations with buffer usage, labeling them as Type-4 semantic clones despite different specific tasks.
- 共享行为: Read bytes from an input stream and write to an output stream using a buffer.
- 行为差异: A handles HTTP protocol and zip entry extraction; B is a simple file copy.；A writes multiple files (one per zip entry); B writes a single file.；A uses ZipInputStream and hardcoded URL; B uses FileInputStream/FileOutputStream with parameters.
- 修正建议: Incorporate data-flow or semantic similarity measures that capture high-level I/O patterns.；Use transfer learning with BCB-style annotations to calibrate clone detection criteria.

### case_id=5748 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `lookupFutureEvents`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads integer IDs from a resource file and returns them as a HashSet.
- B 摘要: Fetches future events from a Meetup API, parses JSON, and returns a list of Event objects.
- 静态失败原因: The model likely focused on the overlapping lexical tokens (URL, openStream, readLine) and the common 'read data from URL' pattern, ignoring the vastly different semantics and output types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB emphasizes overall functionality similarity and would not consider trivial API usage as sufficient for a clone label, hence label 0.
- 共享行为: Both use URL objects to open an input stream and read lines of text.
- 行为差异: readZoneIDs reads from a local resource file; lookupFutureEvents makes an HTTP request.；readZoneIDs parses each line as an integer; lookupFutureEvents parses JSON and constructs Event objects.；readZoneIDs returns a HashSet<Integer>; lookupFutureEvents returns a List<Event>.；readZoneIDs has minimal error handling; lookupFutureEvents has detailed exception handling and parsing.
- 修正建议: Incorporate data flow analysis to distinguish between reading raw data vs. parsing structured data.；Use type information to differentiate output types (HashSet<Integer> vs List<Event>).；Integrate control flow features to capture exception handling differences.

### case_id=5749 FP partial_functionality

- 方法: `getContent` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Executes an HTTP request and returns the response content as a string.
- B 摘要: Constructor for a GUI browser that fetches URL content, optionally transforms XML with XSLT, and displays the result.
- 静态失败原因: The static model likely overemphasized lexical overlap (BufferedReader, StringBuffer, URL) and missed the vast contextual and structural differences. It failed to distinguish partial functionality from full semantic equivalence.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled non-clone because the functions belong to completely different domains (HTTP utility vs. GUI constructor) and their core purposes are unrelated, despite a minor shared pattern of reading from a stream.
- 共享行为: Both read from a URL or HTTP response stream；Both read lines and accumulate into a StringBuffer
- 行为差异: A is a stateless utility method; B is a constructor with GUI setup and event handling；A returns a simple string; B displays content in a JEditorPane and performs XML/XSLT transformation；A uses HttpClient; B uses URL.openStream() directly；B has extensive GUI code, window listeners, and error handling
- 修正建议: Incorporate method-level context (class, parameters, return type) into the model；Use a code clone detector that considers control flow and data dependencies beyond token overlap；Apply a threshold on structural similarity metrics beyond token Jaccard

### case_id=5750 FP lexical_or_api_overlap

- 方法: `getDatasetsList` vs `getLinksFromURLFast`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a list of dataset strings from a URL by appending '?server=list' and caches the result.
- B 摘要: Extracts hyperlinks and link texts from an HTML page by parsing anchor tags using regular expressions.
- 静态失败原因: The static model likely overemphasized lexical and API-level overlaps (URL, BufferedReader, InputStreamReader, readLine) and the general I/O pattern, while failing to capture the distinct semantic transformations and output types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because the core functionality differs: one is a dataset listing service with caching, the other is a web page link extractor. Despite both involving URL reading, the purpose and output are distinct, so BCB would not consider them functionally similar.
- 共享行为: Both open a URL connection and read from it using BufferedReader；Both involve reading textual data from a remote resource
- 行为差异: A returns a List<String> of dataset names; B returns a Vector[] containing links and texts；A caches results in a HashMap; B does not cache；A reads lines one by one; B reads the entire page into a buffer；A uses regex for parsing? No, A just reads lines; B uses regex to extract <a> tags
- 修正建议: Incorporate method names and return types as important features；Use data flow analysis to distinguish transformations (e.g., list accumulation vs. regex matching)；Consider caching behavior and synchronization as discriminators

### case_id=5751 FN partial_functionality

- 方法: `main` vs `load`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Main method that sends a POST request to RenRen API with specific parameters and prints the response.
- B 摘要: Load method that downloads XML from a pastebin URL using GET and returns the content as a string.
- 静态失败原因: Static BERT models rely heavily on token overlap and surface features; the low Jaccard similarity (0.163) and different method signatures likely caused misclassification. The models may struggle to recognize the shared structural pattern when tokens differ.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because they share a common code skeleton of URL connection, input stream reading, and line-by-line reading, which is a recognizable pattern even though the specific API and parameters differ.
- 共享行为: Both open a URL connection and read the response line by line using BufferedReader；Both handle IOException implicitly (A throws, B catches)
- 行为差异: A sends a POST request with many parameters, B sends a simple GET request；A prints output, B returns a string；A constructs URL with many parameters, B just appends id to a base URL；B shows a dialog on error, A throws exception
- 修正建议: Improve training data with more diverse Type-3/Type-4 clone pairs；Use models that capture control flow and data flow, not just token sequence；Incorporate structural embeddings or graph-based representations

### case_id=5752 FP lexical_or_api_overlap

- 方法: `main` vs `getResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter classes from a Prolog file.
- B 摘要: Returns an HTTP response byte array from a requested resource.
- 静态失败原因: The model likely overemphasized overlapping API tokens like 'ByteArrayOutputStream', 'IOUtils', 'IOException', 'PrintStream', and 'InputStream', which are common in many Java programs, leading to false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label non-clone because the functions have entirely different purposes (code generation vs HTTP response handling), despite sharing some I/O patterns.
- 共享行为: Both use I/O streams (ByteArrayOutputStream, InputStream, etc.)；Both handle exceptions；Both have conditional error output paths
- 行为差异: Function A processes Prolog files and generates Java classes; Function B processes HTTP requests and returns byte array；Function A writes to a file; Function B returns a byte array from memory；Function A involves complex code generation and reflection; Function B is a simple HTTP response handler
- 修正建议: Increase training data with negative examples that share library usage but have different semantics；Incorporate structure-aware features like abstract syntax trees or control-flow graphs；Improve tokenization to distinguish between routine I/O boilerplate and actual business logic

### case_id=5753 FN boilerplate_overlap

- 方法: `addIDs` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches metabolite data from a web service, parses HTML-like response to extract IDs and molecular weight, sets on row, returns score.
- B 摘要: Checks for new version by fetching version file from URL, parses version/build lines, displays message to user.
- 静态失败原因: Static BERT likely relied on token overlap and flow structure; the shared API calls (URL, BufferedReader, IOException) and control flow led the model to overestimate similarity while missing the distinct semantic goals.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider these clones due to the common pattern of fetching data from a URL, parsing lines, and handling I/O exceptions, which is a typical Type-3 clone in BigCloneBench's 'data fetch and parse' category.
- 共享行为: Open URL and read lines with BufferedReader；Parse lines by searching for specific patterns；Handle IOException with error message or logging；Use try-catch-finally pattern
- 行为差异: Different URL and query construction；Different parsing logic: HTML tags vs. line prefixes；Different side effects: sets row properties vs. shows UI messages；Different return type and value
- 修正建议: Incorporate data flow analysis to capture the actual usage of parsed data；Improve representation of domain-specific operations (e.g., setVar vs. GUIUtilities.message)；Use contrastive learning with hard negative examples that share API patterns but differ in intent

### case_id=5754 FP lexical_or_api_overlap

- 方法: `loadExistingAntlibs` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads antlib definitions from classpath resources using ClassLoader.
- B 摘要: Checks for software upgrade by querying a remote license server and updating a database.
- 静态失败原因: The model likely overemphasized superficial API overlaps (e.g., BufferedReader, InputStreamReader, URL) while ignoring the completely different domain logic, method names, and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because they have entirely different purposes and no significant shared functionality beyond generic I/O boilerplate.
- 共享行为: Both use BufferedReader and InputStreamReader to read textual input.；Both handle I/O exceptions (IOException) and wrap them in RuntimeException.；Both involve iteration over input lines or records.
- 行为差异: Function A reads local classpath resources; Function B performs HTTP requests and database operations.；Function A parses antlib URIs and loads Ant libraries; Function B processes upgrade data and updates a database table.；Function A is instance method; Function B is static.；Different external dependencies: ClassLoader vs URLConnection and database commands.
- 修正建议: Incorporate method-level semantics via context-aware embeddings or code summarization.；Use graph-based models that capture control and data dependencies to distinguish different functionalities.；Include method name and class context as features to reduce false positives from boilerplate overlap.

### case_id=5755 FN partial_functionality

- 方法: `main` vs `copyFileByNIO`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, unzips it, and writes each entry to a file.
- B 摘要: Copies a file using NIO FileChannel transferTo method.
- 静态失败原因: Static BERT models rely on token overlap (low Jaccard) and code structure; these functions have different method signatures, control flow, and library usage (URL, Zip vs FileChannel), making it hard to capture the high-level semantic similarity of I/O data transfer.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider both as I/O data transfer operations, but the specific functionality is very different. Possibly they are considered Type-4 clones due to similar data flow pattern of reading and writing bytes.
- 共享行为: Both involve reading data from an input source and writing to an output destination using Java I/O.
- 行为差异: Code A downloads from a URL and extracts a zip file entry by entry, while Code B copies a file entirely using file channels.；Code A is a specific main method with hardcoded URL and handles zip format, Code B is a generic method for copying any file.；Code A uses ZipInputStream and BufferedOutputStream, Code B uses FileChannel.transferTo.
- 修正建议: Improve training data with more diverse I/O patterns.；Use contrastive learning to focus on data flow rather than specific API calls.；Incorporate sequence of I/O operations as abstract semantic patterns.

### case_id=5756 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Validates a Minecraft handshake packet by checking username format and optionally authenticating via a session server, then either disconnects or sends a login packet.
- B 摘要: Extracts a fullscreen video URL from a YouTube page by parsing HTTP response for relevant parameters like video_id and t, then constructs the URL.
- 静态失败原因: Static BERT/GraphCodeBERT models may have been misled by surface-level lexical similarities such as URL, BufferedReader, try-catch patterns, and string manipulation, while ignoring the completely different purpose and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the functions have entirely different high-level functionality and no meaningful behavioral overlap beyond trivial use of common Java I/O classes.
- 共享行为: Both use URL and BufferedReader to fetch data over HTTP；Both include exception handling with try-catch；Both manipulate strings for parsing
- 行为差异: Different domain: Minecraft network protocol vs YouTube video extraction；Different purpose: handshake validation/authentication vs URL construction；Different control flow: conditional based on username vs parsing HTML lines；Different output: void (with side effects) vs String (full URL)
- 修正建议: Incorporate control flow and data dependency analysis to distinguish superficial API use from core functionality；Add contrastive learning with diverse negative examples that share APIs but differ in semantics；Use domain-specific pre-training or fine-tuning to capture intent

### case_id=5757 FP lexical_or_api_overlap

- 方法: `loadExistingAntlibs` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads antlib XML definitions from classpath resources by reading resource files and constructing URIs.
- B 摘要: Retrieves tickets for a specific queue from a request tracker system via HTTP API calls.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized lexical and API overlap (e.g., BufferedReader, InputStream, exception handling patterns) and structural similarity in control flow (loops, try-catch blocks), while missing the core semantic difference in what the functions actually do.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB (BigCloneBench) labels non-clones when functions have no semantic similarity in functionality, even if they share some boilerplate. These two functions have entirely different purposes and output types.
- 共享行为: Both utilize BufferedReader to read lines from an input stream.；Both perform I/O operations with resource management.
- 行为差异: Function A reads classpath resources (antlib files) while B makes HTTP requests to a remote server.；Function A processes antlib URIs and calls loadAntLib, while B parses ticket IDs and fetches individual tickets.；Function A throws RuntimeException on errors, while B returns null or throws custom exceptions.；The data structures and logic for handling results are completely different.
- 修正建议: Incorporate more dataflow or dependency analysis to differentiate variable usage and function calls.；Use function-level semantics (e.g., via code summarization) to capture domain-specific operations.；Train with more diverse examples that have similar boilerplate but different semantics as negative samples.

### case_id=5758 FN benchmark_preference_bias

- 方法: `readGeoParserResult` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads geo-parser results from a URL, builds XML request, parses XML response, extracts place names and gazetteer IDs, returns a collection of tuples, with retry logic and exception handling.
- B 摘要: Checks for new version by fetching URL, reads lines to extract version and build info, displays message or error, no retry, no collection return.
- 静态失败原因: Static BERT likely focused on low token overlap and syntactic differences, missing the abstract pattern of 'URL reading + line processing' that BCB might consider as clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both functions as clones because they both perform URL fetching and line-by-line reading, a common pattern, and the label is lenient towards partial functionality similarity.
- 共享行为: Both open a URL and read lines using BufferedReader in a loop；Both use try-catch for exception handling
- 行为差异: Function A builds XML, parses XML, and extracts nested data; Function B only reads simple line prefixes；Function A has retry logic; Function B does not；Function A returns a collection; Function B returns void and shows GUI messages；Function A handles multiple data structures; Function B is linear and simple
- 修正建议: Incorporate high-level pattern recognition for URL/IO operations；Train on more diverse clones including partial functionality similarity

### case_id=5759 FN benchmark_preference_bias

- 方法: `main` vs `testCopy_inputStreamToOutputStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its contents to files.
- B 摘要: Tests copying an input stream to an output stream and verifying content equality.
- 静态失败原因: The model correctly identified semantic divergence due to low token overlap and different structural patterns, but BCB's lenient labeling caused a false negative from BCB's perspective.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them clones because both perform stream copying operations, albeit in different contexts, accepting broad Type-4 similarity where data transfer from input to output is seen as functionally similar.
- 共享行为: Both involve reading from an InputStream and writing to an OutputStream.；Both process data in byte chunks.；Both use streams for I/O.
- 行为差异: A extracts ZIP entries to separate files; B copies entire stream to a byte array.；A handles network protocol and file I/O; B uses in-memory streams for testing.；A does not verify copied content; B has assertions for correctness.
- 修正建议: Improve BCB annotation consistency; consider that generic stream I/O alone is insufficient for clone classification.；Use stricter criteria for Type-4 clones to avoid over-generalization.

### case_id=5760 FP boilerplate_overlap

- 方法: `doVersionCheck` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for software version updates by reading a version URL and comparing build numbers.
- B 摘要: Constructor for a Swing browser that loads an HTML page from a URL, optionally transforming XML with XSLT.
- 静态失败原因: Static BERT likely over-relied on lexical and API-level overlap (URL, BufferedReader, try-catch) and ignored the fundamental difference in program goals and output behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because their overall functionality and purpose are entirely different; the only overlap is trivial I/O boilerplate.
- 共享行为: Both open a URL and wrap the input stream in a BufferedReader；Both handle IOException with error messages
- 行为差异: Function A is a static method for version checking; B is a constructor for a GUI component；A displays a message dialog; B builds a window with HTML content；A parses simple version/build lines; B parses XML and optionally transforms with XSLT；A uses jEdit properties; B sets up Swing components and listeners
- 修正建议: Incorporate data flow analysis to track the purpose of variables and method outputs.；Use functional similarity measures that go beyond token overlap, e.g., behavioral signatures or program slicing.；Train models on tasks that emphasize high-level semantic roles rather than surface syntax.

### case_id=5761 FN partial_functionality

- 方法: `read` vs `fetchUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads data from either a file or URL and returns a status code.
- B 摘要: Fetches the content of a URL and returns it as a string.
- 静态失败原因: The model likely focused on low token overlap and different return types, missing the structural similarity of URL connection, input stream, and try-catch pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because they both perform the core task of reading data from a URL (and possibly file) with error handling, despite differences in return type and input scope. The functional overlap in URL reading is considered significant.
- 共享行为: Open a URL connection and read data；Handle IOException gracefully
- 行为差异: Function A also supports local file input；Function A returns an integer status code, Function B returns the content string；Function A reads raw bytes via BufferedInputStream, Function B reads text lines via BufferedReader
- 修正建议: Enhance model to recognize partial functional overlap, e.g., by identifying common subpatterns like URL opening with error handling；Use data augmentation to teach model that different return types can still indicate clone

### case_id=5762 FN benchmark_preference_bias

- 方法: `readData` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Initializes multiple sets and maps from string tokens representing character categories and parses a file to populate lookup tables.
- B 摘要: Checks for software version updates by fetching a URL and comparing version strings, showing appropriate messages.
- 静态失败原因: Static BERT methods rely on lexical overlap and structural similarity; low token Jaccard (0.104) and large difference in function length led to a non-clone prediction, which aligns with our assessment that they are not clones.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled them as clones due to both involving reading and processing data in loops, and both having a file/network I/O aspect, despite the completely different application domains.
- 共享行为: Both read from input sources and iterate over lines or tokens；Both have error handling (IOException or exceptions)；Both use while loops for iteration
- 行为差异: Differing purposes: data initialization vs version check；Different input sources: string constants/file vs URL；Different output actions: populate data structures vs show UI messages；Different error handling styles
- 修正建议: Improve annotation consistency by considering semantic intent rather than superficial structural patterns；Provide clearer guidelines for distinguishing partial functionality clones from genuine Type-4 clones

### case_id=5763 FP boilerplate_overlap

- 方法: `copyFileTo` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file from source to destination using buffered I/O.
- B 摘要: Handles GUI action events to set various configuration preferences.
- 静态失败原因: The model likely relied on lexical/API overlap (e.g., 'File', 'IOException', 'InputStream') and common code patterns (while loops, try-catch), ignoring the vast difference in program logic and context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones for functions with no shared functionality; these two have entirely different purposes and no semantic overlap.
- 共享行为: Both involve file-related objects (File, FileInputStream/FileOutputStream in A; FileChooser, File in B).；Both use Java I/O and GUI libraries (but no functional overlap).
- 行为差异: A performs a straightforward file copy; B is a complex event handler with many conditions for different commands.；A operates on file streams; B interacts with Swing components and stores preferences.；A has no user interaction; B is driven by user actions and updates UI elements.
- 修正建议: Incorporate control-flow and data-dependency analysis to distinguish file I/O from GUI event handling.；Use semantic role labeling or functional summarization to capture intent.；Train on more diverse non-clones with low token overlap to reduce false positives.

### case_id=5764 FN partial_functionality

- 方法: `addIDs` vs `runScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads and parses metabolite information from a Golm database web service, extracting multiple identifiers and setting them on a PeakListRow.
- B 摘要: Downloads and returns the content of a script file from the applet's codebase as a string.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on token-level differences (low Jaccard 0.13) and unique domain-specific strings, failing to capture the common pattern of URL opening and stream reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'fetching data from a URL using Java's URL class and reading it', which could be seen as broadly similar functionality at a high level, possibly qualifying as a Type-3 clone despite differences in parsing and output.
- 共享行为: Both open a URL connection and read the input stream
- 行为差异: A parses the response for multiple fields and updates a row object; B returns the raw content as a string；A has complex conditional parsing; B has a simple read loop；A returns an integer score; B returns a String
- 修正建议: Incorporate structural similarity of control flow for network I/O；Use AST or CFG based features to capture URL/stream patterns；Add training examples where high-level task similarity exists despite different tokens

### case_id=5765 FP boilerplate_overlap

- 方法: `getUser` vs `readURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from DAO or falls back to parsing a configuration file from a URL, matching login and saving user.
- B 摘要: Reads lines from a URL and prints them to standard output.
- 静态失败原因: Static BERT/GraphCodeBERT may have overemphasized overlapping tokens like 'BufferedReader', 'readLine', 'url.openStream', and exception handling, while missing the divergent control flow and return type semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely annotates non-clones for pairs where the overall functionality differs significantly despite some shared low-level I/O patterns, as the core purpose diverges.
- 共享行为: Both open a URL and read lines using BufferedReader；Both catch exceptions and print stack traces
- 行为差异: A has conditional logic to parse tokens and create a User object; B simply prints lines.；A returns a User object; B returns void.；A interacts with DAO and has user-specific business logic; B has no such logic.；A uses StringTokenizer to split lines; B does not parse.
- 修正建议: Incorporate structural information such as control flow graphs or data flow to distinguish read-and-print from read-and-process.；Use method names and return types as signals.；Apply contrastive learning to penalize pairs with high API overlap but different logic.

### case_id=5766 FN partial_functionality

- 方法: `fileDownload` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL and saves it to a local file using character stream I/O.
- B 摘要: Reads a resource file from the classpath, parses it into sections delimited by '---', and validates the expected number of sections.
- 静态失败原因: Static models like GraphCodeBERT rely heavily on token overlap and structural matching; the low token Jaccard and differing method names/signatures caused it to predict non-clone, missing the high-level loop similarity that BCB values.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions share a common I/O pattern of opening a URL/resource and iterating through the stream, which is a typical Type-3 clone with similar control flow and structure despite different specific tasks.
- 共享行为: Both open a URL/resource and read characters via a BufferedReader and InputStreamReader.；Both use a loop to read data until the end of the stream is reached.；Both handle I/O related exceptions (one catches, one throws).
- 行为差异: A retrieves data from a URL parameter; B retrieves data from a classpath resource.；A writes all data to a file; B accumulates sections in a list in memory.；A processes raw bytes/characters; B processes lines and splits by a delimiter.；A suppresses exceptions via logging; B throws exceptions to the caller.
- 修正建议: Improve the model's ability to recognize common I/O patterns such as URL opening and stream iteration.；Include more diverse training examples where control flow is similar but specific operations differ.；Incorporate graph-based representations that highlight data flow from input to output, capturing the shared read-loop behavior.

### case_id=5767 FN partial_functionality

- 方法: `main` vs `getProjectTreeData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a hardcoded URL, extracts its zip entries, and saves each entry to a file.
- B 摘要: Downloads an XML file from a dynamically constructed URL, saves it to a temporary file, then parses the XML to extract project tree data and returns a 2D array.
- 静态失败原因: Static models like GraphCodeBERT often rely on token overlap and structural patterns. The low Jaccard similarity (0.1679) and different method names ('main' vs. 'getProjectTreeData') lead to a non-clone prediction. The model fails to capture the high-level I/O pattern due to surrounding code differences (zip extraction vs. XML parsing) that dominate the representation.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a clone because both functions implement the core pattern of downloading remote data and saving it to a local file, which is a significant structural and semantic overlap. The additional steps (unzip vs. parse) are considered extensions of the same high-level task.
- 共享行为: Both download a file from a URL using URL.openStream.；Both read the input stream in a buffer loop and write to a FileOutputStream.；Both use URL, InputStream, FileOutputStream, and byte buffers.
- 行为差异: A downloads a zip and extracts multiple files; B downloads XML and parses it for data.；A uses a hardcoded URL; B constructs URL with parameters.；A does not return data; B returns a 2D array.；Different exception handling styles; A uses catch for generic Exception, B has multiple catch blocks.
- 修正建议: Use data-flow analysis to identify common I/O patterns (URL open, stream read, file write).；Train models with contrastive learning on pairs sharing sub-functionality.；Incorporate functional semantics via API call sequences (e.g., URL.openStream -> FileOutputStream).

### case_id=5768 FP boilerplate_overlap

- 方法: `persist` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Persists a FreeFormConfigurable's configuration to a file by copying its input stream to a file output stream.
- B 摘要: Handles various UI action commands for a preferences dialog, saving multiple settings and updating UI components.
- 静态失败原因: The model likely overestimated similarity due to common boilerplate patterns (try-catch, file handling) and maybe shared I/O-related vocabulary, ignoring the vast difference in method purpose and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the methods implement completely different high-level functionalities: one is a generic persistence utility, the other is a UI event handler. Despite both involving persistence, their roles in the system are distinct.
- 共享行为: Both methods perform some form of data persistence (file I/O vs. preference storage).
- 行为差异: Code A saves a single configuration object to a file; Code B handles multiple unrelated commands and saves many preferences.；Code A is a simple file copy; Code B involves complex UI event handling, file chooser dialogs, and UI updates.；Code A uses a generic configurable; Code B is tightly coupled to a specific UI application (Suku).
- 修正建议: Improve training data to include more diverse non-clone pairs with similar code structure but different semantics.；Incorporate method-level context (e.g., class name, method name) to disambiguate purpose.；Use finer-grained semantic analysis that captures data flow and API usage patterns.

### case_id=5769 FP boilerplate_overlap

- 方法: `executePost` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Performs an HTTP GET request to Google Images, parses HTML to extract image URLs, and updates a UI component with the first image.
- 静态失败原因: The static model likely overfocused on common API calls (HttpURLConnection, BufferedReader, InputStreamReader) and structural patterns (open, read loop, close, exception handling), leading it to overlook the critical differences in request method, return type, and side effects. The lexical overlap in these boilerplate patterns caused a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have fundamentally different overall purposes (generic HTTP POST utility vs. specific Google Images search with UI update), even though they share boilerplate HTTP code. BCB annotations often require significant similarity in core functionality, which is absent here.
- 共享行为: Both open an HTTP connection to a URL；Both read the response line by line using BufferedReader and InputStreamReader；Both handle exceptions with try-catch blocks；Both close the reader and connection in finally or after use
- 行为差异: A uses POST method with request body; B uses GET method with query parameters in URL；A returns a String; B is void and sets UI elements；A sends urlParameters in the output stream; B does not send any data；A parses the response into a single string with carriage returns; B splits the HTML to extract image URLs
- 修正建议: Incorporate dataflow analysis to track how the response is used (returned vs. parsed for UI)；Add attention to request method (POST vs GET) and request properties；Consider return type and side effects as discriminative features；Use method names and their context to inform semantic differences

### case_id=5770 FP partial_functionality

- 方法: `readAndRewrite` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads a DICOM image, parses it, extracts pixel data, and writes it to an output file.
- B 摘要: Reads a configuration file of Tibetan/Sanskrit text mappings, tokenizes lines, and populates multiple sets and hash tables.
- 静态失败原因: The model may have been misled by the common 'read' prefix in method names and superficial I/O structure, failing to capture the deep semantic difference between DICOM image processing and text configuration parsing. It lacked the domain-specific context to distinguish them.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the two functions perform entirely different tasks: medical image I/O vs. text tokenization and mapping. Even under broad Type-4 functional similarity, they share no common purpose or output behavior.
- 共享行为: Both read data from files；Both parse the input into structured in-memory representations；Both use loops and conditional logic
- 行为差异: Function A handles medical image (DICOM) format; Function B handles human language (Tibetan/Sanskrit) text mappings；Function A writes output to another file; Function B only populates internal data structures；Function A uses specialized libraries (ImageIO, DcmParser); Function B uses StringTokenizer and basic file I/O；Function B is much longer and more complex with multiple sub-parsers for different token types
- 修正建议: Incorporate more context-specific embeddings (e.g., domain-specific pre-training)；Use data flow analysis to capture actual operations and transformations；Increase sensitivity to library API usage beyond surface-level names

### case_id=5771 FP partial_functionality

- 方法: `getRequestContent` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Fetches the first line of content from a given URL using HttpURLConnection.
- B 摘要: Constructor for a simple Swing web browser that loads a URL, optionally applies XSLT transformation, and displays the resulting HTML.
- 静态失败原因: Static models may overemphasize shared API patterns (URL, BufferedReader) and ignore the surrounding code that defines distinct behavior, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically requires significant functional overlap; here the functions are entirely different in purpose and complexity, so BCB would label as non-clone.
- 共享行为: Both read from a URL using BufferedReader and InputStreamReader.；Both use the URL class to create a URL object from a string.
- 行为差异: Function A returns only the first line, while B processes the entire content.；Function B is a constructor that sets up a GUI and handles XML/XSLT, whereas A is a simple utility method.；Function A uses HttpURLConnection; B uses URL.openStream().；Function B includes extensive error handling, GUI creation, and event listeners.
- 修正建议: Enhance training with more examples that distinguish utility methods from complex constructors.；Incorporate data flow or control flow analysis to capture overall semantics.；Use contrastive learning to reduce sensitivity to common I/O snippets.

### case_id=5772 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a localized properties file by adding or updating a message key-value pair, copying from an English file if the locale file doesn't exist.
- B 摘要: Runs the main method of a Weka experiment setup GUI, loading an existing experiment from file or creating a new one, and later optionally saving it on window closing.
- 静态失败原因: Static BERT/GraphCodeBERT focuses on high-level semantics and sees no functional overlap; the broad BCB definition requiring only partial similarity or generic file I/O behavior is not captured by the model, leading to false negative.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'modifying application configuration' since A modifies localization properties and B modifies an experiment configuration, despite very different implementations and domains.
- 共享行为: Both use try-catch exception handling；Both perform file I/O operations (reading/writing files)
- 行为差异: A operates on .properties files for localization; B operates on serialized Experiment objects and a GUI；A has no GUI; B sets up a JFrame with a SetupPanel；A modifies a single message; B handles full experiment lifecycle (load, display, save)；A uses Properties class indirectly via file parsing; B uses ObjectInputStream/ObjectOutputStream
- 修正建议: Include training examples that are functionally different but share abstract patterns like 'file reading/writing with exception handling'；Use contrastive learning to learn broader similarity notions from BCB-style annotations

### case_id=5773 FP lexical_or_api_overlap

- 方法: `sendPost` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request to a given URL with parameters and returns the response body as a string.
- B 摘要: Runs a thread that opens an HTTP GET connection to a fixed URL and reads the response without any processing.
- 静态失败原因: The model overemphasized surface similarities such as the use of URL, BufferedReader, and try-catch blocks, and the common pattern of opening a stream and reading lines. The token Jaccard similarity (0.2586) indicates moderate lexical overlap, which may have misled the model into ignoring critical semantic differences like HTTP method, data flow, and return type.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered these non-clones because the functions have distinct purposes (a generic POST utility vs. a specific void GET task) and differ in HTTP method, parameters, return value, and exception handling, making them semantically incomparable.
- 共享行为: Both open an HTTP connection to a URL；Both read the response line by line using a BufferedReader
- 行为差异: A uses POST method with parameters, B uses GET without parameters；A returns the response string, B discards it (void method)；A takes URL and param as arguments, B has a hardcoded URL；A uses HttpURLConnection with explicit output, B uses URL.openStream()
- 修正建议: Incorporate dataflow analysis to track whether the response is used；Consider method signatures (parameters, return type) in the representation；Use type-aware or API-call context analysis to distinguish POST vs GET；Add training examples highlighting such nuanced differences

### case_id=5774 FN partial_functionality

- 方法: `getResourceAsStream` vs `copyResourceToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource as an InputStream with caching and HTTP handling.
- B 摘要: Copies a resource to a file using IOUtils.copyStream.
- 静态失败原因: Low token Jaccard similarity (0.10) and different method names, variable names, and control flow structures. Static BERT models rely on surface-level token overlap and may not capture the underlying functional similarity of resource copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotates broad Type-3/Type-4 clones, considering functional similarity even with different signatures and additional logic. Both methods perform the core task of reading a resource and writing its data to an output, which qualifies as a clone under BCB guidelines.
- 共享行为: Both open an InputStream from a resource；Both write data to an output (file or stream)；Both handle resource cleanup (close streams)
- 行为差异: A returns an InputStream; B writes to a file and returns void；A includes caching logic and HTTP conditional requests; B does not；A uses manual buffered copy; B uses IOUtils.copyStream；A has extensive error handling with multiple close attempts; B uses finally block
- 修正建议: Incorporate AST or data flow features to capture resource access and I/O operations；Train on more examples of resource-copying or file-I/O patterns with varied signatures；Use graph-based representations to highlight common substructures like try-with-resources

### case_id=5775 FN partial_functionality

- 方法: `main` vs `saveFileData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its entries to the current directory.
- B 摘要: Saves file data to a destination file within a CMS, handling caching, image metadata, and cleanup.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on token overlap and syntactic structure, which are low (Jaccard=0.12766). The methods use different APIs (ZipInputStream vs FileChannel) and have distinct control flows, leading the model to classify them as non-clones. The model missed the high-level functional similarity in performing file I/O tasks.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered both methods as performing 'file data transfer' operations with similar I/O patterns, despite different contexts. The broad definition of Type-4 clones (functionally similar albeit different implementation) could include this pair due to shared low-level operations like reading and writing file bytes.
- 共享行为: Both read data from an input source and write to an output file.；Both use Java I/O streams and handle exceptions (throws Exception).；Both perform file I/O operations that may involve large data transfers.
- 行为差异: A downloads from a URL and extracts zip entries; B copies files within a CMS and manages versioning.；A uses ZipInputStream and BufferedOutputStream; B uses FileChannel.transferTo and manages caches.；A does not handle image metadata or cache invalidation; B checks for image files and sets dimensions, removes cached resources.；A outputs to entry names directly; B writes to specific destination files and handles newDataFile overwrites.
- 修正建议: Incorporate dataflow analysis to abstract file I/O operations.；Use graph-based representations to capture the common pattern of reading and writing data.；Train on examples with broader functional similarity definitions (Type-4).

### case_id=5776 FN benchmark_preference_bias

- 方法: `main` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Tests a custom StraightStreamReader by writing bytes 0-255 to a file and reading them back using various read methods, printing errors for mismatches.
- B 摘要: Downloads a KMZ file from a URL, opens a ZipInputStream, and extracts all entries to files using a buffer.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low token overlap and differing control flow structures, correctly identifying them as non-clones despite BCB's label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as I/O-intensive tasks that read from an input and write to an output, possibly as Type-4 clones (different implementations, similar functionality) based on the high-level pattern of stream copying.
- 共享行为: Both involve reading from an input stream and writing to an output stream.；Both use byte arrays for buffered I/O.；Both handle I/O operations within a try-catch or throws context.
- 行为差异: Function A writes predetermined byte values to a file for testing, while Function B reads and extracts zip entries.；Function A uses multiple read methods (single-byte, buffered, offset) for verification, Function B uses a simple standard buffer read loop.；Function A operates on a local file, Function B downloads from a URL and handles zip decompression.；Function A deletes the file afterwards; Function B does not.
- 修正建议: Incorporate control flow and data flow analysis to distinguish between testing and extraction logic.；Use more granular clone type definitions to avoid over-broad Type-4 labeling.

### case_id=5777 FN partial_functionality

- 方法: `fileDownload` vs `getPagina`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads content from a URL and writes it to a file named download.pdf in a specified directory.
- B 摘要: Fetches content from a URL, optionally using authentication, and returns it as a concatenated string.
- 静态失败原因: The static model likely relied on token overlap (Jaccard 0.24) and surface-level differences (method names, return types, I/O classes) without recognizing that both functions share the core intent of downloading content from a URL. The model may not capture the high-level semantic similarity due to the divergent output destinations and specific code details.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often annotates Type-3/Type-4 clones based on similar functionality and control flow. Both functions perform HTTP GET requests and process the response, using similar APIs (URL, BufferedReader) and exception handling structures. The differences in output handling (file vs string) and minor reading styles are typical of partial functionality similarity accepted in BCB.
- 共享行为: Both open a URL connection and read data using a BufferedReader；Both handle exceptions with try-catch blocks；Both read input until the stream ends；Both close the reader after reading
- 行为差异: A writes the downloaded content to a file; B returns it as a string；A reads character-by-character; B reads line-by-line；A uses a fixed output filename (download.pdf); B concatenates lines into a result string；B sets a default Authenticator; A does not
- 修正建议: Train on more diverse clone pairs that include partial functionality overlap；Incorporate dataflow or dependency analysis to identify common operations like URL fetching；Use code summarization techniques to capture high-level intent；Focus on the shared API usage pattern (URL, BufferedReader, stream reading) as a strong clone indicator

### case_id=5778 FN partial_functionality

- 方法: `loadMFileViaWeb` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads an M-file from a web URL, reads its content line by line with newlines appended, parses it into a UserFunction object, and returns it.
- B 摘要: Reads a file from local filesystem or classpath resource, concatenates its lines without newlines, and returns the content as a single String.
- 静态失败原因: Static model likely relied on token/structural similarity, which is low (0.21 Jaccard). It didn't capture the underlying I/O pattern similarity. Different names, return types, and error handling may have caused non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as Type-4 clones because both are utilities that read a text resource from some source and process lines. The structural similarity (BufferedReader loop) might be considered sufficient for a clone label in BCB's annotation guidelines, which sometimes accept partial functionality overlap.
- 共享行为: Both read a text file line by line using BufferedReader and InputStreamReader；Both handle IO exceptions and close the reader
- 行为差异: Source of input: URL vs local file/classpath；Output: UserFunction vs String; newlines appended vs not；Error handling: throws MathLibException vs prints and exits；Overall purpose: loading a specific file type for parsing vs general file-to-string conversion
- 修正建议: Use data augmentation to include more examples of similar I/O patterns with different post-processing；Incorporate program dependency graphs or dataflow to capture the common reading structure；Add contrastive training on pairs that share sub-patterns

### case_id=5779 FP boilerplate_overlap

- 方法: `readZoneIDs` vs `callService`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads zone IDs from a resource file, parses each line as integer, and returns a set of integers.
- B 摘要: Reads a URL response, concatenates lines into a string, and stores the result in a field variable.
- 静态失败原因: Static BERT may rely on high token overlap (URL, openStream, readLine, try-catch) and ignore the divergent data flow and return semantics, leading to false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the overall functionality is different: one parses numbers from a file, the other reads a web service response. Despite shared I/O boilerplate, the core purpose and output type differ significantly.
- 共享行为: Both open a URL and read lines using openStream()；Both use a loop to read lines until null；Both have exception handling (catch blocks)
- 行为差异: Function A returns a HashSet<Integer>; Function B returns void and sets a field；Function A parses lines as integers; Function B concatenates lines into a string；Function A uses LineNumberReader; Function B uses BufferedReader；Function A reads from a resource path; Function B constructs URL from member variables
- 修正建议: Incorporate data-flow analysis to track how data read from stream is processed；Add features like return type, field writes, and method signature patterns；Use graph-based representations that capture control and data dependencies beyond token sequences

### case_id=5780 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `sendPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a file containing integer zone IDs and returns them as a HashSet.
- B 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- 静态失败原因: The static BERT model likely overfocused on shared API tokens like 'URL', 'InputStreamReader', 'readLine', and the while-loop pattern, ignoring the larger semantic difference in I/O direction and data transformation.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels as non-clone when the core functionality differs significantly despite structural overlap. Here, one is a resource file parser and the other is an HTTP client, so BCB annotators likely deemed them non-clones.
- 共享行为: Open a URL connection；Use InputStreamReader and readLine() in a while loop；Handle exceptions with try-catch；Return a result from the method
- 行为差异: readZoneIDs reads from a local class resource, while sendPost communicates over HTTP；readZoneIDs parses each line as an integer and adds to a set, while sendPost sends data via POST and concatenates response lines；sendPost sets request properties and uses PrintWriter; readZoneIDs does not
- 修正建议: Train with more diverse examples to reduce reliance on surface-level API overlap；Incorporate data flow or control flow analysis to distinguish read vs write operations；Add negative mining of pairs with high structural similarity but different end goals

### case_id=5781 FP lexical_or_api_overlap

- 方法: `getFrameworkFactory` vs `sendRequestObjectResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads an OSGi FrameworkFactory by reading a services file and instantiating the specified class.
- B 摘要: Sends an HTTP request with XML data to a server, saves the response to a file, and opens it in a browser.
- 静态失败原因: The static model likely overemphasized lexical overlaps like 'URL', 'openStream', 'BufferedReader', and common control flow patterns, ignoring the distinct overall purpose and logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled 0 because the core functionality is completely different; one is a factory lookup, the other is a network communication method. Even with some shared I/O patterns, they are not semantically similar.
- 共享行为: Both use URL loading；Both involve I/O streams；Both have try-catch blocks
- 行为差异: A is a static factory method; B is an instance method sending network requests；A uses class loader and reflection; B uses HTTP connection, GZIP compression, and file I/O；A throws an exception; B returns a filename and shows browser
- 修正建议: Incorporate structural analysis (e.g., AST, data flow) to capture method intent；Use type and return value checks to differentiate factory vs. network methods；Train on more diverse negative examples with high lexical overlap but different semantics

### case_id=5782 FP other

- 方法: `actionPerformed` vs `readAndRewrite`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles GUI action commands for setting application preferences, including file paths and other settings.
- B 摘要: Reads a DICOM file, parses pixel data, and writes it to another file.
- 静态失败原因: Likely misled by presence of common file-related tokens (File, putPref) or similar control flow patterns (if/else), leading to false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would label as non-clone because methods have completely different functionality and domain, despite superficial file I/O commonality.
- 共享行为: Both perform file I/O operations (read/write files)
- 行为差异: A is a GUI event handler for preference settings; B is a static utility for DICOM image conversion.；A deals with various commands and updates UI components; B processes DICOM metadata and pixel data.；A involves user interaction via JFileChooser; B works directly with file streams.
- 修正建议: Improve model's ability to distinguish domain-specific operations.；Use structural analysis beyond token overlap.；Incorporate more context (e.g., class name, imports).

### case_id=5783 FP boilerplate_overlap

- 方法: `getURLContent` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens a URL connection and reads the entire content as a string using BufferedReader, appending newlines.
- B 摘要: Sends an HTTP POST request with parameters and reads the response as a string using BufferedReader, appending carriage returns, with exception handling.
- 静态失败原因: The static model likely overemphasized the common boilerplate code for reading HTTP responses (URL, BufferedReader, while loop, StringBuilder) and ignored the significant differences in HTTP method setup and parameter handling, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions perform fundamentally different HTTP operations (GET vs POST) with distinct input parameters and error handling, making them functionally different despite shared reading boilerplate.
- 共享行为: Open a URL connection to a given URL；Read response line by line using BufferedReader；Accumulate lines into a StringBuilder/StringBuffer；Close the reader and connection
- 行为差异: Function A uses GET method; B uses POST；Function A reads content-encoding; B does not；Function B sends URL parameters via DataOutputStream; A does not；Function A appends '\n'; B appends '\r'
- 修正建议: Represent HTTP method and request setup more explicitly in the code representation；Downweight common I/O patterns that appear across many URL reading functions；Use dataflow analysis to distinguish how the URL connection is configured

### case_id=5784 FP long_range_semantics

- 方法: `actionPerformed` vs `doPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles GUI action events to set file paths for external tools (GraphViz, ImageMagick) and update UI preferences.
- B 摘要: Handles HTTP POST requests to process multipart file upload and generate a mailer output.
- 静态失败原因: The static BERT model likely focused on superficial similarities like presence of try-catch blocks, stream handling, and multiple conditional branches, ignoring the different context (Swing vs Servlet). The truncated long code A might have led to fragmented pattern matching.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels non-clones when functions have completely different domain, purpose, and control flow, even if both involve file I/O. The low token Jaccard and different method names support non-clone.
- 行为差异: Function A is a Swing event listener; Function B is a servlet HTTP handler.；A manipulates UI components and stores preferences; B processes file uploads and streams output.；A uses JFileChooser and Suku.kontroller; B uses ServletFileUpload and IOUtils.；A's control flow depends on action commands like 'GRAPHVIZ'; B's control flow depends on multipart field names.
- 修正建议: Incorporate structural information like method signatures, class context, or call hierarchies.；Use fine-grained semantic role labeling to distinguish UI event handling from HTTP request processing.；Improve handling of long code by summarizing or using hierarchical embeddings.

### case_id=5785 FN lexical_or_api_overlap

- 方法: `login` vs `getNetworkServersIPs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into a web service by sending credentials and extracting a session ID from the response.
- B 摘要: Retrieves a list of server IPs from a configuration file hosted at a URL.
- 静态失败原因: The static BERT model likely relied on token-level similarity, which is low (Jaccard=0.2267) due to different method names, variable names, and logic. It failed to capture the high-level structural similarity of the URL reading pattern, leading to a false negative prediction.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as clones under a broad Type-4 definition because they both involve network I/O, reading data from a URL, parsing lines, and returning extracted information. The similar boilerplate code for URL connection and buffered reading might be deemed sufficient for a clone label in BigCloneBench.
- 共享行为: Both open a URL connection；Both read lines using BufferedReader；Both iterate over lines and perform parsing；Both handle IO exceptions
- 行为差异: login sends a POST request with form data, while getNetworkServersIPs only reads；login extracts a session ID from the first line, while getNetworkServersIPs parses multiple lines for IP addresses；login uses OutputStreamWriter to write data, getNetworkServersIPs does not write
- 修正建议: Incorporate structural or data flow features to capture common API usage patterns；Use models that are more robust to token-level variation, such as GraphCodeBERT；Add training data that emphasizes broad functional similarity over exact token matches

### case_id=5786 FN benchmark_preference_bias

- 方法: `logging` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Logs inbound messages by copying input stream to cached output stream, handling encoding and headers, with optional truncation.
- B 摘要: Launches a NexOpen project configuration by processing pom.xml files, handling Hibernate dialect, and copying reverse engineering resource files.
- 静态失败原因: Static BERT models rely on token and structural similarity, which is low (Jaccard=0.092); they missed the broader functional pattern of stream copy because of different method names, contexts, and APIs.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label as clone due to shared sub-pattern of input-to-output stream copying with error handling and logging, which qualifies as Type-4 partial functionality similarity.
- 共享行为: Both copy data from an InputStream to an OutputStream using IOUtils.copy；Both handle IOExceptions by throwing a Fault or RuntimeException；Both involve logging or debug output；Both use ByteArrayOutputStream or similar buffered output
- 行为差异: Different overall purpose: logging vs. project launch；Different data types: network message vs. XML/properties；Logging uses CachedOutputStream with temp file and truncation; launch uses ByteArrayOutputStream and file creation；Launch has complex configuration logic; logging is simpler
- 修正建议: Train with more Type-4 examples that share sub-functionality；Incorporate data-flow or usage patterns of common utility methods (e.g., IOUtils.copy)；Consider multi-level representation that captures partial functionality

### case_id=5787 FN partial_functionality

- 方法: `getFile` vs `fetchURLData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint in the XML, and saves to a temporary file, returning the file path.
- B 摘要: Fetches data from a URL (supporting HTTP and file protocols with optional proxy) and returns the data as a byte array.
- 静态失败原因: Static BERT models rely on token overlap and structural patterns; low Jaccard (0.12) and differing details (XML parsing, file I/O vs. HTTP proxy) cause the model to miss the shared semantic of URL fetching.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers this a clone because both functions share the core behavior of downloading data from a URL, which is a common functional similarity recognized in Type-4 clones.
- 共享行为: Open a URL connection to download data from a remote source；Handle IO streams and exceptions
- 行为差异: A writes to file and modifies XML; B returns byte array；A uses specific debugging logs and catches multiple specific exceptions; B supports proxy and file:// protocol；A's purpose is WSDL processing; B is generic fetch
- 修正建议: Enhance model to recognize common sub-tasks like URL streaming；Incorporate data flow analysis to trace input-output patterns；Train on more diverse examples of functional similarity

### case_id=5788 FP lexical_or_api_overlap

- 方法: `run` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a resource file from classpath and sets UI text asynchronously in Swing.
- B 摘要: Reads first line from an HTTP URL and returns it as a string.
- 静态失败原因: High lexical overlap (URL, BufferedReader, InputStreamReader, readLine) misleads the model into thinking they are similar.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers non-clone because the functions have different inputs, outputs, and side effects, despite shared API usage.
- 共享行为: Both open a URL/connection and use BufferedReader to read text.
- 行为差异: A reads all lines from a classpath resource, B reads only first line from an HTTP URL.；A updates UI via invokeLater, B returns a string synchronously.；A swallows exceptions, B throws Exception.
- 修正建议: Incorporate data-flow and output type differences.；Use graph-based models to distinguish usage patterns.；Focus on functional behavior rather than library calls.

### case_id=5789 FN partial_functionality

- 方法: `setBundleInfoName` vs `fileDownload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL containing bundle info lines and updates a list of BundleInfo objects with name mappings.
- B 摘要: Downloads a file from a URL and writes it to a local directory.
- 静态失败原因: The model likely focused on the high lexical dissimilarity (low Jaccard score) and different high-level purposes (parsing vs downloading), missing the shared substructure of URL reading and exception handling. It failed to recognize the partial functionality overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a Type-4 clone because both functions share the common pattern of opening a URL connection and reading data, even though the subsequent processing differs. The underlying I/O functionality is similar.
- 共享行为: Both establish a URL connection and read data from it using BufferedReader.；Both handle I/O exceptions via try-catch blocks.
- 行为差异: A reads lines and parses key-value pairs to update a list; B reads raw bytes and writes them to a file.；A returns a boolean indicating success; B returns void and logs errors.；A processes structured text data; B treats data as binary.；B creates a local file and writes to it; A only modifies in-memory objects.
- 修正建议: Enhance the model to detect common I/O idioms and structural patterns (e.g., URL opening + reading).；Incorporate data-flow analysis to identify shared operations on streams.；Use contrastive learning on pairs that share partial functionality but differ in specifics.

### case_id=5790 FP lexical_or_api_overlap

- 方法: `run` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a tile from a data source, reads JSON, creates geometry collection, and adds to a data loader.
- B 摘要: Reads configuration from a URL, parses lines into version/url/info variables, handles errors, and notifies listeners.
- 静态失败原因: Probably due to lexical overlap (both have 'run', 'BufferedReader', 'URL', 'IOException', 'readLine', loops). The models focused on common tokens and boilerplate structure, ignoring the different surrounding logic and ultimate purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely annotated as non-clone because the functions have different overall goals (tile loading vs. configuration parsing) and different outputs. Despite both involving reading from a network/file and processing lines, the processing logic is distinct and the context of use is different.
- 共享行为: Override run()；Read from a URL/file using BufferedReader；Handle IOException and FileNotFoundException；Loop reading lines until null
- 行为差异: A checks for duplicate keys using synchronization; B does not；A constructs geometry objects and adds to data loader; B parses lines into version/url/info and notifies listeners；A handles file and http protocols; B only uses URL.openStream()；A has error handling with logging; B uses French error messages and sets error flags
- 修正建议: Focus on concrete semantics like what data is read and how it is processed；Use data flow analysis to track how input is transformed into output；Consider the broader context (fields, methods called) to differentiate goals；Train models to recognize that boilerplate patterns (e.g., read lines, catch exceptions) are common across many unrelated functions

### case_id=5791 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Check for a new version of jEdit by fetching a version file from a URL and comparing build numbers.
- B 摘要: Search for album art images from Google Images by parsing HTML results.
- 静态失败原因: Static BERT or GraphCodeBERT may have focused on the structural similarity of URL opening and reading loops, overlooking the distinct semantic intent, or may have been misled by common library usage patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the high-level functionality is completely different; they only share boilerplate HTTP/IO code which is not sufficient for a functional clone in BCB's evaluation.
- 共享行为: Both open a URL and read lines of text；Both perform string parsing on the fetched data；Both handle IO-related exceptions
- 行为差异: One checks for software version updates; the other retrieves image URLs from a search engine；Different URL construction and property retrieval；Different string parsing logic (startsWith vs substring vs split)；Different UI feedback (wait cursor vs adding to a list and error dialog)
- 修正建议: Inject data flow awareness to distinguish variable usage contexts；Enhance the model with semantic role labeling to differentiate between generic IO and domain-specific parsing；Add type information and external knowledge about method names and library functions

### case_id=5792 FN partial_functionality

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its XML endpoint, and returns the file path.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: Low token overlap (0.102) and different method names led static BERT to miss the structural similarity in file copying logic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered the core file transfer via FileChannel as a common sub-behavior, labeling them Type-4 clones despite different overall functionality.
- 共享行为: Both use FileChannel to transfer data between streams；Both handle file I/O operations
- 行为差异: getFile downloads from a remote URL and modifies XML, whereas copyFile is a straightforward file copy；getFile creates temporary files and handles cleanup；Different error handling and method signatures
- 修正建议: Incorporate dataflow analysis to capture shared sub-steps；Use a model that abstracts variable names and focuses on API call sequences

### case_id=5793 FN partial_functionality

- 方法: `getHTML` vs `import_hints`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads HTML content from a URL and optionally writes it to a file, returning the HTML as a string.
- B 摘要: Imports puzzle hints from a file (possibly via URL) by parsing integer coordinates and placing pieces on a board, returning success status.
- 静态失败原因: The static BERT model likely relied on token-level similarity and syntactic structure. The token Jaccard similarity is very low (0.14), and the method names and variable types differ significantly. The model may not capture the high-level 'URL reading' pattern due to lack of training on such broad semantic clones.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BigCloneBench often marks Type-4 clones as positive, especially when functions share a common high-level pattern (e.g., reading from a URL using BufferedReader) despite different application logic. Both functions implement the 'read from URL' pattern, which BCB considers a clone at a broad level.
- 共享行为: Both functions create a URL and open an input stream to read data；Both wrap the stream in a BufferedReader and read lines in a loop；Both handle IOException and suppress exceptions；Both use similar boilerplate for I/O operations
- 行为差异: Function A returns the downloaded HTML string; Function B returns a boolean and modifies internal game state；Function A supports an encoding parameter and optional file writing; Function B does not；Function A uses HttpURLConnection with a User-Agent header; Function B uses URL.openStream() directly；Function B parses structured data (first integer count, then coordinates/rotation) using StringTokenizer; Function A just appends raw lines
- 修正建议: Train the model to recognize common I/O patterns (e.g., URL reading) across different tasks；Incorporate control-flow and data-flow analysis to detect similar resource acquisition and reading structure；Add examples of Type-4 clones in the training data with low lexical overlap

### case_id=5794 FN benchmark_preference_bias

- 方法: `scrapeForIsbns` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Scrapes ISBN-10 codes from a URL with retry logic and returns count.
- B 摘要: Reads a file or URL stream and returns a status code after delegating to another read method.
- 静态失败原因: Given that our analysis agrees with static prediction (non-clone), the model did not fail; it correctly predicted non-clone. The BCB label is likely a false positive due to broad clone definition.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone because both involve reading from a URL and returning an int, but the functional purpose and logic are very different; BCB sometimes accepts broad Type-4 clones based on similar I/O operations.
- 共享行为: Both open an input stream from a URL；Both return an int
- 行为差异: A specifically extracts ISBN patterns using regex, B does not parse content；A has retry logic with exponential backoff on connection failures, B does not；A reads line by line, B likely reads bytes；A uses a shared collection outputIsbns, B sets status field
- 修正建议: Re-evaluate BCB label for this pair; likely should be non-clone；Improve model to handle partial functionality by considering structural similarity in I/O patterns, but in this case model was correct

### case_id=5795 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Modifies a specific message in a locale-specific properties file, creating default from English if needed.
- B 摘要: Reads a DICOM image file and writes its pixel data to another file.
- 静态失败原因: The model correctly predicted non-clone due to low lexical overlap (Jaccard 0.05) and completely different semantics, but BCB's erroneous label caused a false negative classification.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Likely a labeling error in BCB, as only superficial file I/O similarity exists, which is insufficient for even broad clone detection.
- 共享行为: Both involve reading a file and writing a modified version to another file.
- 行为差异: Different file formats (properties vs DICOM medical image)；Different processing logic (string replacement vs pixel data copying)；Different libraries and domain-specific APIs；Different exception handling (Exception vs IOException)
- 修正建议: Review BCB annotations for consistency and correctness；Incorporate domain-specific knowledge to avoid superficial similarity mislabeling；Use functional similarity metrics beyond token overlap

### case_id=5796 FN benchmark_preference_bias

- 方法: `readPage` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a web page line by line, optionally filtering out comment lines starting with '#', and returns the concatenated HTML string.
- B 摘要: Reads configuration data from string variables and a file, parsing tokens to populate multiple sets and maps, with extensive error checking and data structure updates.
- 静态失败原因: Static models like CodeBERT rely on token and structural similarity; the low Jaccard similarity (0.072) and different control flow/API usage led them to correctly predict non-clone under a strict semantic view. They failed to match BCB's overly broad clone definition.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones under a broad Type-4 interpretation where both methods are seen as 'reading input data and processing it line by line,' despite vastly different specific logic and output. This seems like an error in BCB annotation.
- 共享行为: Both involve iterating over input lines or tokens and performing conditional processing
- 行为差异: A returns a concatenated string; B has no return value and populates multiple data structures.；A has simple line filtration; B has complex parsing with multiple tokenizers, nested conditionals, and error handling.；A reads from a URL; B reads from in-memory strings and a file.；A's logic is straightforward; B involves a large, intricate state machine for parsing a specific format.
- 修正建议: Incorporate coarse-grained semantic roles (e.g., 'data reading and processing') as features.；Use a contrastive learning objective that captures partial functionality similarity beyond strict equivalence.

### case_id=5797 FP lexical_or_api_overlap

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses configuration strings and a file to initialize multiple sets and a mapping for Tibetan transliteration.
- B 摘要: Copies a source file to a destination directory using a buffer.
- 静态失败原因: The model likely overgeneralized the presence of IOException handling and File operations, ignoring the fundamentally different algorithm and data structures.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because they have entirely different purposes and functionality; no Type-1/2/3/4 similarity.
- 共享行为: Both involve file I/O operations and handle IOException.
- 行为差异: readData builds data structures from configuration; copyFile transfers bytes.；readData is complex with multiple tokenization steps and error handling; copyFile is a straightforward file copy.；readData uses static variables and is stateful; copyFile is stateless.
- 修正建议: Improve context understanding to differentiate between functions that share API calls but have different high-level goals.；Use control-flow and data-flow features to distinguish file I/O used for reading vs. copying.

### case_id=5798 FP lexical_or_api_overlap

- 方法: `main` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that generates adapter classes from a Prolog file and writes them to a JAR file.
- B 摘要: Run method that parses XML input, generates a XUL menu overlay, and packages it as a ZIP/JAR file.
- 静态失败原因: The model likely relied on surface-level similarities such as File, streams, and JAR/ZIP API usage, missing the deep semantic difference in domain and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels them as non-clones because they have completely different domains and output types, despite some structural similarities in using streams and writing archives.
- 共享行为: Both perform file I/O；Both handle exceptions with print/throw；Both write output to a JAR/ZIP stream
- 行为差异: Function A is a command-line entry point; Function B is a private instance method；Function A processes Prolog files; Function B processes XML files；Function A generates Java classes; Function B generates XUL/JavaScript content；Function A uses complex reflection and class loading; Function B uses simpler XML parsing
- 修正建议: Improve training with more diverse examples that have overlapping APIs but different semantics；Incorporate dataflow analysis to capture input-output transformation logic

### case_id=5799 FN partial_functionality

- 方法: `copyOverWarFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies .war files from a source directory to the apps data directory and processes them.
- B 摘要: Retrieves a resource from a URL or cache, downloads it to a local cache file, and returns an InputStream.
- 静态失败原因: Static BERT relies on token-level and structural overlap; low Jaccard (0.138) and different control flow lead to low similarity, missing potential deep semantic connection.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider both as file copy operations with stream handling, accepting broad Type-4 similarity despite different sources and destinations.
- 共享行为: Both read from an input source and write to a file using streams.；Both use File, FileInputStream, FileOutputStream.；Both include exception handling and print debug messages.
- 行为差异: A copies local .war files; B downloads from a URL with caching logic.；A operates on multiple files in a loop; B handles a single resource per call.；A calls moveUnzipAndExtract after copy; B returns an InputStream.；A uses IOUtils.copy; B uses manual read/write loop.
- 修正建议: Enhance model with data-flow analysis to capture I/O operations.；Use graph-based representations (e.g., AST with edges for data flow) to handle variable names and control flow differences.；Incorporate API-level semantics for file handling functions.

### case_id=5800 FN partial_functionality

- 方法: `readData` vs `getEncoding`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses tokenized configuration strings into multiple sets and maps for Tibetan character processing.
- B 摘要: Extracts character encoding from HTTP response headers and content using URL connection.
- 静态失败原因: Low token Jaccard similarity (0.07) and long code length; static models rely on surface-level overlap and miss abstract structural similarity of parsing loops.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as data extraction from text input, focusing on the parsing loop pattern and populating data structures, hence a broad Type-4 clone.
- 共享行为: Both read from external input sources (string tokens vs URL stream)；Both parse line-by-line or token-by-token to extract information；Both populate data structures (HashSets, Maps) based on parsed content
- 行为差异: Input source: static string fields vs URL connection；Output: multiple sets/maps vs single encoding string；Error handling: throws errors vs returns default encoding；Function signature: void vs returns String
- 修正建议: Incorporate graph-based representations like AST or control flow graphs to capture loop structures；Use contrastive learning on abstract functionality patterns rather than token overlap；Add data flow analysis to detect similar read-parse-store patterns

### case_id=5801 FP boilerplate_overlap

- 方法: `gerarTutorialPage` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Generates a website by creating directories, copying CSS files, and writing HTML pages, displaying success/error messages.
- B 摘要: Reads a configuration file and populates several hash sets and mappings for Tibetan/Wylie processing.
- 静态失败原因: The static BERT model likely over-relied on common keywords (try, catch, File, IOException) and similar I/O boilerplate, ignoring the fundamental difference in purpose and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotation would not consider these clones because they have completely different functionality and no meaningful code overlap beyond boilerplate exception handling and I/O.
- 共享行为: Both use try-catch for exception handling；Both perform I/O operations
- 行为差异: Function A writes files and creates directories; Function B reads a file and populates data structures；Function A uses FileChannel and FileWriter; Function B uses BufferedReader and StringTokenizer；Function A has GUI interactions; Function B has no GUI；Different purposes: website generation vs. data initialization
- 修正建议: Improve model to better differentiate boilerplate from core logic；Incorporate data flow and type information；Use higher-level semantic representations

### case_id=5802 FN benchmark_preference_bias

- 方法: `main` vs `wordFrequency`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Main method that builds a fixed set of post parameters for a RenRen API call and prints the response.
- B 摘要: Method that queries a web service for word frequency by replacing a placeholder and parsing the response for a pattern.
- 静态失败原因: The static BERT model, by predicting non-clone, actually matched our strict view; it likely identified the significant semantic differences despite the boilerplate overlap. However, it failed to align with BCB's broader clone definition, possibly due to benchmark preference bias.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both performing network I/O with similar boilerplate patterns (URL, BufferedReader, while loop, try-catch), possibly considering them Type-4 (functionally similar at a high level like 'fetch data from web and process').
- 共享行为: Both create a URL and open an HTTP connection.；Both read response line by line using BufferedReader.；Both handle IOException and MalformedURLException.；Both involve string manipulation for URL construction.
- 行为差异: A sends a POST request with many hardcoded parameters; B sends a GET request with a single parameter.；A prints the entire response; B parses for a specific pattern and returns an integer.；A is a void main method; B returns int and takes a String parameter.；A uses HttpURLConnection explicitly; B uses URL.openStream().
- 修正建议: Adjust clone detection benchmarks to clearly distinguish between true functional similarity and accidental structural overlap.；Incorporate functional purpose detection beyond surface I/O patterns.

### case_id=5803 FN benchmark_preference_bias

- 方法: `importRoles` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Parses RoleName objects from XML retrieved via URL and returns a list.
- B 摘要: Registers a user by setting properties, creating a forum user via URL call, persisting to database, and sending confirmation email.
- 静态失败原因: Static models like GraphCodeBERT accurately captured the semantic dissimilarity, but BCB's broad clone interpretation led to a false positive annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotators may have considered the structural similarity of the URL-reading loop as sufficient for a Type-4 clone, ignoring the vastly different overall functionality.
- 共享行为: Both open a URL and read lines using BufferedReader.
- 行为差异: A returns a list of RoleName objects; B returns a boolean.；A is static and has no side effects; B is instance method with many side effects (database persist, email).；A catches exceptions silently; B logs and rethrows or returns false.；A only reads XML; B also encodes password, sets dates, adds authorities, and sends emails.
- 修正建议: Refine BCB annotations to be more consistent with semantic equivalence.；Train models on a wider variety of clone types including partial functionality.；Use data augmentation to teach models to distinguish boilerplate API usage from core semantics.

### case_id=5804 FN partial_functionality

- 方法: `main` vs `encodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its zip entries to local files.
- B 摘要: Reads a file, Base64-encodes it, and writes the encoded output to another file.
- 静态失败原因: Static BERT models rely on token embeddings and may not capture high-level semantic purpose, seeing low token Jaccard (0.226) and different method names/signatures, leading to a non-clone prediction. The models may not recognize the shared I/O loop pattern as a clone indicator when lexical overlap is low.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled this as a clone because both functions share the common pattern of reading bytes from an input stream and writing them to an output stream in a while loop with a buffer, which is a frequent Type-3 clone pattern, disregarding the specific I/O source and transformation.
- 共享行为: Both read bytes from an input stream and write them to an output stream in a buffered loop using a byte buffer.
- 行为差异: A reads from a ZipInputStream over a network or file stream; B reads from a Base64-decoding input stream over a file.；A writes to multiple files (one per zip entry); B writes to a single output file.；A does not have error handling (throws Exception); B has try-catch-finally.；A is a main method without parameters; B is a static method with parameters.
- 修正建议: Improve training data with more examples of I/O loop patterns as clones.；Use dataflow or control flow features to capture structural similarity.；Consider fine-tuning on pairs with similar loop structures but different I/O details.

### case_id=5805 FN partial_functionality

- 方法: `main` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its ZIP entries to the current directory.
- B 摘要: Recursively copies a file or directory using FileChannel and handles directory recursion.
- 静态失败原因: The token Jaccard similarity is low (0.198), and the functions differ in structure and purpose, making it hard for static models to recognize any abstract I/O similarity without explicit training.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled as clone due to superficial overlap in stream-based I/O patterns, despite drastically different high-level functionality.
- 共享行为: Both perform file I/O operations using streams and handle data transfer in chunks.
- 行为差异: Code A downloads from HTTP and unzips a ZIP archive; Code B copies local files/directories.；Code A is a main method with hardcoded URL; Code B is a generic utility method.；Code A uses ZipInputStream and BufferedOutputStream; Code B uses FileChannel and recursion.；Code B checks file/directory types and handles directory recursion; Code A does not.
- 修正建议: Augment training data with diverse I/O tasks to improve understanding of high-level semantics；Use data flow or control flow graphs to capture essential functional structure

### case_id=5806 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for new version of jEdit by reading a remote version file and comparing build numbers.
- B 摘要: Reads tab-delimited data from a URL and populates a vector of descriptions.
- 静态失败原因: Static models like BERT likely over-relied on lexical and API-level similarities (URL, openStream, while loop) and structural pattern, missing the distinct parsing logic and output behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires semantic equivalence or near equivalence; these functions serve entirely different purposes, so they are not considered clones.
- 共享行为: Both open a URL and read input stream；Both read line by line from the stream
- 行为差异: Different parsing logic: doVersionCheck looks for lines starting with '.version' or '.build', readUNI uses Scanner with tab delimiter；Different output: doVersionCheck shows dialogs, readUNI adds to a vector；Different error handling: doVersionCheck catches IOException and shows error dialog, readUNI catches MalformedURLException and generic Exception with printStackTrace；Different parameters and context: doVersionCheck uses a View and jEdit properties, readUNI uses a Vector and string source
- 修正建议: Incorporate data flow analysis to track how read data is processed；Use semantic similarity measures that capture purpose and output behavior；Train on more diverse examples to reduce overemphasis on API usage patterns

### case_id=5807 FP lexical_or_api_overlap

- 方法: `scrapeForIsbns` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Scrapes ISBN-10 patterns from a URL's content with retry logic and logging.
- B 摘要: Executes an HTTP POST request with parameters and returns the response string.
- 静态失败原因: Static models likely overemphasized lexical and API overlap (URL, openStream, BufferedReader) and structural similarities, ignoring the distinct method names and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the core task (scraping ISBNs vs. posting and receiving response) is entirely different, despite overlapping boilerplate networking code.
- 共享行为: Both open a URL stream and read from it using BufferedReader；Both handle exceptions
- 行为差异: A uses GET method (default) and regex for pattern matching; B uses POST method and writes parameters；A retries on connection errors; B does not retry；A returns count of matches; B returns response string；A does not write to output; B writes URL parameters
- 修正建议: Incorporate dataflow analysis to track how inputs and outputs are used；Use method name and return type as discriminative features；Consider task-level context such as external library calls

### case_id=5808 FP lexical_or_api_overlap

- 方法: `googleImageSearch` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Google image search function that fetches and parses image URLs from a Google search page.
- B 摘要: Reads and discards content from a localhost JSP page without processing.
- 静态失败原因: Static models likely overemphasized lexical and structural overlap (URL, BufferedReader, try-catch, readLine) without understanding the high-level intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the functions have completely different purposes: image search vs. trivial page reading, despite similar API usage.
- 共享行为: Both open HTTP connections and read data using BufferedReader
- 行为差异: Function A constructs a query URL for Google Images and parses HTML to extract image links；Function B only reads a fixed URL and ignores all content；Function A checks artist change and updates state; Function B has no conditional logic；Function A adds results to a list; Function B has no output
- 修正建议: Incorporate data flow analysis to track how input/output are used；Add intent classification using method names and context；Use more robust program slicing to isolate core logic

### case_id=5809 FP boilerplate_overlap

- 方法: `get` vs `sendRequestObjectResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Makes an HTTP GET request with custom headers to fetch game records, skips comment lines, and returns an array of GameRecord.
- B 摘要: Sends an HTTP POST request with GZIP-compressed XML, saves the response to a file determined by content type, and opens it in a browser.
- 静态失败原因: The static model likely overemphasized overlapping API usage patterns (e.g., URL.openConnection, setRequestProperty, getInputStream, try-catch) while ignoring the distinct data flow and method signatures, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically does not consider such broad functional similarity as clones; despite both using HTTP, the core logic and outputs are completely different, so BCB labels as non-clone.
- 共享行为: Both open an HTTP connection；Both set request properties；Both read from input stream；Both handle IOException in try-catch
- 行为差异: Different HTTP methods: GET vs POST；Different purpose: fetching records vs sending XML and saving file；Different output: returns GameRecord[] vs returns filename string；Different request handling: read line-by-line vs write compressed XML and read binary response
- 修正建议: Incorporate data flow analysis to distinguish between read and write operations；Use method name and return type as strong discriminators；Train on more diverse non-clone pairs with similar API usage but different semantics

### case_id=5810 FN partial_functionality

- 方法: `main` vs `unJarStart`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts all entries from a KMZ archive downloaded via HTTP and writes them to the current directory.
- B 摘要: Extracts specific entries from a JAR file that start with a given prefix, writing them to a constructed path.
- 静态失败原因: Low token overlap (0.13) and different method names, parameters, and library calls (ZipInputStream vs JarFile) misled the model into treating them as unrelated.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB groups both under 'Extract Archive' functionality, considering them semantically similar despite API and detail differences.
- 共享行为: Both iterate over archive entries (zip/jar) and extract some entries to files using stream I/O.
- 行为差异: A extracts all entries; B filters by prefix.；A writes to entry.getName(); B constructs a target path from jarPath.；A uses ZipInputStream; B uses JarFile and IOUtils.copy.；A prints extraction info; B does not.
- 修正建议: Use structural features like AST-based clone detection to capture the common pattern of iterating archive entries and writing files.；Incorporate API-level abstraction (e.g., group ZipInputStream and JarFile as archive I/O).

### case_id=5811 FP lexical_or_api_overlap

- 方法: `run` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a resource file from classpath and displays its text content in a GUI panel.
- B 摘要: Performs a Google image search, parses the HTML response to extract image URLs, and displays an image in a GUI.
- 静态失败原因: Static models may over-rely on surface-level overlaps like 'URL', 'BufferedReader', and the try-catch loop structure, missing the semantic difference in the data source and processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the functions serve entirely different purposes (resource loading vs. image search) and the similarity is only in boilerplate I/O code.
- 共享行为: Both use URL and URL connections to fetch data over HTTP or classpath.；Both read data line by line using BufferedReader and InputStreamReader.；Both handle exceptions with a try-catch block.；Both eventually update a GUI component after obtaining data.
- 行为差异: Function A reads a static resource from classpath; Function B performs a dynamic web search with query parameters.；Function A sets text content; Function B extracts and displays image URLs and an actual image.；Function A uses a StringBuilder; Function B concatenates strings directly and performs HTML parsing.；Function B has more complex post-processing of the response (splitting, filtering URLs) and updates multiple GUI elements.
- 修正建议: Incorporate dataflow analysis to distinguish data sources (classpath vs. HTTP).；Use control-flow or call-graph information to recognize different end goals (text display vs. image search).；Train on more examples with similar I/O patterns but different semantics to reduce false positives.

### case_id=5812 FP lexical_or_api_overlap

- 方法: `read` vs `get`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a camera log from a URL line by line, parses into CameraLogRecord, catches LogParseException, sorts records, and logs.
- B 摘要: Sends an HTTP GET request with custom headers to a URL, reads response lines, decodes non-comment lines into GameRecord, returns array, prints error on failure, catches IOException.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overemphasized the lexical overlap of common API usage (URL, BufferedReader, readLine) and control flow (while loop), ignoring the different semantics of parsing and output types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions have different outputs, error handling, and domain-specific parsing, making them functionally distinct even if they share a common structure of reading line by line from a URL.
- 共享行为: Both read from a URL and process lines.；Both use BufferedReader and readLine in a loop.；Both handle potentially malformed lines (one catches exception, one skips comments).；Both collect parsed objects into a list/collection.
- 行为差异: A uses URL.openStream(); B uses HttpURLConnection with custom headers and request method.；A catches LogParseException; B skips lines starting with '#'.；A sorts records; B does not sort.；A returns void; B returns GameRecord[].
- 修正建议: Incorporate data-flow analysis to track how lines are parsed and what transforms are applied.；Add attention to output types and exception handling to distinguish generic I/O patterns from specific business logic.；Use contrastive learning on negative pairs with high token overlap but different semantics.

### case_id=5813 FP boilerplate_overlap

- 方法: `fetchURLData` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches URL data with optional proxy support, handling file:// and http:// URLs.
- B 摘要: Handles GUI action events for configuring settings like Graphviz path, image scaling, and look-and-feel.
- 静态失败原因: The model likely relied on surface-level patterns such as null checks, try-finally blocks, and common API calls (e.g., 'if (x == null) return') leading to false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the two functions have completely different purposes and functionality; strict behavioral equivalence not required but even partial similarity is absent.
- 共享行为: Both use conditional checks and resource management patterns
- 行为差异: Function A performs network I/O to fetch remote data; Function B responds to GUI events and updates UI components；Function A returns byte array; Function B is void and modifies internal state；Function A deals with URL connections and streams; Function B deals with file choosers, preferences, and UI updates
- 修正建议: Train on more diverse examples with low lexical overlap；Incorporate structure-aware representations like AST or data flow；Use contrastive learning to distinguish functions with similar boilerplate but different semantics

### case_id=5814 FN partial_functionality

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (from URL or file) to a destination file without buffering.
- B 摘要: Copies a source file to a destination file using buffered I/O.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on surface-level features (tokens, AST structure) and may miss the semantic similarity due to low token overlap (Jaccard=0.25), different method names, parameter lists, and control structures. The model likely focused on the differences in exception handling and I/O patterns rather than the common dataflow of read-write.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers these clones because the core functionality of copying data from a source to a destination is identical, and the differences (source type, buffering, exception handling) are considered implementation variations rather than different semantics.
- 共享行为: Both copy bytes from an input source to a file output；Both check source existence before reading；Both close the input and output streams after copying
- 行为差异: Function A can read from a URL, while B only reads from files；A uses unbuffered byte-by-byte reading, B uses a buffer (4096 bytes)；A throws a generic Exception, B throws specific IOException and IllegalArgumentException；A does not use try-finally, B uses try-finally to ensure stream closure
- 修正建议: Enhance model with data flow analysis to capture read-write operations；Use contrastive learning on cases with low lexical similarity but high semantic overlap；Incorporate knowledge of common I/O APIs (InputStream, OutputStream) to abstract away specific implementations；Train on more examples of file/resource copying with varied implementations

### case_id=5815 FN lexical_or_api_overlap

- 方法: `File2String` vs `sendRequestObjectResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file from filesystem or classpath and returns its contents as a string.
- B 摘要: Sends an HTTP request with XML content, saves the response to a file, and returns the filename.
- 静态失败原因: Static BERT models rely on token-level similarity and structural overlap; the low Jaccard similarity (0.124) and different domain-specific keywords led to a non-clone prediction, missing the broad I/O functionality similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones due to both being I/O-intensive functions that read from a source and produce output, involving similar stream handling patterns and exception handling, despite different sources and sinks.
- 共享行为: Both involve reading from an input stream and processing data.；Both handle I/O exceptions with try-catch blocks.；Both use System.out.println for debugging.
- 行为差异: Function A reads a local file; Function B sends an HTTP request.；Function A returns the file content; Function B returns the filename of a saved response.；Function A uses System.exit on error; Function B shows an error dialog.；Function B includes network setup, compression, and file creation logic absent in A.
- 修正建议: Improve token representation to capture API usage patterns.；Use data-flow or control-flow embeddings to model stream operations.；Incorporate explicit I/O operation signatures.

### case_id=5816 FN partial_functionality

- 方法: `getResourceAsStream` vs `_checkLanguagesFiles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a resource from a URL, caches it locally, and returns an InputStream, handling HTTP connections and file caching.
- B 摘要: Checks that language properties files exist in two directories and copies them if missing, ensuring synchronization between global and temp directories.
- 静态失败原因: Static BERT models may rely heavily on lexical and API token overlap, and the token Jaccard here is low (0.122). They might miss the common file-handling structure due to different method names and overall purposes, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both methods perform similar file caching and copying patterns, which are considered Type-3 or Type-4 clones in BigCloneBench, where the focus is on similar functionality rather than exact implementation.
- 共享行为: Perform file I/O operations including checking file existence, creating files, and copying data between files.；Use FileInputStream and FileOutputStream for reading and writing files.；Handle exceptions with try-catch blocks and print stack traces.
- 行为差异: Function A involves network access (URL, HTTP connection) whereas Function B only operates on local files.；Function A has complex caching logic using a hash table and HTTP headers, while Function B simply copies files if they don't exist.；Function A returns an InputStream, while Function B returns void and modifies files.
- 修正建议: Use models that incorporate structural information like code property graphs or control flow graphs to capture similar patterns.；Train on more diverse examples of file I/O operations to recognize common idioms.；Consider ensemble methods combining lexical and semantic features.

### case_id=5817 FP boilerplate_overlap

- 方法: `encrypt` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Encrypts a string to MD5 hex digest.
- B 摘要: Processes a web form classification request, interacts with an external service, and forwards to appropriate action.
- 静态失败原因: The model likely over-relied on superficial common elements like try-catch blocks and standard library usage, causing it to miss the fundamental semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the two functions perform entirely different operations (encryption vs. web request handling) with no shared functionality.
- 共享行为: Both use try-catch for exception handling.；Both use standard Java library classes.
- 行为差异: A performs cryptographic hashing; B handles web request/response and business logic.；A is stateless; B uses session and request parameters.；A returns a hex string; B returns an ActionForward.；B involves multiple I/O operations (URL connection, XML parsing) not present in A.
- 修正建议: Train on more diverse examples to recognize boilerplate patterns as non-indicative of clone.；Incorporate task-agnostic semantics (e.g., method purpose classification) to differentiate general I/O from business logic.

### case_id=5818 FN partial_functionality

- 方法: `read` vs `PhoneSetImpl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Read from a URL or file path, delegate to another read method, and return status.
- B 摘要: Constructor that reads from a URL, parses lines, and populates a map.
- 静态失败原因: Static BERT/GraphCodeBERT models likely failed due to low token overlap (Jaccard 0.195) and different signatures/control flow, missing the shared URL reading pattern because the functions have different primary goals.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone because both functions involve reading from a URL stream and processing input, which is considered partial functionality similarity under BCB's broad Type-4 annotation guidelines.
- 共享行为: Both open an input stream from a URL；Both read data from the stream；Both handle I/O operations
- 行为差异: Function A also handles file paths, while B only handles URLs；Function A delegates to another read method and returns a status code, while B directly parses lines and builds a map；Function A may handle errors by setting status, while B throws IOException；Function A reads all bytes, while B reads line by line and processes
- 修正建议: Improve training data to include more diverse partial similarity cases；Incorporate data flow context to capture shared I/O operations；Use contrastive learning with harder negatives to distinguish partial clones

### case_id=5819 FP boilerplate_overlap

- 方法: `sendPost` vs `sendRequestObjectResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST with parameters and returns the response as a string.
- B 摘要: Sends a request to a servlet, compresses and logs it, saves the response to a file based on content type, and returns the file path.
- 静态失败原因: The static model likely overfitted to common API usage patterns (URL, HttpURLConnection, streams) and boilerplate try-catch structures, ignoring the significant behavioral differences due to lack of deep semantic understanding.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled them as non-clones because they perform fundamentally different operations: one is a generic HTTP POST helper, the other is a complex request-response handler with compression, file saving, and UI interactions. They share only basic HTTP boilerplate, not core functionality.
- 共享行为: Both use HTTP connections to send data over the network.；Both read the response from the server.
- 行为差异: Function A sends simple POST parameters, while B sends XML with compression.；Function A returns the response string, B saves it to a file and returns the file path.；Function B includes server configuration dialogs, logging, and file type handling.；Function B has error handling with dialog messages, A uses a simple message print.
- 修正建议: Incorporate control flow and data flow analysis to distinguish simple CRUD from complex multi-step processes.；Focus on semantic roles (e.g., send-and-return vs. send-process-save) rather than shared API calls.；Train on examples with similar boilerplate but different logic to discourage false positives.

### case_id=5820 FN benchmark_preference_bias

- 方法: `getResourceAsStream` vs `gzip`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Retrieves a resource from a URL, caches it locally, and returns an InputStream.
- B 摘要: Compresses a directory into a GZIP file.
- 静态失败原因: Static BERT correctly identified non-clone due to low token overlap and distinct control flows, but may have been penalized for failing to detect an alleged similarity that doesn't exist.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have mislabeled due to a broad interpretation of file/stream handling or an annotation error.
- 共享行为: Both perform file I/O operations.；Both use FileInputStream and OutputStream.
- 行为差异: Function A fetches from URL and caches; function B compresses local directory.；A returns an InputStream; B has void return and writes to a specific file.；A involves HTTP connection handling; B does not.
- 修正建议: Review BCB annotation for correctness.；Improve dataset quality.

### case_id=5821 FN benchmark_preference_bias

- 方法: `readData` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Parses static string fields to initialize sets and maps for Tibetan/Sanskrit character processing.
- B 摘要: Registers a user by validating input, encoding password, creating forum user via HTTP, persisting to database, and sending confirmation email.
- 静态失败原因: Static models like GraphCodeBERT rely on token and structural similarity; the extremely low Jaccard similarity (0.108) and disparate operations likely led to a correct non-clone prediction, but BCB's annotation may be an outlier or reflect a loose definition.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'data parsing and storage' methods, a very broad Type-4 categorization, but this interpretation is tenuous given the low token overlap and distinct purposes.
- 共享行为: Both involve some form of string parsing and data storage.
- 行为差异: Different domains: character set initialization vs. user registration.；Different I/O: reading from class fields vs. external HTTP and database operations.；Different control flow: A uses simple loops, B includes exception handling and conditional returns.
- 修正建议: Review BCB annotation for this pair; if it is a mislabel, correct the ground truth.；If BCB intends broad Type-4, improve model to capture abstract behavioral patterns like 'parsing' or 'initialization'.

### case_id=5822 FP boilerplate_overlap

- 方法: `readRemoteFile` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a remote file line by line and returns the concatenated content as a single string.
- B 摘要: Loads a vector tile from a URL, reads its JSON content, processes it into geometries, and updates a data source with concurrency management.
- 静态失败原因: The static BERT/GraphCodeBERT model was likely misled by high lexical overlap in the initial reading phase (URL, openStream, BufferedReader, readLine, string concatenation), ignoring the crucial contextual differences in the later code. The model may also suffer from limited context window, failing to capture the long-range semantics of function B's extensive processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label this as non-clone because the overall functionality differs significantly: one is a simple file reader, the other is a multi-step data loading and processing routine. The shared I/O pattern is common boilerplate and does not imply semantic equivalence.
- 共享行为: Both open a URL input stream and read lines using BufferedReader.；Both concatenate lines into a string while reading.；Both handle IOException (including MalformedURLException implicitly).
- 行为差异: Function A returns the concatenated string; Function B processes the string into geometries and updates a data source.；Function A uses a while loop with manual eof flag; Function B uses standard while((line=in.readLine())!=null) pattern.；Function B has concurrency control with synchronized blocks; Function A does not.；Function B constructs URL from data source methods; Function A uses a static remote file URL.
- 修正建议: Use a model with longer context to capture entire function behavior.；Incorporate data flow or control flow graphs to distinguish different uses of read data.；Add post-hoc verification that compares output types and side effects.；Train on more diverse examples to reduce bias toward common I/O patterns.

### case_id=5823 FP lexical_or_api_overlap

- 方法: `getVersion` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches the latest version string from a remote repository URL.
- B 摘要: Performs a Google image search for the current track's artist and album, extracts image URLs, and adds them to a list.
- 静态失败原因: Static BERT likely over-relied on lexical and structural overlap (e.g., URL, BufferedReader, try-catch, while loop), ignoring the different method names, return types, and core logic, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench considers Type-4 clones only if they perform the same functionality; here, the underlying tasks (version retrieval vs. image search) are completely different despite similar boilerplate HTTP access.
- 共享行为: Both open HTTP connections to remote URLs；Both use BufferedReader to read line-by-line from input stream
- 行为差异: getVersion returns a single line version string; googleImageSearch concatenates all lines and parses HTML for image URLs；getVersion uses URLConnection without setting User-Agent; googleImageSearch uses HttpURLConnection with custom User-Agent；googleImageSearch has complex string manipulation and multiple data structures; getVersion is straightforward；getVersion has no side effects besides return; googleImageSearch modifies static variables and a list
- 修正建议: Train on more diverse negative examples with similar API usage but different semantics；Incorporate dataflow analysis or control flow differences to distinguish simple retrieval from parsing；Use method-level summarization of intent or API call sequences to capture behavioral differences

### case_id=5824 FN benchmark_preference_bias

- 方法: `EncodeReturn` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Encrypts and combines multiple data files to produce a final encrypted route file.
- B 摘要: Downloads a resource from a URL, caches it locally, and returns an InputStream to the cached file.
- 静态失败原因: The static model likely focused on low token overlap (0.064) and different method signatures, missing the high-level pattern of file reading/writing that BCB might emphasize.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them clones based on broad functional similarity in data I/O and file manipulation, despite different high-level purposes.
- 共享行为: Both perform file I/O operations including reading and writing files.；Both handle exceptions and ensure resources are closed.；Both involve copying data from a source to a destination.
- 行为差异: Function A has an encryption step, while B does not.；Function B includes HTTP connection handling and caching logic.；Function A returns a File object, while B returns an InputStream.；Function B is synchronized and uses a cache hashtable.
- 修正建议: Train model to recognize broader behavioral patterns in file I/O, not just lexical similarity.；Incorporate data flow analysis to identify common transformations (e.g., read-process-write).

### case_id=5825 FN benchmark_preference_bias

- 方法: `ExternalDecoder` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Constructor that initiates a background thread to copy data from an input stream to a process's standard input.
- B 摘要: Method that modifies a localized properties file by reading, replacing or appending a key-value pair, and writing back.
- 静态失败原因: The static BERT/GraphCodeBERT method likely relied on token similarity and structural patterns, and the very low Jaccard similarity (0.0857) and different API usage made it miss the abstract I/O similarity that BCB might have used.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as data copying or I/O operations, or they might be mislabeled in the benchmark.
- 行为差异: One copies data from a stream to a process's stdin; the other modifies a file on disk.；One involves threading; the other does not.；One uses Apache IOUtils; the other uses standard java.io.；One is a constructor; the other is a public method.
- 修正建议: Incorporate higher-level semantic features like data flow and overall I/O behavior.；Use contrastive learning on diverse I/O patterns.；Review BCB annotations for consistency.

### case_id=5826 FN partial_functionality

- 方法: `testNetworkHTTP` vs `runScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: This function performs multiple HTTP GET requests to predefined URLs with query parameters from private data fields, reads and discards the response lines, logging a start message.
- B 摘要: This function downloads a script file from a URL formed by appending a script name to the code base, reads the content byte by byte, and returns it as a string, or returns 'error!' on failure.
- 静态失败原因: Static BERT models rely on token and syntactic overlap; the low Jaccard similarity (0.1096) and different structures lead to a non-clone prediction, while BCB focuses on the shared high-level behavior of HTTP GET and stream reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both implement the pattern of 'open HTTP connection, read input stream, and handle exceptions', which is a common Type-4 semantic clone despite differences in the number of requests, response handling, and return value.
- 共享行为: Both functions open an HTTP connection to a URL and read the response input stream using buffered readers.
- 行为差异: Function A makes multiple requests (6) to different URLs with query parameters and discards the response; Function B makes a single request and accumulates the response.；Function A returns void; Function B returns the response content as a String.；Function A uses HttpURLConnection and explicitly disconnects; Function B uses URL.openStream() without explicit disconnect.；Function A only catches IOException; Function B catches Exception.
- 修正建议: Improve static models to capture semantic patterns like network I/O operations beyond token overlap.；Use dataflow analysis to identify common I/O patterns.

### case_id=5827 FP lexical_or_api_overlap

- 方法: `getWebByUrl` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads a web page from a URL, saves it to a local HTML file, and recursively extracts URLs from the page.
- B 摘要: Reads a tab-separated values file from a URL, parses each line to extract an ID and description, and adds them to a vector.
- 静态失败原因: Static BERT models may over-rely on lexical overlap (e.g., 'URL', 'openStream', 'is.close') and shared API usage patterns, ignoring the broader control flow and output differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have different outputs and side effects (file writing vs. data collection), and the core logic differs significantly despite similar URL reading boilerplate.
- 共享行为: Both open a URL connection and read data line by line from an InputStream.
- 行为差异: Function A writes output to a file and recursively processes URLs; Function B parses lines with a delimiter and stores results in a Vector.；Function A uses PrintWriter and StringBuffer; Function B uses Scanner and Vector.
- 修正建议: Add more structural features like control flow graphs, data flow analysis, or incorporate output types and side effects into the model.

### case_id=5828 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses HTML from a URL to extract all links and their text.
- B 摘要: Queries a ticket system's REST API for open tickets in a queue and returns a list of ticket objects.
- 静态失败原因: The static model may have been misled by common boilerplate patterns (URL connection, BufferedReader, while loop reading lines, exception handling) that are typical in network I/O code, causing a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the methods have different functionality (web scraping vs. API client) despite some structural overlap in I/O handling.
- 共享行为: Both open a URL connection and read data via BufferedReader
- 行为差异: A uses regex to parse HTML links; B uses REST API with query parameters；A returns vectors of links/texts; B returns list of RTTicket objects after fetching each ticket；B includes authentication and more complex error handling
- 修正建议: Train on more diverse examples to distinguish domain-specific logic from generic I/O patterns；Use dataflow analysis to capture semantic differences in processing lines

### case_id=5829 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Modifies a locale-specific properties file by replacing or adding a message key-value pair.
- B 摘要: Reads a DICOM image file and writes its pixel data to another file.
- 静态失败原因: The static model correctly predicted non-clone (0) because of very low token overlap and distinct API usage. It did not fail; it correctly identified semantic difference.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to a broad interpretation of 'file read/write' operations, despite completely different domains and logic. This is likely an annotation error.
- 共享行为: Both read from a file and write to a file.
- 行为差异: A works with properties files and string manipulation; B works with binary DICOM images.；A modifies a specific key-value pair; B copies entire pixel data.；A uses Java I/O streams and BufferedReader; B uses ImageIO and DICOM-specific APIs.；A may create a new file if not exist by copying from English file; B always expects input file to exist.
- 修正建议: Improve annotation guidelines to avoid labeling semantically unrelated functions as clones.；Use functional similarity metrics based on output behavior rather than superficial I/O patterns.

### case_id=5830 FN boilerplate_overlap

- 方法: `unzipModel` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts all entries from a zip file to a temporary directory.
- B 摘要: Modifies a specific message value in a locale-specific properties file, copying from English if missing.
- 静态失败原因: Static BERT/GraphCodeBERT models likely focused on the distinct domain-specific operations (zip decompression vs. properties manipulation) and low token overlap, thus missing the broader structural similarity that BCB considers a clone. The model prioritized semantic precision over coarse-grained functionality similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this pair as a clone due to both functions involving reading from an input source, processing data, and writing to output files with similar structural patterns like loop reading and stream handling, which could be considered Type-3 or Type-4 clones under a very broad interpretation of file processing functionality.
- 共享行为: Both perform file I/O operations with streams；Both use try-catch blocks for exception handling；Both read data in a loop and write to a file；Both close streams and files after use
- 行为差异: Function A reads and decompresses zip entries; Function B reads and processes text lines；Function A writes binary data; Function B writes text data；Function A creates multiple output files (one per entry); Function B writes to a single file；Function A does not modify input; Function B modifies input by updating a key-value pair
- 修正建议: Train models to recognize broad functional similarity beyond exact logic, such as file processing tasks；Use hierarchical representations or incorporate task-level annotations；Consider data augmentation with pairs that share structural patterns but different specific tasks

### case_id=5831 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a version check URL and parses build lines to compare versions.
- B 摘要: Constructor for a simple Swing browser that fetches an XML/HTML URL, optionally applies XSLT, and displays content.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on lexical and API overlap (URL, BufferedReader, try-catch) and possibly similar control flow patterns, missing the distinct semantic contexts and goals.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions share only trivial API usage and have completely different overall purposes, structure, and output. The annotation preference is for high-level functional similarity beyond common libraries.
- 共享行为: Both open a URL and read lines using BufferedReader.
- 行为差异: A is a static utility for version checking; B is a GUI constructor.；A parses build lines and calls another method; B parses XML, XSLT, and displays HTML.；A has no GUI components; B sets up a full Swing interface.；A uses view.showWaitCursor/hideWaitCursor; B uses JFrame and JEditorPane.
- 修正建议: Incorporate data flow and control flow analysis to distinguish different data transformations.；Use graph-based representations that capture the overall function purpose beyond token sequences.；Add contrastive training with hard negative examples that share API but differ in intent.

### case_id=5832 FP lexical_or_api_overlap

- 方法: `run` vs `getURLContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Runs a thread to fetch a vector tile URL, read its content, parse into geometries, and add to data loader with synchronization and error handling.
- B 摘要: Reads the content of a URL and returns it as a string using URLConnection and BufferedReader.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-relied on lexical overlap (common API calls: URL, BufferedReader, readLine, etc.) and missed the broader context—function A has many additional operations (synchronization, protocol check, tile parsing, data storage) that dominate its behavior. The model may have been misled by the common reading pattern without recognizing the distinct overall semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled non-clone (0) because, despite sharing a common sub-task of reading URL content, the overall functionality and purpose are distinct: one is a complex tile-loading thread with domain-specific processing, the other is a generic URL content fetcher. The shared part is insufficient to consider them any type of clone under BCB guidelines.
- 共享行为: Both open a URL and read its content line by line using BufferedReader.readLine()
- 行为差异: Function A uses synchronization to avoid duplicate requests, handles multiple protocols (http, file), and has extensive error handling beyond IOException.；Function A processes the read lines into a geoJSON string, then parses it into vector tile geometries and adds to a data loader; function B simply returns the entire string with newlines appended.；Function B is static and returns the content; function A is an instance method with side effects on data structures.；Function A adds newline characters in the read loop; function B does not.
- 修正建议: Incorporate dataflow or control-flow analysis to distinguish incidental shared subroutines from core functionality.；Use contrastive learning with negative sampling based on overall functional purpose rather than token overlap.；Enhance model with long-range dependency handling (e.g., transformer with larger window) to capture the full logic of function A.

### case_id=5833 FN benchmark_preference_bias

- 方法: `testTrainingBackprop` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: A JUnit test that creates a temporary file, copies a resource stream to it, builds a neural network, and trains it.
- B 摘要: A method that retrieves a resource as an InputStream with caching via local files and HTTP support.
- 静态失败原因: The static model correctly identified the semantic differences and low token overlap, predicting non-clone, but BCB label is a false positive.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotators may have considered both as methods that open a resource stream and write to a file, ignoring the larger context, leading to a broad Type-4 clone label.
- 共享行为: Both involve reading a resource stream and writing to a file
- 行为差异: A is a test method; B is a utility for resource loading；A trains a neural network; B returns an InputStream；A uses IOUtils.copy; B has complex caching logic
- 修正建议: Improve BCB annotation guidelines to avoid labeling methods with only trivial I/O similarity as clones；Use more diverse evaluation metrics

### case_id=5834 FN partial_functionality

- 方法: `setBundleInfoName` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses a URL-accessible properties file to update bundle name mappings in a list.
- B 摘要: Reads from a file or URL stream and delegates to another method, returning a status code.
- 静态失败原因: Static BERT models like GraphCodeBERT might fail because they rely on lexical and syntactic similarity, and here the token overlap is low (0.25). The shared URL opening pattern is not sufficient to overcome the overall difference in functionality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered them clones because both functions read data from a URL stream and involve processing, possibly as a Type-4 clone if the other read method does similar parsing. However, the listed code strongly suggests different purposes.
- 共享行为: Both open a URL stream using java.net.URL；Both handle IOException via catch block
- 行为差异: Function A updates a list of BundleInfo objects with parsed key-value pairs; Function B only returns status and does not modify any list.；Function A reads lines and splits by '='; Function B delegates to a different read method with unknown behavior.；Return types differ: boolean vs int.；Function B also handles local file input, while A only handles URLs.
- 修正建议: Improve alignment of variable names and method signatures in embeddings；Incorporate data flow analysis to distinguish between writing to list vs returning status；Use fine-tuning with more negative examples of URL-opening functions with different purposes

### case_id=5835 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter feed from a fixed URL using HttpClient and returns the JSON content as a string.
- B 摘要: Constructor for a Swing browser GUI that fetches XML from a URL, optionally applies XSLT transformation, and displays the result in a JEditorPane.
- 静态失败原因: Static model may have focused on superficial similarities like BufferedReader and URL usage, or boilerplate try-catch patterns, ignoring the overall semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have different high-level purposes and minimal structural similarity, despite both using URL reading.
- 共享行为: Both read content from a URL using BufferedReader；Both handle IOException
- 行为差异: A is a simple HTTP GET to fetch a Twitter feed; B is a GUI constructor with XML parsing, XSLT transformation, and display；A uses Apache HttpClient; B uses URL.openStream()；A returns a String; B sets up a JFrame and displays content；A handles ClientProtocolException; B handles TransformerException
- 修正建议: Incorporate structural information like AST paths to distinguish high-level tasks；Use data-flow analysis to capture different data transformations；Increase training diversity with more GUI vs. non-GUI examples

### case_id=5836 FN benchmark_preference_bias

- 方法: `parse` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Parses an input stream and either saves it to a file or delegates to a downstream parser based on resource name metadata.
- B 摘要: Builds edited HTML pages for a site by reading XML, applying transformations, and writing output files for each page.
- 静态失败原因: The static BERT method predicted non-clone correctly; the BCB label is likely incorrect, so the model actually succeeded despite the discrepancy.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely mislabeled this pair due to incidental lexical overlap (e.g., 'stream', 'FileOutputStream') or an annotation error; even the broadest Type-4 clone definition requires some shared functionality, which is absent.
- 共享行为: Both perform file I/O operations
- 行为差异: Function A is a short parser delegator; B is a long site builder；Function A conditionally copies stream; B processes multiple pages with XSLT；A uses ContentHandler/Metadata API; B uses FileSystem and DOM；A has no loops; B has a for loop over pages
- 修正建议: Double-check BCB annotation for this pair; it may be a false positive；Incorporate better semantic understanding to avoid matching unrelated functions

### case_id=5837 FN partial_functionality

- 方法: `processAddByURLSubmit` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads content from a URL and processes it as DOAP XML, handling file not found and IO errors.
- B 摘要: Gets an InputStream for a resource name, using a caching mechanism with HTTP conditional requests and local file caching.
- 静态失败原因: The functions have low lexical overlap (Jaccard 0.07377) and different method names, lengths, and control structures. Static BERT models rely heavily on token-level similarity and structural alignment, which are insufficient here. The semantic similarity (both reading from URL) is not captured by surface features.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers functions that perform core I/O operations from a URL as functionally similar (Type-4), even if post-processing differs. The shared pattern of opening a URL stream and reading data is considered a clone under broad Type-3/Type-4 criteria.
- 共享行为: Both open a URL connection and read from its input stream.；Both handle exceptions during stream reading.
- 行为差异: Function A processes the stream content as a String and passes it to a DOAP processor; Function B returns an InputStream or caches it locally.；Function A has no caching; Function B has extensive caching logic.；Function A returns void; Function B returns InputStream.；Function B handles HTTP-specific caching and conditional requests; Function A does not.
- 修正建议: Use a model that captures long-range dependencies and semantic roles, such as GraphCodeBERT with dataflow analysis.；Incorporate API call structure as a feature, e.g., both contain 'URL.openStream()' or 'URLConnection.getInputStream()'.

### case_id=5838 FN boilerplate_overlap

- 方法: `copyResource` vs `combineJs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.45`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a single resource from either a URL or a local file to a destination file by reading and writing byte by byte.
- B 摘要: Combines multiple JavaScript files from URLs into a single file, optionally minifies them, updates an HTML element's src attribute, and manages temporary files.
- 静态失败原因: The model likely relied on token-level overlap and structural similarity, which are low (Jaccard 0.122). The shared I/O operations are small compared to the overall diverse contexts, leading to a non-clone prediction.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as a clone due to the common pattern of reading from a URL and writing to a file, considering the core I/O functionality as the primary semantic similarity, while disregarding the additional complex operations in B.
- 共享行为: Open an input stream from a URL using url.openStream()；Write to an output file stream；Close input and output streams
- 行为差异: A copies a single resource; B processes a list of multiple JavaScript files.；B includes minification logic via JavaScriptCompressor and error handling.；B creates temporary directories and files, manages multiple output files (combine and concat).；B modifies an HTML element attribute and computes a hash for the output file name.
- 修正建议: Expand training data with more diverse I/O patterns to better capture functional differences.；Use models that incorporate data flow and control flow to distinguish simple copy from complex processing.；Consider hierarchical representations that separate boilerplate from core functionality.

### case_id=5839 FN benchmark_preference_bias

- 方法: `moveFile` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copy a file to a target location and delete the original.
- B 摘要: Handle an HTTP GET request to serve a page, including page lookup, permission checks, logging, and caching.
- 静态失败原因: Static BERT methods rely on token overlap and structure; here, low Jaccard similarity and different API usage led to correct non-clone prediction.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB potentially mislabeled this pair; the low token similarity and disparate functionalities make clone status unlikely even under broad Type-4 criteria.
- 共享行为: Both involve file I/O operations；Both handle exceptions
- 行为差异: A is a simple file copy while B is a complex web request handler；A has no HTTP or servlet context, B is tightly coupled to servlet API；A operates on files only, B interacts with database, properties, and HTTP response
- 修正建议: Review BCB label for possible annotation error；If label is correct, consider looser matching criteria that include shared I/O patterns

### case_id=5840 FN boilerplate_overlap

- 方法: `doVersionCheck` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads URL to fetch version information and parse build lines.
- B 摘要: Sends XML request to geospatial service, parses XML response to extract place names and IDs, with retry logic.
- 静态失败原因: The model likely over-relied on lexical tokens like 'URL', 'openStream', 'BufferedReader', 'readLine', and 'try-catch', ignoring higher-level semantics and data flow differences. The structural similarity in I/O patterns caused false negative based on token-based features.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled as clone due to superficial boilerplate overlap: both perform network I/O with BufferedReader and readLine, common in Java I/O patterns. However, core functionality differs significantly; this is likely a misannotation in BCB.
- 共享行为: Both open a URL and read lines via BufferedReader.；Both have try-catch blocks for IOException/Exception.；Both use while loop to read lines until null.
- 行为差异: Function A has a single try-catch without retry; B has retry loop (up to 3 retries).；A parses simple lines for build versions; B constructs and parses complex XML.；A returns void and calls another method; B returns a collection of tuples.；A uses a fixed URL from properties; B dynamically constructs URL with XML content.
- 修正建议: Incorporate data flow or control flow features to distinguish I/O boilerplate from core logic.；Add negative training examples that share I/O patterns but differ in business logic.；Use code summarization to capture goal/behavior beyond surface tokens.

### case_id=5841 FP partial_functionality

- 方法: `getURLContent` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads entire URL content line by line, appends newline separators, and returns the full string, handling encoding.
- B 摘要: Opens a URL and returns only the first line of its content without encoding handling.
- 静态失败原因: The model likely overemphasized lexical and structural similarities (similar signatures, URL, BufferedReader, readLine) and missed the critical control flow difference (loop vs no loop) that changes the output size.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels as non-clone when the core functionality differs in output behavior (full content vs single line), even though both involve URL content fetching.
- 共享行为: Both create a URL object from a string parameter；Both open a network connection and get an InputStream；Both wrap the InputStream in a BufferedReader；Both close the reader after reading
- 行为差异: Function A reads all lines using a while loop and accumulates them in a StringBuilder with newlines; Function B reads only the first line.；Function A handles content encoding; Function B does not.；Function A uses URLConnection, Function B uses HttpURLConnection and calls disconnect()；Function A returns the full content; Function B returns just the first line.
- 修正建议: Incorporate control flow features (e.g., loop detection) to distinguish reading all lines vs first line.；Use dataflow analysis to track how many lines are read.；Train on pairs with similar API usage but different output characteristics.

### case_id=5842 FP lexical_or_api_overlap

- 方法: `run` vs `sendPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a text resource from classpath and displays it in a Swing component.
- B 摘要: Sends an HTTP POST request and returns the response body as a string.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on the common lexical patterns (URL, BufferedReader, InputStreamReader, line loop) and exception handling, overlooking the different contexts and purposes. The model likely classified based on API similarity rather than overall semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because the high-level functionalities are distinct: one is a resource loader for UI, the other is an HTTP client method. The structural overlap in I/O boilerplate is insufficient for a clone label in BigCloneBench.
- 共享行为: Both use BufferedReader to read lines from an input stream.；Both use InputStreamReader with UTF-8 encoding.；Both have try-catch blocks that handle exceptions.
- 行为差异: A reads from a local file resource; B makes a network POST request.；A writes to a UI component; B returns a string to caller.；A sends no output; B sends data via PrintWriter.；A appends newline characters to each line; B concatenates lines without newlines.
- 修正建议: Incorporate method name and class context as features to distinguish purpose.；Add data flow analysis to differentiate input-only vs. input-output streams.；Use control flow and API call differences (openStream vs. HttpURLConnection).

### case_id=5843 FN benchmark_preference_bias

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file from one path to another, creating parent directories if needed and checking canonical paths to avoid self-copy.
- B 摘要: Builds a site for editing by reading XML, performing XSLT transformations, concatenating controls and menus, and writing output files for each page with extensive configuration and error handling.
- 静态失败原因: The static BERT model correctly predicted non-clone because the token Jaccard is very low (0.07) and the code structures are dissimilar. It captured the lack of semantic overlap beyond generic file operations, which is insufficient for clone detection in this case.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this pair as clones (Type-4) due to both performing file I/O with similar low-level patterns (read-write-close) and having exception handling, despite vastly different complexity and purpose. This reflects a preference for high-level functional similarity (both 'copying' or 'writing files') over detailed semantics.
- 共享行为: Both involve file input/output operations (opening streams, reading, writing, closing).；Both include exception handling with logging.
- 行为差异: copyFile is a simple byte-by-byte copy of a single file; buildSiteForEdit processes multiple pages with complex XML parsing, XSLT, and string manipulation.；buildSiteForEdit has a large number of parameters and dependencies on external classes; copyFile is a standalone utility.；copyFile creates directories; buildSiteForEdit does not (it assumes output paths exist).；buildSiteForEdit includes conditional logic, versioning, and media handling; copyFile is unconditional.
- 修正建议: Clarify BCB annotation guidelines to avoid labeling generic I/O patterns as clones unless specific behavioral overlap exists.；Use a more fine-grained clone type classification (e.g., require Type-3 with significant shared control flow or data flow).；Incorporate task-level semantics (e.g., method purpose from documentation or context) to distinguish utility functions from complex business logic.

### case_id=5844 FP boilerplate_overlap

- 方法: `readPage` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads HTML from a URL, optionally ignoring comment lines starting with '#', and returns the entire HTML as a string.
- B 摘要: Imports sequence names and sequences from a URL in FASTA-like format, parsing by '>' delimiters and storing them in ArrayLists.
- 静态失败原因: The static model may have over-emphasized common boilerplate code: URL opening, BufferedReader, InputStreamReader, loop patterns, and exception handling. It likely missed the high-level semantic difference due to reliance on token-level similarities without capturing the distinct data processing goals.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality is distinct: one is a generic HTML fetcher, the other is a specialized sequence parser. Despite shared URL-reading boilerplate, the core purpose and output differ significantly, aligning with Type-4 only if functionality is similar, which it is not.
- 共享行为: Both open a URL stream and read text input line by line.；Both handle IOExceptions.
- 行为差异: readPage returns a concatenated HTML string; importSequences populates two ArrayLists.；readPage optionally skips lines starting with '#'; importSequences searches for '>' delimiter to separate sequence entries.；readPage reads all lines; importSequences uses an ImportHelper for structured parsing of sequences.
- 修正建议: Use structure-aware models that capture longer-range semantics.；Incorporate data flow analysis to differentiate processing of read data.；Add training examples with similar boilerplate but different functionality to reduce overemphasis on common APIs.

### case_id=5845 FN partial_functionality

- 方法: `getResourceAsStream` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource from a URL, caches it locally, and returns an InputStream to the cached file, with HTTP conditional requests.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: Static models rely on lexical and structural overlap; the low Jaccard similarity (0.14), different method names, and different APIs (HTTP vs file I/O) caused the model to miss the underlying I/O copy pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone because both functions perform file copy operations (reading input and writing output) and share common resource management boilerplate, considering Type-4 semantic similarity where one is a more complex variant of the other.
- 共享行为: Both read from an input source and write to an output file；Both use try-catch-finally to manage resources；Both close streams/channels in finally
- 行为差异: A handles HTTP connections, caching, and conditional requests; B is a simple copy without caching or network；A returns an InputStream; B returns void；A uses byte-by-byte copy with BufferedStreams; B uses transferTo on FileChannel
- 修正建议: Improve model to recognize core file copy logic even with additional wrapping；Use dataflow analysis to match transferTo with byte-by-byte copy；Incorporate knowledge of common I/O patterns across different libraries

### case_id=5846 FP boilerplate_overlap

- 方法: `getTicketsForQueue` vs `postXml`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Queries a REST API for open tickets of a queue and fetches each ticket.
- B 摘要: Sends an XML payload via HTTP POST to a URL and returns the response string.
- 静态失败原因: The static model likely overemphasized common API usage patterns (e.g., HttpURLConnection, BufferedReader) and ignored the distinct control flow, data dependencies, and domain-specific logic, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions serve different purposes (ticket retrieval vs. generic XML posting) and the structural similarity is limited to boilerplate HTTP I/O code, which is not sufficient for even Type-3/4 clones in BCB's criteria.
- 共享行为: Both use HTTP connections to interact with remote servers.；Both read response content line by line using BufferedReader.；Both handle IOException and close streams.；Both set request properties (timeout, content type, etc.).
- 行为差异: A uses GET method; B uses POST method.；A queries for ticket IDs then retrieves each ticket; B sends XML and returns raw response.；A has complex parsing logic (checking for ticket IDs); B simply appends all lines.；A returns a list of RTTicket objects; B returns a String.
- 修正建议: Incorporate data-flow and control-flow embeddings to distinguish core logic from boilerplate.；Use method-level structural features like return type and parameter types.；Apply attention mechanisms sensitive to long-range semantic differences.；Include domain-specific fine-tuning on code with similar boilerplate but different semantics.

### case_id=5847 FN benchmark_preference_bias

- 方法: `doGet` vs `addToArchive`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request for a page, performing access control, logging, caching, and rendering.
- B 摘要: Adds a file entry to a zip archive and returns the URL within the pod.
- 静态失败原因: Static model correctly predicted non-clone based on low token overlap (Jaccard 0.028) and distinct semantics; the error is a false negative relative to the BCB label, which we deem incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'adding an item to a collection/store' (A caches pages, B adds to archive), but the contexts are entirely different and the shared behavior is superficial.
- 行为差异: A is an HTTP servlet method; B is a static utility for zip archives.；A deals with request/response, user permissions, and page rendering; B deals with stream I/O and archive entries.；A has complex control flow and multiple side effects; B is a straightforward pipeline.；A involves persistent storage (database, file cache); B writes to a ZipOutputStream.
- 修正建议: Re-evaluate BCB annotation for this pair; it may be an annotation error.；Use domain-specific filtering to avoid matching HTTP servlet methods with file archiving utilities.

### case_id=5848 FN lexical_or_api_overlap

- 方法: `getWebPage` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.75`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves entire content of a web page as a concatenated string using URL.openStream().
- B 摘要: Downloads or parses OPDS catalog from a URL with HTTP connection handling, redirects, pagination, and file download.
- 静态失败原因: Static BERT/GraphCodeBERT rely heavily on token overlap and API usage patterns; the token Jaccard is extremely low (0.074), and code_b contains many APIs (HttpURLConnection, etc.) absent in code_a. The models fail to capture the high-level semantic similarity of 'fetching web content' due to lack of lexical and structural alignment.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might label them as clones because both involve fetching web content from a URL, but the differences in complexity and purpose are significant; the low token Jaccard and limited overlap suggest BCB's annotation may be lenient or an error.
- 共享行为: Both open a URL and read data from it.
- 行为差异: Code_a is a simple, generic web page fetcher returning a string; Code_b is a complex method handling HTTP specifics, redirects, timeouts, and content types.；Code_b includes state (connection, visited set), GUI updates, and supports pagination and book downloading; Code_a does not.；Code_a uses URL.openStream() directly; Code_b uses HttpURLConnection with custom headers and timeouts.；Code_a throws an Error on failure; Code_b uses onError callback and returns early.
- 修正建议: Use feature extraction focusing on high-level intent (e.g., web fetching) rather than low-level tokens.；Incorporate graph-based representations that capture data flow and API call sequences.；Train with data augmentation that includes diverse implementations of similar functionality.

### case_id=5849 FN partial_functionality

- 方法: `doTransfer` vs `retrieveTemplate`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A method that acts as an HTTP proxy, forwarding a request to a remote URL and returning the response.
- B 摘要: A method that retrieves a blog template URL, reads its content, caches it, and returns it as a string.
- 静态失败原因: The static BERT/GraphCodeBERT model likely focused on lexical token overlap (low Jaccard) and surface-level differences in method names and code structure, missing the abstract semantic similarity of HTTP fetching. The model may also be biased toward exact structural matches, not broad functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this pair as a clone because both functions perform an HTTP GET request to a URL and process the response content, which is a core overlapping functionality despite differences in scope and additional operations.
- 共享行为: Both open a URL connection to a remote resource.；Both read data from the HTTP response stream.
- 行为差异: doTransfer copies request headers and body to the remote server; retrieveTemplate does not.；doTransfer writes the remote response back to the original HTTP response; retrieveTemplate caches the content in a local variable and returns it.；doTransfer handles various HTTP methods and error responses; retrieveTemplate only reads and caches.；doTransfer uses both input and output streams; retrieveTemplate uses only an input stream.
- 修正建议: Incorporate control/data flow analysis to detect common patterns like URL opening and stream reading.；Train on more diverse Type-3/Type-4 clone examples to learn abstract semantics.；Use a model that captures high-level API usage (e.g., URL, HttpURLConnection).

### case_id=5850 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads and reads Twitter timeline as a JSON string via HTTP client.
- B 摘要: Loads a FrameworkFactory instance from a service resource file using class reflection.
- 静态失败原因: The model likely over-relied on the shared I/O patterns (BufferedReader, InputStream, reading lines) and the try-catch blocks, ignoring the distinct method names and the core tasks (HTTP vs reflection). Static BERT lacks understanding of the overall program semantics and domain context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functional similarity beyond I/O boilerplate; these functions have entirely different purposes (web API access vs OSGi service loading), so they would be labeled non-clones.
- 共享行为: Both use BufferedReader to read line-by-line from an input stream；Both involve I/O resource handling and closing；Both return a value (String vs FrameworkFactory)
- 行为差异: Function A performs an HTTP GET request; Function B loads a class from a resource file.；Function A returns a JSON string; Function B returns a reflective instance of FrameworkFactory.；Function A catches specific exceptions; Function B throws Exception.
- 修正建议: Train model with more diverse examples where common I/O patterns appear in semantically different functions.；Include method names and class context in the representation tokenization.；Apply dataflow analysis to capture the distinct data sources and sinks.

### case_id=5851 FP boilerplate_overlap

- 方法: `getWebPage` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a web page from a URL and returns its content as a string, with humorous error handling.
- B 摘要: Retrieves tickets from a Request Tracker queue by making an HTTP GET request, parsing ticket IDs from the response, and fetching each ticket.
- 静态失败原因: Static models like GraphCodeBERT may over-rely on surface-level features such as common API usage (BufferedReader, readLine) and structural patterns (try-catch loops), missing the semantic differences in data processing and overall goal.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions perform entirely different tasks, even if they share common I/O patterns. The overall functionality and purpose differ significantly.
- 共享行为: Both read lines from a BufferedReader in a try-catch block.
- 行为差异: A reads a web page and returns its content; B queries a REST API and processes structured data.；A accumulates all lines into a single string; B parses lines for specific patterns and extracts data.；A throws an Error on failure; B returns null or throws custom exceptions.；B involves multiple HTTP requests (one for search, then each ticket), while A does a single stream read.
- 修正建议: Train on more diverse negative pairs with similar I/O but different logic.；Incorporate data-flow analysis to track how read data is used.；Add attention to API call sequences and external library usage.

### case_id=5852 FN benchmark_preference_bias

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint, saves it locally, and returns the file path.
- B 摘要: Recursively copies a file or directory to another location using byte stream buffering.
- 静态失败原因: The model (static BERT) predicted non-clone correctly from a strict semantic viewpoint; it likely failed to match the BCB label due to low token overlap (0.156) and low structural similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as file-handling utility functions with similar structure (try-catch, stream usage), but this is a very broad interpretation; likely an annotation error.
- 共享行为: Both perform file I/O operations (reading/writing files)；Both handle exceptions
- 行为差异: A downloads from a remote URL, B copies local files；A modifies XML content, B does not；A returns a String, B returns void；A uses channels and DOM parsing, B uses simple byte buffer
- 修正建议: Re-evaluate the BCB annotation for this pair; the functions have fundamentally different purposes.；If considering strict semantics, the model's prediction is correct; adjust benchmark labels accordingly.

### case_id=5853 FP boilerplate_overlap

- 方法: `readRemoteFile` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads the entire content of a remote file from a URL and returns it as a single string.
- B 摘要: Checks for software upgrades by querying a remote server with license information, parsing XML-like response, updating database, and updating UI.
- 静态失败原因: The static model likely overemphasized the superficial common pattern of opening a URL and reading lines, ignoring the vastly different overall semantics and context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clones because the core functionality is completely different; the only similarity is a common I/O pattern that is incidental, not the primary behavior.
- 共享行为: Both open a URL connection and use BufferedReader to read lines.
- 行为差异: readRemoteFile simply returns file content; checkForUpgrade performs complex upgrade logic with database and UI.；checkForUpgrade includes error handling specific to license queries, while readRemoteFile just handles I/O errors.；checkForUpgrade uses multiple database queries and UI updates, absent in readRemoteFile.；The purpose and output are entirely different: one returns a string, the other updates state and shows messages.
- 修正建议: Incorporate more global context or high-level semantic understanding.；Use a contrastive learning approach that penalizes similarity on mere boilerplate patterns.；Improve training data to include examples where common subpatterns appear in non-clone pairs.

### case_id=5854 FN partial_functionality

- 方法: `copyResource` vs `trainClassifier`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies content from a resource (URL or file) to a destination file using a byte-by-byte loop.
- B 摘要: Trains a classifier by executing a command and copying its stdout and stderr to System.out and System.err using IOUtils.copy.
- 静态失败原因: Static BERT likely relied on token overlap and method names (low Jaccard) and missed the abstract stream-copy pattern due to different implementations and contexts.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as stream-copy operations (Type-4) despite different contexts, emphasizing shared I/O pattern over specific functionality.
- 共享行为: Both involve reading from an InputStream and writing to an OutputStream；Both throw Exception for error handling
- 行为差异: Source: A reads from URL or file, B reads from process streams；Destination: A writes to a file, B writes to standard output/error；A uses a manual byte copy loop, B uses IOUtils.copy；A checks resource existence, B constructs command array and executes process
- 修正建议: Enhance model with dataflow analysis to detect stream-copy patterns regardless of surrounding code；Include structural similarity over I/O operations；Use code summarization to capture high-level intent

### case_id=5855 FP long_range_semantics

- 方法: `uploadFile` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Uploads a file by renaming or copying bytes from input to output.
- B 摘要: Parses configuration data from a file to populate character sets and hash maps for Tibetan transliteration.
- 静态失败原因: The model likely over-relied on superficial structural patterns (e.g., multiple loops and conditionals) while ignoring the distinct data flow and high-level semantics, leading to a false positive despite very low token overlap.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB prefers labeling as non-clone because the functions have no functional similarity; one is a file utility, the other is a data initialization routine.
- 共享行为: Both involve file I/O operations
- 行为差异: Different purposes: file upload vs. data parsing；Different data structures and logic；Different control flow complexity
- 修正建议: Incorporate method name and documentation context；Use contrastive learning to distinguish dissimilar long functions；Improve model's ability to capture overall program purpose

### case_id=5856 FP lexical_or_api_overlap

- 方法: `getUser` vs `GetResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from a database or a local config file by login name.
- B 摘要: Retrieves HTTP response content from a URL using a GET request.
- 静态失败原因: The model over-relied on lexical and API similarities (BufferedReader, InputStreamReader, while loop, try-catch) and the shared pattern of reading from a stream, ignoring the semantic difference between local file I/O and HTTP communication.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the functions perform entirely different domain tasks (user management vs. HTTP client) despite superficial structural similarities.
- 共享行为: Both use BufferedReader to read line-by-line from an input stream；Both handle I/O exceptions with try-catch；Both return a string-like object (User contains strings)
- 行为差异: Reads from a local file vs. fetches from remote HTTP connection；Parses tokenized line to create User object vs. concatenates raw response lines；Interacts with database via DAO vs. pure HTTP response retrieval；URL comes from classpath resource vs. method parameter
- 修正建议: Incorporate dataflow analysis to distinguish local file versus network resource；Use type information of returned objects (User vs String) and method signatures；Include more diverse negative examples with similar structural patterns but different semantics

### case_id=5857 FP lexical_or_api_overlap

- 方法: `getDatasetsList` vs `getUser`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a list of dataset names from a remote server URL with caching.
- B 摘要: Loads a user from a local config file by login name with caching via DAO.
- 静态失败原因: Static BERT models may over-rely on lexical and API-level similarities (URL, BufferedReader, while loop, try-catch) and fail to capture the distinct semantics of the read-loop body and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators likely considered these non-clones because the core functionality and output types differ significantly, despite some structural overlap in reading and caching.
- 共享行为: Both read from a URL or resource using BufferedReader and line-by-line iteration；Both implement caching: A with HashMap, B with DAO；Both handle exceptions and manage resource closing
- 行为差异: A gets a list of all lines; B parses colon-separated tokens to find a matching user；A constructs URL with query parameter; B loads from classpath resource；A is synchronized; B is not；A throws RuntimeException on error; B prints stack trace and returns null
- 修正建议: Train on more diverse pairs that share structural patterns but differ in logic；Incorporate dataflow or control-flow analysis to distinguish read vs parse operations；Use contrastive learning with negative examples that have API overlap but different semantics

### case_id=5858 FN partial_functionality

- 方法: `createOutputStream` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Filters and recompresses a zip file, skipping 'content.xml' initially then adding it last, using character streams.
- B 摘要: Downloads a KMZ file and extracts all its entries to individual files using byte streams.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on low token overlap (Jaccard=0.229) and surface API differences (e.g., ZipOutputStream vs FileOutputStream, character vs byte streams), missing the shared while-loop iteration over zip entries that defines their functional similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels broad Type-3/Type-4 clones where high-level functionality (zip entry processing) is similar despite differences in I/O details, encoding, and output form. The core loop structure is considered a clone pattern.
- 共享行为: Both process zip files by iterating over ZipEntry objects；Both read data in chunks and write to an output；Both use a while loop with getNextEntry()
- 行为差异: A writes to a ZipOutputStream (compressed), B writes to FileOutputStream (files)；A selectively reorders and renames entries; B extracts all entries as-is；A uses character streams (Reader/Writer), B uses byte streams；A returns a BufferedWriter, B prints progress and closes stream
- 修正建议: Incorporate structural AST or CFG features to capture loop and I/O patterns；Use data-flow analysis to recognize zip stream processing；Add training examples of zip processing with varying APIs to learn the high-level similarity

### case_id=5859 FN partial_functionality

- 方法: `setImg` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens a file chooser to select an image, copies it to a local 'images' directory, and sets the image as an ImageIcon.
- B 摘要: Retrieves a resource by URL, caches it locally, and returns an InputStream to the cached file, with conditional caching logic.
- 静态失败原因: Static BERT models like CodeBERT may focus on token overlap and syntactic patterns; the two functions share common tokens like 'File', 'InputStream', 'FileOutputStream', 'while', 'read', 'write', 'try', 'catch', but the overall semantic context is different, leading to a false negative if the model prioritized semantic meaning over structural similarity
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as Type-4 clones because they perform file I/O copying with similar stream handling and exception patterns, ignoring high-level purpose differences
- 共享行为: Both copy data from an input stream to an output file using a byte-by-byte loop；Both handle exceptions with printStackTrace
- 行为差异: A uses a GUI file chooser and copies to a fixed directory, while B uses URLConnection and caches with hashtable；A writes to disk and then sets an ImageIcon, while B returns a FileInputStream；A deals with image-specific logic, B deals with HTTP caching
- 修正建议: Consider adding more context about method names and surrounding class；Use graph-based models that capture dataflow；Incorporate API call sequences to distinguish GUI vs networking

### case_id=5860 FN lexical_or_api_overlap

- 方法: `doGet` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles HTTP GET requests by retrieving a page, checking visibility, logging, and writing a cached response.
- B 摘要: Retrieves a file from the user directory or copies a resource from the classpath to the user directory.
- 静态失败原因: The static model correctly predicted non-clone because token overlap is very low and AST structures differ vastly; no failure occurred.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have erroneously labeled as clone due to annotation noise or inconsistent criteria; there is no apparent functional similarity.
- 行为差异: Function A is a servlet doGet method handling web requests with complex logic; Function B is a simple file retrieval utility.；Function A involves HTTP request/response objects, page rendering, caching, and logging; Function B only deals with file I/O and resource loading.；Function A has extensive error handling and permission checks; Function B has minimal error handling.
- 修正建议: Review BCB label for potential annotation error; if label is correct, consider that BCB might accept very broad similarity, but this pair seems unrelated.；Ensure consistent annotation guidelines; for future models, low token Jaccard and different method signatures are strong indicators of non-clones.

### case_id=5861 FN benchmark_preference_bias

- 方法: `addIDs` vs `doRawRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Parses an online database to retrieve metabolite IDs and scores and updates a row object.
- B 摘要: Sends a POST request and returns the raw response string.
- 静态失败原因: The model correctly predicted non-clone due to low token overlap (Jaccard=0.1085) and distinct control flows. BCB's preference for broad semantic similarity caused the false negative annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider both as 'URL-based data retrieval' functions, thus a Type-4 clone based on high-level purpose, ignoring implementation details.
- 共享行为: Both open a URL connection and read lines via BufferedReader.
- 行为差异: Different HTTP methods (GET vs POST)；Different return types (int vs String)；A does complex HTML parsing and updates a data object; B returns entire response；Different exception handling
- 修正建议: Increase tolerance for high-level I/O tasks；Incorporate deeper semantic understanding of function purpose

### case_id=5862 FN partial_functionality

- 方法: `getFile` vs `copyTo`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a given URL, processes XML to modify an endpoint attribute, saves to a temporary file, and returns the file path.
- B 摘要: Recursively copies a file or directory to a destination, using NIO FileChannel for data transfer.
- 静态失败原因: Low token overlap (12.9%) and different method names led the model to focus on surface semantics (downloading vs copying) rather than the shared I/O structure using FileChannel.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels clones based on partial functional similarity or shared implementation patterns, such as common use of NIO FileChannel for file transfer, despite different high-level tasks.
- 共享行为: Uses FileChannel to transfer data from a source to a destination；Creates new files (createNewFile)；Handles IOException
- 行为差异: A downloads over network from a URL; B copies locally from a File；A includes XML parsing and modification; B does not；A creates temporary files and renames them; B does not；A returns a String; B returns void
- 修正建议: Incorporate structural features like AST or control-flow graphs to capture shared I/O patterns；Use data flow analysis to recognize similar sequences of operations (open channel, transfer, close)；Increase weight on API usage patterns in addition to token overlap

### case_id=5863 FP lexical_or_api_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Prolog file, parses it, generates adapter classes, and writes them to a JAR file.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: The static model likely over-relied on shared API tokens (e.g., File, IOException) and common Java boilerplate, ignoring the vast difference in overall purpose and complexity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because there is no functional similarity; one is a main method for adapter generation, the other is a utility for file copying.
- 行为差异: Function A involves complex parsing, code generation, and I/O with multiple files; Function B is a simple file copy.；Function A uses many external libraries (PrologParser, FactVisitor, ClassWriter); Function B uses only standard I/O.；Function A has error handling for multiple steps; Function B declares IOException and has no error handling.
- 修正建议: Include structural or semantic features (e.g., control flow, data flow) to distinguish high-level behavior.；Use contrastive learning on pairs with similar API usage but different semantics.

### case_id=5864 FN boilerplate_overlap

- 方法: `main` vs `issueCommandToServer`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: main method that makes a specific HTTP POST request with hardcoded parameters to RenRen API and prints the response.
- B 摘要: generic method that sends a command and capsule to a server via HTTP POST and returns the response as a string.
- 静态失败原因: Low lexical overlap (token Jaccard 0.13) and different method signatures and structures led the model to miss the underlying functional similarity in HTTP request handling.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers both as functions for sending data to a server via HTTP and reading the response, focusing on the common boilerplate pattern of network communication.
- 共享行为: Both perform an HTTP POST request to a server.；Both use URLConnection to open a connection.；Both read the response line by line using BufferedReader.
- 行为差异: A is a static main with debug prints; B is a protected method returning a string.；A constructs parameters and appends them to URL (missing POST body); B writes command and capsule data to output stream.；A uses HttpURLConnection explicitly and sets request method; B uses URLConnection without setting method.；A has hardcoded parameters; B receives command and capsule as arguments.
- 修正建议: Use graph-based representations that capture the sequence of network API calls.；Incorporate dataflow analysis to track that both methods involve opening a connection, sending data, and reading response.；Train on more diverse examples of network communication patterns.

### case_id=5865 FN benchmark_preference_bias

- 方法: `_checkLanguagesFiles` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Iterates over language entries and initializes property files by creating missing files and copying from global to temporary.
- B 摘要: Builds a site for editing by iterating over pages, reading XML, performing XSLT transformation, and writing output files with post-processing.
- 静态失败原因: The model correctly detected low token overlap and structural differences, leading to a non-clone prediction; however, it failed to recognize the potential abstract similarity of initializing files for editing as a common CMS task, which a human annotator might consider.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones based on a broad interpretation of both being file-processing routines within a CMS, focusing on the high-level task of initializing or building resources for editing, despite different implementations.
- 共享行为: Both methods iterate over a collection (languages/pages) and perform file I/O operations in a loop.
- 行为差异: Different inputs: A uses request attributes, B uses multiple path and property parameters.；Different operations: A creates and copies files, B reads XML, transforms via XSLT, and writes HTML.；Different complexity: A is small and straightforward, B is large with many steps including debugging and error handling.；Different output: A modifies local file system, B produces website files.
- 修正建议: Use domain-specific pre-training or fine-tuning on CMS codebases to capture high-level task semantics.；Incorporate abstract representations that model the overall purpose beyond token-level patterns.；Consider multi-modal features that combine code structure with documentation or comments.

### case_id=5866 FN benchmark_preference_bias

- 方法: `doGet` vs `trainClassifier`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests for pages, including permission checks, caching, and logging.
- B 摘要: Trains a classifier by executing an external command with file arguments and copying output streams.
- 静态失败原因: Static BERT/GraphCodeBERT correctly identified the low token overlap and distinct API usage, leading to a non-clone prediction. The model did not fail; rather, the BCB annotation may be noisy or based on very abstract similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered them clones due to both involving system calls (A: file operations, B: process execution) and configuration retrieval, but the behavioral divergence is too large for a typical BCB clone.
- 共享行为: Both perform file I/O operations (A: cache file, B: model file).；Both use property values (A: Property.getProperty, B: this.getCommand/getModelName).
- 行为差异: A is a web request handler; B is a model training routine.；A has complex logic with multiple conditions and loops; B is a straightforward command execution.；A uses servlet API and database interactions; B uses Runtime.exec and stream copying.；A handles user permissions and page rendering; B does not involve user interaction.
- 修正建议: Review and correct BCB annotations for this pair to ensure consistency.；Consider adding more training examples with high-level structural differences.

### case_id=5867 FN dataflow_blindspot

- 方法: `getResourceAsStream` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `dynamic_equivalence_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves a resource from a URL with caching and returns its input stream.
- B 摘要: Copies a file from source to destination using file channels.
- 静态失败原因: Static BERT had low token overlap (Jaccard=0.076) and different method names, so it missed the common I/O dataflow pattern that BCB might recognize as similar.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本可能是 API 写法不同但行为等价的漏报。建议测试目标为 input_output_equivalence。
- BCB 偏好解释: BCB may view both as implementing a general pattern of reading from a source and writing to a destination, considering them Type-4 clones despite different types and complexity.
- 共享行为: Both perform file I/O involving reading from a source and writing to a destination.；Both handle stream closing with proper resource management.
- 行为差异: A includes caching, HTTP connection, and conditional logic; B is a simple file copy.；A uses BufferedInputStream and BufferedOutputStream; B uses FileChannel.；A returns an InputStream; B is void.；A handles multiple exceptions with printStackTrace; B uses try-finally.
- 修正建议: Train on more examples of I/O patterns with varied implementations.；Incorporate dataflow analysis or graph-based representations.

### case_id=5868 FP lexical_or_api_overlap

- 方法: `importSequences` vs `PhoneSetImpl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Imports sequences from a URL by reading FASTA-like format with '>' markers.
- B 摘要: Constructs a PhoneSetImpl by reading from a URL and parsing lines that do not start with '***'.
- 静态失败原因: Static BERT may have focused on overlapping tokens like 'URL', 'openStream', 'reader', 'line', and loop structure, missing semantic differences in parsing logic and data handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions perform different domain-specific tasks (sequence import vs. phone set construction) despite structural similarities like reading from URL.
- 共享行为: Both open a URL stream and read lines in a loop；Both process each line based on a condition
- 行为差异: A uses ImportHelper and reads sequences with specific delimiters; B uses plain BufferedReader.；A stores names and sequences in separate lists; B stores parsed data into a map.；A handles multiple sequences with '>' separators; B processes all lines uniformly.；Different exception handling: A catches multiple exceptions; B throws IOException.
- 修正建议: Incorporate structural and semantic differences in parsing logic and data structures.；Use control flow and data flow analysis to distinguish specific I/O patterns.；Train on more diverse examples of URL reading tasks with different parsing semantics.

### case_id=5869 FN partial_functionality

- 方法: `loadMFileViaWeb` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads a MATLAB function file from a URL and parses it into a UserFunction object.
- B 摘要: Queries a geocoding/parsing web service with an XML request, reads the XML response, and extracts place name and gazetteer ID tuples.
- 静态失败原因: Static BERT models rely on token-level embeddings and may have been misled by low token Jaccard (0.113) to predict non-clone. They fail to capture the abstract structural pattern that BCB considers, thus diverging from BCB's annotation.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as clone because both functions follow a high-level 'web data loader' pattern: construct URL, open stream, read data, parse, and return. This pattern matches Type-3 (near-miss) or Type-4 (semantic) clone criteria, overlooking domain and detailed processing differences.
- 共享行为: Open a URL and read lines using BufferedReader；Use try-catch for exception handling；Return a processed object after parsing
- 行为差异: Input parameters: A takes codeBase, directoryAndFile, mFileName; B takes recordContent and getGazeteerIds；URL construction and destination service are completely different；Data format: A reads plain text (MATLAB code), B reads XML；Parsing logic: A uses FunctionParser, B uses XML DOM parsing with DocumentHelper
- 修正建议: Incorporate data-flow or control-flow graphs to distinguish different processing logic；Use program synthesis or higher-level semantic analysis to recognize the shared pattern；Fine-tune with more training examples of Type-3/Type-4 clones to align with BCB preferences

### case_id=5870 FN partial_functionality

- 方法: `getHTML` vs `getJSONData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML content from a URL using HttpURLConnection, reads it line by line, optionally writes to a file, and returns the complete HTML string.
- B 摘要: Fetches JSON data from a URL using HttpClient, reads it line by line, parses it to a JSONObject, and returns the JSONObject.
- 静态失败原因: Static BERT models like GraphCodeBERT may fail because they rely on token-level similarities and structural differences. The functions have different method names, use different HTTP libraries (HttpURLConnection vs DefaultHttpClient), and different return types. The token Jaccard is low (0.276), and the model likely focused on these surface-level differences rather than the underlying data flow pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because they both perform the core task of fetching content from a URL and reading it line by line, which is a common pattern. The differences in output type (String vs JSONObject) and HTTP client are considered implementation details, and BCB often considers such pairs as Type-3/Type-4 clones.
- 共享行为: Both open a URL connection；Both read the response line by line using BufferedReader；Both handle exceptions with printStackTrace
- 行为差异: getHTML returns a String (HTML) and optionally writes to a file; getJSONData returns a JSONObject (parsed JSON)；getHTML uses HttpURLConnection; getJSONData uses DefaultHttpClient and HttpGet；getJSONData parses the response with JSONTokener; getHTML does not parse
- 修正建议: Improve model to recognize common URL fetching patterns despite different HTTP client usage；Use data flow analysis to capture the pattern of connecting to a URL and reading lines；Add more training examples of pairs that share core behavior but differ in output processing

### case_id=5871 FP boilerplate_overlap

- 方法: `main` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a fixed URL and prints each line to standard output.
- B 摘要: Searches Google Images for an artist and album, downloads the HTML, and extracts image URLs into a list.
- 静态失败原因: The static model likely focused on the high lexical overlap in the URL reading code (URL, BufferedReader, while readLine, close) and ignored the surrounding context and different purposes, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because the overall functionality is completely different: one is a trivial URL printer, the other is a complex image search parser. Despite sharing I/O boilerplate, the core task and output are dissimilar.
- 共享行为: Open a URL and read lines using BufferedReader；Close the reader after reading
- 行为差异: Function A is a main method; B is an instance method；A uses a fixed URL; B constructs a dynamic URL with query parameters；A prints lines directly; B processes HTML to extract image URLs；A does not handle exceptions; B catches exceptions and shows error dialog
- 修正建议: Use contrastive learning to reduce weight on common I/O patterns；Incorporate dataflow analysis to capture how data is used after reading；Augment training data with similar non-clone pairs that share boilerplate but differ in logic

### case_id=5872 FN partial_functionality

- 方法: `doRawRequest` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends HTTP POST to a fixed URL with provided postData and returns the raw response as a string.
- B 摘要: Sends HTTP POST to a dynamically constructed URL with JSON arguments, handles HTTP errors, returns deserialized object, and retries on connection timeout.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low token overlap (Jaccard 0.138), different API usage (java.net vs. Apache HttpClient), and structural differences (B has retry logic, error handling, and JSON parsing) that obscure the underlying common HTTP POST behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions implement the core functionality of making an HTTP POST request and reading the response, which is considered a semantic similarity despite differences in libraries, error handling, and additional features.
- 共享行为: Both perform HTTP POST requests to a URL；Both read the response line by line using a BufferedReader；Both return the response content (though B does additional processing)
- 行为差异: A uses java.net.URLConnection, B uses Apache HttpClient (HttpPost)；A has no error handling, B checks HTTP status codes and throws exception；B includes retry logic on ConnectTimeoutException；B deserializes JSON response to a typed object, A returns raw string
- 修正建议: Use data-flow analysis to abstract HTTP operations to a common representation；Incorporate library-aware normalization (e.g., map URLConnection and HttpClient to shared concepts)；Utilize graph-based representations that capture request/response patterns despite control flow variations

### case_id=5873 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads Twitter timeline JSON via HttpClient, checks status, returns response body as string.
- B 摘要: Reads a local JSP page via URL stream and discards all content, returning void.
- 静态失败原因: Static BERT likely over-relied on common token patterns (BufferedReader, InputStreamReader, while loop, try-catch) and overlooked semantic differences (return vs void, content usage).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because of differing API usage, return types, data processing, and error handling; high-level URL reading may not suffice for Type-4 similarity.
- 共享行为: Both open an HTTP connection to a URL.；Both read lines using BufferedReader and InputStreamReader.；Both handle IOException and MalformedURLException.
- 行为差异: A uses HttpClient; B uses URL.openStream().；A checks HTTP status code; B does not.；A accumulates lines into StringBuilder and returns it; B discards lines and returns void.；A has active error logging; B has empty catch blocks.
- 修正建议: Incorporate data-flow analysis to check if read content is used.；Consider method signature (return type) and parameter usage.；Distinguish between different HTTP client APIs (HttpClient vs URL).

### case_id=5874 FN partial_functionality

- 方法: `copyResource` vs `createNew`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file using byte-by-byte reading.
- B 摘要: Creates a new file in a directory from an InputStream, with ownership validation and logging, using IOUtils.copy.
- 静态失败原因: Low token overlap (0.1) and different structure; BERT may not capture semantic similarity between a manual byte loop and IOUtils.copy, and extra conditionals obscure the core copy behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers Type-4 clones where core functionality is writing an input stream to a file, despite different APIs and extra logic.
- 共享行为: Both copy data from an input source to a file output stream.
- 行为差异: A reads from URL or local file; B receives InputStream directly.；A checks resource existence; B checks ownership and special file names.；A uses byte-by-byte copy; B uses IOUtils.copy (buffered).；A returns void; B returns Resource object.
- 修正建议: Train on more Type-4 examples with different APIs.；Incorporate data flow analysis to identify core I/O operations.；Use AST-based features to highlight similar substructures like stream copy.

### case_id=5875 FN benchmark_preference_bias

- 方法: `copyDeleting` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file by reading bytes from source and writing to destination.
- B 摘要: Launches a project configuration process that validates project structure, handles XML files, sets properties, and creates a reverse engineering file from a resource.
- 静态失败原因: The model correctly predicted non-clone (0) based on low structural and semantic overlap; the BCB label (1) appears to be an error or overly broad interpretation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have annotated this as a clone due to the presence of file copying behavior in both, considering partial functionality similarity (Type-4), but the overall purpose and complexity differ substantially.
- 共享行为: Both involve file I/O operations but at different levels and contexts.
- 行为差异: copyDeleting is a simple file copy; launch is a complex multi-step configuration task.；launch includes XML parsing, property setting, project management, and error handling; copyDeleting has none.；launch uses byte array streams and resource copying; copyDeleting uses direct file streams.
- 修正建议: Ensure clone annotations focus on core functional equivalence; revise BCB label for this pair to 0.

### case_id=5876 FP partial_functionality

- 方法: `getZipAsFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Extracts the content of a DigitalObject into a temporary zip file and returns the file.
- B 摘要: Handles various GUI action commands by opening file choosers, saving preferences, and updating UI components.
- 静态失败原因: The model likely over-relied on surface-level similarities like File objects, IOException handling, and general structure, missing the distinct domain contexts (data extraction vs GUI event handling) and the vast difference in scope.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB considers them non-clones because despite both involving files, the semantic intent and overall functionality are completely different; they are not even partially related.
- 共享行为: Both involve File objects and IO operations with exception handling.；Both are part of larger systems dealing with file management.
- 行为差异: Function A is a focused utility for extracting a zip file from a digital object.；Function B is a lengthy event handler managing multiple GUI actions and preferences.；They have different inputs (DigitalObject vs ActionEvent) and different outputs (File vs void).；Control flow differs significantly: linear in A, event-driven branching in B.
- 修正建议: Incorporate attention to method names and class context to distinguish utility vs event handler.；Use dataflow analysis to capture differing input-output behaviors.；Train on more diverse examples to reduce bias toward generic file operations.

### case_id=5877 FP boilerplate_overlap

- 方法: `main` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Main method for generating adapter JAR from a Prolog file using command-line arguments.
- B 摘要: ActionPerformed method handling GUI events to update user preferences in a genealogy application.
- 静态失败原因: Static BERT models may focus on surface-level lexical and structural similarities (e.g., common Java idioms, try-catch blocks, conditional statements) and fail to capture the deeper semantic divergence in function purpose and domain.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions serve entirely different purposes (batch file generation vs GUI event handling) despite sharing some common Java boilerplate patterns.
- 共享行为: Both use conditional logic to handle different cases；Both involve file I/O and exception handling；Both use System.out.println for output
- 行为差异: Function A processes command-line arguments and generates a JAR file；Function B handles GUI events and updates application preferences；Function A has no GUI interaction；Function B has no file generation logic
- 修正建议: Incorporate data flow and call graph analysis to distinguish between different application domains；Use contrastive learning with negative sampling of semantically different but lexically similar pairs；Add task-specific contextual embeddings (e.g., method name, class context)

### case_id=5878 FP lexical_or_api_overlap

- 方法: `scrapeForIsbns` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Scrapes ISBN-10 codes from a given URL by reading lines and matching a regex pattern, with retry logic on connection failures.
- B 摘要: Searches Google Images for album art by constructing a query URL, fetching the HTML, and extracting image URLs via string splitting.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by lexical and API overlaps such as 'URL', 'BufferedReader', 'InputStreamReader', 'openStream', 'readLine', and 'Pattern'. These common web scraping constructs dominate token-level similarity, causing the model to overestimate functional similarity despite different domain and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions serve different specific purposes (ISBN extraction vs image URL extraction), despite both being web scraping. The structural similarities are at a high API level, but the core algorithms and input/output differ significantly.
- 共享行为: Both open a URL connection and read data via BufferedReader；Both use regex or pattern matching to extract specific substrings from the fetched content；Both handle I/O exceptions with try-catch blocks
- 行为差异: Function A takes a URL parameter and returns an integer count; Function B has no parameters and returns void；Function A retries up to RETRIES times on connection failures; Function B has no retry logic；Function A extracts ISBN-10 codes using a regex on each line; Function B extracts image URLs by splitting the entire HTML text；Function B has a conditional on artist change to proceed; Function A always processes
- 修正建议: Incorporate data flow and control flow graph features；Integrate semantic role labeling to distinguish extraction purposes；Train with more examples of functions sharing API but differing in domain

### case_id=5879 FP lexical_or_api_overlap

- 方法: `getUser` vs `fetchUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Gets a user by login, first loading from DAO, then falling back to a config file and saving to DAO if found.
- B 摘要: Fetches the content of a URL as a string, returning empty string on failure.
- 静态失败原因: Static BERT/GraphCodeBERT likely over-emphasized the lexical overlap of URL, BufferedReader, InputStreamReader, and while loop patterns, while missing the high-level semantic difference (authentication vs URL fetching).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when two functions have completely different purposes and implementations, even if they share some low-level API calls.
- 共享行为: Both use BufferedReader to read from an input stream；Both handle IOException
- 行为差异: Function A writes to DAO, Function B returns the content；Function A parses lines with StringTokenizer, Function B concatenates all lines；Function A throws no exceptions (catches all), Function B catches specific exceptions；Function A's source is a classpath resource, Function B's source is a URL
- 修正建议: Add more discriminative training on high-level semantics；Use data flow or control flow features to distinguish different tasks；Increase weight on method-level context (e.g., method name, class dependencies)

### case_id=5880 FN benchmark_preference_bias

- 方法: `copy` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a single file to another using NIO FileChannel transfer.
- B 摘要: Builds a website for editing by reading configuration, transforming XML, and writing output files.
- 静态失败原因: Low token Jaccard (0.0588) and differing method names led the model to predict non-clone. The static model likely lacks understanding of overarching task similarity and is biased by surface-level lexical features.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a Type-4 clone based on partial functionality: both methods involve file I/O (read and write), but the overall semantics differ greatly. The annotation might have been influenced by the presence of common Java I/O APIs.
- 共享行为: Both use FileInputStream to read a file.；Both write output to files.；Both handle IOException.
- 行为差异: A copies a single file; B processes multiple files and applies transformations.；A uses FileChannel.transferTo; B uses character buffers and string operations.；B involves XML parsing, DOM manipulation, and property handling; A has no such logic.
- 修正建议: Incorporate task-level reasoning (e.g., intent classification) to recognize broad I/O operations as clones.；Use data-flow or control-flow analysis to detect structural similarities beyond token overlap.；Review BCB annotations for consistency in partial-functionality clones.

### case_id=5881 FP lexical_or_api_overlap

- 方法: `doRawRequest` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends HTTP POST request with postData and returns response body as string.
- B 摘要: Performs Google image search by constructing a query URL, fetching HTML, and extracting image URLs to a list, with conditional execution based on artist change.
- 静态失败原因: The static BERT model likely overemphasized the lexical similarity of URL, URLConnection, BufferedReader, while loop for reading lines, and the general structure. It may have missed the crucial difference that one writes before reading and the other only reads, and that one has significant parsing and conditional logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have different input/output behavior and distinct purpose, even if they share common boilerplate code like HTTP request setup and response reading. The writing of data vs. no writing, and the parsing logic, are major functional differences.
- 共享行为: Both open an HTTP URL connection.；Both read the response line by line using BufferedReader.
- 行为差异: Function A writes data (postData) to the request; function B does not write any data.；Function A returns the entire response string; function B parses the response to extract image URLs and adds them to a list.；Function A lacks error handling; function B has a try-catch block and error dialog.；Function B includes a condition to check if artist has changed before executing the search; function A has no such guard.
- 修正建议: Train with more negative examples that share API usage but differ in data flow and control logic.；Incorporate dataflow analysis to distinguish write operations from read-only operations.；Use structural differencing to capture distinct control flow paths (e.g., conditionals, loops).

### case_id=5882 FN lexical_or_api_overlap

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file by reading and writing byte by byte.
- B 摘要: Copies a source file to a destination file using NIO FileChannel transferFrom for efficient transfer.
- 静态失败原因: Static BERT models rely on token similarity and API patterns; low token Jaccard (0.235) and different method names, parameters, and I/O classes lead to prediction of non-clone, missing the functional equivalence.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: None
- 共享行为: Both copy content from a source to a destination file.
- 行为差异: A reads from a URL or file; B reads only from a file.；A uses byte-by-byte streaming; B uses NIO channels with transferFrom.；A uses InputStream/OutputStream; B uses FileChannel.；A throws Exception, B throws IOException with proper resource cleanup in finally.
- 修正建议: Incorporate dataflow or program dependence graphs.；Use structure-based features (AST, CFG).；Train with contrastive learning on functional equivalence.；Include I/O type and resource handling patterns.

### case_id=5883 FN partial_functionality

- 方法: `copyResource` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file path to a destination file, reading byte by byte.
- B 摘要: Copies a file from source path to destination path using a buffer.
- 静态失败原因: Static BERT relied on low token overlap (0.294) and focused on surface-level differences like method signatures and control flow, missing the high-level semantic similarity of copying functionality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers them clones because both implement the same core task of copying data to a file, and the differences (URL vs file, buffering) are treated as syntactic variations typical of Type-3 clones.
- 共享行为: Both copy bytes from an input stream to an output stream；Both use FileOutputStream for output；Both close streams after copying
- 行为差异: A can open URLs; B only files；A reads byte by byte; B uses a 1024-byte buffer；A does not use try-finally; B does；A throws Exception; B throws IOException
- 修正建议: Enhance training with examples that share core behavior despite different inputs or source resolution；Incorporate dataflow analysis to capture information transfer from input to output；Use task-level embeddings to represent overall functionality

### case_id=5884 FP lexical_or_api_overlap

- 方法: `writeFileType` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a file of URIs, opens each URL, checks first 100 lines for OWL/RDFS/RDF namespaces, and writes the classification to an output file.
- B 摘要: Downloads an RDF model from a given URL using Jena library with appropriate HTTP headers and returns the Model object.
- 静态失败原因: The token overlap includes 'URL', 'InputStream', 'BufferedReader', 'RDF', 'OWL', and try-catch structure, which may have misled the model into thinking they are clones, ignoring the different purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this non-clone because the overall functionality (file classification vs model download) differs significantly, despite shared I/O patterns.
- 共享行为: Both open a URL connection and read from its input stream
- 行为差异: A processes multiple URIs from a file and writes results; B processes a single URL and returns a Model；A uses simple string matching to detect namespaces; B uses Jena to parse the full RDF model；A logs progress to stderr and continues on error; B throws RuntimeException on failure；B sets HTTP request headers; A does not
- 修正建议: Incorporate dataflow analysis to capture return types and library usage (e.g., Jena vs. manual parsing)；Add attention to high-level intent (e.g., output file vs. returning model)；Use contrastive learning to distinguish similar-looking IO operations with different goals

### case_id=5885 FN boilerplate_overlap

- 方法: `doVersionCheck` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for a newer version of jEdit by fetching a version file from a URL, parsing .version and .build lines, and notifying user if update is available.
- B 摘要: Sends a POST request to RenRen API with parameters to publish a templatized action, then prints the response.
- 静态失败原因: The functions have low token overlap (Jaccard 0.14) and use different domain-specific vocabulary (jEdit vs RenRen). Static BERT models often rely on surface-level lexical and structural patterns; here the common boilerplate is too generic to trigger a clone classification.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might consider both as network I/O routines with similar boilerplate (URL, BufferedReader), but the domain-specific purpose and output behavior are distinct, making them unlikely clones even under BCB's broad criteria.
- 共享行为: Both open a URL connection and read input line by line using BufferedReader.；Both handle IOException with try-catch.
- 行为差异: Function A performs a version check; Function B sends a POST request to an API.；Function A uses URL.openStream() (GET); Function B uses HttpURLConnection with POST.；Function A parses lines for specific prefixes; Function B prints all lines.；Function A shows UI messages; Function B prints to console.
- 修正建议: Incorporate more detailed semantic analysis beyond token overlap.；Use data flow or program dependency graphs to capture actual behavior differences.；Train on pairs with similar boilerplate but different intent to reduce false negatives.

### case_id=5886 FP lexical_or_api_overlap

- 方法: `readAndRewrite` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads a DICOM image file, parses metadata and pixel data, then writes the data to an output file.
- B 摘要: Parses comma-separated token strings to populate sets and hash maps for Tibetan/Sanskrit character mapping initialization.
- 静态失败原因: Static models may rely on superficial similarities like both having 'read' in the method name, both using loops and try-catch blocks, and both involving parsing operations, even though the actual API usage and domain specific logic are entirely different.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically regards Type-4 (functionally different) code as non-clones; these two methods have completely different domains and purposes, so they are correctly labeled non-clones.
- 共享行为: Both perform input parsing using iterators；Both use System.out.println for logging or error messages
- 行为差异: Function A processes DICOM image data with specific libraries (ImageIO, DcmParser, etc.)；Function B processes configuration strings to build lookup tables；Function A performs file I/O (reading and writing images)；Function B only reads from string fields and populates data structures
- 修正建议: Incorporate more fine-grained semantic features such as API call sequences and data flow；Use a larger context window to capture the surrounding class or method dependencies；Train on more diverse examples to recognize domain-specific differences

### case_id=5887 FN benchmark_preference_bias

- 方法: `convert` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Converts an ACRNEMA file to DICOM format by parsing pixel data and adding UIDs.
- B 摘要: Handles an HTTP GET request for a portal page, checking permissions and rendering the page output.
- 静态失败原因: The static model correctly predicted non-clone because the functions have minimal lexical overlap (token Jaccard 0.085) and no semantic similarity in functionality or structure.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to a misinterpretation of partial functionality similarity, such as both performing I/O operations and exception handling, but the specific domains and logic are entirely different.
- 共享行为: Both involve reading input and writing output streams.；Both use try-finally blocks for resource management.；Both include conditional logic and error handling.
- 行为差异: Function A is a file format converter; Function B is an HTTP request handler.；Function A processes binary pixel data; Function B processes HTTP parameters and page content.；Function A writes to a file; Function B writes to an HTTP response.；Function A deals with DICOM tags; Function B deals with portal page objects and user permissions.
- 修正建议: Review BCB annotation for potential mislabeling.；Improve model training data to avoid overgeneralization of I/O patterns as clone indicators.

### case_id=5888 FN partial_functionality

- 方法: `main` vs `doRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, unzips it, and extracts each entry to a local file.
- B 摘要: Handles an HTTP request by mapping a path alias to an internal resource, opening a stream, and copying it to the response output stream.
- 静态失败原因: Static BERT or GraphCodeBERT models often rely on token overlap and structural similarity. Here the token Jaccard is very low (0.1089), and the code structures are quite different. The model likely failed to recognize the functional similarity because it cannot abstract away the different surrounding contexts (zip handling vs. path mapping) and focus only on the core stream copy operation.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these Type-4 clones because the core task of reading from a network resource and writing to an output stream is shared, despite different contexts and additional processing. The low token overlap suggests they are not structurally similar, but functional similarity in stream copy might be enough for BCB's broad clone classification.
- 共享行为: Both open an InputStream from a URL-like resource；Both copy the input stream to an output stream；Both handle potential null or protocol conditions
- 行为差异: A is a main method with no request/response context; B is a servlet method handling request/response；A downloads a specific URL; B serves internal resources based on alias mapping；A involves zip decompression; B does not；A writes to local files; B writes to HTTP response
- 修正建议: Train models to recognize functional similarity beyond token overlap, possibly using dataflow or program dependence graphs.；Use techniques like code summarization or contrastive learning that focus on high-level intent.；Incorporate knowledge of common library usage (e.g., IOUtils.copyAndClose) as a hint for similar behavior.

### case_id=5889 FN lexical_or_api_overlap

- 方法: `copyResource` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file path to a destination file by reading and writing bytes.
- B 摘要: Reads a DICOM file, processes pixel data, and rewrites it to another file using DICOM-specific APIs.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on lexical and structural similarity. With a token Jaccard of 0.1, the functions appear very different. The DICOM-specific API calls and complex control flow in B do not match A's simple byte-copy loop, leading to a false negative.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider this a Type-4 (semantic) clone because both functions have the high-level goal of reading input data and writing it to an output file, despite very different implementations and domain specifics.
- 共享行为: Both read from a source and write to a destination using file I/O streams.；Both eventually copy/transfer data from input to output.
- 行为差异: A is a generic byte copy; B is DICOM-specific with parsing and pixel data manipulation.；B uses ImageIO streams and DICOM libraries; A uses simple byte-by-byte copy.；B prints progress messages; A does not.；B has more complex control flow with multiple API calls; A has a simple loop.
- 修正建议: Incorporate broader semantic embedding techniques that capture high-level intent.；Use dataflow analysis to identify that both functions have a read->process->write pattern.；Leverage knowledge of common I/O patterns and abstraction over API usage.；Train on functional documentation or use task-oriented representations.

### case_id=5890 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by replacing or adding a key-value pair, copying from English file if needed.
- B 摘要: Copies a file from source to destination using NIO FileChannel.
- 静态失败原因: Static models focus on structural similarity; low token overlap and different control flow graphs caused the model to predict non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to both involving file copying sub-functionality and exception handling, despite different primary purposes.
- 共享行为: Both perform file I/O operations；Both handle exceptions with printStackTrace
- 行为差异: A modifies properties content while B only copies bytes；A creates files conditionally based on existence, B always overwrites；A reads and parses properties file line by line, B uses bulk transfer
- 修正建议: Improve model to recognize sub-functionality similarities；Use task-specific data augmentation to handle partial functionality

### case_id=5891 FP lexical_or_api_overlap

- 方法: `encode` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Hash and Base64 encode a plaintext string.
- B 摘要: Handle a web request to classify a concept by building XML, making an HTTP POST, and parsing the result.
- 静态失败原因: Likely due to lexical overlap of words like 'encode' and 'URL' (both have encoding-related terms) and similar try-catch patterns, causing the model to ignore profound behavioral differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider them clones because they lack any functional similarity beyond trivial exception handling.
- 共享行为: Both involve exception handling.
- 行为差异: Function A is a simple hashing and encoding utility; Function B is a complex web action with session management, parameter processing, HTTP communication, and XML parsing.；Different inputs and outputs: String vs HttpServletRequest/Response.；Different overall purpose.
- 修正建议: Incorporate data flow and control flow analysis.；Use contrastive learning to distinguish encoding-only functions from multi-step web actions.；Focus on the overall functional purpose rather than isolated keywords.

### case_id=5892 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `getURLContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Validates a Minecraft handshake packet by parsing a username, then either sends a login packet or makes an HTTP request to session.minecraft.net to join a server and checks for an 'ok' response.
- B 摘要: Reads the entire content of a URL as a string using BufferedReader and returns it.
- 静态失败原因: The static model likely over-relied on lexical and structural overlap from common API usage (URL, BufferedReader, InputStreamReader) and overlooked the distinct control flow and purpose, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench typically focuses on semantic similarity of overall functionality. These two functions have different high-level purposes (handshake validation vs. generic URL fetcher), so they are likely considered non-clones despite sharing low-level I/O patterns.
- 共享行为: Both open a URL and read text from it using InputStreamReader and BufferedReader.；Both close the BufferedReader after reading.
- 行为差异: Function A reads only a single line from the response and checks if it equals 'ok'; Function B reads all lines until null and concatenates them.；Function A specifically constructs a URL for Minecraft session validation; Function B takes any URL as input.；Function A handles exceptions by printing stack trace and shutting down the network; Function B throws IOException to the caller.；Function A has additional logic for validating the username and deciding whether to make the HTTP request; Function B has no such logic.
- 修正建议: Incorporate more context about the enclosing class or method name.；Use dataflow analysis to track how the read data is used (single line vs. full content).；Train the model on more diverse examples to reduce sensitivity to common boilerplate patterns.

### case_id=5893 FN benchmark_preference_bias

- 方法: `getFile` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint address in the XML, and saves it to a temporary file.
- B 摘要: Reads input files, applies a pseudolocalization pipeline, and writes output files with a modified suffix.
- 静态失败原因: Static BERT correctly identified non-clone; this is a true negative from the model's perspective.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have mislabeled this pair due to superficial similarities like file I/O and error handling, but the functions are semantically unrelated.
- 共享行为: Both perform file I/O (read/write).；Both use logging (mLog vs System.out/err).；Both handle IOException.
- 行为差异: Different domains: WSDL handling vs pseudolocalization.；Different core operations: XML DOM manipulation vs message catalog processing.；Different control flow: single URL download vs iterating over multiple files.；Different error handling: throws AxisFault vs prints to stderr.
- 修正建议: Reconsider BCB label for this pair as it appears to be a false positive.；For future models, ensure training data has consistent annotation guidelines to avoid such mismatches.

### case_id=5894 FN benchmark_preference_bias

- 方法: `read` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a camera log from a URL, parses each line into CameraLogRecord objects, adds them to a list, and sorts them.
- B 摘要: Reads static comma-separated strings and a configuration file to populate multiple sets and hash tables for a Tibetan transliteration system.
- 静态失败原因: Static BERT/GraphCodeBERT correctly identified them as non-clones due to low token overlap (0.083) and different method names, structure, and domain. However, it was marked as a false negative because it disagreed with the BCB label. The failure is not in the model's reasoning but in the benchmark label being overly broad.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled these as clones under a very broad Type-4 interpretation where both functions are considered 'reading and parsing input data into structured collections', ignoring the specific domain and detailed logic. The annotators may have considered the high-level pattern of reading line by line, tokenizing, and populating data structures as semantically similar.
- 共享行为: Both read input data (from a URL or static strings and a file) and parse it line by line.；Both use tokenization to extract fields and populate collections (e.g., lists, sets, hash maps).；Both handle input errors (e.g., parse exceptions, file disappearance).
- 行为差异: Different input sources: function A reads from a URL; function B reads from static string fields and a file.；Different parsing logic: function A parses each line into a single object; function B tokenizes by comma and populates multiple specific sets.；Different outputs: function A produces a sorted list of records; function B populates multiple global data structures (HashSet, HashMap).；Function A uses logging; function B uses System.out and throws errors.
- 修正建议: Re-evaluate BCB annotation guidelines for Type-4 clones to ensure they capture meaningful semantic equivalence.；Use more detailed structural and semantic features to distinguish broad pattern matching from actual functional equivalence.；Incorporate domain-specific or flow-aware analysis to avoid grouping unrelated data-reading functions.

### case_id=5895 FN benchmark_preference_bias

- 方法: `getFile` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a given URL, optionally modifies endpoint addresses in the XML, and returns the file path.
- B 摘要: Reads a DICOM image file, parses pixel data, and writes it to an output file.
- 静态失败原因: The model correctly predicted non-clone; the BCB label likely is an error in the benchmark, not a model failure.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to both being file-processing utilities with similar structure (try-catch, file streams) and possibly due to a lenient Type-4 functional similarity threshold.
- 共享行为: Both perform file I/O operations (reading and writing files).；Both use logging (System.out) and exception handling.
- 行为差异: Function A downloads a WSDL from a URL and manipulates XML; Function B processes DICOM medical images.；Function A returns a file path; Function B is void and writes output to a given file.；Function A uses AxisFault exceptions; Function B throws IOException.；Function A involves temporary files and conditional downloads; Function B directly reads and writes.
- 修正建议: Review BCB labeling guidelines to ensure such diverse functional pairs are not marked as clones.；Improve dataset quality by filtering out pairs with low semantic similarity despite structural overlap.

### case_id=5896 FN benchmark_preference_bias

- 方法: `copyResource` vs `unzipModel`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file byte-by-byte.
- B 摘要: Extracts entries from a zip file into a directory using buffered I/O.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token and structure overlap; low token Jaccard (0.225) and different method names/API calls caused the model to miss the abstract similarity in I/O patterns that BCB values.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them clones because both perform abstract I/O copy operations and share similar loop structure, matching a broad Type-3/Type-4 clone interpretation.
- 共享行为: Both read from an input source and write byte data to an output；Both use a while loop to read and write bytes；Both handle I/O and throw exceptions
- 行为差异: A reads a single source (URL or file), B reads multiple zip entries；A writes to a single file, B creates multiple files；A uses unbuffered byte-by-byte read, B uses buffered bulk read with buffer size 2048；A no buffering, B uses BufferedOutputStream
- 修正建议: Incorporate abstract I/O patterns like 'stream read-write loops' as features；Use data flow analysis to capture input-to-output copying behavior；Train with more diverse Type-4 clone examples to recognize broad functional similarity

### case_id=5897 FP partial_functionality

- 方法: `getWebPage` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads content from a URL and returns it as a string.
- B 摘要: Fetches a tile from a data source, reads its GeoJSON content, processes it into geometry objects, and adds them to a data layer with duplicate request management.
- 静态失败原因: The model likely over-weighted the common I/O loop and missed the extensive surrounding code that defines distinct behaviors; it focused on a partial functionality overlap.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the overarching functionality differs entirely; the shared I/O pattern is boilerplate and too generic to indicate semantic equivalence, even under broad Type-3/4 criteria.
- 共享行为: Both open a URL stream and read line by line using BufferedReader.
- 行为差异: Function A returns the concatenated string; function B processes the string into geometry objects and adds them to collections.；Function B manages a set of launched HTTP requests to avoid duplicates, handles multiple protocols (http, file), and interacts with a data source and loader.；Function A throws an Error on IOException; function B logs and returns on various exceptions.；Function B is much longer and has additional steps for geometry creation and data loading.
- 修正建议: Enhance model to capture overall method purpose rather than local patterns.；Use dataflow analysis to distinguish simple data retrieval from complex processing.；Include more negative examples where I/O patterns are similar but overall semantics differ.

### case_id=5898 FN boilerplate_overlap

- 方法: `sendExceptionToServer` vs `addIDs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a remote server via HTTP POST.
- B 摘要: Retrieves metabolite IDs from a remote database via HTTP GET and populates a data row.
- 静态失败原因: Low token Jaccard (0.13) and limited lexical overlap; static BERT may focus on superficial token matching and miss the functional similarity in HTTP boilerplate, leading to a non-clone prediction.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: None
- 共享行为: Perform HTTP requests using URL and stream handling；Handle IOException and exceptions；Read or write from network streams
- 行为差异: HTTP method: POST (sends data) vs GET (retrieves data)；Function purpose: error reporting vs chemical ID retrieval and assignment；Data processing: simple string building vs complex HTML parsing and variable assignment
- 修正建议: Enhance model with control-flow and data-dependency features to differentiate boilerplate from core logic；Use contrastive learning that captures functional intent rather than only lexical similarity；Incorporate method-level semantic role annotation (e.g., network I/O, data transformation)

### case_id=5899 FN partial_functionality

- 方法: `doTransfer` vs `sendExceptionToServer`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an incoming HTTP request to another URL, including headers and body, and returns the response.
- B 摘要: Sends exception details (message, stack trace, config, problem) to a server via HTTP POST and reads the response.
- 静态失败原因: Low lexical overlap (token Jaccard 0.21) and different method names/contexts misled the model; GraphCodeBERT may not capture the structural similarity of HTTP client patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones due to similar high-level pattern of HTTP communication (open connection, write, read, close) and common error handling, despite different specific purposes.
- 共享行为: Both create an HTTP connection to a URL；Both set the connection to do output；Both write data to the output stream；Both read the response from the input stream
- 行为差异: A forwards the entire request (headers and body), B sends a fixed set of URL-encoded parameters；A uses HttpURLConnection with explicit method, B uses URLConnection；A copies request headers, B does not；A returns response to client, B only logs success/failure
- 修正建议: Incorporate data flow analysis to compare read/write sequences；Use API-level embedding for HTTP operations；Add more training examples of broad Type-4 clones

### case_id=5900 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by updating or adding a message key-value pair.
- B 摘要: Reads a text file, applies wrapping and title case filters, and writes to another file.
- 静态失败原因: Static BERT methods rely on token and structural similarity; low Jaccard (0.22) and divergent high-level semantics led to a non-clone prediction, missing the broad file-processing overlap that BCB might emphasize.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this as a clone based on broad Type-4 criteria, considering both as file processing utilities that read lines and write output, despite different specific transformations.
- 共享行为: Both read from a file line by line using BufferedReader；Both write output to a file using FileWriter
- 行为差异: Function A handles properties file format, updates specific keys, and creates missing files；Function B applies text transformation filters (WrapFilter, TitleCaseFilter)；Different error handling: A catches Exception, B throws IOException；Different input/output semantics: A uses locale and message parameters, B uses command-line arguments
- 修正建议: Incorporate high-level task classification (e.g., file I/O utilities vs. property manipulation)；Use data-flow or control-flow analysis to distinguish different transformation logic

### case_id=5901 FP other

- 方法: `encrypt` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Encrypts a password using a specified algorithm and returns hex-encoded uppercase string.
- B 摘要: Handles HTTP request in Struts action to classify a concept, including session validation, parameter extraction, and remote XML communication.
- 静态失败原因: Static model likely overfit to common API tokens (String, byte, for, try, catch) and small code size, failing to capture vast semantic differences. Low Jaccard suggests false positive may be due to random noise or model bias.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotation requires full-function semantic equivalence. These functions share no meaningful functionality; one is encryption, the other is web request handling. They are clearly not clones.
- 共享行为: Both contain a for loop over array elements；Both use StringBuffer for string building；Both catch exceptions (NoSuchAlgorithmException vs Exception)
- 行为差异: Function A is a short cryptographic utility; Function B is a large web controller with business logic；Function A returns a transformed string; Function B returns an ActionForward object；Function A has no external dependencies; Function B interacts with session, request, and remote URL；Function A is ~20 lines; Function B is >200 lines (truncated)
- 修正建议: Use structural features like AST or CFG to capture code logic；Increase training data variety to reduce overfitting to boilerplate；Apply contrastive learning to better separate dissimilar functions；Incorporate data flow analysis to understand variable dependencies

### case_id=5902 FN benchmark_preference_bias

- 方法: `CopyTo` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file to a destination file using FileReader and FileWriter.
- B 摘要: Retrieves a resource as an InputStream, with caching to a local file and HTTP handling.
- 静态失败原因: Static BERT models rely on token-level similarity; the low Jaccard similarity (0.16) and differing control flow (simple vs. complex with conditional logic) led to a non-clone prediction. The model could not recognize the abstract I/O transfer pattern that BCB considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this as a clone because both methods perform data transfer via streams (reading and writing bytes), and share common patterns like try-catch-finally and loop-based I/O. This is a broad Type-4 interpretation of 'similar functionality' (I/O copy).
- 共享行为: Both perform I/O operations to read data from a source and write to a file.；Both use a while loop to transfer data as integer bytes.；Both close streams in finally blocks.
- 行为差异: A is a simple file copy; B involves URL/HTTP handling and caching logic.；A's source is a fixed file field; B's source is a resource identified by a string.；A writes to a specified destination file; B writes to a cache file and returns an InputStream.；B has numerous System.out.println statements and conditional caching; A has none.
- 修正建议: Incorporate training examples that explicitly distinguish between low-level syntactic overlap and high-level semantic equivalence.；Use models with data flow or graph representations to better capture structural similarities and differences.；Validate annotations to ensure consistency; consider if such pairs should truly be clones.

### case_id=5903 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `addQDInformation`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a resource file line by line, parsing each line as an integer, and returns a HashSet of those integers.
- B 摘要: Reads a local or remote file with specific key-value lines to update internal date and project information.
- 静态失败原因: The static model likely overemphasized the lexical overlap of common patterns like 'try-catch', 'while readLine', 'URL', 'InputStream', etc., ignoring the different contexts and data formats.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the two functions have no semantic similarity beyond basic file reading commonality; the specific purpose and output are entirely different.
- 共享行为: Both read text files line by line；Both perform numeric parsing of lines
- 行为差异: A returns a set of parsed integers; B updates internal state；A reads from class resource; B reads from file system or HTTP；A parses each line as a single integer; B parses lines with prefixes 'pg ' and 'pt ' with specific formats；B has conditional logic on file modification date
- 修正建议: Incorporate dataflow analysis to capture the specific purpose and output；Use context-aware embeddings that distinguish between different file formats and processing logic

### case_id=5904 FN partial_functionality

- 方法: `copyResource` vs `processAddByURLSubmit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using byte-by-byte loop.
- B 摘要: Reads a URL, copies its content to a StringWriter using IOUtils.copy, then processes it as a DOAP file.
- 静态失败原因: Static BERT models rely on token and syntactic overlap, which is low (Jaccard=0.082). They fail to recognize the shared abstract pattern of opening a URL stream and reading all content, especially when one implementation uses a utility method (IOUtils.copy) and the other uses a manual loop. The different method signatures and class contexts further obscure the similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs as Type-4 (semantically similar) when they share a core operation like reading a URL stream and copying it, despite different output destinations and auxiliary code. The low syntactic overlap is typical for such broad clones.
- 共享行为: Both open a URL stream and read its content.；Both handle exceptions during URL stream access.；Both involve copying the entire stream to an output destination.
- 行为差异: A writes to a file; B writes to a StringWriter then processes the string.；A supports both URL and local file sources; B only handles URLs.；B includes user-facing error handling and logging; A throws generic Exception.；A uses manual byte-by-byte copy; B uses Apache Commons IOUtils.copy.
- 修正建议: Use dataflow analysis to detect stream-reading patterns that end with full consumption of the input.；Incorporate knowledge of common I/O utility methods like IOUtils.copy to recognize equivalent behavior.；Train on examples of partial functionality clones where only a subset of code is semantically aligned.；Employ graph-based representations that model control and data flow beyond token sequences.

### case_id=5905 FP boilerplate_overlap

- 方法: `get` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches game records from a URL using geographic parameters and returns an array of GameRecord objects.
- B 摘要: Scrapes Google image search results and updates a GUI component with an image icon.
- 静态失败原因: The model likely over-weighted the common API usage (HttpURLConnection, BufferedReader, while readLine) and boilerplate structure, ignoring the distinct data processing and output semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the core functionality is completely different: one retrieves structured game records, the other scrapes images for GUI display. The shared HTTP reading boilerplate is insufficient for clone annotation.
- 共享行为: Both open an HTTP connection to a URL；Both read response line by line using BufferedReader；Both handle IOException with exception printing or error dialog
- 行为差异: A returns GameRecord[] array; B returns void and modifies GUI；A uses custom request headers; B uses User-Agent；A filters lines by '# ' prefix; B concatenates all lines；A decodes lines into GameRecord; B extracts image URLs via regex
- 修正建议: Train model to differentiate between shared boilerplate and core semantics；Incorporate data flow analysis to capture how response data is used；Increase weight on method signature and return type differences

### case_id=5906 FP boilerplate_overlap

- 方法: `hash` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes MD5 hash of input string using MessageDigest.
- B 摘要: Processes web request, updates session beans, performs HTTP POST to classify concept, and returns ActionForward.
- 静态失败原因: Possible reasons: both functions contain boilerplate code (exception handling, object instantiation) that may have misled the model, or the model may have learned coarse patterns unrelated to semantics. The low token overlap suggests the model did not rely on lexical similarity; it might have overfitted to some shared keywords like 'digest', 'byte', or 'data'.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because they perform entirely different functionalities: one is a cryptographic hash utility, the other is a web action handler with business logic. There is no partial functionality overlap.
- 共享行为: None
- 行为差异: Function A is a simple static hash computation; B is a complex web request handler with multiple steps.；A uses MD5 algorithm; B involves session management, parameter parsing, and remote HTTP call.；A returns a hex string; B returns an ActionForward object.；A is thread-safe via synchronized; B is not explicitly synchronized.
- 修正建议: Increase training data diversity with more negative pairs from different domains.；Use contrastive learning that explicitly penalizes false positives with low lexical overlap.

### case_id=5907 FN benchmark_preference_bias

- 方法: `copyJar` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file using NIO FileChannel with error logging.
- B 摘要: Builds a site for editing by processing XML, reading/writing multiple files, and transforming content.
- 静态失败原因: Static BERT models rely on lexical and structural similarity; the token Jaccard is very low (0.066) and functions have different purposes. The model correctly detected no semantic equivalence, failing only if BCB's broad criteria are taken as ground truth.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them clones due to both involving file manipulation in a broader system, or this could be a labeling error.
- 共享行为: Both perform file I/O operations: opening files for reading and writing.
- 行为差异: A is a simple single-file copy; B is a complex multi-file site builder with XML transformations.；A uses FileChannel for efficient transfer; B uses traditional streams and filesystem utilities.；A has minimal parameters; B takes numerous parameters including paths, properties, and selection options.；A does not involve DOM or XSLT; B extensively uses XML processing and transformation.
- 修正建议: Incorporate higher-level functional intent understanding.；Use hierarchical representations to capture coarse-grained similarity beyond individual operations.；Validate BCB labels to reduce noise.

### case_id=5908 FN partial_functionality

- 方法: `doPost` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: doPost handles an HTTP POST multipart request, extracts webpage content or URL and root URL, then sends processed page via ToMailerDelegate to response output stream.
- B 摘要: buildSiteForEdit iterates over pages, reads XML, applies XSLT transformations, reads control path, replaces placeholders, and writes transformed content to output files.
- 静态失败原因: Static BERT likely captured low lexical and structural similarity (Jaccard 0.0749) and correctly predicted non-clone, but BCB's broad criteria overestimated similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone because both functions involve stream I/O, string processing, and error handling, which could be seen as a broad Type-4 similarity under partial functionality.
- 共享行为: Both read from input streams and write to output streams；Both perform string manipulation and handle exceptions
- 行为差异: A is an HTTP servlet responding to requests; B is a site builder writing multiple files；A uses multipart form parsing and ToMailerDelegate; B uses XMLTransformer and file I/O；A writes to response output stream; B writes to file system and uses debug tracing
- 修正建议: Enhance model to distinguish between different types of I/O operations and their purposes；Incorporate BCB annotation guidelines that require clear functional similarity beyond common boilerplate patterns；Use finer-grained semantic analysis to differentiate web request handling from batch file processing

### case_id=5909 FN partial_functionality

- 方法: `copyResource` vs `writeData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file byte by byte.
- B 摘要: Writes a formatted table of mass spectrometry data to a text file, including header and multiple columns per row.
- 静态失败原因: Low token overlap (Jaccard 0.098) and no shared API calls or structures; the model correctly predicted non-clone based on surface features.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them both as 'file writing' operations under a broad Type-4 category, but the functionality is too different; likely a benchmark misannotation.
- 共享行为: Both write data to a file.；Both close the file after writing.
- 行为差异: A copies raw bytes from an external input stream; B generates and formats data from function parameters.；A uses binary streams (InputStream/OutputStream); B uses PrintWriter for text output.；A has minimal control flow; B has nested loops and conditional logic.；B writes a structured header and multiple columns per row; A writes raw bytes continuously.
- 修正建议: Re-evaluate BCB annotation for this pair; it may be a false positive.；Incorporate behavioral similarity beyond I/O operations.

### case_id=5910 FP lexical_or_api_overlap

- 方法: `main` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Main method of AdapterGenerator that reads a Prolog file, parses it, and generates adapter JAR files.
- B 摘要: readData method that initializes data structures by parsing string fields and a file for a Tibetan transliteration system.
- 静态失败原因: The model likely overemphasized common Java API tokens (File, StringTokenizer, HashSet, IOException) and structural patterns (loops, try-catch), while missing the semantic context that these functions serve completely different purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have entirely different goals and outputs, despite some superficial similarities in control flow and API usage.
- 共享行为: Both read input data (file or string tokens) to populate collections.；Both contain loops and conditional logic.；Both use exception handling (try-catch).
- 行为差异: Purpose: A generates adapter code; B initializes transliteration character sets.；Input: A reads a Prolog file; B reads from static string fields and a .ini file.；Output: A writes JAR files; B populates in-memory data structures (HashSet, HashMap).；Complexity: A involves class generation and assembly; B is purely data parsing and storage.
- 修正建议: Incorporate program dependency analysis to capture data flow and output characteristics.；Use better tokenization to distinguish between domain-specific and generic boilerplate code.；Leverage code summarization or intention detection to capture high-level functionality.

### case_id=5911 FN benchmark_preference_bias

- 方法: `doUpload` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles multipart file upload, creates temporary directory, processes parameters, and returns XML or forwards to JSP.
- B 摘要: Launches a Maven-based NexOpen project by configuring Hibernate dialect, handling pom.xml files, and scheduling an install action.
- 静态失败原因: Static BERT likely correctly identified non-clone due to low token overlap and distinct API references, thus it didn't match the BCB annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them similar because both are lengthy methods with complex control flow, file I/O, and error handling, which could be seen as broad Type-3 or Type-4 clones.
- 共享行为: Both perform file/resource operations and logging；Both handle multiple conditional paths；Both involve configuration-like setup steps
- 行为差异: Different domains: web upload vs Eclipse project launch；Different input/output (HTTP request/response vs ILaunchConfiguration)；Different API usage (servlet vs Eclipse/JDT)
- 修正建议: Use domain-specific features to capture high-level purpose；Require higher structural similarity threshold；Incorporate API-level semantics for better differentiation

### case_id=5912 FP lexical_or_api_overlap

- 方法: `run` vs `sendRequest`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves tile data from a URL (file or HTTP), parses geometry, and adds it to a data loader.
- B 摘要: Sends an XML request to a servlet via HTTP with GZIP compression, receives and parses an XML response.
- 静态失败原因: The static model likely overemphasized common API tokens (URL, InputStream, BufferedReader, IOException) and boilerplate code for reading HTTP responses, overlooking the distinct data processing logic and overall intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the methods solve completely different functional problems despite sharing low-level stream reading boilerplate. Broad Type-3/Type-4 similarity is not sufficient for clone equivalence.
- 共享行为: Both create URL objects and open input streams to read data from HTTP or file sources.；Both handle IOExceptions and use similar stream reading patterns (BufferedReader/InputStreamReader).；Both involve string concatenation of read data.
- 行为差异: A loads and processes geometric tile data; B sends an XML request and receives/parses an XML response.；A reads from HTTP or file; B only uses HTTP with additional GZIP compression.；A modifies internal state (data loader and cache); B returns an empty string and has side effects (printing, dialogs).；A checks and maintains a set of launched HTTP requests to avoid duplicates; B does not.
- 修正建议: Incorporate data dependency analysis to distinguish reading raw data vs. structured XML/geometry.；Enhance model with control flow and context about method signatures and class hierarchies.；Use a more fine-grained representation that captures the unique operations performed on the read data.

### case_id=5913 FP partial_functionality

- 方法: `copyFile` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel transfer.
- B 摘要: Parses comma-separated strings from global variables and a configuration file to initialize sets and maps for Tibetan transliteration.
- 静态失败原因: Static BERT models may rely on surface-level features like the presence of 'IOException', 'file', 'catch', and 'finally' blocks. The long, truncated code_b may confuse the model due to its length and complexity, leading to a false positive based on partial lexical overlap.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotators typically mark as non-clone when functions serve entirely different purposes, even if both involve file I/O. The core functionality (copy vs. parse) is completely different, and the code structure and complexity are dissimilar.
- 共享行为: Both involve file I/O and exception handling.
- 行为差异: copyFile copies file content using FileChannel; readData parses token strings and populates data structures.；copyFile is simple and standalone; readData is complex with many nested loops and conditionals.；copyFile throws IOException; readData catches IOException and throws Error on malformed data.
- 修正建议: Improve model's ability to distinguish between data parsing and simple file copy by incorporating finer-grained semantic understanding.；Use data flow analysis to capture the overall purpose instead of relying on bag-of-words or local context.

### case_id=5914 FP lexical_or_api_overlap

- 方法: `sendRequestObjectResponse` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an XML request to a configurable server URL, receives a response, saves it to a file based on content type, and returns the file path.
- B 摘要: Searches Google Images by constructing a URL, parses the HTML response to extract image URLs, and updates a GUI component with the first image.
- 静态失败原因: The static model likely overemphasized the common API usage (URL, HttpURLConnection, BufferedReader) and the try-catch structure, ignoring the distinct logic and outcomes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these as clones because they have fundamentally different purposes and I/O behavior; the broad Type-3/Type-4 criteria still require similar functionality, which is absent here.
- 共享行为: Both functions perform HTTP GET/POST requests；Both read input from HTTP connections；Both handle exceptions using try-catch
- 行为差异: Function A sends a request payload and saves response to a file; Function B does not send request data and parses HTML for image URLs；Function A uses preferences/dialog for server configuration; Function B hardcodes the search URL；Function A returns a file path; Function B updates a GUI and does not return a value
- 修正建议: Incorporate dataflow analysis to distinguish between sending/receiving vs. just reading；Use control flow to identify different output targets (file vs. GUI)；Consider including more context about method names and overall purpose

### case_id=5915 FN benchmark_preference_bias

- 方法: `save` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Writes a byte array to a file, creating parent directories and safely closing streams.
- B 摘要: Launches a NexOpen project configuration by processing XML, setting properties, and running an install action.
- 静态失败原因: Static model correctly predicted non-clone due to low lexical overlap (Jaccard 0.06) and different method signatures; no failure.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered the shared use of IOUtils.copy and ByteArrayOutputStream as sufficient for partial similarity, ignoring the vast difference in overall functionality.
- 共享行为: Both use IOUtils.copy and ByteArrayOutputStream for I/O operations.
- 行为差异: Purpose: one is generic file save, other is Eclipse launch configuration.；Code complexity: simple I/O vs. complex control flow with XML parsing and project management.；Error handling: finally blocks for stream closure vs. custom exceptions and logging.；Context: standalone utility vs. plugin framework with workspace resources.
- 修正建议: Re-evaluate BCB annotation for this pair; likely a false positive.；Improve clone detection to weight overall functionality more heavily than isolated API usage.

### case_id=5916 FP boilerplate_overlap

- 方法: `readUNI` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads TSV data from a URL and populates a list with parsed entries.
- B 摘要: Fetches a version string from a URL and returns it.
- 静态失败原因: Static BERT likely overemphasized the similar boilerplate code (URL opening, reading, exception handling) and overlooked the distinct semantic goals and data transformations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have different intentions and data processing logic, despite sharing a common pattern like URL reading.
- 共享行为: Open URL and read lines from input stream；Use try-catch-finally for resource cleanup
- 行为差异: A populates an externally provided list with multiple entries; B returns a single string；A parses tab-separated values; B reads entire lines；A has void return and takes parameters; B returns String with no parameters；A uses hardcoded URL in B; B's URL is passed as parameter
- 修正建议: Incorporate return type and parameter analysis；Emphasize differences in data parsing logic；Use data flow to track variable transformations

### case_id=5917 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads version check URL, parses .build and .stablebuild lines, and invokes another method with parsed versions.
- B 摘要: Reads OSGi service file from classpath, parses lines to find a class name, loads and instantiates it as FrameworkFactory.
- 静态失败原因: Static BERT models often rely on overlapping tokens and API usage patterns (URL, BufferedReader, readLine) without capturing high-level semantic intent, leading to false positives.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires high functional similarity for clones; these have entirely different outputs and contexts, so they would be labeled non-clone.
- 共享行为: Both open a URL and read lines using BufferedReader；Both trim and parse lines based on prefixes or conditions；Both close the reader in a finally block or after reading
- 行为差异: Different purposes: version checking vs. framework factory loading；Different parsing logic: checks for .build/.stablebuild vs. ignores comments and loads class；Different return types: void (and side effect) vs. FrameworkFactory instance；Different error handling: catches IOException and shows error vs. throws Exception
- 修正建议: Use data flow analysis to capture input-output relationships；Incorporate structural differencing for control flow and variable usage；Train with contrastive learning to penalize API-level similarity when semantics differ

### case_id=5918 FN partial_functionality

- 方法: `main` vs `readURL`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Constructs HTTP POST parameters for RenRen API and sends a POST request, then prints the response line by line.
- B 摘要: Reads from a URL and prints its content line by line with proper resource cleanup.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on structural overlap and token similarity; the low token Jaccard (0.15) and the presence of many distinct API calls in A (PostParameter, RenRenPostParameters) might have led the model to classify them as non-clone. Additionally, the model may have been misled by the different method names and signatures (main vs readURL).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because the core behavior of reading from a URL and printing line by line is identical, and the additional parameter setup in A is considered preprocessing that does not affect the core functionality. The difference in HTTP method (POST vs GET) may be overlooked due to broad Type-4 similarity.
- 共享行为: Both read from a URL and print its content line by line；Both use BufferedReader and InputStreamReader to read
- 行为差异: Function A sets up HTTP POST parameters and sends a POST request, while Function B generically opens a URL stream without specifying HTTP method；Function A lacks exception handling and resource cleanup (e.g., no finally block), while Function B includes try-catch-finally and closes streams；Function A is a public static main method, B is a protected instance method
- 修正建议: Increase training data with more partial functionality pairs；Incorporate data flow analysis to recognize that the core reading loop is the same；Use techniques that abstract away specific API details and focus on control flow patterns

### case_id=5919 FP lexical_or_api_overlap

- 方法: `getUser` vs `getXML`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves a User object from a DAO or parses a config file.
- B 摘要: Fetches XML content from a URL and returns it as a String.
- 静态失败原因: The static model likely over-emphasized lexical/API overlap (e.g., BufferedReader, InputStreamReader, URL) and missed the significant differences in data flow, return types, and overall intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functionalities are completely different: one retrieves a user entity, the other fetches raw XML content. Despite shared I/O patterns, the purpose and output are distinct.
- 共享行为: Both read data from an external source using BufferedReader and InputStreamReader.；Both handle exceptions with try-catch blocks.；Both return null under certain failure conditions.
- 行为差异: Function A reads from a local config file or database; B reads from a remote URL.；Function A parses colon-separated tokens and creates a User object; B just concatenates lines.；Function A uses a DAO for persistence; B does not.；Different input types and return types (User vs String).
- 修正建议: Incorporate data flow analysis to track return types and transformations.；Use argument type and return type information as features.；Focus on the high-level purpose (e.g., entity retrieval vs. web content fetching).

### case_id=5920 FN benchmark_preference_bias

- 方法: `doGet` vs `extractUninstallFiles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests to retrieve and render a portal page with permission checks and caching.
- B 摘要: Extracts uninstallation files to a destination directory, handling upgrades, file copying, and JAR processing.
- 静态失败原因: Static BERT model correctly predicted non-clone given low token overlap and distinct contexts; the model did not fail from a semantic perspective, but BCB considered it clone possibly due to benchmark preference bias.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have annotated as clone due to superficial structural similarities such as try-catch blocks, loops, and file I/O, despite completely different domain purposes.
- 共享行为: Both contain try-catch blocks for IOException；Both perform file-related operations
- 行为差异: First method handles HTTP request/response and user permissions; second manages file system and JAR extraction；First uses servlet context; second uses file paths and zip streams；First deals with page rendering and caching; second deals with uninstall script generation
- 修正建议: Improve dataset annotations to reduce false positives from broad structural similarity；Use domain-aware embeddings to differentiate web app logic from file management

### case_id=5921 FN partial_functionality

- 方法: `main` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts all entries from a KMZ (ZIP) file fetched via URL or local file.
- B 摘要: Decompresses a single .gz file specified via command line argument.
- 静态失败原因: Static BERT models rely heavily on lexical and API tokens (e.g., ZipInputStream vs GZIPInputStream), and low Jaccard similarity (0.27) leads to false negative; they miss the high-level behavioral similarity of decompression over different archive formats.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as 'decompression' or 'archive extraction' tasks, accepting broad Type-3/4 similarity despite different compression formats and input sources.
- 共享行为: Both read compressed input and write decompressed data to files；Both use a buffer and read-write loop；Both close input/output streams
- 行为差异: Different compression formats: ZIP vs GZIP；Input source: hardcoded URL vs command line argument；Multiple files output vs single file output；Error handling: throws Exception vs try-catch
- 修正建议: Train models with more diverse Type-3/4 clone pairs that share functional purpose but differ in API or file format；Incorporate semantic role labeling or code summarization to capture abstract intent；Use contrastive learning on pairs with low lexical but high semantic similarity

### case_id=5922 FP boilerplate_overlap

- 方法: `sendPost` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with a parameter and returns the response body as a string.
- B 摘要: Reads sequence data from a URL in FASTA-like format and populates internal lists of names and sequences.
- 静态失败原因: Static BERT-based models may over-emphasize common structural patterns (URL, InputStream, read loop, try-catch) and ignore the distinct API calls and data processing logic, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels only semantically equivalent or highly similar functions as clones. Here, the overall functionality differs completely (HTTP client vs sequence importer), so BCB would not consider them clones despite shared I/O boilerplate.
- 共享行为: Both open a URL connection and read from an InputStream.；Both use try-catch blocks to handle I/O exceptions.；Both read data line by line in a loop.
- 行为差异: A is an HTTP POST client that sends a parameter; B is a passive reader that just opens an InputStream without sending data.；A returns a concatenated string of the response; B modifies class-level lists (names, sequences).；A uses PrintWriter to send data over the output stream; B does not write anything.；B includes logic to parse '>' delimiters and tokenize names, which A lacks.
- 修正建议: Include more negative examples with similar boilerplate but different semantics.；Use data-flow analysis or dependency graphs to capture semantics more accurately.；Incorporate method-level documentation or context (e.g., class name, surrounding methods) to disambiguate purpose.

### case_id=5923 FP lexical_or_api_overlap

- 方法: `createDialogArea` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Creates a dialog area to display license agreement read from a bundle resource.
- B 摘要: Checks for software upgrades by querying a remote license server and updating database/UI.
- 静态失败原因: Static BERT models may over-rely on overlapping tokens like 'URL', 'BufferedReader', 'while' loop, and miss the distinct high-level semantics due to limited contextual reasoning.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clone when functions have entirely different objectives, even if they share trivial API usage patterns.
- 共享行为: Both open a URL or InputStream and read lines of text using BufferedReader.；Both handle exceptions for I/O operations.
- 行为差异: Purpose: dialog creation for license display vs. upgrade logic with network communication.；UI involved: one creates Eclipse dialog widgets, the other manipulates existing UI components.；Data source: local bundle resource vs. remote HTTP server.
- 修正建议: Enhance model to capture overall task semantics beyond local token overlap.；Use contrastive training with hard negative examples that share API but differ in goal.

### case_id=5924 FN partial_functionality

- 方法: `testNetworkHTTP` vs `sendRequestObjectResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Tests network by sending multiple HTTP GET requests to hardcoded URLs and discarding responses.
- B 摘要: Sends an HTTP POST request with XML data to a server, receives a response, saves it to a file, and returns the file path.
- 静态失败原因: Static BERT-based models rely heavily on token overlap and structural similarity. The low Jaccard similarity (0.079) and different variable names, method names, and control flow caused the model to classify them as non-clones, missing the high-level similarity of HTTP communication pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators might have considered both functions as 'HTTP client operations' that establish connections and read responses, overlooking the differences in request method, data sending, response handling, and return value.
- 共享行为: Both functions use java.net.URL and HttpURLConnection to make HTTP requests；Both functions read from an InputStream obtained from the connection；Both functions handle IOException and print stack trace
- 行为差异: Function A makes multiple GET requests without sending data; function B makes a single POST request sending XML data；Function A discards the response; function B saves the response to a file and returns its path；Function A uses fixed URLs; function B uses configurable server URL and port from preferences；Function B has additional features like GZIP compression, content-type detection, and file writing
- 修正建议: Improve model to capture abstract API usage patterns (e.g., sequence of HTTP operations)；Incorporate data flow and semantic role of variables to distinguish between sending data vs. just reading；Use contrastive learning on pairs that share API sequences but different intents

### case_id=5925 FP lexical_or_api_overlap

- 方法: `run` vs `executeHttpGet`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a tile from a URL (file or HTTP), reads geoJSON, converts to geometries, and adds to data source while tracking launched requests.
- B 摘要: Executes an HTTP GET request and returns the response body as a JSONObject.
- 静态失败原因: The static method likely focused on the token-level overlap of reading HTTP response with BufferedReader and StringBuilder, ignoring the broader context and different API calls (URL vs HttpClient) and the additional logic in A.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels as non-clone if functions have different logic structures and purposes, even if they share a common IO pattern. Here, A has extensive tile processing and state management, while B is a simple HTTP fetch.
- 共享行为: Both read input line by line using BufferedReader；Both build a string from the read lines；Both handle HTTP URLs (though A also handles file)
- 行为差异: A manages a list of launched HTTP requests to prevent duplicates; B does not；A handles both file and HTTP protocols; B only HTTP；A processes geoJSON into geometries and interacts with a data source; B returns raw JSONObject；A uses URL class and openStream; B uses Apache HttpClient
- 修正建议: Improve model to capture longer-range semantic structure；Incorporate control flow and data flow analysis to distinguish simple HTTP fetch from complex processing；Use graph-based representations that capture method dependencies

### case_id=5926 FP boilerplate_overlap

- 方法: `transformSingleFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Compresses an X3D file to GZIP format and returns the output file path.
- B 摘要: Handles user action commands in a settings dialog to update configuration preferences and UI state.
- 静态失败原因: The static model likely overmatched on shared boilerplate patterns (file handling, exception handling, message displays) and common API usage (File, JFileChooser, streams), while missing the entirely different semantic contexts.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels it non-clone because the functions have completely different purposes and no shared functionality beyond basic Java boilerplate.
- 行为差异: Function A performs file compression; Function B updates UI preferences.；Function A works with X3D editor objects; Function B works with Swing components and action commands.；Function A has a single focus (GZIP compression); Function B handles multiple command types.；Function A returns a file path; Function B returns void and updates UI state.
- 修正建议: Enhance model to focus on core logic rather than entire method body.；Use flow-aware or dependency-based representations to distinguish different API usage patterns.；Incorporate functional domain knowledge (e.g., one is compression, one is UI config) as features.

### case_id=5927 FN partial_functionality

- 方法: `sendRequest` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP request with compressed XML payload and builds a JDOM document from the compressed response, but returns an empty string.
- B 摘要: Reads a file's content as a string, either from the filesystem or classpath resource, and returns it.
- 静态失败原因: Static BERT models likely rely on token overlap and structural patterns; the low Jaccard similarity and different method names/contexts mislead them, and they miss the broad functional similarity due to focusing on exact operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as 'read a resource and return its string content' at a high level, valuing the common I/O boilerplate and error handling patterns over specific operations.
- 共享行为: Both read input streams and produce a string output；Both use BufferedReader and InputStreamReader；Both have try-catch error handling；Both use System.out.println for debugging
- 行为差异: A sends data via HTTP POST, B reads from file or classpath；A uses GZIP compression and checksum, B does not；A returns empty string regardless, B returns file content；A builds JDOM document, B concatenates lines
- 修正建议: Incorporate data flow analysis to track resource reading purpose；Add contrastive learning examples with partial functional similarity；Use graph representations capturing I/O operation sequences

### case_id=5928 FP boilerplate_overlap

- 方法: `loadExistingAntlibs` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads Antlib definitions by reading package names from classpath resources and resolving them to antlib XML files.
- B 摘要: Imports sequence names and sequences from a FASTA-like file provided by a URL selection.
- 静态失败原因: The static model likely over-relied on common I/O boilerplate (try-catch, InputStream, BufferedReader, readLine) and ignored the distinct domain-specific operations and method names, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when the functions perform different tasks despite superficial structural similarities. Here, the domain (Antlib vs sequences) and core logic differ, so BCB correctly marks as non-clone.
- 共享行为: Both read from an input stream using readers；Both handle IOException in try-catch blocks；Both loop through lines or tokens of input
- 行为差异: Different input sources: ClassLoader resources vs URL combo box；Different output: loading antlibs vs storing names/sequences in fields；Different parsing logic: simple line reading with URI construction vs tokenization with ImportHelper；Different error handling: wrapping exceptions vs printing stack trace
- 修正建议: Incorporate method name and parameter type embeddings to capture semantic intent；Use dataflow or call-graph information to distinguish processing logic；Train on more diverse examples with similar boilerplate but different functionality

### case_id=5929 FN partial_functionality

- 方法: `copyToDir` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file to a specified directory, creating directories and files as needed.
- B 摘要: Retrieves a resource (possibly from network) and caches it locally, returning an InputStream.
- 静态失败原因: Static embedding models like BERT or GraphCodeBERT rely on token and structure similarity. These functions have low token Jaccard (0.196), different method names, and different high-level structures (one is a straightforward file copy, the other is a complex resource caching mechanism with network and cache logic). The model likely saw insufficient overlap to classify as clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered these clones due to both involving file copying operations (reading from a source and writing to a destination) with similar try-catch and stream patterns, despite differences in source type and purpose.
- 共享行为: Both use FileOutputStream and FileInputStream for file I/O；Both create directories if they don't exist；Both handle exceptions with try-catch；Both perform copying of data from one stream to another
- 行为差异: copyToDir copies a local file to a local directory; getResourceAsStream may download from a URL and caches results；getResourceAsStream includes cache logic with hashtable and HTTP handling; copyToDir does not；copyToDir updates its internal file reference; getResourceAsStream returns an InputStream；The copying loops differ: copyToDir uses byte array buffer incorrectly; getResourceAsStream reads byte by byte
- 修正建议: Improve model with dataflow analysis to capture file I/O patterns better；Use contrastive learning to distinguish between detailed copying vs. caching with network；Include more negative examples of similar low-level patterns with different high-level intent

### case_id=5930 FN partial_functionality

- 方法: `readGeoParserResult` vs `retrieveTemplate`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads geo-parser result by sending XML request to a URL, parsing response, and extracting place names and IDs with retry logic.
- B 摘要: Retrieves a blog template from a URL, reads the response line by line, caches it, and returns the string.
- 静态失败原因: Static models like BERT or GraphCodeBERT often rely on token-level or structural similarity, but the token Jaccard is low (0.113). They may not capture high-level functional similarity due to different domain-specific terms, API calls, and control flow. The models may focus on exact code matches or near-miss clones, missing broad functional overlap because the implementations are quite different despite sharing a common I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both functions perform a network request to fetch data from a URL, read the response line by line, and return a processed result. The core I/O pattern is similar, and they are both examples of 'retrieve data from HTTP source' functionality, which falls under broad Type-4 or partial functionality similarity.
- 共享行为: Both open a URL connection and read the response line by line using BufferedReader.；Both construct a result from the read lines (string or collection of tuples).；Both involve network I/O and handle exceptions (one with try-catch, one throws).
- 行为差异: Different input parameters (String+boolean vs no input; relies on blogEditor field).；Different output types (Collection of Tuple vs String).；Function A includes XML request construction and response parsing; Function B simply concatenates lines.；Function A has retry logic; Function B has caching of the template.
- 修正建议: Incorporate functional similarity metrics that capture I/O patterns and API call sequences beyond token overlap.；Use graph-based models that represent data flow (e.g., from URL to reader to output) to identify similar patterns.；Include program slicing to focus on relevant sub-functions (e.g., network read and accumulation).

### case_id=5931 FN benchmark_preference_bias

- 方法: `createTar` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Creates a tar archive from a directory by iterating over files and writing them to a tar output stream.
- B 摘要: Builds a website for editing by processing pages, reading XML/control files, applying XSLT transformations, and writing output files.
- 静态失败原因: Static model relies heavily on token overlap; the token Jaccard is very low (0.083), so it sees little lexical similarity and predicts non-clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone due to both involving file processing and output generation, though the specific operations are different, falling under broad Type-4 similarity.
- 共享行为: Both perform file I/O operations；Both iterate over a collection to produce output files
- 行为差异: Function A handles tar-specific structures (TarEntry, TarOutputStream)；Function B handles XML/HTML transformation with XSLT and string replacements
- 修正建议: Train model to capture high-level semantic patterns like file I/O and iteration；Re-evaluate BCB annotations for this pair to ensure consistency

### case_id=5932 FP lexical_or_api_overlap

- 方法: `getFrameworkFactory` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads an OSGi framework factory from a service configuration file using reflection.
- B 摘要: Downloads an RDF model from a URL via HTTP connection.
- 静态失败原因: Static models like GraphCodeBERT may have been misled by superficial similarities: both functions use URL, InputStream, and BufferedReader/Reader patterns, and both have try-catch blocks. The model may have focused on these API overlaps and structural similarities while ignoring the semantic difference in purpose and output.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators consider these as non-clones because they implement completely different functionality: one is a service loader for OSGi, the other is an HTTP-based model downloader. There is no overlap in domain or logic beyond basic I/O.
- 共享行为: Both perform I/O operations involving URL and InputStream；Both have try-catch blocks for exception handling；Both return a derived object after reading data
- 行为差异: Different purpose: service discovery vs. RDF model download；Different output type: FrameworkFactory vs. Model；Different error handling: throws Exception vs. throws RuntimeException；Different I/O patterns: reading a text file line by line vs. reading binary stream into a model
- 修正建议: Improve model's ability to differentiate between different business logic by incorporating higher-level semantic features；Train with more diverse negative examples that have API overlaps but different functionality；Use dataflow analysis to capture the intent of the code

### case_id=5933 FP boilerplate_overlap

- 方法: `actionPerformed` vs `convert`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Handles user-triggered GUI actions to set application preferences like Graphviz path, ImageMagick path, country code, date format, and look and feel, with possible restart.
- B 摘要: Converts an ACRNEMA stream file to DICOM format by adding UIDs and handling pixel data inflation.
- 静态失败原因: The static BERT model likely relied on superficial lexical or structural patterns common to many Java methods (e.g., file handling, conditionals, try-finally) and missed the distinct domain-specific semantics due to lack of context or long-range dependencies.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB correctly labels as non-clone because the functions have no semantic similarity and perform unrelated tasks.
- 行为差异: Completely different domains: GUI preference setting vs medical image file conversion；Different control flow: event-driven action handler vs sequential file processing；Different I/O: uses JFileChooser and preference storage vs low-level file streams and DICOM tags
- 修正建议: Incorporate semantic role labeling or domain-specific embeddings；Use more fine-grained code structure analysis like control flow and data flow graphs；Train on more diverse negative examples to reduce false positives from boilerplate code

### case_id=5934 FN benchmark_preference_bias

- 方法: `readVersion` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a 'version' resource from classpath, parsing lines for Version, Revision, and Date to set internal fields.
- B 摘要: Opens a URL or file resource and delegates reading to an overloaded method, returning a status code.
- 静态失败原因: Static BERT likely correctly predicted non-clone due to low token overlap and different control flow, but FN arises because BCB’s label is overly lenient, not because model missed true similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to very broad Type-4 similarity: both involve reading from a URL and handling I/O exceptions, but the specific functionality differs significantly.
- 共享行为: Both open an input stream via URL.openStream()；Both catch IOException
- 行为差异: A reads from a fixed classpath resource, B reads from a dynamic name (URL or file)；A parses specific key-value lines, B delegates to another read method；A sets multiple instance fields, B returns an integer status；A uses BufferedReader for line reading, B uses BufferedInputStream
- 修正建议: Re-evaluate BCB annotation guidelines for this pair; consider removing from clone set.；Improve training data to avoid labeling such broad partial functionality as clones.

### case_id=5935 FN benchmark_preference_bias

- 方法: `readReferenceText` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.75`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a reference text file and returns its content as a string.
- B 摘要: Registers a user by encoding password, setting authorities, persisting to DB, and optionally calling a forum URL.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on overall semantics and token overlap, which are low, and correctly identified them as non-clones under strict equivalence; the BCB label is arguably inconsistent.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider the shared I/O pattern (URL opening and BufferedReader reading) as sufficient for a partial functionality clone, ignoring the vastly different high-level purposes.
- 共享行为: Both use URL, URLConnection, BufferedReader, InputStreamReader, and readLine loops to read input
- 行为差异: Function A reads from a local bundle file, while B makes an HTTP POST request；Function A returns the entire file content, B returns a boolean indicating email success and does many other operations；Function B handles user object, persists to database, performs error logging, and calls sendConfirmationEmail
- 修正建议: The model should be trained with more discriminative examples where partial I/O patterns do not imply clone；Consider using task-specific objectives that weigh structural similarity against functional intent

### case_id=5936 FP lexical_or_api_overlap

- 方法: `getUser` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user from DAO or local config file by parsing lines with colon delimiter.
- B 摘要: Performs a Google image search via HTTP and parses HTML for image URLs.
- 静态失败原因: Static BERT/GraphCodeBERT overemphasized lexical and API overlaps (URL, BufferedReader, InputStreamReader, try-catch), missing deeper semantic differences and intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone due to completely different functionality and domain (user authentication vs image search), despite some superficial API overlap.
- 共享行为: Both use URL and BufferedReader to read data；Both have try-catch exception handling；Both use InputStreamReader and loops
- 行为差异: A reads from local file; B fetches from remote HTTP；A parses simple colon-delimited text; B parses HTML；A conditionally saves User object; B collects image URLs into list
- 修正建议: Incorporate data flow analysis to distinguish local vs remote resource access；Use method names and context to infer domain；Focus on functional behavior rather than boilerplate patterns

### case_id=5937 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `encodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modify a .properties file for a given locale by updating or appending a key-value pair.
- B 摘要: Read a file, Base64 encode its content, and write the encoded data to another file.
- 静态失败原因: Low token overlap (0.206) and distinct domain-specific vocabulary (properties vs Base64) led the static model to correctly identify them as non-clones, but BCB's annotation preference for structural similarity over functional semantics caused the mismatch.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label as a clone due to both being file transformation utilities with similar I/O structure and error handling, fitting a broad Type-4 or partial functionality category.
- 共享行为: Open input and output streams；Read data in a loop and write transformed data；Handle exceptions and close resources in finally block
- 行为差异: A works with character streams and properties format; B works with byte streams and Base64 encoding；A conditionally copies a default file; B always encodes；A modifies specific message lines; B performs whole-file transformation
- 修正建议: Adapt model to BCB's specific clone definition through fine-tuning on BCB-style annotations；Incorporate functional labels or API usage patterns as features；Use contrastive learning with both syntactic and semantic negative sampling

### case_id=5938 FN benchmark_preference_bias

- 方法: `encodeFileToFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Encodes a given input file to an output file using Base64 encoding, returning success status.
- B 摘要: Launches a NexOpen project configuration, handling Maven pom files and Hibernate setup, throwing CoreException on failure.
- 静态失败原因: The static model correctly predicted non-clone; BCB label is likely an error or outlier in the benchmark.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this as a clone due to overbroad annotation criteria, possibly mistaking similar structural patterns (try-catch-finally, file I/O) as semantic similarity, despite no functional overlap.
- 行为差异: Different purpose: file encoding vs project launch；Different domains: base64 encoding vs Eclipse plug-in launch；Different control flow: simple I/O loop vs complex conditional configuration；Different data types: byte buffers vs IProject, Document, etc.
- 修正建议: Re-examine BCB annotation guidelines to avoid false positive over file I/O boilerplate；Remove such pairs from clone benchmark or update labels

### case_id=5939 FN benchmark_preference_bias

- 方法: `sendExceptionToServer` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends an exception report to a server via HTTP POST, building a URL-encoded data string with various parameters.
- B 摘要: Reads a resource file from the classpath and displays its content in a Swing text area.
- 静态失败原因: Static BERT/GraphCodeBERT correctly identified semantic dissimilarity, but BCB labels them as clone based on structural overlap, so the model 'failed' from BCB perspective by not matching the benchmark's broad Type-3/Type-4 criteria.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider these clones due to overlapping API usage patterns (URL, InputStream, BufferedReader, StringBuilder) and both being I/O utility functions, despite different high-level purposes.
- 共享行为: Both use URL to access a resource；Both read from an InputStream using BufferedReader；Both use StringBuilder to process text；Both handle exceptions with try-catch
- 行为差异: A writes data to the URL connection and reads a response; B only reads a resource file；A has multiple parameters and conditional code; B has none；A prints status messages on success/failure; B silently ignores exceptions；A is for remote error reporting; B is for loading a local GUI resource
- 修正建议: Incorporate higher-level semantic understanding to align with BCB's partial functionality similarity；Use data augmentation with structurally similar but semantically diverse examples；Train with multi-view representations combining text and code structure

### case_id=5940 FN partial_functionality

- 方法: `main` vs `postRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: main method hardcodes RenRen API parameters, opens HTTP POST connection, sends request, and prints response lines to console.
- B 摘要: Generic method takes URL and data HashMap, opens HTTP POST connection, sends URL-encoded parameters, reads response, and returns concatenated string with exception handling.
- 静态失败原因: Low token overlap, different method names, and distinct API usage (hardcoded vs generic) cause the model to miss the underlying semantic similarity. The model focuses on lexical and structural differences rather than the common HTTP communication pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs as clones if they share core functional similarity, even with different implementation details. Both methods perform the same high-level task: sending an HTTP POST with parameters and processing the response.
- 共享行为: Both create an HTTP POST request with parameters and read the response.
- 行为差异: A hardcodes parameters and prints response; B takes parameters as input and returns response.；A does no exception handling; B catches exceptions and returns null on error.；A uses RenRen-specific classes; B is generic.
- 修正建议: Incorporate data flow analysis to recognize common patterns like network I/O.；Use abstract representations of API calls (e.g., HTTP POST) to capture high-level behavior.；Train on examples of clone pairs with low token similarity but similar functionality.

### case_id=5941 FP lexical_or_api_overlap

- 方法: `importSequences` vs `GetResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Imports sequences from a URL stream by reading FASTA format, extracting sequence names and sequences, and storing them in class-level lists.
- B 摘要: Performs an HTTP GET request to a URL, reads the response line by line, concatenates into a string, and returns it.
- 静态失败原因: The model likely overfitted to surface-level lexical and API overlaps such as 'URL', 'openStream', 'BufferedReader', 'readLine', and exception handling patterns, while ignoring the deeper intent and data flow differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when the functionality is completely different, even if there is API-level overlap; these methods serve entirely different purposes (bioinformatics sequence import vs. HTTP client response), so they are not considered clones.
- 共享行为: Both use URL objects to open streams/connections；Both read input line by line using BufferedReader；Both catch MalformedURLException and IOException
- 行为差异: A reads from a generic InputStream, B from an HttpURLConnection；A parses FASTA format (looking for '>' delimiter), B reads raw HTTP response body；A stores results in class-level lists, B returns a concatenated string；A uses ImportHelper helper class, B uses standard Java I/O directly
- 修正建议: Enrich training data with negative pairs that have high lexical overlap but different semantics；Incorporate static analysis features like method names, class context, or data flow graphs；Use contrastive learning objectives to push apart lexically similar but semantically different functions

### case_id=5942 FP lexical_or_api_overlap

- 方法: `read` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a skeleton file from classpath, parses sections separated by '---', and validates section count.
- B 摘要: Performs a Google image search query, fetches HTML, and extracts image URLs.
- 静态失败原因: Static BERT models may focus on lexical and structural similarities such as common API usage (URL, BufferedReader, InputStreamReader) and similar control flow (while loop reading lines), leading to a false positive prediction. They fail to capture the semantic difference in the overall task and the different data processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functionality is completely different: one reads a configuration skeleton file, the other performs web image search. Even though both involve I/O reading, the high-level purpose and logic are distinct.
- 共享行为: Both open a URL and read its contents line by line using BufferedReader；Both build a string from lines read；Both handle I/O exceptions
- 行为差异: Function A reads from a resource file, makes no HTTP connection; Function B uses HttpURLConnection to query Google；Function A parses sections based on delimiter; Function B extracts image URLs from HTML；Function A validates section count; Function B has no such validation；Function B uses string replacement and URL encoding; Function A does not
- 修正建议: Incorporate task-level understanding, e.g., method names and comments；Use more fine-grained semantic representations that capture data flow and output；Add training data with such false positives to improve discrimination

### case_id=5943 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `doCopyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles GUI action events, updating preferences and UI settings based on command string.
- B 摘要: Copies a file from source to destination using FileChannel, with error checking and optional date preservation.
- 静态失败原因: Static analysis likely misled by common Java library usage (e.g., File, IOException) and general boilerplate structure, but ignored the vast difference in control flow and domain.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones based on functional irrelevance; these two functions have no overlap in purpose or logic.
- 共享行为: None
- 行为差异: Function A is a GUI event handler with no file copying behavior; Function B is a file copy utility.；Function A involves user interaction and preferences; Function B is purely file I/O.
- 修正建议: Improve model sensitivity to overall control flow structure, not just keywords.；Use more discriminative features for event handlers vs. data processing functions.

### case_id=5944 FP lexical_or_api_overlap

- 方法: `getVersion` vs `sendRequestObjectResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves a version string from a remote HTTP URL using a GET request and returns it or null on failure.
- B 摘要: Sends an XML request to a servlet via HTTP POST, saves the response to a file based on content type, and returns the file path, with additional setup for server URL and port.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overfitted to common API tokens like 'URL', 'URLConnection', 'InputStream', 'try' and 'catch', ignoring the overall control flow and semantics. The low Jaccard similarity was not enough to offset the strong lexical signal from these shared tokens, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled these as non-clones because despite sharing some HTTP-related API usage, the overall functionality differs completely: one is a simple version check, the other is a full servlet communication with file saving. BCB typically requires substantial similarity in behavior or structure for Type-3/4 clones, which is absent here.
- 共享行为: Both use java.net.URL and URLConnection to interact with a remote server over HTTP.；Both read data from an InputStream obtained from the connection.；Both have try-catch blocks handling exceptions.
- 行为差异: Method A performs a simple HTTP GET without sending request body; Method B performs an HTTP POST with GZIP-compressed XML output.；Method A returns a String (version number) or null; Method B returns a file path (String) after writing response to disk.；Method B includes complex logic for server URL discovery, user dialogs, file naming based on content type, and system logging.；Method B uses additional streams (GZIPOutputStream, FileOutputStream) and writes a log file.
- 修正建议: Incorporate dataflow analysis to differentiate between read-only and read-write HTTP interactions.；Use AST-based matching with higher weight on method signatures, parameters, and return types.；Apply control flow graph comparisons to capture the structural complexity difference.；Weight tokens from common libraries less, especially when they appear in different contexts.

### case_id=5945 FN partial_functionality

- 方法: `getResourceAsStream` vs `createOutputStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource as an InputStream, caching the resource locally with cache consistency checks using URLConnection.
- B 摘要: Creates a BufferedWriter that filters and copies a zip file, excluding then re-adding a specific entry (content.xml).
- 静态失败原因: The static BERT model likely focused on low token similarity (Jaccard 0.123) and different method names, failing to capture the high-level I/O pattern that humans might recognize as similar. Long-range dependencies and different control structures also contributed to the misclassification.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions performing high-level I/O operations that involve reading from one source and writing to another, with similar stream usage patterns, even though the specific functionality differs. The Type-4 annotation guideline considers such partial functional similarity acceptable.
- 共享行为: Both involve reading from an input source and writing to an output file.；Both use BufferedInputStream/BufferedOutputStream or similar buffered streams.；Both perform file I/O with FileInputStream/FileOutputStream.
- 行为差异: A returns an InputStream for reading; B returns a BufferedWriter for writing.；A uses HTTP caching logic and remote URL access; B manipulates zip entries.；A has extensive error handling with multiple catch blocks; B throws IOException.；A is synchronized; B is not.
- 修正建议: Incorporate graph-based or dataflow-aware models that capture stream connections.；Use method-level documentation or comments as additional semantic clues.；Train on more diverse Type-4 clone examples that share high-level design patterns.

### case_id=5946 FN benchmark_preference_bias

- 方法: `doExecute` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP multipart form submission to compose and send an email with attachments, including parsing form fields and file uploads.
- B 摘要: Handles HTTP GET request to retrieve and render a portal page based on a selected page parameter, with visibility checks and caching.
- 静态失败原因: Static BERT models rely on token overlap and structural similarity; the low Jaccard (0.0947) correctly indicates non-clone. The model did not fail relative to strict semantics, but it disagreed with the BCB label, which may be erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones based on a very broad 'web request handler' category, but their functionality is entirely different in domain and logic, so this is likely a misannotation.
- 共享行为: Both are HTTP request handlers that parse request parameters and produce responses；Both use logging and error handling patterns
- 行为差异: A processes multipart form data to send emails; B retrieves and renders portal pages；A uses Struts ActionForward; B writes directly to response output stream；A handles file uploads and attachments; B handles page visibility and caching
- 修正建议: Re-evaluate BCB annotation for this pair; it may be a false positive.；Consider using more refined clone categories that exclude such broad type-4 matches.；Improve model to better handle case where BCB label is unreliable.

### case_id=5947 FN partial_functionality

- 方法: `doTransfer` vs `PageLoader`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an incoming HTTP request to another URL, copying headers and body, and returns the response.
- B 摘要: Loads the contents of a web page into a string by reading from a URL.
- 静态失败原因: Low lexical overlap and different method signatures caused the model to focus on surface patterns, missing the underlying common URL-reading logic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both involve fetching data from a URL, which is a common functionality, even though the broader context differs.
- 共享行为: Both create a URL object and read data from a URL's input stream.
- 行为差异: Function A forwards headers and request body, Function B does not.；Function A writes response to servlet output, Function B stores in a field.；Function A handles HTTP status codes, Function B ignores them.；Function A uses HttpURLConnection with full configuration, Function B uses URL.openStream() directly.
- 修正建议: Use graph-based representations that capture data flow from URL creation to input reading.；Include source code comments or documentation to highlight the core behavior.；Train with more Type-4 examples to learn functional similarity beyond lexical overlap.

### case_id=5948 FN partial_functionality

- 方法: `copyResource` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using byte-by-byte stream I/O.
- B 摘要: Copies a file to another file using NIO FileChannel transferTo for efficient bulk transfer.
- 静态失败原因: Static BERT models rely heavily on token overlap and local syntactic patterns. The low Jaccard similarity (0.1458) and different APIs (stream vs. channel, byte loop vs. transferTo) led the model to miss the high-level functional equivalence.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often annotates Type-3/Type-4 clones as positive when functions share core functionality (copying data from input to output) even with different APIs or algorithms, focusing on behavioral similarity over syntactic form.
- 共享行为: Copy content from a source to a destination file.；Open input and output streams/channels.；Close resources after copying.
- 行为差异: Function A supports both URL and file sources; function B only accepts a File source.；Function A uses a byte-by-byte read-write loop; function B uses NIO transferTo for bulk copy.；Function A throws generic Exception; function B throws IOException.；Function A relies on external methods getResource and destinationFile; function B takes explicit File parameters.
- 修正建议: Incorporate dataflow or control-flow features that capture the input-to-output copy pattern.；Use graph-based representations that highlight resource handling (open/read/write/close).；Train with contrastive examples emphasizing functional equivalence despite syntactic variation.

### case_id=5949 FP lexical_or_api_overlap

- 方法: `download` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Downloads a resource from the classpath to a file with error handling.
- B 摘要: Parses a file to populate several sets and hash maps with tokenized data.
- 静态失败原因: Lexical overlap in common Java APIs (e.g., IOException, try-catch, fileName) may have misled the model, despite low overall Jaccard similarity (0.04797). The model likely failed to capture the distinct semantic purposes due to the stark length difference and lack of common data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions perform entirely different high-level tasks—resource download vs. data parsing—and share no functional similarity.
- 共享行为: Both methods involve I/O operations.；Both may throw or handle IOException.
- 行为差异: A is a simple file copy; B is a complex data parsing routine.；A uses InputStream/OutputStream and IOUtils.copy; B uses StringTokenizer and sets/maps.；B modifies global data structures; A does not.；A is short (20 lines); B is long (hundreds of lines).
- 修正建议: Use structure-aware representations like AST or control flow graphs.；Incorporate task-specific objectives to distinguish high-level intent.；Apply contrastive learning to reduce sensitivity to boilerplate code.

### case_id=5950 FP lexical_or_api_overlap

- 方法: `testReadPerMemberSixSmall` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Tests GZIP member reading by iterating over a compressed byte array and verifying member copy counts.
- B 摘要: Handles GUI action events to set various application preferences and file paths.
- 静态失败原因: The static model may have been misled by the presence of conditional branches and loops in both methods, despite no semantic similarity, or by a few common tokens like 'return' or 'if'.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the methods have completely different functionality and no partial overlap.
- 共享行为: No shared behavior
- 行为差异: Function A is a unit test for GZIP decompression; Function B is a GUI event handler for settings.；They operate on entirely different data and API calls.
- 修正建议: Improve model's ability to understand method-level semantics beyond lexical patterns.；Incorporate method names and comments to disambiguate purpose.；Use AST-based or higher-level structure features to distinguish test methods from event handlers.

### case_id=5951 FN partial_functionality

- 方法: `postRequest` vs `lookupFutureEvents`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with form-encoded parameters from a HashMap and returns the response body as a string, or null on error.
- B 摘要: Fetches future events from the Meetup API via HTTP GET, parses the JSON response into Event objects with detailed fields, and returns a list of events, throwing an exception on I/O error.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token overlap and syntactic structure. The low token Jaccard (0.179) and different method names, parameter types, and return types likely caused the model to focus on the differences rather than the high-level pattern. The model missed the shared network request pattern because it lacks understanding of semantic intent beyond surface form.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a clone based on broad Type-4 similarity: both functions perform a network request to fetch data from a URL, read the response, and process it, even though the details of processing and input/output differ significantly. The presence of common boilerplate (URL, BufferedReader, try-catch) also contributes.
- 共享行为: Both open a URL connection and read the response line by line.；Both handle I/O errors, though differently (printStackTrace vs throw exception).
- 行为差异: A uses HTTP POST with data in the request body; B uses HTTP GET with query parameters in URL.；A returns a raw string; B parses JSON into domain objects (Event).；A returns null on error; B throws a custom exception GtugsException.；A takes a URL string and HashMap; B takes a group identifier string and uses an API key field.
- 修正建议: Incorporate higher-level semantic modeling, e.g., by using API call sequences or domain knowledge.；Train on more diverse Type-4 clone pairs to learn to recognize functional similarity despite low token overlap.；Enhance the model with data flow analysis to capture that both functions use a URL connection and read response.；Use contrastive learning to emphasize positive pairs with low token similarity but similar intent.

### case_id=5952 FN benchmark_preference_bias

- 方法: `addDataFromURL` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads entire content from a URL and appends it to a class field.
- B 摘要: Sends an XML request to a GeoParser web service, reads the XML response, parses it to extract place names and gazetteer IDs, and returns a collection.
- 静态失败原因: Static BERT models likely focused on the low token overlap and structural differences, correctly predicting non-clone, but failed to align with BCB's broader notion of similarity based on 'URL reading' pattern.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled this as a clone due to the common pattern of reading from a URL and handling IO, despite vastly different overall logic, possibly considering them Type-3/Type-4 clones with broad functional similarity.
- 共享行为: Both open a URL and read lines using a BufferedReader.
- 行为差异: Different purposes: A appends to a field, B parses XML and returns structured data.；B includes retry logic, XML construction, and complex parsing; A has none.；B has a debugging/testing mode; A does not.；A closes the input stream; B does not explicitly close streams.
- 修正建议: Incorporate more abstract patterns like 'IO with URL' into training.；Use contrastive learning with BCB's annotations to capture their tolerance for partial similarity.；Employ cross-level matching: combine token-level and functionality-level features.

### case_id=5953 FP partial_functionality

- 方法: `addDataFromURL` vs `get`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens a URL and appends each read line to a text buffer, with basic error handling.
- B 摘要: Fetches game records from a server via HTTP GET, parses specific lines into objects, and returns an array.
- 静态失败原因: Static models may overemphasize the shared structural pattern of opening a URL and reading lines, ignoring the distinct post-processing and return semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels non-clone because the overall purpose and output are completely different, despite a similar initial data retrieval pattern.
- 共享行为: Both open a URL connection and read lines using BufferedReader and InputStreamReader.
- 行为差异: Function A appends raw lines to a field; Function B decodes lines into GameRecord objects.；Function B sets HTTP headers and checks response code; Function A does not.；Function B filters out comment lines; Function A includes all lines.；Function A closes the stream explicitly; Function B does not.
- 修正建议: Incorporate dataflow analysis to track how read data is used.；Train on more examples with similar I/O patterns but divergent functionality.；Consider output types and side effects (e.g., void vs. return).

### case_id=5954 FP other

- 方法: `copyDeleting` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using a buffer and try-finally block.
- B 摘要: Handles various action commands in a GUI application, setting preferences and updating UI components.
- 静态失败原因: The static model likely made a false positive due to low token overlap and inability to capture overall program semantics; it may have been misled by shared keywords like 'File' and 'IOException' or boilerplate try-catch patterns, despite fundamentally different behaviors.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels non-clone because the two functions have completely different functionality and no significant code similarity; they implement unrelated operations.
- 共享行为: Both use File objects；Both involve I/O operations
- 行为差异: Function A performs a simple file copy; Function B is a complex event handler.；Function A is short and focused; Function B is long with many conditional branches.；Function A is static; Function B is an instance method.；Function A uses FileInputStream/FileOutputStream; Function B uses JFileChooser and File for selection.
- 修正建议: Improve training data to include more diverse non-clone pairs with low lexical similarity.；Incorporate structural or data-flow analysis to distinguish between different high-level tasks.；Use graph-based or AST-based models that better capture program structure.

### case_id=5955 FP boilerplate_overlap

- 方法: `get` vs `retrieveTemplate`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP GET request with custom headers (latitude, longitude, count) to fetch game records, filters out lines starting with '#', and returns an array of GameRecord objects.
- B 摘要: Fetches the HTML template from a blog URL by reading all lines without filtering, caches the result, and returns the string; throws exception on error.
- 静态失败原因: The model was misled by common boilerplate code for reading from a URL (BufferedReader, while loop, readLine) and the presence of similar keywords (URL, openConnection/openStream), ignoring differences in headers, filtering, return types, and caching.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have different output types, data processing, and purposes despite both using URL reading; low token similarity and non-equivalent semantics match their conservative Type-3/Type-4 criteria.
- 共享行为: Both perform HTTP GET requests to read content from a URL line by line using BufferedReader.
- 行为差异: Function A sets custom request headers (latitude, longitude, count) while function B does not.；Function A filters out lines starting with '#'; function B includes all lines.；Function A returns an array of GameRecord objects; function B returns a single string.；Function A does not cache; function B caches the result.
- 修正建议: Incorporate type information and method signatures to distinguish return types.；Add attention to dataflow and API usage patterns (e.g., setting headers vs not).；Include more global context, such as class names and surrounding methods.；Use representation that captures functional intent beyond local lexical patterns.

### case_id=5956 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by copying a default if needed, then updating or adding a message key-value pair.
- B 摘要: Copies a file from source to destination using buffered streams.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on token/structural similarity, and the high-level semantics are different despite shared low-level file I/O patterns. The model may have missed the distinct business logic in A (property modification) because it focused on the common I/O boilerplate.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because both contain a file copy loop (while read/write) and the overall structure of reading and writing files sequentially. Under broad Type-3/Type-4, partial functionality overlap (the copy part in A) can be considered similar even though the intended purposes differ.
- 共享行为: Both read from one file and write to another file byte by byte；Both use while loop with read/write pattern；Both involve file I/O with exception handling
- 行为差异: Function A parses properties file lines, handles comments, and modifies specific key-value pairs; Function B does a raw binary copy；Function A conditionally copies a default file if locale file is missing; Function B always copies the given source；Function A writes back to the same file after modification; Function B writes to a separate destination file；Function A handles string splitting and building; Function B does no string processing
- 修正建议: Incorporate data flow analysis to track variable purposes (e.g., properties vs raw bytes)；Use function renaming or API-level semantics to disambiguate file copy from property modification；Enhance training data with more examples of distinct high-level operations sharing low-level I/O patterns；Consider control flow complexity: string parsing and conditional copy in A vs direct copy in B

### case_id=5957 FN partial_functionality

- 方法: `runInternal` vs `retrieveTemplate`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: runInternal handles HTTP connections to load OPDS catalog entries or download books, with pagination and error handling.
- B 摘要: retrieveTemplate reads a blog template from a URL and caches the result.
- 静态失败原因: Low token Jaccard similarity and different API usage patterns led the model to miss the high-level functional overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled it a clone due to the broad commonality of reading content from a URL, despite significant differences in purpose and complexity.
- 共享行为: Both open URL connections to read data from the web.
- 行为差异: A handles multiple URL parts (pagination), B reads only one page.；A has complex error handling and progress reporting, B has minimal error handling.；A parses OPDS catalog or downloads files, B simply concatenates lines.；A uses HttpURLConnection with settings, B uses URL.openStream() directly.
- 修正建议: Incorporate semantic features like API call sequences and control flow graphs.；Use graph-based models or pretrained embeddings that capture functional similarity.

### case_id=5958 FN boilerplate_overlap

- 方法: `getDatasetsList` vs `sendExceptionToServer`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a list of datasets from a remote server, caching results in a map.
- B 摘要: Sends exception details to a remote server as a POST request and prints the response.
- 静态失败原因: Static BERT models rely on token-level similarity and short-range patterns; they may have been misled by the low token overlap and different method names, failing to recognize the high-level structural similarity of network communication with error handling.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider these clones because both implement network I/O operations with similar patterns of URL handling, stream reading/writing, and exception handling, despite different specific purposes.
- 共享行为: Both open a URL connection to a remote server；Both use streams (BufferedReader, InputStreamReader) to read data；Both handle IOExceptions with logging or printing
- 行为差异: Function A reads a list of strings from a GET-style URL and caches the result; Function B sends a POST request with encoded parameters and prints the server response；Function A returns a List<String>; Function B is void；Function A uses a synchronized cache (HashMap); Function B does not cache；Function A throws RuntimeException on failure; Function B catches and prints a message
- 修正建议: Incorporate higher-level structural features like control-flow patterns of network I/O；Use graph-based representations that capture common boilerplate sequences；Train with contrastive learning to distinguish similar boilerplate from true functional clones

### case_id=5959 FN partial_functionality

- 方法: `copyResource` vs `copyIconFiles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a single resource from a URL or local file to a destination file using byte-by-byte streaming.
- B 摘要: Copies icon files specified by annotations on a UML class to a resource directory, handling two icon sizes separately.
- 静态失败原因: Low lexical overlap (token Jaccard 0.114) and different code patterns (InputStream vs FileChannel, conditional blocks) cause static BERT models to miss the shared file-copying concept, as they rely on surface-level similarity rather than functional semantics.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators likely considered both functions as 'copy file' operations, despite API and logic differences, fitting a broad Type-4 category where high-level functionality (copying a resource from source to destination) is deemed similar.
- 共享行为: Both functions copy data from an input source to an output file using Java I/O.
- 行为差异: copyResource handles a single source from URL or file; copyIconFiles handles two sources based on annotations.；copyResource uses InputStream/OutputStream; copyIconFiles uses FileChannel.；copyResource reads byte-by-byte; copyIconFiles uses transferFrom.；copyResource throws Exception; copyIconFiles catches and prints exceptions.
- 修正建议: Train on more diverse examples of file I/O operations with varying APIs.；Incorporate data flow analysis to recognize core copy behavior despite different stream/channel usage.；Use contrastive learning to align high-level functional descriptions with implementations.

### case_id=5960 FN benchmark_preference_bias

- 方法: `readGeoParserResult` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Parses geo data from an XML web service, returning a collection of place names with associated gazetteer IDs, with retry logic.
- B 摘要: Checks for application version updates by reading a version file from a URL and invoking a version comparison method.
- 静态失败原因: Static BERT likely correctly identified non-clone due to low token overlap and distinct semantic roles; the BCB label may be a benchmark anomaly.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones based on a broad category of 'reading and parsing data from network resources', despite very different specific functionalities.
- 共享行为: Both open a URL connection and read lines from the stream；Both use try-catch for IOException handling
- 行为差异: A uses XML parsing and builds complex requests; B uses simple text prefix matching；A has retry mechanism (up to 3 attempts); B has no retries；A returns a collection of tuples; B calls another method and returns void；A includes testing mode; B does not
- 修正建议: Refine BCB annotations to exclude trivial common patterns；Use finer-grained semantic categories in evaluation

### case_id=5961 FN benchmark_preference_bias

- 方法: `convert` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Converts an ACRNEMA medical image stream to DICOM format with UID injection.
- B 摘要: Launches a Eclipse NexOpen project configuration, handling Maven pom files and Hibernate dialect setup.
- 静态失败原因: Static BERT/GraphCodeBERT likely predicted non-clone due to low token overlap and different domain-specific APIs, missing the supposed broad structural similarity that BCB annotators might have considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled based on vague structural similarity (e.g., both are long, have multiple branches, and involve resource handling) despite completely different semantics.
- 共享行为: Both involve file I/O operations；Both use conditional checks and logging
- 行为差异: Different domains: medical imaging vs Eclipse IDE；Different input parameters and output behavior；A handles pixel data inflation; B handles XML parsing and project configuration
- 修正建议: Improve semantic understanding with dataflow analysis；Incorporate domain-specific knowledge；Use more robust clone detection criteria that align with actual semantic equivalence

### case_id=5962 FP lexical_or_api_overlap

- 方法: `perform` vs `hashPassword`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Processes a web form submission, manages session attributes, sends an HTTP request with XML data to a URL, parses the response XML, and forwards to a success or failure page.
- B 摘要: Hashes a password using the SHA algorithm and returns the hash as a string with a '{SHA}' prefix.
- 静态失败原因: The static BERT model likely focused on surface-level lexical similarities such as common Java keywords (try, catch, String, return), method signatures with parameters, and the presence of logging and string concatenation. It failed to capture the deep semantic meaning because it lacks understanding of the overall program structure and domain-specific operations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clones because the functionalities are entirely different: one is a web action handler with I/O and session logic, the other is a utility for password hashing. There is no semantic overlap in what they accomplish.
- 共享行为: Both methods handle exceptions with try-catch blocks.；Both methods use string operations and return a value.；Both methods have logging (log.error in B, Categories.dataServer().error in A).
- 行为差异: Function A involves web request handling, session management, and XML parsing; Function B is a simple cryptographic hash function.；Function A has a complex control flow with conditional checks and loops; Function B is linear and straightforward.；Function A interacts with external resources (URL connection); Function B is self-contained.；The return types are different: ActionForward vs String.
- 修正建议: Use a model that incorporates control flow and data flow (e.g., GraphCodeBERT with abstract syntax trees).；Train on pairs with higher token Jaccard but different semantics to penalize lexical overlap.；Add explicit instruction to ignore boilerplate patterns (e.g., try-catch, logging).

### case_id=5963 FN lexical_or_api_overlap

- 方法: `readGeoParserResult` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads geo-parser result from external web service, retries up to 3 times, parses XML, returns collection of place names and gazetteer IDs.
- B 摘要: Registers a user: validates, sets password, sets date, adds authority, creates hash, calls phpBB forum URL, persists user, sends confirmation email, returns boolean success.
- 静态失败原因: Static BERT models may rely heavily on lexical and API-level overlaps; the shared URL connection pattern and common API calls (URL, BufferedReader, readLine) could dominate the representation, masking the semantic difference.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might have labelled these as clone due to superficial structural similarities (URL connection, BufferedReader, try-catch) possibly under a broad Type-4 or 'other' category, but this seems inconsistent with typical BigCloneBench annotations which require functional similarity.
- 共享行为: Both open a URL connection and read lines from the response.
- 行为差异: Different input and output types (Collection vs boolean).；Different domain (geo-parsing vs user registration).；Different error handling: A has retry loop, B throws exceptions.；Different data processing: A parses XML, B builds URL string and persists entity.
- 修正建议: Incorporate control flow and data flow analysis to distinguish different purposes.；Use program dependency graphs or semantic embeddings that capture input/output transformations.；Filter out boilerplate code (e.g., URL reading) from similarity computation.

### case_id=5964 FN partial_functionality

- 方法: `fileDownload` vs `readVersion`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a given URL to a local destination directory, writing each byte read from the input stream to a file.
- B 摘要: Reads a version configuration file from the classpath resource, parsing key-value pairs for version, revision, and compile date.
- 静态失败原因: Static BERT/GraphCodeBERT may be too sensitive to token-level differences, low Jaccard similarity, and different method names and output operations. It likely fails to recognize the shared I/O pattern and exception handling structure.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both follow a common pattern of reading from a URL or resource via BufferedReader, iterating line-by-line, handling exceptions, and closing resources. The high-level task of reading remote data and processing it is similar, and BCB often accepts broad Type-3/Type-4 similarity where the core I/O loop is the same despite different processing logic.
- 共享行为: Both open a URL connection or resource stream；Both read line-by-line using BufferedReader；Both handle IOException and close the stream in a finally block
- 行为差异: Function A writes downloaded bytes to a file; Function B parses specific key-value lines and stores values in instance variables；Function A uses URLConnection and writes to FileOutputStream; Function B uses ClassLoader.getSystemResource and only reads
- 修正建议: Incorporate structural similarity metrics that capture control flow patterns (e.g., AST-based similarity)；Use contrastive learning to focus on common I/O boilerplate；Augment training data with more Type-3 clones that share partial behavior but differ in processing

### case_id=5965 FP lexical_or_api_overlap

- 方法: `createMD5` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes MD5 hash of a password string and returns its hexadecimal representation.
- B 摘要: Handles a web request to classify a concept, involving session management, XML construction, HTTP connection, and forwarding to a result page.
- 静态失败原因: Static analysis likely focused on superficial similarities like 'MessageDigest', 'StringBuffer', and basic structure, missing the semantic gap; the model may have been misled by common Java library usage patterns or boilerplate code.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clones because they perform entirely different functionalities; function A is a cryptographic hash utility, function B is a web framework action with complex business logic.
- 共享行为: Both methods handle exceptions；Both use StringBuffer for string building
- 行为差异: Function A is a simple cryptographic hash utility；Function B is a complex web action with session, request, and HTTP operations；Different parameters and return types；Different control flow and logic
- 修正建议: Improve model to understand functional purpose beyond API surface；Incorporate data flow analysis to differentiate simple utility vs. complex business logic；Add training examples that contrast simple utility methods with action methods；Consider context from class names and method names (createMD5 vs perform)

### case_id=5966 FN benchmark_preference_bias

- 方法: `readData` vs `wordFrequency`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a set of tokenized strings into various collections and maps for initializing a Tibetan transliteration system.
- B 摘要: Queries a web service for the frequency of a given word by parsing an HTML response.
- 静态失败原因: Static BERT likely relied on low token overlap and different method signatures, correctly identifying non-clone; BCB label appears to be an error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'reading and processing input data' at a high level, ignoring the completely different domain and output.
- 共享行为: Both use basic Java I/O patterns (StringTokenizer / URL and BufferedReader)；Both involve loops over input tokens/lines
- 行为差异: Different purpose: A initializes internal state, B returns a computed value；A operates on pre-defined string constants, B performs network I/O；A modifies global collections, B has no side effects
- 修正建议: Re-evaluate BCB annotation for this pair; likely false positive.；Include more context in static model training to recognize diverse execution paradigms.

### case_id=5967 FP partial_functionality

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Main method that reads a Prolog file, parses it, generates adapter classes, and writes them to a JAR file.
- B 摘要: Utility method that copies a file from source to destination using FileChannel.
- 静态失败原因: Static BERT may have focused on common API tokens like 'File', 'IOException', and 'close' despite low Jaccard similarity, or misjudged due to length disparity and lack of structural understanding.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels non-clone because the methods have entirely different purposes and no shared logic beyond basic file handling, which is too generic.
- 共享行为: Both involve file I/O operations
- 行为差异: Code A performs complex adapter generation from Prolog, while Code B is a simple file copy.；Code A includes parsing, class writing, and serialization; Code B only transfers bytes.；Code A handles multiple files and JAR entries; Code B handles two files.
- 修正建议: Incorporate dataflow or control flow analysis to distinguish different program intents.；Train on more diverse pairs to reduce over-reliance on surface-level API matches.；Use hierarchical embeddings to capture method-level semantics beyond token overlap.

### case_id=5968 FP lexical_or_api_overlap

- 方法: `main` vs `unzip`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter code from a Prolog file and writes outputs to a JAR file.
- B 摘要: Extracts a zip file into a target directory.
- 静态失败原因: Static BERT methods may over-rely on lexical and API-level overlaps (e.g., File, IOException, InputStream, logging), ignoring the distinct semantic contexts and data flows.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the functions have entirely different purposes and logic, despite superficial similarities in exception handling and file operations.
- 共享行为: Both use File I/O operations.；Both handle exceptions and log messages.
- 行为差异: Function A is a complex code generation pipeline; Function B is a simple file extraction.；Function A parses Prolog files and uses reflection; Function B reads zip entries.；Function A writes multiple JAR entries; Function B writes extracted files to disk.
- 修正建议: Incorporate data flow analysis to distinguish transformation vs extraction.；Use higher-level semantic features like method purpose or domain knowledge.

### case_id=5969 FN partial_functionality

- 方法: `readURL` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a given URL line by line and prints each line to stdout with proper resource cleanup.
- B 摘要: Reads a hardcoded URL's content into a StringBuffer and logs the entire content.
- 静态失败原因: Static BERT/GraphCodeBERT likely missed the similarity due to low token overlap (Jaccard 0.265), different method signatures, different API usage (URL vs URLConnection), and different control flow, focusing too much on lexical and syntactic patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as clone because both functions perform the same high-level task: reading a URL and outputting its text content. Differences in parameterization, output style, and error handling are considered minor in BCB's Type-3/4 guidelines.
- 共享行为: Both read content from a URL using BufferedReader；Both output the content (print or log)
- 行为差异: A is parameterized; B uses hardcoded URL；A prints each line; B appends all lines to buffer and logs once；A catches exceptions; B throws them；A closes multiple streams; B only closes BufferedReader
- 修正建议: Improve modeling of high-level intent beyond lexical tokens；Incorporate understanding of common I/O patterns and API equivalences；Use graph-based representations that capture data flow and control flow similarities

### case_id=5970 FN partial_functionality

- 方法: `save` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Saves multiple Java source files: writes byte contents to files in a base directory, then copies them to a package-specific subdirectory while prepending a package declaration.
- B 摘要: Modifies a locale-specific properties file: reads a file, updates or inserts a key-value pair, and writes back; creates the file from an English template if missing.
- 静态失败原因: The static model likely relied on low token overlap (Jaccard 0.2368) and structural patterns, which correctly indicated non-clonality; BCB may have overestimated similarity based on superficial I/O patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered these as clones because both are file-processing utilities that read, transform, and write data, but the specific purposes are too distinct, so broad Type-3/4 similarity seems unlikely.
- 共享行为: Both perform file I/O operations using File, FileReader, FileWriter, BufferedReader.；Both handle file existence checks and error handling.；Both write transformed content to output files.
- 行为差异: Function A writes multiple files from byte arrays and then copies with a prepended line; Function B reads and modifies a single properties file line-by-line.；Function A creates directories; Function B copies a default file if missing.；The transformation logic (prepend vs. replace/insert) is entirely different.
- 修正建议: Improve model to distinguish general I/O boilerplate from true functional similarity.；Use contrastive learning with more diverse examples of non-clone file operations.

### case_id=5971 FN benchmark_preference_bias

- 方法: `readGeoParserResult` vs `getNetworkServersIPs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a record content, sends it to a geo-parser service, and parses the XML response to extract place names with associated gazetteer IDs, with retries and a testing mode.
- B 摘要: Connects to a URL, reads its content line by line, and extracts server IPs based on a specific header format (!SERVERS) and delimiter (:).
- 静态失败原因: The static BERT model likely correctly identified the low token overlap (Jaccard=0.14) and significant behavioral differences, thus predicting non-clone (0). However, BCB's gold label is 1, indicating that the model's strict semantic judgment conflicts with the broader annotation criteria used in BigCloneBench. The model failed to account for the benchmark's preference for structural/functional similarity even when the specific tasks are different.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this pair as a clone due to broad structural similarity: both involve network communication, line-by-line reading, and parsing text to extract fields into a collection. The shared pattern of opening a URL, reading lines, and iterating over parsed elements might be considered Type-3/Type-4 similarity in BigCloneBench, especially if the annotators focused on the control flow and error handling rather than the specific domain logic.
- 共享行为: Both establish a URL connection and read the response using BufferedReader.；Both parse the input stream to extract data and return a collection of results.；Both use try-catch blocks to handle IO exceptions.
- 行为差异: A constructs an XML request and sends it to a geo-parser service; B directly reads from a URL without constructing a request.；A parses XML using DocumentHelper and Element iterators; B parses plain text lines with simple string matching.；A includes retries (up to 3) and a testing mode; B has no retries or testing.；A extracts place names and gazetteer IDs; B extracts server IP addresses.
- 修正建议: Adjust the model's decision threshold or incorporate fine-tuning with BCB's annotation guidelines that allow for broader clone definitions.；Enhance the model to recognize high-level functional patterns (e.g., 'read-from-URL-and-parse') as clone indicators, even if local details differ.；Use data augmentation to expose the model to more BCB-style positive pairs with low token overlap but similar structure.

### case_id=5972 FN partial_functionality

- 方法: `testNetworkHTTP` vs `createHTML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Tests network connectivity by making multiple HTTP GET requests to several URLs and reading response streams, discarding all data.
- B 摘要: Generates an HTML string for different page types by reading a CSS file and constructing HTML content, optionally querying a database.
- 静态失败原因: The model focused on the overall semantic goal and structural differences (e.g., switch, database queries in B) and did not recognize the common I/O loop as sufficient for cloning.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled these as Type-3 clones due to the shared pattern of opening a URL, reading lines with BufferedReader, and handling exceptions, despite very different overall functionality.
- 共享行为: Both use URL, BufferedReader, InputStreamReader to read data line by line；Both handle IOException and include finally blocks
- 行为差异: A makes actual HTTP connections to external servers; B reads a local resource file；A discards all read data; B accumulates read data into a string；B builds HTML structure and queries a database; A does not；B is parametric based on PAGE_TYPE; A has a fixed sequence of URLs
- 修正建议: Enhance model to recognize common I/O idioms as a basis for partial similarity；Incorporate structural graph matching for patterns like URL->openStream->BufferedReader->while(readLine)

### case_id=5973 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `copyExternalResource`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by updating or adding a message entry.
- B 摘要: Copies a source file to a destination file using NIO FileChannel.
- 静态失败原因: The static model correctly distinguished the low token overlap and distinct semantics; it did not consider the broad resource management aspect that BCB might have used.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as resource management operations (file reading/writing) and ignored the specific domain difference, or the labeling could be a noise in the dataset.
- 共享行为: Both perform file I/O operations；Both close resources (streams/channels) after use；Both handle exceptions (one prints stack trace, one throws IOException)
- 行为差异: Function A reads and rewrites a properties file; Function B copies a binary file；A modifies content; B duplicates bytes；A depends on configuration structure; B is generic file copy
- 修正建议: Re-evaluate BCB ground truth for this pair; likely a mislabel；For model improvement, incorporate broader functional categories only if specifically required by the clone detection definition

### case_id=5974 FP boilerplate_overlap

- 方法: `populateResources` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Populates static resources by loading template files and images from predefined resource paths and saving them to a database.
- B 摘要: Downloads a file from a given URL to a local file, with progress updates via a MessageFrame.
- 静态失败原因: The model may have been misled by common API calls (URL, InputStream, BufferedReader, FileOutputStream) and similar boilerplate code for reading files, over-prioritizing structural patterns while ignoring the overall logic and parameters.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions perform entirely different tasks despite some superficial I/O similarities; the overall functionality and purpose are distinct.
- 共享行为: Both involve reading from input streams and writing to output streams.；Both handle file I/O and can throw exceptions.
- 行为差异: A loads multiple resources from internal paths and saves to a data store; B downloads a single file from a specified URL to the file system.；A has no progress tracking or return value (void); B reports progress and returns boolean success.；A processes strings and specific file types (.xml, .txt); B is a generic binary download.；A uses static methods with no parameters; B takes URL and destination path as parameters.
- 修正建议: Incorporate more context about method signatures, return types, and parameters.；Use data flow analysis or more fine-grained structural matching.；Add a classifier focusing on method purpose using method names or surrounding context.；Train with more negative examples that have similar I/O but different purposes.

### case_id=5975 FN benchmark_preference_bias

- 方法: `write` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Encrypts and wraps ByteBuffer data using SSL/TLS, handling handshake status and buffering.
- B 摘要: Fetches a resource by URL, caching it locally via HTTP with conditional retrieval based on modification time.
- 静态失败原因: Static BERT did not fail; it correctly predicted non-clone based on low token overlap and divergent AST structures. The BCB label appears mistaken.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'I/O wrapper' functions or 'stream processing' but this is overly broad; the functional semantics are entirely different. The annotation is likely an error.
- 行为差异: Function A performs SSL/TLS encryption on byte buffers; function B retrieves resources via HTTP and caches them as files.；Different input/output types: A takes ByteBuffer[] and returns ByteBuffer[]; B takes String and returns InputStream.；Different state management: A manages SSL engine handshake; B manages local file cache.；Different error handling: A throws RuntimeException on SSL exceptions; B catches exceptions and prints stack trace.
- 修正建议: Re-evaluate BCB annotation for this pair; consider correcting the label to 0.；Improve model robustness to handle cases where BCB labels are noisy.

### case_id=5976 FN benchmark_preference_bias

- 方法: `getResourceAsStream` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Downloads a remote resource via HTTP, caches it locally, and returns an InputStream.
- B 摘要: Configures and launches a Maven-based NexOpen project, handling XML profiles and reverse engineering files.
- 静态失败原因: Static BERT models rely on token overlap and local context; these functions have very low Jaccard similarity (0.067) and belong to different domains, leading to correct non-clone prediction but disagreeing with BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotators may have considered both as resource-loading or setup operations, interpreting loose functional similarity as Type-4 clone despite clear differences.
- 共享行为: Both perform file I/O operations (reading/writing files).；Both check file existence and handle exceptions with try-catch.；Both use InputStream/OutputStream for data transfer.
- 行为差异: Function A fetches a remote resource and caches it; Function B configures a project launch with XML parsing and Eclipse APIs.；Function A returns an InputStream; Function B is void and modifies project configuration.；Function A uses HttpURLConnection and caching logic; Function B uses DOM parsing and Property handling.
- 修正建议: Use models that capture deep semantic similarity beyond token overlap.；Incorporate type dependencies and call graphs for better context.；Calibrate model to BCB annotation guidelines for Type-4 clones.

### case_id=5977 FN benchmark_preference_bias

- 方法: `storeImage` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Stores an image from an InputStream to a file, with optional resizing and property-based path configuration.
- B 摘要: Handles an HTTP GET request to retrieve a page, render it, log it, and conditionally cache it to a file.
- 静态失败原因: Static BERT methods rely on token overlap and structural patterns; the low token Jaccard (0.073) and very different control flows cause the model to see no clone, while BCB's broad Type-4 criteria may consider them similar due to shared property and file operations. The model failed to capture this high-level intent.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider both as server-side file handling utilities that use property lookups and file I/O, thus partial functional similarity. However, this is a very loose interpretation and likely an annotation error.
- 共享行为: Both use Java properties for configuration；Both involve file I/O (writing/caching files)；Both have logging；Both handle exceptions
- 行为差异: storeImage uploads and saves an image; doGet retrieves and renders a web page；storeImage returns a path string; doGet writes to HTTP response；storeImage has image resizing logic; doGet has page caching and user permission checks；storeImage uses Calendar for date-based folders; doGet uses request parameters for page selection
- 修正建议: Improve semantic understanding of high-level intent (e.g., server-side file handling versus HTTP request processing).；Use models that capture underlying purpose beyond token overlap, such as dataflow or API usage patterns.；Reconsider BCB annotations for Type-4 clones that share only common patterns like property loading and file I/O.

### case_id=5978 FN partial_functionality

- 方法: `doVersionCheck` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for a new version of jEdit by reading a version file from a URL.
- B 摘要: Registers a user in a system, creates a forum user via URL, and persists the user.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low token-level overlap (Jaccard 0.14) and different method names and overall logic. The model may not capture the structural similarity of the URL-reading pattern without explicit dataflow information.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone (Type-4) because both functions involve the same high-level pattern: connecting to a URL, reading a response, parsing it, and reacting to the result. Despite different purposes, the structural similarity and shared API usage are strong enough for BCB's broad clone definition.
- 共享行为: Both open a URL and read lines from an input stream using BufferedReader and InputStreamReader.；Both handle IOException with error logging or user messaging.；Both use a while loop to read lines and process them conditionally.
- 行为差异: doVersionCheck reads version and build info from a simple property file and compares versions; register reads forum ID from URL response and sets it on the User object.；register includes parameter validation, password encoding, setting registration date and hash, persisting with entity manager, and sending confirmation email; doVersionCheck only shows a message or calls newVersionAvailable.；register has additional error handling for NumberFormatException and throws RuntimeException; doVersionCheck catches IOException and shows an error dialog.
- 修正建议: Incorporate dataflow analysis to capture sequences of I/O operations and API calls.；Use graph-based representations that highlight control flow and object usage.；Enhance training with more examples of Type-4 clones that share structural patterns despite different contexts.

### case_id=5979 FN boilerplate_overlap

- 方法: `createSettingsIfNecessary` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Creates a settings file from a bundled resource if it does not exist.
- B 摘要: Caches a remote resource locally and returns an InputStream.
- 静态失败原因: Static BERT may have missed the distinction due to overlapping vocabulary related to streams and file operations, despite low token Jaccard.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label as clone due to superficial similarity in stream handling and file I/O patterns, even though overall functionality differs.
- 共享行为: Both involve file existence checks before proceeding；Both copy data from an input stream to an output stream；Both manage I/O streams with try-catch-finally
- 行为差异: Different inputs: bundled resource vs remote URL；Different outputs: settings file vs cache file；Different intentions: creation vs caching/retrieval；Return values: void vs InputStream
- 修正建议: Incorporate data-flow analysis to distinguish source/destination；Focus on method signatures and high-level intent

### case_id=5980 FN partial_functionality

- 方法: `testNetworkHTTP` vs `getJSONData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Tests network connectivity by making multiple HTTP GET requests to various URLs and discarding response.
- B 摘要: Fetches JSON data from a given URL using HTTP GET and parses it into a JSONObject.
- 静态失败原因: Static BERT models may have distinguished between a test method and a utility method, focusing on differences in HTTP client usage and absence of JSON parsing in A, leading to low similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label it as clone because both functions involve HTTP GET requests and reading the response line by line, which matches a common pattern in network I/O considered as a clone despite different specific usage.
- 共享行为: Make HTTP GET request；Read response using BufferedReader and InputStreamReader；Handle exceptions
- 行为差异: Number of requests (multiple vs single)；Response processing (discard vs parse to JSON)；Input/Output (no input/void output vs URL input/JSONObject output)；HTTP library (HttpURLConnection vs DefaultHttpClient)
- 修正建议: Improve understanding of functional purpose beyond I/O patterns；Incorporate data flow analysis to track whether response is used；Consider method signature differences (input/output)

### case_id=5981 FN partial_functionality

- 方法: `tail` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads the last 1024 bytes of an HDFS file and optionally tails it with a sleep loop.
- B 摘要: Launches a NexOpen project configuration by checking Maven pom files, handling Hibernate dialects, and scheduling an install project action.
- 静态失败原因: Static BERT correctly identified low token overlap (0.093) and distinct semantic contexts, but BCB's annotation might have been influenced by superficial I/O similarities. The model's prediction of non-clone is actually correct under strict semantics, so the failure is misalignment with BCB's broad labeling criteria.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to both functions involving file reading and data copying (IOUtils.copy), or due to both being 'utility' methods that handle I/O, but this is a very loose interpretation.
- 共享行为: Both use IOUtils.copy for copying data.；Both handle file existence checks.
- 行为差异: Function A operates on HDFS files with seek and offset; B operates on local Eclipse workspace files.；A is a simple tail command; B is a complex launch configuration with multiple file processing steps.；A uses a loop and sleep; B uses progress monitor and project refresh.；B involves XML parsing, property handling, and error logging; A does not.
- 修正建议: Improve training data to reduce false positives in BCB by requiring stronger functional similarity.；Include context-aware features that distinguish between different domains (Eclipse vs HDFS).；Use graph-based representations to capture control flow and data dependencies more accurately.

### case_id=5982 FN partial_functionality

- 方法: `testNetworkHTTP` vs `readReferenceText`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Tests HTTP connectivity by making multiple GET requests to various URLs and reading responses without processing.
- B 摘要: Reads a reference text file from a plugin bundle, builds a string, and returns it, throwing exceptions on failure.
- 静态失败原因: Static BERT models rely on token overlap and syntactic structure; this pair has low Jaccard (0.17) and different method signatures, so the model likely saw them as non-clones. However, a human might see a shared pattern of URL-based stream reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider these clones if they focus on the common pattern of reading lines from a URL stream, disregarding the different contexts and side effects.
- 共享行为: Both use BufferedReader to read from an InputStream obtained from a URL.；Both use try-catch for IOException.；Both involve reading lines from a stream.
- 行为差异: Function a makes multiple HTTP connections and discards all read data; function b reads a single resource and returns the content.；Function a has no return value and is a test; function b returns a string.；Function a uses HttpURLConnection with manual disconnect; function b uses URL.openStream() and streams.；Function a has a specific sequence of URLs with parameters; function b uses a dynamic filename from an identifier.
- 修正建议: Use data flow analysis to capture the I/O pattern despite different variable names.；Incorporate conceptual knowledge about common library usage (HTTP vs. file reading).；Consider partial clone detection with a threshold for common subgraph.

### case_id=5983 FP partial_functionality

- 方法: `run` vs `retrieveTemplate`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches a tile from a data source by URL, reads GeoJSON, constructs a VectorTile, extracts geometries, and adds to a data layer.
- B 摘要: Retrieves a blog template from a URL, reads and caches it, and returns the cached content.
- 静态失败原因: Static BERT models may overweigh the lexical and structural overlap of the common I/O pattern (URL, BufferedReader, StringBuilder), ignoring the broader semantic context and differing post-processing steps.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely marked as non-clone because the overall functionality differs significantly; the common I/O pattern is a minor sub-task, not sufficient for Type-3/4 similarity given the distinct high-level purposes.
- 共享行为: Both read text from a URL using BufferedReader line by line and concatenate into a string.
- 行为差异: Code A handles multiple protocols (file, http), constructs a VectorTile and processes geometries, adds to data loader and updates display cache.；Code B caches the result and has no geometry processing.
- 修正建议: Incorporate dataflow analysis to trace how the read data is used.；Consider method-level context such as class name, imported types, and called methods.；Use contrastive learning with hard negative pairs emphasizing different high-level goals despite similar I/O.

### case_id=5984 FN benchmark_preference_bias

- 方法: `convert` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Converts an ACRNEMA medical image file to DICOM format by validating pixel data and adding UIDs.
- B 摘要: Launches a NexOpen project build by verifying project structure, manipulating Maven pom.xml files, and setting Hibernate properties.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed (predicted non-clone) because the token-level similarity is very low (Jaccard 0.0578) and the functions belong to entirely different domains with no shared vocabulary or API calls. The model could not capture the high-level structural similarity that BCB annotators might have considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to broad Type-4 functional similarity: both functions involve complex file I/O, conditional checks, and writing transformed data to output streams, despite differing domains. The annotation could also be influenced by the length and structural complexity of both functions.
- 共享行为: Both use try-finally blocks for resource management；Both read and write to files using streams；Both check conditions before proceeding and return early if invalid
- 行为差异: Different domains: medical imaging vs Eclipse project configuration；Different operations: image pixel conversion vs XML/properties manipulation；Different output: modified image file vs triggered build job
- 修正建议: Improve tokenization to capture structural patterns beyond exact matches；Incorporate domain-agnostic functional similarity measures, such as data-flow or control-flow graphs；Re-annotate ambiguous pairs with stricter functional criteria

### case_id=5985 FN partial_functionality

- 方法: `main` vs `getWebByUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: main method that sends a hardcoded POST request to RenRen API and prints the response line by line.
- B 摘要: method that fetches a web page content by URL, saves it to a file, and recursively processes links.
- 静态失败原因: Static BERT models rely on lexical and API-level overlap, which is low (Jaccard 0.152). The methods have different method names, constant strings, and structural patterns (main vs method), making it hard for the model to recognize the shared high-level functionality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers these Type-4 clones because both implement the core behavior of fetching content from a URL and processing it line by line, despite differences in I/O and parameterization.
- 共享行为: Both open a URL connection and read input line by line using BufferedReader.；Both output the content (console print vs file write) and print progress messages.；Both handle exceptions during network operations.
- 行为差异: Function A is a static main method with hardcoded API parameters; Function B is an instance method with parameters.；Function A uses HTTP POST; Function B uses GET (via openStream).；Function A outputs to console; Function B writes to a file and supports recursive crawling.；Function A includes specific RenRen API setup; Function B is generic web fetching.
- 修正建议: Train on examples of Type-4 clones even with low lexical overlap.；Incorporate data flow or control flow features to capture core I/O patterns.；Use contrastive learning to align similar behavioral snippets regardless of specific APIs.

### case_id=5986 FP boilerplate_overlap

- 方法: `getVersion` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a version string from a remote URL and returns it, ignoring the actual content beyond the first line.
- B 摘要: Reads all lines from a remote URL and prints each line to standard output.
- 静态失败原因: Static models like GraphCodeBERT often rely on lexical and structural similarity. The two functions share a high token Jaccard similarity (0.306) due to common API patterns (URL, BufferedReader, while loop). This leads the model to predict a clone based on the overlapping boilerplate, ignoring the semantic differences in what is done with the data.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because their overall purpose is different: one is a getter for a specific version, the other is a generic URL content printer. Despite similar I/O code, the functionality and usage contexts are distinct.
- 共享行为: Both use similar boilerplate code to open a URL connection and read lines with BufferedReader.；Both perform HTTP GET requests to retrieve a resource.
- 行为差异: Function A returns the last line read as a version string, while Function B prints every line.；Function A handles exceptions by setting version to null; Function B throws IOException.；Function A is a private helper method; Function B is the main entry point.
- 修正建议: Improve model to distinguish between shared boilerplate and core functionality.；Incorporate data-flow analysis to track how the read data is used.；Use contrastive learning on examples where only the I/O pattern matches but output differs.

### case_id=5987 FN boilerplate_overlap

- 方法: `storeImage` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.5`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Stores an image from an input stream to a file system, with optional resizing.
- B 摘要: Downloads a KMZ file from a URL and extracts its zip entries to files.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on token-level similarity, which is low (Jaccard=0.104), and missed the higher-level functional similarity of stream-to-file operations.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label them as clones because they share the high-level task of reading from a stream and writing to files, a common I/O pattern that BCB sometimes considers broad Type-4 clones despite different specific implementations.
- 共享行为: Both read from an input stream and write to files
- 行为差异: Different input sources (parameter vs URL)；Different number of output files (one vs multiple)；Different processing (optional resize vs zip extraction)；Different output file naming and structure
- 修正建议: Incorporate structural abstractions like dataflow or I/O stream usage patterns；Use models that capture long-range dependencies and functional intent beyond lexical tokens

### case_id=5988 FN partial_functionality

- 方法: `PageLoader` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Constructor that reads the content of a given URL into a string field.
- B 摘要: Method that performs HTTP GET request, handles redirects, parses OPDS catalog or downloads book, with error handling and progress reporting.
- 静态失败原因: Static BERT models rely on lexical and structural similarity; the token Jaccard is very low (0.043) and the code lengths differ greatly (A ~10 lines, B ~100+ lines). The models likely failed to capture the deep semantic similarity of URL fetching due to high lexical divergence and different control flow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both involve reading from a URL, even though B is much more complex. The core functionality of fetching URL content is present in both, which could be seen as partial functional similarity.
- 共享行为: Both open a connection to a URL and read data from it.
- 行为差异: A is a simple synchronous read of the entire stream; B uses HTTP connection with headers, timeouts, handles multiple response types, follows redirects, parses content, downloads files, and runs asynchronously.；A is a constructor that sets a field; B is a void method that updates internal state and invokes callbacks.；B includes extensive error handling, progress reporting, and conditional logic based on response headers.
- 修正建议: Improve models to recognize partial functional overlap by learning to match high-level API usage patterns (e.g., URL.openStream vs URL.openConnection).；Use dataflow or graph-based representations to capture similar I/O operations despite different surrounding code.；Incorporate type information and method signatures to abstract away implementation details.

### case_id=5989 FP lexical_or_api_overlap

- 方法: `SRWGuiClient` vs `retrieveTemplate`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Constructor to initialize a GUI browser, read XML from a URL, optionally apply XSLT, and display HTML.
- B 摘要: Private method to retrieve and cache the HTML content from a blog URL as a string.
- 静态失败原因: The model likely overemphasized lexical similarities such as URL, BufferedReader, and readLine loops, leading it to ignore the vast difference in overall purpose and additional logic (XML, GUI).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would consider these non-clones because the overall functionality differs: one builds a browser GUI with XML/XSLT processing, the other simply fetches a blog template as a string. The shared reading from URL is incidental boilerplate.
- 共享行为: Both read from a URL using BufferedReader and InputStreamReader；Both read lines in a loop until null；Both use StringBuilder/StringBuffer for string concatenation
- 行为差异: A is a constructor setting up a full GUI; B is a private method returning a string；A processes XML and XSLT; B just reads raw content；A displays HTML in a JEditorPane; B does not display anything；A has extensive GUI and event handling; B has none
- 修正建议: Incorporate structural or semantic features capturing the method's core responsibility；Use graph-based representations that differentiate GUI setup from string retrieval；Train on paired examples with varied purposes but similar boilerplate

### case_id=5990 FP lexical_or_api_overlap

- 方法: `addDataFromURL` vs `getUser`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads from a URL and appends each line to a string buffer.
- B 摘要: Loads a User from a DAO or falls back to parsing a config file from the classpath to create and save a User object.
- 静态失败原因: Static model likely overemphasized lexical overlap of common constructs (URL, BufferedReader, while loop, try-catch) without capturing distinct semantic intents.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely annotated these as non-clones due to entirely different overall functionality despite shared API usage patterns.
- 共享行为: Both use BufferedReader to read line by line；Both handle exceptions in try-catch blocks
- 行为差异: First method appends text to a buffer, second returns a User object；First method always reads from a given URL, second reads from classpath resource only if DAO lookup fails；Second method involves parsing tokens and creating/saving domain objects
- 修正建议: Incorporate dataflow analysis to distinguish between text accumulation vs object construction；Use type-aware representation to differentiate primitive string operations from domain object logic

### case_id=5991 FN benchmark_preference_bias

- 方法: `main` vs `decodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its Zip entries to files.
- B 摘要: Decodes a Base64-encoded input file and writes the decoded data to an output file.
- 静态失败原因: The token Jaccard similarity is low (0.22619) due to different API calls (e.g., 'ZipInputStream' vs 'Base64.InputStream', 'FileInputStream' vs 'BufferedInputStream'), and the function signatures differ (main vs decodeFileToFile). A static model like GraphCodeBERT may rely on lexical overlap and control-flow structure; this pair lacks syntactic similarity and the structural similarity (while loop pattern) is too generic to be recognized as a clone without understanding the broader domain context.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotators likely considered these as clones because both are common boilerplate patterns for reading from an input stream, processing (unzip or decode), and writing to an output stream. The high-level goal of 'transforming input data to output files' is similar, and the structural pattern of buffered I/O loops is shared, fitting a broad Type-4 or partial functionality clone definition.
- 共享行为: Reads from an InputStream using buffered reading；Writes to an OutputStream using buffered writing；Uses a while loop to read chunks of bytes and write them；Performs file I/O operations with stream handling
- 行为差异: Function A handles HTTP/file URL retrieval and Zip entry extraction; Function B handles Base64 decoding of a local file.；Function A writes each Zip entry to a separate file; Function B writes a single decoded output file.；Function A has no return value and throws Exception; Function B returns boolean success and handles exceptions internally.；Function A uses different compression-related classes (ZipInputStream, ZipEntry) whereas Function B uses Base64.InputStream.
- 修正建议: Include domain-specific semantics, e.g., that both are I/O transformation utilities operating on byte streams.；Use graph representations that capture high-level data flow and compression/decompression intent.；Augment training data with more examples of broad semantic clones that share structural patterns but differ in API libraries.

### case_id=5992 FN partial_functionality

- 方法: `loadSourceCode` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads source code from a file resource, applies syntax highlighting, and returns it as an HTML string.
- B 摘要: Opens a URL connection, reads all lines, and logs the content.
- 静态失败原因: Static BERT likely focused on low token overlap (0.206) and different method names/literals, missing the structural similarity of the read loop pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs as clones if they share a common algorithmic pattern, even if details differ. Both functions implement a URL reading loop, which is considered a cloneable fragment.
- 共享行为: Both open a URL and create a BufferedReader to read lines.；Both read lines until null using readLine() in a while loop.
- 行为差异: A catches exceptions and uses a fallback error string; B throws Exception.；A uses a file resource URL from a field; B uses a hardcoded URL.；A applies syntax highlighting to each line; B appends raw lines.；A builds an HTML string; B logs the result.
- 修正建议: Incorporate structural similarity via control flow graphs or program dependency graphs.；Use contrastive learning to emphasize common patterns like read loops.；Add data augmentation to generalize over literal differences.

### case_id=5993 FN lexical_or_api_overlap

- 方法: `doGet` vs `descargarArchivo`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests by retrieving and displaying a page with access control, logging, and caching.
- B 摘要: Copies a file from a source path to a destination path using file channels.
- 静态失败原因: Low token overlap and different domain APIs make it hard for a static model to detect similarity without deeper semantic understanding.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled them as clone due to both involving file I/O and error handling, but the overall functionality is too different for a typical Type-3/4 clone.
- 共享行为: Both methods handle IOException；Both are void methods
- 行为差异: A executes complex business logic for page rendering; B simply copies a file；A interacts with HTTP request/response; B deals with local files；A uses logging, property lookups, caching; B has none
- 修正建议: Incorporate control flow and data flow analysis；Use models that capture functional intent beyond lexical tokens

### case_id=5994 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `postXml`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter feed using HTTP GET with Apache HttpClient and returns the response as a string.
- B 摘要: Sends an XML/SOAP POST request using HttpURLConnection and returns the response string.
- 静态失败原因: A static BERT/GraphCodeBERT model might have focused on lexical overlaps (e.g., 'BufferedReader', 'StringBuilder', 'IOException', 'Http') and the general structure of opening a connection, reading lines, and building a string, missing the critical differences in HTTP method and parameters.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled this as non-clone because the functions have different intents (read vs post) and use different HTTP methods and libraries, making them Type-4 but not similar enough for BCB's annotation criteria.
- 共享行为: Both make HTTP requests and read the response line by line into a StringBuilder.；Both return the accumulated string.；Both use try-catch for IOException.
- 行为差异: Function A uses HTTP GET, while B uses POST with a request body.；Function A uses Apache HttpClient, B uses Java URLConnection.；A has a fixed URL; B takes URL, SOAP action, and XML as parameters.；A logs errors and prints stack traces; B throws a RuntimeException.
- 修正建议: Add training examples of GET vs POST with different libraries.；Incorporate deeper dataflow analysis to distinguish request methods.；Use API call patterns to differentiate HTTP operations.

### case_id=5995 FN partial_functionality

- 方法: `main` vs `downLoadZippedFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Main method that downloads a specific KMZ file from a hardcoded URL and extracts all zip entries to the current directory, printing each entry.
- B 摘要: Private helper that downloads a zip file from a given URL, saves it to a temporary file, unzips it to a specified destination directory, and returns the local URL.
- 静态失败原因: Static BERT models often rely on token-level and structural similarity; here the low token Jaccard (0.1585), different method names, and different API usage (ZipInputStream vs IOUtils.copy) obscured the semantic overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers the high-level functionality of downloading and unzipping a file as sufficient for clone classification, despite differences in parameters, output, and exact extraction method.
- 共享行为: Both download a zip file from a URL；Both extract the contents of the zip file
- 行为差异: A uses hardcoded URL; B takes URL as parameter；A extracts entries directly from zip stream; B saves to temp file first then unzips；A extracts to current directory; B extracts to destDir；A prints each entry; B does not print
- 修正建议: Use program dependence graphs or control-flow alignment to capture high-level similarity；Incorporate data flow analysis to identify shared operations like URL.openStream and unzip；Train with more examples of broad Type-3/4 clones that vary in implementation details

### case_id=5996 FP partial_functionality

- 方法: `getWebPage` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches the content of a web page as a string by reading lines.
- B 摘要: Downloads an RDF model from a URL using HTTP headers and parses it.
- 静态失败原因: The static model likely focused on the common API usage (URL, InputStream, IOException) and structural similarity (try-catch blocks), ignoring the crucial differences in output processing and data types.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels these as non-clones because they perform fundamentally different tasks: retrieving plain text vs downloading and parsing structured RDF data. The output types and processing logic are completely distinct.
- 共享行为: Both open a URL connection and read from an input stream.；Both handle IOExceptions.
- 行为差异: Different return types: String vs Model.；Different data processing: line-by-line text concatenation vs RDF parsing.；Different error handling: throws Error vs logs and throws RuntimeException.；Function B sets HTTP request properties; Function A does not.
- 修正建议: Incorporate data flow analysis to track how the input stream is processed.；Consider output type and downstream usage as distinguishing features.；Use fine-grained semantic matching that differentiates between reading raw text and parsing structured data.

### case_id=5997 FN benchmark_preference_bias

- 方法: `downloadURLtoString` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a URL and returns its contents as a string.
- B 摘要: Parses static string fields to populate multiple sets and maps for a Tibetan transliteration system.
- 静态失败原因: Static BERT/GraphCodeBERT did not fail; it correctly predicted non-clone due to extremely low token overlap (Jaccard 0.06) and distinct structural patterns. The error is in the BCB ground truth.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone based on a very loose notion of both being 'data reading' methods, but the token and structural overlap is negligible. This appears to be an annotation error.
- 共享行为: Both involve reading input and constructing data structures via loops.；Both use while loops to process tokens or lines.
- 行为差异: A downloads from a network URL; B reads from pre-initialized string fields.；A produces a single string output; B populates global collections with side effects.；A is a simple I/O wrapper; B is a complex initialization routine with many branches and error handling.；The data formats and processing logic are completely unrelated.
- 修正建议: Re-evaluate the BCB annotation for this pair; it is likely a false positive.；If reannotation confirms no clone, update the dataset to remove this label.

### case_id=5998 FN partial_functionality

- 方法: `copyResource` vs `byReference`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file byte by byte.
- B 摘要: Copies an InputStream to a temporary file and returns a DigitalObjectContent.
- 静态失败原因: Static BERT models rely on token overlap and syntactic structure; the low token Jaccard (0.145) and different method signatures, variable names, and API calls (manual loop vs IOUtils) lead to a non-clone prediction. The models fail to capture the underlying functional similarity of data copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions perform the core task of copying data from an input source to a file, which is a common pattern. The differences in signatures, exception handling, and return types are considered minor variations in Type-4 clones.
- 共享行为: Both read from an input source and write to an output file.；Both handle potential IOExceptions.；Both close the output stream after writing.
- 行为差异: Method A takes no parameters (uses instance fields), method B takes an InputStream.；Method A writes to a specified destination file, method B creates a temporary file.；Method A returns void, method B returns a DigitalObjectContent.；Method A uses a manual byte-by-byte loop, method B uses IOUtils.copyLarge.
- 修正建议: Incorporate data flow analysis to detect input-output transformation patterns.；Use models that learn from code documentation or comments.；Augment training with pairs that have different APIs but same high-level functionality.

### case_id=5999 FP lexical_or_api_overlap

- 方法: `readPage` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a web page line by line, optionally ignoring comment lines starting with '#', and returns the concatenated HTML content.
- B 摘要: Reads a YouTube page, extracts video parameters from a line containing 'fullscreenUrl', and constructs a download URL for the video.
- 静态失败原因: The model likely over-relied on lexical and structural similarities (both use BufferedReader, URL, while loop reading lines) and missed the semantic difference in purpose and data processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when the core logic differs significantly, even if there is boilerplate I/O overlap. The shared read-line pattern is not sufficient for clone classification.
- 共享行为: Open a URL connection；Read lines using BufferedReader；Concatenate lines into a string
- 行为差异: A optionally filters lines starting with '#'; B searches for 'fullscreenUrl' substring.；B parses the extracted line to get video_id, t, title and builds a new URL.；B updates a progress bar and prints debug information; A does not.；B sets setDoOutput(true) on the connection; A does not.
- 修正建议: Incorporate data flow analysis to track how read data is used.；Use type or method context to distinguish generic I/O from specific extraction.；Consider method names and overall structure for better differentiation.

### case_id=6000 FN lexical_or_api_overlap

- 方法: `init` vs `login`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads controller classes from a registry file using class loader.
- B 摘要: Logs in to LOLA service by sending HTTP POST with credentials and returns session ID.
- 静态失败原因: The static BERT model correctly predicted non-clone because it learned to distinguish functionality. However, according to BCB label, it failed because it did not recognize the broad structural similarity that BCB annotators considered sufficient for a Type-3/4 clone. The model likely focused on semantic differences rather than shared I/O patterns.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as a clone due to superficial structural similarities: both methods have try-catch blocks, use BufferedReader, URL objects, and perform I/O operations. Additionally, both are initialization-like methods in a broad sense.
- 共享行为: Both use BufferedReader to read text from an input stream.；Both use URL or URL-related objects to locate resources.；Both handle exceptions with try-catch blocks.
- 行为差异: Function A loads Java classes, while B performs an HTTP login.；A reads from local classpath resources, B sends data to a remote URL.；A returns void, B returns a String (session ID).；A uses classLoader, B uses URLConnection with POST.
- 修正建议: Train on more diverse non-clones with similar APIs but different semantics.；Add negative samples that share I/O patterns.；Incorporate functional flow analysis.
