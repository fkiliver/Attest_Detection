# Error Case Studies 1-500

- Source model: `configured-llm`
- Cases: `1` to `500`

### case_id=1 FN benchmark_preference_bias

- 方法: `main` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its ZIP entries to disk.
- B 摘要: Sets up a Weka experiment with GUI, handling command-line flags for loading/saving serialized Experiment objects.
- 静态失败原因: The static BERT model correctly predicted non-clone (0) because the code structures and tokens are largely disjoint; it did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have considered both as main methods with file I/O and exception handling as Type-3/4 clones, but the low token overlap and completely different purpose suggest this is an over-annotation.
- 共享行为: Both are public static void main methods；Both use try-catch or throws Exception for error handling；Both perform file I/O operations
- 行为差异: Function A processes a single hardcoded URL and extracts ZIP entries sequentially；Function B parses command-line arguments, creates a GUI, and manages Experiment serialization；Function A uses ZipInputStream and BufferedOutputStream; Function B uses ObjectInputStream/ObjectOutputStream；Function B includes a GUI with window listener, threading, and user interaction; Function A has no GUI
- 修正建议: Re-evaluate BCB annotation for this pair; likely should be non-clone；Consider using stricter thresholds for clone detection in benchmark

### case_id=2 FP boilerplate_overlap

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads and parses multiple comma-separated token lists into sets and a mapping, then processes a file to build lookup tables.
- B 摘要: Copies a file from source to destination using a byte buffer.
- 静态失败原因: Static BERT likely relied on overlapping I/O tokens (InputStream, FileInputStream, IOException, catch) and similar boilerplate structure (try-catch, throws IOException) while missing the vast difference in data manipulation and algorithmic logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would reject this pair because the functions have no meaningful functional similarity; one is a complex data initializer, the other is a generic file copy utility.
- 共享行为: Both handle IOException via try-catch.
- 行为差异: readData builds data structures (HashSets, HashMap) from parsed tokens; copyFile performs a straightforward byte-level copy.；readData involves file parsing with column indexing and conditional logic; copyFile uses streaming I/O with no parsing.；readData updates multiple global sets and maps; copyFile writes to a new file and has no side effects besides copying.
- 修正建议: Train with contrastive examples that penalize low-level API similarity when high-level semantics diverge.；Incorporate control flow and data flow graphs to capture structural differences.；Use longer context or hierarchical embeddings to distinguish between file I/O scaffolding and core logic.

### case_id=3 FN partial_functionality

- 方法: `doGet` vs `createTempFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET request by retrieving a page, checking access, and optionally caching the response to a temp file.
- B 摘要: Creates a temp file from a classpath resource for testing by copying the resource stream.
- 静态失败原因: Token overlap is very low (0.052), and the overall methods differ greatly in length and purpose; static BERT models prioritize lexical and structural similarity, missing the subtle shared file operation pattern that is only a small part of A.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may focus on the common pattern of temporary file creation and writing, considering that as sufficient functional similarity (Type-4 broad functionality).
- 共享行为: Both use File.createTempFile to create a temporary file and write data to it.
- 行为差异: A involves HTTP request handling, page lookup, access control, logging, and multiple exception paths; B simply copies a resource to a temp file without any user or session context.
- 修正建议: Use dataflow or structural analysis to focus on API call similarity.；Train to recognize partial similarity even when overall structure differs.；Augment training set with examples of methods sharing utility calls.

### case_id=4 FP boilerplate_overlap

- 方法: `readTwitterFead` vs `createDialogArea`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches Twitter timeline as JSON over HTTP and returns the response body as a String.
- B 摘要: Creates a dialog area composite in SWT, loads a license text from a bundle resource, and displays it in a browser or text widget.
- 静态失败原因: Static BERT/GraphCodeBERT might over-rely on token-level overlap, especially the common I/O pattern (BufferedReader, InputStreamReader, while loop, append). The long loop structure and similar variable names (reader, line, sb) could cause high attention on that segment, making it appear as clone. The model may have missed the surrounding context that indicates different purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones if functions are semantically different even if there is some syntactic similarity. The similarity here is only in boilerplate I/O reading loops, which is common to many programs. The overall functionality is completely different (network download vs UI dialog creation), so BCB labels 0.
- 共享行为: Reads from a stream line by line using BufferedReader；Appends each line to a StringBuilder/StringBuffer
- 行为差异: A uses Apache HttpClient for HTTP GET; B uses resource URL.openStream；A returns a string; B returns a composite Control；A has no UI; B creates SWT composite and widgets；Error handling: A catches ClientProtocolException and IOException, logs; B catches IOException and prints stack trace, has finally block to close streams
- 修正建议: Use structure-aware models that can differentiate between core logic and common boilerplate；Incorporate caller context or method signatures；Train with hard negatives that share boilerplate but differ in functionality

### case_id=5 FP boilerplate_overlap

- 方法: `readUNI` vs `postRequest`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a tab-delimited file from a URL resource and populates a vector with concatenated id and description strings.
- B 摘要: Sends an HTTP POST request with form parameters and returns the response body as a string.
- 静态失败原因: Static BERT models likely over-emphasized shared boilerplate code (URL creation, try-catch, InputStream/Reader, while loop) and missed the critical difference in HTTP method and data direction. The model may have treated both as generic 'network read' functions.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled these as non-clones because they perform fundamentally different HTTP operations (GET vs POST) and have distinct data processing logic. The token Jaccard is low (0.20), indicating little code similarity beyond common networking boilerplate.
- 共享行为: Both open a URL connection and read input data.；Both handle exceptions with try-catch blocks that print stack traces.；Both use loops to process line-oriented input (Scanner for A, BufferedReader for B).
- 行为差异: A performs a GET-like read; B performs a POST with form data.；A parses tab-separated fields; B returns raw concatenated response.；A modifies an externally provided Vector; B returns a String.；A uses Scanner with delimiter; B uses PrintWriter to write output before reading input.
- 修正建议: Encode directional data flow (whether output is written) as a feature.；Use API-level abstraction to differentiate HTTP methods.；Leverage control flow and data dependency analysis to focus on core logic rather than I/O boilerplate.

### case_id=6 FN benchmark_preference_bias

- 方法: `doGet` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request for a portal page, including parameter processing, user authentication, page retrieval, and rendering with caching.
- B 摘要: Converts a DICOM file from ACRNEMA to DICOM format, parsing headers and pixel data, and writing output.
- 静态失败原因: The static BERT model correctly predicted non-clone (0) due to extremely low lexical overlap (Jaccard=0.085) and no shared API calls or functional patterns. The 'failure' is from the benchmark perspective mislabeling this pair as a clone; the model's prediction is actually correct.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB annotation likely considered both functions as having a similar structure of try-catch blocks, logging, and conditional checks, but this is far too generic to indicate semantic similarity. The pair appears to be a labeling error in the BCB dataset.
- 行为差异: Function A handles HTTP requests and web page rendering; function B converts file formats.；Function A uses servlet API, logging, and property lookups; function B uses DICOM parsing and byte-level I/O.；Function A involves user permissions and caching; function B involves pixel data inflation and file metadata.；The control flow and error handling patterns are completely different.
- 修正建议: Re-evaluate the BCB annotation for this pair; it is likely a false positive.；Provide clearer guidelines for Type-4 clone detection to avoid unrelated functions being labeled as clones.

### case_id=7 FN partial_functionality

- 方法: `getHTML` vs `getEncoding`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches the full HTML content from a URL with specified encoding, optionally writes it to a file.
- B 摘要: Extracts the character encoding from HTTP headers or HTML content of a URL, returning a string.
- 静态失败原因: Static BERT relies on token overlap and local context; the functions have different names, returns, and overall purpose, causing low similarity despite shared structural patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels functions as clones if they belong to the same domain (here web fetching) and share significant logic patterns, even if outputs differ.
- 共享行为: Open HTTP connection to a URL；Read input stream line by line；Handle exceptions and close resources
- 行为差异: A returns entire HTML; B returns only encoding；A optionally writes results to file; B does not；A sets User-Agent header; B does not；B has fallback to STANDARDENCODING; A does not
- 修正建议: Use models that capture control flow and data dependencies (e.g., graph-based)；Incorporate domain-specific features like URL handling

### case_id=8 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches version build numbers from a URL and triggers a version check dialog.
- B 摘要: Performs a complex upgrade check involving database queries, license validation, and UI updates.
- 静态失败原因: The model likely over-relied on surface-level lexical overlap (e.g., 'URL', 'BufferedReader', 'readLine', 'while ((line = in.readLine()) != null)') and ignored the vast differences in the surrounding logic, data processing, and external API usage.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically treats functions as non-clones if they have significant structural and semantic differences, even if they share a high-level purpose like 'version check'. Here, the core logic and context diverge completely.
- 共享行为: Both open a URL connection and read lines using BufferedReader；Both perform some form of version or upgrade checking
- 行为差异: Function A uses a simple URL with one parameter; B constructs a URL with multiple parameters including client version, unit ID, and MAC addresses.；Function A retrieves only build numbers; B retrieves license data and a list of upgrades from an XML-like response.；Function A has no database interaction; B includes multiple database operations (DELETE, SELECT, INSERT).；Function A shows a wait cursor and a single error dialog; B manipulates multiple UI components and shows various message types.
- 修正建议: Incorporate structural similarity measures that capture control flow and data dependencies.；Use context-aware embeddings that model long-range dependencies and differentiate between generic I/O boilerplate and domain-specific logic.；Apply contrastive learning with hard negative examples that share lexical patterns but differ semantically.

### case_id=9 FN partial_functionality

- 方法: `copyResource` vs `createOutputStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or local file to a destination file byte by byte.
- B 摘要: Processes a zip file by copying all entries except 'content.xml', then creates a new 'content.xml' entry and returns a BufferedWriter for writing to it.
- 静态失败原因: The static model focused on low token similarity (Jaccard 0.16) and structural differences (different method signatures, parameters, and control flow), missing the high-level functional similarity of stream copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider these clones because both perform a 'copy' operation from input to output, and they share the underlying concept of data transfer, fitting a broad Type-4 interpretation.
- 共享行为: Both read from an input source and write to an output destination.
- 行为差异: A performs a simple byte-level copy of the entire source; B selectively copies zip entries, excludes one, and returns a writer for additional content.；A uses InputStream/OutputStream; B uses Reader/Writer with encoding and zip streams.；A throws Exception; B throws IOException.；A writes to a file; B writes to a zip and returns a writer.
- 修正建议: Incorporate task-level semantic similarity (e.g., both are stream-copy operations).；Use functional embeddings that capture I/O patterns.；Train on partial clone examples.

### case_id=10 FN boilerplate_overlap

- 方法: `getResourceAsStream` vs `execute`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a remote resource and caches it locally, returning an input stream.
- B 摘要: Converts a source file to a destination file using a specified conversion type and configuration.
- 静态失败原因: Low lexical overlap (Jaccard 0.105) and different method names led the model to focus on surface differences, missing the underlying structural similarity in I/O patterns.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider these as Type-4 clones because both implement the common template of resource copying with stream I/O and error handling, despite different specific functionalities.
- 共享行为: Both read from an input source and write to an output；Both use try-catch-finally blocks for resource management；Both close streams in finally block
- 行为差异: A handles HTTP connections and caching; B does not；A returns an InputStream; B returns void；A has conditional logic based on cache existence and modification times; B delegates to another execute method
- 修正建议: Incorporate data flow analysis to capture I/O patterns；Use structure-based models like ASTNN or CodeBERT with graph features；Augment training data with more diverse I/O clone pairs

### case_id=11 FN partial_functionality

- 方法: `invoke` vs `startScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Makes an HTTP POST request to a service URL, reads the response, handles retry on timeout, and deserializes JSON.
- B 摘要: Reads a script from a URL specified in attributes and appends it to a dialog script, with error handling.
- 静态失败原因: Static BERT/GraphCodeBERT models may rely on lexical overlap and structural similarity. Token Jaccard is low (0.137), so the model likely focused on the low overlap and different method names, and missed the high-level semantic pattern of URL reading and line concatenation that BCB considers. The model also may not capture the concept of 'reading from a remote resource' as a shared characteristic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as clone because both functions involve the common pattern of fetching content from a URL and processing it line by line, which is a Type-4 semantic clone. The specific context (RPC vs. script loading) is considered less important in broad BCB annotation.
- 共享行为: Both open a URL and read its content line by line.；Both concatenate lines into a string with newline separators.；Both use BufferedReader and InputStreamReader.
- 行为差异: A uses HTTP POST with JSON serialization, B uses direct URL reading.；A has retry logic on timeout, B does not.；A handles generic return types and JSON deserialization, B just appends to dialog.script.；B exits on error, A throws exceptions.
- 修正建议: Enhance model to recognize common behavior patterns like URL-based data fetching.；Incorporate API usage awareness (e.g., URL.openStream, HttpClient).；Use data augmentation with pairs that share partial functionality but differ in other parts.

### case_id=12 FN benchmark_preference_bias

- 方法: `populateResources` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Populates default resources (templates and images) from classpath/locale directories and saves them.
- B 摘要: Invokes a remote HTTP service with retry logic, parses JSON response.
- 静态失败原因: The model correctly predicted non-clone based on low lexical overlap and clear functional difference; if BCB label is ground truth, the model failed because it did not recognize a potential broad Type-4 similarity that is not apparent.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to superficial structural similarities (both read streams, both use StringBuilder) or considered them both as 'populating' operations, but this is a stretch and likely a dataset error.
- 共享行为: Both perform I/O operations reading from streams using BufferedReader；Both use try-catch for exception handling；Both build strings from read lines using StringBuilder
- 行为差异: A is local resource initialization; B is remote procedure call with HTTP；A saves resources to a database; B returns a deserialized object；B has retry logic and service discovery; A does not
- 修正建议: Improve functional understanding to differentiate local resource initialization from remote invocation；If BCB label is correct, incorporate broader context or project-level semantics

### case_id=13 FN partial_functionality

- 方法: `doTransfer` vs `handler`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request from a servlet to a remote URL, replicating headers and body, and sends back the response.
- B 摘要: Reads a web page from a URL, parses lines to extract substrings between given markers, and stores results in a map.
- 静态失败原因: Static BERT may have over-emphasized common keywords (URL, openStream, IOException) and missed the distinct high-level semantics due to limited context understanding.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB would likely label these non-clones because the overall purpose and logic differ fundamentally, despite sharing some low-level I/O operations.
- 共享行为: Both open a URL connection and read from an input stream.；Both handle MalformedURLException and IOException.
- 行为差异: A performs full HTTP proxy with request/response forwarding; B only extracts a specific token from the page.；A sends request body and sets request properties; B does not.；A writes response to servlet output stream; B updates a map.；A uses HttpURLConnection for arbitrary methods; B uses URL.openStream() for GET.
- 修正建议: Incorporate control-flow or data-flow features to differentiate proxy vs. scraper patterns.；Enhance training data with examples that distinguish between full HTTP forwarding and simple page scraping.；Use models that better capture long-range semantic intent.

### case_id=14 FP lexical_or_api_overlap

- 方法: `scrapeForIsbns` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Opens a URL, reads lines, extracts ISBN-10 patterns using regex, counts matches, and stores them in a map, with retry logic on connection failures.
- B 摘要: Opens a URL with optional authentication, reads lines, writes the entire content to a temporary file, and updates a status label with file size.
- 静态失败原因: The model may have over-weighted the common API usage (URL.openStream, BufferedReader, while loop) and missed the distinct functional goals and data handling logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the core purpose differs (scraping specific data vs. downloading a file) despite sharing URL-reading boilerplate.
- 共享行为: Both open a URL connection and read lines using BufferedReader；Both handle IOException
- 行为差异: A extracts ISBN patterns and counts matches; B writes entire content to a file；A includes retry logic on ConnectException; B has optional HTTP Basic Authentication；A updates a map outputIsbns; B updates a JLabel and creates a temporary file；A returns match count; B returns void
- 修正建议: Train with more examples emphasizing functional purpose；Incorporate structure-aware representations that distinguish boilerplate from core logic；Use contrastive learning to separate functions with similar APIs but different intents

### case_id=15 FN lexical_or_api_overlap

- 方法: `loadSourceCode` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads source code from a resource file and builds an HTML string with syntax-highlighted lines.
- B 摘要: Main method that constructs an HTTP POST request to RenRen API with predefined parameters and prints the response.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token and structural overlap; given the low Jaccard similarity (0.12) and differing API calls/semantics, the model correctly identified them as non-clones from a strict syntactic perspective, but BCB's broader clone definition considered them clones, causing a false negative.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled these as clones based on a very broad interpretation of both methods performing 'I/O operations reading lines from a stream' and possibly because both involve URL opening and BufferedReader usage, despite completely different application logic.
- 共享行为: Both use BufferedReader to read lines from an InputStream；Both open a URL to obtain an InputStream；Both use while loop to read lines until null
- 行为差异: Function A reads from a local file (class resource) while B reads from HTTP response；Function A processes lines with syntax highlighting, B simply prints lines；Function A stores result in a field, B prints to System.out；Function B constructs complex parameter objects and handles HTTP connection, A does not
- 修正建议: Improve sensitivity to common I/O patterns that might be considered clones under broad definitions；Incorporate functional similarity through code summarization or semantic embeddings beyond token overlap

### case_id=16 FP boilerplate_overlap

- 方法: `executePost` vs `postXml`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends form-encoded POST request, returns response string or null on exception.
- B 摘要: Sends XML POST request with optional SOAPAction, returns response string or throws RuntimeException.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by the high lexical overlap of boilerplate HTTP connection code (e.g., setRequestMethod, setRequestProperty, etc.) and the overall structure of sending and receiving data. It likely ignored the semantic differences in content type and error handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB may consider these as non-clones because despite similar HTTP POST pattern, the specific content type and error handling are considered distinct functionalities. The broad Type-4 similarity might be overridden by the differences in input format and exception behavior.
- 共享行为: Opens HTTP connection；Sets POST method；Sets output and input；Writes data to output stream
- 行为差异: Content-Type header differs (form vs xml)；Input data writing mechanism differs (bytes vs string)；Error handling differs (return null vs throw)；Additional headers (Content-Length, Content-Language vs Accept, SOAPAction)
- 修正建议: Use contrastive learning to distinguish similar boilerplate code；Incorporate API usage patterns (e.g., content type) into embedding；Focus on the semantic purpose (form vs xml) rather than structural similarity

### case_id=17 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `transferWSDL`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a key-value pair in a locale-specific properties file, creating the file from a template if it doesn't exist.
- B 摘要: Downloads a WSDL file from a URL via HTTP GET, optionally with basic authentication, and saves it to a temporary file.
- 静态失败原因: Static BERT/GraphCodeBERT relied on token and structural similarity, which is low (Jaccard 0.19), so it correctly predicted no clone; it failed to capture the BCB label because the label appears to be based on a broader, non-lexical similarity that the model does not consider.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider these clones due to both involving file I/O and resource management, but this seems overly broad; likely the BCB label is a mistake or based on a very lenient interpretation.
- 共享行为: Both perform file I/O operations (reading from an input source and writing to a file).
- 行为差异: Purpose: property modification vs WSDL download.；Input source: local file vs HTTP response.；Output destination: specific properties file vs temporary file.；Exception handling: generic vs specific WiseConnectionException.
- 修正建议: Incorporate higher-level task semantics or domain knowledge.；Use data flow analysis to distinguish different I/O patterns.；Consider functional clustering rather than just lexical matching.

### case_id=18 FP lexical_or_api_overlap

- 方法: `getUser` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user by login from a DAO or a config file.
- B 摘要: Downloads an RDF model from a URL.
- 静态失败原因: The model likely focused on structural/lexical similarities such as opening a URL connection, reading an InputStream, and handling exceptions, while missing the distinct domain and high-level functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers semantic similarity in functionality; these functions have entirely different purposes (user login vs. model download), thus not clones.
- 共享行为: Both take a string input and return an object after reading from a source；Both use try-catch for exception handling；Both involve opening a connection/stream and reading data
- 行为差异: Function A retrieves user credentials; Function B downloads a model；Function A reads from a classpath resource; Function B reads from a network URL；Function A parses colon-delimited tokens; Function B reads RDF/XML into a Model object
- 修正建议: Incorporate data flow analysis to differentiate input/output types；Use method name and return type embeddings to capture intent；Train on broader code understanding to distinguish domain-specific operations

### case_id=19 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `unJar`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a locale-specific properties file, modifies or adds a message key-value pair, and writes back.
- B 摘要: Extracts a specific entry from a JAR file to a target directory.
- 静态失败原因: Low token overlap (0.108) and distinct API sequences (Properties vs JarFile) made the model correctly identify non-clone, contradicting the BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider them Type-4 clones due to both being file modification operations, but this is a very loose interpretation; more likely an annotation error or bias towards broad resource management tasks.
- 共享行为: Both involve file I/O and exception handling with printStackTrace；Both manipulate file paths and strings
- 行为差异: A modifies properties files; B extracts from JAR archives；A reads text lines and conditionally replaces; B copies binary data from zip entry；A writes to existing or new file; B creates directories and then writes；Return type void vs String
- 修正建议: Review BCB annotation for this pair; if truly clone, train model with more varied structural clones；Alternatively, accept model prediction as correct and adjust benchmark labels

### case_id=20 FN benchmark_preference_bias

- 方法: `copy` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file using FileChannel.transferTo.
- B 摘要: Launches an Eclipse NexOpen project configuration, involving XML processing, file copying, and property setting.
- 静态失败原因: Static BERT correctly predicted non-clone due to very low token overlap (0.038) and clear syntactic/structural differences; it correctly rejected this false positive in BCB annotations.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB label likely an annotation error; the functions share no significant semantic similarity beyond basic file I/O usage, which is too broad for Type-3/4.
- 行为差异: Function A is a simple file copy; function B is a complex project launch.；Function A uses only FileChannel; function B uses multiple APIs (XML, Properties, IOUtils).；Function A has no branching or exception handling; function B has extensive error handling and conditionals.
- 修正建议: Review BCB annotations for this pair to correct potential mislabeling.；Use additional semantics-aware features beyond token overlap.

### case_id=21 FP lexical_or_api_overlap

- 方法: `run` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a resource file from classpath and sets the content to a GUI text area.
- B 摘要: Queries a REST API for tickets in a queue, parses response to get ticket IDs, and retrieves each ticket.
- 静态失败原因: Overemphasized lexical and API overlap (BufferedReader, InputStreamReader, readLine) while ignoring the fundamental semantic difference in data source and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have completely different purposes and execution contexts, despite sharing some I/O pattern.
- 共享行为: Both use BufferedReader to read lines from an InputStream；Both handle exceptions with try-catch blocks
- 行为差异: A reads a local file from classpath; B performs HTTP GET requests；A updates a GUI component; B processes REST API responses and builds a list of tickets；A is a Runnable; B returns a List<RTTicket>；Different control flow and data processing logic
- 修正建议: Include method-level context like method name and surrounding class；Use dataflow analysis to distinguish file I/O from network I/O；Incorporate code summarization or comment analysis

### case_id=22 FP lexical_or_api_overlap

- 方法: `getVersion` vs `postData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves a version string from a remote URL via HTTP GET, returning the first line or null on failure.
- B 摘要: Sends form data via HTTP POST to a specified URL, discarding the response and throwing exceptions on invalid input.
- 静态失败原因: The static BERT/GraphCodeBERT likely overemphasized the common API usage pattern (URL, URLConnection, BufferedReader, while loop) and overlooked the semantic differences in HTTP method, parameter usage, and return type. The model may have been confused by the shared code structure.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have distinct purposes (reading a version vs posting data) despite sharing HTTP connection boilerplate. BCB typically requires some functional equivalence or similar intent, which is absent here.
- 共享行为: Both use URL and URLConnection to open HTTP connections；Both read from the connection's InputStream using BufferedReader；Both close the input stream after reading；Both use a while loop to read lines from the response
- 行为差异: HTTP method: GET (a) vs POST (b)；Return value: a returns a string (version) or null; b returns void；Parameters: a has none; b has four parameters including data to post；Error handling: a catches exceptions and returns null; b throws Exception
- 修正建议: Incorporate dataflow analysis to detect write operations to output streams；Add attention to method signatures and return types；Train on more examples distinguishing read-only vs read-write HTTP operations；Use a classifier that considers the sequence of API calls and their direction

### case_id=23 FP lexical_or_api_overlap

- 方法: `getTicketsForQueue` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves open tickets from an RT queue via REST API, parses ticket IDs, and fetches each ticket.
- B 摘要: Reads and discards the content of a local URL without any processing.
- 静态失败原因: Static BERT may have focused on lexical and API-level overlaps (e.g., 'BufferedReader', 'InputStreamReader', 'URL', 'readLine') and missed the semantic disparity in what the data is used for.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labeled non-clone because the functions have entirely different high-level purposes (ticket retrieval vs. trivial URL read) and output types, despite sharing low-level I/O patterns.
- 共享行为: Both perform HTTP GET requests and read response line by line using BufferedReader.
- 行为差异: Function A has complex logic for building query parameters, parsing ticket IDs, and handling multiple exceptions; Function B simply reads and discards.；Function A returns a list of tickets; Function B returns void.；Function A uses a global base URL and session; Function B uses hardcoded local URL.；Function A processes the response to extract structured data; Function B ignores the content read.
- 修正建议: Enhance model with data flow analysis to track how read data is used (e.g., parsed vs. discarded).；Incorporate control flow and purpose-level features (e.g., return type, exception handling structure).

### case_id=24 FN benchmark_preference_bias

- 方法: `getResourceAsStream` vs `test`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Retrieves a resource as an InputStream with caching and HTTP handling.
- B 摘要: Tests the StorageStringWriter class, verifying its behavior when writing, reading, and handling exceptions.
- 静态失败原因: The static model correctly predicted non-clone because the functions have very low token overlap and are semantically unrelated. The model did not fail; rather, the BCB label is likely incorrect for this pair.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely considered both functions as involving InputStream reading and error handling, but this is an extremely weak similarity. The pair appears to be a labeling error or a result of overly broad criteria in BCB.
- 共享行为: Both involve InputStream operations.；Both handle IOException (though in different contexts).
- 行为差异: A caches resources locally; B does not.；A uses HTTP connection to fetch resources; B uses a StorageStringWriter.；A returns an InputStream; B performs assertions and does not return a value.；A has complex caching logic; B is a simple unit test.
- 修正建议: Re-evaluate BCB annotation for this pair to confirm if it is truly a clone.；Remove this pair from the clone set if it is determined to be a false positive in BCB.

### case_id=25 FN partial_functionality

- 方法: `dump` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a source file to a target file byte by byte.
- B 摘要: Reads a properties file for a specific locale, replaces or appends a key-value pair, and writes the modified content back, copying a default file if the locale file does not exist.
- 静态失败原因: Static BERT models rely on token and structural similarity; the low token Jaccard (0.168) and divergent syntactic structures (short vs long, different signatures) caused the model to miss the shared file copy pattern, as it is not sensitive to sub-function overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered this a Type-4 clone because both functions contain a core file copying subroutine (read-while-write loop), and they are both I/O utility functions, aligning with BCB's acceptance of partial functionality similarity.
- 共享行为: Both perform file I/O operations using while loops to read and write.；Both handle exceptions by catching and either ignoring or printing stack trace.；Both use buffered streams or readers for file copying.
- 行为差异: A copies raw bytes without interpretation; B processes text lines and modifies key-value pairs.；A only copies; B additionally parses and modifies content.；A uses byte streams; B uses character streams for copy and text processing.；B includes conditional file creation and more complex logic.
- 修正建议: Incorporate dataflow analysis to detect similar I/O patterns.；Use subgraph matching for sub-function similarity detection.；Augment training with partial clone examples where only part of the code matches.

### case_id=26 FN partial_functionality

- 方法: `doTransfer` vs `getHTML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request to a specified URL and returns the response to the original servlet response.
- B 摘要: Fetches a web page from a URL and returns its HTML content as a string, optionally saving to a file.
- 静态失败原因: Low token Jaccard (0.198) and different method names/structures led the model to predict non-clone; it failed to capture the high-level functional similarity of fetching and reading HTTP response.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both perform an HTTP GET-like operation and process the response, which is a core common functionality. The additional proxy logic in A is seen as extension rather than different purpose.
- 共享行为: Both create an HttpURLConnection to a URL；Both read the response content from the connection；Both handle IOException
- 行为差异: A copies request headers and body from the original request; B only sets User-Agent；A supports different HTTP methods via parameter; B only does GET implicitly；A sets response content type and encoding and writes to output stream; B returns string and optionally writes to file；A uses streams and debug prints; B uses BufferedReader and StringBuilder
- 修正建议: Enhance model with dataflow or control flow analysis to identify core I/O operations；Use code summarization or functional grouping to recognize common subtasks；Incorporate training with more Type-4 clones that share partial functionality

### case_id=27 FN partial_functionality

- 方法: `clonarFichero` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copy a file from an input stream to a destination path using FileChannel transferTo and return success status.
- B 摘要: Configure and launch a NexOpen project by processing Maven POM files, setting properties, creating reverse engineering files, and scheduling an install action.
- 静态失败原因: Static BERT models rely heavily on token overlap and structural similarity, which is very low (Jaccard 0.0498). The model correctly detected no lexical or syntactic clone, but missed the partial functional similarity in file I/O that BCB annotators might have considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as Type-4 clones because both perform file creation/copy operations from an input stream, even though B's file operation is a small part of a larger, functionally different task. The broad definition of Type-4 (similar output behavior) might capture the shared file-copying aspect.
- 共享行为: Both involve file I/O operations (reading and writing files).；Both use try-catch blocks for exception handling.
- 行为差异: A is a simple file copy; B is a complex multi-step configuration with project-specific logic.；A returns a boolean; B returns void.；B uses Eclipse APIs, XML parsing, and property manipulation; A uses basic Java file channels.；B has conditional checks for project type and file existence; A only copies if possible.
- 修正建议: Use data-flow analysis to identify common sub-tasks like file copying.；Incorporate contrastive learning with positive pairs from broad BCB annotations.；Add domain-aware features for Eclipse/IDE operations.；Use graph-based models that capture long-range dependencies and abstract behavior.

### case_id=28 FN partial_functionality

- 方法: `readGeoParserResult` vs `retrieveQ`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses geographic record by building and sending an XML request to a geoserver, then extracts place names and optional gazetteer IDs from the response.
- B 摘要: Retrieves the entire content of a URL as a string by opening a connection and reading lines.
- 静态失败原因: Static BERT models rely heavily on token overlap and method-level semantics. The low Jaccard similarity (0.125) and different method names led the model to miss the shared URL reading substructure. The model likely focused on the high-level differences (XML, collections vs string) and ignored the common loop pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often annotates as clones methods that share a core I/O pattern (open URL, read lines, build string) even if the rest of the logic differs. The structural similarity in the URL reading loop outweighs the surrounding differences.
- 共享行为: Both open a URL and read from it line by line using a BufferedReader；Both accumulate lines into a string buffer (StringBuffer or StringBuilder)
- 行为差异: A builds an XML request, parses XML response, and returns structured data (Collection of tuples); B returns raw string；A includes retry logic and error handling; B throws exceptions；A has a testing mode that returns hardcoded data；B prints the HTTP response message to stderr
- 修正建议: Incorporate more fine-grained structural awareness (e.g., dataflow or control-flow graphs) to capture shared I/O patterns；Use contrastive learning to emphasize small but semantically important code fragments；Improve handling of long-range dependencies to connect the reading loop even when surrounding code differs

### case_id=29 FN partial_functionality

- 方法: `runInternal` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads and parses an OPDS catalog from a URL, handling pagination and partial loading, and downloads books if not a catalog.
- B 摘要: Checks for a new software version by reading a remote version file and comparing build numbers.
- 静态失败原因: Low token overlap (Jaccard=0.116) and different domain-specific APIs (Android vs jEdit) led the static model to focus on surface form; it missed the abstract common pattern of 'fetch and parse from URL' due to lack of semantic role understanding.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers common high-level functionality (URL fetching and text parsing) as sufficient for a Type-3 or Type-4 clone, prioritizing task-level similarity over detailed implementation equivalence.
- 共享行为: Both open HTTP connections to URLs and read text data from the stream；Both parse lines from the input (one for catalog entries, one for version info)；Both handle exceptions (IOExceptions) and perform network I/O
- 行为差异: Code_a uses a do-while loop for pagination and may download book files; code_b is sequential and only reads a single file；Code_a interacts with an Android app engine and shows progress; code_b shows wait cursor and UI messages；Code_a parses Atom/OPDS XML; code_b parses simple property lines (.version, .build)；Code_a has extensive error handling and progress reporting; code_b simpler
- 修正建议: Incorporate data-flow or program dependency to capture high-level I/O and parsing operations；Use models that can abstract away specific library calls and focus on functional roles；Leverage method documentation or comments to infer intent

### case_id=30 FN partial_functionality

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or local file) to a destination file using byte-by-byte stream reading and writing.
- B 摘要: Copies a local file to another using FileChannel transferFrom for efficient bulk transfer.
- 静态失败原因: Low token overlap (0.13), different method names and APIs (URL vs FileChannel), but functional similarity missed due to reliance on surface lexical patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-3/Type-4 clones where core functionality is similar despite different APIs or source types, like copying a file/resource.
- 共享行为: Both copy data from a source to a destination file；Both handle file output streams and close resources
- 行为差异: A can read from URL or local file, B only from local file；A uses InputStream/OutputStream byte-by-byte, B uses FileChannel；A throws generic Exception, B throws IOException；B uses logging, A does not
- 修正建议: Use dataflow or control-flow analysis to capture I/O operations similarity；Consider graph-based models that abstract method names and APIs；Incorporate semantic role labeling for copy operations

### case_id=31 FP long_range_semantics

- 方法: `readData` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads and parses tokenized configuration strings to populate sets and maps for character mapping.
- B 摘要: Copies a file from source to destination using NIO FileChannel.
- 静态失败原因: Likely failed due to long-range semantics: the enormous size and complexity of code_a made it difficult for the model to capture overall functionality, leading to spurious matching on trivial patterns like exception handling.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would not label these as clones because they have completely different purposes and no functional similarity.
- 共享行为: No shared behavior
- 行为差异: Performs data parsing and initialization vs. file I/O；Complex nested tokenization loops vs. simple channel operations
- 修正建议: Use graph-based models (e.g., GNNs) that better capture control and data flow；Incorporate structural features like call graphs and data dependencies；Improve attention mechanisms to handle long sequences

### case_id=32 FP lexical_or_api_overlap

- 方法: `run` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a tile URL, downloads geoJSON, and converts it to vector tile geometry for display.
- B 摘要: Downloads a VRML file from a URL with authentication and writes it to a temporary file, updating a progress label.
- 静态失败原因: Static models like BERT may focus on token-level overlap (e.g., 'BufferedReader', 'readLine', 'URL') while missing the distinct semantic context and long-range dependencies that differentiate the functions.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label these as non-clones because despite similar boilerplate (URL reading), the core functionality and data processing are fundamentally different.
- 共享行为: Both open a URL and read lines using BufferedReader
- 行为差异: Function A includes concurrency control and caching logic; Function B does not.；Function A processes geoJSON into vector tile geometries; Function B writes raw data to a file.；Function B supports HTTP authentication and progress reporting; Function A does not.
- 修正建议: Incorporate data-flow analysis to distinguish different processing stages.；Use graph-based representations that capture control flow and API call sequences beyond surface tokens.

### case_id=33 FN partial_functionality

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using InputStream/OutputStream.
- B 摘要: Copies a file to another file using FileChannel transferTo.
- 静态失败原因: Low token overlap and different API usage (InputStream vs FileChannel) misled the model into thinking they are semantically different.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers functions that perform the same high-level task (copying data) as clones, ignoring API differences.
- 共享行为: Both copy data from a source to a destination file.；Both close open streams/channels after copying.
- 行为差异: copyResource supports URL and file sources, copyFile only file paths.；copyResource reads byte by byte, copyFile uses bulk transfer.；copyResource throws Exception, copyFile throws IOException.；copyResource is instance method, copyFile is static.
- 修正建议: Train on abstract representations of IO operations.；Incorporate dataflow or program dependence graphs.；Use contrastive learning to match functionally similar but syntactically different codes.

### case_id=34 FN partial_functionality

- 方法: `doGet` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to fetch and serve a page with permission checks, logging, and caching.
- B 摘要: Copies data from an InputStream to an OutputStream with error handling and resource cleanup.
- 静态失败原因: Static models rely on lexical and syntactic similarity; the low token overlap (0.04) and differing code structures prevent recognizing the shared stream-copying pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: None
- 共享行为: Performs I/O operations with try-catch-finally for exception handling and resource management
- 行为差异: Function A has complex logic for page retrieval, user permissions, logging, caching, and HTML output; Function B simply copies bytes.
- 修正建议: Incorporate dataflow analysis to detect stream copying patterns across different contexts.；Use API usage pattern matching (e.g., IOUtils.copyLarge) to identify common sub-tasks.

### case_id=35 FN benchmark_preference_bias

- 方法: `runDynusT` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies DynusT executable and model files to a temp directory and runs the DynusT.exe simulation with a timeout, optionally deleting executables after completion.
- B 摘要: Configures a NexOpen Eclipse project by validating Maven POM files, setting Hibernate dialect properties, and performing a reverse engineering setup before launching an installation job.
- 静态失败原因: The static model correctly predicted non-clone (score 0) due to very low token Jaccard and no shared structure or functionality; the failure is actually a false negative in BCB's ground truth, not model error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: This appears to be a misannotation in the BCB dataset; the functions share no meaningful similarity in purpose or implementation, so BCB likely labeled them as clones by error.
- 共享行为: Both involve file operations (copying or creating files) and logging.
- 行为差异: Function A runs an external simulation executable; Function B configures and launches an Eclipse plugin project.；Function A deals with simulation files; Function B deals with Maven POM, Hibernate, and Eclipse launch configuration.；Function A uses a timeout and exit code check; Function B uses progress monitors and persistent properties.；Function A optionally cleans up; Function B has no cleanup.
- 修正建议: Re-evaluate BCB annotation for this pair; consider relabeling as non-clone.；If dataset correction is not possible, incorporate additional validation to detect such annotation errors.

### case_id=36 FN partial_functionality

- 方法: `getEncoding` vs `load`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens a URL connection and extracts the character encoding from HTTP headers or response content.
- B 摘要: Downloads the entire content of a pastebin URL as a string.
- 静态失败原因: Static models rely on method name and token overlap; Jaccard=0.24 is low. They miss structural similarity in URL reading boilerplate and treat different purposes as non-clones.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB broad criteria accept Type-3/4 clones where two functions share similar control flow and I/O structure, even if specific tasks differ. Both functions fetch data from a URL using BufferedReader, making them functionally related.
- 共享行为: Open a URL connection using URLConnection；Read input via BufferedReader wrapping InputStreamReader；Read lines in a loop until null；Handle IOException
- 行为差异: A inspects HTTP headers for content-type and charset; B does not；A looks for encoding patterns, B concatenates all lines unchanged；A returns a single encoding string or default; B returns full XML content；B shows an error dialog on IOException; A does not
- 修正建议: Use dataflow analysis to detect URL connection and read pattern；Employ structure-aware embeddings that capture I/O patterns；Include functional role (e.g., 'data fetching') in representation

### case_id=37 FN long_range_semantics

- 方法: `copyResource` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using byte-by-byte stream copying.
- B 摘要: Copies a source file to a destination file using NIO FileChannel transfer with robust resource management.
- 静态失败原因: Low token overlap (0.12963) and different API usage (FileChannel vs. InputStream) cause the static model to miss semantic similarity; it relies on lexical and structural patterns that differ significantly.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as a Type-3 clone because both functions implement the core functionality of copying a source to a destination file, despite differences in source handling and implementation details.
- 共享行为: Both copy the entire content from a source to a destination file.
- 行为差异: Source type: A handles URL or file, B only file paths.；Copying method: A uses InputStream.read() byte-by-byte, B uses FileChannel.transferTo() for efficient transfer.；Error handling: A has simple sequential close, B uses nested try-finally blocks for guaranteed cleanup.；Method signature: A is private with implicit parameters, B is public static with explicit parameters.
- 修正建议: Incorporate data flow analysis to trace read/write operations as copying.；Use abstract syntax tree (AST) or graph-based models to capture high-level intent.；Enhance training data with diverse implementations of the same functionality.

### case_id=38 FN benchmark_preference_bias

- 方法: `extractResourceToFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Extracts a resource from classpath and copies it to a file using IOUtils.
- B 摘要: Builds a site for editing by reading XML, transforming, and writing multiple output files.
- 静态失败原因: The static BERT model likely relied on low token overlap and distinct method names, missing the broad resource-copying pattern that BCB considers a clone under Type-4 criteria.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered the common pattern of opening an input stream, copying to an output stream, and cleaning up resources as a partial functionality similarity, despite the vast difference in overall purpose and complexity.
- 共享行为: Both perform file I/O with input streams and output streams.；Both use try-finally blocks for resource cleanup.
- 行为差异: Function A is a simple one-shot resource copy; B is a multi-step site generator with loops and transformations.；Function A uses getClass().getResourceAsStream; B uses FileInputStream and custom file system.；Function A uses IOUtils.copy; B uses custom readfilestr and string manipulation.；B has many parameters and debugging statements; A has none.
- 修正建议: Train with more weight on structural/flow similarity beyond tokens.；Incorporate intermediate representation like dataflow graphs to capture common I/O patterns.

### case_id=39 FP partial_functionality

- 方法: `run` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads a tile from a URL (file or http), reads JSON, parses into vector tile geometries, and adds to a data loader after synchronization.
- B 摘要: Opens a hardcoded local URL, reads lines and discards them, catching exceptions without action.
- 静态失败原因: Static BERT/GraphCodeBERT models may rely too much on lexical and API token overlap (e.g., URL, BufferedReader, readLine) and method name 'run', failing to capture the vastly different semantic intents and data flows.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would likely label this as non-clone because the overall functionality is entirely different despite shared boilerplate code for URL reading. The partial similarity is insufficient for clone detection.
- 共享行为: Both use java.net.URL to open a connection；Both read lines via BufferedReader；Both have try-catch for MalformedURLException and IOException
- 行为差异: A supports multiple protocols and uses synchronization to avoid duplicate requests; B uses only HTTP and no synchronization；A parses the response into complex geometric structures and adds to collections; B discards all data；A has additional error handling for file not found; B has empty catch blocks；A performs significant post-processing; B no post-processing
- 修正建议: Incorporate dataflow analysis to distinguish actual usage of read data；Use contrastive learning with functional similarity labels；Augment training data with negative pairs that share boilerplate but differ in behavior

### case_id=40 FP other

- 方法: `readData` vs `extractZipFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads configuration from string constants and a file, populating multiple data structures.
- B 摘要: Extracts a zip archive to the file system, handling directories and files.
- 静态失败原因: Likely due to common structural patterns (loops, conditionals) and generic API tokens (String, File, IOException) misleading the model into false similarity detection.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would label non-clone because the functions are semantically unrelated; even the broad Type-4 category requires partial functional similarity, which is absent.
- 共享行为: Both involve reading input data (strings vs zip entries)
- 行为差异: A parses static string fields and a configuration file; B decompresses a zip.；A populates hash sets and a hash map; B writes file output streams.；A uses StringTokenizer; B uses ZipInputStream and FileOutputStream.
- 修正建议: Incorporate more discriminative features like method names, API call sequences, or data flow analysis.；Fine-tune on pairs with low token overlap but diverse functionality to reduce bias.

### case_id=41 FP boilerplate_overlap

- 方法: `getNetworkServersIPs` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Connects to a server list URL, reads lines, and extracts IP addresses from lines after the '!SERVERS' marker.
- B 摘要: Connects to Google Images, downloads HTML, parses image URLs, and updates UI components with the first image.
- 静态失败原因: GraphCodeBERT likely over-relied on syntactic similarities like URL, URLConnection, BufferedReader patterns, and common exception handling, overlooking the completely different loop logic and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates as non-clone because the functions serve entirely different purposes (server IP extraction vs. image search with UI updates) and share only boilerplate HTTP reading code.
- 共享行为: Both open a URL connection and read from an InputStream using BufferedReader.；Both catch MalformedURLException and IOException (though B catches generic Exception).
- 行为差异: A returns a Vector of IPs; B is void and updates UI.；A processes line-by-line with a state flag; B reads entire response and splits with regex.；A extracts substrings after ':' in specific lines; B extracts image URLs from HTML.；B modifies global state (googleImages, MusicBoxView components) and displays an image.
- 修正建议: Incorporate data flow analysis to distinguish variable usage and output types.；Train on more diverse negative pairs with high API overlap to penalize boilerplate matching.；Use contrastive learning with hard negatives that share structure but differ in semantics.

### case_id=42 FN benchmark_preference_bias

- 方法: `main` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.1`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Compresses a file using GZIPOutputStream with error handling.
- B 摘要: Launches an Eclipse configuration for a NexOpen project, handling Maven pom files and Hibernate properties.
- 静态失败原因: The static BERT model likely captured the low token overlap and fundamentally different syntactic and structural patterns, correctly identifying them as non-clones; but BCB's annotation favors a higher-level behavioral abstraction that the model did not learn.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone under broad Type-4 or partial functionality similarity, possibly because both functions act as entry points performing a sequence of operations with error handling and resource management, even though their specific domains and logic are completely different.
- 共享行为: Both perform file I/O operations；Both include exception handling try-catch blocks；Both check for existence of resources
- 行为差异: A works on a single file via command line; B works on Eclipse project configurations；A uses GZIP compression; B uses XML parsing and property manipulation；A has simple linear flow; B has complex nested callbacks and state management；A has no external dependencies beyond Java IO; B depends on Eclipse frameworks and custom APIs
- 修正建议: Train the model with examples of broad Type-4 clones that share high-level control flow patterns but differ in implementation；Incorporate domain knowledge or functional role information (e.g., 'main/launch method')；Use ensemble of structural and semantic features that capture overall program goal

### case_id=43 FP boilerplate_overlap

- 方法: `readZoneIDs` vs `startScript`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads zone IDs from a classpath resource file, parses each line as an integer, returns a set of integers.
- B 摘要: Reads a script from a URL and appends its lines to a dialog object's script field, with error handling that exits the program.
- 静态失败原因: The static model likely overemphasized the structural similarity of the boilerplate reading-loop pattern and the try-catch block, while missing the semantic differences in data usage (parsing integers vs. appending strings) and the divergent side effects (returning a set vs. modifying dialog state).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers these non-clones because the overall functionality is distinct: one extracts numeric zone IDs for processing, the other loads a script for execution in a dialog context. The similarity in I/O patterns is overshadowed by the different purposes and outputs.
- 共享行为: Both open an input stream from a URL/resource；Both read lines in a loop；Both use try-catch for exception handling
- 行为差异: Function A returns a HashSet<Integer>; function B modifies dialog.script and does not return a value；Function A reads from a classpath resource; function B reads from a URL specified as an attribute；Function A parses each line as an integer; function B concatenates lines as strings；Error handling: A prints stack trace and continues; B prints error message and exits
- 修正建议: Incorporate data flow analysis to track how read lines are used or transformed；Add attention to method signatures and return types to distinguish different intents；Train on more diverse examples where similar boilerplate code leads to different functional behavior

### case_id=44 FP boilerplate_overlap

- 方法: `scrapeForIsbns` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Scrapes ISBN numbers from a URL by reading lines and matching a regex pattern.
- B 摘要: Downloads an RDF model from a URL using an HTTP connection.
- 静态失败原因: The static method might have overemphasized common structural patterns (URL opening, try-catch, stream reading) and ignored the semantic differences in core logic (regex matching vs model reading).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clones because the functions have entirely different purposes and outputs, despite sharing some boilerplate URL reading code.
- 共享行为: Both open a URL connection to read data；Both handle IOException
- 行为差异: A uses retries with sleep on ConnectException, B does not retry；A parses lines with regex, B reads directly into a model；A returns count of matches, B returns a Model object
- 修正建议: Incorporate more semantic features like method names, variable types, and output types；Use dataflow analysis to capture differences in data processing

### case_id=45 FN benchmark_preference_bias

- 方法: `DialogHelper` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Constructor that creates a JDialog with a save button to copy an image file from a URL to a local file.
- B 摘要: Servlet doGet that processes page requests, checks visibility, logs, and optionally caches responses to files.
- 静态失败原因: Static BERT model correctly predicted non-clone (0) because the token overlap is very low (0.083) and the APIs (Swing vs Servlet) are distinct. The model did not make an error; it correctly identified the lack of semantic equivalence.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: None
- 共享行为: Both involve file I/O (reading and writing files).；Both handle exceptions and user interactions (dialogs in A, HTTP responses in B).
- 行为差异: A creates a GUI dialog; B is an HTTP servlet handler.；A copies a single image file; B retrieves and renders a web page with caching.；A uses Swing components (JDialog, JButton); B uses servlet API (HttpServletRequest, HttpServletResponse).；A interacts with user via dialog for save confirmation; B uses HTTP status codes and logging.
- 修正建议: Correct the BCB label from 1 to 0 for this pair.；Improve benchmark annotation guidelines to avoid labeling completely unrelated functions as clones.

### case_id=46 FN partial_functionality

- 方法: `getHTML` vs `createDialogArea`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML content from a URL, reads line by line, optionally writes to a file, and returns the HTML string.
- B 摘要: Creates a dialog area in a SWT composite, reads a license file from the bundle, and sets the text of a browser or text widget.
- 静态失败原因: Static BERT models may rely on token similarity and structural overlap; they might have focused on the overall different method signatures and UI code, missing the shared stream-reading pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the shared pattern of reading from a stream and building a string as sufficient for a Type-3 clone, especially given similar exception handling and line-by-line reading logic, even though overall contexts differ.
- 共享行为: Both read from an input stream line by line, appending lines with "\r\n" into a string buffer.
- 行为差异: A retrieves from an HTTP URL; B reads from a resource file within the plugin bundle.；A returns a string and optionally writes to a file; B returns a composite and sets UI text.；A uses HttpURLConnection; B uses bundle.getResource.；A writes to a file if dirPath is provided; B does not write to file.
- 修正建议: Improve model to recognize common sub-patterns across different contexts.；Incorporate data flow analysis to understand that input reading is a distinct functionality.

### case_id=47 FP lexical_or_api_overlap

- 方法: `callService` vs `get`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads entire content from a constructed URL and stores as a string in an instance variable.
- B 摘要: Makes an HTTP GET request with custom headers, parses response lines to create an array of GameRecord objects, returning the array or null on failure.
- 静态失败原因: Static methods may overemphasize the overlapping lexical elements (URL, BufferedReader, readLine, IOException) while missing the significant differences in data processing, return type, and HTTP setup.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have different return types, different processing logic, and different purposes (simple fetch vs. structured API call with parsing).
- 共享行为: Both read data from a URL using BufferedReader；Both handle IOException with try-catch；Both use a while loop to read lines
- 行为差异: Function A stores result as a string; Function B parses lines into GameRecord objects；Function A is void and uses instance variable; Function B returns an array；Function B sets HTTP method and custom headers; Function A does not；Function B checks HTTP response code; Function A does not
- 修正建议: Add training examples that require distinguishing between simple URL reading and structured API calls；Incorporate dataflow analysis to track how the read data is used (string vs. object parsing)；Pay attention to return types and method signatures

### case_id=48 FP lexical_or_api_overlap

- 方法: `executeHttpGet` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Executes an HTTP GET request using Apache HttpClient and returns the entire response body parsed as a JSONObject.
- B 摘要: Executes an HTTP GET request using java.net.HttpURLConnection and returns only the first line of the response as a String.
- 静态失败原因: The model may have been misled by lexical overlaps (e.g., 'HttpGet', 'BufferedReader', 'StringBuilder') and the common pattern of reading HTTP responses, ignoring the crucial difference in reading all lines versus only the first line and the return type transformation.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers them non-clones because they have different return types, different HTTP libraries, and different levels of response processing (whole body vs first line). The functionality is not partially similar enough for a Type-3/Type-4 clone.
- 共享行为: Both perform HTTP GET requests；Both read from an InputStream using BufferedReader
- 行为差异: A reads all lines and parses JSON; B reads only the first line and returns raw string；A uses Apache HttpClient; B uses java.net.HttpURLConnection；A returns JSONObject; B returns String；A does not explicitly close resources beyond the loop; B closes reader and disconnects
- 修正建议: Better capture loop vs single read distinction；Incorporate return type and data transformation steps；Distinguish between different HTTP client libraries and their methods

### case_id=49 FP lexical_or_api_overlap

- 方法: `getVersion` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves version string from a remote URL.
- B 摘要: Loads a FrameworkFactory instance from a service provider configuration file.
- 静态失败原因: The static model likely relied on overlapping tokens like 'URL', 'BufferedReader', 'readLine', 'close', etc., and similar control flow, without understanding the semantics of the operations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considers these non-clones because they perform distinct tasks (version checking vs factory loading) with different return types and error strategies; only superficial structural similarity.
- 共享行为: Both open a URL connection；Both read lines with BufferedReader；Both handle exceptions
- 行为差异: Function A returns a String from a remote URL; Function B returns an object from a classpath resource；Function B parses lines for non-comment, non-empty; Function A simply takes the last line；Error handling differs: A returns null, B throws exception
- 修正建议: Improve model to differentiate based on return types and context；Use structure-aware embeddings that capture semantic roles

### case_id=50 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `unJarStart`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a given locale by replacing or adding a message key-value pair.
- B 摘要: Extracts files from a JAR archive that match a given entry prefix.
- 静态失败原因: Low token Jaccard (0.128) and distinct vocabulary (locale/message vs jar/entry) caused the model to miss the abstract structural pattern, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a clone due to the shared generic file-processing structure (read, iterate, filter, write) despite different domains, under broad Type-4 functional similarity.
- 共享行为: Read from a resource (properties file or JAR) using streams；Iterate over entries/lines, conditionally process based on string matching；Write output to file(s)；Handle exceptions by printing stack trace
- 行为差异: Different resource types: properties file vs JAR archive；Different processing: modify key-value vs extract file contents；Different output: single properties file vs multiple extracted files
- 修正建议: Enhance model with data-flow or control-flow analysis to capture I/O patterns；Use contrastive learning to group similar abstract operations across domains

### case_id=51 FP boilerplate_overlap

- 方法: `scrapeForIsbns` vs `getRequestContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Scrapes ISBN-10 patterns from a webpage with retries and counts matches.
- B 摘要: Retrieves the first line of content from a given URL.
- 静态失败原因: The static model likely overemphasized the shared structural patterns of URL opening and reading, neglecting the distinct semantics and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clones because the core functionality is entirely different despite some boilerplate overlap.
- 共享行为: Both open a URL and read input using BufferedReader.
- 行为差异: Different input types (URL vs String).；Different return types (int vs String).；Function A counts ISBN matches with retry logic; Function B returns first line without retries.；Different exception handling and connection methods (HttpURLConnection vs generic URL stream).
- 修正建议: Incorporate more training examples with varying purposes but similar infrastructure to penalize such false positives.；Use semantic-aware embeddings or program flow analysis to differentiate higher-level intents.

### case_id=52 FN partial_functionality

- 方法: `copyResource` vs `decodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file byte by byte.
- B 摘要: Decodes a Base64-encoded file and writes the decoded content to another file.
- 静态失败原因: Low lexical overlap (Jaccard 0.19697) and presence of specialized terms like 'Base64' and different method signatures likely caused the model to miss the structural I/O pattern similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers broad Type-3/4 clones where both functions perform file copying with similar control flow (open, read loop, write, close), differences in encoding or buffering are considered superficial.
- 共享行为: Open input and output streams；Read data from input and write to output；Close streams after operation；Handle potential I/O exceptions
- 行为差异: A copies raw bytes, B decodes Base64 encoding；A reads byte by byte, B uses buffered chunk reads；A throws Exception on failure, B returns boolean and prints stack trace；A supports URL or file source, B only file source
- 修正建议: Incorporate data flow analysis to detect common I/O patterns；Use AST or graph-based representations that capture structure over lexical tokens；Augment training data with more Type-3/4 clone examples with low lexical overlap

### case_id=53 FN boilerplate_overlap

- 方法: `copy` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file or directory from a source filesystem to a local destination, optionally deleting the source.
- B 摘要: Modifies or adds a key-value pair in a locale-specific properties file, creating the file if missing.
- 静态失败原因: Static BERT/GraphCodeBERT likely predicted non-clone correctly because the functions are semantically different. The model failed to match the BCB label, which itself may be an annotation bias.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might have labeled these as clones due to superficial similarities in file I/O operations (copying, reading/writing), but the overall functionality is distinct. The label likely reflects a lenient interpretation of partial functionality overlap.
- 共享行为: Both perform file I/O operations (reading/writing files, using streams).；Both handle directories and files.
- 行为差异: First function copies entire files/directories; second modifies a properties file.；First uses Hadoop filesystem; second uses local files.；First optionally deletes source; second creates file from template if not exists and then modifies content.；Second parses and edits file content line by line; first copies bytes without modification.
- 修正建议: Improve model to distinguish core functionality from boilerplate I/O.；Incorporate higher-level semantic understanding (e.g., data flow, purpose).；Use task-specific heuristics to ignore standard library patterns.

### case_id=54 FP lexical_or_api_overlap

- 方法: `readData` vs `streamContains`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.15`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated string constants to populate various sets and mappings used in Tibetan transliteration.
- B 摘要: Checks if a given string is contained in the bytes of an input stream as UTF-8, using an assertion.
- 静态失败原因: The model likely misidentified due to superficial lexical overlap (both use 'String', 'HashSet', 'IOException') or by mistakenly matching the boilerplate structure of try-catch and loops, despite drastically different semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the two functions have completely different functionality, even though both involve string processing, they solve different tasks.
- 行为差异: Function A modifies several global HashSet and Map fields, while Function B only uses local variables.；Function A reads from string constants and has complex parsing logic, whereas Function B reads from an InputStream and performs a simple substring check.；Function A has extensive error handling, while Function B throws an assertion error if the condition fails.
- 修正建议: Improve negative sampling with pairs that share API keywords but differ in intent.；Incorporate functional context or data flow analysis to distinguish setup routines from test assertions.

### case_id=55 FN boilerplate_overlap

- 方法: `addIDs` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Adds metabolite IDs and properties to a PeakListRow by fetching and parsing data from a remote metabolite database.
- B 摘要: Checks for updates by fetching and parsing a version file from a remote server.
- 静态失败原因: The model likely relied on low token-level overlap (0.16) and distinctive identifier names, missing the structural similarity of the I/O pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might consider the common boilerplate of network I/O and line parsing as sufficient for a broad Type-4 clone, despite different domain logic.
- 共享行为: Both use HTTP to fetch a text resource and parse it line by line.；Both handle IOException with logging or error messages.
- 行为差异: A constructs URLs based on input name and extracts multiple database IDs and scores; B reads fixed URL from properties and extracts version strings.；A modifies a PeakListRow object; B calls another method to show update dialog.；A returns an int score; B returns void.
- 修正建议: Train the model to recognize common I/O and parsing boilerplate as a clone pattern.；Incorporate AST-based features to capture control flow similarity.

### case_id=56 FN partial_functionality

- 方法: `copyFile` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Modifies a key-value pair in a locale-specific properties file, creating it from English if missing.
- 静态失败原因: Static model correctly predicted non-clone under strict semantics; if BCB label is considered ground truth, model failed due to reliance on token overlap and lack of understanding of high-level purpose.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone due to both being file manipulation utilities with try-catch and file streams, despite different purposes.
- 共享行为: Both perform file I/O operations and handle exceptions.
- 行为差异: A copies entire file content; B edits a specific property.；A uses NIO channels; B uses streams and readers.；A overwrites output file; B modifies existing or creates new file.
- 修正建议: Incorporate dataflow analysis to differentiate file copy vs. property editing.；Use task-oriented representation to capture intent.

### case_id=57 FN benchmark_preference_bias

- 方法: `getResourceAsStream` vs `copyFiles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Retrieves a resource as an InputStream, with caching and HTTP conditional GET support.
- B 摘要: Recursively copies files or directories from source to destination using NIO FileChannel.
- 静态失败原因: Static BERT/GraphCodeBERT likely predicted non-clone due to low token overlap (0.108) and different method signatures, missing the potential BCB bias towards general file operation similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled as clone due to both being file-handling utilities with similar boilerplate (e.g., file existence checks, stream manipulation), but this is a broad similarity that does not align with typical Type-3/Type-4 clone definitions.
- 共享行为: Both perform file I/O operations using streams/channels；Both create directories if needed；Both close resources in finally-like blocks
- 行为差异: Different primary purpose: resource loading vs file copying；A uses HTTP connection and caching; B does not；A reads byte-by-byte; B uses transferTo for bulk copy；A handles remote URLs; B handles local files
- 修正建议: Use more specific semantic labels instead of binary clone/non-clone；Improve training data to distinguish between different file operation patterns；Incorporate control-flow and data-flow analysis to capture exact behavior

### case_id=58 FN benchmark_preference_bias

- 方法: `getFile` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint address in the WSDL, and saves it to a temporary file.
- B 摘要: Reads a medical image file (ACRNEMA stream), checks for conversion requirements, adds DICOM UIDs, and writes the converted DICOM file.
- 静态失败原因: Static BERT/GraphCodeBERT predicted correctly (0) due to low token similarity and different semantic embeddings; it did not fail, but the benchmark label is inconsistent.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB annotation may be erroneous, or possibly the annotator considered generic file processing as similar, but this does not align with typical BCB semantic similarity criteria.
- 共享行为: Read from an input stream；Perform a transformation on the data；Write to an output file；Include debugging output (logging/printing)
- 行为差异: Input source: URL vs local file；Transformation: XML modification vs DICOM metadata and pixel data handling；Output format: WSDL file vs DICOM file；Domain: web services vs medical imaging
- 修正建议: Re-evaluate the BCB label for this pair as non-clone.；Ensure annotation guidelines emphasize domain and core functionality over boilerplate patterns.

### case_id=59 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `_checkLanguagesFiles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a specific message key in a locale-specific properties file, creating the file from a template if it doesn't exist.
- B 摘要: Ensures that for each language ID, two properties files (source and temp) exist, creating them and copying content if they don't exist.
- 静态失败原因: Low token overlap (0.13) and different syntactic structures; static BERT models rely on token-level patterns and may miss the high-level domain similarity. Different APIs (BufferedReader vs FileChannel) and control flow obscure the shared functionality.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones because they both handle .properties files in a localization context, sharing file I/O operations and creation logic, which aligns with lenient Type-4/partial functionality similarity.
- 共享行为: Both operate on .properties files for localization purposes.；Both check file existence and create files if missing.；Both involve writing content to files.
- 行为差异: A modifies a specific message key; B ensures existence and copies between two files per language.；A reads and rewrites an existing file line by line; B uses FileChannel for copying.；A iterates over lines of a single file; B iterates over a list of language IDs.
- 修正建议: Incorporate domain-specific features or code summarization to capture purpose.；Use AST-based or graph-based models that abstract over syntactic variations.；Train with more diverse examples of partial functional clones.

### case_id=60 FN benchmark_preference_bias

- 方法: `send` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Sends an email with various parameters like to, cc, bcc, subject, body, attachments, and headers using JavaMail.
- B 摘要: Builds a website page for editing by applying XSLT transformations to XML and writing output files.
- 静态失败原因: Static BERT/GraphCodeBERT correctly identified them as non-clones due to low token overlap and different API usage; the label 1 in BCB is likely a dataset annotation error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to superficial similarities like multiple parameters, loops, and try-catch blocks, but the actual functionality is entirely different.
- 共享行为: Both methods have long parameter lists and use loops and exception handling.
- 行为差异: One sends email, the other builds web pages.；Different libraries used: JavaMail vs. file I/O and XSLT.；Different output: email messages vs. HTML files.
- 修正建议: Correct the BCB annotation to non-clone.；Improve dataset curation to avoid such false positives.

### case_id=61 FN partial_functionality

- 方法: `init` vs `runScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Initializes a servlet by loading classes listed in a configuration file found via classpath URL enumeration.
- B 摘要: Reads a script file from the applet codebase and returns its content as a string.
- 静态失败原因: Low token overlap (0.14) and different method names/signatures cause static BERT to rely on lexical patterns, missing the abstract shared I/O loop behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as reading from a URL stream and processing the data, a common Type-3 pattern where the loop and try-catch structure are similar despite different purposes.
- 共享行为: Both open a URL stream and read data from it；Both use a while loop to read line-by-line or byte-by-byte；Both catch exceptions and log/print errors；Both operate in a Java environment with I/O handling
- 行为差异: A reads lines and loads classes via ClassLoader, B reads bytes and concatenates into a string；A iterates over multiple URLs (Enumeration), B reads a single URL；A accumulates class objects into a collection, B returns the data string；Exception handling: A prints stack trace and logs errors, B returns 'error!' string
- 修正建议: Incorporate data flow analysis to detect common stream-reading patterns；Use graph-based models that capture control flow and I/O operations；Augment training data with more diverse I/O clones

### case_id=62 FP lexical_or_api_overlap

- 方法: `import_hints` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads hints from a file or URL, parses piece data, and places them on a board with rotation.
- B 摘要: Imports biological sequences from a URL, parsing FASTA-like format into names and sequences.
- 静态失败原因: Static BERT/GraphCodeBERT likely overfocused on lexical and API-level similarities (e.g., URL, StringTokenizer, BufferedReader, IOException) and structural patterns (try-catch, loops) while missing the semantic gap in the data processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because the domain-specific operations (puzzle pieces vs. biological sequences) make them functionally different despite similar superficial I/O patterns.
- 共享行为: Both open an input stream from a URL (or file in A)；Both use StringTokenizer to parse tokens from lines；Both use try-catch blocks to handle IOExceptions；Both read lines in a loop
- 行为差异: Function A returns a boolean indicating success; function B is void and prints stack traces on errors；Function A processes puzzle piece IDs, columns, rows, and rotations; function B processes sequence names and sequences；Function A has a fixed number of iterations from the first line; function B loops until a '>' delimiter；Function A places pieces on a board object; function B stores parsed data in ArrayLists
- 修正建议: Incorporate data-flow analysis to track the types and usage of parsed data；Include domain-specific semantics by recognizing the operations on board vs. sequence lists；Use control-flow comparison to distinguish the loop conditions (fixed count vs. delimiter-based)

### case_id=63 FP lexical_or_api_overlap

- 方法: `executeHttpGet` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs an HTTP GET request and parses the response as a JSON object.
- B 摘要: Checks for software upgrades by querying a remote server, processing license and upgrade data, updating a database, and modifying UI components.
- 静态失败原因: The static model likely focused on superficial lexical overlap (both use HttpGet, HttpClient, BufferedReader, StringBuilder, and similar try-catch patterns) and the common pattern of opening a connection, reading lines, and building a string, while ignoring the vast differences in control flow, data structures, and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB's negative label indicates that even with broad acceptance of Type-3/Type-4 clones, these functions are not considered clones because they perform completely different tasks with no meaningful overlap in functionality or purpose.
- 共享行为: Both make HTTP requests；Both read response line by line using BufferedReader
- 行为差异: Function A simply returns a JSONObject; Function B has complex side effects (DB updates, UI changes)；Function A is a generic utility; Function B is specific to an upgrade process with license validation；Function B includes parsing of a custom response format (row/field splitting) and loops over multiple upgrades；Function B conditionally shows/hides UI components and displays messages
- 修正建议: Incorporate graph-based representations to capture long-range dependencies and overall control flow；Use method-level embeddings that consider the entire function body with attention to distinguish utility functions from complex business logic；Include context such as method name, class name, and surrounding code to better infer purpose

### case_id=64 FN partial_functionality

- 方法: `fileDownload` vs `retrieveTemplate`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL to a local directory with a fixed filename.
- B 摘要: Retrieves a web page content as a string with caching.
- 静态失败原因: Low token Jaccard similarity and differences in API usage and control flow; the model likely focused on surface-level structure and missed the semantic similarity of the core URL reading pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both involve reading from a URL and processing the content, sharing the 'read from URL' pattern despite differences in output and caching.
- 共享行为: Both open a URL connection and read content using BufferedReader/InputStreamReader
- 行为差异: A writes to a file, B returns a string；A uses fixed filename, B uses caching；A reads character by character, B reads line by line
- 修正建议: Train on more partial clone examples；Incorporate data flow analysis to capture shared subroutines；Use contrastive learning to distinguish similar but not identical functions

### case_id=65 FP boilerplate_overlap

- 方法: `createOutputStream` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Creates a BufferedWriter for writing to a zip file, copying entries except content.xml from input to output, then adding a new content.xml entry.
- B 摘要: Main method that parses command line arguments, reads a Prolog file, processes it to generate Java adapter classes and a serialized adapter layer.
- 静态失败原因: Static BERT may have been misled by overlapping boilerplate patterns such as common Java I/O classes (File, IOException, InputStream/OutputStream) and exception handling, even though the core functionality is unrelated.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because they serve completely different purposes despite both using I/O. BCB generally requires some level of functional equivalence or structural similarity, which is absent here.
- 共享行为: Both perform file I/O operations using java.io classes.；Both handle IOException or other exceptions with try-catch blocks.；Both involve reading and writing data streams.
- 行为差异: A manipulates zip entries and copies data between zip files; B processes Prolog source to generate Java classes and resources.；A returns a BufferedWriter; B is a void main method that prints usage or exits.；A uses ZipInputStream/ZipOutputStream, B uses custom classes like Parser, FactVisitor, ClassWriter.；A operates on two file paths; B operates on command-line arguments and generates artifacts.
- 修正建议: Incorporate dataflow or call-graph analysis to distinguish core logic from boilerplate.；Use structure-aware encoders that can capture high-level program intent beyond token sequences.；Train on more diverse negative samples with similar boilerplate but different semantics.

### case_id=66 FN partial_functionality

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using single-byte stream copy.
- B 摘要: Copies a file to a destination with buffered I/O, force overwrite handling, and proper resource cleanup.
- 静态失败原因: Low token similarity (0.289) and differences in method signatures, control flow (try-finally vs simple close), and source handling led the model to miss the underlying common copy pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB typically accepts broad Type-3/Type-4 clones where the core functionality is similar despite differences in implementation details, such as buffering, error handling, and source type.
- 共享行为: Both copy data from an input source to an output file using streams.；Both read bytes from an InputStream and write to an OutputStream.；Both close streams after copying.
- 行为差异: Source acquisition: A uses URL or File, B only File.；Buffering: A uses single-byte read/write; B uses a buffer of configurable size.；Error handling: A throws generic Exception; B throws IOException with try-finally for resource cleanup.；Additional features: B has force overwrite flag and logging; A does not.
- 修正建议: Incorporate data-flow analysis to capture the essential read-write-close pattern.；Use AST-based features that abstract away syntactic variations in error handling and buffering.；Train on more varied clone pairs that differ in source type but share core data transport.

### case_id=67 FN partial_functionality

- 方法: `main` vs `processAddByURLSubmit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a hardcoded URL and extracts its contents to the local filesystem.
- B 摘要: Fetches RDF XML data from a given URL and processes it as a DOAP description, handling errors.
- 静态失败原因: Static BERT models rely on token and structural similarity; the low token Jaccard (0.07) and different control flow (while loop vs. try-catch) lead to a correct non-clone prediction. The model fails to capture the abstract commonality of 'URL stream reading' because it is overwhelmed by the dissimilar subsequent code.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both methods share a high-level pattern of 'opening a URL and processing its input stream', even though the specific processing differs significantly. This broad functional similarity (Type-4) is sometimes accepted in BCB annotation.
- 共享行为: Both open a URL stream using url.openStream()；Both read data from the stream
- 行为差异: A reads a zip file and extracts entries to the filesystem; B reads plain text into a StringWriter and calls processSubmittedDoap；A writes extracted files to disk; B processes data in memory；A has no error handling (throws Exception); B has specific exception handling for FileNotFoundException and IOException；A is a standalone main method; B is a protected instance method in a web form page
- 修正建议: Incorporate data flow analysis to detect the common 'open stream, read, process' pattern；Use a model that considers high-level function purpose rather than exact token matches；Enhance training data with more diverse URL-processing examples to learn the abstraction

### case_id=68 FN benchmark_preference_bias

- 方法: `copyFileByNIO` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file using NIO channels.
- B 摘要: Builds a site for editing by transforming XML and writing output files.
- 静态失败原因: Static BERT likely failed to predict clone due to extremely low lexical overlap (Jaccard=0.048) and entirely different method structures and purposes.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Human annotator may have considered both as file I/O operations, but BCB typically requires deeper semantic similarity; this is likely an annotation error.
- 共享行为: Both use FileInputStream and file I/O operations
- 行为差异: Function A is a simple file copy; Function B is a complex site builder with XML transformation, multiple file reads/writes, and property handling；Function A has no loops or conditionals; Function B has extensive loops and error handling；Function A is short and generic; Function B is long and specific to a CMS platform
- 修正建议: Reevaluate human annotation for this pair；Train model to focus on high-level semantics rather than low-level lexical features

### case_id=69 FN partial_functionality

- 方法: `init` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads Java classes from controller registry files found on the classpath.
- B 摘要: Sends an HTTP POST request to a social network API and prints the response.
- 静态失败原因: Static BERT/GraphCodeBERT models often rely on surface-level representations and may miss the deeper semantic similarity of the reading-line pattern. The large difference in token similarity (0.126) and different method names/contexts led to a non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider the common pattern of reading lines from a URL-like resource and processing each line as a Type-3 clone, ignoring the different processing logic.
- 共享行为: Both read lines from an input stream using BufferedReader
- 行为差异: A loads Java classes; B sends HTTP requests；A uses logging; B uses System.out；A catches exceptions; B throws IOException；A reads from classpath resources; B reads from HTTP connection
- 修正建议: Include explicit representation of method-level patterns like 'read lines from input stream'；Use dataflow analysis to capture the common I/O structure；During training, include more diverse examples of Type-3 clones with low token overlap

### case_id=70 FP lexical_or_api_overlap

- 方法: `addDataFromURL` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads content from a URL and appends it to a text buffer.
- B 摘要: Performs upgrade check involving database queries, license validation, and UI updates.
- 静态失败原因: The model likely focused on common API patterns (URL, BufferedReader, while readLine) and missed the overall semantic difference due to lexical overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they serve entirely different purposes and have minimal functional overlap, even at a partial level.
- 共享行为: Both use URL to open a connection；Both read lines from a BufferedReader
- 行为差异: A only reads and appends text; B performs complex upgrade logic；B handles database, UI, and license validation; A does not；B involves multiple API calls and conditional branches; A is straightforward I/O
- 修正建议: Incorporate function-level context (name, comments) into representation；Use AST-based or control-flow-aware models to distinguish simple I/O from complex logic

### case_id=71 FP boilerplate_overlap

- 方法: `readData` vs `gzip`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses configuration strings and initializes various sets and maps for Tibetan transliteration.
- B 摘要: Compresses a directory into a GZIP file.
- 静态失败原因: The model might have been fooled by common boilerplate patterns (try-catch, loops) and possibly the presence of file I/O tokens, but the long length of code_a caused loss of semantic context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have no functional overlap; one is a configuration parser, the other is a file archiver.
- 行为差异: Different overall purpose: data initialization vs file compression.；Different I/O: code_a reads from strings and possibly a file; code_b writes to a GZIP file.；Different data structures: code_a builds HashSets and maps; code_b uses byte buffers and streams.
- 修正建议: Improve handling of long functions by using hierarchical or summary-based representations.；Incorporate data-flow analysis to differentiate variable and data structure usage.；Use more robust training data that includes diverse non-clone pairs with low token overlap.

### case_id=72 FN benchmark_preference_bias

- 方法: `doGet` vs `setPayload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests to retrieve and render a web page, checking visibility and caching.
- B 摘要: Appends data from a temporary file to a destination file and recursively calls itself.
- 静态失败原因: Static BERT might have focused on the low token overlap (4.9%) and correctly identified them as non-clones; the BCB label is likely a false positive.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them similar due to both involving file I/O and exception handling, though the contexts are vastly different.
- 共享行为: Both involve file operations (A uses caching, B writes to files)
- 行为差异: A is a servlet method processing HTTP requests; B is a private file copying method；A has complex logic for page retrieval, user permissions, and statistics; B is straightforward file I/O；A uses response objects and servlet specific features; B does not
- 修正建议: Improve BCB annotation consistency by requiring stronger functional similarity；Use a model that captures higher-level semantics beyond file I/O patterns

### case_id=73 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a property value in a locale-specific properties file, creating the file if missing.
- B 摘要: Copies a source file to a destination file using NIO channels.
- 静态失败原因: Static BERT models often rely on token overlap and syntactic structure. Here the token Jaccard is low (0.138), and the functions have very different lexical signatures, so the model correctly predicted non-clone. The BCB label seems inconsistent with this pair's low similarity, suggesting a possible annotation error or benchmark bias.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones because both are file manipulation functions that read from a file and write to another, albeit with different purposes. However, this is a very broad interpretation and unlikely under standard BCB guidelines.
- 共享行为: Both involve file I/O operations；Both use try-catch for exception handling；Both work with files on disk
- 行为差异: Function A reads and writes text properties, Function B performs binary copy；Function A has conditional logic to create missing file, Function B always overwrites；Function A manipulates file content line by line, Function B transfers all bytes at once；Function A uses Reader/Writer, Function B uses NIO channels
- 修正建议: Re-evaluate the BCB annotation for this pair; if it is indeed a clone, it would require a broader definition of functional similarity that includes any file I/O operation.；Consider using more fine-grained clone detection that captures specific application logic.

### case_id=74 FN lexical_or_api_overlap

- 方法: `getFile` vs `CopyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint, saves to temp directory, and returns file path.
- B 摘要: Copies a file from source path to destination path using NIO FileChannel.
- 静态失败原因: Overlap in API usage (FileChannel, FileInputStream, FileOutputStream) and file-related keywords led the model to false positive despite low token Jaccard.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as file manipulation utilities, but the core functionality differs; likely mislabeled.
- 共享行为: Both perform file I/O operations using FileChannel and FileOutputStream.
- 行为差异: A involves network download and XML manipulation; B only copies local files.；A creates temporary files and modifies content; B simply transfers bytes.；A has extensive error handling and logging; B throws generic Exception.
- 修正建议: Incorporate control-flow and data-flow analysis to differentiate network I/O from local copy.；Use code summarization to capture intent.

### case_id=75 FP boilerplate_overlap

- 方法: `main` vs `CopyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file to generate adapter classes and writes them to a JAR.
- B 摘要: Copies a file from source to destination using NIO FileChannel.
- 静态失败原因: The model likely overfitted to common boilerplate patterns like method signature, exception handling, and File usage, misleading it into predicting a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clones because they perform entirely different tasks with no shared functionality beyond basic file I/O.
- 共享行为: Both involve file operations (reading and writing files).
- 行为差异: Function A parses Prolog and generates Java adapters; Function B only copies bytes.；Function A has complex control flow with multiple I/O and reflection; Function B is a simple transfer.；Function A catches specific exceptions; Function B throws Exception.；Function A writes JAR entries; Function B writes a file directly.
- 修正建议: Enhance models to focus on method-level semantics and domain-specific API calls.；Use control flow graphs to distinguish different high-level operations.；Incorporate token-level attention to method names and unique library usage.

### case_id=76 FN benchmark_preference_bias

- 方法: `addIDs` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Fetches metabolite data from a web service and adds identifiers and molecular weight to a row.
- B 摘要: Downloads and parses an OPDS catalog, handling HTTP connections and pagination.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on code structure and token similarity; these functions have low lexical overlap and distinct control flow, so the model correctly predicted 0. The model may have failed to capture the BCB annotation preference for broad similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled it as clone due to both functions performing network I/O and parsing responses, which could be considered a similar high-level behavior (Type-4 clone). However, the detailed logic and domain-specific operations are different.
- 共享行为: Both open URL connections；Both read from input streams；Both handle HTTP responses；Both may parse HTML/XML content
- 行为差异: Function A specifically interacts with a metabolite database; Function B interacts with OPDS catalogs；Function A sets specific fields on a PeakListRow; Function B manages catalog entries and downloads books；Function A parses specific patterns for metabolite IDs; Function B parses XML/OPDS format；Function A returns an integer score; Function B returns void and uses callbacks
- 修正建议: Improve training data to better reflect BCB annotation preferences；Include more examples of partial functionality clones；Incorporate high-level semantic similarity measures beyond lexical overlap

### case_id=77 FP lexical_or_api_overlap

- 方法: `saveAttachmentBody` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Saves an email attachment's body to a file and updates the attachment metadata in the content provider.
- B 摘要: Handles GUI action events to configure external tools and settings, updating preferences and UI elements.
- 静态失败原因: The model likely overgeneralized due to presence of File and I/O related APIs in both functions, despite different contexts and little token overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would consider these non-clones because they perform completely different tasks with distinct inputs/outputs and no shared logic beyond basic Java constructs.
- 共享行为: Both involve file system operations using File objects
- 行为差异: Function A deals with email attachments and content providers; Function B handles GUI events and preferences
- 修正建议: Incorporate structural or syntactic features to distinguish function-level semantics；Use better tokenization to capture domain-specific terms

### case_id=78 FP lexical_or_api_overlap

- 方法: `getURLContent` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads and returns the entire content from a given URL as a string.
- B 摘要: Performs an upgrade check by querying a remote server, updating UI components and database records.
- 静态失败原因: The static model likely relied on lexical overlap of URL, URLConnection, BufferedReader, and while loop patterns, missing the higher-level purpose divergence.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB tends to require substantial functional similarity; the shared URL reading pattern is a common boilerplate, not sufficient for Type-3/Type-4 classification.
- 共享行为: Both open a URLConnection and read lines from the input stream using BufferedReader.
- 行为差异: Function A is a simple utility returning the URL content; Function B has extensive UI manipulation, database queries, and conditional logic for upgrade status.；Function A returns a String; Function B returns void and has multiple side effects.；Function B parses XML-like response and iterates over upgrade items, while A just concatenates lines.
- 修正建议: Enhance model with global context such as method name and surrounding code.；Incorporate data-flow or graph representations to capture functional intent.；Increase training data with similar-boilerplate but semantically different examples.

### case_id=79 FN partial_functionality

- 方法: `postRequest` vs `CheckUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends HTTP POST request with form parameters and returns full response body.
- B 摘要: Sends HTTP GET request and returns the first line of the response body.
- 静态失败原因: Static BERT models rely on lexical and structural similarity; token Jaccard is only 0.345, and the code structures differ significantly (e.g., HashMap, loop for POST processing in A vs simple GET in B). The model likely overfocused on these differences and missed the underlying semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as clones because they share the core behavior of making an HTTP request and reading the response, which is a common task. The differences in request method and data handling are considered secondary in the clone annotation guidelines.
- 共享行为: Both open a URL connection and read from an InputStream.；Both return a string containing response data.；Both use try-catch and print stack trace on exception.；Both are static methods returning String.
- 行为差异: Function A uses POST method with form encoded data; Function B uses GET with no data.；Function A reads all lines of response; Function B reads only the first line.；Function A uses URLConnection; Function B uses HttpURLConnection.；Function A handles key-value pair encoding; Function B does not.
- 修正建议: Train or fine-tune models on BCB-style annotations to recognize partial functionality clones.；Incorporate structural abstractions like control flow graphs or API call sequences (e.g., URL.openConnection, BufferedReader) to capture high-level semantics.；Use data augmentation or contrastive learning to better distinguish between essential and non-essential differences.

### case_id=80 FN partial_functionality

- 方法: `onlyFileCopy` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies the contents of a source file to a destination file using FileChannel.transferTo.
- B 摘要: Retrieves a resource from a URL, caches it locally, and returns a FileInputStream to the cached file.
- 静态失败原因: Static BERT models rely heavily on token overlap and short-range patterns. The low Jaccard similarity (0.1495) and different APIs (FileChannel vs. URLConnection, HttpURLConnection) made the model fail to recognize the high-level semantic similarity of file copying. The model likely focused on the many distinct tokens in Code B (URL, HTTP, caching) and missed the underlying I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as Type-4 (semantic) clones because both ultimately perform a file copy operation: Code A copies a file to another file, Code B copies a remote resource to a local cache file. The core functionality of copying bytes from a source to a destination is shared, albeit with different source types and additional logic.
- 共享行为: Both involve reading from a source and writing to a destination file.；Both handle exceptions and ensure streams are closed.；Both use FileInputStream and FileOutputStream (or their channels) for file I/O.
- 行为差异: Code A copies directly from file to file; Code B downloads from a URL and caches.；Code A uses FileChannel.transferTo for efficient copy; Code B uses byte-by-byte copy with Buffered streams.；Code B includes HTTP request handling, caching logic, and logging; Code A does not.；Code A is void; Code B returns an InputStream.
- 修正建议: Incorporate features that capture data flow and I/O operations, such as identifying 'source->destination copy' patterns.；Use graph-based models (e.g., CodeBERT with AST or data flow) to abstract away surface differences.；Train on examples of broad Type-3/Type-4 clones that share core behavior despite different APIs.

### case_id=81 FN partial_functionality

- 方法: `run` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Makes an HTTP GET request to a hardcoded URL and reads the response line by line without using it.
- B 摘要: Makes an HTTP POST request to a dynamic service URL, sends JSON arguments, reads and parses the response as JSON, with retry logic and exception handling.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap, which is very low (0.117). The significant structural and semantic differences (e.g., retry loops, JSON parsing, exception handling patterns) overshadow the shared I/O pattern, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers these clones because both share the core pattern of making an HTTP request and reading the response line by line. Under broad Type-3/Type-4 criteria, the additional differences in URL construction, HTTP method, serialization, and retry are seen as extensions rather than fundamental alterations of the shared I/O behavior.
- 共享行为: Both perform an HTTP request；Both read the response line by line using BufferedReader and InputStreamReader；Both catch network-related exceptions
- 行为差异: Function A uses static URL and GET method; Function B uses dynamic URL and POST method with JSON payload；Function A discards the response; Function B parses it and returns an object；Function B includes serialization, status code checking, retry logic, and service discovery；Function A has no return value; Function B returns a generic Object
- 修正建议: Enhance training data with more examples of partial functionality clones having low token overlap；Incorporate structural or semantic features capturing common I/O patterns and API usage；Use graph-based representations (e.g., CFG or data flow graphs) to identify shared control and data flow

### case_id=82 FN partial_functionality

- 方法: `copyResource` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using byte-by-byte streaming.
- B 摘要: Reads a DICOM file, parses its contents, and writes the dataset to another file using DICOM-specific libraries.
- 静态失败原因: Static BERT-based models rely heavily on token-level similarity; the very low Jaccard similarity (0.1) and lack of common code patterns caused the model to predict non-clone, missing the functional overlap that BCB captures.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB's annotation guidelines often consider broad Type-4 clones based on high-level functional similarity, such as reading from an input source and writing to an output file, even if the implementations are vastly different. Both functions achieve a similar end goal of copying/rewriting data, hence BCB likely labeled them as clones.
- 共享行为: Both read data from a source and write to a destination file.
- 行为差异: Function A handles both URL and file sources; Function B only handles file input.；Function A performs a generic byte copy; Function B does DICOM-specific parsing, reading pixel data, and encoding.；Function A uses simple InputStream/OutputStream; Function B uses DICOM-specific streams and libraries.；Function B includes console output statements; Function A does not.
- 修正建议: Incorporate structural or dataflow features to capture high-level behavior.；Train on functional similarity benchmarks with contrastive learning over abstract syntax trees or control flow graphs.；Use retrieval-based methods to identify similar high-level tasks despite different token sets.

### case_id=83 FN benchmark_preference_bias

- 方法: `doGet` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request for a portal page, retrieves page parameter, performs visibility checks, and outputs the page with caching logic.
- B 摘要: Reads a text file, applies WrapFilter and TitleCaseFilter, and writes the transformed content to another file.
- 静态失败原因: The model correctly predicted non-clone due to low token Jaccard similarity and distinct API usage; the BCB label is likely an anomaly.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotators may have considered both as broad 'processing' tasks (Type-4), or possibly misannotated due to low-level I/O overlap.
- 共享行为: Both perform input/output operations；Both involve some form of data transformation
- 行为差异: Input source: HTTP request vs file；Output destination: HTTP response vs file；Logic: page retrieval, user permissions, caching vs word wrapping and title casing；Overall domain: web application vs file processing utility
- 修正建议: Re-evaluate this pair's BCB label for possible annotation error；Include more context-specific semantic features in the model

### case_id=84 FN partial_functionality

- 方法: `doGet` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Proxies an HTTP request by forwarding it to a Fedora URL and copying the response headers and body to the original response.
- B 摘要: Downloads a KMZ file from a URL, decompresses it using ZipInputStream, and extracts all entries to the local file system.
- 静态失败原因: Static BERT models rely on token overlap and local syntax; the functions have very low token Jaccard similarity (0.12) and different APIs (servlet vs. IO streams), causing the model to predict non-clone despite a shared high-level pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators may consider these clones because both functions follow a common pattern of reading data from a URL and writing it to an output stream, representing a generic data transfer operation.
- 共享行为: Both open a URL connection, obtain an InputStream, and copy data to an OutputStream.
- 行为差异: Function A processes HTTP headers and works in a servlet context, while Function B handles ZIP decompression and writes to files.；Function A is a server-side proxy, Function B is a command-line unzip tool.
- 修正建议: Train models to recognize high-level data flow patterns, such as URL-to-stream copying, even with different surrounding context.；Use structural or flow-based features rather than just token overlap.

### case_id=85 FP boilerplate_overlap

- 方法: `readData` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses comma-separated tokens from string fields into multiple sets and maps for Tibetan transliteration data.
- B 摘要: Copies a file from source to destination using NIO FileChannel.
- 静态失败原因: The static BERT model likely misclassified due to overgeneralization of common Java idioms like try-catch, IOException, and while loops, despite low token overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions are semantically unrelated and share no common functionality.
- 行为差异: Function A performs data initialization from string tokens and file parsing; Function B performs file I/O copy.；Function A involves extensive set/map population; Function B involves channel transfer.；Function A uses StringTokenizer and while loops; Function B uses FileChannel and transferFrom.
- 修正建议: Increase sensitivity to functional semantics via contrastive learning.；Incorporate dataflow analysis to distinguish file copy from data parsing.

### case_id=86 FP lexical_or_api_overlap

- 方法: `readUNI` vs `import_hints`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads tab-separated lines from a URL and adds id and description pairs to a vector.
- B 摘要: Reads hint data from a file or URL, parses piece placements, and places them on a board.
- 静态失败原因: The static BERT model likely relied on surface-level lexical and API similarities such as URL.openStream(), reading lines, and tokenizing, while ignoring the semantic differences in the data processing and output side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the high-level functionalities differ: one is for reading descriptive annotations, the other for importing puzzle hints with board manipulation. Even though both read from a URL, the purpose and output are distinct, which BCB typically treats as non-clones.
- 共享行为: Both open a URL input stream and read lines of text.；Both parse tokenized data from each line.；Both handle IOException and close the input stream in a finally block.
- 行为差异: Function A returns void and populates a Vector; Function B returns a boolean and modifies a board.；Function A reads tab-separated fields; Function B reads space-separated fields with a header line.；Function A extracts only id and description; Function B extracts multiple numeric fields for piece placement.；Function A can only read from URL; Function B can also read from a local file.
- 修正建议: Incorporate method name and broader context (class, surrounding methods) into the representation.；Use a detector sensitive to data flow and output types (e.g., what is done with parsed data).；Train with more examples of non-clone pairs that share API usage but differ in purpose.

### case_id=87 FN long_range_semantics

- 方法: `getFile` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies XML endpoint, and saves to temp directory.
- B 摘要: Recursively copies a file or directory using FileChannel with MappedByteBuffer.
- 静态失败原因: Model likely relied on low token overlap and focused on differences in method names, control flow, and XML processing, missing the core file transfer pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider file copying operations using NIO channels as semantically similar, even if sources differ or additional processing occurs.
- 共享行为: Both handle file I/O using FileChannel
- 行为差异: Source: URL vs local file；A modifies XML content, B does not；A returns String, B is void；Different exception handling and logging
- 修正建议: Incorporate graph-based dataflow analysis to capture I/O operations；Use code summaries or docstrings for high-level intent；Train on more diverse file I/O patterns to generalize across APIs

### case_id=88 FN partial_functionality

- 方法: `getDatasetsList` vs `login`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves and caches a list of dataset names from a Das2 server via HTTP GET.
- B 摘要: Authenticates user and retrieves a session ID from a LOLA server via HTTP POST.
- 静态失败原因: Static models rely on token overlap and local patterns; low Jaccard (0.1279) suggests different tokens, and the model didn't capture the high-level network I/O pattern as semantically similar due to different tasks and return types.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones due to similar control flow involving network I/O: both open a URL, read lines, and handle exceptions, indicating a broad Type-3/4 similarity.
- 共享行为: Both connect to a remote server via URL；Both read lines from a BufferedReader；Both handle IOExceptions；Both use try-catch or try-catch-finally for exception handling
- 行为差异: A uses GET request with query parameter; B uses POST with form data；A returns a List<String>; B returns a String (session ID)；A caches results; B does not；A throws RuntimeException on error; B returns empty string
- 修正建议: Improve model's ability to recognize higher-level semantic patterns like URL-based communication；Incorporate control-flow and data-flow information to detect common I/O patterns；Use contrastive learning on broader categories of functional similarity

### case_id=89 FP long_range_semantics

- 方法: `baseHash` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Computes MD5 hash of a name and password.
- B 摘要: Handles a Struts action for classifying a concept, involving session management and HTTP communication.
- 静态失败原因: The static model may have misclassified due to low lexical overlap but shared structural patterns like try-catch and method return, or the model might have been misled by the length and complexity of function B causing loss of semantic context.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely annotated as non-clone due to completely different functionality and no shared semantic goal.
- 共享行为: Both have try-catch blocks for exception handling
- 行为差异: Function A performs cryptographic hashing; Function B handles web request processing.；Function A has no I/O with external services; Function B makes HTTP requests.；Function A is short and focused; Function B is long and involves multiple business logic steps.
- 修正建议: Improve handling of long-range dependencies with attention or graph-based models.；Incorporate data flow and control flow features to distinguish different functionalities.；Use contrastive learning to better separate dissimilar pairs.

### case_id=90 FP lexical_or_api_overlap

- 方法: `PageLoader` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Constructor that reads the entire content of a URL as plain text into a string field.
- B 摘要: Static method that downloads an RDF model from a URL and returns a Model object.
- 静态失败原因: The model likely relied on lexical overlap (URL, InputStream, readLine/read, close) and ignored the different data handling and return types, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels as non-clone if functions have different high-level purposes despite sharing some API calls. Here, one loads a web page text, the other downloads a semantic web model.
- 共享行为: Both open a connection to a URL and read data from an input stream.；Both use try-catch (though A throws exception, B catches and wraps).
- 行为差异: A concatenates lines of plain text; B reads RDF data into a Model.；A stores result in an instance variable; B returns a Model object.；B sets HTTP headers for content negotiation; A does not.；B handles HTTP connections specifically; A uses generic URL.openStream().
- 修正建议: Incorporate structural information like control flow and data dependencies.；Use graph-based representations that capture the overall purpose.；Train on more diverse examples to distinguish between similar API usage patterns with different semantics.

### case_id=91 FN partial_functionality

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request for a page, retrieves page based on parameter, checks user permissions, logs, optionally caches the response to a temporary file, and outputs the page.
- B 摘要: Recursively copies a file or directory from one location to another using file I/O streams.
- 静态失败原因: The static BERT model likely focused on the overall semantic dissimilarity (HTTP vs file copy) and low token overlap (Jaccard 0.097), failing to capture the partial file I/O similarity that BCB might have considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones (Type-4) because both include file writing functionality (A writes a temporary cache file, B copies files), and both use similar stream and file API patterns, despite very different overall purposes.
- 共享行为: Both involve file I/O operations；Both include exception handling (IOException)
- 行为差异: A is a servlet doGet method handling HTTP request/response; B is a static utility for file copying；A includes user permission checks, logging, and caching logic; B performs recursive directory traversal；A writes to a file from a response buffer; B reads from and writes to files
- 修正建议: Improve detection of partial functional overlaps, such as file I/O operations embedded in larger functions；Incorporate call graph analysis to identify common library usage；Use fine-grained code similarity that weighs specific API calls (e.g., FileInputStream, FileOutputStream) when they are the key commonality

### case_id=92 FN benchmark_preference_bias

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies the endpoint, and returns the local file path.
- B 摘要: Copies a source file to a destination directory using a buffer.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on token overlap and structural similarity, which are low; it failed to recognize the high-level functional similarity in file I/O.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as file transfer utilities, thus labeling them as Type-3 or Type-4 clones despite different specifics.
- 共享行为: Both perform file I/O operations; both handle IOException.
- 行为差异: Function A involves network download, XML parsing, and endpoint modification; Function B only copies a file locally.；Function A has multiple exception types; Function B only catches IOException.；Function A uses NIO channels and temporary files; Function B uses simple stream copy.
- 修正建议: Incorporate functional role labeling from API calls; use graph representations that capture data flow and I/O patterns.

### case_id=93 FN partial_functionality

- 方法: `doTransfer` vs `postXml`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request to a specified URL, copying headers and body, and returns the response to the original servlet response.
- B 摘要: Sends an XML string via HTTP POST with SOAP headers to a specified URL and returns the response as a string.
- 静态失败原因: Static BERT/GraphCodeBERT may have focused on lexical differences (different method names, variable names, and structure) or missed the common pattern of HTTP request handling due to surface-level dissimilarities like 'doTransfer' vs 'postXml', different signatures, and different I/O handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both functions perform HTTP client operations with similar structure (open connection, set properties, write, read response), and they share partial functionality as HTTP request handlers. BCB's Type-4 clone detection often accepts such functional similarity even with implementation differences.
- 共享行为: Open HTTP connection；Set request headers；Write data to output stream；Read response from input stream
- 行为差异: doTransfer forwards entire request including headers and body dynamically; postXml sends fixed XML with specific SOAP headers；doTransfer handles both input and output streams to proxy; postXml returns response as String and does not modify original request；doTransfer uses dynamic HTTP method; postXml always POST；doTransfer includes error handling with response codes and prints debug; postXml throws RuntimeException on error
- 修正建议: Improve model's ability to recognize common patterns like HTTP request handling despite different method signatures and specific header manipulations；Use dataflow-aware models that capture the sequence of opening connection, writing, reading；Train on more diverse Type-4 clone examples from BCB

### case_id=94 FN lexical_or_api_overlap

- 方法: `doTransfer` vs `PhoneSetImpl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request to a new URL and returns the response.
- B 摘要: Reads a phone set from a URL and parses lines.
- 静态失败原因: Static models may have partial structural overlap (both use URL, BufferedReader, InputStream) leading to confusion, but the token Jaccard is low, so it should have been correctly identified as non-clone. Possibly the model overfitted to common patterns.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as clone due to both functions involving URL reading and IO operations, but they are substantially different in purpose and behavior.
- 共享行为: Both access a URL；Both read data from an input stream；Both handle IO exceptions
- 行为差异: doTransfer is a servlet method handling HTTP request/response; PhoneSetImpl is a constructor reading a file.；doTransfer writes to output stream and handles response codes; PhoneSetImpl only reads and parses lines.；doTransfer uses many HTTP-specific headers and methods; PhoneSetImpl is a simple line reader.
- 修正建议: Increase focus on control flow and data flow beyond token overlap.；Use more detailed semantic understanding of method purpose.；Consider context like method name and surrounding class.

### case_id=95 FN benchmark_preference_bias

- 方法: `doTransfer` vs `setBundleInfoName`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Forwards an HTTP request to another URL, copying headers and request body, then returning the response.
- B 摘要: Reads a configuration file from a URL line by line, parsing key=value pairs to update bundle names in a list.
- 静态失败原因: The static BERT model likely correctly identified these as non-clones due to low token Jaccard (0.15) and clear functional differences. The model did not fail; rather the BCB label may be inaccurate.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled these as clones due to shared patterns of URL usage and stream I/O, possibly considering them as Type-4 (semantic similarity) under the abstract category of 'reading data from a URL'. However, the actual functionalities are very different.
- 共享行为: Both open a URL and read data from it；Both handle IOException with try-catch；Both use InputStream or similar streams
- 行为差异: A performs full HTTP request forwarding with headers and method; B simply reads lines from URL.openStream()；A writes to HTTP response; B updates BundleInfo objects in a list；A uses HttpURLConnection with input/output streams; B uses BufferedReader on URL stream；A returns void; B returns boolean
- 修正建议: Re-evaluate BCB label for this pair; consider narrowing clone definition to exclude such structurally similar but functionally different pairs；Improve model to be robust against benchmark label noise

### case_id=96 FN benchmark_preference_bias

- 方法: `copyResource` vs `execute`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file.
- B 摘要: Reads class files, performs bytecode injection, and writes modified classes back.
- 静态失败原因: Static BERT models rely on token overlap and structural similarity; these methods have low Jaccard similarity (0.14) and different method names, leading to a non-clone prediction.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider this a clone due to the common pattern of reading input and writing output, despite different high-level purposes, as a broad Type-4 similarity.
- 共享行为: Both open an InputStream and read data.；Both write data to an OutputStream.；Both close streams after use.；Both handle I/O exceptions.
- 行为差异: A copies raw bytes; B reads and parses class files for injection.；A has simple read-write loop; B uses ClassReader/ClassWriter for bytecode manipulation.；B processes multiple resources conditionally; A handles a single resource.；B includes logging and metrics; A does not.
- 修正建议: Align model training with BCB's annotation guidelines, which may accept broad functional similarity.；Incorporate high-level semantic features like I/O patterns.；Use benchmark-specific fine-tuning to capture BCB preferences.

### case_id=97 FP lexical_or_api_overlap

- 方法: `postData` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Posts data to a URL and reads the response without processing it.
- B 摘要: Retrieves a YouTube video URL by parsing a webpage response.
- 静态失败原因: The static model likely overemphasized the lexical overlap of common Java network API patterns (URLConnection, BufferedReader, etc.) and ignored the larger semantic differences in purpose and data handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label this as non-clone because the functions perform entirely different tasks (posting data vs. extracting a URL) despite sharing boilerplate network code.
- 共享行为: Both open a URL connection and read from the input stream.
- 行为差异: Function A sends data via POST, while Function B only reads (GET-like).；Function A discards the response; Function B parses the response for specific patterns.；Function A has parameters for protocol, host, form, data; Function B uses a stored field ytUrl.
- 修正建议: Add negative examples with high API overlap but different semantics.；Train the model to focus on functional intent rather than just code structure.

### case_id=98 FN boilerplate_overlap

- 方法: `main` vs `parse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: This main method creates a RenRen API request with hardcoded parameters, sends it via POST, prints the response.
- B 摘要: This parse method reads a structured data file or URL, parses it using StreamTokenizer, and returns a DataSet object.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on lexical and token-level similarity, which is low (Jaccard=0.078). They fail to capture high-level structural or behavioral patterns like I/O reading and error handling that may indicate clone under broad definitions.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might consider this a clone due to both functions performing network I/O (reading from a URL), using similar boilerplate code (BufferedReader, try-catch, InputStreamReader), and having a similar high-level purpose of data retrieval and processing.
- 共享行为: Both involve reading from a URL or file using BufferedReader.；Both handle IOException with try-catch blocks.；Both use InputStreamReader to convert streams.
- 行为差异: Function A sends an HTTP POST request; function B only reads from a URL or file.；Function A prints output to console; function B returns a DataSet object.；Function A uses hardcoded parameters; function B uses configurable headers and types.；Function A is a simple one-off script; function B is a general-purpose parser with many configuration options.
- 修正建议: Incorporate control flow and data flow analysis to identify shared I/O patterns.；Use graph-based representations that abstract away specific parameter values and method names.；Include attention over common exception handling and stream usage patterns.

### case_id=99 FP lexical_or_api_overlap

- 方法: `PageLoader` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Constructor that reads entire content of a URL into a single string.
- B 摘要: Method that imports biological sequences from a URL by parsing FASTA-like format.
- 静态失败原因: The model likely focused on overlapping API calls like URL.openStream(), BufferedReader/InputStreamReader, readLine() etc., and missed the overall control flow and data usage differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the two functions have entirely different purposes and output structures; one is a generic page loader, the other is a sequence parser.
- 共享行为: Both open a URL stream and read text data.
- 行为差异: Function A concatenates all lines into one string; Function B parses structured sequence data with headers.；Function A has no exception handling; Function B catches multiple IO exceptions.；Function A reads until stream ready; Function B reads until certain delimiter '>'.
- 修正建议: Improve model's ability to differentiate between reading entire content versus parsing structured format.；Incorporate data-flow analysis to track how the input is processed.

### case_id=100 FP lexical_or_api_overlap

- 方法: `executePost` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- B 摘要: Performs a version check by fetching a URL, parsing version/build strings, and displaying a dialog based on comparison.
- 静态失败原因: The model likely overemphasized lexical and API-level overlaps (e.g., URL, BufferedReader, InputStream, readLine) and boilerplate I/O code, mistaking similar patterns for semantic similarity. It failed to capture the distinct high-level behavior and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because these functions have different purposes (generic HTTP POST vs. version check), different return types, and different control flow (one returns data, the other shows dialogs). Even broad similarity (type-4) is not warranted as they accomplish unrelated tasks.
- 共享行为: Both open a URL and read from it using BufferedReader.；Both handle IOException and read lines in a loop.；Both use InputStream and InputStreamReader.
- 行为差异: Function A uses HTTP POST, writes parameters; Function B uses HTTP GET via openStream() without parameters.；Function A returns the response string; Function B is void and shows GUI dialogs.；Function B has specific parsing for version/build lines and performs version comparison; Function A just concatenates all lines.；Function A uses HttpURLConnection with detailed configuration; Function B uses simpler URL.openStream().
- 修正建议: Incorporate data-flow and control-flow graphs to distinguish generic I/O from specific business logic.；Use models that capture higher-level intent, e.g., via method names and context (one is 'executePost', other 'doVersionCheck').；Add attention to return types and side effects (e.g., GUI interaction in B).

### case_id=101 FN partial_functionality

- 方法: `getWebPage` vs `testNetworkHTTP`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches entire web page content from a single URL and returns it as a string.
- B 摘要: Performs multiple HTTP GET requests to different URLs, reading and discarding the response, with logging and cleanup.
- 静态失败原因: Low token overlap and superficial differences in structure, method names, and error handling led the model to miss the core shared behavior of HTTP reading.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels any functions that perform HTTP GET and read response lines as clones due to functional similarity in network I/O, even if other details differ.
- 共享行为: Both open HTTP connections and read lines using BufferedReader.
- 行为差异: A returns concatenated content; B discards lines.；A uses URL.openStream; B uses HttpURLConnection.；A throws Error on failure; B catches IOException and prints stack trace, then disconnects.；A handles one URL; B handles multiple URLs.
- 修正建议: Include structural features that capture the presence of HTTP connection and read operations.；Use dataflow analysis to abstract over variable names and literal URLs.；Train on more examples of partial-functional clones to recognize network I/O as a shared behavior.

### case_id=102 FP partial_functionality

- 方法: `get` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP GET request with location and count headers, reads response lines, parses non-comment lines into GameRecord array, returns null on failure.
- B 摘要: Fetches a version check URL, reads lines, extracts build numbers from lines with specific prefixes, and displays error dialog on failure.
- 静态失败原因: Static models like GraphCodeBERT may over-rely on structural patterns (HTTP connection, BufferedReader loop, line parsing with if-starts) and miss semantic differences in purpose, data flow, and output types, leading to false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely annotates as non-clone because the functions have different domain purposes (game data retrieval vs version checking), different return types, different parameters, and different output behavior, despite sharing a common pattern of reading HTTP responses.
- 共享行为: Both perform HTTP GET requests to read text data line by line from a URL.；Both use BufferedReader to read lines and check line prefixes.；Both handle IOException with error output (printStackTrace or error dialog).
- 行为差异: Function A returns an array of GameRecord; Function B returns void.；Function A sets custom HTTP headers; Function B does not.；Function A parses lines not starting with '#' as data; Function B parses lines starting with '.build' and '.stablebuild'.；Function A prints response message on HTTP error; Function B shows GUI error dialog.
- 修正建议: Incorporate method signature information (return type, parameters) into the clone detection model.；Use data flow analysis to distinguish different data manipulations.；Train on more diverse examples where similar structure maps to different semantics.；Add a classifier for functional purpose or domain.

### case_id=103 FN partial_functionality

- 方法: `getFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies an XML attribute, and saves it to a local file.
- B 摘要: Copies a file from a specified offset to another file using buffered streams.
- 静态失败原因: Static BERT-based methods rely on lexical and structural token overlap, which is low (Jaccard 0.11). They fail to recognize the partial functional similarity in file I/O behavior, focusing instead on the distinct method names and overall logic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions involve file copying as a core subtask, and they share similar boilerplate for stream handling, exception handling, and file output, which fits broad Type-3/Type-4 similarity criteria.
- 共享行为: Both involve reading from a source and writing to a destination file；Both handle I/O exceptions and use buffered streams；Both perform file copying operations
- 行为差异: Code A downloads from a URL, Code B reads from a local file；Code A modifies XML after download, Code B does not；Code A uses NIO channels, Code B uses traditional byte-by-byte copy；Code A returns a file path, Code B has no return (void)
- 修正建议: Incorporate dataflow or control-flow analysis to capture shared file I/O patterns；Use partial clone detection that identifies common sub-traces；Train models on pairs with low token overlap but similar I/O sequences

### case_id=104 FN benchmark_preference_bias

- 方法: `decodeFileToFile` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Decodes a Base64-encoded file and writes the result to another file using buffered streams.
- B 摘要: Handles an HTTP GET request, retrieves a page, checks permissions, and writes the page content as HTTP response.
- 静态失败原因: Static BERT correctly predicted non-clone due to low token overlap and distinct API calls, but BCB's annotation may have been influenced by broad structural similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'read-process-write' patterns with similar structural elements (try-catch, stream operations), but the actual processing logic is entirely different; this is likely a benchmark mislabeling.
- 共享行为: Both involve reading from an input source and writing to an output destination using stream operations.
- 行为差异: Code A performs a fixed file decoding operation, while Code B handles HTTP request processing with user authentication, page retrieval, and caching.；Code A uses Base64 decoding, Code B does not.；Code A returns a boolean success flag; Code B throws exceptions and sends HTTP error codes.
- 修正建议: Improve tokenization to capture structural patterns across different APIs.；Include functional similarity metrics beyond token overlap.；Review BCB annotations for consistency.

### case_id=105 FP boilerplate_overlap

- 方法: `testTrainingBackprop` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Tests neural network training backpropagation on XOR data, verifying error threshold.
- B 摘要: Reads and parses multiple comma-separated string resources into sets and hash maps, handling a specific file format.
- 静态失败原因: The static model likely overemphasized common APIs (File, IOException, StringTokenizer) and boilerplate structure, ignoring the vast semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they have no functional similarity; one is a test method, the other is a data-loading routine.
- 共享行为: Both involve file I/O operations；Both use IOException
- 行为差异: Completely different purpose: training a neural network vs parsing configuration data；Different data structures and logic: Fann/Trainer vs StringTokenizer/HashSet；Different control flow: simple test vs complex parsing with multiple cases
- 修正建议: Incorporate more structural or semantic features (e.g., AST, dataflow)；Use a model better at distinguishing local API usage from overall purpose

### case_id=106 FN benchmark_preference_bias

- 方法: `runScript` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a script file from a URL and returns its content as a string, with error handling that returns 'error!'.
- B 摘要: Sends an XML request to a geo-parser service, reads the response, extracts place names and IDs, and returns a collection of tuples.
- 静态失败原因: Static BERT/GraphCodeBERT likely correctly predicted non-clone because the token overlap is very low (0.098) and the structural contexts differ significantly, so this is not a model failure but a benchmark annotation inconsistency.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions involving URL-based I/O, stream reading, and exception handling, considering that as a partial functional similarity under a broad Type-4 interpretation.
- 共享行为: Both open an InputStream from a URL and read data.；Both handle exceptions by catching Exception and logging or returning fallback values.
- 行为差异: Function A reads raw bytes into a string; Function B reads XML and parses it with DocumentHelper.；Function A has no XML or structured data processing; Function B processes XML, queries, and builds a complex collection.；Function A returns a simple string; Function B returns a Collection of Tuple<String, ArrayList<String>>.；Function B includes retry logic and state-dependent behavior (TESTING mode).
- 修正建议: Review BCB annotation guidelines to ensure such functionally distinct pairs are not labeled as clones.；Add a functional signature comparison or a more precise semantic equivalence criterion.；Consider removing or relabeling this pair in the benchmark if it does not meet a reasonable clone definition.

### case_id=107 FP long_range_semantics

- 方法: `testCopy_readerToOutputStream_Encoding` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Tests copying a reader to an output stream with specified encoding and verifying content equality.
- B 摘要: Reads configuration data from tokenized strings to populate several sets and maps for Tibetan transliteration processing.
- 静态失败原因: The model likely over-relied on shallow structural patterns (e.g., both methods involve streams and strings) and failed to capture the semantic mismatch, possibly due to the extreme length of method_b causing attention dilution.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels Type-3/Type-4 as clones only when there is significant functional similarity; here functions have no common purpose, so BCB correctly labels as non-clones.
- 共享行为: Both perform data transformation from one form to another (stream to byte array in A, tokens to sets/maps in B)
- 行为差异: A is a unit test with assertions; B is a private utility method.；A uses IOUtils.copy for stream copying; B uses StringTokenizer and manual parsing.；A has no error handling; B has extensive try-catch and error throws.；A is short (~10 lines); B is very long (hundreds of lines).
- 修正建议: Improve model's ability to handle long-range dependencies and disparate lengths.；Incorporate features like function length or cyclomatic complexity as discriminators.；Use pre-training with more varied data to reduce false positives from boilerplate patterns.

### case_id=108 FN partial_functionality

- 方法: `storeImage` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Stores an image from an InputStream to a file on disk, with optional resizing and return of relative path.
- B 摘要: Retrieves a resource by name, caching it locally, and returns an InputStream.
- 静态失败原因: Static BERT models rely on lexical overlap and structural similarity; low token Jaccard (0.12) and different control flow led to non-clone prediction, missing the shared file-writing subprocess.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled them as clones because both functions involve reading from an InputStream and writing to a file, sharing a subprocess of file output.
- 共享行为: Both involve file I/O using InputStream and File objects.
- 行为差异: storeImage writes to a file and returns a path string; getResourceAsStream reads from a file/network and returns an InputStream.；storeImage includes image resizing logic; getResourceAsStream includes HTTP caching logic.；storeImage uses current date for folder naming; getResourceAsStream uses a cache directory and URL-based naming.
- 修正建议: Enhance models to detect partial functionality or subgraph similarity.；Incorporate cross-function semantic matching of common I/O patterns.

### case_id=109 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by reading, replacing a message value, and writing back, with fallback to copy English file if missing.
- B 摘要: Copies a file from source to destination with validation and buffered I/O.
- 静态失败原因: Static BERT models rely on token overlap and structural AST matching; the low Jaccard similarity and different method signatures may cause it to miss the shared file copy sub-task.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as clone because function A includes a file copy step (copying English file to locale file) that is structurally similar to function B's entire operation, and both use common I/O patterns.
- 共享行为: Both perform file reading and writing using buffered streams.；Both check file existence and handle I/O exceptions.；Both copy data byte-by-byte or character-by-character from an input to an output.
- 行为差异: A modifies a properties file by parsing lines and replacing values; B copies raw bytes without parsing.；A has locale-specific file creation logic; B is a generic file copy utility.；A writes updated properties as text; B writes raw binary data.
- 修正建议: Incorporate dataflow analysis to detect sub-task similarity.；Train on examples with partial functionality overlap.；Use contrastive learning to capture non-lexical structural clones.

### case_id=110 FP long_range_semantics

- 方法: `createNew` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Creates a new file resource if allowed, handling .request and .tokens files specially.
- B 摘要: Reads configuration data from string tokens and populates multiple sets and hash tables for character classification.
- 静态失败原因: The static model may have been misled by surface-level similarities such as both containing loops, conditionals, or references to file-related classes (File, InputStream, etc.), but lacked deeper semantic understanding of the distinct business logic.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled this as non-clone because the functions have completely different purposes, I/O patterns, and data transformations, with no meaningful functional overlap.
- 共享行为: Both involve some form of data I/O (file read/write).
- 行为差异: Function A writes a file from an input stream; Function B parses tokenized strings into sets.；Function A returns a Resource object; Function B returns void and populates global data structures.；Function A has access control and logging; Function B has none.；Function A handles specific file names (.request, .tokens); Function B handles multiple character categories (vowels, consonants, etc.).
- 修正建议: Increase diversity of negative examples in training to avoid spurious correlations.；Incorporate structural or dataflow analysis to distinguish different I/O patterns.；Use larger context or function-level summarization to capture overall intent.

### case_id=111 FN benchmark_preference_bias

- 方法: `getFile` vs `saveFileData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint in the XML, and returns the file path.
- B 摘要: Saves file data by copying file channels, updating image dimensions if applicable, and deleting thumbnails.
- 静态失败原因: Low token Jaccard (0.138) and different control flow led to non-clone prediction, which aligns with strict semantics; but BCB bias for I/O patterns may have been missed.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to common use of FileChannel and file I/O patterns, which could be considered broad Type-4 similarity in a benchmark focused on API usage.
- 共享行为: Both use FileChannel for data transfer；Both involve file I/O with streams
- 行为差异: A downloads from network, B copies local files；A parses XML to modify attributes, B handles image metadata；A returns a String, B returns void
- 修正建议: Incorporate functional intent beyond API sequences；Use dataflow analysis to distinguish network vs local I/O；Adjust granularity for partial functionality clones

### case_id=112 FN benchmark_preference_bias

- 方法: `combineJs` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Combines multiple JavaScript files into a single file with optional minification.
- B 摘要: Handles HTTP GET requests to retrieve and serve a portal page.
- 静态失败原因: The static model correctly identified them as non-clones; the failure is in the BCB annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to surface-level similarities like file I/O, exception handling, and use of similar library calls (e.g., FileReader, IOUtils), despite completely different semantics.
- 共享行为: Both perform file I/O operations and handle exceptions.
- 行为差异: Different overall purpose: file combination vs. HTTP request handling.；Different inputs: list of JS nodes vs. HTTP request parameters.；Different outputs: modified HTML element vs. HTTP response.；Control flow and error handling strategies are dissimilar.
- 修正建议: Improve annotation consistency in BCB by focusing on semantic equivalence.；Consider adding functional signature analysis to avoid superficial matches.

### case_id=113 FN partial_functionality

- 方法: `run` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.2`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs HTTP GET request with basic authentication and reads the response into a string, updating a timestamp.
- B 摘要: Performs HTTP POST request to a service URL with JSON payload, reads response, deserializes JSON, and retries on timeout.
- 静态失败原因: Static BERT models rely heavily on lexical overlap and API surface similarity, which are low (Jaccard 0.173) due to different libraries (URLConnection vs HttpClient), method names, and authentication patterns, causing the model to miss the high-level semantic similarity of the HTTP response reading loop.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: Both functions implement the core pattern of making an HTTP request and reading the response line by line to build a string, which BCB may consider as a Type-4 semantic clone despite differences in method, authentication, and additional logic.
- 共享行为: Opens HTTP connection；Reads response line by line；Builds string from response；Closes input stream and reader
- 行为差异: HTTP method: GET vs POST；Authentication: Basic vs none；Error handling: catch all vs specific timeout retry；Output processing: raw string vs JSON deserialization
- 修正建议: Use data augmentation with API abstraction to capture common patterns like HTTP request-response handling；Incorporate contrastive learning with hard negatives having similar structure but different purpose；Enhance model with code summarization to understand high-level intent

### case_id=114 FP long_range_semantics

- 方法: `checkInputStream` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Compares the content of an InputStream against a byte array using assertions.
- B 摘要: Parses comma-separated string fields to populate sets and maps for Tibetan transliteration processing.
- 静态失败原因: The static BERT model likely failed due to the long length of function B, causing it to focus on local patterns like loops and HashSet usage, which superficially resemble the iteration in function A, while missing the overall semantic difference.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would not consider these clones because they perform entirely different tasks with no functional similarity.
- 共享行为: Both are private void methods that perform some data processing.
- 行为差异: Function A compares byte streams; Function B initializes static data structures from string tokens.；Function A uses I/O utilities; Function B uses StringTokenizer and HashSet.；Function A is short and generic; Function B is long and domain-specific.；Function A throws IOException; Function B catches IOException.
- 修正建议: Improve model's ability to capture long-range dependencies.；Use dataflow or call-graph features to distinguish utility functions from domain-specific initialization.

### case_id=115 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFromTo`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request, retrieves a page by parameter, checks user permissions, logs requests, renders the page, and optionally caches it to a file.
- B 摘要: Copies a file from source to destination using FileChannel, with error handling and preserving last modified timestamp.
- 静态失败原因: The static model correctly predicted non-clone (0) due to low lexical overlap and different functional contexts. The BCB label is likely an annotation error, so the model's prediction is actually correct.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider the file caching portion of doGet (writing to a temp file) as functionally similar to copyFromTo, but this is a very minor part of doGet; the overall semantics are vastly different, so labeling as clone seems incorrect even under BCB's broad criteria.
- 共享行为: Both use try-catch blocks for exception handling.；Both perform file I/O operations (A writes to a file for caching; B copies files).；Both use File and stream classes.
- 行为差异: A is a web servlet handler that processes HTTP requests; B is a utility for file copying.；A has complex logic for page retrieval, permission checks, logging, and rendering; B is straightforward file transfer.；A relies on external services (Property, Page, PortalRequest); B is self-contained.；A writes an HTML response to an HTTP response stream; B writes to a file via FileChannel.
- 修正建议: Re-evaluate BCB annotations for this pair; it may be a false clone label.；Improve training data quality to avoid such outliers.；Consider using models that capture higher-level semantics, but here the issue is the label, not the model.

### case_id=116 FN partial_functionality

- 方法: `setMembers` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses HTML from a Trac URL to extract component and priority options into class fields.
- B 摘要: Invokes a remote service via HTTP POST with JSON payload, handles retries, and returns deserialized response.
- 静态失败原因: The functions have low token overlap (0.128) and use different APIs (URL vs HttpPost), leading GraphCodeBERT to focus on surface-level differences and miss the high-level HTTP communication pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled them as clones because both involve HTTP communication and reading from a URL, considering them Type-4 clones with similar I/O patterns, even though their specific purposes differ.
- 共享行为: Both use HTTP to communicate with a remote server；Both use BufferedReader to read response lines；Both handle exceptions
- 行为差异: Function A uses GET request, Function B uses POST；Function A parses HTML, Function B uses JSON serialization/deserialization；Function A sets class fields, Function B returns Object；Function B includes retry logic, A does not
- 修正建议: Incorporate high-level semantic labels (e.g., 'HTTP request') as features；Use program analysis to identify common I/O patterns；Increase weight on control flow similarity for broad Type-4 clones

### case_id=117 FN partial_functionality

- 方法: `fileDownload` vs `callService`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads content from a given URL and writes it to a file in a specified directory.
- B 摘要: Fetches content from a constructed URL and stores it as a string in an instance variable.
- 静态失败原因: Static BERT models may focus on lexical overlap and method signatures, missing the high-level semantic similarity of URL reading due to differences in output handling and low token Jaccard.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels broad Type-4 clones where the core functionality of fetching data from a URL is the same, even if output handling differs.
- 共享行为: Both create a URL and open a connection/stream.；Both read from the input stream in a loop.；Both close the input stream.
- 行为差异: A writes to a file; B stores to a string.；A reads binary data using read(); B reads text using readLine() and appends to StringBuffer.；A uses a fixed output filename; B stores result in an instance variable.；A handles exceptions by logging; B sets answer and returns.
- 修正建议: Use models that capture abstract patterns like URL I/O.；Incorporate data flow or program dependence information.；Train with contrastive examples of URL reading tasks.

### case_id=118 FP lexical_or_api_overlap

- 方法: `run` vs `setMembers`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads vector tile data from a URL and processes it into a geometry collection for display.
- B 摘要: Parses HTML from a Trac ticket URL to populate component and priority arrays.
- 静态失败原因: The static BERT model likely overemphasized the lexical overlap in URL opening, BufferedReader usage, and exception handling, while missing the vastly different semantic purposes. It may have been fooled by the high token Jaccard similarity in those parts.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label as non-clone because the core functionality is entirely different despite shared I/O boilerplate. BCB typically requires partial functional similarity, not just common pattern of reading from a URL.
- 共享行为: Both open a URL and read from an InputStream using BufferedReader.；Both handle MalformedURLException and IOException.；Both use a while loop to read lines.；Both have try-catch blocks.
- 行为差异: A uses synchronization on a set to avoid duplicate requests; B does not.；A constructs tile and geometry objects; B parses HTML with regex.；A writes to dataSource loader; B stores into static arrays.；A handles different protocols (file and http); B only uses http.
- 修正建议: Improve model to capture data flow and control flow differences beyond API call sequences.；Incorporate structure-based features that distinguish between different post-processing logic.；Use contrastive learning to better separate functions that share boilerplate but differ in intent.

### case_id=119 FN partial_functionality

- 方法: `readRemoteFile` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a remote file from a hardcoded URL and returns its content as a string.
- B 摘要: Invokes a remote service method via HTTP POST, reads the response, and deserializes it to the expected return type, with retry logic on timeout.
- 静态失败原因: The model likely focused on syntactic differences like method name, control flow, and additional logic (retries, deserialization), missing the conceptual overlap of remote data retrieval.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels functions as clones when they share the core purpose of reading remote data and converting it to a usable format, even if the implementation and complexity differ.
- 共享行为: Both read data from a remote source over HTTP；Both use BufferedReader and InputStreamReader to read line by line；Both build a string from the response
- 行为差异: Function A reads from a static URL; B constructs URL dynamically based on invocation；Function A returns raw string; B returns deserialized object；Function B includes error handling for timeout and retries, A does not；Function B appends newlines; A concatenates lines directly
- 修正建议: Improve model's ability to recognize high-level I/O patterns regardless of surrounding boilerplate；Incorporate data flow information to trace URL opening and response reading；Add training examples that pair simple and complex variants of similar operations

### case_id=120 FP partial_functionality

- 方法: `getWebByUrl` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a web page from a URL, saves it to a local HTML file, and recursively processes links up to a depth limit.
- B 摘要: Downloads an RDF model from a URL by opening a connection and reading the input stream into a Model object.
- 静态失败原因: Static BERT may over-rely on overlapping API symbols (URL, InputStream, openConnection) and the common try-catch pattern, missing the high-level semantic differences in output and recursion.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically annotates non-clones when functions perform different tasks despite sharing low-level API usage; here the overall purpose (web page scraping vs RDF model download) is distinct.
- 共享行为: Both open a URLConnection and obtain an InputStream；Both handle IOExceptions with try-catch blocks
- 行为差异: Return type: void vs Model；Output: file writing vs in-memory model；Method signature: three parameters vs one；Recursive crawling vs single download
- 修正建议: Include method signature and type information in representation；Use data flow analysis to distinguish reading vs writing patterns；Incorporate task-level context via method name or surrounding code

### case_id=121 FP lexical_or_api_overlap

- 方法: `copy` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Recursively copies a file or directory from Hadoop FileSystem to local file system, optionally deleting the source.
- B 摘要: Handles UI action events to save various application preferences, including file paths for external tools.
- 静态失败原因: The static model likely relied on shallow lexical cues such as 'File' and exception handling, which appear in both methods, leading to a false positive despite low token overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label as non-clone because the functions have completely different functionality despite both being Java methods.
- 共享行为: Both involve file operations；Both handle exceptions
- 行为差异: A copies files; B saves preferences；A uses Hadoop FileSystem and streams; B uses JFileChooser and preferences API；A is recursive and returns boolean; B is event-driven and returns void；A checks file type (directory/file); B checks command strings
- 修正建议: Increase sensitivity to structural differences；Improve detection of dataflow and functional semantics；Use better negative sampling for diverse non-clone pairs

### case_id=122 FN library_context_missing

- 方法: `addIDs` vs `login`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `context_recovery_then_expert`；动态可解性: `low`；执行优先级: `medium`
- A 摘要: Queries a metabolomics database to add metabolite IDs and molecular weights to a peak list row.
- B 摘要: Logs into a web service by sending credentials and retrieves a session ID.
- 静态失败原因: GraphCodeBERT may have focused on lexical tokens and API calls; the low token overlap and different variable/domain names led to a non-clone prediction. The model might miss the high-level semantic similarity in network I/O and exception handling.
- 静态 case study: 该类错误缺少关键上下文或需要深层语义，纯静态方法不可靠。
- 动态 case study: 动态执行价值较低：样本可能依赖库、框架、网络、GUI、数据库或项目上下文，需要先恢复环境或 mock 依赖。
- BCB 偏好解释: BCB might label these as clones (Type-4) due to the shared pattern of performing an HTTP request, reading the response, and returning a result, though the domain-specific logic differs significantly.
- 共享行为: Both make HTTP connections using URL and BufferedReader.；Both handle IOException/Exception and return a default value on failure.；Both parse response data from the stream.
- 行为差异: A uses HTTP GET to query a public database; B uses HTTP POST with form data for authentication.；A sets multiple fields on a PeakListRow; B sets a session variable and returns a session ID.；A returns an integer score; B returns a String session ID.；A has complex parsing of metabolite identifiers; B extracts session ID from a simple line.
- 修正建议: Enhance model with data-flow analysis to recognize common API usage patterns (e.g., URL, BufferedReader).；Include task-specific representations like 'HTTP request' as a structural feature.；Use contrastive learning on diverse API patterns to improve generalization.

### case_id=123 FN partial_functionality

- 方法: `getFile` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the SOAP address endpoint in the XML, and saves it to a temporary file, returning the file path.
- B 摘要: Converts an ACRNEMA stream file to DICOM format by parsing the dataset, adding UIDs, and optionally inflating pixel data, writing the result to a destination file.
- 静态失败原因: Static BERT models rely on token overlap and structural patterns; the low lexical similarity (Jaccard 0.117) and different domain-specific terms (WSDL vs. DICOM) likely led to a correct non-clone prediction under strict semantics, but the benchmark's broader criteria expects clone detection.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to a broad interpretation of 'file processing' or 'data transformation' functionality, considering both as file converters that read, modify, and write data. This is a Type-4 semantic similarity based on high-level behavior rather than specific operations.
- 共享行为: Both perform file I/O operations (read and write files).；Both use try-catch-finally for error handling.；Both involve processing and modifying file content before writing output.
- 行为差异: Function A deals with WSDL and XML; Function B deals with DICOM medical image data.；Function A downloads from a URL; Function B reads from a local file.；Function A returns a String; Function B returns void.；Function A performs XML manipulation; Function B performs pixel data inflation and DICOM header modifications.
- 修正建议: Train on more diverse examples of semantically similar functions with low lexical overlap.；Incorporate abstract syntax tree (AST) patterns to capture common I/O and transformation structures.；Use code summarization or functionality classification to identify high-level behaviors.

### case_id=124 FN partial_functionality

- 方法: `read` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file or URL and returns a status code indicating success or error.
- B 摘要: Checks for a new version by fetching a URL, parsing version/build lines, and displaying a message to the user.
- 静态失败原因: The model likely relied on token overlap and API usage, missing the distinct high-level purposes (generic read vs. version check). The low Jaccard score (0.25) indicates limited lexical similarity, but the model may have failed to capture the semantic difference due to insufficient context.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as examples of 'reading from a URL' due to shared API usage and exception handling, possibly viewing B as a specialized version of A.
- 共享行为: Open a URL and read from an input stream；Handle IOException with error handling
- 行为差异: Function A reads entire stream via an external read method; B reads line by line and parses；Function A returns a status code; B has UI interactions and no return value；Function A also handles file paths; B only uses a fixed URL from configuration；Function A is non-static; B is static and takes a View parameter
- 修正建议: Incorporate method-level semantic information, such as method name and surrounding context.；Use a model that captures task-specific intents, not just structural patterns.；Improve representation of control flow and data dependencies.

### case_id=125 FN benchmark_preference_bias

- 方法: `main` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Main method that constructs and sends a POST request to the RenRen API with predefined parameters and prints the response.
- B 摘要: Reads from a URL or file by opening an InputStream and delegates to another read method, returning a status code.
- 静态失败原因: The model correctly predicted non-clone because token Jaccard is low (0.07) and method names/structures differ; the model did not fail but correctly identified the lack of semantic equivalence.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to superficial similarity in using URL and InputStream, but the core functionality (API call vs. generic reading) is distinct, likely a false positive in BCB annotation.
- 共享行为: Both open an InputStream from a URL and read data
- 行为差异: Function A sends a POST request while B only reads (GET-like)；A constructs multiple parameters specifically for an API, B uses the name directly；A prints the response to stdout, B returns a status int；A is a void main method, B returns an int
- 修正建议: No fix needed for the model; the BCB label may be erroneous.；If aiming to match BCB annotations, consider adding heuristic for URL/IO boilerplate similarity.

### case_id=126 FN benchmark_preference_bias

- 方法: `readFixString` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a fixed-length string from a limited input stream using IOUtils.copy and returns it as a String.
- B 摘要: Retrieves a resource as an InputStream by checking a local cache or downloading and caching it from a URL.
- 静态失败原因: The static BERT model likely learned to rely on token overlap and structural similarity, which is very low here, so it correctly predicted non-clone. The model did not fail; the BCB label is questionable.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both methods dealing with stream I/O and error handling, but this is very loose; likely a mislabel.
- 共享行为: Both involve reading data from streams；Both handle IOException by wrapping or printing stack trace
- 行为差异: A returns a String, B returns an InputStream；A reads a fixed number of bytes, B retrieves a whole resource possibly with caching；B has complex caching logic and HTTP handling, A does not；B prints debug messages, A does not
- 修正建议: Re-evaluate BCB label for this pair；Improve training data quality

### case_id=127 FN partial_functionality

- 方法: `main` vs `checkInputStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, unzips it, and extracts each entry to a file.
- B 摘要: Copies an InputStream to a ByteArrayOutputStream and asserts the bytes match an expected array.
- 静态失败原因: Static BERT models relied on token and syntax similarity, but the low Jaccard index and different method names, control flow (loop vs no loop), and API calls obscured the underlying streaming resemblance. It missed the partial functional overlap of stream copy.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels functions with similar stream copying patterns as Type-3 clones, even if the overall purpose differs. The core behavior of reading from an input stream and writing to an output stream is considered a shared functionality under their broad criteria.
- 共享行为: Both read from an InputStream；Both write to an OutputStream (FileOutputStream in A, ByteArrayOutputStream in B)；Both involve reading and writing bytes in a streaming manner
- 行为差异: A handles zip entry iteration and multiple files; B handles a single stream and byte comparison；A uses URL and protocol handling; B is a test helper that expects exact byte match；A writes to files; B writes to memory and asserts equality
- 修正建议: Incorporate API usage patterns (e.g., read, write, copy) as abstract features；Use AST-based matching with path-sensitive generalization for stream I/O；Augment training data with pairs having partial behavioral similarity

### case_id=128 FP lexical_or_api_overlap

- 方法: `readUNI` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a tab-separated file from a URL and extracts id and description fields.
- B 摘要: Searches Google Images for an album cover and extracts image URLs from the HTML response.
- 静态失败原因: Static BERT/GraphCodeBERT may have overemphasized the shared API calls (URL, openStream, while loop) and control-flow structure, ignoring distinct data transformations and output semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider this a clone because the core functionality (parsing TSV vs. web scraping images) is completely different, despite superficial similarities in URL handling and line reading.
- 共享行为: Both open a URL connection and read input line by line；Both use try-catch for exception handling and close resources in finally；Both iterate over lines to extract specific substrings
- 行为差异: Purpose: extracting structured data (TSV) vs. scraping HTML for image URLs；Output: Vector<String> of concatenated id+desc vs. adding to list of image URLs；Parsing: tab-delimited Scanner vs. regex split on href attributes；Conditional logic in function B (artist comparison) absent in A
- 修正建议: Incorporate dataflow analysis to track input-to-output transformations；Use contrastive learning with negative examples having similar API usage but different semantics；Leverage method names and comments as semantic hints

### case_id=129 FP boilerplate_overlap

- 方法: `sendRequestObjectResponse` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an XML request to a server, receives response, saves to file based on content type, and returns file path.
- B 摘要: Downloads an RDF model from a URL via HTTP and returns the model.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by common boilerplate patterns (URL connection, stream reading) and similar API calls, overlooking the overall semantic difference.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires high functional similarity. These functions have different input/output types and domain purposes, so they are likely not considered clones even under broad Type-4.
- 共享行为: Both open HTTP connections and read input streams
- 行为差异: A sends a request and writes response to file; B reads directly into a model；A handles compression and content-type-specific file naming; B only accepts RDF/XML；A returns file name; B returns Model object；A has extensive UI interaction (dialogs, browser); B just downloads
- 修正建议: Enhance training data with more diverse non-clone pairs sharing boilerplate；Use structural or data-flow features to distinguish different processing after the common part

### case_id=130 FN benchmark_preference_bias

- 方法: `readAndRewrite` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a DICOM file and rewrites it to another file with encoding.
- B 摘要: Launches a NexOpen project configuration, processing POM files and setting up Hibernate reverse engineering.
- 静态失败原因: The static model correctly identified low token overlap and different domains, predicting non-clone; it did not fail but agreed with our analysis.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this as a clone erroneously due to noise in the dataset; the functions share no meaningful similarity.
- 行为差异: One operates on DICOM medical images, the other on Eclipse project configurations.；Different input/output types and processing logic.；No common functionality or similar control flow.
- 修正建议: Re-evaluate BCB annotation for this pair; it appears to be a false positive.；Use a more reliable dataset for clone detection evaluation.

### case_id=131 FN partial_functionality

- 方法: `copyResource` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a single resource (URL or file) to a destination file using byte-by-byte streaming.
- B 摘要: Copies multiple source files to multiple destination files using NIO FileChannels, with additional deletion and SVN operations.
- 静态失败原因: Syntactic differences (stream vs. channel, loops vs. recursion, different method names) and low token overlap (0.16) caused the model to miss the shared file-copying behavior; static models are poor at capturing high-level functional semantics.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers the core file-copying functionality as sufficient semantic similarity for a clone, despite syntactic and extra behavioral differences, which fits broad Type-4 clone criteria.
- 共享行为: Both read content from a source file and write it to a destination file.
- 行为差异: Function A uses InputStream/OutputStream; Function B uses FileChannel.transferTo.；Function A handles a single source; Function B handles multiple sources and targets.；Function B has extra deletion, SVN operations, status printing, and System.exit calls.；Function A throws exceptions; Function B catches and exits.
- 修正建议: Enhance model with dataflow analysis to track file I/O operations.；Use API-level representations (e.g., sequences of file read/write calls).；Include more Type-4 training examples with diverse control flow but similar core function.

### case_id=132 FP boilerplate_overlap

- 方法: `testSimpleQuery` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Tests a JCR query by setting up nodes, executing an XPath query, and verifying the result.
- B 摘要: Main method that generates adapter classes from a Prolog file using code generation and serialization.
- 静态失败原因: The static model likely over-relied on common boilerplate patterns (try-catch, file I/O, stream handling, method structure) and ignored the distinct APIs and logic, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels them as non-clones because they have completely different functionality and no partial similarity; they are not even Type-4 (similar idea) as one is a test and the other is a generative tool.
- 共享行为: Both are Java methods with void return type.；Both involve stream operations (input/output).
- 行为差异: A is a unit test verifying query results; B is a tool entry point generating code.；A uses JCR content repository API; B uses Prolog parsing and bytecode generation.；A has assertions; B prints usage and debug output.；A writes and reads XML content; B reads Prolog files and writes JAR files.
- 修正建议: Incorporate dataflow analysis to distinguish actual operations.；Use method signatures and imports to determine domain.；Train on more diverse real-world methods to reduce sensitivity to generic patterns.

### case_id=133 FP lexical_or_api_overlap

- 方法: `getEncoding` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL connection's HTTP headers and body to detect and return the charset encoding.
- B 摘要: Constructs a Swing browser GUI, loads XML from a URL, optionally applies XSLT transformation, and displays the resulting HTML.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized token-level similarities (e.g., URL, BufferedReader, readLine) and failed to capture the distinct control flow and overall purpose, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels pairs as non-clones when the high-level functionality differs fundamentally, despite low-level API overlap. Here, the shared IO operations are incidental to completely different tasks.
- 共享行为: Both open a URL and read content using BufferedReader and InputStreamReader
- 行为差异: A focuses exclusively on encoding detection; B initializes a full GUI and processes XML/XSLT；A returns a String; B is a constructor with no return；A checks HTTP headers; B checks XML declaration and stylesheet
- 修正建议: Include training data with non-clone pairs that share API calls but differ in functionality；Incorporate structural features like method signatures and control flow graphs；Use data flow analysis to distinguish read vs. transform operations

### case_id=134 FN lexical_or_api_overlap

- 方法: `getFile` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.75`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL from a URL, modifies an XML attribute, and saves to a temporary file.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: Static BERT/GraphCodeBERT relied on low lexical overlap (token Jaccard 0.138) and missed the abstract FileChannel usage pattern; it likely did not recognize the structural similarity in I/O handling.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them clones due to both being file I/O utilities that use FileChannel, but this is a stretch given the functional mismatch; likely a BCB annotation error or very broad interpretation of file manipulation.
- 共享行为: Both use FileChannel for data transfer；Both involve file input/output operations
- 行为差异: Function A downloads from a URL, modifies XML, and manages temporary files; Function B simply copies bytes from one file to another；Function A includes error handling for multiple exception types; Function B only handles IOException
- 修正建议: Enhance model to recognize abstract API usage patterns (e.g., FileChannel) beyond lexical tokens；Incorporate data flow and control flow to identify I/O operations as similar

### case_id=135 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for new version by reading a version file from a URL and comparing build numbers.
- B 摘要: Performs a Google image search by parsing HTML to extract image URLs and displaying the first image.
- 静态失败原因: The static model likely over-relied on lexical and API-level overlap (e.g., URL, BufferedReader, while readLine loop) and failed to capture the distinct semantic purposes and data transformations. The high token-level similarity in generic I/O patterns biased the model toward a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the core functionality is entirely different (version checking vs. image search), despite sharing common I/O boilerplate. BCB annotations typically require significant functional similarity, which is absent here.
- 共享行为: Both open a URL connection；Both read input line by line with BufferedReader；Both use try-catch for exception handling；Both close the reader after reading
- 行为差异: A compares build versions to determine if a new version is available, while B parses HTML for image URLs；A shows UI messages based on version check outcome, while B updates UI with an album art image；A uses a property-based URL, B constructs a URL with query parameters and a User-Agent header；B handles spaces in the URL and replaces newlines in the response, A does not
- 修正建议: Incorporate dataflow analysis to distinguish how fetched data is used (e.g., version comparison vs. image URL extraction)；Use contrastive learning with negative samples that share boilerplate but differ in core logic；Focus on task-specific keywords and structural patterns rather than generic I/O；Enhance model with program dependence graphs to capture semantic differences in data manipulation

### case_id=136 FN partial_functionality

- 方法: `copyResource` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file by reading and writing bytes.
- B 摘要: Reads a DICOM file, parses its headers and pixel data, then writes it to another file with re-encoding.
- 静态失败原因: The static model likely predicted non-clone due to low token Jaccard (0.1) and entirely different API usage, missing the abstract I/O copying pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled them as clones based on a very high-level notion of 'copy data from input to output', ignoring domain-specific processing.
- 共享行为: Reads from an input source and writes to an output destination；Uses stream-based I/O for data transfer
- 行为差异: Function A copies raw bytes; Function B parses DICOM headers and processes pixel data；Function A handles URLs and local files; Function B only handles files and uses DICOM-specific libraries；Function A's output preserves original bytes; Function B re-encodes the DICOM dataset
- 修正建议: Train model to recognize abstract data flow patterns beyond surface-level tokens；Introduce program simplification techniques to normalize API calls into generic I/O operations

### case_id=137 FN benchmark_preference_bias

- 方法: `copyResource` vs `testCopy_readerToWriter_nullIn`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a resource (from URL or file) to a destination file using byte-by-byte streaming.
- B 摘要: Tests that IOUtils.copy throws NullPointerException when given a null Reader.
- 静态失败原因: Static BERT/GraphCodeBERT might have been misled by the low token overlap (0.105) and correctly identified them as different; however, the BCB label may be based on broader project-level or functional similarity that static models miss.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider these as clones because they both relate to the 'copy' functionality of IOUtils, possibly under a broad type-4 semantic category.
- 共享行为: Both involve I/O copy operations in the same project
- 行为差异: Function A performs actual resource copying; Function B tests exception handling for null input；Function A is a private utility; Function B is a public JUnit test；Function A reads from file/URL and writes to file; Function B uses ByteArrayOutputStream and Writer；Function A uses InputStream/OutputStream; Function B uses Reader/Writer
- 修正建议: Use functional-level similarity instead of lexical/structural overlap；Incorporate project-level context or API usage patterns；Consider test-code vs production-code separation

### case_id=138 FN partial_functionality

- 方法: `runScript` vs `PhoneSetImpl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a script file from a URL and returns its content as a string, with error handling returning 'error!'.
- B 摘要: Constructor that reads a configuration file from a URL, parses lines (skipping comments), and populates a phone set map.
- 静态失败原因: Low token overlap and differing method signatures (return type, constructor vs method) misled the model; it likely focused on lexical/syntactic differences rather than the shared I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones due to the common pattern of reading from a URL with a buffered stream and iterative processing, accepting broad Type-4 semantic similarity despite different purposes.
- 共享行为: Both open a URL stream and read data using buffered I/O；Both iterate over input (characters or lines) until end；Both use URL input stream handling
- 行为差异: A returns a concatenated string; B populates a HashMap via parseAndAdd；A reads characters; B reads lines；A has exception handling returning a default string; B throws IOException；A is a method; B is a constructor
- 修正建议: Incorporate dataflow or control-flow analysis to capture stream reading patterns；Use structural alignment on loop bodies；Add attention to constructor/method distinction but recognize similar I/O operations

### case_id=139 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `run`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a new version by reading version and build numbers from a URL and comparing with current build.
- B 摘要: Loads vector tile geometry from a URL or file, reads GeoJSON, parses it into geometries, and adds them to a data loader.
- 静态失败原因: The model may have over-relied on surface-level lexical and structural similarities (URL, BufferedReader, IOException) and missed the distinct high-level semantics, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the core functionality is entirely different: one is version checking and the other is tile loading, despite similar boilerplate IO code.
- 共享行为: Both open a URL and read lines from an input stream using BufferedReader；Both handle IOException with try-catch blocks
- 行为差异: Function A performs version comparison and displays messages; Function B processes GeoJSON into geometry objects；Function A has UI-related wait cursor calls; Function B has synchronization and geospatial processing；Function B handles multiple protocols (http, file) and has more complex error handling
- 修正建议: Include negative examples with high token overlap but different functionality；Incorporate semantic similarity measures that capture higher-level purpose beyond API usage

### case_id=140 FP boilerplate_overlap

- 方法: `eventHash` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes MD5 hash of an input string and returns Base64-encoded digest.
- B 摘要: Processes an HTTP request for classification, builds XML, sends to server, parses result, and returns an ActionForward.
- 静态失败原因: The static model likely overfitted to surface-level similarities such as try-catch blocks with printStackTrace, return statements, and method signatures with similar parameter types (String vs String, etc.), despite the Jaccard similarity being low.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have completely different purposes and no semantic overlap, which aligns with the strict Type-3/Type-4 criteria that require at least partial functional similarity.
- 共享行为: Both contain exception handling with printStackTrace；Both return a value (or null)
- 行为差异: eventHash is a simple hash utility; perform is a complex web action；perform involves session management, HTTP communication, and XML parsing; eventHash does not；perform has multiple control flow paths and side effects; eventHash is deterministic and side-effect free
- 修正建议: Improve model sensitivity to core logic versus boilerplate code；Use dataflow or control-flow features to distinguish distinct algorithmic patterns

### case_id=141 FN benchmark_preference_bias

- 方法: `getURLContent` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Fetches content from a URL and returns as string.
- B 摘要: Reads a file or string data, tokenizes, and populates sets/maps for internal lookup.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone because the semantic gap is large; it did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both functions involving reading and processing text data line by line, which is a broad Type-4 functional similarity (data extraction).
- 共享行为: Both involve reading data from an external source and processing lines.
- 行为差异: A reads from a URL connection; B reads from a file or string tokens.；A returns the entire content as a single string; B populates multiple data structures and does not return a value.；A's logic is simple while B's logic is complex with multiple token parsing and conditional branches.
- 修正建议: Re-annotate this pair as non-clone in BCB to reduce noise.；Ensure function-level semantic equivalence criteria are applied consistently.

### case_id=142 FN partial_functionality

- 方法: `httpRequestByPOST` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body string, handling errors by setting error fields and returning null.
- B 摘要: Performs an HTTP GET request to fetch a version check file, parses lines for version and build info, and displays a dialog with the result.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low token overlap (Jaccard=0.226) and different method names, APIs, and error handling patterns, missing the high-level semantic similarity of HTTP request-and-read loops.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels functions as clones if they share similar algorithmic structure (e.g., network I/O, line-by-line reading) even with different specific APIs and domains, accepting Type-3/Type-4 partial functionality similarity.
- 共享行为: Both perform an HTTP network request and read the response line by line using BufferedReader.；Both handle IOException by returning an error indicator or showing an error dialog.；Both use try-catch blocks for network I/O.
- 行为差异: Method A uses POST with URL-encoded form parameters; Method B uses GET via URL.openStream().；Method A returns the entire response string; Method B parses specific lines for version/build data.；Method A sets class fields on error; Method B shows GUI dialogs.；Method A is an instance method; Method B is static.
- 修正建议: Incorporate dataflow or control-flow graphs to capture structural similarity beyond token sequence.；Use API usage embeddings (e.g., library call patterns) to recognize common I/O patterns.；Apply contrastive learning on program semantics to learn representations invariant to surface-level differences.

### case_id=143 FN benchmark_preference_bias

- 方法: `doGet` vs `clonarFichero`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve, render, and cache a page with access control and logging.
- B 摘要: Copies a file from an input stream to a destination file using NIO channels.
- 静态失败原因: The model correctly found no lexical or structural similarity; the BCB label appears anomalous due to overbroad criteria.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as performing data reading/writing, leading to a broad Type-4 clone label despite different contexts.
- 共享行为: Both involve file I/O operations；Both use try-catch for IOException handling
- 行为差异: Different domain: web request handling vs file copy utility；Function A is complex with access control and caching; Function B is simple and standalone
- 修正建议: Re-examine this pair in the benchmark for possible mislabeling；Use domain-specific heuristics to avoid false clone annotations

### case_id=144 FP lexical_or_api_overlap

- 方法: `loadMFileViaWeb` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a MATLAB M-file from a web URL, parses it into a UserFunction object.
- B 摘要: Retrieves a version string from a URL by reading the first line of the response.
- 静态失败原因: Static BERT models may have focused on the common API sequence (URL, BufferedReader, try-catch) and lexical overlap (URL, BufferedReader, readLine, close) leading to a false positive. They may not capture the distinct return types and final processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because their high-level semantics differ: one loads and parses code, the other fetches a version string. Even though they share a similar low-level URL reading pattern, BCB considers them functionally distinct.
- 共享行为: Opens a URL and reads text via BufferedReader；Handles exceptions by logging or returning null
- 行为差异: Function A reads multiple lines and concatenates to form code, then parses into a UserFunction; Function B reads only the first line and returns it as a string.；Function A sets the parsed function's name; Function B does not parse.
- 修正建议: Train on more diverse examples to distinguish tasks despite API similarity.；Incorporate return type and final output semantics into the model.

### case_id=145 FP lexical_or_api_overlap

- 方法: `doRequest` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Handles HTTP request by resolving a resource path, setting MIME type, and copying stream to response.
- B 摘要: Reads data from string tokens to populate multiple HashSets and a map, and parses a file into tables.
- 静态失败原因: The static model likely over-relied on superficial lexical cues such as common keywords like 'IOException', 'throw', 'catch', and 'String', or API classes like HashSet and StringTokenizer appearing in code_b, leading to a false positive despite low Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically considers Type-1/2/3 clones; these functions have entirely different purposes and structures, so they are clearly non-clones under any type.
- 共享行为: Both use Java I/O (InputStream/OutputStream vs file reading).；Both can throw IOException (one throws, one catches).
- 行为差异: doRequest handles HTTP servlet request/response; readData parses static string data and a file.；doRequest returns boolean indicating success; readData is void and modifies global sets/maps.；doRequest uses HttpServletRequest, HttpServletResponse, URL, IOUtils; readData uses StringTokenizer, HashSet, HashMap, BufferedReader.；doRequest has a single resource copy; readData has complex multi-step parsing with error handling.
- 修正建议: Improve tokenization to capture structural differences (e.g., control flow, method signatures).；Use graph-based representations to model data flow and call dependencies.；Enhance training data with more negative examples that share vocabulary but differ in semantics.

### case_id=146 FN lexical_or_api_overlap

- 方法: `callService` vs `readGeoParserResult`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches a URL and stores the response as a string in an instance variable.
- B 摘要: Calls a geo-parsing web service with an XML request, parses the response, and extracts place names and IDs.
- 静态失败原因: Static BERT/GraphCodeBERT may have been misled by the low lexical overlap (0.12) and the presence of many XML-specific tokens in function B, failing to recognize the shared URL-reading pattern, as it focuses on surface token similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider these clones because both functions involve fetching data from a URL via HTTP GET and reading the response line by line, which is a common pattern, despite differences in URL construction and response parsing.
- 共享行为: Both open a URL connection and read the response line by line into a buffer.；Both handle IOExceptions.
- 行为差异: A does not construct parameters; B builds an XML request.；A does not parse the response; B parses XML and extracts specific data.；A returns nothing (void); B returns a collection.；A uses instance variable; B returns value.
- 修正建议: Improve model's ability to detect structural patterns like URL reading despite superficial differences.；Use code structural features or abstract syntax trees to capture common API usage patterns.；Enhance training with more diverse positive pairs that share partial functionality.

### case_id=147 FP lexical_or_api_overlap

- 方法: `setMembers` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses HTML from a Trac URL to extract component and priority list options and stores them in class arrays.
- B 摘要: Downloads a file from a given URL with optional authentication and writes it to a temporary file, updating a status label.
- 静态失败原因: Static BERT models may over-rely on surface-level API usage (URL, BufferedReader, InputStreamReader) and loop structure, while ignoring the semantic differences in data processing (parsing vs. file writing). The token-level similarity from common Java idioms likely misled the model into predicting a clone.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels Type-4 (unrelated) functions as non-clones. These two functions share only generic I/O boilerplate, and their core logic (parsing vs. downloading) is entirely different, so BCB correctly labels them as non-clones.
- 共享行为: Both open a URL connection；Both read lines from a BufferedReader wrapping an InputStream；Both use a while loop to process each line
- 行为差异: Function A parses HTML for specific select elements; Function B writes raw lines to a file.；Function A does not handle authentication; Function B includes basic HTTP authentication.；Function A updates class-level arrays; Function B writes to a temporary file and updates a UI label.；Function A catches exceptions and prints messages; Function B throws IOException.
- 修正建议: Incorporate data-flow analysis to distinguish between reading data for parsing vs. writing to file.；Add type information for class fields to recognize that function A updates fields while function B writes to file system.；Use graph-based models that capture semantic structure beyond sequence of API calls.

### case_id=148 FN benchmark_preference_bias

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file using FileChannel.
- B 摘要: Builds a site for editing by processing XML pages and writing output files.
- 静态失败原因: Static model correctly predicted non-clone. It likely learned that the two functions have very different token patterns, method names, and control structures.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both using FileInputStream and performing file writing, but the functionality is vastly different. Possibly an annotation error.
- 共享行为: Both involve file I/O (FileInputStream, FileOutputStream)
- 行为差异: copyFile is a simple low-level file copy; buildSiteForEdit is a high-level complex site generation with XML transformation, string manipulation, and multiple file writes.；copyFile has no loops or conditionals; buildSiteForEdit has loops, conditionals, exception handling.；copyFile uses NIO channels; buildSiteForEdit uses streams and custom FileSystem class.
- 修正建议: Review BCB annotation for this pair; likely a label error.；If BCB considers partial functionality, these do not share enough common behavior.

### case_id=149 FN benchmark_preference_bias

- 方法: `addIDs` vs `callApiPost`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Fetches metabolite data from a web service, parses HTML to extract IDs and properties, and populates a PeakListRow object, returning a score.
- B 摘要: Makes an HTTP POST request to a given API URL with parameters, sets headers, and returns the response InputStream, throwing an exception on error.
- 静态失败原因: Static BERT likely focused on syntactic structure and literal semantics, missing the high-level thematic similarity of HTTP client behavior that BCB annotators might have loosely considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as clones because they are both network communication functions that involve URL handling and stream I/O, accepting broad Type-4 similarity.
- 共享行为: Both perform HTTP requests and handle IO exceptions
- 行为差异: Different HTTP methods (GET vs POST)；Different request setup (no headers vs custom headers)；Different response handling (HTML parsing vs raw InputStream)；Different output side effects (modifying row vs returning stream)
- 修正建议: Use AST-based or flow-aware models to capture high-level semantic patterns like 'makes HTTP request'.；Incorporate domain-specific knowledge to distinguish generic network functions from specific data extraction tasks.

### case_id=150 FN benchmark_preference_bias

- 方法: `getHTML` vs `readVersion`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Fetches HTML content from a URL, optionally saves to a file, and returns the content as a string.
- B 摘要: Reads version information from a classpath resource and sets internal fields.
- 静态失败原因: The static BERT model likely focused on explicit semantic differences (e.g., return type, method signature, specific token names like 'Version=' instead of generic line appending) and judged them as non-clones. It may have missed the broader structural similarity that BCB considers, possibly due to training on stricter clone definitions or sensitivity to superficial token differences.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labels this as a clone (Type-3) because both methods exhibit a common structural pattern: opening an input stream, reading lines in a loop, processing each line, and cleaning up resources with try-catch-finally. Despite different functional outcomes, the repetitive I/O structure aligns with BCB's acceptance of partial functionality similarity.
- 共享行为: Both open a stream (HTTP connection or URL) and read lines using BufferedReader；Both use a loop to read lines until null；Both handle IOException and close resources in finally block；Both have similar exception handling (printStackTrace)
- 行为差异: Method A returns a String; method B returns void and sets class fields；Method A writes output to a file conditionally; method B does no file I/O；Method A processes all lines as raw text with newlines; method B parses specific key-value patterns；Method A uses HTTP connection with custom User-Agent and encoding; method B uses classpath resource
- 修正建议: Train with a dataset that includes BCB-style annotations emphasizing structural patterns over specific functionality；Incorporate data augmentation that creates partial functionality clones to teach models to recognize common I/O patterns；Use graph-based features to capture control flow and resource handling similarities

### case_id=151 FP long_range_semantics

- 方法: `logging` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Logs inbound message details (encoding, headers, content) and writes to a cache, handling IOException.
- B 摘要: Initializes multiple sets and hash maps by parsing comma-separated string tokens for Tibetan transliteration data.
- 静态失败原因: Static BERT likely failed due to truncation of B's long code, losing the distinctive initialization logic and only seeing generic I/O patterns which may have matched A.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels this as non-clone because the functions have completely different purposes and logic; they are not Type-3/4 clones.
- 行为差异: A handles network message logging; B initializes static data structures.；A uses InputStream and CachedOutputStream; B uses StringTokenizer and HashSet.；A involves exception throwing (Fault); B catches IOException.；A writes to logger; B populates configuration sets.
- 修正建议: Use sliding window or chunk-based encoding to preserve full context；Apply more aggressive data-flow analysis to distinguish I/O handling from data initialization

### case_id=152 FN benchmark_preference_bias

- 方法: `main` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Main method to run Weka Experiment Setup GUI, loading/saving experiment via serialization.
- B 摘要: Build a website for editing by reading XML files, applying XSLT transforms, and writing output files for each page.
- 静态失败原因: Static BERT correctly identified non-clone due to low token overlap and distinct semantics; the misclassification is due to a potential erroneous BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered the presence of file I/O and tracing as functional similarity, but these are too generic to indicate a clone.
- 共享行为: Both perform file I/O operations；Both use exception handling；Both include debug tracing/logging
- 行为差异: Different purposes: GUI experiment editor vs. static site generator；Different control flow: event-driven vs. sequential loop；Different output: object serialization vs. HTML files；Different data types and structures used
- 修正建议: Reassess the BCB label for this pair；Consider excluding pairs with very low token similarity from BCB annotations；Use additional structural analysis to confirm non-clone status

### case_id=153 FN partial_functionality

- 方法: `main` vs `gzip`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts entries from a zip file downloaded via URL and writes them to disk.
- B 摘要: Compresses a directory into a gzip file.
- 静态失败原因: The model likely relied on high lexical overlap (stream handling, buffer usage, file I/O) and missed the semantic difference between compression and decompression, as well as the different data sources (URL vs file system).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB sometimes labels clones based on shared algorithmic structure or domain, even if direction differs; both involve compression/decompression with similar I/O boilerplate.
- 共享行为: Both use buffered I/O to copy data from an input stream to an output stream.；Both use byte arrays and loops to read/write chunks.；Both handle compression/decompression related streams (ZipInputStream vs GZIPOutputStream).
- 行为差异: Function a decompresses (reads a zip archive) while function b compresses (writes a gzip archive).；Function a reads from a URL and processes multiple entries, function b reads from a local directory and produces a single file.；Function a uses ZipInputStream with ZipEntry iteration, function b uses GZIPOutputStream directly.；Function a writes to new files per entry, function b writes to a single gzip file.
- 修正建议: Incorporate directionality analysis (compression vs decompression).；Distinguish between single-entry and multi-entry archive processing.；Use data-flow analysis to track stream types (ZipInputStream vs GZIPOutputStream).

### case_id=154 FP boilerplate_overlap

- 方法: `getUser` vs `getEncoding`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a User from a database or config file based on a login string.
- B 摘要: Extracts the character encoding from an HTTP response or URL content.
- 静态失败原因: Static BERT likely focused on superficial structural patterns common to many I/O operations (e.g., BufferedReader, readLine, null checks, return statements) and overgeneralized, missing the distinct domain-specific logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the functions have entirely different purposes and outputs; no partial functionality overlap or semantic equivalence.
- 共享行为: Both use BufferedReader to read from a stream line by line.；Both parse tokens or substrings from lines read.；Both handle potential null or missing data and return a default/null value.；Both use try-catch or try-finally blocks for exception handling.
- 行为差异: A loads a User object; B returns a String encoding.；A reads from a local config file; B reads from a URL connection.；A creates and saves a User; B only extracts encoding.；A uses StringTokenizer; B uses contains and indexOf.
- 修正建议: Include more diverse non-clone pairs with similar I/O boilerplate but different semantics.；Improve modeling of domain-specific vocabulary and data flow (e.g., User vs. encoding).；Use techniques to emphasize functional purpose over generic control flow.

### case_id=155 FP long_range_semantics

- 方法: `split` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Splits a large FASTA file into multiple smaller partitions based on size or entry count limits.
- B 摘要: Reads configuration data from tokenized strings and populates various sets and hash tables for Tibetan/EWTS processing.
- 静态失败原因: The model may have been misled by the presence of common Java constructs (loops, conditionals, collection operations) and underestimated the overall semantic difference, despite low token Jaccard. Possibly the model overfitted to certain patterns.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotators would clearly label these as non-clones because they serve entirely different purposes with no functional overlap, and the token-level similarity is very low.
- 行为差异: Function A performs file I/O and splitting logic on FASTA files.；Function B processes string tokens and populates in-memory data structures.；Function A returns a Long count of partitions; Function B is void and populates static fields.；Function A involves complex state machine for FASTA parsing; Function B uses simple token iteration.
- 修正建议: Enhance model with global control-flow and data-flow graphs.；Use contrastive learning to teach models to distinguish based on overall purpose.；Incorporate task-specific pre-training on file processing vs. string parsing domains.

### case_id=156 FN benchmark_preference_bias

- 方法: `doGet` vs `encodeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET requests for a portal page, performing page retrieval, visibility checks, logging, caching, and response output.
- B 摘要: Encodes a file to base64 and writes the output to another file.
- 静态失败原因: Static BERT did not fail; it correctly predicted non-clone (0). The error type 'FN' suggests BCB label is incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label of 1 is likely an error, as there is no meaningful semantic or structural similarity; possibly due to accidental presence of file-related code in A or broad interpretation of 'file operations'.
- 行为差异: Different overall purpose: HTTP request handling vs. file encoding；Different input/output mechanisms: HTTP request/response vs. file streams；Different logic complexity: A includes page navigation, user permissions, caching; B is a straightforward I/O loop
- 修正建议: Review BCB annotation guidelines to ensure consistency；Remove or correct mislabeled pairs in the benchmark；Use stricter criteria for clone labeling

### case_id=157 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `writeFileType`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles a handshake packet by validating a server key and either sending a login packet or shutting down the network connection.
- B 摘要: Reads a file of URIs, fetches each URI's content, classifies it as OWL/RDFS/RDF/unknown, and writes results to an output file.
- 静态失败原因: Static BERT models may over-rely on overlapping API tokens (URL, BufferedReader, printStackTrace) and miss the radical difference in control flow and overall semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB generally labels as non-clones when functions have entirely different high-level purposes and outputs, even if they share some low-level API usage.
- 共享行为: Both use URL and BufferedReader to fetch data from a URL；Both have exception handling with printStackTrace
- 行为差异: A performs authentication and network shutdown; B classifies document types and writes to file；A has a single URL fetch per call; B loops over many URIs from a file；A's output is a login packet or shutdown; B's output is a classification written to file
- 修正建议: Improve model's ability to distinguish shared library usage from shared functionality；Incorporate control flow and data flow features to capture different logic paths；Use contrastive learning to emphasize purpose differences

### case_id=158 FN benchmark_preference_bias

- 方法: `main` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Main method that copies files from a source to multiple targets using FileChannel, optionally deletes originals and performs SVN operations.
- B 摘要: Method that builds a website for editing by parsing XML configuration, transforming pages, and writing output files with various string replacements.
- 静态失败原因: The model correctly identified low lexical overlap (Jaccard 0.115) and distinct API usage, but BCB's broad annotation criterion leads to a false positive label that the model cannot capture without deeper semantic understanding.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotators may have considered both as 'file manipulation' clones due to presence of file streams and loops, but this is too broad and likely a mislabel.
- 共享行为: Both perform file I/O (reading/writing)；Both iterate over collections (targets/pages)
- 行为差异: Different purposes: file copying vs. site building；Different data structures: simple file paths vs. complex XML/Properties；Different iteration logic and error handling
- 修正建议: Re-evaluate BCB labels for pairs with low token similarity; consider stricter clone definition.；Incorporate more diverse negative examples in training to avoid overfitting to broad functional categories.

### case_id=159 FN partial_functionality

- 方法: `readPage` vs `getHTML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL, optionally skipping lines starting with '#', returns content with newline characters.
- B 摘要: Reads a URL with specified encoding and user-agent, returns content with CRLF, and optionally writes it to a file.
- 静态失败原因: Low token Jaccard similarity (0.246) and significant surface-level differences (parameters, file writing, error handling) likely caused the model to overlook the shared core behavior of fetching HTML from a URL.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions fundamentally retrieve HTML from a URL and return it as a string, which is considered the core functionality despite differences in parameters, line endings, and file writing.
- 共享行为: Both open a URL connection and read all lines of HTML content.；Both concatenate lines and return the HTML as a single string.
- 行为差异: Function A ignores comment lines when ignoreComments is true; B does not.；Function B uses a specific User-Agent and encoding; A does not.；Function A uses newline (\n); B uses CRLF (\r\n).；Function B writes the HTML to a file if dirPath is provided; A does not.
- 修正建议: Incorporate semantic similarity focused on core I/O operations (e.g., URL opening, reading lines, string concatenation).；Use program slicing to isolate the common subset of functionality for comparison.

### case_id=160 FP boilerplate_overlap

- 方法: `getTicketsForQueue` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves open tickets for a given queue from a Request Tracker system via HTTP REST API, parses ticket IDs, and fetches each ticket.
- B 摘要: Checks for available software upgrades by querying a remote server and database, processes upgrade data, and updates UI components accordingly.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overfocused on common boilerplate code (e.g., BufferedReader, try-catch, line reading) and missed the distinct domain-specific logic and data flows, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they have completely different purposes and functionalities, despite some surface-level similarities in I/O patterns.
- 共享行为: Both use HTTP connections to interact with remote servers；Both read response data line by line using BufferedReader
- 行为差异: Function A performs a query to retrieve tickets; Function B checks for upgrades and manages UI；Function A interacts with a REST API; Function B uses a URL connection to a JSP page；Function A parses ticket IDs from lines; Function B parses XML-like rows and fields；Function A returns a list of tickets; Function B returns void
- 修正建议: Enhance training with more diverse non-clone pairs that share I/O patterns；Incorporate data flow and control flow analysis to distinguish semantically different functions；Use graph-based representations that capture call dependencies and data transformations

### case_id=161 FN partial_functionality

- 方法: `ExternalDecoder` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: A constructor that sets up a background thread to copy data from an input stream to a process's stdin, then closes.
- B 摘要: A static method that downloads a WSDL file from a URL, modifies its XML endpoint, and returns the file path.
- 静态失败原因: Static BERT models rely on surface tokens; low lexical overlap (Jaccard=0.057), different method names, and different API calls (IOUtils vs NIO) obscured the shared copy pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered both as performing a 'copy stream' operation, a common functional pattern, despite different contexts and additional logic.
- 共享行为: Both perform I/O operations that copy data from an input stream to an output stream.；Both handle IOExceptions (though differently).
- 行为差异: A is a constructor; B is a static utility method.；A copies to a process's stdin; B copies to a file.；A uses IOUtils.copy; B uses NIO transferFrom.；B modifies XML and renames files; A does not.
- 修正建议: Incorporate data flow analysis to detect stream copy patterns across different APIs.；Use a larger context window to capture the I/O operation essence.；Train on functional similarity rather than exact token overlap.

### case_id=162 FN boilerplate_overlap

- 方法: `login` vs `scrapeForIsbns`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into a system by sending credentials via HTTP POST and returns session ID.
- B 摘要: Scrapes a URL for ISBN-10 patterns using regex and returns count of matches.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low token overlap and different method names, causing low similarity score; they may not capture the semantic divergence in high-level intent.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled as clone because both functions involve network I/O with similar boilerplate (try-catch, URL, BufferedReader), but this overlooks fundamental differences in purpose and behavior.
- 共享行为: Both open a URL connection；Both read lines from an input stream；Both handle exceptions
- 行为差异: login uses HTTP POST with output stream; scrape uses HTTP GET；login extracts session ID from first response line; scrape uses regex on all lines；login has no retry logic; scrape retries on ConnectException；login sets internal session state; scrape populates a collection of ISBNs
- 修正建议: Incorporate control flow and data flow analysis；Use contrastive learning to reduce weight of boilerplate tokens；Add functional context (e.g., method call sequences)

### case_id=163 FN benchmark_preference_bias

- 方法: `doGet` vs `testReadHelloWorldTxt`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve and render a portal page with visibility checks, logging, and caching.
- B 摘要: Unit test that reads a resource file, copies it to a temp directory, and verifies FSContentResolver retrieves content from various path forms.
- 静态失败原因: The model correctly predicted non-clone due to very low token similarity and structural differences. It failed to match the erroneous BCB label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Given the low token overlap and completely different domains, it is unlikely that BCB annotators would label these as clones even under broad Type-3/Type-4 criteria. The BCB label of 1 may be a misannotation or data error.
- 共享行为: Both methods read data from a file or resource.；Both handle exceptions (e.g., IOException).；Both perform logging of information.
- 行为差异: A is a servlet handler with complex page rendering and user authentication; B is a simple unit test with assertions.；A uses HttpServletRequest/HttpServletResponse; B uses InputStream/FileOutputStream and FSContentResolver.；A writes output to HTTP response and optionally caches to disk; B writes to a temp file and reads back for verification.；A has many nested try-catch blocks; B has a single exception declaration.
- 修正建议: Review BCB annotation quality for this pair to ensure correctness.；Incorporate high-level semantic similarity measures beyond token overlap.；Use dataflow analysis to detect common I/O patterns.

### case_id=164 FN benchmark_preference_bias

- 方法: `getResourceAsStream` vs `doUpload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Retrieves a resource as an InputStream with caching to a local file, handling HTTP and file I/O.
- B 摘要: Handles multipart file upload, creates temporary directories, processes upload parameters, and manages response redirects.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on low token similarity (Jaccard 0.08) and different method contexts (resource loading vs servlet upload), leading it to correctly identify them as non-clones. The model failed to detect a BCB-style clone because it weighted semantic differences more heavily than structural pattern overlap, which BCB considered sufficient.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to the presence of similar file I/O patterns, directory creation, error handling with stream cleanup, and caching behavior, despite different overall purposes. BCB's broad interpretation of Type-3/Type-4 clones could consider the structural similarity sufficient.
- 共享行为: Both involve file I/O operations (reading/writing files)；Both create directories (mkdirs/mkdir)；Both use try-catch blocks with stream cleanup；Both involve URL or path manipulation
- 行为差异: Function A reads a remote resource and caches it locally；Function B writes uploaded files to a temporary directory；Function A returns an InputStream；Function B writes to response, forwards request, or returns void
- 修正建议: Re-evaluate BCB annotations to ensure they align with semantic equivalence, not just structural overlap；Incorporate more diverse examples of non-clones with similar I/O patterns to improve model robustness；Use contrastive learning to emphasize functional purpose over superficial patterns

### case_id=165 FN partial_functionality

- 方法: `doGet` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to serve portal pages with access control, caching, and logging.
- B 摘要: Reads from a file and writes to another, with optional diagnostics mode using security annotations.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token overlap and syntactic structure. The low Jaccard similarity (0.088) and different APIs (servlet vs file I/O) result in low token-level similarity. Additionally, the models may not capture high-level semantic patterns like 'read-process-write' without explicit dataflow information.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled these as clones because both implement a 'read-process-write' pattern at a high level, which is a Type-4 semantic clone. Despite different APIs and domains, the overall data flow and conditional structure are similar enough to be considered a broad clone.
- 共享行为: Both perform I/O operations: reading input and producing output.；Both have conditional logic to alter behavior based on parameters.；Both include error handling (exceptions or error responses).
- 行为差异: Different input sources: HTTP request parameter vs file path argument.；Different output targets: HTTP response stream vs file output stream.；Different programming domains: web portal vs file processing utility.；Function A includes authentication, page visibility checks, caching, and detailed logging.
- 修正建议: Use data flow or program dependence graphs to capture abstract I/O patterns.；Incorporate domain-agnostic normalization (e.g., replacing specific API calls with generic concepts like 'read' and 'write').；Train with examples of broad semantic clones that share functionality structure despite different implementations.

### case_id=166 FN benchmark_preference_bias

- 方法: `doVersionCheck` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Checks for a new version by reading a version file from a URL and comparing builds.
- B 摘要: Invokes a remote service via HTTP POST, reads JSON response, and deserializes it, with retry logic on timeout.
- 静态失败原因: Static BERT/GraphCodeBERT likely predicted 0 (non-clone) because the token overlap is low (0.16) and the semantic purposes differ significantly. The model correctly captured that these functions are unrelated, but BCB label suggests a false positive in the dataset.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone due to broad Type-4 similarity: both functions perform network I/O using similar boilerplate code (open stream, read lines, close) and error handling. The annotation might have prioritized structural pattern over semantic purpose.
- 共享行为: Both open a URL/HTTP connection and read lines from an InputStream using BufferedReader.；Both handle IOException by showing an error message or throwing an exception.
- 行为差异: Function A is a version-check utility; Function B is a generic RPC invocation method.；Function A uses GET request implicitly; Function B uses POST with JSON payload.；Function B has retry logic; Function A does not.；Function B deserializes JSON response; Function A only compares version strings.
- 修正建议: Re-evaluate BCB annotation for this pair; consider refining clone criteria to exclude purely structural patterns without functional overlap.；For detection, use models that better capture semantic intent rather than surface-level I/O patterns.

### case_id=167 FN other

- 方法: `doGet` vs `readFixString`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests for portal pages with authentication, logging, error handling, and caching.
- B 摘要: Reads a fixed-length string from an input stream using IOUtils.copy and returns it.
- 静态失败原因: Static BERT did not fail; it correctly predicted non-clone. The BCB label is erroneous.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: This pair is likely a false positive in BCB; perhaps the annotator mistakenly considered both as involving I/O operations, but their functionality is completely unrelated.
- 行为差异: Function A processes HTTP requests and responses; function B reads from an input stream.；Function A involves complex business logic (page retrieval, permissions, caching); function B is a simple utility.；Function A writes to output stream; function B returns a string.；Function A has extensive error handling specific to web context; function B wraps an IOException into a runtime exception.
- 修正建议: Re-evaluate the BCB annotation for this pair to correct the label to non-clone.

### case_id=168 FN partial_functionality

- 方法: `copyResource` vs `makeBackup`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a single resource (URL or file) to a destination file using byte stream.
- B 摘要: Backs up all files from a source directory to a destination directory, including directory creation and timestamp setting.
- 静态失败原因: Static BERT/GraphCodeBERT models often rely on token-level and structural patterns. Here, the token Jaccard similarity is low (0.223), and the method names are different ('copyResource' vs 'makeBackup'). The model may have been misled by the different method signatures, additional parameters in B, and the surrounding boilerplate code (e.g., directory listing, timestamp setting) which obscures the shared core loop. The long-range dependency of the loop structure might not be captured well, and the dataflow of streams is not explicitly represented.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers this a Type-4 clone because the core functionality of copying files using byte streams is identical, and the additional operations in B are considered peripheral. The shared loop structure and stream usage outweigh the differences in context.
- 共享行为: Both use byte-by-byte stream copy (while read/write loop)；Both open FileInputStream and FileOutputStream (though A also handles URL)；Both close streams after copying
- 行为差异: A copies a single resource, B copies multiple files from a directory；B creates destination directories and sets timestamps；B has exception handling with printStackTrace, A throws exception；B handles a specific file (azureus.config) separately
- 修正建议: Improve representation of data flow and control flow to highlight core shared patterns；Use graph-based models that can abstract away peripheral operations；Enhance tokenization to capture stream operations more robustly；Consider method-level refactoring or alignment of similar subroutines

### case_id=169 FN partial_functionality

- 方法: `transport` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.1`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Recursively copies files from a source to a destination directory using NIO file channels.
- B 摘要: Generates static site pages by transforming XML with XSLT and writing output files.
- 静态失败原因: Low token similarity (Jaccard 0.078) and very different method names, signatures, and code structures misled the static model into predicting non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: The BCB annotation might consider these clones due to both involving file transfer/output operations, but the semantic gap is large. Likely a labeling error or unintended broad interpretation.
- 共享行为: Both perform file I/O operations (reading and writing files).；Both use FileInputStream and FileOutputStream.；Both iterate over collections (files in directory, pages in vector).
- 行为差异: A is a simple recursive file copy; B is a complex multi-step site builder with XML transformation.；A handles directories; B does not.；A has a single file parameter; B has many parameters including paths, properties, and configuration strings.；B includes exception handling for specific types like DOMException and TransformerException; A only handles IOException.
- 修正建议: Use a clone detector that captures semantic roles (e.g., dataflow analysis) rather than surface tokens.；Increase the weight of functional behavior over boilerplate code.；For BCB, re-evaluate the ground truth label to ensure consistency.

### case_id=170 FP partial_functionality

- 方法: `sendPost` vs `getURLContent`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an HTTP POST request with parameters and returns the response body as a string, with error handling by catching exceptions.
- B 摘要: Opens a URL connection (HTTP GET) and reads the entire content into a string, appending newlines, and throws IOException.
- 静态失败原因: Static models like BERT or GraphCodeBERT may focus on lexical and structural similarities (URL, BufferedReader, readLine) while missing the semantic difference in HTTP method and parameter handling, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels clones based on functional equivalence. Although both functions fetch URL content, the core functionality differs (POST vs GET) and error handling/encoding diverges, making them non-clones under BCB's definition.
- 共享行为: Both open a URL connection to retrieve content；Both read the response line by line using BufferedReader；Both return the content as a String
- 行为差异: Method A uses POST with a parameter string; Method B uses GET without parameters；Method A sets request properties (Accept-Language) and enables output; Method B does not；Method A handles exceptions by printing a message; Method B declares throws IOException；Method A uses UTF-8 encoding explicitly; Method B uses the connection's content encoding (defaulting to ISO-8859-1)
- 修正建议: Incorporate AST or data flow features to distinguish HTTP method (e.g., setDoOutput, PrintWriter usage)；Use method names or comments as additional signals；Train on more examples of POST vs GET to capture the distinction

### case_id=171 FN benchmark_preference_bias

- 方法: `getEncoding` vs `getXML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Extracts character encoding from a URL by checking HTTP headers and scanning response lines.
- B 摘要: Fetches the full XML content from a servlet URL as a string.
- 静态失败原因: Static BERT models rely on token and structural similarity; these functions have low token overlap (0.2058), different method names, and distinct control flow (header loop vs direct read). The model overlooked the higher-level semantic category of 'URL response processing' that BCB annotators considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely classifies these as Type-4 clones because both are utility methods that read from a URL line-by-line, sharing the core pattern of 'open stream, read lines, handle IO' even though their specific purposes differ (encoding detection vs content retrieval).
- 共享行为: Both open a URL connection and read data using BufferedReader；Both read lines in a while loop until null；Both handle IO exceptions (implicitly or with catch blocks)；Both return a String value
- 行为差异: A searches for encoding in headers and content; B simply concatenates all lines；A has header parsing and early return logic; B has no parsing；A uses try-finally for resource cleanup; B closes stream inside try；A returns a default encoding if not found; B returns null on any exception
- 修正建议: Train with a dataset that includes partial-functionality clones to capture broader semantic categories；Incorporate global context (e.g., class-level or domain-specific hints) to infer higher-level intent；Use contrastive learning that groups functions by overall behavior rather than only structural overlap

### case_id=172 FP boilerplate_overlap

- 方法: `main` vs `setContenu`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A main method that parses command-line arguments, reads a Prolog file, and generates adapter JAR resources.
- B 摘要: A method that copies file content from a content source to a file, sets metadata, and handles existing file conflicts.
- 静态失败原因: Static BERT may have overfocused on common boilerplate patterns like try-catch-finally, IOUtils.copy, and file existence checks, while ignoring the distinct method names and high-level purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions serve completely different purposes, despite both involving file operations; Type-3/Type-4 similarity is not met.
- 共享行为: Both involve file I/O operations；Both have conditional checks and exception handling；Both use InputStream/OutputStream patterns
- 行为差异: A is a command-line entry point for code generation; B is a business logic method for file management；A generates classes and JARs; B copies streams and sets metadata；A uses complex class generation; B uses simple stream copying
- 修正建议: Enhance the model to better leverage method names and class context；Train on more non-clone pairs with similar boilerplate but different core logic；Incorporate data flow analysis to distinguish different data transformations

### case_id=173 FN partial_functionality

- 方法: `getFile` vs `extractResourceToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies a SOAP address location attribute, and saves to a temp file.
- B 摘要: Extracts a classpath resource to a file using InputStream and FileOutputStream.
- 静态失败原因: Low token overlap (0.0866) and long-range semantic differences (XML manipulation, multiple steps) likely caused the model to miss the shared byte-copying pattern, classifying as non-clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may view both as 'extract resource to file' operations (Type-4 functional similarity) despite different sources and additional processing in A.
- 共享行为: Both read from an InputStream and write to a FileOutputStream
- 行为差异: Source of data: URL vs classpath resource；A performs XML modification (wsdlsoap:address) and temp file renaming; B does not；A has extensive error handling and logging; B is simpler
- 修正建议: Incorporate data-flow analysis to detect common I/O patterns；Use control-flow abstraction to ignore unrelated XML processing；Add fine-grained clone detection for sub-patterns like 'copy stream to file'

### case_id=174 FN benchmark_preference_bias

- 方法: `createFile` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies content from a source file to an output stream managed by a resource manager.
- B 摘要: Modifies a locale-specific properties file by replacing or adding a message entry.
- 静态失败原因: The model correctly identified the low token overlap and structural differences, but BCB's annotation might reflect a bias toward considering any file I/O operations as semantically similar, which the model did not capture.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as file manipulation utilities (read/write) with shared mechanisms, possibly labeling them as Type-4 clones based on broad functional similarity in file processing.
- 共享行为: Both handle file I/O operations；Both use exception handling (try-catch)；Both close streams/readers after use
- 行为差异: A copies an entire file to a resource; B reads, modifies, and writes a properties file；A uses IOUtils.copy for bulk copy; B uses manual line-by-line parsing；B has complex logic for file existence, fallback copy, and property key-value parsing；A targets a resource manager; B targets the local file system
- 修正建议: Refine clone definition to require more precise behavioral equivalence；Incorporate higher-level intent or application domain context；Use data flow analysis to distinguish distinct file manipulation patterns

### case_id=175 FP lexical_or_api_overlap

- 方法: `sendRequest` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an XML request to a servlet via HTTP with GZIP compression, and returns an empty string.
- B 摘要: Downloads an RDF model from a URL using Apache Jena and returns the model.
- 静态失败原因: Static BERT models may have been misled by overlapping API calls (URL.openConnection, InputStream, try-catch blocks) and similar control flow structure, ignoring differences in compression, return types, and overall task.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have different high-level purposes and return types, despite some shared networking patterns.
- 共享行为: Both open an HTTP connection and read an InputStream.
- 行为差异: A sends an XML request with GZIP compression; B only reads a model.；A returns empty string; B returns a Model object.；A handles connection errors with UI dialog; B logs and throws RuntimeException.；A is instance method using preferences; B is static with URL argument.
- 修正建议: Add features capturing return type and overall purpose (send vs. download).；Incorporate data flow analysis to distinguish writing to output stream vs. reading only.；Use models that better capture semantic roles of method arguments and outputs.

### case_id=176 FN partial_functionality

- 方法: `fileDownload` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a URL and saves it as 'download.pdf' in a specified directory.
- B 摘要: Reads data from a URL or local file, returning a status code.
- 静态失败原因: Low lexical overlap (Jaccard 0.149) and different API usage patterns (BufferedReader vs BufferedInputStream, FileOutputStream vs status return) cause the model to focus on syntactic differences rather than the shared URL reading intent.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often considers broad Type-3/Type-4 clones where functions share a core I/O pattern; here, both read from a URL, so they may be judged as functionally similar despite different outputs.
- 共享行为: Both open a URL connection and read from the input stream
- 行为差异: A writes the downloaded content to a file; B does not write to a file；A only handles URLs; B also handles local file paths；A uses text-based streams; B uses binary streams；A saves to a fixed filename; B returns a status and relies on an internal read method
- 修正建议: Augment training data with abstracted I/O examples；Incorporate code summarization features to capture high-level semantics

### case_id=177 FP lexical_or_api_overlap

- 方法: `readData` vs `fileCopy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads data from a file, parsing tokens and populating various sets and maps related to Tibetan transliteration.
- B 摘要: Copies a file from source to destination with error handling.
- 静态失败原因: The static model may have been misled by common API usage (File, IOException, StringTokenizer) and the presence of file-related operations, but ignored the overall functional disparity and long-range semantic context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have entirely different purposes and implementations; one is a data parser, the other is a file utility.
- 共享行为: Both involve file I/O and exception handling.
- 行为差异: readData parses and structures data into multiple collections; fileCopy simply transfers bytes.；readData has complex parsing logic with multiple tokenizers and conditional processing; fileCopy is straightforward.；readData writes to internal data structures; fileCopy writes to an output file.；Error handling differs significantly: readData throws generic Errors and catches IOException; fileCopy uses custom abort() and finally block.
- 修正建议: Improve model's ability to capture overall control flow and data dependencies beyond surface API tokens.；Incorporate dataflow analysis to distinguish between reading data for transformation vs. raw copying.；Add training examples with high token overlap but different semantics.

### case_id=178 FP lexical_or_api_overlap

- 方法: `readRemoteFile` vs `handleHandshake`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a remote file from a URL and returns its content as a string.
- B 摘要: Handles a Minecraft handshake packet by validating username and performing session authentication via HTTP.
- 静态失败原因: The model likely over-relied on lexical overlap of common stream-reading API calls (URL, BufferedReader, readLine) and structural patterns (open, read, exception handling), ignoring the domain-specific logic and different program purposes.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because the functionality is entirely different despite shared API usage; BCB requires significant functional similarity, which is absent here.
- 共享行为: Both use URL and BufferedReader to read from a network stream；Both handle exceptions in a try-catch block
- 行为差异: A reads file content line by line; B validates authentication and sends network packets；A returns a String; B returns void and manipulates game state；A has a simple loop; B has multiple conditional branches specific to Minecraft protocol
- 修正建议: Incorporate semantic role analysis to distinguish reading from authentication；Use dataflow graphs to capture the purpose of data (e.g., output vs. side effect)；Consider function names and context to disambiguate domain-specific tasks

### case_id=179 FP lexical_or_api_overlap

- 方法: `decodeFileToFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Decodes a Base64-encoded input file and writes the decoded content to an output file, returning success status.
- B 摘要: Handles GUI action events by performing various UI operations like opening file choosers, updating preferences, and changing look-and-feel settings.
- 静态失败原因: The model likely over-relied on superficial lexical overlap (e.g., common tokens like 'File', 'InputStream', 'OutputStream', 'try-catch', 'null') and the presence of file-related APIs, ignoring the stark difference in overall program logic and intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because they perform entirely different tasks (file decoding vs. GUI event handling) with no functional similarity, even at a broad Type-4 level.
- 行为差异: Function A performs file I/O with Base64 decoding; Function B handles GUI event-driven actions.；Function A returns a boolean indicating success; Function B is void and modifies UI state.；Function A uses byte streams and fixed-size buffers; Function B uses Swing components and preference storage.；No overlap in the logic or purpose of the two functions.
- 修正建议: Increase negative sampling of non-clones that share lexical patterns but differ in semantics.；Incorporate control-flow or data-flow analysis to capture functionality rather than just token sequences.；Use larger context windows or graph-based representations (like AST or CFG) to distinguish structural dissimilarities.

### case_id=180 FN partial_functionality

- 方法: `login` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into a remote service by sending POST request with email/password, extracting session ID from response, and setting it locally.
- B 摘要: Registers a user by encoding password, setting user properties, making a GET request to a forum to create user, persisting to database, and sending confirmation email.
- 静态失败原因: Static BERT fails due to low lexical overlap (token Jaccard 0.14) and different method names, focusing on surface tokens rather than functional pattern of HTTP client operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them as having partial functionality similarity because both involve network communication and similar boilerplate code for URL connection, despite different business logic.
- 共享行为: Both make HTTP requests to a remote URL；Both use URLConnection and BufferedReader to handle response；Both encode parameters for the request
- 行为差异: HTTP method: POST vs GET (implicitly via URL parameters)；Response handling: single line extraction vs reading all lines and setting integer values；Side effects: set session locally vs persist user and send email；Error handling: return empty string vs throw runtime exceptions
- 修正建议: Include API call patterns as features；Use dynamic analysis to capture behavioral equivalence；Leverage structural similarity beyond token overlap

### case_id=181 FN partial_functionality

- 方法: `parse` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses an InputStream by either saving it to a file if the resource name is in a wanted set or delegating to a downstream parser.
- B 摘要: Retrieves a resource as an InputStream by downloading and caching it locally if not already cached, with exception handling and debug output.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low token overlap (0.12) and different method signatures, causing the model to focus on surface-level dissimilarity rather than the high-level semantic pattern of conditional file saving.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as Type-4 semantic clones because they share the high-level pattern of 'conditional file output based on a lookup', which is a common resource handling idiom, despite different implementations and contexts.
- 共享行为: Both involve conditional writing to a file based on a map lookup (wanted map vs. cache hashtable).；Both handle streams and file output with exception handling.
- 行为差异: Function A writes the input stream directly to a file if the name is wanted; Function B downloads from URL and caches with modification checking.；Function A delegates to another parser if not wanted; Function B returns a cached file input stream.；Function A is simple and synchronous; Function B is complex with network I/O and caching logic.；Signatures differ: A takes InputStream, ContentHandler, Metadata, ParseContext; B takes String name and returns InputStream.
- 修正建议: Incorporate data flow and control flow analysis to capture common subpatterns like conditional file writing.；Train on more diverse Type-4 clones with low token overlap but high semantic similarity.；Use domain-specific pre-training on resource handling code.

### case_id=182 FN benchmark_preference_bias

- 方法: `readGeoParserResult` vs `parse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Sends XML request to a geo-parsing web service and extracts place names with gazetteer IDs from response.
- B 摘要: Parses a delimited text file from a URL or local file into a DataSet object, handling headers, types, and number formats.
- 静态失败原因: The static model likely focused on low token overlap and different API calls, failing to capture any abstract parsing similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'parsing functions' that read from a source and produce structured data, possibly viewing them as Type-4 clones due to high-level functional similarity.
- 共享行为: Both read input from an external source (URL or file) using BufferedReader；Both perform parsing of structured data；Both handle exceptions and retries in some way
- 行为差异: A specifically queries a geo-parsing web service with XML, B reads arbitrary delimited files；A returns a collection of tuples of strings, B returns a DataSet object；A has early return for testing, B has dryrun mode；A uses Document and Element XML parsing, B uses StreamTokenizer and type conversion
- 修正建议: Improve model to require stronger functional similarity beyond high-level parsing；Add negative examples with different parsing domains

### case_id=183 FN partial_functionality

- 方法: `copyResource` vs `createNew`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (from URL or local file) to a destination file using byte-by-byte read/write.
- B 摘要: Creates a new resource by writing an InputStream to a file in a folder, but only if client is allowed and filename matches specific patterns; also handles request management and returns resource objects.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap and surface-level syntax; the low Jaccard similarity (0.102) and different method names, signatures, and control flow make the embedding distance large, causing a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often annotates Type-4 clones where the core functionality (copying an input to a file output) is present, even if the surrounding logic and signatures differ. Here both methods perform that core copy, so BCB likely considered it a weak clone.
- 共享行为: Both copy data from an InputStream to a FileOutputStream.
- 行为差异: Function A reads from a URL or local file; Function B receives the InputStream as a parameter.；Function A copies byte-by-byte; Function B uses IOUtils.copy.；Function B has permission checks and conditional logic for filename, and returns different types or null.；Function A throws Exception on missing resource; Function B returns null or logs error.
- 修正建议: Incorporate dataflow analysis to detect the common copy pattern (InputStream to OutputStream).；Use AST-based matching of core functionality, ignoring auxiliary checks and different I/O sources.；Train on functional annotations that capture partial behavior similarity.

### case_id=184 FN partial_functionality

- 方法: `main` vs `createOutputStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts all entries from a zip file (KMZ) to individual files, printing extraction info.
- B 摘要: Copies entries from one zip file to another, skipping 'content.xml' and adding a new one, then returns a BufferedWriter.
- 静态失败原因: Static models may focus on lexical overlap (e.g., ZipInputStream, ZipEntry, read loops) and miss the divergent data flow and overall purpose. The difference in method signature, return type, and specific logic (skipping entry) may cause under-confidence or misclassification due to partial functionality alignment.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as clone because both methods involve reading a ZIP archive, iterating entries, and performing I/O, which is a common pattern for ZIP manipulation tasks. The structural and conceptual similarity in the core loop likely justifies a Type-4 annotation despite different goals.
- 共享行为: Both use ZipInputStream to iterate over zip entries；Both read byte/character data from zip entries；Both write data to some output
- 行为差异: A writes to individual files, B writes to a zip output stream；A processes all entries, B skips a specific entry and adds a new one；A is a main method with no return, B returns a BufferedWriter；A uses BufferedOutputStream, B uses BufferedWriter with specific encodings
- 修正建议: Incorporate dataflow analysis to track how inputs and outputs are processed；Use contrastive learning to emphasize functional differences beyond lexical overlap；Leverage function name and return type as semantic cues

### case_id=185 FN partial_functionality

- 方法: `updateFile` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file to a new location by replacing a path prefix, using FileChannel for efficient transfer.
- B 摘要: Modifies a locale-specific properties file by updating or adding a key-value pair, creating the file if needed by copying from an English properties file.
- 静态失败原因: Low lexical overlap (token Jaccard 0.14) and different API usage (FileChannel vs Properties/Reader) cause static BERT models to miss the functional similarity. The models rely on surface-level token matches and do not capture the underlying file I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as file update operations that involve reading and writing files, potentially with creation if missing. The high-level purpose of updating a file is shared, even though the specific transformation differs, which aligns with BCB's acceptance of Type-3/Type-4 partial functionality similarity.
- 共享行为: Both perform file reading and writing operations.；Both check if the destination file exists and create it if not.；Both use file streams to handle I/O.；Both involve file creation and directory creation.
- 行为差异: A copies an entire file unchanged, while B reads and modifies specific lines of a properties file.；A uses FileChannel for copying; B uses BufferedReader/Writer and string manipulation.；A does not parse file content; B parses properties format.；A is a generic file copy; B is specific to i18n property files.
- 修正建议: Incorporate dataflow analysis to track file read/write operations.；Use AST-based matching for file I/O patterns.；Train on more pairs with low lexical but high functional similarity.；Consider domain-specific knowledge of common file manipulation idioms.

### case_id=186 FP lexical_or_api_overlap

- 方法: `loadSourceCode` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a source file from a resource, applies syntax highlighting, and returns an HTML string.
- B 摘要: Performs a Google image search by fetching and parsing HTML to extract image URLs into a list.
- 静态失败原因: The static model likely overemphasized the shared use of URL, BufferedReader, and exception handling patterns, mistaking structural overlap for semantic equivalence.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels functions as non-clones unless they share core functionality. Here, the purposes (source code viewer vs. image search) are entirely different, despite superficial I/O pattern similarities.
- 共享行为: Both use URL, BufferedReader, and InputStreamReader for I/O.；Both have try-catch blocks handling exceptions.；Both involve reading lines in a loop.
- 行为差异: One reads a local resource for source code display; the other fetches external web data for image search.；One processes lines with syntax highlighting; the other parses HTML for image links.；One outputs an HTML string; the other populates a list of image URLs.；One uses getResource and openStream; the other uses HttpURLConnection with custom headers.
- 修正建议: Incorporate higher-level semantic analysis, e.g., function purpose from comments or method names.；Use more discriminative features like the data flow of domain-specific objects (e.g., syntax highlighter vs. image parser).；Augment training with more diverse examples of I/O patterns with different intents.

### case_id=187 FN benchmark_preference_bias

- 方法: `readData` vs `createDialogArea`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated string fields into sets and a map, and reads a file to populate internal data structures.
- B 摘要: Creates a dialog area with a browser or text widget, reads a license file from a bundle, and displays its content.
- 静态失败原因: Static methods like BERT or GraphCodeBERT rely heavily on token overlap and structural similarity; the very low token Jaccard (0.0888) and completely different APIs (StringTokenizer vs. Browser, SWT vs. set/map operations) led to a correct non-clone prediction, but BCB label suggests a different criterion.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'data loading' or 'initialization' routines, possibly accepting broad Type-4 similarity based on high-level purpose, even though implementations are entirely different.
- 共享行为: Both involve reading from some source (StringTokenizer or file)；Both perform some form of data initialization
- 行为差异: readData parses multiple tokenized strings and a file into sets/maps; createDialogArea creates UI components and reads a single file for display；readData is static void with no UI; createDialogArea returns a Control and builds a dialog；Error handling differs: readData throws Error, createDialogArea catches IOException and prints stack trace；readData involves complex column parsing logic; createDialogArea simple file read
- 修正建议: Review BCB annotation guideline for this specific pair; likely a mislabel；Consider using more context-aware models that can distinguish different high-level behaviors；Augment training data with explicit non-clone pairs that have superficial overlap in reading behavior

### case_id=188 FN boilerplate_overlap

- 方法: `copyFile` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Handles an HTTP GET request for a page, including authentication, caching, and writing cached output to a file.
- 静态失败原因: Static BERT models rely heavily on token overlap and overall semantics. The low Jaccard similarity and vastly different high-level purposes caused the model to predict non-clone, failing to recognize the partial functional similarity in file I/O boilerplate.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotators likely focused on the common pattern of opening a file resource, writing data, and closing within try-catch-finally, which appears in both functions despite different contexts. This partial structural similarity may lead to a Type-3 clone label.
- 共享行为: Both functions write data to a file using Java I/O APIs.；Both use try-catch-finally for resource management and handle IOException.
- 行为差异: copyFile is a simple file copy utility; doGet is a complex servlet handler with multiple conditional branches.；copyFile uses FileChannel for efficient transfer; doGet uses FileWriter for writing string content.；doGet involves HTTP request processing, page lookup, authentication, logging, and statistics; copyFile has none of these.；The file I/O in doGet is conditional and part of a larger workflow; in copyFile it is the entire function.
- 修正建议: Incorporate subgraph-based matching to detect shared code patterns in larger functions.；Use hybrid models that combine lexical similarity with structural or semantic fragment matching.；Fine-tune on tasks emphasizing partial functional similarity (e.g., Type-3 clones) with data augmentation.

### case_id=189 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `recurseFiles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a properties file by replacing or adding a message key-value pair for a given locale.
- B 摘要: Recursively traverses a file tree and adds non-zip files to a zip archive.
- 静态失败原因: Static BERT correctly predicted non-clone due to low token overlap and clear functional difference; no failure here.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Unlikely BCB would label as clone; possibly a labeling error or benchmark noise given the low similarity and distinct functionalities.
- 共享行为: Both perform file I/O operations
- 行为差异: A modifies text properties files; B creates binary zip archives；A reads/writes line-by-line; B copies entire file streams；A handles missing files by copying from English version; B skips directories and zip files；A uses Properties and BufferedReader; B uses ZipArchiveOutputStream and FileInputStream
- 修正建议: Re-evaluate BCB label for this pair；Provide more diverse negative examples in training data

### case_id=190 FN boilerplate_overlap

- 方法: `modifyApplicationMessage` vs `extractImage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file by reading, editing, or appending a message based on locale.
- B 摘要: Extracts an image file, applies scaling and transforms, and writes to output.
- 静态失败原因: The model focused on boilerplate patterns (file I/O, try-catch) and missed semantic differences in data manipulation (properties vs. image processing).
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled them as clones due to broad structural similarity in file processing and exception handling, disregarding domain-specific operations.
- 共享行为: Both involve file I/O operations (reading and writing)；Both use try-catch blocks for exception handling；Both process input and produce output files
- 行为差异: A modifies text-based properties files for i18n; B processes binary image data；A uses Properties and BufferedReader; B uses BufferedImage and Djatoka API；A optionally copies a default file if target missing; B handles STDIN input；A appends missing message; B applies scaling and transforms
- 修正建议: Incorporate dataflow analysis to differentiate text vs. image processing；Use API embeddings to capture domain-specific operations；Require matching of method-level semantics beyond file I/O structure

### case_id=191 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `execute`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles various GUI preference settings via action commands, including file choosers for GRAPHVIZ and IMAGEMAGICK paths, and other settings like country, date format, look and feel.
- B 摘要: Saves a HomeMap object to a database and writes an image file to disk, then returns a list.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on lexical or API overlap (e.g., FileOutputStream, JFileChooser) and missed the completely different semantics and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions are from different domains (preference settings vs. image upload) with no semantic similarity beyond superficial API usage.
- 共享行为: Both involve file operations (reading/writing files).；Both handle exceptions.
- 行为差异: A is a large event handler with multiple branches; B is a simple sequential save.；A heavily uses GUI components; B has no GUI.；A manages preferences; B manages database/file storage.
- 修正建议: Improve sensitivity to control flow and data dependencies.；Incorporate cross-function context or broader scope analysis.；Use contrastive learning with hard negative samples that share API but differ semantically.

### case_id=192 FN benchmark_preference_bias

- 方法: `readAndRewrite` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads a DICOM file and rewrites it to another file using DICOM parsing and pixel data manipulation.
- B 摘要: Launches a NexOpen project configuration, validating Maven pom files and potentially generating reverse engineering resources.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on the low lexical overlap (token Jaccard 0.03) and the completely different API usage, correctly predicting non-clone, but the benchmark annotation may have overgeneralized based on I/O operations.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to both functions involving file input/output and stream handling, which could be considered a partial functional similarity under a broad Type-4 criterion.
- 共享行为: Both perform file I/O operations using streams
- 行为差异: Function A processes DICOM medical images; Function B configures an Eclipse project for a specific framework.；Function A is a simple read-rewrite of a single file; Function B involves multiple file checks, callbacks, and property handling.；Function A uses DICOM-specific APIs; Function B uses Eclipse/Java development APIs.
- 修正建议: Re-evaluate BCB annotations for pairs with very low token similarity to ensure they reflect meaningful semantic similarity.；Incorporate domain-specific awareness to distinguish between medical image processing and project configuration.；Consider using a more fine-grained clone type labeling to reduce false positives in broad Type-4 categories.

### case_id=193 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `testReadPerMemberSixSmall`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Modifies a properties file by updating or adding a message entry for a given locale.
- B 摘要: Tests reading a GZIP members input stream by copying to null output and checking byte counts.
- 静态失败原因: The static method likely correctly predicted non-clone due to very low token overlap and clear functional difference.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have incorrectly labeled due to possible test case or annotation error; there is no apparent similarity.
- 行为差异: Function A handles file I/O and string manipulation for properties files.；Function B handles GZIP stream reading and assertion checks.；Different input/output types and purposes.
- 修正建议: Review BCB annotation for potential mislabeling.；Improve benchmark quality control.

### case_id=194 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `readReferenceText`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a file of zone IDs, parsing each line as an integer, and returns a set of integers.
- B 摘要: Reads a reference text file based on an identifier, concatenates lines with newlines, and returns the full text string, throwing an exception if not found.
- 静态失败原因: The static model likely over-relied on lexical and structural overlap of the read-line loop pattern, ignoring semantic differences in parsing and return type. The boilerplate of URL reading and line iteration caused false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically annotates as clone only if there is significant semantic similarity. Here, despite similar reading pattern, the core functionality (parsing integers vs reading text) differs, so BCB labels as non-clone (Type-4).
- 共享行为: Both open a URL stream and read lines in a loop；Both use InputStreamReader and readLine pattern
- 行为差异: Different return types: HashSet<Integer> vs String；Different parsing: integer conversion vs string concatenation；Different error handling: printStackTrace vs logging and throwing custom exception；Different exception declarations: one catches Exception, one catches specific exceptions
- 修正建议: Train with more diverse non-clone pairs that share boilerplate but differ in core logic；Incorporate dataflow or type information to distinguish different processing of read data

### case_id=195 FP partial_functionality

- 方法: `get` vs `fetchUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches a URL with custom headers, filters lines starting with '#', decodes each line into GameRecord objects, and returns an array.
- B 摘要: Fetches a URL and returns its entire content as a single string.
- 静态失败原因: The static BERT model likely focused on the shared pattern of URL opening and line reading (BufferedReader, while loop), ignoring the differences in return types, filtering, and headers. The common API usage and similar try-catch structure misled the model into predicting a clone.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have distinct return types and processing logic; one is domain-specific (game records) while the other is generic string retrieval. The low token overlap and significant behavioral differences support a non-clone annotation.
- 共享行为: Both open a URL connection and read lines from the response stream；Both use a while loop to read lines；Both handle IOExceptions
- 行为差异: Function A returns an array of GameRecord objects and filters comment lines; Function B returns a concatenated string of all lines；Function A sets custom HTTP headers using additional parameters; Function B has no headers；Function A prints error messages; Function B silently returns empty string on error；Function A specifically decodes lines into GameRecord; Function B just appends strings
- 修正建议: Include type information in static embeddings；Add dataflow analysis to track transformations of data；Use contrastive learning to distinguish functions with different output types and filtering logic

### case_id=196 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `sendPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Connects to a URL to fetch version information and compares with current build, showing UI messages.
- B 摘要: Sends an HTTP POST request with parameters and returns the concatenated response as a string.
- 静态失败原因: The static model likely overvalued lexical and API-level similarities (both use URL, BufferedReader, readLine, try-catch) and the structural pattern of opening a connection and reading lines, ignoring the distinct method names and the high-level purpose differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench typically labels as clones only if functions are semantically equivalent or near-equivalent in core functionality. Here, the intents (version check vs. POST submission) are clearly different despite sharing I/O patterns, so BCB correctly labels as non-clone.
- 共享行为: Open a URL connection and read from an input stream；Use BufferedReader to read lines in a loop；Handle exceptions during network I/O
- 行为差异: A uses GET request, B uses POST request with parameters；A performs version comparison and shows UI messages, B returns a string；A uses view for wait cursor and GUIUtilities for messages, B has no UI；Exception handling differs: A specific IOException, B generic Exception
- 修正建议: Incorporate method name embeddings or purpose-aware features；Use control-flow and data-flow analysis to distinguish different operations (GET vs POST, version comparison vs concatenation)；Include context from class or comments if available

### case_id=197 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `clonarFichero`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles various GUI actions to set application preferences, including file paths for external tools.
- B 摘要: Copies a file from an input stream to a destination using NIO FileChannels.
- 静态失败原因: Low token overlap (0.0606) suggests spurious similarity from common terms like 'File' and 'filename', causing the model to misclassify as clone due to lexical overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: Even under relaxed BCB criteria, these functions share no common subfunctionality; one is a large settings handler, the other a simple file copy.
- 共享行为: Both involve file operations in a Java application.
- 行为差异: A is a GUI event handler with multiple conditional branches; B is a focused file copy utility.；A has side effects on global state and UI components; B only performs file I/O and returns a boolean.；A is void and extensive; B is compact and returns a value.
- 修正建议: Use structural or flow-aware models to capture method size and control flow differences.；Incorporate return type and method signature features to distinguish diverse functionality.

### case_id=198 FN partial_functionality

- 方法: `downloadURLtoString` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads content from a URL and returns it as a string, appending lines without newlines, propagating IOException.
- B 摘要: Reads content from a file or system resource, appending lines, with extensive error handling that prints messages and exits JVM on failure.
- 静态失败原因: Low token Jaccard (0.279) and significant structural differences (extra error handling, print statements, fallback logic) likely caused the model to focus on surface-level features rather than the shared core behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB labels as clone because the core algorithmic pattern (read line-by-line, accumulate, return string) is identical, and the differences in error handling and input acquisition are considered non-essential for functionality-based clone detection.
- 共享行为: Both read line by line from a BufferedReader wrapping an InputStream；Both append each line to a StringBuffer；Both return the concatenated string
- 行为差异: Input source: URL vs file or classpath resource with fallback；Error handling: throws IOException vs prints messages and calls System.exit；B includes debug print statements and exit on failure; A does not
- 修正建议: Train with more examples where core logic is similar but wrappers differ；Incorporate data flow or control flow analysis to detect the read-accumulate pattern；Use contrastive learning to emphasize functional similarity over lexical overlap

### case_id=199 FN partial_functionality

- 方法: `runInternal` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Downloads and parses OPDS catalog data from a URL, handling pagination and progress updates.
- B 摘要: Reads configuration strings and a file to initialize character sets and mappings for Tibetan transliteration.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on low token overlap (Jaccard 0.108) and no shared API calls, leading to a non-clone prediction, but missed the broad functional similarity of loading and organizing data into collections.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled them as clones based on superficial structural resemblance: both have multiple while loops, tokenization, and conditional checks for data loading, despite different domains.
- 共享行为: Both populate HashSet and HashMap data structures with parsed tokens.
- 行为差异: Function A involves network I/O, HTTP connection, and XML parsing; Function B only reads local strings and a file.；Function A handles pagination and progress callbacks; Function B is a static initialization without network or GUI interactions.；Domain and purpose are completely different: OPDS catalog reading vs. Tibetan character set initialization.
- 修正建议: Incorporate functional semantics via fine-tuning on tasks like code summarization.；Use graph-based representations that capture data flow and control flow similarities.

### case_id=200 FP boilerplate_overlap

- 方法: `setBundleInfoName` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a URL to update bundle names in a list of BundleInfo objects based on key-value pairs, returning success status.
- B 摘要: Checks for available upgrades by querying a remote server, processing license and upgrade data, and updating UI and database accordingly; throws Exception.
- 静态失败原因: The model likely focused on shared token patterns (URL, BufferedReader, InputStreamReader, readLine) and boilerplate I/O code, overlooking the fundamentally different core logic and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions serve entirely different purposes and have minimal functional overlap beyond trivial I/O patterns.
- 共享行为: Both read from a URL using BufferedReader and InputStreamReader；Both process lines read from the input stream
- 行为差异: Function A only sets bundle names; Function B performs database operations, UI updates, and complex license/upgrade logic；Function A returns boolean; Function B returns void and throws Exception；Function A has simple key-value parsing; Function B has complex XML-like response parsing and conditional branching
- 修正建议: Incorporate data flow analysis to capture distinct post-read operations；Add method-level context or purpose classification to distinguish boilerplate from core functionality

### case_id=201 FN partial_functionality

- 方法: `runInternal` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs paginated OPDS catalog parsing, downloading book entries, handling HTTP redirects and errors.
- B 摘要: Registers a User object, creates a phpBB forum user via HTTP, persists the user, and sends a confirmation email.
- 静态失败原因: Static BERT model likely focused on structural clues like URLConnection and loop constructs, but missed the semantic divergence in core task, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled them as clones due to superficial similarity in network I/O patterns and exception handling, but this is overly broad and not indicative of functional equivalence.
- 共享行为: Both use URLConnection for HTTP requests；Both handle IOException with logging
- 行为差异: Entirely different domain and purpose (catalog reading vs user registration)；Different control flow (do-while pagination vs single request)；Different data manipulation (parsing OPDS entries vs persisting User entity)
- 修正建议: Use task-specific or multi-task learning to capture overall intent；Incorporate dataflow analysis to distinguish input/output transformations；Train on more diverse negative examples to avoid over-attending to common API usage

### case_id=202 FP lexical_or_api_overlap

- 方法: `retrieveQ` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads entire content from a URL and returns it as a string.
- B 摘要: Parses YouTube page to extract video_id and t to construct video download URL.
- 静态失败原因: The static model likely over-relied on structural similarities (URL connection, BufferedReader, while loop) and ignored the critical semantic differences in the data processing and output. Token Jaccard is low (0.228), but the model may have attended to common API sequences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the two functions have distinct purposes: generic HTTP retrieval vs. specific YouTube URL construction. Only boilerplate I/O code overlaps; the core business logic is different.
- 共享行为: Both open a URL connection and read lines from the input stream using BufferedReader.
- 行为差异: Function A returns the entire content as a string; Function B searches for a specific line containing 'fullscreenUrl' and extracts parameters.；Function B includes progress bar updates and debug prints; Function A prints the HTTP response message.
- 修正建议: Include AST-based differencing to detect variable usage and logic flow.；Incorporate data flow analysis to track how input is transformed to output.；Use contrastive learning with hard negatives that share API but differ in core logic.

### case_id=203 FP boilerplate_overlap

- 方法: `readZoneIDs` vs `importRoles`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads integers from a classpath resource file and returns them as a HashSet.
- B 摘要: Reads XML from a URL, parses role name elements, and returns a list of RoleName objects.
- 静态失败原因: The high overlap in boilerplate code (URL, InputStreamReader, while loop, readLine, try-catch) and similar structural patterns misled the model into ignoring the semantically different core logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functional similarity beyond boilerplate; these functions solve completely different tasks (reading integer IDs vs importing XML roles), so they are classified as non-clones.
- 共享行为: Both read text line by line from a stream (URL or resource)；Both parse each line or accumulated lines into data objects；Both collect parsed results into a collection (HashSet/ArrayList)
- 行为差异: Input source: classpath resource (A) vs URL (B)；Output type: HashSet<Integer> (A) vs ArrayList<RoleName> (B)；Parsing logic: simple integer parsing (A) vs XML tag detection and delegation to ProfileParser (B)；Error handling: generic Exception catch with printStackTrace (A) vs specific exception catches with empty bodies (B)
- 修正建议: Incorporate dataflow analysis to track how input lines are transformed into output objects；Use AST depth or language model embeddings that focus on non-boilerplate tokens；Add training examples that differentiate similar IO patterns with different business logic

### case_id=204 FP boilerplate_overlap

- 方法: `populateResources` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads template resources and default images from URLs based on locale and saves them.
- B 摘要: Imports biological sequences (names and sequences) from a URL using an ImportHelper.
- 静态失败原因: The static model likely focused on overlapping tokens like 'try', 'catch', 'MalformedURLException', 'IOException', 'InputStream', 'URL', and generic structure, missing the fundamental semantic difference in task objectives.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because functions have entirely different purposes and domains, despite sharing some I/O exception handling patterns.
- 共享行为: Both use try-catch for MalformedURLException and IOException；Both read from an InputStream obtained from a URL
- 行为差异: A processes XML/txt templates; B processes sequence data；A saves Resource and Image objects; B stores strings in lists；A deals with locale-specific resources; B deals with user-selected URL
- 修正建议: Improve training data to include more diverse examples with similar boilerplate but different semantics；Incorporate dataflow or control-flow analysis to detect mismatched high-level operations

### case_id=205 FN partial_functionality

- 方法: `getEncoding` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads HTTP response headers and body to detect character encoding.
- B 摘要: Fetches structured data from a URL by reading lines and parsing them into version, URL, and additional information.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed due to low lexical overlap and different control structures, leading to low embedding similarity, causing a false negative. The model focused on surface-level tokens like 'BufferedReader' and 'IOException' but not enough to overcome differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered both as achieving the goal of retrieving information from a URL over HTTP, thus partially similar functionality (Type-4 clone). However, the specific purposes are quite different.
- 共享行为: Both open a URL connection and read lines using BufferedReader；Both handle IOException and close resources in finally；Both iterate over lines from the stream
- 行为差异: A specifically searches for charset encoding in headers and body, while B parses lines based on position；A returns a String encoding, B updates instance fields and notifies listeners；A has more complex logic for content-type header parsing, B has specific error handling with user-friendly messages
- 修正建议: Train model with more Type-4 examples that share only partial functionality；Incorporate functional role of methods (e.g., using source code summarization) to capture high-level intent

### case_id=206 FN partial_functionality

- 方法: `run` vs `runScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a resource from classpath and sets it as text in a Swing panel.
- B 摘要: Reads a script file from a URL and returns its content as a string.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token similarity and structure, but these functions have low token Jaccard (0.16) and different control flow (while loop vs do-while) and different API usage (BufferedReader vs BufferedInputStream), leading to low embedding similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both belong to the category 'read from URL and accumulate data', a common utility functionality, ignoring differences in line separator handling and output mechanism.
- 共享行为: Both read from a URL and accumulate the content into a string-like buffer；Both handle exceptions by catching Exception
- 行为差异: A adds line separators (\r\n) after each line; B does not；A updates GUI component; B returns the string；A uses BufferedReader for line-by-line reading; B uses byte-by-byte reading；A's URL is obtained from class loader; B's URL is relative to applet codebase
- 修正建议: Train models to recognize higher-level semantic patterns like 'reading from a URL' even when implementation details differ；Use dataflow or IO-based features to capture common behaviors；Augment training with Type-4 clone examples where only functionality matches

### case_id=207 FP boilerplate_overlap

- 方法: `getVersion` vs `getNetworkServersIPs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Connects to a hardcoded URL and returns the last line read as a version string.
- B 摘要: Connects to a parameter-provided URL and extracts IP addresses from lines after the '!SERVERS' marker, ignoring lines starting with ';'.
- 静态失败原因: Static models like BERT or GraphCodeBERT may over-rely on surface-level common tokens (URL, BufferedReader, while loop) and method naming pattern ('get*'), ignoring the divergent logic inside the loop. The model may have been misled by the identical I/O setup and exception handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions have completely different purposes and outputs despite sharing boilerplate I/O code. BCB's broad Type-3/4 still requires functional similarity, which is absent here.
- 共享行为: Both open a URL connection, read lines with BufferedReader, and close the stream.；Both have try-catch exception handling around I/O operations.
- 行为差异: Function A uses a hardcoded URL; function B takes a URL parameter.；Function A returns the last line as a single string; function B returns a Vector of IPs parsed from specific lines.；Function A ignores all line content except the last; function B uses a state machine to filter and parse lines.；Different exception handling: A catches generic Exception and returns null; B catches specific I/O exceptions and prints stack trace.
- 修正建议: Include data-flow analysis to compare how line contents are processed inside the while loop.；Use program slicing to isolate core functional behavior from boilerplate.；Consider output type and method signature more carefully.；Train on more diverse examples where boilerplate is shared but semantics differ.

### case_id=208 FP lexical_or_api_overlap

- 方法: `readReferenceText` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads reference text from a file specified by an identifier and returns the entire content as a string.
- B 摘要: Reads a service configuration file to locate and instantiate a FrameworkFactory via reflection.
- 静态失败原因: High lexical overlap (e.g., BufferedReader, readLine, URL, InputStream) and similar loop structure mislead the model into focusing on surface-level boilerplate code.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically considers functional equivalence; the two functions have different purposes and outputs, so they are not clones even under broad Type-3/4 criteria because the core logic differs significantly.
- 共享行为: Both open a resource using URL and openStream.；Both create a BufferedReader to read lines.；Both use a while loop to read lines until null.
- 行为差异: Function A concatenates all lines into a single string; Function B processes each line to find a non-comment line and instantiate a class.；Function A returns a String; Function B returns a FrameworkFactory.；Function A handles different exceptions (MalformedURLException, UnsupportedEncodingException, IOException) separately; Function B throws Exception and uses a finally block to close the reader.；Function A appends newline characters between lines; Function B trims lines and ignores comments.
- 修正建议: Incorporate dataflow analysis to track how input data is transformed and the final output type.；Use AST or program dependence graphs to capture structural differences in control flow and data dependencies.；Add contrastive training examples with similar boilerplate but different core logic.

### case_id=209 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `transferWSDL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Event handler for saving various application preferences from a settings dialog, using file choosers and UI updates.
- B 摘要: Downloads a WSDL file from a URL with authentication and saves it to a local temporary file, returning the file path.
- 静态失败原因: The static BERT model likely overestimated the importance of common API tokens (File, InputStream, String, etc.) and overlooked the distinct semantics. The low token Jaccard (0.1067) suggests limited lexical overlap, but the model may have been misled by a few shared symbols or the length of function A.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they have completely different functionality and purpose. The only similarity is generic Java file handling, which is insufficient for Type-3/4 clone status.
- 共享行为: Both involve handling of files (saving/loading)；Both use Java I/O classes (File, input/output streams)；Both have try-catch blocks for exception handling
- 行为差异: Function A is a UI event handler (actionPerformed) dealing with user interaction and preference storage; Function B is a utility method for network download and file writing.；Function A has a void return type; Function B returns a String (file path).；Function A uses multiple conditional branches (if-else on command strings); Function B follows a sequential control flow for HTTP connection and file output.；Function A interacts with external objects (owner, Suku.kontroller, graphVizPath, etc.); Function B uses only local variables and passed parameters.
- 修正建议: Incorporate structural or dataflow analysis to differentiate UI event handlers from data processing utilities.；Improve training data with more diverse examples of non-clones that share only shallow API usage.；Use techniques like control flow graph or program dependency graph to capture semantic differences.

### case_id=210 FN benchmark_preference_bias

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL, unzips its contents, and extracts each entry to the file system.
- B 摘要: Copies a file from a source File to a destination File using NIO FileChannel.
- 静态失败原因: The static BERT model likely failed because it relies on lexical and syntactic overlap, and these two functions share low token Jaccard (0.159) and have different APIs and control flows, causing the model to miss the broad functional similarity that BCB annotators favored.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider them clones due to both being file I/O utilities that involve reading from a source and writing to a destination, representing a broad Type-4 semantic similarity.
- 共享行为: Both perform file I/O operations (reading from a source and writing to a destination).
- 行为差异: A reads from a network URL and unzips; B reads from a local file.；A extracts multiple files; B copies a single file.；A outputs files named by zip entry; B outputs to a specified File.；A prints progress information; B does not.
- 修正建议: Train the model on a dataset with more Type-3/Type-4 clone examples to capture broad functional similarity.；Incorporate graph-based representations like data flow graphs that highlight I/O operations.；Use a contrastive learning objective that rewards similarity based on functionality rather than exact syntax.

### case_id=211 FN lexical_or_api_overlap

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file using FileChannel transfer.
- B 摘要: Builds a site for editing by reading XML, applying transformations, and writing output files.
- 静态失败原因: Static BERT models may rely on lexical overlap and API call similarity (FileInputStream, FileOutputStream, etc.), causing false positive confidence.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled as clone due to both using FileInputStream and FileOutputStream for file operations, and perhaps a broad interpretation of 'file processing'.
- 共享行为: Both involve file I/O (reading/writing files)
- 行为差异: Different purposes: copy vs. build site；A is simple, B is complex with many steps；A uses FileChannel, B uses FileReader/Writer and XML processing；B has many parameters and exception types, A has none
- 修正建议: Incorporate structural understanding beyond API calls；Use dataflow analysis to capture different control flows；Increase sensitivity to method length and complexity

### case_id=212 FP boilerplate_overlap

- 方法: `getUser` vs `postRequest`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves a user by login from a database or a configuration file, parsing colon-separated fields.
- B 摘要: Sends an HTTP POST request with form data from a HashMap and returns the response body.
- 静态失败原因: Static models often rely on token overlap and structural patterns. Both functions use URL, BufferedReader, try-catch, and printStackTrace, leading to moderate Jaccard similarity. The model likely over-emphasized these common API usages and missed the entirely different business logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions perform fundamentally different tasks, even if they share some boilerplate code. Here, the two functions have no semantic overlap in purpose.
- 共享行为: Uses Java I/O to read from a URL connection；Handles exceptions by printing stack trace and returning null；Contains try-catch blocks with similar structure
- 行为差异: A reads from a local config file; B writes to and reads from a remote URL；A parses colon-delimited tokens; B encodes key-value pairs into form data；A returns a User object; B returns a String；A may persist data to a DAO; B does not persist data
- 修正建议: Incorporate semantic analysis, e.g., using a model that captures method names and variable types.；Use dataflow or program dependence graphs to differentiate between local file reading and network communication.；Increase training weight on unique or task-specific tokens.；Add a filter to detect pure boilerplate overlap vs. semantic similarity.

### case_id=213 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a specific message in a locale-specific properties file, copying the English file first if it doesn't exist.
- B 摘要: Copies a file from source to destination using FileChannel.
- 静态失败原因: Low token similarity (Jaccard 0.07) and different method names/parameters confused the model; it could not infer the file copy sub-task from the complex A code.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered the file copy sub-task in A as functionally similar to B, thus labeling them as a Type-3/Type-4 clone despite overall difference.
- 共享行为: Both perform file copying: A copies an English properties file to a locale-specific file if not already present, B copies any file.
- 行为差异: A includes reading, parsing, and modifying properties content, while B only copies bytes.；A handles localization and message replacement, B is a generic file copy utility.；A uses InputStream/Reader and Writer, B uses FileChannel for efficient file copy.
- 修正建议: Use data-flow analysis to detect file I/O operations and match them across functions.；Train on sub-task level clone detection using program slicing.；Incorporate structural similarity of nested operations.

### case_id=214 FN partial_functionality

- 方法: `main` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a hardcoded URL and extracts its zip entries to files.
- B 摘要: Parses command-line arguments to convert an input file to an output file using HTML entity decoding.
- 静态失败原因: Static BERT models rely on lexical/structural overlap, which is low (token Jaccard=0.2). The different API calls (URL vs CmdLineParser, ZipInputStream vs InputStreamReader) and distinct command-line parsing logic cause the model to miss the high-level semantic equivalence.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers them clones because both implement a data transfer pipeline (read→process→write) with similar I/O boilerplate and exception handling, which matches their broad Type-4 semantic similarity criteria.
- 共享行为: Both are public static void main methods；Both handle exceptions；Both read from an input stream and write to an output stream；Both use buffered I/O and close resources
- 行为差异: A has a hardcoded URL source; B uses command-line arguments；A extracts a zip archive; B reads a text file with HTML decoding；A writes multiple files (zip entries); B writes a single output file；A uses ZipInputStream, B uses InputStreamReader and HtmlEntityDecoderReader
- 修正建议: Enhance model with dataflow and control-flow analysis；Use contrastive learning on program intent rather than surface form；Incorporate abstract execution traces or high-level I/O patterns

### case_id=215 FN partial_functionality

- 方法: `runInternal` vs `getPagina`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches an OPDS catalog or downloads a book from a URL, handling HTTP connections, redirects, pagination, and progress.
- B 摘要: Fetches the content of a URL as a string, with basic error handling.
- 静态失败原因: Function A is long and complex with low token overlap (0.078) with B. Static models like CodeBERT may not capture the high-level semantic similarity of URL fetching without execution context, focusing instead on token differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label it a clone because both functions share the core functionality of downloading content from a URL, and the annotators considered this as a Type-4 (semantic) clone despite differences in complexity.
- 共享行为: Both open a URL and read from the HTTP response.；Both handle exceptions.
- 行为差异: A handles OPDS-specific parsing, pagination, and progress; B just reads lines.；A sets many connection properties; B uses default.；A uses callbacks; B returns a string.；A handles redirects, content-disposition, content types; B does not.
- 修正建议: Improve model's ability to infer high-level intent from API usage (e.g., recognizing URL.openStream() and HttpURLConnection usage as similar).；Use dataflow analysis to track URL input and reading of response.；Incorporate functional context (method name, purpose).

### case_id=216 FP lexical_or_api_overlap

- 方法: `run` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Copies a file from input to output with optional diagnostic byte counting.
- B 摘要: Parses string constants and a configuration file to populate data structures for Tibetan transliteration.
- 静态失败原因: Static BERT may have been mislead by low-level API overlap (both use file I/O), long code lengths, or the presence of anonymous inner classes in A that resemble setup code in B, despite no semantic similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label non-clone because the functions have entirely different purposes: one is generic I/O pumping, the other is domain-specific initialization.
- 共享行为: Both perform some form of input reading
- 行为差异: Function A is a file copying pump; Function B is a configuration parser initializing multiple maps and sets；Function A uses diagnostic counters; Function B builds lookup tables；Function A writes output; Function B only reads and populates internal structures
- 修正建议: Incorporate dataflow analysis to distinguish read/write patterns；Use method signatures and class context to disambiguate；Train on more diverse non-clone pairs with low token overlap

### case_id=217 FN benchmark_preference_bias

- 方法: `encodeFileToFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Encodes an input file to an output file using Base64, returns success.
- B 摘要: Launches a NexOpen project configuration, modifying POM files and properties.
- 静态失败原因: Static BERT/GraphCodeBERT methods rely on lexical and structural similarity; low token Jaccard (0.0667) and different method names/domains led to correct non-clone prediction, but BCB expected a clone.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this as a clone based on very broad I/O and exception handling patterns, but the overall functionality is entirely different.
- 共享行为: Both use Java I/O streams；Both handle exceptions with try-catch
- 行为差异: Function A is a simple file encoding; Function B is a complex project setup；A returns boolean; B is void and can throw CoreException；A uses Base64; B uses Maven POM and Hibernate dialect；B includes scheduling jobs and setting persistent properties
- 修正建议: Improve BCB annotation guidelines to avoid overly broad clone labels；Use domain-specific knowledge to filter out unrelated I/O patterns

### case_id=218 FN benchmark_preference_bias

- 方法: `execute` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Saves a HomeMap object with a description and copies an uploaded image file to a directory named by the map's ID, then returns the result of a list() method.
- B 摘要: Builds an editable website site by reading XML page data, transforming it with XSLT, and writing the output to files, handling various configuration properties and file paths.
- 静态失败原因: The static BERT/GraphCodeBERT method predicted non-clone (0) because the token Jaccard similarity is very low (0.036) and the code structures are vastly different. The model correctly identified they are not clones, but BCB's label indicates a false negative in the sense that the model missed a clone that only exists under a very lenient definition. The static model likely relied on surface-level features and did not capture any vague similarity in overall purpose.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone due to both functions involving file I/O and exception handling, possibly considering them as Type-4 (semantic) clones because they both copy or write data to files. However, this interpretation is overly broad and not typical of BCB's usual standards.
- 共享行为: Both functions perform file I/O operations (reading/writing files) and handle IOExceptions.
- 行为差异: Function A is a simple upload and save operation, while B is a complex multi-step site generation process.；Function A uses a single file input and output, whereas B processes multiple pages with loops and transformations.；Function A returns a string from list(), while B is void and throws several exceptions.；Function A has no loops or conditional logic; B has loops, if-else blocks, and error handling for multiple exceptions.
- 修正建议: Re-annotate the pair in BCB to reflect the lack of functional similarity, considering only clear semantic clones.；If the intent is to detect broad clones, then require additional contextual information or task-level metadata to justify such high-level similarity.

### case_id=219 FN partial_functionality

- 方法: `CheckUrl` vs `getXML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens a URL connection and returns the first line of the response.
- B 摘要: Encodes a request, constructs a URL, fetches all lines of the response, and returns them as a single string.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token overlap and surface-level patterns; the low Jaccard similarity (0.318), different method names, and different control flow (single read vs while loop) caused the model to miss the underlying semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers these clones because both methods perform the core task of fetching HTTP content from a URL and returning it as a string, which is a Type-4 (semantic) similarity despite differences in parameters and exact reading logic.
- 共享行为: Both fetch content from a URL using HTTP connection；Both use BufferedReader to read the response；Both return the fetched content as a string
- 行为差异: CheckUrl takes one parameter (URL) while getXML takes two (servletURL and request) and encodes the request；CheckUrl reads only the first line; getXML reads all lines using a while loop；CheckUrl returns the raw line; getXML returns concatenated lines；Error handling differs: CheckUrl prints stack trace and returns empty string; getXML returns null for specific exceptions
- 修正建议: Train with more diverse examples of URL fetching patterns；Incorporate data flow information to capture common I/O operations；Use graph neural networks that model API call sequences more abstractly；Apply data augmentation to vary method names and parameter styles

### case_id=220 FN partial_functionality

- 方法: `read` vs `getXML`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file or URL by name, opens a stream, delegates to an internal read method, and returns a status code.
- B 摘要: Constructs a URL from servlet URL and request parameters, opens a BufferedReader, reads lines into a StringBuffer, and returns the concatenated string or null on error.
- 静态失败原因: The low token Jaccard (0.23) indicates significant lexical differences, such as different method names, return types, and string operations. The model likely failed to abstract away these differences and recognize the shared URL-reading pattern, which is a common blind spot for static models that rely on token similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers these as clones because they share the core pattern of opening a URL connection, reading input, and handling exceptions, despite differences in return type and specific read operations. This is typical of Type-3/Type-4 clones where partial functionality overlap is accepted.
- 共享行为: Both open a URL stream using URL and openStream()；Both handle IOException with try-catch；Both involve reading data from a network resource
- 行为差异: Function A can also read local files; Function B only reads from URLs；Function A returns an integer status; Function B returns a String；Function A delegates reading to another method; Function B reads lines itself；Function B uses BufferedReader and reads line by line; Function A uses BufferedInputStream
- 修正建议: Use graph-based or AST-based representations that capture structural patterns like URL open-and-read independently of method names.；Incorporate API usage embeddings to recognize common I/O patterns.；Train with contrastive learning to focus on semantic rather than lexical similarity.

### case_id=221 FP lexical_or_api_overlap

- 方法: `readTwitterFead` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a Twitter feed from a hardcoded URL using HttpClient and returns the content as a string.
- B 摘要: Performs a version check by fetching a file from a configurable URL, parsing version/build numbers, and showing a UI dialog.
- 静态失败原因: The model likely overemphasized lexical and structural similarities: both use BufferedReader, while-read loop, try-catch for IOException, and similar variable names (line, builder/version). It failed to capture the deeper semantic differences in purpose and data processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clones because the overall functionality differs: one is a generic HTTP reader for Twitter data, the other is a version checker with specific parsing and UI feedback. Even though both read from a URL, the intent and output are distinct.
- 共享行为: Both open an HTTP connection to a URL；Both read the response line by line using BufferedReader；Both handle IOException
- 行为差异: A uses HttpClient and HttpGet, B uses URL.openStream；A returns a string, B is void and interacts with UI；A has a hardcoded URL, B gets URL from a property；A appends all lines to a builder, B parses specific prefixes
- 修正建议: Incorporate data flow analysis to distinguish output usage；Add context about API usage (HttpClient vs URL.openStream)；Use call graph or method role information

### case_id=222 FP lexical_or_api_overlap

- 方法: `GetResponse` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches HTTP response content from a given URL and returns it as a string, with a bug that prepends 'null'.
- B 摘要: Performs a Google image search by constructing a URL, parsing HTML to extract image URLs, and updating a GUI with the first image.
- 静态失败原因: The static model likely over-relied on lexical overlap from common HTTP GET patterns (HttpURLConnection, BufferedReader, while loop) and missed the deeper semantic differences in input/output types, side effects, and overall functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the functions have completely different purposes (raw HTTP response vs. image search with GUI update) despite sharing low-level HTTP GET boilerplate.
- 共享行为: Both perform an HTTP GET request and read the response line by line.
- 行为差异: Function A returns raw response content (string) with null prepended; Function B is void and parses HTML to extract image URLs.；Function A only reads if response code is 200; Function B reads regardless of response code.；Function A has no side effects; Function B modifies global state (googleImages list) and updates UI components.；Function A handles specific exceptions (MalformedURLException, IOException) silently; Function B catches generic Exception and shows error dialog.
- 修正建议: Improve training to focus on overall function purpose rather than just API calls.；Incorporate control-flow and data-flow analysis to detect differences in input/output and side effects.；Use negative sampling to distinguish similar-looking but semantically different code.

### case_id=223 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `testTrainingBackprop`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Modifies a properties file to update or add a message for a given locale.
- B 摘要: Trains a feedforward neural network on XOR data using backpropagation.
- 静态失败原因: The static model correctly identified the low token overlap and distinct API usage, predicting non-clone, which is consistent with the lack of functional similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB annotators may have mistakenly considered both as involving file reading and data processing, but the tasks are fundamentally different in purpose and implementation.
- 行为差异: Different domains: localization vs machine learning；Different I/O patterns: A reads and writes properties; B reads training data, trains network, and asserts error；Different libraries and APIs used
- 修正建议: Remove noisy BCB labels that are false positives；Improve annotation guidelines to avoid over-generalizing clones across unrelated domains

### case_id=224 FP long_range_semantics

- 方法: `main` vs `WebmillDeploy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Parses command-line arguments, reads a Prolog file, parses it, generates adapter classes, and writes them into a JAR file.
- B 摘要: Processes a WAR file by reading XML configuration files, rewriting them, and producing a new WAR file.
- 静态失败原因: Static models may be misled by common API usage (File, JarFile, JarOutputStream) and control flow (while loops, try-finally) without understanding the distinct application logic.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically labels as non-clone when two functions solve entirely different problems, even if they share some common boilerplate patterns.
- 共享行为: Both perform file I/O and resource cleanup；Both use try-catch-finally for exception handling；Both output status messages to console
- 行为差异: Different purpose: adapter generation vs. web application deployment；Different input/output: Prolog file to JAR vs. WAR to WAR；Different processing logic: Prolog parser and adapter generation vs. XML parsing and rewriting
- 修正建议: Improve training data with more diverse non-clone examples；Incorporate task-specific features or application domain information；Use a model that captures global function semantics, such as data flow or control flow graphs

### case_id=225 FN lexical_or_api_overlap

- 方法: `encodeFileToFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Encodes a file to Base64 format and writes to another file.
- B 摘要: Downloads a ZIP file from a URL and extracts its entries to the current directory.
- 静态失败原因: Static BERT models often rely on lexical overlap and API call names. Here, the token Jaccard similarity is low (0.22619), and the key API names differ (Base64 vs ZipInputStream, FileInputStream vs URL). The model missed the structural similarity because of low lexical overlap and different method signatures.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considers this a clone due to the shared structural pattern of reading from an input stream and writing to an output stream with a buffer loop, which is a common I/O boilerplate in Java (Type-3/Type-4 clone). The exact functionality may differ, but the core data transfer structure is similar.
- 共享行为: Both use buffered I/O streams to read from an input source and write to an output file in a loop with a byte buffer.；Both have similar boilerplate for stream handling (try-catch-finally, close streams).
- 行为差异: Function A performs Base64 encoding during reading, while Function B performs ZIP decompression.；Function A returns a boolean success indicator; Function B is void and is the main method.；Function A uses Base64.InputStream wrapper; Function B uses ZipInputStream.；Function A uses local file paths; Function B uses a specific HTTP URL.
- 修正建议: Incorporate control flow graph or data flow features to capture structural patterns.；Use graph-based models like GraphCodeBERT that can capture code structure beyond token overlap.；Augment training with more Type-3/Type-4 clone pairs that have low lexical but high structural similarity.

### case_id=226 FN partial_functionality

- 方法: `runInternal` vs `addQDInformation`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches and parses an OPDS catalog from a URL, handles pagination, and downloads books.
- B 摘要: Reads and parses QD information from a local file or remote URL, updating project data.
- 静态失败原因: Low token Jaccard similarity (0.139) and high lexical divergence (domain-specific terms like OPDS, CoolReader vs qdinfo, projectNum) caused the model to miss the structural similarity of opening a connection, reading lines, and parsing.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels these as clones because both perform I/O reading from a URL/file, iterate over lines, parse key-value data, and handle exceptions, fitting a broad Type-4 clone category of 'data reading and parsing'.
- 共享行为: Both open a connection to a URL or file to read data；Both read line by line using a BufferedReader；Both parse lines to extract specific fields；Both handle IOException exceptions
- 行为差异: A uses HttpURLConnection with custom headers; B uses FileReader or URL.openStream；A parses OPDS XML/Atom feeds; B parses custom line format with 'pg ' and 'pt ' prefixes；A implements pagination loop; B does not；A calls callback onFinish; B updates internal state (_qdValue, _qdDate)
- 修正建议: Use dataflow-aware models (e.g., GraphCodeBERT with dataflow edges) to capture structural patterns；Incorporate AST or control flow graph features to abstract common I/O and parsing patterns；Train with contrastive learning on function pairs that share partial functionality；Add more training examples of cross-domain I/O functions to improve generalization

### case_id=227 FN partial_functionality

- 方法: `invoke` vs `readURL`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Makes an HTTP POST request to a service, handles retries, and returns parsed JSON response.
- B 摘要: Reads a URL's content line by line and prints each line to standard output.
- 静态失败原因: The static BERT model likely relied on lexical overlap and method signatures, which are very different (e.g., 'invoke' vs 'readURL', low token Jaccard). It failed to recognize the shared I/O substructure.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a Type-4 clone because both functions share the common pattern of reading from a URL line-by-line, despite different overall purposes and additional complexity.
- 共享行为: Both open a URL and read its content line by line using BufferedReader；Both close input streams and readers after use
- 行为差异: Function A uses HTTP POST with headers and entity; B uses URL.openStream()；Function A checks HTTP status code and throws exception; B does not；Function A returns a deserialized object; B returns void；Function A has retry logic and service discovery; B does not
- 修正建议: Use a model that incorporates code structure (e.g., AST or dataflow) to detect common subpatterns；Normalize variable names and method names to reduce surface differences；Train on more examples of partial functionality clones

### case_id=228 FP lexical_or_api_overlap

- 方法: `run` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads from a URL, parses lines into version, url, and remaining information, handles network errors, and notifies listeners.
- B 摘要: Reads a configuration file from classpath to instantiate an OSGi framework factory class.
- 静态失败原因: A static BERT model may have over-weighted the lexical overlap of URL, BufferedReader, readLine, try-catch-finally, and close, while missing the distinct semantic intents.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they have different method signatures, different purposes, and only share common I/O boilerplate. The high-level functionality is completely unrelated.
- 共享行为: Both use URL to open an input stream；Both use BufferedReader and readLine()；Both handle exceptions and close streams
- 行为差异: A reads from a remote URL; B reads from a local classpath resource；A parses lines into multiple instance fields; B searches for a single class name；A notifies listeners on completion; B returns an instance or throws exception；A has localized error handling with French messages; B throws generic Exception
- 修正建议: Improve model to distinguish boilerplate from core logic；Use control-flow and data-flow features to capture different dependencies；Incorporate type information and method signatures to enforce different return types

### case_id=229 FN partial_functionality

- 方法: `getEncoding` vs `startScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads HTTP response headers and body to extract character encoding from a URL, returning the encoding or a default.
- B 摘要: Reads a script from a URL source attribute and appends its content to a dialog script buffer.
- 静态失败原因: The static BERT model likely focused on different method names, API usage (URLConnection vs. URL.openStream), and output behavior, missing the structural similarity of URL reading loops.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers them clones due to the shared pattern of reading from a URL line-by-line, which is a common I/O idiom, despite different purposes.
- 共享行为: Both open a URL and read from it using BufferedReader/InputStreamReader；Both read lines in a loop
- 行为差异: A extracts charset from headers and body; B simply concatenates all lines；A returns a String; B is void and modifies dialog.script；A uses URLConnection and header inspection; B uses direct URL.openStream()；A has specific exception handling without exit; B catches IOException and exits
- 修正建议: Augment training data with more I/O-heavy clone pairs to emphasize structural patterns；Use graph-based features that capture data flow from URL to line reading

### case_id=230 FN partial_functionality

- 方法: `sendExceptionToServer` vs `postData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details and system info to a server via HTTP POST, then checks response for success.
- B 摘要: Posts arbitrary data to a server via HTTP POST, discarding the response.
- 静态失败原因: The low token Jaccard (0.22) and different method names led the model to focus on lexical dissimilarity. The model likely overlooked the shared HTTP POST pattern due to the high variation in data preparation and error handling. It may have failed to recognize the common API usage (URL, URLConnection, OutputStream).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may annotate these as clones because both implement the core behavior of sending data over HTTP POST. The structural similarity (create URL, open connection, setDoOutput, write, read) is considered functionally similar despite differences in parameter handling and response processing.
- 共享行为: Both perform HTTP POST requests.；Both set doOutput on URLConnection.；Both write data to the output stream.；Both read the response input stream.
- 行为差异: Function A builds a complex multipart query string; Function B uses a pre-formed data string.；Function A includes exception handling and prints success/failure; Function B throws exceptions and discards response.；Function A has multiple conditional parameters; Function B has default values for protocol, host, form.；Function A uses URLEncoder for encoding; Function B does not encode (assumes data already encoded?).
- 修正建议: Include more diverse examples of HTTP POST functions to teach models the common pattern.；Use graph-based representations that capture data and control flow similarities.；Add features for API call sequences to boost detection of functionally similar methods.

### case_id=231 FN partial_functionality

- 方法: `getFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint address, and saves it locally.
- B 摘要: Decompresses a gzip file by reading compressed input and writing uncompressed output.
- 静态失败原因: The low token overlap and different method names prevented the model from recognizing the shared pattern of stream-based file copying with transformation.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a Type-4 clone based on high-level file I/O and transformation pattern, ignoring domain-specific details.
- 共享行为: Open input and output streams；Copy data between streams；Close resources in finally block；Handle IOException
- 行为差异: Different data sources: URL vs local file；Different transformations: XML modification vs gzip decompression；Different output content: WSDL file vs decompressed file；Different error handling: custom exceptions vs print to stderr
- 修正建议: Incorporate data-flow analysis to capture input-output transformations；Use program slicing to isolate core I/O logic；Train on broader Type-4 clone pairs with low token similarity

### case_id=232 FN partial_functionality

- 方法: `sendExceptionToServer` vs `getWebByUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST with encoded parameters.
- B 摘要: Downloads a web page from a URL and saves it to a file, recursively fetching linked URLs.
- 静态失败原因: The static BERT/GraphCodeBERT model likely relied on token overlap and API-level similarity, which is low (Jaccard 0.225). It missed the abstract structural pattern of HTTP communication because the specific libraries and variable names differ significantly.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both methods perform similar high-level operations: establishing an HTTP connection, sending/receiving data, and handling I/O exceptions. The structural skeleton (URL, URLConnection, streams, try-catch) is common, and BCB often accepts broad Type-3 or partial functionality clones.
- 共享行为: Both use URL and URLConnection to open network connections.；Both set doOutput true and handle stream I/O.；Both read response using BufferedReader.；Both handle exceptions with try-catch blocks.
- 行为差异: A constructs and sends a POST request with encoded parameters, B reads and saves response content.；A reads response to check success, B writes content to file and recursively processes links.；A uses System.out.println for messages, B uses addReport and file writing.；B specifies a file path and uses PrintWriter, while A only reads response.
- 修正建议: Incorporate dataflow and control-flow graphs to capture structural patterns of HTTP operations.；Use contrastive learning with positive pairs that share abstract functionality but differ in low-level implementation.；Augment training data with more diverse Type-3/Type-4 clones to teach the model to recognize broad functional similarity.

### case_id=233 FP boilerplate_overlap

- 方法: `copy` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file from source to destination with validation checks.
- B 摘要: Main method that generates adapter classes from a Prolog file.
- 静态失败原因: Static BERT likely overfitted on common API patterns (File, IOException, try-catch) and structural similarities, ignoring semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically does not label such functionally distinct methods as clones despite some shared API usage.
- 共享行为: Both use File objects and handle IOExceptions；Both print stack traces in error handling
- 行为差异: Function A performs file copy; function B performs code generation；Function A has simple I/O loop; function B has complex parsing and class writing；Different control flow and logic
- 修正建议: Improve distinction between core logic and boilerplate code；Incorporate dataflow or control-flow features to capture semantics；Use contrastive learning to reduce false positives from common structures

### case_id=234 FP partial_functionality

- 方法: `readZoneIDs` vs `retrieveTemplate`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a zone file from a resource URL, parses each line as an integer, and returns a set of integers.
- B 摘要: Reads a blog URL, concatenates all lines into a string, caches it, and returns the template string.
- 静态失败原因: The static BERT model likely relied on token overlap and structural similarity (both read from URL, read lines, loop) without capturing the differing return types and output semantics. The high-level pattern of URL reading and line iteration may have dominated the representation, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB typically requires functional similarity in terms of input/output behavior and purpose. Here, the purposes are distinct: one extracts numeric IDs, the other retrieves a text template. Despite similar I/O patterns, the semantics differ enough for BCB to label as non-clone (Type-4 would require same functional behavior, which they don't share).
- 共享行为: Both open a URL and read lines from an input stream.；Both use a loop to process each line from the stream.；Both return a data structure after reading input.
- 行为差异: Function A parses lines as integers and collects them into a HashSet; Function B appends lines to a StringBuilder to form a single string.；Function A catches exceptions and prints stack trace; Function B throws the exception.；Function A reads from a resource file; Function B reads from a blog URL.；Function A returns a HashSet<Integer>; Function B returns a String.
- 修正建议: Incorporate output type and purpose into the representation.；Add attention to exception handling and loop body details.；Use contrastive learning to distinguish similar patterns with different semantics.

### case_id=235 FN lexical_or_api_overlap

- 方法: `loadExistingAntlibs` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads antlib definitions from classpath resources and invokes loadAntLib for each package.
- B 摘要: Reads a file from filesystem or classpath resource and returns its content as a string.
- 静态失败原因: The static model correctly predicted non-clone due to different method names, overall structure, and low token overlap; it was not misled by surface similarities.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might consider the shared resource-reading loop as a common pattern, but the overall functionality differs significantly; the low token overlap suggests this is likely an annotation error.
- 共享行为: Read from an InputStream using BufferedReader；Iterate over lines in a loop；Handle IOException and close resources
- 行为差异: A processes lines as package names to load antlibs, B concatenates lines into a single string；A reads multiple resources, B reads a single file/resource；A writes errors to System.err, B writes to System.out and calls System.exit on failure
- 修正建议: Ensure clone annotations consider overall functionality, not just shared sub-tasks；Require higher semantic similarity for broad clone types

### case_id=236 FN benchmark_preference_bias

- 方法: `readData` vs `sendRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Parses input strings and a configuration file to populate sets and maps for character data.
- B 摘要: Establishes a compressed HTTP connection, sends XML request, and parses the XML response.
- 静态失败原因: Static BERT/GraphCodeBERT likely correctly identified the semantic difference; the low token Jaccard and different control flow patterns led to a non-clone prediction, which is accurate under strict semantics.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled it as a clone due to partial similarity in reading/processing data from input, but the specific functionality is distinct.
- 共享行为: Both methods handle I/O operations and use Java collections.
- 行为差异: Different data sources (local file vs. network)；Different purpose (initialization vs. request-response)；Different output (modifies global state vs. returns string)；Different error handling (custom errors vs. dialogs)
- 修正建议: No fix needed; the model's prediction is correct. If BCB annotation is to be matched, better to clarify clone definition to exclude such pairs.

### case_id=237 FP partial_functionality

- 方法: `getRequestContent` vs `fetchUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Opens HTTP connection, reads first line of response, returns it, throws exceptions.
- B 摘要: Opens URL stream, reads entire response into string builder, returns concatenated string, catches exceptions and returns empty string.
- 静态失败原因: Static model over-relied on lexical and structural similarity (URL, BufferedReader, readLine, return String) and missed the critical difference in the read loop vs single read, leading to false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely marks non-clone because the methods have different input/output behavior (first line vs full content) and different error handling, which constitute significant semantic divergence even though structure overlaps.
- 共享行为: Both fetch content from a URL using BufferedReader.；Both parse URL from string.；Both return a String.
- 行为差异: A reads only the first line; B reads all lines.；A uses HttpURLConnection; B uses URL.openStream().；A throws Exception; B catches exceptions and returns empty string.；A is protected; B is public static.
- 修正建议: Incorporate control-flow analysis to distinguish single read from loop.；Improve data-flow tracking to capture number of readLine calls.；Augment training data with pairs where methods differ in reading extent (one line vs all lines).

### case_id=238 FN partial_functionality

- 方法: `getResourceAsStream` vs `downloadFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a resource from a URL, caches it locally, and returns its InputStream, with HTTP caching logic.
- B 摘要: Downloads a file from S3, decrypts and decompresses it, and saves it to a target file on local disk.
- 静态失败原因: Low token Jaccard similarity (0.10), different method names, and different library APIs (e.g., URLConnection vs S3-specific) caused the model to overlook the high-level similarity in data flow.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as Type-4 clones because they both implement the high-level concept of downloading remote data and saving to local storage, despite different protocols and data transformations.
- 共享行为: Both read data from a remote source；Both write data to a local file；Both involve I/O and error handling
- 行为差异: A uses HTTP and caching; B uses S3 with decryption/decompression；A returns an InputStream; B writes to a specific file and uses temp file；A has extensive caching logic; B does not cache
- 修正建议: Use data flow analysis to capture common patterns of remote resource acquisition and local storage；Incorporate method-level semantic embeddings based on code summaries or docstrings

### case_id=239 FP lexical_or_api_overlap

- 方法: `googleImageSearch` vs `handledRun`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs a Google image search, parses image URLs from HTML, and updates UI with an album art icon.
- B 摘要: Downloads and processes an XML game data file from a URL, checks version, and updates the game database if newer.
- 静态失败原因: The model likely over-relied on lexical similarities (e.g., URL, BufferedReader, try-catch) and mistook common boilerplate for semantic equivalence.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the core functionality (image search vs. game data update) is completely different, despite sharing some I/O boilerplate.
- 共享行为: Both open HTTP connections and read input streams；Both use BufferedReader and handle exceptions；Both perform string processing on fetched data
- 行为差异: Function A parses image search result HTML; Function B parses XML for version check；Function A updates UI components; Function B updates game database files；Function A deals with image URLs; Function B deals with game data versions and file I/O
- 修正建议: Incorporate data-flow or type information to distinguish different high-level operations；Increase training data with contrasting examples where API usage is similar but semantics differ；Use longer context or structural features to capture the main intent rather than surface tokens

### case_id=240 FN benchmark_preference_bias

- 方法: `getFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads WSDL file from URL, modifies endpoint attribute, and saves locally, with error handling.
- B 摘要: Demonstrates file read/write using FileChannel and ByteBuffer with different encodings.
- 静态失败原因: Static BERT likely correctly predicted non-clone due to low token overlap and distinct control flows; the model's prediction aligns with semantic dissimilarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both using FileChannel and ByteBuffer, but overall functionality is entirely different, possibly a labeling error.
- 共享行为: Both use FileChannel for file I/O operations
- 行为差异: A performs network download and XML manipulation; B is local file I/O demonstration；A has complex error handling and logging; B has minimal exception handling；A returns a file path; B outputs to console
- 修正建议: Reassess BCB label for this pair；Consider higher threshold for file I/O similarity；Improve annotation guidelines to avoid overgeneralization

### case_id=241 FN benchmark_preference_bias

- 方法: `copy` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file character by character from source path to destination path.
- B 摘要: Builds a site for editing by processing XML, transforming strings, and writing output files for each page.
- 静态失败原因: Static BERT likely correctly predicted non-clone due to very low token Jaccard similarity (0.062) and clear structural differences. The BCB label appears to be a false positive, so the model did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled as clone due to both methods performing file I/O (read and write) with character buffers, but the functional overlap is minimal and does not constitute a broad Type-3/Type-4 clone.
- 共享行为: Both read from a file and write to a file using character streams
- 行为差异: A is a simple file copy; B involves complex XML transformation, string manipulation, multiple parameters, and page iteration；A uses FileReader/FileWriter; B uses FileInputStream, StringWriter, and custom FileSystem methods；A has no error handling beyond IOException; B handles multiple exception types and has debugging traces；A operates on two files; B operates on many files and directories
- 修正建议: Re-evaluate BCB annotation for this pair; consider it a non-clone based on distinct functionality.；If BCB requires clones to have shared file I/O, clarify annotation guidelines to avoid such false positives.

### case_id=242 FP boilerplate_overlap

- 方法: `createHTML` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Builds an HTML page from a CSS resource and database content based on a page type.
- B 摘要: Executes an HTTP POST request and returns the response body.
- 静态失败原因: Static models like GraphCodeBERT may overestimate similarity due to overlapping API calls (URL, openStream, BufferedReader) and common boilerplate patterns (try-catch-finally), despite low token Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB focuses on functional similarity, not just structural code patterns; these functions have completely different intents and logic, so they are not clones.
- 共享行为: Both use URL, InputStreamReader, BufferedReader to read data from a stream；Both have try-catch-finally error handling
- 行为差异: One generates HTML for a dashboard; the other sends an HTTP POST request；Different input parameters and output formats；A queries a database; B writes to an HTTP connection
- 修正建议: Improve training data with non-clone pairs that share boilerplate but differ semantically；Incorporate data flow analysis to distinguish different data transformations；Use semantic role labeling to capture intent

### case_id=243 FP boilerplate_overlap

- 方法: `init` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads controller classes from a registry file using servlet context.
- B 摘要: Searches Google images, parses image URLs, and updates UI components.
- 静态失败原因: Static BERT models rely on lexical and API token overlap. Both functions use similar boilerplate (URL, BufferedReader, try-catch), leading to false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functionality is completely different, even if some API usage overlaps.
- 共享行为: Use URL and BufferedReader for I/O；Handle exceptions with try-catch；Read lines from streams
- 行为差异: Different purpose: class loading vs. image search；Different input: servlet context vs. search query；Different output: class registration vs. UI update；Different domain: server-side vs. client-side
- 修正建议: Use data flow analysis to distinguish context；Incorporate domain-specific features；Train with contrastive learning on functional differences

### case_id=244 FP lexical_or_api_overlap

- 方法: `init` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Initializes a servlet by loading controller classes from a registry file on the classpath.
- B 摘要: Constructor for a Swing GUI browser that reads XML/XSLT from a URL and renders HTML.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token-level and structural patterns, and the common use of BufferedReader/InputStreamReader patterns, try-catch blocks, and similar variable names (e.g., 'url', 'inputLine') may mislead the model into predicting a clone, even though the broader context and semantics differ.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely annotate as non-clone because despite the token overlap in reading streams, the functions have completely different high-level semantic goals (servlet initialization vs. GUI browser construction) with minimal functional similarity.
- 共享行为: Both use BufferedReader and InputStreamReader to read from a URL stream.
- 行为差异: A loads Java classes dynamically; B builds a GUI and processes XML/XSLT transformations.；A uses ClassLoader and manages servlet controllers; B sets up Swing components and handles user interaction.；A outputs debugging logs; B displays HTML content in a JEditorPane.；Error handling: A logs errors via logger; B shows warning dialogs.
- 修正建议: Incorporate higher-level semantic features such as method purpose classification.；Use context-aware embeddings that capture the surrounding code structure and class-level context.；Apply dataflow analysis to differentiate between reading resources for class loading vs. for UI rendering.；Increase training data diversity for non-clones with overlapping API usage.

### case_id=245 FP boilerplate_overlap

- 方法: `handleHandshake` vs `postRequest`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles a Minecraft handshake packet by validating username and optionally making an HTTP GET to session.minecraft.net to authenticate.
- B 摘要: Makes an HTTP POST request to a given URL with a map of parameters and returns the response body.
- 静态失败原因: GraphCodeBERT likely over-relied on shared lexical tokens (URL, BufferedReader, printStackTrace) and the structural pattern of connecting, reading, and exception handling, missing the divergent higher-level intent and control flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotation (0) considers these non-clones because their core semantics differ: one is a handshake handler embedded in game logic, the other is a standalone HTTP POST utility. BCB requires more than superficial API overlap.
- 共享行为: Both open HTTP connections and read responses；Both use java.net.URL and handle exceptions with printStackTrace
- 行为差异: A uses GET method; B uses POST with output；A involves Minecraft-specific session logic and packet handling; B is a generic HTTP utility；A shuts down network on error; B returns null on error；A reads only one line; B reads all lines
- 修正建议: Incorporate data flow analysis to distinguish GET vs POST and different error handling behaviors；Use models that capture task-level semantics (e.g., handshake vs generic request) beyond code structure

### case_id=246 FN benchmark_preference_bias

- 方法: `doGet` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve, authorize, and serve a web page with logging and caching.
- B 摘要: Copies a file from source to destination using NIO FileChannel.
- 静态失败原因: The model correctly predicted non-clone (0). The BCB label is arguably incorrect, so the model did not fail but rather disagreed with a potentially erroneous benchmark label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label (1) is likely an error; the functions have no meaningful similarity. The extremely low token Jaccard (0.046) and divergent purposes suggest a misannotation in the benchmark.
- 行为差异: Completely different domain: HTTP request handling vs. file I/O；Code A includes complex logic for page lookup, user permissions, caching; Code B is a simple utility method；Different method signatures and intent
- 修正建议: Re-examine and correct the BCB annotation for this pair if it is indeed a mislabel.；Improve model robustness to handle such outliers, though in this case the model performed correctly.

### case_id=247 FN boilerplate_overlap

- 方法: `testNetworkHTTP` vs `getEncoding`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends multiple HTTP GET requests to various URLs, reads and discards all response data.
- B 摘要: Extracts character encoding from an HTTP response by examining the Content-Type header and response body.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token similarity and structural features; here token Jaccard is low (0.18). The models may not recognize the shared HTTP read pattern due to different variable names, URL strings, and control flow, especially with different return types and method signatures.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely considered these as clones because both functions follow the same pattern of HTTP connection, BufferedReader usage, and line-by-line reading—a common Type-3 boilerplate. BCB's broad annotation groups such structurally similar I/O operations.
- 共享行为: Both open an HTTP URL connection and get an input stream；Both wrap the input stream in a BufferedReader；Both read lines in a loop using readLine()；Both use try-finally or try-catch for resource management
- 行为差异: Function A performs multiple requests with different parameterized URLs; Function B processes a single connection；Function A does not return anything; Function B returns a string；Function A catches and prints IOException; Function B throws IOException；Function A disconnects the connection in finally; Function B closes the reader in finally
- 修正建议: Improve detection of common API usage patterns (e.g., HTTP read) regardless of specific strings or variable names；Use data-flow-aware models to recognize that both functions iterate over HTTP response lines；Incorporate functional similarity grouping, e.g., treating 'read HTTP response' as a shared behavior

### case_id=248 FN partial_functionality

- 方法: `read` vs `startScript`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file or URL into an internal stream and returns a status code, handling IO exceptions by setting error status.
- B 摘要: Reads a URL and appends each line to a dialog script, exiting on IO errors.
- 静态失败原因: Low token overlap (0.169) and different method signatures/names caused the model to miss the common URL-reading pattern. Structural differences and distinct overall purposes dominated the embedding.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as 'reading from a URL' operations, which is a common sub-functionality, and thus labels them as Type-3/4 clones despite different contexts.
- 共享行为: Both open a URL stream and read its content；Both handle IOException with error handling
- 行为差异: Method A handles both files and URLs, method B only URLs；Method A returns an int status, method B is void and modifies a dialog object；Method A reads via another read(in) method, method B reads line by line and concatenates to a string；Method B calls System.exit(0) on error, method A sets a status variable
- 修正建议: Incorporate data flow analysis to detect common sub-patterns like URL reading；Employ semantic role labeling to identify shared operations across different contexts

### case_id=249 FN benchmark_preference_bias

- 方法: `doTransfer` vs `readVersion`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Forwards HTTP request by opening a URL connection, copying headers, transferring request body, and returning response.
- B 摘要: Reads a version resource file from classpath and parses version, revision, and date strings.
- 静态失败原因: Static BERT models may rely on token overlap and structural similarity. Here, token overlap is low (0.155), and the methods have different method names and parameters, so the model correctly identified them as different. The BCB label might be an outlier.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider this a clone due to both methods using URL connections and reading lines, seen as a generic IO pattern. However, their purposes and complexity differ greatly.
- 共享行为: Both open a URL and read input using streams；Both handle IOException with printStackTrace；Both read data line by line
- 行为差异: A performs HTTP forwarding with request/response handling; B only reads a static resource；A modifies request headers and method; B parses specific key-value pairs；A has output streaming to response; B has no output；A uses both input and output streams; B only reads
- 修正建议: Improve training data consistency by reviewing BCB annotations；Add context-aware training to distinguish generic IO from specific functionalities

### case_id=250 FN partial_functionality

- 方法: `sendExceptionToServer` vs `postXml`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends an exception report to a server by building a URL-encoded string of diagnostic data, POSTs it, reads response, and prints status.
- B 摘要: POSTs an arbitrary XML string to a URL with optional SOAPAction, reads response, and returns it; throws RuntimeException on failure.
- 静态失败原因: Low token overlap (0.275) and different syntactic structures (building payload vs. direct XML) caused the model to miss the shared HTTP POST pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as 'send data via HTTP POST and handle response', viewing them as functionally similar even though payload and response handling differ.
- 共享行为: Open an HTTP URLConnection；Set doOutput to true；Write a payload string to output stream；Read response via BufferedReader
- 行为差异: A constructs URL-encoded payload from multiple parameters; B uses pre-formed XML；A does not explicitly set request method; B sets POST；A prints response/errors to console; B returns response or throws RuntimeException；A uses hardcoded server URL field; B takes url parameter
- 修正建议: Use models that capture structural patterns like HTTP request/response handling；Include control-flow and data-flow graphs to detect functional similarity beyond token overlap；Augment training data with more diverse Type-3/Type-4 clones

### case_id=251 FN partial_functionality

- 方法: `copyResource` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.65`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file byte by byte.
- B 摘要: Converts a DICOM file, including parsing, validation, metadata injection, and pixel data transformation, then writes the result.
- 静态失败原因: The static BERT/GraphCodeBERT model predicted non-clone because token overlap is extremely low (Jaccard 0.12782) and the methods differ greatly in length, structure, and vocabulary. The model failed to recognize the broad byte-copying similarity that BCB annotators might have considered as evidence of a clone.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered these clones because both functions involve copying data from an input stream to an output stream, which is a common high-level behavior. The 'copy' pattern is present in both, even though convert adds significant DICOM-specific processing. Under BCB's broad Type-4 similarity, this partial functional overlap might be deemed sufficient.
- 共享行为: Both read from an input source and write to an output file.；Both use a loop to copy bytes from input to output.
- 行为差异: copyResource simply copies all bytes; convert parses DICOM headers, validates metadata, and conditionally inflates pixel data.；convert writes structured DICOM file headers and group lengths; copyResource writes raw bytes with no structure.；convert includes multiple early returns and conditional branches; copyResource has a single straightforward flow.
- 修正建议: Increase sensitivity to Type-4 clones by focusing on shared I/O patterns rather than exact token matches.；Use program slicing to isolate common core functionality (e.g., the byte-copying loop).；Incorporate high-level semantic information, such as common use of InputStream/OutputStream.

### case_id=252 FP lexical_or_api_overlap

- 方法: `readData` vs `readAndRewrite`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses comma-separated configuration strings into various sets and hash maps for Tibetan text processing.
- B 摘要: Reads DICOM pixel data from an input file and writes it to an output file using image I/O streams.
- 静态失败原因: The static BERT/GraphCodeBERT model likely focused on the shared method name prefix 'read' and a few common tokens like 'IOException' and 'HashSet', ignoring the vast behavioral differences. The model may have also been misled by both functions having long, complex bodies with loops and conditionals, but structurally they are very different.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators likely label this as non-clone because the functionalities are completely unrelated: one initializes character sets for a text encoding system, the other copies DICOM medical images.
- 行为差异: Function A populates static sets and maps from tokenized strings; function B performs file I/O on DICOM images.；Function A is an internal data initialization routine; function B is a file conversion utility.；Function A has no file I/O (except possibly reading from fields); function B explicitly reads from and writes to files.；Function A throws Error on invalid data; function B throws IOException.
- 修正建议: Use data-flow-aware models that can distinguish between internal string parsing and external file I/O.；Include more negative examples where method names are similar but functionality differs.；Augment training with cross-project data to reduce reliance on method name similarity.

### case_id=253 FN partial_functionality

- 方法: `main` vs `copyResource`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies file from command-line source to destination using FileChannel and ByteBuffer.
- B 摘要: Copies a resource (URL or file) to a destination file using InputStream/OutputStream.
- 静态失败原因: Low token Jaccard (0.2) and different API names (FileChannel vs InputStream) cause BERT to miss the abstract functional similarity. The models rely on surface-level lexical and API overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers functional similarity at a high level: both functions copy data from one location to another, fulfilling the same core purpose despite different implementations.
- 共享行为: Both copy data from a source to a destination.
- 行为差异: Different I/O APIs: FileChannel vs InputStream/OutputStream.；One is static main method, the other is instance method.；One uses command line args, the other uses class fields.；One uses byte buffer bulk copy, the other reads byte-by-byte.
- 修正建议: Incorporate structural similarity like AST or control-flow graphs.；Use functional similarity measures based on data flow or I/O operations.；Train with more abstract representations that capture intent despite API differences.

### case_id=254 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `addQDInformation`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses HTML content from a URL to extract hyperlinks and their text, returning two vectors.
- B 摘要: Reads a configuration file (local or remote) and updates internal project information fields based on parsed lines.
- 静态失败原因: The model likely over-relied on boilerplate code overlap (BufferedReader, InputStreamReader, URL connection) and reading loop structure, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functional similarity; these functions have completely different purposes despite sharing low-level I/O patterns.
- 共享行为: Both use Java I/O to read text line by line from a stream (URL or file)；Both use BufferedReader and InputStreamReader；Both may handle URL connections
- 行为差异: A extracts hyperlinks using regex from HTML; B parses specific line prefixes ('pg ', 'pt ')；A returns extracted data in vectors; B modifies internal state；A includes time checks and absolute URL conversion; B handles file existence and exception types differently
- 修正建议: Incorporate data flow or control flow features to distinguish variable usage and output；Use AST-based differencing or semantic role labeling to reduce reliance on API sequences；Train with more negative examples that share API calls but diverge in functionality

### case_id=255 FN benchmark_preference_bias

- 方法: `setMembers` vs `httpRequestByPOST`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Parses HTML from a Trac ticket page to extract component and priority lists.
- B 摘要: Sends an HTTP POST request with parameters and returns the response body as a string.
- 静态失败原因: The model correctly identified them as non-clones due to low token overlap (0.186), different method signatures, distinct APIs (URL vs HttpClient), and divergent control flow; the 'failure' is only relative to BCB's lenient annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label them as clone because both involve HTTP communication and reading data from a URL, falling under a broad 'HTTP data retrieval' functionality category (Type-4).
- 共享行为: Both make HTTP requests to a URL.；Both read the response line by line using BufferedReader.；Both use UTF-8 encoding for text.
- 行为差异: A uses GET, B uses POST.；A parses HTML with regex to extract specific select options; B returns raw response.；A sets class member variables; B returns a string.；A only handles success; B also handles HTTP error status codes with custom error fields.
- 修正建议: Reconsider BCB annotation for this pair as it does not represent true functional similarity.；For future benchmarks, define stricter Type-4 criteria to avoid grouping generic HTTP utilities with specific scraping tasks.；Static models could be tuned to ignore superficial API similarities when overall semantics differ.

### case_id=256 FN partial_functionality

- 方法: `genCustRatingFileAndMovieIndexFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Generates customer rating and movie index files from a binary master file using file channels and byte buffers.
- B 摘要: Retrieves a resource as an InputStream with caching and HTTP conditional GET.
- 静态失败原因: Static BERT models may focus on surface-level similarities like 'File', 'InputStream', 'outC1.write', etc., but fail to capture the high-level semantic difference in purpose (data processing vs. resource retrieval). The low token overlap (0.15) suggests lexical similarity is low, but static models might still be misled by common API usage patterns.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider them clones due to shared file I/O patterns (both read from a file/stream and write to a file) and common exception handling structure, but the overall functionality is distinct.
- 共享行为: Both perform file I/O operations；Both read from a source and potentially write to a file
- 行为差异: Function A processes binary data sequentially to split into two files; Function B fetches a resource over HTTP or from cache；Function A returns boolean; Function B returns InputStream；Function A uses FileChannel and ByteBuffer; Function B uses BufferedStream and URLConnection；Function A has no caching or network; Function B has caching and network protocol handling
- 修正建议: Improve models to understand program intent beyond local API calls；Use higher-level semantic embeddings (e.g., code2seq) that capture overall purpose；Incorporate structural similarity at the level of control flow and data dependencies

### case_id=257 FN partial_functionality

- 方法: `getHTML` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a URL, optionally saves to file, and returns the HTML string.
- B 摘要: Reads camera log lines from a URL, parses them into records, sorts, and logs.
- 静态失败原因: Static models like GraphCodeBERT likely failed due to low token overlap (0.24), different method names and return types, and different API calls (HttpURLConnection vs url.openStream). The model may not capture the underlying semantic similarity of reading from a URL, focusing instead on surface-level syntax.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone because both functions share a common core: reading lines from a URL via BufferedReader. This partial functionality overlap is often accepted as a Type-4 (semantic) clone in BigCloneBench.
- 共享行为: Both open a URL and read lines of text using BufferedReader.；Both close the underlying stream/connection after reading.
- 行为差异: A returns the accumulated HTML string; B returns void and populates a list of parsed objects.；A optionally writes the content to a file; B sorts the collected records.；A uses HttpURLConnection with custom headers; B uses url.openStream() directly.；A prints stack trace on any exception; B catches specific LogParseException per line and continues.
- 修正建议: Incorporate data flow analysis to detect common I/O patterns like 'open stream, read lines, close'.；Use contrastive learning with positive examples that share partial functionality but differ in surrounding logic.；Enrich training data with more syntactic variations of URL reading patterns.

### case_id=258 FP lexical_or_api_overlap

- 方法: `getNetworkServersIPs` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a list of server IPs from a specific formatted text file over HTTP, returning a Vector of strings.
- B 摘要: Downloads a file from a URL to a temporary file with optional authentication and progress display, writing all content.
- 静态失败原因: The static model overemphasized overlapping API calls (URL, URLConnection, BufferedReader, readLine) and common code structure, ignoring distinct high-level semantics and control flow that define the true purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because their core functionality and output differ significantly; only low-level I/O patterns overlap.
- 共享行为: Both open an HTTP connection and read lines from the response using BufferedReader
- 行为差异: A parses lines for server IPs using markers and returns a vector; B writes all content to a file with authentication and UI updates；A catches exceptions and prints stack traces; B throws IOException；A reads from a string URL; B takes a URL object directly
- 修正建议: Incorporate data-flow analysis to distinguish variable usage and output transformation；Use graph-based representations that capture statement context and control flow beyond token sequences；Train on more diverse examples that penalize partial structural overlap without functional equivalence

### case_id=259 FP lexical_or_api_overlap

- 方法: `run` vs `SRWGuiClient`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A run method that fetches a tile from a data source, parses GeoJSON, extracts geometries, and adds them to a data loader.
- B 摘要: A constructor for a Swing browser that reads XML/HTML from a URL, optionally applies XSLT transformation, and displays the content in a JEditorPane.
- 静态失败原因: Static BERT/GraphCodeBERT models may have over-relied on surface-level API tokens like 'URL', 'BufferedReader', 'IOException' etc., and missed the high-level semantic differences due to limited context understanding or inadequate training on distinguishing complete structural disparity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators would not consider these clones because they have completely different purposes and implementation contexts, despite some low-level API overlap.
- 共享行为: Both use URL and BufferedReader to read from a URL；Both handle IOExceptions
- 行为差异: Function A is a tile loader that works with GeoJSON and geometries in a background thread；Function B is a GUI constructor that sets up a browser window, reads XML/HTML, and applies XSLT transformations
- 修正建议: Improve training with more negative examples that have similar API usage but different semantics；Incorporate structural or flow-level features to differentiate between different use cases；Use method-level summary or task categorization to filter obvious non-clones

### case_id=260 FP boilerplate_overlap

- 方法: `readFixString` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a fixed-length string from an input stream, copying limited bytes into a StringWriter.
- B 摘要: Handles action commands in a GUI settings dialog, setting file paths and preferences for GRAPHVIZ, IMAGEMAGICK, and other options.
- 静态失败原因: Static BERT models may over-rely on surface-level patterns like @Override, try-catch blocks, or common Java library usage (e.g., StringWriter, JFileChooser) while missing the deep semantic disconnect due to long-range dependencies and lack of context understanding.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB requires substantial functional similarity; these two methods serve entirely different purposes and share no common functionality beyond being Java methods.
- 共享行为: Both are @Override methods in some class.；Both involve some conditional logic and exception handling.
- 行为差异: Function A reads binary data from a stream; Function B processes user actions in a GUI.；Function A returns a string; Function B has void return and updates UI components.；Function A has a simple IO-focused flow; Function B has complex branching for multiple commands.；Function A uses IOUtils.copy; Function B uses JFileChooser, preferences, and UI updates.
- 修正建议: Incorporate dataflow or control-flow analysis to distinguish IO operations from UI event handling.；Use hierarchical embeddings that separate boilerplate (e.g., common Java patterns) from task-specific logic.；Augment training with negative examples that have similar syntax but different semantics.

### case_id=261 FN benchmark_preference_bias

- 方法: `getResourceAsStream` vs `displayDiffResults`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Retrieves a resource by URL with caching, returning an InputStream from either cache or network.
- B 摘要: Generates an HTML diff report file and launches a browser to display it, writing HTML content and appending binary data from a temp file.
- 静态失败原因: Static BERT/GraphCodeBERT likely correctly predicted non-clone because it learned to distinguish high-level semantics: the method names, control flow, and data dependencies are very different. The model may have captured that one is a resource getter and the other is a display function.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to superficial structural similarities (both handle file I/O, use BufferedInputStream/OutputStream, and have loops reading from streams) and the fact that both are complex methods performing multiple I/O operations, leading to a broad Type-4 (semantic) annotation despite different overall purposes.
- 共享行为: Both involve reading from an InputStream and writing to an OutputStream；Both use FileInputStream/FileOutputStream and Buffered streams；Both handle file I/O operations
- 行为差异: Function A retrieves a resource and returns an InputStream; Function B generates an HTML report and launches a browser；Function A implements caching logic and deals with HTTP connections; Function B does not；Function A has complex conditional logic for cache freshness; Function B writes fixed HTML content；Function A returns an InputStream; Function B has no return value (void)
- 修正建议: Review BCB annotation: this pair may be a false positive in BCB due to over-reliance on structural I/O similarity；Improve training data by filtering out such broad Type-4 clones that are not semantically equivalent；Use contrastive learning to emphasize functional purpose over tangential I/O patterns

### case_id=262 FN partial_functionality

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Builds an entire site for editing by reading XML and other files, applying transformations, and writing output.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token overlap and syntactic structure. The token Jaccard is extremely low (0.0628), and the method names and overall structure are completely different, leading to a low similarity score. The model fails to recognize the abstract commonality of file I/O operations.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might label it as a clone due to both functions performing file I/O operations (reading from a file and writing to a file), even though the overall functionality differs significantly. This could be considered a partial functionality similarity at a very high level.
- 共享行为: Both involve reading from files and writing to files using Java I/O.
- 行为差异: copyFile copies entire file content; buildSiteForEdit processes XML and other files, applies transformations, and writes multiple outputs.；buildSiteForEdit is much more complex with DOM operations, string replacements, and exception handling for various types.
- 修正建议: Incorporate dataflow or control-flow analysis to detect that both methods perform read and write operations.；Add training examples where functions share common low-level I/O patterns despite different high-level purposes.；Use a more fine-grained comparison of API usage patterns.

### case_id=263 FN benchmark_preference_bias

- 方法: `send` vs `getFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends an email with various parameters including headers, priority, and body, handling charset and quotas.
- B 摘要: Downloads a WSDL file from a URL, modifies the endpoint in the XML, and saves it to a temporary file.
- 静态失败原因: Static BERT model likely predicted non-clone due to low token overlap and distinct domain-specific vocabulary (email vs. WSDL download), failing to capture any high-level similarity that BCB might have intended.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as involving network operations and exception handling, but this is a weak similarity; likely a labeling error.
- 共享行为: Both involve network communication；Both use try-catch blocks for exception handling；Both write data to files or streams；Both use logging (though only B uses mLog)
- 行为差异: A sends an email message; B downloads and modifies a WSDL file；A uses JavaMail and Hibernate; B uses URL connections and XML parsing；A sets multiple email headers and addresses; B only modifies one attribute in XML；A spawns a thread for sending; B is synchronous
- 修正建议: Re-evaluate BCB label for this pair; consider removing from training set；Improve model to capture abstract semantic similarity across different application domains

### case_id=264 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `test`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a localized properties file by updating or adding a message key-value pair.
- B 摘要: Tests the StorageStringWriter class for correct write, read, and exception handling.
- 静态失败原因: Static BERT/GraphCodeBERT predicted non-clone correctly based on semantic structure, but BCB considered them clones. Actually, the model did not fail; the benchmark label is questionable. However, if we must explain model error: The model might have been misled by shared API tokens like 'FileWriter', 'IOException', but it correctly identified the lack of semantic equivalence.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled it as a clone based on superficial similarity of both methods performing text reading/writing operations with error handling, but the actual functionality is entirely different.
- 共享行为: Both perform I/O operations；Both use try-catch for exception handling；Both involve reading and writing text data
- 行为差异: A modifies a properties file for internationalization; B tests an in-memory storage writer；A uses file I/O with FileReader/FileWriter; B uses custom StorageStringWriter with InputStream/OutputStream；A has specific logic for parsing properties; B has assertions and exception tests
- 修正建议: Re-evaluate BCB annotation for this pair；Improve benchmark consistency

### case_id=265 FP boilerplate_overlap

- 方法: `get` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs an HTTP GET request, reads response lines, filters comments, decodes each line into GameRecord, returns array or null on error.
- B 摘要: Reads a service configuration file from classpath, filters comments, instantiates the class named in the first non-comment line, returns that instance or throws exception.
- 静态失败原因: Static BERT might have focused on token overlap (e.g., 'BufferedReader', 'readLine', '#', '!=', 'return') and structural patterns like try-catch and loops, ignoring the critical differences in method names, return types, and external API calls (URL vs ClassLoader.getResource). The model likely overfit to common boilerplate patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels clones based on functional similarity; these functions have different purposes and output types, so they would be considered non-clones despite similar boilerplate I/O code.
- 共享行为: Both open a textual resource, read it line by line, ignore lines starting with '#', and process each line to produce output.；Both use BufferedReader and InputStreamReader.
- 行为差异: Different resource types (HTTP URL vs classpath resource)；Different processing (parsing CSV-like vs class loading)；Different return types (array vs single object)；Different error handling (return null vs throw exception)
- 修正建议: Incorporate type/return-type awareness；Use method name semantics；Consider longer context like method signatures；Leverage dataflow or graph-based features to distinguish different API usages

### case_id=266 FN partial_functionality

- 方法: `File2String` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file from filesystem or classpath resource and returns its content as a string, with error handling that prints messages and exits.
- B 摘要: Connects to a fixed URL and logs its content, throwing exceptions on failure.
- 静态失败原因: The static BERT model likely relied on surface tokens and AST structure, which differ significantly due to different method names, return types, error handling, and source types. The shared core behavior (BufferedReader, StringBuffer, readLine loop) may not have been weighted enough to overcome the differences, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as 'read all text from a source into a string buffer' clones, ignoring source type and return value due to high-level functional similarity.
- 共享行为: Open an input stream from a source (file/URL)；Create a BufferedReader；Read lines until end, appending to a StringBuffer；Close the reader
- 行为差异: Source type differs: filesystem/classpath vs fixed URL；Return type differs: String vs void (logging)；Error handling: System.exit vs exception throwing；A has fallback mechanism; B does not
- 修正建议: Enhance training with more diverse I/O source variants to capture high-level functional equivalence.；Use contrastive learning objectives that encourage similarity when core behavior (e.g., reading lines into a buffer) matches despite superficial differences.；Incorporate intermediate representations like dataflow or program dependence graphs to capture semantic commonalities.

### case_id=267 FP lexical_or_api_overlap

- 方法: `getRequestContent` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches the first line from a given URL via HTTP connection.
- B 摘要: Loads a FrameworkFactory instance from a classpath service file by reading and parsing its content.
- 静态失败原因: The model may have focused on the overlapping API calls (URL, BufferedReader, InputStreamReader, readLine, close) and the try-finally pattern, disregarding the different contexts and subsequent operations. The lexical overlap is low but the structural pattern is misleading.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions have distinct purposes and return types, despite both involving stream reading. The overall functionality and output are not similar enough.
- 共享行为: Both use BufferedReader to read from an input stream line by line.；Both close the reader after reading.；Both declare throws Exception.
- 行为差异: A reads from an HTTP connection; B reads from a classpath resource.；A returns a String; B returns a FrameworkFactory object via reflection.；A reads only one line; B reads multiple lines until a valid non-comment line is found.；B includes complex parsing (trimming, comment skipping) and reflection; A does not.
- 修正建议: Train model to differentiate based on return type and the operations performed on the read data (e.g., reflection vs. direct return).；Incorporate data-flow analysis to track how the read data is used after the stream is closed.

### case_id=268 FN boilerplate_overlap

- 方法: `fileDownload` vs `issueCommandToServer`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a given URL and saves it to a local directory with a hardcoded filename 'download.pdf'.
- B 摘要: Sends a command and a data capsule to a server via HTTP POST and returns the server's response as a string.
- 静态失败原因: Static BERT models rely on token overlap and localized syntax. The low Jaccard similarity (0.14) and divergent control flow (read vs write direction) caused the model to miss the underlying structural boilerplate overlap that BCB annotators consider sufficient for a clone label.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a clone because both functions share the common pattern of URLConnection-based I/O (open connection, read/write streams) and are both network communication operations, which can be considered broad Type-4 semantic similarity.
- 共享行为: Both open a URLConnection to interact with a web server.；Both use BufferedReader to read from an input stream.；Both perform a loop to read data until end-of-stream.；Both handle IOException within the method (A catches Exception widely, B declares throws).
- 行为差异: A reads from the URL and writes to a file; B writes to the URL (POST request) and then reads the response.；A's output is a file; B's output is a returned String.；A has a hardcoded filename; B encodes parameters using URLEncoder.；A does not set request properties; B sets doInput, doOutput, and Content-Type header.
- 修正建议: Increase model sensitivity to structural patterns beyond token overlap.；Incorporate data flow analysis to recognize reversed I/O operations as conceptually similar.；Use contrastive learning with pairs labeled by BCB to learn the annotation preference.

### case_id=269 FP lexical_or_api_overlap

- 方法: `callApiPost` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters, checks response code, and returns the input stream.
- B 摘要: Performs a Google image search by constructing a URL, parsing HTML to extract image URLs, and updates a GUI component.
- 静态失败原因: Static BERT methods focused on lexical and API-level similarities (e.g., URL handling, HttpURLConnection) and missed the overall semantic difference due to boilerplate code overlap.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically marks as non-clone when functions have different purposes despite some code overlap. The functions differ significantly in functionality and context.
- 共享行为: Both open HTTP connections；Both handle I/O and exceptions；Both use InputStream/Reader for reading response
- 行为差异: A is a generic API caller, B is specific to Google Images；A returns InputStream, B returns void and updates GUI；A uses POST, B uses GET；A checks response status, B does not
- 修正建议: Incorporate high-level semantic understanding like method purpose or return type；Use data flow analysis to differentiate between data retrieval and UI update；Consider method signatures and class context as additional features

### case_id=270 FN partial_functionality

- 方法: `doVersionCheck` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a version-check URL, parses lines to extract build versions, and invokes another method for version comparison.
- B 摘要: Opens an HTTP connection to an OPDS catalog URL, parses the response to download books or navigate pagination, handling errors and callbacks.
- 静态失败原因: Low token overlap and differing method names, plus static models often miss high-level behavioral similarity when code structures diverge significantly in length and detail.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as examples of 'network I/O with parsing' tasks, accepting broad structural similarity despite different specific functionalities.
- 共享行为: Both open a URL and read input data；Both parse the input (lines or XML-based catalog)；Both handle IOExceptions and show errors
- 行为差异: Different parsing logic: version strings vs. OPDS catalog entries；Different error handling: generic error dialog vs. specific error callback；Function B manages HTTP connections, headers, redirects, and content types; Function A uses simple URL.openStream；Function B involves pagination and file download; Function A just extracts versions
- 修正建议: Incorporate higher-level semantic representations like API call sequences；Use graph-based models that capture control-flow and data-flow abstractions

### case_id=271 FP lexical_or_api_overlap

- 方法: `issueCommandToServer` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends a POST request to a server with command and capsule parameters and returns the response string.
- B 摘要: Performs a Google image search, parses the HTML response to extract image URLs, and updates a UI component with the first image.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on lexical and API-level overlap (e.g., HttpURLConnection, BufferedReader, readLine) without understanding the semantic purpose of the functions. The high token overlap in common Java HTTP boilerplate caused a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they implement entirely different functionalities (server command vs image search), despite sharing some HTTP boilerplate. The common pattern is generic and does not indicate semantic equivalence.
- 共享行为: Both open an HTTP connection to a URL；Both read the response line by line using BufferedReader
- 行为差异: Function A uses POST request with form data; Function B uses GET request；Function A sends specific parameters; Function B builds a search query URL；Function A returns the raw response; Function B parses HTML and extracts image URLs；Function B updates a UI component; Function A does not interact with UI
- 修正建议: Incorporate dataflow analysis to track how inputs and outputs are used；Add context-aware embeddings that consider the broader task (e.g., UI vs server communication)；Use contrastive learning to penalize models for relying on boilerplate patterns

### case_id=272 FN benchmark_preference_bias

- 方法: `copyResource` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file using byte streams.
- B 摘要: Main method that prints instructions and performs multiple PDF signing and verification operations.
- 静态失败原因: Static BERT correctly identified the semantic difference due to low token overlap and different method names, but BCB's label was likely a benchmark annotation bias or error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled them as clones because both involve file I/O with streams and exception handling, which could be considered broad Type-4 semantic similarity under a very loose interpretation.
- 共享行为: Both read from an input source and write to an output destination；Both handle I/O exceptions
- 行为差异: A is a generic byte copy; B is a specific PDF signing workflow；A has no side effects beyond file copy; B prints to console and manipulates digital signatures；A uses simple byte copying loop; B uses complex PDF library APIs
- 修正建议: Re-evaluate BCB annotation to remove false positives based on overly broad I/O similarity；Improve annotation guidelines to require more specific functional equivalence

### case_id=273 FP lexical_or_api_overlap

- 方法: `postData` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends HTTP POST data to a URL and reads the response.
- B 摘要: Downloads a file from a URL to local storage with progress reporting.
- 静态失败原因: Static BERT/GraphCodeBERT may have overemphasized lexical overlap in API calls (URLConnection, openConnection, streams) and structural similarity (opening connection, handling streams) while ignoring the direction of data flow (output vs input) and the distinct functional purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they solve different tasks (HTTP POST vs file download) despite sharing networking boilerplate. The token Jaccard is low (0.18), and method names differ substantially.
- 共享行为: Open URL connection using URL class and openConnection；Use getInputStream() and getOutputStream() for I/O；Handle exceptions with throws Exception；Close streams after use
- 行为差异: postData sends data (write to output stream), downloadFile receives data (read from input stream)；postData has void return; downloadFile returns boolean true；downloadFile writes to a file and reports progress via MessageFrame; postData discards response；Different parameters and data types
- 修正建议: Incorporate data flow analysis to distinguish write-oriented vs read-oriented operations；Leverage method names and parameter types as semantic hints；Add fine-grained I/O directionality awareness (e.g., output vs input stream usage)；Consider functional goal (sending data vs downloading file) beyond API sequence

### case_id=274 FN partial_functionality

- 方法: `getEncoding` vs `readVersion`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads HTTP response headers and content to extract character encoding.
- B 摘要: Reads a system resource file to extract version, revision, and date information.
- 静态失败原因: Static BERT models often rely on token and structural similarity; here the token Jaccard is low (0.25) and the functional purpose differs, so it predicted non-clone. However, it may have missed the abstract pattern of line-by-line reading and substring extraction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone due to the shared pattern of reading a resource line by line and extracting substrings based on prefixes, which falls under Type-3/4 clones where structural similarity overrides functional differences.
- 共享行为: Both open a URL/resource using a URL object and read its content line by line with a BufferedReader.；Both iterate over lines looking for specific prefixes/keywords to extract data.；Both handle closing the reader in a finally block.
- 行为差异: Function A returns a string encoding or a default, while Function B sets instance variables and returns void.；Function A searches for charset in HTTP headers and then in body, while Function B looks for specific key-value pairs like Version=, Revision=, Date=.；Function A uses URLConnection and gets header fields, while Function B uses ClassLoader.getSystemResource and url.openStream().
- 修正建议: Include a more abstract representation of file reading and parsing patterns.；Use dataflow analysis to capture similar variable assignments and control flow despite different constants.；Train on pairs that share overall structure but differ in domain constants.

### case_id=275 FP boilerplate_overlap

- 方法: `getFrameworkFactory` vs `parse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Loads and instantiates a FrameworkFactory from a service file using class loader.
- B 摘要: Parses a data file (URL or local) into a DataSet using StreamTokenizer with configurable delimiters, headers, and type conversion.
- 静态失败原因: The model likely overfitted to common API tokens (BufferedReader, InputStream, etc.) and overlooked the distinct domain semantics, possibly due to the truncated long code in B.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they implement entirely different functionalities with no shared business logic or algorithmic similarity.
- 共享行为: Both open an input stream and read data；Both handle exceptions；Both use BufferedReader and InputStreamReader
- 行为差异: Different purpose: loading a service vs. parsing structured data；Different output: FrameworkFactory vs. DataSet；Different parsing logic: simple line reading vs. complex tokenization with type conversion；Different error handling: throw specific exceptions vs. generic runtime exception
- 修正建议: Use semantic-aware embeddings that capture intent beyond token overlap；Incorporate call graph or data flow analysis；Apply attention over longer sequences to handle complex functions

### case_id=276 FN lexical_or_api_overlap

- 方法: `createOutputStream` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Creates a BufferedWriter that reads a ZIP file, copies all entries except 'content.xml', then adds a new 'content.xml' entry with UTF-8 encoding.
- B 摘要: Retrieves a resource by URL as an InputStream, employing local caching and HTTP conditional GET, returns null on failure.
- 静态失败原因: Static BERT correctly predicted non-clone due to low token overlap and distinct APIs, but BCB label considers them clone, causing a false negative error.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled them as Type-4 clones due to both being stream-based I/O utility methods, despite different domains (ZIP vs HTTP), but this is a stretch and likely a misannotation.
- 共享行为: Both perform I/O operations using streams；Both handle file paths and use buffered streams
- 行为差异: A processes ZIP files, B handles HTTP resources；A writes to output stream, B reads from input stream；A uses specific encoding, B uses caching logic；Exception handling differs significantly
- 修正建议: Increase training data with diverse I/O patterns；Incorporate high-level semantic understanding (e.g., task labels)

### case_id=277 FN benchmark_preference_bias

- 方法: `doGet` vs `downLoadZippedFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request by fetching a page based on parameters, checking permissions, logging, and rendering the page with caching and statistics.
- B 摘要: Downloads a file from a URL to a temporary file, unzips it to a destination directory, and returns the local URL of the decompressed content.
- 静态失败原因: The static model correctly predicted non-clone due to very low token overlap (Jaccard=0.0558) and distinct vocabulary; the BCB label is likely an error, so the model did not fail from a semantic perspective. If BCB label is considered ground truth, the model failed because it could not capture the high-level resource-handling similarity that BCB annotators may have perceived.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have mistakenly labeled them as clones due to superficial similarity in resource handling patterns (e.g., file creation, I/O streams) despite completely different purposes, indicating a potential annotation error or overly broad Type-4 interpretation.
- 共享行为: Both use temporary file creation and file I/O operations；Both have try-finally blocks for resource cleanup
- 行为差异: Different core functionality: web page serving vs file download/unzip；Different input/output types: HttpServletRequest/Response vs URL/File；Code A involves user authentication and page rendering; Code B is a utility method
- 修正建议: Use more robust semantic clustering to discern domain-specific functionality；Incorporate API call sequences and data flow to differentiate between serving and downloading；Consider annotator disagreement and use ensemble labels to reduce noise

### case_id=278 FN partial_functionality

- 方法: `getHTML` vs `doRawRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML content from a URL using GET, optionally writes to a file, and returns the content as a string with line breaks.
- B 摘要: Sends a POST request with postData to a service URL and returns the response body as a string.
- 静态失败原因: The static model likely focused on surface-level differences: different method names, HTTP method (GET vs POST), parameters, and additional file I/O in function A, leading to low token Jaccard (0.2985) and feature mismatch. The model may not have captured the high-level semantic similarity of performing an HTTP request and returning the response body.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers functions with similar core functionality (HTTP request-response) as clones, even if the HTTP method or auxiliary operations differ, as long as the primary behavior of fetching and returning web content is present.
- 共享行为: Both open an HTTP connection to a URL；Both read the response line by line and accumulate into a string；Both return the accumulated string
- 行为差异: Function A uses GET, function B uses POST；Function A has an encoding parameter, function B does not；Function A optionally writes to a file, function B does not；Function A uses HttpURLConnection with User-Agent header, function B uses URLConnection with output enabled
- 修正建议: Improve model to recognize that HTTP GET and POST can be similar when the core behavior is reading response.；Add pre-training on code that abstracts HTTP operations.；Use graph-based representations that capture control flow of network I/O.

### case_id=279 FN benchmark_preference_bias

- 方法: `copy` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file or directory recursively using NIO FileChannel.
- B 摘要: Builds a website for editing by transforming XML pages with XSLT and writing output files.
- 静态失败原因: The static model correctly predicted non-clone; the BCB label appears to be an error. The model was not misled by lexical overlap (low Jaccard) and correctly identified the distinct functionality.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have annotated this as a clone based on superficial similarity of 'file copying' behavior, but the methods are conceptually distinct. The broad interpretation of Type-4 (functional similarity) might consider both as 'file processing' but that is too coarse.
- 共享行为: Both perform file I/O operations (read/write) with error handling.
- 行为差异: Function A is a generic recursive file copy utility; Function B is a complex site builder that transforms XML, applies string replacements, and writes multiple output files per page.；Function A uses FileChannel for efficient copying; Function B uses FileInputStream and FileWriter for reading/writing.；Function A has no XML processing, transformation, or page iteration; Function B heavily relies on these.；Function A handles directories and files; Function B only reads specific XML files and writes HTML-like output.
- 修正建议: Re-evaluate BCB annotation for this pair; consider removing it from clone set.；Improve model to handle long-range semantics but in this case model is correct.

### case_id=280 FN partial_functionality

- 方法: `copy` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from a source path to a destination path using FileChannel with nested finally blocks for resource cleanup.
- B 摘要: Builds a website for editing by processing multiple pages, transforming XML, and writing output files with extensive error handling and debugging.
- 静态失败原因: Static BERT models likely rely on token similarity and structural overlap, which are very low here (Jaccard 0.057). The model cannot capture the broad functional similarity that BCB might assign due to shared file I/O patterns, leading to a false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions involve file stream handling and resource cleanup, and BCB sometimes accepts broad Type-3/Type-4 clones based on partial functionality similarity (e.g., both manage file I/O lifecycle).
- 共享行为: Both perform file I/O operations (reading and writing files)；Both manage resources such as streams and channels, with nested try-finally blocks
- 行为差异: Function A is a simple file copy; Function B is a complex site builder with multiple processing steps；Function A uses FileChannel for efficient transfer; Function B uses FileInputStream, FileWriter, and transformers；Function A has no conditional logic; Function B contains loops, conditionals, and exception handling for many sub-tasks
- 修正建议: Incorporate broader functional abstraction matching (e.g., detecting file I/O as a shared sub-task)；Use dataflow analysis to recognize common resource management patterns；Include training examples of Type-3/Type-4 clones with low token overlap

### case_id=281 FN partial_functionality

- 方法: `getContent` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Makes an HTTP request and returns the entire response content as a string.
- B 摘要: Registers a user by validating, setting fields, calling a forum URL via HTTP, reading the response to set forum ID, persisting the user, and sending a confirmation email, returning a boolean for email success.
- 静态失败原因: The static BERT model failed because the lexical and structural overlap between the functions is very low (token Jaccard 0.096), and the shared subpattern (reading HTTP responses) is a small, embedded portion of function B, leading the model to classify them as non-clones.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone due to both functions involving reading HTTP responses with BufferedReader, considering that as a common pattern despite the different overall goals.
- 共享行为: Both use BufferedReader to read lines from an HTTP response stream.
- 行为差异: Function A is purely about reading HTTP response; function B has many additional steps (validation, encoding, database persistence, email).；Function A returns the response content as a string; function B returns a boolean indicating email success.；Function A does not catch exceptions; function B catches IOException and NumberFormatException.；Function A sets connection and socket timeouts; function B does not.
- 修正建议: Train models to recognize shared subroutines even when embedded in larger, unrelated code.；Consider data augmentation that emphasizes partial overlaps.；Re-evaluate BCB labels for pairs with very low token Jaccard to reduce noise.

### case_id=282 FP partial_functionality

- 方法: `getWebPage` vs `getVersion`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads entire content of a given URL and returns it as a string, throwing an error on failure.
- B 摘要: Reads a single line from a hardcoded version URL and returns it as the version string, returning null on failure.
- 静态失败原因: Static BERT may have over-emphasized structural and lexical overlap (e.g., both have try-catch, BufferedReader, readLine) while missing the crucial difference in how read lines are accumulated vs overwritten.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labeled it as non-clone because the functions have different names, inputs, output semantics, and error handling, even though they share a similar I/O pattern.
- 共享行为: Both open a URL connection and use BufferedReader to read lines from the response.
- 行为差异: A reads all lines and concatenates them; B reads only the first line.；A throws IOException as an Error; B returns null on any Exception.；A takes a URL parameter; B uses a hardcoded URL.；A has a verbose error message; B has a debug print.
- 修正建议: Incorporate dataflow analysis to track variable assignments (e.g., concatenation vs single assignment).；Use program dependence graphs to capture control and data dependencies.；Add contrastive training examples that highlight such subtle behavioral differences.

### case_id=283 FP lexical_or_api_overlap

- 方法: `main` vs `addRecord`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Command-line tool that parses a Prolog file and generates adapter JARs.
- B 摘要: Adds a data record from an input stream to a file-based data store with digest-based deduplication.
- 静态失败原因: Static models often over-rely on lexical overlap and common programming constructs (e.g., try-catch, File operations) without understanding high-level intent, leading to false positives.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the functions have no semantic similarity in purpose or behavior, despite sharing some API usage patterns.
- 共享行为: Both perform file I/O operations；Both use exception handling with try-catch-finally
- 行为差异: Function A processes Prolog files and generates adapters, while B stores data records；A has complex command-line argument parsing, B reads from InputStream；A writes multiple JAR entries, B writes a single file；A uses reflection and class loading, B uses message digest and file renaming
- 修正建议: Improve model's ability to distinguish task-level semantics beyond token overlap；Incorporate more structural or data-flow information to capture different control flows and data dependencies

### case_id=284 FN benchmark_preference_bias

- 方法: `addIDs` vs `getWebByUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Extracts metabolite IDs, scores, and molecular weight from a specific metabolomics database web page, and sets various properties on a PeakListRow object.
- B 摘要: Downloads a web page from a given URL and saves it to a file, while also recursively crawling links from the page.
- 静态失败原因: BERT-based models rely on token overlap and structural similarity. The low Jaccard similarity (0.11465) and different domain-specific keywords (e.g., 'Metabolites', 'Analytes' vs 'fileIndex', 'PrintWriter') lead to low representation similarity, so the model correctly predicted non-clone based on surface features.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as 'web scraping' functions that read from URLs and iterate over lines, thus falling under a broad Type-3 or Type-4 clone, emphasizing common patterns over specific processing.
- 共享行为: Both open a URL connection and read the response line by line using BufferedReader；Both handle IOException/Exception
- 行为差异: A parses specific HTML patterns to extract structured data (metabolite IDs, scores) and updates a PeakListRow object; B writes the entire page content to a file and optionally crawls further URLs；A returns an integer score; B returns void；A handles multiple ID types (PubChem, ChEBI, etc.) and sets them on the row; B does not parse any specific fields；A has complex conditional logic to extract substrings; B simply appends lines to a StringBuffer and writes to file
- 修正建议: Use a model that captures semantic intent beyond surface tokens, such as program dependence graphs or dataflow analysis；Incorporate domain-specific embeddings or contextualized representations that can recognize broader functional similarity；Re-evaluate BCB annotation guidelines for consistency in labeling such pairs

### case_id=285 FP library_context_missing

- 方法: `doImageProcess` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `context_recovery_then_dynamic`；动态可解性: `low`；执行优先级: `low`
- A 摘要: Handles HTTP image processing request, optionally resizes image and writes to response.
- B 摘要: Parses multiple configuration strings into sets and maps for Tibetan script processing.
- 静态失败原因: Likely due to the model overgeneralizing from common API tokens (e.g., IOException, InputStream, StringTokenizer) and ignoring the overall context and purpose.
- 静态 case study: 该类错误缺少关键上下文或需要深层语义，纯静态方法不可靠。
- 动态 case study: 动态执行价值较低：样本可能依赖库、框架、网络、GUI、数据库或项目上下文，需要先恢复环境或 mock 依赖。
- BCB 偏好解释: BCB typically labels non-clones when functions have entirely different functionality, even if they use similar Java APIs; here both are unrelated.
- 行为差异: Purpose: image serving vs. data parsing；I/O: HTTP response output vs. reading from string fields；Data types: image bytes vs. character/token sets
- 修正建议: Include more functional context in training, e.g., surrounding method names or class names.；Improve handling of long-range semantics with structure-aware models.

### case_id=286 FP boilerplate_overlap

- 方法: `getUser` vs `import_hints`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a user by login from a DAO, falling back to parsing a colon-delimited config file from classpath if not found.
- B 摘要: Imports puzzle hints from a space-delimited file (URL or local), placing pieces on a board with rotation and marking them as hints.
- 静态失败原因: Static models like CodeBERT often over-rely on overlapping tokens (e.g., 'BufferedReader', 'StringTokenizer', 'InputStreamReader') and structural patterns (try-catch, while loop) while ignoring deep semantic context, leading to false positive clones.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB emphasizes functional similarity; these functions serve entirely different domains and perform different transformations, so they are labeled non-clones despite sharing boilerplate I/O patterns.
- 共享行为: Reads from a file or URL using BufferedReader and InputStreamReader；Parses lines using StringTokenizer with a delimiter
- 行为差异: Purpose: user authentication vs. game hint import；Parsing logic: colon delimiter with three tokens vs. space delimiter with five tokens；Output: returns User object or null vs. returns boolean success flag；Data source: classpath resource vs. URL or local file selected by flag
- 修正建议: Incorporate data-flow analysis to distinguish local variable usage and method calls that define core logic；Use graph-based representations (e.g., AST with edges for API calls) to capture semantic roles of variables；Add contrastive learning to penalize matches based solely on boilerplate idioms

### case_id=287 FN benchmark_preference_bias

- 方法: `PageLoader` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads the entire content of a URL into a string via BufferedReader in a constructor.
- B 摘要: Invokes a remote HTTP service method with retry logic, JSON serialization, and error handling.
- 静态失败原因: The static model (e.g., GraphCodeBERT) correctly identified the low token overlap (Jaccard=0.095) and significant structural/functional differences, predicting non-clone. However, BCB's positive label suggests the model failed to align with BCB's lenient criteria that prioritize partial behavioral similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have annotated this as a clone due to the shared pattern of reading HTTP response body using BufferedReader, ignoring the larger context and different purposes. This reflects a lenient interpretation of Type-3/Type-4 similarity where a common code snippet suffices.
- 共享行为: Both use BufferedReader to read HTTP response line by line.；Both close input streams and readers after reading.
- 行为差异: Function A is a constructor that simply loads a web page into a field (inputLine); Function B is a method that makes HTTP POST requests, handles retries, and deserializes JSON responses.；Function A has no error handling, retry, or method invocation context; Function B is part of a service invocation framework with timeout handling.；The overall purpose and complexity are vastly different: one is a simple page loader, the other is a generic remote procedure call.
- 修正建议: Consider the overall function purpose and context, not just code patterns.；Use task-oriented clustering to distinguish simple data loading from complex service invocation.；Incorporate semantic role labeling to differentiate between a constructor and a method with retry logic.

### case_id=288 FN benchmark_preference_bias

- 方法: `unzip` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Unzips a zip file into a target directory, creating parent directories as needed.
- B 摘要: Launches an Eclipse launch configuration for a NexOpen project, processing Maven pom files and setting up Hibernate properties and reverse engineering files.
- 静态失败原因: Static BERT correctly predicted non-clone (0) due to very low token overlap (0.084) and distinct API usage, but BCB labeled it as clone, causing a false negative. The model did not fail; BCB may have an inconsistent label.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled this as a clone due to a broad interpretation of file and directory manipulation, or due to both functions containing boilerplate I/O and exception handling, but this is unlikely as the contexts are entirely different. More likely a labeling error in BCB.
- 行为差异: Function A performs file decompression; Function B performs Eclipse project configuration and Maven handling.；Function A uses ZipInputStream and file streams; Function B uses Eclipse API, XML parsing, and project properties.；No overlapping logic or data flow.
- 修正建议: Correct BCB label to non-clone (0)；Re-evaluate BCB annotation criteria for such pairs

### case_id=289 FN lexical_or_api_overlap

- 方法: `retrieveQ` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads content from a URL via HTTP GET and returns the raw response as a string, also prints the response message to stderr.
- B 摘要: Invokes a remote service method via HTTP POST, sends JSON arguments, deserializes the response JSON into the expected return type, and retries on timeout.
- 静态失败原因: The static model failed due to low token overlap (Jaccard=0.167) and significant differences in API usage (URLConnection vs Apache HttpClient), control flow (retry, exception handling), and output types. The surface-level features dominated, causing the model to miss the high-level commonality of HTTP request-response handling.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a clone because both functions are primarily concerned with making an HTTP request and reading the response content, which is a core semantic similarity despite differences in method, error handling, and serialization. The broader Type-3/Type-4 category in BCB often accepts such partial functionality overlap.
- 共享行为: Both perform HTTP requests.；Both read response content line by line.；Both return a string-based result (although B does further processing).
- 行为差异: Different HTTP methods: GET vs POST.；Different error handling: A ignores non-200 status, B throws exception on >=300.；B includes retry logic on timeout, A does not.；B serializes/deserializes JSON, A returns raw string.
- 修正建议: Train on more diverse API usages for HTTP interactions.；Incorporate data flow or graph representations to capture common patterns.；Use program analysis to abstract HTTP request-response behavior.

### case_id=290 FN partial_functionality

- 方法: `sendExceptionToServer` vs `sendRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a server via HTTP POST, reads response, and prints success or failure.
- B 摘要: Sends an XML request to a servlet via HTTP POST with GZIP compression, reads GZIP compressed XML response, and builds a JDOM document.
- 静态失败原因: Static BERT models rely heavily on token similarity (Jaccard=0.189) and API usage. The functions use different APIs (e.g., GZIP compression vs. plain), different data formatting, and little lexical overlap. The model missed the conceptual similarity of both being HTTP client routines.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers both as Type-4 clones because they perform the same high-level task: sending data to a server via HTTP and reading the response. The specific details are considered variations on a theme.
- 共享行为: Both establish an HTTP connection to a server.；Both send data via HTTP POST.；Both read the HTTP response.；Both handle exceptions and print output.
- 行为差异: Function A sends plain text URL-encoded parameters; B sends GZIP-compressed XML.；Function A's URL is from a static variable; B constructs URL dynamically from preferences and servlet name.；Function A reads response line by line; B decompresses and parses XML.；Function A checks for response 'success'; B returns an empty string regardless.
- 修正建议: Enhance model to capture dataflow and control-flow structure for HTTP operations.；Use graph neural networks that abstract away low-level details (e.g., compression, encoding) to focus on request/response pattern.；Incorporate more examples of different implementations of similar tasks during training.

### case_id=291 FN benchmark_preference_bias

- 方法: `run` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Opens a URL to a local daily trend page and reads the response lines into a global variable.
- B 摘要: Registers a new user by validating input, encoding password, setting authorities, generating a forum user via HTTP request, persisting to database, and sending confirmation email.
- 静态失败原因: The static BERT/GraphCodeBERT model likely relied on token-level or structural similarities. The low token Jaccard (0.128) and significant differences in method signature, control flow, and length caused it to classify as non-clone. The model failed to recognize the shallow network I/O similarity that BCB might prioritize, possibly due to lack of training on such broad functional categories.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled this as a clone because both functions perform network I/O (HTTP GET request and reading response), which falls under a broad category of network operations. BigCloneBench may consider Type-4 clones for similar high-level I/O patterns despite different overall purposes.
- 共享行为: Both make an HTTP request (URL open, BufferedReader, read lines).
- 行为差异: Function A is a trivial HTTP fetch with no return value and no data usage; Function B is a multi-step registration workflow with validation, persistence, and email sending.；Function A reads all lines but discards them; Function B reads a single line to set forum ID.；Function B has extensive error handling and logging; Function A has minimal exception handling.
- 修正建议: Increase the model's sensitivity to high-level functional categories like network I/O even when syntax varies.；Incorporate functional tagging or API usage patterns to recognize common I/O operations despite different contexts.

### case_id=292 FP lexical_or_api_overlap

- 方法: `addDataFromURL` vs `sendPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads content from a URL and appends it to a field.
- B 摘要: Sends an HTTP POST request with parameters and returns the response.
- 静态失败原因: The high lexical overlap (URL, BufferedReader, InputStreamReader) and similar loop structure mislead static models into focusing on local patterns while ignoring the semantic difference in HTTP method and return behavior.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically treats functions that share only superficial API usage but differ in core functionality (GET vs POST, void vs String return) as non-clones, even if they have similar reading loops.
- 共享行为: Open a URL connection；Read lines from an input stream；Handle exceptions；Use BufferedReader and InputStreamReader
- 行为差异: A uses GET via openStream, B uses POST with HttpURLConnection；A appends to a field, B returns a String；A appends line breaks, B concatenates without newlines；A prints exception to stdout, B shows message via MsgPrint
- 修正建议: Incorporate dataflow analysis to differentiate read vs write operations；Consider method signature (return type, parameters) as discriminative features；Use control flow to distinguish separate close block vs integrated handling

### case_id=293 FP partial_functionality

- 方法: `doVersionCheck` vs `readZoneIDs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads version info from a URL, extracts stable and devel build versions, and triggers a version check dialog.
- B 摘要: Reads zone IDs from a resource file, parses each line as integer, and returns a set of IDs.
- 静态失败原因: The static model likely captured the structural skeleton (open URL, read lines, close) but missed the critical semantic differences in how lines are processed and the overall goal, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels this as non-clone because despite similar input reading pattern, the functional purpose and data processing are entirely different; they do not perform the same task even at a high level.
- 共享行为: Both open a URL and read lines from an input stream；Both use a while loop to read lines until null；Both have try-catch blocks for exception handling
- 行为差异: A processes lines looking for specific version strings, B parses each line as integer；A shows and hides wait cursor and displays error dialogs, B prints stack trace；A calls another method with extracted versions, B returns a HashSet；A uses BufferedReader, B uses LineNumberReader
- 修正建议: Incorporate dataflow analysis to track variable transformations；Add attention to loop body operations beyond boilerplate；Use contrastive learning to distinguish similar skeletons with different semantics

### case_id=294 FN partial_functionality

- 方法: `readAndRewrite` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads a DICOM file, parses it, and rewrites pixel data to an output file.
- B 摘要: Reads a localized properties file, modifies a message entry, and writes back.
- 静态失败原因: Static BERT models rely on token overlap and syntactic similarity; with a token Jaccard of 0.05, they fail to recognize the abstract behavioral pattern shared by both functions.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB's lenient Type-4 clone definition may consider them clones because both implement a read-modify-write pattern on files, a sufficiently abstract functional similarity despite different data formats.
- 共享行为: Both perform file I/O (read from and write to files).；Both transform data in some way before writing.；Both handle exceptions and close resources.
- 行为差异: A processes binary DICOM image data; B processes text properties files.；A uses specialized DICOM libraries; B uses standard Java I/O and Properties.；A involves pixel array manipulation; B involves string replacement and appending.
- 修正建议: Train models to recognize functional patterns beyond lexical overlap (e.g., using program flow or graph-based representations).；Use data augmentation with diverse implementations of similar abstract tasks.；Incorporate high-level API calls or structural motifs (e.g., read-write loops) into features.

### case_id=295 FP lexical_or_api_overlap

- 方法: `addDataFromURL` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches content from a given URL and appends it to a text buffer.
- B 摘要: Performs Google image search, parses HTML response to extract image URLs, and updates the UI with the first image.
- 静态失败原因: Static BERT/GraphCodeBERT methods may over-rely on lexical and API-level overlaps (e.g., URL, BufferedReader, readLine, try-catch) and common structural patterns, while missing the high-level semantic differences. The long range of function B and the UI manipulation parts may not be fully captured by token-level representations.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions serve fundamentally different purposes: one is a generic URL content fetcher, the other is a specific image search with UI interaction. Despite similar I/O patterns, the functionality and output are distinct.
- 共享行为: Both open a URL connection and read from it using BufferedReader；Both handle exceptions with try-catch blocks；Both use InputStreamReader to wrap the input stream
- 行为差异: A appends raw text to a buffer; B parses HTML for image URLs and updates UI；A takes a URL object; B constructs URL from string parameters；B uses HttpURLConnection and sets User-Agent; A uses URL.openStream()；B manipulates UI components (button, label); A does not
- 修正建议: Incorporate function name embeddings to capture purpose；Use data flow analysis to track how data is processed and outputs are used；Train with contrastive learning on functional similarity rather than token overlap；Introduce attention to high-level semantics via code summarization or docstring

### case_id=296 FN partial_functionality

- 方法: `File2String` vs `lookupFutureEvents`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a file or classpath resource into a string, with fallback and exit on failure.
- B 摘要: Fetches JSON from a Meetup API and parses it into a list of Event objects.
- 静态失败原因: Static models like GraphCodeBERT rely on overall token and semantic similarity; the low token overlap (0.158) and different method names and contexts obscure the shared sub-pattern. The model fails to recognize the common I/O loop as a clone indicator.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels functions as clones when they share a significant code fragment or idiom, such as the common pattern of reading lines into a StringBuilder, even if the overall purpose differs. This pair is a typical Type-3/Type-4 partial clone.
- 共享行为: Both use a BufferedReader to read lines from an input stream and append them to a StringBuilder.
- 行为差异: Function A reads a local file; Function B fetches from a remote API.；Function A exits on error; Function B throws a custom exception.；Function B parses JSON and constructs domain objects; Function A returns raw text.
- 修正建议: Incorporate dataflow or control-flow graphs to capture shared sub-patterns.；Use clone detectors specializing in Type-3/Type-4 clones that consider common idioms.；Enhance training with more partial-clone examples.

### case_id=297 FN partial_functionality

- 方法: `doTransfer` vs `scrapeForIsbns`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Proxies an incoming HTTP request to another URL, copying headers and request body, then forwarding the response.
- B 摘要: Scrapes a URL for ISBN-10 patterns using a regex, retrying on connection failures, and counts matches.
- 静态失败原因: Static BERT models rely on surface-level token overlap and structural similarity, which is low here (token Jaccard 0.1088). The different method names, distinct control flows (proxy vs scraper), and lack of common API sequences caused it to miss a potential broad clone that BCB accepted.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled as clone based on very broad similarity in reading from a URL and handling network exceptions, which is considered Type-4 or partial functionality similarity.
- 共享行为: Both open a URL and read its input stream；Both handle IOException
- 行为差异: doTransfer copies entire HTTP request/response; scrapeForIsbns extracts specific text patterns；scrapeForIsbns has retry logic; doTransfer does not；doTransfer modifies request headers and uses multiple streams; scrapeForIsbns only reads content
- 修正建议: Train models with more emphasis on high-level intent rather than exact token matching；Include dataflow analysis to differentiate proxy versus extraction tasks；Use dynamic analysis or execution traces to capture behavioral equivalence

### case_id=298 FP boilerplate_overlap

- 方法: `perform` vs `encrypt`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles HTTP request for classifying a concept, involving session validation, form data extraction, XML building, and HTTP POST to a remote service.
- B 摘要: Encrypts a plaintext string using SHA-512 hashing and Base64 encoding.
- 静态失败原因: The static model likely over-relied on superficial overlaps like 'throws Exception', 'try-catch' blocks, and the presence of String/Buffer operations, or it may have been misled by boilerplate patterns common in Java methods.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB label 0 indicates these are not clones under any of the clone types. Function A is a large, multi-step web action, while Function B is a simple encryption method. They share no meaningful semantic or structural similarity.
- 共享行为: Both methods return a String.；Both use try-catch for exception handling.
- 行为差异: Function A handles complex web request lifecycle with session and form objects; Function B is a simple cryptographic utility.；Function A writes to an HTTP connection and reads response; Function B hashes a string.；Function A has many error conditions and forward to different views; Function B throws Exception on error.
- 修正建议: Improve the model's handling of method length and structural diversity.；Encode better representations of control flow and data dependencies to distinguish web request handling from simple cryptographic functions.；Use token-level attention to focus on distinctive API calls like URLConnection vs MessageDigest.

### case_id=299 FN benchmark_preference_bias

- 方法: `doGet` vs `buildDeb`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles an HTTP GET request, retrieves a page by ID or name, checks user permissions, and outputs the page content with statistics.
- B 摘要: Builds a Debian package file by writing an ar archive containing control and data files.
- 静态失败原因: Static BERT/GraphCodeBERT correctly identified the lack of semantic similarity due to low token Jaccard and differing API usage. However, the BCB label is likely incorrect, so the model prediction aligns with true semantics but not the benchmark annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to a possible misinterpretation of both functions writing output, or due to annotation error. The low token overlap and divergent functionality suggest it is not a clone even under broad BCB criteria.
- 共享行为: Both involve file I/O operations (writing to output stream), but at a very abstract level.
- 行为差异: Function A is a servlet method handling HTTP requests with complex logic for page retrieval, permissions, caching, and logging.；Function B is a static utility that creates a Debian package by writing binary headers and copying file contents.；No overlap in control flow, input parameters, or output semantics.
- 修正建议: Re-evaluate the BCB label for this pair; consider removing from clone set or re-annotating.

### case_id=300 FP boilerplate_overlap

- 方法: `scrapeForIsbns` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves a URL, reads lines, matches ISBN-10 regex pattern, counts matches, and retries on connection failure.
- B 摘要: Reads a service file from classpath to load and instantiate an OSGi framework factory class.
- 静态失败原因: Static BERT models likely focused on lexical and syntactic overlap (BufferedReader, URL, etc.) without understanding semantic intent, leading to false positive due to structural similarity in I/O boilerplate.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because functions have completely different purposes and output types; they are not semantically or syntactically similar beyond basic I/O boilerplate.
- 共享行为: Both open a URL or resource and read lines via BufferedReader and InputStreamReader；Both have try-catch for exceptions；Both use a while loop to read lines
- 行为差异: Function A counts matches and adds to a collection; Function B instantiates a class on first matching line；Function A has retry logic with sleep; Function B does not；Function A returns int; Function B returns FrameworkFactory or throws exception
- 修正建议: Include more context or use whole program analysis to differentiate functional purpose；Incorporate type information and method return types to disambiguate；Use data flow analysis to capture how read data is used

### case_id=301 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks and their anchor text from HTML content of a given URL.
- B 摘要: Reads tab-separated records from a URL and populates a vector with concatenated id and description.
- 静态失败原因: The model likely focused on superficial API similarities (URL, InputStream, BufferedReader) and the loop structure, while ignoring the distinct parsing logic and output semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they perform fundamentally different tasks (link extraction vs. tabular data parsing), even though both involve URL reading.
- 共享行为: Both open a URL and read input from the connection.
- 行为差异: Function A parses HTML to extract links using regex; function B parses tab-separated lines using Scanner.；Function A returns two vectors; function B modifies an input vector and returns void.；Function A includes timing statements; function B has exception handling with try-catch-finally.
- 修正建议: Enhance model to differentiate between parsing patterns (HTML vs. CSV/TSV).；Incorporate data flow analysis: track how input is transformed and what output is produced.

### case_id=302 FN benchmark_preference_bias

- 方法: `readData` vs `sendRequestObjectResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads comma-separated token strings and populates multiple sets and a map for input validation.
- B 摘要: Sends an HTTP request with XML content, receives response, saves it to a file based on content type, and returns the filename.
- 静态失败原因: Static model likely relied on low token overlap (Jaccard=0.079) and distinct control flows, correctly identifying them as non-clones. The BCB label appears to be a false positive.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to a broad interpretation of 'data processing' or a labeling error; there is no functional similarity.
- 共享行为: Both involve some form of data processing (reading strings vs. network I/O), but no common logic.
- 行为差异: A initializes static data structures from string tokens; B communicates with a server and saves a file.；A uses no network or file output; B uses no token parsing or set construction.
- 修正建议: Review and correct BCB annotation for this pair.；Improve training data quality by removing erroneous clone labels.

### case_id=303 FN partial_functionality

- 方法: `copyResource` vs `recurseFiles`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file to a destination file.
- B 摘要: Recursively traverses a directory and adds non-zip files to a zip archive.
- 静态失败原因: Low token overlap and different control flow (linear vs. recursive) make it hard for BERT-based methods to capture the high-level behavioral similarity that BCB might assume.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider both as 'file copy' operations under a broad Type-4 category, focusing on the common I/O pattern of reading and writing byte streams, despite different overall tasks.
- 共享行为: Both read input from a file or stream；Both write output to an OutputStream；Both close streams after use
- 行为差异: A reads from a single source; B reads from multiple files recursively；A writes to a plain file; B writes to a zip archive entry；A handles URL resources; B only handles local files；A copies byte-by-byte; B uses IOUtils.copy (buffered)
- 修正建议: Train on more diverse file I/O examples to capture abstraction；Incorporate dataflow analysis to match input-output transformations；Use structural AST matching with semantics-aware embeddings

### case_id=304 FP boilerplate_overlap

- 方法: `getWebPage` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a web page from a URL and returns its content as a string, throwing an error on IOException.
- B 摘要: Performs a Google image search by constructing a URL, parsing image links from the HTML response, storing them, and updating a UI component with the first image.
- 静态失败原因: The model likely relied on lexical and structural overlap (e.g., BufferedReader, while loop, string concatenation, try-catch) without capturing the semantic purpose, return types, and additional logic like URL construction, HTML parsing, and UI updates.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality is completely different: one is a generic web page fetcher, the other is a specific image search with UI update. The shared boilerplate is not sufficient for a clone label in BCB.
- 共享行为: Both open a URL and read the response line by line using BufferedReader and InputStreamReader.；Both concatenate lines into a single string.；Both use try-catch blocks for exception handling.
- 行为差异: Function A returns a String; Function B is void and updates a UI and a list.；Function B constructs a custom search URL with parameters and adds a User-Agent header; Function A uses the given URL as-is.；Function B parses the HTML to extract image URLs; Function A just returns raw content.；Function B has UI interaction (set icon, enable button); Function A has none.
- 修正建议: Incorporate data flow and method call context to differentiate utility code from core logic.；Use attention mechanisms that focus on distinguishing features like return type, additional API calls (e.g., HttpURLConnection, split, UI components).；Train with more negative examples that share I/O boilerplate but differ in goal.

### case_id=305 FN partial_functionality

- 方法: `fileDownload` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a given URL and saves it to a local directory as download.pdf.
- B 摘要: Fetches version information from a URL (based on jEdit property) and checks for a newer version, displaying messages.
- 静态失败原因: Static BERT methods rely on token-level embeddings and lexical overlap (Jaccard 0.2). They miss the high-level similarity of the URL-reading boilerplate and focus on different method names, variable names, and APIs (FileOutputStream vs. GUIUtilities), leading to a non-clone prediction.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both functions as clones due to shared pattern of fetching data from a URL via BufferedReader, which can be seen as a broad Type-4 semantic similarity despite different post-processing.
- 共享行为: Open a URL and create a BufferedReader to read content；Use a while loop to read input；Handle IOException exceptions；Close the stream after reading
- 行为差异: Function A saves content to a file; Function B parses lines for version info；Function A reads bytes; Function B reads lines；Function A has no user interaction; Function B shows dialogs and cursor changes；Function A uses FileOutputStream; Function B uses string comparison and GUI utilities
- 修正建议: Use program analysis to detect common subpatterns like 'open URL, read input' as a clone indicator；Incorporate dataflow analysis to capture shared I/O operations；Train models to abstract away specific output operations and focus on the input-processing structure

### case_id=306 FN benchmark_preference_bias

- 方法: `readIntoList` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads from a URL, parses HTML lines to extract command names, and populates a map with JMenuItem objects with action listeners.
- B 摘要: Reads a file or classpath resource, concatenates all lines into one string, and returns it; exits on failure.
- 静态失败原因: Static BERT likely relied on token overlap; low Jaccard and clear syntactic differences led to correct non-clone prediction under strict semantics, but the model missed any possible broad similarity BCB might have seen.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'reading text from an external source and processing lines', but this is overly broad and the processing goals are fundamentally different.
- 共享行为: Both read lines from an input stream using BufferedReader
- 行为差异: A parses HTML and creates GUI components; B concatenates lines and returns a string.；A only opens a URL; B tries file system then URL.；A has side effects (populating map, adding listeners); B returns a string.；A does not exit on error; B calls System.exit.
- 修正建议: Improve dataset labeling quality to ensure clones have genuine functional similarity；Use more robust features beyond token overlap to capture partial functionality

### case_id=307 FN partial_functionality

- 方法: `copyResource` vs `getZipAsFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies data from a resource identified by a URL or file path to a destination file.
- B 摘要: Copies data from a DigitalObject's content to a temporary zip file and returns the file.
- 静态失败原因: Low token Jaccard (0.097) and differing method names cause models to miss the high-level semantic similarity of copying data streams.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label as clone because both methods perform the generic functionality of copying input data to a file output, a common Type-4 pattern despite API differences.
- 共享行为: Both open an input stream and write to a file output stream.
- 行为差异: Input source differs (URL/file vs. DigitalObject).；Output destination differs (fixed file vs. temporary file).；Error handling differs (throws Exception vs. catch and print).；Return value differs (void vs. File).
- 修正建议: Use graph-based representations (e.g., program dependency graphs) to capture data flow.；Incorporate functional role detection (source, sink, transformation).；Augment training with type-4 clone examples that have low lexical overlap.

### case_id=308 FP boilerplate_overlap

- 方法: `PageLoader` vs `readUNI`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Constructs a PageLoader by reading all content from a URL and concatenating it into a single string.
- B 摘要: Reads tab-separated lines from a URL, skips the header, and adds parsed description entries to a vector.
- 静态失败原因: The model likely overemphasized the overlapping token patterns like 'URL', 'openStream', 'InputStream', and exception handling, leading it to classify based on structural similarity of reading from a URL rather than the semantically different data processing logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because the core functionality is different: one is a generic content loader, the other is a format-specific parser. The purpose, output, and data handling logic are distinct, despite sharing URL reading boilerplate.
- 共享行为: Both open a URL connection and read text content from it.；Both handle input streams and close them eventually.；Both perform line-based reading.
- 行为差异: A concatenates all lines into one string; B parses lines into structured data with specific fields.；A uses BufferedReader with ready() loop; B uses Scanner with hasNextLine() loop.；A does not skip any lines; B explicitly skips the first line (header).；A stores result in an instance variable; B adds results to a passed collection.
- 修正建议: Incorporate dataflow analysis to track how read data is used after retrieval.；Enhance model with control flow graph comparison to distinguish different loop structures and conditionals.；Train on more examples with high boilerplate overlap but different semantics to penalize such false positives.

### case_id=309 FN benchmark_preference_bias

- 方法: `runScript` vs `getEncoding`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads a script file from a URL and returns its content as a string.
- B 摘要: Extracts the character encoding from an HTTP response by examining headers and body.
- 静态失败原因: Static BERT correctly predicted non-clone (0) because the functions have low token overlap (0.1127) and distinct intents; it did not fail, but BCB label is erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone based on superficial structural similarity (both involve URL opening and reading), but the semantic purposes are completely different, so it should not be considered a clone even under broad Type-4.
- 共享行为: Both open a URL connection and read data from it.
- 行为差异: runScript reads the entire file into a single string; getEncoding looks for charset information.；runScript returns the file content or "error!"; getEncoding returns an encoding string or a default.；getEncoding uses BufferedReader and reads lines; runScript reads bytes one by one.；Error handling: runScript catches all exceptions and returns "error!"; getEncoding throws IOException and has a finally block to close reader.
- 修正建议: Re-evaluate BCB annotation to ensure functional equivalence or strong similarity is required.；Increase token similarity threshold or require behavioral alignment.

### case_id=310 FN partial_functionality

- 方法: `sendExceptionToServer` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends exception details to a remote server via HTTP POST and prints success/failure status.
- B 摘要: Checks for a new version by fetching a version file via HTTP GET and notifies the user via GUI messages.
- 静态失败原因: Static BERT models (e.g., GraphCodeBERT) are sensitive to low token overlap (Jaccard 0.218) and distinct method names and context (sendException vs doVersionCheck). They likely miss the high-level functional similarity due to focus on literal tokens and structure, rather than abstract behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers broad Type-3/Type-4 similarity where both functions perform a network request (HTTP) and parse a response, despite different purposes and output methods. The common pattern of opening a URL, reading lines, and handling IO exceptions may be deemed functionally similar.
- 共享行为: Open a URL connection and read from an InputStream line by line；Handle IOException with error reporting；Perform a network request and process the response；Use BufferedReader and InputStreamReader
- 行为差异: A sends data via POST with URL-encoded parameters; B performs a simple GET；A prints to console; B uses GUI methods like GUIUtilities.message or GUIUtilities.error；A's purpose is error reporting; B's purpose is version checking；A has multiple optional parameters (config, prob); B has only a View parameter
- 修正建议: Incorporate data-flow or program-dependence features to capture abstract IO patterns；Use contrastive learning on pairs with low lexical but high functional similarity；Augment training data with more network-utility clones

### case_id=311 FP lexical_or_api_overlap

- 方法: `loadSourceCode` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads a source file and generates HTML with syntax-highlighted code.
- B 摘要: Imports biological sequences from a URL in FASTA format.
- 静态失败原因: Static BERT/GraphCodeBERT likely overemphasized the similar I/O boilerplate (stream opening, reading loops, exception handling) and token overlap (0.213), ignoring the domain-specific core logic (syntax highlighting vs sequence parsing).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB marks non-clones when functions have entirely different functionality; these two methods serve distinct purposes (source code display vs sequence import), even though they share common I/O boilerplate.
- 共享行为: Both open an input stream (from file or URL)；Both use a reader to read line by line；Both handle exceptions during I/O
- 行为差异: Different input source: local file vs URL；Different output: HTML string vs ArrayLists of names/sequences；Different processing: syntax highlighting vs tokenization of FASTA data
- 修正建议: Incorporate data flow analysis to distinguish core operations；Use a model that captures domain-specific API calls (e.g., CodeViewer vs ImportHelper)；Add training examples that separate similar boilerplate from different semantics

### case_id=312 FP lexical_or_api_overlap

- 方法: `main` vs `Converter`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses a Prolog file, generates adapter classes, and writes them to a JAR file.
- B 摘要: Constructor that reads a file with SJIS encoding and writes it with UTF-8 encoding.
- 静态失败原因: Static BERT models may have been misled by overlapping API calls (FileInputStream, BufferedReader, IOException) and similar error handling patterns, despite overall semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires significant structural and functional similarity, which is lacking here; the functions differ in type, purpose, and complexity.
- 共享行为: Read from a file；Write to a file；Handle IOException with print statements
- 行为差异: A is a static main method, B is a constructor；A involves complex parsing and code generation, B is simple encoding conversion；A uses command-line arguments, B uses constructor parameters；A writes to a JAR file with multiple components, B writes to a single file
- 修正建议: Include method signature and type information in the representation；Use data flow or control flow analysis to capture structural differences；Apply contrastive learning on dissimilar pairs with similar lexical features

### case_id=313 FP boilerplate_overlap

- 方法: `perform` vs `getRandomGUID`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs a web action that processes a classification request by building concept data, sending it to a remote service via HTTP POST, parsing the XML response, and storing results in session.
- B 摘要: Generates a random GUID by computing an MD5 hash of a concatenation of a static identifier, current time, and a random number.
- 静态失败原因: The model likely overfit on superficial tokens such as 'try', 'catch', 'StringBuffer', and error logging patterns, causing it to ignore the vastly different high-level semantics and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they perform entirely different tasks with no functional similarity; they belong to different application domains (web actions vs. utility GUID generation) and share no core logic.
- 共享行为: Both contain try-catch blocks for error handling；Both use StringBuffer for building strings
- 行为差异: A involves HTTP communication and session management; B is purely local computation；A processes web request parameters and beans; B generates a unique identifier；A has complex control flow with multiple conditions; B is a straightforward hashing routine
- 修正建议: Train with more diverse negative examples that share boilerplate but differ in core logic；Incorporate dataflow or control-flow analysis to distinguish functions with similar API patterns but different intentions；Use program dependence graphs or AST-based features to capture deeper structural differences

### case_id=314 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `sendRequestObjectResponse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks from HTML content of a given URL using regex and returns vectors of links and texts.
- B 摘要: Sends an HTTP request with XML payload, receives response, saves it to a file based on content type, and returns the file path.
- 静态失败原因: Over-relied on lexical overlap of URL/URLConnection and stream handling, missing the distinct semantic purposes
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label them as clones because the core functionality is entirely different; shared API usage is too generic to indicate clone
- 共享行为: Both use java.net.URL and URLConnection for network operations；Both handle IO streams and exceptions
- 行为差异: getLinksFromURLFast parses HTML and extracts links; sendRequestObjectResponse sends data and saves response；Different inputs/outputs: one returns vectors, the other returns filename string；Different logic: regex vs. URL construction, compression, file saving
- 修正建议: Enhance model with data flow analysis to capture intent；Include training examples with similar API but different semantics to reduce false positives；Incorporate structural matching beyond API use

### case_id=315 FN boilerplate_overlap

- 方法: `load` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.4`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Loads raw text from a pastebin URL via HTTP GET and returns it as a string.
- B 摘要: Invokes a remote method via HTTP POST, deserializes JSON response, and retries on timeout.
- 静态失败原因: The low token Jaccard (0.146) and significant API differences (javax.net vs apache http, no JSON parsing vs JSON parsing) likely led the model to view them as semantically distinct, failing to recognize the structural I/O pattern similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label as clone because both methods share common networking boilerplate (URL connection, reading response, error handling), and at a high level both 'fetch data from a remote source', fitting broad Type-3/Type-4 similarity.
- 共享行为: Both perform HTTP network requests and read the response line by line using BufferedReader；Both return a string representation of the response (though B also deserializes)；Both handle IOException exceptions
- 行为差异: A uses GET request, B uses POST request；A does not parse the response; B deserializes JSON and maps to method return type；A has input length validation and shows error dialog; B has retry logic on timeout and throws exceptions；B involves reflection on MethodInvocation and type handling
- 修正建议: Use a clone detector that recognizes common I/O patterns as partial clones；Include a rule to boost similarity for methods sharing network request/response handling even if business logic differs；Train on more diverse clone pairs that are functionally different but structurally similar in utility code

### case_id=316 FN benchmark_preference_bias

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using NIO FileChannel.
- B 摘要: Builds an editable version of a website by reading XML, applying XSLT transformations, and writing output files.
- 静态失败原因: The static BERT model likely failed to recognize a clone because of very low token overlap (Jaccard 0.0616) and different method names, missing the broad functional similarity that BCB annotators may have considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones under a broad 'file I/O' category, focusing on the common use of FileInputStream and FileOutputStream, despite major differences in overall functionality.
- 共享行为: Both read from files using FileInputStream.；Both write to files using FileOutputStream or similar.；Both handle IOException.
- 行为差异: Function A is a simple file copy; function B performs complex XML transformation and string manipulation.；Function B iterates over multiple pages, reads control files, and assembles output; function A is a single file operation.；Function B uses DOM and Transformer APIs; function A uses only NIO channels.
- 修正建议: Fine-tune the model on BCB-style annotations to capture broad functional similarity.；Incorporate semantic role labeling for I/O operations to detect partial functionality matches.

### case_id=317 FP boilerplate_overlap

- 方法: `readUNI` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads tab-separated data from a URL and adds parsed descriptions to a vector.
- B 摘要: Fetches version check data from a URL and displays version update messages.
- 静态失败原因: The model likely overemphasized the structural similarity (URL.openStream(), while loop, try-catch-finally) and ignored the functional differences, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels these as non-clones because they perform distinct functional tasks; the shared boilerplate of URL reading is insufficient for clone classification.
- 共享行为: Open a URL and read text content line by line；Close the input stream in a finally block
- 行为差异: Different purposes: data loading vs. version checking；Different parsing logic: tab-separated fields vs. prefix-based key-value extraction；Different output: adding to a vector vs. displaying GUI messages；Different exception handling: silent for MalformedURLException vs. error dialog for IOException
- 修正建议: Incorporate data flow and semantic role analysis to distinguish parse logic；Add attention to method names and comments for context；Train on more diverse negative examples with similar boilerplate

### case_id=318 FP boilerplate_overlap

- 方法: `createOutputStream` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Creates a BufferedWriter that copies entries from an input zip to an output zip, skipping 'content.xml' and later writing it with UTF-8 encoding.
- B 摘要: Handles action events for setting preferences like Graphviz path, ImageMagick path, and other UI settings, saving them to a controller.
- 静态失败原因: A static BERT/GraphCodeBERT model might have overfitted to the presence of common Java libraries (e.g., BufferedWriter, File, FileOutputStream) and the general structure of reading/writing files, leading to a false positive. The model may not have captured the high-level purpose difference due to limited context or attention.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely annotated these as non-clones because they perform completely different tasks: one is a utility for zip file manipulation, the other is an event handler for a settings dialog. Even if some low-level I/O operations overlap, the overall functionality is distinct.
- 共享行为: Both involve file I/O operations (zip reading/writing vs file chooser and saving preferences).；Both use Java I/O classes like BufferedWriter, File, etc.
- 行为差异: Function A performs a specific zip file transformation; function B is a general UI event handler for preferences.；Function A is about data processing; function B is about user interface and configuration.；Their control flow and purpose are entirely different.
- 修正建议: Improve training with more diverse examples to reduce sensitivity to common API usage.；Incorporate structural or data flow analysis to distinguish file-processing from UI-event handling.；Use contrastive learning to better separate functions with similar low-level but different high-level behaviors.

### case_id=319 FP boilerplate_overlap

- 方法: `doRawRequest` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with given data and returns the response as a string.
- B 摘要: Loads a FrameworkFactory instance by reading a service file from classpath and using reflection.
- 静态失败原因: The model likely overweighed lexical overlap (URL, BufferedReader, InputStreamReader) which are common Java I/O patterns, and missed the semantic difference in the surrounding code (HTTP vs service loading).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the two methods have completely different functionality: one is for making HTTP requests, the other for loading a framework factory via service discovery. Despite sharing some I/O boilerplate, their core purposes are unrelated.
- 共享行为: Both open a URL and read from an input stream using BufferedReader.；Both use InputStreamReader to convert stream to reader.；Both handle I/O with try/catch or explicit close.
- 行为差异: doRawRequest performs an HTTP POST (sends data), while getFrameworkFactory reads a static file.；doRawRequest writes to output stream, getFrameworkFactory does not.；getFrameworkFactory reflects on class name to instantiate object, doRawRequest just returns string.；Different exception handling: doRawRequest throws IOException, getFrameworkFactory throws Exception.
- 修正建议: Incorporate structural information like control flow and data dependencies to differentiate common I/O boilerplate from unique logic.；Use a model that can capture the high-level purpose (e.g., network request vs resource loading) via function names or import analysis.；Apply fine-tuning on BCB dataset with emphasis on distinguishing similar-looking but semantically different code.

### case_id=320 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.2`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a locale-specific properties file by updating or adding a key-value pair, copying a default English file if necessary.
- B 摘要: Recursively copies a file or directory to a destination path using NIO FileChannel and MappedByteBuffer.
- 静态失败原因: The model relies on lexical and syntactic similarity, which is low (token Jaccard 0.176). It likely failed to recognize the abstract similarity in file copying behavior due to different API usage (Properties vs FileChannel) and different control structures.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotators likely considered the common file copying sub-task as sufficient for a Type-4 clone, as both functions involve copying a file under certain conditions, despite differing overall purposes and implementations.
- 共享行为: Both perform file I/O operations including writing to files.；Both involve copying a file (default English file in A, general file/directory in B).
- 行为差异: A is specifically for modifying properties files with text parsing and rewriting; B is a generic copy utility for any file type.；A uses character streams and BufferedReader/Writer; B uses NIO FileChannel and MappedByteBuffer.；A handles missing locale file by copying from a default; B handles directories recursively.
- 修正建议: Incorporate data-flow or control-flow analysis to detect shared I/O patterns.；Train on examples of partial functionality clones to capture such conceptual similarities.

### case_id=321 FP boilerplate_overlap

- 方法: `getTicketsForQueue` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Retrieves open tickets for a given queue from a Request Tracker server via REST API and returns a list of ticket objects.
- B 摘要: Performs a version check by fetching a configuration URL, parsing build numbers, and triggering a version check dialog.
- 静态失败原因: The model was misled by common structural patterns (e.g., BufferedReader, line reading loops, try-catch) and similar API usage, despite low lexical overlap, due to over-reliance on boilerplate code that appears in many I/O tasks.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the functions perform entirely different tasks; they are not functionally similar even at a high level.
- 共享行为: Both read from a remote source line by line using BufferedReader；Both check line prefixes to identify relevant data；Both close streams in finally or after use；Both handle IOExceptions
- 行为差异: Different purpose: fetching tickets vs. version checking；Different API endpoints and protocols (REST vs. plain URL)；Different parsing logic (ticket IDs vs. build numbers)；Different output (list of ticket objects vs. calling method)
- 修正建议: Train with hard negative examples that have task-irrelevant boilerplate；Incorporate task identification features (e.g., method names, domain-specific terms)；Use more abstract representations to distinguish general I/O patterns from specific business logic

### case_id=322 FN benchmark_preference_bias

- 方法: `writeConfiguration` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Writes the configuration resource from a URL to a Writer, handling null resource.
- B 摘要: Retrieves a resource by name as an InputStream, with caching and HTTP conditional GET handling.
- 静态失败原因: Static BERT models often rely on API/lexical overlap; here the token Jaccard is low (0.10) but both use common IO APIs (URL, InputStream), which could cause false similarity in some contexts. However, the mismatch in overall structure and length likely led to a correct non-clone prediction; the BCB label may be an outlier.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider both as 'configuration resource access' functions, and under Type-4 (functionally similar) they may be labeled clones despite different I/O directions and caching logic.
- 共享行为: Both open a URL to access a resource；Both obtain an InputStream from the URL connection；Both handle IO exceptions
- 行为差异: A writes the InputStream content to a Writer; B returns an InputStream (or cached file stream)；B implements caching with local file store and HTTP response code checking；B uses synchronization and print statements; A is simple and synchronous；B has multiple cache hit/miss branches; A has a single copy path
- 修正建议: Increase sensitivity to output directionality (write vs. read) and caching behavior；Incorporate data-flow analysis to distinguish stream consumers vs. producers；Use method signature information (return type, parameters) to disambiguate

### case_id=323 FP boilerplate_overlap

- 方法: `copyFile` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file from source to destination using NIO FileChannel.
- B 摘要: Main method that generates Java adapters from a Prolog file, handling command-line arguments and multiple steps.
- 静态失败原因: The model likely overfitted to common Java I/O boilerplate (File, IOException, try-catch) and general method structure, missing the vast difference in intent and complexity. The low token Jaccard suggests the model relied on structural embeddings that may have been biased by similar control flow patterns.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled 0 because the functions are semantically unrelated: one copies a file, the other generates code from a Prolog file. Even broad Type-4 similarity is absent.
- 共享行为: Both use java.io.File and handle IOException.
- 行为差异: Function A is a simple file copy; Function B is a complex adapter generator with parsing, class writing, and serialization.；Function A has a single purpose; Function B includes argument parsing, file reading, parsing, code generation, and error handling.；Function A uses FileChannel for efficient transfer; Function B uses multiple file operations and libraries (Apache Commons IO, ASM, etc.).
- 修正建议: Increase training data diversity for file I/O related methods.；Incorporate more fine-grained semantic similarity signals, such as data flow graphs or program dependence graphs.；Use a model that better captures long-range semantic differences beyond local patterns.

### case_id=324 FN benchmark_preference_bias

- 方法: `doGet` vs `copyExternalResource`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET request to retrieve and render a portal page, with optional caching of output to a temp file.
- B 摘要: Copies the content of a source file to a destination file using NIO FileChannel.
- 静态失败原因: Static BERT/GraphCodeBERT correctly predicted non-clone due to low token overlap and very different API usage; the model was not misled by the limited shared file I/O behavior.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as performing file-writing operations, accepting broad Type-4 similarity; alternatively, this could be a labeling error.
- 共享行为: Both may involve file I/O operations (A writes to temp file, B copies file)
- 行为差异: A is a servlet method handling web requests with complex logic, B is a utility for file copy；A uses HTTP request/response and portal APIs, B uses java.io and nio；A writes conditionally and after extensive processing, B directly copies content
- 修正建议: Review BCB annotation to confirm if this pair truly qualifies as a clone；If not, correct the label to non-clone

### case_id=325 FN benchmark_preference_bias

- 方法: `split` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Splits a large FASTA file into multiple smaller files based on maximum base and entry counts, using NIO channels and buffers for efficient I/O.
- B 摘要: Retrieves a resource as an InputStream, caching the content locally from a remote URL with HTTP conditional GET support.
- 静态失败原因: The static model correctly predicted non-clone; the failure is in the BCB label, not the model.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label may have been misapplied due to superficial similarity in file handling or a benchmark annotation error, as there is no functional overlap.
- 共享行为: Both perform file I/O operations and handle exceptions.
- 行为差异: Function A splits a local file; Function B caches remote resources.；Function A uses NIO channels and direct buffers; Function B uses buffered streams and HTTP connections.；Function A's goal is partitioning by size; Function B's goal is caching for subsequent access.
- 修正建议: Re-annotate the pair as non-clone in BCB.；Improve benchmark consistency by filtering out dissimilar pairs.

### case_id=326 FP boilerplate_overlap

- 方法: `getTicketsForQueue` vs `parse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Retrieves open tickets for a queue from an RT server via HTTP and returns a list of RTTicket objects.
- B 摘要: Parses a delimited data file or URL into a DataSet object, handling headers, types, and scientific notation.
- 静态失败原因: The model likely overemphasized lexical/structural similarities such as common I/O patterns (BufferedReader, line reading) and the phrase 'does not exist' in error handling, ignoring the fundamental difference in domain logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB considers whole-function semantic equivalence; these two functions have completely different purposes and are not functionally similar, hence non-clone.
- 共享行为: Both read input line by line using BufferedReader；Both use try-catch blocks for exception handling；Both check for 'does not exist' conditions
- 行为差异: A performs an HTTP GET request and parses ticket IDs; B reads from local file or URL using StreamTokenizer；A focuses on ticket retrieval; B focuses on generic data parsing with configurable delimiters and types；A has nested loops to fetch individual tickets; B builds a DataSet with column metadata
- 修正建议: Increase corpus diversity to reduce overreliance on I/O boilerplate；Incorporate domain-specific semantic features or API call analysis；Use contrastive learning with harder negative examples

### case_id=327 FP lexical_or_api_overlap

- 方法: `populateResources` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Populates resource templates and image properties from predefined locations.
- B 摘要: Performs a Google image search, extracts image URLs, and updates the UI with an image.
- 静态失败原因: The model overemphasized syntactic overlap (similar control flow: try-catch, URL, BufferedReader, while loop reading lines) and ignored different operational semantics. Static methods like BERT do not capture dataflow or domain-specific differences well.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the overall functionality is entirely different; the only overlap is boilerplate I/O and error handling, which BCB does not consider sufficient for a clone.
- 共享行为: Both use URL, InputStream, BufferedReader for I/O；Both have try-catch exception handling；Both iterate over lines from a stream
- 行为差异: A loads local resources and saves to database; B fetches remote web content and updates UI；A deals with XML/txt files and predefined images; B parses HTML for image URLs；A saves properties; B displays an image on a UI component
- 修正建议: Add negative samples with similar I/O patterns but different business logic；Use dataflow-aware training or graph-based code representations；Include domain-specific features

### case_id=328 FN partial_functionality

- 方法: `getFile` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint attribute, and saves it to a temporary directory, with extensive error handling and logging.
- B 摘要: Copies a file from a source File object to a destination File object using FileChannel.
- 静态失败原因: Static models like GraphCodeBERT rely on token overlap and AST substructures; the low Jaccard similarity (0.1167) and large structural differences (one long, complex method vs a short one) prevent capturing the high-level semantic similarity of data copying.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these clones because both perform a 'copy' operation (one from a URL to file, the other from file to file) using similar FileChannel patterns, aligning with broad Type-4 semantic similarity.
- 共享行为: Both use FileChannel to transfer data between input and output streams.；Both involve reading from an input source and writing to an output destination.；Both methods throw IOException and operate on files.
- 行为差异: getFile downloads from a remote URL via HTTP, while copy operates on local files.；getFile includes XML parsing and modification of WSDL content; copy does not transform data.；getFile has extensive error handling and logging; copy is minimal and without logging.；getFile checks file existence and length before downloading; copy does not perform such checks.
- 修正建议: Train models to recognize high-level operations like copy/download via API call sequences and data flow.；Use contrastive learning to align semantically similar but syntactically different code snippets.；Incorporate method names and documentation as weak signals for semantics.

### case_id=329 FN boilerplate_overlap

- 方法: `main` vs `upload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its contents to local files.
- B 摘要: Copies an image file from a source path to a destination path and returns 'show'.
- 静态失败原因: The model likely relied on token overlap and simple API sequence similarity. Both functions contain FileOutputStream and IOException handling, but the higher-level logic (download-and-unzip vs. copy) differs. Low Jaccard similarity (0.11) was outweighed by the presence of common I/O tokens.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: The BCB label of 1 might be due to both functions performing file I/O with similar boilerplate code (FileOutputStream, try-catch), but the overall functionality is semantically different. BCB sometimes overestimates similarity when common library calls are present.
- 共享行为: Both use FileOutputStream to write data to a file.；Both handle IOExceptions with stack trace printing.
- 行为差异: A involves network download and ZIP extraction; B copies a single local file.；A writes multiple files (each entry); B writes a single file.；A prints status messages; B returns a String.；A uses ZipInputStream and BufferedOutputStream; B uses IOUtils.copy.
- 修正建议: Include features capturing high-level control flow (e.g., loops, conditionals) to distinguish iteration over zip entries from single file copy.；Incorporate external API usage context (URL vs File) to differentiate network from local operations.；Use AST-based structural matching to identify distinct functional patterns.

### case_id=330 FN partial_functionality

- 方法: `copy` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies files or directories from a Hadoop FileSystem to a local destination, with optional deletion of source.
- B 摘要: Retrieves a resource by name, caching it locally from a network source, and returns a FileInputStream to the cached file.
- 静态失败原因: Static BERT models rely on token overlap and local structural patterns; low token Jaccard (0.114) and differing control flow prevent detection of high-level semantic similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as Type-4 clones because both functions perform data copying from a source to a local file at a high level of abstraction, despite significant syntactic and contextual differences.
- 共享行为: Both transfer data from a source to a local file destination.
- 行为差异: Source type: Hadoop FileSystem vs. network resource (URL).；Function A recursively copies directories; Function B handles single resources with caching.；Function A uses IOUtils.copyBytes; Function B manually reads/writes bytes with buffered streams.；Function B has HTTP caching logic; Function A optionally deletes source after copy.
- 修正建议: Train models on behavioral clone pairs with diverse syntax.；Incorporate program dependency graphs or data flow analysis to capture shared data transfer semantics.

### case_id=331 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `postData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a URL's HTML content to extract all anchor links and their text, returning them as two Vectors.
- B 摘要: Sends HTTP POST data to a specified URL and reads the response without processing it.
- 静态失败原因: The static model likely over-relied on the shared API calls (URL, URLConnection, BufferedReader, InputStreamReader) and the structural pattern of opening a connection and reading input. It may have ignored the core logic differences in parsing vs. writing, and misjudged the similar-looking setup and teardown as evidence of cloning.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotations typically consider whole-function semantic equivalence or at least similar functional behavior. Here, the functions have no overlapping purpose; they perform completely different tasks on the web (scraping vs. posting). Hence BCB correctly labeled as non-clone.
- 共享行为: Both open a URL connection using URL and URLConnection.；Both read from the connection's input stream using BufferedReader and InputStreamReader.；Both handle exceptions with throws Exception.
- 行为差异: Function A extracts links from HTML; Function B sends data via POST.；Function A uses regex to parse anchor tags; Function B does not parse the response.；Function A returns data; Function B is void.；Function A uses timeCheck logging; Function B does not.
- 修正建议: Train model to focus on core functional logic rather than boilerplate I/O setup.；Add attention to the method's return type and purpose (void vs. returning data).；Incorporate data flow awareness to distinguish writing vs. reading patterns.；Include IDE type inference or method documentation to understand intent.

### case_id=332 FP boilerplate_overlap

- 方法: `copy` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Copies data from an InputStream to an OutputStream, handling IOException and closing streams.
- B 摘要: Reads and parses multiple string delimited lists into various sets and maps for configuration.
- 静态失败原因: The model likely overfitted to common lexical patterns like 'try', 'catch (IOException e)', and 'private static' method modifier, ignoring the entirely different logic and context.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically marks non-clones when functions have entirely different purposes and minimal code overlap; here the methods are clearly unrelated in functionality.
- 共享行为: Both handle IOException with try-catch.；Both are private static methods.
- 行为差异: Function A performs I/O stream copying; Function B parses tokens and populates data structures.；Function A uses IOUtils utilities; Function B uses StringTokenizer and HashSet/Map operations.；Function A is short and focused; Function B is lengthy and complex with multiple loops and state changes.
- 修正建议: Increase sensitivity to method purpose beyond exception handling boilerplate.；Use control-flow and data-flow analysis to differentiate stream copying from token parsing.

### case_id=333 FP lexical_or_api_overlap

- 方法: `get` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches game records from a remote server via HTTP GET with location and count parameters, parses lines skipping comments, returns array of GameRecord.
- B 摘要: Checks for a newer version of jEdit by reading a version file from a URL, parses version and build strings, and displays appropriate UI message.
- 静态失败原因: The model likely over-relied on lexical and structural overlap (URL, BufferedReader, while loop) and failed to capture the distinct functional intents and different APIs (GameRecord vs. jEdit properties, UI interaction).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: Even under broad BCB criteria, these functions implement fundamentally different business logic (game record retrieval vs. version checking) despite sharing a similar I/O boilerplate pattern, so they are unlikely considered clones.
- 共享行为: Both open a URL and read from an InputStream line by line.；Both skip lines with a specific prefix (# or .).；Both handle IOException with error output.
- 行为差异: Different purposes: data retrieval (A) vs. version check (B).；Different inputs: URL + coordinates + count (A) vs. View (B).；Different outputs: returns GameRecord[] (A) vs. void (B).；Different parsing: decode into GameRecord (A) vs. extract version/build strings (B).
- 修正建议: Enhance training to differentiate between boilerplate patterns and actual functionality.；Incorporate richer semantic representations of method purpose (e.g., using method name or docstring).；Consider return types and side effects (e.g., UI calls vs. data return).

### case_id=334 FP lexical_or_api_overlap

- 方法: `copyOverWarFile` vs `main`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies war files from a specified directory or user.dir/war to the apps data directory, then moves and extracts them.
- B 摘要: Reads a Prolog file, parses it, generates adapter code and a JAR file containing the adapters and shared classes.
- 静态失败原因: Static models like BERT or GraphCodeBERT may rely on token similarity and API usage; both functions contain common tokens like 'File', 'System.out.println', 'IOException', and try-catch blocks, leading to a false positive prediction.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators would likely label this as not clones because the functions have completely different purposes and logic, despite some superficial API overlap.
- 共享行为: Both use File class and file I/O operations；Both print messages to System.out；Both handle exceptions with try-catch blocks；Both use Logger or print stack traces for errors
- 行为差异: Function A deals with copying .war files; Function B deals with parsing Prolog and generating Java adapters；Function A uses WildcardFileFilter; Function B uses complex parser, visitor, and class generation；Function A is short (~30 lines); Function B is long (~80 lines) with many steps；Function A has no command-line arguments; Function B processes args for file paths and debug flag
- 修正建议: Use data flow or control flow features to distinguish different program intents；Train on a more diverse dataset to reduce bias towards boilerplate patterns；Incorporate method name and overall structure in the representation

### case_id=335 FN benchmark_preference_bias

- 方法: `EncodeReturn` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Encodes and returns a file after encryption and piggybacking of data.
- B 摘要: Launches a NexOpen project configuration, handling Maven pom files, Hibernate dialect, and reverse engineering files.
- 静态失败原因: The static model correctly predicted non-clone due to low token overlap and distinct structures; the failure is in BCB annotation, not the model.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: The BCB label likely results from overly broad Type-4 clone criteria, considering both methods as 'file processing' or 'setup' activities, or it may be a labeling error.
- 共享行为: Performs file I/O operations；Handles exceptions and checked exceptions
- 行为差异: Different domain: cryptographic file processing vs. Eclipse project configuration；Different control flow and purpose；Different exception types and handling
- 修正建议: Re-evaluate BCB label for this pair; likely should be non-clone；Improve consistency in BCB annotations for dissimilar function pairs

### case_id=336 FN partial_functionality

- 方法: `setBundleInfoName` vs `File2String`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.75`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL, parses key=value lines, and updates matching BundleInfo objects in a list.
- B 摘要: Reads a file or classpath resource and concatenates all lines into a single string, exiting on failure.
- 静态失败原因: Low token overlap and different method names/purposes; static BERT models rely on lexical similarity and miss abstract semantic similarity of reading lines from input.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'reading from an external source and processing lines', focusing on structural similarity of BufferedReader usage and exception handling, thus labeling as Type-3 clone.
- 共享行为: Both open an input stream (from URL or File).；Both use BufferedReader to read lines.；Both handle IOException.；Both iterate through lines.
- 行为差异: A parses lines as key=value pairs, B concatenates lines.；A uses location as URL, B tries file then classpath resource.；A updates a list of objects, B returns a string.；B has System.exit and print statements, A only prints stack trace.
- 修正建议: Incorporate structural representations (e.g., AST, CFG) to capture common pattern of reading lines.；Use fine-grained matching of IO operations and exception handling.；Consider method purpose classification to differentiate final output goals.

### case_id=337 FN benchmark_preference_bias

- 方法: `addIDs` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Retrieves metabolite data from a web service by parsing HTML and updates a PeakListRow with parsed IDs.
- B 摘要: Reads a resource file and sets the text of a GUI text component.
- 静态失败原因: Static BERT models may rely on surface token overlap, but here the model correctly predicted non-clone. The BCB annotation is likely erroneous; the model did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might consider them Type-4 clones due to both containing while loops reading lines from a BufferedReader and closing resources, but this overlooks fundamentally different data processing.
- 共享行为: Both use BufferedReader to read from an InputStream line by line.；Both close resources in try-catch blocks.
- 行为差异: Function A parses HTML and sets multiple fields on a data object; Function B reads a resource and updates a GUI.；Function A returns an integer score; Function B has no return value.；Function A uses external HTTP URL; Function B reads from classpath resource.
- 修正建议: Ensure evaluation benchmarks reflect true semantic similarity, not superficial I/O patterns.；Use models that capture purpose and data flow rather than token overlap.

### case_id=338 FN benchmark_preference_bias

- 方法: `getEncoding` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Retrieves the character encoding from a URL by examining HTTP headers and then reading the response content for charset/encoding declarations.
- B 摘要: Performs a version check by reading a remote file from a URL and extracting build version strings from lines starting with '.build' and '.stablebuild'.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on lexical and syntactic patterns; the low token Jaccard suggests little lexical overlap. The model likely failed to recognize any functional similarity because the code structures differ: header handling vs not, different condition checks, and different return types. The model correctly predicted non-clone according to strict semantics, but BCB's label is the opposite.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to the common pattern of reading from a URL, buffered line reading, and conditional extraction of information from lines, which could be seen as a Type-3 clone with differences in conditions and extracted data. However, the functional purpose differs significantly.
- 共享行为: Both open a URL connection and read lines from its input stream using BufferedReader；Both parse each line for specific keywords/prefixes to extract information
- 行为差异: Function A examines HTTP headers and falls back to content scanning; Function B does not examine headers；Function A extracts character encoding; Function B extracts version strings；Function A returns a string encoding; Function B calls another method and does not return a value；Function A closes reader in finally block; Function B closes in try block
- 修正建议: Improve detection of Type-4 clones by incorporating semantic role labeling or goal-oriented analysis；Use contrastive learning on varied functional patterns；Consider that BCB labels may include broad functional similarity; train with tolerance for differing purposes if both involve URL reading and line parsing

### case_id=339 FP boilerplate_overlap

- 方法: `executePost` vs `parse`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Sends an HTTP POST request to a given URL with parameters and returns the response as a string.
- B 摘要: Parses a data file (or URL) according to configured delimiters, headers, and types, and returns a DataSet object.
- 静态失败原因: The static BERT model may have been misled by common I/O API usage (URL, BufferedReader, streams) and structural patterns (try-catch-finally, loops), leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label as non-clone because the functions have completely different purposes and outputs, despite some shared I/O boilerplate.
- 共享行为: Both use streams and buffered readers；Both handle exceptions；Both involve I/O operations
- 行为差异: Different core functionality: HTTP POST vs file parsing；Different output types: String vs DataSet；A writes data before reading, B only reads；B has complex parsing logic for headers, types, and scientific notation
- 修正建议: Use dataflow analysis to distinguish I/O patterns；Incorporate method signature and return type features；Train with more diverse negative examples

### case_id=340 FP boilerplate_overlap

- 方法: `getLinksFromURLFast` vs `import_hints`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts hyperlinks and anchor texts from an HTML page given a URL using regex.
- B 摘要: Imports puzzle hints from a file or URL, parsing piece positions and rotations, and placing them on a board.
- 静态失败原因: Static BERT likely focused on the overlapping I/O boilerplate (URL, BufferedReader, InputStreamReader, StringTokenizer) and the while-read-loop pattern, ignoring the distinct semantic goals and output types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires semantic equivalence or strong functional similarity. These functions have completely different high-level purposes (web scraping vs game state import), so BCB would label as non-clone.
- 共享行为: Both open a URL or file and read lines via BufferedReader and InputStreamReader；Both parse tokens from each line
- 行为差异: A parses HTML with regex to find <a> tags; B reads structured text with tokens；A returns vectors of links and texts; B places pieces on a board and returns boolean；A uses timeCheck for debugging; B has a byurl flag and handles FileReader alternative；B involves game-specific logic (place_piece_at, set_as_hint); A focuses on URL extraction
- 修正建议: Train model to capture high-level intent via function names or class context；Incorporate data-flow analysis to distinguish different output semantics；Use contrastive learning to penalize false similarity from common API patterns

### case_id=341 FN partial_functionality

- 方法: `addIDs` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Queries a metabolite database via HTTP to retrieve and set multiple properties on a PeakListRow object, returning a score (int).
- B 摘要: Registers a User by encoding password, setting default authority, creating a phpBB forum user via HTTP, persisting to database, and sending confirmation email, returning a boolean.
- 静态失败原因: Low token overlap (0.116) and different method names, API calls, and code structure caused the model to miss the abstract HTTP I/O pattern; local attention may not capture the high-level similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions share a common pattern of HTTP I/O followed by object population, which fits broad Type-3/Type-4 definitions of functional similarity despite different domains.
- 共享行为: Both perform HTTP connections to external URLs and read responses using BufferedReader.；Both use the response data to set properties on an object (PeakListRow vs User).；Both involve some form of registration or retrieval of external identifiers.
- 行为差异: Different input types (PeakListRow+String vs Object/User) and output types (int vs boolean).；A parses HTML to extract multiple fields; B sends form data and reads a single line.；A handles errors by returning 0 on IOException; B throws RuntimeException or returns false.；High-level goal: metabolite lookup vs user registration.
- 修正建议: Incorporate data-flow analysis to capture patterns like URL connection -> read -> update object.；Use graph-based representations that model I/O operations and object state changes.；Augment training data with paraphrased functions that share I/O patterns but differ lexically.

### case_id=342 FP lexical_or_api_overlap

- 方法: `importSequences` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Imports biological sequences from a URL, parsing FASTA format and storing names and sequences.
- B 摘要: Checks for software upgrades by querying a remote server, processing license and upgrade data, and updating UI.
- 静态失败原因: Static BERT models likely relied on lexical overlap (e.g., URL, InputStream, BufferedReader) and exception handling boilerplate, ignoring deeper semantic differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functionality is entirely different despite shared I/O patterns.
- 共享行为: Both read data from a URL using similar I/O classes；Both handle I/O exceptions
- 行为差异: Different domains: biology vs. software upgrade；A parses sequence data and stores in lists; B parses XML-like responses and performs database operations and UI updates
- 修正建议: Improve semantic understanding by training on more diverse examples that differentiate domain-specific logic；Incorporate dataflow analysis to capture distinct transformations；Use contextual embeddings that capture broader code structure

### case_id=343 FP other

- 方法: `readData` vs `testCopy_inputStreamToOutputStream`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses configuration strings into sets and maps for Tibetan transliteration.
- B 摘要: Tests copying an InputStream to an OutputStream using IOUtils.copy.
- 静态失败原因: Likely due to lexical overlap of common Java tokens (e.g., 'new', 'while', variable declarations) and possibly the model misinterpreting both as 'setup' methods without capturing the core semantic difference.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB requires some functional similarity for Type-3/Type-4 clones; these functions are completely unrelated, so BCB correctly labels as non-clone.
- 共享行为: None
- 行为差异: Entirely different purpose: one initializes data structures, the other tests IO copying.；Different code structure: one is a large private method with many loops and tokenization, the other is a short test method with stream setup and assertions.；Different side effects: one modifies global sets/maps, the other only affects local streams and asserts.
- 修正建议: Improve model to distinguish test methods from data initialization methods.；Incorporate method-level annotations and context.；Use a model that captures long-range semantics and data flows.

### case_id=344 FN partial_functionality

- 方法: `buildDeb` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Build a Debian package archive by writing header and three sequential files (debian-binary, control, data) using file I/O.
- B 摘要: Build an editable web site by reading XML, applying transformations, reading control files, replacing strings, and writing output files for each page.
- 静态失败原因: Low token overlap (Jaccard=0.066) and different method names/lengths caused the model to miss the common I/O pattern; it relies on surface-level token and structure similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels Type-3 clones when functions share a high-level file-processing task, even if implementation details differ; both functions fundamentally copy/transform file content to output.
- 共享行为: Both perform file I/O: read from input files and write to output files using buffered loops.
- 行为差异: Different output formats (Debian archive vs HTML/XML web pages)；Function B includes XML transformation, string replacement, and debug logging absent in A；Function A has fixed constant file names; B has dynamic parameters and multiple file paths
- 修正建议: Incorporate dataflow analysis to detect common file read/write patterns；Use contrastive learning on tasks with similar I/O behavior；Add global context of file operations beyond local tokens

### case_id=345 FP lexical_or_api_overlap

- 方法: `getVersion` vs `loadExistingAntlibs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a version string from a hardcoded URL by reading the first line.
- B 摘要: Loads ant libraries from system resources by iterating through URLs, reading lines, and processing each as a package URI.
- 静态失败原因: The static BERT model likely overemphasized the shared API calls (URL, BufferedReader, InputStream) and similar loop structures, ignoring the different method signatures, return types, and overall intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the overall functionality is distinct despite shared I/O patterns; BCB requires functional similarity beyond common utility usage.
- 共享行为: Both use URL, URLConnection, BufferedReader, and InputStreamReader to read from URLs.；Both have while loops that read lines.；Both handle exceptions.
- 行为差异: getVersion returns a String (the version) and reads from a single URL; loadExistingAntlibs returns void and iterates over multiple resources.；getVersion assigns the last read line to a variable; loadExistingAntlibs processes each line individually to create URIs and load antlibs.；getVersion has no specific error handling beyond setting version to null; loadExistingAntlibs throws RuntimeExceptions.；Different method signatures: getVersion takes no parameters, loadExistingAntlibs takes a ClassLoader.
- 修正建议: Incorporate method signature and return type information.；Use data flow analysis to track how read data is used.；Consider call context and external dependencies.

### case_id=346 FN partial_functionality

- 方法: `onlyFileCopy` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel.transferTo in a loop with proper resource management.
- B 摘要: Launches an Eclipse launch configuration for a NexOpen project, involving Maven POM handling, profile setup, Hibernate dialect configuration, and resource file copying.
- 静态失败原因: Static BERT models rely on token similarity and method signatures; the low Jaccard similarity (0.064) and different method names (onlyFileCopy vs launch) led to a non-clone prediction, missing the underlying file copy substructure in B.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as clones because they share the core behavior of copying a file, even though B has extra logic. BCB's broad Type-4 inclusion accepts partial functionality overlap.
- 共享行为: Both involve file I/O operations, specifically copying data from one location to another.
- 行为差异: Function A is exclusively dedicated to file copying, while function B performs many additional tasks.；Function A uses FileChannel and direct byte transfer; function B uses IOUtils.copy and stream-based copy.；Function B manipulates Eclipse workspace, project metadata, and Maven POM files, which are absent in A.
- 修正建议: Use a model that can detect substructure or subprogram similarity, e.g., by decomposing functions into smaller semantic units or employing graph-based representations that capture data flow.；Augment training data with pairs where one function embeds another's core behavior.

### case_id=347 FN benchmark_preference_bias

- 方法: `main` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a URL and extracts its ZIP entries to local files.
- B 摘要: Reads message catalog files, applies a pseudolocalization pipeline, and writes processed messages to output files with a suffix.
- 静态失败原因: The static BERT model correctly predicted non-clone because of low token overlap and clear semantic difference; the BCB label appears to be an annotation error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to superficial structural similarity (while loops, file streams) or a misinterpretation of Type-4 similarity, but there is no functional overlap.
- 共享行为: Both perform file I/O operations using input and output streams.
- 行为差异: Completely different purpose: one extracts a specific archive format, the other processes message catalogs for localization.；Different input sources: fixed URL vs. file list/stdin.；Different output format: raw extracted files vs. processed messages with suffix.
- 修正建议: Review BCB annotation for this pair; likely remove from clone set.；Ensure annotators are trained to distinguish generic I/O patterns from true semantic clones.

### case_id=348 FN benchmark_preference_bias

- 方法: `forBundle` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Iterates over bundle entries, writes them to a JAR with modified manifest, and installs/uninstalls plugins.
- B 摘要: Processes Eclipse launch configuration, validates project structure, handles Maven pom files, generates reverse engineering files, and schedules an install project action.
- 静态失败原因: Static BERT/GraphCodeBERT may have correctly identified the semantic difference due to distinct method names and overall logic, but failed to recognize the BCB's broad Type-4 label because the lexical and API overlap is low. The model's training on BCB might have not seen such pairs as clones.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to overlapping use of OSGi bundle access, ByteArrayOutputStream, and plugin-related operations, considering them both as 'plugin management' tasks. The broad Type-4 similarity in terms of involving plugin installation and file bundling might have been considered.
- 共享行为: Both use ByteArrayOutputStream and IOUtils.copy for file I/O；Both access bundle or plugin resources；Both involve file creation and manipulation
- 行为差异: A focuses on bundling template files into a JAR and installing plugin; B focuses on Eclipse launch configuration and Maven project validation.；A manipulates bundle entries and manifest; B manipulates XML pom files and properties.；A uses ZipOutputStream; B uses Document and ContentHandlerTemplate for XML processing.；A has uninstall/install plugin lifecycle; B has launch configuration and project setup.
- 修正建议: Improve annotation consistency in BCB to avoid overly broad Type-4 clones；Enhance models to better distinguish domain-specific tasks

### case_id=349 FP boilerplate_overlap

- 方法: `importRoles` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses role names from an XML-like response fetched via URL, building a list of RoleName objects.
- B 摘要: Checks for software upgrades by querying a remote server and a local database, then updates the UI accordingly.
- 静态失败原因: Static BERT models may over-rely on token-level similarities from common boilerplate code (URL, BufferedReader, while loop) and miss the divergent semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels clones only when functions share significant functionality or intent; these functions have minimal overlap beyond URL reading.
- 共享行为: Both open a URL connection and read lines via BufferedReader
- 行为差异: Different purposes: importing roles vs. checking upgrades；Different return types and parameters；B performs database operations and UI manipulation, A does not；A accumulates lines and parses XML; B splits and processes structured data
- 修正建议: Incorporate data flow and control dependencies；Use method signatures and return types as features；Add graph-based encodings to capture program structure

### case_id=350 FN benchmark_preference_bias

- 方法: `copyResource` vs `write`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a resource from a URL or file path to a destination file byte by byte.
- B 摘要: Encrypts ByteBuffer data using SSL/TLS, handling handshaking and wrapping.
- 静态失败原因: Static model likely correctly identified non-clone based on low token overlap and different control flow; it 'failed' because it did not match an erroneous or overly broad BCB annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB label may be due to a very broad interpretation of 'writing data' or a misannotation, as these functions share no meaningful functionality or structural similarity.
- 共享行为: Both involve reading and writing byte data, but with entirely different sources, destinations, and transformations.
- 行为差异: Simple file I/O copy vs. complex SSL encryption；No encryption in A; heavily uses SSLEngine and handshake states in B；Different input/output types: file/URL vs. ByteBuffer arrays；A is a side-effect method; B returns encrypted ByteBuffer array
- 修正建议: Verify the BCB annotation for this pair; it may be a data error.；If annotation is correct, the static model needs additional high-level semantic features to recognize such abstract functional equivalence.

### case_id=351 FN benchmark_preference_bias

- 方法: `main` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using NIO FileChannel.
- B 摘要: Builds a website for editing by processing XML files, applying transformations, and writing output files.
- 静态失败原因: Static BERT models rely on lexical overlap and structural similarity; the low token Jaccard (0.064) and different API usage (FileChannel vs. XML Transformers) cause the model to predict non-clone, missing a possible BCB-broad annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider these clones due to broad functional similarity in file I/O, possibly classifying them as Type-4 (semantic) clones where both functions read from a file and write to another, despite vastly different contexts and additional logic.
- 共享行为: Both perform file I/O operations: reading from a file and writing to another.
- 行为差异: Function A is a simple, single-purpose file copy; Function B involves XML parsing, transformation, and writing multiple files based on a list of pages.；Function B has error handling and debugging output, while Function A does not.；Function B uses StringBuilder and character buffers, whereas Function A uses ByteBuffer.
- 修正建议: Incorporate broader functional semantics, e.g., detecting common I/O patterns beyond lexical tokens.；Use dataflow or control-flow analysis to identify similar subroutines (e.g., both have read-write loops).；Fine-tune on BCB-specific annotations to learn their Type-4 clone preferences.

### case_id=352 FP boilerplate_overlap

- 方法: `main` vs `copyTextFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method of AdapterGenerator that parses command line arguments, reads a Prolog file, generates adapter code, and writes output to a JAR.
- B 摘要: Copies the contents of a source file to a destination file using buffered I/O streams.
- 静态失败原因: The static model likely overemphasized the superficial similarity of exception handling and file I/O APIs, while missing the vast difference in algorithmic logic and intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when two functions perform completely different tasks, even if they share some common API usage (e.g., file I/O). Here, one is a multi-step code generator, the other is a straightforward file copy, so they are not considered Type-3 or Type-4 clones.
- 共享行为: Both handle IOException with try-catch.；Both perform file operations (read/write).
- 行为差异: A is a complex main method for code generation; B is a simple file copy utility.；A parses arguments, reads Prolog, generates classes, and writes JAR; B only copies bytes.；A has multiple stages and uses many libraries; B uses basic Java I/O.；A interacts with class loaders, assemblers, and custom visitors; B has no such complexity.
- 修正建议: Train with more diverse examples to avoid overgeneralizing boilerplate patterns.；Incorporate data flow and control flow features to capture high-level semantics.；Use contrastive learning to distinguish between methods with similar API usage but different behavior.

### case_id=353 FN partial_functionality

- 方法: `callApiPost` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Makes an HTTP POST request with parameters, checks expected status code, and returns the response input stream, handling IO exceptions.
- B 摘要: Reads from a URL or file, delegates to a read method, and returns a status code, handling IO exceptions.
- 静态失败原因: Low token overlap and different method signatures/control flow; the model likely focused on surface-level features and missed the underlying I/O similarity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers them functionally similar as both involve opening a stream and reading data from a network or file, and handling IO errors, representing a broad Type-4 clone.
- 共享行为: Both perform I/O operations to read data from external sources (network or file)；Both handle IOException by either throwing or setting a status
- 行为差异: A uses HTTP POST with parameters and expects a specific response code; B uses GET or file read and returns an integer status；A returns an InputStream; B returns an int status code
- 修正建议: Incorporate structural similarity of I/O patterns；Use data flow analysis to capture stream handling

### case_id=354 FN benchmark_preference_bias

- 方法: `getResponse` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Parses an HTTP GET request from a byte array and returns the corresponding HTTP response (200, 400, or 404) with the resource content.
- B 摘要: Launches a NexOpen project configuration by processing pom.xml files, setting Hibernate properties, and optionally creating a reverse engineering file.
- 静态失败原因: The static BERT model correctly predicted non-clone (0), but BCB labeled it as clone (1). The model's low token Jaccard and semantic dissimilarity led to correct prediction, so it did not fail; rather, the benchmark label is erroneous.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: None
- 共享行为: Both use IOUtils for copying streams；Both use ByteArrayOutputStream；Both handle exceptions
- 行为差异: Completely different domain (HTTP server vs Eclipse launch)；Different input/output types and purposes；Different control flow and libraries used
- 修正建议: Re-evaluate BCB labels for pairs with low token Jaccard and no shared functionality；Consider using more fine-grained semantic similarity measures

### case_id=355 FP lexical_or_api_overlap

- 方法: `downloadModel` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Downloads an RDF model from a URL using HTTP headers and error handling.
- B 摘要: Extracts a full screen video URL from a YouTube page by parsing its HTML content.
- 静态失败原因: A static model like GraphCodeBERT might overemphasize overlapping API tokens (URL, URLConnection, openConnection, getInputStream) and structural patterns (try-catch, InputStream usage) while ignoring the high-level semantic divergence. The method name embeddings and different output types are not sufficiently captured.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels clones only if they implement similar functionality. Here, the methods have completely different purposes (model download vs. video URL extraction), despite sharing some I/O patterns. The low token Jaccard (0.137) and distinct return types further support a non-clone label.
- 共享行为: Both open a URL connection and read from an InputStream.；Both handle exceptions with try-catch blocks.
- 行为差异: downloadModel downloads and returns an RDF Model; getFullScreenUrl parses and returns a String URL.；downloadModel sets specific HTTP Accept and Accept-Language headers; getFullScreenUrl sets doOutput and reads line by line.；getFullScreenUrl performs extensive string parsing for video_id, t, etc.; downloadModel does not parse the input.
- 修正建议: Enhance model with wider context (e.g., method-level comments, class context) to disambiguate purpose.；Incorporate data-flow analysis to differentiate how the I/O streams are consumed.；Add more non-clone training examples with overlapping API usage but distinct goals.

### case_id=356 FP lexical_or_api_overlap

- 方法: `setMembers` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses HTML from a Trac newticket page to extract component and priority options into static arrays.
- B 摘要: Queries a Request Tracker REST API for open tickets in a given queue, retrieves their IDs, and fetches each ticket returning a list.
- 静态失败原因: The model likely focused on lexical overlaps (URL, BufferedReader, while loop, IOException, Pattern/Matcher vs. string parsing) and ignored the high-level purpose difference, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BigCloneBench considers overall functionality: A populates dropdown options for a bug tracker form, B retrieves ticket data. They serve completely different use cases, thus non-clone.
- 共享行为: Both perform HTTP GET requests to fetch data from a remote server；Both read response line by line using BufferedReader；Both have exception handling for IO errors
- 行为差异: A sets static class fields, B returns a List<RTTicket>；A parses HTML select elements, B parses lines starting with 'ticket/'；A uses regex to extract option values, B uses string prefix matching；A has no parameters, B requires queueName and limit
- 修正建议: Incorporate method signature and return type features；Use data flow analysis to distinguish output destinations (static field vs. return)；Train with contrastive examples that penalize API similarity without behavioral alignment

### case_id=357 FN benchmark_preference_bias

- 方法: `doCopyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.85`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination, optionally preserving the last-modified timestamp, using NIO FileChannel for efficient transfer.
- B 摘要: Builds a website for editing by processing XML, applying XSLT transformations, reading control files, and writing output for each page, involving multiple I/O operations and string manipulations.
- 静态失败原因: The static BERT model likely relied on token-level overlap and structural similarity, which are very low here, leading to correct non-clone prediction. However, BCB's label suggests a bias towards high-level behavioral similarities that the static model does not capture, causing a false negative in the benchmark's view.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to very broad Type-4 criteria, possibly considering any method that performs file I/O and throws IOException as semantically similar in a utility context, or due to annotation error.
- 共享行为: Both perform file I/O operations (read/write).；Both can throw IOException.
- 行为差异: doCopyFile is a simple file copy with no content processing.；buildSiteForEdit involves complex XML parsing, XSLT transformation, and conditional logic for multiple pages.；buildSiteForEdit has many parameters and interacts with multiple subsystems (FTP, DOM, etc.).；doCopyFile preserves file modification date; buildSiteForEdit does not.
- 修正建议: Re-evaluate BCB annotation for this pair to confirm if it truly should be a clone.；Improve static models to better distinguish broad I/O utilities from domain-specific complex methods.；Use code summarization or functional role classification to reduce benchmark bias.

### case_id=358 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file by replacing or adding a message for a given locale.
- B 摘要: Copies a file from one path to another, creating directories if needed.
- 静态失败原因: Static BERT models rely on token similarity and structural embeddings; the low token Jaccard (0.22) and different method names made it predict non-clone, while the shared byte-copy loop and file I/O boilerplate were not enough to overcome the semantic differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: None
- 共享行为: Both read from an input file and write to an output file using byte-by-byte loops.；Both use File, FileReader/FileInputStream, FileWriter/FileOutputStream.；Both catch exceptions and print stack traces.
- 行为差异: A parses properties file lines and modifies key-value pairs; B does not modify content.；A conditionally creates a locale-specific file by copying from English; B creates parent directories.；A uses BufferedReader for line-oriented reading; B uses FileInputStream for raw bytes.；A writes with FileWriter and string concatenation; B writes with FileOutputStream.
- 修正建议: Incorporate data flow analysis to distinguish between simple copy and content-modifying operations.；Use fine-grained structural matching that accounts for loop semantics and conditional branches.；Consider normalizing API calls and I/O patterns before comparison.

### case_id=359 FP lexical_or_api_overlap

- 方法: `getContent` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Executes an HTTP request and returns the response body as a string.
- B 摘要: Checks for software upgrades by querying a database and a remote license server, then updates the UI accordingly.
- 静态失败原因: The static model likely overfocused on the shared lexical pattern of 'BufferedReader', 'readLine()', and 'while ((line = ...) != null)' leading to a false positive prediction despite divergent semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when functions have substantially different purposes and logic, even if they share common low-level patterns like reading lines from a stream. The overall behavior and intent are completely different.
- 共享行为: Both use BufferedReader to read lines from a stream
- 行为差异: Function A is a simple HTTP GET and content extraction; Function B involves database queries, UI manipulation, and complex conditional logic.；Function A returns a string; Function B is void and performs side effects.；Function A has no database or UI interactions; Function B has extensive database and UI interactions.；Function B contains multiple stages (UI hide, DB cleanup, license query, processing, UI update) while A is a single-purpose utility.
- 修正建议: Include structural or flow-sensitive features to distinguish between simple content retrieval and multi-step orchestration.；Train on more negative examples that share superficial API usage but differ in overall goal.；Use dataflow analysis to capture the different contexts and output types.

### case_id=360 FN benchmark_preference_bias

- 方法: `copyFile` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies the content of one file to another using buffered stream I/O, handling errors and returning the destination file.
- B 摘要: Builds a site for editing by processing multiple pages, reading XML, applying transformations, and writing output files, with extensive error handling.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on lexical and structural similarity. The low token Jaccard (0.074) and different method names, signatures, and code bodies led the model to correctly predict non-clone, failing to match the possibly overly broad BCB annotation.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB likely labeled this as a clone due to broad Type-4 similarity: both functions perform file I/O and could be seen as 'file handling' utilities, despite vastly different purposes and complexity.
- 共享行为: Both involve file input/output operations such as reading and writing files.；Both handle I/O-related exceptions.
- 行为差异: Function A is a simple file copy utility acting on two files; Function B is a complex multi-step site builder processing many pages.；Function A returns a File or null; Function B returns void and throws multiple exception types.；Function A uses BufferedInputStream/BufferedOutputStream; Function B uses FileReader, StringWriter, and other XML/string manipulation classes.；Function A has linear control flow; Function B has loops, conditional logic, and multiple sub-steps.
- 修正建议: Train models to prioritize high-level semantic purpose over low-level I/O operations.；Incorporate data-flow or control-flow analysis to distinguish simple utilities from complex business logic.；Re-evaluate BCB labels for such pairs to ensure consistency in annotation guidelines.

### case_id=361 FP dataflow_blindspot

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.99`
- 推荐路线: `dynamic_rejection_with_trace`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that parses a Prolog file, generates adapter classes, and writes them to a JAR file.
- B 摘要: Copies a file from source to destination using a buffer.
- 静态失败原因: The model likely focused on superficial similarities such as the presence of File, InputStream, and OutputStream classes, and the general pattern of reading and writing, but failed to capture the vastly different high-level semantics and control flow.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 dataflow_trace_and_outputs。
- BCB 偏好解释: BCB would not consider these clones because they perform fundamentally different tasks with no shared functionality beyond basic file I/O, which is too broad.
- 共享行为: Both involve file I/O operations (reading/writing files).
- 行为差异: Function A parses Prolog and generates code; function B simply copies bytes.；Function A has complex control flow (argument parsing, error handling, iteration over adapter layers); function B uses a simple loop.；Function A uses many specialized classes (Parser, ClassWriter, etc.); function B only uses standard I/O streams.；Function A writes to a JAR file and resources; function B writes to a plain file.
- 修正建议: Enhance the model to incorporate global control flow and dataflow analysis.；Use graph-based representations (e.g., AST or PDG) to distinguish programs with different structural patterns.；Introduce contrastive training examples of non-clones that share API usage but differ in intent.

### case_id=362 FN partial_functionality

- 方法: `doTransfer` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Proxies an HTTP request to another URL, forwarding headers and body, and returning the response.
- B 摘要: Checks for software version by reading a text file from a URL and parsing version numbers.
- 静态失败原因: Static BERT correctly identified non-clone due to low lexical overlap and distinct method names and functionality, but BCB labeled as clone based on superficial API similarity, leading to false negative from BCB perspective.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considered both as 'web access' tasks due to common use of URL, input streams, and exception handling, possibly as a Type-4 clone with similar high-level interaction pattern.
- 共享行为: Open a URL connection；Read input streams (InputStream/Reader)；Handle IOException
- 行为差异: A forwards entire HTTP request (headers, body) and relays response; B only reads a simple text file.；A uses HttpURLConnection with full request method and multiple streams; B uses URL.openStream() and BufferedReader.；A modifies request headers and response; B has no output to the connection.；A involves bidirectional I/O copying; B only reads lines and calls a separate method.
- 修正建议: Use dependency-aware embeddings to differentiate proxy vs. read-only usage；Incorporate control-flow analysis to capture different goals (forwarding vs. parsing)；Filter out boilerplate API patterns that are too generic

### case_id=363 FP boilerplate_overlap

- 方法: `main` vs `uncaughtException`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Processes command-line arguments, reads a Prolog file, parses it, and generates adapter code.
- B 摘要: Handles uncaught exceptions in an SWT application, showing an error dialog and offering to launch the issue tracker.
- 静态失败原因: The static model likely overemphasized common tokens related to exception handling ('catch', 'Exception', 'e', 'getMessage') and ignored the distinct library-specific APIs and overall control flow, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels them as non-clones because they have completely different tasks and only superficial lexical overlap (e.g., exception handling), with low token Jaccard (0.076).
- 行为差异: Different method signatures and return types；Different core functionality: code generation vs. error handling；Different libraries used (Prolog, ASM vs. SWT, logging)；Different control flow and error reporting
- 修正建议: Enhance training data with fine-grained differentiation of error handling boilerplate；Incorporate structural features like method signatures and API calls；Use dataflow or program dependence graphs to capture semantic differences

### case_id=364 FN lexical_or_api_overlap

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies content from a resource (URL or file path) to a destination file using byte streams.
- B 摘要: Copies a source file to a destination file using NIO FileChannel.
- 静态失败原因: Low token overlap (0.235) and distinct method names, parameter types, and I/O patterns (stream vs channel) mislead the static model to ignore the high-level semantic similarity.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB often treats functionally similar file copy operations as clones (Type-4) even with different APIs and parameter styles, as long as the core task matches.
- 共享行为: Both copy data from a source to a destination file；Both close streams/channels after copying；Both handle exceptions during file operations
- 行为差异: Different input types: string resource vs File objects；Different I/O mechanisms: byte streams vs FileChannel；Different exception types: Exception vs IOException；Destination creation: copyResource relies on helper method, copyFile explicitly creates if not exists
- 修正建议: Train on more diverse file copy examples；Incorporate data flow analysis (read from source, write to dest)；Use synonym detection for method names like 'copyResource' and 'copyFile'

### case_id=365 FN boilerplate_overlap

- 方法: `modifyApplicationMessage` vs `extractFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies or adds a property value in a locale-specific properties file, reading existing content and writing back.
- B 摘要: Copies the content of a source file to a destination file using a buffer.
- 静态失败原因: The models likely focused on the shared I/O loop structure (read/write) and ignored the semantically distinct operations inside the loop (property parsing vs raw copy). Overlap in keywords like 'FileReader', 'while', 'read', 'write' biased the representation.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider these as Type-4 (functionally similar) clones because both perform file-to-file data transfer with loop-based reading and writing, which is a common boilerplate pattern that could be considered similar functionality at a high level.
- 共享行为: Both read from a file and write to another file.；Both use a while loop for I/O operations.；Both involve file I/O with byte/character streams.
- 行为差异: Function A manipulates properties files (key-value pairs), while B performs generic binary file copy.；A preserves comments and modifies specific entries; B does no content interpretation.；A handles missing locale file by copying from English file; B does not handle file existence.；A uses BufferedReader and StringBuilder; B uses byte buffer and FileOutputStream.
- 修正建议: Incorporate dataflow analysis to track variable usage beyond I/O handles.；Use structural differencing to detect when inner loop logic differs significantly.；Add attention to domain-specific identifiers (e.g., 'properties', 'messageName').

### case_id=366 FN benchmark_preference_bias

- 方法: `readGeoParserResult` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `preference_memory_with_manual_audit`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Reads geo-parser results from a remote service, parsing XML to extract place names and gazetteer IDs with retries.
- B 摘要: Checks for a new version of jEdit by fetching a version file from a URL and comparing build numbers.
- 静态失败原因: Static BERT models rely heavily on token-level similarity and structural features; the low Jaccard similarity (0.14) and different domain-specific keywords (XML parsing vs version check) caused the model to miss the shared functional pattern.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as clone because both functions follow the same high-level pattern: fetch data from a URL, parse the response line by line, and handle errors. This qualifies as Type-4 semantic clone under BCB's broad definition.
- 共享行为: Both open a URL and read lines from the input stream；Both perform parsing of the retrieved content；Both handle exceptions with error logging or user messages
- 行为差异: Different input parameters: recordContent and getGazeteerIds vs View；Different outputs: Collection of tuples vs void (side effects only)；Different parsing logic: XML vs simple prefix matching；Different retry/error handling: retries up to 3 times vs single attempt with GUI messages
- 修正建议: Enhance the model with features capturing functional semantics, such as API call sequences or control flow patterns；Use contrastive learning on functionally similar but lexically different code pairs；Incorporate data augmentation that transforms code while preserving functionality (e.g., variable renaming, loop conversions)

### case_id=367 FP lexical_or_api_overlap

- 方法: `copy` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel.
- B 摘要: Parses comma-separated strings and populates multiple sets and maps for Tibetan character processing.
- 静态失败原因: The model likely overfitted to the presence of 'IOException' and 'File' related keywords, plus both are static void methods. The extreme length of code_b and low token overlap may have been ignored due to attention dilution.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions perform completely different tasks even if some lexical elements overlap. These two functions have no shared functionality.
- 共享行为: Both are static methods；Both handle IOException (though implicitly in A via throws, explicitly in B via catch)
- 行为差异: Method A performs file I/O with FileChannel; Method B parses string tokens and builds data structures；Method A has no parameters for file paths; Method B uses instance fields；Method A is very short (6 lines); Method B is very long (200+ lines)；Method A uses transferTo; Method B uses StringTokenizer and HashSet
- 修正建议: Add negative examples with similar lexical patterns to train model to ignore superficial commonalities；Enhance model to better handle long-range dependencies and overall function semantics；Use abstract syntax tree or control flow graph features to capture structural differences

### case_id=368 FN benchmark_preference_bias

- 方法: `getJSONData` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Fetches JSON data from a URL via HTTP GET and returns it as a JSONObject.
- B 摘要: Initializes static sets and a map by parsing comma-separated string constants and reading a configuration file for Tibetan transliteration.
- 静态失败原因: Static BERT/GraphCodeBERT actually predicted non-clone (0), which appears correct. The model did not fail; instead, the BCB annotation is likely a false positive. The model correctly identified the lack of semantic similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to superficial similarities like using BufferedReader and handling exceptions, or because both methods involve parsing input. However, their overall functionality is distinct.
- 共享行为: Both involve reading and parsing text data, but with completely different sources and formats.
- 行为差异: Function A performs network I/O and JSON parsing; Function B initializes static data structures from string constants and file I/O.；Function A returns a JSONObject; Function B is void and modifies static fields.；Function A uses HTTP client and JSON tokener; Function B uses StringTokenizer and custom file parsing.
- 修正建议: Re-evaluate the BCB annotation for this pair, as the functions have distinct purposes and no meaningful semantic overlap.

### case_id=369 FP partial_functionality

- 方法: `checkForUpgrade` vs `retrieveTemplate`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Checks for software upgrades by querying a license server and updating the installation database.
- B 摘要: Retrieves a blog template from a URL and caches it.
- 静态失败原因: The model likely over-focused on the similar API usage pattern (URL, BufferedReader, while loop) and ignored the broader context and different semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB likely labels these as non-clones because they belong to distinct application domains and have fundamentally different logic beyond the shared HTTP reading snippet.
- 共享行为: Both open a URL and read content line by line into a string
- 行为差异: Different overall purpose: upgrade checking vs template retrieval；Different side effects: database writes and UI updates vs caching only；Different parameters and return types；One is public static void, the other private non-static returning String
- 修正建议: Enhance model to capture global control flow and data dependencies；Include structural constraints like method signature and call hierarchy；Use contrastive learning to distinguish similar API usage in different contexts

### case_id=370 FN benchmark_preference_bias

- 方法: `main` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a hardcoded URL, decompresses its zip entries, and writes each entry to a local file.
- B 摘要: Handles an HTTP GET request by translating the request path to a local file and streaming its content to the response output.
- 静态失败原因: The model correctly predicted non-clone because it captured the distinct semantics (download/unzip vs. servlet file server) and API usage (ZipInputStream vs. HttpServletRequest). It did not fail; the BCB label is likely incorrect or based on overly broad criteria.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB might have labeled them as clones due to the common high-level pattern of reading from an input source and writing to an output source using streams, considering them Type-4 or broad Type-3, or the annotation may be a mistake.
- 共享行为: Both involve reading from an input stream (file or network) and writing to an output stream (file or response).；Both handle I/O exceptions with throws clauses.
- 行为差异: A uses zip decompression; B does not.；A writes multiple files; B writes a single file.；A has a hardcoded URL; B uses the request path.；A is a main method; B is a servlet method.
- 修正建议: Re-examine the BCB annotation for this pair; consider removing or correcting the label.；If the model must align with BCB, incorporate more abstract I/O stream patterns into feature representation, but this may harm precision.

### case_id=371 FN benchmark_preference_bias

- 方法: `modifyApplicationMessage` vs `transport`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Modifies a properties file by setting or adding a key-value pair for a given locale.
- B 摘要: Recursively copies files from a source directory to a destination directory using FileChannel.
- 静态失败原因: Static BERT/GraphCodeBERT likely failed because of low token overlap and differing API usage (Properties vs FileChannel), leading to low similarity scores.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as clone due to a broad interpretation of file manipulation tasks, but typical BCB standards require more specific functional similarity.
- 共享行为: Both perform file I/O operations.
- 行为差异: A modifies property files; B copies files.；A uses Properties file format; B uses file channels for copy.；A creates files if missing; B recursively traverses directories.
- 修正建议: Use more robust semantic representations (e.g., data flow analysis) that capture the core functionality.；Consider structural similarity in addition to token overlap.；Train with more diverse examples to reduce bias towards lexical similarity.

### case_id=372 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a localized properties file by copying a default English file if the target locale file is missing, then reads, modifies, or adds a message property.
- B 摘要: Copies a file from a source to a destination using a buffer.
- 静态失败原因: Static BERT models typically rely on token and AST surface similarity; the low token Jaccard (0.163) and different method names lead to low similarity. The shared file copy behavior is a small part of the longer first function, making it hard for static models to detect without data flow or deeper semantic understanding.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label them as clones because both involve file I/O and specifically both include file copying; the partial overlap in file copy behavior is considered sufficient for Type-4 semantic clone annotation in BCB.
- 共享行为: Both perform file copying from a source to a destination file.；Both handle file I/O with try-catch and stream management.
- 行为差异: modifyApplicationMessage additionally reads, parses, and modifies properties file content, while copyFile only copies raw bytes.；modifyApplicationMessage has conditional logic to copy a default file if target missing, and later updates a specific property.；copyFile is a generic utility method with no property-specific logic.
- 修正建议: Enhance models with data-flow analysis to capture I/O operations and partial functional overlap.；Use graph-based representations that highlight sub-structures like file copy patterns.；Consider contrastive learning that emphasizes partial functional similarity.

### case_id=373 FP long_range_semantics

- 方法: `readData` vs `patch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated string constants to populate various sets and reads a configuration file to initialize a transliteration mapping for Tibetan Wylie.
- B 摘要: Checks if mods are empty, then copies the Minecraft jar to a backup and opens it for patching.
- 静态失败原因: The static model likely overgeneralized from common Java idioms like loops and exception handling, missing the entirely different high-level semantics of the two functions.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB labels based on functional similarity; these functions have no common purpose or behavior, so they are not clones.
- 共享行为: Both use standard Java I/O and collection classes.
- 行为差异: Function a is a complex data loading routine for linguistic processing, while function b is a simple file backup and jar access for game modding.；They operate on completely different data structures and have no functional overlap.
- 修正建议: Improve model sensitivity to overall program purpose beyond local patterns.；Incorporate data flow or control flow analysis to distinguish distinct functionalities.

### case_id=374 FN partial_functionality

- 方法: `setMembers` vs `runInternal`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches a Trac newticket page and parses HTML select elements to extract component and priority options.
- B 摘要: Opens an HTTP/HTTPS connection to a URL, handles redirects, reads content, and processes it as an OPDS catalog or downloads a book.
- 静态失败原因: The token Jaccard similarity is very low (0.092), and the method names and surrounding context are completely different. Static models relying on lexical or syntactic features fail to capture the high-level behavioral similarity of network-based data retrieval and parsing.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: Both functions involve fetching data from a URL via HTTP, reading the response stream, and extracting structured information. Despite different application domains and specific parsing logic, the overall pattern of network I/O followed by stream processing is considered a Type-4 clone in BigCloneBench, which allows functional similarity without exact code match.
- 共享行为: Open a URL and establish a network connection；Read input stream from the connection；Parse or process the streamed data；Handle exceptions like MalformedURLException or IOException
- 行为差异: Function A specifically parses HTML for <select> elements; Function B handles multiple content types (OPDS, book downloads).；Function A uses simple regex to extract option values; Function B uses an XML pull parser or other handler.；Function A stores extracted data in class-level arrays; Function B stores results in a handler and passes to callback.；Function B includes connection setup (user-agent, timeouts, redirects) absent in A.
- 修正建议: Enrich training data with examples of network I/O plus parsing tasks across different domains.；Use a model that captures program flow and data dependencies (e.g., dataflow graphs) rather than just token sequences.；Include semantic role labeling for common operations like 'open connection', 'read stream', 'parse content'.

### case_id=375 FP lexical_or_api_overlap

- 方法: `getJSONData` vs `sendPost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Performs an HTTP GET request, reads the response, and parses it as a JSONObject.
- B 摘要: Performs an HTTP POST request with parameters and returns the response as a String.
- 静态失败原因: Static BERT likely over-relied on lexical overlap (e.g., BufferedReader, URL, try-catch) and API tokens, missing the semantic difference in HTTP method and return type.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as non-clone because the HTTP method and data handling differ significantly, and partial functionality similarity is not enough to consider them Type-3/4.
- 共享行为: Both perform an HTTP request to a URL；Both read the response line by line；Both handle exceptions；Both return the response content
- 行为差异: GET vs POST HTTP method；One parses JSON, the other returns raw string；Different HTTP client libraries (HttpClient vs HttpURLConnection)；Different error handling (printStackTrace vs showMsg)
- 修正建议: Incorporate structural features like HTTP method type；Use dataflow analysis to track request method and response parsing；Fine-tune on datasets with clear method semantics

### case_id=376 FN partial_functionality

- 方法: `getEncoding` vs `postXml`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts the character encoding from an HTTP response by checking headers and body for charset information.
- B 摘要: Sends an XML payload via HTTP POST and returns the full response body as a string.
- 静态失败原因: Static BERT/CodeBERT models rely heavily on token overlap and surface-level API calls. These functions share few tokens (Jaccard 0.23) and use different keywords (extractEncoding vs setRequestProperty, charset vs SOAPAction), so the model fails to recognize the shared HTTP-response-reading skeleton.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may classify these as Type-4 (semantic) clones because both implement a common pattern: open an HTTP connection, read the response, and return a derived string. The annotation guidelines often accept such broad functional similarity in utility methods.
- 共享行为: Both open an HTTP URL connection.；Both read from the input stream using a BufferedReader.；Both loop through lines of the response.；Both return a String (encoding or full response).
- 行为差异: getEncoding does not send any request body; postXml sends an XML payload.；getEncoding examines headers and body for charset; postXml returns the entire body.；getEncoding returns a short encoding string or a default; postXml returns the full response.；getEncoding implicitly uses GET; postXml explicitly uses POST.
- 修正建议: Incorporate data-flow or control-flow graph features to capture structural similarity.；Train on more diverse patterns of HTTP-response reading functions to learn the common template.；Use a model that abstracts away specific variable names and API calls, focusing on the sequence of operations (open connection, get input stream, read lines, return).

### case_id=377 FN partial_functionality

- 方法: `doVersionCheck` vs `read`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs version checking by reading a remote property file and comparing build numbers.
- B 摘要: Opens a URL or file stream and delegates reading to another method, returning a status code.
- 静态失败原因: Static models may have been misled by the superficial lexical differences (method names, return types, specific parsing) and lacked the dataflow analysis to recognize the high-level semantic similarity of network I/O.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to the shared pattern of URL opening and error handling, but the functions differ significantly in purpose and logic, making the clone label questionable.
- 共享行为: Both open a stream from a URL and handle IOException.
- 行为差异: A reads text lines and parses for version/build strings; B reads raw bytes and calls another read method.；A involves UI interaction (wait cursor, messages); B is a low-level I/O method.；A returns void; B returns int status.
- 修正建议: Incorporate dataflow analysis to capture common I/O patterns.；Use contrastive learning to focus on high-level intent rather than low-level details.

### case_id=378 FN partial_functionality

- 方法: `testNetworkHTTP` vs `postRequest`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A test method that performs multiple HTTP GET requests to fixed URLs, discarding all response content.
- B 摘要: A utility method that performs a single HTTP POST request with parameters from a HashMap and returns the response as a string.
- 静态失败原因: The static model likely focused on method names, signatures, and token-level similarity, which are low (Jaccard 0.20). It failed to recognize the underlying structural similarity of the HTTP request pattern, as the code bodies differ significantly in details like parameter handling and HTTP method.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers this a clone because both functions implement the core functionality of performing an HTTP request, opening a connection, reading input, and handling exceptions, which is a common pattern in network communication tasks. Differences in HTTP method, number of requests, and return value are considered secondary in Type-3/Type-4 clone detection.
- 共享行为: Both functions make HTTP network requests using URL and URLConnection.；Both read the response via BufferedReader and InputStreamReader.；Both handle exceptions with printStackTrace.；Both follow a try-catch pattern for network operations.
- 行为差异: A uses HTTP GET, B uses HTTP POST.；A sends multiple requests, B sends a single request.；A discards the response, B returns it as a string.；A is void, B returns String.
- 修正建议: Train the model to recognize structural patterns like URL->openConnection->getInputStream->BufferedReader as a common idiom regardless of HTTP method.；Incorporate data flow analysis to capture that both functions use the same core I/O operations.；Augment training data with more Type-3/Type-4 clones that share partial functionality but differ in specifics.

### case_id=379 FN lexical_or_api_overlap

- 方法: `setMembers` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Fetches a webpage and extracts option values from HTML select elements using regex.
- B 摘要: Parses a configuration file and tokenizes string fields to populate multiple hash sets and mappings.
- 静态失败原因: Low lexical overlap (token Jaccard 0.10) and completely different API calls (URL/Regex vs StringTokenizer/File) led to low similarity score.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled as clone due to both being initialization routines that parse input and fill fields, but the actual tasks are too different for typical Type-4 clones.
- 共享行为: Both are private static void methods；Both catch IOExceptions and print messages；Both populate static data structures
- 行为差异: Data source: URL vs file/string variables；Parsing: regex vs StringTokenizer；Output: arrays vs sets/maps；Error handling: different messages
- 修正建议: Incorporate functional semantic understanding beyond syntax；Use data-flow analysis to capture common patterns of input parsing and field assignment

### case_id=380 FP boilerplate_overlap

- 方法: `md5` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Computes MD5 hash of input string and returns hex representation, with logging and error handling.
- B 摘要: Handles a web request to classify a concept by processing parameters, validating session, calling external service via HTTP, parsing XML response, and setting session attributes.
- 静态失败原因: The static BERT/GraphCodeBERT model likely overgeneralized from overlapping boilerplate code (logging, StringBuffer usage, for loops, try-catch) and the presence of common Java keywords, leading to a false positive despite low token Jaccard similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones when functions have distinct purposes and minimal shared functionality, even if some common coding patterns exist. Here, the functions are from entirely different domains (cryptography vs. web request handling) with no semantic equivalence.
- 共享行为: Both use StringBuffer for building strings；Both have loops (for/while) with index variable i；Both include logging statements (logger.debug/warn)；Both handle exceptions in try-catch blocks
- 行为差异: Function A computes a cryptographic hash; function B performs a complex business logic workflow involving network I/O and XML parsing.；Function A returns a hex string; function B returns an ActionForward (Struts control flow).；Function A handles only an input string; function B processes multiple request parameters, session, and external services.；Function A's error handling returns empty string; function B's error handling sets status and forwards to failure page.
- 修正建议: Train model to better distinguish domain-specific logic from generic boilerplate；Incorporate structural information like method signatures and call graphs；Use attention masking to reduce focus on log statements and other boilerplate；Add negative sampling with similar boilerplate but different semantics

### case_id=381 FN long_range_semantics

- 方法: `copyIconFiles` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies icon files (16x16 and 32x32) from annotation paths to a destination directory using FileChannel.
- B 摘要: Modifies a named message value in a locale-specific properties file, creating the file from English defaults if missing.
- 静态失败原因: The static model likely relied on token similarity (Jaccard = 0.099) and failed to capture the high-level functional similarity that BCB annotators might have seen. Alternatively, the model might have been too strict, missing the abstract file manipulation pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled these as clones under a broad Type-4 interpretation, considering both are 'file manipulation methods' that read and write data, despite different specific tasks.
- 共享行为: Both perform file I/O operations (reading and writing files).；Both use try-catch blocks and print stack traces on exception.
- 行为差异: A copies entire files; B reads line-by-line and edits a specific line.；A uses FileChannel for efficient transfer; B uses Reader/Writer with string building.；A handles two icons; B handles a single message in a properties file.；A uses annotations as input; B takes locale, messageName, and messageValue.
- 修正建议: Enhance model with abstract syntax tree or control flow graph features to capture structure.；Use contrastive learning on paired file I/O operations with different specific tasks.；Incorporate function name or context embeddings to infer high-level purpose.

### case_id=382 FN partial_functionality

- 方法: `getEncoding` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts character encoding from HTTP response headers or content.
- B 摘要: Checks for software version updates by parsing a version file from a URL.
- 静态失败原因: Low lexical overlap and different method names, domain-specific strings, and distinct control flow caused the model to miss the structural similarity of reading lines from a URL.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels these as clones due to the shared functional pattern of reading from a URL and parsing lines for specific information, despite different domains.
- 共享行为: Open a URL and read its content line by line；Use BufferedReader and InputStreamReader；Parse lines for specific substrings
- 行为差异: A checks HTTP headers before reading content; B only reads lines directly；A returns a default encoding if not found; B calls another method and shows error dialogs；Error handling: A uses try-finally to close reader; B catches IOException and shows error dialog
- 修正建议: Incorporate dataflow analysis to highlight I/O patterns；Train with contrastive learning on functional similarity examples；Use graph-based representations capturing object interactions

### case_id=383 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for a new version of jEdit by reading a version file from a URL and comparing build numbers.
- B 摘要: Checks for product upgrades by querying a remote server, parsing license and upgrade XML, and updating a local database.
- 静态失败原因: The model likely overemphasized common API usage (URL, BufferedReader, InputStream, openStream, readLine, close) and the shared high-level purpose of checking for updates, while ignoring fundamental differences in parsing, data sources, and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clones because despite both being 'check for update' functions, they have very low token overlap (Jaccard=0.10) and belong to completely different application contexts with distinct logic and data handling.
- 共享行为: Both use URL to fetch remote content；Both use BufferedReader and InputStreamReader to read response；Both parse the response to extract version/upgrade info；Both perform conditional actions based on the parsed result
- 行为差异: doVersionCheck only compares a single version string; checkForUpgrade handles multiple upgrades, licenses, and database operations；doVersionCheck uses simple line prefix matching; checkForUpgrade uses XML-like row/field splitting；checkForUpgrade includes database delete/insert, UI component visibility toggling, and error handling for license status；doVersionCheck is a static method in jEdit; checkForUpgrade is a method in an upgrade system for TegsoftCC
- 修正建议: Incorporate control flow and data flow analysis to differentiate processing logic；Use contrastive learning on hard negative examples with similar API usage but different semantics；Add more structural features like AST edit distance or program dependency graphs

### case_id=384 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `getPagina`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft handshake by validating username and optionally authenticating via HTTP or sending a login packet.
- B 摘要: Fetches and returns the entire content of a given URL as a string, handling exceptions.
- 静态失败原因: The static model likely overemphasized lexical and API overlap (URL, BufferedReader, InputStreamReader) and ignored the high-level semantic and structural differences, such as conditional logic and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions differ in purpose and control flow; the URL reading fragment is only a small part of A's overall authentication logic, not the main functionality.
- 共享行为: Both create a URL object and open an HTTP connection to read lines via BufferedReader.
- 行为差异: A has conditional logic based on username validation, while B directly fetches the URL.；A sends network packets (Packet1Login) or shuts down the connection; B only returns the fetched content.；A parses a hex string and uses a specific authentication URL; B is generic and uses any URL.；A handles exceptions by printing stack trace and shutting down; B catches exceptions and returns error string.
- 修正建议: Incorporate control flow and data flow analysis to differentiate side effects.；Train with more negative examples having high API overlap but different semantics.；Use structural features like graph representations of the code.

### case_id=385 FP boilerplate_overlap

- 方法: `loadBinaryStream` vs `readData`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Loads a binary stream from an HTTP request and writes it to the response output stream with headers.
- B 摘要: Reads configuration data from comma-separated string fields and a data file, populating various sets and maps for Tibetan text processing.
- 静态失败原因: The static model might have focused on superficial commonalities like 'private static' methods and I/O operations, or it may have misclassified due to low token overlap but other features (e.g., length, control flow) being similar.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the two functions do not share any significant functional similarity; one is about streaming binary data in a servlet, the other is about parsing configuration strings and file data.
- 共享行为: Both are private/static methods that perform some initialization or data handling.
- 行为差异: Function A is a web request handler writing binary data to response; Function B is a data parsing and setup routine for sets and maps.；Function A uses HTTP objects and IOUtils; Function B uses StringTokenizer and file reading.
- 修正建议: Improve training to emphasize functional semantics over boilerplate patterns.；Use data-flow or call-graph information to distinguish different API usage.

### case_id=386 FP lexical_or_api_overlap

- 方法: `getWebPage` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads entire web page content line by line and returns it as a single string, throwing a custom error on failure.
- B 摘要: Reads web page content line by line with optional HTTP authentication, writes each line to a temporary file, and updates a UI status label; does not return content.
- 静态失败原因: Static models may have overemphasized the lexical overlap (BufferedReader, InputStreamReader, URL) and the overall 'read URL' pattern, ignoring differences in parameters, return type, side effects, and error handling.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functional similarity beyond just reading from a URL. The presence of authentication, file writing, and UI updates in function B makes it functionally distinct from function A, so BCB marks them as non-clones.
- 共享行为: Both open a URL and read lines using BufferedReader.；Both handle IO exceptions (though differently).
- 行为差异: Function A returns the content as a String; function B writes to a file and returns nothing.；Function B includes HTTP Basic authentication; function A does not.；Function B updates a UI label and prints progress to console; function A does not.；Function A throws a generic Error on IOException; function B declares and throws IOException.
- 修正建议: Include data-flow analysis to distinguish string concatenation vs. file writing.；Consider return types and method signatures more explicitly.；Incorporate structural features like control flow and exception handling differences.

### case_id=387 FN partial_functionality

- 方法: `getFile` vs `readAndRewrite`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its endpoint attribute, saves to a temp directory, and returns the file path.
- B 摘要: Reads a DICOM file, parses pixel data, and rewrites the data to an output file without returning a value.
- 静态失败原因: Low token Jaccard similarity and use of completely different domain-specific APIs prevented the static model from recognizing the broad functional similarity at the input-output level.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as instances of file transformation tasks where input is read, transformed, and output is written, despite different domain-specific libraries and processing details.
- 共享行为: Both functions involve reading input data (from URL or file), processing it, and writing output to a file.
- 行为差异: Different domains: WSDL XML manipulation vs DICOM medical image processing.；Different processing steps: A modifies XML attributes; B reads and writes pixel data with no explicit modification.；Different return types: A returns a String path; B returns void.
- 修正建议: Use flow-aware models that capture high-level input-output transformations.；Incorporate more abstract representations of file I/O and data processing tasks.

### case_id=388 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a version check URL, reads lines to extract version and build info, then compares with current jEdit build to show update status or message.
- B 摘要: Fetches a Google Images search URL for the current track's artist and album, reads the entire HTML response, and extracts image URLs from href attributes.
- 静态失败原因: The static BERT/GraphCodeBERT model likely over-relied on common lexical and API patterns (URL, BufferedReader, readLine, try-catch) without capturing the distinct functional semantics and control flow differences.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the overall functionality differs significantly (version checking vs. image search), even though both involve network I/O and line parsing. The annotation preference for Type-3/4 is not lenient enough to consider such different behaviors as clones.
- 共享行为: Both open a URL connection and read response line-by-line using BufferedReader.；Both perform string parsing on the read lines.；Both handle exceptions with error dialogs.
- 行为差异: Function A reads specific lines starting with '.version' and '.build' for a version check, while Function B reads the entire HTML and uses regex to extract image URLs.；Function A uses URL.openStream() and Function B uses HttpURLConnection with custom headers.；Function A interacts with GUI wait cursor and messages, while Function B updates a static list and resets a static location.；Function A compares version strings, Function B concatenates strings and replaces characters.
- 修正建议: Incorporate data flow analysis to track how parsed data is used differently.；Add context-aware embeddings that consider method names and surrounding class context.；Use contrastive learning with harder negative examples that share API calls but different functionality.

### case_id=389 FN partial_functionality

- 方法: `invoke` vs `wordFrequency`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A generic RPC method that sends HTTP POST requests, handles retries, and deserializes JSON responses.
- B 摘要: A specific method that fetches a URL by replacing a placeholder, reads the response line by line, and returns the first matched integer frequency.
- 静态失败原因: The static BERT model likely focused on low lexical overlap (token Jaccard 0.16) and different method names, missing the higher-level structural similarity in HTTP request-response handling.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider these as Type-4 clones because both functions follow a common pattern of network I/O with URL handling and line-by-line reading, despite different HTTP methods and purposes.
- 共享行为: Both perform HTTP requests to a remote server.；Both read the response line by line using BufferedReader.；Both handle exceptions (ConnectTimeoutException vs MalformedURLException/IOException).；Both return a value based on the response content.
- 行为差异: A uses HTTP POST while B uses HTTP GET.；A includes retry logic on timeout, B does not.；A deserializes JSON into a generic type, B matches a regex pattern to extract an integer.；A builds a full response body string, B processes lines incrementally.
- 修正建议: Incorporate structural features like control flow graphs or data flow graphs to capture shared I/O patterns.；Use contrastive learning to emphasize behavioral similarity over lexical overlap.；Include API call sequences (e.g., URL.openStream, BufferedReader, etc.) as features.

### case_id=390 FP boilerplate_overlap

- 方法: `doVersionCheck` vs `executePost`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a version-check URL, parses lines for build versions, and displays error on failure.
- B 摘要: Executes an HTTP POST request with parameters and returns the response string.
- 静态失败原因: The static BERT model likely overemphasized the shared I/O pattern (URL, BufferedReader, readLine) and common API tokens, missing the different method names, logic, and purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would likely label this as non-clone because the functions serve distinct purposes (version checking vs. generic POST execution) despite sharing a common URL reading boilerplate. BCB values functional relevance over structural similarity.
- 共享行为: Both create a URL object and open an input stream；Both use BufferedReader to read lines from the stream；Both close the stream after reading
- 行为差异: A uses GET (default) for version check, B uses POST with parameters；A parses lines for specific prefixes (.build, .stablebuild), B appends all lines to a response buffer；A shows an error dialog on IOException, B prints stack trace and returns null；A is void and calls another method on success, B returns a String
- 修正建议: Incorporate data-flow and control-flow analysis to distinguish actual read/write patterns；Use method-level semantic similarity that considers the method's overall goal；Add negative mining for functions sharing only boilerplate but differing in intent

### case_id=391 FP lexical_or_api_overlap

- 方法: `main` vs `copyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses command-line arguments, reads a Prolog file, parses it, generates adapter classes, and writes them into a JAR file.
- B 摘要: Copies a file from source to destination using FileChannel with proper resource management.
- 静态失败原因: The model likely over-relied on shared API tokens like 'File', 'IOException', 'try', and resource closing patterns, ignoring the drastically different control flow and domain logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they have entirely different functionality and purpose, despite some superficial API overlap.
- 共享行为: Both perform file I/O operations (reading/writing files).；Both handle exceptions and close resources.
- 行为差异: Function A is a complex code generation pipeline; B is a simple file copy.；A involves parsing, code generation, and JAR creation; B only copies bytes.；A has many dependencies on specific libraries; B uses standard Java NIO.
- 修正建议: Incorporate structural awareness (e.g., AST or data-flow graphs) to distinguish complex pipelines from simple utilities.；Enhance context understanding via larger receptive fields or attention mechanisms.

### case_id=392 FP boilerplate_overlap

- 方法: `main` vs `testCodingEmptyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that generates adapter code from a Prolog file, performing parsing, class loading, and output writing.
- B 摘要: Unit test that writes data to a buffer, transfers from a temp file using an encoder, and asserts the output.
- 静态失败原因: The model likely focused on superficial lexical overlaps such as common Java I/O patterns (File, streams) and boilerplate code, ignoring the distinct high-level logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions have no semantic similarity and perform entirely different tasks.
- 共享行为: Both involve file handling and I/O operations
- 行为差异: Different overall purpose: code generation vs. unit testing；Different control flow and complexity；Different APIs and libraries used
- 修正建议: Improve training to include more diverse negative pairs with similar API usage；Incorporate structural differences or method-level semantics

### case_id=393 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `writeFileToFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a specific locale by reading, editing, or adding a key-value pair, with fallback to copying an English file if the target does not exist.
- B 摘要: Copies the entire content of a source file to a destination file using NIO FileChannels, with an optional append mode.
- 静态失败原因: The static BERT/GraphCodeBERT model likely failed due to low token overlap (Jaccard 0.135) and different method names/signatures. The model may have focused on high-level semantics (one modifies properties, the other copies files) without recognizing that the file-copying subtask in A matches B's complete behavior. The model is not sensitive to partial functionality overlap embedded in longer functions.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled this as a clone because both functions perform a file copy operation as a key subtask. In A, the file-copying logic (copying English file when locale file missing) is structurally similar to B's entire logic. BCB's broad Type-3/Type-4 annotations sometimes accept partial functionality overlap, especially when the core algorithm is the same.
- 共享行为: Both involve reading from one file and writing to another file, performing a file copy operation.；Both handle file I/O with proper resource cleanup (closing streams/channels).
- 行为差异: A manipulates the content of a properties file (splitting lines, matching keys, modifying values) while B simply transfers bytes without interpretation.；A creates a new locale file by copying the English file if it does not exist; B always overwrites or appends to an existing file.；A uses character-based reading (BufferedReader/FileReader) and writing (FileWriter), while B uses NIO channels for efficient byte transfer.；A handles exceptions with a catch block that prints stack trace; B throws IOExceptions to the caller.
- 修正建议: Train the model to detect subgraph or subtask clones, e.g., by using dataflow analysis to identify embedded code snippets that are functionally similar.；Include more examples of Type-4 clones where one function implements a super set of another function's behavior.；Enhance the model with structural matching of I/O patterns (e.g., read-write loops) rather than relying solely on token similarity.

### case_id=394 FP lexical_or_api_overlap

- 方法: `handleHandshake` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles Minecraft handshake by validating username and performing online authentication via HTTP.
- B 摘要: Loads an OSGi FrameworkFactory by reading a service configuration file via classloader resource.
- 静态失败原因: The model likely overemphasized lexical and API overlaps (URL, BufferedReader, InputStreamReader) and structural similarities (try-catch, loop) while missing the domain-specific differences in purpose and logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would consider these non-clones because their functionality is entirely different despite similar I/O patterns; they are not functionally similar even at a high level.
- 共享行为: Both open a URL or resource stream and read lines using BufferedReader.；Both handle I/O exceptions with try-catch or finally blocks.
- 行为差异: A validates a username and interacts with an external authentication server; B reads a service file and instantiates a class via reflection.；A sends network packets or shuts down connection; B throws an exception if factory not found.；A uses the Minecraft session and network manager; B uses classloader and OSGi framework.
- 修正建议: Incorporate higher-level semantic understanding, e.g., by analyzing method names, context, or dependencies.；Train on tasks that require distinguishing between superficially similar but semantically different code.；Use more robust feature extraction that captures program intent beyond token overlap.

### case_id=395 FN partial_functionality

- 方法: `invoke` vs `retrieveTemplate`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: RPC invoke that sends HTTP POST request and deserializes JSON response with retry logic.
- B 摘要: Retrieves a web template from URL, caches it, and returns as string.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on lexical token overlap and overall semantics, which are low due to different method names, signatures, and control flow, causing it to miss the partial structural similarity in the I/O reading snippet.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a Type-3/Type-4 clone because both functions contain a significant common code pattern of reading from a URL line by line using BufferedReader and StringBuilder, even though overall functionality differs.
- 共享行为: Read from a URL (HTTP or URL)；Use BufferedReader and StringBuilder to accumulate content line by line；Close the reader after reading
- 行为差异: A uses HTTP POST with entity; B uses plain URL openStream；A includes retry logic on ConnectTimeoutException; B has no retry；A deserializes JSON response to object type; B returns raw string；A does not cache; B caches result in cachedTemplate
- 修正建议: Enhance model to recognize common sub-patterns like stream reading across different contexts；Incorporate data flow analysis to detect similar I/O operations；Use clone detection metrics that allow for partial structural similarity

### case_id=396 FP lexical_or_api_overlap

- 方法: `sendPost` vs `readIntoList`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with parameters and returns the response as a concatenated string.
- B 摘要: Reads HTML content from a URL, parses anchor tags to extract command names, creates JMenuItems with action listeners, and adds them to a map.
- 静态失败原因: The model likely overemphasized the shared use of URL, BufferedReader, and readLine patterns, along with the try-catch structure, while missing the semantic intent signaled by method names, return types, and the distinct operations (sending data vs. parsing HTML).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels as non-clone because the functions have entirely different purposes (sending HTTP POST vs. parsing HTML for GUI menu items), despite some superficial API overlap.
- 共享行为: Both use URL and BufferedReader to read line-by-line from a URL connection.；Both handle exceptions with try-catch blocks.；Both close the BufferedReader after reading.
- 行为差异: A sends an HTTP POST request with parameters via PrintWriter; B performs a GET request via url.openStream() without sending data.；A returns a String; B modifies a Map and creates GUI components.；A sets request properties and handles output; B parses HTML and creates action listeners.；A uses HttpURLConnection with setDoOutput and setDoInput; B uses URL.openStream() directly.
- 修正建议: Incorporate method name embeddings and return type information.；Use dataflow analysis to distinguish between sending data and reading only.；Add training examples that contrast similar API usage with different goals.；Improve attention to long-range dependencies and overall function purpose.

### case_id=397 FP long_range_semantics

- 方法: `md5` vs `perform`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Computes MD5 hash of input string and returns hex-encoded digest.
- B 摘要: Performs a Struts action that classifies a concept by processing HTTP request, session data, and XML, returning an ActionForward.
- 静态失败原因: The static model likely focused on the presence of try-catch blocks or method signature patterns, failing to capture the vast semantic difference due to the long length of function b and lack of understanding of the Struts framework.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB would not consider these clones because they have completely different functionality, input/output types, and code length; the only superficial similarity is exception handling.
- 行为差异: Function a is a simple cryptographic hash; function b is a complex web request handler.；Function a has one input (String) and returns a String; function b has multiple inputs (ActionMapping, ActionForm, etc.) and returns an ActionForward.；Function a involves no I/O except possibly exception; function b performs HTTP connections, session management, XML parsing.
- 修正建议: Improve handling of long-range dependencies in the model, e.g., by using graph-based representations or hierarchical attention.；Increase training data with long functions to better distinguish boilerplate from core logic.；Incorporate type information and method call context to detect framework-specific semantics.

### case_id=398 FP boilerplate_overlap

- 方法: `addQDInformation` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a local or remote file containing QD information and updates internal data structures with parsed values.
- B 摘要: Downloads content from a URL with optional authentication, writes it to a temporary file, and updates a GUI progress label.
- 静态失败原因: The static model likely overfitted on the common boilerplate patterns (BufferedReader, URL opening, try-catch) and missed the semantic mismatch in the loop bodies and the overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely marked this as non-clone because while both involve reading from URLs, the core functionality (parsing QD info vs. downloading VRML) and output are completely different, making them Type-4 (similar functionality but different purpose) which is typically not considered clone in BCB.
- 共享行为: Both use BufferedReader to read line-by-line from an input stream；Both handle network I/O (URL opening) and local file I/O；Both catch IOException
- 行为差异: Code A parses specific line prefixes ('pg', 'pt') to extract hexadecimal dates and project values; Code B writes all lines verbatim to a file；Code A updates internal _qdDate and info._qdValue; Code B writes to a temporary VRML file and updates a JLabel；Code B includes HTTP Basic Authentication; Code A does not；Code A has a condition to use local file if _local true; Code B always uses a URL
- 修正建议: Add negative samples that have similar structural boilerplate but different core logic；Incorporate dataflow or type-specific information to distinguish shared library usage from actual semantic similarity；Use contrastive learning that focuses on the actual operations inside loops

### case_id=399 FP dataflow_blindspot

- 方法: `readData` vs `copy`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_with_trace`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Reads global string variables and a file to populate various sets and maps for Tibetan transliteration processing.
- B 摘要: Copies a file from source to destination using NIO FileChannel and MappedByteBuffer.
- 静态失败原因: Static BERT methods may have been misled by both functions containing file reading operations and try-catch blocks, and the extreme length of readData may have caused the model to miss its core logic, leading to a false positive.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 dataflow_trace_and_outputs。
- BCB 偏好解释: BCB typically labels non-clones when functions perform entirely different tasks, even if they share some low-level I/O operations. The label 0 is consistent with strong behavioral difference.
- 共享行为: Both involve reading data from external sources (strings/file in A, file in B)
- 行为差异: readData parses tokenized strings and a structured file to build data structures; copy transfers bytes from one file to another.；readData has complex logic with multiple sets and maps; copy is a simple one-to-one byte copy.；readData modifies global state; copy does not (it just writes to dest).
- 修正建议: Improve model's ability to capture long-range dependencies and distinguish different data flow patterns.；Use larger context windows or hierarchical encoding for long functions.；Incorporate more robust tokenization that can differentiate between initialization and file copy patterns.

### case_id=400 FN partial_functionality

- 方法: `getFile` vs `write`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Downloads a WSDL file from a URL, optionally modifies the endpoint, and saves to a temporary directory.
- B 摘要: Creates a JAR output stream by copying entries from multiple input JAR files, excluding manifest and empty entries.
- 静态失败原因: The static model likely relied on lexical and syntactic similarity, which is very low. It may not capture the high-level task similarity that BCB annotators might assume. The model correctly identified them as different under strict semantics, but BCB's broader criteria may consider them as clones.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to a broad interpretation of file-based I/O operations, possibly considering both as 'file writing' tasks in a deployment pipeline, despite different domains.
- 共享行为: Both use I/O streams to read from an input and write to an output；Both handle exceptions (IOException and others)；Both perform file operations (create, delete, rename in A; entry creation in B)
- 行为差异: A downloads a single file from network; B aggregates entries from multiple local JAR files；A modifies XML content; B does not modify content, only copies；A returns a file path; B writes to an output stream and has no return value；A uses URL, channels, and XML parsing; B uses JarOutputStream and ZipEntry enumeration
- 修正建议: Improve model to incorporate functional intent or domain context, e.g., by using task labels or documentation；Augment training data with examples of broad Type-4 clones that share only high-level goal but different code；Use program analysis to capture input/output relationships and transformations

### case_id=401 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFromTo`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a property value in a locale-specific properties file, copying a default English file if the locale file does not exist.
- B 摘要: Copies a file from source to destination using FileChannel.transferTo, with error handling and system exit on failure.
- 静态失败原因: The static BERT/GraphCodeBERT model likely recognized the low token overlap and the distinct overall purposes, correctly identifying them as non-clones under a strict semantic equivalence criterion.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled this as a clone due to the shared file copying sub-task, considering it as Type-4 (semantic) clone based on partial functional similarity, despite overall differences in purpose and implementation.
- 共享行为: Both read from a source file and write to a destination file.；Both handle file existence and I/O exceptions.；Both output status or error messages.
- 行为差异: Function A's primary purpose is to modify a property value; file copying is only a small preparatory step.；Function B's entire purpose is to copy a file; it has no property modification logic.；The file copy in A uses character-by-character I/O, while B uses NIO FileChannel.transferTo for efficiency.；Function A does not exit on exception; B calls System.exit(-1) on errors.
- 修正建议: Incorporate hierarchical clone detection that can identify shared subroutines.；Use a multi-label approach that separates whole-function equivalence from partial functional overlap.；Consider benchmark-specific preferences to refine annotation guidelines.

### case_id=402 FP lexical_or_api_overlap

- 方法: `sendRequest` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.98`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with compressed XML to a servlet and parses the XML response.
- B 摘要: Reads a service file via class loader to load and instantiate an OSGi FrameworkFactory.
- 静态失败原因: Static BERT models may over-rely on overlapping API keywords (URL, InputStreamReader, Exception) and generic I/O patterns, missing the high-level semantic distinction.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the two functions perform completely different tasks (HTTP request vs. service loading) with no shared intent or result.
- 共享行为: Both use Java I/O streams and URL handling.；Both catch exceptions.
- 行为差异: A writes data to a server output stream; B only reads from a resource file.；A uses HTTP connection and GZIP compression; B uses class loader and plain text reading.；A returns an empty string; B returns a FrameworkFactory object.；A handles connection errors with a dialog; B throws an exception if factory not found.
- 修正建议: Include data flow analysis to differentiate write vs. read operations.；Add contrastive training with diverse I/O examples.；Encode type-specific context (e.g., HttpURLConnection vs. ClassLoader).

### case_id=403 FP boilerplate_overlap

- 方法: `compressWithZip` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: A utility method that compresses a list of file paths into a ZIP archive
- B 摘要: An event handler that processes various action commands like setting file paths for Graphviz, ImageMagick, and other preferences
- 静态失败原因: The model likely overfit on surface-level patterns like null checks and file I/O API calls (e.g., File, FileInputStream) that appear in both, ignoring the completely different high-level semantics
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label non-clone because there is no functional similarity; one is about file compression and the other about GUI configuration handling
- 共享行为: Both check for null or empty inputs early and return；Both perform I/O operations on files
- 行为差异: A reads file contents and writes to a ZIP file; B reads file paths via JFileChooser and stores preferences；A uses streams (FileInputStream, ZipOutputStream); B uses Swing components and putsPref；A is a static method with no GUI; B is an instance method handling UI events；A has a single loop; B has many conditional branches and UI updates
- 修正建议: Include more diverse datasets with low lexical overlap but different semantics；Use contrastive learning to distinguish boilerplate patterns from true semantic clones；Add explicit data-flow or control-flow features to separate unrelated behaviors

### case_id=404 FP boilerplate_overlap

- 方法: `importSequences` vs `loadURL`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads sequences from a URL and parses FASTA-like data into name and sequence lists.
- B 摘要: Downloads a file from a URL with optional authentication and writes it to a temporary file while updating a status label.
- 静态失败原因: The static BERT/GraphCodeBERT model likely over-relied on lexical and API overlaps (URL, openStream, InputStreamReader, while loop) and control flow similarity, missing the semantic divergence in data transformation and overall goal.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels as non-clone when functions serve distinct high-level purposes, even if they share low-level I/O patterns. Here the functional intent is completely different.
- 共享行为: Both methods open a URL connection and read data from it using InputStreamReader.
- 行为差异: Method A parses a specific FASTA format; method B writes raw lines to a temp file.；Method A stores results in memory lists; method B creates a file and updates a UI label.；Method A includes authentication only in method B.；Method B writes output to a file and prints to console; method A does not.
- 修正建议: Incorporate data flow analysis to capture how input is transformed into output.；Use models that understand domain-specific semantics (e.g., biological vs. file download).；Add attention to function-level purpose via documentation or method names.

### case_id=405 FN boilerplate_overlap

- 方法: `login` vs `readURL`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into LOLA by sending email and password via POST request, extracts session ID from response, and returns it.
- B 摘要: Reads a URL and prints its content line by line to stdout.
- 静态失败原因: The static BERT/GraphCodeBERT model likely focused on token-level or simple dataflow differences and missed the high-level structural similarity of the URL reading pattern. The low Jaccard similarity and different method names contributed to the false negative.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label these as clones because both functions perform network I/O with similar boilerplate (URL, BufferedReader, try-catch), which is considered a common pattern. The low token similarity is offset by structural similarity in code clone benchmarks.
- 共享行为: Open a URL and read its content via BufferedReader；Handle IOException with try-catch block；Print output (either error or content)；Use URL and stream handling classes
- 行为差异: A sends POST data (email, pw) for authentication; B only opens a URL without sending data；A extracts and returns a session ID; B prints all lines and returns void；A uses URLConnection with doOutput and OutputStreamWriter; B uses URL.openStream()；A prints a login message and error message; B prints each line read
- 修正建议: Use a model that captures API usage patterns and control flow structures；Enhance training data with examples of skeleton-similar functions；Incorporate data-flow graph contrastive learning to recognize common I/O patterns

### case_id=406 FN benchmark_preference_bias

- 方法: `doGet` vs `convert`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles HTTP GET requests to retrieve and render a web page with permission checks, logging, and optional caching.
- B 摘要: Converts an ACRNEMA file to DICOM format by adding UIDs and handling pixel data with optional inflation.
- 静态失败原因: Static BERT model correctly identified low token overlap and semantic mismatch; it did not fail but was overridden by BCB annotation bias.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled these as clones due to superficial similarities like both having file I/O and logging, or due to annotation error.
- 共享行为: Both use try-catch-finally for error handling；Both perform I/O operations (file reading/writing or response writing)
- 行为差异: Different input types: HTTP request/response vs. File I/O；Different output: HTML page rendering vs. DICOM file conversion；Different domains: web portal vs. medical image processing
- 修正建议: Re-evaluate BCB annotations for cross-domain pairs；Use domain-specific features to disambiguate true semantic clones

### case_id=407 FP lexical_or_api_overlap

- 方法: `addDataFromURL` vs `getFrameworkFactory`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads from a given URL and appends each line to a StringBuilder, with fallback appending the URL string on exception.
- B 摘要: Reads a specific service file from the classpath to find a class name and instantiate a FrameworkFactory via reflection, throwing an exception if not found.
- 静态失败原因: The static model likely overemphasized the lexical overlap of API calls (URL.openStream, BufferedReader, readLine) and the try-catch structure, ignoring the different semantic goals and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would consider these non-clones because the overall functionality differs significantly: one is a data accumulation utility, the other is a service loader. Despite similar I/O patterns, the intent and output are distinct.
- 共享行为: Both open a URL stream and read lines using BufferedReader
- 行为差异: Function A appends all lines to a StringBuilder; Function B parses lines for a non-comment class name and reflectively instantiates an object；Function A catches exceptions and prints a stack trace; Function B throws exceptions if the factory cannot be found；Function A's URL is a parameter; Function B's URL is fixed to a resource file；Function A has no return value; Function B returns a FrameworkFactory instance
- 修正建议: Incorporate data-flow analysis to track how the read data is used；Consider return types and whether the method modifies internal state vs. returns a new object；Add contrastive training examples with similar API usage but different semantics

### case_id=408 FP boilerplate_overlap

- 方法: `readRemoteFile` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a remote file via URL, concatenates all lines into a single string, and returns it.
- B 摘要: Queries a REST API for open tickets in a queue, extracts ticket IDs from the response, fetches each ticket, and returns a list of tickets.
- 静态失败原因: Static BERT/GraphCodeBERT models often rely on lexical and syntactic surface forms. Both functions contain overlapping keywords (BufferedReader, readLine, URL, InputStream, IOException, etc.) and similar structural fragments (while loop, try-catch), causing high embedding similarity even though the semantics differ completely.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones (Type-4 not semantically similar) despite both using network I/O and line reading, because the overall functionality and purpose are entirely different. BCB requires substantial functional overlap, not just shared low-level I/O patterns.
- 共享行为: Both perform network I/O (HTTP requests).；Both use BufferedReader to read lines from an InputStream.；Both have typical exception handling for I/O errors.
- 行为差异: Function A reads a file and returns its entire content as a single string; Function B parses a structured response to extract ticket IDs and then fetches individual tickets.；Function A uses java.net.URL directly; Function B uses Apache HttpClient for REST API calls.；Function B includes validation of HTTP status codes, multiple request loops, and complex logic for parsing and error handling; Function A is a straightforward read until EOF.；Function B returns a list of domain objects (RTTicket); Function A returns a plain String.
- 修正建议: Enhance training with more diverse negative examples that share I/O boilerplate but differ in semantics.；Incorporate data-flow analysis to distinguish variable manipulation and control flow beyond token similarity.；Use contrastive learning to penalize shallow lexical matches.

### case_id=409 FN partial_functionality

- 方法: `saveAttachmentBody` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Saves an attachment body from an email part to a file and updates the database with attachment size and content URI.
- B 摘要: Retrieves a resource from a URL, caches it locally if not already cached, and returns an InputStream to the local file.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on lexical tokens and code structure, oversimplifying the core functionality to stream copying while missing the distinct inputs, outputs, and side effects (e.g., database update vs. HTTP handling).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as Type-4 clones because they share a common I/O pattern of copying data from an input stream to a file, which is a frequent clone category in BigCloneBench despite different high-level purposes.
- 共享行为: Read from an input stream and write to a file；Check file existence and create directories if needed；Handle streams with proper close operations
- 行为差异: Function A updates a database with attachment metadata; function B does not；Function B implements caching logic and handles HTTP responses; function A does not；Function B returns an InputStream; function A returns void
- 修正建议: Incorporate method signature and return type into representation；Enhance data flow analysis to distinguish different I/O sources and sinks；Consider contextual information like class names and method names

### case_id=410 FN partial_functionality

- 方法: `read` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads camera log from URL, parses lines into CameraLogRecord, sorts records, with logging.
- B 摘要: Reads entire content from a fixed URL via URLConnection and logs the concatenated string.
- 静态失败原因: Static BERT/GraphCodeBERT models rely on token/structural similarity; low token Jaccard (0.222) and differences in exception handling, sorting, and variable types likely overshadowed the common I/O pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB considers them clones because they share the core I/O pattern (open URL, read lines, close) and have similar logging; differences in data processing are tolerated as Type-3/4.
- 共享行为: Both open a URL stream and read lines using BufferedReader；Both perform logging before and/or after reading；Both close the reader in a finally or at end
- 行为差异: A parses each line into CameraLogRecord and catches LogParseException; B concatenates lines into string；A sorts the records after reading; B does not；A uses url.openStream(); B uses URLConnection.getInputStream()；A has nested try-finally; B has simple try
- 修正建议: Augment training data with more Type-3/4 examples that share I/O patterns but differ in processing；Incorporate functional semantics via code summarization or documentation embeddings；Enhance graph representation to capture control flow and relevant dataflow around I/O operations

### case_id=411 FN benchmark_preference_bias

- 方法: `sendExceptionToServer` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Sends exception details to a remote server via HTTP POST with parameters.
- B 摘要: Checks for a new version by reading a file from a URL and parsing version strings.
- 静态失败原因: The low token Jaccard (0.2056) suggests limited lexical overlap; static models relying on token or structural features predicted non-clone, which aligns with actual functional difference, but BCB's lenient annotation caused a false negative.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: Annotators may have considered both as 'network I/O with line parsing' and labeled as Type-4 clone due to similar control flow structure despite different functionalities.
- 共享行为: Both open a URL connection and read lines from an input stream；Both handle IOException with try-catch blocks；Both use BufferedReader and InputStreamReader
- 行为差异: A performs HTTP POST with query string construction; B performs HTTP GET；A writes output to console; B interacts with a View and calls another method；A's parsing is conditional on multiple parameters; B's parsing targets specific version line prefixes；Different method names, parameters, and overall purpose
- 修正建议: Incorporate API call sequence analysis to distinguish POST vs GET；Use method name semantics to identify different intents；Enforce stricter semantic equivalence criteria in benchmark

### case_id=412 FN benchmark_preference_bias

- 方法: `doGet` vs `sendErrorMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to render a page based on a parameter, with visibility checks, logging, caching, and error responses.
- B 摘要: Sends an error message via email, including compressing a log file and attaching it.
- 静态失败原因: The static model correctly predicted non-clone (Jaccard 0.083). It did not fail; the BCB annotation is likely incorrect. The model's low token overlap and lack of semantic similarity led to correct non-clone prediction.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both functions containing error handling and logging, but overall purpose is different. Possibly a BCB annotation error or overly broad Type-4 interpretation.
- 共享行为: Both use try-catch for exception handling；Both perform logging；Both involve sending error responses (but different contexts)
- 行为差异: Function A is a web controller for page rendering, while B is a utility for email error reporting；A interacts with HTTP request/response objects, B uses file I/O and mail API；A has complex logic for page retrieval and caching, B has simple zip and mail logic
- 修正建议: Review BCB annotation for this pair; it may be a false positive in the benchmark.；If BCB prefers partial functionality, ensure that shared error handling is not overweighed.；Improve annotation guidelines to avoid such unrelated pairs.

### case_id=413 FN partial_functionality

- 方法: `getHTML` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML from a URL and optionally writes it to a file, returning the HTML content.
- B 摘要: Registers a User object by encoding password, setting registration date, adding authorities, creating forum user via URL call, persisting user, and sending confirmation email; returns success of email sending.
- 静态失败原因: GraphCodeBERT may have focused on the distinct method names ('getHTML' vs 'register') and the different surrounding code (password encoding, persistence), causing it to miss the shared URL reading pattern. The model might rely heavily on token-level semantic matching and may not generalize well to partial functionality similarity when there is significant unrelated code.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB might consider these clones because both functions share the core sub-pattern of opening a URL connection, reading lines into a StringBuilder. This common I/O operation might be deemed as a Type-4 clone (functionally similar sub-task) by BCB annotators, especially if they focus on the network read functionality rather than the overall business logic.
- 共享行为: Both use URL and URLConnection to fetch data from a URL；Both read the URL response line by line using BufferedReader；Both use StringBuilder to build a string from the response；Both handle IOExceptions
- 行为差异: A is a simple HTML fetcher; B performs complex user registration logic including password encoding, database persistence, and email sending；A optionally writes to a file; B does not；B performs multiple URL parameters and handles different exception types (NumberFormatException) while A only catches Exception；A returns the HTML string; B returns a boolean indicating email success
- 修正建议: Combine data-flow analysis to identify shared subroutines across functions；Use hierarchical or compositional clone detection that can match sub-patterns；Train with contrastive learning that emphasizes structural similarity over lexical features

### case_id=414 FN benchmark_preference_bias

- 方法: `getFile` vs `displayDiffResults`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the 'location' attribute of 'wsdlsoap:address' XML elements, and saves the modified file to a temporary directory, returning the file path.
- B 摘要: Generates an HTML report displaying line-of-code differences (added, modified, deleted) and launches the report in a web browser.
- 静态失败原因: Static BERT/GraphCodeBERT models may have incorrectly predicted non-clone because they rely on token similarity and structural patterns; the token overlap is very low (7.8%), and the functions have distinct control flows and API calls. The model likely correctly detected they are not clones, but BCB label requires clone detection.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: None
- 共享行为: Both write to output streams；Both create temporary files；Both use file I/O operations
- 行为差异: Function A downloads from URL and modifies XML; Function B generates HTML report from static data；Function A returns file path; Function B launches browser；Function A has extensive error handling and logging; Function B throws IOException with no logging；Function A uses XML parsing; Function B uses string concatenation for HTML
- 修正建议: Improve dataset annotation consistency；Incorporate domain-specific knowledge in model training；Use data-flow representations to capture input-output relationships

### case_id=415 FN boilerplate_overlap

- 方法: `login` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.2`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs in to LOLA by sending POST request with email and password, reads response to extract session ID, and sets session.
- B 摘要: Fetches content from a URL via GET request, reads entire response, and logs it.
- 静态失败原因: The static BERT model likely focused on token-level similarity and method names, which are low (Jaccard=0.183), and failed to recognize the high-level API usage pattern (URLConnection + BufferedReader) that BCB considers as clone.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may label this as a clone due to shared boilerplate pattern of URL connection opening and reading, which is considered a partial functionality or Type-4 semantic clone in the benchmark, despite different specific tasks (login vs fetch).
- 共享行为: Both use java.net.URLConnection and BufferedReader to read input stream；Both open a URL connection to an HTTP endpoint；Both read text response line by line
- 行为差异: Function A performs POST with output stream, function B performs GET only；Function A extracts and returns session ID, function B logs entire response and returns void；Function A handles exceptions locally, function B declares exception；Function A uses URL encoding for parameters, function B does not
- 修正建议: Incorporate structural information about API call sequences into the model；Use graph-based representations that capture control flow and data flow of network I/O；Add training examples that distinguish between different I/O tasks but share boilerplate

### case_id=416 FP lexical_or_api_overlap

- 方法: `wordFrequency` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches a URL, reads lines, and returns the integer frequency found by matching a regex pattern.
- B 摘要: Fetches a YouTube URL, reads lines, extracts video parameters from a line containing 'fullscreenUrl', and returns a constructed download URL.
- 静态失败原因: Static BERT likely over-fitted on shared lexical tokens (URL, BufferedReader, readLine, try-catch) and loop structure, ignoring the domain-specific semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this non-clone because the high-level functionality differs entirely (word frequency vs. URL construction), despite similar I/O patterns.
- 共享行为: Both open a URL connection and read lines using BufferedReader.；Both loop through lines and perform pattern matching or string checking.；Both use try-catch for exception handling.
- 行为差异: Function A returns an integer (word frequency); Function B returns a String (full screen URL).；Function A uses regex to match lines; Function B uses contains and string splitting.；Function A's output is derived from a matched line directly; Function B parses and constructs a new URL from multiple line segments.；Function B has additional UI updates (progress bar) and prints debug info.
- 修正建议: Train with contrastive examples emphasizing method semantic intent over surface syntax.；Incorporate return type and method name embeddings.；Use data flow or program dependence graphs to capture output semantics.

### case_id=417 FN benchmark_preference_bias

- 方法: `getEncoding` vs `sendRequestObjectResponse`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Extracts character encoding from HTTP response headers or body.
- B 摘要: Sends an XML request to a servlet via HTTP, compresses it, saves the response to a file based on content type, and returns the file path.
- 静态失败原因: Static BERT correctly predicted non-clone; the low token Jaccard and structural differences align with the lack of semantic equivalence.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to the common activity of URL connection and content-type detection, but the core functions are entirely different.
- 共享行为: Both open HTTP connections and read from them；Both check the content-type header
- 行为差异: A only reads headers/body to find charset; B writes a compressed request and saves response to disk；B involves UI dialogs, preferences, and error handling unrelated to encoding；A returns encoding string; B returns file path
- 修正建议: Focus on detecting functional purpose beyond shallow API usage；Incorporate control-flow and data-flow analysis to distinguish different tasks

### case_id=418 FP lexical_or_api_overlap

- 方法: `get` vs `addQDInformation`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches game records from a remote URL via HTTP GET, parsing lines that are not comments.
- B 摘要: Updates internal QD information by reading a local file or remote URL and parsing configuration data.
- 静态失败原因: Static BERT/GraphCodeBERT may have over-relied on lexical overlaps such as 'BufferedReader', 'readLine', 'URL', 'InputStream', and common exception handling pattern, missing the entirely different semantics and data flow.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels this as not a clone because the functions have different purposes, outputs, and complex logic; only superficial I/O similarities.
- 共享行为: Both read data from an external source (URL or file) line by line using BufferedReader；Both ignore lines starting with a specific prefix (though different prefixes)；Both use try-catch for IOException
- 行为差异: FunctionA returns an array of GameRecord objects; FunctionB modifies internal state；FunctionA sets custom HTTP headers and checks response code; FunctionB may read from local file or URL based on a flag；FunctionA uses GameRecord.decode for parsing; FunctionB parses 'pg ' and 'pt ' prefixes for date and project values；Different method signatures: public static vs private void
- 修正建议: Improve model to differentiate between similar I/O boilerplate and distinct business logic；Incorporate data flow analysis to capture how input is transformed；Use contrastive learning with hard negative examples of similar utilities but different functionalities

### case_id=419 FP boilerplate_overlap

- 方法: `readData` vs `sendErrorMessage`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses configuration strings into sets and builds a lookup table from a file, handling Tibetan and Sanskrit characters.
- B 摘要: Creates a zip archive of a log file and sends it as an error message to recipients via email.
- 静态失败原因: The model likely fixated on common Java idioms (exception handling, loops, use of StringTokenizer/HashSet, error throwing) while ignoring the distinct domain-specific semantics and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they perform entirely different tasks with no shared intent, despite some superficial structural similarities.
- 共享行为: Both use try-catch blocks for exception handling.；Both perform iteration over collections or streams.；Both involve string manipulation and file I/O operations.
- 行为差异: Function A is a data-loading routine; Function B is an error-reporting method.；Function A populates multiple HashSets and maps; Function B sends an email with a zipped log.；Function A has complex conditional logic for parsing columns; Function B has simple file compression and mailing logic.
- 修正建议: Train on more diverse examples emphasizing functional semantics over syntactic patterns.；Use code representations that capture method-level intent, such as dataflow or program dependence graphs.；Incorporate documentation or comments as additional signals.

### case_id=420 FN benchmark_preference_bias

- 方法: `parse` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Parses an input stream, optionally extracting a file to disk based on metadata, or delegates to a downstream parser.
- B 摘要: Modifies a locale-specific properties file by updating or adding a key-value pair, copying from an English file if necessary.
- 静态失败原因: Static BERT/GraphCodeBERT likely focused on low lexical overlap (Jaccard 0.108), different method names, parameters, and control flow, missing the abstract file-IO commonality. The model may not generalize well to such coarse-grained similarity.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered them clones due to broad Type-3 similarity: both involve file I/O operations (reading streams, writing files) and conditional logic, but the functional equivalence is minimal. The labeling might be a benchmark preference bias toward partial functionality overlap.
- 共享行为: Both methods read from an input source and write to a file；Both involve conditional checks based on existence or conditions
- 行为差异: Method A extracts a single file from a stream during parsing; Method B modifies a properties file based on string manipulation；Method A uses an InputStream and delegates to a parser; Method B uses file I/O and property file editing；The overall purpose and context are completely different
- 修正建议: Improve model sensitivity to high-level functional similarity beyond lexical tokens；Incorporate data-flow or API-call overlap in embeddings；Use domain-specific fine-tuning for file I/O patterns

### case_id=421 FN benchmark_preference_bias

- 方法: `copyFile` vs `doGet`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies a file using FileChannel transferTo with proper resource cleanup.
- B 摘要: Handles HTTP GET requests for a portal page, including parameter parsing, authentication, logging, page rendering, and caching.
- 静态失败原因: The static BERT model correctly predicted non-clone based on low token similarity and clear semantic differences, but the BCB annotation considered weak structural patterns (file I/O, try-catch) as sufficient, causing a mismatch.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled as clone due to both functions involving file writing operations (code_b writes to a cache file) and similar exception-handling patterns, reflecting a broad Type-4 notion where partial functionality overlap is accepted.
- 共享行为: Both involve file I/O operations；Both use try-catch-finally for resource management
- 行为差异: code_a is a simple file copy; code_b is a complex servlet handler；code_a operates on File objects; code_b operates on request/response objects；code_b includes business logic, database queries, and access control; code_a does not
- 修正建议: Improve training data quality by filtering out noisy BCB labels；Incorporate better semantic similarity measures that require functional equivalence

### case_id=422 FP boilerplate_overlap

- 方法: `get` vs `importRoles`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches game records from a URL using HTTP GET with custom headers, parsing lines that do not start with '#'.
- B 摘要: Fetches XML role names from a URL by reading lines and parsing when encountering a closing tag.
- 静态失败原因: The static model likely overemphasized the common boilerplate of URL connection, BufferedReader, and while loop, leading to a false positive. It may have missed the differences in method signatures, specific API calls, and data processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels this as non-clone because the functions have different input parameters, different parsing logic, different return types, and serve distinct purposes (game records vs. role imports). The token Jaccard is low, and BCB typically requires more than just similar boilerplate structure.
- 共享行为: Both make HTTP GET requests to a URL.；Both read lines from an input stream using BufferedReader.；Both parse lines in a loop to build data objects.
- 行为差异: A accepts extra parameters (lat, lon, count) and sets custom headers; B only takes a URL string.；A parses lines that do not start with '#' into GameRecord objects; B parses XML fragments into RoleName objects.；A returns an array of GameRecord or null on failure; B returns an ArrayList<RoleName> (empty on failure).；A catches only IOException and prints stack trace; B catches multiple exceptions (MalformedURLException, IOException, ParsingException) silently.
- 修正建议: Incorporate method signature information (parameters, return type) more strongly.；Add attention to specific API calls and data parsing details.；Use dataflow analysis to capture the transformation from input to output.；Train on more diverse examples to reduce bias towards common boilerplate patterns.

### case_id=423 FN benchmark_preference_bias

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using NIO FileChannel.
- B 摘要: Launches a NexOpen project launch configuration, handling Maven POM files and Hibernate settings, then schedules an install action.
- 静态失败原因: The static model correctly predicted non-clone (0) because the token Jaccard is very low (0.06) and the semantics are entirely different. It did not fail; rather, the BCB label is likely incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'file operations' due to the use of FileInputStream/FileOutputStream in A and file handling in B, but this is extremely broad and unlikely to be intended. The pair appears to be an annotation error.
- 共享行为: Both involve file I/O operations
- 行为差异: copyFile is purely a file copy utility; launch is a complex Eclipse launch configuration method；copyFile uses FileChannel; launch uses SAX parsers, properties, and project actions；copyFile returns a boolean; launch returns void and throws CoreException；copyFile has no Eclipse dependencies; launch is tightly coupled to Eclipse and Hibernate frameworks
- 修正建议: Re-annotate the BCB pair as non-clone；Investigate if there was a misinterpretation in BCB annotation guidelines for this specific case

### case_id=424 FN lexical_or_api_overlap

- 方法: `decodeBody` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Decodes a message body using content transfer encoding and writes it to a temporary file, returning a Body object.
- B 摘要: Retrieves a resource by name from a URL, caches it locally, and returns a FileInputStream to the cached or remote content.
- 静态失败原因: Static BERT relied on lexical overlap and API similarity, which is very low (Jaccard 0.10). The functions share no common method names or significant token sequences, leading to a non-clone prediction.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have considered both as utility methods that copy data from an input stream to a file, despite vastly different contexts and purposes, reflecting a broad Type-4 similarity or potential annotation bias.
- 共享行为: Both involve reading from an InputStream and writing to an OutputStream (file or temp file).；Both handle stream copying and resource cleanup.
- 行为差异: Different input: A takes an InputStream and encoding string; B takes a resource name and uses caching.；Different processing: A applies decoding (quoted-printable/base64); B handles HTTP connections and file caching.；Different return types: A returns BinaryTempFileBody; B returns InputStream.；Error handling: A does not have extensive exception handling; B has a large try-catch block.
- 修正建议: Increase model sensitivity to control-flow and data-flow structure.；Use graph-based representations to capture deeper semantic similarity beyond token overlap.；Include broader context about method purpose (e.g., method names, comments).

### case_id=425 FN partial_functionality

- 方法: `login` vs `CheckUrl`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Logs into LOLA by sending email and password via HTTP POST, extracts session ID from response, and sets it.
- B 摘要: Fetches the first line of content from a given URL via HTTP GET and returns it as a string.
- 静态失败原因: Static BERT models rely on token-level similarity (Jaccard = 0.27) and may be misled by different method names, logic (POST vs GET), and return processing, missing the underlying structural similarity of HTTP boilerplate.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs with significant boilerplate overlap and partial functionality similarity as clones (Type-3/4). Both functions perform common HTTP I/O tasks (open connection, read line) despite different specific purposes.
- 共享行为: Open HTTP connection to a URL；Read first line from response using BufferedReader；Return a string from the response；Handle exceptions with try-catch
- 行为差异: A uses POST with form data, B uses GET；A has a specific target URL, B takes URL as parameter；A parses session ID from response, B returns raw line；A has side effect (set_session), B is pure
- 修正建议: Use AST or data-flow features to capture structural similarity beyond token overlap；Train with contrastive learning on BCB-style labels to emphasize partial functional similarity；Incorporate method name and API usage patterns

### case_id=426 FP boilerplate_overlap

- 方法: `sendPost` vs `load`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request to a given URL with provided parameters and returns the response body as a string, handling exceptions by showing a message and returning an empty string.
- B 摘要: Downloads the content of a Pastebin document by its ID via HTTP GET, returning the content as a string, with early validation of ID length and error handling via a dialog.
- 静态失败原因: The model likely over-emphasized the boilerplate code pattern (try-catch, BufferedReader, while loop, concatenation) shared by both functions, while ignoring the semantic differences in HTTP method, parameter handling, and error-specific details.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered them non-clones because they have different HTTP methods (POST vs GET), different input handling, and different purposes. Even under broad Type-4, the functionality differs significantly beyond a common HTTP request pattern.
- 共享行为: Both make an HTTP request and read the full response into a string using BufferedReader.
- 行为差异: A uses POST method with parameter body; B uses GET method without parameters.；A sets a request header; B does not.；A uses HttpURLConnection with explicit output; B uses URLConnection.openStream().；Error handling differs: A uses MsgPrint.showMsg, B uses JOptionPane.showMessageDialog.
- 修正建议: Train with more diverse examples that share structural patterns but differ in core semantics.；Incorporate dataflow analysis to distinguish POST vs GET logic.；Add negative samples with similar boilerplate but different operations.

### case_id=427 FN partial_functionality

- 方法: `scrapeForIsbns` vs `invoke`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Scrapes ISBN numbers from a URL using regex, with retries on connection failure.
- B 摘要: Invokes a remote method via HTTP POST, deserializes JSON response, with retries on timeout.
- 静态失败原因: The low token Jaccard similarity (0.128) and different API calls (regex vs. HTTP library) made a static embedder like BERT fail to capture the underlying structural loop-and-stream pattern. The model likely focuses on surface lexical and API tokens, missing the common control flow and intent.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these Type-4 clones because they share a common structural pattern of retrying network operations with exception handling and streaming input, even though the specific payload processing differs. The broad functional similarity (accessing HTTP resource with retry) aligns with BCB's acceptance of partial functionality clones.
- 共享行为: Both open an HTTP connection and read the response line by line using BufferedReader and InputStreamReader.；Both implement a retry mechanism for network-related exceptions (ConnectException in A, ConnectTimeoutException in B).；Both handle exceptions and log messages.；Both return a value after processing the response stream.
- 行为差异: A matches lines against a regex to find ISBNs; B reads entire response and deserializes JSON.；A uses a fixed number of retries (RETRIES constant) with a sleep of 5 seconds; B uses a retryTimes parameter decremented and recursive call without sleep.；A returns an integer count; B returns an Object (parsed from JSON or null).；A uses java.net.URL and Pattern; B uses Apache HttpClient and custom JsonUtils.
- 修正建议: Train on code with explicit program structure (e.g., data flow, control flow graphs) to capture retry pattern.；Use contrastive learning with pairs that share structural similarity despite different APIs.；Incorporate AST or CFG features to recognize common loop/exception-handling structures.

### case_id=428 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Modifies a locale-specific properties file by adding or updating a key-value pair, with fallback copy of the English properties file if the locale file does not exist.
- B 摘要: Copies a file from source to destination using NIO FileChannel transfer.
- 静态失败原因: Static BERT-based models rely on token and structural overlap; low Jaccard similarity (0.05) and different method names led to non-clone prediction. The partial file-copy overlap is a small portion of A and not captured as a shared pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB annotator may have focused on the shared file-copy sub-task as a common operation, or applied a very broad interpretation of functional similarity (Type-4) despite low structural overlap.
- 共享行为: Both perform file I/O operations involving reading and writing files.；Both involve copying file content (A copies only if locale file missing, B always copies).
- 行为差异: A operates on properties files with locale handling, line parsing, and conditional file creation; B is a generic file copy without modification.；A has complex logic and error handling; B is a simple utility function.；A modifies file content by adding/updating a key-value pair; B duplicates file content exactly.
- 修正建议: Incorporate data-flow analysis to detect shared subroutines like file copy.；Add a module to recognize partial functionality overlap where one function delegates to a common utility pattern.；Use contrastive learning to emphasize task-level semantics over local token matching.

### case_id=429 FP lexical_or_api_overlap

- 方法: `getFrameworkFactory` vs `googleImageSearch`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Loads an OSGi framework factory from a service file.
- B 摘要: Searches Google Images, parses HTML, and updates a GUI component.
- 静态失败原因: The static BERT/GraphCodeBERT model likely over-relied on the overlapping lexical tokens (e.g., 'URL', 'BufferedReader', 'for', 'try', 'catch') and the similar control flow pattern of reading lines from a URL, ignoring the substantial semantic differences in the data processing and overall purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because they have entirely different functionality despite superficial structural similarities like reading from a URL.
- 共享行为: Both open a URL and read lines using BufferedReader.；Both have a try-catch structure.；Both use loops to process text.
- 行为差异: Function A loads a class dynamically; function B parses HTML and extracts image URLs.；Function A throws exception if no factory found; function B shows error dialog and continues.；Function A is private and static; function B is public and void.；Function A returns an object; function B updates a GUI and has no return.
- 修正建议: Improve the model to better distinguish between different high-level tasks (e.g., service loading vs. web scraping) even when low-level I/O patterns are similar.；Enhance the model with task-specific embeddings or abstract syntax tree (AST) features to capture semantic intent.；Incorporate more context about the function's role (e.g., class name, surrounding methods) to disambiguate.

### case_id=430 FP lexical_or_api_overlap

- 方法: `init` vs `downloadModel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Initializes servlet by loading controller class names from registry files on classpath.
- B 摘要: Downloads an RDF model from a given URL and returns it.
- 静态失败原因: Static model overemphasized lexical overlaps (URL, InputStream, IOException, logging) and structural similarity (try-catch), missing semantic differences in data processing.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the core functionality differs significantly: class loading vs. RDF download, despite shared I/O patterns.
- 共享行为: Both open a network resource (URL) and read input；Both handle IOExceptions with logging；Both use try-catch blocks
- 行为差异: A loads multiple resources via classLoader.getResources, B uses single URL；A reads lines of text (class names), B reads RDF model；A adds classes to registry, B returns Model；A catches ClassNotFoundException, B catches MalformedURLException
- 修正建议: Incorporate data flow analysis to distinguish how read data is consumed；Use fine-grained AST matching to separate I/O boilerplate from core logic；Train on more diverse negative examples with overlapping API usage but different semantics

### case_id=431 FN partial_functionality

- 方法: `doRawRequest` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Function A performs an HTTP POST request with provided data and returns the response as a string.
- B 摘要: Function B performs an HTTP GET request to a fixed URL and logs the response.
- 静态失败原因: Static BERT models may focus on lexical differences like method names, hardcoded URL, and the presence of OutputStreamWriter in A, leading to a false negative. The token Jaccard similarity is moderate (~0.4), and the model may not capture the underlying shared dataflow of reading HTTP responses, treating the POST-specific code as a significant divergence.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labels this as a clone because both functions implement the same high-level pattern of performing an HTTP request and reading the response line-by-line, despite differences in HTTP method and output handling. The structural similarity (URL, URLConnection, BufferedReader, while loop) is high, and BCB often considers such partial functionality overlap as a Type-3/Type-4 clone.
- 共享行为: Both open a URL connection using URL.openConnection()；Both read the response line by line using BufferedReader and InputStreamReader；Both accumulate lines into a StringBuffer；Both close the BufferedReader
- 行为差异: A writes POST data via OutputStreamWriter; B does not write any data (GET request)；A sets conn.setDoOutput(true); B does not；A returns the accumulated string; B logs it via log.debug()；A uses a dynamic SERVICE_URL; B uses a hardcoded URL
- 修正建议: Use a model that incorporates control flow or data flow graphs to capture structural similarity；Include more training examples of HTTP-related clones with varying details (GET vs POST, log vs return)；Apply contrastive learning to emphasize semantic similarity despite surface differences；Consider using AST-based features to align similar patterns of URL connection and response reading

### case_id=432 FP lexical_or_api_overlap

- 方法: `getLinksFromURLFast` vs `read`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches HTML page from a URL and extracts hyperlinks and anchor texts using regex, returning them as two Vectors.
- B 摘要: Reads camera log from a URL, parses each line into CameraLogRecord objects, sorts them, and logs the process.
- 静态失败原因: Static BERT models may over-focus on common I/O tokens (BufferedReader, InputStreamReader, readLine) and the while-loop structure, ignoring the divergent core logic.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clone because the functions have completely different purposes and outputs, despite sharing I/O boilerplate.
- 共享行为: Both read from a URL via BufferedReader；Both use a while loop to read lines
- 行为差异: A extracts HTML links; B parses log records；A returns Vectors; B populates a list and sorts；A uses regex for parsing; B uses CameraLogRecord constructor；A has debugging prints and timeCheck; B has logging
- 修正建议: Enhance training with hard negative pairs that share I/O patterns but differ in logic；Incorporate structure-aware features (e.g., data flow, call graphs) into the model；Leverage method names and surrounding context to disambiguate

### case_id=433 FP lexical_or_api_overlap

- 方法: `getWebPage` vs `importSequences`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads entire content from a URL and returns it as a string; throws Error on failure.
- B 摘要: Imports FASTA sequences from a URL selected via combo box, populates names and sequences lists.
- 静态失败原因: The model might have been misled by the common pattern of opening a URL stream and reading lines, despite low token Jaccard. Lexical overlap like 'InputStream', 'openStream', 'IOException' and similar try-catch structure could cause false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely annotated based on functional purpose: one is a generic web page retriever, the other is a sequence importer with specific parsing logic.
- 共享行为: Both open a URL stream and read text data.
- 行为差异: A reads all lines and concatenates; B parses FASTA format.；A returns a string; B modifies instance fields.；A throws Error on IOException; B catches exceptions and prints stack trace.；A uses standard readers; B uses custom ImportHelper.
- 修正建议: Incorporate structure-aware features like AST or CFG.；Use domain-specific token embeddings.；Employ graph-based representations to distinguish control flow and data flow.

### case_id=434 FP lexical_or_api_overlap

- 方法: `main` vs `testLoadSource`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that generates adapter JAR from a Prolog file using command line arguments.
- B 摘要: Test method that loads an article source and asserts its content contains a specific string.
- 静态失败原因: Overlapping API calls (e.g., IOUtils.copy, StringWriter, InputStream) and boilerplate patterns led to false similarity detection.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotates as non-clone because the functions perform completely different tasks with no semantic overlap.
- 共享行为: No meaningful shared behavior beyond standard Java I/O and utility usage
- 行为差异: Different input: command line vs. metadata object；Different output: JAR file vs. string content；Different purpose: code generation vs. testing
- 修正建议: Incorporate method-level context (e.g., main vs. test), type signatures, and task domain to disambiguate.；Use code summaries or documentation to capture functional intent.；Downweight common library calls that are frequent across unrelated methods.

### case_id=435 FN benchmark_preference_bias

- 方法: `doGet` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request for a portal page, performing access control, caching, and logging.
- B 摘要: Downloads a KMZ file from a fixed URL and extracts its contents to local storage.
- 静态失败原因: The model correctly identified low token overlap and semantic dissimilarity, thus predicting non-clone. The BCB label is likely incorrect, so the model did not fail.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled them as clones due to superficial similarities like both using stream I/O and having try-catch blocks, but the actual semantics are vastly different, likely a labeling error.
- 共享行为: Both have a method that processes some data and may write output
- 行为差异: A handles HTTP requests, B is a standalone main method；A involves complex portal logic, B is a simple file download and extraction；A uses servlet-specific objects, B uses URL and ZipInputStream；A does permission checking and caching, B does not
- 修正建议: Correct the benchmark label to non-clone；If BCB intended broad clones, refine annotation guidelines

### case_id=436 FP lexical_or_api_overlap

- 方法: `createFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Copies a file from a source to a resource managed by a resource manager, with error logging.
- B 摘要: Handles various action commands from a settings UI, updating preferences and UI components based on user selections.
- 静态失败原因: The model might have been misled by common keywords like 'File', 'filename', and 'return', or by the presence of try-catch blocks. However, token overlap is low, so the failure may stem from insufficient context understanding or a bias toward partial functionality matches.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not consider these clones because their functionalities are entirely different: one is a file copy utility, the other is a UI event handler. The only superficial similarity is the presence of file-related variables, but the core semantics differ.
- 共享行为: Both involve file name handling.
- 行为差异: Function A performs a single file copy operation; Function B processes multiple UI commands.；Function A is a utility method; Function B is an event handler with side effects on UI and preferences.；Function A has simple try-catch; Function B has complex conditional logic and multiple dialog interactions.
- 修正建议: Improve representation to capture high-level semantics and API usage.；Incorporate control flow and data dependency information.；Use contrastive learning to distinguish between similar-looking but semantically different functions.

### case_id=437 FP partial_functionality

- 方法: `init` vs `downloadFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Initializes controllers by reading class names from a registry file and loading them.
- B 摘要: Downloads a file from a URL to a local path with progress updates.
- 静态失败原因: The model likely focused on overlapping API elements (URL, openStream, BufferedReader, BufferedInputStream) and exception handling, ignoring the divergent high-level purposes and data flows.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB considers these non-clones because they perform completely different tasks (framework initialization vs file download) despite sharing low-level I/O patterns; the similarity in API usage does not imply functional similarity.
- 共享行为: Opens a URL stream and reads data；Uses InputStream and BufferedReader/BufferedInputStream；Handles IO exceptions
- 行为差异: Function A parses text lines and loads classes; Function B writes binary data to a file；Function A is void; Function B returns boolean；Function B writes to file and reports download progress
- 修正建议: Incorporate dataflow analysis to distinguish read-use patterns (parsing vs binary copy)；Add training examples where functions share APIs but differ in overall goal

### case_id=438 FN partial_functionality

- 方法: `invoke` vs `getNetworkServersIPs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Sends HTTP POST to a remote service, serializes arguments to JSON, deserializes response, and retries on timeout.
- B 摘要: Downloads a text file from a URL and extracts server IPs from lines following the '!SERVERS' marker.
- 静态失败原因: Static BERT models rely on token overlap and structural similarity; the low Jaccard similarity (0.151) and different method names, return types, and detailed logic led to a non-clone prediction, missing the common HTTP-data-fetching idiom.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often annotates clones based on shared high-level patterns, such as fetching data over HTTP and processing it line by line, even if the data format and specific operations differ.
- 共享行为: Both open an HTTP connection to a remote resource；Both read the response line by line using BufferedReader；Both parse the text content from the response；Both return a result derived from the response
- 行为差异: A uses HTTP POST; B uses HTTP GET；A serializes/deserializes JSON; B parses custom line format；A includes retry logic on timeout; B does not；A returns Object; B returns Vector<String>
- 修正建议: Enhance the model with data-flow analysis to detect HTTP I/O operations；Use graph-based representations that capture control and data dependencies related to external resource access；Incorporate API call patterns (e.g., URL.openConnection, HttpClient.execute) as features

### case_id=439 FN benchmark_preference_bias

- 方法: `doGet` vs `createNew`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request to retrieve a page, checks visibility, logs, and renders the page with caching.
- B 摘要: Creates a new file resource in a folder, checks permission, and handles special file names.
- 静态失败原因: Static BERT likely relied on low lexical overlap and different method names, missing the potential high-level semantic similarity that BCB annotators saw in the permission-check pattern.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as involving resource access with authorization checks, possibly categorizing them as Type-4 (semantic) clones due to similar high-level intent of handling user requests with permission control.
- 共享行为: Both perform permission checks before proceeding with the main operation.；Both log errors and handle exceptions.；Both involve conditional logic based on file or user properties.
- 行为差异: A retrieves and displays a web page; B creates a file and returns a Resource object.；A involves HTTP response handling and caching; B is file I/O focused.；A has extensive page rendering and statistics; B is simpler and returns null on failure.
- 修正建议: Increase emphasis on control-flow and high-level structure similarity in addition to token overlap.；Incorporate hand-crafted features for permission-check patterns or resource handling.；Use more robust semantic representation that captures abstract behavior beyond local tokens.

### case_id=440 FN partial_functionality

- 方法: `split` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.2`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Splits a FASTA file into multiple smaller files based on base and entry count limits using file channels and buffers.
- B 摘要: Builds a website for editing by applying XSLT transformations to XML pages and inserting control files, writing output files.
- 静态失败原因: The static BERT model failed due to low token overlap and lack of deep structural understanding; it likely relied on lexical and API-level matches, which are minimal here.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone due to both methods performing file I/O operations in a loop with conditional logic, representing a Type-3 clone with similar control flow but different domain logic.
- 共享行为: Both methods read from an input source and write to output files.；Both use loops to process data in chunks or pages.
- 行为差异: Function A splits binary sequence data; Function B transforms textual XML with XSLT.；Different input types: FASTA file vs. XML files and properties.；Output: multiple numbered FASTA files vs. web pages with specific naming.；Function B involves multiple external dependencies (XSLT, DOM, FTP).
- 修正建议: Incorporate control flow and data flow analysis to capture structural similarities.；Use graph-based models that compare abstract syntax trees or program dependency graphs.；Train on partial functionality clones with varied domains.

### case_id=441 FN lexical_or_api_overlap

- 方法: `copyTo` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Recursively copies a file or directory to a destination using file channels.
- B 摘要: Builds a website for editing by processing pages with XML transformations and writing output files.
- 静态失败原因: Low token Jaccard (0.06) and very different lexical content, method length, and API usage cause the model to predict non-clone.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might consider them clones due to both being file manipulation utilities, but this is a very broad and likely incorrect annotation.
- 共享行为: Both perform file input/output operations.
- 行为差异: copyTo is a simple recursive file copier; buildSiteForEdit is a complex multi-step site builder.；Different parameter sets and purposes.；Different algorithms: recursion vs. iteration and XML processing.
- 修正建议: Incorporate structural or dataflow information；Use code summarization to capture functional similarity；Address long-range dependencies with graph-based models

### case_id=442 FN partial_functionality

- 方法: `copyResource` vs `setPayload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using InputStream/OutputStream.
- B 摘要: Appends a file's content to another file using FileChannel, then recursively calls itself with a different argument.
- 静态失败原因: Static models rely on token overlap and surface features; low Jaccard similarity and different API usage (InputStream vs FileChannel) and control flow (loop vs recursion) obscured the shared file copy intent.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels functions with similar core functionality (e.g., file copying) as clones even if implementation details differ, treating them as Type-3 or Type-4 clones.
- 共享行为: Both copy data from an input source to an output file.
- 行为差异: A can read from URL; B reads only from a file.；A writes to a new file; B appends to an existing file.；A uses byte-by-byte copying; B uses FileChannel transferTo.；B has recursion and state (Index); A does not.
- 修正建议: Use dataflow or graph representations to capture read-write patterns.；Incorporate IO API knowledge.；Train on semantic similarity rather than surface forms.

### case_id=443 FN partial_functionality

- 方法: `modifyApplicationMessage` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.4`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Modifies a properties file for a specific locale, optionally copying the default English file if missing, then updates or adds a key-value pair.
- B 摘要: Copies a file from source to destination using FileChannel and NIO.
- 静态失败原因: The model likely relied on method names and high-level semantics, saw low token overlap, and missed the embedded file copy logic in A.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as Type-4 clones due to the shared file copy subroutine and similar exception handling patterns, despite different main purposes.
- 共享行为: Both perform file copy operations (optional in A).；Both use try-catch for exception handling.；Both close resources in a finally block.
- 行为差异: A's main purpose is properties editing; B's is pure file copy.；A uses character streams (FileReader/FileWriter) and string manipulation; B uses byte channels (FileChannel).；A has logic for parsing and modifying property lines; B does not.
- 修正建议: Enhance model to detect partial functional overlap or subroutines within larger functions.；Incorporate structural similarity of code blocks (e.g., try-catch-finally sequences).；Use methods like AST-based matching for finer granularity.

### case_id=444 FN benchmark_preference_bias

- 方法: `doGet` vs `persist`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Handles an HTTP GET request to retrieve and display a page, with visibility checks and optional caching.
- B 摘要: Persists a FreeFormConfigurable object's configuration to a file by copying an input stream to an output stream.
- 静态失败原因: Static BERT correctly predicted non-clone due to low lexical overlap and different structures; BCB's broad annotation preference caused the FN error.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: None
- 行为差异: Different domains: HTTP request handling vs. file persistence；Code A is long and complex; Code B is short and simple；Different APIs: HttpServletRequest/Response vs. FileOutputStream/InputStream；Different error handling: multiple catch blocks vs. throwing exception
- 修正建议: Use task-specific semantics in representation；Refine clone type definitions to exclude overly broad categories

### case_id=445 FN boilerplate_overlap

- 方法: `addIDs` vs `loadExistingAntlibs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves metabolite information from a web service by querying with a name, parses the response to extract various chemical IDs and scores, and updates a PeakListRow object.
- B 摘要: Loads Ant library definitions from classpath resources by reading a resource file listing package names, constructing URIs for antlib.xml files, and loading each ant library.
- 静态失败原因: Static models like GraphCodeBERT rely on token and structural similarity; the low token overlap (12.3%) and different API calls (e.g., 'PeakListRow' vs 'ClassLoader', 'URL' vs 'Enumeration') lead to a correct non-clone prediction, but fail to capture the higher-level structural similarity that BCB annotators may have considered.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB might consider both as 'resource loading and processing' functions that follow a similar pattern of opening streams, reading lines, and handling exceptions, thus classifying them as Type-4 (functionally similar) clones despite different domains.
- 共享行为: Both use BufferedReader to read lines from a stream；Both open and close streams (URL/URI resources)；Both handle exceptions (IOException, URISyntaxException)；Both iterate over lines in a loop
- 行为差异: Function A performs HTTP query to a web service and updates a data row with specific chemical properties；Function B loads Ant library definitions from classpath and registers them via loadAntLib；Function A returns an integer score; Function B returns void；Function A uses string parsing with specific patterns; Function B uses URI/URL resolution
- 修正建议: Incorporate more domain-specific semantic understanding to distinguish between truly similar functionalities vs. boilerplate patterns；Use functional decomposition or API usage similarity beyond simple token matching；Perhaps incorporate task/domain cues from method names and imports

### case_id=446 FN boilerplate_overlap

- 方法: `extractImage` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Extracts an image from an input file (supports stdin), applies scaling/transform, and writes to output file via a writer.
- B 摘要: Launches a NexOpen project configuration: checks project structure, processes pom.xml files, generates reverse engineering files, and triggers an install action.
- 静态失败原因: The static model likely correctly identified the functions as non-clones due to low token overlap and distinct structural patterns; the BCB label is likely an anomaly.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this as a clone due to superficial similarities in boilerplate code (e.g., file I/O, exception handling, use of streams) or a mistaken mix-up in annotation. The low Jaccard similarity suggests no strong lexical overlap.
- 行为差异: Function A processes image data (BufferedImage) while Function B handles project configuration and XML parsing.；Function A uses temporary files for input if stdin is provided; Function B does not use stdin but reads existing project files.；Function A writes output as a file; Function B modifies project properties and schedules a job.
- 修正建议: Re-evaluate BCB annotation for this pair; it appears to be a false positive.

### case_id=447 FN boilerplate_overlap

- 方法: `addIDs` vs `getEncoding`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.6`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Adds metabolite IDs and scores to a PeakListRow by scraping a web page based on a given name.
- B 摘要: Extracts character encoding from an HTTP response by inspecting headers and HTML content.
- 静态失败原因: Static BERT/GraphCodeBERT correctly identified them as non-clones based on low lexical overlap and distinct semantic roles. The misclassification as a false negative is due to BCB's potentially overbroad similarity criterion that BERT's training did not capture.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may have labeled this pair as a clone due to the shared boilerplate of using URL, BufferedReader, and reading lines, but the core functionality is entirely different. This label likely reflects a broad interpretation of Type-4 or partial similarity based on common I/O patterns.
- 共享行为: Both open URL connections and read from them using BufferedReader.；Both use try-catch or try-finally for exception handling.；Both return a value after processing the HTTP response.
- 行为差异: Function A parses HTML for specific patterns to extract metabolite IDs and scores, setting columns on a row.；Function B searches for 'charset' or 'encoding' in header fields or HTML lines to determine encoding.；Function A has complex conditional logic for multiple ID types and builds strings, while Function B has simpler conditional logic.；The return types and meanings are completely different (int score vs String encoding).
- 修正建议: Improve token alignment to weigh functional keywords (e.g., 'setVar', 'extractEncoding') more heavily.；Incorporate dataflow analysis to highlight different output variables and usage.；Train on finer-grained clone annotations that distinguish between shared I/O patterns and true functional similarity.

### case_id=448 FP boilerplate_overlap

- 方法: `scrapeForIsbns` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Scrapes ISBN-10 codes from a URL by reading lines and applying regex, with retry logic.
- B 摘要: Checks for software upgrades by querying a license server, parsing XML-like response, and manipulating UI and database.
- 静态失败原因: Static BERT models likely overemphasized common boilerplate tokens such as 'URL', 'BufferedReader', 'InputStreamReader', and the while loop pattern for reading lines, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label these as non-clones because they have entirely different domain logic and no functional similarity beyond generic I/O patterns.
- 共享行为: Both use URL connection and BufferedReader to read data from a network source.
- 行为差异: A extracts ISBNs using regex; B processes upgrade records using string splitting.；A counts matches and stores them; B performs database operations and UI updates.；A handles ConnectException with retry; B handles license errors with UI messages.；A returns an integer; B is void.
- 修正建议: Improve model to distinguish functional logic from boilerplate patterns.；Incorporate dataflow or call-graph analysis to capture actual semantics.；Use contrastive learning with hard negative examples that share I/O but differ in purpose.

### case_id=449 FN benchmark_preference_bias

- 方法: `extractImage` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Extracts an image from a JP2 file, applies scaling and transforms, and writes to an output file.
- B 摘要: Builds a website for editing by reading XML files, applying XSLT transformations, and writing processed HTML files.
- 静态失败原因: The model correctly identified low lexical overlap and distinct semantic domains, but BCB's annotation is overly broad; the model failed to recognize a clone under an extremely loose definition.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both as generic file processing utilities with input-output patterns, leading to a broad Type-4 clone label despite semantic dissimilarity.
- 共享行为: Both read input data and write output data using file streams；Both handle I/O exceptions and clean up resources
- 行为差异: A processes binary image data; B processes XML/HTML text；A uses image processing library; B uses XSLT transformers and string buffers；A has a single output file; B iterates over multiple pages and writes many output files
- 修正建议: Review BCB annotation for potential mislabeling；Train model to be robust against overly broad clone definitions by incorporating domain-specific features

### case_id=450 FP lexical_or_api_overlap

- 方法: `actionPerformed` vs `copyResourceToFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Handles UI action events for configuring application settings like graphviz path, image magick path, and look-and-feel.
- B 摘要: Copies a resource file to a destination file, managing input/output streams.
- 静态失败原因: The model likely over-relied on overlapping lexical tokens like 'File', 'IOException', and general control flow patterns (if statements, try-catch) which are common boilerplate, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would not label these as clones because they perform completely different tasks with no functional overlap.
- 共享行为: Both are Java methods that handle file-related operations, but the specifics are entirely different.
- 行为差异: Code A is a complex event handler with numerous UI preference updates, while Code B is a simple file copy utility.；Code A uses file chooser dialogs and preference storage; Code B performs actual file I/O.；Code A has extensive conditional logic for different commands; Code B is linear and straightforward.
- 修正建议: Incorporate AST-based or dataflow-based features to capture structural differences.；Add context from method names and surrounding class to disambiguate.；Train on longer code spans to better understand method-level semantics.

### case_id=451 FN partial_functionality

- 方法: `doVersionCheck` vs `fileDownload`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: A function that checks for a new version by reading a remote version file, extracting version and build strings, and comparing with current build.
- B 摘要: A function that downloads a file from a URL and saves it to a local directory as 'download.pdf'.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on token sequences and structure, and may overemphasize the shared URL/stream/loop pattern while missing the critical differences in data processing (line parsing vs byte copy) and overall purpose (version check vs file download). The low token Jaccard suggests lexical diversity, but structural similarity might mislead the model into false negative.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely annotates this as a clone because both functions share a common skeleton: URL creation, stream opening, reading loop with while, and stream closing. The core algorithmic pattern of fetching and processing remote data via URL is similar, fitting broad Type-3/Type-4 clones despite different specific operations.
- 共享行为: Both open a URL and read from its input stream.；Both use a loop to read data until end-of-stream.；Both close the input stream after reading.；Both handle IO exceptions.
- 行为差异: Function A reads lines and parses key-value pairs, while B reads raw bytes.；Function A interacts with UI (show/hide cursor, messages), B writes to a file.；Function A takes a View object and uses jEdit properties; B takes URL string and directory.；Function A performs a version comparison; B downloads regardless of content.
- 修正建议: Incorporate data flow analysis to track how read data is used (parsed vs copied).；Add type-aware encodings for API calls (readLine vs read byte) and output operations (UI message vs file write).；Use contrastive learning that distinguishes similar program skeletons with different semantics.

### case_id=452 FP lexical_or_api_overlap

- 方法: `readUNI` vs `doVersionCheck`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a URL with tab-separated lines, extracting ID and description into a vector.
- B 摘要: Reads a version check URL, parses lines for build numbers, and calls another method.
- 静态失败原因: Static BERT overemphasized the lexical and API overlap (URL, InputStream, line reading) while ignoring the distinct parsing logic and overall functionality.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clone because the functions serve different purposes and have different output behavior despite sharing a common URL reading pattern.
- 共享行为: Both open a URL and read lines；Both parse lines using conditional logic
- 行为差异: Different parsing logic (tab-separated vs line prefix)；Different output (adds to vector vs calls method)；Different error handling (catch and ignore vs show error dialog)
- 修正建议: Incorporate data flow or control flow analysis to capture semantic differences；Use contrastive training with negative examples that have high lexical but low semantic similarity

### case_id=453 FP boilerplate_overlap

- 方法: `PageLoader` vs `getFullScreenUrl`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads entire content of a web page into a string variable.
- B 摘要: Extracts a YouTube full screen video URL from a web page by parsing specific parameters.
- 静态失败原因: The static model likely overemphasized the common API sequence (URL, BufferedReader, InputStreamReader, readLine, close) and failed to recognize that the data extraction and parsing logic are fundamentally different.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically treats functions that share only generic boilerplate (like URL reading) as non-clones because the core functionality differs significantly. Here, one is a general page loader, the other is a specific YouTube URL extractor.
- 共享行为: Open a URL connection；Read from a BufferedReader wrapping an InputStreamReader；Close the reader
- 行为差异: Function A reads all lines and concatenates; Function B searches for a specific line containing 'fullscreenUrl'；Function B parses the line to extract video_id, t, title; Function A does no parsing；Function B sets progress bar indeterminate and prints debug output; Function A does not；Function A returns void; Function B returns a String
- 修正建议: Introduce data-flow or control-flow sensitivity to distinguish read-all vs search-and-parse；Increase weight on functional purpose (e.g., method name, high-level task) over low-level API usage

### case_id=454 FP boilerplate_overlap

- 方法: `readData` vs `decodeFileToFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Initializes sets and hash maps from tokenized strings and a file containing Tibetan character mappings.
- B 摘要: Decodes a Base64 encoded input file and writes the decoded content to an output file.
- 静态失败原因: Static BERT model likely over-relied on common structural patterns (file I/O, exception handling, stream closing) shared across many Java methods, mistaking them for semantic similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels non-clones because the functions have completely different purposes and low lexical overlap (Jaccard=0.065), indicating no shared functionality.
- 共享行为: Both use I/O streams (FileInputStream, BufferedOutputStream) and handle IOExceptions.；Both use try-catch-finally blocks with resource cleanup.
- 行为差异: A parses string tokens and populates data structures, B copies bytes after Base64 decoding.；A reads configuration data, B performs file format transformation.；A is private and void, B is public and returns boolean success indicator.
- 修正建议: Incorporate data flow analysis to distinguish between data initialization and data transformation.；Use method name and return type as strong discriminators.；Weight token overlap more heavily and reduce influence of generic I/O patterns.

### case_id=455 FP long_range_semantics

- 方法: `readData` vs `CopyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.99`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Parses multiple comma-separated strings to populate various sets and maps with tokens, and computes a maximum length.
- B 摘要: Copies a file from source path to destination path using FileChannel.
- 静态失败原因: The model likely focused on superficial token-level similarities (e.g., both use 'HashSet', 'StringTokenizer', 'IOException') and failed to capture the overall semantic intent due to the extreme length difference and complexity of readData.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotations typically require whole-function semantic equivalence; these functions have completely different purposes and implementations.
- 共享行为: Both involve data processing but at a high level only
- 行为差异: readData parses string tokens and populates collections; CopyFile performs file I/O without any string parsing；readData is long and complex with many iterations; CopyFile is short and straightforward；readData uses StringTokenizer and HashSet; CopyFile uses FileChannel and FileInputStream/FileOutputStream
- 修正建议: Improve handling of long-range dependencies in code representation；Incorporate structural matching or control-flow analysis to differentiate boilerplate from core logic；Train on more diverse negative examples with low token overlap

### case_id=456 FN library_context_missing

- 方法: `copyResource` vs `copyFile`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `context_recovery_then_expert`；动态可解性: `low`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file using byte-by-byte streaming.
- B 摘要: Copies a file to another file using NIO FileChannel transferTo.
- 静态失败原因: Low token overlap and syntactic differences (stream vs NIO, exception handling) prevented the model from recognizing the shared semantic goal of copying a file.
- 静态 case study: 该类错误缺少关键上下文或需要深层语义，纯静态方法不可靠。
- 动态 case study: 动态执行价值较低：样本可能依赖库、框架、网络、GUI、数据库或项目上下文，需要先恢复环境或 mock 依赖。
- BCB 偏好解释: BCB often marks Type-4 clones where two functions perform the same high-level operation (copying a file) despite different implementations and low code similarity, considering intent and output equivalence.
- 共享行为: Both copy data from a source to a destination file.
- 行为差异: A handles URL and file sources, B only files.；A uses InputStream/OutputStream, B uses NIO FileChannel.；A throws Exception, B throws IOException.；A closes resources manually, B uses try-finally.
- 修正建议: Train on diverse implementations of same functionality；Incorporate dataflow or API semantics；Use contrastive learning to align different APIs performing same task

### case_id=457 FP lexical_or_api_overlap

- 方法: `extractResourceToFile` vs `actionPerformed`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Extracts a resource file to a destination file by copying input stream to output stream with proper resource management.
- B 摘要: Handles action events to set various application preferences such as file paths for Graphviz and ImageMagick, and other settings.
- 静态失败原因: The static model likely overfitted to incidental lexical overlap (e.g., common keywords like 'File', 'null', 'if') or boilerplate patterns like null checks, leading to a false positive despite no semantic similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB would label this as non-clone because the functions have completely different purposes and no shared functionality, even under a relaxed definition of Type-3/Type-4 clones.
- 行为差异: Function A performs a generic IO copy operation, while Function B handles multiple UI actions for setting preferences.；Function A uses InputStream and FileOutputStream with try-finally for resource cleanup; Function B primarily uses JFileChooser and conditional logic.；Function A returns void; Function B returns void but has side effects on GUI components and preferences.
- 修正建议: Train with more discriminative loss functions that penalize false positives due to superficial overlap.；Incorporate dataflow or abstract syntax tree (AST) differences to better capture semantic intent.；Use contrastive learning to separate unrelated functions.

### case_id=458 FP boilerplate_overlap

- 方法: `readData` vs `copyFileChannel`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `1.0`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `low`
- A 摘要: Parses comma-separated tokens from strings into multiple sets and maps for Tibetan transliteration configuration.
- B 摘要: Copies a file from source to destination using Java NIO FileChannel, optionally preserving modification time.
- 静态失败原因: The static BERT model may have been misled by common structural elements like try-catch blocks and file I/O, failing to capture the distinct core semantics due to function A's length and complexity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely considered these non-clones because their functionalities are entirely different: one is data parsing/configuration loading, the other is file copying. There is no semantic equivalence or partial functionality overlap.
- 共享行为: Both involve file I/O operations；Both handle exceptions (IOException)
- 行为差异: readData parses and populates data structures from configuration strings; copyFileChannel transfers bytes between files；readData uses StringTokenizer and HashSet; copyFileChannel uses FileChannel and FileInputStream/FileOutputStream；readData has complex multi-step parsing; copyFileChannel is a straightforward file copy；readData interacts with multiple static variables; copyFileChannel uses local variables and parameters
- 修正建议: Improve model's ability to distinguish generic boilerplate from core functionality；Incorporate data flow analysis to differentiate data parsing from file copying；Use longer context or hierarchical attention to handle long functions

### case_id=459 FP boilerplate_overlap

- 方法: `main` vs `logging`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Parses a Prolog file and generates adapter classes into a JAR with debug options and error handling.
- B 摘要: Logs an inbound message by caching the input stream and writing it to a buffer, with size limits and error handling.
- 静态失败原因: The static model likely overemphasized common boilerplate patterns (exception handling, stream I/O) and ignored the distinct high-level purposes, leading to a false positive.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB labels these as non-clones because they implement completely different functionalities with no overlapping logic or output, despite some shared low-level I/O patterns.
- 共享行为: Both involve reading from input streams and handling IOException.
- 行为差异: Function A is a main program that generates adapter code and writes a JAR file; Function B logs a message for debugging.；A uses file parsing, class generation, and serialization; B uses interceptors, caching, and logging.；A has command-line argument parsing; B does not.
- 修正建议: Incorporate dataflow or control-flow analysis to distinguish core logic from generic boilerplate.；Use an approach that captures the high-level intent, such as semantic role labeling or API call sequences.

### case_id=460 FN partial_functionality

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from one location to another using FileChannel.
- B 摘要: Launches a NexOpen project configuration, involving XML processing, file operations including copying a resource file, and triggering an install job.
- 静态失败原因: Static BERT models like GraphCodeBERT rely on token-level and AST-level representations. The token Jaccard is very low (0.0377), indicating almost no lexical overlap. The model likely focused on method-level semantics and identified that the overall functionality is different (launch vs. copyFile). It failed to capture the shared file-copy sub-behavior because that sub-behavior is a small part of B and may not be prominent in the learned representation. The model may have been biased by the method names and the significant difference in context and dependencies.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as Type-4 clones because both methods involve the core functionality of copying a file. Despite the overall difference in complexity and purpose, the presence of a common file-copy sub-routine (using IOUtils.copy or transferTo) suggests partial functional similarity. BCB's annotation often accepts broad semantic overlap even if one method does much more.
- 共享行为: Both perform file copy operations: A copies a file directly; B copies a file from a bundle to a project.
- 行为差异: B is much more complex: it handles launch configuration, project validation, XML parsing, property setting, and job scheduling.；A is a simple utility method for file copy; B's file copy is a small part within many other operations.；B includes error handling that throws RuntimeExceptions, while A prints stack trace and continues.
- 修正建议: Augment training data with pairs that have low lexical overlap but share a sub-functional behavior.；Use contrastive learning to emphasize common sub-patterns.；Incorporate dataflow analysis to identify common I/O operations.

### case_id=461 FN partial_functionality

- 方法: `getHTML` vs `postData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Performs an HTTP GET request to retrieve HTML content from a URL, optionally writing it to a file, and returns the HTML string.
- B 摘要: Performs an HTTP POST request to send data to a URL, reads the response but discards it, and does not return anything.
- 静态失败原因: Low token Jaccard (0.193) and significant differences in method signatures, control flow, and data flow likely caused the static model to classify them as non-clones, overlooking the underlying HTTP communication pattern.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider this a clone due to shared high-level functionality of making an HTTP connection and reading the response, despite differences in HTTP method and file output.
- 共享行为: Both open a URL connection and set request properties；Both read from the HTTP response input stream；Both close the connection and streams after use
- 行为差异: HTTP method: GET vs POST；Return type: String vs void；File writing present in A but not in B；Error handling: A catches and prints exceptions, B throws them
- 修正建议: Incorporate data-flow analysis to capture the core HTTP request pattern；Use models that recognize API usage sequences (e.g., URLConnection, BufferedReader) as indicators of similar functionality；Consider functional similarity metrics that allow for method variations like GET vs POST

### case_id=462 FN partial_functionality

- 方法: `fileDownload` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a given URL to a local PDF file using character-by-character reading.
- B 摘要: Reads and discards all lines from a fixed URL without any output.
- 静态失败原因: The static model likely relied on API-level similarities (URL, BufferedReader, read loop) and structural patterns, failing to capture that the read data is used for different purposes (output vs. discarded).
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'URL reading' operations with similar control flow (try-catch, BufferedReader, while loop), and may overlook the output differences as inessential to the core task.
- 共享行为: Both open a URL connection and read data from the input stream using BufferedReader.；Both use a while loop to read until end of stream and close the reader.
- 行为差异: Function A writes the read data to a file; Function B discards it.；Function A reads character-by-character; Function B reads line-by-line.；Function A takes a parameterized URL and destination; Function B uses a hardcoded URL.
- 修正建议: Incorporate data flow analysis to track whether read data is used beyond reading.；Add training examples that contrast URL reading with and without output.；Use abstract syntax tree differencing to highlight differences in output handling.

### case_id=463 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for software version updates by fetching a version file from a URL and parsing it.
- B 摘要: Performs a complete upgrade check, including license validation, database operations, and UI updates.
- 静态失败原因: Static BERT/GraphCodeBERT might have focused on surface-level similarities like using URL, BufferedReader, while loop reading lines, and similar method names, missing deeper differences in control flow, data handling, and side effects.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators likely labeled as non-clone because the functions differ significantly in purpose and complexity; the shared fetch-parse pattern is too generic.
- 共享行为: Fetch a URL, read its content line by line using BufferedReader
- 行为差异: A only reads and parses version strings; B interacts with database, checks license, manipulates UI components, and installs upgrades；B has error handling for license failure; A has error handling for IOException；A calls another method after parsing; B does everything inline；B uses multiple SQL commands and data insertion; A does not modify state
- 修正建议: Improve model to recognize that simple URL fetching with line parsing is not enough to determine clone when the subsequent logic differs；Incorporate dataflow analysis to see that the parsed data is used in very different ways；Use control flow graph differences

### case_id=464 FN benchmark_preference_bias

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Copies a file from a source path to a destination path, creating parent directories and handling exceptions.
- B 摘要: Launches a NexOpen project configuration, validating project structure, processing POM files, setting properties, and scheduling an install job.
- 静态失败原因: Static BERT/GraphCodeBERT models rely heavily on token overlap and syntactic structure. With a token Jaccard of 0.05 and completely different method names, the model correctly predicted non-clone. The BCB label is questionable, so the model didn't actually fail; it identified the semantic divergence.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may label this as a clone due to partial functional similarity in file I/O (both create or copy files), despite the overall context difference. However, given the low token overlap and distinct method names, such broad Type-4 annotation seems unlikely.
- 共享行为: Both perform file I/O operations (reading from an input and writing to a file).；Both create directories if needed (copyFile explicitly; launch relies on project structure).；Both include exception handling with logging.
- 行为差异: copyFile is a simple file copy utility; launch is a complex multi-step configuration and build process.；copyFile uses low-level Java I/O streams; launch uses Eclipse/EMF APIs, content handlers, and job scheduling.；copyFile is a static method with no dependencies; launch is an instance method relying on launch configuration and project resources.；The file I/O in launch is a minor sub-task, not the main purpose.
- 修正建议: Re-evaluate BCB annotation for this pair; consider whether partial I/O similarity justifies clone label.；For future models, incorporate dataflow or API sequence patterns to capture shared functionality in specific sub-tasks.；Use method-level semantic analysis with dependency graphs to separate I/O operations from overall logic.

### case_id=465 FN partial_functionality

- 方法: `getWebPage` vs `addIDs`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Reads a URL and returns the entire page content as a string.
- B 摘要: Reads a URL to a metabolite database, parses HTML for metabolite IDs and chemical identifiers, and sets them on a data row; returns a numerical score.
- 静态失败原因: Low token overlap (Jaccard=0.1) means the model saw little lexical similarity. Static models lack understanding of structural patterns like URL reading loops, which span longer code sequences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB often labels pairs with common algorithmic structure or API usage patterns as clones, even if output differs. Both perform HTTP GET requests and read HTML, which may be considered a Type-3 clone.
- 共享行为: Both open a URL and create a BufferedReader from an InputStreamReader.；Both read lines in a loop until null.；Both handle IOException with an error response.
- 行为差异: A simply concatenates all lines and returns the full content; B parses specific patterns and extracts multiple pieces of information.；B sets fields on a PeakListRow object and returns an integer score; A returns the raw content string.；B uses conditional branching, break statements, and additional URL constructions; A has linear flow.
- 修正建议: Train with more diverse Type-3/Type-4 clone examples to capture shared structure.；Use models that incorporate AST or data flow, like GraphCodeBERT.；Add heuristic features for API call sequences (e.g., URL.openStream -> InputStreamReader -> BufferedReader).

### case_id=466 FN lexical_or_api_overlap

- 方法: `copyResource` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.9`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource to a destination file, supporting both URL and local file sources, using byte streams.
- B 摘要: Copies a file from one path to another using character streams.
- 静态失败原因: Static BERT models like GraphCodeBERT rely heavily on token-level overlap and API usage; low Jaccard similarity (0.22) and different stream class names (InputStream vs FileReader) likely caused the false negative prediction.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BigCloneBench often labels file-copy functionality as clones even when stream types or error handling differ, because the core algorithmic pattern (read from source, write to destination) is the same and represents a Type-3 clone.
- 共享行为: Copy content from a source to a destination file；Use a read-write loop to transfer data；Close streams after copying
- 行为差异: A uses byte streams (InputStream/OutputStream), B uses character streams (Reader/Writer)；A can read from a URL, B only from files；A is a private instance method, B is public static；Different exception handling (A throws Exception, B throws IOException)
- 修正建议: Incorporate data-flow analysis to capture the read-write loop abstraction regardless of stream type；Use a model that can recognize common I/O patterns across different APIs；Augment training with more examples of structurally similar but lexically different clones

### case_id=467 FN benchmark_preference_bias

- 方法: `readData` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Reads multiple configuration strings and populates sets and maps for character classification.
- B 摘要: Fetches version information from a URL and initiates version check.
- 静态失败原因: Static BERT/GraphCodeBERT predicted non-clone (0), which aligns with our analysis. It 'failed' only because the ground truth label (1) is likely incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have broadly considered both as 'reading data and parsing input', but the token similarity is very low (0.098). Likely an annotation error or overly broad Type-4 classification.
- 共享行为: Both perform I/O operations (reading from strings vs. URL)；Both use while loops to parse input；Both are static methods
- 行为差异: Reads from pre-defined comma-separated strings vs. reads from a URL stream；Populates many static data structures vs. parses only two lines and calls another method；Long and complex (many tokenizer loops) vs. short and simple；Different parameters: none vs. View
- 修正建议: Re-evaluate ground truth label for this pair；Consider removing or correcting the BCB annotation

### case_id=468 FP lexical_or_api_overlap

- 方法: `main` vs `doCopyFile`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Main method that reads a Prolog file, parses it, generates adapter JAR, and writes output.
- B 摘要: Copies a file from source to destination, preserving file date if specified.
- 静态失败原因: Static models may over-rely on token overlap and API usage (e.g., File, IOException, try-catch) while missing overall semantics, especially for the long and complex function A.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels as non-clone because the functions serve completely different purposes beyond shared I/O patterns, and the token Jaccard is low (0.08).
- 共享行为: Both perform file I/O operations；Both handle IOException；Both check file existence or properties
- 行为差异: A is a complex code generation pipeline, B is a simple file copy；A uses command-line parsing, B uses explicit parameters；A writes JAR and resources, B copies bytes；A uses many external libraries (FileUtils, Parser, ClassWriter), B uses only java.nio channels
- 修正建议: Use structural analysis (AST, CFG) to differentiate control flow；Incorporate method-level documentation embeddings；Apply contrastive learning to separate different functional patterns；Expand training data with diverse file I/O usage scenarios

### case_id=469 FN partial_functionality

- 方法: `getFile` vs `doFinishLoadAttachment`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies its wsdlsoap:address location, and saves it to the temp directory, returning the file path.
- B 摘要: Handles completion of loading an email attachment; if save flag is set, saves attachment to external storage, otherwise opens it via an intent.
- 静态失败原因: The very low token Jaccard similarity (0.0947) caused the model to classify as non-clone. Static BERT/GraphCodeBERT lacks high-level functional understanding to recognize the shared file-saving pattern across different domains.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as file download/save operations (Type-4 functional similarity) despite different contexts, focusing on the common pattern of reading from an input and writing to a file.
- 共享行为: Both read data from a source (URL stream or content URI) and write it to a file using input/output streams.
- 行为差异: Function A downloads from a network URL and performs XML manipulation on the downloaded file before saving; Function B saves an already-available attachment or opens it.；Function A returns the file path; Function B is void.；Function A has extensive error handling for multiple exception types; Function B only catches IOException.；Function A uses file channels and explicit buffer transfer; Function B uses IOUtils.copy.
- 修正建议: Enhance model with data flow or control flow graphs to capture structural similarities.；Use large-scale pre-training on diverse code to learn abstract functional patterns.；Incorporate functional labels or API usage embeddings to detect common I/O operations.

### case_id=470 FN partial_functionality

- 方法: `createHTML` vs `seeURLConnection`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.95`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Builds an HTML page by loading CSS from classpath and querying a database to add dashboard content.
- B 摘要: Opens an HTTP URL connection and reads the entire response into a string for logging.
- 静态失败原因: The shared pattern is small and embedded in a large function (A), causing low lexical similarity (Jaccard=0.10). Static BERT models are overwhelmed by the surrounding dissimilar code and fail to detect the structural overlap.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers them clones due to the identical code pattern of reading from a URL using BufferedReader within a while loop, accepting this partial functionality overlap as sufficient for a Type-3/4 clone.
- 共享行为: Both read lines from a URL input stream using BufferedReader and InputStreamReader.
- 行为差异: A uses classpath resource URL, B uses HTTP URL.；A builds HTML with multiple sections and database queries, B just logs the response.；A has complex control flow (switch, SQL), B is linear.；A handles IO exceptions, B propagates them.
- 修正建议: Improve model's ability to recognize partial functionality clones via contrastive learning on extracted code slices.；Enhance input representations with data-flow graphs that highlight common I/O patterns.

### case_id=471 FN partial_functionality

- 方法: `getURLContent` vs `register`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches the entire content of a given URL as a string using HTTP GET.
- B 摘要: Registers a user object by persisting it and creating a forum account via HTTP, returning success status.
- 静态失败原因: Static BERT/GraphCodeBERT likely relied on token-level similarity and high-level structure, but the Jaccard similarity is low (0.186). The model may have been confused by the shared boilerplate (URL, BufferedReader, while loop) but correctly identified different overall functionality. However, since BCB says clone, the model failed to recognize that BCB accepts this as a clone. The model may be too strict and not account for the annotation guideline that considers partial functionality clones.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled these as clones due to the common code pattern of opening a connection and reading lines, considering it a Type-3 clone (structurally similar code which may be transformed into a method). The annotation guidelines for BigCloneBench sometimes accept partial functionality where a significant code fragment is duplicated.
- 共享行为: Both open a URL connection, read lines from an InputStream using a BufferedReader in a loop.
- 行为差异: Function A is a simple utility to fetch a URL's content, while Function B performs multiple user registration steps beyond reading the URL.；Function A has no error handling, while Function B has try-catch for IOException and NumberFormatException.；Function B uses the URL reading as a sub-step for forum registration, while Function A's sole purpose is URL reading.；Function A returns the entire content as a string; Function B returns a boolean.
- 修正建议: Improve the model to detect shared sub-functionality even when overall semantics differ.；Incorporate annotation guideline awareness, possibly by training on partial clone examples.；Use additional structural features to identify common code fragments, not just whole-function semantics.

### case_id=472 FN partial_functionality

- 方法: `runInternal` vs `doVersionCheck`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.85`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads and parses an OPDS catalog from a URL, handling pagination, authentication, content types, and progress updates.
- B 摘要: Checks for the latest version of jEdit by reading a version file from a configured URL.
- 静态失败原因: The static BERT/GraphCodeBERT model likely focused on lexical and structural features, but the low token Jaccard (0.108) and different method names (runInternal vs doVersionCheck) caused a false negative. The model failed to recognize the high-level semantic similarity in network I/O pattern due to large differences in code length and complexity.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely considers these as Type-4 (functionally similar) clones because both are network-based data retrieval functions with error handling and user feedback, satisfying a broad notion of 'download and process remote data'.
- 共享行为: Open a URL and read input from the network；Display progress or wait cursor during network operation；Handle IOException and show error messages；Use properties or configuration for URL
- 行为差异: A handles multiple content types (OPDS, ePub, archives) and can download files or parse catalog entries; B only reads version numbers from a plain text file；A includes pagination loop to load multiple pages; B reads a single response；A uses advanced HTTP features (redirects, cookies, timeouts); B uses basic URL.openStream()；A has a fallback for partial loading and callback mechanism; B invokes another method (doVersionCheck) after parsing
- 修正建议: Use graph-based representations (e.g., AST or CFG) to capture control-flow patterns like open stream, read, close, error handling；Incorporate data flow analysis to track input/output relationships (URL to InputStream)；Train on functional similarity rather than strict lexical overlap, e.g., by clustering functions by API usage patterns

### case_id=473 FN lexical_or_api_overlap

- 方法: `copyResource` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.8`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Copies a resource (URL or file) to a destination file by reading bytes one by one and writing them.
- B 摘要: Reads a text file line by line, applies WrapFilter and TitleCaseFilter transformations, and writes the result to another file.
- 静态失败原因: The models likely focused on method names ('copyResource' vs 'main'), different APIs (URL, FileInputStream vs FileReader, WrapFilter), and low token overlap, missing the broader I/O loop pattern.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: Both methods follow the same high-level pattern of reading from an input source and writing to an output source using a read-write loop, which is considered a Type-3 clone with slight modifications in API and processing.
- 共享行为: Both read from an input source and write to an output file.；Both use a loop to read and write until the input is exhausted.；Both close the input and output streams after processing.
- 行为差异: A reads binary data (bytes), B reads text data (lines).；A performs a raw copy without transformation; B applies filtering (wrap and title case).；A's input can be a URL or a file; B's input is always a file specified as command-line argument.
- 修正建议: Train with more examples of I/O loops using different APIs to generalize the pattern.；Incorporate dataflow analysis to detect that input is consumed and output is produced in both.；Use structure-based features that capture the open-read-write-close sequence.

### case_id=474 FN partial_functionality

- 方法: `getFile` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies the endpoint location in the XML, and saves it to a temporary file.
- B 摘要: Concatenates multiple input files into one output file by reading lines and writing them to a PrintWriter.
- 静态失败原因: The model likely relied on token overlap and syntactic similarity, which are low (Jaccard=0.1145), and failed to capture the abstract similarity in file I/O operations that BCB may have considered.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider them clones because both functions involve downloading/reading from an input source and writing to a file, with similar exception handling patterns, despite different high-level purposes.
- 共享行为: Both perform file I/O operations.；Both handle exceptions (IOException, etc.).；Both create and write to output files.
- 行为差异: Input source: URL stream vs local files.；Processing: XML manipulation vs simple line copying.；Output structure: single WSDL file vs concatenated text file.
- 修正建议: Incorporate data flow analysis to detect common I/O patterns.；Use graph-based models to capture structural similarities in exception handling and resource management.；Enhance training data with diverse I/O operations to recognize partial functionality similarity.

### case_id=475 FN partial_functionality

- 方法: `main` vs `fetchURLData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a KMZ file from a hardcoded URL and extracts its zip entries to local files.
- B 摘要: Fetches a URL (with optional proxy) and returns its content as a byte array.
- 静态失败原因: Static BERT may have failed due to low lexical overlap and different control flow structures; the models may rely on surface-level similarity or structural patterns, and these two functions share only a few common tokens and have different structures.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered both as data retrieval from URLs, overlooking the zip extraction step in A as a subsequent processing detail.
- 共享行为: Both open a URL and handle file:// and http:// protocols.；Both use input streams to read data from the URL.
- 行为差异: A extracts zip entries and writes them to files; B returns raw bytes as a byte array.；A is a main method with hardcoded URL; B is a utility method with parameters.；A uses ZipInputStream and FileOutputStream; B uses ByteArrayOutputStream and IOUtils.copy.
- 修正建议: Improve recognition of functional differences beyond shared boilerplate.；Use data-flow analysis to distinguish between reading raw bytes vs. extracting archives.；Incorporate more training examples where similar boilerplate leads to different final outputs.

### case_id=476 FN partial_functionality

- 方法: `getResourceAsStream` vs `main`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Retrieves a resource via URL, caches it locally, and returns the local file input stream.
- B 摘要: Copies a portion of a file to another file starting from a given offset.
- 静态失败原因: Static BERT models may overemphasize structural patterns (try-catch, loop, IO streams) and miss high-level semantic differences in goal and context.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have labeled as clone due to similar byte-copying loop and IO exception handling, focusing on partial functional similarity despite different overall purposes.
- 共享行为: Both use BufferedInputStream and BufferedOutputStream to copy bytes
- 行为差异: A handles HTTP connections, caching, and error recovery; B simply copies a file with an offset and no caching；A returns an InputStream; B writes to output file and has no return value
- 修正建议: Incorporate function names and comments into the representation；Use models that capture long-range dependencies and overall intent

### case_id=477 FN long_range_semantics

- 方法: `doGet` vs `copy`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.6`
- 推荐路线: `hybrid_review`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Handles HTTP GET request by retrieving a page, checking permissions, rendering, and optionally caching to a file.
- B 摘要: Copies a file from one location to another using NIO channels.
- 静态失败原因: Low lexical overlap (Jaccard 0.07) and different syntactic structures cause static models to miss the functional similarity in I/O handling; they rely on surface forms and control flow patterns which are very different.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider both as I/O operations that read from a source and write to a destination, with error handling and resource cleanup, thus broad Type-4.
- 共享行为: Both perform I/O operations (reading/writing data) with error handling and resource management.
- 行为差异: Method A handles HTTP requests and involves complex business logic (user permissions, logging, caching); Method B is a simple file copy utility.；Method A works with servlet objects; Method B works with files.
- 修正建议: Use dataflow analysis to capture I/O operations；Enhance model with functional role classification (e.g., I/O, file handling)

### case_id=478 FN partial_functionality

- 方法: `testNetworkHTTP` vs `lookupFutureEvents`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Tests network connectivity by making multiple HTTP GET requests and discarding the responses.
- B 摘要: Fetches future events from a Meetup API, parses the JSON response, and constructs a list of Event objects.
- 静态失败原因: The token overlap is low (Jaccard 0.1367), and the methods have very different overall structure and vocabulary. BERT-based models rely heavily on token similarity and structural code representations, which highlight the many differences in variable names, method names, and logic (e.g., JSON parsing vs. no parsing). The shared HTTP pattern is a small portion of each method, and the model likely considered the overall semantics too different.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled it as a clone because both functions share the common pattern of making an HTTP GET request and reading the response line by line. The boilerplate code (URL creation, BufferedReader, readLine loop) is considered a functionally similar sub-task, which matches BCB's acceptance of partial functionality similarity (Type-4).
- 共享行为: Both open an HTTP connection to a URL and read lines from the response stream.；Both handle IOException by printing stack trace or throwing an exception.
- 行为差异: Function A does not parse or process the response content; Function B parses JSON and creates structured Event objects.；Function A makes multiple requests to different URLs; Function B makes a single request.；Function A is void and does not return anything; Function B returns a List<Event>.；Function A is a test method without parameters; Function B takes a groupIdentifier parameter and has a clear API key.
- 修正建议: Augment training data with pairs that share only boilerplate patterns to teach models to recognize thin clones.；Incorporate data flow analysis to detect common API usage patterns even when other code differs.；Use hierarchical or attention-based models that can focus on local patterns while being robust to overall differences.

### case_id=479 FP boilerplate_overlap

- 方法: `get` vs `PageLoader`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Fetches game records from a URL using HTTP GET with custom headers and returns an array of decoded GameRecords.
- B 摘要: Loads the entire content of a web page into a string field via a constructor.
- 静态失败原因: The model over-emphasized shared API calls (URL, BufferedReader) and overall structure of reading from a URL, ignoring critical differences in control flow (response check, line filtering) and return types.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled as non-clone because the functions have distinct purposes and output types, with low token overlap and no functional equivalence beyond basic HTTP reading.
- 共享行为: Both open a URL stream and read text line by line using BufferedReader.
- 行为差异: A checks HTTP response code and returns null on failure; B throws an exception.；A filters lines starting with '#' and decodes them into GameRecord objects; B concatenates all lines into one string without filtering.；A returns an array of GameRecord; B stores the result in an instance field.
- 修正建议: Enhance model with dataflow analysis to capture conditional branches and return types.；Introduce attention to method signatures and output types to differentiate utility functions from constructors.；Use contrastive learning to reduce sensitivity to common boilerplate patterns.

### case_id=480 FP lexical_or_api_overlap

- 方法: `main` vs `doGet`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.3`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Generates adapter classes from a Prolog file, writing them to a JAR archive.
- B 摘要: Serves a static file from the file system in response to an HTTP GET request.
- 静态失败原因: The model may have been misled by the presence of similar library calls (File, FileInputStream, IOException) and the general pattern of reading from a file, but it failed to capture the different overall purposes and data flows.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators would likely consider these as non-clones because they implement completely different functionalities despite both involving file I/O. The shared behaviors are generic and not indicative of semantic clones as a whole.
- 共享行为: Both perform file I/O operations；Both handle IOException
- 行为差异: Purpose: A is a code generation tool, B is a web file server；A uses a complex pipeline of parsing, visiting, and generating classes; B simply reads and copies a file to the response output stream；A writes multiple outputs to a JAR; B writes to HTTP response；A includes debug and error printing; B does not
- 修正建议: Improve model's ability to distinguish between similar low-level operations in very different high-level contexts；Incorporate control flow and data flow analysis to understand the overall program goal；Increase emphasis on method-level semantics beyond token overlap

### case_id=481 FP lexical_or_api_overlap

- 方法: `readZoneIDs` vs `sendRequest`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a file containing integer zone IDs and returns them as a set.
- B 摘要: Sends an XML request to a servlet using HTTP with GZIP compression and returns an empty string.
- 静态失败原因: Overlapping API usage (URL, try-catch, printStackTrace) and both are I/O related; static method focused on lexical tokens ignoring high-level semantics.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically requires functional similarity; these functions are too different, so BCB would label as non-clone.
- 共享行为: Both use URL objects to open connections/streams；Both use try-catch for exception handling；Both print stack traces on exceptions
- 行为差异: Main purpose (reading local file vs. sending HTTP request)；Return types and values (HashSet<Integer> vs. String)；Use of GZIP compression and JDOM parsing in B；Use of preferences and dialog in B
- 修正建议: Incorporate dataflow or control flow analysis；Use contrastive learning with negative samples having similar tokens but different semantics；Improve understanding of overall intent

### case_id=482 FP lexical_or_api_overlap

- 方法: `doVersionCheck` vs `get`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Checks for version strings (develBuild, stableBuild) from a remote URL and performs version check with view.
- B 摘要: Fetches game records from a URL with custom HTTP headers, filtering lines, and returns an array of GameRecord.
- 静态失败原因: Static BERT models may over-rely on token-level overlap like 'URL', 'BufferedReader', 'IOException', and 'readLine', missing the semantic differences in the loop processing and overall intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labeled non-clone because the functions have entirely different purposes and data processing logic, despite superficial structural similarities.
- 共享行为: Both open URL connections and read lines via BufferedReader；Both handle IOException；Both iterate over lines with while loop
- 行为差异: Different HTTP request setup (GET vs. default GET, custom headers in B)；Different line processing (startsWith checks for version vs. skipping '#' and decoding GameRecord)；Different error handling (GUI error vs. printStackTrace)；Different return type (void vs. GameRecord[])
- 修正建议: Incorporate control-flow and data-flow analysis to distinguish different processing within loops；Improve representation of HTTP method and headers；Use fine-grained difference in error handling (GUI vs. printStackTrace)

### case_id=483 FN partial_functionality

- 方法: `runScript` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.8`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Reads a script from a URL and returns its content as a string.
- B 摘要: Reads a configuration file and parses comma-separated tokens into multiple sets and maps.
- 静态失败原因: Low token Jaccard (0.075) and different identifiers/control flow cause static embeddings to miss the abstract similarity of data ingestion.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label these as clones due to both being data-reading utilities with external input, a typical Type-4 semantic clone category.
- 共享行为: Both read external data (URL stream vs file).；Both process data character/token-wise.；Both handle exceptions (catch block).
- 行为差异: A returns data as a string; B populates global data structures.；A reads from a URL; B reads from a local file.；A reads until end of stream; B reads line by line and tokenizes.；A is simple character concatenation; B has complex parsing with multiple delimiters and error handling.
- 修正建议: Use models capturing data flow or program dependency graphs.；Increase context length or use contrastive learning for high-level semantic alignment.

### case_id=484 FN partial_functionality

- 方法: `getFile` vs `run`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a WSDL file from a URL, modifies XML address endpoint, and saves to a temporary file.
- B 摘要: Copies files from an HDFS directory to a local output stream.
- 静态失败原因: Low lexical overlap (Jaccard=0.128) and different APIs (URL vs FileSystem) mislead static models to focus on surface differences rather than underlying I/O behavior.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as 'data transfer' tasks involving downloading/copying files, which falls under partial functionality similarity (Type-3/4).
- 共享行为: Both involve file I/O and stream copying.；Both handle exceptions and log errors.；Both write data to local filesystem.
- 行为差异: Data source differs: HTTP URL vs HDFS directory.；Function A performs XML manipulation; Function B does not.；Function A checks file existence and re-downloads if needed; Function B assumes directory exists.；Function A returns file path; Function B returns exit code.
- 修正建议: Enhance models with functional role annotations (e.g., file download vs directory copy).；Incorporate data flow analysis to capture abstract I/O operations.；Use code summarization to identify high-level intent.

### case_id=485 FP boilerplate_overlap

- 方法: `executePost` vs `getNetworkServersIPs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Executes an HTTP POST request with given URL and parameters, returning the response body as a string.
- B 摘要: Fetches a server list from a URL, parsing lines to extract IP addresses after the '!SERVERS' marker.
- 静态失败原因: Static BERT models often rely on token overlap and structural similarity. Both functions contain common tokens like 'URL', 'BufferedReader', 'InputStreamReader', 'while ((line = reader.readLine())', 'e.printStackTrace()', and URL connection setup. This overlap, combined with similar control flow (try-catch-finally), caused the model to overestimate functional similarity.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB tends to label non-clones when functions perform distinct high-level tasks, despite sharing low-level I/O boilerplate. The domain-specific parsing in getNetworkServersIPs diverges significantly from the generic HTTP POST.
- 共享行为: Both open a URL connection and read from an InputStreamReader wrapped in BufferedReader.；Both iterate over lines of input and build a result (string or vector).；Both handle exceptions with printStackTrace and return a default value or empty result.
- 行为差异: executePost sends a POST request with output stream; getNetworkServersIPs only reads (GET).；executePost writes URL parameters; getNetworkServersIPs does not write anything.；executePost returns the entire response string; getNetworkServersIPs parses specific lines for IP addresses.；getNetworkServersIPs has special logic for '!SERVERS' and semicolons to toggle parsing mode.
- 修正建议: Improve representation of functional semantics, e.g., by incorporating data flow or API call sequences.；Add attention to domain-specific literals and markers (like '!SERVERS') that indicate distinct purposes.；Use contrastive learning to separate concurrent I/O boilerplate from core logic.

### case_id=486 FN partial_functionality

- 方法: `testNetworkHTTP` vs `scrapeForIsbns`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: This function tests network connectivity by making multiple HTTP GET requests to several hardcoded URLs and discarding the response content, logging errors.
- B 摘要: This function scrapes ISBN-10 codes from a given URL by reading lines, matching a regex pattern, storing matches, and retrying on connection failures, returning the count.
- 静态失败原因: The static model likely relied on token-level or structure-level similarity and observed low token Jaccard (0.15), different method names, signatures, and bodies (many hardcoded URLs vs. regex and retries). It failed to capture the abstract pattern of 'network read loop' as a feature, focusing instead on exact lexical matches and control flow differences.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB likely labeled this as a clone because both functions share the core pattern of opening a network stream and reading lines in a loop, which is considered a semantically similar operation despite different contexts (test vs. scraping). The partial functionality overlap outweighs the differences under BCB's broad Type-3/Type-4 criteria.
- 共享行为: Open an HTTP connection and create a BufferedReader from the input stream；Read lines in a while loop until null；Handle IOException
- 行为差异: A makes multiple connections to fixed URLs; B takes a single URL parameter；A discards all read data; B extracts and stores ISBNs using regex；A is void; B returns an int count；A uses HttpURLConnection explicitly; B uses URL.openStream()
- 修正建议: Incorporate graph-based or dataflow representations to abstract away specific URLs and regex patterns；Train models on more clone pairs with partial functional similarity to learn high-level API usage patterns；Use contrastive learning to emphasize shared behavior (e.g., open stream, read lines) over superficial differences

### case_id=487 FN benchmark_preference_bias

- 方法: `testSimpleQuery` vs `modifyApplicationMessage`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: A test method that writes XML data to a JCR repository, executes a query, and asserts the result matches expected content.
- B 摘要: A utility method that modifies a properties file for a given locale by updating or adding a message key-value pair.
- 静态失败原因: The static model correctly identified the functions as having different purposes and low token overlap, so it predicted non-clone, but the benchmark labels it as clone. The model failed to match the BCB annotator's possibly overly broad similarity criterion.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have considered both as 'modifying and reading back data' at a very high level, or there might be a mislabeling in the benchmark.
- 共享行为: Both perform file/stream I/O operations to write and read data.
- 行为差异: A is a test method with assertions; B is a production utility with error handling.；A uses JCR API and XML; B uses standard Java file I/O and Properties.；A expects data to be present; B creates files if missing.；A reads data via a query; B reads via file reading and string parsing.
- 修正建议: Improve benchmark annotation consistency for broad Type-4 clones.；Use domain-specific features to differentiate test code from production utility code.

### case_id=488 FN benchmark_preference_bias

- 方法: `writeFileToFile` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.75`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Copies content from a source file to a destination file using FileChannel transfer.
- B 摘要: Retrieves a resource from a URL, caches it locally, and returns an InputStream to the cached file.
- 静态失败原因: GraphCodeBERT likely focused on token overlap and structural patterns; low Jaccard (0.125) suggests limited lexical similarity, and the large behavioral difference may have led to correct prediction of non-clone, but BCB labeled as clone due to broader criteria.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider both functions as involving file reading/writing and stream operations, possibly viewing them as Type-4 (functionally similar but not equivalent) despite differing high-level purposes.
- 共享行为: Both involve reading from an input source and writing to a file output stream.
- 行为差异: Function A is a straightforward file-to-file copy; Function B is a caching resource loader with HTTP handling and local cache management.；Function A uses FileChannel for efficient transfer; Function B uses BufferedStreams and manual byte-by-byte copying.；Function A only copies file content; Function B may retrieve from network and cache, and returns an InputStream instead of writing to a fixed output.；Function B includes conditional caching logic and URL handling absent in Function A.
- 修正建议: Ensure BCB annotations are consistent with strict functional equivalence for Type-1/2/3, and avoid labeling semantically distinct functions as clones.；Add explicit filtering of false positives in training data by requiring similar I/O signatures and return types.

### case_id=489 FN benchmark_preference_bias

- 方法: `doRequest` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Handles HTTP request by validating path alias, resolving internal resource, setting MIME type, and copying input stream to output stream.
- B 摘要: Configures and launches an Eclipse launch configuration for a NexOpen project, handling Maven pom files, Hibernate dialect setup, reverse engineering file creation, and scheduling install action.
- 静态失败原因: The static BERT model correctly predicted non-clone (0). The failure is not in the model but in the BCB annotation, which appears incorrect.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have labeled this as a clone due to very general similarities like using IOUtils and handling I/O, or due to benchmark annotation errors. Typically, BCB requires more substantial functional overlap.
- 共享行为: Both involve handling resources and streams, but at different abstraction levels.
- 行为差异: Function A is a servlet request handler; function B is an Eclipse launch configuration handler.；Function A returns a boolean; function B returns void.；Function A has no project or Maven-related logic; function B heavily relies on project structure and XML manipulation.；Function A uses IOUtils.copyAndClose; function B uses IOUtils.copy but in a different context.
- 修正建议: Re-evaluate BCB annotation for this pair; likely a false positive in the benchmark.；Consider removing or correcting this pair to improve benchmark accuracy.

### case_id=490 FN boilerplate_overlap

- 方法: `getHTML` vs `writeFileType`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `api_abstraction_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Fetches HTML content from a given URL and optionally writes it to a file, returning the content as a string.
- B 摘要: Reads a list of URIs from a file, fetches each URI's content, detects RDF/OWL keywords within the first 100 lines, and writes the URI and its type to an output file.
- 静态失败原因: Static BERT models rely on token embeddings and may overemphasize common API calls (e.g., URL, BufferedReader, BufferedWriter) and similar control flow structures, missing the divergent intent and overall functionality.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB may consider them as Type-3 clones because both involve similar low-level operations (URL connection, reading lines, writing to file) despite different high-level purposes. The structural similarity in boilerplate code and exception handling could justify a positive annotation.
- 共享行为: Both connect to HTTP URLs using URLConnection.；Both use BufferedWriter to write output to files.；Both handle exceptions with printStackTrace.
- 行为差异: A fetches a single URL; B processes multiple URIs from an input file.；A returns the fetched content; B writes classification results (URI + type) to a file and does not return any value.；B includes keyword detection for OWL, RDFS, and RDF; A does not have any content analysis.
- 修正建议: Incorporate dataflow analysis to distinguish different input-output roles.；Use task-agnostic semantic embeddings that capture program purpose beyond token similarity.

### case_id=491 FN benchmark_preference_bias

- 方法: `login` vs `readData`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.2`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `low`
- A 摘要: Performs HTTP POST login with email and password, reads response, extracts session ID, and returns it.
- B 摘要: Reads a configuration file or data, parses tokens, and populates multiple sets and mappings for Tibetan/Sanskrit character processing.
- 静态失败原因: The static BERT model likely relied on token overlap (Jaccard 0.07) and structural similarity, which are minimal, causing it to predict non-clone. However, BCB may accept partial functionality overlap that the model missed, such as the common pattern of reading input and building data structures.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may have annotated this as a clone due to both being non-trivial methods that handle I/O and parse input, possibly under a broad Type-4 semantic category of 'input processing' or 'initialization', though the specific behaviors are very different.
- 共享行为: Both use try-catch blocks for exception handling；Both print messages to System.out；Both involve reading from an input source (HTTP response vs file/string)
- 行为差异: Login performs network I/O, while readData performs file/string parsing；Login returns a String (session ID), readData is void；Login has minimal processing (one line read), readData has extensive parsing with many tokens and data structures；Login is instance method, readData is static
- 修正建议: Incorporate higher-level semantic embeddings or program flow representations；Use data-flow features to capture I/O patterns；Train with more diverse and balanced clone pairs that include broad Type-4 similarities

### case_id=492 FP lexical_or_api_overlap

- 方法: `doRawRequest` vs `checkForUpgrade`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request to a fixed URL with provided data and returns the response body as a string.
- B 摘要: Checks for software upgrades by querying a remote server via HTTP GET, parsing an XML-like response, updating a local database, and toggling UI components.
- 静态失败原因: The model likely overfitted to the lexical overlap of HTTP API tokens (URL, URLConnection, BufferedReader, readLine) and similar looping structure, ignoring the divergent surrounding logic and function purpose.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB likely labels non-clones because the overall semantic functionality is completely different despite shared HTTP boilerplate. The common pattern (open connection, read lines) is too generic to indicate clone status.
- 共享行为: Both use URLConnection to make HTTP requests and read the response line by line into a string buffer.
- 行为差异: Function A is a generic POST utility; Function B is a specific upgrade checker using GET.；Function B includes database queries, UI manipulation, and complex XML-like parsing; A does not.；Function B has conditional logic based on response content; A simply returns the response.；Function B writes to a database table; A does no such persistence.
- 修正建议: Incorporate method-level context (e.g., class, method name, parameters) to differentiate purpose.；Use data-flow analysis to capture that one writes to DB and manipulates UI, while the other does not.；Train on more diverse examples where HTTP boilerplate is not indicative of clone status.

### case_id=493 FP lexical_or_api_overlap

- 方法: `readReferenceText` vs `getTicketsForQueue`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Reads a reference text from a file within a plugin bundle, given an identifier, and returns the content as a string.
- B 摘要: Retrieves a list of tickets for a given queue from a Request Tracker REST API, parsing the response to extract ticket IDs and fetching each ticket.
- 静态失败原因: The static model likely focused on the overlap of BufferedReader/InputStreamReader patterns and similar control flow (readLine loop), ignoring the vast difference in purpose and the surrounding code (e.g., HTTP request, URL construction, list accumulation).
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB annotators would likely consider these non-clones because they perform entirely different tasks (file reading vs. API interaction) and share only generic I/O boilerplate, not meaningful functionality.
- 共享行为: Both use InputStreamReader and BufferedReader to read input line by line.；Both perform string manipulation (e.g., appending lines, parsing prefixes).；Both handle exceptions and log errors.
- 行为差异: Function A reads from a local file (URL), while Function B makes an HTTP GET request to a remote server.；Function A returns a single string, while Function B returns a list of RTTicket objects.；Function B includes query construction, HTTP response handling, and multiple API calls, which are absent in Function A.；The content and structure of what is read are completely different (plain text vs. ticket IDs).
- 修正建议: Incorporate task-level semantics, e.g., by distinguishing local file I/O from network I/O.；Use structural or graph-based representations that capture the overall computation graph rather than just token sequences.；Increase weighting of unique method names and external API calls to differentiate purposes.

### case_id=494 FN partial_functionality

- 方法: `tail` vs `buildSiteForEdit`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Implements the tail command to display the last 1024 bytes of a file, with optional follow mode.
- B 摘要: Builds an edit site by transforming XML pages via XSLT and writing output files.
- 静态失败原因: Static BERT models may have focused on similar I/O-related tokens (e.g., 'FileSystem', 'read', 'write') and overlooked the high-level semantic divergence due to the length and complexity of the code.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may have considered both as examples of 'file reading and copying' but the functions serve entirely different purposes; this likely is a false positive annotation.
- 共享行为: Both perform file I/O operations；Both use loops to process data over time/pages；Both involve reading from a file and writing to an output stream
- 行为差异: Function A reads a single file and outputs to stdout; function B reads multiple XML files and writes HTML files；Function A has a sleep-based follow loop; function B loops over pages without sleeps；Function A uses Hadoop FileSystem; function B uses a custom FileSystem class；Function B performs XSLT transformations and string replacements; function A does not
- 修正建议: Incorporate method name and comment information as semantic hints；Use AST-based structural similarity that captures control flow and data dependencies better；Include information retrieval features like code summaries or documentation

### case_id=495 FN partial_functionality

- 方法: `copy` vs `getResourceAsStream`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `yes`；confidence: `0.7`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Recursively copies a file or directory, skipping .svn directories, to a destination directory.
- B 摘要: Retrieves a resource as an InputStream by downloading from a URL with caching, returning a FileInputStream from cache if available.
- 静态失败原因: Static models like GraphCodeBERT rely on syntactic and structural patterns. The low token Jaccard and different method names caused the model to see them as distinct. The model likely missed the common I/O pattern due to different context (recursive copy vs. HTTP download) and ignored the shared low-level buffer copying logic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider both as file copying operations, where one copies local files and the other copies remote resources to a local cache, thus sharing core I/O functionality.
- 共享行为: Both perform file I/O operations using buffers；Both check existence and last modified times before copying；Both use while loops to transfer data in chunks
- 行为差异: Method A copies local files/directories; Method B downloads from remote URLs；Method A is recursive for directories; Method B handles only single files；Method B has caching logic and HTTP handling; Method A does not；Method B returns an InputStream; Method A returns void
- 修正建议: Train the model to recognize abstract functionality patterns like file copying, even when source/destination types differ.；Incorporate data flow analysis to identify that both methods read from a source and write to a destination using a buffer.

### case_id=496 FN partial_functionality

- 方法: `fileDownload` vs `getEncoding`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.9`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `medium`
- A 摘要: Downloads a file from a given URL to a local destination directory as 'download.pdf'.
- B 摘要: Extracts the character encoding from an HTTP URL's response headers or content.
- 静态失败原因: Static BERT models rely on token similarity (Jaccard 0.149) and may miss the overarching pattern of URL connection handling; they also lack understanding of the high-level purpose and treat the methods as distinct due to different method names, return types, and specific processing logic.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may consider these as Type-4 clones because both methods perform network I/O and read from a URL connection, sharing a broad functional pattern of downloading or processing web content.
- 共享行为: Both open a URLConnection and read from the input stream using a loop.；Both involve I/O operations over a network resource.
- 行为差异: Method A writes the input stream to a local file; method B parses the input for charset information.；Method A has parameters for URL and destination; method B uses an instance field `url` and no parameters.；Method A returns void; method B returns a String (encoding).；Method A catches all exceptions; method B throws IOException.
- 修正建议: Incorporate graph-based or dataflow representations to capture shared I/O patterns.；Use attention mechanisms that focus on common operations (e.g., URLConnection, BufferedReader) even when variable names differ.；Train with more diverse examples of broad functional similarity.

### case_id=497 FN partial_functionality

- 方法: `copyFile` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `uncertain`；confidence: `0.6`
- 推荐路线: `subfunction_dynamic_plus_preference`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Copies a file from source to destination using FileChannel.transferFrom, with proper resource cleanup.
- B 摘要: Launches a NexOpen project configuration by validating project files, processing XML, setting properties, copying a reverse engineering file if needed, and running an install action.
- 静态失败原因: Static BERT/GraphCodeBERT models likely failed due to very low token Jaccard (0.0566) and significant structural differences. The models rely on token overlap and local context, so they miss the shared file copy behavior embedded in a much larger, differently-structured method.
- 静态 case study: 该类错误需要子功能定位和 BCB 偏好建模，单一整函数静态 embedding 不稳定。
- 动态 case study: 动态执行只能部分解决：整函数 I/O 等价过于严格，需要先由 LLM/静态分析定位共享子功能，再做局部行为测试，并结合 BCB 偏好判断。
- BCB 偏好解释: BCB may label this as a clone because both functions involve copying files from one location to another, even though launch's file copy is a minor sub-step. BCB's annotation guidelines often accept Type-4 (similar functionality) clones where the main behavior overlaps partially.
- 共享行为: Both methods perform file copying operations: copyFile copies an entire file via FileChannel; launch copies a resource file into the project when needed.
- 行为差异: copyFile is a standalone utility for file copy; launch is a complex project launcher with multiple steps beyond copying.；copyFile uses java.nio.channels.FileChannel; launch uses IOUtils.copy and ByteArrayOutputStream for file copy.；launch includes error handling, logging, and project-specific setup; copyFile has simple error handling.
- 修正建议: Enhance models to recognize sub-functionality across methods, e.g., via code summarization or data-flow analysis to detect common I/O patterns.；Use graph-based representations that capture high-level operations like file copy, even if implemented with different APIs.

### case_id=498 FN benchmark_preference_bias

- 方法: `doImageProcess` vs `launch`
- 标签/预测: BCB `1`，GraphCodeBERT `0`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.7`
- 推荐路线: `preference_memory`；动态可解性: `not_applicable`；执行优先级: `medium`
- A 摘要: Processes an image request by setting content type, optionally resizing the image, and writing the image data to the HTTP response output stream.
- B 摘要: Launches a NexOpen project by validating configuration, processing Maven POM files, setting up Hibernate dialect properties, and scheduling an install project action.
- 静态失败原因: Static BERT methods like GraphCodeBERT rely on lexical and structural similarity. The low token Jaccard (0.0736) and different method signatures indicate minimal overlap, leading to a non-clone prediction. The model likely failed to capture the subtle commonalities in I/O patterns that the BCB annotators considered.
- 静态 case study: 该类错误主要是 benchmark 偏好问题，不能只靠严格静态语义解决。
- 动态 case study: 动态执行不适合作为主证据：该样本更接近 BCB 标注偏好或严格语义冲突，整函数动态测试大概率会支持严格非克隆，未必提高 BCB 分数。
- BCB 偏好解释: BCB may consider these clones due to shared low-level I/O patterns and exception handling, despite different high-level purposes. The annotation might reflect a broad Type-4 perspective where functions that perform I/O with similar API usage are considered functionally similar.
- 共享行为: Both handle I/O operations (reading from input streams and writing to output streams)；Both use IOUtils.copy to transfer data between streams；Both handle exceptions and resource cleanup
- 行为差异: Function A serves an image to an HTTP response; Function B configures and launches an Eclipse project；Function A deals with image formats and sizes; Function B deals with Maven, Hibernate, and Eclipse resources；Function A is a request handler; Function B is a launch configuration handler
- 修正建议: Incorporate dataflow analysis to highlight common I/O operations；Train on BCB-style annotations to learn broader clone definitions；Use control-flow graph features to abstract away domain-specific details

### case_id=499 FP lexical_or_api_overlap

- 方法: `executePost` vs `loadExistingAntlibs`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `dynamic_rejection_oracle`；动态可解性: `high`；执行优先级: `high`
- A 摘要: Sends an HTTP POST request with URL-encoded parameters and returns the response string.
- B 摘要: Loads antlib resources from the classpath using a class loader and processes their URIs.
- 静态失败原因: Static BERT likely overemphasized lexical and API overlap (e.g., URL, BufferedReader, IOException) and similar control flow patterns, ignoring the distinct semantic intent.
- 静态 case study: 该类错误不是静态方法的天然不可解问题。更强的静态表示、hard negative 训练、boilerplate 降权、API 语义和数据流目的地建模应能明显改善。
- 动态 case study: 动态执行价值高：该样本主要用于排除静态模型由 API/模板/数据流表面相似导致的误报。建议测试目标为 whole_function_behavior_and_side_effects。
- BCB 偏好解释: BCB typically labels non-clones when methods have different names, different parameters, and clearly distinct purposes, despite shared I/O boilerplate.
- 共享行为: Both handle I/O operations using URL, InputStream, and BufferedReader；Both use try-catch blocks for exception handling；Both read lines from a stream
- 行为差异: Different primary functionality: one is an HTTP client, the other is a resource loader；Different method signatures (parameters and return type)；Different control flow: executePost has a fixed flow, loadExistingAntlibs iterates over resources and handles URI resolution
- 修正建议: Integrate method name and parameter type as additional features；Use data flow analysis to distinguish I/O consumption vs. network request；Incorporate structural differencing on method return types and call patterns

### case_id=500 FP long_range_semantics

- 方法: `readData` vs `getFileContentAsString`
- 标签/预测: BCB `0`，GraphCodeBERT `1`
- strict_clone: `no`；bcb_style_clone: `no`；confidence: `0.95`
- 推荐路线: `static_summary_plus_selective_dynamic`；动态可解性: `medium`；执行优先级: `low`
- A 摘要: Initializes multiple HashSet fields and a validInputSequences map by parsing comma-separated strings via StringTokenizer.
- B 摘要: Reads the content of a file specified by a path into a String using the provided encoding.
- 静态失败原因: Static models like GraphCodeBERT may over-rely on superficial patterns (both methods have try-catch for IOException, use InputStream or similar) and fail to capture the overall intent due to the extreme length disparity; code A is too long for the model to correctly encode its global semantics.
- 静态 case study: 该类错误静态方法可部分解决，但通常需要和动态证据或 LLM 摘要结合。
- 动态 case study: 动态执行可作为辅助证据：可先尝试构造 harness 和输入输出 oracle，若执行条件不足则回退到 LLM 专家判断和偏好建模。
- BCB 偏好解释: BCB annotation prefers non-clone because the functions have completely different semantics and outputs, even if both involve reading data. Strict functional equivalence is absent, and partial similarity is unlikely to be considered a clone in BCB's framework.
- 共享行为: Both involve reading input data (internal tokens vs file content).；Both handle potential IO exceptions (code A has a catch for IOException, code B throws it).
- 行为差异: Code A populates global data structures; code B returns a string.；Code A processes predefined string variables; code B reads from a file resource.；Code A uses StringTokenizer for parsing; code B uses IOUtils.copy.；Code A is very long with many initialization steps; code B is a short utility method.
- 修正建议: Use hierarchical or sliding window approaches to handle very long methods.；Incorporate dataflow or control-flow analysis to distinguish disparate functionalities.；Train on more diverse negative examples with high lexical overlap but different semantics.
